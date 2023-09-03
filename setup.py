import os
from subprocess import call
from time import sleep
import json
import requests
from includes import keys
import winsound
import shutil
import win32com.client
from threading import Thread

call(["pip","install","wit==6.0.1","playsound==1.2.2"])

from playsound import playsound

def run():
    call(["pythonw","maxx.pyw"], shell=True)

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

packages =["tk==0.1.0","SpeechRecognition==3.8.1","wolframalpha==5.0.0","pyscreenshot==3.0","prompt_toolkit==3.0.28","pyaudio==0.2.12","wikipedia==1.4.0","psutil==5.9.2", "pyttsx3==2.90",
           "google-api-python-client==2.64.0","google-auth-httplib2==0.1.0","google-auth-oauthlib==0.4.6","pywin32==304","pillow==9.2.0","gTTS==2.2.4","pyside2==5.15.2.1","kivy==2.1.0","kivymd==1.0.2"]

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

startup_folder = os.path.join(os.getenv("APPDATA"), "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
shortcut_path = os.path.join(startup_folder, "Maxx-AI.lnk")
shell = win32com.client.Dispatch("WScript.Shell")
shortcut = shell.CreateShortCut(shortcut_path)
shortcut.Targetpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "maxx.pyw")
shortcut.WorkingDirectory = os.path.dirname(os.path.abspath(__file__))
shortcut.save()

call(['setx', 'maxxaipath', os.getcwd()])

Thread(target=run, daemon=True).start()
speak("That's it, we are officially roommates.")
speak("If you wanna talk with me, I am always waiting for you in the taskbar.")