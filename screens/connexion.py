from kivy.lang import Builder
from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty, ObjectProperty
import os, pathlib

Builder.load_file(os.path.join(pathlib.Path(__file__).parent,"screen_style/connexion.kv"))

class ConnexionScreen(MDScreen):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class SignIn(MDScreen):
    back_screen_name = StringProperty()
    ScreenManager = ObjectProperty()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    
    def back_screen(self,x):
        self.ScreenManager.current = self.back_screen_name
        self.ScreenManager.transition.direction = 'up'
        
