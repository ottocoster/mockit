"""
HTTP/REST API driver for Mock'it.

Serves per-driver routes defined in ``configs/<device_type>/api/routes.json``,
mapping ``METHOD /path`` to a response file (json/txt/xml). Authentication is
configured per driver via environment variables (see src/options.py -> 'api'):
``none`` | ``bearer`` | ``apikey`` | ``oauth2``.

OAuth2 supports both the simple client-credentials flow and a multi-step
authorization-code flow (login -> authorize -> token), enough to mock platforms
like HPE GreenLake and Aruba Central. Route flags:

* ``"oauth_token": true``     - issues an access token (client_credentials,
                                authorization_code or refresh_token grants)
* ``"oauth_authorize": true`` - returns an ``auth_code`` for the code flow
* ``"public": true``          - serve this file route without authentication

Built on aiohttp so it shares the asyncio event loop / ServerRegistry with the
SSH, Telnet, SNMP and NETCONF drivers.
"""

import asyncio
import json
import logging
import ssl
from pathlib import Path

from aiohttp import web


logger = logging.getLogger("app")


class APIServer:
    """aiohttp-based mock REST API server for a single driver."""

    def __init__(self):
        self.runner: web.AppRunner | None = None

    # ---- lifecycle -------------------------------------------------------

    async def run(self, status, options):
        app = self.build_app(options)
        self.runner = web.AppRunner(app, access_log=None)
        await self.runner.setup()

        ssl_ctx = self._ssl_context(options)
        site = web.TCPSite(
            self.runner, host="0.0.0.0", port=options["port"], ssl_context=ssl_ctx
        )
        await site.start()

        scheme = "https" if ssl_ctx else "http"
        logger.info(
            f"API server running on {scheme}://0.0.0.0:{options['port']} "
            f"for device `{options['device_type']}` (auth={options.get('auth_type', 'none')})"
        )

        await status.service_ready()
        try:
            await asyncio.Event().wait()  # serve until cancelled
        except asyncio.CancelledError:
            pass
        finally:
            await self.runner.cleanup()
            self.runner = None

    def stop(self):
        return None

    # ---- TLS -------------------------------------------------------------

    def _ssl_context(self, options):
        if not options.get("tls", True):
            return None
        cert, key = options.get("cert"), options.get("key")
        if not (cert and key and Path(cert).exists() and Path(key).exists()):
            logger.warning(
                "API TLS requested but cert/key missing (%s, %s); serving plain HTTP",
                cert, key,
            )
            return None
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(certfile=cert, keyfile=key)
        return ctx

    # ---- routing ---------------------------------------------------------

    def _api_dir(self, options) -> Path:
        d = Path(f"configs/{options['device_type']}")
        if options.get("device_version"):
            d = d / options["device_version"]
        return d / "api"

    def _load_routes(self, options) -> list[dict]:
        rf = self._api_dir(options) / "routes.json"
        if not rf.exists():
            logger.warning(f"No API routes file found: {rf}")
            return []
        try:
            data = json.loads(rf.read_text())
        except json.JSONDecodeError as e:
            logger.error(f"Invalid routes.json ({rf}): {e}")
            return []
        if isinstance(data, dict):
            return data.get("routes", [])
        return data if isinstance(data, list) else []

    def build_app(self, options) -> web.Application:
        app = web.Application(middlewares=[self._auth_middleware(options)])
        api_dir = self._api_dir(options)
        public_paths: set[str] = set()

        for route in self._load_routes(options):
            method = route.get("method", "GET").upper()
            path = route["path"]
            if route.get("oauth_token"):
                public_paths.add(path)
                handler = self._token_handler(options)
            elif route.get("oauth_authorize"):
                public_paths.add(path)
                handler = self._authorize_handler(options)
            else:
                if route.get("public"):
                    public_paths.add(path)
                handler = self._file_handler(api_dir, route)
            app.router.add_route(method, path, handler)

        app["public_paths"] = public_paths
        return app

    def _file_handler(self, api_dir: Path, route: dict):
        status_code = route.get("status", 200)
        ctype = route.get("content_type", "application/json")
        file = route.get("file")
        inline = route.get("body")

        async def handler(request):
            if inline is not None:
                text = inline if isinstance(inline, str) else json.dumps(inline)
            elif file:
                fp = api_dir / file
                if not fp.exists():
                    return web.json_response(
                        {"error": f"response file `{file}` not found"}, status=404
                    )
                text = fp.read_text()
            else:
                text = ""
            return web.Response(text=text, status=status_code, content_type=ctype)

        return handler

    # ---- oauth2 ----------------------------------------------------------

    def _authorize_handler(self, options):
        async def handler(request):
            return web.json_response(
                {"auth_code": options.get("oauth_auth_code", "mockit-auth-code")}
            )
        return handler

    def _token_handler(self, options):
        async def handler(request):
            body = await self._read_body(request)
            grant = body.get("grant_type", "")
            cid, secret = body.get("client_id"), body.get("client_secret")
            exp_id = options.get("oauth_client_id", "")
            exp_secret = options.get("oauth_client_secret", "")

            # Validate client credentials when they are configured.
            if grant in ("client_credentials", "authorization_code"):
                if (exp_id and cid != exp_id) or (exp_secret and secret != exp_secret):
                    return web.json_response({"error": "invalid_client"}, status=401)

            # Authorization-code grant must present the issued code.
            if grant == "authorization_code":
                expected = options.get("oauth_auth_code", "mockit-auth-code")
                if expected and body.get("code") != expected:
                    return web.json_response({"error": "invalid_grant"}, status=401)

            return web.json_response(
                {
                    "access_token": options.get("oauth_access_token", "mockit-access-token"),
                    "refresh_token": options.get("oauth_refresh_token", "mockit-refresh-token"),
                    "token_type": "Bearer",
                    "expires_in": 3600,
                }
            )
        return handler

    async def _read_body(self, request) -> dict:
        """Read a request body as a dict from JSON or form-encoded content."""
        try:
            if "application/json" in request.headers.get("Content-Type", ""):
                return await request.json()
            return dict(await request.post())
        except Exception:  # noqa: BLE001 - tolerate malformed bodies
            return {}

    # ---- authentication --------------------------------------------------

    def _auth_middleware(self, options):
        auth_type = options.get("auth_type", "none")

        @web.middleware
        async def middleware(request, handler):
            if request.path in request.app.get("public_paths", set()):
                return await handler(request)
            if self._authorized(request, options, auth_type):
                return await handler(request)
            return web.json_response({"error": "unauthorized"}, status=401)

        return middleware

    def _authorized(self, request, options, auth_type) -> bool:
        if auth_type == "none":
            return True
        if auth_type == "bearer":
            return request.headers.get("Authorization", "") == f"Bearer {options.get('token', '')}"
        if auth_type == "apikey":
            header = options.get("api_key_header", "X-API-KEY")
            return request.headers.get(header) == options.get("api_key", "")
        if auth_type == "oauth2":
            expected = options.get("oauth_access_token", "mockit-access-token")
            return request.headers.get("Authorization", "") == f"Bearer {expected}"
        logger.warning(f"Unknown API_AUTH_TYPE `{auth_type}`; denying request")
        return False
