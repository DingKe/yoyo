# yoyo
A python based barebone framework for Voice Assistant.

* HW: Raspberry Pi 3 Model B
* OS: [Raspbian Stretch](https://www.raspberrypi.org/downloads/raspbian/)
* Mic: Playstation Eye (USB)
* Speaker: Dual speaker with external power (AV)

## 1. Audio I/O
Audio I/O using [PortAudio](http://www.portaudio.com/) (python wrapper [pyaudio](http://people.csail.mit.edu/hubert/pyaudio/)).

## 2. ASR
Streaming ASR engine from [Tencent AI Lab](https://ai.qq.com/product/aaiasr.shtml). See this [post](https://blog.csdn.net/JackyTintin/article/details/80003146) for more information.

## 3. TTS
TTS engine from [Tencent AI Lab](http://ai.qq.com/doc/aaitts.shtml).

## 4. Wakeup
Keyword Detector via [snowboy](https://github.com/Kitt-AI/snowboy).

## 5. VAD
Voice Activity Detection using [webrtc's VAD](https://chromium.googlesource.com/external/webrtc/stable/webrtc/+/master/common_audio/vad).

## Undergoing
* DM

## TODO
* NLU
