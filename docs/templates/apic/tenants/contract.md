# Contract

Description

{{ aac_doc }}

## Examples

```yaml
apic:
  tenants:
    - name: ABC
      contracts:
        - name: CON1
          alias: CON1-ALIAS
          description: My Desc
          scope: global
          qos_class: level3
          target_dscp: AF13
          subjects:
            - name: SUB1
              alias: SUB1-ALIAS
              description: My Desc
              service_graph: TEMPLATE1
              qos_class: level3
              target_dscp: AF13
              filters:
                - filter: FILTER1
                  action: permit
                  priority: default
                  log: true
                  no_stats: false
```
