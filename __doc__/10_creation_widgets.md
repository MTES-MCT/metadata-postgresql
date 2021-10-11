# Création d'un nouveau widget

La présente page explique comment créer les widgets qui formeront le formulaire de consultation / édition des métadonnées à partir du dictionnaire des widgets. On suppose que le programme est en train de boucler sur les clés du dictionnaire.

Soit :
- `widgetsdict` le dictionnaire contenant tous les widgets et leurs informations de paramétrage (cf. [Génération du dictionnaire des widgets](/__doc__/05_generation_dictionnaire_widgets.md)).
- `key` la clé de l'enregistrement en cours de traitement.
- `vocabulary` le graphe RDF qui rassemble les valeurs des thésaurus (cf. [Génération du dictionnaire des widgets](/__doc__/05_generation_dictionnaire_widgets.md#vocabulary--la-compilation-des-thésaurus)).
- `language` la langue principale de rédaction des métadonnées sélectionnée par l'utilisateur (cf. [Actions générales](/__doc__/16_actions_generales.md#langue-principale-des-métadonnées)).

Chaque enregistrement du dictionnaire des widgets contrôle un widget principal et, le cas échéant, un ou plusieurs widgets annexes. Non seulement son dictionnaire interne donne les informations nécessaires à leur création, mais certaines de ses clés servent à référencer les objets Qt créés.

**Widget principal** : [Type](#type) • [Stockage](#stockage) • [Parent](#parent) • [Widget masqué ?](#widget-masqué-) • [Paramètres spécifiques aux widgets QGroupBox](#paramètres-spécifiques-aux-widgets-qgroupbox) • [Paramètres spécifiques aux widgets QToolButton](#paramètres-spécifiques-aux-widgets-qtoolbutton) • [Paramètres spécifiques aux widgets de saisie](#paramètres-spécifiques-aux-widgets-de-saisie) • [Paramètres spécifiques aux widgets QLineEdit et QTextEdit](#paramètres-spécifiques-aux-widgets-qlineedit-et-qtextedit) • [Paramètres spécifiques aux widgets QComboBox](#paramètres-spécifiques-aux-widgets-qcombobox) • [Paramètres spécifiques aux widgets QLabel](#paramètres-spécifiques-aux-widgets-qlabel) • [Placement dans la grille](#placement-dans-la-grille)

**Widgets annexes** : [Widget annexe : grille](#widget-annexe--grille) • [Widget annexe : étiquette](#widget-annexe--étiquette) • [Widget annexe : bouton de sélection de la source](#widget-annexe--bouton-de-sélection-de-la-source) • [Widget annexe : bouton de sélection de la langue](#widget-annexe--bouton-de-sélection-de-la-langue) • [Widget annexe : bouton "moins"](#widget-annexe--bouton-moins)

Le widget principal et les widgets annexes sont totalement indépendants. Ils peuvent être simplement créés les uns à la suite des autres, de la manière suivante :

```python
	
	# commandes de création du widget principal, variables
	# selon le type :
	if widgetsdict[key]['main widget type'] == 'QGroupBox':
		...	
	elif widgetsdict[key]['main widget type'] == ...
		...
	# etc.
	
	# commandes de création du widget annexe d'étiquette,
	# s'il y a lieu :
	if widgetsdict[key]['object'] == 'edit' and widgetsdict[key]['label']:
		...
	
	# commandes de création du widget annexe de sélection de
	# la source, s'il y a lieu :
	if widgetsdict[key]['multiple sources']:
		...
		
	# commandes de création du widget annexe de sélection de
	# la langue, s'il y a lieu :
	if widgetsdict[key]['authorized languages']:
		...
		
	# commandes de création du widget annexe bouton moins,
	# s'il y a lieu :
	if widgetsdict[key]['has minus button']:
		...

```

Les commandes à exécuter sont détaillées dans la suite.
 
## Widget principal

### Type

Le type du widget principal (QGroupBox, QToolButton, QLineEdit...) est fourni par la clé `'main widget type'` du dictionnaire interne.

```python

widgetsdict[key]['main widget type']

```

**Si `'main widget type'` ne contient aucune valeur, il n'y a pas lieu de créer de widget.** Il s'agit de catégories de métadonnées non répertoriées dans le modèle de formulaire (template), et qui ne doivent donc pas être affichées, mais qui contiennent des valeurs qu'il n'est pas question de perdre.

### Stockage

Le nouveau widget a vocation à être stocké dans la clé `'main widget'` du dictionnaire interne.

```python

widgetsdict[key]['main widget']

```

### Parent

Le widget *parent* est le `'main widget'` de l'enregistrement dont la clé est le second argument du tuple `key`. Il s'agira toujours d'un QGroupBox.

Par exemple, si `key` vaut `(2, (5, (0,)))`,  son parent est le widget principal de la clé `(5, (0,))`.

```python

widgetsdict[key[1]]['main widget']

```

**Mais on utilisera plutôt la méthode `parent_widget()`**, qui renvoie directement le widget principal (QGroupBox) de l'enregistrement parent :

```python

widgetsdict.parent_widget(key)

```

### Widget masqué ?

Certains widgets seront à masquer ou afficher selon les actions de l'utilisateur. Ceci concerne par exemple les boutons de traduction, qui devront être masqués si une traduction a déjà été saisie pour chacune des langues autorisées. Autre cas : lorsqu'une métadonnée peut être saisie au choix sous la forme d'un URI ou d'un ensemble de propriétés littérales, les widgets servant pour la forme non sélectionnée sont masqués tant que l'utilisateur ne décide pas de changer de forme.

Concrètement, le widget principal **et tous les widgets annexes** d'un enregistrement devront être masqués dès lors que la clé `'hidden'` ou la clé `'hidden M'` vaut `True`.

```python

widgetsdict[key]['hidden'] or widgetsdict[key]['hidden M']

```


### Paramètres spécifiques aux widgets QGroupBox

Deux cas doivent être distingués lorsque `'main widget type'` vaut `'QGroupBox'` : les onglets et les autres groupes.


#### Onglets

Les onglets sont reconnaissables au fait que la condition suivante est remplie :

```python

if rdf_utils.is_root(key):
    ...

```

Ils correspondent aux onglets du formulaire. Contrairement à tous les autres widgets, ils n'auront donc pas vocation à être placés dans un QGridLayout (la partie [Placement dans la grille](#placement-dans-la-grille) ne s'applique pas à eux), mais devront être insérés en tant que pages dans le QTabWidget qui portera le formulaire. Le QTabWidget en question ne fait pas l'objet d'un enregistrement du dictionnaire et devra avoir été créé au préalable.

Les libellés des onglets sont fournis par la clé `'label'` du dictionnaire interne.

```python

widgetsdict[key]['label']

```

#### Autres groupes

Pour tous les autres groupes, c'est-à-dire ceux pour lesquels `rdf_utils.is_root(key)` renvoie `False`.

- L'**étiquette** - paramètre `title` du QGroupBox - est fournie par la clé `'label'` du dictionnaire interne.

```python

widgetsdict[key]['label']

```

Cette clé ne sera renseignée que s'il y a lieu d'afficher un libellé sur le groupe.

- Lorsqu'elle est renseignée, la clé `'help text'` fournit un **texte d'aide** (descriptif de la catégorie de métadonnée), qui pourrait alimenter un `toolTip` (voire un `whatsThis`).

```python

widgetsdict[key]['main widget'].setToolTip(widgetsdict[key]['help text'])

```

- La couleur du cadre du QGroupBox dépendra de la nature du groupe, soit de la valeur de la clé `'object'` ou plus simplement la valeur renvoyée par :

```python

widgetsdict.group_kind(key)

```

On pourra utiliser les valeurs par défaut suivantes :

| Type de groupe | `group_kind(key)` | Couleur |
| --- | --- | --- |
| Groupe de propriétés | `'group of properties'` | `'#958B62'` |
| Groupe de valeurs | `'group of values'` | `'#5770BE'` |
| Groupe de traduction | `'translation group'` | `'#FF8D7E'` |



### Paramètres spécifiques aux widgets QToolButton

Les seuls cas où le widget principal est un QToolButton sont ceux des "boutons plus" et "boutons de traduction", qui permettent à l'utilisateur d'ajouter réciproquement des valeurs ou traductions supplémentaires. La clé `'object'` vaut alors `'plus button'` ou `'translation button'`.

- L'action associée à ce QToolButton sera stockée dans la clé `'main action'` du dictionnaire.

```python

widgetsdict[key]['main action']

```

*Pour la définition de l'action, cf. [Actions contrôlées par les widgets du formulaire](/__doc__/15_actions_widgets.md#boutons-plus-et-boutons-de-traduction).*

- L'image ![plus_button.svg](/plume/icons/buttons/plus_button.svg) à utiliser est toujours [plus_button.svg](/plume/icons/buttons/plus_button.svg), mais la couleur dépendra du type de groupe dans lequel se trouve le bouton, soit de la valeur renvoyée par :

```python

widgetsdict.group_kind(key)

```

Comme pour les QGroupBox, on pourra utiliser les valeurs par défaut suivantes :

| Type de groupe | `group_kind(key)` | Couleur |
| --- | --- | --- |
| Groupe de propriétés | `'group of properties'` | `'#958B62'` |
| Groupe de valeurs | `'group of values'` | `'#5770BE'` |
| Groupe de traduction | `'translation group'` | `'#FF8D7E'` |

*NB. En pratique, il n'y a pas de bouton plus dans les groupes de propriétés, donc la couleur associée ne sera jamais utilisée dans ce contexte.*

Soit `color` la couleur souhaitée pour le bouton et `raw_svg` le contenu du fichier *plus_button.svg*, on pourra appliquer la couleur avec :

```python

colored_svg = raw_svg.format(fill=color)

```

- Le texte d'aide à afficher en infobulle sur le bouton se trouve dans la clé `text help` du dictionnaire.

```python

widgetsdict[key]['text help']

```

### Paramètres spécifiques aux widgets de saisie

- Lorsqu'elle existe, soit parce qu'elle était déjà renseignée dans la fiche de métadonnées, soit parce qu'une valeur par défaut est définie pour la catégorie considérée, la **valeur à afficher** dans le widget est fournie par la clé `'value'` du dictionnaire.

À noter que les valeurs par défaut ne sont utilisées que si le groupe de propriétés est vide.

```python

widgetsdict[key]['value']

```

- Si la clé `'read only'` vaut `True`, le widget doit être visible mais désactivé, pour empêcher les modifications manuelles par l'utilisateur.

```python

widgetsdict[key]['read only']

```

- La clé `'is mandatory'` contient un booléen indiquant s'il est obligatoire (valeur `True`) ou non (valeur `False` ou `None`) de saisir une valeur pour la catégorie.

```python

widgetsdict[key]['is mandatory']

```
 

### Paramètres spécifiques aux widgets QLineEdit et QTextEdit

Pour les widgets d'édition de texte, le dictionnaire apporte divers paramètres complémentaires. Ils sont tous optionnels. Si la clé ne contient pas de valeur, c'est qu'il n'y a pas lieu d'utiliser le paramètre.

- `'placeholder text'` donne la **valeur fictive** à afficher dans le widget :

```python

widgetsdict[key]['main widget'].setPlaceholderText(widgetsdict[key]['placeholder text'])

```

- `'input mask'` donne le **masque de saisie** :

```python

widgetsdict[key]['main widget'].setInputMask(widgetsdict[key]['input mask'])

```

- `'type validator'` indique si un **validateur basé sur le type** doit être défini et lequel :

```python

mTypeValidator = widgetsdict[key]['type validator']

if mTypeValidator == 'QIntValidator':
    widgetsdict[key]['main widget'].setValidator(QIntValidator(widgetsdict[key]['main widget']))
elif mTypeValidator == 'QDoubleValidator':
    widgetsdict[key]['main widget'].setValidator(QDoubleValidator(widgetsdict[key]['main widget']))

```

*Ces validateurs permettent également de définir des valeurs minimum et maximum autorisées. Comme le SHACL le permet également (avec `sh:minInclusive` et `sh:maxInclusive`, car les paramètres `bottom` et `top` de `QIntValidator()` et `QDoubleValidator()` sont inclusifs), cette possibilité pourrait être utilisée à l'avenir, mais aucune clé n'a été prévue en ce sens à ce stade.*

- `'regex validator pattern'` donne l'**expression rationnelle** que doit respecter la valeur saisie et `'regex validator flags'` les options éventuelles :

```python

re = QRegularExpression(widgetsdict[key]['regex validator pattern'])

if "i" in widgetsdict[key]['regex validator flags']:
    re.setPatternOptions(QRegularExpression.CaseInsensitiveOption)
    
if "s" in widgetsdict[key]['regex validator flags']:
    re.setPatternOptions(QRegularExpression.DotMatchesEverythingOption)

if "m" in widgetsdict[key]['regex validator flags']:
    re.setPatternOptions(QRegularExpression.MultilineOption)
    
if "x" in widgetsdict[key]['regex validator flags']:
    re.setPatternOptions(QRegularExpression.ExtendedPatternSyntaxOption)

widgetsdict[key]['main widget'].setValidator(
    QRegularExpressionValidator(re),
    widgetsdict[key]['main widget'])
    )

```

*Seules les options `i`, `s`, `m` et `x` sont à la fois admises en SHACL et par QT, ce sont donc les seules à être gérées.*


### Paramètres spécifiques aux widgets QComboBox

- Pour obtenir la **liste des termes** à afficher dans le QComboBox, on utilisera la fonction `build_vocabulary()`. La clé `'current source'` contient le nom du thésaurus à utiliser.

```python

thesaurus = build_vocabulary(widgetsdict[key]['current source'], vocabulary, language)

```

*`language` est le paramètre utilisateur qui spécifie la langue principale de saisie des métadonnées, qui est également la langue dans laquelle seront affichés les termes des QComboBox. Cf. [Paramètres utilisateur](/__doc__/20_parametres_utilisateur.md).*
*`vocabulary` est le graphe qui répertorie les termes de tous les thésaurus, importé via la fonction `rdf_utils.load_vocabulary()`. Cf. [Génération du dictionnaire de widgets](/__doc__/05_generation_dictionnaire_widgets.md) pour plus de détails.*

- Comme les QTextEdit et QLineEdit, les widgets QComboBox peuvent afficher une **valeur fictive** fournie par la clé `'placeholder text'`. Celle-ci sera généralement renseignée car, si ni le schéma des métadonnées communes ni le modèle local ne fournissent de texte fictif, c'est le nom du thésaurus courant qui sera affiché.


```python

widgetsdict[key]['main widget'].setPlaceholderText(widgetsdict[key]['placeholder text'])

```

Autant que possible - considérant la quantité de termes dans certains thésaurus - les QComboBox devraient afficher une ligne de saisie avec **auto-complétion**. Il est par contre important qu'ils **ne permettent pas d'entrer d'autres valeurs que celles des thésaurus**.


### Paramètres spécifiques aux widgets QLabel

*NB : il n'est pas question dans cette partie des [widgets annexes d'étiquettes]((#widget-annexe--étiquette)) mais du cas où le widget principal lui-même est un QLabel.*

En mode lecture, des widgets QLabel remplacent la plupart des widgets de saisie (à ce jour tous sauf les QCheckBox). Ils permettent notamment d'afficher des hyperliens cliquables.

Comme pour les véritables widgets de saisie, la **valeur à afficher** est fournie par la clé `'value'` du dictionnaire.

```python

widgetsdict[key]['value']

```

Il importera d'activer le découpage sur plusieurs lignes :

```python

widgetsdict[key]['main widget'].setWordWrap(True)

```

Ainsi sans doute que l'ouverture automatique des liens :

```python

widgetsdict[key]['main widget'].setOpenExternalLinks(True)

```

### Placement dans la grille

*Les informations ci-après ne valent pas pour les onglets (cf. [Onglets](#onglets)).*

Le nouveau widget doit être placé dans le QGridLayout associé à son parent.

```python

widgetsdict[key[1]]['grid widget']

```

**Mais on utilisera plutôt la méthode dédiée `parent_grid()`**, qui renvoie directement la grille (QGridLayout) de l'enregistrement parent :

```python

widgetsdict.parent_grid(key)

```

Les paramètres de placement du widget dans la grille - soit les arguments `row`, `column`, `rowSpan` et `columnSpan` de la méthode `addWidget()` - sont donnés par la méthode `widget_placement()` de la classe `WidgetsDict`.

```python

row, column, rowSpan, columnSpan = widgetsdict.widget_placement(key, 'main widget')

```

[↑ haut de page](#création-dun-nouveau-widget)


## Widget annexe : grille

Pour les groupes de valeurs, groupes de propriétés et groupes de traduction, un widget annexe QGridLayout doit être créé en paralèlle du QGroupBox.

```python

widgetsdict[key]['object'] in ('group of values', 'group of properties', 'translation group')

```

### Stockage

Le widget QGridLayout sera stocké dans la clé `'grid widget'` du dictionnaire interne.

```python

widgetsdict[key]['grid widget']

```

### Parent

Le widget *parent* est le `'main widget'` de l'enregistrement.

```python

widgetsdict[key]['main widget']

```

[↑ haut de page](#création-dun-nouveau-widget)



## Widget annexe : étiquette

**Pour les widgets de saisie uniquement**, un QLabel doit être créé dès lors que la clé `'label'` du dictionnaire interne n'est pas nulle. Le libellé à afficher correspond bien entendu à la valeur de la clé `'label'`.

```python

widgetsdict[key]['object'] == 'edit' and widgetsdict[key]['label']

```

### Stockage

Le widget QLabel sera stocké dans la clé `'label widget'` du dictionnaire interne.

```python

widgetsdict[key]['label widget']

```

### Parent

Le widget *parent* est le même que pour le widget principal. Il s'agit du `'main widget'` de l'enregistrement dont la clé est le second argument de `key`, qu'on obtiendra plutôt avec :

```python

widgetsdict.parent_widget(key)

```

### Placement dans la grille

Le QLabel doit être placé dans le QGridLayout associé à son parent.

```python

widgetsdict.parent_grid(key)

```

Les paramètres de placement du widget dans la grille - soit les arguments `row`, `column`, `rowSpan` et `columnSpan` de la méthode `addWidget()` - sont donnés par la méthode `widget_placement()` de la classe `WidgetsDict`.

```python

row, column, rowSpan, columnSpan = widgetsdict.widget_placement(key, 'label widget')

```


### Texte d'aide

Lorsqu'elle est renseignée, la clé `'help text'` fournit un **texte d'aide** (descriptif de la catégorie de métadonnée), qui pourrait alimenter un `toolTip` (voire un `whatsThis`).

```python

widgetsdict[key]['label widget'].setToolTip(widgetsdict[key]['help text'])

```


[↑ haut de page](#création-dun-nouveau-widget)


### Widget masqué ?

Le QLabel doit être masqué dès lors que la clé `'hidden'` ou la clé `'hidden M'` vaut `True`.

```python

widgetsdict[key]['hidden'] or widgetsdict[key]['hidden M']

```


## Widget annexe : bouton de sélection de la source

Un widget QToolButton de sélection de source doit être créé dès lors que la condition suivante est vérifiée :

```python

widgetsdict[key]['multiple sources']

```

### Stockage

Le widget de sélection de la source est stocké dans la clé `'switch source widget'` du dictionnaire interne.

```python

widgetsdict[key]['switch source widget']

```

### Parent

Le widget *parent* est le même que pour le widget principal. Il s'agit du `'main widget'` de l'enregistrement dont la clé est le second argument de `key`, qu'on obtiendra plutôt avec :

```python

widgetsdict.parent_widget(key)

```

### Menu

Le QMenu associé au QToolButton est stocké dans la clé `'switch source menu'` du dictionnaire.

```python

widgetsdict[key]['switch source menu']

```

Ce QMenu contient une QAction par thésaurus utilisable pour la métadonnée. Les QAction sont elles-mêmes stockées dans la clé `'switch source actions'` du dictionnaire, sous la forme d'une liste.

```python

widgetsdict[key]['switch source actions']

```

Les libellés des QAction correspondent aux noms des thésaurus et sont fournis par la liste contenue dans la clé `'sources'` du dictionnaire :

```python

widgetsdict[key]['sources']

```

*Pour la définition des actions, cf. [15_actions_widgets](/__doc__/15_actions_widgets.md#boutons-de-sélection-de-la-source).*

Il serait souhaitable de mettre en évidence le thésaurus courant - celui qui fournit les valeurs du QComboBox - par exemple via une icône (tandis que les autres thésaurus n'en auraient pas). Son nom est donné par la clé `'current source'`.

```python

widgetsdict[key]['current source']

```

### Placement dans la grille

Le QToolButton doit être placé dans le QGridLayout associé à son parent.

```python

widgetsdict.parent_grid(key)

```

Le bouton de sélection de la source est toujours positionné immédiatement à droite de la zone de saisie.

Concrètement, les paramètres de placement du widget dans la grille - soit les arguments `row`, `column`, `rowSpan` et `columnSpan` de la méthode `addWidget()` - sont donnés par la méthode `widget_placement()` de la classe `WidgetsDict`.

```python

row, column, rowSpan, columnSpan = widgetsdict.widget_placement(key, 'switch source widget')

```


### Icône

L'icône ![source_button.svg](/plume/icons/buttons/source_button.svg) à utiliser pour le bouton de sélection de la source est fournie par le fichier [source_button.svg](/plume/icons/buttons/source_button.svg). Contrairement aux boutons plus et moins, sa couleur est fixe à ce stade.

[↑ haut de page](#création-dun-nouveau-widget)


### Texte d'aide

On pourra afficher en infobulle sur le bouton le texte suivant :

```python

'Sélection du thésaurus ou mode de saisie'

```


### Widget masqué ?

Le QToolButton doit être masqué dès lors que la clé `'hidden'` ou la clé `'hidden M'` vaut `True`.

```python

widgetsdict[key]['hidden'] or widgetsdict[key]['hidden M']

```


## Widget annexe : bouton de sélection de la langue

Un widget QToolButton de sélection de langue doit être créé dès lors que la condition suivante est vérifiée (ce qui ne se produira que si le mode traduction est actif) :

```python

widgetsdict[key]['authorized languages']

```

### Stockage

Le bouton de sélection de la langue est stocké dans la clé `'language widget'` du dictionnaire interne.

```python

widgetsdict[key]['language widget']

```

### Parent

Le widget *parent* est le même que pour le widget principal. Il s'agit du `'main widget'` de l'enregistrement dont la clé est le second argument de `key`, qu'on obtiendra plutôt avec :

```python

widgetsdict.parent_widget(key)

```

### Menu

Le QMenu associé au QToolButton est stocké dans la clé `'language menu'` du dictionnaire.

```python

widgetsdict[key]['language menu']

```

Ce QMenu contient une QAction par langue disponible. Les QAction sont elles-mêmes stockées dans la clé `'language actions'` du dictionnaire, sous la forme d'une liste.

```python

widgetsdict[key]['language actions']

```

Les libellés des QAction correspondent aux noms abrégés des langues et sont fournis par la liste contenue dans la clé `'authorized languages'` du dictionnaire :

```python

widgetsdict[key]['authorized languages']

```

*Pour la définition des actions, cf. [Actions contrôlées par les widgets du formulaire](/__doc__/15_actions_widgets.md#boutons-de-sélection-de-la-langue).*

### Rendu

Au lieu d'une icône, le QToolButton de sélection de la langue montre un texte correspondant au nom abrégé de la langue sélectionnée. Celui-ci est fourni par la clé `'language value'`.

```python

widgetsdict[key]['language value']

```

### Texte d'aide

On pourra afficher en infobulle sur le bouton le texte suivant :

```python

'Sélection de la langue de la métadonnée'

```

### Placement dans la grille

Le QToolButton doit être placé dans le QGridLayout associé à son parent.

```python

widgetsdict.parent_grid(key)

```

Le bouton de sélection de la langue est toujours positionné immédiatement à droite de la zone de saisie. Il n'y a pas de conflit possible avec les boutons de sélection de source, car ceux-là ne peuvent apparaître que sur des objets de type *IRI* ou *BlankNode*, alors que spécifier la langue n'est possible que pour les objets de type *Literal*.

Concrètement, les paramètres de placement du widget dans la grille - soit les arguments `row`, `column`, `rowSpan` et `columnSpan` de la méthode `addWidget()` - sont donnés par la méthode `widget_placement()` de la classe `WidgetsDict`.

```python

row, column, rowSpan, columnSpan = widgetsdict.widget_placement(key, 'language widget')

```

[↑ haut de page](#création-dun-nouveau-widget)


### Widget masqué ?

Le QToolButton doit être masqué dès lors que la clé `'hidden'` ou la clé `'hidden M'` vaut `True`.

```python

widgetsdict[key]['hidden'] or widgetsdict[key]['hidden M']

```


## Widget annexe : bouton "moins"

Pour les propriétés admettant des valeurs multiples ou des traductions, des widgets QToolButton permettent à l'utilisateur de supprimer les valeurs précédemment saisies, à condition qu'il en reste au moins une.

Un tel widget doit être créé dès lors que la condition suivante est vérifiée :

```python

widgetsdict[key]['has minus button']

```

### Stockage

Il est stocké dans la clé `'minus widget'` du dictionnaire interne.

```python

widgetsdict[key]['minus widget']

```

### Parent

Le widget *parent* est le même que pour le widget principal. Il s'agit du `'main widget'` de l'enregistrement dont la clé est le second argument de `key`, qu'on obtiendra plutôt avec :

```python

widgetsdict.parent_widget(key)

```

### Action

L'action associée au QToolButton est stockée dans la clé `'minus action'` du dictionnaire.

```python

widgetsdict[key]['minus action']

```

*Pour la définition de l'action, cf. [Actions contrôlées par les widgets du formulaire](/__doc__/15_actions_widgets.md#boutons-moins).*

### Placement dans la grille

Le QToolButton doit être placé dans le QGridLayout associé à son parent.

```python

widgetsdict.parent_grid(key)

```

Le bouton "moins" est positionné sur la ligne de la zone de saisie, à droite du bouton de sélection de la source / de la langue s'il y en a un, sinon immédiatement à droite de la zone de saisie. À noter que, par construction, il ne peut jamais y avoir à la fois un bouton de sélection de la langue et un bouton de sélection de la source.

Concrètement, les paramètres de placement du widget dans la grille - soit les arguments `row`, `column`, `rowSpan` et `columnSpan` de la méthode `addWidget()` - sont donnés par la méthode `widget_placement()` de la classe `WidgetsDict`.

```python

row, column, rowSpan, columnSpan = widgetsdict.widget_placement(key, 'minus widget')

```

### Icône

L'image ![minus_button.svg](/plume/icons/buttons/minus_button.svg) à utiliser pour un bouton moins est toujours [minus_button.svg](/plume/icons/buttons/minus_button.svg), mais la couleur dépendra du type de groupe dans lequel se trouve le bouton, soit de la valeur renvoyée par :

```python

widgetsdict.group_kind(key)

```

Comme pour les QGroupBox et les boutons plus/boutons de traduction, on pourra utiliser les valeurs par défaut suivantes :

| Type de groupe | `group_kind(key)` | Couleur |
| --- | --- | --- |
| Groupe de propriétés | `'group of properties'` | `'#958B62'` |
| Groupe de valeurs | `'group of values'` | `'#5770BE'` |
| Groupe de traduction | `'translation group'` | `'#FF8D7E'` |

*NB. En pratique, il n'y a pas de bouton moins dans les groupes de propriétés, donc la couleur associée ne sera jamais utilisée dans ce contexte.*

Soit `color` la couleur souhaitée pour le bouton et `raw_svg` le contenu du fichier *minus_button.svg*, on pourra appliquer la couleur avec :

```python

colored_svg = raw_svg.format(fill=color)

```

### Texte d'aide

On pourra afficher en infobulle sur le bouton le texte suivant :

```python

'Supprimer l'élément'

```

### Widget masqué ?

Comme tous les autres widgets, le QToolButton du bouton moins doit être masqué dès lors que la clé `'hidden'` ou la clé `'hidden M'` vaut `True`.

```python

widgetsdict[key]['hidden'] or widgetsdict[key]['hidden M']

```

Il devra également être masqué si le groupe de traduction ou groupe de valeurs ne contient qu'un élément, soit quand la condition suivante est remplie :

```python

widgetsdict[key]['hide minus button']

```

[↑ haut de page](#création-dun-nouveau-widget)
