# -*- coding: utf-8 -*-
"""
Created on Sun Feb 13 22:47:21 2018

@author: keding
"""
from __future__ import print_function

import os
import time

from snowboy.snowboydetect import SnowboyDetect
from audio import AudioStream, play


class Wakeup(object):
    pass


class Snowboy(Wakeup):

    """Keyword Detector by [snowboy](https://github.com/Kitt-AI/snowboy)
    """

    def __init__(self, models, sensitivity, audio_gain=1.):
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        resource = os.path.join(cur_dir, "snowboy/resources/common.res")

        if type(models) != list:
            models = [models]
        models = [os.path.join(cur_dir, model) for model in models]
        model_str = ','.join(models)

        if type(sensitivity) != list:
            sensitivity = [sensitivity] * len(models)
        sensitivity_str = ','.join([str(s) for s in sensitivity])

        assert len(models) == len(sensitivity), \
            "number of hotwords in decoder_model (%d) and sensitivity " \
            "(%d) does not match" % (len(models), len(sensitivity))

        self.detector = SnowboyDetect(
            resource_filename=resource.encode(),
            model_str=model_str.encode())
        self.detector.SetSensitivity(sensitivity_str.encode())
        self.detector.SetAudioGain(audio_gain)

        self.stream = AudioStream(chunk=16 * 100, buffer_bytes=16000 * 2)
        self.stream.start()

    def start_detect(self, sleep_time=0.05, callback=None):
        while True:
            data = self.stream.get()

            if len(data) == 0:
                time.sleep(sleep_time)
                continue

            ans = self.detector.RunDetection(data)
            if ans <= 0:
                time.sleep(sleep_time)
            else:
                break

        self.stream.stop()

        if callback:
            callback(ans)

        return ans


def test_snowboy():
    def callback(keyword):
        ding = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'snowboy/resources/ding.wav')
        dong = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'snowboy/resources/dong.wav')
        if keyword == 1:
            play(ding)
        else:
            play(dong)

    models = ['snowboy/resources/models/snowboy.umdl',
              'snowboy/resources/models/alexa_02092017.umdl']
    kws = Snowboy(models, 0.5)
    print('Wake me up~')
    kws.start_detect(callback=callback)


if __name__ == '__main__':
    import pytest

    pytest.main([__file__, '-s'])
