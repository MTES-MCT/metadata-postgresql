# (c) Didier  LECLERC 2020 CMSIG MTE-MCTRCT/SG/SNUM/UNI/DRC Site de Rouen
# créé sept 2021
import os.path
import subprocess
import logging
from qgis.core import QgsSettings

#==================================================
def manageLibrary(mVersionPlume, mVersionPlumeBibli) :
    mPath = os.path.dirname(__file__)
    if mVersionPlume != mVersionPlumeBibli :
       logging.debug("Installation des bibliothèques ...")
       try:
           subprocess.check_call(['python3', '-m', 'pip', 'install', '--upgrade', '--retries', '1', '--timeout', '5', '--quiet', '--quiet', '--quiet', 'pip'])
       except subprocess.CalledProcessError:
           logging.exception("pip n'a pas été mis à jour.") 

       mPathPerso = mPath.replace("\\","/") + "/requirements.txt"
       subprocess.check_call(['python3', '-m', 'pip', 'install', '-r', mPathPerso])

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
       
    return

#==================================================
#==================================================
# FIN
#==================================================
