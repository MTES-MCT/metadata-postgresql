"""
Utilitary functions for parsing and serializing RDF metadata.

Les fonctions suivantes permettent :
- d'extraire des métadonnées en JSON-LD d'une chaîne de
caractères balisée et les désérialiser sous la forme d'un
graphe ;
- de traduire ce graphe en un dictionnaire de catégories
de métadonnées qui pourra alimenter un formulaire ;
- en retour, de reconstruire un graphe à partir d'un
dictionnaire de métadonnées ;
- de sérialiser ce graphe en JSON-LD et l'inclure dans
une chaîne de caractères balisée.

Dépendances : rdflib, rdflib-jsonld et requests.
"""

from rdflib import Graph, Namespace, Literal, BNode, URIRef
from rdflib.namespace import NamespaceManager
from rdflib.serializer import Serializer
from locale import strxfrm, setlocale, LC_COLLATE
from typing import Union, Dict, List, Tuple
import re, uuid

# NB : pour les annotations, à partir de python 3.9, on devrait écrire
# dict[str, Namespace] au lieu de Dict[str, Namespace] et
# idem pour list/List et tuple/Tuple, puisqu'il est désormais
# possible de spécifier directement les types génériques. La forme
# ancienne est conservée à ce stade, car les versions de QGIS déployées
# à cette heure ne sont pas sous python 3.9.


    
    
def buildGraph(widgetsDict: dict, vocabulary: Graph, language: str = "fr") -> Graph:
    """Return a RDF graph build from given dictionary.

    Arguments :
    - widgetsDict est un dictionnaire produit par la fonction buildDict (lancée
    en mode 'edit') et modifié par les actions de l'utilisateur.
    - vocabulary est un graphe réunissant le vocabulaire de toutes les ontologies
    pertinentes.
    - language (paramètre utilisateur, en l'état où il se trouve à l'issue de la
    saisie) est la langue principale de rédaction des métadonnées.

    Résultat : un graphe RDF de métadonnées.
    """

    graph = Graph()
    mem = None
    
    for k, d in widgetsDict.items():
    
        mObject = None
        
        # cas d'un nouveau noeud
        if d['node']:
        
            mem = (d['subject'], d['predicate'], d['node'], d['class'])
            # on mémorise les informations utiles, mais le noeud
            # n'est pas immédiatement créé, au cas où il n'y aurait
            # pas de métadonnées associées
            
            
        elif d['value'] in [None, '']:
            continue
                
        else:
        
            if mem and mem[2] == d['subject']:
            
                # création effective du noeud vide à partir
                # des informations mémorisées
                graph.update("""
                    INSERT
                        { ?s ?p ?n .
                          ?n a ?c }
                    WHERE
                        { }
                """,
                initBindings = {
                    's' : mem[0],
                    'p' : mem[1],
                    'n' : mem[2],
                    'c' : mem[3]
                    }
                )
                
                mem = None
        
            if d['node kind'] == 'sh:Literal':
        
                mObject = Literal( d['value'], datatype = d['data type'] ) \
                            if not d['data type'] == URIRef("http://www.w3.org/2001/XMLSchema#string") \
                            else Literal( d['value'], lang = d['language value'] )
                            
            else:
    
                if d['transform'] == 'email':
                    mObject = owlThingFromEmail(d['value'])
                    
                elif d['transform'] == 'phone':
                    mObject = owlThingFromTel(d['value']) 
                    
                elif d['current source']:
                    c = getConceptFromValue(d['value'], d['current source'], vocabulary, language)
                    
                    if c is None:
                        raise ValueError( "'{}' isn't referenced as a label in scheme '{}' for language '{}'.".format(
                            d['value'], d['current source'], language )
                            ) 
                    else:
                        mObject = c[0]
                    
                else:
                    f = forbiddenChar(d['value'])                
                    if f:
                        raise ValueError( "Character '{}' is not allowed in ressource identifiers.".format(f) )
                        
                    mObject = URIRef( d['value'] )
            
            graph.update("""
                INSERT
                    { ?s ?p ?o }
                WHERE
                    { }
            """,
            initBindings = { 's' : d['subject'], 'p' : d['predicate'], 'o' : mObject }
            )  

    return graph




def buildDict(
    graph: Graph,
    shape: Graph,
    vocabulary: Graph,
    template: dict = None,
    mode: str = 'edit',
    readHideBlank: bool = True,
    hideUnlisted: bool = False,
    language: str = "fr",
    translation: bool = False,
    langList: List[str] = ['fr', 'en'],
    labelLengthLimit: int = 25,
    valueLengthLimit: int = 100,
    textEditRowSpan: int = 6,
    mPath: str = None,
    mTargetClass: URIRef = None,
    mParentWidget: tuple = None,
    mParentNode: Union[URIRef, BNode] = None,
    mNSManager : NamespaceManager = None,
    mWidgetDictTemplate : dict = None,
    mDict: dict = None,
    mGraphEmpty: bool = None,
    mShallowTemplate: dict = None,
    mTemplateEmpty: bool = None,
    mHidden: bool = None
    ) -> dict:
    """Return a dictionary with relevant informations to build a metadata update form. 

    Arguments :
    - graph est un graphe RDF contenant les métadonnées associées à un jeu de données.
    Elles serviront à initialiser le formulaire de saisie.
    - shape est un schéma SHACL augmenté décrivant les catégories de métadonnées communes.
    - template est un dictionnaire contenant les informations relatives au modèle
    de formulaire à utiliser. Fournir un template permet : d'ajouter des métadonnées
    locales aux catégories communes définies dans shape ; de restreindre les catégories
    communes à afficher ; de substituer des paramètres locaux à ceux spécifiés par shape
    (par exemple remplacer le nom à afficher pour la catégorie de métadonnée ou changer
    le type de widget à utiliser). La forme de template est proche de celle du
    dictionnaire résultant de la présente fonction (cf. plus loin) si ce n'est que ses
    clés sont des chemins SPARQL identifiant des catégories de métadonnées et ses
    dictionnaires internes ne comprennent que les clés marquées d'astéristiques. Certains
    caractéristiques ne peuvent être définies que pour les catégories de métadonnées
    locales : il n'est pas possible de changer 'data type' ni 'multiple values' pour une
    catégorie commune.
    - vocabulary est un graphe réunissant le vocabulaire de toutes les ontologies
    pertinentes.
    - mode indique si le formulaire est ouvert pour édition ('edit'), en lecture ('read')
    ou pour lancer une recherche ('search'). Le principal effet du mode lecture est la
    disparition des boutons, notamment les "boutons plus" qui faisaient l'objet d'un
    enregistrement à part dans le dictionnaire. [ATTENTION !!! le mode recherche n'est pas
    encore implémenté, il renvoie le même dictionnaire que le mode lecture]
    - readHideBlank (paramètre utilisateur) indique si les champs vides doivent être masqués
    en mode lecture.
    - hideUnlisted (paramètre utilisateur) indique si les catégories hors template doivent
    être masquées. En l'absence de template, si hideUnlisted vaut True, seules les métadonnées
    communes seront visibles.
    - language (paramètre utilisateur) est la langue principale de rédaction des métadonnées.
    Français ("fr") par défaut. La valeur de language doit être incluse dans langList ci-après.
    - translation (paramètre utilisateur) est un booléen qui indique si les widgets de
    traduction doivent être affichés. False par défaut.
    - langList est la liste des langues autorisées pour les traductions, par défaut
    français et anglais.
    - labelLengthLimit est le nombre de caractères au-delà duquel le label sera
    toujours affiché au-dessus du widget de saisie et non sur la même ligne. À noter que
    pour les widgets QTextEdit le label est placé au-dessus quoi qu'il arrive.
    - valueLengthLimit est le nombre de caractères au-delà duquel une valeur qui aurait
    dû être affichée dans un widget QLineEdit sera présentée à la place dans un QTextEdit.
    Indépendemment du nombre de catactères, la substitution sera aussi réalisée si la
    valeur contient un retour à la ligne.
    - textEditRowSpan est le nombre de lignes par défaut pour un widget QTextEdit. shape ou
    template peuvent définir des valeurs différentes.

    Les autres arguments sont uniquement utilisés lors des appels récursifs de la fonction
    et ne doivent pas être renseignés manuellement.

    Résultat : un dictionnaire avec autant de clés que de widgets à empiler verticalement
    (avec emboîtements). Les valeurs associées aux clés sont elles mêmes des dictionnaires,
    contenant les informations utiles à la création des widgets + des clés pour le
    stockage des futurs widgets.

    La clé du dictionnaire externe est un tuple formé :
    [0] d'un index, qui garantit l'unicité de la clé.
    [1] de la clé du groupe parent.
    [2] dans quelques cas, la lettre M, indiquant que le widget est la version "manuelle" d'un
    widget normalement abondé par un ou plusieurs thésaurus. Celui-ci a la même clé sans "M"
    (même parent, même index, même placement dans la grille). Ces deux widgets sont
    supposés être substitués l'un à l'autre dans la grille lorque l'utilisateur active ou
    désactive le "mode manuel" (cf. 'switch source widget' ci-après)
    

    Description des clés des dictionnaires internes :
    
    - 'object' : classification des éléments du dictionnaire. "group of values" ou
    "group of properties" ou "translation group" ou "edit" ou "plus button" ou "translation button".
    Les "translation group" et "translation button" ne peuvent exister que si l'argument
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
    - 'main action' : pour la QAction éventuellement associée au widget principal.
    - 'minus action' : pour la QAction associée au 'minus widget'.    

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
    implémenté (cf. minus widget). Sur le principe, on prévoit des boutons de suppression dès qu'il
    y a effectivement plusieurs valeurs saisies ou en cours de saisie pour une catégorie (un pour
    chacune).
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
    stockée dans le dictionnaire, mais peut être obtenue via la fonction getVocabulary.
    - 'read only' : booléen qui vaudra True si la métadonnée ne doit pas être modifiable par
    l'utilisateur. En mode lecture, 'read only' vaut toujours True.

    La dernière série de clés ne sert qu'aux fonctions de rdf_utils : 'default value'* (valeur par
    défaut), 'multiple values'* (la catégorie est-elle censée admettre plusieurs valeurs ?),
    'node kind', 'data type'**, 'class', 'path'***, 'subject', 'predicate', 'node', 'transform',
    'default widget type', 'one per language'.

    * ces clés apparaissent aussi dans le dictionnaire interne de template.
    ** le dictionnaire interne de template contient également une clé 'data type', mais dont les
    valeurs sont des chaînes de catactères parmi 'string', 'boolean', 'decimal', 'integer', 'date',
    'time', 'dateTime', 'duration', 'float', 'double' (et non des objets de type URIRef).
    *** le chemin est la clé principale de template.
           
    >>> buildDict(graph, shape, template, vocabulary)
    """

    nsm = mNSManager or shape.namespace_manager
    
    # ---------- INITIALISATION ----------
    # uniquement à la première itération de la fonction
    
    if mParentNode is None:

        for n, u in nsm.namespaces():
            graph.namespace_manager.bind(n, u, override=True, replace=True)

        mTargetClass = URIRef("http://www.w3.org/ns/dcat#Dataset")
        mPath = None
        mParentNode = None
        mGraphEmpty = ( len(graph) == 0 )
        mTemplateEmpty = ( template is None )
        
        # on travaille sur une copie du template pour pouvoir supprimer les catégories
        # au fur et à mesure de leur traitement par la première itération (sur les
        # catégories communes). À l'issue de celle-ci, ne resteront donc dans le
        # dictionnaire que les catégories locales.
        mShallowTemplate = template.copy() if template else dict()        

        # récupération de l'identifiant
        # du jeu de données dans le graphe, s'il existe
        if not mGraphEmpty:
        
            q_id = graph.query(
                """
                SELECT
                    ?id
                WHERE
                    { ?id a dcat:Dataset . }
                """
                )

            if len(q_id) > 1:
                raise ValueError("More than one dcat:Dataset object in graph.")

            for i in q_id:
                mParentNode = i['id']

        # si on n'a pas pu extraire d'identifiant, on en génère un nouveau
        # (et, in fine, le formulaire sera vierge)
        mParentNode = mParentNode or URIRef("urn:uuid:" + str(uuid.uuid4()))

        # coquille de dictionnaire pour les attributs des widgets
        mWidgetDictTemplate = {
            'object' : None,
            
            'main widget' : None,
            'grid widget' : None,
            'label widget' : None,
            'minus widget' : None,
            'language widget' : None,
            'switch source widget' : None,

            'main action' : None,
            'minus action' : None,
            'switch source menu' : None,
            'switch source actions' : [],
            'language menu' : None,
            'language actions' : [],
            
            'main widget type' : None,
            'row' : None,
            'row span' : None,              
            'label' : None,
            'label row' : None,
            'help text' : None,
            'value' : None,
            'language value': None,
            'placeholder text' : None,
            'input mask' : None,
            'is mandatory' : None,
            'has minus button' : None,
            'regex validator pattern' : None,
            'regex validator flags' : None,
            'type validator' : None,
            'multiple sources': None,
            'sources' : None,
            'current source' : None,
            'authorized languages' : None,
            'read only' : None,
            
            'default value' : None,
            'multiple values' : None,
            'node kind' : None,
            'data type' : None,
            'ontology' : None,
            'transform' : None,
            'class' : None,
            'path' : None,
            'subject' : None,
            'predicate' : None,
            'node' : None,
            'default widget type' : None,
            'one per language' : None
            }

        # on initialise le dictionnaire avec un groupe racine :
        mParentWidget = (0,)
        
        mDict = { mParentWidget : mWidgetDictTemplate.copy() }
        mDict[mParentWidget].update( {
            'object' : 'group of properties',
            'main widget type' : 'QGroupBox',
            'row' : 0,
            'node' : mParentNode,
            'class' : URIRef('http://www.w3.org/ns/dcat#Dataset')
            } )


    # ---------- EXECUTION COURANTE ----------

    idx = dict( { mParentWidget : 0 } )
    rowidx = dict( { mParentWidget : 0 } )

    # on extrait du modèle la liste des catégories de métadonnées qui
    # décrivent la classe cible, avec leurs caractéristiques
    q_tp = shape.query(
        """
        SELECT
            ?property ?name ?kind ?type
            ?class ?order ?widget ?descr
            ?default ?min ?max ?unilang
            ?pattern ?flags ?transform
            ?placeholder ?rowspan ?mask
        WHERE
            { ?u sh:targetClass ?c .
              ?u sh:property ?x .
              ?x sh:path ?property .
              ?x sh:name ?name .
              ?x sh:nodeKind ?kind .
              ?x sh:order ?order .
              OPTIONAL { ?x snum:widget ?widget } .
              OPTIONAL { ?x sh:datatype ?type } .
              OPTIONAL { ?x sh:class ?class } .
              OPTIONAL { ?x sh:description ?descr } .
              OPTIONAL { ?x snum:placeholder ?placeholder } .
              OPTIONAL { ?x snum:inputMask ?mask } .
              OPTIONAL { ?x sh:defaultValue ?default } .
              OPTIONAL { ?x sh:pattern ?pattern } .
              OPTIONAL { ?x sh:flags ?flags } .
              OPTIONAL { ?x snum:transform ?transform } .
              OPTIONAL { ?x snum:rowSpan ?rowspan } .
              OPTIONAL { ?x sh:uniqueLang ?unilang } .
              OPTIONAL { ?x sh:minCount ?min } .
              OPTIONAL { ?x sh:maxCount ?max } . }
        ORDER BY ?order
        """,
        initBindings = { 'c' : mTargetClass }
        )

    # --- BOUCLE SUR LES CATEGORIES
    
    for p in q_tp:

        mParent = mParentWidget
        mProperty = p['property']
        mKind = p['kind'].n3(nsm)
        mNPath = ( mPath + " / " if mPath else '') + mProperty.n3(nsm)
        mSources = None
        mDefaultTrad = None
        mDefaultSource = None
        mLangList = None
        mNHidden = mHidden or False
        values = None

        # on extrait la ou les valeurs éventuellement
        # renseignées dans le graphe pour cette catégorie
        # et le sujet considéré
        if not mGraphEmpty:
        
            q_gr = graph.query(
                """
                SELECT
                    ?value
                WHERE
                     { ?n ?p ?value . }
                """,
                initBindings = { 'n' : mParentNode, 'p' : mProperty }
                )
                
            values = [ v['value'] for v in q_gr ]
    
        # exclusion des catégories qui ne sont pas prévues par
        # le modèle et n'ont pas de valeur renseignée
        if values in ( None, [], [ None ] ) and not mTemplateEmpty and not ( mNPath in template ):
            continue
        elif hideUnlisted and not mTemplateEmpty and not ( mNPath in template ):
            mNHidden = True
        
        if not ( readHideBlank and mode == 'read' ):
            values = values or [ None ]
        
        if not mNHidden and ( mNPath in mShallowTemplate ):
            t = mShallowTemplate[mNPath]
            mShallowTemplate[mNPath].update( { 'done' : True } )
        else:
            t = dict()


        if mNHidden:
            # cas d'une catégorie qui ne sera pas affichée à l'utilisateur, car
            # absente du template, mais pour laquelle une valeur était renseignée
            # et qu'il s'agit de ne pas perdre
        
            if len(values) > 1:               
                # si plusieurs valeurs étaient renseignées, on référence un groupe
                # de valeurs (dans certains cas un groupe de traduction aurait été plus
                # adapté, mais ça n'a pas d'importance) sans aucune autre propriété
                mWidget = ( idx[mParent], mParent )
                mDict.update( { mWidget : mWidgetDictTemplate.copy() } )
                mDict[mWidget].update( {
                    'object' : 'group of values'
                    } )

                idx[mParent] += 1
                idx.update( { mWidget : 0 } )
                mParent = mWidget        
        
        else:
            # récupération de la liste des ontologies
            if mKind in ("sh:BlankNodeOrIRI", "sh:IRI") :

                q_on = shape.query(
                    """
                    SELECT
                        ?ontology
                    WHERE
                        { ?u sh:targetClass ?c .
                          ?u sh:property ?x .
                          ?x sh:path ?p .
                          ?x snum:ontology ?ontology . }
                    """,
                    initBindings = { 'c' : mTargetClass, 'p' : mProperty }
                    )

                for s in q_on:
                    
                    q_vc = vocabulary.query(
                        """
                        SELECT
                            ?scheme
                        WHERE
                            {{ ?s a skos:ConceptScheme ;
                             skos:prefLabel ?scheme .
                              FILTER ( lang(?scheme) = "{}" ) }}
                        """.format(language),
                        initBindings = { 's' : s['ontology'] }
                        )

                    mSources = ( mSources or [] ) + ( [ str(l['scheme']) for l in q_vc ] if len(q_vc) == 1 else [] )
                        
                if mSources == []:
                    mSources = None

                if mSources and t.get('default value', None):
                    mDefaultSource = getConceptFromValue(t.get('default value', None), None, vocabulary, language)[1]
                elif mSources and p['default']:
                    mDefaultTrad, mDefaultSource = getValueFromConcept(p['default'], vocabulary, language)   
                    
                        
            multilingual = p['unilang'] and bool(p['unilang']) or False
            multiple = ( p['max'] is None or int( p['max'] ) > 1 ) and not multilingual
            
            if translation and multilingual:
                mLangList = [ l for l in langList or [] if not l in [ v.language for v in values if isinstance(v, Literal) ] ]
                # à ce stade, mLangList contient toutes les langues de langList pour lesquelles
                # aucune tranduction n'est disponible. On y ajoutera ensuite la langue de la valeur
                # courante pour obtenir la liste à afficher dans son widget de sélection de langue
            
            if len(values) > 1 or ( ( ( translation and multilingual ) or multiple )
                    and not ( mode == 'read' and readHideBlank ) ):
                
                # si la catégorie admet plusieurs valeurs uniquement s'il
                # s'agit de traductions, on référence un widget de groupe
                mWidget = ( idx[mParent], mParent )
                mDict.update( { mWidget : mWidgetDictTemplate.copy() } )
                mDict[mWidget].update( {
                    'object' : 'translation group' if ( multilingual and translation ) else 'group of values',
                    'main widget type' : 'QGroupBox',
                    'row' : rowidx[mParent],
                    'label' : t.get('label', None) or str(p['name']),
                    'help text' : t.get('help text', None) or ( str(p['descr']) if p['descr'] else None )
                    } )

                idx[mParent] += 1
                rowidx[mParent] += 1
                idx.update( { mWidget : 0 } )
                rowidx.update( { mWidget : 0 } )
                mParent = mWidget
                # les widgets de saisie référencés juste après auront
                # ce widget de groupe pour parent
                
                
            mLabel = ( t.get('label', None) or str(p['name']) ) if (
                        ( mode == 'read' and len(values) <= 1 ) or not (
                        multiple or len(values) > 1 or ( multilingual and translation ) ) ) else None
                        
            mHelp = ( t.get('help text', None) or ( str(p['descr']) if p['descr'] else None ) ) if (
                        ( mode == 'read' and len(values) <= 1 ) or not (
                        multiple or len(values) > 1 or ( multilingual and translation ) ) ) else None


        # --- BOUCLE SUR LES VALEURS
        
        for mValueBrut in values:
            
            mValue = None
            mCurSource = None
            mLanguage = ( ( mValueBrut.language if isinstance(mValueBrut, Literal) else None ) or language ) if (
                        mKind == 'sh:Literal' and p['type'].n3(nsm) == 'xsd:string' ) else None
            
            # cas d'un noeud vide :
            # on ajoute un groupe et on relance la fonction sur la classe du noeud
            if mKind in ( 'sh:BlankNode', 'sh:BlankNodeOrIRI' ) and (
                    not readHideBlank or not mode == 'read' or isinstance(mValueBrut, BNode) ):

                # cas d'une branche masquée
                if mNHidden and isinstance(mValueBrut, BNode):
                    
                    mNode = mValueBrut
                    mWidget = ( idx[mParent], mParent )
                    mDict.update( { mWidget : mWidgetDictTemplate.copy() } )
                    mDict[mWidget].update( {
                        'object' : 'group of properties',
                        'node kind' : mKind,
                        'class' : p['class'],
                        'path' : mNPath,
                        'subject' : mParentNode,
                        'predicate' : mProperty,
                        'node' : mNode
                        } )
                    idx[mParent] += 1                    
                    idx.update( { mWidget : 0 } )

                # branche visible
                elif not mNHidden:
                
                    mNGraphEmpty = mGraphEmpty or mValueBrut is None              
                    mNode = mValueBrut if isinstance(mValueBrut, BNode) else BNode()

                    if mKind == 'sh:BlankNodeOrIRI':
                        mSources = ( mSources + [ "< manuel >" ] ) if mSources else [ "< URI >", "< manuel >" ]
                        mCurSource = "< manuel >" if isinstance(mValueBrut, BNode) else None

                    mWidget = ( idx[mParent], mParent, 'M' ) if mKind == 'sh:BlankNodeOrIRI' else ( idx[mParent], mParent )
                    mDict.update( { mWidget : mWidgetDictTemplate.copy() } )
                    mDict[mWidget].update( {
                        'object' : 'group of properties',
                        'main widget type' : 'QGroupBox',
                        'row' : rowidx[mParent],
                        'label' : mLabel,
                        'help text' : mHelp,
                        'has minus button' : ( len(values) > 1 and mode == 'edit' ) or False,
                        'multiple values' : multiple,
                        'node kind' : mKind,
                        'class' : p['class'],
                        'path' : mNPath,
                        'subject' : mParentNode,
                        'predicate' : mProperty,
                        'node' : mNode,
                        'multiple sources' : mKind == 'sh:BlankNodeOrIRI' and mode == 'edit',
                        'current source' : mCurSource,
                        'sources' : mSources
                        } )

                    if mKind == 'sh:BlankNode':
                        idx[mParent] += 1
                        rowidx[mParent] += 1
                        
                    idx.update( { mWidget : 0 } )
                    rowidx.update( { mWidget : 0 } )

                if not mNHidden or isinstance(mValueBrut, BNode):              
                    buildDict(
                        graph, shape, vocabulary, template, mode, readHideBlank, hideUnlisted,
                        language, translation, langList, labelLengthLimit, valueLengthLimit,
                        textEditRowSpan, mNPath, p['class'], mWidget, mNode, mNSManager,
                        mWidgetDictTemplate, mDict, mNGraphEmpty, mShallowTemplate, mTemplateEmpty,
                        mNHidden
                        )

            # pour tout ce qui n'est pas un pur noeud vide :
            # on ajoute un widget de saisie, en l'initialisant avec
            # une représentation lisible de la valeur
            if not mKind == 'sh:BlankNode' and (
                    not readHideBlank or not mode == 'read' or not isinstance(mValueBrut, BNode) ):
                    
                # cas d'une valeur masquée
                if mNHidden:
                
                    if isinstance(mValueBrut, BNode):
                        continue   
                        
                    mDict.update( { ( idx[mParent], mParent ) : mWidgetDictTemplate.copy() } )
                    mDict[ ( idx[mParent], mParent ) ].update( {
                        'object' : 'edit',                      
                        'value' : mValueBrut,                        
                        'language value' : mLanguage,                        
                        'node kind' : mKind,
                        'data type' : p['type'],
                        'class' : p['class'],
                        'path' : mNPath,
                        'subject' : mParentNode,
                        'predicate' : mProperty                      
                        } )
                
                    idx[mParent] += 1
                    continue

                
                if isinstance(mValueBrut, BNode):
                    mValueBrut = None
                    
                if  multilingual and translation and mLanguage:
                    mLangList = mLangList + [ mLanguage ] if not mLanguage in mLangList else mLangList
                elif translation and mLanguage:
                    mLangList = [ mLanguage ] + ( langList or [] ) if not mLanguage in ( langList or [] ) else langList
                
                # cas d'une catégorie qui tire ses valeurs d'une
                # ontologie : on récupère le label à afficher
                if isinstance(mValueBrut, URIRef) and mSources:             
                    mValue, mCurSource = getValueFromConcept(mValueBrut, vocabulary, language)                   
                    if not mCurSource in mSources:
                        mCurSource = '< non répertorié >'
                        
                elif mSources and mGraphEmpty and ( mValueBrut is None ):
                    mCurSource = mDefaultSource

                if mSources and ( mCurSource is None ):
                    # cas où la valeur n'était pas renseignée - ou n'est pas un IRI
                    mCurSource = '< non répertorié >' if mValueBrut else mSources[0]

                elif mCurSource == "< manuel >":
                    mCurSource = None               
                

                # cas d'un numéro de téléphone. on transforme
                # l'IRI en quelque chose d'un peu plus lisible
                if mValueBrut and str(p['transform']) == 'phone':
                    mValue = telFromOwlThing(mValueBrut)

                # cas d'une adresse mél. on transforme
                # l'IRI en quelque chose d'un peu plus lisible
                if mValueBrut and str(p['transform']) == 'email':
                    mValue = emailFromOwlThing(mValueBrut)

                mDefault = t.get('default value', None) or mDefaultTrad or ( str(p['default']) if p['default'] else None )
                mValue = mValue or ( str(mValueBrut) if mValueBrut else ( mDefault if mGraphEmpty else None ) )

                mWidgetType = t.get('main widget type', None) or str(p['widget']) or "QLineEdit"
                mDefaultWidgetType = mWidgetType
                
                mLabelRow = None

                if mWidgetType == "QLineEdit" and mValue and ( len(mValue) > valueLengthLimit or mValue.count("\n") > 0 ):
                    mWidgetType = 'QTextEdit'

                if mLabel and ( mWidgetType == 'QTextEdit' or len(mLabel) > labelLengthLimit ):
                    mLabelRow = rowidx[mParent]
                    rowidx[mParent] += 1

                mDict.update( { ( idx[mParent], mParent ) : mWidgetDictTemplate.copy() } )
                mDict[ ( idx[mParent], mParent ) ].update( {
                    'object' : 'edit',
                    'main widget type' : mWidgetType,
                    'row' : rowidx[mParent],
                    'row span' : ( t.get('row span', None) or ( int(p['rowspan']) if p['rowspan'] else textEditRowSpan )
                               ) if mWidgetType == 'QTextEdit' else None,
                    'input mask' : t.get('input mask', None) or ( str(p['mask']) if p['mask'] else None ),
                    'label' : mLabel,
                    'label row' : mLabelRow,
                    'help text' : mHelp,
                    'value' : mValue,
                    'placeholder text' : ( t.get('placeholder text', None) or ( str(p['placeholder']) if p['placeholder'] else mCurSource ) 
                                ) if mWidgetType in ( 'QTextEdit', 'QLineEdit', 'QComboBox' ) else None,
                    'language value' : mLanguage,
                    'is mandatory' : t.get('is mandatory', None) or ( int(p['min']) > 0 if p['min'] else False ),
                    'has minus button' : ( len(values) > 1 and mode == 'edit' ) or False,
                    'regex validator pattern' : str(p['pattern']) if p['pattern'] else None,
                    'regex validator flags' : str(p['flags']) if p['flags'] else None,
                    'default value' : mDefault,
                    'multiple values' : multiple,
                    'node kind' : mKind,
                    'data type' : p['type'],
                    'class' : p['class'],
                    'path' : mNPath,
                    'subject' : mParentNode,
                    'predicate' : mProperty,
                    'default widget type' : mDefaultWidgetType,
                    'transform' : str(p['transform']) if p['transform'] else None,
                    'type validator' : 'QIntValidator' if p['type'] and p['type'].n3(nsm) == "xsd:integer" else (
                        'QDoubleValidator' if p['type'] and p['type'].n3(nsm) in ("xsd:decimal", "xsd:float", "xsd:double") else None ),
                    'multiple sources' : len(mSources) > 1 if mSources and mode == 'edit' else False,
                    'current source' : mCurSource,
                    'sources' : ( mSources or [] ) + '< non répertorié >' if mCurSource == '< non répertorié >' else mSources,
                    'one per language' : multilingual and translation,
                    'authorized languages' : mLangList if mode == 'edit' else None,
                    'read only' : ( mode == 'read' ) or bool(t.get('read only', False))
                    } )
                
                idx[mParent] += 1
                rowidx[mParent] += 1

        # référencement d'un widget bouton pour ajouter une valeur
        # si la catégorie en admet plusieurs
        if not mNHidden and mode == 'edit' and ( ( multilingual and translation and mLangList and len(mLangList) > 1 ) or multiple ):
        
            mDict.update( { ( idx[mParent], mParent ) : mWidgetDictTemplate.copy() } )
            mDict[ ( idx[mParent], mParent ) ].update( {
                'object' : 'translation button' if multilingual else 'plus button',
                'main widget type' : 'QToolButton',
                'row' : rowidx[mParent]
                } )
            
            idx[mParent] += 1
            rowidx[mParent] += 1
            


    # ---------- METADONNEES LOCALES DEFINIES PAR LE MODELE ----------
    
    if mTargetClass == URIRef("http://www.w3.org/ns/dcat#Dataset"):

        for meta, t in mShallowTemplate.items():

            if t.get('done', False):
                # on passe les catégories déjà traitées
                continue

            if not isValidMiniPath(meta, nsm):
                # on élimine d'office les catégories locales dont
                # l'identifiant n'est pas un chemin SPARQL valide
                # à un seul élément et dont le préfixe éventuel
                # est déjà référencé
                continue

            mParent = mParentWidget

            mType = URIRef( "http://www.w3.org/2001/XMLSchema#" +
                    ( ( t.get('data type', None) ) or "string" ) )

            if not mType.n3(nsm) in ('xsd:string', 'xsd:integer', "xsd:decimal",
                        "xsd:float", "xsd:double", 'xsd:boolean', 'xsd:date',
                        'xsd:time', 'xsd:dateTime', 'xsd:duration'):
                mType = URIRef("http://www.w3.org/2001/XMLSchema#string")

            # on extrait la ou les valeurs éventuellement
            # renseignées dans le graphe pour cette catégorie
            q_gr = graph.query(
                """
                SELECT
                    ?value
                WHERE
                     {{ ?n {} ?value . }}
                """.format(meta),
                initBindings = { 'n' : mParentNode }
                )

            values = [ v['value'] for v in q_gr ] if mode == 'read' and readHideBlank else (
                        [ v['value'] for v in q_gr ] or [ t.get('default value', None) if mGraphEmpty else None ] )

            multiple = t.get('multiple values', False)

            if len(values) > 1 or ( multiple and not ( mode == 'read' and readHideBlank ) ):
 
                mWidget = ( idx[mParent], mParent )
                mDict.update( { mWidget : mWidgetDictTemplate.copy() } )
                mDict[mWidget].update( {
                    'object' : 'group of values',
                    'main widget type' : 'QGroupBox',
                    'row' : rowidx[mParent],
                    'label' : t.get('label', None) or "???",
                    'help text' : t.get('help text', None)
                    } )

                idx[mParent] += 1
                rowidx[mParent] += 1
                idx.update( { mWidget : 0 } )
                rowidx.update( { mWidget : 0 } )
                mParent = mWidget

            for mValueBrut in values:
                
                # on considère que toutes les valeurs sont des Literal
                mValue = str(mValueBrut) if mValueBrut else None
                mLanguage = ( ( mValueBrut.language if mValueBrut and isinstance(mValueBrut, Literal) else None ) or language
                                 ) if mType.n3(nsm) == 'xsd:string' else None
                                 
                mLangList = ( [ mLanguage ] + ( langList or [] ) if not mLanguage in ( langList or [] ) else langList 
                            ) if mLanguage and translation else None

                mWidgetType = t.get('main widget type', None) or "QLineEdit"
                mDefaultWidgetType = mWidgetType
                mLabel = ( t.get('label', None) or "???" ) if not ( multiple or len(values) > 1 ) else None
                mLabelRow = None

                if mWidgetType == "QLineEdit" and mValue and ( len(mValue) > valueLengthLimit or mValue.count("\n") > 0 ):
                    mWidgetType = 'QTextEdit'

                if mLabel and ( mWidgetType == 'QTextEdit' or len(mLabel) > labelLengthLimit ):
                    mLabelRow = rowidx[mParent]
                    rowidx[mParent] += 1                

                mDict.update( { ( idx[mParent], mParent ) : mWidgetDictTemplate.copy() } )
                mDict[ ( idx[mParent], mParent ) ].update( {
                    'object' : 'edit',
                    'main widget type' : mWidgetType,
                    'row' : rowidx[mParent],
                    'row span' : t.get('row span', textEditRowSpan) if mWidgetType == 'QTextEdit' else None,
                    'input mask' : t.get('input mask', None),
                    'label' : mLabel,
                    'label row' : mLabelRow,
                    'help text' : t.get('help text', None) if not ( multiple or len(values) > 1 ) else None,
                    'value' : mValue,
                    'placeholder text' : t.get('placeholder text', None) if mWidgetType in ( 'QTextEdit', 'QLineEdit', 'QComboBox' ) else None,
                    'language value' : mLanguage,
                    'is mandatory' : t.get('is mandatory', None),
                    'multiple values' : multiple,
                    'has minus button' : ( len(values) > 1 and mode == 'edit' ) or False,
                    'default value' : t.get('default value', None),
                    'node kind' : "sh:Literal",
                    'data type' : mType,
                    'subject' : mParentNode,
                    'predicate' : URIRef(meta),
                    'path' : meta,
                    'default widget type' : mDefaultWidgetType,
                    'type validator' : 'QIntValidator' if mType.n3(nsm) == "xsd:integer" else (
                        'QDoubleValidator' if mType.n3(nsm) in ("xsd:decimal", "xsd:float", "xsd:double") else None ),
                    'authorized languages' : mLangList if mode == 'edit' else None,
                    'read only' : ( mode == 'read' ) or bool(t.get('read only', False))
                    } )
                        
                idx[mParent] += 1
                rowidx[mParent] += 1

            if multiple and mode == 'edit':

                mDict.update( { ( idx[mParent], mParent ) : mWidgetDictTemplate.copy() } )
                mDict[ ( idx[mParent], mParent ) ].update( {
                    'object' : 'plus button',
                    'main widget type' : 'QToolButton',
                    'row' : rowidx[mParent]
                    } )
                
                idx[mParent] += 1
                rowidx[mParent] += 1


    # ---------- METADONNEES NON DEFINIES ----------
    # métadonnées présentes dans le graphe mais ni dans shape ni dans template
    
    if not hideUnlisted and mTargetClass == URIRef("http://www.w3.org/ns/dcat#Dataset"):
        
        q_gr = graph.query(
            """
            SELECT
                ?property ?value
            WHERE
                { ?n ?property ?value . 
                  FILTER ( ?property != rdf:type ) }
            """,
            initBindings = { 'n' : mParentNode }
            )
        
        dpv = dict()
        
        for p, v in q_gr:          
            if not p.n3(nsm) in [ d.get('path', None) for d in mDict.values() ]:        
                dpv.update( { p : ( dpv.get(p, []) ) + [ v ] } )

        for p in dpv:

            mParent = mParentWidget
            
            if len(dpv[p]) > 1:

                mWidget = ( idx[mParent], mParent )
                mDict.update( { mWidget : mWidgetDictTemplate.copy() } )
                mDict[mWidget].update( {
                    'object' : 'group of values',
                    'main widget type' : 'QGroupBox',
                    'row' : rowidx[mParent],
                    'label' : "???"
                    } )

                idx[mParent] += 1
                rowidx[mParent] += 1
                idx.update( { mWidget : 0 } )
                rowidx.update( { mWidget : 0 } )
                mParent = mWidget


            for v in dpv[p]:

                mValue = str(v)
                mWidgetType = 'QTextEdit' if ( len(mValue) > valueLengthLimit or mValue.count("\n") > 0 ) else "QLineEdit"
                mLabelRow = None

                if len(dpv[p]) == 1 and mWidgetType == 'QTextEdit':
                    mLabelRow = rowidx[mParent]
                    rowidx[mParent] += 1

                mType = ( v.datatype if isinstance(v, Literal) else None ) or URIRef("http://www.w3.org/2001/XMLSchema#string")
                # NB : pourrait ne pas être homogène pour toutes les valeurs d'une même catégorie
                
                mLanguage = ( ( v.language if isinstance(v, Literal) else None ) or language 
                            ) if mType.n3(nsm) == 'xsd:string' else None
                            
                mLangList = ( [ mLanguage ] + ( langList or [] ) if not mLanguage in ( langList or [] ) else langList 
                            ) if mLanguage and translation else None

                mDict.update( { ( idx[mParent], mParent ) : mWidgetDictTemplate.copy() } )
                mDict[ ( idx[mParent], mParent ) ].update( {
                    'object' : 'edit',
                    'main widget type' : mWidgetType,
                    'row' : rowidx[mParent],
                    'row span' : textEditRowSpan if mWidgetType == "QTextEdit" else None,
                    'label' : "???" if len(dpv[p]) == 1 else None,
                    'label row' : mLabelRow,
                    'value' : mValue,
                    'language value' : mLanguage,
                    'node kind' : "sh:Literal",
                    'data type' : mType,
                    'multiple values' : False,
                    'has minus button' : ( len(dpv[p]) > 1 and mode == 'edit' ) or False,
                    'subject' : mParentNode,
                    'predicate' : p,
                    'path' : p.n3(nsm),
                    'default widget type' : "QLineEdit",
                    'type validator' : 'QIntValidator' if mType.n3(nsm) == "xsd:integer" else (
                        'QDoubleValidator' if mType.n3(nsm) in ("xsd:decimal", "xsd:float", "xsd:double") else None ),
                    'authorized languages' : mLangList if mode == 'edit' else None,
                    'read only' : ( mode == 'read' )
                    } )
                        
                idx[mParent] += 1
                rowidx[mParent] += 1

            # pas de bouton plus, faute de modèle indiquant si la catégorie
            # admet des valeurs multiples

    return mDict


def forbiddenChar(anyStr: str) -> str:
    """Return any character from given string that is not allowed in IRIs.
    
    - anyStr est la chaîne de caractères à tester.
    
    >>> forbiddenChar('avec des espaces')
    ' '
    """
    
    r = re.search(r'([<>"\s{}|\\^`])', anyStr)
    
    return r[1] if r else None


def isValidMiniPath(path: str, mNSManager: NamespaceManager) -> bool:
    """Run basic validity test on SPARQL mono-element path.

    Arguments :
    - path est un chemin SPARQL.
    - mNSManager est un gestionnaire d'espaces de nommage.

    La fonction renvoie False si path est visiblement composé
    de plus d'un élément.

    Elle renvoie True si path est un URI valide (pas de
    caractères interdits), soit non abrégé et écrit entre < >,
    soit abrégé avec un préfixe référencé dans le gestionnaire
    d'espaces de nommage fourni en argument.

    >>> isValidMiniPath('<https://www.w3.org/TR/sparql11-query/>',
    ...     Graph().namespace_manager)
    True
    """

    if re.match(r'^[<][^<>"\s{}|\\^`]+[:][^<>"\s{}|\\^`]+[>]$', path):
        return True

    r = re.match('^([a-z]{1,10})[:][a-z0-9-]{1,25}$', path)
    if r and r[1] in [ k for k,v in mNSManager.namespaces() ]:
        return True

    return False
    


def extractMetadata(description: str, shape: Graph) -> Graph:
    """Get JSON-LD metadata from description and parse them into a graph.

    Arguments :
    - description est une chaîne de caractères supposée correspondre à la
    description (ou les commentaire) d'un objet PostgreSQL.
    - shape est un schéma SHACL augmenté décrivant les catégories de métadonnées
    communes. Il fournit ici les préfixes d'espaces de nommage à déclarer dans
    le graphe.

    Résultat : un graphe RDF déduit par désérialisation du JSON-LD.

    Le JSON-LD est présumé se trouver entre deux balises <METADATA> et </METADATA>.

    Si la valeur contenue entre les balises n'est pas un JSON valide, la
    fonction échoue sur une erreur de type json.decoder.JSONDecodeError.

    S'il n'y a pas de balises, s'il n'y a rien entre les balises ou si la valeur
    contenue entre les balises est un JSON et pas un JSON-LD, la fonction renvoie
    un graphe vide.

    >>> with open('shape.ttl', encoding='UTF-8') as src:
    ...    shape = Graph().parse(data=src.read(), format='turtle')
    >>> with open('exemples\\exemple_commentaire_pg.txt', encoding='UTF-8') as src:
    ...    c_source = src.read()
    >>> g_source = extractMetadata(c_source, shape)
    """

    j = re.search("^(?:.*)[<]METADATA[>](.*?)[<][/]METADATA[>]", description, re.DOTALL)
    # s'il y a plusieurs balises <METADATA> et/ou </METADATA>, cette expression retient
    # les caractères compris entre la dernière balise <METADATA> et la première balise </METADATA>.
    # s'il devait y avoir plusieurs couples de balises, elle retiendrait le contenu du
    # dernier.

    if j is None:

        g = Graph()

    elif j[1]:

        g = Graph().parse(data=j[1], format='json-ld')

    else:
        g = Graph()
  
    for n, u in shape.namespace_manager.namespaces():
            g.namespace_manager.bind(n, u, override=True, replace=True)

    return g


def updateDescription(description: str, graph: Graph) -> str:
    """Return new description with metadata section updated from JSON-LD serialization of graph.

    Arguments :
    - description est une chaîne de caractères supposée correspondre à la
    description (ou les commentaire) d'un objet PostgreSQL.
    - graph est un graphe RDF présumé contenir les métadonnées de l'objet.

    Résultat : une chaîne de caractère correspondant à la description mise à jour
    d'après le contenu du graphe.

    Les informations comprises entre les deux balises <METADATA> et </METADATA>
    sont remplacées. Si les balises n'existaient pas, elles sont ajoutées à la
    fin du texte.

    >>> updateDescription(c, g)
    """

    if len(graph) == 0:
        return description
    
    s = graph.serialize(format="json-ld").decode("utf-8")
    
    t = re.subn(
        "[<]METADATA[>].*[<][/]METADATA[>]",
        "<METADATA>\n" + s + "\n</METADATA>",
        description,
        flags=re.DOTALL
        )
    # cette expression remplace tout de la première balise <METADATA> à
    # la dernière balise </METADATA> (elle maximise la cible, au contraire
    # de la fonction extractMetadata)

    if t[1] == 0:
        return description + "\n\n<METADATA>\n" + s + "\n</METADATA>\n"

    else:
        return t[0]
        

def getVocabulary(schemeStr: str, vocabulary, language: str = "fr") -> List[str]:
    """List all concept labels from given scheme.

    Arguments :
    - schemeStr est le nom de l'ensemble dont on veut lister les concepts.
    - vocabulary est un graphe réunissant le vocabulaire de tous les ensembles
    à considérer.
    - language est la langue attendue pour les libellés des concepts. schemeStr
    doit être donné dans cette même langue.

    Résultat : liste contenant les libellés, triés par ordre alphabétique selon
    la locale de l'utilisateur.

    >>> getVocabulary("Thèmes de données (UE)", vocabulary)
    ['Agriculture, pêche, sylviculture et alimentation', 'Données provisoires',
    'Économie et finances', 'Éducation, culture et sport', 'Énergie', 'Environnement',
    'Gouvernement et secteur public', 'Justice, système juridique et sécurité publique',
    'Population et société', 'Questions internationales', 'Régions et villes', 'Santé',
    'Science et technologie', 'Transports']
    """
    
    q_vc = vocabulary.query(
        """
        SELECT
            ?label
        WHERE
            {{ ?c a skos:Concept ;
            skos:inScheme ?s ;
            skos:prefLabel ?label .
            ?s a skos:ConceptScheme ;
                skos:prefLabel ?l .
              FILTER ( lang(?label) = "{}" ) }}
        """.format(language),
        initBindings = { 'l' : Literal(schemeStr, lang=language) }
        )

    if len(q_vc) > 0:

        setlocale(LC_COLLATE, "")

        return sorted(
            [str(l['label']) for l in q_vc],
            key=lambda x: strxfrm(x)
            )


def getConceptFromValue(conceptStr: str, schemeStr: str, vocabulary, language: str = 'fr') -> Tuple[URIRef, URIRef]:
    """Return a skos:Concept IRI matching given label.

    Arguments :
    - conceptStr est une chaîne de caractères présumée correspondre au libellé d'un
    concept.
    - schemeStr est une chaîne de caractères présumée correspondre au libellé de
    l'ensemble qui référence ce concept. Si schemeStr n'est pas spécifié, la fonction
    effectuera la recherche dans tous les ensembles disponibles. En cas de
    correspondance multiple, elle renvoie arbitrairement un des résultats.
    - vocabulary est un graphe réunissant le vocabulaire de tous les ensembles
    à considérer.
    - language est la langue présumée de strValue et schemeStr. Français par défaut.

    Résultat : un tuple formé [0] de l'IRI du terme et [1] de l'IRI de l'ensemble.

    >>> getConceptFromValue("Domaine public", "Types de licences (UE)", vocabulary)
    (rdflib.term.URIRef('http://purl.org/adms/licencetype/PublicDomain'), rdflib.term.URIRef('http://purl.org/adms/licencetype/1.1'))
        
    >>> getConceptFromValue("Transports", None, vocabulary)
    (rdflib.term.URIRef('http://publications.europa.eu/resource/authority/data-theme/TRAN'), rdflib.term.URIRef('http://publications.europa.eu/resource/authority/data-theme'))
    """

    if schemeStr:
        q_vc = vocabulary.query(
            """
            SELECT
                ?concept ?scheme
            WHERE
                { ?concept a skos:Concept ;
                   skos:inScheme ?scheme ;
                   skos:prefLabel ?c .
                   ?scheme a skos:ConceptScheme ;
                   skos:prefLabel ?s . }
            """,
            initBindings = { 'c' : Literal(conceptStr, lang=language),
                            's' : Literal(schemeStr, lang=language) }
            )
         
        for t in q_vc:
            return ( t['concept'], t['scheme'] )
            
    else:
        q_vc = vocabulary.query(
            """
            SELECT
                ?concept ?scheme
            WHERE
                { ?concept a skos:Concept ;
                   skos:inScheme ?scheme ;
                   skos:prefLabel ?c . }
            """,
            initBindings = { 'c' : Literal(conceptStr, lang=language) }
            )
         
        for t in q_vc:
            return t['concept'], t['scheme']
        
    return ( None, None )



def getValueFromConcept(conceptIRI: URIRef, vocabulary, language: str = "fr") -> Tuple[str, str]:
    """Return the skos:prefLabel strings matching given conceptIRI and its scheme.

    Arguments :
    - conceptIRI est un objet de type rdflib.term.URIRef présumé correspondre à un
    concept d'ontologie.
    - vocabulary est un graphe réunissant le vocabulaire de tous les ensembles à
    considérer.
    - language est la langue attendue pour le libellé résultant. Français par défaut.
    
    Si aucune valeur n'est disponible pour la langue spécifiée, la fonction retournera
    la traduction française (si elle existe).

    Résultat : une tuple contenant deux chaînes de caractères. [0] est le libellé
    du concept. [1] est le nom de l'ensemble. (None, None) si l'IRI n'est pas répertorié.
    
    Dans l'exemple ci-après, il existe une traduction française et anglaise pour le terme
    recherché, mais pas de version espagnole.

    >>> u = URIRef("http://publications.europa.eu/resource/authority/data-theme/TRAN")
    
    >>> getValueFromConcept(u, vocabulary)
    ('Transports', 'Thèmes de données (UE)')
    
    >>> getValueFromConcept(u, vocabulary, 'en')
    ('Transport', 'Data theme (EU)')
    
    >>> getValueFromConcept(u, vocabulary, 'es')
    ('Transports', 'Thèmes de données (UE)')
    """
    
    q_vc = vocabulary.query(
        """
        SELECT
            ?label ?scheme
        WHERE
            {{ ?c a skos:Concept ;
               skos:inScheme ?s ;
               skos:prefLabel ?label .
               ?s a skos:ConceptScheme ;
               skos:prefLabel ?scheme .
               FILTER (( lang(?label) = "{0}" ||
                      ( ( lang(?label) != "{0}" )
                      && ( lang(?label) = "fr" ) ) ) 
                  && ( lang(?scheme) = "{0}" ||
                      ( ( lang(?scheme) != "{0}" )
                      && ( lang(?scheme) = "fr" ) ) )) }}
        """.format(language),
        initBindings = { 'c' : conceptIRI }
        )
     
    for t in q_vc:
        return ( str( t['label'] ), str( t['scheme'] ) )
        
    return ( None, None )
    


def emailFromOwlThing(thingIRI: URIRef) -> str:
    """Return a string human-readable version of an owl:Thing IRI representing an email adress.

    Arguments :
    - thingIRI est un objet de type URIref supposé correspondre
    à une adresse mél (classe RDF owl:Thing).

    Résultat : une chaîne de caractères.

    Cette fonction très basique se contente de retirer le préfixe
    "mailto:" s'il était présent.

    >>> emailFromOwlThing(URIRef("mailto:jon.snow@the-wall.we"))
    'jon.snow@the-wall.we'
    """

    # à partir de la version 3.9
    # str(thingIRI).removeprefix("mailto:") serait plus élégant
    
    return re.sub("^mailto[:]", "", str(thingIRI))


def owlThingFromEmail(emailStr: str) -> URIRef:
    """Return an IRI from a string representing an email adress.

    Arguments :
    - emailStr est une chaîne de caractère supposée correspondre à une
    adresse mél.

    Résultat : un objet de type URIRef respectant grosso modo le schéma
    officiel des URI pour les adresses mél : mailto:<email>.
    (réf : https://datatracker.ietf.org/doc/html/rfc6068)

    La fonction ne fait aucun contrôle de validité sur l'adresse si ce
    n'est vérifier qu'elle ne contient aucun caractère interdit pour
    un IRI.

    >>> owlThingFromEmail("jon.snow@the-wall.we")
    rdflib.term.URIRef('mailto:jon.snow@the-wall.we')
    """

    emailStr = re.sub("^mailto[:]", "", emailStr)

    l = [i for i in '<> "{}|\\^`' if i in emailStr]

    if l and not l == []:          
        raise ValueError("Invalid IRI. Forbiden character '{}' in email adress '{}'.".format("".join(l), emailStr))

    if emailStr and not emailStr == "":
        return URIRef("mailto:" + emailStr)


def telFromOwlThing(thingIRI: URIRef) -> str:
    """Return a string human-readable version of an owl:Thing IRI representing a phone number.

    Arguments :
    - thingIRI est un objet de type URIref supposé correspondre
    à un numéro de téléphone (classe RDF owl:Thing).

    Résultat : une chaîne de caractères.

    Contrairement à owlThingFromTel, cette fonction très basique ne standardise
    pas la forme du numéro de téléphone. Elle se contente de retirer le préfixe
    "tel:" s'il était présent.

    >>> telFromOwlThing(URIRef("tel:+33-1-23-45-67-89"))
    '+33-1-23-45-67-89'
    """
    
    return re.sub("^tel[:]", "", str(thingIRI))


def owlThingFromTel(telStr: str, addPrefixFr: bool = True) -> URIRef:
    """Return an IRI from a string representing a phone number.

    Arguments :
    - telStr est une chaîne de caractère supposée correspondre à un
    numéro de téléphone.
    - addPrefixFr est un booléen indiquant si la fonction doit tenter
    de transformer les numéros de téléphone français locaux ou présumés
    comme tels (un zéro suivi de neuf chiffres) en numéros globaux ("+33"
    suivi des neuf chiffres).

    Résultat : un objet de type URIRef respectant grosso modo le schéma
    officiel des URI pour les numéros de téléphone : tel:<phonenumber>.
    (réf : https://datatracker.ietf.org/doc/html/rfc3966)

    Si le numéro semble être un numéro de téléphone français valide,
    il est standardisé sous la forme <tel:+33-x-xx-xx-xx-xx>.

    >>> owlThingFromTel("0123456789")
    rdflib.term.URIRef('tel:+33-1-23-45-67-89')
    """

    telStr = re.sub("^tel[:]", "", telStr)
    red = re.sub(r"[.\s-]", "", telStr)
    tel = ""

    if addPrefixFr:
        a = re.match(r"0(\d{9})$", red)
        # numéro français local
        
        if a:
            red = "+33" + a[1]

    if re.match(r"[+]33\d{9}$", red):
    # numéro français global
    
        for i in range(len(red)):
            if i == 3 or i > 2 and i%2 == 0:
                tel = tel + "-" + red[i]
            else:
                tel = tel + red[i]

    else:
        tel = re.sub(r"(\d)\s(\d)", r"\1-\2", telStr).strip(" ")
        # les espaces entre les chiffres sont remplacés par des tirets,
        # ceux en début et fin de chaine sont supprimés

        l = [i for i in '<> "{}|\\^`' if i in tel]

        if l and not l == []:          
            raise ValueError("Invalid IRI. Forbiden character '{}' in phone number '{}'.".format("".join(l), telStr))

    if tel and not tel == "":
        return URIRef("tel:" + tel)
        

    
