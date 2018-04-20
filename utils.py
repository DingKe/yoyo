# -*- coding: utf-8 -*-
"""
Created on Sun Feb 12 10:17:54 2018

@author: keding
"""
import requests
import urllib
import hashlib
import json
import subprocess
import time
from contextlib import contextmanager
from ctypes import *


def md5(string):
    md = hashlib.md5()
    md.update(string)
    md5 = md.hexdigest().upper()
    return md5


def urlencode(args):
    tuples = [(k, args[k]) for k in sorted(args.keys()) if args[k]]
    query_str = urllib.urlencode(tuples)
    return query_str


def signify(args, app_key):
    query_str = urlencode(args)
    query_str = query_str + '&app_key=' + app_key
    signiture = md5(query_str)
    return signiture


def http_post(api_url, args):
    resp = requests.post(url=api_url, data=args)
    resp = json.loads(resp.text)
    return resp


def cmd_exists(cmd):
    return subprocess.call('type ' + cmd, shell=True,
                           stdin=subprocess.PIPE, stdout=subprocess.PIPE) == 0


def py_error_handler(*args):
    pass


ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p,
                               c_int, c_char_p,
                               c_int, c_char_p)

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)


@contextmanager
def no_alsa_error():
    try:
        asound = cdll.LoadLibrary('libasound.so')
        asound.snd_lib_error_set_handler(c_error_handler)
        yield
        asound.snd_lib_error_set_handler(None)
    except:
        yield
        pass
