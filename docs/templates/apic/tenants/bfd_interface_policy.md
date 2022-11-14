# BFD Interface Policy

Description

{{ aac_doc }}

## Examples

```yaml
apic:
  tenants:
    - name: ABC
      policies:
        bfd_interface_policies:
          - name: BFD1
            description: descr
            subinterface_optimization: true
            detection_multiplier: 5
            echo_admin_state: false
            echo_rx_interval: 100
            min_rx_interval: 100
            min_tx_interval: 100
```
