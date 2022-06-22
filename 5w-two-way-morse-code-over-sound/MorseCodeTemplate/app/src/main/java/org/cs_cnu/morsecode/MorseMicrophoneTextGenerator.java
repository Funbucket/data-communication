package org.cs_cnu.morsecode;

import android.util.Log;

import java.util.Map;

public class MorseMicrophoneTextGenerator {

    final String morse_code;
    final Map<String, String> map;
    final String text;

    public MorseMicrophoneTextGenerator(String morse_code, Map<String, String> map) {
        this.morse_code = morse_code;
        this.map = map;

// Need to edit below!
        StringBuilder sb = new StringBuilder();
        String[] m_words = morse_code.split("/");
        for(String m_word : m_words) {
            String[] m_characters = m_word.split(" ");
            for(String m_character : m_characters) {
                sb.append(getKey(map, m_character));
            }
            sb.append(" ");
        }
// Need to edit above!

        this.text = sb.toString();
        Log.i("Sound input", text);
    }

    public String getText() {
        return this.text;
    }

    private <K, V> K getKey(Map<K, V> map, V value) {
        for (Map.Entry<K, V> entry : map.entrySet()) {
            if (entry.getValue().equals(value)) {
                return entry.getKey();
            }
        }
        return null;
    }
}
