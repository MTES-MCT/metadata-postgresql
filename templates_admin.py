"""
Fonctions d'administration des modèles et compilations d'ontologies.
"""

from pathlib import Path
from rdflib import Graph
from rdflib.util import guess_format
from rdflib.serializer import Serializer

from rdf_utils import buildNSDict


def importVocabulary(directory: str, gTemplate: Graph, language: str ="fr") -> Graph:
    """Parse RDF SKOS ontologies into a graph.

    - directory est le chemin du répertoire où sont stockés les fichiers contenant
    les ontologies. Ne seront considérés que les fichiers .rdf et .ttl.
    - gTemplate est un modèle de graphe qui explicite les ontologies à utiliser pour
    les métadonnées via des propriétés skos:inScheme.
    - la langue pour laquelle le vocabulaire sera importé. Français par défaut.

    Résultat : un graphe contenant une version allégée des ontologies, avec
    pour chaque terme un objet de type skos:Concept avec ses propriétés
    skos:inScheme et skos:prefLabel (pour la langue choisie uniquement).

    Par exemple :
    <http://publications.europa.eu/resource/authority/data-theme/ENVI> a skos:Concept ;
        skos:inScheme <http://publications.europa.eu/resource/authority/data-theme> ;
        skos:prefLabel "Environnement"@fr .

    Ne sont importés que les objets dont la propriété skos:inScheme est référencée
    dans le modèle gTemplate.

    En supposant que les ontologies à traiter sont dans un sous-répertoire
    "ontologies" et que le modèle de graphe est un fichier dataset_template.ttl :
    >>> with open('dataset_template.ttl', encoding='UTF-8') as src:
        dataset_template = Graph().parse(data=src.read(), format='turtle')
    >>> g = importVocabulary("ontologies", dataset_template)
    >>> print(g.serialize(format="turtle").decode("utf-8"))
    """

    prefixDict = buildNSDict(gTemplate)

    graph = Graph()
    graph.namespace_manager = gTemplate.namespace_manager

    gOntology = Graph()

    for f in Path(directory).iterdir():
        if f.is_file() and f.suffix in (".ttl", ".rdf"):
            with open(f, encoding='UTF-8') as src:
                gOntology.parse(data=src.read(), format=guess_format(f))

    q1 = gTemplate.query(
            """
            SELECT
                ?o
            WHERE
                {{ ?s {} ?o }}
            """.format("skos:inScheme"),
            initNs = prefixDict
            )

    for r1 in q1:

        q2 = gOntology.query(
            """
            SELECT
                ?s ?l
            WHERE
                { ?s a skos:Concept ;
                    skos:inScheme ?o ;
                    skos:prefLabel ?l .
                  FILTER ( lang(?l) = "fr" ) }
            """,
            initNs = prefixDict,
            initBindings = { "o": r1.o }
            )

        for r2 in q2:
            
            graph.update(
                """
                INSERT
                    { ?s a skos:Concept ;
                        skos:inScheme ?o ;
                        skos:prefLabel ?l }
                WHERE
                    { }
                """,
                initNs = prefixDict,
                initBindings = { "o": r1.o, "s": r2.s, "l": r2.l }
                )

    return graph
        
#print(gr.serialize(format="turtle").decode("utf-8"))

#with open('ontologies.ttl', encoding='UTF-8') as src:
#    vocabulary = Graph().parse(data=src.read(), format='turtle')
    
        
