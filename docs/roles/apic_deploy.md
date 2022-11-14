# apic_deploy

This role adds/modifies/deletes APIC objects.

## Sample Playbook

```yaml
---
- name: Deploy APIC
  hosts: apic
  gather_facts: no
 
  tasks:
    - name: APIC Deploy
      ansible.builtin.include_role:
        name: cisco.aac.apic_deploy
```

## Classes

### Fabric Policies

Class | Example
---|---
Date and Time Format | [link](../model/apic/fabric_policies/date_time_format.md)
APIC Connectivity Preference | [link](../model/apic/fabric_policies/apic_connectivity_pref.md)
GUI and CLI Banner | [link](../model/apic/fabric_policies/banner.md)
EP Loop Protection | [link](../model/apic/fabric_policies/ep_loop_protection.md)
Rogue EP Control | [link](../model/apic/fabric_policies/rogue_ep_control.md)
IP Aging | [link](../model/apic/fabric_policies/ip_aging.md)
Fabric Wide Settings | [link](../model/apic/fabric_policies/fabric_wide_settings.md)
Port Tracking | [link](../model/apic/fabric_policies/port_tracking.md)
PTP | [link](../model/apic/fabric_policies/ptp.md)
Fabric ISIS Redistribute Metric | [link](../model/apic/fabric_policies/isis_policy.md)
Fabric ISIS BFD | [link](../model/apic/fabric_policies/fabric_isis_bfd.md)
DNS Profile Policy | [link](../model/apic/fabric_policies/dns_policy.md)
Error Disabled Recovery Policy | [link](../model/apic/fabric_policies/err_disabled_recovery.md)
COOP Policy Group | [link](../model/apic/fabric_policies/coop_policy.md)
Infra DSCP Translation Policy | [link](../model/apic/fabric_policies/infra_dscp_translation_policy.md)
AAA Settings | [link](../model/apic/fabric_policies/aaa.md)
TACACS Provider | [link](../model/apic/fabric_policies/tacacs.md)
User | [link](../model/apic/fabric_policies/user.md)
Login Domain | [link](../model/apic/fabric_policies/login_domain.md)
Remote Location | [link](../model/apic/fabric_policies/remote_location.md)
Scheduler | [link](../model/apic/fabric_policies/scheduler.md)
Config Export | [link](../model/apic/fabric_policies/config_export.md)
SNMP Trap | [link](../model/apic/fabric_policies/snmp_trap.md)
Syslog | [link](../model/apic/fabric_policies/syslog.md)
Monitoring Policy | [link](../model/apic/fabric_policies/monitoring_policy.md)
CA Certificate | [link](../model/apic/fabric_policies/ca_cert.md)
Keyring | [link](../model/apic/fabric_policies/keyring.md)
Date and Time Policy | [link](../model/apic/fabric_policies/date_time_policy.md)
BGP Policy | [link](../model/apic/fabric_policies/bgp_policy.md)
Fabric Leaf Switch Profile | [link](../model/apic/fabric_policies/fp_leaf_switch_profile.md)
Fabric Spine Switch Profile | [link](../model/apic/fabric_policies/fp_spine_switch_profile.md)
Fabric Leaf Interface Profile | [link](../model/apic/fabric_policies/fp_leaf_interface_profile.md)
Fabric Spine Interface Profile | [link](../model/apic/fabric_policies/fp_spine_interface_profile.md)
Pod Profile | [link](../model/apic/fabric_policies/pod_profile.md)
SNMP Pod Policy | [link](../model/apic/fabric_policies/snmp_policy.md)
PSU Switch Policy | [link](../model/apic/fabric_policies/psu_policy.md)
Node Control Switch Policy | [link](../model/apic/fabric_policies/node_control_policy.md)
Pod Policy Group | [link](../model/apic/fabric_policies/pod_policy_group.md)
Fabric Leaf Switch Policy Group | [link](../model/apic/fabric_policies/fp_leaf_switch_policy_group.md)
Fabric Spine Switch Policy Group | [link](../model/apic/fabric_policies/fp_spine_switch_policy_group.md)
External Connectivity Policy | [link](../model/apic/fabric_policies/ext_conn_policy.md)
VMware VMM Domain | [link](../model/apic/fabric_policies/vmw_vmm_domain.md)
Geolocation Policy | [link](../model/apic/fabric_policies/geolocation.md)

### Access Policies

Class | Example
---|---
MCP Global Instance | [link](../model/apic/access_policies/mcp.md)
QoS Class | [link](../model/apic/access_policies/qos.md)
Access Leaf Switch Profile | [link](../model/apic/access_policies/ap_leaf_switch_profile.md)
Access Spine Switch Profile | [link](../model/apic/access_policies/ap_spine_switch_profile.md)
Access Leaf Interface Profile | [link](../model/apic/access_policies/ap_leaf_interface_profile.md)
Access FEX Interface Profile | [link](../model/apic/access_policies/ap_fex_interface_profile.md)
Access Spine Interface Profile | [link](../model/apic/access_policies/ap_spine_interface_profile.md)
Vlan Pool | [link](../model/apic/access_policies/vlan_pool.md)
Physical Domain | [link](../model/apic/access_policies/physical_domain.md)
Routed Domain | [link](../model/apic/access_policies/routed_domain.md)
AAEP | [link](../model/apic/access_policies/aaep.md)
CDP Interface Policy | [link](../model/apic/access_policies/cdp_policy.md)
LLDP Interface Policy | [link](../model/apic/access_policies/lldp_policy.md)
Link Level Interface Policy | [link](../model/apic/access_policies/link_level_policy.md)
Port Channel Interface Policy | [link](../model/apic/access_policies/port_channel_policy.md)
Port Channel Member Interface Policy | [link](../model/apic/access_policies/port_channel_member_policy.md)
Spanning Tree Interface Policy | [link](../model/apic/access_policies/spanning_tree_policy.md)
MCP Interface Policy | [link](../model/apic/access_policies/mcp_policy.md)
L2 Interface Policy | [link](../model/apic/access_policies/l2_policy.md)
Storm Control Interface Policy | [link](../model/apic/access_policies/storm_control_policy.md)
MST Switch Policy | [link](../model/apic/access_policies/mst_policy.md)
VPC Switch Policy | [link](../model/apic/access_policies/vpc_policy.md)
Forwarding Scale Switch Policy | [link](../model/apic/access_policies/forwarding_scale_policy.md)
Access Leaf Switch Policy Group | [link](../model/apic/access_policies/ap_leaf_switch_policy_group.md)
Access Spine Interface Policy Group | [link](../model/apic/access_policies/ap_spine_interface_policy_group.md)
Access Leaf Interface Policy Group | [link](../model/apic/access_policies/ap_leaf_interface_policy_group.md)

### Pod Policies

Class | Example
---|---
Pod Setup | [link](../model/apic/pod_policies/pod_setup.md)

### Node Policies

Class | Example
---|---
Node Registration | [link](../model/apic/node_policies/node_registration.md)
OOB Node Address | [link](../model/apic/node_policies/oob_node_address.md)
INB Node Address | [link](../model/apic/node_policies/inb_node_address.md)
Maintenance Group | [link](../model/apic/node_policies/maintenance_group.md)
Firmware Group | [link](../model/apic/node_policies/firmware_group.md)
VPC Group | [link](../model/apic/node_policies/vpc_group.md)

### Interface Policies

Class | Example
---|---
Access Spine Interface Selector | [link](../model/apic/interface_policies/spine_interface_selector.md)
Access Leaf Interface Selector | [link](../model/apic/interface_policies/leaf_interface_selector.md)
Access FEX Interface Selector | [link](../model/apic/interface_policies/fex_interface_selector.md)

### Tenants

Class | Example
---|---
Tenant | [link](../model/apic/tenants/tenant.md)
VRF | [link](../model/apic/tenants/vrf.md)
Bridge | [link](../model/apic/tenants/bridge_domain.md)
L3out | [link](../model/apic/tenants/l3out.md)
External Endpoint Group | [link](../model/apic/tenants/external_endpoint_group.md)
Application Profile | [link](../model/apic/tenants/application_profile.md)
Endpoint Group | [link](../model/apic/tenants/endpoint_group.md)
Contract | [link](../model/apic/tenants/contract.md)
Imported Contract | [link](../model/apic/tenants/imported_contract.md)
Filter | [link](../model/apic/tenants/filter.md)
OSPF Interface Policy | [link](../model/apic/tenants/ospf_interface_policy.md)
BFD Interface Policy | [link](../model/apic/tenants/bfd_interface_policy.md)
DHCP Relay Policy | [link](../model/apic/tenants/dhcp_relay_policy.md)
DHCP Option Policy | [link](../model/apic/tenants/dhcp_option_policy.md)
Match Rule | [link](../model/apic/tenants/match_rule.md)
Set Rule | [link](../model/apic/tenants/set_rule.md)
BGP Timer Policy | [link](../model/apic/tenants/bgp_timer_policy.md)
Redirect Policy | [link](../model/apic/tenants/redirect_policy.md)
L4L7 Device | [link](../model/apic/tenants/l4l7_device.md)
Service Graph Template | [link](../model/apic/tenants/service_graph_template.md)
Device Selection Policy | [link](../model/apic/tenants/device_selection_policy.md)
INB Endpoint Group | [link](../model/apic/tenants/inb_endpoint_group.md)
OOB Endpoint Group | [link](../model/apic/tenants/oob_endpoint_group.md)
OOB External Management Instance | [link](../model/apic/tenants/oob_ext_mgmt_instance.md)
OOB Contract | [link](../model/apic/tenants/oob_contract.md)
