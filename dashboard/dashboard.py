from  kivymd.app import MDApp 
from kivy.lang import Builder
from kivymd.uix.button import MDFlatButton
import json
from kivymd.uix.expansionpanel import MDExpansionPanelOneLine, MDExpansionPanel
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.uix.dialog import MDDialog
from kivymd.toast import toast
import requests
import winsound
import os
from gtts import gTTS
from time import sleep
from playsound import playsound

class MainScreen(Screen):
    pass

class WitaiContent(MDBoxLayout):
    def voice_test(self,voice):
        print("Voice")
        audio= requests.post(
        'https://api.wit.ai/synthesize',
        params={
            'v': '20220622',
        },
        headers={
            'Authorization': 'Bearer YGLFI5TF35JA4KHYTBT75KTH3AEQOZLL',
        },
        json={ 'q': f"This is {voice} voice from wit a.i voice engine.", 'voice': voice },
        )

        with open("output.wav","wb") as f:
            f.writelines(audio)
        f.close()
        
        
        winsound.PlaySound("output.wav", winsound.SND_FILENAME)
        os.remove("output.wav")

class GttsContent(MDBoxLayout):
    def voice_test(self,voice,voice_name):
        tts=gTTS(f"This is {voice_name} voice from gtts voice engine",lang='en',tld=voice)
        tts.save('output.mp3')
        sleep(0.5)
        playsound("output.mp3")
        os.remove("output.mp3")

class Dashboard(MDApp):
    def build(self):
        self.theme_cls.theme_style="Light"
        app = Builder.load_file("app.kv")
        return app

    def on_start(self):
        self.user_config= None
        with open('./dashboard/dashboard_config.json','r') as f:
            self.user_config = json.load(f)
        f.close()
        theme = self.user_config['theme']
        if theme == "Dark":
            self.root.get_screen('main').ids.darkmode_switch.active=True
        else:
            self.root.get_screen('main').ids.darkmode_switch.active=False
            self.theme_cls.theme_style=theme
        witaicontent = WitaiContent()
        self.root.get_screen('main').ids.card.add_widget(
            MDExpansionPanel(
                on_open=self.panel_open,
                on_close=self.panel_close,
                content=witaicontent,
                panel_cls=MDExpansionPanelOneLine(text="Wit.ai"),
            ))
        
        gttscontent = GttsContent()
        self.root.get_screen('main').ids.card.add_widget(
            MDExpansionPanel(
                on_open=self.panel_open,
                on_close=self.panel_close,
                content=gttscontent,
                panel_cls=MDExpansionPanelOneLine(text="GTTS"),
            ))

    def change_theme(self):
        if self.root.get_screen('main').ids.darkmode_switch.active==True:
            self.theme_cls.theme_style="Dark"
            self.user_config['theme']="Dark"
        else:
            self.theme_cls.theme_style="Light"
            self.user_config['theme']="Light"

        with open("./dashboard/dashboard_config.json","w") as f:
            json.dump(self.user_config,f,indent=2)
        f.close()

    def switch_inside(self,screen):
        self.root.get_screen('main').ids.nav_drawer.set_state('close')
        self.root.get_screen('main').ids.inner_screen_manager.current=screen
    
    def panel_open(self, *args):
        Animation(
            height=(self.root.ids.box.height + self.root.ids.content.height)
            - self.theme_cls.standard_increment * 2,
            d=0.2,
        ).start(self.root.get_screen('main').ids.box)

    def panel_close(self, *args):
        Animation(
            height=(self.root.ids.box.height - self.root.ids.content.height)
            + self.theme_cls.standard_increment * 2,
            d=0.2,
        ).start(self.root.get_screen('main').ids.box)

    def change_voice(self,engine,voice,voice_name):
        
        toast("Changed {} from {} engine as default voice".format(voice_name,engine))
        with open("./assets/config.json","r") as f:
            user_config = json.load(f)
        f.close()
       
        user_config['defaults']['voice_engine'] = engine
        user_config['defaults']['voice'] = voice

        with open("./assets/config.json","w") as f:
            json.dump(user_config, f, indent=3)
        f.close()
        print("New voice : "+voice+" from "+engine)
        
        

if __name__ == "__main__":
	Dashboard().run()


