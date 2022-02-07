"""Répertoire des thésaurus.

"""

from locale import strxfrm, setlocale, LC_COLLATE

from plume.rdf.rdflib import Graph, URIRef
from plume.rdf.exceptions import UnknownSource
from plume.rdf.namespaces import FOAF, SKOS, SNUM
from plume.rdf.utils import abspath, pick_translation, graph_from_file

vocabulary = graph_from_file(abspath('rdf/data/vocabulary.ttl'))
"""Graphe contenant le vocabulaire de tous les thésaurus.

"""
  
class Thesaurus:
    """Thésaurus.
    
    Tout nouveau thésaurus généré est mémorisé pour gagner en temps
    de calcul.
    
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
    iri : URIRef
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
    
    collection = {}
    """Accès à l'ensemble des thésaurus déjà compilés.
    
    `collection` est un dictionnaire dont les clés sont des tuples
    (`iri`, `langlist`) et les valeurs l'objet :py:class:`Thesaurus`
    lui-même.
    
    """
    
    @classmethod
    def get_values(cls, thesaurus):
        """Cherche ou génère un thésaurus et renvoie la liste de ses termes.
        
        Autant que possible, cette méthode va chercher les termes dans le
        répertoire des thésaurus déjà compilés (:py:attr:`Thesaurus.collection`),
        à défaut le thésaurus est compilé à partir de :py:data:`vocabulary`.
        
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
            mais n'existe même pas dans :py:data:`vocabulary`.
        
        Examples
        --------
        >>> Thesaurus.get_values((SNUM.CrpaAuthorizedLicense, ('fr', 'en')))
        ['', 'Licence Ouverte version 2.0', 'ODC Open Database License (ODbL) version 1.0']
        
        """
        if thesaurus in cls.collection:
            return cls.collection[thesaurus].values
        t = Thesaurus(*thesaurus)
        if t:
            return t.values
        raise UnknownSource(thesaurus[0])
    
    @classmethod
    def get_label(cls, thesaurus):
        """Cherche ou génère un thésaurus et renvoie son libellé.
        
        Autant que possible, cette méthode va chercher le libellé dans le
        répertoire des thésaurus déjà compilés (:py:attr:`Thesaurus.collection`),
        à défaut le thésaurus est compilé à partir de :py:data:`vocabulary`.
        
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
            mais n'existe même pas dans :py:data:`vocabulary`.
        
        Examples
        --------
        >>> Thesaurus.get_label((SNUM.CrpaAccessLimitations, ('fr', 'en')))
        "Restrictions d'accès en application du Code des relations entre le public et l'administration"
        
        """
        if thesaurus in cls.collection:
            return cls.collection[thesaurus].label
        t = Thesaurus(*thesaurus)
        if t:
            return t.label
        raise UnknownSource(thesaurus[0])
    
    @classmethod
    def concept_iri(cls, thesaurus, concept_str):
        """Cherche ou génère un thésaurus et renvoie l'IRI d'un concept.
        
        Autant que possible, cette méthode va chercher l'IRI dans le
        répertoire des thésaurus déjà compilés (:py:attr:`Thesaurus.collection`),
        à défaut le thésaurus est compilé à partir de :py:data:`vocabulary`.
        
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
        URIRef
            L'IRI du concept. Peut être ``None``, si le thésaurus existe
            mais que la chaîne de caractères n'y est pas répertoriée.
        
        Raises
        ------
        UnknownSource
            Si le thésaurus non seulement n'avait pas déjà été compilé,
            mais n'existe même pas dans :py:data:`vocabulary`.
        
        Examples
        --------
        >>> Thesaurus.concept_iri(
        ...     (SNUM.CrpaAccessLimitations, ('fr', 'en')), 
        ...     'Communicable au seul intéressé - atteinte à la' \
        ...         ' protection de la vie privée (CRPA, L311-6 1°)'
        ...     )
        rdflib.term.URIRef('http://snum.scenari-community.org/Metadata/Vocabulaire/#CrpaAccessLimitations-311-6-1-vp')
        
        """
        if thesaurus in cls.collection:
            return cls.collection[thesaurus].iri_from_str.get(concept_str)
        t = Thesaurus(*thesaurus)
        if t:
            return t.iri_from_str.get(concept_str)
        raise UnknownSource(thesaurus[0])
    
    @classmethod
    def concept_str(cls, thesaurus, concept_iri):
        """Cherche ou génère un thésaurus et renvoie le libellé d'un concept.
        
        Autant que possible, cette méthode va chercher le libellé dans le
        répertoire des thésaurus déjà compilés (:py:attr:`Thesaurus.collection`),
        à défaut le thésaurus est compilé à partir de :py:data:`vocabulary`.
        
        Parameters
        ----------
        thesaurus : tuple(rdflib.term.URIRef, tuple(str))
            Source. Tuple dont le premier élément est l'IRI de la source,
            le second un tuple de langues pour lequel le thésaurus doit
            être généré. Lorsque plusieurs traductions sont disponibles,
            les langues qui apparaissent en premier dans le tuple
            seront privilégiées.
        concept_iri : URIRef
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
            mais n'existe même pas dans :py:data:`vocabulary`.
        
        Examples
        --------
        >>> Thesaurus.concept_str(
        ...     (SNUM.CrpaAccessLimitations, ('fr', 'en')), 
        ...     SNUM['CrpaAccessLimitations-311-6-1-vp']
        ...     )
        'Communicable au seul intéressé - atteinte à la protection de la vie privée (CRPA, L311-6 1°)'
        
        """
        if thesaurus in cls.collection:
            return cls.collection[thesaurus].str_from_iri.get(concept_iri)
        t = Thesaurus(*thesaurus)
        if t:
            return t.str_from_iri.get(concept_iri)
        raise UnknownSource(thesaurus[0])
    
    @classmethod
    def concept_link(cls, thesaurus, concept_iri):
        """Cherche ou génère un thésaurus et renvoie le lien d'un concept.
        
        Autant que possible, cette méthode va chercher le lien dans le
        répertoire des thésaurus déjà compilés (:py:attr:`Thesaurus.collection`),
        à défaut le thésaurus est compilé à partir de :py:data:`vocabulary`.
        
        Parameters
        ----------
        thesaurus : tuple(rdflib.term.URIRef, tuple(str))
            Source. Tuple dont le premier élément est l'IRI de la source,
            le second un tuple de langues pour lequel le thésaurus doit
            être généré. Lorsque plusieurs traductions sont disponibles,
            les langues qui apparaissent en premier dans le tuple
            seront privilégiées.
        concept_iri : URIRef
            L'IRI d'un terme présumé issu du thésaurus, dont on cherche le lien.
        
        Returns
        -------
        URIRef
            Le lien associé au concept. Peut être ``None``, si le thésaurus
            existe mais que l'IRI n'y est pas répertorié.
        
        Raises
        ------
        UnknownSource
            Si le thésaurus non seulement n'avait pas déjà été compilé,
            mais n'existe même pas dans :py:data:`vocabulary`.
        
        Examples
        --------
        >>> Thesaurus.concept_link(
        ...     (SNUM.CrpaAccessLimitations, ('fr', 'en')), 
        ...     SNUM['CrpaAccessLimitations-311-6-1-vp']
        ...     )
        rdflib.term.URIRef('https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000037269056')
        
        """
        if thesaurus in cls.collection:
            return cls.collection[thesaurus].links_from_iri.get(concept_iri)
        t = Thesaurus(*thesaurus)
        if t:
            return t.links_from_iri.get(concept_iri)
        raise UnknownSource(thesaurus[0])
    
    @classmethod
    def concept_source(cls, concept_iri):
        """Renvoie l'IRI du thésaurus référençant l'IRI considérée.
        
        Parameters
        ----------
        concept_iri : URIRef
            L'IRI d'un terme présumé issu d'un thésaurus.

        Returns
        -------
        URIRef
        
        Notes
        -----
        Cette méthode se borne à interroger :py:data:`vocabulary`.
        Elle n'exploite pas le répertoire des thésaurus.
        
        """
        return vocabulary.value(concept_iri, SKOS.inScheme)
    
    @classmethod
    def add(cls, iri, langlist, thesaurus):
        """Ajoute un thésaurus au répertoire des thésaurus compilés.
        
        Parameters
        ----------
        iri : URIRef
            L'IRI du thésaurus considéré.
        langlist : tuple(str)
            Le tuple de langues pour lequel le thésaurus a été généré.
        thesaurus : Thesaurus
            Le thésaurus en tant que tel.
        
        """
        cls.collection.update({(iri, langlist): thesaurus})
    
    def __init__(self, iri, langlist):
        self.iri = iri
        self.langlist = langlist
        self.values = []
        self.iri_from_str = {}
        self.str_from_iri = {}
        self.links_from_iri = {}
        
        slabels = [o for o in vocabulary.objects(iri, SKOS.prefLabel)]
        if slabels:
            t = pick_translation(slabels, langlist)
            self.label = str(t)
        else:
            raise UnknownSource(iri)
        
        concepts = [c for c in vocabulary.subjects(SKOS.inScheme, iri)] 

        if concepts:
            for c in concepts:
                clabels = [o for o in vocabulary.objects(c, SKOS.prefLabel)]
                if clabels:
                    t = pick_translation(clabels, langlist)
                    self.values.append(str(t))
                    self.iri_from_str.update({str(t): c})
                    self.str_from_iri.update({c: str(t)})
                    page = vocabulary.value(c, FOAF.page)
                    self.links_from_iri.update({c: page or c})

            if self.values:
                setlocale(LC_COLLATE, "")
                self.values.sort(
                    key=lambda x: strxfrm(x)
                    )
        self.values.insert(0, '')       
        Thesaurus.add(iri, langlist, self)
    

