# (c) Didier  LECLERC 2021 CMSIG MTE-MCTRCT-Mer/SG/SNUM/UNI/DRC Site de Rouen
# créé 2022

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QDialog, QTreeWidgetItemIterator
from qgis.core import *

from .importcsw import Ui_Dialog_ImportCSW
from plume.config import (VALUEDEFAUTFILEHELP, VALUEDEFAUTFILEHELPPDF, VALUEDEFAUTFILEHELPHTML, URLCSWDEFAUT, URLCSWIDDEFAUT)  

class Dialog(QDialog, Ui_Dialog_ImportCSW):
      def __init__(self, Dialog):
          QDialog.__init__(self)
          self.setupUiImportCSW(self, Dialog)

      def reject(self):
          try :
            self.saveUrlCsw()
          except:
            pass

          self.hide() 
          
      def saveUrlCsw(self) :
          mDicCSW          = {}
          mSettings = QgsSettings()
          mSettings.beginGroup("PLUME")
          #======================
          # liste des CSW
          mSettings.beginGroup("CSW")
          #Ajouter si autre param
          mDicCSW["urlCsw"] =  ''
          iterator = QTreeWidgetItemIterator(self.mTreeCSW)
          _mListCSW = []
          while iterator.value() :
             itemValueText = iterator.value().text(0)
             if itemValueText not in URLCSWDEFAUT and itemValueText != self.mTreeCSW.mLibNodeUrlDefaut : 
                _mListCSW.append(itemValueText)
             iterator += 1
          mDicCSW["urlCsw"] =  ",".join(_mListCSW)
          
          #----
          for key, value in mDicCSW.items():
              mSettings.setValue(key, value)
          # liste des CSW
          #----
          #Réinitialise la variable du QGIS3.INI
          self.Dialog.urlCsw   = mDicCSW["urlCsw"]
          #======================
          mSettings.endGroup()
          mSettings.endGroup()
          return    
                 
		
