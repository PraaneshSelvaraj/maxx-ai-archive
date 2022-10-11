import os
from subprocess import call
from time import sleep
import json
import requests
from includes import keys
import winsound
call(["pip","install","wit","playsound==1.2.2"])

from playsound import playsound

def speak(txt):
    audio= requests.post(
    'https://api.wit.ai/synthesize',
    params={
        'v': '20220622',
    },
    headers={
        'Authorization': 'Bearer {}'.format(keys.wit_access_token),
    },
    json={ 'q': txt, 'voice': 'Charlie' },
    )

    with open("output.wav","wb") as f:
        f.writelines(audio)
    f.close()
    
    print(txt)
    winsound.PlaySound("output.wav", winsound.SND_FILENAME)
    os.remove("output.wav")

speak("Hi, I am Maxx.")
speak("People say that I am an A.I, But I am your bestfriend.")
speak("I am going to move in and live with you.")
speak("Let me pack up my things from my home server and shift them to your system.")

packages =["tk","SpeechRecognition","wolframalpha","pyscreenshot","prompt_toolkit","pyaudio","wikipedia","psutil", "pyttsx3",
           "google-api-python-client","google-auth-httplib2","google-auth-oauthlib","pywin32","pillow","gTTS","pyside2"]

for package in packages:
    call(["pip","install",package])

speak("I've just moved in to your system.")
speak("Let's have a party")
speak("Oops, I can't find your songs, can you show me where you save your songs?")

from tkinter import Tk
from tkinter import filedialog

window=Tk()
window.title('Maxx-AI')

songs_path = filedialog.askdirectory()
if songs_path:
    window.destroy()

songs_path = songs_path.replace("/","\\")
songs_path+="\\"

with open("./assets/config.json","r") as f:
    user_config = json.load(f)
f.close()

user_config['songs_path'] = songs_path

with open("./assets/config.json","w") as f:
    json.dump(user_config, f, indent=3)
f.close()

speak("I need access to your google account to see your calendar events.")
speak("Don't worry, I am not going to steal your data.")

from includes import google_con
google_service_calendar = google_con.build_service("calendar")

speak("That's it, we are officially roommates.")
speak("If you wanna talk with me, I am always waiting for you in the taskbar.")