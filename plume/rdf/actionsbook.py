"""Carnets d'actions.

Les carnets d'actions - objets de classe `ActionsBook` -
servent à répertorier les actions réalisée sur les dictionnaires
de widgets qui devront se retraduire en actions sur les widgets
eux-mêmes.

Chaque attribut du carnet d'actions correspond à un type d'action,
il prend pour valeur une liste de clés - `WidgetKey` - pour
laquelle l'action est à accomplir.

Pour faciliter leur exploitation, les `ActionsBook` sont
traduits en dictionnaires par la méthode `actionsbook_to_dict`
de la classe `WidgetsDict`.

Les listes des carnets d'actions contiennent par construction
des informations inutiles (comme le fait de rendre visible le
bouton moins annexé à un widget qui n'en a pas) ou redondantes
(comme le fait de déplacer un widget qui n'a pas encore été créé).
La consolidation est également du ressort de la méthode
`actionsbook_to_dict`.

"""

class ActionsBook:
    """Classe pour les carnets d'actions.
    
    Attributes
    ----------
    show : WidgetKey
        Clés dont les widgets doivent être rendus visibles.
    show_minus_button : WidgetKey
        Clés dont le bouton moins doit être rendu visible,
        s'il existe.
    hide : WidgetKey
        Clés dont les widgets doivent être masqués.
    hide_minus_button : WidgetKey
        Clés dont le bouton moins doit être masqué, s'il existe.
    drop : WidgetKey
        Clés dont les widgets doivent être supprimés.
    create : WidgetKey
        Clés dont les widgets doivent être créés.
    move : WidgetKey
        Clés dont les widgets doivent être déplacés dans la grille.
    languages : WidgetKey
        Clés dont le menu des langues doit être mis à jour.
    sources : WidgetKey
        Clés dont le menu des sources doit être mis à jour.
    thesaurus : WidgetKey
        Clés dont la liste de valeurs doit être recalculée.
    
    """
    
    def __init__(self):
        self.show = []
        self.show_minus_button = []
        self.hide = []
        self.hide_minus_button = []
        self.drop = []
        self.create = []
        self.move = []
        self.languages = []
        self.source = []
        self.thesaurus = []

