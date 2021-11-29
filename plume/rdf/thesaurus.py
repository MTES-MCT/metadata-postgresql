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
from plume.rdf.widgetsdict import pick_translation

vocabulary = graph_from_file(Path('data') / 'vocabulary.ttl')
"""Graphe contenant le vocabulaire de tous les thésaurus.

"""
  
class Thesaurus:
    """Thésaurus.
    
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
    parser : dict
        Dictionnaire dont les clés sont les valeurs du thésaurus
        et les valeurs les IRI correspondants.
    links : dict
        Dictionnaire dont les clés sont les valeurs du thésaurus
        et les valeurs les liens associés.
    
    """
    
    collection = {}
    """Accès à l'ensemble des thésaurus déjà compilés.
    
    `collection` est un dictionnaire dont les clés sont des tuples
    (`iri`, `language`) et les valeurs l'objet `Thesaurus` lui-même.
    
    """
    
    @classmethod
    def values(cls, value_source):
        """Cherche ou génère un thésaurus et renvoie la liste de ses valeurs.
        
        Autant que possible, cette méthode va chercher les valeurs dans le
        répertoire des thésaurus déjà compilés (`Thesaurus.collection`), à
        défaut le thésaurus est compilé à partir de `vocabulary`.
        
        Parameters
        ----------
        value_source : tuple of URIRef and str
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
        
        """
        iri, language = value_source
        if value_source in cls.collection:
            return cls.collection[value_source].values
        t = Thesaurus(iri, language)
        if t:
            return t.values
        raise UnknownParameterValue('iri', iri)
    
    @classmethod
    def label(cls, value_source):
        """Cherche ou génère un thésaurus et renvoie son libellé.
        
        Autant que possible, cette méthode va chercher les valeurs dans le
        répertoire des thésaurus déjà compilés (`Thesaurus.collection`), à
        défaut le thésaurus est compilé à partir de `vocabulary`.
        
        Parameters
        ----------
        value_source : tuple of URIRef and str
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
            
        """
        iri, language = value_source
        if value_source in cls.collection:
            return cls.collection[value_source].label
        t = Thesaurus(iri, language)
        if t:
            return t.label
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
        """Génère un thésaurus d'après son IRI (et le stocke).
        
        Parameters
        ----------
        iri : URIRef
            L'IRI du thésaurus.
        language : str
            La langue pour laquelle le thésaurus doit être généré.
        
        """
        self.iri = iri
        self.language = language
        self.values = []
        self.parser = {}
        self.links = {}
        
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
                    self.parser.update({str(t): c})
                    page = vocabulary.value(c, URIRef("http://xmlns.com/foaf/0.1/page"))
                    self.links.update({str(t): page or iri})

            if self.values:
                setlocale(LC_COLLATE, "")
                self.values.sort(
                    key=lambda x: strxfrm(x)
                    )
        
        self.values.insert(0, '')       
        Thesaurus.add(iri, language, self)
        

