package org.cs_cnu.morsecode;

import android.Manifest;
import android.annotation.SuppressLint;
import android.content.pm.PackageManager;
import android.media.AudioFormat;
import android.media.AudioRecord;
import android.media.MediaRecorder;
import android.provider.MediaStore;
import android.util.Log;

import androidx.core.app.ActivityCompat;

import java.nio.ByteBuffer;
import java.util.Arrays;
import java.util.Map;

public class MorseMicrophoneThread extends Thread {
    public interface MorseMicrophoneCallback {
        void onProgress(String value);
        void onDone(String value);
    }


    final short MORSE_THRESHOLD = Short.MAX_VALUE / 4;  // 8191
    final float UNSEEN_THRESHOLD = 3.0f;

    final int sample_rate;
    final float frequency;
    final float unit;
    final int unit_size;
    final int buffer_size;
    boolean BF = false;  // begin flag
    int SILENCE_COUNT = 0;

    final MorseMicrophoneThread.MorseMicrophoneCallback callback;

    public MorseMicrophoneThread(MorseMicrophoneThread.MorseMicrophoneCallback callback,
                                 int sample_rate, float frequency, float unit) {
        this.callback = callback;
        this.sample_rate = sample_rate;
        this.frequency = frequency;
        this.unit = unit;
        this.unit_size = (int) Math.ceil(this.sample_rate * this.unit);
        this.buffer_size = (int) AudioRecord.getMinBufferSize(sample_rate, AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT);
        setPriority(Thread.MAX_PRIORITY);
    }

    private String binary2morse(String binary_morse) {
        binary_morse = binary_morse.replace("111", "-");
        binary_morse = binary_morse.replace("1", ".");
        binary_morse = binary_morse.replace("0000000", " / ");
        binary_morse = binary_morse.replace("000", " ");
        return  binary_morse.replace("0", "");
    }

    @Override
    public void run() {
        @SuppressLint("MissingPermission")
        final AudioRecord record = new AudioRecord(
                MediaRecorder.AudioSource.DEFAULT,
                this.sample_rate,
                AudioFormat.CHANNEL_IN_MONO,
                AudioFormat.ENCODING_PCM_16BIT,
                unit_size);

        final short[] samples = new short[unit_size];
        StringBuilder sb = new StringBuilder();

        record.startRecording();
// Need to edit below!
        String binary_morse = "";

        while (true) {
            short sum = 0;
            int result = record.read(samples, 0, unit_size);
            if ( result < 0 ) {
                break;
            } else {
                for(short sample : samples) {
                    sum += (Math.abs(sample) / 1000);
                }

                if ( sum > MORSE_THRESHOLD ) {
                    BF = true;
                }

                if ( BF && SILENCE_COUNT > 30 ) {
                    BF = false;
                    binary_morse = binary_morse.substring(0, binary_morse.lastIndexOf("1") + 1);
                    break;
                } else if ( BF && sum < MORSE_THRESHOLD ) {
                    binary_morse += "0";
                    SILENCE_COUNT++;
                } else if ( BF && sum > MORSE_THRESHOLD ) {
                    SILENCE_COUNT = 0;
                    binary_morse += "1";
                }
            }
        }
        record.stop();
        record.release();
        String morse = binary2morse(binary_morse);
        Log.i("RawMorse", morse);
        Log.i("Morse", morse);
        callback.onDone(morse);
// Need to edit above!
    }
}
