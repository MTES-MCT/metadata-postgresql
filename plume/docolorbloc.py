# (c) Didier  LECLERC 2021 CMSIG MTE-MCTRCT-Mer/SG/SNUM/UNI/DRC Site de Rouen
# créé sept 2021 

from PyQt5.QtWidgets import QDialog

from plume.colorbloc_ui import Ui_Dialog_ColorBloc

class Dialog(QDialog, Ui_Dialog_ColorBloc):
      def __init__(self, mDialog):
          QDialog.__init__(self)
          self.setupUiColorBloc(self, mDialog)

		
