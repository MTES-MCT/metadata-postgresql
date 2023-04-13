# (c) Didier  LECLERC 2021 CMSIG MTE-MCTRCT-Mer/SG/SNUM/UNI/DRC Site de Rouen
# créé 2022

from PyQt5.QtWidgets import QDialog

from plume.bibli_plume import ( returnAndSaveDialogParam )

from plume.createtemplate import Ui_Dialog_CreateTemplate

class Dialog(QDialog, Ui_Dialog_CreateTemplate):
      def __init__(self, Dialog):
          QDialog.__init__(self)
          self.setupUiCreateTemplate(self, Dialog)

          return    

      def reject(self):
          returnAndSaveDialogParam(self, "SaveTemplate", self.width(), self.height())

          self.hide()                 
		
