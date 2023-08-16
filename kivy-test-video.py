from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.video import Video

class VideoApp(App):
    def build(self):
        layout = BoxLayout()
        video = Video(source="./Videos/Adventure-Time-Intro.mp4", allow_stretch=True, state='play')
        layout.add_widget(video)
        return layout

VideoApp().run()