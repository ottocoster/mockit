import logging

from api_server.api_server import APIServer


logger = logging.getLogger("app")

_api_server = APIServer()


async def start_api(status, options):
    """Entry point used by ServerRegistry to start the REST API driver."""
    logger.debug(f"starting api {options}")
    await _api_server.run(status, options)


def stop_api():
    _api_server.stop()
