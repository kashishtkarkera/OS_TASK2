# AI Prompt Log

Student: Kashish USN: NNM24IS102 AI tool used: Claude (Anthropic), through the chat interface on claude.ai Assignment: Operating Systems - AI-Assisted Synchronization and Visualization

## Initial prompt
I uploaded the assignment PDF and told Claude that I had not read all six pages and did not know where to begin. I asked it to explain what the assignment is about, describe the format and the deliverables, and then give me the code one program at a time. I also asked for code that is simple and easy to read, so that I could follow it and explain it myself.

## Follow-up prompts
1. Asked for the exact folder structure and a clear list of what to do, in order, to finish before the deadline.
2. Asked how to run dp_monitor.py. My first attempts failed with a "can't open file" error because I was in the wrong folder, so I also asked what "unzip" means and how to reach the extracted folder in PowerShell. After that the program ran correctly.
3. Uploaded another student's report as a layout reference only, and asked Claude to write a report draft of my own based on my code, in original wording, plus keywords for searching Google Scholar.
4. Asked which headings in the draft were not required by the assignment, and whether the variable names used in the report match the code.
5. Asked Claude to fill in the execution-trace section of the report, then asked for a simple paragraph explaining a trace taken from my own run.
6. Asked Claude to prepare this prompt log.

## What I changed manually
Added my name and USN to the README and the report.
Ran dp_monitor.py on my own computer (Windows, Python 3.14) and opened the HTML page it generated.
[Ran the other three programs and opened their HTML pages - delete if not done]
[Took the screenshots in the report from my own runs - delete if not done]
[Replaced the sample trace lines with lines from my own run for: ... - fill in or delete]
[Reworded parts of the report in my own words and changed: ... - fill in]
[Changed values such as the number of readers or the delays and ran the programs again - delete if not done]

## One error / limitation I noticed
Starvation is hard to see in practice. Each thread only runs a few rounds, so even the versions where starvation is possible always finish. A run that completes tells me little about fairness, so I had to explain starvation by reasoning about the code and not from the output.
Replay timing. The HTML page moves from one event to the next at a fixed interval set by the speed box. The real gaps between events are not shown, so a long wait in the program looks the same as a short one. Using the recorded timestamps to space out the replay would fix this.
Event order within a millisecond. The log call is placed just before or just after each synchronization operation, so two events with almost the same timestamp may not appear in exactly their true order.
Reader preference vs writer preference. The semaphore version can keep a writer waiting while readers keep coming (I saw a writer wait for over a second in one run), while the monitor version avoids this but could in theory delay readers. Neither one is completely fair.
