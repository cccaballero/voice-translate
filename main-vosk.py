#!/usr/bin/env python3

# Import necessary libraries
import json      # For handling JSON data
import os        # For file and directory operations
import queue     # For thread-safe queue operations
import sounddevice as sd  # For audio input/output
import vosk      # Offline speech recognition library
import sys       # For system-specific functions and variables


def main():
    # Flag to control the recording loop
    stop_listening = False

    # Create a thread-safe queue to pass audio data between threads
    q = queue.Queue()

    def callback(indata, frames, time, status):
        """
        Callback function that's called for each audio block from the microphone.
        Runs in a separate thread from the main program.
        
        Args:
            indata: The audio data as a numpy array
            frames: Number of frames in the audio block
            time: Timestamp information
            status: Status flags from the audio system
        """
        if not stop_listening:
            if status:
                print(status, file=sys.stderr)
            # Convert audio data to bytes and put it in the queue
            q.put(bytes(indata))

    try:
        # Check if the Vosk model directory exists
        if not os.path.exists("model"):
            print("Please download a model for your language from https://alphacephei.com/vosk/models")
            print("and unpack as 'model' in the current folder.")
            sys.exit(2)


        # Get information about the default audio input device
        device_info = sd.query_devices(None, 'input')
        # Get the sample rate from the device (converting from float to int)
        samplerate = int(device_info['default_samplerate'])

        # Load the Vosk speech recognition model
        model = vosk.Model('model')

        # Open an audio input stream
        with sd.RawInputStream(samplerate=samplerate, 
                             blocksize=8000,  # Size of audio blocks to process
                             device=None,     # Use default input device
                             dtype='int16',   # Audio data type (16-bit PCM)
                             channels=1,      # Mono audio
                             callback=callback):  # Function to call for each audio block
                
                print('#' * 80)
                print('Press Ctrl+C to stop the recording')
                print('#' * 80)


                # Create a Kaldi speech recognizer
                rec = vosk.KaldiRecognizer(model, samplerate)
                
                # Main processing loop
                while True:
                    # Get the next audio block from the queue
                    data = q.get()
                    
                    # Process the audio with Vosk
                    if rec.AcceptWaveform(data):
                        # If we have a final recognition result
                        result = json.loads(rec.Result())
                        if result['text']:  # If there's recognized text
                            print('')
                            print(f'{"#" * 10} Text {"#" * 10}')
                            print('Text: ', result['text'])
                    else:
                        # Get partial recognition results (while still speaking)
                        partial_result = json.loads(rec.PartialResult())
                        if partial_result['partial']:  # If there's partial text
                            print('')
                            print(f'{"#" * 10} Partial {"#" * 10}')
                            print('Text: ', partial_result['partial'])


    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print('\nDone')
    except Exception as e:
        # Handle any other exceptions
        print(type(e).__name__ + ': ' + str(e))
        sys.exit(1)


# Standard Python idiom to execute main() when the script is run directly
if __name__ == '__main__':
    main()
