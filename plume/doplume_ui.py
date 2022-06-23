# (c) Didier  LECLERC 2020 CMSIG MTE-MCTRCT/SG/SNUM/UNI/DRC Site de Rouen
# créé sept 2021

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QDialog
from qgis.core import *

from .plume_ui import Ui_Dialog_plume
from . import bibli_plume
from .bibli_plume import *

class Dialog(QDialog, Ui_Dialog_plume):
      def __init__(self, _dicTooltipExiste):
          QDialog.__init__(self)
          self.setupUi(self, _dicTooltipExiste)

      def reject(self):
          try :
            bibli_plume.returnAndSaveDialogParam(self, "Save")
          except:
            pass
            
          self.hide()   
          