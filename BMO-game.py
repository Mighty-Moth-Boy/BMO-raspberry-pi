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
        {"video": TALKING_VIDEO, "audio": "song_audio1.mp3"},
        {"video": TALKING_VIDEO, "audio": "song_audio2.mp3"},
        {"video": TALKING_VIDEO, "audio": "song_audio3.mp3"}
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
        print("Say something...")
        audio = r.listen(source)

    try:
        return r.recognize_google(audio)
    except sr.UnknownValueError:
        print("Sorry, I couldn't understand that. Please repeat.")
        return "unrecognized"  # return a value indicating the speech was not understood
    except sr.RequestError:
        print("API unavailable. Please check your internet connection or try again later.")
        return "error"  # return a value indicating there was an error with the request


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
    screen = pygame.display.set_mode((640, 480))  # Set up display in the main thread
    last_speech_recognition_time = 0
    speech_recognition_interval = 10  # Interval (in seconds) between consecutive speech recognitions

    while True:
        current_time = time.time()

        # If enough time has passed since the last speech recognition, try recognizing again
        if current_time - last_speech_recognition_time > speech_recognition_interval:
            speech_text = recognize_speech()
            
            if speech_text == "unrecognized":
                speak_text("I didn't catch that. Can you say it again?")
                last_speech_recognition_time = current_time
                continue
            elif speech_text == "error":
                speak_text("I'm having trouble understanding right now. Please check the connection or try again later.")
                last_speech_recognition_time = current_time
                continue

            closest_match, score = process.extractOne(speech_text, responses.keys())
            if score >= 80:
                response_options = responses[closest_match]
                selected_response = random.choice(response_options)

                if selected_response.get("response"):
                    speak_text(selected_response["response"])
                if selected_response.get("video"):
                    play_video(selected_response["video"])
                if selected_response.get("audio"):
                    play_audio(selected_response["audio"])

            last_speech_recognition_time = current_time
        else:
            # Display a random image
            selected_image = random.choice(images)
            img = pygame.image.load(selected_image)
            screen.blit(img, (0, 0))
            pygame.display.flip()
            time.sleep(image_display_time)



if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        pygame.quit()
