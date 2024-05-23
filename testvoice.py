import speech_recognition as sr
from gtts import gTTS
import pygame
import time
import pyttsx3

class SpeechAssistant:
    def __init__(self):
        # Initialize Pygame Mixer
        pygame.mixer.init()
        
        # Initialize the speech recognizer
        self.recognizer = sr.Recognizer()

    def recognize_speech(self):
        """Recognizes speech from microphone input and converts it to text."""
        with sr.Microphone() as source:
            print("Listening...")
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source)

            try:
                text = self.recognizer.recognize_google(audio)
                return text
            except sr.UnknownValueError:
                return "Sorry, I couldn't understand what you said."
            except sr.RequestError as e:
                return f"Sorry, I couldn't request results from Google Speech Recognition service; {e}"

    def text_to_speech(self, text, filename):
        """Converts text to speech and saves it as an audio file."""
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 0.9)
        engine.save_to_file(text, filename)
        engine.runAndWait()

    def play_audio(self, filename):
        """Plays an audio file."""
        print("Playing")
        sound = pygame.mixer.Sound(filename)
        sound.play()

    def run(self):
        """Main method to run the speech assistant."""
        while True:
            input("Press Enter to start speaking...")
            text = self.recognize_speech()
            print("You said:", text)
            self.text_to_speech(text, "output.wav")
            self.play_audio("output.wav")

if __name__ == "__main__":
    assistant = SpeechAssistant()
    assistant.run()
