from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.core.audio import SoundLoader
from kivy.uix.video import Video
from kivy.clock import Clock
import threading
import time
import speech_recognition as sr
from fuzzywuzzy import process
import os
import random

TALKING_VIDEO = './Videos/talking.mp4'

responses = {
    "hello": [
        {"audio": "./responses/hello-1.wav"},
        {"audio": "./responses/hello-2.wav"},
        {"audio": "./responses/hello-3.wav"}
    ],
    "how are you": [
        {"audio": "./responses/how-are-you-1.wav"},
        {"audio": "./responses/how-are-you-2.wav"},
        {"audio": "./responses/how-are-you-3.wav"}
    ],

    "sing me a song": [
        {"audio": "./songs/Fly me to the Moon.mp3", "picture": "./pictures/space-cowboy.jpg"},
        {"audio": "./songs/I Dont Want to Set the World on Fire.mp3", "picture": "./pictures/cowboy.PNG"},
        {"audio": "./songs/Rises the Moon.mp3", "picture": "./pictures/happy.PNG"},
        {"audio": "./songs/From The Start.mp3", "picture": "./pictures/song-face.PNG"}
    ],
    "tell me something funny":[
        {"audio": "./memes/SIX-CONSOLES.wav", "picture": "./pictures/song-face.PNG"},
    ],

    "what time is it": [
        {"video": "./Videos/Original-Intro.mp4"},
        {"video": "./Videos/Bad-Jubies-intro.mp4.mp4"},
        {"video": "./Videos/elements-intro.mp4.mp4"},
        {"video": "./Videos/Finale-intro.mp4.mp4"},
        {"video": "./Videos/Food-Chain-intro.mp4.mp4"},
        {"video": "./Videos/Islands-intro.mp4.mp4"},
        {"video": "./Videos/Pixel-intro.mp4.mp4"},
        {"video": "./Videos/Stakes-intro.mp4.mp4"}
    ],
    "tell me a story": [
        {"video": "./Videos/boat-story.mp4"},
        {"video": "./Videos/Robot-Cowboy.mp4"},
    ]
}

image_directory = "./faces"
images = [os.path.join(image_directory, f) for f in os.listdir(image_directory) if f.endswith('.jpg')]


class BMOApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_playing = False  # Flag to check if video or audio is currently playing
        self.max_video_duration = 0

    def build(self):
        self.layout = BoxLayout()
        self.image = Image(source=random.choice(images), allow_stretch=True)
        self.layout.add_widget(self.image)
        
        # Start with the initial greeting
        self.initial_greeting()
        
        return self.layout

    def initial_greeting(self):
        # Play the talking video and loop it for the duration of the audio
        initial_audio_path = "./responses/startup.mp3"
        self.talk_audio(initial_audio_path)

        # Schedule the listener to start after the audio finishes
        sound = SoundLoader.load(initial_audio_path)
        if sound:
            duration = sound.length
            Clock.schedule_once(self.listen_for_command, duration + 2)  # +2 seconds to give a brief pause before listening

    def change_face(self, *args):
        self.image.source = random.choice(images)

    def play_video_for_duration(self, video_path, duration):
        """Play a video and loop it for the specified duration."""
        self.layout.clear_widgets()
        self.video_duration = duration
        self.video_start_time = time.time()  # Store the starting time
        
        video = Video(source=video_path, allow_stretch=True)
        video.bind(eos=self.loop_video)
        self.layout.add_widget(video)
        video.state = 'play'
        
    def loop_video(self, instance, state):
        """Restart the video if it hasn't reached the specified duration."""
        elapsed_time = time.time() - self.video_start_time
        if elapsed_time < self.video_duration:
            instance.seek(0)
            instance.state = 'play'
        else:
            instance.state = 'stop'
            self.layout.clear_widgets()
            self.image = Image(source=random.choice(images), allow_stretch=True)
            self.layout.add_widget(self.image)

    def check_video_position(self, instance, value):
        """Stop the video if it exceeds the specified duration."""
        if value >= self.max_video_duration:
            instance.state = 'stop'
            self.layout.clear_widgets()
            self.image = Image(source=random.choice(images), allow_stretch=True)
            self.layout.add_widget(self.image)

    def talk_audio(self, audio_path):
        """Play an audio and loop a 1-second video until the audio is finished."""
        self.is_playing = True
        sound = SoundLoader.load(audio_path)
        if sound:
            duration = sound.length
            self.play_video_for_duration(TALKING_VIDEO, duration)
            sound.play()
            sound.bind(on_stop=self.on_audio_end)

    def play_static_audio_with_image(self, audio_path, image_path):
        """Play an audio and display a specified image until the audio finishes."""
        self.is_playing = True
        self.show_image_while_song_plays(image_path)
        sound = SoundLoader.load(audio_path)
        if sound:
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
            # if "hey BeeMo" not in speech_text.upper():  # Checks if wake word "BMO" is in the recognized text
            #     return

            closest_match, score = process.extractOne(speech_text, responses.keys())
            if score >= 80:
                self.process_command(closest_match)
        except sr.UnknownValueError:
            self.talk_audio("./responses/unknown-value-error.wav")  # Placeholder for error audio
        except sr.RequestError:
            self.talk_audio("./responses/fatal-error.wav")  # Placeholder for error audio

    def process_command(self, command):
        self.is_playing = True  
        if command == "goodnight":
            self.talk_audio(responses["goodnight"][0]["audio"])
            self.stop()  # This will stop the Kivy application
            return
        
        response_options = responses[command]
        selected_response = random.choice(response_options)
        
        if selected_response.get("audio"):
            if selected_response.get("picture"):
                # Display the specified picture with the audio
                self.play_static_audio_with_image(selected_response["audio"], selected_response["picture"])
            else:
                # If there's no picture, use the talking video as default
                self.talk_audio(selected_response["audio"])
        
        # If there's a video (and it's not the TALKING_VIDEO), play it
        if selected_response.get("video") and selected_response.get("video") != TALKING_VIDEO:
            self.play_video(selected_response["video"])

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


BMOApp().run()