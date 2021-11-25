"""Clés des dictionnaires de widgets.

La classe `WidgetKey` matérialise les clés des dictionnaires
de widgets (classe `WidgetsDict`).

Dans le contexte d'un dictionnaire, ces clés forment un arbre :
- à la base, la clé racine est la seule qui n'ait pas
de "parent". Elle est référencée dans l'attribut `root` du
dictionnaire WidgetsDict ;
- toutes les autres clés descendent d'une clé parente,
référencée dans leur attribut `parent`. Réciproquement,
les filles d'une clé sont référencées dans son attribut
`children`.

La clé est porteuse de toutes les informations nécessaires
au maintien de l'intégrité du dictionnaire de widgets.
Les autres informations, qui servent au paramétrage des widgets,
à la sérialisation en graphe de métadonnées (classe `Metagraph`),
etc. sont stockées dans le dictionnaire interne (classe
`InternalDict`) associé à la clé.

Les clés ne sont *pas* indépendantes les unes des autres. La
seule création d'une nouvelle clé entraîne la modification de
son parent et parfois de ses soeurs.

"""

import uuid
from plume.rdf.exceptions import IntegrityBreach, MissingParameter, ForbiddenOperation, \
    UnknownParameterValue
from plume.rdf.actionsbook import ActionsBook


class WidgetKey:
    """Clés des dictionnaires de widgets.
    
    Attributes
    ----------
    uuid : str
        Identifiant unique de la clé.
    kind : {'edit', 'group of values', 'translation group',
        'group of properties', 'plus button', 'translation button'}
        Nature de l'objet pour lequel est utilisé la clé.
    generation : int
        Génération de la clé. 0 pour une clé racine.
    is_root : bool
        True pour une clé racine, qui n'a pas de parent.
    parent : WidgetKey
        La clé parente. None pour une clé racine.
    is_ghost : bool
        True pour une clé qui ne porte pas de widget (clé fantôme).
    is_m : bool
        True pour une clé de saisie manuelle.
    m_twin : WidgetKey
        Le cas échéant, la clé jumelle.
    children : list of WidgetKey
        Liste des clés filles, vide le cas échéant.
    button : WidgetKey
        Si la clé est utilisée pour un groupe de valeur ou de
        traduction, clé du bouton plus ou bouton de traduction
        du groupe.
    row : int
        L'indice de la ligne de la grille occupée par le widget
        porté par la clé. Vaut None pour une clé fantôme.
    rowspan : int
        Nombre de lignes occupées par le ou les widgets portés par
        la clé, étiquette séparée comprise. Vaut 0 pour une clé fantôme.
    hidden_m : bool
        True pour la clé présentement masquée d'un couple de
        jumelles, ou toute clé descendant de celle-ci (branche
        masquée).
    hidden_b : bool
        True si le widget porté par la clé est un bouton plus
        ou bouton de traduction masqué.
    hide_minus_button : bool
        True si, pour une clé de type 'edit' dans un groupe de valeurs
        ou de traduction, le bouton moins doit être masqué (car il
        n'y a qu'une seule valeur dans le groupe). À noter que cet
        attribut peut valoir True dans des circonstances où il
        n'existe pas de bouton moins, il conviendra alors d'ignorer
        cette information sans intérêt.
    do_not_save : bool
        True pour une clé dont les informations attachées ne
        doivent pas être sauvegardées.
    available_languages : list of str
        Dans un groupe de traduction, la liste des langues encore
        disponibles pour les traductions. La clé `authorized_languages`
        du dictionnaire interne associé correspond toujours à
        `available_languages` + la langue du widget si elle n'est
        pas incluse dans `available_languages`.
    
    """
    
    def __init__(self, kind, parent=None, is_m=False, m_twin=None, rowspan=None,
        is_ghost=False, hidden_m=False, hidden_b=False, do_not_save=False,
        available_languages=None, widget_language=None, actionsbook=None,
        no_computation=False):
        """Crée une clé de dictionnaire de widgets.
        
        Parameters
        ----------
        kind : {'edit', 'group of values', 'translation group',
            'group of properties', 'plus button', 'translation button'}
            Nature de l'objet pour lequel est utilisé la clé.
        parent : WidgetKey, optional
            La clé parente. Vaudra None pour une clé racine.
        is_m : bool, default False
            La clé est-elle une clé de saisie manuelle ?
        m_twin : WidgetKey, optional
            Le cas échéant, la clé jumelle.
        rowspan : int, optional
            Nombre de lignes occupées par le ou les widgets portés par
            la clé fille, le cas échéant. Si non spécifié,
            sera fixé à 0 si `is_ghost` vaut True, sinon génère une
            erreur.
        is_ghost : bool, default False
            True pour une clé qui ne porte pas de widget.
        hidden_m : bool, default False
            True pour la clé présentement masquée d'un couple de
            jumelles, ou toute clé descendant de celle-ci (branche
            masquée).
        do_not_save : bool, default False
            True pour une clé dont les informations attachées ne
            doivent pas être sauvegardées.
        available_languages : list of str, optional
            Liste des langues encore disponibles pour les traductions.
            Obligatoire pour les groupes de traduction, ignoré sinon.
        widget_language : str, optional
            Langue utilisée par le widget. Obligatoire pour une clé
            'edit' dont la clé parente est un groupe de traduction.
        actionsbook : ActionsBook, optional
            Si présent, les actions à répercuter sur les widgets
            seront tracées dans ce carnet d'actions.
        no_computation : bool, default False
            Si True, la fonction n'exécutera pas le calcul des indices 
            de lignes et de la visibilité des boutons moins. Cette option ne
            doit être utilisée que si un grand nombre d'opérations
            sont réalisées successivement et qu'il est prévu d'effectuer
            tous les calculs en fin de processus - c'est ainsi que procède
            `build_dict`.
            
        Notes
        -----
        Les informations relatives aux clés filles sont saisies
        a posteriori.
        
        Une nouvelle fille est automatiquement enregistrée dans
        les attributs de la clé parent et, s'il y a lieu, auprès
        de sa jumelle.
        
        Returns
        -------
        WidgetKey

        """
        if not kind in ('edit', 'group of values', 'translation group',
            'group of properties', 'plus button', 'translation button'):
            raise UnknownParameterValue('kind', kind, self)
        
        self.kind = kind       
        self.uuid = str(uuid.uuid4())
        self.parent = parent
        self.generation = 0 if parent is None else parent.generation + 1
        self.is_root = parent is None
        self.is_m = is_m
        self.m_twin = m_twin
        
        if actionsbook:
            actionsbook.create.append(self)
        
        # attributs relatifs au widget porté
        # par la clé
        self.is_ghost = is_ghost
        self.hidden_m = hidden_m
        self.hidden_b = False
        self.do_not_save = do_not_save
        self.row = None
        self.hide_minus_button = True
        
        if self.is_ghost:
            self.rowspan = 0
        elif self.kind != 'edit':
            self.rowspan = 1
        elif rowspan is None:
            raise MissingParameter('rowspan', self)
        else:
            self.rowspan = rowspan
        
        # attributs relatifs aux futures filles
        self.children = []
        self.button = None
        
        if self.kind == 'translation group':
            if available_languages is None:
                raise MissingParameter('available_languages', self)
            self.available_languages = available_languages.copy()
        else:
            self.available_languages = None

        # déclaration auprès de la jumelle et
        # contrôle d'intégrité
        if m_twin:
            if self.hidden_m == self.m_twin.hidden_m:
                raise IntegrityBreach(
                    self,
                    'Une et une seule des clés jumelles devrait ' \
                    'être masquée (hidden_m).'
                    )
            if self.is_m == self.m_twin.is_m:
                raise IntegrityBreach(
                    self,
                    'Une et une seule des clés jumelles devrait ' \
                    'être manuelle (is_m).'
                    )
            if self.rowspan != self.m_twin.rowspan:
                raise IntegrityBreach(
                    self,
                    'rowspan devrait être indentique pour les deux ' \
                    'clés jumelles.'
                    )
            self.m_twin.m_twin = self

        # déclaration auprès du parent
        if not self.is_root:

            if not relationship_makes_sense(self.parent.kind, self.kind):
                raise IntegrityBreach(self, "Impossible de rattacher une " \
                    "clé '{}' à une clé '{}'.".format(self.kind, self.parent.kind))
                    
            self.parent.children.append(self)
            
            if self.kind in ('translation button', 'plus button'):
                if self.parent.button:
                    raise IntegrityBreach(self, "Un bouton est déjà référencé" \
                        " dans le groupe parent.")
                self.parent.button = self
            
            if not no_computation:
                self.parent.compute_minus_buttons(actionsbook)
                self.parent.compute_rows(actionsbook)
            
            if self.kind == 'edit' and self.parent.kind == 'translation group':
                if not widget_language:
                    raise MissingParameter('widget_language', self)
                self.parent.language_out(widget_language, actionsbook)

    
    def __str__(self):
        return "WidgetKey {}".format(self.uuid)
      
    
    def kill(self, widget_language=None, actionsbook=None):
        """Efface une clé de la mémoire de son parent.
        
        Parameters
        ----------
        widget_language : str
            Langue utilisée par le widget. Devrait toujours être
            spécifiée pour une clé 'edit' dont la clé parente est un
            groupe de traduction, sauf si la langue en question
            n'était pas autorisée, et ne doit donc pas être reversée
            dans la liste des langues disponibles.
        actionsbook : ActionsBook, optional
            Si présent, les actions à répercuter sur les widgets
            seront tracées dans ce carnet d'actions.
        
        Notes
        -----
        Le cas échéant, la clé jumelle sera également effacée,
        il n'y a donc pas lieu d'appeler deux fois cette méthode.
        
        Appliquer cette fonction sur une clé racine ne provoque
        pas d'erreur, elle n'aura simplement aucun effet.
        
        """
        if self.is_root:
            return
        
        self.parent.remove(self)
        if self.m_twin:
            self.parent.remove(m_twin)
        
        if self.kind in ('translation button', 'plus button'):
            self.parent.button = None
            # ne devrait jamais être utilisé, aucun mécanisme
            # ne prévoit de supprimer le bouton d'un groupe
            # sans supprimer également celui-ci.
        
        if self.kind == 'edit' and self.parent.kind == 'translation group':
            if not widget_language:
                raise MissingParameter('widget_language', self)
            self.parent.language_in(widget_language, actionsbook)
        
        self.parent.compute_minus_buttons(actionsbook)
        self.parent.compute_rows(actionsbook)


    def compute_rows(self, actionsbook=None):
        """Actualise les indices de lignes des filles du groupe.
        
        Cette méthode devrait être systématiquement appliquée à
        la clé parente après toute création ou effacement de clé.
        
        Parameters
        ----------
        actionsbook : ActionsBook, optional
            Si présent, les actions à répercuter sur les widgets
            seront tracées dans ce carnet d'actions.
        
        Notes
        -----
        `compute_rows` respecte l'ordre des clés filles dans la
        liste de l'attribut `children`. Cette liste est
        systématiquement réordonnée pour veiller à ce que les
        boutons éventuels soient à la fin de la liste (en préservant
        l'ordre antérieur pour les autres éléments).
        
        """      
        self.children.sort(
            key=lambda x: 1 if x.kind in \
                ('translation button', 'plus button') else 0
            )
        n = 0
        for child in self.real_children():
        
            if child.is_m and child.m_twin:
                continue
                # traitée ensuite avec la jumelle
            
            if child.row != n:
                child.row = n
                if actionsbook:
                    actionsbook.move.append(child)
                if child.m_twin:
                    child.m_twin.row = n
                    if actionsbook:
                        actionsbook.move.append(child.m_twin)
            
            n += child.rowspan


    def compute_minus_buttons(self, actionsbook=None):
        """Actualise la visibilité des boutons moins des filles du groupe.
        
        Cette méthode devrait être systématiquement appliquée à
        la clé parente après toute création ou effacement de clé.
        En pratique, elle n'a d'effet que si sa cible est un groupe
        de traduction ou groupe de valeur.
        
        Parameters
        ----------
        actionsbook : ActionsBook, optional
            Si présent, les actions à répercuter sur les widgets
            seront tracées dans ce carnet d'actions.
            
        """       
        if not self.kind in ('translation group', 'group of values'):
            return
        
        true_children_count = sum(
            1 for child in self.real_children(include_button = False) \
                if not child.is_m or not child.m_twin
            )
        
        for child in self.real_children(include_button=False):
            # boutons moins à afficher
            if true_children_count >= 2 \
                and child.hide_minus_button:
                child.hide_minus_button = False
                if actionsbook:
                    actionsbook.show_minus_button.append(child)
            # boutons moins à masquer
            if true_children_count < 2 \
                and not child.hide_minus_button:
                child.hide_minus_button = True
                if actionsbook:
                    actionsbook.hide_minus_button.append(child)


    def language_in(self, widget_language, actionsbook=None):
        """Ajoute une langue à la liste des langues disponibles.
        
        Parameters
        ----------
        widget_language : str
            Langue redevenue disponible.
        actionsbook : ActionsBook, optional
            Si présent, les actions à répercuter sur les widgets
            seront tracées dans ce carnet d'actions.
        
        """        
        if not self.kind == 'translation group':
            return
        
        if widget_language is None:
            raise MissingParameter('widget_language', self)
        
        if widget_language in self.available_languages:
            raise IntegrityBreach(
                self,
                "La langue '{}' est déjà dans la liste" \
                " des langues disponibles.".format(widget_language)
                )
        
        self.available_languages.append(widget_language)
        if actionsbook:
            for child in self.real_children(include_button=False):
                actionsbook.languages.append(child)
        
        if self.button and len(self.available_languages) == 1:
            self.button.hidden_b = False
            if actionsbook:
                actionsbook.show.append(self.button)


    def language_out(self, widget_language, actionsbook=None):
        """Retire une langue de la liste des langues disponibles.
        
        Parameters
        ----------
        widget_language : str
            Langue redevenue disponible.
        actionsbook : ActionsBook, optional
            Si présent, les actions à répercuter sur les widgets
            seront tracées dans ce carnet d'actions.
        
        """        
        if not self.kind == 'translation group':
            return
        
        if widget_language is None:
            raise MissingParameter('widget_language', self)
        
        if not widget_language in self.available_languages:
            return
            # on admet que la langue ait pu ne pas se trouver
            # dans la liste (métadonnées importées, etc.)
        
        self.available_languages.remove(widget_language)
    
        if actionsbook:
            for child in self.real_children(include_button=False):
                actionsbook.languages.append(child)
        
        if not self.available_languages and self.button:
            self.button.hidden_b = True
            if actionsbook:
                actionsbook.hide.append(self.button)
  

    def hide_m(self, actionsbook=None):
        """Inverse la visibilité d'un couple de jumelles (et leurs descendantes).
        
        Parameters
        ----------
        actionsbook : ActionsBook, optional
            Si présent, les actions à répercuter sur les widgets
            seront tracées dans ce carnet d'actions.
        
        """
        if not self.m_twin:
            raise IntegrityBreach(self, "Pas de clé jumelle renseignée.")
        self.m_twin._hide_m(actionsbook)
        self._hide_m(actionsbook)   


    def _hide_m(self, actionsbook):
        self.hidden_m = not self.hidden_m
        
        if actionsbook and self.hidden_m:
            actionsbook.show.append(self)
        elif actionsbook:
            actionsbook.hide.append(self)
            
        for child in self.children:
            child.hide_m()
            
    
    def real_children(self, include_ghost=False, include_hidden=True,
        include_button=True):
        """Générateur sur les clés filles.
        
        Parameters
        ----------
        include_ghost : bool, default False
            Les clés fantôme doivent-elles être incluses ?
        include_hidden : bool, default True
            Les clés masquées doivent-elles être incluses ?
        include_button : bool, default True
            Les boutons doivent-ils être inclus ?
        
        Yields
        ------
        WidgetKey
        
        """
        for child in self.children:
            if ( include_ghost or not child.is_ghost ) \
                and ( include_hidden or not child.hidden_m ) \
                and ( include_hidden or not child.hidden_b ) \
                and ( include_button or not child.kind in \
                ('translation button', 'plus button') ):
                yield child


    def siblings(self, include_ghost=False, include_hidden=True,
        include_button=True, include_self=False):
        """Générateur sur les clés soeurs.
        
        Parameters
        ----------
        include_ghost : bool, default False
            Les clés fantôme doivent-elles être incluses ?
        include_hidden : bool, default True
            Les clés masquées doivent-elles être incluses ?
        include_button : bool, default True
            Les boutons doivent-ils être inclus ?
        include_self: bool, default False
            La clé elle-même doit-elle être incluse ?
        
        Yields
        ------
        WidgetKey
        
        """
        if self.parent:
            for sibling in self.parent.children:
                if ( include_ghost or not sibling.is_ghost ) \
                    and ( include_hidden or not sibling.hidden_m ) \
                    and ( include_hidden or not sibling.hidden_b ) \
                    and ( include_button or not sibling.kind in \
                    ('translation button', 'plus button') ) \
                    and ( include_self or not sibling == self ) \
                    and ( include_m or not sibling.is_m ) \
                    and ( include_twin or not sibling == self.m_twin ):
                    yield sibling 

  
    def descendants(self, include_ghost=False, include_hidden=True,
        include_button=True, include_do_not_save=True):
        """Générateur sur les descendants.
        
        Parameters
        ----------
        include_ghost : bool, default False
            Les clés fantôme doivent-elles être incluses ?
        include_hidden : bool, default True
            Les clés masquées doivent-elles être incluses ?
        include_button : bool, default True
            Les boutons doivent-ils être inclus ?
        include_do_not_save : bool, default True
            Les clés à ne pas sauvegarder doivent-elles être
            incluses ?
            
        Notes
        -----
        L'itération respecte l'arborescence - d'abord les parents,
        puis leurs enfants.
        
        Yields
        ------
        WidgetKey
        
        """
        for child in self.children:
            if ( include_ghost or not child.is_ghost ) \
                and ( include_hidden or not child.hidden_m ) \
                and ( include_hidden or not child.hidden_b ) \
                and ( include_do_not_save or not child.do_not_save) \
                and ( include_button or not child.kind in \
                ('translation button', 'plus button') ):
                yield child
                for grandchild in child.descendants(
                    include_ghost=include_ghost,
                    include_hidden=include_hidden,
                    include_button=include_button
                    ):
                    yield granchchild


def relationship_makes_sense(parent_kind, child_kind):
    """Vérifie qu'il n'est pas absurde de rattacher une clé à une autre au vu de leurs objets respectifs.
    
    Parameters
    ----------
    parent_kind : {'edit', 'group of values', 'translation group',
        'group of properties', 'plus button', 'translation button'}
        Nature de l'objet pour lequel est utilisé la clé parente.
    child_kind : {'edit', 'group of values', 'translation group',
        'group of properties', 'plus button', 'translation button'}
        Nature de l'objet pour lequel est utilisé la clé fille.
    
    Returns
    -------
    bool
        True si la relation est licite. False dans le cas contraire.
    """
    d = {
        'group of values': ['edit', 'group of properties', 'plus button'],
        'translation group': ['edit', 'translation button'],
        'group of properties': ['edit', 'group of properties', 'group of values',
            'translation group']
        }
    
    if not parent_kind in d:
        return False
        
    if child_kind in d[parent_kind]:
        return True
    
    return False
    



