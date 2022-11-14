# SPAN Source Group

Description

{{ aac_doc }}
## Examples

```yaml
apic:
  access_policies:
    span:
      source_groups:
        - name: SRC_GRP1
          filter_group: FLT_GRP1
          destination:
            name: DST_GRP1
          sources:
            - name: SRC1
              direction: both
              access_paths:
                - node_id: 101
                  port: 1
                - node_id: 101
                  port: 10
            - name: SRC2
              direction: both
              access_paths:
                - channel: VPC1
                  node_id: 101
                  node2_id: 102
```
