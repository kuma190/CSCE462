import pyaudio
import numpy
p = pyaudio.PyAudio()
for ii in range(p.get_device_count()):
  print(ii,p.get_device_info_by_index(ii).get('name'),p.get_device_info_by_index(ii).get('maxInputChannels'),p.get_device_info_by_index(ii).get('defaultSampleRate'))