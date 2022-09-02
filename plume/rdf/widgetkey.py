"""Clés des dictionnaires de widgets.

La classe `WidgetKey` produit les clés des dictionnaires
de widgets (classe :py:class:`plume.rdf.widgetsdict.WidgetsDict`).

Dans le contexte d'un dictionnaire, ces clés forment un arbre :

* à la base, la clé racine, de classe :py:class:`RootKey`, est la
  seule qui n'ait pas de clé "parente". Elle est référencée dans
  l'attribut `root` du dictionnaire de widgets ;
* toutes les autres clés descendent d'une clé parente,
  référencée dans leur attribut :py:attr:`WidgetKey.parent`.
  Réciproquement, les filles d'une clé sont référencées dans
  son attribut :py:attr:`GroupKey.children`.

La clé est porteuse de toutes les informations nécessaires
au maintien de l'intégrité du dictionnaire de widgets, au
paramétrage des widgets et à la sérialisation en graphe de
métadonnées (classe :py:class:`plume.rdf.metagraph.Metagraph`).

Les clés ne sont pas indépendantes les unes des autres. La
création ou la modification d'une clé entraîne la modification
(automatique) de son parent et parfois de ses soeurs.

"""

from uuid import uuid4

from plume.rdf.rdflib import URIRef, BNode, Literal
from plume.rdf.exceptions import IntegrityBreach, MissingParameter, \
    ForbiddenOperation
from plume.rdf.actionsbook import ActionsBook
from plume.rdf.namespaces import DCAT, RDF, XSD, GSP, PlumeNamespaceManager
from plume.rdf.metagraph import Metagraph
from plume.rdf.utils import DatasetId, int_from_duration, path_n3

NSM = PlumeNamespaceManager()

class WidgetKey:
    """Clé d'un dictionnaire de widgets.
    
    Parameters
    ----------
    parent : GroupKey
        La clé parente. Ne peut pas être ``None``, sauf dans le cas d'un objet
        de la classe :py:class:`RootKey` (groupe racine).
    is_ghost : bool, default False
        ``True`` si la clé ne doit pas être matérialisée. À noter que quelle
        que soit la valeur fournie à l'initialisation, une fille de clé
        fantôme est toujours un fantôme.
    order_idx : tuple of int, default (999,)
        Indice(s) permettant le classement de la clé parmi ses soeurs dans
        un groupe de propriétés. Les clés de plus petits indices seront les
        premières. Cet argument sera ignoré si le groupe parent est un
        groupe de valeurs (:py:class:`GroupOfvaluesKey`).
    
    Attributes
    ----------
    uuid : UUID
        Identifiant unique de la clé.
    
    Warnings
    --------
    Cette classe ne doit pas être utilisée directement pour créer de
    nouvelles clés. On préfèrera toujours les classes filles qui héritent
    de ses méthodes et attributs :
    
    * :py:class:`RootKey` pour la clé racine d'un arbre de clés.
    * :py:class:`GroupOfPropertiesKey` pour les groupes de propriétés.
    * :py:class:`GroupOfValuesKey` pour les groupes de valeurs.
    * :py:class:`TranslationGroupKey` pour les groupes de traduction.
    * :py:class:`TabKey` pour les onglets.
    * :py:class:`ValueKey` pour les clés-valeurs (correspondent aux
       widgets de saisie).
    * :py:class:`PlusButtonKey` pour les boutons plus des groupes de
      valeurs.
    * :py:class:`TranslationButtonKey` pour les boutons de traduction.
    
    """
    
    langlist = ['fr', 'en']
    """list(str): Liste des langues autorisées.
    
    Warnings
    --------
    Cet attribut est partagé par toutes les instances de la classe.
    Il ne doit sous aucun prétexte être modifié après l'initialisation
    de l'arbre de clés.
    
    """
    
    max_rowspan = 30
    """int: Nombre maximum de lignes pouvant être occupées par un widget.
    
    Warnings
    --------
    Cet attribut est partagé par toutes les instances de la classe.
    Il ne doit sous aucun prétexte être modifié après l'initialisation
    de l'arbre de clés.
    
    """
    
    with_language_buttons = True
    """bool: Faut-il créer des boutons de sélection de la langue ?
    
    Mettre cet attribut à ``False`` permet d'inhiber la création
    des boutons de choix de la langue, s'il y avait par ailleurs
    lieu d'en créer.
    
    Warnings
    --------
    Cet attribut est partagé par toutes les instances de la classe.
    Il ne doit sous aucun prétexte être modifié après l'initialisation
    de l'arbre de clés.
    
    """
    
    with_source_buttons = True
    """bool: Faut-il créer des boutons de sélection de la source ?
    
    Mettre cet attribut à ``False`` permet d'inhiber la création
    des boutons de choix de la source, s'il y avait par ailleurs
    lieu d'en créer.
    
    Warnings
    --------
    Cet attribut est partagé par toutes les instances de la classe.
    Il ne doit sous aucun prétexte être modifié après l'initialisation
    de l'arbre de clés.
    
    """
    
    with_unit_buttons = True
    """bool: Faut-il créer des boutons de sélection d'unité ?
    
    Mettre cet attribut à ``False`` permet d'inhiber la création
    des boutons de choix de l'unité, s'il y avait par ailleurs
    lieu d'en créer.
    
    Warnings
    --------
    Cet attribut est partagé par toutes les instances de la classe.
    Il ne doit sous aucun prétexte être modifié après l'initialisation
    de l'arbre de clés.
    
    """
    
    with_geo_buttons = True
    """bool: Faut-il créer des boutons d'aide à la saisie des géométries ?
    
    Mettre cet attribut à ``False`` permet d'inhiber la création
    des boutons d'aide à la saisie des géométries, s'il y avait par ailleurs
    lieu d'en créer.
    
    Warnings
    --------
    Cet attribut est partagé par toutes les instances de la classe.
    Il ne doit sous aucun prétexte être modifié après l'initialisation
    de l'arbre de clés.
    
    """
    
    with_compute_buttons = True
    """bool: Faut-il créer des boutons de calcul des métadonnées ?
    
    Mettre cet attribut à ``False`` permet d'inhiber la création
    des boutons de calcul, s'il y avait par ailleurs lieu d'en créer.
    
    Warnings
    --------
    Cet attribut est partagé par toutes les instances de la classe.
    Il ne doit sous aucun prétexte être modifié après l'initialisation
    de l'arbre de clés.
    
    """
    
    actionsbook = ActionsBook()
    """plume.rdf.actionsbook.ActionsBook: Carnet d'actions, qui trace les actions à réaliser sur les widgets suite aux modifications des clés.
    
    Le carnet d'actions trace les actions à réaliser sur les widgets
    au fil des modifications des clés. Pour le réinitialiser, on
    utilisera la méthode de classe :py:meth:`clear_actionsbook`, et
    :py:meth:`unload_actionsbook` pour le récupérer.
    
    Notes
    -----
    Cet attribut est partagé par toutes les instances de la classe.
    
    """
    
    no_computation = False
    """bool: Si True, empêche l'exécution immédiate de certaines opérations.
    
    Les opérations concernées sont les plus coûteuses en temps de calcul : le
    calcul des lignes et le calcul des langues disponibles dans les groupes de
    traduction. Il peut être préférable de réaliser ces opérations après avoir
    initialisé toutes les clés du groupe, plutôt qu'une fois pour chaque clé.
    
    Notes
    -----
    Cet attribut est partagé par toutes les instances de la classe.
    
    """
    
    @classmethod
    def width(cls, kind):
        """Renvoie le nombre de colonnes occupées par l'élément.
    
        Parameters
        ----------
        kind : str
            Une chaîne de caractère correspondant au nom de l'élément :
            
            * `'grid'` pour la largeur totale de la grille.
            * `'label'` pour une étiquette positionnée sur la même
              ligne que le widget de saisie. La largeur n'est pas
              fixe pour les étiquettes indépendantes (quand
              :py:attr:`WidgetKey.independant_label` vaut ``True``),
              mais calée sur le nombre de colonnes occupées par le
              widget de saisie.
            * `'unit button'` pour un bouton de sélection de
              l'unité.
            * `'language button'` pour un bouton de sélection de
              la langue.
            * `'source button'` pour un bouton de sélection de
              la source.
            * `'geo button'` pour un bouton d'aide à la saisie des
              géométries.
            * `'compute button'` pour un bouton de calcul.
            * `'minus button'` pour un bouton moins.
            * `'plus button'` pour un bouton plus.
        
        Returns
        -------
        int
        
        """
        d = {'grid': 6, 'label': 1, 'unit button': 2, 'language button': 1,
            'source button': 1, 'geo button': 1, 'compute button': 1,
            'minus button': 1, 'plus button': 1}
        # grid = label + minus button + max(language button, source button
        # geo button, unit button) + compute button + 1
        return d.get(kind)
    
    @classmethod
    def reinitiate_shared_attributes(cls):
        """Rend leur valeur par défaut à toutes les variables partagées par les instances de la classe.
        
        """
        cls.langlist = ['fr', 'en']
        cls.max_rowspan = 30
        cls.with_language_buttons = True
        cls.with_source_buttons = True
        cls.with_unit_buttons = True
        cls.with_geo_buttons = True
        cls.with_compute_buttons = True
        cls.clear_actionsbook()
        cls.no_computation = False
    
    @classmethod
    def clear_actionsbook(cls, **kwargs):
        """Remplace le carnet d'actions par un carnet vierge.
        
        Parameters
        ----------
        **kwargs : dict, optional
            Paramètres à passer à la fonction d'initialisation
            de la classe :py:class:`plume.rdf.actionsbook.ActionsBook`.
        
        """
        cls.actionsbook = ActionsBook(**kwargs)
    
    @classmethod
    def unload_actionsbook(cls, preserve_book=False):
        """Renvoie le carnet d'actions et le remplace par un carnet vierge.
        
        Parameters
        ----------
        preserve_book : bool, default False
            Si ``True`` le carnet d'actions n'est pas
            réinitialisé après récupération de son
            contenu.
        
        Returns
        -------
        plume.rdf.actionsbook.ActionsBook
        
        """
        book = cls.actionsbook
        if not preserve_book:
            cls.clear_actionsbook()
        return book
    
    @property
    def main_language(self):
        """Langue principale de saisie des métadonnées.
        
        Cette propriété est commune à toutes les clés. Concrètement,
        `main_language` est simplement la première valeur de
        :py:attr:`langlist`.
        
        Returns
        -------
        str
        
        Raises
        ------
        MissingParameter
            Si :py:attr:`langlist` ne contient pas au moins une valeur.
        
        """
        if WidgetKey.langlist:
            return WidgetKey.langlist[0]
        else:
            raise MissingParameter('langlist')
  
    @main_language.setter
    def main_language(self, value):
        """Définit la langue principale de saisie des métadonnées.
        
        Parameters
        ----------
        value : str
            La langue.
        
        Example
        -------
        >>> self.main_language = 'fr'
        
        Notes
        -----
        La langue principale n'est pas stockée indépendamment, ce
        *setter* réordonne simplement :py:attr:`langlist` pour que la
        nouvelle langue principale soit en tête de la liste. Si la
        langue n'était pas incluse dans la liste des langues autorisées,
        elle est silencieusement ajoutée.
        
        """
        if value and WidgetKey.langlist and not value in WidgetKey.langlist:
            WidgetKey.langlist.append(value)
        if value and WidgetKey.langlist:
            # langlist est trié de manière à ce que la langue principale
            # soit toujours le premier élément.
            WidgetKey.langlist.sort(key= lambda x: (x != value, x))

    def __new__(cls, **kwargs):
        if cls.__name__ == 'WidgetKey':
            raise ForbiddenOperation('La classe `WidgetKey` ne ' \
                'devrait pas être directement utilisée pour créer ' \
                'de nouvelles clés.')
        return super().__new__(cls)

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
        if self and self.parent and not WidgetKey.no_computation:
            self.parent.compute_rows()
            self.parent.compute_single_children()
        self._is_unborn = False
        WidgetKey.actionsbook.create.append(self)

    def _base_attributes(self, **kwargs):
        return
    
    def _heritage(self, **kwargs):
        self.parent = kwargs.get('parent')
    
    def _computed_attributes(self, **kwargs):
        return
    
    def __str__(self):
        if hasattr(self, 'path') and self.path:
            path = '"{}" '.format(path_n3(self.path, NSM))
        else:
            path = ''
        return "{} {}{}".format(type(self).__name__, path, self.uuid)
    
    def __repr__(self):
        if hasattr(self, 'path') and self.path:
            path = '"{}" '.format(path_n3(self.path, NSM))
        else:
            path = ''
        return "{} {}{}".format(type(self).__name__, path, self.uuid)
    
    def __bool__(self):
        return not self.is_ghost
    
    @property
    def parent(self):
        """GroupKey: Clé parente.
        
        Raises
        ------
        MissingParameter
            Quand aucune clé n'est fournie pour le parent.
        ForbiddenOperation
            En cas de tentative de modification du parent post
            initialisation de la clé.
        ForbiddenOperation
            Si la classe de l'enfant n'est pas cohérente avec celle
            du parent.
        ForbiddenOperation
            En cas de tentative pour mêler des onglets et des
            clés d'autres types dans un même groupe.
        
        Notes
        -----
        Cette propriété n'est plus modifiable après l'initialisation.
        Pour reproduire la clé avec un autre parent, on utilisera la
        méthode :py:meth:`WidgetKey.copy`. :py:meth:`WidgetKey.kill`
        permet d'effacer la clé d'origine si besoin.
        
        """
        return self._parent

    @parent.setter
    def parent(self, value):
        if not self._is_unborn:
            raise ForbiddenOperation('Modifier a posteriori ' \
                "le parent d'une clé n'est pas permis.", self)
        if value is None:
            # surtout pas "not value" ici, on ne veut pas rejeter
            # tous les parents fantômes
            raise MissingParameter('parent', self)
        if not self._validate_parent(value):
            raise ForbiddenOperation('La classe du parent ' \
                "n'est pas cohérente avec celle de la clé.", self)
        for child in value.children:
            if isinstance(self, TabKey) and not isinstance(child, TabKey):
                raise ForbiddenOperation("Il n'est pas permis " \
                    'de créer un onglet dans un groupe contenant ' \
                    "des clés d'autres types.", self)
            if not isinstance(self, TabKey) and isinstance(child, TabKey):
                raise ForbiddenOperation('Le groupe parent ' \
                    "contenant un onglet, il n'est pas permis d'y " \
                    "ajouter des clés d'autres types.", self)
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
    def generation(self):
        """int: Génération à laquelle appartient la clé.
        
        ``0`` pour la clé-racine, ``1`` pour ses enfants, etc.
        
        """
        return 1 + self.parent.generation
    
    @property
    def is_ghost(self):
        """bool: La clé est-elle une clé fantôme non matérialisée ?
        
        Notes
        -----
        Cette propriété n'est plus modifiable une fois la clé
        initialisée, sauf pour les certains groupes dont, entre
        autres conditions, tous les enfants sont des fantômes.
        
        :py:attr:`is_ghost` définit la valeur booléenne de la clé :
        ``bool(widgetkey)`` vaut ``False`` si ``widgetkey`` est une
        clé fantôme.
        
        See Also
        --------
        GroupOfPropertiesKey.is_ghost :
            Réécriture de la propriété pour les groupes de propriétés.
        GroupOfValuesKey.is_ghost :
            Réécriture de la propriété pour les groupes de valeurs.
        TabKey.is_ghost :
            Réécriture de la propriété pour les onglets.
        
        """
        return self._is_ghost
    
    @property
    def is_hidden_b(self):
        """bool: La clé est-elle un bouton masqué ?
        
        Notes
        -----
        Cette propriété est en lecture seule. Elle est définie sur la
        classe :py:class:`WidgetKey` pour simplifier les tests de visibilité,
        mais elle vaut toujours ``False`` quand la clé n'est pas un bouton.
        
        See Also
        --------
        PlusButtonKey.is_hidden_b :
            Réécriture de la propriété pour un bouton plus.
        TranslationButtonKey.is_hidden_b :
            Réécriture de la propriété pour un bouton de traduction.
        
        """
        return False
    
    @property
    def is_hidden_m(self):
        """bool: La clé appartient-elle à une branche masquée ?
        
        Cette propriété héréditaire vaut ``True`` pour la clé présentement
        masquée d'un couple de jumelles, ou toute clé descendant de
        celle-ci (branche masquée).
        
        Notes
        -----
        Cette propriété est en lecture seule. Le *setter* est défini
        sur la classe :py:class:`ObjectKey`.
        
        See Also
        --------
        ObjectKey.is_hidden_m
            Réécriture de la propriété pour les clés-objets.
        
        """
        return self._is_hidden_m

    def _hide_m(self, value, rec=False):
        # pour les enfants et les boutons, cf. méthodes
        # de même nom des classes GroupKey et GroupOfValuesKey
        if not self:
            return
        old_value = self.is_hidden_m
        self._is_hidden_m = value
        if not value and old_value:
            WidgetKey.actionsbook.show.append(self)
        elif value and not old_value:
            WidgetKey.actionsbook.hide.append(self)

    @property
    def is_hidden(self):
        """bool: La clé est-elle masquée ?
        
        Cette propriété, qui synthétise :py:attr:`is_ghost`,
        :py:attr:`is_hidden_b` et :py:attr:`is_hidden_m`, vaut ``True``
        pour une clé masquée ou fantôme. Elle permet de filtrer les clés
        non matérialisées ou non visibles.
        
        Notes
        -----
        Cette propriété est en lecture seule.
        
        """
        return not self or self.is_hidden_b or self.is_hidden_m

    @property
    def has_minus_button(self):
        """bool: Un bouton moins est-il associé à la clé ?
        
        Notes
        -----
        Cette propriété est en lecture seule. Elle est définie sur la
        classe :py:class:`WidgetKey` pour simplifier les tests, mais elle
        vaut toujours ``False`` quand la clé n'est pas une clé-objet
        (:py:class:`ObjectKey`).
        
        See Also
        --------
        ObjectKey.has_minus_button
        
        """
        return False

    @property
    def has_language_button(self):
        """bool: Un bouton annexe de sélection de la langue doit-il être créé pour la clé ?
        
        Notes
        -----
        Cette propriété est en lecture seule. Elle est définie sur la
        classe :py:class:`WidgetKey` pour simplifier les tests, mais elle
        vaut toujours ``False`` quand la clé n'est pas une clé-valeur
        (:py:class:`ValueKey`).
        
        See Also
        --------
        ValueKey.has_language_button
        
        """
        return False

    @property
    def has_source_button(self):
        """bool: Un bouton annexe de sélection de la source doit-il être créé pour la clé ?
        
        Notes
        -----
        Cette propriété est en lecture seule. Elle est définie sur la
        classe :py:class:`WidgetKey` pour simplifier les tests, mais elle
        vaut toujours ``False`` quand la clé n'est pas une clé-objet
        (:py:class:`ObjectKey`).
        
        See Also
        --------
        ValueKey.has_source_button, GroupOfPropertiesKey.has_source_button
        
        """
        return False

    @property
    def has_unit_button(self):
        """bool: Un bouton annexe de sélection de l'unité doit-il être créé pour la clé ?
        
        Notes
        -----
        Cette propriété est en lecture seule. Elle est définie sur la
        classe :py:class:`WidgetKey` pour simplifier les tests, mais elle
        vaut toujours ``False`` quand la clé n'est pas une clé-valeur
        (:py:class:`ValueKey`).
        
        See Also
        --------
        ValueKey.has_unit_button
        
        """
        return False

    @property
    def has_geo_button(self):
        """bool: Un bouton annexe d'aide à la saisie des géométries doit-il être créé pour la clé ?
        
        Notes
        -----
        Cette propriété est en lecture seule. Elle est définie sur la
        classe :py:class:`WidgetKey` pour simplifier les tests, mais elle
        vaut toujours ``False`` quand la clé n'est pas une clé-valeur
        (:py:class:`ValueKey`).
        
        See Also
        --------
        ValueKey.has_geo_button
        
        """
        return False

    @property
    def has_compute_button(self):
        """bool: Un bouton annexe de calcul de la métadonnée doit-il être créé pour la clé ?
        
        Notes
        -----
        Cette propriété est en lecture seule. Elle est définie sur la
        classe :py:class:`WidgetKey` pour simplifier les tests, mais elle
        vaut toujours ``False`` quand la clé n'est pas une clé-valeur
        (:py:class:`ValueKey`) ou un groupe de valeurs.
        
        See Also
        --------
        ValueKey.has_compute_button, GroupOfValuesKey.has_compute_button
        
        """
        return False

    @property
    def has_label(self):
        """bool: Une étiquette non intégrée au widget principal doit-elle être créée pour la clé ?
        
        Notes
        -----
        Cette propriété est en lecture seule. Elle est définie sur la
        classe :py:class:`WidgetKey` pour simplifier les tests, mais elle
        vaut toujours ``False`` quand la clé n'est pas une clé-valeur
        (:py:class:`ValueKey`).
        
        See Also
        --------
        ValueKey.has_label
        
        """
        return False

    @property
    def path(self):
        """rdflib.paths.SequencePath: Chemin de la clé.
        
        Notes
        -----
        Cette propriété est en lecture seule. Elle est définie
        sur la classe :py:class:`WidgetKey` par commodité, mais elle vaut
        ``None`` si la clé n'appartient pas aux classes :py:class:`ObjectKey`
        ou :py:class:`GroupOfValuesKey`.
        
        See Also
        --------
        ObjectKey.path, GroupOfValuesKey.path
        
        """
        return None

    @property
    def independant_label(self):
        """bool: L'étiquette de la clé occupe-t-elle sa propre ligne de la grille ?
        
        Notes
        -----
        Cette propriété est en lecture seule. Elle est définie sur la classe
        :py:class:`WidgetKey` pour simplifier les tests, mais elle vaut
        toujours ``False`` quand la clé n'est pas une clé-valeur
        (:py:class:`ValueKey`).
        
        See Also
        --------
        ValueKey.independant_label
        
        """
        return False

    @property
    def row(self):
        """int: Ligne de la clé dans la grille.
        
        Vaut toujours ``None`` pour une clé fantôme.
        
        Notes
        -----
        Propriété calculée par :py:meth:`GroupKey.compute_rows`,
        accessible uniquement en lecture.
        
        """
        return None if not self else self._row

    @property
    def rowspan(self):
        """int: Nombre de lignes de la grille occupées par la clé.
        
        Notes
        -----
        Cette propriété est en lecture seule. Dans le cas général, 
        elle vaut ``1`` si la clé n'est pas un fantôme (cf.
        :py:attr:`WidgetKey.is_ghost`) et ``0`` sinon. Elle ne peut
        être modifiée et prendre d'autres valeurs que pour les
        clés-valeurs.
        
        See Also
        --------
        ValueKey.independant_label
        
        """
        return 0 if not self else 1

    @property
    def placement(self):
        """tuple(int): Placement du widget principal de la clé dans la grille, le cas échéant.
        
        Cette propriété est un tuple formé de quatre éléments :
        
        * ``[0]`` est l'indice de ligne.
        * ``[1]`` est l'indice de colonne.
        * ``[2]`` est le nombre de lignes occupées.
        * ``[3]`` est le nombre de colonnes occupées.
        
        Elle vaut ``None`` pour une clé fantôme, un onglet ou une clé-racine.
        
        See Also
        --------
        PlusButtonKey.placement, RootKey.placement, TabKey.placement
        
        """
        if not self:
            return
        columnspan = WidgetKey.width('grid') \
            - (WidgetKey.width('unit button') \
                if self.has_unit_button else 0) \
            - (WidgetKey.width('language button') \
                if self.has_language_button else 0) \
            - (WidgetKey.width('source button') \
                if self.has_source_button else 0) \
            - (WidgetKey.width('geo button') \
                if self.has_geo_button else 0) \
            - (WidgetKey.width('compute button') \
                if self.has_compute_button else 0) \
            - (WidgetKey.width('minus button') \
                if self.has_minus_button else 0) \
            - (WidgetKey.width('label') if self.has_label \
                and not self.independant_label else 0)
        column = WidgetKey.width('label') if self.has_label \
            and not self.independant_label else 0
        return (self.row, column, self.rowspan, columnspan)

    @property
    def unit_button_placement(self):
        """tuple(int): Placement du bouton de sélection de l'unité dans la grille, le cas échéant.
        
        Cette propriété est un tuple formé de quatre éléments :
        
        * ``[0]`` est l'indice de ligne.
        * ``[1]`` est l'indice de colonne.
        * ``[2]`` est le nombre de lignes occupées.
        * ``[3]`` est le nombre de colonnes occupées.
        
        Elle vaut ``None`` pour une clé fantôme ou qui n'a pas de bouton
        de sélection d'unité.
        
        Notes
        -----
        Le bouton de sélection d'unité est placé immédiatement à droite
        du widget principal.
        
        """
        if not self.has_unit_button:
            return
        row, column, rowspan, columnspan = self.placement
        return (row, column + columnspan, 1, WidgetKey.width('unit button'))

    @property
    def language_button_placement(self):
        """tuple(int): Placement du bouton de sélection de la langue dans la grille, le cas échéant.
        
        Cette propriété est un tuple formé de quatre éléments :
        
        * ``[0]`` est l'indice de ligne.
        * ``[1]`` est l'indice de colonne.
        * ``[2]`` est le nombre de lignes occupées.
        * ``[3]`` est le nombre de colonnes occupées.
        
        Elle vaut ``None`` pour une clé fantôme ou qui n'a pas de bouton
        de sélection de la langue.
        
        Notes
        -----
        Le bouton de sélection de la source est placé à droite du widget
        principal et de l'éventuel bouton de sélection de la langue.
        En pratique, les boutons de sélection d'unité et de sélection
        de la langue étant liés à des types différents, ils n'apparaissent
        jamais simultanément et le bouton de sélection de la langue sera
        placé immédiatement à droite du widget principal.
        
        """
        if not self.has_language_button:
            return
        row, column, rowspan, columnspan = self.placement
        column = column + columnspan \
            + (WidgetKey.width('unit button') \
                if self.has_unit_button else 0) 
        return (row, column, 1, WidgetKey.width('language button'))

    @property
    def source_button_placement(self):
        """tuple(int): Placement du bouton de sélection de la source dans la grille, le cas échéant.
        
        Cette propriété est un tuple formé de quatre éléments :
        
        * ``[0]`` est l'indice de ligne.
        * ``[1]`` est l'indice de colonne.
        * ``[2]`` est le nombre de lignes occupées.
        * ``[3]`` est le nombre de colonnes occupées.
        
        Elle vaut ``None`` pour une clé fantôme ou qui n'a pas de bouton
        de sélection de la source.
        
        Notes
        -----
        Le bouton de sélection de la source est placé à droite du widget
        principal et des éventuels boutons de sélection de l'unité
        et bouton de sélection la langue (lesquels ne peuvent en pratique
        jamais apparaître en même temps qu'un bouton de sélection de
        la source).
        
        """
        if not self.has_source_button:
            return
        row, column, rowspan, columnspan = self.placement
        column = column + columnspan \
            + (WidgetKey.width('unit button') \
                if self.has_unit_button else 0) \
            + (WidgetKey.width('language button') \
                if self.has_language_button else 0) 
        return (row, column, 1, WidgetKey.width('source button'))

    @property
    def geo_button_placement(self):
        """tuple(int): Placement du bouton d'aide à la saisie des géométries dans la grille, le cas échéant.
        
        Cette propriété est un tuple formé de quatre éléments :
        
        * ``[0]`` est l'indice de ligne.
        * ``[1]`` est l'indice de colonne.
        * ``[2]`` est le nombre de lignes occupées.
        * ``[3]`` est le nombre de colonnes occupées.
        
        Elle vaut ``None`` pour une clé fantôme ou qui n'a pas de bouton
        de sélection d'aide à la saisie des géométries.
        
        Notes
        -----
        Le bouton d'aide à la saisie des géométries est placé à droite du
        widget principal et des éventuels boutons de sélection de l'unité,
        bouton de sélection la langue et bouton de sélection de la source
        (lesquels ne peuvent en pratique jamais apparaître en même temps
        qu'un bouton d'aide à la saisie des géométries).
        
        """
        if not self.has_geo_button:
            return
        row, column, rowspan, columnspan = self.placement
        column = column + columnspan \
            + (WidgetKey.width('unit button') \
                if self.has_unit_button else 0) \
            + (WidgetKey.width('language button') \
                if self.has_language_button else 0) \
            + (WidgetKey.width('source button') \
                if self.has_source_button else 0)
        return (row, column, 1, WidgetKey.width('geo button'))

    @property
    def compute_button_placement(self):
        """tuple(int): Placement du bouton de calcul dans la grille, le cas échéant.
        
        Cette propriété est un tuple formé de quatre éléments :
        
        * ``[0]`` est l'indice de ligne.
        * ``[1]`` est l'indice de colonne.
        * ``[2]`` est le nombre de lignes occupées.
        * ``[3]`` est le nombre de colonnes occupées.
        
        Elle vaut ``None`` pour une clé fantôme ou qui n'a pas de bouton
        de calcul.
        
        Notes
        -----
        Le bouton de calcul est placé à droite du widget principal et des
        éventuels boutons de sélection de l'unité, bouton de sélection la langue
        et bouton de sélection de la source et bouton d'aide à la saisie des
        géométries (en supposant qu'ils puissent apparaître ensemble).
        
        """
        if not self.has_compute_button:
            return
        row, column, rowspan, columnspan = self.placement
        column = column + columnspan \
            + (WidgetKey.width('unit button') \
                if self.has_unit_button else 0) \
            + (WidgetKey.width('language button') \
                if self.has_language_button else 0) \
            + (WidgetKey.width('source button') \
                if self.has_source_button else 0) \
            + (WidgetKey.width('geo button') \
                if self.has_geo_button else 0)
        return (row, column, 1, WidgetKey.width('compute button'))

    @property
    def minus_button_placement(self):
        """tuple(int): Placement du bouton moins dans la grille, le cas échéant.
        
        Cette propriété est un tuple formé de quatre éléments :
        
        * ``[0]`` est l'indice de ligne.
        * ``[1]`` est l'indice de colonne.
        * ``[2]`` est le nombre de lignes occupées.
        * ``[3]`` est le nombre de colonnes occupées.
        
        Elle vaut ``None`` pour une clé fantôme ou qui n'a pas de bouton moins.
        
        Notes
        -----
        Le bouton moins est placé à droite du widget principal et des éventuels
        boutons de sélection de l'unité, de sélection de la langue, de
        sélection de la source, d'aide à la saisie des géométries et
        de calcul.
        
        """
        if not self.has_minus_button:
            return
        row, column, rowspan, columnspan = self.placement
        column = column + columnspan \
            + (WidgetKey.width('unit button') \
                if self.has_unit_button else 0) \
            + (WidgetKey.width('language button') \
                if self.has_language_button else 0) \
            + (WidgetKey.width('source button') \
                if self.has_source_button else 0) \
            + (WidgetKey.width('geo button') \
                if self.has_geo_button else 0) \
            + (WidgetKey.width('compute button') \
                if self.has_compute_button else 0)
        return (row, column, 1, WidgetKey.width('minus button'))
    
    @property
    def label_placement(self):
        """tuple(int): Placement de l'étiquette dans la grille, le cas échéant.
        
        Cette propriété est un tuple formé de quatre éléments :
        
        * ``[0]`` est l'indice de ligne.
        * ``[1]`` est l'indice de colonne.
        * ``[2]`` est le nombre de lignes occupées.
        * ``[3]`` est le nombre de colonnes occupées.
        
        Elle vaut ``None`` pour une clé fantôme, qui n'a pas d'étiquette
        ou dont l'étiquette est intégrée au widget principal.
        
        """
        if not self.has_label:
            return
        row, column, rowspan, columnspan = self.placement
        row = ( row - 1 ) if self.independant_label else row
        if not self.independant_label:
            columnspan = WidgetKey.width('label')
        return (row, 0, 1, columnspan)

    @property
    def is_single_child(self):
        """bool: La clé est-elle un enfant unique ?
        
        Notes
        -----
        Propriété calculée par
        :py:meth:`GroupOfValuesKey.compute_single_children`, accessible
        uniquement en lecture.
        
        """
        return bool(self) and self._is_single_child

    @property
    def order_idx(self):
        """tuple(int): Indice de classement de la clé parmi ses soeurs.
        
        Notes
        -----
        Si la clé appartient à un groupe de valeurs ou de traduction,
        modifier la valeur de cette propriété n'aura silencieusement aucun
        effet, car il n'y a pas de notion d'ordre dans ces groupes.
        :py:attr:`WidgetKey.order_idx` y vaut toujours ``None``.
        Dans le cas contraire, ``None`` est silencieusement remplacé par
        ``(9999,)``, de manière ce que les clés sans indice soient classées
        après les autres.
        
        Modifier cette propriété emporte la mise en cohérence de la propriété
        :py:attr:`WidgetKey.row` pour toutes les clés du groupe parent.
        
        See Also
        --------
        ObjectKey.order_idx
        
        """
        return self._order_idx

    @order_idx.setter
    def order_idx(self, value):
        if isinstance(self.parent, GroupOfValuesKey):
            self._order_idx = None
        else:
            self._order_idx = value or (9999,)
        if not self._is_unborn:
            self.parent.compute_rows()

    @property
    def tree_idx(self):
        """tuple: Représentation du placement de la clé dans l'arbre.
        
        """
        l = list(self.parent.tree_idx)
        l.append(self.parent.children.index(self))
        return tuple(l)

    @property
    def attr_to_copy(self):
        """dict: Attributs de la classe à prendre en compte pour la copie des clés.
        
        Cette propriété est un dictionnaire dont les clés sont les
        noms des attributs contenant les informations nécessaires pour
        dupliquer la clé, et les valeurs sont des booléens qui indiquent
        si l'attribut est à prendre en compte lorsqu'il s'agit de
        créer une copie vide de la clé.
        
        Certains attributs sont volontairement exclus de cette liste, car
        ils requièrent un traitement spécifique.
        
        See Also
        --------
        WidgetKey.copy
        
        Notes
        -----
        Plusieurs classes filles de :py:class:`WidgetKey` redéfinissent
        cette propriété, en complétant le dictionnaire avec leurs propres
        attributs.
        
        """
        return { 'order_idx': True, 'parent': True }

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
            dans un groupe de valeurs ou de traduction) - ``True`` - ou
            souhaite-t-on dupliquer une branche de l'arbre de clés
            en préservant son contenu - ``False`` ?
        
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
        Cette méthode est complétée sur la classe :py:class:`GroupKey`
        pour copier également la branche descendant de la clé, sur
        :py:class:`GroupOfValuesKey` pour les boutons, et sur
        :py:class:`GroupOfPropertiesKey` et :py:class:`ValueKey`
        pour la jumelle éventuelle. Elle utilise la propriété
        :py:attr:`attr_to_copy`, qui liste les attributs non calculables
        de chaque classe.
        
        """
        if not self:
            raise ForbiddenOperation('La copie des clés fantômes ' \
                "n'est pas autorisée.", self)
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
        de la clé effacée. Elle coupe simplement la branche de
        l'arbre. Pour autant tous les descendants de la clé sont
        enregistrés la liste :py:attr:`plume.rdf.actionsbook.ActionsBook.drop`
        du carnet d'actions.
        
        La méthode est sans effet sur les clés-racine (:py:class:`RootKey`).
        
        """
        self.parent.children.remove(self)
        WidgetKey.actionsbook.drop.append(self)
        if isinstance(self, GroupKey):
            self._notify_dead_children()

    @property
    def attr_to_update(self):
        """list(str): Liste des attributs et propriétés pouvant être redéfinis post initialisation.
        
        Notes
        -----
        Plusieurs des classes filles de :py:class:`WidgetKey` redéfinissent
        cette propriété en ajoutant ou retirant des attributs à la liste.
        
        """
        return ['order_idx']

    def update(self, exclude_none=False, **kwargs):
        """Met à jour les attributs de la clé selon les valeurs fournies.
        
        Parameters
        ----------
        exclude_none : bool
            Si ``True``, les attributs ne seront mis à jour que
            si la nouvelle valeur n'est pas ``None``.
        **kwargs : dict
            Les attributs à mettre à jour. Si un attribut n'est
            pas défini pour la classe de la clé ou s'il n'est
            pas modifiable, il sera silencieusement ignoré.
        
        """
        for k, v in kwargs.items():
            if k in self.attr_to_update and \
                (not v is None or not exclude_none):
                setattr(self, k, v)

    def _tree_keys(self):
        if self:
            yield self

class ObjectKey(WidgetKey):
    """Clé-objet.
    
    Une clé-objet est une clé de dictionnaire de widgets représentant
    un couple prédicat/objet d'un graphe RDF. Le sujet du triplet est
    alors sa clé parente.
    
    Outre ses propriétés propres listées ci-après, :py:class:`ObjectKey`
    hérite des attributs et méthodes de la classe :py:class:`WidgetKey`.
    
    Parameters
    ----------
    parent : GroupKey
        La clé parente. Ne peut pas être ``None``.
    is_ghost : bool, default False
        ``True`` si la clé ne doit pas être matérialisée. À noter que quelle
        que soit la valeur fournie à l'initialisation, une fille de clé
        fantôme est toujours un fantôme.
    order_idx : tuple of int, default (999,)
        Indice(s) permettant le classement de la clé parmi ses soeurs dans
        un groupe de propriétés. Les clés de plus petits indices seront les
        premières. Cet argument sera ignoré si le groupe parent est un
        groupe de valeurs (:py:class:`GroupOfvaluesKey`).
    predicate : rdflib.term.URIRef
        Prédicat représenté par la clé. Si la clé appartient à un groupe
        de valeurs, c'est lui qui porte cette information. Sinon, elle
        est obligatoire. Pour des clés jumelles, le prédicat déclaré
        sur la jumelle de référence prévaut, sauf s'il vaut ``None``.
    label : str or rdflib.term.Literal, optional
        Etiquette de la clé (libellé de la catégorie de métadonnée
        représentée par la clé). Cet argument est ignoré si la clé
        appartient à un groupe de valeurs. Pour des clés jumelles,
        l'étiquette déclarée sur la jumelle de référence prévaut.
    description : str or rdflib.term.Literal, optional
        Définition de la catégorie de métadonnée représentée par la clé.
        Cet argument est ignoré si la clé appartient à un groupe de valeurs.
        Pour des clés jumelles, le descriptif déclaré sur la jumelle de
        référence prévaut.
    m_twin : ObjectKey, optional
        Clé jumelle, le cas échéant. Un couple de jumelle ne se déclare
        qu'une fois, sur la seconde clé créée.
    is_hidden_m : bool, default False
        La clé est-elle la clé masquée du couple de jumelles ? Ce paramètre
        n'est pris en compte que pour une clé qui a une jumelle.
    is_read_only : bool or rdflib.term.Literal, default False
        La clé est-elle en lecture seule ? Si la clé appartient
        à un groupe de valeurs, c'est lui qui porte cette information.
        Une clé appartenant à un groupe de propriétés en lecture seule
        sera elle-même considérée comme étant en lecture seule.        
    
    Warnings
    --------
    Cette classe ne doit pas être utilisée directement pour créer de
    nouvelles clés. On préfèrera toujours les classes filles qui héritent
    de ses méthodes et attributs :
    
    * :py:class:`GroupOfPropertiesKey` pour les groupes de propriétés.
      C'est la classe à utiliser lorsque l'objet du triplet RDF est un 
      noeud anonyme.
    * :py:class:`ValueKey` pour les clés-valeurs (correspondent aux
      widgets de saisie). C'est la classe à utiliser lorsque l'objet
      du triplet RDF est un IRI ou une valeur litérale.
    
    """
    
    def __new__(cls, **kwargs):
        if cls.__name__ == 'ObjectKey':
            raise ForbiddenOperation('La classe `ObjectKey` ne ' \
                'devrait pas être directement utilisée pour créer ' \
                'de nouvelles clés.')
        return super().__new__(cls, **kwargs)
    
    def _base_attributes(self, **kwargs):
        self._is_read_only = None
        self._predicate = None
        self._label = None
        self._description = None
        self._m_twin = None
        self._is_main_twin = None
    
    def _computed_attributes(self, **kwargs):
        self.is_read_only = kwargs.get('is_read_only')
        self.m_twin = kwargs.get('m_twin')
        self.predicate = kwargs.get('predicate')
        self.label = kwargs.get('label')
        self.description = kwargs.get('description')
        self.is_hidden_m = kwargs.get('is_hidden_m')
        self.is_main_twin = kwargs.get('is_main_twin')
    
    @property
    def is_read_only(self):
        """bool: La clé est-elle en lecture seule ?
        
        Notes
        -----
        Si la clé appartient à un groupe de valeurs ou de traduction,
        la propriété du groupe parent est renvoyée. Tenter d'en modifier
        la valeur n'aura silencieusement aucun effet.
        
        Si la clé appartient à un groupe de propriétés, elle
        sera considérée comme étant en lecture seule si le groupe
        parent est en lecture seule ou si la clé elle-même est
        paramétrée comme telle.
        
        Les clés en lecture seule ne sont accompagnées d'aucun bouton.

        Il est permis de fournir des valeurs de type ``rdflib.term.Literal``,
        qui seront alors automatiquement converties.
        
        """
        if isinstance(self.parent, GroupOfValuesKey):
            return self.parent.is_read_only
        elif isinstance(self.parent, GroupOfPropertiesKey):
            return self.parent.is_read_only or self._is_read_only
        return self._is_read_only

    @is_read_only.setter
    def is_read_only(self, value):
        if not isinstance(self.parent, GroupOfValuesKey):
            self._is_read_only = bool(value)
    
    @property
    def has_minus_button(self):
        """bool: Un bouton moins est-il associé à la clé ?
        
        Notes
        -----
        Cette propriété est en lecture seule. Si la clé appartient à
        un groupe de valeurs ou de traduction, elle est déduite de la
        propriété :py:attr:`GroupOfValuesKey.with_minus_buttons` du groupe
        parent, sinon elle vaut ``False`` quoi qu'il arrive.
        
        """
        if isinstance(self.parent, GroupOfValuesKey):
            return bool(self) and self.parent.with_minus_buttons \
                and not self.is_read_only
        return False
    
    @property
    def predicate(self):
        """rdflib.term.URIRef: Prédicat représenté par la clé.
        
        Raises
        ------
        MissingParameter
            Pour toute tentative de mettre à ``None`` la valeur de cette
            propriété alors que la clé n'appartient pas à un groupe de valeurs,
            cette information étant alors obligatoire.
        
        Notes
        -----
        Si la clé appartient à un groupe de valeurs ou de traduction,
        la propriété du groupe parent est renvoyée. Tenter d'en modifier
        la valeur n'aura silencieusement aucun effet.
        
        Si la clé a une jumelle dont le prédicat est différent
        de la valeur fournie, c'est celui de la jumelle de référence
        qui prévaudra, sauf s'il vaut ``None``. Autrement dit, pour
        changer le prédicat d'un couple de jumelles, il faut cibler
        la jumelle de référence, sans quoi l'opération n'aura pas d'effet.
        
        """
        if isinstance(self.parent, GroupOfValuesKey):
            return self.parent.predicate
        return self._predicate

    @predicate.setter
    def predicate(self, value):
        if not isinstance(self.parent, GroupOfValuesKey):
            if self.m_twin and (not self.is_main_twin or not value):
                value = self.m_twin.predicate
            if not value:
                raise MissingParameter('predicate', self)
            self._predicate = value
            if self.m_twin and value != self.m_twin.predicate \
                and self.is_main_twin:
                self.m_twin._predicate = value 

    @property
    def path(self):
        """rdflib.paths.SequencePath: Chemin représenté par la clé.
        
        Notes
        -----
        Cette propriété est en lecture seule. Si la clé appartient à un
        groupe de valeurs ou de traduction, le chemin est celui du groupe
        parent. Sinon, il est calculé dynamiquement à partir du chemin du
        parent et de la valeur de :py:attr:`ObjectKey.predicate`.
        
        """
        parent_path = self.parent.path
        if isinstance(self.parent, GroupOfValuesKey):
            return parent_path
        if not parent_path:
            return self.predicate
        return parent_path / self.predicate

    @property
    def label(self):
        """str: Etiquette de la clé.
        
        Notes
        -----
        Si la clé appartient à un groupe de valeurs ou de traduction,
        cette propriété vaudra ``None``, car l'étiquette est portée
        par le groupe. Tenter d'en modifier la valeur n'aura silencieusement
        aucun effet.
        
        Hors d'un groupe de valeurs, si aucune étiquette n'est mémorisée,
        la propriété renvoie ``'???'``` plutôt que ``None``.
        
        Si la clé a une jumelle dont l'étiquette est différente
        de la valeur fournie, c'est celle de la jumelle de référence
        qui prévaudra. Autrement dit, pour changer l'étiquette d'un
        couple de jumelles, il faut cibler la jumelle de référence,
        sans quoi l'opération n'aura pas d'effet.
        
        Il est permis de fournir des valeurs de type ``rdflib.term.Literal``,
        qui seront alors automatiquement converties.
        
        """
        if not isinstance(self.parent, GroupOfValuesKey):
            return self._label or '???'
    
    @label.setter
    def label(self, value):
        if not isinstance(self.parent, GroupOfValuesKey):
            if self.m_twin and not self.is_main_twin:
                value = self.m_twin.label
            value = str(value) if value else None
            self._label = value
            if self.m_twin and self.is_main_twin:
                self.m_twin._label = value
        else:
            self._label = None

    @property
    def description(self):
        """str: Descriptif de la métadonnée représentée par la clé.
        
        Notes
        -----
        Si la clé appartient à un groupe de valeurs ou de traduction,
        la propriété du groupe parent est renvoyée. Tenter d'en modifier
        la valeur n'aura silencieusement aucun effet.
        
        Lorsqu'il n'y a ni étiquette, ni descriptif mémorisé, cette
        propriété renvoie le chemin (:py:attr:`ObjectKey.path`).
        
        Si la clé a une jumelle dont le descriptif est différent
        de la valeur fournie, c'est celui de la jumelle de référence
        qui prévaudra. Autrement dit, pour changer le descriptif d'un
        couple de jumelles, il faut cibler la jumelle de référence,
        sans quoi l'opération n'aura pas d'effet.
        
        Il est permis de fournir des valeurs de type ``rdflib.term.Literal``,
        qui seront alors automatiquement converties.
        
        """
        if isinstance(self.parent, GroupOfValuesKey):
            return self.parent.description
        if not self._label and not self._description:
            return self.path
        return self._description
    
    @description.setter
    def description(self, value):
        if not isinstance(self.parent, GroupOfValuesKey):
            if self.m_twin and not self.is_main_twin:
                value = self.m_twin.description
            value = str(value) if value else None
            self._description = value
            if self.m_twin and self.is_main_twin:
                self.m_twin._description = value
        else:
            self._description = None

    @property
    def order_idx(self):
        """tuple(int): Indice de classement de la clé parmi ses soeurs.
        
        Notes
        -----
        Si la clé appartient à un groupe de valeurs ou de traduction,
        modifier la valeur de cette propriété n'aura silencieusement aucun
        effet, car il n'y a pas de notion d'ordre dans ces groupes.
        :py:attr:`WidgetKey.order_idx` y vaut toujours ``None``.
        Dans le cas contraire, ``None`` est silencieusement remplacé par
        ``(9999,)``, de manière ce que les clés sans indice soient classées
        après les autres.
        
        Si la clé a une jumelle dont l'indice de classement est différent
        de la valeur fournie, c'est celui de la jumelle de référence
        qui prévaudra. Autrement dit, pour changer l'indice de classement
        d'un couple de jumelles, il faut cibler la jumelle de référence,
        sans quoi l'opération n'aura pas d'effet.
        
        Modifier cette propriété emporte la mise en cohérence de la propriété
        :py:attr:`WidgetKey.row` pour toutes les clés du groupe parent.
        
        """
        return self._order_idx

    @order_idx.setter
    def order_idx(self, value):
        if isinstance(self.parent, GroupOfValuesKey):
            self._order_idx = None
        else:
            if self.m_twin and not self.is_main_twin:
                value = self.m_twin.order_idx
            value = value or (9999,)
            self._order_idx = value
            if self.m_twin and self.is_main_twin:
                self.m_twin._order_idx = value
        if not self._is_unborn:
            self.parent.compute_rows()

    @property
    def m_twin(self):
        """ObjectKey: Clé jumelle.
        
        Deux clés jumelles sont une clé-valeur (classe :py:class:`ValueKey`)
        et une clé groupe de propriétés (classe :py:class:`GroupOfPropertiesKey`)
        représentant le même objet, la première sous forme d'IRI, la seconde sous
        la forme d'un ensemble de propriétés (définition "manuelle"). Les deux clés
        occupant le même emplacement dans la grille, l'une des deux doit toujours
        être masquée (:py:attr:`ObjectKey.is_hidden_m` valant ``True``).
        
        Les clés jumelles partagent certains attributs :
        :py:attr:`ObjectKey.predicate` (et par suite :py:attr:`ObjectKey.path`),
        :py:attr:`ObjectKey.label`, :py:attr:`ObjectKey.description`
        et :py:attr:`ObjectKey.order_idx` prennent toujours la même valeur pour les
        deux jumelles (mise à jour automatique).
        
        Raises
        ------
        ForbiddenOperation
            Si la clé cible est un fantôme, si la clé jumelle n'est pas du bon
            type (:py:class:`ValueKey` pour une clé :py:class:`GroupOfPropertiesKey`
            et inversement), ou si les deux clés n'ont pas le même parent.
        
        Notes
        -----
        Modifier cette propriété emporte la mise en cohérence des propriétés
        :py:attr:`ObjectKey.is_hidden_m`, :py:attr:`ObjectKey.is_main_twin`,
        :py:attr:`ObjectKey.predicate`, :py:attr:`ObjectKey.label`,
        :py:attr:`ObjectKey.description` et :py:attr:`ObjectKey.order_idx`
        de la clé et de sa jumelle, des propriétés :py:attr:`ObjectKey.rowspan`
        et :py:attr:`ObjectKey.independant_label` de la clé-valeur du couple,
        ainsi que de la propriété :py:attr:`WidgetKey.is_single_child` pour
        toutes les clés du groupe parent.
        
        """
        return self._m_twin
    
    @m_twin.setter
    def m_twin(self, value):
        if not value is None:
            if not value:
                # fait aussi tourner court toute tentative de désigner un
                # fantôme comme jumeau.
                return
            if not self :
                raise ForbiddenOperation('Un fantôme ne peut avoir ' \
                    'de clé jumelle.', self)
            d = {ValueKey: GroupOfPropertiesKey, GroupOfPropertiesKey: ValueKey}
            if not isinstance(value, d[type(self)]):
                raise ForbiddenOperation('La clé jumelle devrait' \
                    ' être de type {}.'.format(d[type(self)]), self)
            if self.parent != value.parent:
                raise ForbiddenOperation('La clé et sa jumelle ' \
                    'devraient avoir la même clé parent.', self)
        elif self.m_twin and not self.is_main_twin:
            # cas de la suppression du jumeau, lorsque la clé n'était
            # pas la jumelle principale
            self.is_hidden_m = self.m_twin.is_hidden_m
        self._m_twin = value
        if value:
            value._m_twin = self
        if not self._is_unborn:
            # pour une clé dont le jumeau est défini a posteriori,
            # il faut s'assurer de la cohérence des attributs partagés
            self.is_hidden_m = self.is_hidden_m
            # NB: assure aussi la mise à jour de is_main_twin
            self.predicate = self.predicate
            self.rdfclass = self.rdfclass
            # emporte la mise en cohérence de ValueKey.datatype (None), et
            # par suite de ValueKey.is_long_text (False), ce qui garantit
            # que le rowspan de la clé-valeur vaut 1, comme celui du groupe.
            # on réexprime toutefois cette contrainte explicitement pour plus
            # de clarté
            if isinstance(self, ValueKey):
                self.rowspan = self.rowspan
                self.independant_label = self.independant_label
            elif value is not None:
                value.rowspan = value.rowspan
                value.independant_label = value.independant_label
            self.label = self.label
            self.description = self.description
            self.order_idx = self.order_idx
            self.parent.compute_single_children()
    
    @property
    def is_hidden_m(self):
        """bool: La clé appartient-elle à une branche masquée ?
        
        Cette propriété héréditaire vaut ``True`` pour la clé présentement
        masquée d'un couple de jumelles, ou toute clé descendant de celle-ci
        (branche masquée).
        
        Sauf à ce que les deux jumelles appartiennent à une branche
        masquée en amont, une et une seule clé du couple est toujours
        masquée (:py:attr:`ObjectKey.is_hidden_m` vaut ``True``). Cette
        cohérence est maintenue automatiquement.
        
        Toute tentative pour rendre visible une partie d'une branche
        restant masquée en amont sera silencieusement ignorée.
        
        Notes
        -----
        Réécriture de la propriété :py:attr:`WidgetKey.is_hidden_m`.
        
        Modifier cette propriété emporte la mise en cohérence de la
        propriété :py:attr:`ObjectKey.is_main_twin` de la clé et de sa
        jumelle.
        
        """
        return self._is_hidden_m 
    
    @is_hidden_m.setter
    def is_hidden_m(self, value):
        if not self or self.parent.is_hidden_m or not self.m_twin:
            if not self._is_unborn:
                self.is_main_twin = self.is_main_twin
            return
            # pas besoin de retoucher à la valeur définie à
            # l'initialisation ou héritée du parent
        value = value or False
        self._hide_m(value, rec=False)
        self.m_twin._hide_m(not value, rec=False)
        if not self._is_unborn:
            self.is_main_twin = not self.is_hidden_m

    @property
    def is_main_twin(self):
        """bool: La clé est-elle la jumelle référente du couple ?
        
        Toujours ``False`` si la clé n'a pas de jumelle.
        
        Notes
        -----
        Cette propriété n'est pas supposée être modifiée manuellement.
        Elle ne peut d'ailleurs l'être que lorsque les deux jumelles
        appartiennent à une branche masquée, sinon elle est déduite de
        :py:attr:`ObjectKey.is_hidden_m`.
        
        """
        return self._is_main_twin

    @is_main_twin.setter
    def is_main_twin(self, value):
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
    def attr_to_update(self):
        """list(str): Liste des attributs et propriétés pouvant être redéfinis post initialisation.
        
        Notes
        -----
        Réécriture de la propriété :py:attr:`WidgetKey.attr_to_update`.
        
        """
        return ['order_idx', 'predicate', 'label', 'description',
            'is_hidden_m', 'is_read_only']

    @property
    def attr_to_copy(self):
        """dict: Attributs de la classe à prendre en compte pour la copie des clés.
        
        Cette propriété est un dictionnaire dont les clés sont les
        noms des attributs contenant les informations nécessaires pour
        dupliquer la clé, et les valeurs sont des booléens qui indiquent
        si l'attribut est à prendre en compte lorsqu'il s'agit de
        créer une copie vide de la clé.
        
        Certains attributs sont volontairement exclus de cette liste, car
        ils requièrent un traitement spécifique.
        
        See Also
        --------
        WidgetKey.copy
        
        Notes
        -----
        Réécriture de la propriété :py:attr:`WidgetKey.attr_to_copy`.
        
        """
        return { 'order_idx': True, 'parent': True, 'predicate': True,
            'label': True, 'description': True, 'is_read_only': True }

    def kill(self, preserve_twin=False):
        """Efface une clé de la mémoire de son parent.
        
        Parameters
        ----------
        preserve_twin : bool
            ``True`` si la jumelle doit être conservée (généralement
            non souhaitable, sauf dans le cas très spécifique du
            nettoyage des groupes de propriétés vides).
        
        Notes
        -----
        Complète la méthode :py:meth:`WidgetKey.kill` en effaçant aussi
        la clé jumelle, s'il y en a une.
        
        """
        super().kill()
        if self.m_twin:
            if not preserve_twin:
                self.parent.children.remove(self.m_twin)
                WidgetKey.actionsbook.drop.append(self.m_twin)
                if isinstance(self.m_twin, GroupKey):
                    self.m_twin._notify_dead_children()
            else:
                # on déréfence toujours la jumelle sur
                # la clé qui a vocation à être conservée,
                # pour lui rendre sa visibilité si besoin
                self.m_twin.m_twin = None

    def drop(self, append_book=False):
        """Supprime une clé d'un groupe de valeur ou de traduction.
        
        Utiliser cette méthode sur une clé sans bouton moins n'a pas d'effet,
        et le carnet d'actions renvoyé est vide.
        
        Parameters
        ----------
        append_book : bool, default False
            Si ``True``, le carnet d'action n'est pas réinitialisé
            avant exécution, mais complété avec les nouvelles
            opérations réalisées.
        
        Returns
        -------
        plume.rdf.actionsbook.ActionsBook
            Le carnet d'actions qui permettra de matérialiser
            la suppresssion de la clé.
        
        """
        if not self.has_minus_button:
            return ActionsBook()
        if not append_book:
            WidgetKey.clear_actionsbook()
        self.kill()
        return WidgetKey.unload_actionsbook(preserve_book=append_book)

    def switch_twin(self, value_source=None, append_book=False):
        """Intervertit la visibilité d'un couple de jumelles.
        
        Utiliser cette méthode sur une clé non visible n'a pas d'effet,
        et le carnet d'actions renvoyé est vide : cette méthode est
        supposée être appliquée sur la jumelle visible du couple.
        
        Parameters
        ----------
        value_source : rdflib.term.URIRef, optional
            Si la clé qui redevient visible est la clé-valeur, la
            source à utiliser pour celle-ci. Si non fourni, la
            source antérieure est conservée.
        append_book : bool, default False
            Si ``True``, le carnet d'action n'est pas réinitialisé
            avant exécution, mais complété avec les nouvelles
            opérations réalisées.
        
        Returns
        -------
        plume.rdf.actionsbook.ActionsBook
            Le carnet d'actions qui permettra de répercuter
            le changement de source sur les widgets.
        
        """
        if self.is_hidden:
            return ActionsBook()
        if not append_book:
            WidgetKey.clear_actionsbook()
        self.is_hidden_m = True
        if isinstance(self.m_twin, ValueKey) and value_source:
            self.m_twin.value_source = value_source
        return WidgetKey.unload_actionsbook(preserve_book=append_book)

class GroupKey(WidgetKey):
    """Clé de groupe.
    
    Une clé de groupe est une clé de dictionnaire de widgets qui pourra être
    désignée comme parent d'autres clés, dites "clés filles".
    
    Outre ses attributs propres listés ci-après, :py:class:`GroupKey` hérite
    de tous les attributs et propriétés de la classe :py:class:`WidgetKey`.
    
    Parameters
    ----------
    parent : GroupKey
        La clé parente. Ne peut pas être ``None``, sauf dans le cas d'un objet
        de la classe :py:class:`RootKey` (groupe racine).
    is_ghost : bool, default False
        ``True`` si la clé ne doit pas être matérialisée. À noter que quelle
        que soit la valeur fournie à l'initialisation, une fille de clé
        fantôme est toujours un fantôme.
    order_idx : tuple of int, default (999,)
        Indice(s) permettant le classement de la clé parmi ses soeurs dans
        un groupe de propriétés. Les clés de plus petits indices seront les
        premières. Cet argument sera ignoré si le groupe parent est un
        groupe de valeurs (:py:class:`GroupOfvaluesKey`).
    
    Attributes
    ----------
    children : list of WidgetKey
        Liste des clés filles.
    
    Warnings
    --------
    Cette classe ne doit pas être utilisée directement pour créer de
    nouvelles clés. On préfèrera toujours les classes filles qui héritent
    de ses méthodes et attributs :
    
    * :py:class:`RootKey` pour la clé racine d'un arbre de clés.
    * :py:class:`GroupOfPropertiesKey` pour les groupes de propriétés.
    * :py:class:`GroupOfValuesKey` pour les groupes de valeurs.
    * :py:class:`TranslationGroupKey` pour les groupes de traduction.
    * :py:class:`TabKey` pour les onglets.
    
    """
    def __new__(cls, **kwargs):
        if cls.__name__ == 'GroupKey':
            raise ForbiddenOperation('La classe `GroupKey` ne ' \
                'devrait pas être directement utilisée pour créer ' \
                'de nouvelles clés.')
        return super().__new__(cls, **kwargs)
    
    def _base_attributes(self, **kwargs):
        self.children = ChildrenList()
    
    def _hide_m(self, value, rec=False):
        super()._hide_m(value, rec=rec)
        for child in self.real_children():
            child._hide_m(value, rec=True)
        if value and not self._is_unborn:
            self.compute_rows()
    
    @property
    def columnspan(self):
        """int: Nombre de colonnes de la grille occupées par le widget principal de la clé.
        
        Vaut toujours ``0`` pour une clé fantôme.
        
        Notes
        -----
        Réécriture de la propriété :py:attr:`WidgetKey.columnspan`.
        
        """
        return 0 if not self else 2
    
    def is_empty(self, **kwargs):
        """Le groupe est-il vide ?
        
        Un groupe est considéré comme vide quand il ne contient
        que des groupes vides ou des clés-valeurs sans valeur.
        Les fantômes sont pris en compte.
        
        Notes
        -----
        Cette méthode admet des paramètres arbitraires pour
        qu'elle puisse être appelée dans les mêmes conditions
        que les méthodes de même nom définies sur d'autres
        classes de clés. En pratique, elle n'en utilise aucun.
        
        See Also
        --------
        GroupOfValuesKey.is_empty
        
        """
        for child in self.children:
            if not child.is_empty():
                return False
        return True
    
    @property
    def has_real_children(self):
        """bool: Y a-t-il au moins un enfant dans ce groupe qui ne soit pas un fantôme ?
        
        """
        for child in self.children:
            if child:
                return True
        return False
    
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
        
        Cette méthode n'a pas d'effet dans un groupe fantôme, ou si
        l'attribut de classe :py:attr:`WidgetKey.no_computation` vaut
        ``True``.
        
        Returns
        -------
        int
            L'indice de la prochaine ligne disponible.
        
        Notes
        -----
        Hormis dans les groupes de valeurs, où elle respecte
        l'ordre d'initialisation des clés filles, la méthode trie
        la liste :py:attr:`GroupKey.children` en fonction de
        l'attribut :py:attr:`WidgetKey.order_idx`. Les indices
        des clés sont définis par leur ordre dans la liste et 
        les valeurs de :py:attr:`WidgetKey.rowspan` des clés
        qui les précèdent.
        
        """
        if not self or WidgetKey.no_computation:
            return
        n = 0
        if not isinstance(self, GroupOfValuesKey):
            # dans les groupes de valeurs, le premier entré
            # reste toujours le premier ; sinon, on trie en
            # fonction de `order_idx`
            self.children.sort(key=lambda x: x.order_idx)
        for child in self.real_children():
            if isinstance(child, ObjectKey) and \
                child.m_twin and not child.is_main_twin:
                continue
            if child.independant_label:
                n += 1
            if child.row != n:
                child._row = n
                WidgetKey.actionsbook.move.append(child)
            if isinstance(child, ObjectKey) and child.m_twin \
                and child.is_main_twin and child.m_twin.row != n:
                child.m_twin._row = n
                WidgetKey.actionsbook.move.append(child.m_twin)
            n += child.rowspan 
        return n

    def _search_from_path(self, path, allow_ghosts=False):
        for child in (self.children if allow_ghosts else self.real_children()):
            if path == child.path:
                if isinstance(child, ObjectKey) and \
                    child.m_twin and not child.is_main_twin:
                    continue
                return child
            elif (not child.path or path.n3().startswith(child.path.n3())) \
                and isinstance(child, GroupKey):
                # à cette heure, rdflib ne propose pas de méthode
                # pour casser proprement un chemin, on prend donc
                # le parti de comparer des chaînes de caractères
                # "not child.path" est là pour les onglets rattachés
                # à la racine, dont le chemin est vide
                target = child._search_from_path(path, allow_ghosts=allow_ghosts)
                if target is not None:
                    return target

    def _search_from_rdfclass(self, rdfclass, matchlist):
        for child in self.real_children():
            if isinstance(child, GroupOfPropertiesKey) and \
                rdfclass == child.rdfclass:
                matchlist.append(child)
            if isinstance(child, GroupKey):
                # moins efficace que search_from_path,
                # parce qu'on est obligé de parcourir toutes
                # les branches
                child._search_from_rdfclass(rdfclass, matchlist)

    def _search_from_uuid(self, uuid):
        for child in self.children:
            if str(child.uuid) == str(uuid):
                return child
            elif isinstance(child, GroupKey):
                return child._search_from_uuid(uuid)

    def _clean(self):
        if isinstance(self, GroupOfPropertiesKey) and self.m_twin \
            and not self.is_main_twin and not self.has_source_button:
            self.kill(preserve_twin=True)
            return
        for child in self.children.copy():
            if isinstance(child, GroupKey):
                child._clean()
            elif isinstance(child, ValueKey) and child.m_twin \
                and not child.is_main_twin and not child.has_source_button:
                # cas d'un jumeau qui n'avait pas lieu
                # d'être, puisqu'il est masqué et qu'il n'y
                # a pas de bouton pour l'afficher
                child.kill(preserve_twin=True)
        if not self.children:
            if isinstance(self, GroupOfPropertiesKey):
                self.kill(preserve_twin=True)
            else:
                self.kill()
        elif self and not self.has_real_children:
            self.is_ghost = True

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
            dans un groupe de valeurs ou de traduction) - ``True`` - ou
            souhaite-t-on dupliquer une branche de l'arbre de clés
            en préservant son contenu - ``False`` ?
        
        Returns
        -------
        GroupKey
        
        Raises
        ------
        ForbiddenOperation
            Lorsque la méthode est explicitement appliquée à une clé
            fantôme. Il est possible de copier des branches contenant
            des fantômes, ceux-ci ne seront simplement pas copiés.
        
        Notes
        -----
        Redéfinit la méthode :py:meth:`WidgetKey.copy` en gérant la
        copie des filles de la clé.
        
        """
        key = super().copy(parent=parent, empty=empty)
        for child in self.real_children():
            child.copy(parent=key, empty=empty)
            if empty and isinstance(self, GroupOfValuesKey):
                # dans un groupe de valeurs ou de traduction,
                # seule la première fille est copiée
                break
        return key

    def search_tab(self, label=None):
        """Cherche parmi les filles du groupe et renvoie l'onglet d'étiquette donnée.
        
        Parameters
        ----------
        label : str or rdflib.term.Literal, optional
            L'étiquette de l'onglet recherché. Si `label` n'est
            pas spécifié, le premier onglet du groupe est renvoyé (sous
            réserve qu'il y en ait un).
        
        Returns
        -------
        TabKey
        
        Notes
        -----
        Les clés fantômes sont exclues de la recherche. Si plusieurs
        onglets s'avérait porter le même nom, l'un est renvoyé
        arbitrairement.
        
        """
        for child in self.real_children():
            if isinstance(child, TabKey) and (not label or \
                str(label) == child.label):
                return child
        if label:
            raise IntegrityBreach(f'Aucun onglet nommé "{label}".')
        else:
            raise IntegrityBreach('Aucun onglet.')

    def _build_metagraph(self, metagraph):
        b = False
        for child in self.children:
            b = child._build_metagraph(metagraph) or b
        return b

    def _tree_keys(self):
        if self:
            yield from super()._tree_keys()
            for child in self.children:
                yield from child._tree_keys()
    
    def _notify_dead_children(self):
        for child in self.children:
            WidgetKey.actionsbook.drop.append(child)
            if isinstance(child, GroupKey):
                child._notify_dead_children()

class TabKey(GroupKey):
    """Onglet.
    
    Les onglets sont des clés de dictionnaires de widgets qui doublent
    leur groupe de propriétés ou groupe racine parent sans porter
    aucune information sur la structure du graphe RDF.
    
    :py:class:`TabKey` hérite des attributs et méthodes de la classe
    :py:class:`GroupKey`.
    
    Parameters
    ----------
    parent : GroupKey
        La clé parente. Ne peut pas être ``None``.
    is_ghost : bool, default False
        ``True`` si la clé ne doit pas être matérialisée. À noter que quelle
        que soit la valeur fournie à l'initialisation, une fille de clé
        fantôme est toujours un fantôme.
    order_idx : tuple of int, default (999,)
        Indice(s) permettant le classement de la clé parmi ses soeurs dans
        un groupe de propriétés. Les clés de plus petits indices seront les
        premières.
    label : str or rdflib.term.Literal
        Etiquette de l'onglet.
    
    Notes
    -----
    Il n'est pas permis de créer un onglet dans un groupe contenant autre
    chose que des onglets ni, réciproqument, une clé qui ne serait pas un
    onglet dans un groupe contenant un onglet. C'est le setter de la
    propriété :py:attr:`WidgetKey.parent` qui veille au respect de cette
    condition.
    
    """
    
    def _base_attributes(self, **kwargs):
        super()._base_attributes(**kwargs)
        self._label = None
        
    def _computed_attributes(self, **kwargs):
        super()._computed_attributes(**kwargs)
        self.label = kwargs.get('label')
    
    def _validate_parent(self, parent):
        return isinstance(parent, GroupOfPropertiesKey) \
            or isinstance(parent, RootKey)
    
    @property
    def key_object(self):
        """str: Transcription littérale du type de clé.
        
        """
        return 'tab'

    @property
    def node(self):
        """rdflib.term.URIRef or rdflib.term.BNode: Noeud sujet des filles de l'onglet.
        
        Identique à celui du groupe parent.
        
        """
        return self.parent.node

    @property
    def path(self):
        """rdflib.paths.SequencePath: Chemin représenté par la clé.
        
        Notes
        -----
        Cette propriété est en lecture seule. Le chemin d'un
        onglet est identique à celui du groupe parent.
        
        """
        if isinstance(self.parent, RootKey):
            return None
        return self.parent.path

    @property
    def label(self):
        """str: Etiquette de la clé.
        
        Notes
        -----
        Si aucune étiquette n'est mémorisée, la propriété renvoie ``'???'```
        plutôt que ``None``.
        
        Il est permis de fournir des valeurs de type ``rdflib.term.Literal``,
        qui seront alors automatiquement converties.
        
        """
        return self._label or '???'
    
    @label.setter
    def label(self, value):
        self._label = str(value) if value else None

    @property
    def is_ghost(self):
        """bool: La clé est-elle une clé fantôme non matérialisée ?
        
        Notes
        -----
        Réécriture de la propriété :py:attr:`WidgetKey.is_ghost`.
        
        Cette propriété n'est modifiable post initialisation que 
        pour transformer en fantôme une clé qui ne l'était pas,
        si les conditions suivantes sont réunies :
        * le groupe a au moins un enfant ;
        * tous les enfants du groupe sont des fantômes.
        
        :py:attr:`is_ghost` définit la valeur booléenne de la clé :
        ``bool(widgetkey)`` vaut ``False`` si ``widgetkey`` est une
        clé fantôme.
        
        """
        return self._is_ghost

    @is_ghost.setter
    def is_ghost(self, value):
        if value and self and self.children \
            and not self.has_real_children:
            self._is_ghost = True
            if not WidgetKey.no_computation:
                # NB: on n'exécute pas compute_single_children,
                # car le parent ne peut pas être un groupe
                # de valeurs.
                self.parent.compute_rows()
            WidgetKey.actionsbook.drop.append(self) 

    @property
    def placement(self):
        return

    @property
    def attr_to_update(self):
        """list(str): Liste des attributs et propriétés pouvant être redéfinis post initialisation.
        
        Notes
        -----
        Réécriture de la propriété :py:attr:`WidgetKey.attr_to_update`.
        
        """
        return ['order_idx', 'label']

class GroupOfPropertiesKey(GroupKey, ObjectKey):
    """Groupe de propriétés.
    
    Un groupe de propriétés est une clé de dictionnaire de widgets qui 
    représente un couple prédicat / noeud anonyme. Ses filles représentent
    les triplets dont le noeud anonyme est le sujet.
    
    Outre ses attributs propres listés ci-après, la classe
    :py:class:`GroupOfPropertiesKey` hérite de tous les attributs et
    méthodes des classes :py:class:`GroupKey` et :py:class:`ObjectKey`.
    
    Parameters
    ----------
    parent : GroupKey
        La clé parente. Ne peut pas être ``None``.
    is_ghost : bool, default False
        ``True`` si la clé ne doit pas être matérialisée. À noter que quelle
        que soit la valeur fournie à l'initialisation, une fille de clé
        fantôme est toujours un fantôme.
    order_idx : tuple of int, default (999,)
        Indice(s) permettant le classement de la clé parmi ses soeurs dans
        un groupe de propriétés. Les clés de plus petits indices seront les
        premières. Cet argument sera ignoré si le groupe parent est un
        groupe de valeurs (:py:class:`GroupOfvaluesKey`).
    predicate : rdflib.term.URIRef
        Prédicat représenté par la clé. Si la clé appartient à un groupe
        de valeurs, c'est lui qui porte cette information. Sinon, elle
        est obligatoire. Pour des clés jumelles, le prédicat déclaré
        sur la jumelle de référence prévaut, sauf s'il vaut ``None``.
    label : str or rdflib.term.Literal, optional
        Etiquette de la clé (libellé de la catégorie de métadonnée
        représentée par la clé). Cet argument est ignoré si la clé
        appartient à un groupe de valeurs. Pour des clés jumelles,
        l'étiquette déclarée sur la jumelle de référence prévaut, sauf si
        elle vaut ``None``.
    description : str or rdflib.term.Literal, optional
        Définition de la catégorie de métadonnée représentée par la clé.
        Cet argument est ignoré si la clé appartient à un groupe de valeurs.
        Pour des clés jumelles, le descriptif déclaré sur la jumelle de
        référence prévaut, sauf s'il vaut ``None``.
    m_twin : ValueKey, optional
        Clé jumelle, le cas échéant. Un couple de jumelle ne se déclare
        qu'une fois, sur la seconde clé créée.
    is_hidden_m : bool, default False
        La clé est-elle la clé masquée du couple de jumelles ? Ce paramètre
        n'est pris en compte que pour une clé qui a une jumelle.
    node : BNode, optional
        Le noeud anonyme objet du prédicat, qui est également le sujet
        des triplets des enfants du groupe. Si non fourni, un nouveau
        noeud anonyme est généré.
    rdfclass : rdflib.term.URIRef
        La classe RDF du noeud. Si la clé appartient à un groupe de valeurs,
        c'est lui qui porte cette information. Sinon, elle est obligatoire.
    
    """
    
    def _base_attributes(self, **kwargs):
        GroupKey._base_attributes(self, **kwargs)
        ObjectKey._base_attributes(self, **kwargs)
        self._rdfclass = None
        self._node = None
    
    def _computed_attributes(self, **kwargs):
        ObjectKey._computed_attributes(self, **kwargs)
        self.rdfclass = kwargs.get('rdfclass')
        self.node = kwargs.get('node')
 
    def _validate_parent(self, parent):
        if isinstance(parent, GroupOfValuesKey) and not parent.rdfclass:
            raise IntegrityBreach("L'attribut `rdfclass` de " \
                "la clé parente n'est pas renseigné.", self)
        return isinstance(parent, GroupKey) and \
            not isinstance(parent, TranslationGroupKey)
 
    @property
    def key_object(self):
        """str: Transcription littérale du type de clé.
        
        """
        return 'group of properties'
 
    @property
    def node(self):
        """rdflib.term.BNode: Le noeud anonyme objet du prédicat et sujet des filles du groupe.
        
        Warnings
        --------
        Aucun contrôle n'est réalisé pour vérifier que le nouveau
        noeud anonyme n'est pas déjà utilisé par une autre clé. En
        cas de doute sur l'unicité des valeurs disponibles, il est
        préférable de ne pas en donner, un nouveau noeud anonyme est
        alors automatiquement généré (idem si la valeur fournie
        n'était pas véritablement un noeud anonyme).
        
        """
        return self._node
 
    @node.setter
    def node(self, value):
        if value and isinstance(value, BNode):
            self._node = value
        else:
            self._node = BNode()
 
    @property
    def rdfclass(self):
        """rdflib.term.URIRef: La classe RDF du noeud.
        
        Raises
        ------
        MissingParameter
            Pour toute tentative de mettre à ``None`` la valeur de
            cette propriété obligatoire.
        
        Notes
        -----
        Si la clé appartient à un groupe de valeurs ou de traduction,
        la propriété du groupe parent est renvoyée. Tenter d'en modifier
        la valeur n'aura silencieusement aucun effet.

        Si la clé a une jumelle dont la classe est différente
        de la valeur fournie, c'est celle de la jumelle de référence
        qui prévaudra, sauf si elle vaut ``None``. Autrement dit, pour
        changer la classe d'un couple de jumelles, il faut cibler
        la jumelle de référence, sans quoi l'opération n'aura pas d'effet.

        """
        if isinstance(self.parent, GroupOfValuesKey):
            return self.parent.rdfclass
        return self._rdfclass

    @rdfclass.setter
    def rdfclass(self, value):
        if not isinstance(self.parent, GroupOfValuesKey):
            if self.m_twin and (not self.is_main_twin or not value):
                value = self.m_twin.rdfclass
            if not value:
                raise MissingParameter('rdfclass', self)
            self._rdfclass = value
            if self.m_twin and value != self.m_twin.rdfclass \
                and self.is_main_twin:
                self.m_twin._rdfclass = value 

    @property
    def sources(self):
        """list(rdflib.term.URIRef): Le cas échéant, la liste des sources de la clé-valeur jumelle.

        Notes
        -----
        Cette propriété n'est pas modifiable. Elle vaut toujours ``None``
        pour une clé sans jumelle.
        
        """
        if self.m_twin:
            return self.m_twin.sources

    @property
    def has_source_button(self):
        """bool: Un bouton annexe de sélection de la source doit-il être créé pour la clé ?
        
        Notes
        -----
        Réécriture de la propriété :py:attr:`WidgetKey.has_source_button`.
        
        """
        return bool(self) and WidgetKey.with_source_buttons \
            and bool(self.m_twin) and not self.is_read_only

    @property
    def is_ghost(self):
        """bool: La clé est-elle une clé fantôme non matérialisée ?
        
        Notes
        -----
        Réécriture de la propriété :py:attr:`WidgetKey.is_ghost`.
        
        Cette propriété n'est modifiable post initialisation que 
        pour transformer en fantôme une clé qui ne l'était pas,
        si les conditions suivantes sont réunies :
        * le groupe de propriétés a au moins un enfant ;
        * tous les enfants du groupe sont des fantômes ;
        * la clé n'a pas de jumelle ou est la jumelle principale.
          Dans ce cas, la clé-valeur jumelle sera supprimée.
        
        :py:attr:`is_ghost` définit la valeur booléenne de la clé :
        ``bool(widgetkey)`` vaut ``False`` si ``widgetkey`` est une
        clé fantôme.
        
        """
        return self._is_ghost

    @is_ghost.setter
    def is_ghost(self, value):
        if value and self and (not self.m_twin or self.is_main_twin) \
            and self.children and not self.has_real_children:
            if self.is_main_twin:
                # NB: en pratique, cette condition sera toujours remplie
                # à l'initialisation du dictionnaire de widgets, car c'est
                # la jumelle principale qui contient les données du graphe,
                # et qui dit fantôme dit données à préserver
                self.m_twin.kill(preserve_twin=True)
            self._is_ghost = True
            if not WidgetKey.no_computation:
                self.parent.compute_rows()
                self.parent.compute_single_children()
            WidgetKey.actionsbook.drop.append(self) 

    def _hide_m(self, value, rec=False):
        if rec and value and self.m_twin and not self.is_main_twin:
            return
        super()._hide_m(value, rec=rec)

    @property
    def attr_to_update(self):
        """list(str) : Liste des attributs et propriétés pouvant être redéfinis post initialisation.
        
        Notes
        -----
        Réécriture de la propriété :py:attr:`WidgetKey.attr_to_update`.
        
        """
        return ['order_idx', 'predicate', 'label', 'description', 'is_hidden_m',
            'node', 'rdfclass', 'is_read_only']

    @property
    def attr_to_copy(self):
        """dict: Attributs de la classe à prendre en compte pour la copie des clés.
        
        Cette propriété est un dictionnaire dont les clés sont les
        noms des attributs contenant les informations nécessaires pour
        dupliquer la clé, et les valeurs sont des booléens qui indiquent
        si l'attribut est à prendre en compte lorsqu'il s'agit de
        créer une copie vide de la clé.
        
        Certains attributs sont volontairement exclus de cette liste, car
        ils requièrent un traitement spécifique.
        
        See Also
        --------
        WidgetKey.copy, GroupKey.copy
        
        Notes
        -----
        Réécriture de la propriété :py:attr:`WidgetKey.attr_to_copy`.
        
        """
        return { 'order_idx': True, 'parent': True, 'predicate': True,
            'label': True, 'description': True, 'rdfclass': True,
            'is_read_only': True }

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
            dans un groupe de valeurs ou de traduction) - ``True`` - ou
            souhaite-t-on dupliquer une branche de l'arbre de clés
            en préservant son contenu - ``False`` ?
        
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

    def paste_from_rdfclass(self, widgetkey):
        """Remplace la branche par une branche de même type.
        
        Cette méthode n'a pas d'effet si elle est appliquée à
        une clé fantôme ou masquée.
        
        Parameters
        ----------
        widgetkey : GroupOfPropertiesKey
            La clé mère de la branche à copier.
        
        Returns
        -------
        plume.rdf.actionsbook.ActionsBook
            Le carnet d'actions qui permettra de matérialiser les
            opérations réalisées.
        
        Raises
        ------
        ForbiddenOperation
            Si la clé à copier est un fantôme, est masquée,
            n'est pas un groupe de propriétés, ou si sa classe
            RDF n'est pas celle de `self`.
        
        """
        if self.is_hidden:
            return ActionsBook()
        if widgetkey.is_hidden:
            raise ForbiddenOperation("Il n'est pas permis de " \
                'copier/coller une branche fantôme ou masquée.', self)
        if not isinstance(widgetkey, GroupOfPropertiesKey):
            raise ForbiddenOperation('Seul un groupe de ' \
                'propriétés peut être copié avec cette méthode.', self)
        if not self.rdfclass == widgetkey.rdfclass:
            raise ForbiddenOperation('`rdfclass` doit être ' \
                'identique pour les deux clés.', self)
        WidgetKey.clear_actionsbook()
        self.kill()
        newkey = widgetkey.copy(parent=self.parent, empty=False)
        newkey.update(predicate=self.predicate, label=self.label,
            description=self.description, order_idx=self.order_idx)
            # les informations relatives au prédicat du groupe
            # sont conservées
        return WidgetKey.unload_actionsbook()

    def kill(self, **kwargs):
        """Efface une clé de la mémoire de son parent.
        
        Notes
        -----
        Cette méthode réoriente simplement la commande vers la méthode
        :py:meth:`ObjectKey.kill` de la classe :py:class:`ObjectKey`
        (sinon c'est :py:meth:`WidgetKey.kill` qui serait utilisée).
        
        """
        ObjectKey.kill(self, **kwargs)

    def _build_metagraph(self, metagraph):
        if self.is_hidden_m:
            return False
        b = super()._build_metagraph(metagraph)
        if b:
            metagraph.add((self.parent.node, self.predicate, self.node))
            metagraph.add((self.node, RDF.type, self.rdfclass))
            # il n'est pas très intuitif d'ajouter le parent au
            # graphe après ses enfants, mais ça ne rend pas le graphe
            # invalide et de cette façon on n'intègre pas de groupes de
            # propriétés vides
        return b

class GroupOfValuesKey(GroupKey):
    """Groupe de valeurs.
    
    Un groupe de valeurs est une clé de groupe dont les filles,
    qui peuvent être des :py:class:`GroupOfPropertiesKey` ou des
    :py:class:`ValueKey`, ont le même prédicat.
    
    Outre ses attributs spécifiques listés ci-après, la classe
    :py:class:`GroupOfValuesKey` hérite de tous les attributs
    de la classe :py:class:`GroupKey`.
    
    Parameters
    ----------
    parent : GroupKey
        La clé parente. Ne peut pas être ``None``.
    is_ghost : bool, default False
        ``True`` si la clé ne doit pas être matérialisée. À noter que quelle
        que soit la valeur fournie à l'initialisation, une fille de clé
        fantôme est toujours un fantôme.
    order_idx : tuple of int, default (999,)
        Indice(s) permettant le classement de la clé parmi ses soeurs dans
        un groupe de propriétés. Les clés de plus petits indices seront les
        premières.
    with_minus_buttons : bool, default True
        ``True`` si des boutons moins (non représentés par des clés) sont
        supposés être associés aux clés du groupe.
    predicate : rdflib.term.URIRef
        Le prédicat commun à toutes les clés du groupe.
    label : str or rdflib.term.Literal, optional
        Etiquette du groupe (libellé de la catégorie de métadonnée dont
        les filles du groupe sont les valeurs).
    description : str or rdflib.term.Literal, optional
        Définition de la catégorie de métadonnée représentée par les clés
        du groupe.
    rdfclass : rdflib.term.URIRef, optional
        La classe RDF commune à toutes les valeurs du groupe. Cette
        information est obligatoire dès lors qu'une des filles du groupe est
        de type :py:class:`GroupOfPropertiesKey`.
    sources : list of rdflib.term.URIRef, optional
        Liste des sources de vocabulaire contrôlé pour les valeurs du groupe.
    transform : {None, 'email', 'phone'}, optional
        Le cas échéant, la nature de la transformation appliquée aux
        objets du groupe.
    datatype : rdflib.term.URIRef, default xsd:string
        Le cas échéant, le type des valeurs litérales du groupe. La valeur de
        ce paramètre est ignorée si :py:attr:`GroupOfValuesKey.rdfclass` est
        renseigné, sinon ``xsd:string`` fait office de valeur par défaut.
        Seuls les types suivants sont pris en charge, pour les autres
        ``xsd:string`` serait utilisé à la place : ``xsd:string``,
        ``xsd:integer``, ``xsd:decimal``, ``xsd:boolean``, ``xsd:date``,
        ``xsd:time``, ``xsd:dateTime``, ``xsd:duration``, ``gsp:wktLiteral``,
        ``rdf:langString``.
    placeholder : str or rdflib.term.Literal, optional
        Texte de substitution à utiliser pour les clés du groupe.
    input_mask : str or rdflib.term.Literal, optional
        Masque de saisie à utiliser pour les clés du groupe.
    is_mandatory : bool or rdflib.term.Literal, default False
        Ce groupe doit-il obligatoirement avoir une clé avec une valeur ?
    is_read_only : bool or rdflib.term.Literal, default False
        Les valeurs des clés du groupe sont-elles en lecture seule ?
    regex_validator : str, optional
        Expression rationnelle de validation à utiliser pour les clés du
        groupe.
    regex_validator_flags : str, optional
        Paramètres associés à l'expression rationnelle de validation des
        clés du groupe.
    geo_tools : list(str or rdflib.term.Literal)
        Liste de fonctionnalités d'aide à la saisie des géométries
        disponibles pour les clés du groupe. Seules les valeurs suivantes
        seront prises en compte : ``'show'``, ``'point'``, ``'linestring'``,
        ``'rectangle'``, ``'polygon'``, ``circle``, ``'bbox'``,
        ``'centroid'``. 
    compute : list(str or rdflib.term.Literal), optional
        Liste de modes de calcul disponibles pour le groupe. Seules les
        valeurs `'manual'`, `'auto'`, `'empty'` et `'new'` sont reconnues
        à ce stade.
    compute_params : dict, optional
        Paramètres à fournir à la méthode de calcul.
    
    Attributes
    ----------
    button : PlusButtonKey
        Référence la clé qui représente le bouton plus du groupe.
    
    """
    def _base_attributes(self, **kwargs):
        super()._base_attributes(**kwargs)
        self.button = None
        self._with_minus_buttons = None
        self._predicate = None
        self._label = None
        self._description = None
        self._rdfclass = None
        self._sources = None
        self._datatype = None
        self._transform = None
        self._placeholder = None
        self._input_mask = None
        self._is_mandatory = None
        self._is_read_only = None
        self._regex_validator = None
        self._regex_validator_flags = None
        self._geo_tools = None
        self._compute = None
        self._compute_params = None
        
    def _computed_attributes(self, **kwargs):
        super()._computed_attributes(**kwargs)
        self.with_minus_buttons = kwargs.get('with_minus_buttons', True)
        self.predicate = kwargs.get('predicate')
        self.label = kwargs.get('label')
        self.description = kwargs.get('description')
        self.rdfclass = kwargs.get('rdfclass')
        self.sources = kwargs.get('sources')
        self.datatype = kwargs.get('datatype')
        self.transform = kwargs.get('transform')
        self.placeholder = kwargs.get('placeholder')
        self.input_mask = kwargs.get('input_mask')
        self.is_mandatory = kwargs.get('is_mandatory')
        self.is_read_only = kwargs.get('is_read_only')
        self.regex_validator = kwargs.get('regex_validator')
        self.regex_validator_flags = kwargs.get('regex_validator_flags')
        self.geo_tools = kwargs.get('geo_tools')
        self.compute = kwargs.get('compute')
        self.compute_params = kwargs.get('compute_params')
    
    def _validate_parent(self, parent):
        return isinstance(parent, (GroupOfPropertiesKey, TabKey, RootKey))
    
    @property
    def key_object(self):
        """str: Transcription littérale du type de clé.
        
        """
        return 'group of values'
    
    @property
    def is_ghost(self):
        """bool: La clé est-elle une clé fantôme non matérialisée ?
        
        Notes
        -----
        Réécriture de la propriété :py:attr:`WidgetKey.is_ghost`.
        
        Cette propriété n'est modifiable post initialisation que 
        pour transformer en fantôme une clé qui ne l'était pas,
        si les conditions suivantes sont réunies :
        * la clé n'est pas un groupe de traduction ;
        * le groupe de valeurs a au moins un enfant ;
        * tous les enfants du groupe sont des fantômes ;
        * le groupe n'a pas de bouton plus.
        
        :py:attr:`is_ghost` définit la valeur booléenne de la clé :
        ``bool(widgetkey)`` vaut ``False`` si ``widgetkey`` est une
        clé fantôme.
        
        """
        return self._is_ghost

    @is_ghost.setter
    def is_ghost(self, value):
        if value and self and self.children and not self.has_real_children \
            and not self.button and not isinstance(self, TranslationGroupKey):
            self._is_ghost = True
            self.with_minus_buttons = self.with_minus_buttons
            if not WidgetKey.no_computation:
                self.parent.compute_rows()
                self.parent.compute_single_children()
            WidgetKey.actionsbook.drop.append(self) 
    
    @property
    def with_minus_buttons(self):
        """bool: Les filles du groupe sont-elles accompagnées de boutons moins ?
        
        Notes
        -----
        Cette propriété vaudra toujours ``False`` pour un groupe
        fantôme.
        
        """
        return self._with_minus_buttons
    
    @with_minus_buttons.setter
    def with_minus_buttons(self, value):
        if not self:
            self._with_minus_buttons = False
        self._with_minus_buttons = value
    
    @property
    def predicate(self):
        """rdflib.term.URIRef: Prédicat commun à toutes les clés du groupe.
        
        Raises
        ------
        MissingParameter
            Pour toute tentative de mettre à ``None`` la valeur de
            cette propriété obligatoire.
        
        """
        return self._predicate

    @predicate.setter
    def predicate(self, value):
        if not value:
            raise MissingParameter('predicate', self)
        self._predicate = value
    
    @property
    def node(self):
        """rdflib.term.URIRef or rdflib.term.BNode: Noeud sujet des filles du groupe.
        
        Identique à celui du groupe parent.
        
        """
        return self.parent.node
    
    @property
    def path(self):
        """rdflib.paths.SequencePath: Chemin commun à toutes les clés du groupe.
        
        Notes
        -----
        Cette propriété est en lecture seule. Elle est calculée dynamiquement
        à partir du chemin du parent et de la valeur de l'attribut
        :py:attr:`GroupOfValuesKey.predicate`.
        
        """
        parent_path = self.parent.path
        if not parent_path:
            return self.predicate
        return parent_path / self.predicate
    
    @property
    def label(self):
        """str: Etiquette du groupe.
        
        Il s'agit du libellé de la métadonnée représentée par les
        clés du groupe.

        Notes
        -----
        Si aucune étiquette n'est mémorisée, la propriété renvoie
        ``'???'``` plutôt que ``None``.
        
        Il est permis de fournir des valeurs de type ``rdflib.term.Literal``,
        qui seront alors automatiquement converties.
        
        """
        return self._label or '???'
    
    @label.setter
    def label(self, value):
        self._label = str(value) if value else None

    @property
    def description(self):
        """str: Descriptif de la métadonnée représentée par les clés du groupe.
        
        Notes
        -----
        Lorsqu'il n'y a ni étiquette, ni descriptif mémorisé, cette
        propriété renvoie le chemin - py:attr:`GroupOfValuesKey.path`.
        
        Il est permis de fournir des valeurs de type ``rdflib.term.Literal``,
        qui seront alors automatiquement converties.
        
        """
        if not self._label and not self._description:
            return self.path
        return self._description
    
    @description.setter
    def description(self, value):
        self._description = str(value) if value else None
    
    @property
    def rdfclass(self):
        """rdflib.term.URIRef: Classe RDF commune à toutes les valeurs du groupe.
        
        Raises
        ------
        MissingParameter
            Pour toute tentative de mettre à ``None`` la valeur de
            cette propriété alors qu'il y a au moins un groupe de
            propriétés (représentant un noeud anonyme, qui doit avoir
            une classe associée) parmi les enfants du groupe.
        
        Notes
        -----
        Modifier cette propriété emporte la mise en cohérence de
        :py:attr:`GroupOfValuesKey.datatype`.
        
        """
        return self._rdfclass
        
    @rdfclass.setter
    def rdfclass(self, value):
        if not value and any(isinstance(child, GroupOfPropertiesKey) \
            for child in self.children):
            raise MissingParameter('rdfclass', self)
        self._rdfclass = value
        if not self._is_unborn:
            self.datatype = self.datatype
    
    @property
    def sources(self):
        """list(rdflib.term.URIRef): Liste des sources de vocabulaire contrôlé commune à toutes les valeurs du groupe.
        
        Notes
        -----
        Modifier cette propriété emporte la mise en cohérence de
        la propriété :py:attr:`ValueKey.value_source` pour toutes
        les clés-valeurs du groupe. 
        
        """
        return self._sources
        
    @sources.setter
    def sources(self, value):
        if value != self.sources:
            self._sources = value
            if not self._is_unborn:
                for child in self.children:
                    if isinstance(child, ValueKey) and child.value_source:
                        child.value_source = child.value_source
                    if isinstance(child, ValueKey) or child.m_twin:
                        WidgetKey.actionsbook.sources.append(child)
                        if child.m_twin:
                            WidgetKey.actionsbook.sources.append(child.m_twin)
    
    @property
    def datatype(self):
        """rdflib.term.URIRef: Type de valeur commun aux valeurs du groupe, le cas échéant.
        
        Notes
        -----
        :py:attr:`GroupOfValuesKey.rdfclass` prévaut sur
        :py:attr:`GroupOfValuesKey.datatype` : si le premier est renseigné,
        c'est que la valeur est un IRI ou un noeud anonyme, et le second
        ne peut qu'être nul. Sinon, ``xsd:string`` est utilisé comme valeur
        par défaut.
        
        Seuls les types suivants sont pris en charge, pour les autres
        ``xsd:string`` serait utilisé à la place : ``xsd:string``,
        ``xsd:integer``, ``xsd:decimal``, ``xsd:boolean``, ``xsd:date``,
        ``xsd:time``, ``xsd:dateTime``, ``xsd:duration``, ``gsp:wktLiteral``,
        ``rdf:langString``.
        
        Modifier cette propriété emporte la mise en cohérence de
        :py:attr:`GroupOfValuesKey.geo_tools`, ainsi que des
        propriétés :py:attr:`ValueKey.value_language`,
        :py:attr:`ValueKey.is_long_text` et :py:attr:`ValueKey.value_unit`
        pour toutes les clés-valeurs du groupe.
        
        """
        return self._datatype
    
    @datatype.setter
    def datatype(self, value):
        tlist = [XSD.string, XSD.integer, XSD.decimal,
            XSD.boolean, XSD.date, XSD.time, XSD.dateTime,
            XSD.duration, GSP.wktLiteral, RDF.langString]
        if self.rdfclass:
            value = None
        elif not value in tlist:
            value = XSD.string
        self._datatype = value
        if not self._is_unborn:
            self.geo_tools = self._geo_tools
            # on réinitialise bien avec _geo_tools
            # et pas geo_tools, car le second tronque
            # la liste si la clé est en lecture seule
            for child in self.children:
                if isinstance(child, ValueKey):
                    child.value_language = child.value_language
                    child.is_long_text = child.is_long_text
                    child.value_unit = child.value_unit
    
    @property
    def transform(self):
        """{None, 'email', 'phone'}: Nature de la transformation appliquée aux clés-valeurs du groupe.
        
        Notes
        -----
        Il est permis de fournir des valeurs de type ``rdflib.term.Literal``,
        qui seront alors automatiquement converties. Toute tentative pour 
        définir une transformation autre que celles listées ci-avant sera
        silencieusement ignorée.
        
        Il n'est pas interdit de définir une valeur pour cette propriété
        lorsque le groupe de valeurs ne contient que des groupes de 
        propriétés, mais cela ne présente aucun intérêt.
        
        """
        return self._transform
    
    @transform.setter
    def transform(self, value):
        if isinstance(value, Literal):
            value = str(value)
        if not value in (None, 'email', 'phone'):
            return
        self._transform = value
    
    @property
    def placeholder(self):
        """str: Texte de substitution à utiliser pour les clés-valeurs du groupe.
        
        Notes
        -----
        Il est permis de fournir des valeurs de type ``rdflib.term.Literal``,
        qui seront alors automatiquement converties.
        
        Il n'est pas interdit de définir une valeur pour cette propriété
        lorsque le groupe de valeurs ne contient que des groupes de 
        propriétés, mais cela ne présente aucun intérêt.
        
        """
        return self._placeholder

    @placeholder.setter
    def placeholder(self, value):
        self._placeholder = str(value) if value else None
    
    @property
    def input_mask(self):
        """str: Masque de saisie à utiliser pour les clés-valeurs du groupe.
        
        Notes
        -----
        Il est permis de fournir des valeurs de type ``rdflib.term.Literal``,
        qui seront alors automatiquement converties.
        
        Il n'est pas interdit de définir une valeur pour cette propriété
        lorsque le groupe de valeurs ne contient que des groupes de 
        propriétés, mais cela ne présente aucun intérêt.
        
        """
        return self._input_mask

    @input_mask.setter
    def input_mask(self, value):
        self._input_mask = str(value) if value else None
    
    @property
    def is_mandatory(self):
        """bool: Au moins une clé-valeur du groupe devra-t-elle obligatoirement recevoir une valeur ?
        
        Notes
        -----
        Il est permis de fournir des valeurs de type ``rdflib.term.Literal``,
        qui seront alors automatiquement converties.
        
        Il n'est pas interdit de définir une valeur pour cette propriété
        lorsque le groupe de valeurs ne contient que des groupes de 
        propriétés, mais cela ne présente aucun intérêt.
        
        """
        return self._is_mandatory

    @is_mandatory.setter
    def is_mandatory(self, value):
        self._is_mandatory = bool(value)
    
    @property
    def is_read_only(self):
        """bool: Les valeurs des clés-valeurs du groupe sont-elles en lecture seule ?
        
        Notes
        -----
        Si la clé appartient à un groupe de propriétés, elle
        sera considérée comme étant en lecture seule si le groupe
        parent est en lecture seule ou si la clé elle-même est
        paramétrée comme telle.
        
        Un bouton plus dans un groupe de valeurs en lecture seule
        sera toujours masqué.
        
        Il est permis de fournir des valeurs de type ``rdflib.term.Literal``,
        qui seront alors automatiquement converties.
        
        """
        if isinstance(self.parent, GroupOfPropertiesKey):
            return self.parent.is_read_only or self._is_read_only
        return self._is_read_only

    @is_read_only.setter
    def is_read_only(self, value):
        self._is_read_only = bool(value)
    
    @property
    def regex_validator(self):
        """str: Expression rationnelle de validation à utiliser pour les clés-valeurs du groupe.
        
        Notes
        -----        
        Il est permis de fournir des valeurs de type ``rdflib.term.Literal``,
        qui seront alors automatiquement converties.
        
        Il n'est pas interdit de définir une valeur pour cette propriété
        lorsque le groupe de valeurs ne contient que des groupes de 
        propriétés, mais cela ne présente aucun intérêt.
        
        Modifier cette propriété emporte la mise en cohérence de la propriété
        :py:attr:`GroupOfValuesKey.regex_validator_flags`.
        
        """
        return self._regex_validator

    @regex_validator.setter
    def regex_validator(self, value):
        self._regex_validator = str(value) if value else None
        if not self._is_unborn:
            self.regex_validator_flags = self.regex_validator_flags
    
    @property
    def regex_validator_flags(self):
        """str: Paramètres associés à l'expression rationnelle de validation des clés-valeurs du groupe.
        
        Notes
        -----
        Toute tentative pour définir une valeur pour cette propriété alors
        que :py:attr:`GroupOfValuesKey.regex_validator` vaut ``None``
        sera silencieusement ignorée.
        
        Il est permis de fournir des valeurs de type ``rdflib.term.Literal``,
        qui seront alors automatiquement converties.
        
        Il n'est pas interdit de définir une valeur pour cette propriété
        lorsque le groupe de valeurs ne contient que des groupes de 
        propriétés, mais cela ne présente aucun intérêt.
        
        """
        return self._regex_validator_flags

    @regex_validator_flags.setter
    def regex_validator_flags(self, value):
        if not self.regex_validator:
            value = None
        self._regex_validator_flags = str(value) if value else None

    @property
    def geo_tools(self):
        """list(str): Fonctionnalités d'aide à la saisie des géométries disponibles pour les clés-valeurs du groupe.
        
        Notes
        -----
        Il n'est pas interdit de définir une valeur pour cette propriété
        lorsque le groupe de valeurs ne contient que des groupes de 
        propriétés, mais cela ne présente aucun intérêt.
        
        Cette propriété vaudra toujours ``None`` si 
        :py:attr:`GroupOfValues.datatype` n'est pas ``gsp:wktLiteral``.
        Pour le type ``gsp:wktLiteral``, il s'agira toujours d'une liste,
        quitte à ce qu'elle soit vide.
        
        Seules les valeurs suivantes sont acceptées (les autres seront
        silencieusement éliminées) : ``'show'``, ``'point'``,
        ``'linestring'``, ``'rectangle'``, ``'polygon'``, ``'circle'``,
        ``'bbox'``, ``'centroid'``.
        
        Lorsque la clé est en lecture seule, soit quand la propriété
        :py:attr:`GroupOfValuesKey.is_read_only` vaut  ``True``, la liste
        contiendra au plus `'show'`. C'est le getter de la propriété qui 
        génère à la volée une liste tronquée à partir de la liste mémorisée,
        afin de préserver toutes les valeurs pour le cas où
        :py:attr:`GroupOfValuesKey.is_read_only` reviendrait à ``False``.
        
        Il est permis de fournir en argument une liste de
        ``rdflib.term.Literal``, qui seront alors automatiquement convertis.
        
        """
        if self.is_read_only and self._geo_tools:
            return ['show'] if 'show' in self._geo_tools else []
        return self._geo_tools
    
    @geo_tools.setter
    def geo_tools(self, value):
        if not self.datatype == GSP.wktLiteral:
            value = None
        elif not value:
            value = []
        else:
            l = ['show', 'point', 'linestring', 'rectangle',
                'polygon', 'circle', 'bbox', 'centroid']
            value = [str(o) for o in value if str(o) in l]
        self._geo_tools = value

    @property
    def has_compute_button(self):
        """bool: Un bouton annexe de calcul de la métadonnée doit-il être créé pour la clé ?
        
        Notes
        -----
        Réécriture de la propriété :py:attr:`WidgetKey.has_compute_button`.
        
        Contrairement à beaucoup d'autre propriétés qui valent 
        pour les clés du groupe et non pour le groupe lui-même,
        celle-ci porte bien sur le groupe de valeurs.
        
        """
        return self and WidgetKey.with_compute_buttons \
            and bool(self.compute) and 'manual' in self.compute \
            and not self.is_read_only
    
    @property
    def compute(self):
        """list(str): Modes de calcul définis pour la clé.
        
        Notes
        -----
        Contrairement à beaucoup d'autre propriétés qui valent 
        pour les clés du groupe et non pour le groupe lui-même,
        celle-ci porte bien sur le groupe de valeurs.
        
        Il est permis de fournir en argument une liste de
        ``rdflib.term.Literal``, qui seront alors automatiquement
        convertis.

        """
        return self._compute
    
    @compute.setter
    def compute(self, value):
        if value:
            l = ['manual', 'auto', 'empty', 'new']
            value = [str(o) for o in value if str(o) in l]
        self._compute = value or []

    @property
    def compute_params(self):
        """dict: Paramètres à fournir à la méthode de calcul.
        
        Notes
        -----
        Contrairement à beaucoup d'autre propriétés qui valent 
        pour les clés du groupe et non pour le groupe lui-même,
        celle-ci porte bien sur le groupe de valeurs.
        
        Les paramètres sont fournis sous la forme clé/valeur,
        où la clé est une chaîne de caractères correspondant
        au nom du paramètre.

        """
        return self._compute_params
    
    @compute_params.setter
    def compute_params(self, value):
        if isinstance(value, dict):
            params = value.copy()
            for p in params:
                if not isinstance(p, str):
                    del params[p]
            if params:
                self._compute_params = params
            else:
                self._compute_params = None
        else:
            self._compute_params = None

    def is_empty(self, sources=None):
        """Le groupe est-il vide ?
        
        Un groupe est considéré comme vide quand il ne contient
        que des groupes vides ou des clés-valeurs sans valeur.
        Les fantômes sont pris en compte.
        
        Parameters
        ----------
        sources : list
            Une liste de sources à prendre en compte. Si ce
            paramètre est renseigné, toutes les clés-valeurs dont la
            source ne fait pas partie de la liste seront
            ignorées, de même que les groupes de propriétés.
        
        Notes
        -----
        Réécriture de la méthode :py:meth:`GroupKey.is_empty`.
        
        """
        if not sources:
            return super().is_empty()
        for child in self.children:
            if isinstance(child, ValueKey) \
                and child.value_source in sources \
                and not child.is_empty():
                return False
        return True

    def _hide_m(self, value, rec=False):
        super()._hide_m(value, rec=rec)
        if self.button:
            self.button._hide_m(value, rec=rec)

    def _search_from_uuid(self, uuid):
        super()._search_from_uuid(uuid)
        if self.button and str(self.button.uuid) == str(uuid):
            return self.button

    @property
    def attr_to_update(self):
        """list(str): Liste des attributs et propriétés pouvant être redéfinis post initialisation.
        
        Notes
        -----
        Réécriture de la propriété :py:attr:`WidgetKey.attr_to_update`.
        
        """
        return ['order_idx', 'predicate', 'label', 'description', 'rdfclass',
            'sources', 'datatype', 'transform', 'placeholder', 'input_mask',
            'is_mandatory', 'is_read_only', 'regex_validator',
            'regex_validator_flags', 'with_minus_buttons', 'geo_tools',
            'compute', 'compute_params']

    @property
    def attr_to_copy(self):
        """dict: Attributs de la classe à prendre en compte pour la copie des clés.
        
        Cette propriété est un dictionnaire dont les clés sont les
        noms des attributs contenant les informations nécessaires pour
        dupliquer la clé, et les valeurs sont des booléens qui indiquent
        si l'attribut est à prendre en compte lorsqu'il s'agit de
        créer une copie vide de la clé.
        
        Certains attributs sont volontairement exclus de cette liste, car
        ils requièrent un traitement spécifique.
        
        See Also
        --------
        WidgetKey.copy, GroupOfValuesKey.copy
        
        Notes
        -----
        Réécriture de la propriété :py:attr:`WidgetKey.attr_to_copy`.
        
        """
        return { 'order_idx': True, 'parent': True, 'predicate': True,
            'rdfclass': True, 'sources': True, 'datatype': True, 'transform': True,
            'with_minus_buttons' : True, 'label': True, 'description': True,
            'placeholder': True, 'input_mask': True, 'is_mandatory': True,
            'is_read_only': True, 'regex_validator': True,
            'regex_validator_flags': True, 'geo_tools': True, 'compute': True,
            'compute_params': True }

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
            dans un groupe de valeurs ou de traduction) - ``True`` - ou
            souhaite-t-on dupliquer une branche de l'arbre de clés
            en préservant son contenu - ``False`` ?
        
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
        
        Cette méthode n'a pas d'effet dans un groupe fantôme, ou si
        l'attribut de classe :py:attr:`WidgetKey.no_computation` vaut
        ``True``.
            
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
                WidgetKey.actionsbook.move.append(self.button)
            n += self.button.rowspan
        return n

    def compute_single_children(self):
        """Détermine si les clés du groupe sont des filles uniques.
        
        Cette méthode n'a pas d'effet dans un groupe fantôme, ou si
        l'attribut de classe :py:attr:`WidgetKey.no_computation` vaut
        ``True``.
        
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
                WidgetKey.actionsbook.show_minus_button.append(child)
            # boutons moins à masquer
            if true_children_count < 2 \
                and not child.is_single_child:
                child._is_single_child = True
                WidgetKey.actionsbook.hide_minus_button.append(child) 

    def shrink_expend(self, length, sources=None):
        """Prépare les clés filles du groupe en vue d'une saisie massive des valeurs.
        
        Cette méthode retire les valeurs des clés et, selon
        le nombre de clés demandées, supprime les clés excédentaires
        ou crée celles qui manquent.
        
        Parameters
        ----------
        length : int
            Nombre de clés attendues. Si `length` est inférieur
            à ``1``, il sera considéré qu'il vaut ``1``.
        sources : list(rdflib.term.URIRef), optional
            Liste de sources de vocabulaire contrôlé concernées.
            Si des sources sont définies pour le groupe, les
            clés-valeurs dont la source courante fait partie de
            cette liste seront supprimées-recrées, tandis que les
            autres seront préservées (incluant les groupes de
            propriétés qui sont la jumelle principale, même si
            la source courante de la clé-valeur associée est dans
            la liste). Si ce paramètres est ``None``, toutes les clés
            (clés-valeurs et groupes de propriétés) seront remplacées,
            quelle que soit leur source. Si ce paramètre est une 
            liste vide, toutes les clés existantes sont préservées.
        
        Returns
        -------
        list(ValueKey)
            Une liste de longueur `length` contenant les
            clés-valeurs prêtes à recevoir de nouvelles valeurs.
        
        Notes
        -----
        Cette méthode renvoie une liste vide si elle est appliquée à un
        groupe de valeurs sans bouton.
        
        """
        if self.is_hidden or not self.button:
            return []
        if not length or length < 1:
            length = 1
        old_children = self.children.copy()
        n = length
        l = [] # clés pour futur stockage des valeurs
        d = [] # clés à supprimer
        for child in self.real_children():
            if isinstance(child, GroupOfPropertiesKey):
                continue
            if child.m_twin and not child.is_main_twin:
                if sources is None:
                    if n:
                        child.m_twin.switch_twin(append_book=True)
                        n -= 1
                        l.append(child)
                    else:
                        d.append(child.m_twin)
                else:
                    continue
            elif sources is None or child.value_source in sources:
                if n:
                    n -= 1
                    child.value = None
                    l.append(child)
                else:
                    d.append(child)
        for child in d:
            child.drop(append_book=True)
        for i in range(n):
            self.button.add(append_book=True)
            # à la recherche de la clé qui vient d'être ajoutée...
            for child in self.real_children():
                if child.m_twin and not child.is_main_twin:
                    continue
                if not child in old_children and not child in l:
                    if isinstance(child, GroupOfPropertiesKey):
                        child.switch_twin(append_book=True)
                        l.append(child.m_twin)
                    else:
                        l.append(child)
                    break
        return l

    def _tree_keys(self):
        if self:
            yield from super()._tree_keys()
            if self.button:
                yield from self.button._tree_keys()
    
    def _notify_dead_children(self):
        super()._notify_dead_children()
        if self.button:
            WidgetKey.actionsbook.drop.append(self.button)

class TranslationGroupKey(GroupOfValuesKey):
    """Groupe de traduction.
    
    Un groupe de traduction est une clé de groupe de valeurs spécifique,
    dont les filles représentent les traductions d'un objet. Chaque membre
    du groupe a donc une propriété :py:attr:`ValueKey.value_language`
    différente, et tout l'enjeu du groupe de traduction est de veiller à
    ce que les langues restent distinctes.
    
    Outre ses attributs propres listés ci-après, :py:class:`TranslationGroupKey`
    hérite de tous les attributs de la classe :py:class:`GroupOfValuesKey`.
    La plupart présentent toutefois peu d'intérêt, valant soit ``None``, soit
    une valeur fixe (par exemple ``rdf:langString`` pour
    :py:attr:`TranslationGroupKey.xsd:type`).
    
    Parameters
    ----------
    parent : GroupKey
        La clé parente. Ne peut pas être ``None``.
    is_ghost : bool, default False
        True si la clé ne doit pas être matérialisée. À noter que quelle
        que soit la valeur fournie à l'initialisation, une fille de clé
        fantôme est toujours un fantôme. Il n'est pas permis d'avoir un
        groupe de traduction fantôme, y compris par héritage. Le cas échéant,
        c'est un groupe de valeurs classique (:py:class:GroupOfValuesKey)
        qui sera automatiquement créé à la place.
    order_idx : tuple of int, default (999,)
        Indice(s) permettant le classement de la clé parmi ses soeurs dans
        un groupe de propriétés. Les clés de plus petits indices seront les
        premières.
    predicate : rdflib.term.URIRef
        Le prédicat commun à toutes les valeurs du groupe.
    
    Warnings
    --------
    Il n'est possible de créer un groupe de traduction que si
    l'attribut partagé :py:attr:`with_language_buttons` vaut ``True``.
    À défaut, c'est un groupe de valeurs qui sera créé à la place.
    
    Notes
    -----
    Dans un groupe de traduction, dont les enfants sont nécessairement
    des clés-valeurs (:py:class:`ValueKey`) représentant des valeurs
    littérales, il n'y a jamais lieu de fournir des valeurs pour les
    propriétés :py:attr:`GroupOfValuesKey.rdfclass` et
    :py:attr:`GroupOfValuesKey.sources`. Elles n'apparaissent donc pas
    dans la liste de paramètres ci-avant, et - si valeurs il y avait -
    elles seraient silencieusement perdues. Ces propriétés renvoient
    toujours ``None``.
    
    """
    def __new__(cls, **kwargs):
        # crée un groupe de valeurs au lieu d'un groupe de
        # traduction dans le cas d'un fantôme
        parent = kwargs.get('parent')
        if kwargs.get('is_ghost', False) or not parent \
            or not WidgetKey.with_language_buttons:
            # si `parent` n'était pas spécifié, il y aura de toute
            # façon une erreur à l'initialisation
            return GroupOfValuesKey.__call__(**kwargs)
        return super().__new__(cls)
    
    def _base_attributes(self, **kwargs):
        super()._base_attributes(**kwargs)
        self._available_languages = WidgetKey.langlist.copy()

    @property
    def key_object(self):
        """str: Transcription littérale du type de clé.
        
        """
        return 'translation group'

    @property
    def available_languages(self):
        """list(str) : Liste des langues encore disponibles pour les traductions.
        
        Cette liste est initialisée avec la variable partagée
        :py:attr:`WidgetKey.langlist`, et mise à jour automatiquement
        au gré des ajouts et suppressions de traductions dans le groupe.
        
        """
        return self._available_languages

    @property
    def rdfclass(self):
        return None
        
    @rdfclass.setter
    def rdfclass(self, value):
        self._rdfclass = None
        
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
    def datatype(self):
        """rdflib.term.URIRef: Type de valeur commun à toutes les valeurs du groupe.
        
        Notes
        -----
        Cette propriété vaut toujours ``rdf:langString`` pour un groupe
        de traduction. Toute tentative de modification sera silencieusement
        ignorée.
        
        """
        return self._datatype
        
    @datatype.setter
    def datatype(self, value):
        self._datatype = RDF.langString

    def language_in(self, value_language):
        """Ajoute une langue à la liste des langues disponibles.
        
        Parameters
        ----------
        value_language : str
            Langue redevenue disponible.

        """        
        if not value_language in WidgetKey.langlist \
            or value_language in self.available_languages:
            return
            # une langue qui n'était pas autorisée n'est
            # pas remise dans le pot. Idem pour une langue
            # qui y était déjà (cas de doubles traductions,
            # ce qui pourrait arriver dans des fiches importées).       
        self.available_languages.append(value_language)     
        for child in self.real_children():
            WidgetKey.actionsbook.languages.append(child)
        if self.button and len(self.available_languages) == 1:
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
        for child in self.real_children():
            WidgetKey.actionsbook.languages.append(child)
        if not self.available_languages and self.button:
            WidgetKey.actionsbook.hide.append(self.button)


class ValueKey(ObjectKey):
    """Clé-valeur.
    
    Une clé-valeur est une clé-objet représentant une valeur litérale ou
    un IRI. Elle a vocation a être matérialisée par un widget de saisie.
    
    Outre ses méthodes et attributs propres listés ci-après,
    py:class:`ValueKey` hérite de toutes les méthodes et attributs de
    la classe py:class:`ObjectKey`.
    
    Parameters
    ----------
    parent : GroupKey
        La clé parente. Ne peut pas être ``None``.
    is_ghost : bool, default False
        ``True`` si la clé ne doit pas être matérialisée. À noter que quelle
        que soit la valeur fournie à l'initialisation, une fille de clé
        fantôme est toujours un fantôme.
    order_idx : tuple of int, default (999,)
        Indice(s) permettant le classement de la clé parmi ses soeurs dans
        un groupe de propriétés. Les clés de plus petits indices seront les
        premières. Cet argument sera ignoré si le groupe parent est un
        groupe de valeurs (:py:class:`GroupOfvaluesKey`).
    predicate : rdflib.term.URIRef
        Prédicat représenté par la clé. Si la clé appartient à un groupe
        de valeurs, c'est lui qui porte cette information. Sinon, elle
        est obligatoire. Pour des clés jumelles, le prédicat déclaré
        sur la jumelle de référence prévaut, sauf s'il vaut ``None``.
    label : str or rdflib.term.Literal, optional
        Etiquette de la clé (libellé de la catégorie de métadonnée
        représentée par la clé). Cet argument est ignoré si la clé
        appartient à un groupe de valeurs. Pour des clés jumelles,
        l'étiquette déclarée sur la jumelle de référence prévaut.
    description : str or rdflib.term.Literal, optional
        Définition de la catégorie de métadonnée représentée par la clé.
        Cet argument est ignoré si la clé appartient à un groupe de valeurs.
        Pour des clés jumelles, le descriptif déclaré sur la jumelle de
        référence prévaut.
    m_twin : ObjectKey, optional
        Clé jumelle, le cas échéant. Un couple de jumelle ne se déclare
        qu'une fois, sur la seconde clé créée.
    is_hidden_m : bool, default False
        La clé est-elle la clé masquée du couple de jumelles ? Ce paramètre
        n'est pris en compte que pour une clé qui a une jumelle.    
    rowspan : int, optional
        Nombre de lignes occupées par le ou les widgets portés par la clé,
        étiquette séparée non comprise. `rowspan` vaudra toujours ``0`` pour une
        clé fantôme. Si aucune valeur n'est fournie, une valeur par défaut de
        ``1`` est appliquée.
    independant_label : bool, default False
        ``True`` si l'étiquette de la clé occupe une ligne séparée de la grille.
    sources : list of rdflib.term.URIRef, optional
        Le cas échéant, liste des sources de vocabulaire contrôlé pour les valeurs
        de la clé. Si la clé appartient à un groupe de valeurs, c'est lui qui
        porte cette information.
    transform : {None, 'email', 'phone'}, optional
        Le cas échéant, la nature de la transformation appliquée à
        l'objet. Si la clé appartient à un groupe de valeurs, c'est lui
        qui porte cette information.
    placeholder : str or rdflib.term.Literal, optional
        Le cas échéant, texte de substitution à utiliser pour la clé. Si la
        clé appartient à un groupe de valeurs, c'est lui qui porte cette
        information.
    input_mask : str or rdflib.term.Literal, optional
        Le cas échéant, masque de saisie à utiliser pour la clé. Si la clé
        appartient à un groupe de valeurs, c'est lui qui porte cette
        information.
    is_mandatory : bool or rdflib.term.Literal, default False
        Cette clé devra-t-elle obligatoirement recevoir une valeur ? Si la
        clé appartient à un groupe de valeurs, c'est lui qui porte cette
        information.
    regex_validator : str, optional
        Le cas échéant, expression rationnelle de validation à utiliser pour
        la clé. Si la clé appartient à un groupe de valeurs, c'est lui qui porte
        cette information.
    regex_validator_flags : str, optional
        Le cas échéant, paramètres associés à l'expression rationnelle de
        validation de la clé. Si la clé appartient à un groupe de valeurs, c'est
        lui qui porte cette information.
    rdfclass : rdflib.term.URIRef, optional
        Classe RDF de la clé-valeur, s'il s'agit d'un IRI. Si la clé appartient
        à un groupe de valeurs, c'est lui qui porte cette information.
    datatype : rdflib.term.URIRef, optional
        Le type de la clé-valeur, le cas échéant. Doit impérativement
        valoir ``rdf:langString`` pour que les informations sur les
        langues soient prises en compte. Si la clé appartient à un groupe de
        valeurs, c'est lui qui porte cette information. Dans le cas contraire,
        si :py:attr:`ValueKey.rdfclass` n'est pas nul, il sera toujours
        considéré que :py:attr:`ValueKey.datatype` l'est. Sinon, ``xsd:string``
        est utilisé comme valeur par défaut.
        Seuls les types suivants sont pris en charge, pour les autres
        ``xsd:string`` serait utilisé à la place : ``xsd:string``,
        ``xsd:integer``, ``xsd:decimal``, ``xsd:boolean``, ``xsd:date``,
        ``xsd:time``, ``xsd:dateTime``, ``xsd:duration``, ``gsp:wktLiteral``,
        ``rdf:langString``.
    do_not_save : bool, default False
        ``True`` si la valeur de la clé (:py:attr:`ValueKey.value`) ne doit
        pas être sauvegardée.
    value : rdflib.term.Literal or rdflib.term.URIRef, optional
        La valeur mémorisée par la clé (objet du triplet RDF). Une clé
        fantôme ne sera effectivement créée que si une valeur est fournie
        pour ce paramètre ou si le paramètre `delayed` ci-après vaut ``True``.
    delayed : bool, default False
        Si ``True``, autorise la création d'une clé-fantôme sans valeur,
        étant entendu que la valeur sera fournie ultérieurement. Ce
        paramètres est utile lorsque la valeur doit être dé-sérialisée
        en fonction des paramètres de la clé (par exemple avec la méthode
        :py:meth:`plume.rdf.widgetsdict.WidgetsDict.update_value`), ce qui
        suppose que celle-ci soit préalablement initialisée.
    value_language : str, optional
        La langue de l'objet. Obligatoire pour une valeur litérale de
        type ``rdf:langString`` et a fortiori dans un groupe de traduction,
        ignoré pour tous les autres types.
    value_source : rdflib.term.URIRef
        La source utilisée par la valeur courante de la clé. Si la valeur
        fournie pour l'IRI ne fait pas partie des sources autorisées, elle
        sera silencieusement supprimée.
    is_long_text : bool, default False
        Dans le cas d'une valeur de type ``xsd:string`` ou ``rdf:langString``,
        indique si le texte est présumé long (``True``) ou court (``False``,
        valeur par défaut). Même dans un groupe de valeurs, cette propriété
        est définie indépendamment pour chaque clé, afin qu'il soit possible
        de l'adapter à la longueur effective des valeurs.
    geo_tools : list(str or rdflib.term.Literal)
        Liste de fonctionnalités d'aide à la saisie des géométries
        disponibles pour la clé. Seules les valeurs suivantes seront prises
        en compte : ``'show'``, ``'point'``, ``'linestring'``, ``'rectangle'``,
        ``'polygon'``, ``circle``, ``'bbox'``, ``'centroid'``.
    compute : list(str or rdflib.term.Literal), optional
        Liste de modes de calcul disponibles pour la clé. Seules les valeurs
        `'manual'`, `'auto'`, `'empty'` et `'new'` sont reconnues à ce stade.
    compute_params : dict, optional
        Paramètres à fournir à la méthode de calcul.
    
    """
    
    def __new__(cls, **kwargs):
        # inhibe la création de clés-valeurs fantôme sans
        # valeur, sauf à ce que delayed vaille True
        parent = kwargs.get('parent')
        if not kwargs.get('value') and (kwargs.get('is_ghost', False) \
            or (parent is not None and parent.is_ghost)) and \
            not kwargs.get('delayed', False):
            return
        return super().__new__(cls)
    
    def _base_attributes(self, **kwargs):
        super()._base_attributes(**kwargs)
        self._do_not_save = None
        self._independant_label = None
        self._sources = None
        self._rdfclass = None
        self._datatype = None
        self._is_long_text = None
        self._rowspan = 0
        self._transform = None
        self._placeholder = None
        self._input_mask = None
        self._is_mandatory = None
        self._regex_validator = None
        self._regex_validator_flags = None
        self._geo_tools = None
        self._compute = None
        self._compute_params = None        
        self._value = None
        self._value_language = None
        self._value_source = None
        self._value_unit = None
    
    def _computed_attributes(self, **kwargs):
        super()._computed_attributes(**kwargs)
        self.do_not_save = kwargs.get('do_not_save')
        self.independant_label = kwargs.get('independant_label')
        self.sources = kwargs.get('sources')
        self.rdfclass = kwargs.get('rdfclass')
        self.datatype = kwargs.get('datatype')
        self.is_long_text = kwargs.get('is_long_text')
        self.rowspan = kwargs.get('rowspan')
        self.transform = kwargs.get('transform')
        self.placeholder = kwargs.get('placeholder')
        self.input_mask = kwargs.get('input_mask')
        self.is_mandatory = kwargs.get('is_mandatory')
        self.regex_validator = kwargs.get('regex_validator')
        self.regex_validator_flags = kwargs.get('regex_validator_flags')
        self.geo_tools = kwargs.get('geo_tools')
        self.compute = kwargs.get('compute')
        self.compute_params = kwargs.get('compute_params')
        self.value = kwargs.get('value')
        self.value_language = kwargs.get('value_language')
        self.value_source = kwargs.get('value_source')
        self.value_unit = None

    @property
    def key_object(self):
        """str: Transcription littérale du type de clé.
        
        """
        return 'edit'
    
    @property
    def rowspan(self):
        """int: Nombre de lignes de la grille occupées par la clé.
        
        Notes
        -----
        `rowspan` vaudra toujours ``0`` pour une clé fantôme. Si aucune
        valeur n'est fournie, une valeur par défaut de ``1`` est appliquée.
        `rowspan` vaut toujours ``1`` quand :py:attr:`is_long_text` vaut
        ``False`` ou pour une clé qui a une jumelle.
        
        Il est permis de fournir des valeurs de type ``rdflib.term.Literal``,
        qui seront alors automatiquement converties. De même pour
        des valeurs qui se trouveraient être fournies sous forme de
        chaîne de caractères.
        
        Modifier cette propriété emporte la mise en cohérence de
        la propriété :py:attr:`WidgetKey.row` pour toutes les clés
        du groupe parent, via :py:meth:`GroupKey.compute_rows`.
        
        """
        return self._rowspan
    
    @rowspan.setter
    def rowspan(self, value):
        old_value = self.rowspan
        if not self:
            value = 0
        else:
            if not self.is_long_text or self.m_twin:
                # théoriquement, l'existence d'un jumeau implique
                # que rdfclass n'est pas None et donc que is_long_text
                # vaut False, mais on écrit explicitement la condition
                # pour plus de résilience
                value = 1
            elif isinstance(value, Literal):
                value = value.toPython()
            elif isinstance(value, str) and value.isdigit():
                value = int(value)
            if not isinstance(value, int) or value <= 0:
                value = 1
        value = min((value, WidgetKey.max_rowspan))
        self._rowspan = value
        if not self._is_unborn and old_value != value:
            self.parent.compute_rows()
    
    @property
    def independant_label(self):
        """bool: L'étiquette de la clé occupe-t-elle sa propre ligne de la grille ?
        
        Notes
        -----
        Réécriture de la propriété :py:attr:`WidgetKey.independant_label`.
        
        Cette propriété vaudra toujours ``False`` pour une clé fantôme ou
        qui n'a pas d'étiquette. Par défaut, il est également considéré
        qu'elle vaut ``False``.
        
        Il n'est pas permis à une clé jumelle d'avoir une étiquette indépendante,
        car les deux jumelles doivent occuper exactement le même nombre de lignes
        de la grille, et le groupe de propriétés n'en occupe qu'une. La valeur
        sera mise silencieusement à ``False`` dans ce cas.
        
        Il est permis de fournir des valeurs de type ``rdflib.term.Literal``,
        qui seront alors automatiquement converties.
        
        Modifier cette propriété emporte la mise en cohérence de la propriété
        :py:attr:`WidgetKey.row` pour toutes les clés du groupe parent.
        
        """
        return self._independant_label
    
    @independant_label.setter
    def independant_label(self, value):
        old_value = self.independant_label
        if self.m_twin or not self.has_label:
            value = False
        value = bool(value)
        self._independant_label = value
        if not self._is_unborn and old_value != value:
            self.parent.compute_rows()
    
    @property
    def has_language_button(self):
        """bool: Un bouton annexe de sélection de la langue doit-il être créé pour la clé ?
        
        Notes
        -----
        Réécriture de la propriété :py:attr:`WidgetKey.has_language_button`.
        
        """
        return self and WidgetKey.with_language_buttons \
            and self.datatype == RDF.langString \
            and not self.is_read_only
    
    @property
    def has_source_button(self):
        """bool: Un bouton annexe de sélection de la source doit-il être créé pour la clé ?
        
        Notes
        -----
        Réécriture de la propriété :py:attr:`WidgetKey.has_source_button`.
        
        """
        return self and WidgetKey.with_source_buttons \
            and ((self.sources and len(self.sources) > 1) or bool(self.m_twin)) \
            and not self.is_read_only
    
    @property
    def has_unit_button(self):
        """bool: Un bouton annexe de sélection de l'unité doit-il être créé pour la clé ?
        
        Notes
        -----
        Réécriture de la propriété :py:attr:`WidgetKey.has_unit_button`.
        
        Pour l'heure, de tels boutons ne sont prévus que pour les valeurs
        de type ``xsd:duration``.
        
        """
        return self and WidgetKey.with_unit_buttons \
            and self.datatype == XSD.duration \
            and not self.is_read_only
    
    @property
    def has_geo_button(self):
        """bool: Un bouton annexe d'aide à la saisie des géométries doit-il être créé pour la clé ?
        
        Notes
        -----
        Réécriture de la propriété :py:attr:`WidgetKey.has_geo_button`.
        
        Pour l'heure, de tels boutons ne sont prévus que pour les valeurs
        de type ``gsp:wktLiteral``.
        
        Au contraire de la plupart des autres boutons, des boutons d'aide à la
        saisie des géométries peuvent accompagner des clés en lecture seule
        (c'est-à-dire pour lesquelles la propriété :py:attr:`ValueKey.is_read_only`
        vaut  ``True``), car ils portent aussi des fonctionnalités de visualisation.
        C'est la propriété :py:attr:`ValueKey.geo_tools` qui se charge d'éliminer
        les fonctionnalités d'édition.        
        
        """
        return self and WidgetKey.with_geo_buttons \
            and bool(self.geo_tools)
    
    @property
    def has_compute_button(self):
        """bool: Un bouton annexe de calcul de la métadonnée doit-il être créé pour la clé ?
        
        Notes
        -----
        Réécriture de la propriété :py:attr:`WidgetKey.has_compute_button`.
        
        Il n'y a jamais de bouton de calcul quand un bouton
        d'aide à la saisie des géométries est présent, car les
        deux seraient redondants.
        
        """
        return self and WidgetKey.with_compute_buttons \
            and bool(self.compute) and 'manual' in self.compute \
            and not self.has_geo_button \
            and not self.is_read_only
    
    @property
    def has_label(self):
        """bool: Une étiquette non intégrée au widget principal doit-elle être créée pour la clé ?
        
        """
        return bool(self and self.label)
    
    @property
    def value(self):
        """rdflib.term.URIRef or rdflib.term.Literal: Valeur portée par la clé (objet du triplet RDF).

        """
        return self._value
        
    @value.setter
    def value(self, value):
        # le setter est trivial pour l'heure, mais on pourrait
        # envisager d'y ajouter des contrôles, notamment sur
        # le type.
        self._value = value
        if not self._is_unborn:
            if value:
                # l'unité est réinitialisée selon la valeur
                self.value_unit = None
                # idem pour la langue
                self.value_language = None
            # on considère que la valeur du widget de saisie
            # devra être actualisée même si la nouvelle
            # valeur de value est identique à l'ancienne,
            # car cela permet de réinitialiser des valeurs
            # saisies dans les widgets sans avoir encore été
            # transmises aux clés
            WidgetKey.actionsbook.update.append(self)

    @property
    def rdfclass(self):
        """rdflib.term.URIRef: La classe RDF de la clé-valeur.
        
        Notes
        -----
        Si la clé appartient à un groupe de valeurs ou de traduction,
        la propriété du groupe parent est renvoyée. Tenter d'en modifier
        la valeur n'aura silencieusement aucun effet.
        
        Si la clé a une jumelle dont la classe est différente
        de la valeur fournie, c'est celle de la jumelle de référence
        qui prévaudra, sauf si elle vaut ``None``. Autrement dit, pour
        changer la classe d'un couple de jumelles, il faut cibler
        la jumelle de référence, sans quoi l'opération n'aura pas d'effet.
        
        Modifier cette propriété emporte la mise en cohérence de la propriété
        :py:attr:`ValueKey.datatype`.
        
        """
        if isinstance(self.parent, GroupOfValuesKey):
            return self.parent.rdfclass
        return self._rdfclass

    @rdfclass.setter
    def rdfclass(self, value):
        if not isinstance(self.parent, GroupOfValuesKey):
            if self.m_twin and (not self.is_main_twin or not value):
                value = self.m_twin.rdfclass
                # impossible que value soit None, le setter
                # de GroupOfPropertiesKey aurait renvoyé une erreur
            self._rdfclass = value
            if not self._is_unborn:
                self.datatype = self.datatype
            if self.m_twin and value != self.m_twin.rdfclass \
                and self.is_main_twin:
                self.m_twin._rdfclass = value 

    @property
    def datatype(self):
        """rdflib.term.URIRef: Renvoie le type de la valeur portée par la clé.
        
        Notes
        -----
        Si la clé appartient à un groupe de valeurs ou de traduction,
        la propriété du groupe parent est renvoyée. Tenter d'en modifier
        la valeur n'aura silencieusement aucun effet.
        
        :py:attr:`ValueKey.rdfclass` prévaut sur :py:attr:`ValueKey.datatype` :
        si le premier est renseigné, c'est que la valeur est un IRI ou un noeud
        anonyme, et le second ne peut qu'être nul. Sinon, ``xsd:string`` est utilisé
        comme valeur par défaut.
        
        Seuls les types suivants sont pris en charge, pour les autres
        ``xsd:string`` serait utilisé à la place : ``xsd:string``,
        ``xsd:integer``, ``xsd:decimal``, ``xsd:boolean``, ``xsd:date``,
        ``xsd:time``, ``xsd:dateTime``, ``xsd:duration``, ``gsp:wktLiteral``,
        ``rdf:langString``.
        
        Modifier cette propriété emporte la mise en cohérence des
        propriétés :py:attr:`ValueKey.value_language`,
        :py:attr:`ValueKey.is_long_text`, :py:attr:`ValueKey.value_unit`,
        :py:attr:`ValueKey.geo_tools`. En particulier, si
        :py:attr:`ValueKey.value_language` contient une langue mais
        que :py:attr:`ValueKey.datatype` n'est plus ``rdf:langString``,
        la langue sera silencieusement effacée. De même, la liste
        de fonctionnalités d'aide à la saisie contenue dans 
        :py:attr:`ValueKey.geo_tools` sera définitivement perdue
        si :py:attr:`ValueKey.datatype` n'est plus ``gsp:wktLiteral``.
        
        """
        if isinstance(self.parent, GroupOfValuesKey):
            return self.parent.datatype
        return self._datatype
    
    @datatype.setter
    def datatype(self, value):
        if not isinstance(self.parent, GroupOfValuesKey):
            tlist = [XSD.string, XSD.integer, XSD.decimal,
                XSD.boolean, XSD.date, XSD.time, XSD.dateTime,
                XSD.duration, GSP.wktLiteral, RDF.langString]
            if self.rdfclass:
                value = None
            elif not value in tlist:
                value = XSD.string
            self._datatype = value
            if not self._is_unborn:
                self.geo_tools = self._geo_tools
                # on réinitialise bien avec _geo_tools
                # et pas geo_tools, car le second tronque
                # la liste si la clé est en lecture seule
                self.value_language = self.value_language
                self.is_long_text = self.is_long_text
                self.value_unit = self.value_unit
    
    @property
    def placeholder(self):
        """str: Texte de substitution à utiliser pour la clé.
        
        Notes
        -----
        Si la clé appartient à un groupe de valeurs ou de traduction,
        la propriété du groupe parent est renvoyée. Tenter d'en modifier
        la valeur n'aura silencieusement aucun effet.
        
        Il est permis de fournir des valeurs de type ``rdflib.term.Literal``,
        qui seront alors automatiquement converties.
        
        """
        if isinstance(self.parent, GroupOfValuesKey):
            return self.parent.placeholder
        return self._placeholder

    @placeholder.setter
    def placeholder(self, value):
        if not isinstance(self.parent, GroupOfValuesKey):
            self._placeholder = str(value) if value else None
    
    @property
    def input_mask(self):
        """str: Masque de saisie à utiliser pour la clé.
        
        Notes
        -----
        Si la clé appartient à un groupe de valeurs ou de traduction,
        la propriété du groupe parent est renvoyée. Tenter d'en modifier
        la valeur n'aura silencieusement aucun effet.

        Il est permis de fournir des valeurs de type ``rdflib.term.Literal``,
        qui seront alors automatiquement converties.
        
        """
        if isinstance(self.parent, GroupOfValuesKey):
            return self.parent.input_mask
        return self._input_mask

    @input_mask.setter
    def input_mask(self, value):
        if not isinstance(self.parent, GroupOfValuesKey):
            self._input_mask = str(value) if value else None
    
    @property
    def is_mandatory(self):
        """bool: Cette clé devra-t-elle obligatoirement recevoir une valeur ?
        
        Notes
        -----
        Si la clé appartient à un groupe de valeurs ou de traduction,
        la propriété du groupe parent est renvoyée. Tenter d'en modifier
        la valeur n'aura silencieusement aucun effet.

        Il est permis de fournir des valeurs de type ``rdflib.term.Literal``,
        qui seront alors automatiquement converties.
        
        """
        if isinstance(self.parent, GroupOfValuesKey):
            return self.parent.is_mandatory
        return self._is_mandatory

    @is_mandatory.setter
    def is_mandatory(self, value):
        if not isinstance(self.parent, GroupOfValuesKey):
            self._is_mandatory = bool(value)
    
    @property
    def regex_validator(self):
        """str: Expression rationnelle de validation à utiliser pour la clé.
        
        Notes
        -----
        Si la clé appartient à un groupe de valeurs ou de traduction,
        la propriété du groupe parent est renvoyée. Tenter d'en modifier
        la valeur n'aura silencieusement aucun effet.
        
        Dans le cas d'une clé prenant pour valeur des IRI libres
        (non issues d'un thésaurus) et pour laquelle aucune expression
        rationnelle n'est explicitement définie, y compris par héritage,
        la propriété renvoie une expression rationnelle permettant
        
        Il est permis de fournir des valeurs de type ``rdflib.term.Literal``,
        qui seront alors automatiquement converties.
        
        Modifier cette propriété emporte la mise en cohérence de la propriété
        :py:attr:`ValueKey.regex_validator_flags`.
        
        """
        rv = self.parent.regex_validator \
            if isinstance(self.parent, GroupOfValuesKey) \
            else self._regex_validator
        if not rv and self.rdfclass and not self.sources:
            return r'^[^<>"\s{}|\\^`]*$'
        else:
            return rv

    @regex_validator.setter
    def regex_validator(self, value):
        if not isinstance(self.parent, GroupOfValuesKey):
            self._regex_validator = str(value) if value else None
            if not self._is_unborn:
                self.regex_validator_flags = self.regex_validator_flags
    
    @property
    def regex_validator_flags(self):
        """str: Paramètres associés à l'expression rationnelle de validation de la clé.
        
        Notes
        -----
        Si la clé appartient à un groupe de valeurs ou de traduction,
        la propriété du groupe parent est renvoyée. Tenter d'en modifier
        la valeur n'aura silencieusement aucun effet.
        
        Toute tentative pour définir une valeur pour cette propriété alors
        que :py:attr:`ValueKey.regex_validator` vaut ``None`` sera
        silencieusement ignorée.
        
        Il est permis de fournir des valeurs de type ``rdflib.term.Literal``,
        qui seront alors automatiquement converties.
        
        """
        if isinstance(self.parent, GroupOfValuesKey):
            return self.parent.regex_validator_flags
        return self._regex_validator_flags

    @regex_validator_flags.setter
    def regex_validator_flags(self, value):
        if not isinstance(self.parent, GroupOfValuesKey):
            if not self.regex_validator:
                value = None
            self._regex_validator_flags = str(value) if value else None
    
    @property
    def geo_tools(self):
        """list(str): Fonctionnalités d'aide à la saisie des géométries disponibles pour la clé.
        
        Notes
        -----
        Si la clé appartient à un groupe de valeurs, la propriété du
        groupe parent est renvoyée. Tenter d'en modifier la valeur
        n'aura silencieusement aucun effet.
        
        Cette propriété vaudra toujours ``None`` si :py:attr:`ValueKey.datatype`
        n'est pas ``gsp:wktLiteral``. Pour le type ``gsp:wktLiteral``, il s'agira
        toujours d'une liste, quitte à ce qu'elle soit vide.
        
        Seules les valeurs suivantes sont acceptées (les autres seront
        silencieusement éliminées) : ``'show'``, ``'point'``,
        ``'linestring'``, ``'rectangle'``, ``'polygon'``, ``'circle'``,
        ``'bbox'``, ``'centroid'``.
        
        Lorsque la clé est en lecture seule, soit quand la propriété
        :py:attr:`ValueKey.is_read_only` vaut ``True``, la liste
        contiendra au plus `'show'`. C'est le getter de la propriété qui 
        génère à la volée une liste tronquée à partir de la liste mémorisée,
        afin de préserver toutes les valeurs pour le cas où
        :py:attr:`ValueKey.is_read_only` reviendrait à ``False``.
        
        Il est permis de fournir en argument une liste de
        ``rdflib.term.Literal``, qui seront alors automatiquement convertis.

        """
        if isinstance(self.parent, GroupOfValuesKey):
            return self.parent.geo_tools
        if self.is_read_only and self._geo_tools:
            return ['show'] if 'show' in self._geo_tools else []
        return self._geo_tools
    
    @geo_tools.setter
    def geo_tools(self, value):
        if not isinstance(self.parent, GroupOfValuesKey):
            if not self.datatype == GSP.wktLiteral:
                value = None
            elif not value:
                value = []
            else:
                l = ['show', 'point', 'linestring', 'rectangle',
                    'polygon', 'circle', 'bbox', 'centroid']
                value = [str(o) for o in value if str(o) in l]
            self._geo_tools = value
        else:
            self._geo_tools = None
    
    @property
    def compute(self):
        """list(str): Modes de calcul définis pour la clé.
        
        Notes
        -----
        Si la clé appartient à un groupe de valeurs, cette propriété
        vaudra toujours ``None``.
        
        Il est permis de fournir en argument une liste de
        ``rdflib.term.Literal``, qui seront alors automatiquement convertis.

        """
        if not isinstance(self.parent, GroupOfValuesKey):
            return self._compute
    
    @compute.setter
    def compute(self, value):
        if not isinstance(self.parent, GroupOfValuesKey):
            if value:
                l = ['manual', 'auto', 'empty', 'new']
                value = [str(o) for o in value if str(o) in l]
            self._compute = value or []
        else:
            self._compute = None
    
    def is_empty(self, **kwargs):
        """La clé est-elle vide ?
        
        Renvoie simplement ``True`` si l'attribut
        :py:attr:``ValueKey.value`` de la clé vaut ``None``.
        
        Notes
        -----
        Cette méthode admet des paramètres arbitraires pour
        qu'elle puisse être appelée dans les mêmes conditions
        que les méthodes de même nom définies sur d'autres
        classes de clés. En pratique, elle n'en utilise aucun.
        
        """
        return self.value is None
    
    @property
    def compute_params(self):
        """dict: Paramètres à fournir à la méthode de calcul.
        
        Notes
        -----
        Si la clé appartient à un groupe de valeurs, cette propriété
        vaudra toujours ``None``.
        
        Les paramètres sont fournis sous la forme clé/valeur,
        où la clé est une chaîne de caractères correspondant
        au nom du paramètre.

        """
        if not isinstance(self.parent, GroupOfValuesKey):
            return self._compute_params
    
    @compute_params.setter
    def compute_params(self, value):
        if not isinstance(self.parent, GroupOfValuesKey) \
            and isinstance(value, dict):
            params = value.copy()
            for p in params:
                if not isinstance(p, str):
                    del params[p]
            if params:
                self._compute_params = params
            else:
                self._compute_params = None
        else:
            self._compute_params = None
    
    @property
    def value_language(self):
        """str: Langue de la valeur portée par la clé.
        
        Tant qu'aucune langue n'a été explicitement définie, et s'il
        y a lieu de renvoyer une langue, c'est la langue principale
        de saisie des métadonnées qui est renvoyée.
        
        Notes
        -----
        Si :py:attr:`ValueKey.datatype` n'est pas ``rdf:langString``,
        cette propriété vaudra toujours ``None``.
        
        À l'initialisation, si aucune langue n'est fournie, elle
        sera déduite de :py:attr:`ValueKey.value` si une valeur
        a été spécifiée. À défaut, dans un groupe de traduction,
        la première langue de la liste des langues disponibles
        sera utilisée.
        
        """
        if self._value_language:
            return self._value_language
        elif self.datatype == RDF.langString:
            return self.main_language
    
    @value_language.setter
    def value_language(self, value):
        if self.datatype != RDF.langString:
            value = None
        elif not value and isinstance(self.value, Literal):
            value = self.value.language
        if isinstance(self.parent, TranslationGroupKey):
            if not value:
                if self.available_languages:
                    value = self.available_languages[0]
                else:
                    raise IntegrityBreach('Plus de langue disponible.', self)
            if self._value_language != value:
                self.parent.language_in(self._value_language)
                self.parent.language_out(value)
        elif self.value_language != value:
            WidgetKey.actionsbook.languages.append(self)
        self._value_language = value
    
    @property
    def value_source(self):
        """rdflib.term.URIRef: Renvoie la source de la valeur portée par la clé.
        
        Notes
        -----
        :py:attr:`ValueKey.value_source` vaut toujours ``None`` quand
        la clé n'admet pas de sources de vocabulaire contrôlé. Elle peut
        valoir ``None`` alors que :py:attr:`ValueKey.sources` n'est pas nul,
        si la source fournie n'était pas référencée. Sinon, toute valeur
        prise par cette propriété est nécessairement une des valeurs de la liste
        de l'attribut :py:attr:`ValueKey.sources`.
        
        Si aucune source n'est fournie et qu'il n'y a pas non plus de valeur
        (:py:attr:`ValueKey.value` est `None`), la première source de
        :py:attr:`ValueKey.sources` est utilisée.
        
        Modifier la source post initialisation a pour effet d'effacer la
        valeur mémorisée (:py:attr:`ValueKey.value`), puisque l'ancienne valeur
        est présumée issue de l'ancienne source.

        """
        return self._value_source
    
    @value_source.setter
    def value_source(self, value):
        old_value = self.value_source
        if not self.sources:
            self._value_source = None
        else:
            if not value and not self.value:
                value = self.sources[0]
            if value in self.sources:
                self._value_source = value
            else:
                self._value_source = None
        if not self._is_unborn and self.value_source != old_value:
            WidgetKey.actionsbook.sources.append(self)
            WidgetKey.actionsbook.thesaurus.append(self)
            # même si l'ancienne valeur était déjà None,
            # car on veut réinitialiser la valeur contenue
            # dans le widget même si elle n'a pas été transmise
            # à la clé
            self.value = None
    
    @property
    def value_unit(self):
        """str: Unité de la valeur portée par la clé.
        
        Notes
        -----
        Si :py:attr:`ValueKey.datatype` n'est pas ``xsd:duration``,
        cette propriété vaudra toujours ``None``.
        
        Cette propriété est déduite de :py:attr:`ValueKey.value`
        (et mise à jour quand :py:attr:`ValueKey.value` est modifié).
        À défaut, il s'agira de la première valeur de la liste
        :py:attr:`ValueKey.units`.
        
        Modifier cette propriété ne change pas :py:attr:`ValueKey.value`.
        Autrement dit, l'unité effectivement incluse dans la valeur
        prévaut toujours sur cette propriété, puisque c'est elle qui
        sera conservée lors de la transformation en graphe par
        :py:meth:`RootKey.build_metagraph`.
        
        """
        return self._value_unit
    
    @value_unit.setter
    def value_unit(self, value):
        old_value = self.value_unit
        if not self.units:
            self._value_unit = None
        else:
            if not value or not value in self.units:
                value = None
                if self.value:
                    i, value = int_from_duration(self.value)
            if not value:
                value = self.units[0]
            self._value_unit = value
        if not self._is_unborn and self.value_unit != old_value:
            WidgetKey.actionsbook.units.append(self)  
    
    @property
    def do_not_save(self):
        """bool: Faut-il ne pas sauvegarder la valeur renseignée sur la clé ?
        
        Notes
        -----
        Il est permis de fournir des valeurs de type ``rdflib.term.Literal``,
        qui seront alors automatiquement converties.
        
        """
        return self._do_not_save
        
    @do_not_save.setter
    def do_not_save(self, value):
        self._do_not_save = bool(value)
    
    @property
    def is_long_text(self):
        """bool: La valeur de la clé est-elle un long texte ?
        
        Notes
        -----
        Cette propriété ne peut valoir ``True`` que pour une valeur textuelle
        (``rdf:langString``, ``xsd:string``, ``gsp:wktLiteral``). Toute
        tentative dans d'autres circonstances serait silencieusement ignorée.

        Elle vaut toujours ``True`` pour le type ``gsp:wktLiteral``.
        
        Il est permis de fournir des valeurs de type ``rdflib.term.Literal``,
        qui seront alors automatiquement converties.
        
        Modifier cette propriété emporte la mise en cohérence de
        la propriété :py:attr:`WidgetKey.rowspan`.
        
        """
        return self._is_long_text
    
    @is_long_text.setter
    def is_long_text(self, value):
        if self.datatype == GSP.wktLiteral:
            self._is_long_text = True
        elif value and self.datatype in (RDF.langString, XSD.string):
            self._is_long_text = True
        else:
            self._is_long_text = False
        if not self._is_unborn:
            self.rowspan = self.rowspan
    
    @property
    def transform(self):
        """{None, 'email', 'phone'}: Nature de la transformation appliquée à l'objet.
        
        Notes
        -----
        Si la clé appartient à un groupe de valeurs ou de traduction,
        la propriété du groupe parent est renvoyée. Tenter d'en modifier
        la valeur n'aura silencieusement aucun effet.
        
        Il est permis de fournir des valeurs de type ``rdflib.term.Literal``,
        qui seront alors automatiquement converties. Toute tentative pour 
        définir une transformation autre que celles listées ci-avant sera
        silencieusement ignorée.
        
        """
        if isinstance(self.parent, GroupOfValuesKey):
            return self.parent.transform
        return self._transform
    
    @transform.setter
    def transform(self, value):
        if not isinstance(self.parent, GroupOfValuesKey):
            if isinstance(value, Literal):
                value = str(value)
            if not value in (None, 'email', 'phone'):
                return
            self._transform = value   
    
    @property
    def sources(self):
        """list(rdflib.term.URIRef): Liste de sources de la clé.
        
        Notes
        -----
        Si la clé appartient à un groupe de valeurs ou de traduction,
        la propriété du groupe parent est renvoyée. Tenter d'en modifier
        la valeur n'aura silencieusement aucun effet.
        
        Modifier cette propriété emporte la mise en cohérence de la propriété
        :py:attr:`ValueKey.value_source`.
        
        """
        if isinstance(self.parent, GroupOfValuesKey):
            return self.parent.sources
        return self._sources
    
    @sources.setter
    def sources(self, value):
        if not isinstance(self.parent, GroupOfValuesKey) \
            and self.sources != value:
            self._sources = value
            WidgetKey.actionsbook.sources.append(self)
            if not self._is_unborn and self.value_source:
                # pour le cas où value_source ne serait plus
                # une source autorisée.
                self.value_source = self.value_source
    
    @property
    def available_languages(self):
        """list(str): Renvoie la liste des langues disponibles pour la clé.
        
        Notes
        -----
        Cette propriété est en lecture seule. Si la clé appartient à un
        groupe de traduction, la méthode va chercher la liste définie sur la clé
        parente. Sinon elle renvoie :py:attr:`WdigetKey.langlist`, ou ``None``
        si le type de valeur ne suppose pas de langue.
        
        """
        if isinstance(self.parent, TranslationGroupKey):
            return self.parent.available_languages
        elif self.datatype == RDF.langString:
            return WidgetKey.langlist

    @property
    def units(self):
        """list(str): Renvoie la liste des unités possibles pour la clé.
        
        Notes
        -----
        Les valeurs dépendent du type - :py:attr:`ValueKey.datatype`.
        Pour l'heure, seul ``xsd:duration`` suppose des unités, la
        propriété renverra ``None`` pour les valeurs non littérales
        ou de tout autre type.
        
        """
        if self.datatype == XSD.duration:
            return ['ans', 'mois', 'jours', 'heures', 'min.', 'sec.']

    def _hide_m(self, value, rec=False):
        if rec and value and self.m_twin and not self.is_main_twin:
            return
        super()._hide_m(value, rec=rec)

    @property
    def attr_to_update(self):
        """list(str): Liste des attributs et propriétés pouvant être redéfinis post initialisation.
        
        Notes
        -----
        Réécriture de la propriété :py:attr:`WidgetKey.attr_to_update`.
        
        """
        return ['order_idx', 'predicate', 'label', 'description', 'is_hidden_m',
            'rowspan', 'value', 'rdfclass', 'datatype', 'placeholder',
            'input_mask', 'is_mandatory', 'is_read_only', 'regex_validator', 
            'regex_validator_flags', 'value_language', 'value_source',
            'do_not_save', 'is_long_text', 'transform', 'sources', 'independant_label',
            'value_unit', 'geo_tools', 'compute', 'compute_params']

    @property
    def attr_to_copy(self):
        """dict: Attributs de la classe à prendre en compte pour la copie des clés.
        
        Cette propriété est un dictionnaire dont les clés sont les
        noms des attributs contenant les informations nécessaires pour
        dupliquer la clé, et les valeurs sont des booléens qui indiquent
        si l'attribut est à prendre en compte lorsqu'il s'agit de
        créer une copie vide de la clé.
        
        Certains attributs sont volontairement exclus de cette liste, car
        ils requièrent un traitement spécifique.
        
        See Also
        --------
        WidgetKey.copy
        
        Notes
        -----
        Réécriture de la propriété :py:attr:`WidgetKey.attr_to_copy`.
        
        """
        return { 'order_idx': True, 'parent': True, 'predicate': True,
            'label': True, 'description': True, 'do_not_save': True,
            'sources': True, 'rdfclass': True, 'datatype': True, 'transform': True,
            'rowspan': True, 'value': False, 'value_language': False,
            'value_source': False, 'placeholder': True, 'input_mask': True,
            'is_mandatory': True, 'is_read_only': True, 'regex_validator': True,
            'regex_validator_flags': True, 'is_long_text': True,
            'independant_label': True, 'value_unit': False, 'geo_tools': True,
            'compute': True, 'compute_params': True }

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
            dans un groupe de valeurs ou de traduction) - ``True`` - ou
            souhaite-t-on dupliquer une branche de l'arbre de clés
            en préservant son contenu - ``False`` ?
        
        Returns
        -------
        ValueKey
        
        Raises
        ------
        ForbiddenOperation
            Lorsque la méthode est explicitement appliquée à une clé
            fantôme. Il est possible de copier des branches contenant
            des fantômes, ceux-ci ne seront simplement pas copiés.
        
        Notes
        -----
        Complète la méthode :py:meth:`WidgetKey.copy` en gérant le
        cas d'une clé jumelle. Concrètement, c'est alors la clé groupe de
        propriétés du couple qui est copiée (:py:meth:`GroupOfPropertiesKey.copy`
        porte le mécanisme de copie des couples), et la méthode renvoie 
        ensuite sa jumelle.
        
        """
        if self.m_twin:
            groupkey = self.m_twin.copy(parent=parent, empty=empty)
            return groupkey.m_twin
        else:
            return super().copy(parent=parent, empty=empty)

    def change_language(self, value_language, append_book=False):
        """Change la langue d'une clé-valeur.
        
        Utiliser cette méthode sur une clé non visible n'a pas d'effet,
        et le carnet d'actions renvoyé est vide.
        
        Parameters
        ----------
        value_language : str
            La nouvelle langue à déclarer.
        append_book : bool, default False
            Si ``True``, le carnet d'action n'est pas réinitialisé
            avant exécution, mais complété avec les nouvelles
            opérations réalisées.
        
        Returns
        -------
        plume.rdf.actionsbook.ActionsBook
            Le carnet d'actions qui permettra de répercuter le changement
            de langue sur les widgets.
        
        """
        if self.is_hidden:
            return ActionsBook()
        if not append_book:
            WidgetKey.clear_actionsbook()
        self.value_language = value_language
        return WidgetKey.unload_actionsbook(preserve_book=append_book)
    
    def change_source(self, value_source, append_book=False):
        """Change la source d'une clé-valeur.
        
        Utiliser cette méthode sur une clé non visible n'a pas d'effet,
        et le carnet d'actions renvoyé est vide.
        
        Parameters
        ----------
        value_source : rdflib.term.URIRef
            La nouvelle source à déclarer.
        append_book : bool, default False
            Si ``True``, le carnet d'action n'est pas réinitialisé
            avant exécution, mais complété avec les nouvelles
            opérations réalisées.
        
        Returns
        -------
        plume.rdf.actionsbook.ActionsBook
            Le carnet d'actions qui permettra de répercuter le changement
            de source sur les widgets.
        
        """
        if self.is_hidden:
            return ActionsBook()
        if not append_book:
            WidgetKey.clear_actionsbook()
        self.value_source = value_source
        return WidgetKey.unload_actionsbook(preserve_book=append_book)

    def change_unit(self, value_unit, append_book=False):
        """Change l'unité d'une clé-valeur.
        
        Utiliser cette méthode sur une clé non visible n'a pas d'effet,
        et le carnet d'actions renvoyé est vide.
        
        Parameters
        ----------
        value_unit : str
            La nouvelle unité à déclarer.
        append_book : bool, default False
            Si ``True``, le carnet d'action n'est pas réinitialisé
            avant exécution, mais complété avec les nouvelles
            opérations réalisées.
        
        Returns
        -------
        plume.rdf.actionsbook.ActionsBook
            Le carnet d'actions qui permettra de répercuter le changement
            d'unité sur les widgets.
        
        """
        if self.is_hidden:
            return ActionsBook()
        if not append_book:
            WidgetKey.clear_actionsbook()
        self.value_unit = value_unit
        return WidgetKey.unload_actionsbook(preserve_book=append_book)

    def _build_metagraph(self, metagraph):
        if self.do_not_save or self.is_hidden_m or self.value is None:
            # les clés fantôme sont sauvegardées (elles servent
            # à ça), mais pas les clés masquées
            return False
        metagraph.add((self.parent.node, self.predicate, self.value))
        return True

class PlusButtonKey(WidgetKey):
    """Bouton plus.
    
    Les boutons plus sont des clés de dictionnaire de widgets à visée
    utilitaire. Ils n'existent que dans les groupes de valeurs et leur
    présence signifie que l'utilisateur est autorisé à ajouter de
    nouveaux éléments au groupe.
    
    Il ne peut pas y avoir de bouton plus fantôme, de bouton plus dans un
    groupe fantôme, de bouton plus sans parent, ou de bouton plus dont le
    parent n'est pas un groupe valeurs ou de traduction. Dans 
    tous ces cas, rien ne sera créé.
    
    Les boutons héritent des attributs et méthodes de la classe
    `WidgetKey`.
    
    Parameters
    ----------
    parent : GroupKey
        La clé parente. Ne peut pas être ``None``.
    is_ghost : bool, default False
        ``True`` si la clé ne doit pas être matérialisée. À noter que quelle
        que soit la valeur fournie à l'initialisation, une fille de clé
        fantôme est toujours un fantôme. Tenter de créer un bouton plus
        fantôme ne produira rien.
    
    """
    
    def __new__(cls, **kwargs):
        parent = kwargs.get('parent')
        if kwargs.get('is_ghost', False) or not parent \
            or not isinstance(parent, GroupOfValuesKey):
            return
        return super().__new__(cls)

    @property
    def key_object(self):
        """str: Transcription littérale du type de clé.
        
        """
        return 'plus button'
        
    def _validate_parent(self, parent):
        return type(parent) == GroupOfValuesKey
        
    def _register(self, parent):
        parent.button = self
    
    @property
    def tree_idx(self):
        """tuple: Représentation du placement de la clé dans l'arbre.
        
        """
        l = list(self.parent.tree_idx)
        l.append(len(self.parent.children) + 1)
        return tuple(l)
    
    @property
    def description(self):
        """str: Texte d'aide.
        
        """
        return 'Ajouter un élément « {} ».'.format(self.parent.label)
    
    @property
    def path(self):
        """rdflib.paths.SequencePath: Chemin du bouton.
        
        Notes
        -----
        Cette propriété est en lecture seule. Le chemin d'un bouton
        est simplement celui de son groupe parent.
        
        """
        return self.parent.path
    
    @property
    def is_hidden_b(self):
        """bool: La clé est-elle un bouton masqué ?
        
        Un bouton plus est toujours masqué dans un groupe de valeurs
        en lecture seule.
        
        Notes
        -----
        Réécriture de la propriété :py:attr:`WidgetKey.is_hidden_b`.
        
        See Also
        --------
        TranslationButtonKey.is_hidden_b :
            Réécriture de la propriété pour un bouton de traduction.

        """
        return self.parent.is_read_only

    @property
    def placement(self):
        """tuple(int): Placement du widget principal de la clé dans la grille, le cas échéant.
        
        Cette propriété est un tuple formé de quatre éléments :
        
        * ``[0]`` est l'indice de ligne.
        * ``[1]`` est l'indice de colonne.
        * ``[2]`` est le nombre de lignes occupées.
        * ``[3]`` est le nombre de colonnes occupées.
        
        Elle vaut ``None`` pour une clé fantôme, un onglet ou une clé-racine.
        
        Notes
        -----
        Réécriture de la propriété :py:attr:`WidgetKey.placement`.
        Les boutons plus sont toujours placés en colonne 0 et
        occupent une seule colonne.
        
        """
        return (self.row, 0, self.rowspan, WidgetKey.width('plus button')) \
            if self else None
    
    def kill(self):
        """Efface une clé bouton de la mémoire de son parent.
        
        Notes
        -----
        Réécrit :py:meth:`WidgetKey.kill` pour l'adapter au cas
        des boutons. Dans l'absolu, elle n'est pas supposée
        servir, car aucun mécanisme ne prévoit de supprimer le
        bouton d'un groupe sans supprimer également celui-ci.
        
        """
        self.parent.button = None

    def add(self, append_book=False):
        """Ajoute une clé vierge dans le groupe parent du bouton.
        
        Parameters
        ----------
        append_book : bool, default False
            Si ``True``, le carnet d'action n'est pas réinitialisé
            avant exécution, mais complété avec les nouvelles
            opérations réalisées.
        
        Returns
        -------
        plume.rdf.actionsbook.ActionsBook
            Le carnet d'actions qui permettra de matérialiser
            la création de la clé.
        
        """
        if not append_book:
            WidgetKey.clear_actionsbook()
        for child in self.parent.real_children():
            child.copy(parent=self.parent, empty=True)
            break
        return WidgetKey.unload_actionsbook(preserve_book=append_book)
    

class TranslationButtonKey(PlusButtonKey):
    """Bouton de traduction.
    
    Un bouton de traduction est l'équivalent d'un bouton plus, mais dont
    le parent est un groupe de traduction. Sa présence indique que
    l'utilisateur est autorisé à ajouter de nouvelles traductions.
    
    En cas de tentative de création d'un bouton de traduction dans
    un groupe de valeurs, c'est un bouton plus qui est créé à la place.
    
    Les boutons héritent des attributs et méthodes de la classe
    `WidgetKey`. Ils n'ont pas d'attributs propres.
    
    Parameters
    ----------
    parent : GroupKey
        La clé parente. Ne peut pas être ``None``.
    is_ghost : bool, default False
        ``True`` si la clé ne doit pas être matérialisée. À noter que quelle
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
    def key_object(self):
        """str: Transcription littérale du type de clé.
        
        """
        return 'translation button'
    
    @property
    def description(self):
        """str: Texte d'aide.
        
        """
        return 'Ajouter une traduction.'
    
    @property
    def is_hidden_b(self):
        """bool: La clé est-elle un bouton masqué ?
        
        Un bouton de traduction est masqué lorsque le stock
        de langues disponibles pour les traductions est épuisé.
        
        Notes
        -----
        Réécriture de la propriété :py:attr:`WidgetKey.is_hidden_b`.

        Cette propriété est en lecture seule. Elle est déduite dynamiquement
        de la propriété :py:attr:`TranslationGroupKey.available_languages`
        du groupe parent.
        
        """
        return self.parent.is_read_only or not self.parent.available_languages

    def _validate_parent(self, parent):
        return isinstance(parent, TranslationGroupKey)


class RootKey(GroupKey):
    """Clé-racine du graphe RDF.
    
    Une clé-racine est, comme son nom l'indique, l'origine d'un arbre
    de clés, et donc la seule clé de l'arbre qui n'ait pas de parent.
    Elle porte l'identifiant du jeu de données, dans son attribut
    :py:attr:`RootKey.node`.
    
    Outre ses attributs propres listés ci-après, `RootKey` hérite
    des attributs de la classe `GroupKey`.
    
    Parameters
    ----------
    datasetid : rdflib.term.URIRef, optional
        L'identifiant du graphe de métadonnées. S'il n'est pas fourni
        un nouvel UUID est généré pour l'attribut :py:attr:`RootKey.node`.
    
    Notes
    -----
    Une clé-racine n'est jamais un fantôme, et toute tentative
    dans ce sens serait ignorée.
    
    """
    def _heritage(self, **kwargs):
        return
    
    def _base_attributes(self, **kwargs):
        self._node = None
        self._is_hidden_m = False
        self._is_hidden_b = False
        self._rowspan = 0
        self._row = None
        self.children = ChildrenList()
 
    def _computed_attributes(self, **kwargs):
        self.node = kwargs.get('datasetid')
 
    @property
    def generation(self):
        """int: Génération à laquelle appartient la clé.
        
        ``0`` pour la clé-racine, ``1`` pour ses enfants, etc.
        
        """
        return 0
 
    @property
    def node(self):
        """rdflib.term.URIRef: Identifiant du jeu de données.
        
        Notes
        -----
        Si la valeur fournie n'est pas un IRI, un nouvel identifiant
        (UUID) est généré.
        
        """
        return self._node
    
    @node.setter
    def node(self, value):
        # NB: on pourrait juste écrire self._node = DatasetId(value)
        # pour s'assurer d'avoir un identifiant valide. Mais cela
        # empêcherait d'extraire les informations de graphes dont,
        # pour une raison ou une autre, l'identifiant a été corrompu.
        # C'est la fonction d'initialisation de WidgetsDict qui s'assurera
        # de corriger l'identifiant (post extraction des métadonnées).
        if not isinstance(value, URIRef):
            value = DatasetId()
        self._node = value
 
    @property
    def key_object(self):
        """str: Transcription littérale du type de clé.
        
        """
        return 'root'
    
    @property
    def parent(self):
        return
 
    @property
    def is_ghost(self):
        return False
    
    @is_ghost.setter
    def is_ghost(self, value):
        return
 
    @property
    def placement(self):
        return
 
    @property
    def rdfclass(self):
        """rdflib.term.URIRef: Classe RDF.
        
        Notes
        -----
        Vaut toujours ``dcat:Dataset``.
        
        """
        return DCAT.Dataset

    @property
    def tree_idx(self):
        """tuple: Représentation du placement de la clé dans l'arbre.
        
        """
        return (0,)

    @property
    def attr_to_copy(self):
        return {}

    @property
    def attr_to_update(self):
        return []

    def kill(self):
        return

    def search_from_path(self, path, allow_ghosts=False):
        """Renvoie la première clé de l'arbre dont le chemin correspond à celui recherché.
        
        Si une clé et son parent ont le même chemin (cas d'un groupe
        de valeurs et ses clés filles, ou d'un groupe de propriétés
        et ses onglets), c'est toujours le groupe parent qui est
        renvoyé.
        
        Si le chemin pointe sur un couple de jumelles, c'est la jumelle
        de référence (celle dont la propriété :py:attr:`ObjectKey.is_main_twin`
        vaut ``True``) qui est renvoyée.
        
        Si le chemin n'existe pas dans l'arbre, la méthode ne renvoie
        rien. Les clés fantômes ne sont pas prises en compte, sauf si
        le paramètre `allow_ghosts` est explicitement mis à ``True``.
        
        Parameters
        ----------
        path : rdflib.paths.SequencePath
            Le chemin à chercher.
        allow_ghosts : bool, default False
            Si ``True``, les clés fantômes seront prises en compte.
        
        Returns
        -------
        WidgetKey
        
        """
        return self._search_from_path(path, allow_ghosts=allow_ghosts)

    def search_from_rdfclass(self, rdfclass):
        """Renvoie la liste des groupes de propriétés du type recherché.
        
        Les clés fantômes ne sont pas prises en compte.
        
        Parameters
        ----------
        rdfclass : rdflib.term.URIRef
            La classe RDF cible.
            
        Returns
        -------
        list of GroupOfPropertiesKey
        
        """
        matchlist = []
        self._search_from_rdfclass(rdfclass, matchlist)

    def search_from_uuid(self, uuid):
        """Renvoie la clé de l'arbre dont l'identifiant est l'UUID recherché.
        
        Parameters
        ----------
        uuid : str or uuid.UUID
        
        """
        if str(self.uuid) == str(uuid):
            return self
        return self._search_from_uuid(uuid)

    def paste_from_path(self, widgetkey):
        """Copie et colle une branche dans l'arbre de clés.
        
        La clé est positionnée en fonction de son type et de la valeur
        de son attribut :py:attr:`WidgetKey.path`. Si le chemin n'existe
        pas dans l'arbre dont `self` est la racine, la méthode n'a pas
        d'effet. Idem s'il pointe sur une branche masquée.
        
        Si le chemin pointe sur un groupe de valeurs avec un bouton
        (donc dans lequel on présume que les ajouts sont autorisés)
        et que la clé à coller est de classe :py:class:`GroupOfPropertiesKey`,
        elle est ajoutée au groupe. Sinon, la clé à coller remplace
        la clé de même chemin dans l'arbre cible, sous réserve qu'elles
        soient bien de même nature.
        
        Parameters
        ----------
        widgetkey : GroupOfPropertiesKey or GroupOfValuesKey
            La clé correspondant à la base de la branche à copier.
            
        Returns
        -------
        plume.rdf.actionsbook.ActionsBook
            Le carnet d'actions qui permettra de matérialiser les
            opérations réalisées.
        
        Raises
        ------
        ForbiddenOperation
            Si appliquée à une clé qui n'est pas un groupe de valeurs
            ou de propriétés, ou à une clé fantôme ou masquée.
        
        """
        if widgetkey.is_hidden:
            raise ForbiddenOperation("Il n'est pas permis de " \
                'copier/coller une branche fantôme ou masquée.', self)
        if not isinstance(widgetkey, (GroupOfPropertiesKey, GroupOfValuesKey)):
            raise ForbiddenOperation('Seuls les groupes de valeurs, de ' \
                'traduction ou de propriétés peuvent être copiés/collés.',
                self)
        WidgetKey.clear_actionsbook()
        refkey = self.search_from_path(widgetkey.path)
        if not refkey or refkey.is_hidden:
            return ActionsBook()
        if type(refkey) == type(widgetkey):
            refkey.kill()
            widgetkey.copy(parent=refkey.parent, empty=False)  
        elif isinstance(widgetkey, GroupOfPropertiesKey) and \
            isinstance(refkey, GroupOfValuesKey) and refkey.button \
            and not refkey.button.is_hidden:
            widgetkey.copy(parent=refkey, empty=False)
        return WidgetKey.unload_actionsbook()

    def clean(self):
        """Balaie l'arbre de clés et supprime tous les groupes sans fille.
        
        Les groupes qui ne contiennent que des fantômes sont transformés
        en fantômes, s'ils ne l'étaient pas déjà (sous réserve des
        contraintes exprimées dans les descriptifs des propriétés
        :py:attr:`GroupOfPropertiesKey.is_ghost`, :py:attr:`TabKey.is_ghost`
        et :py:attr:`GroupOfValuesKey.is_ghost`).
        
        Cette méthode a la spécificité de pouvoir supprimer
        une clé tout en préservant sa jumelle clé-valeur (qui
        n'est alors plus une clé jumelle). Outre le cas des jumelles
        supprimées parce que ce sont des groupes de propriétés
        vides, la méthode élimine les clés qui ne sont pas la
        jumelle principale lorsqu'il n'y a pas de bouton de sélection
        de la source qui permettraient de les afficher.
        
        Returns
        -------
        plume.rdf.actionsbook.ActionsBook
            Le carnet d'actions qui permettra de matérialiser les
            opérations réalisées.
        
        Notes
        -----
        Les suppressions et les fantômisations se traduisent par
        des entrées dans la liste :py:attr:`ActionsBook.drop`
        du carnet d'actions.
        
        """
        WidgetKey.clear_actionsbook(allow_ghosts=True)
        self._clean()
        return WidgetKey.unload_actionsbook()

    def build_metagraph(self):
        """Traduit l'arbre de clés en graphe de métadonnées.
        
        Returns
        -------
        plume.rdf.metagraph.Metagraph
        
        """
        metagraph = Metagraph()
        metagraph.add((self.node, RDF.type, self.rdfclass))
        self._build_metagraph(metagraph)
        return metagraph

    def tree_keys(self):
        """Générateur sur les clés de l'arbre.
        
        Les fantômes sont exclus, les boutons sont inclus.
        
        Yields
        ------
        WidgetKey
        
        """
        yield from self._tree_keys()

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



