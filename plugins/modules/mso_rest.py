#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Daniel Schmidt <danischm@cisco.com>

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = r"""
---
module: mso_rest
short_description: Direct access to the Cisco MSO REST API
description:
- |
  Enables the management of the Cisco MSO through direct access to the Cisco MSO REST API.
  MSO assigns unique IDs to each object which then need to be referenced if the object is
  to be modified or deleted. In order to modify/delete objects without knowing its ID in
  advance, wherever an ID needs to be inserted it can be replaced with a placeholder
  (format: '%%API_ENDPOINT%OBJECT_KEY%%'). This placeholder will then be resolved during
  runtime. API_ENDPOINT is the respective API endpoint of that object, and OBJECT_KEY is
  an attribute that is used as a unique key (eg. its name). The supported API endpoints
  and the objects key attribute are defined in module_utils/mso.py .
author:
- Daniel Schmidt
version_added: '2.8'
options:
  method:
    description:
    - The HTTP method of the request.
    - Using C(delete) is typically used for deleting objects.
    - Using C(get) is typically used for querying objects.
    - Using C(post) is typically used for creating objects.
    - Using C(put) is typically used for modifying objects.
    - Using C(patch) is typically used for updating an existing object.
    - Using C(post_or_put) is typically used for creating or modifying objects.
    type: str
    choices: [ delete, get, post, put, patch, post_or_put ]
    default: get
    aliases: [ action ]
  path:
    description:
    - URI being used to execute API calls.
    type: str
    required: yes
    aliases: [ uri ]
  content:
    description:
    - When used instead of C(src), sets the payload of the API request directly.
    - This may be convenient to template simple requests.
    - For anything complex use the C(template) lookup plugin or the M(template)
      module with parameter C(src).
    type: raw
  src:
    description:
    - Name of the absolute path of the filename that includes the body
      of the HTTP request being sent to the MSO.
    - If you require a templated payload, use the C(content) parameter
      together with the C(template) lookup plugin, or use M(template).
    type: path
    aliases: [ config_file ]
extends_documentation_fragment: mso
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""

import json
import os
import re

# Optional, only used for YAML validation
try:
    import yaml

    HAS_YAML = True
except Exception:
    HAS_YAML = False

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.network.aci.mso import MSOModule, mso_argument_spec
from ansible.module_utils._text import to_text
from ansible_collections.cisco.aac.plugins.module_utils.mso import (
    api_endpoint_mappings,
    query_objs,
)


def main():
    argument_spec = mso_argument_spec()
    argument_spec.update(
        path=dict(type="str", required=True, aliases=["uri"]),
        method=dict(
            type="str",
            default="get",
            choices=["delete", "get", "post", "put", "patch", "post_or_put"],
            aliases=["action"],
        ),
        src=dict(type="path", aliases=["config_file"]),
        content=dict(type="raw"),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[["content", "src"]],
    )

    content = module.params["content"]
    path = module.params["path"]
    src = module.params["src"]
    method = module.params["method"]
    # required for MSOModule.exit_json()
    module.params["state"] = "present"

    # Report missing file
    file_exists = False
    if src:
        if os.path.isfile(src):
            file_exists = True
        else:
            module.fail_json(msg="Cannot find/access src '%s'" % src)

    mso = MSOModule(module)

    # We include the payload as it may be templated
    payload = content
    if file_exists:
        with open(src, "r") as config_object:
            # TODO: Would be nice to template this, requires action-plugin
            payload = config_object.read()

    # Validate payload
    if content and isinstance(content, dict):
        # Validate inline YAML/JSON
        payload = json.dumps(payload)
    elif payload and isinstance(payload, str) and HAS_YAML:
        try:
            # Validate YAML/JSON string
            payload = json.dumps(yaml.safe_load(payload))
        except Exception as e:
            module.fail_json(
                msg="Failed to parse provided JSON/YAML payload: %s" % to_text(e),
                exception=to_text(e),
                payload=payload,
            )
    if payload is not None:
        payload = json.loads(payload)

    lookup_cache = {}

    def lookup(path, search_key, use_cache=True):
        container = api_endpoint_mappings.get(path).get("container")
        key = api_endpoint_mappings.get(path).get("key")
        if lookup_cache.get(path) is None or not use_cache:
            lookup_cache[path] = query_objs(mso, path, key=container)
        for obj in lookup_cache[path]:
            if search_key is None or obj.get(key) == search_key:
                return obj
        return {}

    def update_ref(payload):
        if isinstance(payload, dict):
            match_regex = "%%.*?%.*?%%"
            for k, v in payload.items():
                if isinstance(v, list):
                    for o in v:
                        update_ref(o)
                else:
                    m = re.search(match_regex, str(v))
                    if m is not None:
                        d = m.group().find("%", 2)
                        path = m.group()[2:d]
                        key = m.group()[d + 1 : -2]
                        id = lookup(path, key).get("id")
                        if id is None:
                            mso.fail_json(
                                msg="Lookup failed for key '%s'" % key,
                                path=path,
                                key=key,
                            )
                        payload[k] = re.sub(match_regex, id, str(v))

    # replace names with IDs in references
    update_ref(payload)

    # update references in path
    path_dict = {"path": path}
    update_ref(path_dict)
    path = path_dict["path"]

    # Query for existing object(s)
    lookup_path = path
    lookup_value = None
    if method in ["put", "post_or_put"]:
        if lookup_path in api_endpoint_mappings:
            key = api_endpoint_mappings.get(lookup_path).get("key")
            has_id = api_endpoint_mappings.get(lookup_path).get("has_id")
            if key is not None:
                lookup_value = payload.get(key)
            mso.existing = lookup(lookup_path, lookup_value)
            if mso.existing and has_id:
                obj_id = mso.existing["id"]
                path = path + "/{id}".format(id=obj_id)
                method = "put"
            elif method == "post_or_put":
                method = "post"
            mso.previous = mso.existing

    if payload is not None:
        mso.sanitize(payload, collate=True)

    mso.existing = mso.request(path, method, data=mso.sent)

    # fix indempotency if put returns different result than get
    if (
        (mso.existing != mso.previous)
        and method == "put"
        and lookup_path in api_endpoint_mappings
    ):
        mso.existing = lookup(lookup_path, lookup_value, use_cache=False)

    # Remove keys storing version information. These keys break the idempotency check
    mso.existing.pop("_updateVersion", None)
    mso.existing.pop("version", None)
    mso.previous.pop("_updateVersion", None)
    mso.previous.pop("version", None)

    mso.exit_json()


if __name__ == "__main__":
    main()
