# (c) Didier  LECLERC 2020 CMSIG MTE-MCTRCT/SG/SNUM/UNI/DRC Site de Rouen
# créé sept 2021
#        **************************************************************************
#        copyright            : (C) 2020 by JD Lomenede for
#                      self.proxy_model = self.navigateurTreeView.model()
#                      self.model = iface.browserModel()
#                      item = self.model.dataItem(self.proxy_model.mapToSource(index))
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

from .bibli_rdf import rdf_utils_demo
from .bibli_rdf import rdf_utils

class Ui_Dialog_postmeta(object):
    #def __init__(self):
    def __init__(self):
        #"""Constructor."""
        #super(Ui_Dialog_postmeta).__init__()

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
        _pathIcons = os.path.dirname(__file__) + "/bibli_rdf/icons/general"
        _iconSourcesEdit         = _pathIcons + "/edit.svg"
        _iconSourcesEmpty        = _pathIcons + "/empty.svg"
        _iconSourcesExport       = _pathIcons + "/export.svg"
        _iconSourcesImport       = _pathIcons + "/import.svg"
        _iconSourcesSave         = _pathIcons + "/Save.svg"
        _iconSourcesTemplate     = _pathIcons + "/template.svg"
        _iconSourcesTranslation  = _pathIcons + "/translation.svg"
             
        #--------
        Dialog.resize(QtCore.QSize(QtCore.QRect(0,0, self.lScreenDialog, self.hScreenDialog).size()).expandedTo(Dialog.minimumSizeHint()))
        Dialog.setWindowTitle("POSTGRESQL METADATA GUI (Metadata storage in PostGreSQL)")
        Dialog.setWindowModality(Qt.WindowModal)
        Dialog.setWindowFlags(Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint) 
        iconSource = bibli_postmeta.getThemeIcon("postmeta.png")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(iconSource), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)

        #==========================              
        #Zone Onglets
        self.tabWidget = QTabWidget(Dialog)
        self.tabWidget.setObjectName("tabWidget")
        x, y = 10, 25
        larg, haut =  self.lScreenDialog -20, (self.hScreenDialog - 80 )
        self.tabWidget.setGeometry(QtCore.QRect(x, y, larg , haut))
        self.tabWidget.setStyleSheet("QTabWidget::pane {border: 2px solid " + self.colorQTabWidget  + "; font-family:" + self.policeQGroupBox  +"; } \
                                    QTabBar::tab {border: 1px solid " + self.colorQTabWidget  + "; border-bottom-color: none; font-family:" + self.policeQGroupBox  +";\
                                                    border-top-left-radius: 6px;border-top-right-radius: 6px;\
                                                    width: 160px; padding: 2px;} \
                                      QTabBar::tab:selected {background: qlineargradient(x1: 0, y1: 0, x2: 0.5, y2: 0.5, stop: 0 " + self.colorQTabWidget  + ", stop: 1 white);  font: bold;} \
                                     ")
        #--                        
        #==========================         
        #Groupe liseré bas
        self.groupBoxDown = QtWidgets.QGroupBox(Dialog)
        self.groupBoxDown.setGeometry(QtCore.QRect(10,self.hScreenDialog - 50,self.lScreenDialog -20,40))
        self.groupBoxDown.setObjectName("groupBoxDown")
        self.groupBoxDown.setStyleSheet("QGroupBox {   \
                                border-style: outset;    \
                                border-width: 1px;       \
                                border-radius: 10px;     \
                                border-color: grey;      \
                                font: bold 12px;         \
                                padding: 6px;            \
                                }")  
        #=====================================================
        #Boutons  
        #------       
        self.okhButton = QtWidgets.QPushButton(self.groupBoxDown)
        self.okhButton.setGeometry(QtCore.QRect(((self.groupBoxDown.width() -200) / 3) + 100 + ((self.groupBoxDown.width() -200) / 3), 10, 100,23))
        self.okhButton.setObjectName("okhButton")
        if self.ihm in ["dockTrue", "dockFalse"] :
           self.okhButton.setVisible(False) 
        #------                                    
        self.helpButton = QtWidgets.QPushButton(self.groupBoxDown)
        self.helpButton.setGeometry(QtCore.QRect((self.groupBoxDown.width() -200) / 3, 10, 100,23))
        self.helpButton.setObjectName("helpButton")
        #------  
        #Connections  
        self.helpButton.clicked.connect(Dialog.myHelpAM)
        self.okhButton.clicked.connect(Dialog.reject)        
                             
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
        iconParam = bibli_postmeta.getThemeIcon("postmeta.png")
        self.mMenuBarDialog = QMenuBar(self)
        #--- Icons Actions ---- Edit, Empty, Export, Import, Save, Template, Traslation -----
        mText = QtWidgets.QApplication.translate("postmeta_main", "Edit") 
        self.postmetaEdit = QAction(QIcon(_iconSourcesEdit),mText,Dialog)
        self.postmetaEdit.setToolTip(mText)
        self.postmetaEdit.setObjectName(mText)
        self.postmetaEdit.triggered.connect(self.clickButtonsActions)
        self.mMenuBarDialog.addAction(self.postmetaEdit)


        mText = QtWidgets.QApplication.translate("postmeta_main", "Edit") 
        self.postmetaEdit2 = QtWidgets.QPushButton(self.mMenuBarDialog)
        self.postmetaEdit2.setIcon(QIcon(_iconSourcesEdit))
        self.postmetaEdit2.setObjectName(mText)
        self.postmetaEdit2.setToolTip(mText)
        self.postmetaEdit2.setGeometry(QtCore.QRect(10,0,18,18))
        self.postmetaEdit2.setObjectName(mText)
        self.postmetaEdit2.clicked.connect(self.clickButtonsActions)


        #--
        mText = QtWidgets.QApplication.translate("postmeta_main", "Save") 
        self.postmetaSave = QAction(QIcon(_iconSourcesSave),"Save",Dialog)
        self.postmetaSave.setText(mText)
        self.postmetaSave.setToolTip(mText)
        self.postmetaSave.setEnabled(False)
        self.postmetaSave.setObjectName(mText)
        self.postmetaSave.triggered.connect(self.clickButtonsActions)
        self.mMenuBarDialog.addAction(self.postmetaSave)
        #--
        mText = QtWidgets.QApplication.translate("postmeta_main", "Empty") 
        self.postmetaEmpty = QAction(QIcon(_iconSourcesEmpty),"Empty",Dialog)
        self.postmetaEmpty.setText(mText)
        self.postmetaEmpty.setToolTip(mText)
        self.postmetaEmpty.setObjectName(mText)
        self.postmetaEmpty.triggered.connect(self.clickButtonsActions)
        self.mMenuBarDialog.addAction(self.postmetaEmpty)
        #--
        mText = QtWidgets.QApplication.translate("postmeta_main", "Export") 
        self.postmetaExport = QAction(QIcon(_iconSourcesExport),"Export",Dialog)
        self.postmetaExport.setText(mText)
        self.postmetaExport.setToolTip(mText)
        self.postmetaExport.setObjectName(mText)
        self.postmetaExport.triggered.connect(self.clickButtonsActions)
        #self.mMenuBarDialog.addAction(self.postmetaExport)
        #--
        mText = QtWidgets.QApplication.translate("postmeta_main", "Import") 
        self.postmetaImport = QAction(QIcon(_iconSourcesImport),"Import",Dialog)
        self.postmetaImport.setText(mText)
        self.postmetaImport.setToolTip(mText)
        self.postmetaImport.setObjectName(mText)
        self.postmetaImport.triggered.connect(self.clickButtonsActions)
        #self.mMenuBarDialog.addAction(self.postmetaImport)
        #--
        mText = QtWidgets.QApplication.translate("postmeta_main", "Template") 
        self.postmetaTemplate = QAction(QIcon(_iconSourcesTemplate),"Template",Dialog)
        self.postmetaTemplate.setText(mText)
        self.postmetaTemplate.setToolTip(mText)
        self.postmetaTemplate.setObjectName(mText)
        self.postmetaTemplate.triggered.connect(self.clickButtonsActions)
        #self.mMenuBarDialog.addAction(self.postmetaTemplate)
        #--
        mText = QtWidgets.QApplication.translate("postmeta_main", "Translation") 
        self.postmetaTranslation = QAction(QIcon(_iconSourcesTranslation),"Translation",Dialog)
        self.postmetaTranslation.setText(mText)
        self.postmetaTranslation.setToolTip(mText)
        self.postmetaTranslation.setObjectName(mText)
        self.postmetaTranslation.triggered.connect(self.clickButtonsActions)
        #self.mMenuBarDialog.addAction(self.postmetaTranslation)
        #------------
        #------------
        self.mMenuParam = QMenu(self)
        self.mMenuParam.setToolTipsVisible(True)
        self.mMenuBarDialog.addMenu(self.mMenuParam)
        self.mMenuParam.setTitle(QtWidgets.QApplication.translate("asgard_general_ui", "ParamSettings"))

        self.mMenuParam.addAction(self.postmetaExport)
        self.mMenuParam.addAction(self.postmetaImport)
        self.mMenuParam.addAction(self.postmetaTemplate)
        self.mMenuParam.addAction(self.postmetaTranslation)
        self.mMenuParam.addSeparator()


        #--
        self.paramColor = QAction(QIcon(iconParam),"Customization of the IHM",Dialog)
        self.paramColor.setText(QtWidgets.QApplication.translate("asgard_main", "Customization of the IHM"))
        self.mMenuParam.addAction(self.paramColor)
        #- Actions
        self.paramColor.triggered.connect(self.clickColorDialog)
        if self.ihm in ["dockTrue", "dockFalse"] : self.mMenuBarDialog.show()


        #==========================
        #==========================

        self.retranslateUi(Dialog)
        #Interactions avec les différents canaux de communication
        self.gestionInteractionConnections()

    #==========================
    # == Gestion des actions de bouttons de la barre de menu
    def clickButtonsActions(self):
        print(self.mMenuBarDialog.sender().objectName())
        pass 
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
            bibli_postmeta.test_interaction_sql(self)
        return

    #---------------------------
    def getAllFromUri(self):
        uri = QgsDataSourceUri(self.layer.source())
        self.schema, self.table = uri.schema(), uri.table()
        #print( [ self.schema, self.table ] )
        #self.relationType = db_table._relationType #type de relation v=vue, m= vue matérialisée, r = relation (table)
        mConnectEnCours = psycopg2.connect(uri.connectionInfo(), application_name="POSTMETA")
        self.mConnectEnCours = mConnectEnCours
        self.mConnectEnCoursPointeur = mConnectEnCours.cursor()
        return

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
        larg, haut =  self.tabWidget.width()- 5, self.tabWidget.height()-25
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
        self.helpButton.setText(QtWidgets.QApplication.translate("postmeta_ui", "Help", None))
        self.okhButton.setText(QtWidgets.QApplication.translate("postmeta_ui", "Close", None))

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
                 