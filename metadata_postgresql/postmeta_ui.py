# (c) Didier  LECLERC 2020 CMSIG MTE-MCTRCT/SG/SNUM/UNI/DRC Site de Rouen
# créé sept 2021
#        **************************************************************************
#        copyright            : (C) 2020 by JD Lomenede for # self.proxy_model = self.navigateurTreeView.model() = self.model = iface.browserModel() = item = self.model.dataItem(self.proxy_model.mapToSource(index)) #
#        **************************************************************************
#        copyright            : (C) 2021 by DL
#        **************************************************************************

from PyQt5 import QtCore, QtGui, QtWidgets, QtQuick 
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QAction, QMenu , QMenuBar, QApplication, QMessageBox, QFileDialog, QPlainTextEdit, QDialog, QDockWidget, QTreeView, QGridLayout, QTabWidget, QWidget, QDesktopWidget, QSizePolicy
from PyQt5.QtGui import QIcon, QStandardItem, QStandardItemModel

from . import bibli_postmeta
from .bibli_postmeta import *
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

from .bibli_rdf.tests import rdf_utils_demo
from .bibli_rdf import rdf_utils
from .bibli_pg  import pg_queries
from .bibli_pg  import template_utils

class Ui_Dialog_postmeta(object):
    def __init__(self):
        self.iface = qgis.utils.iface                         
        self.firstOpen = True                                 
        self.firstOpenConnect = True
    
    def setupUi(self, Dialog):
        self.Dialog = Dialog
        Dialog.setObjectName("Dialog")
        mDic_LH = bibli_postmeta.returnAndSaveDialogParam(self, "Load")
        self.mDic_LH = mDic_LH
        self.lScreenDialog, self.hScreenDialog = int(self.mDic_LH["dialogLargeur"]), int(self.mDic_LH["dialogHauteur"])
        self.displayMessage  = False if self.mDic_LH["displayMessage"] == 'dialogTitle' else True #Qmessage box (dialogBox) ou barre de progression (dialogTitle)
        self.fileHelp        = self.mDic_LH["fileHelp"]      #Type Fichier Help
        self.fileHelpPdf     = self.mDic_LH["fileHelpPdf"]   #Fichier Help  PDF
        self.fileHelpHtml    = self.mDic_LH["fileHelpHtml"]  #Fichier Help  HTML
        self.durationBarInfo = int(self.mDic_LH["durationBarInfo"])  #durée d'affichage des messages d'information
        self.ihm             = self.mDic_LH["ihm"]  #window/dock
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
        _pathIcons = os.path.dirname(__file__) + "/icons/general"
        _iconSourcesEdit         = _pathIcons + "/edit.svg"
        _iconSourcesEmpty        = _pathIcons + "/empty.svg"
        _iconSourcesExport       = _pathIcons + "/export.svg"
        _iconSourcesImport       = _pathIcons + "/import.svg"
        _iconSourcesSave         = _pathIcons + "/Save.svg"
        _iconSourcesTemplate     = _pathIcons + "/template.svg"
        _iconSourcesTranslation  = _pathIcons + "/translation.svg"
        _iconSourcesHelp         = _pathIcons + "/info.svg"
        _iconSourcesParam        = _pathIcons + "/configuration.svg"
             
        #--------
        Dialog.resize(QtCore.QSize(QtCore.QRect(0,0, self.lScreenDialog, self.hScreenDialog).size()).expandedTo(Dialog.minimumSizeHint()))
        Dialog.setWindowTitle("POSTGRESQL METADATA GUI (Metadata storage in PostGreSQL)")
        Dialog.setWindowModality(Qt.WindowModal)
        Dialog.setWindowFlags(Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint) 
        _pathIcons = os.path.dirname(__file__) + "/icons/logo"
        iconSource          = _pathIcons + "/postmeta.svg"
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

        QtCore.QMetaObject.connectSlotsByName(Dialog)
        #========================== 

        #==========================
        #Récupération données 
        _d_template, _dict, _g_shape, _g_vocabulary, _g, _g1 = rdf_utils_demo.post_meta_return()
        self._g_vocabulary = _g_vocabulary
        #Récupération données 
        #==========================

        #print(rdf_utils_demo.pseudo_form(_dict))

        #==========================
        #Génération à la volée 
        #Dict des objets instanciés
        self.mDicObjetsInstancies = _dict
        self.listeResizeIhm = [] # For resizeIhm
        self.mFirstColor = True
        #--
        for key, value in _dict.items() :
            if _dict[key]['main widget type'] != None :
               #Gestion des onglets
               #if (rdf_utils.is_root(key) or  _dict[key]['label'] == "couverture temporelle") and _dict[key]['main widget type'] == "QGroupBox" : 
               if (rdf_utils.is_root(key) and _dict[key]['main widget type'] == "QGroupBox") : 
                  self.mFirst = rdf_utils.is_root(key)
                  self.groupBoxPrincipal = None
                  #Génération à la volée des onglets 
                  mParent = self.gestionOnglets(key, value)
               else :   
                  mParent = self.mDicObjetsInstancies.parent_grid(key)
               #Génération à la volée des objets 
               bibli_gene_objets.generationObjets(self, key, value, mParent)
               self.mFirstColor = False
            else :
               pass
        #--
        #--------------------------
        self.tabWidget.setCurrentIndex(0)
        #--
        #Génération à la volée 
        #==========================
        #=====================================================  
        # Window Versus Dock
        if self.ihm in ["dockTrue", "dockFalse"] :
           #----
           dlg = QDockWidget()
           dlg.setObjectName("POSTMETA")
           dlg.setMinimumSize(420, 300)
           dlg.setWindowTitle(QtWidgets.QApplication.translate("postmeta_ui", "POSTGRESQL METADATA GUI (Metadata storage in PostGreSQL)", None) + "  (" + str(bibli_postmeta.returnVersion()) + ")")
           self.iface.addDockWidget(Qt.RightDockWidgetArea, dlg)
           dlg.setFloating(True if self.ihm in ["dockTrue"] else False)
           dlg.setWidget(self.Dialog)
           dlg.resize(420, 300)
           self.dlg = dlg 
        # Window Versus Dock
        #=====================================================  
        #Menu Dialog
        self.mMenuBarDialog = QMenuBar(self)
        self.mMenuBarDialog.setGeometry(QtCore.QRect(0, 0, 280, 20))
        #--- Icons Actions ---- Edit, Empty, Export, Import, Save, Template, Traslation -----
        mText = QtWidgets.QApplication.translate("postmeta_main", "Edit") 
        self.postmetaEdit = QtWidgets.QPushButton(self.mMenuBarDialog)
        self.postmetaEdit.setStyleSheet("QPushButton { border: 0px solid black;}")  
        self.postmetaEdit.setIcon(QIcon(_iconSourcesEdit))
        self.postmetaEdit.setObjectName(mText)
        self.postmetaEdit.setToolTip(mText)
        self.postmetaEdit.setGeometry(QtCore.QRect(10,0,18,18))
        self.postmetaEdit.clicked.connect(self.clickButtonsActions)
        #--
        mText = QtWidgets.QApplication.translate("postmeta_main", "Save") 
        self.postmetaSave = QtWidgets.QPushButton(self.mMenuBarDialog)
        self.postmetaSave.setStyleSheet("QPushButton { border: 0px solid black;}")  
        self.postmetaSave.setIcon(QIcon(_iconSourcesSave))
        self.postmetaSave.setObjectName(mText)
        self.postmetaSave.setToolTip(mText)
        self.postmetaSave.setGeometry(QtCore.QRect(40,0,18,18))
        self.postmetaSave.clicked.connect(self.clickButtonsActions)
        #--
        mText = QtWidgets.QApplication.translate("postmeta_main", "Empty") 
        self.postmetaEmpty = QtWidgets.QPushButton(self.mMenuBarDialog)
        self.postmetaEmpty.setStyleSheet("QPushButton { border: 0px solid black;}")  
        self.postmetaEmpty.setIcon(QIcon(_iconSourcesEmpty))
        self.postmetaEmpty.setObjectName(mText)
        self.postmetaEmpty.setToolTip(mText)
        self.postmetaEmpty.setGeometry(QtCore.QRect(70,0,18,18))
        self.postmetaEmpty.clicked.connect(self.clickButtonsActions)
        #--
        mText = QtWidgets.QApplication.translate("postmeta_main", "Export") 
        self.postmetaExport = QtWidgets.QPushButton(self.mMenuBarDialog)
        self.postmetaExport.setStyleSheet("QPushButton { border: 0px solid black;}")  
        self.postmetaExport.setIcon(QIcon(_iconSourcesExport))
        self.postmetaExport.setObjectName(mText)
        self.postmetaExport.setToolTip(mText)
        self.postmetaExport.setGeometry(QtCore.QRect(100,0,18,18))
        self.postmetaExport.clicked.connect(self.clickButtonsActions)
        #--
        mText = QtWidgets.QApplication.translate("postmeta_main", "Import") 
        self.postmetaImport = QtWidgets.QPushButton(self.mMenuBarDialog)
        self.postmetaImport.setStyleSheet("QPushButton { border: 0px solid black;}")  
        self.postmetaImport.setIcon(QIcon(_iconSourcesImport))
        self.postmetaImport.setObjectName(mText)
        self.postmetaImport.setToolTip(mText)
        self.postmetaImport.setGeometry(QtCore.QRect(130,0,18,18))
        self.postmetaImport.clicked.connect(self.clickButtonsActions)
        #--
        mText = QtWidgets.QApplication.translate("postmeta_main", "Template") 
        self.postmetaTemplate = QtWidgets.QPushButton(self.mMenuBarDialog)
        self.postmetaTemplate.setStyleSheet("QPushButton { border: 0px solid black;}")  
        self.postmetaTemplate.setIcon(QIcon(_iconSourcesTemplate))
        self.postmetaTemplate.setObjectName(mText)
        self.postmetaTemplate.setToolTip(mText)
        self.postmetaTemplate.setGeometry(QtCore.QRect(160,0,18,18))
        self.postmetaTemplate.clicked.connect(self.clickButtonsActions)
        #--
        mText = QtWidgets.QApplication.translate("postmeta_main", "Translation") 
        self.postmetaTranslation = QtWidgets.QPushButton(self.mMenuBarDialog)
        self.postmetaTranslation.setStyleSheet("QPushButton { border: 0px solid black;}")  
        self.postmetaTranslation.setIcon(QIcon(_iconSourcesTranslation))
        self.postmetaTranslation.setObjectName(mText)
        self.postmetaTranslation.setToolTip(mText)
        self.postmetaTranslation.setGeometry(QtCore.QRect(190,0,18,18))
        self.postmetaTranslation.clicked.connect(self.clickButtonsActions)
        #------------
        #------------
        mText = QtWidgets.QApplication.translate("postmeta_main", "Customization of the IHM") 
        self.paramColor = QtWidgets.QPushButton(self.mMenuBarDialog)
        self.paramColor.setStyleSheet("QPushButton { border: 0px solid black;}")  
        self.paramColor.setIcon(QIcon(_iconSourcesParam))
        self.paramColor.setObjectName(mText)
        self.paramColor.setToolTip(mText)
        self.paramColor.setGeometry(QtCore.QRect(220,0,18,18))
        self.paramColor.clicked.connect(self.clickColorDialog)
        #--
        mText = QtWidgets.QApplication.translate("postmeta_main", "Help") 
        self.postmetaHelp = QtWidgets.QPushButton(self.mMenuBarDialog)
        self.postmetaHelp.setStyleSheet("QPushButton { border: 0px solid black;}")  
        self.postmetaHelp.setIcon(QIcon(_iconSourcesHelp))
        self.postmetaHelp.setObjectName(mText)
        self.postmetaHelp.setToolTip(mText)
        self.postmetaHelp.setGeometry(QtCore.QRect(250,0,18,18))
        self.postmetaHelp.clicked.connect(self.myHelpAM)
        #------------
        
        if self.ihm in ["dockTrue", "dockFalse"] : self.mMenuBarDialog.show()
        #==========================
        #==========================

        self.retranslateUi(Dialog)
        #Interactions avec les différents canaux de communication
        self.gestionInteractionConnections()

    #==========================
    # == Gestion des actions de bouttons de la barre de menu
    def clickButtonsActions(self):
        if not hasattr(self, 'mConnectEnCours') :
           zTitre = QtWidgets.QApplication.translate("postmeta_ui", "POSTMETA : Warning", None)
           zMess  = QtWidgets.QApplication.translate("bibli_ihm_asgard", "Merci de sélectionner une table, une vue dans un schéma. \
                                                                          \n\nSoit :                                               \
                                                                          \n * dans votre panneau 'Explorateur'                       \
                                                                          \n * dans votre gestionnaire de couche.", None)
           bibli_postmeta.displayMess(self.Dialog, (2 if self.Dialog.displayMessage else 1), zTitre, zMess, Qgis.Warning, self.Dialog.durationBarInfo)
           return

        mItem = self.mMenuBarDialog.sender().objectName()
        #**********************

        #**********************
        #**********************
        if mItem == "Edition" : 
           mKeySql = (pg_queries.query_is_relation_owner(), (self.schema, self.table))
           r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self.mConnectEnCoursPointeur, mKeySql, optionRetour = "fetchone")

           # A SUPPRIMER
           textTest = "Délimitation simplifiée des départements de France métropolitaine pour représentation à petite échelle, conforme au code officiel géographique (COG) de l'INSEE au 1er janvier de l'année de référence." 
           for k, v in self.mDicObjetsInstancies.items() :
               if v['value'] == textTest :
                  self.mDicObjetsInstancies[k]['main widget'].setText(str("SUPER, j'ai les droits" if r else "C'est BALOT !!, je n'ai pas de droits"))
                  break
           # A SUPPRIMER

           print(r)
        return
    # == Gestion des actions de bouttons de la barre de menu
    #==========================

    #---------------------------
    #---------------------------
    # == Gestion des INTERACTIONS
    def gestionInteractionConnections(self):
        #self.dbplugin = createDbPlugin('postgis', 'postgres')
        self.db      = None
        self.schema  = None
        self.table   = None
        self.comment = None
        self.origine = None
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
        self.origine = 'gestionnaire'
        self.layer = iface.activeLayer()
        if self.layer:
           if self.layer.dataProvider().name() == 'postgres':
              self.getAllFromUri()
              #--
              if self.connectBaseOKorKO[0] :
                 bibli_postmeta.test_interaction_sql(self)
        return
    
    #---------------------------
    def retrieveInfoLayerBrowser(self, index):
        mNav = self.sender().objectName()
        # DL
        self.origine = self.mNav1 if mNav == self.mNav1 else self.mNav2 
        #issu code JD Lomenede
        # DL
        self.proxy_model = self.navigateurTreeView.model() if mNav == self.mNav1 else self.navigateurTreeView2.model()
        # DL
        self.model = iface.browserModel()
        item = self.model.dataItem(self.proxy_model.mapToSource(index))
        #issu code JD Lomenede

        if isinstance(item, QgsLayerItem):
            self.layer = QgsVectorLayer(item.uri(), item.name(), 'postgres')
            self.getAllFromUri()
            #--
            if self.connectBaseOKorKO[0] :
               bibli_postmeta.test_interaction_sql(self)
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
           self.mConnectEnCoursPointeur = self.mConnectEnCours.cursor()
        else :    
           zTitre = QtWidgets.QApplication.translate("postmeta_ui", "POSTMETA : Warning", None)
           zMess  = QtWidgets.QApplication.translate("postmeta_ui", "Authentication problem", None)
           bibli_postmeta.displayMess(self.Dialog, (2 if self.Dialog.displayMessage else 1), zTitre, zMess, Qgis.Warning, self.Dialog.durationBarInfo)
        return

    #----------------------
    def connectBase(self) :
        return self.mTestConnect(self.mConfigConnection, self.uri)
          
    #----------------------
    def mTestConnect(self, mConfigConnection, uri) :
        retUser, retPassword, mTestConnect, okConnect = self.username, self.password, True, False
        mMessAuth = QtWidgets.QApplication.translate("postmeta_ui", "Authentication problem, check your password in particular.", None)
        connInfoUri = uri.connectionInfo()

        while mTestConnect :
           try :
              mConnectEnCours = psycopg2.connect(uri.connectionInfo(), application_name="Asgard Manager")
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
           self.mConnectEnCoursPointeur = mConnectEnCours.cursor()
           return True, self.mConnectEnCours, mConfigConnection
        else : 
           return False, None, ""    

    # == Gestion des INTERACTIONS
    #---------------------------
    #---------------------------

    #==========================
    def gestionOnglets(self, _key, _value):
        #--------------------------
        tab_widget_Onglet = QWidget()
        tab_widget_Onglet.setObjectName(str(_key))
        labelTabOnglet = str(_value['label'])
        self.tabWidget.addTab(tab_widget_Onglet, labelTabOnglet)
        #==========================         
        #Zone affichage Widgets
        zoneWidgetsGroupBox = QtWidgets.QGroupBox(tab_widget_Onglet)
        zoneWidgetsGroupBox.setStyleSheet("QGroupBox {   \
                                font-family: Serif ;   \
                                border-style: outset;    \
                                border-width: 0px;       \
                                border-radius: 10px;     \
                                border-color: red;      \
                                font: bold 11px;         \
                                padding: 6px;            \
                                }")

        x, y = 0, 0
        larg, haut =  self.tabWidget.width()- 5, self.tabWidget.height()-5
        zoneWidgetsGroupBox.setGeometry(QtCore.QRect(x, y, larg, haut))
        #--                        
        zoneWidgets = QtWidgets.QGridLayout()
        zoneWidgets.setContentsMargins(0, 0, 0, 0)
        zoneWidgetsGroupBox.setLayout(zoneWidgets )
        zoneWidgets.setObjectName("zoneWidgets" + str(_key))
        #--                        
        scroll_bar = QtWidgets.QScrollArea(tab_widget_Onglet) 
        scroll_bar.setWidgetResizable(True)
        scroll_bar.setGeometry(QtCore.QRect(x, y, larg, haut))
        scroll_bar.setMinimumWidth(50)
        self.groupBoxPrincipal = zoneWidgetsGroupBox
        scroll_bar.setWidget(self.groupBoxPrincipal)
        
        #--  
        #For resizeIhm 
        self.listeResizeIhm.append(zoneWidgetsGroupBox)                     
        self.listeResizeIhm.append(scroll_bar)                     
        return zoneWidgets

    #==========================
    def resizeEvent(self, event):
        if self.firstOpen :
           self.firstOpen = False
        #else :
        bibli_postmeta.resizeIhm(self, self.Dialog.width(), self.Dialog.height())

    #==========================
    def clickParamDisplayMessage(self):
        mDicAutre = {}
        mSettings = QgsSettings()
        mSettings.beginGroup("POSTMETA")
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
        Dialog.setWindowTitle(QtWidgets.QApplication.translate("postmeta_ui", "POSTGRESQL METADATA GUI (Metadata storage in PostGreSQL)", None) + "  (" + str(bibli_postmeta.returnVersion()) + ")")

    #==========================
    def clickColorDialog(self):
        d = docolorbloc.Dialog()
        d.exec_()
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
        bibli_postmeta.execPdf(valueDefautFileHelp)
        return
                 