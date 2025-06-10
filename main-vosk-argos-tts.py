#!/usr/bin/env python3

# Import necessary libraries
import json      # For handling JSON data
import os        # For file and directory operations
import queue     # For thread-safe queue operations
import sounddevice as sd  # For audio input/output
import vosk      # Offline speech recognition library
import sys       # For system-specific functions and variables

# Import Argos Translate components
from argostranslate import package  # For managing translation packages
from argostranslate.translate import translate  # For text translation

# Import Text-to-Speech components
from TTS.api import TTS  # For converting text to speech
import playsound         # For playing the generated audio

# Define source and target languages
# Using language codes: 'es' for Spanish, 'en' for English
from_code = "es"
to_code = "en"


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

    # Setup Argos Translate
    print("Setting up Argos Translate...")
    # Update the package index to get the latest translation models
    package.update_package_index()
    # Get list of available translation packages
    available_packages = package.get_available_packages()
    # Find the specific translation package we need (Spanish to English)
    package_to_install = next(
        filter(
            lambda x: x.from_code == from_code and x.to_code == to_code, 
            available_packages
        )
    )
    # Download and install the translation package
    package.install_from_path(package_to_install.download())
    print("Translation model ready!")

    print("Initializing Text-to-Speech...")
    # Initialize the Text-to-Speech engine using a pre-trained Tacotron2 model for English speech synthesis
    tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC_ph")
    print("TTS engine ready!")
    

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
            print('Speak in Spanish to hear the English translation')
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
                        print(f'{"#" * 10} Recognized Text (Spanish) {"#" * 10}')
                        print('Spanish: ', result['text'])
                        # Translate the recognized text using Argos Translate
                        translated = translate(result['text'], from_code, to_code)
                        print(f'{"#" * 10} Translation (English) {"#" * 10}')
                        print('English: ', translated)

                        # Pause listening to avoid recording the TTS output
                        stop_listening = True

                        try:
                            # Convert the translated text to speech
                            print("Generating speech...")
                            tts.tts_to_file(text=translated, file_path='output.wav')

                            # Play the generated speech
                            print("Playing translation...")
                            playsound.playsound('output.wav')
                        except Exception as e:
                            print(f"Error in TTS: {e}")
                        finally:
                            # Resume listening
                            stop_listening = False
                            print("\nReady to listen again...")

                else:
                    # Get partial recognition results (while still speaking)
                    partial_result = json.loads(rec.PartialResult())
                    if partial_result['partial']:  # If there's partial text
                        print('')
                        print(f'{"#" * 10} Partial Recognition {"#" * 10}')
                        print('Spanish (partial): ', partial_result['partial'])
                        # Translate the partial text as well (for real-time feedback)
                        print('English (partial): ', translate(partial_result['partial'], from_code, to_code))

    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print('\nTranslation stopped by user')
    except Exception as e:
        # Handle any other exceptions
        print("An error occurred:")
        print(type(e).__name__ + ': ' + str(e))
        sys.exit(1)


# Standard Python idiom to execute main() when the script is run directly
if __name__ == '__main__':
    main()
