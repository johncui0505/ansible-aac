# External Connectivity Policy

Description

{{ aac_doc }}
## Examples

```yaml
apic:
  fabric_policies:
    external_connectivity_policy:
      name: IPN
      site_id: 1
      bgp_password: cisco
      routing_profiles:
        - name: IPN1
          subnets:
            - 11.1.0.0/16
  pod_policies:
    pods:
      - id: 1
        data_plane_tep: 1.2.3.4
```
