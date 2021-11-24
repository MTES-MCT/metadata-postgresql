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
from plume.rdf.exceptions import IntegrityBreach
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
    is_m : bool
        True pour une clé de saisie manuelle.
    m_twin : WidgetKey
        Le cas échéant, la clé jumelle.
    children : list of WidgetKey
        Liste des clés filles, vide le cas échéant.
    true_children_count : int
        Nombre de clés filles à représenter. Les clés jumelles
        ne comptent que pour un, les clés fantômes ne compte pas.
    next_row : int
        L'indice de la prochaine ligne disponible dans la grille.
    button : WidgetKey
        Si la clé est utilisée pour un groupe de valeur ou de
        traduction, clé du bouton plus ou bouton de traduction
        du groupe.
    row : int
        L'indice de la ligne de la grille occupée par le widget
        porté par la clé. Vaut None pour une clé fantôme.
    rowspan : int
        Nombre de lignes occupées par le widget porté par la clé.
        Vaut 0 pour une clé fantôme.
    is_ghost : bool
        True pour une clé qui ne porte pas de widget (clé fantôme).
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
    
    def __init__(self, parent, kind, is_m=False, m_twin=None, rowspan=None,
        is_ghost=False, hidden_m=False, hidden_b=False, do_not_save=False,
        available_languages=None, widget_language=None, actionsbook=None):
        """Crée une clé de dictionnaire de widgets.
        
        Parameters
        ----------
        parent : WidgetKey
            La clé parente. Vaudra None pour une clé racine.
        kind : {'edit', 'group of values', 'translation group',
            'group of properties', 'plus button', 'translation button'}
            Nature de l'objet pour lequel est utilisé la clé.
        is_m : bool, default False
            La clé est-elle une clé de saisie manuelle ?
        m_twin : WidgetKey, optional
            Le cas échéant, la clé jumelle.
        rowspan : int, optional
            Nombre de lignes occupées par le widget porté par
            la clé fille, le cas échéant. Si non spécifié,
            sera fixé à 1, ou 0 ssi `is_ghost` vaut True.
            Vaudra toujours 1 pour des clés jumelles, quelle
            que soit la valeur fournie en argument.
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
            seront tracées dans le carnet d'actions.
            
        Notes
        -----
        Les informations relatives aux clés filles sont saisies
        a posteriori.
        
        La nouvelle fille est automatiquement enregistrée dans
        les attributs de la clé parent et, s'il y a lieu, auprès
        de sa jumelle.
        
        Returns
        -------
        WidgetKey

        """
        self.uuid = str(uuid.uuid4())
        self.parent = parent
        self.generation = 0 if parent is None else parent.generation + 1
        self.kind = kind
        self.is_root = parent is None
        self.is_m = is_m
        self.m_twin = m_twin
        
        if actionsbook:
            actionsbook.create.append(self)
        
        # attributs relatifs au widget porté
        # par la clé
        self.is_ghost = is_ghost
        self.hidden_m = hidden_m
        self.do_not_save = do_not_save
        self.rowspan = rowspan or (0 if is_ghost else 1)
        
        # attributs relatifs aux futures filles
        self.children = []
        self.next_row = 0
        self.button = None
        self.true_children_count = 0

        # déclaration auprès de la jumelle et
        # contrôle d'intégrité
        if m_twin:
            self.m_twin.m_twin = self
            if self.hidden_m == self.m_twin.hidden_m:
                raise IntegrityBreach(
                    self,
                    'Une des clés jumelles devrait être masquée (hidden_m).'
                    )
            if self.is_m == self.m_twin.is_m:
                raise IntegrityBreach(
                    self,
                    'Une des clés jumelles devrait être manuelle (is_m).'
                    )

        # déclaration auprès du parent
        self.row = None
        self.hide_minus_button = True
        if parent:
            parent.children.append(self)
            
            if self.kind in ('translation button', 'plus button'):
                self.button = child
            
            if self.m_twin:
                # si une jumelle est spécifiée, la clé réutilise
                # sa ligne
                self.row = self.m_twin.row
                self.rowspan = self.m_twin.rowspan = 1
            
            elif not is_ghost:
                # ... sinon la valeur de l'attribut next_row du
                # parent, qui est incrémentée en retour
                self.row = parent.next_row
                parent.next_row += self.rowspan
                parent.true_children_count += 1

            # boutons moins dans les groupes de valeurs et
            # groupes de traduction
            if parent.kind in ('translation group',
                'group of values'):
                if parent.true_children_count == 3:
                    # bouton plus/de traduction et au moins
                    # deux clés, incluant la nouvelle
                    for child in parent.children:
                        child.hide_minus_button = False
                    if actionsbook:
                        for child in self.siblings(
                            include_hidden=False,
                            include_button=False
                            ):
                            actionsbook.show_minus_button.append(child)
                elif parent.true_children_count > 3:
                    self.hide_minus_button = False

        # gestion des langues
        self.available_languages = None
        self.hidden_b = False
        if kind == 'translation group':
            if available_languages is None:
                raise IntegrityBreach(
                    self,
                    'La liste des langues disponibles pour les ' \
                    'traductions est manquante.'
                    )
            self.available_languages = available_languages
        if kind == 'edit' and parent and parent.kind == 'translation group':
            if not widget_language:
                raise IntegrityBreach(
                    self,
                    'La langue du widget doit être spécifiée.'
                    )
            # la langue utilisée n'est plus disponible :
            if widget_language in self.parent.available_languages:
                parent.available_languages.remove(widget_language)
                # pas d'erreur si la langue n'est pas dans la liste, car
                # on ne maîtrise pas les traductions initialement présentes
                
                if actionsbook:
                    for child in parent.siblings(
                        include_button=False
                        ):
                        actionsbook.languages.append(child)
                
                if not len(parent.available_languages):
                    parent.button.hidden_b = True
                    if actionsbook:
                        actionsbook.hide.append(parent.button)

    
    def __str__(self):
        return "WidgetKey {}".format(self.uuid)
      
    
    def kill(self, widget_language=None):
        """Efface une clé de la mémoire de son parent.
        
        Parameters
        ----------
        widget_language : str
            Langue utilisée par le widget. Devrait toujours être
            spécifiée pour une clé 'edit' dont la clé parente est un
            groupe de traduction, sauf si la langue en question
            n'était pas autorisée, et ne doit donc pas être reversée
            dans la liste des langues disponibles.
        
        Notes
        -----
        Le cas échéant, la clé jumelle sera également effacée,
        il n'y a donc pas lieu d'appeler deux fois cette méthode.
        
        Appliquer cette fonction sur une clé racine ne provoque
        pas d'erreur, elle n'aura simplement aucun effet.
        
        """
        if self.parent:
        
            self.parent.remove(self)
            self.parent.next_row -= self.rowspan
            
            if self.m_twin:
                self.parent.remove(m_twin)
            
            if self.kind in ('translation button', 'plus button'):
                self.parent.button = None
                # ne devrait jamais être utilisé, aucun mécanisme
                # ne prévoit de supprimer le bouton d'un groupe
                # sans supprimer également celui-ci.
                
            # langues diponibles
            if widget_language and self.parent.kind == 'translation group':
                if widget_language in self.parent.available_languages:
                    raise IntegrityBreach(
                        self,
                        "La langue '{}' est déjà dans la liste" \
                        " des langues disponibles.".format(widget_language)
                        )
                self.parent.available_languages.append(widget_language)
                if len(self.parent.available_languages) == 1:
                    self.parent.button.hidden_b = False
            
            # boutons moins
            if self.parent.kind in ('translation group',
                'group of values'):
                if len(self.parent.children == 2):
                    # 2, car bouton plus/de traduction
                    # + une unique valeur restante
                    for child in self.parent.children:
                        child.hide_minus_button = True


    def hide_m(self, rec=False):
        """Marque une clé d'un couple de jumelles et ses descendantes comme masquées.
        
        Par symétrie, la clé jumelle et ses descendantes seront
        marquées comme non masquées (`hidden_m` valant False).
        
        """
        if not rec:
            if not self.m_twin:
                raise IntegrityBreach(self, "Pas de clé jumelle renseignée.")
            self.m_twin._hide_m()
        self._hide_m()   


    def _hide_m(self):
        self.hidden_m = not self.hidden_m
        for child in self.children:
            child.hide_m()
            
    
    def children(self, include_ghost=False, include_hidden=True,
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

   
