import os
import time
import busio
import digitalio
import board
import signal
import statistics as s
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D22)
mcp = MCP.MCP3008(spi, cs)
chan0 = AnalogIn(mcp, MCP.P0)
vals = []
updownarray = []
lens = [0,0]
activeup = False
activedown = False
startTimedown = None
endTimedown = None
startTimeup = None 
endTimeup = None
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
def process() :
    for i in range(len(updownarray)):
      #up can only have two lengths, 1 or 3. 
      if updownarray[i][0] == "up":
      #if dit duration is empty, populate it immediately
        if lens[0] == 0:
          lens[0] = updownarray[i][1]
        #if the current up duration is approximately the current dit duration divided by 3, 
        #make the dash duration that of the dit, and put this new value as dit duration
        elif updownarray[i][1] < lens[0]/2.5 and updownarray[i][1] > lens[0]/3.5:
          lens[1] = lens[0]
          lens[0] = updownarray[i][1]
          break
        #If current up is approx 3 times current dit duration, populate dash duration and exit
        elif updownarray[i][1]> lens[0]*2.5 and updownarray[1][1] < lens[0]*3.5:
          lens[1] = updownarray[i][1]
          break
    unit = lens[0]
    print(unit)
      
    #converts all the durations (up or down) into units (based on the dit duration)
    for i in range(len(updownarray)):
      #approx times 1
      if updownarray[i][1] > unit*0.5 and updownarray[i][1] < unit*1.5:
        updownarray[i].append(1)
      #approx times 3
      elif updownarray[i][1] > unit*2 and updownarray[i][1] < unit*5:
        updownarray[i].append(3)
      #approx times 7
      elif updownarray[i][1] > unit*5 and updownarray[i][1] < unit*9:
        updownarray[i].append(7)
      #none of the above 
      else:
        updownarray[i].append(-1)
          
    #uses the duration in terms of "units" to translate into morse code
    morse =""    
    for i in range(len(updownarray)):
      if updownarray[i][0] == "up":
        #dit
        if updownarray[i][2] == 1:
          morse += "."
          #dash
        elif updownarray[i][2] == 3:
          morse += "-"
          
      if updownarray[i][0] == "down":
        #interword space
        if updownarray[i][2] == 3:
            morse += " "
        #inter character space
        elif updownarray[i][2] == 7:
          morse += " / "
    print(morse)
    
    #uses morse code to translate into english
    words = morse.split(" ")
    finalstream = ""
    for i in words:
      if i != "/":
        finalstream = finalstream+getChar(i)
      else:
        finalstream += " "
    print(finalstream)
    print(updownarray)


def getChar(dits):
  for i in morseDict:
    if morseDict[i] == dits:
      return i
  return "?"

def handler(signum, frame) :
  process()
  exit(1)

signal.signal(signal.SIGINT, handler)
if __name__ == "__main__":
  timeAr = [0, 0]
  while True: 
      v = chan0.voltage
      vals.append(v)
      if len(vals) >= 10:
          dev = s.stdev(vals) 
          vals = []
          if (dev > 0.009 and activedown): 
              if timeAr[1] == 0: 
                timeAr[1] = time.time() 
              updownarray.append(["down", timeAr[1]-timeAr[0]])
              activedown = False
              timeAr = [0,0] 
          elif dev > 0.009: 
              if timeAr[0] == 0: 
                timeAr[0] = time.time()
              activeup = True 
          elif (dev < 0.009 and activeup):
              if timeAr[1] == 0: 
                timeAr[1] = time.time()
              updownarray.append(["up", timeAr[1]-timeAr[0]])
              activeup = False
              timeAr = [0,0] 
          elif (dev < 0.009):
              if timeAr[0] == 0: 
                timeAr[0] = time.time()
              activedown = True 
          