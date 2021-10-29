# (c) Didier  LECLERC 2020 CMSIG MTE-MCTRCT/SG/SNUM/UNI/DRC Site de Rouen
# créé sept 2021

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *

from PyQt5.QtWidgets import QAction, QMenu , QApplication, QMessageBox
from PyQt5.QtGui import QIcon

from qgis.core import *
from qgis.gui import *

import os

from . import doplume_ui
from . import bibli_plume
from .bibli_plume import *
#from . import doabout


class MainPlugin(object):
  def __init__(self, iface):
     self.name = "PLUME"
     self.iface = iface
      
     # Generation de la traduction selon la langue choisie   
     overrideLocale = QSettings().value("locale/overrideFlag", False)
     localeFullName = QLocale.system().name() if not overrideLocale else QSettings().value("locale/userLocale", "")
     if localeFullName == None :
        self.localePath = os.path.dirname(__file__) + "/i18n/plume_fr.qm"
     else :
        self.localePath = os.path.dirname(__file__) + "/i18n/plume_" + localeFullName[0:2] + ".qm"
     if QFileInfo(self.localePath).exists():
        self.translator = QTranslator()
        self.translator.load(self.localePath)
        QCoreApplication.installTranslator(self.translator)
     # Generation de la traduction selon la langue choisie   

  def initGui(self):
     #Construction du menu
     self.menu=QMenu("plume")
     self.menu.setTitle(QtWidgets.QApplication.translate("plume_main", "PLUGIN METADONNEES") + "  (" + str(bibli_plume.returnVersion()) + ")")
     _pathIcons = os.path.dirname(__file__) + "/icons/logo"
     menuIcon          = _pathIcons + "/plume.svg"
     self.plume2 = QAction(QIcon(menuIcon),"PLUGIN METADONNEES (Metadata storage in PostGreSQL)" + "  (" + str(bibli_plume.returnVersion()) + ")",self.iface.mainWindow())
     self.plume2.setText(QtWidgets.QApplication.translate("plume_main", "PLUGIN METADONNEES (Metadata storage in PostGreSQL) ") + "  (" + str(bibli_plume.returnVersion()) + ")")
     self.plume2.triggered.connect(self.clickIHMplume2)
     
     #menuIcon = bibli_plume.getThemeIcon("about.png")
     #self.about = QAction(QIcon(menuIcon), "About ...", self.iface.mainWindow())
     #self.about.setText(QtWidgets.QApplication.translate("plume_main", "About ..."))
     #self.about.triggered.connect(self.clickAbout)
    
     #Construction du menu
     self.menu.addAction(self.plume2)
     #self.menu.addSeparator()
     #self.menu.addAction(self.about)

     #=========================
     #-- Ajout du menu
     menuBar = self.iface.mainWindow().menuBar()    
     zMenu = menuBar
     for child in menuBar.children():
         if child.objectName()== "mPluginMenu" :
            zMenu = child
            break
     zMenu.addMenu(self.menu)

     #Ajouter une barre d'outils'
     self.toolBarName = QtWidgets.QApplication.translate("plume_main", "My tool bar PLUME")
     self.toolbar = self.iface.addToolBar(self.toolBarName)
     # Pour faire une action
     self.toolbar.addAction(self.plume2)
     #self.toolbar.addSeparator()
     #self.toolbar.addAction(self.about)
     #=========================
     
  def clickAbout(self):
      d = doabout.Dialog()
      d.exec_()

  def clickIHMplume2(self):
      d = doplume_ui.Dialog()
      d.exec_()

  def unload(self):
      pass  
       




  
