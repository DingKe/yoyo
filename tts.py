# -*- coding: utf-8 -*-
"""
Created on Sun Feb 11 10:39:18 2018

@author: keding
"""
from __future__ import print_function

import os
import tempfile
import time
import random
import base64

from audio import play
from utils import *


class BaseTTS(object):
    pass


class BasicTTS(BaseTTS):

    """ Online TTS from Tencent AI Lab
    http://ai.qq.com/doc/aaitts.shtml
    """

    ext2idx = {'pcm': '1', 'wav': '2', 'mp3': '3'}
    speakers = [1, 5, 6, 7]

    def __init__(self, api_url='https://api.ai.qq.com/fcgi-bin/aai/aai_tts',
                 app_id='110????605', app_key='XeJaa????7uNHeyC',
                 cache_dir=None):
        self.api_url = api_url
        self.app_id = app_id
        self.app_key = app_key
        self.cache_dir = cache_dir or tempfile.mkdtemp()
        self.lookup = {}

        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def __del__(self):
        files = self.lookup.values()
        for file in files:
            os.remove(file)

        try:
            os.rmdir(self.cache_dir)
        except:
            pass

    def tts(self, text, speaker=1, ext='wav', speed=100,
            volume=10, aht=0, apc=58):
        hash = md5(text)

        if hash in self.lookup:
            return self.lookup[hash]
        else:
            file_name = os.path.join(
                self.cache_dir, '%d.%s' % (len(self.lookup), ext))
            self.lookup[hash] = file_name

        if speaker not in self.speakers:
            speaker = 1

        args = {
            'app_id': self.app_id,
            'time_stamp': str(int(time.time())),
            'nonce_str': '%.x' % random.randint(1048576, 104857600),
            'speaker': str(speaker),
            'format': self.ext2idx[ext],
            'volume': str(volume),
            'speed': str(speed),
            'text': text,
            'aht': str(aht),
            'apc': str(apc),
        }

        signiture = signify(args, self.app_key)
        args['sign'] = signiture
        resp = http_post(self.api_url, args)

        data = resp['data']
        speech = base64.b64decode(data['speech'])
        with open(file_name, "wb") as fptr:
            fptr.write(speech)

        return file_name

    def say(self, text, **kwargs):
        speech_file = self.tts(text, **kwargs)
        play(speech_file)


def test_tts():
    texts = ['早上好!', '即将为您播放周杰伦的《简单爱》。', '早上好!',
             '北京今天晴转多云，微风，空气质量优']
    tts_engine = BasicTTS()
    for text in texts:
        speech_file = tts_engine.tts(text, ext='wav', speaker=6, volume=10)
        play(speech_file)
        tts_engine.say(text, ext='wav', speaker=6, volume=10)


if __name__ == '__main__':
    import pytest

    pytest.main([__file__, '-s'])
