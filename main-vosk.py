#!/usr/bin/env python3

import argparse
import json
import os
import queue
import sounddevice as sd
import vosk
import sys


def main():
    stop_listening = False

    q = queue.Queue()

    def callback(indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if not stop_listening:
            if status:
                print(status, file=sys.stderr)
            q.put(bytes(indata))


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
                    else:
                        partial_result = json.loads(rec.PartialResult())
                        if partial_result['partial']:
                            print('')
                            print('#' * 10, ' Partial ', '#' * 10)
                            print('Text: ', partial_result['partial'])

    except KeyboardInterrupt:
        print('\nDone')
    except Exception as e:
        print(type(e).__name__ + ': ' + str(e))
        sys.exit(1)


if __name__ == '__main__':
    main()
