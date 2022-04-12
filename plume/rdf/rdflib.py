"""Import des classes et fonctions de la bibliothèque tierce RDFLib.

À l'usage des modules de Plume, qui devront ainsi appeler
le présent module au lieu d'un appel direct à RDFLib.

On s'assurera ainsi d'écrire :

    >>> from plume.rdf.rdflib import URIRef

Et jamais :

    >>> from rdflib.term import URIRef

References
----------
https://rdflib.readthedocs.io/en/stable/index.html

"""

from rdflib.graph import Graph
from rdflib.term import BNode, Literal, URIRef
from rdflib.util import from_n3
from rdflib.namespace import Namespace, NamespaceManager
from rdflib.compare import isomorphic