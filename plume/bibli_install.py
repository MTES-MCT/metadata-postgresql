# (c) Didier  LECLERC 2020 CMSIG MTE-MCTRCT/SG/SNUM/UNI/DRC Site de Rouen
# créé sept 2021
import os.path
import subprocess
import time
from qgis.core import QgsSettings
from PyQt5 import QtCore, QtGui, QtWidgets 
from plume.config import (PLUME_VERSION) 
from PyQt5.QtWidgets import ( QMessageBox, QProgressDialog, QPushButton )
from qgis.core import QgsSettings
import qgis
 
#==================================================
def manageLibrary() :
    mVersionPlume = PLUME_VERSION
    #--                  
    mSettings = QgsSettings()
    mSettings.beginGroup("PLUME")
    mSettings.beginGroup("Generale")
    version_cur        = qgis.utils.Qgis.QGIS_VERSION.split(".")
    python_version_cur = "-".join([ version_cur[0], version_cur[1], version_cur[2].split("-")[0] ])
    
    mDicAutre        = {}
    valueDefautVersion = ""
    valueDefautVersion_python_version = ""
    mDicAutre["versionPlumeBibli"]    = valueDefautVersion
    valueDefautVersion_python_version = mDicAutre["versionPlumeBibli"]
    mDicAutre[python_version_cur]     = valueDefautVersion_python_version
    #--                  
    for key, value in mDicAutre.items():
        if not mSettings.contains(key) :
           mSettings.setValue(key, value)
        else :
           mDicAutre[key] = mSettings.value(key)
    #--                  
    mSettings.endGroup()
    mVersionPlumeBibli = mDicAutre["versionPlumeBibli"]
    mPython_version    = mDicAutre[python_version_cur]
    #-- #issue 125                 
    update_lib = False
    if not (mVersionPlume != mVersionPlumeBibli or mVersionPlume != mPython_version) : 
       try:
          import plume.rdf.rdflib
       except:
          update_lib = True
    #-- #issue 125                 
    if (mVersionPlume != mVersionPlumeBibli or mVersionPlume != mPython_version) or update_lib :
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
       num = managerPatienter.prgr_dialog.maximum() / 4
       #------ PIP ----
       for i in range(int(num)) :
           managerPatienter.prgr_dialog.setValue(int(i))
           time.sleep(0.05)
       if not updatePip() : managerPatienter.prgr_dialog.setLabelText(monHtml + "\n\n" + QtWidgets.QApplication.translate("bibli_install", "pip has not been updated.", None))
       #------ PIP ----
       #------ BIBLI ----
       managerPatienter.startBibli(num, comptBibli, 66)
       if not updateRequierement(mPathPerso) :
          managerPatienter.prgr_dialog.setValue(100)
          _messError  = QtWidgets.QApplication.translate("bibli_install", "One or more libraries were not installed correctly.", None)
          _messError += "\n\n" + QtWidgets.QApplication.translate("bibli_install", "Plume could malfunction.", None)
          _messError += "\n\n" + QtWidgets.QApplication.translate("bibli_install", "Please contact support.", None)
          managerPatienter.prgr_dialog.setLabelText(_messError)
          _pathIcons = os.path.dirname(__file__) + "/icons/logo"
          iconSource          = _pathIcons + "/plume.svg"
          icon = QtGui.QIcon()
          icon.addPixmap(QtGui.QPixmap(iconSource), QtGui.QIcon.Normal, QtGui.QIcon.Off)
          _QMess = QMessageBox(QMessageBox.Information, zMessTitle, _messError )
          _QMess.setWindowIcon(icon)
          _QMess.exec_()
       else :
          managerPatienter.startBibli(66, comptBibli, 100)
          managerPatienter.prgr_dialog.setValue(100)
          #==================================================
          #Sauvegarde de la version de Plume pour les bibliothèques
          mSettings = QgsSettings()
          mDicAutre = {}
          mSettings.beginGroup("PLUME")
          mSettings.beginGroup("Generale")
          mDicAutre["versionPlumeBibli"] = mVersionPlume
          mDicAutre[python_version_cur]  = mVersionPlume
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
       _sortie = subprocess.run(['python3', '-m', 'pip', 'install', '--upgrade', '--retries', '0', '--timeout', '5', '--quiet', '--quiet', '--quiet', 'pip'], check=True, startupinfo=si) 
    except subprocess.CalledProcessError as err :
       return False
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
       self.prgr_dialog.setWindowModality(QtCore.Qt.WindowModal)
       self.prgr_dialog.setWindowIcon(icon)
       self.prgr_dialog.setFixedSize(300, 170)
       self.prgr_dialog.setMinimumDuration(0)
       self.prgr_dialog.mCancelButton = self.prgr_dialog.findChild(QPushButton)
       self.prgr_dialog.mCancelButton.setVisible(False)
       self.prgr_dialog.setCancelButtonText("OK")
       self.prgr_dialog.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
       self.prgr_dialog.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
       self.prgr_dialog.setWindowTitle(_title)
       self.prgr_dialog.setAutoReset(False)
       self.prgr_dialog.setAutoClose(False)
       self.prgr_dialog.show()

   #------
   def startBibli(self, _num, _comptBibli, _total) :
       i    = int(_num)
       step = _num / _comptBibli
       totalBibli = _total
       while i <= totalBibli :
           self.prgr_dialog.setValue(int(i))
           time.sleep(0.05)
           i += step
       return            

#==================================================
#==================================================
# FIN
#==================================================
