# Génération du dictionnaire des widgets

 [metagraph : le graphe des métadonnées pré-existantes](#metagraph--le-graphe-des-métadonnées-pré-existantes) • [template : le modèle de formulaire](#template--le-modèle-de-formulaire) • [columns : les descriptifs des champs](#columns--les-descriptifs-des-champs) • [data : les métadonnées calculées](#data--les-métadonnées-calculées) • [mode](#mode) • [translation](#translation) • [langList](#langlist) • [language](#language) • [readHideBlank](#readhideblank) • [editHideUnlisted](#edithideunlisted) • [readHideUnlisted](#readhideunlisted) • [editOnlyCurrentLanguage](#editonlycurrentlanguage) • [readOnlyCurrentLanguage](#readonlycurrentlanguage) • [labelLengthLimit](#labellengthlimit) • [valueLengthLimit](#valuelengthlimit) • [textEditRowSpan](#texteditrowspan) • [Résultat : un dictionnaire de widgets](#résultat--un-dictionnaire-de-widgets)

Lorsqu'un utilisateur demande l'affichage de la fiche de métadonnées d'une table ou vue, le plugin :
1. rassemble dans un "dictionnaire de widgets", c'est-à-dire un objet de classe `WidgetsDict`, des informations issues de toutes sortes de sources, incluant évidemment les métadonnées de la table stockées dans son descriptif PostgreSQL ;
2. parcourt ce dictionnaire de widgets pour construire le formulaire qui sera présenté à l'utilisateur. 

La première de ces étapes est traitée ici. Pour la seconde, cf. [Création d'un nouveau widget](/docs/source/usage/creation_widgets.md).

La classe `WidgetsDict` est définie par le module [plume.rdf.widgetsdict](/plume/rdf/widgetsdict.py). Sa fonction d'initialisation prend deux types d'arguments : des sources de données et des paramètres utilisateur. Aucun n'est obligatoire.

Sources de données :

| Nom | Type | Valeur par défaut | Détails |
| --- | --- | --- | --- |
| `metagraph` | [`plume.rdf.metagraph.Metagraph`](/plume/rdf/metagraph.py) | `None` | [→ graphe des métadonnées](#metagraph--le-graphe-des-métadonnées-pré-existantes) |
| `template` | [`plume.pg.template.TemplateDict`](/plume/pg/template.py) | `None` | [→ modèle de formulaire](#template--le-modèle-de-formulaire) |
| `data` | `dict` | `None` | [→ métadonnées calculées](#data--les-métadonnées-calculées) |
| `columns` | `list(tuple(str, str))` | `None` | [→ descriptifs des champs](#columns--les-descriptifs-des-champs) |

Paramètres utilisateurs :

| Nom | Type | Valeur par défaut | Détails |
| --- | --- | --- | --- |
| `mode` | `str` | `'edit'` | [→](#mode) |
| `translation` | `bool` | `False` | [→](#translation) |
| `langList` | `list(str)` ou `tuple(str)` | `('fr', 'en')` | [→](#langlist) |
| `language` | `str` | `'fr'` | [→](#language) |
| `readHideBlank` | `bool` | `True` | [→](#readhideblank) |
| `editHideUnlisted` | `bool` | `False` | [→](#edithideunlisted) |
| `readHideUnlisted` | `bool` | `True` | [→](#readhideunlisted) |
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

*`connection_string` est la chaîne de connexion à la base de données PostgreSQL. `table_name` et `schema_name` sont respectivement le nom de la relation (table, vue, etc.) dont on souhaite importer les métadonnées et le nom du schéma auquel elle est rattachée.*

Une fois le descriptif récupéré, on l'utilisera pour générer un objet de classe  [`plume.pg.description.PgDescription`](/plume/pg/description.py), ce qui a pour effet d'en extraire les métadonnées - s'il y en avait - et les dé-sérialiser en graphe de métadonnées.

```python

from plume.pg.description import PgDescription

old_description = PgDescription(raw_old_description)

```

Ce même objet `PgDescription` servira ultérieurement pour la création d'un nouveau descriptif PostgreSQL contenant les métadonnées mises à jour. Il mémorise en effet également le texte saisi hors des balises `<METADATA>`, qu'il s'agit de préserver. Cf. [Sauvegarde](/docs/source/usage/actions_generales.md#sauvegarde) pour plus de détails.

Le graphe de métadonnées, objet de classe [`plume.rdf.metagraph.Metagraph`](/plume/rdf/metagraph.py), est ensuite obtenu par un simple appel à la propriété `metagraph` de `old_description`.


```python

metagraph = old_description.metagraph
```

La propriété renverra un graphe vide si le descriptif PostgreSQL ne contenait pas les balises `<METADATA>` et `</METADATA>` entre lesquelles est supposé se trouver le JSON-LD contenant les métadonnées. C'est typiquement ce qui arrivera lorsque les métadonnées n'ont pas encore été rédigées.

Si le contenu des balises n'est pas un JSON-LD valide, la propriété renverra également un graphe de métadonnées vide.

### template : le modèle de formulaire

`template` est un objet de classe [`plume.pg.template.TemplateDict`](/plume/pg/template.py) contenant les informations relatives au modèle de formulaire à utiliser.

Les modèles de formulaires sont définis à l'échelle du service et stockés dans la base PostgreSQL. Ils permettent :
- d'ajouter des catégories locales au schéma de métadonnées communes défini par [shape.ttl](/plume/rdf/data/shape.ttl) ;
- de restreindre les catégories communes à afficher ;
- de substituer des paramètres locaux à ceux spécifiés par le schéma commun (par exemple remplacer le nom à afficher pour la catégorie de métadonnée, répartir les métadonnées dans plusieurs onglets...).

Pour plus de détails sur les modèles de formulaire, on se reportera à la partie [Modèles de formulaire](/docs/source/usage/modeles_de_formulaire.md), et plus particulièrement à sa sous-partie [Import par le plugin](/docs/source/usage/modeles_de_formulaire.md#import-par-le-plugin), qui explique comment générer `template`.


### columns : les descriptifs des champs

`columns` est la liste des champs de la table / vue courante. Plus précisément, il s'agit d'une liste de tuples dont le premier élément est le nom du champ et le second son descriptif, stocké tel quel en tant que descriptif PostgreSQL du champ.

Elle peut être obtenue ainsi :

```python

import psycopg2
from plume.pg import queries

conn = psycopg2.connect(connection_string)

with conn:
    with conn.cursor() as cur:
    
        query = queries.query_get_columns(schema_name, table_name)
        cur.execute(query)
        columns = cur.fetchall()

conn.close()

```

Dans le formulaire résultant, chaque champ se trouvera représenté par un widget `QTextEdit` placé dans l'onglet *Champs*.


### data : les métadonnées calculées

`data` est un dictionnaire contenant des informations actualisées à partir de sources externes (par exemple déduites des données) qui écraseront les valeurs présentes dans `metagraph`. Les clés du dictionnaire sont des chemins SPARQL identifiant des catégories de métadonnées, ses valeurs sont des listes contenant la ou les valeurs (`str`) à faire apparaître pour les catégories en question.

À ce stade, `WidgetsDict` prend parfaitement en charge le paramètre `data`, mais aucun mécanisme d'alimentation en informations externes n'a été mis en place. On pourra donc considérer qu'il vaut toujours `None`.

## Paramètres utilisateur

Sauf indication contraire, tous les paramètres utilisateur évoqués ci-après sont à récupérer dans les fichiers de configuration. Si un paramètre n'y est pas explicitement spécifié (parce que l'utilisateur n'a pas éprouvé le besoin de modifier le comportement par défaut), il ne devra pas non plus apparaître dans les arguments du constructeur de `WidgetsDict`.

### mode

`mode` est un paramètre utilisateur au sens où il est déterminé par l'utilisateur, mais **il ne doit pas être sauvegardé dans le fichier de configuration**.

Comme détaillé dans [Actions générales](/docs/source/usage/actions_generales.md#mode-lecture-mode-edition), il devra toujours valoir `'read'` (mode lecture) lors de l'ouverture initiale de la fiche. Si ses privilèges sont suffisants, l'utilisateur peut ensuite activer le mode édition, et `mode` vaudra alors `'edit'`.

Il est préférable de toujours spécifier explicitement ce paramètre dans la liste des arguments du constructeur de `WidgetsDict` (où sa valeur par défaut est `'edit'`).

### readHideBlank

`readHideBlank` est un booléen indiquant si les champs vides doivent être masqués en mode lecture.

Le comportement naturel est de masquer ces champs, et c'est ce que fera le constructeur de `WidgetsDict` si ce paramètre n'est pas spécifié.

### readHideUnlisted

`readHideUnlisted` est un booléen indiquant si, en mode lecture, il faut masquer les catégories qui n'apparaissent pas dans le modèle de formulaire à utiliser (cf. [template](#template--le-modèle-de-formulaire)) mais pour lesquelles des métadonnées ont été saisies antérieurement. Si aucun modèle n'est défini, les catégories concernées sont celles qui ne sont pas répertoriées dans le schéma des catégories communes.

Le comportement par défaut du constructeur de `WidgetsDict` est de masquer les champs en question.

### editHideUnlisted

`editHideUnlisted` est le pendant de `readHideUnlisted` pour le mode édition.

C'est un booléen indiquant si, en mode édition, il faut masquer les catégories qui n'apparaissent pas dans le modèle de formulaire à utiliser (cf. [template](#template--le-modèle-de-formulaire)) mais pour lesquelles des métadonnées ont été saisies antérieurement. Si aucun modèle n'est défini, les catégories concernées sont celles qui ne sont pas répertoriées dans le schéma des catégories communes.

Le comportement par défaut du constructeur de `WidgetsDict` est d'afficher les champs en question.

### language

`language` est une chaîne de caractères indiquant la langue principale de saisie des métadonnées. Ce paramètre peut être modifié via un widget dans l'interface fixe du plugin - cf. [Actions générales](/docs/source/usage/actions_generales.md#langue-principale-des-métadonnées).

Si `language` n'apparaît pas dans les arguments du constructeur de `WidgetsDict`, il sera considéré que les métadonnées sont saisies dans la première langue de la liste des langues autorisées, [`langList`](#langlist). Nonobstant, il est recommandé de toujours spécifier explicitement ce paramètre, afin d'assurer que la valeur utilisée par la fonction soit identique à celle qui apparaît dans la partie fixe de l'interface.

La documentation invitera l'utilisateur à privilégier les codes de langues sur deux caractères, comme attendu en RDF. Référence : [ISO 639](https://www.iso.org/iso-639-language-codes.html).

La langue principale de saisie des métadonnées a trois usages :
- les métadonnées identifiées comme traduisibles (par exemple le libellé du jeu de données et son descriptif sont traduisibles, mais pas sa date de création ni son identifiant) sont représentées en RDF avec une information sur leur langue. Cette langue sera toujours la langue principale de saisie des métadonnées, sauf lorsque le mode traduction (cf. [`translation`](#translation)) est actif.
- en mode lecture, lorsque des valeurs dans plusieurs langues sont disponibles pour une catégorie de métadonnées, le comportement par défaut de Plume est d'afficher uniquement les valeurs dans la langue principale (à défaut il tente les langues de [`langList`](#langList) dans l'ordre et, à défaut, choisit une langue disponible au hasard). Il est possible d'inhiber ce comportement avec le paramètre [`readOnlyCurrentLanguage`](#readOnlyCurrentLanguage), ou de forcer le même comportement en mode édition avec [`editOnlyCurrentLanguage`](#editOnlyCurrentLanguage) ;
- lorsqu'une métadonnées prend ses valeurs dans un thésaurus, lesdites valeurs sont représentées en RDF sous la forme d'URI. Ces URI sont référencés dans le fichier [vocabulary.ttl](/plume/rdf/data/vocabulary.ttl), qui fournit pour chacun d'entre eux des libellés lisibles par un être humain. Il existe toujours un libellé en français et souvent en anglais. La langue principale de saisie détermine la langue des libellés affichés dans l'interface. À défaut de libellé dans la langue principale, les langues de [`langList`](#langList) sont testées dans l'ordre et, à défaut, une traduction est choisie au hasard.

### translation

`translation` est un booléen indiquant si le mode traduction est actif. Comme [`language`](#language), ce paramètre peut être modifié via un widget dans l'interface fixe du plugin - cf. [Actions générales](/docs/source/usage/actions_generales.md#activation-du-mode-traduction). Il est ignoré quand le dictionnaire n'est pas généré en mode édition ([`mode`](#mode) valant `'edit'`).

Si `translation` n'apparaît pas dans les arguments du constructeur de `WidgetsDict`, il sera considéré que le mode traduction n'est pas actif. Nonobstant, il est recommandé de toujours spécifier explicitement ce paramètre, afin d'assurer que la valeur utilisée par la fonction soit identique à celle qui apparaît dans la partie fixe de l'interface.

### langList

`langList` est une liste ou un tuple de chaînes de caractères qui donne les langues autorisées pour les traductions, en complément de la langue principale de saisie spécifiée par [`language`](#language). Il alimente aussi la liste de valeurs du widget qui, dans la partie fixe de l'interface, permet de choisir la langue principale [Actions générales](/docs/source/usage/actions_generales.md#langue-principale-des-métadonnées).

Si `langList` n'apparaît pas dans les arguments du constructeur de `WidgetsDict`, celui-ci utilisera le tuple `('fr', 'en')` (français et anglais). Nonobstant, il est recommandé de toujours spécifier explicitement ce paramètre, afin d'assurer que la valeur utilisée par la fonction soit identique à celle qui apparaît dans la partie fixe de l'interface.

### readOnlyCurrentLanguage

`readOnlyCurrentLanguage` est un booléen qui indique si, en mode lecture, seules les métadonnées saisies dans la langue principale doivent être affichées. Cf. [language](#language) pour plus de détails.

Si `readOnlyCurrentLanguage` n'apparaît pas dans les arguments du constructeur de `WidgetsDict`, il sera considéré comme valant `True`.

### editOnlyCurrentLanguage

`editOnlyCurrentLanguage` est le pendant de `readOnlyCurrentLanguage` pour le mode édition.

C'est un booléen indiquant si, en mode édition **et lorsque le mode traduction n'est pas actif**, seules les métadonnées saisies dans la langue principale doivent être affichées. Cf. [language](#language) pour plus de détails.

Si `editdOnlyCurrentLanguage` n'apparaît pas dans les arguments du constructeur de `WidgetsDict`, il sera considéré comme valant `False`.

### labelLengthLimit

`labelLengthLimit` est un entier qui indique le nombre de caractères au-delà duquel l'étiquette d'une catégorie de métadonnées sera toujours affiché au-dessus du widget de saisie et non sur la même ligne. À noter que pour les widgets `QTextEdit` le label est placé au-dessus quoi qu'il arrive.

Si `labelLengthLimit` n'apparaît pas dans les arguments du constructeur de `WidgetsDict`, le seuil est fixé à 25 caractères.

### valueLengthLimit

`valueLengthLimit` est un entier qui indique le nombre de caractères au-delà duquel une valeur qui aurait dû être affichée dans un widget `QLineEdit` sera présentée à la place dans un `QTextEdit`. Indépendemment du nombre de caractères, la substitution sera aussi réalisée si la valeur contient un retour à la ligne.

Si `valueLengthLimit` n'apparaît pas dans les arguments du constructeur de `WidgetsDict`, le seuil est fixé à 65 caractères.

### textEditRowSpan

`textEditRowSpan` est un entier qui définit le nombre de lignes par défaut d'un widget `QTextEdit`, c'est-à-dire la valeur de `rowSpan` qui sera utilisée par le constructeur de `WidgetsDict` pour toutes les catégories telles que ni le modèle de formulaire ni le schéma des catégories communes ne fixe une valeur.

Si `textEditRowSpan` n'apparaît pas dans les arguments du constructeur de `WidgetsDict`, la hauteur est fixée à 6 lignes.


## Résultat : un dictionnaire de widgets

La classe `WidgetsDict` hérite de `dict` et définit des méthodes supplémentaires qui gèrent notamment l'actualisation du dictionnaire en fonction des actions de l'utilisateur (cf. [Actions contrôlées par les widgets du formulaire](/docs/source/usage/actions_widgets.md)).

En premier lieu, le dictionnaire de widgets sert de base à la génération du formulaire de saisie / consultation des métadonnées. Pour ce faire, on bouclera sur les clés du dictionnaire et créera au fur et à mesure les widgets qu'elles définissent, comme expliqué dans [Création d'un nouveau widget](/docs/source/usage/creation_widgets.md).

```python

{
    widgetkey_1 : dictionnaire_interne_1,
    widgetkey_2 : dictionnaire_interne_2
}

```

Chaque enregistrement du dictionnaire représente l'un objets des objets suivants du formulaire : une zone de saisie, un groupe de valeurs, un groupe de propriétés, un groupe de traduction, un bouton plus ou un bouton de traduction.

Les clés du dictionnaire de widgets sont des objets `plume.rdf.widgetkey.WidgetKey`. Elles forment une structure arborescente qui, y compris lorsque des widgets sont ajoutés, supprimés, masqués suite aux actions de l'utilisateur, assure que la cohérence du positionnement des widgets. Elle permet aussi de recréer aisément un graphe de métadonnées à partir du dictionnaire de widgets, en vu de l'enregistrement en JSON-LD des métadonnées actualisées.

Les valeurs du dictionnaire du widgets sont des objets [`plume.rdf.internaldict.InternalDict`](/plume/rdf/internaldict.py), dit "dictionnaires internes". Cette classe présente des dictionnaires de structure homogène qui contiennent toutes les informations nécessaires à la création du ou des widgets associés à l'objet et seront également utilisés pour référencer chacun des widgets créés. Outre leur fonction de référencement, les dictionnaires internes servent essentiellement à traduire les informations portées par les `WidgetKey` sous une forme plus aisément exploitable par les bibliothèques de QT.



