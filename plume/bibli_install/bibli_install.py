# (c) Didier  LECLERC 2020 CMSIG MTE-MCTRCT/SG/SNUM/UNI/DRC Site de Rouen
# créé sept 2021
import os.path
import subprocess
from platform import python_version

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
           subprocess.check_call(['python3', '-m', 'pip', 'install', '--upgrade', 'pip'])
           
       # WHEEL
       mPathPerso = os.path.dirname(__file__) + '\\wheel-0.37.1-py2.py3-none-any.whl'
       mPathPerso = mPathPerso.replace("\\","/")
       subprocess.check_call(['python3', '-m', 'pip', 'install', mPathPerso])
       # SIX
       mPathPerso = os.path.dirname(__file__) + '\\six-1.16.0-py2.py3-none-any.whl'
       mPathPerso = mPathPerso.replace("\\","/")
       subprocess.check_call(['python3', '-m', 'pip', 'install', mPathPerso])
       # ISODATE
       mPathPerso = os.path.dirname(__file__) + '\\isodate-0.6.1-py2.py3-none-any.whl'
       mPathPerso = mPathPerso.replace("\\","/")
       subprocess.check_call(['python3', '-m', 'pip', 'install', mPathPerso])
       # PYPARSING
       mPathPerso = os.path.dirname(__file__) + '\\pyparsing-3.0.7-py3-none-any.whl'
       mPathPerso = mPathPerso.replace("\\","/")
       subprocess.check_call(['python3', '-m', 'pip', 'install', mPathPerso])
       # SETUPTOOLS
       mPathPerso = os.path.dirname(__file__) + '\\setuptools-61.2.0-py3-none-any.whl'
       mPathPerso = mPathPerso.replace("\\","/")
       subprocess.check_call(['python3', '-m', 'pip', 'install', mPathPerso])
       if python_version() < ('3,8') :
          # ZIPP
          mPathPerso = os.path.dirname(__file__) + '\\zipp-3.7.0-py3-none-any.whl'
          mPathPerso = mPathPerso.replace("\\","/")
          subprocess.check_call(['python3', '-m', 'pip', 'install', mPathPerso])
          # IMPORTLIB-METADATA
          mPathPerso = os.path.dirname(__file__) + '\\importlib_metadata-4.11.3-py3-none-any.whl'
          mPathPerso = mPathPerso.replace("\\","/")
          subprocess.check_call(['python3', '-m', 'pip', 'install', mPathPerso])
       # RDFLIB
       mPathPerso = os.path.dirname(__file__) + '\\rdflib-6.1.1-py3-none-any.whl'
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
