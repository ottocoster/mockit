from netconf.netconf import AsyncNetconfServer
import logging

logging.basicConfig(level=logging.INFO)  # Set to DEBUG to capture all logs, including INFO, WARNING, ERROR, and DEBUG

async def start_netconf(options):
    logger = logging.getLogger()
    logger.debug(f"starting netconf {options}")

    # Create and start the NetconfServer instance
    nc_server = AsyncNetconfServer()

    # Set properties on the server
    nc_server.base_version = "1.1"
    nc_server.host = "0.0.0.0"
    nc_server.port = 830
    nc_server.username = options['username']
    nc_server.password = options['password']
    nc_server.authorized_key = options['authorized_key']

    # Interact with the server as needed
    nc_server.expect_request(
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<nc:rpc xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="{message_id}">'
            "<nc:get-config><nc:source><nc:running/></nc:source></nc:get-config>"
            "</nc:rpc>"
        ).respond_with(
            """
            <?xml version="1.0" encoding="UTF-8"?>
            <rpc-reply message-id="{message_id}"
                xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <data>
                    OK
                </data>
            </rpc-reply>"""
        )

    nc_server.start()

    # # Stop the server when done
    # nc_server.stop()

