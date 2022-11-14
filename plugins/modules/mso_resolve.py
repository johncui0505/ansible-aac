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
- Enables the management of the Cisco MSO through direct access to the Cisco MSO REST API.
author:
- Daniel Schmidt
version_added: '2.8'
options:
  src:
    description:
    - Name of the absolute path of the filename that includes template.
    type: path
  dest:
    description:
    - Name of the absolute path of the filename that should be created.
    type: path
extends_documentation_fragment: mso
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""

import os
import re

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.network.aci.mso import MSOModule, mso_argument_spec
from ansible_collections.cisco.aac.plugins.module_utils.mso import (
    api_endpoint_mappings,
    query_objs,
)


def main():
    argument_spec = mso_argument_spec()
    argument_spec.update(
        src=dict(type="path", required=True), dest=dict(type="path", required=True)
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
    )

    src = module.params["src"]
    dest = module.params["dest"]
    # required for MSOModule.exit_json()
    module.params["state"] = "present"

    if os.path.isfile(src):
        with open(src, "r") as src_file:
            content = src_file.read()
    else:
        module.fail_json(msg="Cannot find/access src '%s'" % src)

    mso = MSOModule(module)

    lookup_cache = {}

    def lookup(path, search_key):
        container = api_endpoint_mappings.get(path).get("container")
        key = api_endpoint_mappings.get(path).get("key")
        if lookup_cache.get(path) is None:
            lookup_cache[path] = query_objs(mso, path, key=container)
        for obj in lookup_cache[path]:
            if search_key is None or obj.get(key) == search_key:
                return obj
        return {}

    def update_ref(payload):
        match_regex = "%%.*?%.*?%%"
        m = re.search(match_regex, payload)
        while m is not None:
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
            payload = re.sub(m.group(), id, payload)
            m = re.search(match_regex, payload)
        return payload

    # replace names with IDs
    content = update_ref(content)

    mso.result["changed"] = True

    if os.path.isfile(dest):
        with open(dest, "r") as dest_file:
            existing = dest_file.read()
            if existing == content:
                mso.result["changed"] = False

    with open(dest, "w") as dest_file:
        dest_file.write(content)

    mso.exit_json()


if __name__ == "__main__":
    main()
