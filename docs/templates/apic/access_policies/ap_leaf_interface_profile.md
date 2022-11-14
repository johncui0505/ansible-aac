# Access Leaf Interface Profile

Description

{{ aac_doc }}

## Examples

```yaml
apic:
  auto_generate_switch_pod_profiles: true
  access_policies:
    leaf_interface_profile_name: "LEAF\\g<id>"
    leaf_interface_selector_name: "ETH\\g<mod>-\\g<port>"
```
