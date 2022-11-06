from  kivymd.app import MDApp 
from kivy.lang import Builder
from kivymd.uix.button import MDFlatButton
import json
from kivymd.uix.expansionpanel import MDExpansionPanelOneLine, MDExpansionPanel
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.uix.dialog import MDDialog
from kivymd.toast import toast
from kivymd.uix.list import OneLineAvatarIconListItem, IconLeftWidget, IconRightWidget
from kivymd.uix.dialog import MDDialog
import urllib.request
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
            'Authorization': 'Bearer NPKPNP3YPMP6WOWHSM6WGVITON5PNPJ6',
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

        self.update_service_list()
        self.service_type = None
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
    
    def check_box(self, service_type):
        self.service_type = service_type
        print(self.service_type)

    def clear(self, field):
        if field == 'service_name':
            self.root.get_screen('main').ids.service_name.text = ''
        elif field == "alias":
            self.root.get_screen('main').ids.alias.text = ''
        elif field == "site_url":
            self.root.get_screen('main').ids.site_url.text = ''
        elif field == "site_search_url":
            self.root.get_screen('main').ids.site_search_url.text = ''
        elif field == "application":
            self.root.get_screen('main').ids.application.text = ''
        
        self.dialog.dismiss()

    def update_service_list(self):
        with open('./assets/config.json','r') as f:
            self.app_config = json.load(f)
        f.close()
        
        for service in self.app_config['services']:
            item = OneLineAvatarIconListItem(text=service['name'])
            item.add_widget(IconLeftWidget(icon='pencil'))
            item.add_widget(IconRightWidget(icon='delete'))
            self.root.get_screen('main').ids.serivce_list.add_widget(item)
        
    def create_service(self):
        self.dialog = None
        service_name = self.root.get_screen('main').ids.service_name.text
        alias = self.root.get_screen('main').ids.alias.text
        site_url = self.root.get_screen('main').ids.site_url.text
        site_search_url = self.root.get_screen('main').ids.site_search_url.text
        application = self.root.get_screen('main').ids.application.text
        
        if not service_name or not alias:
            self.dialog = MDDialog(text="Enter all required fields",title="Error", buttons=[
                    MDFlatButton(text="OK",
                    on_release=lambda *args: self.clear(''),)
                    ])
            self.dialog.open()
            return

        invalid_characters = '~!@#$%^&*()_+{:"|}<>?`-=[];\,/.'

        for char in service_name:
            if char in invalid_characters:
                self.dialog = MDDialog(text="Invalid Service Name",title="Error", buttons=[
                    MDFlatButton(text="OK",
                    on_release=lambda *args: self.clear('service_name'),)
                    ])
                self.dialog.open()
                return
                
        for char in alias:
            if char in invalid_characters:
                if char ==",": continue
                self.dialog = MDDialog(text="Invalid Alias Name",title="Error", buttons=[
                        MDFlatButton(text="OK",
                        on_release=lambda *args: self.clear('alias'),)
                        ])
                self.dialog.open()
                return

        if site_url:
            try:
                status_code = urllib.request.urlopen(site_url).getcode()
            except: 
                status_code = 404

            if status_code != 200:
                self.dialog = MDDialog(text="Invalid Site url",title="Error", buttons=[
                            MDFlatButton(text="OK",
                            on_release=lambda *args: self.clear('site_url'),)
                            ])
                self.dialog.open()
                return

        if application:
            if not os.path.exists(application):
                self.dialog = MDDialog(text="Invalid Application path",title="Error", buttons=[
                            MDFlatButton(text="OK",
                            on_release=lambda *args: self.clear('application'),)
                            ])
                self.dialog.open()
                return
        
        if not site_url and not site_search_url and not application:
            self.dialog = MDDialog(text="Fill alteast one among the three.",title="Error", buttons=[
                            MDFlatButton(text="OK",
                            on_release=lambda *args: self.clear(''),)
                            ])
            self.dialog.open()
            return

        if "," in alias:
            alias = alias.split(",")
        else: 
            alias = [alias]

        if not site_url: site_url = 'none'
        if not site_search_url: site_search_url = 'none'
        if not application: application = 'none'

        with open("./assets/config.json","r") as f:
            user_config = json.load(f)
        f.close()
        
        new_service = {'name':service_name, 'type':self.service_type, 'alias':alias, 
                        'url':site_url,'search_url':site_search_url, 'app':application}
        print(new_service)
        user_config['services'].append(new_service)

        with open("./assets/config.json","w") as f:
            json.dump(user_config, f, indent=3)
        f.close()

        toast("Added {} to Services".format(service_name))
        
if __name__ == "__main__":
	Dashboard().run()