import signal
import sys
from gpiozero import LED
from time import sleep
from multiprocessing import Process
import multiprocessing
from datetime import datetime
import math
from gpiozero import Button
import board
import busio
import adafruit_mcp4725
i2c = busio.I2C(board.SCL, board.SDA)
dac = adafruit_mcp4725.MCP4725(i2c)
MAX_VOLTS = 3.3
SCALE = 4095
REST = 0.5
HERTZ = 10

morseDict = {
    'A':'.-',
    'B':'-...',
    'C':'-.-.',
    'D':'-..',
    'E':'.',
    'F':"..-.",
    'G':"--.",
    'H':"....",
    'I':"..",
    'J':".---",
    'K':"-.-",
    'L':".-..",
    "M":"--",
    'N':"-.",
    'O':"---",
    'P':".--.",
    'Q':'--.-',
    'R':".-.",
    'S':"...",
    'T':'-',
    'U':'..-',
    'V':"...-",
    'W':".--",
    'X':"-..-",
    'Y':"-.--",
    'Z':"--..",
    "1":".----",
    "2":"..---",
    '3':'...--',
    '4':'....-',
    '5':'.....',
    '6':'-....',
    '7':'--...',
    '8':'---..',
    '9':'----.',
    '0':'-----'
}

# def square_wave(hertz,ampVolt,units):
#     #print("initiating square_wave",hertz,ampVolt)
#     rest = 0.5/hertz
#     t = 0.0
#     MAX = 4090*(ampVolt/MAX_VOLTS)
#     tStep = 0.0005
#     prevV = 0.0
#     before = datetime.now().timestamp()
#     while True:
#         if prevV == 0:
#             voltage = MAX
#             prevV = MAX
#         elif prevV == MAX:
#             voltage = 0
#             prevV = 0
#         dac.raw_value = int(voltage)
#         #if int(voltage) == MAX:
#            # now = datetime.now().timestamp()
#            # offset = now-before
#            # print(offset)
#         #t+= rest
#         sleep(rest)
def highSig(units):
    MAX = MAX_VOLTS
    voltage = SCALE
    rest = 0.5/HERTZ
    dac.raw_value = int(voltage)
    print(dac.raw_value)
    for i in range(units):
        sleep(rest)
    #  for i in range(units):
    #     print("-", end='')
def lowSig(units):
    rest = 0.5/HERTZ
    dac.raw_value = 0
    print(dac.raw_value)
    for i in range(units):
        sleep(rest)
    # for i in range(units):
    #     print("_", end='')

def dot():
    highSig(1)
    lowSig(1)

def dash():
    highSig(3)
    lowSig(1)

def charSpace():
    lowSig(2)

def wordSpace():
    lowSig(4)

def wordsToMorse(words):
    wordArr = words.split()
    for i in range(len(wordArr)):
        word = wordArr[i]
        for char in word:
            for d in morseDict[char.upper()]:
                if d == ".":
                    dot()
                elif d == "-":
                    dash()
            charSpace()
        if i != len(wordArr)-1:
            wordSpace()



if __name__ == '__main__':
    wordsToMorse("Zebras are blue")
