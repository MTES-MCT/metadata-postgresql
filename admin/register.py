"""Gestion du registre de Plume.

Les classes, propriétés, concepts et ensembles de concepts de Plume sont
publiés dans le registre http://registre.data.developpement-durable.gouv.fr/plume.

Ce module définit les classes et méthodes permettant la mise à jour
de ce registre.

Pour qu'il soit utilisable, il est nécessaire de disposer d'un fichier
``/admin/local/credentials.json`` contenant un dictionnaire à trois
clés :

* ``api`` pour l'URL de base de l'API du registre.
* ``user`` pour l'identifiant.
* ``password`` pour le mot de passe.

Routine Listings
----------------

Initialisation du requêteur :

    >>> api = RegisterApi()

Interrogation simple d'un élément du registre :

    >>> api.get('id')

où ``'id'`` est l'identifiant de l'objet dans le registre, avec ou sans slash
initial. Par exemple ``'plume/isExternal'`` pour la propriété ``plume:isExternal``.

Consultation du contenu du registre pour un élément :

    >>> api.post('id')

Mise à jour d'un élément dans le registre :

    >>> api.put('id')

Suppression d'un élément du registre :

    >>> api.delete('id')

Mise à jour massive du registre (avec ajout des éléments manquants, mais pas
suppression des éléments obsolètes):

    >>> api.udapte()

References
----------
https://github.com/benoitdavidfr/registre

"""

from urllib.parse import urljoin
from urllib.request import urlopen, HTTPBasicAuthHandler, \
    build_opener, install_opener, Request, HTTPPasswordMgrWithDefaultRealm
from urllib.error import HTTPError
from json import load, loads, dumps

from plume.rdf.utils import abspath, pick_translation
from plume.rdf.rdflib import Graph, URIRef
from plume.rdf.thesaurus import vocabulary
from plume.rdf.properties import shape
from plume.rdf.namespaces import PLUME, SKOS, DCT, SH, \
    RDF, RDFS, PlumeNamespaceManager


class RegisterApi:
    """Requêteur sur le registre de Plume.
    
    Attributes
    ----------
    api : str
        URL de base de l'API du registre.
    request : urllib.Request
        Dernière requête envoyée à l'API.
    raw : bytes
        Résultat brut de la dernière requête envoyée à l'API.
    response : dict or list
        Désérialisation python du JSON résultant de la dernière
        requête renvoyée à l'API.
    errcode : int
        Si la dernière requête a produit une erreur, code
        de l'erreur, sinon ``None``.
    reason : str
        Si la dernière requête a produit une erreur,
        la description textuelle de l'erreur, sinon ``None``.
    
    """
    def __init__(self):
        self.collection = DefinitionsCollection()
        credpath = abspath('').parents[0] / 'admin/local/credentials.json'
        with open(credpath, encoding='utf-8') as src:
            credentials = load(src)
        self.api = credentials['api']
        password_mgr = HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(
            realm=None,
            uri=self.api,
            user=credentials['user'],
            passwd=credentials['password']
            )
        auth_handler = HTTPBasicAuthHandler(password_mgr)
        opener = build_opener(auth_handler)
        install_opener(opener)
        self.request = None
        self.raw = None
        self.errcode = None
        self.reason = None
        self.response = None
    
    def get(self, objid):
        """Génère et envoie une requête GET (interrogation du registre).
        
        * :py:attr:`errcode` et :py:attr:`reason` avec respectivement
          le code et la description de l'erreur renvoyée par le serveur
          le cas échéant, ``None`` sinon.
        * :py:attr:`raw` avec le résultat brut de la requête.
        * :py:attr:`response` avec la désérialisation du résultat
          de la requête. En cas d'erreur, il s'agit d'un dictionnaire
          avec une unique clé ``error``.
        
        Parameters
        ----------
        objid : str
            Identifiant (dans le registre) de l'objet pour lequel on
            souhaite consulter le registre. Le slash initial peut être
            omis.
        
        Raises
        ------
        ValueError
            Lorsque le résultat de la requête n'est pas un JSON valide.
        
        Examples
        --------
        >>> api = RegisterApi()
        >>> api.get('plume/isExternal')
        >>> description = api.response
        
        """
        self.raw = None
        self.response = None
        self.errcode = None
        self.reason = None
        url = urljoin(self.api, objid)
        self.request = Request(url)
        try:
            with urlopen(self.request) as src:
                self.raw = src.read()
        except HTTPError as err:
            self.errcode = err.code
            self.reason = err.reason
            self.raw = err.read()
            try:
                self.response = loads(self.raw)
            except:
                pass
            return
        try:
            self.response = loads(self.raw)
        except:
            raise ValueError('Echec de la désérialisation du JSON.')
        
    
    def post(self, objid):
        """Génère et envoie une requête POST (consultation des données du registre).
        
        Cette méthode met à jour les attributs suivants:
        
        * :py:attr:`errcode` et :py:attr:`reason` avec respectivement
          le code et la description de l'erreur renvoyée par le serveur
          le cas échéant, ``None`` sinon.
        * :py:attr:`raw` avec le résultat brut de la requête.
        * :py:attr:`response` avec la désérialisation du résultat
          de la requête, qui devrait être un dictionnaire dont les
          clés sont ``id``, ``parent``, ``type``, ``title``,
          ``script``, ``jsonval`` et ``htmlval`` lorsqu'il n'y a pas
          eu d'erreur, ou une unique clé ``error`` en cas d'erreur.
        
        Parameters
        ----------
        objid : str
            Identifiant (dans le registre) de l'objet pour lequel on
            souhaite consulter le registre. Le slash initial peut être
            omis.
        
        Raises
        ------
        ValueError
            Lorsque le résultat de la requête n'est pas un JSON valide.
        
        Examples
        --------
        >>> api = RegisterApi()
        >>> api.post('plume/isExternal')
        >>> description = api.response
        
        """
        self.raw = None
        self.response = None
        self.errcode = None
        self.reason = None
        url = urljoin(self.api, objid)
        self.request = Request(url, method='POST')
        try:
            with urlopen(self.request) as src:
                self.raw = src.read()
        except HTTPError as err:
            self.errcode = err.code
            self.reason = err.reason
            self.raw = err.read()
            try:
                self.response = loads(self.raw)
            except:
                pass
            return
        try:
            self.response = loads(self.raw)
        except:
            raise ValueError('Echec de la désérialisation du JSON.')
    
    def put(self, objid, data=None):
        """Génère et envoie une requête PUT (mise à jour du registre).
        
        Cette méthode met à jour les attributs suivants:
        
        * :py:attr:`errcode` et :py:attr:`reason` avec respectivement
          le code et la description de l'erreur renvoyée par le serveur
          le cas échéant, ``None`` sinon.
        * :py:attr:`raw` avec la réponse brute du serveur.
        * :py:attr:`response`, qui vaut toujours ``None`` sauf dans
          le cas où le serveur a renvoyé une erreur sous forme de JSON.
          Il s'agit alors d'un dictionnaire avec une unique clé ``error``.
        
        Parameters
        ----------
        objid : str
            Identifiant (dans le registre) de l'objet à ajouter ou
            mettre à jour. Le slash initial peut être omis.
        data : bytes, optionnal
            Les paramètres de la requête. Si non fourni, la méthode
            récupère les informations nécessaires dans la collection
            d'objets locaux, dans laquelle `objid` doit alors
            être impérativement être référencé.
        
        Examples
        --------
        >>> api = RegisterApi()
        >>> api.put('plume/isExternal')
        
        """
        self.raw = None
        self.response = None
        self.errcode = None
        self.reason = None
        url = urljoin(self.api, objid)
        if not data:
            data = self.collection[objid.strip('/')].parameters()
        self.request = Request(url, data=data, method='PUT')
        try:
            with urlopen(self.request) as src:
                self.raw = src.read()
        except HTTPError as err:
            self.errcode = err.code
            self.reason = err.reason
            self.raw = err.read()
            try:
                self.response = loads(self.raw)
            except:
                pass

    def delete(self, objid):
        """Génère et envoie une requête DELETE (suppression d'un objet du registre).
        
        Cette méthode met à jour les attributs suivants:
        
        * :py:attr:`errcode` et :py:attr:`reason` avec respectivement
          le code et la description de l'erreur renvoyée par le serveur
          le cas échéant, ``None`` sinon.
        * :py:attr:`raw` avec la réponse brute du serveur.
        * :py:attr:`response`, qui vaut toujours ``None`` sauf dans
          le cas où le serveur a renvoyé une erreur sous forme de JSON.
          Il s'agit alors d'un dictionnaire avec une unique clé ``error``.
        
        Parameters
        ----------
        objid : str
            Identifiant (dans le registre) de l'objet à supprimer. Le slash
            initial peut être omis.
        
        Examples
        --------
        >>> api = RegisterApi()
        >>> api.delete('plume/isExternal')
        
        """
        self.raw = None
        self.response = None
        self.errcode = None
        self.reason = None
        url = urljoin(self.api, objid)
        self.request = Request(url, method='DELETE')
        try:
            with urlopen(self.request) as src:
                self.raw = src.read()
        except HTTPError as err:
            self.errcode = err.code
            self.reason = err.reason
            self.raw = err.read()
            try:
                self.response = loads(self.raw)
            except:
                pass
    
    def update(self, abort_on_failure=True):
        """Met à jour le registre distant selon les informations locales.
        
        Cette méthode boucle sur la collection d'objets de Plume 
        :py:attr:``RegistreApi.collection`` pour mettre à
        jour les éléments correspondants du registre, sans chercher
        à savoir s'ils avaient réellement été modifiés entre temps.
        
        Pour l'heure, elle n'est pas capable d'identifier les éléments
        du registres qui n'apparaissent plus dans la collection en
        vue de leur suppression.
        
        Pour chaque objet, un message dans la console indique si la
        mise à jour a réussi ou échoué.
        
        Parameters
        ----------
        abort_on_failure : bool, default True
            Si ``True``, les mises à jour s'arrêtent à la première
            erreur rencontrée, sinon elles se poursuivent
            pour les objets suivants de la collection.
        
        """
        for objid, objdef in self.collection.items():
            self.put(objid)
            if self.errcode:
                print('{} > Erreur {} : {}.'.format(objid, self.errcode,
                    self.reason))
                if self.response:
                    print(self.response.get('error', ''))
                if abort_on_failure:
                    break
            else:
                print('{} > Mise à jour réussie.'.format(objid))

class ObjectDefinition:
    """Définition d'un objet RDF créé par Plume.
    
    Attributes
    ----------
    objid : str
        Fragment d'URI constituant l'identifiant de l'objet dans
        le registre (sans le slash initial).
    parent : str
        Identifiant de l'objet parent, le cas échéant.
    objtype : {'R', 'E'}
        Type d'objet. `R` (registre) pour un ensemble de concepts,
        `E` (élément) pour un concept, une propriété ou une classe.
    title : str
        Le libellé principal de l'objet.
    graph : rdflib.graph.Graph
        Graphe contenant la description de l'objet.
    jsonval : list
        Désérialisation python de la sérialisation JSON-LD de
        `graph`.
    
    """
    def __init__(self, objid, objtype, title, graph):
        self.objid = objid.strip('/')
        if '/' in self.objid:
            self.parent = '/{}'.format(self.objid.rsplit('/', 1)[0])
        else:
            self.parent = ''
        self.objtype = objtype
        self.title = title
        self.graph = graph
        self.jsonval = None
        if graph:
            jsonld = graph.serialize(format='json-ld')
            self.jsonval = loads(jsonld)

    def parameters(self):
        """Renvoie la description de l'objet sous forme de paramètres utilisables par une requête HTTP POST.
        
        Returns
        -------
        bytes
            Représentation binaire d'un objet JSON.
        
        """
        data = dumps({
            'parent': self.parent or '',
            'type': self.objtype or 'E',
            'title': self.title or '',
            'script': '',
            'jsonval': self.jsonval or '',
            'htmlval': ''
            })
        return data.encode('ascii')
    
class ConceptDefinition(ObjectDefinition):
    """Définition d'un concept de Plume.
    
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
            objid = str(iri).replace(str(PLUME), 'plume/')
            s = iri
        else:
            scheme = vocabulary.value(iri, SKOS.inScheme)
            if not str(scheme).startswith(str(PLUME)):
                raise ValueError("Le concept '{}' n'appartient pas à un " \
                    'thésaurus créé par Plume.'.format(iri))
            suffix = vocabulary.value(iri, DCT.identifier) or iri.rsplit('/', 1)[1]
            objid = '{}/{}'.format(str(scheme).replace(str(PLUME), 'plume/'), suffix)
            s = URIRef('{}/{}'.format(scheme, suffix))
            graph.add((s, SKOS.exactMatch, iri))
        labels = [o for o in vocabulary.objects(iri, SKOS.prefLabel)]
        title = str(pick_translation(labels, ('fr', 'en')))
        for p, o in vocabulary.predicate_objects(iri):
            if not p == DCT.identifier:
                # les DCT.identifier ne sont vraiment là que pour
                # fournir des identifiants plus acceptables quand
                # le dernier élément de l'URI du concept ne l'est
                # pas (ex : http://www.opengis.net/def/crs/EPSG/0),
                # il ne paraît pas pertinent de les exposer
                graph.add((s, p, o))
        super().__init__(objid=objid, objtype='E',
            title=title, graph=graph)

class ConceptSchemeDefinition(ObjectDefinition):
    """Définition d'un ensemble de concepts de Plume.
    
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
            objid = str(iri).replace(str(PLUME), 'plume/')
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
    """Définition d'une propriété de Plume.
    
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
            objid = str(iri).replace(str(PLUME), 'plume/')
        else:
            raise ValueError("'{}' n'est pas une " \
                'propriété créée par Plume.'.format(iri))
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
    """Définition d'une classe de Plume.
    
    Parameters
    ----------
    iri : rdflib.term.URIRef
        L'IRI de la classe, présumée référencée
        dans :py:data:`plume.rdf.properties.shape`.
    
    Raises
    ------
    ValueError
        Si la classe n'utilise pas l'espace de nommage de
        Plume. Il est alors considéré qu'il ne s'agit pas
        d'une classe créée par Plume.
    
    Notes
    -----
    À ce stade, le libellé et la description de la
    classe sont ceux de la propriété qui l'introduit,
    étant entendu que, dans le schéma des métadonnées
    communes de Plume, toute classe autre que ``dcat:Dataset``
    est nécessairement introduite par au moins une propriété
    et, en pratique, jamais plus d'une pour l'heure.
    
    """
    
    def __init__(self, iri):
        graph = Graph(namespace_manager=PlumeNamespaceManager())
        if str(iri).startswith(str(PLUME)):
            objid = str(iri).replace(str(PLUME), 'plume/')
        else:
            raise ValueError("'{}' n'est pas une " \
                'classe créée par Plume.'.format(iri))
        for n in shape.subjects(SH['class'], iri):
            labels = [o for o in shape.objects(n, SH.name)]
            title = str(pick_translation(labels, ('fr', 'en')))
            for o in labels:
                graph.add((iri, RDFS.label, o))
            for o in shape.objects(n, SH.description):
                graph.add((iri, RDFS.comment, o))
            break
        super().__init__(objid=objid, objtype='E',
            title=title, graph=graph)

class DefinitionsCollection(dict):
    """Répertoire de définitions des objets du registre de Plume.
    
    Les objets de cette classe sont initialisés par
    lecture du schéma des métadonnées communes,
    :py:data:`plume.rdf.properties.shape`,
    et de la compilation des thésaurus de Plume,
    :py:data:`plume.rdf.thesaurus.vocabulary`. Sont
    conservés les propriétés, classes, concepts et
    ensemble de concepts utilisant l'espace de nommage
    de Plume, ainsi que tous les concepts de ensembles
    de concepts utilisant l'espace de nommage de Plume.
    
    Les clés du dictionnaire sont les identifiants des objets
    dans le registre (sans le slash initial), les valeurs
    sont les objets :py:class:`ObjectDefinition` qui les
    décrivent.
    
    """
    
    def __init__(self):
        self['plume'] = ObjectDefinition(objid='plume', objtype='R',
            title="Registre de l'application Plume (gestion des métadonnées d'un patrimoine PostgreSQL)",
            graph=None)
        for s, p, iri in shape.triples((None, SH.path, None)):
            if str(iri).startswith(str(PLUME)):
                od = PropertyDefinition(iri)
                self[od.objid] = od
        for s, p, iri in shape.triples((None, SH.targetClass, None)):
            if str(iri).startswith(str(PLUME)): 
                od = ClassDefinition(iri)
                self[od.objid] = od
        for iri, p, s in vocabulary.triples((None, RDF.type, SKOS.ConceptScheme)):
            if str(iri).startswith(str(PLUME)): 
                od = ConceptSchemeDefinition(iri)
                self[od.objid] = od
        for iri, p, s in vocabulary.triples((None, SKOS.inScheme, None)):
            if str(iri).startswith(str(PLUME)) or str(s).startswith(str(PLUME)): 
                od = ConceptDefinition(iri)
                self[od.objid] = od
    
