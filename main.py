
#importation depuis kivy
from kivy.config import Config
Config.set("graphics", 'width', 350)
Config.set("graphics", 'height', 550)

from kivy.lang import Builder
from kivy.utils import get_color_from_hex
from kivy.properties import NumericProperty,StringProperty, ObjectProperty, ListProperty, BooleanProperty
from kivy.clock import Clock
from kivy.metrics import dp
#importation des module uix

from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.filemanager import MDFileManager

# importation des ecrans
from screens.connexion import*
from screens.selections import*

from kivymd.app import MDApp

from scripts.backend import Game,GameBase,Settigs,user_table, int_or_float, FileLoader
from random import choice

import sys, os,pathlib,time
import shutil 


__version__ = 1.0

base_path = pathlib.Path(__file__).parent

game = None 
settings = None


class MenuOptions(MDDropdownMenu):
    menue_selection = ObjectProperty()
    options = ListProperty()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
        self.items = [
                {
                    "viewclass":"OneLineListItem",
                    'id':str(p[0]),
                    'height': dp(50),
                    "text": p[1],
                    'on_release': lambda x=p[0],y=p[1]: self.menue_selection(x,y)
                }for p in enumerate(self.options)
            ]
        
        self.position = 'auto'
        self.width_mult=3
        
        
class SignInScreen(SignIn):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.us_login = ''
    
    def create_user(self):
        us_name = self.ids['us_name'].text
        prenom = self.ids["us_frist_name"].text
        us_levels = self.ids["us_levels"].text
        login = self.ids["login"].text
        us_password = self.ids["us_password"].text
        us_password_conf = self.ids["us_password_conf"].text
        if us_password_conf.strip() != us_password.strip():
            self.ids["us_password_conf"].hint_text = "mot de passe incorrecte "
            self.ids["us_password_conf"].helper_text = "Vous devez saisir le même mot de passe"
        
        else:
            # print(us_name, prenom, us_levels, login,us_password)
            user_table.add(user_name=us_name, user_frist_name=prenom,login=login,
                           pwd=us_password, niveau=us_levels, auto_connect=0)
            
            self.us_login = login
            
            self.create_user_settings()
            
            
    def create_user_settings(self):
        Settigs.create()
        GameBase.create()
        us_id = user_table.get(login = self.us_login)[0]
        Settigs.add(user_id = us_id.id, app_theme="Light",version=str(__version__))
    
        Domaine = FileLoader("assets/resources/domaines.json")
        for domaine in Domaine.get_itms():
            try:
                sections = FileLoader(f"assets/resources/{Domaine.get(domaine).get('file')}").get_itms()
            except IndexError:
                pass
            else:
                for section in sections:
                    GameBase.add(user_id = us_id.id, domaine=domaine, section=section,step=1,exo=1,points=0)
        
            
        Manager.current = 'login'
            


class LoginScreen(ConnexionScreen):
    background_image = StringProperty("assets/image/maths.png")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user = None
        self.log_in = True
        self.menu_in = False
        self.users = []
        self.menu_object = None
    
    def on_parent(self, widget, parent):
        if self.log_in:
            try:
                self.get_users() 
                if len(self.users) == 1 and self.users[0].auto_connect == 1:
                    self.unlock()
            except:
                pass
        
        self.log_in = not self.log_in
    
    def get_users(self):
        self.users = user_table.all()
        
        self.menu_object = MenuOptions(options =[us.login for us in self.users],
                                       menue_selection=self.menue_selection )
        
        
        self.ids['us_login'].text = self.users[0].login
    
    def menue_selection(self,index,text):
        self.user = self.users[index] 
        self.menu_object.dismiss()
        self.ids['us_login'].text = self.user.login
        if self.user.auto_connect == 1 or self.user.pwd == '':
            self.unlock()
    
    def menu_open(self,x):
        if not self.menu_in:
            self.menu_object.caller = x
            self.menu_object.open()
        
        self.menu_in = not self.menu_in
    
    def changer_user(self):
        user = self.ids['us_login'].text
        self.user = user_table.get(login=user)[0]
        
        
    def connect(self):
        self.changer_user()
        if self.ids['us_password'].text == self.user.pwd:
            self.unlock()
        else:
            # print("password error")
            pass
    
    def unlock(self):
        global settings
        global game
        global app 
        game = Game(base=GameBase)
        game.user = self.user.id
        settings = Settigs.get(user_id = self.user.id, id=self.user.id)[0]
        app.theme = settings.app_theme
        app.version = settings.version
        Manager.transition.direction = 'left'
        Manager.current = 'mainwidget'

class MainWidget(SelectionOne):
    background_image = StringProperty("assets/image/maths.png")
    source = "assets/resources/domaines.json"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.login = True
        self.File = FileLoader(self.source)
        self.data = self.File.get_itms()
        
    def on_parent(self, widget,parent):
        if self.login:
            self.load()
        
        self.login = not self.login
    
    def press(self,x):
        file = self.File.domain_file_path(x.title)
        game.file_name = file
        game.domaine = x.title
        Manager.transition.direction = 'left'
        Manager.current = 'sections'
    
    def back_screen(self, x):
        # print("back")
        pass
        

class Sections(SelectionTow):
    """
    selection de l'opération 
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.login = True
        self.File = None
        self.data = []
    
    def on_parent(self, widget,parent):
        if self.login:
            self.File = FileLoader(game.file_name)
            self.data = self.File.get_itms()
            self.load()
        
        self.login = not self.login
    
    def press(self,x):
        game.section = x.title
        Manager.transition.direction = 'left'
        Manager.current = 'levelscreen'
    
    def back_screen(self, x):
        Manager.transition.direction = 'right'
        Manager.current = 'mainwidget'
        
class LevelScreen(SelectionTow):
    """
    Ecran de selection du niveau des opération 
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.login = True
        self.File = None
        self.data = []
    
    def on_parent(self, widget,parent):
        if self.login:
            self.File = FileLoader(game.file_name).get(game.section)
            self.data = list(self.File.keys())[1:]
            g_dt = GameBase.get(user_id=game.user,domaine=game.domaine,section=game.section)[0]
            self.unlock_index = g_dt.step
            self.load()
        
        self.login = not self.login
    
    def press(self,x):
        # il faut bloquer l'accès pour les niveau verouillés
        if x.isLocked:
           return 0
       
        game.step = int(x.title.split()[-1])
        Manager.current = 'gamescreen'

    def back_screen(self, x):
        Manager.transition.direction = 'right'
        Manager.current = 'sections'

class GameScreen(MDScreen):
    niveau = NumericProperty(0)
    points = NumericProperty(0)
    exercice = NumericProperty(0)
    progression = NumericProperty(0)
    progression_ratio = NumericProperty(0)
    total_step = NumericProperty(0)
    total_exos = NumericProperty(0)
    
    Builder.load_file("assets/layouts/game.kv")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.solution = None
        self.bt_is_select = 0
        self.point = 0
        
        self.menu_object = MenuOptions(options=["Compte","Parametre","Déconnexion",'exit'],
                                      menue_selection=self.menue_selection )
        
    
    def on_parent(self, widget, parent):
       
        game.init()
        self.update()
        self.next_step()
        
    def update(self):
        self.total_step = game.total_step
        self.points = game.point
        self.exercice = game.exo
        self.niveau = game.step
        self.progression_ratio = game.step
        self.progression = game.exo
        self.total_exos = game.game_data['exos']
        self.ids['progression'].value=self.progression
    
    def next_step(self):
        try:
            exo = game.create()
            self.solution = int_or_float(eval(exo))
        except Exception as e:
            if isinstance(e,SyntaxError):
                self.next_step()
        else:
            self.ids['operation'].text = exo 
            rp = game.responses_generator(sl = self.solution)
            for i in range(len(rp)):
                ch = choice(rp)
                self.ids[f'bt{i+1}'].text = str(ch)
                self.ids[f'bt{i+1}'].md_bg_color = get_color_from_hex("#516d4c")
                rp.remove(ch)
            
            self.ids["check_go"].md_bg_color = get_color_from_hex("#6d7172")
            self.ids['check_go'].text = "vérifier"
            
    def selection_button(self, button):
        if get_color_from_hex("#2897ad")!= button.md_bg_color: # si boutton est selectionner 
            button.md_bg_color = get_color_from_hex("#2897ad")
            self.bt_is_select += 1
        else: # si boutton est deselectionner
            button.md_bg_color = get_color_from_hex("#516d4c")
            self.bt_is_select -= 1
        
        if self.bt_is_select == 0:
            self.ids["check_go"].md_bg_color = get_color_from_hex("#6d7172")
        else:
            self.ids["check_go"].md_bg_color = get_color_from_hex("#32b9f3")
    
    def check(self, button):
        sl_check = True
        if button.text == "vérifier":
            if self.bt_is_select != 0:
                for i in range(4):
                    bt = self.ids[f'bt{i+1}']
                    if get_color_from_hex("#2897ad") == bt.md_bg_color:
                        if bt.text == str(self.solution):
                            bt.md_bg_color = get_color_from_hex("#2eed48")
                        else:
                            bt.md_bg_color = get_color_from_hex("#e62806")
                            sl_check = False
                    else:
                        if bt.text == str(self.solution):
                            bt.md_bg_color = get_color_from_hex("#3355a5")
                            sl_check = False
           
                self.bt_is_select = 0
                button.text = "Suivant"
                button.md_bg_color =get_color_from_hex("#da930f")
                
                if sl_check:
                    game.point += game.game_data['point']
                else:
                    game.point -= game.game_data['point']

        else:
            self.next_step()
            button.text = "vérifier"
            button.md_bg_color = get_color_from_hex("#32b9f3")
            game.exo += 1
            self.step_over()
        
        self.update()
        game.save()

    def step_over(self):
        
        if game.step <= game.total_step:
            if game.exo == game.game_data['exos']:
                game.step += 1
                game.exo = 1
                game.save()
                game.init()
        
        else:
            try:
                section = game.sections[game.sections.index(game.section) +1 ]
            except Exception as e:
                '''on est à la dernier section'''
            else:
                game.section = section
                game.step = 1
                game.exo = 1
                game.point = 0
                game.save()
                game.init()
            
    
    def menue(self,x):
        self.menu_object.caller = x
        self.menu_object.open()
    
    def menue_selection(self, index,text):
        if index == 0:
            Manager.current = "account"
            Manager.transition.direction = 'left'
        elif index == 1:
            Manager.current = "setting"
            Manager.transition.direction = 'left'
        elif index == 2:
            Manager.current = "login"
            Manager.transition.direction = 'left'
        elif index == 3:
            sys.exit(0)
        self.menu_object.dismiss()
    
    def back_screen(self,x):
        Manager.transition.direction = 'right'
        Manager.current = 'levelscreen'


class Setting(MDScreen):
    Builder.load_file('assets/layouts/setting.kv')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def back_screen(self,x):
        Manager.transition.direction = 'right'
        Manager.current = 'gamescreen'
    
class Account(MDScreen):
    Builder.load_file("assets/layouts/account.kv")
    user_name = StringProperty()
    user_frist_name = StringProperty()
    us_login = StringProperty()
    us_password = StringProperty()
    us_level = StringProperty()
    us_auto_connect = BooleanProperty()
    us_profil_image = StringProperty("assets/profils/maths.png")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.login = True
        self.user = None
        self.focus_in = False
        self.temp = ''
        self.upd = True
        self.lastScreen = None
        
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager, select_path=self.select_path,
            ext=['.png','.jpg','.jpeg'],preview=True
            )
        
    
    def on_parent(self, widget,parent):
        if self.login: 
            self.user = user_table.get(id=game.user)[0]
            self.user_name = self.user.user_name
            self.user_frist_name = self.user.user_frist_name
            self.us_login = self.user.login
            self.us_level = self.user.niveau
            self.us_auto_connect = bool(self.user.auto_connect)
            self.us_password = self.user.pwd
            self.us_profil_image = self.user.profil_img if self.user.profil_img else self.us_profil_image
            
        self.login = not self.login
        
    def back_screen(self, x):
        Manager.current = "gamescreen"
        Manager.transition.direction = 'right'
    
    def save_all(self,x):
        self.get_password(self.ids['new_us_password'])
        self.user.user_name = self.user_name
        self.user.user_frist_name = self.user_frist_name
        self.user.login = self.us_login
        self.user.niveau = self.us_level
        self.user.auto_connect = int(self.us_auto_connect)
        self.user.pwd = self.us_password
        self.user.last_in = time.strftime("%Y-%m-%d %H:%M:%S") 
        self.user.profil_img = self.us_profil_image 
        self.user.save()
        
        
    def get_password(self, x):
        if self.ids['ls_us_password'].text != '' and self.ids['new_us_password'] != '':
            if self.us_password == self.ids['ls_us_password'].text.strip():
                self.us_password = x.text.strip()
        
            else:
                self.ids['error_massage'].text = "Mot de passe incorrect"
                self.ids['error_massage'].adaptive_height = True
        
    
    def create_new(self):
        if "signin" not in Manager.screen_names:
            scren = SignInScreen(name="signin")
            scren.back_screen_name=self.name
            scren.ScreenManager = Manager
            Manager.add_widget(scren)
        Manager.current = 'signin'
        Manager.transition.direction = 'down'
    
    def profil_change(self):
        self.file_manager.show(os.path.expanduser("~"))
    
    def select_path(self, path:str):
        ex = path.split('.')[-1]
        shutil.copy(path,os.path.join(base_path, f"assets/profils/{self.us_login.lower()}.{ex}"))
        self.us_profil_image = f"assets/profils/{self.us_login.lower()}.{ex}"
        
        self.exit_manager()

    def exit_manager(self):
        self.file_manager.close()
    

class MyApp(MDApp):
    Builder.load_file("assets/layouts/mainapp.kv")
    
    theme = StringProperty()
    version = StringProperty()
    
    def build(self):
        global Manager
        self.Manager = Manager
        
        self.Manager.add_widget(LoginScreen(name="login"))
        self.Manager.add_widget(Account(name="account"))
        self.Manager.add_widget(Setting(name="setting"))
        self.Manager.add_widget(MainWidget(name="mainwidget"))
        self.Manager.add_widget(Sections(name='sections'))
        self.Manager.add_widget(LevelScreen(name='levelscreen'))
        self.Manager.add_widget(GameScreen(name="gamescreen"))
        
        return self.Manager
    
    def on_start(self):
        global game
        global settings
 
        self.title = "MATHS"
        if settings != None:
            self.theme = settings.app_theme
            self.version = settings.version
        else:
            self.theme = "Light"
        
        self.theme_cls.theme_style = self.theme
        self.theme_cls.primary_palette="Teal"
        self.theme_cls.material_style="M2"

    def create_user(self):
        global Manager
        Manager.add_widget(SignInScreen(name="signin"))
        
    def on_theme(self,instance,value):
        if settings is not None:
            settings.app_theme = value
            self.theme_cls.theme_style = self.theme
            settings.save()


Manager = MDScreenManager()

if not os.path.exists(os.path.join(base_path,"databases/gamesql.db")):
    user_table.create()
    
    MyApp().create_user()
    
app = MyApp()
app.run()
