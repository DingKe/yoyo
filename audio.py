# -*- coding: utf-8 -*-
"""
Created on Sun Feb 11 22:58:32 2018

@author: keding
"""
from __future__ import print_function

import collections
import wave
import threading
import subprocess

import pyaudio
from utils import cmd_exists, no_alsa_error


def play(speech_file, volume=1.):
    if cmd_exists('aplay'):
        cmd = ['aplay', speech_file]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        p.wait()
    else:
        wf = wave.open(audio_file, 'rb')
        with no_alsa_error():
            pa = pyaudio.PyAudio()
        stream = pa.open(format=pa.get_format_from_width(wf.getsampwidth()),
                         channels=wf.getnchannels(),
                         rate=wf.getframerate(),
                         output=True)
        stream.start_stream()

        chunk = 16000
        data = wf.readframes(chunk)
        while data:
            stream.write(data)
            data = wf.readframes(chunk)

        stream.stop_stream()
        stream.close()

        wf.close()
        pa.terminate()


class AudioStream(object):
    """Audio capturer with ring buffer
    """

    def __init__(self, chunk=16 * 20, buffer_bytes=16000, rate=16000):
        self.chunk = chunk
        self.buffer_bytes = buffer_bytes
        self.rate = rate

        self._buf = collections.deque(maxlen=buffer_bytes)
        self._lock = threading.Lock()
        self.record_thread = None

    def get(self):
        """Retrieves data from the beginning of buffer"""
        with self._lock:
            tmp = bytes(bytearray(self._buf))
        return tmp

    def get_and_clear(self):
        """Retrieves data from the beginning of buffer and clears it"""
        with self._lock:
            tmp = bytes(bytearray(self._buf))
            self._buf.clear()

        return tmp

    def clear(self):
        with self._lock:
            self._buf.clear()

    def extend(self, data):
        """Adds data to the end of buffer"""
        with self._lock:
            self._buf.extend(data)

    def record_proc(self):
        with no_alsa_error():
            pa = pyaudio.PyAudio()
        stream = pa.open(format=pyaudio.paInt16,
                         channels=1,
                         rate=self.rate,
                         input=True,
                         frames_per_buffer=self.chunk)
        stream.start_stream()

        while self.recording:
            data = stream.read(self.chunk)
            self.extend(data)

        stream.stop_stream()
        stream.close()
        pa.terminate()

    def start(self):
        """
        Start a thread for spawning arecord process and reading its stdout
        """
        self._buf.clear()

        self.recording = True
        self.record_thread = threading.Thread(target=self.record_proc)
        self.record_thread.daemon = True
        self.record_thread.start()

    def stop(self):
        if self.record_thread:
            self.recording = False
            self.record_thread.join()

        self._buf.clear()

    def __del__(self):
        self.stop()


def test_audio_stream():
    import time

    chunk = 16 * 20  # 20ms
    buffer_bytes = 16000 * 2  # 1s

    stream = AudioStream(chunk=chunk, buffer_bytes=buffer_bytes)

    stream.start()
    print('Stream Start')

    # record 3s
    record_time = 3
    rate = 16000

    record_file = 'wav/test_audio_stream.wav'
    wf = wave.open(record_file, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(rate)

    recorded = 0
    while recorded < rate * record_time:
        data = stream.get_and_clear()
        recorded += len(data) / 2
        if len(data) > 0:
            wf.writeframes(b''.join(data))
        else:
            time.sleep(0.03)
    wf.close()

    stream.stop()
    print('Stream Stop and start replay...')
    time.sleep(0.5)

    play(record_file)


if __name__ == '__main__':
    import pytest

    pytest.main([__file__, '-s'])
