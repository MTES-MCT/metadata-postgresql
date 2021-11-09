
# PLUME NOUS SOUHAITE LA BIENVENUE !!

## À faire ou en cours
![Logo](plume/flyers/plume1.png) 
       
## Plume version 1.0

### Warning versions

|     Quoi      |     A faire     |  Terminé   |  Qui   | Notes |
| ------------- | :-------------: | :---------: | :---------: |  --- |
| Plume ne fonctionne qu'à partir de la version 3.10 et supérieure de Qgis |        |   Ok   |   DL/LL   | Le problème provient de la version de "psycopg2" qui est embarquée dans la version de Qgis (passage d'arguments)
- Qgis 3.4.5 = psycopg2 2.7.5
- Qgis 3.10 = psycopg2 2.8.4
- Qgis 3.20 = psycopg2 2.8.6 |

### Fonctionnalités majeures à implémenter

|     Quoi      |     A faire     |  Terminé   |  Qui   | Notes |
| ------------- | :-------------: | :---------: | :---------: |  --- |
| Accès aux trois canaux             |        |   Ok   |   DL   | |
| DockWidget vs Windows              |        |   Ok   |   DL   | |
| Formulaire à la volée              |        |   Ok   |   DL   | |
| QtabWidget (gestion des onglets)   |        |   Ok   |   DL   | |
| Installation de l'extension de PLUME |        |   OK   |   DL   | Il s'agit de proposer dans l'interface de Asgard Manager, l'installation et les mises à jour de l'extension de PLUME pour l'ADL |
| Import de la bibliothèque RDFLIB   |        |   OK     |   DL   | Il s'agit de pouvoir vérifier et installer la bibliothèque RDFLIB de façon autonome (solution : installation en local, pas besoin de connexion, PLUME est indépendant et embarque la distribution et se charge de l'installation)| 
| Compléter le schéma SHACL          |   X    |        |   LL   | + thésaurus manquants |
| Outillage de l'import de métadonnées GéoIDE Catalogue |   X    |        |   LL   | En attente retour de Luc Boyer sur la documentation de l'API. |
| Documentation sous Scenari         |   X   |        |   LL / DL   | |
| Audit de performance               |   X   |        |   LL / DL   | |

### Fonctionnalités mineures à implémenter

|     Quoi      |     A faire     |  Terminé   |  Qui   | Notes |
| ------------- | :-------------: | :---------: | :---------: |  --- |
| Bascule mode lecture/mode édition  |       |   Ok   |   DL   | |
| Sauvegarde                         |       |   OK   |   DL   | |
| Réinitialisation                   |       |   OK   |   DL   | Décrit dans [Actions générales](/__doc__/16_actions_generales.md#réinitialisation) |
| Export                             |       |   OK   |   DL   | Décrit dans [Actions générales](/__doc__/16_actions_generales.md#export-des-métadonnées-dans-un-fichier) |
| Import                             |       |   OK   |   DL   | Décrit dans [Actions générales](/__doc__/16_actions_generales.md#import-de-métadonnées-depuis-un-fichier) |
| Choix du modèle                    |       |   OK   |   DL   | |
| Activation du mode traduction      |       |   OK   |   DL   | |
| Création d'un menu type QToolButton/QMenu |       |   OK   |   DL   | Il s'agit de créer un menu type QToolButton/QMenu dans la barre de menu afin d'alléger ladite barre d'icone (Les items du menu de ce bouton serait "Aide / A propos" dans un premier temps |
| Création d'une boite de dialogue A propos |       |   OK   |   DL   | Création d'une boite de dialogue A propos type de celle de Asgard Manager |
| Choix de la langue principale      |       |   OK   |   DL   | Décrit dans [Actions générales](/__doc__/16_actions_generales.md#langue-principale-des-métadonnées) |
| Génération petit JSON GéoIDE       |       |   OK   |   DL   | Petite adaptation à faire à l'étape 3 du [processus de sauvegarde](/__doc__/16_actions_generales.md#sauvegarde). Il s'agit de passer un paramètre supplémentaire à `update_pg_description()` + gestion du [paramètre utilisateur](/__doc__/20_parametres_utilisateurs.md) correspondant (`geoideJSON`). |
| Récupération des UUID GéoIDE       |       |    OK  |   DL   | L'argument `data` de `build_dict()` sert maintenant à quelque chose ! La [documentation](/__doc__/05_generation_dictionnaire_widgets.md#data--les-métadonnées-calculées) explique comment l'utiliser pour passer l'identifiant GéoIDE à `build_dict()`. |
| Mécanisme de copier/coller de fiche complète |       |   OK   |   DL   | Décrit dans [Actions générales](/__doc__/16_actions_generales.md#copier--coller-dune-fiche-complète) |
| Consolidation de la gestion des paramètres utilisateurs  |      |   OK   |   DL   | Comme évoqué [ici](https://github.com/MTES-MCT/metadata-postgresql/blob/main/__doc__/20_parametres_utilisateur.md), il s'agit de ne plus créer de valeur par défaut pour certains paramètres. |
| Nouvelle gestion des paramètres utilisateurs   |        |   OK   |   DL   | Il s'agit à l'ouverture de Plume, de créer les paramètres utilisateurs (Sous section + nom du paramètre) dans le QGIS3.ini sans valeur. Pour que le paramètre soit pris en compte dans les process de Plume, l'utilisateur, n'aura plus qu'à saisir une valeur sans se soucier de la syntaxe  |

### Anomalies et bricoles

|     Quoi      |     A faire     |  Terminé   |  Qui   | Notes |
| ------------- | :-------------: | :---------: | :---------: |  --- |
| Les doubles clics sur une couche n'ont pas d'effet (pour ouvrir la fenêtre des propriétés dans le panneau des couches ou pour charger une couche depuis l'explorateur) |       |   OK   |   DL   | Semble directement lié au temps de chargement des métadonnées. Les améliorations de performance ont résolu complètement le problème chez DL, partiellement chez LL. |
| ToolTips sur les QLabel ?  |       |   OK   |   DL   | Si c'est possible, bien sûr. Concernerait à la fois les QLabel qui donnent les noms des catégories (vu qu'ils ont tendance à occuper la moitié de l'espace...) et les QLabel utilisés pour les valeurs en mode lecture. Le texte est toujours dans la clé `'help text'`. |
| Widget date et time à revoir ou pas       |   X   |        |   DL   | Le principal sujet est de ne pas afficher de date quand aucune n'a été saisie (et qu'il n'est pas prévu d'avoir une valeur par défaut) |
| Valeur vide dans les listes des QComboBox |       |   OK   |   DL   | Comme pour les QDateEdit, il s'agit de ne pas afficher de valeur (= la première de la liste) lorsqu'il n'y en a pas. |
| Changer les couleurs par défaut des cadres |       |   OK   |   DL   | Les bonnes sont [là](https://github.com/MTES-MCT/metadata-postgresql/blob/main/__doc__/10_creation_widgets.md#autres-groupes). |
| Créer une icône pour la valeur courante des menus des QToolButton  |      |    OK    |   LL   | Finalement, pas de nouvelle icône. On utilise le logo de Plume. |
| La petite flèche des QComboBox n'a pas le même aspect que celles des autres widgets ?  |       |   OK   |   DL   | |
| `rdf:langString` au lieu de `xsd:string` dans le schéma SHACL pour distinguer les valeurs litérales qui appellent réellement une traduction  |       |   OK   |   LL   | |
| Masquer les groupes de propriétés dont tous les enfants sont masqués (clé `'main widget type'` valant `None`)  |       |   OK   |   LL   | À confirmer, mais lancer `mDict[mParentWidget]['main widget'] = None` si `rowidx[mParentWidget] == 0` devrait faire l'affaire. |
| Optimisation : remplacer les appels à `query` par les méthodes natives de rdflib partout où c'est possible |       |   OK   |   LL   | Spécialement lorsqu'il y a des arguments optionnels, leur traitement paraît spécialement coûteux. |
| Anomalie : quand l'extension metadata est installée mais que les modèles pré-configurés n'ont pas été chargés, à l'ouverture d'une fiche de métadonnées on a un onglet "Général" vide et toutes les métadonnées dans "Autres". |       |  OK  |   DL   | NB : la petite plume de l'interface indique que le modèle est "Aucun", mais ce n'est pas vraiment le cas puisque cliquer sur "Aucun" remet les choses en ordre (= toutes les métadonnées dans "Général"). Il y a peut-être un rapport avec le paramètre `preferedTemplate` enregistré avec comme valeur `"Basique"` dans `QGIS3.ini` ? |
| Gestion des erreurs PostgreSQL à nettoyer |      |   OK   |   DL   | Pas besoin de distinguer des erreurs gérées ou non pour Plume - PG n'est jamais censé renvoyer d'erreur. Pour l'image affichée dans la boîte de dialogue, le logo de Plume devrait faire l'affaire pour l'instant. |
| Reprise du `metagraph` d'origine lorsqu'on quitte le mode édition sans sauvegarder après une réinitialisation, un import ou un copier/coller.  |       |   OK   |   DL   | Pour l'heure le formulaire est régénéré avec le `metagraph` résultant de l'action annulée lorsque l'utilisateur revient en mode lecture. Il faut recliquer sur la source pour retrouver les métadonnées d'origine. |
| Quand le modèle référencé dans `preferedTemplate` est appelé mais n'existe pas, `template` et `templateTabs` devraient être mis à `None`.  |       |   OK   |   DL   | |

## Plume version 2.0

### Fonctionnalités majeures à implémenter

|     Quoi      |     A faire     |  Terminé   |  Qui   | Notes |
| ------------- | :-------------: | :---------: | :---------: |  --- |
| Prise en charge des relations entre tables   |   X     |      |   LL   | |
| Gestion des métadonnées des schémas          |   X     |      |   LL / DL  | |
| Recherche                                    |   X     |      |   LL / DL  | |
| Mécanisme de copier/coller d'une branche     |   X     |      |   LL / DL  | |
