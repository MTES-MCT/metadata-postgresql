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
    
    *Cette classe ne doit pas être utilisée directement, on préfèrera toujours
    les classes filles qui héritent de ses méthodes et attributs.*
    
    Parameters
    ----------
    parent : GroupKey
        La clé parente. Ne peut pas être None, sauf dans le cas d'un objet
        de la classe `RootKey` (groupe racine).
    is_ghost : bool, default False
        True si la clé ne doit pas être matérialisée. À noter que quelle
        que soit la valeur fournie à l'initialisation, une fille de clé
        fantôme est toujours un fantôme.
    
    Attributes
    ----------
    actionsbook : ActionsBook
        *Variable partagée entre les instances de la classe.* Le carnet
        d'actions trace les actions à réaliser sur les widgets au fil
        des modifications des clés. Pour le réinitialiser, on utilisera
        la méthode de classe `clear_actionsbook`.
    no_computation : bool
        *Variable partagée entre les instances de la classe.* Si True,
        inhibe temporairement la réalisation de certains calculs.
    main_language : str
        *Propriété communes à toutes les instances.* Langue principale
        de saisie des métadonnées.
    langlist : str
        *Propriété communes à toutes les instances.* Liste des langues
        autorisées.
    uuid : UUID
        *Attribut généré automatiquement.* Identifiant unique de la clé.
    parent : GroupKey
        *Propriété non modifiable après l'initialisation.* La clé parente.
        None pour une clé racine (`RootKey`).
    is_ghost : bool
        *Propriété non modifiable après l'initialisation.* True pour une
        clé non matérialisée et ses descendantes.
    is_hidden_m : bool
        *Propriété non modifiable manuellement.* True pour la clé présentement
        masquée d'un couple de jumelles, ou toute clé descendant de celle-ci
        (branche masquée).
    is_hidden_b : bool
        *Propriété non modifiable manuellement.* True pour une clé représentant
        un bouton masqué.
    row : int
        *Propriété non modifiable manuellement.* L'indice de la ligne de la
        grille occupée par le widget porté par la clé. Vaut None pour une clé
        fantôme.
    rowspan : int
        *Propriété non modifiable manuellement.* Nombre de lignes occupées
        par le ou les widgets portés par la clé, étiquette séparée comprise.
        Vaut 0 pour une clé fantôme.
    is_single_child : bool
        *Propriété non modifiable manuellement*. True si le parent est un
        groupe de valeurs et il n'y a qu'une seule valeur dans le groupe.
    
    Methods
    -------
    clear_actionsbook()
        *Méthode de classe.* Remplace le carnet d'actions par un carnet vierge.
    kill()
        Efface la clé de la mémoire de son parent.
    
    """
    
    _langlist = None
    _main_language = None
    
    actionsbook = None
    """Carnet d'actions, qui trace les actions à réaliser sur les widgets suite aux modifications des clés.
    
    """
    
    no_computation = False
    """Si True, `no_computation` empêche l'exécution immédiate de certaines opérations.
    
    Les opérations concernées sont les plus coûteuses en temps de calcul : le
    calcul des lignes et le calcul des langues disponibles dans les groupes de
    traduction. Il est préférable de réaliser ces opérations après avoir
    initialisé toutes les clés du groupe, plutôt qu'une fois pour chaque clé.
    
    """
    
    @classmethod
    def clear_actionsbook()
        """Remplace le carnet d'actions par un carnet vierge.
        
        """
        WidgetKey.actionsbook = ActionsBook()
    
    @property
    def main_language(self):
        """Langue principale de saisie des métadonnées.
        
        Cette propriété est commune à toutes les clés.
        
        Returns
        -------
        str
        
        """
        return WidgetKey._main_language
  
    @main_language.setter
    def main_language(self, value):
        """Définit la langue principale de saisie des métadonnées.
        
        Cette propriété est commune à toutes les clés.
        
        Parameters
        ----------
        value : str
            La langue.
        
        Raises
        ------
        ForbiddenOperation
            Si `value` n'est pas dans la liste des langues autorisées
            (`langlist`) - évidemment uniquement quand cette liste
            est déjà définie.
        
        """
        if value and self.langlist and not value in self.langlist:
            raise ForbiddenOperation(self, 'La langue principale devrait ' \
                'faire partie de la liste des langues autorisées.')
        if value and self.langlist:
            WidgetKey._langlist.sort(key= lambda x: (x != value, x))
            # langlist est trié de manière à ce que la langue principale
            # soit toujours le premier élément.
        WidgetKey._main_language = value

    @property
    def langlist(self):
        """Liste des langues autorisées.
        
        Cette propriété est commune à toutes les clés.
        
        Returns
        -------
        list of str
        
        """
        return WidgetKey._langlist
    
    @langlist.setter
    def langlist(self, value):
        """Définit la liste des langues autorisées.
        
        Cette propriété est commune à toutes les clés.
        
        Parameters
        ----------
        value : list of str
            La liste des langues.
        
        Raises
        ------
        ForbiddenOperation
            Si `langlist` ne contient pas la langue principale de saisie
            (`main_language`) - évidemment quand celle-ci est déjà définie.
        
        """
        WidgetKey._langlist = value
        self.main_language = self.main_language
        # assure la cohérence entre main_language et langlist
        # et effectue le tri de la liste.

    def __init__(self, **kwargs):     
        self.uuid = uuid4()
        self._row = None
        self._is_single_child = False
        self._is_hidden_m = False
        # la méthode __init__ de la classe ObjectKey se
        # charger d'exploiter le paramètre is_hidden_m qui
        # aurait pu être fourni.
        self._is_ghost = kwargs.get('is_ghost', False)
        self._parent = None
        self.parent = kwargs.get('parent')
        if WidgetKey.actionsbook:
            WidgetKey.actionsbook.create.append(self)

    def __str__(self):
        return "WidgetKey {}".format(self.uuid)
    
    @property
    def parent(self):
        """Clé parente.
        
        Returns
        -------
        GroupKey
        
        """
        return self._parent

    @parent.setter
    def parent(self, value):
        """Définit la clé parente.
        
        Parameters
        ----------
        value : GroupKey
            La clé parente.
        
        Raises
        ------
        MissingParameter
            Quand aucune clé n'est fournie pour le parent.
        ForbiddenOperation
            En cas de tentative de modification a posteriori du parent.
            Ceci est un pseudo-setter, qui n'est utilisé qu'à l'initialisation.
        ForbiddenOperation
            Si la classe de l'enfant n'est pas cohérente avec celle du parent.
        
        """
        if self.parent:
            raise ForbiddenOperation(self, 'Modifier a posteriori ' \
                "le parent d'une clé n'est pas permis.")
        if not value:
            raise MissingParameter('parent', self)
        if not self._validate_parent(value):
            raise ForbiddenOperation(self, 'La classe du parent ' \
                "n'est pas cohérente avec celle de la clé.")
        
        self._register(value)
        self._parent = value
        
        # héritage dans les branches fantômes
        # et masquées
        if value.is_ghost:
            self._is_ghost = True
        if value.is_hidden_m:
            self._is_hidden_m = True
 
    def _validate_parent(self, parent):
        return isinstance(self.parent, GroupKey)
        
    def _register(self, parent):
        parent.children.append(self)
    
    @property
    def is_ghost(self):
        """La clé est-elle une clé fantôme non matérialisée ?
        
        Returns
        -------
        bool
        
        Notes
        -----
        Cette propriété est en lecture seule, il n'est pas prévu
        à ce stade qu'elle puisse être modifiée après l'initialisation
        des clés.
        """
        return self._is_ghost
    
    @property
    def is_hidden_b(self):
        """La clé est-elle un bouton masqué ?
        
        Returns
        -------
        bool
        
        Notes
        -----
        Cette propriété est définie sur la classe `WidgetKey` pour
        simplifier les tests de visibilité, mais seul son alter ego
        de la classe `TranslationButtonKey` présente un intérêt.
        
        """
        return False
    
    @property
    def is_hidden_m(self):
        """La clé appartient-elle à une branche masquée ?
        
        Cette propriété vaut True pour la clé présentement masquée d'un
        couple de jumelles, ou toute clé descendant de celle-ci (branche
        masquée). Cet attribut est héréditaire.
        
        Returns
        -------
        bool
        
        Notes
        -----
        Cette propriété est en lecture seule pour la classe `WidgetKey`.
        Le setter est défini sur `ObjectKey`.
        
        """
        return self._is_hidden_m 

    def _hide_m(self, value):
        if self.is_ghost :
            return
        self._is_hidden_m = value
        if WidgetKey.actionsbook and not self.is_hidden_m:
            WidgetKey.actionsbook.show.append(self)
        elif WidgetKey.actionsbook:
            WidgetKey.actionsbook.hide.append(self)
        # pour les enfants et les boutons, cf. méthodes
        # de même nom des classes GroupKey et GroupOfValuesKey

    @property
    def rowspan(self):
        """Nombre de lignes de la grille occupées par la clé.
        
        Returns
        -------
        int
        
        Notes
        -----
        Cette propriété est définie sur la classe `WidgetKey` pour
        simplifier son utilisation, mais seul son alter ego
        de la classe `ValueKey` présente un intérêt.
        
        """
        return 0 if self.is_ghost else 1

    @property
    def row(self):
        """Ligne de la clé dans la grille.
        
        Returns
        -------
        int
        
        Notes
        -----
        Propriété calculée par `compute_rows`, accessible uniquement en
        lecture.
        
        """
        return None if self.is_ghost else self._row

    @property
    def is_single_child(self):
        """La clé est-elle un enfant unique ?
        
        Returns
        -------
        bool
        
        Notes
        -----
        Propriété calculée par `compute_single_children`, accessible
        uniquement en lecture.
        
        """
        return False is self.is_ghost else self._is_single_child

    def kill(self):
        """Efface une clé de la mémoire de son parent.
        
        Notes
        -----
        Cette méthode n'est pas appliquée récursivement aux enfants
        de la clé "tuée". Elle coupe simplement la branche.
        
        """
        self.parent.children.remove(self)
        if WidgetKey.actionsbook:
            WidgetKey.actionsbook.drop.append(self) 


class ObjectKey(WidgetKey):
    """Clé de dictionnaire de widgets représentant un couple prédicat/objet (au sens RDF).
    
    *Cette classe ne doit pas être utilisée directement, on préfèrera toujours
    `ValueKey` et `GroupOfPropertiesKey`, qui héritent de ses méthodes et
    attributs.*
    
    Outre ses propriétés propres listées ci-après, `ObjectKey` hérite des
    attributs et méthodes de la classe `WidgetKey`.
    
    Parameters
    ----------
    parent : GroupKey
        La clé parente. Ne peut pas être None.
    is_ghost : bool, default False
        True si la clé ne doit pas être matérialisée. À noter que quelle
        que soit la valeur fournie à l'initialisation, une fille de clé
        fantôme est toujours un fantôme.
    predicate : URIRef, optional
        Prédicat représenté par la clé. Si la clé appartient à un groupe
        de valeurs, c'est lui qui porte cette information. Sinon, elle
        est obligatoire.
    m_twin : ObjectKey, optional
        Clé jumelle. Un couple de jumelle ne se déclare qu'une fois, sur
        la seconde clé créée.
    is_hidden_m : bool, default False
        La clé est-elle la clé masquée du couple de jumelles ? Ce paramètre
        n'est pris en compte que pour une clé qui a une jumelle.        
    
    Attributes
    ----------
    predicate : URIRef
        *Propriété.* Prédicat représenté par la clé.
    m_twin : ObjectKey
        *Propriété.* Clé jumelle.
    
    """
    def __init__(self, **kwargs):
        if not isinstance(self, GroupOfPropertiesKey):
            # GroupOfPropertiesKey hérite à la fois de
            # la classe ObjectKey et de GroupKey, et
            # c'est GroupKey qui appelera la méthode
            # __init__ de WidgetKey.
            super().__init__(self, **kwargs)
        self._predicate = None
        self.predicate = kwargs.get('predicate')
        self._m_twin = None
        m_twin = kwargs.get('m_twin')
        if m_twin:
            self._is_hidden_m = self.is_hidden_m or \
                kwargs.get('is_hidden_m', False)
            self.m_twin = kwargs.get('m_twin')
    
    @property
    def predicate(self):
        """Prédicat représenté par la clé.
        
        Si la clé appartient à un groupe de valeurs ou de traduction,
        la méthode va chercher la propriété du groupe parent.
        
        Returns
        -------
        URIRef
        
        """
        if isinstance(self.parent, GroupOfValuesKey):
            return self.parent.predicate
        return self._predicate

    @predicate.setter
    def predicate(self, value):
        """Définit le prédicat représenté par la clé.
        
        Si la clé appartient à un groupe de valeurs ou de traduction,
        la méthode n'aura silencieusement aucun effet, car cette
        information est supposée être définie par la propriété de
        même nom du groupe.
        
        Parameters
        ----------
        value : URIRef
            Le prédicat à déclarer.
        
        Raises
        ------
        MissingParameter
            Si `value` vaut None, cette information étant obligatoire.
        
        """
        if not isinstance(self.parent, GroupOfValuesKey):
            if not value:
                raise MissingParameter('value', self)
            self._predicate = value

    @property
    def m_twin(self):
        """Clé jumelle.
        
        Deux clés jumelles sont une clé `ValueKey` et une clé
        `GroupOfPropertiesKey` représentant le même objet, la première
        sous forme d'IRI, la seconde sous la forme d'un ensemble de
        propriétés (définition "manuelle"). Les deux clés occupant le
        même emplacement dans la grille, l'une des deux doit toujours être
        masquée (`is_hidden_m` valant True).
        
        Returns
        -------
        ObjectKey
        
        """
        return self._m_twin
    
    @m_twin.setter
    def m_twin(self, value):
        """Définit la clé jumelle.
        
        Parameters
        ----------
        value : ObjectKey
            La clé jumelle.
        
        Raises
        ------
        ForbiddenOperation
            Si la clé jumelle n'est pas du bon type (`ValueKey` pour une
            clé `GroupOfPropertiesKey` et inversement), si les deux clés
            n'ont pas le même parent, si leur visibilité n'est pas correcte,
            si elle n'ont pas la même valeur d'attribut `rowspan`, si l'une
            d'elles est un fantôme.
        
        """
        if self.is_ghost :
            raise ForbiddenOperation(self, 'Un fantôme ne peut avoir ' \
                'de clé jumelle.')
        if value.is_ghost :
            raise ForbiddenOperation(self, 'La clé jumelle ne peut pas ' \
                'être un fantôme.')
        d = {ValueKey: GroupOfPropertiesKey, GroupOfPropertiesKey: ValueKey}
        if not isinstance(value, d[type(self)]):
            raise ForbiddenOperation(self, 'La clé jumelle devrait' \
                ' être de type {}'.format(d[type(self)]))
        if not self.parent == value.parent:
            raise ForbiddenOperation(self, 'La clé et sa jumelle ' \
                'devraient avoir la même clé parent.')
        if self.rowspan != value.rowspan:
            raise ForbiddenOperation(self, "L'attribut rowspan devrait" \
                ' être identique pour les deux clés jumelles.')
        
        self.is_hidden_m = self.is_hidden_m
        # assure que la visibilité de la jumelle est inversée
        # par rapport à celle de la clé
        
        self._m_twin = value
        value._m_twin = self
        # surtout pas value.m_twin, l'objectif n'est pas de créer une boucle
        # infinie.
    
    @property
    def is_hidden_m(self):
        """La clé appartient-elle à une branche masquée ?
        
        Cette propriété vaut True pour la clé présentement masquée d'un
        couple de jumelles, ou toute clé descendant de celle-ci (branche
        masquée). Cet attribut est héréditaire.
        
        Returns
        -------
        bool
        
        """
        return self._is_hidden_m 
    
    @is_hidden_m.setter
    def is_hidden_m(self, value):
        """Définit l'état de visibilité de la clé, de sa jumelle et de leurs descendantes.
        
        Toute tentative pour rendre visible une partie d'une branche restant
        masquée en amont sera silencieusement ignorée.
        
        Parameters
        ----------
        value : bool
            True si la clé est masquée, False sinon.
        
        """
        if self.parent.is_hidden_m or not self.m_twin:
            return
        self._hide_m(value)
        self.m_twin._hide_m(not value)

    def kill(self):
        """Efface une clé de la mémoire de son parent.
        
        Notes
        -----
        Cette méthode complète la méthode éponyme de la classe
        `WidgetKey` en effaçant aussi la clé jumelle, s'il y en
        a une.
        
        """
        super().kill()
        if self.m_twin:
            self.parent.children.remove(m_twin)
            if WidgetKey.actionsbook:
                WidgetKey.actionsbook.drop.append(m_twin)


class GroupKey(WidgetKey):
    """Clé de dictionnaire de widgets représentant un groupe.
    
    Une "clé de groupe" est une clé qui pourra être désignée comme parent
    d'autres clés, dites "clés filles".
    
    *Cette classe ne doit pas être utilisée directement, on préfèrera toujours
    ses classes filles, qui héritent de ses méthodes et attributs.*
    
    Outre ses attributs propres listés ci-après, `GroupKey` hérite de tous
    les attributs de la classe `WidgetKey`.
    
    Parameters
    ----------
    parent : GroupKey
        La clé parente. Ne peut pas être None, sauf dans le cas d'un objet
        de la classe `RootKey` (groupe racine).
    is_ghost : bool, default False
        True si la clé ne doit pas être matérialisée. À noter que quelle
        que soit la valeur fournie à l'initialisation, une fille de clé
        fantôme est toujours un fantôme.
    
    Attributes
    ----------
    children : list of WidgetKey
        Liste des clés filles.
    
    Methods
    -------
    real_children()
        Générateur sur les enfants de la clé qui ne sont ni des fantômes ni
        des boutons.
    
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.children = []
    
    def _hide_m(self, value):
        super()._hide_m(value)
        for child in self.real_children():
            child._hide_m(value)
    
    def real_children(self):
        """Générateur sur les clés filles qui ne sont pas des fantômes (ni des boutons).
        
        Yields
        ------
        ValueKey or GroupKey
        
        """
        for child in self.children:
            if not child.is_ghost:
                yield child
    
    def compute_single_children(self):
        return
   
    def compute_available_language(self, key_in=None, key_out=None):
        return
    
    def compute_rows(self):
        """Actualise les indices de ligne des filles du groupe.
        
        Cette méthode devrait être systématiquement appliquée à
        la clé parente après toute création ou effacement de clé.
        Elle n'a pas d'effet dans un groupe fantôme, ou si la
        variable partagée `no_computation` vaut True.
        
        Returns
        -------
        int
            L'indice de la prochaine ligne disponible.
        
        Notes
        -----
        `compute_rows` respecte l'ordre des clés filles dans la
        liste de l'attribut `children`.
        
        """
        if self.is_ghost or WidgetKey.no_computation:
            return
        n = 0
        for child in self.real_children():
            if isinstance(child, ValueKey) and child.m_twin:
                continue
                # traitée ensuite avec sa jumelle
            if child.row != n:
                child.row = n
                if WidgetKey.actionsbook:
                    WidgetKey.actionsbook.move.append(child)
            if isinstance(child, GroupOfPropertiesKey) \
                and child.m_twin and child.m_twin.row != n:
                child.m_twin.row = n
                if WidgetKey.actionsbook:
                    WidgetKey.actionsbook.move.append(child.m_twin)
            n += child.rowspan 
        return n


class TabKey(GroupKey):
    """Clé de dictionnaire de widgets représentant un onglet.
    
    Les onglets doublent leur groupe de propriétés parent sans porter
    aucune information sur la structure du graphe RDF.
    
    `TabKey` hérite des attributs et méthodes de la classe `GroupKey`.
    
    Parameters
    ----------
    parent : GroupKey
        La clé parente. Ne peut pas être None, sauf dans le cas d'un objet
        de la classe `RootKey` (groupe racine).
    is_ghost : bool, default False
        True si la clé ne doit pas être matérialisée. À noter que quelle
        que soit la valeur fournie à l'initialisation, une fille de clé
        fantôme est toujours un fantôme.
    
    """
    def object(self):
        """Renvoie une transcription littérale de la classe de la clé.
        
        """
        return 'tab'

    def _validate_parent(self, parent):
        return isinstance(self.parent, GroupOfPropertiesKey)


class GroupOfPropertiesKey(GroupKey, ObjectKey):
    """Clé de dictionnaire de widgets représentant un groupe de propriétés.
    
    Une "clé de groupe de propriétés" représente un couple prédicat / noeud
    vide, ce dernier étant à la fois un objet et un sujet. Ses filles
    représentent les différents prédicats qui décrivent à leur tour le sujet.
    
    Outre ses attributs propres listés ci-après, `GroupOfPropertiesKey`
    hérite de tous les attributs et méthodes des classes `GroupKey` et
    `ObjectKey`.
    
    Parameters
    ----------
    parent : GroupKey
        La clé parente. Ne peut pas être None, sauf dans le cas d'un objet
        de la classe `RootKey` (groupe racine).
    is_ghost : bool, default False
        True si la clé ne doit pas être matérialisée. À noter que quelle
        que soit la valeur fournie à l'initialisation, une fille de clé
        fantôme est toujours un fantôme.
    predicate : URIRef, optional
        Prédicat représenté par la clé. Si la clé appartient à un groupe
        de valeurs, c'est lui qui porte cette information. Sinon, elle
        est obligatoire.
    m_twin : ObjectKey, optional
        Clé jumelle. Un couple de jumelle ne se déclare qu'une fois, sur
        la seconde clé créée.
    is_hidden_m : bool, default False
        La clé est-elle la clé masquée du couple de jumelles ? Ce paramètre
        n'est pris en compte que pour une clé qui a une jumelle.
    node : BNode, optional
        Le noeud vide objet du prédicat, qui est également le sujet
        des triplets des enfants du groupe. Si non fourni, un nouveau
        noeud vide est généré.
    rdftype : URIRef, optional
        La classe RDF du noeud. Si la clé appartient à un groupe
        de valeurs, c'est lui qui porte cette information. Sinon, elle
        est obligatoire.
    
    Attributes
    ----------
    node : BNode
        Le noeud vide objet du prédicat, qui est également le sujet des
        triplets des enfants du groupe.
    rdftype : URIRef
        La classe RDF du noeud.
    
    """
    def __init__(self, **kwargs):
        GroupKey.__init__(**kwargs)
        ObjectKey.__init__(**kwargs)
        self._rdftype = None
        self.rdftype = kwargs.get('rdftype')
        node = kwargs.get('node')
        if node and isinstance(node, BNode):
            self.node = node
        else:
            self.node = BNode()
 
    def _validate_parent(self, parent):
        if isinstance(parent, GroupOfValuesKey) and not parent.rdftype:
            raise IntegrityBreach(self, "L'attribut `rdftype` de " \
                "la clé parente n'est pas renseigné.")
        return isinstance(self.parent, GroupKey) and \
            not isinstance(self.parent, TranslationGroupKey)
 
    @property
    def rdftype(self):
        """La classe RDF du noeud.
        
        Si la clé appartient à un groupe de valeurs ou de traduction,
        la méthode va chercher la propriété du groupe parent.
        
        Returns
        -------
        URIRef
        
        """
        if isinstance(self.parent, GroupOfValuesKey):
            return self.parent.rdftype
        return self._rdftype

    @rdftype.setter
    def rdftype(self, value):
        """Définit la classe RDF du noeud.
        
        Si la clé appartient à un groupe de valeurs ou de traduction,
        la méthode n'aura silencieusement aucun effet, car cette
        information est supposée être définie par la propriété de
        même nom du groupe.
        
        Parameters
        ----------
        value : URIRef
            La classe RDF à déclarer.
        
        Raises
        ------
        MissingParameter
            Si `value` vaut None, cette information étant obligatoire.
        
        """
        if not isinstance(self.parent, GroupOfValuesKey):
            if not value:
                raise MissingParameter('value', self)
            self._rdftype = value
 
    def object(self):
        """Renvoie une transcription littérale de la classe de la clé.
        
        """
        return 'group of properties'


class GroupOfValuesKey(GroupKey):
    """Clé de dictionnaire de widgets représentant un groupe de valeurs.
    
    Une "clé de groupe de valeurs" est une clé de groupe dont les filles,
    qui peuvent être des `GroupOfPropertiesKey` ou des `ValueKey`,
    représentent les différents objets d'un même couple sujet / prédicat.
    
    Outre les attributs spécifiques listés ci-après, `GroupOfValuesKey`
    hérite de tous les attributs de la classe `GroupKey`.
    
    Parameters
    ----------
    parent : GroupKey
        La clé parente. Ne peut pas être None.
    is_ghost : bool, default False
        True si la clé ne doit pas être matérialisée. À noter que quelle
        que soit la valeur fournie à l'initialisation, une fille de clé
        fantôme est toujours un fantôme.
    predicate : URIRef
        Le prédicat commun à toutes les valeurs du groupe.
    rdftype : URIRef, optional
        La classe RDF commune à toutes les valeurs du groupe. Peut
        valoir None si le groupe ne contient pas de `GroupOfPropertiesKey`.
    sources : list of URIRef, optional
        Liste des sources de vocabulaire contrôlé pour les valeurs
        du groupe.
    
    Attributes
    ----------
    button : PlusButtonKey
        Référence la clé qui représente le bouton du groupe.
    predicate : URIRef
        Prédicat commun à toutes les valeurs du groupe.
    rdftype : URIRef
        Classe RDF commune à toutes les valeurs du groupe. Peut
        valoir None si le groupe ne contient pas de `GroupOfPropertiesKey`.
    sources : list of URIRef
        Liste des sources de vocabulaire contrôlé pour les valeurs
        du groupe, s'il y a lieu.
    
    """
    def __init__(self, **kwargs):
        self.button = None
        self.predicate = kwargs.get('predicate')
        if not self.predicate:
            raise MissingParameter('predicate')
        self._rdftype = None
        self.rdftype = kwargs.get('rdftype')
        self._sources = None
        self.sources = kwargs.get('sources')
        super().__init__(**kwargs)
    
    @property
    def predicate(self):
        """Prédicat commun à toutes les valeurs du groupe.
        
        Returns
        -------
        URIRef
        
        """
        return self._predicate

    @predicate.setter
    def predicate(self, value):
        """Définit le prédicat commun à toutes les valeurs du groupe.
        
        Parameters
        ----------
        value : URIRef
            Le prédicat à déclarer.
        
        Raises
        ------
        MissingParameter
            Si `value` vaut None, cette information étant obligatoire.
        
        """
        if not value:
            raise MissingParameter('value', self)
        self._predicate = value
    
    @property
    def rdftype(self):
        """Classe RDF commune à toutes les valeurs du groupe.
        
        Returns
        -------
        URIRef
        
        """
        return self._rdftype
        
    @rdftype.setter
    def rdftype(self, value):
        """Définit la classe RDF commune à toutes les valeurs du groupe.
        
        Parameters
        ----------
        value : URIRef
            La classe à déclarer.
        
        Raises
        ------
        ForbiddenOperation
            En cas de tentative de mettre `value` à None alors qu'il y
            a au moins un groupe de propriétés (représentant un noeud
            vide, qui doit avoir une classe associée) parmi les enfants
            du groupe.
        
        """
        if not value and any(isinstance(child, GroupOfPropertiesKey) \
            for child in self.children):
            raise MissingParameter('rdftype', self)
        self._rdftype = value
    
    @property
    def sources(self):
        """Liste des sources de vocabulaire contrôlé commune à toutes les valeurs du groupe.
        
        Returns
        -------
        list of URIRef
        
        """
        return self._sources
        
    @sources.setter
    def sources(self, value):
        """Définit la liste des sources de vocabulaire contrôlé commune à toutes les valeurs du groupe.
        
        Parameters
        ----------
        value : list of URIRef
            La liste de sources à déclarer.
        
        Raises
        ------
        ForbiddenOperation
            En cas de tentative de modification a posteriori (après la
            déclaration du premier enfant).
        
        """
        if self.children:
            raise ForbiddenOperation(self, 'Modifier a posteriori ' \
                "la liste des sources n'est pas permis.")
        self._sources = value
    
    def _validate_parent(self, parent):
        return isinstance(self.parent, (GroupOfPropertiesKey, TabKey))
    
    def object(self):
        """Renvoie une transcription littérale de la classe de la clé.
        
        """
        return 'group of values'
    
    def _hide_m(self, value):
        super()._hide_m(value)
        if self.button:
            button._hide_m(value)

    def compute_rows(self):
        """Actualise les indices de ligne des filles du groupe.
        
        Cette méthode devrait être systématiquement appliquée à
        la clé parente après toute création ou effacement de clé.
        Elle n'a pas d'effet dans un groupe fantôme, ou si la
        variable partagée `no_computation` vaut True.
            
        Returns
        -------
        int
            L'indice de la prochaine ligne disponible.
        
        """
        if self.is_ghost or WidgetKey.no_computation:
            return
        n = super().compute_rows()
        if self.button and self.button.row != n:
            self.button.row = n
            if WidgetKey.actionsbook:
                WidgetKey.actionsbook.move.append(self.button)
        n += self.button.rowspan
        return n

    def compute_single_children(self):
        """Actualise l'attribut `is_single_child` des clés filles du groupe.
        
        Cette méthode devrait être systématiquement appliquée à
        la clé parente après toute création ou effacement de clé.
        Elle n'a pas d'effet dans un groupe fantôme, ou si la
        variable partagée `no_computation` vaut True.
        
        """
        if self.is_ghost or WidgetKey.no_computation :
            return
        true_children_count = sum([
            1 for c in self.real_children() if not c.m_twin or \
            not isinstance(c, GroupOfPropertiesKey)
            ])
            # ne compte pas les fantômes ni les boutons et les
            # couples de jumelles ne comptent que pour 1
        
        for child in self.real_children():
            # boutons moins à afficher
            if true_children_count >= 2 \
                and not child.is_single_child is False:
                child.is_single_child = False
                if WidgetKey.actionsbook:
                    WidgetKey.actionsbook.show_minus_button.append(child)
            # boutons moins à masquer
            if true_children_count < 2 \
                and not child.is_single_child:
                child.is_single_child = True
                if WidgetKey.actionsbook:
                    WidgetKey.actionsbook.hide_minus_button.append(child) 


class TranslationGroupKey(GroupOfValuesKey):
    """Clé de dictionnaire de widgets représentant un groupe de traduction.
    
    Une "clé de groupe de traduction" est une clé de groupe dont les filles
    représentent les traductions d'un objet. Chaque membre du groupe
    a donc un attribut `value_language` différent, et tout l'enjeu du
    groupe de traduction est d'y veiller.
    
    Outre ses attributs propres listés ci-après, `TranslationGroupKey`
    hérite de tous les attributs de la classe `GroupOfValuesKey`.
    
    Il n'est pas permis d'avoir un groupe de traduction fantôme, y compris
    par héritage (d'autant que de besoin, on utilisera des groupes de
    valeurs à la place).
    
    Parameters
    ----------
    parent : GroupKey
        La clé parente. Ne peut pas être None.
    is_ghost : bool, default False
        True si la clé ne doit pas être matérialisée. À noter que quelle
        que soit la valeur fournie à l'initialisation, une fille de clé
        fantôme est toujours un fantôme.
    predicate : URIRef
        Le prédicat commun à toutes les valeurs du groupe.
    
    Attributes
    ----------
    available_languages : list of str
        Liste des langues encore disponibles pour les traductions. Elle
        est initialisée avec la variable partagée `langlist`, et mise à 
        jour automatiquement au gré des ajouts et suppressions de traductions
        dans le groupe.
    
    Notes
    -----
    Dans un groupe de traduction, dont les enfants sont nécessairement des
    `ValueKey` représentant des valeurs littérales, il n'y a jamais lieu
    de fournir des valeurs pour les paramètres `rdftype` et `sources`
    de `GroupOfValuesKey`. Ils n'apparaissent donc pas dans la liste de
    paramètres ci-avant, et - si valeurs il y avait - elles seraient
    silencieusement effacées. Les propriétés éponymes renvoient
    toujours None.
    
    """
    def __init__(self, **kwargs):
        if kwargs.get('is_ghost'):
            raise ForbiddenOperation('Les groupes de traduction ne ' \
                'peuvent pas être des fantômes.')
        self.available_languages = WidgetKey.langlist
        super().__init__(**kwargs)

    @property
    def rdftype(self):
        return None
        
    @rdftype.setter
    def rdftype(self, value):
        self._rdftype = None
        
    @property
    def sources(self):
        return None
        
    @rdftype.setter
    def sources(self, value):
        self._sources = None

    def _validate_parent(self, parent):
        if parent.is_ghost:
            raise ForbiddenOperation('Les groupes de traduction ne sont ' \
                'pas autorisés dans les groupes fantômes.')
        return super()._validate_parent(parent)

    def object(self):
        """Renvoie une transcription littérale de la classe de la clé.
        
        """
        return 'translation group'

    def compute_available_language(self, key_in=None, key_out=None):
        """Met à jour la liste des langues disponibles dans le groupe de traduction.
        
        Cette méthode devrait être systématiquement appliquée à
        la clé parente après toute création ou effacement de clé.
        
        Parameters
        ----------
        key_in : WidgetKey, optional
            Clé venant d'être ajoutée au groupe.
        key_out : WidgetKey, optional
            Clé venant d'être supprimée du groupe.
        
        Notes
        -----
        `no_computation` n'influe pas sur l'exécution de cette
        méthode, car son résultat est nécessaire à des contrôles
        réalisés lors de toute création d'enfant dans le groupe.
        Elle ne peut donc être différée. Accessoirement, elle n'est
        pas redondante, il n'y aurait donc aucun bénéfice à attendre
        pour réaliser les calculs en une seule fois.
        
        """
        if not key_in and not key_out:
            return
        if key_in and isinstance(key_in, ValueKey):
            self.language_out(key_in.language_value)
        if key_out and isinstance(key_out, ValueKey):
            self.language_in(key_out.language_value)

    def language_in(self, value_language):
        """Ajoute une langue à la liste des langues disponibles.
        
        Parameters
        ----------
        value_language : str
            Langue redevenue disponible.
        
        Raises
        ------
        MissingParameter
            Si aucune langue n'est spécifiée.

        """        
        if not value_language:
            raise MissingParameter('value_language', self)
        
        if not value_language in WidgetKey.langlist \
            or value_language in self.available_languages:
            return
            # une langue qui n'était pas autorisée n'est
            # pas remise dans le pot. Idem pour une langue
            # qui y était déjà (cas de doubles traductions,
            # ce qui pourrait arriver dans des fiches importées).
        
        self.available_languages.append(value_language)
        
        if WidgetKey.actionsbook:
            for child in self.real_children():
                WidgetKey.actionsbook.languages.append(child)
        
        if self.button and len(self.available_languages) == 1:
            if WidgetKey.actionsbook:
                WidgetKey.actionsbook.show.append(self.button)

    def language_out(self, value_language):
        """Retire une langue de la liste des langues disponibles.
        
        Parameters
        ----------
        value_language : str
            Langue désormais non disponible.
            
        Raises
        ------
        MissingParameter
            Si aucune langue n'est spécifiée.
        
        """        
        if not value_language:
            raise MissingParameter('value_language', self)
        
        if not value_language in self.available_languages:
            return
            # on admet que la langue ait pu ne pas se trouver
            # dans la liste (métadonnées importées, etc.)
        
        self.available_languages.remove(value_language)
    
        if WidgetKey.actionsbook:
            for child in self.real_children():
                WidgetKey.actionsbook.languages.append(child)
        
        if not self.available_languages and self.button:
            if WidgetKey.actionsbook:
                WidgetKey.actionsbook.hide.append(self.button)


class ValueKey(ObjectKey):
    """Clé de dictionnaire de widgets représentant une valeur.
    
    Outre ses méthodes et attributs propres listés ci-après, `ValueKey`
    de toutes les méthodes et attributs de la classe `ObjectKey`.
    
    Parameters
    ----------
    parent : GroupKey
        La clé parente. Ne peut pas être None.
    is_ghost : bool, default False
        True si la clé ne doit pas être matérialisée. À noter que quelle
        que soit la valeur fournie à l'initialisation, une fille de clé
        fantôme est toujours un fantôme.
    predicate : URIRef, optional
        Prédicat représenté par la clé. Si la clé appartient à un groupe
        de valeurs, c'est lui qui porte cette information. Sinon, elle
        est obligatoire.
    m_twin : ObjectKey, optional
        Clé jumelle. Un couple de jumelle ne se déclare qu'une fois, sur
        la seconde clé créée.
    is_hidden_m : bool, default False
        La clé est-elle la clé masquée du couple de jumelles ? Ce paramètre
        n'est pris en compte que pour une clé qui a une jumelle.
    sources : list of URIRef, optional
        Liste des sources de vocabulaire contrôlé pour les valeurs
        de la clé. Si la clé appartient à un groupe de valeurs, c'est lui
        qui porte cette information. Sinon, elle est obligatoire.
    do_not_save : bool, default False
        True pour une information qui ne devra pas être sauvegardée.
    value : Literal or URIRef, optional
        La valeur mémorisée par la clé (objet du triplet RDF).
    value_type : URIRef, optional
        Le type (xsd:type) de l'objet du triplet. Si non renseigné
        et que `value_language` est fourni, il sera considéré que
        l'objet est de type rdf:langString, sinon il sera considéré que
        les valeurs sont des URIRef.
    value_transform : {None, 'email', 'phone'}, optional
        Le cas échéant, la nature de la transformation appliquée à
        l'objet.
    value_language : str, optional
        La langue de l'objet. Obligatoire pour un Literal de
        type rdf:langString et a fortiori dans un groupe de traduction,
        ignoré pour tous les autres types.
    value_source : URIRef
        La source utilisée par la valeur courante de la clé. Si la valeur
        fournie pour l'IRI ne fait pas partie des sources autorisées, elle
        sera silencieusement supprimée.
    
    Attributes
    ----------
    rowspan : int
        *Propriété.* Nombre de lignes occupées par le ou les widgets portés
        par la clé, étiquette séparée comprise. Vaut 0 pour une clé fantôme.
    available_languages : list or str
        *Propriété non modifiable.* Liste des langues disponibles pour
        les traductions.
    sources : list of URIRef
        Liste des sources de vocabulaire contrôlé pour les valeurs
        de la clé.
    value : Literal or URIRef
        La valeur mémorisée par la clé (objet du triplet RDF).
    value_type : URIRef
        Le type (xsd:type) de l'objet du triplet. None si l'objet n'est
        pas un Literal.
    value_language : str
        La langue de l'objet. None si l'objet n'est pas un Literal de
        type rdf:langString. Obligatoirement renseigné dans un groupe
        de traduction.
    value_transform : {None, 'email', 'phone'}
        Le cas échéant, la nature de la transformation appliquée à
        l'objet.
    value_source : URIRef
        La source utilisée par la valeur courante de la clé.
    do_not_save : bool
        True pour une information qui ne devra pas être sauvegardée.
    
    Methods
    -------
    parse_value(value)
        Prépare une valeur en vue de son enregistrement dans un graphe
        de métadonnées.
    
    Notes
    -----
    L'objet du triplet est porté par le dictionnaire interne
    associé à la clé et non par la clé elle-même.
    
    """
    def __init__(self, **kwargs):
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
        
        self._rowspan = None
        self.rowspan = kwargs.get('rowspan')
        self._sources = None
        self.sources = kwargs.get('sources')
        self._predicate = None
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
    
    @property
    def rowspan(self):
        """Nombre de lignes de la grille occupées par la clé.
        
        Returns
        -------
        int
        
        """
        return self._rowspan
    
    @rowspan.setter
    def rowspan(self, value):
        """Définit le nombre de lignes de la grille occupées par la clé.
        
        Parameters
        ----------
        value : int
            Le nombre de lignes.
        
        Raises
        ------
        MissingParameter
            Si aucune valeur n'est fournie ou si la valeur est 0.
        
        """
        if not value:
            raise MissingParameter('rowspan', self)
        if self.rowspan:
            self._rowspan = value
            self.parent.compute_rows()
        else:
            self._rowspan = value
            # pas de calcul des lignes à l'initialisation,
            # car ce sera fait juste après, lors de la déclaration
            # auprès du parent.
    
    @property
    def value(self):
        return self._value
        
    @value.setter
    def value(self, value):
        if self.is_ghost and not value:
            raise MissingParameter('value', self)
        self._value = value
    
    @property
    def value_language(self):
        """Renvoie la langue de la valeur portée par la clé.
        
        Tant qu'aucune langue n'a été explicitement définie, et s'il
        y a lieu de renvoyer une langue, c'est la langue principale
        de saisie des métadonnées qui est renvoyée.
        
        Returns
        -------
        str
        
        """
        if self._value_language:
            return self._value_language
        elif self.value_type == RDF.langString:
            return WidgetKey.main_language
    
    @value_language.setter
    def value_language(self, value):
        """Définit la langue de la valeur portée par la clé.
        
        Met à jour la propriété `value_language` et l'attribut
        `unauthorized_language`.
        
        Dans un groupe de traduction, si aucune valeur n'est
        fournie, la première langue de la liste des langues
        disponibles sera utilisée.
        
        Parameters
        ----------
        value : str
            La nouvelle langue à déclarer.
        
        """
        if not value and not self.value_type == RDF.langString:
            return
        elif value and not self.value_type:
            self.value_type == RDF.langString
        elif value and not self.value_type == RDF.langString:
            raise ForbiddenOperation(self, 'Pas de langue attendue ' \
                'pour cette clé.')
        
        if isinstance(self.parent, TranslationGroupKey):
            if not value:
                if self.available_languages:
                    value = self.available_languages[0]
                else:
                    raise IntegrityBreach(self, 'Plus de langue disponible.')
            if not self.unauthorized_language:
                self.parent.language_in(self.value_language)
            self.unauthorized_language = not self.parent.language_out(value)
        
        elif value:
            self.unauthorized_language = not value in self.available_languages
        self._value_language = value

    @property
    def value_type(self):
        """Renvoie le type de la valeur portée par la clé.
        
        Si la clé appartient à un groupe de valeurs ou de traduction,
        la méthode va chercher la propriété du groupe parent.
        
        Returns
        -------
        URIRef
        
        """
        if isinstance(self.parent, GroupOfValuesKey):
            return self.parent.value_type
        return self._value_type
    
    @value_type.setter
    def value_type(self, value):
        """Définit le type de la valeur portée par la clé.
        
        Si la clé appartient à un groupe de valeurs ou de traduction,
        la méthode n'aura silencieusement aucun effet, car cette
        information est supposée être définie par la propriété de
        même nom du groupe.
        
        Parameters
        ----------
        value : URIRef
            Le type à déclarer.
        
        """
        if not isinstance(self.parent, GroupOfValuesKey):
            if self.value_language:
                if value is None:
                    value = RDF.langString
                elif not value == RDF.langString:
                    raise ForbiddenOperation(self, 'Seul le type ' \
                        'rdf:langString est accepté lorsque ' \
                        '`value_language` est défini.')
            self._value_type = value
    
    @property
    def value_source(self):
        """Renvoie la source de la valeur portée par la clé.
        
        Returns
        -------
        URIRef
        
        """
        return self._value_source
    
    @value_source.setter
    def value_source(self, value):
        """Définit la source de la valeur portée par la clé.
        
        Parameters
        ----------
        value : URIRef
            L'IRI de la nouvelle source. Peut être None pour une
            valeur "non référencée".
        
        """
        if not self.sources :
            raise ForbiddenOperation(self, 'Pas de source attendue ' \
                'pour cette clé.')
        if value in self.sources:
            self._value_source = value
    
    @property
    def sources(self):
        """Renvoie la liste de sources de la clé.
        
        Si la clé appartient à un groupe de valeurs, la méthode
        renvoie la propriété de même nom du groupe parent.
        
        Returns
        -------
        list of URIRef
        
        """
        if isinstance(self.parent, GroupOfValuesKey):
            return self.parent.sources
        return self._sources
    
    @sources.setter
    def sources(self, value):
        """Définit la liste de sources de la clé.
        
        Si la clé appartient à un groupe de valeurs, la méthode
        n'aura silencieusement aucun effet, la liste étant
        définie sur le parent.
        
        Parameters
        ----------
        value : list of URIRef
            La liste de sources.
        
        """
        if not isinstance(self.parent, GroupOfValues):
            self._sources = value
            if self.value_source:
                self.value_source = self.value_source
                # pour le cas où value_source ne serait plus
                # une source autorisée.
    
    @property
    def available_languages(self):
        """Renvoie la liste des langues disponibles pour la clé.
        
        Si la clé appartient à un groupe de traduction, la méthode
        va chercher la liste définie sur la clé parente. Sinon elle
        renvoie la valeur de l'attribut `langlist` de la classe
        mère `WidgetKey`, ou None si le type de valeur ne suppose
        pas de langue.
        
        Returns
        -------
        list of str
        
        """
        if isinstance(self.parent, TranslationGroupKey):
            return self.parent.available_languages
        elif self.value_type == RDF.langString:
            self.langlist
    
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
            if WidgetKey.actionsbook:
                WidgetKey.actionsbook.sources.append(self)
                WidgetKey.actionsbook.thesaurus.append(self)
    
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
    
    Il n'est pas permis d'avoir des boutons fantômes, y compris
    par héritage.
    
    """
    def __init__(self, **kwargs):
        if kwargs.get('is_ghost'):
            raise ForbiddenOperation('Les boutons ne ' \
                'peuvent pas être des fantômes.')
        super().__init__(**kwargs)
        
    def object(self):
        """Renvoie une transcription littérale de la classe de la clé.
        
        """
        return 'plus button'
        
    def _validate_parent(self, parent):
        if parent.is_ghost:
            raise ForbiddenOperation('Les boutons plus ne sont pas autorisés ' \
                'dans les groupes fantômes.')
        return isinstance(parent, GroupOfValuesKey)
        
    def _register(self, parent):
        parent.button = self
    
    def kill(self):
        """Efface une clé bouton de la mémoire de son parent.
        
        Notes
        -----
        Cette méthode adapte la méthode éponyme de `WidgetKey`
        au cas des boutons. Dans l'absolu, elle n'est pas supposée
        servir, car aucun mécanisme ne prévoit de supprimer le
        bouton d'un groupe sans supprimer également celui-ci.
        
        """
        self.parent.button = None


class TranslationButtonKey(PlusButtonKey):
    """Clé de dictionnaire de widgets représentant un bouton de traduction.
    
    """
    @property
    def is_hidden_b(self):
        """La clé est-elle un bouton masqué ?
        
        Returns
        -------
        bool
        
        """
        return not parent.available_languages

    def _validate_parent(self, parent):
        return isinstance(self.parent, TranslationGroupKey)

    def object(self):
        """Renvoie une transcription littérale de la classe de la clé.
        
        """
        return 'translation button'


class RootKey(GroupKey):
    """Clé de dictionnaire de widgets représentant la racine du graphe RDF.
    
    Outre ses attributs propres listés ci-après, `RootKey` hérite
    des attributs de la classe `GroupKey`. Une clé racine n'a pas
    de parent. Elle porte l'identifiant du jeu de données, dans
    son attribut `node`.
    
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
        if WidgetKey.actionsbook:
            WidgetKey.actionsbook.create.append(self)
 
    @property
    def parent(self):
        return None
 
    def object(self):
        """Renvoie une transcription littérale de la classe de la clé.
        
        """
        return 'root'

    def kill(self):
        return

    def register_child(self, child_key, **kwargs):
        """Référence une fille dans les clés du groupe.
        
        Parameters
        ----------
        child_key : GroupKey or ValueKey
            La clé de la fille à déclarer.
        **kwargs : dict
            Autres paramètres, passés à la méthode `register_child`
            de la classe `GroupKey`.
        
        """
        if not isinstance(child_key, (GroupKey, ValueKey)):
            raise ForbiddenOperation(child_key, 'Ce type de clé ne ' \
                'peut pas être ajouté au groupe racine.')
        super().register_child(child_key, **kwargs)


class GhostValueKey(ValueKey):
    """Clé de dictionnaire de widgets représentant une valeur fantôme.
    
    Les clés fantômes ne donneront pas lieu à une représentation sous
    forme de widget.
    
    `GhostValueKey` hérite de tous les attributs et méthodes de la
    classe `ValueKey`, même si la plupart renvoient des résultats triviaux.
    Hormis `is_ghost`, qui vaut toujours True, tous les booléens vaudront
    systématiquement False. `row` vaut None, `rowspan` vaut 0. Toutes les
    autres propriétés à l'exception de `parent`, `predicate` et `value`
    valent None.
    
    Parameters
    ----------
    parent : GroupKey
        La clé parente. Ne peut pas être None.
    predicate : URIRef, optional
        Prédicat représenté par la clé. Si la clé appartient à un groupe
        de valeurs, c'est lui qui porte cette information. Sinon, elle
        est obligatoire.
    value : Literal or URIRef
        La valeur mémorisée par la clé (objet du triplet RDF). Sa
        présence est obligatoire pour une clé fantôme, qui sans ça
        n'a pas lieu d'être.
    
    Attributes
    ----------
    value : Literal or URIRef
        *Propriété.* La valeur mémorisée par la clé (objet du triplet RDF).
    is_ghost : bool
        *Propriété non modifiable.* La clé est-elle une clé fantôme ? Vaut
        toujours True.
    
    """
    
    def __init__(self, **kwargs):
        self._value = None
        self.value = kwarg.get('value')
        
    



class ChildrenList(list):
    """Liste des enfants d'une clé.
    
    Notes
    -----
    Cette classe redéfinit les méthodes `append` et `remove`
    des listes, pour que leur utilisation s'accompagne du calcul
    automatique des lignes, des enfants uniques et des langues
    autorisées.
    
    """
    def append(self, value):
        super().append(value)
        value.parent.compute_rows()
        value.parent.compute_single_children()
        value.parent.compute_available_language(key_in=value)
        
    def remove(self, value):
        super().append(value)
        value.parent.compute_rows()
        value.parent.compute_single_children()
        value.parent.compute_available_language(key_out=value)

    
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


