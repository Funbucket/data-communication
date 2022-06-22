import math
import struct
import time
import pyaudio
import morsecode
from huffman import huffman_decode, huffman_encode
import audio2file

HUFF_TREE = huffman_encode()
MORSE_DICT = morsecode.code
CHANNELS = 1
SAMPLERATE = 48000
FREQUENCY = 523.251
UNIT = 0.1
SHORTMAX = 2**(32-1)-1
MORSE_THRESHOLD = 800
UNSEEN_THRESHOLD = 3.0
UNITSIZE = math.ceil(SAMPLERATE*UNIT)


def unicode2hex(text):
    """
    :param text: 사용자 입력 unicode
    :return: unicode 가 16진수화된 string
    """
    text = text.strip()
    byte_hex = text.encode('utf-8')
    byte_string = byte_hex.hex().upper()
    return byte_string


def hex2morse(hex):
    """
    :param hex: hex string
    :return: 입력된 hex string 에 맞게 mapping 된 morse code
    """
    morse = ''
    for h in hex:
        morse += MORSE_DICT[h]
    return morse


def hex2text(hex):
    """
    :param hex: hex string
    :return: text
    """
    client_byte_hex = bytes.fromhex(hex)
    text = client_byte_hex.decode('utf-8')
    return text


def morse2audio(morse):
    """
    :param morse:
    :return sine graph 가 digitalized 된 값들의 배열 array of integer:
    - 국제 표준 -
    dits : 1 unit
    dahs : 3 units
    dits dahs 사이 : 1 unit
    """
    def sine_wave(x):
        # x 값에 해당하는 sine wave의 해 반환
        return math.sin(2 * math.pi * FREQUENCY * (x / SAMPLERATE))

    audio = []
    for idx, m in enumerate(morse):
        if m == '.':
            for i in range(UNITSIZE):
                audio.append(int(SHORTMAX*sine_wave(i)))

        elif m == '-':
            for i in range(3*UNITSIZE):
                audio.append(int(SHORTMAX*sine_wave(i)))

        for i in range(UNITSIZE):
            audio.append(int(0))

    return audio[0:-1]


def play_audio(audio):
    p = pyaudio.PyAudio()

    stream = p.open(format=pyaudio.paInt16,
                    channels=CHANNELS,
                    rate=SAMPLERATE,
                    frames_per_buffer=UNITSIZE,
                    output=True)

    for a in audio:
        stream.write(struct.pack('<h', a))

    time.sleep(0.5/UNIT)  # Wait for play

    stream.stop_stream()
    stream.close()
    p.terminate()


def send_data():
    user_input = input('Input the text (Unicode): ')
    byte_string = unicode2hex(user_input)
    morse = hex2morse(byte_string)
    print(f'MorseCode: {morse}')
    audio = morse2audio(morse)
    print(f'AudioSize: {len(audio)}')
    play_audio(audio)


def record_audio():
    p = pyaudio.PyAudio()
    binary_morse = ""

    def binary2morse(binary_morse):
        """
        :param string type binary morse code:
        :return morse code:
        '111' : dah
        '1' : dit
        '0': between dit and dah
        """
        binary_morse = binary_morse.replace('111', '-')
        binary_morse = binary_morse.replace('1', '.')
        return binary_morse.replace('0', '')

    stream = p.open(format=pyaudio.paInt16,
                    channels=CHANNELS,
                    rate=SAMPLERATE,
                    frames_per_buffer=UNITSIZE,
                    input=True)

    recoding = True
    tuning = True
    abs_sum = 0
    count = 0
    silence_count = 0

    while recoding:
        data = stream.read(UNITSIZE)
        for i in range(0, len(data), 2):
            d = struct.unpack('<h', data[i:i+2])[0]
            if tuning:
                if abs(d) > MORSE_THRESHOLD:
                    tuning = False
                    abs_sum = d
            else:
                abs_sum = abs_sum + abs(d)
                count = count + 1
                if count == UNITSIZE:
                    if abs_sum / count >= MORSE_THRESHOLD:
                        binary_morse += "1"
                        silence_count = 0
                    else:
                        binary_morse += "0"
                        silence_count += 1
                    abs_sum = 0
                    count = 0
                    if silence_count > 3.0/UNIT:
                        recoding = False
                        break

    morse = binary2morse(binary_morse)
    stream.stop_stream()
    stream.close()
    p.terminate()

    return morse


def receive_data():
    morse = record_audio()
    print(f'Morse: {morse}')
    byte_string = huffman_decode(morse, HUFF_TREE[0])
    text = hex2text(byte_string)
    print(f'Sound input: {text}')


def main():
    while True:
        print('Morse Code Data Communication 2022')
        print('[1] Send data over sound (play)')
        print('[2] Receive data over sound (record)')
        print('[q] Exit')
        select = input('Select menu: ').strip().upper()
        if select == '1':
            send_data()
        elif select == '2':
            receive_data()
        elif select == 'Q':
            print('Terminating...')
            break


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true',
                         help='The present debug message')

    FLAGS, _ = parser.parse_known_args()
    DEBUG = FLAGS.debug

    main()

    # ㄱ! A?
    # .--.-...-.-......-..-.-----...-----....-......----......-

    # A!?
    # ......-----...----......-

    # text = "A!?"
    # byte_string = unicode2hex(text)
    # morse = hex2morse(byte_string)
    # audio = morse2audio(morse)
    # audio2file.audio2file(audio, "./{}.wav".format(text))

