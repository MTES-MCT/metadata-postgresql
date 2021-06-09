"""
Recette des fonctions du module rdf_utils.
"""


from rdflib import Graph, Namespace, Literal, BNode, URIRef
from rdflib.serializer import Serializer
from locale import strxfrm, setlocale, LC_COLLATE
from rdflib.compare import isomorphic
from json.decoder import JSONDecodeError
from inspect import signature
import re, uuid, unittest
import rdf_utils


class TestRDFUtilsMethods(unittest.TestCase):
    
    def setUp(self):
        with open('dataset_template.ttl', encoding='UTF-8') as src:
            self.dataset_template = Graph().parse(data=src.read(), format='turtle')
        with open('ontologies.ttl', encoding='UTF-8') as src:
            self.vocabulary = Graph().parse(data=src.read(), format='turtle')

        
    ### buildNSDict
        
    def test_buildNSDict_1(self):
        self.assertTrue("dcat" in rdf_utils.buildNSDict(self.dataset_template).keys())

    def test_buildNSDict_2(self):
        self.assertEqual(len(rdf_utils.buildNSDict(Graph())), 4)
        # par défaut, les préfixes xml, rdf, rdfs et xsd sont définis


    ### fetchUUID
        
    def test_fetchUUID_1(self):
        self.assertEqual(rdf_utils.fetchUUID(self.dataset_template),
                         URIRef('urn:uuid:5c78c95d-d9ff-4f95-8e15-dd14cbc6cced'))

    def test_fetchUUID_2(self):
        self.assertEqual(rdf_utils.fetchUUID(Graph()), None)

        
    ### testPath
        
    def test_testPath_1(self):
        self.assertFalse(rdf_utils.testPath(Graph(), "dct:title"))

    def test_testPath_2(self):
        self.assertTrue(rdf_utils.testPath(Graph(), ""))

    def test_testPath_3(self):
        self.assertTrue(rdf_utils.testPath(self.dataset_template, ""))

    def test_testPath_4(self):
        self.assertTrue(rdf_utils.testPath(self.dataset_template, "dct:title"))

    def test_testPath_5(self):
        self.assertTrue(rdf_utils.testPath(self.dataset_template,
                                           "dcat:distribution / dct:licence / rdfs:label"))


    ### fetchValue

    # peu de tests ici, mais la fonction est utilisée
    # dans la suite de la recette sur des tests plus
    # complexes, qui permettront de valider son
    # commportement dans des contextes moins triviaux

    def test_fetchValue_1(self):
        self.assertEqual(rdf_utils.fetchValue(Graph(), "dct:title"), None)

    def test_fetchValue_2(self):
        self.assertEqual(rdf_utils.fetchValue(Graph(), ""), None)

    def test_fetchValue_3(self):
        self.assertEqual(rdf_utils.fetchValue(self.dataset_template, ""), None)

    def test_fetchValue_4(self):
        l = rdf_utils.fetchValue(self.dataset_template, "dcat:theme / skos:inScheme")
        self.assertTrue(
            len(l) == 1
            and l[0] == URIRef("http://publications.europa.eu/resource/authority/data-theme")
            )

    def test_fetchValue_3(self):
        self.assertEqual(rdf_utils.fetchValue(self.dataset_template, "N'importe quoi !!"), None)
        
    

    ### fetchType
        
    def test_fetchType_1(self):
        self.assertEqual(rdf_utils.fetchType("dct:title", Graph()), None)

    def test_fetchType_2(self):
        self.assertEqual(rdf_utils.fetchType("", Graph()), None)

    def test_fetchType_3(self):
        self.assertEqual(rdf_utils.fetchType("", self.dataset_template), None)

    def test_fetchType_4(self):
        self.assertEqual(rdf_utils.fetchType("dct:title / bla:bla",
                                             self.dataset_template), None)

    def test_fetchType_5(self):
        self.assertEqual(rdf_utils.fetchType("n'importe quoi !!!",
                                             self.dataset_template), None)
        
    def test_fetchType_6(self):
        self.assertEqual(rdf_utils.fetchType("dcat:distribution / dct:licence",
                                             self.dataset_template),
                         URIRef('http://purl.org/dc/terms/LicenseDocument'))

    def test_fetchType_7(self):
        self.assertEqual(rdf_utils.fetchType("dct:title",
                                             self.dataset_template),
                         URIRef("http://www.w3.org/2000/01/rdf-schema#Literal"))
        

    ### fetchDataType
        
    def test_fetchDataType_1(self):
        self.assertEqual(rdf_utils.fetchDataType("dct:title", Graph()), None)

    def test_fetchDataType_2(self):
        self.assertEqual(rdf_utils.fetchDataType("", Graph()), None)

    def test_fetchDataType_3(self):
        self.assertEqual(rdf_utils.fetchDataType("", self.dataset_template), None)

    def test_fetchDataType_4(self):
        self.assertEqual(rdf_utils.fetchDataType("dct:title / bla:bla",
                                             self.dataset_template), None)

    def test_fetchDataType_5(self):
        self.assertEqual(rdf_utils.fetchDataType("n'importe quoi !!!",
                                             self.dataset_template), None)
        
    def test_fetchDataType_6(self):
        self.assertEqual(rdf_utils.fetchDataType("dcat:distribution / dct:licence",
                                             self.dataset_template), None)

    def test_fetchDataType_7(self):
        self.assertEqual(rdf_utils.fetchDataType("dct:title",
                                             self.dataset_template), None)
        # la fonction ne renvoie rien pour les Literal xsd:string

    def test_fetchDataType_8(self):
        self.assertEqual(rdf_utils.fetchDataType("dct:modified",
                                             self.dataset_template),
                         URIRef('http://www.w3.org/2001/XMLSchema#dateTime'))

    def test_fetchDataType_9(self):
        self.assertEqual(rdf_utils.fetchDataType("dct:spatial / dcat:centroid",
                                             self.dataset_template),
                         URIRef('http://www.opengis.net/ont/geosparql#wktLiteral'))


    ### fetchVocabulary

    def test_fetchVocabulary_1(self):
        self.assertEqual(rdf_utils.fetchVocabulary("dcat:theme", Graph(), self.vocabulary),
                         None)

    def test_fetchVocabulary_2(self):
        self.assertEqual(rdf_utils.fetchVocabulary("dcat:theme", self.dataset_template, Graph()),
                         None)

    def test_fetchVocabulary_3(self):
        self.assertEqual(rdf_utils.fetchVocabulary("", self.dataset_template,
                                                 self.vocabulary),
                         None)

    def test_fetchVocabulary_4(self):
        self.assertEqual(rdf_utils.fetchVocabulary("dcat:theme", self.dataset_template,
                                                 self.vocabulary),
                         ['Agriculture, pêche, sylviculture et alimentation',
                          'Données provisoires', 'Économie et finances',
                          'Éducation, culture et sport', 'Énergie', 'Environnement',
                          'Gouvernement et secteur public',
                          'Justice, système juridique et sécurité publique',
                          'Population et société', 'Questions internationales',
                          'Régions et villes', 'Santé', 'Science et technologie',
                          'Transports'])

    def test_fetchVocabulary_5(self):
        self.assertEqual(rdf_utils.fetchVocabulary("dct:spatial / dcat:centroid",
                                                 self.dataset_template,
                                                 self.vocabulary),
                         None)

    # il manquerait un test vérifiant que rien n'est renvoyé pour une
    # propriété avec un skos:inScheme identifié mais sans vocabulaire
    # associé. Toutefois il n'y en a plus dans le modèle à cette date.


    ### fetchConceptFromValue

    def test_fetchConceptFromValue_1(self):
        self.assertEqual(rdf_utils.fetchConceptFromValue("dcat:theme", "Transports",
                                                   Graph(), self.vocabulary),
                         (False,))

    def test_fetchConceptFromValue_2(self):
        self.assertEqual(rdf_utils.fetchConceptFromValue("dcat:theme", "Transports",
                                                   self.dataset_template, Graph()),
                         (True,))

    def test_fetchConceptFromValue_3(self):
        self.assertEqual(rdf_utils.fetchConceptFromValue("", "Transports",
                                                   self.dataset_template, self.vocabulary),
                         (False,))

    def test_fetchConceptFromValue_4(self):
        self.assertEqual(rdf_utils.fetchConceptFromValue("dcat:theme", "",
                                                   self.dataset_template, self.vocabulary),
                         (False,))

    def test_fetchConceptFromValue_5(self):
        self.assertEqual(rdf_utils.fetchConceptFromValue("dcat:theme", "Transports",
                                                   self.dataset_template, self.vocabulary),
                         (True, URIRef('http://publications.europa.eu/resource/authority/data-theme/TRAN')))

    def test_fetchConceptFromValue_6(self):
        self.assertEqual(rdf_utils.fetchConceptFromValue("dcat:theme", Literal("Transports", lang="en"),
                                                   self.dataset_template, self.vocabulary),
                         (True, URIRef('http://publications.europa.eu/resource/authority/data-theme/TRAN')))

    def test_fetchConceptFromValue_7(self):
        self.assertEqual(rdf_utils.fetchConceptFromValue("dcat:theme", "Littérature",
                                                   self.dataset_template, self.vocabulary),
                         (True,))

    def test_fetchConceptFromValue_8(self):
        self.assertEqual(rdf_utils.fetchConceptFromValue("dct:language", "FRA",
                                                   self.dataset_template, self.vocabulary),
                         (True,))

    def test_fetchConceptFromValue_9(self):
        self.assertEqual(rdf_utils.fetchConceptFromValue("dct:title", "Mon titre",
                                                   self.dataset_template, self.vocabulary),
                         (False,))


    ### fetchValueFromConcept

    def test_fetchValueFromConcept_1(self):
        self.assertEqual(rdf_utils.fetchValueFromConcept("dcat:theme",
                                                   "http://publications.europa.eu/resource/authority/data-theme/TRAN",
                                                   Graph(), self.vocabulary),
                         None)

    def test_fetchValueFromConcept_2(self):
        self.assertEqual(rdf_utils.fetchValueFromConcept("dcat:theme",
                                                   "http://publications.europa.eu/resource/authority/data-theme/TRAN",
                                                   self.dataset_template, Graph()),
                         None)

    def test_fetchValueFromConcept_3(self):
        self.assertEqual(rdf_utils.fetchValueFromConcept("",
                                                   "http://publications.europa.eu/resource/authority/data-theme/TRAN",
                                                   self.dataset_template, self.vocabulary),
                         None)

    def test_fetchValueFromConcept_4(self):
        self.assertEqual(rdf_utils.fetchValueFromConcept("dcat:theme", "",
                                                   self.dataset_template, self.vocabulary),
                         None)

    def test_fetchValueFromConcept_5(self):
        self.assertEqual(rdf_utils.fetchValueFromConcept("dcat:theme",
                                                   "http://publications.europa.eu/resource/authority/data-theme/TRAN",
                                                   self.dataset_template, self.vocabulary),
                         Literal("Transports", lang="fr"))

    def test_fetchValueFromConcept_6(self):
        self.assertEqual(rdf_utils.fetchValueFromConcept("dcat:theme",
                                                   URIRef("http://publications.europa.eu/resource/authority/data-theme/TRAN"),
                                                   self.dataset_template, self.vocabulary),
                         Literal("Transports", lang="fr"))

    def test_fetchValueFromConcept_7(self):
        self.assertEqual(rdf_utils.fetchValueFromConcept("dcat:theme", "Littérature & Cinéma",
                                                   self.dataset_template, self.vocabulary),
                         None)

    def test_fetchValueFromConcept_8(self):
        self.assertEqual(rdf_utils.fetchValueFromConcept("dct:language", "FRA",
                                                   self.dataset_template, self.vocabulary),
                         None)

    def test_fetchValueFromConcept_9(self):
        self.assertEqual(rdf_utils.fetchValueFromConcept("dct:modified", "2021-02-04",
                                                   self.dataset_template, self.vocabulary),
                         None)

    ### emailFromOwlThing

    def test_emailFromOwlThing_1(self):
        self.assertEqual(rdf_utils.emailFromOwlThing(URIRef("mailto:jon.snow@the-wall.we")),
                         'jon.snow@the-wall.we')

    def test_emailFromOwlThing_2(self):
        self.assertEqual(rdf_utils.emailFromOwlThing(URIRef("jon.snow@the-wall.we")),
                         'jon.snow@the-wall.we')


    ### owlThingFromEmail

    def test_owlThingFromEmail_1(self):
        self.assertEqual(rdf_utils.owlThingFromEmail("jon.snow@the-wall.we"),
                         URIRef("mailto:jon.snow@the-wall.we"))

    def test_owlThingFromEmail_2(self):
        self.assertEqual(rdf_utils.owlThingFromEmail("mailto:jon.snow@the-wall.we"),
                         URIRef("mailto:jon.snow@the-wall.we"))

    def test_owlThingFromEmail_3(self):
        self.assertRaisesRegex(ValueError, r"Invalid.IRI.*[']\s[']",
                                rdf_utils.owlThingFromEmail, "xxxx xxxxxxxx")

    def test_owlThingFromEmail_4(self):
        self.assertRaisesRegex(ValueError, r"Invalid.IRI.*['][{][']",
                                rdf_utils.owlThingFromEmail, "xxxx{xxxxxxxx")

    def test_owlThingFromEmail_5(self):
        self.assertEqual(rdf_utils.owlThingFromEmail(""), None)

    def test_owlThingFromEmail_6(self):
        self.assertEqual(rdf_utils.owlThingFromEmail("mailto:"), None)
        

    ### telFromOwlThing

    def test_telFromOwlThing_1(self):
        self.assertEqual(rdf_utils.telFromOwlThing(URIRef("tel:+33-1-23-45-67-89")),
                         '+33-1-23-45-67-89')

    def test_telFromOwlThing_2(self):
        self.assertEqual(rdf_utils.telFromOwlThing(URIRef("+33-1-23-45-67-89")),
                         '+33-1-23-45-67-89')

    def test_telFromOwlThing_3(self):
        self.assertEqual(rdf_utils.telFromOwlThing(URIRef("tel:xxxxxxxxxxxx")),
                         'xxxxxxxxxxxx')

    def test_telFromOwlThing_4(self):
        self.assertEqual(rdf_utils.telFromOwlThing(URIRef("xxxxxxxxxxxx")),
                         'xxxxxxxxxxxx')


    ### owlThingFromTel

    def test_owlThingFromTel_1(self):
        self.assertEqual(rdf_utils.owlThingFromTel("xxxxxxxxxxxx"),
                         URIRef("tel:xxxxxxxxxxxx"))

    def test_owlThingFromTel_2(self):
        self.assertEqual(rdf_utils.owlThingFromTel("0123456789"),
                         URIRef("tel:+33-1-23-45-67-89"))

    def test_owlThingFromTel_3(self):
        self.assertEqual(rdf_utils.owlThingFromTel("0123456789", False),
                         URIRef("tel:0123456789"))

    def test_owlThingFromTel_4(self):
        self.assertEqual(rdf_utils.owlThingFromTel(" 01 23.45-67 89 "),
                         URIRef("tel:+33-1-23-45-67-89"))

    def test_owlThingFromTel_5(self):
        self.assertEqual(rdf_utils.owlThingFromTel(" 01 23.45-67 89 ", False),
                         URIRef("tel:01-23.45-67-89"))

    def test_owlThingFromTel_6(self):
        self.assertRaisesRegex(ValueError, r"Invalid.IRI.*[']\s[']",
                                rdf_utils.owlThingFromTel, "xxxx xxxxxxxx")

    def test_owlThingFromTel_7(self):
        self.assertRaisesRegex(ValueError, r"Invalid.IRI.*['][{][']",
                                rdf_utils.owlThingFromTel, "xxxx{xxxxxxxx")

    def test_owlThingFromTel_8(self):
        self.assertEqual(rdf_utils.owlThingFromTel(""), None)

    def test_owlThingFromTel_9(self):
        self.assertEqual(rdf_utils.owlThingFromTel("tel:"), None)

    def test_owlThingFromTel_10(self):
        self.assertEqual(rdf_utils.owlThingFromTel("tel:0123456789"),
                         URIRef("tel:+33-1-23-45-67-89"))


    ### buildGraph
        
    # pas de tests avec un modèle problématique ou sans graphe de vocabulaire, car la fonction
    # ne devrait jamais être utilisée dans ce contexte (et les erreurs qui en résulteraient
    # n'ont pas vocation à être gérées).

    def test_buildGraph_1(self):
        self.assertEqual(len(rdf_utils.buildGraph(dict(), self.dataset_template, self.vocabulary)), 1)

    def test_buildGraph_2(self):
        g = rdf_utils.buildGraph(dict(), self.dataset_template, self.vocabulary)
        q = g.query("SELECT ?s ?p ?v WHERE { ?s ?p ?v }")
        for r in q:
            a, b, c = r.s, r.p, r.v
        self.assertTrue(
            len(q) == 1
            and re.match('urn[:]uuid[:]', str(a))
            and b == URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
            and c == URIRef("http://www.w3.org/ns/dcat#Dataset")
            )

    def test_buildGraph_3(self):
        d = {
            'dct:description': ["Délimitation simplifiée des départements de France métropolitaine pour représentation à petite échelle, conforme au code officiel géographique (COG) de l'INSEE au 1er janvier de l'année de référence."],
            'dct:provenance / rdfs:label': ["Donnée référentielle produite par l'IGN."],
            'dct:publisher / foaf:name': ["Institut national de l'information géographique et forestière (IGN-F)"],
            'dct:created': ['2020-08-03'],
            'dcat:keyword': ['donnée externe'],
            'dct:modified': ['2021-02-04'],
            'dcat:distribution / dct:accessURL': ['https://geoservices.ign.fr/documentation/diffusion/telechargement-donnees-libres.html#admin-express'],
            'dcat:distribution / dct:issued': ['2021-01-19'],
            'dcat:distribution / dct:licence / rdfs:label': ['Base de données soumise aux conditions de la licence ouverte Etalab.'],
            'dct:accessRights / rdfs:label': ["Aucune restriction d'accès ou d'usage."],
            'dct:title': ['ADMIN EXPRESS - Départements de métropole'],
            'dct:temporal / dcat:startDate': ['2021-01-15'],
            'dct:temporal / dcat:endDate': ['2021-01-15'],
            'dcat:landingPage': ['https://geoservices.ign.fr/ressources_documentaires/Espace_documentaire/BASES_VECTORIELLES/ADMIN_EXPRESS/IGNF_ADMIN_EXPRESS_2-4.html']
            }
        g = rdf_utils.buildGraph(d, self.dataset_template, self.vocabulary)
        self.assertTrue(all(map(lambda x: rdf_utils.testPath(g, x), d.keys())))
        # on vérifie que tous les chemins (clés) du dictionnaire sont bien présents dans le graphe

    def test_buildGraph_4(self):
        d = {
            'dct:description': ["Délimitation simplifiée des départements de France métropolitaine pour représentation à petite échelle, conforme au code officiel géographique (COG) de l'INSEE au 1er janvier de l'année de référence."],
            'dct:provenance / rdfs:label': ["Donnée référentielle produite par l'IGN."],
            'dct:publisher / foaf:name': ["Institut national de l'information géographique et forestière (IGN-F)"],
            'dct:created': ['2020-08-03'],
            'dcat:keyword': ['donnée externe'],
            'dct:modified': ['2021-02-04'],
            'dcat:distribution / dct:accessURL': ['https://geoservices.ign.fr/documentation/diffusion/telechargement-donnees-libres.html#admin-express'],
            'dcat:distribution / dct:issued': ['2021-01-19'],
            'dcat:distribution / dct:licence / rdfs:label': ['Base de données soumise aux conditions de la licence ouverte Etalab.'],
            'dct:accessRights / rdfs:label': ["Aucune restriction d'accès ou d'usage."],
            'dct:title': ['ADMIN EXPRESS - Départements de métropole'],
            'dct:temporal / dcat:startDate': ['2021-01-15'],
            'dct:temporal / dcat:endDate': ['2021-01-15'],
            'dcat:landingPage': ['https://geoservices.ign.fr/ressources_documentaires/Espace_documentaire/BASES_VECTORIELLES/ADMIN_EXPRESS/IGNF_ADMIN_EXPRESS_2-4.html']
            }
        g = rdf_utils.buildGraph(d, self.dataset_template, self.vocabulary)
        
        self.assertTrue(
            all(map(lambda x: sorted([str(z) for z in rdf_utils.fetchValue(g, x)]) == sorted(d[x]),
                    d.keys())))
        # on utilise fetchValue pour vérifier que les valeurs stockées dans le graphe
        # pour chaque chemin sont bien identiques à celles du dictionnaire

    def test_buildGraph_5(self):
        # idem test_buildGraph_4 avec catégorie de métadonnées personnalisée
        d = {
            'dct:description': ["Délimitation simplifiée des départements de France métropolitaine pour représentation à petite échelle, conforme au code officiel géographique (COG) de l'INSEE au 1er janvier de l'année de référence."],
            'dct:provenance / rdfs:label': ["Donnée référentielle produite par l'IGN."],
            'dct:publisher / foaf:name': ["Institut national de l'information géographique et forestière (IGN-F)"],
            'dct:created': ['2020-08-03'],
            'dcat:keyword': ['donnée externe'],
            'dct:modified': ['2021-02-04'],
            'dcat:distribution / dct:accessURL': ['https://geoservices.ign.fr/documentation/diffusion/telechargement-donnees-libres.html#admin-express'],
            'dcat:distribution / dct:issued': ['2021-01-19'],
            'dcat:distribution / dct:licence / rdfs:label': ['Base de données soumise aux conditions de la licence ouverte Etalab.'],
            'dct:accessRights / rdfs:label': ["Aucune restriction d'accès ou d'usage."],
            'dct:title': ['ADMIN EXPRESS - Départements de métropole'],
            'dct:temporal / dcat:startDate': ['2021-01-15'],
            'dct:temporal / dcat:endDate': ['2021-01-15'],
            'dcat:landingPage': ['https://geoservices.ign.fr/ressources_documentaires/Espace_documentaire/BASES_VECTORIELLES/ADMIN_EXPRESS/IGNF_ADMIN_EXPRESS_2-4.html'],
            "<urn:uuid:218c1245-6ba7-4163-841e-476e0d5582af>": ["À mettre à jour !"]
            }
        g = rdf_utils.buildGraph(d, self.dataset_template, self.vocabulary)
        
        self.assertTrue(
            all(map(lambda x: sorted([str(z) for z in rdf_utils.fetchValue(g, x)]) == sorted(d[x]),
                    d.keys())))

    def test_buildGraph_6(self):
        # idem test_buildGraph_5 avec liste de valeurs pour une même catégorie de métadonnées
        d = {
            'dct:description': ["Délimitation simplifiée des départements de France métropolitaine pour représentation à petite échelle, conforme au code officiel géographique (COG) de l'INSEE au 1er janvier de l'année de référence."],
            'dct:provenance / rdfs:label': ["Donnée référentielle produite par l'IGN."],
            'dct:publisher / foaf:name': ["Institut national de l'information géographique et forestière (IGN-F)"],
            'dct:created': ['2020-08-03'],
            'dct:modified': ['2021-02-04'],
            'dcat:distribution / dct:accessURL': ['https://geoservices.ign.fr/documentation/diffusion/telechargement-donnees-libres.html#admin-express'],
            'dcat:distribution / dct:issued': ['2021-01-19'],
            'dcat:distribution / dct:licence / rdfs:label': ['Base de données soumise aux conditions de la licence ouverte Etalab.'],
            'dct:accessRights / rdfs:label': ["Aucune restriction d'accès ou d'usage."],
            'dct:title': ['ADMIN EXPRESS - Départements de métropole'],
            'dct:temporal / dcat:startDate': ['2021-01-15'],
            'dct:temporal / dcat:endDate': ['2021-01-15'],
            'dcat:landingPage': ['https://geoservices.ign.fr/ressources_documentaires/Espace_documentaire/BASES_VECTORIELLES/ADMIN_EXPRESS/IGNF_ADMIN_EXPRESS_2-4.html'],
            "<urn:uuid:218c1245-6ba7-4163-841e-476e0d5582af>": ["À mettre à jour !"],
            "dcat:keyword": ["donnée externe", "ign", "admin express"]
            }
        g = rdf_utils.buildGraph(d, self.dataset_template, self.vocabulary)
        
        self.assertTrue(
            all(map(lambda x: sorted([str(z) for z in rdf_utils.fetchValue(g, x)]) == sorted(d[x]),
                    d.keys())))

    def test_buildGraph_7(self):
        # idem test_buildGraph_6 en ajoutant une propriété avec vocabulaire contrôlé.
        # Dans ce cas, les valeurs renvoyées par fetchValue ne correspondent
        # pas à celles du dictionnaire, on passe par fetchValueFromConcept
        d = {
            'dct:description': ["Délimitation simplifiée des départements de France métropolitaine pour représentation à petite échelle, conforme au code officiel géographique (COG) de l'INSEE au 1er janvier de l'année de référence."],
            'dct:provenance / rdfs:label': ["Donnée référentielle produite par l'IGN."],
            'dct:publisher / foaf:name': ["Institut national de l'information géographique et forestière (IGN-F)"],
            'dct:created': ['2020-08-03'],
            'dct:modified': ['2021-02-04'],
            'dcat:distribution / dct:accessURL': ['https://geoservices.ign.fr/documentation/diffusion/telechargement-donnees-libres.html#admin-express'],
            'dcat:distribution / dct:issued': ['2021-01-19'],
            'dcat:distribution / dct:licence / rdfs:label': ['Base de données soumise aux conditions de la licence ouverte Etalab.'],
            'dct:accessRights / rdfs:label': ["Aucune restriction d'accès ou d'usage."],
            'dct:title': ['ADMIN EXPRESS - Départements de métropole'],
            'dct:temporal / dcat:startDate': ['2021-01-15'],
            'dct:temporal / dcat:endDate': ['2021-01-15'],
            'dcat:landingPage': ['https://geoservices.ign.fr/ressources_documentaires/Espace_documentaire/BASES_VECTORIELLES/ADMIN_EXPRESS/IGNF_ADMIN_EXPRESS_2-4.html'],
            "<urn:uuid:218c1245-6ba7-4163-841e-476e0d5582af>": ["À mettre à jour !"],
            "dcat:keyword": ["donnée externe", "ign", "admin express"],
            "dcat:theme" : ["Régions et villes", "Données provisoires"]
            }
        g = rdf_utils.buildGraph(d, self.dataset_template, self.vocabulary)
        self.assertTrue(
            all(
                map(
                    lambda x: sorted([
                        str(
                            rdf_utils.fetchValueFromConcept(
                                x, z, self.dataset_template, self.vocabulary
                                )
                            or z
                            )
                        for z in rdf_utils.fetchValue(g, x)
                        ]) == sorted(d[x]),
                    d.keys()
                    )
                )
            )

    def test_buildGraph_8(self):
        # valeur non autorisée pour une propriété au vocabulaire contrôlé
        d = {
            "dcat:theme" : ["Littérature"]
            }
        self.assertRaisesRegex(ValueError, "^Controlled.vocabulary", rdf_utils.buildGraph,
                               d, self.dataset_template, self.vocabulary)

    def test_buildGraph_9(self):
        # IRI invalide
        d = {
            'dcat:landingPage': ['https:// !!!  geoservices.ign.fr/ressources_documentaires/Espace_documentaire/BASES_VECTORIELLES/ADMIN_EXPRESS/IGNF_ADMIN_EXPRESS_2-4.html'],
            }
        self.assertRaisesRegex(ValueError, "^Invalid.IRI", rdf_utils.buildGraph,
                               d, self.dataset_template, self.vocabulary)

    def test_buildGraph_10(self):
        # conservation de l'UUID
        d = {'dct:title': ['ADMIN EXPRESS - Départements de métropole']}
        i = URIRef("urn:uuid:" + str(uuid.uuid4()))
        self.assertEqual(
            rdf_utils.fetchUUID(rdf_utils.buildGraph(d, self.dataset_template, self.vocabulary,
                                                     datasetUUID=i)),
            i
            )

    def test_buildGraph_11(self):
        d1 = {
            'dct:description': ["Délimitation simplifiée des départements de France métropolitaine pour représentation à petite échelle, conforme au code officiel géographique (COG) de l'INSEE au 1er janvier de l'année de référence."],
            'dct:provenance / rdfs:label': ["Donnée référentielle produite par l'IGN."],
            'dct:publisher / foaf:name': ["Institut national de l'information géographique et forestière (IGN-F)"],
            'dct:created': ['2020-08-03'],
            'dct:modified': ['2021-02-04'],
            'dcat:distribution / dct:accessURL': ['https://geoservices.ign.fr/documentation/diffusion/telechargement-donnees-libres.html#admin-express'],
            'dcat:distribution / dct:issued': ['2021-01-19'],
            'dcat:distribution / dct:licence / rdfs:label': ['Base de données soumise aux conditions de la licence ouverte Etalab.'],
            'dct:accessRights / rdfs:label': ["Aucune restriction d'accès ou d'usage."],
            'dct:title': ['ADMIN EXPRESS - Départements de métropole'],
            'dct:temporal / dcat:startDate': ['2021-01-15'],
            'dct:temporal / dcat:endDate': ['2021-01-15'],
            'dcat:landingPage': ['https://geoservices.ign.fr/ressources_documentaires/Espace_documentaire/BASES_VECTORIELLES/ADMIN_EXPRESS/IGNF_ADMIN_EXPRESS_2-4.html'],
            "<urn:uuid:218c1245-6ba7-4163-841e-476e0d5582af>": ["À mettre à jour !"],
            "dcat:keyword": ["donnée externe", "ign", "admin express"],
            "dcat:theme" : ["Régions et villes", "Données provisoires"]
            }
        g1 = rdf_utils.buildGraph(d1, self.dataset_template, self.vocabulary)
        d2 = rdf_utils.buildDict(g1, self.dataset_template, self.vocabulary)
        g2 = rdf_utils.buildGraph(d1, self.dataset_template, self.vocabulary,
                                  datasetUUID=rdf_utils.fetchUUID(g1))
        self.assertTrue(isomorphic(g1, g2))

    def test_buildGraph_12(self):
        self.assertRaises(TypeError, rdf_utils.buildGraph, dict(),
                          self.dataset_template, self.vocabulary,
                          datasetUUID = "urn:uuid:218c1245-6ba7-4163-841e-476e0d5582a")

    def test_buildGraph_13(self):
        self.assertRaises(TypeError, rdf_utils.buildGraph, dict(),
                          self.dataset_template, self.vocabulary,
                          templateUUID = "urn:uuid:218c1245-6ba7-4163-841e-476e0d5582a")

    def test_buildGraph_14(self):
        # si la liste de valeurs est vide, la propriété n'est pas créée
        g = rdf_utils.buildGraph({ 'dct:title' : [], "dcat:keyword" : ["ohé"] },
                                 self.dataset_template, self.vocabulary)
        self.assertTrue(len(g) == 2 # dcat:keyword + a dcat:Dataset
                        and rdf_utils.fetchValue(g, "dct:title") is None
                        and rdf_utils.fetchValue(g, "dcat:keyword") == [Literal("ohé", lang="fr")])

    def test_buildGraph_15(self):
        # si la liste de valeurs est vide
        g = rdf_utils.buildGraph({ 'dcat:distribution / dct:accessURL' : [], "dcat:keyword" : ["ohé"] },
                                 self.dataset_template, self.vocabulary)
        self.assertTrue(len(g) == 2 # dcat:keyword + a dcat:Dataset
                        and rdf_utils.fetchValue(g, "dcat:keyword") == [Literal("ohé", lang="fr")])

    def test_buildGraph_16(self):
        # chaînes vides dans la liste de valeurs
        g = rdf_utils.buildGraph({ 'dct:title' : ["mon titre"], "dcat:keyword" : ["ohé", ""] },
                                 self.dataset_template, self.vocabulary)
        self.assertTrue(len(g) == 3 # dct:title + dcat:keyword + a dcat:Dataset
                        and rdf_utils.fetchValue(g, "dct:title") == [Literal("mon titre", lang="fr")]
                        and rdf_utils.fetchValue(g, "dcat:keyword") == [Literal("ohé", lang="fr")])

    def test_buildGraph_17(self):
        # uniquement des chaînes vides dans la liste de valeurs
        g = rdf_utils.buildGraph({ 'dct:title' : ["mon titre"], "dcat:distribution / dct:accessURL" : ["", ""] },
                                 self.dataset_template, self.vocabulary)
        self.assertTrue(len(g) == 2 # dct:title + a dcat:Dataset
                        and rdf_utils.fetchValue(g, "dct:title") == [Literal("mon titre", lang="fr")])

    def test_buildGraph_18(self):
        # None dans la liste de valeurs
        g = rdf_utils.buildGraph({ 'dct:title' : ["mon titre"], "dcat:keyword" : ["ohé", None] },
                                 self.dataset_template, self.vocabulary)
        self.assertTrue(len(g) == 3 # dct:title + dcat:keyword + a dcat:Dataset
                        and rdf_utils.fetchValue(g, "dct:title") == [Literal("mon titre", lang="fr")]
                        and rdf_utils.fetchValue(g, "dcat:keyword") == [Literal("ohé", lang="fr")])

    def test_buildGraph_19(self):
        # uniquement None dans la liste de valeurs
        g = rdf_utils.buildGraph({ 'dct:title' : ["mon titre"], "dcat:distribution / dct:accessURL" : [None, None] },
                                 self.dataset_template, self.vocabulary)
        self.assertTrue(len(g) == 2 # dct:title + a dcat:Dataset
                        and rdf_utils.fetchValue(g, "dct:title") == [Literal("mon titre", lang="fr")])

    def test_buildGraph_20(self):
        # valeur None
        g = rdf_utils.buildGraph({ 'dct:title' : ["mon titre"], "dcat:distribution / dct:accessURL" : None },
                                 self.dataset_template, self.vocabulary)
        self.assertTrue(len(g) == 2 # dct:title + a dcat:Dataset
                        and rdf_utils.fetchValue(g, "dct:title") == [Literal("mon titre", lang="fr")])

    def test_buildGraph_21(self):
        # clé None
        g = rdf_utils.buildGraph({ 'dct:title' : ["mon titre"], None : ["?"] },
                                 self.dataset_template, self.vocabulary)
        self.assertTrue(len(g) == 2 # dct:title + a dcat:Dataset
                        and rdf_utils.fetchValue(g, "dct:title") == [Literal("mon titre", lang="fr")])

    def test_buildGraph_22(self):
        # clé ""
        g = rdf_utils.buildGraph({ 'dct:title' : ["mon titre"], "" : ["?"] },
                                 self.dataset_template, self.vocabulary)
        self.assertTrue(len(g) == 2 # dct:title + a dcat:Dataset
                        and rdf_utils.fetchValue(g, "dct:title") == [Literal("mon titre", lang="fr")])

    # les tests 23 à 27 correspondent à des entrées illégales dans le graphe, ou
    # du moins non prévues par le modèle commun et qui n'ont pas non plus le
    # formalisme prévu pour les catégories locales (UUID comme identifiant).
    # Pour l'heure, tant que les préfixes utilisés sont valides (ou qu'aucun
    # préfixe n'est utilisé), les propriétés sont enregistrées dans le graphe
    # si et seulement si le chemin n'a qu'une composante et les valeurs
    # sont toujours considérées comme Literal... sauf si le chemin est une
    # branche raccourcie (auquel cas la valeur est toujours un IRI).

    def test_buildGraph_23(self):
        g = rdf_utils.buildGraph({ "sh:hasValue" : ["?"] }, self.dataset_template, self.vocabulary)
        self.assertTrue(len(g) == 2
                        and rdf_utils.fetchValue(g, "sh:hasValue") == [Literal("?", lang="fr")])

    def test_buildGraph_24(self): # branche raccourcie
        g = rdf_utils.buildGraph({ "dct:temporal" : ["?"] }, self.dataset_template, self.vocabulary)
        self.assertTrue(len(g) == 2
                        and rdf_utils.fetchValue(g, "dct:temporal") == [URIRef("?")])

    def test_buildGraph_25(self): # branche raccourcie (mais IRI invalide)
        self.assertRaisesRegex(ValueError, "Invalid.IRI", rdf_utils.buildGraph,
                               { "dct:temporal" : ["?^"] }, self.dataset_template, self.vocabulary)
    
    def test_buildGraph_26(self):
        self.assertRaisesRegex(KeyError, "Invalid.path", rdf_utils.buildGraph,
                               { "dct:temporal / dcat:keyword" : ["?"] }, self.dataset_template, self.vocabulary)
        
    def test_buildGraph_27(self):
        self.assertRaisesRegex(KeyError, "Invalid.path", rdf_utils.buildGraph,
                               { "sh:hasValue / dcat:keyword" : ["?"] }, self.dataset_template, self.vocabulary)

    # les chemins mal formés et préfixe non connus (absents du modèle)
    # provoquent des erreurs non gérées

    def test_buildGraph_28(self):
        g = rdf_utils.buildGraph({"dcat:contactPoint / vcard:hasTelephone" : ["0123456789"]},
                                 self.dataset_template, self.vocabulary)
        self.assertEqual(rdf_utils.fetchValue(g, "dcat:contactPoint / vcard:hasTelephone"),
                         [URIRef("tel:+33-1-23-45-67-89")])

    def test_buildGraph_29(self):
        g = rdf_utils.buildGraph({"dct:publisher / foaf:phone" : ["0123456789"]},
                                 self.dataset_template, self.vocabulary)
        self.assertEqual(rdf_utils.fetchValue(g, "dct:publisher / foaf:phone"),
                         [URIRef("tel:+33-1-23-45-67-89")])
        
        # cf. owlThingFromTel pour les tests approfondis sur différents types
        # de numéros de téléphones

    def test_buildGraph_30(self):
        g = rdf_utils.buildGraph({"dcat:contactPoint / vcard:hasEmail" : ["jon.snow@the-wall.we"]},
                                 self.dataset_template, self.vocabulary)
        self.assertEqual(rdf_utils.fetchValue(g, "dcat:contactPoint / vcard:hasEmail"),
                         [URIRef("mailto:jon.snow@the-wall.we")])

    def test_buildGraph_31(self):
        g = rdf_utils.buildGraph({"dct:publisher / foaf:mbox" : ["jon.snow@the-wall.we"]},
                                 self.dataset_template, self.vocabulary)
        self.assertEqual(rdf_utils.fetchValue(g, "dct:publisher / foaf:mbox"),
                         [URIRef("mailto:jon.snow@the-wall.we")])
        


    ### buildDict

    # pas de tests avec un modèle problématique ou sans graphe de vocabulaire, car la fonction
    # ne devrait jamais être utilisée dans ce contexte (et les erreurs qui en résulteraient
    # n'ont pas vocation à être gérées).

    def test_buildDict_1(self):
        self.assertEqual(rdf_utils.buildDict(Graph(), self.dataset_template, self.vocabulary), dict())

    def test_buildDict_2(self):
        g = rdf_utils.buildGraph(dict(), self.dataset_template, self.vocabulary)
        self.assertEqual(rdf_utils.buildDict(g, self.dataset_template, self.vocabulary), dict())
        
    def test_buildDict_3(self):
        d1 = {
            'dct:description': ["Délimitation simplifiée des départements de France métropolitaine pour représentation à petite échelle, conforme au code officiel géographique (COG) de l'INSEE au 1er janvier de l'année de référence."],
            'dct:provenance / rdfs:label': ["Donnée référentielle produite par l'IGN."],
            'dct:publisher / foaf:name': ["Institut national de l'information géographique et forestière (IGN-F)"],
            'dct:created': ['2020-08-03'],
            'dcat:keyword': ['donnée externe'],
            'dct:modified': ['2021-02-04'],
            'dcat:distribution / dct:accessURL': ['https://geoservices.ign.fr/documentation/diffusion/telechargement-donnees-libres.html#admin-express'],
            'dcat:distribution / dct:issued': ['2021-01-19'],
            'dcat:distribution / dct:licence / rdfs:label': ['Base de données soumise aux conditions de la licence ouverte Etalab.'],
            'dct:accessRights / rdfs:label': ["Aucune restriction d'accès ou d'usage."],
            'dct:title': ['ADMIN EXPRESS - Départements de métropole'],
            'dct:temporal / dcat:startDate': ['2021-01-15'],
            'dct:temporal / dcat:endDate': ['2021-01-15'],
            'dcat:landingPage': ['https://geoservices.ign.fr/ressources_documentaires/Espace_documentaire/BASES_VECTORIELLES/ADMIN_EXPRESS/IGNF_ADMIN_EXPRESS_2-4.html']
            }
        g = rdf_utils.buildGraph(d1, self.dataset_template, self.vocabulary)
        d2 = rdf_utils.buildDict(g, self.dataset_template, self.vocabulary)
        self.assertEqual(sorted([k + str(sorted(v)) for k, v in d1.items()]),
                         sorted([k + str(sorted(v)) for k, v in d2.items()]))

    def test_buildDict_4(self):
        d1 = {
            'dct:description': ["Délimitation simplifiée des départements de France métropolitaine pour représentation à petite échelle, conforme au code officiel géographique (COG) de l'INSEE au 1er janvier de l'année de référence."],
            'dct:provenance / rdfs:label': ["Donnée référentielle produite par l'IGN."],
            'dct:publisher / foaf:name': ["Institut national de l'information géographique et forestière (IGN-F)"],
            'dct:created': ['2020-08-03'],
            'dcat:keyword': ['donnée externe'],
            'dct:modified': ['2021-02-04'],
            'dcat:distribution / dct:accessURL': ['https://geoservices.ign.fr/documentation/diffusion/telechargement-donnees-libres.html#admin-express'],
            'dcat:distribution / dct:issued': ['2021-01-19'],
            'dcat:distribution / dct:licence / rdfs:label': ['Base de données soumise aux conditions de la licence ouverte Etalab.'],
            'dct:accessRights / rdfs:label': ["Aucune restriction d'accès ou d'usage."],
            'dct:title': ['ADMIN EXPRESS - Départements de métropole'],
            'dct:temporal / dcat:startDate': ['2021-01-15'],
            'dct:temporal / dcat:endDate': ['2021-01-15'],
            'dcat:landingPage': ['https://geoservices.ign.fr/ressources_documentaires/Espace_documentaire/BASES_VECTORIELLES/ADMIN_EXPRESS/IGNF_ADMIN_EXPRESS_2-4.html'],
            "<urn:uuid:218c1245-6ba7-4163-841e-476e0d5582af>": ["À mettre à jour !"]
            }
        g = rdf_utils.buildGraph(d1, self.dataset_template, self.vocabulary)
        d2 = rdf_utils.buildDict(g, self.dataset_template, self.vocabulary)
        self.assertEqual(sorted([k + str(sorted(v)) for k, v in d1.items()]),
                         sorted([k + str(sorted(v)) for k, v in d2.items()]))

    def test_buildDict_5(self):
        d1 = {
            'dct:description': ["Délimitation simplifiée des départements de France métropolitaine pour représentation à petite échelle, conforme au code officiel géographique (COG) de l'INSEE au 1er janvier de l'année de référence."],
            'dct:provenance / rdfs:label': ["Donnée référentielle produite par l'IGN."],
            'dct:publisher / foaf:name': ["Institut national de l'information géographique et forestière (IGN-F)"],
            'dct:created': ['2020-08-03'],
            'dct:modified': ['2021-02-04'],
            'dcat:distribution / dct:accessURL': ['https://geoservices.ign.fr/documentation/diffusion/telechargement-donnees-libres.html#admin-express'],
            'dcat:distribution / dct:issued': ['2021-01-19'],
            'dcat:distribution / dct:licence / rdfs:label': ['Base de données soumise aux conditions de la licence ouverte Etalab.'],
            'dct:accessRights / rdfs:label': ["Aucune restriction d'accès ou d'usage."],
            'dct:title': ['ADMIN EXPRESS - Départements de métropole'],
            'dct:temporal / dcat:startDate': ['2021-01-15'],
            'dct:temporal / dcat:endDate': ['2021-01-15'],
            'dcat:landingPage': ['https://geoservices.ign.fr/ressources_documentaires/Espace_documentaire/BASES_VECTORIELLES/ADMIN_EXPRESS/IGNF_ADMIN_EXPRESS_2-4.html'],
            "<urn:uuid:218c1245-6ba7-4163-841e-476e0d5582af>": ["À mettre à jour !"],
            "dcat:keyword": ["donnée externe", "ign", "admin express"]
            }
        g = rdf_utils.buildGraph(d1, self.dataset_template, self.vocabulary)
        d2 = rdf_utils.buildDict(g, self.dataset_template, self.vocabulary)
        self.assertEqual(sorted([k + str(sorted(v)) for k, v in d1.items()]),
                         sorted([k + str(sorted(v)) for k, v in d2.items()]))

    def test_buildDict_6(self):
        d1 = {
            'dct:description': ["Délimitation simplifiée des départements de France métropolitaine pour représentation à petite échelle, conforme au code officiel géographique (COG) de l'INSEE au 1er janvier de l'année de référence."],
            'dct:provenance / rdfs:label': ["Donnée référentielle produite par l'IGN."],
            'dct:publisher / foaf:name': ["Institut national de l'information géographique et forestière (IGN-F)"],
            'dct:created': ['2020-08-03'],
            'dct:modified': ['2021-02-04'],
            'dcat:distribution / dct:accessURL': ['https://geoservices.ign.fr/documentation/diffusion/telechargement-donnees-libres.html#admin-express'],
            'dcat:distribution / dct:issued': ['2021-01-19'],
            'dcat:distribution / dct:licence / rdfs:label': ['Base de données soumise aux conditions de la licence ouverte Etalab.'],
            'dct:accessRights / rdfs:label': ["Aucune restriction d'accès ou d'usage."],
            'dct:title': ['ADMIN EXPRESS - Départements de métropole'],
            'dct:temporal / dcat:startDate': ['2021-01-15'],
            'dct:temporal / dcat:endDate': ['2021-01-15'],
            'dcat:landingPage': ['https://geoservices.ign.fr/ressources_documentaires/Espace_documentaire/BASES_VECTORIELLES/ADMIN_EXPRESS/IGNF_ADMIN_EXPRESS_2-4.html'],
            "<urn:uuid:218c1245-6ba7-4163-841e-476e0d5582af>": ["À mettre à jour !"],
            "dcat:keyword": ["donnée externe", "ign", "admin express"],
            "dcat:theme" : ["Régions et villes", "Données provisoires"]
            }
        g = rdf_utils.buildGraph(d1, self.dataset_template, self.vocabulary)
        d2 = rdf_utils.buildDict(g, self.dataset_template, self.vocabulary)
        self.assertEqual(sorted([k + str(sorted(v)) for k, v in d1.items()]),
                         sorted([k + str(sorted(v)) for k, v in d2.items()]))

    def test_buildDict_7(self):
        self.assertRaises(TypeError, rdf_utils.buildDict, Graph(),
                          self.dataset_template, self.vocabulary,
                          datasetUUID = "urn:uuid:218c1245-6ba7-4163-841e-476e0d5582a")

    def test_buildDict_8(self):
        self.assertRaises(TypeError, rdf_utils.buildDict, Graph(),
                          self.dataset_template, self.vocabulary,
                          templateUUID = "urn:uuid:218c1245-6ba7-4163-841e-476e0d5582a")

    def test_buildDict_9(self):
        g = rdf_utils.buildGraph({"dcat:contactPoint / vcard:hasTelephone" : ["0123456789"]},
                                 self.dataset_template, self.vocabulary)
        d = rdf_utils.buildDict(g, self.dataset_template, self.vocabulary)
        self.assertEqual(d["dcat:contactPoint / vcard:hasTelephone"], ["+33-1-23-45-67-89"])

    def test_buildDict_10(self):
        g = rdf_utils.buildGraph({"dct:publisher / foaf:phone" : ["0123456789"]},
                                 self.dataset_template, self.vocabulary)
        d = rdf_utils.buildDict(g, self.dataset_template, self.vocabulary)
        self.assertEqual(d["dct:publisher / foaf:phone"], ["+33-1-23-45-67-89"])

    def test_buildDict_11(self):
        g = rdf_utils.buildGraph({"dcat:contactPoint / vcard:hasEmail" : ["jon.snow@the-wall.we"]},
                                 self.dataset_template, self.vocabulary)
        d = rdf_utils.buildDict(g, self.dataset_template, self.vocabulary)
        self.assertEqual(d["dcat:contactPoint / vcard:hasEmail"], ["jon.snow@the-wall.we"])

    def test_buildDict_12(self):
        g = rdf_utils.buildGraph({"dct:publisher / foaf:mbox" : ["jon.snow@the-wall.we"]},
                                 self.dataset_template, self.vocabulary)
        d = rdf_utils.buildDict(g, self.dataset_template, self.vocabulary)
        self.assertEqual(d["dct:publisher / foaf:mbox"], ["jon.snow@the-wall.we"])


    ### extractMetadata

    def test_extractMetadata_1(self):
        c = ""
        self.assertTrue(isomorphic(rdf_utils.extractMetadata(c, self.dataset_template), Graph()))

    def test_extractMetadata_2(self):
        c = "Commentaire sans métadonnées."
        self.assertTrue(isomorphic(rdf_utils.extractMetadata(c, self.dataset_template), Graph()))

    def test_extractMetadata_3(self):
        c = "Commentaire avec métadonnées vides.<METADATA></METADATA>"
        self.assertTrue(isomorphic(rdf_utils.extractMetadata(c, self.dataset_template), Graph()))

    def test_extractMetadata_4(self):
        c = "Commentaire avec métadonnées invalides.<METADATA>Ceci n'est pas un JSON !</METADATA>"
        self.assertRaises(JSONDecodeError, rdf_utils.extractMetadata, c, self.dataset_template)

    def test_extractMetadata_5(self):
        c = 'Commentaire avec métadonnées mal structurées.<METADATA>{"name": "Pas un JSON-LD !"}</METADATA>'
        self.assertTrue(isomorphic(rdf_utils.extractMetadata(c, self.dataset_template), Graph()))

    def test_extractMetadata_6(self):
        c = """Commentaire avec métadonnées bien structurées.<METADATA>
[
  {
    "@id": "urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778",
    "@type": [
      "http://www.w3.org/ns/dcat#Dataset"
    ],
    "http://purl.org/dc/terms/created": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#date",
        "@value": "2020-08-03"
      }
    ]
  }
]
</METADATA>"""
        g = rdf_utils.buildGraph({"dct:created" : ["2020-08-03"]}, self.dataset_template,
                                 self.vocabulary,
                                 datasetUUID=URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"))
        self.assertTrue(isomorphic(rdf_utils.extractMetadata(c, self.dataset_template), g))

    # les tests 7 à 10 contrôlent la résilience de la fonction face aux
    # anomalies de balisage
    
    def test_extractMetadata_7(self):
        c = """<METADATA><METADATA>
[
  {
    "@id": "urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778",
    "@type": [
      "http://www.w3.org/ns/dcat#Dataset"
    ],
    "http://purl.org/dc/terms/created": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#date",
        "@value": "2020-08-03"
      }
    ]
  }
]
</METADATA>"""
        g = rdf_utils.buildGraph({"dct:created" : ["2020-08-03"]}, self.dataset_template,
                                 self.vocabulary,
                                 datasetUUID=URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"))
        self.assertTrue(isomorphic(rdf_utils.extractMetadata(c, self.dataset_template), g))

    def test_extractMetadata_8(self):
        c = """<METADATA><METADATA>
[
  {
    "@id": "urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778",
    "@type": [
      "http://www.w3.org/ns/dcat#Dataset"
    ],
    "http://purl.org/dc/terms/created": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#date",
        "@value": "2020-08-03"
      }
    ]
  }
]
</METADATA></METADATA>"""
        g = rdf_utils.buildGraph({"dct:created" : ["2020-08-03"]}, self.dataset_template,
                                 self.vocabulary,
                                 datasetUUID=URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"))
        self.assertTrue(isomorphic(rdf_utils.extractMetadata(c, self.dataset_template), g))


    def test_extractMetadata_9(self):
        c = """<METADATA>
[
  {
    "@id": "urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778",
    "@type": [
      "http://www.w3.org/ns/dcat#Dataset"
    ],
    "http://purl.org/dc/terms/created": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#date",
        "@value": "2020-08-03"
      }
    ]
  }
]
</METADATA></METADATA>"""
        g = rdf_utils.buildGraph({"dct:created" : ["2020-08-03"]}, self.dataset_template,
                                 self.vocabulary,
                                 datasetUUID=URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"))
        self.assertTrue(isomorphic(rdf_utils.extractMetadata(c, self.dataset_template), g))
        

    def test_extractMetadata_10(self):
        c = """<METADATA>
[
  {
    "@id": "urn:uuid:d41423cc-fb59-443f-86f4-72592a4f6778",
    "@type": [
      "http://www.w3.org/ns/dcat#Dataset"
    ]
  }
]
</METADATA><METADATA>
[
  {
    "@id": "urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778",
    "@type": [
      "http://www.w3.org/ns/dcat#Dataset"
    ],
    "http://purl.org/dc/terms/created": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#date",
        "@value": "2020-08-03"
      }
    ]
  }
]
</METADATA>"""
        g = rdf_utils.buildGraph({"dct:created" : ["2020-08-03"]}, self.dataset_template,
                                 self.vocabulary,
                                 datasetUUID=URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"))
        self.assertTrue(isomorphic(rdf_utils.extractMetadata(c, self.dataset_template), g))


    ### updateDescription

    def test_updateDescription_1(self):
        c1 = ""
        c2 = """

<METADATA>
[
  {
    "@id": "urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778",
    "@type": [
      "http://www.w3.org/ns/dcat#Dataset"
    ],
    "http://purl.org/dc/terms/created": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#date",
        "@value": "2020-08-03"
      }
    ]
  }
]
</METADATA>
"""
        g = rdf_utils.buildGraph({"dct:created" : ["2020-08-03"]}, self.dataset_template,
                                 self.vocabulary,
                                 datasetUUID=URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"))
        self.assertEqual(rdf_utils.updateDescription(c1, g), c2)

    def test_updateDescription_2(self):
        c1 = "Commentaire."
        c2 = """Commentaire.

<METADATA>
[
  {
    "@id": "urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778",
    "@type": [
      "http://www.w3.org/ns/dcat#Dataset"
    ],
    "http://purl.org/dc/terms/created": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#date",
        "@value": "2020-08-03"
      }
    ]
  }
]
</METADATA>
"""
        g = rdf_utils.buildGraph({"dct:created" : ["2020-08-03"]}, self.dataset_template,
                                 self.vocabulary,
                                 datasetUUID=URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"))
        self.assertEqual(rdf_utils.updateDescription(c1, g), c2)

    def test_updateDescription_3(self):
        c1 = "Commentaire."
        self.assertEqual(rdf_utils.updateDescription(c1, Graph()), c1)

    def test_updateDescription_4(self):
        c1 = "Commentaire.<METADATA></METADATA>"
        c2 = """Commentaire.<METADATA>
[
  {
    "@id": "urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778",
    "@type": [
      "http://www.w3.org/ns/dcat#Dataset"
    ],
    "http://purl.org/dc/terms/created": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#date",
        "@value": "2020-08-03"
      }
    ]
  }
]
</METADATA>"""
        g = rdf_utils.buildGraph({"dct:created" : ["2020-08-03"]}, self.dataset_template,
                                 self.vocabulary,
                                 datasetUUID=URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"))
        self.assertEqual(rdf_utils.updateDescription(c1, g), c2)

    def test_updateDescription_5(self):
        c1 = "Commentaire.<METADATA>N'importe quoi !!</METADATA>"
        c2 = """Commentaire.<METADATA>
[
  {
    "@id": "urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778",
    "@type": [
      "http://www.w3.org/ns/dcat#Dataset"
    ],
    "http://purl.org/dc/terms/created": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#date",
        "@value": "2020-08-03"
      }
    ]
  }
]
</METADATA>"""
        g = rdf_utils.buildGraph({"dct:created" : ["2020-08-03"]}, self.dataset_template,
                                 self.vocabulary,
                                 datasetUUID=URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"))
        self.assertEqual(rdf_utils.updateDescription(c1, g), c2)

    def test_updateDescription_6(self):
        c1 = "Commentaire.<METADATA><METADATA>N'importe quoi !!</METADATA>"
        c2 = """Commentaire.<METADATA>
[
  {
    "@id": "urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778",
    "@type": [
      "http://www.w3.org/ns/dcat#Dataset"
    ],
    "http://purl.org/dc/terms/created": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#date",
        "@value": "2020-08-03"
      }
    ]
  }
]
</METADATA>"""
        g = rdf_utils.buildGraph({"dct:created" : ["2020-08-03"]}, self.dataset_template,
                                 self.vocabulary,
                                 datasetUUID=URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"))
        self.assertEqual(rdf_utils.updateDescription(c1, g), c2)

    def test_updateDescription_7(self):
        c1 = "Commentaire.<METADATA><METADATA>N'importe quoi !!</METADATA></METADATA>Suite."
        c2 = """Commentaire.<METADATA>
[
  {
    "@id": "urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778",
    "@type": [
      "http://www.w3.org/ns/dcat#Dataset"
    ],
    "http://purl.org/dc/terms/created": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#date",
        "@value": "2020-08-03"
      }
    ]
  }
]
</METADATA>Suite."""
        g = rdf_utils.buildGraph({"dct:created" : ["2020-08-03"]}, self.dataset_template,
                                 self.vocabulary,
                                 datasetUUID=URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"))
        self.assertEqual(rdf_utils.updateDescription(c1, g), c2)

    def test_updateDescription_8(self):
        c1 = "Commentaire.<METADATA>N'importe quoi !!</METADATA></METADATA>Suite."
        c2 = """Commentaire.<METADATA>
[
  {
    "@id": "urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778",
    "@type": [
      "http://www.w3.org/ns/dcat#Dataset"
    ],
    "http://purl.org/dc/terms/created": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#date",
        "@value": "2020-08-03"
      }
    ]
  }
]
</METADATA>Suite."""
        g = rdf_utils.buildGraph({"dct:created" : ["2020-08-03"]}, self.dataset_template,
                                 self.vocabulary,
                                 datasetUUID=URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"))
        self.assertEqual(rdf_utils.updateDescription(c1, g), c2)

    def test_updateDescription_9(self):
        c1 = """Commentaire.<METADATA>N'importe quoi 1!!</METADATA>
             <METADATA>N'importe quoi 2!!</METADATA>Suite."""
        c2 = """Commentaire.<METADATA>
[
  {
    "@id": "urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778",
    "@type": [
      "http://www.w3.org/ns/dcat#Dataset"
    ],
    "http://purl.org/dc/terms/created": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#date",
        "@value": "2020-08-03"
      }
    ]
  }
]
</METADATA>Suite."""
        g = rdf_utils.buildGraph({"dct:created" : ["2020-08-03"]}, self.dataset_template,
                                 self.vocabulary,
                                 datasetUUID=URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"))
        self.assertEqual(rdf_utils.updateDescription(c1, g), c2)


    ### combinaisons

    # les tests ci-après reproduisent les mécanismes qui seront vraisembablement
    # mis en oeuvre par les plugins de consultation/saisie des métadonnées

    def test_combinaison_1(self):
        c0 = "Commentaire."
        g0 = rdf_utils.extractMetadata(c0, self.dataset_template)
        d0 = rdf_utils.buildDict(g0, self.dataset_template, self.vocabulary)
        g1 = rdf_utils.buildGraph(d0, self.dataset_template, self.vocabulary)
        i1 = rdf_utils.fetchUUID(g1)
        c1 = """Commentaire.

<METADATA>
[
  {{
    "@id": "{}",
    "@type": [
      "http://www.w3.org/ns/dcat#Dataset"
    ]
  }}
]
</METADATA>
""".format(str(i1))
        self.assertEqual(rdf_utils.updateDescription(c0, g1), c1)
        

    def test_combinaison_2(self):
        c0 = "Commentaire."
        g0 = rdf_utils.extractMetadata(c0, self.dataset_template)
        d0 = rdf_utils.buildDict(g0, self.dataset_template, self.vocabulary)
        g1 = rdf_utils.buildGraph(d0, self.dataset_template, self.vocabulary)
        i1 = rdf_utils.fetchUUID(g1)
        c1 = rdf_utils.updateDescription(c0, g1)
        g2 = rdf_utils.extractMetadata(c1, self.dataset_template)
        
        self.assertTrue(isomorphic(g1, g2))

    def test_combinaison_3(self):
        c0 = "Commentaire."
        g0 = rdf_utils.extractMetadata(c0, self.dataset_template)
        d0 = rdf_utils.buildDict(g0, self.dataset_template, self.vocabulary)
        g1 = rdf_utils.buildGraph(d0, self.dataset_template, self.vocabulary)
        i1 = rdf_utils.fetchUUID(g1)
        c1 = rdf_utils.updateDescription(c0, g1)
        g2 = rdf_utils.extractMetadata(c1, self.dataset_template)
        i2 = rdf_utils.fetchUUID(g2)
        d2 = rdf_utils.buildDict(g2, self.dataset_template, self.vocabulary)
        d2.update({
            'dct:description': ["Délimitation simplifiée des départements de France métropolitaine pour représentation à petite échelle, conforme au code officiel géographique (COG) de l'INSEE au 1er janvier de l'année de référence."],
            'dct:provenance / rdfs:label': ["Donnée référentielle produite par l'IGN."],
            'dct:publisher / foaf:name': ["Institut national de l'information géographique et forestière (IGN-F)"],
            'dct:created': ['2020-08-03'],
            'dcat:keyword': ['donnée externe'],
            'dct:modified': ['2021-02-04'],
            'dcat:distribution / dct:accessURL': ['https://geoservices.ign.fr/documentation/diffusion/telechargement-donnees-libres.html#admin-express'],
            'dcat:distribution / dct:issued': ['2021-01-19'],
            'dcat:distribution / dct:licence / rdfs:label': ['Base de données soumise aux conditions de la licence ouverte Etalab.'],
            'dct:accessRights / rdfs:label': ["Aucune restriction d'accès ou d'usage."],
            'dct:title': ['ADMIN EXPRESS - Départements de métropole'],
            'dct:temporal / dcat:startDate': ['2021-01-15'],
            'dct:temporal / dcat:endDate': ['2021-01-15'],
            'dcat:landingPage': ['https://geoservices.ign.fr/ressources_documentaires/Espace_documentaire/BASES_VECTORIELLES/ADMIN_EXPRESS/IGNF_ADMIN_EXPRESS_2-4.html'],
            "<urn:uuid:218c1245-6ba7-4163-841e-476e0d5582af>": ["À mettre à jour !"],
            "dcat:contactPoint / vcard:fn": ["Pôle IG"],
            "dcat:contactPoint / vcard:hasEmail": ["mailto:pig.servicex@developpement-durable.gouv.fr"],
            "dcat:keyword": ["donnée externe", "ign", "admin express"],
            "dcat:theme" : ["Régions et villes", "Données provisoires"]
            })
        g3 = rdf_utils.buildGraph(d2, self.dataset_template, self.vocabulary, datasetUUID = i2)
        i3 = rdf_utils.fetchUUID(g3)
        
        self.assertEqual(i1, i3)
        

    def test_combinaison_4(self):
        c0 = "Commentaire."
        g0 = rdf_utils.extractMetadata(c0, self.dataset_template)
        d0 = rdf_utils.buildDict(g0, self.dataset_template, self.vocabulary)
        g1 = rdf_utils.buildGraph(d0, self.dataset_template, self.vocabulary)
        i1 = rdf_utils.fetchUUID(g1)
        c1 = rdf_utils.updateDescription(c0, g1)
        g2 = rdf_utils.extractMetadata(c1, self.dataset_template)
        i2 = rdf_utils.fetchUUID(g2)
        d2 = rdf_utils.buildDict(g2, self.dataset_template, self.vocabulary)
        d2.update({
            'dct:description': ["Délimitation simplifiée des départements de France métropolitaine pour représentation à petite échelle, conforme au code officiel géographique (COG) de l'INSEE au 1er janvier de l'année de référence."],
            'dct:provenance / rdfs:label': ["Donnée référentielle produite par l'IGN."],
            'dct:publisher / foaf:name': ["Institut national de l'information géographique et forestière (IGN-F)"],
            'dct:created': ['2020-08-03'],
            'dcat:keyword': ['donnée externe'],
            'dct:modified': ['2021-02-04'],
            'dcat:distribution / dct:accessURL': ['https://geoservices.ign.fr/documentation/diffusion/telechargement-donnees-libres.html#admin-express'],
            'dcat:distribution / dct:issued': ['2021-01-19'],
            'dcat:distribution / dct:licence / rdfs:label': ['Base de données soumise aux conditions de la licence ouverte Etalab.'],
            'dct:accessRights / rdfs:label': ["Aucune restriction d'accès ou d'usage."],
            'dct:title': ['ADMIN EXPRESS - Départements de métropole'],
            'dct:temporal / dcat:startDate': ['2021-01-15'],
            'dct:temporal / dcat:endDate': ['2021-01-15'],
            'dcat:landingPage': ['https://geoservices.ign.fr/ressources_documentaires/Espace_documentaire/BASES_VECTORIELLES/ADMIN_EXPRESS/IGNF_ADMIN_EXPRESS_2-4.html'],
            "<urn:uuid:218c1245-6ba7-4163-841e-476e0d5582af>": ["À mettre à jour !"],
            "dcat:contactPoint / vcard:fn": ["Pôle IG"],
            "dcat:contactPoint / vcard:hasEmail": ["mailto:pig.servicex@developpement-durable.gouv.fr"],
            "dcat:keyword": ["donnée externe", "ign", "admin express"],
            "dcat:theme" : ["Régions et villes", "Données provisoires"]
            })
        g3 = rdf_utils.buildGraph(d2, self.dataset_template, self.vocabulary, datasetUUID = i2)
        i3 = rdf_utils.fetchUUID(g3)
        c3 = rdf_utils.updateDescription(c1, g3)
        g4 = rdf_utils.extractMetadata(c3, self.dataset_template)
        
        self.assertTrue(isomorphic(g3, g4))


    def test_combinaison_5(self):
        c0 = "Commentaire."
        g0 = rdf_utils.extractMetadata(c0, self.dataset_template)
        d0 = rdf_utils.buildDict(g0, self.dataset_template, self.vocabulary)
        g1 = rdf_utils.buildGraph(d0, self.dataset_template, self.vocabulary)
        i1 = rdf_utils.fetchUUID(g1)
        c1 = rdf_utils.updateDescription(c0, g1)
        g2 = rdf_utils.extractMetadata(c1, self.dataset_template)
        i2 = rdf_utils.fetchUUID(g2)
        d2 = rdf_utils.buildDict(g2, self.dataset_template, self.vocabulary)
        d2.update({
            'dct:description': ["Délimitation simplifiée des départements de France métropolitaine pour représentation à petite échelle, conforme au code officiel géographique (COG) de l'INSEE au 1er janvier de l'année de référence."],
            'dct:provenance / rdfs:label': ["Donnée référentielle produite par l'IGN."],
            'dct:publisher / foaf:name': ["Institut national de l'information géographique et forestière (IGN-F)"],
            'dct:created': ['2020-08-03'],
            'dcat:keyword': ['donnée externe'],
            'dct:modified': ['2021-02-04'],
            'dcat:distribution / dct:accessURL': ['https://geoservices.ign.fr/documentation/diffusion/telechargement-donnees-libres.html#admin-express'],
            'dcat:distribution / dct:issued': ['2021-01-19'],
            'dcat:distribution / dct:licence / rdfs:label': ['Base de données soumise aux conditions de la licence ouverte Etalab.'],
            'dct:accessRights / rdfs:label': ["Aucune restriction d'accès ou d'usage."],
            'dct:title': ['ADMIN EXPRESS - Départements de métropole'],
            'dct:temporal / dcat:startDate': ['2021-01-15'],
            'dct:temporal / dcat:endDate': ['2021-01-15'],
            'dcat:landingPage': ['https://geoservices.ign.fr/ressources_documentaires/Espace_documentaire/BASES_VECTORIELLES/ADMIN_EXPRESS/IGNF_ADMIN_EXPRESS_2-4.html'],
            "<urn:uuid:218c1245-6ba7-4163-841e-476e0d5582af>": ["À mettre à jour !"],
            "dcat:contactPoint / vcard:fn": ["Pôle IG"],
            "dcat:contactPoint / vcard:hasEmail": ["mailto:pig.servicex@developpement-durable.gouv.fr"],
            "dcat:keyword": ["donnée externe", "ign", "admin express"],
            "dcat:theme" : ["Régions et villes", "Données provisoires"]
            })
        g3 = rdf_utils.buildGraph(d2, self.dataset_template, self.vocabulary, datasetUUID = i2)
        i3 = rdf_utils.fetchUUID(g3)
        c3 = rdf_utils.updateDescription(c1, g3)
        g4 = rdf_utils.extractMetadata(c3, self.dataset_template)
        d4 = rdf_utils.buildDict(g4, self.dataset_template, self.vocabulary)
        
        self.assertEqual(sorted([k + str(sorted(v)) for k, v in d2.items()]),
                         sorted([k + str(sorted(v)) for k, v in d4.items()]))
        

    ### annotations des fonctions

    def test_annotations_buildNSDict_1(self):
        self.assertTrue(all(map(lambda x: not x.annotation is x.empty,
                          signature(rdf_utils.buildNSDict).parameters.values())))

    def test_annotations_buildNSDict_2(self):
        self.assertTrue(not signature(rdf_utils.buildNSDict).return_annotation
                        is signature(rdf_utils.buildNSDict).empty)

    def test_annotations_fetchUUID_1(self):
        self.assertTrue(all(map(lambda x: not x.annotation is x.empty,
                          signature(rdf_utils.fetchUUID).parameters.values())))

    def test_annotations_fetchUUID_2(self):
        self.assertTrue(not signature(rdf_utils.fetchUUID).return_annotation
                        is signature(rdf_utils.fetchUUID).empty)

    def test_annotations_testPath_1(self):
        self.assertTrue(all(map(lambda x: not x.annotation is x.empty,
                          signature(rdf_utils.testPath).parameters.values())))

    def test_annotations_testPath_2(self):
        self.assertTrue(not signature(rdf_utils.testPath).return_annotation
                        is signature(rdf_utils.testPath).empty)

    def test_annotations_fetchValue_1(self):
        self.assertTrue(all(map(lambda x: not x.annotation is x.empty,
                          signature(rdf_utils.fetchValue).parameters.values())))

    def test_annotations_fetchValue_2(self):
        self.assertTrue(not signature(rdf_utils.fetchValue).return_annotation
                        is signature(rdf_utils.fetchValue).empty)

    def test_annotations_fetchType_1(self):
        self.assertTrue(all(map(lambda x: not x.annotation is x.empty,
                          signature(rdf_utils.fetchType).parameters.values())))

    def test_annotations_fetchType_2(self):
        self.assertTrue(not signature(rdf_utils.fetchType).return_annotation
                        is signature(rdf_utils.fetchType).empty)

    def test_annotations_fetchDataType_1(self):
        self.assertTrue(all(map(lambda x: not x.annotation is x.empty,
                          signature(rdf_utils.fetchDataType).parameters.values())))

    def test_annotations_fetchDataType_2(self):
        self.assertTrue(not signature(rdf_utils.fetchDataType).return_annotation
                        is signature(rdf_utils.fetchDataType).empty)

    def test_annotations_fetchVocabulary_1(self):
        self.assertTrue(all(map(lambda x: not x.annotation is x.empty,
                          signature(rdf_utils.fetchVocabulary).parameters.values())))

    def test_annotations_fetchVocabulary_2(self):
        self.assertTrue(not signature(rdf_utils.fetchVocabulary).return_annotation
                        is signature(rdf_utils.fetchVocabulary).empty)

    def test_annotations_fetchConceptFromValue_1(self):
        self.assertTrue(all(map(lambda x: not x.annotation is x.empty,
                          signature(rdf_utils.fetchConceptFromValue).parameters.values())))

    def test_annotations_fetchConceptFromValue_2(self):
        self.assertTrue(not signature(rdf_utils.fetchConceptFromValue).return_annotation
                        is signature(rdf_utils.fetchConceptFromValue).empty)

    def test_annotations_fetchValueFromConcept_1(self):
        self.assertTrue(all(map(lambda x: not x.annotation is x.empty,
                          signature(rdf_utils.fetchValueFromConcept).parameters.values())))

    def test_annotations_fetchValueFromConcept_2(self):
        self.assertTrue(not signature(rdf_utils.fetchValueFromConcept).return_annotation
                        is signature(rdf_utils.fetchValueFromConcept).empty)

    def test_annotations_buildGraph_1(self):
        self.assertTrue(all(map(lambda x: not x.annotation is x.empty,
                          signature(rdf_utils.buildGraph).parameters.values())))

    def test_annotations_buildGraph_2(self):
        self.assertTrue(not signature(rdf_utils.buildGraph).return_annotation
                        is signature(rdf_utils.buildGraph).empty)

    def test_annotations_buildDict_1(self):
        self.assertTrue(all(map(lambda x: not x.annotation is x.empty,
                          signature(rdf_utils.buildDict).parameters.values())))

    def test_annotations_buildDict_2(self):
        self.assertTrue(not signature(rdf_utils.buildDict).return_annotation
                        is signature(rdf_utils.buildDict).empty)

    def test_annotations_extractMetadata_1(self):
        self.assertTrue(all(map(lambda x: not x.annotation is x.empty,
                          signature(rdf_utils.extractMetadata).parameters.values())))

    def test_annotations_extractMetadata_2(self):
        self.assertTrue(not signature(rdf_utils.extractMetadata).return_annotation
                        is signature(rdf_utils.extractMetadata).empty)

    def test_annotations_updateDescription_1(self):
        self.assertTrue(all(map(lambda x: not x.annotation is x.empty,
                          signature(rdf_utils.updateDescription).parameters.values())))

    def test_annotations_updateDescription_2(self):
        self.assertTrue(not signature(rdf_utils.updateDescription).return_annotation
                        is signature(rdf_utils.updateDescription).empty)

unittest.main()
