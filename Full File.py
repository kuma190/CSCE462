from scipy.io import wavfile
import sys
import numpy as np
import os
import time
import busio
import digitalio
import board
import signal
import statistics as s
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import wave
import pyaudio


spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D22)
mcp = MCP.MCP3008(spi, cs)
chan0 = AnalogIn(mcp, MCP.P0)
CHUNK = 4096
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
dev_index = 0
vals = []
updownarray = []
lens = [0,0]
activeup = False
activedown = False
startTimedown = None
endTimedown = None
startTimeup = None
endTimeup = None
np. set_printoptions(threshold=np. inf)
data = []
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

def record():
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, input_device_index=dev_index,
                    frames_per_buffer=CHUNK)

    print("Start recording")

    frames = []

    try:
        while True:
            data = stream.read(CHUNK)
            frames.append(data)
    except KeyboardInterrupt:
        print("Done recording")
    except Exception as e:
        print(str(e))

    sample_width = p.get_sample_size(FORMAT)

    stream.stop_stream()
    stream.close()
    p.terminate()

    return sample_width, frames

def record_to_file(file_path):
    wf = wave.open(file_path, 'wb')
    wf.setnchannels(CHANNELS)
    sample_width, frames = record()
    wf.setsampwidth(sample_width)
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def process():
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
    unit = lens[0]
    print(unit)

    # converts all the durations (up or down) into units (based on the dit duration)
    for i in range(len(updownarray)):
        # approx times 1
        if updownarray[i][1] > unit * 0.5 and updownarray[i][1] < unit * 1.5:
            updownarray[i].append(1)
        # approx times 3
        elif updownarray[i][1] > unit * 2 and updownarray[i][1] < unit * 5:
            updownarray[i].append(3)
        # approx times 7
        elif updownarray[i][1] > unit * 5 and updownarray[i][1] < unit * 9:
            updownarray[i].append(7)
        # none of the above
        else:
            updownarray[i].append(-1)

    # uses the duration in terms of "units" to translate into morse code
    morse = ""
    for i in range(len(updownarray)):
        if updownarray[i][0] == "up":
            # dit
            if updownarray[i][2] == 1:
                morse += "."
                # dash
            elif updownarray[i][2] == 3:
                morse += "-"

        if updownarray[i][0] == "down":
            # interword space
            if updownarray[i][2] == 3:
                morse += " "
            # inter character space
            elif updownarray[i][2] == 7:
                morse += " / "
    print(morse)

    # uses morse code to translate into english
    words = morse.split(" ")
    finalstream = ""
    for i in words:
        if i != "/":
            finalstream = finalstream + getChar(i)
        else:
            finalstream += " "
    print(finalstream)
    print(updownarray)

def getChar(dits):
    for i in morseDict:
        if morseDict[i] == dits:
            return i
    return "?"

def decode(letter):
    return morseDict.get(letter)

def LightAnalyze():
    #define variables to later use
    words = ''
    null_count = 0
    num_count = 0
    morse_list = []
    null_list = []
    space_list = []
    tolerance = 10
    final_string = ""
    #find when sound is being produced and when it is silent (average values within a tolerance)
    on = max(data)
    off = min(data)
    _tol = (on-off)*.2
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

def SoundAnalyzer():
    samplerate, data = wavfile.read('outpu.wav')
    #variables
    string = ''
    words = ''
    null_count = 0
    num_count = 0
    morse_list = []
    null_list = []
    space_list = []
    tolerance = 10
    final_string = ""
    #print all array vals
    np.set_printoptions(threshold=np. inf)

    for x in data:
        if abs(x) > 100:
            string += str(x)
            num_count += 1
            if num_count > 1200 and null_count > 3000:
                null_list.append(null_count)
                null_count = 0
        else:
            string+='-'
            null_count += 1
            if null_count > 3000 and num_count > 1200:
                morse_list.append(num_count)
                num_count = 0

    null_list = null_list[1:]
    print(null_list)
    print(morse_list)
    #get any non-silence values and determine whether it is a dot or a dash
    dot = min(morse_list)
    dash = max(morse_list)
    mean = (dot + dash)/2
    #append words with a dot or a dash respectively
    for x in morse_list:
        if mean > x:
            words += '.'
        elif x > mean:
            words += '-'

    #get the silence and determine whether it is no space, letter space, or a word space
    no_space = min(null_list)
    word_space = max(null_list)
    letter_space = 3 * no_space
    if letter_space + 3*no_space > word_space:
        word_space = np.inf
    noTOletter = (no_space + letter_space)/2
    letterTOword = (word_space + letter_space)/2
    print(noTOletter, letterTOword)
    number = 0
    #append space_list with a type of space, space_list is a list, whereas words is not
    for x in range(len(null_list)):
        if noTOletter > null_list[x]:
            space_list.append('')
        elif letterTOword < null_list[x]:
            space_list.append('  ')
        else:
            space_list.append(' ')

    #This will process the words and space_list and combine them into a final string
    for x in range(len(space_list)):
        final_string+=words[x]
        final_string+=space_list[x]
        if x == len(space_list)-1:
            final_string += words[x+1]
    print(final_string)
    #Now we convert that into a list using the word_spaces
    word_list = final_string.split('  ')
    letter_list = []
    for x in word_list:
        #convert the list into a 2D list using the letter spaces
        letter_list.append(x.split(' '))

    decoded_letters = []
    #Put it all back together and decode it as well
    for x in letter_list:
        for y in x:
            decoded_letters.append(decode(y))

        decoded_letters.append(' ')
    response = ""
    #Combine it into one string
    for x in decoded_letters:
        response+=x
    #print
    print(response)

def CollectEasy():
    while True:
        v = chan0.voltage
        data.append(v)


def CollectHard():
    global vals, activedown, activeup
    timeAr = [0, 0]
    while True:
        v = chan0.voltage
        vals.append(v)
        if len(vals) >= 10:
            dev = s.stdev(vals)
            vals = []
            if dev > 0.009 and activedown:
                if timeAr[1] == 0:
                    timeAr[1] = time.time()
                updownarray.append(["down", timeAr[1] - timeAr[0]])
                activedown = False
                timeAr = [0, 0]
            elif dev > 0.009:
                if timeAr[0] == 0:
                    timeAr[0] = time.time()
                activeup = True
            elif dev < 0.009 and activeup:
                if timeAr[1] == 0:
                    timeAr[1] = time.time()
                updownarray.append(["up", timeAr[1] - timeAr[0]])
                activeup = False
                timeAr = [0, 0]
            elif dev < 0.009:
                if timeAr[0] == 0:
                    timeAr[0] = time.time()
                activedown = True


if __name__ == "__main__":
    InputType = input("Please enter 'Light' or 'Sound': \n").lower()
    if InputType == "sound":
        print("Would you like to do close range or long range(experimental)?")
        SoundType = input("Please enter sr or lr: \n").lower()
        if SoundType == "lr":
            print('#' * 80)
            print("Please speak word(s) into the microphone")
            print('Press Ctrl+C to stop the recording')

            record_to_file('outpu.wav')

            print("Result written to output.wav")
            print('#' * 80)
            SoundAnalyzer()
        elif SoundType == "sr":
            CollectHard()
            process()
        else:
            print("Invalid Input!")
    elif InputType == "light":
        CollectEasy()
        LightAnalyze()




