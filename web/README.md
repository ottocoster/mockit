# Mock'it in the browser (WebAssembly)

This directory builds a static web page that runs Mock'it's device emulation
inside the browser using [Pyodide](https://pyodide.org) (CPython compiled to
WebAssembly) and [xterm.js](https://xtermjs.org). No server or Docker is
needed: open the page, pick a device, and type commands.

```bash
cd web
npm install            # fetches Pyodide + xterm.js
npm run build          # writes dist/ (python3 build.py)
python3 -m http.server -d dist 8080
# open http://localhost:8080/?device=cisco_ios
```

Live demo: <https://ottocoster.github.io/mockit/>. The workflow in
`.github/workflows/pages.yml` redeploys it on every push to `main` that
touches `web/`, `src/` or `configs/`, and it can also be started by hand.

`dist/` is a plain static site. You can host it on GitHub Pages, S3 or any
web server. It must be served over HTTP(S), not opened as a `file://` URL.

## How it works

`build.py` packs `src/` and the SSH parts of `configs/` (handler modules,
`scripts/` and `templates/`) into `mockit.zip`. In the page,
`mockit_browser.py`:

* stubs `asyncssh` and `openai`, which cannot run in a browser, and replaces
  `db_operations` (sqlite) with an in-memory store;
* imports the **unmodified** `<device>_handler` class, just like
  `src/start_ssh.py` does;
* hands it a fake `SSHServerProcess` whose stdin and stdout are connected
  to the xterm.js terminal.

So prompts, templates, device scripts (for example `vlan 10` followed by
`show vlan brief` on `cisco_ios`), `?` help, `sh`/`disp` aliases, enable mode
with an enable secret and per-vendor overrides all behave as they do in the
container. URL parameters `device` and `version` choose the device, for
example `?device=mikrotik_routeros&version=v6`.

## Honeypot mode

Tick **Honeypot mode** (or add `honeypot=1` to the URL) to run the session
the way `HONEYPOT_MODE=true` does. The enable prompt accepts any password,
and every input line and enable password is recorded through
`src/honeypot.py`. The lines appear live in a panel next to the terminal,
in the same format as the container's
`<HONEYPOT_LOG_DIR>/<date>/<ip>.txt` files, and **Download** saves them as
a text file. Nothing leaves the browser: the log lives only in the page
and disappears on reload.

## Limitations

* **No network listeners.** A browser tab cannot accept TCP or UDP
  connections, so the SSH, Telnet, SNMP, NETCONF and REST API servers do not
  exist here. Netmiko, Ansible and similar tools cannot connect to the page.
  It is an interactive demo and playground for the device library, not a
  replacement for the container.
* SSH handlers only. Telnet-specific handlers and AI mode are not wired up.
* State such as VLANs created by scripts lasts until the page reloads.
