# Modèles de formulaire

Les modèles de formulaire sont définis par l'administrateur de données pour tous les utilisateurs de son service. Etant partagés, ils sont stockés sur le serveur PostgreSQL, dans un ensemble de tables créées par l'extension PostgreSQL appelée à ce stade *metadata*.

Leur usage est totalement optionnel.

[Gestion dans PostgreSQL](#gestion-dans-postgresql) • [Import par le plugin](#import-par-le-plugin)


## Gestion dans PostgreSQL

### Principe

Par défaut, les formulaires du plugin QGIS présentent toutes les catégories de métadonnées définies par le schéma des métadonnées communes (en mode édition, car les champs non remplis sont masqués en mode lecture sauf paramétrage contraire).

Souvent, c'est trop : selon l'organisation du service, selon la table considérée, selon le profil de l'utilisateur, les catégories de métadonnées réellement pertinentes ne sont pas les mêmes, et il est peu probable que toutes le soient.

Parfois, c'est insuffisant : toujours selon l'organisation du service, la table considérée et le profil de l'utilisateur, il peut être très utile voire indispensable de disposer d'informations qui ne sont pas prévue dans les catégories communes.

L'extension PostgreSQL *metadata* y remédie en permettant à l'administrateur de définir des modèles de formulaire adaptés à son service.

Concrètement, un modèle de formulaire déclare un ensemble de catégories de métadonnées à présenter à l'utilisateur avec leurs modalités d'affichage. Il restreint ainsi les catégories communes par un système de liste blanche, tout en autorisant l'ajout de catégories locales supplémentaires.

L'admistrateur de données peut prévoir autant de modèles qu'il le souhaite et, selon les besoins, il peut définir des conditions dans lesquelles un modèle sera appliqué par défaut à une fiche de métadonnées (si cela se justifie).

### Installation de l'extension metadata

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


### Création d'un modèle de formulaire

La table `meta_template` comporte une ligne par modèle. Un modèle doit obligatoirement avoir un nom, renseigné dans le champ `tpl_label`, qui lui tiendra lieu d'identifiant. Ce nom devra être aussi parlant que possible pour les utilisateurs, qui n'auront accès qu'à cette information au moment de sélectionner un modèle. Sa longueur est limitée à 48 caractères.

Les champs `sql_filter` et `md_conditions` servent à définir des conditions selon lesquelles le modèle sera appliqué automatiquement à la fiche de métadonnées considérée. Les remplir est bien évidemment optionnel.

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
        "snum:isExternal": "True",
        "dcat:keyword": "IGN"
        },
    "ensemble de conditions 2": {
        "dct:publisher / foaf:name": "Institut national de l''information géographique et forestière (IGN-F)"
        }
}

```

Les noms donnés aux ensembles n'ont pas d''incidence. Dans un ensemble, les clés sont les chemins de catégories de métadonnées (champ `path` de la table `meta_categorie` évoquée ci-après) et les valeurs des valeurs qui doivent apparaître dans les métadonnées pour les catégories considérées.

Dans l'exemple ci-avant, une table validera les conditions du modèle si :
- il s'agit d'une donnée externe (valeur `True` pour la catégorie `snum:isExternal`) **ET** l'un de ses mots-clés (`dcat:keyword`) est IGN ;
- **OU** le nom du diffuseur (`dct:publisher / foaf:name`) est `Institut national de l'information géographique et forestière (IGN-F)`.

La comparaison des valeurs ne tient pas compte de la casse.

Il faudra soit que toutes les conditions de l'un des ensembles du JSON soient vérifiées, soit que le filtre SQL ait renvoyé True pour que le modèle soit considéré comme applicable. Si un jeu de données remplit les conditions de plusieurs modèles, c'est celui dont le niveau de priorité, (champ `priority`) est le plus élevé qui sera retenu.

À noter que les conditions ne valent qu'à l'ouverture de la fiche. L'utilisateur du plugin pourra a posteriori choisir librement un autre modèle dans la liste, y compris un modèle sans conditions définies ou dont les conditions d'application automatique ne sont pas vérifiées. Il aura aussi la possibilité de n'appliquer aucun modèle, auquel cas le schéma des métadonnées communes s'appliquera tel quel.


### Onglets des formulaires

Sans que ce soit obligatoire en aucune façon, les modèles de formulaires peuvent répartir les catégories de métadonnées par onglets.

Avant d'y affecter des catégories, les onglets doivent être définis dans la table `meta_tab`. Celle-ci contient deux champs :
- `tab_name` pour le nom de l'onglet. Il est limité à 48 caractères et doit obligatoirement être renseigné ;
- `tab_num` sert à ordonner les onglets. Les onglets sont affichés du plus petit numéro au plus grand (`NULL` à la fin), puis par ordre alphabétique en cas d''égalité. Les numéros n''ont pas à se suivre et peuvent être répétés. *NB. Tous les onglets de `meta_tab` ne seront évidemment pas présents dans tous les modèles, mais ceux qui le sont seront donc toujours présentés dans le même ordre quel que soit le modèle.*


### Catégories de métadonnées

La table `meta_categorie` répertorie toutes les catégories de métadonnées disponibles, à la fois celle qui sont décrites par le schéma SHACL des catégories communes (fichier [shape.ttl](/plume/bibli_rdf/modeles/shape.ttl)) et les catégories supplémentaires locales définies par l'ADL pour le seul usage de son service.

Il s'agit en fait d'une table partitionnée avec deux tables filles :
- `meta_shared_categorie` pour les catégories communes (`origin` vaut `shared`) ;
- `meta_local_categorie` pour les catégories supplémentaires locales (`origin` vaut `local`).

L'utilisateur peut évidemment écrire directement dans `meta_categorie` sans se préoccuper de là où sont effectivement stockées les données.

Concrètement, la table `meta_categorie` a deux fonctions :
- elle permet de créer les catégories supplémentaires locales, en ajoutant une ligne à la table par nouvelle catégorie. Il est a minima nécessaire de renseigner un libellé, histoire de savoir de quoi il est question ;
- elle permet de modifier la manière dont les catégories communes sont présentées par le plugin QGIS (nouveau label, widget différent, nouveau texte d'aide, etc.), en jouant sur les nombreux champs de paramétrage.

Les champs sur lesquels l'ADL peut intervenir sont :

| Nom du champ | Description | Remarques |
| --- | --- | --- |
| `cat_label` | Libellé de la catégorie. | |
| `data_type` | Type de valeur attendu pour la catégorie, parmi (type énuméré `meta_data_type`) : `'xsd:string'`, `'xsd:integer'`, `'xsd:decimal'`, `'xsd:float'`, `'xsd:double'`, `'xsd:boolean'`, `'xsd:date'`, `'xsd:time'`, `'xsd:dateTime'`, `'xsd:duration'`, `'rdf:langString'` (chaîne de caractères avec une langue associée[^langString]) et `'gsp:wktLiteral'` (géométrie au format textuel WKT). | Pour les catégories communes, les modifications apportées sur ce champ ne seront pas prises en compte. Si, pour une catégorie locale, aucune valeur n'est renseignée pour ce champ (ni dans `meta_categorie` ni dans `meta_template_categories`), le plugin considérera que la catégorie prend des valeurs de type `'string'`. |
| `widget_type` | Type de widget de saisie à utiliser. Cf. ci-après. | Pour une catégorie locale, si aucune valeur n'est renseignée pour ce champ (ni dans `meta_categorie` ni dans `meta_template_categories`), le plugin appliquera un widget `'QLineEdit'`. | 
| `row_span` | Nombre de lignes occupées par le widget de saisie, s'il y a lieu. | La valeur ne sera considérée que pour un widget de type `'QTextEdit'`. | 
| `help_text` | Description de la catégorie. Sera affiché sous la forme d'un texte d'aide dans le formulaire. | |
| `default_value` | Valeur par défaut pour la catégorie, le cas échéant. | Les valeurs par défaut ne sont appliquées que sur les fiches de métadonnées vierges. | 
| `placeholder_text` | Valeur fictive pré-affichée en tant qu'exemple dans le widget de saisie, s'il y a lieu. | La valeur ne sera considérée que pour un widget de type `'QTextEdit'` ou `'QLineEdit'`. | 
| `input_mask` | Masque de saisie, s'il y a lieu. | |
| `multiple_values` | `True` si la catégorie admet plusieurs valeurs. | Pour les catégories communes, les modifications apportées sur ce champ ne seront pas prises en compte. | 
| `is_mandatory` | `True` si une valeur doit obligatoirement être saisie pour cette catégorie. | Modifier cette valeur permet de rendre obligatoire une catégorie commune optionnelle, mais pas l''inverse. | 
| `order_key` | Ordre d'apparence de la catégorie dans le formulaire. Les plus petits numéros sont affichés en premier, il n'est pas nécessaire que les numéros se suivent. Dans le cas des catégories communes, qui ont une structure arborescente, il s'agit de l'ordre parmi les catégories de même niveau dans la branche. | |

[^langString]: Si une catégorie de métadonnée est de type `'rdf:langString'`, l'interface de Plume permettra, lorsque les modes édition et traduction sont simultanément activés, d'associer une langue à la métadonnée. Par défaut, les valeurs saisies hors mode traduction seront présumées être dans la [langue principale des métadonnées](/__doc__/16_actions_generales.md#langue-principale-des-métadonnées). Une catégorie de type `'xsd:string'` est une chaîne de caractères sans langue, ce qui est adapté pour toutes les catégories apparentées à des identifiants (nom d'application, nom d'organisation, nom d'objet PostgreSQL, adresse...), qui n'ont pas vocation à être traduites. Pour toutes les autres, `'rdf:langString'` est généralement préférables.

Les champs `path` (chemin SPARQL identifiant la catégorie), `origin` et `is_node` sont calculés automatiquement. Il est fortement recommandé de ne pas les modifier à la main.

Les valeurs autorisées pour `widget_type` sont définies par le type énuméré, `meta_widget_type`.

| Valeur | Description |
| --- | --- |
| `'QLineEdit'` | saisie de texte libre sur une seule ligne |
| `'QTextEdit'` | saisie multiligne de texte libre |
| `'QDateEdit'` | date avec aide à la saisie |
| `'QDateTimeEdit'` | date et heure avec aide à la saisie |
| `'QCheckBox'` | case à cocher |
| `'QComboBox'` | sélection d'un terme dans une liste |

À noter que `'QComboBox'` n'est pas disponible pour les catégories supplémentaires locales.

Les caractéristiques spécifiées dans la table `meta_categorie` seront utilisées pour tous les modèles, sauf -- cette possibilité sera détaillée par la suite -- à avoir prévu des valeurs spécifiques au modèle via la table `meta_template_categories`. Pour les catégories partagées, elles se substitueront au paramétrage par défaut défini par le schéma SHACL, qui est repris dans `meta_categorie` lors de l'initialisation de l'extension.


### Association de catégories à un modèle

La définition des catégories associées à chaque modèle (relation n-n) se fait par l'intermédiaire de la table de correspondance `meta_template_categories`.

Le modèle est identifié par son nom (champ `tpl_label`), la catégorie par son chemin (champ `path` de `meta_categorie`, repris dans `loccat_path` pour une catégorie locale et dans `shrcat_path` pour une catégorie commune).

Hormis ces champs de clés étrangères et la clé primaire séquentielle `tplcat_id`, tous les champs de la table `meta_template_categories` servent au paramétrage du modèle. Les valeurs qui y sont saisies remplaceront (pour le modèle considéré) celles qui avaient éventuellement été renseignées dans `meta_categorie` et le paramétrage du schéma SHACL des catégories communes.

Soit un modèle M, une catégorie de métadonnées C et une propriété P.
- Si une valeur est renseignée pour la propriété P, la catégorie C et le modèle M dans `meta_template_categories`, alors elle s'applique au modèle M pour la catégorie C et la propriété P.
- Sinon, si une valeur est renseignée pour la propriété P et la catégorie C dans `meta_categorie`, alors elle s'applique au modèle M pour la catégorie C et la propriété P.
- Sinon, pour une catégorie commune, la valeur éventuellement prévue par le schéma SHACL s'appliquera au modèle M pour la catégorie C et la propriété P. Pour les catégories locales, des valeurs par défaut sont prévues sur les propriétés essentielles - par exemple des widgets `'QLineEdit'` seront utilisés si le type n'est spécifié ni dans `meta_template_categories` ni dans `meta_categorie`.

Aux champs de paramétrage qui apparaissaient déjà dans `meta_categorie`, la table `meta_template_categories` ajoute deux champs optionnels :
- un champ booléen `read_only` qui pourra valoir `True` si la catégorie doit être en lecture seule pour le modèle considéré. Il peut notamment être mis à profit lorsque des fiches de métadonnées sont co-rédigées par un service métier référent et l'administrateur de données, pour permettre à chacun de voir les informations saisies par l'autre, sans qu'il risque de les modifier involontairement (sauf à ce qu'il change de modèle, bien sûr, ce n'est pas un dispositif de verrouillage, seulement de l'aide à la saisie) ;
- un champ `tab_name` qui permet de spécifier l'onglet (préalablement déclaré dans `meta_tab` dans lequel devra être placée la catégorie. Cette information n'est considérée que pour les catégories locales et les catégories communes de premier niveau (par exemple `'dcat:distribution / dct:issued'` ira nécessairement dans le même onglet que `'dcat:distribution'`). Pour celles-ci, si aucun onglet n'est fourni, la catégorie ira toujours dans le premier onglet cité pour le modèle ou, si le modèle n'utilise explicitement aucun onglet, dans un onglet "Général".

*NB. Pour les catégories de métadonnées communes imbriquées, il serait théoriquement attendu qu'un modèle fasse systématiquement apparaître tous les chemins intermédiaires (par exemple `'dcat:distribution'` et `'dcat:distribution / dct:license'` pour `'dcat:distribution / dct:license / rdfs:label'`) puisqu'ils devront figurer également dans le formulaire pour que la catégorie finale puisse être présentée à l'utilisateur. En pratique, toutefois, le plugin saura ajouter lui-même les chemins intermédiaires manquants, de même qu'il enlèvera les chemins intermédiaires sans catégorie finale. Ainsi, l'administrateur pourra se contenter d'associer `'dcat:distribution / dct:license / rdfs:label'` à son modèle, sauf à avoir envie de renommer les catégories `'dcat:distribution'` et/ou `'dcat:distribution / dct:license'`, de leur ajouter un texte d'aide, etc.* 


### Modèles pré-configurés

L'extension propose des modèles pré-configurés - deux à ce stade - qui peuvent être importés via la commande suivante :

```sql

SELECT * FROM z_metadata.meta_import_sample_template(%tpl_label) ;

```

*`%tpl_label` est à remplacer par une chaîne de caractères correspondant au nom du modèle à importer. Il est aussi possible de ne donner aucun argument à la fonction, dans ce cas tous les modèles pré-configurés sont importés.*

```sql

SELECT * FROM z_metadata.meta_import_sample_template() ;

```

La fonction renvoie une table dont la première colonne contient les noms des modèles traités et la seconde indique si le modèle a été créé (`'created'`) ou, dans le cas d'un modèle déjà répertorié, mis à jour / réinitialisé (`'updated'`).

Modèles pré-configurés disponibles :

| Nom du modèle (`tpl_label`) | Description |
| --- | --- |
| `'Basique'` | Modèle limité à quelques catégories de métadonnées essentielles. |
| `'Donnée externe'` | Modèle assez complet adapté à des données externes. |


## Import par le plugin

La gestion des modèles par le plugin fait intervenir :
- [pg_queries.py](/plume/bibli_pg/pg_queries.py) pour les requêtes SQL pré-écrites à exécuter sur les curseurs de Psycopg ;
- [template_utils.py](/plume/bibli_pg/template_utils.py) pour tout les outils permettant de traiter le résultat des requêtes.

Aucune des fonctions de ces deux fichiers n'envoie à proprement parler de requête au serveur PostgreSQL.

Concrètement, l'import du modèle de formulaire se fait en cinq temps :
1. vérification de la présence de l'extension *metadata*.
2. récupération sur le serveur PostgreSQL de la liste des modèles disponibles et de leurs conditions d'application → `templates`.
3. sélection du modèle à utiliser parmi la liste → `tpl_label`.
4. récupération sur le serveur PostgreSQL des catégories associées au modèle sélectionné avec leurs paramètres d'affichage → `categories`.
5. mise au propre du modèle sous la forme d'un dictionnaire → `template`.
6. récupération sur le serveur PostgreSQL de la liste des onglets du modèle → `tabs`.
7. mise au propre de la liste des onglets sous la forme d'un dictionnaire → `templateTabs`.

À l'ouverture de la fiche de métadonnées, le choix du modèle (étape 3) est automatique, mais les étapes 4 et 5 pourront être relancées par la suite, si l'utilisateur souhaite changer le modèle courant.

Soit :
- `connection_string` la chaîne de connexion à la base de données PostgreSQL ;
- `table_name` le nom de la table ou vue dont l'utilisateur cherche à consulter / éditer les métadonnées ;
- `schema_name` le nom de son schéma.


### Présence de l'extension *metadata*

Si l'extension n'est pas installée sur la base d'où provient la table considérée, on peut d'ores-et-déjà conclure qu'il n'y a pas de modèle de formulaire à appliquer (`template` et `templateTabs` valent `None`) et en rester là.

Pour le vérifier :

```python

import psycopg2
conn = psycopg2.connect(connection_string)

with conn:
    with conn.cursor() as cur:
    
        cur.execute(pg_queries.query_exists_extension(), ('metadata',))
        metadata_exists = cur.fetchone()[0]

conn.close()

```

Si `metadata_exists` vaut `True`, on poursuit avec les opérations suivantes.


### Récupération de la liste des modèles

Il s'agit tout bêtement d'aller chercher sur le serveur le contenu de la table `meta_template`, à la petite nuance près que `query_list_templates()` exécute ce faisant les filtres SQL du champ `sql_filter` (côté serveur, grâce à la fonction `z_metadata.meta_execute_sql_filter(text, text, text)` de l'extension *metadata*) et c'est le booléen résultant qui est importé plutôt que le filtre lui-même.

```python

import psycopg2
conn = psycopg2.connect(connection_string)

with conn:
    with conn.cursor() as cur:
    
        cur.execute(pg_queries.query_list_templates(), (schema_name, table_name))
        templates = cur.fetchall()

conn.close()

```

Puisque l'utilisateur devra avoir la possibilité de choisir ultérieurement un nouveau modèle (ou aucun modèle), la liste doit être gardée en mémoire. Les conditions ne servant plus à rien, on pourra se contenter des noms :

```python

templateLabels = [t[0] for t in templates]

```

### Sélection automatique du modèle

Cette étape détermine le modèle qui sera utilisé à l'ouverture initiale du formulaire. Elle mobilise la fonction `search_template()`, qui parcourt la liste des modèles (avec le résultat du filtre SQL / champ `sql_filter` de `meta_template`) en déterminant si les conditions d'usage portant sur les métadonnées (champ `md_conditions`) sont vérifiées, et renvoie le nom du modèle de plus haut niveau de priorité (champ `priority`) dont le filtre SQL ou les conditions sur les métadonnées sont satisfaites.

```python

tpl_label = template_utils.search_template(metagraph, templates)

```

*`metagraph` est le graphe contenant les métadonnées de la table ou vue considérée. Cf. [Génération du dictionnaire des widgets](/__doc__/05_generation_dictionnaire_widgets.md#metagraph--le-graphe-des-métadonnées-pré-existantes).*

Il est tout à possible que la fonction `search_template()` ne renvoie rien, d'autant que tous les services ne souhaiteront pas nécessairement utiliser ce mécanisme d'application automatique des modèles. Dans ce cas, on utilisera le "modèle préféré" (`preferedTemplate`) désigné dans les paramètres de configuration de l'utilisateur -- sous réserve qu'il soit défini et fasse bien partie de `templateLabels` -- ou, à défaut, aucun modèle (`template` et `templateTabs` valent `None`).

À noter que l'utilisateur peut décider que son modèle préféré prévaut sur toute sélection automatique, en mettant à `True` le paramètre utilisateur `enforcePreferedTemplate`. Dans ce cas, il n'est même pas utile de lancer `search_template()`, on a directement :

```python

if preferedTemplate and enforcePreferedTemplate \
    and templateLabels and preferedTemplate in templateLabels:
    tpl_label = preferedTemplate

```


### Récupération des catégories associées au modèle retenu

Une fois le nom du modèle à appliquer connu (s'il y en a un), on peut aller chercher dans la table `meta_template_categories` les catégories associées au modèle.

```python

import psycopg2
conn = psycopg2.connect(connection_string)

with conn:
    with conn.cursor() as cur:
    
        cur.execute(pg_queries.query_get_categories(), (tpl_label,))
        categories = cur.fetchall()

conn.close()

```

### Génération de *template*

À ce stade, `categories` est une liste de tuples, qui doit être transformée en dictionnaire et consolidée avant de pouvoir être utilisée par `build_dict()`.

C'est l'affaire de la fonction `build_template()` :

```python

template = template_utils.build_template(categories)

```

Le dictionnaire ainsi obtenu peut être passé dans l'argument `template` de la fonction `build_dict()`. Cf. [Génération du dictionnaire des widgets](/__doc__/05_generation_dictionnaire_widgets.md#template--le-modèle-de-formulaire).

Concrètement, `template` est un dictionnaire dont la structure est similaire à celle des `WidgetsDict`, si ce n'est que :
- ses clés sont des chemins SPARQL identifiant des catégories de métadonnées. Par exemple `dcat:contactPoint / vcard:hasEmail` pour l'adresse mél du point de contact ;
- ses dictionnaires internes comprennent nettement moins de clés.

Avec `build_template()`, toutes les clés possibles seront systématiquement présentes pour toutes les catégories, mais ce n'est pas obligatoire (la fonction `build_dict()` utilise systématiquement la méthode `get` pour interroger le formulaire).

Le fichier [exemple_dict_modele_local.json](/plume/bibli_rdf/exemples/exemple_dict_modele_local.json) donne un exemple de `template` valide sérialisé en JSON.


### Récupération des onglets associés au modèle retenu

La liste des onglets est obtenue en exécutant `query_template_tabs()` avec le nom du modèle en paramètre.

```python

import psycopg2
conn = psycopg2.connect(connection_string)

with conn:
    with conn.cursor() as cur:
    
        cur.execute(pg_queries.query_template_tabs(), (tpl_label,))
        tabs = cur.fetchall()

conn.close()

```

### Génération de *templateTabs*

La fonction `build_template_tabs()` permet de transformer la liste brute `tabs` renvoyée par `query_template_tabs()` en un dictionnaire qui pourra être fourni en argument à la fonction `build_dict()`. Cf. [Génération du dictionnaire des widgets](/__doc__/05_generation_dictionnaire_widgets.md#templatetabs--la-liste-des-onglets).

```python

templateTabs = template_utils.build_template_tabs(tabs)

```

`templateTabs` peut être égal à `None` si le modèle n'utilise pas d'onglets. Dans ce cas, `build_dict()` affectera toutes les catégories à un unique onglet nommé "Général".