
Tested with:
PyInstaller: 3.4
Python: 2.7.14
Platform: Linux-4.12.14-lp150.12.82-default-x86_64-with-glibc2.2.5
Bottle: 0.12.19
Geckodriver: 0.29.1

DONE:
1) at the very top, it says "DQM [] Mirror". Could you say "DQM2 [] Mirror" instead ? (with superscript "2" if possible)
2) between the hostname/status display and a table of each client status, we need:
6) number of dqm client displayed. This number is in () next to the time stamp on top of the client list in P5 DQM

TODO:
3) I don't know what really happened, but I got in a mode that displaying "production" mode and "playback" mode alternating every ~ 7 sec or so, automatically.  I was clicking "production" and "playback" , then clicking some log files, when I got into that mode. 
5) a question: about a run# in playback system: The true run # of the run which playback is looking at is actually not run #501522, but it is whatever you have on a disk feeding into the playback system.

