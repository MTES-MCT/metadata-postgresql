# Version mineure 0.4.0 bêta

*Date de publication : 10 juin 2022.*

*Sur GitHub : [https://github.com/MTES-MCT/metadata-postgresql/releases/tag/v0.4-beta](https://github.com/MTES-MCT/metadata-postgresql/releases/tag/v0.4-beta).*

Plume 0.4 bêta met en service les fonctionnalités de calcul de métadonnées côté serveur. Elle apporte également diverses petites évolutions fonctionnelles visant notamment à fluidifier et sécuriser la navigation.

Il est fortement recommandé de mettre à jour l'extension PostgreSQL PlumePg en parallèle (version 0.1.0). La version 0.0.1 n'est plus reconnue par cette nouvelle version de Plume. 

## Calcul des métadonnées côté serveur

Plume permet désormais de générer des métadonnées à partir d'informations disponibles côté serveur :
- soit automatiquement à l'ouverture de la fiche de métadonnées ;
- soit à la demande de l'utilisateur, lorsque celui-ci clique sur le bouton ![compute_button.svg](../../plume/icons/buttons/compute_button.svg) placé à droite du champ de saisie dans le formulaire.

L'activation des fonctionnalités de calcul est contrôlée par les modèles. Elle n'est évidemment possible que pour les catégories pour lesquelles une méthode de calcul est d'ores-et-déjà définie dans Plume (essentiellement, il s'agit une requête SQL à envoyer au serveur). Certaines méthodes de calcul ne sont disponible que si l'extension PlumePg est installée sur la base PostgreSQL cible.

Dans cette version, cela concerne :
- le titre et la description du jeu de données, qui peuvent être extraits du descriptif PostgreSQL de la table à l'aide d'une expression régulière ;
- les dates de création et de dernière modification, si elles ont été [enregistrées](#enregistrement-des-dates-de-création-et-dernière-modification-des-tables) ;
- les référentiels de coordonnées déclarés pour les champs de la table.

Cf. [Métadonnées calculées](../usage/metadonnees_calculees.md) pour plus de précisions.

*Réferences : [issue #23](https://github.com/MTES-MCT/metadata-postgresql/issues/23) (prérequis : [issue #22](https://github.com/MTES-MCT/metadata-postgresql/issues/23)), [issue #42](https://github.com/MTES-MCT/metadata-postgresql/issues/42).*

## Amélioration de la navigation

### Verrouillage de l'affichage sur la fiche courante

Plume 0.4 bêta ajoute à la barre d'outil de Plume un bouton en forme de cadenas ![lock.svg](../../plume/icons/general/lock.svg) qui permet de verrouiller l'affichage sur la fiche de métadonnées courante.

En mode lecture, ce bouton est désactivé par défaut. Quand l'utilisateur sélectionne une nouvelle couche PostgreSQL dans l'explorateur ou le panneau, les métadonnées de cette couche s'affichent dans le panneau de Plume. Lorsqu'il sélectionne une couche dont le fournisseur n'est pas un serveur PostgreSQL, Plume revient à son écran d'accueil.

Si l'utilisateur actionne le bouton de verrouillage, la fiche de métadonnées courante restera affichée dans le panneau de Plume quelles que soient les manipulations réalisées par l'utilisateur dans l'explorateur et le panneau des couches.

En mode édition, ce bouton est activé par défaut et ne peut pas être désactivé. Ceci permet d'éviter à l'utilisateur de perdre accidentellement ses modifications à cause d'un clic malencontreux sur une autre couche.

*Références : [issue #36](https://github.com/MTES-MCT/metadata-postgresql/issues/36), [issue #41](https://github.com/MTES-MCT/metadata-postgresql/issues/41), [issue #47](https://github.com/MTES-MCT/metadata-postgresql/issues/47).*

### Confirmation à la sortie du mode édition

Lorsque l'utilisateur quitte le mode édition sans avoir préalablement sauvegardé ses modifications, Plume lui demande maintenant une confirmation. Un paramètre utilisateur permet de supprimer cette étape.

*Références : [issue #46](https://github.com/MTES-MCT/metadata-postgresql/issues/46).*

### Affichage des métadonnées de la couche sélectionnée au lancement de Plume

Si l'utilisateur sélectionne une couche PostgreSQL dans l'explorateur ou le panneau des couches *puis* lance Plume, les métadonnées de cette couche sont maintenant immédiatement affichées. Auparavant, seules les couches sélectionnées après le lancement de Plume étaient prises en compte.

*Références : [issue #38](https://github.com/MTES-MCT/metadata-postgresql/issues/38).*


## PlumePg v0.1.0

**Une mise à jour de l'extension PostgreSQL PlumePg sera nécessaire** pour continuer à utiliser les modèles personnalisés avec la version 0.4 de Plume.

La version 0.1.0 de PlumePg apporte deux évolutions fonctionnelles notables :
- un paramétrage plus fin des [fonctionnalités de calcul des métadonnées](../usage/metadonnees_calculees.md) par les modèles ;
- un mécanisme pour enregistrer les dates de création et de dernière modification des tables, en vue de les intégrer aux fiches de métadonnées.

### Paramétrage du calcul automatique des métadonnées

Les champs `compute` des tables `meta_categorie` et `meta_template_categories` admettent maintenant deux nouvelles valeurs, `empty` et `new`. Comme `auto`, ces mots-clés signalent à Plume que la métadonnée doit être calculée automatiquement à partir des informations disponibles sur le serveur PostgreSQL lors du chargement de la fiche de métadonnées. Toutefois, ils posent des conditions à cette action :
- `empty` indique que le calcul automatique doit avoir lieu si et seulement si aucune valeur n'est encore renseignée pour la métadonnée considérée.
- `new` signale que le calcul doit s'exécuter si et seulement si la fiche de métadonnées est vierge.

Les tables `meta_categorie` et `meta_template_categories`, ainsi que la vue `meta_template_categories_full` présentent maintenant un champ supplémentaire `compute_params` de type `jsonb` qui permet de paramétrer la méthode de calcul des métadonnées définie pour la catégorie, lorsque la méthode le prévoit.

### Désactivation d'un modèle

La table `meta_template` présente désormais un champ supplémentaire, `enabled`, qui peut être mis à `False` pour empêcher qu'un modèle soit proposé aux utilisateurs du plugin QGIS. Ce mécanisme pourra notamment être mis à profit pendant la consitution des modèles, afin de ne pas mettre à disposition des utilisateurs des modèles non finalisés.

### Enregistrement des dates de création et dernière modification des tables

PlumePg propose désormais un mécanisme, entièrement optionnel, pour enregistrer automatiquement les dates de création et dernière modification des tables. Cf. [Installation et gestion de l'extension PostgreSQL *PlumePg*](../usage/gestion_plume_pg.md#activation-de-lenregistrement-des-dates).

*Références : [issue #60](https://github.com/MTES-MCT/metadata-postgresql/issues/60).*

### Accès aux données de l'extension

Pour faciliter la gestion des droits sur l'extension, PlumePg confère désormais à tous les utilisateurs un accès en lecture à toutes ses données, via le pseudo-rôle `public`. Cf. [Installation et gestion de l'extension PostgreSQL *PlumePg*](../usage/gestion_plume_pg.md#privilèges).


## Amélioration de la gestion des métadonnées en lecture seule

Plume 0.4 bêta assure que les métadonnées en lecture seule[^isreadonly] en mode édition ne sont plus accompagnées d'aucun bouton permettant d'en altérer la valeur. Les groupes de valeurs en lecture seule n'ont plus de bouton plus.

La lecture seule est désormais une caractéristique héritable. Ainsi, si le modèle indique par exemple que la métadonnée `dct:temporal` est en lecture seule, `dct:temporal / dcat:startDate` le sera également même si ce n'est pas explicitement spécifié dans le modèle.

[^isreadonly]: Une catégorie peut être déclarée comme étant "en lecture seule" (non éditable) par un modèle de fiche défini avec *PlumePg*, en indiquant `True` dans le champ `is_read_only` de la table `z_plume.meta_template_categories` pour le modèle et la catégorie considérés.

*Référence : [issue #48](https://github.com/MTES-MCT/metadata-postgresql/issues/48).*


## Gestion des dépendances Python

Plume 0.4 bêta met en place un nouveau système de gestion des bibliothèques Python requises pour le fonctionnement de Plume, qui permettra de les mettre à jour en parallèle des mises à jour de Plume et allège leur processus d'installation.

Elles restent incorporées dans le plugin (installateurs dans le répertoire [/plume/bibli_install](https://github.com/MTES-MCT/metadata-postgresql/tree/main/plume/bibli_install)), mais sont maintenant référencées par un fichier de dépendances [`/plume/requirements.txt`](https://github.com/MTES-MCT/metadata-postgresql/tree/main/plume/requirements.txt).

En pratique, l'utilisateur pourra constater les changements suivants :
- Plume mettra systématiquement à jour les dépendances au premier lancement du plugin suivant chaque mise à jour de Plume, c'est-à-dire lorsqu'il clique pour la première fois sur l'icône de Plume dans la barre d'outils. Jusqu'à présent Plume se contentait de tester la disponibilité de la bibliothèque RDFLib et, à défaut, l'installait avec ses dépendances sans contrôler en aucune façon les versions.
- Le processus commence toujours par une tentative de mise à jour de `pip`, l'utilitaire de gestion des bibliothèques python. Cette étape se manifeste par l'ouverture d'une première fenêtre de commandes. Elle échouera nécessairement en l'absence de connexion internet ou si la connexion nécessite de passer par un proxy, sans que cela ne prête à conséquence pour la suite. À noter qu'au lieu de retenter cinq fois d'établir la connexion avec un délai / *timeout* de 10 secondes, Plume ne réalise plus qu'un seul essai avec un délai de 5 secondes, ce qui accélère considérablement l'opération. 
- Plume installe ou met ensuite à jour les dépendances elles-mêmes, selon les spécifications du fichier [`requirements.txt`](https://github.com/MTES-MCT/metadata-postgresql/blob/main/plume/requirements.txt). Cette étape ouvre désormais une unique fenêtre de commande dans laquelle apparaîtront toutes les opérations réalisées, et non plus une fenêtre par bibliothèque comme auparavant.

*Référence : [issue #51](https://github.com/MTES-MCT/metadata-postgresql/issues/51), [issue #53](https://github.com/MTES-MCT/metadata-postgresql/issues/53).*


## Modification du modèle de métadonnées

La métadonnée commune `dct:subject` (*catégorie thématique*) est supprimée. Cette métadonnée était un ajout de GeoDCAT-AP par rapport à DCAT et DCAT-AP. La nomenclature ISO qu'elle utilisait est désormais l'un des thésaurus utilisables pour la propriété `dcat:theme` (thème), qui devient donc l'unique métadonnée relative aux thèmes catégorisés. Si elle est présente dans des métadonnées importées, elle sera désormais automatiquement transformée en `dcat:theme`.

La version 0.1.0 de PlumePg fait disparaître en conséquence cette métadonnée de la liste des catégories communes disponibles, ce qui provoquera en cascade sa suppression des modèles. S'il y a lieu de la remplacer (par exemple par `dcat:theme`), cette opération devra être réalisée manuellement.

## Anomalies et divers

Les fonctionnalités de visualisation des métadonnées géométriques prennent désormais en charge tous les types géométriques dont QGIS sait interpréter la représentation WKT. *Références : [issue #34](https://github.com/MTES-MCT/metadata-postgresql/issues/34).*

Il est désormais possible de sélectionner et copier du texte dans les fiches de métadonnées ouvertes en mode lecture. *Références : [issue #56](https://github.com/MTES-MCT/metadata-postgresql/issues/56).*

Le nom du modèle courant est dorénavant explicitement affiché dans la barre d'outils de Plume. *Références : [issue #55](https://github.com/MTES-MCT/metadata-postgresql/issues/55).*

Il est maintenant possible de spécifier via un modèle qu'une catégorie commune prenant pour valeur des dates simples utilise à la place des dates avec heures, ou réciproquement. Jusqu'ici, les modèles pouvaient seulement changer le type de valeur pour les catégories locales.

Complément sur la traduction anglaise des textes de l'interface du plugin QGIS, hors éléments inclus dans les fiches de métadonnées. *Référence : [issue #50](https://github.com/MTES-MCT/metadata-postgresql/issues/50).*

Plume vérifie désormais la compatibilité des versions de Plume et PlumePg avant de tenter d'utiliser cette dernière pour importer des modèles. En cas de non compatibilité, seuls les modèles locaux sont disponibles, comme dans le cas où PlumePg n'est pas installée sur la base. *Référence : [issue #49](https://github.com/MTES-MCT/metadata-postgresql/issues/49).*

Correction d'une anomalie qui empêchait d'importer des fiches de métadonnées depuis certains CSW, notamment celui de GéoIDE. *Référence : [issue #65](https://github.com/MTES-MCT/metadata-postgresql/issues/65).*

Correction du point de moissonnage pour le CSW de GéoIDE : `http://ogc.geo-ide.developpement-durable.gouv.fr/csw/harvestable-dataset` est remplacé par `http://ogc.geo-ide.developpement-durable.gouv.fr/csw/dataset-harvestable`. Les points de moissonnages pré-configurés ne sont désormais plus référencés dans le `QGIS3.ini`, afin de faciliter leur maintenance. Plus généralement tous les paramètres de configuration qui n'ont pas vocation à être personnalisés par l'utilisateur ou selon l'environnement sortent du fichier `QGIS3.ini`. Ils sont maintenant définis par un fichier interne au code de Plume, `config.py`.

Consolidation de la gestion des connexions au serveur PostgreSQL et des erreurs induites par les suppressions d'objets pendant l'édition des métadonnées, tant dans QGIS que côté serveur. *Référence : [issue #59](https://github.com/MTES-MCT/metadata-postgresql/issues/59) et [issue #63](https://github.com/MTES-MCT/metadata-postgresql/issues/63).*

Les champs supprimés n'apparaissent plus dans l'onglet *Champs* des fiches de métadonnées, ce qui - en plus de n'être pas pertinent - provoquait une erreur lors de l'enregistrement.

Correction d'une anomalie (ou du moins révision d'un comportement intentionnel mais sous optimal) qui faisait apparaître des blocs vides dans fiches de métadonnées dans les conditions suivantes :
- En mode lecture.
- Catégorie autorisant à la fois des valeurs issues d'un thésaurus et des valeurs décrites manuellement.
- Toutes les propriétés servant à la description manuelle sont hors modèle, seules les valeurs issues d'un thésaurus sont donc supposées être affichées.
- La description manuelle avait servi pour une valeur (au moins une propriété préalablement renseignée). C'est le bloc correspond à cette valeur qui apparaissait vide au lieu de ne pas apparaître du tout.

Correction d'une coquille qui affectait la suppression de sources de vocabulaire contrôlé via les modèles.

