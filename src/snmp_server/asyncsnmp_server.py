"""
Command example:

$ snmpwalk -v3 -u usr-md5-des -l authPriv -A authkey1 -X privkey1 localhost .1.3.6
"""

from pysnmp.entity import engine, config
from pysnmp.entity.rfc3413 import cmdrsp, context
from pysnmp.carrier.asyncio.dgram import udp
from pysnmp.debug import set_logger, Debug
from openai import OpenAI

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

    # if options["debug"]:
    #     set_logger(Debug('all'))

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

   # Load SNMP MIBs from JSON file or use default values
    file = os.path.join(f"/configs/{options['device_type']}", "snmp.json")
    if options['device_version']:
        file = os.path.join(f"/configs/{options['device_type']}/{options['device_version']}", "snmp.json")
    try:
        if os.path.isfile(file):
            with open(file, "r") as f:
                for key, value in json.loads(f.read()).items():
                    set_mibs(mibBuilder, key, value)
        else:
            logger.warning(f"Unable to find {file}, using default MIB values")
            if options['openai_support']:
                snmp_dict = get_ai_snmp_json(options['device_type'], options['device_version'], options['openai_apikey'])
                for key, value in snmp_dict.items():
                    set_mibs(mibBuilder, key, value)
    except Exception as e:
        logger.error("Something went wrong loading SNMP info")
        logger.exception(e)


    # Register SNMP command responders
    cmdrsp.GetCommandResponder(snmpEngine, snmpContext)
    cmdrsp.SetCommandResponder(snmpEngine, snmpContext)
    cmdrsp.NextCommandResponder(snmpEngine, snmpContext)
    cmdrsp.BulkCommandResponder(snmpEngine, snmpContext)

    logger.info("Started SNMP server successfully")

def get_ai_snmp_json(device_type, device_version, openai_apikey):
    logger.info("get_ai_snmp_json called")

    prompt = """
    ### Example snmp json file
    {
        "SNMPv2-MIB": [
            {
                "name": "sysName",
                "type": "string",
                "value": "arista_eos.some.net"
            },
            {
                "name": "sysDescr",
                "type": "string",
                "value": "Arista Networks EOS version 4.21.1.1F running on an Arista Networks vEOS"
            },
            {
                "name": "sysObjectID",
                "type": "id",
                "oid": "1.3.6.1.4.1.30065.1.2759"
            }
        ]
    }
    ###
    """ + f"""
    ### Device type
    {device_type}
    ###


    ### Device version
    {device_version}
    ###

    Please generate a snmp json content based on above information without any explanation and markdown format.
    """
    model = "gpt-4o"

    openai_api_key = openai_apikey

    openai_client = OpenAI(
        api_key=openai_api_key,
    )

    chat_completion = openai_client.chat.completions.create(
        messages=[
                {"role": "system", "content": "You are a AI SNMP assitant that generate a snmp.json content"},
                {"role": "user", "content": prompt}
        ],
        model=model,
    )
    message_content = chat_completion.choices[0].message.content
    message_content = message_content.replace("```", "")
    logger.info(f"get_ai_output output {message_content}")
    snmp_dict = json.loads(message_content)

    return snmp_dict

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
        return None, config.USM_AUTH_NONE
    if protocol == "md5":
        return key, config.USM_AUTH_HMAC96_MD5
    if protocol == "sha":
        return key, config.USM_AUTH_HMAC96_SHA
    if protocol == "sha224":
        return key, config.USM_AUTH_HMAC128_SHA224
    if protocol == "sha256":
        return key, config.USM_AUTH_HMAC192_SHA256
    if protocol == "sha384":
        return key, config.USM_AUTH_HMAC256_SHA384
    if protocol == "sha512":
        return key, config.USM_AUTH_HMAC384_SHA512

    logger.warning(f"Unknown Auth type `{protocol}`, using none instead")
    return None, config.USM_AUTH_NONE

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
        return None, config.USM_AUTH_NONE
    if not authKey:
        logger.warning("Auth type was none, setting Priv type to none too")
        return None, config.USM_AUTH_NONE
    if protocol == "des":
        return key, config.USM_PRIV_CBC56_DES
    if protocol == "3des":
        return key, config.USM_PRIV_CBC168_3DES
    if protocol == "aes128":
        return key, config.USM_PRIV_CFB128_AES
    if protocol == "aes192":
        return key, config.USM_PRIV_CFB192_AES
    if protocol == "aes256":
        return key, config.USM_PRIV_CFB256_AES
    if protocol == "aesblumenthal192":
        return key, config.USM_PRIV_CFB192_AES_BLUMENTHAL
    if protocol == "aesblumenthal256":
        return key, config.USM_PRIV_CFB256_AES_BLUMENTHAL

    logger.warning(f"Unknown Priv type `{protocol}`, using none instead")
    return None, config.usmNoPrivProtocol
