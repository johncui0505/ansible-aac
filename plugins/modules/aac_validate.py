#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2022, Daniel Schmidt <danischm@cisco.com>

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {"metadata_version": "0.1", "status": ["preview"]}

DOCUMENTATION = r"""
---
module: aac_validate
short_description: Perform syntactic and semantic validation of YAML files.
description:
- Perform syntactic and semantic validation of YAML files.
version_added: '2.12'
options:
  schema:
    description:
    - The path to the schema file.
    type: str
    required: no
  rules:
    description:
    - The path to a directory with semantic validation rules.
    type: str
    required: no
  dir:
    description:
    - The path to a directory with yaml files.
    type: str
    required: yes
author:
- Daniel Schmidt
"""

EXAMPLES = r"""

"""

RETURN = r"""

"""

import os

from ansible.module_utils.basic import AnsibleModule
import iac_validate.validator


def run_module():
    module_args = dict(
        schema=dict(type="str", required=False),
        rules=dict(type="str", required=False),
        dir=dict(type="str", required=True),
    )

    result = dict(changed=False)

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    schema = module.params["schema"]
    rules = module.params["rules"]
    dir = module.params["dir"]

    if dir and not os.path.exists(dir):
        module.fail_json(
            msg="The provided directory (dir) does not appear to exist. Is it a directory?"
        )

    if rules and not os.path.exists(rules):
        module.fail_json(
            msg="The provided directory (rules) does not appear to exist. Is it a directory?"
        )

    validator = iac_validate.validator.Validator(schema, rules)
    if schema:
        validator.validate_syntax([dir])
    if rules:
        validator.validate_semantics([dir])

    msg = ""
    for error in validator.errors:
        msg += error + "\n"

    if msg:
        module.fail_json(msg=msg)

    if len(os.listdir(dir)):
        result["changed"] = True

    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
