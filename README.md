# OS Synchronization Assignment - Readers-Writers & Dining Philosophers

Readers-Writers and Dining Philosophers, each solved with semaphores and with a monitor, written in Python. Every program records what its threads do while it runs and then writes an HTML page that replays that recorded run in a browser.

| | |
|---|---|
| **Student** | KASHISH |
| **USN** | NNM24IS102 |
| **Course** | Operating Systems |

## What is in this repository

| # | Problem | Method | Source file |
|---|---------|--------|-------------|
| 1 | Readers-Writers | Semaphores (`mutex` and `resource`), readers get preference | `readers_writers/semaphore/rw_semaphore.py` |
| 2 | Readers-Writers | Monitor class with a lock and two condition variables, writers get preference | `readers_writers/monitor/rw_monitor.py` |
| 3 | Dining Philosophers (4) | One semaphore per fork plus a `room` semaphore set to 3 | `dining_philosophers/semaphore/dp_semaphore.py` |
| 4 | Dining Philosophers (4) | Monitor class that hands out both forks in one step | `dining_philosophers/monitor/dp_monitor.py` |

Other folders:

- `generated_html/` holds the four HTML pages produced by the programs
- `screenshots/` holds my terminal and browser screenshots
- `ai_prompts/prompts.md` is the log of my AI prompts
- `references/references.md` lists the sources I used
- `report/` holds the written report

Each program is a single self-contained file. They do not import each other.

## What each program does

**Readers-Writers (semaphore).** Several reader threads and writer threads share one integer. Readers can read together, a writer needs the data to itself. The first reader locks the data for the group of readers and the last one unlocks it.

**Readers-Writers (monitor).** The same problem, but the rules sit inside a `ReadWriteMonitor` class. Threads wait on condition variables until it is safe to enter. Waiting writers are served before new readers.

**Dining Philosophers (semaphore).** Four philosophers share four forks. To avoid deadlock, at most three of them may try to pick up forks at the same time.

**Dining Philosophers (monitor).** A `TableMonitor` class lets a philosopher eat only when both neighbours are not eating, and gives him both forks together.

## Requirements

- Python 3 (I used 3.14 on Windows)
- No extra libraries. Only `threading`, `time`, `random` and `json` from the standard library are used.
- Any web browser, to open the generated pages

There is nothing to compile or install.

## How to run

Open a terminal inside the folder of the program you want, then run it. For example:

```
cd dining_philosophers/monitor
python dp_monitor.py
```

The four commands are:

```
python rw_semaphore.py      (inside readers_writers/semaphore)
python rw_monitor.py        (inside readers_writers/monitor)
python dp_semaphore.py      (inside dining_philosophers/semaphore)
python dp_monitor.py        (inside dining_philosophers/monitor)
```

On Mac or Linux use `python3` instead of `python`.

The programs finish by themselves after a few seconds. If one of them ever hangs, that would mean a deadlock.

### Changing the settings

The values at the top of each file can be edited and the program run again:

- Readers-Writers: `NUM_READERS`, `NUM_WRITERS`, `ROUNDS`, `MAX_DELAY`
- Dining Philosophers: `ROUNDS`, `MAX_DELAY` (`NUM` is fixed at 4)

## Generating and viewing the HTML simulation

Running a program is also how the HTML is generated. When the threads have finished, the program writes its page into the folder it was run from, with one of these names:

- `readers_writers_semaphore.html`
- `readers_writers_monitor.html`
- `dining_philosophers_semaphore.html`
- `dining_philosophers_monitor.html`

Double-click the file (or open it in Chrome or Firefox) and press **Start**. The page has Pause and Reset buttons and a box for the replay speed. Running the program again creates a new page from a new run, because the delays are random.

Copies of the pages from my runs are kept in `generated_html/`.

## Expected output

At the end of a Readers-Writers run the terminal shows something like:

```
Finished. Final value = 6
Events recorded: 60
Open readers_writers_semaphore.html in your browser.
```

(6 is two writers times three rounds.) A Dining Philosophers run shows:

```
Finished. Every philosopher ate 3 times, no deadlock.
Events recorded: 60
Open dining_philosophers_monitor.html in your browser.
```

The number of events can differ slightly between programs.

## Screenshots

The `screenshots/` folder contains the terminal output and the browser view for each of the four programs. [ADD YOUR SCREENSHOTS BEFORE SUBMITTING]

## How the simulation is made

While a program runs, its threads call a `log()` function whenever their state changes. Each call stores the time, who changed, the new state and, for the philosophers, who holds each fork. After all threads have finished, the list of events is converted to JSON and placed inside an HTML template. JavaScript in the page then steps through the events one by one and redraws the screen. Nothing in the page is scripted by hand, so it always reflects the run that produced it.

## Known limitations

- The replay moves at a fixed interval, so the real gaps between events are not visible (the real times appear in the log box).
- Python does not promise that waiting threads are served in order, so starvation cannot be completely ruled out in any version.
- In the semaphore Readers-Writers program, writers can be kept waiting for a long time while readers keep arriving.
- In the monitor Readers-Writers program, readers can be delayed if writers keep arriving.
- In the monitor Dining Philosophers program, a philosopher could in theory be skipped repeatedly if both neighbours keep taking turns.

## AI tools used

Claude (Anthropic) helped with planning, code, explanations and the report draft. The prompts are in [`ai_prompts/prompts.md`](ai_prompts/prompts.md).

## References and acknowledgements

See [`references/references.md`](references/references.md).
