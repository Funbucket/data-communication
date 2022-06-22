package org.cs_cnu.morsecode;

import android.util.Log;

import java.io.UnsupportedEncodingException;
import java.math.BigInteger;
import java.util.Map;

public class MorseMicrophoneTextGenerator {

    final String morse_code;
    final Map<String, String> map;
    final String text;

    public MorseMicrophoneTextGenerator(String morse_code, Map<String, String> map) {
        this.morse_code = morse_code;
        this.map = map;

// Need to edit below!
        Node root = Huffman.huffmanEncode();
        String byteString = Huffman.huffmanDecode(morse_code, root);

        byte[] clientByteHex = new byte[byteString.length()/2];
        for (int i = 0; i < clientByteHex.length; i++) {
            int index = i * 2;
            clientByteHex[i] = (byte) Integer.parseInt(byteString.substring(index, index+2), 16);
        }

        String clientOutput = "";
        try {
            clientOutput = new String(clientByteHex, "UTF-8");
        } catch (UnsupportedEncodingException e) {
            System.out.println("Exception: " + e.toString());
        }
// Need to edit above!

        this.text = clientOutput;
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
