# Version mineure 0.6.0 bêta

*Date de publication : 8 décembre 2022.*

*Sur GitHub : https://github.com/MTES-MCT/metadata-postgresql/releases/tag/v0.6-beta.*

Plume 0.6 bêta rassemble des améliorations sensibles en matière d'ergonomie et de petites améliorations fonctionnelles.

L'extension PostgreSQL PlumePG est mise à jour en parallèle en version 0.1.2.

_**Avertissement :** Plume 0.6 bêta reste une version de test, à ne pas utiliser en production, car son schéma de métadonnées communes est susceptible d'évoluer dans la prochaine version sans que la rétro-compatibilité ne soit assurée. Autrement dit, les fiches de métadonnées créées avec cette version pourraient ne pas être pleinement exploitables par les versions ultérieures de Plume._ 

## Refonte de l'interface

L'**interface de Plume** devient plus **ergonomique** et plus **souple**. En particulier : 
- Les éléments (*widgets*) qui composent les fiches de métadonnées étaient antérieurement répartis sur toute la hauteur du panneau ou de la fenêtre, ce qui créait de grands espaces verticaux entre les métadonnées, voire entre le libellé d'une métadonnée et sa valeur. La version 0.6.0 rend la lecture bien plus confortable en supprimant tous ces espaces inutiles.

  Ce changement rend aussi la propriété [`rowspan`](../usage/modeles_de_formulaire.md#categories-de-metadonnees) des modèles bien plus pertinente, puisqu'elle contrôle désormais véritablement la hauteur des zones de saisie multilignes, qui étaient auparavant étendues pour occuper tout l'espace. *Référence : [issue #79](https://github.com/MTES-MCT/metadata-postgresql/issues/79).*
- La barre d'outils de Plume et ses fiches de métadonnées présentent désormais de nouvelles icônes colorées plus aisément reconnaissables. *Références : [issue #77](https://github.com/MTES-MCT/metadata-postgresql/issues/77), [issue #84](https://github.com/MTES-MCT/metadata-postgresql/issues/84).*
- Des raccourcis clavier ont été définis sur les boutons de la barre d'outils qui le justifiaient :
  `Alt+Maj+S` pour la sauvegarde ![save.svg](../../plume/icons/general/save.svg), `Alt+Maj+E` pour la bascule entre mode lecture et mode édition ![read.svg](../../plume/icons/general/read.svg), `Alt+Maj+R` pour verrouiller ou déverrouiller la fiche ![verrou.svg](../../plume/icons/general/verrou.svg), etc.   Les raccourcis de tous les boutons qui en disposent sont rappelés dans leurs infobulles. *Référence : [issue #77](https://github.com/MTES-MCT/metadata-postgresql/issues/77).*
- Les boutons ![plus_button.svg](../../plume/icons/buttons/plus_button.svg) plus et ![minus_button.svg](../../plume/icons/buttons/minus_button.svg) moins des fiches de métadonnées, qui permettent de gérer la saisie des métadonnées à valeurs multiples, sont désormais plus petits, afin de ne pas attirer l'oeil davantage qu'ils ne le méritent. *Référence : [issue #77](https://github.com/MTES-MCT/metadata-postgresql/issues/77).*
- Il est désormais possible d'utiliser des polices exotiques, ou encore d'activer le grossissement sur son écran sans avoir de libellés tronqués. Ceci vaut pour l'interface principale, mais aussi la boîte de dialogue de configuration de Plume et la boîte de dialogue pour l'import via un service CSW. *Référence : [issue #91](https://github.com/MTES-MCT/metadata-postgresql/issues/91).*
- La boîte de paramétrage ![configuration.svg](../../plume/icons/general/configuration.svg) a été réorganisée, avec un classement plus intuitif des paramètres dans les onglets. *Référence : [issue #90](https://github.com/MTES-MCT/metadata-postgresql/issues/90).*
- La barre d'outils de l'interface principale bénéficie désormais d'un placement dynamique des icônes et réagit mieux en cas de redimensionnement de la fenêtre, grossissement, etc. *Références : [issue #82](https://github.com/MTES-MCT/metadata-postgresql/issues/82), [issue #87](https://github.com/MTES-MCT/metadata-postgresql/issues/87).*
- Dans tous les menus de choix, il est désormais possible d'identifier immédiatement la valeur actuellement sélectionnée par la petite flèche positionnée devant :
  - ![selected_brown.svg](../../plume/icons/general/selected_brown.svg) flèche brune pour les menus de la barre d'outils,
  - ![selected_blue.svg](../../plume/icons/buttons/selected_blue.svg) flèche bleue pour les menus des fiches de métadonnées.

  Ce fonctionnement existait déjà pour le menu de choix du modèle (barre d'outils) et les menus de choix de la source qui accompagnent certaines catégories de métadonnées, il est désormais étendu à tous les autres. *Référence : [issue #85](https://github.com/MTES-MCT/metadata-postgresql/issues/85).*

NB : Afin d'assurer l'homogénéité visuelle des boutons avec menus, le **bouton d'aide à la saisie des géométries** qui, en mode édition, est associé aux métadonnées de type géométrique, adopte un nouveau fonctionnement :
cliquer brièvement active/désactive la visualisation de la géométrie saisie, cliquer en maintenant appuyé quelques secondes fait apparaître le menu.  *Référence : [issue #81](https://github.com/MTES-MCT/metadata-postgresql/issues/81).*


## Traitements automatiques sur les descriptifs PostgreSQL

Plume 0.6 bêta ajoute trois paramètres de configuration, accessibles dans l'onglet *Avancé* de la ![configuration.svg](../../plume/icons/general/configuration.svg) boîte de dialogue de paramétrage, qui visent à automatiser des opérations récurrentes souvent utiles sur le contenu du descriptif PostgreSQL hors fiche de métadonnées.

« *Nettoyer le descriptif PostgreSQL* » permet ainsi d'automatiser la suppression des informations écrites dans le descriptif PostgreSQL à l'extérieur de la fiche de métadonnées. Celles-ci sont normalement préservées par Plume, néanmoins l'administrateur pourrait préférer les supprimer dès lors que leur contenu a été reporté dans la fiche de métadonnées (potentiellement automatiquement là aussi, grâce aux fonctionnalités de [calcul](../usage/metadonnees_calculees.md) de Plume).

Trois options sont possibles :
* « *Jamais* » (défaut) pour préserver le descriptif hors fiche de métadonnées.
* « *À l'initialisation de la fiche* » pour supprimer les informations hors fiche de métadonnées lorsque celle-ci est créée (à la première sauvegarde). Si du texte est de nouveau saisi par la suite, il sera préservé.
* « *Toujours* » pour systématiquement supprimer les informations hors fiche de métadonnées lorsque la fiche est sauvegardée.

« *Copier le libellé du jeu de données dans le descriptif PostgreSQL* » et « *Copier la description du jeu de données dans le descriptif PostgreSQL* » permettent d'inscrire automatiquement le libellé et/ou la description du jeu de données au début du descriptif lors de l'enregistrement de la fiche.

Ces derniers paramètres visent notamment à faciliter deux usages :
* Pour une personne qui consulterait directement le descriptif PostgreSQL d'une table, par exemple dans pgAdmin, le format JSON-LD n'est pas aisé à lire. Trouver les informations les plus importantes au début du descriptif est facilitateur.
* AsgardMenu permet d'[extraire les libellés des tables](https://snum.scenari-community.org/Asgard/Documentation/co/SEC_NommageObjets.html#N0L2UPcCthkfUY71ywBLmi) de leur descriptif PostgreSQL grâce à une expression régulière. En activant *Copier le libellé du jeu de données dans le descriptif PostgreSQL*, le libellé sera placé en début de descriptif et séparé du reste par un retour à la ligne.

*Référence : [issue #62](https://github.com/MTES-MCT/metadata-postgresql/issues/62).*

## Registre de Plume

Plume dispose désormais d'un véritable **registre RDF**, accessible à l'adresse : https://registre.data.developpement-durable.gouv.fr/plume.

Ainsi, une personne ou une application qui consulte une fiche de métadonnées élaborée avec Plume peut maintenant interroger ce registre pour disposer d'informations sur les catégories de métadonnées communes et les vocabulaires contrôlés spécifiques à Plume.

Le raccourci « *plume:* » représente cet esapce de nommage dans les identifiants de catégories de métadonnées utilisés par les [modèles de fiches de métadonnées](../usage/modeles_de_formulaire.md#categories-de-metadonnees).

Par exemple, les URI http://registre.data.developpement-durable.gouv.fr/plume/isExternal (`plume:isExternal`) et http://registre.data.developpement-durable.gouv.fr/plume/CrpaAccessLimitations/L311-4 sont désormais interrogeables. Ils identifient respectivement la catégorie de métadonnées servant à distinguer les données produites par le service des données externes, et le terme de vocabulaire contrôlé indiquant que l'accès à la donnée est restreint en application de l'article L311-4 du code des relations entre le public et l'administration.

*Référence : [issue #32](https://github.com/MTES-MCT/metadata-postgresql/issues/32).*

## Schéma des métadonnées communes

Ajout de la catégorie `adms:status` - *Maturité du jeu de données* - aux métadonnées décrivant un jeu de données, avec deux vocabulaires contrôlés : un [vocabulaire spécifique à Plume correspondant aux codes *ProgressCode*](http://registre.data.developpement-durable.gouv.fr/plume/ISO19139ProgressCode) du standard ISO 19139 et le [vocabulaire *Dataset status* de la Commission européenne](https://op.europa.eu/en/web/eu-vocabularies/dataset/-/resource?uri=http://publications.europa.eu/resource/dataset/dataset-status).

La propriété équivalente pour les distributions `dcat:distribution / adms:status` - *Maturité de la distribution* - autorise maintenant également le vocabulaire basé sur les codes *ProgressCode* d'ISO 19139. Son libellé a par ailleurs été modifié.

Correction d'URI de termes et d'ensembles de termes de vocabulaires contrôlés qui présentaient à tort le protocole *https* au lieu de *http*.

***Attention :*** *Ces évolutions donnent lieu à une nouvelle version de l'extension PlumePg, la version 0.1.2, qui les répercute dans la table des catégories `z_plume.meta_categorie`. **Il est fortement recommandé aux utilisateurs de PlumePg de procéder à la mise à jour l'extension**, faute de quoi les modèles personnalisés définis via PlumePg ne seront plus disponibles pour les utilisateurs de Plume.*

*Pour cette version bêta, la rétro-compatibilité n'est pas assurée au niveau des fiches de métadonnées elles-mêmes. Si des métadonnées déjà saisies contiennent les URI erronnées susmentionnées, celles-ci ne seront pas correctement affichées dans l'interface de Plume.*

## Des libellés pour les services CSW

Plume permettait déjà de mémoriser des URL de base de services CSW pour éviter d'avoir à les ressaisir à chaque import de fiche. Il est désormais possible d'ajouter un libellé à ces URL pour retrouver plus facilement à quoi elles correspondent.

*Référence : [issue #95](https://github.com/MTES-MCT/metadata-postgresql/issues/95).*

## Sécurisation de l'activation du mode traduction et du changement de langue ou de modèle

L'utilisateur est désormais averti qu'il risque de perdre ses modifications non enregistrées lorsqu'il active ou désactive le [mode traduction](../usage/actions_generales.md#activation-du-mode-traduction) ![translation.svg](../../plume/icons/general/translation.svg) et lorsqu'il change la [langue principale de saisie](../usage/actions_generales.md#langue-principale-des-métadonnées) ou la [trame de formulaire](../usage/actions_generales.md#choix-de-la-trame-de-formulaire) ![template.svg](../../plume/icons/general/template.svg) (modèle de fiche de métadonnées).

Le message est similaire à celui qui apparaissait déjà lorsque l'utilisateur cliquait sur le bouton ![read.svg](../../plume/icons/general/read.svg) pour revenir du [mode édition au mode lecture](../usage/actions_generales.md#mode-lecture-mode-édition).

L'affichage de ces avertissements peut être désactivé dans la boîte de dialogue de configuration de Plume ![configuration.svg](../../plume/icons/general/configuration.svg).

*Références : [issue #78](https://github.com/MTES-MCT/metadata-postgresql/issues/78), [issue #88](https://github.com/MTES-MCT/metadata-postgresql/issues/88).*

## Gestion des dépendances Python

Consolidation du mécanisme d'import des bibliothèques python nécessaires au fonctionnement de Plume, afin de prendre en compte :
* Le cas d'un poste utilisateur disposant de plusieurs versions de QGIS basées sur des versions différentes de Python.
* Le cas d'un utilisateur remplaçant sa version de QGIS par une version basée sur une autre version de Python.

Dans ces deux cas, le mécanisme antérieur présumait que les bibliothèques étaient disponibles dès lors qu'elles avaient été installées une fois, alors que l'installation doit en fait être réalisée indépendamment pour chaque version de Python.

Le nouveau mécanisme (re-)contrôle les bibliothèques pour chaque version de QGIS (et donc de Python) après l'installation d'une nouvelle version de Plume.

*Référence : [issue #76](https://github.com/MTES-MCT/metadata-postgresql/issues/76).*


## Correction d'anomalies et divers

Correction de la fonctionnalité d'import depuis un fichier de métadonnées INSPIRE ou ISO 19115/19139 pour qu'elle reconnaisse l'élément `gmd:MD_Metadata` qu'il soit à la racine ou englobé dans un élément de réponse comme `csw:GetRecordByIdResponse`. À défaut, les tentatives d'import produisaient souvent une fiche vide. Cette évolution rend aussi plus permissif l'import depuis les CSW, même s'il n'y avait pas nécessairement de besoin identifié à date (mêmes commandes de traitement pour les deux sources). *Référence : [issue #93](https://github.com/MTES-MCT/metadata-postgresql/issues/93).*

Un rôle qui n'est pas propriétaire d'une table/vue et n'a donc accès à ses métadonnées qu'en lecture peut désormais réaliser toutes les actions normalement disponibles dans ce mode : choisir la langue principale d'affichage des métadonnées, choisir le modèle de fiche de métadonnées, copier la fiche, exporter la fiche. *Référence : [issue #94](https://github.com/MTES-MCT/metadata-postgresql/issues/94).*

Correction d'une anomalie qui provoquait l'apparition de boutons moins parasites lors de l'activation ou la désactivation de la saisie manuelle. *Référence : [issue #89](https://github.com/MTES-MCT/metadata-postgresql/issues/89).*

Correction d'une anomalie qui altérait l'ordre de préférence des langues défini par l'utilisateur.

Correction d'une anomalie qui provoquait des erreurs lors de l'usage d'un modèle de fiche de métadonnées affectant explicitement un onglet à une catégorie commune dont le chemin comporte des majuscules. 

Correction d'une anomalie qui faisait qu'une fiche de métadonnées ouverte en mode édition lors de la fermeture de Plume réapparaissait comme fiche courante si Plume était rouvert avec une ressource sélectionnée autre qu'une couche PostgreSQL. *Référence : [issue #83](https://github.com/MTES-MCT/metadata-postgresql/issues/83).*

Correction d'une anomalie qui faisait que fermer Plume avec une fiche en mode édition puis rouvrir immédiatement Plume montrait à l'utilisateur l'écran d'accueil... avec tous les boutons de la barre d'outils actifs.  *Référence : [issue #83](https://github.com/MTES-MCT/metadata-postgresql/issues/83).*

Suppression d'un cadre surnuméraire dans les onglets des fiches de métadonnées. *Référence : [issue #80](https://github.com/MTES-MCT/metadata-postgresql/issues/80).*