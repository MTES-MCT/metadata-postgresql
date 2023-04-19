"""Répertoire des thésaurus.

Tout nouveau vocabulaire utilisable doit être ajouté sous la forme
d'un fichier encodé en turtle dans le répertoire ``plume/rdf/data/vocabularies``.
Le ou les IRI des ensembles qu'il contient doivent également 
être listés dans :py:data:``VOCABULARIES``, pour expliciter le lien
avec le fichier susmentionné. 

"""

from locale import strxfrm, setlocale, LC_COLLATE

from plume.rdf.rdflib import Graph, URIRef
from plume.rdf.exceptions import UnknownSource
from plume.rdf.namespaces import FOAF, SKOS, PlumeNamespaceManager
from plume.rdf.utils import abspath, pick_translation, graph_from_file, MetaCollection

VOCABULARIES = {
    'http://registre.data.developpement-durable.gouv.fr/plume/ISO19139ProgressCode': 'iso_19139_progress_code.ttl'
}  

class VocabularyGraph(Graph, metaclass=MetaCollection):
    """Graphe contenant le vocabulaire d'un thésaurus.
    
    Pour obtenir le graphe de vocabulaire associé à
    l'IRI d'un ensemble de concepts ``iri`` :

        >>> graph = VocabularyGraph[iri]

    Si le vocabulaire avait déjà été mobilisé auparavant,
    son graphe est récupéré dans les données en mémoire,
    sinon il est chargé depuis le fichier qui contient les
    données. Pour cela, ``iri`` doit être répertorié dans
    :py:data:`VOCABULARIES` (sous la forme d'une chaîne de
    caractères), avec en valeur le nom du fichier du 
    répertoire ``plume/rdf/data/vocabularies`` où se trouvent
    les données. Dans le cas contraire, une erreur 
    :py:class:`plume.rdf.exceptions.UnknownSource` est émise.

    Attributes
    ----------
    iri : rdflib.term.URIRef
        L'IRI de l'ensemble de concepts qui identifie
        le vocabulaire.
    
    """

    def __new__(cls, iri):
        file = VOCABULARIES.get(str(iri))
        if not file:
            raise UnknownSource(iri)
        
        filepath = abspath('rdf/data/vocabularies') / file
        if not filepath.exists() or not filepath.is_file():
            raise UnknownSource(iri)

        return graph_from_file(filepath)
    
    def __init__(self, iri):
        super().__init__(namespace_manager=PlumeNamespaceManager())
        self.iri = iri

    def all_vocabularies():
        """Renvoie un graphe contenant tous les vocabulaires connus.
        
        Returns
        -------
        rdflib.graph.Graph
        
        """
        graph = Graph(namespace_manager=PlumeNamespaceManager())
        for str_iri in VOCABULARIES:
            graph += VocabularyGraph[URIRef(str_iri)]

class Thesaurus(metaclass=MetaCollection):
    """Thésaurus.
    
    Pour accéder à un thésaurus déjà chargé ou le générer :

        >>> Thesaurus[(iri, langlist)]

    Tout nouveau thésaurus généré de cette façon est mémorisé pour
    gagner en temps de calcul.
    
    Parameters
    ----------
    iri : rdflib.term.URIRef
        L'IRI du thésaurus.
    langlist : tuple(str)
        Le tuple de langues pour lequel le thésaurus doit être
        généré. Lorsque plusieurs traductions sont disponibles, les
        langues qui apparaissent en premier dans `langlist` seront
        privilégiées.
    
    Attributes
    ----------
    label : str
        Le libellé du thésaurus.
    iri : rdflib.term.URIRef
        L'IRI du thésaurus.
    langlist : tuple(str)
        Le tuple de langues pour lequel le thésaurus a été généré.
    values : list
        La liste des termes du thésaurus.
    iri_from_str : dict
        Dictionnaire dont les clés sont les libellés des termes du
        thésaurus et les valeurs les IRI correspondants.
    str_from_iri : dict
        Dictionnaire dont les clés sont les IRI des termes du
        thésaurus et les valeurs leurs libellés.
    links_from_iri : dict
        Dictionnaire dont les clés sont les IRI des termes du
        thésaurus et les valeurs les liens associés.
    
    """
    
    @classmethod
    def get_values(cls, thesaurus):
        """Cherche ou génère un thésaurus et renvoie la liste de ses termes.
        
        Parameters
        ----------
        thesaurus : tuple(rdflib.term.URIRef, tuple(str))
            Source. Tuple dont le premier élément est l'IRI de la source,
            le second un tuple de langues pour lequel le thésaurus doit
            être généré. Lorsque plusieurs traductions sont disponibles,
            les langues qui apparaissent en premier dans le tuple
            seront privilégiées.
        
        Returns
        -------
        list
            La liste des termes du thésaurus. La première valeur de la liste
            est toujours une chaîne de caractères vides.
        
        Raises
        ------
        UnknownSource
            Si le thésaurus non seulement n'avait pas déjà été compilé,
            mais n'est pas répertorié dans :py:data:`VOCABULARIES`.
        
        Examples
        --------
        >>> thesaurus = (URIRef('http://registre.data.developpement-durable.gouv.fr/plume/CrpaAuthorizedLicense'), ('fr', 'en'))
        >>> Thesaurus.get_values(thesaurus)
        ['', 'Licence Ouverte version 2.0', 'ODC Open Database License (ODbL) version 1.0']
        
        """
        t = Thesaurus[thesaurus]
        return t.values
    
    @classmethod
    def get_label(cls, thesaurus):
        """Cherche ou génère un thésaurus et renvoie son libellé.
        
        Parameters
        ----------
        thesaurus : tuple(rdflib.term.URIRef, tuple(str))
            Source. Tuple dont le premier élément est l'IRI de la source,
            le second un tuple de langues pour lequel le thésaurus doit
            être généré. Lorsque plusieurs traductions sont disponibles,
            les langues qui apparaissent en premier dans le tuple
            seront privilégiées.
        
        Returns
        -------
        str
            Le libellé du thésaurus.
        
        Raises
        ------
        UnknownSource
            Si le thésaurus non seulement n'avait pas déjà été compilé,
            mais n'est pas répertorié dans :py:data:`VOCABULARIES`.
        
        Examples
        --------
        >>> thesaurus = (URIRef('http://registre.data.developpement-durable.gouv.fr/plume/CrpaAccessLimitations'), ('fr', 'en'))
        >>> Thesaurus.get_label(thesaurus)
        "Restrictions d'accès en application du Code des relations entre le public et l'administration"
        
        """
        t = Thesaurus[thesaurus]
        return t.label
    
    @classmethod
    def concept_iri(cls, thesaurus, concept_str):
        """Cherche ou génère un thésaurus et renvoie l'IRI d'un concept.
        
        Parameters
        ----------
        thesaurus : tuple(rdflib.term.URIRef, tuple(str))
            Source. Tuple dont le premier élément est l'IRI de la source,
            le second un tuple de langues pour lequel le thésaurus doit
            être généré. Lorsque plusieurs traductions sont disponibles,
            les langues qui apparaissent en premier dans le tuple
            seront privilégiées.
        concept_str : str
            Le libellé d'un terme présumé issu du thésaurus, dont on
            cherche l'IRI.
        
        Returns
        -------
        rdflib.term.URIRef
            L'IRI du concept. Peut être ``None``, si le thésaurus existe
            mais que la chaîne de caractères n'y est pas répertoriée.
        
        Raises
        ------
        UnknownSource
            Si le thésaurus non seulement n'avait pas déjà été compilé,
            mais n'est pas répertorié dans :py:data:`VOCABULARIES`.
        
        Examples
        --------
        >>> thesaurus = (URIRef('http://registre.data.developpement-durable.gouv.fr/plume/CrpaAccessLimitations'), ('fr', 'en'))
        >>> Thesaurus.concept_iri(
        ...     thesaurus, 
        ...     'Communicable au seul intéressé - atteinte à la protection de la vie privée (CRPA, L311-6 1°)'
        ...     )
        rdflib.term.URIRef('http://registre.data.developpement-durable.gouv.fr/plume/CrpaAccessLimitations/L311-6-1-vp')
        
        """
        t = Thesaurus[thesaurus]
        return t.iri_from_str.get(concept_str)
    
    @classmethod
    def concept_str(cls, thesaurus, concept_iri):
        """Cherche ou génère un thésaurus et renvoie le libellé d'un concept.
        
        Parameters
        ----------
        thesaurus : tuple(rdflib.term.URIRef, tuple(str))
            Source. Tuple dont le premier élément est l'IRI de la source,
            le second un tuple de langues pour lequel le thésaurus doit
            être généré. Lorsque plusieurs traductions sont disponibles,
            les langues qui apparaissent en premier dans le tuple
            seront privilégiées.
        concept_iri : rdflib.term.URIRef
            L'IRI d'un terme présumé issu du thésaurus, dont on cherche
            le libellé.
        
        Returns
        -------
        str
            Le libellé du concept. Peut être ``None``, si le thésaurus existe
            mais que l'IRI n'y est pas répertorié.
        
        Raises
        ------
        UnknownSource
            Si le thésaurus non seulement n'avait pas déjà été compilé,
            mais n'est pas répertorié dans :py:data:`VOCABULARIES`.
        
        Examples
        --------
        >>> thesaurus = (URIRef('http://registre.data.developpement-durable.gouv.fr/plume/CrpaAccessLimitations'), ('fr', 'en'))
        >>> Thesaurus.concept_str(
        ...     thesaurus,
        ...     URIRef('http://registre.data.developpement-durable.gouv.fr/plume/CrpaAccessLimitations/L311-6-1-vp')
        ...     )
        'Communicable au seul intéressé - atteinte à la protection de la vie privée (CRPA, L311-6 1°)'
        
        """
        t = Thesaurus[thesaurus]
        return t.str_from_iri.get(concept_iri)
    
    @classmethod
    def concept_link(cls, thesaurus, concept_iri):
        """Cherche ou génère un thésaurus et renvoie le lien d'un concept.
        
        Parameters
        ----------
        thesaurus : tuple(rdflib.term.URIRef, tuple(str))
            Source. Tuple dont le premier élément est l'IRI de la source,
            le second un tuple de langues pour lequel le thésaurus doit
            être généré. Lorsque plusieurs traductions sont disponibles,
            les langues qui apparaissent en premier dans le tuple
            seront privilégiées.
        concept_iri : rdflib.term.URIRef
            L'IRI d'un terme présumé issu du thésaurus, dont on cherche le lien.
        
        Returns
        -------
        rdflib.term.URIRef
            Le lien associé au concept. Peut être ``None``, si le thésaurus
            existe mais que l'IRI n'y est pas répertorié.
        
        Raises
        ------
        UnknownSource
            Si le thésaurus non seulement n'avait pas déjà été compilé,
            mais n'est pas répertorié dans :py:data:`VOCABULARIES`.
        
        Examples
        --------
        >>> thesaurus = (URIRef('http://registre.data.developpement-durable.gouv.fr/plume/CrpaAccessLimitations'), ('fr', 'en'))
        >>> Thesaurus.concept_link(
        ...     thesaurus, 
        ...     URIRef('http://registre.data.developpement-durable.gouv.fr/plume/CrpaAccessLimitations/L311-6-1-vp')
        ...     )
        rdflib.term.URIRef('https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000037269056')
        
        """
        t = Thesaurus[thesaurus]
        return t.links_from_iri.get(concept_iri)
    
    @classmethod
    def concept_source(cls, concept_iri, scheme_iris):
        """Renvoie l'IRI du thésaurus référençant l'IRI considérée.
        
        Parameters
        ----------
        concept_iri : rdflib.term.URIRef
            L'IRI d'un terme présumé issu d'un thésaurus.
        scheme_iris : list(rdflib.term.URIRef)
            Les IRI des ensembles auxquels l'URI est présumé
            appartenir, soit ceux qui sont autorisés pour la
            catégorie de métadonnées considérée. Pour des questions
            d'optimisation, il est préférable que les premiers
            ensembles listés soient les plus petits et/ou les
            plus susceptibles de contenir le concept considéré.

        Returns
        -------
        rdflib.term.URIRef
            Le bon IRI parmis ceux qui étaient listés dans
            `scheme_iris`.
        
        """
        for iri in scheme_iris:
            vocabulary = VocabularyGraph[iri]
            if source := vocabulary.value(concept_iri, SKOS.inScheme):
                return source
    
    def __init__(self, iri, langlist):
        self.iri = iri
        self.langlist = langlist
        self.values = []
        self.iri_from_str = {}
        self.str_from_iri = {}
        self.links_from_iri = {}
        self.graph = VocabularyGraph[iri]
        
        slabels = [o for o in self.graph.objects(iri, SKOS.prefLabel)]
        if slabels:
            t = pick_translation(slabels, langlist)
            self.label = str(t)
        else:
            raise UnknownSource(iri)
        
        concepts = [c for c in self.graph.subjects(SKOS.inScheme, iri)] 

        if concepts:
            for c in concepts:
                clabels = [o for o in self.graph.objects(c, SKOS.prefLabel)]
                if clabels:
                    t = pick_translation(clabels, langlist)
                    self.values.append(str(t))
                    self.iri_from_str.update({str(t): c})
                    self.str_from_iri.update({c: str(t)})
                    page = self.graph.value(c, FOAF.page)
                    self.links_from_iri.update({c: page or c})

            if self.values:
                setlocale(LC_COLLATE, "")
                self.values.sort(
                    key=lambda x: strxfrm(x)
                    )
        self.values.insert(0, '')
    

