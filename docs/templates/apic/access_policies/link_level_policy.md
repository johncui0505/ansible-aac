# Link Level Interface Policy

Description

{{ aac_doc }}

## Examples

```yaml
apic:
  access_policies:
    interface_policies:
      link_level_policies:
        - name: 10G
          speed: 10G
          auto: true
          fec_mode: inherit
```
