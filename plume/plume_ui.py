# (c) Didier  LECLERC 2020 CMSIG MTE-MCTRCT/SG/SNUM/UNI/DRC Site de Rouen
# créé sept 2021
#        **************************************************************************
#        copyright            : (C) 2021 by DL
#        **************************************************************************

from PyQt5 import QtCore, QtGui, QtWidgets, QtQuick 

from PyQt5.QtCore import *
from PyQt5.QtWidgets import (QAction, QMenu , QMenuBar, QToolBar, QApplication, QMessageBox, QFileDialog, QPlainTextEdit, QDialog, QStyle, 
                             QDockWidget, QTreeView, QGridLayout, QTabWidget, QWidget, QDesktopWidget, QSizePolicy, 
                             QTreeWidget, QTreeWidgetItem, QTreeWidgetItemIterator, QStyleFactory, QStyle, QToolBar)

from PyQt5.QtGui import QIcon, QStandardItem, QStandardItemModel
from html import escape

from . import bibli_plume
from .bibli_plume import *
#
from . import bibli_gene_objets
from .bibli_gene_objets import *
#
from . import docolorbloc
from . import doabout
from . import doimportcsw

from qgis.core import *
from qgis.gui import *
from qgis.PyQt.QtCore import QUrl

import qgis  
import os
import subprocess
import time
import sys
import traceback

from contextlib import contextmanager
import psycopg2
from plume.pg import queries
from plume.rdf.metagraph import copy_metagraph
from plume.pg.template import LocalTemplatesCollection
from plume.config import (VALUEDEFAUTFILEHELP, VALUEDEFAUTFILEHELPPDF, VALUEDEFAUTFILEHELPHTML, URLCSWDEFAUT, URLCSWIDDEFAUT)  


class Ui_Dialog_plume(object):
    def __init__(self):
        self.iface = qgis.utils.iface                                                          
        self.firstOpen = True                                 
        self.firstOpenConnect = True
        
    @contextmanager
    def safe_pg_connection(self) :
        if not getattr(self, 'mConnectEnCours', False) or self.mConnectEnCours.closed:
           self.getAllFromUri()
        try:
           yield
           
        except psycopg2.Error as err :
           self.layerBeforeClicked = ("", "")
           saveinitializingDisplay("write", self.layerBeforeClicked)
           bibli_plume.breakExecuteSql(self)

           if err.diag:
              zTitre = QtWidgets.QApplication.translate("plume_ui", "PLUME : Warning", None)
              zMess  = err.diag.message_primary  
              displayMess(self.Dialog, (2 if self.Dialog.displayMessage else 1), zTitre, zMess, Qgis.Warning, self.Dialog.durationBarInfo)

        except NoReturnSql as err_NoReturnSql :
           self.layerBeforeClicked = ("", "")
           saveinitializingDisplay("write", self.layerBeforeClicked)
           bibli_plume.breakExecuteSql(self)

           zTitre = QtWidgets.QApplication.translate("plume_ui", "PLUME : Warning", None)
           zMess  = str(err_NoReturnSql.mMess) 
           displayMess(self.Dialog, (2 if self.Dialog.displayMessage else 1), zTitre, zMess, Qgis.Warning, self.Dialog.durationBarInfo)

        except Exception as err_Exception :
           self.layerBeforeClicked = ("", "")
           saveinitializingDisplay("write", self.layerBeforeClicked)
           bibli_plume.breakExecuteSql(self)

           zTitre = QtWidgets.QApplication.translate("plume_ui", "PLUME : Warning", None)
           zMess  = str(err_Exception) + "\n" + str(traceback.format_tb(Exception.__traceback__)) 
           displayMess(self.Dialog, (2 if self.Dialog.displayMessage else 1), zTitre, zMess, Qgis.Warning, self.Dialog.durationBarInfo)
        
        finally:
           if getattr(self, 'mConnectEnCours', False) : self.mConnectEnCours.close()
                
    def setupUi(self, Dialog, _dicTooltipExiste):
        self.Dialog = Dialog
        Dialog.setObjectName("Dialog")
        self.zMessError_Transaction = "FIN TRANSACTION"
        self._dicTooltipExiste = _dicTooltipExiste
        #--
        mDic_LH = bibli_plume.returnAndSaveDialogParam(self, "Load")
        self.mDic_LH = mDic_LH
        #--
        self.lScreenDialog, self.hScreenDialog = int(self.mDic_LH["dialogLargeur"]), int(self.mDic_LH["dialogHauteur"])
        self.displayMessage    = False if self.mDic_LH["displayMessage"] == 'dialogTitle' else True #Qmessage box (dialogBox) ou barre de progression (dialogTitle)
        self.fileHelp          = VALUEDEFAUTFILEHELP      #Type Fichier Help
        self.fileHelpPdf       = VALUEDEFAUTFILEHELPPDF   #Fichier Help  PDF
        self.fileHelpHtml      = VALUEDEFAUTFILEHELPHTML  #Fichier Help  HTML
        self.durationBarInfo   = int(self.mDic_LH["durationBarInfo"])  #durée d'affichage des messages d'information
        self.ihm               = self.mDic_LH["ihm"]  #window/dock
        self.toolBarDialog     = self.mDic_LH["toolBarDialog"]    #toolBarDialog
        self.versionPlumeBibli = self.mDic_LH["versionPlumeBibli"]  #version Plume des bibliothèques
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
        self.urlCswDefaut      = URLCSWDEFAUT       #l'Url par defaut
        self.urlCswIdDefaut    = URLCSWIDDEFAUT     #l'Id de l'Url par defaut
        self.urlCsw            = self.mDic_LH["urlCsw"]             #Liste des urlcsw sauvegardées
        # for geometry
        self.geomColor       = self.mDic_LH["geomColor"]       
        self.geomEpaisseur   = self.mDic_LH["geomEpaisseur"]       
        self.geomPoint       = self.mDic_LH["geomPoint"]       
        self.geomPointEpaisseur = self.mDic_LH["geomPointEpaisseur"]       
        self.geomZoom        = True if self.mDic_LH["geomZoom"] == "true" else False
        self.geomPrecision   = int(self.mDic_LH["geomPrecision"])       
        #-
        #tooltip         
        self.activeTooltip          = True if mDic_LH["activeTooltip"]          == "true" else False
        self.activeTooltipWithtitle = True if mDic_LH["activeTooltipWithtitle"] == "true" else False
        self.activeTooltipLogo      = True if mDic_LH["activeTooltipLogo"]      == "true" else False
        self.activeTooltipCadre     = True if mDic_LH["activeTooltipCadre"]     == "true" else False
        self.activeTooltipColor     = True if mDic_LH["activeTooltipColor"]     == "true" else False
        self.activeTooltipColorText       = mDic_LH["activeTooltipColorText"] 
        self.activeTooltipColorBackground = mDic_LH["activeTooltipColorBackground"] 
        #-
        mDicType         = ["ICON_CROSS", "ICON_X", "ICON_BOX", "ICON_CIRCLE", "ICON_FULL_BOX" , "ICON_DIAMOND" , "ICON_FULL_DIAMOND"]
        mDicTypeObj      = [QgsRubberBand.ICON_X, QgsRubberBand.ICON_CROSS, QgsRubberBand.ICON_BOX, QgsRubberBand.ICON_CIRCLE, QgsRubberBand.ICON_FULL_BOX, QgsRubberBand.ICON_DIAMOND, QgsRubberBand.ICON_FULL_DIAMOND]
        self.mDicTypeObj = dict(zip(mDicType, mDicTypeObj)) # For bibli_plume_tools_map
        _pathIconsUser = QgsApplication.qgisSettingsDirPath().replace("\\","/") + "plume/icons/buttons"
        createFolder(_pathIconsUser)        
        #-
        #Management Click before open IHM 
        if self.mDic_LH["layerBeforeClickedWho"] == "qgis" : 
           self.layerBeforeClicked = (bibli_plume.returnIfExisteInLegendeInterface(self, self.mDic_LH["layerBeforeClicked"]), self.mDic_LH["layerBeforeClickedWho"], self.mDic_LH["layerBeforeClickedBrowser"]) # Couche mémorisée avant ouverture et de l'origine
        elif self.mDic_LH["layerBeforeClickedWho"] == "postgres" : 
           self.layerBeforeClicked = (bibli_plume.returnIfExisteInBrowser(self, self.mDic_LH["layerBeforeClicked"]), self.mDic_LH["layerBeforeClickedWho"], self.mDic_LH["layerBeforeClickedBrowser"]) # Couche mémorisée avant ouverture et de l'origine
        else :
           self.layerBeforeClicked = ('', '') 
        #Cas ou l'instance sauvegardé dans le QGIS3.INI n'a plus de correspondance 
        if self.layerBeforeClicked[0] is None : self.layerBeforeClicked = ('', '')
        #Cas ou l'instance sauvegardé dans le QGIS3.INI n'a plus de correspondance 
           
        # for geometry
        # liste des Paramétres UTILISATEURS
        bibli_plume.listUserParam(self)
        # liste des Paramétres UTILISATEURS
        #for test param user
        """
        l = [ self.language,self.initTranslation,self.langList,self.geoideJSON,self.preferedTemplate,self.enforcePreferedTemplate,\
              self.readHideBlank,self.readHideUnlisted,self.editHideUnlisted,self.readOnlyCurrentLanguage,\
              self.editOnlyCurrentLanguage,self.labelLengthLimit,self.valueLengthLimit,self.textEditRowSpan ] 
        print(l)
        """
        #for test param user
        #---
        _pathIcons = os.path.dirname(__file__) + "/icons/general"
        _iconSourcesRead          = _pathIcons + "/read.svg"
        _iconSourcesEmpty         = _pathIcons + "/empty.svg"
        _iconSourcesExport        = _pathIcons + "/export.svg"
        _iconSourcesImport        = _pathIcons + "/import.svg"
        _iconSourcesCopy          = _pathIcons + "/copy_all.svg"
        _iconSourcesPaste         = _pathIcons + "/paste_all.svg"
        _iconSourcesSave          = _pathIcons + "/save.svg"
        _iconSourcesTemplate      = _pathIcons + "/template.svg"
        _iconSourcesTranslation   = _pathIcons + "/translation.svg"
        _iconSourcesParam         = _pathIcons + "/configuration.svg"
        _iconSourcesInterrogation = _pathIcons + "/info.svg"
        _iconSourcesHelp          = _pathIcons + "/assistance.png"
        _iconSourcesAbout         = _pathIcons + "/about.png"
        _iconSourcesVerrou        = _pathIcons + "/verrou.svg"
        # For menu contex QGroupBox
        self._iconSourcesCopy, self._iconSourcesPaste = _iconSourcesCopy, _iconSourcesPaste
        _iconSourcesPaste         = _pathIcons + "/paste_all.svg"
        
        self.listIconToolBar = [ _iconSourcesRead, _iconSourcesSave, _iconSourcesEmpty, _iconSourcesExport, _iconSourcesImport, _iconSourcesCopy, _iconSourcesPaste, _iconSourcesTemplate, _iconSourcesTranslation, _iconSourcesParam, _iconSourcesInterrogation, _iconSourcesHelp, _iconSourcesAbout, _iconSourcesVerrou ]
        #--------
        Dialog.resize(QtCore.QSize(QtCore.QRect(0,0, self.lScreenDialog, self.hScreenDialog).size()).expandedTo(Dialog.minimumSizeHint()))
        self.messWindowTitle = QtWidgets.QApplication.translate("plume_ui", "PLUGIN METADATA (Metadata storage in PostGreSQL)", None) + "  (" + str(bibli_plume.returnVersion()) + ")" 
        Dialog.setWindowTitle(self.messWindowTitle)
        Dialog.setWindowModality(Qt.WindowModal)
        Dialog.setWindowFlags(Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint) 
        _pathIcons = os.path.dirname(__file__) + "/icons/logo"
        iconSource          = _pathIcons + "/plume.svg"
        iconSourceTooltip   = _pathIcons + "/plume.png"
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(iconSource), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)

        #Affiche info si MAJ version
        self.barInfo = QgsMessageBar(self.iface.mainWindow())
        self.barInfo.setSizePolicy( QSizePolicy.Minimum, QSizePolicy.Fixed )
        self.barInfo.setGeometry(10,25, self.iface.mainWindow().width()-30, 30)
        #==========================              
        #Zone Onglets
        self.tabWidget = QTabWidget(Dialog)
        self.tabWidget.setObjectName("tabWidget")
        x, y = 10, 45
        larg, haut =  self.lScreenDialog -20, (self.hScreenDialog - 60 )
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
           bibli_plume.afficheNoConnections(self, "first")
           self.listeResizeIhm = [] # For resizeIhm
        #First Open 
        #==========================

        #=====================================================  
        # Window Versus Dock
        if self.ihm in ["dockTrue", "dockFalse"] :
           monDock = MONDOCK(self.Dialog)
           self.monDock = monDock
        # Window Versus Dock
        #----
        self.mode            = "read"  #Intiialise les autres instances  
        self.verrouLayer     = False   #Verrouillage de la couche 
        self.nameVerrouLayer = None    #Couche verrouillée 
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
        #Active Tooltip
        self._myExploBrowser  = MyExploBrowser(self.navigateur.findChildren(QTreeView)[0],  self._dicTooltipExiste, self.activeTooltip, self.activeTooltipColorText, self.activeTooltipColorBackground, self.langList, iconSourceTooltip,  self.activeTooltipLogo,  self.activeTooltipCadre,  self.activeTooltipColor, self.activeTooltipWithtitle)
        self._myExploBrowser2 = MyExploBrowser(self.navigateur2.findChildren(QTreeView)[0], self._dicTooltipExiste, self.activeTooltip, self.activeTooltipColorText, self.activeTooltipColorBackground, self.langList, iconSourceTooltip,  self.activeTooltipLogo,  self.activeTooltipCadre,  self.activeTooltipColor, self.activeTooltipWithtitle)
        
        #==========================
        #Instanciation des "shape, template, vocabulary, mode" 
        self.translation = bibli_plume.returnObjetTranslation(self)
        #==========================
        #Management Click before open IHM 
        if self.layerBeforeClicked[0] != "" : 
           if self.layerBeforeClicked[1] == "qgis" : 
              self.retrieveInfoLayerQgis(None)
           elif self.layerBeforeClicked[1] == "postgres" : 
              self.retrieveInfoLayerQgis(self.layerBeforeClicked[0])
        #Management Click before open IHM 
           
        # == Gestion Context ==
        with self.safe_pg_connection() :
           self.displayToolBar(*self.listIconToolBar)
    #= Fin setupUi

    #==========================
    # == Gestion des actions de boutons de la barre de menu
    def clickButtonsActions(self):
        # == Gestion Context ==
        with self.safe_pg_connection() :
           # If suppression d'une couche active pour les métadonnées affichées
           if not bibli_plume.gestionErreurExisteLegendeInterface(self) : return
           # If suppression d'une couche active pour les métadonnées affichées

           mItem = self.mMenuBarDialog.sender().objectName()
           #**********************
           if mItem == "Edition" :
              #Interroge l'utilisateur si modifications
              if self.mode == "edit" and self.zoneConfirmMessage :
                 if self.mDicObjetsInstancies.modified or bibli_plume.ifChangeValues(self.mDicObjetsInstancies) :
                    if QMessageBox.question(None, "Confirmation", QtWidgets.QApplication.translate("plume_ui", "If you continue, unsaved changes will be lost."),QMessageBox.Ok|QMessageBox.Cancel) ==  QMessageBox.Cancel : return
                    #Si vous poursuivez, les modifications non enregistrées seront perdues.
        
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
              # For mode Edit
              if self.mode == "edit" : 
                 if self.nameVerrouLayer == None  : self.nameVerrouLayer = self.layer 
                 self.verrouLayer = True
              else :
                 self.iface.setActiveLayer(self.nameVerrouLayer)
                 self.nameVerrouLayer = None 
                 self.verrouLayer = False
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
              old_metagraph = self.metagraph
              self.metagraph = copy_metagraph(None, old_metagraph)
           #**********************
           elif mItem == "Copy" :
              self.copyMetagraph = self.metagraph
              if self.copyMetagraph !=  None :
                 mTextToolTip = QtWidgets.QApplication.translate("plume_main", "Paste the metadata card of ") + "<b>" + str(self.schema) + "." + str(self.table) + "</b>" 
              else :    
                 mTextToolTip = QtWidgets.QApplication.translate("plume_main", "Paste the saved metadata card.")    
              self.copyMetagraphTooltip = mTextToolTip
              self.plumePaste.setToolTip(mTextToolTip)
           #**********************
           elif mItem == "Paste" :
              if self.copyMetagraph != None :
                 src_metagraph, old_metagraph = self.copyMetagraph, self.metagraph
                 _metagraph = copy_metagraph(src_metagraph, old_metagraph)
                 self.metagraph = _metagraph
           #**********************
           elif mItem == "plumeImportFile" :
              if self.saveMetaGraph :
                 self.oldMetagraph  = self.metagraph
              else :   
                 self.metagraph     = self.oldMetagraph
              self.saveMetaGraph = False
              #-   
              metagraph  = bibli_plume.importObjetMetagraph(self)
              if metagraph != None : self.metagraph = metagraph
           #**********************
           elif mItem == "plumeImportFileInspire" :
              if self.saveMetaGraph :
                 self.oldMetagraph  = self.metagraph
              else :   
                 self.metagraph     = self.oldMetagraph
              self.saveMetaGraph = False
              #-   
              metagraph  = bibli_plume.importObjetMetagraphInspire(self)
              if metagraph != None : self.metagraph = metagraph
           #**********************
           elif mItem == "Traduction" :
              self.translation = (False if self.translation else True) 
           #**********************
           elif QtWidgets.QApplication.translate("plume_ui", mItem) == "Verrouillage" :
              self.verrouLayer = (False if self.verrouLayer else True) 
              self.nameVerrouLayer = (self.layer if self.verrouLayer else None) 

           #**********************
           #*** commun
           if mItem in ["Edition", "Save", "Empty", "plumeImportFile", "plumeImportFileInspire", "Paste", "Traduction"] :
              bibli_plume.saveObjetTranslation(self.translation)
              self.generationALaVolee(bibli_plume.returnObjetsMeta(self))
           #-
           self.displayToolBar(*self.listIconToolBar)
        return
    # == Gestion des actions de boutons de la barre de menu
    #==========================

    #==========================
    # == Gestion des actions du bouton EXPORT de la barre de menu
    def clickButtonsExportActions(self):
        # If suppression d'une couche active pour les métadonnées affichées
        if not bibli_plume.gestionErreurExisteLegendeInterface(self) : return
        # If suppression d'une couche active pour les métadonnées affichées

        mItemExport = self.mMenuBarDialog.sender().objectName()
        exportObjetMetagraph(self, self.schema, self.table, mItemExport, self.metagraph.available_export_formats(no_duplicate=True, format=mItemExport))        
        
        return
    # == Gestion des actions du bouton EXPORT de la barre de menu
    #==========================

    #==========================
    # == Gestion des actions du bouton TEMPLATE de la barre de menu
    def clickButtonsTemplateActions(self):
        # == Gestion Context ==
        with self.safe_pg_connection() :
           # If suppression d'une couche active pour les métadonnées affichées
           if not bibli_plume.gestionErreurExisteLegendeInterface(self) : return
           # If suppression d'une couche active pour les métadonnées affichées

           mItemTemplates = self.mMenuBarDialog.sender().objectName()

           """
           #Lecture existence Extension METADATA
           _mContinue = True
           #if not hasattr(self, 'mConnectEnCours') :
           #   if not self.instalMetadata : _mContinue = False
           """

           if mItemTemplates == "Aucun" :
              self.template = None
           else : 
              #-
              if self.instalMetadata :
                 # Choix du modèle
                 bibli_plume.generationTemplateAndTabs(self, mItemTemplates)
              else : 
                 self.template = self.templates_collection.get(mItemTemplates) if mItemTemplates else None
              #-
           # Génération à la volée
           self.generationALaVolee(bibli_plume.returnObjetsMeta(self))

           # MAJ ICON FLAGS
           self.majQmenuModeleIconFlag(mItemTemplates)
           #
           self.majButtonTemplate(self.plumeTemplate, mItemTemplates, int(len(mItemTemplates)))
           # MAJ ICON FLAGS
        return
    # == Gestion des actions du bouton TEMPLATE de la barre de menu
    #==========================

    #==========================
    # == Gestion des actions du bouton Changement des langues
    def  clickButtonsChoiceLanguages(self):
        # == Gestion Context ==
        with self.safe_pg_connection() :
           # If suppression d'une couche active pour les métadonnées affichées
           if not bibli_plume.gestionErreurExisteLegendeInterface(self) : return
           # If suppression d'une couche active pour les métadonnées affichées

           mItem = self.mMenuBarDialog.sender().objectName()
           #un peu de robustesse car théo gérer dans le lecture du Qgis3.ini
           if mItem == "" : 
              self.language, mItem = "fr", "fr" 
           else:
               self.language = mItem
           if mItem not in self.langList : self.langList.append(mItem)  
           #un peu de robustesse car théo gérer dans le lecture du Qgis3.ini
           self.plumeChoiceLang.setText(mItem)
           mDicUserSettings        = {}
           mSettings = QgsSettings()
           mSettings.beginGroup("PLUME")
           mSettings.beginGroup("UserSettings")
           #Ajouter si autre param
           mDicUserSettings["language"] = mItem
           mDicUserSettings["langList"] = self.langList
           #----
           for key, value in mDicUserSettings.items():
               mSettings.setValue(key, value)
           #======================
           mSettings.endGroup()
           mSettings.endGroup()
           #----
           #Regénération du dictionnaire    
           self.generationALaVolee(bibli_plume.returnObjetsMeta(self))
           #-
           self.displayToolBar(*self.listIconToolBar)
        return
    # == Gestion des actions du bouton Changement des langues
    #==========================


    #==================================================
    #AJOUT 30 JANVIER 2022
    def menuContextuelQGroupBox(self, _keyObjet, _mObjetGroupBox, point):
        _menuGroupBox = QMenu() 
        _menuGroupBox.setStyleSheet("QMenu {  font-family:" + self.policeQGroupBox  +"; width:120px; border-style:" + self.editStyle  + "; border-width: 0px;}")
        #-------   
        menuIcon = returnIcon(self._iconSourcesPaste)          
        _menuActionQGroupBoxCopier = QAction(QIcon(menuIcon), "Copier le bloc.", _menuGroupBox)
        _menuGroupBox.addAction(_menuActionQGroupBoxCopier)
        _menuActionQGroupBoxCopier.triggered.connect(lambda : self.actionFonctionQGroupBox(_keyObjet, "copierQGroupBox"))
        #-------   
        menuIcon = returnIcon(self._iconSourcesCopy)          
        _menuActionQGroupBoxColler = QAction(QIcon(menuIcon), "Coller le bloc.", _menuGroupBox)
        _menuGroupBox.addAction(_menuActionQGroupBoxColler)
        _menuActionQGroupBoxColler.triggered.connect(lambda : self.actionFonctionQGroupBox(_keyObjet, "collerQGroupBox"))
        #-------
        _menuGroupBox.exec_(_mObjetGroupBox.mapToGlobal(point))
        return

    #**********************
    def actionFonctionQGroupBox(self,_keyObjet, mAction):
        print(str(_keyObjet))
        if mAction == "copierQGroupBox" :
           print("copierQGroupBox")
        elif mAction == "collerQGroupBox" :
           print("collerQGroupBox")
        return
    #AJOUT 30 JANVIER 2022
    #==================================================

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
        self.dic_geoToolsShow = {} # For visualisation sur BBOX, Centroid and geometry
        #Supprime si l'objet existe l'affichage du rubberBand et desactive le process QgsMapTool
        try : 
           for k, v in self.dic_objetMap.items() :
              try : 
                 qgis.utils.iface.mapCanvas().unsetMapTool(self.dic_objetMap[k])
                 self.dic_objetMap[k].rubberBand.hide()
              except :
                 pass        
        except :
           pass        
        #Supprime si l'objet existe l'affichage du rubberBand
        self.dic_objetMap     = {} # For visualisation sur BBOX, Centroid and geometry

        #*****************************
        # ** BEFORE SAISIE ** Mode automatique calcul des Métadonnées
        # Lorsque la clé correspond à un widget de saisie, le calcul doit avoir lieu avant la saisie de la valeur dans le widget
        # Il s’agit là aussi de boucler sur les clés du dictionnaire de widgets pour exécuter les calculs
        for key, value in _dict.items_to_compute():
            action_mObjetQToolButton_ComputeButton(self, key, value, 'BEFORE')
        #*****************************
                    
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
        iface.layerTreeView().clicked.connect(lambda : self.retrieveInfoLayerQgis(None))
                
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
    def retrieveInfoLayerQgis(self, _layerBeforeClicked = None) :
        #-
        #Management Click before open IHM
        if _layerBeforeClicked != None :  
           self.layer = _layerBeforeClicked #Management Click before open IHM
        else :    
           if self.verrouLayer :
              return
           else :
              self.layer = iface.activeLayer()
        #-
        if self.layer:
           if self.layer.dataProvider().name() == 'postgres':
              # == Gestion Context ==
              with self.safe_pg_connection() :
                #self.getAllFromUri()
                self.messWindowTitle = "Plume | " + self.returnSchemaTableGeom(self.layer)[0] + "." + self.returnSchemaTableGeom(self.layer)[1] + " (" + self.returnSchemaTableGeom(self.layer)[2] + ")"
                #--                                                                          
                bibli_plume.afficheNoConnections(self, "hide")
                #-
                self.comment    = bibli_plume.returnObjetComment(self, self.schema, self.table)
                self.metagraph  = bibli_plume.returnObjetMetagraph(self, self.comment)
                self.oldMetagraph  = self.metagraph
                self.saveMetaGraph = False
                self.columns    = bibli_plume.returnObjetColumns(self, self.schema, self.table)
                self.data       = bibli_plume.returnObjetData(self)
                self.mode = "read"
                self.loadLayer = self.ifLayerLoad(self.layer)
                #-
                self.displayToolBar(*self.listIconToolBar)
                #-
                if self.instalMetadata :
                   #-
                   tpl_labelDefaut      = bibli_plume.returnObjetTpl_label(self, None)
                   if tpl_labelDefaut :
                      self.template     = bibli_plume.generationTemplateAndTabs(self, tpl_labelDefaut)
                   else :
                      self.template     = None
                else :
                   tpl_labelDefaut      = bibli_plume.returnObjetTpl_label(self, "LOCAL")
                   self.template        = self.templates_collection[tpl_labelDefaut] if tpl_labelDefaut else None
                #-
                self.createQmenuModele(self._mObjetQMenu, self.templateLabels)
                self.majQmenuModeleIconFlag(tpl_labelDefaut)
                #
                self.majButtonTemplate(self.plumeTemplate, "Aucun" if tpl_labelDefaut == None else tpl_labelDefaut, int(len("Aucun" if tpl_labelDefaut == None else tpl_labelDefaut)))
                #-
                self.layerQgisBrowserOther = "QGIS"
                #-
                self.generationALaVolee(bibli_plume.returnObjetsMeta(self))
                #-
                self.layerBeforeClicked = (self.layer, "qgis")
                bibli_plume.saveinitializingDisplay("write", self.layerBeforeClicked)                 
           else :
              if not self.verrouLayer : bibli_plume.initIhmNoConnection(self)
        return

    #---------------------------
    def retrieveInfoLayerBrowser(self, index):
        #-
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
        if isinstance(item, QgsLayerItem) :
           if self.ifVectorPostgres(item) :
              if self.verrouLayer :
                 return
              else :
                 self.layer = QgsVectorLayer(item.uri(), item.name(), 'postgres')
                 # == Gestion Context ==
                 with self.safe_pg_connection() :
                    #self.getAllFromUri()
                    self.messWindowTitle = "Plume | " + self.returnSchemaTableGeom(self.layer)[0] + "." + self.returnSchemaTableGeom(self.layer)[1] + " (" + self.returnSchemaTableGeom(self.layer)[2] + ")"
                    #--
                    bibli_plume.afficheNoConnections(self, "hide")
                    #-
                    self.comment    = bibli_plume.returnObjetComment(self, self.schema, self.table)
                    self.metagraph  = bibli_plume.returnObjetMetagraph(self, self.comment)
                    self.oldMetagraph  = self.metagraph
                    self.saveMetaGraph = False
                    self.columns    = bibli_plume.returnObjetColumns(self, self.schema, self.table)
                    self.data       = bibli_plume.returnObjetData(self)
                    self.mode = "read"
                    self.loadLayer = self.ifLayerLoad(self.layer)
                    #-
                    self.displayToolBar(*self.listIconToolBar)
                    #-
                    if self.instalMetadata :
                       #-
                       tpl_labelDefaut      = bibli_plume.returnObjetTpl_label(self, None)
                       if tpl_labelDefaut :
                          self.template     = bibli_plume.generationTemplateAndTabs(self, tpl_labelDefaut)
                       else :
                          self.template     = None
                    else :
                       tpl_labelDefaut      = bibli_plume.returnObjetTpl_label(self, "LOCAL")
                       self.template        = self.templates_collection[tpl_labelDefaut] if tpl_labelDefaut else None
                    #-
                    self.createQmenuModele(self._mObjetQMenu, self.templateLabels)
                    self.majQmenuModeleIconFlag(tpl_labelDefaut)
                    #
                    self.majButtonTemplate(self.plumeTemplate, "Aucun" if tpl_labelDefaut == None else tpl_labelDefaut, int(len("Aucun" if tpl_labelDefaut == None else tpl_labelDefaut)))
                    #-
                    self.layerQgisBrowserOther = "BROWSER"
                    #-
                    self.generationALaVolee(bibli_plume.returnObjetsMeta(self))
                    #-
                    self.layerBeforeClicked = (self.layer, "postgres")
                    bibli_plume.saveinitializingDisplay("write", self.layerBeforeClicked, index, mNav)                 
           else :
              if not self.verrouLayer : bibli_plume.initIhmNoConnection(self)
        else :
           if not self.verrouLayer : bibli_plume.initIhmNoConnection(self)
        return

    #---------------------------
    def getAllFromUri(self):
        # ex : Projet fermé
        try : 
           if not getattr(self, 'layer', False) : 
              bibli_plume.breakExecuteSql(self)
              return
        except :       
           bibli_plume.breakExecuteSql(self)
           return
        uri = QgsDataSourceUri(self.layer.source())
        self.schema, self.table, self.geom = uri.schema(), uri.table(), uri.geometryColumn()
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
        #===Existence de l'extension Postgis   
        self.postgis_exists = self.if_postgis_exists()
        #===Existence de l'extension Postgis   
        return

    #----------------------
    def ifVectorPostgres(self, item) : return True if item.providerKey() == 'postgres' else False     

    #----------------------
    def returnSchemaTableGeom(self, mLayer) :
        try :
           uri = QgsDataSourceUri(self.layer.source())
           _schema, _table, _geom = uri.schema(), uri.table(), uri.geometryColumn()
        except : 
           _schema, _table, _geom = "", "", ""
        return (_schema, _table, _geom)

    #----------------------
    def ifLayerLoad(self, mLayer) :
        mIfLayerLoad = False
        for elemLayer in QgsProject.instance().mapLayers().values():
            if mLayer.id() == elemLayer.id() : 
               mIfLayerLoad = True
               break
        return mIfLayerLoad     

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
        Dialog.setWindowTitle(self.messWindowTitle)

    #==========================
    def clickColorDialog(self):
        d = docolorbloc.Dialog(self)
        d.exec_()
        return
        
    #==========================
    def clickImportCSW(self):
        d = doimportcsw.Dialog(self)
        d.exec_()
        return
        
    #==========================
    def clickAbout(self):
        d = doabout.Dialog()
        d.exec_()
        return
        
    #==========================
    def if_postgis_exists(self) :
        mKeySql = queries.query_exists_extension('postgis')
        r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self.mConnectEnCours, mKeySql, optionRetour = "fetchone")
        return r

    #==========================
    # == Gestion des actions de boutons de la barre de menu
    def displayToolBar(self, _iconSourcesRead, _iconSourcesEmpty, _iconSourcesExport, _iconSourcesImport, _iconSourcesSave, _iconSourcesCopy, _iconSourcesPaste, _iconSourcesTemplate, _iconSourcesTranslation, _iconSourcesParam, _iconSourcesInterrogation, _iconSourcesHelp, _iconSourcesAbout, _iconSourcesVerrou):
        #-- Désactivation
        self.plumeEdit.setEnabled(False)
        self.plumeSave.setEnabled(False)
        self.plumeEmpty.setEnabled(False)
        self.plumeExport.setEnabled(False)
        self.plumeImport.setEnabled(False)
        self.plumeCopy.setEnabled(False)
        self.plumePaste.setEnabled(False)
        self.plumeTemplate.setEnabled(False)
        self.plumeTranslation.setEnabled(False)
        self.plumeChoiceLang.setEnabled(False)
        self.plumeVerrou.setEnabled(False)

        #====================
        #====================
        #--QToolButton TEMPLATE                                               
        if hasattr(self, 'mConnectEnCours') :
           self.plumeTemplate.setIcon(QIcon(_iconSourcesTemplate))
           self.plumeTemplate.setObjectName("Template")
           #Lecture existence Extension METADATA            
           mKeySql = queries.query_plume_pg_check()
           r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self.mConnectEnCours, mKeySql, optionRetour = "fetchall")
           result = r[0]
           self.instalMetadata = False
           #Information si not installe
           if not result[0]:
              if not result[3]:
                  pb = "L'extension PlumePg n'est pas disponible sur le serveur cible."
              elif not result[2]:
                  pb = "L'extension PlumePg n'est pas installée sur la base cible."
              elif result[5]:
                  pb = 'Votre rôle de connexion ne dispose pas du privilège ' \
                      'SELECT sur {} {}.'.format(
                      'la table' if len(result[5]) == 1 else 'les tables',
                      ', '.join(result[5]))
              elif result[4]:
                  pb = 'Votre rôle de connexion ne dispose pas du privilège ' \
                      'USAGE sur {} {}.'.format(
                      'le schéma' if len(result[4]) == 1 else 'les schémas',
                      ', '.join(result[4]))
              else:
                  pb = 'Votre version de Plume est incompatible avec PlumePg < {} ou ≥ {}' \
                      ' (version base cible : PlumePg {}).'.format(result[1][0],
                      result[1][1], result[2])
           if r[0][0] :
              self.instalMetadata = True
              self.plumeTemplate.setEnabled(True)
              #MenuQToolButton                        
              # Génération des items via def createQmenuModele(self, _mObjetQMenu, templateLabels)
              mTextToolTip = QtWidgets.QApplication.translate("plume_ui", "Choose a form template.")  
              self.plumeTemplate.setEnabled(True)
           else :
              #instanciation des modèles LOCAUX disponibles si l'extension PLUME n'est pas installée 
              self.templates_collection = LocalTemplatesCollection()
              #instanciation des modèles LOCAUX disponibles si l'extension PLUME n'est pas installée 

              self.plumeTemplate.setEnabled(False)
              mTextToolTip = QtWidgets.QApplication.translate("plume_ui", "Choose a form template.")  
              mTextToolTip += "<br><br><i>NB : Vous n'avez accès qu'aux modèles pré-configurés standards. " + escape(pb) + "</i>"

           self.plumeTemplate.setToolTip(mTextToolTip)
        #--QToolButton TEMPLATE                                               
        #====================
        #====================

        if hasattr(self, 'mConnectEnCours') :
           #--QToolButton EXPORT                                               
           self.majQmenuExportIconFlag()
           #-
           mKeySql = queries.query_is_relation_owner(self.schema, self.table)
           r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self.mConnectEnCours, mKeySql, optionRetour = "fetchone")
           
           #-- Activation ou pas 
           self.plumeEdit.setEnabled(r)
           self.plumeSave.setEnabled(r)
           self.plumeEmpty.setEnabled(r)
           self.plumeExport.setEnabled(r)
           self.plumeImport.setEnabled(r)
           self.plumeCopy.setEnabled(r)
           self.plumePaste.setEnabled(True if (self.copyMetagraph != None and self.mode == "edit") else False)
           self.plumeTemplate.setEnabled(r)
           self.plumeTranslation.setEnabled(True if self.mode == "edit" else False)
           self.plumeChoiceLang.setEnabled(r)
           
           self.plumeVerrou.setEnabled(False if self.mode == "edit" else True)
           if self.mode == "edit" : self.verrouLayer = True
           
           #Mode edition avec les droits
           if r == True and self.mode == 'read' : 
              self.plumeSave.setEnabled(False)
              self.plumeEmpty.setEnabled(False)
              self.plumeImport.setEnabled(False)                  
              self.plumeTranslation.setEnabled(False)
        #-
        self.plumeEdit.setToolTip(self.mTextToolTipEdit if self.mode == 'read' else self.mTextToolTipRead)   
        if self.toolBarDialog == "picture" :
           _mColorFirstPlan, _mColorSecondPlan = "transparent", "#cac5b1"     #Brun            
           self.plumeEdit.setStyleSheet("QPushButton { border: 0px solid black; background-color: "  + _mColorFirstPlan  + ";}" "QPushButton::pressed { border: 0px solid black; background-color: " + _mColorSecondPlan + ";}"  if self.mode == 'read' else \
                                        "QPushButton { border: 0px solid black;; background-color: " + _mColorSecondPlan + ";}" "QPushButton::pressed { border: 0px solid black; background-color: " + _mColorFirstPlan  + ";}")   
           self.plumeTranslation.setStyleSheet("QPushButton { border: 0px solid black; background-color: "  + _mColorFirstPlan  + ";}" "QPushButton::pressed { border: 0px solid black; background-color: " + _mColorSecondPlan + ";}"  if not self.translation else \
                                        "QPushButton { border: 0px solid black;; background-color: " + _mColorSecondPlan + ";}" "QPushButton::pressed { border: 0px solid black; background-color: " + _mColorFirstPlan  + ";}")   
           self.plumeVerrou.setStyleSheet("QPushButton { border: 0px solid black; background-color: "  + _mColorFirstPlan  + ";}" "QPushButton::pressed { border: 0px solid black; background-color: " + _mColorSecondPlan + ";}"  if not self.verrouLayer else \
                                        "QPushButton { border: 0px solid black;; background-color: " + _mColorSecondPlan + ";}" "QPushButton::pressed { border: 0px solid black; background-color: " + _mColorFirstPlan  + ";}")   

        #-ToolTip
        #-
        if self.copyMetagraph !=  None :
           mTextToolTip = self.copyMetagraphTooltip
        else :    
           mTextToolTip = QtWidgets.QApplication.translate("plume_ui", "Paste the saved metadata card.")  
        self.plumePaste.setToolTip(mTextToolTip)
        #-
        self.plumeTranslation.setToolTip(self.mTextToolTipOui if self.translation else self.mTextToolTipNon)   
        #-
        if self.mode == "edit" :
           self.plumeVerrou.setToolTip("")
        else :   
           self.plumeVerrou.setToolTip(self.mTextToolTipVerrouEdit if self.verrouLayer else self.mTextToolTipVerrouRead)
        if self.nameVerrouLayer != None :   
           self.messWindowTitleVerrou = "Plume | " + self.returnSchemaTableGeom(self.nameVerrouLayer)[0] + "." + self.returnSchemaTableGeom(self.nameVerrouLayer)[1] + " (" + self.returnSchemaTableGeom(self.nameVerrouLayer)[2] + ")"
        else :    
           self.messWindowTitleVerrou = ""
        self.Dialog.setWindowTitle(self.messWindowTitleVerrou if self.verrouLayer else self.messWindowTitle)   
        if hasattr(self, "dlg") : self.dlg.setWindowTitle(self.messWindowTitleVerrou if self.verrouLayer else self.messWindowTitle)   
        return

    #==========================
    # == Gestion des actions de boutons de la barre de menu
    def createQmenuModele(self, _mObjetQMenu, templateLabels) :
        _mObjetQMenu.clear()
        templateLabels.insert(0, "Aucun")
        self.lenButtonTemplate = int(len(max(templateLabels, key=len)) * 10) + 20     
        _mObjetQMenu.setStyleSheet("QMenu { font-family:" + self.policeQGroupBox  +"; width: " + str(self.lenButtonTemplate) + "px;}")
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
    # == Gestion de la taille et du texte du bouton Templates
    def majButtonTemplate(self, _plumeTemplate, _mTemplateTextChoice, _mLenTemplateTextChoice) :
        _plumeTemplate.setText(_mTemplateTextChoice)
        _plumeTemplate.setFixedSize(QSize((_mLenTemplateTextChoice * 10) + 20, 18))
        return

    #==========================
    # == Gestion des Icons Flags dans le menu des templates
    def majQmenuExportIconFlag(self) :
        mListExtensionFormat = self.metagraph.available_formats
        self.mListExtensionFormat = mListExtensionFormat
        self._mObjetQMenuExport.clear()
        self._mObjetQMenuExport.setStyleSheet("QMenu { font-family:" + self.policeQGroupBox  +"; width: " + str((int(len(max(mListExtensionFormat))) * 10) + 70) + "px;}")
        #------------
        for elemQMenuItem in mListExtensionFormat :
            _mObjetQMenuItem = QAction(elemQMenuItem, self._mObjetQMenuExport)
            _mObjetQMenuItem.setText(elemQMenuItem)
            _mObjetQMenuItem.setObjectName(str(elemQMenuItem))
            mTextToolTip = QtWidgets.QApplication.translate("plume_ui", "Export of the metadata sheet in the format ") + str(elemQMenuItem.upper())  
            _mObjetQMenuItem.setToolTip(mTextToolTip)
            self._mObjetQMenuExport.addAction(_mObjetQMenuItem)   
            #- Actions
            _mObjetQMenuItem.triggered.connect(lambda : self.clickButtonsExportActions())
        #-
        self.plumeExport.setPopupMode(self.plumeExport.MenuButtonPopup)
        self.plumeExport.setMenu(self._mObjetQMenuExport)
        return

    #==========================
    def createToolBar(self, _iconSourcesRead, _iconSourcesSave, _iconSourcesEmpty, _iconSourcesExport, _iconSourcesImport, _iconSourcesCopy, _iconSourcesPaste, _iconSourcesTemplate, _iconSourcesTranslation, _iconSourcesParam, _iconSourcesInterrogation, _iconSourcesHelp, _iconSourcesAbout, _iconSourcesVerrou ):
        #Menu Dialog  
        self.mMenuBarDialog = QMenuBar(self) 
        try : 
           if hasattr(self, "monDock") :
              self.mMenuBarDialog.setGeometry(QtCore.QRect(0, 0, self.monDock.width() - 150, 40))
           else:    
              self.mMenuBarDialog.setGeometry(QtCore.QRect(0, 0, self.Dialog.width() - 30, 40))
        except :
              pass 
              self.mMenuBarDialog.setGeometry(QtCore.QRect(0, 0, 500, 20))
        _mColorFirstPlan, _mColorSecondPlan = "transparent", "#cac5b1"     #Brun            

        #====================
        # ** First line **
        #====================
        #--
        abs, ord, larg, haut = 10, 0, 18, 18
        deltaIcone = 6 
        mText = QtWidgets.QApplication.translate("plume_ui", "Edition") 
        self.plumeEdit = QtWidgets.QPushButton(self.mMenuBarDialog)
        if self.toolBarDialog == "picture" : self.plumeEdit.setStyleSheet("QPushButton { border: 0px solid black;}")
        self.plumeEdit.setIcon(QIcon(_iconSourcesRead))
        self.plumeEdit.setObjectName("Edition")
        self.mTextToolTipRead = QtWidgets.QApplication.translate("plume_ui", "Edit") 
        self.mTextToolTipEdit = QtWidgets.QApplication.translate("plume_ui", "Read") 
        self.plumeEdit.setToolTip(self.mTextToolTipEdit)
        self.plumeEdit.setGeometry(QtCore.QRect(abs, ord, larg, haut))
        self.plumeEdit.clicked.connect(self.clickButtonsActions)
        #--
        abs, ord, larg, haut = (abs + larg + deltaIcone), ord, 18, 18
        mText = QtWidgets.QApplication.translate("plume_ui", "Save") 
        self.plumeSave = QtWidgets.QPushButton(self.mMenuBarDialog)
        if self.toolBarDialog == "picture" : self.plumeSave.setStyleSheet("QPushButton { border: 0px solid black;}" "background-color: "  + _mColorFirstPlan  + ";}" "QPushButton::pressed { border: 0px solid black; background-color: " + _mColorSecondPlan + ";}")  
        self.plumeSave.setIcon(QIcon(_iconSourcesSave))
        self.plumeSave.setObjectName("Save")
        self.plumeSave.setToolTip(mText)
        self.plumeSave.setGeometry(QtCore.QRect(abs, ord, larg, haut))
        self.plumeSave.clicked.connect(self.clickButtonsActions)
        #--                                        
        abs, ord, larg, haut = (abs + larg + deltaIcone), ord, 18, 18
        mText = QtWidgets.QApplication.translate("plume_ui", "Translation") 
        self.plumeTranslation = QtWidgets.QPushButton(self.mMenuBarDialog)
        if self.toolBarDialog == "picture" : self.plumeTranslation.setStyleSheet("QPushButton { border: 0px solid black;}")  
        self.plumeTranslation.setIcon(QIcon(_iconSourcesTranslation))
        self.plumeTranslation.setObjectName("Traduction")
        self.mTextToolTipNon = QtWidgets.QApplication.translate("plume_ui", "Enable translation functions.") 
        self.mTextToolTipOui = QtWidgets.QApplication.translate("plume_ui", "Disable translation functions.")
        self.plumeTranslation.setToolTip(self.mTextToolTipNon)
        self.plumeTranslation.setGeometry(QtCore.QRect(abs, ord, larg, haut))
        self.plumeTranslation.clicked.connect(self.clickButtonsActions)
        #====================
        #--QToolButton LANGUAGE                                               
        abs, ord, larg, haut = (abs + larg + deltaIcone), ord, 40, 18
        _editStyle = self.editStyle             #style saisie
        self.plumeChoiceLang = QtWidgets.QToolButton(self.mMenuBarDialog)
        self.plumeChoiceLang.setObjectName("plumeChoiceLang")
        self.plumeChoiceLang.setText(self.language)
        self.mTextToolTip = QtWidgets.QApplication.translate("plume_ui", "Change the main metadata language.") 
        self.plumeChoiceLang.setToolTip(self.mTextToolTip)
        self.plumeChoiceLang.setGeometry(QtCore.QRect(abs, ord, larg, haut))
        if self.toolBarDialog == "picture" : self.plumeChoiceLang.setStyleSheet("QToolButton { border: 0px solid black;}")  
        #MenuQToolButton                        
        _mObjetQMenu = QMenu()
        _mObjetQMenu.setStyleSheet("QMenu {  font-family:" + self.policeQGroupBox  +"; width:50px; border-style:" + _editStyle  + "; border-width: 0px;}")
        #------------
        for elemQMenuItem in self.langList :
            _mObjetQMenuItem = QAction(elemQMenuItem, _mObjetQMenu)
            _mObjetQMenuItem.setText(elemQMenuItem)
            _mObjetQMenuItem.setObjectName(str(elemQMenuItem))
            _mObjetQMenu.addAction(_mObjetQMenuItem)
            #- Actions
            _mObjetQMenuItem.triggered.connect(self.clickButtonsChoiceLanguages)
       
        self.plumeChoiceLang.setPopupMode(self.plumeChoiceLang.MenuButtonPopup)
        self.plumeChoiceLang.setMenu(_mObjetQMenu)
        
        self.plumeChoiceLang.setStyleSheet("QToolButton { font-family:" + self.policeQGroupBox  +"; width:20px; border-style:" + _editStyle  + "; border-width: 0px;}")
        #--QToolButton LANGUAGE                                               
        #====================
        #====================
        #--QToolButton TEMPLATE                                               
        abs, ord, larg, haut = (abs + larg + deltaIcone), ord, self.lenButtonTemplate if hasattr(self, "lenButtonTemplate") else 100, 18
        mText = QtWidgets.QApplication.translate("plume_ui", "Template") 
        self.plumeTemplate = QtWidgets.QToolButton(self.mMenuBarDialog)
        self.plumeTemplate.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.plumeTemplate.setIcon(QIcon(_iconSourcesTemplate))
        self.plumeTemplate.setObjectName("Template")
        self.plumeTemplate.setGeometry(QtCore.QRect(abs, ord, larg, haut))
        self.plumeTemplate.setAutoRaise(True)
        mTextToolTip = QtWidgets.QApplication.translate("plume_ui", "METADATA extension not installed.")   
        mTextToolTip = QtWidgets.QApplication.translate("plume_ui", "Choose a form template.")    
        self.plumeTemplate.setToolTip(mTextToolTip)
        #MenuQToolButton                        
        _mObjetQMenu = QMenu()
        self._mObjetQMenu = _mObjetQMenu
        #--QToolButton TEMPLATE                                               
        #====================

        #====================
        # ** Second line **
        #====================
        #--
        abs, ord, larg, haut = 10, 20, 18, 18
        deltaIcone = 6 
        #--
        mText = QtWidgets.QApplication.translate("plume_ui", "Copy") 
        self.plumeCopy = QtWidgets.QPushButton(self.mMenuBarDialog)
        if self.toolBarDialog == "picture" : self.plumeCopy.setStyleSheet("QPushButton { border: 0px solid black;}" "background-color: "  + _mColorFirstPlan  + ";}" "QPushButton::pressed { border: 0px solid black; background-color: " + _mColorSecondPlan + ";}")  
        self.plumeCopy.setIcon(QIcon(_iconSourcesCopy))
        self.plumeCopy.setObjectName("Copy")
        mTextToolTip = QtWidgets.QApplication.translate("plume_ui", "Copy the metadata card.") 
        self.plumeCopy.setToolTip(mTextToolTip)
        self.plumeCopy.setGeometry(QtCore.QRect(abs, ord, larg, haut))
        self.plumeCopy.clicked.connect(self.clickButtonsActions)
        #Création pour la copy à None
        self.copyMetagraph = None
        #--
        abs, ord, larg, haut = (abs + larg + deltaIcone), ord, 18, 18
        mText = QtWidgets.QApplication.translate("plume_main", "Paste") 
        self.plumePaste = QtWidgets.QPushButton(self.mMenuBarDialog)
        if self.toolBarDialog == "picture" : self.plumePaste.setStyleSheet("QPushButton { border: 0px solid black;}" "background-color: "  + _mColorFirstPlan  + ";}" "QPushButton::pressed { border: 0px solid black; background-color: " + _mColorSecondPlan + ";}")  
        self.plumePaste.setIcon(QIcon(_iconSourcesPaste))
        self.plumePaste.setObjectName("Paste")
        mTextToolTip = QtWidgets.QApplication.translate("plume_ui", "Paste the saved metadata card.") 
        self.plumePaste.setToolTip(mTextToolTip)
        self.plumePaste.setGeometry(QtCore.QRect(abs, ord, larg, haut))
        self.plumePaste.clicked.connect(self.clickButtonsActions)
        #--
        abs, ord, larg, haut = (abs + larg + deltaIcone), ord, 18, 18
        mText = QtWidgets.QApplication.translate("plume_ui", "Empty") 
        self.plumeEmpty = QtWidgets.QPushButton(self.mMenuBarDialog)
        if self.toolBarDialog == "picture" : self.plumeEmpty.setStyleSheet("QPushButton { border: 0px solid black;}" "background-color: "  + _mColorFirstPlan  + ";}" "QPushButton::pressed { border: 0px solid black; background-color: " + _mColorSecondPlan + ";}")  
        self.plumeEmpty.setIcon(QIcon(_iconSourcesEmpty))
        self.plumeEmpty.setObjectName("Empty")
        mTextToolTip = QtWidgets.QApplication.translate("plume_ui", "Empty the metadata card.")
        self.plumeEmpty.setToolTip(mTextToolTip)
        self.plumeEmpty.setGeometry(QtCore.QRect(abs, ord, larg, haut))
        self.plumeEmpty.clicked.connect(self.clickButtonsActions)
        #--                                        
        #====================
        #--QToolButton IMPORT                                               
        abs, ord, larg, haut = (abs + larg + deltaIcone), ord, 42, 18
        mText = QtWidgets.QApplication.translate("plume_main", "Import") 
        self.plumeImport = QtWidgets.QToolButton(self.mMenuBarDialog)
        if self.toolBarDialog == "picture" : self.plumeImport.setStyleSheet("QToolButton { border: 0px solid black;}")  
        self.plumeImport.setIcon(QIcon(_iconSourcesImport))
        self.plumeImport.setObjectName("Import")
        self.plumeImport.setGeometry(QtCore.QRect(abs, ord, larg, haut))
        mTextToolTip = QtWidgets.QApplication.translate("plume_ui", "Import metadata.") 
        self.plumeImport.setToolTip(mTextToolTip)
        #MenuQToolButton                        
        _mObjetQMenu = QMenu()
        _mObjetQMenu.setToolTipsVisible(True)
        _editStyle = self.editStyle             #style saisie
        _mObjetQMenu.setStyleSheet("QMenu {  font-family:" + self.policeQGroupBox  +"; width:270px; border-style:" + _editStyle  + "; border-width: 0px;}")
        #------------
        #-- Importer les métadonnées depuis un fichier DACT
        mText = QtWidgets.QApplication.translate("plume_ui", "Import from file (DCAT)")
        self.plumeImportFile = QAction("plumeImportFile",self.plumeImport)
        self.plumeImportFile.setText(mText)
        self.plumeImportFile.setObjectName("plumeImportFile")
        self.plumeImportFile.setToolTip(mText)
        self.plumeImportFile.triggered.connect(self.clickButtonsActions)
        mTextToolTip = QtWidgets.QApplication.translate("plume_ui", "Import the contents of a metadata file using RDF syntax with DCAT vocabulary.") + "\n" +  QtWidgets.QApplication.translate("plume_ui", "The result will be all the more conclusive if the metadata conforms to the DCAT-AP v2 or GeoDCAT-AP v2 profiles.") 
        self.plumeImportFile.setToolTip(mTextToolTip)
        _mObjetQMenu.addAction(self.plumeImportFile)
        #-- Importer les métadonnées depuis un fichier DACT
        #-- Importer les métadonnées depuis un fichier INSPIRE
        mText = QtWidgets.QApplication.translate("plume_ui", "Import from file (INSPIRE)")
        self.plumeImportFileInspire = QAction("plumeImportFileInspire",self.plumeImport)
        self.plumeImportFileInspire.setText(mText)
        self.plumeImportFileInspire.setObjectName("plumeImportFileInspire")
        self.plumeImportFileInspire.setToolTip(mText)
        self.plumeImportFileInspire.triggered.connect(self.clickButtonsActions)
        mTextToolTip = QtWidgets.QApplication.translate("plume_ui", "Import the metadata contained in an XML file that complies with INSPIRE specifications.") 
        self.plumeImportFileInspire.setToolTip(mTextToolTip)
        _mObjetQMenu.addAction(self.plumeImportFileInspire)
        #-- Importer les métadonnées depuis un fichier INSPIRE
        #-- Importer les métadonnées depuis un service CSW
        mText = QtWidgets.QApplication.translate("plume_ui", "Import from a CSW service (INSPIRE)") 
        self.plumeImportCsw = QAction("plumeImportCSW",self.plumeImport)
        self.plumeImportCsw.setText(mText)
        self.plumeImportCsw.setObjectName("plumeImportCSW")
        self.plumeImportCsw.setToolTip(mText)
        self.plumeImportCsw.triggered.connect(self.clickImportCSW)
        mTextToolTip = QtWidgets.QApplication.translate("plume_ui", "Import metadata that conforms to INSPIRE specifications by querying a CSW service.") 
        self.plumeImportCsw.setToolTip(mTextToolTip)
        _mObjetQMenu.addAction(self.plumeImportCsw)
        #-- Importer les métadonnées depuis un service CSW
        #------------
        self.plumeImport.setPopupMode(self.plumeImport.MenuButtonPopup)
        self.plumeImport.setMenu(_mObjetQMenu)
        #--QToolButton IMPORT                                               
        #====================
        #====================
        #--QToolButton EXPORT                                               
        abs, ord, larg, haut = (abs + larg + deltaIcone), ord, 42, 18
        mText = QtWidgets.QApplication.translate("plume_ui", "Export") 
        self.plumeExport = QtWidgets.QToolButton(self.mMenuBarDialog)
        if self.toolBarDialog == "picture" : self.plumeExport.setStyleSheet("QToolButton { border: 0px solid black;}")  
        self.plumeExport.setIcon(QIcon(_iconSourcesExport))
        self.plumeExport.setObjectName("Export")
        self.plumeExport.setGeometry(QtCore.QRect(abs, ord, larg, haut))
        mTextToolTip = QtWidgets.QApplication.translate("plume_ui", "Export metadata to a file.")
        self.plumeExport.setToolTip(mTextToolTip)
        #MenuQToolButton                        
        _mObjetQMenu = QMenu()
        _mObjetQMenu.setToolTipsVisible(True)
        self._mObjetQMenuExport = _mObjetQMenu
        #--QToolButton EXPORT                                               
        #====================
        #--
        abs, ord, larg, haut = (abs + larg + deltaIcone + 10), ord, 18, 18
        mText = QtWidgets.QApplication.translate("plume_ui", "Customization of the IHM") 
        self.paramColor = QtWidgets.QPushButton(self.mMenuBarDialog)
        if self.toolBarDialog == "picture" : self.paramColor.setStyleSheet("QPushButton { border: 0px solid black;}" "background-color: "  + _mColorFirstPlan  + ";}" "QPushButton::pressed { border: 0px solid black; background-color: " + _mColorSecondPlan + ";}")  
        self.paramColor.setIcon(QIcon(_iconSourcesParam))
        self.paramColor.setObjectName("Customization of the IHM")
        self.paramColor.setToolTip(mText)
        self.paramColor.setGeometry(QtCore.QRect(abs, ord, larg, haut))
        self.paramColor.clicked.connect(self.clickColorDialog)
        #====================
        #--QToolButton POINT ?                                               
        abs, ord, larg, haut = (abs + larg + deltaIcone), ord, 40, 18
        self.plumeInterrogation = QtWidgets.QToolButton(self.mMenuBarDialog)
        self.plumeInterrogation.setObjectName("plumeInterrogation")
        self.mTextToolTip = QtWidgets.QApplication.translate("plume_ui", "Help / About") 
        self.plumeInterrogation.setIcon(QIcon(_iconSourcesInterrogation))
        self.plumeInterrogation.setToolTip(self.mTextToolTip)
        self.plumeInterrogation.setGeometry(QtCore.QRect(abs, ord, larg, haut))
        if self.toolBarDialog == "picture" : self.plumeInterrogation.setStyleSheet("QToolButton { border: 0px solid black;}")  
        #MenuQToolButton                        
        _mObjetQMenu = QMenu()
        _mObjetQMenu.setToolTipsVisible(True)
        _editStyle = self.editStyle             #style saisie
        _mObjetQMenu.setStyleSheet("QMenu {  font-family:" + self.policeQGroupBox  +"; width:120px; border-style:" + _editStyle  + "; border-width: 0px;}")
        #------------
        #-- Aide
        mText = QtWidgets.QApplication.translate("plume_ui", "Help") 
        self.plumeHelp = QAction("Help",self.plumeInterrogation)
        self.plumeHelp.setText(mText)
        #self.plumeHelp.setIcon(QIcon(_iconSourcesHelp))
        self.plumeHelp.setObjectName("Help")
        self.plumeHelp.setToolTip(mText)
        self.plumeHelp.triggered.connect(self.myHelpAM)
        _mObjetQMenu.addAction(self.plumeHelp)
        #-- Aide
        _mObjetQMenu.addSeparator()
        #-- About
        mText = QtWidgets.QApplication.translate("plume_ui", "About") 
        self.plumeAbout = QAction("About",self.plumeInterrogation)
        self.plumeAbout.setText(mText)
        #self.plumeAbout.setIcon(QIcon(_iconSourcesAbout))
        self.plumeAbout.setObjectName("About")
        self.plumeAbout.setToolTip(mText)
        self.plumeAbout.triggered.connect(self.clickAbout)
        _mObjetQMenu.addAction(self.plumeAbout)
        #-- About
        #------------
        self.plumeInterrogation.setPopupMode(self.plumeInterrogation.MenuButtonPopup)
        self.plumeInterrogation.setMenu(_mObjetQMenu)
        #--QToolButton POINT ?                                               
        #-- Verrouillage
        abs, ord, larg, haut = self.mMenuBarDialog.width() - 20, ord, 18, 18
        mText = QtWidgets.QApplication.translate("plume_ui", "Lockdown") 
        self.plumeVerrou = QtWidgets.QPushButton(self.mMenuBarDialog)
        if self.toolBarDialog == "picture" : self.plumeVerrou.setStyleSheet("QPushButton { border: 0px solid black;}")
        self.plumeVerrou.setIcon(QIcon(_iconSourcesVerrou))
        self.plumeVerrou.setObjectName("Verrouillage")
        self.mTextToolTipVerrouRead = QtWidgets.QApplication.translate("plume_ui", 'Lock the display on the current metadata card.') 
        self.mTextToolTipVerrouEdit = QtWidgets.QApplication.translate("plume_ui", 'Unlock the display.')                       
        self.plumeVerrou.setToolTip(self.mTextToolTipVerrouEdit)
        self.plumeVerrou.setGeometry(QtCore.QRect(abs, ord, larg, haut))
        self.plumeVerrou.clicked.connect(self.clickButtonsActions)
        #-- Verrouillage
        #====================
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
        dlg.setWindowTitle(mDialog.messWindowTitle)
        mDialog.iface.addDockWidget(Qt.RightDockWidgetArea, dlg)
        dlg.setFloating(True if mDialog.ihm in ["dockTrue"] else False)
        dlg.setWidget(mDialog)
        dlg.resize(420, 300)
        mDialog.dlg = dlg

    #==========================
    def closeEvent(self, event):

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
            
                 
