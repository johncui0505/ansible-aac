# Syslog

Description

{{ aac_doc }}

## Examples

```yaml
apic:
  fabric_policies:
    monitoring:
      syslogs:
        - name: syslog1
          description: desc1
          admin_state: false
          format: nxos
          show_millisecond: true
          local_admin_state: false
          local_severity: emergencies
          console_admin_state: false
          console_severity: alerts
          destinations:
            - hostname_ip: 2.2.2.2
              port: 1234
              admin_state: false
              facility: local0
              severity: emergencies
              mgmt_epg: inb
            - hostname_ip: 2.2.2.3
```
