# Test de l'interface utilisateur

Procédure de test manuel de l'interface utilisateur, à dérouler avant la diffusion d'une nouvelle version.

## Sauvegarde

 - Sauvegarder le plugin (zip, 7z) via l'explorateur

## Générer un ZIP propre du plugin
 - Créer le zip d'installation avec {py:func}`admin.zip_plume.zip_plume`. Cf. [Aide-mémoire](./memo.md#générer-un-zip-propre-du-plugin) pour la méthode.

## Nettoyage
### QGIS3.ini
 - Supprimer la section [PLUME] dans le fichier QGIS3.ini
### Bibliothèques
 - Désintaller rdflib via pip
   - Ouvrir une session shell dans l'environnement du Qgis et tapez : ```pip uninstall rdflib```

## Installation
 - Installer Plume à partir du gestionnaire d'extension sous Qgis
### Fermer et relancer Qgis
 - la boite de dialogue d'installation ou de mise à jour des bibliothèques doit apparaître
 - La barre d'outil de Plume doit s'afficher

## Tests boite de dialogue de Plume **fermé**
### Ouvrir le panneau d'Asgard Menu
 - Naviguer dans le panneau d'Asgard Menu et constater l'affichage des infobulles
### Ouvrir si ce n'est pas le cas, le panneau de l'explorateur
 - Naviguer dans le le panneau de l'explorateur et constater l'affichage des infobulles

## Tests boite de dialogue de Plume **ouverte**
### Ouvrir le panneau d'Asgard Menu
 - Naviguer dans le panneau d'Asgard Menu et constater l'affichage des infobulles
### Ouvrir si ce n'est pas le cas, le panneau de l'explorateur
 - Naviguer dans le le panneau de l'explorateur et constater l'affichage des infobulles
### se connecter sur une base de données **sans** l'extension plume_pg
 - Vérifier que les trois modèles locaux soient disponibles
 - En mode edition, naviguer de l'un à l'autre et constater les changements dans l'interface
 - Saisir une information et sauvegarder
 - Ouvrir la boite de personnalisation de l'interface et changer quelques paramètres
 - Fermer et ouvrir Plume, puis constater les changements dans l'interface
### se connecter sur une base de données **avec** l'extension plume_pg
 - Vérifier que les trois modèles locaux soient disponibles ainsi que ceux importés dans PostgreSQL
 - En mode edition, naviguer de l'un à l'autre et constater les changements dans l'interface
 - Saisir une information et sauvegarder
 - Ouvrir la boite de personnalisation de l'interface et changer quelques paramètres
 - Fermer et ouvrir Plume, puis constater les changements dans l'interface
 - Changement de thésaurus dans les listes déroulantes
### Barre d'outils de Plume (clic sur les boutons et constat)
 - Edition
 - Copier / Coller / Vider
 - Sauvegarde
 - Traduction
 - Export / import

