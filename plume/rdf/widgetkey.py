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
    
    Parameters
    ----------
    parent : GroupKey
        La clé parente. Ne peut pas être None, sauf dans le cas d'un objet
        de la classe descendante `RootKey`.
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
        
        """
        WidgetKey._langlist = value
        self.main_language = self.main_language
        # assure la cohérence entre main_language et langlist
        # et effectue le tri de la liste.

    def __init__(self, **kwargs):     
        self.uuid = uuid4()
        self._row = None
        self._is_hidden_m = False
        # la méthode __init__ de la classe ObjectKey se
        # charger d'exploiter le paramètre is_hidden_m qui
        # aurait pu être fourni.
        self._is_ghost = kwargs.get('is_ghost', False)
        self._parent = None
        self.parent = kwargs.get('parent')

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
        """
        if self.parent:
            raise ForbiddenOperation(self, 'Modifier a posteriori ' \
                "le parent d'une clé n'est pas permis.")
        if not value:
            raise MissingParameter('parent', self)
        
        value.register_child(self)
        self._parent = value
        
        # héritage dans les branches fantômes
        # et masquées
        if value.is_ghost:
            self._is_ghost = True
        if value.is_hidden_m:
            self._is_hidden_m = True
 
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
        de la classe `EditKey` présente un intérêt.
        
        """
        return 0 if self.is_ghost else 1

    def kill(self):
        """Efface une clé de la mémoire de son parent.
        
        Notes
        -----
        Le cas échéant, la clé jumelle sera également effacée,
        il n'y a donc pas lieu d'appeler deux fois cette méthode.
        
        Appliquer cette fonction sur une clé racine ne provoque
        pas d'erreur, elle n'aura simplement aucun effet.
        
        """
        self.parent.children.remove(self)
        
        if WidgetKey.actionsbook:
            WidgetKey.actionsbookdrop.append(self)
        
        if isinstance(self, (EditKey, GroupOfPropertiesKey)) \
            and self.m_twin:
            self.parent.children.remove(self.m_twin)

        self.parent.compute_rows()
        if isinstance(self.parent, GroupOfValuesKey):
            self.parent.compute_single_children()  


class ObjectKey(WidgetKey):
    """Clé de dictionnaire de widgets représentant un couple prédicat/objet (au sens RDF).
    
    Cette classe ne doit pas être utilisée directement, on préfèrera toujours
    `EditKey` et `GroupOfPropertiesKey`, qui héritent de ses méthodes et
    propriétés.
    
    Attributes
    ----------
    predicate
    m_twin
    
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
        """Définit le prédicate représenté par la clé.
        
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
        
        Deux clés jumelles sont une clé `EditKey` et une clé
        `GroupOfPropertiesKey` représentant le même objet, la première
        sous forme d'IRI, la seconde sous la forme d'un ensemble de
        propriétés (définition "manuelle"). Les deux clés occupant le
        même emplacement dans la grille, l'une des deux doit toujours être
        masquée (`is_hidden_m` valant True).
        
        Returns
        -------
        EditKey or GroupOfPropertiesKey
        
        """
        return self._m_twin
    
    @m_twin.setter
    def m_twin(self, value):
        """Définit la clé jumelle.
        
        Parameters
        ----------
        value : EditKey or GroupOfPropertiesKey
            La clé jumelle.
        
        Raises
        ------
        ForbiddenOperation
            Si la clé jumelle n'est pas du bon type (`EditKey` pour une
            clé `GroupOfPropertiesKey` et inversement), si les deux clés
            n'ont pas le même parent, si leur visibilité n'est pas correcte,
            si elle n'ont pas la même valeur d'attribut `rowspan`.
        
        """
        d = {EditKey: GroupOfPropertiesKey, GroupOfPropertiesKey: EditKey}
        if not isinstance(value, d[type(self)]):
            raise ForbiddenOperation(self, 'La clé jumelle devrait' \
                ' être de type {}'.format(d[type(self)]))
        if not self.parent == value.parent:
            raise ForbiddenOperation(self, 'La clé et sa jumelle ' \
                'devraient avoir la même clé parent.')
        if not self.parent.is_hidden_m \
            and self.is_hidden_m == value.is_hidden_m:
            raise ForbiddenOperation(self, 'Une et une seule des clés ' \
                'jumelles devrait être masquée.')
        if self.rowspan != value.rowspan:
            raise ForbiddenOperation(self, "L'attribut rowspan devrait" \
                ' être identique pour les deux clés jumelles.')
        
        self._m_twin = value
        value._m_twin = self
        # surtout pas value.m_twin, l'objectif n'est pas de créer une boucle
        # infinie.
    
    @is_hidden_m.setter
    def is_hidden_m(self, value):
        """Définit l'état de visibilité de la clé et ses descendantes.
        
        Parameters
        ----------
        value : bool
            True si la clé est masquée, False sinon.
        
        Raises
        ------
        ForbiddenOperation
            Lorsque l'opération aurait pour effet de rendre visible
            une partie d'une branche restant masquée en amont.
        
        """
        if value == self.is_hidden_m:
            return
        if not self.m_twin:
            raise ForbiddenOperation(self, "Cette clé n'a pas de jumelle.")
        if self.parent.is_hidden_m:
            raise ForbiddenOperation(self, 'La branche est masquée en amont.')
        self.m_twin._hide_m()
        self._hide_m()


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
    
    def _hide_m(self, value):
        super()._hide_m(value)
        for child in self.real_children():
            child._hide_m(value)
    
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
                if WidgetKey.actionsbook:
                    WidgetKey.actionsbookmove.append(child)
            if isinstance(child, GroupOfPropertiesKey) \
                and child.m_twin and child.m_twin.row != n:
                child.m_twin.row = n
                if WidgetKey.actionsbook:
                    WidgetKey.actionsbookmove.append(child.m_twin)
            
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
            WidgetKey.actionsbookcreate.append(self)
 
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
    
    def _hide_m(self, value):
        super()._hide_m(value)
        if self.button:
            button._hide_m(value)
    
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
            if WidgetKey.actionsbook:
                WidgetKey.actionsbookmove.append(self.button)
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
                if WidgetKey.actionsbook:
                    WidgetKey.actionsbookshow_minus_button.append(child)
            # boutons moins à masquer
            if true_children_count < 2 \
                and not child.is_single_child:
                child.is_single_child = True
                if WidgetKey.actionsbook:
                    WidgetKey.actionsbookhide_minus_button.append(child) 


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
        if WidgetKey.actionsbook:
            for child in self.real_children():
                WidgetKey.actionsbooklanguages.append(child)
        
        if self.button and len(self.available_languages) == 1:
            self.button.is_hidden_b = False
            if WidgetKey.actionsbook:
                WidgetKey.actionsbookshow.append(self.button)

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
    
        if WidgetKey.actionsbook:
            for child in self.real_children():
                WidgetKey.actionsbooklanguages.append(child)
        
        if not self.available_languages and self.button:
            self.button.is_hidden_b = True
            if WidgetKey.actionsbook:
                WidgetKey.actionsbookhide.append(self.button)
        
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
        
        self._rowspan = kwargs.get('rowspan')
        
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
        if isinstance(self.parent, GroupOfValuesKey):
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
                WidgetKey.actionsbooksources.append(self)
                WidgetKey.actionsbookthesaurus.append(self)
    
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
    @property
    def is_hidden_b(self):
        """La clé est-elle un bouton masqué ?
        
        Returns
        -------
        bool
        
        """
        return not self.parent.available_languages

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


