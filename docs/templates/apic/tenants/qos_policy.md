# QoS Policy

Description

{{ aac_doc }}
## Examples

```yaml
apic:
  tenants:
    - name: ABC
      policies:
        qos:
          - name: TEST_QOS_POLICY
            dscp_priority_maps:
              - dscp_from: AF11
                dscp_to: AF12
                cos_target: 1
                dscp_target: AF11
              - priority: level2
                dscp_from: AF21
                dscp_to: AF21
            dot1p_classifiers:
              - dot1p_from: 4
                dot1p_to: 5
              - priority: level3
                dot1p_from: 1
                dot1p_to: 2
                dscp_target: CS2
                cos_target: 3
```
