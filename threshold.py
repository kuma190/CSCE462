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
pod = []
prevSlope = None
prevV = None
#assumes that first edge is gonna be pos, so sets prev to neg.
prevEdge = "neg"
prevTime = 0
Max = -100
Min = 100
timeNow = time.time()
final =[] #stores every positive and negative edge and the time in between them.
processed = []
lens = [0,0] #lens[0] stores dit (1) duration, lens[1] stores dash (3) duration
lis = []
edges = []
threshold = 0

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
  
def getEdges():
  threshold = (max(lis) +min(lis))/2
  prevTime = 0
  print("threshold",threshold)
  for i in range(len(lis)-1):
    if lis[i] < threshold and lis[i+1] > threshold:
      update = ["posedge",i, i-prevTime]
      final.append(update)
      prevTime = i
    elif lis[i] > threshold and lis[i+1] < threshold:
      update = ["negedge",i, i-prevTime]
      final.append(update)
      prevTime = i
  #final = edges
    
      
  


def process():
  #translates positive and negative edges into ups and downs with their respective durations
  for i in range(len(final)-1):
    if final[i][0] == "posedge" and final[i+1][0] == "negedge":
      processed.append(["up",final[i+1][2]])
    elif final[i][0] == "negedge" and final[i+1][0] == "posedge":
      processed.append(["down",final[i+1][2]])
      
  for i in range(len(processed)):
    print("determining dit duration",i)
    
    #up can only have two lengths, 1 or 3. 
    if processed[i][0] == "up":
      #if dit duration is empty, populate it immediately
      if lens[0] == 0:
        lens[0] = processed[i][1]
      #if the current up duration is approximately the current dit duration divided by 3, 
      #make the dash duration that of the dit, and put this new value as dit duration
      elif processed[i][1] < lens[0]/2.5 and processed[i][1] > lens[0]/3.5:
        lens[1] = lens[0]
        lens[0] = processed[i][1]
        break
      #If current up is approx 3 times current dit duration, populate dash duration and exit
      elif processed[i][1]> lens[0]*2.5 and processed[1][1] < lens[0]*3.5:
        lens[1] = processed[i][1]
        break
  print(lens)
  unit = lens[0]
  
  #converts all the durations (up or down) into units (based on the dit duration)
  for i in range(len(processed)):
    #approx times 1
    if processed[i][1] > unit*0.5 and processed[i][1] < unit*1.5:
      processed[i].append(1)
    #approx times 3
    elif processed[i][1] > unit*2 and processed[i][1] < unit*5:
      processed[i].append(3)
    #approx times 7
    elif processed[i][1] > unit*6 and processed[i][1] < unit*9:
      processed[i].append(7)
    #none of the above 
    else:
      processed[i].append(-1)
  
  #uses the duration in terms of "units" to translate into morse code
  morse =""    
  for i in range(len(processed)):
    if processed[i][0] == "up":
      #dit
      if processed[i][2] == 1:
        morse += "."
        #dash
      elif processed[i][2] == 3:
        morse += "-"
        
    if processed[i][0] == "down":
      #interword space
      if processed[i][2] == 3:
          morse += " "
      #inter character space
      elif processed[i][2] == 7:
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
    
    
      
      
    
    
    
    

#when ctrl+C is pressed, everything is outputted for now.
def handler(signum, frame):
  #print(lis)
  getEdges()
  print(final)
  process()
  for i in final:
    print(i)
  print('\n')
  for i in processed:
    print(i)
  exit(1)
  
def handler1(signum, frame):
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
      #noise smoothing by taking data in pods of five and averaging it out
      avgV = statistics.mean(pod)
      pod = []
      lis.append(avgV)
      
      
      