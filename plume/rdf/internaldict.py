"""Dictionnaires internes des dictionnaires de widgets.

"""

class InternalDict(dict):
    """Classe pour les dictionnaires internes.
    
    Cette classe n'a pas d'attribut.
    
    Un objet de classe `InternalDict`, ou "dictionnaire interne" est un dictionnaire
    comportant les clés listées ci-après. Les valeurs des dictionnaires de widgets
    (`WidgetsDict`) sont des dictionnaires internes.
    
    - 'object' : classification des éléments du dictionnaire. "group of values" ou
    "group of properties" ou "translation group" ou "edit" ou "plus button" ou "translation button".
    Les "translation group" et "translation button" ne peuvent exister que si l'attribut
    "translation" vaut True.

    Les clés 'X widget' ci-après ont vocation à accueillir les futurs widgets (qui ne sont pas
    créés par la fonction). Il y a toujours un widget principal, le plus souvent de type
    QGroupBox ou QXEdit, et éventuellement des widgets secondaires. Tous ont le même parent et
    seraient à afficher sur la même ligne de la grille.
    
    - 'main widget' : widget principal.
    - 'grid widget' : widget de type QGridLayout, à créer pour tous les éléments "group of values",
    "group of properties" et "translation group".
    - 'label widget' : pour certains éléments "edit" (concrètement, tous ceux dont
    la clé "label" ci-après n'est pas vide - pour les autres il y a un "group of values" qui porte
    le label), le widget QLabel associé.
    - 'minus widget' : pour les propriétés qui admettent plusieurs valeurs ou qui, de fait, en ont,
    (concrètement celles pour lesquelles la clé "has minus button" vaut True), widget QButtonTool [-]
    permettant de supprimer les widgets.
    - 'language widget' : pour certains widgets "edit" (concrètement, ceux dont 'authorized languages'
    n'est pas vide), widget pour afficher/sélectionner la langue de la métadonnée. Les 'languages
    widget' n'auront vocation à être affiché que si le mode "traduction" est actif, soit un 
    paramètre 'translation' valant True pour la fonction.
    - 'switch source widget' : certaines catégories de métadonnées peuvent prendre une valeur
    parmi plusieurs thésaurus ou permettre de choisir entre une valeur issue d'un thésaurus et
    une valeur saisie manuellement. Le bouton "switch source widget" est un QButtonTool qui permet
    de sélectionner le thésaurus à utiliser ou de basculer en mode manuel. Il doit être implémenté
    dès lors que la clé 'multiple sources' indique True. Cf. aussi 'sources' et 'current sources'.
    
    Parmi les trois derniers boutons seuls deux au maximum pourront être affichés simultanément,
    la combinaison 'language widget' et 'switch source widget' étant impossible.
    
    En complément, des clés sont prévues pour les QMenu et QAction associés à certains widgets.
    
    - 'switch source menu' : pour le QMenu associé au 'switch source widget'.
    - 'switch source actions' : liste des QAction associées au 'switch source menu'.
    - 'language menu' : pour le QMenu associé au 'language widget'.
    - 'language actions' : liste des QAction associées au 'language menu'.   

    Les clés suivantes sont, elles, remplies par la fonction, avec toutes les informations nécessaires
    au paramétrage des widgets.
    
    - 'main widget type'* : type du widget principal (QGroupBox, QLineEdit...). Si cette clé est
    vide, c'est qu'aucun widget ne doit être créé. Ce cas correspond aux catégories de métadonnées
    hors template, dont les valeurs ne seront pas affichées, mais qu'il n'est pas question d'effacer
    pour autant.
    - 'row' : placement vertical (= numéro de ligne) du widget dans la grille (QGridLayout) qui
    organise tous les widgets rattachés au groupe parent (QGroupBox). Initialement, row est
    toujours égal à l'index de la clé, mais il ne le sera plus si les boutons d'ajout/suppression
    de valeurs ont été utilisés.
    - 'row span'* : hauteur du widget, en nombre de lignes de la grille. Spécifié uniquement pour
    certains QTextEdit (valeur par défaut à prévoir).
    - 'label'* : s'il y a lieu de mettre un label (pour les "group of values" et les "edit" ou "node
    group" qui n'ont pas de "group of values" parent), label intégré au widget QGroupBox ou, pour un
    widget "edit", le label du QLabel associé.
    - 'label row' : pour les widgets QTextEdit ou lorsque le label dépasse la longueur définie par
    l'argument labelLengthLimit, il est considéré que le label sera affiché au-dessus de la zone
    de saisie. Dans ce cas 'label row' contient la valeur à donner au paramètre row. Si cette clé
    est vide alors que 'label' contient une valeur, c'est que le label doit être positionné sur
    la même ligne que le widget principal, et son paramètre row est donc fourni par l'index
    contenu dans la clé du dictionnaire externe.
    - 'help text'* : s'il y a lieu, texte explicatif sur la métadonnée. Pourrait être affiché en
    infobulle.
    - 'value' : pour un widget "edit", la valeur à afficher. Elle tient compte à la fois de ce qui
    était déjà renseigné dans la fiche de métadonnées et des éventuelles valeurs par défaut de shape
    et template. Les valeurs par défaut sont utilisées uniquement dans les groupes de propriétés
    vides.
    - 'placeholder text'* : pour un widget QLineEdit ou QTextEdit, éventuel texte à utiliser comme
    "placeholder".
    - 'input mask'* : éventuel masque de saisie.
    - 'language value' : s'il y a lieu de créer un widget secondaire pour spécifier la langue (cf.
    'language widget'), la langue à afficher dans ce widget. Elle est déduite de la valeur lorsqu'il
    y a une valeur, sinon on utilise la valeur de l'argument language de la fonction.
    - 'authorized languages' : liste des langues disponibles dans le 'language widget', s'il y a
    lieu (cf. 'language widget').
    - 'is mandatory'* : booléen indiquant si la métadonnée doit obligatoirement être renseignée.
    - 'has minus button' : booléen indiquant si un bouton de suppression du widget doit être
    créé (cf. minus widget). Sur le principe, ce sera le cas dès qu'une catégorie admet plusieurs
    valeurs ou traductions, ou qu'il y a effectivement plusieurs valeurs saisies (un bouton pour
    chaque valeur).
    - 'hide minus button' : booléen qui vaudra True si le bouton moins doit être masqué parce
    qu'il ne reste qu'un widget dans le groupe de valeurs ou groupe de traduction.
    - 'regex validator pattern' : pour un widget "edit", une éventuelle expression régulière que la
    valeur est censée vérifier. Pour usage par un QRegularExpressionValidator.
    - 'regex validator flags' : flags associés à 'regex validator pattern', le cas échéant.
    - 'type validator' : si un validateur basé sur le type (QIntValidator ou QDoubleValidator) doit
    être utilisé, le nom du validateur.
    - 'sources' : lorsque la métadonnée prend ses valeurs dans une ou plusieurs ontologies /
    thésaurus, liste des sources. La valeur 'manuel' indique qu'une saisie manuelle est possible
    (uniquement via un widget "M").
    - 'multiple sources' : booléen indiquant que la métadonnée fait appel à plusieurs ontologies
    ou autorise à la fois la saisie manuelle et l'usage d'ontologies.
    - 'current source' spécifie la source en cours d'utilisation. Pour un widget "M", vaut
    toujours "manuel" lorsque le widget est en cours d'utilisation, None sinon). Pour un widget
    non "M", il donne le nom littéral de l'ontologie ou "non répertorié" lorsque la valeur
    antérieurement saisie n'apparaît dans aucune ontologie associée à la catégorie, None si le
    widget n'est pas utilisé. La liste des termes autorisés par la source n'est pas directement
    stockée dans le dictionnaire, mais peut être obtenue via la fonction build_vocabulary.
    - 'thesaurus values' : le cas échéant, la liste des valeurs à afficher dans le QComboBox.
    - 'read only'* : booléen qui vaudra True si la métadonnée ne doit pas être modifiable par
    l'utilisateur. En mode lecture, 'read only' vaut toujours True.
    - 'hidden' : booléen. Si True, le widget principal doit être masqué. Concerne
    les boutons de traduction, lorsque toutes les langues disponibles (cf. langList) ont été
    utilisées.
    - 'hidden M' : booléen. Si True, le widget principal doit être masqué. Concerne les branches
    M/non M (qui permettent de saisir une métadonnées soit sous forme d'IRI soit sous forme d'un
    ensemble de propriétés littérales) lorsque l'autre forme est utilisée.

    La dernière série de clés ne sert qu'aux fonctions de rdf_utils : 'default value'* (valeur par
    défaut), 'node kind', 'data type'**, 'class', 'path'***, 'subject', 'predicate', 'node',
    'transform', 'default widget type', 'one per language', 'next child' (indice à utiliser si un
    enregistrement est ajouté au groupe), 'multiple values'* (la catégorie est-elle
    censée admettre plusieurs valeurs ?), 'order shape', 'order template'* (ordre des catégories, cette
    clé s'appelle simplement "order" dans le template), 'do not save', 'sources URI', 'default source',
    'independant label'.

    * ces clés apparaissent aussi dans le dictionnaire interne de template.
    ** le dictionnaire interne de template contient également une clé 'data type', mais dont les
    valeurs sont des chaînes de catactères parmi 'string', 'boolean', 'decimal', 'integer', 'date',
    'time', 'dateTime', 'duration', 'float', 'double' (et non des objets de type URIRef).
    *** le chemin est la clé principale de template.
    """
    
    def __init__(self):
        """Génère un dictionnaire interne vierge.
        
        Returns
        -------
        InternalDict
            Un dictionnaire interne vide.
        """
        
        keys = [
            'object',
            # stockage des widgets :
            'main widget', 'grid widget', 'label widget', 'minus widget',
            'language widget', 'switch source widget',
            'switch source menu', 'switch source actions', 'language menu',
            'language actions',
            # paramétrage des widgets
            'main widget type', 'row', 'row span', 'label', 'label row',
            'help text', 'value', 'language value', 'placeholder text',
            'input mask', 'is mandatory', 'has minus button', 'hide minus button',
            'regex validator pattern', 'regex validator flags', 'type validator',
            'multiple sources', 'sources', 'current source', 'current source URI',
            'thesaurus values', 'authorized languages', 'read only', 'hidden', 'hidden M',
            # à l'usage des fonctions de rdf_utils
            'default value', 'default source', 'multiple values', 'node kind',
            'data type', 'ontology', 'transform', 'class', 'path', 'subject',
            'predicate', 'node', 'default widget type', 'one per language',
            'next child', 'shape order', 'template order', 'do not save',
            'sources URI', 'independant label'
            ]
        
        self.update({ k:None for k in keys })

