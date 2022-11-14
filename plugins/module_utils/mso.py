#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Daniel Schmidt <danischm@cisco.com>

api_endpoint_mappings = {
    "platform/remote-locations": {
        "container": "remoteLocations",
        "key": "name",
        "has_id": True,
    },
    "auth/providers/radius": {
        "container": "radiusProviders",
        "key": "host",
        "has_id": True,
    },
    "auth/providers/tacacs": {
        "container": "tacacsProviders",
        "key": "host",
        "has_id": True,
    },
    "auth/providers/ldap": {
        "container": "ldapProviders",
        "key": "host",
        "has_id": True,
    },
    "auth/domains": {"container": "domains", "key": "name", "has_id": True},
    "users": {"container": "users", "key": "username", "has_id": True},
    "roles": {"container": "roles", "key": "name", "has_id": True},
    "sites": {"container": "sites", "key": "name", "has_id": "yes"},
    "tenants": {"container": "tenants", "key": "name", "has_id": True},
    "schemas": {"container": "schemas", "key": "displayName", "has_id": True},
    "auth/security/certificates": {
        "container": "caCertificates",
        "key": "name",
        "has_id": True,
    },
    "platform/systemConfig": {
        "container": "systemConfigs",
        "key": None,
        "has_id": True,
    },
    "policies/dhcp/relay": {
        "container": "DhcpRelayPolicies",
        "key": "name",
        "has_id": True,
    },
    "policies/dhcp/option": {
        "container": "DhcpRelayPolicies",
        "key": "name",
        "has_id": True,
    },
    "platform/security/keyrings": {
        "container": "keyrings",
        "key": "name",
        "has_id": True,
    },
    "sites/fabric-connectivity": {"container": None, "key": None, "has_id": False},
    "tenants/allowed-users": {
        "container": None,
        "key": "domain_username",
        "has_id": True,
    },
}


def query_tenant_users(mso):
    found = []
    domains = {}
    objs = mso.request("tenants/allowed-users/domains", method="GET")
    for obj in objs["domains"]:
        domains[obj["id"]] = obj["name"]
    objs = mso.request("tenants/allowed-users", method="GET")
    if objs == {}:
        return found
    for obj in objs["users"]:
        if obj["domainId"] in domains:
            obj["domain_username"] = domains[obj["domainId"]] + "/" + obj["username"]
            found.append(obj)
    return found


def query_objs(mso, path, key=None, **kwargs):
    if path == "tenants/allowed-users":
        return query_tenant_users(mso)
    found = []
    objs = mso.request(path, method="GET")

    if objs == {}:
        return found

    if key is not None and key not in objs:
        mso.fail_json(msg="Key '%s' missing from data", data=objs)

    if key is None:
        return [objs]
    if not isinstance(objs[key], list):
        return [objs[key]]
    for obj in objs[key]:
        for kw_key, kw_value in kwargs.items():
            if kw_value is None:
                continue
            if obj[kw_key] != kw_value:
                break
        else:
            found.append(obj)
    return found
