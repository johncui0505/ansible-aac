# Vlan Pool

Description

{{ aac_doc }}
## Examples

```yaml
apic:
  access_policies:
    vlan_pools:
      - name: STATIC1
        description: "Static VLAN Pool"
        allocation: static
        ranges:
          - from: 4000
            to: 4002
            role: external
            description: "Range #1"
```
