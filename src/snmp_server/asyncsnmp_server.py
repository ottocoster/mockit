"""
Command example:

$ snmpwalk -v3 -u usr-md5-des -l authPriv -A authkey1 -X privkey1 localhost .1.3.6
"""

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
    """
    Start the SNMP server with the provided options.

    Args:
        options (dict): Configuration options for the server.
    """
    if not options["snmpv2_enabled"] and not options["snmpv3_enabled"]:
        raise Exception("SNMPv2 and SNMPv3 can't both be disabled")

    if options["debug"]:
        setLogger(Debug('all'))

    logger.info("Starting SNMP server")
    logger.debug(f"Using SNMP options: {options}")
    snmpEngine = engine.SnmpEngine()

    # Add transport endpoint
    config.addTransport(
        snmpEngine,
        udp.domainName,
        udp.UdpTransport().openServerMode(('0.0.0.0', 161))
    )

    # SNMPv2 configuration
    if options["snmpv2_enabled"]:
        config.addV1System(snmpEngine, "my-area", options["snmpv2_name"])
        config.addVacmUser(snmpEngine, 2, "my-area", 'noAuthNoPriv', (1, 3, 6, 1, 2, 1), (1, 3, 6, 1, 2, 1))

    # SNMPv3 configuration
    if options["snmpv3_enabled"]:
        authKey, authProtocol = get_auth(options["snmpv3_authkey"], options["snmpv3_authtype"])
        privKey, privProtocol = get_priv(options["snmpv3_privkey"], options["snmpv3_privtype"], authKey)

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
    
    # Load SNMP MIBs from JSON file
    file = os.path.join(f"/configs/{options['device_type']}", "snmp.json")
    if options['device_version']:
        file = os.path.join(f"/configs/{options['device_type']}/{options['device_version']}", "snmp.json")
    try:
        if os.path.isfile(file):
            with open(file, "r") as f:
                for key, value in json.loads(f.read()).items():
                    set_mibs(mibBuilder, key, value)
        else:
            logger.warning(f"Unable to find {file}")
    except Exception as e:
        logger.error("Something went wrong loading SNMP info")
        logger.exception(e)

    # Register SNMP command responders
    cmdrsp.GetCommandResponder(snmpEngine, snmpContext)
    cmdrsp.SetCommandResponder(snmpEngine, snmpContext)
    cmdrsp.NextCommandResponder(snmpEngine, snmpContext)
    cmdrsp.BulkCommandResponder(snmpEngine, snmpContext)

    logger.info("Started SNMP server successfully")

def set_mibs(mibBuilder, key, values):
    """
    Set MIBs in the MIB builder.

    Args:
        mibBuilder: MIB builder instance.
        key (str): MIB key.
        values (list): List of MIB values.
    """
    if key == "SNMPv2-MIB":
        MibTable, MibScalarInstance = mibBuilder.importSymbols('SNMPv2-SMI', 'MibTable', 'MibScalarInstance')
        for x in values:
            mib_tuple = mibBuilder.importSymbols('SNMPv2-MIB', x["name"])
            mib = mib_tuple[0]
            if x["type"] == "string":
                mib_instance = MibScalarInstance(mib.name, (0,), mib.syntax.clone(x["value"]))
                mibBuilder.exportSymbols("__MY_MIB", **{x["name"]: mib_instance})
            if x["type"] == "id":
                mib_instance = MibScalarInstance(mib.name, (0,), mib.syntax.clone(x["oid"]))
                mibBuilder.exportSymbols("__MY_MIB", **{x["name"]: mib_instance})

def get_auth(key, protocol):
    """
    Get authentication protocol and key.

    Args:
        key (str): Authentication key.
        protocol (str): Authentication protocol.

    Returns:
        tuple: Authentication key and protocol.
    """
    protocol = protocol.lower()
    if protocol == "none":
        return None, config.usmNoAuthProtocol
    if protocol == "md5":
        return key, config.usmHMACMD5AuthProtocol
    if protocol == "sha":
        return key, config.usmHMACSHAAuthProtocol
    if protocol == "sha224":
        return key, config.usmHMAC128SHA224AuthProtocol
    if protocol == "sha256":
        return key, config.usmHMAC192SHA256AuthProtocol
    if protocol == "sha384":
        return key, config.usmHMAC256SHA384AuthProtocol
    if protocol == "sha512":
        return key, config.usmHMAC384SHA512AuthProtocol

    logger.warning(f"Unknown Auth type `{protocol}`, using none instead")
    return None, config.usmNoAuthProtocol

def get_priv(key, protocol, authKey):
    """
    Get privacy protocol and key.

    Args:
        key (str): Privacy key.
        protocol (str): Privacy protocol.
        authKey (str): Authentication key.

    Returns:
        tuple: Privacy key and protocol.
    """
    protocol = protocol.lower()
    if protocol == "none":
        return None, config.usmNoPrivProtocol
    if not authKey:
        logger.warning("Auth type was none, setting Priv type to none too")
        return None, config.usmNoPrivProtocol
    if protocol == "des":
        return key, config.usmDESPrivProtocol
    if protocol == "3des":
        return key, config.usm3DESEDEPrivProtocol
    if protocol == "aes128":
        return key, config.usmAesCfb128Protocol
    if protocol == "aes192":
        return key, config.usmAesCfb192Protocol
    if protocol == "aes256":
        return key, config.usmAesCfb256Protocol
    if protocol == "aesblumenthal192":
        return key, config.usmAesBlumenthalCfb192Protocol
    if protocol == "aesblumenthal256":
        return key, config.usmAesBlumenthalCfb256Protocol

    logger.warning(f"Unknown Priv type `{protocol}`, using none instead")
    return None, config.usmNoPrivProtocol
