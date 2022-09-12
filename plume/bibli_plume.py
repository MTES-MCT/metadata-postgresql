# (c) Didier  LECLERC 2020 CMSIG MTE-MCTRCT/SG/SNUM/UNI/DRC Site de Rouen
# créé sept 2021

from PyQt5 import QtCore, QtGui, QtWidgets, QtSvg
from PyQt5.QtWidgets import (QAction, QMenu , QApplication, QMessageBox, QFileDialog, QTextEdit, QLineEdit, QMainWindow, QWidget, QDockWidget, QTreeView, QTreeWidget) 
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import *
                     
from qgis.core import QgsProject, QgsMapLayer, QgsVectorLayerCache, QgsFeatureRequest, QgsSettings, QgsDataSourceUri, QgsCredentials
from qgis.utils import iface

from plume.config import (PLUME_VERSION)  

#==================================================
#==================================================
def returnVersion() : return PLUME_VERSION
#==================================================

from plume.rdf.widgetsdict import WidgetsDict
from plume.rdf.metagraph import Metagraph, metagraph_from_file, copy_metagraph, metagraph_from_iso_file
from plume.rdf.utils import export_extension_from_format, import_formats, import_extensions_from_format, export_format_from_extension
from plume.pg.description import PgDescription, truncate_metadata
from plume.pg.template import TemplateDict, search_template
from plume.pg import queries

from . import doerreur

from qgis.gui import (QgsAttributeTableModel, QgsAttributeTableView, QgsLayerTreeViewMenuProvider, QgsAttributeTableFilterModel)
from qgis.utils import iface

from qgis.core import *
from qgis.gui import *
import qgis                              
import os                       
import datetime
import os.path
import time

#==========================
#Regeneration de l'IHML et de la barre d'icone comme à l'ouverture
def initIhmNoConnection(self) :
    self.tabWidget.clear()
    tab_widget_Onglet = QWidget()
    tab_widget_Onglet.setObjectName("Informations")
    labelTabOnglet = "     Informations     "
    self.tabWidget.addTab(tab_widget_Onglet, labelTabOnglet)
    #-
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
    #-
    self.mode            = "read"  #Intiialise les autres instances  
    self.verrouLayer     = False   #Verrouillage de la couche 
    self.nameVerrouLayer = None    #Couche verrouillée 
    #-
    afficheNoConnections(self, "show")
    self.messWindowTitle = QtWidgets.QApplication.translate("plume_ui", "PLUGIN METADATA (Metadata storage in PostGreSQL)", None) + "  (" + str(returnVersion()) + ")" 
    self.Dialog.setWindowTitle(self.messWindowTitle)   
    if hasattr(self, "dlg") : self.dlg.setWindowTitle(self.messWindowTitle)   
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
       #---------- Sélectionnez une couche PostgreSQL  dans le panneau des couches ou   dans l'explorateur   pour consulter ses métadonnées.
       _zMess1 = QtWidgets.QApplication.translate("plume_ui", "Select a PostgreSQL layer", None) 
       _zMess2 = QtWidgets.QApplication.translate("plume_ui", "in the layers panel or", None) 
       _zMess3 = QtWidgets.QApplication.translate("plume_ui", "in explorer", None)
       _zMess4 = QtWidgets.QApplication.translate("plume_ui", "to view its metadata.", None) 
       zMess   = "<html>" + _zMess1 + "<ul style='margin: 0;'><li>" + _zMess2 + "</li><li>" + _zMess3 + "</li></ul>\n" + _zMess4 + "</html>"
       self.zoneWarningClickSource = QtWidgets.QLabel(self.tabWidget )
       self.zoneWarningClickSource.setGeometry(30, 110, 300, 100)
       self.zoneWarningClickSource.setStyleSheet("QLabel {   \
                font-family:" + self.policeQGroupBox  +" ; \
                }")
       self.zoneWarningClickSource.setText(zMess)
    else :
       self.labelImage.setVisible(True if action == "show" else False)
       self.zoneWarningClickSource.setVisible(True if action == "show" else False)
    #if hasattr(self, "plumeTemplate") : self.plumeTemplate.setFixedSize(QSize(30, 18))
    return

#==================================================
#Généralisation erreur si fin de transaction PostgreSLQ quel que soit le motif
def breakExecuteSql(self) :
    initIhmNoConnection(self)
    self.verrouLayer     = False   #Verrouillage de la couche 
    self.nameVerrouLayer = None    #Couche verrouillée
    return

#==========================
# If suppression d'une couche active pour les métadonnées affichées
#
#Gestion des erreurs et Liste des couches dans la légende
def gestionErreurExisteLegendeInterface(self, _first = False) :
    ret = True
    try : 
       self.layerBeforeClicked[0].id()
    except :
       if not _first : 
          zTitre = QtWidgets.QApplication.translate("plume_ui", "PLUME : Warning", None)
          zMess  = QtWidgets.QApplication.translate("plume_ui", "The layer corresponding to the metadata in Plume no longer exists.") + "\n" + QtWidgets.QApplication.translate("plume_ui", "Please reselect in the layer panel or in the explorer.", None)  
          displayMess(self.Dialog, (2 if self.Dialog.displayMessage else 1), zTitre, zMess, Qgis.Warning, self.Dialog.durationBarInfo)
       self.layerBeforeClicked = ("", "")
       saveinitializingDisplay("write", self.layerBeforeClicked)
       initIhmNoConnection(self)
       ret = False
    return ret
#
#Retounre si la couche existe ou pas
def ifExisteInLegendeInterface(self, _layerBeforeClick) :
    ret = False
    if _layerBeforeClick[1] == "qgis" : #uniquement sur le gestionnaire de couches
       layers = QgsProject.instance().mapLayers()
       for layer_id, layer in layers.items() :
          if _layerBeforeClick[0] == layer :
             ret = True
             break
    else : 
       ret = True 
    return ret   
#
# If suppression d'une couche active pour les métadonnées affichées
#==========================

#==========================
#Retounre si l'objet de type QgsVectorlayer en fonction de l'id
def returnIfExisteInLegendeInterface(self, _IdLayerBeforeClick) :
    layers = QgsProject.instance().mapLayers()
    return layers.get(_IdLayerBeforeClick)

#==========================
#Retounre si l'objet de type QgsVectorlayer en fonction de l'id
def returnIfExisteInBrowser(self, _ItemLayerBeforeClick) :
    index = _ItemLayerBeforeClick
    ret = None

    # Interaction avec le navigateur de QGIS
    mNav1, mNav2 = 'Browser', 'Browser2' 
    #1
    self.navi = iface.mainWindow().findChild(QDockWidget, mNav1)
    self.naviTreeView = self.navi.findChild(QTreeView)
    self.naviTreeView.setObjectName(mNav1)
    #2
    self.navi2 = iface.mainWindow().findChild(QDockWidget, mNav2)
    self.naviTreeView2 = self.navi2.findChild(QTreeView)
    self.naviTreeView2.setObjectName(mNav2)

    mNav = self.iface.sender().objectName()
    self.proxy_model = self.naviTreeView.model() if self.mDic_LH["layerBeforeClickedBrowser"] == mNav1 else self.naviTreeView2.model()

    self.modelDefaut = iface.browserModel() 
    self.model = iface.browserModel()
    item = self.model.dataItem(self.proxy_model.mapToSource(index))

    if isinstance(item, QgsLayerItem) :
       if item.providerKey() == 'postgres' :
          ret = QgsVectorLayer(item.uri(), item.name(), 'postgres')
    return ret   
#==========================

#==================================================
#Mets à jour la valeur de l'objet en fonction de son type
def updateObjetWithValue(_mObjetQSaisie, _valueObjet) : 
    __Val = _valueObjet['value']

    if _valueObjet['main widget type'] in ("QLineEdit",) :
       _mObjetQSaisie.setText(__Val if __Val != None else "")  
    elif _valueObjet['main widget type'] in ("QTextEdit",) :
       _mObjetQSaisie.setPlainText(__Val if __Val != None else "")  
    elif _valueObjet['main widget type'] in ("QComboBox",) :
       _mObjetQSaisie.setCurrentText(__Val if __Val != None else "")  
    elif _valueObjet['main widget type'] in ("QLabel",) :
       _mObjetQSaisie.setText(__Val if __Val != None else "")  
    elif _valueObjet['main widget type'] in ("QDateEdit",) :
       _displayFormat = 'dd/MM/yyyy'
       _mObjetQSaisie.setDate(QDate.fromString( __Val, _displayFormat)) 
    elif _valueObjet['main widget type'] in ("QDateTimeEdit",) :
       _displayFormat = 'dd/MM/yyyy hh:mm:ss'
       _mObjetQSaisie.setDateTime(QDateTime.fromString( __Val, _displayFormat))       
    elif _valueObjet['main widget type'] in ("QTimeEdit",) :
       _displayFormat = 'hh:mm:ss'
       _mObjetQSaisie.setTime(QTime.fromString( __Val, _displayFormat))       
    elif _valueObjet['main widget type'] in ("QCheckBox",) :
       _mObjetQSaisie.setCheckState((Qt.Checked if str(__Val).lower() == 'true' else Qt.Unchecked) if __Val != None else Qt.PartiallyChecked)
    return
#Mets à jour la valeur de l'objet en fonction de son type
#==================================================

#==================================================
def ifChangeValues(_dict):
    # Retourne si valeur changer dans l'IHM
    ret = False
    for key, value in _dict.items() :
        if _dict[key]['main widget type'] != None :
           oldValue = _dict[key]['value'] 
           if _dict[key]['main widget type'] in ("QLineEdit",) :
               goodValue = _dict[key]['main widget'].text() if _dict[key]['main widget'].text() != "" else None 
               if oldValue != (_dict[key]['main widget'].text() if _dict[key]['main widget'].text() != "" else None ) : ret = True
           elif _dict[key]['main widget type'] in ("QTextEdit",) :
               goodValue = _dict[key]['main widget'].toPlainText() if _dict[key]['main widget'].toPlainText() != "" else None 
               if oldValue != (_dict[key]['main widget'].toPlainText() if _dict[key]['main widget'].toPlainText() != "" else None ) : ret = True
           elif _dict[key]['main widget type'] in ("QComboBox",) :
               goodValue = _dict[key]['main widget'].currentText() if _dict[key]['main widget'].currentText() != "" else None 
               if oldValue != (_dict[key]['main widget'].currentText() if _dict[key]['main widget'].currentText() != "" else None) : ret = True
           elif _dict[key]['main widget type'] in ("QDateEdit",) :
               goodValue = _dict[key]['main widget'].date().toString("dd/MM/yyyy") if _dict[key]['main widget'].date().toString("dd/MM/yyyy") != "" else None 
               if oldValue != (_dict[key]['main widget'].date().toString("dd/MM/yyyy") if _dict[key]['main widget'].date().toString("dd/MM/yyyy") != "" else None ) : ret = True
           elif _dict[key]['main widget type'] in ("QDateTimeEdit",) :
               goodValue = _dict[key]['main widget'].dateTime().toString("dd/MM/yyyy hh:mm:ss") if _dict[key]['main widget'].dateTime().toString("dd/MM/yyyy hh:mm:ss") != "" else None 
               if oldValue != (_dict[key]['main widget'].dateTime().toString("dd/MM/yyyy hh:mm:ss") if _dict[key]['main widget'].dateTime().toString("dd/MM/yyyy hh:mm:ss") != "" else None ) : ret = True
           elif _dict[key]['main widget type'] in ("QTimeEdit",) :
               goodValue = _dict[key]['main widget'].time().toString("hh:mm:ss") if _dict[key]['main widget'].time().toString("hh:mm:ss") != "" else None 
               if oldValue != (_dict[key]['main widget'].time().toString("hh:mm:ss") if _dict[key]['main widget'].time().toString("hh:mm:ss") != "" else None ) : ret = True
           elif _dict[key]['main widget type'] in ("QCheckBox",) :
               goodValue = ("True" if _dict[key]['main widget'].checkState() == Qt.Checked else "False") if  _dict[key]['main widget'].checkState() != Qt.PartiallyChecked else None 
               if oldValue != ("True" if _dict[key]['main widget'].checkState() == Qt.Checked else "False") if  _dict[key]['main widget'].checkState() != Qt.PartiallyChecked else None : ret = True
           if ret :
              #print([_dict[key]['main widget type'], oldValue, goodValue ])
              break
    return ret

#==================================================
def listUserParam(self):
    # liste des Paramétres UTILISATEURS
    self.preferedTemplate        = self.mDic_LH["preferedTemplate"]                                       if ("preferedTemplate"        in self.mDic_LH and self.mDic_LH["preferedTemplate"] != "")        else None
    self.enforcePreferedTemplate = (True if self.mDic_LH["enforcePreferedTemplate"] == "true" else False) if ("enforcePreferedTemplate" in self.mDic_LH and self.mDic_LH["enforcePreferedTemplate"] != "") else None
    self.readHideBlank           = (True if self.mDic_LH["readHideBlank"]           == "true" else False) if ("readHideBlank"           in self.mDic_LH and self.mDic_LH["readHideBlank"] != "")           else None
    self.readHideUnlisted        = (True if self.mDic_LH["readHideUnlisted"]        == "true" else False) if ("readHideUnlisted"        in self.mDic_LH and self.mDic_LH["readHideUnlisted"] != "")        else None
    self.editHideUnlisted        = (True if self.mDic_LH["editHideUnlisted"]        == "true" else False) if ("editHideUnlisted"        in self.mDic_LH and self.mDic_LH["editHideUnlisted"] != "")        else None
    self.language                = self.mDic_LH["language"]                                               if "language"                 in self.mDic_LH                                                    else "fr"
    self.initTranslation         = self.mDic_LH["translation"]                                            if "translation"              in self.mDic_LH                                                    else "false" 
    self.langList                = self.mDic_LH["langList"]                                               if "langList"                 in self.mDic_LH                                                    else ['fr', 'en']
    self.geoideJSON              = (True if self.mDic_LH["geoideJSON"]              == "true" else False) if "geoideJSON"               in self.mDic_LH                                                    else True
    self.readOnlyCurrentLanguage = (True if self.mDic_LH["readOnlyCurrentLanguage"] == "true" else False) if ("readOnlyCurrentLanguage" in self.mDic_LH and self.mDic_LH["readOnlyCurrentLanguage"] != "") else None
    self.editOnlyCurrentLanguage = (True if self.mDic_LH["editOnlyCurrentLanguage"] == "true" else False) if ("editOnlyCurrentLanguage" in self.mDic_LH and self.mDic_LH["editOnlyCurrentLanguage"] != "") else None
    self.labelLengthLimit        = self.mDic_LH["labelLengthLimit"]                                       if ("labelLengthLimit"        in self.mDic_LH and self.mDic_LH["labelLengthLimit"] != "")        else None
    self.valueLengthLimit        = self.mDic_LH["valueLengthLimit"]                                       if ("valueLengthLimit"        in self.mDic_LH and self.mDic_LH["valueLengthLimit"] != "")        else None
    self.textEditRowSpan         = self.mDic_LH["textEditRowSpan"]                                        if ("textEditRowSpan"         in self.mDic_LH and self.mDic_LH["textEditRowSpan"] != "")         else None
    self.zoneConfirmMessage      = (True if self.mDic_LH["zoneConfirmMessage"]      == "true" else False) if "zoneConfirmMessage"       in self.mDic_LH                                                    else True
    self.zComboCleanPgDescription          = self.mDic_LH["cleanPgDescription"]                                               if "cleanPgDescription"                in self.mDic_LH                                                 else "never"
    self.copyDctTitleToPgDescription       = (True if self.mDic_LH["copyDctTitleToPgDescription"]       == "true" else False) if "copyDctTitleToPgDescription"       in self.mDic_LH                                                 else "false" 
    self.copyDctDescriptionToPgDescription = (True if self.mDic_LH["copyDctDescriptionToPgDescription"] == "true" else False) if "copyDctDescriptionToPgDescription" in self.mDic_LH                                                 else "false" 

    # liste des Paramétres UTILISATEURS
    
#==================================================
def returnObjetMetagraph(self, old_description) : return old_description.metagraph

#==================================================
def exportObjetMetagraph(self, schema, table, format, mListExtensionFormat) :
    #boite de dialogue Fichiers
    extStr = ""
    for elem in mListExtensionFormat :
        modelExt = export_extension_from_format(elem)
        extStrExt = "*" + str(modelExt) + " "
        extStr += ";;" + str(elem) + " (" + str(extStrExt) + ")"
    TypeList = extStr[2:]
    table = table.replace(".","_").replace(" ","_")
    InitDir = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') + "\\" + "metadata_" + str(schema) + "_" + str(table) + "" +  export_extension_from_format(format)
    mDialogueSave = QFileDialog
    fileName  = mDialogueSave.getSaveFileName(None,QtWidgets.QApplication.translate("bibli_plume", "PLUME Export of metadata files", None),InitDir,TypeList)[0] 
    format    = export_format_from_extension(os.path.splitext(fileName)[1], format)
    if fileName == "" : return
    #**********************
    # Export fiche de métadonnée
    try:
       self.metagraph.export(fileName, format)
    except:
       zTitre = QtWidgets.QApplication.translate("bibli_plume", "PLUME : Warning", None)
       zMess  = QtWidgets.QApplication.translate("bibli_plume", "PLUME failed to export your metadata record.", None)  
       displayMess(self.Dialog, (2 if self.Dialog.displayMessage else 1), zTitre, zMess, Qgis.Warning, self.Dialog.durationBarInfo)
    return  

#==================================================
def importObjetMetagraph(self) :
    #boite de dialogue Fichiers
    importFormats = import_formats()
    extStr = ""
    for elem in importFormats :
        modelExt = import_extensions_from_format(elem)
        extStrExt = ""
        for elemExt in modelExt :
            extStrExt += "*" + str(elemExt) + " "
        extStr += ";;" + str(elem) + " (" + str(extStrExt) + ")"
         
    MonFichierPath = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    MonFichierPath = MonFichierPath.replace("\\","/")        
    InitDir = MonFichierPath
    TypeList = extStr[2:]
    fileName = QFileDialog.getOpenFileName(None,QtWidgets.QApplication.translate("bibli_plume", "Metadata cards", None),InitDir,TypeList) 
    filepath = str(fileName[0]) if fileName[0] != "" else "" 
    if filepath == "" : return
    #**********************
    # Récupération fiche de métadonnée
    try:
       old_metagraph = self.metagraph
       metagraph  = metagraph_from_file(filepath, old_metagraph=old_metagraph)
    except:
       zTitre = QtWidgets.QApplication.translate("bibli_plume", "PLUME : Warning", None)
       zMess  = QtWidgets.QApplication.translate("bibli_plume", "PLUME failed to import your metadata record.", None) 
       displayMess(self.Dialog, (2 if self.Dialog.displayMessage else 1), zTitre, zMess, Qgis.Warning, self.Dialog.durationBarInfo)

       metagraph = None
    return metagraph 

#==================================================
def importObjetMetagraphInspire(self) :
    #boite de dialogue Fichiers
    MonFichierPath = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    MonFichierPath = MonFichierPath.replace("\\","/")        
    InitDir = MonFichierPath
    TypeList = QtWidgets.QApplication.translate("bibli_plume", "Inspire file", None) + " (*.xml);;" + QtWidgets.QApplication.translate("bibli_plume", "Other files", None) + " (*.*)"
    fileName = QFileDialog.getOpenFileName(None,QtWidgets.QApplication.translate("bibli_plume", "Metadata cards Inspire", None),InitDir,TypeList) 
    filepath = str(fileName[0]) if fileName[0] != "" else "" 
    if filepath == "" : return
    #**********************
    # Récupération fiche de métadonnée
    try:
       old_metagraph = self.metagraph
       metagraph = metagraph_from_iso_file(filepath, old_metagraph=old_metagraph)
    except:
       zTitre = QtWidgets.QApplication.translate("bibli_plume", "PLUME : Warning", None)
       zMess  = QtWidgets.QApplication.translate("bibli_plume", "PLUME failed to import your metadata record.", None) 
       displayMess(self.Dialog, (2 if self.Dialog.displayMessage else 1), zTitre, zMess, Qgis.Warning, self.Dialog.durationBarInfo)

       metagraph = None
    return metagraph 

#==================================================
def returnObjetTpl_label(self, option = None) : #None = Pas local et "LOCAL" = local
    #**********************
    #Récupération de la liste des modèles
    if option == "LOCAL" :
       mKeySql = queries.query_evaluate_local_templates(self.templates_collection, self.schema, self.table)
    else :   
       mKeySql = queries.query_list_templates(self.schema, self.table)
    self.templates, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self.mConnectEnCours, mKeySql, optionRetour = "fetchall")
    self.templateLabels = [t[0] for t in self.templates]    # templateLabels ne contient que les libellés des templates

    # Sélection automatique du modèle
    templateLabels = self.templateLabels 
    if self.preferedTemplate and self.enforcePreferedTemplate and templateLabels and self.preferedTemplate in templateLabels :
       tpl_label = self.preferedTemplate
    else : 
       tpl_label = search_template(self.templates, self.metagraph)
       if not tpl_label :
          if self.preferedTemplate and templateLabels and self.preferedTemplate in templateLabels :
             tpl_label = self.preferedTemplate

    return tpl_label 

#==================================================
# == Génération des CATEGORIES, TEMPLATE, TABS
def generationTemplateAndTabs(self, tpl_label):
    # Récupération des CATEGORIES associées au modèle retenu
    mKeySql = queries.query_get_categories(tpl_label)
    categories, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self.mConnectEnCours, mKeySql, optionRetour = "fetchall")
        
    # Récupération des ONGLETS associés au modèle retenu
    mKeySql = queries.query_template_tabs(tpl_label)
    tabs , zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self.mConnectEnCours, mKeySql, optionRetour = "fetchall")
           
    # Génération de template
    self.template = TemplateDict(categories, tabs)
    return self.template

#==================================================
def returnObjetColumns(self, _schema, _table) :
    #**********************
    # liste des champs de la table
    mKeySql = queries.query_get_columns(_schema, _table)
    columns, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self.mConnectEnCours, mKeySql, optionRetour = "fetchall")
    return columns 

#==================================================
def returnObjetData(self) :
    return    

#==================================================
def returnObjetTranslation(self) :
    #**********************
    # Mode  True False
    translation = True if self.initTranslation == 'true' else False
    return translation 

#==================================================
def saveObjetTranslation(mTranslation) :
    mSettings = QgsSettings()
    mDicAutre = {}
    mSettings.beginGroup("PLUME")
    mSettings.beginGroup("UserSettings")    

    mDicAutre["translation"] = "true" if mTranslation else 'false'
                 
    for key, value in mDicAutre.items():
        mSettings.setValue(key, value)

    mSettings.endGroup()
    mSettings.endGroup()    
    return    

#==================================================
def returnObjetComment(self, _schema, _table) :
    #**********************
    # Récupération champ commentaire
    mKeySql = queries.query_get_table_comment(_schema, _table)
    old_description, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self.mConnectEnCours, mKeySql, optionRetour = "fetchone")
    return PgDescription(old_description, 
                         clean=self.zComboCleanPgDescription,
                         copy_dct_title=self.copyDctTitleToPgDescription,
                         copy_dct_description=self.copyDctDescriptionToPgDescription
                        )

#==================================================
def returnObjetsMeta(self) :
    #**********************
    #Create Dict
    kwa = {}
    for param in ('metagraph', 'template', 'columns', 'data', 'mode', 'translation',
        'language', 'langList', 'readHideBlank', 'readHideUnlisted', 'editHideUnlisted',
        'readOnlyCurrentLanguage', 'editOnlyCurrentLanguage', 'labelLengthLimit',
        'valueLengthLimit', 'textEditRowSpan'):
        if getattr(self, param) is not None:
            kwa[param] = getattr(self, param)
    return WidgetsDict(**kwa)

#==================================================
def saveMetaIhm(self, _schema, _table) :
    #---------------------------
    # Gestion des langues
    _language = self.language

    #-    
    # Enregistrer dans le dictionnaire de widgets les valeurs contenues dans les widgets de saisie.
    for _keyObjet, _valueObjet in self.mDicObjetsInstancies.items() :
        if _valueObjet['main widget type'] != None :
           value = None
           if _valueObjet['main widget type'] in ("QLineEdit",) :
               value = _valueObjet['main widget'].text()
           elif _valueObjet['main widget type'] in ("QTextEdit",) :
               value = _valueObjet['main widget'].toPlainText()
           elif _valueObjet['main widget type'] in ("QComboBox",) :
               value = _valueObjet['main widget'].currentText()                   
           elif _valueObjet['main widget type'] in ("QDateEdit",) :
               value = _valueObjet['main widget'].date().toString("dd/MM/yyyy")
           elif _valueObjet['main widget type'] in ("QDateTimeEdit",) :
              value = _valueObjet['main widget'].dateTime().toString("dd/MM/yyyy hh:mm:ss")
           elif _valueObjet['main widget type'] in ("QTimeEdit",) :
              value = _valueObjet['main widget'].time().toString("hh:mm:ss")
           elif _valueObjet['main widget type'] in ("QCheckBox",) :
              value = (True if _valueObjet['main widget'].checkState() == Qt.Checked else False) if  _valueObjet['main widget'].checkState() != Qt.PartiallyChecked else None

           if _valueObjet['object'] == "edit" and not (_valueObjet['hidden']): 
              self.mDicObjetsInstancies.update_value(_keyObjet, value)
    #-    
    #Générer un graphe RDF à partir du dictionnaire de widgets actualisé 
    self.metagraph = self.mDicObjetsInstancies.build_metagraph()        
    self.oldMetagraph  = self.metagraph
    #-    
    #Créer une version actualisée du descriptif PostgreSQL de l'objet. 
    self.comment.metagraph = self.metagraph
    new_pg_description = str(self.comment)
    # une requête de mise à jour du descriptif.
    mKeySql = queries.query_get_relation_kind(_schema, _table) 
    kind, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self.mConnectEnCours, mKeySql, optionRetour = "fetchone")
    #-    
    mKeySql = queries.query_update_table_comment(_schema, _table, relation_kind = kind[0], description = new_pg_description) 
    r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self.mConnectEnCours, mKeySql, optionRetour = None)
    self.mConnectEnCours.commit()
    #-
    #Mettre à jour les descriptifs des champs de la table.    
    mKeySql = queries.query_update_columns_comments(_schema, _table, self.mDicObjetsInstancies)
    r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self.mConnectEnCours, mKeySql, optionRetour = None)
    self.mConnectEnCours.commit()
    #- Mettre à jour les descriptifs de la variable columns pour réaffichage
    self.columns = returnObjetColumns(self, self.schema, self.table)
    return  

#==================================================
# class pour gérer les erreur autre  que PostgreSLQ qui ne retourne pas de valeurs
#==================================================
class NoReturnSql(Exception) :
    def __init__(self, _mMess) :
        self.mMess = _mMess
        return
        
#==================================================
#==================================================
# gestion des tooltip in the browser
class MyExploBrowser(QTreeWidget):
   def __init__(self, parent, _dicTooltipExiste, _activeTooltip, _activeTooltipColorText, _activeTooltipColorBackground, _langList, _iconSource, _activeTooltipLogo, _activeTooltipCadre, _activeTooltipColor, _activeTooltipWithtitle, *args):
        QTreeWidget.__init__(self, parent = None, *args)
        self.parent = parent
        self.parent.setMouseTracking(True)
        self._activeTooltip, self._activeTooltipColorText, self._activeTooltipColorBackground, self._langList, self._iconSource, self._activeTooltipLogo, self._activeTooltipCadre, self._activeTooltipColor, self._activeTooltipWithtitle = \
             _activeTooltip,      _activeTooltipColorText,      _activeTooltipColorBackground,      _langList,      _iconSource,      _activeTooltipLogo,      _activeTooltipCadre,      _activeTooltipColor,      _activeTooltipWithtitle
        self._dicTooltipExiste = _dicTooltipExiste
        #
        self.parent.viewport().installEventFilter(self)

   def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.MouseMove:                   
            if event.buttons() == QtCore.Qt.NoButton:
                self.proxy_model = self.parent.model()
                self.model       = iface.browserModel()
                #
                index = self.parent.indexAt(event.pos())
                #
                if index != -1 and self.proxy_model != None :
                   self.itemLayer = self.model.dataItem(self.proxy_model.mapToSource(index))
                   
                   if self.itemLayer != None :
                      #Gestion id for _dicTooltipExiste  
                      if isinstance(self.itemLayer, QgsLayerItem) :
                         if self.itemLayer.providerKey() == 'postgres' :
                            itemLayer_id = QgsVectorLayer(self.itemLayer.uri(), self.itemLayer.name(), 'postgres').id()
                         else : # Non vector postgresql
                            return False  
                      else :  # Non type layer     
                         return False  
                      #Gestion id for _dicTooltipExiste  

                      self.itemLayer.setObjectName("itemLayer")

                      # Alimentation du dictionnaire des tooltip d'ORIGINE existantes"
                      if self.itemLayer in self._dicTooltipExiste :
                         itemLayerTooltip = self._dicTooltipExiste[self.itemLayer]
                      else :
                         itemLayerTooltip = self.itemLayer.toolTip()
                         self._dicTooltipExiste[self.itemLayer] = itemLayerTooltip 
                      # Alimentation du dictionnaire des tooltip d'ORIGINE existantes"

                      itemLayerTooltipNew, mFindMetadata_OR_itemLayerTooltipNew = truncate_metadata(itemLayerTooltip, self._activeTooltipWithtitle, self._langList)
                      itemLayerTooltipNew = itemLayerTooltipNew.replace("\n","<br>")
                      
                      if self._activeTooltip : # For disable modif tooltip 
                         if mFindMetadata_OR_itemLayerTooltipNew :
                            _border     = "style='border: 1px solid black;'"
                            _icon       = "<img width='30' src='" + self._iconSource + "'/>" 
                            mTableHtml  = "<table style='border=0' width=100%>"
                            mTableHtml += "<tr><td>" + itemLayerTooltipNew
                            mTableHtml += "</td></tr>"
                            #
                            if self._activeTooltipColor : 
                               if self._activeTooltipCadre :
                                  mTableHtml += "<tr><td style='color:" + self._activeTooltipColorText + ";' style='background-color:" + self._activeTooltipColorBackground + ";'" + _border + ">"
                               else :   
                                  mTableHtml += "<tr><td style='color:" + self._activeTooltipColorText + ";' style='background-color:" + self._activeTooltipColorBackground + ";'>"
                            else :   
                               if self._activeTooltipCadre :
                                  mTableHtml += "<tr><td " + _border + ">"
                               else :
                                  mTableHtml += "<tr><td>"
                            #
                            if self._activeTooltipLogo : mTableHtml += _icon + "<br>"
                            #
                            mTableHtml += mFindMetadata_OR_itemLayerTooltipNew     
                            mTableHtml += "</td></tr>"
                            mTableHtml += "</table>"
                            self.itemLayer.setToolTip(mTableHtml)
                      else :
                         self.itemLayer.setToolTip(itemLayerTooltip)
                   return True
                else:
                   return False
        else :
            return False
        return super(MyExploBrowser, self).eventFilter(source, event)
#==================================================
#==================================================
        
#==================================================
def executeSql(self, pointeur, _mKeySql, optionRetour = None) : 
    zMessError_Code, zMessError_Erreur, zMessError_Diag = '', '', ''
    pointeurBase = pointeur.cursor() 
       
    try :
      if isinstance(_mKeySql, tuple) :
         pointeurBase.execute(*_mKeySql)
      else :
         pointeurBase.execute(*_mKeySql)
      #--
      if optionRetour == None :
         result = None
      elif optionRetour == "fetchone" :
         resultTemp = pointeurBase.fetchone() 
         if resultTemp == None :
            raise NoReturnSql(_mKeySql.missing_mssg)  
         else :   
            result = resultTemp[0]
      elif optionRetour == "fetchall" :
         result = pointeurBase.fetchall()
      else :   
         result = pointeurBase.fetchall()
          
    finally :
      pointeurBase.close()   
      #-------------
    return result, zMessError_Code, zMessError_Erreur, zMessError_Diag

#==================================================
def transformeSql(self, mDic, mKeySql) :
    for key, value in mDic.items():
        if isinstance(value, bool) :
           mValue = str(value)
        elif (value is None) :
           mValue = "''"
        else :
           value = value.replace("'", "''")
           mValue =  str(value) 
        mKeySql = mKeySql.replace(key, mValue)
    return mKeySql

#==================================================
def updateUriWithPassword(self, mUri) :
        nameBase = mUri.database()
        #===========================
        if returnSiVersionQgisSuperieureOuEgale("3.10") : 
           #modification pour permettre d'utiliser les configurations du passwordManager (QGIS >=3.10)
           metadata = QgsProviderRegistry.instance().providerMetadata('postgres')

           if nameBase not in metadata.connections(False) :
              QMessageBox.critical(self, "Error", "new : There is no defined database connection for " + nameBase)
              mListConnectBase = []
           #modification pour permettre d'utiliser les configurations du passwordManager (QGIS >=3.10)

           #modification pour permettre d'utiliser les configurations du passwordManager (QGIS >=3.10)
           uri = QgsDataSourceUri(metadata.findConnection(nameBase).uri())
           #modification pour permettre d'utiliser les configurations du passwordManager (QGIS >=3.10)
           self.password = uri.password() or os.environ.get('PGPASSWORD')
        else :
           mSettings = QgsSettings()
           self.mConnectionSettingsKey = "/PostgreSQL/connections/{}".format(nameBase)
           mSettings.beginGroup(self.mConnectionSettingsKey)
           if not mSettings.contains("database") :
              QMessageBox.critical(self, "Error", "There is no defined database connection")
              mListConnectBase = []
           else :
              uri = QgsDataSourceUri()
              settingsList = ["service", "host", "port", "database", "username", "password"]
              self.service, self.host, self.port, self.database, self.username, self.password = map(lambda x: mSettings.value(x, "", type=str), settingsList)
           mSettings.endGroup()

        return self.password

#==================================================
def returnSiVersionQgisSuperieureOuEgale(_mVersTexte) :
    _mVersMax = 1000000  #Valeur max arbitraire
    try :
       _mVers = qgis.utils.Qgis.QGIS_VERSION_INT
    except : 
       _mVers = _mVersMax
    if _mVersTexte == "3.4.5" :
       _mBorne = 30405
       _mMess = "_mVers >= '3.4.5'"                    
    elif _mVersTexte == "3.10" : 
       _mBorne = 31006
       _mMess = "_mVers >= '3.10'" 
    elif _mVersTexte == "3.16" : 
       _mBorne = 31605
       _mMess = "_mVers >= '3.16'" 
    elif _mVersTexte == "3.18" : 
       _mBorne = 31801
       _mMess = "_mVers >= '3.18'"
    elif _mVersTexte == "3.20" : 
       _mBorne = 32002
       _mMess = "_mVers >= '3.20'"
    elif _mVersTexte == "3.21" : 
       _mBorne = 33000
       _mMess = "_mVers >= '3.21'"

    return True if _mVers >= _mBorne else False

#==================================================
def cleanMessError(mMess) :
    mContext = "CONTEXT:"
    mErreur  = "ERREUR:"  
    mHint    = "HINT:"  
    mDetail  = "DETAIL:"

    mMess = mMess.replace(mContext, "").replace(mErreur, "").replace(mHint, "<br><br>").replace(mDetail, "<br><br>")
    return mMess 
 
#==================================================
def dialogueMessageError(mTypeErreur, zMessError_Erreur):
    d = doerreur.Dialog(mTypeErreur, zMessError_Erreur)
    d.exec_()


#==================================================
def resizeIhm(self, l_Dialog, h_Dialog) :
    #----
    x, y = 10, 50
    larg, haut =  self.Dialog.width() -20, (self.Dialog.height() - 60 )
    self.tabWidget.setGeometry(QtCore.QRect(x, y, larg , haut))
    #----
    x, y = 0, 0 
    larg, haut =  self.tabWidget.width()-5, self.tabWidget.height()-25
    for elem in self.listeResizeIhm :
        elem.setGeometry(QtCore.QRect(x, y, larg, haut))
    #----
    try : 
       if hasattr(self, "monDock") :
          self.mMenuBarDialogLine1.setGeometry(QtCore.QRect(10,  0, self.tabWidget.width() , 23))
          self.mMenuBarDialogLine2.setGeometry(QtCore.QRect(10, 24, self.tabWidget.width() , 23))
       else:    
          self.mMenuBarDialogLine1.setGeometry(QtCore.QRect(10,  0, self.Dialog.width() - 20, 23))
          self.mMenuBarDialogLine2.setGeometry(QtCore.QRect(10, 24, self.Dialog.width() - 20, 23))
    except :
        pass 
    #----
    #----
    #Réinit les dimensions de l'IHM
    returnAndSaveDialogParam(self, "Save")
    self.mDic_LH = returnAndSaveDialogParam(self, "Load")
    self.Dialog.lScreenDialog, self.Dialog.hScreenDialog = int(self.mDic_LH["dialogLargeur"]), int(self.mDic_LH["dialogHauteur"])
    #----
    return  

#==================================================
#Lecture du fichier ini pour Tooltip
#==================================================
def loadParamTooltip(self) :
    mSettings = QgsSettings()
    mDicAutre = {}
    mSettings.beginGroup("PLUME")
    mSettings.beginGroup("Generale")
    mDicAutre["activeTooltip"]                = "false"
    mDicAutre["activeTooltipWithtitle"]       = "true"
    mDicAutre["activeTooltipLogo"]            = "true"
    mDicAutre["activeTooltipCadre"]           = "false"
    mDicAutre["activeTooltipColor"]           = "false"
    mDicAutre["activeTooltipColorText"]       = "#FFFFFF"
    mDicAutre["activeTooltipColorBackground"] = "#D88F92"
    for key, value in mDicAutre.items():
        if not mSettings.contains(key) :
           mSettings.setValue(key, value)
        else :
           mDicAutre[key] = mSettings.value(key)
                  
    mSettings.endGroup()
    mSettings.endGroup()
    return mDicAutre

#==================================================
#Lecture du fichier ini pour click before open IHM
#==================================================
def saveinitializingDisplay(mAction, layerBeforeClicked = None, mItem = None, mBrowser = "") :
    mSettings = QgsSettings()
    mDicAutre = {}
    mSettings.beginGroup("PLUME")
    mSettings.beginGroup("Generale")
    if mAction == "write" : 
       if layerBeforeClicked[0] != None and layerBeforeClicked[0] != "" :
          mDicAutre["layerBeforeClicked"]         = layerBeforeClicked[0].id() if layerBeforeClicked[1] == "qgis" else mItem if mItem != None else layerBeforeClicked[0]
          mDicAutre["layerBeforeClickedWho"]      = layerBeforeClicked[1]
          mDicAutre["layerBeforeClickedBrowser"]  = mBrowser
       else :   
          mDicAutre["layerBeforeClicked"]         = layerBeforeClicked[0]
          mDicAutre["layerBeforeClickedWho"]      = layerBeforeClicked[1]
          mDicAutre["layerBeforeClickedBrowser"]  = mBrowser
       #   
       for key, value in mDicAutre.items():
           mSettings.setValue(key, value)
       #---- for Tooltip
       mDicAutre = {}
       mDicAutre["activeTooltip"]                = "true"
       mDicAutre["activeTooltipWithtitle"]       = "true"
       mDicAutre["activeTooltipLogo"]            = "true"
       mDicAutre["activeTooltipCadre"]           = "false"
       mDicAutre["activeTooltipColor"]           = "false"

       for key, value in mDicAutre.items():
          if not mSettings.contains(key) :
             mSettings.setValue(key, value)
          else :
             mDicAutre[key] = mSettings.value(key)
       #---- for Tooltip color
       mSettings.endGroup()
       mSettings.beginGroup("BlocsColor")
       mDicAutre = {}
       mDicAutre["activeTooltipColorText"]       = "#000000"
       mDicAutre["activeTooltipColorBackground"] = "#fff4f2"

       for key, value in mDicAutre.items():
          if not mSettings.contains(key) :
             mSettings.setValue(key, value)
          else :
             mDicAutre[key] = mSettings.value(key)
       #---- for Tooltip

    elif mAction == "read" : 
       mDicAutre["layerBeforeClicked"]         = ""
       mDicAutre["layerBeforeClickedWho"]      = ""
       mDicAutre["layerBeforeClickedBrowser"]  = ""
       for key, value in mDicAutre.items():
           if not mSettings.contains(key) :
              mSettings.setValue(key, value)
           else :
              mDicAutre[key] = mSettings.value(key)
                  
    mSettings.endGroup()
    mSettings.endGroup()
    return

#==================================================
#Lecture du fichier ini pour dimensions Dialog
#==================================================
def returnAndSaveDialogParam(self, mAction):
    mDicAutre        = {}
    mDicAutreColor   = {}
    mDicAutrePolice  = {}
    mDicUserSettings = {}
    mDicCSW          = {}
    mSettings = QgsSettings()
    mSettings.beginGroup("PLUME")
    mSettings.beginGroup("Generale")
    
    if mAction == "Load" :
       #Ajouter si autre param
       valueDefautL = 810
       valueDefautH = 640
       valueDefautDisplayMessage = "dialogBox"
       valueDefautDurationBarInfo = 10
       valueDefautIHM = "dockFalse"
       valueDefautLayerBeforeClicked    = ""
       valueDefautLayerBeforeClickedWho = ""
       valueDefautLayerBeforeClickedBrowser = ""
       valueDefautVersion = ""
       mDicAutre["dialogLargeur"]   = valueDefautL
       mDicAutre["dialogHauteur"]   = valueDefautH
       mDicAutre["displayMessage"]  = valueDefautDisplayMessage
       mDicAutre["durationBarInfo"] = valueDefautDurationBarInfo
       mDicAutre["ihm"]             = valueDefautIHM
       mDicAutre["layerBeforeClicked"]        = valueDefautLayerBeforeClicked
       mDicAutre["layerBeforeClickedWho"]     = valueDefautLayerBeforeClickedWho
       mDicAutre["layerBeforeClickedBrowser"] = valueDefautLayerBeforeClickedBrowser
       mDicAutre["versionPlumeBibli"]     = valueDefautVersion
       #---- for Tooltip
       mDicAutre["activeTooltip"]                = "true"
       mDicAutre["activeTooltipWithtitle"]       = "true"
       mDicAutre["activeTooltipLogo"]            = "true"
       mDicAutre["activeTooltipCadre"]           = "false"
       mDicAutre["activeTooltipColor"]           = "false"
       #---- for Tooltip

       for key, value in mDicAutre.items():
           if not mSettings.contains(key) :
              mSettings.setValue(key, value)
           else :
              mDicAutre[key] = mSettings.value(key)
       #--                  
       mSettings.endGroup()
       mSettings.beginGroup("BlocsColor")
       #Ajouter si autre param
       
       mDicAutreColor["defaut"]                      = "#a38e63"
       mDicAutreColor["QGroupBox"]                   = "#a38e63"
       mDicAutreColor["QGroupBoxGroupOfProperties"]  = "#a38e63"
       mDicAutreColor["QGroupBoxGroupOfValues"]      = "#465f9d"
       mDicAutreColor["QGroupBoxTranslationGroup"]   = "#e18b76"
       mDicAutreColor["QTabWidget"]                  = "#cecece"
       mDicAutreColor["QLabelBackGround"]            = "#e3e3fd"
       mDicAutreColor["geomColor"]                   = "#a38e63"
       mDicAutreColor["geomEpaisseur"]               = "2"
       mDicAutreColor["geomPoint"]                   = "ICON_X"
       mDicAutreColor["geomPointEpaisseur"]          = "8"
       mDicAutreColor["geomZoom"]                    = "true"
       mDicAutreColor["geomPrecision"]               = "8"
       #---- for Tooltip
       mDicAutreColor["activeTooltipColorText"]       = "#000000"
       mDicAutreColor["activeTooltipColorBackground"] = "#fee9e9"
       #---- for Tooltip

       for key, value in mDicAutreColor.items():
           if not mSettings.contains(key) :
              mSettings.setValue(key, value)
           else :
              mDicAutreColor[key] = mSettings.value(key)           
       #----
       mDicAutre = {**mDicAutre, **mDicAutreColor}          
       #--                  

       mSettings.endGroup()
       mSettings.beginGroup("BlocsPolice")
       #Ajouter si autre param
       mDicAutrePolice["QEdit"] = "outset"
       mDicAutrePolice["QGroupBoxEpaisseur"] = 1
       mDicAutrePolice["QGroupBoxLine"]    = "dashed"
       mDicAutrePolice["QGroupBoxPolice"]  = "Marianne"
       mDicAutrePolice["QTabWidgetPolice"] = "Helvetica"

       for key, value in mDicAutrePolice.items():
           if not mSettings.contains(key) :
              mSettings.setValue(key, value)
           else :
              mDicAutrePolice[key] = mSettings.value(key)           
       #----
       mDicAutre = {**mDicAutre, **mDicAutrePolice}          

       #======================
       # liste des Paramétres UTILISATEURS
       mSettings.endGroup()
       mSettings.beginGroup("UserSettings")
       #Ajouter si autre param
       mDicUserSettings["language"]                = "fr"
       mDicUserSettings["translation"]             = "false"
       mDicUserSettings["langList"]                = ['fr', 'en']
       mDicUserSettings["geoideJSON"]              = "true"
       #----
       mDicUserSettings["preferedTemplate"]        = ""
       mDicUserSettings["enforcePreferedTemplate"] = ""
       mDicUserSettings["readHideBlank"]           = ""
       mDicUserSettings["readHideUnlisted"]        = ""
       mDicUserSettings["editHideUnlisted"]        = ""
       mDicUserSettings["readOnlyCurrentLanguage"] = ""
       mDicUserSettings["editOnlyCurrentLanguage"] = ""
       mDicUserSettings["labelLengthLimit"]        = ""
       mDicUserSettings["valueLengthLimit"]        = ""
       mDicUserSettings["textEditRowSpan"]         = ""
       mDicUserSettings["zoneConfirmMessage"]      = "true"
       mDicUserSettings["cleanPgDescription"]                = "never"
       mDicUserSettings["copyDctTitleToPgDescription"]       = "false"
       mDicUserSettings["copyDctDescriptionToPgDescription"] = "false"
       #----
       for key, value in mDicUserSettings.items():
           if not mSettings.contains(key) :
              mSettings.setValue(key, value)
           else :
              mDicUserSettings[key] = mSettings.value(key)           

       #----       
       #Pour les langues un peu de robustesse car théo gérer dans le lecture du Qgis3.ini
       if mDicUserSettings["language"] not in mDicUserSettings["langList"] : 
          mDicUserSettings["langList"].append(mDicUserSettings["language"])
          # Je re sauvegarde langList  
          mSettings.setValue("langList", mDicUserSettings["langList"])
       #Pour les langues un peu de robustesse car théo gérer dans le lecture du Qgis3.ini
       
       mDicAutre = {**mDicAutre, **mDicUserSettings}          
       # liste des Paramétres UTILISATEURS
       #======================

       #======================
       # liste des CSW
       mSettings.endGroup()
       mSettings.beginGroup("CSW")
       #Ajouter si autre param
       mDicCSW["urlCsw"]            =  ""
       #----
       for key, value in mDicCSW.items():
           if not mSettings.contains(key) :
              mSettings.setValue(key, value)
           else :
              mDicCSW[key] = mSettings.value(key)           
       mDicAutre = {**mDicAutre, **mDicCSW}          
       # liste des CSW
       #======================

    elif mAction == "Save" :
       mDicAutre["dialogLargeur"] = self.Dialog.width()
       mDicAutre["dialogHauteur"] = self.Dialog.height()
                 
       for key, value in mDicAutre.items():
           mSettings.setValue(key, value)

    mSettings.endGroup()
    mSettings.endGroup()    
    return mDicAutre

#==================================================
#==================================================
#Création GIF et Déplacement 
def addDeplaceGif(**kwargs) :
    if kwargs['_action'] == "ADD" :
       _movie = QtGui.QMovie(kwargs['_gif'])
       kwargs['_objet'].setMovie(_movie)
       _movie.start()
    kwargs['_objet'].setGeometry(QtCore.QRect(kwargs['_x'], kwargs['_y'], kwargs['_l'], kwargs['_h']))
    return

#==================================================
#Execute Pdf 
#==================================================
def execPdf(nameciblePdf):
    paramGlob = nameciblePdf            
    os.startfile(paramGlob)

    return            
#==================================================
def getThemeIcon(theName):
    myPath = CorrigePath(os.path.dirname(__file__))
    myDefPathIcons = myPath + "\\icons\\logo\\"
    myDefPath = myPath.replace("\\","/")+ theName
    myDefPathIcons = myDefPathIcons.replace("\\","/")+ theName
    myCurThemePath = QgsApplication.activeThemePath() + "/plugins/" + theName
    myDefThemePath = QgsApplication.defaultThemePath() + "/plugins/" + theName
    myQrcPath = "python/plugins/plume/" + theName
    if QFile.exists(myDefPath): return myDefPath
    elif QFile.exists(myDefPathIcons): return myDefPathIcons
    elif QFile.exists(myCurThemePath): return myCurThemePath
    elif QFile.exists(myDefThemePath): return myDefThemePath
    elif QFile.exists(myQrcPath): return myQrcPath
    else: return theName

#==================================================
def returnIcon( iconAdress) :
    iconSource = iconAdress
    iconSource = iconSource.replace("\\","/")
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap(iconSource), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    icon.actualSize(QSize(15, 15))
    return icon 

#==================================================
def CorrigePath(nPath):
    nPath = str(nPath)
    a = len(nPath)
    subC = "/"
    b = nPath.rfind(subC, 0, a)
    if a != b : return (nPath + "/")
    else: return nPath

#==================================================
def createFolder(mFolder):
    try:
       os.makedirs(mFolder)
    except OSError:
       pass
    return mFolder
    
#==================================================
#==================================================
def displayMess(mDialog, type,zTitre,zMess, level=Qgis.Critical, duration = 10):
    #type 1 = MessageBar
    #type 2 = QMessageBox
    if type == 1 :
       mDialog.barInfo.clearWidgets()
       mDialog.barInfo.pushMessage(zTitre, zMess, level=level, duration = duration)
    else :
       QMessageBox.information(None,zTitre,zMess)
    return  

#==================================================
def debugMess(type,zTitre,zMess, level=Qgis.Critical):
    #type 1 = MessageBar
    #type 2 = QMessageBox
    if type == 1 :
       qgis.utils.iface.messageBar().pushMessage(zTitre, zMess, level=level)
    else :
       QMessageBox.information(None,zTitre,zMess)
    return  

#==================================================
# FIN
#==================================================
