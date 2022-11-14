*** Settings ***
Documentation   Verify Bootstrap
Suite Setup     Login MSO
Default Tags    mso   config   bootstrap
Resource        ./mso_common.resource

*** Test Cases ***
Get Users
    ${r}=   GET On Session   mso   /api/v1/users
    Set Suite Variable   ${r}

{% if mso_username != "admin" %}

Verify Ansible User {{ mso_username }}
    ${user}=   Set Variable   $..users[?(@.username=='{{ mso_username }}')]
    Should Be Equal Value Json String   ${r.json()}   ${user}.username   {{ mso_username }}
    Should Be Equal Value Json String   ${r.json()}   ${user}.firstName   {{ defaults.mso.bootstrap.ansible_user_first_name }}
    Should Be Equal Value Json String   ${r.json()}   ${user}.lastName   {{ defaults.mso.bootstrap.ansible_user_last_name }}
    Should Be Equal Value Json String   ${r.json()}   ${user}.emailAddress   {{ defaults.mso.bootstrap.ansible_user_email }}
    Should Be Equal Value Json String   ${r.json()}   ${user}.accountStatus   {{ defaults.mso.users.status }}

{% endif %}

{% if mso_test_username is defined and mso_test_username != "admin" %}
Verify Test User {{ mso_test_username }}
    ${user}=   Set Variable   $..users[?(@.username=='{{ mso_test_username }}')]
    Should Be Equal Value Json String   ${r.json()}   ${user}.username   {{ mso_test_username }}
    Should Be Equal Value Json String   ${r.json()}   ${user}.firstName   {{ defaults.mso.bootstrap.test_user_first_name }}
    Should Be Equal Value Json String   ${r.json()}   ${user}.lastName   {{ defaults.mso.bootstrap.test_user_last_name }}
    Should Be Equal Value Json String   ${r.json()}   ${user}.emailAddress   {{ defaults.mso.bootstrap.test_user_email }}
    Should Be Equal Value Json String   ${r.json()}   ${user}.accountStatus   {{ defaults.mso.users.status }}
{% endif %}
