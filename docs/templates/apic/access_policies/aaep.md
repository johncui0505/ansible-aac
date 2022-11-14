# AAEP

Description

{{ aac_doc }}

## Examples

```yaml
apic:
  access_policies:
    aaeps:
      - name: AAEP1
        infra_vlan: true
        physical_domains:
          - PHY1
        routed_domains:
          - ROUTED1
        vmware_vmm_domains:
          - VMM1
        endpoint_groups:
          - tenant: ABC
            application_profile: AP1
            endpoint_group: EPG1
            vlan: 1234
            mode: untagged
            deployment_immediacy: immediate
```
