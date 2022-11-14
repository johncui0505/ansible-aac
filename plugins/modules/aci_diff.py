#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Daniel Schmidt <danischm@cisco.com>

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {"metadata_version": "0.1", "status": ["preview"]}

DOCUMENTATION = r"""
---
module: aci_diff
short_description: Find modified objects.
description:
- Create a list of changed objects based on diff.
version_added: '2.8'
options:
  mode:
    description:
    - The mode to use.
    type: str
    choices: [ only_provided, only_changed, all ]
    default: only_provided
  current_inventory:
    description:
    - The path to the current inventory files.
    type: str
    required: yes
  previous_inventory:
    description:
    - The path to the inventory files from the previous run.
    - Required in C(only_changed) mode.
    type: str
    required: no
  objects:
    description:
    - A list of objects.
    type: list
    required: no
  leaf_objects:
    description:
    - A list of leaf objects.
    type: list
    required: no
  leafs:
    description:
    - A list of leafs.
    type: list
    required: no
  spine_objects:
    description:
    - A list of spine objects.
    type: list
    required: no
  spines:
    description:
    - A list of spines.
    type: list
    required: no
  tenant_objects:
    description:
    - A list of tenant objects.
    type: list
    required: no
  tenants:
    description:
    - A list of tenants.
    type: list
    required: no
  skip_non_idempotent_tasks:
    description:
    - Skip non-idempotent tasks.
    type: bool
    required: no
author:
- Daniel Schmidt
"""

EXAMPLES = r"""

"""

RETURN = r"""

"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.cisco.aac.plugins.module_utils.aac import compare

from ansible_collections.cisco.aac.plugins.module_utils.aci_diff import ACIDiff


def match(path1, path2):
    return path1 in path2 or path2 in path1


def tenant_in_scope(tenant, object):
    if (tenant in ["infra", "mgmt"] and tenant in object.get("scope", [])) or (
        tenant not in ["infra", "mgmt"] and "user" in object.get("scope", [])
    ):
        return True
    return False


def run_module():
    module_args = dict(
        mode=dict(
            type="str",
            default="only_provided",
            choices=["only_provided", "only_changed", "all"],
        ),
        current_inventory=dict(type="str", required=True),
        previous_inventory=dict(type="str", required=False),
        objects=dict(type="list", elements="dict", required=False),
        leaf_objects=dict(type="list", elements="dict", required=False),
        leafs=dict(type="list", elements="str", required=False),
        spine_objects=dict(type="list", elements="dict", required=False),
        spines=dict(type="list", elements="str", required=False),
        tenant_objects=dict(type="list", elements="dict", required=False),
        tenants=dict(type="list", elements="str", required=False),
        skip_non_idempotent_tasks=dict(type="bool", required=False),
    )

    result = dict(changed=False)

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    aci_diff = None
    try:
        aci_diff = ACIDiff(module.params)
    except Exception as e:
        module.fail_json(msg="{}".format(e))

    mode = module.params["mode"]
    objects = module.params["objects"]
    leaf_objects = module.params["leaf_objects"]
    leafs = module.params["leafs"]
    spine_objects = module.params["spine_objects"]
    spines = module.params["spines"]
    tenant_objects = module.params["tenant_objects"]
    tenants = module.params["tenants"]
    skip_non_idempotent_tasks = module.params["skip_non_idempotent_tasks"]

    # remove empty strings from lists
    if leafs:
        leafs = [i for i in leafs if i]
    if spines:
        spines = [i for i in spines if i]
    if tenants:
        tenants = [i for i in tenants if i]

    try:
        aci_diff.load_configurations()
    except Exception as e:
        module.fail_json(msg="{}".format(e))

    previous = aci_diff.get_previous_config()
    current = aci_diff.get_current_config()

    if module.check_mode:
        module.exit_json(**result)

    if mode == "only_changed":
        diff = compare(previous, current)
        result["diff"] = diff
        changed_tenants = []
        for diff_element in diff:
            tenant = diff_element.get("tenant")
            if tenant and tenant not in changed_tenants:
                changed_tenants.append(tenant)

    states = aci_diff.get_states()
    result["states"] = states

    if objects:
        result_objects = []
        result_test_objects = []

        for obj in objects:
            # skip objects with either configure=true or non-idempotent tasks
            if skip_non_idempotent_tasks and not obj.get("idempotent", True):
                continue
            if mode == "all":
                if obj.get("configure", True):
                    result_objects.append([obj, "", ""])
                for type in obj.get("test_types", []):
                    test_obj = dict(obj)
                    test_obj["type"] = type
                    result_test_objects.append([test_obj, "", ""])
            elif mode == "only_changed":
                # compile a list of changed objects (result_objects)
                if obj.get("configure", True):
                    # only append object if path affected
                    paths = obj.get("paths", []) + obj.get("diff_paths", [])
                    for path in paths:
                        for diff_element in diff:
                            r_object = [obj, "", ""]
                            if (
                                match(path, diff_element["path"])
                                and r_object not in result_objects
                            ):
                                result_objects.append(r_object)
                # compile a list of tests (result_test_objects)
                for type in obj.get("test_types", []):
                    # skip config test if config has not changed
                    if type == "config" and [obj, "", ""] not in result_objects:
                        continue
                    test_obj = dict(obj)
                    test_obj["type"] = type
                    result_test_objects.append([test_obj, "", ""])
            elif mode == "only_provided":
                if obj.get("configure", True):
                    r_object = [obj, "", ""]
                    # only append object if path affected
                    for path in obj.get("paths", []):
                        for state in states:
                            if (
                                match(path, state.get("path"))
                                and r_object not in result_objects
                            ):
                                result_objects.append(r_object)
                                for type in obj.get("test_types", []):
                                    test_obj = dict(obj)
                                    test_obj["type"] = type
                                    result_test_objects.append([test_obj, "", ""])

        result["objects"] = result_objects
        result["test_objects"] = result_test_objects

        result_folders = []
        result_test_folders = []

        for obj in result_objects:
            folder = obj[0].get("folder")
            if folder is not None and folder not in result_folders:
                result_folders.append(folder)

        for obj in result_test_objects:
            for type in obj[0].get("test_types", []):
                test_folder = "{}/{}".format(type, obj[0].get("folder"))
                if test_folder is not None and test_folder not in result_test_folders:
                    result_test_folders.append(test_folder)

        result["folders"] = result_folders
        result["test_folders"] = result_test_folders

    for node_type in ["leaf", "spine"]:
        if node_type == "leaf":
            node_objects = leaf_objects
            nodes = leafs
        else:
            node_objects = spine_objects
            nodes = spines

        if node_objects:
            result_node_objects = []
            result_nodes = []
            result_node_test_objects = []

            for node in nodes:
                for obj in node_objects:
                    if mode == "all":
                        if obj.get("configure", True):
                            result_node_objects.append([obj, str(node), ""])
                        for type in obj.get("test_types", []):
                            test_obj = dict(obj)
                            test_obj["type"] = type
                            result_node_test_objects.append([test_obj, str(node), ""])
                        if node not in result_nodes:
                            result_nodes.append(node)
                    elif mode == "only_changed":
                        if obj.get("configure", True):
                            paths = obj.get("paths", []) + obj.get("diff_paths", [])
                            for path in paths:
                                for diff_element in diff:
                                    r_object = [obj, str(diff_element.get("node")), ""]
                                    if (
                                        match(path, diff_element["path"])
                                        and diff_element.get("node") == node
                                        and r_object not in result_node_objects
                                    ):
                                        result_node_objects.append(r_object)
                                        if node not in result_nodes:
                                            result_nodes.append(node)
                        for type in obj.get("test_types", []):
                            if (
                                type == "config"
                                and [obj, str(node), ""] not in result_node_objects
                            ):
                                continue
                            test_obj = dict(obj)
                            test_obj["type"] = type
                            result_node_test_objects.append([test_obj, str(node), ""])
                    elif mode == "only_provided":
                        if obj.get("configure", True):
                            for path in obj.get("paths", []):
                                for element in states:
                                    r_object = [obj, str(node), ""]
                                    if (
                                        match(path, element["path"])
                                        and element.get("node") == node
                                        and r_object not in result_node_objects
                                    ):
                                        result_node_objects.append(r_object)
                                        if node not in result_nodes:
                                            result_nodes.append(node)
                                        for type in obj.get("test_types", []):
                                            test_obj = dict(obj)
                                            test_obj["type"] = type
                                            result_node_test_objects.append(
                                                [test_obj, str(node), ""]
                                            )

            if node_type == "leaf":
                result["leaf_objects"] = result_node_objects
                result["leafs"] = result_nodes
                result["leaf_test_objects"] = result_node_test_objects
            else:
                result["spine_objects"] = result_node_objects
                result["spines"] = result_nodes
                result["spine_test_objects"] = result_node_test_objects

    if tenant_objects:
        result_tenant_objects = []
        result_tenant_test_objects = []
        result_tenants = []

        for tenant in tenants:
            for obj in tenant_objects:
                if mode == "all":
                    if obj.get("configure", True):
                        if tenant_in_scope(tenant, obj):
                            result_tenant_objects.append([obj, "", tenant])
                    for type in obj.get("test_types", []):
                        test_obj = dict(obj)
                        test_obj["type"] = type
                        result_tenant_test_objects.append([test_obj, "", tenant])
                    if tenant not in result_tenants:
                        result_tenants.append(tenant)
                elif mode == "only_changed":
                    if obj.get("configure", True):
                        paths = obj.get("paths", []) + obj.get("diff_paths", [])
                        for path in paths:
                            for diff_element in diff:
                                r_object = [obj, "", str(diff_element.get("tenant"))]
                                if (
                                    match(path, diff_element["path"])
                                    and tenant_in_scope(diff_element.get("tenant"), obj)
                                    and diff_element.get("tenant") == tenant
                                    and r_object not in result_tenant_objects
                                ):
                                    result_tenant_objects.append(r_object)
                                    if tenant not in result_tenants:
                                        result_tenants.append(tenant)
                    for type in obj.get("test_types", []):
                        if (
                            type == "config"
                            and [obj, "", tenant] not in result_tenant_objects
                        ):
                            continue
                        # skip tests for untouched tenants
                        if tenant not in changed_tenants:
                            continue
                        test_obj = dict(obj)
                        test_obj["type"] = type
                        result_tenant_test_objects.append([test_obj, "", tenant])
                elif mode == "only_provided":
                    if obj.get("configure", True):
                        for path in obj.get("paths", []):
                            for element in states:
                                r_object = [obj, "", str(tenant)]
                                if (
                                    match(path, element["path"])
                                    and element.get("tenant") == tenant
                                    and tenant_in_scope(element.get("tenant"), obj)
                                    and r_object not in result_tenant_objects
                                ):
                                    result_tenant_objects.append(r_object)
                                    if tenant not in result_tenants:
                                        result_tenants.append(tenant)
                                    for type in obj.get("test_types", []):
                                        test_obj = dict(obj)
                                        test_obj["type"] = type
                                        result_tenant_test_objects.append(
                                            [test_obj, "", tenant]
                                        )

        result["tenant_objects"] = result_tenant_objects
        result["tenant_test_objects"] = result_tenant_test_objects
        result["tenants"] = result_tenants

        result_test_tenant_folders = []

        for obj in result_tenant_test_objects:
            if len(obj) > 2:
                tenant = obj[2]
                for type in obj[0].get("test_types", []):
                    test_folder = "{}/tenants/{}".format(type, tenant)
                    if (
                        test_folder is not None
                        and test_folder not in result_test_tenant_folders
                    ):
                        result_test_tenant_folders.append(test_folder)

        result["test_tenant_folders"] = result_test_tenant_folders

    if mode == "only_changed" and len(diff):
        result["changed"] = True
    elif mode == "only_provided" and len(states):
        result["changed"] = True

    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
