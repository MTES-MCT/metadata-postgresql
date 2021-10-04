# (c) Didier  LECLERC 2020 CMSIG MTE-MCTRCT/SG/SNUM/UNI/DRC Site de Rouen
# créé sept 2021

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QDialog
from qgis.core import *

from .postmeta_ui import Ui_Dialog_postmeta
from . import bibli_postmeta
from .bibli_postmeta import *

class Dialog(QDialog, Ui_Dialog_postmeta):
      def __init__(self):
          QDialog.__init__(self)
          self.setupUi(self)

      def reject(self):
          try :
            bibli_postmeta.returnAndSaveDialogParam(self, "Save")
          except:
            pass

          self.hide()        
