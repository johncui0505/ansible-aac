# SPAN Filter Group

Description

{{ aac_doc }}
## Examples

```yaml
apic:
  access_policies:
    span:
      filter_groups:
        - name: FLT_GRP1
          description: My SPAN Filter Group
          entries:
            - name: ENTRY1
              destination_ip: 10.10.10.10
              destination_port_from: 80
              destination_port_to: 90
              source_port_from: 100
              source_port_to: 102
              source_ip: 20.20.20.20
              ip_protocol: tcp
```
