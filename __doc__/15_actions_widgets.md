# Actions contrôlées par les widgets du formulaire

En plus d'être généré à la volée, le formulaire de saisie des métadonnées est dynamique. L'utilisateur peut déclencher des actions qui auront pour effet d'afficher ou masquer des widgets, d'en créer, d'en supprimer, de modifier des menus...

Toutes ces actions impliquent en premier lieu de mettre à jour le dictionnaire de widgets, grâce à des méthodes de la classe `WidgetsDict` qui renvoient les informations nécessaires pour, en second lieu, réaliser les opérations qui s'imposent sur les widgets eux-mêmes.

Pour les interactions de l'utilisateur avec la partie "fixe" de l'interface (sauvegarde, import, export, modification des paramètres utilisateur, etc.), on se reportera à [Actions générales](/__doc__/16_actions_generales.md).

[Boutons "plus" et boutons de traduction](#boutons-plus-et-boutons-de-traduction) • [Boutons "moins"](#boutons-moins) • [Boutons de sélection de la source](#boutons-de-sélection-de-la-source) • [Boutons de sélection de la langue](#boutons-de-sélection-de-la-langue)


## Boutons "plus" et boutons de traduction

Un bouton "plus" est un widget QToolButton qui, lorsqu'il est activé par l'utilisateur, permet d'ajouter une valeur dans un groupe de valeurs.

![gv_bouton_plus](/__doc__/schemas/gv_bouton_plus.png)

Un bouton de traduction est un QToolButton qui permet d'ajouter une traduction dans un groupe de traductions.

![gt_bouton_de_traduction](/__doc__/schemas/gt_bouton_de_traduction.png)

Ces deux types de boutons sont considérés ensemble, car le traitement à prévoir est le même (les méthodes utilisées n'auront pas exactement le même effet, mais c'est transparent).

Soit `key` la clé du bouton "plus" ou bouton de traduction considéré dans le dictionnaire de widgets `widgetsdict`.

### Mise à jour du dictionnaire des widgets

Lors de l'activation du bouton, il faudra commencer par exécuter la commande de mise à jour du dictionnaire (méthode `add()`) :

```python

r = widgetsdict.add(key, language, langList)

```

*`language` et `langList` sont les paramètres utilisateur qui spécifient réciproquement la langue principale de saisie et la liste des langues autorisées pour les traductions. Ils prennent des valeurs identiques pour tous les boutons "plus" et celles-ci peuvent être considérées comme fixes pour toute la durée de la saisie, dans la mesure où tout changement nécessiterait de regénérer intrégralement le dictionnaire des widgets et, par suite, le formulaire.*

### ... puis du formulaire

Les informations renvoyées par `add()` permettent de réaliser les opérations subséquentes sur les widgets.

Le résultat, ici `r`, est un dictionnaire à cinq clés :

- `"widgets to show"` contient une liste de widgets (QWidget) jusque-là masqués qu'il s'agit maintenant d'afficher.

    *Concrètement, cette liste, si elle n'est pas vide, contiendra des widgets QToolButton correspondant à des boutons "moins" (lorsqu'il ne reste qu'un objet dans un groupe, son bouton "moins" disparaît pour empêcher sa suppression, il doit être ré-affiché si un nouvel objet est ajouté).*
    
- Inversement, `"widgets to hide"` contient une liste de widgets (QWidget) qui devront être masqués.

    *La liste sera toujours vide pour un bouton "plus". Pour un bouton de traduction, elle pourra contenir le QToolButton du bouton "plus" lui-même si toutes les langues disponibles pour les traductions sont maintenant utilisées, et qu'il n'y a donc plus lieu d'ajouter des traductions supplémentaires.*
    
- `"widgets to move"` fournit une liste de tuples contenant les informations relatives à des widgets dont - parce qu'on a ajouté un widget au-dessus d'eux dans la grille - il faut à présent modifier la position :
    - `[0]` est la grille concernée (QGridLayout).
    - `[1]` est le widget lui-même (QWidget).
    - `[2]` est le nouveau numéro de ligne/valeur du paramètre `row` pour le widget dans la grille.
    
    *Concrètement, cela concerne systématiquement et exclusivement le bouton plus ou bouton de traduction lui-même.*
    
- `"language menu to update"` contient une liste de clés du dictionnaire de widgets (et non directement des widgets, cette fois), pour lesquelles le menu des langues doit être régénéré. Comme lors de la création initiale du formulaire, la liste (mise à jour) des langues à faire apparaître dans ce menu est contenue dans la clé `"authorized languages"` du dictionnaire interne pour la clé fournie.

    *En pratique, cette liste sera toujours vide pour le bouton "plus" d'un groupe de valeur. Dans un groupe de traduction, ajouter une traduction implique que la langue de celle-ci n'est plus disponible et doit donc être supprimée des menus des boutons de sélection de la langue qui accompagnent tous les widgets de saisie du groupe. Cf. [Création d'un nouveau widget](/__doc__/10_creation_widgets.md#widget-annexe--bouton-de-sélection-de-la-langue) pour plus de détails sur la génération des menus de langues.*

- `"new keys"` contient une liste de clés qui viennent d'être ajoutées au dictionnaire, et pour lesquelles il faudra donc implémenter tous les widgets. La marche à suivre est la même que lors de la génération initiale du formulaire. Cf. [Création d'un nouveau widget](/__doc__/10_creation_widgets.md). 


## Boutons "moins"

Les boutons "moins" existent à la fois dans les groupes de valeurs et dans les groupes de traduction. Dans les deux cas, ce sont des QToolButton dont l'activation permet à l'utilisateur de faire disparaître des zones de saisie excédentaires.

*NB : une telle opération a pour seul intérêt le confort visuel de l'utilisateur et, lorsqu'il s'agit de retirer une branche complète et pas juste un widget de saisie, de lui éviter de devoir supprimer à la main un potentiellement grand nombre de valeurs. Du point de vue des fonctions de RDF Utils, la présence de widgets vides n'a aucune espèce d'importance.*

![gv_bouton_moins](/__doc__/schemas/gv_bouton_moins.png) ![gt_bouton_moins](/__doc__/schemas/gt_bouton_moins.png)

Soit `key` la clé du bouton "moins" considéré dans le dictionnaire de widgets `widgetsdict`.

### Mise à jour du dictionnaire des widgets

Lors de l'activation du bouton, il faudra commencer par exécuter la commande de mise à jour du dictionnaire (méthode `drop()`) :

```python

r = widgetsdict.drop(key, langList)

```

*`langList` est le paramètre utilisateur qui spécifie la liste des langues autorisées pour les traductions. Il prend une valeur identique pour tous les boutons "moins" et celle-ci peut être considérée comme fixe pour toute la durée de la saisie, dans la mesure où tout changement nécessiterait de regénérer intrégralement le dictionnaire des widgets et, par suite, le formulaire.*

### ... puis du formulaire

Les informations renvoyées par `drop()` permettent de réaliser les opérations subséquentes sur les widgets.

Le résultat, ici `r`, est un dictionnaire à sept clés :

- `"widgets to delete"` contient une liste de widgets (QWidget) à détruire.
    
    *Ces widgets ne sont plus référencés dans le dictionnaire, il ne sera donc plus jamais possible d'interagir avec eux. Les supprimer paraît la meilleure chose à faire.*

- Dans la même veine, `"actions to delete"` contient la liste des objets QAction à détruire.

- `"menus to delete"` contient la liste des objets QMenu à détruire.

- `"widgets to show"` contient une liste de widgets (QWidget) jusque-là masqués qu'il s'agit maintenant d'afficher.

    *Cette liste sera toujours vide pour un bouton "moins" dans un groupe de valeur. Dans un groupe de traduction, elle pourra contenir le QToolButton du bouton "plus" du groupe si retirer une traduction fait que toutes les langues ne sont désormais plus utilisées, et qu'il est donc de nouveau possible d'ajouter des traductions supplémentaires.*
    
- Inversement, `"widgets to hide"` contient une liste de widgets (QWidget) qui devront être masqués.

   *Concrètement, cette liste, si elle n'est pas vide, contiendra des widgets QToolButton correspondant à des boutons "moins" qui doivent être masqués parce qu'il ne reste plus qu'un élément dans le groupe de valeurs ou de traductions (et qu'il n'est pas permis à l'utilisateur de supprimer le dernier élément d'un groupe).*
    
- `"language menu to update"` contient une liste de clés du dictionnaire de widgets (et non directement des widgets, cette fois), pour lesquelles le menu des langues doit être régénéré. Comme lors de la création initiale du formulaire, la liste (mise à jour) des langues à faire apparaître dans ce menu est contenue dans la clé `"authorized languages"` du dictionnaire interne pour la clé fournie.

    *En pratique, cette liste sera toujours vide pour un bouton "moins" dans un groupe de valeur. Dans un groupe de traduction, supprimer une traduction implique que la langue de celle-ci (sous réserve qu'elle ait été autorisée au départ) est de nouveau disponible et doit donc être rajoutée aux menus des boutons de sélection de la langue qui accompagnent tous les widgets de saisie du groupe. Cf. [Création d'un nouveau widget](/__doc__/10_creation_widgets.md#widget-annexe--bouton-de-sélection-de-la-langue) pour plus de détails sur la génération des menus de langues.*

- `"widgets to move"` fournit une liste de tuples contenant les informations relatives à des widgets dont - parce qu'on a supprimé un widget antérieurement positionné au-dessus d'eux dans la grille - il faut à présent modifier la position :
    - `[0]` est la grille concernée (QGridLayout).
    - `[1]` est le widget lui-même (QWidget).
    - `[2]` est le nouveau numéro de ligne/valeur du paramètre `row` pour le widget dans la grille.


## Boutons de sélection de la source

Le bouton de sélection de la source est un QToolButton qui accompagne un widget de saisie de type QComboBox ou un widget de groupe.

![div_bouton_selection_source](/__doc__/schemas/div_bouton_selection_source.png)

Cf. [Création d'un nouveau widget](/__doc__/10_creation_widgets.md#widget-annexe--bouton-de-sélection-de-la-source) pour plus de détails sur les modalités de création de ces widgets.

Soit :
- `key` la clé du bouton de sélection de la langue considéré dans le dictionnaire de widgets `widgetsdict` ;
- `source` la nouvelle source choisie par l'utilisateur dans le menu associé au QToolButton.

### Mise à jour du dictionnaire des widgets

Quand l'utilisateur sélectionne une nouvelle source dans le menu, il faudra commencer par exécuter la commande de mise à jour du dictionnaire (méthode `change_source()`) :

```python

r = widgetsdict.change_source(key, source)

```

### ... puis du formulaire

Les informations renvoyées par `change_source()` permettent de réaliser les opérations subséquentes sur les widgets.

Le résultat, ici `r`, est un dictionnaire à cinq clés :

- `"concepts list to update"` est une liste de clés du dictionnaire de widgets correspondant à des widgets de saisie de type QComboBox dont la liste de valeurs doit être actualisée. La liste est déduite de la clé `'current source'` du dictionnaire interne, qui contient le nom du nouveau thésaurus. Cf. [Création d'un nouveau widget](/__doc__/10_creation_widgets.md#paramètres-spécifiques-aux-widgets-qcombobox) pour plus de détails.

    *Concrètement, cette liste, si elle n'est pas vide, contiendra soit la clé de l'enregistrement courant, soit celle du widget qui sera désormais affiché à la place.*

- `"widgets to empty"` est une liste de widgets (QWidget) dont le texte doit être effacé.

    *Concrètement, cette liste, si elle n'est pas vide, ne contiendra jamais que la clé de l'enregistrement courant.*

- `"switch source menu to update"` est une liste de clés du dictionnaire de widgets pour lesquelles le menu des sources doit être régénéré.

    *Concrètement, cette liste, si elle n'est pas vide, contiendra soit la clé de l'enregistrement courant et/ou celle du widget qui sera désormais affiché à la place. Dans la grande majorité des cas, les items du menu ne changent pas, seulement la source identifiée comme sélectionnée, mais on préférera régénérer intégralement tous les objets QMenu et QAction par précaution.*

- `"widgets to show"` contient une liste de widgets (QWidget) jusque-là masqués qu'il s'agit maintenant d'afficher.

    *Lors d'une bascule en mode manuel, il faudra afficher le groupe de propriétés dans lequel se fera la saisie manuelle, ainsi que tous les widgets qu'il contient. En cas de sortie du mode manuel, il s'agira d'afficher le widget de saisie QComboBox (si thésaurus) ou QLineEdit (si saisie libre d'URI) que l'utilisateur devra désormais utiliser pour la catégorie de métadonnées concernée.*

- Inversement, `"widgets to hide"` contient une liste de widgets (QWidget) qui devront être masqués.

    *Lors d'une bascule en mode manuel ou sortie du mode manuel, les widgets utilisés pour l'ancien mode doivent être masqués.*


## Boutons de sélection de la langue

Le bouton de sélection de la langue est un QToolButton qui accompagne un widget de saisie. Il a deux fonctions :
- afficher la langue dans laquelle a été saisie la valeur (sous une forme abrégée - on écrira par exemple "FR" pour une métadonnée en français) ;
- lors de l'édition des métadonnées, permettre à l'utilisateur de choisir dans un menu la langue de la valeur qu'il vient de saisir ou va saisir.

![gt_bouton_selection_langue](/__doc__/schemas/gt_bouton_selection_langue.png)

Cf. [Création d'un nouveau widget](/__doc__/10_creation_widgets.md#widget-annexe--bouton-de-sélection-de-la-langue) pour plus de détails sur les modalités de création de ces widgets.

Soit :
- `key` la clé du bouton de sélection de la langue considéré dans le dictionnaire de widgets `widgetsdict` ;
- `langue` la nouvelle langue choisie par l'utilisateur.


### Mise à jour du dictionnaire des widgets

Quand l'utilisateur sélectionne une nouvelle langue `new_language` dans le menu, il faudra commencer par exécuter la commande de mise à jour du dictionnaire (méthode `change_language()`) :

```python

r = widgetsdict.change_language(key, new_language, langList)

```

*`langList` est le paramètre utilisateur qui spécifie la liste des langues autorisées pour les traductions. Il prend une valeur identique pour tous les boutons de sélection de la langue et celle-ci peut être considérée comme fixe pour toute la durée de la saisie, dans la mesure où tout changement nécessiterait de regénérer intrégralement le dictionnaire des widgets et, par suite, le formulaire.*


### ... puis du formulaire

Les informations renvoyées par `change_language()` permettent de réaliser les opérations subséquentes sur les widgets.

Le résultat, ici `r`, est un dictionnaire à deux clés :

- `"language menu to update"` contient une liste de clés du dictionnaire de widgets (et non directement des widgets), pour lesquelles le menu des langues doit être régénéré. Comme lors de la création initiale du formulaire, la liste (mise à jour) des langues à faire apparaître dans ce menu est contenue dans la clé `"authorized languages"` du dictionnaire interne pour la clé fournie.

    *Dans le cas général, cette liste contiendra les clés de tous les widgets de saisie du groupe de traduction. Pour le widget courant, la langue à afficher sur le bouton de sélection de la langue a été modifiée. Pour les autres widgets de saisie, il s'agit d'enlever la langue nouvellement choisie et de rajouter celle qui l'était précédemment dans la liste des langues disponibles pour les traductions. Sans entrer dans ces subtilités, on pourra simplement recréer les QMenu et QAction pour les clés concernées sans chercher à savoir ce qui a changé exactement. Cf. [Création d'un nouveau widget](/__doc__/10_creation_widgets.md#widget-annexe--bouton-de-sélection-de-la-langue) pour plus de détails sur la génération des menus de langues.*

-  `"widgets to hide"` contient une liste de widgets (QWidget) qui devront être masqués.

    *Dans de rares cas, ce liste pourra contenir le QToolButton du bouton "plus" du groupe de traduction (si la langue antérieurement sélectionnée n'était pas dans `listLang` et que, après changement, toutes les langues autorisées sont désormais utilisées).*
    

