# TACACS Provider

Description

{{ aac_doc }}

## Examples

```yaml
apic:
  fabric_policies:
    aaa:
      tacacs_providers:
        - hostname_ip: 1.1.1.1
          description: descr
          port: 4949
          protocol: chap
          key: '123'
          timeout: 2
          retries: 2
          mgmt_epg: oob
          monitoring: true
          monitoring_username: user1
          monitoring_password: pass1
```
