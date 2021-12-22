"""Import des classes et fonctions de la bibliothèque tierce RDFLib.

À l'usage des modules de Plume, qui devront ainsi appeler
le présent module au lieu d'un appel direct à RDFLib.

On s'assurera ainsi d'écrire:

    >>> from plume.rdf.rdflib import URIRef

Et jamais:

    >>> from rdflib.term import URIRef

Plume requiert RDFLib 6.0.

Le présent module s'assure d'appeler l'installeur interne de
Plume si la bibliothèque n'est pas disponible.

References
----------
https://rdflib.readthedocs.io/en/stable/index.html

"""

try:
    from rdflib.graph import Graph
except:
    from plume.bibli_install.bibli_install import manageLibrary
    # installe RDFLib si n'est pas déjà disponible
    manageLibrary("RDFLIB")
    from rdflib.graph import Graph

from rdflib.term import BNode, Literal, URIRef
from rdflib.util import from_n3
from rdflib.namespace import Namespace, NamespaceManager
from rdflib.compare import isomorphic