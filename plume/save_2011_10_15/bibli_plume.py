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
def returnObjetsMeta(self, _schema, _table) :
    #**********************
    # Récupération champ commentaire
    mKeySql = pg_queries.query_get_table_comment(_schema, _table)
    old_description, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self.mConnectEnCoursPointeur, mKeySql, optionRetour = "fetchone")

    #**********************
    # schéma SHACL qui décrit les métadonnées communes
    shape = rdf_utils.load_shape()  #Only

    #**********************
    # vocabulaire - ontologies utilisées par les métadonnées communes
    vocabulary = rdf_utils.load_vocabulary() 

    #**********************
    # Mode a supprimer en test
    mode = None

    #**********************
    # Récupération fiche de métadonnée
    try:
       #       g = rdf_utils.metagraph_from_pg_description(src.read(), shape)
       metagraph = rdf_utils.metagraph_from_pg_description(old_description, shape)
    except:
    # dialogue avec l'utilisateur
    #...
	# si l'exécution n'est pas interrompue :
       metagraph = rdf_utils.metagraph_from_pg_description("", shape)

    #**********************
    # exemple de modèle de formulaire
    with Path(__path__[0] + r'\exemples\exemple_dict_modele_local.json').open(encoding='UTF-8') as src:
        template = json.loads(src.read())
    template = None
    #**********************
    # liste des champs de la table
    mKeySql = pg_queries.query_get_columns(_schema, _table)
    columns, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self.mConnectEnCoursPointeur, mKeySql, optionRetour = "fetchall")

    #**********************
    #Create Dict
    kwa = {}
    # ajout des arguments obligatoires
    kwa.update({'metagraph': metagraph,	'shape': shape,	'vocabulary': vocabulary})
    # ajout des arguments optionnels
    if template is not None:
       kwa.update({ 'template': template })
    #--   
    if columns is not None:
       kwa.update({ 'columns': columns })
    #--
    if mode is not None:
       kwa.update({ 'mode': mode })
    #--   
    d = rdf_utils.build_dict(**kwa)
    return template, d, shape, vocabulary, metagraph, metagraph
    
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
def test_interaction_sql(self) :

    mKeySql = pg_queries.query_get_table_comment(self.schema, self.table)
    #**********************
    r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self.mConnectEnCoursPointeur, mKeySql, optionRetour = "fetchone")
    # A SUPPRIMER
    self.textTest = "Délimitation simplifiée des départements de France métropolitaine pour représentation à petite échelle, conforme au code officiel géographique (COG) de l'INSEE au 1er janvier de l'année de référence." 
    for k, v in self.mDicObjetsInstancies.items() :
        if v['value'] == self.textTest :
           self.mDicObjetsInstancies[k]['main widget'].setText(str(r))
           break
    # A SUPPRIMER
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
         result = pointeurBase.fetchall()
      elif optionRetour == "fetchone" :
         result = pointeurBase.fetchone()[0]
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
    mDicAutre = {}
    mDicAutreColor = {}
    mDicAutrePolice = {}
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
       mDicAutre["dialogLargeur"]  = valueDefautL
       mDicAutre["dialogHauteur"]  = valueDefautH
       mDicAutre["displayMessage"] = valueDefautDisplayMessage
       mDicAutre["fileHelp"]       = valueDefautFileHelp
       mDicAutre["fileHelpPdf"]    = valueDefautFileHelpPdf
       mDicAutre["fileHelpHtml"]   = valueDefautFileHelpHtml
       mDicAutre["durationBarInfo"]= valueDefautDurationBarInfo
       mDicAutre["ihm"]            = valueDefautIHM

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
       mDicAutreColor["QGroupBox"]                   = "#BADCFF"
       mDicAutreColor["QGroupBoxGroupOfProperties"]  = "#7560FF"
       mDicAutreColor["QGroupBoxGroupOfValues"]      = "#00FF21"
       mDicAutreColor["QGroupBoxTranslationGroup"]   = "#0026FF"
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
