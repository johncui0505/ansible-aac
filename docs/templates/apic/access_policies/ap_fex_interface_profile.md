# Access FEX Interface Profile

Description

{{ aac_doc }}

## Examples

```yaml
apic:
  auto_generate_switch_pod_profiles: true
  access_policies:
    fex_profile_name: "LEAF\\g<id>-FEX\\g<fex>"
    fex_interface_selector_name: "ETH\\g<mod>-\\g<port>"
```
