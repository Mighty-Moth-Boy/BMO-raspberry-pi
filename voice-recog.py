import speech_recognition as sr
from gtts import gTTS
import os

recognizer = sr.Recognizer()

def speak(text):
    tts = gTTS(text=text, lang='en')
    tts.save("response.mp3")
    os.system("mpg321 response.mp3")

def process_command(command):
    # Basic commands
    if "hello" in command:
        return "Hello! I'm BMO!"
    elif "how are you" in command:
        return "I'm doing great! Ready to play?"
    # ... add other basic commands here

    # If no basic command is recognized, use GPT (or a placeholder for now)
    return "I'm not sure what you said. Can you try again?"


while True:
    with sr.Microphone(device_index=1) as source:
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