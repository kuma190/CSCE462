import os
import time
import busio
import digitalio
import board
import statistics as stat
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D22)
mcp = MCP.MCP3008(spi, cs)
chan0 = AnalogIn(mcp, MCP.P0)

if __name__ == "__main__":
  while(True):
      v = chan0.voltage
      time.sleep(0.5)
      print(v)
