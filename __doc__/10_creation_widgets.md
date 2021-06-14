### Création d'un nouveau widget

*Soit :*
- *`widgetsDict` le dictionnaire contenant tous les widgets et leurs informations de paramétrage.*
- *`key` la clé de l'enregistrement en cours de traitement.*

Chaque enregistrement du dictionnaire des widgets contrôle un widget principal et, le cas échéant, un ou plusieurs widgets annexes.

 
## Widget principal

# Type

Le type de widget à créer (QGroupBox, QToolButton, QLineEdit...) est fourni par la clé `'main widget type'` du dictionnaire interne.

```python

widgetsDict[key]['main widget type']

```

# Stockage

Le nouveau widget a vocation à être stocké dans la clé `'main widget'` du dictionnaire interne.

```python

widgetsDict[key]['main widget']

```

# Paramètre *parent*

Le widget *parent* est le `'main widget'` de l'enregistrement dont la clé est le second argument de `key`. Il s'agira toujours d'un QGroupBox.

Par exemple, si `key` vaut `(2, (5, (0,)))`,  son parent est le widget principal de la clé `(5, (0,))`.

```python

widgetsDict[key[1]]['main widget']

```

# Paramètres spécifiques aux widgets QGroupBox

Le paramètre *title* du QGroupBox est fourni par la clé `'label'` du dictionnaire interne.

Cette clé ne sera renseignée que s'il y a lieu d'afficher un libellé sur le groupe.

```python

widgetsDict[key]['label']

```

# Paramètres spécifiques aux widgets de saisie

Lorsqu'elle existe, soit parce qu'elle était déjà renseignée dans la fiche de métadonnées, soit parce qu'une valeur par défaut est définie pour la catégorie considérée, la valeur à afficher dans le widget est fournie par la clé `'value'` du dictionnaire.

```python

widgetsDict[key]['value']

```

# Paramètres spécifiques aux widgets QLineEdit et QTextEdit

Pour les widgets d'édition de texte, le dictionnaire apporte divers paramètres complémentaires :

- la clé `'placeholder text'` fournit le paramètre *placeholderText* ;
- 

Tous ces paramètres sont optionnels. Si la clé ne contient pas de valeur, c'est qu'il n'y a pas lieu d'utiliser le paramètre.


# Placement dans la grille

Le nouveau widget doit être placé dans le QGridLayout associé à son parent.

```python

widgetsDict[key[1]]['grid widget']

```

Son placement vertical (paramètre *row* de la méthode addWidget) est donné par la clé `'row'` du dictionnaire interne.

```python

widgetsDict[key]['row']

```

**Pour les widgets QTextEdit uniquement**, La hauteur du widget (paramètre *row span*) est fournie par la clé `'row span'` du dictionnaire interne.

```python

widgetsDict[key]['row span']

```

Le placement horizontal (paramètre *column*) et la largeur du widget (paramètre *column span*) ne sont pas définis par le dictionnaire à ce stade, mais pourraient l'être à l'avenir. D'une manière générale, *column* vaudra 0 sauf pour un widget de saisie tel qu'une étiquette est placée sur la même ligne. *column span* dépendra de la présence d'une étiquette et/ou de boutons "moins" ou de sélection de la source.


## Widget annexe : grille

Pour les groupes de valeurs, groupes de propriétés et groupes de traduction, un widget annexe QGridLayout doit être créé en paralèlle du QGroupBox.

```python

widgetsDict[key]['object'] in ('group of values', 'group of properties', 'translation group')

```

# Stockage

Le widget QGridLayout sera stocké dans la clé `'grid widget'` du dictionnaire interne.

```python

widgetsDict[key]['grid widget']

```

# Paramètre *parent*

Le widget *parent* est le `'main widget'` de l'enregistrement.

```python

widgetsDict[key]['main widget']

```

## Widget annexe : étiquette

Pour les widgets de saisie uniquement, un QLabel doit être créé dès lors que la clé `'label'` du dictionnaire interne n'est pas nulle. Le libellé à afficher correspond bien entendu à la valeur de la clé `'label'`.

```python

widgetsDict[key]['label']

```

# Stockage

Le widget QLabel sera stocké dans la clé `'label widget'` du dictionnaire interne.

```python

widgetsDict[key]['label widget']

```

# Paramètre *parent*

Le widget *parent* est le même que pour le widget principal : il s'agit du `'main widget'` de l'enregistrement dont la clé est le second argument de `key`.


```python

widgetsDict[key[1]]['main widget']

```

# Placement dans la grille

Le QLabel doit être placé dans le QGridLayout associé à son parent.

```python

widgetsDict[key[1]]['grid widget']

```

Son placement vertical (paramètre *row* de la méthode addWidget) est donné par :
- la clé `'label row'` si elle n'est pas vide. Cela correspond au cas où le label doit être positionné au-dessus de la zone de saisie ;
- sinon la clé `'row'`. Dans ce cas le label et la zone de saisie sont toujours positionnés sur la même ligne.

```python

widgetsDict[key]['label row'] or widgetsDict[key]['row']

```

Le paramètre *column* vaut toujours 0.

Le paramètre *column span* n'est pas défini par le dictionnaire à ce stade, mais pourrait l'être à l'avenir.



## Widget annexe : bouton "moins"

## Infobulle

## Visibilité des widgets



