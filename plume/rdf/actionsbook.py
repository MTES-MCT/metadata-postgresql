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

Les carnets d'actions sont supposés être lus et réinitialisés
après chaque commande, sans quoi ils finiront immanquablement par
contenir des informations contradictoires ou fausses.

"""

class ActionsBook:
    """Classe pour les carnets d'actions.
    
    Attributes
    ----------
    modified : list
        Liste de toutes les clés modifiées (excluant les créations
        et les suppressions).
    show : list
        Liste des clés dont les widgets doivent être rendus visibles.
    show_minus_button : list
        Liste des clés dont le bouton moins doit être rendu visible,
        s'il existe.
    hide : list
        Liste des clés dont les widgets doivent être masqués.
    hide_minus_button : list
        Liste des clés dont le bouton moins doit être masqué, s'il existe.
    create : list
        Liste des clés dont les widgets doivent être créés.
    move : list
        Liste des clés dont les widgets doivent être déplacés dans la grille.
    languages : list
        Liste des clés dont le menu des langues doit être mis à jour.
    sources : list
        Liste des clés dont le menu des sources doit être mis à jour.
    thesaurus : list
        Liste des clés dont la liste de valeurs doit être recalculée.
    empty : list
        Liste des clés pour lesquelles le texte saisi doit être effacé.
    drop : list
        Liste des clés dont les widgets doivent être supprimés.
    
    """
    
    def __init__(self):
        self.modified = NoGhostKeyList(actionsbook=self)
        self.show = VisibleKeyList(actionsbook=self, erase=['hide',
            'show_minus_button'])
        self.show_minus_button = TrueMinusButtonKeyList(actionsbook=self,
            erase=['hide_minus_button'])
        self.hide = NoGhostKeyList(actionsbook=self, erase=['show',
            'show_minus_button', 'hide_minus_button'])
        self.hide_minus_button = TrueMinusButtonKeyList(actionsbook=self,
            erase=['show_minus_button'])
        self.create = NoGhostKeyList(actionsbook=self, erase=['show',
            'show_minus_button', 'hide', 'hide_minus_button', 'move',
            'languages', 'sources', 'thesaurus', 'modified', 'empty'])
        self.move = NoGhostKeyList(actionsbook=self)
        self.languages = NoGhostKeyList(actionsbook=self)
        self.sources = NoGhostKeyList(actionsbook=self)
        self.thesaurus = NoGhostKeyList(actionsbook=self)
        self.empty = NoGhostKeyList(actionsbook=self)
        self.drop = NoGhostKeyList(actionsbook=self, erase=['show',
            'show_minus_button', 'hide', 'hide_minus_button', 'create',
            'move', 'languages', 'sources', 'thesaurus', 'modified',
            'empty'])

    def __bool__(self):
        return sum(len(getattr(self, a)) for a in self.__dict__.keys()) > 0


class NoGhostKeyList(list):
    """Liste de clés garantie sans fantôme.
    
    Parameters
    ----------
    actionsbook : ActionsBook
        Le carnet d'actions auquel appartient la liste.
    erase : list of str, optional
        La liste des attributs où la clé doit être supprimée
        dès lors qu'elle apparaît dans la présente liste.
    
    Attributes
    ----------
    actionsbook : ActionsBook
        Le carnet d'actions auquel appartient la liste. Cet
        attribut sert à croiser les listes pour veiller
        à leur cohérence.
    erase : list of str
        La liste des attributs où la clé doit être supprimée
        dès lors qu'elle apparaît dans la présente liste.
    
    Notes
    -----
    Cette classe réécrit la méthode `append` de `list` pour
    exclure silencieusement les clés fantômes. Les clés en
    cours d'initialisation ne sont pas non plus prises en
    compte, de même que les clés qui se trouvent déjà dans
    `create`.
    
    """
    def __init__(self, actionsbook, erase=None):
        self.actionsbook = actionsbook
        self.erase = erase or []
        super().__init__(self)
    
    def append(self, value):
        if value and not value._is_unborn:
            if not value in self and \
                not value in self.actionsbook.create:
                super().append(value)
            if not value in self.actionsbook.modified \
                and not value in self.actionsbook.create \
                and not value in self.actionsbook.drop:
                self.actionsbook.modified.append(value)
            for a in self.erase:
                l = getattr(self.actionsbook, a)
                if value in l:
                    l.remove(value)

class VisibleKeyList(NoGhostKeyList):
    """Liste de clés garanties visibles.
    
    """
    def append(self, value):
        if not value.is_hidden:
            super().append(value)

class TrueMinusButtonKeyList(VisibleKeyList):
    """Liste de clés garanties visibles et avec un bouton moins.
    
    Ceci ne présage pas de la visibilité du bouton moins
    lui-même.
    
    """
    def append(self, value):
        if value.has_minus_button:
            super().append(value)


