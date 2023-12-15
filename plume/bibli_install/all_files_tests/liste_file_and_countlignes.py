# (c) Didier  LECLERC 2023 MTE-MCTRCT/SG/DNUM/UNI/DRC Site de Rouen
# créé sept 2023

import os
import linecache

def count_lines(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    return len(lines)

def mPrint(py_files, subdir_counts) :
   mTotal = 0
   for file_path, num_lines in py_files:
       print(f'Fichier : {file_path} | Nombre de lignes : {num_lines}')
       mTotal += float(num_lines)     
   print(f'Total des lignes : {mTotal}')

   print("\nDécompte des lignes .py par sous-dossier :")
   for subdir, count in subdir_counts.items():
       print(f'Sous-dossier : {subdir} | Nombre de lignes .py : {count}')

   return    

def list_and_count_py_files(root_dir, _print = None):
    py_files = []
    subdir_counts = {}  # Dictionnaire pour stocker les décomptes des fichiers .py par sous-dossier

    for foldername, subfolders, filenames in os.walk(root_dir):
        py_count = 0  # Décompte de fichiers .py pour ce sous-dossier
        for filename in filenames:
            if filename.endswith('.py'):
                file_path = os.path.join(foldername, filename)
                num_lines = count_lines(file_path)
                py_files.append((file_path, num_lines))
                py_count += num_lines
        if py_count > 0:
            subdir_counts[foldername] = py_count
                
    if _print == "PRINT" : mPrint(py_files, subdir_counts)
                
    return py_files, subdir_counts


root_directory = 'C:/Users/didier.leclerc/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/plume'
list_and_count_py_files(root_directory, "PRINT")
root_directory = 'C:/Users/didier.leclerc/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/asgardmanager'
list_and_count_py_files(root_directory, "PRINT")


