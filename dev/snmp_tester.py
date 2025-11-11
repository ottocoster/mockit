from pysnmp.hlapi.asyncio import *

from pathlib import Path

import asyncio

mib_folders = set('../mibs')
mibs_root = Path('../mibs')
for p in mibs_root.rglob("*.py"):
    mib_folders.add(str(p.parent))

async def walk_snmpv2(host, community_string, *oid):
    result = walk_cmd(
        SnmpEngine(),
        CommunityData(community_string, mpModel=1), 
        await UdpTransportTarget.create((host, 161)),
        ContextData(),
        ObjectType(ObjectIdentity(*oid).add_mib_source(*mib_folders))
    )
    async for errorIndication, errorStatus, errorIndex, varBinds in result:
        if errorIndication:
            print(f"{host} walk_snmpv2 gave {errorIndication}")
        elif errorStatus:
            print(f"{host} get_chasis_id gave error status {errorStatus.prettyPrint()} at {errorIndex and varBinds[int(errorIndex) - 1] or '?'}")
        else:
            for oid, value in varBinds:
                print(f"{oid.prettyPrint()} - {value}")

asyncio.run(walk_snmpv2("127.0.0.1", "public", "AIRESPACE-WIRELESS-MIB", "bsnAPEthernetMacAddress"))

