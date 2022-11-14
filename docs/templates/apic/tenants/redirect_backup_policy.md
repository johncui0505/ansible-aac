# Redirect Backup Policy

Description

{{ aac_doc }}
## Examples

```yaml
apic:
  tenants:
    - name: ABC
      services:
        redirect_backup_policies:
          - name: L4L7_REDIRECT_BACKUP12
            l3_destinations:
              - ip: 5.6.7.8
                mac: 00:00:00:11:22:33
                redirect_health_group: HEALTH_GROUP_1
          - name: L4L7_REDIRECT_BACKUP14
            l3_destinations:
              - ip: 10.6.7.8
                ip_2: 4.5.6.7
                mac: 84:53:64:09:53:00
                destination_name: BACKUP_DESTINATION_NAME
```
