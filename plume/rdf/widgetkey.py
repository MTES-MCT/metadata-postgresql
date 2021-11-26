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
    """Clé d'un dictionnaire de widgets.
    
    Attributes
    ----------
    uuid : str
        Identifiant unique de la clé.
    parent : WidgetKey
        La clé parente. None pour une clé racine.
    is_root : bool
        True pour une clé racine, qui n'a pas de parent.
    is_ghost : bool
        True pour une clé non matérialisée. Cet attribut est
        héréditaire.
    is_hidden_m : bool
        True pour la clé présentement masquée d'un couple de
        jumelles, ou toute clé descendant de celle-ci (branche
        masquée). Cet attribut est héréditaire.
    is_hidden_b : bool
        True une clé représentant un bouton masqué.
    row : int
        L'indice de la ligne de la grille occupée par le widget
        porté par la clé. Vaut None pour une clé fantôme.
    rowspan : int
        Nombre de lignes occupées par le ou les widgets portés par
        la clé, étiquette séparée comprise. Vaut 0 pour une
        clé fantôme.
    
    """
    
    def __init__(self, **kwargs):
        """Crée une clé de dictionnaire de widgets.
        
        Parameters
        ----------
        parent : GroupKey, optional
            La clé parente. Vaudra None pour une clé racine.
        is_ghost : bool, optional
            True pour une clé non matérialisée.
        is_hidden_m : bool, optional
            True pour la clé présentement masquée d'un couple de
            jumelles.
        rowspan : int, optional
            Nombre de lignes occupées par le ou les widgets portés par
            la clé. Si non spécifié, sera fixé à 0 si `is_ghost` vaut
            True, sinon génère une erreur.
        actionsbook : ActionsBook, optional
            Si présent, les actions à répercuter sur les widgets
            seront tracées dans ce carnet d'actions.
        
        Notes
        -----
        Les attributs `is_hidden_m` et `is_ghost` seront automatiquement
        mis à True s'ils valent True pour le groupe parent, sans qu'il soit
        nécessaire de le spécifier.
        
        Returns
        -------
        WidgetKey
        
        """
        self.uuid = str(uuid.uuid4())
        self.parent = kwargs.get('parent')
        self.is_root = self.parent is None
        
        if self.is_root and not isinstance(self, GroupOfPropertiesKey):
            raise ForbiddenOperation(self, 'La racine ne peut ' \
                "être qu'un groupe de propriétés.")
        
        self.is_ghost = kwargs.get('is_ghost', False)
        self.is_hidden_m = kwargs.get('is_hidden_m', False)
        self.is_hidden_b = False
        
        if not self.is_root:
            if not self.is_ghost and self.parent.is_ghost:
                self.is_ghost = True
            if not self.is_hidden_m and self.parent.is_hidden_m:
                self.is_hidden_m = True
        
        self.rowspan = 0 if self.is_ghost else kwargs.get('rowspan', 1)
        self.row = None
        
        if not self.is_root:
            self.parent.register_child(self, **kwargs)
        
        actionsbook = kwargs.get('actionsbook')
        if actionsbook:
            actionsbook.create.append(self)
    
    def __str__(self):
        return "WidgetKey {}".format(self.uuid)


class GroupKey(WidgetKey):
    """Clé de dictionnaire de widgets représentant un groupe.
    
    Une "clé de groupe" est une clé qui pourra être désignée comme parent
    d'autres clés, dites "clés filles".
    
    Outre les attributs spécifiques listés ci-après, `GroupKey`
    hérite de tous les attributs de la classe `WidgetKey`.
    
    Attributes
    ----------
    children : list of WidgetKey
        Liste des clés filles.
    
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.children = []
        
    def register_child(self, child_key, **kwargs):
        """Référence une fille dans les clés du groupe.
        
        Cette méthode devrait systématiquement être appliquée après
        toute création de clé. Pour les boutons, les méthodes
        `register_button` des classes `GroupOfPropertiesKey` et
        `TranslationGroupKey` doivent être utilisées à la place.
        
        Parameters
        ----------
        child_key : GroupOfPropertiesKey or EditKey
            La clé de la fille à déclarer.
        actionsbook : ActionsBook, optional
            Si présent, les actions à répercuter sur les widgets
            seront tracées dans ce carnet d'actions.
        no_computation : bool, optional
            Si présent et vaut True, les calculs d'attributs
            ne sont pas immédiatement réalisés.
        
        """
        self.children.append(child_key)
        
        no_computation = kwargs.get('no_computation')
        actionsbook = kwargs.get('actionsbook')
        
        if not no_computation:
            self.compute_rows(actionsbook) 
    
    def kill(self, actionsbook=None):
        """Efface une clé de la mémoire de son parent.
        
        Parameters
        ----------
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
            self.parent.remove(self.m_twin)

        self.parent.compute_rows(actionsbook)
        if isinstance(self.parent, GroupOfValuesKey):
            self.parent.compute_single_children(actionsbook)  
    
    def real_children(self):
        """Générateur sur les clés filles qui ne sont pas des fantômes (ni des boutons).
        
        Yields
        ------
        EditKey or GroupKey
        
        """
        for child in self.children:
            if not child.is_ghost:
                yield child
    
    def compute_rows(self, actionsbook=None):
        """Actualise les indices de lignes des filles du groupe.
        
        Cette méthode devrait être systématiquement appliquée à
        la clé parente après toute création ou effacement de clé.
        
        Parameters
        ----------
        actionsbook : ActionsBook, optional
            Si présent, les actions à répercuter sur les widgets
            seront tracées dans ce carnet d'actions.
        
        Returns
        -------
        int
            L'indice de la prochaine ligne disponible.
        
        Notes
        -----
        `compute_rows` respecte l'ordre des clés filles dans la
        liste de l'attribut `children`.
        
        """      
        n = 0
        for child in self.real_children():
        
            if isinstance(child, EditKey) and child.m_twin:
                continue
                # traitée ensuite avec la jumelle
            
            if child.row != n:
                child.row = n
                if actionsbook:
                    actionsbook.move.append(child)
                if isinstance(child, GroupOfPropertiesKey) and child.m_twin:
                    child.m_twin.row = n
                    if actionsbook:
                        actionsbook.move.append(child.m_twin)
            
            n += child.rowspan
            
        return n


class GroupOfPropertiesKey(GroupKey):
    """Clé de dictionnaire de widgets représentant un groupe de propriétés.
    
    Une "clé de groupe de propriétés" représente un couple prédicat / noeud
    vide, ce dernier étant à la fois un objet et un sujet. Ses filles
    représentent les différents prédicats qui décrivent le sujet.
    
    Outre les attributs spécifiques listés ci-après, `GroupOfPropertiesKey`
    hérite de tous les attributs de la classe `GroupKey`.
    
    Attributes
    ----------
    m_twin : EditKey
        Le cas échéant, une clé dite "jumelle", occupant la même ligne
        de la grille.
    is_single_child : bool
        True si le parent est un groupe de valeurs et il n'y a qu'une
        seule valeur dans le groupe.
    
    """
    def __init__(self, **kwargs):
        self.is_single_child = None
        self.m_twin = kwargs.get('m_twin')
        super().__init__(**kwargs)

    def register_child(self, child_key, **kwargs):
        """Référence une fille dans les clés du groupe.
        
        Parameters
        ----------
        child_key : GroupKey or EditKey
            La clé de la fille à déclarer.
        **kwargs : dict
            Autres paramètres, passés à la méthode `register_child`
            de la classe `GroupKey`.
        
        """
        if not isinstance(child_key, (GroupKey, EditKey)):
            raise ForbiddenOperation(child_key, 'Ce type de clé ne ' \
                'peut pas être ajouté à un groupe de propriétés.')
        super().register_child(child_key, **kwargs)

    def register_m_twin(self, m_twin_key):
        """Référence une clé de widget de saisie auprès de sa jumelle groupe de propriétés.
        
        Parameters
        ----------
        m_twin_key : EditKey
            La clé jumelle à déclarer.
        """
        if self.is_root :
            raise ForbiddenOperation(self, 'Une clé racine ne peut ' \
                'pas avoir de jumelle.')
        
        if self.m_twin and self.m_twin != m_twin_key:
            raise IntegrityBreach(self, 'Une autre jumelle est déjà' \
                ' référencée.')
        
        if not isinstance(m_twin_key, EditKey):
            raise ForbiddenOperation(self, 'La clé jumelle devrait ' \
                'être un widget de saisie.')
        
        if self.parent != m_twin_key.parent:
            raise IntegrityBreach(self, 'La clé et sa jumelle ' \
                'devraient avoir la même clé parent.')
        
        if not self.parent.is_hidden_m \
            and self.is_hidden_m == self.m_twin_key.is_hidden_m:
            raise IntegrityBreach(self, 'Une et une seule des clés ' \
                'jumelles devrait être masquée (is_hidden_m).')
        
        if self.rowspan != m_twin_key.rowspan:
            raise IntegrityBreach(self, "L'attribut rowspan devrait" \
                ' être identique pour les deux clés jumelles.')
        
        self.m_twin = m_twin_key

    def hide_m(self, actionsbook):
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
        self.is_hidden_m = not self.is_hidden_m
        
        if actionsbook and self.hidden_m:
            actionsbook.show.append(self)
        elif actionsbook:
            actionsbook.hide.append(self)
            
        for child in self.real_children():
            child._hide_m(actionsbook)
            
        if self.button:
            button._hide_m(actionsbook)


class GroupOfValuesKey(GroupKey):
    """Clé de dictionnaire de widgets représentant un groupe de valeurs.
    
    Une "clé de groupe de valeurs" est une clé de groupe dont les filles,
    qui peuvent être des `GroupOfPropertiesKey` ou des `EditKey`,
    représentent les différents objets d'un même couple sujet / prédicat.
    
    Outre les attributs spécifiques listés ci-après, `GroupOfValuesKey`
    hérite de tous les attributs de la classe `GroupKey`.
    
    Attributes
    ----------
    button : PlusButtonKey
        Référence la clé qui représente le bouton du groupe.
    
    """
    def __init__(self, **kwargs):
        self.button = None
        super().__init__(**kwargs)
    
    def register_child(self, child_key, **kwargs):
        """Référence une fille dans les clés du groupe.
        
        Cette méthode devrait systématiquement être appliquée après
        toute création de clé. Pour les boutons, la méthode
        `register_button` doit être utilisée à la place.
        
        Parameters
        ----------
        child_key : GroupOfPropertiesKey or EditKey or PlusButtonKey
            La clé de la fille à déclarer.
        actionsbook : ActionsBook, optional
            Si présent, les actions à répercuter sur les widgets
            seront tracées dans ce carnet d'actions.
        no_computation : bool, optional
            Si présent et vaut True, les calculs d'attributs
            ne sont pas immédiatement réalisés.
        **kwargs : dict
            Autres paramètres, passés à la méthode `register_child`
            de la classe `GroupKey`.
        
        """
        if isinstance(child_key, PlusButtonKey):
            self.register_button(child_key, **kwargs)
            return
        
        if not isinstance(child_key, (EditKey, GroupOfPropertiesKey)):
            raise ForbiddenOperation(child_key, 'Ce type de clé ne ' \
                'peut pas être ajouté à un groupe de valeur.')
        
        super().register_child(child_key, **kwargs)
        
        no_computation = kwargs.get('no_computation')
        actionsbook = kwargs.get('actionsbook')
        if not no_computation:
            self.compute_single_children(actionsbook)
    
    def register_button(self, button_key, **kwargs):
        """Référence le bouton plus du groupe.
        
        Cette méthode devrait systématiquement être appliquée après
        toute création de bouton.
        
        Parameters
        ----------
        button_key : PlusButtonKey
            La clé du bouton à déclarer.
        actionsbook : ActionsBook, optional
            Si présent, les actions à répercuter sur les widgets
            seront tracées dans ce carnet d'actions.
        no_computation : bool, optional
            Si présent et vaut True, les calculs d'attributs
            ne sont pas immédiatement réalisés.
        
        """
        if not isinstance(button_key, PlusButtonKey):
            raise ForbiddenOperation(button_key, 'Cette clé ' \
                "n'est pas un bouton plus.")

        if self.button and self.button != button_key:
            raise IntegrityBreach(button_key, 'Un bouton est ' \
                'déjà référencé dans le groupe parent.')
        self.button = button_key
        
        no_computation = kwargs.get('no_computation')
        actionsbook = kwargs.get('actionsbook')
        if not no_computation:
            self.compute_rows(actionsbook)

    def compute_rows(self, actionsbook=None):
        """Actualise les indices de lignes des filles du groupe.
        
        Cette méthode devrait être systématiquement appliquée à
        la clé parente après toute création ou effacement de clé.
        
        Parameters
        ----------
        actionsbook : ActionsBook, optional
            Si présent, les actions à répercuter sur les widgets
            seront tracées dans ce carnet d'actions.
            
        Returns
        -------
        int
            L'indice de la prochaine ligne disponible.
        
        """
        n = super().compute_rows(actionsbook)
        self.button.row = n
        return n + 1

    def compute_single_children(self, actionsbook=None):
        """Actualise l'attribut `is_single_child` des clés filles du groupe.
        
        Cette méthode devrait systématiquement être appliquée après toute
        création ou effacement de clé.
        
        Parameters
        ----------
        actionsbook : ActionsBook, optional
            Si présent, les actions à répercuter sur les widgets
            seront tracées dans ce carnet d'actions.
        
        """
        true_children_count = sum([
            1 for c in self.children if not c.is_ghost and \
            (not isinstance(self, GroupOfPropertiesKey) or not self.m_twin)
            ])
        
        for child in self.real_children():
            # boutons moins à afficher
            if true_children_count >= 2 \
                and child.is_single_child:
                child.is_single_child = False
                if actionsbook:
                    actionsbook.show_minus_button.append(child)
            # boutons moins à masquer
            if true_children_count < 2 \
                and not child.is_single_child:
                child.is_single_child = True
                if actionsbook:
                    actionsbook.hide_minus_button.append(child) 


class TranslationGroupKey(GroupOfValuesKey):
    """Clé de dictionnaire de widgets représentant un groupe de traduction.
    
    Une "clé de groupe de traduction" est une clé de groupe dont les filles
    représentent les traductions d'un objet.
    
    Outre les attributs spécifiques listés ci-après, `TranslationGroupKey`
    hérite de tous les attributs de la classe `GroupOfValuesKey`.
    
    Attributes
    ----------
    available_languages : list of str
        Liste des langues encore disponibles pour les traductions.
    
    """
    def __init__(self, **kwargs):
        """Crée une clé représentant un groupe de traduction.
        
        Parameters
        ----------
        available_languages : list of str
            Liste des langues disponibles pour les traductions.
        **kwargs : dict
            Autres paramètres, passés à la méthode `__init__`
            de la classe `GroupOfValuesKey`.
        
        Returns
        -------
        TranslationGroupKey
        
        """
        self.available_languages = kwargs.get('available_languages')
        if self.available_languages is None:
            raise MissingParameter('available_languages', self)
        super().__init__(**kwargs)

    def register_button(self, button_key, **kwargs):
        """Référence le bouton de traduction du groupe.
        
        Cette méthode devrait systématiquement être appliquée après
        toute création de bouton de traduction.
        
        Parameters
        ----------
        button_key : TranslationButtonKey
            La clé du bouton à déclarer.
        
        """
        if not isinstance(button_key, TranslationButtonKey):
            raise ForbiddenOperation(button_key, 'Cette clé ' \
                "n'est pas un bouton de traduction.")
        super().register_button(button_key, **kwargs)
    
    def register_child(self, child_key, **kwargs):
        """Référence une fille dans les clés du groupe de traduction.
        
        Cette méthode devrait systématiquement être appliquée après
        toute création de clé.
        
        Parameters
        ----------
        child_key : EditKey or TranslationButtonKey
            La clé de la fille à déclarer.
        widget_language : str
            Langue utilisée par le widget.
        **kwargs : dict
            Autres paramètres, passés à la méthode `register_child`
            de la classe `GroupOfValuesKey`.
        
        """
        if isinstance(child_key, TranslationButtonKey):
            self.register_button(child_key, **kwargs)
            return
        
        if not isinstance(child_key, EditKey):
            raise ForbiddenOperation(child_key, 'Ce type de clé ne ' \
                'peut pas être ajouté à un groupe de traduction.')
        super().register_child(child_key, **kwargs)
        
        widget_language = kwargs.get('widget_language')
        if not widget_language:
            raise MissingParameter('widget_language', child_key)
        
        actionsbook = kwargs.get('actionsbook')
        self.language_out(widget_language, actionsbook)

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
        if not widget_language:
            raise MissingParameter('widget_language', self)
        
        if widget_language in self.available_languages:
            raise IntegrityBreach(
                self,
                "La langue '{}' est déjà dans la liste" \
                " des langues disponibles.".format(widget_language)
                )
        
        self.available_languages.append(widget_language)
        if actionsbook:
            for child in self.real_children():
                actionsbook.languages.append(child)
        
        if self.button and len(self.available_languages) == 1:
            self.button.is_hidden_b = False
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
        if not widget_language:
            raise MissingParameter('widget_language', self)
        
        if not widget_language in self.available_languages:
            return
            # on admet que la langue ait pu ne pas se trouver
            # dans la liste (métadonnées importées, etc.)
        
        self.available_languages.remove(widget_language)
    
        if actionsbook:
            for child in self.real_children():
                actionsbook.languages.append(child)
        
        if not self.available_languages and self.button:
            self.button.is_hidden_b = True
            if actionsbook:
                actionsbook.hide.append(self.button)


class EditKey(WidgetKey):
    """Clé de dictionnaire de widgets représentant un widget de saisie.
    
    Attributes
    ----------
    m_twin : GroupOfPropertiesKey
        Le cas échéant, une clé dite "jumelle", occupant la même ligne
        de la grille.
    is_single_child : bool
        True si le parent est un groupe de valeurs et il n'y a qu'une
        seule valeur dans le groupe.
    
    """
    def __init__(self, **kwargs):
        self.is_single_child = None
        self.m_twin = kwargs.get('m_twin')
        if kwargs.get('rowspan') is None:
            raise MissingParameter('rowspan', self)
        super().__init__(**kwargs)
    
    def kill(self, widget_language=None, actionsbook=None):
        """Efface une clé de la mémoire de son parent.
        
        Parameters
        ----------
        widget_language : str, optional
            Langue utilisée par le widget. Devrait toujours être
            spécifiée pour une clé dont la clé parente est un
            groupe de traduction, sauf si la langue en question
            n'était pas autorisée, et ne doit donc pas être reversée
            dans la liste des langues disponibles.
        actionsbook : ActionsBook, optional
            Si présent, les actions à répercuter sur les widgets
            seront tracées dans ce carnet d'actions.
        
        """
        super().kill(actionsbook)
        if isinstance(self.parent, TranslationGroupKey) and widget_language:
            self.parent.language_in(widget_language, actionsbook)


class PlusButtonKey(WidgetKey):
    """Clé de dictionnaire de widgets représentant un bouton plus.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def kill(self, actionsbook=None):
        """Efface une clé bouton de la mémoire de son parent.
        
        Parameters
        ----------
        actionsbook : ActionsBook, optional
            Si présent, les actions à répercuter sur les widgets
            seront tracées dans ce carnet d'actions.
        
        """
        super().kill(actionsbook)
        self.parent.button = None
        # ne devrait jamais être utilisé, aucun mécanisme
        # ne prévoit de supprimer le bouton d'un groupe
        # sans supprimer également celui-ci.


class TranslationButtonKey(PlusButtonKey):
    """Clé de dictionnaire de widgets représentant un bouton de traduction.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_hidden_b = not self.parent.available_languages

