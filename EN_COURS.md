# À faire ou en cours
![Logo](plume/flyers/plume1.png)
        
## Plume version 1.0

### Fonctionnalités majeures à implémenter

|     Quoi      |     A faire     |  Terminé   |  Qui   | Notes |
| ------------- | :-------------: | :---------: | :---------: |  --- |
| Accès aux trois canaux             |        |   Ok   |   DL   | |
| DockWidget vs Windows              |        |   Ok   |   DL   | |
| Formulaire à la volée              |        |   Ok   |   DL   | Prise en charge des main widgets QLabel |
| QtabWidget (gestion des onglets)   |        |   Ok   |   DL   | |
| Compléter le schéma SHACL          |   X    |        |   LL   | + thésaurus manquants |
| Outillage de l'import de métadonnées GéoIDE Catalogue |   X    |        |   LL   | À basculer en v2.0 si les fiches DCAT du Front Office ne sont pas exploitables. |
| Documentation sous Scenari         |   X   |        |   LL / DL   | |

### Fonctionnalités mineures à implémenter

|     Quoi      |     A faire     |  Terminé   |  Qui   | Notes |
| ------------- | :-------------: | :---------: | :---------: |  --- |
| Bascule mode lecture/mode édition  |       |   Ok   |   DL   | |
| Sauvegarde                         |   X   |        |   DL   | |
| Réinitialisation                   |   X   |        |   DL   | |
| Export                             |   X   |        |   DL   | |
| Import                             |   X   |        |   DL   | |
| Choix du modèle                    |   X   |        |   DL   | |
| Activation du mode traduction      |       |   OK   |   DL   | |
| Choix de la langue principale      |   X   |        |   DL   | |

### Anomalies et bricoles

|     Quoi      |     A faire     |  Terminé   |  Qui   | Notes |
| ------------- | :-------------: | :---------: | :---------: |  --- |
| Problème double clique sur l'explorateur  |   X   |        |   DL   | |
| Widget date et time à revoir ou pas       |   X   |        |   DL   | Le principal sujet est de ne pas afficher de date quand aucune n'a été saisie (et qu'il n'est pas prévu d'avoir une valeur par défaut) |
| Valeur vide dans les listes des QComboBox |   X   |        |   DL   | Comme pour les QDateEdit, il s'agit de ne pas afficher de valeur (= la première de la liste) lorsqu'il n'y en a pas. |
| Changer les couleurs par défaut des cadres |       |   OK   |   DL   | Les bonnes sont [là](https://github.com/MTES-MCT/metadata-postgresql/blob/main/__doc__/10_creation_widgets.md#autres-groupes), et ce ne sont définitivement pas celles qui servent à ce stade. |
| Créer une icône pour la valeur courante des menus des QToolButton  |   X   |        |   LL   | |

## Plume version 2.0

### Fonctionnalités majeures à implémenter

|     Quoi      |     A faire     |  Terminé   |  Qui   | Notes |
| ------------- | :-------------: | :---------: | :---------: |  --- |
| Prise en charge des relations entre tables   |   X     |      |   LL   | |
| Gestion des métadonnées des schémas          |   X     |      |   LL / DL  | |
| Recherche                                    |   X     |      |   LL / DL  | |
