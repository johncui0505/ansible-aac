*** Settings ***
Documentation   Verify Physical Domain Health
Suite Setup     Login APIC
Default Tags    apic   day1   health   access_policies   non-critical
Resource        ../../apic_common.resource

*** Test Cases ***
{% for domain in apic.access_policies.physical_domains | default([]) %}
{% set domain_name = domain.name ~ defaults.apic.access_policies.physical_domains.name_suffix %}

Verify Physical Domain {{ domain_name }} Faults
    ${r}=   GET On Session   apic   /api/mo/uni/phys-{{ domain_name }}/fltCnts.json
    ${critical}=   Get Value From Json   ${r.json()}   $..faultCounts.attributes.crit
    ${major}=   Get Value From Json   ${r.json()}   $..faultCounts.attributes.maj
    ${minor}=   Get Value From Json   ${r.json()}   $..faultCounts.attributes.minor
    Run Keyword If   ${critical}[0] > 0   Run Keyword And Continue On Failure
    ...   Fail  "{{ domain_name }} has ${critical}[0] critical faults"
    Run Keyword If   ${major}[0] > 0   Run Keyword And Continue On Failure
    ...   Fail  "{{ domain_name }} has ${major}[0] major faults"
    Run Keyword If   ${minor}[0] > 0   Run Keyword And Continue On Failure
    ...   Fail  "{{ domain_name }} has ${minor}[0] minor faults"

{% endfor %}