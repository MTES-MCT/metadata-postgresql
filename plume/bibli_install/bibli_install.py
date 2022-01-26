# (c) Didier  LECLERC 2020 CMSIG MTE-MCTRCT/SG/SNUM/UNI/DRC Site de Rouen
# créé sept 2021
import os.path
import subprocess

#==================================================
def manageLibrary(mBibli) :
    if mBibli == "RDFLIB" :
       try:
           import pip
       except ImportError:
           exec(
               open(str(pathlib.Path(plugin_dir, 'scripts', 'get_pip.py'))).read()
           )
           import pip
           subprocess.check_call(['python3', '-m', 'pip', 'uninstall', '--upgrade', 'pip'])

       mPathPerso = os.path.dirname(__file__) + '\\rdflib-6.0.2.tar.gz'
       mPathPerso = mPathPerso.replace("\\","/")
       subprocess.check_call(['python3', '-m', 'pip', 'install', mPathPerso])
    elif mBibli == "OWSLIB" :
       #--
       try:
           import pip
       except ImportError:
           exec(
               open(str(pathlib.Path(plugin_dir, 'scripts', 'get_pip.py'))).read()
           )
           import pip
           subprocess.check_call(['python3', '-m', 'pip', 'uninstall', '--upgrade', 'pip'])

       mPathPerso = os.path.dirname(__file__) + '\\OWSLib-0.25.0.tar.gz'
       mPathPerso = mPathPerso.replace("\\","/")
       subprocess.check_call(['python3', '-m', 'pip', 'install', mPathPerso])
    return
    
#==================================================
#==================================================
# FIN
#==================================================
