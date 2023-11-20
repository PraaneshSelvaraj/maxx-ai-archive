import string
import subprocess
import threading
import webbrowser
from gtts import gTTS
import os
import socket
import pickle
from playsound import playsound
import random
import speech_recognition as sr
import get_wit
from time import sleep
from includes import config, keys, skills, file_share, toasts
from includes import google_con 
import json
import wolframalpha
import pyttsx3
import sys
from PySide2 import QtWidgets, QtGui
import requests
import winsound
import pickle

engine = pyttsx3.init()


with open("./assets/config.json","r") as f:
    user_config = json.load(f)
f.close()

quick_connect = False
if user_config['quick_connect']=="enabled":
    quick_connect = True
cache = {}
try:
    with open("./assets/cache.pkl", "rb") as f:
        cache = pickle.load(f)
    f.close()
except: print("Unable to load cache.")

encoding='ascii'
buffer = 1024

song_loaded = skills.load_songs()
toast_notifications = toasts.Toasts()

wolfram_app = wolframalpha.Client(keys.wolframalpha_app_id)
google_service_calendar = google_con.build_service("calendar")
google_service_people = google_con.build_service("people")

host ='0.0.0.0'                                                    
port = 1612
server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((host,port))  
server.listen()
print(f"Server started: @{port}")
devices = []
nicknames = []

def speak(txt):

    try:
        if config.redirect:
            if config.redirect_device:
                if config.redirect_device in nicknames:
                    if "LISTENER*"+config.redirect_device in nicknames:
                        device = "LISTENER*"+config.redirect_device
                    else:
                        device = config.redirect_device
                    resp = reqnresp("speak~{}".format(txt),device)
                    print("RESP SPEAK: {}".format(resp))
                    if resp:
                        return

        config.redirect = False
        config.redirect_device=None

        if user_config['defaults']['voice_engine'] == 'pyttsx3':
            engine.say(txt)
            engine.runAndWait()
            return

        elif user_config['defaults']['voice_engine'] == 'gTTS':
            tts=gTTS(txt,lang='en',tld=user_config['defaults']['voice'])
            tts.save('output.mp3')
            sleep(0.5)
            print(txt)
            playsound("output.mp3")
            os.remove("output.mp3")

        elif user_config['defaults']['voice_engine'] == 'wit.ai':
            audio= requests.post(
            'https://api.wit.ai/synthesize',
            params={
                'v': '20220622',
            },
            headers={
                'Authorization': 'Bearer {}'.format(keys.wit_access_token),
            },
            json={ 'q': txt, 'voice': user_config['defaults']['voice'] },
            )

            with open("output.wav","wb") as f:
                f.writelines(audio)
            f.close()
            
            print(txt)
            winsound.PlaySound("output.wav", winsound.SND_FILENAME)
            os.remove("output.wav")

    except Exception as e:
        print("speak exception: {}".format(e))


if song_loaded==False:
    speak("Something went wrong while loading songs.")
    
def get_audio():

    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.pause_threshold =  1.5
        r.adjust_for_ambient_noise(source, duration=0.5)
        r.energy_threshold = 2000
        r.dynamic_energy_threshold = True
        audio = r.listen(source,timeout=6,phrase_time_limit=6)
        said = ""
        print("processing audio..")

        try:
            said = r.recognize_google(audio)
            said = said.lower()
            config.is_Exception = False
            print(said)
        
        except Exception as e:
            print(e)

    return said

def recieve_msg_client(client,nickname):
    client.settimeout(8)
    while True:
        try:
            msg = client.recv(buffer).decode(encoding)

            if msg == "trigger":
                awake()

            elif msg =="!DISCONNECT":
                nicknames.remove(nickname)
                for i in devices:
                    if i['name'] == nickname:
                        devices.remove(i)
                        break
                print(nickname + " disconnected")
                speak(nickname+" is offline")
                exit()
            
            elif 'MSG' in msg:
                device,msg = msg.split("~")
                print(device+": "+msg)
                assistant(msg)

            elif "ARTWORK"in msg:
                path = msg.split("~")[-1]
                if path[0]=="/": path=path[1:]
                file_share.send(path)

        except Exception as e:
            if "timed out" in "{}".format(e):
                continue
            print("CLIENT EXCEPTION : {}".format(e))
            
def new_conn(client, nickname, address ,hsh):
    print(hsh)
    lst = string.ascii_letters+string.digits
    
    def hash(a=""):
        if len(a)<=64:
            a+=random.choice(lst)
            return hash(a)
        else: return a

    rf = open("./assets/data.pickle","rb")
    old_data = pickle.load(rf)
    rf.close()

    for i in old_data:
        if i['name'] == nickname:

            if i['hash']==hsh:

                print('matched')
                if nickname in nicknames:
                    print("Already in nicknames")
                else:
                    nicknames.append(nickname)
                    dev = {"name":nickname,"client":client}
                    devices.append(dev)

                client.send("CONNECTIONACCEPTED".encode(encoding))

                client.send(hsh.encode(encoding))
                speak(nickname+" is online.")
                
                
                rec_thrd = threading.Thread(target=recieve_msg_client,args=(client,nickname),daemon=True)
                rec_thrd.start()
                return

            elif i['ip']==address[0]:
                print('ip matched')
                nicknames.append(nickname)
                dev = {"name":nickname,"client":client}
                devices.append(dev)
                client.send("CONNECTIONACCEPTED".encode(encoding))

                hsh =hash()
                client.send(hsh.encode(encoding))
                speak(nickname+" is online.")
                
                
                rec_thrd = threading.Thread(target=recieve_msg_client,args=(client,nickname),daemon=True)
                rec_thrd.start()
                return

            else:
                client.send("!DISCONNECT".encode(encoding))
                print("NO MATCH")
                client.send(hsh.encode(encoding))

    speak("A device named "+nickname+" wants to connect. Do you want me to connect it.")

    if toast_notifications.new_connection(nickname):
        nicknames.append(nickname)
        dev = {"name":nickname,"client":client}
        devices.append(dev)
        client.send("CONNECTIONACCEPTED".encode(encoding))

        hsh = hash()
        print(hsh)
        client.send(hsh.encode(encoding))
        
        rec_thrd = threading.Thread(target=recieve_msg_client,args=(client,nickname),daemon=True)
        rec_thrd.start()

        data = {'name':nickname,'hash':hsh,'ip':address[0]}
        old_data.append(data)
        print(old_data)
        f= open("./assets/data.pickle","wb")
        pickle.dump(old_data,f)
        f.close()
        speak(nickname+" connected successfully.")
    else:
        client.send("!DISCONNECT".encode(encoding))
        speak("Okay")

def check_clients():
    rm_names = []
    for i in devices:
        msg = "!ALIVE"
        msg=msg.encode(encoding)
        i['client'].send(msg)
        resp = i['client'].recv(buffer)
        if resp:
            continue
        else: 
            rm_names.append(i['name'])
            devices.remove(i)

    return rm_names

def receive():                                                          
    while True:
        client, address = server.accept()
        client.settimeout(10)
        print("Connected with {}".format(str(address)))       
        client.send('NICKNAME'.encode(encoding))
        nickname = client.recv(buffer).decode(encoding)
        print(nickname)
        nickname, hash = nickname.split("~")
        if "LISTENER*" in nickname:
            if nickname.split("LISTENER*")[-1] in nicknames:
                nicknames.append(nickname)
                dev = {"name":nickname,"client":client}
                devices.append(dev)
                print(nickname+" is online")
                client.send("CONNECTIONACCEPTED".encode(encoding))
                client.send(hash.encode(encoding))
        else:
            new_conn(client,nickname,address, hash)

receive_thread = threading.Thread(target=receive,daemon=True)         
receive_thread.start()

def reqnresp(message, target):
    if message=="": return None
    msg = message.encode(encoding)
    
    for i in devices:
        if i['name'] == target:
            try:
                i['client'].send(msg)
                resp = i['client'].recv(buffer)
                if message=="!DISCONNECT":
                    try:
                        nicknames.remove(i['name'])
                        devices.remove(i)

                    except:
                        print("NO NICKNAME")
                        
                    print("DISCONNECTED")
                    print(nicknames)
                      
                else:
                    resp=resp.decode(encoding)
                    
                    if resp:
                        print("response",resp)
                    else:
                        nicknames.remove(i['name'])
                        devices.remove(i)
                        print("DISCONNECTED")
                        print(nicknames)

                    if resp=="!DISCONNECT":
                        nicknames.remove(i['name'])
                        devices.remove(i)
                        print("DISCONNECTED")
                        print(nicknames)
                        
                    return resp

            except:
                nicknames.remove(i['name'])
                devices.remove(i)
                print(nicknames)
        
        
    
    
    print(f"can't able to find {target}")
    
def assistant(query):
    playsound("./assets/sounds/process.mp3")
    if query in cache:
        print("cached")
        res = cache[query]
    else:
        res = get_wit.get_res(query)
        cache[query] = res
        with open("./assets/cache.pkl", "wb") as f:
            pickle.dump(cache, f)
        f.close()

    print("got resp")
    intent = get_wit.get_intent(res)
     
    if not intent:
        speak("I can't able to understand it")
        config.in_use = False

    elif intent=="get_time":
        time = skills.time()
        speak(f"It is {time}.")

    elif intent == "get_date":
        date = skills.date()
        speak(f"It is {date}.")

    elif(intent == "take_note"):
        speak(random.choice(["What would you like me to write down?","What should I write?"]))
        note_text = get_audio()
        skills.note(note_text)
        speak(random.choice(["I've made a note of that.","I've noted it.","Note taken"]))
    
    elif intent =="screenshot":
        skills.screenshot()
        speak("Screenshot Captured")
    
    elif intent == "check_battery":
        percent, plugged = skills.check_battery()
        if plugged:
            speak(f"{percent} percentage and charging")
        else:
            speak(f"{percent} percentage")
    
    elif intent == "play_track":
        track = get_wit.get_playlist(res)
        print(track)
        txt = "playing it"
        if not track or track == "random" or track=="any":
            track = "$random"
            txt = "Playing a random song"
        song = skills.get_track(track)

        if song:
            speak(txt)
            print(song)
            def play_song(song,user_config):
                subprocess.call([user_config['defaults']['media_player']['cmd'],song])
            x= threading.Thread(target=play_song,args=(song,user_config),daemon=True)
            x.start()
        else:
            speak("I can't able to find it")

    elif intent == "play_songs":
        name = get_wit.get_playlist(res)
        name = str(name).replace(" ","")
        print(name)
        
        playlist = skills.play_playlist(name)
        print(playlist)
        if playlist:
            speak("Playing it")
            def play_thrd(song,user_config):
                subprocess.call([user_config['defaults']['media_player']['cmd'],song])
            x=threading.Thread(target=play_thrd,args=(playlist,user_config),daemon=True)
            x.start()
        else: 
            speak("Unable to find it")

    elif intent == "wikipedia":
        speak("Searching on wikipedia")
        search = get_wit.get_search(res)
        if search:
            summary, link = skills.wiki(search)

            if summary:
                webbrowser.open(link)
                speak(summary)
                

            else: speak("I can't find that on wikipedia")
        else: speak("I can't able to find that")
        
    elif intent == "map_search":
        place = get_wit.get_map_places(res)
        print(place)
        if place:
            place = place.replace(" ","%20")
            link = user_config['defaults']['maps']['search_url']+place
            webbrowser.open(link)
            speak("here it is")
        else:
             speak("No place specified.")

    elif intent == "wolframalpha":
        speak("give me a second")
        try:
            resp = wolfram_app.query(query)
            txt =next(resp.results).text
            speak(txt)
        except:
            speak("I can't able to solve it.")

    elif intent == "website_search":
        device = get_wit.get_network_device(res)
        service = get_wit.get_service(res)
        search = get_wit.get_search(res)
        
        if not search:
            speak("Unable to search it")
            return
        if not service: 
            service = 'google'
            
        speak("Searching")
        link = skills.website_search(service,search)
        
        if link:

            if device:
                dev = "LISTENER*" + device
                if dev not in nicknames:
                    if device in nicknames: 
                        dev = device
                print("device = {}".format(dev))
                msg = "WEBBROWSER~{}".format(link)
                reqnresp(message=msg,target=dev)
                speak("Opening results in {}".format(device))
            else:
                speak("Opening results in browser")
                webbrowser.open(link)

        else:
            speak("I can't find it.")

    elif intent == "open_service":

        service = get_wit.get_service(res)
        if not service:
            speak("no service specified")
            return 
        service_type = get_wit.get_service_type(res)
        resp =  skills.open_service(service)
        print("resp: {}".format(resp))
        if not resp:
            speak("Unable to find it")
            return

        link,cmd, lcl_type = resp
        print("service type {}".format(service_type))
        print("lcl service type {}".format(lcl_type))
        print("app {}".format(cmd))
        if service_type == None:
            if lcl_type == "hybrid":
                service_type = user_config['service_default']
            else:
                service_type = lcl_type

        
        if service_type == "website":
            if not link:
                speak("unable to open it")
                return
            speak("Opening {}".format(service))
            webbrowser.open(link)

        elif service_type == "app":
            if not cmd:
                speak("Unable to open it")
                return

            speak("Opening {}".format(service))

            def open_serv(cmd):
                print("thread")
                subprocess.run([cmd])
            app=threading.Thread(target=open_serv,args=(cmd,),daemon=True)
            app.start()
    
    elif intent == "list_network_devices":

        resp=""
        if len(nicknames) >0:
            for n in nicknames:
                resp+=n+", "
            speak("These are the connected devices, ")
            speak(resp)
        else:
            speak("No device connected.")
    elif intent == "refresh_network_devices":

        if len(nicknames)>0:
            rm_devices = check_clients()
            if len(rm_devices) == 0 :
                speak("All devices are online.")
            elif len(rm_devices) ==1:
                speak(rm_devices[0]+" is offline.")
            elif len(rm_devices) >1:
                rm =""
                for i in rm_devices:
                    rm+=i+", "
                speak("These devices are disconnected {} .".format(rm))

            
        else:
            speak(random.choice(["No connections to refresh","No device connected."]))

    elif intent == "remove_network_device" :
        dev = get_wit.get_network_device(res)
        if dev:
            print(dev)
            if dev in nicknames:
                try:

                    if quick_connect==True:
                        print("quick connect")
                        rf = open("./assets/data.pickle","rb")
                        old_data = pickle.load(rf)
                        print(old_data)
                        rf.close()
                        for i in old_data:
                            if i['name'] == dev:
                                old_data.remove(i)
                        wf = open("./assets/data.pickle","wb")
                        pickle.dump(old_data,wf)
                        wf.close()
                        reqnresp("!DISCONNECT",dev)     
                        reqnresp("!DISCONNECT","LISTENER*"+dev)     
                        speak(dev+" is offline.")
           
                    else:
                        speak(dev+" is offline.")
                except:
                    if dev in nicknames:
                        speak("Unable to disconnect "+dev)
                    else:
                        speak(dev+" is offline.")
            else:
                speak("I can't able to find device named "+ dev)
        else:
            speak("No device specified.")

    elif intent=="redirect_output":
        device = get_wit.get_network_device(res)
        if device:
            speak("Redirecting audio output to {}".format(device))
            if "server" in device:
                config.redirect = False
                config.redirect_device = None
            else:
                if device in nicknames:
                    config.redirect = True
                    config.redirect_device = device
                    speak("Audio output redirected to {}".format(device))
                else:
                    speak("{} is offline.".format(device))

    elif intent=="schedule":
        min = get_wit.get_data_time(res)
        date,time = min.split("T")
        val = time.split(":")
        val[0]="23:"
        val[1] = "59:"
        time =""
        for i in val: 
            time+=i
        max = date+"T"+time
        events_result = google_service_calendar.events().list(calendarId='primary', timeMin=min,timeMax=max,
                                                maxResults=10, singleEvents=True,
                                                orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            speak(random.choice(['You are a free bird.',"You are free","You don't have any events"]))
        else:    
            i=1
            l = len(events)
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                d,t = start.split("T")
                hf ='A.M.'
                print(t)
                tmp =t.split(":")
                hour=int(tmp[0])
                min = int(tmp[1])
                if min ==0:
                    min="00"
                if hour>=12:
                    hour-=12
                    hf="P.M."
                if i==1:
                    speak(f"You have {event['summary']} at {hour}:{min} {hf}")
                elif i==len(events):
                    speak(f"and {event['summary']} at {hour}:{min} {hf}")
                else:
                    speak(f" {event['summary']} at {hour}:{min} {hf}")
                i+=1

    elif intent == "support":
        speak("Opening users support.")
        webbrowser.open("https://groups.google.com/g/maxx-ai-users-support")

    elif intent =="speak":
        speak_txt = get_wit.get_speak(res)
        if speak_txt: 
            speak(speak_txt)

def awake():
    if config.in_use:
        return
    config.in_use = True
    print(config.in_use)
    print("Listening...")
    playsound("./assets/sounds/awake.mp3")
    text = get_audio()
    if text:
        assistant(text)
        config.in_use = False
    else:
        config.in_use = False
        return
        
def start_dashboard():
    def dash_thread():
        subprocess.run(["./dashboard/dashboard.exe"])

    dash = threading.Thread(target=dash_thread,daemon=True)
    dash.start()

def restart_now():
    os.startfile(sys.argv[0])
    sys.exit()
    
#Creating System Tray Icon
class SystemTrayApp(QtWidgets.QSystemTrayIcon):
    def __init__(self,icon,parent):
        QtWidgets.QSystemTrayIcon.__init__(self,icon,parent)
        self.setToolTip("Maxx-AI")
        menu=QtWidgets.QMenu(parent)

        awake_opt = menu.addAction("Awake")
        awake_opt.triggered.connect(awake)
        awake_opt.setIcon(QtGui.QIcon("assets/images/icon.png"))
        menu.addSeparator()

        dashboard_opt = menu.addAction("Dashboard")
        dashboard_opt.triggered.connect(start_dashboard)
        menu.addSeparator()
        
        restart_opt = menu.addAction("Restart")
        restart_opt.triggered.connect(restart_now)
        menu.addSeparator()

        exit_opt = menu.addAction("Exit")
        exit_opt.triggered.connect(lambda: sys.exit())

        self.setContextMenu(menu)
        self.activated.connect(self.OnTrayIconActivated)


    def OnTrayIconActivated(self, reason):
        if reason==self.Trigger:
            awake()
  
if __name__ == "__main__":
    app=QtWidgets.QApplication(sys.argv)
    w=QtWidgets.QWidget()
    tray_icon=SystemTrayApp(QtGui.QIcon("assets/images/icon.png"),w)
    tray_icon.show()
    sys.exit(app.exec_())