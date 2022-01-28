# Installation et gestion de l'extension PostgreSQL *PlumePg*

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

Ces deux fichiers doivent être copiés dans le répertoire des extensions du serveur. Son chemin varie selon l'installation, mais il est vraisemblable qu'il soit de la forme `C:\Program Files\PostgreSQL\xx\share\extension` sous Windows et `/usr/share/postgresql/xx/extension` sous Linux, `xx` étant la version de PostgreSQL.

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

L'installation est à réaliser par l'ADL. Il ne paraît pas judicieux d'imaginer que celle-ci puisse se faire via l'interface QGIS de Plume, dont la grande majorité des utilisateurs ne disposera pas des droits nécessaires sur le serveur PostgreSQL. *AsgardManager* pourrait proposer cette fonctionnalité, par contre.

Tous les objets de l'extension sont créés dans le schéma `z_plume_pg`. Si celui-ci existait avant l'installation de l'extension, il ne sera pas marqué comme dépendant de l'extension et ne sera donc pas supprimé en cas de désinstallation.
