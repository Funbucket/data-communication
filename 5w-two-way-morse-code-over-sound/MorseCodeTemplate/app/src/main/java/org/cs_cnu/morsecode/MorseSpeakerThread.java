package org.cs_cnu.morsecode;

import android.media.AudioFormat;
import android.media.AudioManager;
import android.media.AudioTrack;
import android.util.Log;

import java.util.Iterator;

public class MorseSpeakerThread extends Thread {
    public interface MorseSpeakerCallback {
        void onProgress(int current, int total);
        void onDone();
    }

    public interface MorseSpeakerIterator extends Iterable<String> {
        int getSize();
    }

    final int sample_rate;
    final float frequency;
    final float unit;
    final int unit_size;
    static int sample_idx;

    final MorseSpeakerIterator iterator;
    final MorseSpeakerCallback callback;
    boolean done = false;

    public MorseSpeakerThread(MorseSpeakerIterator iterator, MorseSpeakerCallback callback,
                              int sample_rate, float frequency, float unit) {
        this.iterator = iterator;
        this.callback = callback;
        this.sample_rate = sample_rate;
        this.frequency = frequency;
        this.unit = unit;
        this.unit_size = (int) Math.ceil(this.sample_rate * this.unit);
        setPriority(Thread.MAX_PRIORITY);
    }

    @Override
    public void run() {
        final int morse_size = iterator.getSize();
        final int array_size = (morse_size+1)*unit_size; // add last silence

        final AudioTrack track = new AudioTrack(
                AudioManager.STREAM_MUSIC,
                sample_rate,
                AudioFormat.CHANNEL_OUT_MONO,
                AudioFormat.ENCODING_PCM_16BIT,
                2*sample_rate,
                AudioTrack.MODE_STREAM
        );

        track.setPlaybackPositionUpdateListener(new AudioTrack.OnPlaybackPositionUpdateListener() {
            @Override
            public void onMarkerReached(AudioTrack track) {
                if (!done) {
                    callback.onDone();
                    done = true;
                }
            }

            @Override
            public void onPeriodicNotification(AudioTrack track) {
                if (!done) {
                    callback.onProgress(track.getPlaybackHeadPosition(), array_size);
                }
            }
        });

        track.setPositionNotificationPeriod(1);

        track.play();

        final short[] samples = new short[array_size];
        Log.i("Size", "MorseSize: " + Integer.toString(morse_size) +
                "  UnitSize: " + Integer.toString(unit_size) +
                "  ArraySize: " + Integer.toString(array_size));
// Need to edit below!
        String morse = "";

        for (String str : iterator) {  // iterator ??? ?????? ?????? ?????? string?????? ???????????? ?????? ?????? ??????
            morse += str;
        }

        sample_idx = 0;  // sample index ?????????

        for (int i=0; i<morse.length(); i++){
            System.out.println(sample_idx);
            int next = i + 1;
            int prev = i - 1;
            System.out.println(morse.charAt(i));
            if ( morse.charAt(i) == '.' ){
                insertSinewave(samples, 1, false);
                if ( next < morse.length() ) {  // ????????? morse code ????????????
                    if ( morse.charAt(next) != ' ' && morse.charAt(next) != '/' ){  // dits dahs ?????? ?????? 1 unit ??????
                        insertSinewave(samples, 1, true);
                    }
                } else break;
            } else if ( morse.charAt(i) == '-' ) {
                insertSinewave(samples, 3, false);
                if ( next < morse.length() ) {
                    if ( morse.charAt(next) != ' ' && morse.charAt(next) != '/' ){  // dits dahs ?????? ?????? 1 unit ??????
                        insertSinewave(samples, 1, true);
                    }
                }
            } else if ( morse.charAt(i) == ' ' ) {
                if ( next < morse.length() ) {
                    if ( morse.charAt(prev) != '/' && morse.charAt(next) != '/') {  // ???????????? ????????? ?????? ?????? ??????
                        insertSinewave(samples, 3, true);
                    }
                }
            } else if ( morse.charAt(i) == '/' ) {
                insertSinewave(samples, 7, true);
            }
        }
// Need to edit above!
        track.write(samples, 0, samples.length);
        track.setNotificationMarkerPosition(array_size);
    }

    /*
    * insertSinewave
    * input : samples array, unit(??????), silence(?????? ?????? ?????????)
    * */
    private void insertSinewave(short[] samples, int unit, boolean silence) {
        for (int j=0; j< (unit*unit_size); j++){
            if ( !silence ) {
                samples[sample_idx] = (short) (Short.MAX_VALUE * Math.sin(2 * Math.PI * frequency * j / sample_rate));
            } else {
                samples[sample_idx] = (short) 0;
            }
            sample_idx ++;
        }
    }
}
