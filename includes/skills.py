import datetime
import os
import json
import random
import subprocess
import psutil
import wikipedia
import pyscreenshot
from threading import Thread
from win32com.shell import shell, shellcon

home = shell.SHGetFolderPath(0, shellcon.CSIDL_PROFILE, None,0)

with open ("./assets/config.json","r") as jf:
    user_config = json.load(jf)
jf.close()

file_index = []

def time():
   time =  str(datetime.datetime.now().strftime('%H:%M'))
   return time

def date():
    date = str(datetime.date.today())
    return date

def note(txt):
    time = str(datetime.datetime.now()).replace(":","-")
    file = home+"/Documents/"+time+"-note.txt"
    with open(file,"w") as f:
        f.writelines(txt)
    f.close()

    os.startfile(path)
    return True

def screenshot():
    time = str(datetime.datetime.now()).replace(":","-")
    path = f"{home}/Pictures/{time}.png"
    screenshot = pyscreenshot.grab()
    screenshot.save(path)
    os.startfile(path)

def check_battery():
    battery = psutil.sensors_battery()
    return int(battery.percent), battery.power_plugged

def load_songs():
    songs_path = user_config['songs_path']
    try:
        for root, _, files in os.walk(songs_path):
            if files:
                for i in files:
                    path = os.path.join(root,i)
                    file_index.append(path)
        
        return True
                    
    except:
        return False


def get_track(name):
    exts = ["mp3", "mp4", "mkv", "avi", "flv", "wmv", "mov", "wav", "ogg", "aac", "flac", "webm", "m4a", "ogg", "mpg", "mpeg"]
    
    files = []
    for file in file_index:
        i = file.split(".")[-1]
        if i in exts:
            files.append(file)

    if not name: return None
    
    elif name == "$random":

        return random.choice(files)
    else:
        for i in files:
            song = i.split("/")[-1]
            name = name.strip()
            song = song.strip()
            if name.lower() in song.lower():
                return i


def play_playlist(name):
    if not name: return None
    
    for i in file_index:
        if ".xspf" in i: 
            song = i.split("/")[-1]
            name = name.replace(" ","")
            song = song.replace(" ","")
            if name.lower() in song.lower() and ".xspf" in song.lower():
                return i
        else : continue
    return None


def wiki(search):
    try:
        summary = wikipedia.summary(search,sentences=2)
        url = wikipedia.page(search).url
        return summary, url

    except:
        return None, None

def website_search(service, search):
    service = service.replace(" ","")
    search = search.replace(" ","+")

    for s in user_config['services']:
        for name in s['alias']:
            if name == service:
                if s['search_url']:
                    return s['search_url']+search
                else:
                    return None

    return None

def open_service(service):
    service = service.replace(" ","")
    for s in user_config['services']:
        for name in s['alias']:
            if name == service:
                try: url=s['url']
                except: url=None
                try: app= s['app'] 
                except: app=None
                return url, app, s['type']


    return None
