from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.clock import Clock
import speech_recognition as sr
from threading import Thread
import time


class VoiceAssistantApp(App):
    def build(self):
        self.layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Display for wake word status
        self.output_label = Label(text="Listening for 'Ciphera'...", font_size=20, size_hint=(1, 0.8))
        self.layout.add_widget(self.output_label)

        # Button to manually trigger speech recognition (for testing)
        self.speak_button = Button(text="Manually Start", size_hint=(1, 0.2), font_size=18)
        self.speak_button.bind(on_press=self.trigger_speech_recognition)
        self.layout.add_widget(self.speak_button)

        # Start wake word detection in a separate thread
        self.wake_word_thread = Thread(target=self.listen_for_wake_word, daemon=True)
        self.wake_word_thread.start()

        return self.layout

    def update_label(self, text):
        """Updates the main label safely from a thread."""
        Clock.schedule_once(lambda dt: setattr(self.output_label, "text", text))

    def listen_for_wake_word(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            while True:
                try:
                    self.update_label("Listening for 'Ciphera'...")
                    audio = recognizer.listen(source, phrase_time_limit=3)  # Shorter listen time
                    text = recognizer.recognize_google(audio).lower()

                    # Check if the wake word is detected
                    if any(wake_word in text for wake_word in ["ciphera", "cipher", "cyphera", "cypher", "hello"]):
                        Clock.schedule_once(lambda dt: self.trigger_speech_recognition())

                except sr.UnknownValueError:
                    continue
                except sr.RequestError:
                    self.update_label("Speech recognition service error.")

    def trigger_speech_recognition(self, instance=None):
        """Opens the speech recognition popup and starts listening."""
        self.popup_label = Label(text="Listening...", font_size=18)
        self.popup = Popup(title="Live Transcription",
                           content=self.popup_label,
                           size_hint=(0.8, 0.4))
        self.popup.open()

        # Start continuous speech recognition in a thread
        self.speech_thread = Thread(target=self.recognize_continuous_speech, daemon=True)
        self.speech_thread.start()

    def update_popup_text(self, text):
        """Updates the popup label safely from a thread."""
        Clock.schedule_once(lambda dt: setattr(self.popup_label, "text", text))

    def recognize_continuous_speech(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            self.update_popup_text("Listening...")

            transcript = ""
            last_audio_time = time.time()

            while True:
                try:
                    audio = recognizer.listen(source, phrase_time_limit=3)
                    text = recognizer.recognize_google(audio)

                    if text:
                        transcript += text + " "
                        self.update_popup_text(transcript)
                        last_audio_time = time.time()

                except sr.UnknownValueError:
                    pass  # Ignore unknown audio
                except sr.RequestError:
                    self.update_popup_text("Speech recognition error.")
                    break

                # Stop listening after 7 seconds of silence
                if time.time() - last_audio_time > 7:
                    break

        Clock.schedule_once(lambda dt: self.popup.dismiss())  # Close popup after silence


if __name__ == "__main__":
    VoiceAssistantApp().run()
