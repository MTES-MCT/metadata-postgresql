"""Graphes de métadonnées.

"""

from uuid import UUID, uuid4
from pathlib import Path

from plume.rdf.rdflib import Graph, URIRef, BNode, Literal
from plume.rdf.namespaces import PlumeNamespaceManager, DCAT, RDF, SH, \
    LOCAL, SNUM, DCT, predicate_map
from plume.rdf.utils import abspath, DatasetId, graph_from_file, get_datasetid, \
    export_extension_from_format, export_format_from_extension, export_formats, \
    forbidden_char
from plume.iso.map import IsoToDcat


shape = graph_from_file(abspath('rdf/data/shape.ttl'))
"""Schéma SHACL définissant la structure des métadonnées communes.

"""

class Metagraph(Graph):
    """Graphes de métadonnées.
    
    Un graphe de métadonnées est présumé décrire un et un seul jeu de
    données (dcat:Dataset).
    
    Attributes
    ----------
    datasetid
    available_formats
    linked_record
    
    Notes
    -----   
    Tous les graphes de métadonnées sont initialisés avec
    l'espace de nommage standard de Plume
    (:py:class:`plume.rdf.namespaces.PlumeNamespaceManager`).
    
    """
    def __init__(self):
        super().__init__(namespace_manager=PlumeNamespaceManager())

    def __str__(self):
        datasetid = self.datasetid
        gid = datasetid.uuid if isinstance(datasetid, DatasetId) else datasetid
        if gid:
            return 'dataset {}'.format(gid)
        return 'no dataset'

    @property
    def datasetid(self):
        """rdflib.term.URIRef: Identifiant du jeu de données décrit par le graphe.
        
        Peut être ``None`` si le graphe de métadonnées ne contient
        pas d'élément ``dcat:Dataset``.
        
        Il est possible de définir l'identifiant du jeu de données via
        cette propriété, sous réserve que le graphe soit vide (dans le cas
        contraire, la commande n'aura aucun effet).
        
        Identifiant aléatoire:
        
            >>> metagraph = Metagraph()
            >>> metagraph.datasetid = None
            >>> metagraph.datasetid
            DatasetId('urn:uuid:...')
        
        Identifiant pré-déterminé:
        
            >>> metagraph = Metagraph()
            >>> metagraph.datasetid = '523d5fa9-77a8-41da-a5ce-36b64fe935ed'
            >>> metagraph.datasetid
            DatasetId('urn:uuid:523d5fa9-77a8-41da-a5ce-36b64fe935ed')
        
        L'identifiant doit être UUID valide, sans quoi un nouvel UUID sera
        utilisé à la place. Il peut être fourni sous la forme d'une chaîne
        de caractères, d'un objet :py:class:`uuid.UUID`, :py:class:`rdflib.URIRef`
        ou encore :py:class:`plume.rdf.utils.DatasetId`.
        
        """
        return get_datasetid(self)

    @datasetid.setter
    def datasetid(self, value):
        if len(self) > 0:
            return
        datasetid = DatasetId(value)
        self.add((datasetid, RDF.type, DCAT.Dataset))

    @property
    def linked_record(self):
        """tuple(str): Fiche de métadonnées distante référencée par le graphe, le cas échéant.
        
        Le tuple est constitué de deux éléments : l'URL de base du service
        CSW et l'identifiant de la fiche.
        
        À défaut de configuration sauvegardée, cette propriété vaut ``None``.
        
        Pour sauvegarder une configuration:
        
            >>> metagraph = Metagraph()
            >>> metagraph.datasetid = None
            >>> metagraph.linked_record = (
            ...     'http://ogc.geo-ide.developpement-durable.gouv.fr/csw/dataset-harvestable', 
            ...     'fr-120066022-jdd-d3d794eb-76ba-450a-9f03-6eb84662f297'
            ...     ) 
        
        Le graphe doit a minima contenir un identifiant de jeu de données,
        sans quoi la tentative de sauvegarde sera silencieusement ignorée.
        
        Pour effacer la configuration:
        
            >>> metagraph.linked_record = None
        
        """
        datasetid = self.datasetid
        url_csw = self.value(datasetid, SNUM.linkedRecord / SNUM.csw)
        file_identifier = self.value(datasetid, SNUM.linkedRecord / DCT.identifier)
        if url_csw and file_identifier:
            return (str(url_csw), str(file_identifier))

    @linked_record.setter
    def linked_record(self, value):
        if value is not None:
            if not isinstance(value, tuple) \
                or not len(value)==2:
                return
            url_csw, file_identifier = value
            if forbidden_char(url_csw):
                return
        datasetid = self.datasetid
        if not datasetid:
            return
        node = self.value(datasetid, SNUM.linkedRecord)
        if node:
            self.remove((node, SNUM.csw, None))
            self.remove((node, DCT.identifier, None))
            if value is None:
                self.remove((datasetid, SNUM.linkedRecord, node))
                return
        else:
            node = BNode()
        if value is not None:
            self.add((datasetid, SNUM.linkedRecord, node))
            self.add((node, SNUM.csw, URIRef(url_csw)))
            self.add((node, DCT.identifier, Literal(file_identifier)))

    def print(self):
        """Imprime le graphe de métadonnées dans la console (sérialisation turtle).
        
        """
        print(self.serialize())

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
        acceptées, on exécutera :py:func:`plume.rdf.utils.import_formats`.
    old_metagraph : Metagraph, optional
        Le graphe contenant les métadonnées actuelles de l'objet
        PostgreSQL considéré, dont on récupèrera l'identifiant.
    
    Returns
    -------
    Metagraph
    
    Notes
    -----
    Cette fonction se borne à exécuter successivement
    :py:func:`plume.rdf.utils.graph_from_file` et
    :py:func:`clean_metagraph`.
    
    """
    g = graph_from_file(filepath, format=format)
    return clean_metagraph(g, old_metagraph=old_metagraph)

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
    raw_datasetid = get_datasetid(raw_graph)
    old_datasetid = old_metagraph.datasetid if old_metagraph else None
    datasetid = DatasetId(old_datasetid)
    
    if not raw_datasetid :
        # le graphe ne contient pas de dcat:Dataset
        # on renvoie un graphe avec uniquement l'ancien
        # identifiant (ou potentiellement un nouveau
        # si l'ancien n'était pas un UUID valide)
        metagraph.add((datasetid, RDF.type, DCAT.Dataset))
        return metagraph

    memory = Graph()
    
    # memory stockera les triples déjà traités de raw_graph,
    # il sert à éviter les boucles
    for p, o in raw_graph.predicate_objects(raw_datasetid):
        triple = (datasetid, predicate_map.get(p, p), o)
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
        
    old_datasetid = old_metagraph.datasetid if old_metagraph else None
    datasetid = DatasetId(old_datasetid)
    metagraph = Metagraph()
    
    # cas où le graphe à copier ne contiendrait pas
    # de descriptif de dataset, on renvoie un graphe contenant
    # uniquement l'identifiant
    if not src_datasetid:
        metagraph.add((datasetid, RDF.type, DCAT.Dataset))
        return metagraph
    
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

def metagraph_from_iso(raw_xml, old_metagraph=None):
    """Crée un graphe de métadonnées à partir d'un XML renvoyé par un service CSW.
    
    Parameters
    ----------
    raw_xml : str
        Le résultat brut retourné par le service CSW, présumé être
        un XML conforme au standard ISO 19139.
    old_metagraph : Metagraph, optional
        Le graphe contenant les métadonnées actuelles de l'objet
        PostgreSQL considéré, dont on récupèrera l'identifiant.
    
    Returns
    -------
    Metagraph
    
    Examples
    --------
    >>> from urllib.request import urlopen
    >>> from plume.iso.csw import getrecordbyid_request
    >>> r = getrecordbyid_request(
	...     'http://ogc.geo-ide.developpement-durable.gouv.fr/csw/dataset-harvestable', 
	...     'fr-120066022-jdd-3c998f8c-0e33-4ae5-8535-150a745bccce'
	...     )
    >>> with urlopen(r) as src:
	...     xml = src.read()
    >>> g = metagraph_from_iso(xml)
    
    """
    old_datasetid = old_metagraph.datasetid if old_metagraph else None
    metagraph = Metagraph()
    metagraph.datasetid = old_datasetid

    if raw_xml:
        iso = IsoToDcat(raw_xml, datasetid=metagraph.datasetid)
        for t in iso.triples:
            metagraph.add(t)
    return metagraph



