# Infra DSCP Translation Policy

Description

{{ aac_doc }}

## Examples

```yaml
apic:
  fabric_policies:
    infra_dscp_translation_policy:
      admin_state: true
      control_plane: CS7
      level_1: EF
      level_2: CS3
      level_3: CS0
      level_4: AF11
      level_5: AF21
      level_6: AF31
      policy_plane: CS4
      span: CS1
      traceroute: CS2
```
