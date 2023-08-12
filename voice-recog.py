import os
import speech_recognition as sr
from fuzzywuzzy import fuzz
from gradio_client import Client
from gtts import gTTS
import threading
import random
import time

# Set up Gradio client
client = Client("http://localhost:7897/")

# Set up speech recognizer
recognizer = sr.Recognizer()

#constants for idle and talking video
IDLE_VIDEO = "./Videos/BMO-idle.mp4"
TALKING_VIDEO = "./Videos/BMO-talking.mp4"


responses = {
    "hello": ("Hello! I'm BeeMoe!", TALKING_VIDEO),
    "im bored": ("who wants to play video games?", TALKING_VIDEO),
    "what time is it": ("", "./Videos/Adventure-Time-Intro.mp4"),
    "beemo are you a cowboy?": ("", "./Videos/Robot-Cowboy.mp4")
    # ... other responses ...
}



def play_video(video_path, duration=None):
    #"""Play a video using omxplayer for a specified duration."""
    if duration:
        os.system(f"timeout {duration} omxplayer {video_path}")
    else:
        os.system(f"omxplayer {video_path}")


def play_idle_video():
    #"""Continuously play the idle video."""
    while True:
        play_video(IDLE_VIDEO)


def speak(text):
    tts = gTTS(text=text, lang='en')
    tts.save("response.mp3")


def process_command(command):
    for key, (response_text, response_video) in responses.items():
        if fuzz.partial_ratio(command, key) > 80:
            # Calculate duration based on length of response_text
            duration = len(response_text) * 0.1
            play_response_and_video(response_text, response_video, duration)
            return
    # If no specific response matches
    play_response_and_video("what?", TALKING_VIDEO, 2)


def play_response_and_video(text, video_path, duration):
    # Thread for playing video
    video_thread = threading.Thread(target=play_video, args=(video_path, duration))
    
    # Thread for speaking the response
    speak_thread = threading.Thread(target=speak, args=(text))
    
    # Start both threads
    video_thread.start()
    speak_thread.start()
    
    # Wait for both threads to finish
    video_thread.join()
    speak_thread.join()



# Example usage:
# play_response_and_video("Hello! I'm BeeMoe!", TALKING_VIDEO)


# Main loop
try:
    while True:
        with sr.Microphone() as source:
            print("Listening...")
            audio_data = recognizer.listen(source)
            try:
                text = recognizer.recognize_google(audio_data)
                print("You said:", text)
                process_command(text)

            except sr.UnknownValueError:
                print("Sorry mic no worky :( ")
except KeyboardInterrupt:
    # Handle Ctrl+C to exit
    print("Exiting...")

