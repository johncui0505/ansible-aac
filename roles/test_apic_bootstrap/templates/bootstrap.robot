*** Settings ***
Documentation   Verify Bootstrap Config
Suite Setup     Login APIC
Default Tags    apic   bootstrap   config
Resource        ./apic_common.resource

*** Test Cases ***
Verify Ansible User
    ${r}=   GET On Session   apic   /api/mo/uni/userext/user-{{ apic_username }}.json   params=rsp-subtree=full
    Should Be Equal Value Json String   ${r.json()}   $..aaaUser.attributes.name   {{ apic_username }}
    Should Be Equal Value Json String   ${r.json()}   $..aaaUser.attributes.expiration   never
    ${domain}=   Set Variable   $..aaaUser.children[?(@.aaaUserDomain.attributes.name=='all')]
    Should Be Equal Value Json String   ${r.json()}   ${domain}..aaaUserDomain.attributes.name   all
    ${role}=   Set Variable   $..aaaUserDomain.children[?(@.aaaUserRole.attributes.name=='admin')]
    Should Be Equal Value Json String   ${r.json()}   ${role}..aaaUserRole.attributes.name   admin
    Should Be Equal Value Json String   ${r.json()}   ${role}..aaaUserRole.attributes.privType   writePriv
{% if apic_password is not defined %}
    Should Be Equal Value Json String   ${r.json()}   $..aaaUserCert.attributes.name   {{ apic_username }}
{% endif %}

{% if apic_test_username is defined %}
Verify Test User
    ${r}=   GET On Session   apic   /api/mo/uni/userext/user-{{ apic_test_username }}.json   params=rsp-subtree=full
    Should Be Equal Value Json String   ${r.json()}   $..aaaUser.attributes.name   {{ apic_test_username }}
    Should Be Equal Value Json String   ${r.json()}   $..aaaUser.attributes.expiration   never
    ${domain}=   Set Variable   $..aaaUser.children[?(@.aaaUserDomain.attributes.name=='all')]
    Should Be Equal Value Json String   ${r.json()}   ${domain}..aaaUserDomain.attributes.name   all
    ${role}=   Set Variable   $..aaaUserDomain.children[?(@.aaaUserRole.attributes.name=='admin')]
    Should Be Equal Value Json String   ${r.json()}   ${role}..aaaUserRole.attributes.name   admin
    Should Be Equal Value Json String   ${r.json()}   ${role}..aaaUserRole.attributes.privType   readPriv
{% endif %}

{% if apic_mso_username is defined %}
Verify MSO User
    ${r}=   GET On Session   apic   /api/mo/uni/userext/user-{{ apic_mso_username }}.json   params=rsp-subtree=full
    Should Be Equal Value Json String   ${r.json()}   $..aaaUser.attributes.name   {{ apic_mso_username }}
    Should Be Equal Value Json String   ${r.json()}   $..aaaUser.attributes.expiration   never
    ${domain}=   Set Variable   $..aaaUser.children[?(@.aaaUserDomain.attributes.name=='all')]
    Should Be Equal Value Json String   ${r.json()}   ${domain}..aaaUserDomain.attributes.name   all
    ${role}=   Set Variable   $..aaaUserDomain.children[?(@.aaaUserRole.attributes.name=='admin')]
    Should Be Equal Value Json String   ${r.json()}   ${role}..aaaUserRole.attributes.name   admin
    Should Be Equal Value Json String   ${r.json()}   ${role}..aaaUserRole.attributes.privType   writePriv
{% endif %}

{% if apic.bootstrap.config_passphrase is defined %}
Verify Encryption Passphrase
    ${r}=   GET On Session   apic   /api/node/mo/uni/exportcryptkey.json
    Should Be Equal Value Json String   ${r.json()}   $..pkiExportEncryptionKey.attributes.strongEncryptionEnabled   yes
{% endif %}

{% for object in apic.bootstrap.objects_to_delete | default([]) %}
Verify Deletion default object {{ object.name }}
    ${r}=   GET On Session   apic   {{ object.dn }}
    Should Be Equal Value Json String   ${r.json()}   $.totalCount   0

{% endfor %}