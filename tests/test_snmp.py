from pysnmp.hlapi.asyncio import *

def snmp_get(snmp_target, community='public', snmp_port=161, oid='1.3.6.1.2.1.1.1.0'):
    try:
        error_indication, error_status, error_index, var_binds = next(
            getCmd(SnmpEngine(),
                   CommunityData(community, mpModel=1),  # Use mpModel=1 for SNMPv2c
                   UdpTransportTarget((snmp_target, snmp_port)),
                   ContextData(),
                   ObjectType(ObjectIdentity(oid)))
        )

        if error_indication:
            raise Exception(f"Connection failed: {error_indication}")
        elif error_status:
            raise Exception(f"Error from server: {error_status.prettyPrint()} at {error_index and var_binds[int(error_index) - 1][0] or '?'}")
        else:
            for var_bind in var_binds:
                # var_bind is a tuple (OID, value)
                print(f"{var_bind[0]} = {var_bind[1]}")
                return var_bind[1]  # Return the value part

    except Exception as e:
        raise Exception(f"An error occurred: {e}")

def test_snmp_get():
    # Replace with your SNMP server details
    snmp_target = '192.168.233.128'  # Update to your server's IP
    community = 'public'  # Update to the correct community string if needed
    oid = '1.3.6.1.2.1.1.1.0'  # OID for sysDescr.0

    response = snmp_get(snmp_target, community, oid=oid)
    assert response is not None, "Failed to retrieve a valid response from SNMP server"
    print(f"Response: {response}")

# Run the test
test_snmp_get()
