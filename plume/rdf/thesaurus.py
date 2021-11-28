"""Répertoire des thésaurus.

Ce système ne fonctionne que parce que les libellés des
thésaurus sont uniques indépendemment de la langue.

"""

from plume.rdf.metagraph import metagraph_from_file

try:
    from rdflib import Graph, URIRef
except:
    from plume.bibli_install.bibli_install import manageLibrary
    # installe RDFLib si n'est pas déjà disponible
    manageLibrary()
    from rdflib import Graph, URIRef


vocabulary = metagraph_from_file('vocabulary.ttl')
    """Graphe contenant le vocabulaire de tous les thésaurus.
    
    """

thesaurusCollection = ThesaurusCollection()
    """Accès aux thésaurus déjà compilés.

    """
    
class ThesaurusCollection(dict):
    """Répertoire de thésaurus.
    
    Un répertoire de thésaurus est un dictionnaire dont les clés sont
    les libellés des thésaurus et les valeurs des objets de classe
    `Thesaurus`.
    
    """
    def add(self, label, thesaurus):
        self.update({label: thesaurus})
        
    def get_values(self, label, value, language):
        """
        """
        if label == '< non répertorié >':
            return ['', value] if value else ['']
        if label in self:
            return self[label].values
        return Thesaurus(language, label=label)
    
    
class Thesaurus:
    """Thésaurus.
    
    Attributes
    ----------
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
    def __init__(self, language, label=None, iri=None):
        """Génère un thésaurus d'après son libellé ou son IRI.
        
        Le thésaurus sera automatiquement enregistré dans
        `KnownThesaurusCollection`.
        
        Parameters
        ----------
        language : str
            La langue pour laquelle le thésaurus doit être généré.
        label : str, optional
            Le libellé du thésaurus.
        iri : URIRef, optional
            L'IRI du thésaurus.
        
        `label` ou `iri` doit être renseigné.
        
        """
        self.values = []
        self.parser = {}
        self.links = {}
        
        if not iri:
            for s in vocabulary.subjects(
                URIRef('http://www.w3.org/2004/02/skos/core#prefLabel'),
                label):
                iri = s
                break
            if not iri:
                raise UnknownParameterValue('label', label)
        
        if not label:
            label = vocabulary.value(iri,
                URIRef("http://www.w3.org/2004/02/skos/core#prefLabel"))
            if not label:
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
                    self.links.update({str(t): page})

            if self.values:
                setlocale(LC_COLLATE, "")

                self.values = sorted(
                    self.values,
                    key=lambda x: strxfrm(x)
                    )
                    
        self.values.insert(0, '')       
        thesaurusCollection.add(label, self)
        
