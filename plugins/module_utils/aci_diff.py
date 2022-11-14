#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Daniel Schmidt <danischm@cisco.com>, Michael Wielpuetz <mwielpue@cisco.com>

from os import path

from ansible_collections.cisco.aac.plugins.module_utils.aac import (
    load_yaml_dir,
    get_paths,
)


class ACIDiff:
    """
    This class implements ACI diff functionality.
    Depending on the mode (all, only_changed, or only_provided) it will compare the previous deployment to the
    current deployment.
    """

    def __init__(self, params):
        self.__mode = params["mode"]
        self.__current_inventory = params["current_inventory"]
        self.__previous_inventory = params["previous_inventory"]

        self.__previous_config = {}
        self.__current_config = {}

        self.__validate()

    def __validate(self):
        """
        Validate the object. Will raise an Exception in case of an error.
        The Exception raised will contain additional error information.
        """
        if self.__mode == "only_changed" and not self.__previous_inventory:
            raise Exception(
                "Previous inventory (previous_inventory) required when using mode 'only_changed'."
            )

        if self.__previous_inventory and not path.exists(self.__previous_inventory):
            raise Exception(
                "The provided directory (previous_inventory) '{}' does not appear to exist."
                "Is it a directory?".format(self.__previous_inventory)
            )

        if not self.__current_inventory:
            raise Exception(
                "Current inventory (current_inventory) is a required parameter."
            )

        if not path.exists(self.__current_inventory):
            raise Exception(
                "The provided directory (current_inventory) '{}' does not appear to exist."
                "Is it a directory?".format(self.__current_inventory)
            )

    def get_current_config(self):
        return self.__current_config

    def get_previous_config(self):
        return self.__previous_config

    def load_configurations(self):
        """
        Load current and previous configurations.
        """
        # Previous inventory has already been validated.
        # There are situations where it is ok to not provide a previous_inventory
        # , e.g. with render mode 'all'
        if self.__previous_inventory:
            try:
                self.__previous_config = load_yaml_dir(self.__previous_inventory)
            except Exception as e:
                raise Exception(
                    "Cannot read files from '{}' - {}".format(
                        self.__previous_inventory, e
                    )
                )

        try:
            self.__current_config = load_yaml_dir(self.__current_inventory)
        except Exception as e:
            raise Exception(
                "Cannot read files from '{}' - {}".format(self.__current_inventory, e)
            )

    def get_states(self):
        """
        This function will return all states, when rendering mode is only_provided.
        If render mode is all, or only_changed it will always return an empty list.
        """
        states = []
        if self.__mode == "only_provided":
            states = get_paths(self.__current_config)

        return states
