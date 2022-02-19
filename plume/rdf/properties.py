"""Description des catégories de métadonnées.

Ce module gère la convergence des informations descriptives des
catégories de métadonnées communes (décrites par un schéma SHACL) et
locales (décrites par un modèle stocké dans des tables PostgreSQL).

La classe :py:class:`PlumeProperty` et la plupart des fonctions
du module n'ont pas vraiment vocation à être utilisées
directement. La plus utile - et celle qui sert au module
:py:mod:`plume.rdf.widgetsdict` - est :py:func:`class_properties`.

"""

from plume.rdf.rdflib import URIRef
from plume.rdf.namespaces import SH, SNUM
from plume.rdf.metagraph import shape
from plume.rdf.utils import path_n3, path_from_n3


class PlumeProperty:
    """Catégorie de métadonnée.
    
    Parameters
    ----------
    origin : {'shared', 'local', 'unknown'}
        L'origine de la catégorie :
        
        * ``'shared'`` pour une catégorie commune issue du schéma SHACL.
          L'argument `property_node` est alors obligatoire. `template`
          et `base_path` doivent être fournis s'il y a lieu.
        * ``'local'`` pour une catégorie locale définie par le modèle.
          Les arguments `template` et `n3_path` sont alors obligatoires.
        * ``'unknown'`` pour une catégorie issue du graphe de métadonnées,
          qui n'est répertoriée ni par le schéma SHACL ni par le modèle.
          L'argument `predicate` est alors obligatoire.
    nsm : PlumeNamespaceManager
        Le gestionnaire d'espaces de nommage du dictionnaire de widgets.
    property_node : BNode, optional
        Noeud anonyme du schéma SHACL représentant la catégorie,
        s'il s'agit d'une catégorie commune.
    base_path : rdflib.paths.SequencePath, optional
        Le chemin de la clé parente. À fournir pour les catégories
        communes.
    template : dict, optional
        Modèle local de formulaire, le cas échéant.
    n3_path : str, optional
        La représentation N3 du chemin de la catégorie, s'il s'agit
        d'une catégorie locale. `n3_path` doit impérativement être
        répertorié dans le modèle s'il est fourni.
    predicate : URIRef, optional
        L'IRI de la catégorie. À fournir pour les propriétés qui ne
        sont répertoriées ni dans le schéma SHACL ni dans le modèle
        local.
    
    Attributes
    ----------
    path : rdflib.paths.SequencePath
        Chemin de la catégorie.
    n3_path : str
        La représentation N3 du chemin de la catégorie.
    predicate : URIRef
        L'IRI de la catégorie.
    prop_dict : dict
        Paramétrage de la catégorie (à passer à la fonction
        d'initialisation des futures clés).
    unlisted : bool
        S'agit-il d'une catégorie non répertoriée par le modèle ?
        Vaut toujours ``False`` s'il n'y a pas de modèle.
    origin : {'shared', 'local', 'unknown'}
        L'origine de la catégorie.
    
    Raises
    ------
    RuntimeError
        Quand tous les arguments requis pour la valeur d'`origin`
        n'ont pas été fournis.
    
    """
    def __init__(self, origin, nsm, base_path=None, property_node=None,
        template=None, n3_path=None, predicate=None):
        self.origin = origin
        
        if origin == 'shared' and property_node:
            self.origin = 'shared'
            self.prop_dict = read_shape_property(property_node)
            self.predicate = self.prop_dict['predicate']
            self.path = (base_path / self.predicate) if base_path \
                else self.predicate
            self.n3_path = path_n3(self.path, nsm)
            if not template:
                self.unlisted = False
            elif self.n3_path in template.shared:
                merge_property_dict(self.prop_dict, template.shared[self.n3_path])
                self.unlisted = False
            else:
                self.unlisted = True
        
        elif origin == 'local' and n3_path and template:
            self.origin = 'local'
            self.unlisted = False
            self.prop_dict = template.local[n3_path].copy()
            self.predicate = path_from_n3(n3_path, nsm=nsm)
            self.path = self.predicate
            self.prop_dict.update({'predicate': self.predicate})
            self.n3_path = n3_path
        
        elif origin == 'unknown' and predicate:
            self.origin = 'unknown'
            self.unlisted = True
            self.predicate = predicate
            self.path = predicate
            self.n3_path = predicate.n3(nsm)
            self.prop_dict = {'predicate': self.predicate}
        
        else:
            raise RuntimeError("Pas assez d'arguments pour définir une propriété.")    

def merge_property_dict(shape_dict, template_dict):
    """Fusionne deux dictionnaires décrivant une même catégorie de métadonnées.
    
    Parameters
    ----------
    shape_dict : dict
        Dictionnaire portant les informations relatives à la
        propriété issues du schéma SHACL descriptif des métadonnées
        communes.
    template_dict : dict
        Dictionnaire portant le paramétrage local.
    
    Notes
    -----
    La fonction ne renvoie rien, elle complète `shape_dict`.
    
    Les clés ``predicate``, ``kind``, ``datatype``, ``is_multiple``
    et ``unilang`` ne peuvent pas être redéfinies par le modèle,
    leurs valeurs éventuelles seront ignorées.
    
    La clé ``order_idx`` produite par :py:func:`read_shape_property`
    à partir de l'indice fourni par le schéma SHACL est un tuple
    dont la première valeur est ``9999``, et la seconde l'indice.
    :py:class:`plume.pg.template.TemplateDict` fait exactement
    l'inverse : ses clés ``order_idx`` ont l'indice du modèle en
    première (et unique) valeur. `merge_property_dict` recréé des
    clés ``order_idx`` dont la première valeur est l'indice du
    modèle, et la seconde celle du schéma des catégories communes.
    
    La clé ``sources`` peut être restreinte par le modèle : si ce
    dernier fournit une liste d'URL, alors seules les sources qui
    se trouvent dans cette liste seront conservées, sous réserve
    qu'il y en ait au moins une (sinon la clé d'origine est préservée).
    
    Le modèle peut rendre obligatoire une catégorie qui n'est
    pas définie comme telle par le schéma des catégories communes,
    mais pas l'inverse. La valeur de la clé ``is_mandatory`` n'est
    donc écrasée que dans le cas où elle vaut ``False`` dans le
    schéma et ``True`` dans le modèle.
    
    """
    restricted = ['predicate', 'kind', 'datatype', 'is_multiple',
        'unilang', 'transform', 'sources', 'order_idx', 'is_mandatory',
        'rdfclass']
        # propriétés que le modèle n'a pas le droit d'écraser, ou
        # du moins pas brutalement
    for key, value in template_dict.items():
        if not key in restricted and not value is None:
            shape_dict[key] = value
            # NB: on remplace des Literal et URIRef par des str, bool, etc.,
            # mais ça n'a pas d'importance, WidgetKey peut gérer les deux
            # formes
    if 'order_idx' in template_dict:
        shape_dict['order_idx'] = (template_dict['order_idx'][0], shape_dict['order_idx'][1])
    if shape_dict.get('sources') and template_dict.get('sources'):
        sources = shape_dict['sources'].copy()
        for s in sources:
            if not s in template_dict['sources']:
                sources.remove(s)
        if sources:
            shape_dict['sources'] = sources
    if template_dict.get('is_mandatory') and not shape_dict.get('is_mandatory'):
        shape_dict['is_mandatory'] = True

def class_properties(rdfclass, nsm, base_path, template=None):
    """Renvoie la liste des propriétés communes d'une classe.
    
    Parameters
    ----------
    rdfclass : URIRef
        IRI d'une classe présumée décrite dans le schéma SHACL.
    nsm : PlumeNamespaceManager
        Le gestionnaire d'espaces de nommage du dictionnaire de widgets.
    base_path : rdflib.paths.SequencePath
        Chemin de la clé parente. Peut être ``None`` pour les catégories
        de premier niveau.
    template : dict, optional
        Modèle local de formulaire, le cas échéant.
    
    Returns
    -------
    tuple(list(PlumeProperty), list(URIRef))
        Un tuple avec :
        
        * ``[0]`` La liste des propriétés.
        * ``[1]`` La liste des IRI des propriétés (prédicats des
          triplets du graphe de métadonnées).
    
    """
    # IRI de la forme décrivant la classe
    shape_iri = None
    for s in shape.subjects(SH.targetClass, rdfclass):
        shape_iri = s
        break
    if not shape_iri:
        return []
    
    properties = []
    predicates = []
    # propriétés associées
    for property_node in shape.objects(shape_iri, SH['property']):
        p = PlumeProperty(origin='shared', nsm=nsm,
            property_node=property_node, base_path=base_path,
            template=template)
        properties.append(p)
        predicates.append(p.predicate)
    return properties, predicates

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
        SNUM.placeholder: ('placeholder', False),
        SNUM.inputMask: ('input_mask', False),
        SNUM.rowSpan: ('rowspan', False),
        SH.minCount: ('min', False),
        SH.maxCount: ('max', False),
        SH.datatype: ('datatype', False),
        SH.uniqueLang: ('unilang', False),
        SH.pattern: ('regex_validator', False),
        SH.flags: ('regex_validator_flags', False),
        SNUM.transform: ('transform', False),
        SNUM.ontology: ('sources', True),
        SNUM.longText: ('is_long_text', False),
        SNUM.geoTool: ('geo_tools', True),
        SNUM.compute: ('compute', True)
        }
        # le booléen indique si la propriété
        # peut prendre des valeurs multiples
    p = {}
    for a, b in shape.predicate_objects(shape_node):
        if a in prop_map:
            if prop_map[a][1]:
                p[prop_map[a][0]] = p.get(prop_map[a][0], []) + [b]
            else:
                p[prop_map[a][0]] = b
    p['is_mandatory'] = int(p.get('min', 0)) > 0
    p['is_multiple'] = int(p.get('max', 99)) > 1
    p['order_idx'] = (9999, int(p.get('shape_order', 9999)))
    return p

