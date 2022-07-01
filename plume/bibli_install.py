# (c) Didier  LECLERC 2020 CMSIG MTE-MCTRCT/SG/SNUM/UNI/DRC Site de Rouen
# créé sept 2021
import os.path
import subprocess
import logging
import time
from qgis.core import QgsSettings
from PyQt5 import QtCore, QtGui, QtWidgets 
from PyQt5.Qt import *
from plume.config import (PLUME_VERSION)

from PyQt5.QtWidgets import QMessageBox 
#==================================================
def manageLibrary(mVersionPlume, mVersionPlumeBibli) :
    if mVersionPlume != mVersionPlumeBibli :
       mPath = os.path.dirname(__file__)
       mPathPerso = mPath.replace("\\","/") + "/requirements.txt"
       #----------
       comptBibli = 0
       with open(mPathPerso,"r") as fileRequirement :
            for zLigne in fileRequirement :
                if "==" in zLigne : comptBibli += 1
       if comptBibli < 5 : comptBibli = 5   #Minimum 5
       #----------
       zMessTitle      = QtWidgets.QApplication.translate("patienter_ui", "Installing Plume", None) + "  " + str(PLUME_VERSION)
       zMessConfirme   = QtWidgets.QApplication.translate("patienter_ui", "Updating Python libraries in progress...", None)
       zMessConfirme2  = QtWidgets.QApplication.translate("patienter_ui", "This operation may take a few minutes.", None)
       zMessConfirme3  = QtWidgets.QApplication.translate("patienter_ui", "Wait ........", None)
       #----------
       monHtml = zMessConfirme + "\n\n" + zMessConfirme2  + "\n\n" + zMessConfirme3
       #----------
       managerPatienter = ManagerPatienter(zMessTitle, monHtml)
       num = managerPatienter.prgr_dialog.maximum() / 2
       #------ PIP ----
       for i in range(int(num)) :
           managerPatienter.prgr_dialog.setValue(int(i))
           time.sleep(0.05)
       if not updatePip() : managerPatienter.prgr_dialog.setLabelText(monHtml + "\n\n" + QtWidgets.QApplication.translate("bibli_install", "pip has not been updated."))
       #------ PIP ----
       #------ BIBLI ----
       managerPatienter.startBibli(num, comptBibli)
       if not updateRequierement(mPathPerso) :
          managerPatienter.prgr_dialog.setValue(100)
          _messError  = QtWidgets.QApplication.translate("bibli_install", "One or more libraries were not installed correctly.")
          _messError += "\n\n" + QtWidgets.QApplication.translate("bibli_install", "Plume could malfunction.")
          _messError += "\n\n" + QtWidgets.QApplication.translate("bibli_install", "Please contact support.")
          managerPatienter.prgr_dialog.setLabelText(_messError)
          _pathIcons = os.path.dirname(__file__) + "/icons/logo"
          iconSource          = _pathIcons + "/plume.svg"
          icon = QtGui.QIcon()
          icon.addPixmap(QtGui.QPixmap(iconSource), QtGui.QIcon.Normal, QtGui.QIcon.Off)
          _QMess = QMessageBox(QMessageBox.Information, zMessTitle, _messError )
          _QMess.setWindowIcon(icon)
          _QMess.exec_()
       else :
          managerPatienter.prgr_dialog.setValue(100)
          #==================================================
          #Sauvegarde de la version de Plume pour les bibliothèques
          mSettings = QgsSettings()
          mDicAutre = {}
          mSettings.beginGroup("PLUME")
          mSettings.beginGroup("Generale")
          mDicAutre["versionPlumeBibli"] = mVersionPlume
          for key, value in mDicAutre.items():
              mSettings.setValue(key, value)
          mSettings.endGroup()
          mSettings.endGroup()
          #------ BIBLI ----
    return

#==================================================
def updatePip() :
    si = subprocess.STARTUPINFO() 
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    try:
       _sortie = subprocess.run(['python3', '-m', 'pip', 'install', '--upgrade', '--retries', '1', '--timeout', '5', '--quiet', '--quiet', '--quiet', 'pip'], check=True, startupinfo=si) 
    except subprocess.CalledProcessError as err :
       return  False
    return True

#==================================================
def updateRequierement(mPathPerso) :
    si = subprocess.STARTUPINFO() 
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    try:
       _sortie = subprocess.run(['python3', '-m', 'pip', 'install', '-r', mPathPerso], check=True, startupinfo=si)
    except subprocess.CalledProcessError as err:
       return  False
    return True
        
#==================================================
class ManagerPatienter() :
   #------
   def __init__(self, _title, _mess) :
       _pathIcons = os.path.dirname(__file__) + "/icons/logo"
       iconSource          = _pathIcons + "/plume.svg"
       icon = QtGui.QIcon()
       icon.addPixmap(QtGui.QPixmap(iconSource), QtGui.QIcon.Normal, QtGui.QIcon.Off)
       #
       self.prgr_dialog = QProgressDialog(_mess, "",  0, 100)
       self.prgr_dialog.setWindowModality(Qt.WindowModal)
       self.prgr_dialog.setWindowIcon(icon)
       self.prgr_dialog.setFixedSize(300, 170)
       self.prgr_dialog.setMinimumDuration(0)
       self.prgr_dialog.mCancelButton = self.prgr_dialog.findChild(QPushButton)
       self.prgr_dialog.mCancelButton.setVisible(False)
       self.prgr_dialog.setCancelButtonText("OK")
       self.prgr_dialog.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
       self.prgr_dialog.setWindowFlag(Qt.WindowCloseButtonHint, False)
       self.prgr_dialog.setWindowTitle(_title)
       self.prgr_dialog.setAutoReset(False)
       self.prgr_dialog.setAutoClose(False)
       self.prgr_dialog.show()

   #------
   def startBibli(self, _num, _comptBibli) :
       i    = int(_num)
       step = _num / _comptBibli
       totalBibli = 100
       while i <= totalBibli :
           self.prgr_dialog.setValue(int(i))
           time.sleep(0.05)
           i += step
       return            

#==================================================
#==================================================
# FIN
#==================================================
