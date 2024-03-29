"""Graphes de métadonnées.

"""

from pathlib import Path
from time import strftime, localtime

from plume.rdf.rdflib import Graph, URIRef, BNode, Literal
from plume.rdf.namespaces import (
    PlumeNamespaceManager, DCAT, RDF, SH, LOCAL, PLUME, DCT, FOAF,
    XSD, PREDICATE_MAP, CLASS_MAP
)
from plume.rdf.utils import (
    abspath, DatasetId, graph_from_file, get_datasetid,
    export_extension_from_format, export_format_from_extension,
    export_formats, forbidden_char, data_from_file, import_formats
)
from plume.rdf.transliterations import transliterate

from plume.iso.map import IsoToDcat


SHAPE = graph_from_file(abspath('rdf/data/shape.ttl'))
"""Schéma SHACL définissant la structure des métadonnées communes.

"""

class Metagraph(Graph):
    """Graphes de métadonnées.
    
    Un graphe de métadonnées est présumé décrire un et un seul jeu de
    données (dcat:Dataset).
    
    Attributes
    ----------
    fresh : bool
        ``False`` pour un graphe de métadonnées généré par
        désérialisation d'un dictionnaire de widgets (méthode
        :py:meth:`plume.rdf.widgetsdict.WidgetsDict.build_metagraph`).
    rewritten : bool
        ``True`` si le graphe est issu d'une source externe. Concrètement,
        les constructeurs :py:func:`clean_metagraph`, :py:func:`copy_metagraph`
        et :py:func:`metagraph_from_iso` mettent cet attribut à ``True``
        sur les graphes qu'elles génèrent. Il vaudra ``False`` dans tous
        les autres cas.
    langlist : tuple(str)
        Tuple des langues autorisées pour les traductions, hérité
        le cas échéant du dictionnaire de widgets à partir duquel
        le graphe a été généré. Dans les autres cas, cet attribut
        vaut toujours ``('fr', 'en')``.
    
    Notes
    -----   
    Tous les graphes de métadonnées sont initialisés avec
    l'espace de nommage standard de Plume
    (:py:class:`plume.rdf.namespaces.PlumeNamespaceManager`).
    
    """
    def __init__(self):
        super().__init__(namespace_manager=PlumeNamespaceManager())
        self.fresh = True
        self.rewritten = False
        self.langlist = ('fr', 'en')

    def __str__(self):
        datasetid = self.datasetid
        gid = datasetid.uuid if isinstance(datasetid, DatasetId) else datasetid
        if gid:
            return 'dataset {}'.format(gid)
        return 'no dataset'

    @property
    def is_empty(self):
        """bool: Le graphe est-il vide ?
        
        Au sens de cette propriété, un graphe de métadonnées est considéré
        comme vide quand il contient au plus un identifiant et une
        date de dernière modification de la fiche de métadonnées.
        
        Un graphe qui ne contiendrait pas d'élément de classe ``dcat:Dataset``
        sera toujours considéré comme vide.
        
        """
        datasetid = self.datasetid
        if datasetid is None:
            return True
        bnode = self.value(datasetid, FOAF.isPrimaryTopicOf)
        for s, p, o in self:
            if p == RDF.type or (s == datasetid and \
                p in (DCT.identifier, FOAF.isPrimaryTopicOf)) \
                or (bnode and (s, p) == (bnode, DCT.modified)):
                continue
            return False
        return True

    @property
    def datasetid(self):
        """rdflib.term.URIRef: Identifiant du jeu de données décrit par le graphe.
        
        Peut être ``None`` si le graphe de métadonnées ne contient
        pas d'élément ``dcat:Dataset``.
        
        Il est possible de définir l'identifiant du jeu de données via
        cette propriété, sous réserve que le graphe soit vide (dans le cas
        contraire, la commande n'aura aucun effet).
        
        Identifiant aléatoire :
        
            >>> metagraph = Metagraph()
            >>> metagraph.datasetid = None
            >>> metagraph.datasetid
            DatasetId('urn:uuid:...')
        
        Identifiant pré-déterminé :
        
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
        
        À défaut de configuration sauvegardée, cette propriété vaut ``(None, None)``.
        
        Pour sauvegarder une configuration :
        
            >>> metagraph = Metagraph()
            >>> metagraph.datasetid = None
            >>> metagraph.linked_record = (
            ...     'http://ogc.geo-ide.developpement-durable.gouv.fr/csw/dataset-harvestable', 
            ...     'fr-120066022-jdd-d3d794eb-76ba-450a-9f03-6eb84662f297'
            ...     ) 
        
        Le graphe doit a minima contenir un identifiant de jeu de données,
        sans quoi la tentative de sauvegarde sera silencieusement ignorée.
        
        Pour effacer la configuration :
        
            >>> metagraph.linked_record = None
        
        """
        datasetid = self.datasetid
        url_csw = self.value(datasetid, PLUME.linkedRecord / DCAT.endpointURL)
        file_identifier = self.value(datasetid, PLUME.linkedRecord / DCT.identifier)
        return (str(url_csw) if url_csw else None,
            str(file_identifier) if file_identifier else None)

    @linked_record.setter
    def linked_record(self, value):
        if value is not None:
            if not isinstance(value, tuple) \
                or not len(value)==2:
                return
            url_csw, file_identifier = value
            if not url_csw and not file_identifier:
                value = None
            elif url_csw and forbidden_char(url_csw):
                url_csw = None
        datasetid = self.datasetid
        if not datasetid:
            return
        node = self.value(datasetid, PLUME.linkedRecord)
        if node:
            self.remove((node, DCAT.endpointURL, None))
            self.remove((node, DCT.identifier, None))
            if value is None:
                self.remove((datasetid, PLUME.linkedRecord, node))
                return
        else:
            node = BNode()
        if value is not None:
            self.add((datasetid, PLUME.linkedRecord, node))
            if url_csw:
                self.add((node, DCAT.endpointURL, URIRef(url_csw)))
            if file_identifier:
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
        
        See Also
        --------
        :py:meth:`Metagraph.available_export_formats`
            Méthode dont est dérivée cette propriété.
        
        """ 
        return self.available_export_formats()

    def available_export_formats(self, no_duplicate=False, format=None):
        """Renvoie la liste des formats d'export recommandés pour le graphe.
        
        Parameters
        ----------
        no_duplicate : bool, default False
            Si ``True``, lorsque plusieurs formats disponibles
            utilise la même extension (cas notamment de ``'xml'`` et
            ``'pretty-xml'``), la méthode n'en renvoie qu'un.
        format : str, optional
            Un format d'export à prioriser. `format` ne sera
            jamais éliminé par la suppression de pseudo-doublons
            effectuée lorsque `no_duplicate` vaut ``True``. Il
            s'agira toujours de la première valeur de la liste
            renvoyée, sauf s'il ne s'agissait pas d'un format
            d'export disponible (auquel cas il ne sera pas du tout
            dans la liste renvoyée).
        
        Returns
        -------
        list(str)
        
        Notes
        -----
        À date, cette méthode appelle la fonction
        :py:func:`plume.rdf.utils.export_formats`, puis exclut
        du résultat les formats ``'xml'`` et ``'pretty-xml'`` 
        en présence de catégories locales de métadonnées, car leurs 
        espaces de nommage ne sont pas gérés correctement. Il s'agit
        d'une limitation de RDFLib et non du format, qui pourrait être 
        corrigée à l'avenir.
        
        """
        l = export_formats(no_duplicate=no_duplicate, format=format)
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
        l = [(p, o) for p, o in raw_metagraph.predicate_objects(raw_subject) \
            if not p == RDF.type]
        
        if l:
            raw_rdfclass = raw_metagraph.value(raw_subject, RDF.type)
            rdfclass = CLASS_MAP.get(raw_rdfclass, raw_rdfclass)
            # s'il n'y a pas de classe, ou que la classe n'est pas décrite
            # dans SHAPE, un IRI ou Literal sera écrit tel quel,
            # sans ses descendants, un BNode est effacé
            if not rdfclass or \
                not (None, SH.targetClass, rdfclass) in SHAPE:
                l = []
                if isinstance(raw_subject, BNode):
                    return
            else:
                l.append((RDF.type, rdfclass))

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
                triple = (subject, PREDICATE_MAP.get(p, p), o)
                self._clean_metagraph(raw_metagraph, o, triple, memory)

    def merge(self, alt_metagraph, replace=False):
        """Met à jour le graphe de métadonnées avec le contenu d'un autre graphe de métadonnées.
        
        Parameters
        ----------
        alt_metagraph : Metagraph
            Un autre graphe de métadonnées.
        replace : bool, default False
            Mode de fusion des deux graphes :
            
            * Si `replace` vaut ``True``, les informations du
              graphe source sont preservées pour les catégories
              de métadonnées non présentes dans le graphe complémentaire.
              Sinon, elles sont remplacées par celles du graphe
              complémentaire.
            * Si `replace` vaut ``False``, les valeurs du 
              graphe complémentaire ne sont importées que pour les
              catégories de métadonnées qui n'étaient pas
              renseignées dans le graphe source.
        
        Notes
        -----
        À ce stade, le mécanisme de fusion est sommaire. En particulier,
        il n'est pas récursif et, dans le cas de catégories qui
        admettent plusieurs valeurs, remplace ou préserve toutes
        les valeurs plutôt que de les comparer une à une.
        
        Par principe, la propriété dct:identifier n'est jamais
        remplacée, même si `replace` vaut ``True``, puisqu'elle
        est censée rester cohérente avec l'URI du dcat:Dataset.
        
        """
        alt_datasetid = alt_metagraph.datasetid if alt_metagraph else None
        if not alt_datasetid:
            return
        
        datasetid = self.datasetid
        if not datasetid:
            self.datasetid = None
            # NB: génère un nouvel identifiant
            datasetid = self.datasetid
        
        for predicate in alt_metagraph.predicates(alt_datasetid):
            if predicate in (RDF.type, DCT.identifier):
                continue
            if (datasetid, predicate, None) in self:
                if replace:
                    for o in self.objects(datasetid, predicate):
                        self.remove((datasetid, predicate, o))
                        if isinstance(o, BNode):
                            self.delete_branch(o)
                else:
                    continue
            for o in alt_metagraph.objects(alt_datasetid, predicate):
                self.add((datasetid, predicate, o))
                if isinstance(o, BNode):
                    self.copy_branch(alt_metagraph, o)

    def delete_branch(self, bnode):
        """Supprime du graphe de métadonnées une branche non liée au dcat:Dataset.
        
        Parameters
        ----------
        bnode : rdflib.terms.BNode
            Le noeud anonyme sujet de la branche libre à
            supprimer.
        
        Notes
        -----
        Cette méthode est récursive. Partant des triplets
        dont `bnode` était sujet, elle les supprime et
        supprime à leur tour les triplets dont leurs objets
        étaient sujets (sauf à ce que ce sujet demeure
        l'objet d'un autre triplet), et ainsi de suite.
        
        Elle n'aura d'effet que si tous les triplets
        dont `bnode` était objet ont préalablement
        été supprimés du graphe.
        
        """
        if not isinstance(bnode, BNode):
            return
        for triple in self.triples((bnode, None, None)):
            self.remove(triple)
            o = triple[2]
            if isinstance(o, BNode) and not (None, None, o) in self:
                self.delete_branch(o)

    def copy_branch(self, alt_metagraph, bnode):
        """Copie dans le graphe une branche d'un autre graphe.
        
        Parameters
        ----------
        alt_metagraph : Metagraph
            Le graphe de métadonnées contenant la branche
            à copier.
        bnode : rdflib.terms.BNode
            Le noeud anonyme sujet de la branche à copier
            de `alt_metagraph`. Il est présumé exister en
            tant qu'objet dans le graphe source, sans
            quoi la méthode n'aura aucun effet.
        
        Notes
        -----
        Cette méthode préserve les noeuds anonymes copiés
        (mêmes identifiants dans le graphe résultant que
        dans `alt_metagraph`).
        
        """
        if not isinstance(bnode, BNode) or not (None, None, bnode) in self:
            return
        for triple in alt_metagraph.triples((bnode, None, None)):
            if not triple in self:
                self.add(triple)
                o = triple[2]
                if isinstance(o, BNode):
                    self.copy_branch(alt_metagraph, o)

    def update_metadata_date(self):
        """Met à jour la date de dernière modification des métadonnées.
        
        """
        datasetid = self.datasetid
        date = Literal(strftime("%Y-%m-%dT%H:%M:%S", localtime()),
            datatype=XSD.dateTime)
        bnode = self.value(datasetid, FOAF.isPrimaryTopicOf)
        if not bnode:
            bnode = BNode()
            self.add((datasetid, FOAF.isPrimaryTopicOf, bnode))
            self.add((bnode, RDF.type, DCAT.CatalogRecord))
        else:
            self.remove((bnode, DCT.modified, None))
        self.add((bnode, DCT.modified, date))

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

def metagraph_from_rdf_data(data, format, old_metagraph=None):
    """Crée un graphe à partir de données textuelles, résultant par exemple d'une requête internet.

    Parameters
    ----------
    data : str
        Données RDF brutes.
    format : str
        Le format d'encodage des données. Pour connaître la liste des valeurs
        acceptées, on exécutera :py:func:`plume.rdf.utils.import_formats`.
    old_metagraph : Metagraph, optional
        Le graphe contenant les métadonnées actuelles de l'objet
        PostgreSQL considéré, dont on récupèrera l'identifiant (et
        lui seul, tout le reste est perdu).
    
    Returns
    -------
    Metagraph

    """
    raw_graph = Graph()
    if not format in import_formats():
        raise ValueError(f"Format '{format}' is not supported.")
    raw_graph.parse(data=data, format=format)
    return clean_metagraph(raw_graph, old_metagraph=old_metagraph)

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
    metagraph.rewritten = True
    raw_datasetid = get_datasetid(raw_graph)
    old_datasetid = old_metagraph.datasetid if old_metagraph else None
    datasetid = DatasetId(old_datasetid)
    
    if not raw_datasetid :
        # le graphe ne contient pas de dcat:Dataset
        # on renvoie un graphe avec uniquement l'ancien
        # identifiant (ou potentiellement un nouveau
        # si l'ancien n'était pas un UUID valide)
        metagraph.add((datasetid, RDF.type, DCAT.Dataset))
        transliterate(metagraph)
        return metagraph

    memory = Graph()
    
    # memory stockera les triples déjà traités de raw_graph,
    # il sert à éviter les boucles
    for p, o in raw_graph.predicate_objects(raw_datasetid):
        triple = (datasetid, PREDICATE_MAP.get(p, p), o)
        metagraph._clean_metagraph(raw_graph, o, triple, memory)
    
    transliterate(metagraph)
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
        src_metagraph = Metagraph()
        src_datasetid = None
    else:  
        src_datasetid = src_metagraph.datasetid
        
    old_datasetid = old_metagraph.datasetid if old_metagraph else None
    datasetid = DatasetId(old_datasetid)
    metagraph = Metagraph()
    metagraph.rewritten = True
    
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

def metagraph_from_iso(raw_xml, old_metagraph=None, preserve='always'):
    """Crée un graphe de métadonnées à partir d'un XML renvoyé par un service CSW.
    
    Parameters
    ----------
    raw_xml : str
        Le résultat brut retourné par le service CSW, présumé être
        un XML conforme au standard ISO 19139.
    old_metagraph : Metagraph, optional
        Le graphe contenant les métadonnées actuelles de l'objet
        PostgreSQL considéré, dont on récupèrera l'identifiant.
    preserve : {'always', 'if blank', 'never'}, optional
        Mode de fusion de l'ancien et du nouveau graphe :
        
        * Si `preserve` vaut ``'never'``, le graphe est
          est intégralement recréé à partir des informations
          disponibles sur le catalogue distant. Hormis l'identifiant,
          tout le contenu de l'ancien graphe est perdu.
        * Si `preserve` vaut ``'if blank'``, les informations de
          l'ancien graphe ne sont preservées que pour les
          catégories de métadonnées qui ne sont pas renseignées
          sur le catalogue distant.         .
        * Si `preserve` vaut ``'always'``, les valeurs du 
          catalogue distant ne sont importées que pour les
          catégories de métadonnées qui n'étaient pas
          renseignées dans l'ancien graphe.
    
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
    metagraph.rewritten = True

    if raw_xml:
        iso = IsoToDcat(raw_xml, datasetid=metagraph.datasetid)
        for t in iso.triples:
            metagraph.add(t)
    
    if preserve != 'never':
        metagraph.merge(old_metagraph, replace=(preserve == 'always'))
    
    return metagraph

def metagraph_from_iso_file(filepath, old_metagraph=None, preserve='never'):
    """Crée un graphe de métadonnées à partir d'un fichier XML contenant des métadonnées INSPIRE/ISO 19139.
    
    Parameters
    ----------
    filepath : str
        Chemin complet du fichier source, supposé contenir des
        métadonnées INSPIRE/ISO 19139, sans quoi la fiche de
        métadonnées résultante sera certainement vide.
        Le fichier sera présumé être encodé en UTF-8 et mieux
        vaudrait qu'il le soit.
    old_metagraph : Metagraph, optional
        Le graphe contenant les métadonnées actuelles de l'objet
        PostgreSQL considéré, dont on récupèrera l'identifiant.
    preserve : {'never', 'if blank', 'always'}, optional
        Mode de fusion de l'ancien et du nouveau graphe :
        
        * Si `preserve` vaut ``'never'``, le graphe est
          est intégralement recréé à partir des informations
          disponibles sur le catalogue distant. Hormis l'identifiant,
          tout le contenu de l'ancien graphe est perdu.
        * Si `preserve` vaut ``'if blank'``, les informations de
          l'ancien graphe ne sont preservées que pour les
          catégories de métadonnées qui ne sont pas renseignées
          sur le catalogue distant.         .
        * Si `preserve` vaut ``'always'``, les valeurs du 
          catalogue distant ne sont importées que pour les
          catégories de métadonnées qui n'étaient pas
          renseignées dans l'ancien graphe.
    
    Returns
    -------
    Metagraph
    
    Notes
    -----
    Cette fonction se borne à exécuter successivement
    :py:func:`plume.rdf.utils.data_from_file` et
    :py:func:`metagraph_from_iso`.
    
    """
    raw_xml = data_from_file(filepath)
    return metagraph_from_iso(raw_xml, old_metagraph=old_metagraph, preserve=preserve)

