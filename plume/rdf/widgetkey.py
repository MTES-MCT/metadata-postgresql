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

try:
    from rdflib import URIRef, BNode, Literal
except:
    from plume.bibli_install.bibli_install import manageLibrary
    # installe RDFLib si n'est pas déjà disponible
    manageLibrary()
    from rdflib import URIRef, BNode, Literal
from rdflib.namespace import RDF, XSD

from plume.rdf.exceptions import IntegrityBreach, MissingParameter, ForbiddenOperation, \
    UnknownParameterValue
from plume.rdf.actionsbook import ActionsBook



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
    order_idx : tuple of int, default (999,)
        Indice(s) permettant le classement de la clé parmi ses soeurs dans
        un groupe de propriétés. Les clés de plus petits indices seront les
        premières. Cet argument sera ignoré si le groupe parent n'est pas
        un groupe de propriétés.
    
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
        *Propriété de classe.* Liste des langues autorisées. Par défaut, cette
        propriété vaut ['fr', 'en'], mais elle est supposée être actualisée
        avant toute génération d'arbre de clés (et il n'est pas conseillé de
        de la modifier tant qu'on ne change pas d'arbre).
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
    has_minus_button : bool
        *Propriété.* True si un bouton moins est associé à la clé
        (potentiellement masqué, selon `is_single_child`).
    independant_label : bool
        *Propriété.* True si l'étiquette de la clé occupe sa propre ligne de la
        grille.
    row : int
        *Propriété non modifiable manuellement.* L'indice de la ligne de la
        grille occupée par le widget porté par la clé. Vaut None pour une clé
        fantôme.
    rowspan : int
        *Propriété non modifiable manuellement.* Nombre de lignes occupées
        par le ou les widgets portés par la clé, étiquette séparée non comprise.
        Vaut 0 pour une clé fantôme.
    order_idx : tuple of int
        *Propriété.* Indice(s) permettant le classement de la clé parmi ses
        soeurs. Les clés de plus petits indices seront les premières.
    path : str
        *Propriété non modifiable manuellement.* Chemin SPARQL de la clé.
    
    Methods
    -------
    clear_actionsbook()
        *Méthode de classe.* Remplace le carnet d'actions par un carnet vierge.
    unload_actionsbook()
        *Méthode de classe.* Renvoie le carnet d'actions et le remplace par
        un carnet vierge.
    kill()
        Efface la clé de la mémoire de son parent.
    copy(parent, empty)
        Copie une clé et, le cas échéant, la branche qui en descend.
    
    """
    
    _langlist = ['fr', 'en']
    
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
        
        Cette propriété est commune à toutes les clés. Concrètement,
        main_language est simplement la première valeur de `langlist`.
        
        Returns
        -------
        str
        
        """
        return WidgetKey._langlist[0]
  
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
        
        Notes
        -----
        `main_language` n'étant jamais que la première valeur de `langlist`,
        le principal effet de cette fonction est d'ajouter la langue à la
        liste si besoin et de retrier la liste.
        """
        if value and WidgetKey._langlist and not value in WidgetKey._langlist:
            WidgetKey._langlist.append(value)
        if value and WidgetKey._langlist:
            # langlist est trié de manière à ce que la langue principale
            # soit toujours le premier élément.
            WidgetKey._langlist.sort(key= lambda x: (x != value, x))

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
        return WidgetKey._langlist
    
    @langlist.setter
    def langlist(self, value):
        """Définit la liste des langues autorisées.
        
        Cette propriété est commune à toutes les clés.
        
        La première langue de la liste fait office de langue
        principale de saisie, mais il est également possible
        définir explicitement cette dernière, s'il n'est pas certains
        que la liste est correctement triée.
        
        Parameters
        ----------
        value : list of str
            La liste des langues.
        
        Raises
        ------
        MissingParameter
            Si aucune valeur n'est fournie, ou si la liste est vide.
            
        """
        if not value:
            raise MissingParameter('langlist')
        WidgetKey._langlist = value

    def __init__(self, **kwargs):
        self._is_unborn = True
        self.uuid = uuid4()
        self._row = None
        self._is_single_child = False
        self._is_ghost = kwargs.get('is_ghost', False)
        self._parent = None
        self._is_hidden_m = False
        self._order_idx = None
        self._base_attributes(**kwargs)
        self._heritage(**kwargs)
        self._computed_attributes(**kwargs)
        self.order_idx = kwargs.get('order_idx')
        self._is_unborn = False
        if self and self.parent and not self.no_computation:
            self.parent.compute_rows()
            self.parent.compute_single_children()
        if WidgetKey.actionsbook:
            WidgetKey.actionsbook.create.append(self)

    def _base_attributes(self, **kwargs):
        return
    
    def _heritage(self, **kwargs):
        self.parent = kwargs.get('parent')
    
    def _computed_attributes(self, **kwargs):
        return
    
    def __str__(self):
        return "{} {}".format(self.key_type, self.uuid)
    
    def __repr__(self):
        return "{} {}".format(self.key_type, self.uuid)
    
    def __bool__(self):
        return not self.is_ghost
    
    @property
    def key_type(self):
        """Type de clé.
        
        Returns
        -------
        str
        
        """
        return 'WidgetKey'
    
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
        self._parent = value
        self._register(value)
 
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

    def _hide_m(self, value, rec=False):
        # pour les enfants et les boutons, cf. méthodes
        # de même nom des classes GroupKey et GroupOfValuesKey
        if not self:
            return
        old_value = self.is_hidden_m
        self._is_hidden_m = value
        if WidgetKey.actionsbook and not value and old_value:
            WidgetKey.actionsbook.show.append(self)
        elif WidgetKey.actionsbook and value and not old_value:
            WidgetKey.actionsbook.hide.append(self)

    @property
    def is_hidden(self):
        """La clé est-elle masquée ?
        
        Cette propriété, qui synthétise `is_ghost`, `is_hidden_b` et
        `is_hidden_m`, vaut True pour une clé masquée **ou fantôme**.
        Elle permet de filtrer les clés non visibles.
        
        """
        return not self or self.is_hidden_b or self.is_hidden_m

    @property
    def has_minus_button(self):
        """Un bouton moins est-il associé à la clé ?
        
        Returns
        -------
        bool
        
        Notes
        -----
        Cette propriété est définie sur la classe `WidgetKey`
        pour simplifier les tests, mais seul son alter ego
        de la classe `ObjectKey` présente un intérêt.
        
        """
        return False

    @property
    def path(self):
        """Chemin SPARQL de la clé.
        
        Returns
        -------
        str
        
        Notes
        -----
        Cette propriété sert aux recherches de clé. Elle est définie
        sur la classe `WidgetKey` par commodité, mais ce sont ses
        alter ego des classes `ObjectKey` et `GroupOfValuesKey` qui
        présentent un intérêt.
        
        """
        return None

    @property
    def independant_label(self):
        """L'étiquette de la clé occupe-t-elle sa propre ligne de la grille ?
        
        Returns
        -------
        bool
        
        Notes
        -----
        Cette propriété est définie sur la classe `WidgetKey`
        pour simplifier les tests, mais seul son alter ego
        de la classe `ValueKey` présente un intérêt.
        
        """
        return False

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
        return 0 if not self else 1

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
        return None if not self else self._row

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
        return bool(self) and self._is_single_child

    @property
    def order_idx(self):
        """Indice de classement de la clé parmi ses soeurs.
        
        Returns
        -------
        tuple of int
        
        """
        return self._order_idx

    @order_idx.setter
    def order_idx(self, value):
        """Définit l'indice de classement de la clé parmi ses soeurs.
        
        Parameters
        ----------
        value : tuple of int
        
        """
        if isinstance(self.parent, GroupOfValuesKey):
            self._order_idx = None
        else:
            self._order_idx = value or (999,)
        if not self._is_unborn:
            self.parent.compute_rows()

    @property
    def attr_to_copy(self):
        """Attributs de la classe à prendre en compte pour la copie des clés.
        
        Cette propriété est un dictionnaire dont les clés sont les
        noms des attributs contenant les informations nécessaire pour
        dupliquer la clé et les valeurs sont des booléens qui indiquent
        si la valeur serait à conserver pour créer une copie vide de la clé.
        
        Certains attributs sont volontairement exclus de cette liste, car
        ils requièrent un traitement spécifique.
        
        Returns
        -------
        dict
        
        """
        return { 'parent': True }

    def copy(self, parent=None, empty=True):
        """Renvoie une copie de la clé.
        
        Parameters
        ----------
        parent : GroupKey, optional
            La clé parente. Si elle n'est pas spécifiée, il sera
            considéré que le parent de la copie est le même que celui
            de l'original.
        empty : bool, default True
            Crée-t-on une copie vide (cas d'un nouvel enregistrement
            dans un groupe de valeurs ou de traduction) - True - ou
            souhaite-t-on dupliquer une branche de l'arbre de clés
            en préservant son contenu - False ?
        
        Returns
        -------
        WidgetKey
        
        Raises
        ------
        ForbiddenOperation
            Lorsque la méthode est explicitement appliquée à une clé
            fantôme. Il est possible de copier des branches contenant
            des fantômes, ceux-ci ne seront simplement pas copiés.
        
        Notes
        -----
        Cette méthode est complétée sur la classe `GroupKey` pour
        copier également la branche descendant de la clé, sur
        `GroupOfValuesKey` pour les boutons, et sur `ObjectKey`
        pour la jumelle éventuelle. Elle utilise la propriété
        `attr_to_copy`, qui liste les attributs non calculables
        de chaque classe.
        
        """
        if not self:
            raise ForbiddenOperation(self, 'La copie des clés fantômes ' \
                "n'est pas autorisée.")
        return self._copy(parent=parent, empty=empty)

    def _copy(self, parent=None, empty=True):
        d = self.attr_to_copy
        kwargs = { k: getattr(self, k) for k in d.keys() \
            if not empty or d[k] }
        if parent:
           kwargs['parent'] = parent
        return type(self).__call__(**kwargs)

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
        le prédicat n'est pas renseigné ou pas cohérent avec celui de
        la jumelle, c'est celui de la jumelle qui sera utilisé.
    path : str, optional
        Chemin SPARQL de la métadonnée. Si la clé appartient à un groupe
        de valeurs, c'est lui qui porte cette information. Sinon, elle
        est obligatoire. À noter que si une jumelle est déclarée et que
        le chemin n'est pas renseigné ou pas cohérent avec celui de
        la jumelle, c'est celui de la jumelle qui sera utilisé.
    label : str or Literal, optional
        Etiquette de la clé (libellé de la catégorie de métadonnée
        représentée par la clé). Cet argument est ignoré si la clé
        appartient à un groupe de valeurs. Si une jumelle est déclarée et
        que l'étiquette n'est pas renseignée ou pas cohérente avec celle de
        la jumelle, c'est celle de la jumelle qui sera utilisée.
    description : str or Literal, optional
        Définition de la catégorie de métadonnée représentée par la clé.
        Cet argument est ignoré si la clé appartient à un groupe de valeurs.
        Si une jumelle est déclarée et que le descriptif n'est pas renseigné
        ou pas cohérent avec celui de la jumelle, c'est celui de la jumelle
        qui sera utilisé.
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
    path : str
        *Propriété.* Chemin SPARQL de la métadonnée.
    label : str
        *Propriété.* Etiquette de la clé (libellé de la catégorie de
        métadonnée représentée par la clé). None pour une clé appartenant
        à un groupe de valeurs, car c'est alors lui qui porte l'étiquette.
    description : str
        *Propriété.* Définition de la catégorie de métadonnée représentée
        par la clé. None pour une clé appartenant à un groupe de valeurs,
        car c'est alors lui qui porte cette information.
    m_twin : ObjectKey
        *Propriété.* Clé jumelle.
    is_main_twin : bool
        *Propriété.* La clé est-elle la clé de référence du couple de
        jumelles ? Toujours False si la clé n'a pas de jumelle.
        La clé visible est celle qui n'est pas masquée ou, si les
        deux jumelles sont masquées, la jumelle de classe `ValueKey`.
        La clé de référence est celle qui redeviendra visible si la
        branche est démasquée en amont.
    
    Methods
    -------
    drop
        Supprime une clé-objet d'un groupe de valeurs ou de traduction
        et renvoie le carnet d'actions qui permettra de matérialiser
        l'opération sur les widgets.
    switch_twin
        Change la visibilité d'un couple de jumelles et renvoie le
        carnet d'actions qui permettra de matérialiser l'opération
        sur les widgets.
    
    """    
    def _base_attributes(self, **kwargs):
        self._predicate = None
        self._path = None
        self._label = None
        self._description = None
        self._m_twin = None
        self._is_main_twin = None
    
    def _computed_attributes(self, **kwargs):
        self.m_twin = kwargs.get('m_twin')
        self.predicate = kwargs.get('predicate')
        self.path = kwargs.get('path')
        self.label = kwargs.get('label')
        self.description = kwargs.get('description')
        self.is_hidden_m = kwargs.get('is_hidden_m')
        self.is_main_twin = kwargs.get('is_main_twin')
    
    @property
    def key_type(self):
        """Type de clé.
        
        Returns
        -------
        str
        
        """
        return 'ObjectKey'
    
    @property
    def has_minus_button(self):
        """Un bouton moins est-il associé à la clé ?
        
        Si la clé appartient à un groupe de valeurs ou de traduction,
        la méthode va chercher la propriété `with_minus_buttons` du
        groupe parent. Sinon cette propriété vaut False quoi qu'il arrive.
        
        Returns
        -------
        bool
        
        """
        if isinstance(self.parent, GroupOfValuesKey):
            return bool(self) and self.parent.with_minus_buttons
        return False
    
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
                raise MissingParameter('predicate', self)
            self._predicate = value

    @property
    def path(self):
        """Chemin représenté par la clé.
        
        Si la clé appartient à un groupe de valeurs ou de traduction,
        la méthode va chercher la propriété du groupe parent.
        
        Returns
        -------
        str
        
        """
        if isinstance(self.parent, GroupOfValuesKey):
            return self.parent.path
        return self._path

    @path.setter
    def path(self, value):
        """Définit le chemin représenté par la clé.
        
        Si la clé appartient à un groupe de valeurs ou de traduction,
        la méthode n'aura silencieusement aucun effet, car cette
        information est supposée être définie par la propriété de
        même nom du groupe.
        
        Si la clé a une jumelle dont le chemin est différent
        de la valeur fournie, c'est ce chemin qui sera utilisé.
        
        Parameters
        ----------
        value : str
            Le chemin à déclarer.
        
        Raises
        ------
        MissingParameter
            Si `value` vaut None, cette information étant obligatoire.
        
        """
        if not isinstance(self.parent, GroupOfValuesKey):
            if self.m_twin and value != self.m_twin.path:
                value = self.m_twin.path
            if not value:
                raise MissingParameter('path', self)
            self._path = value

    @property
    def label(self):
        """Etiquette de la clé.
        
        Si la clé appartient à un groupe de valeurs ou de traduction,
        la méthode renvoie None, car l'étiquette est portée par le
        groupe.
        
        Returns
        -------
        str
        
        """
        return self._label
    
    @label.setter
    def label(self, value):
        """Définit l'étiquette de la clé.
        
        Si la clé appartient à un groupe de valeurs ou de traduction,
        la méthode n'aura silencieusement aucun effet, car cette
        information est supposée être définie par la propriété de
        même nom du groupe.
        
        Si la clé a une jumelle dont l'étiquette est différente
        de la valeur fournie, c'est cette étiquette qui sera utilisée.
        
        Parameters
        ----------
        value : str or Literal
            Le libellé de l'étiquette.
        
        """
        if not isinstance(self.parent, GroupOfValuesKey):
            if self.m_twin and value != self.m_twin.label:
                value = self.m_twin.label
            if not value:
                value = '???'
            self._label = str(value)

    @property
    def description(self):
        """Descriptif de la métadonnée représentée par la clé.
        
        Si la clé appartient à un groupe de valeurs ou de traduction,
        la méthode renvoie None, car l'étiquette est portée par le
        groupe. Sinon, lorsqu'il n'y a ni étiquette, ni descriptif
        mémorisé, cette propriété renvoie le chemin - `path`.
        
        Returns
        -------
        str
        
        """
        if not isinstance(self.parent, GroupOfValuesKey):
            if self.value == '???' and not self._description:
                return self.path
            return self._description
    
    @description.setter
    def description(self, value):
        """Définit le descriptif de la métadonnée représentée par la clé.
        
        Si la clé appartient à un groupe de valeurs ou de traduction,
        la méthode n'aura silencieusement aucun effet, car cette
        information est supposée être définie par la propriété de
        même nom du groupe.
        
        Si la clé a une jumelle dont le descriptif est différent
        de la valeur fournie, c'est ce descriptif qui sera utilisé.
        
        Parameters
        ----------
        value : str or Literal
            Le descriptif.
        
        """
        if not isinstance(self.parent, GroupOfValuesKey) and value:
            if self.m_twin and value != self.m_twin.description:
                value = self.m_twin.description
            if value:
                self._description = str(value)
            else:
                self._description = None

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
        
        Les attributs `rowspan`, `predicate` and `is_hidden_m`, de la clé
        sont silencieusement mis en cohérence / déduits de ceux de la clé
        jumelle.
        
        Parameters
        ----------
        value : ObjectKey
            La clé jumelle.
        
        Raises
        ------
        ForbiddenOperation
            Si la clé cible est un fantôme, si la clé jumelle n'est pas du bon
            type (`ValueKey` pour une clé `GroupOfPropertiesKey` et inversement),
            ou si les deux clés n'ont pas le même parent.
        
        """
        if not value:
            # fait aussi tourner court toute tentative de désigner un
            # fantôme comme jumeau.
            return
        if not self :
            raise ForbiddenOperation(self, 'Un fantôme ne peut avoir ' \
                'de clé jumelle.')
        d = {ValueKey: GroupOfPropertiesKey, GroupOfPropertiesKey: ValueKey}
        if not isinstance(value, d[type(self)]):
            raise ForbiddenOperation(self, 'La clé jumelle devrait' \
                ' être de type {}.'.format(d[type(self)]))
        if self.parent != value.parent:
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
        if not self or self.parent.is_hidden_m or not self.m_twin:
            return
            # pas besoin de retoucher à la valeur
            # définie à l'initialisation ou héritée
            # du parent
        if value is None:
            value = False
        self._hide_m(value, rec=False)
        self.m_twin._hide_m(not value, rec=False)
        if not self._is_unborn:
            self.is_main_twin = not self.is_hidden_m
            self.parent.compute_rows()

    @property
    def is_main_twin(self):
        """La clé est-elle la jumelle de référence du couple ?
        
        Toujours False si la clé n'a pas de jumelle.
        
        Returns
        -------
        bool
        
        """
        return self._is_main_twin

    @is_main_twin.setter
    def is_main_twin(self, value):
        """Définit si la clé est la jumelle de référence du couple.
        
        Cette propriété n'est pas supposée être définie manuellement. Elle
        ne peut d'ailleurs l'être que lorsque les deux jumelles appartiennent
        à une branche masquée, sinon elle est déduite de `is_hidden_m`.
        
        Parameters
        ----------
        value : bool
        
        """
        if not self.m_twin:
            self._is_main_twin = False
            return
        if not self.is_hidden_m:
            self._is_main_twin = True
            self.m_twin._is_main_twin = False
            return
        if not self.m_twin.is_hidden_m:
            self._is_main_twin = False
            self.m_twin._is_main_twin = True
            return
        # reste le cas où les deux jumelles sont masquées,
        # ce qui n'est supposé arriver que dans une branche
        # masquée.
        if value is None:
            value = isinstance(self, ValueKey)
        self._is_main_twin = value
        self.m_twin._is_main_twin = not value   

    @property
    def attr_to_copy(self):
        """Attributs de la classe à prendre en compte pour la copie des clés.
        
        Cette propriété est un dictionnaire dont les clés sont les
        noms des attributs contenant les informations nécessaire pour
        dupliquer la clé et les valeurs sont des booléens qui indiquent
        si la valeur serait à conserver pour créer une copie vide de la clé.
        
        Certains attributs sont volontairement exclus de cette liste, car
        ils requièrent un traitement spécifique.
        
        Returns
        -------
        dict
        
        """
        return { 'parent': True, 'predicate': True }

    def copy(self, parent=None, empty=True):
        """Renvoie une copie de la clé.
        
        Dans le cas d'un couple de jumelles, cette méthode n'aura d'effet que
        si elle est appliquée sur la clé `GroupOfPropertiesKey`. Elle
        copie alors à la fois la clé et sa jumelle `ValueKey`.
        
        Parameters
        ----------
        parent : GroupKey, optional
            La clé parente. Si elle n'est pas spécifiée, il sera
            considéré que le parent de la copie est le même que celui
            de l'original.
        empty : bool, default True
            Crée-t-on une copie vide (cas d'un nouvel enregistrement
            dans un groupe de valeurs ou de traduction) - True - ou
            souhaite-t-on dupliquer une branche de l'arbre de clés
            en préservant son contenu - False ?
        
        Returns
        -------
        WidgetKey
        
        Raises
        ------
        ForbiddenOperation
            Lorsque la méthode est explicitement appliquée à une clé
            fantôme. Il est possible de copier des branches contenant
            des fantômes, ceux-ci ne seront simplement pas copiés.
        
        Notes
        -----
        La méthode n'est réécrite sur cette classe que pour exclure les
        jumelles `ValueKey`. Cf. `GroupOfPropertiesKey.copy` pour le
        mécanisme de copie des couples.
        
        """
        if self.m_twin:
            return
            # NB: les objets de classe `GroupOfPropertiesKey`
            # n'appellent pas cette méthode, donc cette
            # condition exclut seulement les jumeaux `ValueKey`.
        return super().copy(parent=parent, empty=empty)

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

    def drop(self):
        """Supprime une clé d'un groupe de valeur ou de traduction.
        
        Utiliser cette méthode sur une clé sans bouton moins n'a pas d'effet,
        et le carnet d'actions renvoyé est vide.
        
        Returns
        -------
        ActionsBook
            Le carnet d'actions qui permettra de répercuter sur les widgets
            la suppresssion de la clé.
        
        """
        if not self.has_minus_button:
            return ActionsBook()
        WidgetKey.clear_actionsbook()
        self.kill()
        return WidgetKey.unload_actionsbook()

    def switch_twin(self):
        """Change la visibilité d'un couple de jumelles.
        
        Utiliser cette méthode sur une clé non visible n'a pas d'effet,
        et le carnet d'actions renvoyé est vide : cette méthode est
        supposée être appliquée sur la jumelle visible du couple.
        
        Returns
        -------
        ActionsBook
            Le carnet d'actions qui permettra de répercuter le changement
            de source sur les widgets.
        
        """
        if self.is_hidden:
            return ActionsBook()
        WidgetKey.clear_actionsbook()
        self.is_hidden_m = True
        return WidgetKey.unload_actionsbook()

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
        self.children = ChildrenList()
    
    def _hide_m(self, value, rec=False):
        super()._hide_m(value, rec=rec)
        for child in self.real_children():
            child._hide_m(value, rec=True)
        if value and not self._is_unborn:
            self.compute_rows()
    
    @property
    def key_type(self):
        """Type de clé.
        
        Returns
        -------
        str
        
        """
        return 'GroupKey'
    
    def real_children(self):
        """Générateur sur les clés filles qui ne sont pas des fantômes (ni des boutons).
        
        Yields
        ------
        ValueKey or GroupKey
        
        """
        for child in self.children:
            if child:
                yield child
    
    def compute_single_children(self):
        return
    
    def compute_rows(self):
        """Actualise les indices de ligne des filles du groupe.
        
        Cette méthode n'a pas d'effet dans un groupe fantôme, ou si la
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
        if not self or WidgetKey.no_computation:
            return
        n = 0
        if not isinstance(self, GroupOfValuesKey):
            # dans les groupes de valeurs, le premier entré
            # reste toujours le premier ; dans les groupes de
            # propriétés, on trie en fonction de `order_idx`
            self.children.sort(key=lambda x: x.order_idx)
        for child in self.real_children():
            if isinstance(child, ObjectKey) and \
                child.m_twin and not child.is_main_twin:
                continue
            if child.independant_label:
                n += 1
            if child.row != n:
                child._row = n
                if WidgetKey.actionsbook:
                    WidgetKey.actionsbook.move.append(child)
            n += child.rowspan 
        return n

    def copy(self, parent=None, empty=True):
        """Renvoie une copie de la clé.
        
        La branche descendante est également dupliquée.
        
        Parameters
        ----------
        parent : GroupKey, optional
            La clé parente. Si elle n'est pas spécifiée, il sera
            considéré que le parent de la copie est le même que celui
            de l'original.
        empty : bool, default True
            Crée-t-on une copie vide (cas d'un nouvel enregistrement
            dans un groupe de valeurs ou de traduction) - True - ou
            souhaite-t-on dupliquer une branche de l'arbre de clés
            en préservant son contenu - False ?
        
        Returns
        -------
        WidgetKey
        
        Raises
        ------
        ForbiddenOperation
            Lorsque la méthode est explicitement appliquée à une clé
            fantôme. Il est possible de copier des branches contenant
            des fantômes, ceux-ci ne seront simplement pas copiés.
        
        """
        key = super().copy(parent=parent, empty=empty)
        for child in self.real_children():
            child.copy(parent=key, empty=empty)
            if empty and isinstance(child, GroupOfValuesKey):
                # dans un groupe de valeurs ou de traduction,
                # seule la première fille est copiée
                break
        return key


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
    label : str or Literal
        Etiquette de l'onglet.
    
    """
    
    def _base_attributes(self, **kwargs):
        self._label = None
        
    def _computed_attributes(self, **kwargs):
        self.label = kwargs.get('label')
    
    def _validate_parent(self, parent):
        return isinstance(parent, GroupOfPropertiesKey)
    
    @property
    def key_type(self):
        """Type de clé.
        
        Returns
        -------
        str
        
        """
        return 'TabKey'
    
    @property
    def key_object(self):
        """Transcription littérale du type de clé.
        
        """
        return 'tab'

    @property
    def label(self):
        """Etiquette de la clé.
        
        Returns
        -------
        str
        
        """
        return self._label
    
    @label.setter
    def label(self, value):
        """Définit l'étiquette de la clé.
        
        Parameters
        ----------
        value : str or Literal
            Le libellé de l'onglet.
        
        Raises
        ------
        MissingParameter
            Si aucune valeur n'est fournie, cette information
            étant obligatoire.
        
        """
        if not value:
            raise MissingParameter('label', self)
        self._label = str(value)

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
        *Propriété.* La classe RDF du noeud.
    sources : list of URIRef
        *Propriété non modifiable.* La liste de sources de la clé-valeur
        jumelle.
    
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
    def key_type(self):
        """Type de clé.
        
        Returns
        -------
        str
        
        """
        return 'GroupOfPropertiesKey'
 
    @property
    def key_object(self):
        """Transcription littérale du type de clé.
        
        """
        return 'group of properties'
 
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

    @property
    def sources(self):
        """Le cas échéant, la liste des sources de la clé-valeur jumelle.

        Cette propriété vaut toujours None pour une clé sans jumelle.
        
        Returns
        -------
        list of URIRef
        
        """
        if self.m_twin:
            return self.m_twin.sources

    def compute_rows(self):
        """Actualise les indices de ligne des filles du groupe.
        
        Cette méthode n'a pas d'effet dans un groupe fantôme, ou si la
        variable partagée `no_computation` vaut True.
        
        Returns
        -------
        int
            L'indice de la prochaine ligne disponible.
        
        Notes
        -----
        La méthode `compute_rows` de `GroupOfPropertiesKey` trie
        les clés en fonction de leur attribut `order_idx` avant
        de calculer les indices de ligne.
        
        """
        if not self or WidgetKey.no_computation:
            return
        if not isinstance(self, GroupOfValuesKey):
            self.children.sort(key=lambda x: x.order_idx)
        return super().compute_rows()

    def _hide_m(self, value, rec=False):
        if rec and value and self.m_twin and not self.is_main_twin:
            return
        super()._hide_m(value, rec=rec)

    @property
    def attr_to_copy(self):
        """Attributs de la classe à prendre en compte pour la copie des clés.
        
        Cette propriété est un dictionnaire dont les clés sont les
        noms des attributs contenant les informations nécessaire pour
        dupliquer la clé et les valeurs sont des booléens qui indiquent
        si la valeur serait à conserver pour créer une copie vide de la clé.
        
        Certains attributs sont volontairement exclus de cette liste, car
        ils requièrent un traitement spécifique.
        
        Returns
        -------
        dict
        
        """
        return { 'parent': True, 'predicate': True, 'rdftype': True }

    def copy(self, parent=None, empty=True):
        """Renvoie une copie de la clé.
        
        La branche descendante est également dupliquée, ainsi que la
        clé jumelle, le cas échéant.
        
        Parameters
        ----------
        parent : GroupKey, optional
            La clé parente. Si elle n'est pas spécifiée, il sera
            considéré que le parent de la copie est le même que celui
            de l'original.
        empty : bool, default True
            Crée-t-on une copie vide (cas d'un nouvel enregistrement
            dans un groupe de valeurs ou de traduction) - True - ou
            souhaite-t-on dupliquer une branche de l'arbre de clés
            en préservant son contenu - False ?
        
        Returns
        -------
        WidgetKey
        
        Raises
        ------
        ForbiddenOperation
            Lorsque la méthode est explicitement appliquée à une clé
            fantôme. Il est possible de copier des branches contenant
            des fantômes, ceux-ci ne seront simplement pas copiés.
        
        """
        key = GroupKey.copy(self, parent=parent, empty=empty)
        if self.m_twin:
            parent = key.parent
            twin_key = self.m_twin._copy(parent=parent, empty=empty)
            key.m_twin = twin_key
            key.is_hidden_m = self.is_hidden_m
        return key

    def kill(self):
        """Efface une clé de la mémoire de son parent.
        
        Notes
        -----
        Cette méthode réoriente simplement la commande vers la
        méthode `kill` de la classe `ObjectKey`.
        
        """
        ObjectKey.kill(self)

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
    has_minus_button : bool, default True
        True si des boutons moins (non représentés par des clés) sont
        supposés être associés aux clés du groupe.
    predicate : URIRef
        Le prédicat commun à toutes les clés du groupe.
    path : str
        Le chemin SPARQL commun à toutes les clés du groupe.
    label : str or Literal, optional
        Etiquette du groupe (libellé de la catégorie de métadonnée dont
        les filles du groupe sont les valeurs).
    description : str or Literal, optional
        Définition de la catégorie de métadonnée représentée par les clés
        du groupe.
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
        Le cas échéant, le type (xsd:type) des valeurs du groupe. La valeur
        de ce paramètre est ignorée si `rdftype` est renseigné, sinon 
        xsd:string fait office de valeur par défaut.
    placeholder : str or Literal, optional
        Texte de substitution à utiliser pour les clés du groupe.
    input_mask : str or Literal, optional
        Masque de saisie à utiliser pour les clés du groupe.
    is_mandatory : bool or Literal, default False
        Ce groupe doit-il obligatoirement avoir une clé avec une valeur ?
    is_read_only : bool or Literal, default False
        Les valeurs des clés du groupe sont-elles en lecture seule ?
    regex_validator : str, optional
        Expression rationnelle de validation à utiliser pour les clés du
        groupe.
    regex_validator_flags : str, optional
        Paramètres associés à l'expression rationnelle de validation des
        clés du groupe.
    
    Attributes
    ----------
    button : PlusButtonKey
        Référence la clé qui représente le bouton plus du groupe.
    predicate : URIRef
        *Propriété.* Prédicat commun à toutes les valeurs du groupe.
    path : str
        *Propriété.* Chemin SPARQL commun à toutes les clés du groupe.
    label : str
        *Propriété.* Etiquette du groupe (libellé de la catégorie de
        métadonnée dont les filles du groupe sont les valeurs).
    description : str
        *Propriété.* Définition de la catégorie de métadonnée représentée
        par les clés du groupe.
    with_minus_buttons : bool, default True
        True si des boutons moins (non représentés par des clés) sont
        supposés être associés aux clés du groupe.
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
        *Propriété.* Le cas échéant, le type (xsd:type) des valeurs du groupe. 
    placeholder : str
        *Propriété.* Texte de substitution à utiliser pour les clés du groupe.
    input_mask : str
        *Propriété.* Masque de saisie à utiliser pour les clés du groupe.
    is_mandatory : bool
        *Propriété.* Ce groupe doit-il obligatoirement avoir une clé avec une
        valeur ?
    is_read_only : bool
        *Propriété.* Les valeurs des clés du groupe sont-elles en lecture
        seule ?
    regex_validator : str
        *Propriété.* Expression rationnelle de validation à utiliser pour
        les clés du groupe.
    regex_validator_flags : str
        *Propriété.* Paramètres associés à l'expression rationnelle de
        validation des clés du groupe.
    
    """
    def _base_attributes(self, **kwargs):
        super()._base_attributes(**kwargs)
        self.button = None
        self._with_minus_buttons = None
        self._predicate = None
        self._path = None
        self._label = None
        self._description = None
        self._rdftype = None
        self._sources = None
        self._xsdtype = None
        self._transform = None
        self._placeholder = None
        self._input_mask = None
        self._is_mandatory = None
        self._is_read_only = None
        self._regex_validator = None
        self._regex_validator_flags = None
        
    def _computed_attributes(self, **kwargs):
        super()._computed_attributes(**kwargs)
        self.with_minus_buttons = kwargs.get('with_minus_buttons', True)
        self.predicate = kwargs.get('predicate')
        self.path = kwargs.get('path')
        self.label = kwargs.get('label')
        self.description = kwargs.get('description')
        self.rdftype = kwargs.get('rdftype')
        self.sources = kwargs.get('sources')
        self.xsdtype = kwargs.get('xsdtype')
        self.transform = kwargs.get('transform')
        self.placeholder = kwargs.get('placeholder')
        self.input_mask = kwargs.get('input_mask')
        self.is_mandatory = kwargs.get('is_mandatory')
        self.is_read_only = kwargs.get('is_read_only')
        self.regex_validator = kwargs.get('regex_validator')
        self.regex_validator_flags = kwargs.get('regex_validator_flags')
    
    def _validate_parent(self, parent):
        return isinstance(parent, (GroupOfPropertiesKey, TabKey))
    
    @property
    def key_type(self):
        """Type de clé.
        
        Returns
        -------
        str
        
        """
        return 'GroupOfValuesKey'
    
    @property
    def key_object(self):
        """Transcription littérale du type de clé.
        
        """
        return 'group of values'
    
    @property
    def with_minus_buttons(self):
        """Les filles du groupe sont-elles accompagnées de boutons moins ?
        
        Returns
        -------
        bool
        
        """
        return self._with_minus_buttons
    
    @with_minus_buttons.setter
    def with_minus_buttons(self, value):
        """Détermine si les filles du groupe sont accompagnées de boutons moins.
        
        Assure que la propriété vaudra toujours False pour un groupe fantôme.
        
        Parameters
        ----------
        value : bool
        
        """
        if not self:
            self._with_minus_buttons = False
        self._with_minus_buttons = value
    
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
            raise MissingParameter('predicate', self)
        self._predicate = value
    
    @property
    def path(self):
        """Chemin commun à toutes les valeurs du groupe.
        
        Returns
        -------
        str
        
        """
        return self._path

    @path.setter
    def path(self, value):
        """Définit le chemin commun à toutes les valeurs du groupe.
        
        Parameters
        ----------
        value : str
            Le chemin à déclarer.
        
        Raises
        ------
        MissingParameter
            Si `value` vaut None, cette information étant obligatoire.
        
        """
        if not value:
            raise MissingParameter('path', self)
        self._path = value
    
    @property
    def label(self):
        """Etiquette du groupe.
        
        Il s'agit du libellé de la métadonnée représentée par les
        clés du groupe.
        
        Returns
        -------
        str
        
        """
        return self._label
    
    @label.setter
    def label(self, value):
        """Définit l'étiquette du groupe.
        
        Parameters
        ----------
        value : str or Literal
            Le libellé de l'étiquette.
        
        """
        if not value:
            value = '???'
        self._label = str(value)

    @property
    def description(self):
        """Descriptif de la métadonnée représentée par les clés du groupe.
        
        Lorsqu'il n'y a ni étiquette, ni descriptif mémorisé, cette
        propriété renvoie le chemin - `path`.
        
        Returns
        -------
        str
        
        """
        if self.value == '???' and not self._description:
            return self.path
        return self._description
    
    @description.setter
    def description(self, value):
        """Définit le descriptif de la métadonnée représentée par les clés du groupe.
        
        Parameters
        ----------
        value : str or Literal
            Le descriptif.
        
        """
        if value:
            self._description = str(value)
        else:
            self._description = None
    
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
        if not self._is_unborn:
            self.xsdtype = self.xsdtype
    
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
        
        `rdftype` prévaut sur `xsdtype` : si le premier est renseigné,
        c'est que la valeur est un IRI ou un noeud vide, et le second
        ne peut qu'être nul. Sinon, xsd:string est utilisé comme valeur
        par défaut.
        
        Parameters
        ----------
        value : URIRef
            Le type à déclarer.
        
        """
        if self.rdftype:
            value = None
        elif not value:
            value = XSD.string
        self._xsdtype = value
        if not self._is_unborn:
            for child in self.children:
                child.value_language = child.value_language
    
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
    
    @property
    def placeholder(self):
        """Texte de substitution à utiliser pour les clés du groupe.
        
        Returns
        -------
        str
        
        """
        return self._placeholder

    @placeholder.setter
    def placeholder(self, value):
        """Définit le texte de substitution à utiliser pour les clés du groupe.
        
        Parameters
        ----------
        value : str or Literal
            Le texte de substitution à déclarer.
        
        """
        if value:
            self._placeholder = str(value)
        else:
            self._placeholder = None
    
    @property
    def input_mask(self):
        """Masque de saisie à utiliser pour les clés du groupe.
        
        Returns
        -------
        str
        
        """
        return self._input_mask

    @input_mask.setter
    def input_mask(self, value):
        """Définit le masque de saisie à utiliser pour les clés du groupe.
        
        Parameters
        ----------
        value : str or Literal
            Le masque de saisie à déclarer.
        
        """
        if value:
            self._input_mask = str(value)
        else:
            self._input_mask = None
    
    @property
    def is_mandatory(self):
        """Au moins une clé du groupe devra-t-elle obligatoirement recevoir une valeur ?
        
        Returns
        -------
        bool
        
        """
        return self._is_mandatory

    @is_mandatory.setter
    def is_mandatory(self, value):
        """Définit si au moins une clé du groupe doit obligatoirement recevoir une valeur.
        
        Parameters
        ----------
        value : bool or Literal
        
        """
        if value is None:
            value = False
        self._is_mandatory = bool(value)
    
    @property
    def is_read_only(self):
        """Les valeurs des clés du groupe sont-elles en lecture seule ?
        
        Returns
        -------
        bool
        
        """
        return self._is_read_only

    @is_read_only.setter
    def is_read_only(self, value):
        """Définit si les valeurs des clés du groupe sont lecture seule.

        Parameters
        ----------
        value : bool or Literal
        
        """
        if value is None:
            value = False
        self._is_read_only = bool(value)
    
    @property
    def regex_validator(self):
        """Expression rationnelle de validation à utiliser pour les clés du groupe.
        
        Returns
        -------
        str
        
        """
        return self._regex_validator

    @regex_validator.setter
    def regex_validator(self, value):
        """Définit l'expression rationnelle de validation à utiliser pour les clés du groupe.
        
        Parameters
        ----------
        value : str or Literal
            L'expression rationnelle.
        
        """
        if value:
            self._regex_validator = str(value)
        else:
            self._regex_validator = None
    
    @property
    def regex_validator_flags(self):
        """Paramètres associés à l'expression rationnelle de validation des clés du groupe.
        
        Returns
        -------
        str
        
        """
        return self._regex_validator_flags

    @regex_validator_flags.setter
    def regex_validator_flags(self, value):
        """Définit les paramètres associés à l'expression rationnelle de validation des clés du groupe.
        
        Parameters
        ----------
        value : str or Literal
        
        """
        if value:
            self._regex_validator_flags = str(value)
        else:
            self._regex_validator_flags = None

    def _hide_m(self, value, rec=False):
        super()._hide_m(value, rec=rec)
        if self.button:
            self.button._hide_m(value, rec=rec)

    @property
    def attr_to_copy(self):
        """Attributs de la classe à prendre en compte pour la copie des clés.
        
        Cette propriété est un dictionnaire dont les clés sont les
        noms des attributs contenant les informations nécessaire pour
        dupliquer la clé et les valeurs sont des booléens qui indiquent
        si la valeur serait à conserver pour créer une copie vide de la clé.
        
        Certains attributs sont volontairement exclus de cette liste, car
        ils requièrent un traitement spécifique.
        
        Returns
        -------
        dict
        
        """
        return { 'parent': True, 'predicate': True, 'rdftype': True,
            'sources': True, 'xsdtype': True, 'transform': True,
            'with_minus_buttons' : True }

    def copy(self, parent=None, empty=True):
        """Renvoie une copie de la clé.
        
        La branche descendante est également dupliquée, ainsi que le
        bouton du groupe, le cas échéant.
        
        Parameters
        ----------
        parent : GroupKey, optional
            La clé parente. Si elle n'est pas spécifiée, il sera
            considéré que le parent de la copie est le même que celui
            de l'original.
        empty : bool, default True
            Crée-t-on une copie vide (cas d'un nouvel enregistrement
            dans un groupe de valeurs ou de traduction) - True - ou
            souhaite-t-on dupliquer une branche de l'arbre de clés
            en préservant son contenu - False ?
        
        Returns
        -------
        WidgetKey
        
        Raises
        ------
        ForbiddenOperation
            Lorsque la méthode est explicitement appliquée à une clé
            fantôme. Il est possible de copier des branches contenant
            des fantômes, ceux-ci ne seront simplement pas copiés.
        
        """
        key = super().copy(parent=parent, empty=empty)
        if self.button:
            self.button.copy(parent=key, empty=empty)
        return key

    def compute_rows(self):
        """Actualise les indices de ligne des filles du groupe.
        
        Cette méthode n'a pas d'effet dans un groupe fantôme, ou si la
        variable partagée `no_computation` vaut True.
            
        Returns
        -------
        int
            L'indice de la prochaine ligne disponible.
        
        """
        if not self or WidgetKey.no_computation:
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
        
        Cette méthode n'a pas d'effet dans un groupe fantôme, ou si la
        variable partagée `no_computation` vaut True.
        
        """
        if not self or WidgetKey.no_computation :
            return
        true_children_count = sum([
            1 for c in self.real_children() if not c.m_twin or \
            c.is_main_twin
            ])
            # ne compte pas les fantômes ni les boutons et les
            # couples de jumelles ne comptent que pour 1
        
        for child in self.real_children():
            # boutons moins à afficher
            if true_children_count >= 2 \
                and not child.is_single_child is False:
                child._is_single_child = False
                if WidgetKey.actionsbook:
                    WidgetKey.actionsbook.show_minus_button.append(child)
            # boutons moins à masquer
            if true_children_count < 2 \
                and not child.is_single_child:
                child._is_single_child = True
                if WidgetKey.actionsbook:
                    WidgetKey.actionsbook.hide_minus_button.append(child) 


class TranslationGroupKey(GroupOfValuesKey):
    """Clé de dictionnaire de widgets représentant un groupe de traduction.
    
    Une "clé de groupe de traduction" est une clé de groupe dont les filles
    représentent les traductions d'un objet. Chaque membre du groupe
    a donc un attribut `value_language` différent, et tout l'enjeu du
    groupe de traduction est d'y veiller.
    
    Outre ses attributs propres listés ci-après, `TranslationGroupKey`
    hérite de tous les attributs de la classe `GroupOfValuesKey`. La plupart
    présentent toutefois peu d'intérêt, valant soit None, soit une valeur
    fixe (rdf:langString pour `xsd:type`).
    
    Parameters
    ----------
    parent : GroupKey
        La clé parente. Ne peut pas être None.
    is_ghost : bool, default False
        True si la clé ne doit pas être matérialisée. À noter que quelle
        que soit la valeur fournie à l'initialisation, une fille de clé
        fantôme est toujours un fantôme. Il n'est pas permis d'avoir un
        groupe de traduction fantôme, y compris par héritage. Le cas échéant,
        c'est un groupe de valeurs qui sera automatiquement créé à la place.
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
    def __new__(cls, **kwargs):
        # crée un groupe de valeurs au lieu d'un groupe de
        # traduction dans le cas d'un fantôme
        parent = kwargs.get('parent')
        if kwargs.get('is_ghost', False) or not parent:
            # si `parent` n'était pas spécifié, il y aura de toute
            # façon une erreur à l'initialisation
            return GroupOfValuesKey.__call__(**kwargs)
        return super().__new__(cls)
    
    def _base_attributes(self, **kwargs):
        super()._base_attributes(**kwargs)
        self.available_languages = self.langlist.copy()

    @property
    def key_type(self):
        """Type de clé.
        
        Returns
        -------
        str
        
        """
        return 'TranslationGroupKey'

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

    @property
    def key_object(self):
        """Transcription littérale du type de clé.
        
        """
        return 'translation group'

    def language_in(self, value_language):
        """Ajoute une langue à la liste des langues disponibles.
        
        Parameters
        ----------
        value_language : str
            Langue redevenue disponible.

        """        
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
        
        """        
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
        étiquette séparée non comprise. `rowspan` vaudra toujours 0 pour une
        clé fantôme. Si aucune valeur n'est fournie, une valeur par défaut de 1
        est appliquée.
    independant_label : bool, default False
        True si l'étiquette de la clé occupe une ligne séparée de la grille.
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
    placeholder : str or Literal, optional
        Texte de substitution à utiliser pour la clé. Si la clé appartient
        à un groupe de valeurs, c'est lui qui porte cette information, le
        cas échéant.
    input_mask : str or Literal, optional
        Masque de saisie à utiliser pour la clé. Si la clé appartient
        à un groupe de valeurs, c'est lui qui porte cette information, le
        cas échéant.
    is_mandatory : bool or Literal, default False
        Cette clé devra-t-elle obligatoirement recevoir une valeur ? Si la
        clé appartient à un groupe de valeurs, c'est lui qui porte cette
        information, le cas échéant.
    is_read_only : bool or Literal, default False
        La valeur de cette clé est-elle en lecture seule ? Si la clé appartient
        à un groupe de valeurs, c'est lui qui porte cette information, le cas
        échéant.
    regex_validator : str, optional
        Expression rationnelle de validation à utiliser pour la clé. Si la clé
        appartient à un groupe de valeurs, c'est lui qui porte cette information,
        le cas échéant.
    regex_validator_flags : str, optional
        Paramètres associés à l'expression rationnelle de validation de la clé.
        Si la clé appartient à un groupe de valeurs, c'est lui qui porte cette
        information, le cas échéant.
    rdftype : URIRef, optional
        Classe RDF de la clé-valeur, s'il s'agit d'un IRI. Si la clé appartient
        à un groupe de valeurs, c'est lui qui porte cette information, le cas
        échéant.
    xsdtype : URIRef, optional
        Le type (xsd:type) de la clé-valeur, le cas échéant. Doit impérativement
        valoir rdf:langString pour que les informations sur les
        langues soient prises en compte. Si la clé appartient à un groupe de
        valeurs, c'est lui qui porte cette information, le cas échéant.
        Dans le cas contraire, si `rdftype` n'est pas nul, il sera toujours
        considéré que `xsdtype` l'est. Sinon, xsd:string est utilisé comme
        valeur par défaut.
    do_not_save : bool, default False
        True pour une information qui ne devra pas être sauvegardée.
    value : Literal or URIRef, optional
        La valeur mémorisée par la clé (objet du triplet RDF). Une clé
        fantôme ne sera effectivement créée que si une valeur est fournie.
    value_language : str, optional
        La langue de l'objet. Obligatoire pour un Literal de
        type rdf:langString et a fortiori dans un groupe de traduction,
        ignoré pour tous les autres types.
    value_source : URIRef
        La source utilisée par la valeur courante de la clé. Si la valeur
        fournie pour l'IRI ne fait pas partie des sources autorisées, elle
        sera silencieusement supprimée.
    is_long_text : bool, default False
        Dans le cas d'une valeur de type xsd:string ou rdf:langString, indique
        si le texte est présumé long (True) ou court (False, valeur par défaut).
        Même dans un groupe de valeurs, cette propriété est définie indépendamment
        pour chaque clé, afin qu'il soit possible de l'adapter à la longueur
        effective des valeurs.
    
    Attributes
    ----------
    rowspan : int
        *Propriété.* Nombre de lignes occupées par le ou les widgets portés
        par la clé, étiquette séparée comprise. Vaut 0 pour une clé fantôme.
    available_languages : list or str
        *Propriété non modifiable.* Liste des langues disponibles pour
        les traductions.
    sources : list of URIRef
        *Propriété.* Liste des sources de vocabulaire contrôlé pour les valeurs
        de la clé.
    value : Literal or URIRef
        *Propriété.* La valeur mémorisée par la clé (objet du triplet RDF).
    rdftype : URIRef
        *Propriété.* La classe RDF de la clé-valeur, si c'est un IRI.
    xsdtype : URIRef
        *Propriété.* Le type (xsd:type) de la clé-valeur. None si
        l'objet n'est pas un Literal.
    transform : {None, 'email', 'phone'}
        *Propriété.* Le cas échéant, la nature de la transformation appliquée à
        l'objet.
    placeholder : str
        *Propriété.* Texte de substitution à utiliser pour la clé.
    input_mask : str
        *Propriété.* Masque de saisie à utiliser pour la clé.
    is_mandatory : bool
        *Propriété.* Cette clé devra-t-elle obligatoirement recevoir une valeur ?
    is_read_only : bool
        *Propriété.* La valeur de cette clé est-elle en lecture seule ?
    regex_validator : str
        *Propriété.* Expression rationnelle de validation à utiliser pour la clé.
    regex_validator_flags : str
        *Propriété.* Paramètres associés à l'expression rationnelle de validation
        de la clé.
    value_language : str
        *Propriété.* La langue de l'objet. None si l'objet n'est pas un Literal de
        type rdf:langString. Obligatoirement renseigné dans un groupe
        de traduction.
    value_source : URIRef
        *Propriété.* La source utilisée par la valeur courante de la clé.
    do_not_save : bool
        True pour une information qui ne devra pas être sauvegardée.
    is_long_text : bool
        Dans le cas d'une valeur de type xsd:string ou rdf:langString, indique
        si le texte est présumé long (True) ou court (False).
    
    Methods
    -------
    change_language(value_language)
        Change la langue d'une clé-valeur et renvoie le carnet d'actions
        qui permettra de matérialiser l'opération sur les widgets.
    change_source(value_source)
        Change la source d'une clé-valeur et renvoie le carnet d'actions
        qui permettra de matérialiser l'opération sur les widgets.
    
    """
    
    def __new__(cls, **kwargs):
        # inhibe la création de clés-valeurs fantôme sans
        # valeur (ou sans parent)
        if not kwargs.get('value') and (kwargs.get('is_ghost', False) \
            or not kwargs.get('parent')):
            return
        return super().__new__(cls)
    
    def _base_attributes(self, **kwargs):
        super()._base_attributes(**kwargs)
        self.do_not_save = kwargs.get('do_not_save', False)
        self._rowspan = 0
        self._independant_label = None
        self._sources = None
        self._rdftype = None
        self._xsdtype = None
        self._transform = None
        self._placeholder = None
        self._input_mask = None
        self._is_mandatory = None
        self._is_read_only = None
        self._regex_validator = None
        self._regex_validator_flags = None   
        self._value = None
        self._value_language = None
        self._value_source = None
        self._is_long_text = None
    
    def _computed_attributes(self, **kwargs):
        super()._computed_attributes(**kwargs)
        self.rowspan = kwargs.get('rowspan')
        self.independant_label = kwargs.get('independant_label')
        self.sources = kwargs.get('sources')
        self.rdftype = kwargs.get('rdftype')
        self.xsdtype = kwargs.get('xsdtype')
        self.transform = kwargs.get('transform')
        self.placeholder = kwargs.get('placeholder')
        self.input_mask = kwargs.get('input_mask')
        self.is_mandatory = kwargs.get('is_mandatory')
        self.is_read_only = kwargs.get('is_read_only')
        self.regex_validator = kwargs.get('regex_validator')
        self.regex_validator_flags = kwargs.get('regex_validator_flags')
        self.value = kwargs.get('value')
        self.value_language = kwargs.get('value_language')
        self.value_source = kwargs.get('value_source')
        self.is_long_text = kwargs.get('is_long_text')

    @property
    def key_type(self):
        """Type de clé.
        
        Returns
        -------
        str
        
        """
        return 'ValueKey'

    @property
    def key_object(self):
        """Transcription littérale du type de clé.
        
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
        if not self:
            value = 0
        elif self.m_twin and value != self.m_twin.rowspan:
            value = self.m_twin.rowspan
        elif not value:
            value = 1
        self._rowspan = value
        if not self._is_unborn:
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
        
        Parameters
        ----------
        value : URIRef or Literal
            La valeur.
        
        """
        if value:
            self._value = value
        else:
            self._value = None

    @property
    def rdftype(self):
        """La classe RDF de la clé-valeur.
        
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
        """Définit la classe RDF de la clé-valeur.
        
        Si la clé appartient à un groupe de valeurs ou de traduction,
        la méthode n'aura silencieusement aucun effet, car cette
        information est supposée être définie par la propriété de
        même nom du groupe.
        
        Parameters
        ----------
        value : URIRef
            La classe RDF à déclarer.
        
        """
        if not isinstance(self.parent, GroupOfValuesKey):
            self._rdftype = value
            if not self._is_unborn:
                self.xsdtype = self.xsdtype

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
        
        `rdftype` prévaut sur `xsdtype` : si le premier est renseigné,
        c'est que la valeur est un IRI, et le second ne peut qu'être nul.
        Sinon, xsd:string tient lieu de valeur par défaut.
        
        `xsdtype` prévaut sur `value_language` : si `value_language`
        contient une langue mais que `xsdtype` n'est pas rdf:langString,
        la langue sera silencieusement effacée.
        
        Parameters
        ----------
        value : URIRef
            Le type à déclarer.
        
        """
        if not isinstance(self.parent, GroupOfValuesKey):
            if self.rdftype:
                value = None
            elif not value:
                value = XSD.string
            self._xsdtype = value
            if not self._is_unborn:
                self.value_language = self.value_language
    
    @property
    def placeholder(self):
        """Texte de substitution à utiliser pour la clé.
        
        Si la clé appartient à un groupe de valeurs ou de traduction,
        la méthode va chercher la propriété du groupe parent.
        
        Returns
        -------
        str
        
        """
        if isinstance(self.parent, GroupOfValuesKey):
            return self.parent.placeholder
        return self._placeholder

    @placeholder.setter
    def placeholder(self, value):
        """Définit le texte de substitution à utiliser pour la clé.
        
        Si la clé appartient à un groupe de valeurs ou de traduction,
        la méthode n'aura silencieusement aucun effet, car cette
        information est supposée être définie par la propriété de
        même nom du groupe.
        
        Parameters
        ----------
        value : str or Literal
            Le texte de substitution à déclarer.
        
        """
        if not isinstance(self.parent, GroupOfValuesKey):
            if value:
                self._placeholder = str(value)
            else:
                self._placeholder = None
    
    @property
    def input_mask(self):
        """Masque de saisie à utiliser pour la clé.
        
        Si la clé appartient à un groupe de valeurs ou de traduction,
        la méthode va chercher la propriété du groupe parent.
        
        Returns
        -------
        str
        
        """
        if isinstance(self.parent, GroupOfValuesKey):
            return self.parent.input_mask
        return self._input_mask

    @input_mask.setter
    def input_mask(self, value):
        """Définit le masque de saisie à utiliser pour la clé.
        
        Si la clé appartient à un groupe de valeurs ou de traduction,
        la méthode n'aura silencieusement aucun effet, car cette
        information est supposée être définie par la propriété de
        même nom du groupe.
        
        Parameters
        ----------
        value : str or Literal
            Le masque de saisie à déclarer.
        
        """
        if not isinstance(self.parent, GroupOfValuesKey) and value:
            if value:
                self._input_mask = str(value)
            else:
                self._input_mask = None
    
    @property
    def is_mandatory(self):
        """Cette clé devra-t-elle obligatoirement recevoir une valeur ?
        
        Si la clé appartient à un groupe de valeurs ou de traduction,
        la méthode va chercher la propriété du groupe parent.
        
        Returns
        -------
        bool
        
        """
        if isinstance(self.parent, GroupOfValuesKey):
            return self.parent.is_mandatory
        return self._is_mandatory

    @is_mandatory.setter
    def is_mandatory(self, value):
        """Définit si la clé doit obligatoirement recevoir une valeur.
        
        Si la clé appartient à un groupe de valeurs ou de traduction,
        la méthode n'aura silencieusement aucun effet, car cette
        information est supposée être définie par la propriété de
        même nom du groupe.
        
        Parameters
        ----------
        value : bool or Literal
        
        """
        if not isinstance(self.parent, GroupOfValuesKey):
            if value is None:
                value = False
            self._is_mandatory = bool(value)
    
    @property
    def is_read_only(self):
        """La valeur de cette clé est-elle en lecture seule ?
        
        Si la clé appartient à un groupe de valeurs ou de traduction,
        la méthode va chercher la propriété du groupe parent.
        
        Returns
        -------
        bool
        
        """
        if isinstance(self.parent, GroupOfValuesKey):
            return self.parent.is_read_only
        return self._is_read_only

    @is_read_only.setter
    def is_read_only(self, value):
        """Définit si la valeur de la clé est en lecture seule.
        
        Si la clé appartient à un groupe de valeurs ou de traduction,
        la méthode n'aura silencieusement aucun effet, car cette
        information est supposée être définie par la propriété de
        même nom du groupe.
        
        Parameters
        ----------
        value : bool or Literal
        
        """
        if not isinstance(self.parent, GroupOfValuesKey):
            if value is None:
                value = False
            self._is_read_only = bool(value)
    
    @property
    def regex_validator(self):
        """Expression rationnelle de validation à utiliser pour la clé.
        
        Si la clé appartient à un groupe de valeurs ou de traduction,
        la méthode va chercher la propriété du groupe parent.
        
        Returns
        -------
        str
        
        """
        if isinstance(self.parent, GroupOfValuesKey):
            return self.parent.regex_validator
        return self._regex_validator

    @regex_validator.setter
    def regex_validator(self, value):
        """Définit l'expression rationnelle de validation à utiliser pour la clé.
        
        Si la clé appartient à un groupe de valeurs ou de traduction,
        la méthode n'aura silencieusement aucun effet, car cette
        information est supposée être définie par la propriété de
        même nom du groupe.
        
        Parameters
        ----------
        value : str or Literal
            L'expression rationnelle.
        
        """
        if not isinstance(self.parent, GroupOfValuesKey) and value:
            if value:
                self._regex_validator = str(value)
            else:
                self._regex_validator = None
    
    @property
    def regex_validator_flags(self):
        """Paramètres associés à l'expression rationnelle de validation de la clé.
        
        Si la clé appartient à un groupe de valeurs ou de traduction,
        la méthode va chercher la propriété du groupe parent.
        
        Returns
        -------
        str
        
        """
        if isinstance(self.parent, GroupOfValuesKey):
            return self.parent.regex_validator_flags
        return self._regex_validator_flags

    @regex_validator_flags.setter
    def regex_validator_flags(self, value):
        """Définit les paramètres associés à l'expression rationnelle de validation de la clé.
        
        Si la clé appartient à un groupe de valeurs ou de traduction,
        la méthode n'aura silencieusement aucun effet, car cette
        information est supposée être définie par la propriété de
        même nom du groupe.
        
        Parameters
        ----------
        value : str or Literal
        
        """
        if not isinstance(self.parent, GroupOfValuesKey) and value:
            if value:
                self._regex_validator_flags = str(value)
            else:
                self._regex_validator_flags = None
    
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
            value = None
        elif not value and isinstance(self.value, Literal):
            value = self.value.language
        if isinstance(self.parent, TranslationGroupKey):
            if not value:
                if self.available_languages:
                    value = self.available_languages[0]
                else:
                    raise IntegrityBreach(self, 'Plus de langue disponible.')
            self.parent.language_in(self._value_language)
            self.parent.language_out(value)
        self._value_language = value
    
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
    def is_long_text(self):
        """La valeur de la clé est-elle un long texte ?
        
        Returns
        -------
        bool
        
        """
        return self._is_long_text
    
    @is_long_text.setter
    def is_long_text(self, value):
        """Définit si la valeur de la clé est ou sera un long texte.
        
        Cette propriété ne peut valoir True que pour une valeur textuelle
        (type rdf:langString ou xsd:string), toute tentative dans d'autres
        circonstances serait silencieusement ignorée.
        
        Returns
        -------
        bool
        
        """
        if not value or not self.xsdtype in (RDF.langString, XSD.string):
            self._is_long_text = False
        else:
            self._is_long_text = True
    
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
    def independant_label(self):
        """L'étiquette de la clé occupe-t-elle sa propre ligne de la grille ?
        
        Returns
        -------
        bool
        
        """
        return self._independant_label
    
    @independant_label.setter
    def independant_label(self, value):
        """Définit si l'étiquette de la clé occupe sa propre ligne de la grille.
        
        Cette propriété vaudra toujours False pour une clé fantôme ou
        qui n'a pas d'étiquette.
        
        Parameters
        ----------
        value : bool
        
        """
        if not self or not self.label:
            self._independant_label = False
        self._independant_label = value or False
        if not self._is_unborn:
            self.parent.compute_rows()
    
    @property
    def label_row(self):
        """Indice de ligne de l'étiquette de la clé.
        
        Returns
        -------
        int
        
        """
        if not self.row:
            return None
        return ( self.row - 1 ) if self.independant_label else self.row 
    
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

    def _hide_m(self, value, rec=False):
        if rec and value and self.m_twin and not self.is_main_twin:
            return
        super()._hide_m(value, rec=rec)

    @property
    def attr_to_copy(self):
        """Attributs de la classe à prendre en compte pour la copie des clés.
        
        Cette propriété est un dictionnaire dont les clés sont les
        noms des attributs contenant les informations nécessaire pour
        dupliquer la clé et les valeurs sont des booléens qui indiquent
        si la valeur serait à conserver pour créer une copie vide de la clé.
        
        Certains attributs sont volontairement exclus de cette liste, car
        ils requièrent un traitement spécifique.
        
        Returns
        -------
        dict
        
        """
        return { 'parent': True, 'predicate': True, 'do_not_save': True,
            'sources': True, 'rdftype': True, 'xsdtype': True, 'transform': True,
            'rowspan': True, 'value': False, 'value_language': False,
            'value_source': False }

    def change_language(self, value_language):
        """Change la langue d'une clé-valeur.
        
        Utiliser cette méthode sur une clé non visible n'a pas d'effet,
        et le carnet d'actions renvoyé est vide.
        
        Returns
        -------
        ActionsBook
            Le carnet d'actions qui permettra de répercuter le changement
            de langue sur les widgets.
        
        """
        if self.is_hidden:
            return ActionsBook()
        WidgetKey.clear_actionsbook()
        self.language = value_language
        return WidgetKey.unload_actionsbook()
    
    def change_source(self, value_source):
        """Change la source d'une clé-valeur.
        
        Utiliser cette méthode sur une clé non visible n'a pas d'effet,
        et le carnet d'actions renvoyé est vide.
        
        Returns
        -------
        ActionsBook
            Le carnet d'actions qui permettra de répercuter le changement
            de source sur les widgets.
        
        """
        if self.is_hidden:
            return ActionsBook()
        WidgetKey.clear_actionsbook()
        self.source = value_source
        return WidgetKey.unload_actionsbook()

class PlusButtonKey(WidgetKey):
    """Clé de dictionnaire de widgets représentant un bouton plus.
    
    Il ne peut pas y avoir de bouton fantôme, de bouton dans un
    groupe fantôme, de bouton sans parent, ou de bouton dont le
    parent n'est pas un groupe valeurs ou de traduction. Dans 
    tous ces cas, rien ne sera créé.
    
    Les boutons héritent des attributs et méthodes de la classe
    `WidgetKey`. Ils n'ont pas d'attributs propres.
    
    Parameters
    ----------
    parent : GroupKey
        La clé parente. Ne peut pas être None.
    is_ghost : bool, default False
        True si la clé ne doit pas être matérialisée. À noter que quelle
        que soit la valeur fournie à l'initialisation, une fille de clé
        fantôme est toujours un fantôme. Tenter de créer un bouton plus
        fantôme ne produira rien.
    
    Methods
    -------
    add
        Ajoute une clé vierge au groupe de valeurs ou de traduction
        parent et renvoie le carnet d'actions qui permettra de
        matérialiser l'opération sur les widgets.
    
    """
    
    def __new__(cls, **kwargs):
        parent = kwargs.get('parent')
        if kwargs.get('is_ghost', False) or not parent \
            or not isinstance(parent, GroupOfValuesKey):
            return
        return super().__new__(cls)
    
    @property
    def key_type(self):
        """Type de clé.
        
        Returns
        -------
        str
        
        """
        return 'PlusButtonKey'

    @property
    def key_object(self):
        """Transcription littérale du type de clé.
        
        """
        return 'plus button'
        
    def _validate_parent(self, parent):
        return isinstance(parent, GroupOfValuesKey) \
            and not isinstance(parent, TranslationGroupKey)
        
    def _register(self, parent):
        parent.button = self
    
    @property
    def path(self):
        """Chemin SPARQL du bouton.
        
        Le chemin SPARQL d'un bouton est simplement celui de son groupe
        parent.
        
        Returns
        -------
        str
        
        """
        return self.parent.path
    
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

    def add(self):
        """Ajoute une clé vierge dans le groupe parent du bouton.
        
        Utiliser cette méthode sur un bouton masqué n'a pas d'effet,
        et le carnet d'actions renvoyé est vide. Il en irait de même
        sur un groupe ne contenant aucune clé non fantôme.
        
        Returns
        -------
        ActionsBook
            Le carnet d'actions qui permettra de répercuter sur les widgets
            la création de la clé.
        
        """
        if self.is_hidden:
            return ActionsBook()
        WidgetKey.clear_actionsbook()
        for child in self.parent.real_children():
            child.copy(parent=self.parent, empty=True)
            break
        return WidgetKey.unload_actionsbook()
        

class TranslationButtonKey(PlusButtonKey):
    """Clé de dictionnaire de widgets représentant un bouton de traduction.
    
    En cas de tentative de création d'un bouton de traduction dans
    un groupe de valeurs, c'est un bouton plus qui est créé à la place.
    
    Les boutons héritent des attributs et méthodes de la classe
    `WidgetKey`. Ils n'ont pas d'attributs propres.
    
    Parameters
    ----------
    parent : TranslationGroupKey
        La clé parente. Ne peut pas être None.
    is_ghost : bool, default False
        True si la clé ne doit pas être matérialisée. À noter que quelle
        que soit la valeur fournie à l'initialisation, une fille de clé
        fantôme est toujours un fantôme. Comme pour les boutons plus,
        tenter de créer un bouton de traduction fantôme ne produira rien.
    
    """
    
    def __new__(cls, **kwargs):
        parent = kwargs.get('parent')
        if kwargs.get('is_ghost', False) or not parent:
            # inhibe la création de boutons fantômes ou sans
            # parent
            return
        if not isinstance(parent, TranslationGroupKey):
            return PlusButtonKey.__call__(**kwargs)
        return super().__new__(cls, **kwargs)
    
    @property
    def key_type(self):
        """Type de clé.
        
        Returns
        -------
        str
        
        """
        return 'TranslationButtonKey'
   
    @property
    def key_object(self):
        """Transcription littérale du type de clé.
        
        """
        return 'translation button'
    
    @property
    def is_hidden_b(self):
        """La clé est-elle un bouton masqué ?
        
        Returns
        -------
        bool
        
        """
        return not self.parent.available_languages

    def _validate_parent(self, parent):
        return isinstance(parent, TranslationGroupKey)


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
        self.children = ChildrenList()
 
    @property
    def key_type(self):
        """Type de clé.
        
        Returns
        -------
        str
        
        """
        return 'RootKey'
 
    @property
    def key_object(self):
        """Transcription littérale du type de clé.
        
        """
        return 'root'
    
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

    @property
    def attr_to_copy(self):
        return {}

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
        if value and not value._is_unborn:
            value.parent.compute_rows()
            value.parent.compute_single_children()
            if isinstance(value.parent, TranslationGroupKey) \
                and isinstance(value, ValueKey):
                # NB : à l'initialisation, `language_out` est
                # exécuté par le setter de `value_language`.
                value.parent.language_out(value.value_language)
        
    def remove(self, value):
        super().remove(value)
        if value:
            value.parent.compute_rows()
            value.parent.compute_single_children()
        if isinstance(value.parent, TranslationGroupKey) \
            and isinstance(value, ValueKey):
            value.parent.language_in(value.value_language)



