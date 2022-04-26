import os
import time
import busio
import digitalio
import board
import statistics as stat
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
#from MorseToAnalog import decode

def decode(letter):
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
    for i in morseDict:
        if morseDict[i] == letter:
            return i
    return "NaN"

spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D22)
mcp = MCP.MCP3008(spi, cs)
chan0 = AnalogIn(mcp, MCP.P0)
prevv = 0
signals = list()
time_held = list()
digits = ''
threshold = .2
zero = 1
period = 1
if __name__ == "__main__":
  while(True):    
    v = chan0.voltage
    time.sleep(0.25)
    start = time.time()
    if v > abs(prevv + threshold) or v < abs(prevv - threshold):
      print(v)
      end = time.time()
      time_held = end-start
      if time_held > 2*period and v > 1:
        digits += '-'
      elif time_held < 2*period and v > 1:
        digits += '.'
      if time_held > 2*period and v < abs(zero):
        print(decode(digits))                
        digits = ''
      if time_held > 4*period and v < abs(zero):
        print(" ")
    prevv=v
        
    

      
