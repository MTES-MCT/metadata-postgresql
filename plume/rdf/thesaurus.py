"""Répertoire des thésaurus.

"""

from pathlib import Path
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

vocabulary = graph_from_file(Path('data') / 'vocabulary.ttl')
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
        La liste des valeurs du thésaurus.
    iri_from_str : dict
        Dictionnaire dont les clés sont les valeurs du thésaurus
        (str) et les valeurs les IRI correspondants.
    str_from_iri : dict
        Dictionnaire dont les clés sont les IRI des valeurs du thésaurus
        et les valeurs leurs libellés (str).
    links_from_iri : dict
        Dictionnaire dont les clés sont les IRI des valeurs du thésaurus
        et les valeurs les liens associés.
    
    Methods
    -------
    values(thesaurus)
        *Méthode de classe.* Renvoie la liste des valeurs du thésaurus.
    label(thesaurus)
        *Méthode de classe.* Renvoie le libellé du thésaurus.
    concept_iri(thesaurus, concept_str)
        *Méthode de classe.* Renvoie l'IRI correspondant à un libellé
        de thésaurus.
    concept_str(thesaurus, concept_iri)
        *Méthode de classe.* Renvoie le libellé d'un concept de thésaurus.
    concept_link(thesaurus, concept_iri)
        *Méthode de classe.* Renvoie le lien d'un concept de thésaurus.
    
    """
    
    collection = {}
    """Accès à l'ensemble des thésaurus déjà compilés.
    
    `collection` est un dictionnaire dont les clés sont des tuples
    (`iri`, `language`) et les valeurs l'objet `Thesaurus` lui-même.
    
    """
    
    @classmethod
    def values(cls, thesaurus):
        """Cherche ou génère un thésaurus et renvoie la liste de ses valeurs.
        
        Autant que possible, cette méthode va chercher les valeurs dans le
        répertoire des thésaurus déjà compilés (`Thesaurus.collection`), à
        défaut le thésaurus est compilé à partir de `vocabulary`.
        
        Parameters
        ----------
        thesaurus : tuple of URIRef and str
            Source. Tuple dont le premier élément est l'IRI de la source,
            le second la langue pour laquelle le thésaurus doit être généré.
        
        Returns
        -------
        list
            La liste des valeurs du thésaurus. La première valeur de la liste
            est toujours une chaîne de caractères vides.
        
        Raises
        ------
        UnknownParameterValue
            Si le thésaurus non seulement n'avait pas déjà été compilé,
            mais n'existe même pas dans `vocabulary`.
        
        Examples
        --------
        >>> Thesaurus.values(
        ...     (URIRef('http://snum.scenari-community.org/Metadata/Vocabulaire/#CrpaAuthorizedLicense'), 'fr')
        ...     )
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
        
        Autant que possible, cette méthode va chercher les valeurs dans le
        répertoire des thésaurus déjà compilés (`Thesaurus.collection`), à
        défaut le thésaurus est compilé à partir de `vocabulary`.
        
        Parameters
        ----------
        thesaurus : tuple of URIRef and str
            Source. Tuple dont le premier élément est l'IRI de la source,
            le second la langue pour laquelle le thésaurus doit être généré.
        
        Returns
        -------
        list
            La liste des valeurs du thésaurus.
        
        Raises
        ------
        UnknownParameterValue
            Si le thésaurus non seulement n'avait pas déjà été compilé,
            mais n'existe même pas dans `vocabulary`.
        
        Examples
        --------
        >>> Thesaurus.label(
        ...     (URIRef('http://snum.scenari-community.org/Metadata/Vocabulaire/#CrpaAccessLimitations'), 'fr')
        ...     )
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
        répertoire des thésaurus déjà compilés (`Thesaurus.collection`), à
        défaut le thésaurus est compilé à partir de `vocabulary`.
        
        Parameters
        ----------
        thesaurus : tuple of URIRef and str
            Source. Tuple dont le premier élément est l'IRI de la source,
            le second la langue pour laquelle le thésaurus doit être généré.
        concept_str : str
            Une valeur présumée issue du thésaurus, dont on cherche l'IRI.
        
        Returns
        -------
        URIRef
            L'IRI du concept. Peut être None, si le thésaurus existe mais que
            la chaîne de caractères n'y est pas répertoriée.
        
        Raises
        ------
        UnknownParameterValue
            Si le thésaurus non seulement n'avait pas déjà été compilé,
            mais n'existe même pas dans `vocabulary`.
        
        Examples
        --------
        >>> Thesaurus.concept_iri(
        ...     (URIRef('http://snum.scenari-community.org/Metadata/Vocabulaire/#CrpaAccessLimitations'), 'fr'), 
        ...     'Communicable au seul intéressé - atteinte à la protection de la vie privée (CRPA, L311-6 1°)'
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
        
        Autant que possible, cette méthode va chercher l'IRI dans le
        répertoire des thésaurus déjà compilés (`Thesaurus.collection`), à
        défaut le thésaurus est compilé à partir de `vocabulary`.
        
        Parameters
        ----------
        thesaurus : tuple of URIRef and str
            Source. Tuple dont le premier élément est l'IRI de la source,
            le second la langue pour laquelle le thésaurus doit être généré.
        concept_iri : URIRef
            Un IRI présumé issu du thésaurus, dont on cherche le libellé.
        
        Returns
        -------
        str
            Le libellé du concept. Peut être None, si le thésaurus existe mais
            que l'IRI n'y est pas répertorié.
        
        Raises
        ------
        UnknownParameterValue
            Si le thésaurus non seulement n'avait pas déjà été compilé,
            mais n'existe même pas dans `vocabulary`.
        
        Examples
        --------
        >>> Thesaurus.concept_str(
        ...     (URIRef('http://snum.scenari-community.org/Metadata/Vocabulaire/#CrpaAccessLimitations'), 'fr'), 
        ...     URIRef('http://snum.scenari-community.org/Metadata/Vocabulaire/#CrpaAccessLimitations-311-6-1-vp')
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
        
        Autant que possible, cette méthode va chercher l'IRI dans le
        répertoire des thésaurus déjà compilés (`Thesaurus.collection`), à
        défaut le thésaurus est compilé à partir de `vocabulary`.
        
        Parameters
        ----------
        thesaurus : tuple of URIRef and str
            Source. Tuple dont le premier élément est l'IRI de la source,
            le second la langue pour laquelle le thésaurus doit être généré.
        concept_iri : URIRef
            Un IRI présumé issu du thésaurus, dont on cherche le lien.
        
        Returns
        -------
        URIRef
            Le lien associé au concept. Peut être None, si le thésaurus existe
            mais que l'IRI n'y est pas répertorié.
        
        Raises
        ------
        UnknownParameterValue
            Si le thésaurus non seulement n'avait pas déjà été compilé,
            mais n'existe même pas dans `vocabulary`.
        
        Examples
        --------
        >>> Thesaurus.concept_link(
        ...     (URIRef('http://snum.scenari-community.org/Metadata/Vocabulaire/#CrpaAccessLimitations'), 'fr'), 
        ...     URIRef('http://snum.scenari-community.org/Metadata/Vocabulaire/#CrpaAccessLimitations-311-6-1-vp')
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
        
        slabels = [ o for o in vocabulary.objects(iri,
            URIRef("http://www.w3.org/2004/02/skos/core#prefLabel")) ]
        if slabels:
            t = pick_translation(slabels, language)
            self.label = str(t)
        else:
            raise UnknownParameterValue('iri', iri)
        
        concepts = [ c for c in vocabulary.subjects(
            URIRef("http://www.w3.org/2004/02/skos/core#inScheme"), iri) ] 

        if concepts:
            for c in concepts:
                clabels = [ o for o in vocabulary.objects(c,
                    URIRef("http://www.w3.org/2004/02/skos/core#prefLabel")) ]
                if clabels:
                    t = pick_translation(clabels, language)
                    self.values.append(str(t))
                    self.iri_from_str.update({str(t): c})
                    self.str_from_iri.update({c: str(t)})
                    page = vocabulary.value(c, URIRef("http://xmlns.com/foaf/0.1/page"))
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
    litlist : list of Literal
        Une liste de Literal, présumés de type xsd:string.
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

