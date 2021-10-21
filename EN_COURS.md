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
| Réinitialisation                   |   X   |        |   DL   | |
| Export                             |   X   |        |   DL   | |
| Import                             |   X   |        |   DL   | |
| Choix du modèle                    |   X   |        |   DL   | |
| Activation du mode traduction      |       |   OK   |   DL   | |
| Choix de la langue principale      |   X   |        |   DL   | |
| Génération petit JSON GéoIDE      |   X   |        |   LL   | Les fonctions sont écrites, mise à jour de la doc à faire avant passage de relai à DL. |
| Récupération des UUID GéoIDE     |   X   |        |   LL   | |
| Mécanisme de copier/coller de fiche complète |   X   |        |   LL   | À ajouter à la documentation avant passage de relai à DL. |

### Anomalies et bricoles

|     Quoi      |     A faire     |  Terminé   |  Qui   | Notes |
| ------------- | :-------------: | :---------: | :---------: |  --- |
| Problème double clique sur l'explorateur  |   X   |        |   DL   | |
| Widget date et time à revoir ou pas       |   X   |        |   DL   | Le principal sujet est de ne pas afficher de date quand aucune n'a été saisie (et qu'il n'est pas prévu d'avoir une valeur par défaut) |
| Valeur vide dans les listes des QComboBox |   X   |        |   DL   | Comme pour les QDateEdit, il s'agit de ne pas afficher de valeur (= la première de la liste) lorsqu'il n'y en a pas. |
| Changer les couleurs par défaut des cadres |       |   OK   |   DL   | Les bonnes sont [là](https://github.com/MTES-MCT/metadata-postgresql/blob/main/__doc__/10_creation_widgets.md#autres-groupes). |
| Créer une icône pour la valeur courante des menus des QToolButton  |   X   |        |   LL   | |
| La petite flèche des QComboBox n'a pas le même aspect que celles des autres widgets ?  |   X   |        |   DL   | |

## Plume version 2.0

### Fonctionnalités majeures à implémenter

|     Quoi      |     A faire     |  Terminé   |  Qui   | Notes |
| ------------- | :-------------: | :---------: | :---------: |  --- |
| Prise en charge des relations entre tables   |   X     |      |   LL   | |
| Gestion des métadonnées des schémas          |   X     |      |   LL / DL  | |
| Recherche                                    |   X     |      |   LL / DL  | |
| Mécanisme de copier/coller d'une branche     |   X     |      |   LL / DL  | |
