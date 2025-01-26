from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
import speech_recognition as sr
from threading import Thread


class VoiceAssistantApp(App):
    def build(self):
        self.layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Display for recognized text
        self.output_label = Label(text="Press the button to speak!", font_size=20, size_hint=(1, 0.8))
        self.layout.add_widget(self.output_label)

        # Button to trigger speech recognition
        self.speak_button = Button(text="Speak", size_hint=(1, 0.2), font_size=18)
        self.speak_button.bind(on_press=self.start_recognition)
        self.layout.add_widget(self.speak_button)

        return self.layout

    def recognize_speech(self):
        recognizer = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                self.update_label("Adjusting for ambient noise... Please wait.")
                recognizer.adjust_for_ambient_noise(source)
                self.update_label("Listening... Speak now!")
                audio = recognizer.listen(source, timeout=5)
                self.update_label("Recognizing...")
                text = recognizer.recognize_google(audio)
                self.update_label(f"You said: {text}")
        except sr.UnknownValueError:
            self.update_label("Sorry, I could not understand the audio.")
        except sr.RequestError as e:
            self.update_label(f"Could not request results; {e}")
        except Exception as e:
            self.update_label(f"An error occurred: {e}")

    def start_recognition(self, instance):
        # Run the recognition in a separate thread to avoid blocking the UI
        recognition_thread = Thread(target=self.recognize_speech)
        recognition_thread.start()

    def update_label(self, text):
        # Update the label text safely
        self.output_label.text = text


if __name__ == "__main__":
    VoiceAssistantApp().run()


