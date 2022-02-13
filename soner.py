#!/usr/bin/env python3

# yedek ssh pycharm

# KY040 Python Class
# Martin O'Hanlon
# stuffaboutcode.com
import errno
import os
import signal
import subprocess
import time
import socket

import RPi.GPIO as GPIO
from time import sleep


import radyoCS


GPIO.setmode(GPIO.BCM)

### PINS ###
CLOCKPIN = 16
DATAPIN = 15
SWITCHPIN = 14

# setup pins
GPIO.setup(CLOCKPIN, GPIO.IN)
GPIO.setup(DATAPIN, GPIO.IN)
GPIO.setup(SWITCHPIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)


MIN_LIMIT_CHANNEL = 0
MAX_LIMIT_CHANNEL = radyoCS.NUM_OF_LINES_IN_URL_TXT - 1


# for testing purpose, it is actually 0
counter = 2

flag = 0



signal.signal(signal.SIGCHLD, signal.SIG_IGN)


def internetExist(host="8.8.8.8", port=53, timeout=2):
   """
   Host: 8.8.8.8 (google-public-dns-a.google.com)
   OpenPort: 53/tcp
   Service: domain (DNS/TCP)
   """
   try:
     socket.setdefaulttimeout(timeout)
     socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
     return True
   except Exception as ex:
     #print (ex.message)
     return False

def pid_exists(pid):
    if os.path.isdir('/proc/{}'.format(pid)):
        return True
    return False

'''
def show_waitpid_results(results):
    print("results: %s" % (str(results)))
    print("core: %r continued: %r stopped: %r signaled: %r exited %r" %
        (
            os.WCOREDUMP(results[1]),
            os.WIFCONTINUED(results[1]),
            os.WIFSTOPPED(results[1]),
            os.WIFSIGNALED(results[1]),
            os.WIFEXITED(results[1]))
        )
    if os.WIFEXITED(results[1]):
        print("exit code: %r" % (os.WEXITSTATUS(results[1])))
'''

mplayerProcess = None

try:
    while True:
        signal.signal(signal.SIGCHLD, signal.SIG_IGN)
        # if file is updated
        MAX_LIMIT_CHANNEL = radyoCS.NUM_OF_LINES_IN_URL_TXT - 1

        if not internetExist():
            fifo = open(radyoCS.path, "w")
            fifo.write('internetproblem')
            fifo.close()
            while True:
                if internetExist():
                    print("internet geldi")
                    fifo = open(radyoCS.path, "w")
                    fifo.write('internetssid')
                    fifo.close()
                    break

        if not flag:
            print("pid -> " + str(os.getpid()))
            flag = 1

        # put list number, ssid and ip onto screen when switched over
        fifo = open(radyoCS.path, "w")
        channel = 'Channel: ' + str(counter) + ' / ' + str(MAX_LIMIT_CHANNEL)
        fifo.write("General: " + channel)
        fifo.close()

        pid = os.fork()


        if pid == 0:

            print("i'm child my pid => " + str(os.getpid()) + "my parent => " + str(os.getppid()))
            if mplayerProcess is not None:
                mplayerProcess.terminate()
                mplayerProcess.wait()
            mplayerProcess = radyoCS.playStation(counter)
            #print(counter)

            ### normally playStation does work, control is takeovered by '''mplayer''' !!!!
            #time.sleep(20)
            #print("cocuk ciakr mi")
            while True:
                pass
        else:
            ### wait until rotary switcher turns
            """
            clock = GPIO.input(CLOCKPIN)
            data = GPIO.input(DATAPIN)
            print("clock before" + str(data))
            print("data before" + str(data))
            #sleep(1)
            #while clock == 1 or clock == 0:
            #print("clock before" + str(clock))
            """

            GPIO.wait_for_edge(CLOCKPIN, GPIO.FALLING)
            data = GPIO.input(DATAPIN)
            sleep(0.5)

            """
            clock = GPIO.input(CLOCKPIN)
            print("clock after" + str(data))
            print("data after" + str(data))
            """


            ### stop current child to create new child
            ### stop currently playing radio station to change to new station
            print("soner---->>>>>    " + str(pid))
            if pid_exists(pid):
                os.kill(pid, signal.SIGTERM)
            #while os.waitpid(pid, 0) == (0, 0):
            #    sleep(0.01)
            #os.waitpid(pid, 0)
            #waitpid_result = os.waitpid(pid, os.WNOHANG)
            #show_waitpid_results(waitpid_result)

            print("i'm waiting, value t > " + str(counter))





            ### We have 5 radio stations, if data==1 turned counter clokwise, otherwise clockwise
            if data == 1:   #  clokwise
                if counter == MAX_LIMIT_CHANNEL:
                    counter = MIN_LIMIT_CHANNEL - 1
                counter += 1
            else:           # counter clockwise
                if counter == MIN_LIMIT_CHANNEL:
                    counter = MAX_LIMIT_CHANNEL + 1
                counter -= 1


finally:
    GPIO.cleanup()