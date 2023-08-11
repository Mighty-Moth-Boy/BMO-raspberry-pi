import os
import speech_recognition as sr
from fuzzywuzzy import fuzz
from gradio_client import Client

# Set up Gradio client
client = Client("https://e99ee63ec117b91eee.gradio.live/")

# Define the list of potential responses
responses = {
    "hello": ["Hello! I'm BMO!", "Hi there! BMO at your service!", "hey... wait wheres finn and jake?"],
    "how are you": ["I'm doing great! Ready to play?", "Fantastic! How about you?", "I'm a computer, so I don't have feelings, but I'm running smoothly!"],
}

recognizer = sr.Recognizer()

def speak(text):
    result = client.predict(
        text,  # Input text
        text,  # API Key for ElevenLabs (or leave empty for GoogleTTS)
        "Adam",  # Voice
        "en",  # Language
        fn_index=5
    )
    # The result should contain the transformed audio URL. Download and save this to "response.mp3"
    # You might need to further process the result to get the exact audio URL.
    
    os.system("mpg321 response.mp3")

def process_command(command):
    for key, possible_responses in responses.items():
        if fuzz.partial_ratio(command, key) > 80:
            return random.choice(possible_responses)
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
