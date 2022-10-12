from  kivymd.app import MDApp 
from kivy.lang import Builder
from kivymd.uix.button import MDFlatButton
import json
from kivymd.uix.expansionpanel import MDExpansionPanelOneLine, MDExpansionPanel
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager

class MainScreen(Screen):
    pass

class WitaiContent(MDBoxLayout):
    pass

class GttsContent(MDBoxLayout):
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
        witaicontent = WitaiContent()
        self.root.get_screen('main').ids.card.add_widget(
            MDExpansionPanel(
                on_open=self.panel_open,
                on_close=self.panel_close,
                content=witaicontent,
                panel_cls=MDExpansionPanelOneLine(text="Wit.ai"),
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

if __name__ == "__main__":
	Dashboard().run()


