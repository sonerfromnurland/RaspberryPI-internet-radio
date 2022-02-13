#!/usr/bin/env python3
import errno
import os

import re
import subprocess
import pathlib

### READ RADIO STATIONS FROM FILE AT FIRST ###

playlist = ["m3u", "pls", "asx"]

f = open('/home/pi/Desktop/project_home/urls.txt', 'r')
stations = [line for line in f.readlines()]
f.close()

print('\n'.join(str(p) for p in stations))
NUM_OF_LINES_IN_URL_TXT = sum(1 for p in stations)
#print("soner test count: " + str(count))



path = "/tmp/test2.fifo"

"""
p = pathlib.Path(path)
if p.exists():
    print("fifo exist and is about to be removed!")
    os.unlink(path)
else:
    print("not found")
"""

try:
    os.mkfifo(path)
except OSError as oe:
    if oe.errno != errno.EEXIST:
        raise


### FUNCTIONS ###
def playStation(i):
    #global p
    killMPlayer = "killall mplayer"
    #subprocess.call(killMPlayer)
    os.system(killMPlayer)
    print("PlayStation gelen deger ->>>  " + str(i))
    if any(x in stations[i] for x in playlist):
        radioName = 'mplayer ' + '-prefer-ipv4 ' + '-playlist ' + stations[i]
        p = subprocess.Popen(radioName.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    else:
        radioName = 'mplayer ' + '-prefer-ipv4 ' + stations[i]
        p = subprocess.Popen(radioName.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)



    for line in p.stdout:
        fifo = open(path, "w")
        if line.startswith(('ICY Info:'.encode(), 'Name'.encode())):
            if 'Name'.encode() in line:
                nameStr = str(line)
                searchRadioName = re.search(r'(?<=:\s).*?(?=\\n)', nameStr, re.M | re.I)
                if searchRadioName:
                    print(searchRadioName.group())
                    fifo.write("1-" +  searchRadioName.group())


            if 'ICY Info:'.encode() in line:
                trackStr = str(line)
                searchTrackName = re.search(r'(?<=\=\').*?(?=\';)', trackStr, re.M | re.I)
                if searchTrackName:
                    print(searchTrackName.group())
                    fifo.write("2-" +  searchTrackName.group())


        else:
            if 'Error while opening playlist'.encode() in line \
                    or 'No stream found to handle url'.encode() in line:

                print("ERROR!!" + " " + stations[i])
                fifo.write("ERROR!!" + " " + stations[i])
                print("fifo kapanacak")



        print("read: " + str(line.decode("UTF-8")))
        fifo.close()
    return p
