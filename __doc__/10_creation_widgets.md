# Création d'un nouveau widget

Soit :
- `widgetsDict` le dictionnaire contenant tous les widgets et leurs informations de paramétrage.
- `key` la clé de l'enregistrement en cours de traitement.

Chaque enregistrement du dictionnaire des widgets contrôle un widget principal et, le cas échéant, un ou plusieurs widgets annexes.

[Widget principal](#widget-principal) • [Widget annexe : grille](#widget-annexe--grille) • [Widget annexe : étiquette](#widget-annexe--étiquette) • [Wdget annexe : bouton de sélection de la source](#widget-annexe--bouton-de-selection-de-la-source) • [Widget annexe : bouton de sélection de la langue](#widget-annexe--bouton-de-selection-de-la-langue) • [Widget annexe : bouton "moins"](#widget-annexe--bouton-moins)

 
## Widget principal

### Type

Le type du widget principal (QGroupBox, QToolButton, QLineEdit...) est fourni par la clé `'main widget type'` du dictionnaire interne.

```python

widgetsDict[key]['main widget type']

```

### Stockage

Le nouveau widget a vocation à être stocké dans la clé `'main widget'` du dictionnaire interne.

```python

widgetsDict[key]['main widget']

```

### Parent

Le widget *parent* est le `'main widget'` de l'enregistrement dont la clé est le second argument du tuple `key`. Il s'agira toujours d'un QGroupBox.

Par exemple, si `key` vaut `(2, (5, (0,)))`,  son parent est le widget principal de la clé `(5, (0,))`.

```python

widgetsDict[key[1]]['main widget']

```

### Paramètres spécifiques aux widgets QGroupBox

Le paramètre *title* du QGroupBox est fourni par la clé `'label'` du dictionnaire interne.

Cette clé ne sera renseignée que s'il y a lieu d'afficher un libellé sur le groupe.

```python

widgetsDict[key]['label']

```

Lorsqu'elle est renseignée, la clé `'help text'` fournit un descriptif de la catégorie de métadonnée, qui pourrait apparaître en infobulle.

```python

widgetsDict[key]['help text']

```

### Paramètres spécifiques aux widgets de saisie

Lorsqu'elle existe, soit parce qu'elle était déjà renseignée dans la fiche de métadonnées, soit parce qu'une valeur par défaut est définie pour la catégorie considérée, la valeur à afficher dans le widget est fournie par la clé `'value'` du dictionnaire.

À noter que les valeurs par défaut ne sont utilisées que si le groupe de propriétés est vide.

```python

widgetsDict[key]['value']

```

Si la clé `'read only'` vaut `True`, le widget doit être visible mais désactivé, pour empêcher les modifications manuelles par l'utilisateur.

```python

widgetsDict[key]['read only']

```

La clé `'is mandatory'` contient un booléen indiquant s'il est obligatoire (valeur `True`) ou non (valeur `False` ou `None`) de saisir une valeur pour la catégorie.

```python

widgetsDict[key]['is mandatory']

```
 

### Paramètres spécifiques aux widgets QLineEdit et QTextEdit

Pour les widgets d'édition de texte, le dictionnaire apporte divers paramètres complémentaires. Ils sont tous optionnels. Si la clé ne contient pas de valeur, c'est qu'il n'y a pas lieu d'utiliser le paramètre.

- `'placeholder text'` donne la valeur fictive à afficher dans le widget :

```python

widgetsDict[key]['main widget'].setPlaceholderText(widgetsDict[key]['placeholder text'])

```

- `'input mask'` donne le masque de saisie :

```python

widgetsDict[key]['main widget'].setInputMask(widgetsDict[key]['input mask'])

```

- `'type validator'` indique si un validateur basé sur le type doit être défini et lequel :

```python

widgetsDict[key]['type validator'] = mTypeValidator

if mTypeValidator == 'QIntValidator':
    widgetsDict[key]['main widget'].setValidator(QIntValidator(widgetsDict[key]['main widget']))
elif mTypeValidator == 'QDoubleValidator':
    widgetsDict[key]['main widget'].setValidator(QDoubleValidator(widgetsDict[key]['main widget']))

```

*Ces validateurs permettent également de définir des valeurs minimum et maximum autorisées. Comme le SHACL le permet également (avec `sh:minInclusive` et `sh:maxInclusive`, car les paramètres `bottom` et `top` de `QIntValidator()` et `QDoubleValidator()` sont inclusifs), cette possibilité pourrait être utilisée à l'avenir, mais aucune clé n'a été prévue en ce sens à ce stade.*

- `'regex validator pattern'` donne l'expression rationnelle que doit respecter la valeur saisie et `'regex validator flags'` les options éventuelles :

```python

re = QRegularExpression(widgetsDict[key]['regex validator pattern'])

if "i" in widgetsDict[key]['regex validator flags']:
    re.setPatternOptions(QRegularExpression.CaseInsensitiveOption)
    
if "s" in widgetsDict[key]['regex validator flags']:
    re.setPatternOptions(QRegularExpression.DotMatchesEverythingOption)

if "m" in widgetsDict[key]['regex validator flags']:
    re.setPatternOptions(QRegularExpression.MultilineOption)
    
if "x" in widgetsDict[key]['regex validator flags']:
    re.setPatternOptions(QRegularExpression.ExtendedPatternSyntaxOption)

widgetsDict[key]['main widget'].setValidator(
    QRegularExpressionValidator(re),
    widgetsDict[key]['main widget'])
    )

```

*Seules les options `i`, `s`, `m` et `x` sont à la fois admises en SHACL et par QT, ce sont donc les seules à être gérées.*



### Placement dans la grille

Le nouveau widget doit être placé dans le QGridLayout associé à son parent.

```python

widgetsDict[key[1]]['grid widget']

```

Son placement vertical (paramètre *row* de la méthode addWidget) est donné par la clé `'row'` du dictionnaire interne.

```python

widgetsDict[key]['row']

```

**Pour les widgets QTextEdit uniquement**, La hauteur du widget (paramètre `row span`) est fournie par la clé `'row span'` du dictionnaire interne.

```python

widgetsDict[key]['row span']

```

*Le placement horizontal (paramètre `column`) et la largeur du widget (paramètre `column span`) ne sont pas explicitement définis par le dictionnaire à ce stade, mais pourraient l'être à l'avenir.*

D'une manière générale, `column` vaudra `0`, sauf pour un widget de saisie tel qu'une étiquette est placée sur la même ligne. Dans ce cas, `column` vaut `1`.

```python

column = 1 if widgetsDict[key]['label'] and widgetsDict[key]['label row'] is None else 0

```

*`column span` pourrait dépendre de la présence d'une étiquette et/ou de boutons "moins" ou de sélection de la source.*

[↑ haut de page](#création-dun-nouveau-widget)



## Widget annexe : grille

Pour les groupes de valeurs, groupes de propriétés et groupes de traduction, un widget annexe QGridLayout doit être créé en paralèlle du QGroupBox.

```python

widgetsDict[key]['object'] in ('group of values', 'group of properties', 'translation group')

```

### Stockage

Le widget QGridLayout sera stocké dans la clé `'grid widget'` du dictionnaire interne.

```python

widgetsDict[key]['grid widget']

```

### Parent

Le widget *parent* est le `'main widget'` de l'enregistrement.

```python

widgetsDict[key]['main widget']

```

[↑ haut de page](#création-dun-nouveau-widget)



## Widget annexe : étiquette

**Pour les widgets de saisie uniquement**, un QLabel doit être créé dès lors que la clé `'label'` du dictionnaire interne n'est pas nulle. Le libellé à afficher correspond bien entendu à la valeur de la clé `'label'`.

```python

widgetsDict[key]['label']

```

### Stockage

Le widget QLabel sera stocké dans la clé `'label widget'` du dictionnaire interne.

```python

widgetsDict[key]['label widget']

```

### Parent

Le widget *parent* est le même que pour le widget principal : il s'agit du `'main widget'` de l'enregistrement dont la clé est le second argument de `key`.

```python

widgetsDict[key[1]]['main widget']

```

### Placement dans la grille

Le QLabel doit être placé dans le QGridLayout associé à son parent.

```python

widgetsDict[key[1]]['grid widget']

```

Son placement vertical (paramètre `row` de la méthode addWidget) est donné par :
- la clé `'label row'` si elle n'est pas vide. Cela correspond au cas où le label doit être positionné au-dessus de la zone de saisie ;
- sinon la clé `'row'`. Dans ce cas le label et la zone de saisie sont toujours placés sur la même ligne.

Le paramètre `column` vaut toujours 0.

```python

row = widgetsDict[key]['label row'] or widgetsDict[key]['row']
column = 0

```

*Le paramètre `column span` n'est pas défini par le dictionnaire à ce stade, mais pourrait l'être à l'avenir.*

[↑ haut de page](#création-dun-nouveau-widget)




## Widget annexe : bouton de sélection de la source

Un widget QToolButton de sélection de source doit être créé dès lors que la condition suivante est vérifiée :

```python

widgetsDict[key]['multiple sources']

```

### Stockage

Il est stocké dans la clé `'switch source widget'` du dictionnaire interne.

```python

widgetsDict[key]['switch source widget']

```

### Parent

Le widget *parent* est le même que pour le widget principal : il s'agit du `'main widget'` de l'enregistrement dont la clé est le second argument de `key`.

```python

widgetsDict[key[1]]['main widget']

```

### Placement dans la grille

Le QToolButton doit être placé dans le QGridLayout associé à son parent.

```python

widgetsDict[key[1]]['grid widget']

```

Le bouton de sélection de la source est toujours positionné immédiatement à droite de la zone de saisie.

```python

row = widgetsDict[key]['row']
column = 2 if widgetsDict[key]['label'] and widgetsDict[key]['label row'] is None else 1

```

Il n'y a a priori pas lieu de spécifier les paramètres `row span` et `column span`.

[↑ haut de page](#création-dun-nouveau-widget)



## Widget annexe : bouton  de sélection de la langue

Un widget QToolButton de sélection de source doit être créé dès lors que la condition suivante est vérifiée :

```python

widgetsDict[key]['authorized languages']

```

### Stockage

Il est stocké dans la clé `'language widget'` du dictionnaire interne.

```python

widgetsDict[key]['language widget']

```

### Parent

Le widget *parent* est le même que pour le widget principal : il s'agit du `'main widget'` de l'enregistrement dont la clé est le second argument de `key`.

```python

widgetsDict[key[1]]['main widget']

```

### Placement dans la grille

Le QToolButton doit être placé dans le QGridLayout associé à son parent.

```python

widgetsDict[key[1]]['grid widget']

```

Le bouton de sélection de la source est toujours positionné immédiatement à droite de la zone de saisie.

```python

row = widgetsDict[key]['row']
column = 2 if widgetsDict[key]['label'] and widgetsDict[key]['label row'] is None else 1

```

Il n'y a a priori pas lieu de spécifier les paramètres `row span` et `column span`.

[↑ haut de page](#création-dun-nouveau-widget)



## Widget annexe : bouton "moins"

Pour les propriétés admettant des valeurs multiples ou des traductions, des widgets QToolButton permettent à l'utilisateur de supprimer les valeurs.

Un tel widget doit être créé dès lors que la condition suivante est vérifiée :

```python

widgetsDict[key]['has minus button']

```

### Stockage

Il est stocké dans la clé `'minus widget'` du dictionnaire interne.

```python

widgetsDict[key]['minus widget']

```

### Parent

Le widget *parent* est le même que pour le widget principal : il s'agit du `'main widget'` de l'enregistrement dont la clé est le second argument de `key`.

```python

widgetsDict[key[1]]['main widget']

```

### Placement dans la grille

Le QToolButton doit être placé dans le QGridLayout associé à son parent.

```python

widgetsDict[key[1]]['grid widget']

```

Le bouton "moins" est positionné sur la ligne de la zone de saisie, à droite du bouton de sélection de la source / de la langue s'il y en a un, sinon immédiatement à droite de la zone de saisie. À noter que, par construction, il ne peut jamais y avoir à la fois un bouton de sélection de la langue et un bouton de sélection de la source.

```python

row = widgetsDict[key]['row']
column = ( 2 if widgetsDict[key]['label'] and widgetsDict[key]['label row'] is None else 1 ) \
    + ( 1 if widgetsDict[key]['multiple sources'] else 0 ) \
    + ( 1 if widgetsDict[key]['authorized languages'] else 0 )

```

Il n'y a a priori pas lieu de spécifier les paramètres `row span` et `column span`.

[↑ haut de page](#création-dun-nouveau-widget)
