import asyncio

from netconf.netconf import AsyncNetconfServer
import logging


logger = logging.getLogger('app')


async def start_netconf(status, options):
    logger.debug(f"starting netconf {options}")

    # Create and start the NetconfServer instance
    nc_server = AsyncNetconfServer(status)

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

    start_netconf.stop_server = nc_server.stop

    async def stop_server():
        nc_server.stop()

    fs = [asyncio.ensure_future(nc_server.start())]
    await asyncio.wait(fs, return_when=asyncio.FIRST_COMPLETED)


def stop_netconf():
    start_netconf.stop_server()
