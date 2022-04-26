from scipy.io import wavfile
import sys
import numpy as np
from MorseToAnalog import decode
samplerate, data = wavfile.read('morse.wav')
np. set_printoptions(threshold=np. inf)
string = ''
words = ''
null_count = 0
num_count = 0
morse_list = []
null_list = []
space_list = []
tolerance = 10
final_string = ""
for x in data:
    if x != 128:
        string += str(x)
        num_count += 1
        if num_count > 3 and null_count > 10:
            null_list.append(null_count)
            null_count = 0
    else:
        string+='-'
        null_count += 1
        if null_count > 10 and num_count > 2:

            morse_list.append(num_count)
            num_count = 0

dot = min(morse_list)
dash = max(morse_list)
for x in morse_list:
    if dot + tolerance > x > dot - tolerance:
        words += '.'
    elif dash + tolerance > x > dash - tolerance:
        words += '-'
no_space = min(null_list)
word_space = max(null_list)
number = 0
for x in range(len(null_list)):
    if no_space + tolerance > null_list[x] > no_space - tolerance:
        space_list.append('')
    elif word_space + tolerance > null_list[x] > word_space - tolerance:
        space_list.append('  ')
    else:
        space_list.append(' ')

for x in range(len(space_list)):
    final_string+=words[x]
    final_string+=space_list[x]
    if x == len(space_list)-1:
        final_string += words[x+1]


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







