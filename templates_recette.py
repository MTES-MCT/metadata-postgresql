"""
Contrôle des templates, compilations d'ontologies, etc.
"""


from rdflib import Graph, Namespace, Literal, BNode, URIRef
from rdflib.serializer import Serializer
from locale import strxfrm, setlocale, LC_COLLATE
from rdflib.compare import isomorphic
from json.decoder import JSONDecodeError
from inspect import signature
import re, uuid, unittest
import rdf_utils


class TestTemplatesMethods(unittest.TestCase):
    
    def setUp(self):
        with open('dataset_template.ttl', encoding='UTF-8') as src:
            self.dataset_template = Graph().parse(data=src.read(), format='turtle')
        with open('ontologies.ttl', encoding='UTF-8') as src:
            self.vocabulary = Graph().parse(data=src.read(), format='turtle')

        
    ### ontologies
        
    def test_ontologies_1(self):
        # présence de vocabulaire dans ontologies.ttl pour tous les skos:inScheme
        # associés à des propriétés dans dataset_template.ttl ?
        d = rdf_utils.buildDict(self.dataset_template, self.dataset_template,
                                self.vocabulary)
        self.assertTrue(all(map(
            lambda x: re.search("skos[:]inScheme$", x) is None
                and rdf_utils.fetchVocabulary(x, self.dataset_template,
                                              self.vocabulary) is None
                or re.search("skos[:]inScheme$", x)
                and rdf_utils.fetchVocabulary(re.sub(r"\s[/]\sskos[:]inScheme$", "", x),
                                              self.dataset_template,
                                              self.vocabulary),
            d.keys()
            )))

    ### dataset_template

    def test_dataset_template_1(self):
        # toutes les propriétés ont un type rdf:type ?
        d = rdf_utils.buildDict(self.dataset_template, self.dataset_template,
                                self.vocabulary, keepRDFType=True)
        self.assertTrue(all(map(
            lambda x: re.search("rdf[:]type$", x)
                or re.sub(r"\s[/]\s[^\s]*$", " / rdf:type", x) in d,
            d.keys()
            )))

    def test_dataset_template_2(self):
        # seuls des Literal ont un type sh:datatype ?
        d = rdf_utils.buildDict(self.dataset_template, self.dataset_template,
                                self.vocabulary, keepRDFType=True)
        lit = 'http://www.w3.org/2000/01/rdf-schema#Literal'
        self.assertTrue(all(map(
            lambda x: re.search("sh[:]datatype$", x)
                and d[re.sub(r"\s[/]\s[^\s]*$", " / rdf:type", x)] == [lit]
                or re.search("sh[:]datatype$", x) is None,
            d.keys()
            )))

    def test_dataset_template_3(self):
        # pas de skos:inScheme sur des Literal ?
        d = rdf_utils.buildDict(self.dataset_template, self.dataset_template,
                                self.vocabulary, keepRDFType=True)
        lit = 'http://www.w3.org/2000/01/rdf-schema#Literal'
        self.assertTrue(all(map(
            lambda x: re.search("skos[:]inScheme$", x)
                and not d[re.sub(r"\s[/]\s[^\s]*$", " / rdf:type", x)] == [lit]
                or re.search("skos[:]inScheme$", x) is None,
            d.keys()
            )))
        

unittest.main()
