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
| 5 | `columns` | list | non | `None` | [→](#columns--les-descriptifs-des-champs) |
| 6 | `data` | dict | non | `None` | [→](#data--les-métadonnées-calculées) |

Paramètres utilisateurs :

| Position | Nom | Type | Obligatoire ? | Valeur par défaut | Détails |
| --- | --- | --- | --- | --- | --- |
| 7 | `mode` | str | non | `'edit'` | [→](#mode) |
| 8 | `readHideBlank` | bool | non | `True` | [→](#readhideblank) |
| 9 | `readHideUnlisted` | bool | non | `True` | [→](#readHideunlisted) |
| 10 | `editHideUnlisted` | bool | non | `False` | [→](#editHideunlisted) |
| 11 | `language` | str | non | `'fr'` | [→](#language) |
| 12 | `translation` | bool | non | `False` | [→](#translation) |
| 13 | `langList` | list (str) | non | `['fr', 'en']` | [→](#langlist) |
| 14 | `readOnlyCurrentLanguage` | bool | non | `True` | [→](#readonlycurrentlanguage) |
| 15 | `editOnlyCurrentLanguage` | bool | non | `False` | [→](#editonlycurrentlanguage) |
| 16 | `labelLengthLimit` | int | non | `25` | [→](#labellengthlimit) |
| 17 | `valueLengthLimit` | int | non | `65` | [→](#valuelengthlimit) |
| 18 | `textEditRowSpan` | int | non | `6` | [→](#texteditrowspan) |

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

**Quoi qu'il arrive, les arguments optionnels doivent impérativement être nommés.** Leurs positions sont susceptibles d'être modifiées si de nouveaux arguments sont ajoutés à la fonction.

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


### templateTabs : la liste des onglets

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


### columns : les descriptifs des champs

`columns` est la liste des champs de la table / vue courante. Plus précisément, il s'agit d'une liste de tuples dont le premier élément est le nom du champ et le second son descriptif.

Elle peut être obtenue ainsi :

```python

import psycopg2
conn = psycopg2.connect(connection_string)

with conn:
    with conn.cursor() as cur:
    
        query = pg_queries.query_get_columns(schema_name, table_name)
        cur.execute(query)
        columns = cur.fetchall()

conn.close()

```

Dans le formulaire résultant, chaque champ se trouvera représenté par un QTextEdit placé dans l'onglet *Champs*.


### data : les métadonnées calculées

`data` est un dictionnaire contenant des informations actualisées à partir de sources externes (par exemple déduites des données) qui écraseront les valeurs présentes dans `metagraph`. Les clés du dictionnaire sont des chemins SPARQL identifiant des catégories de métadonnées, ses valeurs sont des listes contenant la ou les valeurs (str) à faire apparaître pour les catégories en question.

À ce stade, `data` est implémenté dans `build_dict()`, mais aucun mécanisme n'a été mis en place pour le constituer.

On se contentera donc pour l'heure de :

```python

data = None

```

## Paramètres utilisateur

Sauf indication contraire, tous les paramètres utilisateur évoqués ci-après sont à récupérer dans les fichiers de configuration. Si un paramètre n'y est pas explicitement spécifié (parce que l'utilisateur n'a pas éprouvé le besoin de modifier le comportement par défaut), il ne devra pas non plus apparaître dans les arguments de `build_dict()`.

### mode

`mode` est un paramètre utilisateur au sens où il est déterminé par l'utilisateur, mais **il ne doit pas être sauvegardé dans le fichier de configuration**.

Comme détaillé dans [Actions générales](/__doc__/16_actions_generales.md#mode-lecture-mode-edition), il devra toujours valoir `'read'` (mode lecture) lors de l'ouverture initiale de la fiche. Si ses privilèges sont suffisants, l'utilisateur peut ensuite activer le mode édition, et `mode` vaudra alors `'edit'`.

Il est préférable de toujours spécifier explicitement ce paramètre dans la liste des arguments de `build_dict()` (où sa valeur par défaut est `'edit'`).

### readHideBlank

`readHideBlank` est un booléen indiquant si les champs vides doivent être masqués en mode lecture.

Le comportement naturel est de masquer ces champs, et c'est ce que fera `build_dict()` si ce paramètre n'est pas spécifié.

### readHideUnlisted

`readHideUnlisted` est un booléen indiquant si, en mode lecture, il faut masquer les catégories qui n'apparaissent pas dans le modèle de formulaire à utiliser (cf. [template](#template--le-modèle-de-formulaire)) mais pour lesquelles des métadonnées ont été saisies antérieurement. Si aucun modèle n'est défini, les catégories concernées sont celles qui ne sont pas répertoriées dans le schéma des catégories communes.

Le comportement par défaut de `build_dict()` est de masquer les champs en question.

### editHideUnlisted

`editHideUnlisted` est le pendant de `readHideUnlisted` pour le mode édition.

C'est un booléen indiquant si, en mode édition, il faut masquer les catégories qui n'apparaissent pas dans le modèle de formulaire à utiliser (cf. [template](#template--le-modèle-de-formulaire)) mais pour lesquelles des métadonnées ont été saisies antérieurement. Si aucun modèle n'est défini, les catégories concernées sont celles qui ne sont pas répertoriées dans le schéma des catégories communes.

Le comportement par défaut de `build_dict()` est d'afficher les champs en question.

### language

`language` est une chaîne de caractères indiquant la langue principale de saisie des métadonnées. Ce paramètre peut être modifié via un widget dans l'interface fixe du plugin - cf. [Actions générales](/__doc__/16_actions_generales.md#langue-principale-des-métadonnées).

Si `language` n'apparaît pas dans les arguments de `build_dict()`, il sera considéré que les métadonnées sont saisies en français, `'fr'`. Nonobstant, il est recommandé de toujours spécifier explicitement ce paramètre, afin d'assurer que la valeur utilisée par la fonction soit identique à celle qui apparaît dans la partie fixe de l'interface.

### translation

`translation` est un booléen indiquant si le mode traduction est actif. Comme `language`, ce paramètre peut être modifié via un widget dans l'interface fixe du plugin - cf. [Actions générales](/__doc__/16_actions_generales.md#activation-du-mode-traduction).

Si `translation` n'apparaît pas dans les arguments de `build_dict()`, il sera considéré que le mode traduction n'est pas actif. Nonobstant, il est recommandé de toujours spécifier explicitement ce paramètre, afin d'assurer que la valeur utilisée par la fonction soit identique à celle qui apparaît dans la partie fixe de l'interface.

### langList

`langList` est une liste de chaînes de caractères qui donne les langues autorisées pour les traductions. Elle alimente aussi la liste de valeur du widget qui, dans la partie fixe de l'interface, permet de choisir la langue principale [Actions générales](/__doc__/16_actions_generales.md#langue-principale-des-métadonnées).

Si `langList` n'apparaît pas dans les arguments de `build_dict()`, celle-ci utilisera la liste `['fr', 'en']` (français et anglais). Nonobstant, il est recommandé de toujours spécifier explicitement ce paramètre, afin d'assurer que la valeur utilisée par la fonction soit identique à celle qui apparaît dans la partie fixe de l'interface.

### readOnlyCurrentLanguage

`readOnlyCurrentLanguage` est un booléen qui indique si, en mode lecture, seules les métadonnées saisies dans la langue principale (cf. [language](#language)) doivent être affichées. À noter que si aucune traduction n'est disponible dans la langue demandée, les valeurs d'une langue arbitraire seront alors affichées.

Si `readOnlyCurrentLanguage` n'apparaît pas dans les arguments de `build_dict()`, il sera considéré comme valant `True`.

### editOnlyCurrentLanguage

`editOnlyCurrentLanguage` est le pendant de `readOnlyCurrentLanguage` pour le mode édition.

C'est un booléen indiquant si, en mode édition **et lorsque le mode traduction n'est pas actif**, seules les métadonnées saisies dans la langue principale (cf. [language](#language)) doivent être affichées. À noter que si aucune traduction n'est disponible dans la langue demandée, les valeurs d'une langue arbitraire seront alors affichées.

Si `editdOnlyCurrentLanguage` n'apparaît pas dans les arguments de `build_dict()`, il sera considéré comme valant `False`.

### labelLengthLimit

`labelLengthLimit` est un entier qui indique le nombre de caractères au-delà duquel l'étiquette d'une catégorie de métadonnées sera toujours affiché au-dessus du widget de saisie et non sur la même ligne. À noter que pour les widgets QTextEdit le label est placé au-dessus quoi qu'il arrive.

Si `labelLengthLimit` n'apparaît pas dans les arguments de `build_dict()`, le seuil est fixé à 25 caractères.

### valueLengthLimit

`valueLengthLimit` est un entier qui indique le nombre de caractères au-delà duquel une valeur qui aurait dû être affichée dans un widget QLineEdit sera présentée à la place dans un QTextEdit. Indépendemment du nombre de caractères, la substitution sera aussi réalisée si la valeur contient un retour à la ligne.

Si `valueLengthLimit` n'apparaît pas dans les arguments de `build_dict()`, le seuil est fixé à 65 caractères.

### textEditRowSpan

`textEditRowSpan` est un entier qui définit le nombre de lignes par défaut d'un widget QTextEdit, c'est-à-dire la valeur qui sera utilisée par `build_dict()` pour toutes les catégories telles que ni le modèle de formulaire ni le schéma des catégories communes ne fixe une valeur.

Si `textEditRowSpan` n'apparaît pas dans les arguments de `build_dict()`, la hauteur est fixée à 6 lignes.



## Résultat : un dictionnaire de widgets

La fonction `build_dict()` renvoie un dictionnaire de widgets, soit un objet de classe `WidgetsDict`. Cette classe hérite de `dict` et définit des méthodes supplémentaires qui gèrent notamment l'actualisation du dictionnaire en fonction des actions de l'utilisateur (cf. [Actions contrôlées par les widgets du formulaire](/__doc__/15_actions_widgets.md)).

En premier lieu, le dictionnaire de widgets sert de base à la génération du formulaire de saisie / consultation des métadonnées. Pour ce faire, on bouclera sur les clés du dictionnaire et créera au fur et à mesure les widgets qu'elles définissent, comme expliqué dans [Création d'un nouveau widget](/__doc__/10_creation_widgets.md).

```python

{
    key1 : dictionnaire_interne_key1,
    key2 : dictionnaire_interne_key2
}

```

Chaque enregistrement du dictionnaire représente l'un objets des objets suivants du formulaire : une zone de saisie, un groupe de valeurs, un groupe de propriétés, un groupe de traduction, un bouton plus ou un bouton de traduction.

Les clés sont des tuples, ou plus précisément des tuples imbriqués dans des tuples. En plus d'identifier chaque objet, elles définissent son positionnement dans la structure arborescente du formulaire.

Exemple : `(0, (0, (0,)))` est la clé du premier objet de parent `(0, (0,))`.

Les dictionnaires internes sont eux-mêmes des dictionnaires, tous de structure identiques. Ils contiennent toutes les informations nécessaires à la création du ou des widgets associés à l'objet et seront également utilisés pour référencer chacun des widgets créés.



