import os
import numpy as np
import deepspeech
import pyaudio  # Required for getting audio from microphone
import speech_recognition as sr
from gtts import gTTS

# Initialize DeepSpeech model
model_path = "/home/pi/BMO/BMO-raspberry-pi/deepspeech-0.9.3-models.tflite"
scorer_path = "/home/pi/BMO/BMO-raspberry-pi/deepspeech-0.9.3-models.scorer"
model = deepspeech.Model(model_path)
model.enableExternalScorer(scorer_path)


# Configuration for capturing audio from microphone
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000  # DeepSpeech requires audio to be 16kHz
CHUNK = 1024

# Initialize PyAudio
audio = pyaudio.PyAudio()

def speak(text):
    tts = gTTS(text=text, lang='en')
    tts.save("response.mp3")
    os.system("mpg321 response.mp3")

def process_command(command):
    if "hello" in command:
        return "Hello! I'm BMO!"
    elif "how are you" in command:
        return "I'm doing great! Ready to play?"
    elif "hey bmo whats up" in command:
        return "who wants to play video games!"
    # ... add other basic commands here
    return "I'm not sure what you said. Can you try again?"

while True:
    # Start recording
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    print("Listening...")
    frames = []

    for _ in range(0, int(RATE / CHUNK * 3)):  # 3 seconds of audio
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()

    # Convert audio to numpy array and recognize using DeepSpeech
    audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
    text = model.stt(audio_data)
    print("You said:", text)

    response = process_command(text)
    print("BMO:", response)
    speak(response)
