"""
Command example:

$ snmpwalk -v3 -u usr-md5-des -l authPriv -A authkey1 -X privkey1 localhost .1.3.6
"""
import asyncio
import socket
import logging
import os
import json
import re

from pysnmp.proto.rfc1902 import OctetString, ObjectName, Integer32
from pysnmp.smi import builder, rfc1902, view
from pysnmp.entity import engine, config
from pysnmp.entity.rfc3413 import cmdrsp, context
from pysnmp.carrier.asyncio.dgram import udp
from openai import OpenAI
from pathlib import Path

from src.options import get_normalized_device_type

logger = logging.getLogger("app")
_shutdown_event = None

# AI_SNMP_PROMPT — custom system message for the snmp.json generation.
DEFAULT_SNMP_PROMPT = "You are a AI SNMP assitant that generate a snmp.json content"

# AI_SNMP_OUTPUT — custom user prompt template for the snmp.json generation.
# Supports {device_type} and {device_version} placeholders.
DEFAULT_SNMP_OUTPUT = """
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
                "value": "1.3.6.1.4.1.30065.1.2759"
            }
        ]
    }
    ###

    ### Device type
    {device_type}
    ###


    ### Device version
    {device_version}
    ###

    Please generate a snmp json content based on above information without any explanation and markdown format.
    """

def _load_mibs(mibBuilder, options):
    """
    Blocking MIB loading: scans /mibs, then loads MIB values from snmp.json
    or generates missing content through the AI (OpenAI-compatible) request.

    Pure CPU/IO work with no event-loop interaction, so it's safe to run in a
    worker thread (asyncio.to_thread).

    :param mibBuilder: pysnmp MIB builder to populate.
    :param options: Options dict for the SNMP server.
    """
    mib_folders = set()
    mibs_root = Path('/mibs')
    for p in mibs_root.rglob("*.py"):
        mib_folders.add(str(p.parent))
    for f in sorted(mib_folders):
        mibBuilder.add_mib_sources(builder.DirMibSource(f))

    # Load SNMP MIBs from JSON file or use default values
    norm = get_normalized_device_type(options['device_type'])
    file = os.path.join(f"/configs/{norm}", "snmp.json")
    if options['device_version']:
        file = os.path.join(f"/configs/{norm}/{options['device_version']}", "snmp.json")
    try:
        if os.path.isfile(file):
            with open(file, "r") as f:
                for key, value in json.loads(f.read()).items():
                    set_mibs(mibBuilder, key, value)
        else:
            logger.warning(f"Unable to find {file}, using default MIB values")
            if options['ai_support']:
                # Blocking is fine here: we're running in a worker thread.
                snmp_dict = get_ai_snmp_json(
                    norm,
                    options['device_version'],
                    options['ai_apikey'],
                    ai_url=options.get('ai_url', ''),
                    ai_model=options.get('ai_model') or 'gpt-5.5',
                    output=options.get('ai_snmp_output'),
                    prompt=options.get('ai_snmp_prompt'),
                )
                for key, value in snmp_dict.items():
                    set_mibs(mibBuilder, key, value)
    except Exception as e:
        logger.error("Something went wrong loading SNMP info")
        logger.exception(e)


async def start_server(status, options):
    """
    Start the SNMP server with the provided options.

    Args:
        options (dict): Configuration options for the server.
    """
    if not options["snmpv2_enabled"] and not options["snmpv3_enabled"]:
        raise Exception("SNMPv2 and SNMPv3 can't both be disabled")

    global _shutdown_event
    _shutdown_event = asyncio.Event()

    # if options["debug"]:
    #     set_logger(Debug('all'))

    logger.info("Starting SNMP server")
    logger.debug(f"Using SNMP options: {options}")
    snmpEngine = engine.SnmpEngine()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    sock.bind(('0.0.0.0', 161))
    sock.setblocking(False)

    # Add transport endpoint (must run on the event-loop thread: pysnmp's
    # asyncio carrier interacts with the running loop here).
    config.add_transport(
        snmpEngine,
        udp.DOMAIN_NAME,
        udp.UdpTransport().open_server_mode(
            #('0.0.0.0', 161),
            sock=sock)
    )

    # SNMPv2 configuration
    if options["snmpv2_enabled"]:
        config.add_v1_system(snmpEngine, "my-area", options["snmpv2_name"])
        config.add_vacm_user(snmpEngine, 2, "my-area", 'noAuthNoPriv', (1, 3, 6, 1), (1, 3, 6, 1))

    # SNMPv3 configuration
    if options["snmpv3_enabled"]:
        authKey, authProtocol = get_auth(options["snmpv3_authkey"], options["snmpv3_authtype"])
        privKey, privProtocol = get_priv(options["snmpv3_privkey"], options["snmpv3_privtype"], authKey)

        level = 'noAuthNoPriv'
        if authKey and not privKey:
            level = 'authNoPriv'
        if authKey and privKey:
            level = 'authPriv'

        config.add_v3_user(
            snmpEngine, options["snmpv3_username"],
            authProtocol, authKey,
            privProtocol, privKey
        )
        config.add_vacm_user(snmpEngine, 3, options["snmpv3_username"], level, (1, 3, 6, 1), (1, 3, 6, 1))

    snmpContext = context.SnmpContext(snmpEngine)
    mibBuilder = snmpContext.get_mib_instrum().get_mib_builder()
    mibBuilder.add_mib_sources(builder.DirMibSource('/mibs'))

    # Scanning /mibs and compiling the MIBs is slow, blocking work; run it
    # in a worker thread so the event loop stays responsive and other
    # services can start in parallel (avoids asyncio slow-callback warnings).
    await asyncio.to_thread(_load_mibs, mibBuilder, options)

    # Register SNMP command responders
    cmdrsp.GetCommandResponder(snmpEngine, snmpContext)
    cmdrsp.SetCommandResponder(snmpEngine, snmpContext)
    cmdrsp.NextCommandResponder(snmpEngine, snmpContext)
    cmdrsp.BulkCommandResponder(snmpEngine, snmpContext)

    await status.service_ready()
    logger.info("Started SNMP server successfully")
    await _shutdown_event.wait()


def stop_server():
    """Signal the SNMP server to stop"""
    if (loop := _shutdown_event._get_loop()) and not loop.is_closed():
        loop.call_soon_threadsafe(_shutdown_event.set)


def get_ai_snmp_json(device_type, device_version, ai_apikey,
                     ai_url: str = "",
                     ai_model: str = "gpt-5.5",
                     output: str | None = None,
                     prompt: str | None = None):
    """
    Generate the snmp.json MIB content using an OpenAI-compatible API.

    :param device_type: The (normalized) device type.
    :param device_version: Optional device version, empty string when unset.
    :param ai_apikey: API key for the AI provider.
    :param ai_url: Optional base URL of an OpenAI-compatible API
        (e.g. LM Studio `http://localhost:1234/v1`). Empty uses the default
        OpenAI endpoint.
    :param ai_model: Model name to request from the AI provider.
    :param output: Optional custom user prompt template (AI_SNMP_OUTPUT).
        Supports the {device_type} and {device_version} placeholders.
        Falls back to DEFAULT_SNMP_OUTPUT when None.
    :param prompt: Optional custom system message (AI_SNMP_PROMPT).
        Falls back to DEFAULT_SNMP_PROMPT when None.
    """
    logger.info("get_ai_snmp_json called")

    output_template = output if output else DEFAULT_SNMP_OUTPUT
    # Placeholder substitution via str.replace (instead of str.format) so that
    # literal braces in the prompt (e.g. the example JSON) stay untouched.
    prompt_template_text = (output_template
                            .replace("{device_type}", str(device_type))
                            .replace("{device_version}", str(device_version or "")))

    model = ai_model

    client_kwargs = {"api_key": ai_apikey or "lm-studio"}
    if ai_url:
        client_kwargs["base_url"] = ai_url
    ai_client = OpenAI(**client_kwargs)

    chat_completion = ai_client.chat.completions.create(
        messages=[
                {"role": "system", "content": prompt if prompt else DEFAULT_SNMP_PROMPT},
                {"role": "user", "content": prompt_template_text}
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
    MibTable, MibScalarInstance = mibBuilder.importSymbols('SNMPv2-SMI', 'MibTable', 'MibScalarInstance')
    try:
        mibBuilder.load_modules(key)
        for x in values:
            type = x['type']
            value = x["value"]
            name = x["name"]
            
            mib_tuple = mibBuilder.import_symbols(key, name)
            mib = mib_tuple[0]
            suffix = parse_suffix(x.get("suffix"))
            if type == "hex":
                mib_value = mib.syntax.clone(bytes(int(b, 16) for b in value.split()))
            elif type == "oid":
                mib_value = mib.syntax.clone(parse_oid_value(mibBuilder, value))
            elif type == "timeticks":
                mib_value = mib.syntax.clone(parse_timeticks(value))
            else:
                mib_value = mib.syntax.clone(value)
            mib_instance = MibScalarInstance(mib.name, suffix, mib_value)
            mibBuilder.export_symbols("__MY_MIB", mib_instance)
    except Exception as e:
        logger.error(f"Failed to load {key} with values {values}")
        logger.exception(e)

def parse_oid_value(mibBuilder, value):
    value = value.strip()

    # Numeric OID, e.g. "1.3.6.1.4.1.9"
    numeric = value.lstrip(".")
    if numeric and all(part.isdigit() for part in numeric.split(".")):
        return tuple(int(part) for part in numeric.split("."))

    # Symbolic OID, e.g. "CISCO-SMI::ciscoModules.3.1.9.74.106"
    if "::" in value:
        module, symbol_path = value.split("::", 1)
        parts = symbol_path.split(".")
        symbol = parts[0]
        suffix = parts[1:]

        mib_symbol = mibBuilder.import_symbols(module, symbol)[0]
        return tuple(mib_symbol.name) + tuple(int(part) for part in suffix)

    raise ValueError(f"Unsupported OID value: {value}")


def parse_timeticks(value):
    if isinstance(value, int):
        return value

    match = re.match(r"^\s*\(?(\d+)\)?", str(value))
    if match:
        return int(match.group(1))

    raise ValueError(f"Invalid TimeTicks value: {value!r}")

def parse_suffix(suffix):
    if not suffix:
        return (0,)

    # numeric OID suffix
    if "." in suffix or suffix.isdigit():
        return tuple(int(x) for x in suffix.split("."))

    # MAC address
    if ":" in suffix:
        return tuple(int(x, 16) for x in suffix.split(":"))

    raise ValueError(f"Unsupported suffix format: {suffix}")

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
