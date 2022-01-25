# Génération du dictionnaire des widgets

Foncièrement, lorsqu'un utilisateur demande l'affichage de la fiche de métadonnées d'une table ou vue, le plugin :
1. rassemble dans un "dictionnaire de widgets", soit un objet python de classe `WidgetsDict`, des informations issues de toutes sortes de sources, incluant évidemment les métadonnées de la table stockées dans son descriptif PostgreSQL ;
2. parcourt ce dictionnaire de widgets pour construire le formulaire qui sera présenté à l'utilisateur. 

La première de ces étapes est traitée ici. Pour la seconde, cf. [Création d'un nouveau widget](/__doc__/10_creation_widgets.md).

La classe `WidgetsDict` est définie par le module [plume.rdf.widgetsdict](/plume/rdf/widgetsdict.py). Sa fonction d'initialisation prend deux types d'arguments : des sources de données et des paramètres utilisateur. Aucun n'est obligatoire.

Sources de données :

| Nom | Type | Valeur par défaut | Détails |
| --- | --- | --- | --- |
| `metagraph` | [`plume.rdf.metagraph.Metagraph`](/plume/rdf/metagraph.py) | `None` | [→](#metagraph--le-graphe-des-métadonnées-pré-existantes) |
| `template` | [`plume.pg.template.TemplateDict`](/plume/pg/template.py) | `None` | [→](#template--le-modèle-de-formulaire) |
| `data` | `dict` | `None` | [→](#data--les-métadonnées-calculées) |
| `columns` | `list(tuple(str, str))` | `None` | [→](#columns--les-descriptifs-des-champs) |

Paramètres utilisateurs :

| Nom | Type | Valeur par défaut | Détails |
| --- | --- | --- | --- |
| `mode` | `str` | `'edit'` | [→](#mode) |
| `translation` | `bool` | `False` | [→](#translation) |
| `langList` | `list(str)` ou `tuple(str)` | `('fr', 'en')` | [→](#langlist) |
| `language` | `str` | `'fr'` | [→](#language) |
| `readHideBlank` | `bool` | `True` | [→](#readhideblank) |
| `editHideUnlisted` | `bool` | `False` | [→](#editHideunlisted) |
| `readHideUnlisted` | `bool` | `True` | [→](#readHideunlisted) |
| `editOnlyCurrentLanguage` | `bool` | `False` | [→](#editonlycurrentlanguage) |
| `readOnlyCurrentLanguage` | `bool` | `True` | [→](#readonlycurrentlanguage) |
| `labelLengthLimit` | `int` | `25` | [→](#labellengthlimit) |
| `valueLengthLimit` | `int` | `65` | [→](#valuelengthlimit) |
| `textEditRowSpan` | `int` | `6` | [→](#texteditrowspan) |

Tous les arguments sont décrits plus en détail dans la suite, ainsi que le résultat obtenu.

Afin que les valeurs par défaut s'appliquent correctement, on fournira de préférence à `WidgetsDict()` ses arguments sous la forme d'un dictionnaire ne contenant que les arguments pour lesquels une valeur est effectivement disponible[^defaultvalues].

[^defaultvalues]: Ce sujet concerne surtout les paramètres booléens. Pour les autres, les valeurs par défaut sont appliquées dans le corps de la fonction d'initialisation et non déclarées dans les paramètres. Ainsi, elles s'appliqueront aussi dans le cas où une valeur `None` est explicitement fournie en argument.

Par exemple :

```python

from plume.rdf.widgetsdict import WidgetsDict

kwa = {}

if metagraph is not None:
    kwa['metagraph'] = metagraph
if template is not None:
    kwa['template'] = template
# etc.

widgetsdict = WidgetsDict(**kwa)

```

## Sources de données

### metagraph : le graphe des métadonnées pré-existantes

Les métadonnées pré-existantes sont déduites du descriptif PostgreSQL de la table ou de la vue, ci-après `old_description_raw`. Elles sont supposées se trouver entre deux balises `<METADATA>` et `</METADATA>`, et avoir été encodées au format JSON-LD.

Le module [plume.pg.queries](/plume/pg/queries.py) propose une requête pré-configurée `query_get_table_comment()`, qui permet d'obtenir le descriptif de l'objet :

```python

import psycopg2
from plume.pg import queries

conn = psycopg2.connect(connection_string)

with conn:
    with conn.cursor() as cur:
    
        query = queries.query_get_table_comment(schema_name, table_name)
        cur.execute(query)
        raw_old_description = cur.fetchone()[0]

conn.close()

```

*`connection_string` est la chaîne de connexion à la base de données PostgreSQL.*

Une fois le descriptif récupéré, on l'utilisera pour générer un objet de classe  [`plume.pg.description.PgDescription`](/plume/pg/description.py), ce qui a pour effet d'en extraire les métadonnées - s'il y en avait - et les dé-sérialiser en graphe de métadonnées.

```python

from plume.pg.description import PgDescription

old_description = PgDescription(raw_old_description)

```

Le graphe de métadonnées, objet de classe [`plume.rdf.metagraph.Metagraph`](/plume/rdf/metagraph.py), peut être obtenu par un appel à la propriété `metagraph` de `old_description`.


```python

metagraph = old_description.metagraph
```

La propriété renverra un graphe vide si le descriptif PostgreSQL ne contenait pas les balises `<METADATA>` et `</METADATA>` entre lesquelles est supposé se trouver le JSON-LD contenant les métadonnées. C'est typiquement ce qui arrivera lorsque les métadonnées n'ont pas encore été rédigées.

Si le contenu des balises n'est pas un JSON-LD valide, la propriété renverra également un graphe de métadonnées vide.

### template : le modèle de formulaire

`template` est un objet de classe [`plume.pg.template.TemplateDict`](/plume/pg/template.py) contenant les informations relatives au modèle de formulaire à utiliser.

Les modèles de formulaires sont définis à l'échelle du service et stockés dans la base PostgreSQL. Ils permettent :
- d'ajouter des catégories locales au schéma de métadonnées communes ;
- de restreindre les catégories communes à afficher ;
- de substituer des paramètres locaux à ceux spécifiés par le schéma commun (par exemple remplacer le nom à afficher pour la catégorie de métadonnée, répartir les métadonnées dans plusieurs onglets...).

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

À ce stade, `data` est uniquement utilisé pour mettre en cohérence l'identifiant du jeu de données avec celui qui est contenu dans le petit JSON de GéoIDE.

On se contentera donc pour l'heure de :

```python

geoide_id = rdf_utils.get_geoide_json_uuid(old_description)
data = { 'dct:identifier': [geoide_id] } if geoide_id else None

```

*`old_description` est le descriptif PostgreSQL de la table ou vue, [préalablement récupéré](#metagraph--le-graphe-des-métadonnées-pré-existantes) pour générer `metagraph`.*


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



