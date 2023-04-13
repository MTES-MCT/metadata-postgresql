# (c) Didier  LECLERC 2020 CMSIG MTE-MCTRCT-Mer/SG/SNUM/UNI/DRC Site de Rouen
# créé sept 2020 

from PyQt5.QtWidgets import QDialog

from plume.about import Ui_Dialog

class Dialog(QDialog, Ui_Dialog):
	def __init__(self):
		QDialog.__init__(self)
		self.setupUi(self)
		
