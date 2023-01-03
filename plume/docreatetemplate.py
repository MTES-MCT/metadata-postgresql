# (c) Didier  LECLERC 2021 CMSIG MTE-MCTRCT-Mer/SG/SNUM/UNI/DRC Site de Rouen
# créé 2022

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QDialog, QTreeWidgetItemIterator
from qgis.core import *
from . import bibli_plume

from .createtemplate import Ui_Dialog_CreateTemplate

class Dialog(QDialog, Ui_Dialog_CreateTemplate):
      def __init__(self, Dialog):
          QDialog.__init__(self)
          self.setupUiCreateTemplate(self, Dialog)

          return    

      def reject(self):
          bibli_plume.returnAndSaveDialogParam(self, "SaveTemplate", self.width(), self.height())

          self.hide()                 
		
