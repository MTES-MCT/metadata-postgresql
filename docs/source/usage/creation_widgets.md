# Création d'un nouveau widget

La présente page explique comment créer les widgets - `QtWidgets.QWidget` - et autres objets QT (`QtWidgets.QGridLayout`, `QtWidgets.QMenu`, `QtGui.QAction`) qui formeront le formulaire de consultation / édition des métadonnées à partir du [dictionnaire des widgets](/docs/source/usage/generation_dictionnaire_widgets.md). On suppose que le programme est en train de boucler sur les clés dudit dictionnaire.

Soit :
- `widgetsdict` le dictionnaire contenant tous les widgets et leurs informations de paramétrage (cf. [Génération du dictionnaire des widgets](/docs/source/usage/generation_dictionnaire_widgets.md)), objet de classe [`plume.rdf.widgetsdict.WidgetsDict`](/plume/rdf/widgetsdict.py).
- `widgetkey` la clé de l'enregistrement en cours de traitement, objet de classe [`plume.rdf.widgetkey.WidgetKey`](/plume/rdf/widgetkey.py).

La valeur associée à `widgetkey` dans le dictionnaire de widgets, c'est-à-dire `widgetsdict[widgetkey]`, est un objet de classe [`plume.rdf.internaldict.InternalDict`](/plume/rdf/internaldict.py) dit "dictionnaire interne".

Chaque enregistrement du dictionnaire des widgets contrôle un widget principal et, le cas échéant, un ou plusieurs widgets annexes. Non seulement son dictionnaire interne donne les informations nécessaires à leur création, mais certaines de ses clés servent à référencer les objets Qt créés.

**Widget principal** : [Type](#type) • [Stockage](#stockage) • [Placement dans la grille](#placement-dans-la-grille) • [Widget masqué ?](#widget-masqué-) • [Paramètres spécifiques aux widgets QGroupBox](#paramètres-spécifiques-aux-widgets-qgroupbox) • [Paramètres spécifiques aux widgets QToolButton](#paramètres-spécifiques-aux-widgets-qtoolbutton) • [Paramètres spécifiques aux widgets de saisie](#paramètres-spécifiques-aux-widgets-de-saisie) • [Paramètres spécifiques aux widgets QLineEdit et QTextEdit](#paramètres-spécifiques-aux-widgets-qlineedit-et-qtextedit) • [Paramètres spécifiques aux widgets QComboBox](#paramètres-spécifiques-aux-widgets-qcombobox) • [Paramètres spécifiques aux widgets QLabel](#paramètres-spécifiques-aux-widgets-qlabel)

**Widgets annexes** : [Widget annexe : grille](#widget-annexe--grille) • [Widget annexe : étiquette](#widget-annexe--étiquette) • [Widget annexe : bouton de sélection de la source](#widget-annexe--bouton-de-sélection-de-la-source) • [Widget annexe : bouton de sélection de la langue](#widget-annexe--bouton-de-sélection-de-la-langue) • [Widget annexe : bouton de sélection de l'unité](#widget-annexe--bouton-de-sélection-de-lunité) • [Widget annexe : bouton d'aide à la saisie des géométries](#widget-annexe--bouton-daide-à-la-saisie-des-géométries) • [Widget annexe : bouton "moins"](#widget-annexe--bouton-moins)

Le widget principal et les widgets annexes sont totalement indépendants. Ils peuvent être simplement créés les uns à la suite des autres, de la manière suivante :

```python

    # commandes de création du widget principal, variables
    # selon le type :
    if widgetsdict[widgetkey]['main widget type'] == 'QGroupBox':
        ...	
    elif widgetsdict[widgetkey]['main widget type'] == ...
        ...
    # etc.

    # commandes de création du widget annexe d'étiquette,
    # s'il y a lieu :
    if widgetsdict[widgetkey]['has label']:
        ...

    # commandes de création du widget annexe de sélection de
    # la source, s'il y a lieu :
    if widgetsdict[widgetkey]['multiple sources']:
        ...
        
    # commandes de création du widget annexe de sélection de
    # la langue, s'il y a lieu :
    if widgetsdict[widgetkey]['authorized languages']:
        ...

    # commandes de création du widget annexe de sélection de
    # l'unité, s'il y a lieu :
    if widgetsdict[widgetkey]['units']:
        ...
    
    # commandes de création du widget annexe d'aide à la saisie
    # des géométries, s'il y a lieu :
    if widgetsdict[widgetkey]['geo tools']:
        ...
    
    # commandes de création du widget annexe bouton moins,
    # s'il y a lieu :
    if widgetsdict[widgetkey]['has minus button']:
        ...

```

Les commandes à exécuter sont détaillées dans la suite.
 
## Widget principal

### Type

Le type du widget principal (`QGroupBox`, `QToolButton`, `QLineEdit`...) est fourni par la clé `'main widget type'` du dictionnaire interne.

```python

widgetsdict[widgetkey]['main widget type']

```

*Si `'main widget type'` ne contient aucune valeur, il n'y a pas lieu de créer de widget. Ceci ne se produit en pratique que pour la clé-racine du dictionnaire, qui est également référencée par l'attribut `plume.rdf.widgetsdict.WidgetsDict.root` et n'appelle aucune action.*

### Stockage

Le nouveau widget a vocation à être stocké dans la clé `'main widget'` du dictionnaire interne.

```python

widgetsdict[widgetkey]['main widget'] = main_widget

```

*Où `main_widget` est le widget principal qui vient d'être créé.*


### Placement dans la grille

*Les informations ci-après ne valent pas pour les onglets (cf. [Onglets](#onglets)).*

Le nouveau widget doit être placé dans le `QGridLayout` associé à la clé parente, obtenu grâce à la méthode `plume.rdf.widgetsdict.WidgetsDict.parent_grid`.

Les paramètres de placement du widget dans la grille - soit les arguments `row`, `column`, `rowSpan` et `columnSpan` de la méthode `QGridLayout.addWidget` - sont donnés par la méthode `plume.rdf.widgetsdict.WidgetsDict.widget_placement`.

```python

row, column, rowSpan, columnSpan = widgetsdict.widget_placement(widgetkey, 'main widget')
grid = widgetsdict.parent_grid(widgetkey)
grid.addWidget(main_widget, row, column, rowSpan, columnSpan)

```

*`main_widget` est le widget principal qui vient d'être créé. Le second paramètre de `widget_placement` indique que les coordonnées demandées sont celles du widget principal de la clé. La même méthode sera utilisée ensuite pour connaître le placement de ses widgets annexes, avec en second argument le nom du widget annexe considéré.*

Les grilles sont elles-mêmes des widgets annexes associés aux clés de groupes. Cf. [Widget annexe : grille](#widget-annexe--grille).

[↑ haut de page](#création-dun-nouveau-widget)

### Widget masqué ?

Certains widgets seront à masquer ou afficher selon les actions de l'utilisateur. Ceci concerne par exemple les boutons de traduction, qui devront être masqués si une traduction a déjà été saisie pour chacune des langues autorisées. Autre cas : lorsqu'une métadonnée peut être saisie au choix sous la forme d'un URI ou d'un ensemble de propriétés littérales, les widgets servant pour la forme non sélectionnée sont masqués tant que l'utilisateur ne décide pas de changer de source (cf. [Widget annexe : bouton de sélection de la source](#widget-annexe--bouton-de-sélection-de-la-source)).

Concrètement, le widget principal **et tous les widgets annexes** d'un enregistrement devront être masqués dès lors que la clé `'hidden'` vaut `True`.

```python

if widgetsdict[widgetkey]['hidden']:
    ...

```


### Paramètres spécifiques aux widgets QGroupBox

Deux cas doivent être distingués lorsque `'main widget type'` vaut `'QGroupBox'` : les onglets et les autres groupes.


#### Onglets

Les onglets sont reconnaissables au fait que la condition suivante est remplie :

```python

if widgetsdict[widgetkey]['object'] == 'tab':
    ...

```

Ils correspondent aux onglets du formulaire. Contrairement à tous les autres widgets, ils n'auront donc pas vocation à être placés dans un `QGridLayout` (la partie [Placement dans la grille](#placement-dans-la-grille) ne s'applique pas à eux), mais devront être insérés en tant que pages dans le `QTabWidget` qui portera le formulaire. Le `QTabWidget` en question ne fait pas l'objet d'un enregistrement du dictionnaire et devra avoir été créé au préalable.

Les libellés des onglets sont, comme pour toutes les étiquettes, fournis par la clé `'label'` du dictionnaire interne.

```python

widgetsdict[widgetkey]['label']

```

#### Autres groupes

Pour tous les autres groupes, c'est-à-dire ceux pour lesquels la valeur de la clé `'object'` n'est pas `'tab'`.

- La partie [Placement dans la grille](#placement-dans-la-grille) s'applique.

- L'**étiquette** - paramètre `title` du `QGroupBox` - est fournie par la clé `'label'` du dictionnaire interne.

```python

widgetsdict[widgetkey]['label']

```

Cette clé ne sera renseignée que s'il y a lieu d'afficher un libellé sur le groupe.

- Lorsqu'elle est renseignée, la clé `'help text'` fournit un **texte d'aide** (descriptif de la catégorie de métadonnée), qui pourrait alimenter un `toolTip` (voire un `whatsThis`).

```python

widgetsdict[widgetkey]['main widget'].setToolTip(widgetsdict[widgetkey]['help text'])

```

- La couleur du cadre du `QGroupBox` dépendra de la nature du groupe, soit de la valeur de la clé `'object'` ou plus simplement la valeur renvoyée par :

```python

widgetsdict.group_kind(widgetkey)

```

On pourra utiliser les valeurs par défaut suivantes :

| Type de groupe | `group_kind(widgetkey)` | Couleur |
| --- | --- | --- |
| Groupe de propriétés | `'group of properties'` | `'#958B62'` |
| Groupe de valeurs | `'group of values'` | `'#5770BE'` |
| Groupe de traduction | `'translation group'` | `'#FF8D7E'` |



### Paramètres spécifiques aux widgets QToolButton

Les seuls cas où le widget principal est un `QToolButton` sont ceux des "boutons plus" et "boutons de traduction", qui permettent à l'utilisateur d'ajouter réciproquement des valeurs ou traductions supplémentaires. La clé `'object'` vaut alors `'plus button'` ou `'translation button'`.

- L'image ![plus_button.svg](/plume/icons/buttons/plus_button.svg) à utiliser est toujours [plus_button.svg](/plume/icons/buttons/plus_button.svg), mais la couleur dépendra du type de groupe dans lequel se trouve le bouton, soit de la valeur renvoyée par :

```python

widgetsdict.group_kind(widgetkey)

```

Comme pour les `QGroupBox`, on pourra utiliser les valeurs par défaut suivantes :

| Type de groupe | `group_kind(widgetkey)` | Couleur |
| --- | --- | --- |
| Groupe de propriétés | `'group of properties'` | `'#958B62'` |
| Groupe de valeurs | `'group of values'` | `'#5770BE'` |
| Groupe de traduction | `'translation group'` | `'#FF8D7E'` |

*NB. En pratique, il n'y a pas de bouton plus dans les groupes de propriétés, donc la couleur associée ne sera jamais utilisée dans ce contexte.*

Soit `color` la couleur souhaitée pour le bouton et `raw_svg` le contenu du fichier *plus_button.svg*, on pourra appliquer la couleur avec :

```python

colored_svg = raw_svg.format(fill=color)

```

- Le texte d'aide à afficher en infobulle sur le bouton se trouve dans la clé `'text help'` du dictionnaire.

```python

widgetsdict[widgetkey]['text help']

```

### Paramètres spécifiques aux widgets de saisie

- Lorsqu'elle existe (car préalablement renseignée dans la fiche de métadonnées), la **valeur à afficher** dans le widget est fournie par la clé `'value'` du dictionnaire.

```python

widgetsdict[widgetkey]['value']

```

- Si la clé `'read only'` vaut `True`, le widget doit être visible mais désactivé, pour empêcher les modifications manuelles par l'utilisateur.

```python

widgetsdict[widgetkey]['read only']

```

- La clé `'is mandatory'` contient un booléen indiquant s'il est obligatoire (valeur `True`) ou non (valeur `False` ou `None`) de saisir une valeur pour la catégorie.

```python

widgetsdict[widgetkey]['is mandatory']

```
 

### Paramètres spécifiques aux widgets QLineEdit et QTextEdit

Pour les widgets d'édition de texte, le dictionnaire apporte divers paramètres complémentaires. Ils sont tous optionnels. Si la clé ne contient pas de valeur, c'est qu'il n'y a pas lieu d'utiliser le paramètre.

- `'placeholder text'` donne la **valeur fictive** à afficher dans le widget :

```python

widgetsdict[widgetkey]['main widget'].setPlaceholderText(widgetsdict[widgetkey]['placeholder text'])

```

- `'input mask'` donne le **masque de saisie** :

```python

widgetsdict[widgetkey]['main widget'].setInputMask(widgetsdict[widgetkey]['input mask'])

```

- `'type validator'` indique si un **validateur basé sur le type** doit être défini et lequel :

```python

mTypeValidator = widgetsdict[widgetkey]['type validator']

if mTypeValidator == 'QIntValidator':
    widgetsdict[widgetkey]['main widget'].setValidator(QIntValidator(widgetsdict[widgetkey]['main widget']))
elif mTypeValidator == 'QDoubleValidator':
    widgetsdict[widgetkey]['main widget'].setValidator(QDoubleValidator(widgetsdict[widgetkey]['main widget']))

```

*Ces validateurs permettent également de définir des valeurs minimum et maximum autorisées. Comme le SHACL le permet également (avec `sh:minInclusive` et `sh:maxInclusive`, car les paramètres `bottom` et `top` de `QIntValidator` et `QDoubleValidator` sont inclusifs), cette possibilité pourrait être utilisée à l'avenir, mais aucune clé n'a été prévue en ce sens à ce stade.*

- `'regex validator pattern'` donne l'**expression rationnelle** que doit respecter la valeur saisie et `'regex validator flags'` les options éventuelles :

```python

if widgetsdict[widgetkey]['regex validator pattern']:
    qre = QRegularExpression(widgetsdict[widgetkey]['regex validator pattern'])

    if widgetsdict[widgetkey]['regex validator flags']:
        if 'i' in widgetsdict[widgetkey]['regex validator flags']:
            qre.setPatternOptions(QRegularExpression.CaseInsensitiveOption)        
        if 's' in widgetsdict[widgetkey]['regex validator flags']:
            qre.setPatternOptions(QRegularExpression.DotMatchesEverythingOption)
        if 'm' in widgetsdict[widgetkey]['regex validator flags']:
            qre.setPatternOptions(QRegularExpression.MultilineOption)
        if 'x' in widgetsdict[widgetkey]['regex validator flags']:
            qre.setPatternOptions(QRegularExpression.ExtendedPatternSyntaxOption)

    widgetsdict[widgetkey]['main widget'].setValidator(
        QRegularExpressionValidator(qre, widgetsdict[widgetkey]['main widget']))

```

*Seules les options `i`, `s`, `m` et `x` sont à la fois admises en SHACL et par QT, ce sont donc les seules à être gérées.*


### Paramètres spécifiques aux widgets QComboBox

#### Liste des termes

La **liste des termes** à afficher dans le `QComboBox` est fournie par la clé `'thesaurus values'` du dictionnaire interne.

```python

widgetsdict[widgetkey]['thesaurus values']

```

Cette liste présentera toujours une chaîne de caractères vide `''` en première position, pour représenter une absence de valeur. Lors de la sauvegarde, ces chaînes de caractères vides sont traitées comme des `None`.

Autant que possible - considérant la quantité de termes dans certains thésaurus - les `QComboBox` devraient afficher une ligne de saisie avec **auto-complétion**. Il est par contre important qu'ils **ne permettent pas d'entrer d'autres valeurs que celles des thésaurus**.

#### Placeholder

Comme les `QTextEdit` et `QLineEdit`, les widgets `QComboBox` peuvent afficher une **valeur fictive** fournie par la clé `'placeholder text'`.

```python

widgetsdict[widgetkey]['main widget'].setPlaceholderText(widgetsdict[widgetkey]['placeholder text'])

```


### Paramètres spécifiques aux widgets QLabel

*NB : il n'est pas question dans cette partie des [widgets annexes d'étiquettes]((#widget-annexe--étiquette)) mais du cas où le widget principal lui-même est un QLabel.*

En mode lecture, des widgets `QLabel` remplacent la plupart des widgets de saisie (à ce jour tous sauf les `QCheckBox`). Ils permettent notamment d'afficher des hyperliens cliquables.

Comme pour les véritables widgets de saisie, la **valeur à afficher** est fournie par la clé `'value'` du dictionnaire.

```python

widgetsdict[widgetkey]['value']

```

Il importera d'activer le découpage sur plusieurs lignes :

```python

widgetsdict[widgetkey]['main widget'].setWordWrap(True)

```

Ainsi sans doute que l'ouverture automatique des liens :

```python

widgetsdict[widgetkey]['main widget'].setOpenExternalLinks(True)

```


## Widget annexe : grille

Pour les onglets, groupes de valeurs, groupes de propriétés et groupes de traduction (en fait dès lors que `'main widget type'` vaut `'QGroupBox'`), un widget annexe `QGridLayout` doit être créé en paralèlle du `QGroupBox`.

Le widget `QGridLayout` sera stocké dans la clé `'grid widget'` du dictionnaire interne.

```python

widgetsdict[widgetkey]['grid widget'] = grid
widgetsdict[widgetkey]['main widget'].setLayout(grid)

```

*Où `grid` est l'objet `QGridLayout` qui vient d'être créé.*

[↑ haut de page](#création-dun-nouveau-widget)


## Widget annexe : étiquette

Un `QLabel` doit être créé dès lors que la clé `'has label'` du dictionnaire interne vaut `True`. En pratique, cela concernera les widgets de saisie dont la clé `'label'` contient une valeur. Le libellé à afficher correspond bien entendu à la valeur de la clé `'label'`.

```python

if widgetsdict[widgetkey]['has label']:
    ...

```

### Stockage

Le widget `QLabel` sera stocké dans la clé `'label widget'` du dictionnaire interne.

```python

widgetsdict[widgetkey]['label widget'] = label_widget

```

*Où `label_widget` est le widget d'étiquette qui vient d'être créé.*

### Placement dans la grille

Le `QLabel` doit être placé dans le `QGridLayout` associé à la clé parente, obtenu grâce à la méthode `plume.rdf.widgetsdict.WidgetsDict.parent_grid`.

Les paramètres de placement du widget dans la grille - soit les arguments `row`, `column`, `rowSpan` et `columnSpan` de la méthode `QGridLayout.addWidget` - sont donnés par la méthode `plume.rdf.widgetsdict.WidgetsDict.widget_placement`.

```python

row, column, rowSpan, columnSpan = widgetsdict.widget_placement(widgetkey, 'label widget')
grid = widgetsdict.parent_grid(widgetkey)
grid.addWidget(label_widget, row, column, rowSpan, columnSpan)

```

*`label_widget` est le `QLabel` qui vient d'être créé. Le second paramètre de `widget_placement` indique que les coordonnées demandées sont celles du widget annexe d'étiquette de la clé.*

### Texte d'aide

Lorsqu'elle est renseignée, la clé `'help text'` fournit un **texte d'aide** (descriptif de la catégorie de métadonnée), qui pourrait alimenter un `toolTip` (voire un `whatsThis`).

```python

widgetsdict[widgetkey]['label widget'].setToolTip(widgetsdict[widgetkey]['help text'])

```

### Widget masqué ?

Le `QLabel` doit être masqué dès lors que la clé `'hidden'` vaut `True`.

```python

if widgetsdict[widgetkey]['hidden']:
    ...

```

[↑ haut de page](#création-dun-nouveau-widget)


## Widget annexe : bouton de sélection de la source

Un widget `QToolButton` de sélection de source doit être créé dès lors que la condition suivante est vérifiée :

```python

if widgetsdict[widgetkey]['multiple sources']:
    ...

```

### Stockage

Le widget de sélection de la source est stocké dans la clé `'switch source widget'` du dictionnaire interne.

```python

widgetsdict[widgetkey]['switch source widget'] = source_widget

```

*Où `source_widget` est le widget de sélection de la source qui vient d'être créé.*

### Menu

Le `QMenu` associé au `QToolButton` est stocké dans la clé `'switch source menu'` du dictionnaire.

```python

widgetsdict[widgetkey]['switch source menu'] = source_menu

```

*Où `source_menu` est le `QMenu` qui vient d'être créé.*

Ce `QMenu` contient une `QAction` par thésaurus utilisable pour la métadonnée. Les `QAction` sont elles-mêmes stockées dans la clé `'switch source actions'` du dictionnaire, sous la forme d'une liste.

```python

widgetsdict[widgetkey]['switch source actions'].append(source_action)

```

*Où `source_action` représente chaque `QAction` venant d'être créée.*

Les libellés des `QAction` correspondent aux noms des thésaurus et sont fournis par la liste contenue dans la clé `'sources'` du dictionnaire :

```python

widgetsdict[widgetkey]['sources']

```

*Pour la définition des actions, cf. [Actions contrôlées par les widgets du formulaire](/docs/source/usage/actions_widgets.md#boutons-de-sélection-de-la-source).*

Il serait souhaitable de mettre en évidence le thésaurus courant - celui qui fournit les valeurs du `QComboBox` - par exemple via une icône (tandis que les autres thésaurus n'en auraient pas). Le nom de ce thésaurus courant est donné par la clé `'current source'`.

```python

widgetsdict[widgetkey]['current source']

```

### Placement dans la grille

Le `QToolButton` doit être placé dans le `QGridLayout` associé à la clé parente, obtenu grâce à la méthode `plume.rdf.widgetsdict.WidgetsDict.parent_grid`.

Les paramètres de placement du widget dans la grille - soit les arguments `row`, `column`, `rowSpan` et `columnSpan` de la méthode `QGridLayout.addWidget` - sont donnés par la méthode `plume.rdf.widgetsdict.WidgetsDict.widget_placement`.

```python

row, column, rowSpan, columnSpan = widgetsdict.widget_placement(widgetkey, 'switch source widget')
grid = widgetsdict.parent_grid(widgetkey)
grid.addWidget(source_widget, row, column, rowSpan, columnSpan)

```

*`source_widget` est le `QToolButton` qui vient d'être créé. Le second paramètre de `widget_placement` indique que les coordonnées demandées sont celles du widget annexe de sélection de la source.*

### Icône

L'icône ![source_button.svg](/plume/icons/buttons/source_button.svg) à utiliser pour le bouton de sélection de la source est fournie par le fichier [source_button.svg](/plume/icons/buttons/source_button.svg). Contrairement aux boutons plus et moins, sa couleur est fixe à ce stade.

[↑ haut de page](#création-dun-nouveau-widget)


### Texte d'aide

On pourra afficher en infobulle sur le bouton le texte suivant :

```python

'Sélection du thésaurus ou mode de saisie'

```

### Widget masqué ?

Le `QToolButton` doit être masqué dès lors que la clé `'hidden'` vaut `True`.

```python

if widgetsdict[widgetkey]['hidden']:
    ...

```


## Widget annexe : bouton de sélection de la langue

Un widget `QToolButton` de sélection de langue doit être créé dès lors que la condition suivante est vérifiée (ce qui ne se produira que si le mode traduction est actif) :

```python

if widgetsdict[widgetkey]['authorized languages']:
    ...

```

### Stockage

Le bouton de sélection de la langue est stocké dans la clé `'language widget'` du dictionnaire interne.

```python

widgetsdict[widgetkey]['language widget'] = language_widget

```

*Où `language_widget` est le widget de sélection de la langue qui vient d'être créé.*

### Menu

Le `QMenu` associé au `QToolButton` est stocké dans la clé `'language menu'` du dictionnaire.

```python

widgetsdict[widgetkey]['language menu'] = language_menu

```

*Où `language_menu` est le `QMenu` qui vient d'être créé.*

Ce `QMenu` contient une `QAction` par langue disponible. Les `QAction` sont elles-mêmes stockées dans la clé `'language actions'` du dictionnaire, sous la forme d'une liste.

```python

widgetsdict[widgetkey]['language actions'].append(language_action)

```

*Où `language_action` représente chaque `QAction` venant d'être créée.*

Les libellés des `QAction` correspondent aux noms abrégés des langues et sont fournis par la liste contenue dans la clé `'authorized languages'` du dictionnaire :

```python

widgetsdict[widgetkey]['authorized languages']

```

*Pour la définition des actions, cf. [Actions contrôlées par les widgets du formulaire](/docs/source/usage/actions_widgets.md#boutons-de-sélection-de-la-langue).*

### Rendu

Au lieu d'une icône, le `QToolButton` de sélection de la langue montre un texte correspondant au nom abrégé de la langue sélectionnée. Celui-ci est fourni par la clé `'language value'`.

```python

widgetsdict[widgetkey]['language value']

```

### Texte d'aide

On pourra afficher en infobulle sur le bouton le texte suivant :

```python

'Sélection de la langue de la métadonnée'

```

### Placement dans la grille

Le `QToolButton` doit être placé dans le `QGridLayout` associé à la clé parente, obtenu grâce à la méthode `plume.rdf.widgetsdict.WidgetsDict.parent_grid`.

Les paramètres de placement du widget dans la grille - soit les arguments `row`, `column`, `rowSpan` et `columnSpan` de la méthode `QGridLayout.addWidget` - sont donnés par la méthode `plume.rdf.widgetsdict.WidgetsDict.widget_placement`.

```python

row, column, rowSpan, columnSpan = widgetsdict.widget_placement(widgetkey, 'language widget')
grid = widgetsdict.parent_grid(widgetkey)
grid.addWidget(language_widget, row, column, rowSpan, columnSpan)

```

*`language_widget` est le `QToolButton` qui vient d'être créé. Le second paramètre de `widget_placement` indique que les coordonnées demandées sont celles du widget annexe de sélection de la langue.*

### Widget masqué ?

Le `QToolButton` doit être masqué dès lors que la clé `'hidden'` vaut `True`.

```python

if widgetsdict[widgetkey]['hidden']:
    ...

```

[↑ haut de page](#création-dun-nouveau-widget)



## Widget annexe : bouton de sélection de l'unité

Un widget `QToolButton` de sélection de l'unité doit être créé dès lors que la condition suivante est vérifiée (ce qui ne se produira qu'en mode édition) :

```python

if widgetsdict[widgetkey]['units']:
    ...

```

Pour l'heure, de tels widgets ne sont utilisés que pour spécifier les unités à associer aux durées (type RDF `xsd:duration`).

### Stockage

Le bouton de sélection de l'unité est stocké dans la clé `'unit widget'` du dictionnaire interne.

```python

widgetsdict[widgetkey]['unit widget'] = unit_widget

```

*Où `unit_widget` est le widget de sélection de l'unité qui vient d'être créé.*

### Menu

Le `QMenu` associé au `QToolButton` est stocké dans la clé `'unit menu'` du dictionnaire.

```python

widgetsdict[widgetkey]['unit menu'] = unit_menu

```

*Où `unit_menu` est le `QMenu` qui vient d'être créé.*

Ce `QMenu` contient une `QAction` par unité disponible. Les `QAction` sont elles-mêmes stockées dans la clé `'unit actions'` du dictionnaire, sous la forme d'une liste.

```python

widgetsdict[widgetkey]['unit actions'].append(unit_action)

```

*Où `unit_action` représente chaque `QAction` venant d'être créée.*

Les libellés des `QAction` correspondent aux noms abrégés des langues et sont fournis par la liste contenue dans la clé `'units'` du dictionnaire :

```python

widgetsdict[widgetkey]['units']

```

*Pour la définition des actions, cf. [Actions contrôlées par les widgets du formulaire](/docs/source/usage/actions_widgets.md#boutons-de-sélection-de-lunité).*

### Rendu

Au lieu d'une icône, le `QToolButton` de sélection de l'unité montre un texte correspondant à l'unité sélectionnée. Celui-ci est fourni par la clé `'current unit'`.

```python

widgetsdict[widgetkey]['current unit']

```

### Texte d'aide

On pourra afficher en infobulle sur le bouton le texte suivant :

```python

'Sélection de l'unité de mesure'

```

### Placement dans la grille

Le `QToolButton` doit être placé dans le `QGridLayout` associé à la clé parente, obtenu grâce à la méthode `plume.rdf.widgetsdict.WidgetsDict.parent_grid`.

Les paramètres de placement du widget dans la grille - soit les arguments `row`, `column`, `rowSpan` et `columnSpan` de la méthode `QGridLayout.addWidget` - sont donnés par la méthode `plume.rdf.widgetsdict.WidgetsDict.widget_placement`.

```python

row, column, rowSpan, columnSpan = widgetsdict.widget_placement(widgetkey, 'unit widget')
grid = widgetsdict.parent_grid(widgetkey)
grid.addWidget(unit_widget, row, column, rowSpan, columnSpan)

```

*`unit_widget` est le `QToolButton` qui vient d'être créé. Le second paramètre de `widget_placement` indique que les coordonnées demandées sont celles du widget annexe de sélection de l'unité.*

### Widget masqué ?

Le `QToolButton` doit être masqué dès lors que la clé `'hidden'` vaut `True`.

```python

if widgetsdict[widgetkey]['hidden']:
    ...

```

[↑ haut de page](#création-dun-nouveau-widget)


## Widget annexe : bouton d'aide à la saisie des géométries

Un widget `QToolButton` d'aide à la saisie des géométries doit être créé dès lors que la condition suivante est vérifiée (ce qui ne se produira qu'en mode édition) :

```python

if widgetsdict[widgetkey]['geo tools']:
    ...

```

De tels widgets accompagnent les widgets de saisie appelant des valeurs de type `gsp:wktLiteral`.

### Stockage

Le bouton d'aide à la saisie des géométries est stocké dans la clé `'geo widget'` du dictionnaire interne.

```python

widgetsdict[widgetkey]['geo widget'] = geo_widget

```

*Où `geo_widget` est le widget d'aide à la saisie des géométries qui vient d'être créé.*

### Menu

Le `QMenu` associé au `QToolButton` est stocké dans la clé `'geo menu'` du dictionnaire.

```python

widgetsdict[widgetkey]['geo menu'] = geo_menu

```

*Où `geo_menu` est le `QMenu` qui vient d'être créé.*

Ce `QMenu` contient une `QAction` par fonction d'assistance disponible. Les `QAction` sont elles-mêmes stockées dans la clé `'geo actions'` du dictionnaire, sous la forme d'une liste.

```python

widgetsdict[widgetkey]['geo actions'].append(geo_action)

```

*Où `geo_action` représente chaque `QAction` venant d'être créée.*

### Description des actions

La nature des actions disponibles dépend de la propriété considérée. Elles peuvent être déduite des valeurs listées par la clé `'geo tools'`.

| Valeur incluse dans `'geo tools'` | Libellé de l'action | Texte d'aide | Description de l'effet |
| --- | --- | --- | --- |
| `'point'` | Tracé libre (point) | Saisie libre d'un point dans le canvas. | Permet à l'utilisateur de cliquer sur un point dans le canvas et mémorise la géométrie dans les métadonnées. |
| `'rectangle'` | Tracé libre (rectangle) | Saisie libre d'un rectangle dans le canvas. | Permet à l'utilisateur de tracer un rectangle dans le canvas et mémorise la géométrie dans les métadonnées. |
| `'linestring'` | Tracé libre (ligne) | Saisie libre d'une ligne dans le canvas.  | Permet à l'utilisateur de tracer une ligne dans le canvas et mémorise la géométrie dans les métadonnées. |
| `'polygon'` | Tracé libre (polygone) | Saisie libre d'un polygone dans le canvas. | Permet à l'utilisateur de tracer un polygone dans le canvas et mémorise la géométrie dans les métadonnées. |
| `'bbox'` | Calcul à partir des données (emprise) | Calcule le rectangle d'emprise à partir des données. | Calcule l'emprise de la couche grâce aux méthodes de QGIS (`QgsVectorLayer.extent`) et mémorise la géométrie dans les métadonnées. _NB : Cette option ne sera disponible que si le paramètre `isLayer` donné au constructeur de `plume.rdf.widgetsdict.WidgetDict` valait ``True``._ |
| `'centroid'` | Calcul à partir des données (centroïde) | Calcule le centre du rectangle d'emprise à partir des données. | Calcule l'emprise de la couche grâce aux méthodes de QGIS (`QgsVectorLayer.extent`), puis le centre du rectangle (`QgsRectangle.centre`), et mémorise la géométrie dans les métadonnées. _NB : Cette option ne sera disponible que si le paramètre `isLayer` donné au constructeur de `plume.rdf.widgetsdict.WidgetDict` valait ``True``._ |

Contrairement à tous les autres boutons du formulaire, le bouton d'aide à la saisie des géométries n'affecte pas le dictionnaire. La géométrie obtenue sera simplement saisie dans le `QLineEdit` ou `QTextEdit`, après les deux opérations suivantes :
1. Conversion au format WKT, avec les méthodes `QgsRectangle.asWktPolygon`, `QgsPointXY.asWkt`, etc. de QGIS.
2. Explicitation du système de coordonnées, car c'est ce qui est attendu en RDF pour les valeurs de type `gsp:wktLiteral`. On utilisera pour ce faire la fonction `plume.rdf.utils.wkt_with_srid`.

```python

from plume.rdf.utils import wkt_with_srid

geom_wkt = wkt_with_srid(raw_wkt, srid)

```

*Où `raw_wkt` est le résultat de la conversion de la géométrie en WKT et `srid` le référentiel de coordonnées courant de la couche (pour les fonctionnalités de calcul automatisé) ou du canvas (pour les fonctionnalités de tracé libre).*

Les valeurs résultantes seront de cette forme : `'<http://www.opengis.net/def/crs/EPSG/0/2154> POINT(651796.3281 6862298.5858)'`.

### Icône

*À venir.*

### Texte d'aide

On pourra afficher en infobulle sur le bouton le texte suivant :

```python

'Aide à la saisie des géométries'

```

### Placement dans la grille

Le `QToolButton` doit être placé dans le `QGridLayout` associé à la clé parente, obtenu grâce à la méthode `plume.rdf.widgetsdict.WidgetsDict.parent_grid`.

Les paramètres de placement du widget dans la grille - soit les arguments `row`, `column`, `rowSpan` et `columnSpan` de la méthode `QGridLayout.addWidget` - sont donnés par la méthode `plume.rdf.widgetsdict.WidgetsDict.widget_placement`.

```python

row, column, rowSpan, columnSpan = widgetsdict.widget_placement(widgetkey, 'geo widget')
grid = widgetsdict.parent_grid(widgetkey)
grid.addWidget(geo_widget, row, column, rowSpan, columnSpan)

```

*`geo_widget` est le `QToolButton` qui vient d'être créé. Le second paramètre de `widget_placement` indique que les coordonnées demandées sont celles du widget annexe d'aide à la saisie des géométries.*

### Widget masqué ?

Le `QToolButton` doit être masqué dès lors que la clé `'hidden'` vaut `True`.

```python

if widgetsdict[widgetkey]['hidden']:
    ...

```

[↑ haut de page](#création-dun-nouveau-widget)



## Widget annexe : bouton "moins"

Pour les propriétés admettant des valeurs multiples ou des traductions, des widgets `QToolButton` permettent à l'utilisateur de supprimer les valeurs précédemment saisies, à condition qu'il en reste au moins une.

Un tel widget doit être créé dès lors que la condition suivante est vérifiée :

```python

if widgetsdict[widgetkey]['has minus button']:
    ...

```

### Stockage

Le boutoin moins est stocké dans la clé `'minus widget'` du dictionnaire interne.

```python

widgetsdict[widgetkey]['minus widget'] = minus_widget

```

*Où `minus_widget` est le widget de sélection de la source qui vient d'être créé.*

### Placement dans la grille

Le `QToolButton` doit être placé dans le `QGridLayout` associé à la clé parente, obtenu grâce à la méthode `plume.rdf.widgetsdict.WidgetsDict.parent_grid`.

Les paramètres de placement du widget dans la grille - soit les arguments `row`, `column`, `rowSpan` et `columnSpan` de la méthode `QGridLayout.addWidget` - sont donnés par la méthode `plume.rdf.widgetsdict.WidgetsDict.widget_placement`.

```python

row, column, rowSpan, columnSpan = widgetsdict.widget_placement(widgetkey, 'minus widget')
grid = widgetsdict.parent_grid(widgetkey)
grid.addWidget(minus_widget, row, column, rowSpan, columnSpan)

```

*`minus_widget` est le `QToolButton` qui vient d'être créé. Le second paramètre de `widget_placement` indique que les coordonnées demandées sont celles du boutoin moins.*

### Icône

L'image ![minus_button.svg](/plume/icons/buttons/minus_button.svg) à utiliser pour un bouton moins est toujours [minus_button.svg](/plume/icons/buttons/minus_button.svg), mais la couleur dépendra du type de groupe dans lequel se trouve le bouton, soit de la valeur renvoyée par :

```python

widgetsdict.group_kind(widgetkey)

```

Comme pour les `QGroupBox` et les boutons plus/boutons de traduction, on pourra utiliser les valeurs par défaut suivantes :

| Type de groupe | `group_kind(widgetkey)` | Couleur |
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

Comme tous les autres widgets, le `QToolButton` doit être masqué dès lors que la clé `'hidden'` vaut `True`. Mais il devra également être masqué si le groupe de traduction ou groupe de valeurs ne contient qu'un élément, soit quand `'hide minus button'` vaut `True`.

```python

if widgetsdict[widgetkey]['hidden'] or widgetsdict[widgetkey]['hide minus button']:
    ...

```

[↑ haut de page](#création-dun-nouveau-widget)
