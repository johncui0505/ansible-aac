# Management Access Policy

Description

{{ aac_doc }}

## Examples

```yaml
apic:
  fabric_policies:
    pod_policies:
      management_access_policies:
        - name: MGMT1
          telnet:
            admin_state: true
          ssh:
            port: 22
            hmac_sha1: false
            chacha: false
          https:
            tlsv1: true
          http:
            admin_state: trues
            port: 8080
```
