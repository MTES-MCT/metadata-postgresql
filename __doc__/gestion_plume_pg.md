# Installation et gestion de l'extension PostgreSQL *PlumePg*

L'extension PostgreSQL *PlumePg* est un composant optionnel de Plume, qui ouvre la possibilité d'utiliser des [modèles de formulaire](/__doc__/08_modeles_de_formulaire.md).

## Compatibilité

| Version | Compatibilité | Remarques |
| --- | --- | --- |
| PostgreSQL 9.5 | à évaluer | nécessite l'extension `pgcrypto` |
| PostgreSQL 10 | oui | nécessite l'extension `pgcrypto` |
| PostgreSQL 11 | à évaluer | nécessite l'extension `pgcrypto` |
| PostgreSQL 12 | à évaluer | nécessite l'extension `pgcrypto` |
| PostgreSQL 13 | à évaluer | |
| PostgreSQL 14 | à évaluer | |

## Installation 

Les fichiers d'installation de *PlumePg* se trouvent dans le dossier [`postgresql`](/postgresql) du Git :
- `plume_pg--x.x.x.sql` contient le code de la version `x.x.x` de l'extension *PlumePg*. Celui-ci s'exécute lorsqu'elle est installée sur une base.
- [`plume_pg.control`](/postgresql/plume_pg.control) contient quelques métadonnées et des informations de paramétrage.

Ces deux fichiers doivent être copiés dans le répertoire des extensions du serveur. Son chemin varie selon l'environnement d'installation, mais il est vraisemblable qu'il soit de la forme `C:\Program Files\PostgreSQL\xx\share\extension` sous Windows et `/usr/share/postgresql/xx/extension` sous Linux, `xx` étant la version de PostgreSQL.

L'activation de *PlumePg* sur une base passe par une simple commande `CREATE EXTENSION`. Pour PostgreSQL 12 et les versions antérieures, il est toutefois nécessaire d'installer préalablement l'extension [`pgcrypto`](https://www.postgresql.org/docs/12/pgcrypto.html), sur laquelle *PlumePg* s'appuie pour la génération des UUID[^pgcrypto]. Il s'agit d'une extension standard de PostgreSQL, qui est en principe disponible dans toutes les distributions des versions de PostgreSQL compatibles avec *PlumePg*.

```sql

CREATE EXTENSION IF NOT EXISTS pgcrypto ;
CREATE EXTENSION plume_pg ;

```

Une autre possibilité est d'exécuter la commande `CREATE EXTENSION` avec l'option `CASCADE`, ce qui installe automatiquement toutes les extensions marquées comme requises dans `plume_pg.control` :

```sql

CREATE EXTENSION plume_pg CASCADE ;

```

[^pgcrypto]: *PlumePg* la fonction `gen_random_uuid()` pour générer des UUID. Pour les versions 10, 11, et 12 de PostgreSQL, elle est fournie par l'extension *pgcrypto*. Pour les versions 13 et supérieures, cette fonction est incluse dans le coeur de PostgreSQL (cf. [documentation de PostgreSQL](https://www.postgresql.org/docs/13/functions-uuid.html)), installer `pgcrypto` n'est donc en principe plus nécessaire et il pourrait être pertinent de modifier le fichier `plume_pg.control` pour retirer `pgcrypto` de la liste des extensions requises.

L'installation est à réaliser par l'ADL. Il n'était pas pertinent que celle-ci puisse se faire via l'interface QGIS de Plume, dont la grande majorité des utilisateurs ne disposera pas des droits nécessaires sur le serveur PostgreSQL. Par contre, [*AsgardManager*](https://snum.scenari-community.org/Asgard/Documentation/#SEC_AsgardManager) propose cette fonctionnalité, via son menu [`Gestion de la base`](https://snum.scenari-community.org/Asgard/Documentation/#SEC_MenuGestionBase).

## Localisation des objets de l'extension

Tous les objets de l'extension sont créés dans le schéma `z_plume`.

## Cohabitation avec *Asgard*

Il n'y a pas de lien fonctionnel direct entre *PlumePg* et l'extension [*Asgard*](https://snum.scenari-community.org/Asgard/Documentation/), outil créé dans le cadre du GT PostGIS pour faciliter la gestion des droits.

Si l'extension *PlumePg* est installée sur une base disposant déjà d'*Asgard*, `g_admin` sera automatiquement désigné comme *producteur* du schéma et `g_consult` en sera fait *lecteur*. Il s'agit juste de faciliter le travail de l'administrateur, cette opération ne crée aucune adhérence durable. Il est ensuite tout à fait possible, sans que cela ne pose de problème particulier, y compris lors des futures montées de version de *PlumePg* :
- de choisir d'autres rôles comme *producteur*, *éditeur* et *lecteur* de `z_plume` ;
- de déréférencer le schéma `z_plume` pour gérer ses droits hors d'*Asgard* ;
- de désinstaller *Asgard*.

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

La désinstallation entraîne la perte définitive de tous les [modèles de formulaire](/__doc__/08_modeles_de_formulaire.md).

*NB. Si le schéma `z_plume` existait avant l'installation de l'extension, il ne sera pas marqué comme dépendant de l'extension et ne sera donc pas supprimé en cas de désinstallation. Tout son contenu le sera, par contre.*

## Sauvegarde et restauration de la base

Pour que les données de *PlumePg* soient préservées lors de la restauration, notamment les [modèles de formulaire](/__doc__/08_modeles_de_formulaire.md), il est essentiel de **ne pas chercher à réinstaller manuellement l'extension sur la base de restauration**. Tout est automatique. On veillera seulement à ce que :
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
