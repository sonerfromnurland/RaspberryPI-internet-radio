#!/usr/bin/env python3

# Written by Limor "Ladyada" Fried for Adafruit Industries, (c) 2015
# This code is released into the public domain

import time
import os
from subprocess import call

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
DEBUG = 0


# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
    if ((adcnum > 7) or (adcnum < 0)):
        return -1
    GPIO.output(cspin, True)

    GPIO.output(clockpin, False)  # start clock low
    GPIO.output(cspin, False)  # bring CS low

    commandout = adcnum
    commandout |= 0x18  # start bit + single-ended bit
    commandout <<= 3  # we only need to send 5 bits here
    for i in range(5):
        if (commandout & 0x80):
            GPIO.output(mosipin, True)
        else:
            GPIO.output(mosipin, False)
        commandout <<= 1
        GPIO.output(clockpin, True)
        GPIO.output(clockpin, False)

    adcout = 0
    # read in one empty bit, one null bit and 10 ADC bits
    for i in range(11):
        GPIO.output(clockpin, True)
        GPIO.output(clockpin, False)
        adcout <<= 1
        if (GPIO.input(misopin)):
            adcout |= 0x1

    GPIO.output(cspin, True)

    return adcout


# change these as desired - they're the pins connected from the
# SPI port on the ADC to the Cobbler
SPICLK = 18
SPIMISO = 23
SPIMOSI = 24
SPICS = 25

# set up the SPI interface pins
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)

# 10k trim pot connected to adc #0
potentiometer_adc = 0

last_read = 0  # this keeps track of the last potentiometer value
tolerance = 5  # to keep from being jittery we'll only change
# volume when the pot has moved more than 5 'counts'

saved_set_volume = 0
set_volume = 50

while True:
    # we'll assume that the pot didn't move
    trim_pot_changed = False

    # read the analog pin
    trim_pot = readadc(potentiometer_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)
    # how much has it changed since the last read?
    pot_adjust = abs(trim_pot - last_read)

    if DEBUG:
        print("trim_pot:", trim_pot)
        print("pot_adjust:", pot_adjust)
        print("last_read", last_read)

    if (pot_adjust > tolerance):
        trim_pot_changed = True

    print("pod adjust: " + str(pot_adjust))
    print("tolerance: " + str(tolerance))

    if DEBUG:
        print("trim_pot_changed", trim_pot_changed)

    if (trim_pot_changed):
        set_volume = trim_pot / 10.24  # convert 10bit adc0 (0-1024) trim pot read into 0-100 volume level
        set_volume = round(set_volume)  # round out decimal value
        set_volume = int(set_volume)  # cast volume as integer

       # if abs(saved_set_volume - set_volume) < 3:
       #     continue

        if set_volume <= 90:
            set_volume += 1

            #print('Volume = {volume}%'.format(volume=set_volume))
            #amixer set PCM
            set_vol_cmd = 'amixer set PCM {volume}% > /dev/null'.format(volume=set_volume)
            # os.system(set_vol_cmd)  # set volume
            # cmd = "amixer -D pulse sset Master {volume}%".format(volume=set_volume)
            call(set_vol_cmd, shell=True)

            if DEBUG:
                print("set_volume", set_volume)
                print("tri_pot_changed", set_volume)

            # save the potentiometer reading for the next loop
            last_read = trim_pot
            saved_set_volume = set_volume
            # time.sleep(0.01)

        else:
            continue

    # hang out and do nothing for a half second

