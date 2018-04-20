# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 23:09:04 2018

@author: keding
"""
from __future__ import print_function

import os
import collections
import wave

import webrtcvad
from wakeup import Snowboy
from asr import BasicStreamASR
from tts import BasicTTS
from audio import play, AudioStream
import pyaudio
from utils import no_alsa_error


def wakeup_alert(keyword):
    ding = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        'snowboy/resources/ding.wav')
    dong = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        'snowboy/resources/dong.wav')
    if keyword == 1:
        play(ding)
    else:
        play(dong)


if __name__ == '__main__':
    app_id = '11????605'
    app_key = 'XeJaa????7uNHeyC'

    # initialize TTS
    tts_engine = BasicTTS(app_id=app_id, app_key=app_key)
    # initialize ASR
    asr_engine = BasicStreamASR(app_id=app_id, app_key=app_key)

    vad = webrtcvad.Vad(0)

    with no_alsa_error():
        pa = pyaudio.PyAudio()

    tts_engine.say("你好", speaker=6)
    while True:
        # set up wakeup
        models = ['snowboy/resources/models/snowboy.umdl',
                  'snowboy/resources/models/alexa_02092017.umdl']
        keyword_detector = Snowboy(models, 0.5)
        keyword_detector.start_detect(callback=wakeup_alert)

        # speech streaming
        rate = 16000
        chunk_duration = 20  # in ms
        chunk = rate // 1000 * chunk_duration
        stream = pa.open(format=pyaudio.paInt16, channels=1, rate=rate,
                         input=True, frames_per_buffer=chunk)
        stream.start_stream()

        # feed speech into ASR engine
        buffer_duration = 1500  # 1.5s
        num_buffer_chunks = buffer_duration // chunk_duration
        num_window_chunks = 400 // chunk_duration
        num_window_chunks_end = 2 * num_window_chunks
        max_waiting_chunks = 2000 // chunk_duration

        ring_buffer = collections.deque(maxlen=num_buffer_chunks)
        triggered = False
        count = 0
        flags = [0] * num_window_chunks
        flags_end = [1] * num_window_chunks_end
        idx, idx_end = 0, 0
        voiced_frames = []
        seq = 0
        text = ''
        while True:
            '''adapted from https://github.com/wangshub/python-vad
            '''
            count += 1

            frames = stream.read(chunk)
            status = vad.is_speech(frames, rate)

            active = 1 if status else 0
            flags[idx] = flags_end[idx_end] = active
            idx = (idx + 1) % num_window_chunks
            idx_end = (idx_end + 1) % num_window_chunks_end

            if not triggered:
                # time out
                if count > max_waiting_chunks:
                    break

                ring_buffer.append(frames)

                if sum(flags) > 0.8 * len(flags):
                    triggered = True
                    voiced_frames.append(b''.join(ring_buffer))
                    ring_buffer.clear()
            else:  # check end point
                voiced_frames.append(frames)
                if sum(flags_end) < 0.1 * len(flags_end):
                    triggered = False
                    break

        stream.stop_stream()
        stream.close()

        # save wave
        wav_file = 'wav/test_main_loop.wav'
        wf = wave.open(wav_file, 'wb')
        wf.setnchannels(1)
        wf.setframerate(16000)
        wf.setsampwidth(2)
        wf.writeframes(b''.join(voiced_frames))

        wf.close()
        play(wav_file)
        text = asr_engine.stt(wav_file)
        print(text)

    pa.terminate()
