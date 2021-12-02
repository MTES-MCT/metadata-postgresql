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
    from rdflib import URIRef, BNode, Literal, RDF
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
        *Attribut de classe.* Le carnet d'actions trace les actions à
        réaliser sur les widgets au fil des modifications des clés. Pour
        le réinitialiser, on utilisera la méthode de classe `clear_actionsbook`.
    no_computation : bool
        *Attribut de classe.* Si True, inhibe temporairement la réalisation de
        certains calculs.
    main_language : str
        *Propriété de classe.* Langue principale de saisie des métadonnées.
    langlist : str
        *Propriété de classe.* Liste des langues autorisées.
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
    is_single_child : bool
        *Propriété non modifiable manuellement*. True si le parent est un
        groupe de valeurs et il n'y a qu'une seule valeur dans le groupe.
    row : int
        *Propriété non modifiable manuellement.* L'indice de la ligne de la
        grille occupée par le widget porté par la clé. Vaut None pour une clé
        fantôme.
    rowspan : int
        *Propriété non modifiable manuellement.* Nombre de lignes occupées
        par le ou les widgets portés par la clé, étiquette séparée comprise.
        Vaut 0 pour une clé fantôme.
    
    Methods
    -------
    clear_actionsbook()
        *Méthode de classe.* Remplace le carnet d'actions par un carnet vierge.
    unload_actionsbook()
        *Méthode de classe.* Renvoie le carnet d'actions et le remplace par
        un carnet vierge.
    kill()
        Efface la clé de la mémoire de son parent.
    
    """
    
    _langlist = None
    _main_language = None
    
    actionsbook = ActionsBook()
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
    def clear_actionsbook(cls):
        """Remplace le carnet d'actions par un carnet vierge.
        
        """
        cls.actionsbook = ActionsBook()
    
    @classmethod
    def unload_actionsbook(cls):
        """Renvoie le carnet d'actions et le remplace par un carnet vierge.
        
        Returns
        -------
        ActionsBook
        
        """
        book = cls.actionsbook
        cls.clear_actionsbook()
        return book
    
    @property
    def main_language(self):
        """Langue principale de saisie des métadonnées.
        
        Cette propriété est commune à toutes les clés.
        
        Returns
        -------
        str
        
        Raises
        ------
        MissingParameter
            Si la valeur de `main_language` n'est pas définie.
        
        """
        if WidgetKey._main_language is None:
            raise MissingParameter('main_language')
        return WidgetKey._main_language
  
    @main_language.setter
    def main_language(self, value):
        """Définit la langue principale de saisie des métadonnées.
        
        Cette propriété est commune à toutes les clés.
        
        Si la langue n'était pas incluse dans la liste des langues
        autorisées, elle est silencieusement ajoutée.
        
        Parameters
        ----------
        value : str
            La langue.
        
        Example
        -------
        >>> WidgetKey.main_language = 'fr'
        
        """
        if value and WidgetKey._langlist and not value in WidgetKey._langlist:
            WidgetKey._langlist.append(value)
        if value and WidgetKey._langlist:
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
        
        Raises
        ------
        MissingParameter
            Si la valeur de `langlist` n'est pas définie.
        
        """
        if WidgetKey._langlist is None:
            raise MissingParameter('langlist')
        return WidgetKey._langlist
    
    @langlist.setter
    def langlist(self, value):
        """Définit la liste des langues autorisées.
        
        Cette propriété est commune à toutes les clés.
        
        Si la liste ne contient pas la langue principale de saisie,
        celle-ci sera silencieusement ajoutée.
        
        Parameters
        ----------
        value : list of str
            La liste des langues.
        
        """
        WidgetKey._langlist = value
        if WidgetKey._main_language:
            WidgetKey.main_language = self.main_language
            # assure la cohérence entre main_language et langlist
            # et effectue le tri de la liste.

    def __init__(self, **kwargs):
        self._is_unborn = True
        self.uuid = uuid4()
        self._row = None
        self._is_single_child = False
        self._is_ghost = kwargs.get('is_ghost', False)
        self._parent = None
        self._is_hidden_m = False
        self._base_attributes(**kwargs)
        self._heritage(**kwargs)
        self._computed_attributes(**kwargs)
        self._is_unborn = False
        if WidgetKey.actionsbook:
            WidgetKey.actionsbook.create.append(self)

    def _base_attributes(self, **kwargs):
        return
    
    def _heritage(self, **kwargs):
        self.parent = kwargs.get('parent')
    
    def _computed_attributes(self, **kwargs):
        return
    
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
        # héritage dans les branches fantômes et masquées
        if value.is_ghost:
            self._is_ghost = True
        if value.is_hidden_m:
            self._is_hidden_m = True
        self._register(value)
        self._parent = value
 
    def _validate_parent(self, parent):
        return isinstance(parent, GroupKey)
        
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
        old_value = self.is_hidden_m
        self._is_hidden_m = value
        if WidgetKey.actionsbook and self.is_hidden_m \
            and not old_value:
            WidgetKey.actionsbook.show.append(self)
        elif WidgetKey.actionsbook and not self.is_hidden_m \
            and old_value:
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
        return False if self.is_ghost else self._is_single_child

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
        est obligatoire. À noter que si une jumelle est déclarée et que
        le prédicat n'est pas renseigné ou pas cohérent avec celui du
        jumeau, c'est celui du jumeau qui sera utilisé.
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
    def _base_attributes(self, **kwargs):
        self._predicate = None
        self._m_twin = None
    
    def _computed_attributes(self, **kwargs):
        self.m_twin = kwargs.get('m_twin')
        self.predicate = kwargs.get('predicate')
        self.is_hidden_m = kwargs.get('is_hidden_m', False)
    
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
        
        Si la clé a une jumelle dont le prédicat est différent
        de la valeur fournie, c'est ce prédicat qui sera utilisé.
        
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
            if self.m_twin and value != self.m_twin.predicate:
                value = self.m_twin.predicate
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
        if not value:
            return
        if self.is_ghost :
            raise ForbiddenOperation(self, 'Un fantôme ne peut avoir ' \
                'de clé jumelle.')
        if value.is_ghost :
            raise ForbiddenOperation(self, 'La clé jumelle ne peut pas ' \
                'être un fantôme.')
        d = {ValueKey: GroupOfPropertiesKey, GroupOfPropertiesKey: ValueKey}
        if not isinstance(value, d[type(self)]):
            raise ForbiddenOperation(self, 'La clé jumelle devrait' \
                ' être de type {}.'.format(d[type(self)]))
        if not self.parent == value.parent:
            raise ForbiddenOperation(self, 'La clé et sa jumelle ' \
                'devraient avoir la même clé parent.')
        self._m_twin = value
        value._m_twin = self
        if not self._is_unborn:
            # pour une clé dont le jumeau est défini a posteriori,
            # il faut s'assurer de la cohérence des prédicats et
            # et des nombres de lignes, et du fait
            # que la visibilité de la jumelle est inversée
            # par rapport à celle de la clé
            self.rowspan = self.rowspan
            self.predicate = self.predicate
            self.is_hidden_m = self.is_hidden_m
    
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
            # pas besoin de retoucher à la valeur
            # définie à l'initialisation ou héritée
            # du parent
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
    def _base_attributes(self, **kwargs):
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
                child._row = n
                if WidgetKey.actionsbook:
                    WidgetKey.actionsbook.move.append(child)
            if isinstance(child, GroupOfPropertiesKey) \
                and child.m_twin and child.m_twin.row != n:
                child.m_twin._row = n
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
        return isinstance(parent, GroupOfPropertiesKey)


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
    
    def _base_attributes(self, **kwargs):
        GroupKey._base_attributes(self, **kwargs)
        ObjectKey._base_attributes(self, **kwargs)
        self._rdftype = None
        node = kwargs.get('node')
        if node and isinstance(node, BNode):
            self.node = node
        else:
            self.node = BNode()
    
    def _computed_attributes(self, **kwargs):
        ObjectKey._computed_attributes(self, **kwargs)
        self.rdftype = kwargs.get('rdftype')
 
    def _validate_parent(self, parent):
        if isinstance(parent, GroupOfValuesKey) and not parent.rdftype:
            raise IntegrityBreach(self, "L'attribut `rdftype` de " \
                "la clé parente n'est pas renseigné.")
        return isinstance(parent, GroupKey) and \
            not isinstance(parent, TranslationGroupKey)
 
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
                raise MissingParameter('rdftype', self)
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
    transform : {None, 'email', 'phone'}, optional
        Le cas échéant, la nature de la transformation appliquée aux
        objets du groupe.
    xsdtype : URIRef, optional
        Le cas échéant, le type (xsd:type) des valeurs du groupe.
    
    Attributes
    ----------
    button : PlusButtonKey
        Référence la clé qui représente le bouton du groupe.
    predicate : URIRef
        *Propriété.* Prédicat commun à toutes les valeurs du groupe.
    rdftype : URIRef
        *Propriété.* Classe RDF commune à toutes les valeurs du groupe. Peut
        valoir None si le groupe ne contient pas de `GroupOfPropertiesKey`.
    sources : list of URIRef
        *Propriété non modifiable après l'initialisation.* Liste des sources
        de vocabulaire contrôlé pour les valeurs du groupe, s'il y a lieu.
    transform : {None, 'email', 'phone'}, optional
        *Propriété.* Le cas échéant, la nature de la transformation appliquée
        aux objets du groupe.
    xsdtype : URIRef, optional
        *Propriété non modifiable après l'initialisation.* Le cas échéant,
        le type (xsd:type) des valeurs du groupe.
    
    """
    def _base_attributes(self, **kwargs):
        super()._base_attributes(**kwargs)
        self.button = None
        self._predicate = None
        self._rdftype = None
        self._sources = None
        self._xsdtype = None
        self._transform = None
        
    def _computed_attributes(self, **kwargs):
        super()._computed_attributes(**kwargs)
        self.predicate = kwargs.get('predicate')
        self.rdftype = kwargs.get('rdftype')
        self.sources = kwargs.get('sources')
        self.xsdtype = kwargs.get('xsdtype')
        self.transform = kwargs.get('transform')
    
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
    
    @property
    def xsdtype(self):
        """Type XSD commun aux valeurs du groupe, le cas échéant.
        
        Returns
        -------
        URIRef
        
        """
        return self._xsdtype
    
    @xsdtype.setter
    def xsdtype(self, value):
        """Définit le type XSD commun aux valeurs du groupe.
        
        Parameters
        ----------
        value : URIRef
            Le type à déclarer.
        
        Raises
        ------
        ForbiddenOperation
            En cas de tentative de modification a posteriori.
        
        """
        if self.xsdtype :
            raise ForbiddenOperation(self, 'Modifier a posteriori le ' \
                "type XSD n'est pas permis.")
        self._xsdtype = value
    
    @property
    def transform(self):
        """Nature de la transformation appliquée aux valeurs du groupe.
        
        Returns
        -------
        {None, 'email', 'phone'}
        
        """
        return self._transform
    
    @transform.setter
    def transform(self, value):
        """Définit la nature de la transformation appliquée aux valeurs du groupe.

        Toute valeur qui ne serait pas dans la liste ci-après serait ignorée.

        Parameters
        ----------
        value : {None, 'email', 'phone'}
            La transformation.
        
        """
        if not value in (None, 'email', 'phone'):
            return
        self._transform = value
    
    def _validate_parent(self, parent):
        return isinstance(parent, (GroupOfPropertiesKey, TabKey))
    
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
        if self.button:
            if self.button.row != n:
                self.button._row = n
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
    def _base_attributes(self, **kwargs):
        super()._base_attributes(**kwargs)
        if kwargs.get('is_ghost'):
            raise ForbiddenOperation('Les groupes de traduction ne ' \
                'peuvent pas être des fantômes.')
        self.available_languages = self.langlist.copy()

    @property
    def rdftype(self):
        return None
        
    @rdftype.setter
    def rdftype(self, value):
        self._rdftype = None
        
    @property
    def sources(self):
        return None
        
    @sources.setter
    def sources(self, value):
        self._sources = None

    @property
    def transform(self):
        return None
        
    @transform.setter
    def transform(self, value):
        self._transform = None

    @property
    def xsdtype(self):
        """Type XSD commun à toutes les valeurs du groupe.
        
        Toujours rdf:langString.
        
        Returns
        -------
        URIRef
        
        """
        return self._xsdtype
        
    @xsdtype.setter
    def xsdtype(self, value):
        """Définit le type XSD des valeurs du groupe.
        
        Ceci est un pseudo-setter qui bloque la valeur sur rdf:langString.
        
        Parameters
        ----------
        value : URIRef
            La classe à déclarer.
        
        """
        self._xsdtype = RDF.langString

    def _validate_parent(self, parent):
        if parent.is_ghost:
            raise ForbiddenOperation('Les groupes de traduction ne sont ' \
                'pas autorisés dans les groupes fantômes.')
        return super()._validate_parent(parent)

    def object(self):
        """Renvoie une transcription littérale de la classe de la clé.
        
        """
        return 'translation group'

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
        
        if not value_language in self.langlist \
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
    rowspan : int, optional
        Nombre de lignes occupées par le ou les widgets portés par la clé,
        étiquette séparée comprise. À noter que si une jumelle est déclarée
        et que `rowspan` n'est pas renseigné ou pas cohérent avec celui du
        jumeau, c'est celui du jumeau qui sera utilisé. `rowspan` vaudra
        toujours 0 pour une clé fantôme. Si aucune valeur n'est fournie,
        une valeur par défaut de 1 est appliquée.
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
    transform : {None, 'email', 'phone'}, optional
        Le cas échéant, la nature de la transformation appliquée à
        l'objet. Si la clé appartient à un groupe de valeurs, c'est lui
        qui porte cette information, le cas échéant.
    xsdtype : URIRef, optional
        Le type (xsd:type) de l'objet du triplet. Doit impérativement
        valoir rdf:langString pour que les informations sur les
        langues soient prises en compte. Si la clé appartient à un groupe de
        valeurs, c'est lui qui porte cette information, le cas échéant.
    do_not_save : bool, default False
        True pour une information qui ne devra pas être sauvegardée.
    value : Literal or URIRef, optional
        La valeur mémorisée par la clé (objet du triplet RDF).
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
    xsdtype : URIRef
        Le type (xsd:type) de l'objet du triplet. None si l'objet n'est
        pas un Literal.
    transform : {None, 'email', 'phone'}
        Le cas échéant, la nature de la transformation appliquée à
        l'objet.
    value_language : str
        La langue de l'objet. None si l'objet n'est pas un Literal de
        type rdf:langString. Obligatoirement renseigné dans un groupe
        de traduction.
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
    
    def _base_attributes(self, **kwargs):
        super()._base_attributes(**kwargs)
        self.do_not_save = kwargs.get('do_not_save', False)
        self._rowspan = 0
        self._sources = None
        self._xsdtype = None
        self._transform = None
        self._value = None
        self._value_language = None
        self._value_source = None
    
    def _computed_attributes(self, **kwargs):
        super()._computed_attributes(**kwargs)
        self.rowspan = kwargs.get('rowspan')
        self.sources = kwargs.get('sources')
        self.xsdtype = kwargs.get('xsdtype')
        self.transform = kwargs.get('transform')
        self.value = kwargs.get('value')
        self.value_language = kwargs.get('value_language')
        self.value_source = kwargs.get('value_source')

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
        
        Si la clé a une jumelle dont le nombre de lignes est différent
        de la valeur fournie, c'est celui de la jumelle qui sera utilisé.
        
        `rowspan` vaudra toujours 0 pour une clé fantôme. Si aucune
        valeur n'est fournie, une valeur par défaut de 1 est appliquée.
        
        Parameters
        ----------
        value : int
            Le nombre de lignes.
        
        """
        if self.m_twin and value != self.m_twin.rowspan:
            value = self.m_twin.rowspan
        if self.is_ghost:
            value = 0
        elif not value:
            value = 1
        self._rowspan = value
        self.parent.compute_rows()
    
    @property
    def value(self):
        """Valeur portée par la clé (objet du triplet RDF).
        
        Returns
        -------
        URIRef or Literal
        
        """
        return self._value
        
    @value.setter
    def value(self, value):
        """Définit la valeur portée par la clé (objet du triplet RDF).
        
        Si la valeur fournie n'est pas un IRI ou un litéral RDF,
        elle est convertie grâce à `parse_value` (sous réserve que
        la valeur soit fournie après l'initialisation de la clé,
        sinon elle sera juste ignorée).
        
        Parameters
        ----------
        value : URIRef or Literal
            La valeur.
        
        Raises
        ------
        MissingParameter
            Si aucune valeur n'est fournie pour un clé fantôme (qui ne
            sert à rien d'autre qu'à mémoriser une valeur).
        
        """
        if self.is_ghost and not value:
            raise MissingParameter('value', self)
        if not isinstance(value, (URIRef, Literal)):
            if self._is_unborn:
                return
            self._value = self.parse_value(value)
        self._value = value
    
    @property
    def value_language(self):
        """Langue de la valeur portée par la clé.
        
        Tant qu'aucune langue n'a été explicitement définie, et s'il
        y a lieu de renvoyer une langue, c'est la langue principale
        de saisie des métadonnées qui est renvoyée.
        
        Returns
        -------
        str
        
        """
        if self._value_language:
            return self._value_language
        elif self.xsdtype == RDF.langString:
            return self.main_language
    
    @value_language.setter
    def value_language(self, value):
        """Définit la langue de la valeur portée par la clé.
        
        Si le type XSD n'est pas xsd:langString, ce setter
        n'a aucun effet.
        
        Si aucune langue n'est fournie, le setter tente de
        la déduire de `value`. À défaut, dans un groupe de
        traduction, la première langue de la liste des langues
        disponibles sera utilisée.
        
        Parameters
        ----------
        value : str
            La nouvelle langue à déclarer.
        
        """
        if self.xsdtype != RDF.langString:
            return
        if not value and isinstance(self.value, Literal):
            value = self.value.language
        if isinstance(self.parent, TranslationGroupKey):
            if not value:
                if self.available_languages:
                    value = self.available_languages[0]
                else:
                    raise IntegrityBreach(self, 'Plus de langue disponible.')
            self.parent.language_in(self.value_language)
            self.parent.language_out(value)
        self._value_language = value

    @property
    def xsdtype(self):
        """Renvoie le type de la valeur portée par la clé.
        
        Si la clé appartient à un groupe de valeurs ou de traduction,
        la méthode va chercher la propriété du groupe parent.
        
        Returns
        -------
        URIRef
        
        """
        if isinstance(self.parent, GroupOfValuesKey):
            return self.parent.xsdtype
        return self._xsdtype
    
    @xsdtype.setter
    def xsdtype(self, value):
        """Définit le type de la valeur portée par la clé.
        
        Si la clé appartient à un groupe de valeurs ou de traduction,
        la méthode n'aura silencieusement aucun effet, car cette
        information est supposée être définie par la propriété de
        même nom du groupe.
        
        `xsdtype` prévaut sur `value_language` : si `value_language`
        contient une langue mais que `xsdtype` n'est pas rdf:langString,
        la langue sera silencieusement effacée.
        
        Parameters
        ----------
        value : URIRef
            Le type à déclarer.
        
        Raises
        ------
        ForbiddenOperation
            En cas de tentative de modification a posteriori.
        
        """
        if not isinstance(self.parent, GroupOfValuesKey):
            if self.xsdtype :
                raise ForbiddenOperation(self, 'Modifier a posteriori le ' \
                    "type XSD n'est pas permis.")
            if self.value_language and value != RDF.langString:
                self.value_language = None
            self._xsdtype = value
    
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
            return
        old_value = self.value_source
        if value in self.sources:
            self._value_source = value
        else:
            self._value_source = None
        if WidgetKey.actionsbook and self.value_source != old_value:
            WidgetKey.actionsbook.sources.append(self)
            WidgetKey.actionsbook.thesaurus.append(self)
    
    @property
    def transform(self):
        """Nature de la transformation appliquée à l'objet.
        
        Si la clé appartient à un groupe de valeurs, la méthode
        renvoie la propriété de même nom du groupe parent.
        
        Returns
        -------
        {None, 'email', 'phone'}
        
        """
        if isinstance(self.parent, GroupOfValuesKey):
            return self.parent.transform
        return self._transform
    
    @transform.setter
    def transform(self, value):
        """Définit la nature de la transformation appliquée à l'objet.
        
        Si la clé appartient à un groupe de valeurs, la méthode
        n'aura silencieusement aucun effet, la liste étant
        définie sur le parent.
        
        Toute valeur qui ne serait pas dans la liste ci-après serait ignorée.
        
        Parameters
        ----------
        value : {None, 'email', 'phone'}
            La transformation.
        
        """
        if not isinstance(self.parent, GroupOfValuesKey):
            if not value in (None, 'email', 'phone'):
                return
            self._transform = value   
    
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
        if not isinstance(self.parent, GroupOfValuesKey) \
            and self.sources != value:
            self._sources = value
            if WidgetKey.actionsbook:
                WidgetKey.actionsbook.sources.append(self)
            if self.value_source:
                # pour le cas où value_source ne serait plus
                # une source autorisée.
                self.value_source = self.value_source
    
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
        elif self.xsdtype == RDF.langString:
            self.langlist

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
        if self.xsdtype:
            return Literal(value, datatype=self.xsdtype)
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
        
    def _validate_parent(self, parent):
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
        return isinstance(parent, TranslationGroupKey)

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
    
    Parameters
    ----------
    datasetid : URIRef, optional
        L'identifiant du graphe de métadonnées.
    
    Attributes
    ----------
    node : URIRef
        L'identifiant du jeu de données, qui sera le sujet des
        triplets des enfants du groupe.
    rdftype : URIRef
        La classe de l'objet RDF décrit par le groupe racine.
        Vaut toujours URIRef("http://www.w3.org/ns/dcat#Dataset").
    
    """
    def _heritage(self, **kwargs):
        return
    
    def _computed_attributes(self, **kwargs):
        return
    
    def _base_attributes(self, **kwargs):
        datasetid = kwargs.get('datasetid')
        if not isinstance(datasetid, URIRef):
            datasetid = URIRef(uuid4().urn)
        self.node = datasetid
        self._rdftype = URIRef("http://www.w3.org/ns/dcat#Dataset")
        self._is_ghost = False
        self._is_hidden_m = False
        self._is_hidden_b = False
        self._rowspan = 0
        self._row = None
        self.children = []
 
    @property
    def parent(self):
        return None
 
    @property
    def rdftype(self):
        """Classe RDF.
        
        Returns
        -------
        URIRef
        
        """
        return self._rdftype
        
    @rdftype.setter
    def rdftype(self, value):
        return
 
    def object(self):
        """Renvoie une transcription littérale de la classe de la clé.
        
        """
        return 'root'

    def kill(self):
        return


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
        if value.rowspan:
            value.parent.compute_rows()
        value.parent.compute_single_children()
        
    def remove(self, value):
        super().append(value)
        if value.rowspan:
            value.parent.compute_rows()
        value.parent.compute_single_children()

    
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


