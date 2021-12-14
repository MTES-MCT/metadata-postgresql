"""Description des catégories de métadonnées.

Ce module gère la convergence des informations descriptives des
catégories de métadonnées communes (décrites par un schéma SHACL) et
locales (décrites par un modèle stocké dans des tables PostgreSQL).

"""

from plume.rdf.namespaces import SH, SNUM
from plume.rdf.metagraph import graph_from_file

shape = graph_from_file(abspath('rdf/data/shape.ttl'))
"""Schéma SHACL définissant la structure des métadonnées communes.

"""

class PlumeProperty:
    """Catégorie de métadonnée.
    
    Parameters
    ----------
    property_node : BNode, optional
        Noeud anonyme du schéma SHACL représentant la catégorie.
        Si renseigné à l'initialisation, et seulement dans ce cas,
        l'attribut `shape` est automatiquement calculé.
    property_iri : URIRef, optional
        L'IRI de la catégorie. Obligatoire si `property_node` n'est pas
        fourni, ignoré sinon.
    no_template : bool, default True
    
    Attributes
    ----------
    base : dict
        Paramétrage issu du schéma SHACL ou minimum d'informations
        nécessaires aux traitements.
    template : dict or None
        Paramétrage additionnel issu d'un modèle local, le cas
        échéant.
    unlisted : bool
        S'agit-il d'une catégorie non répertoriée par le modèle ?
        Vaut toujours False s'il n'y a pas de modèle.
    
    """
    def __init__(self, property_node = None, property_iri = None,
        no_template = True):
        if property_node:
            self.base = read_shape_property(property_node)
        else:
            self.base['predicate'] = property_iri
        self.no_template = no_template
    
    @property
    def unlisted(self):
        return not self.no_template and not self.template
    

def class_properties(class_iri):
    """Renvoie la liste des propriétés d'une classe.
    
    Parameters
    ----------
    class_iri : URIRef
        IRI d'une classe présumée décrite dans le schéma SHACL.
    
    Returns
    -------
    list(PlumeProperty)
    
    """
    # IRI de la forme décrivant la classe
    shape_iri = None
    for s in shape.subjects(SH.targetClass, class_iri):
        shape_iri = shape_iri_from_class(class_iri)
        break
    if not shape_iri:
        return []
    
    properties = []
    # propriétés associées
    for property_node in shape.objects(shape_iri, SH['property']):
        properties.append(PlumeProperty(property_node=property_node))
    return properties

def read_shape_property(shape_node):
    """Extrait du schéma SHACL les caractéristiques d'une propriété d'une forme.
    
    Parameters
    ----------
    shape_node : BNode, optional
        Noeud anonyme du schéma SHACL représentant la catégorie.
    
    Returns
    -------
    dict
        Un dictionnaire avec une clé par caractéristique potentiellement
        fournie.
    
    """
    prop_map = {
        SH.path: ('predicate', False),
        SH.name: ('label', False),
        SH.description: ('description', False),
        SH.nodeKind: ('kind', False),
        SH.order: ('shape_order', False),
        SH['class']: ('rdfclass', False),
        SH.placeholder: ('placeholder', False),
        SNUM.inputMask: ('input_mask', False),
        SNUM.rowSpan: ('rowspan', False),
        SH.minCount: ('min', False),
        SH.maxCount: ('max', False),
        SH.datatype: ('datatype', False),
        SH.uniqueLang: ('unilang', False),
        SH.pattern: ('regex_validator', False),
        SH.flags: ('regex_validator_flags', False),
        SNUM.transform: ('transform', False),
        SNUM.ontology: ('sources', True)
        SNUM.longText: ('is_long_text', False)
        }
        # le booléen indique si la propriété
        # peut prendre des valeurs multiples
    p = {v[0]: None for v in prop_map.values()}
    
    for a, b in shape.predicate_objects(shape_node):
        if a.n3(nsm) in prop_map:
            if prop_map[a][1]:
                p[prop_map[a][0]] = (p[prop_map[a][0]] or []) + [b]
            else:
                p[prop_map[a][0]] = b
    
    p['is_mandatory'] = p['min'] and int(p['min']) > 0
    p['is_multiple'] = p['max'] is None or int(p['max']) > 1
    
    return p

