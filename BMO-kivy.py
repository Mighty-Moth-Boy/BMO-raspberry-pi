from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.video import Video
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from gtts import gTTS
import speech_recognition as sr
from fuzzywuzzy import process
import random
import os

TALKING_VIDEO = './Videos/BMO-talking.mp4'

responses = {
    "hello": [
        {"response": "hello im bmo", "video": TALKING_VIDEO},
        {"response": "hi there!", "video": TALKING_VIDEO}
    ],
    "what time is it": [
        {"response": "", "video": "./Videos/Adventure-Time-Intro.mp4"}
    ],
    "hey sing me a song": [
        {"video": TALKING_VIDEO, "audio": "./songs/Fly me to the Moon.mp3"},
        {"video": TALKING_VIDEO, "audio": "./songs/I Dont Want to Set the World on Fire.mp3"},
        {"video": TALKING_VIDEO, "audio": "./songs/Rises the Moon.mp3"}
    ]
}

# Directory where images are stored
image_directory = "./faces"
images = [os.path.join(image_directory, f) for f in os.listdir(image_directory) if f.endswith('.jpg')]


class BMOApp(App):
    def build(self):
        self.display = Image(source=random.choice(images))
        Clock.schedule_interval(self.check_for_speech, 10)
        return self.display


    def check_for_speech(self, *args):
        speech_text = self.recognize_speech()
        if speech_text == "unrecognized":
            self.speak_text("I didn't catch that. Can you say it again?")
        elif speech_text == "error":
            self.speak_text("I'm having trouble understanding right now. Please check the connection or try again later.")
        else:
            closest_match, score = process.extractOne(speech_text, responses.keys())
            if score >= 80:
                response_options = responses[closest_match]
                selected_response = random.choice(response_options)
                if selected_response.get("response"):
                    self.speak_text(selected_response["response"])
                if selected_response.get("video"):
                    self.play_video(selected_response["video"])
                if selected_response.get("audio"):
                    self.play_audio(selected_response["audio"])


    def recognize_speech(self):
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


    def speak_text(self, text):
        tts = gTTS(text)
        tts.save("temp_audio.mp3")
        self.play_audio("temp_audio.mp3")


    def play_audio(self, audio_path):
        sound = SoundLoader.load(audio_path)
        if sound:
            sound.play()


    def play_video(self, video_path):
        # For now, we'll simply switch the source of the display to the video
        # This will replace the image with the video.
        self.display.source = video_path
        self.display.play = True

if __name__ == "__main__":
    BMOApp().run()
