# Modèles de formulaire

Les modèles de formulaire sont définis par l'administrateur de données pour tous les utilisateurs de son service. Etant partagés, ils sont stockés sur le serveur PostgreSQL, dans un ensemble de tables créées par l'extension PostgreSQL appelée à ce stade *metadata*.

Leur usage est totalement optionnel.


## Gestion dans PostgreSQL

### Installation de l'extension

L'extension PostgreSQL *metadata* crée une structure de données adaptée au stockage des modèles.

Ses fichiers d'installation se trouvent dans le dossier [postgresql](/postgresql) :
- [metadata--0.0.1.sql](/postgresql/metadata--0.0.1.sql) ;
- [metadata.control](/postgresql/metadata.control).

```sql

CREATE EXTENSION metadata ;

```

Il est nécessaire d'installer préalablement l'extension *pgcrypto*, qui sert en l'occurrence à générer des UUID.

En une seule commande :

```sql

CREATE EXTENSION metadata CASCADE ;

```

L'installation est à réaliser par l'ADL. A priori, il ne paraît pas judicieux d'imaginer que celle-ci puisse se faire par l'intermédiaire du plugin QGIS, dont la grande majorité des utilisateurs ne disposera pas des droits nécessaires sur le serveur PostgreSQL...

Tous les objets de l'extension sont créés dans le schéma `z_metadata`. Si celui-ci existait avant l'installation de l'extension, il ne sera pas marqué comme dépendant de l'extension et ne sera donc pas supprimé en cas de désinstallation.


### Principe

Concrètement, un modèle de formulaire déclare un ensemble de catégories de métadonnées à présenter à l'utilisateur avec leurs modalités d'affichage. L'admistrateur de données peut prévoir autant de modèles qu'il le souhaite et, selon les besoins, il peut définir des conditions dans lesquelles un modèle sera appliqué par défaut à une fiche de métadonnées.


### Création d'un modèle de formulaire

La table `meta_template` comporte une ligne par modèle. Un modèle doit obligatoirement avoir un nom, renseigné dans le champ `tpl_label`. Ce nom devra être aussi parlant que possible pour les utilisateurs, qui n'auront accès qu'à cette information au moment de sélectionner un modèle.

Les champs suivants servent à définir les conditions d'usage du modèle :
- `sql_filter` est un filtre SQL, qui peut se référer au nom du schéma avec $1 et/ou de la table / vue avec $2. Il est évalué côté serveur au moment de l'import des modèles par le plugin, par la fonction `meta_execute_sql_filter(text, text, text)`.

Par exemple, le filtre suivant appliquera le modèle aux tables des schémas des blocs "données référentielles" (préfixe `'r_'`) et "données externes" (préfixe `'e_'`) de la nomenclature nationale :

```sql

'$1 ~ ANY(ARRAY[''^r_'', ''^e_'']'

```` 

D'une manière générale, toute commande renvoyant un booléen peut être utilisée. Ainsi, le filtre suivant appliquera le modèle pour toutes les fiches de métadonnées dès lors que l''utilisateur est membre du rôle `g_admin` :

```sql

'pg_has_role(''g_admin'', ''USAGE'')'

```

- `md_conditions` est un JSON définissant des ensembles de conditions portant cette fois sur les métadonnées.

```json

{
    "ensemble de conditions 1": {
        "snum:isExternal": True,
        "dcat:keyword": "IGN"
        },
    "ensemble de conditions 2": {
        "dct:publisher / foaf:name": "Institut national de l''information géographique et forestière (IGN-F)"
        }
}

```

Les noms donnés aux ensembles n'ont pas d''incidence. Dans un ensemble, les clés sont les chemins des catégories de métadonnées (champ `path` de la table `meta_categorie` évoquée ci-après) et les valeurs des valeurs qui doivent apparaître dans les métadonnées pour les catégories considérées.

Dans l'exemple ci-avant, une table validera les conditions du modèle si :
- il s'agit d'une donnée externe (valeur `True` pour la catégorie `snum:isExternal`) **ET** l'un de ses mots-clés (`dcat:keyword`) est IGN ;
- **OU** le nom du diffuseur (`dct:publisher / foaf:name`) est `Institut national de l'information géographique et forestière (IGN-F)`.

La comparaison des valeurs ne tient pas compte de la casse.

Il faudra soit que toutes les conditions de l'un des ensembles de conditions du JSON soient vérifiées, soit que le filtre SQL ait renvoyé True pour que le modèle soit considéré comme potentiellement applicable. Si un jeu de données remplit les conditions de plusieurs modèles, c'est celui dont le niveau de priorité, (champ `priority`) est le plus élevé qui sera retenu.

À noter que l'utilisateur du plugin pourra a posteriori choisir un autre modèle dans la liste, y compris un modèle sans conditions définies ou dont les conditions d'application automatiques ne sont pas vérifiées.


### Catégories de métadonnées

La table `meta_categorie` répertorie toutes les catégories de métadonnées, à la fois celle qui sont décrites par le schéma SHACL des catégories communes (fichier [shape.ttl](/metadata_postgresql_bibi_rdf/modeles/shape.ttl), correspond au paramètre `shape` des fonctions de RDF Utils) et les catégories supplémentaires locales définies par l'ADL pour le seul usage de son service. Il s'agit en fait d'une table partitionnée avec deux tables filles :
- `meta_shared_categorie` pour les catégories communes (`origin` vaut `shared`) ;
- `meta_local_categorie` pour les catégories supplémentaires locales (`origin` vaut `local`).

L'utilisateur peut évidemment écrire directement dans `meta_categorie` sans se préoccuper de là où sont effectivement stockées les données.

Concrètement, la table `meta_categorie` a deux fonctions :
- elle permet de créer les catégories supplémentaires locales, en ajoutant une ligne à la table par nouvelle catégorie. Il est a minima nécessaire de renseigner un libellé, histoire de savoir de quoi il est question ;
- elle permet de modifier la manière dont les catégories communes sont présentées par le plugin QGIS (nouveau label, widget différent, nouveau texte d'aide, etc.), en jouant sur les nombreux champs de paramétrage.

Les champs sur lesquels l'ADL peut intervenir sont :

| `cat_label` | Libellé de la catégorie. | 
| `widget_type` | Type de widget de saisie à utiliser. | 
| `row_span` | Nombre de lignes occupées par le widget de saisie, s''il y a lieu. La valeur ne sera considérée que pour un widget QTextEdit. | 
| `help_text` | Description de la catégorie. Sera affiché sous la forme d''un texte d''aide dans le formulaire). | 
| `default_value` | Valeur par défaut, le cas échéant. | 
| `placeholder_text` | Valeur fictive pré-affichée en tant qu''exemple dans le widget de saisie, s''il y a lieu. | 
| `input_mask` | Masque de saisie, s''il y a lieu. | 
| `multiple_values` | True si la catégorie admet plusieurs valeurs. | 
| `is_mandatory` | True si une valeur doit obligatoirement être saisie pour cette catégorie. | 
| `order_key` | Ordre d''apparence de la catégorie dans le formulaire. Les plus petits numéros sont affichés en premier. | 

Les champs `cat_id` (identifiant unique numérique), `path` (chemin SPARQL identifiant la catégorie) et `origin` sont calculés automatiquement.

Les caractéristiques spécifiées dans cette table seront utilisées pour tous les modèles, sauf -- cette possibilité sera détaillée par la suite -- à avoir prévu des valeurs spécifiques au modèle. Pour les catégories partagées, elles se substitueront au paramétrage par défaut défini par le schéma SHACL et repris pour information dans `meta_categorie` lors de l'initialisation de l'extension.

## Import par le plugin



## Génération du *template*

