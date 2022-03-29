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

from . import doplume_ui
from . import bibli_plume
from .bibli_plume import *

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
     #self.initializingDisplay() ICI pour gérer les connections
     #-
     #=========================

     #==========================
  def initializingDisplay(self):
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
      return
              
  #==========================
  def returnLayerBeforeClickedQgis(self) :
      layerBeforeClicked = ""
      self.layer = iface.activeLayer()
      if self.layer:
         if self.layer.dataProvider().name() == 'postgres':
            layerBeforeClicked = self.layer
         
      self.saveinitializingDisplay("write", layerBeforeClicked)

  #==========================
  def returnLayerBeforeClickedBrowser(self, index) :
      layerBeforeClicked = ""
      mNav = self.iface.sender().objectName()
      self.proxy_model = self.navigateurTreeView.model() if mNav == self.mNav1 else self.navigateurTreeView2.model()
      # DL
      self.modelDefaut = iface.browserModel() 
      self.model = iface.browserModel()
      item = self.model.dataItem(self.proxy_model.mapToSource(index))
      #issu code JD Lomenede
      if isinstance(item, QgsLayerItem) :
         if item.providerKey() == 'postgres' :
            self.layer = QgsVectorLayer(item.uri(), item.name(), 'postgres')
            layerBeforeClicked = self.layer
      self.saveinitializingDisplay("write", layerBeforeClicked)

  #==========================
  def saveinitializingDisplay(self, mAction, layerBeforeClicked = None) :
      mSettings = QgsSettings()
      mDicAutre = {}
      mSettings.beginGroup("PLUME")
      mSettings.beginGroup("Generale")
      if mAction == "write" : 
         mDicAutre["layerBeforeClicked"]  = layerBeforeClicked
         for key, value in mDicAutre.items():
             mSettings.setValue(key, value)
      elif mAction == "read" : 
         mDicAutre["layerBeforeClicked"]  = ""
         for key, value in mDicAutre.items():
             if not mSettings.contains(key) :
                mSettings.setValue(key, value)
             else :
                mDicAutre[key] = mSettings.value(key)
                  
      mSettings.endGroup()
      mSettings.endGroup()
      print(mDicAutre)

      return
     
  #==========================
  def clickAbout(self):
      d = doabout.Dialog()
      d.exec_()

  def clickIHMplume2(self):
      d = doplume_ui.Dialog()
      d.exec_()

  def unload(self):
      pass  
       




  
