import re
import math
import struct
import time
import pyaudio
import numpy as np
import morsecode
from audio2file import audio2file

MORSE_DICT = morsecode.code
CHANNELS = 1
SAMPLERATE = 48000
FREQUENCY = 523.251
UNIT = 0.1
SHORTMAX = 2**(16-1)-1
MORSE_THRESHOLD = 3000
UNSEEN_THRESHOLD = 3.0
UNITSIZE = math.ceil(SAMPLERATE*UNIT)


def text2morse(text):
    """
    :param text:
    :return morse:
    ascii 십진수 값으로 조건 분기
    case 1 : ascii 값이 65 이상 90 이하 이면 대문자 alphabet
    case 2 : ascii 값이 48 이상 57 이하 이면 숫자값
    case 3 : ascii 값이 32 이면 space(단어사이)
    """
    text = text.upper()
    morse = ''
    for t in text:
        ascii_dec = ord(t)
        if ascii_dec == 32:
            morse += "/"  # 단어사이 7 units 할당하기 위한 delimiter 추가
        else:
            morse += MORSE_DICT[t]
        morse += " "  # 문자사이 3units 할당하기 위한 delimiter 로 공백 추가 (delimiter to units 은 morse2audio에서 처리)

    return morse[0:-1]  # 마지막 space 제거


def morse2audio(morse):
    """
    :param morse:
    :return sine graph 가 digitalized 된 값들의 배열 array of integer:
    - 국제 표준 -
    dits : 1 unit
    dahs : 3 units
    dits dahs 사이 : 1 unit
    문자 사이 : 3 units
    단어 사이 : 7 units
    """
    def sine_wave(x):
        # x 값에 해당하는 sine wave의 해 반환
        return math.sin(2 * math.pi * FREQUENCY * (x / SAMPLERATE))

    audio = []
    for idx, m in enumerate(morse):
        next = idx + 1  # 다음 index 값 저장
        prev = idx - 1  # 이전 index 값 저장
        if m == '.':
            for i in range(UNITSIZE):
                audio.append(int(SHORTMAX*sine_wave(i)))
            try:
                if morse[next] != " " and morse[next] != "/":  # dits dahs 사이 1 unit 추가
                    for i in range(UNITSIZE):
                        audio.append(int(0))
            except IndexError as e:
                return audio

        elif m == '-':
            for i in range(3*UNITSIZE):
                audio.append(int(SHORTMAX*sine_wave(i)))
            try:
                if morse[next] != " " and morse[next] != "/":  # dits dahs 사이 1 unit 추가
                    for i in range(UNITSIZE):
                        audio.append(int(0))
            except IndexError as e:
                return audio
        elif m == " ":
            try:
                if morse[prev] != "/" and morse[next] != "/":  # 문자 사이 공백일때만 3 units 추가
                    for i in range(3*UNITSIZE):
                        audio.append(int(0))
            except IndexError as e:
                return audio
        elif m == "/":
            # 단어 사이 7 units 추가
            for i in range(7*UNITSIZE):
                audio.append(int(0))
    return audio


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
    while True:
        print('Type some text (only English)')
        text = input('User input: ').strip()
        if re.match(r'[A-Za-z0-9 ]+', text):
            break
    morse = text2morse(text)
    print(f'MorseCode: {morse}')
    audio = morse2audio(morse)
    print(f'AudioSize: {len(audio)}')
    play_audio(audio)


def record_audio():
    BF = False  # begin flag
    SILENCE_COUNT = 0

    p = pyaudio.PyAudio()
    binary_morse = ""

    def binary2morse(binary_morse):
        """
        :param string type binary morse code:
        :return morse code:
        '111' : dah
        '1' : dit
        '0000000' : between words
        '000' : between characters
        '0': between dit and dah
        """
        binary_morse = binary_morse.replace('111', '-')
        binary_morse = binary_morse.replace('1', '.')
        binary_morse = binary_morse.replace('0000000', ' / ')
        binary_morse = binary_morse.replace('000', ' ')
        return binary_morse.replace('0', '')

    stream = p.open(format=pyaudio.paInt16,
                    channels=CHANNELS,
                    rate=SAMPLERATE,
                    frames_per_buffer=UNITSIZE,
                    input=True)

    while True:
        data = np.fromstring(stream.read(UNITSIZE), dtype=np.int16)
        average = int(np.average(np.abs(data) * 10))

        if average > MORSE_THRESHOLD:
            BF = True

        # 시작 후 묵음 일정 30 UNIT 이상 지속시 record 종료 (unit = 0.1s 이기 때문에 대략 3초 대기)
        if BF and SILENCE_COUNT > 30:
            binary_morse = binary_morse.rstrip('0')  # 뒤에 불필요한 0 값 제거(끝나기전 record 된 묵음)
            break

        # 시작 후 묵음 or noise
        elif BF and average < MORSE_THRESHOLD:
            binary_morse += "0"
            SILENCE_COUNT += 1

        # 시작 후 소리
        elif BF and average > MORSE_THRESHOLD:
            SILENCE_COUNT = 0  # 묵음 횟수 최기화
            binary_morse += "1"

    morse = binary2morse(binary_morse)
    stream.stop_stream()
    stream.close()
    p.terminate()

    return morse


def morse2text(morse):
    """
    :param morse code:
    :return text:
    """

    m_words = morse.split("/")  # / 을 separator 로 하여 단어단위 저장

    text = ""

    for m_word in m_words:  # 단어 단위로 구분된 morse 순회
        m_characters = m_word.split(" ")  # space 을 separator 로 하여 문자단위 저장
        for m_character in m_characters:  # 문자 단위 morse 순회
            for key, value in MORSE_DICT.items():
                if value == m_character:  # 해당 morse convert
                    text += key
        text += " "

    return text


def receive_data():
    morse = record_audio()
    print(f'Morse: {morse}')
    text = morse2text(morse)
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
    # import argparse
    #
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--debug', action='store_true',
    #                      help='The present debug message')
    #
    # FLAGS, _ = parser.parse_known_args()
    # DEBUG = FLAGS.debug
    #
    # main()

    text = "a"
    morse = text2morse(text)
    audio = morse2audio(morse)
    audio2file(audio, "./{}.wav".format(text))

