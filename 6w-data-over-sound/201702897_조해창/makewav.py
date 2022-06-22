import math
import struct
import wave

SHORTMAX = 2**(16-1)-1
channels = 1
unit = 0.1
samplerate = 48000
rules = {'START': 512, '0': 768, '1': 896,
         '2': 1024, '3': 1152, '4': 1280,
         '5': 1408, '6': 1536, '7': 1664,
         '8': 1792, '9': 1920, 'A': 2048,
         'B': 2176, 'C': 2304, 'D': 2432,
         'E': 2560, 'F': 2688, 'END': 2944}


text = '🧡💛💚💙💜'
string_hex = text.encode('utf-8').hex().upper()
audio = []

for i in range(int(unit*samplerate*2)):
    audio.append(SHORTMAX*math.sin(2*math.pi*rules['START']*i/samplerate))
for s in string_hex:
    for i in range(int(unit * samplerate * 1)):
        audio.append(SHORTMAX * math.sin(2 * math.pi * rules[s] * i / samplerate))
for i in range(int(unit*samplerate*1)):
    audio.append(SHORTMAX * math.sin(2 * math.pi * rules['END'] * i / samplerate))

with wave.open("🧡💛💚💙💜.wav", 'wb') as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(samplerate)
    for a in audio:
        w.writeframes(struct.pack('<h', int(a)))
