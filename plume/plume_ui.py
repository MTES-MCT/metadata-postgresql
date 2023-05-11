# (c) Didier  LECLERC 2020 CMSIG MTE-MCTRCT/SG/SNUM/UNI/DRC Site de Rouen
# créé sept 2021
#        **************************************************************************
#        copyright            : (C) 2021 by DL
#        **************************************************************************

from PyQt5 import QtCore, QtGui, QtWidgets, QtQuick 


from PyQt5.QtWidgets import (QAction, QMenu , QMenuBar, QMessageBox, 
                             QDockWidget, QTreeView, QTabWidget, QWidget, QSizePolicy)

from PyQt5.QtGui import ( QIcon, QKeySequence )
from html import escape

from qgis.core import Qgis

from plume.bibli_plume import ( NoReturnSql, MyExploBrowser, MyExploBrowserAsgardMenu,  
                                returnIcon, displayMess, saveinitializingDisplay, createFolder, exportObjetMetagraph, breakExecuteSql,
                                returnAndSaveDialogParam, returnIfExisteInBrowser, returnIfExisteInLegendeInterface, listUserParam, returnVersion,
                                afficheNoConnections,returnObjetTranslation, initIhmNoConnection, gestionErreurExisteLegendeInterface, ifChangeValues, saveMetaIhm,
                                importObjetMetagraph, importObjetMetagraphInspire, saveObjetTranslation, returnObjetsMeta, generationTemplateAndTabs,
                                resizeIhm, returnObjetComment, returnObjetMetagraph, returnObjetColumns, returnObjetData, returnObjetTpl_label, ifActivateRightsToManageModels,
                                executeSql, execPdf )

from plume.bibli_gene_objets import generationObjets, action_mObjetQToolButton_ComputeButton
#
from plume import docolorbloc
from plume import doabout
from plume import doimportcsw
from plume import docreatetemplate

from qgis.core import ( Qgis, QgsProject, QgsApplication, QgsSettings, QgsLayerItem, QgsVectorLayer, QgsDataSourceUri, QgsCredentials )
from qgis.gui  import ( QgsRubberBand, QgsMessageBar )
from PyQt5.QtCore    import ( Qt, QSize )

import qgis  
from qgis.utils import iface

import os
import traceback

from contextlib import contextmanager
import psycopg2
from plume.pg import queries
from plume.rdf.metagraph import copy_metagraph
from plume.pg.template import LocalTemplatesCollection
from plume.config import (VALUEDEFAUTFILEHELP, VALUEDEFAUTFILEHELPPDF, VALUEDEFAUTFILEHELPHTML, LIBURLCSWDEFAUT, URLCSWDEFAUT, URLCSWIDDEFAUT)  


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
           breakExecuteSql(self)

           if err.diag:
              zTitre = QtWidgets.QApplication.translate("plume_ui", "PLUME : Warning", None)
              zMess  = err.diag.message_primary  
              displayMess(self.Dialog, (2 if self.Dialog.displayMessage else 1), zTitre, zMess, Qgis.Warning, self.Dialog.durationBarInfo)

        except NoReturnSql as err_NoReturnSql :
           self.layerBeforeClicked = ("", "")
           saveinitializingDisplay("write", self.layerBeforeClicked)
           breakExecuteSql(self)

           zTitre = QtWidgets.QApplication.translate("plume_ui", "PLUME : Warning", None)
           zMess  = str(err_NoReturnSql.mMess) 
           displayMess(self.Dialog, (2 if self.Dialog.displayMessage else 1), zTitre, zMess, Qgis.Warning, self.Dialog.durationBarInfo)

        except Exception as err_Exception :
           self.layerBeforeClicked = ("", "")
           saveinitializingDisplay("write", self.layerBeforeClicked)
           breakExecuteSql(self)

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
        mDic_LH = returnAndSaveDialogParam(self, "Load")
        self.mDic_LH = mDic_LH
        #--
        self.lScreenDialog, self.hScreenDialog = int(self.mDic_LH["dialogLargeur"]), int(self.mDic_LH["dialogHauteur"])
        self.displayMessage    = False if self.mDic_LH["displayMessage"] == 'dialogTitle' else True #Qmessage box (dialogBox) ou barre de progression (dialogTitle)
        self.fileHelp          = VALUEDEFAUTFILEHELP      #Type Fichier Help
        self.fileHelpPdf       = VALUEDEFAUTFILEHELPPDF   #Fichier Help  PDF
        self.fileHelpHtml      = VALUEDEFAUTFILEHELPHTML  #Fichier Help  HTML
        self.durationBarInfo   = int(self.mDic_LH["durationBarInfo"])  #durée d'affichage des messages d'information
        self.ihm               = self.mDic_LH["ihm"]  #window/dock
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
        self.margeQToolButton = 40
        self.margeQMenu       = 50
        self.editStyle        = self.mDic_LH["QEdit"]              #style saisie
        self.epaiQGroupBox    = self.mDic_LH["QGroupBoxEpaisseur"] #épaisseur QGroupBox
        self.lineQGroupBox    = self.mDic_LH["QGroupBoxLine"]      #trait QGroupBox
        self.policeQGroupBox  = self.mDic_LH["QGroupBoxPolice"]    #Police QGroupBox
        self.policeQTabWidget = self.mDic_LH["QTabWidgetPolice"]   #Police QTabWidget
        #---
        self.libUrlCswDefaut   = LIBURLCSWDEFAUT       #libellé de l'Url par defaut
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
        self.activeZoneNonSaisie  = True   if self.mDic_LH["activeZoneNonSaisie"]     == "true" else False
        # For the Dock AsgardMenu Gestion des toolTip
        self.asgardMenuDock               = mDic_LH["asgardMenuDock"]
        #-
        mDicType         = ["ICON_CROSS", "ICON_X", "ICON_BOX", "ICON_CIRCLE", "ICON_FULL_BOX" , "ICON_DIAMOND" , "ICON_FULL_DIAMOND"]
        mDicTypeObj      = [QgsRubberBand.ICON_X, QgsRubberBand.ICON_CROSS, QgsRubberBand.ICON_BOX, QgsRubberBand.ICON_CIRCLE, QgsRubberBand.ICON_FULL_BOX, QgsRubberBand.ICON_DIAMOND, QgsRubberBand.ICON_FULL_DIAMOND]
        self.mDicTypeObj = dict(zip(mDicType, mDicTypeObj)) # For bibli_plume_tools_map
        _pathIconsUser = QgsApplication.qgisSettingsDirPath().replace("\\","/") + "plume/icons/buttons"
        createFolder(_pathIconsUser)        
        #-
        #Management Click before open IHM 
        if self.mDic_LH["layerBeforeClickedWho"] == "qgis" : 
           self.layerBeforeClicked = (returnIfExisteInLegendeInterface(self, self.mDic_LH["layerBeforeClicked"]), self.mDic_LH["layerBeforeClickedWho"], self.mDic_LH["layerBeforeClickedBrowser"]) # Couche mémorisée avant ouverture et de l'origine
        elif self.mDic_LH["layerBeforeClickedWho"] == "postgres" : 
           self.layerBeforeClicked = (returnIfExisteInBrowser(self, self.mDic_LH["layerBeforeClicked"]), self.mDic_LH["layerBeforeClickedWho"], self.mDic_LH["layerBeforeClickedBrowser"]) # Couche mémorisée avant ouverture et de l'origine
        else :
           self.layerBeforeClicked = ('', '') 
        #Cas ou l'instance sauvegardé dans le QGIS3.INI n'a plus de correspondance 
        if self.layerBeforeClicked[0] is None : self.layerBeforeClicked = ('', '')
        #Cas ou l'instance sauvegardé dans le QGIS3.INI n'a plus de correspondance 
           
        # for geometry
        # liste des Paramétres UTILISATEURS
        listUserParam(self)
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
        _pathIcons = os.path.dirname(__file__) + "/icons/misc"
        _iconSourcesBlank         = _pathIcons + "/blank.svg"
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
        _iconSourcesParam         = _pathIcons + "/custom.svg"
        _iconSourcesInterrogation = _pathIcons + "/info.svg"
        _iconSourcesVerrou        = _pathIcons + "/verrou.svg"
        _pathIconsQComboBox       = os.path.dirname(__file__) + "/icons/buttons"
        _iconQComboBox            = _pathIconsQComboBox + "/drop_down_arrow.svg"
        self._iconQComboBox = _iconQComboBox.replace("\\","/")
        
        # For menu contex QGroupBox
        self._iconSourcesCopy, self._iconSourcesPaste = _iconSourcesCopy, _iconSourcesPaste
        _iconSourcesPaste         = _pathIcons + "/paste_all.svg"
        
        self.listIconToolBar = [ _iconSourcesRead, _iconSourcesSave, _iconSourcesEmpty, _iconSourcesExport, _iconSourcesImport, _iconSourcesCopy, _iconSourcesPaste, _iconSourcesTemplate, _iconSourcesTranslation, _iconSourcesParam, _iconSourcesInterrogation, _iconSourcesVerrou, _iconSourcesBlank ]
        #--------
        Dialog.resize(QtCore.QSize(QtCore.QRect(0,0, self.lScreenDialog, self.hScreenDialog).size()).expandedTo(Dialog.minimumSizeHint()))
        self.messWindowTitle = QtWidgets.QApplication.translate("plume_ui", "PLUGIN METADATA (Metadata storage in PostGreSQL)", None) + "  (" + str(returnVersion()) + ")" 
        Dialog.setWindowTitle(self.messWindowTitle)
        Dialog.setWindowModality(Qt.WindowModal)
        Dialog.setWindowFlags(Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint) 
        _pathIcons = os.path.dirname(__file__) + "/icons/logo"
        iconSource          = _pathIcons + "/plume.svg"
        iconSourceTooltip   = _pathIcons + "/plume.svg"
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
        x, y = 10, 50
        larg, haut =  self.lScreenDialog -20, (self.hScreenDialog - 60 )
        self.tabWidget.setGeometry(QtCore.QRect(x, y, larg , haut))  
        self.tabWidget.setStyleSheet("QTabWidget::pane {border: 2px solid " + self.colorQTabWidget  + "; font-family:" + self.policeQGroupBox  +"; } \
                                    QTabBar::tab {border: 1px solid " + self.colorQTabWidget  + "; border-bottom-color: none; font-family:" + self.policeQGroupBox  +";\
                                                    border-top-left-radius: 6px;border-top-right-radius: 6px; \
                                                    } \
                                      QTabBar::tab:selected {background: qlineargradient(x1: 0, y1: 0, x2: 0.5, y2: 0.5, stop: 0 " + self.colorQTabWidget  + ", stop: 1 white);} \
                                     ")
        self.tabWidget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        tab_widget_Onglet = QWidget()
        tab_widget_Onglet.setObjectName("Informations")
        labelTabOnglet = "     Informations     "
        self.tabWidget.addTab(tab_widget_Onglet, labelTabOnglet)

        QtCore.QMetaObject.connectSlotsByName(Dialog)
        #========================== 
        #==========================
        #First Open 
        if self.firstOpen :
           afficheNoConnections(self, "first")
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
        if self.ihm in ["dockTrue", "dockFalse"] : self.mMenuBarDialogLine1.show()
        if self.ihm in ["dockTrue", "dockFalse"] : self.mMenuBarDialogLine2.show()
        #==========================
        self.retranslateUi(Dialog)

        #==========================
        #Interactions avec les différents canaux de communication
        self.gestionInteractionConnections()
        
        #==========================
        #Active Tooltip
        self._myExploBrowser           = MyExploBrowser(self.navigateur.findChildren(QTreeView)[0],               self._dicTooltipExiste, self.activeTooltip, self.activeTooltipColorText, self.activeTooltipColorBackground, self.langList, iconSourceTooltip,  self.activeTooltipLogo,  self.activeTooltipCadre,  self.activeTooltipColor, self.activeTooltipWithtitle)
        self._myExploBrowser2          = MyExploBrowser(self.navigateur2.findChildren(QTreeView)[0],              self._dicTooltipExiste, self.activeTooltip, self.activeTooltipColorText, self.activeTooltipColorBackground, self.langList, iconSourceTooltip,  self.activeTooltipLogo,  self.activeTooltipCadre,  self.activeTooltipColor, self.activeTooltipWithtitle)
        if self.navigateurasgardMenuDock != None : self._myExploBrowserAsgardMenu = MyExploBrowserAsgardMenu(self.navigateurasgardMenuDock.findChild(QTreeView),       self._dicTooltipExiste, self.activeTooltip, self.activeTooltipColorText, self.activeTooltipColorBackground, self.langList, iconSourceTooltip,  self.activeTooltipLogo,  self.activeTooltipCadre,  self.activeTooltipColor, self.activeTooltipWithtitle)
        
        #==========================
        #Instanciation des "shape, template, vocabulary, mode" 
        self.translation = returnObjetTranslation(self)
        
        #==========================
        #Management Click before open IHM 
        if self.layerBeforeClicked[0] != "" : 
           if self.layerBeforeClicked[1] == "qgis" : 
              self.retrieveInfoLayerQgis(None)
           elif self.layerBeforeClicked[1] == "postgres" : 
              self.retrieveInfoLayerQgis(self.layerBeforeClicked[0])
        else :      
           if not self.verrouLayer : initIhmNoConnection(self)
        #Management Click before open IHM 
           
    #= Fin setupUi

    #==========================
    # == Gestion des actions de boutons de la barre de menu
    def clickButtonsActions(self):
        # == Gestion Context ==
        with self.safe_pg_connection() :
           # If suppression d'une couche active pour les métadonnées affichées
           if not gestionErreurExisteLegendeInterface(self) : return
           # If suppression d'une couche active pour les métadonnées affichées

           mItemLine1 = self.mMenuBarDialogLine1.sender().objectName()
           mItemLine2 = self.mMenuBarDialogLine2.sender().objectName()
           #**********************
           if mItemLine1 == "Edition" :
              #Interroge l'utilisateur si modifications
              if self.mode == "edit" and self.zoneConfirmMessage :
                 if self.mDicObjetsInstancies.modified or ifChangeValues(self.mDicObjetsInstancies) or self.metagraph.rewritten :
                    if QMessageBox.question(None, "Confirmation", QtWidgets.QApplication.translate("plume_ui", "If you continue, unsaved changes will be lost."),QMessageBox.Ok|QMessageBox.Cancel) ==  QMessageBox.Cancel :
                       self.plumeEdit.setChecked(False if self.plumeEdit.isChecked() else True)  
                       return
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
           elif mItemLine1 == "Save" :                                            
              saveMetaIhm(self, self.schema, self.table) 
              self.saveMetaGraph = True
           #**********************
           elif mItemLine2 == "Empty" :
              if self.saveMetaGraph :
                 self.oldMetagraph  = self.metagraph
              else :   
                 self.metagraph     = self.oldMetagraph
              self.saveMetaGraph = False
              #-   
              old_metagraph = self.metagraph
              self.metagraph = copy_metagraph(None, old_metagraph)
           #**********************
           elif mItemLine2 == "Copy" :
              self.copyMetagraph = self.metagraph
              if self.copyMetagraph !=  None :
                 mTextToolTip = QtWidgets.QApplication.translate("plume_main", "Paste the metadata card of ") + "<b>" + str(self.schema) + "." + str(self.table) + "</b>     Alt+Maj+V" 
              else :    
                 mTextToolTip = QtWidgets.QApplication.translate("plume_main", "Paste the saved metadata card.")    
              self.copyMetagraphTooltip = mTextToolTip
              self.plumePaste.setToolTip(mTextToolTip)
           #**********************
           elif mItemLine2 == "Paste" :
              if self.copyMetagraph != None :
                 src_metagraph, old_metagraph = self.copyMetagraph, self.metagraph
                 _metagraph = copy_metagraph(src_metagraph, old_metagraph)
                 self.metagraph = _metagraph
           #**********************
           elif mItemLine2 == "plumeImportFile" :
              if self.saveMetaGraph :
                 self.oldMetagraph  = self.metagraph
              else :   
                 self.metagraph     = self.oldMetagraph
              self.saveMetaGraph = False
              #-   
              metagraph  = importObjetMetagraph(self)
              if metagraph != None : self.metagraph = metagraph
           #**********************
           elif mItemLine2 == "plumeImportFileInspire" :
              if self.saveMetaGraph :
                 self.oldMetagraph  = self.metagraph
              else :   
                 self.metagraph     = self.oldMetagraph
              self.saveMetaGraph = False
              #-   
              metagraph  = importObjetMetagraphInspire(self)
              if metagraph != None : self.metagraph = metagraph
           #**********************
           elif mItemLine1 == "Traduction" :
              #Interroge l'utilisateur si modifications
              if self.mode == "edit" and self.zoneConfirmMessage :
                 if self.mDicObjetsInstancies.modified or ifChangeValues(self.mDicObjetsInstancies) :
                    if QMessageBox.question(None, "Confirmation", QtWidgets.QApplication.translate("plume_ui", "If you continue, unsaved changes will be lost."),QMessageBox.Ok|QMessageBox.Cancel) ==  QMessageBox.Cancel : 
                       self.plumeTranslation.setChecked(False if self.plumeTranslation.isChecked() else True)  
                       return
                    #Si vous poursuivez, les modifications non enregistrées seront perdues.
              self.translation = (False if self.translation else True) 
           #**********************
           elif QtWidgets.QApplication.translate("plume_ui", mItemLine2) == "Verrouillage" :
              self.verrouLayer = (False if self.verrouLayer else True) 
              self.nameVerrouLayer = (self.layer if self.verrouLayer else None) 
              self.plumeVerrou.setChecked(True if self.verrouLayer else False)  

           #**********************
           #*** commun
           if mItemLine1 in ["Edition", "Save", "Empty", "plumeImportFile", "plumeImportFileInspire", "Paste", "Traduction"] or mItemLine2 in ["Edition", "Save", "Empty", "plumeImportFile", "plumeImportFileInspire", "Paste", "Traduction"] :
              saveObjetTranslation(self.translation)
              self.generationALaVolee(returnObjetsMeta(self))
           #-
           self.displayToolBar(*self.listIconToolBar)
        return
    # == Gestion des actions de boutons de la barre de menu
    #==========================

    #==========================
    # == Gestion des actions du bouton EXPORT de la barre de menu
    def clickButtonsExportActions(self):
        # If suppression d'une couche active pour les métadonnées affichées
        if not gestionErreurExisteLegendeInterface(self) : return
        # If suppression d'une couche active pour les métadonnées affichées

        mItemExport = self.mMenuBarDialogLine2.sender().objectName()
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
           if not gestionErreurExisteLegendeInterface(self) : return
           # If suppression d'une couche active pour les métadonnées affichées

           #Interroge l'utilisateur si modifications
           if self.mode == "edit" and self.zoneConfirmMessage :
              if self.mDicObjetsInstancies.modified or ifChangeValues(self.mDicObjetsInstancies) :
                 if QMessageBox.question(None, "Confirmation", QtWidgets.QApplication.translate("plume_ui", "If you continue, unsaved changes will be lost."),QMessageBox.Ok|QMessageBox.Cancel) ==  QMessageBox.Cancel :
                    self.plumeTemplate.setText(self.plumeTemplate.text())
                    return
                 #Si vous poursuivez, les modifications non enregistrées seront perdues.

           mItemTemplates = self.mMenuBarDialogLine1.sender().objectName()

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
                 generationTemplateAndTabs(self, mItemTemplates)
              else : 
                 self.template = self.templates_collection.get(mItemTemplates) if mItemTemplates else None
              #-
           # Génération à la volée
           self.generationALaVolee(returnObjetsMeta(self))

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
           if not gestionErreurExisteLegendeInterface(self) : return
           # If suppression d'une couche active pour les métadonnées affichées

           #Interroge l'utilisateur si modifications
           if self.mode == "edit" and self.zoneConfirmMessage :
              if self.mDicObjetsInstancies.modified or ifChangeValues(self.mDicObjetsInstancies) :
                 if QMessageBox.question(None, "Confirmation", QtWidgets.QApplication.translate("plume_ui", "If you continue, unsaved changes will be lost."),QMessageBox.Ok|QMessageBox.Cancel) ==  QMessageBox.Cancel :
                    self.plumeChoiceLang.setText(self.plumeChoiceLang.text())
                    return
                 #Si vous poursuivez, les modifications non enregistrées seront perdues.

           mItemLine1 = self.mMenuBarDialogLine1.sender().objectName()

           # MAJ ICON FLAGS
           self.majQmenuModeleIconFlagChoiceLang(mItemLine1)

           #un peu de robustesse car théo gérer dans le lecture du Qgis3.ini
           if mItemLine1 == "" : 
              self.language, mItemLine1 = "fr", "fr" 
           else:
               self.language = mItemLine1
           if mItemLine1 not in self.langList : self.langList.append(mItemLine1)  
           #un peu de robustesse car théo gérer dans le lecture du Qgis3.ini
           self.plumeChoiceLang.setText(mItemLine1)
           lenQTool = self.plumeChoiceLang.fontMetrics().size(Qt.TextSingleLine, mItemLine1).width()
           mDicUserSettings        = {}
           mSettings = QgsSettings()
           mSettings.beginGroup("PLUME")
           mSettings.beginGroup("UserSettings")
           #Ajouter si autre param
           mDicUserSettings["language"] = mItemLine1
           mDicUserSettings["langList"] = self.langList
           #----
           for key, value in mDicUserSettings.items():
               mSettings.setValue(key, value)
           #======================
           mSettings.endGroup()
           mSettings.endGroup()
           #----
           #Regénération du dictionnaire    
           self.generationALaVolee(returnObjetsMeta(self))
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
        labelTabOnglet = "     Informations     "
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
               generationObjets(self, key, value)
        self.mFirstColor = False
        #--

        # Nettoyage
        for comptElemTab in range(self.tabWidget.count()) :
            if self.tabWidget.tabText(comptElemTab) == "     Informations     " :
               self.tabWidget.removeTab(comptElemTab)
               
        # For Réaffichage du dimensionnement
        resizeIhm(self, self.Dialog.width(), self.Dialog.height())
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
        self.mNav1, self.mNav2, self.mNavAsgardMenu = 'Browser', 'Browser2', self.asgardMenuDock 
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
        #3 
        if len(iface.mainWindow().findChildren(QWidget, self.mNavAsgardMenu)) > 0 : 
           self.navigateurasgardMenuDock          = iface.mainWindow().findChildren(QWidget, self.mNavAsgardMenu)[0]
           self.navigateurasgardMenuDockTreeView  = self.navigateurasgardMenuDock.findChild(QTreeView)
           self.navigateurasgardMenuDockTreeView.setObjectName(self.mNavAsgardMenu)
        else :   
           self.navigateurasgardMenuDock = None
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
                afficheNoConnections(self, "hide")
                #-
                self.comment    = returnObjetComment(self, self.schema, self.table)
                self.metagraph  = returnObjetMetagraph(self, self.comment)
                self.oldMetagraph  = self.metagraph
                self.saveMetaGraph = False
                self.columns    = returnObjetColumns(self, self.schema, self.table)
                self.data       = returnObjetData(self)
                self.mode = "read"
                self.loadLayer = self.ifLayerLoad(self.layer)
                #-
                self.displayToolBar(*self.listIconToolBar)
                #-
                if self.instalMetadata :
                   #-
                   tpl_labelDefaut      = returnObjetTpl_label(self, None)
                   if tpl_labelDefaut :
                      self.template     = generationTemplateAndTabs(self, tpl_labelDefaut)
                   else :
                      self.template     = None
                else :
                   tpl_labelDefaut      = returnObjetTpl_label(self, "LOCAL")
                   self.template        = self.templates_collection[tpl_labelDefaut] if tpl_labelDefaut else None
                #-
                self.createQmenuModele(self._mObjetQMenu, self.templateLabels)
                self.majQmenuModeleIconFlag(tpl_labelDefaut)
                #
                self.majButtonTemplate(self.plumeTemplate, "Aucun" if tpl_labelDefaut == None else tpl_labelDefaut, int(len("Aucun" if tpl_labelDefaut == None else tpl_labelDefaut)))
                #-
                self.layerQgisBrowserOther = "QGIS"
                #-
                self.generationALaVolee(returnObjetsMeta(self))
                #-
                self.layerBeforeClicked = (self.layer, "qgis")
                saveinitializingDisplay("write", self.layerBeforeClicked)                 
           else :
              if not self.verrouLayer : initIhmNoConnection(self)
        return

    #---------------------------
    def retrieveInfoLayerBrowser(self, index):
        #-
        mNav = self.sender().objectName()
        # DL
        #issu code JD Lomenede
        # copyright            : (C) 2020 by JD Lomenede for # self.proxy_model = self.navigateurTreeView.model() = self.model = iface.browserModel() = item = self.model.dataItem(self.proxy_model.mapToSource(index)) #
        if mNav == self.mNav1 :
           self.proxy_model = self.navigateurTreeView.model()
        elif mNav == self.mNav2 :
           self.proxy_model = self.navigateurTreeView2.model()
        elif mNav == self.mNavAsgardMenu and self.navigateurasgardMenuDock != None :
           self.proxy_model = self.navigateurasgardMenuDockTreeView.model()
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
                    afficheNoConnections(self, "hide")
                    #-
                    self.comment    = returnObjetComment(self, self.schema, self.table)
                    self.metagraph  = returnObjetMetagraph(self, self.comment)
                    self.oldMetagraph  = self.metagraph
                    self.saveMetaGraph = False
                    self.columns    = returnObjetColumns(self, self.schema, self.table)
                    self.data       = returnObjetData(self)
                    self.mode = "read"
                    self.loadLayer = self.ifLayerLoad(self.layer)
                    #-
                    self.displayToolBar(*self.listIconToolBar)
                    #-
                    if self.instalMetadata :
                       #-
                       tpl_labelDefaut      = returnObjetTpl_label(self, None)
                       if tpl_labelDefaut :
                          self.template     = generationTemplateAndTabs(self, tpl_labelDefaut)
                       else :
                          self.template     = None
                    else :
                       tpl_labelDefaut      = returnObjetTpl_label(self, "LOCAL")
                       self.template        = self.templates_collection[tpl_labelDefaut] if tpl_labelDefaut else None
                    #-
                    self.createQmenuModele(self._mObjetQMenu, self.templateLabels)
                    self.majQmenuModeleIconFlag(tpl_labelDefaut)
                    #
                    self.majButtonTemplate(self.plumeTemplate, "Aucun" if tpl_labelDefaut == None else tpl_labelDefaut, int(len("Aucun" if tpl_labelDefaut == None else tpl_labelDefaut)))
                    #-
                    self.layerQgisBrowserOther = "BROWSER"
                    #-
                    self.generationALaVolee(returnObjetsMeta(self))
                    #-
                    self.layerBeforeClicked = (self.layer, "postgres")
                    saveinitializingDisplay("write", self.layerBeforeClicked, index, mNav)                 
           else :
              if not self.verrouLayer : initIhmNoConnection(self)
        else :
           if not self.verrouLayer : initIhmNoConnection(self)
        return

    #---------------------------
    def getAllFromUri(self):
        # ex : Projet fermé
        try : 
           if not getattr(self, 'layer', False) : 
              breakExecuteSql(self)
              return
        except :       
           breakExecuteSql(self)
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
           displayMess(self.Dialog, (2 if self.Dialog.displayMessage else 1), zTitre, zMess, Qgis.Warning, self.Dialog.durationBarInfo)
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
        resizeIhm(self, self.Dialog.width(), self.Dialog.height())

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
        with self.safe_pg_connection():
            d = doimportcsw.Dialog(self)
            d.exec_()
        return
        
    #==========================
    def clickCreateTemplate(self):
        
        with self.safe_pg_connection() :
           d = docreatetemplate.Dialog(self)
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
    def displayToolBar(self, _iconSourcesRead, _iconSourcesEmpty, _iconSourcesExport, _iconSourcesImport, _iconSourcesSave, _iconSourcesCopy, _iconSourcesPaste, _iconSourcesTemplate, _iconSourcesTranslation, _iconSourcesParam, _iconSourcesInterrogation, _iconSourcesVerrou, _iconSourcesBlank):
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
        self.plumeVerrou.setChecked(False)
        #Permet d'afficher si ifActivateRightsToManageModels = True
        self.mIfActivateRightsToManageModels = ifActivateRightsToManageModels(self)
        self.paramColor.setVisible(False if self.mIfActivateRightsToManageModels else True)
        self.paramColorModele.setVisible(True if self.mIfActivateRightsToManageModels else False)

        #====================
        #====================
        #--QToolButton TEMPLATE                                               
        if hasattr(self, 'mConnectEnCours') :
           
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
           self.plumeImport.setEnabled(r)
           self.plumePaste.setEnabled(True if (self.copyMetagraph != None and self.mode == "edit") else False)
           self.plumeTranslation.setEnabled(True if self.mode == "edit" else False)
           # issue 94 gestion des bouton sbarre d'outils dans le cas où nous ne sommes pas propriétaire
           self.plumeChoiceLang.setEnabled(r if r else True)
           self.plumeTemplate.setEnabled(r if r else True)
           self.plumeCopy.setEnabled(r if r else True)
           self.plumeExport.setEnabled(r if r else True)
           #
           self.plumeTranslation.setChecked(True if self.translation else False)  
           
           self.plumeVerrou.setEnabled(False if self.mode == "edit" else True)
           if self.mode == "edit" : self.verrouLayer = True
           if self.verrouLayer : self.plumeVerrou.setChecked(True)  
           #Mode edition avec les droits

           #Mode edition avec les droits
           if r == True and self.mode == 'read' : 
              self.plumeSave.setEnabled(False)
              self.plumeEmpty.setEnabled(False)
              self.plumeImport.setEnabled(False)                  
              self.plumeTranslation.setEnabled(False)
        #-
        self.plumeEdit.setToolTip(self.mTextToolTipEdit if self.mode == 'read' else self.mTextToolTipRead)   
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
    # == Gestion des Icons Flags dans le menu des choix des langues
    def majQmenuModeleIconFlagChoiceLang(self, mItemLang) :
        try : 
           _pathIcons = os.path.dirname(__file__) + "/icons/general"
           _iconSourcesSelect    = _pathIcons + "/selected_brown.svg"
           _iconSourcesVierge    = _pathIcons + ""

           if mItemLang == None : mItemLang = "Aucun" # Gestion si None
           for elemQMenuItem in self._mObjetQMenuChoiceLang.children() :
               if elemQMenuItem.text() == mItemLang : 
                  _mObjetQMenuIcon = QIcon(_iconSourcesSelect)
               else :                 
                  _mObjetQMenuIcon = QIcon(_iconSourcesVierge)
               elemQMenuItem.setIcon(_mObjetQMenuIcon)
        except :
           pass 
        return

    #==========================
    # == Gestion des actions de boutons de la barre de menu
    def createQmenuModele(self, _mObjetQMenu, templateLabels) :
        _mObjetQMenu.clear()
        templateLabels.insert(0, "Aucun")
        #------------
        textItem = ""
        for elemQMenuItem in templateLabels :
            _mObjetQMenuItem = QAction(elemQMenuItem, _mObjetQMenu)
            _mObjetQMenuItem.setText(elemQMenuItem)
            _mObjetQMenuItem.setObjectName(str(elemQMenuItem))
            _mObjetQMenu.addAction(_mObjetQMenuItem)   
            #- Actions
            _mObjetQMenuItem.triggered.connect(lambda : self.clickButtonsTemplateActions())

        textItem = max( templateLabels, key=lambda x:_mObjetQMenu.fontMetrics().size(Qt.TextSingleLine, x).width() )

        lenQTool = _mObjetQMenu.fontMetrics().size(Qt.TextSingleLine, textItem).width()
        _mObjetQMenu.setStyleSheet("QMenu {  font-family:" + self.policeQGroupBox  +"; border-width: 0px;}")
        #-
        self.plumeTemplate.setPopupMode(self.plumeTemplate.InstantPopup)
        self.plumeTemplate.setMenu(_mObjetQMenu)
        return

    #==========================
    # == Gestion des Icons Flags dans le menu des templates
    def majQmenuModeleIconFlag(self, mItemTemplates) :
        try : 
           _pathIcons = os.path.dirname(__file__) + "/icons/general"
           _iconSourcesSelect    = _pathIcons + "/selected_brown.svg"
           _iconSourcesVierge    = _pathIcons + ""

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
    #== Gestion de la taille et du texte du bouton Templates
    def majButtonTemplate(self, _plumeTemplate, _mTemplateTextChoice, _mLenTemplateTextChoice) :
        _plumeTemplate.setText(_mTemplateTextChoice)
        #_plumeTemplate.updateGeometry()
        #lenQTool = _plumeTemplate.fontMetrics().size(Qt.TextSingleLine, _mTemplateTextChoice).width()
        #_plumeTemplate.setMinimumWidth(lenQTool + self.margeQToolButton)
        _plumeTemplate.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        return

    #==========================
    # == Gestion des Icons Flags dans le menu des templates
    def majQmenuExportIconFlag(self) :
        mListExtensionFormat = self.metagraph.available_formats
        self.mListExtensionFormat = mListExtensionFormat
        self._mObjetQMenuExport.clear()
        textItem = max( mListExtensionFormat, key=lambda x:self._mObjetQMenuExport.fontMetrics().size(Qt.TextSingleLine, x).width() )
        lenQTool = self._mObjetQMenuExport.fontMetrics().size(Qt.TextSingleLine, textItem).width()
        #self._mObjetQMenuExport.setStyleSheet("QMenu { font-family:" + self.policeQGroupBox  +"; width:" + str((int(len(max(mListExtensionFormat))) * 10) + 50) + "px; border-style:" + self.editStyle  + "; border-width: 0px;}")
        self._mObjetQMenuExport.setStyleSheet("QMenu { font-family:" + self.policeQGroupBox  +"; border-style:" + self.editStyle  + "; border-width: 0px;}")
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
        self.plumeExport.setMenu(self._mObjetQMenuExport)
        return

    #==========================         
    def genereButtonsToolBarWithDict(self, dicParamButton ) :
        for k, v in dicParamButton.items() :
            if k == "typeWidget"    : _buttonToolBar = v
            if k == "qSizePolicy"   : _buttonToolBar.setSizePolicy(v, v)
            if k == "iconWidget"    : _buttonToolBar.setIcon(QIcon(v))
            if k == "nameWidget"    : _buttonToolBar.setObjectName(v)
            if k == "toolTipWidget" : _buttonToolBar.setToolTip(v)
            if k == "actionWidget"  : _buttonToolBar.clicked.connect(v)
            if k == "autoRaise"     : _buttonToolBar.setAutoRaise(v)
            if k == "checkable"     : _buttonToolBar.setCheckable(v)
            #-- Icon Blank
            if k == "redimIcon"     :
               h = _buttonToolBar.iconSize().height()
               _buttonToolBar.setIconSize(QSize(1, h))
            #-- Text
            if k == "textWidget"    : _buttonToolBar.setText(v)
            #-- StyleSheet
            if k == "styleSheet"    : _buttonToolBar.setStyleSheet(v)
            #-- Raccourci
            if k == "shorCutWidget" : _buttonToolBar.setShortcut(QKeySequence(v))
        return _buttonToolBar

    #==========================
    def createToolBar(self, _iconSourcesRead, _iconSourcesSave, _iconSourcesEmpty, _iconSourcesExport, _iconSourcesImport, _iconSourcesCopy, _iconSourcesPaste, _iconSourcesTemplate, _iconSourcesTranslation, _iconSourcesParam, _iconSourcesInterrogation, _iconSourcesVerrou, _iconSourcesBlank ):
        #Menu Dialog  
        self.mMenuBarDialogLine1 = QMenuBar(self)  
        self.mMenuBarDialogLine2 = QMenuBar(self) 
        try : 
           if hasattr(self, "monDock") :
              self.mMenuBarDialogLine1.setGeometry(QtCore.QRect(10,  0, self.tabWidget.width() , 23))
              self.mMenuBarDialogLine2.setGeometry(QtCore.QRect(10, 24, self.tabWidget.width() , 23))
           else:    
              self.mMenuBarDialogLine1.setGeometry(QtCore.QRect(10,  0, self.Dialog.width() - 20, 24))
              self.mMenuBarDialogLine2.setGeometry(QtCore.QRect(10, 24, self.Dialog.width() - 20, 24))
           self.mMenuBarDialogLine1.setStyleSheet("QMenuBar { border: 0px solid red;}")
           self.mMenuBarDialogLine2.setStyleSheet("QMenuBar { border: 0px solid green;}") 
           
           self.mMenuBarDialogLine1.setContentsMargins(0, 0, 0, 0)
           self.mMenuBarDialogLine2.setContentsMargins(0, 0, 0, 0)
        except :
              pass 

        self.mMenuBarDialogGridLine1 = QtWidgets.QHBoxLayout()
        self.mMenuBarDialogGridLine1.setContentsMargins(0, 0, 0, 0)
        self.mMenuBarDialogLine1.setLayout(self.mMenuBarDialogGridLine1)

        self.mMenuBarDialogGridLine2 = QtWidgets.QHBoxLayout()
        self.mMenuBarDialogGridLine2.setContentsMargins(0, 0, 0, 0)
        self.mMenuBarDialogLine2.setLayout(self.mMenuBarDialogGridLine2)
        #====================
        # ** First line **
        #====================
        # [ == plumeEdit == ]
        self.mTextToolTipRead = QtWidgets.QApplication.translate("plume_ui", "Edit") 
        self.mTextToolTipEdit = QtWidgets.QApplication.translate("plume_ui", "Read") 
        _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "iconWidget", "toolTipWidget", "actionWidget", "shorCutWidget", "autoRaise", "checkable", "qSizePolicy" ]
        _ListValues = [ QtWidgets.QToolButton(), "Edition", "Edition", _iconSourcesRead, self.mTextToolTipEdit, self.clickButtonsActions, "ALT+SHIFT+E", True, True, QSizePolicy.Fixed ]
        dicParamButton = dict(zip(_Listkeys, _ListValues))
        self.plumeEdit = self.genereButtonsToolBarWithDict( dicParamButton )
        # [ == plumeSave == ]
        _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "iconWidget", "toolTipWidget", "actionWidget", "shorCutWidget", "autoRaise", "qSizePolicy" ]
        _ListValues = [ QtWidgets.QToolButton(), "Save", "Save", _iconSourcesSave, QtWidgets.QApplication.translate("plume_ui", "Save"), self.clickButtonsActions, "ALT+SHIFT+S", True, QSizePolicy.Fixed ]
        dicParamButton = dict(zip(_Listkeys, _ListValues))
        self.plumeSave = self.genereButtonsToolBarWithDict( dicParamButton )
        # [ == plumeTranslation == ]    
        self.mTextToolTipNon = QtWidgets.QApplication.translate("plume_ui", "Enable translation functions.") 
        self.mTextToolTipOui = QtWidgets.QApplication.translate("plume_ui", "Disable translation functions.")
        _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "iconWidget", "toolTipWidget", "actionWidget", "shorCutWidget", "autoRaise", "checkable", "qSizePolicy" ]
        _ListValues = [ QtWidgets.QToolButton(), "Translation", "Traduction", _iconSourcesTranslation, self.mTextToolTipNon, self.clickButtonsActions, "ALT+SHIFT+T", True, True, QSizePolicy.Fixed ]
        dicParamButton = dict(zip(_Listkeys, _ListValues))
        self.plumeTranslation = self.genereButtonsToolBarWithDict( dicParamButton )
        #====================
        # [ == plumeChoiceLang == ]
        _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "iconWidget", "redimIcon", "toolTipWidget", "actionWidget", "autoRaise", "qSizePolicy", "styleSheet" ]
        _ListValues = [ QtWidgets.QToolButton(), self.language, "plumeChoiceLang", _iconSourcesBlank, True, QtWidgets.QApplication.translate("plume_ui", "Change the main metadata language.") , self.clickButtonsActions, True, QSizePolicy.Preferred, "QToolButton { font-family:" + self.policeQGroupBox  +";}" ]
        dicParamButton = dict(zip(_Listkeys, _ListValues))
        self.plumeChoiceLang = self.genereButtonsToolBarWithDict( dicParamButton )
        # -- QToolButton LANGUAGE MenuQToolButton                        
        _editStyle = self.editStyle  #style saisie
        _mObjetQMenu = QMenu()
        self._mObjetQMenuChoiceLang = _mObjetQMenu
        _mObjetQMenu.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        _mObjetQMenu.setStyleSheet("QMenu {  font-family:" + self.policeQGroupBox  +"; border-style:" + _editStyle  + "; border-width: 0px;}")

        _pathIcons = os.path.dirname(__file__) + "/icons/general"
        _iconSourcesSelect    = _pathIcons + "/selected_brown.svg"
        _iconSourcesVierge    = _pathIcons + ""
        #------------
        for elemQMenuItem in self.langList :
            _mObjetQMenuItem = QAction(elemQMenuItem, _mObjetQMenu)
            if elemQMenuItem == self.language : _mObjetQMenuItem.setIcon(QIcon(_iconSourcesSelect))
            _mObjetQMenuItem.setText(elemQMenuItem)
            _mObjetQMenuItem.setObjectName(str(elemQMenuItem))
            _mObjetQMenu.addAction(_mObjetQMenuItem)
            #- Actions
            _mObjetQMenuItem.triggered.connect(self.clickButtonsChoiceLanguages)
        #------------
        self.plumeChoiceLang.setPopupMode(self.plumeChoiceLang.InstantPopup)
        self.plumeChoiceLang.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.plumeChoiceLang.setMenu(_mObjetQMenu)
        # -- QToolButton LANGUAGE MenuQToolButton                        
        #====================
        # [ == plumeTemplate == ]
        _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "iconWidget", "toolTipWidget", "actionWidget", "autoRaise", "qSizePolicy", "styleSheet" ]
        _ListValues = [ QtWidgets.QToolButton(), QtWidgets.QApplication.translate("plume_ui", "Template"), "Template", _iconSourcesTemplate, QtWidgets.QApplication.translate("plume_ui", "Choose a form template."), self.clickButtonsActions, True, QSizePolicy.Preferred, "QToolButton { font-family:" + self.policeQGroupBox  +";}" ]
        dicParamButton = dict(zip(_Listkeys, _ListValues))
        self.plumeTemplate = self.genereButtonsToolBarWithDict( dicParamButton )
        # -- QToolButton TEMPLATE MenuQToolButton                        
        _mObjetQMenu = QMenu()
        self._mObjetQMenu = _mObjetQMenu
        #------------
        self.plumeTemplate.setPopupMode(self.plumeTemplate.InstantPopup)
        self.plumeTemplate.setToolButtonStyle(Qt.ToolButtonTextBesideIcon) 
        # -- QToolButton TEMPLATE MenuQToolButton                        

        # ** Add First line **
        self.mMenuBarDialogGridLine1.addWidget(self.plumeEdit)
        self.mMenuBarDialogGridLine1.addWidget(self.plumeSave)
        self.mMenuBarDialogGridLine1.addWidget(self.plumeTranslation)
        self.mMenuBarDialogGridLine1.addWidget(self.plumeChoiceLang)
        self.mMenuBarDialogGridLine1.addWidget(self.plumeTemplate)
        self.mMenuBarDialogGridLine1.addStretch(1)

        # [ == plumeCopy == ]
        _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "iconWidget", "toolTipWidget", "actionWidget", "shorCutWidget", "autoRaise", "qSizePolicy" ]
        _ListValues = [ QtWidgets.QToolButton(), QtWidgets.QApplication.translate("plume_ui", "Copy"), "Copy", _iconSourcesCopy, QtWidgets.QApplication.translate("plume_ui", "Copy the metadata card."), self.clickButtonsActions, "ALT+SHIFT+C", True, QSizePolicy.Fixed ]
        dicParamButton = dict(zip(_Listkeys, _ListValues))
        self.plumeCopy = self.genereButtonsToolBarWithDict( dicParamButton )
        #Création pour la copy à None
        self.copyMetagraph = None
        # [ == plumePaste == ]
        _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "iconWidget", "toolTipWidget", "actionWidget", "shorCutWidget", "autoRaise", "qSizePolicy" ]
        _ListValues = [ QtWidgets.QToolButton(), QtWidgets.QApplication.translate("plume_ui", "Paste"), "Paste", _iconSourcesPaste, QtWidgets.QApplication.translate("plume_ui", "Paste the saved metadata card."), self.clickButtonsActions, "ALT+SHIFT+V", True, QSizePolicy.Fixed ]
        dicParamButton = dict(zip(_Listkeys, _ListValues))
        self.plumePaste = self.genereButtonsToolBarWithDict( dicParamButton )
        # [ == plumeEmpty == ]
        _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "iconWidget", "toolTipWidget", "actionWidget", "shorCutWidget", "autoRaise", "qSizePolicy" ]
        _ListValues = [ QtWidgets.QToolButton(), QtWidgets.QApplication.translate("plume_ui", "Empty"), "Empty", _iconSourcesEmpty, QtWidgets.QApplication.translate("plume_ui", "Empty the metadata card."), self.clickButtonsActions, "ALT+SHIFT+B", True, QSizePolicy.Fixed ]
        dicParamButton = dict(zip(_Listkeys, _ListValues))
        self.plumeEmpty = self.genereButtonsToolBarWithDict( dicParamButton )
        # [ == plumeImport == ]
        _Listkeys   = [ "typeWidget", "nameWidget", "iconWidget", "toolTipWidget", "actionWidget", "autoRaise", "qSizePolicy" ]
        _ListValues = [ QtWidgets.QToolButton(), "Import", _iconSourcesImport, QtWidgets.QApplication.translate("plume_ui", "Import metadata."), self.clickButtonsActions, True, QSizePolicy.Fixed ]
        dicParamButton = dict(zip(_Listkeys, _ListValues))
        self.plumeImport = self.genereButtonsToolBarWithDict( dicParamButton )
        # -- QToolButton IMPORT MenuQToolButton                        
        _mObjetQMenu = QMenu()
        _mObjetQMenu.setToolTipsVisible(True)
        _editStyle = self.editStyle             #style saisie
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
        lenQTool = self._mObjetQMenu.fontMetrics().size(Qt.TextSingleLine, mText).width()
        _mObjetQMenu.setStyleSheet("QMenu {  font-family:" + self.policeQGroupBox  +"; border-style:" + _editStyle  + "; border-width: 0px;}")
        #------------
        self.plumeImport.setPopupMode(self.plumeImport.InstantPopup)
        self.plumeImport.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.plumeImport.setMenu(_mObjetQMenu)
        # -- QToolButton IMPORT MenuQToolButton                        
        #====================
        # [ == plumeExport == ]
        _Listkeys   = [ "typeWidget", "nameWidget", "iconWidget", "toolTipWidget", "actionWidget", "autoRaise", "qSizePolicy" ]
        _ListValues = [ QtWidgets.QToolButton(), "Export", _iconSourcesExport, QtWidgets.QApplication.translate("plume_ui", "Export metadata to a file."), self.clickButtonsActions, True, QSizePolicy.Fixed ]
        dicParamButton = dict(zip(_Listkeys, _ListValues))
        self.plumeExport = self.genereButtonsToolBarWithDict( dicParamButton )
        # -- QToolButton EXPORT MenuQToolButton                        
        _mObjetQMenu = QMenu()
        _mObjetQMenu.setToolTipsVisible(True)
        self._mObjetQMenuExport = _mObjetQMenu
        _mObjetQMenu.setStyleSheet("QMenu {  font-family:" + self.policeQGroupBox  +"; border-style:" + _editStyle  + "; border-width: 0px;}")
        #------------
        self.plumeExport.setPopupMode(self.plumeExport.InstantPopup)
        self.plumeExport.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        # -- QToolButton EXPORT MenuQToolButton                        
        #====================
        # [ == paramColor == ] afficher si ifActivateRightsToManageModels = False
        _Listkeys   = [ "typeWidget", "nameWidget", "iconWidget", "toolTipWidget", "actionWidget", "autoRaise", "qSizePolicy" ]
        _ListValues = [ QtWidgets.QToolButton(), "Customization of the IHM", _iconSourcesParam, QtWidgets.QApplication.translate("plume_ui", "Customization of the IHM"), self.clickColorDialog, True, QSizePolicy.Fixed ]
        dicParamButton = dict(zip(_Listkeys, _ListValues))
        self.paramColor = self.genereButtonsToolBarWithDict( dicParamButton )


        #====================
        # [ == paramColor and Gestion des modèles == ] afficher si ifActivateRightsToManageModels = True
        _Listkeys   = [ "typeWidget", "nameWidget", "iconWidget", "toolTipWidget", "actionWidget", "autoRaise", "qSizePolicy" ]
        _ListValues = [ QtWidgets.QToolButton(), "Customization of the IHM / Model management", _iconSourcesParam, QtWidgets.QApplication.translate("plume_ui", "Customization of the IHM / Model management"), self.clickButtonsActions, True, QSizePolicy.Fixed ]
        dicParamButton = dict(zip(_Listkeys, _ListValues))
        self.paramColorModele = self.genereButtonsToolBarWithDict( dicParamButton )
        
        # -- QToolButton paramColor ? MenuQToolButton                        
        _mObjetQMenu = QMenu()
        _mObjetQMenu.setToolTipsVisible(True)
        _editStyle = self.editStyle             #style saisie
        #------------
        #-- paramColor
        mText = QtWidgets.QApplication.translate("plume_ui", "Customization of the IHM") 
        self.paramColorItem = QAction("Customization of the IHM",self.paramColorModele)
        self.paramColorItem.setText(mText)
        self.paramColorItem.setObjectName("Customization of the IHM")
        self.paramColorItem.setToolTip(mText)
        self.paramColorItem.triggered.connect(self.clickColorDialog)
        _mObjetQMenu.addAction(self.paramColorItem)
        #-- paramColor
        _mObjetQMenu.addSeparator()
        #-- Gestion des modèles
        mText = QtWidgets.QApplication.translate("plume_ui", "Model management") 
        self.paramModeleItem = QAction("Model management",self.paramColorModele)
        self.paramModeleItem.setText(mText)
        self.paramModeleItem.setObjectName("Model management")
        self.paramModeleItem.setToolTip(mText)
        self.paramModeleItem.triggered.connect(self.clickCreateTemplate)
        _mObjetQMenu.addAction(self.paramModeleItem)
        #-- Gestion des modèles
        _mObjetQMenu.setStyleSheet("QMenu {  font-family:" + self.policeQGroupBox  +"; border-style:" + _editStyle  + "; border-width: 0px;}")
        #------------
        self.paramColorModele.setPopupMode(self.paramColorModele.InstantPopup)
        self.paramColorModele.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.paramColorModele.setMenu(_mObjetQMenu)
        # -- QToolButton paramColor ? MenuQToolButton                        
        # [ == paramColor and Gestion des modèles == ] afficher si ifActivateRightsToManageModels = True
        #====================


        #====================
        # [ == templates == ]
        _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "iconWidget", "toolTipWidget", "actionWidget", "autoRaise", "qSizePolicy", "styleSheet" ]
        _ListValues = [ QtWidgets.QToolButton(), QtWidgets.QApplication.translate("plume_ui", "Template"), "CreateTemplate", _iconSourcesTemplate, QtWidgets.QApplication.translate("plume_ui", "Choose a form template."), self.clickCreateTemplate, True, QSizePolicy.Preferred, "QToolButton { font-family:" + self.policeQGroupBox  +";}" ]
        dicParamButton = dict(zip(_Listkeys, _ListValues))
        self.createTemplate = self.genereButtonsToolBarWithDict( dicParamButton )


        #====================
        # [ == plumeInterrogation == ]
        _Listkeys   = [ "typeWidget", "nameWidget", "iconWidget", "toolTipWidget", "actionWidget", "autoRaise", "qSizePolicy" ]
        _ListValues = [ QtWidgets.QToolButton(), "plumeInterrogation", _iconSourcesInterrogation, QtWidgets.QApplication.translate("plume_ui", "Help / About"), self.clickButtonsActions, True, QSizePolicy.Fixed ]
        dicParamButton = dict(zip(_Listkeys, _ListValues))
        self.plumeInterrogation = self.genereButtonsToolBarWithDict( dicParamButton )
        # -- QToolButton POINT ? MenuQToolButton                        
        _mObjetQMenu = QMenu()
        _mObjetQMenu.setToolTipsVisible(True)
        _editStyle = self.editStyle             #style saisie
        #------------
        #-- Aide
        mText = QtWidgets.QApplication.translate("plume_ui", "Help") 
        self.plumeHelp = QAction("Help",self.plumeInterrogation)
        self.plumeHelp.setText(mText)
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
        self.plumeAbout.setObjectName("About")
        self.plumeAbout.setToolTip(mText)
        self.plumeAbout.triggered.connect(self.clickAbout)
        _mObjetQMenu.addAction(self.plumeAbout)
        #-- About
        _mObjetQMenu.setStyleSheet("QMenu {  font-family:" + self.policeQGroupBox  +"; border-style:" + _editStyle  + "; border-width: 0px;}")
        #------------
        self.plumeInterrogation.setPopupMode(self.plumeInterrogation.InstantPopup)
        self.plumeInterrogation.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.plumeInterrogation.setMenu(_mObjetQMenu)
        # -- QToolButton POINT ? MenuQToolButton                        
        # [ == plumeVerrou == ]
        self.mTextToolTipVerrouRead = QtWidgets.QApplication.translate("plume_ui", 'Lock the display on the current metadata card.') 
        self.mTextToolTipVerrouEdit = QtWidgets.QApplication.translate("plume_ui", 'Unlock the display.')                       
        _Listkeys   = [ "typeWidget", "nameWidget", "iconWidget", "toolTipWidget", "actionWidget", "shorCutWidget", "autoRaise", "checkable", "qSizePolicy" ]
        _ListValues = [ QtWidgets.QToolButton(), "Verrouillage", _iconSourcesVerrou, self.mTextToolTipVerrouEdit, self.clickButtonsActions, "ALT+SHIFT+R", True, True, QSizePolicy.Fixed ]
        dicParamButton = dict(zip(_Listkeys, _ListValues))
        self.plumeVerrou = self.genereButtonsToolBarWithDict( dicParamButton )

        #====================
        # ** Add Second line **
        self.mMenuBarDialogGridLine2.addWidget(self.plumeCopy)
        self.mMenuBarDialogGridLine2.addWidget(self.plumePaste)
        self.mMenuBarDialogGridLine2.addWidget(self.plumeEmpty)
        self.mMenuBarDialogGridLine2.addWidget(self.plumeImport)
        self.mMenuBarDialogGridLine2.addWidget(self.plumeExport)
        self.mMenuBarDialogGridLine2.addWidget(self.paramColor)
        self.mMenuBarDialogGridLine2.addWidget(self.paramColorModele)
        self.mMenuBarDialogGridLine2.addWidget(self.plumeInterrogation)
        self.mMenuBarDialogGridLine2.addWidget(self.createTemplate)
        
        self.createTemplate.setVisible(False) #Temporaire, A supprimer quand OK
        
        self.mMenuBarDialogGridLine2.addStretch(1)
        self.mMenuBarDialogGridLine2.addWidget(self.plumeVerrou)
        #--
        self.paramColor.setVisible(True)
        self.paramColorModele.setVisible(False)

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
        execPdf(valueDefautFileHelp)
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
            
                 
