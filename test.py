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
while True: 
    v = chan0.voltage
    vals.append(v)
    if len(vals) >= 10:
        dev = s.stdev(vals) 
        vals = []
        if (dev > 0.009 and activedown): 
            endTimedown = time.time()  
            updownarray.append(["down", endTimedown-startTimedown])
            activedown = False
        elif dev > 0.009: 
            startTimeup = time.time()
            activeup = True
        elif (dev < 0.009 and activeup):
            print(dev)
            endTimeup = time.time()
            updownarray.append(["up", endTimeup-startTimeup])
            activeup = False
        elif (dev < 0.009):
            startTimedown = time.time()
            activedown = True 
        print(updownarray)