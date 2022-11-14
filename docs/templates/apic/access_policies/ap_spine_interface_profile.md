# Access Spine Interface Profile

Description

{{ aac_doc }}

## Examples

```yaml
apic:
  auto_generate_switch_pod_profiles: true
  access_policies:
    spine_interface_profile_name: "SPINE\\g<id>"
    spine_interface_selector_name: "ETH\\g<mod>-\\g<port>"
```
