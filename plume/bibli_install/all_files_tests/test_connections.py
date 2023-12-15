from qgis.core import QgsProject, QgsVectorLayer

from qgis.PyQt.QtWidgets import QAction, QMenu
from qgis.utils import iface

def connection() :
   # Spécifiez les paramètres de connexion PostgreSQL
   dbname = 'base_demo'
   host = 'localhost'
   port = '5432'
   user = 'postgres'
   password = 'postgres'
   schema = 'r_eurostat'
   table = 't2020_rn310'
   geometry_column = 'geom'

   # Construisez la chaîne de connexion PostgreSQL
   uri = f"dbname={dbname} host={host} port={port} user={user} password={password} key={geometry_column} table={schema}.{table} (geom) sql="

   # Créez une nouvelle couche vecteur à partir de la connexion PostgreSQL
   layer = QgsVectorLayer(uri, 'Ma couche', 'postgres')

   # Ajoutez la couche au projet
   QgsProject.instance().addMapLayer(layer)

def menu_asgard_menu_move() :
   # Création d'une action de menu personnalisée
   action = QAction("Mon Menu Personnalisé", iface.mainWindow())
   action.triggered.connect(lambda: print("Action personnalisée cliquée"))

   # Obtention du menu principal de QGIS
   main_menu = iface.mainWindow().menuBar()

   #-- Ajout du menu
   menuBar = self.iface.mainWindow().menuBar()    
   zMenu = menuBar
   for child in menuBar.children():
       #if child.objectName()== "mPluginMenu" :
       if child.title() == "&Aide":
          print(child.objectName())
          zMenu = child
          break
   zMenu.addMenu(self.menu)


   # Recherche de l'option "Aide" dans le menu principal
   found_help_menu = None
   for menu in main_menu.findChildren(QMenu):
       if found_help_menu is not None:
           # Ajout de l'action après avoir trouvé l'option "Aide"
           menu.addAction(action)
           break
       if menu.title() == "&Aide":
           found_help_menu = menu

   # Si l'option "Aide" n'est pas trouvée, ajoutez l'action à la fin du menu principal
   if found_help_menu is None:
       main_menu.addAction(action)

#connection()
menu_asgard_menu_move()
