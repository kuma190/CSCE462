import numpy as np
from MorseToAnalog import decode
import os
import time
import busio
import digitalio
import board
import signal
import statistics
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D22)
mcp = MCP.MCP3008(spi, cs)
chan0 = AnalogIn(mcp, MCP.P1)

np. set_printoptions(threshold=np. inf)
data = []
def decode(letter):
    morseDict = {
        '.-': 'A',
        '-...': 'B',
        '-.-.': 'C',
        '-..': 'D',
        '.': 'E',
        '..-.': "F",
        '--.': "G",
        '....': "H",
        '..': "I",
        '.---': "J",
        '-.-': "K",
        '.-..': "L",
        "--": "M",
        '-.': "N",
        '---': "O",
        '.--.': "P",
        '--.-': 'Q',
        '.-.': "R",
        '...': "S",
        '-': 'T',
        '..-': 'U',
        '...-': "V",
        '.--': "W",
        '-..-': "X",
        '-.--': "Y",
        '--..': "Z",
        ".----": "1",
        "..---": "2",
        '...--': '3',
        '....-': '4',
        '.....': '5',
        '-....': '6',
        '--...': '7',
        '---..': '8',
        '----.': '9',
        '-----': '0'
    }
    return morseDict.get(letter)

def LightAnalyze():
    words = ''
    null_count = 0
    num_count = 0
    morse_list = []
    null_list = []
    space_list = []
    tolerance = 10
    final_string = ""

    on = max(data)
    off = min(data)
    _tol = .1
    for x in data:
        if off - _tol < x < off + _tol:
            if num_count!=0:
                morse_list.append(num_count)
            num_count = 0
            null_count += 1
        elif on - _tol < x < on + _tol:
            if null_count!=0:
                null_list.append(null_count)
            null_count = 0
            num_count += 1
    null_list = null_list[1:]
    print(null_list)
    print(morse_list)
    dot = min(morse_list)
    dash = max(morse_list)
    mean = (dot + dash)/2
    for x in morse_list:
        if mean > x:
            words += '.'
        elif x > mean:
            words += '-'
    no_space = min(null_list)
    word_space = max(null_list)
    letter_space = 3 * no_space
    if letter_space + 3*no_space > word_space:
        word_space = np.inf
    noTOletter = (no_space + letter_space)/2
    letterTOword = (word_space + letter_space)/2
    print(noTOletter, letterTOword)
    number = 0
    for x in range(len(null_list)):
        if noTOletter > null_list[x]:
            space_list.append('')
        elif letterTOword < null_list[x]:
            space_list.append('  ')
        else:
            space_list.append(' ')

    for x in range(len(space_list)):
        final_string+=words[x]
        final_string+=space_list[x]
        if x == len(space_list)-1:
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

def handler(signum, frame):
    LightAnalyze()
    exit(1)

signal.signal(signal.SIGINT, handler)
if __name__ == "__main__":
  while True:
    v = chan0.voltage
    data.append(v)