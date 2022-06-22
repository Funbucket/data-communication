package org.cs_cnu.morsecode;

import android.util.Log;

import java.util.Iterator;
import java.util.Map;

public class MorseSpeakerCodeGenerator implements MorseSpeakerThread.MorseSpeakerIterator {

    final String message;
    final Map<String, String> map;
    final String morse_code;

    public MorseSpeakerCodeGenerator(String message, Map<String, String> map) {
        this.message = message.toUpperCase();
        this.map = map;

// Need to edit below!
        StringBuilder sb = new StringBuilder();

        for (char ch: this.message.toCharArray()) {
            if ( (int)ch >= 48 && (int)ch <= 57 ||
                    (65 <= (int)ch && (int)ch <= 90) ) {
                sb.append(map.get(Character.toString(ch)));
            }else if( (int)ch == 32 ) {
                sb.append("/");  // 단어사이 7 units 할당하기 위한 delimiter 추가
            }
            sb.append(" ");  // 문자사이 3units 할당하기 위한 delimiter 로 공백 추가
        }
// Need to edit above!

        this.morse_code = sb.toString().trim();
        Log.i("MorseCode", this.morse_code);
    }

    public String getMorseCode() {
        return this.morse_code;
    }

    @Override
    public int getSize() {
        int size = 0;
        for (int i = 0; i < this.morse_code.length(); i++) {
            char ch = this.morse_code.charAt(i);
            if (ch == '/') {
                size = size + 1;
            } else if (ch == ' ') {
                size = size + 1;
            } else if (ch == '.') {
                size = size + 1;
            } else if (ch == '-') {
                size = size + 3;
            }
        }
        size = size + this.morse_code.length();
        return size;
    }

    @Override
    public Iterator<String> iterator() {
        return new Iterator<String> () {
            boolean start = false;
            boolean end = false;
            int i = 0;

            @Override
            public boolean hasNext() {
                if (!start || !end) {
                    return true;
                }
                return false;
            }

            @Override
            public String next() {
                if (!start) {
                    start = true;
                    i = 0;
                }
                if (morse_code.length() > i) {
                    String value = Character.toString(morse_code.charAt(i));
                    i = i + 1;
                    return value;
                } else {
                    end = true;
                }
                return "";
            }
        };
    }
}
