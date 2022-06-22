import math
import wave
import struct
import statistics

INTMAX = 2 ** (32 - 1) - 1
t = 0.1
fs = 48000
f = 523.251
UNIT = int(t * fs)


def audio2file(audio, filename):
    """
    :param audio:
    :param filename:
    :return wav file:
    """
    with wave.open(filename, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(4)
        w.setframerate(48000)
        for a in audio:
            w.writeframes(struct.pack('<l', a))


