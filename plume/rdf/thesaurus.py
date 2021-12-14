"""Répertoire des thésaurus.

"""


from locale import strxfrm, setlocale, LC_COLLATE

try:
    from rdflib import Graph, URIRef
except:
    from plume.bibli_install.bibli_install import manageLibrary
    # installe RDFLib si n'est pas déjà disponible
    manageLibrary()
    from rdflib import Graph, URIRef

from plume.rdf.metagraph import graph_from_file
from plume.rdf.exceptions import UnknownParameterValue
from plume.rdf.namespaces import FOAF, SKOS, SNUM
from plume.rdf.utils import abspath

vocabulary = graph_from_file(abspath('rdf/data/vocabulary.ttl'))
"""Graphe contenant le vocabulaire de tous les thésaurus.

"""
  
class Thesaurus:
    """Thésaurus.
    
    Tout nouveau thésaurus généré est mémorisé pour gagner en temps
    de calcul.
    
    Parameters
    ----------
    iri : URIRef
        L'IRI du thésaurus.
    language : str
        La langue pour laquelle le thésaurus doit être généré.
    
    Attributes
    ----------
    collection : dict
        Attribut de classe. Répertoire de tous les thésaurus déjà
        compilés.
    label : str
        Le libellé du thésaurus.
    iri : URIRef
        L'IRI du thésaurus.
    language : str
        La langue pour laquelle le thésaurus a été généré.
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
    
    Methods
    -------
    values(thesaurus)
        *Méthode de classe.* Renvoie la liste des termes du thésaurus.
    label(thesaurus)
        *Méthode de classe.* Renvoie le libellé du thésaurus.
    concept_iri(thesaurus, concept_str)
        *Méthode de classe.* Renvoie l'IRI correspondant au libellé
        d'un terme de thésaurus.
    concept_str(thesaurus, concept_iri)
        *Méthode de classe.* Renvoie le libellé correspondant à l'IRI
        d'un terme de thésaurus.
    concept_link(thesaurus, concept_iri)
        *Méthode de classe.* Renvoie le lien d'un terme de thésaurus.
    concept_source(concept_iri)
        *Méthode de classe.* Renvoie l'IRI du thésaurus auquel
        appartient le terme.
    
    """
    
    collection = {}
    """Accès à l'ensemble des thésaurus déjà compilés.
    
    `collection` est un dictionnaire dont les clés sont des tuples
    (`iri`, `language`) et les valeurs l'objet :py:class:`Thesaurus`
    lui-même.
    
    """
    
    @classmethod
    def values(cls, thesaurus):
        """Cherche ou génère un thésaurus et renvoie la liste de ses termes.
        
        Autant que possible, cette méthode va chercher les termes dans le
        répertoire des thésaurus déjà compilés (:py:attr:`Thesaurus.collection`),
        à défaut le thésaurus est compilé à partir de :py:data:`vocabulary`.
        
        Parameters
        ----------
        thesaurus : tuple(URIRef, str)
            Source. Tuple dont le premier élément est l'IRI de la source,
            le second la langue pour laquelle le thésaurus doit être généré.
        
        Returns
        -------
        list
            La liste des termes du thésaurus. La première valeur de la liste
            est toujours une chaîne de caractères vides.
        
        Raises
        ------
        UnknownParameterValue
            Si le thésaurus non seulement n'avait pas déjà été compilé,
            mais n'existe même pas dans :py:data:`vocabulary`.
        
        Examples
        --------
        >>> Thesaurus.values((SNUM.CrpaAuthorizedLicense, 'fr'))
        ['', 'Licence Ouverte version 2.0', 'ODC Open Database License (ODbL) version 1.0']
        
        """
        iri, language = thesaurus
        if thesaurus in cls.collection:
            return cls.collection[thesaurus].values
        t = Thesaurus(iri, language)
        if t:
            return t.values
        raise UnknownParameterValue('iri', iri)
    
    @classmethod
    def label(cls, thesaurus):
        """Cherche ou génère un thésaurus et renvoie son libellé.
        
        Autant que possible, cette méthode va chercher le libellé dans le
        répertoire des thésaurus déjà compilés (:py:attr:`Thesaurus.collection`),
        à défaut le thésaurus est compilé à partir de :py:data:`vocabulary`.
        
        Parameters
        ----------
        thesaurus : tuple(URIRef, str)
            Source. Tuple dont le premier élément est l'IRI de la source,
            le second la langue pour laquelle le thésaurus doit être généré.
        
        Returns
        -------
        str
            Le libellé du thésaurus.
        
        Raises
        ------
        UnknownParameterValue
            Si le thésaurus non seulement n'avait pas déjà été compilé,
            mais n'existe même pas dans :py:data:`vocabulary`.
        
        Examples
        --------
        >>> Thesaurus.label((SNUM.CrpaAccessLimitations, 'fr'))
        "Restrictions d'accès en application du Code des relations entre le public et l'administration"
        
        """
        iri, language = thesaurus
        if thesaurus in cls.collection:
            return cls.collection[thesaurus].label
        t = Thesaurus(iri, language)
        if t:
            return t.label
        raise UnknownParameterValue('iri', iri)
    
    @classmethod
    def concept_iri(cls, thesaurus, concept_str):
        """Cherche ou génère un thésaurus et renvoie l'IRI d'un concept.
        
        Autant que possible, cette méthode va chercher l'IRI dans le
        répertoire des thésaurus déjà compilés (:py:attr:`Thesaurus.collection`),
        à défaut le thésaurus est compilé à partir de :py:data:`vocabulary`.
        
        Parameters
        ----------
        thesaurus : tuple(URIRef, str)
            Source. Tuple dont le premier élément est l'IRI de la source,
            le second la langue pour laquelle le thésaurus doit être généré.
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
        UnknownParameterValue
            Si le thésaurus non seulement n'avait pas déjà été compilé,
            mais n'existe même pas dans :py:data:`vocabulary`.
        
        Examples
        --------
        >>> Thesaurus.concept_iri(
        ...     (SNUM.CrpaAccessLimitations, 'fr'), 
        ...     'Communicable au seul intéressé - atteinte à la' \
        ...         ' protection de la vie privée (CRPA, L311-6 1°)'
        ...     )
        rdflib.term.URIRef('http://snum.scenari-community.org/Metadata/Vocabulaire/#CrpaAccessLimitations-311-6-1-vp')
        
        """
        iri, language = thesaurus
        if thesaurus in cls.collection:
            return cls.collection[thesaurus].iri_from_str.get(concept_str)
        t = Thesaurus(iri, language)
        if t:
            return t.iri_from_str.get(concept_str)
        raise UnknownParameterValue('iri', iri)
    
    @classmethod
    def concept_str(cls, thesaurus, concept_iri):
        """Cherche ou génère un thésaurus et renvoie le libellé d'un concept.
        
        Autant que possible, cette méthode va chercher le libellé dans le
        répertoire des thésaurus déjà compilés (:py:attr:`Thesaurus.collection`),
        à défaut le thésaurus est compilé à partir de :py:data:`vocabulary`.
        
        Parameters
        ----------
        thesaurus : tuple(URIRef, str)
            Source. Tuple dont le premier élément est l'IRI de la source,
            le second la langue pour laquelle le thésaurus doit être généré.
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
        UnknownParameterValue
            Si le thésaurus non seulement n'avait pas déjà été compilé,
            mais n'existe même pas dans :py:data:`vocabulary`.
        
        Examples
        --------
        >>> Thesaurus.concept_str(
        ...     (SNUM.CrpaAccessLimitations, 'fr'), 
        ...     SNUM['CrpaAccessLimitations-311-6-1-vp']
        ...     )
        'Communicable au seul intéressé - atteinte à la protection de la vie privée (CRPA, L311-6 1°)'
        
        """
        iri, language = thesaurus
        if thesaurus in cls.collection:
            return cls.collection[thesaurus].str_from_iri.get(concept_iri)
        t = Thesaurus(iri, language)
        if t:
            return t.str_from_iri.get(concept_iri)
        raise UnknownParameterValue('iri', iri)
    
    @classmethod
    def concept_link(cls, thesaurus, concept_iri):
        """Cherche ou génère un thésaurus et renvoie le lien d'un concept.
        
        Autant que possible, cette méthode va chercher le lien dans le
        répertoire des thésaurus déjà compilés (:py:attr:`Thesaurus.collection`),
        à défaut le thésaurus est compilé à partir de :py:data:`vocabulary`.
        
        Parameters
        ----------
        thesaurus : tuple(URIRef, str)
            Source. Tuple dont le premier élément est l'IRI de la source,
            le second la langue pour laquelle le thésaurus doit être généré.
        concept_iri : URIRef
            L'IRI d'un terme présumé issu du thésaurus, dont on cherche le lien.
        
        Returns
        -------
        URIRef
            Le lien associé au concept. Peut être ``None``, si le thésaurus
            existe mais que l'IRI n'y est pas répertorié.
        
        Raises
        ------
        UnknownParameterValue
            Si le thésaurus non seulement n'avait pas déjà été compilé,
            mais n'existe même pas dans :py:data:`vocabulary`.
        
        Examples
        --------
        >>> Thesaurus.concept_link(
        ...     (SNUM.CrpaAccessLimitations, 'fr'), 
        ...     SNUM['CrpaAccessLimitations-311-6-1-vp']
        ...     )
        rdflib.term.URIRef('https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000037269056')
        
        """
        iri, language = thesaurus
        if thesaurus in cls.collection:
            return cls.collection[thesaurus].links_from_iri.get(concept_iri)
        t = Thesaurus(iri, language)
        if t:
            return t.links_from_iri.get(concept_iri)
        raise UnknownParameterValue('iri', iri)
    
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
    def add(cls, iri, language, thesaurus):
        """Ajoute un thésaurus au répertoire des thésaurus compilés.
        
        Parameters
        ----------
        iri : URIRef
            L'IRI du thésaurus considéré.
        language : str
            La langue pour laquelle le thésaurus a été généré.
        thesaurus : Thesaurus
            Le thésaurus en tant que tel.
        
        """
        cls.collection.update({(iri, language): thesaurus})
    
    def __init__(self, iri, language):
        self.iri = iri
        self.language = language
        self.values = []
        self.iri_from_str = {}
        self.str_from_iri = {}
        self.links_from_iri = {}
        
        slabels = [o for o in vocabulary.objects(iri, SKOS.prefLabel)]
        if slabels:
            t = pick_translation(slabels, language)
            self.label = str(t)
        else:
            raise UnknownParameterValue('iri', iri)
        
        concepts = [c for c in vocabulary.subjects(SKOS.inScheme, iri)] 

        if concepts:
            for c in concepts:
                clabels = [o for o in vocabulary.objects(c, SKOS.prefLabel)]
                if clabels:
                    t = pick_translation(clabels, language)
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
        Thesaurus.add(iri, language, self)
  

def pick_translation(litlist, language):
    """Renvoie l'élément de la liste correspondant à la langue désirée.
    
    Parameters
    ----------
    litlist : list of rdflib.term.Literal
        Une liste de valeurs litérales, présumées de type
        ``xsd:string``.
    language : str
        La langue pour laquelle on cherche une traduction.
    
    Returns
    -------
    Literal
        Un des éléments de la liste, qui peut être :
        - le premier dont la langue est `language` ;
        - à défaut, le dernier dont la langue est 'fr' ;
        - à défaut, le premier de la liste.

    """
    if not litlist:
        raise ForbiddenOperation('La liste ne contient aucune valeur.')
    
    val = None
    
    for l in litlist:
        if l.language == language:
            val = l
            break
        elif l.language == 'fr':
            # à défaut de mieux, on gardera la traduction
            # française
            val = l
            
    if val is None:
        # s'il n'y a ni la langue demandée ni traduction
        # française, on prend la première valeur de la liste
        val = litlist[0]
        
    return val

