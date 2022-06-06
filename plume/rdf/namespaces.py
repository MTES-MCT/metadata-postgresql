"""Gestion des espaces de nommage.

"""

from plume.rdf.rdflib import Graph, Namespace, NamespaceManager

ADMS = Namespace('http://www.w3.org/ns/adms#')
CNT = Namespace('http://www.w3.org/2011/content#')
DCAT = Namespace('http://www.w3.org/ns/dcat#')
DCATAP = Namespace('http://data.europa.eu/r5r/')
DCT = Namespace('http://purl.org/dc/terms/')
DCTYPE = Namespace('http://purl.org/dc/dcmitype/')
DQV = Namespace('http://www.w3.org/ns/dqv#')
FOAF = Namespace('http://xmlns.com/foaf/0.1/')
GEODCAT = Namespace('http://data.europa.eu/930/')
GSP = Namespace('http://www.opengis.net/ont/geosparql#')
LOCN = Namespace('http://www.w3.org/ns/locn#')
ORG = Namespace('http://www.w3.org/ns/org#')
OWL = Namespace('http://www.w3.org/2002/07/owl#')
PROV = Namespace('http://www.w3.org/ns/prov#')
RDF = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
RDFS = Namespace('http://www.w3.org/2000/01/rdf-schema#')
SDO = Namespace('http://schema.org/')
SH = Namespace('http://www.w3.org/ns/shacl#')
SKOS = Namespace('http://www.w3.org/2004/02/skos/core#')
VCARD = Namespace('http://www.w3.org/2006/vcard/ns#')
XSD = Namespace('http://www.w3.org/2001/XMLSchema#')
PLUME = Namespace('http://registre.data.developpement-durable.gouv.fr/plume/')
LOCAL = Namespace('urn:uuid:')

NAMESPACES = {
    'adms': ADMS,
    'cnt': CNT,
    'dcat': DCAT,
    'dcatap': DCATAP,
    'dct': DCT,
    'dctype': DCTYPE,
    'dqv': DQV,
    'foaf': FOAF,
    'geodcat': GEODCAT,
    'gsp': GSP,
    'locn': LOCN,
    'org': ORG,
    'owl': OWL,
    'prov': PROV,
    'rdf': RDF,
    'rdfs': RDFS,
    'sdo': SDO,
    'sh': SH,
    'skos': SKOS,
    'vcard': VCARD,
    'xsd': XSD,
    'plume': PLUME,
    'uuid': LOCAL
    }

PREDICATE_MAP = {
    VCARD['organisation-name']: VCARD['organization-name'],
    SDO.endDate: DCAT.endDate,
    SDO.startDate: DCAT.startDate,
    DCT.subject: DCAT.theme,
    DCAT.mediaType: DCT['format']
    }
"""Mapping de prédicats.

Coquilles, formes obsolètes, mapping de propriétés non prises
en charge par Plume... Ce dictionnaire sert notamment au nettoyage
des graphes importés de sources externes par la fonction 
:py:func:`plume.rdf.metagraph.clean_metagraph`.

"""

CLASS_MAP = {
    ORG.Organization: FOAF.Agent,
    FOAF.Organization: FOAF.Agent,
    ORG.OrganizationalUnit: FOAF.Agent,
    ORG.FormalOrganization: FOAF.Agent,
    VCARD.Individual: VCARD.Kind,
    VCARD.Organization: VCARD.Kind,
    VCARD.Location: VCARD.Kind,
    VCARD.Group: VCARD.Kind
    }
"""Mapping de classes.

Principalement des sous-classes susceptibles d'apparaître dans
des graphes importés de sources externes, qui sont mappées
vers la classe parente utilisée par Plume. Ce dictionnaire sert
notamment à la fonction :py:func:`plume.rdf.metagraph.clean_metagraph`.

"""

class PlumeNamespaceManager(NamespaceManager):
    """Gestionnaire d'espaces de nommage.
    
    Le gestionnaire est initialisé avec les préfixes nécessaires
    à l'exécution de Plume. Il peut ensuite être complété si
    besoin.
    
    """
    def __init__(self):
        super().__init__(Graph())
        for prefix, namespace in NAMESPACES.items():
            self.bind(prefix, namespace, override=True, replace=True)

