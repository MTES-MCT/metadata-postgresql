# Modèles de formulaire

Les modèles de formulaire sont définis par l'administrateur de données pour tous les utilisateurs de son service. Etant partagés, ils sont stockés sur le serveur PostgreSQL, dans un ensemble de tables créées par l'extension PostgreSQL *PlumePg*.

Leur usage est totalement optionnel.

[Principe](#principe) • [Gestion dans PostgreSQL](#gestion-dans-postgresql) • [Import des modèles par Plume](#import-des-modèles-par-plume)


## Principe

Par défaut, les formulaires de Plume présentent toutes les catégories de métadonnées définies par le schéma des métadonnées communes, [`shape.ttl`](/plume/rdf/data/shape.ttl)[^metadonnees-masquées]. Souvent, c'est trop. Selon l'organisation du service, selon la table considérée, selon le profil de l'utilisateur, les catégories de métadonnées réellement pertinentes ne seront pas les mêmes, et il est peu probable que toutes les catégories communes le soient.

[^metadonnees-masquées]: Du moins en mode édition, car les champs non remplis sont masqués en mode lecture sauf paramétrage contraire.

Parfois, c'est au contraire insuffisant. Toujours selon l'organisation du service, la table considérée et le profil de l'utilisateur, il peut être très utile voire indispensable de disposer d'informations qui ne sont pas prévues dans les catégories communes.

Plume y remédie, via l'extension PostgreSQL *PlumePg*, en permettant à l'administrateur de définir des modèles de formulaire adaptés à son service, que le plugin QGIS saura exploiter.

Concrètement, un modèle de formulaire déclare un ensemble de catégories de métadonnées à présenter à l'utilisateur avec leurs modalités d'affichage. Il restreint ainsi les catégories communes par un système de liste blanche, tout en autorisant l'ajout de catégories locales supplémentaires.

L'admistrateur de données peut prévoir autant de modèles qu'il le souhaite et, selon les besoins, il peut définir des conditions dans lesquelles un modèle sera appliqué par défaut à une fiche de métadonnées (si cela se justifie). Dans l'interface QGIS de Plume, l'utilisateur peut basculer à sa convenance d'un modèle à l'autre.


## Gestion dans PostgreSQL

L'extension PostgreSQL *PlumePg* crée une structure de données adaptée au stockage des modèles. Pour bénéficier des modèles, elle doit être installée sur toutes les bases du serveur PostgreSQL dont on souhaite gérer les métadonnées avec Plume[^base-par-base].

[^base-par-base]: Plus précisément, si *PlumePg* n'est pas installée sur une base donnée, aucun modèle ne sera proposé dans l'interface de Plume pour les métadonnées des objets de cette base.

Cf. [Installation et gestion de l'extension PostgreSQL *PlumePg*](/docs/source/usage/gestion_plume_pg.md) pour plus de détails sur l'installation et la maintenance de cette extension.

*PlumePg* crée dans le schéma `z_plume` un ensemble de tables permettant de définir les modèles de formulaires :
- `meta_template` liste les modèles.
- `meta_categorie` liste les catégories de métadonnées disponibles, qu'il s'agisse des catégories du schéma commun ou de catégories locales, et paramètre leur affichage dans les formulaires.
- `meta_tab` liste des noms d'onglets de formulaires dans lesquels pourront être classées les catégories.
- `meta_template_categories` permet de déclarer les catégories utilisées par chaque modèle, de les ranger dans des onglets, et de définir si besoin des paramètres d'affichage spécifique à un modèle pour certaines catégories, qui remplaceront ceux de `meta_categorie`.

### Création d'un modèle de formulaire

La table `z_plume.meta_template` comporte une ligne par modèle. Un modèle doit obligatoirement avoir un nom, renseigné dans le champ `tpl_label`, qui lui tiendra lieu d'identifiant. Ce nom devra être aussi parlant que possible pour les utilisateurs, qui n'auront accès qu'à cette information au moment de sélectionner un modèle. Sa longueur est limitée à 48 caractères.

Les champs `sql_filter` et `md_conditions` servent à définir des conditions selon lesquelles le modèle sera appliqué automatiquement à la fiche de métadonnées considérée. Les remplir est bien évidemment optionnel.

- `sql_filter` est un filtre SQL, qui peut se référer au nom du schéma avec `$1` et/ou de la table / vue avec `$2`. Il est évalué côté serveur au moment de l'import des modèles par le plugin, par la fonction `z_plume.meta_execute_sql_filter(text, text, text)`.

Par exemple, le filtre suivant appliquera le modèle aux tables des schémas des blocs "données référentielles" (préfixe `'r_'`) et "données externes" (préfixe `'e_'`) de la nomenclature nationale :

```sql

'$1 ~ ANY(ARRAY[''^r_'', ''^e_'']'

```` 

D'une manière générale, toute commande renvoyant un booléen peut être utilisée. Ainsi, le filtre suivant appliquera le modèle pour toutes les fiches de métadonnées dès lors que l''utilisateur est membre du rôle `g_admin` :

```sql

'pg_has_role(''g_admin'', ''USAGE'')'

```

- `md_conditions` est une liste JSON définissant des ensembles de conditions portant cette fois sur les métadonnées.

```json

[
    {
        "snum:isExternal": true,
        "dcat:keyword": "IGN"
    },
    {
        "dct:publisher / foaf:name": "Institut national de l''information géographique et forestière (IGN-F)"
    }
]

```

Les ensembles sont combinés entre eux avec l'opérateur `OR`. Au sein d'un ensemble, les conditions sont combinées avec l'opérateur `AND`.

Les clés des conditions sont les chemins des catégories de métadonnées (champ `path` de la table `meta_categorie` évoquée ci-après) et les valeurs des valeurs qui doivent apparaître dans les métadonnées pour les catégories considérées.

Dans l'exemple ci-avant, une table validera les conditions du modèle si :
- il s'agit d'une donnée externe (valeur `True` pour la catégorie `snum:isExternal`) **ET** l'un de ses mots-clés (`dcat:keyword`) est `'IGN'` ;
- **OU** le nom du diffuseur (`dct:publisher / foaf:name`) est `'Institut national de l'information géographique et forestière (IGN-F)'`.

La comparaison des valeurs ne tient pas compte de la casse.

Il faudra soit que toutes les conditions de l'un des ensembles du JSON soient vérifiées, soit que le filtre SQL ait renvoyé True pour que le modèle soit considéré comme applicable. Si un jeu de données remplit les conditions de plusieurs modèles, c'est celui dont le niveau de priorité, (champ `priority`) est le plus élevé qui sera retenu.

À noter que les conditions ne valent qu'à l'ouverture de la fiche. L'utilisateur du plugin pourra a posteriori choisir librement un autre modèle dans la liste, y compris un modèle sans conditions définies ou dont les conditions d'application automatique ne sont pas vérifiées. Il aura aussi la possibilité de n'appliquer aucun modèle, auquel cas le schéma des métadonnées communes s'appliquera tel quel.


### Onglets des formulaires

Sans que ce soit obligatoire en aucune façon, les modèles de formulaires peuvent répartir les catégories de métadonnées par onglets.

Avant d'y affecter des catégories, les onglets doivent être définis dans la table `z_plume.meta_tab`. Celle-ci contient deux champs :
- `tab` pour le nom de l'onglet. Il est limité à 48 caractères et doit obligatoirement être renseigné ;
- `tab_num` sert à ordonner les onglets. Les onglets sont affichés du plus petit numéro au plus grand (`NULL` à la fin), puis par ordre alphabétique en cas d''égalité. Les numéros n''ont pas à se suivre et peuvent être répétés. *NB. Tous les onglets de `meta_tab` ne seront évidemment pas présents dans tous les modèles, mais ceux qui le sont seront donc toujours présentés dans le même ordre quel que soit le modèle.*


### Catégories de métadonnées

La table `z_plume.meta_categorie` répertorie toutes les catégories de métadonnées disponibles, à la fois celle qui sont décrites par le schéma SHACL des catégories communes (fichier [shape.ttl](/plume/rdf/data/shape.ttl)) et les catégories supplémentaires locales définies par l'ADL pour le seul usage de son service.

Il s'agit en fait d'une table partitionnée avec deux tables filles :
- `z_plume.meta_shared_categorie` pour les catégories communes (`origin` vaut `shared`) ;
- `z_plume.meta_local_categorie` pour les catégories supplémentaires locales (`origin` vaut `local`).

L'utilisateur peut évidemment écrire directement dans `meta_categorie` sans se préoccuper de là où sont effectivement stockées les données.

Concrètement, la table `meta_categorie` a deux fonctions :
- elle permet de créer les catégories supplémentaires locales, en ajoutant une ligne à la table par nouvelle catégorie. Il est a minima nécessaire de renseigner un libellé, histoire de savoir de quoi il est question ;
- elle permet de modifier la manière dont les catégories communes sont présentées par le plugin QGIS (nouveau label, nouveau texte d'aide, etc.), en jouant sur les nombreux champs de paramétrage.

Les champs sur lesquels l'ADL peut intervenir sont :

| Nom du champ | Description | Remarques |
| --- | --- | --- |
| `label` | Libellé de la catégorie. | |
| `description`| Description de la catégorie. Elle sera affichée sous la forme d'un texte d'aide dans le formulaire. | |
| `datatype` | Type de valeur attendu pour la catégorie, parmi (type énuméré `z_plume.meta_data_type`) : `'xsd:string'`, `'xsd:integer'`, `'xsd:decimal'`, `'xsd:boolean'`, `'xsd:date'`, `'xsd:time'`, `'xsd:dateTime'`, `'xsd:duration'`, `'rdf:langString'` (chaîne de caractères avec une langue associée[^langString]) et `'gsp:wktLiteral'` (géométrie au format textuel WKT). Cette information détermine notamment la nature des widgets utilisés par Plume pour afficher et éditer les valeurs, ainsi que les validateurs appliqués. | Pour les catégories communes, les modifications apportées sur ce champ ne seront pas prises en compte. Si, pour une catégorie locale, aucune valeur n'est renseignée pour ce champ (ni dans `meta_categorie` ni dans `meta_template_categories`), le plugin considérera que la catégorie prend des valeurs de type `'xsd:string'`. |
| `is_long_text` | `True` pour une catégorie appelant un texte de plusieurs lignes. | Cette information ne sera prise en compte que si le type de valeur (`datatype`) est `'xsd:string'`, `'rdf:langString'` ou `'gsp:wktLiteral'`. |
| `rowspan` | Nombre de lignes occupées par le widget de saisie, s'il y a lieu de modifier le comportement par défaut de Plume. | La valeur ne sera considérée que si `is_long_text` vaut `True`. | 
| `special` | Le cas échéant, mise en forme spécifique à appliquer au champ. Valeurs autorisées (type énuméré `z_plume.meta_datatype`) : `'url'`, `'email'`, et `'phone'`. |  Pour les catégories communes, les modifications apportées à ce champ ne seront pas prises en compte. |
| `placeholder` | Valeur fictive pré-affichée en tant qu'exemple dans le widget de saisie, s'il y a lieu. | | 
| `input_mask` | Masque de saisie, s'il y a lieu. La syntaxe est décrite dans la [documentation de l'API Qt for python](https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QLineEdit.html#PySide2.QtWidgets.PySide2.QtWidgets.QLineEdit.inputMask). | La valeur sera ignorée si le widget utilisé pour la catégorie ne prend pas en charge ce mécanisme. |
| `is_multiple` | `True` si la catégorie admet plusieurs valeurs. | Pour les catégories communes, les modifications apportées sur ce champ ne seront pas prises en compte. |
| `unilang` | `True` si la catégorie n'admet plusieurs valeurs que si elles sont dans des langues différentes (par exemple un jeu de données n'a en principe qu'un seul titre, mais il peut être traduit). | Pour les catégories communes, les modifications apportées sur ce champ ne seront pas prises en compte. `is_multiple` est ignoré quand `unilang` vaut `True`. Cette information n'est considérée que si `datatype` vaut `'rdf:langString'`. | 
| `is_mandatory` | `True` si une valeur doit obligatoirement être saisie pour cette catégorie. | Modifier cette valeur permet de rendre obligatoire une catégorie commune optionnelle, mais pas l''inverse. |
| `sources` | Pour une catégorie prenant ses valeurs dans un ou plusieurs thésaurus, liste des sources admises. | Cette information n'est considérée que pour les catégories communes. Il n'est pas possible d'ajouter des sources ni de les retirer toutes - Plume reviendrait alors à la liste initiale -, mais ce champ permet de restreindre la liste à un ou plusieurs thésaurus jugés les mieux adaptés. |
| `order_key` | Ordre d'apparence de la catégorie dans le formulaire. Les plus petits numéros sont affichés en premier, il n'est pas nécessaire que les numéros se suivent. Dans le cas des catégories communes, qui ont une structure arborescente, il s'agit de l'ordre parmi les catégories de même niveau dans la branche. | |

[^langString]: Si une catégorie de métadonnée est de type `'rdf:langString'`, l'interface de Plume permettra, lorsque les modes édition et traduction sont simultanément activés, d'associer une langue à la métadonnée. Par défaut, les valeurs saisies hors mode traduction seront présumées être dans la [langue principale des métadonnées](/docs/source/usage/actions_generales.md#langue-principale-des-métadonnées). Une catégorie de type `'xsd:string'` est une chaîne de caractères sans langue, ce qui est adapté pour toutes les catégories apparentées à des identifiants (nom d'application, nom d'objet PostgreSQL...), qui n'ont pas vocation à être traduites. Pour toutes les autres, `'rdf:langString'` est généralement préférables.

Les champs `path` (chemin SPARQL identifiant la catégorie), `origin` et `is_node` sont calculés automatiquement. Il est fortement recommandé de ne pas les modifier à la main.

Les caractéristiques spécifiées dans la table `meta_categorie` seront utilisées pour tous les modèles, sauf -- cette possibilité sera détaillée par la suite -- à avoir prévu des valeurs spécifiques au modèle via la table `meta_template_categories`. Pour les catégories partagées, elles se substitueront au paramétrage par défaut défini par le schéma des catégories communes, qui est repris dans `meta_categorie` lors de l'initialisation de l'extension.


### Association de catégories à un modèle

La définition des catégories associées à chaque modèle (relation n-n) se fait par l'intermédiaire de la table de correspondance `meta_template_categories`.

Le modèle est identifié par son nom (champ `tpl_label`), la catégorie par son chemin (champ `path` de `meta_categorie`, repris dans `loccat_path` pour une catégorie locale et dans `shrcat_path` pour une catégorie commune).

Hormis ces champs de clés étrangères et la clé primaire séquentielle `tplcat_id`, tous les champs de la table `meta_template_categories` servent au paramétrage du modèle. Les valeurs qui y sont saisies remplaceront (pour le modèle considéré) celles qui avaient éventuellement été renseignées dans `meta_categorie` et le paramétrage du schéma des catégories communes.

Soit un modèle M, une catégorie de métadonnées C et une propriété P.
- Si une valeur est renseignée pour la propriété P, la catégorie C et le modèle M dans `meta_template_categories`, alors elle s'applique au modèle M pour la catégorie C et la propriété P.
- Sinon, si une valeur est renseignée pour la propriété P et la catégorie C dans `meta_categorie`, alors elle s'applique au modèle M pour la catégorie C et la propriété P.
- Sinon, pour une catégorie commune, la valeur éventuellement prévue par le schéma des catégories communes s'appliquera au modèle M pour la catégorie C et la propriété P. Pour les catégories locales, il sera considéré par défaut que la catégorie doit être affichée sous la forme d'une zone de texte sur une seule ligne et qu'elle n'admet qu'une seule valeur.

Aux champs de paramétrage qui apparaissaient déjà dans `meta_categorie`, la table `meta_template_categories` ajoute deux champs optionnels :
- un champ booléen `read_only` qui pourra valoir `True` si la catégorie doit être en lecture seule pour le modèle considéré. Il peut notamment être mis à profit lorsque des fiches de métadonnées sont co-rédigées par un service métier référent et l'administrateur de données, pour permettre à chacun de voir les informations saisies par l'autre, sans qu'il risque de les modifier involontairement (sauf à ce qu'il change de modèle, bien sûr, ce n'est pas un dispositif de verrouillage, seulement de l'aide à la saisie) ;
- un champ `tab` qui permet de spécifier l'onglet (préalablement déclaré dans `meta_tab`) dans lequel devra être placée la catégorie. Cette information n'est considérée que pour les catégories locales et les catégories communes de premier niveau (par exemple la catégorie de deuxième niveau `'dcat:distribution / dct:issued'` ira nécessairement dans le même onglet que `'dcat:distribution'`). Pour celles-ci, si aucun onglet n'est fourni, la catégorie ira toujours dans le premier onglet cité pour le modèle ou, si le modèle n'utilise explicitement aucun onglet, dans un onglet _"Général"_.

*NB. Pour les catégories de métadonnées communes imbriquées, il n'est pas nécessaire que le modèle fasse systématiquement apparaître tous les chemins intermédiaires (par exemple `'dcat:distribution'` et `'dcat:distribution / dct:license'` pour `'dcat:distribution / dct:license / rdfs:label'`). Le plugin saura ajouter lui-même les chemins intermédiaires manquants, de même qu'il enlèvera les chemins intermédiaires sans catégorie finale. Ainsi, l'administrateur pourra se contenter d'associer `'dcat:distribution / dct:license / rdfs:label'` à son modèle, sauf à avoir envie de renommer les catégories `'dcat:distribution'` et/ou `'dcat:distribution / dct:license'`, de leur ajouter un texte d'aide, etc.* 


### Modèles pré-configurés

L'extension propose des modèles pré-configurés - trois à ce stade - qui peuvent être importés via la commande suivante :

```sql

SELECT * FROM z_plume.meta_import_sample_template(%tpl_label) ;

```

*`%tpl_label` est à remplacer par une chaîne de caractères correspondant au nom du modèle à importer. Il est aussi possible de ne donner aucun argument à la fonction, dans ce cas tous les modèles pré-configurés sont importés.*

```sql

SELECT * FROM z_plume.meta_import_sample_template() ;

```

La fonction renvoie une table dont la première colonne contient les noms des modèles traités et la seconde indique si le modèle a été créé (`'created'`) ou, dans le cas d'un modèle déjà répertorié, mis à jour / réinitialisé (`'updated'`).

Modèles pré-configurés disponibles :

| Nom du modèle (`tpl_label`) | Description |
| --- | --- |
| `'Basique'` | Modèle limité à quelques catégories de métadonnées essentielles. |
| `'Donnée externe'` | Modèle assez complet adapté à des données externes. |
| `'Classique'` | Modèle comportant les principales catégories de métadonnées intéressantes pour des données produites par le service. |


## Import des modèles par Plume

La gestion des modèles par le plugin fait intervenir :
- le module [`plume.pg.queries`](/plume/pg/queries.py) pour les requêtes SQL pré-écrites à exécuter sur les curseurs de Psycopg ;
- le module [`plume.pg.template`](/plume/pg/template.py) pour le traitement du résultat de ces requêtes.

Aucune des fonctions de ces deux modules n'envoie à proprement parler de requête au serveur PostgreSQL.

Concrètement, l'import du modèle de formulaire se fait en six temps :
1. vérification de la présence de l'extension *PlumePg*.
2. récupération sur le serveur PostgreSQL de la liste des modèles disponibles et de leurs conditions d'application → `templates`.
3. sélection du modèle à utiliser parmi la liste → `tpl_label`.
4. récupération sur le serveur PostgreSQL des catégories associées au modèle sélectionné avec leurs paramètres d'affichage → `categories`.
5. récupération sur le serveur PostgreSQL de la liste des onglets du modèle → `tabs`.
6. mise au propre du modèle sous la forme d'un dictionnaire → `template`.

À l'ouverture de la fiche de métadonnées, le choix du modèle (étape 3) est automatique. Les étapes 4 à 6 devront être relancées à chaque fois que l'utilisateur change manuellement le modèle courant.

Soit :
- `connection_string` la chaîne de connexion à la base de données PostgreSQL ;
- `table_name` le nom de la table ou vue dont l'utilisateur cherche à consulter / éditer les métadonnées ;
- `schema_name` le nom de son schéma.


### Présence de l'extension *PlumePg*

Si l'extension n'est pas installée sur la base d'où provient la table considérée, on peut d'ores-et-déjà conclure qu'il n'y a pas de modèle de formulaire à appliquer (`template` vaut `None`) et en rester là.

Pour le vérifier :

```python

import psycopg2
from plume.pg import queries

conn = psycopg2.connect(connection_string)

with conn:
    with conn.cursor() as cur:
    
        cur.execute(queries.query_exists_extension(), ('plume_pg',))
        plume_pg_exists = cur.fetchone()[0]

conn.close()

```

Si `plume_pg_exists` vaut `True`, on poursuit avec les opérations suivantes.


### Récupération de la liste des modèles

Il s'agit simplement d'aller chercher sur le serveur le contenu de la table `meta_template`, à la petite nuance près que `query_list_templates()` exécute ce faisant les filtres SQL du champ `sql_filter` (côté serveur, grâce à la fonction `z_plume.meta_execute_sql_filter(text, text, text)` de l'extension *PlumePg*) et c'est le booléen résultant qui est importé plutôt que le filtre lui-même.

```python

import psycopg2
from plume.pg import queries

conn = psycopg2.connect(connection_string)

with conn:
    with conn.cursor() as cur:
    
        cur.execute(queries.query_list_templates(), (schema_name, table_name))
        templates = cur.fetchall()

conn.close()

```

Puisque l'utilisateur devra avoir la possibilité de choisir ultérieurement un nouveau modèle (ou aucun modèle), la liste doit être gardée en mémoire. Les conditions ne servant plus à rien, on pourra se contenter des noms :

```python

templateLabels = [t[0] for t in templates]

```

### Sélection automatique du modèle

Cette étape détermine le modèle qui sera utilisé à l'ouverture initiale du formulaire. Elle mobilise la fonction `plume.pg.template.search_template`, qui parcourt la liste des modèles (avec le résultat du filtre SQL / champ `sql_filter` de la table `meta_template`) en déterminant si les conditions d'usage portant sur les métadonnées (champ `md_conditions`) sont vérifiées. Elle renvoie le nom du modèle de plus haut niveau de priorité (champ `priority`) dont le filtre SQL ou les conditions sur les métadonnées sont satisfaites.

```python

from plume.pg.template import search_template

tpl_label = search_template(templates, metagraph)

```

*`metagraph` est le graphe contenant les métadonnées de la table ou vue considérée. Cf. [Génération du dictionnaire des widgets](/docs/source/usage/generation_dictionnaire_widgets.md#metagraph--le-graphe-des-métadonnées-pré-existantes).*

Il est tout à possible que la fonction `search_template` ne renvoie rien, d'autant que tous les services ne souhaiteront pas nécessairement utiliser ce mécanisme d'application automatique des modèles. Dans ce cas, on utilisera le "modèle préféré" (`preferedTemplate`) désigné dans les [paramètres de configuration de l'utilisateur](/docs/source/usage/parametres_utilisateur.md) -- sous réserve qu'il soit défini et fasse bien partie de `templateLabels` -- ou, à défaut, aucun modèle (`template` vaut `None`).

À noter que l'utilisateur peut décider que son modèle préféré prévaut sur toute sélection automatique, en mettant à `True` le paramètre utilisateur `enforcePreferedTemplate`. Dans ce cas, il n'est même pas utile de lancer `search_template`, on a directement :

```python

if preferedTemplate and enforcePreferedTemplate \
    and templateLabels and preferedTemplate in templateLabels:
    tpl_label = preferedTemplate

```


### Récupération des catégories associées au modèle retenu

Une fois le nom du modèle à appliquer connu (s'il y en a un), on peut aller chercher dans la table `meta_template_categories` les catégories associées au modèle.

```python

import psycopg2
from plume.pg import queries

conn = psycopg2.connect(connection_string)

with conn:
    with conn.cursor() as cur:
    
        cur.execute(queries.query_get_categories(), (tpl_label,))
        categories = cur.fetchall()

conn.close()

```

### Récupération des onglets associés au modèle retenu

La liste des onglets est obtenue en exécutant la requête renvoyée par `plume.pg.queries.query_template_tabs`, avec le nom du modèle en paramètre.

```python

import psycopg2
from plume.pg import queries

conn = psycopg2.connect(connection_string)

with conn:
    with conn.cursor() as cur:
    
        cur.execute(queries.query_template_tabs(), (tpl_label,))
        tabs = cur.fetchall()

conn.close()

```

Si `tabs` est une liste vide, toutes les catégories seront affectées à un unique onglet nommé _"Général"_.

### Génération de *template*

À ce stade, `categories` est une liste de tuples, qui doit être consolidée avant de pouvoir être utilisée pour générer le [dictionnaire de widgets](/docs/source/usage/generation_dictionnaire_widgets.md).

Concrètement, il s'agit de créer un objet `plume.pg.template.TemplateDict` à partir de `categories` et `tabs` :

```python

template = TemplateDict(categories, tabs)

```

Le modèle de formulaire ainsi obtenu peut être passé dans l'argument `template` du constructeur de `plume.rdf.widgetsdict.WigdetsDict`. Cf. [Génération du dictionnaire des widgets](/docs/source/usage/generation_dictionnaire_widgets.md#template--le-modèle-de-formulaire).
