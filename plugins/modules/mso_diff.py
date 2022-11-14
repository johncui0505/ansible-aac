#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Daniel Schmidt <danischm@cisco.com>

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {"metadata_version": "0.1", "status": ["preview"]}

DOCUMENTATION = r"""
---
module: mso_diff
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
author:
- Daniel Schmidt
"""

EXAMPLES = r"""

"""

RETURN = r"""

"""

import os

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.cisco.aac.plugins.module_utils.aac import (
    load_yaml_dir,
    compare,
    get_paths,
)


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
    )

    result = dict(changed=False)

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    mode = module.params["mode"]
    current_inventory = module.params["current_inventory"]
    previous_inventory = module.params["previous_inventory"]
    objects = module.params["objects"]

    if mode == "only_changed" and not previous_inventory:
        module.fail_json(
            msg="Previous inventory (previous_inventory) required when using mode 'only_changed'."
        )

    if previous_inventory and not os.path.exists(previous_inventory):
        module.fail_json(
            msg="The provided directory (previous_inventory) does not appear to exist. Is it a directory?"
        )
    try:
        previous = load_yaml_dir(previous_inventory)
    except Exception:
        module.fail_json(msg="Cannot read files from '%s'." % previous_inventory)

    if not os.path.exists(current_inventory):
        module.fail_json(
            msg="The provided directory (current_inventory) does not appear to exist. Is it a directory?"
        )
    try:
        current = load_yaml_dir(current_inventory)
    except Exception:
        module.fail_json(msg="Cannot read files from '%s'." % current_inventory)

    if module.check_mode:
        module.exit_json(**result)

    tenants = []
    schemas = []

    if mode == "only_changed":
        diff = compare(previous, current)
        result["diff"] = diff
        for diff_element in diff:
            tenant = diff_element.get("tenant")
            schema = diff_element.get("schema")
            if tenant and tenant not in tenants:
                tenants.append(tenant)
            if schema and schema not in schemas:
                schemas.append(schema)
    else:
        states = get_paths(current)
        result["states"] = states
        for element in states:
            tenant = element.get("tenant")
            schema = element.get("schema")
            if tenant and tenant not in tenants:
                tenants.append(tenant)
            if schema and schema not in schemas:
                schemas.append(schema)

    result["schemas"] = schemas

    if objects:
        result_objects = []
        result_test_objects = []

        for obj in objects:
            obj["diff_object_ids"] = obj["object_ids"]
            if mode == "all":
                if obj.get("configure", True):
                    result_objects.append(obj)
                for type in obj.get("test_types", []):
                    test_obj = dict(obj)
                    test_obj["type"] = type
                    result_test_objects.append(test_obj)
            elif mode == "only_changed":
                if obj.get("configure", True):
                    paths = obj.get("paths", []) + obj.get("diff_paths", [])
                    for path in paths:
                        for diff_element in diff:
                            if (
                                path in diff_element["path"]
                                and obj not in result_objects
                            ):
                                if obj.get("api_path") == "tenants":
                                    obj["diff_object_ids"] = tenants
                                elif obj.get("api_path") == "schemas":
                                    obj["diff_object_ids"] = schemas
                                result_objects.append(obj)
                for type in obj.get("test_types", []):
                    if type == "config" and obj not in result_objects:
                        continue
                    test_obj = dict(obj)
                    test_obj["type"] = type
                    result_test_objects.append(test_obj)
            elif mode == "only_provided":
                if obj.get("configure", True):
                    for path in obj.get("paths", []):
                        for state in states:
                            if path in state.get("path") and obj not in result_objects:
                                if obj.get("api_path") == "tenants":
                                    obj["diff_object_ids"] = tenants
                                elif obj.get("api_path") == "schemas":
                                    obj["diff_object_ids"] = schemas
                                result_objects.append(obj)
                                for type in obj.get("test_types", []):
                                    test_obj = dict(obj)
                                    test_obj["type"] = type
                                    result_test_objects.append(test_obj)

        result["objects"] = result_objects
        result["test_objects"] = result_test_objects

        result_test_folders = []

        for obj in result_test_objects:
            for type in obj.get("test_types", []):
                test_folder = obj.get("folder")
                if (
                    test_folder is not None
                    and [type, test_folder] not in result_test_folders
                ):
                    result_test_folders.append([type, test_folder])

        result["test_folders"] = result_test_folders

    if mode == "only_changed" and len(diff):
        result["changed"] = True
    elif mode == "only_provided" and len(states):
        result["changed"] = True

    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
