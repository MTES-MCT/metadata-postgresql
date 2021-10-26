# (c) Didier  LECLERC 2020 CMSIG MTE-MCTRCT/SG/SNUM/UNI/DRC Site de Rouen
# créé sept 2021
#        **************************************************************************
#        copyright            : (C) 2021 by DL
#        **************************************************************************

from PyQt5 import QtCore, QtGui, QtWidgets, QtQuick 

from PyQt5.QtCore import *
from PyQt5.QtWidgets import (QAction, QMenu , QMenuBar, QApplication, QMessageBox, QFileDialog, QPlainTextEdit, QDialog, QStyle, 
                             QDockWidget, QTreeView, QGridLayout, QTabWidget, QWidget, QDesktopWidget, QSizePolicy, 
                             QTreeWidget, QTreeWidgetItem, QTreeWidgetItemIterator)

from PyQt5.QtGui import QIcon, QStandardItem, QStandardItemModel

from .bibli_pg  import template_utils                                                                                                                                    
from . import bibli_plume
from .bibli_plume import *
#
from . import bibli_gene_objets
from .bibli_gene_objets import *
#
from . import docolorbloc

from qgis.core import *
from qgis.gui import *
from qgis.PyQt.QtCore import QUrl

import qgis  
import os
import subprocess
import time
import sys

from .bibli_rdf import rdf_utils
from .bibli_pg  import pg_queries
from .bibli_pg  import template_utils

class Ui_Dialog_plume(object):
    def __init__(self):
        self.iface = qgis.utils.iface                         
        self.firstOpen = True                                 
        self.firstOpenConnect = True
    
    def setupUi(self, Dialog):
        self.Dialog = Dialog
        Dialog.setObjectName("Dialog")
        #--
        mDic_LH = bibli_plume.returnAndSaveDialogParam(self, "Load")
        self.mDic_LH = mDic_LH
        self.lScreenDialog, self.hScreenDialog = int(self.mDic_LH["dialogLargeur"]), int(self.mDic_LH["dialogHauteur"])
        self.displayMessage  = False if self.mDic_LH["displayMessage"] == 'dialogTitle' else True #Qmessage box (dialogBox) ou barre de progression (dialogTitle)
        self.fileHelp        = self.mDic_LH["fileHelp"]      #Type Fichier Help
        self.fileHelpPdf     = self.mDic_LH["fileHelpPdf"]   #Fichier Help  PDF
        self.fileHelpHtml    = self.mDic_LH["fileHelpHtml"]  #Fichier Help  HTML
        self.durationBarInfo = int(self.mDic_LH["durationBarInfo"])  #durée d'affichage des messages d'information
        self.ihm             = self.mDic_LH["ihm"]  #window/dock
        self.toolBarDialog   = self.mDic_LH["toolBarDialog"]    #toolBarDialog
        self.extExport       = self.mDic_LH["extExport"]    #extExport
        print(self.extExport)
        #---
        self.colorDefaut                      = self.mDic_LH["defaut"]                      #Color QGroupBox
        self.colorQGroupBox                   = self.mDic_LH["QGroupBox"]                   #Color QGroupBox
        self.colorQGroupBoxGroupOfProperties  = self.mDic_LH["QGroupBoxGroupOfProperties"]  #Color QGroupBox
        self.colorQGroupBoxGroupOfValues      = self.mDic_LH["QGroupBoxGroupOfValues"]      #Color QGroupBox
        self.colorQGroupBoxTranslationGroup   = self.mDic_LH["QGroupBoxTranslationGroup"]   #Color QGroupBox
        self.colorQTabWidget                  = self.mDic_LH["QTabWidget"]                  #Color QTabWidget
        self.labelBackGround                  = self.mDic_LH["QLabelBackGround"]            #Fond Qlabel
        #---
        self.editStyle        = self.mDic_LH["QEdit"]              #style saisie
        self.epaiQGroupBox    = self.mDic_LH["QGroupBoxEpaisseur"] #épaisseur QGroupBox
        self.lineQGroupBox    = self.mDic_LH["QGroupBoxLine"]      #trait QGroupBox
        self.policeQGroupBox  = self.mDic_LH["QGroupBoxPolice"]    #Police QGroupBox
        self.policeQTabWidget = self.mDic_LH["QTabWidgetPolice"]   #Police QTabWidget
        #---
        # liste des Paramétres UTILISATEURS
        self.preferedTemplate        = self.mDic_LH["preferedTemplate"]                                       if "preferedTemplate"        in self.mDic_LH   else None
        self.enforcePreferedTemplate = (True if self.mDic_LH["enforcePreferedTemplate"] == "true" else False) if "enforcePreferedTemplate" in self.mDic_LH   else None
        self.readHideBlank           = (True if self.mDic_LH["readHideBlank"]           == "true" else False) if "readHideBlank"           in self.mDic_LH   else None
        self.readHideUnlisted        = (True if self.mDic_LH["readHideUnlisted"]        == "true" else False) if "readHideUnlisted"        in self.mDic_LH   else None
        self.editHideUnlisted        = (True if self.mDic_LH["editHideUnlisted"]        == "true" else False) if "editHideUnlisted"        in self.mDic_LH   else None
        self.language                = self.mDic_LH["language"]                                               if "language"                in self.mDic_LH   else "fr"
        self.initTranslation         = self.mDic_LH["translation"]                                            if "translation"             in self.mDic_LH   else "false" 
        self.langList                = self.mDic_LH["langList"]                                               if "langList"                in self.mDic_LH   else ['fr', 'en']
        self.geoideJSON              = (True if self.mDic_LH["geoideJSON"]              == "true" else False) if "geoideJSON"              in self.mDic_LH   else True
        self.readOnlyCurrentLanguage = (True if self.mDic_LH["readOnlyCurrentLanguage"] == "true" else False) if "readOnlyCurrentLanguage" in self.mDic_LH   else None
        self.editOnlyCurrentLanguage = (True if self.mDic_LH["editOnlyCurrentLanguage"] == "true" else False) if "editOnlyCurrentLanguage" in self.mDic_LH   else None
        self.labelLengthLimit        = self.mDic_LH["labelLengthLimit"]                                       if "labelLengthLimit"        in self.mDic_LH   else None
        self.valueLengthLimit        = self.mDic_LH["valueLengthLimit"]                                       if "valueLengthLimit"        in self.mDic_LH   else None
        self.textEditRowSpan         = self.mDic_LH["textEditRowSpan"]                                        if "textEditRowSpan"         in self.mDic_LH   else None
        # liste des Paramétres UTILISATEURS
        #---
        _pathIcons = os.path.dirname(__file__) + "/icons/general"
        _iconSourcesRead         = _pathIcons + "/read.svg"
        _iconSourcesEmpty        = _pathIcons + "/empty.svg"
        _iconSourcesExport       = _pathIcons + "/export.svg"
        _iconSourcesImport       = _pathIcons + "/import.svg"
        _iconSourcesSave         = _pathIcons + "/Save.svg"
        _iconSourcesTemplate     = _pathIcons + "/template.svg"
        _iconSourcesTranslation  = _pathIcons + "/translation.svg"
        _iconSourcesHelp         = _pathIcons + "/info.svg"
        _iconSourcesParam        = _pathIcons + "/configuration.svg"
        self.listIconToolBar = [ _iconSourcesRead, _iconSourcesEmpty, _iconSourcesExport, _iconSourcesImport, _iconSourcesSave, _iconSourcesTemplate, _iconSourcesTranslation, _iconSourcesHelp, _iconSourcesParam ]
        #--------
        Dialog.resize(QtCore.QSize(QtCore.QRect(0,0, self.lScreenDialog, self.hScreenDialog).size()).expandedTo(Dialog.minimumSizeHint()))
        Dialog.setWindowTitle("PLUME (Metadata storage in PostGreSQL)")
        Dialog.setWindowModality(Qt.WindowModal)
        Dialog.setWindowFlags(Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint) 
        _pathIcons = os.path.dirname(__file__) + "/icons/logo"
        iconSource          = _pathIcons + "/plume.svg"
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(iconSource), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)

        #Affiche info si MAJ version
        self.barInfo = QgsMessageBar(self)
        self.barInfo.setSizePolicy( QSizePolicy.Minimum, QSizePolicy.Fixed )
        self.barInfo.setGeometry(280, 0, Dialog.width()-280, 25)
        #==========================              
        #Zone Onglets
        self.tabWidget = QTabWidget(Dialog)
        self.tabWidget.setObjectName("tabWidget")
        x, y = 10, 25
        larg, haut =  self.lScreenDialog -20, (self.hScreenDialog - 40 )
        self.tabWidget.setGeometry(QtCore.QRect(x, y, larg , haut))
        self.tabWidget.setStyleSheet("QTabWidget::pane {border: 2px solid " + self.colorQTabWidget  + "; font-family:" + self.policeQGroupBox  +"; } \
                                    QTabBar::tab {border: 1px solid " + self.colorQTabWidget  + "; border-bottom-color: none; font-family:" + self.policeQGroupBox  +";\
                                                    border-top-left-radius: 6px;border-top-right-radius: 6px;\
                                                    width: 160px; padding: 2px;} \
                                      QTabBar::tab:selected {background: qlineargradient(x1: 0, y1: 0, x2: 0.5, y2: 0.5, stop: 0 " + self.colorQTabWidget  + ", stop: 1 white);  font: bold;} \
                                     ")
        tab_widget_Onglet = QWidget()
        tab_widget_Onglet.setObjectName("Informations")
        labelTabOnglet = "Informations"
        self.tabWidget.addTab(tab_widget_Onglet, labelTabOnglet)

        QtCore.QMetaObject.connectSlotsByName(Dialog)
        #========================== 
        #==========================
        #First Open 
        if self.firstOpen :
           self.afficheNoConnections("first")
           self.listeResizeIhm = [] # For resizeIhm

        #First Open 
        #==========================
        #=====================================================  
        # Window Versus Dock
        if self.ihm in ["dockTrue", "dockFalse"] :
           monDock = MONDOCK(self.Dialog)
        # Window Versus Dock
        #----
        self.mode = "read"  #Intiialise les autres instances  
        #----
        #=====================================================  
        #--- Icons Actions ---- Edit, Empty, Export, Import, Save, Template, Traslation -----
        self.createToolBar(*self.listIconToolBar)
        #------------
        
        if self.ihm in ["dockTrue", "dockFalse"] : self.mMenuBarDialog.show()
        #==========================
        self.retranslateUi(Dialog)

        #==========================
        #Interactions avec les différents canaux de communication
        self.gestionInteractionConnections()

        #==========================
        #Instanciation des "shape, template, vocabulary, mode" 
        self.vocabulary  = bibli_plume.returnObjetVocabulary()
        self.shape       = bibli_plume.returnObjetShape()
        self.translation = bibli_plume.returnObjetTranslation(self)
        #-
        self.displayToolBar(*self.listIconToolBar)    
    #= Fin setupUi

    #==========================
    # == Gestion des actions de boutons de la barre de menu
    def clickButtonsActions(self):
        if not hasattr(self, 'mConnectEnCours') :
           self.afficheNoConnections("show")
           return

        mItem = self.mMenuBarDialog.sender().objectName()
        #**********************
        if mItem == "Edition" :
           if self.mode == None or self.mode == "read" : 
              self.mode = "edit"
           elif self.mode == "edit" : 
              self.mode = "read"
           else  : 
              self.mode = "read"
           #-   
           if self.saveMetaGraph :
              self.oldMetagraph  = self.metagraph
           else :   
              self.metagraph     = self.oldMetagraph
           self.saveMetaGraph = False
        #**********************
        elif mItem == "Save" :                                            
           bibli_plume.saveMetaIhm(self, self.schema, self.table) 
           self.saveMetaGraph = True
        #**********************
        elif mItem == "Empty" :
           if self.saveMetaGraph :
              self.oldMetagraph  = self.metagraph
           else :   
              self.metagraph     = self.oldMetagraph
           self.saveMetaGraph = False
           #-   
           self.metagraph  = bibli_plume.returnObjetMetagraph(self, "")
        #**********************
        elif mItem == "Export" :
           pass
        #**********************
        elif mItem == "Import" :
           if self.saveMetaGraph :
              self.oldMetagraph  = self.metagraph
           else :   
              self.metagraph     = self.oldMetagraph
           self.saveMetaGraph = False
           #-   
           metagraph  = bibli_plume.importObjetMetagraph(self)
           if metagraph != None : self.metagraph = metagraph
        #**********************
        elif mItem == "Traduction" :
           self.translation = (False if self.translation else True) 
        #**********************
        #*** commun
        if mItem in ["Edition", "Save", "Empty", "Import", "Traduction"] :
           bibli_plume.saveObjetTranslation(self.translation)
           self.generationALaVolee(bibli_plume.returnObjetsMeta(self, self.schema, self.table))

        #-
        self.displayToolBar(*self.listIconToolBar)
        return
    # == Gestion des actions de boutons de la barre de menu
    #==========================

    #==========================
    # == Gestion des actions du bouton EXPORT de la barre de menu
    def clickButtonsExportActions(self):
        mItemExport = self.mMenuBarDialog.sender().objectName()
        exportObjetMetagraph(self, self.schema, self.table, mItemExport)
        return
    # == Gestion des actions du bouton EXPORT de la barre de menu
    #==========================

    #==========================
    # == Gestion des actions du bouton TEMPLATE de la barre de menu
    def clickButtonsTemplateActions(self):
        mItemTemplates = self.mMenuBarDialog.sender().objectName()

        #Lecture existence Extension METADATA
        _mContinue = True
        if not hasattr(self, 'mConnectEnCours') :
           if not self.instalMetadata : _mContinue = False

        if _mContinue : 
           if mItemTemplates == "Aucun" :
              self.template, self.templateTabs = None, None
           else :   
              # Choix du modèle
              bibli_plume.generationTemplateAndTabs(self, mItemTemplates)
           # Génération à la volée
           self.generationALaVolee(bibli_plume.returnObjetsMeta(self, self.schema, self.table))

           # MAJ ICON FLAGS
           self.majQmenuModeleIconFlag(mItemTemplates)
           # MAJ ICON FLAGS
           
        return
    # == Gestion des actions du bouton TEMPLATE de la barre de menu
    #==========================

    #==========================
    #Génération à la volée 
    #Dict des objets instanciés
    def generationALaVolee(self, _dict):
        # Nettoyage
        for comptElemTab in range(self.tabWidget.count()) :
            self.tabWidget.removeTab(0)
        #== For Create premier onglet Générale 
        tab_widget_Onglet = QWidget()
        tab_widget_Onglet.setObjectName("Informations")
        labelTabOnglet = "Informations"
        self.tabWidget.addTab(tab_widget_Onglet, labelTabOnglet)
        #== For Create premier onglet Générale 
        # Nettoyage 

        #--
        self.mDicObjetsInstancies = _dict
        self.mFirstColor = True
        #--
        for key, value in _dict.items() :
            if _dict[key]['main widget type'] != None :
               #Génération à la volée des objets 
               bibli_gene_objets.generationObjets(self, key, value)
        self.mFirstColor = False
        #--

        # Nettoyage
        for comptElemTab in range(self.tabWidget.count()) :
            if self.tabWidget.tabText(comptElemTab) == "Informations" :
               self.tabWidget.removeTab(comptElemTab)
               
        # For Réaffichage du dimensionnement
        bibli_plume.resizeIhm(self, self.Dialog.width(), self.Dialog.height())
        #--------------------------
        self.tabWidget.setCurrentIndex(0)
    #--
    #Génération à la volée 
    #==========================

    #---------------------------
    #---------------------------
    # == Gestion des INTERACTIONS
    def gestionInteractionConnections(self):
        _mCommentPlume = "Attention !! des métadonnées sont gérées pour cette couche !"
        self.db      = None
        self.schema  = None
        self.table   = None
        self.comment = None
        #Interaction avec le gestionnaire de couche de QGIS
        #iface.layerTreeView().currentLayerChanged.connect(self.retrieveInfoLayerQgis)
        iface.layerTreeView().clicked.connect(self.retrieveInfoLayerQgis)
                
        # Interaction avec le navigateur de QGIS
        self.mNav1, self.mNav2 = 'Browser', 'Browser2' 
        #1
        self.navigateur = iface.mainWindow().findChild(QDockWidget, self.mNav1)
        self.navigateurTreeView = self.navigateur.findChild(QTreeView)
        self.navigateurTreeView.setObjectName(self.mNav1)
        self.navigateurTreeView.clicked.connect(self.retrieveInfoLayerBrowser)
        #2
        self.navigateur2 = iface.mainWindow().findChild(QDockWidget, self.mNav2)
        self.navigateurTreeView2 = self.navigateur2.findChild(QTreeView)
        self.navigateurTreeView2.setObjectName(self.mNav2)
        self.navigateurTreeView2.clicked.connect(self.retrieveInfoLayerBrowser)
        return

    #---------------------------
    def retrieveInfoLayerQgis(self) :
        self.layer = iface.activeLayer()
        if self.layer:
           if self.layer.dataProvider().name() == 'postgres':
              self.getAllFromUri()
              #--                                                                          
              if self.connectBaseOKorKO[0] :
                 self.afficheNoConnections("hide")
                 #-
                 self.comment    = bibli_plume.returnObjetComment(self, self.schema, self.table)
                 self.metagraph  = bibli_plume.returnObjetMetagraph(self, self.comment)
                 self.oldMetagraph  = self.metagraph
                 self.saveMetaGraph = False
                 self.columns    = bibli_plume.returnObjetColumns(self, self.schema, self.table)
                 self.mode = "read"
                 #-
                 self.displayToolBar(*self.listIconToolBar)
                 #-
                 if self.instalMetadata :
                    #-
                    tpl_labelDefaut                     = bibli_plume.returnObjetTpl_label(self)
                    if tpl_labelDefaut :
                       self.template, self.templateTabs = bibli_plume.generationTemplateAndTabs(self, tpl_labelDefaut)
                    else :
                       self.template, self.templateTabs = None, None   
                    #-
                    self.createQmenuModele(self._mObjetQMenu, self.templateLabels)
                    self.majQmenuModeleIconFlag(tpl_labelDefaut)
                 else :
                    self.template, self.templateTabs = None, None   
                 #-
                 self.generationALaVolee(bibli_plume.returnObjetsMeta(self, self.schema, self.table))
        return

    #---------------------------
    def retrieveInfoLayerBrowser(self, index):
        mNav = self.sender().objectName()
        # DL
        #issu code JD Lomenede
        # copyright            : (C) 2020 by JD Lomenede for # self.proxy_model = self.navigateurTreeView.model() = self.model = iface.browserModel() = item = self.model.dataItem(self.proxy_model.mapToSource(index)) #
        self.proxy_model = self.navigateurTreeView.model() if mNav == self.mNav1 else self.navigateurTreeView2.model()
        # DL
        self.modelDefaut = iface.browserModel() 
        self.model = iface.browserModel()
        item = self.model.dataItem(self.proxy_model.mapToSource(index))
        #issu code JD Lomenede
        if isinstance(item, QgsLayerItem):
            self.layer = QgsVectorLayer(item.uri(), item.name(), 'postgres')
            self.getAllFromUri()
            #--
            if self.connectBaseOKorKO[0] :
               self.afficheNoConnections("hide")
               #-
               self.comment = bibli_plume.returnObjetComment(self, self.schema, self.table)
               self.metagraph  = bibli_plume.returnObjetMetagraph(self, self.comment)
               self.oldMetagraph  = self.metagraph
               self.saveMetaGraph = False
               self.columns = bibli_plume.returnObjetColumns(self, self.schema, self.table)
               self.mode = "read"
               #-
               self.displayToolBar(*self.listIconToolBar)
               #-
               if self.instalMetadata :
                  #-
                  tpl_labelDefaut                     = bibli_plume.returnObjetTpl_label(self)
                  if tpl_labelDefaut :
                     self.template, self.templateTabs = bibli_plume.generationTemplateAndTabs(self, tpl_labelDefaut)
                  else :
                     self.template, self.templateTabs = None, None   
                  #-
                  self.createQmenuModele(self._mObjetQMenu, self.templateLabels)
                  self.majQmenuModeleIconFlag(tpl_labelDefaut)
               else :
                  self.template, self.templateTabs = None, None   
               #-
               self.generationALaVolee(bibli_plume.returnObjetsMeta(self, self.schema, self.table))
        return

    #---------------------------
    def getAllFromUri(self):
        uri = QgsDataSourceUri(self.layer.source())
        self.schema, self.table = uri.schema(), uri.table()
        #print( [ self.schema, self.table ] )
        #self.relationType = db_table._relationType #type de relation v=vue, m= vue matérialisée, r = relation (table)
        #-
        self.uri, self.mConfigConnection, self.username, self.password = uri, uri.connectionInfo(), uri.username() or "", uri.password() or ""
        self.connectBaseOKorKO = self.connectBase()
        #-
        if self.connectBaseOKorKO[0] :
           pass
        else :    
           zTitre = QtWidgets.QApplication.translate("plume_ui", "PLUME : Warning", None)
           zMess  = QtWidgets.QApplication.translate("plume_ui", "Authentication problem", None)
           bibli_plume.displayMess(self.Dialog, (2 if self.Dialog.displayMessage else 1), zTitre, zMess, Qgis.Warning, self.Dialog.durationBarInfo)
        return

    #----------------------
    def connectBase(self) :
        return self.mTestConnect(self.mConfigConnection, self.uri)
          
    #----------------------
    def mTestConnect(self, mConfigConnection, uri) :
        retUser, retPassword, mTestConnect, okConnect = self.username, self.password, True, False
        mMessAuth = QtWidgets.QApplication.translate("plume_ui", "Authentication problem, check your password in particular.", None)
        connInfoUri = uri.connectionInfo()

        while mTestConnect :
           try :
              mConnectEnCours = psycopg2.connect(uri.connectionInfo(), application_name="PLUME")
              mTestConnect, okConnect = False, True
           except :
              (retSuccess, retUser, retPassword) = QgsCredentials.instance().get(connInfoUri, retUser, retPassword, mMessAuth)
              if not retSuccess : #Annuler 
                 mTestConnect, okConnect = False, False
              else :
                 uri.setUsername(retUser)     if retUser else ''
                 uri.setPassword(retPassword) if retPassword else ''
        #--------
        if okConnect :
           QgsCredentials.instance().put(connInfoUri, retUser, retPassword) 
           self.mConnectEnCours = mConnectEnCours
           return True, self.mConnectEnCours, mConfigConnection
        else : 
           return False, None, ""    

    # == Gestion des INTERACTIONS
    #---------------------------
    #---------------------------

    #==========================
    def closeEvent(self, event):
        print("DOCK DIALOG " + str(event))

        try :
           if hasattr(self, 'mConnectEnCours') :
              self.mConnectEnCours.close()
        except:
           pass

        try :
           self.navigateurTreeView.clicked.disconnect(self.retrieveInfoLayerBrowser)
        except:
           pass

        try :
           self.navigateurTreeView2.clicked.disconnect(self.retrieveInfoLayerBrowser)
        except:
           pass

        try :
           iface.layerTreeView().clicked.disconnect(self.retrieveInfoLayerQgis)
        except:
           pass

    #==========================
    def resizeEvent(self, event):
        if self.firstOpen :
           self.firstOpen = False
        #else :
        bibli_plume.resizeIhm(self, self.Dialog.width(), self.Dialog.height())

    #==========================
    def clickParamDisplayMessage(self):
        mDicAutre = {}
        mSettings = QgsSettings()
        mSettings.beginGroup("PLUME")
        mSettings.beginGroup("Generale")
        mDicAutre["displayMessage"] = "dialogBox"
        for key, value in mDicAutre.items():
            if not mSettings.contains(key) :
               mSettings.setValue(key, value)
            else :
               mDicAutre[key] = 'dialogBox' if self.paramDisplayMessage.isChecked() else 'dialogTitle'
        #--                 
        for key, value in mDicAutre.items():
            mSettings.setValue(key, value)
        mSettings.endGroup()
        mSettings.endGroup()
        #--
        self.displayMessage = self.paramDisplayMessage.isChecked()  #Qmessage box (dialogBox) ou barre de progression (dialogTitle)
        return
        
    #==========================
    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtWidgets.QApplication.translate("plume_ui", "PLUGIN METADONNEES (Metadata storage in PostGreSQL)", None) + "  (" + str(bibli_plume.returnVersion()) + ")")

    #==========================
    def clickColorDialog(self):
        d = docolorbloc.Dialog()
        d.exec_()
        return
        
    #==========================
    def afficheNoConnections(self, action = ""):
        if action == "first" :
           myPath = os.path.dirname(__file__)+"\\icons\\logo\\plume.svg"
           #----------    
           self.labelImage = QtWidgets.QLabel(self.tabWidget)
           myDefPath = myPath.replace("\\","/")
           carIcon = QtGui.QImage(myDefPath)
           self.labelImage.setPixmap(QtGui.QPixmap.fromImage(carIcon))
           self.labelImage.setGeometry(QtCore.QRect(30, 20, 100, 100))
           self.labelImage.setObjectName("labelImage")
           #----------
           _zMess  = "<html>Sélectionnez une couche PostgreSQL\
                         <ul style='margin: 0;'><li>dans le panneau des couches ou</li><li>dans l'explorateur</li></ul>\
                         \npour consulter ses métadonnées.</html>"
           zMess  = QtWidgets.QApplication.translate("plume_ui", _zMess, None)
           self.zoneWarningClickSource = QtWidgets.QLabel(self.tabWidget )
           self.zoneWarningClickSource.setGeometry(30, 110, 300, 100)
           self.zoneWarningClickSource.setStyleSheet("QLabel {   \
                                font-family:" + self.policeQGroupBox  +" ; \
                                }")
           self.zoneWarningClickSource.setText(zMess)
        else :
           self.labelImage.setVisible(True if action == "show" else False)
           self.zoneWarningClickSource.setVisible(True if action == "show" else False)
        return

    #==========================
    # == Gestion des actions de boutons de la barre de menu
    def displayToolBar(self, _iconSourcesRead, _iconSourcesEmpty, _iconSourcesExport, _iconSourcesImport, _iconSourcesSave, _iconSourcesTemplate, _iconSourcesTranslation, _iconSourcesHelp, _iconSourcesParam) :
        #-- Désactivation
        self.plumeEdit.setEnabled(False)
        self.plumeSave.setEnabled(False)
        self.plumeEmpty.setEnabled(False)
        self.plumeExport.setEnabled(False)
        self.plumeImport.setEnabled(False)
        self.plumeTemplate.setEnabled(False)
        self.plumeTranslation.setEnabled(False)

        #====================
        #====================
        #--QToolButton TEMPLATE                                               
        if hasattr(self, 'mConnectEnCours') :
           if self.toolBarDialog == "picture" : self.plumeTemplate.setStyleSheet("QToolButton { border: 0px solid black;}")  
           self.plumeTemplate.setIcon(QIcon(_iconSourcesTemplate))
           self.plumeTemplate.setObjectName("Template")
           #Lecture existence Extension METADATA
           mKeySql = (pg_queries.query_exists_extension(), ('metadata',))
           r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self.mConnectEnCours, mKeySql, optionRetour = "fetchone")
           self.instalMetadata = False
           if r :
              self.instalMetadata = True
              self.plumeTemplate.setEnabled(True)
              #MenuQToolButton                        
              # Génération des items via def createQmenuModele(self, _mObjetQMenu, templateLabels)
              mTextToolTip = QtWidgets.QApplication.translate("plume_main", "Choisir un modèle de formulaire.") 
              self.plumeTemplate.setEnabled(True)
           else :
              self.plumeTemplate.setEnabled(False)
              mTextToolTip = QtWidgets.QApplication.translate("plume_main", "Extension METADATA non installée.") 
           self.plumeTemplate.setToolTip(mTextToolTip)
        #--QToolButton TEMPLATE                                               
        #====================
        #====================

        if hasattr(self, 'mConnectEnCours') :
           #--QToolButton EXPORT                                               
           self.majQmenuExportIconFlag()
           #-
           mKeySql = (pg_queries.query_is_relation_owner(), (self.schema, self.table))
           r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self.mConnectEnCours, mKeySql, optionRetour = "fetchone")
           #-- Activation ou pas 
           self.plumeEdit.setEnabled(r)
           self.plumeSave.setEnabled(r)
           self.plumeEmpty.setEnabled(r)
           self.plumeExport.setEnabled(r)
           self.plumeImport.setEnabled(r)
           self.plumeTemplate.setEnabled(r)
           self.plumeTemplate.setEnabled(r)
           self.plumeTranslation.setEnabled(True if self.mode == "edit" else False)
           #Mode edition avec les droits
           if r == True and self.mode == 'read' : 
              self.plumeSave.setEnabled(False)
              self.plumeEmpty.setEnabled(False)
              self.plumeImport.setEnabled(False)                  
              #self.plumeTemplate.setEnabled(False)
              self.plumeTranslation.setEnabled(False)
        #-
        self.plumeEdit.setToolTip(self.mTextToolTipEdit if self.mode == 'read' else self.mTextToolTipRead)   
        if self.toolBarDialog == "picture" :
           _mColorFirstPlan, _mColorSecondPlan = "transparent", "#cac5b1"     #Brun            
           self.plumeEdit.setStyleSheet("QPushButton { border: 0px solid black; background-color: "  + _mColorFirstPlan  + ";}" "QPushButton::pressed { border: 0px solid black; background-color: " + _mColorSecondPlan + ";}"  if self.mode == 'read' else \
                                        "QPushButton { border: 0px solid black;; background-color: " + _mColorSecondPlan + ";}" "QPushButton::pressed { border: 0px solid black; background-color: " + _mColorFirstPlan  + ";}")   
           self.plumeTranslation.setStyleSheet("QPushButton { border: 0px solid black; background-color: "  + _mColorFirstPlan  + ";}" "QPushButton::pressed { border: 0px solid black; background-color: " + _mColorSecondPlan + ";}"  if not self.translation else \
                                        "QPushButton { border: 0px solid black;; background-color: " + _mColorSecondPlan + ";}" "QPushButton::pressed { border: 0px solid black; background-color: " + _mColorFirstPlan  + ";}")   
        #-
        self.plumeTranslation.setToolTip(self.mTextToolTipOui if self.translation else self.mTextToolTipNon)   
        
        return

    #==========================
    # == Gestion des actions de boutons de la barre de menu
    def createQmenuModele(self, _mObjetQMenu, templateLabels) :
        _mObjetQMenu.clear()
        templateLabels.insert(0, "Aucun")
        _mObjetQMenu.setStyleSheet("QMenu { font-family:" + self.policeQGroupBox  +"; width: " + str((int(len(max(templateLabels))) * 10) + 50) + "px;}")
        #------------
        for elemQMenuItem in templateLabels :
            _mObjetQMenuItem = QAction(elemQMenuItem, _mObjetQMenu)
            _mObjetQMenuItem.setText(elemQMenuItem)
            _mObjetQMenuItem.setObjectName(str(elemQMenuItem))
            _mObjetQMenu.addAction(_mObjetQMenuItem)   
            #- Actions
            _mObjetQMenuItem.triggered.connect(lambda : self.clickButtonsTemplateActions())
        #-
        self.plumeTemplate.setPopupMode(self.plumeTemplate.MenuButtonPopup)
        self.plumeTemplate.setMenu(_mObjetQMenu)
        return

    #==========================
    # == Gestion des Icons Flags dans le menu des templates
    def majQmenuModeleIconFlag(self, mItemTemplates) :
        try : 
           _pathIcons = os.path.dirname(__file__) + "/icons/buttons"
           _iconSourcesSelect    = _pathIcons + "/source_button.png"
           _iconSourcesVierge    = _pathIcons + "/vierge.png"

           if mItemTemplates == None : mItemTemplates = "Aucun" # Gestion si None
           for elemQMenuItem in self._mObjetQMenu.children() :
               if elemQMenuItem.text() == mItemTemplates : 
                  _mObjetQMenuIcon = QIcon(_iconSourcesSelect)
               else :                 
                  _mObjetQMenuIcon = QIcon(_iconSourcesVierge)
               elemQMenuItem.setIcon(_mObjetQMenuIcon)
        except :
           pass 
        return

    #==========================
    # == Gestion des Icons Flags dans le menu des templates
    def majQmenuExportIconFlag(self) :
        mListExtension = rdf_utils.available_formats(self.metagraph, self.shape)
        self._mObjetQMenuExport.clear()
        self._mObjetQMenuExport.setStyleSheet("QMenu { font-family:" + self.policeQGroupBox  +"; width: " + str((int(len(max(mListExtension))) * 10) + 70) + "px;}")
        #------------
        for elemQMenuItem in mListExtension :
            _mObjetQMenuItem = QAction(elemQMenuItem, self._mObjetQMenuExport)
            _mObjetQMenuItem.setText(elemQMenuItem)
            _mObjetQMenuItem.setObjectName(str(elemQMenuItem))
            self._mObjetQMenuExport.addAction(_mObjetQMenuItem)   
            #- Actions
            _mObjetQMenuItem.triggered.connect(lambda : self.clickButtonsExportActions())
        #-
        self.plumeExport.setPopupMode(self.plumeExport.MenuButtonPopup)
        self.plumeExport.setMenu(self._mObjetQMenuExport)
        return
    #==========================
    def createToolBar(self, _iconSourcesRead, _iconSourcesEmpty, _iconSourcesExport, _iconSourcesImport, _iconSourcesSave, _iconSourcesTemplate, _iconSourcesTranslation, _iconSourcesHelp, _iconSourcesParam):
        #Menu Dialog
        self.mMenuBarDialog = QMenuBar(self)
        self.mMenuBarDialog.setGeometry(QtCore.QRect(0, 0, 300, 20))
        _mColorFirstPlan, _mColorSecondPlan = "transparent", "#cac5b1"     #Brun            
        #--
        mText = QtWidgets.QApplication.translate("plume_main", "Edition") 
        self.plumeEdit = QtWidgets.QPushButton(self.mMenuBarDialog)
        if self.toolBarDialog == "picture" : self.plumeEdit.setStyleSheet("QPushButton { border: 0px solid black;}")
        self.plumeEdit.setIcon(QIcon(_iconSourcesRead))
        self.plumeEdit.setObjectName(mText)
        self.mTextToolTipRead = QtWidgets.QApplication.translate("plume_main", "Edit") 
        self.mTextToolTipEdit = QtWidgets.QApplication.translate("plume_main", "Read") 
        self.plumeEdit.setToolTip(self.mTextToolTipEdit)
        self.plumeEdit.setGeometry(QtCore.QRect(10,0,18,18))
        self.plumeEdit.clicked.connect(self.clickButtonsActions)
        #--
        mText = QtWidgets.QApplication.translate("plume_main", "Save") 
        self.plumeSave = QtWidgets.QPushButton(self.mMenuBarDialog)
        if self.toolBarDialog == "picture" : self.plumeSave.setStyleSheet("QPushButton { border: 0px solid black;}" "background-color: "  + _mColorFirstPlan  + ";}" "QPushButton::pressed { border: 0px solid black; background-color: " + _mColorSecondPlan + ";}")  
        self.plumeSave.setIcon(QIcon(_iconSourcesSave))
        self.plumeSave.setObjectName("Save")
        self.plumeSave.setToolTip(mText)
        self.plumeSave.setGeometry(QtCore.QRect(40,0,18,18))
        self.plumeSave.clicked.connect(self.clickButtonsActions)
        #--
        mText = QtWidgets.QApplication.translate("plume_main", "Empty") 
        self.plumeEmpty = QtWidgets.QPushButton(self.mMenuBarDialog)
        if self.toolBarDialog == "picture" : self.plumeEmpty.setStyleSheet("QPushButton { border: 0px solid black;}" "background-color: "  + _mColorFirstPlan  + ";}" "QPushButton::pressed { border: 0px solid black; background-color: " + _mColorSecondPlan + ";}")  
        self.plumeEmpty.setIcon(QIcon(_iconSourcesEmpty))
        self.plumeEmpty.setObjectName("Empty")
        mTextToolTip = QtWidgets.QApplication.translate("plume_main", "Vider la fiche de métadonnées.") 
        self.plumeEmpty.setToolTip(mTextToolTip)
        self.plumeEmpty.setGeometry(QtCore.QRect(70,0,18,18))
        self.plumeEmpty.clicked.connect(self.clickButtonsActions)
        #--                                        
        #====================
        #--QToolButton EXPORT                                               
        mText = QtWidgets.QApplication.translate("plume_main", "Export") 
        self.plumeExport = QtWidgets.QToolButton(self.mMenuBarDialog)
        if self.toolBarDialog == "picture" : self.plumeExport.setStyleSheet("QToolButton { border: 0px solid black;}")  
        self.plumeExport.setIcon(QIcon(_iconSourcesExport))
        self.plumeExport.setObjectName("Export")
        self.plumeExport.setGeometry(QtCore.QRect(85,0,42,18))
        mTextToolTip = QtWidgets.QApplication.translate("plume_main", "Exporter les métadonnées dans un fichier.") 
        self.plumeExport.setToolTip(mTextToolTip)
        #MenuQToolButton                        
        _mObjetQMenu = QMenu()
        self._mObjetQMenuExport = _mObjetQMenu
        #--QToolButton EXPORT                                               
        #====================
        #--
        mText = QtWidgets.QApplication.translate("plume_main", "Import") 
        self.plumeImport = QtWidgets.QPushButton(self.mMenuBarDialog)
        if self.toolBarDialog == "picture" : self.plumeImport.setStyleSheet("QPushButton { border: 0px solid black;}" "background-color: "  + _mColorFirstPlan  + ";}" "QPushButton::pressed { border: 0px solid black; background-color: " + _mColorSecondPlan + ";}")  
        self.plumeImport.setIcon(QIcon(_iconSourcesImport))
        self.plumeImport.setObjectName("Import")
        mTextToolTip = QtWidgets.QApplication.translate("plume_main", "Importer les métadonnées depuis un fichier.") 
        self.plumeImport.setToolTip(mTextToolTip)
        self.plumeImport.setGeometry(QtCore.QRect(135,0,18,18))
        self.plumeImport.clicked.connect(self.clickButtonsActions)
        #====================
        #--QToolButton TEMPLATE                                               
        mText = QtWidgets.QApplication.translate("plume_main", "Template") 
        self.plumeTemplate = QtWidgets.QToolButton(self.mMenuBarDialog)
        if self.toolBarDialog == "picture" : self.plumeTemplate.setStyleSheet("QToolButton { border: 0px solid black;}")  
        self.plumeTemplate.setIcon(QIcon(_iconSourcesTemplate))
        self.plumeTemplate.setObjectName("Template")
        self.plumeTemplate.setGeometry(QtCore.QRect(150,0,42,18))
        mTextToolTip = QtWidgets.QApplication.translate("plume_main", "Extension METADATA non installée.") 
        mTextToolTip = QtWidgets.QApplication.translate("plume_main", "Choisir un modèle de formulaire.") 
        self.plumeTemplate.setToolTip(mTextToolTip)
        #MenuQToolButton                        
        _mObjetQMenu = QMenu()
        self._mObjetQMenu = _mObjetQMenu
        #self.plumeTemplate.clicked.connect(self.clickButtonsActions)
        #--QToolButton TEMPLATE                                               
        #====================
        #--
        mText = QtWidgets.QApplication.translate("plume_main", "Translation") 
        self.plumeTranslation = QtWidgets.QPushButton(self.mMenuBarDialog)
        if self.toolBarDialog == "picture" : self.plumeTranslation.setStyleSheet("QPushButton { border: 0px solid black;}")  
        self.plumeTranslation.setIcon(QIcon(_iconSourcesTranslation))
        self.plumeTranslation.setObjectName(mText)
        self.mTextToolTipNon = QtWidgets.QApplication.translate("plume_main", "Activer les fonctions de traduction.") 
        self.mTextToolTipOui = QtWidgets.QApplication.translate("plume_main", "Désactiver les fonctions de traduction.") 
        self.plumeTranslation.setToolTip(self.mTextToolTipNon)
        self.plumeTranslation.setGeometry(QtCore.QRect(200,0,18,18))
        self.plumeTranslation.clicked.connect(self.clickButtonsActions)
        #------------
        #------------
        mText = QtWidgets.QApplication.translate("plume_main", "Customization of the IHM") 
        self.paramColor = QtWidgets.QPushButton(self.mMenuBarDialog)
        if self.toolBarDialog == "picture" : self.paramColor.setStyleSheet("QPushButton { border: 0px solid black;}" "background-color: "  + _mColorFirstPlan  + ";}" "QPushButton::pressed { border: 0px solid black; background-color: " + _mColorSecondPlan + ";}")  
        self.paramColor.setIcon(QIcon(_iconSourcesParam))
        self.paramColor.setObjectName(mText)
        self.paramColor.setToolTip(mText)
        self.paramColor.setGeometry(QtCore.QRect(230,0,18,18))
        self.paramColor.clicked.connect(self.clickColorDialog)
        #--
        mText = QtWidgets.QApplication.translate("plume_main", "Help") 
        self.plumeHelp = QtWidgets.QPushButton(self.mMenuBarDialog)
        if self.toolBarDialog == "picture" : self.plumeHelp.setStyleSheet("QPushButton { border: 0px solid black;}" "background-color: "  + _mColorFirstPlan  + ";}" "QPushButton::pressed { border: 0px solid black; background-color: " + _mColorSecondPlan + ";}")  
        self.plumeHelp.setIcon(QIcon(_iconSourcesHelp))
        self.plumeHelp.setObjectName(mText)
        self.plumeHelp.setToolTip(mText)
        self.plumeHelp.setGeometry(QtCore.QRect(250,0,18,18))
        self.plumeHelp.clicked.connect(self.myHelpAM)
        #------------
        return

    #==========================
    def myHelpAM(self):
        #-
        if self.fileHelp == "pdf" :
           valueDefautFileHelp = self.fileHelpPdf
        elif self.fileHelp == "html" :
           valueDefautFileHelp  = self.fileHelpHtml
        else :
           valueDefautFileHelp  = self.fileHelpHtml
        bibli_plume.execPdf(valueDefautFileHelp)
        return

#==========================
# Window Versus Dock
class MONDOCK(QDockWidget):
    def __init__(self, mDialog):
        super().__init__()
        dlg = QDockWidget()
        dlg.setObjectName("PLUME")
        dlg.setMinimumSize(420, 300)
        dlg.setWindowTitle(QtWidgets.QApplication.translate("plume_ui", "PLUGIN METADONNEES (Metadata storage in PostGreSQL)", None) + "  (" + str(bibli_plume.returnVersion()) + ")")
        mDialog.iface.addDockWidget(Qt.RightDockWidgetArea, dlg)
        dlg.setFloating(True if mDialog.ihm in ["dockTrue"] else False)
        dlg.setWidget(mDialog)
        dlg.resize(420, 300)
        mDialog.dlg = dlg

    #==========================
    def event(self, event):
        print("DOCK event " + str(event))
        event.accept()
        return

    #==========================
    def closeEvent(self, event):
        print(mDialog.ihm)
        print("DOCK closeEvent " + str(event))
        try :
           if hasattr(self, 'mConnectEnCours') :
              self.mConnectEnCours.close()
        except:
           pass

        try :
           self.navigateurTreeView.clicked.disconnect(self.retrieveInfoLayerBrowser)
        except:
           pass

        try :
           self.navigateurTreeView2.clicked.disconnect(self.retrieveInfoLayerBrowser)
        except:
           pass

        try :
           iface.layerTreeView().clicked.disconnect(self.retrieveInfoLayerQgis)
        except:
           pass
        return
         
# Window Versus Dock
            
                 