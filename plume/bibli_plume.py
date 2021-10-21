# (c) Didier  LECLERC 2020 CMSIG MTE-MCTRCT/SG/SNUM/UNI/DRC Site de Rouen
# créé sept 2021

from PyQt5 import QtCore, QtGui, QtWidgets, QtSvg
from PyQt5.QtWidgets import (QAction, QMenu , QApplication, QMessageBox, QFileDialog, QTextEdit, QLineEdit,  QMainWindow) 
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import *
                     
from qgis.core import QgsProject, QgsMapLayer, QgsVectorLayerCache, QgsFeatureRequest, QgsSettings, QgsDataSourceUri, QgsCredentials
 
from qgis.utils import iface
import psycopg2
from . import doerreur

from psycopg2 import sql

import re, uuid
import json
from pathlib import Path
from .bibli_pg  import pg_queries
from .bibli_pg  import template_utils
from .bibli_rdf import rdf_utils,  __path__

from qgis.gui import (QgsAttributeTableModel, QgsAttributeTableView, QgsLayerTreeViewMenuProvider, QgsAttributeTableFilterModel)
from qgis.utils import iface

from qgis.core import *
from qgis.gui import *
import qgis                              
import os                       
import datetime
import os.path
import time

#========================================================
#========================================================
def dicListSql(mKeySql):
    mdicListSql = {}

    #------------------
    # TESTS EN COURS
    #-----------------
    #Fonction tests 
    mdicListSql['Fonction_Tests'] = ("""
                  SELECT nombase, schema, nomobjet, typeobjet, etat FROM z_replique.replique;
                                          """) 
    mdicListSql['Fonction_Tests_SELECT'] = (""" SELECT * FROM "#schema#"."#table#"; """) 

    return  mdicListSql[mKeySql]

#==================================================
def returnObjetVocabulary() :
    #**********************
    # vocabulaire - ontologies utilisées par les métadonnées communes
    vocabulary = rdf_utils.load_vocabulary()
    return vocabulary 

#==================================================
def returnObjetShape() :
    #**********************
    # schéma SHACL qui décrit les métadonnées communes
    shape = rdf_utils.load_shape()
    return shape 

#==================================================
def returnObjetMetagraph(self, old_description) :
    #**********************
    # Récupération fiche de métadonnée
    try:
       #       g = rdf_utils.metagraph_from_pg_description(src.read(), shape)
       metagraph = rdf_utils.metagraph_from_pg_description(old_description, self.shape)
    except:
       # dialogue avec l'utilisateur  
       # La fonction metagraph_from_pg_description() renverra un graphe vide si le descriptif PostgreSQL ne contenait pas les balises <METADATA> et </METADATA> 
       # entre lesquelles est supposé se trouver le JSON-LD contenant les métadonnées. 
       # C'est typiquement ce qui arrivera lorsque les métadonnées n'ont pas encore été rédigées.
       # Si les balises sont présentes, mais ne contiennent pas un JSON valide, la fonction échouera sur une erreur json.decoder.JSONDecodeError. 
       # Dans ce cas, on pourra proposer à l'utilisateur de choisir entre abandonner l'ouverture de la fiche de métadonnées 
       #ou ouvrir une fiche vierge à la place.si entre les ba:lise
       #...
       # si l'exécution n'est pas interrompue :
       metagraph = rdf_utils.metagraph_from_pg_description("", self.shape)
    return metagraph 

#==================================================
def returnObjetTpl_label(self) :
    #**********************
    #Récupération de la liste des modèles
    mKeySql = (pg_queries.query_list_templates(), (self.schema, self.table))
    self.templates, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self.mConnectEnCoursPointeur, mKeySql, optionRetour = "fetchall")
    self.templateLabels = [t[0] for t in self.templates]    # templateLabels ne contient que les libellés des templates

    # Sélection automatique du modèle
    templateLabels = self.templateLabels
    if self.preferedTemplate and self.enforcePreferedTemplate and templateLabels and self.preferedTemplate in templateLabels :
       tpl_label = self.preferedTemplate
    else : 
       tpl_label = template_utils.search_template(self.metagraph, self.templates)

    return tpl_label 

#==================================================
# == Génération des CATEGORIES, TEMPLATE, TABS
def generationTemplateAndTabs(self, tpl_label):
    # Récupération des CATEGORIES associées au modèle retenu
    mKeySql = (pg_queries.query_get_categories(), (tpl_label,))
    categories, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self.mConnectEnCoursPointeur, mKeySql, optionRetour = "fetchall")
        
    # Génération de template
    self.template = template_utils.build_template(categories)

    # Récupération des TEMPLATES associés au modèle retenu
    mKeySql = (pg_queries.query_template_tabs(), (tpl_label,))
    tabs , zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self.mConnectEnCoursPointeur, mKeySql, optionRetour = "fetchall")
           
    # Génération de templateTabs
    self.templateTabs = template_utils.build_template_tabs(tabs)
    return self.template, self.templateTabs 

#==================================================
def returnObjetColumns(self, _schema, _table) :
    #**********************
    # liste des champs de la table
    mKeySql = pg_queries.query_get_columns(_schema, _table)
    columns, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self.mConnectEnCoursPointeur, mKeySql, optionRetour = "fetchall")
    return columns 

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
    mKeySql = pg_queries.query_get_table_comment(_schema, _table)
    old_description, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self.mConnectEnCoursPointeur, mKeySql, optionRetour = "fetchone")
    return old_description

#==================================================
def returnObjetsMeta(self, _schema, _table) :
    #**********************
    #Create Dict
    kwa = {}
    # ajout des arguments obligatoires
    kwa.update({'metagraph': self.metagraph,	'shape': self.shape,	'vocabulary': self.vocabulary})
    # ajout des arguments optionnels
    if self.template is not None:
       kwa.update({ 'template': self.template })
    #--   
    if self.columns is not None:
       kwa.update({ 'columns': self.columns })
    #--
    if self.mode is not None:
       kwa.update({ 'mode': self.mode })
    #--
    if self.translation is not None and self.mode == "edit" :
       kwa.update({ 'translation': self.translation })
    #--   
    d = rdf_utils.build_dict(**kwa)
    return d

#==================================================
def saveMetaIhm(self, _schema, _table) :
    #---------------------------
    # Gestion des langues
    _language = 'fr'

    #-    
    # Enregistrer dans le dictionnaire de widgets les valeurs contenues dans les widgets de saisie.
    for _keyObjet, _valueObjet in self.mDicObjetsInstancies.items() :
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

        if _valueObjet['object'] == "edit" and not (_valueObjet['hidden'] or _valueObjet['hidden M']): 
           self.mDicObjetsInstancies.update_value(_keyObjet, value)
    #-    
    #Générer un graphe RDF à partir du dictionnaire de widgets actualisé        
    self.metagraph = self.mDicObjetsInstancies.build_graph(self.vocabulary, language=_language) 
    #-    
    #Créer une version actualisée du descriptif PostgreSQL de l'objet.   
    new_pg_description = rdf_utils.update_pg_description(self.comment, self.metagraph) 
    self.comment = new_pg_description
    # une requête de mise à jour du descriptif.
    mKeySql = pg_queries.query_get_relation_kind(_schema, _table) 
    kind, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self.mConnectEnCoursPointeur, mKeySql, optionRetour = "fetchone")
    #-    
    mKeySql = (pg_queries.query_update_table_comment(_schema, _table, relation_kind=kind[0]), (new_pg_description,)) 
    r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self.mConnectEnCoursPointeur, mKeySql, optionRetour = None)
    self.mConnectEnCours.commit()
    #-
    #Mettre à jour les descriptifs des champs de la table.    
    mKeySql = pg_queries.query_update_columns_comments(_schema, _table, self.mDicObjetsInstancies)
    r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self.mConnectEnCoursPointeur, mKeySql, optionRetour = None)
    self.mConnectEnCours.commit()
    return  
    
#==================================================
def executeSql(pointeurBase, _mKeySql, optionRetour = None) :
    zMessError_Code, zMessError_Erreur, zMessError_Diag = '', '', ''
    QApplication.instance().setOverrideCursor(Qt.WaitCursor) 

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
      QApplication.instance().setOverrideCursor(Qt.ArrowCursor) 
      result = None
      zMessError_Code   = (str(err.pgcode) if hasattr(err, 'pgcode') else '')
      zMessError_Erreur = (str(err.pgerror) if hasattr(err, 'pgerror') else '')
      print("err.pgcode = %s" %(zMessError_Code))
      print("err.pgerror = %s" %(zMessError_Erreur))
      zMessError_Erreur = cleanMessError(zMessError_Erreur)
      mListeErrorCode = ["42501", "P0000", "P0001", "P0002", "P0003", "P0004"] 
      if zMessError_Code in [ mCodeErreur for mCodeErreur in mListeErrorCode] :   #Erreur PLUME
         mTypeErreur = "plumeGEREE" if dicExisteExpRegul(self, 'Search_0', zMessError_Erreur) else "plumeNONGEREE"
      else : 
         mTypeErreur = "plume"

      dialogueMessageError(mTypeErreur, zMessError_Erreur )   
      #-------------
    QApplication.instance().setOverrideCursor(Qt.ArrowCursor) 
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
       mDicUserSettings["preferedTemplate"]        = "Basique"
       mDicUserSettings["enforcePreferedTemplate"] = "false"
       mDicUserSettings["readHideBlank"]           = "true"
       mDicUserSettings["readHideUnlisted"]        = "true"
       mDicUserSettings["editHideUnlisted"]        = "false"
       mDicUserSettings["language"]                = "fr"
       mDicUserSettings["translation"]             = "false"
       mDicUserSettings["langList"]                = ['fr', 'en']
       mDicUserSettings["readOnlyCurrentLanguage"] = "true"
       mDicUserSettings["editOnlyCurrentLanguage"] = "false"
       mDicUserSettings["labelLengthLimit"]        = 25
       mDicUserSettings["valueLengthLimit"]        = 65
       mDicUserSettings["textEditRowSpan"]         = 6
       #----
       for key, value in mDicUserSettings.items():
           if not mSettings.contains(key) :
              mSettings.setValue(key, value)
           else :
              mDicUserSettings[key] = mSettings.value(key)           
       #----
       mDicAutre = {**mDicAutre, **mDicUserSettings}          
       # liste des Paramétres UTILISATEURS
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
def returnVersion() : return "version 0.1.0"

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
