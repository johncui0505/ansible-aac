#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Daniel Schmidt <danischm@cisco.com>

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {"metadata_version": "0.1", "status": ["preview"]}

DOCUMENTATION = r"""
---
module: aci_delete
short_description: delete objects
description:
- Delete objects based on comparison to desired json inventory.
version_added: '2.8'
options:
  aci_class:
    description:
    - A list of classes to delete.
    type: list
    required: yes
  file:
    description:
    - The path to the json inventory file.
    type: str
    required: yes
  ignore:
    description:
    - List of additional attribute values (except 'default') to ignore.
    type: list
  ignore_attr:
    description:
    - List of additional attributes (except 'name') to consider to ignore.
    type: list
  match_dn:
    description:
    - Only delete objects if dn matches.
    type: str
  ignore_annotations:
    description:
    - List of annotations to ignore.
    type: list
  only_aac:
    description:
    - Only delete AAC objects ("orchestrator:aac" annotation).
    type: bool
    default: yes
    required: no

extends_documentation_fragment: aci
seealso:
- name: APIC Management Information Model reference
  description: More information about the internal APIC classes.
  link: https://developer.cisco.com/docs/apic-mim-ref/
author:
- Daniel Schmidt
"""

EXAMPLES = r"""

"""

RETURN = r"""

"""

import re
import os
import json
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.network.aci.aci import ACIModule, aci_argument_spec

DEFAULT_IGNORE_ATTR_VALUE = "default"
DEFAULT_IGNORE_ATTR = "name"
AAC_ANNOTATION = "orchestrator:aac"


def main():
    argument_spec = aci_argument_spec()
    argument_spec.update(
        aci_class=dict(type="list", elements="str"),
        file=dict(type="str"),
        ignore=dict(type="list", elements="str", required=False),
        ignore_attr=dict(type="list", elements="str", required=False),
        match_dn=dict(type="str", required=False),
        ignore_annotations=dict(type="list", required=False, default=[]),
        only_aac=dict(type="bool", default=True, required=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    changed = False
    classes = module.params["aci_class"]
    file = module.params["file"]
    ignore = [DEFAULT_IGNORE_ATTR_VALUE]
    if len(module.params["ignore"]) > 0 and module.params["ignore"][0]:
        ignore.extend(module.params["ignore"])
    ignore_attr = [DEFAULT_IGNORE_ATTR]
    if len(module.params["ignore_attr"]) > 0 and module.params["ignore_attr"][0]:
        ignore_attr.extend(module.params["ignore_attr"])
    match_dn = module.params["match_dn"]
    ignore_annotations = module.params["ignore_annotations"]
    only_aac = module.params["only_aac"]

    aci = ACIModule(module)

    dn_deleted = []

    for cl in classes:
        if not cl:
            continue
        aci.params["state"] = "query"
        aci.construct_url(
            root_class=dict(
                aci_class=cl,
                aci_rn=None,
                module_object=None,
                target_filter={},
            ),
        )
        aci.get_existing()

        if not os.path.exists(file):
            aci.module.fail_json(
                msg="The provided file does not appear to exist. Is it a filename?"
            )
        try:
            with open(file, "r") as fh:
                inv = json.loads(fh.read())
        except Exception:
            aci.module.fail_json(msg="Cannot open file '%s'." % aci.params["file"])

        # create a list of DNs from json inventory
        dn_list = []

        def find_object(obj, inventory):
            if obj in inventory:
                dn_list.append(inventory[obj]["attributes"]["dn"])
            else:
                for k, v in inventory.items():
                    if "children" in v:
                        for o in v["children"]:
                            find_object(obj, o)

        find_object(cl, inv)

        # create a list of DNs to delete
        dn_delete = []
        for o in aci.existing:
            att = o[cl]["attributes"]
            if att["dn"] not in dn_list:
                found_ignore = False
                # ignore MSO objects
                if "annotation" in att:
                    if only_aac and att["annotation"] != AAC_ANNOTATION:
                        continue
                    if att["annotation"] in set(ignore_annotations):
                        continue
                for ia in ignore_attr:
                    if ia in att and att[ia] in ignore:
                        found_ignore = True
                if not found_ignore:
                    dn_delete.append(att["dn"])

        # filter objects
        dn_delete_filter = list(dn_delete)
        if match_dn:
            for dn in dn_delete:
                if not re.search(match_dn, dn):
                    dn_delete_filter.remove(dn)
        dn_delete = dn_delete_filter

        dn_deleted.append(dn_delete)

        # delete objects
        for dn in dn_delete:
            # remove 'uni/' prefix
            prefix = "uni/"
            rn = dn[len(prefix) :] if dn.startswith(prefix) else dn
            aci.construct_url(
                root_class=dict(
                    aci_class=cl,
                    aci_rn=rn,
                    module_object="a",
                    target_filter={},
                ),
            )
            aci.get_existing()
            aci.delete_config()
            if aci.result["changed"]:
                changed = True

    # TODO: build module return values
    aci.result["changed"] = changed
    aci.result["deleted_dn"] = dn_deleted

    aci.exit_json()


if __name__ == "__main__":
    main()
