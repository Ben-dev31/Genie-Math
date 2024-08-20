
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty,ListProperty
from kivy.lang import Builder
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDIcon, MDLabel

from kivymd.uix.behaviors import HoverBehavior

from kivymd.app import MDApp

import os, pathlib

Builder.load_file(os.path.join(pathlib.Path(__file__).parent,"screen_style/selections.kv"))


class SelectionBox(MDBoxLayout, HoverBehavior):
    text = StringProperty("")
    title = StringProperty("Calculs")
    image = StringProperty('assets/image/maths.png')
    press_function = ObjectProperty()
    isLocked = BooleanProperty(False)
    box_size = ListProperty([200,300])
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.size_hint_max_x = 50
    
    def on_parent(self, widget, parent):
        if self.isLocked:
            wdg = self.ids['contener']
            wdg.clear_widgets()
            wdg.md_bg_color = "#e79b0d"
            wdg.add_widget(
                MDIcon(
                    icon='lock',
                    pos_hint= {'center_x': 0.5,'center_y': 0.5},
                    font_size=20,
                    
                    color='red'
                )
            )
            
            wdg.add_widget(
                MDLabel(
                    text= self.title,
                    pos_hint= {'center_x': 0.5,'center_y': 0.3},
                    font_size=14,
                    color='red',
                    halign = 'center',
                )
            )
        
    

class SelectionOne(MDScreen):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = []
        
    def load(self):
        parent = self.ids['widget_one']
        parent.clear_widgets()
        for name in self.data:
            parent.add_widget(
                SelectionBox(
                    title= name,
                    press_function = lambda x: self.press(x)
                )
            )
    
    def press(self, x):
        pass
        


class SelectionTow(MDScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = []
        self.unlock_index = 0
        self.box_size = [200,300]
        
    def load(self):
        parent = self.ids['widget_two']
        parent.clear_widgets()
        
        lock = False
        for name in self.data:
            try:
                if int(name.split()[-1])<= self.unlock_index:
                    lock = False
                    self.box_size = [200,300]
                else:
                    lock = True
                    self.box_size = [60,100]
            except:
                pass 
            
            parent.add_widget(
                SelectionBox(
                    box_size=self.box_size,
                    title=name,
                    press_function = lambda x: self.press(x),
                    isLocked = lock
                )
            )
            
            
    def press(self, x):
        if x.isLocked:
            pass
            # print('locked')


if __name__ == "__main__":
    
    class App(MDApp):
        def build(self):
            screen = MDScreen()
            screen.add_widget(SelectionBox(isLocked=True))
            
            return screen 
    
    
    App().run()