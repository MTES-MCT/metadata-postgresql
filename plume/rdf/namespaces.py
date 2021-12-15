"""Gestion des espaces de nommage.

"""

from rdflib import Graph
from rdflib.namespace import Namespace, NamespaceManager

ADMS = Namespace('http://www.w3.org/ns/adms#')
DCAT = Namespace('http://www.w3.org/ns/dcat#')
DCT = Namespace('http://purl.org/dc/terms/')
DCTYPE = Namespace('http://purl.org/dc/dcmitype/')
DQV = Namespace('http://www.w3.org/ns/dqv#')
FOAF = Namespace('http://xmlns.com/foaf/0.1/')
GEODCAT = Namespace('http://data.europa.eu/930/')
GSP = Namespace('http://www.opengis.net/ont/geosparql#')
LOCN = Namespace('http://www.w3.org/ns/locn#')
OWL = Namespace('http://www.w3.org/2002/07/owl#')
PROV = Namespace('http://www.w3.org/ns/prov#')
RDF = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
RDFS = Namespace('http://www.w3.org/2000/01/rdf-schema#')
SDO = Namespace('http://schema.org/')
SH = Namespace('http://www.w3.org/ns/shacl#')
SKOS = Namespace('http://www.w3.org/2004/02/skos/core#')
VCARD = Namespace('http://www.w3.org/2006/vcard/ns#')
XSD = Namespace('http://www.w3.org/2001/XMLSchema#')
SNUM = Namespace('http://snum.scenari-community.org/Metadata/Vocabulaire/#')
UUID = Namespace('urn:uuid:')

namespaces = {
    'adms': ADMS,
    'dcat': DCAT,
    'dct': DCT,
    'dctype': DCTYPE,
    'dqv': DQV,
    'foaf': FOAF,
    'geodcat': GEODCAT,
    'gsp': GSP,
    'locn': LOCN,
    'owl': OWL,
    'prov': PROV,
    'rdf': RDF,
    'rdfs': RDFS,
    'sdo': SDO,
    'sh': SH,
    'skos': SKOS,
    'vcard': VCARD,
    'xsd': XSD,
    'snum': SNUM,
    'uuid': UUID
    }

class PlumeNamespaceManager(NamespaceManager):
    """Gestionnaire d'espaces de nommage.
    
    Le gestionnaire est initialisé avec les préfixes nécessaires
    à l'exécution de Plume. Il peut ensuite être complété si
    besoin.
    
    """
    def __init__(self):
        super().__init__(Graph())
        for prefix, namespace in namespaces.items():
            self.bind(prefix, namespace, override=True, replace=True)

