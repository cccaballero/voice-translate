#!/usr/bin/env python3

import json
import os
import queue
import sounddevice as sd
import vosk
import sys

from argostranslate import package
from argostranslate.translate import translate

from TTS.api import TTS
import playsound


from_code = "es"
to_code = "en"


def main():
    stop_listening = False

    q = queue.Queue()

    def callback(indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if not stop_listening:
            if status:
                print(status, file=sys.stderr)
            q.put(bytes(indata))

    # argos
    package.update_package_index()
    available_packages = package.get_available_packages()
    package_to_install = next(
        filter(
            lambda x: x.from_code == from_code and x.to_code == to_code, available_packages
        )
    )
    package.install_from_path(package_to_install.download())

    # TTS
    device = "cpu"
    print(TTS().list_models().list_models())
    tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC_ph")
    

    try:
        if not os.path.exists("model"):
            print ("Please download a model for your language from https://alphacephei.com/vosk/models")
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
                            translated = translate(result['text'], from_code, to_code)
                            print('Translation: ', translated)
                            stop_listening = True
                            tts.tts_to_file(text=translated, file_path='output.wav')
                            playsound.playsound('output.wav')
                            stop_listening = False
                    else:
                        partial_result = json.loads(rec.PartialResult())
                        if partial_result['partial']:
                            print('')
                            print('#' * 10, ' Partial ', '#' * 10)
                            print('Text: ', partial_result['partial'])
                            print('Translation: ', translate(partial_result['partial'], from_code, to_code))

    except KeyboardInterrupt:
        print('\nDone')
    except Exception as e:
        print(type(e).__name__ + ': ' + str(e))
        sys.exit(1)


if __name__ == '__main__':
    main()
