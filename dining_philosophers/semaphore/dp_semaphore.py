
# Dining Philosophers (4) solved using semaphores.
# This program generates dining_philosophers_semaphore.html
# using events collected during the actual execution.

import threading
import time
import random
import json

NUM_PHILOSOPHERS = 4
EATING_ROUNDS = 3
MAX_DELAY = 0.6

# -1 indicates that a fork is currently free.
fork_owner = [-1] * NUM_PHILOSOPHERS

log_lock = threading.Lock()
events = []
start_time = time.time()


def log(who, state, note=""):
    """Record an event and the current fork ownership."""
    with log_lock:
        events.append({
            "time": round(time.time() - start_time, 3),
            "who": who,
            "state": state,
            "note": note,
            "forks": list(fork_owner),
        })


def pause():
    delay = random.uniform(0.1, MAX_DELAY)
    time.sleep(delay)


# Each fork is protected by its own semaphore.
forks = [
    threading.Semaphore(1) for _ in range(NUM_PHILOSOPHERS)
]

# Allow only three philosophers to attempt to acquire forks at once.
# This prevents all four philosophers from holding one fork each.
room = threading.Semaphore(NUM_PHILOSOPHERS - 1)


def philosopher(i):
    left = i
    right = (i + 1) % NUM_PHILOSOPHERS

    for _ in range(EATING_ROUNDS):
        log(i, "thinking")
        pause()

        log(i, "hungry", "wants to eat")
        room.acquire()

        log(i, "acquiring", "picking up forks")
        forks[left].acquire()
        fork_owner[left] = i
        log(i, "acquiring", "has left fork " + str(left))

        forks[right].acquire()
        fork_owner[right] = i

        # Critical section: the philosopher eats while holding both forks.
        log(i, "eating", "has forks " + str(left) + " and " + str(right))
        pause()

        log(i, "releasing", "putting forks down")
        fork_owner[left] = -1
        forks[left].release()

        fork_owner[right] = -1
        forks[right].release()

        room.release()


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Concurrency Visualizer</title>

<style>
:root {
  --bg: #0f1420;
  --panel: #171e2e;
  --panel-2: #1f283b;
  --line: #2c3750;
  --text: #e6ebf5;
  --muted: #8b97b3;
  --accent: #5eead4;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  font-family: "Segoe UI", Tahoma, sans-serif;
  background: var(--bg);
  color: var(--text);
  min-height: 100vh;
}

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 14px;
  padding: 18px 28px;
  background: var(--panel);
  border-bottom: 1px solid var(--line);
}

.brand h1 {
  margin: 0;
  font-size: 22px;
  letter-spacing: 0.4px;
}

.brand small {
  color: var(--muted);
  font-size: 13px;
}

.transport {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.btn {
  border: 1px solid var(--line);
  background: var(--panel-2);
  color: var(--text);
  padding: 9px 15px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 13px;
}

.btn:hover { border-color: var(--accent); }
.btn.primary { background: var(--accent); color: #07211e; border-color: var(--accent); font-weight: 600; }

.speedbox {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--muted);
  font-size: 12px;
}

.speedbox input { width: 110px; }

.progress-wrap {
  height: 4px;
  background: var(--line);
}

#bar {
  height: 100%;
  width: 0%;
  background: var(--accent);
  transition: width 0.2s;
}

main {
  padding: 22px 28px 40px;
  max-width: 1200px;
  margin: 0 auto;
}

.stats {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.stat {
  flex: 1 1 160px;
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 14px 18px;
}

.stat label { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 1px; }
.stat b { display: block; font-size: 28px; margin-top: 4px; }

.grid {
  display: grid;
  grid-template-columns: 1.1fr 1fr;
  gap: 18px;
}

.card {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 18px;
}

.card h2 {
  margin: 0 0 14px;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 1.2px;
  color: var(--muted);
}

#ring { width: 100%; max-height: 420px; display: block; }

.roster { display: grid; gap: 8px; }

.chip-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--panel-2);
  border-radius: 10px;
  padding: 10px 14px;
  border-left: 5px solid var(--line);
  font-size: 14px;
}

.chip-row em {
  font-style: normal;
  font-size: 12px;
  padding: 3px 10px;
  border-radius: 12px;
  color: #0b1020;
  font-weight: 600;
}

.res-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
  gap: 8px;
  margin-top: 16px;
}

.res {
  background: var(--panel-2);
  border-radius: 10px;
  padding: 9px 12px;
  font-size: 13px;
  border-top: 3px solid #3b8f6a;
}

.res.busy { border-top-color: #e0566b; }
.res span { display: block; color: var(--muted); font-size: 11px; margin-top: 3px; }

.logcard { margin-top: 18px; }

.logtools {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.logtools select {
  background: var(--panel-2);
  color: var(--text);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 5px 8px;
}

#timeline {
  max-height: 260px;
  overflow-y: auto;
  padding-left: 4px;
}

.tl {
  display: flex;
  gap: 12px;
  padding: 7px 0;
  font-size: 13px;
  border-bottom: 1px dashed var(--line);
}

.tl .t { color: var(--muted); width: 62px; flex-shrink: 0; font-family: Consolas, monospace; }
.tl .dot { width: 10px; height: 10px; border-radius: 50%; margin-top: 4px; flex-shrink: 0; }
.tl .note { color: var(--muted); }

@media (max-width: 820px) {
  .grid { grid-template-columns: 1fr; }
  main { padding: 16px 14px 30px; }
  .topbar { padding: 14px; }
}
</style>
</head>

<body>

<div class="topbar">
  <div class="brand">
    <h1 id="ttl">Simulation</h1>
    <small id="sub"></small>
  </div>
  <div class="transport">
    <button class="btn primary" id="playBtn">Play</button>
    <button class="btn" id="stepBtn">Step</button>
    <button class="btn" id="resetBtn">Reset</button>
    <div class="speedbox">
      Slow
      <input id="speedRange" type="range" min="50" max="1500" step="50" value="600">
      Fast
    </div>
  </div>
</div>
<div class="progress-wrap"><div id="bar"></div></div>

<main>
  <div class="stats">
    <div class="stat"><label>Step</label><b id="sStep">0</b></div>
    <div class="stat"><label>Active (eating / working)</label><b id="sActive">0</b></div>
    <div class="stat"><label>Free resources</label><b id="sFree">0</b></div>
    <div class="stat"><label>Sim time</label><b id="sTime">0s</b></div>
  </div>

  <div class="grid">
    <div class="card">
      <h2>Table view</h2>
      <svg id="ring" viewBox="0 0 400 400"></svg>
    </div>

    <div class="card">
      <h2>Participants</h2>
      <div class="roster" id="roster"></div>
      <div class="res-grid" id="resGrid"></div>
    </div>
  </div>

  <div class="card logcard">
    <div class="logtools">
      <h2 style="margin:0">Event timeline</h2>
      <select id="filter"><option value="all">All states</option></select>
    </div>
    <div id="timeline"></div>
  </div>
</main>

<script>
var events = __EVENTS__;

/* Edit these labels when reusing the template for another program */
var CONFIG = {
  title: "Dining Philosophers",
  subtitle: "Semaphore-based synchronization",
  actor: "Philosopher",
  actorShort: "P",
  resource: "Fork",
  resourceShort: "F",
  activeStates: ["eating", "writing", "reading", "working"]
};

var KNOWN = {
  thinking: "#94a3b8", hungry: "#fbbf24", acquiring: "#a78bfa",
  eating: "#34d399", releasing: "#60a5fa", waiting: "#fbbf24",
  reading: "#38bdf8", writing: "#fb7185", idle: "#94a3b8"
};

var Sim = {
  pos: 0,
  playing: false,
  handle: null,
  actors: 0,
  resCount: 0,
  state: [],
  holder: [],
  seen: {}
};

function colorFor(name) {
  if (KNOWN[name]) return KNOWN[name];
  var h = 0;
  for (var i = 0; i < name.length; i++) h = (h * 31 + name.charCodeAt(i)) % 360;
  return "hsl(" + h + ",65%,65%)";
}

function $(id) { return document.getElementById(id); }

function scan() {
  var maxWho = -1, rc = 0;
  for (var i = 0; i < events.length; i++) {
    if (events[i].who > maxWho) maxWho = events[i].who;
    if (events[i].forks && events[i].forks.length > rc) rc = events[i].forks.length;
  }
  Sim.actors = maxWho + 1;
  Sim.resCount = rc;
}

function blank() {
  Sim.state = [];
  Sim.holder = [];
  for (var i = 0; i < Sim.actors; i++) Sim.state.push("thinking");
  for (var j = 0; j < Sim.resCount; j++) Sim.holder.push(-1);
}

function polar(deg, r) {
  var a = deg * Math.PI / 180;
  return { x: 200 + r * Math.cos(a), y: 200 + r * Math.sin(a) };
}

function paint() {
  var n = Sim.actors, m = Sim.resCount;
  var svg = "<circle cx='200' cy='200' r='105' fill='#1f283b' stroke='#2c3750'/>";
  var actorPts = [], resPts = [];

  for (var i = 0; i < n; i++) actorPts.push(polar(-90 + i * 360 / n, 150));
  for (var k = 0; k < m; k++) resPts.push(polar(-90 + (k + 0.5) * 360 / m, 105));

  for (var q = 0; q < m; q++) {
    var o = Sim.holder[q];
    if (o >= 0 && actorPts[o]) {
      svg += "<line x1='" + resPts[q].x + "' y1='" + resPts[q].y + "' x2='" + actorPts[o].x +
             "' y2='" + actorPts[o].y + "' stroke='" + colorFor(Sim.state[o]) +
             "' stroke-width='3' stroke-dasharray='5 4'/>";
    }
  }

  for (var r = 0; r < m; r++) {
    var busy = Sim.holder[r] >= 0;
    svg += "<rect x='" + (resPts[r].x - 11) + "' y='" + (resPts[r].y - 11) +
           "' width='22' height='22' rx='5' fill='" + (busy ? "#e0566b" : "#3b8f6a") + "'/>";
    svg += "<text x='" + resPts[r].x + "' y='" + (resPts[r].y + 4) +
           "' font-size='11' fill='white' text-anchor='middle'>" + CONFIG.resourceShort + r + "</text>";
  }

  for (var a = 0; a < n; a++) {
    var c = colorFor(Sim.state[a]);
    svg += "<circle cx='" + actorPts[a].x + "' cy='" + actorPts[a].y + "' r='25' fill='" + c +
           "' stroke='#0f1420' stroke-width='3'/>";
    svg += "<text x='" + actorPts[a].x + "' y='" + (actorPts[a].y + 5) +
           "' font-size='14' font-weight='700' fill='#0b1020' text-anchor='middle'>" +
           CONFIG.actorShort + a + "</text>";
  }
  $("ring").innerHTML = svg;

  var roster = "", active = 0;
  for (var s = 0; s < n; s++) {
    var st = Sim.state[s];
    if (CONFIG.activeStates.indexOf(st) >= 0) active++;
    roster += "<div class='chip-row' style='border-left-color:" + colorFor(st) + "'><span>" +
              CONFIG.actor + " " + CONFIG.actorShort + s + "</span><em style='background:" +
              colorFor(st) + "'>" + st + "</em></div>";
  }
  $("roster").innerHTML = roster;

  var rg = "", free = 0;
  for (var t = 0; t < m; t++) {
    if (Sim.holder[t] < 0) {
      free++;
      rg += "<div class='res'>" + CONFIG.resource + " " + t + "<span>free</span></div>";
    } else {
      rg += "<div class='res busy'>" + CONFIG.resource + " " + t + "<span>held by " +
            CONFIG.actorShort + Sim.holder[t] + "</span></div>";
    }
  }
  $("resGrid").innerHTML = rg;

  $("sStep").textContent = Sim.pos + " / " + events.length;
  $("sActive").textContent = active;
  $("sFree").textContent = free;
  $("bar").style.width = (events.length ? (Sim.pos / events.length * 100) : 0) + "%";
}

function addLine(ev) {
  var row = document.createElement("div");
  row.className = "tl";
  row.setAttribute("data-state", ev.state);
  var txt = "<span class='t'>" + ev.time + "s</span>";
  txt += "<span class='dot' style='background:" + colorFor(ev.state) + "'></span>";
  txt += "<span>" + CONFIG.actorShort + ev.who + " &rarr; <b>" + ev.state + "</b>";
  if (ev.note) txt += " <span class='note'>(" + ev.note + ")</span>";
  txt += "</span>";
  row.innerHTML = txt;

  var box = $("timeline");
  box.appendChild(row);
  box.scrollTop = box.scrollHeight;
  applyFilter();

  if (!Sim.seen[ev.state]) {
    Sim.seen[ev.state] = true;
    var opt = document.createElement("option");
    opt.value = ev.state;
    opt.textContent = ev.state;
    $("filter").appendChild(opt);
  }
}

function applyFilter() {
  var want = $("filter").value;
  var rows = $("timeline").children;
  for (var i = 0; i < rows.length; i++) {
    var ok = want === "all" || rows[i].getAttribute("data-state") === want;
    rows[i].style.display = ok ? "flex" : "none";
  }
}

function advance() {
  if (Sim.pos >= events.length) {
    halt();
    return false;
  }
  var ev = events[Sim.pos];
  Sim.state[ev.who] = ev.state;
  if (ev.forks) Sim.holder = ev.forks.slice();
  Sim.pos++;
  $("sTime").textContent = ev.time + "s";
  addLine(ev);
  paint();
  return true;
}

function loop() {
  if (!Sim.playing) return;
  if (!advance()) return;
  Sim.handle = setTimeout(loop, 1550 - Number($("speedRange").value));
}

function launch() {
  if (Sim.pos >= events.length) return;
  Sim.playing = true;
  $("playBtn").textContent = "Pause";
  loop();
}

function halt() {
  Sim.playing = false;
  clearTimeout(Sim.handle);
  $("playBtn").textContent = "Play";
}

function restart() {
  halt();
  Sim.pos = 0;
  Sim.seen = {};
  $("timeline").innerHTML = "";
  $("filter").innerHTML = "<option value='all'>All states</option>";
  $("sTime").textContent = "0s";
  blank();
  paint();
}

$("playBtn").onclick = function () { Sim.playing ? halt() : launch(); };
$("stepBtn").onclick = function () { halt(); advance(); };
$("resetBtn").onclick = restart;
$("filter").onchange = applyFilter;

document.title = CONFIG.title + " - Visualizer";
$("ttl").textContent = CONFIG.title;
$("sub").textContent = CONFIG.subtitle;

scan();
blank();
paint();
</script>

</body>
</html>
"""


def make_html(filename):
    page = HTML_TEMPLATE.replace("__EVENTS__", json.dumps(events))

    with open(filename, "w", encoding="utf-8") as html_file:
        html_file.write(page)


def main():
    threads = [
        threading.Thread(target=philosopher, args=(i,))
        for i in range(NUM_PHILOSOPHERS)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    make_html("dining_philosophers_semaphore.html")

    print(
        "Finished. Every philosopher ate",
        EATING_ROUNDS,
        "times, no deadlock."
    )
    print("Events recorded:", len(events))
    print("Open dining_philosophers_semaphore.html in your browser.")


if __name__ == "__main__":
    main()
