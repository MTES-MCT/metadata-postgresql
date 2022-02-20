"""Dictionnaires internes des dictionnaires de widgets.

"""

class InternalDict(dict):
    """Dictionnaires interne.
    
    Un dictionnaire interne est un dictionnaire comportant les clés listées ci-après. Les
    valeurs des dictionnaires de widgets (:py:class:`plume.rdf.widgetsdict.WidgetsDict`) sont
    des dictionnaires internes. Un dictionnaire interne traduit les attributs des clés
    du dictionnaire de widgets sous une forme plus aisément exploitable pour construire un
    formulaire avec les bibliothèques QT. Il a également pour fonction de référencer les widgets
    et autres objets QT qui constituent le formulaire, afin de pouvoir les modifier d'autant que
    de besoin à mesure des actions de l'utilisateur.
    
    À l'initialisation, toutes les clés du dictionnaire interne ont pour valeur ``None``.
    Elles doivent être calculées avant la création des widgets avec la méthode
    :py:meth:`plume.rdf.widgetsdict.WidgetsDict.internalize`, et recalculées par le
    même moyen à chaque fois que la clé du dictionnaire de widgets qui porte le dictionnaire
    interne est modifiée.
        
    * ``object`` : classification par nature des éléments du dictionnaire. L'objet est une
      chaîne de caractères pouvant prendre les valeurs :
      * ``'group of values'`` pour un groupe de valeurs,
      * ``'group of properties'`` pour un groupe de propriétés,
      * ``'translation group'`` pour un groupe de traduction,
      * ``'edit'`` pour un widget de saisie,
      * ``'plus button'`` pour un bouton plus,
      * ``'translation button'`` pour un bouton de traduction.
    * ``main widget type`` est le type du widget principal de la clé (``'QGroupBox'``,
      ``'QLineEdit'``...). Si ``None`` (clé dite "fantôme), aucun widget ne doit être créé.
      Ce cas correspond aux catégories de métadonnées dont le modèle couramment utilisé ne
      prévoit pas l'affichage, mais dont il n'est pas question de perdre les valeurs.

    Les clés ``... widget`` ci-après ont vocation à accueillir les futurs widgets.
    
    * ``main widget`` : widget principal.
    * ``grid widget`` : widget annexe de type ``QGridLayout``, à créer dès lors que le widget
      principal est de type ``'QGroupBox'``.
    * ``label widget`` : widget annexe de type ``QLabel`` portant une étiquette qui fournit le
      libellé de la catégorie de métadonnée. À créer lorsque la valeur de ``has label`` est
      ``True``. Le libellé à afficher est la valeur de ``label``.
    * ``minus widget`` :  widget annexe de type ``QToolButton`` permettant à l'utilisateur
      de supprimer le widget. À créer lorsque la valeur de ``has minus button`` est ``True``.
    * ``language widget`` : widget annexe de type ``QToolButton`` permettant à l'utilisateur
      de spécifier la langue du texte qu'il saisit. À créer lorsque la valeur de
      ``authorized languages`` n'est pas ``None``.
    * ``switch source widget`` : widget annexe de type ``QToolButton`` permettant à l'utilisateur
      de spécifier le thésaurus qu'il veut utiliser, lorsque plusieurs sont disponibles, ou
      de passer en mode manuel (saisie manuelle des propriétés de l'objet, au lieu de la simple
      sélection de son IRI dans un thésaurus). À créer lorsque la valeur de ``multiple sources``
      est ``True``.
    * ``unit widget`` : widget annexe de type ``QToolButton`` permettant à l'utilisateur
      de choisir l'unité de la valeur qu'il est en train de saisir. À créer lorsque la
      valeur de la clé ``units`` n'est pas ``None``.
    * ``geo widget`` : widget annexe de type ``QToolButton`` proposant des fonctionnalités
      d'aide à la saisie des géométries. À créer lorsque la valeur de la clé ``geo tools``
      n'est pas ``None``.
    * ``compute widget`` : widget annexe de type ``QToolButton`` permettant à l'utilisateur
      de mettre à jour la métadonnée par un calcul plutôt que par saisie manuelle. À créer
      lorsque ``has compute button`` vaut ``True``.
    
    En complément, des clés sont prévues pour les ``QMenu`` et ``QAction`` associés à certains
    widgets boutons.
    
    * ``switch source menu`` : pour le ``QMenu`` associé au widget référencé par 
      ``switch source widget``. Ce menu présente une liste de sources (cf. ``sources``),
      dont une est sélectionnée (cf. ``current source``).
    * ``switch source actions`` : liste des ``QAction`` du ``switch source menu``.
    * ``language menu`` : pour le ``QMenu`` associé au widget référencé par
      ``language widget``. Ce menu présente une liste de langues (cf. ``authorized languages``),
      dont une est sélectionnée (cf. ``language value``), il permet à l'utilisateur de
      spécifier la langue du texte qu'il est en train de saisir.
    * ``language actions`` : liste des ``QAction`` du ``language menu``.
    * ``unit menu`` : pour le ``QMenu`` associé au widget référencé par ``unit widget``.
      Ce menu présente une liste d'unités disponibles (cf. ``units``), dont une est
      sélectionnée (cf. ``current unit``).
    * ``unit actions`` : liste des ``QAction`` du ``unit menu``.
    * ``geo menu`` : pour le ``QMenu`` associé au widget référencé par ``geo widget``.
      Ce menu présente une liste fixe d'actions possibles.
    * ``geo actions`` : liste des ``QAction`` du ``geo menu``. 

    Les clés suivantes contiennent les informations nécessaires au paramétrage des widgets.
    
    * ``hidden`` : booléen. Si ``True``, le widget principal et tous les widgets annexes doivent
      être masqués.
    * ``label`` : s'il y a lieu de mettre une étiquette, soit intégrée au widget (par exemple
      dans le cas d'un ``QGroupBox``), soit indépendante (cf. ``has label``), le libellé
      que portera ladite étiquette.
    * ``has label`` : ``True`` si un widget ``QLabel`` doit être créé pour porter le libellé
      de la catégorie de métadonnée. Il devra alors être référencé dans ``label widget``.
    * ``help text`` : le cas échéant, texte explicatif à afficher en infobulle.
    * ``value`` : pour un widget de saisie, l'éventuelle valeur à afficher.
    * ``placeholder text`` : le cas échéant, valeur du paramètre ``placeholder`` (texte de
      substitution, qui apparaît tant qu'aucune valeur n'est renseignée) pour le widget principal.
    * ``input mask`` : le cas échéant, valeur du paramètre ``inputMask`` (masque de saisie)
      pour le widget principal.
    * ``is mandatory`` : ``True`` si la métadonnée doit obligatoirement être renseignée.
    * ``read only`` : ``True`` si la métadonnée ne doit pas être modifiable par l'utilisateur,
      ce qui conduira à désactiver le widget de saisie.
    * ``has minus button`` : ``True`` si un widget annexe bouton moins doit être créé. Il sera
      alors référencé dans ``minus widget``.
    * ``hide minus button`` : ``True`` si le widget annexe bouton moins doit être masqué. À noter
      que même si la valeur de cette clé n'est pas ``True``, le bouton moins devra être masqué
      si ``hidden`` vaut ``True``.
    * ``regex validator pattern`` : le cas échéant, éventuelle expression régulière que la
      valeur est censée vérifier. Pour usage par un ``QRegularExpressionValidator``.
    * ``regex validator flags`` : flags associés à ``regex validator pattern``, le cas échéant.
    * ``type validator`` : si un validateur basé sur le type (``QIntValidator`` ou
      ``QDoubleValidator``) doit être utilisé, le nom du validateur.
    * ``multiple sources`` : ``True`` si la métadonnée fait appel à plusieurs thésaurus
      ou autorise à la fois la saisie manuelle et l'usage de thésaurus. Un widget de sélection
      de la source doit alors être créé et référencé dans ``switch source widget``.
    * ``sources`` : s'il y a lieu de créer un widget annexe pour spécifier la source
      (cf. ``multiple sources``), la liste des sources à afficher dans le menu associé
      (``switch source menu``).
    * ``current source`` : s'il y a lieu de créer un widget annexe pour spécifier la source
      (cf. ``multiple sources``), la source qui devra être présentée comme actuellement
      sélectionnée par le menu associé (``switch source menu``).
    * ``thesaurus values`` : le cas échéant, la liste des valeurs à afficher dans le
      widget principal de type ``QComboBox``.
    * ``authorized languages`` : liste des langues à présenter dans le menu associé au
       widget de sélection de la langue (``language menu``), le cas échéant. La non nullité
       de cette clé emporte la création d'un widget de sélection de la langue (``language widget``).
    * ``language value`` : s'il y a lieu de créer un widget annexe pour spécifier la langue
      (cf. ``authorized languages``), la langue qui devra être présentée comme actuellement
      sélectionnée par le menu associé (``language menu``).
    * ``units`` : liste des unités disponibles, à présenter dans le menu associé au widget
      de sélection de l'unité (``unit menu``), le cas échéant. La non nullité de cette clé
      emporte la création d'un widget de sélection de l'unité (``unit widget``).
    * ``current unit`` : s'il y a lieu de créer un widget pour spécifier l'unité (cf. ``units``),
      l'unité qui devra être présentée comme actuellement sélectionné par le menu associé
      (``unit menu``).
    * ``geo tools`` : liste des fonctionnalités d'aide à la saisie des géométries à
      proposer. La non nullité de cette clé emporte la création d'un bouton d'aide
      à la saisie des géométries (``geo widget``) par lequel l'utilisateur accédera
      à ces fonctionnalités.
    * ``has compute button`` : ``True`` si un bouton de calcul de la métadonnée doit être
      créé. Il sera alors référencé dans ``compute widget``.  La méthode de calcul est
      fournie par la clé ``compute method``.
    * ``auto compute`` : ``True`` si la métadonnée doit être calculée automatiquement à
      la création du dictionnaire. La méthode de calcul est fournie par la clé
      ``compute method``.
    * ``compute method`` : un objet :py:class:`plume.pg.computer.ComputeMethod` qui porte
      les informations nécessaires pour exécuter le calcul de la métadonnée.
    
    """
    
    def __init__(self):
        keys = [
            'object', 'main widget type',
            # stockage des widgets :
            'main widget', 'grid widget', 'label widget', 'minus widget',
            'language widget', 'switch source widget', 'unit widget', 'geo widget',
            'compute widget',
            # stockage des menus, actions, etc. :
            'switch source menu', 'switch source actions', 'language menu',
            'language actions', 'unit menu', 'unit actions', 'geo menu', 'geo actions',
            # paramétrage des widgets :
            'hidden', 'label', 'has label', 'help text', 'value', 'placeholder text',
            'input mask', 'is mandatory', 'read only', 'has minus button',
            'hide minus button', 'regex validator pattern', 'regex validator flags',
            'type validator', 'multiple sources', 'sources', 'current source',
            'thesaurus values', 'authorized languages', 'language value', 'units',
            'current unit', 'geo tools', 'has compute button', 'auto compute',
            'compute method'
            ]
        self.update({ k:None for k in keys })

