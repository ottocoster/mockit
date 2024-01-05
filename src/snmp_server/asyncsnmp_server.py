"""
Command example:

| $ snmpwalk -v3 -u usr-md5-des -l authPriv -A authkey1 -X privkey1 localhost .1.3.6

"""#

from pysnmp.entity import engine, config
from pysnmp.entity.rfc3413 import cmdrsp, context
from pysnmp.carrier.asyncio.dgram import udp
from pysnmp.debug import setLogger, Debug
import asyncio
import logging
import os
import json

logger = logging.getLogger("snmp")

async def start_server(options):
    if not options["snmpv2_enabled"] and not options["snmpv3_enabled"]:
        raise Exception("snmpv2 and snmpv3 can't both be disabled")

    if options["debug"]:
        setLogger(Debug('all'))

    
    logger.info("Starting snmp server")
    logger.debug(f"Using snmp options: {options}")
    snmpEngine = engine.SnmpEngine()

    config.addTransport(
        snmpEngine,
        udp.domainName,
        udp.UdpTransport().openServerMode(('0.0.0.0', 161))
    )

    if options["snmpv2_enabled"]:
        config.addV1System(snmpEngine, "my-area", options["snmpv2_name"])
        config.addVacmUser(snmpEngine, 2, "my-area", 'noAuthNoPriv', (1, 3, 6, 1, 2, 1), (1, 3, 6, 1, 2, 1))

    if options["snmpv3_enabled"]:
        (authKey, authProtocol) = get_auth(options["snmpv3_authkey"], options["snmpv3_authtype"])
        (privKey, privProtocol) = get_priv(options["snmpv3_privkey"], options["snmpv3_privtype"], authKey)

        level = 'noAuthNoPriv'
        if authKey and not privKey:
            level = 'authNoPriv'
        if authKey and privKey:
            level = 'authPriv'
        config.addV3User(
            snmpEngine, options["snmpv3_username"],
            authProtocol, authKey,
            privProtocol, privKey
        )
        config.addVacmUser(snmpEngine, 3, options["snmpv3_username"], level, (1, 3, 6, 1, 2, 1), (1, 3, 6, 1, 2, 1))

    snmpContext = context.SnmpContext(snmpEngine)
    
    mibBuilder = snmpContext.getMibInstrum().getMibBuilder()
    file = os.path.join(f"/configs/{options['device_type']}", "snmp.json")
    if options['device_version']:
        file = os.path.join(f"/configs/{options['device_type']}/{options['device_version']}", "snmp.json")
    try:
        if os.path.isfile(file):
            with open(file, "r") as f:
                for key, value in json.loads(f.read()).items():
                    set_mibs(mibBuilder, key, value)
        else:
            logger.warn(f"Unable to find {file}")
    except Exception as e:
        logger.error("Something went wrong loading snmp info")
        logger.exception(e)

    cmdrsp.GetCommandResponder(snmpEngine, snmpContext)
    cmdrsp.SetCommandResponder(snmpEngine, snmpContext)
    cmdrsp.NextCommandResponder(snmpEngine, snmpContext)
    cmdrsp.BulkCommandResponder(snmpEngine, snmpContext)

    logger.info("Started snmp server succesfully")


def set_mibs(mibBuilder, key, values):
    if key == "SNMPv2-MIB":
        (MibTable, MibScalarInstance) = mibBuilder.importSymbols('SNMPv2-SMI', 'MibTable', 'MibScalarInstance')
        for x in values:
            tupple = mibBuilder.importSymbols('SNMPv2-MIB', (x["name"]))
            mib = tupple[0]
            if x["type"] == "string":
                __mib = MibScalarInstance(mib.name, (0,), mib.syntax.clone(x["value"]))
                mibBuilder.exportSymbols("__MY_MIB", **{x["name"]: __mib})
            if x["type"] == "id":
                __mib = MibScalarInstance(mib.name, (0,), mib.syntax.clone(x["oid"]))
                mibBuilder.exportSymbols("__MY_MIB", **{x["name"]: __mib})

def get_auth(key, protocol):
    protocol = protocol.lower()
    if protocol == "none":    
        return (None, config.usmNoAuthProtocol)
    if protocol == "md5":     
        return (key, config.usmHMACMD5AuthProtocol)
    if protocol == "sha":     
        return (key, config.usmHMACSHAAuthProtocol)
    if protocol == "sha224":  
        return (key, config.usmHMAC128SHA224AuthProtocol)
    if protocol == "sha256":  
        return (key, config.usmHMAC192SHA256AuthProtocol)
    if protocol == "sha384":  
        return (key, config.usmHMAC256SHA384AuthProtocol)
    if protocol == "sha512":  
        return (key, config.usmHMAC384SHA512AuthProtocol)

    logger.warn(f"Unknown Auth type `{protocol}`, using none instead")
    return (None, config.usmNoAuthProtocol)

def get_priv(key, protocol, authKey):
    protocol = protocol.lower()
    if protocol == "none":
        return (None, config.usmNoPrivProtocol)
    if not authKey:
        logger.warn(f"Auth type was none, setting Priv type to none too")
        return (None, config.usmNoPrivProtocol)
    if protocol == "des":
        return (key, config.usmDESPrivProtocol)
    if protocol == "3des":
        return (key, config.usm3DESEDEPrivProtocol)
    if protocol == "aes128":
        return (key, config.usmAesCfb128Protocol)
    if protocol == "aes192":
        return (key, config.usmAesCfb192Protocol)
    if protocol == "aes256":
        return (key, config.usmAesCfb256Protocol)
    if protocol == "aesblumenthal192":
        return (key, config.usmAesBlumenthalCfb192Protocol)
    if protocol == "aesblumenthal256":
        return (key, config.usmAesBlumenthalCfb256Protocol)

    logger.warn(f"Unknown Priv type `{protocol}`, using none instead")
    return (None, config.usmNoPrivProtocol)
