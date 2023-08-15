import pygame
import speech_recognition as sr
from fuzzywuzzy import process
from gtts import gTTS
import os
import threading
import time
import random

# Initialize pygame
pygame.init()

TALKING_VIDEO = './Videos/BMO-talking.mp4'

responses = {
    "hello": [
        {"response": "hello im bmo", "video": TALKING_VIDEO},
        {"response": "hi there!", "video": TALKING_VIDEO}
    ],
    "what time is it": [
        {"response": "", "video": "adventuretime_intro1.mp4"},
        {"response": "", "video": "adventuretime_intro2.mp4"}
    ],
    "hey sing me a song": [
        {"response": "", "audio": "song_audio1.mp3"},
        {"response": "", "audio": "song_audio2.mp3"},
        {"response": "", "audio": "song_audio3.mp3"}
    ]
}


# Directory where images are stored
image_directory = "./faces"
images = [os.path.join(image_directory, f) for f in os.listdir(image_directory) if f.endswith('.jpg')]

image_display_time = 5

display_images_event = threading.Event()

def play_video(video_path):
    screen = pygame.display.set_mode((640, 480))
    movie = pygame.movie.Movie(video_path)
    movie.play()
    while movie.get_busy():
        pygame.time.Clock().tick(25)

def speak_text(text):
    tts = gTTS(text)
    tts.save("temp_audio.mp3")
    play_audio("temp_audio.mp3")

def play_audio(audio_path):
    pygame.mixer.music.load(audio_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(25)

def recognize_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
    return r.recognize_google(audio)

def display_images_loop():
    screen = pygame.display.set_mode((640, 480))
    while True:
        selected_image = random.choice(images)
        img = pygame.image.load(selected_image)
        screen.blit(img, (0, 0))
        pygame.display.flip()
        for _ in range(image_display_time):
            time.sleep(1)
            if not display_images_event.is_set():
                return

def main_loop():
    threading.Thread(target=display_images_loop).start()

    while True:
        speech_text = recognize_speech()
        closest_match, score = process.extractOne(speech_text, responses.keys())

        if score >= 80:
            display_images_event.clear()
            response_options = responses[closest_match]
            selected_response = random.choice(response_options)
            
            if selected_response.get("response"):
                speak_text(selected_response["response"])
            if selected_response.get("video"):
                play_video(selected_response["video"])
            if selected_response.get("audio"):
                play_audio(selected_response["audio"])

            display_images_event.set()

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        pygame.quit()
