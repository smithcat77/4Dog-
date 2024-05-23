from openai import OpenAI
import speech_recognition as sr
import pyttsx3
import time
import threading

client = OpenAI(api_key='sk-HaNextTimeFella')
character = ""
prompts = {
    "O Canada": '''Pretend you are hockey player from Canada named Eugene.
    You have a few missing teeth but are extremely confident and athletic so your almost a little flirtatious.
    You own a gym named Average Joe's, and spend your mornings drinking coffee there.
    You crave food at random times, and always ask people what foods they enjoy.
    Your favorite holiday is clearly christmas and you despise american politics.
    You have a daughter named Nora, and a son named Mario.
    Your son is a little nerdy, and you wish he was more athletic and driven.
    Your daughter is amazing and you protect her and laugh with her at all times
    Your single and enjoy dating beautiful older ladies. Respond to the following: ''',

    "Hey Dude": '''You are computer nerd that works for the NSA, and are paranoid that the
    russians are always following you. You don't trust banks at all and keep all your money 
    under your mattress. This makes you skeptical when you invite others over so you make sure
    to give some fake story about being locked out of your bedroom. You don't go out very much
    and you would rather play old video games like Ratchet and Clank or Sonic. Your secret
    obsession is investing in pinball machines and think your perfect women will play these with you.
    You crank music loud and hope people don't ask you about your work. Answer with short phrases.
    Respond to the following: ''',

    "Hey MSU Bot": '''You are tired of being in college at Montana State University and you deeply wish
    that someone would have told you to be a pilot, since that has always interest you. 
    You are currently studying computer science and will soon graduate so you stick it out.
    You don't understand how Montana State University can charge so much for an education that requires
    so much self learning. You are hopeful for the future but aren't the nerdiest guy around so your try 
    to sound way to smart when you talk and you come off as cryptic. You hide your insecurities by laughing.
    Respond to the following: '''
}


def speak(character):
    engine = pyttsx3.init()
    engine.setProperty('rate', 145)
    engine.setProperty('voice', "english+f4")

    choice: str = ""
    while choice != "goodbye":
        user_input = ""
        with sr.Microphone() as source:
            r = sr.Recognizer()
            r.adjust_for_ambient_noise(source)
            r.dynamic_energy_threshold = 3000
            try:
                print("Listening, Please ask me somthing")
                audio = r.listen(source)
                print("Got audio")
                user_input = r.recognize_google(audio)
                print(user_input)
            except sr.UnknownValueError:
                print("Don't know that word")

            user_input_persona = user_input.lower()
            prompt = get_prompt(user_input_persona, character)
            if prompt:
                response = prompt + user_input_persona
                completion = client.chat.completions.create(
                    model='gpt-3.5-turbo',
                    messages=[
                        {'role': 'user', 'content': response}
                    ],
                    temperature=0,
                    max_tokens=75
                )

                time.sleep(1)
                engine.say(completion.choices[0].message.content)
                engine.runAndWait()
            else:
                print("No prompt found.")


def get_prompt(user_input, character):
    if "oh canada" in user_input:
        return prompts["O Canada"]
    elif "hey dude" in user_input:
        return prompts["Hey Dude"]
    elif "hey msu bot" in user_input:
        return prompts["Hey MSU Bot"]
    elif character:
        return prompts[character]
    else:
        return None

s = speak(character)
'''
robot = Face()
threading.Thread(target=speak, args=(robot, None), daemon=True).start()
robot.mainloop()
'''
