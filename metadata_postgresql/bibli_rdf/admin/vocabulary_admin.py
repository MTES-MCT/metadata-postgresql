"""
Utilitaires pour la gestion des thésaurus.

En supposant que la source se trouve dans un sous-répertoire "ontologies".

0. Ensemble de concepts que l'on souhaite ajouter au vocabulaire :
>>> s = 'http://publications.europa.eu/resource/authority/data-theme'

1. Dé-sérialisation du contenu de la source :
>>> v = import_vocabulary('ontologies', s)

2. Contrôle et ajout des traductions manquantes :
>>> add_translation(v)

3. Contrôle et correction du nom du thésaurus (il faut valider sans saisir
de nouvelle valeur pour ne pas modifier le libellé) :
>>> replace_scheme_label(v, s)

4. Vérification du visuelle du résultat :
>>> print(v.serialize(format="turtle").decode("utf-8"))

5. Ajout à vocabulary.ttl :
>>> export_vocabulary(v)
"""

from pathlib import Path
from rdflib import Graph, URIRef, Literal
from rdflib.util import guess_format
from rdflib.serializer import Serializer

from metadata_postgresql.bibli_rdf import __path__


def import_vocabulary(directory, scheme, languages=["fr","en"]):
    """Parse RDF SKOS ontologies into a graph.

    ARGUMENTS
    ---------
    - directory (str) : chemin du répertoire où sont stockés les fichiers contenant
    les ontologies. Ne seront considérés que les fichiers .rdf et .ttl.
    - scheme (str ou rdflib.term.URIRef) : IRI de l'ensemble dont on souhaite
    récupérer les concepts (chaînes de caractères ou URIRef).
    - [optionnel] languages (list) : liste des langues (str) pour lesquelles le
    vocabulaire sera importé. Français et anglais par défaut.

    RESULTAT
    --------
    Un graphe contenant une version allégée des ontologies, avec
    le label de l'ensemble et les labels des concepts traduits dans les langues
    choisies.

    EXEMPLES
    --------
    En supposant que la source se trouve dans un sous-répertoire "ontologies" :
    >>> v = import_vocabulary('ontologies', 'http://publications.europa.eu/resource/authority/data-theme')
    """

    if not isinstance(languages, list):
        raise TypeError("languages should be a list.")
    
    graph = Graph()
    graph.namespace_manager.bind('skos', URIRef('http://www.w3.org/2004/02/skos/core#'), override=True, replace=True)
    
    dskos = { 'skos' : URIRef('http://www.w3.org/2004/02/skos/core#') }

    gOntology = Graph()

    for f in Path(directory).iterdir():
        if f.is_file() and f.suffix in (".ttl", ".rdf"):
            with open(f, encoding='UTF-8') as src:
                gOntology.parse(data=src.read(), format=guess_format(f))
    
    for l in languages:
    
        q_s = gOntology.query(
            """
            SELECT
                ?scheme
            WHERE
                {{ ?s a skos:ConceptScheme ;
                   skos:prefLabel ?scheme .
                   FILTER ( lang(?scheme) = "{}" ) }}
            """.format(l),
            initNs = dskos,
            initBindings = { 's': URIRef(scheme) }
            )
            
        for r_s in q_s:
        
            graph.update(
                """
                INSERT
                    { ?s a skos:ConceptScheme ;
                        skos:prefLabel ?scheme }
                WHERE
                    { }
                """,
                initNs = dskos,
                initBindings = { 's': URIRef(scheme), 'scheme': r_s['scheme'] }
                )

        q_c = gOntology.query(
            """
            SELECT
                ?c ?concept
            WHERE
                {{ ?c a skos:Concept ;
                   skos:inScheme ?s ;
                   skos:prefLabel ?concept .
                   FILTER ( lang(?concept) = "{}" ) }}
            """.format(l),
            initNs = dskos,
            initBindings = { 's': URIRef(scheme) }
            )   

        for r_c in q_c:
            
            graph.update(
                """
                INSERT
                    { ?c a skos:Concept ;
                        skos:inScheme ?s ;
                        skos:prefLabel ?concept }
                WHERE
                    { }
                """,
                initNs = dskos,
                initBindings = { 's': URIRef(scheme), 'c': r_c['c'], 'concept': r_c['concept'] }
                )

    return graph



def add_translation(graph, languages=["fr", "en"]):
    """Basic interface to add missing translations of concepts and schemes labels in given graph.
    
    ARGUMENTS
    ---------
    - graph (rdflib.graph.Graph) : graphe contenant les labels associés à un
    ensemble de concepts.
    - [optionnel] languages (list) : liste des langues (str) pour lesquelles on
    souhaite contrôler et compléter les traductions manquantes. Français et
    anglais par défaut.
    
    EXEMPLES
    --------
    >>> add_translation(v)
    """
    
    for l in languages:
    
        q = graph.query(
            """
            SELECT
                ?s ?o
            WHERE
                {{ ?s skos:prefLabel ?o .
                   FILTER ( NOT EXISTS {{ ?s skos:prefLabel ?t .
                                          FILTER ( lang(?t) = "{}" ) }} ) }}
            """.format(l)
            )
            
        for r in q:
        
            print('')
            print( 'Missing translation for "{}".'.format( str(r.s) ) )
            print( '{} : {}'.format( r.o.language.upper(), str(r.o) ) )
            t = input( '{} : '.format(l.upper()) )
            
            graph.update(
                """
                INSERT
                    { ?s skos:prefLabel ?t }
                WHERE
                    { }
                """,
                initBindings = { 's': r.s, 't': Literal(t, lang=l) }
                )


def replace_scheme_label(graph, scheme=None):
    """Basic interface to replace schemes labels in given graph.
    
    ARGUMENTS
    ---------
    - graph (rdflib.graph.Graph) : graphe contenant les labels associés à un
    ensemble de concepts.
    - [optionnel] scheme (str ou rdflib.term.URIRef) : IRI de l'ensemble de
    concepts dont le label serait à remplacer. S'il n'est pas renseigné,
    la fonction balaie tous les ensembles du graphe, mais ne sera alors pas
    en mesure de repérer les ensembles sans libellé.
    
    Il sera systématiquement proposé de remplacer chaque traduction du
    label.
    
    Pour ne pas remplacer un label, il suffit de valider sans saisir de
    nouvelle valeur.
    
    EXEMPLES
    --------
    >>> replace_scheme_label(v, s)
    """  
    if scheme:
    
        q = graph.query(
            """
            SELECT
                ?s ?o
            WHERE
                { ?s skos:prefLabel ?o ;
                   a skos:ConceptScheme . }
            """,
            initBindings = { 's': URIRef(scheme) }
            )
            
        if len(q) == 0:
        
            print('')
            print( 'Scheme : "{}".'.format( URIRef(scheme) ) )
            print( 'No label !' )
            n = input( 'New FR label : ' )
            print('Please add other translations with add_translation.')
            
            if n != '':
                graph.update(
                    """
                    INSERT
                        { ?s skos:prefLabel ?n  ;
                          a skos:ConceptScheme . }
                    WHERE
                        { }
                    """,
                    initBindings = { 's': URIRef(scheme), 'n': Literal(n, lang = 'fr') }
                    )
                    
    else:
        q = graph.query(
            """
            SELECT
                ?s ?o
            WHERE
                { ?s skos:prefLabel ?o ;
                   a skos:ConceptScheme . }
            """
            )
        
    for r in q:
    
        print('')
        print( 'Scheme : "{}".'.format( str(r.s) ) )
        print( 'Current {} label : {}'.format( r.o.language.upper(), str(r.o) ) )
        n = input( 'New {} label : '.format( r.o.language.upper() ) )
        
        if n != '':
            graph.update(
                """
                DELETE
                    { ?s skos:prefLabel ?o }
                INSERT
                    { ?s skos:prefLabel ?n }
                WHERE
                    { }
                """,
                initBindings = { 's': r.s, 'o' : r.o, 'n': Literal(n, lang = r.o.language) }
                )
           

def export_vocabulary(graph, mode = 'a'):
    """Append content of given graph to vocabulary.ttl.
    
    ARGUMENTS
    ---------
    - graph (rdflib.graph.Graph) : graphe contenant les labels associés
    à un ensemble de concepts.
    - [optionnel] mode (str) : indique si les nouvelles valeurs doivent
    être ajoutées à la suite du contenu actuel du fichier ("a", valeur par
    défaut), ou si celui-ci doit être intégralement remplacé ("w").

    EXEMPLES
    --------
    >>> export_vocabulary(v)
    """
    s = v.serialize(format="turtle").decode('utf-8')
    
    with open(__path__[0] + r'\modeles\vocabulary.ttl', encoding='UTF-8', mode=mode) as dest:
        dest.write(s)
        
