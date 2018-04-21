# -*- coding: utf-8 -*-
"""
Created on Sun Feb 12 10:04:44 2018

@author: keding
"""
from __future__ import print_function

import time
import wave
import random
import base64
import threading

from utils import *


class BaseASR(object):

    ext2idx = {'pcm': '1', 'wav': '2', 'amr': '3', 'slk': '4'}

    def __init__(self, api_url, app_id, app_key):
        self.api_url = api_url
        self.app_id = app_id
        self.app_key = app_key

    def stt(self, audio_file, ext='wav', rate=16000):
        raise Exception("Not Implemented!")


class BasicASR(BaseASR):
    """ Online ASR from Tencent
    https://ai.qq.com/doc/aaiasr.shtml
    """

    def __init__(self, api_url='https://api.ai.qq.com/fcgi-bin/aai/aai_asr',
                 app_id='110????605', app_key='XeJaa????7uNHeyC'):
        super(BasicASR, self).__init__(api_url, app_id, app_key)

    def stt(self, audio_file, ext='wav', rate=16000):
        if ext == 'wav':
            wf = wave.open(audio_file)
            nf = wf.getnframes()
            audio_data = wf.readframes(nf)
            wf.close()
        else:
            raise Exception("Unsupport audio file format!")

        args = {
            'app_id': self.app_id,
            'time_stamp': str(int(time.time())),
            'nonce_str': '%.x' % random.randint(1048576, 104857600),
            'format': self.ext2idx[ext],
            'rate': str(rate),
            'speech': base64.b64encode(audio_data),
        }

        signiture = signify(args, self.app_key)
        args['sign'] = signiture
        resp = http_post(self.api_url, args)
        text = resp['data']['text'].encode('utf-8')

        return text


class BasicStreamASR(BaseASR):
    """ Online ASR from Tencent AI Lab
    https://ai.qq.com/doc/aaiasr.shtml
    """

    def __init__(self, api_url='https://api.ai.qq.com/fcgi-bin/aai/aai_asrs',
                 app_id='110????605', app_key='XeJaa????7uNHeyC'):
        super(BasicStreamASR, self).__init__(api_url, app_id, app_key)

    def stt(self, audio_file, ext='wav', rate=16000, chunk=4800):
        if type(audio_file) is str:
            if ext == 'wav':
                wf = wave.open(audio_file)
            else:
                raise Exception("Unsupport audio file format!")
        else:
            wf = audio_file

        total_len = wf.getnframes() * wf.getsampwidth()
        seq, end = 0, 0
        while end != 1:
            data = wf.readframes(chunk)
            length = len(data)
            end = int(length + seq >= total_len)

            resp = self.post_one_packet(data, rate, seq, end, ext=ext)

            seq += length

        return resp['data']['speech_text'].encode('utf-8')

    def post_one_packet(self, data, rate, seq, end, ext='wav', speech_id=0):
        args = {
            'app_id': self.app_id,
            'time_stamp': str(int(time.time())),
            'nonce_str': '%.x' % random.randint(1048576, 104857600),
            'format': self.ext2idx[ext],
            'rate': str(rate),
            'seq': str(seq),
            'len': str(len(data)),
            'end': str(end),
            'speech_id': str(speech_id),
            'speech_chunk': base64.b64encode(data),
        }

        signiture = signify(args, self.app_key)
        args['sign'] = signiture
        resp = http_post(self.api_url, args)

        return resp

    def post_one_packet_async(self, *args, **kwargs):
        thread = threading.Thread(target=self.post_one_packet, args=args, kwargs=kwargs)
        thread.daemon = True
        thread.start()
        return thread

def test_basic_asr():
    audio_files = ['wav/chinense_utterance.wav']
    asr_engine = BasicASR()
    for audio_file in audio_files:
        text = asr_engine.stt(audio_file, ext='wav')
        print(text)


def test_stream_asr():
    audio_files = ['wav/chinese_utterance.wav']
    asr_engine = BasicStreamASR()
    for audio_file in audio_files:
        text = asr_engine.stt(audio_file, ext='wav', chunk=16000)
        print(text)


if __name__ == '__main__':
    import pytest

    pytest.main([__file__, '-s'])
