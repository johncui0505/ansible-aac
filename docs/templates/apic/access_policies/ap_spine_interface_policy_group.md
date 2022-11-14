# Access Spine Interface Policy Group

Description

{{ aac_doc }}
## Examples

```yaml
apic:
  access_policies:
    spine_interface_policy_groups:
      - name: IPN1
        link_level_policy: 10G
        cdp_policy: CDP-ENABLED
        aaep: AAEP1
```
