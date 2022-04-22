#!/usr/bin/env python3

import argparse
import json
import os
import queue
import sounddevice as sd
import vosk
import sys

from argostranslate import package, translate

import pyttsx3

stop_listening = False

q = queue.Queue()

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if not stop_listening:
        if status:
            print(status, file=sys.stderr)
        q.put(bytes(indata))


# argos
if not os.path.exists("translate-es_en-1_0.argosmodel"):
    print ("Please download an einglish-spanish translation model from https://www.argosopentech.com/argospm/index/")
    print ("and unpack as 'translate-es_en-1_0.argosmodel' in the current folder.")
    sys.exit(2)
package.install_from_path('translate-es_en-1_0.argosmodel')
installed_languages = translate.get_installed_languages()
translation_es_en = installed_languages[1].get_translation(installed_languages[0])

# pyttsx3
engine = pyttsx3.init()
engine.setProperty('voice', "english-us")
engine.setProperty('rate', 150)


try:
    if not os.path.exists("model"):
        print ("Please download a vosk model for spanish language from https://alphacephei.com/vosk/models")
        print ("and unpack as 'model' in the current folder.")
        sys.exit(2)

    device_info = sd.query_devices(None, 'input')
    # soundfile expects an int, sounddevice provides a float:
    samplerate = int(device_info['default_samplerate'])

    model = vosk.Model('model')

    with sd.RawInputStream(samplerate=samplerate, blocksize = 8000, device=None, dtype='int16',
                            channels=1, callback=callback):
            print('#' * 80)
            print('Press Ctrl+C to stop the recording')
            print('#' * 80)

            rec = vosk.KaldiRecognizer(model, samplerate)
            while True:
                data = q.get()
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    if result['text']:
                        print('')
                        print('#' * 10, ' Text ', '#' * 10)
                        print('Text: ', result['text'])
                        translated = translation_es_en.translate(result['text'])
                        print('Translation: ', translated)
                        stop_listening = True
                        engine.say(translated)
                        engine.runAndWait()
                        stop_listening = False
                else:
                    partial_result = json.loads(rec.PartialResult())
                    if partial_result['partial']:
                        print('')
                        print('#' * 10, ' Partial ', '#' * 10)
                        print('Text: ', partial_result['partial'])
                        print('Translation: ', translation_es_en.translate(partial_result['partial']))

except KeyboardInterrupt:
    print('\nDone')
except Exception as e:
    print(type(e).__name__ + ': ' + str(e))
    sys.exit(1)
