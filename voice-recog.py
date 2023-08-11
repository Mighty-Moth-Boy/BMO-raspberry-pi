import os
import speech_recognition as sr
from fuzzywuzzy import fuzz
from gradio_client import Client
import random

# Set up Gradio client
client = Client("https://2e4eb32d100d705a8e.gradio.live/")

# Define the list of potential responses
responses = {
    "hello": ["Hello! I'm BMO!", "Hi there! BMO at your service!", "hey... wait wheres finn and jake?"],
    "how are you": ["I'm doing great! Ready to play?", "Fantastic! How about you?", "I'm a computer, so I don't have feelings, but I'm running smoothly!"],
}

recognizer = sr.Recognizer()

def speak(text):
    api_key = "70174fc2caa769dafde9faff20cb5777"
    result = client.predict(
        api_key,           # API Key for ElevenLabs
        text,              # Input text
        "Elli",            # Voice
        "en",              # Language
        fn_index=5
    )
    # The result should contain the transformed audio URL. Download and save this to "response.mp3"
    # You might need to further process the result to get the exact audio URL.
    audio_url = result[0]   # Adjust this if the structure of result is different.
    os.system(f"wget {audio_url} -O response.mp3")
    os.system("mpg321 response.mp3")

import glob

# ... [rest of the imports and code]

def play_random_song():
    # List all the mp3 files in the songs directory
    songs = glob.glob("./BMO-songs/*.mp3")
    
    # Choose a song at random
    song = random.choice(songs)
    
    # Play the chosen song
    os.system(f"mpg321 {song}")

def process_command(command):
    for key, possible_responses in responses.items():
        if fuzz.partial_ratio(command, key) > 80:
            return random.choice(possible_responses)
    if fuzz.partial_ratio(command, "sing me a song") > 80:
        play_random_song()
        return "Playing a song for you!"
    return "What?"

while True:
    with sr.Microphone() as source:
        print("Listening...")
        audio_data = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio_data)
            print("You said:", text)
            
            response = process_command(text)
            print("BMO:", response)
            speak(response)
            
        except sr.UnknownValueError:
            print("Sorry I did not hear your request, Please repeat again.")
