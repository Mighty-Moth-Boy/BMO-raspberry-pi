from gradio_client import Client
from gtts import gTTS
import os
import pygame


def play_audio(file_path):
	# Initialize pygame mixer
	pygame.mixer.init()

	# Load the audio file
	pygame.mixer.music.load(file_path)

	# Play the audio
	pygame.mixer.music.play()

	# Keep the program running while the audio is playing
	while pygame.mixer.music.get_busy():
		pygame.time.Clock().tick(10)


# Create a TTS audio file using gTTS
text_to_convert = "4 seconds, it took you 4 fucking seconds to piss me off"
tts = gTTS(text=text_to_convert, lang='en')
tts_file_path = "sample_tts_audio.mp3"
tts.save(tts_file_path)

# Initialize the Gradio client
client = Client("http://localhost:7860/")

# Make the API call using the generated TTS audio file
result = client.predict(
				"0",	# str  in 'Pitch Up key' Textbox component
				tts_file_path,	# str (filepath or URL to file) in 'Original Audio' Audio component
				"./BMO.index",	# str (filepath or URL to file) in 'Index' File component
				"harvest",	# str  in 'Pitch Collection Method' Radio component
				"./BMO.pth",	# str (filepath or URL to file) in 'Model' File component
				0,	# int | float (numeric value between 0.0 and 1.0) in 'Search Feature Ratio' Slider component
				"cuda:0",	# str (Option from: ['cuda:0', 'cpu', 'mps']) in 'Device' Dropdown component
				False,	# bool  in 'Use half precision model (Depends on GPU support)' Checkbox component
				3,	# int | float (numeric value between 0 and 10) in 'Filter Radius (Pitch)' Slider component
				0,	# int | float (numeric value between 0 and 48000) in 'Resample Sample-rate (Bug)' Slider component
				1,	# int | float (numeric value between 0.0 and 1.0) in 'Voice Envelope Normalizaiton' Slider component
				0.3,	# int | float (numeric value between 0.0 and 0.5) in 'Protect Breath Sounds' Slider component
				fn_index=87
)

print(result)
play_audio(result)