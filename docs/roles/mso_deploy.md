# mso_deploy

This role adds/modifies/deletes MSO objects.

## Sample Playbook

```yaml
---
- name: Deploy MSO
  hosts: mso
  gather_facts: no
 
  tasks:
    - name: MSO Deploy
      ansible.builtin.include_role:
        name: cisco.aac.mso_deploy
```

## Classes

Class | Example
---|---
System Config | [link](../model/mso/mso/system_config.md)
TACACS Provider | [link](../model/mso/mso/tacacs_provider.md)
Login Domain | [link](../model/mso/mso/login_domain.md)
Remote Location | [link](../model/mso/mso/remote_location.md)
User | [link](../model/mso/mso/user.md)
CA Certificate | [link](../model/mso/mso/ca_certificate.md)
Site | [link](../model/mso/mso/site.md)
Site Fabric Connectivity | [link](../model/mso/mso/fabric_connectivity.md)
Tenant | [link](../model/mso/mso/tenant.md)
Schema | [link](../model/mso/schema/schema.md)
DHCP Relay Policy | [link](../model/mso/mso/dhcp_relay.md)
DHCP Option Policy | [link](../model/mso/mso/dhcp_option.md)
