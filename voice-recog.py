import os
import numpy as np
import deepspeech
import pyaudio  # Required for getting audio from microphone
import speech_recognition as sr
from gtts import gTTS
from fuzzywuzzy import fuzz
import random


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
    # Define a threshold for fuzzy matching. If similarity is above this threshold, it's a match.
    threshold = 85
    
    # Command-response mapping
    responses = {
        "hello": ["Hello! I'm BMO!", "Hi! BMO here!", "oh hello, wheres finn and jake??"],
        "how are you": ["I'm doing great! Ready to play?", "Fantastic! How about you?", "Awesome! Let's have some fun!"],
        "hey whats up": [ "Not much, just being BMO!", "Just hanging around. How about you?"],
        "im bored": ["who wants to play video games!"]

# on startup: "Who wants to play video games!", on shutdown: "battery low, shutting down"

        # Guess who's late for their video chat
        # All right, last night, an electric presence came into my room and said, "BMO, I need your perfect body to host the human incarnation of a baby!"
        # I think I am dying. But that's okay, BMO always bounces back!
        # ... add other basic commands here
    }

    # Loop through the commands and see which one has the highest similarity
    best_match = None
    highest_ratio = 0
    for key in responses.keys():
        current_ratio = fuzz.partial_ratio(command, key)
        if current_ratio > highest_ratio:
            highest_ratio = current_ratio
            best_match = key
    
    # If the highest similarity is above the threshold, return a random response from the matched command
    if highest_ratio > threshold:
        return random.choice(responses[best_match])
    
    return "What?"

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





