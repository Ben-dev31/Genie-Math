
import random
import json
from scripts.model import Model
import os, pathlib

GameBase = Model(
    base_name='databases/gamesql.db',
    name='game_data',
    fields=[
        ('id','INTEGER PRIMARY KEY'),('user_id','INTEGER'),('domaine','VARCHAR(255)'),('section','VARCHAR(255)'),('step','INTEGER'),
            ('exo','INTEGER'),('points','INTEGER')
    ]
)
Settigs = Model(
    base_name='databases/gamesql.db',
    name='setting_data',
    fields=[
        ('id','INTEGER PRIMARY KEY'),("user_id", "INTEGER"),('app_theme','VARCHAR(255)'),
        ('version','VARCHAR(255)')
    ]
)
user_table = Model(
    base_name='databases/gamesql.db',
    name='user_tb',
    fields=[
        ('id','INTEGER PRIMARY KEY'),("user_name", "VARCHAR(255)"),("user_frist_name","VARCHAR(255)"),("login","VARCHAR(255)"),('pwd','VARCHAR(8)'),
        ('niveau','VARCHAR(255)'),("last_in", "VARCHAR(255)"),("auto_connect",'INTEGER'),('profil_img',"TEXT")
    ]
)


def int_or_float(s,n_round=2):
    if isinstance(s,int):
        return s 
    elif isinstance(s,float):
        return int(s) if s.is_integer() else round(s,n_round)
     

class DataStructure(dict):
    def __init__(self, data) -> None:
        if isinstance(data, dict):
            self.update(data)
        else:
            raise TypeError(f"DataStructure object accept only dict type not {type(data)}")
    

class Game:
    def __init__(self,base, file_name=None):
        self.base_data = None
        self.file_name = file_name
        self.step = 1             # int: niveau
        self.section = ''    # str: operation name (Addition, soustraction ..)
        self.exo = 1
        self.total_step = 0       # int: niveau total
        self.point = 0
        self.domaine = None
        self.operator = None
        self.game_data = None
        self.sections = None
        self.user = 1
        self.base = base
        
    
    def init(self):
        self.base_data = self.base.get(user_id = self.user, domaine = self.domaine, section=self.section)[0]
        self.step = self.base_data.step 
        self.exo = self.base_data.exo
        self.total_step = None
        self.point = self.base_data.points
        self.game_data = FileLoader(self.file_name) 
        
        self.sections = list(self.game_data.get_itms())
        
        self.game_data = self.game_data.get(self.section)   # a modiffier 
        
        self.total_step = len(self.game_data) -1 
        self.operator = self.game_data.get("operator")
        self.game_data = self.game_data.get(f"Niveau {self.step}")
        
    def __randn(self,a=0 ,b=1,lenght=2,use_int=True, n_round=2) ->list:
        ls = []
        if use_int:
            for i in range(lenght):
                ls.append(random.randint(int(a),int(b)))
        else:
            for i in range(lenght):
                n=random.random()
                va = int_or_float((b-a)*n + a, n_round)
                ls.append(va)
        return ls 
    
    def __generator(self):
        string = ''
        operand = self.__randn(b=self.game_data.get('lim'),
                               lenght= self.game_data.get('nb_operande'),
                               use_int=self.game_data.get('use_int'))
        opertor = self.operator
        
        if len(opertor) >1 and len(operand)!= len(opertor)+1:
            raise ValueError()
        
        i=0
        for p in operand:
            if operand.index(p)<len(operand)-1:
                string+=f"{p} {opertor[i]} "
            else:
                string+=f"{p} "
                
            if len(opertor)>1:
                i+=1
        return string
    
    def responses_generator(self, sl, lenght=4, n_round=2):
        
        solution = self.__randn(a=sl-5, 
                                b=sl+5,
                                lenght=3,
                                use_int=self.game_data.get('use_int'),
                                n_round=n_round)
        solution.append(sl)
        while solution.count(sl) >2:
            solution=None
            solution = self.__randn(a=sl-5, b=sl+5,lenght=3,n_round=n_round)
            solution.append(sl)
            
        return solution

    
    def create(self)->str:
        return self.__generator()

    def save(self)->None:
        self.base_data.user_id = self.user
        self.base_data.section = self.section
        self.base_data.exo = self.exo
        self.base_data.step = self.step
        self.base_data.points = self.point
        self.base_data.save()
    
    def save_on(self):
        self.base_data.save(points = self.point, exo=self.exo)


    
class FileLoader:
    def __init__(self, file_name) -> None:
        self.file_name = file_name
        self.data = None
        self.load_data()
    
    def load_data(self):
        file = open(self.file_name, 'r', encoding='utf8')
        try:
            self.data = json.load(file)
        except json.decoder.JSONDecodeError:
            self.data = {}

    
    def get_itms(self):
        return list(self.data.keys())

    def get(self, att):
        if att in self.get_itms():
            return DataStructure(self.data[att])
        else:
            raise ValueError(f"the file '{self.file_name}' dose not content key '{att}' avalable values is {tuple(self.get_itms())}")
        
    def domain_file_path(self, domain):
        file = self.get(domain).get('file')
        path = os.path.abspath(os.path.join(pathlib.Path(self.file_name).parent, file))
        return path
    
if __name__=="__main__":
    D = FileLoader("assets/resources/arithmetique.json")
    # print(D.get_itms())