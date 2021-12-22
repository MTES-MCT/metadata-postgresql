"""Graphes RDF.

"""

from uuid import UUID, uuid4
from pathlib import Path

from plume.rdf.rdflib import Graph, URIRef, BNode
from plume.rdf.namespaces import PlumeNamespaceManager, DCAT, RDF, SH, \
    LOCAL, predicate_map
from plume.rdf.utils import abspath


class Metagraph(Graph):
    """Graphes de métadonnées.
    
    Un graphe de métadonnées est présumé décrire un et un seul jeu de
    données (dcat:Dataset).
    
    Attributes
    ----------
    datasetid
    uuid
    available_formats
    
    Notes
    -----   
    Tous les graphes de métadonnées sont initialisés avec
    l'espace de nommage standard de Plume
    (:py:class:`plume.rdf.namespaces.PlumeNamespaceManager`).
    
    """
    def __init__(self):
        super().__init__(namespace_manager=PlumeNamespaceManager())

    def __str__(self):
        gid = self.uuid
        if gid:
            return 'dataset {}'.format(gid)
        return 'no dataset'

    @property
    def datasetid(self):
        """rdflib.term.URIRef: Identifiant du jeu de données décrit par le graphe, sous forme d'IRI.
        
        Peut être ``None`` si le graphe de métadonnées ne contient
        pas d'élément ``dcat:Dataset``.
        
        """
        return get_datasetid(self)

    @property
    def uuid(self):
        """uuid.UUID: Identifiant du jeu de données décrit par le graphe, sous forme d'UUID.
        
        Peut être ``None`` si le graphe de métadonnées ne contient
        pas d'élément ``dcat:Dataset``, ou si l'identifiant, pour une
        raison ou une autre, n'était pas un UUID valide.
        
        """
        datasetid = self.datasetid
        if datasetid:
            return uuid_from_datasetid(datasetid)

    def export(self, filepath, format=None):
        """Sérialise le graphe de métadonnées dans un fichier.
        
        Parameters
        ----------
        filepath : str
            Chemin complet du fichier cible.
        format : str, optional
            Format d'export. Pour connaître la liste des valeurs
            acceptées, on exécutera :py:func:`export_formats`.
            À noter certains formats peuvent donner un résultat peu
            probant selon le graphe. La propriété
            :py:attr:`available_formats` fournit une liste de formats
            présumés adaptés pour le graphe, il préférable de choisir
            l'un d'eux.
            Si aucun format n'est fourni et qu'il ne peut pas être
            déduit de l'extension du fichier cible, l'export sera fait
            en turtle.
        
        Notes
        -----
        Le fichier sera toujours encodé en UTF-8 sauf pour le format
        NTriples (encodage ASCII).
        
        """
        pfile = Path(filepath)

        if format and not format in export_formats():
            raise ValueError("Format '{}' is not supported.".format(format))
        
        # en l'absence de format, si le chemin comporte un
        # suffixe, on tente d'en déduire le format
        if not format and pfile.suffix:
            format = export_format_from_extension(pfile.suffix)
        if not format:
            format = 'turtle'
        
        # réciproquement, si le nom de fichier n'a pas
        # de suffixe, on en ajoute un d'après le format
        if not pfile.suffix:
            pfile = pfile.with_suffix(
                export_extension_from_format(format) or ''
                )
        
        s = self.serialize(
            format=format,
            encoding='ascii' if format=='nt' else 'utf-8'
            )
        
        with open(pfile, 'wb') as dest:
            dest.write(s)

    @property
    def available_formats(self):
        """list(str): Liste des formats d'export recommandés pour le graphe.
        
        Notes
        -----
        À date, cette propriété exclut les formats ``'xml'`` et
        ``'pretty-xml'`` en présence de catégories locales de
        métadonnées, car leurs espaces de nommage ne sont pas
        gérés correctement. Il s'agit d'une limitation de RDFLib
        et non du format, qui pourrait être corrigée à l'avenir.
        
        """
        l = export_formats()
        # Une méthode plus gourmande pourrait consister à purement et simplement
        # tester toutes les sérialisations possibles et retourner celles qui
        # ne produisent pas d'erreur. À ce stade, il semble cependant que
        # la seule incompatibilité prévisible et admissible soit la
        # combinaison XML + usage d'UUID pour les métadonnées locales. C'est
        # donc uniquement ce cas qui est testé ici.
        for p in self.predicates():
            if p in LOCAL:
                for f in ('xml', 'pretty-xml'):
                    if f in l:
                        l.remove(f)            
                break  
        return l

    def _clean_metagraph(self, raw_metagraph, raw_subject, triple, memory):
        l = [(p, o) for p, o in raw_metagraph.predicate_objects(raw_subject)]
        
        # si la liste ne contient que la classe de l'IRI
        # ou du noeud anonyme, on passe
        if (len(l) == 1 and l[0][0] == RDF.type):
            l = []
        
        if l:
            rdfclass = raw_metagraph.value(raw_subject, RDF.type)
            # s'il n'y a pas de classe, ou que la classe n'est pas décrite
            # dans shape, un IRI ou Literal sera écrit tel quel,
            # sans ses descendants, un BNode est effacé
            if not rdfclass or \
                not (None, SH.targetClass, rdfclass) in shape:
                l = []
                if isinstance(raw_subject, BNode):
                    return

        # suppression des noeuds anonymes terminaux
        if not l and isinstance(raw_subject, BNode):
            return
        
        subject = raw_subject
        # cas d'un IRI non terminal
        # on le remplace par un noeud anonyme
        if l and not isinstance(raw_subject, BNode):
            subject = BNode()
            triple = (triple[0], triple[1], subject)
        
        self.add(triple)
        
        for p, o in l:
            if not (raw_subject, p, o) in memory:
                memory.add((raw_subject, p, o))
                triple = (subject, predicate_map.get(p, p), o)
                self._clean_metagraph(raw_metagraph, o, triple, memory)



# ------ utilitaires de gestion des identifiants ------

def uuid_from_datasetid(datasetid):
    """Extrait l'UUID d'un identifiant de jeu de données.
    
    Parameters
    ----------
    datasetid : URIRef
        Un identifiant de jeu de données.
    
    Returns
    -------
    uuid.UUID
        L'UUID contenu dans l'identifiant. ``None`` si l'identifiant
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
    uuid : uuid.UUID or str
        Un UUID ou une chaîne de caractères présumée
        être un UUID.
    
    Returns
    -------
    URIRef
        Un identifiant de jeu de données. ``None`` si la valeur n'était
        pas un UUID.
    
    """
    if not isinstance(uuid, UUID):
        try:
            uuid = UUID(uuid)
        except:
            return
    return URIRef(uuid.urn)

def get_datasetid(anygraph):
    """Renvoie l'identifiant du jeu de données éventuellement contenu dans le graphe.
    
    Parameters
    ----------
    anygraph : Graph
        Un graphe quelconque, présumé contenir la description d'un
        jeu de données (``dcat:Dataset``).
    
    Returns
    -------
    URIRef
        L'identifiant du jeu de données. None si le graphe ne contenait
        pas de jeu de données.
    
    """
    for s in anygraph.subjects(RDF.type, DCAT.Dataset):
        return s

# ------ utilitaires d'import / export ------

def metagraph_from_file(filepath, format=None, old_metagraph=None):
    """Crée un graphe de métadonnées à partir d'un fichier.
    
    Parameters
    ----------
    filepath : str
        Chemin complet du fichier source, supposé contenir des
        métadonnées dans un format RDF, sans quoi l'import échouera.
        Le fichier sera présumé être encodé en UTF-8 et mieux
        vaudrait qu'il le soit.
    format : str, optional
        Le format des métadonnées. Si non renseigné, il est autant que
        possible déduit de l'extension du fichier, qui devra donc être
        cohérente avec son contenu. Pour connaître la liste des valeurs
        acceptées, on exécutera :py:func:`import_formats`.
    old_metagraph : Metagraph, optional
        Le graphe contenant les métadonnées actuelles de l'objet
        PostgreSQL considéré, dont on récupèrera l'identifiant.
    
    Returns
    -------
    Metagraph
    
    Notes
    -----
    Cette fonction se borne à exécuter successivement :py:func:`graph_from_file`
    et :py:func:`clean_metagraph`.
    
    """
    g = graph_from_file(filepath, format=format)
    return clean_metagraph(g, old_metagraph=old_metagraph)

def graph_from_file(filepath, format=None):
    """Désérialise le contenu d'un fichier sous forme de graphe.
    
    Le fichier sera présumé être encodé en UTF-8 et mieux
    vaudrait qu'il le soit.
    
    Parameters
    ----------
    filepath : str
        Chemin complet du fichier source, supposé contenir des
        métadonnées dans un format RDF, sans quoi l'import échouera.
    format : str, optional
        Le format des métadonnées. Si non renseigné, il est autant que
        possible déduit de l'extension du fichier, qui devra donc être
        cohérente avec son contenu. Pour connaître la liste des valeurs
        acceptées, on exécutera :py:func:`import_formats`.
    
    Returns
    -------
    Graph
        Un graphe.
    
    """
    pfile = Path(filepath)
    
    if not pfile.exists():
        raise FileNotFoundError("Can't find file {}.".format(filepath))
        
    if not pfile.is_file():
        raise TypeError("{} is not a file.".format(filepath))
    
    if format and not format in import_formats():
        raise ValueError("Format '{}' is not supported.".format(format))
    
    if not format:
        if not pfile.suffix in import_extensions_from_format():
            raise TypeError("Couldn't guess RDF format from file extension." \
                            "Please use format to declare it manually.")
                            
        else:
            format = import_format_from_extension(pfile.suffix)
            # NB : en théorie, la fonction parse de RDFLib est censée
            # pouvoir reconnaître le format d'après l'extension, mais à
            # ce jour elle n'identifie même pas toute la liste ci-avant.
    
    with pfile.open(encoding='UTF-8') as src:
        g = Graph().parse(data=src.read(), format=format)
    return g

def clean_metagraph(raw_graph, old_metagraph=None):
    """Crée un graphe propre à partir d'un graphe issu d'une source externe.
    
    Parameters
    ----------
    raw_graph : rdflib.graph.Graph
        Un graphe de métadonnées présumé issu d'un import via
        :py:func:`graph_from_file` ou équivalent.
    old_metagraph : Metagraph, optional
        Le graphe contenant les métadonnées actuelles de l'objet
        PostgreSQL considéré, dont on récupèrera l'identifiant.
    
    Returns
    -------
    Metagraph
    
    Notes
    -----
    Le graphe est retraité de manière à ce qu'un maximum de
    métadonnées soient reconnues lors de la génération du dictionnaire
    de widgets. En particulier, la fonction s'assure que tous les noeuds
    sont des noeuds anonymes.
    
    """
    metagraph = Metagraph()
    raw_subject = get_datasetid(raw_graph)
    subject = None
    if old_metagraph:
        subject = old_metagraph.datasetid
    
    if not raw_subject :
        # le graphe ne contient pas de dcat:Dataset
        # on renvoie un graphe avec uniquement l'ancien
        # identifiant, ou vierge en l'absence d'identifiant
        if subject:
            metagraph.add((subject, RDF.type, DCAT.Dataset))
        return metagraph
    
    # à défaut d'avoir pu récupérer l'identifiant de
    # l'ancien graphe, on en génère un nouveau
    if not subject:
        subject = datasetid_from_uuid(uuid4())
    memory = Graph()
    
    # memory stockera les triples déjà traités de raw_graph,
    # il sert à éviter les boucles
    for p, o in raw_graph.predicate_objects(raw_subject):
        triple = (subject, predicate_map.get(p, p), o)
        metagraph._clean_metagraph(raw_graph, o, triple, memory)
    return metagraph

def copy_metagraph(src_metagraph=None, old_metagraph=None):
    """Génère un nouveau graphe de métadonnées avec le contenu du graphe cible. 

    Parameters
    ----------
    src_metagraph : Metagraph, optional
        Le graphe dont on souhaite copier le contenu. Si non
        spécifié, la fonction considère un graphe vide.
    old_metagraph : Metagraph, optional
        Le graphe contenant les métadonnées actuelles de l'objet
        PostgreSQL considéré, dont on récupèrera l'identifiant.
    
    Returns
    -------
    Metagraph
    
    Notes
    -----
    Cette fonction ne réalise aucun contrôle sur les informations
    qu'elle copie. Si `src_metagraph` n'est pas issu d'une source fiable,
    il est préférable d'utiliser :py:func:`clean_metagraph`.
    
    """
    if src_metagraph is None:
        src_metagraph = Graph()
        src_datasetid = None
    else:  
        src_datasetid = src_metagraph.datasetid
        
    datasetid = old_metagraph.datasetid if old_metagraph else None
    metagraph = Metagraph()
    
    # cas où le graphe à copier ne contiendrait pas
    # de descriptif de dataset, on renvoie un graphe contenant
    # uniquement l'identifiant, ou vierge à défaut d'identifiant
    if not src_datasetid:
        if datasetid:
            metagraph.add((datasetid, RDF.type, DCAT.Dataset))
        return metagraph
    
    # à défaut d'avoir pu d'extraire un identifiant de l'ancien
    # graphe, on en génère un nouveau
    if not datasetid:
        datasetid = datasetid_from_uuid(uuid4())
    
    # boucle sur les triples du graphe source, on remplace
    # l'identifiant partout où il apparaît en sujet ou (même si
    # ça ne devrait pas être le cas) en objet
    for s, p, o in src_metagraph:
        metagraph.add((
            datasetid if s == src_datasetid else s,
            p,
            datasetid if o == src_datasetid else o
            ))
        
    # NB : on ne se préoccupe pas de mettre à jour dct:identifier,
    # ce sera fait à l'initialisation du dictionnaire de widgets.
    return metagraph

def import_formats():
    """Renvoie la liste de tous les formats disponibles pour l'import.
    
    Returns
    -------
    list of str
        La liste des formats reconnus par RDFLib à l'import.
    
    """
    return [ k for k, v in rdflib_formats.items() if v['import'] ]

def export_formats():
    """Renvoie la liste de tous les formats disponibles pour l'export.
    
    Returns
    -------
    list of str
        La liste des formats reconnus par RDFLib à l'export.
    
    """
    return [ k for k in rdflib_formats.keys() ]

def import_extensions_from_format(format=None):
    """Renvoie la liste des extensions associées à un format d'import.
    
    Parameters
    ----------
    format : str, optional
        Un format d'import présumé inclus dans la liste des formats
        reconnus par les fonctions de RDFLib (rdflib_formats avec
        import=True).
    
    Returns
    -------
    list of str
        La liste de toutes les extensions associées au format considéré,
        avec le point.
        Si `format` n'est pas renseigné, la fonction renvoie la liste
        de toutes les extensions reconnues pour l'import.
    
    Examples
    --------
    >>> import_extensions_from_format('xml')
    ['.rdf', '.xml']
    
    """
    if not format:
        l = []
        for k, d in rdflib_formats.items():
            if d['import']:
                l += d['extensions']
        return l
    
    d = rdflib_formats.get(format)
    if d and d['import']:
        return d['extensions']

def export_extension_from_format(format):
    """Renvoie l'extension utilisée pour les exports dans le format considéré.
    
    Parameters
    ----------
    format : str
        Un format d'export présumé inclus dans la liste des formats
        reconnus par les fonctions de RDFLib (rdflib_format).
    
    Returns
    -------
    str
        L'extension à utiliser pour le format considéré, avec le point.
    
    Example
    -------
    >>> rdf_utils.export_extension('pretty-xml')
    '.rdf'
    
    """
    d = rdflib_formats.get(format)
    if d:
        return d['extensions'][0]

def import_format_from_extension(extension):
    """Renvoie le format d'import correspondant à l'extension.
    
    Parameters
    ----------
    extension : str
        Une extension (avec point).
    
    Returns
    -------
    str
        Un nom de format. La fonction renvoie None si l'extension
        n'est pas reconnue.
    
    """
    for k, d in rdflib_formats.items():
        if d['import'] and extension in d['extensions']:
            return k

def export_format_from_extension(extension):
    """Renvoie le format d'export correspondant à l'extension.
    
     Parameters
    ----------
    extension : str
        Une extension (avec point).
    
    Returns
    -------
    str
        Un nom de format. La fonction renvoie None si l'extension
        n'est pas reconnue.
    
    """
    for k, d in rdflib_formats.items():
        if d['export default'] and extension in d['extensions']:
            return k

rdflib_formats = {
    'turtle': {
        'extensions': ['.ttl'],
        'import': True,
        'export default': True
        },
    'n3': {
        'extensions': ['.n3'],
        'import': True,
        'export default': True
        },
    'json-ld': {
        'extensions': ['.jsonld', '.json'],
        'import': True,
        'export default': True
        },
    'xml': {
        'extensions': ['.rdf', '.xml'],
        'import': True,
        'export default': False
        },
    'pretty-xml': {
        'extensions': ['.rdf', '.xml'],
        'import': False,
        'export default': True
        },
    'nt': {
        'extensions': ['.nt'],
        'import': True,
        'export default': True
        },
    'trig': {
        'extensions': ['.trig'],
        'import': True,
        'export default': True
        }
    }
"""Formats reconnus par les fonctions de RDFLib.

Si la clé ``import`` vaut ``False``, le format n'est pas reconnu
à l'import. Si ``export default`` vaut ``True``, il s'agit du
format d'export privilégié pour les extensions listées
par la clé ``extension``.

"""

shape = graph_from_file(abspath('rdf/data/shape.ttl'))
"""Schéma SHACL définissant la structure des métadonnées communes.

"""
