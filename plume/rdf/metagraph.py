"""Graphes RDF.

"""

try:
    from rdflib import Graph, URIRef
except:
    from plume.bibli_install.bibli_install import manageLibrary
    # installe RDFLib si n'est pas déjà disponible
    manageLibrary()
    from rdflib import Graph, URIRef
    

class Metagraph(Graph):
    """Graphes de métadonnées.
    
    """
    
class Shapegraph(Graph):
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
            L'IRI de la forme. None si la classe n'est pas décrite par
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


