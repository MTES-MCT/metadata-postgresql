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

from uuid import uuid4
from plume.rdf.exceptions import IntegrityBreach, MissingParameter, ForbiddenOperation, \
    UnknownParameterValue
from plume.rdf.actionsbook import ActionsBook

try:
    from rdflib import URIRef, BNode, RDF
except:
    from plume.bibli_install.bibli_install import manageLibrary
    # installe RDFLib si n'est pas déjà disponible
    manageLibrary()
    from rdflib import URIRef, BNode, RDF


class WidgetKey:
    """Clé d'un dictionnaire de widgets.
    
    Attributes
    ----------
    uuid : UUID
        Identifiant unique de la clé.
    parent : WidgetKey
        La clé parente. None pour une clé racine (`RootKey`).
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
            True, sinon à 1 pour tout ce qui n'est pas un widget de saisie.
            Obligatoire pour un widget de saisie.
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
        self.uuid = uuid4()
        self.parent = kwargs.get('parent')
        if not self.parent:
            raise MissingParameter('parent', self)
        
        self.is_ghost = kwargs.get('is_ghost', False)
        if self.is_ghost and not isinstance(self, (EditKey,
            GroupOfPropertiesKey, GroupOfValuesKey)):
            raise ForbiddenOperation(self, "Ce type de clé ne " \
                "peut être un fantôme.")
        
        self.is_hidden_m = kwargs.get('is_hidden_m', False)
        self.is_hidden_b = False
        
        if not self.is_ghost and self.parent.is_ghost:
            self.is_ghost = True
        if not self.is_hidden_m and self.parent.is_hidden_m:
            self.is_hidden_m = True
        
        if not self.is_ghost and isinstance(self, EditKey):
            self.rowspan = kwargs.get('rowspan')
            if self.rowspan is None:
                raise MissingParameter('rowspan', self)
        else:
            self.rowspan = 0 if self.is_ghost else 1
        self.row = None
        
        if isinstance(self, (EditKey, GroupOfPropertiesKey)) \
            and self.m_twin:
            self.m_twin.register_m_twin(self)
        
        self.parent.register_child(self, **kwargs)
        
        actionsbook = kwargs.get('actionsbook')
        if actionsbook:
            actionsbook.create.append(self)
    
    def __str__(self):
        return "WidgetKey {}".format(self.uuid)

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
        if isinstance(self, RootKey):
            return
        
        self.parent.children.remove(self)
        
        if actionsbook:
            actionsbook.drop.append(self)
        
        if isinstance(self, (EditKey, GroupOfPropertiesKey)) \
            and self.m_twin:
            self.parent.children.remove(self.m_twin)

        self.parent.compute_rows(actionsbook)
        if isinstance(self.parent, GroupOfValuesKey):
            self.parent.compute_single_children(actionsbook)  

    def register_m_twin(self, m_twin_key):
        """Référence une clé auprès de sa jumelle.
        
        Parameters
        ----------
        m_twin_key : EditKey or GroupOfPropertiesKey
            La clé jumelle à déclarer.
        
        """
        if isinstance(self, RootKey) :
            raise ForbiddenOperation(self, 'Une clé racine ne peut ' \
                'pas avoir de jumelle.')
        
        if self.m_twin and self.m_twin != m_twin_key:
            raise IntegrityBreach(self, 'Une autre jumelle est déjà' \
                ' référencée.')
        
        if not isinstance(self, (EditKey, GroupOfPropertiesKey)):
            raise ForbiddenOperation(self, 'Seul un widget de saisie ' \
                'ou un groupe de propriétés peut avoir une clé jumelle.')
        
        if isinstance(self, GroupOfPropertiesKey) \
            and not isinstance(m_twin_key, EditKey):
            raise ForbiddenOperation(self, 'La clé jumelle devrait ' \
                'être un widget de saisie.')
        
        if isinstance(self, EditKey) \
            and not isinstance(m_twin_key, GroupOfPropertiesKey):
            raise ForbiddenOperation(self, 'La clé jumelle devrait ' \
                'être un groupe de propriétés.')
        
        if self.parent != m_twin_key.parent:
            raise IntegrityBreach(self, 'La clé et sa jumelle ' \
                'devraient avoir la même clé parent.')
        
        if not self.parent.is_hidden_m \
            and self.is_hidden_m == m_twin_key.is_hidden_m:
            raise IntegrityBreach(self, 'Une et une seule des clés ' \
                'jumelles devrait être masquée (is_hidden_m).')
        
        if self.rowspan != m_twin_key.rowspan:
            raise IntegrityBreach(self, "L'attribut rowspan devrait" \
                ' être identique pour les deux clés jumelles.')
        
        self.m_twin = m_twin_key

    def hide_m(self, actionsbook=None):
        """Inverse la visibilité d'un couple de jumelles (et leurs descendantes).
        
        Parameters
        ----------
        actionsbook : ActionsBook, optional
            Si présent, les actions à répercuter sur les widgets
            seront tracées dans ce carnet d'actions.
        
        """
        if not isinstance(self, (GroupOfPropertiesKey, EditKey)):
            raise ForbiddenOperation('Cette méthode ne peut être ' \
                "appliquée qu'à des clés de groupe de propriétés ou " \
                'de widget de saisie.')
        
        if not self.m_twin:
            raise IntegrityBreach(self, 'Pas de clé jumelle renseignée.')
        self.m_twin._hide_m(actionsbook)
        self._hide_m(actionsbook)   

    def _hide_m(self, actionsbook):
        self.is_hidden_m = not self.is_hidden_m
        
        if actionsbook and not self.is_hidden_m:
            actionsbook.show.append(self)
        elif actionsbook:
            actionsbook.hide.append(self)
        
        if isinstance(self, GroupKey):
            for child in self.real_children():
                child._hide_m(actionsbook)
                
        if isinstance(self, GroupOfValuesKey) and self.button:
            button._hide_m(actionsbook)


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
            if isinstance(child, GroupOfPropertiesKey) \
                and child.m_twin and child.m_twin.row != n:
                child.m_twin.row = n
                if actionsbook:
                    actionsbook.move.append(child.m_twin)
            
            n += child.rowspan
            
        return n


class RootKey(GroupKey):
    """Clé de dictionnaire de widgets représentant la racine du graphe RDF.
    
    Outre ses attributs propres listés ci-après, `RootKey` hérite
    des attributs de la classe `GroupKey`. Une clé racine n'a pas
    de parent. Elle porte l'identifiant du jeu de données, dans
    son attribut `object`.
    
    Attributes
    ----------
    node : URIRef
        L'identifiant du jeu de données, qui sera le sujet des
        triplets des enfants du groupe.
    rdftype : URIRef
        La classe de l'objet RDF décrit par le groupe racine.
        Vaut toujours URIRef("http://www.w3.org/ns/dcat#Dataset").
    
    """
    def __init__(self, datasetid, **kwargs):
        """Crée une clé racine.
        
        Parameters
        ----------
        datasetid : URIRef
            L'identifiant du graphe de métadonnées.
        rdftype : URIRef
            La classe de l'objet RDF décrit par le groupe.
        
        Returns
        -------
        GroupOfPropertiesKey
        
        """
        if not isinstance(datasetid, URIRef):
            raise TypeError('datasetid doit être de type URIRef.')
        self.parent = None
        self.node = datasetid
        self.rdftype = URIRef("http://www.w3.org/ns/dcat#Dataset")
        self.uuid = uuid4()
        self.is_ghost = False
        self.is_hidden_m = False
        self.is_hidden_b = False
        self.rowspan = 0
        self.row = None
        self.children = []
        actionsbook = kwargs.get('actionsbook')
        if actionsbook:
            actionsbook.create.append(self)
 
    def object(self):
        """Renvoie une transcription littérale de la classe de la clé.
        
        """
        return 'root'

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
                'peut pas être ajouté au groupe racine.')
        super().register_child(child_key, **kwargs)


class TabKey(GroupKey):
    """Clé de dictionnaire de widgets représentant un onglet.
    
    Les onglets doublent leur groupe de propriétés parent sans porter
    aucune information sur la structure du graphe RDF.
    
    `TabKey` hérite des attributs de la classe `GroupKey`.
    
    """
    def object(self):
        """Renvoie une transcription littérale de la classe de la clé.
        
        """
        return 'tab'

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
                'peut pas être ajouté à un onglet.')
        super().register_child(child_key, **kwargs)


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
    predicate : URIRef
        Le prédicat représenté par le groupe de propriétés.
    node : BNode
        Le noeud vide objet du prédicat, qui est également le sujet des
        triplets des enfants du groupe.
    rdftype : URIRef
        La classe de l'objet RDF décrit par le groupe.
    
    """
    def __init__(self, rdftype, **kwargs):
        """Crée une clé de groupe de propriétés.
        
        Parameters
        ----------
        m_twin : EditKey
            Le cas échéant, une clé dite "jumelle", occupant la même
            ligne de la grille. Cette information doit être fournie 
            lorsque la clé a une jumelle et que celle-ci a déjà été
            créée (donc toujours sur la seconde jumelle déclarée).
        predicate : URIRef, optional
            Le prédicat représenté par le groupe de propriétés. Dans
            un groupe de valeurs, il sera déduit du prédicat
            porté par le groupe, sinon il doit obligatoirement être
            fourni.
        node : BNode, optional
            Le noeud vide objet du prédicat, qui est également le sujet
            des triplets des enfants du groupe. Si non fourni, un nouveau
            noeud vide est généré.
        rdftype : URIRef
            La classe de l'objet RDF décrit par le groupe.
        
        Returns
        -------
        GroupOfPropertiesKey
        
        """
        self.is_single_child = None
        self.m_twin = kwargs.get('m_twin')
        
        self.predicate = kwargs.get('predicate')
        super().__init__(**kwargs)
        
        if not self.predicate:
            raise MissingParameter('predicate')
        self.rdftype = rdftype
        node = kwargs.get('node')
        
        if node and isinstance(node, BNode):
            self.node = node
        else:
            self.node = BNode()
 
    def object(self):
        """Renvoie une transcription littérale de la classe de la clé.
        
        """
        return 'group of properties'

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
    predicate : URIRef
        Le prédicat commun à toutes les valeurs du groupe.
    sources : list of URIRef, optional
        Liste des sources de vocabulaire contrôlé pour les valeurs
        du groupe, qui sert à construire son attribut `sources`.
    
    """
    def __init__(self, **kwargs):
        self.button = None
        self.predicate = kwargs.get('predicate')
        if not self.predicate:
            raise MissingParameter('predicate')
        self.sources = kwargs.get('sources')
        super().__init__(**kwargs)
        
    def object(self):
        """Renvoie une transcription littérale de la classe de la clé.
        
        """
        return 'group of values'
    
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
        child_key.predicate = self.predicate
        child_key.sources = self.sources
        
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
        if self.button:
            self.button.row = n
            if actionsbook:
                actionsbook.move.append(self.button)
            n += 1
        return n

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
            (not isinstance(c, GroupOfPropertiesKey) or not c.m_twin)
            ])
        
        for child in self.real_children():
            # boutons moins à afficher
            if true_children_count >= 2 \
                and not child.is_single_child is False:
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
        if kwargs.get('sources'):
            raise ForbiddenOperation('Les sources contrôlées ne sont ' \
                'pas autorisées dans un groupe de traduction.')
        super().__init__(**kwargs)

    def object(self):
        """Renvoie une transcription littérale de la classe de la clé.
        
        """
        return 'translation group'

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
        if child_key.value_type != RDF.langString:
            raise ForbiddenOperation(child_key, 'Seul le type' \
                ' rdf:langString est autorisé dans un groupe ' \
                'de traduction.')
        
        super().register_child(child_key, **kwargs)
        
        if kwargs.get('no_value'):
            if not self.available_languages:
                raise IntegrityBreach(child_key, 'Plus de langue ' \
                    'disponible.')
            child_key.language_value = self.available_languages[0]
        
        actionsbook = kwargs.get('actionsbook')
        child_key.unauthorized_language = not self.language_out(
            child_key.value_language, actionsbook)

    def language_in(self, value_language, actionsbook=None):
        """Ajoute une langue à la liste des langues disponibles.
        
        Parameters
        ----------
        value_language : str
            Langue redevenue disponible.
        actionsbook : ActionsBook, optional
            Si présent, les actions à répercuter sur les widgets
            seront tracées dans ce carnet d'actions.
        
        """        
        if not value_language:
            raise MissingParameter('value_language', self)
        
        if value_language in self.available_languages:
            raise IntegrityBreach(
                self,
                "La langue '{}' est déjà dans la liste" \
                " des langues disponibles.".format(value_language)
                )
        
        self.available_languages.append(value_language)
        if actionsbook:
            for child in self.real_children():
                actionsbook.languages.append(child)
        
        if self.button and len(self.available_languages) == 1:
            self.button.is_hidden_b = False
            if actionsbook:
                actionsbook.show.append(self.button)

    def language_out(self, value_language, actionsbook=None):
        """Retire une langue de la liste des langues disponibles.
        
        Parameters
        ----------
        value_language : str
            Langue désormais non disponible.
        actionsbook : ActionsBook, optional
            Si présent, les actions à répercuter sur les widgets
            seront tracées dans ce carnet d'actions.
        
        Returns
        -------
        bool
            True si la langue retirée était bien disponible.
        """        
        if not value_language:
            raise MissingParameter('value_language', self)
        
        if not value_language in self.available_languages:
            return False
            # on admet que la langue ait pu ne pas se trouver
            # dans la liste (métadonnées importées, etc.)
        
        self.available_languages.remove(value_language)
    
        if actionsbook:
            for child in self.real_children():
                actionsbook.languages.append(child)
        
        if not self.available_languages and self.button:
            self.button.is_hidden_b = True
            if actionsbook:
                actionsbook.hide.append(self.button)
        
        return True


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
    predicate : URIRef
        Le prédicat représenté par la clé.
    sources : list of URIRef, optional
        Liste des sources de vocabulaire contrôlé pour les valeurs
        de la clé, qui sert à construire l'attribut `sources` de la clé.
        Dans un groupe de valeurs, ce dernier est déduit de
        l'attribut `sources` du groupe.
    value_type : URIRef
        Le type (xsd:type) de l'objet du triplet. None si l'objet n'est
        pas un Literal.
    value_language : str
        La langue de l'objet. None si l'objet n'est pas un Literal de
        type rdf:langString. Obligatoirement renseigné dans un groupe
        de traduction.
    unauthorized_language : bool
        True si la langue n'est pas autorisée. Cet attribut est calculé
        automatiquement. Il vaudra True si, à l'initialisation de la
        clé, la langue de l'objet n'était pas dans la liste des langues
        disponibles du groupe de traduction parent. Vaut toujours False
        si le parent n'est pas un groupe de traduction.
    value_transform : str
        Le cas échéant, la nature de la transformation appliquée à
        l'objet.
    value_source : URIRef
        La source utilisée par la valeur courante de la clé.
    do_not_save : bool
        True pour une information qui ne devra pas être sauvegardée.
    
    Notes
    -----
    L'objet du triplet est porté par le dictionnaire interne
    associé à la clé et non par la clé elle-même.
    
    """
    def __init__(self, **kwargs):
        """Crée une clé de widget de saisie.
        
        Parameters
        ----------
        predicate : URIRef, optional
            Le prédicat représenté par la clé. Dans un groupe de valeurs
            ou groupe de traduction, il sera déduit du prédicat
            porté par le groupe, sinon il doit obligatoirement être
            fourni.
        sources : list of URIRef, optional
            Liste des sources de vocabulaire contrôlé pour les valeurs
            de la clé, qui sert à construire l'attribut `sources` de la clé.
            Dans un groupe de valeurs, ce dernier est déduit de
            l'attribut `sources` du groupe.
        m_twin : GroupOfPropertiesKey, optional
            Le cas échéant, une clé dite "jumelle", occupant la même
            ligne de la grille. Cette information doit être fournie 
            lorsque la clé a une jumelle et que celle-ci a déjà été
            créée (donc toujours sur la seconde jumelle déclarée).
        do_not_save : bool, default False
            True pour une information qui ne devra pas être sauvegardée.
        value_type : URIRef, optional
            Le type (xsd:type) de l'objet du triplet. Si non renseigné
            et que `value_language` est fourni, il sera considéré que
            l'objet est de type rdf:langString, sinon il sera considéré que
            les valeurs sont des URIRef.
        value_transform : str, optional
            Le cas échéant, la nature de la transformation appliquée à
            l'objet.
        no_value : bool, default False
            True s'il n'y a actuellement aucune valeur associée à la clé.
            Dans ce cas, `value_language` et `value_source` seront renseignés
            automatiquement.
        value_language : str, optional
            La langue de l'objet. Obligatoire pour un Literal de
            type rdf:langString et a fortiori dans un groupe de traduction,
            ignoré pour tous les autres types.
        value_source : tuple of URIRef and str
            La source utilisée par la valeur courante de la clé, représentée
            par un tuple dont le premier élément est l'IRI de la source et
            le second la langue utilisée. Si la valeur fournie pour l'IRI
            ne fait pas partie des sources autorisées, elle sera
            silencieusement supprimée.
        language : str, default 'fr'
            Langue principale de saisie des métadonnées (à ne pas confondre
            avec `value_language`). Cette information n'est utilisée que si
            `no_value` vaut True, pour générer automatiquement `value_source`
            s'il y a lieu.
        
        Returns
        -------
        EditKey
        
        """
        self.is_single_child = None
        self.m_twin = kwargs.get('m_twin')
        self.do_not_save = kwargs.get('do_not_save', False)
        
        self.value_transform = kwargs.get('value_transform')
        self.value_type = kwargs.get('value_type')
        no_value = kwargs.get('no_value')
        value_language = kwargs.get('value_language')
        
        if value_language and not self.value_type:
            self.value_type = RDF.langString
            self.value_language = value_language
        elif self.value_type == RDF.langString:
            if not value_language and not no_value:
                raise MissingParameter('value_language')
            self.value_language = value_language
        else:
            self.value_language = None            
        
        self.sources = kwargs.get('sources')
        self.predicate = kwargs.get('predicate')
        # dans un groupe de valeurs, sources et predicate
        # seront écrasés par les valeurs du groupe
        super().__init__(**kwargs)
        if not self.predicate:
            raise MissingParameter('predicate')
        
        value_source = kwargs.get('value_source')
        if self.sources and no_value:
            language = kwargs.get('language', 'fr')
            self.value_source = (self.sources[0], language)
        elif value_source and self.sources \
            and value_source[0] in self.sources:
            self.value_source = value_source

    def object(self):
        """Renvoie une transcription littérale de la classe de la clé.
        
        """
        return 'edit'
       
    def change_language(self, value_language, actionsbook=None):
        """Déclare une nouvelle langue pour la clé.
        
        Parameters
        ----------
        value_language : str
            Nouvelle langue.
        actionsbook : ActionsBook, optional
            Si présent, les actions à répercuter sur les widgets
            seront tracées dans ce carnet d'actions.
        
        """
        if not self.value_language:
            raise ForbiddenOperation(self, 'Pas de langue attendue ' \
                'pour cette clé.')
        if isinstance(self.parent, TranslationGroupKey):
            if not self.unauthorized_language:
                self.parent.language_in(self.value_language)
                # NB : on ne met pas actionsbook en argument de
                # language_in, parce qu'il renverrait exactement
                # les mêmes informations que language_out, exécuté
                # juste après
            self.unauthorized_language = not self.parent.language_out(
                value_language, actionsbook)
        self.value_language = value_language
    
    def change_source(self, value_source, actionsbook=None):
        """Déclare une nouvelle source pour la clé.
        
        Parameters
        ----------
        value_source : tuple of URIRef and str
            Nouvelle source. Tuple dont le premier élément est
            l'IRI de la source, le second la langue.
        actionsbook : ActionsBook, optional
            Si présent, les actions à répercuter sur les widgets
            seront tracées dans ce carnet d'actions.
        
        """
        if self.sources 
            and (not value_source or value_source[0] in self.sources) \
            and value_sources != self.value_source:
            self.value_source = value_source
            if actionsbook:
                actionsbook.sources.append(self)
                actionsbook.thesaurus.append(self)
    
    def kill(self, actionsbook=None):
        """Efface une clé de la mémoire de son parent.
        
        Parameters
        ----------
        actionsbook : ActionsBook, optional
            Si présent, les actions à répercuter sur les widgets
            seront tracées dans ce carnet d'actions.
        
        """
        super().kill(actionsbook)
        if isinstance(self.parent, TranslationGroupKey) \
            and self.value_language and not self.unauthorized_language:
            self.parent.language_in(self.value_language, actionsbook)

    def parse_value(self, value):
        """Prépare une valeur en vue de son enregistrement dans un graphe de métadonnées.
        
        Parameters
        ----------
        value : str
            La valeur, exprimée sous la forme d'une chaîne de caractères.
        
        Returns
        -------
        Literal or URIRef
        
        """
        if value in (None, ''):
            return
        if self.value_language:
            return Literal(value, lang=self.value_language)
        if self.value_type:
            return Literal(value, datatype=self.value_type)
        if self.value_transform == 'email':
            return owlthing_from_email(value)
        if self.value_transform == 'phone':
            return owlthing_from_tel(value)
        if self.value_source:
            res = Thesaurus.values(self.value_source).parser(value)
            if res:
                return res
        f = forbidden_char(value)
        if f:
            raise ForbiddenOperation(self, "Le caractère '{}' " \
                "n'est pas autorisé dans un IRI.".format(f))
        return URIRef(value)


class PlusButtonKey(WidgetKey):
    """Clé de dictionnaire de widgets représentant un bouton plus.
    
    """   
    def object(self):
        """Renvoie une transcription littérale de la classe de la clé.
        
        """
        return 'plus button'
    
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

    def object(self):
        """Renvoie une transcription littérale de la classe de la clé.
        
        """
        return 'translation button'

    
def forbidden_char(anystr):
    """Le cas échéant, renvoie le premier caractère de la chaîne qui ne soit pas autorisé dans un IRI.
    
    Parameters
    ----------
    anystr : str
        La chaîne de caractères à tester.
    
    Returns
    -------
    str
        Si la chaîne contient au moins un caractère interdit, l'un
        de ces caractères.
    
    Example
    -------
    >>> forbidden_char('avec des espaces')
    ' '
    
    """
    r = re.search(r'([<>"\s{}|\\^`])', anystr)
    return r[1] if r else None


