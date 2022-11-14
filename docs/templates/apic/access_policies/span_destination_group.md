# SPAN Destination Group

Description

{{ aac_doc }}

## Examples

```yaml
apic:
  access_policies:
    span:
      destination_groups:
        - name: DST_GRP1
          ip: 1.2.3.4
          source_prefix: 1.1.1.1
          flow_id: 10
          ttl: 32
          mtu: 9000
          version: 1
          enforce_version: true
          tenant: MSO1
          application_profile: AP1
          endpoint_group: EPG1
        - name: DST_GRP2
          description: My_SPAN_Destination
          node_id: 101
          port: 10
```
