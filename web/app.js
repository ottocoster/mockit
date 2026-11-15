// Mock'it in the browser: xterm.js front end for the Pyodide runtime.
"use strict";

const $ = (id) => document.getElementById(id);
const statusEl = $("status");
const deviceEl = $("device");
const secretEl = $("secret");
const connectEl = $("connect");

const term = new Terminal({
  cursorBlink: true,
  convertEol: false,
  fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Consolas, monospace',
  fontSize: 14,
  theme: { background: "#0d1117", foreground: "#c9d1d9" },
  scrollback: 5000,
});
const fit = new FitAddon.FitAddon();
term.loadAddon(fit);
term.open($("terminal"));
fit.fit();
window.addEventListener("resize", () => fit.fit());

let py = null;        // Pyodide-loaded mockit_browser module
let session = null;   // current Python Session
let line = "";        // line being edited
const cmdHistory = [];
let historyIndex = 0;

function setStatus(text) { statusEl.textContent = text; }

function deviceLabel(d) { return d.version ? `${d.type} (${d.version})` : d.type; }

function closeSession() {
  const old = session;
  session = null; // detach first: close() fires the exit callback
  if (old) {
    try { old.close(); } catch (_) { /* already closed */ }
    old.destroy();
  }
}

function connect() {
  closeSession();
  const [type, version] = deviceEl.value.split("|");
  const url = new URL(location);
  url.searchParams.set("device", type);
  if (version) url.searchParams.set("version", version); else url.searchParams.delete("version");
  history.replaceState(null, "", url);

  term.reset();
  line = "";
  term.write(`\x1b[90mConnected to mock ${deviceLabel({ type, version })} (Pyodide ${py.pyodideVersion}).\x1b[0m\r\n` +
    `\x1b[90mIf the device asks you to log in, use ${py.mod.LOGIN_USERNAME} / ${py.mod.LOGIN_PASSWORD}.\x1b[0m\r\n`);
  try {
    let current = null;
    current = py.mod.new_session(
      type, version || "",
      (data) => term.write(data),
      (code) => {
        if (session !== current) return; // replaced by a newer session
        term.write(`\r\n\x1b[90mConnection closed (exit ${code}). Press Enter or Reconnect to start a new session.\x1b[0m\r\n`);
        session = null;
        // Destroy after Python has returned from the exit() call.
        setTimeout(() => current.destroy(), 0);
      },
      secretEl.value,
    );
    session = current;
    setStatus(`Device: ${deviceLabel({ type, version })}`);
  } catch (err) {
    term.write(`\r\n\x1b[31mFailed to load ${type}: ${err.message}\x1b[0m\r\n`);
    setStatus("Load failed");
  }
  term.focus();
}

function replaceLine(text) {
  term.write("\b \b".repeat(line.length));
  line = text;
  term.write(line);
}

function commonPrefix(words) {
  let p = words[0];
  for (const w of words) while (!w.startsWith(p)) p = p.slice(0, -1);
  return p;
}

function complete() {
  if (!session || !line) return;
  const matches = session.complete(line).toJs();
  if (!matches.length) return;
  const prefix = commonPrefix(matches);
  if (prefix.length > line.length) {
    replaceLine(matches.length === 1 ? prefix + " " : prefix);
  } else if (matches.length > 1) {
    term.write("\r\n" + matches.join("\r\n") + "\r\n" + session.handler.prompt_terminator + line);
  }
}

function submit() {
  if (!session) { connect(); return; }
  const cmd = line;
  const secret = session.password_mode();
  // The device handler echoes the command itself (the way each vendor does
  // over SSH), so erase our local echo before handing the line over.
  if (!secret) term.write("\b \b".repeat(cmd.length));
  if (cmd.trim() && !secret) {
    cmdHistory.push(cmd);
  }
  historyIndex = cmdHistory.length;
  line = "";
  session.send_line(cmd);
}

term.onData((data) => {
  if (!py) return;
  // Multi-character data is a paste (or an escape sequence).
  if (data === "\x1b[A" || data === "\x1b[B") {
    if (!cmdHistory.length || (session && session.password_mode())) return;
    historyIndex = Math.max(0, Math.min(cmdHistory.length, historyIndex + (data === "\x1b[A" ? -1 : 1)));
    replaceLine(cmdHistory[historyIndex] ?? "");
    return;
  }
  if (data.startsWith("\x1b")) return; // ignore other escape sequences
  for (const ch of data) {
    const secret = session && session.password_mode();
    if (ch === "\r") submit();
    else if (ch === "\n") continue;
    else if (ch === "\x7f" || ch === "\b") {
      if (line.length) { line = line.slice(0, -1); if (!secret) term.write("\b \b"); }
    } else if (ch === "\t") { if (!secret) complete(); }
    else if (ch === "\x03") { // Ctrl+C: drop the line, get a fresh prompt
      term.write("^C"); line = "";
      if (session) session.send_line(""); else term.write("\r\n");
    } else if (ch === "\x15") { if (!secret) replaceLine(""); else line = ""; } // Ctrl+U
    else if (ch === "\x0c") { term.clear(); } // Ctrl+L
    else if (ch >= " ") { line += ch; if (!secret) term.write(ch); }
  }
});

async function main() {
  const pyodide = await loadPyodide({ indexURL: new URL("pyodide/", location).href });
  setStatus("Loading device library…");
  const resp = await fetch("mockit.zip");
  if (!resp.ok) throw new Error(`mockit.zip: HTTP ${resp.status}`);
  pyodide.unpackArchive(await resp.arrayBuffer(), "zip", { extractDir: "/mockit" });
  const src = await (await fetch("mockit_browser.py")).text();
  pyodide.FS.writeFile("/mockit/mockit_browser.py", src);
  pyodide.runPython("import sys; sys.path.insert(0, '/mockit')");
  const mod = pyodide.pyimport("mockit_browser");
  py = { mod, pyodideVersion: pyodide.version };

  const devices = mod.list_devices().toJs({ dict_converter: Object.fromEntries });
  const params = new URLSearchParams(location.search);
  const wanted = `${params.get("device") || "cisco_ios"}|${params.get("version") || ""}`;
  deviceEl.innerHTML = "";
  for (const d of devices) {
    const opt = document.createElement("option");
    opt.value = `${d.type}|${d.version}`;
    opt.textContent = deviceLabel(d);
    deviceEl.appendChild(opt);
  }
  deviceEl.value = [...deviceEl.options].some((o) => o.value === wanted) ? wanted : "cisco_ios|";
  deviceEl.disabled = false;
  connectEl.disabled = false;
  deviceEl.addEventListener("change", connect);
  connectEl.addEventListener("click", connect);
  secretEl.addEventListener("keydown", (e) => { if (e.key === "Enter") { e.preventDefault(); connect(); } });
  window.mockit = { pyodide, connect, get session() { return session; } };
  connect();
}

main().catch((err) => {
  console.error(err);
  setStatus("Failed to start");
  term.write(`\x1b[31mFailed to start Mock'it: ${err.message}\x1b[0m\r\n`);
});
