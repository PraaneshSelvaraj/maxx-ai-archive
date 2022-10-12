from time import sleep
import webbrowser
from  kivymd.app import MDApp 
from kivy.lang import Builder
from kivymd.uix.button import MDFlatButton
import json
import os
import pickle
import threading
import socket
import requests
from kivy.clock import Clock
from requests.auth import HTTPBasicAuth
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineIconListItem, IconRightWidget, OneLineListItem
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window
from kivymd.uix.card import MDCard
from kivymd.uix.templates import StencilWidget
from kivymd.uix.templates import ScaleWidget
from kivy.animation import Animation
from kivy.properties import NumericProperty, StringProperty

Window.keyboard_anim_args = {'d': .2, 't': 'in_out_expo'}
Window.softinput_mode = "below_target"
#Window.size = (1080/2, 2134/2)

class MainScreen(Screen):
    pass

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
    
if __name__ == "__main__":
	Dashboard().run()


