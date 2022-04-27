import os
import numpy as np
import time
import busio
import digitalio
import board
import signal
import statistics as s
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
from LightMaxMin import decode
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D22)
mcp = MCP.MCP3008(spi, cs)
chan0 = AnalogIn(mcp, MCP.P0)
vals = []
updownarray = []
lens = [0, 0]
activeup = False
activedown = False
startTimedown = None
endTimedown = None
startTimeup = None
endTimeup = None
morseDict = {
    'A': '.-',
    'B': '-...',
    'C': '-.-.',
    'D': '-..',
    'E': '.',
    'F': "..-.",
    'G': "--.",
    'H': "....",
    'I': "..",
    'J': ".---",
    'K': "-.-",
    'L': ".-..",
    "M": "--",
    'N': "-.",
    'O': "---",
    'P': ".--.",
    'Q': '--.-',
    'R': ".-.",
    'S': "...",
    'T': '-',
    'U': '..-',
    'V': "...-",
    'W': ".--",
    'X': "-..-",
    'Y': "-.--",
    'Z': "--..",
    "1": ".----",
    "2": "..---",
    '3': '...--',
    '4': '....-',
    '5': '.....',
    '6': '-....',
    '7': '--...',
    '8': '---..',
    '9': '----.',
    '0': '-----'
}


def process(updownarray):
    uptimes = []
    downtimes = []
    updownarray = updownarray[1:]
    for i in range(len(updownarray)):
        # up can only have two lengths, 1 or 3.
        if updownarray[i][0] == "up":
            # if dit duration is empty, populate it immediately
            if lens[0] == 0:
                lens[0] = updownarray[i][1]
            # if the current up duration is approximately the current dit duration divided by 3,
            # make the dash duration that of the dit, and put this new value as dit duration
            elif updownarray[i][1] < lens[0] / 2.5 and updownarray[i][1] > lens[0] / 3.5:
                lens[1] = lens[0]
                lens[0] = updownarray[i][1]
                break
            # If current up is approx 3 times current dit duration, populate dash duration and exit
            elif updownarray[i][1] > lens[0] * 2.5 and updownarray[1][1] < lens[0] * 3.5:
                lens[1] = updownarray[i][1]
                break


    for x in updownarray:
        if x[0] == "up":
            uptimes.append(x[1])
        else:
            downtimes.append(x[1])
    print(uptimes, downtimes)
    dot = max(uptimes)
    dash = min(uptimes)
    words = ""
    spaces = []
    mean = (dot + dash) / 2
    no_space = min(downtimes)
    word_space = max(downtimes)
    final_string = ""
    letter_space = 3 * no_space
    if letter_space * 2 > word_space:
        word_space = np.inf
    noTOletter = (no_space + letter_space) / 2
    letterTOword = (word_space + letter_space) / 2
    for x in uptimes:        
        if mean > x:
            words += '.'
        elif x > mean:
            words += '-'
    for x in downtimes:
        if x > letterTOword:
            spaces.append('  ')
        elif x < noTOletter:
            spaces.append('')
        else:
            spaces.append(' ')
    print(words, spaces)
    for x in range(len(spaces)):
        final_string+=words[x]
        final_string+=spaces[x]
        if x == len(spaces)-1:
            final_string += words[x+1]
    print(final_string)
    word_list = final_string.split('  ')
    letter_list = []
    for x in word_list:
        letter_list.append(x.split(' '))
    decoded_letters = []
    for x in letter_list:
        for y in x:
            decoded_letters.append(decode(y))

        decoded_letters.append(' ')
    response = ""
    for x in decoded_letters:
        response+=x
    print(response)
    print(words)
    # converts all the durations (up or down) into units (based on the dit duration)

    print(updownarray)


def getChar(dits):
    for i in morseDict:
        if morseDict[i] == dits:
            return i
    return "?"


def handler(signum, frame):
    process(updownarray)
    exit(1)


signal.signal(signal.SIGINT, handler)
if __name__ == "__main__":
    timeAr = [0, 0]
    while True:
        v = chan0.voltage
        vals.append(v)
