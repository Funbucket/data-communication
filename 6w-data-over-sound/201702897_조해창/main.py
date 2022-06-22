import struct
import wave
import numpy as np
import scipy.fftpack
import reedsolo

UNIT = 0.1
CHANNELS = 1
SAMPWIDTH = 2
SAMPLERATE = 48000
FREQ_START = 512
FERQ_STEP = 128
DATA_LEN = 12
RSC_LEN = 4
PADDING = 5

rules = {'START': 512, '0': 768, '1': 896,
         '2': 1024, '3': 1152, '4': 1280,
         '5': 1408, '6': 1536, '7': 1664,
         '8': 1792, '9': 1920, 'A': 2048,
         'B': 2176, 'C': 2304, 'D': 2432,
         'E': 2560, 'F': 2688, 'END': 2944}


def unicode2hex(text):
    text = text.strip()
    byte_string = text.encode('utf-8').hex().upper()
    return byte_string


def hex2unicode(hex):
    client_byte_hex = bytes.fromhex(hex)
    text = client_byte_hex.decode('utf-8')
    return text


def ignoreRScode(filename):
    hex_string = ''
    with wave.open(filename, 'rb') as w:
        frames = w.getnframes()
        audio = []
        for i in range(frames):
            frame = w.readframes(1)
            audio.append(struct.unpack('<h', frame)[0])
            if len(audio) >= UNIT * SAMPLERATE:
                freq = scipy.fftpack.fftfreq(len(audio))
                fourier = scipy.fftpack.fft(audio)
                top = freq[np.argmax(abs(fourier))] * SAMPLERATE
                data = ''
                for k, v in rules.items():
                    if v - PADDING <= top <= v + PADDING:
                        data = k
                if data == 'END':
                    print()
                    print(data, end='')
                if data != 'START' and data != 'END':
                    hex_string = f'{hex_string}{data}'
                    print(data, end='')
                if data == 'START':
                    print(data)
                audio.clear()
    print()
    byte_hex = bytes.fromhex(hex_string)
    hex_string = ''

    for k in range(0, len(byte_hex), DATA_LEN + RSC_LEN):
        data = byte_hex[k:k + DATA_LEN + RSC_LEN]
        data = data[:-RSC_LEN]
        decoded_data = data.hex().upper()
        hex_string = f'{hex_string}{decoded_data}'

    return hex2unicode(hex_string)


def errorCorrect(hex_string):
    print("#######hex_string :: " + hex_string)
    client_byte_hex = bytes.fromhex(hex_string)
    client_rsc = reedsolo.RSCodec(RSC_LEN)
    client_byte = client_rsc.decode(client_byte_hex)[0]
    return client_byte


def decodeRScode(filename):
    hex_string = ''
    client_byte = bytearray()
    with wave.open(filename, 'rb') as w:
        frames = w.getnframes()
        audio = []
        for i in range(frames):
            frame = w.readframes(1)
            audio.append(struct.unpack('<h', frame)[0])
            if len(audio) >= UNIT * SAMPLERATE:
                freq = scipy.fftpack.fftfreq(len(audio))
                fourier = scipy.fftpack.fft(audio)
                top = freq[np.argmax(abs(fourier))] * SAMPLERATE
                data = ''
                for k, v in rules.items():
                    if v - PADDING <= top <= v + PADDING:
                        data = k
                if data == 'END':
                    print()
                    print(data, end='')
                if data != 'START' and data != 'END':
                    hex_string = f'{hex_string}{data}'
                    print(data, end='')
                    if len(hex_string) == 32:
                        client_byte += errorCorrect(hex_string)
                        hex_string = ''
                if data == 'START':
                    print(data)
                audio.clear()
    print()
    client_byte += errorCorrect(hex_string)
    return client_byte.decode("utf-8")


if __name__ == '__main__':
    # print(ignoreRScode('201702897-p1.wav'))
    # print(ignoreRScode('201702897-p2.wav'))
    print(decodeRScode('201702897-p2.wav'))
    # print(decodeRScode('201702897-p3.wav'))