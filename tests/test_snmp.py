import pytest
from pysnmp.hlapi import *

def check_snmp_walk(snmp_target, community='public', snmp_port=161, oid='1.3.6.1.2.1'):
    try:
        result = []
        for (error_indication,
             error_status,
             error_index,
             var_binds) in nextCmd(SnmpEngine(),
                                   CommunityData(community, mpModel=1),  # Use mpModel=1 for SNMPv2c
                                   UdpTransportTarget((snmp_target, snmp_port)),
                                   ContextData(),
                                   ObjectType(ObjectIdentity(oid)),
                                   lexicographicMode=False):  # Stop at end of subtree

            if error_indication:
                pytest.fail(f"Connection failed: {error_indication}")
            elif error_status:
                pytest.fail(f"Error from server: {error_status.prettyPrint()} at {error_index and var_binds[int(error_index) - 1][0] or '?'}")
            else:
                for var_bind in var_binds:
                    result.append(var_bind)

        assert result, "No data returned from SNMP walk"
        return result

    except Exception as e:
        pytest.fail(f"An error occurred: {e}")

def test_snmp_walk():
    # Replace with your SNMP server details
    snmp_target = '192.168.233.128'  # Update to your server's IP
    community = 'public'  # Update to the correct community string if needed

    response = check_snmp_walk(snmp_target, community)
    assert response is not None, "Failed to retrieve a valid response from SNMP server"
    assert len(response) > 0, "SNMP walk returned no results"
