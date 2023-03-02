# Modèles de formulaire

Les modèles de formulaire sont définis par l'administrateur de données pour tous les utilisateurs de son service. Etant partagés, ils sont stockés sur le serveur PostgreSQL, dans un ensemble de tables créées par l'extension PostgreSQL *PlumePg*.

Leur usage est totalement optionnel.

[Principe](#principe) • [Gestion dans PostgreSQL](#gestion-dans-postgresql) • [Import des modèles par Plume](#import-des-modèles-par-plume) • [Avec les modèles stockés en local](#avec-les-modèles-stockés-en-local) • [Gestion des modèles via Plume](#gestion-des-modèles-via-plume)


## Principe

Par défaut, les formulaires de Plume présentent toutes les catégories de métadonnées définies par le schéma des métadonnées communes, [`shape.ttl`](../../plume/rdf/data/shape.ttl)[^metadonnees-masquées]. Souvent, c'est trop. Selon l'organisation du service, selon la table considérée, selon le profil de l'utilisateur, les catégories de métadonnées réellement pertinentes ne seront pas les mêmes, et il est peu probable que toutes les catégories communes le soient.

[^metadonnees-masquées]: Du moins en mode édition, car les champs non remplis sont masqués en mode lecture sauf paramétrage contraire.

Parfois, c'est au contraire insuffisant. Toujours selon l'organisation du service, la table considérée et le profil de l'utilisateur, il peut être très utile voire indispensable de disposer d'informations qui ne sont pas prévues dans les catégories communes.

Plume y remédie, via l'extension PostgreSQL *PlumePg*, en permettant à l'administrateur de définir des modèles de formulaire adaptés à son service, que le plugin QGIS saura exploiter.

Concrètement, un modèle de formulaire déclare un ensemble de catégories de métadonnées à présenter à l'utilisateur avec leurs modalités d'affichage. Il restreint ainsi les catégories communes par un système de liste blanche, tout en autorisant l'ajout de catégories locales supplémentaires.

L'admistrateur de données peut prévoir autant de modèles qu'il le souhaite et, selon les besoins, il peut définir des conditions dans lesquelles un modèle sera appliqué par défaut à une fiche de métadonnées (si cela se justifie). Dans l'interface QGIS de Plume, l'utilisateur peut basculer à sa convenance d'un modèle à l'autre.


## Gestion dans PostgreSQL

L'extension PostgreSQL *PlumePg* crée une structure de données adaptée au stockage des modèles. Pour bénéficier des modèles, elle doit être installée sur toutes les bases du serveur PostgreSQL dont on souhaite gérer les métadonnées avec Plume[^base-par-base].

[^base-par-base]: Plus précisément, si *PlumePg* n'est pas installée sur une base donnée, aucun modèle ne sera proposé dans l'interface de Plume pour les métadonnées des objets de cette base.

Cf. [Installation et gestion de l'extension PostgreSQL *PlumePg*](./gestion_plume_pg.md) pour plus de détails sur l'installation et la maintenance de cette extension.

*PlumePg* crée dans le schéma `z_plume` un ensemble de tables permettant de définir les modèles de formulaires :
- `meta_template` liste les modèles.
- `meta_categorie` liste les catégories de métadonnées disponibles, qu'il s'agisse des catégories du schéma commun ou de catégories locales, et paramètre leur affichage dans les formulaires.
- `meta_tab` liste des noms d'onglets de formulaires dans lesquels pourront être classées les catégories.
- `meta_template_categories` permet de déclarer les catégories utilisées par chaque modèle, de les ranger dans des onglets, et de définir si besoin des paramètres d'affichage spécifiques à un modèle pour certaines catégories, qui remplaceront ceux de `meta_categorie`.

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
        "plume:isExternal": true,
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
- il s'agit d'une donnée externe (valeur `True` pour la catégorie `plume:isExternal`) **ET** l'un de ses mots-clés (`dcat:keyword`) est `'IGN'` ;
- **OU** le nom du diffuseur (`dct:publisher / foaf:name`) est `'Institut national de l'information géographique et forestière (IGN-F)'`.

La comparaison des valeurs ne tient pas compte de la casse.

Il faudra soit que toutes les conditions de l'un des ensembles du JSON soient vérifiées, soit que le filtre SQL ait renvoyé True pour que le modèle soit considéré comme applicable. Si un jeu de données remplit les conditions de plusieurs modèles, c'est celui dont le niveau de priorité, (champ `priority`) est le plus élevé qui sera retenu.

À noter que les conditions ne valent qu'à l'ouverture de la fiche. L'utilisateur du plugin pourra a posteriori choisir librement un autre modèle dans la liste, y compris un modèle sans conditions définies ou dont les conditions d'application automatique ne sont pas vérifiées. Il aura aussi la possibilité de n'appliquer aucun modèle, auquel cas le schéma des métadonnées communes s'appliquera tel quel.

Le champ `enabled` de `meta_template` permet de désactiver un modèle, qui ne sera alors plus proposé aux utilisateurs du plugin QGIS, en passant simplement la valeur du champ de `True` (valeur par défaut) à `False`. Ce mécanisme peut notamment être utilisé pour les modèles en cours de construction, dont l'administrateur pourra souhaiter qu'ils n'apparaissent pas dans la liste des modèles disponibles tant qu'ils ne sont pas prêts à l'usage.

On pourra ainsi initier la création d'un nouveau modèle avec une requête de ce type :

```sql

INSERT INTO z_plume.meta_template (tpl_label, enabled)
	VALUES ('Mon nouveau modèle', False) ;

```

Puis, une fois finalisée l'association des catégories au modèle (cf. ci-après), on activera le modèle : 

```sql

UPDATE z_plume.meta_template
    SET enabled = True
	WHERE tpl_label = 'Mon nouveau modèle' ;

``` 


### Onglets des formulaires

Sans que ce soit obligatoire en aucune façon, les modèles de formulaires peuvent répartir les catégories de métadonnées par onglets.

Avant d'y affecter des catégories, les onglets doivent être définis dans la table `z_plume.meta_tab`. Celle-ci contient deux champs :
- `tab` pour le nom de l'onglet. Il est limité à 48 caractères et doit obligatoirement être renseigné ;
- `tab_num` sert à ordonner les onglets. Les onglets sont affichés du plus petit numéro au plus grand (`NULL` à la fin), puis par ordre alphabétique en cas d''égalité. Les numéros n''ont pas à se suivre et peuvent être répétés. *NB. Tous les onglets de `meta_tab` ne seront évidemment pas présents dans tous les modèles, mais ceux qui le sont seront donc toujours présentés dans le même ordre quel que soit le modèle.*


### Catégories de métadonnées

La table `z_plume.meta_categorie` répertorie toutes les catégories de métadonnées disponibles, à la fois celle qui sont décrites par le schéma SHACL des catégories communes (fichier [shape.ttl](../../plume/rdf/data/shape.ttl)) et les catégories supplémentaires locales définies par l'ADL pour le seul usage de son service.

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
| `datatype` | Type de valeur attendu pour la catégorie, parmi (type énuméré `z_plume.meta_data_type`) : `'xsd:string'`, `'xsd:integer'`, `'xsd:decimal'`, `'xsd:boolean'`, `'xsd:date'`, `'xsd:time'`, `'xsd:dateTime'`, `'xsd:duration'`, `'rdf:langString'` (chaîne de caractères avec une langue associée[^langString]) et `'gsp:wktLiteral'` (géométrie au format textuel WKT). Cette information détermine notamment la nature des widgets utilisés par Plume pour afficher et éditer les valeurs, ainsi que les validateurs appliqués. | Pour les catégories communes, les modifications apportées sur ce champ ne seront pas prises en compte sauf s'il s'agit d'utiliser des dates avec heures (`'xsd:dateTime'`) à la place des dates simples (`'xsd:date'`) ou réciproquement. Si, pour une catégorie locale, aucune valeur n'est renseignée pour ce champ (ni dans `meta_categorie` ni dans `meta_template_categories`), le plugin considérera que la catégorie prend des valeurs de type `'xsd:string'`. |
| `is_long_text` | `True` pour une catégorie appelant un texte de plusieurs lignes. | Cette information ne sera prise en compte que si le type de valeur (`datatype`) est `'xsd:string'` ou `'rdf:langString'`. Pour le type `'gsp:wktLiteral'`, elle vaut implicitement toujours `True`. Pour les autres types, notamment `'xsd:string'` et `'rdf:langString'`, elle vaut implicitement toujours `False` (si tant est qu'elle ait encore un objet). |
| `rowspan` | Nombre de lignes occupées par le widget de saisie, s'il y a lieu de modifier le comportement par défaut de Plume. | La valeur ne sera considérée que si `is_long_text` vaut `True`. | 
| `special` | Le cas échéant, mise en forme spécifique à appliquer au champ. Valeurs autorisées (type énuméré `z_plume.meta_datatype`) : `'url'`, `'email'`, et `'phone'`. |  Pour les catégories communes, les modifications apportées à ce champ ne seront pas prises en compte. |
| `placeholder` | Valeur fictive pré-affichée en tant qu'exemple dans le widget de saisie, s'il y a lieu. | | 
| `input_mask` | Masque de saisie, s'il y a lieu. La syntaxe est décrite dans la [documentation de l'API Qt for python](https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QLineEdit.html#PySide2.QtWidgets.PySide2.QtWidgets.QLineEdit.inputMask). | La valeur sera ignorée si le widget utilisé pour la catégorie ne prend pas en charge ce mécanisme. |
| `is_multiple` | `True` si la catégorie admet plusieurs valeurs. | Pour les catégories communes, les modifications apportées sur ce champ ne seront pas prises en compte. |
| `unilang` | `True` si la catégorie n'admet plusieurs valeurs que si elles sont dans des langues différentes (par exemple un jeu de données n'a en principe qu'un seul titre, mais il peut être traduit). | Pour les catégories communes, les modifications apportées sur ce champ ne seront pas prises en compte. `is_multiple` est ignoré quand `unilang` vaut `True`. Cette information n'est considérée que si `datatype` vaut `'rdf:langString'`. | 
| `is_mandatory` | `True` si une valeur doit obligatoirement être saisie pour cette catégorie. | Modifier cette valeur permet de rendre obligatoire une catégorie commune optionnelle, mais pas l''inverse. |
| `sources` | Pour une catégorie prenant ses valeurs dans un ou plusieurs thésaurus, liste des sources admises. | Cette information n'est considérée que pour les catégories communes. Il n'est pas possible d'ajouter des sources ni de les retirer toutes - Plume reviendrait alors à la liste initiale -, mais ce champ permet de restreindre la liste à un ou plusieurs thésaurus jugés les mieux adaptés. |
| `geo_tools` | Pour une catégorie prenant pour valeurs des géométries, liste des fonctionnalités d'aide à la saisie à proposer, parmi `'show'` (visualisation de la géométrie saisie), `'point'` (tracé manuel d'une géométrie ponctuelle), `'linestring'` (tracé manuel d'une géométrie linéaire), `'rectangle'`  (tracé manuel d'un rectangle), `'polygon'` (tracé manuel d'un polygone), `'circle'` (tracé manuel d'un cercle), `'bbox'` (calcul du rectangle d'emprise de la couche courante), `'centroid'` (calcul du centre du rectangle d'emprise de la couche courante). | Cette information ne sera considérée que si le type (`datatype`) est `'gsp:wktLiteral'`. Pour retirer toutes les fonctionnalités proposées par défaut pour une catégorie commune, on saisira une liste vide, soit `ARRAY[]::z_plume.meta_geo_tool[]`. |
| `compute` | Liste des fonctionnalités de calcul à proposer, parmis, `'auto'` (déclenchement automatique lorsque la fiche de métadonnées est générée), `'manuel'` (déclenchement à la demande, lorsque l'utilisateur clique sur le bouton qui apparaîtra alors à côté du champ de saisie dans le formulaire). | Cette information ne sera considérée que si une méthode de calcul est effectivement disponible pour la catégorie. Pour retirer toutes les fonctionnalités proposées par défaut pour une catégorie commune, on saisira une liste vide, soit `ARRAY[]::z_plume.meta_compute[]`. |
| `compute_params` | Paramètres optionnels attendus par la méthode de calcul, si opportun. À spécifier sous la forme d'un dictionnaire JSON dont les clés correspondent aux noms des paramètres et les valeurs sont les valeurs des paramètres. Cf. [Métadonnées calculées](./metadonnees_calculees.md) pour plus de détails. | Cette information ne sera considérée que si une méthode de calcul est effectivement disponible pour la catégorie et qu''elle admet un ou plusieurs paramètres. |
| `template_order` | Ordre d'apparence de la catégorie dans le formulaire. Les plus petits numéros sont affichés en premier, il n'est pas nécessaire que les numéros se suivent. Dans le cas des catégories communes, qui ont une structure arborescente, il s'agit de l'ordre parmi les catégories de même niveau dans la branche. | |

[^langString]: Si une catégorie de métadonnée est de type `'rdf:langString'`, l'interface de Plume permettra, lorsque les modes édition et traduction sont simultanément activés, d'associer une langue à la métadonnée. Par défaut, les valeurs saisies hors mode traduction seront présumées être dans la [langue principale des métadonnées](./actions_generales.md#langue-principale-des-métadonnées). Une catégorie de type `'xsd:string'` est une chaîne de caractères sans langue, ce qui est adapté pour toutes les catégories apparentées à des identifiants (nom d'application, nom d'objet PostgreSQL...), qui n'ont pas vocation à être traduites. Pour toutes les autres, `'rdf:langString'` est généralement préférables.

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
- le module `plume.pg.queries` pour les requêtes SQL pré-écrites à exécuter sur les curseurs de Psycopg ;
- le module `plume.pg.template` pour le traitement du résultat de ces requêtes.

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

La première étape consiste à déterminer :
- si l'extension *PlumePg* est installée sur la base d'où provient la table considérée ;
- si la version installée est compatible avec la version du plugin QGIS de l'utilisateur ;
- si l'utilisateur dispose bien des [privilèges requis](#privilèges-nécessaires) sur les objets de l'extension.

Pour le vérifier, une seule requête :

```python

import psycopg2
from plume.pg import queries

conn = psycopg2.connect(connection_string)

with conn:
    with conn.cursor() as cur:
    
        query = queries.query_plume_pg_check()
        cur.execute(*query)
        result = cur.fetchone()

conn.close()

```

Si le premier élément du tuple `result` vaut `True`, toutes les conditions sont réunies pour utiliser les modèles définis par *PlumePg*. On pourra donc poursuivre avec les opérations décrites dans les parties suivantes.

```python

if result[0]:
    ...

```

Dans le cas contraire, on se reportera à la partie [Avec les modèles stockés en local](#avec-les-modèles-stockés-en-local).

Les autres éléments de `result` permettent de décrire plus précisément le problème :
- `result[1]` est une liste de longueur 2 qui rappelle les versions de *PlumePg* compatibles avec la version du plugin QGIS dont dispose l'utilisateur. Concrètement, toutes les versions supérieures ou égales au premier élément de la liste et strictement inférieures au second sont considérées comme compatibles.
- `result[2]` fournit la version de *PlumePg* installée sur la base cible. Si cet élément vaut `None`, l'extension n'est pas installée sur la base.
- `result[3]` fournit la version de référence de *PlumePg* disponible sur le serveur. Si cet élément vaut `None`, l'extension n'est pas disponible pour l'installation.
- `result[4]` est une liste de schémas sur lesquels l'utilisateur ne dispose par du privilège `USAGE` requis. La liste est vide si l'extension n'est pas installée dans une version compatible ou si les droits sur les schémas sont suffisants.
- `result[5]` est une liste de tables et vues sur lesquelles l'utilisateur ne dispose par du privilège `SELECT` requis. La liste est vide si l'extension n'est pas installée dans une version compatible, si l'utilisateur ne dispose pas des droits requis sur les schémas, ou si les droits sur les tables sont suffisants.

L'infobulle du [bouton de sélection du modèle](./actions_generales.md#choix-de-la-trame-de-formulaire) pourrait expliquer pourquoi les modèles n'ont pas pu être chargés depuis la base. Le message serait alors construit par une suite de conditions similaire à celle-ci :

```python

if not result[3]:
    pb = "L'extension PlumePg n'est pas disponible sur le serveur cible."
elif not result[2]:
    pb = "L'extension PlumePg n'est pas installée sur la base cible."
elif result[5]:
    pb = 'Votre rôle de connexion ne dispose pas du privilège ' \
        'SELECT sur {} {}.'.format(
        'la table' if len(result[5]) == 1 else 'les tables',
        ', '.join(result[5]))
elif result[4]:
    pb = 'Votre rôle de connexion ne dispose pas du privilège ' \
        'USAGE sur {} {}.'.format(
        'le schéma' if len(result[4]) == 1 else 'les schémas',
        ', '.join(result[4]))
else:
    pb = 'Votre version de Plume est incompatible avec PlumePg < {} ou ≥ {}' \
        ' (version base cible : PlumePg {}).'.format(result[1][0],
        result[1][1], result[2])

```

### Récupération de la liste des modèles

Il s'agit simplement d'aller chercher sur le serveur le contenu de la table `meta_template`, à la petite nuance près que `query_list_templates()` exécute ce faisant les filtres SQL du champ `sql_filter` (côté serveur, grâce à la fonction `z_plume.meta_execute_sql_filter(text, text, text)` de l'extension *PlumePg*) et c'est le booléen résultant qui est importé plutôt que le filtre lui-même.

```python

import psycopg2
from plume.pg import queries

conn = psycopg2.connect(connection_string)

with conn:
    with conn.cursor() as cur:
    
        cur.execute(*queries.query_list_templates(schema_name, table_name))
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

*`metagraph` est le graphe contenant les métadonnées de la table ou vue considérée. Cf. [Génération du dictionnaire des widgets](./generation_dictionnaire_widgets.md#metagraph--le-graphe-des-métadonnées-pré-existantes).*

Il est tout à possible que la fonction `search_template` ne renvoie rien, d'autant que tous les services ne souhaiteront pas nécessairement utiliser ce mécanisme d'application automatique des modèles. Dans ce cas, on utilisera le "modèle préféré" (`preferedTemplate`) désigné dans les [paramètres de configuration de l'utilisateur](./parametres_utilisateur.md) -- sous réserve qu'il soit défini et fasse bien partie de `templateLabels` -- ou, à défaut, aucun modèle (`template` vaut `None`).

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
    
        cur.execute(*queries.query_get_categories(tpl_label))
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
    
        cur.execute(*queries.query_template_tabs(tpl_label))
        tabs = cur.fetchall()

conn.close()

```

Si `tabs` est une liste vide, toutes les catégories seront affectées à un unique onglet nommé _"Général"_.

### Génération de *template*

À ce stade, `categories` est une liste de tuples, qui doit être consolidée avant de pouvoir être utilisée pour générer le [dictionnaire de widgets](./generation_dictionnaire_widgets.md).

Concrètement, il s'agit de créer un objet `plume.pg.template.TemplateDict` à partir de `categories` et `tabs` :

```python

template = TemplateDict(categories, tabs)

```

Le modèle de formulaire ainsi obtenu peut être passé dans l'argument `template` du constructeur de `plume.rdf.widgetsdict.WigdetsDict`. Cf. [Génération du dictionnaire des widgets](./generation_dictionnaire_widgets.md#template--le-modèle-de-formulaire).


## Avec les modèles stockés en local

Cette partie décrit la méthode alternative de gestion des modèles mise en oeuvre par Plume dans le cas où l'extension PostgreSQL *PlumePg* n'est pas active sur la base cible (cf. [Présence de l'extension *PlumePg*](#présence-de-lextension-plumepg) pour le test). Le processus est similaire à celui décrit dans la partie [Import des modèles par Plume](#import-des-modèles-par-plume), si ce n'est que certaines étapes ne sont plus nécessaires.

Faute de pouvoir importer les modèles personnalisés par l'administrateur de données depuis le serveur PostgreSQL, Plume utilise des copies locales des modèles pré-configurés de *PlumePg*. Ceux-ci sont stockés dans le fichier [templates.json](../../plume/pg/data/templates.json), dont on chargera le contenu en créant un objet de classe `plume.pg.template.LocalTemplatesCollection`. Celui-ci n'étant jamais modifié, on pourra le générer lorsque Plume rencontre pour la première fois une base sans *PlumePg* et le référencer de manière à pouvoir le réutiliser à chaque nouvelle occurrence par la suite.

```python

from plume.pg.template import LocalTemplatesCollection

templates_collection = LocalTemplatesCollection()

```

Pour connaître l'éventuel modèle à appliquer automatiquement à une table donnée, on procédera comme décrit dans la partie [Sélection automatique du modèle](#sélection-automatique-du-modèle). La seule différence est que la variable `templates` ne résulte pas d'une requête générée par `plume.pg.queries.query_list_templates` mais par `plume.pg.queries.query_evaluate_local_templates`.


```python

import psycopg2
from plume.pg import queries
from plume.pg.template import search_template

conn = psycopg2.connect(connection_string)

with conn:
    with conn.cursor() as cur:
    
        query = queries.query_evaluate_local_templates(templates_collection, schema_name, table_name)
        cur.execute(*query)
        templates = cur.fetchall()

conn.close()

tpl_label = search_template(templates, metagraph)

```

*Où `table_name` est le nom de la table ou vue dont on affiche les métadonnées, `schema_name` le nom de son schéma, et `metagraph` le graphe contenant ses métadonnées.*

Puisque les modèles sont stockés localement, il n'est pas nécessaire d'envoyer des requêtes pour connaître les catégories de métadonnées et onglets associés (autrement dit, les parties [Récupération des catégories associées au modèle retenu](#récupération-des-catégories-associées-au-modèle-retenu) et [Récupération des onglets associés au modèle retenu](#récupération-des-onglets-associés-au-modèle-retenu) n'ont pas d'équivalent ici). On obtiendra directement l'objet `plume.pg.template.TemplateDict` à fournir en argument au constructeur de `plume.rdf.widgetsdict.WidgetsDict` en interrogeant le répertoire des modèles locaux.

```python

template = templates_collection[tpl_label] if tpl_label else None

```

## Gestion des modèles via Plume

*Voir aussi [Gestion de *PlumePg* via Plume](./gestion_plume_pg.md#gestion-de-plumepg-via-plume) pour l'administration générale de l'extension PlumePg avec l'interface de Plume.*

Plume propose aux administrateurs des serveurs PostgreSQL une interface simplificatrice pour la conception de leurs modèles, accessible via le menu *Configuration* de la barre d'outils ![configuration.svg](../../plume/icons/general/configuration.svg).

### Conditions d'apparition

Les fonctionnalités suivantes ne doivent être montrées à l'utilisateur de Plume que si :
* L'extension PostgreSQL *PlumePg* est active sur la base courante, dans une version compatible avec celle de Plume - cf. [Présence de l'extension *PlumePg*](#présence-de-lextension-plumepg).
* L'utilisateur est effectivement habilité à gérer les modèles. Cette condition est contrôlée par la requête générée par `plume.pg.queries.query_is_template_admin`.

```python

import psycopg2
from plume.pg import queries

conn = psycopg2.connect(connection_string)

with conn:
	with conn.cursor() as cur:
	
		cur.execute(
			*queries.query_is_template_admin()
			)
		res = cur.fetchone()
        is_template_admin = res[0]

conn.close()

```
*`connection_string` est la chaîne de connexion à la base de données PostgreSQL.*

Le résultat `is_template_admin` est un booléen, qui vaudra `True` si et seulement si l'utilisateur dispose des privilèges nécessaires pour modifier les modèles.

*NB : Les privilèges contrôlés par la requête ne sont pas tout à fait suffisants pour pouvoir éditer les modèles - elle vérifie les droits sur le schéma et les tables, il faut aussi des droits sur les séquences, les types, etc. Néanmoins, disposer de ces privilèges signifer qu'on a voulu habiliter l'utilisateur à modifier les modèles. S'il lui manque des droits annexes, Plume lui fera savoir par un message d'erreur qui permettra à l'administrateur du serveur d'accorder les privilèges manquants.*

### Manipulation des données des modèles

Les données des modèles sont stockées en base dans une structure de données mise en place par *PlumePg*. Elles peuvent être consultées et éditées via des requêtes générées par des fonctions du module `plume.pg_queries`.

* Objet "modèle" (table `z_plume.meta_template`) :

   | Action | Fonction pour générer la requête |
   | --- | --- |
   | Lecture | `query_read_meta_template` |
   | Insertion & Mise à jour | `query_insert_or_update_meta_template` |
   | Suppression | `query_delete_meta_template` |

* Objet "catégorie de métadonnée" (table `z_plume.meta_categorie`) :

   | Action | Fonction pour générer la requête |
   | --- | --- |
   | Lecture | `query_read_meta_categorie` |
   | Insertion & Mise à jour | `query_insert_or_update_meta_categorie` |
   | Suppression | `query_delete_meta_categorie` |

* Objet "onglet" (table `z_plume.meta_tab`) :

   | Action | Fonction pour générer la requête |
   | --- | --- |
   | Lecture | `query_read_meta_tab` |
   | Insertion & Mise à jour | `query_insert_or_update_meta_tab` |
   | Suppression | `query_delete_meta_tab` |

* Objet "association modèle-catégorie" (table `z_plume.meta_template_categories`) :

   | Action | Fonction pour générer la requête |
   | --- | --- |
   | Lecture | `query_read_meta_template_categories` |
   | Insertion & Mise à jour | `query_insert_or_update_meta_template_categories` |
   | Suppression | `query_delete_meta_template_categories` |

Les requêtes de lecture renvoient les données sous la forme d'une liste de tuples contenant chacun un unique dictionnaire. Ce dictionnaire contient les attributs d'un objet (modèle, onglet, etc. selon la table consultée). Ses clés sont les noms des champs de la table PostgreSQL.

Par exemple, pour la récupération des données de la table des onglets :

```python

import psycopg2
from plume.pg import queries

conn = psycopg2.connect(connection_string)

with conn:
	with conn.cursor() as cur:
	
		cur.execute(
			*queries.query_read_meta_tab()
		)
		tabs = cur.fetchall()

conn.close()

```
*`connection_string` est la chaîne de connexion à la base de données PostgreSQL.*

Le contenu de `tabs` aura cette forme :

```python
[
    (
        {
            'tab': 'Onglet n°1',
            'tab_num': 1
        }
    ),
    (
        {
            'tab': 'Onglet n°2',
            'tab_num': 2
        }
    )
] 
```

Les requêtes d'insertion/modification et les requêtes de suppression fonctionnent de la même façon : elles prennent en argument un dictionnaire `data` décrivant l'objet à créer, modifier ou supprimer, sous la même forme que les dictionnaires renvoyés par les fonctions de consultation. Ses clés doivent être nommées d'après des champs qui existent effectivement dans la table cible, ses valeurs doivent être fournies dans un format compatible avec les types desdits champs - cf. [Modalités de saisie spécifiques à certains champs](#modalités-de-saisie-spécifiques-à-certains-champs).

Le dictionnaire peut contenir les valeurs de tous les champs de la table (le cas échéant vides), ou seulement ceux qui ont été renseignés/modifiés, auxquels il faudra parfois ajouter quelques champs nécessaires au traitement - cf. [Champs obligatoires](#champs-obligatoires). Dans le cas d'une suppression, seul le champ de clé primaire est attendu. Les autres informations peuvent néanmoins être fournies, elles ne seront simplement pas utilisées.

Les fonctions d'insertion/modification renvoient l'enregistrement mis à jour, ci-après `new_data`, tel qu'il est stocké dans la base à l'issue de l'opération. Il est indispensable d'actualiser le formulaire de saisie avec ces informations, qui peuvent différer significativement de la saisie initiale de l'utilisateur (ajout des valeurs par défaut sur les nouveaux enregistrements, etc.).

Exemple de la définition d'un nouveau modèle :

```python

import psycopg2
from plume.pg import queries

conn = psycopg2.connect(connection_string)

with conn:
	with conn.cursor() as cur:
	
		cur.execute(
			*queries.query_insert_or_update_meta_template(data)
		)
        new_data = cur.fetchone()[0]

conn.close()

```

`data` pourrait ressembler à ceci : 

```python
{
    'tpl_label': 'Mon nouveau modèle',
    'priority': 50
}
```

Il est également possible de saisir dans `data` une liste de valeurs, en utilisant le second argument `columns` pour les noms des champs.

```python

import psycopg2
from plume.pg import queries

conn = psycopg2.connect(connection_string)

with conn:
	with conn.cursor() as cur:
	
		cur.execute(
			*queries.query_insert_or_update_meta_template(
                data, columns=columns
            )
		)
        new_data = cur.fetchone()[0]

conn.close()

```

Avec l'exemple précédent, `data` serait ici la liste `['Mon nouveau modèle', 50]`, et `columns` la liste `['tpl_label', 'priority']`.

### Champs obligatoires

Les champs qui suivent doivent impérativement apparaître dans l'argument `data` fourni au constructeur de requêtes avec une valeur non nulle. Les champs précédés d'un astérisque peuvent être omis, mais ne doivent pas être vides s'ils sont présents.

| | Insertion | Modification | Suppression |
| --- | --- | --- | --- |
| Modèle | `tpl_label` | `tpl_label` | `tpl_label` |
| Catégorie de métadonnée (locale) | `label` | `path`, *`label` | `path` |
| Catégorie de métadonnée (commune) | INTERDIT | `path`, `origin` (valant `'shared'`), *`label` | `path` |
| Onglet | `tab`, *`enabled` | `tab`, *`enabled` | `tab` |
| Association modèle-catégorie | `tpl_label`, `shrcat_path` ou `loccat_path` | `tplcat_id` | `tplcat_id` |

Les catégories de métadonnées communes sont distinguées des catégories locales par le fait que l'attribut `origin` est présent et vaut `shared`. Il n'est pas permis d'ajouter de métadonnée commune : si `origin` vaut `shared`, la clé primaire `path` devra impérativement être renseignée et correspondre à l'identifiant d'une catégorie pré-existante que l'utilisateur souhaite mettre à jour.

### Champs non éditables

Les champs listés ci-après ne doivent pas pouvoir faire l'objet d'une modification manuelle par l'utilisateur.

| Objet | Champs |
| --- | --- |
| Modèle | - |
| Catégorie de métadonnée (locale) | `path` (renseigné automatiquement à la création en base), `is_node`, `sources`, `origin` (vaut toujours `'local'`) |
| Catégorie de métadonnée (commune) | `path` (pré-renseigné), `origin` (vaut toujours `'shared'`), `is_node` |
| Onglet | - |
| Association modèle-catégorie | `tpl_label` + `shrcat_path` + `loccat_path` (définis une fois pour toute quand l'utilisateur déclare la catégorie comme utilisée par le modèle), `tplcat_id` (renseigné automatiquement à la création en base) |

### Champs avec des valeurs imposées

Les champs ci-après n'admettent qu'un nombre fini de valeurs, qui peuvent être listées grâce à des requêtes du module `plume.pg.queries`.

| Champ | Objet(s) |  Requête listant les valeurs |
| --- | --- | --- |
| `special` | Catégories et Associations modèle-catégorie | `query_read_enum_meta_special` |
| `datatype` | Catégories et Associations modèle-catégorie | `query_read_enum_meta_datatype` |
| `geo_tools` | Catégories et Associations modèle-catégorie | `query_read_enum_meta_geo_tool` |
| `compute` | Catégories et Associations modèle-catégorie | `query_read_enum_meta_compute` |

Exemple de la récupération des valeurs admises par le champ `datatype` :

```python

import psycopg2
from plume.pg import queries

conn = psycopg2.connect(connection_string)

with conn:
	with conn.cursor() as cur:
	
		cur.execute(
			*queries.query_read_enum_meta_datatype()
		)
        enum_values = cur.fetchone()[0]

conn.close()

```

`enum_values` est la liste des valeurs, triées par ordre alphabétique.

### Modalités de saisie spécifiques à certains champs

D'une manière générale, le widget à utiliser pour un champ peut être déduit de son type.

| Type PostgreSQL | Type Python | Widget | Remarques |
| --- | --- | --- | --- |
| `boolean` | `bool` | `QCheckbox` | Avec trois états sauf mention contraire ci-après. |
| `text` | `str` | `QLineEdit` |  |
| `varchar` | `str` | `QLineEdit` | Validateur `QRegularExpressionValidator` avec l'expression régulière `QRegularExpression(f'^.{{0,{m}}}$')` où `m` est une variable correspondant à la longueur limite. En inscrivant plutôt la limite en dur, on aurait par exemple `QRegularExpression('^.{0,48}$')` pour le type `varchar(48)`. |
| `int` | `int` | `QLineEdit` | Validateur `QIntValidator` pour assurer que seuls des chiffres sont saisis. |
| type énuméré | `str` | `QCombobox`, ou un `QRadioButton` par valeur selon leur nombre | Seules les valeurs prévues par le type sont autorisées. Cf. [Champs avec des valeurs imposées](#champs-avec-des-valeurs-imposées). |
| liste de type énuméré | `list(str)` | Un `QCheckbox` par valeur autorisée ? | Idem *type énuméré*. |
| `text[]` | `list(str)` | *à déterminer* | |

Les champs de type `jsonb` - `compute_params` dans `meta_template_categories` et `meta_categorie` et `md_conditions` dans `meta_template` - nécessiteront des modalités de saisie et validation adaptées.

Les champs qui suivent requièrent des ajustements spécifiques pour assurer le respect des contraintes définies sur les tables de stockage.

| Champ | Objet(s) |  Particularité |
| --- | --- | --- |
| `tpl_label` | Modèles | Expression régulière à adapter pour assurer aussi la non nullité : `QRegularExpression('^.{1,48}$')`. |
| `enabled` | Modèles | Seulement deux états pour la case à cocher, qui doit être cochée par défaut. |
| `tab` | Onglets | Expression régulière à adapter pour assurer aussi la non nullité : `QRegularExpression('^.{1,48}$')`. |
| `label` | Catégories | Validateur `QRegularExpressionValidator` avec l'expression régulière `QRegularExpression('.')` pour la non nullité. |
| `rowspan` | Catégories et Associations modèle-catégorie | Le `QIntValidator` doit aussi fixer la valeur minimum à 1 et maximum à 99. |

### Modifications en cascade

Les champs `tpl_label` de la table des modèles et `tab` de la table des onglets sont libremement modifiables par l'utilisateur, mais il doit être noté que leur modification se répercutera dans la table d'association des catégories aux modèles, où ils sont utilisés comme clés étrangères. Concrètement, si le nom d'un modèle change, son nouveau nom est reporté dans la table d'association modèle-catégorie. Il n'est pas exclu que d'autres champs puissent avoir un comportement similaire à l'avenir.

Ainsi, pour assurer la cohérence des informations présentées à l'utilisateur, il est souhaitable que Plume actualise au moins les données issue de la table d'association modèle-catégorie après toute action sur les tables des modèles, des onglets et (de manière préventive) des catégories.

Toute modification de la table des modèles devra aussi être suivie du rechargement de la liste des modèles disponibles utilisée par le bouton de choix du modèle dans la barre d'outils de Plume. Cf. [Récupération de la liste des modèles](#récupération-de-la-liste-des-modèles).

### Import des modèles pré-configurés

Pour continuer à bénéficier des modèles pré-configurés après l'activation de *PlumePg* sur la base et pouvoir ensuite les éditer, l'administrateur doit commencer par charger ces modèles dans les tables de stockage.

Cette action pourra être proposée via le menu *Configuration* de la barre d'outils ![configuration.svg](../../plume/icons/general/configuration.svg). Ses [conditions d'apparition](#conditions-dapparition) sont les mêmes que pour l'interface de configuration des modèles.

Libellé : *Importer ou réinitialiser les modèles pré-configurés*

Infobulle : *Charge en base les modèles de fiche de métadonnées pré-configurés de Plume (Basique, Classique...). Réexécuter cette action a pour effet de réinitialiser les modèles. Les modifications réalisées après l'import initial seront perdues.*

L'action est réalisée via la requête générée par la fonction `plume.pg.queries.query_plume_pg_import_sample_template`.

```python

import psycopg2
from plume.pg import queries

conn = psycopg2.connect(connection_string)

with conn:
	with conn.cursor() as cur:
	
		cur.execute(
			*queries.query_plume_pg_import_sample_template()
		)

conn.close()

```

À noter que la fonction permet aussi l'import d'un unique modèle ou d'une liste de modèles, dont le ou les noms sont alors à fournir en argument.

Il pourra être pertinent de recharger depuis le serveur la liste des modèles disponibles (utilisée pour le bouton de choix du modèle dans la barre d'outils de Plume) après l'exécution de cette requête - cf. [Récupération de la liste des modèles](#récupération-de-la-liste-des-modèles).
