#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Daniel Schmidt <danischm@cisco.com>

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {"metadata_version": "0.1", "status": ["preview"]}

DOCUMENTATION = r"""
---
module: aci_find
short_description: find objects in tree
description:
- Find objects (DNs) in object tree.
version_added: '2.8'
options:
  aci_class:
    description:
    - A list of classes to find.
    type: list
    required: yes
  tree:
    description:
    - The object tree (list).
    type: list
    required: yes

extends_documentation_fragment: aci
seealso:
- name: APIC Management Information Model reference
  description: More information about the internal APIC class B(fv:Tenant).
  link: https://developer.cisco.com/docs/apic-mim-ref/
author:
- Daniel Schmidt
"""

EXAMPLES = r"""

"""

RETURN = r"""

"""

from ansible.module_utils.basic import AnsibleModule


def run_module():
    argument_spec = dict(
        aci_class=dict(type="list", elements="str"),
        tree=dict(type="list", elements="dict"),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False,
    )

    classes = module.params["aci_class"]
    tree = module.params["tree"]
    changed = True
    result = dict()

    dn_found = []

    for cl in classes:

        def find_object(obj, inventory, dn):
            if obj in inventory:
                if "dn" in inventory[obj]["attributes"]:
                    dn_found.append(inventory[obj]["attributes"]["dn"])
                elif "rn" in inventory[obj]["attributes"]:
                    dn_found.append(dn + "/" + inventory[obj]["attributes"]["rn"])
            else:
                if isinstance(inventory, dict):
                    for k, v in inventory.items():
                        c_dn = dn
                        if "dn" in v["attributes"]:
                            c_dn = v["attributes"]["dn"]
                        elif "rn" in v["attributes"]:
                            c_dn += "/" + v["attributes"]["rn"]
                        if "children" in v:
                            for o in v["children"]:
                                find_object(obj, o, c_dn)

        for o in tree:
            find_object(cl, o, "")

    # TODO: build module return values
    result["changed"] = changed
    result["found_dn"] = dn_found

    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
