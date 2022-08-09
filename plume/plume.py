# (c) Didier  LECLERC 2020 CMSIG MTE-MCTRCT/SG/SNUM/UNI/DRC Site de Rouen
# créé sept 2021

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *

from PyQt5.QtWidgets import (QAction, QMenu , QMenuBar, QApplication, QMessageBox, QFileDialog, QPlainTextEdit, QDialog, QStyle, 
                             QDockWidget, QTreeView, QGridLayout, QTabWidget, QWidget, QDesktopWidget, QSizePolicy, 
                             QTreeWidget, QTreeWidgetItem, QTreeWidgetItemIterator, QStyleFactory, QStyle)
from PyQt5.QtGui import QIcon

from qgis.core import *
from qgis.gui import *
import os
from plume.bibli_install import manageLibrary
from plume.config import (VALUEDEFAUTFILEHELP, VALUEDEFAUTFILEHELPPDF, VALUEDEFAUTFILEHELPHTML, URLCSWDEFAUT, URLCSWIDDEFAUT)  

#===================================================
# Generation de la traduction selon la langue choisie   
overrideLocale = QSettings().value("locale/overrideFlag", False)
localeFullName = QLocale.system().name() if not overrideLocale else QSettings().value("locale/userLocale", "")
if localeFullName == None :
  localePath = os.path.dirname(__file__) + "/i18n/plume_fr.qm"
else :
  localePath = os.path.dirname(__file__) + "/i18n/plume_" + localeFullName[0:2] + ".qm"
if QFileInfo(localePath).exists():
  translator = QTranslator()
  translator.load(localePath)
  QCoreApplication.installTranslator(translator)
# Generation de la traduction selon la langue choisie
#===================================================
# Gestion des bibliothèques, notamment installe RDFLib si n'est pas déjà disponible
manageLibrary()
# Gestion des bibliothèques, notamment installe RDFLib si n'est pas déjà disponible
#===================================================

from . import doplume_ui
from . import bibli_plume
from .bibli_plume import *

class MainPlugin(object):
  def __init__(self, iface):
     self.name = "PLUME"
     self.iface = iface
     #Active Tooltip
     self.dicTooltipExiste = {}   
     #Active Tooltip  
      
  def initGui(self):
     #Construction du menu
     self.menu=QMenu("plume")
     self.menu.setTitle(QtWidgets.QApplication.translate("plume_main", "PLUGIN METADATA") + "  (" + str(bibli_plume.returnVersion()) + ")")
     _pathIcons = os.path.dirname(__file__) + "/icons/logo"
     menuIcon          = _pathIcons + "/plume.svg"
     self.plume2 = QAction(QIcon(menuIcon),"PLUGIN METADATA (Metadata storage in PostGreSQL)" + "  (" + str(bibli_plume.returnVersion()) + ")",self.iface.mainWindow())
     self.plume2.setText(QtWidgets.QApplication.translate("plume_main", "PLUGIN METADATA (Metadata storage in PostGreSQL) "))
     self.plume2.triggered.connect(self.clickIHMplume2)
     #Construction du menu
     self.menu.addAction(self.plume2)
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
     #-
     #Management Click before open IHM 
     self.initializingDisplayPlume()
     #Management Click before open IHM 
     #-

  #==========================
  def initializingDisplayPlume(self):
      try : 
         iface.layerTreeView().clicked.connect(self.returnLayerBeforeClickedQgis)
                
         # Interaction avec le navigateur de QGIS
         self.mNav1, self.mNav2 = 'Browser', 'Browser2' 
         #1
         self.navigateur = iface.mainWindow().findChild(QDockWidget, self.mNav1)
         self.navigateurTreeView = self.navigateur.findChild(QTreeView)
         self.navigateurTreeView.setObjectName(self.mNav1)
         self.navigateurTreeView.clicked.connect(self.returnLayerBeforeClickedBrowser)
         #2
         self.navigateur2 = iface.mainWindow().findChild(QDockWidget, self.mNav2)
         self.navigateurTreeView2 = self.navigateur2.findChild(QTreeView)
         self.navigateurTreeView2.setObjectName(self.mNav2)
         self.navigateurTreeView2.clicked.connect(self.returnLayerBeforeClickedBrowser)
      except :
         pass   

      #tooltip
      mDic_LH = bibli_plume.returnAndSaveDialogParam(self, "Load")
      self.mDic_LH = mDic_LH
      #
      #==========================
      #Active Tooltip   
      self.activeTooltip      = True if mDic_LH["activeTooltip"]      == "true" else False
      self.activeTooltipWithtitle = True if mDic_LH["activeTooltipWithtitle"] == "true" else False
      self.activeTooltipLogo      = True if mDic_LH["activeTooltipLogo"]      == "true" else False
      self.activeTooltipCadre     = True if mDic_LH["activeTooltipCadre"]     == "true" else False
      self.activeTooltipColor     = True if mDic_LH["activeTooltipColor"]     == "true" else False
      self.activeTooltipColorText       = mDic_LH["activeTooltipColorText"] 
      self.activeTooltipColorBackground = mDic_LH["activeTooltipColorBackground"] 
      #
      _pathIcons = os.path.dirname(__file__) + "/icons/logo"
      iconSourceTooltip   = _pathIcons + "/plume.png"
      # liste des Paramétres UTILISATEURS
      listUserParam(self)
      # liste des Paramétres UTILISATEURS
      
      self._myExploBrowser  = MyExploBrowser(self.navigateur.findChildren(QTreeView)[0],  self.dicTooltipExiste, self.activeTooltip, self.activeTooltipColorText, self.activeTooltipColorBackground, self.langList, iconSourceTooltip,  self.activeTooltipLogo,  self.activeTooltipCadre,  self.activeTooltipColor, self.activeTooltipWithtitle)
      self._myExploBrowser2 = MyExploBrowser(self.navigateur2.findChildren(QTreeView)[0], self.dicTooltipExiste, self.activeTooltip, self.activeTooltipColorText, self.activeTooltipColorBackground, self.langList, iconSourceTooltip,  self.activeTooltipLogo,  self.activeTooltipCadre,  self.activeTooltipColor, self.activeTooltipWithtitle)

      return
              
  #==========================
  def returnLayerBeforeClickedQgis(self) :
      layerBeforeClicked = ("", "")
      try : 
         self.layer = iface.activeLayer()
         if self.layer:
            if self.layer.dataProvider().name() == 'postgres':
               layerBeforeClicked = (self.layer, "qgis")
         bibli_plume.saveinitializingDisplay("write", layerBeforeClicked)
      except :
         bibli_plume.saveinitializingDisplay("write", layerBeforeClicked)
      return

  #==========================
  def returnLayerBeforeClickedBrowser(self, index) :
      layerBeforeClicked = ("", "")
      self.index = index
      try : 
         mNav = self.iface.sender().objectName()
         self.proxy_model = self.navigateurTreeView.model() if mNav == self.mNav1 else self.navigateurTreeView2.model()

         self.modelDefaut = iface.browserModel() 
         self.model = iface.browserModel()
         item = self.model.dataItem(self.proxy_model.mapToSource(index))

         if isinstance(item, QgsLayerItem) :
            if item.providerKey() == 'postgres' :
               self.layer = QgsVectorLayer(item.uri(), item.name(), 'postgres')
               layerBeforeClicked = (self.layer, "postgres")
         bibli_plume.saveinitializingDisplay("write", layerBeforeClicked, index, mNav)
      except :
         bibli_plume.saveinitializingDisplay("write", layerBeforeClicked, index, mNav)
      return

  #==========================
  def clickAbout(self):
      d = doabout.Dialog()
      d.exec_()

  def clickIHMplume2(self):
      d = doplume_ui.Dialog(self.dicTooltipExiste)
      d.exec_()

  def unload(self):
      pass  




  
