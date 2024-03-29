# Installation et gestion de l'extension PostgreSQL *PlumePg*

L'extension PostgreSQL *PlumePg* est un composant optionnel de Plume, qui ouvre la possibilité d'utiliser des [modèles de formulaire](./modeles_de_formulaire.md) et d'[enregistrer les dates de création et dernière modification des tables](#activation-de-lenregistrement-des-dates).

[Compatibilité](#compatibilité) • [Installation](#installation) • [Localisation des objets de l'extension](#localisation-des-objets-de-lextension) • [Privilèges](#privilèges) • [Cohabitation avec *Asgard*](#cohabitation-avec-asgard) • [Mise à jour](#mise-à-jour) • [Désinstallation](#désinstallation) • [Activation de l'enregistrement des dates](#activation-de-lenregistrement-des-dates) • [Usage des modèles de formulaires](#usage-des-modèles-de-formulaires) • [Sauvegarde et restauration de la base](#sauvegarde-et-restauration-de-la-base) • [Gestion de *PlumePg* via Plume](#gestion-de-plumepg-via-plume)

## Compatibilité

| Version | Compatibilité | Remarques | Modalités de test |
| --- | --- | --- | --- |
| PostgreSQL <= 9.6 | non | *PlumePg* requiert la prise en charge des tables partitionnées, introduites par PostgreSQL 10. | |
| PostgreSQL 10 | oui | Nécessite l'extension `pgcrypto`. | 2023.06.16. PostgreSQL 10.12 + PlumePg 0.3.0 + pgcrypto 1.3 + Asgard 1.4.0[^withasgard]. |
| PostgreSQL 11 | oui | Nécessite l'extension `pgcrypto`. | 2023.06.16. PostgreSQL 11.9 + PlumePg 0.3.0 + pgcrypto 1.3 + Asgard 1.4.0. |
| PostgreSQL 12 | oui | Nécessite l'extension `pgcrypto`. | 2023.06.16. PostgreSQL 12.4 + PlumePg 0.3.0 + pgcrypto 1.3 + Asgard 1.4.0. |
| PostgreSQL 13 | oui | | 2023.06.16. PostgreSQL 13.0 + PlumePg 0.3.0 + pgcrypto 1.3[^withcrypto] + Asgard 1.4.0. |
| PostgreSQL 14 | oui | | 2023.06.16. PostgreSQL 14.2 + PlumePg 0.3.0 + pgcrypto 1.3 + Asgard 1.4.0. |
| PostgreSQL 15 | oui | | 2023.06.16. PostgreSQL 15.0 + PlumePg 0.3.0 + pgcrypto 1.3 + Asgard 1.4.0. |

[^withasgard]: L'extension PostgreSQL *Asgard* n'est en aucune façon requise pour utiliser Plume et *PlumePg*. Les tests faisant intervenir *Asgard* s'assure simplement que, dans le cas où les deux extensions sont présentes, *Asgard* gère correctement les droits sur les objets de *PlumePg*. Cf. [Cohabitation avec *Asgard*](#cohabitation-avec-asgard)

[^withcrypto]: Les tests sont réalisés avec le fichier de contrôle standard de *PlumePg*, unique pour toutes les versions de PostgreSQL et qui requiert `pgcrypto`. Il est donc vérifié que celui-ci peut être installé pour toutes les versions, y compris PostgreSQL 13, 14 et 15, pour lesquelles *PlumePg* n'utilise ensuite aucune de ses fonctionnalités.

## Installation 

Les fichiers d'installation de *PlumePg* se trouvent dans le dossier [`postgresql`](/postgresql) du Git :
- `plume_pg--x.x.x.sql` contient le code de la version `x.x.x` de l'extension *PlumePg*. Celui-ci s'exécute lorsqu'elle est installée sur une base.
- [`plume_pg.control`](/postgresql/plume_pg.control) contient quelques métadonnées et des informations de paramétrage.

Ces deux fichiers doivent être copiés dans le répertoire des extensions du serveur. Son chemin varie selon l'environnement d'installation, mais il est vraisemblable qu'il soit de la forme `C:\Program Files\PostgreSQL\xx\share\extension` sous Windows et `/usr/share/postgresql/xx/extension` sous Linux, `xx` étant la version de PostgreSQL.

L'activation de *PlumePg* sur une base passe par une simple commande `CREATE EXTENSION`, qui **doit être exécutée par un super-utilisateur** (création de déclencheurs sur évènement). Pour PostgreSQL 12 et les versions antérieures, il est nécessaire d'installer préalablement l'extension [`pgcrypto`](https://www.postgresql.org/docs/12/pgcrypto.html), sur laquelle *PlumePg* s'appuie pour la génération des UUID[^pgcrypto]. Il s'agit d'une extension standard de PostgreSQL, qui est en principe disponible dans toutes les distributions des versions de PostgreSQL compatibles avec *PlumePg*.

```sql

CREATE EXTENSION IF NOT EXISTS pgcrypto ;
CREATE EXTENSION plume_pg ;

```

Une autre possibilité est d'exécuter la commande `CREATE EXTENSION` avec l'option `CASCADE`, ce qui installe automatiquement toutes les extensions marquées comme requises dans `plume_pg.control` :

```sql

CREATE EXTENSION plume_pg CASCADE ;

```

[^pgcrypto]: *PlumePg* se sert de la fonction `gen_random_uuid()` pour générer des UUID. Pour les versions 10, 11, et 12 de PostgreSQL, elle est fournie par l'extension *pgcrypto*. Pour les versions 13 et supérieures, cette fonction est incluse dans le coeur de PostgreSQL (cf. [documentation de PostgreSQL](https://www.postgresql.org/docs/13/functions-uuid.html)), installer `pgcrypto` n'est donc en principe plus nécessaire et il pourrait être pertinent de modifier le fichier `plume_pg.control` pour retirer `pgcrypto` de la liste des extensions requises.

L'installation est à réaliser par l'administrateur du serveur PostgreSQL. Il n'était pas pertinent que celle-ci puisse se faire via l'interface QGIS de Plume, dont la grande majorité des utilisateurs ne disposera pas des droits nécessaires sur le serveur PostgreSQL. Par contre, [*AsgardManager*](https://snum.scenari-community.org/Asgard/Documentation/#SEC_AsgardManager) propose cette fonctionnalité, via son menu [`Gestion de la base`](https://snum.scenari-community.org/Asgard/Documentation/#SEC_MenuGestionBase).

## Localisation des objets de l'extension

Tous les objets de l'extension sont créés dans le schéma `z_plume`.

## Privilèges

Les données du schéma `z_plume` alimentent le plugin QGIS et doivent dès lors être accessibles à tous ses utilisateurs. Pour simplifier la gestion des droits, le pseudo rôle `public` reçoit automatiquement les privilèges suivants lorsque *PlumePg* est installée sur une base :
- `USAGE` sur le schéma `z_plume` ;
- `SELECT` sur toutes les tables et vues de ce schéma.

Des droits étendus sont conférés sur la table `z_plume.stamp_timestamp`, permettant au propriétaire d'une table - et seulement à lui - de modifier manuellement les dates enregistrées pour cette table. *NB : Ce contrôle d'accès est réalisé par un déclencheur et non des politiques de sécurité niveau ligne, car l'usage de ces dernières par les extensions provoque actuellement des erreurs en cas de sauvegarde/restauration.*

## Cohabitation avec *Asgard*

Il n'y a pas de lien fonctionnel direct entre *PlumePg* et l'extension [*Asgard*](https://snum.scenari-community.org/Asgard/Documentation/), outil créé dans le cadre du GT PostGIS pour faciliter la gestion des droits.

Si l'extension *PlumePg* est installée sur une base disposant déjà d'*Asgard*, `g_admin` sera automatiquement désigné comme *producteur* du schéma et `public` en sera fait *lecteur*[^asgard-version]. Il s'agit juste de faciliter le travail de l'administrateur, cette opération ne crée aucune adhérence durable. Il est ensuite tout à fait possible, sans que cela ne pose de problème particulier, y compris lors des futures montées de version de *PlumePg* :
- de choisir d'autres rôles comme *producteur*, *éditeur* et *lecteur* de `z_plume`. *Attention tout de même à sélectionner un lecteur dont sont membres les rôles de connexion de tous les utilisateurs potentiels du plugin QGIS !*
- de déréférencer le schéma `z_plume` pour gérer ses droits hors d'*Asgard* ;
- de désinstaller *Asgard*.

[^asgard-version]: Sous réserve d'utiliser une version d'Asgard supérieure ou égale à la 1.3.2. Dans les versions antérieures, les schémas créés par les extensions n'étaient pas automatiquement référencés.

## Mise à jour

Comme pour l'installation, les fichiers de mise à jour sont disponibles dans le dossier [`postgresql`](/postgresql) du Git :
- un ou plusieurs fichiers `plume_pg--x.x.x--y.y.y.sql`, qui sont des scripts de passage de la version `x.x.x` à la version `y.y.y`. Plusieurs de ces scripts peuvent s'exécuter à la suite lors d'une mise à jour (`plume_pg--x.x.x--x1.x1.x1.sql`, `plume_pg--x1.x1.x1--x2.x2.x2.sql`, ..., `plume_pg--xn.xn.xn--y.y.y.sql`).
- un nouveau fichier [`plume_pg.control`](/postgresql/plume_pg.control) remplaçant le précédent. Ce fichier change en principe peu d'une version à l'autre, si ce n'est pour la *version par défaut* qu'il spécifie, qui sera toujours la version la plus récente.
- un fichier `plume_pg--y.y.y.sql` contenant le code complet de la version `y.y.y` de l'extension *PlumePg*. Celui-ci n'est pas utilisé lors de la mise à jour, mais pourra servir par la suite, notamment en cas de sauvegarde/restauration de la base, ou pour l'installation de *PlumePg* sur une nouvelle base.

Cf. [Installation](#installation) pour l'emplacement du répertoire où ces fichiers doivent être copiés.

Sur toutes les bases où *PlumePg* était installée, on exécutera ensuite :

```sql

ALTER EXTENSION plume_pg UPDATE TO 'y.y.y' ;

```

Sauf à cibler une version qui ne serait pas la dernière, il est souvent plus simple de ne pas spécifier le numéro de version et d'effectuer la mise à jour sur la version par défaut définie par `plume_pg.control` :

```sql

ALTER EXTENSION plume_pg UPDATE ;

```

## Désinstallation

Pour désinstaller *PlumePg* d'une base : 

```sql

DROP EXTENSION plume_pg ;

```

La désinstallation entraîne la perte définitive de tous les [modèles de formulaire](./modeles_de_formulaire.md).

*NB. Si le schéma `z_plume` existait avant l'installation de l'extension, il ne sera pas marqué comme dépendant de l'extension et ne sera donc pas supprimé en cas de désinstallation. Tout son contenu le sera, par contre.*

## Activation de l'enregistrement des dates

*PlumePg* propose un système pour garder une trace des dates de création et dernière modification des tables. Assez rudimentaire, il ne prend en charge que les tables simples, ignorant notamment les vues et vues matérialisées.

Les dates sont enregistrées dans la table `z_plume.stamp_timestamp`. Son champ `relid` contient les identifiants PostgreSQL des tables (OID), son champ `created` les dates de création et son champ `modified` les dates de dernière modification.

À l'installation de *PlumePg*, les fonctionnalités d'enregistrement des dates de création et dernière modification des tables sont inactives. La table `z_plume.stamp_timestamp` est et restera vide sans intervention de l'administrateur.

Dès lors que l'administrateur le souhaite, deux stratégies peuvent être mises en oeuvre : soit enregistrer automatiquement les dates pour toutes les tables dès leur création, soit enregistrer les dates de dernière modification uniquement pour certaines tables explicitement désignées.

### Suivi automatique intégral

Pour mettre en place le suivi intégral, on activera les trois déclencheurs sur évènement de *PlumePg*.

```sql

ALTER EVENT TRIGGER plume_stamp_table_creation ENABLE ;
ALTER EVENT TRIGGER plume_stamp_table_modification ENABLE ;
ALTER EVENT TRIGGER plume_stamp_table_drop ENABLE ;

```

`plume_stamp_table_creation` se charge d'enregistrer les dates de création des tables dans `z_plume.stamp_timestamp` et crée sur les nouvelles tables les déclencheurs `plume_stamp_data_edit` qui assureront le suivi des modifications des données.

`plume_stamp_table_modification` met à jour la date de dernière modification en cas de modification de structure des tables (commandes `ALTER TABLE`).

`plume_stamp_table_drop` efface de `z_plume.stamp_timestamp` les lignes correspondant aux tables qui viennent d'être supprimées.

### Suivi au cas par cas

Pour n'activer le suivi des modifications que sur certaines tables explicitement désignées, il faut laisser inactif le déclencheur sur évènement `plume_stamp_table_creation`.

```sql

ALTER EVENT TRIGGER plume_stamp_table_modification ENABLE ;
ALTER EVENT TRIGGER plume_stamp_table_drop ENABLE ;

```

Il faut alors lancer la fonction `z_plume.stamp_create_trigger` sur une table pour commencer à enregistrer ses dates de modification, tant les modifications des données que celles de la structure. 

```sql

SELECT z_plume.stamp_create_trigger('schema_name.table_name'::regclass) ;

```

La fonction renvoie `True` si la création du déclencheur a fonctionné, `False` sinon. Elle doit être exécutée par le propriétaire de la table.

Une alternative consisterait à activer `plume_stamp_table_creation` en supprimant le suivi des modifications sur certaines tables qui ne le justifient pas :

```sql

DROP TRIGGER plume_stamp_data_edit ON schema_name.table_name ;
DELETE FROM z_plume.stamp_timestamp WHERE relid = 'schema_name.table_name'::regclass ;

```

### Reprise de l'existant

Que `plume_stamp_table_creation` soit actif ou non, les déclencheurs `plume_stamp_data_edit` qui mettent à jour la date de dernière modification lorsque le contenu de leur table est modifié ne sont pas automatiquement créés sur les tables existantes.

Plutôt que de lancer sur chaque table la fonction `z_plume.stamp_create_trigger`, il est possible d'utiliser la fonction `z_plume.stamp_create_triggers`, qui permet de créer les déclencheurs pour toutes les tables d'un ou plusieurs schémas déterminés.

Pour créer des déclencheurs `plume_stamp_data_edit` sur les tables de tous les schémas hors schémas système (`information_schema` et tous les schémas dont le nom commence par `'pg_'`) :

```sql

SELECT * FROM z_plume.stamp_create_triggers() ;

```

Pour créer les déclencheurs sur les tables d'un schéma :

```sql

SELECT * FROM z_plume.stamp_create_triggers('schema_name') ;

```

Pour créer les déclencheurs sur les tables de plusieurs schémas :

```sql

SELECT * FROM z_plume.stamp_create_triggers(schemas_include:=ARRAY['schema_name_1', 'schema_name_2']) ;

```

Pour créer les déclencheurs sur les tables de tous les schémas sauf exceptions listées :

```sql

SELECT * FROM z_plume.stamp_create_triggers(schemas_exclude:=ARRAY['public', 'schema_name']) ;

```

La fonction renvoie la liste des tables des schémas cibles, en indiquant dans le champ `result` si la création du déclencheur sur la table a réussi (`'success'`), si elle a échoué (`'failure'`, le détail de l'erreur sera alors 
précisé par des messages) ou si le déclencheur existait déjà (`'trigger already exists'`), la fonction n'ayant alors aucun effet.


### Intégration directe dans les métadonnées

Pour ne pas trop affecter les performances et laisser au producteur de la donnée la maîtrise de ces informations, les dates ne sont pas immédiatement mises à jour dans les fiches de métadonnées, seulement dans la table `stamp_timestamp`, qui peut être considérée comme un espace de stockage temporaire. Le plugin QGIS permet de les importer facilement lors de l'édition d'une fiche, soit à la demande en cliquant sur un bouton, soit automatiquement à l'ouverture de la fiche (cf. [Métadonnées calculées](./metadonnees_calculees.md)).

Il est toutefois possible de forcer l'actualisation au fil de l'eau de la date de dernière modification en activant le déclencheur `stamp_timestamp_to_metadata` défini sur la table `stamp_timestamp`.

```sql

ALTER TABLE z_plume.stamp_timestamp ENABLE TRIGGER stamp_timestamp_to_metadata ;

```

Ceci ne vaudra que pour les tables qui ont déjà une fiche de métadonnées, raison pour laquelle les dates de création ne sont pas concernées.

Lorsque ce déclencheur est actif, il n'y a aucun intérêt à utiliser les fonctionnalités de calcul pour la date de dernière modification (catégorie `dct:modified`).


### Observations sur la gestion des suppressions de tables 

Quelle que soit la stratégie choisie, il n'est pas indispensable d'activer le déclencheur sur évènement `plume_stamp_table_drop`. À défaut, il faudra éliminer régulièrement les lignes de `z_plume.stamp_timestamp` correspondant aux tables qui n'existent plus avec la fonction `z_plume.stamp_clean_timestamp`.

```sql

SELECT z_plume.stamp_clean_timestamp() ;

```

La fonction renvoie le nombre de lignes supprimées de `z_plume.stamp_timestamp`. Elle doit être exécutée par le propriétaire de `z_plume.stamp_timestamp`.

À noter qu'il n'est généralement pas intéressant de conserver des lignes mortes dans la `z_plume.stamp_clean_timestamp`, sauf à disposer d'un moyen pour retrouver le nom de la table à partir de son identifiant (OID) désormais non référencé dans `pg_class`.


### Fausses modifications 

Le mécanisme mis en place par *PLumePg* peut donner lieu à des faux positifs, soit des cas où la date de dernière modification sera actualisée sans que la table ni son contenu n'aient véritablement changé.

Le déclencheur sur évènement `plume_stamp_table_modification` est ainsi activé par toutes les commandes `ALTER TABLE`, y compris celles qui n'affectent pas réellement la table, comme un changement de nom qui conserve le nom d'origine.

Les déclencheurs `plume_stamp_data_edit` sont activés par toutes les commandes `INSERT`, `UPDATE`, `DELETE` et `TRUNCATE`, y compris celles qui - sans pour autant échouer - n'ont aucun effet. Par exemple une commande `UPDATE` ou `DELETE` telle qu'aucune ligne ne remplit la condition de sa clause `WHERE`. Il paraissait préférable d'avoir recours à des déclencheurs `ON EACH STATEMENT` qu'à des déclencheurs `ON EACH ROW`, certes moins susceptibles de retenir des fausses modifications mais susceptibles d'allonger considérablement le temps d'exécution des requêtes.


## Usage des modèles de formulaires

Cf. [Modèles de formulaires](./modeles_de_formulaire.md).


## Sauvegarde et restauration de la base

Pour que les données de *PlumePg* soient préservées lors de la restauration, notamment les [modèles de formulaire](./modeles_de_formulaire.md), il est essentiel de **ne pas chercher à réinstaller manuellement l'extension sur la base de restauration**. Tout est automatique. On veillera seulement à ce que :
- les fichiers d'installation de *PlumePg* soient disponibles dans le répertoire des extensions du serveur de restauration (cf. [Installation](#installation) pour l'emplacement de ce répertoire) ;
- la version par défaut de *PlumePg* sur le serveur de restauration soit identique à celle qui est effectivement installée sur la base à sauvegarder.

Cette *version par défaut* apparaît dans le fichier `plume_pg.control` et peut également être consultée avec la requête (à exécuter sur n'importe quelle base du serveur de restauration) :

```sql

SELECT name, default_version FROM pg_available_extensions WHERE name = 'plume_pg' ;

```

Pour connaître la version installée sur la base à sauvergarder, on pourra par exemple exécuter sur celle-ci :


```sql

SELECT name, installed_version FROM pg_available_extensions WHERE name = 'plume_pg' ;

```

De manière très classique, le processus de restauration est le suivant :
1. Sauvegarder la base originale, par la méthode habituelle.
2. Créer une base vierge.
3. Lancer la restauration sur cette base vierge, par la méthode habituelle.

### Considérations spécifiques au mécanisme d'enregistrement des dates

En l'état actuel, au contraire des informations relatives aux modèles, les dates stockées dans la table `z_plume.stamp_timestamp` ne sont pas conservées en cas de sauvegarde et restauration de la base. Il faudra qu'elles aient été préalablement intégrées aux fiches de métadonnées pour ne pas être **perdues**. Cette intégration s'effectue en principe lors de l'édition des fiches de métadonnées avec le plugin QGIS, sous réserve d'avoir activé la [fonctionnalité de calcul](./metadonnees_calculees.md) pour les catégories `dct:created` et `dct:modified`. Pour les dates de dernières modifications, elle peut aussi être réalisée automatiquement côté serveur en activant le déclencheur prévu à cette fin - cf. [Intégration directe dans les métadonnées](#intégration-directe-dans-les-métadonnées).

Les déclencheurs et déclencheurs sur évènement retrouvent leur état initial après la restauration et **devront donc être réactivés manuellement** d'autant que de besoin - cf. [Activation de l'enregistrement des dates](#activation-de-lenregistrement-des-dates). Il n'est pas nécessaire de chercher à recréer les déclencheurs `plume_stamp_data_edit` sur les tables, ils sont pour leur part restaurés.

## Gestion de *PlumePg* via Plume

*Voir aussi [Gestion des modèles via Plume](./modeles_de_formulaire.md#gestion-des-modèles-via-plume) pour les modalités d'administration des modèles de fiches de métadonnées avec l'interface de Plume.*

Le module `plume.pg.queries` met à disposition des requêtes permettant la réalisation via l'interface de Plume des actions les plus simples de gestion de *PlumePg*.

Les actions disponibles dépendent des droits de l'utilisateur et de l'état de l'extension sur la base considérée. Pour les connaître, il suffit d'exécuter la requête `query_plume_pg_status`.

```python

import psycopg2
from plume.pg import queries

conn = psycopg2.connect(connection_string)

with conn:
	with conn.cursor() as cur:
	
		cur.execute(
			*queries.query_plume_pg_status()
			)
		actions = cur.fetchone()[0]

conn.close()

```

*`connection_string` est la chaîne de connexion à la base de données PostgreSQL.*

Si `actions` vaut `None`, aucune action n'est possible. Sinon, `actions` est une liste pouvant contenir les mots-clés énumérés dans le tableau suivant. À chaque mot-clé correspond une action qui pourra être proposée à l'utilisateur via le menu *Configuration* de la barre d'outils ![configuration.svg](../../plume/icons/general/configuration.svg).

En pratique, toutes les actions requièrent pour l'heure un super-utilisateur.

| Mot-clé | Nom de l'action | Infobulle | Requête d'action |
| --- | --- | --- | --- |
| `CREATE` | *Activer PlumePg* | Active l'extension PostgreSQL *PlumePg* sur la base courante. | `query_plume_pg_create` |
| `UPDATE` | *Mettre à jour PlumePg* | Met à jour l'extension PostgreSQL *PlumePg* sur la base courante. | `query_plume_pg_update` |
| `DROP` | *Désactiver PlumePg* | Désactive l'extension PostgreSQL *PlumePg* sur la base courante. _**Attention !** Cette action entraînera la perte de tous les modèles personnalisés et des dates de création/modification enregistrées qui n'auraient pas été reportées dans les fiches de métadonnées._ | `query_plume_pg_drop` |
| `STAMP RECORDING ENABLE` | *Activer le suivi des dates par PlumePg* | Active sur la base courante l'ensemble des fonctionnalités de suivi automatique des dates de création et modification des tables mises à disposition par l'extension PostgreSQL *PlumePg*. | `query_stamp_recording_enable` |
| `STAMP RECORDING DISABLE` | *Désactiver le suivi des dates par PlumePg* | Désactive intégralement les fonctionnalités de suivi automatique des dates de création et modification des tables mises à disposition par l'extension PostgreSQL *PlumePg* sur la base courante. | `query_stamp_recording_disable` |
| `STAMP TO METADATA ENABLE` | *Activer la retranscription automatique des dates* | Active sur la base courante la fonctionnalité de l'extension PostgreSQL *PlumePg* qui copie automatiquement les dates de modification des tables dans les fiches de métadonnées. *NB : ce mécanisme est inutile si le suivi des dates est inactif. Il peut notablement ralentir l'exécution de certaines requêtes de mise à jour des données.* | `query_stamp_to_metadata_enable` |
| `STAMP TO METADATA DISABLE` | *Désactiver la retranscription automatique des dates* | Désactive sur la base courante la fonctionnalité de l'extension PostgreSQL *PlumePg* qui copie automatiquement les dates de modification des tables dans les fiches de métadonnées. | `query_stamp_to_metadata_disable` |

Chaque action est exécutée par une requête sur le serveur PostgreSQL, qui peut être générée grâce aux fonctions du module `plume.pg.queries` listées dans la colonne *Requêtes d'action* du tableau ci-avant.

Par exemple, pour l'activation de l'extension : 
```python

import psycopg2
from plume.pg import queries

conn = psycopg2.connect(connection_string)

with conn:
	with conn.cursor() as cur:
	
		cur.execute(
			*queries.query_plume_pg_create()
			)

conn.close()

```

*`connection_string` est la chaîne de connexion à la base de données PostgreSQL.*

Après l'exécution d'une action, il sera nécessaire de re-exécuter la requête générée par `query_plume_pg_status` et d'actualiser en conséquence les actions propsées à l'utilisateur dans le menu *Configuration*.
