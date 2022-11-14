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
module: mso_delete
short_description: Delete MSO objects
description:
- Delete MSO objects based on desired inventory.
author:
- Daniel Schmidt
version_added: '2.8'
options:
  path:
    description:
    - URI being used to execute API calls.
    type: str
    required: yes
    aliases: [ uri ]
  desired:
    description:
    - List of desired objects, all others will be deleted
    type: list
extends_documentation_fragment: mso
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.network.aci.mso import MSOModule, mso_argument_spec
from ansible_collections.cisco.aac.plugins.module_utils.mso import (
    api_endpoint_mappings,
)


def main():
    argument_spec = mso_argument_spec()
    argument_spec.update(
        path=dict(type="str", required=True, aliases=["uri"]),
        desired=dict(type="list", elements="str", required=False),
        ignore=dict(type="list", elements="str", required=False),
        ignore_attr=dict(type="list", elements="str", required=False),
    )

    module = AnsibleModule(argument_spec=argument_spec)

    path = module.params["path"]
    desired = module.params["desired"]
    ignore = module.params["ignore"]
    ignore_attr = module.params["ignore_attr"]
    # required for MSOModule.exit_json()
    module.params["state"] = "absent"

    mso = MSOModule(module)

    ids_to_delete = []

    container = api_endpoint_mappings.get(path).get("container")
    key = api_endpoint_mappings.get(path).get("key")
    if ignore is None:
        ignore = []
    if ignore_attr is None:
        ignore_attr = [key]
    else:
        ignore_attr.append(key)
    objs = mso.query_objs(path, key=container)
    for obj in objs:
        if obj.get(key) not in desired:
            found_ignore = False
            for attr in ignore_attr:
                if obj.get(attr) in ignore:
                    found_ignore = True
            if not found_ignore:
                ids_to_delete.append(obj.get("id"))

    for id in ids_to_delete:
        del_path = "{path}/{id}".format(path=path, id=id)
        mso.existing = mso.request(del_path, method="DELETE")

    if "password" in mso.existing:
        mso.existing["password"] = "******"

    mso.exit_json()


if __name__ == "__main__":
    main()
