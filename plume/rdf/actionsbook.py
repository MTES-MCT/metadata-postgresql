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
    show : VisibleKeyList
        Liste des clés dont les widgets doivent être rendus visibles.
    show_minus_button : TrueMinusButtonKeyList
        Liste des clés dont le bouton moins doit être rendu visible,
        s'il existe.
    hide : NoGhostKeyList
        Liste des clés dont les widgets doivent être masqués.
    hide_minus_button : TrueMinusButtonKeyList
        Liste des clés dont le bouton moins doit être masqué, s'il existe.
    drop : NoGhostKeyList
        Liste des clés dont les widgets doivent être supprimés.
    create : NoGhostKeyList
        Liste des clés dont les widgets doivent être créés.
    move : NoGhostKeyList
        Liste des clés dont les widgets doivent être déplacés dans la grille.
    languages : NoGhostKeyList
        Liste des clés dont le menu des langues doit être mis à jour.
    sources : NoGhostKeyList
        Liste des clés dont le menu des sources doit être mis à jour.
    thesaurus : NoGhostKeyList
        Liste des clés dont la liste de valeurs doit être recalculée.
    
    """
    
    def __init__(self):
        self.show = VisibleKeyList()
        self.show_minus_button = TrueMinusButtonKeyList()
        self.hide = NoGhostKeyList()
        self.hide_minus_button = TrueMinusButtonKeyList()
        self.drop = NoGhostKeyList()
        self.create = NoGhostKeyList()
        self.move = NoGhostKeyList()
        self.languages = NoGhostKeyList()
        self.source = NoGhostKeyList()
        self.thesaurus = NoGhostKeyList()

class NoGhostKeyList(list):
    """Liste de clés garantie sans fantôme.
    
    Notes
    -----
    Cette classe réécrit la méthode `append` de `list` pour
    exclure silencieusement les clés fantômes. Les clés en
    cours d'initialisation ne sont pas non plus prises en
    compte, pour éviter que la même clé apparaisse dans
    `create`, `show`, `move`...
    
    """
    def append(self, value):
        if not value.is_ghost and not value._is_unborn:
            super().append(value)

class VisibleKeyList(list):
    """Liste de clés garanties visibles.
    
    Notes
    -----
    Cette classe réécrit la méthode `append` de `list` pour
    exclure silencieusement les clés non visibles. Les clés en
    cours d'initialisation ne sont pas non plus prises en
    compte, pour éviter que la même clé apparaisse dans
    `create`, `show`, `move`...
    
    """
    def append(self, value):
        if not value.is_ghost and not value.is_hidden_b and \
            not value.is_hidden_m and not value._is_unborn:
            super().append(value)

class TrueMinusButtonKeyList(list):
    """Liste de clés garanties visibles et avec un bouton moins.
    
    Ceci ne présage pas de la visibilité du bouton moins
    lui-même.
    
    Notes
    -----
    Cette classe réécrit la méthode `append` de `list` pour
    exclure silencieusement les clés non visibles ou sans
    bouton moins. Les clés en cours d'initialisation ne sont
    pas non plus prises en compte, pour éviter que la même
    clé apparaisse dans `create`, `show`, `move`...
    
    """
    def append(self, value):
        if not value.is_ghost and not value.is_hidden_b and \
            not value.is_hidden_m and not value._is_unborn \
            and value.has_minus_button:
            super().append(value)


