# Génération du dictionnaire des widgets

Foncièrement, lorsqu'un utilisateur demande l'affichage de la fiche de métadonnées d'une table ou vue, le plugin :
1. rassemble dans un "dictionnaire de widgets", soit un objet python de classe `WidgetsDict`, des informations issues de toutes sortes de sources, incluant évidemment les métadonnées de la table stockées dans son descriptif PostgreSQL ;
2. parcourt ce dictionnaire de widgets pour construire le formulaire qui sera présenté à l'utilisateur. 

La première de ces étapes, objet de la présente partie, est réalisée par la fonction `build_dict` de [rdf_utils.py](/metadata_postgresql/bibli_rdf/rdf_utils.py).

Celle-ci prend deux types d'arguments : des sources de données et des paramètres utilisateur.

Sources de données :

| Position | Nom | Type | Obligatoire ? | Valeur par défaut | Détails |
| --- | --- | --- | --- | --- | --- |
| 0 | `metagraph` | rdflib.graph.Graph | oui |  | [→](#metagraph--le-graphe-des-métadonnées-pré-existantes) |
| 1 | `shape` | rdflib.graph.Graph | oui |  | [→](#shape--le-schéma-shacl-des-métadonnées-communes) |
| 2 | `vocabulary` | rdflib.graph.Graph | oui |  | [→](#vocabulary--la-compilation-des-thésaurus) |
| 3 | `template` | dict | non | `None` | [→](#template--le-modèle-de-formulaire) |
| 4 | `templateTabs` | dict | non | `None` | [→](#templateTabs--la-liste-des-onglets) |
| 5 | `data` | dict | non | `None` | [→](#data--les-métadonnées-calculées) |

Paramètres utilisateurs :

| Position | Nom | Type | Obligatoire ? | Valeur par défaut | Détails |
| --- | --- | --- | --- | --- | --- |
| 6 | `mode` | str | non | `'edit'` | [→](#mode) |
| 7 | `readHideBlank` | bool | non | `True` | [→](#readhideblank) |
| 8 | `hideUnlisted` | bool | non | `False` | [→](#hideunlisted) |
| 9 | `language` | str | non | `'fr'` | [→](#language) |
| 10 | `translation` | bool | non | `False` | [→](#translation) |
| 11 | `langList` | list (str) | non | `['fr', 'en']` | [→](#langlist) |
| 12 | `readOnlyCurrentLanguage` | bool | non | `True` | [→](#readonlycurrentlanguage) |
| 13 | `editOnlyCurrentLanguage` | bool | non | `False` | [→](#editonlycurrentlanguage) |
| 14 | `labelLengthLimit` | int | non | `25` | [→](#labellengthlimit) |
| 15 | `valueLengthLimit` | int | non | `100` | [→](#valuelengthlimit) |
| 16 | `textEditRowSpan` | int | non | `6` | [→](#texteditrowspan) |

Tous les arguments sont décrits plus en détail dans la suite, ainsi que le résultat obtenu.

Afin que les valeurs par défaut s'appliquent, on fournira de préférence à `build_dict()` ses arguments sous la forme d'un dictionnaire ne contenant que les arguments pour lesquels une valeur est effectivement disponible.

Par exemple :

```python

kwa = {}

# ajout des arguments obligatoires
kwa.update({
	'metagraph': metagraph,
	'shape': shape,
	'vocabulary': vocabulary 
	})
	
# ajout des arguments optionnels
if template is not None:
	kwa.update({ 'template': template })
if data is not None:
	kwa.update({ 'data': data })
if mode is not None:
	kwa.update({ 'mode': mode })
# etc.

widgetsdict = rdf_utils.build_dict(**kwa)

```

## Sources de données

### metagraph : le graphe des métadonnées pré-existantes

Les métadonnées pré-existantes sont déduites du descriptif PostgreSQL de la table ou de la vue, ci-après `old_description`.

Cette information est a priori déjà disponible par l'intermédiaire des classes de QGIS. Néanmoins, si nécessaire, [pg_queries.py](/metadata_postgresql/bibli_pg/pg_queries.py) propose une requête pré-configurée `query_get_table_comment()`, qui peut être utilisée comme suit :

```python

import psycopg2
conn = psycopg2.connect(connection_string)

with conn:
    with conn.cursor() as cur:
    
        query = pg_queries.query_get_table_comment(schema_name, table_name)
        cur.execute(query)
        old_description = cur.fetchone()[0]

conn.close()

```

*`connection_string` est la chaîne de connexion à la base de données PostgreSQL.*

Une fois le descriptif récupéré, la fonction `metagraph_from_pg_description()` de [rdf_utils.py](/metadata_postgresql/bibli_rdf/rdf_utils/rdf_utils.py) permet d'en extraire les métadonnées et les dé-sérialiser en graphe RDF.

```python

metagraph = rdf_utils.metagraph_from_pg_description(old_description, shape)

```

*`shape` est le schéma SHACL des métadonnées communes, également argument de `build_dict()` et décrit juste après.*

La fonction `metagraph_from_pg_description()` renverra un graphe vide si le descriptif PostgreSQL ne contenait pas les balises `<METADATA>` et `</METADATA>` entre lesquelles est supposé se trouver le JSON-LD contenant les métadonnées. C'est typiquement ce qui arrivera lorsque les métadonnées n'ont pas encore été rédigées.

Si les balises sont présentes, mais ne contiennent pas un JSON valide, la fonction échouera sur une erreur `json.decoder.JSONDecodeError`. Dans ce cas, on pourra proposer à l'utilisateur de choisir entre abandonner l'ouverture de la fiche de métadonnées ou ouvrir une fiche vierge à la place.

```python

try:

	metagraph = rdf_utils.metagraph_from_pg_description(old_description, shape)
	
except:

	# dialogue avec l'utilisateur
	...
	
	# si l'exécution n'est pas interrompue :
	metagraph = rdf_utils.metagraph_from_pg_description("", shape)

```

### shape : le schéma SHACL des métadonnées communes

`shape` fournit les caractéristiques des métadonnées communes et, surtout, les informations sur la manière dont elles se structurent entre elles.

C'est un schéma SHACL "augmenté", qui ajoute quelques propriétés au standard (celles dont l'espace de nommage est `snum`) afin de spécifier la manière dont les catégories doivent être représentées dans le formulaire. 

En pratique, il s'agit du fichier [shape.ttl](/metadata_postgresql/bibli_rdf/rdf_utils/modeles/shape.ttl), à importer avec la fonction `load_shape()` de [rdf_utils.py](/metadata_postgresql/bibli_rdf/rdf_utils/rdf_utils.py).

```python

shape = rdf_utils.load_shape()

```

### vocabulary : la compilation des thésaurus

`vocabulary` est un graphe RDF où sont compilés les termes de tous les thésaurus dont `shape` prévoit l'utilisation.

Concrètement, il s'agit du fichier [vocabulary.ttl](/metadata_postgresql/bibli_rdf/rdf_utils/modeles/vocabulary.ttl), à importer avec la fonction `load_vocabulary()` de [rdf_utils.py](/metadata_postgresql/bibli_rdf/rdf_utils/rdf_utils.py).

```python

shape = rdf_utils.load_vocabulary()

```

### template : le modèle de formulaire

`template` est un dictionnaire contenant les informations relatives au modèle de formulaire à utiliser.

Les modèles de formulaires sont définis à l'échelle du service et stockés dans la base PostgreSQL. Ils permettent :
- d'ajouter des métadonnées locales aux catégories communes définies dans `shape` ;
- de restreindre les catégories communes à afficher ;
- de substituer des paramètres locaux à ceux spécifiés par `shape` (par exemple remplacer le nom à afficher pour la catégorie de métadonnée ou changer le type de widget à utiliser).

La forme de `template` est proche de celle d'un dictionnaire de widgets, si ce n'est que ses clés sont des chemins SPARQL identifiant des catégories de métadonnées et ses contiennent moins de clés.

Pour plus de détails sur les modèles de formulaire, on se reportera à la partie [Modèles de formulaire](/__doc__/08_modeles_de_formulaire.md), et plus particulièrement à sa sous-partie [Import par le plugin](/__doc__/08_modeles_de_formulaire.md#import-par-le-plugin), qui explique comment générer `template`.


### templateTabs : le liste des onglets

`templateTabs` est un dictionnaire qui répertorie les onglets utilisés par le modèle de formulaire. Il peut valoir `None` en l'absence de modèle ou si le modèle ne répartit pas les catégories dans des onglets.

S'il existe, sa structure est très simple : les clés sont les noms des modèles, les valeurs sont les futures clés correspondantes dans le dictionnaire de widgets.

Par exemple :

```python
{
    "Onglet n°1": (0,),
    "Onglet n°2": (1,),
    "Onglet n°3": (2,)
}
```

Pour plus de détails sur les modèles de formulaire, on se reportera à la partie [Modèles de formulaire](/__doc__/08_modeles_de_formulaire.md), et plus particulièrement à sa sous-partie [Import par le plugin](/__doc__/08_modeles_de_formulaire.md#import-par-le-plugin), qui explique comment générer `templateTabs`.


### data : les métadonnées calculées

`data` est un dictionnaire contenant des informations actualisées à partir de sources externes (par exemple déduites des données) qui écraseront les valeurs présentes dans `metagraph`. Les clés du dictionnaire sont des chemins SPARQL identifiant des catégories de métadonnées, ses valeurs sont des listes contenant la ou les valeurs (str) à faire apparaître pour les catégories en question.

À ce stade, `data` est implémenté dans `build_dict()`, mais aucun mécanisme n'a été mis en place pour le constituer.

On se contentera donc pour l'heure de :

```python

data = None

```

## Paramètres utilisateur

### mode

`mode` est un paramètre utilisateur au sens où il est déterminé par l'utilisateur, mais il n'est pas sauvegardé dans les fichiers INI.

Comme détaillé dans [Actions générales](/__doc__/16_actions_generales.md#mode-lecture-mode-edition), il doit toujours valoir `'read'` (mode lecture) lors de l'ouverture initiale de la fiche. Si ses privilèges sont suffisants, 'utilisateur peut ensuite activer le mode édition, et `mode` vaudra alors `'edit'`.

### readHideBlank

### hideUnlisted

### language

### translation

### langList

### readOnlyCurrentLanguage

### editOnlyCurrentLanguage

### labelLengthLimit

### valueLengthLimit

### textEditRowSpan

## Résultat : un dictionnaire de widgets



