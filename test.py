from gradio_client import Client
from gtts import gTTS
import os

client = Client("https://8a050ec6d496eaca5d.gradio.live/")

def test_speak(text):
    tts = gTTS(text=text, lang='en')
    tts.save("test_response.mp3")
    os.system("mpg321 test_response.mp3")

test_speak("This is a test.")


def speak_as_bmo():
    result = client.predict(
            fn_index=0
    )
    print(f"LOOK HERE => {result}")
    audio_url = result[0]   # Adjust this if the structure of result is different.
    os.system(f"wget {audio_url} -O response.mp3")
    os.system("mpg321 response.mp3")

speak_as_bmo()