# (c) Didier  LECLERC 2020 CMSIG MTE-MCTRCT/SG/SNUM/UNI/DRC Site de Rouen
# créé sept 2021

from PyQt5 import QtCore, QtGui, QtWidgets, QtSvg
from PyQt5.QtWidgets import (QAction, QMenu , QApplication, QMessageBox, QFileDialog, QTextEdit, QLineEdit,  QMainWindow) 
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import *
                     
from qgis.core import QgsProject, QgsMapLayer, QgsVectorLayerCache, QgsFeatureRequest, QgsSettings, QgsDataSourceUri, QgsCredentials
from qgis.utils import iface

from plume.rdf.widgetsdict import WidgetsDict
from plume.rdf.metagraph import Metagraph, metagraph_from_file, copy_metagraph
from plume.rdf.utils import export_extension_from_format, import_formats, import_extensions_from_format
from plume.pg.description import PgDescription
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
    # liste des Paramétres UTILISATEURS
    return 
    
#==================================================
def returnObjetMetagraph(self, old_description) : return old_description.metagraph

#==================================================
def exportObjetMetagraph(self, schema, table, extension, mListExtensionExport) :
    #boite de dialogue Fichiers
    extStr = ""
    for elem in mListExtensionExport :
        modelExt = export_extension_from_format(elem)
        extStrExt = "*" + str(modelExt) + " "
        if elem !=  modelExt[1:] :
           extStrExt += "*." + str(elem) + " "
        extStr += ";;" + str(elem) + " (" + str(extStrExt) + ")"
    TypeList = extStr[2:]
    table = table.replace(".","_").replace(" ","_")
    InitDir = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') + "\\" + "METADATA_" + str(schema) + "_" + str(table) + "." + extension
    mDialogueSave = QFileDialog
    fileName = mDialogueSave.getSaveFileName(None,QtWidgets.QApplication.translate("plume_ui", "PLUME Export des fiches de métadonnées", None),InitDir,TypeList)[0]
    fileName, extension = os.path.splitext(fileName)[0], os.path.splitext(fileName)[1][1:]
    if fileName == "" : return
    #**********************
    # Export fiche de métadonnée
    try:
       self.metagraph.export(fileName, extension)
    except:
       zTitre = QtWidgets.QApplication.translate("plume_ui", "PLUME : Warning", None)
       zMess  = QtWidgets.QApplication.translate("plume_ui", "PLUME n'a pas réussi à exporter votre fiche de métadonnées.", None)
       displayMess(self.Dialog, (2 if self.Dialog.displayMessage else 1), zTitre, zMess, Qgis.Warning, self.Dialog.durationBarInfo)
    return  

#==================================================
def importObjetMetagraphCSW(self) :
    #boite de dialogue CSW
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
    fileName = QFileDialog.getOpenFileName(None,"Fiches de métadonnées",InitDir,TypeList)
    filepath = str(fileName[0]) if fileName[0] != "" else "" 
    if filepath == "" : return
    #**********************
    # Récupération fiche de métadonnée
    try:
       old_metagraph = self.metagraph
       metagraph  = metagraph_from_file(filepath, old_metagraph=old_metagraph)
    except:
       zTitre = QtWidgets.QApplication.translate("plume_ui", "PLUME : Warning", None)
       zMess  = QtWidgets.QApplication.translate("plume_ui", "PLUME n'a pas réussi à importer votre fiche de métadonnées.", None)
       displayMess(self.Dialog, (2 if self.Dialog.displayMessage else 1), zTitre, zMess, Qgis.Warning, self.Dialog.durationBarInfo)

       metagraph = None
    return metagraph 

#==================================================
def returnObjetTpl_label(self) :
    #**********************
    #Récupération de la liste des modèles
    mKeySql = (queries.query_list_templates(), (self.schema, self.table))
    self.templates, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self.mConnectEnCours, mKeySql, optionRetour = "fetchall")
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
    mKeySql = (queries.query_get_categories(), (tpl_label,))
    categories, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self.mConnectEnCours, mKeySql, optionRetour = "fetchall")
        
    # Génération de template
    self.template = template_utils.build_template(categories)

    # Récupération des TEMPLATES associés au modèle retenu
    mKeySql = (queries.query_template_tabs(), (tpl_label,))
    tabs , zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self.mConnectEnCours, mKeySql, optionRetour = "fetchall")
           
    # Génération de template
    self.template = TemplateDict(categories, tabs)
    return self.template
#==================================================
def returnObjetColumns(self, _schema, _table) :
    #**********************
    # liste des champs de la table
    mKeySql = queries.query_get_columns(_schema, _table)
    columns, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self.mConnectEnCours, mKeySql, optionRetour = "fetchall")
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
    old_description, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self.mConnectEnCours, mKeySql, optionRetour = "fetchone")
    return PgDescription(old_description)

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
           if _valueObjet['main widget type'] in ("QLineEdit") :
               value = _valueObjet['main widget'].text()
           elif _valueObjet['main widget type'] in ("QTextEdit") :
               value = _valueObjet['main widget'].toPlainText()
           elif _valueObjet['main widget type'] in ("QComboBox") :
               value = _valueObjet['main widget'].currentText()                   
           elif _valueObjet['main widget type'] in ("QDateEdit") :
               value = _valueObjet['main widget'].date().toString("yyyy-MM-dd")
           elif _valueObjet['main widget type'] in ("QDateTimeEdit") :
              value = _valueObjet['main widget'].date().toString("yyyy-MM-dd")
           elif _valueObjet['main widget type'] in ("QCheckBox") :
              value = True if _valueObjet['main widget'].isChecked() else False

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
    kind, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self.mConnectEnCours, mKeySql, optionRetour = "fetchone")
    #-    
    mKeySql = (queries.query_update_table_comment(_schema, _table, relation_kind=kind[0]), (new_pg_description,)) 
    r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self.mConnectEnCours, mKeySql, optionRetour = None)
    self.mConnectEnCours.commit()
    #-
    #Mettre à jour les descriptifs des champs de la table.    
    mKeySql = queries.query_update_columns_comments(_schema, _table, self.mDicObjetsInstancies)
    r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self.mConnectEnCours, mKeySql, optionRetour = None)
    self.mConnectEnCours.commit()
    #- Mettre à jour les descriptifs de la variable columns pour réaffichage
    self.columns = returnObjetColumns(self, self.schema, self.table)
    return  
    
#==================================================
def executeSql(pointeur, _mKeySql, optionRetour = None) :
    zMessError_Code, zMessError_Erreur, zMessError_Diag = '', '', ''
    pointeurBase = pointeur.cursor() 

    try :
      if isinstance(_mKeySql, tuple) :
         pointeurBase.execute(_mKeySql[0], _mKeySql[1])
      else :
         pointeurBase.execute(_mKeySql)
      #--
      if optionRetour == None :
         result = None
      elif optionRetour == "fetchone" :
         result = pointeurBase.fetchone()[0]
      elif optionRetour == "fetchall" :
         result = pointeurBase.fetchall()
      else :   
         result = pointeurBase.fetchall()
          
    except Exception as err:
      result = None
      zMessError_Code   = (str(err.pgcode) if hasattr(err, 'pgcode') else '')
      zMessError_Erreur = (str(err.pgerror) if hasattr(err, 'pgerror') else '')
      print("err.pgcode = %s" %(zMessError_Code))
      print("err.pgerror = %s" %(zMessError_Erreur))
      zMessError_Erreur = cleanMessError(zMessError_Erreur)
      mTypeErreur = "plume"
      dialogueMessageError(mTypeErreur, zMessError_Erreur )
      pointeurBase.close()   
      #-------------
    pointeurBase.close()   
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
        print(mUri.password())
        print(os.environ.get('PGPASSWORD'))
        nameBase = mUri.database()
        print(nameBase)
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
    mMess = mMess[0:mMess.find(mContext)].lstrip() if mMess.find(mContext) != -1 else mMess
    mMess = mMess[0:mMess.find(mErreur)].lstrip() + mMess[mMess.find(mErreur) + len(mErreur):].lstrip() if mMess.find(mErreur) != -1 else mMess
    mMess = mMess[0:mMess.find(mHint)].lstrip() + "<br><br>" + mMess[mMess.find(mHint) + len(mHint):].lstrip() if mMess.find(mHint) != -1 else mMess
    mMess = mMess[0:mMess.find(mDetail)].lstrip() + "<br><br>" + mMess[mMess.find(mDetail) + len(mDetail):].lstrip() if mMess.find(mDetail) != -1 else mMess
    return mMess 
 
#==================================================
def dialogueMessageError(mTypeErreur, zMessError_Erreur):
    d = doerreur.Dialog(mTypeErreur, zMessError_Erreur)
    d.exec_()


#==================================================
def resizeIhm(self, l_Dialog, h_Dialog) :
    #----
    x, y = 10, 25
    larg, haut =  self.Dialog.width() -20, (self.Dialog.height() - 40 )
    self.tabWidget.setGeometry(QtCore.QRect(x, y, larg , haut))
    #----
    x, y = 0, 0 
    larg, haut =  self.tabWidget.width()-5, self.tabWidget.height()-25
    for elem in self.listeResizeIhm :
        elem.setGeometry(QtCore.QRect(x, y, larg, haut))
    #----
    #----
    #Réinit les dimensions de l'IHM
    returnAndSaveDialogParam(self, "Save")
    self.mDic_LH = returnAndSaveDialogParam(self, "Load")
    self.Dialog.lScreenDialog, self.Dialog.hScreenDialog = int(self.mDic_LH["dialogLargeur"]), int(self.mDic_LH["dialogHauteur"])
    #----
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
       valueDefautFileHelp  = "html"
       valueDefautFileHelpPdf   = "https://snum.scenari-community.org/Asgard/PDF/GuideAsgardManager"
       valueDefautFileHelpHtml  = "https://snum.scenari-community.org/Asgard/Documentation/#SEC_AsgardManager"
       valueDefautDurationBarInfo = 10
       valueDefautIHM = "window"
       valueDefautToolBarDialog = "picture"
       mDicAutre["dialogLargeur"]   = valueDefautL
       mDicAutre["dialogHauteur"]   = valueDefautH
       mDicAutre["displayMessage"]  = valueDefautDisplayMessage
       mDicAutre["fileHelp"]        = valueDefautFileHelp
       mDicAutre["fileHelpPdf"]     = valueDefautFileHelpPdf
       mDicAutre["fileHelpHtml"]    = valueDefautFileHelpHtml
       mDicAutre["durationBarInfo"] = valueDefautDurationBarInfo
       mDicAutre["ihm"]             = valueDefautIHM
       mDicAutre["toolBarDialog"]   = valueDefautToolBarDialog
       for key, value in mDicAutre.items():
           if not mSettings.contains(key) :
              mSettings.setValue(key, value)
           else :
              mDicAutre[key] = mSettings.value(key)
       #--                  
       mSettings.endGroup()
       mSettings.beginGroup("BlocsColor")
       #Ajouter si autre param
       mDicAutreColor["defaut"]                      = "#958B62"
       mDicAutreColor["QGroupBox"]                   = "#958B62"
       mDicAutreColor["QGroupBoxGroupOfProperties"]  = "#958B62"
       mDicAutreColor["QGroupBoxGroupOfValues"]      = "#5770BE"
       mDicAutreColor["QGroupBoxTranslationGroup"]   = "#FF8D7E"
       mDicAutreColor["QTabWidget"]                  = "#958B62"
       mDicAutreColor["QLabelBackGround"]            = "#BFEAE2"

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
       mDicCSW["urlCswDefaut"]   =  'http://ogc.geo-ide.developpement-durable.gouv.fr/csw/harvestable-dataset'
       mDicCSW["urlCswIdDefaut"] =  'fr-120066022-jdd-23d6b4cd-5a3b-4e10-83ae-d8fdad9b04ab'
       mDicCSW["urlCsw"]         =  ''
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
def returnVersion() : return "version 0.2.8"

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
