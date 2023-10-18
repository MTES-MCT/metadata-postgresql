# Publication d'une nouvelle version

Ci-après le processus de préparation de la publication d'une nouvelle version de Plume, étape par étape.


## Mise à jour des bibliothèques Python

Les bibliothèques Python dont dépend Plume sont listées dans le fichier [`plume/requirements.txt`](https://github.com/MTES-MCT/metadata-postgresql/blob/main/plume/requirements.txt). Leurs fichiers d'installation sont de plus intégrés au plugin, afin que celui-ci puisse être installé en toutes circonstances, indépendemment de la configuration réseau de l'utilisateur (proxy, etc.). Les paquets sont stockés au format *wheel* dans le répertoire `plume/bibli_install`.

Avant de publier une nouvelle version de Plume, il convient de vérifier si de nouvelles versions sont disponibles pour chacune des bibliothèques, en veillant à la compatibilité des bibliothèques entre elles et avec les différentes versions de Python prises en charge. Par exemple les versions d'*importlib-metadata* supérieures à la 4.13.0 n'étaient pas compatibles avec RDFLib 6.3.2 - cf. [issue #145](https://github.com/MTES-MCT/metadata-postgresql/issues/145). Pour l'heure, Plume affiche une compatibilité avec Python 3.7 ou supérieur. À noter toutefois que Python 3.7 n'est plus pris en charge par RDFLib à compter de la version 7.0.0 - cf. [issue #168](https://github.com/MTES-MCT/metadata-postgresql/issues/168).


## Numéro de version

Le numéro de la nouvelle version doit être renseigné :
- Dans le paramètre `version` du fichier [`plume/metadata.txt`](https://github.com/MTES-MCT/metadata-postgresql/blob/main/plume/metadata.txt) destiné à QGIS.
- Dans les paramètres `PLUME_VERSION` (sous forme littérale) et `PLUME_VERSION_TPL` (tuple de chiffres) du fichier de configuration [`plume/config.py`](https://github.com/MTES-MCT/metadata-postgresql/blob/main/plume/config.py). 

`PLUME_VERSION` est une information importante, car le mécanisme de mise à jour des bibliothèques Python dont dépend Plume repose sur le fait que ce numéro est différent d'une version de Plume à l'autre. Pour que le processus de mise à jour ne se déclenche pas inutilement à chaque activation de Plume, mais uniquement lors de son installation initiale ou après une mise à jour, Plume compare le numéro de la version courante avec le numéro mémorisé dans le fichier de configuration `QGIS3.ini` pour la version de QGIS considérée. Par exemple, `Generale\3-22-8=v1.1.0` indique que la version de Plume installée sous QGIS 3.22.8 est la v1.1.0. Si les deux numéros sont différents, le processus de mise à jour selon [`plume/requirements.txt`](https://github.com/MTES-MCT/metadata-postgresql/blob/main/plume/requirements.txt) se lance et la version référencée dans le fichier de configuration est actualisée. Ce mécanisme est géré par `plume.bibli_install.manageLibrary`.

Il est donc important de ne pas diffuser aux utilisateurs plusieurs versions portant le même numéro, y compris à des fins de tests. Il est tout à fait possible d'inclure un suffixe dans le numéro de version, par exemple `v1.1.0-beta`, étant entendu que celui-ci n'apparaîtra pas dans `PLUME_VERSION_TPL` (qui n'est pas utilisé pour l'heure).

La numérotation des versions suit les règles de la [gestion sémantique de version](https://semver.org/lang/fr/), résumée comme suit :

> Étant donné un numéro de version MAJEUR.MINEUR.CORRECTIF, il faut incrémenter :
>    * le numéro de version MAJEUR quand il y a des changements non rétrocompatibles,
>    * le numéro de version MINEUR quand il y a des ajouts de fonctionnalités rétrocompatibles,
>    * le numéro de version de CORRECTIF quand il y a des corrections d’anomalies rétrocompatibles.

Le fichier `plume/config.py` comprend également les paramètres `PLUME_PG_MIN_VERSION` et `PLUME_PG_MAX_VERSION`, qui déterminent les versions de l'extension PostgreSQL PlumePg qui sont ou non compatibles avec cette version de Plume. Ils sont utilisés par la requête de contrôle {py:func}`~plume.pg.queries.query_plume_pg_check` du module {py:mod}`plume.pg.queries`, grâce à laquelle Plume détermine s'il doit considérer que PlumePg est disponible sur une base de données ou non. Les versions non compatibles sont ignorées.

## Mise en cohérence des données

Entre le plugin QGIS, l'extension PostgreSQL PlumePg et la documentation technique, certaines données de Plume sont dupliquées, et il importe de maintenir leur cohérence. Des fonctions d'administrations sont prévues pour faciliter ces opérations.

- [Mise à jour de la liste des métadonnées communes de la documentation technique](./memo.md#mise-à-jour-de-la-liste-des-métadonnées-communes-de-la-documentation-technique).
- [Mise à jour des catégories communes dans les scripts de PlumePg](./memo.md#mise-à-jour-des-catégories-communes-dans-les-scripts-de-plumepg).
- [Mise à jour des copies locales des modèles pré-configurés de PlumePg](./memo.md/#modifier-les-modèles-pré-configurés-de-plumepg).

À noter que le module {py:mod}`admin.consistency` de la recette de Plume inclut des tests qui veillent à la cohérence des données et peuvent alerter sur le fait que les fonctions susmentionnées doivent être exécutées.

La gestion des modèles requiert aussi, dans le module [`plume.mapping_template`](https://github.com/MTES-MCT/metadata-postgresql/blob/main/plume/mapping_templates.py), un ensemble de données qui décrivent les champs des tables et les valeurs des types énumérés de PlumePg. Ces informations ne peuvent être saisies que manuellement, par contre des tests vérifient que les noms des champs et des valeurs énumérées renseignées dans ce module correspondent exactement à celles définies par PlumePg.

## Tests

### Recette des mécaniques internes

### Recette de l'interface utilisateur


## Mise à jour de la documentation utilisateur

La documentation technique est présumée mise à jour au fil de l'eau.


## Rédaction d'une note de version

Pour l'heure, les notes de version sont publiées dans la documentation technique.

## Génération et diffusion du paquet Debian PlumePg pour EcoSQL

## Diffusion de PlumePg sur les serveurs EOLE

## Génération d'un ZIP du plugin QGIS

## Création d'une `release` sur GitHub

## Diffusion de Plume sur le dépôt des plugin QGIS du pôle ministériel 

## Information des utilisateurs

Mise à jour sur l'intranet, mail à la liste de diffusion labo.postgis, site OSMOSE du GT PostGIS.



