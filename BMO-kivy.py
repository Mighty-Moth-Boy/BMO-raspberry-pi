from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.core.audio import SoundLoader
from kivy.uix.video import Video
from kivy.clock import Clock
import threading

import speech_recognition as sr
from fuzzywuzzy import process
from gtts import gTTS
import os
import random

TALKING_VIDEO = './Videos/BMO-talking.mp4'
SONG_IMAGE = './song-face.PNG' 

responses = {
    "hello": [
        {"response": "hello im bmo", "video": TALKING_VIDEO},
        {"response": "hi there!", "video": TALKING_VIDEO}
    ],
    "what time is it": [
        {"video": "./Videos/Adventure-Time-Intro.mp4"}
    ],
    "hey sing me a song": [
        {"video": TALKING_VIDEO, "audio": "./songs/Fly me to the Moon.mp3"},
        {"video": TALKING_VIDEO, "audio": "./songs/I Dont Want to Set the World on Fire.mp3"},
        {"video": TALKING_VIDEO, "audio": "./songs/Rises the Moon.mp3"}
    ],
    "stop": [
        {"response": "Shutting down. Goodbye!"}
    ],
}

image_directory = "./faces"
images = [os.path.join(image_directory, f) for f in os.listdir(image_directory) if f.endswith('.jpg')]

class BMOApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_playing = False  # Flag to check if video or audio is currently playing

    def build(self):
        self.layout = BoxLayout()
        self.image = Image(source=random.choice(images), allow_stretch=True)
        self.layout.add_widget(self.image)
        Clock.schedule_interval(self.listen_for_command, 10)  # Check for voice command every 10 seconds
        Clock.schedule_interval(self.change_face, 40)  # Change face every 40 seconds
        return self.layout

    def change_face(self, *args):
        self.image.source = random.choice(images)

    def play_audio(self, audio_path):
        sound = SoundLoader.load(audio_path)
        if sound:
            self.show_image_while_song_plays(SONG_IMAGE)
            sound.play()
            sound.bind(on_stop=self.on_audio_end)

    def show_image_while_song_plays(self, image_path):
        self.layout.clear_widgets()
        song_image = Image(source=image_path, allow_stretch=True)
        self.layout.add_widget(song_image)

    def on_audio_end(self, *args):
        self.is_playing = False
        self.end_song_display()

    def end_song_display(self, *args):
        self.layout.clear_widgets()
        self.image = Image(source=random.choice(images), allow_stretch=True)
        self.layout.add_widget(self.image)
        Clock.schedule_once(self.listen_for_command, 5)  # Delay for 5 seconds before listening again

    def listen_for_command(self, *args):
        if self.is_playing:  # If a video or audio is currently playing, don't listen for commands
            return
        
        r = sr.Recognizer()
        with sr.Microphone() as source:
            audio = r.listen(source)

        try:
            speech_text = r.recognize_google(audio)
            closest_match, score = process.extractOne(speech_text, responses.keys())
            if score >= 80:
                self.process_command(closest_match)
        except sr.UnknownValueError:
            self.speak("I don't know what you said")
        except sr.RequestError:
            self.speak("I'm having trouble understanding right now. Please check the connection or try again later.")

    def process_command(self, command):
        self.is_playing = True  # Set the flag to indicate that a video or audio will be playing
        if command == "stop":
            self.speak(responses["stop"][0]["response"])
            self.stop()  # This will stop the Kivy application
            return
        
        response_options = responses[command]
        selected_response = random.choice(response_options)
        if selected_response.get("response"):
            self.speak(selected_response["response"])
        if selected_response.get("video"):
            self.play_video(selected_response["video"])
        if selected_response.get("audio"):
            self.play_audio(selected_response["audio"])

    def play_video(self, video_path):
        self.layout.clear_widgets()
        video = Video(source=video_path, allow_stretch=True)
        video.bind(eos=self.on_video_end)
        self.layout.add_widget(video)
        video.state = 'play'

    def on_video_end(self, *args):
        self.is_playing = False
        self.layout.clear_widgets()
        self.image = Image(source=random.choice(images), allow_stretch=True)
        self.layout.add_widget(self.image)
        Clock.schedule_once(self.listen_for_command, 5)

    def speak(self, text):
        def play_tts_audio():
            tts = gTTS(text)
            tts.save("temp_audio.mp3")
            os.system("mpg321 temp_audio.mp3")

        # Calculate duration based on the length of text and play the talking video for that duration
        duration = len(text) * 0.1
        self.play_video_for_duration(TALKING_VIDEO, duration)
        threading.Thread(target=play_tts_audio).start()

    def play_video_for_duration(self, video_path, duration):
        self.layout.clear_widgets()
        video = Video(source=video_path, allow_stretch=True, duration=duration)
        video.bind(eos=self.on_video_end_for_duration)
        self.layout.add_widget(video)
        video.state = 'play'

    def on_video_end_for_duration(self, *args):
        self.layout.clear_widgets()
        self.image = Image(source=random.choice(images), allow_stretch=True)
        self.layout.add_widget(self.image)
        Clock.schedule_once(self.listen_for_command, 5)

BMOApp().run()
