# L2 Interface Policy

Description

{{ aac_doc }}

## Examples

```yaml
apic:
  access_policies:
    interface_policies:
      l2_policies:
        - name: PORT-LOCAL
          vlan_scope: portlocal
          qinq: disabled
```
