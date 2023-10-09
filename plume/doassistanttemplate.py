# (c) Didier  LECLERC 2021 CMSIG MTE-MCTRCT-Mer/SG/SNUM/UNI/DRC Site de Rouen
# créé 2022

from PyQt5.QtWidgets import QDialog
from qgis.core import ( QgsSettings )

from plume.assistanttemplate import Ui_Dialog_AssistantTemplate

class Dialog(QDialog, Ui_Dialog_AssistantTemplate):
      def __init__(self, DialogCreateTemplate, DialogPlume, _buttonAssistant, mattrib, modCat_Attrib, mDicEnum, mLabel, mHelp, keyAncetre_ModeleCategorie_Modele_Categorie_Onglet):      # DialogCreateTemplate, DialogPlume
          QDialog.__init__(self)
          self.setupUiAssistantTemplate(self, DialogCreateTemplate, DialogPlume, _buttonAssistant, mattrib, modCat_Attrib, mDicEnum, mLabel, mHelp, keyAncetre_ModeleCategorie_Modele_Categorie_Onglet)
          return    

      #==================================================
      def reject(self):
          try :
             self.saveDimDialog(self.width(), self.height())
          except :
             pass

          self.hide()                 

      #==================================================
      def saveDimDialog(self, templateWidth = None, templateHeight = None) :
          mSettings = QgsSettings()
          mSettings.beginGroup("PLUME")
          mSettings.beginGroup("Generale")
          
          mDicAutre        = {}
          mDicAutre["dialogLargeurAssistantTemplate"] = templateWidth
          mDicAutre["dialogHauteurAssistantTemplate"] = templateHeight
                       
          for key, value in mDicAutre.items():
              mSettings.setValue(key, value)

          mSettings.endGroup()
          mSettings.endGroup()    
          return
		
