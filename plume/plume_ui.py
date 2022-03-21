# (c) Didier  LECLERC 2020 CMSIG MTE-MCTRCT/SG/SNUM/UNI/DRC Site de Rouen
# créé sept 2021
#        **************************************************************************
#        copyright            : (C) 2021 by DL
#        **************************************************************************

from PyQt5 import QtCore, QtGui, QtWidgets, QtQuick 

from PyQt5.QtCore import *
from PyQt5.QtWidgets import (QAction, QMenu , QMenuBar, QApplication, QMessageBox, QFileDialog, QPlainTextEdit, QDialog, QStyle, 
                             QDockWidget, QTreeView, QGridLayout, QTabWidget, QWidget, QDesktopWidget, QSizePolicy, 
                             QTreeWidget, QTreeWidgetItem, QTreeWidgetItemIterator, QStyleFactory, QStyle)

from PyQt5.QtGui import QIcon, QStandardItem, QStandardItemModel

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

import psycopg2
from plume.pg import queries
from plume.rdf.metagraph import copy_metagraph


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
        self.urlCswDefaut     = self.mDic_LH["urlCswDefaut"]       #l'Url par defaut
        self.urlCswIdDefaut   = self.mDic_LH["urlCswIdDefaut"]     #l'Id de l'Url par defaut
        self.urlCsw           = self.mDic_LH["urlCsw"]             #Liste des urlcsw sauvegardées
        # for geometry
        self.geomColor       = self.mDic_LH["geomColor"]       
        self.geomEpaisseur   = self.mDic_LH["geomEpaisseur"]       
        self.geomPoint       = self.mDic_LH["geomPoint"]       
        self.geomZoom        = True if self.mDic_LH["geomZoom"] == "true" else False
        #-
        mDicType         = ["ICON_X", "ICON_CROSS", "ICON_BOX", "ICON_CIRCLE", "ICON_DOUBLE_TRIANGLE"]
        mDicTypeObj      = [QgsVertexMarker.ICON_X, QgsVertexMarker.ICON_CROSS, QgsVertexMarker.ICON_BOX, QgsVertexMarker.ICON_CIRCLE, QgsVertexMarker.ICON_DOUBLE_TRIANGLE]
        self.mDicTypeObj = dict(zip(mDicType, mDicTypeObj)) # For bibli_plume_tools_map
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
        # For menu contex QGroupBox
        self._iconSourcesCopy, self._iconSourcesPaste = _iconSourcesCopy, _iconSourcesPaste
        _iconSourcesPaste         = _pathIcons + "/paste_all.svg"
        
        self.listIconToolBar = [ _iconSourcesRead, _iconSourcesSave, _iconSourcesEmpty, _iconSourcesExport, _iconSourcesImport, _iconSourcesCopy, _iconSourcesPaste, _iconSourcesTemplate, _iconSourcesTranslation, _iconSourcesParam, _iconSourcesInterrogation, _iconSourcesHelp, _iconSourcesAbout ]
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
           old_metagraph = self.metagraph
           self.metagraph = copy_metagraph(None, old_metagraph)
        #**********************
        elif mItem == "Copy" :
           self.copyMetagraph = self.metagraph
           if self.copyMetagraph !=  None :
              mTextToolTip = QtWidgets.QApplication.translate("plume_main", "Coller la fiche de métadonnées de <b>") + str(self.schema) + "." + str(self.table) + "</b>"
           else :    
              mTextToolTip = QtWidgets.QApplication.translate("plume_main", "Coller la fiche de métadonnées mémorisée.") 
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
        elif mItem == "Traduction" :
           self.translation = (False if self.translation else True) 
        #**********************
        #*** commun
        if mItem in ["Edition", "Save", "Empty", "plumeImportFile", "Paste", "Traduction"] :
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
        mItemExport = self.mMenuBarDialog.sender().objectName()
        exportObjetMetagraph(self, self.schema, self.table, mItemExport, self.mListExtensionFormat)
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
              #self.template, self.templateTabs = None, None
              self.template = None
           else :   
              # Choix du modèle
              bibli_plume.generationTemplateAndTabs(self, mItemTemplates)
           # Génération à la volée
           self.generationALaVolee(bibli_plume.returnObjetsMeta(self))

           # MAJ ICON FLAGS
           self.majQmenuModeleIconFlag(mItemTemplates)
           # MAJ ICON FLAGS
           
        return
    # == Gestion des actions du bouton TEMPLATE de la barre de menu
    #==========================

    #==========================
    # == Gestion des actions du bouton Changement des langues
    def  clickButtonsChoiceLanguages(self):
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
                 self.data       = bibli_plume.returnObjetData(self)
                 self.mode = "read"
                 self.loadLayer = self.ifLayerLoad(self.layer)
                 #-
                 self.displayToolBar(*self.listIconToolBar)
                 #-
                 if self.instalMetadata :
                    #-
                    tpl_labelDefaut                     = bibli_plume.returnObjetTpl_label(self)
                    if tpl_labelDefaut :
                       #self.template, self.templateTabs = bibli_plume.generationTemplateAndTabs(self, tpl_labelDefaut)
                       self.template = bibli_plume.generationTemplateAndTabs(self, tpl_labelDefaut)
                    else :
                       #self.template, self.templateTabs = None, None   
                       self.template = None
                    #-
                    self.createQmenuModele(self._mObjetQMenu, self.templateLabels)
                    self.majQmenuModeleIconFlag(tpl_labelDefaut)
                 else :
                    #self.template, self.templateTabs = None, None   
                    self.template = None
                 #-
                 self.layerQgisBrowserOther = "QGIS"
                 self.generationALaVolee(bibli_plume.returnObjetsMeta(self))
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
        if isinstance(item, QgsLayerItem) :
           if self.ifVectorPostgres(item.uri()) :
              self.layer = QgsVectorLayer(item.uri(), item.name(), 'postgres')
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
                 self.data       = bibli_plume.returnObjetData(self)
                 self.mode = "read"
                 self.loadLayer = self.ifLayerLoad(self.layer)
                 #-
                 self.displayToolBar(*self.listIconToolBar)
                 #-
                 if self.instalMetadata :
                    #-
                    tpl_labelDefaut                     = bibli_plume.returnObjetTpl_label(self)
                    if tpl_labelDefaut :
                       self.template = bibli_plume.generationTemplateAndTabs(self, tpl_labelDefaut)
                    else :
                       self.template = None
                    #-
                    self.createQmenuModele(self._mObjetQMenu, self.templateLabels)
                    self.majQmenuModeleIconFlag(tpl_labelDefaut)
                 else :
                    self.template = None
                 #-
                 self.layerQgisBrowserOther = "BROWSER"
                 self.generationALaVolee(bibli_plume.returnObjetsMeta(self))
        return

    #---------------------------
    def getAllFromUri(self):
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
    def ifVectorPostgres(self, itemUri) :
        mStoragePostgres = True
        listSousChaine = ["host=", "dbname=", "user="]
        for elem in listSousChaine :
            if itemUri.find(elem) == -1 :
               mStoragePostgres = False
               break
        return mStoragePostgres     

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
    def if_postgis_exists(self) :
        mKeySql = (queries.query_exists_extension(), ('postgis',))
        r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self.mConnectEnCours, mKeySql, optionRetour = "fetchone")
        return r

    #==========================
    # == Gestion des actions de boutons de la barre de menu
    def displayToolBar(self, _iconSourcesRead, _iconSourcesEmpty, _iconSourcesExport, _iconSourcesImport, _iconSourcesSave, _iconSourcesCopy, _iconSourcesPaste, _iconSourcesTemplate, _iconSourcesTranslation, _iconSourcesParam, _iconSourcesInterrogation, _iconSourcesHelp, _iconSourcesAbout):
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

        #====================
        #====================
        #--QToolButton TEMPLATE                                               
        if hasattr(self, 'mConnectEnCours') :
           if self.toolBarDialog == "picture" : self.plumeTemplate.setStyleSheet("QToolButton { border: 0px solid black;}")  
           self.plumeTemplate.setIcon(QIcon(_iconSourcesTemplate))
           self.plumeTemplate.setObjectName("Template")
           #Lecture existence Extension METADATA
           mKeySql = (queries.query_exists_extension(), ('plume_pg',))
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
              mTextToolTip = QtWidgets.QApplication.translate("plume_main", "L'extension PostgreSQL plume_pg n'est pas installée.") 
           self.plumeTemplate.setToolTip(mTextToolTip)
        #--QToolButton TEMPLATE                                               
        #====================
        #====================

        if hasattr(self, 'mConnectEnCours') :
           #--QToolButton EXPORT                                               
           self.majQmenuExportIconFlag()
           #-
           mKeySql = (queries.query_is_relation_owner(), (self.schema, self.table))
           r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self.mConnectEnCours, mKeySql, optionRetour = "fetchone")
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

        #-ToolTip
        #-
        if self.copyMetagraph !=  None :
           mTextToolTip = self.copyMetagraphTooltip
        else :    
           mTextToolTip = QtWidgets.QApplication.translate("plume_main", "Coller la fiche de métadonnées mémorisée.") 
        self.plumePaste.setToolTip(mTextToolTip)
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
        mListExtensionFormat = self.metagraph.available_formats
        self.mListExtensionFormat = mListExtensionFormat
        self._mObjetQMenuExport.clear()
        self._mObjetQMenuExport.setStyleSheet("QMenu { font-family:" + self.policeQGroupBox  +"; width: " + str((int(len(max(mListExtensionFormat))) * 10) + 70) + "px;}")
        #------------
        for elemQMenuItem in mListExtensionFormat :
            _mObjetQMenuItem = QAction(elemQMenuItem, self._mObjetQMenuExport)
            _mObjetQMenuItem.setText(elemQMenuItem)
            _mObjetQMenuItem.setObjectName(str(elemQMenuItem))
            mTextToolTip = "Export de la fiche de métadonnées au format " + str(elemQMenuItem.upper())
            _mObjetQMenuItem.setToolTip(mTextToolTip)
            self._mObjetQMenuExport.addAction(_mObjetQMenuItem)   
            #- Actions
            _mObjetQMenuItem.triggered.connect(lambda : self.clickButtonsExportActions())
        #-
        self.plumeExport.setPopupMode(self.plumeExport.MenuButtonPopup)
        self.plumeExport.setMenu(self._mObjetQMenuExport)
        return
    #==========================
    def createToolBar(self, _iconSourcesRead, _iconSourcesSave, _iconSourcesEmpty, _iconSourcesExport, _iconSourcesImport, _iconSourcesCopy, _iconSourcesPaste, _iconSourcesTemplate, _iconSourcesTranslation, _iconSourcesParam, _iconSourcesInterrogation, _iconSourcesHelp, _iconSourcesAbout ):
        #Menu Dialog                                                                                                                                                                
        self.mMenuBarDialog = QMenuBar(self)
        self.mMenuBarDialog.setGeometry(QtCore.QRect(0, 0, 420, 20))
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
        _mObjetQMenu.setToolTipsVisible(True)
        self._mObjetQMenuExport = _mObjetQMenu
        #--QToolButton EXPORT                                               
        #====================
        #--
        #====================
        #--QToolButton IMPORT                                               
        mText = QtWidgets.QApplication.translate("plume_main", "Import") 
        self.plumeImport = QtWidgets.QToolButton(self.mMenuBarDialog)
        if self.toolBarDialog == "picture" : self.plumeImport.setStyleSheet("QToolButton { border: 0px solid black;}")  
        self.plumeImport.setIcon(QIcon(_iconSourcesImport))
        self.plumeImport.setObjectName("Import")
        self.plumeImport.setGeometry(QtCore.QRect(125,0,42,18))
        mTextToolTip = QtWidgets.QApplication.translate("plume_main", "Importer les métadonnées depuis un fichier ou depuis un service CSW.") 
        self.plumeImport.setToolTip(mTextToolTip)
        #MenuQToolButton                        
        _mObjetQMenu = QMenu()
        _mObjetQMenu.setToolTipsVisible(True)
        _editStyle = self.editStyle             #style saisie
        _mObjetQMenu.setStyleSheet("QMenu {  font-family:" + self.policeQGroupBox  +"; width:220px; border-style:" + _editStyle  + "; border-width: 0px;}")
        #------------
        #-- Importer les métadonnées depuis un fichier
        mText = QtWidgets.QApplication.translate("plume_main", "Importer depuis un fichier") 
        self.plumeImportFile = QAction("plumeImportFile",self.plumeImport)
        self.plumeImportFile.setText(mText)
        self.plumeImportFile.setObjectName("plumeImportFile")
        self.plumeImportFile.setToolTip(mText)
        self.plumeImportFile.triggered.connect(self.clickButtonsActions)
        _mObjetQMenu.addAction(self.plumeImportFile)
        #-- Importer les métadonnées depuis un fichier
        #-- Importer les métadonnées depuis un service CSW
        mText = QtWidgets.QApplication.translate("plume_main", "Importer depuis un service CSW") 
        self.plumeImportCsw = QAction("plumeImportCSW",self.plumeImport)
        self.plumeImportCsw.setText(mText)
        self.plumeImportCsw.setObjectName("plumeImportCSW")
        self.plumeImportCsw.setToolTip(mText)
        self.plumeImportCsw.triggered.connect(self.clickImportCSW)
        _mObjetQMenu.addAction(self.plumeImportCsw)
        #-- Importer les métadonnées depuis un service CSW
        #------------
        self.plumeImport.setPopupMode(self.plumeImport.MenuButtonPopup)
        self.plumeImport.setMenu(_mObjetQMenu)
        #--QToolButton IMPORT                                               
        #====================
        #--
        mText = QtWidgets.QApplication.translate("plume_main", "Copy") 
        self.plumeCopy = QtWidgets.QPushButton(self.mMenuBarDialog)
        if self.toolBarDialog == "picture" : self.plumeCopy.setStyleSheet("QPushButton { border: 0px solid black;}" "background-color: "  + _mColorFirstPlan  + ";}" "QPushButton::pressed { border: 0px solid black; background-color: " + _mColorSecondPlan + ";}")  
        self.plumeCopy.setIcon(QIcon(_iconSourcesCopy))
        self.plumeCopy.setObjectName("Copy")
        mTextToolTip = QtWidgets.QApplication.translate("plume_main", "Copier la fiche de métadonnées.") 
        self.plumeCopy.setToolTip(mTextToolTip)
        self.plumeCopy.setGeometry(QtCore.QRect(175,0,18,18))
        self.plumeCopy.clicked.connect(self.clickButtonsActions)
        #Création pour la copy à None
        self.copyMetagraph = None
        #--
        mText = QtWidgets.QApplication.translate("plume_main", "Paste") 
        self.plumePaste = QtWidgets.QPushButton(self.mMenuBarDialog)
        if self.toolBarDialog == "picture" : self.plumePaste.setStyleSheet("QPushButton { border: 0px solid black;}" "background-color: "  + _mColorFirstPlan  + ";}" "QPushButton::pressed { border: 0px solid black; background-color: " + _mColorSecondPlan + ";}")  
        self.plumePaste.setIcon(QIcon(_iconSourcesPaste))
        self.plumePaste.setObjectName("Paste")
        mTextToolTip = QtWidgets.QApplication.translate("plume_main", "Coller la fiche de métadonnées mémorisée.") 
        self.plumePaste.setToolTip(mTextToolTip)
        self.plumePaste.setGeometry(QtCore.QRect(205,0,18,18))
        self.plumePaste.clicked.connect(self.clickButtonsActions)
        #====================
        #--QToolButton TEMPLATE                                               
        mText = QtWidgets.QApplication.translate("plume_main", "Template") 
        self.plumeTemplate = QtWidgets.QToolButton(self.mMenuBarDialog)
        if self.toolBarDialog == "picture" : self.plumeTemplate.setStyleSheet("QToolButton { border: 0px solid black;}")  
        self.plumeTemplate.setIcon(QIcon(_iconSourcesTemplate))
        self.plumeTemplate.setObjectName("Template")
        self.plumeTemplate.setGeometry(QtCore.QRect(230,0,42,18))
        mTextToolTip = QtWidgets.QApplication.translate("plume_main", "Extension METADATA non installée.") 
        mTextToolTip = QtWidgets.QApplication.translate("plume_main", "Choisir un modèle de formulaire.") 
        self.plumeTemplate.setToolTip(mTextToolTip)
        #MenuQToolButton                        
        _mObjetQMenu = QMenu()
        self._mObjetQMenu = _mObjetQMenu
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
        self.plumeTranslation.setGeometry(QtCore.QRect(280,0,18,18))
        self.plumeTranslation.clicked.connect(self.clickButtonsActions)
        #====================
        #--QToolButton LANGUAGE                                               
        self.plumeChoiceLang = QtWidgets.QToolButton(self.mMenuBarDialog)
        self.plumeChoiceLang.setObjectName("plumeChoiceLang")
        self.plumeChoiceLang.setText(self.language)
        self.mTextToolTip = QtWidgets.QApplication.translate("plume_main", "Modifier la langue principale des métadonnées.") 
        self.plumeChoiceLang.setToolTip(self.mTextToolTip)
        self.plumeChoiceLang.setGeometry(QtCore.QRect(300,0,40,18))
        if self.toolBarDialog == "picture" : self.plumeChoiceLang.setStyleSheet("QToolButton { border: 0px solid black;}")  
        #MenuQToolButton                        
        _mObjetQMenu = QMenu()
        _editStyle = self.editStyle             #style saisie
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
        #--QToolButton LANGUAGE                                               
        #====================
        mText = QtWidgets.QApplication.translate("plume_main", "Customization of the IHM") 
        self.paramColor = QtWidgets.QPushButton(self.mMenuBarDialog)
        if self.toolBarDialog == "picture" : self.paramColor.setStyleSheet("QPushButton { border: 0px solid black;}" "background-color: "  + _mColorFirstPlan  + ";}" "QPushButton::pressed { border: 0px solid black; background-color: " + _mColorSecondPlan + ";}")  
        self.paramColor.setIcon(QIcon(_iconSourcesParam))
        self.paramColor.setObjectName(mText)
        self.paramColor.setToolTip(mText)
        self.paramColor.setGeometry(QtCore.QRect(350,0,18,18))
        self.paramColor.clicked.connect(self.clickColorDialog)
        #====================
        #--QToolButton POINT ?                                               
        self.plumeInterrogation = QtWidgets.QToolButton(self.mMenuBarDialog)
        self.plumeInterrogation.setObjectName("plumeInterrogation")
        self.mTextToolTip = QtWidgets.QApplication.translate("plume_main", "Aide / À propos") 
        self.plumeInterrogation.setIcon(QIcon(_iconSourcesInterrogation))
        self.plumeInterrogation.setToolTip(self.mTextToolTip)
        self.plumeInterrogation.setGeometry(QtCore.QRect(370,0,40,18))
        if self.toolBarDialog == "picture" : self.plumeInterrogation.setStyleSheet("QToolButton { border: 0px solid black;}")  
        #MenuQToolButton                        
        _mObjetQMenu = QMenu()
        _mObjetQMenu.setToolTipsVisible(True)
        _editStyle = self.editStyle             #style saisie
        _mObjetQMenu.setStyleSheet("QMenu {  font-family:" + self.policeQGroupBox  +"; width:120px; border-style:" + _editStyle  + "; border-width: 0px;}")
        #------------
        #-- Aide
        mText = QtWidgets.QApplication.translate("plume_main", "Help") 
        self.plumeHelp = QAction("Help",self.plumeInterrogation)
        self.plumeHelp.setText(mText)
        #self.plumeHelp.setIcon(QIcon(_iconSourcesHelp))
        self.plumeHelp.setObjectName(mText)
        self.plumeHelp.setToolTip(mText)
        self.plumeHelp.triggered.connect(self.myHelpAM)
        _mObjetQMenu.addAction(self.plumeHelp)
        #-- Aide
        _mObjetQMenu.addSeparator()
        #-- About
        mText = QtWidgets.QApplication.translate("plume_main", "About") 
        self.plumeAbout = QAction("About",self.plumeInterrogation)
        self.plumeAbout.setText(mText)
        #self.plumeAbout.setIcon(QIcon(_iconSourcesAbout))
        self.plumeAbout.setObjectName(mText)
        self.plumeAbout.setToolTip(mText)
        self.plumeAbout.triggered.connect(self.clickAbout)
        _mObjetQMenu.addAction(self.plumeAbout)
        #-- About
        #------------
        self.plumeInterrogation.setPopupMode(self.plumeInterrogation.MenuButtonPopup)
        self.plumeInterrogation.setMenu(_mObjetQMenu)
        #--QToolButton POINT ?                                               
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
        dlg.setWindowTitle(QtWidgets.QApplication.translate("plume_ui", "PLUGIN METADONNEES (Metadata storage in PostGreSQL)", None) + "  (" + str(bibli_plume.returnVersion()) + ")")
        mDialog.iface.addDockWidget(Qt.RightDockWidgetArea, dlg)
        dlg.setFloating(True if mDialog.ihm in ["dockTrue"] else False)
        dlg.setWidget(mDialog)
        dlg.resize(420, 300)
        mDialog.dlg = dlg

    #==========================
    def event(self, event):
        event.accept()
        return

    #==========================
    def closeEvent(self, event):
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
            
                 