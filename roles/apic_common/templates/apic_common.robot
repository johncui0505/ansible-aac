*** Settings ***
Library   RequestsLibrary
Library   JSONLibrary
Library   Collections

*** Variables ***
${login_json}   {"aaaUser" : {"attributes" : {"name" : "{{ apic_test_username | default(apic_username) }}", "pwd" : "{{ apic_test_password | default(apic_password) }}"}}}

*** Keywords ***
Get APIC Token
    Create Session   login   https://{{ apic_host }}
    ${response}=   POST On Session   login   /api/aaaLogin.json   data=${login_json}
    ${r_token}=   Get Value From Json   ${response.json()}   $..token
    Set Suite Variable   ${apic_token}   ${r_token[0]}

Login APIC
    ${apic_token}=   Get Variable Value   ${token}
    Run Keyword If   '${apic_token}' == 'None'   Get APIC Token
    Create Session   apic   https://{{ apic_host }}   headers={"Cookie": "APIC-cookie=${apic_token}"}

Should Be Equal Value Json String
    [Arguments]    ${json}    ${json_path}   ${value}=${EMPTY}
    ${r_value}=   Get Value From Json   ${json}   ${json_path}
    Run Keyword If   "${value}" != "${EMPTY}"   Should Be Equal As Strings   ${r_value}[0]   ${value}

Should Be Equal Value Json List
    [Arguments]    ${json}    ${json_path}   ${value}=${None}
    ${r_value}=   Get Value From Json   ${json}   ${json_path}
    Run Keyword If   "${value}" != "${None}"   Lists Should Be Equal   ${r_value}   ${value}   ignore_order=True