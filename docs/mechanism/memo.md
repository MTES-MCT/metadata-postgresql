# Aide-mémoire

Cette page récapitule les actions à réaliser pour maintenir et modifier différents aspects du fonctionnement de Plume.

[Exécution des tests](#exécution-des-tests) • [Générer un ZIP propre du plugin](#générer-un-zip-propre-du-plugin) • [Modifier les catégories de métadonnées communes](#modifier-les-catégories-de-métadonnées-communes) • [Ajouter une option de configuration des catégories de métadonnées](#ajouter-une-option-de-configuration-des-catégories-de-métadonnées) • [Modifier les modèles pré-configurés de *PlumePg*](#modifier-les-modèles-ré-configurés-de-plumepg) • [Gestion des dépendances](#gestion-des-dépendances) • [Exporter toutes les icônes de Plume au format PNG](#exporter-toutes-les-icônes-de-plume-au-format-png) • [Ajouter un vocabulaire](#ajouter-un-vocabulaire)

## Exécution des tests

Le module {py:mod}`admin.tests` compile les tests de tous les modules de Plume.

On pourra soit exécuter le fichier {file}`/admin/tests.py` comme un script, ce qui lancera l'ensemble des tests, soit utiliser la fonction {py:func}`admin.tests.run`.

Pour lancer tous les tests :

```python

>>> from admin.tests import run
>>> run()

```

Pour lancer uniquement les tests de certains modules ou packages, il faut les lister en argument (uniquement le dernier niveau d'arborescence). Par exemple, la commande suivante exécute les tests de tous les modules du package `plume.pg`, ainsi que les tests du module {py:mod}`plume.rdf.widgetkey` :

```python

>>> from admin.tests import run
>>> run('pg', 'widgetkey')

```

L'exécution des tests nécessite de se connecter à une base PostgreSQL avec un compte super-utilisateur. La base doit remplir les conditions suivantes :
- la version de PostgreSQL est supérieure ou égale à PostgreSQL 10.
- l'extension *PlumePg* (`plume_pg`) est disponible dans sa dernière version ainsi qu'en version 0.0.1, avec tous les fichiers de mise à jour pour passer de l'une à l'autre ;
- si requise pour l'installation de *PlumePg*[^pgcrypto], l'extension `pgcrypto` est active ;
- l'extension *PostGIS* (`postgis`) est active ;
- l'extension [*Asgard*](https://github.com/MTES-MCT/asgard-postgresql) (`asgard`) est disponible sur le serveur dans une version supérieure ou égale à 1.3.2, mais **non active**.

[^pgcrypto]: Nécessaire pour les versions inférieures ou égales à PostgreSQL 12. Cf. [Installation et gestion de l'extension PostgreSQL *PlumePg*](../usage/gestion_plume_pg.md).

## Générer un ZIP propre du plugin

Pour générer une archive utilisable par QGIS pour installer le plugin Plume, expurgée des fichiers de tests et autres éléments sans intérêt pour les utiliseurs, on exécutera :

```python

from admin.zip_plume import zip_plume

zip_plume()

```

Par défaut, le fichier ZIP est créé à la racine du dépôt, mais on pourra fournir en argument à `admin.zip_plume.zip_plume` le chemin absolu d'un autre répertoire cible. Dans tous les cas, l'archive sera nommée `plume.zip`.

## Modifier les catégories de métadonnées communes

### Schéma des métadonnées communes

Les catégories communes sont définies dans le fichier {file}`/plume/rdf/data/shape.ttl`, dit *schéma des métadonnées communes*. La première étape consiste à éditer manuellement ce fichier  (RDF encodé en turtle).

*TODO: détailler le paramétrage des catégories (informations obligatoires selon le type RDF, etc.).*

### Déclaration de l'espace de nommage

Si la modification implique l'usage d'un espace de nommage qui n'avait encore jamais été utilisé, son préfixe devra naturellement être ajouté dans l'en-tête du fichier `shape.ttl`, sans quoi la désérialisation du fichier échouera.

```turtle

@prefix gsp: <http://www.opengis.net/ont/geosparql#> .

```

Le préfixe ne devra comporter que des lettres minuscules.

Il faudra ensuite le déclarer dans le module {py:mod}`plume.rdf.namespaces`, qui gère les espaces de nommage de Plume. Cette opération est importante car Plume utilise la notation N3 pour les exports et, surtout, dans les modèles de formulaire.

Concrètement, il s'agit d'ajouter un objet `rdflib.namespace.Namespace` à ceux déjà définis au début du fichier.

```python

GSP = Namespace('http://www.opengis.net/ont/geosparql#')

```

Le nouvel espace de nommage devra ensuite être ajouté au dictionnaire `namespaces` :

```python

namespaces = {
    ...
    'gsp' : GSP,
    ...
    }

```

La clé de `namespaces` devra être identique au préfixe utilisé dans `shape.ttl`. La variable référençant l'objet `rdflib.namespace.Namespace` porte le même nom en majuscules[^local].

[^local]: La seule exception à cette règle est la variable `LOCAL`, qui a été choisie pour représenter le préfixe `uuid` parce qu'`UUID` est une classe du module `uuid` utilisée par ailleurs par Plume.

### Mise à jour de la liste des métadonnées communes de la documentation technique

La liste des métadonnées communes présentée dans le fichier [`/docs/usage/metadonnees_communes.md`](../usage/metadonnees_communes.md) est mise à jour par la commande suivante :

```python

>>> from admin.docs import shared_metadata_as_page
>>> shared_metadata_as_page()

```

### Mise à jour des catégories communes dans les scripts de *PlumePg*

La commande suivante permet de générer la commande `INSERT` qui ajoute toutes les métadonnées communes à la table `z_plume.meta_categorie` :

```python

>>> from admin.plume_pg import query_from_shape
>>> query_from_shape()

```

Le résultat doit être copié dans le script de création de l'extension, soit un fichier `plume_pg--x.x.x.sql` du répertoire {py:file}`/postgresql` portant le numéro de la version à venir de l'extension.

Pour le script de mise à jour depuis la version précédente, il sera généralement préférable de limiter les commandes aux catégories effectivement modifiées.

### Mise à jour des modèles pré-configurés

Par précaution, on veillera également à actualiser les fichiers JSON qui contiennent une copie locale des modèles pré-configurés de *PlumePg*. Cf. [Modifier les modèles pré-configurés de *PlumePg*](#modifier-les-modèles-pré-configurés-de-plumepg).


## Ajouter une option de configuration des catégories de métadonnées

Les explications qui suivent prennent l'exemple de l'option `geo_tools`, qui définit les fonctionnalités d'aide à la saisie des géométries à proposer pour la catégorie. Chaque cas nécessitera évidemment des adaptations selon les mécanismes associés à l'option, mais le principe restera le même. Toute nouvelle option doit être implémentée à chaque niveau de Plume : schéma des métadonnées communes (fichier {py:file}`/plume/rdf/data/shape.ttl`), désérialisation du schéma métadonnées communes (module {py:mod}`plume.rdf.properties`), modèles de formulaires (extension [*PlumePg*], dont le code se trouve dans le répertoire {py:file}`/postgresql`), import des modèles de formulaire (module {py:mod}`plume.pg.queries`), désérialisation des modèles de formulaire (module {py:mod}`plume.pg.template`), arbre des clés (module {py:widgetkey}`plume.rdf.widgetkey`), dictionnaire interne (module {py:mod}`plume.rdf.internaldict`), dictionnaire de widgets (module {py:mod}`plume.rdf.widgetsdict`), construction du formulaire (description des modalités dans [`creation_widgets.md`](../usage/creation_widgets.md)).

### Schéma des métadonnées communes

Sauf à ce que l'option considérée ait vocation à être exclusivement gérée via les modèles de formulaire, on voudra généralement l'associer à certaines catégories définies par le schéma des métadonnées communes. Ceci suppose de compléter manuellement le fichier {py:file}`/plume/rdf/data/shape.ttl`.

Si elle n'est pas nativement prévue par le language [SHACL](https://www.w3.org/TR/shacl/), on utilisera l'espace de nommage `http://registre.data.developpement-durable.gouv.fr/plume/`, dont le préfixe est `plume`. Par convention, le nom de l'option devra être écrit en CamlCase, avec une minuscule sur le premier caractère puisqu'il s'agit d'une propriété et non d'une classe.

Pour l'aide à la saisie des géométries, c'est ainsi le prédicat `plume:geoTool` qui a été utilisé :

```turtle

plume:LocationShape
    a sh:NodeShape ;
    sh:targetClass dct:Location ;
    sh:closed true ;
    sh:ignoredProperties ( rdf:type ) ;
    sh:property [
        sh:path dcat:centroid ;
        sh:name "Centroïde"@fr ;
        sh:description "Localisant du centre géographique des données, au format textuel WKT."@fr ;
        sh:nodeKind sh:Literal ;
        sh:datatype gsp:wktLiteral ;
        sh:maxCount 1 ;
        sh:order 4 ;
        plume:longText true ;
        plume:placeholder "<http://www.opengis.net/def/crs/EPSG/0/2154> POINT(651796.3281 6862298.5858)" ;
        plume:geoTool "show",
            "centroid",
            "point" ;
	]  ;

```

L'option peut avoir plusieurs valeurs, il faudra juste penser à le déclarer dans la suite.

### Désérialisation du schéma des métadonnées communes

C'est la fonction {py:func}`~plume.rdf.properties.read_shape_property` du module {py:mod}`plume.rdf.properties` qui a la charge de lire et d'interpréter le contenu du fichier {py:file}`/plume/rdf/data/shape.ttl`. Elle a besoin de connaître à l'avance les options à rechercher.

On ajoutera donc à son dictionnaire `prop_map` la nouvelle option : 

```python

prop_map = {
    ...
    SNUM.geoTool: ('geo_tools', True)
    }

```

La clé est l'IRI de l'option de configuration, dont le nom coïncide donc avec celui qui a été utilisé dans `shape.ttl`.

La valeur est un tuple dont le premier élément est le nom qui sera systématiquement donné à l'option dans le code de Plume. Par convention, il est formé de lettres minuscules avec le tiret bas comme séparateur. Il doit ressembler suffisamment à l'IRI pour qu'il ne fasse aucun doute que l'objet est le même. Le deuxième élément du tuple est un booléen qui indique si l'option peut prendre plusieurs valeurs (``True``) ou non (``False``). S'il vaut ``False`` une seule valeur sera considérée même s'il se trouvait y en avoir plusieurs dans `shape.ttl`.

### Extension *PlumePg*

Le plus souvent, une nouvelle option de configuration se manifestera dans *PlumePg* par un champ supplémentaire dans les tables `z_plume.meta_categorie` (ainsi que ses partitions `z_plume.meta_shared_categorie` et `z_plume.meta_local_categorie`) et `z_plume.meta_template_categories`, ainsi que la vue `z_plume.meta_template_categories_full`. Autant que possible, le nom du champ sera identique au nom python de l'option de configuration correspondante (le premier élément du tuple de `prop_map` évoqué dans le paragraphe précédent), soit `geo_tools` pour l'exemple considéré.

Si le champ n'admet que des valeurs pré-déterminées, on pourra définir un type énuméré semblable à `z_plume.meta_datatype`.

Pour l'actualisation des informations relatives aux métadonnées communes incluses dans *PlumePg*, on se reportera à [Mise à jour des catégories communes dans les scripts de *PlumePg*](#mise-à-jour-des-catégories-communes-dans-les-scripts-de-plumepg). Il faudra néanmoins commencer par modifier les fonctions {py:func}`admin.plume_pg._table_from_shape` et {py:func}`admin.plume_pg.query_from_shape` pour qu'elles prennent en compte le nouveau champ.

Dans {py:func}`admin.plume_pg._table_from_shape`, il s'agira d'ajouter le champ au tuple `category`. Dans le cas général, `prop_dict.get('option')` suffit (où `option` est le nom python de l'option de configuration). S'il est nécessaire de caster la valeur, on utilisera la même syntaxe que pour `geo_tool` :

```python

        ...
        geo_tools = prop_dict.get('geo_tools')
        ...
        category = (
            ...,
            ('cast', geo_tools, 'z_plume.meta_geo_tool[]') if geo_tools \
                and not no_cast else geo_tools,
            ...
            )

```

Dans {py:func}`admin.plume_pg.query_from_shape` on ajoute le champ supplémentaire à ceux qui apparaissent dans la commande `INSERT`, en prenant soin de respecter l'ordre du tuple `category` de {py:func}`admin.plume_pg._table_from_shape`.

### Import des modèles de formulaires

Pour que le nouveau champ des tables et vues de *PlumePg* soit exploité, encore faut-il que son contenu soit importé par Plume.

Ceci suppose de l'ajouter dans la requête définie par la fonction {py:func}`~plume.pg.queries.query_get_categories` du module {py:mod}`plume.pg.queries` :

```sql

SELECT 
    ...
    geo_tools::text[],
    ...
    FROM z_plume.meta_template_categories_full
    WHERE tpl_label = %s

```

Psycopg ne reconnaissant pas les types personnalisés, il est préférable de caster toutes les valeurs dont le type n'est pas standard en `text`, `text[]` ou autre type standard adapté.

### Désérialisation des modèles de formulaire

C'est maintenant la fonction d'initialisation de la classe {py:class}`plume.pg.template.TemplateDict` qu'il s'agit d'ajuster.

La boucle `for` nomme les colonnes du résultat de la requête {py:func}`~plume.pg.queries.query_get_categories` susmentionnée. Il faut donc y ajouter le nouveau champ, en s'assurant de respecter l'ordre de {py:func}`~plume.pg.queries.query_get_categories`.

```python

        for path, origin, ..., geo_tools, ... \
            in sorted(categories, reverse=True):

```

Puis le déclarer dans le dictionnaire `config` :

```python

            config = {
                ...
                'geo_tools': geo_tools,
                ...
                }

```

La clé de `config` doit impérativement porter le nom [déclaré dans `read_shape_property`](#désérialisation-du-schéma-des-métadonnées-communes) (premier élément du tuple de `prop_map`).

*NB. D'une manière générale, la validation et les conversions sont plutôt du ressort du module {py:mod}`plume.rdf.widgetkey`, le constructeur de {py:class}`plume.pg.template.TemplateDict` tend donc à reprendre telles quelles les informations issues du modèle. Il peut cependant être nécessaire de retraiter les valeurs à ce niveau dans le cas particulier d'une option pour laquelle les valeurs issues du modèle ne remplacent pas simplement les valeurs du schéma des métadonnées communes, mais nécessitent d'être comparées (cf. paragraphe suivant), ce qui supposent que les formats soient comparables.*

### Croisement du schéma et du modèle

Par défaut, Plume considère que si une catégorie apparaît à la fois dans le modèle et dans le schéma des métadonnées communes :
- les options de configuration définies dans le modèle prévalent sur celle du schéma ;
- les options du schéma s'appliquent quand le modèle ne dit rien.

S'il était nécessaire d'avoir un comportement différent pour l'option considérée, c'est la fonction {py:func}`~plume.rdf.properties.merge_property_dict` du module {py:mod}`plume.rdf.properties` qui devrait être modifiée en ce sens.

### Arbre des clés

L'arbre des clés est la colonne vertébrale de Plume. Il porte la structure des formulaires de saisie, garantie leur cohérence et permet leur évolution dynamique selon les commandes de l'utilisateur.

Avec les opérations précédentes, on aura fait en sorte que les constructeurs des clés  ({py:class}`plume.rdf.widgetkey.ValueKey` et autres classes de clés héritant de {py:class}`plume.rdf.widgetkey.WidgetKey`) reçoivent en paramètre la valeur de la nouvelle option. Le nom de ce paramètre est celui qui a été utilisé pour [la clé de `config`](#désérialisation-des-modèles-de-formulaire) et/ou [le premier élément du tuple de `prop_map`](#désérialisation-du-schéma-des-métadonnées-communes), soit `'geo_tools'` dans le cas des fonctionnalités d'aide à la saisie des géométries.

Ce que font les clés de cette information peut être très variable. Pour `geo_tools`, il s'agissait de définir un nouveau bouton annexe et ses caractéristiques, et cela a nécessité les opérations suivantes.

Classe `WidgetKey` :
- Ajout d'une variable partagée `WidgetKey.with_geo_buttons` permettant d'inhiber la création des boutons d'aide à la saisie des géométries.
- Modification de la méthode de classe `WidgetKey.reinitiate_shared_attributes` pour prendre en compte `WidgetKey.with_geo_buttons`.
- Modification de la méthode de classe `WidgetKey.width` pour qu'elle référence le nombre de colonnes occupées par les boutons d'aide à la saisie des géométries.
- Définition d'une propriété `WidgetKey.has_geo_button` (*getter* seul) valant toujours `False`.
- Définition d'une propriété `WidgetKey.geo_button_placement` (*getter* seul) qui définit le placement du bouton d'aide à la saisie des géométries lorsqu'il existe.
- Modification de la propriété `WidgetKey.minus_button_placement` pour que le bouton moins ne se superpose pas au bouton d'aide à la saisie des géométries lorsque les deux co-existent pour une même clé.
- Modification de la propriété `WidgetKey.placement` pour que le widget de saisie occupe bien l'espace normalement dédié au bouton de calcul lorsqu'il n'y en a pas.

Classe `ValueKey` :
- Re-définition de la propriété `WidgetKey.has_geo_button` (*getter* seul), avec cette fois les conditions d'apparition du bouton.
- Ajout via `WidgetKey._base_attributes` d'un attribut interne `GroupOfValuesKey._geo_tools` mémorisant la configuration du bouton (`self._geo_tools = None`).
- Définition d'une propriété `WidgetKey.geo_tools` (*getter* et *setter*) qui contrôle la mise à jour de `WidgetKey._geo_tools`, en s'assurant notamment de sa cohérence avec les autres attributs de la clé.
- Modification des *setter* des propriétés dont dépend `WidgetKey.geo_tools` (en l'occurence `WidgetKey.datatype`) pour que leur mise à jour post initialisation entraîne celle de `WidgetKey.geo_tools` - `if not self._is_unborn: self.geo_tools = self._geo_tools`.
- Modification de `WidgetKey._computed_attributes` pour initialiser `WidgetKey.geo_tools` à partir du paramètre `geo_tools` reçu par le constructeur (`self.geo_tools = kwargs.get('geo_tools')`). L'ordre d'initialisation des propriétés est important, il faudra toujours s'assurer que la propriété est initialisée après toutes les propriétés dont elle dépend.
- Ajout de `geo_tools` à la liste définie par la propriété `WidgetKey.attr_to_update`, car c'est une propriété dont il est admis de modifier la valeur post initialisation (ce qui devrait toujours être le cas pour les nouvelles propriétés).
- Ajout de `geo_tools` au dictionnaire de la propriété `WidgetKey.attr_to_copy`, car elle doit être copiée lorsque le groupe est dupliqué (ce qui devrait toujours être le cas pour les nouvelles propriétés).

Classe `GroupOfValuesKey` (car cette propriété doit être identique pour toutes les clés d'un même groupe de valeurs) :
- Ajout via `GroupOfValuesKey._base_attributes` d'un attribut interne `GroupOfValuesKey._geo_tools` mémorisant la configuration du bouton (`self._geo_tools = None`).
- Définition d'une propriété `GroupOfValuesKey.geo_tools` (*getter* et *setter*) qui contrôle la mise à jour de `GroupOfValuesKey._geo_tools`, en s'assurant notamment de sa cohérence avec les autres attributs de la clé.
- Modification des *setter* des propriétés dont dépend `GroupOfValuesKey.geo_tools` (en l'occurence `GroupOfValuesKey.datatype`) pour que leur mise à jour post initialisation entraîne celle de `GroupOfValuesKey.geo_tools` - `if not self._is_unborn: self.geo_tools = self._geo_tools`.
- Modification de `GroupOfValuesKey._computed_attributes` pour initialiser `GroupOfValuesKey.geo_tools` à partir du paramètre `geo_tools` reçu par le constructeur (`self.geo_tools = kwargs.get('geo_tools')`). L'ordre d'initialisation des propriétés est important, il faudra toujours s'assurer que la propriété est initialisée après toutes les propriétés dont elle dépend.
- Ajout de `geo_tools` à la liste définie par la propriété `GroupOfValuesKey.attr_to_update`, car c'est une propriété dont il est admis de modifier la valeur post initialisation (ce qui devrait toujours être le cas pour les nouvelles propriétés).
- Ajout de `geo_tools` au dictionnaire de la propriété `GroupOfValuesKey.attr_to_copy`, car elle doit être copiée lorsque le groupe est dupliqué (ce qui devrait toujours être le cas pour les nouvelles propriétés).

### Dictionnaire interne

Lorsque l'option de configuration est un élément d'entrée pour la génération du formulaire, il peut être nécessaire d'ajouter aux dictionnaires internes du dictionnaire de widgets une ou plusieurs clés portant cette information.

Les noms de nouvelles clés sont à déclarer dans la liste `keys` de la fonction d'initialisation de la classe `plume.rdf.internaldict.InternalDict`. Chaque clé doit être décrite dans le *docstring* de la classe.

Par convention, les noms des clés sont écrits en language naturel (ou presque). Ils doivent être explicites et utilisent des espaces comme séparateurs.
 
### Dictionnaire de widgets

Les modifications à réaliser dans le module `plume.rdf.widgetsdict` peuvent varier fortement selon la nature de la nouvelle option de configuration.

Si toutefois il s'agit d'un élément d'entrée pour générer le formulaire, et qu'une ou plusieurs clés ont ainsi été ajoutées à la classe `plume.rdf.internaldict.InternalDict`, il faudra a minima compléter la méthode `plume.rdf.widgetsdict.WidgetsDict.internalize` pour qu'elle sache définir les valeurs des nouvelles clés des dictionnaires internes en fonction des attributs des `WidgetKey`.

Si la nouvelle option suppose l'ajout de widgets annexes dans le formulaire, il faudra au moins :
- adapter la méthode `plume.rdf.widgetsdict.WidgetsDict.widget_placement` pour qu'elle spécifie leur placement ;
- compléter `plume.rdf.widgetsdict.WidgetsDict.list_widgets` pour qu'elle liste également ces widgets ;
- compléter `plume.rdf.widgetsdict.WidgetsDict.print` (méthode d'aperçu sommaire des formulaires utilisée à des fins de test) pour qu'elle représente ces widgets ;
- compléter `plume.rdf.widgetsdict.WidgetsDict.check_grids` pour que ces widgets soient pris en compte dans les tests de contrôle de placement.

### Génération du formulaire

La documentation technique, et particulièrement sa page [Création d'un nouveau widget](../usage/creation_widgets.md), devra être complétée d'autant que de besoin pour expliquer comment la nouvelle option de configuration doit être considérée lors de la génération du formulaire.


## Modifier les modèles pré-configurés de *PlumePg*

Les modèles pré-configurés de l'extension PostgreSQL *PlumePg* sont définis dans le code de l'extension (fichier `plume_pg--x.x.x.sql` du répertoire {file}`/postgresql`) et plus précisément dans le corps de la fonction `z_plume.meta_import_sample_template(text)`. Comme pour tout changement dans le code de *PlumePg*, leur modification devra donner lieu à une nouvelle version de *PlumePg*, outillée par un fichier `plume_pg--x.x.x-y.y.y.sql` permettant de passer de la version `x.x.x` à la version `y.y.y`.

Plume inclut par ailleurs des copies locales des modèles pré-configurés, qui permettent de bénéficier de quelques modèles basiques même si *PlumePg* n'est pas installée sur la base contenant la table ou vue à documenter. Ils sont stockés dans le fichier {file}`/plume/pg/data/templates.json`.

Une fois *PlumePg* modifiée, on pourra mettre à jour ce fichier avec la commande suivante :

```python

>>> from admin.plume_pg import store_sample_templates
>>> store_sample_templates()

```

## Gestion des dépendances

Plume incorpore les bibliothèques python nécessaires à son fonctionnement qui ne sont pas nativement présentes dans QGIS. En pratique, il s'agit de [RDFLib](https://pypi.org/project/rdflib/) et de ses dépendances en cascade, qui devront être contrôlées à chaque mise à jour d'une bibliothèque.

```python

>>> from importlib.metadata import requires
>>> requires('rdflib')

``` 

Les installateurs *wheel* des packages doivent être placés dans le répertoire {file}`/plume/bibli_install`. Les bibliothèques avec leur version de référence sont listées par le fichier {file}`/plume/requirements.txt`.

Pour que les mises à jour se fassent, il est nécessaire que la valeur du paramètre de configuration `plume.config.PLUME_VERSION` corresponde toujours au numéro de la version courante. Plume - plus précisément `plume.bibli_install.manageLibrary` - compare cette chaîne de caractères avec la valeur inscrite dans le fichier `QGIS3.ini` de l'utilisateur pour la version de QGIS courante. Par exemple, si Plume a été lancé sous QGIS 3.22.8, le paramètre utilisateur considéré est `Generale/3-22-8`. Lorsque ce paramètre est absent du fichier de configuration utilisateur (cas par exemple d'une nouvelle installation) ou s'il ne correspond pas à la valeur de `plume.config.PLUME_VERSION`, la mise à jour des dépendances selon `requirements.txt` est lancée et le numéro de version de Plume est enregistré dans le fichier `QGIS3.ini`, de manière à ce que ce processus ne s'exécute plus tant que Plume n'aura pas été mis à jour.


## Exporter toutes les icônes de Plume au format PNG

En veillant au préalable à ce qu'Inskape soit disponible, et son fichier de binaires dans le Path:

```python

>>> from admin.pictures import all_svg_as_png
>>> all_svg_as_png()

```

Les images sont stockées dans le répertoire `pictures` à la racine.


## Ajouter un vocabulaire

### Formalisation du vocabulaire

Les vocabulaires de Plume prennent la forme de fichiers RDF encodés en turtle, utilisant principalement le vocabulaire SKOS.

Un vocabulaire contient ainsi : 
- Un unique objet `skos:ConceptScheme` (ensemble de concepts), qui représente le vocabulaire dans son ensemble. Celui-ci doit avoir au moins une propriété `skos:prefLabel` fournissant un libellé (d'autant que possible en français), et il est possible d'ajouter des traductions dans d'autres langues. Celles-ci sont utilisées lorsque l'utilisateur modifie la langue principale de saisie des métadonnées dans l'interface de Plume. Il est souhaitable que le libellé indique la source du vocabulaire entre parenthèses : `(EU)` pour les vocabulaires de la commission européenne, `(INSPIRE)` pour les vocabulaires du registre INSPIRE, `(OGC)` pour les vocabulaires de l'OGC, etc.

    Exemple : 
    ```turtle
    @prefix skos: <http://www.w3.org/2004/02/skos/core#> .  

    <http://publications.europa.eu/resource/authority/licence> a skos:ConceptScheme ;
        skos:prefLabel "Licence (EU)"@en,
            "Licences (UE)"@fr .
    ```

    Optionnellement, un vocabulaire peut avoir une page web associée, spécifiée par la propriété `foaf:page`. Cette page doit contenir des informations non techniques permettant aux utilisateurs de comprendre comment bien utiliser le vocabulaire.

    Dans l'exemple qui suit, la page correspond à l'article du code des relations entre le public et l'administration qui liste les licences autorisées pour les administrations :
    ```turtle
    @prefix foaf: <http://xmlns.com/foaf/0.1/> .
    @prefix plume: <http://registre.data.developpement-durable.gouv.fr/plume/> .
    @prefix skos: <http://www.w3.org/2004/02/skos/core#> .  

    plume:CrpaAccessLimitations a skos:ConceptScheme ;
        skos:prefLabel "Limitations of public access according to French Code des relations entre le public et l'administration"@en,
            "Restrictions d'accès en application du Code des relations entre le public et l'administration"@fr ;
        foaf:page <https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000031366350/LEGISCTA000031367696> .
    ```
    Lorsque le vocabulaire est importé intégralement depuis un registre tiers, l'URI de l'ensemble de concepts est celui du registre d'origine. Pour les vocabulaires créés spécialement pour Plume, y compris lorsqu'il s'agit d'extraits de vocabulaires plus larges, il est possible de définir un URI dans l'espace de nommage de Plume, `http://registre.data.developpement-durable.gouv.fr/plume/` (prefixe `plume`), avec un identifiant explicite en notation [*camel case*](https://fr.wikipedia.org/wiki/Camel_case). C'est ce qui a été fait dans l'exemple ci-avant.

- Un objet `skos:Concept` (concept) pour chaque terme du vocabulaire. Il doit obligatoirement avoir :
    - Une propriété `skos:inScheme` dont l'objet est l'ensemble de concepts susmentionné.
    - Une propriété `skos:prefLabel` fournissant un libellé, de préférence en français.

    Exemple :

    ```turtle
    <https://spdx.org/licenses/etalab-2.0> a skos:Concept ;
        skos:inScheme <http://registre.data.developpement-durable.gouv.fr/plume/SpdxLicense> ;
        skos:prefLabel "etalab-2.0 : Etalab Open License 2.0"@en,
            "Licence Ouverte version 2.0"@fr .
    ```

    Optionnellement, il est possible de fournir des traductions du libellé dans d'autres langues, toujours avec `skos:prefLabel`. Il est également souhaitable, dans la mesure du possible, d'associer une page web au terme de vocabulaire avec la propriété `foaf:page`. Ces pages servent à générer les hyperliens qui apparaissent dans les fiches de métadonnées en mode lecture. À défaut, c'est l'URI qui est utilisé.

    Lorsqu'il existe déjà un URI pour le terme de vocabulaire, celui-ci doit autant que possible être conservé. Les ensembles de concepts définis dans l'espace de nommage de Plume ont vocation à être publié sur le registre de Plume, ce qui implique de créer pour chaque concept un URI dans l'espace de nommage de Plume. D'une manière générale, cela est fait automatiquement en juxtaposant l'URI de l'ensemble de concepts et le dernier élément de l'URI originelle du concept.

    Par exemple, l'alias du concept `<http://www.opengis.net/def/serviceType/ogc/wms>` dans le registre de Plume est `<http://registre.data.developpement-durable.gouv.fr/plume/DataServiceStandard>` + `wms`, soit `<http://registre.data.developpement-durable.gouv.fr/plume/DataServiceStandard\wms>`.

    Lorsque le dernier élément de l'URI originelle n'est pas adapté pour cet usage, il est possible de forcer l'utilisation d'un autre identifiant via la propriété `dct:identifier`.

    Exemple :

    ```turtle
    @prefix dct: <http://purl.org/dc/terms/> ..
    @prefix skos: <http://www.w3.org/2004/02/skos/core#> .

    <http://tools.ietf.org/html/rfc4287> a skos:Concept ;
        dct:identifier "atom" ;
        skos:inScheme plume:DataServiceStandard ;
        skos:prefLabel "ATOM Syndication Format"@en .
    ```

### Déclaration du vocabulaire

Les fichiers contenant les vocabulaires doivent être placés dans le répertoire {file}`/plume/rdf/data/vocabularies`. Autant que possible, leur nom doit correspondre à celui de l'ensemble de concepts qu'ils définissent, écrit en minuscules avec des tirets bas comme séparateurs. Par exemple, le fichier contenant le vocabulaire `<http://registre.data.developpement-durable.gouv.fr/plume/ISO19139ProgressCode>` est nommé `iso_19139_progress_code.ttl`.

Une fois le vocabulaire placé dans le bon répertoire, l'URI de l'ensemble de concepts doit être déclaré à deux endroits : 
* Dans le dictionnaire {py:data}`plume.rdf.thesaurus.VOCABULARIES`, qui fait la correspondance entre l'URI de l'ensemble de concepts et le nom du fichier qui contient ses termes.
* Dans le schéma des métadonnées communes, {file}`/plume/rdf/data/shape.ttl`. Pour indiquer qu'une catégorie de métadonnées - nécessairement de nature `sh:BlankNodeOrIRI` ou `sh:IRI` - prend ses valeurs dans un ou plusieurs vocabulaires, on déclarera les URI de ces derniers comme objets de la propriété `plume:ontology`.
    
    Exemple :

    ```turtle
    @prefix adms: <http://www.w3.org/ns/adms#> .
    @prefix plume: <http://registre.data.developpement-durable.gouv.fr/plume/> .
    @prefix sh: <http://www.w3.org/ns/shacl#> .
    @prefix skos: <http://www.w3.org/2004/02/skos/core#> .

    sh:property [
        sh:path adms:status ;
        sh:nodeKind sh:IRI ;
        sh:class skos:Concept ;
        plume:ontology <http://publications.europa.eu/resource/authority/dataset-status>,
            <http://registre.data.developpement-durable.gouv.fr/plume/ISO19139ProgressCode> ;
    ] ;
    ```

À noter que l'un des tests de la recette de Plume a pour objet de vérifier que tout vocabulaire qui apparaît dans le schéma des métadonnées communes est aussi dans {py:data}`plume.rdf.thesaurus.VOCABULARIES` et réciproquement. L'existence du fichier est également contrôlée.

Les modifications apportées au schéma des métadonnées communes doivent ensuite être répercutées dans d'autres sections du code. Cf. [Modifier les catégories de métadonnées communes](#modifier-les-catégories-de-métadonnées-communes).

### Mise à jour du registre

Les vocabulaires de Plume - en pratique, tout vocabulaire dont l'URI de l'ensemble de concepts est défini dans l'espace de nommage de Plume - doivent ensuite être copiés sur le registre de Plume, afin de permettre la résolution de leurs URI sur internet. C'est l'objet du module {py:mod}`admin.register`.

