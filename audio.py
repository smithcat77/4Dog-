import openai
from openai import OpenAI
import sounddevice as sd
from pydub import AudioSegment
from io import BytesIO
import time

class SpeechInteractiveBot:
    def __init__(self, character):
        self.character = character
        self.client = OpenAI(api_key='sk-HaNextTimeFella')
        self.locations = {
            "Location A": "Pretend you're heading to your first destination and happy. Respond to the following: ",
            "Location B": "You're now embarking on a journey to location b and sad... Respond to the following: ",
        }

    def record_audio(self, duration=5, samplerate=16000):
        print("Listening, please ask me something...")
        audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
        print(audio)
        sd.wait()
        return audio

    def recognize_speech(self, audio, samplerate=16000):
        audio_segment = AudioSegment(
            data=audio.tobytes(),
            sample_width=audio.dtype.itemsize,
            frame_rate=samplerate,
            channels=1
        )
        audio_buffer = BytesIO()
        audio_segment.export(audio_buffer, format="mp3")
        audio_buffer.seek(0)
        
        try:
            transcription = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_buffer
            )
            return transcription['text']
        except Exception as e:
            print(f"Error during transcription: {e}")
            return None

    def get_destination(self, user_input):
        for key in self.locations:
            if key.lower() in user_input.lower():
                return self.locations[key]
        return None

    def respond(self, user_input):
        destination = self.get_destination(user_input)
        if destination:
            response = destination + user_input
            completion = self.client.chat.completions.create(
                model='gpt-3.5-turbo',
                messages=[{'role': 'user', 'content': response}],
                temperature=0,
                max_tokens=75
            )
            reply = completion['choices'][0]['message']['content']
            print(reply)
            self.speak(reply)
        else:
            print("No location related prompt found.")

    def speak(self, text):
        response = self.client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
        audio_path = 'response.mp3'
        with open(audio_path, 'wb') as f:
            f.write(response.content)
        print(f"Response saved to {audio_path}. Play it using any media player.")

if __name__ == "__main__":
    bot = SpeechInteractiveBot(character="")
    while True:
        audio_data = bot.record_audio()
        user_input = bot.recognize_speech(audio_data)
        if user_input:
            print(f"Recognized: {user_input}")
            bot.respond(user_input.lower())
        time.sleep(1)  # Prevent immediate re-listening
