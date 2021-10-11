rem *******
rem Didier LECLERC avril 2020
rem Generation des fichier Pro pour l'internationalisation des langues
rem *******
SET monpathexe=C:\Python394\Lib\site-packages\PyQt5\
rem *******    
%monpathexe%pylupdate5.exe %1.pro
rem *******
rem Compilation en qm pour FR
%monpathexe%lrelease.exe %1_fr.ts -qm %1_fr.qm 
rem *******
rem Copy dans le sous répertoire et suppression
copy %1*.qm ..\i18n\*.*
del %1*.qm