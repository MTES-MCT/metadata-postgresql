# À faire ou en cours
![Logo](plume/flyers/plume1.png)
        
## Plume version 1.0

### Fonctionnalités majeures à implémenter

|     Quoi      |     A faire     |  Terminé   |  Qui   | Notes |
| ------------- | :-------------: | :---------: | :---------: |  --- |
| Accès aux trois canaux             |        |   Ok   |   DL   | |
| DockWidget vs Windows              |        |   Ok   |   DL   | |
| Formulaire à la volée              |        |   Ok   |   DL   | |
| QtabWidget (gestion des onglets)   |        |   Ok   |   DL   | |
| Compléter le schéma SHACL          |   X    |        |   LL   | + thésaurus manquants |
| Outillage de l'import de métadonnées GéoIDE Catalogue |   X    |        |   LL   | En attente retour de Luc Boyer sur la documentation de l'API. |
| Documentation sous Scenari         |   X   |        |   LL / DL   | |

### Fonctionnalités mineures à implémenter

|     Quoi      |     A faire     |  Terminé   |  Qui   | Notes |
| ------------- | :-------------: | :---------: | :---------: |  --- |
| Bascule mode lecture/mode édition  |       |   Ok   |   DL   | |
| Sauvegarde                         |       |   OK   |   DL   | |
| Réinitialisation                   |   X   |        |   DL   | Décrit dans [Actions générales](/__doc__/16_actions_generales.md#réinitialisation) |
| Export                             |   X   |        |   DL   | Décrit dans [Actions générales](/__doc__/16_actions_generales.md#export-des-métadonnées-dans-un-fichier) |
| Import                             |   X   |        |   DL   | Décrit dans [Actions générales](/__doc__/16_actions_generales.md#import-de-métadonnées-depuis-un-fichier) |
| Choix du modèle                    |       |   OK   |   DL   | |
| Activation du mode traduction      |       |   OK   |   DL   | |
| Choix de la langue principale      |   X   |        |   DL   | Décrit dans [Actions générales](/__doc__/16_actions_generales.md#langue-principale-des-métadonnées) |
| Génération petit JSON GéoIDE       |   X   |        |   DL   | Petite adaptation à faire à l'étape 3 du [processus de sauvegarde](/__doc__/16_actions_generales.md#sauvegarde). Il s'agit de passer un paramètre supplémentaire à `update_pg_description()` + gestion du [paramètre utilisateur](/__doc__/20_parametres_utilisateurs.md) correspondant (`geoideJSON`). |
| Récupération des UUID GéoIDE       |   X   |        |   DL   | L'argument `data` de `build_dict()` sert maintenant à quelque chose ! La [documentation](/__doc__/05_generation_dictionnaire_widgets.md#data--les-métadonnées-calculées) explique comment l'utiliser pour passer l'identifiant GéoIDE à `build_dict()`. |
| Mécanisme de copier/coller de fiche complète |   X   |        |   DL   | Décrit dans [Actions générales](/__doc__/16_actions_generales.md#copier--coller-dune-fiche-complète) |

### Anomalies et bricoles

|     Quoi      |     A faire     |  Terminé   |  Qui   | Notes |
| ------------- | :-------------: | :---------: | :---------: |  --- |
| Problème double clique sur l'explorateur  |   X   |        |   DL   | |
| ToolTips sur les QLabel ?  |   X   |        |   DL   | Si c'est possible, bien sûr. Concernerait à la fois les QLabel qui donnent les noms des catégories (vu qu'ils ont tendance à occuper la moitié de l'espace...) et les QLabel utilisés pour les valeurs en mode lecture. Le texte est toujours dans la clé `'help text'`. |
| Widget date et time à revoir ou pas       |   X   |        |   DL   | Le principal sujet est de ne pas afficher de date quand aucune n'a été saisie (et qu'il n'est pas prévu d'avoir une valeur par défaut) |
| Valeur vide dans les listes des QComboBox |       |   OK   |   DL   | Comme pour les QDateEdit, il s'agit de ne pas afficher de valeur (= la première de la liste) lorsqu'il n'y en a pas. |
| Changer les couleurs par défaut des cadres |       |   OK   |   DL   | Les bonnes sont [là](https://github.com/MTES-MCT/metadata-postgresql/blob/main/__doc__/10_creation_widgets.md#autres-groupes). |
| Créer une icône pour la valeur courante des menus des QToolButton  |      |    OK    |   LL   | Finalement, pas de nouvelle icône. On utilise le logo de Plume. |
| La petite flèche des QComboBox n'a pas le même aspect que celles des autres widgets ?  |   X   |        |   DL   | |
| `rdf:langString` au lieu de `xsd:string` dans le schéma SHACL pour distinguer les valeurs litérales qui appellent réellement une traduction  |       |   OK   |   LL   | |
| Masquer les groupes de propriétés dont tous les enfants sont masqués (clé `'main widget type'` valant `None`)  |       |   OK   |   LL   | À confirmer, mais lancer `mDict[mParentWidget]['main widget'] = None` si `rowidx[mParentWidget] == 0` devrait faire l'affaire. |
| Optimisation : remplacer les appels à `query` par les méthodes natives de rdflib partout où c'est possible |       |   OK   |   LL   | Spécialement lorsqu'il y a des arguments optionnels, leur traitement paraît spécialement coûteux. |
| Anomalie : quand l'extension metadata est installée mais que les modèles pré-configurés n'ont pas été chargés, à l'ouverture d'une fiche de métadonnées on a un onglet "Général" vide et toutes les métadonnées dans "Autres". |   X   |      |   DL   | NB : la petite plume de l'interface indique que le modèle est "Aucun", mais ce n'est pas vraiment le cas puisque cliquer sur "Aucun" remet les choses en ordre (= toutes les métadonnées dans "Général"). Il y a peut-être un rapport avec le paramètre `preferedTemplate` enregistré avec comme valeur `"Basique"` dans `QGIS3.ini` ? |

## Plume version 2.0

### Fonctionnalités majeures à implémenter

|     Quoi      |     A faire     |  Terminé   |  Qui   | Notes |
| ------------- | :-------------: | :---------: | :---------: |  --- |
| Prise en charge des relations entre tables   |   X     |      |   LL   | |
| Gestion des métadonnées des schémas          |   X     |      |   LL / DL  | |
| Recherche                                    |   X     |      |   LL / DL  | |
| Mécanisme de copier/coller d'une branche     |   X     |      |   LL / DL  | |
