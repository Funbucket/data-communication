import math
import wave
import struct
import statistics

INTMAX = 2 ** (32 - 1) - 1
t = 0.1
fs = 48000
f = 523.251
UNIT = int(t * fs)

english = {'A':'.-'   , 'B':'-...' , 'C':'-.-.' ,
           'D':'-..'  , 'E':'.'    , 'F':'..-.' ,
           'G':'--.'  , 'H':'....' , 'I':'..'   ,
           'J':'.---' , 'K':'-.-'  , 'L':'.-..' ,
           'M':'--'   , 'N':'-.'   , 'O':'---'  ,
           'P':'.--.' , 'Q':'--.-' , 'R':'.-.'  ,
           'S':'...'  , 'T':'-'    , 'U':'..-'  ,
           'V':'...-' , 'W':'.--'  , 'X':'-..-_',
           'Y':'-.--' , 'Z':'--..'  }


number = { '1':'.----', '2':'..---', '3':'...--',
           '4':'....-', '5':'.....', '6':'-....',
           '7':'--...', '8':'---..', '9':'----.',
           '0':'-----'}


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
        if 65 <= ascii_dec <= 90:
            morse += english[t]
        elif 48 <= ascii_dec <= 57:
            morse += number[t]
        elif ascii_dec == 32:
            morse += "/"  # 단어사이 7 units 할당하기 위한 delimiter 추가
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
        return math.sin(2 * math.pi * f * (x / fs))

    audio = []
    for idx, m in enumerate(morse):
        next = idx + 1  # 다음 index 값 저장
        prev = idx - 1  # 이전 index 값 저장
        if m == '.':
            for i in range(UNIT):
                audio.append(int(INTMAX*sine_wave(i)))
            try:
                if morse[next] != " " and morse[next] != "/":  # dits dahs 사이 1 unit 추가
                    for i in range(UNIT):
                        audio.append(int(0))
            except IndexError as e:
                return audio

        elif m == '-':
            for i in range(3*UNIT):
                audio.append(int(INTMAX*sine_wave(i)))
            try:
                if morse[next] != " " and morse[next] != "/":  # dits dahs 사이 1 unit 추가
                    for i in range(UNIT):
                        audio.append(int(0))
            except IndexError as e:
                return audio
        elif m == " ":
            # dits dahs 사이 default로 1 unit 씩 할당되기 때문에 추가로 2 unit 할당
            try:
                if morse[prev] != "/" and morse[next] != "/":  # 문자 사이 공백일때만 3 units 추가
                    for i in range(3*UNIT):
                        audio.append(int(0))
            except IndexError as e:
                return audio
        elif m == "/":
            # 단어 사이 7 units 추가
            for i in range(7*UNIT):
                audio.append(int(0))
    return audio


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


def file2morse(filename):
    """
    :param wav file:
    :return morse code:
    """
    with wave.open(filename, 'rb') as w:
        audio = []
        frames = w.getnframes()
        for i in range(frames):
            frame = w.readframes(1)
            audio.append(struct.unpack('<i', frame)[0])

        binary_morse = ""  # 0, 1로 audio 값을 임시로 저장
        for i in range(1, math.ceil(len(audio)/UNIT)+1):
            stdev = statistics.stdev(audio[(i-1)*UNIT:i*UNIT])
            if stdev == 0:
                binary_morse += '0'
            else:
                binary_morse += '1'

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

        morse = binary2morse(binary_morse)

    return morse


def morse2text(morse):
    """
    :param morse code:
    :return text:
    """
    m_words = morse.split("/")  # / 을 separator 로 하여 단어단위 저장

    morseChart = merge_dicts(english, number)  # english, number dict 병합

    text = ""

    for m_word in m_words:  # 단어 단위로 구분된 morse 순회
        m_characters = m_word.split(" ")  # space 을 separator 로 하여 문자단위 저장
        for m_character in m_characters:  # 문자 단위 morse 순회
            for key, value in morseChart.items():
                if value == m_character:  # 해당 morse convert
                    text += key
        text += " "

    return text


def merge_dicts(a, b):
    c = a.copy()  # a 변수를 c에 copy 한 후,
    c.update(b)  # c를 update하여 반환
    return c


if __name__ == '__main__':
    # morse = file2morse("./201702897.wav")
    # morse = file2morse("./hello.wav")
    # text = morse2text(morse)
    # print(text)  # 과제 해석
    #
    # answer = "HOMEWORK DEPTH 201702897 6366 LEADER DAD 8517 2053 4260"
    # morse = text2morse(answer)
    # audio = morse2audio(morse)
    # audio2file(audio, "./{}.wav".format(answer))

    # answer = "a b"
    # morse = text2morse(answer)
    # audio = morse2audio(morse)
    # audio2file(audio, "./{}.wav".format(answer))
    #
    answer = "a b"
    morse = text2morse(answer)
    audio = morse2audio(morse)
    audio2file(audio, "./{}.wav".format(answer))

    # answer = "💑"
    # morse = text2morse(answer)
    # audio = morse2audio(morse)
    # audio2file(audio, "./{}.wav".format(answer))


