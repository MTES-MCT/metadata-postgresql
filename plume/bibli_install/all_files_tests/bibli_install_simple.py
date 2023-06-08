# (c) Didier  LECLERC 2020 CMSIG MTE-MCTRCT/SG/SNUM/UNI/DRC Site de Rouen
# créé sept 2021
import os.path
import subprocess
import qgis
import os
 
#==================================================
def updateRequierement(pathPlume, pathPython,  pathPip, pathBibli) :
    #si = subprocess.STARTUPINFO() 
    #si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    mPatImportlib_metadata = pathBibli + "/importlib_metadata-6.0.0-py3-none-any.whl"
    mPathRdflib            = pathBibli + "/rdflib-6.3.2-py3-none-any.whl"

    mPath = pathPlume
    mPathPerso = mPath.replace("\\","/") + "/requirements.txt"
           
    _sortie = subprocess.run(['python3', '-m', 'pip', 'install', '-r', mPathPerso])
    
    #_sortie = subprocess.run(['python3', '-m', 'pip', 'install', mPatImportlib_metadata] )
    #_sortie = subprocess.run(['python3', '-m', 'pip', 'install', mPathRdflib] )

    try:
       #_sortie = subprocess.run(['python3', '-m', 'pip', 'install', '-r', mPathPerso],  check=True, startupinfo=si, env = getPathPip() )
       pass
    except subprocess.CalledProcessError as err:
       return  False
    return True

pathPlume  = "C:/Users/didier.leclerc/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/plume"
pathBibli  = "C:/Users/didier.leclerc/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/plume/bibli_install"
pathPython = "C:/Programmes/QGIS_3_18/bin"
pathPip    = "C:/Programmes/QGIS_3_18/apps/Python37/Scripts"

        
ret = updateRequierement( pathPlume, pathPython,  pathPip, pathBibli )
