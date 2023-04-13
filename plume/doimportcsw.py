# (c) Didier  LECLERC 2021 CMSIG MTE-MCTRCT-Mer/SG/SNUM/UNI/DRC Site de Rouen
# créé 2022

from PyQt5.QtWidgets import QDialog, QTreeWidgetItemIterator

from plume.importcsw import Ui_Dialog_ImportCSW
from plume.config import ( URLCSWDEFAUT )  
from qgis.core import ( QgsSettings )

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
          mDicCSW["liburlCsw"] =  ''
          iterator = QTreeWidgetItemIterator(self.mTreeCSW)
          _mListCSW = []
          _mListLibCSW = []
          while iterator.value() :
             itemValueText = iterator.value().text(1)
             itemValueLibText = iterator.value().text(0)
             if itemValueText != "" : 
                if itemValueText not in URLCSWDEFAUT.split(",") and itemValueText    != self.mTreeCSW.mLibNodeUrlDefaut and itemValueText    != self.mTreeCSW.mLibNodeUrlUser  :
                   _mListCSW.append(itemValueText)
                   _mListLibCSW.append(itemValueLibText)
             iterator += 1
          mDicCSW["urlCsw"] =  ",".join(_mListCSW)
          mDicCSW["liburlCsw"] =  ",".join(_mListLibCSW)
          
          #----
          for key, value in mDicCSW.items():
              mSettings.setValue(key, value)
          # liste des CSW
          #----
          #Réinitialise la variable du QGIS3.INI
          self.Dialog.urlCsw      = mDicCSW["urlCsw"]
          self.Dialog.libUrlCsw   = mDicCSW["liburlCsw"]
          #======================
          mSettings.endGroup()
          mSettings.endGroup()
          return    
                 
		
