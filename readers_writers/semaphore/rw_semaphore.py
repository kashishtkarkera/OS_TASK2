
# Readers-Writers problem solved using semaphores.
# Generates readers_writers_semaphore.html from recorded execution events.

import threading
import time
import random
import json

NUM_READERS = 3
NUM_WRITERS = 2
TOTAL_ROUNDS = 3
MAX_DELAY = 0.6

shared_data = 0
active_readers = 0

# Semaphores for protecting the reader count and shared resource.
reader_mutex = threading.Semaphore(1)
shared_resource = threading.Semaphore(1)

log_lock = threading.Lock()
events = []
start_time = time.time()


def log(who, state, note=""):
    """Record an execution event for the HTML simulation."""
    with log_lock:
        events.append({
            "time": round(time.time() - start_time, 3),
            "who": who,
            "state": state,
            "value": shared_data,
            "note": note,
        })


def pause():
    delay = random.uniform(0.1, MAX_DELAY)
    time.sleep(delay)


def reader(reader_id):
    global active_readers

    name = "Reader " + str(reader_id)

    for _ in range(TOTAL_ROUNDS):
        log(name, "thinking")
        pause()

        log(name, "waiting", "wants to read")

        reader_mutex.acquire()
        active_readers += 1

        if active_readers == 1:
            shared_resource.acquire()

        reader_mutex.release()

        # Critical section: reading the shared resource.
        log(name, "reading", "read value " + str(shared_data))
        pause()
        log(name, "done", "finished reading")

        reader_mutex.acquire()
        active_readers -= 1

        if active_readers == 0:
            shared_resource.release()

        reader_mutex.release()


def writer(writer_id):
    global shared_data

    name = "Writer " + str(writer_id)

    for _ in range(TOTAL_ROUNDS):
        log(name, "thinking")
        pause()

        log(name, "waiting", "wants to write")
        shared_resource.acquire()

        # Critical section: updating the shared resource.
        shared_data += 1
        log(name, "writing", "wrote value " + str(shared_data))
        pause()
        log(name, "done", "finished writing")

        shared_resource.release()


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

.brand h1 { margin: 0; font-size: 22px; letter-spacing: 0.4px; }
.brand small { color: var(--muted); font-size: 13px; }

.transport { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }

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

.speedbox { display: flex; align-items: center; gap: 8px; color: var(--muted); font-size: 12px; }
.speedbox input { width: 110px; }

.progress-wrap { height: 4px; background: var(--line); }
#bar { height: 100%; width: 0%; background: var(--accent); transition: width 0.2s; }

main { padding: 22px 28px 40px; max-width: 1200px; margin: 0 auto; }

.stats { display: flex; gap: 14px; flex-wrap: wrap; margin-bottom: 20px; }

.stat {
  flex: 1 1 160px;
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 14px 18px;
}

.stat label { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 1px; }
.stat b { display: block; font-size: 28px; margin-top: 4px; }

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

.vault {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 18px;
  border-width: 2px;
  transition: border-color 0.25s;
}

.vault.free { border-color: #4b5875; }
.vault.open { border-color: #34d399; }
.vault.locked { border-color: #fb7185; }
.vault.conflict { border-color: #ff2d55; background: #2a1520; }

.vault .val { font-size: 40px; font-weight: 700; font-family: Consolas, monospace; }
.vault .val.flash { color: var(--accent); }
.vault .badge {
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 14px;
  color: #0b1020;
}

.lanes { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }

.pool { display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 10px; }

.actor {
  background: var(--panel-2);
  border-radius: 10px;
  border-top: 4px solid var(--line);
  padding: 12px;
  text-align: center;
  font-size: 14px;
}

.actor em {
  display: block;
  margin-top: 8px;
  font-style: normal;
  font-size: 12px;
  padding: 3px 8px;
  border-radius: 12px;
  color: #0b1020;
  font-weight: 600;
}

.empty { color: var(--muted); font-size: 13px; }

.logcard { margin-top: 18px; }

.logtools { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }

.logtools select {
  background: var(--panel-2);
  color: var(--text);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 5px 8px;
}

#timeline { max-height: 280px; overflow-y: auto; padding-left: 4px; }

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
.tl .v { margin-left: auto; color: var(--accent); font-family: Consolas, monospace; white-space: nowrap; }

@media (max-width: 820px) {
  .lanes { grid-template-columns: 1fr; }
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
    <div class="stat"><label>Readers inside</label><b id="sRead">0</b></div>
    <div class="stat"><label>Writers inside</label><b id="sWrite">0</b></div>
    <div class="stat"><label>Sim time</label><b id="sTime">0s</b></div>
  </div>

  <div class="card vault free" id="vault">
    <div>
      <h2 style="margin-bottom:6px">Shared resource</h2>
      <div class="val" id="vVal">0</div>
    </div>
    <div class="badge" id="vBadge">FREE</div>
  </div>

  <div class="lanes">
    <div class="card">
      <h2>Readers</h2>
      <div class="pool" id="poolR"></div>
    </div>
    <div class="card">
      <h2>Writers</h2>
      <div class="pool" id="poolW"></div>
    </div>
  </div>

  <div class="card" id="otherCard" style="margin-top:18px; display:none">
    <h2>Other threads</h2>
    <div class="pool" id="poolO"></div>
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
  title: "Readers-Writers",
  subtitle: "Semaphore-based synchronization"
};

var KNOWN = {
  thinking: "#94a3b8", waiting: "#fbbf24", reading: "#34d399",
  writing: "#fb7185", done: "#60a5fa", idle: "#94a3b8"
};

var Sim = {
  pos: 0,
  playing: false,
  handle: null,
  order: [],
  role: {},
  state: {},
  value: 0,
  seen: {}
};

function $(id) { return document.getElementById(id); }

function colorFor(name) {
  if (KNOWN[name]) return KNOWN[name];
  var h = 0;
  for (var i = 0; i < name.length; i++) h = (h * 31 + name.charCodeAt(i)) % 360;
  return "hsl(" + h + ",65%,65%)";
}

function scan() {
  var found = {};
  for (var i = 0; i < events.length; i++) {
    var who = String(events[i].who);
    if (!found[who]) {
      found[who] = true;
      Sim.order.push(who);
    }
    if (events[i].state === "reading") Sim.role[who] = "reader";
    if (events[i].state === "writing") Sim.role[who] = "writer";
  }
  for (var j = 0; j < Sim.order.length; j++) {
    var nm = Sim.order[j];
    if (!Sim.role[nm]) {
      var ch = nm.charAt(0).toLowerCase();
      Sim.role[nm] = ch === "r" ? "reader" : (ch === "w" ? "writer" : "other");
    }
  }
}

function blank() {
  Sim.state = {};
  Sim.value = 0;
  for (var i = 0; i < Sim.order.length; i++) Sim.state[Sim.order[i]] = "thinking";
}

function cardHtml(name) {
  var st = Sim.state[name];
  var c = colorFor(st);
  return "<div class='actor' style='border-top-color:" + c + "'><b>" + name +
         "</b><em style='background:" + c + "'>" + st + "</em></div>";
}

function paint() {
  var rIn = 0, wIn = 0;
  var hr = "", hw = "", ho = "";

  for (var i = 0; i < Sim.order.length; i++) {
    var nm = Sim.order[i];
    var st = Sim.state[nm];
    if (st === "reading") rIn++;
    if (st === "writing") wIn++;
    var role = Sim.role[nm];
    if (role === "reader") hr += cardHtml(nm);
    else if (role === "writer") hw += cardHtml(nm);
    else ho += cardHtml(nm);
  }

  $("poolR").innerHTML = hr || "<span class='empty'>none</span>";
  $("poolW").innerHTML = hw || "<span class='empty'>none</span>";
  $("poolO").innerHTML = ho;
  $("otherCard").style.display = ho ? "block" : "none";

  var cls = "free", label = "FREE", col = "#94a3b8";
  if (wIn > 0 && (rIn > 0 || wIn > 1)) {
    cls = "conflict"; label = "CONFLICT: overlap detected"; col = "#ff2d55";
  } else if (wIn > 0) {
    cls = "locked"; label = "LOCKED by a writer (exclusive)"; col = "#fb7185";
  } else if (rIn > 0) {
    cls = "open"; label = "OPEN to " + rIn + " reader(s)"; col = "#34d399";
  }
  $("vault").className = "card vault " + cls;
  $("vBadge").textContent = label;
  $("vBadge").style.background = col;
  $("vVal").textContent = Sim.value;

  $("sStep").textContent = Sim.pos + " / " + events.length;
  $("sRead").textContent = rIn;
  $("sWrite").textContent = wIn;
  $("bar").style.width = (events.length ? (Sim.pos / events.length * 100) : 0) + "%";
}

function addLine(ev) {
  var row = document.createElement("div");
  row.className = "tl";
  row.setAttribute("data-state", ev.state);

  var txt = "<span class='t'>" + ev.time + "s</span>";
  txt += "<span class='dot' style='background:" + colorFor(ev.state) + "'></span>";
  txt += "<span>" + ev.who + " &rarr; <b>" + ev.state + "</b>";
  if (ev.note) txt += " <span class='note'>(" + ev.note + ")</span>";
  txt += "</span>";
  if (ev.value !== undefined) txt += "<span class='v'>value=" + ev.value + "</span>";
  row.innerHTML = txt;

  var box = $("timeline");
  box.appendChild(row);
  box.scrollTop = box.scrollHeight;

  if (!Sim.seen[ev.state]) {
    Sim.seen[ev.state] = true;
    var opt = document.createElement("option");
    opt.value = ev.state;
    opt.textContent = ev.state;
    $("filter").appendChild(opt);
  }
  applyFilter();
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
  var before = Sim.value;
  Sim.state[String(ev.who)] = ev.state;
  if (ev.value !== undefined) Sim.value = ev.value;
  Sim.pos++;
  $("sTime").textContent = ev.time + "s";
  addLine(ev);
  paint();

  if (Sim.value !== before) {
    var v = $("vVal");
    v.className = "val flash";
    setTimeout(function () { v.className = "val"; }, 400);
  }
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
    threads = []

    for reader_id in range(1, NUM_READERS + 1):
        threads.append(
            threading.Thread(target=reader, args=(reader_id,))
        )

    for writer_id in range(1, NUM_WRITERS + 1):
        threads.append(
            threading.Thread(target=writer, args=(writer_id,))
        )

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    make_html("readers_writers_semaphore.html")

    print("Finished. Final value =", shared_data)
    print("Events recorded:", len(events))
    print("Open readers_writers_semaphore.html in your browser.")


if __name__ == "__main__":
    main()
