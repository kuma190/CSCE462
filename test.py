# import pyaudio
# p = pyaudio.PyAudio()
# for ii in range(p.get_device_count()):
# print(ii,p.get_device_info_by_index(ii).get('name'),p.get_device_info_by_index(ii).get('maxInputChannels'),p.get_device_info_by_index(ii).get('defaultSampleRate'))

import wave
import time
import pyaudio
from scipy.io import wavfile
import numpy as np
CHUNK = 4096
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
dev_index = 0
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

    return morseDict.get(letter)

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



if __name__ == '__main__':
    print('#' * 80)
    print("Please speak word(s) into the microphone")
    print('Press Ctrl+C to stop the recording')

    record_to_file('outpu.wav')
    SoundAnalyzer()
    print("Result written to output.wav")

    print('#' * 80)
