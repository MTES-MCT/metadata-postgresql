"""Gestion du registre de Plume.

Les classes, propriétés, concepts et ensembles de concepts de Plume sont
publiés dans le registre http://registre.data.developpement-durable.gouv.fr/plume.

Ce module définit les classes et méthodes permettant la mise à jour
de ce registre.

Pour qu'il soit utilisable, il est nécessaire de disposer d'un fichier
``/admin/local/credentials.json`` contenant un dictionnaire à trois
clés :

-* ``api`` pour l'URL de base de l'API du registre.
-* ``user`` pour l'identifiant.
-* ``password`` pour le mot de passe.

References
----------
https://github.com/benoitdavidfr/registre

"""

from urllib.parse import urlencode, urljoin
from urllib.request import urlopen, HTTPBasicAuthHandler, \
    build_opener, install_opener, Request
from json import load

from plume.rdf.utils import abspath, pick_translation
from plume.rdf.rdflib import Graph, URIRef
from plume.rdf.thesaurus import vocabulary
from plume.rdf.properties import shape
from plume.rdf.namespaces import PLUME, SKOS, DCT, SH, \
    RDF, RDFS, PlumeNamespaceManager

class ObjectDefinition:
    """Définition d'un objet RDF créé par Plume.
    
    Attributes
    ----------
    objid : str
        Fragment d'URI constituant l'identifiant de l'objet dans
        le registre.
    parent : str
        Identifiant de l'objet parent, le cas échéant.
    objtype : {'R', 'E'}
        Type d'objet. `R` (registre) pour un ensemble de concepts,
        `E` (élément) pour un concept, une propriété ou une classe.
    title : str
        Le libellé principal de l'objet.
    graph : rdflib.graph.Graph
        Graphe contenant la description de l'objet.
    jsonval : str
        Sérialisation JSON-LD de `graph`.
    
    """
    def __init__(self, objid, objtype, title, graph):
        self.objid = objid
        if '/' in objid:
            self.parent = '/plume/{}'.format(objid.rsplit('/', 1)[0])
        else:
            self.parent = '/plume'
        self.objtype = objtype
        self.title = title
        self.graph = graph
        self.jsonval = graph.serialize(format='json-ld')

    def parameters(self):
        """Renvoie la description de l'objet sous forme de paramètres utilisables par une requête HTTP POST.
        
        Returns
        -------
        bytes
        
        """
        data = urlencode({
            'parent': self.parent or '',
            'type': self.objtype or 'E',
            'title': self.title,
            'jsonval': self.jsonval
            })
        return data.encode('ascii')
    
class ConceptDefinition(ObjectDefinition):
    """Graphe décrivant un concept de Plume.
    
    Parameters
    ----------
    iri : rdflib.term.URIRef
        L'IRI du concept, présumé référencé dans 
        :py:data:`plume.rdf.thesaurus.vocabulary`.
    
    Raises
    ------
    ValueError
        Si l'ensemble dont fait partie le concept n'utilise pas
        l'espace de nommage de Plume. Il est alors considéré
        qu'il ne s'agit pas d'un thésaurus créé par Plume.
    
    """
    
    def __init__(self, iri):
        graph = Graph(namespace_manager=PlumeNamespaceManager())
        if str(iri).startswith(str(PLUME)):
            objid = str(iri).replace(str(PLUME), '')
            s = iri
        else:
            scheme = vocabulary.value(iri, SKOS.inScheme)
            if not str(scheme).startswith(str(PLUME)):
                raise ValueError("Le concept '{}' n'appartient pas à un " \
                    'thésaurus créé par Plume.'.format(iri))
            suffix = iri.rsplit('/', 1)[1]
            objid = '{}/{}'.format(str(scheme).replace(str(PLUME), ''), suffix)
            s = PLUME[objid]
            graph.add((s, SKOS.exactMatch, iri))
        labels = [o for o in vocabulary.objects(iri, SKOS.prefLabel)]
        title = str(pick_translation(labels, ('fr', 'en')))
        for p, o in vocabulary.predicate_objects(iri):
            graph.add((s, p, o))
        super().__init__(objid=objid, objtype='E',
            title=title, graph=graph)

class ConceptSchemeDefinition(ObjectDefinition):
    """Classe décrivant un ensemble de concepts de Plume.
    
    Parameters
    ----------
    iri : rdflib.term.URIRef
        L'IRI de l'ensemble de concepts, présumé référencé
        dans :py:data:`plume.rdf.thesaurus.vocabulary`.
    
    Raises
    ------
    ValueError
        Si l'ensemble n'utilise pas l'espace de nommage de
        Plume. Il est alors considéré qu'il ne s'agit pas
        d'un thésaurus créé par Plume.
    
    """
    
    def __init__(self, iri):
        graph = Graph(namespace_manager=PlumeNamespaceManager())
        if str(iri).startswith(str(PLUME)):
            objid = str(iri).replace(str(PLUME), '')
            s = iri
        else:
            raise ValueError("'{}' n'est pas un " \
                'thésaurus créé par Plume.'.format(iri))
        labels = [o for o in vocabulary.objects(iri, SKOS.prefLabel)]
        title = str(pick_translation(labels, ('fr', 'en')))
        predicate_map = {SKOS.prefLabel : DCT.title}
        for p, o in vocabulary.predicate_objects(iri):
            graph.add((s, predicate_map.get(p, p), o))
        for o, p in vocabulary.subject_predicates(iri):
            graph.add((s, SKOS.hasTopConcept, o))
        super().__init__(objid=objid, objtype='R',
            title=title, graph=graph)

class PropertyDefinition(ObjectDefinition):
    """Graphe décrivant une propriété de Plume.
    
    Parameters
    ----------
    iri : rdflib.term.URIRef
        L'IRI de la propriété, présumée référencée
        dans :py:data:`plume.rdf.properties.shape`.
    
    Raises
    ------
    ValueError
        Si la propriété n'utilise pas l'espace de nommage de
        Plume. Il est alors considéré qu'il ne s'agit pas
        d'une propriété créée par Plume.
    
    Notes
    -----
    Dans le schéma des métadonnées communes de Plume, une
    même propriété utilisée par plusieurs classes peut avoir
    des libellés et descriptions légèrement différents pour
    faciliter la compréhension ou donner des conseils de
    saisie. Néanmoins, la question ne se pose pas à date pour
    les propriétés ajoutées par Plume. On conserve ici toutes
    les valeurs trouvées, mais il n'y en aura en fait qu'une.
    
    """
    
    def __init__(self, iri):
        graph = Graph(namespace_manager=PlumeNamespaceManager())
        if str(iri).startswith(str(PLUME)):
            objid = str(iri).replace(str(PLUME), '')
        else:
            raise ValueError("'{}' n'est pas une " \
                'propriété créé par Plume.'.format(iri))
        graph.add((iri, RDF.type, RDF.Property))
        for n in shape.subjects(SH.path, iri):
            labels = [o for o in shape.objects(n, SH.name)]
            title = str(pick_translation(labels, ('fr', 'en')))
            for o in labels:
                graph.add((iri, RDFS.label, o))
            for o in shape.objects(n, SH.description):
                graph.add((iri, RDFS.comment, o))
            o = shape.value(n, SH['class'])
            graph.add((iri, RDFS.range, o or RDFS.Literal))
            for s in shape.subjects(SH.property, n):
                o = shape.value(s, SH.targetClass)
                graph.add((iri, RDFS.domain, o))  
        super().__init__(objid=objid, objtype='E',
            title=title, graph=graph)

class ClassDefinition(ObjectDefinition):
    """Graphe décrivant une classe de Plume.
    
    Parameters
    ----------
    iri : rdflib.term.URIRef
        L'IRI de la classe, présumée référencée
        dans :py:data:`plume.rdf.properties.shape`.
    
    """
    
    def __init__(self, iri):
        super().__init__(objid=objid, objtype='E',
            title=title, graph=graph)

class RegisterApi:
    """Requêteur sur le registre de Plume.
    
    """
    def __init__(self):
        credpath = abspath('').parents[0] / 'admin/local/credentials.json'
        with open(credpath, encoding='utf-8') as src:
            credentials = json.load(src)
        self.api = credentials['api']
        auth_handler = HTTPBasicAuthHandler()
        auth_handler.add_password(
            realm=None,
            uri=self.api,
            user=credentials['user'],
            passwd=credentials['password']
            )
        opener = build_opener(auth_handler)
        install_opener(opener)
    
    def put(self, objid, data):
        """Génère et envoie une requête PUT.
        
        Parameters
        ----------
        objid : str
            L'identifiant de l'objet à ajouter ou mettre à jour
            dans le registre, sans son espace de nommage. À noter
            que l'identifiant d'un concept inclut celui de son
            ensemble (par exemple ``CrpaAccessLimitations/L311-2-dp``).
        data : bytes
            Les paramètres de la requête.
        
        """

