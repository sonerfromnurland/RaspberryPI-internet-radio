#!/usr/bin/env python3

#soner test

import errno
import os
import smbus
import time
import subprocess

# Define some device parameters
I2C_ADDR = 0x27  # I2C device address
LCD_WIDTH = 20  # Maximum characters per line

# Define some device constants
LCD_CHR = 1  # Mode - Sending data
LCD_CMD = 0  # Mode - Sending command

LCD_LINE_1 = 0x80  # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0  # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94  # LCD RAM address for the 3rd line
LCD_LINE_4 = 0xD4  # LCD RAM address for the 4th line

LCD_BACKLIGHT = 0x08  # On
#LCD_BACKLIGHT = 0x00  # Off

ENABLE = 0b00000100  # Enable bit

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

# Open I2C interface
# bus = smbus.SMBus(0)  # Rev 1 Pi uses 0
bus = smbus.SMBus(1)  # Rev 2 Pi uses 1


def lcd_init():
    # Initialise display
    lcd_byte(0x33, LCD_CMD)  # 110011 Initialise
    lcd_byte(0x32, LCD_CMD)  # 110010 Initialise
    lcd_byte(0x06, LCD_CMD)  # 000110 Cursor move direction
    lcd_byte(0x0C, LCD_CMD)  # 001100 Display On,Cursor Off, Blink Off
    lcd_byte(0x28, LCD_CMD)  # 101000 Data length, number of lines, font size
    lcd_byte(0x01, LCD_CMD)  # 000001 Clear display
    time.sleep(E_DELAY)


def lcd_byte(bits, mode):
    # Send byte to data pins
    # bits = the data
    # mode = 1 for data
    #        0 for command

    bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
    bits_low = mode | ((bits << 4) & 0xF0) | LCD_BACKLIGHT

    # High bits
    bus.write_byte(I2C_ADDR, bits_high)
    lcd_toggle_enable(bits_high)

    # Low bits
    bus.write_byte(I2C_ADDR, bits_low)
    lcd_toggle_enable(bits_low)


def lcd_toggle_enable(bits):
    # Toggle enable
    time.sleep(E_DELAY)
    bus.write_byte(I2C_ADDR, (bits | ENABLE))
    time.sleep(E_PULSE)
    bus.write_byte(I2C_ADDR, (bits & ~ENABLE))
    time.sleep(E_DELAY)


def lcd_string(message, line):
    # Send string to display

    message = message.ljust(LCD_WIDTH, " ")

    lcd_byte(line, LCD_CMD)

    for i in range(LCD_WIDTH):
        lcd_byte(ord(message[i]), LCD_CHR)


def main():
    # Main program block

    # Initialise display
    lcd_init()

    FIFO = '/tmp/test2.fifo'

    try:
        os.mkfifo(FIFO)
    except OSError as oe:
        if oe.errno != errno.EEXIST:
            raise

    received = ''

    # count = 0
    while True:
        with open(FIFO) as fifo:
           # count += 1
           # print("FIFO opened   " + str(count) )
            while True:
                data = fifo.read()
                if len(data) == 0:
                   # print("Writer closed")
                    break
                #received = data
                print("data " + data)

                if 'General:' in data:
                    beforeRadioInformation(data + "-" + IPandSSID())

                if data.startswith("ERROR!! "):
                    urlERROR(data)
                elif 'internetproblem' in data:
                    print('internet problem girdi')
                    internetPROBLEM()
                elif 'internetssid' in data:
                    internetOKAY()
                elif '-1' or '-2' in data:
                    parser(data)

                #time.sleep(0.1)


"""
        # Send some test
        lcd_string("tirrek salih      <", LCD_LINE_1)
        lcd_string("operim            <", LCD_LINE_2)
        lcd_string("isiksizda         <", LCD_LINE_3)
        lcd_string("satir4            <", LCD_LINE_4)


        #LCD_BACKLIGHT = 0x00  # Off
        time.sleep(3)
"""

def urlERROR(str):
    lcd_string("URL Error !!", LCD_LINE_1)
    url = str.split(' ')[1].strip("\0\t\n\v\f\r ")
    lcd_string(url[:20], LCD_LINE_2)
    lcd_string(url[-(len(url[1]) - 20):], LCD_LINE_3)
    lcd_string("TRY CHANGING STATION", LCD_LINE_4)


def internetPROBLEM():
    lcd_string(' ://  NO', LCD_LINE_1)
    lcd_string('INTERNET CONNECTION', LCD_LINE_2)
    lcd_string('NO', LCD_LINE_3)
    lcd_string('             NO', LCD_LINE_4)

def internetSSID():
    result = subprocess.run(['sudo', 'iwgetid', '-r'], stdout=subprocess.PIPE)

    ## This line saves the output of the iwlist command as resultline ##
    resultline = str(result.stdout).strip('b\'')[:-2]



    return resultline

def IPandSSID():
    resultline = internetSSID()
    address = subprocess.check_output(['hostname', '-s', '-I']).decode('utf-8')[:-1]

    return 'SSID: ' + resultline + "-IP: " + address

def beforeRadioInformation(str):

    cleanGeneral = str.split("General: ")[1]
    channel = cleanGeneral.split("-")[0]
    lcd_string(channel, LCD_LINE_1)
    ssid = cleanGeneral.split("-")[1]
    ip = cleanGeneral.split("-")[2]
    if len(ssid) - 5 >= 20:
        lcd_string(ssid[:20], LCD_LINE_2)
        lcd_string(ssid[-(len(ssid) - 20):], LCD_LINE_3)
        lcd_string(ip, LCD_LINE_4)
    else:
        lcd_string(ssid, LCD_LINE_2)
        lcd_string(ip, LCD_LINE_3)
    time.sleep(4)


def internetOKAY():
    lcd_string(':) CONNECTED', LCD_LINE_1)
    str = 'SSID: ' + internetSSID()
    lcd_string(str[:20], LCD_LINE_2)
    lcd_string(str[-(len(str)-20):], LCD_LINE_3)
    lcd_string('Radio is on the way', LCD_LINE_4)
    time.sleep(2)

stationName = ''
def parser(input):
    global stationName
    artistName = ''
    trackName = ''

    if input.startswith('1-'):
        stationName = input[2:]
        #print(stationName)
    if input.startswith('2-'):
        trackAndArtistName = input[2:]
        #print(trackAndArtistName)
        if "-" in trackAndArtistName:
            arr = trackAndArtistName.split('-', 1)
            artistName = arr[0].strip()
            trackName = arr[1].strip()
        else:
            artistName = trackAndArtistName
            trackName = ''

    """
    print(arr[0])
    print(arr[1])

    print(arr[0].strip())
    print(arr[1].strip())
    """

    #print("station  " + stationName)



    #print("1.line " + stationName)
    lcd_string(stationName, LCD_LINE_1)
    # if len(trackName) > len(artistName):
    if len(trackName) > 20 and len(artistName) <= 20:
        lcd_string(artistName, LCD_LINE_2)
        lcd_string(trackName[:-len(trackName) + 20], LCD_LINE_3)
        lcd_string(trackName[20:], LCD_LINE_4)
        #print("2.line " + artistName)
        #print("3.line " + trackName[:-len(trackName) + 20])
        #print("4.line " + trackName[20:])
    elif (len(artistName) > 20 and len(trackName) <= 20)\
            or (len(artistName) > 20 and len(trackName) > 20):
        lcd_string(artistName[:-len(artistName) + 20], LCD_LINE_2)
        lcd_string(artistName[20:], LCD_LINE_3)
        lcd_string(trackName, LCD_LINE_4)
        #print("2.line " + artistName[:-len(artistName) + 20])
        #print("3.line " + artistName[20:])
        #print("4.line " + trackName)
    else:
        #lcd_string('', LCD_LINE_1)
        lcd_string(artistName, LCD_LINE_2)
        lcd_string(trackName, LCD_LINE_3)
        lcd_string(' ', LCD_LINE_4)
        #print("2.line " + artistName)
        #print("3.line " + trackName)


if __name__ == '__main__':

    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        lcd_byte(0x01, LCD_CMD)
