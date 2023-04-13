# (c) Didier  LECLERC 2020 CMSIG MTE-MCTRCT/SG/SNUM/UNI/DRC Site de Rouen
# créé sept 2021


from PyQt5.QtWidgets import QDialog

from .plume_ui import Ui_Dialog_plume
from plume.bibli_plume import ( returnAndSaveDialogParam )

class Dialog(QDialog, Ui_Dialog_plume):
      def __init__(self, _dicTooltipExiste):
          QDialog.__init__(self)
          self.setupUi(self, _dicTooltipExiste)

      def reject(self):
          try :
            returnAndSaveDialogParam(self, "Save")
          except:
            pass
            
          self.hide()   
          