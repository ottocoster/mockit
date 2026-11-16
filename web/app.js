// Mock'it in the browser: xterm.js front end for the Pyodide runtime.
"use strict";

const $ = (id) => document.getElementById(id);
const statusEl = $("status");
const deviceEl = $("device");
const secretEl = $("secret");
const connectEl = $("connect");
const honeypotEl = $("honeypot");
const honeypotLogEl = $("honeypot-log");

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
  if (honeypotEl.checked) url.searchParams.set("honeypot", "1"); else url.searchParams.delete("honeypot");
  document.body.classList.toggle("honeypot", honeypotEl.checked);
  fit.fit();
  history.replaceState(null, "", url);

  term.reset();
  line = "";
  term.write(`\x1b[90mConnected to mock ${deviceLabel({ type, version })} (Pyodide ${py.pyodideVersion}).\x1b[0m\r\n` +
    `\x1b[90mIf the device asks you to log in, use ${py.mod.LOGIN_USERNAME} / ${py.mod.LOGIN_PASSWORD}.\x1b[0m\r\n` +
    (honeypotEl.checked ? `\x1b[33mHoneypot mode: any enable password is accepted and all input is recorded.\x1b[0m\r\n` : ""));
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
      honeypotEl.checked,
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

// ---------- honeypot log panel ----------
const honeypotLog = {
  el: honeypotLogEl,
  lines: [],                 // raw lines for Download
  sources: new Map(),        // ip -> { cc, country } (demo attackers)
  seenIps: new Set(),
  seenCountries: new Set(),
  counts: { logins: 0, commands: 0 },
  maxRows: 400,
  suspicious: /wget |curl |tftp:|ftpget|chmod |busybox|\/tmp|base64|authorized_keys|crontab|\bnc\b|privilege 15|secret \d|rm -rf|\.sh\b/i,

  flag(cc) {
    return cc ? String.fromCodePoint(...[...cc.toUpperCase()].map((c) => 0x1f1e6 + c.charCodeAt(0) - 65)) : "";
  },

  parse(event) {
    let m;
    if ((m = event.match(/^(SSH|Telnet) login: username=`(.*)` password=`(.*)`$/)))
      return { kind: "login", tag: `${m[1].toUpperCase()} LOGIN`, user: m[2], pass: m[3] };
    if ((m = event.match(/^SSH enable password: (.*)$/)))
      return { kind: "enable", tag: "ENABLE PW", text: m[1] };
    if ((m = event.match(/^(SSH|Telnet) input: (.*)$/)))
      return { kind: "input", tag: `${m[1].toUpperCase()} CMD`, text: m[2] };
    return { kind: "session", tag: "SESSION", text: event };
  },

  add(ip, line) {
    ip = String(ip);
    this.lines.push(line.replace(/^(\[[^\]]+\]) /, `$1 [${ip}] `));
    const m = line.match(/^\[\d{4}-\d\d-\d\d (\d\d:\d\d:\d\d)\] (.*)$/s);
    const time = m ? m[1] : "";
    const ev = this.parse(m ? m[2] : line);
    const source = this.sources.get(ip);

    if (ev.kind === "login") this.counts.logins++;
    if (ev.kind === "input") this.counts.commands++;
    this.seenIps.add(ip);
    if (source) this.seenCountries.add(source.cc);

    const row = document.createElement("div");
    row.className = `ev ev-${ev.kind}`;
    const meta = document.createElement("div");
    meta.className = "meta";
    const add = (parent, tag, cls, text, title) => {
      const el = document.createElement(tag);
      if (cls) el.className = cls;
      el.textContent = text;
      if (title) el.title = title;
      parent.append(el);
      return el;
    };
    if (ip === "browser") add(meta, "span", "flag", "💻", "Your browser session");
    else add(meta, "span", "flag", this.flag(source?.cc), source?.country);
    add(meta, "span", "ip", ip === "browser" ? "you" : ip);
    if (source) add(meta, "span", "country", source.country);
    add(meta, "span", "tag", ev.tag);
    add(meta, "time", "", time);
    row.append(meta);

    const msg = add(row, "div", "msg", "");
    if (ev.kind === "login") {
      add(msg, "span", "cred", ev.user);
      msg.append(" / ");
      add(msg, "span", "cred", ev.pass);
    } else {
      msg.textContent = ev.text;
      if (ev.kind !== "session" && this.suspicious.test(ev.text)) row.classList.add("suspicious");
    }

    const atBottom = this.el.scrollHeight - this.el.scrollTop - this.el.clientHeight < 24;
    this.el.append(row);
    while (this.el.childElementCount > this.maxRows) this.el.firstElementChild.remove();
    if (atBottom) this.el.scrollTop = this.el.scrollHeight;
    this.renderStats();
  },

  renderStats() {
    $("stat-logins").textContent = this.counts.logins;
    $("stat-commands").textContent = this.counts.commands;
    $("stat-sources").textContent = this.seenIps.size;
    $("stat-countries").textContent = this.seenCountries.size;
  },

  clear() {
    this.el.textContent = "";
    this.lines = [];
    this.seenIps.clear();
    this.seenCountries.clear();
    this.counts = { logins: 0, commands: 0 };
    this.renderStats();
  },
};

// ---------- loading screen ----------
const loader = {
  el: $("loader"),
  stepEl: $("loader-step"),
  detailEl: $("loader-detail"),
  barEl: $("loader-bar"),
  sizes: {},       // file name -> uncompressed size (from sizes.json)
  received: {},    // file name -> bytes received so far
  step(name, text) {
    let reached = false;
    for (const li of document.querySelectorAll("#loader-steps li")) {
      const current = li.dataset.step === name;
      li.classList.toggle("active", current);
      li.classList.toggle("complete", !current && !reached);
      if (current) reached = true;
    }
    this.stepEl.textContent = text;
    setStatus(text);
  },
  detail(text) { this.detailEl.textContent = text; },
  progress() {
    // Once the big runtime files are in, Pyodide compiles and boots.
    if (this.stepEl.textContent.startsWith("Downloading the Python") &&
        ["pyodide.asm.wasm", "python_stdlib.zip"].every((f) => this.sizes[f] && this.received[f] >= this.sizes[f])) {
      this.stepEl.textContent = "Starting the Python interpreter…";
    }
    const mb = (n) => (n / 1048576).toFixed(1);
    const got = Object.values(this.received).reduce((a, b) => a + b, 0);
    const total = Object.values(this.sizes).reduce((a, b) => a + b, 0);
    if (total) {
      this.barEl.style.width = `${Math.min(100, (got / total) * 100).toFixed(1)}%`;
      this.detail(`${mb(Math.min(got, total))} / ${mb(total)} MB`);
    } else {
      this.detail(`${mb(got)} MB downloaded`);
    }
  },
  done() {
    this.barEl.style.width = "100%";
    for (const li of document.querySelectorAll("#loader-steps li")) {
      li.classList.remove("active");
      li.classList.add("complete");
    }
    this.el.classList.add("done");
    setTimeout(() => { fit.fit(); term.focus(); }, 50);
  },
  fail(err) {
    this.el.classList.add("error");
    this.stepEl.textContent = "Mock'it could not start";
    this.detail(err.message);
  },
};

// Count bytes of the large startup downloads (Pyodide fetches its files
// with the global fetch) so the loading screen can show real progress.
async function trackedFetch(input, init) {
  const response = await trackedFetch.original(input, init);
  const name = String(input instanceof Request ? input.url : input).split(/[?#]/)[0].split("/").pop();
  if (!(name in loader.sizes) || !response.ok || !response.body) return response;
  loader.received[name] = 0;
  const counter = new TransformStream({
    transform(chunk, controller) {
      loader.received[name] += chunk.byteLength;
      loader.progress();
      controller.enqueue(chunk);
    },
  });
  return new Response(response.body.pipeThrough(counter), {
    status: response.status, statusText: response.statusText, headers: response.headers,
  });
}
trackedFetch.original = window.fetch.bind(window);

async function main() {
  loader.step("runtime", "Downloading the Python runtime…");
  try {
    loader.sizes = await (await fetch("sizes.json")).json();
  } catch (_) { /* progress without a total */ }
  window.fetch = trackedFetch;
  let pyodide;
  try {
    pyodide = await loadPyodide({ indexURL: new URL("pyodide/", location).href });

    loader.step("library", "Downloading the device library…");
    const resp = await fetch("mockit.zip");
    if (!resp.ok) throw new Error(`mockit.zip: HTTP ${resp.status}`);
    pyodide.unpackArchive(await resp.arrayBuffer(), "zip", { extractDir: "/mockit" });
  } finally {
    window.fetch = trackedFetch.original;
  }

  loader.step("modules", "Importing Mock'it…");
  loader.detail(`Pyodide ${pyodide.version}`);
  await new Promise((r) => setTimeout(r, 0)); // let the screen repaint
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
  honeypotEl.checked = params.get("honeypot") === "1";
  honeypotEl.addEventListener("change", connect);
  mod.set_honeypot_listener((ip, logLine) => honeypotLog.add(ip, logLine));
  $("honeypot-clear").addEventListener("click", () => { honeypotLog.clear(); term.focus(); });
  $("honeypot-download").addEventListener("click", () => {
    const blob = new Blob([honeypotLog.lines.join("\n") + "\n"], { type: "text/plain" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `mockit-honeypot-${new Date().toISOString().slice(0, 10)}.txt`;
    a.click();
    URL.revokeObjectURL(a.href);
  });
  // Demo mode (?demo=1): simulated attackers feed the honeypot log.
  if (params.get("demo") === "1") {
    honeypotEl.checked = true;
    document.body.classList.add("demo");
    const syncDemo = () => {
      if (honeypotEl.checked) {
        MockitDemo.start({
          record: (ip, event) => mod.record_honeypot_event(ip, event),
          register: (ip, cc, country) => honeypotLog.sources.set(ip, { cc, country }),
        });
      } else {
        MockitDemo.stop();
      }
    };
    honeypotEl.addEventListener("change", syncDemo);
    setTimeout(syncDemo, 600);
  }
  window.mockit = { pyodide, connect, get session() { return session; } };
  loader.step("session", `Connecting to ${deviceLabel({ type: deviceEl.value.split("|")[0], version: deviceEl.value.split("|")[1] })}…`);
  await new Promise((r) => setTimeout(r, 0));
  connect();
  loader.done();
}

main().catch((err) => {
  console.error(err);
  setStatus("Failed to start");
  loader.fail(err);
  term.write(`\x1b[31mFailed to start Mock'it: ${err.message}\x1b[0m\r\n`);
});
