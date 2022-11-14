# VSPAN Destination Group

Description

{{ aac_doc }}
## Examples

```yaml
apic:
  access_policies:
    vspan:
      destination_groups:
        - name: DST_GRP1
          description: My VSPAN Destination Groups
          destinations:
            - name: DST1
              description: My Destination 1
              tenant: MSO1
              application_profile: AP1
              endpoint_group: EPG1
              endpoint: 00:50:56:96:6B:4F
            - name: DST2
              ip: 1.2.3.4
              mtu: 9000
              ttl: 10
              flow_id: 10
              dscp: CS4
```
