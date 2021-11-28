"""Graphes RDF.

"""

from uuid import UUID, uuid4

try:
    from rdflib import Graph, URIRef
except:
    from plume.bibli_install.bibli_install import manageLibrary
    # installe RDFLib si n'est pas déjà disponible
    manageLibrary()
    from rdflib import Graph, URIRef
    

class Metagraph(Graph):
    """Graphes de métadonnées.
    
    Un graphe de métadonnées décrit un et un seul jeu de données
    (dcat:Dataset).
    
    Attributs
    ---------
    datasetid : URIRef
        L'identifiant du jeu de données, sous forme d'URIRef.
    uuid : UUID
        L'identifiant du jeu de données, sous forme d'UUID.
    is_empty : bool
        True si le graphe est vide. Renseigner cet attribut permet
        d'éviter d'interroger inutilement le graphe.
    
    """
    def __init__(self, datasetid=None, uuid=None, is_empty=False):
        """Crée un graphe de métadonnées vierge.
        
        Parameters
        ----------
        datasetid : URIRef, optional
            L'identifiant du jeu de données, sous forme d'URIRef.
        uuid : UUID, optional
            L'identifiant du jeu de données, sous forme d'UUID.
        is_empty : bool, default False
            À mettre à True s'il est assuré que le graphe restera
            vide.
        
        Notes
        -----
        `uuid` est déduit de `datasetid` et réciproquement.
        Si `datasetid` et `uuid` sont tous deux renseignés (ce
        qui ne présente aucun intérêt), ce dernier prime.
        Si ni `datasetid` ni `uuid` n'est fourni ou si la
        valeur fournie n'était pas un UUID valide, un nouvel
        identifiant sera généré.
        
        """
        super().__init__(self)
        self.is_empty = is_empty
        
        if uuid:
            self.uuid = uuid
            self.datasetid = datasetid_from_uuid(uuid)
        elif datasetid:
            self.datasetid = datasetid
            self.uuid = uuid_from_datasetid(datasetid)
        
        if not self.datasetid or not self.uuid:
            self.uuid = uuid4()
            self.datasetid = datasetid_from_uuid(self.uuid)


def uuid_from_datasetid(datasetid):
    """Extrait l'UUID d'un identifiant de jeu de données.
    
    Parameters
    ----------
    datasetid : URIRef
        Un identifiant de jeu de données.
    
    Returns
    -------
    UUID
        L'UUID contenu dans l'identifiant. None si l'identifiant
        ne contenait pas d'UUID.
    
    """
    try:
        u = UUID(str(datasetid))
        return u
    except:
        r = re.search('[:]([a-z0-9-]{36})$', str(datasetid))
        if r:
            try:
                u = UUID(r[1])
                return u
            except:
                return


def datasetid_from_uuid(uuid):
    """Crée un identifiant de jeu de données à partir d'un UUID.
    
    Parameters
    ----------
    uuid : UUID
        Un UUID.
    
    Returns
    -------
    URIRef
        Un identifiant de jeu de données.
    
    """
    return URIRef(uuid.urn)


class ShapeGraph(Graph):
    """Schémas SHACL.
    
    """
    def shape_iri_from_class(self, class_iri):
        """Renvoie l'IRI de la forme décrivant la classe considérée.
        
        Parameters
        ----------
        class_iri : URIRef
            IRI d'une classe présumée décrite dans le schéma.
        
        Returns
        -------
        URIRef
            L'IRI de la forme. None si la classe n'est pas décrite  par
            le schéma.
        
        """
        for s in shape.subjects(
            URIRef("http://www.w3.org/ns/shacl#targetClass"),
            class_iri
            ):
            return s
    
    def read_property(self, shape_iri, property_iri):
        """Extrait du schéma SHACL les caractéristiques d'une propriété d'une forme.
        
        Parameters
        ----------
        shape_iri : URIRef
            IRI de la forme.
        property_iri : URIRef
            IRI de la propriété.
        
        Returns
        -------
        dict
            Un dictionnaire avec une clé par caractéristique potentiellement
            fournie.
        
        """
        prop_map = {
            "sh:path": ("property", False),
            "sh:name": ("name", False),
            "sh:description": ("descr", False),
            "sh:nodeKind": ("kind", False),
            "sh:order": ("order", False),
            "snum:widget" : ("widget", False),
            "sh:class": ("class", False),
            "snum:placeholder": ("placeholder", False),
            "snum:inputMask": ("mask", False),
            "sh:defaultValue": ("default", False),
            "snum:rowSpan": ("rowspan", False),
            "sh:minCount": ("min", False),
            "sh:maxCount": ("max", False),
            "sh:datatype": ("type", False),
            "sh:uniqueLang": ("unilang", False),
            "sh:pattern": ("pattern", False),
            "sh:flags": ("flags", False),
            "snum:transform": ("transform", False),
            "snum:ontology": ("ontologies", True)
            } 
        p = { v[0]: None for v in prop_map.values() }
        
        for a, b in shape.predicate_objects(property_iri):
            if a.n3(nsm) in prop_map:
                if prop_map[a.n3(nsm)][1]:
                    p[prop_map[a.n3(nsm)][0]] = (p[prop_map[a.n3(nsm)][0]] or []) + [b]
                else:
                    p[prop_map[a.n3(nsm)][0]] = b
                    
        return p


def get_datasetid(anygraph):
    """Renvoie l'identifiant du jeu de données éventuellement contenu dans le graphe.
    
    Parameters
    ----------
    anygraph : Graph
        Un graphe quelconque, présumé contenir la description d'un
        jeu de données (dcat:Dataset).
    
    Returns
    -------
    URIRef
        L'identifiant du jeu de données. None si le graphe ne contenait
        pas de jeu de données.
    
    """
    for s in anygraph.subjects(
        URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
        URIRef("http://www.w3.org/ns/dcat#Dataset")
        ):
        return s

