# (c) Didier  LECLERC 2020 CMSIG MTE-MCTRCT-Mer/SG/SNUM/UNI/DRC Site de Rouen
# créé sept 2020 

from PyQt5.QtWidgets import QDialog

from plume.erreur_ui import Ui_Dialog

class Dialog(QDialog, Ui_Dialog):
      def __init__(self, mTypeErreur, zMessError_Erreur):
          QDialog.__init__(self)
          self.zMessError_Erreur = zMessError_Erreur
          self.mTypeErreur = mTypeErreur
          self.setupUi(self, self.mTypeErreur, self.zMessError_Erreur)

		
