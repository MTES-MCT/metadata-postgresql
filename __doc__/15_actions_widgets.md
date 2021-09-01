# Actions contrôlées par des widgets

## Boutons intégrés au formulaire

En plus d'être généré à la volée, le formulaire de saisie des métadonnées est dynamique. L'utilisateur peut déclencher des actions qui auront pour effet d'afficher ou masquer des widgets, d'en créer, d'en supprimer, de modifier des menus...

Toutes ces actions impliquent en premier lieu de mettre à jour le dictionnaire de widgets, grâce à des méthodes de la classe `WidgetsDict` qui renvoient les informations nécessaires pour, en second lieu, réaliser les opérations qui s'imposent sur les widgets eux-mêmes.


### Boutons "plus" et boutons de traduction

Un bouton "plus" est un widget QToolButton qui, lorsqu'il est activé par l'utilisateur, permet d'ajouter une valeur dans un groupe de valeurs.

![gv_bouton_plus](/__doc__/gv_bouton_plus.png)

Un bouton de traduction est un QToolButton qui permet d'ajouter une traduction dans un groupe de traductions.

![gt_bouton_de_traduction](/__doc__/gt_bouton_de_traduction.png)

Ces deux types de boutons sont considérés ensemble, car le traitement à prévoir est le même (les méthodes utilisées n'auront pas exactement le même effet, mais c'est transparent).

Soit `key` la clé du bouton "plus" ou bouton de traduction considéré dans le dictionnaire de widgets `widgetsdict`.

Lors de l'activation du bouton, il faudra :

1. exécuter la commande de mise à jour du dictionnaire (méthode `add()`) :

```python

r = widgetsdict.add(key, language, langList)

```

`language` et `langList` sont les paramètres utilisateur qui spécifient réciproquement la langue principale de saisie et la liste des langues autorisées pour les traductions. Ils prennent des valeurs identiques pour tous les boutons "plus" et celles-ci peuvent être considérées comme fixes pour toute la durée de la saisie, dans la mesure où tout changement nécessiterait de regénérer intrégralement le dictionnaire des widgets et, par suite, le formulaire.

2. utiliser les informations renvoyées par `add()` pour réaliser les opérations subséquentes sur les widgets.

Le résultat, ici `r`, est un dictionnaire à quatre clés :

- `"widgets to show"` contient une liste de widgets (QWidget) jusque-là masqués qu'il s'agit maintenant d'afficher (`show()`).

    Concrètement, cette liste, si elle n'est pas vide, contiendra des widgets QToolButton correspondant à des boutons "moins" (lorsqu'il ne reste qu'un objet dans un groupe, son bouton "moins" disparaît pour empêcher sa suppression, il doit être ré-affiché si un nouvel objet est ajouté).
    
- inversement, `"widgets to hide"` contient une liste de widgets (QWidget) qui devront être masqués (`hide()`).

    La liste sera toujours vide pour un bouton "plus". Pour un bouton de traduction, elle pourra contenir le QToolButton du bouton "plus" lui-même si toutes les langues disponibles pour les traductions sont maintenant utilisées, et qu'il n'y a donc plus lieu d'ajouter des traductions supplémentaires.
    
- `"language menu to update"` contient une liste de clés du dictionnaire de widgets (et non directement des widgets, cette fois), pour lesquelles le menu des langues doit être régénéré. Comme lors de la création initiale du formulaire, la liste (mise à jour) des langues à faire apparaître dans ce menu est contenue dans la clé `"authorized languages"` du dictionnaire interne pour la clé fournie.

- `"new keys"` contient une liste de clés qui viennent d'être ajoutées au dictionnaire, et pour lesquelles il faudra donc implémenter tous les widgets.

    La marche à suivre est la même que lors de la génération initiale du formulaire. Cf. [Création d'un nouveau widget](/__doc__/10_creation_widgets.md). 


### Boutons "moins"

Les boutons "moins" existent à la fois dans les groupes de valeurs et dans les groupes de traduction. Dans les deux cas, ce sont des QToolButton dont l'activation permet à l'utilisateur de faire disparaître des zones de saisie excédentaires.

NB : une telle opération a pour seul intérêt le confort visuel de l'utilisateur et, lorsqu'il s'agit de retirer une branche complète et pas juste un widget de saisie, de lui éviter de devoir supprimer à la main un potentiellement grand nombre de valeurs. Du point de vue des fonctions de RDF Utils, la présence de widgets vides n'a aucune espèce d'importance.

![gv_bouton_moins](/__doc__/gv_bouton_moins.png)

![gt_bouton_moins](/__doc__/gt_bouton_moins.png)

Soit `key` la clé du bouton "moins" considéré dans le dictionnaire de widgets `widgetsdict`.

Lors de l'activation du bouton, il faudra :

1. exécuter la commande de mise à jour du dictionnaire (méthode `drop()`) :

```python

r = widgetsdict.drop(key, langList)

```

`langList` est le paramètre utilisateur qui spécifie la liste des langues autorisées pour les traductions. Il prend une valeur identique pour tous les boutons "moins" et celle-ci peut être considérée comme fixe pour toute la durée de la saisie, dans la mesure où tout changement nécessiterait de regénérer intrégralement le dictionnaire des widgets et, par suite, le formulaire.

2. utiliser les informations renvoyées par `drop()` pour réaliser les opérations subséquentes sur les widgets.

Le résultat, ici `r`, est un dictionnaire à sept clés :

- `"widgets to delete"` contient une liste de widgets (QWidget) à détruire.
    
    Ces widgets ne sont plus référencés dans le dictionnaire, il ne sera donc plus jamais possible d'interragir avec eux. Les supprimer paraît la meilleure chose à faire.

- dans la même veine, `"actions to delete"` contient la liste des objets QAction à détruire.

- et `"menus to delete"` celle des objets QMenu à détruire.

- `"widgets to show"` contient une liste de widgets (QWidget) jusque-là masqués qu'il s'agit maintenant d'afficher (`show()`).

    Cette liste sera toujours vide pour le bouton "moins" d'un groupe de valeur. Dans un groupe de traduction, elle pourra contenir le QToolButton du bouton "moins" lui-même si retirer une traduction fait que toutes les langues ne sont désormais plus utilisées, et qu'il est donc de nouveau possible d'ajouter des traductions supplémentaires.
    
- inversement, `"widgets to hide"` contient une liste de widgets (QWidget) qui devront être masqués (`hide()`).

   Concrètement, cette liste, si elle n'est pas vide, contiendra des widgets QToolButton correspondant à des boutons "moins" qui doivent être masqués parce qu'il ne reste plus qu'un élément dans le groupe de valeurs ou de traductions (et qu'il n'est pas permis à l'utilisateur de supprimer le dernier élément d'un groupe).
    
- `"language menu to update"` contient une liste de clés du dictionnaire de widgets (et non directement des widgets, cette fois), pour lesquelles le menu des langues doit être régénéré. Comme lors de la création initiale du formulaire, la liste (mise à jour) des langues à faire apparaître dans ce menu est contenue dans la clé `"authorized languages"` du dictionnaire interne pour la clé fournie.

- `"widgets to move"` fournit une liste de tuples contenant les informations relatives à des widgets dont il faut modifier la position dans la grille (parce qu'on a supprimé un widget positionné au-dessus d'eux) :
    - `[0]` est la grille (QGridLayout) du widget.
    - `[1]` est le widget lui-même (QWidget).
    - `[2]` est le nouveau numéro de ligne/valeur du paramètre `row` pour le widget.


### Boutons de sélection de la source

### Boutons de sélection de la langue

## Boutons fixes

### Bouton de sauvegarde

### Bouton d'annulation

### Bouton de réinitialisation

### Activation du mode traduction

### Choix de la trame de formulaire

