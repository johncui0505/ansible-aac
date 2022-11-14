# OSPF Interface Policy

Description

{{ aac_doc }}

## Examples

```yaml
apic:
  tenants:
    - name: ABC
      policies:
        ospf_interface_policies:
          - name: OIP1
            description: My Desc
            cost: 40
            passive_interface: true
            mtu_ignore: true
            advertise_subnet: true
            bfd: true
            hello_interval: 30
            dead_interval: 180
            network_type: p2p
            priority: 2
            lsa_retransmit_interval: 6
            lsa_transmit_delay: 2
```
