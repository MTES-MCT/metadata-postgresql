"""
Utilitary functions for parsing and serializing RDF metadata.

Les fonctions suivantes permettent :
- d'extraire des métadonnées en JSON-LD d'une chaîne de
caractères balisée et les désérialiser sous la forme d'un
graphe ;
- de traduire ce graphe en un dictionnaire de catégories
de métadonnées qui pourra alimenter un formulaire ;
- en retour, de reconstruire un graphe à partir d'un
dictionnaire de métadonnées (et de l'identifiant du jeu de
données) ;
- de sérialiser ce graphe en JSON-LD et l'inclure dans
une chaîne de caractères balisée ;
- en complément, d'obtenir la liste de valeurs admissibles
pour un champ dont le vocabulaire est contrôlé par une
ontologie sous une forme lisible par un être humain.

Dépendances : rdflib, rdflib-jsonld et requests.

Processus d'utilisation type :

0. partant du principe que c_source contient le commentaire/la description
d'un objet PostgreSQL.

On pourra utiliser l'exemple contenu dans le répertoire exemple :
>>> with open('exemples\\exemple_commentaire_pg.txt', encoding='UTF-8') as src:
...    c_source = src.read()

1. chargement du modèle des métadonnées communes :
>>> with open('shape.ttl', encoding='UTF-8') as src:
...    shape = Graph().parse(data=src.read(), format='turtle')

Ce n'est pas obligatoire - il s'agit d'un paramètre optionnel
dans les fonctions suivantes - mais il peut être judicieux de
stocker une bonne fois pour toute l'identifiant du modèle,
pour éviter que chaque fonction retourne le chercher.
>>> id_template = fetchUUID(dataset_template)

Dans la même logique, on améliorera légèrement la performance
en récupérant en amont dans le modèle un dictionnaire des préfixes
utilisés dans les chemins SPARQL (cf. plus loin) :
>>> prefixes = buildNSDict(dataset_template)

2. import des vocabulaires contrôlés :
>>> with open('ontologies.ttl', encoding='UTF-8') as src:
...    vocabulary = Graph().parse(data=src.read(), format='turtle')

3. extraction et dé-sérialisation sous forme d'un graphe RDF :
>>> g_source = extractMetadata(c_source, dataset_template)

4. stockage de l'identifiant du jeu de données :
>>> id_dataset = fetchUUID(g_source)

Si le commentaire était vierge de métadonnées strucurées, l'identifiant
n'existera pas encore à ce stade (et sera automatiquement créé par
la fonction buildGraph utilisée ensuite), mais None ou pas, il faut
l'avoir récupéré.

5. traduction du graphe en dictionnaire :
>>> d = buildDict(g_source, dataset_template, vocabulary,
...     datasetUUID=id_dataset, templateUUID=id_template,
...     prefixDict=prefixes)

Le dictionnaire utilise comme clés des chemins SPARQL qui identifient
les catégories de métadonnées. Par exemple, "dct:title" pour le nom du
jeu de données, ou "dct:publisher / foaf:name" pour le nom de l'entité
qui publie la donnée.

Pour être valide, un chemin sur plusieurs niveaux doit être identifié
dans le modèle (par ex "dct:publisher / dct:title" ne serait pas accepté).
À ce stade, il est possible de définir librement des chemins à un seul
niveau, sous réserve que les préfixes utilisés - "dct" pour "dct:title",
par ex - soient connus du modèle (p in prefixes) ou, et c'est encore le
plus simple, que les IRI ne soient pas abrégés.

Ainsi, pour les métadonnées locales, il serait possible d'utiliser comme
clés des UUID, sous la forme "<urn:uuid:218c1245-6ba7-4163-841e-476e0d5582af>".

Les valeurs du dictionnaire sont des listes de chaînes de caractères,
correspondant aux valeurs prises par la propriété pour le jeu de données.
Il peut bien entendu n'y en avoir qu'une, mais la valeur saisie dans
le dictionnaire doit être une liste quoi qu'il arrive.

Par exemple :
{'dct:title': ['ADMIN EXPRESS - Départements de métropole'],
'dcat:keyword': ['ign', 'donnée externe', 'admin express']}

Une fois constitué, le dictionnaire peut alimenter un formulaire de
saisie, qui le mettra à jour en retour.

Les étapes suivantes décrivent l'encodage des informations mises
à jour dans le commentaire.

6. génération d'un graphe contenant les métadonnées actualisées :
>>> g_updated = buildGraph(d, dataset_template, vocabulary,
...     datasetUUID=id_dataset, templateUUID=id_template,
...     prefixDict=prefixes)

Le typage des valeurs (toutes représentées par des chaînes de
caractère dans le dictionnaire) est réalisé grâce au modèle.

7. mise à jour du commentaire :
>>> c_updated = updateDescription(c_source, g_updated)

NB : Les fonctions buildGraph et buildDict admettent un paramètre
optionnel language, qui permet de spécifier la langue des
métadonnées. Par défaut, elles sont considérées comme étant
rédigées en français. Dans tous les cas la langue est, à ce
stade, considérée comme homogène pour toutes les métadonnées.


Vocabulaire contrôlé :

Pour certaines catégories de métadonnées identifiées comme telles
dans le modèle, seules les valeurs spécifiées dans une ontologie
particulière peuvent être utilisées. En RDF, ce sont alors les IRI
identifiant les termes qui sont stockés, toutefois - grâce au
vocabulaire importé à l'étape 2 ci-avant - ce sont bien les labels
français explicites qui figureront dans le dictionnaire.

Pour la constitution du formulaire, il pourra être utile de
connaître les propriétés dont le vocabulaire est contrôlé et,
le cas échéant, de disposer de la liste des termes admis.
Pour ce faire, on pourra utiliser la fonction fetchVocabulary qui
prend en entrée le chemin SPARQL d'une propriété (= la clé du
dictionnaire) et renvoie la liste des valeurs autorisées si le
vocabulaire est contrôlé, None sinon. La liste est triée par
ordre alphabétique selon la locale de l'utilisateur.

Par exemple :
>>> l = fetchVocabulary("dcat:theme", dataset_template, vocabulary,
...     templateUUID=id_template, prefixDict=prefixes)

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


def buildNSDict(graph: Graph) -> Dict[str, Namespace]:
    """Return a dictionary of all namespaces (as values) and matching prefixes (as keys) from given graph.

    - graph est un graphe RDF.

    Résultat : un dictionnaire dont les clés sont les préfixes
    définis dans le graphe et les valeurs les espaces de nommage
    correspondants.

    >>> buildNSDict(Graph())
    {'xml': Namespace('http://www.w3.org/XML/1998/namespace'),
    'rdf': Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#'),
    'rdfs': Namespace('http://www.w3.org/2000/01/rdf-schema#'),
    'xsd': Namespace('http://www.w3.org/2001/XMLSchema#')}

    >>> buildNSDict(dataset_template)
    """

    d = dict()

    for p, u in graph.namespace_manager.namespaces():

        d.update( { p : Namespace(str(u)) } )

    return d


def fetchUUID(graph: Graph, prefixDict: Dict[str, Namespace] = None) -> URIRef:
    """Get dataset UUID from metadata graph of said dataset.

    - graph est un graphe RDF.
    - prefixDict est un dictionnaire de préfixes d'espaces de nommage.
    S'il n'est pas renseigné, seuls les préfixes déclarés dans le graphe
    seront reconnus.

    Résultat : un objet de type URIRef contenant l'identifiant
    (sujet du triple "?uuid a dcat:Dataset"), présumé unique,
    contenu dans le graphe.

    Si le graphe contient plus d'un triple "?uuid a dcat:Dataset", la
    fonction ne renvoie rien.

    >>> fetchUUID(dataset_template)
    rdflib.term.URIRef('urn:uuid:5c78c95d-d9ff-4f95-8e15-dd14cbc6cced')
    """

    try:
        
        q = graph.query(
            """
            SELECT
                ?u
            WHERE
                { ?u a dcat:Dataset . }
            """,
            initNs = prefixDict
            )
    except:
        return

    if len(q) == 1:
        for row in q:
            return row.u

      

def testPath(graph: Graph, mPath: str, prefixDict: Dict[str, Namespace] = None,
         datasetUUID: URIRef = None) -> bool:
    """Check existence of path mPath in given graph object.

    - graph est un graphe RDF.
    - mPath est une chaîne de caractères présumée correspondre à un chemin SPARQL.
    - datasetUUID est un objet de type URIRef correspondant à l'identifiant du jeux
    de données considéré. S'il n'est pas renseigné, la fonction ira le récupérer
    dans le graphe.
    - prefixDict est un dictionnaire de préfixes d'espaces de nommage. S'il n'est
    pas renseigné, seuls les préfixes déclarés dans le graphe seront reconnus.

    Résultat : True si le chemin mPath est présent dans le graphe ou s'il s'agit
    d'une chaîne de caractères vide (""). False dans tous les autres cas, y compris
    si le chemin est invalide.

    >>> testPath(dataset_template, "dcat:distribution / dct:licence / rdfs:label")
    True

    >>> testPath(dataset_template, "")
    True

    >>> testPath(dataset_template, "N'importe quoi")
    False
    """

    if mPath == "":
        return True

    if datasetUUID is None:        
        datasetUUID = fetchUUID(graph, prefixDict)

    try:
        
        q = graph.query(
            """
            ASK
                {{ ?u {} ?o }}
            """.format(mPath),
            initNs = prefixDict,
            initBindings = { 'u' : datasetUUID }
            )

    except:
        return False
    else:
        return bool(q)


def fetchValue(graph: Graph, mPath: str, prefixDict: Dict[str, Namespace] = None,
           datasetUUID: URIRef = None) -> List[Union[URIRef, Literal]]:
    """Return a list of metadata values at path mPath in given graph if any.

    - graph est un graphe RDF.
    - mPath est une chaîne de caractères présumée correspondre à un chemin SPARQL.
    - datasetUUID est l'identifiant du jeux de données considéré. S'il n'est
    pas renseigné, la fonction ira le récupérer dans le graphe.
    - prefixDict est un dictionnaire de préfixes d'espaces de nommage. S'il n'est
    pas renseigné, seuls les préfixes déclarés dans le graphe seront reconnus.

    Résultat : la liste des valeurs contenues dans le graphe pour la propriété
    identifiée par le chemin, présumées toutes se rapporter au même sujet. Les
    valeurs peuvent être de type Literal ou URIRef.

    Si le chemin est invalide ou n'existe pas, la fonction ne renvoie rien.

    >>> fetchValue(dataset_template, "dcat:distribution / dct:licence / rdfs:label")
    rdflib.term.Literal('Licence ouverte Etalab.', lang='fr')
    """

    if mPath == "":
         return

    if datasetUUID is None:        
        datasetUUID = fetchUUID(graph, prefixDict)

    try:
        q = graph.query(
            """
            SELECT
                ?o
            WHERE
                {{ ?u {} ?o }}
            """.format(mPath),
            initNs = prefixDict,
            initBindings = { 'u' : datasetUUID }
            )

    except:
        return

    if len(q) > 0:

        l = [row.o for row in q]
            
        return l
    


def fetchType(mPath: str, gTemplate: Graph, prefixDict: Dict[str, Namespace] = None,
          templateUUID: URIRef = None) -> URIRef:
    """Fetch the rdf:type object at path in given template graph if any.

    - mPath est une chaîne de caractères présumée correspondre à un chemin SPARQL
    identifiant la propriété considérée.
    - gTemplate est un modèle de graphe qui explicite les classes (rdf:type)
    des catégories de métadonnées. 
    - prefixDict est un dictionnaire de préfixes d'espaces de nommage. S'il n'est
    pas renseigné, seuls les préfixes définis dans gTemplate seront reconnus.
    - templateUUID est un objet de type URIRef correspondant à l'identifiant du jeu
    de données type décrit dans gTemplate. S'il n'est pas renseigné, la fonction ira
    le récupérer dans gTemplate.

    Résultat : un objet de type URIRef correspondant à la classe RDF de l'objet.

    Si le chemin est invalide, non reconnu ou a plus d'une occurence dans le
    graphe, la fonction ne renvoie rien.
    
    >>> fetchType("dcat:distribution / dct:licence", dataset_template)
    rdflib.term.URIRef('http://purl.org/dc/terms/LicenseDocument')
    """

    if mPath == "":
         return

    if templateUUID is None:        
        templateUUID = fetchUUID(gTemplate, prefixDict)

    try:
        q = gTemplate.query(
            """
            SELECT
                ?o
            WHERE
                {{ ?u {} [ a ?o ] }}
            """.format(mPath),
            initNs = prefixDict,
            initBindings = { 'u' : templateUUID }
            )
    except:
        return

    if len(q) == 1:

        for row in q:
            
            return row.o


def fetchDataType(mPath: str, gTemplate: Graph, prefixDict: Dict[str, Namespace] = None,
          templateUUID: URIRef = None) -> URIRef:
    """Fetch the datatype of the Literal at path in given template graph if any.

    - mPath est une chaîne de caractères présumée correspondre à un chemin SPARQL
    identifiant la propriété considérée.
    - gTemplate est un modèle de graphe qui explicite les types xsd attendues
    pour les catégories de métadonnées de type rfds:Literal via des propriétés
    sh:datatype.
    - prefixDict est un dictionnaire de préfixes d'espaces de nommage. S'il n'est
    pas renseigné, seuls les préfixes définis dans gTemplate seront reconnus.
    - templateUUID est un objet de type URIRef correspondant à l'identifiant du jeu
    de données type décrit dans gTemplate. S'il n'est pas renseigné, la fonction ira
    le récupérer dans gTemplate.

    Résultat : un objet de type URIRef correspondant au type de Literal
    attendu pour la propriété.

    La fonction ne renvoie rien pour les Literal de type xsd:string.

    Si le chemin est invalide, non reconnu, a plus d'une occurence dans le
    graphe, ou pointe sur une valeur qui n'est pas de type Literal, la
    fonction ne renvoie rien.

    >>> fetchDataType("dct:temporal / dcat:startDate", dataset_template)
    rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#date')
    """

    if mPath == "":
         return

    if templateUUID is None:        
        templateUUID = fetchUUID(gTemplate, prefixDict)

    try:
        q = gTemplate.query(
            """
            SELECT
                ?o
            WHERE
                {{ ?u {} [ sh:datatype ?o ] }}
            """.format(mPath),
            initNs = prefixDict,
            initBindings = { 'u' : templateUUID }
            )
    except:
        return

    if len(q) == 1:

        for row in q:
            
            return row.o



def fetchVocabulary(mPath: str, gTemplate: Graph, vocabulary: Graph,
            prefixDict: Dict[str, Namespace] = None,
            templateUUID: URIRef = None, language:str = "fr") -> List[str]:
    """Return a list of possible values for property mPath if bound by an ontology.

    - mPath est une chaîne de caractères présumée correspondre à un chemin SPARQL
    identifiant la propriété considérée.
    - language est la langue attendue pour les valeurs listées, français par défaut.
    - gTemplate est un modèle de graphe qui explicite les ontologies à utiliser via
    des propriétés skos:inScheme.
    - vocabulary est un graphe réunissant le vocabulaire de toutes les ontologies
    pertinentes.
    - templateUUID est l'identifiant du jeu de données type décrit dans gTemplate.
    S'il n'est pas renseigné, la fonction ira le récupérer dans gTemplate.
    - prefixDict est un dictionnaire de préfixes d'espaces de nommage. S'il n'est
    pas renseigné, il est déduit de gTemplate.

    Résultat : liste contenant les valeurs (chaînes de caractères) admissibles pour
    la propriété visée.

    La fonction ne renvoie rien si le chemin mPath n'existe pas dans gTemplate ou 
    si le vocabulaire de la propriété correspondante n'est pas contrôlé.

    Les valeurs sont triées par ordre alphabétique selon la locale de l'utilisateur.

    >>> fetchVocabulary("dcat:theme", dataset_template, vocabulary)
    ['Agriculture, pêche, sylviculture et alimentation', 'Données provisoires',
    'Économie et finances', 'Éducation, culture et sport', 'Énergie', 'Environnement',
    'Gouvernement et secteur public', 'Justice, système juridique et sécurité publique',
    'Population et société', 'Questions internationales', 'Régions et villes', 'Santé',
    'Science et technologie', 'Transports']
    """

    if mPath == "":
         return

    if templateUUID is None:        
        templateUUID = fetchUUID(gTemplate, prefixDict)

    if prefixDict == None:
        prefixDict = buildNSDict(gTemplate)

    try:
        q1 = gTemplate.query(
            """
            SELECT
                ?o
            WHERE
                {{ ?u {} [ skos:inScheme ?o ] }}
            """.format(mPath),
            initNs = prefixDict,
            initBindings = { 'u' : templateUUID }
            )
    except:
        return

    if len(q1) == 1:

        for r1 in q1:

            q2 = vocabulary.query(
                """
                SELECT
                    ?l
                WHERE
                    {{ ?s a skos:Concept ;
                    skos:inScheme ?o ;
                    skos:prefLabel ?l .
                      FILTER ( lang(?l) = "{}" ) }}
                """.format(language),
                initNs = prefixDict,
                initBindings = { 'o' : r1.o }
                )

            if len(q2) > 0:

                setlocale(LC_COLLATE, "")

                return sorted(
                    [str(r2.l) for r2 in q2],
                    key=lambda x: strxfrm(x)
                    )


def fetchConceptFromValue(mPath: str, litValue: Union[Literal, str], gTemplate: Graph,
              vocabulary: Graph, prefixDict: Dict[str, Namespace] = None,
              templateUUID: URIRef = None, language: str = "fr") -> Tuple[bool, URIRef]:
    """Return the skos:Concept IRI matching given literral value for property mPath if any.

    - mPath est une chaîne de caractères présumée correspondre à un chemin SPARQL
    identifiant la propriété considérée.
    - litValue est une chaîne de caractères ou un objet de type rdflib.term.Literal
    correspondant à la transcription littérale de la valeur prise par la propriété
    (skos:prefLabel). À noter litValue sera toujours considéré comme de type
    xsd:string et la langue du Literal sera toujours ignorée (language fait foi).
    - gTemplate est un modèle de graphe qui explicite les ontologies à utiliser via
    des propriétés skos:inScheme.
    - gVocabylary est un graphe réunissant le vocabulaire de toutes les ontologies
    pertinentes.
    - prefixDict est un dictionnaire de préfixes d'espaces de nommage. S'il n'est
    pas renseigné, il est déduit de gTemplate.
    - templateUUID est un objet de type URIRef correspondant à l'identifiant du jeu
    de données type décrit dans gTemplate. S'il n'est pas renseigné, la fonction ira
    le récupérer dans gTemplate.
    - language est la langue de litValue, français par défaut.

    Résultat : un tuple formé (0) d'un booléen indiquant si le vocabulaire est contrôlé
    pour la propriété considérée et, si elle existe, (1) de l'IRI recherchée.

    >>> fetchConceptFromValue("dcat:theme", "Transports", dataset_template, vocabulary)
    (True, rdflib.term.URIRef('http://publications.europa.eu/resource/authority/data-theme/TRAN'))
    
    >>> fetchConceptFromValue("dcat:theme", Literal("Transports", lang="fr"), dataset_template, vocabulary)
    (True, rdflib.term.URIRef('http://publications.europa.eu/resource/authority/data-theme/TRAN'))
    
    >>> fetchConceptFromValue("dcat:theme", "N'existe pas", dataset_template, vocabulary)
    (True,)

    >>> fetchConceptFromValue("dct:title", "Vocabulaire non contrôlé", dataset_template, vocabulary)
    (False,)
    """

    if mPath == "" or str(litValue) == "":
         return False, 

    if templateUUID is None:        
        templateUUID = fetchUUID(gTemplate, prefixDict)

    if prefixDict == None:
        prefixDict = buildNSDict(gTemplate)

    try:
        q1 = gTemplate.query(
            """
            SELECT
                ?o
            WHERE
                {{ ?u {} [ skos:inScheme ?o ] }}
            """.format(mPath),
            initNs = prefixDict,
            initBindings = { 'u' : templateUUID }
            )
    except:
        return False,

    if len(q1) == 1:

        for r1 in q1:

            q2 = vocabulary.query(
                """
                SELECT
                    ?s
                WHERE
                    { ?s a skos:Concept ;
                    skos:inScheme ?o ;
                    skos:prefLabel ?l }
                """,
                initNs = prefixDict,
                initBindings = { 'o' : r1.o, 'l' : Literal(litValue, lang=language) }
                )

            if len(q2) == 1:

                for r2 in q2:
                    return True, r2.s

            else:
                return True,

    elif len(q1) > 1:
        raise RuntimeError("More than one ontology referenced for path '{}'. This shouldn't happen.".format(mPath))

    else:
        return False,


def fetchValueFromConcept(conceptIRI: URIRef, vocabulary, language: str = "fr") -> str:
    """Return the skos:prefLabel strings matching given conceptIRI and its scheme.

    - conceptIRI est un objet de type rdflib.term.URIRef supposément référencé
    dans une ontologie.  
    - vocabulary est un graphe réunissant le vocabulaire de toutes les ontologies
    pertinentes.
    - language est la langue attendue pour la valeur littérale résultante, français
    par défaut.
    
    Si aucune valeur n'est disponible pour la langue spécifiée, la fonction retournera
    la traduction française (si elle existe).

    Résultat : une tuple contenant deux chaînes de caractères. [0] est le libellé
    explicite défini pour la valeur. [1] est le nom de l'ontologie.
    (None, None) si l'IRI n'est pas répertorié.
    
    Dans l'exemple ci-après, il existe une traduction française et anglaise pour le terme
    recherché, mais pas de version espagnole.

    >>> u = URIRef("http://publications.europa.eu/resource/authority/data-theme/TRAN")
    
    >>> fetchValueFromConcept(u, vocabulary)
    ('Transports', 'Thèmes de données (UE)')
    
    >>> fetchValueFromConcept(u, vocabulary, 'en')
    ('Transport', 'Data theme (EU)')
    
    >>> fetchValueFromConcept(u, vocabulary, 'es')
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
        return str( t['label'] ), str( t['scheme'] )
        
    return (None, None)
    
    


def emailFromOwlThing(thingIRI: URIRef) -> str:
    """Return a string human-readable version of an owl:Thing IRI representing an email adress.

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

    
    

def buildGraph(metaDict: Dict[str, List[str]], gTemplate: Graph, vocabulary: Graph = None,
           datasetUUID: URIRef = None, templateUUID: URIRef = None,
           prefixDict: Dict[str, Namespace] = None, language: str = "fr") -> Graph:
    """Return a graph object build from dictionary metaDict using paths as key and metada values as values.

    - metaDict est un dictionnaire dont les clés sont des chemins identifiant des
    catégories de métadonnées et les valeurs des listes de chaînes de caractères
    correspondant aux valeurs saisies pour ces catégories.
    - gTemplate est un modèle de graphe contenant l'arborescence des catégories de
    métadonnées (hors catégories définies localement par le service) et les types de
    valeurs attendus.
    - gVocabylary est un graphe réunissant le vocabulaire de toutes les ontologies
    pertinentes.
    - datasetUUID est un objet de type URIRef correspondant à l'identifiant du jeux
    de données considéré. S'il n'est pas spécifé, un nouvel identifiant est généré.
    - templateUUID est un objet de type URIRef correspondant à l'identifiant du jeu
    de données type décrit dans gTemplate. S'il n'est pas renseigné, la fonction ira
    le récupérer dans gTemplate.
    - prefixDict est un dictionnaire de préfixes d'espaces de nommage. S'il n'est
    pas renseigné, les préfixes du modèle seront utilisés.
    - language est la langue de rédaction des métadonnées, présumée homogène.

    Résultat : un Graph RDF de métadonnées.

    >>> h = buildGraph(d0, dataset_template, vocabulary)
    >>> h = buildGraph(d0, dataset_template, vocabulary , URIRef("urn:uuid:a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"))
    """

    if prefixDict == None:
        prefixDict = buildNSDict(gTemplate)
        

    if templateUUID is None:
        templateUUID = fetchUUID(gTemplate, prefixDict)
    else:
        if not isinstance(templateUUID, URIRef):
            raise TypeError("templateUUID should be an URIRef object.")
        

    if datasetUUID is None:
        datasetUUID = URIRef("urn:uuid:" + str(uuid.uuid4()))
    else:
        if not isinstance(datasetUUID, URIRef):
            raise TypeError("datasetUUID should be an URIRef object.")
        

    graph = Graph()

    for k, v in prefixDict.items():    
        graph.namespace_manager.bind(k, v)
        
        graph.update(
            """
            INSERT
                { ?u a dcat:Dataset }
            WHERE
                { }
            """,
            initNs = prefixDict,
            initBindings = { 'u' : datasetUUID }
            )                

    for k, v in metaDict.items():

        if all(y is None or y == "" for y in v or []) or k is None or k == "":
            # on ignore les listes de valeurs ou clés vides
            continue

        if not testPath(gTemplate, k):
            if " / " in k:
                raise KeyError("Invalid path '{}'. Path can't have more than one level if not referenced in template.".format(k))


        l = list(reversed(re.split(r'\s*[/]\s*', k)))

        p = l.pop()

        c = ""

        while not l == []:

            if c == "":               
                d = p              
            else:   
                d = c + " / " + p

            if not testPath(graph, d, prefixDict, datasetUUID):

                t = fetchType(d, gTemplate, prefixDict, templateUUID)

                if c == "":
                    
                    graph.update(
                        """
                        INSERT
                            {{ ?u {} [ a ?t ] }}
                        WHERE
                            {{ }}
                        """.format(p),
                        initNs = prefixDict,
                        initBindings = { 't' : t, 'u' : datasetUUID }
                        )
                    
                else:
                    graph.update(
                        """
                        INSERT
                            {{ ?o {} [ a ?t ] }}
                        WHERE
                            {{ ?u {} ?o }}
                        """.format(p, c),
                        initNs = prefixDict,
                        initBindings = { 't' : t, 'u' : datasetUUID }
                        )


            c = d

            p = l.pop()
                    
        for f in v:

            e = None

            if f and not f == "":

                if not c == "":
                    z = c + " / " + p
                else:
                    z = p
                

                t = fetchType(z, gTemplate, prefixDict, templateUUID)

                if t is None: # cas d'une catégorie locale non référencée dans le modèle

                    e = Literal(f, lang=language)

                elif t == URIRef("http://www.w3.org/2000/01/rdf-schema#Literal") :
                    # métadonnée de type rdf.Literal

                    dt = fetchDataType(z, gTemplate, prefixDict, templateUUID)

                    if dt or p == "dct:identifier":
                        e = Literal(f, datatype=dt)
                    else:
                        e = Literal(f, lang=language)
                        
                else :

                    if vocabulary:

                        # vocabulaire contrôlé ?
                        b = fetchConceptFromValue(z, f, gTemplate, vocabulary, prefixDict, templateUUID, language)

                        if b[0] and len(b) == 2:
                            e = b[1]
                        elif b[0]:
                            raise ValueError("Controlled vocabulary. '{}' isn't an authorized value for property '{}'.".format(f, str(k)))

                    if p in ("vcard:hasTelephone", "foaf:phone"):
                        e = owlThingFromTel(f)

                    if p in ("vcard:hasEmail", "foaf:mbox"):
                        e = owlThingFromEmail(f)

                    if e is None:
                    
                        # toutes autres métadonnées sont présumées être des
                        # IRI. On vérifie toutefois que la valeur ne contient aucun
                        # caractère interdit qui ferait échouer la sérialisation.
                        if not all(map(lambda x: not x in '<>" {}|\\^`', f)):
                            raise ValueError("Invalid IRI. Forbiden character in value '{}' for key '{}'. Not allowed : <>\" {{}}|\\^`".format(f, str(k)))
                            
                        e = URIRef(f)

                if c == "":

                    graph.update(
                        """
                        INSERT
                            {{ ?u {} ?e }}
                        WHERE
                            {{  }}
                        """.format(p),
                        initNs = prefixDict,
                        initBindings = { 'e' : e, 'u' : datasetUUID }
                        )                    
                    
                else:  
                    graph.update(
                        """
                        INSERT
                            {{ ?o {} ?e }}
                        WHERE
                            {{ ?u {} ?o }}
                        """.format(p, c),
                        initNs = prefixDict,
                        initBindings = { 'e' : e, 'u' : datasetUUID }
                        )

    return graph

             

def buildDict(
    graph: Graph,
    shape: Graph,
    vocabulary: Graph,
    template: dict = dict(),
    mode: str = 'edit',
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
    mDict: dict = None
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
    [0] d'un index, qui définit le placement vertical du widget dans la grille (QGridLayout) qui
    organise tous les widgets rattachés au groupe parent (QGroupBox).
    [1] de la clé du groupe parent.
    [2] dans quelques cas, la lettre M, indiquant que le widget est la version "manuelle" d'un
    widget normalement abondé par un ou plusieurs thésaurus. Celui-ci a la même clé sans "M"
    (même parent et même index, donc même placement dans la grille). Ces deux widgets sont
    supposés être substitués l'un à l'autre dans la grille lorque l'utilisateur active ou
    désactive le "mode manuel" (cf. 'switch source widget' ci-après)
    

    Description des clés des dictionnaires internes :
    
    - 'object' : classification des éléments du dictionnaire. "group of values" ou
    "group of properties" ou "translation group" ou "edit" ou "plus button" ou "translation button".
    Les "translation group" et "translation button" ne peuvent exister que si l'argument
    "translation" vaut True.

    Les clés 'widget X' ci-après ont vocation à accueillir les futurs widgets (qui ne sont pas
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
    

    Les clés suivantes sont elles remplies par la fonction, avec toutes les informations nécessaires
    au paramétrage des widgets.
    
    - 'main widget type'* : type du widget principal (QGroupBox, QLineEdit...).
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
    et template.
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

    La dernière série de clés ne sert qu'aux fonctions de rdf_utils : 'default value'* (valeur par
    défaut), 'multiple values'* (la catégorie est-elle censée admettre plusieurs valeurs ?),
    'node kind', 'data type'**, 'class', 'path'***, 'subject', 'predicate', 'node', 'transform',
    'default widget type', 'one per language'.

    * ces clés apparaissent aussi dans le dictionnaire interne de template.
    ** le dictionnaire interne de template contient également une clé 'data type', mais dont les
    valeurs sont des chaînes de catactères parmi 'string', 'boolean', 'decimal', 'integer', 'date',
    'time', 'dateTime', 'duration' (et non des objets de type URIRef).
    *** le chemin est la clé principale de template.
           
    >>> buildDict(graph, shape, template, vocabulary)
    """

    nsm = mNSManager or shape.namespace_manager
    
    # ---------- INITIALISATION ----------
    # uniquement à la première itération de la fonction
    
    if (mParentNode and mParentWidget and mTargetClass and mDict and mPath and mWidgetDictTemplate) is None:

        for n, u in nsm.namespaces():
            graph.namespace_manager.bind(n, u, override=True, replace=True)

        mTargetClass = URIRef("http://www.w3.org/ns/dcat#Dataset")
        mPath = None

        # récupération de l'identifiant
        # du jeu de données dans le graphe, s'il existe
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
            
            'main widget type' : None,
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
            'one per language' : None,
            'authorized languages' : None
            }

        # on initialise le dictionnaire avec un groupe racine :
        mParentWidget = (0,)
        
        mDict = { mParentWidget : mWidgetDictTemplate.copy() }
        mDict[mParentWidget].update( {
            'object' : 'group of properties',
            'main widget type' : 'QGroupBox'
            } )


    # ---------- EXECUTION COURANTE ----------

    idx = dict( { mParentWidget : 0 } )

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
        mLangList = None

        # on extrait la ou les valeurs éventuellement
        # renseignées dans le graphe pour cette catégorie
        # et le sujet considéré
        q_gr = graph.query(
            """
            SELECT
                ?value
            WHERE
                 { ?n ?p ?value . }
            """,
            initBindings = { 'n' : mParentNode, 'p' : mProperty }
            )

        # exclusion des catégories qui ne sont pas prévues par
        # le modèle et n'ont pas de valeur renseignée
        if len(q_gr) == 0 and not len(template) == 0 and ( not mPath in template ):
            continue

        # récupération de la liste des ontologies
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

        if mSources and p['default']:
            mDefaultTrad = fetchValueFromConcept(p['default'], vocabulary, language)[1]            
        
        t = template.pop(mPath, dict()) if template else dict()
        
        values = [ v['value'] for v in q_gr ] or [ None ]
        multilingual = p['unilang'] and bool(p['unilang']) or False
        multiple = ( p['max'] is None or int( p['max'] ) > 1 ) and not multilingual
        
        if translation and multilingual:
            mLangList = [ l for l in langList or [] if not l in [ v.language for v in values if isinstance(v, Literal) ] ]
            # à ce stade, mLangList contient toutes les langues de langList pour lesquelles
            # aucune tranduction n'est disponible. On y ajoutera ensuite la langue de la valeur
            # courante pour obtenir la liste à afficher dans son widget de sélection de langue
        
        if ( translation and multilingual ) or multiple or len(values) > 1 :
            
            # si la catégorie admet plusieurs valeurs uniquement s'il
            # s'agit de traductions, on référence un widget de groupe
            mWidget = ( idx[mParent], mParent )
            mDict.update( { mWidget : mWidgetDictTemplate.copy() } )
            mDict[mWidget].update( {
                'object' : 'translation group' if ( multilingual and translation ) else 'group of values',
                'main widget type' : 'QGroupBox',
                'label' : t.get('name', None) or str(p['name']),
                'help text' : t.get('help text', None) or ( str(p['descr']) if p['descr'] else None )
                } )

            idx[mParent] += 1
            idx.update( { mWidget : 0 } )
            mParent = mWidget
            # les widgets de saisie référencés juste après auront
            # ce widget de groupe pour parent


        # --- BOUCLE SUR LES VALEURS
        
        for mValueBrut in values:
            
            mValue = None
            mCurSource = None
            mLabel = ( t.get('name', None) or str(p['name']) ) if not ( multiple or len(values) > 1
                        or ( multilingual and translation ) ) else None
            mHelp = ( t.get('help text', None) or ( str(p['descr']) if p['descr'] else None ) ) if not (
                        multiple or len(values) > 1 or ( multilingual and translation ) ) else None
            mLanguage = ( ( mValueBrut.language if isinstance(mValueBrut, Literal) else None ) or language ) if (
                        mKind == 'sh:Literal' and p['type'].n3(nsm) == 'xsd:string' ) else None
            
            # cas d'un noeud vide :
            # on ajoute un groupe et on relance la fonction sur la classe du noeud
            if mKind in ( 'sh:BlankNode', 'sh:BlankNodeOrIRI' ):

                mNode = mValueBrut if isinstance(mValueBrut, BNode) else BNode()

                if mKind == 'sh:BlankNodeOrIRI':
                    mSources = ( mSources + [ "< manuel >" ] ) if mSources else [ "< URI >", "< manuel >" ]
                    mCurSource = "< manuel >" if isinstance(mValueBrut, BNode) else None

                mWidget = ( idx[mParent], mParent, 'M' ) if mKind == 'sh:BlankNodeOrIRI' else ( idx[mParent], mParent )
                mDict.update( { mWidget : mWidgetDictTemplate.copy() } )
                mDict[mWidget].update( {
                    'object' : 'group of properties',
                    'main widget type' : 'QGroupBox',
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
                    
                idx.update( { mWidget : 0 } )

                buildDict(graph, shape, vocabulary, template, mode, language, translation, langList, labelLengthLimit, valueLengthLimit,
                      textEditRowSpan, mNPath, p['class'], mWidget, mNode, mNSManager, mWidgetDictTemplate, mDict)


            # pour tout ce qui n'est pas un pur noeud vide :
            # on ajoute un widget de saisie, en l'initialisant avec
            # une représentation lisible de la valeur
            if not mKind == 'sh:BlankNode':

                if isinstance(mValueBrut, BNode):
                    mValueBrut = None
                    
                if  multilingual and translation and mLanguage:
                    mLangList = mLangList + [ mLanguage ] if not mLanguage in mLangList else mLangList
                elif translation and mLanguage:
                    mLangList = [ mLanguage ] + ( langList or [] ) if not mLanguage in ( langList or [] ) else langList
                
                # cas d'une catégorie qui tire ses valeurs d'une
                # ontologie : on récupère le label à afficher
                if isinstance(mValueBrut, URIRef) and mSources:             
                    mValue, mCurSource = fetchValueFromConcept(mValueBrut, vocabulary, language)
                    
                    if not mCurSource in mSources:
                        mCurSource = '< non répertorié >'

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
                mValue = mValue or ( str(mValueBrut) if mValueBrut else mDefault )

                mWidgetType = t.get('main widget type', None) or str(p['widget']) or "QLineEdit"
                mDefaultWidgetType = mWidgetType
                
                mLabelRow = None

                if mWidgetType == "QLineEdit" and mValue and ( len(mValue) > valueLengthLimit or mValue.count("\n") > 0 ):
                    mWidgetType = 'QTextEdit'

                if mWidgetType == 'QTextEdit' or ( mLabel and len(mLabel) > labelLengthLimit ):
                    mLabelRow = idx[mParent]
                    idx[mParent] += 1

                mDict.update( { ( idx[mParent], mParent ) : mWidgetDictTemplate.copy() } )
                mDict[ ( idx[mParent], mParent ) ].update( {
                    'object' : 'edit',
                    'main widget type' : mWidgetType,
                    'row span' : ( t.get('row span', None) or ( int(p['rowspan']) if p['rowspan'] else textEditRowSpan )
                               ) if mWidgetType == 'QTextEdit' else None,
                    'input mask' : t.get('input mask', None) or ( str(p['mask']) if p['mask'] else None ),
                    'label' : mLabel,
                    'label row' : mLabelRow,
                    'help text' : mHelp,
                    'value' : mValue,
                    'placeholder text' : t.get('placeholder text', None) or ( str(p['placeholder']) if p['placeholder'] else None ),
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
                    'tranform' : str(p['transform']) if p['transform'] else None,
                    'type validator' : 'QIntValidator' if p['type'] and p['type'].n3(nsm) == "xsd:integer" else (
                        'QDoubleValidator' if p['type'] and p['type'].n3(nsm) in ("xsd:decimal", "xsd:float", "xsd:double") else None ),
                    'multiple sources' : len(mSources) > 1 if mSources and mode == 'edit' else False,
                    'current source' : mCurSource,
                    'sources' : ( mSources or [] ) + '< non répertorié >' if mCurSource == '< non répertorié >' else mSources,
                    'one per language' : multilingual and translation,
                    'authorized languages' : mLangList if mode == 'edit' else None
                    } )
                
                idx[mParent] += 1

            # référencement d'un widget bouton pour ajouter une valeur
            # si la catégorie en admet plusieurs
            if mode == 'edit' and ( ( multilingual and translation and mLangList and len(mLangList) > 1 ) or multiple ):
            
                mDict.update( { ( idx[mParent], mParent ) : mWidgetDictTemplate.copy() } )
                mDict[ ( idx[mParent], mParent ) ].update( {
                    'object' : 'translation button' if multilingual else 'plus button',
                    'main widget type' : 'QToolButton'
                    } )
                
                idx[mParent] += 1
            


    # ---------- METADONNEES LOCALES DEFINIES PAR LE MODELE ----------
    
    if mTargetClass == URIRef("http://www.w3.org/ns/dcat#Dataset"):

        for meta, t in template.items():

            # à ce stade, ne restent dans le template que les
            # catégories locales / non communes

            if not isValidMiniPath(meta, nsm):
                # on élimine d'office les catégories locales dont
                # l'identifiant n'est pas un chemin SPARQL valide
                # à un seul élément et dont le préfixe éventuel
                # est déjà référencé
                continue

            mParent = mParentWidget

            mType = URIRef( "http://www.w3.org/2001/XMLSchema#" +
                    ( ( t.get('data type', None) ) or "string" ) )

            if not mType.n3(nsm) in ('xsd:string', 'xsd:integer', 'xsd:float', 'xsd:boolean'):
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

            values = [ v['value'] for v in q_gr ] or [ t.get('default value', None) ]

            multiple = t.get('multiple values', False)

            if multiple or len(values) > 1:
 
                mWidget = ( idx[mParent], mParent )
                mDict.update( { mWidget : mWidgetDictTemplate.copy() } )
                mDict[mWidget].update( {
                    'object' : 'group of values',
                    'main widget type' : 'QGroupBox',
                    'label' : t.get('name', None) or "???",
                    'help text' : t.get('help text', None)
                    } )

                idx[mParent] += 1
                idx.update( { mWidget : 0 } )
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
                mLabel = ( t.get('name', None) or "???" ) if not ( multiple or len(values) > 1 ) else None
                mLabelRow = None

                if mWidgetType == "QLineEdit" and mValue and ( len(mValue) > valueLengthLimit or mValue.count("\n") > 0 ):
                    mWidgetType = 'QTextEdit'

                if mWidgetType == 'QTextEdit' or ( mLabel and len(mLabel) > labelLengthLimit ):
                    mLabelRow = idx[mParent]
                    idx[mParent] += 1                

                mDict.update( { ( idx[mParent], mParent ) : mWidgetDictTemplate.copy() } )
                mDict[ ( idx[mParent], mParent ) ].update( {
                    'object' : 'edit',
                    'main widget type' : mWidgetType,
                    'row span' : t.get('row span', textEditRowSpan) if mWidgetType == 'QTextEdit' else None,
                    'input mask' : t.get('input mask', None),
                    'label' : mLabel,
                    'label row' : mLabelRow,
                    'help text' : t.get('help text', None) if not ( multiple or len(values) > 1 ) else None,
                    'value' : mValue,
                    'placeholder text' : t.get('placeholder text', None),
                    'language value' : mLanguage,
                    'is mandatory' : t.get('is mandatory', None),
                    'multiple values' : multiple,
                    'has minus button' : ( len(values) > 1 and mode == 'edit' ) or False,
                    'default value' : t.get('default value', None),
                    'node kind' : "sh:Literal",
                    'data type' : mType,
                    'subject' : mParentNode,
                    'predicate' : mProperty,
                    'path' : meta,
                    'default widget type' : mDefaultWidgetType,
                    'type validator' : 'QIntValidator' if mType.n3(nsm) == "xsd:integer" else (
                        'QDoubleValidator' if mType.n3(nsm) in ("xsd:decimal", "xsd:float", "xsd:double") else None ),
                    'authorized languages' : mLangList if mode == 'edit' else None
                    } )
                        
                idx[mParent] += 1

            if multiple and mode == 'edit':

                mDict.update( { ( idx[mParent], mParent ) : mWidgetDictTemplate.copy() } )
                mDict[ ( idx[mParent], mParent ) ].update( {
                    'object' : 'plus button',
                    'main widget type' : 'QToolButton'
                    } )
                
                idx[mParent] += 1


    # ---------- METADONNEES NON DEFINIES ----------
    # métadonnées présentes dans le graphe mais ni dans shape ni dans template
    
    if mTargetClass == URIRef("http://www.w3.org/ns/dcat#Dataset"):
        
        q_gr = graph.query(
            """
            SELECT
                ?property ?value
            WHERE
                { ?n ?property ?value . }
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
                    'label' : "???"
                    } )

                idx[mParent] += 1
                idx.update( { mWidget : 0 } )
                mParent = mWidget


            for v in dpv[p]:

                mValue = str(v)
                mWidgetType = 'QTextEdit' if ( len(mValue) > valueLengthLimit or mValue.count("\n") > 0 ) else "QLineEdit"
                mLabelRow = None

                if len(dpv[p]) == 1 and mWidgetType == 'QTextEdit':
                    mLabelRow = idx[mParent]
                    idx[mParent] += 1

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
                    'predicate' : mProperty,
                    'path' : p.n3(nsm),
                    'default widget type' : "QLineEdit",
                    'type validator' : 'QIntValidator' if mType.n3(nsm) == "xsd:integer" else (
                        'QDoubleValidator' if mType.n3(nsm) in ("xsd:decimal", "xsd:float", "xsd:double") else None ),
                    'authorized languages' : mLangList if mode == 'edit' else None
                    } )
                        
                idx[mParent] += 1

            # pas de bouton plus, faute de modèle indiquant si la catégorie
            # admet des valeurs multiples

    return mDict



def isValidMiniPath(path: str, mNSManager: NamespaceManager) -> bool:
    """Run basic validity test on SPARQL mono-element path.

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
    


def extractMetadata(description: str, gTemplate: Graph) -> Graph:
    """Get JSON-LD metadata from description and parse them into a graph.

    - description est une chaîne de caractères supposée correspondre à la
    description (ou les commentaire) d'un objet PostgreSQL.
    - gTemplate est un modèle de graphe contenant l'arborescence des catégories de
    métadonnées (hors catégories définies localement par le service). Il fournit
    ici les préfixes d'espaces de nommage à déclarer dans le graphe.

    Résultat : un graphe RDF déduit par désérialisation du JSON-LD.

    Le JSON-LD est présumé se trouver entre deux balises <METADATA> et </METADATA>.

    Si la valeur contenue entre les balises n'est pas un JSON valide, la
    fonction échoue sur une erreur de type json.decoder.JSONDecodeError.

    S'il n'y a pas de balises, s'il n'y a rien entre les balises ou si la valeur
    contenue entre les balises est un JSON et pas un JSON-LD, la fonction renvoie
    un graphe vide.

    >>> extractMetadata(c, dataset_template)
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

    for n, i in buildNSDict(gTemplate).items():
        g.namespace_manager.bind(n, i)

    return g


def updateDescription(description: str, graph: Graph) -> str:
    """Return new description with metadata section updated from JSON-LD serialization of graph.

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
        

