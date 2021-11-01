# https://github.com/cms-DQM/dqmgui_prod/blob/index128/bin/visDQMSoundAlarmDaemon

SOUNDSERVER = "daq-expert.cms"
PORT = 50555
MSGBODY = ('<CommandSequence><alarm sender="DQM" sound="DQM_1.wav" talk="DQM test alarm">DQM test alarm.</alarm></CommandSequence>')

from socket import socket, AF_INET, SOCK_STREAM, gethostname
s = socket(AF_INET, SOCK_STREAM)
s.connect((SOUNDSERVER, PORT))
s.send(MSGBODY)
data = s.recv(1024)
print(data, data == "All ok\n")
s.close()
