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
chan0 = AnalogIn(mcp, MCP.P0)
pod = []
prevSlope = None
prevV = None
prevEdge = "neg"
prevTime = 0
Max = -100
Min = 100
timeNow = time.time();
final =[];
processed = []
lens = [0,0]

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

def getChar(dits):
  for i in morseDict:
    if morseDict[i] == dits:
      return i
  return "?"

def process():
  for i in range(len(final)-1):
    if final[i][0] == "posedge" and final[i+1][0] == "negedge":
      processed.append(["up",final[i+1][2]])
    elif final[i][0] == "negedge" and final[i+1][0] == "posedge":
      processed.append(["down",final[i+1][2]])
      
  for i in range(len(processed)):
    print("determining dit duration",i)
    if processed[i][0] == "up":
      if lens[0] == 0:
        lens[0] = processed[i][1]
      elif processed[i][1] < lens[0]/2.5 and processed[i][1] > lens[0]/3.5:
        lens[1] = lens[0]
        lens[0] = processed[i][1]
        break
      elif processed[i][1]> lens[0]*2.5 and processed[1][1] < lens[0]*3.5:
        lens[1] = processed[i][1]
        break
  print(lens)
  unit = lens[0]
  
  for i in range(len(processed)):
    if processed[i][1] > unit*0.5 and processed[i][1] < unit*1.5:
      processed[i].append(1)
    elif processed[i][1] > unit*2 and processed[i][1] < unit*4:
      processed[i].append(3)
    elif processed[i][1] > unit*5 and processed[i][1] < unit*9:
      processed[i].append(7)
    else:
      processed[i].append(-1)
  
  morse =""    
  for i in range(len(processed)):
    if processed[i][0] == "up":
      if processed[i][2] == 1:
        morse += "."
      elif processed[i][2] == 3:
        morse += "-"
        
    if processed[i][0] == "down":
      if processed[i][2] == 3:
          morse += " "
      elif processed[i][2] == 7:
        morse += " / "
  print(morse)
  
  words = morse.split(" ")
  finalstream = ""
  for i in words:
    if i != "/":
      finalstream = finalstream+getChar(i)
    else:
      finalstream += " "
  print(finalstream)
    
    
      
      
    
    
    
    

def handler(signum, frame):
    process()
    for i in final:
      print(i)
    print('\n')
    for i in processed:
      print(i)
    exit(1)
 
signal.signal(signal.SIGINT, handler)
if __name__ == "__main__":
  while(True):
    v = chan0.voltage
    pod.append(v)
    if len(pod) == 5:
      avgV = statistics.mean(pod)
      pod = []
      if prevV == None:
        prevV = avgV
      elif prevSlope == None:
        prevSlope = avgV-prevV
        Max = prevSlope
      else:
        slope = avgV - prevV
        #print(prevSlope,slope,prevSlope-slope)
        if prevEdge == "neg":
          #print("testneg")
          #slope = avgV-prevV
          if slope > Max:
            Max = slope
          elif slope < prevSlope and abs(slope-prevSlope) > 0.04:# and slope > .1:
            
            if not len(final):
              prevTime = time.time()
            timeNow = time.time()
            update = ["posedge",timeNow, timeNow-prevTime,slope-prevSlope,slope,Max]
            final.append(update)
            prevTime = timeNow
            #print("posedge")
            #print(prevSlope,slope,prevSlope-slope,update)
            prevEdge = "pos"
            Max = -100
        if prevEdge == "pos":
          #print("testpos")
          #slope = avgV-prevV
          if slope < Min:
            Min = slope
          elif slope > prevSlope and abs(slope-prevSlope) > 0.04: # and slope > .1:
            
            if not len(final):
              prevTime = time.time()
            timeNow = time.time()
            update = ["negedge",timeNow, timeNow-prevTime,slope-prevSlope,slope,Min]
            final.append(update)
            prevTime = timeNow
            #print("negedge")
            #print(prevSlope,slope,prevSlope-slope,update)
            prevEdge = "neg"
            Min = 100
        prevSlope = slope
      prevV = avgV
