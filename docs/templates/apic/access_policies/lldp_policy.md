# LLDP Interface Policy

Description

{{ aac_doc }}

## Examples

```yaml
apic:
  access_policies:
    interface_policies:
      lldp_policies:
        - name: LLDP-ENABLED
          admin_rx_state: true
          admin_tx_state: true
```
