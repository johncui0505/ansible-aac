#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Daniel Schmidt <danischm@cisco.com>

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {"metadata_version": "0.1", "status": ["preview"]}

DOCUMENTATION = r"""
---
module: aac_pabot
short_description: Run pabot.
description:
- Run pabot.
version_added: '2.8'
options:
  tests:
    description:
    - The path to tests (file or dir).
    type: str
    required: yes
  variable_file:
    description:
    - The path to a variable file.
    type: str
    required: no
  name:
    description:
    - Report name.
    type: str
    required: no
  results_dir:
    description:
    - Directory to store test results.
    type: str
    required: no
  output_file:
    description:
    - Path to XML output file relative to C(results_dir).
    type: str
    required: no
  log_file:
    description:
    - Path to log file relative to C(results_dir).
    type: str
    required: no
  report_file:
    description:
    - Path to report file relative to C(results_dir).
    type: str
    required: no
  xunit_file:
    description:
    - Path to xunit file relative to C(results_dir).
    type: str
    required: no
  skip_on_failure_tag:
    description:
    - Tag for skip-on-failure tests.
    type: str
    required: no
  run_empty_suites:
    description:
    - Run suites with no tests.
    type: bool
    default: yes
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


def run_module():
    module_args = dict(
        tests=dict(type="str", required=True),
        variable_file=dict(type="str", required=False),
        name=dict(type="str", required=False),
        results_dir=dict(type="str", required=False),
        output_file=dict(type="str", required=False),
        log_file=dict(type="str", required=False),
        report_file=dict(type="str", required=False),
        xunit_file=dict(type="str", required=False),
        skip_on_failure_tag=dict(type="str", required=False),
        run_empty_suites=dict(type="bool", default=True, required=False),
    )

    result = dict(changed=False)

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    tests = module.params["tests"]
    variable_file = module.params["variable_file"]
    name = module.params["name"]
    results_dir = module.params["results_dir"]
    output_file = module.params["output_file"]
    log_file = module.params["log_file"]
    report_file = module.params["report_file"]
    xunit_file = module.params["xunit_file"]
    skip_on_failure_tag = module.params["skip_on_failure_tag"]
    run_empty_suites = module.params["run_empty_suites"]

    if tests and not os.path.exists(tests):
        module.fail_json(
            msg="The provided file or directory (tests) does not appear to exist."
        )

    if results_dir and not os.path.exists(results_dir):
        module.fail_json(
            msg="The provided directory (results_dir) does not appear to exist. Is it a directory?"
        )

    options = []

    if variable_file:
        options.append("--variablefile")
        options.append(variable_file)
    if name:
        options.append("--name")
        options.append(name)
    if results_dir:
        options.append("--outputdir")
        options.append(results_dir)
    if output_file:
        options.append("--output")
        options.append(output_file)
    if log_file:
        options.append("--log")
        options.append(log_file)
    if report_file:
        options.append("--report")
        options.append(report_file)
    if xunit_file:
        options.append("--xunit")
        options.append(xunit_file)
    if skip_on_failure_tag:
        options.append("--skiponfailure")
        options.append(skip_on_failure_tag)
    if run_empty_suites:
        options.append("--runemptysuite")

    tests_list = tests.split(" ")
    options.extend(tests_list)

    command = ["pabot"]
    command.extend(options)

    rc, _, _ = module.run_command(command)

    if rc > 0 and rc < 251:
        result["failed_tests"] = rc

    result["rc"] = rc
    result["changed"] = True

    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
