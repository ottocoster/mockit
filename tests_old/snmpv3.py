from pysnmp.hlapi import *
from pysnmp.entity import config



authData = UsmUserData('usr-sha-none', authKey='somekey1', 
                authProtocol=config.usmHMACSHAAuthProtocol)
g = nextCmd(SnmpEngine(),
    authData,
    UdpTransportTarget(("localhost", 161)),
    ContextData(),
    ObjectType(ObjectIdentity('SNMPv2-MIB', 'system')),
    ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysName')),
    ObjectType(ObjectIdentity('IF-MIB', 'ifDescr')),
    ObjectType(ObjectIdentity('IF-MIB', 'ifType')),
    ObjectType(ObjectIdentity('IF-MIB', 'ifMtu')),
    ObjectType(ObjectIdentity('IF-MIB', 'ifSpeed')),
    ObjectType(ObjectIdentity('IF-MIB', 'ifPhysAddress')),
    lookupMib=True,
    lexicographicMode = False,
)
succes = False
for errorIndication, errorStatus, errorIndex, varBinds in g:
    if errorIndication:
        print(f"{errorIndication}")
    elif errorStatus:
        print(f"{errorStatus.prettyPrint()} at {errorIndex and varBinds[int(errorIndex) - 1] or '?'}")
    else:           
        for x in varBinds:
            if not isinstance(x[1], EndOfMibView):
                print("----")
                print(x[0].prettyPrint() + " - " + x[0].getOid().prettyPrint())
                if  isinstance(x[1], ObjectIdentity):
                    print(x[1].prettyPrint() + " : " + x[1].getOid().prettyPrint())
                else:
                    print(x[1].prettyPrint())