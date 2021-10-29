"""
Recette de rdf_utils.
"""
from rdflib import Graph, Namespace, Literal, BNode, URIRef
from rdflib.serializer import Serializer
from locale import strxfrm, setlocale, LC_COLLATE
from rdflib.compare import isomorphic
from json.decoder import JSONDecodeError
from inspect import signature
import re, uuid, unittest, json
from pathlib import Path

from plume.bibli_rdf import rdf_utils, __path__
from plume.bibli_rdf.tests.rdf_utils_debug import check_unchanged, \
    populate_widgets, search_keys, check_rows, execute_pseudo_actions, \
    check_hidden_branches, check_buttons


class TestRDFUtils(unittest.TestCase):
    
    def setUp(self):
    
        # import du schéma SHACL qui décrit les métadonnées communes
        with Path(__path__[0] + r'\modeles\shape.ttl').open(encoding='UTF-8') as src:
            self.shape = Graph().parse(data=src.read(), format='turtle')
        self.nsm = self.shape.namespace_manager
        
        # vocabulaire - ontologies utilisées par les métadonnées 
        with Path(__path__[0] + r'\modeles\vocabulary.ttl').open(encoding='UTF-8') as src:
            self.vocabulary = Graph().parse(data=src.read(), format='turtle')
            
        # import d'un exemple de modèle local de formulaire
        with Path(__path__[0] + r'\exemples\exemple_dict_modele_local.json').open(encoding='UTF-8') as src:
            self.template = json.loads(src.read())

        # import d'un exemple de fiche de métadonnée
        with Path(__path__[0] + r'\exemples\exemple_commentaire_pg.txt').open(encoding='UTF-8') as src:
            self.metagraph = rdf_utils.metagraph_from_pg_description(src.read(), self.shape)

        # import d'un exemple de fiche de métadonnée alternative
        with Path(__path__[0] + r'\exemples\exemple_commentaire_pg_2.txt').open(encoding='UTF-8') as src:
            self.metagraph_2 = rdf_utils.metagraph_from_pg_description(src.read(), self.shape)

        # fiche de métadonnées vide
        self.metagraph_empty = rdf_utils.metagraph_from_pg_description("", self.shape)

        # construction d'un dictionnaire de widgets à partir d'un graphe vierge
        self.widgetsdict = rdf_utils.build_dict(
            self.metagraph_empty, self.shape, self.vocabulary,
            translation=True, langList=['fr', 'en', 'it']
            )

        # récupération de quelques clés
        self.lgk = search_keys(self.widgetsdict, 'dct:language', 'edit')[0]
        self.dtk = search_keys(self.widgetsdict, 'dct:type', 'edit')[0]
        self.mdk = search_keys(self.widgetsdict, 'dct:modified', 'edit')[0]
        self.lck = search_keys(self.widgetsdict, 'dcat:distribution / dct:license', 'edit')[0]
        self.lck_m = search_keys(self.widgetsdict, 'dcat:distribution / dct:license', 'group of properties')[0]
        self.lck_m_txt = search_keys(self.widgetsdict, 'dcat:distribution / dct:license / rdfs:label', 'edit')[0]
        self.ttk = search_keys(self.widgetsdict, 'dct:title', 'edit')[0]
        self.ttk_plus = search_keys(self.widgetsdict, 'dct:title', 'translation button')[0]
        self.tck = search_keys(self.widgetsdict, 'dct:temporal', 'group of properties')[0]
        self.tck_plus = search_keys(self.widgetsdict, 'dct:temporal', 'plus button')[0]

        # création de pseudo-widgets
        populate_widgets(self.widgetsdict)


    ### FONCTION export_format_from_extension
    ### -------------------------------------

    def test_export_format_from_extension_1(self):
        l = ['.ttl', '.n3', '.json', '.jsonld', '.xml', '.nt', '.rdf', '.trig']
        for e in l:
            with self.subTest(extension=e):
                self.assertIsNotNone(
                    rdf_utils.export_format_from_extension(e)
                    )

    def test_export_format_from_extension_2(self):
        self.assertEqual(
            rdf_utils.export_format_from_extension('.json'),
            'json-ld'
            )
        self.assertEqual(
            rdf_utils.export_format_from_extension('.rdf'),
            'pretty-xml'
            )
        self.assertIsNone(
            rdf_utils.export_format_from_extension('chose')
            )


    ### FONCTION import_format_from_extension
    ### -------------------------------------

    def test_import_format_from_extension_1(self):
        l = ['.ttl', '.n3', '.json', '.jsonld', '.xml', '.nt', '.rdf', '.trig']
        for e in l:
            with self.subTest(extension=e):
                self.assertIsNotNone(
                    rdf_utils.import_format_from_extension(e)
                    )

    def test_import_format_from_extension_2(self):
        self.assertEqual(
            rdf_utils.import_format_from_extension('.json'),
            'json-ld'
            )
        self.assertEqual(
            rdf_utils.import_format_from_extension('.rdf'),
            'xml'
            )
        self.assertIsNone(
            rdf_utils.import_format_from_extension('chose')
            )


    ### FONCTION import_formats
    ### -----------------------

    def test_import_formats_1(self):
        l = rdf_utils.import_formats()
        lref = ['turtle', 'n3', 'json-ld', 'xml', 'nt', 'trig']
        self.assertEqual(len(l), len(lref))
        for f in lref:
            with self.subTest(format=f):
                self.assertTrue(f in l)


    ### FONCTION import_extensions_from_format
    ### --------------------------

    def test_import_extensions_from_format_1(self):
        lref = ['turtle', 'n3', 'json-ld', 'xml', 'nt', 'trig']
        for f in lref:
            with self.subTest(format=f):
                e = rdf_utils.import_extensions_from_format(f)
                self.assertIsNotNone(e)

    def test_import_extensions_from_format_2(self):
        self.assertEqual(
            rdf_utils.import_extensions_from_format('xml'),
            ['.rdf', '.xml']
            )

    def test_import_extensions_from_format_3(self):
        l = rdf_utils.import_extensions_from_format()
        lref = ['.ttl', '.n3', '.json', '.jsonld', '.xml', '.nt', '.rdf', '.trig']
        self.assertEqual(len(l), len(lref))
        for e in lref:
            with self.subTest(extension=e):
                self.assertTrue(e in l)

    def test_import_extensions_from_format_4(self):
        self.assertEqual(
            rdf_utils.import_extensions_from_format('chose'),
            None
            )


    ### FONCTION export_formats
    ### -----------------------

    def test_export_formats_1(self):
        l = rdf_utils.export_formats()
        lref = ['turtle', 'json-ld', 'xml', 'n3', 'nt', 'pretty-xml', 'trig']
        self.assertEqual(len(l), len(lref))
        for f in lref:
            with self.subTest(format=f):
                self.assertTrue(f in l)

                
    ### FONCTION export_extension_from_format
    ### -------------------------

    def test_export_extension_from_format_1(self):
        lref = ['turtle', 'json-ld', 'xml', 'n3', 'nt', 'pretty-xml', 'trig']
        for f in lref:
            with self.subTest(format=f):
                e = rdf_utils.export_extension_from_format(f)
                self.assertIsNotNone(e)

    def test_export_extension_from_format_2(self):
        self.assertEqual(
            rdf_utils.export_extension_from_format('turtle'),
            '.ttl'
            )

    def test_export_extension_from_format_3(self):
        self.assertEqual(
            rdf_utils.export_extension_from_format('chose'),
            None
            )


    ### FONCTION copy_metagraph
    ### -----------------------

    # récupération de l'identifiant de l'ancien graphe
    def test_copy_metagraph_1(self):
        g_old = Graph()
        g_old.add( (
            URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"),
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            URIRef("http://www.w3.org/ns/dcat#Dataset")
            ) )
        g = Graph()
        g.add( (
            URIRef("urn:uuid:dd4bbc90-ba36-48ee-8840-083a54f87bbc"),
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            URIRef("http://www.w3.org/ns/dcat#Dataset")
            ) )
        g.add( (
            URIRef("urn:uuid:dd4bbc90-ba36-48ee-8840-083a54f87bbc"),
            URIRef("http://purl.org/dc/terms/title"),
            Literal("Mon titre")
            ) )
        gc = rdf_utils.copy_metagraph(g, old_metagraph=g_old)
        self.assertEqual(len(gc), 2)
        self.assertEqual(
            rdf_utils.get_datasetid(gc),
            URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778")
            )
        self.assertTrue( (
            URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"),
            URIRef("http://purl.org/dc/terms/title"),
            Literal("Mon titre")
            ) in gc )

    # récupération de l'identifiant de l'ancien graphe, avec
    # graphe à copier qui ne contient pas de dcat:Dataset
    def test_copy_metagraph_2(self):
        g_old = Graph()
        g_old.add( (
            URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"),
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            URIRef("http://www.w3.org/ns/dcat#Dataset")
            ) )
        g = Graph()
        g.add( (
            URIRef("urn:uuid:dd4bbc90-ba36-48ee-8840-083a54f87bbc"),
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            URIRef("http://xmlns.com/foaf/0.1/Agent")
            ) )
        gc = rdf_utils.copy_metagraph(g, old_metagraph=g_old)
        self.assertEqual(len(gc), 1)
        self.assertEqual(
            rdf_utils.get_datasetid(gc),
            URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778")
            )

    # échec de la récupération de l'identifiant de l'ancien graphe
    # + graphe à copier qui ne contient pas de dcat:Dataset
    # -> graphe vide
    def test_copy_metagraph_3(self):
        g_old = Graph()
        g = Graph()
        g.add( (
            URIRef("urn:uuid:dd4bbc90-ba36-48ee-8840-083a54f87bbc"),
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            URIRef("http://xmlns.com/foaf/0.1/Agent")
            ) )
        gc = rdf_utils.copy_metagraph(g, old_metagraph=g_old)
        self.assertEqual(len(gc), 0)

    # échec de la récupération de l'identifiant de l'ancien graphe
    # et graphe à copier valide -> nouvel identifiant
    def test_copy_metagraph_4(self):
        g_old = Graph()
        g_old.add( (
            URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"),
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            URIRef("http://xmlns.com/foaf/0.1/Agent")
            ) )
        g = Graph()
        g.add( (
            URIRef("urn:uuid:dd4bbc90-ba36-48ee-8840-083a54f87bbc"),
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            URIRef("http://www.w3.org/ns/dcat#Dataset")
            ) )
        g.add( (
            URIRef("urn:uuid:dd4bbc90-ba36-48ee-8840-083a54f87bbc"),
            URIRef("http://purl.org/dc/terms/title"),
            Literal("Mon titre")
            ) )
        gc = rdf_utils.copy_metagraph(g, old_metagraph=g_old)
        self.assertEqual(len(gc), 2)
        u = rdf_utils.get_datasetid(gc)
        self.assertTrue(rdf_utils.is_dataset_uri(u))
        self.assertNotEqual(
            u, URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778")
            )
        self.assertNotEqual(
            u, URIRef("urn:uuid:dd4bbc90-ba36-48ee-8840-083a54f87bbc")
            )

    # copie d'un graphe vide avec récupération de l'identifiant
    def test_copy_metagraph_5(self):
        g_old = Graph()
        g_old.add( (
            URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"),
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            URIRef("http://www.w3.org/ns/dcat#Dataset")
            ) )
        g = Graph()
        gc = rdf_utils.copy_metagraph(g, old_metagraph=g_old)
        self.assertEqual(len(gc), 1)
        self.assertEqual(
            rdf_utils.get_datasetid(gc),
            URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778")
            )

    # graphe à copier valant None
    def test_copy_metagraph_6(self):
        g_old = Graph()
        g_old.add( (
            URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"),
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            URIRef("http://www.w3.org/ns/dcat#Dataset")
            ) )
        g = None
        gc = rdf_utils.copy_metagraph(g, old_metagraph=g_old)
        self.assertEqual(len(gc), 1)
        self.assertEqual(
            rdf_utils.get_datasetid(gc),
            URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778")
            )

  
    ### FONCTION clean_metagraph
    ### ------------------------
    
    # pas un dcat:Dataset
    # la fonction renvoie un graphe vide
    def test_clean_metagraph_1(self):
        g = Graph()
        g.add( (
            URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"),
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            URIRef("http://xmlns.com/foaf/0.1/Agent")
            ) )
        gc = rdf_utils.clean_metagraph(g, self.shape)
        self.assertEqual(len(gc), 0)
   
    # remplacement de l'identifiant
    def test_clean_metagraph_2(self):
        g = Graph()
        g.add( (
            URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"),
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            URIRef("http://www.w3.org/ns/dcat#Dataset")
            ) )
        g.add( (
            URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"),
            URIRef("http://purl.org/dc/terms/title"),
            Literal("Mon titre")
            ) )
        gc = rdf_utils.clean_metagraph(g, self.shape)
        self.assertEqual(len(gc), 2)
        u = rdf_utils.get_datasetid(gc)
        self.assertTrue(rdf_utils.is_dataset_uri(u))
        self.assertNotEqual(
            u, URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778")
            )
        self.assertEqual(
            gc.value(u, URIRef("http://purl.org/dc/terms/title")),
            Literal("Mon titre")
            )
 
    # remplacement des IRI internes par des noeuds vides
    def test_clean_metagraph_3(self):
        g = Graph()
        g.add( (
            URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"),
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            URIRef("http://www.w3.org/ns/dcat#Dataset")
            ) )
        g.add( (
            URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"),
            URIRef("http://www.w3.org/ns/dcat#distribution"),
            URIRef("urn:uuid:dd4bbc90-ba36-48ee-8840-083a54f87bbc")
            ) )
        g.add( (
            URIRef("urn:uuid:dd4bbc90-ba36-48ee-8840-083a54f87bbc"),
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            URIRef("http://www.w3.org/ns/dcat#Distribution")
            ) )
        g.add( (
            URIRef("urn:uuid:dd4bbc90-ba36-48ee-8840-083a54f87bbc"),
            URIRef("http://purl.org/dc/terms/title"),
            Literal("Mon titre de distribution")
            ) )
        gc = rdf_utils.clean_metagraph(g, self.shape)
        self.assertEqual(len(gc), 4)
        u = rdf_utils.get_datasetid(gc)
        b = gc.value(u, URIRef("http://www.w3.org/ns/dcat#distribution"))
        self.assertTrue(isinstance(b, BNode))
        self.assertEqual(
            gc.value(b, URIRef("http://purl.org/dc/terms/title")),
            Literal("Mon titre de distribution")
            )

    # classe non spécifiée (BNode) -> branche éliminée
    def test_clean_metagraph_4(self):
        g = Graph()
        g.add( (
            URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"),
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            URIRef("http://www.w3.org/ns/dcat#Dataset")
            ) )
        b = BNode()
        g.add( (
            URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"),
            URIRef("http://www.w3.org/ns/dcat#distribution"),
            b
            ) )
        g.add( (
            b,
            URIRef("http://purl.org/dc/terms/title"),
            Literal("Mon titre de distribution")
            ) )
        gc = rdf_utils.clean_metagraph(g, self.shape)
        self.assertEqual(len(gc), 1)
        self.assertTrue( (
            None,
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            URIRef("http://www.w3.org/ns/dcat#Dataset")
            ) in gc )

    # classe non spécifiée (IRI) -> branche éliminée, IRI conservée
    def test_clean_metagraph_5(self):
        g = Graph()
        g.add( (
            URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"),
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            URIRef("http://www.w3.org/ns/dcat#Dataset")
            ) )
        g.add( (
            URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"),
            URIRef("http://www.w3.org/ns/dcat#distribution"),
            URIRef("urn:uuid:dd4bbc90-ba36-48ee-8840-083a54f87bbc")
            ) )
        g.add( (
            URIRef("urn:uuid:dd4bbc90-ba36-48ee-8840-083a54f87bbc"),
            URIRef("http://purl.org/dc/terms/title"),
            Literal("Mon titre de distribution")
            ) )
        gc = rdf_utils.clean_metagraph(g, self.shape)
        self.assertEqual(len(gc), 2)
        self.assertTrue( (
            None,
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            URIRef("http://www.w3.org/ns/dcat#Dataset")
            ) in gc )
        self.assertTrue( (
            None,
            URIRef("http://www.w3.org/ns/dcat#distribution"),
            URIRef("urn:uuid:dd4bbc90-ba36-48ee-8840-083a54f87bbc")
            ) in gc )

    # classe non décrite par shape (BNode) -> branche éliminée
    def test_clean_metagraph_6(self):
        g = Graph()
        g.add( (
            URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"),
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            URIRef("http://www.w3.org/ns/dcat#Dataset")
            ) )
        b = BNode()
        g.add( (
            URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"),
            URIRef("http://www.w3.org/ns/dcat#distribution"),
            b
            ) )
        g.add( (
            b,
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            URIRef("http://www.w3.org/ns/dcat#PasUneDistribution")
            ) )
        g.add( (
            b,
            URIRef("http://purl.org/dc/terms/title"),
            Literal("Mon titre de distribution")
            ) )
        gc = rdf_utils.clean_metagraph(g, self.shape)
        self.assertEqual(len(gc), 1)
        self.assertTrue( (
            None,
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            URIRef("http://www.w3.org/ns/dcat#Dataset")
            ) in gc )

    # classe non décrite par shape (IRI) -> branche éliminée, mais
    # l'IRI est conservée
    def test_clean_metagraph_7(self):
        g = Graph()
        g.add( (
            URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"),
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            URIRef("http://www.w3.org/ns/dcat#Dataset")
            ) )
        g.add( (
            URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"),
            URIRef("http://www.w3.org/ns/dcat#distribution"),
            URIRef("urn:uuid:dd4bbc90-ba36-48ee-8840-083a54f87bbc")
            ) )
        g.add( (
            URIRef("urn:uuid:dd4bbc90-ba36-48ee-8840-083a54f87bbc"),
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            URIRef("http://www.w3.org/ns/dcat#PasUneDistribution")
            ) )
        g.add( (
            URIRef("urn:uuid:dd4bbc90-ba36-48ee-8840-083a54f87bbc"),
            URIRef("http://purl.org/dc/terms/title"),
            Literal("Mon titre de distribution")
            ) )
        gc = rdf_utils.clean_metagraph(g, self.shape)
        self.assertEqual(len(gc), 2)
        self.assertTrue( (
            None,
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            URIRef("http://www.w3.org/ns/dcat#Dataset")
            ) in gc )
        self.assertTrue( (
            None,
            URIRef("http://www.w3.org/ns/dcat#distribution"),
            URIRef("urn:uuid:dd4bbc90-ba36-48ee-8840-083a54f87bbc")
            ) in gc )
  
    # noeud vide terminal -> éliminé
    def test_clean_metagraph_8(self):
        g = Graph()
        g.add( (
            URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"),
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            URIRef("http://www.w3.org/ns/dcat#Dataset")
            ) )
        b = BNode()
        g.add( (
            URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"),
            URIRef("http://www.w3.org/ns/dcat#distribution"),
            b
            ) )
        gc = rdf_utils.clean_metagraph(g, self.shape)
        self.assertEqual(len(gc), 1)
        self.assertTrue( (
            None,
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            URIRef("http://www.w3.org/ns/dcat#Dataset")
            ) in gc )

    # récupération de l'identifiant de l'ancien graphe
    def test_clean_metagraph_9(self):
        g_old = Graph()
        g_old.add( (
            URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"),
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            URIRef("http://www.w3.org/ns/dcat#Dataset")
            ) )
        g = Graph()
        g.add( (
            URIRef("urn:uuid:dd4bbc90-ba36-48ee-8840-083a54f87bbc"),
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            URIRef("http://www.w3.org/ns/dcat#Dataset")
            ) )
        g.add( (
            URIRef("urn:uuid:dd4bbc90-ba36-48ee-8840-083a54f87bbc"),
            URIRef("http://purl.org/dc/terms/title"),
            Literal("Mon titre")
            ) )
        gc = rdf_utils.clean_metagraph(g, self.shape, old_metagraph=g_old)
        self.assertEqual(len(gc), 2)
        self.assertEqual(
            rdf_utils.get_datasetid(gc),
            URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778")
            )

    # récupération de l'identifiant de l'ancien graphe, avec
    # graphe importé qui ne contient pas de dcat:Dataset
    def test_clean_metagraph_10(self):
        g_old = Graph()
        g_old.add( (
            URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"),
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            URIRef("http://www.w3.org/ns/dcat#Dataset")
            ) )
        g = Graph()
        g.add( (
            URIRef("urn:uuid:dd4bbc90-ba36-48ee-8840-083a54f87bbc"),
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            URIRef("http://xmlns.com/foaf/0.1/Agent")
            ) )
        gc = rdf_utils.clean_metagraph(g, self.shape, old_metagraph=g_old)
        self.assertEqual(len(gc), 1)
        self.assertEqual(
            rdf_utils.get_datasetid(gc),
            URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778")
            )

    # échec de la récupération de l'identifiant de l'ancien graphe
    # + graphe importé qui ne contient pas de dcat:Dataset
    # -> graphe vide
    def test_clean_metagraph_11(self):
        g_old = Graph()
        g = Graph()
        g.add( (
            URIRef("urn:uuid:dd4bbc90-ba36-48ee-8840-083a54f87bbc"),
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            URIRef("http://xmlns.com/foaf/0.1/Agent")
            ) )
        gc = rdf_utils.clean_metagraph(g, self.shape, old_metagraph=g_old)
        self.assertEqual(len(gc), 0)

    # échec de la récupération de l'identifiant de l'ancien graphe
    # et graphe importé valide -> nouvel identifiant
    def test_clean_metagraph_12(self):
        g_old = Graph()
        g_old.add( (
            URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"),
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            URIRef("http://xmlns.com/foaf/0.1/Agent")
            ) )
        g = Graph()
        g.add( (
            URIRef("urn:uuid:dd4bbc90-ba36-48ee-8840-083a54f87bbc"),
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            URIRef("http://www.w3.org/ns/dcat#Dataset")
            ) )
        g.add( (
            URIRef("urn:uuid:dd4bbc90-ba36-48ee-8840-083a54f87bbc"),
            URIRef("http://purl.org/dc/terms/title"),
            Literal("Mon titre")
            ) )
        gc = rdf_utils.clean_metagraph(g, self.shape, old_metagraph=g_old)
        self.assertEqual(len(gc), 2)
        u = rdf_utils.get_datasetid(gc)
        self.assertTrue(rdf_utils.is_dataset_uri(u))
        self.assertNotEqual(
            u, URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778")
            )
        self.assertNotEqual(
            u, URIRef("urn:uuid:dd4bbc90-ba36-48ee-8840-083a54f87bbc")
            )


    ### FONCTION pick_translation
    ### -------------------------

    def test_pick_translation_1(self):
        l = [
            Literal('a', lang='en'),
            Literal('b', lang='es'),
            Literal('c', lang='fr'),
            Literal('d', lang='de')
            ]
        self.assertEqual(
            rdf_utils.pick_translation(l, 'de'),
            Literal('d', lang='de')
            )
        # pas traduction pour la langue demandée,
        # mais français est dans la liste :
        self.assertEqual(
            rdf_utils.pick_translation(l, 'it'),
            Literal('c', lang='fr')
            )
        l.remove(Literal('c', lang='fr'))
        # pas de traduction et français n'est
        # plus dans la liste :
        self.assertEqual(
            rdf_utils.pick_translation(l, 'it'),
            Literal('a', lang='en')
            )
        

    ### FONCTION uripath_from_sparqlpath
    ### --------------------------------

    def test_uripath_from_sparqlpath_1(self):
        p = rdf_utils.uripath_from_sparqlpath(
            'dct:title',
            self.metagraph.namespace_manager
            )
        s = rdf_utils.get_datasetid(self.metagraph)
        self.assertEqual(
            p, URIRef("http://purl.org/dc/terms/title")
            )
        self.assertIsNotNone(
            self.metagraph.value(s, p)
            )

    def test_uripath_from_sparqlpath_2(self):
        p = rdf_utils.uripath_from_sparqlpath(
            'dcat:distribution / dct:license / rdfs:label',
            self.metagraph.namespace_manager
            )
        s = rdf_utils.get_datasetid(self.metagraph)
        self.assertEqual(
            p,
            URIRef("http://www.w3.org/ns/dcat#distribution") \
                / URIRef("http://purl.org/dc/terms/license") \
                / URIRef("http://www.w3.org/2000/01/rdf-schema#label")
            )
        self.assertIsNotNone(
            self.metagraph.value(s, p)
            )

    def test_uripath_from_sparqlpath_3(self):
        with self.assertRaisesRegex(ValueError, 'not.*valid.*path'):
            rdf_utils.uripath_from_sparqlpath(
                'chose',
                self.metagraph.namespace_manager
                )

    def test_uripath_from_sparqlpath_4(self):
        with self.assertRaisesRegex(ValueError, 'known.*prefix'):
            rdf_utils.uripath_from_sparqlpath(
                'chose:chose',
                self.metagraph.namespace_manager
                )

    def test_uripath_from_sparqlpath_5(self):
        p = rdf_utils.uripath_from_sparqlpath(
            'chose',
            self.metagraph.namespace_manager,
            strict=False
            )
        self.assertIsNone(p)

    def test_uripath_from_sparqlpath_6(self):
        p = rdf_utils.uripath_from_sparqlpath(
            'chose:chose',
            self.metagraph.namespace_manager,
            strict=False
            )
        self.assertIsNone(p)


    ### FONCTION WidgetsDict.retrieve_subject
    ### -------------------------------------

    # appliquée à la racine
    def test_wd_retrieve_subject_1(self):
        parent = (0,)
        child = search_keys(self.widgetsdict, 'dct:title', 'edit')[0]
        subject = self.widgetsdict.retrieve_subject(parent)
        self.assertEqual(
            subject,
            self.widgetsdict[parent]['node']
            )
        self.assertEqual(
            subject,
            self.widgetsdict[child]['subject']
            )

    # appliquée à un groupe de valeurs
    def test_wd_retrieve_subject_2(self):
        parent = search_keys(self.widgetsdict, 'dcat:keyword', 'group of values')[0]
        child = search_keys(self.widgetsdict, 'dcat:keyword', 'edit')[0]
        subject = self.widgetsdict.retrieve_subject(parent)
        self.assertEqual(
            subject,
            self.widgetsdict[(0,)]['node']
            )
        self.assertEqual(
            subject,
            self.widgetsdict[child]['subject']
            )

    # appliquée à un groupe de propriétés autre
    # que la racine
    def test_wd_retrieve_subject_3(self):
        parent = search_keys(self.widgetsdict, 'dcat:distribution', 'group of properties')[0]
        child = search_keys(self.widgetsdict, 'dcat:distribution / dct:issued', 'edit')[0]
        subject = self.widgetsdict.retrieve_subject(parent)
        self.assertEqual(
            subject,
            self.widgetsdict[parent]['node']
            )
        self.assertEqual(
            subject,
            self.widgetsdict[child]['subject']
            )


    ### FONCTION get_geoide_json_uuid
    ### -----------------------------
    
    def test_get_geoide_json_uuid_1(self):
        description = """ /////////////// <GEOIDE>
{
    "business_id": "479fd670-32c5-4ade-a26d-0268b0ce5046",
    "title": "Délimitation des Zones d’Aménagement Concerté (ZAC) de Paris"
}
</GEOIDE> /////////////// """
        self.assertEqual(
            rdf_utils.get_geoide_json_uuid(description),
            "479fd670-32c5-4ade-a26d-0268b0ce5046"
            )

    # pas un UUID valide
    def test_get_geoide_json_uuid_2(self):
        description = """ /////////////// <GEOIDE>
{
    "business_id": "pas-un-uuid",
    "title": "Délimitation des Zones d’Aménagement Concerté (ZAC) de Paris"
}
</GEOIDE> /////////////// """
        self.assertIsNone(
            rdf_utils.get_geoide_json_uuid(description)
            )

    # pas un JSON valide
    def test_get_geoide_json_uuid_3(self):
        description = """ /////////////// <GEOIDE>
{
    "business_id": "479fd670-32c5-4ade-a26d-0268b0ce5046" !
    "title": "Délimitation des Zones d’Aménagement Concerté (ZAC) de Paris"
}
</GEOIDE> /////////////// """
        self.assertIsNone(
            rdf_utils.get_geoide_json_uuid(description)
            )

    # balises manquantes
    def test_get_geoide_json_uuid_4(self):
        description = """ ///////////////
{
    "business_id": "479fd670-32c5-4ade-a26d-0268b0ce5046" !
    "title": "Délimitation des Zones d’Aménagement Concerté (ZAC) de Paris"
}
/////////////// """
        self.assertIsNone(
            rdf_utils.get_geoide_json_uuid(description)
            )


    ### FONCTION WidgetsDict.widget_placement
    ### -------------------------------------
    
    def test_wd_widget_placement_1(self):
        d = self.widgetsdict
        k = search_keys(d, 'dct:title', 'translation group')
        self.assertEqual(
            d.widget_placement(k[0], 'main widget'),
            (0, 0, 1, 2)
            )
        k = search_keys(d, 'dct:description', 'edit')
        self.assertEqual(
            d.widget_placement(k[0], 'main widget'),
            (0, 0, d[k[0]]['row span'], 2)
            )
        self.assertEqual(
            d.widget_placement(k[0], 'language widget'),
            (0, 2, 1, 1)
            )
        self.assertEqual(
            d.widget_placement(k[0], 'minus widget'),
            (0, 3, 1, 1)
            )
        k = search_keys(d, 'dcat:distribution / dct:license', 'edit')
        self.assertEqual(
            d.widget_placement(k[0], 'switch source widget'),
            (d[k[0]]['row'], 2, 1, 1)
            )
        self.assertEqual(
            d.widget_placement(k[0], 'label widget'),
            (d[k[0]]['row'], 0, 1, 1)
            )


    ### FONCTION WidgetsDict.update_value
    ### ---------------------------------

    def test_wd_update_value_1(self):
        k = search_keys(self.widgetsdict, 'dct:title', 'edit')[0]
        self.widgetsdict.update_value(k, 'Mon titre')
        self.assertEqual(self.widgetsdict[k]['value'], 'Mon titre')

    # cas des widgets masqués
    def test_wd_update_value_2(self):
        k = search_keys(self.widgetsdict, 'dct:accessRights / rdfs:label', 'edit')[0]
        self.assertTrue(self.widgetsdict[k]['hidden M'])
        with self.assertRaisesRegex(rdf_utils.ForbiddenOperation, 'hidden'):
            self.widgetsdict.update_value(k, 'not None')
        self.widgetsdict[k]['value'] = 'not None'
        self.widgetsdict.update_value(k, None)
        self.assertIsNone(self.widgetsdict[k]['value'])
        

    ### FONCTION WidgetsDict.group_kind
    ### -------------------------------
    
    def test_wd_group_kind_1(self):
        for k in self.widgetsdict.keys():
            self.assertTrue(self.widgetsdict.group_kind(k) in (
                'group of values', 'group of properties',
                'translation group'
                )
            )


    ### FONCTION export_metagraph
    ### -------------------------

    # on vérifie juste qu'il n'y a pas d'erreur
    # et que la fonction déduit correctement
    # le format et l'extension du fichier, il
    # ne s'agit pas de faire la recette de
    # serialize.
    
    def test_export_metagraph_1(self):
        d = Path(__path__[0] + r'\tests\export')
        for form in (
            "turtle", "json-ld", "xml", "n3", "nt",
            "pretty-xml", "trig"
            ):
            rdf_utils.export_metagraph(
                self.metagraph if not form in ('xml', 'pretty-xml') else Graph(),
                self.shape,
                d / 'test_export_1_{}'.format(form),
                form
                )
        for f in d.iterdir():
            if "export_1" in f.name:
                with self.subTest(file=f.name):
                    self.assertTrue(f.suffix)
                    self.assertIsInstance(
                        rdf_utils.metagraph_from_file(f),
                        Graph
                        )
                # si l'import fonctionne, c'est que le format
                # est probablement cohérent avec l'extension

    def test_export_metagraph_2(self):
        d = Path(__path__[0] + r'\tests\export')
        for ext in (
            "ttl", "n3", "json", "jsonld", "xml",
            "nt", "rdf", "trig"
            ):
            rdf_utils.export_metagraph(
                self.metagraph if not ext in ('xml', 'rdf') else Graph(),
                self.shape,
                d / 'test_export_2_{0}.{0}'.format(ext)
                )
        for f in d.iterdir():
            if "export_2" in f.name:
                with self.subTest(file=f.name):
                    self.assertIsInstance(
                        rdf_utils.metagraph_from_file(f),
                        Graph
                        )
                # si l'import fonctionne, c'est que le format
                # est probablement cohérent avec l'extension

    def test_export_metagraph_3(self):
        d = Path(__path__[0] + r'\tests\export')
        rdf_utils.export_metagraph(
            self.metagraph,
            self.shape,
            d / 'test_export_3_none'
            )
        for f in d.iterdir():
            if "export_3" in f.name:
                self.assertEqual(f.suffix, ".ttl")
                self.assertIsInstance(
                        rdf_utils.metagraph_from_file(f),
                        Graph
                        )
        
        

    ### FONCTION available_formats
    ### -------------------------

    # pas de catégories locales dans un graphe
    # vide, donc xml et pretty-xml devraient
    # être autorisés
    def test_available_format_1(self):
        self.assertTrue(
            'xml' in rdf_utils.available_formats(
                Graph(),
                self.shape
                )
            )
        self.assertTrue(
            'pretty-xml' in rdf_utils.available_formats(
                Graph(),
                self.shape
                )
            )

    # l'exemple contient une catégorie locale, donc
    # la fonction ne doit pas renvoyer xml et
    # pretty-xml
    def test_available_format_2(self):
        self.assertTrue(
            not 'xml' in rdf_utils.available_formats(
                self.metagraph,
                self.shape
                )
            )
        self.assertTrue(
            not 'pretty-xml' in rdf_utils.available_formats(
                self.metagraph,
                self.shape
                )
            )


    ### FONCTION metagraph_from_file
    ### ----------------------------
    
    # prise en charge de différents formats
    def test_metagraph_from_file_1(self):
        p = Path(__path__[0] + r'\tests\samples')
        for f in p.iterdir():
            with self.subTest(file=f.name):
                if f.is_file():
                    g = rdf_utils.metagraph_from_file(f)
                    self.assertTrue(len(g) > 0)
                    gc = rdf_utils.clean_metagraph(g, self.shape)
                    self.assertTrue(len(gc) > 0)
                    
    # NB. trig n'est pas testé à ce stade, l'import
    # semble donner un graphe vide
  

    ### FONCTION build_dict
    ### -------------------

    # informations mises à jour depuis une source externe :
    def test_build_dict_1(self):
        q = self.metagraph.query(
            """
            SELECT
                ?d
            WHERE
                { ?s dct:modified ?d ;
                  a dcat:Dataset . }
            """,
            initNs = {
                'dcat': URIRef('http://www.w3.org/ns/dcat#'),
                'dct': URIRef('http://purl.org/dc/terms/')
                }
            )
        self.assertEqual(len(q), 1)
        for r in q:
            self.assertNotEqual(
                r['d'],
                Literal(
                    '2021-08-31',
                    datatype='http://www.w3.org/2001/XMLSchema#date'
                    )
                )
        d = rdf_utils.build_dict(
            self.metagraph, self.shape, self.vocabulary,
            data = { 'dct:modified' : ['2021-08-31'] }
            )
        b = False
        for k, v in d.items():
            if v['path'] == 'dct:modified':
                self.assertEqual(v['value'], '2021-08-31')
                b = True
        self.assertTrue(b)
        g = d.build_graph(self.vocabulary)
        q = g.query(
            """
            SELECT
                ?d
            WHERE
                { ?s dct:modified ?d ;
                  a dcat:Dataset . }
            """,
            initNs = {
                'dcat': URIRef('http://www.w3.org/ns/dcat#'),
                'dct': URIRef('http://purl.org/dc/terms/')
                }
            )
        self.assertEqual(len(q), 1)
        for r in q:
            self.assertEqual(
                r['d'],
                Literal(
                    '2021-08-31',
                    datatype='http://www.w3.org/2001/XMLSchema#date'
                    )
                )
    
    # informations mises à jour depuis une source externe 
    # + catégorie absente du modèle et editHideUnlisted valant True :
    def test_build_dict_2(self):
        self.assertTrue(not 'dct:modified' in self.template)
        d = rdf_utils.build_dict(
            Graph(), self.shape, self.vocabulary,
            template = self.template, editHideUnlisted=True,
            data = { 'dct:modified' : ['2021-08-31'] }
            )
        b = False
        for k, v in d.items():
            if v['path'] == 'dct:modified':
                self.assertEqual(v['value'], '2021-08-31')
                self.assertIsNone(v['main widget type']) # pas de widget
                b = True
        self.assertTrue(b)
        g = d.build_graph(self.vocabulary)
        q = g.query(
            """
            SELECT
                ?d
            WHERE
                { ?s dct:modified ?d ;
                  a dcat:Dataset . }
            """,
            initNs = {
                'dcat': URIRef('http://www.w3.org/ns/dcat#'),
                'dct': URIRef('http://purl.org/dc/terms/')
                }
            )
        self.assertEqual(len(q), 1)
        for r in q:
            self.assertEqual(
                r['d'],
                Literal(
                    '2021-08-31',
                    datatype='http://www.w3.org/2001/XMLSchema#date'
                    )
                )

    # affichage des traductions selon readOnlyCurrentLanguage
    def test_build_dict_3(self):
        d = rdf_utils.build_dict(
            metagraph=self.metagraph,
            shape=self.shape,
            vocabulary=self.vocabulary,
            translation=True,
            langList=['fr', 'en'],
            language='fr'
            )
        d.add(search_keys(d, 'dct:title', 'translation button')[0])
        l = search_keys(d, 'dct:title', 'edit')
        self.assertEqual(len(l), 2)
        d.update_value(l[0], 'Mon titre')
        self.assertEqual(d[l[0]]['language value'], 'fr')
        d.update_value(l[1], 'My title')
        self.assertEqual(d[l[1]]['language value'], 'en')
        g = d.build_graph(self.vocabulary)
        
        d1 = rdf_utils.build_dict(
            metagraph=g,
            shape=self.shape,
            vocabulary=self.vocabulary,
            mode='read',
            language='en',
            langList=['fr', 'en'],
            readOnlyCurrentLanguage=True
            )
        l = search_keys(d1, 'dct:title', 'edit')
        self.assertEqual(len(l), 2)
        for k in l:
            self.assertTrue(
                d1[k]['language value']=='en' or \
                d1[k]['main widget type'] is None
                )

        d2 = rdf_utils.build_dict(
            metagraph=g,
            shape=self.shape,
            vocabulary=self.vocabulary,
            mode='read',
            language='it',
            langList=['fr', 'en', 'it'],
            readOnlyCurrentLanguage=True
            )
        l = search_keys(d2, 'dct:title', 'edit')
        self.assertEqual(len(l), 2)
        self.assertEqual(
            sum([d2[k]['main widget type'] is not None for k in l]),
            1
            )

        d3 = rdf_utils.build_dict(
            metagraph=g,
            shape=self.shape,
            vocabulary=self.vocabulary,
            mode='read',
            language='fr',
            langList=['fr', 'en'],
            readOnlyCurrentLanguage=False
            )
        l = search_keys(d3, 'dct:title', 'edit')
        self.assertEqual(len(l), 2)
        for k in l:
            self.assertIsNotNone(
                d3[k]['main widget type']
                )

    # consistance de "row" sans template
    def test_build_dict_4(self):
        d = rdf_utils.build_dict(
            metagraph=self.metagraph,
            shape=self.shape,
            vocabulary=self.vocabulary
            )
        e = check_rows(d)
        self.assertIsNone(e)

    # consistance de "row" avec template
    def test_build_dict_5(self):
        d = rdf_utils.build_dict(
            metagraph=self.metagraph,
            shape=self.shape,
            vocabulary=self.vocabulary,
            template=self.template
            )
        e = check_rows(d)
        self.assertIsNone(e)

    # consistance de "row" avec template
    # et editHideUnlisted
    def test_build_dict_6(self):
        d = rdf_utils.build_dict(
            metagraph=self.metagraph,
            shape=self.shape,
            vocabulary=self.vocabulary,
            template=self.template,
            editHideUnlisted=True
            )
        e = check_rows(d)
        self.assertIsNone(e)

    # modification de l'ordre des catégories
    # grâce au template
    def test_build_dict_7(self):
        tck_gv = search_keys(
            self.widgetsdict,
            'dct:temporal',
            'group of values'
            )[0]
        self.assertNotEqual(self.widgetsdict[tck_gv]['row'], 0)
        tck_end = search_keys(
            self.widgetsdict,
            'dct:temporal / dcat:endDate',
            'edit'
            )[0]
        self.assertNotEqual(self.widgetsdict[tck_end]['row'], 0)
        t={
            "dct:temporal": {"order": 1},
            "dct:temporal / dcat:endDate" : {"order": 1}
            }
        d = rdf_utils.build_dict(
            metagraph=Graph(),
            shape=self.shape,
            vocabulary=self.vocabulary,
            template=t
            )
        tck2 = search_keys(
            d,
            'dct:temporal',
            'group of values'
            )[0]
        self.assertEqual(d[tck2]['row'], 0)
        tck2_end = search_keys(
            d,
            'dct:temporal / dcat:endDate',
            'edit'
            )[0]
        self.assertEqual(d[tck2_end]['row'], 0)
        e = check_rows(d)
        self.assertIsNone(e)

    # vérifie qu'en l'absence de thésaurus,
    # les QComboBox deviennent bien des QLineEdit
    def test_build_dict_8(self):
        
        # cas où il n'y a pas de thésaurus
        # dans shape :
        shape2 = rdf_utils.load_shape()
        shape2.update(
            """
            DELETE { ?o snum:ontology ?v }
            WHERE { ?o sh:path dct:accessRights ;
                snum:ontology ?v }
            """
            )
        d = rdf_utils.build_dict(
            metagraph=self.metagraph,
            shape=shape2,
            vocabulary=self.vocabulary
            )
        ark = search_keys(d, "dct:accessRights", 'edit')[0]
        self.assertEqual(d[ark]['main widget type'], 'QLineEdit')
        d = rdf_utils.build_dict(
            metagraph=Graph(),
            shape=shape2,
            vocabulary=self.vocabulary
            )
        ark = search_keys(d, "dct:accessRights", 'edit')[0]
        self.assertEqual(d[ark]['main widget type'], 'QLineEdit')
        
        # cas où l'unique thésaurus n'a pas de vocabulaire associé :
        voc=Graph()
        voc.namespace_manager.bind(
            'skos',
            URIRef('http://www.w3.org/2004/02/skos/core#'),
            override=True, replace=True
            )
        d = rdf_utils.build_dict(
            metagraph=self.metagraph,
            shape=self.shape,
            vocabulary=voc
            )
        ark = search_keys(d, "dct:accessRights", 'edit')[0]
        self.assertEqual(d[ark]['main widget type'], 'QLineEdit')
        dtk = search_keys(d, "dcat:theme", 'edit')[0]
        self.assertEqual(d[dtk]['main widget type'], 'QLineEdit')
        d = rdf_utils.build_dict(
            metagraph=Graph(),
            shape=self.shape,
            vocabulary=voc
            )
        ark = search_keys(d, "dct:accessRights", 'edit')[0]
        self.assertEqual(d[ark]['main widget type'], 'QLineEdit')
        dtk = search_keys(d, "dcat:theme", 'edit')[0]
        self.assertEqual(d[dtk]['main widget type'], 'QLineEdit')

    # modèle de formulaire avec onglets
    def test_build_dict_9(self):
        template = {
            "dct:title":  { "order": 10, "tab name": "Général" },
            "dcat:distribution": { "tab name": "Distribution" },
            "dcat:distribution / dct:issued": {},
            "dcat:distribution / dcat:accessURL": { "tab name": "Autre", "order": 1 },
            "dcat:keyword" : {}
            }
        templateTabs = { "Général" : (0,), "Distribution" : (1,) }
        d = rdf_utils.build_dict(
            metagraph=self.metagraph,
            shape=self.shape,
            vocabulary=self.vocabulary,
            template=template,
            templateTabs=templateTabs
            )
        ttk = search_keys(d, "dct:title", 'edit')[0]
        self.assertTrue(rdf_utils.is_ancestor((0,), ttk))
        kwk = search_keys(d, "dcat:keyword", 'edit')[0]
        self.assertTrue(rdf_utils.is_ancestor((0,), kwk))
        dbk = search_keys(d, "dcat:distribution", 'group of properties')[0]
        self.assertTrue(rdf_utils.is_ancestor((1,), dbk))
        isk = search_keys(d, "dcat:distribution / dct:issued", 'edit')[0]
        self.assertTrue(rdf_utils.is_ancestor((1,), isk))
        self.assertTrue(rdf_utils.is_ancestor(dbk, isk))
        auk = search_keys(d, "dcat:distribution / dcat:accessURL", 'edit')[0]
        self.assertTrue(rdf_utils.is_ancestor((1,), auk))
        self.assertTrue(rdf_utils.is_ancestor(dbk, auk))
        e = check_rows(d)
        self.assertIsNone(e)    


    # génération des tests d'aide sur les boutons
    def test_build_dict_10(self):
        d = rdf_utils.build_dict(
            metagraph=self.metagraph,
            shape=self.shape,
            vocabulary=self.vocabulary,
            translation=True
            )
        for k, v in d.items():
            with self.subTest(key=k):
                if v['object'] == 'translation button':
                    self.assertEqual(v['help text'], 'Ajouter une traduction')
                if v['object'] == 'plus button':
                    self.assertTrue(v['help text'].startswith('Ajouter un élément'))
        

    # contrôle de l'ordre des catégories en multi-onglets
    def test_build_dict_11(self):
        template = {
            "dct:title":  { "order": 10, "tab name": "Général" },
            "dcat:distribution": { "tab name": "Distribution", "order": 1 },
            "dcat:distribution / dct:issued": {},
            "dcat:distribution / dcat:accessURL": {},
            "dct:publisher": { "tab name": "Distribution", "order": 2 },
            "dct:modified": { "tab name": "Distribution" },
            "dcat:keyword" : {},
            "dct:language" : { "tab name": "Distribution", "order": -1 }
            }
        templateTabs = { "Général" : (0,), "Distribution" : (1,) }
        d = rdf_utils.build_dict(
            metagraph=self.metagraph,
            shape=self.shape,
            vocabulary=self.vocabulary,
            template=template,
            templateTabs=templateTabs
            )
        e = check_rows(d)
        self.assertIsNone(e)
        dbk = search_keys(d, "dcat:distribution", 'group of values')[0]
        self.assertEqual(d[dbk[1]]['label'], "Distribution")
        pbk = search_keys(d, "dct:publisher", 'group of properties')[0]
        self.assertEqual(d[pbk[1]]['label'], "Distribution")
        mdk = search_keys(d, "dct:modified", 'edit')[0]
        self.assertEqual(d[mdk[1]]['label'], "Distribution")
        lgk = search_keys(d, "dct:language", 'group of values')[0]
        self.assertEqual(d[lgk[1]]['label'], "Distribution")
        self.assertTrue(d[lgk]['row'] < d[dbk]['row'] < d[pbk]['row'] < d[mdk]['row'])
        

    # métadonnées obligatoires de shape absentes du template
    def test_build_dict_12(self):
        template = {
            "dcat:distribution": { "tab name": "Distribution" },
            "dcat:distribution / dct:issued": {},
            "dcat:distribution / dcat:accessURL": {},
            "dct:publisher": { "tab name": "Distribution" },
            "dct:modified": {},
            "dcat:keyword" : {}
            }
        templateTabs = { "Général" : (0,), "Distribution" : (1,) }
        
        # mode édition sans editHideUnlisted
        # métadonnées présentes dans le graphe
        d = rdf_utils.build_dict(
            metagraph=self.metagraph,
            shape=self.shape,
            vocabulary=self.vocabulary,
            template=template,
            templateTabs=templateTabs,
            editHideUnlisted=False
            )
        e = check_rows(d)
        self.assertIsNone(e)
        ttk = search_keys(d, "dct:title", 'edit')[0]
        self.assertEqual(d[ttk[1]]['label'], "Autres")
        self.assertIsNotNone(d[ttk]['main widget type'])
        dsk = search_keys(d, "dct:description", 'edit')[0]
        self.assertEqual(d[dsk[1]]['label'], "Autres")
        self.assertIsNotNone(d[dsk]['main widget type'])
        
        # mode édition avec editHideUnlisted
        # métadonnées présentes dans le graphe
        d = rdf_utils.build_dict(
            metagraph=self.metagraph,
            shape=self.shape,
            vocabulary=self.vocabulary,
            template=template,
            templateTabs=templateTabs,
            editHideUnlisted=True
            )
        e = check_rows(d)
        self.assertIsNone(e)
        ttk = search_keys(d, "dct:title", 'edit')[0]
        self.assertEqual(d[ttk[1]]['label'], "Autres")
        self.assertIsNotNone(d[ttk]['main widget type'])
        dsk = search_keys(d, "dct:description", 'edit')[0]
        self.assertEqual(d[dsk[1]]['label'], "Autres")
        self.assertIsNotNone(d[dsk]['main widget type'])

        # mode lecture sans readHideUnlisted
        # et avec readHideBlank
        # métadonnées présentes dans le graphe
        d = rdf_utils.build_dict(
            metagraph=self.metagraph,
            shape=self.shape,
            vocabulary=self.vocabulary,
            template=template,
            templateTabs=templateTabs,
            mode='read',
            readHideUnlisted=False,
            readHideBlank=True
            )
        e = check_rows(d, mode='read')
        self.assertIsNone(e)
        ttk = search_keys(d, "dct:title", 'edit')[0]
        self.assertEqual(d[ttk[1]]['label'], "Autres")
        self.assertIsNotNone(d[ttk]['main widget type'])
        dsk = search_keys(d, "dct:description", 'edit')[0]
        self.assertEqual(d[dsk[1]]['label'], "Autres")
        self.assertIsNotNone(d[dsk]['main widget type'])

        # mode lecture avec readHideUnlisted
        # et avec readHideBlank
        # métadonnées présentes dans le graphe
        d = rdf_utils.build_dict(
            metagraph=self.metagraph,
            shape=self.shape,
            vocabulary=self.vocabulary,
            template=template,
            templateTabs=templateTabs,
            mode='read',
            readHideUnlisted=True,
            readHideBlank=True
            )
        e = check_rows(d, mode='read')
        self.assertIsNone(e)
        ttk = search_keys(d, "dct:title", 'edit')[0]
        self.assertEqual(d[ttk[1]]['label'], "Autres")
        self.assertIsNotNone(d[ttk]['main widget type'])
        dsk = search_keys(d, "dct:description", 'edit')[0]
        self.assertEqual(d[dsk[1]]['label'], "Autres")
        self.assertIsNotNone(d[dsk]['main widget type'])

        # mode édition sans editHideUnlisted
        # métadonnées absentes du graphe
        d = rdf_utils.build_dict(
            metagraph=self.metagraph_empty,
            shape=self.shape,
            vocabulary=self.vocabulary,
            template=template,
            templateTabs=templateTabs,
            editHideUnlisted=False
            )
        e = check_rows(d)
        self.assertIsNone(e)
        ttk = search_keys(d, "dct:title", 'edit')[0]
        self.assertEqual(d[ttk[1]]['label'], "Autres")
        self.assertIsNotNone(d[ttk]['main widget type'])
        dsk = search_keys(d, "dct:description", 'edit')[0]
        self.assertEqual(d[dsk[1]]['label'], "Autres")
        self.assertIsNotNone(d[dsk]['main widget type'])
        
        # mode édition avec editHideUnlisted
        # métadonnées absentes du graphe
        d = rdf_utils.build_dict(
            metagraph=self.metagraph_empty,
            shape=self.shape,
            vocabulary=self.vocabulary,
            template=template,
            templateTabs=templateTabs,
            editHideUnlisted=True
            )
        e = check_rows(d)
        self.assertIsNone(e)
        ttk = search_keys(d, "dct:title", 'edit')[0]
        self.assertEqual(d[ttk[1]]['label'], "Autres")
        self.assertIsNotNone(d[ttk]['main widget type'])
        dsk = search_keys(d, "dct:description", 'edit')[0]
        self.assertEqual(d[dsk[1]]['label'], "Autres")
        self.assertIsNotNone(d[dsk]['main widget type'])

        # mode lecture sans readHideUnlisted
        # et avec readHideBlank
        # métadonnées absentes du graphe
        d = rdf_utils.build_dict(
            metagraph=self.metagraph_empty,
            shape=self.shape,
            vocabulary=self.vocabulary,
            template=template,
            templateTabs=templateTabs,
            mode='read',
            readHideUnlisted=False,
            readHideBlank=True
            )
        e = check_rows(d, mode='read')
        self.assertIsNone(e)
        ttk = search_keys(d, "dct:title", 'edit')
        self.assertEqual(ttk, [])
        dsk = search_keys(d, "dct:description", 'edit')
        self.assertEqual(dsk, [])

        # mode lecture avec readHideUnlisted
        # et avec readHideBlank
        # métadonnées absentes du graphe
        d = rdf_utils.build_dict(
            metagraph=self.metagraph_empty,
            shape=self.shape,
            vocabulary=self.vocabulary,
            template=template,
            templateTabs=templateTabs,
            mode='read',
            readHideUnlisted=True,
            readHideBlank=True
            )
        e = check_rows(d, mode='read')
        self.assertIsNone(e)
        ttk = search_keys(d, "dct:title", 'edit')
        self.assertEqual(ttk, [])
        dsk = search_keys(d, "dct:description", 'edit')
        self.assertEqual(dsk, [])

        # mode lecture sans readHideUnlisted
        # et sans readHideBlank
        # métadonnées absentes du graphe
        d = rdf_utils.build_dict(
            metagraph=self.metagraph_empty,
            shape=self.shape,
            vocabulary=self.vocabulary,
            template=template,
            templateTabs=templateTabs,
            mode='read',
            readHideUnlisted=False,
            readHideBlank=False
            )
        e = check_rows(d, mode='read')
        self.assertIsNone(e)
        ttk = search_keys(d, "dct:title", 'edit')
        self.assertEqual(ttk, [])
        dsk = search_keys(d, "dct:description", 'edit')
        self.assertEqual(dsk, [])

        # mode lecture avec readHideUnlisted
        # et sans readHideBlank
        # métadonnées absentes du graphe
        d = rdf_utils.build_dict(
            metagraph=self.metagraph_empty,
            shape=self.shape,
            vocabulary=self.vocabulary,
            template=template,
            templateTabs=templateTabs,
            mode='read',
            readHideUnlisted=True,
            readHideBlank=False
            )
        e = check_rows(d, mode='read')
        self.assertIsNone(e)
        ttk = search_keys(d, "dct:title", 'edit')
        self.assertEqual(ttk, [])
        dsk = search_keys(d, "dct:description", 'edit')
        self.assertEqual(dsk, [])
    

    # avec liste des champs
    def test_build_dict_13(self):
        columns = [
            ("champ 1", "description champ 1"),
            ("champ 2", "description champ 2"),
            ("champ 3", "description champ 3")
            ]
        d = rdf_utils.build_dict(
            metagraph=self.metagraph,
            shape=self.shape,
            vocabulary=self.vocabulary,
            columns=columns
            )
        e = check_rows(d)
        self.assertIsNone(e)
        e = check_buttons(d)
        self.assertIsNone(e)
        clk = search_keys(d, "snum:column", 'edit')
        self.assertEqual(len(clk), 3)
        self.assertEqual(d[clk[0][1]]['label'], "Champs")
        self.assertEqual(d[clk[1]]['label'], "champ 2")
        self.assertEqual(d[clk[1]]['value'], "description champ 2")
        

    # pas de clés réservées à l'édition en mode lecture
    def test_build_dict_14(self):
        d = rdf_utils.build_dict(
            metagraph=self.metagraph,
            shape=self.shape,
            vocabulary=self.vocabulary,
            mode='read'
            )
        e = check_rows(d, mode='read')
        self.assertIsNone(e)
        for k, v in d.items():
            with self.subTest(key=k):
                self.assertIsNone(v['placeholder text'])
                self.assertIsNone(v['input mask'])
                self.assertIsNone(v['is mandatory'])
                self.assertTrue(not v['has minus button'])
                self.assertIsNone(v['hide minus button'])
                self.assertIsNone(v['regex validator pattern'])
                self.assertIsNone(v['regex validator flags'])
                self.assertIsNone(v['type validator'])
                self.assertTrue(not v['multiple sources'])
                self.assertIsNone(v['sources'])

    # idem, avec template
    def test_build_dict_15(self):
        template = {
            "dct:title": { },
            "snum:relevanceScore": {
                'placeholder text': '10.1',
                'input mask': 'xx.x',
                'multiple values': True,
                'is mandatory': True,
                'data type': 'xsd:decimal'
                },
            "uuid:c41423cc-fb59-443f-86f4-72592a4f6778" : {
                'placeholder text': '10.1',
                'input mask': 'xx.x',
                'multiple values': True,
                'is mandatory': True,
                'data type': 'xsd:decimal'
                }
            }
        d = rdf_utils.build_dict(
            metagraph=self.metagraph,
            shape=self.shape,
            vocabulary=self.vocabulary,
            mode='read',
            template=template
            )
        e = check_rows(d, mode='read')
        self.assertIsNone(e)
        for k, v in d.items():
            with self.subTest(key=k):
                self.assertIsNone(v['placeholder text'])
                self.assertIsNone(v['input mask'])
                self.assertIsNone(v['is mandatory'])
                self.assertTrue(not v['has minus button'])
                self.assertIsNone(v['hide minus button'])
                self.assertIsNone(v['regex validator pattern'])
                self.assertIsNone(v['regex validator flags'])
                self.assertIsNone(v['type validator'])
                self.assertTrue(not v['multiple sources'])
                self.assertIsNone(v['sources'])

    # pas d'onglet autre parasite pour les
    # catégories locales non répertoriées en mode
    # lecture avec readHideUnlisted.
    def test_build_dict_16(self):
        d = rdf_utils.build_dict(
            metagraph=self.metagraph,
            shape=self.shape,
            vocabulary=self.vocabulary,
            mode='read',
            readHideUnlisted=True
            )
        e = check_rows(d, mode='read')
        self.assertIsNone(e)
        self.assertFalse(any([(rdf_utils.is_root(k) and v['label'] == "Autres") \
            for k, v in d.items()]))

    # ... mais il est bien là sans readHideUnlisted
    def test_build_dict_17(self):
        d = rdf_utils.build_dict(
            metagraph=self.metagraph,
            shape=self.shape,
            vocabulary=self.vocabulary,
            mode='read',
            readHideUnlisted=False
            )
        e = check_rows(d, mode='read')
        self.assertIsNone(e)
        self.assertTrue(any([(rdf_utils.is_root(k) and v['label'] == "Autres") \
            for k, v in d.items()]))

    # mise à jour de l'identifiant via data
    def test_build_dict_18(self):
        g_id = rdf_utils.get_datasetid(self.metagraph)
        g_title = self.metagraph.value(g_id, URIRef('http://purl.org/dc/terms/title'))
        self.assertIsNotNone(g_title)
        d = rdf_utils.build_dict(
            metagraph=self.metagraph,
            shape=self.shape,
            vocabulary=self.vocabulary,
            data={ "dct:identifier": ["479fd670-32c5-4ade-a26d-0268b0cexxxx"] }
            )
        self.assertIsNone(check_rows(d))
        idk = search_keys(d, 'dct:identifier', 'edit')[0]
        self.assertEqual(
            d[idk]['value'], "479fd670-32c5-4ade-a26d-0268b0cexxxx"
            )
        g1 = d.build_graph(self.vocabulary)
        g1_id = rdf_utils.get_datasetid(g1)
        self.assertEqual(
            rdf_utils.strip_uuid(g1_id),
            "479fd670-32c5-4ade-a26d-0268b0cexxxx"
            )
        g1_title = g1.value(g1_id, URIRef('http://purl.org/dc/terms/title'))
        self.assertEqual(g_title, g1_title)
        j1 = rdf_utils.build_geoide_json(g1)
        self.assertTrue(
            '"business_id": "479fd670-32c5-4ade-a26d-0268b0cexxxx"' in j1
            )

    # idem en mode lecture (même si ça n'a aucun sens
    # puisque l'utilisateur ne pourra pas enregistrer le
    # nouvel identifiant) et avec un template où
    # l'identifiant n'apparait pas
    def test_build_dict_19(self):
        g_id = rdf_utils.get_datasetid(self.metagraph)
        g_title = self.metagraph.value(g_id, URIRef('http://purl.org/dc/terms/title'))
        self.assertIsNotNone(g_title)
        d = rdf_utils.build_dict(
            metagraph=self.metagraph,
            shape=self.shape,
            vocabulary=self.vocabulary,
            mode='read',
            preserve=True,
            readHideUnlisted=True,
            template={ "dcat:keyword": {} },
            data={ "dct:identifier": ["479fd670-32c5-4ade-a26d-0268b0cexxxx"] }
            )
        self.assertIsNone(check_rows(d))
        g1 = d.build_graph(self.vocabulary)
        g1_id = rdf_utils.get_datasetid(g1)
        self.assertEqual(
            rdf_utils.strip_uuid(g1_id),
            "479fd670-32c5-4ade-a26d-0268b0cexxxx"
            )
        g1_title = g1.value(g1_id, URIRef('http://purl.org/dc/terms/title'))
        self.assertEqual(g_title, g1_title)
        j1 = rdf_utils.build_geoide_json(g1)
        self.assertTrue(
            '"business_id": "479fd670-32c5-4ade-a26d-0268b0cexxxx"' in j1
            )

    # utilisation de data pour mettre à jour une propriété
    # dont le chemin est composé
    def test_build_dict_20(self):
        d = rdf_utils.build_dict(
            metagraph=self.metagraph,
            shape=self.shape,
            vocabulary=self.vocabulary,
            data={ "dcat:distribution / dct:license / rdfs:label": ["Ma license"] }
            )
        self.assertIsNone(check_rows(d))
        k = search_keys(d, "dcat:distribution / dct:license / rdfs:label", "edit")[0]
        self.assertEqual(
            d[k]['value'], "Ma license"
            )


    # effacement a posteriori des groupes de propriétés
    # dont toutes les propriétés sont masquées (en mode lecture)
    def test_build_dict_21(self):
        template = {
            "dct:spatial": {},
            "dct:spatial / skos:inScheme": {},
            "dct:spatial / dct:identifier": {}
            }
        d = rdf_utils.build_dict(
            metagraph=self.metagraph_2,
            shape=self.shape,
            vocabulary=self.vocabulary,
            template=template,
            mode='read'
            )
        self.assertIsNone(check_rows(d))
        self.assertIsNone(check_hidden_branches(d))
        bbk = search_keys(d, 'dct:spatial / dcat:bbox', 'edit')[0]
        self.assertIsNone(d[bbk]['main widget type'])
        self.assertEqual(d.count_siblings(bbk, visibleOnly=True), 0)
        self.assertIsNone(d[bbk[1]]['main widget type'])

    # effacement a posteriori des onglets vides
    def test_build_dict_22(self):
        template = {
            "dct:title":  { "tab name": "Général" },
            "geodcat:custodian": { "tab name": "À cacher" },
            "dcat:temporalResolution": { "tab name": "À cacher 2" }
            }
        templateTabs = { "Général" : (0,), "À cacher" : (1,), "À cacher 2" : (2,) }
        d = rdf_utils.build_dict(
            metagraph=self.metagraph,
            shape=self.shape,
            vocabulary=self.vocabulary,
            template=template,
            templateTabs=templateTabs
            )
        self.assertIsNone(check_rows(d))
        self.assertIsNone(d[(1,)]['main widget type'])
        self.assertEqual(d[(2,)]['main widget type'], 'QGroupBox')
        # "geodcat:custodian" a pour objet un noeud vide, donc elle
        # n'est pas affichée même en mode écriture, et par suite
        # l'onglet non plus
        
        d = rdf_utils.build_dict(
            metagraph=self.metagraph,
            shape=self.shape,
            vocabulary=self.vocabulary,
            template=template,
            templateTabs=templateTabs,
            mode='read'
            )
        self.assertIsNone(check_rows(d))
        self.assertIsNone(d[(1,)]['main widget type'])
        self.assertIsNone(d[(2,)]['main widget type'])
        

    # présentation de l'identifiant d'un graphe vide
    # (en mode lecture non, en mode édition oui)
    def test_build_dict_23(self):
        d = rdf_utils.build_dict(
            metagraph=self.metagraph_empty,
            shape=self.shape,
            vocabulary=self.vocabulary,
            mode='read'
            )
        idk = search_keys(d, 'dct:identifier', 'edit')
        self.assertEqual(idk, [])
        d = rdf_utils.build_dict(
            metagraph=self.metagraph_empty,
            shape=self.shape,
            vocabulary=self.vocabulary,
            mode='edit'
            )
        idk = search_keys(d, 'dct:identifier', 'edit')
        self.assertTrue(re.fullmatch('^[a-z0-9-]{36}$', d[idk[0]]['value']))


    # double M non créé, car toutes ses propriétés
    # sont hors template
    def test_build_dict_24(self):
        g = Graph()
        g.add( (
            URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"),
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            URIRef("http://www.w3.org/ns/dcat#Dataset")
            ) )
        g.add( (
            URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"),
            URIRef("http://purl.org/dc/terms/accessRights"),
            URIRef("http://inspire.ec.europa.eu/metadata-codelist/LimitationsOnPublicAccess/noLimitations")
            ) )
        
        # accessRights est dans le modèle, mais aucune des
        # propriétés du noeud vide
        d = rdf_utils.build_dict(g, self.shape, self.vocabulary,
            template={ 'dct:accessRights': {} }, mode='edit')
        k = search_keys(d, 'dct:accessRights', 'edit')[0]
        self.assertIsNotNone(d[k]['main widget type'])
        lkm = search_keys(d, 'dct:accessRights', 'group of properties')
        self.assertEqual(len(lkm), 0)
        self.assertFalse('< manuel >' in d[k]['sources'])
        self.assertIsNone(check_rows(d))
        self.assertIsNone(check_hidden_branches(d))
        self.assertIsNone(check_buttons(d))

        # accessRights n'est même pas dans le modèle
        d = rdf_utils.build_dict(g, self.shape, self.vocabulary,
            template={}, mode='edit')
        k = search_keys(d, 'dct:accessRights', 'edit')[0]
        self.assertIsNotNone(d[k]['main widget type'])
        lkm = search_keys(d, 'dct:accessRights', 'group of properties')
        self.assertEqual(len(lkm), 0)
        self.assertFalse('< manuel >' in d[k]['sources'])
        self.assertIsNone(check_rows(d))
        self.assertIsNone(check_hidden_branches(d))
        self.assertIsNone(check_buttons(d))


    # idem, avec une propriété qui n'admettait qu'une source en
    # plus de < manuel > -> pas de bouton de changement de source
    def test_build_dict_25(self):
        g = Graph()
        g.add( (
            URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"),
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            URIRef("http://www.w3.org/ns/dcat#Dataset")
            ) )
        b = BNode()
        g.add( (
            URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"),
            URIRef("http://www.w3.org/ns/dcat#distribution"),
            b
            ) )
        g.add( (
            b,
            URIRef("http://purl.org/dc/terms/license"),
            URIRef("https://spdx.org/licenses/etalab-2.0")
            ) )
        d = rdf_utils.build_dict(g, self.shape, self.vocabulary,
            template={}, mode='edit')
        k = search_keys(d, 'dcat:distribution / dct:license', 'edit')[0]
        self.assertIsNotNone(d[k]['main widget type'])
        lkm = search_keys(d, 'dct:accessRights', 'group of properties')
        self.assertEqual(len(lkm), 0)
        self.assertFalse('< manuel >' in d[k]['sources'])
        self.assertTrue(not d[k]['multiple sources'])
        self.assertIsNone(check_rows(d))
        self.assertIsNone(check_hidden_branches(d))
        self.assertIsNone(check_buttons(d))


    # propriété multi-source hors template avec valeur manuelle
    def test_build_dict_26(self):
        g = Graph()
        g.add( (
            URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"),
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            URIRef("http://www.w3.org/ns/dcat#Dataset")
            ) )
        b = BNode()
        g.add( (
            URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"),
            URIRef("http://purl.org/dc/terms/accessRights"),
            b
            ) )
        g.add( (
            b,
            URIRef("http://www.w3.org/2000/01/rdf-schema#label"),
            Literal("Mention test.", lang='fr')
            ) )
        
        d = rdf_utils.build_dict(g, self.shape, self.vocabulary,
            template={}, mode='edit')
        k = search_keys(d, 'dct:accessRights', 'edit')[0]
        self.assertIsNotNone(d[k]['main widget type'])
        self.assertIsNone(d[k]['current source'])
        self.assertTrue(d[k]['hidden M'])
        self.assertTrue('< manuel >' in d[k]['sources'])
        km = search_keys(d, 'dct:accessRights', 'group of properties')[0]
        self.assertIsNotNone(d[km]['main widget type'])
        self.assertEqual(d[km]['current source'], '< manuel >')
        self.assertTrue(not d[km]['hidden M'])
        self.assertTrue('< manuel >' in d[km]['sources'])
        self.assertIsNone(check_rows(d))
        self.assertIsNone(check_hidden_branches(d))
        self.assertIsNone(check_buttons(d))
    
    # à compléter !


    ### FONCTION WidgetsDict.change_source
    ### ----------------------------------

    # passage en mode manuel
    def test_wd_change_source_1(self):
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        s = [x for x in d[self.lck]['sources'] if x != '< manuel >'][0]
        
        d.update_value(self.lck, "https://ma_licence")
        self.assertTrue(d[self.lck_m]['hidden M'])
        self.assertTrue(d[self.lck_m_txt]['hidden M'])
        self.assertFalse(d[self.lck]['hidden M'])
        self.assertEqual(d[self.lck]['current source'], s)
        self.assertIsNone(d[self.lck_m]['current source'])
        
        c = d.change_source(self.lck, '< manuel >')
        self.assertEqual(
            sorted(c["widgets to hide"]),
            [
                d[self.lck]['label widget'],
                d[self.lck]['main widget'],
                d[self.lck]['switch source widget']
            ]
            )
        self.assertTrue(
            d[self.lck_m]['main widget'] in c["widgets to show"]
            )
        self.assertTrue(
            d[self.lck_m]['switch source widget'] in c["widgets to show"]
            )
        self.assertTrue(
            d[self.lck_m_txt]['main widget'] in c["widgets to show"]
            )
        self.assertEqual(c["switch source menu to update"], [self.lck_m])
        self.assertEqual(c["widgets to empty"], [d[self.lck]['main widget']])
        self.assertEqual(c["concepts list to update"], [])
        
        self.assertFalse(d[self.lck_m]['hidden M'])
        self.assertFalse(d[self.lck_m_txt]['hidden M'])
        self.assertTrue(d[self.lck]['hidden M'])
        self.assertIsNone(d[self.lck]['value'])
        self.assertEqual(d[self.lck_m]['current source'], '< manuel >')
        self.assertIsNone(d[self.lck]['current source'])
        
        d.update_value(self.lck_m_txt, "Non vide")
        c = d.change_source(self.lck_m, s)
        self.assertEqual(
            sorted(c["widgets to show"]),
            [
                d[self.lck]['label widget'],
                d[self.lck]['main widget'],
                d[self.lck]['switch source widget']
            ]
            )
        self.assertTrue(
            d[self.lck_m]['main widget'] in c["widgets to hide"]
            )
        self.assertTrue(
            d[self.lck_m]['switch source widget'] in c["widgets to hide"]
            )
        self.assertTrue(
            d[self.lck_m_txt]['main widget'] in c["widgets to hide"]
            )
        self.assertEqual(c["switch source menu to update"], [self.lck])
        self.assertEqual(c["widgets to empty"], [])
        if d[self.lck]['current source'] == '< URI >':
            self.assertEqual(c["concepts list to update"], [])
        else:
            self.assertEqual(c["concepts list to update"], [self.lck])
        self.assertTrue(d[self.lck_m]['hidden M'])
        self.assertTrue(d[self.lck_m_txt]['hidden M'])
        self.assertEqual(d[self.lck_m_txt]['value'], "Non vide")
        self.assertFalse(d[self.lck]['hidden M'])
        self.assertIsNone(d[self.lck]['value'])
        self.assertEqual(d[self.lck]['current source'], s)
        self.assertIsNone(d[self.lck_m]['current source'])

    # propriété hors template,
    # avec valeur d'origine manuelle (sinon < manuel > ne sera
    # même pas dans la liste des sources)
    def test_wd_change_source_2(self):
        g = Graph()
        g.add( (
            URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"),
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            URIRef("http://www.w3.org/ns/dcat#Dataset")
            ) )
        b = BNode()
        g.add( (
            URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"),
            URIRef("http://purl.org/dc/terms/accessRights"),
            b
            ) )
        g.add( (
            b,
            URIRef("http://www.w3.org/2000/01/rdf-schema#label"),
            Literal("Mention test.", lang='fr')
            ) )
        d = rdf_utils.build_dict(g, self.shape, self.vocabulary,
            template={}, mode='edit')
        populate_widgets(d)
        self.assertIsNone(check_rows(d, populated=True))
        self.assertIsNone(check_hidden_branches(d, populated=True))
        self.assertIsNone(check_buttons(d, populated=True))
        k = search_keys(d, 'dct:accessRights', 'group of properties')[0]
        
        a = d.change_source(k, "Droits d'accès (UE)")
        execute_pseudo_actions(d, a)
        self.assertIsNone(check_rows(d, populated=True))
        self.assertIsNone(check_hidden_branches(d, populated=True))
        self.assertIsNone(check_buttons(d, populated=True))       

    # changement de thésaurus

    # ancienne source non référencée

    # source inconnue

    # la source ne change pas


    ### FONCTION WidgetsDict.order_keys
    ### -------------------------------
    
    # groupe de valeurs
    def test_wd_order_keys_1(self):
        self.assertEqual(self.widgetsdict.order_keys(self.tck[1]), [9999])
   
    # bouton plus
    def test_wd_order_keys_2(self):
        self.assertEqual(self.widgetsdict.order_keys(self.tck_plus), [9999])
    
    # groupe de traduction
    def test_wd_order_keys_3(self):
        self.assertEqual(self.widgetsdict.order_keys(self.ttk[1]), [9999])

    # bouton de traduction
    def test_wd_order_keys_4(self):
        self.assertEqual(self.widgetsdict.order_keys(self.ttk_plus), [9999])
    
    # groupe de propriétés masqué
    def test_wd_order_keys_5(self):
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        d.change_source(self.lck, '< manuel >')
        d.update_value(self.lck_m_txt, "Non vide")
        d.change_source(self.lck_m, 'Licences admises pour les informations publiques des administrations françaises')
        self.assertEqual(self.widgetsdict.order_keys(self.lck_m_txt), [9999])
    
    # groupe de propriétés non masqué
    def test_wd_order_keys_6(self):
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        d.change_source(self.lck, '< manuel >')
        d.update_value(self.lck_m_txt, "Non vide")
        self.assertEqual(
            self.widgetsdict.order_keys(self.lck_m_txt)[0], 0)
   
    # widget de saisie non vide, non masqué
    
    # widget de saisie ''
    
    # widget de saisie None
    
    # widget de saisie masqué


    ### FONCTION WidgetsDict.build_graph
    ### --------------------------------

    def test_wd_build_graph_1(self):
        self.assertTrue(
            check_unchanged(
                self.metagraph, self.shape, self.vocabulary
                )
            )
            
    def test_wd_build_graph_2(self):
        self.assertTrue(
            check_unchanged(
                self.metagraph, self.shape, self.vocabulary, mode='read',
                preserve=True
                )
            )
            
    def test_wd_build_graph_3(self):
        self.assertTrue(
            check_unchanged(
                self.metagraph, self.shape, self.vocabulary, language='en',
                readOnlyCurrentLanguage=True, mode='read', preserve=True
                )
            )

    # avec template et onglets
    def test_wd_build_graph_4(self):
        template = {
            "dct:title":  { "order": 10, "tab name": "Général" },
            "dcat:distribution": { "tab name": "Distribution" },
            "dcat:distribution / dct:issued": {},
            "dcat:distribution / dcat:accessURL": { "tab name": "Autre", "order": 1 },
            "dcat:keyword" : {}
            }
        templateTabs = { "Général" : (0,), "Distribution" : (1,) }
        self.assertTrue(
            check_unchanged(
                self.metagraph, self.shape, self.vocabulary, template=template,
                templateTabs=templateTabs
                )
            )

    # avec liste des champs
    def test_wd_build_graph_5(self):
        columns = [
            ("champ 1", "description champ 1"),
            ("champ 2", "description champ 2"),
            ("champ 3", "description champ 3")
            ]
        self.assertTrue(
            check_unchanged(
                self.metagraph, self.shape, self.vocabulary, columns=columns
                )
            )

    # avec liste des champs et template
    def test_wd_build_graph_6(self):
        template = {
            "dct:title":  { "order": 10, "tab name": "Général" },
            "dcat:distribution": { "tab name": "Distribution" },
            "dcat:distribution / dct:issued": {},
            "dcat:distribution / dcat:accessURL": { "tab name": "Autre", "order": 1 },
            "dcat:keyword" : {}
            }
        columns = [
            ("champ 1", "description champ 1"),
            ("champ 2", "description champ 2"),
            ("champ 3", "description champ 3")
            ]
        templateTabs = { "Général" : (0,), "Distribution" : (1,) }
        self.assertTrue(
            check_unchanged(
                self.metagraph, self.shape, self.vocabulary, template=template,
                templateTabs=templateTabs, columns=columns
                )
            )

    # avec template vide
    def test_wd_build_graph_7(self):
        self.assertTrue(
            check_unchanged(
                self.metagraph, self.shape, self.vocabulary, template={}
                )
            )
        self.assertTrue(
            check_unchanged(
                self.metagraph, self.shape, self.vocabulary, template={},
                mode = 'read', preserve = True
                )
            )
    
    # à compléter !


    ### FONCTION forbidden_char
    ### -----------------------

    def test_forbidden_char_1(self):
        for c in r'<>" {}|\^`':
            with self.subTest(char=c):
                self.assertEqual(rdf_utils.forbidden_char(c), c)

    def test_forbidden_char_2(self):
        for c in "abcdefghijklmnopqrstuvwxyz" \
                 "ABCDEFGHIJKLMNOPQRSTUVWXYZ" \
                 "1234567890/#%":
            with self.subTest(char=c):
                self.assertIsNone(rdf_utils.forbidden_char(c))


    ### FONCTION WidgetsDict.replace_uuid
    ### ---------------------------------

    def test_wd_replace_uuid_1(self):
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        d.replace_uuid("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778")
        g = d.build_graph(self.vocabulary)
        l_id = [s for s in g.subjects(
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            URIRef('http://www.w3.org/ns/dcat#Dataset')
            )]
        self.assertEqual(len(l_id), 1)
        for i in l_id:
            with self.subTest(uuid=str(i)):
                self.assertEqual(
                    i, URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778")
                    )

    def test_wd_replace_uuid_2(self):
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        d.replace_uuid("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778")
        idk = search_keys(d, "dct:identifier", "edit")
        self.assertEqual(
            d[idk[0]]['value'], "c41423cc-fb59-443f-86f4-72592a4f6778"
            )
        g = d.build_graph(self.vocabulary)
        self.assertEqual(
            g.value(
                URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"),
                URIRef("http://purl.org/dc/terms/identifier")
                ),
            Literal("c41423cc-fb59-443f-86f4-72592a4f6778")
            )
    

    ### FONCTIONS WidgetsDict.add et WidgetsDict.drop
    ### ---------------------------------------------

    def test_wd_drop_1(self):
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        with self.assertRaisesRegex(rdf_utils.ForbiddenOperation, 'outside.of.a.group'):
            d.drop(self.mdk)        

    def test_wd_drop_2(self):
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        with self.assertRaisesRegex(rdf_utils.ForbiddenOperation, 'last.of.its.kind'):
            d.drop(self.tck)

    def test_wd_drop_3(self):
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        with self.assertRaisesRegex(rdf_utils.ForbiddenOperation, 'root'):
            d.drop((0,))

    def test_wd_add_1(self):
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        with self.assertRaisesRegex(rdf_utils.ForbiddenOperation, 'root'):
            d.add((0,))

    def test_wd_add_2(self):
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        with self.assertRaisesRegex(ValueError, 'plus.button'):
            d.add(self.lgk)

    def test_wd_add_3(self):
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        d.add(self.ttk_plus)
        d.add(self.ttk_plus)
        # trois langues, donc trois traductions max et
        # le bouton de traduction disparaît
        with self.assertRaisesRegex(rdf_utils.ForbiddenOperation, 'hidden.button'):
            d.add(self.ttk_plus)

    # ajout d'un groupe de propriétés
    def test_wd_add_4(self):
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        dbk_plus = search_keys(d, "dcat:distribution", 'plus button')[0]
        a = d.add(dbk_plus)
        llck_label = search_keys(d, "dcat:distribution / dct:license / rdfs:label", 'edit')
        self.assertEqual(len(llck_label), 2)
        llck_uri = search_keys(d, "dcat:distribution / dct:license", 'edit')
        self.assertEqual(len(llck_uri), 2)
        self.assertEqual(
            d[llck_uri[0]]['hidden M'],
            d[llck_uri[1]]['hidden M']
            )
        self.assertEqual(
            d[llck_uri[0]]['hidden M'],
            not d[(llck_uri[0][0], llck_uri[0][1], 'M')]['hidden M']
            )
        self.assertEqual(
            d[llck_uri[0]]['hidden M'],
            not d[llck_label[0]]['hidden M']
            )
        self.assertEqual(
            d[llck_uri[0]]['hidden M'],
            not d[(llck_uri[1][0], llck_uri[1][1], 'M')]['hidden M']
            )
        self.assertEqual(
            d[llck_uri[0]]['hidden M'],
            not d[llck_label[1]]['hidden M']
            )
        self.assertIsNone(check_hidden_branches(d))
        execute_pseudo_actions(d, a)
        self.assertIsNone(check_hidden_branches(d, populated=True))
        

    # ajout d'un groupe de propriétés + sauvegarde
    def test_wd_add_5(self):
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        dbk_plus = search_keys(d, "dcat:distribution", 'plus button')[0]
        a = d.add(dbk_plus)
        execute_pseudo_actions(d, a)
        self.assertIsNone(check_buttons(d, populated=True))
        self.assertIsNone(check_rows(d, populated=True))
        self.assertIsNone(check_hidden_branches(d, populated=True))
        # on implémente des valeurs pour que les deux distributions
        # soient enregistrées :
        for k in search_keys(d, "dcat:distribution / dcat:accessURL", 'edit'):
            d.update_value(k, "http://url")   
        g = d.build_graph(self.vocabulary)
        d2 = rdf_utils.build_dict(g, self.shape, self.vocabulary)
        # et on est bien supposé retrouver deux distributions différentes :
        self.assertEqual(
            len(search_keys(d, "dcat:distribution", 'group of properties')), 2
            )

    # ajout/suppression d'une traduction
    # contrôle du résultat dans le dictionnaire de widgets
    def test_wd_add_drop_1(self):
        d = rdf_utils.build_dict(
            Graph(), self.shape, self.vocabulary,
            translation=True, langList=['fr', 'en']
            )
        d.add(self.ttk_plus)
        e = check_rows(d)
        self.assertIsNone(e)
        lttk2 = search_keys(d, 'dct:title', 'edit')
        self.assertEqual(len(lttk2), 2)
        self.assertNotEqual(
            d[lttk2[0]]['language value'],
            d[lttk2[1]]['language value']
            )
        self.assertEqual(
            d[lttk2[0]]['authorized languages'],
            [ d[lttk2[0]]['language value'] ]
            )
        self.assertEqual(
            d[lttk2[1]]['authorized languages'],
            [ d[lttk2[1]]['language value'] ]
            )       
        d.drop(lttk2[1])
        e = check_rows(d)
        self.assertIsNone(e)
        lttk2 = search_keys(d, 'dct:title', 'edit')
        self.assertEqual(len(lttk2), 1)
        self.assertEqual(
            len(d[lttk2[0]]['authorized languages']),
            2
            )

    # ajout/suppression d'un widget de saisie
    # occupant plusieurs lignes
    def test_wd_add_drop_2(self):
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        dsk_plus = search_keys(d, 'dct:description', 'translation button')[0]
        d.add(dsk_plus)
        e = check_rows(d)
        self.assertIsNone(e)
        ldsk = search_keys(d, 'dct:description', 'edit')
        self.assertEqual(len(ldsk), 2)
        self.assertEqual(d[ldsk[0]]['row'], 0)
        self.assertEqual(d[ldsk[1]]['row'], d[ldsk[0]]['row span'])
        self.assertEqual(d[ldsk[1]]['row span'], d[ldsk[0]]['row span'])
        self.assertEqual(d[dsk_plus]['row'], 2 * d[ldsk[0]]['row span'])
              
        d.drop(ldsk[0])
        e = check_rows(d)
        self.assertIsNone(e)
        self.assertEqual(d[ldsk[1]]['row'], 0)
        self.assertEqual(d[dsk_plus]['row'], d[ldsk[1]]['row span'])

    # ajout/suppression de widgets dans
    # un groupe de valeurs
    def test_wd_add_drop_3(self):
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        kwk_plus = search_keys(d, 'dcat:keyword', 'plus button')[0]
        d.add(kwk_plus)
        d.add(kwk_plus)
        e = check_rows(d)
        self.assertIsNone(e)
        lkwk = search_keys(d, 'dcat:keyword', 'edit')
        self.assertEqual(len(lkwk), 3)
        self.assertEqual(sorted([d[lkwk[0]]['row'], d[lkwk[1]]['row'], d[lkwk[2]]['row']]), [0, 1, 2])
        self.assertEqual(d[kwk_plus]['row'], 3)

        d.drop(lkwk[1])
        e = check_rows(d)
        self.assertIsNone(e)
        lkwk = search_keys(d, 'dcat:keyword', 'edit')
        self.assertEqual(len(lkwk), 2)
        self.assertEqual(sorted([d[lkwk[0]]['row'], d[lkwk[1]]['row']]), [0, 1])
        self.assertEqual(d[kwk_plus]['row'], 2)

    # ajout/suppression de groupes de propriétés
    def test_wd_add_drop_4(self):
        d = self.widgetsdict
        dbk_plus = search_keys(d, "dcat:distribution", 'plus button')[0]
        d.add(dbk_plus)
        d.add(dbk_plus)
        e = check_rows(d)
        self.assertIsNone(e)
        ldbk = search_keys(d, 'dcat:distribution', 'group of properties')
        self.assertEqual(len(ldbk), 3)
        self.assertEqual(sorted([d[ldbk[0]]['row'], d[ldbk[1]]['row'], d[ldbk[2]]['row']]), [0, 1, 2])
        self.assertEqual(d[dbk_plus]['row'], 3)

        d.drop(ldbk[1])
        e = check_rows(d)
        self.assertIsNone(e)
        ldbk = search_keys(d, 'dcat:distribution', 'group of properties')
        self.assertEqual(len(ldbk), 2)
        self.assertEqual(sorted([d[ldbk[0]]['row'], d[ldbk[1]]['row']]), [0, 1])
        self.assertEqual(d[dbk_plus]['row'], 2)

    # ajout/suppression de groupes de propriétés
    # dans un onglet qui n'est pas (0,)
    def test_wd_add_drop_5(self):
        template = {
            "dct:title":  { "order": 10, "tab name": "Général" },
            "dcat:distribution": { "tab name": "Distribution" },
            "dcat:distribution / dct:issued": {},
            "dcat:distribution / dcat:accessURL": { "tab name": "Autre", "order": 1 },
            "dcat:keyword" : {}
            }
        templateTabs = { "Général" : (0,), "Distribution" : (1,) }
        d = rdf_utils.build_dict(
            metagraph=self.metagraph,
            shape=self.shape,
            vocabulary=self.vocabulary,
            template=template,
            templateTabs=templateTabs
            )
        dbk_plus = search_keys(d, "dcat:distribution", 'plus button')[0]
        d.add(dbk_plus)
        d.add(dbk_plus)
        e = check_rows(d)
        self.assertIsNone(e)
        ldbk = search_keys(d, 'dcat:distribution', 'group of properties')
        self.assertEqual(len(ldbk), 3)
        self.assertEqual(sorted([d[ldbk[0]]['row'], d[ldbk[1]]['row'], d[ldbk[2]]['row']]), [0, 1, 2])
        self.assertEqual(d[dbk_plus]['row'], 3)

        d.drop(ldbk[1])
        e = check_rows(d)
        self.assertIsNone(e)
        ldbk = search_keys(d, 'dcat:distribution', 'group of properties')
        self.assertEqual(len(ldbk), 2)
        self.assertEqual(sorted([d[ldbk[0]]['row'], d[ldbk[1]]['row']]), [0, 1])
        self.assertEqual(d[dbk_plus]['row'], 2)

    # opérations sur widgets multi-sources hors template
    def test_wd_add_drop_6(self):
        g = Graph()
        g.add( (
            URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"),
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            URIRef("http://www.w3.org/ns/dcat#Dataset")
            ) )
        g.add( (
            URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"),
            URIRef("http://purl.org/dc/terms/accessRights"),
            URIRef("http://inspire.ec.europa.eu/metadata-codelist/LimitationsOnPublicAccess/noLimitations")
            ) )
        d = rdf_utils.build_dict(g, self.shape, self.vocabulary,
            template={}, mode='edit')
        populate_widgets(d)
        k = search_keys(d, 'dct:accessRights', 'plus button')[0]
        self.assertIsNone(check_rows(d, populated=True))
        self.assertIsNone(check_hidden_branches(d, populated=True))
        self.assertIsNone(check_buttons(d, populated=True))
        lkm = search_keys(d, 'dct:accessRights', 'group of properties')
        self.assertEqual(len(lkm), 0)
        
        a = d.add(k)
        execute_pseudo_actions(d, a)
        self.assertIsNone(check_rows(d, populated=True))
        self.assertIsNone(check_hidden_branches(d, populated=True))
        self.assertIsNone(check_buttons(d, populated=True))
        lk = search_keys(d, 'dct:accessRights', 'edit')
        self.assertEqual(len(lk), 2)
        lkm = search_keys(d, 'dct:accessRights', 'group of properties')
        self.assertEqual(len(lkm), 0)
        
        a = d.drop(lk[0])
        execute_pseudo_actions(d, a)
        self.assertIsNone(check_rows(d, populated=True))
        self.assertIsNone(check_hidden_branches(d, populated=True))
        self.assertIsNone(check_buttons(d, populated=True))
        lk = search_keys(d, 'dct:accessRights', 'edit')
        self.assertEqual(len(lk), 1)


    # propriété hors template,
    # avec valeur d'origine manuelle (sinon < manuel > ne sera
    # même pas dans la liste des sources)
    def test_wd_add_drop_7(self):
        g = Graph()
        g.add( (
            URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"),
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            URIRef("http://www.w3.org/ns/dcat#Dataset")
            ) )
        b = BNode()
        g.add( (
            URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"),
            URIRef("http://purl.org/dc/terms/accessRights"),
            b
            ) )
        g.add( (
            b,
            URIRef("http://www.w3.org/2000/01/rdf-schema#label"),
            Literal("Mention test.", lang='fr')
            ) )
        d = rdf_utils.build_dict(g, self.shape, self.vocabulary,
            template={}, mode='edit')
        populate_widgets(d)
        k = search_keys(d, 'dct:accessRights', 'group of properties')[0]
        a = d.change_source(k, "Droits d'accès (UE)")
        execute_pseudo_actions(d, a)
        # NB : jusque-là, reproduit test_wd_change_source_2, donc on
        # ne fait pas de contrôle du résultat
        k = search_keys(d, 'dct:accessRights', 'plus button')[0]
        a = d.add(k)
        execute_pseudo_actions(d, a)
        self.assertIsNone(check_rows(d, populated=True))
        self.assertIsNone(check_hidden_branches(d, populated=True))
        self.assertIsNone(check_buttons(d, populated=True))
        k = search_keys(d, 'dct:accessRights', 'edit')[0]
        a = d.drop(k)
        execute_pseudo_actions(d, a)
        self.assertIsNone(check_rows(d, populated=True))
        self.assertIsNone(check_hidden_branches(d, populated=True))
        self.assertIsNone(check_buttons(d, populated=True))

    # à compléter !


    ### FONCTION WidgetsDict.change_language
    ### ------------------------------------

    def test_wd_change_language_1(self):
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        
        a = d.add(self.ttk_plus)
        execute_pseudo_actions(d, a)
        self.assertEqual(d[self.ttk]['language value'], 'fr')
        self.assertEqual(d[a["new keys"][0]]['language value'], 'en')
        self.assertEqual(d[self.ttk]['authorized languages'], ['fr', 'it'])
        self.assertEqual(d[a["new keys"][0]]['authorized languages'], ['en', 'it'])
        
        c = d.change_language(a["new keys"][0], 'it')
        self.assertEqual(
            sorted(c["language menu to update"]),
            [self.ttk, a["new keys"][0]]
            )
        self.assertEqual(c["widgets to hide"], [])
        self.assertEqual(d[self.ttk]['language value'], 'fr')
        self.assertEqual(d[a["new keys"][0]]['language value'], 'it')
        self.assertEqual(d[self.ttk]['authorized languages'], ['en', 'fr'])
        self.assertEqual(d[a["new keys"][0]]['authorized languages'], ['en', 'it'])

    def test_wd_change_language_2(self):
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        with self.assertRaisesRegex(rdf_utils.ForbiddenOperation, 'authorized.language'):
            d.change_language(self.ttk, 'es')

    def test_wd_change_language_3(self):
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        with self.assertRaisesRegex(rdf_utils.ForbiddenOperation, 'but.a.string'):
            d.change_language(self.mdk, 'en')

    # la nouvelle langue est identique à l'ancienne :
    def test_wd_change_language_4(self):
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        c = d.change_language(self.ttk, 'fr')
        self.assertEqual(c["language menu to update"], [])
        self.assertEqual(c["widgets to hide"], [])
        
    # cas d'une langue de fait non autorisée :
    def test_wd_change_language_5(self):
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        # modification manuelle de la langue
        d[self.ttk]['language value'] = 'es'
        d[self.ttk]['authorized languages'].append('es')
        d[self.ttk]['authorized languages'].sort()
        
        a1 = d.add(self.ttk_plus)
        execute_pseudo_actions(d, a1)
        self.assertEqual(d[a1["new keys"][0]]['language value'], 'en')
        self.assertEqual(d[a1["new keys"][0]]['authorized languages'], ['en', 'fr', 'it'])
        self.assertEqual(d[self.ttk]['authorized languages'], ['es', 'fr', 'it'])
        a2 = d.add(self.ttk_plus)
        execute_pseudo_actions(d, a2)
        self.assertEqual(d[a2["new keys"][0]]['language value'], 'fr')
        self.assertEqual(d[a2["new keys"][0]]['authorized languages'], ['fr', 'it'])
        self.assertEqual(d[a1["new keys"][0]]['authorized languages'], ['en', 'it'])
        self.assertEqual(d[self.ttk]['authorized languages'], ['es', 'it'])
        
        c = d.change_language(self.ttk, 'it', langList=['en', 'fr', 'it'])
        self.assertEqual(d[self.ttk]['language value'], 'it')
        self.assertEqual(d[a1["new keys"][0]]['language value'], 'en')
        self.assertEqual(d[a2["new keys"][0]]['language value'], 'fr')
        self.assertEqual(d[self.ttk]['authorized languages'], ['it'])
        self.assertEqual(d[a1["new keys"][0]]['authorized languages'], ['en'])
        self.assertEqual(d[a2["new keys"][0]]['authorized languages'], ['fr'])
        self.assertEqual(
            sorted(c["language menu to update"]),
            [self.ttk, a1["new keys"][0], a2["new keys"][0]]
            )
        self.assertEqual(c["widgets to hide"], [d[self.ttk_plus]['main widget']])


    ### FONCTION WidgetsDict.child
    ### --------------------------

    def test_wd_child_1(self):
        self.assertEqual(self.widgetsdict.child((0,))[1], (0,))

    def test_wd_child_2(self):
        self.assertEqual(self.widgetsdict.child(self.tck), (0, self.tck))

    # enfants masqués
    def test_wd_child_3(self):
        g = Graph()
        g.add( (
            URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"),
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            URIRef("http://www.w3.org/ns/dcat#Dataset")
            ) )
        b = BNode()
        g.add( (
            URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"),
            URIRef("http://www.w3.org/ns/dcat#distribution"),
            b
            ) )
        g.add( (
            b,
            URIRef("http://www.w3.org/ns/dcat#accessURL"),
            URIRef("http://mon-url.fr")
            ) )
        g.add( (
            URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778"),
            URIRef("http://purl.org/dc/terms/accessRights"),
            URIRef("http://inspire.ec.europa.eu/metadata-codelist/LimitationsOnPublicAccess/noLimitations")
            ) )
        template = { 'dct:title': {}, 'dct:accessRights': {},
                     'dct:accessRights / rdfs:label': {} }
        d = rdf_utils.build_dict(g, self.shape, self.vocabulary,
            template=template, mode='read')
        k = search_keys(d, 'dcat:distribution', 'group of properties')[0]
        self.assertIsNone(d.child(k))
        self.assertIsNotNone(d.child(k, visibleOnly=False))
        d = rdf_utils.build_dict(g, self.shape, self.vocabulary,
            template=template, mode='edit')
        k = search_keys(d, 'dct:accessRights', 'group of properties')[0]
        self.assertTrue(d[k]['hidden M'])
        self.assertIsNone(d.child(k))
        self.assertIsNotNone(d.child(k, visibleOnly=False))
        

    ### FONCTION WidgetsDict.count_siblings
    ### -----------------------------------

    def test_wd_count_siblings_1(self):
        self.assertEqual(self.widgetsdict.count_siblings((0,)), 0)

    def test_wd_count_siblings_2(self):
        self.assertEqual(self.widgetsdict.count_siblings(self.tck), 1)
        # groupe de propriétés

    def test_wd_count_siblings_3(self):
        self.assertEqual(self.widgetsdict.count_siblings(self.tck, restrict=False), 2)
        # groupe de propriétés + bouton plus

    def test_wd_count_siblings_4(self):
        self.assertEqual(self.widgetsdict.count_siblings((0, self.tck)), 2)
        # widgets de saisie pour dcat:endDate et dcat:startDate


    ### FONCTION WidgetsDict.clean_copy
    ### -------------------------------

    # les clés widgets, actions et menus de la copie sont-elles bien vides ?
    def test_wd_clean_copy_1(self):
        c = self.widgetsdict.clean_copy(self.lgk)
        for k in c.keys():
            with self.subTest(key=k):
                if k.endswith(('widget', 'actions', 'menu')):
                    self.assertIsNone(c[k])

    # la valeur est-elle bien réinitialisée ?
    def test_wd_clean_copy_2(self):
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        d[self.lgk]['value'] = 'italien'
        c = d.clean_copy(self.lgk)
        self.assertEqual(c['value'], 'français')

    # la langue est-elle bien réinitialisée ?
    def test_wd_clean_copy_3(self):
        c = self.widgetsdict.clean_copy(self.ttk, language='en')
        self.assertEqual(c['language value'], 'en')

    # ... mais pas pour les IRI ?
    def test_wd_clean_copy_4(self):
        c = self.widgetsdict.clean_copy(self.lgk, language='en')
        self.assertIsNone(c['language value'])
    

    ### FONCTION is_older
    ### ----------------
    
    def test_is_older_1(self):
        self.assertTrue(rdf_utils.is_older((0, (0,)), (0, (1, (0,)))))
  
    def test_is_older_2(self):
        self.assertFalse(rdf_utils.is_older((0, (0,)), (1, (0,))))
    
    def test_is_older_3(self):
        self.assertFalse(rdf_utils.is_older((0, (1, (0,))), (0, (0,))))
    

    ### FONCTION is_ancestor
    ### -------------------
    
    def test_is_ancestor_1(self):
        self.assertTrue(rdf_utils.is_ancestor((1, (2, (0,))), (8, (1, (2, (0,))))))
    
    def test_is_ancestor_2(self):
        self.assertTrue(rdf_utils.is_ancestor((2, (0,)), (8, (1, (2, (0,))))))

    def test_is_ancestor_3(self):
        self.assertFalse(rdf_utils.is_ancestor((2, (0,)), (8, (1, (3, (0,))))))

    def test_is_ancestor_4(self):
        self.assertFalse(rdf_utils.is_ancestor((8, (1, (2, (0,)))), (2, (0,))))

    def test_is_ancestor_5(self):
        self.assertTrue(rdf_utils.is_ancestor((2, (0,)), (8, (1, (2, (0,))), 'M')))

    def test_is_ancestor_6(self):
        self.assertTrue(rdf_utils.is_ancestor(
            (3, (0, (11, (0,))), 'M'),
            (0, (0, (3, (0, (11, (0,))), 'M')))
            ))
    

    ### FONCTION replace_ancestor
    ### -------------------------
    
    def test_replace_ancestor_1(self):
        with self.assertRaisesRegex(ValueError, 'ancestor'):
            rdf_utils.replace_ancestor((1, (0,)), (2, (0,)), (3, (0,)))

    def test_replace_ancestor_2(self):
        with self.assertRaisesRegex(ValueError, 'generation'):
            rdf_utils.replace_ancestor((2, (1, (0,))), (1, (0,)), (1, (1, (0,))))
   
    def test_replace_ancestor_3(self):
        self.assertEqual(
            rdf_utils.replace_ancestor((1, (2, (3, (0, )))), (3, (0, )), (4, (0, ))),
            (1, (2, (4, (0,))))
            )
    
    def test_replace_ancestor_4(self):
        self.assertEqual(
            rdf_utils.replace_ancestor((1, (2, (3, (0, )))), (2, (3, (0, ))), (3, (3, (0, )))),
            (1, (3, (3, (0,))))
            )
    
    def test_replace_ancestor_5(self):
        self.assertEqual(
            rdf_utils.replace_ancestor((2, (3, (0, )), 'M'), (3, (0, )), (4, (0, ))),
            (2, (4, (0,)), 'M')
            )

    def test_replace_ancestor_7(self):
        with self.assertRaisesRegex(
            rdf_utils.ForbiddenOperation, r'replace\snon[-]M\s'
            ):
            rdf_utils.replace_ancestor((2, (1, (0,))), (1, (0,)), (3, (0, ), 'M'))

    def test_replace_ancestor_8(self):
        with self.assertRaisesRegex(
            rdf_utils.ForbiddenOperation, r'replace\sM\s'
            ):
            rdf_utils.replace_ancestor((2, (1, (0,), 'M')), (1, (0,), 'M'), (3, (0, )))

    def test_replace_ancestor_9(self):
        self.assertEqual(
            rdf_utils.replace_ancestor(
                (0, (2, (0, (0, (1,))), 'M')),
                (0, (0, (1,))),
                (2, (0, (1,)))
                ),
            (0, (2, (2, (0, (1,))), 'M'))
            )

    def test_replace_ancestor_10(self):
        self.assertEqual(
            rdf_utils.replace_ancestor(
                (0, (2, (0, (0, (1,)), 'M'))),
                (0, (0, (1,)), 'M'),
                (2, (0, (1,)), 'M')
                ),
            (0, (2, (2, (0, (1,)), 'M')))
            )
    
    
    ### FONCTION WidgetsDict.parent_widget
    ### ----------------------------------
    
    def test_wd_parent_widget_1(self):
        self.assertEqual(
            self.widgetsdict.parent_widget((0,)),
            None
            )
   
    def test_wd_parent_widget_2(self):
        self.assertEqual(
            self.widgetsdict.parent_widget((0,(0,))),
            ['< (0,) main widget (QGroupBox) >', True, 0, None]
            )


    ### FONCTION WidgetsDict.parent_grid
    ### --------------------------------
    
    def test_wd_parent_1(self):
        self.assertEqual(
            self.widgetsdict.parent_grid((0,)),
            None
            )
   
    def test_wd_parent_2(self):
        self.assertEqual(
            self.widgetsdict.parent_grid((0,(0,))),
            ['< (0,) grid widget (QGridLayout) >', True, None, None]
            )


    ### FONCTION concept_from_value
    ### ---------------------------

    def test_concept_from_value_1(self):
        self.assertEqual(
            rdf_utils.concept_from_value("Domaine public", "Types de licence (UE)", self.vocabulary),
            (URIRef('http://purl.org/adms/licencetype/PublicDomain'), URIRef('http://purl.org/adms/licencetype/1.1'))
            )

    # dans une autre langue :
    def test_concept_from_value_2(self):
        self.assertEqual(
            rdf_utils.concept_from_value("Public domain", "Licence type (EU)", self.vocabulary, language="en"),
            (URIRef('http://purl.org/adms/licencetype/PublicDomain'), URIRef('http://purl.org/adms/licencetype/1.1'))
            )
 
    # sans conceptScheme :
    def test_concept_from_value_3(self):
        self.assertEqual(
            rdf_utils.concept_from_value("Domaine public", None, self.vocabulary),
            (URIRef('http://purl.org/adms/licencetype/PublicDomain'), URIRef('http://purl.org/adms/licencetype/1.1'))
            )

    # conceptScheme inconnu :
    def test_concept_from_value_4(self):
        self.assertEqual(
            rdf_utils.concept_from_value("Domaine public", "N'existe pas", self.vocabulary),
            (None, None)
            )
    
    # concept inconnu :
    def test_concept_from_value_5(self):
        self.assertEqual(
            rdf_utils.concept_from_value("N'existe pas", "Types de licence (UE)", self.vocabulary),
            (None, None)
            )
            
    # langue inconnue :
    def test_concept_from_value_6(self):
        self.assertEqual(
            rdf_utils.concept_from_value("Domaine public", "Types de licence (UE)", self.vocabulary, language='it'),
            (None, None)
            )


    ### FONCTION value_from_concept
    ### ---------------------------
    
    def test_value_from_concept_1(self):
        self.assertEqual(
            rdf_utils.value_from_concept(URIRef('http://purl.org/adms/licencetype/PublicDomain'), self.vocabulary),
            ("Domaine public", "Types de licence (UE)")
            )
    
    # autre langue :
    def test_value_from_concept_2(self):
        self.assertEqual(
            rdf_utils.value_from_concept(URIRef('http://purl.org/adms/licencetype/PublicDomain'), self.vocabulary, language='en'),
            ("Public domain", "Licence type (EU)")
            )
    
    # URI non répertoriée :
    def test_value_from_concept_1(self):
        self.assertEqual(
            rdf_utils.value_from_concept(URIRef('http://purl.org/adms/licencetype/Chose'), self.vocabulary),
            (None, None)
            )
    
    # pas de valeur pour la langue :
    def test_value_from_concept_1(self):
        self.assertEqual(
            rdf_utils.value_from_concept(URIRef('http://purl.org/adms/licencetype/PublicDomain'), self.vocabulary, language='it'),
            ("Domaine public", "Types de licence (UE)")
            )


    ### FONCTION email_from_owlthing
    ### ----------------------------

    def test_email_from_owlthing_1(self):
        self.assertEqual(
            rdf_utils.email_from_owlthing(URIRef("mailto:jon.snow@the-wall.we")),
            'jon.snow@the-wall.we'
            )

    def test_email_from_owlthing_2(self):
        self.assertEqual(
            rdf_utils.email_from_owlthing(URIRef("jon.snow@the-wall.we")),
            'jon.snow@the-wall.we'
            )


    ### FONCTION owlthing_from_email
    ### ----------------------------

    def test_owlthing_from_email_1(self):
        self.assertEqual(
            rdf_utils.owlthing_from_email("jon.snow@the-wall.we"),
            URIRef("mailto:jon.snow@the-wall.we")
            )

    def test_owlthing_from_email_2(self):
        self.assertEqual(
            rdf_utils.owlthing_from_email("mailto:jon.snow@the-wall.we"),
            URIRef("mailto:jon.snow@the-wall.we")
            )

    def test_owlthing_from_email_3(self):
        self.assertRaisesRegex(
            ValueError,
            r"Invalid.IRI.*[']\s[']",
            rdf_utils.owlthing_from_email,
            "xxxx xxxxxxxx"
            )

    def test_owlthing_from_email_4(self):
        self.assertRaisesRegex(
            ValueError,
            r"Invalid.IRI.*['][{][']",
            rdf_utils.owlthing_from_email,
            "xxxx{xxxxxxxx"
            )

    def test_owlthing_from_email_5(self):
        self.assertEqual(
            rdf_utils.owlthing_from_email(""),
            None
            )

    def test_owlthing_from_email_6(self):
        self.assertEqual(
            rdf_utils.owlthing_from_email("mailto:"),
            None
            )
        

    ### FONCTION tel_from_owlthing
    ### --------------------------

    def test_tel_from_owlthing_1(self):
        self.assertEqual(
            rdf_utils.tel_from_owlthing(URIRef("tel:+33-1-23-45-67-89")),
            '+33-1-23-45-67-89'
            )

    def test_tel_from_owlthing_2(self):
        self.assertEqual(
            rdf_utils.tel_from_owlthing(URIRef("+33-1-23-45-67-89")),
            '+33-1-23-45-67-89'
            )

    def test_tel_from_owlthing_3(self):
        self.assertEqual(
            rdf_utils.tel_from_owlthing(URIRef("tel:xxxxxxxxxxxx")),
            'xxxxxxxxxxxx'
            )

    def test_tel_from_owlthing_4(self):
        self.assertEqual(
            rdf_utils.tel_from_owlthing(URIRef("xxxxxxxxxxxx")),
            'xxxxxxxxxxxx'
            )


    ### FONCTION owlthing_from_tel
    ### --------------------------

    def test_owlthing_from_tel_1(self):
        self.assertEqual(
            rdf_utils.owlthing_from_tel("xxxxxxxxxxxx"),
            URIRef("tel:xxxxxxxxxxxx")
            )

    def test_owlthing_from_tel_2(self):
        self.assertEqual(
            rdf_utils.owlthing_from_tel("0123456789"),
            URIRef("tel:+33-1-23-45-67-89")
            )

    def test_owlthing_from_tel_3(self):
        self.assertEqual(
            rdf_utils.owlthing_from_tel("0123456789", False),
            URIRef("tel:0123456789")
            )

    def test_owlthing_from_tel_4(self):
        self.assertEqual(
            rdf_utils.owlthing_from_tel(" 01 23.45-67 89 "),
            URIRef("tel:+33-1-23-45-67-89")
            )

    def test_owlthing_from_tel_5(self):
        self.assertEqual(
            rdf_utils.owlthing_from_tel(" 01 23.45-67 89 ", False),
            URIRef("tel:01-23.45-67-89")
            )

    def test_owlthing_from_tel_6(self):
        self.assertRaisesRegex(
            ValueError,
            r"Invalid.IRI.*[']\s[']",
            rdf_utils.owlthing_from_tel,
            "xxxx xxxxxxxx"
            )

    def test_owlthing_from_tel_7(self):
        self.assertRaisesRegex(
            ValueError,
            r"Invalid.IRI.*['][{][']",
            rdf_utils.owlthing_from_tel,
            "xxxx{xxxxxxxx"
            )

    def test_owlthing_from_tel_8(self):
        self.assertEqual(
            rdf_utils.owlthing_from_tel(""),
            None
            )

    def test_owlthing_from_tel_9(self):
        self.assertEqual(
            rdf_utils.owlthing_from_tel("tel:"),
            None
            )

    def test_owlthing_from_tel_10(self):
        self.assertEqual(
            rdf_utils.owlthing_from_tel("tel:0123456789"),
            URIRef("tel:+33-1-23-45-67-89")
            )


    ### FONCTION metagraph_from_pg_description
    ### --------------------------------------

    def test_metagraph_from_pg_description_1(self):
        c = ""
        self.assertTrue(
            isomorphic(
                rdf_utils.metagraph_from_pg_description(c, self.shape),
                Graph()
                )
            )

    def test_metagraph_from_pg_description_2(self):
        c = "Commentaire sans métadonnées."
        self.assertTrue(
            isomorphic(
                rdf_utils.metagraph_from_pg_description(c, self.shape),
                Graph()
                )
            )

    def test_metagraph_from_pg_description_3(self):
        c = "Commentaire avec métadonnées vides.<METADATA></METADATA>"
        self.assertTrue(
            isomorphic(
                rdf_utils.metagraph_from_pg_description(c, self.shape),
                Graph()
                )
            )

    def test_metagraph_from_pg_description_4(self):
        c = "Commentaire avec métadonnées invalides.<METADATA>Ceci n'est pas un JSON !</METADATA>"
        self.assertRaises(
            JSONDecodeError,
            rdf_utils.metagraph_from_pg_description,
            c,
            self.shape
            )

    def test_metagraph_from_pg_description_5(self):
        c = 'Commentaire avec métadonnées mal structurées.<METADATA>{"name": "Pas un JSON-LD !"}</METADATA>'
        self.assertTrue(
            isomorphic(
                rdf_utils.metagraph_from_pg_description(c, self.shape),
                Graph()
                )
            )

    def test_metagraph_from_pg_description_6(self):
        c = """Commentaire avec métadonnées bien structurées.<METADATA>
[
  {
    "@id": "urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778",
    "@type": [
      "http://www.w3.org/ns/dcat#Dataset"
    ],
    "http://purl.org/dc/terms/identifier": [
      {
        "@value": "c41423cc-fb59-443f-86f4-72592a4f6778"
      }
    ],
    "http://purl.org/dc/terms/modified": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#date",
        "@value": "2020-08-03"
      }
    ]
  }
]
</METADATA>"""
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        d.replace_uuid("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778")
        d[self.mdk]['value'] = "2020-08-03"
        d[self.lgk]['value'] = None
        d[self.dtk]['value'] = None
        g = d.build_graph(self.vocabulary)
        self.assertTrue(
            isomorphic(
                rdf_utils.metagraph_from_pg_description(c, self.shape),
                g
                )
            )


    # les tests 7 à 10 contrôlent la résilience de la fonction face aux
    # anomalies de balisage
    
    def test_metagraph_from_pg_description_7(self):
        c = """<METADATA><METADATA>
[
  {
    "@id": "urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778",
    "@type": [
      "http://www.w3.org/ns/dcat#Dataset"
    ],
    "http://purl.org/dc/terms/identifier": [
      {
        "@value": "c41423cc-fb59-443f-86f4-72592a4f6778"
      }
    ],
    "http://purl.org/dc/terms/modified": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#date",
        "@value": "2020-08-03"
      }
    ]
  }
]
</METADATA>"""
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        d.replace_uuid("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778")
        d[self.mdk]['value'] = "2020-08-03"
        d[self.lgk]['value'] = None
        d[self.dtk]['value'] = None
        g = d.build_graph(self.vocabulary)
        self.assertTrue(
            isomorphic(
                rdf_utils.metagraph_from_pg_description(c, self.shape),
                g
                )
            )

    def test_metagraph_from_pg_description_8(self):
        c = """<METADATA><METADATA>
[
  {
    "@id": "urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778",
    "@type": [
      "http://www.w3.org/ns/dcat#Dataset"
    ],
    "http://purl.org/dc/terms/identifier": [
      {
        "@value": "c41423cc-fb59-443f-86f4-72592a4f6778"
      }
    ],
    "http://purl.org/dc/terms/modified": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#date",
        "@value": "2020-08-03"
      }
    ]
  }
]
</METADATA></METADATA>"""
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        d.replace_uuid("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778")
        d[self.mdk]['value'] = "2020-08-03"
        d[self.lgk]['value'] = None
        d[self.dtk]['value'] = None
        g = d.build_graph(self.vocabulary)
        self.assertTrue(
            isomorphic(
                rdf_utils.metagraph_from_pg_description(c, self.shape),
                g
                )
            )

    def test_metagraph_from_pg_description_9(self):
        c = """<METADATA>
[
  {
    "@id": "urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778",
    "@type": [
      "http://www.w3.org/ns/dcat#Dataset"
    ],
    "http://purl.org/dc/terms/identifier": [
      {
        "@value": "c41423cc-fb59-443f-86f4-72592a4f6778"
      }
    ],
    "http://purl.org/dc/terms/modified": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#date",
        "@value": "2020-08-03"
      }
    ]
  }
]
</METADATA></METADATA>"""
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        d.replace_uuid("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778")
        d[self.mdk]['value'] = "2020-08-03"
        d[self.lgk]['value'] = None
        d[self.dtk]['value'] = None
        g = d.build_graph(self.vocabulary)
        self.assertTrue(
            isomorphic(
                rdf_utils.metagraph_from_pg_description(c, self.shape),
                g
                )
            )
        

    def test_metagraph_from_pg_description_10(self):
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
    "http://purl.org/dc/terms/identifier": [
      {
        "@value": "c41423cc-fb59-443f-86f4-72592a4f6778"
      }
    ],
    "http://purl.org/dc/terms/modified": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#date",
        "@value": "2020-08-03"
      }
    ]
  }
]
</METADATA>"""
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        d.replace_uuid("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778")
        d[self.mdk]['value'] = "2020-08-03"
        d[self.lgk]['value'] = None
        d[self.dtk]['value'] = None
        g = d.build_graph(self.vocabulary)
        self.assertTrue(
            isomorphic(
                rdf_utils.metagraph_from_pg_description(c, self.shape),
                g
                )
            )


    ### FONCTION update_pg_description
    ### ------------------------------

    def test_update_pg_description_1(self):
        c1 = ""
        c2 = """

<METADATA>
[
  {
    "@id": "urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778",
    "@type": [
      "http://www.w3.org/ns/dcat#Dataset"
    ],
    "http://purl.org/dc/terms/identifier": [
      {
        "@value": "c41423cc-fb59-443f-86f4-72592a4f6778"
      }
    ],
    "http://purl.org/dc/terms/modified": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#date",
        "@value": "2020-08-03"
      }
    ]
  }
]
</METADATA>
"""
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        d.replace_uuid("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778")
        d[self.mdk]['value'] = "2020-08-03"
        d[self.lgk]['value'] = None
        d[self.dtk]['value'] = None
        g = d.build_graph(self.vocabulary)
        self.assertEqual(rdf_utils.update_pg_description(c1, g), c2)

    def test_update_pg_description_2(self):
        c1 = "Commentaire."
        c2 = """Commentaire.

<METADATA>
[
  {
    "@id": "urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778",
    "@type": [
      "http://www.w3.org/ns/dcat#Dataset"
    ],
    "http://purl.org/dc/terms/identifier": [
      {
        "@value": "c41423cc-fb59-443f-86f4-72592a4f6778"
      }
    ],
    "http://purl.org/dc/terms/modified": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#date",
        "@value": "2020-08-03"
      }
    ]
  }
]
</METADATA>
"""
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        d.replace_uuid("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778")
        d[self.mdk]['value'] = "2020-08-03"
        d[self.lgk]['value'] = None
        d[self.dtk]['value'] = None
        g = d.build_graph(self.vocabulary)
        self.assertEqual(rdf_utils.update_pg_description(c1, g), c2)

    def test_update_pg_description_3(self):
        c1 = "Commentaire."
        self.assertEqual(rdf_utils.update_pg_description(c1, Graph()), c1)

    def test_update_pg_description_4(self):
        c1 = "Commentaire.<METADATA></METADATA>"
        c2 = """Commentaire.<METADATA>
[
  {
    "@id": "urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778",
    "@type": [
      "http://www.w3.org/ns/dcat#Dataset"
    ],
    "http://purl.org/dc/terms/identifier": [
      {
        "@value": "c41423cc-fb59-443f-86f4-72592a4f6778"
      }
    ],
    "http://purl.org/dc/terms/modified": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#date",
        "@value": "2020-08-03"
      }
    ]
  }
]
</METADATA>"""
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        d.replace_uuid("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778")
        d[self.mdk]['value'] = "2020-08-03"
        d[self.lgk]['value'] = None
        d[self.dtk]['value'] = None
        g = d.build_graph(self.vocabulary)
        self.assertEqual(rdf_utils.update_pg_description(c1, g), c2)

    def test_update_pg_description_5(self):
        c1 = "Commentaire.<METADATA>N'importe quoi !!</METADATA>"
        c2 = """Commentaire.<METADATA>
[
  {
    "@id": "urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778",
    "@type": [
      "http://www.w3.org/ns/dcat#Dataset"
    ],
    "http://purl.org/dc/terms/identifier": [
      {
        "@value": "c41423cc-fb59-443f-86f4-72592a4f6778"
      }
    ],
    "http://purl.org/dc/terms/modified": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#date",
        "@value": "2020-08-03"
      }
    ]
  }
]
</METADATA>"""
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        d.replace_uuid("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778")
        d[self.mdk]['value'] = "2020-08-03"
        d[self.lgk]['value'] = None
        d[self.dtk]['value'] = None
        g = d.build_graph(self.vocabulary)
        self.assertEqual(rdf_utils.update_pg_description(c1, g), c2)

    def test_update_pg_description_6(self):
        c1 = "Commentaire.<METADATA><METADATA>N'importe quoi !!</METADATA>"
        c2 = """Commentaire.<METADATA>
[
  {
    "@id": "urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778",
    "@type": [
      "http://www.w3.org/ns/dcat#Dataset"
    ],
    "http://purl.org/dc/terms/identifier": [
      {
        "@value": "c41423cc-fb59-443f-86f4-72592a4f6778"
      }
    ],
    "http://purl.org/dc/terms/modified": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#date",
        "@value": "2020-08-03"
      }
    ]
  }
]
</METADATA>"""
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        d.replace_uuid("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778")
        d[self.mdk]['value'] = "2020-08-03"
        d[self.lgk]['value'] = None
        d[self.dtk]['value'] = None
        g = d.build_graph(self.vocabulary)
        self.assertEqual(rdf_utils.update_pg_description(c1, g), c2)

    def test_update_pg_description_7(self):
        c1 = "Commentaire.<METADATA><METADATA>N'importe quoi !!</METADATA></METADATA>Suite."
        c2 = """Commentaire.<METADATA>
[
  {
    "@id": "urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778",
    "@type": [
      "http://www.w3.org/ns/dcat#Dataset"
    ],
    "http://purl.org/dc/terms/identifier": [
      {
        "@value": "c41423cc-fb59-443f-86f4-72592a4f6778"
      }
    ],
    "http://purl.org/dc/terms/modified": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#date",
        "@value": "2020-08-03"
      }
    ]
  }
]
</METADATA>Suite."""
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        d.replace_uuid("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778")
        d[self.mdk]['value'] = "2020-08-03"
        d[self.lgk]['value'] = None
        d[self.dtk]['value'] = None
        g = d.build_graph(self.vocabulary)
        self.assertEqual(rdf_utils.update_pg_description(c1, g), c2)

    def test_update_pg_description_8(self):
        c1 = "Commentaire.<METADATA>N'importe quoi !!</METADATA></METADATA>Suite."
        c2 = """Commentaire.<METADATA>
[
  {
    "@id": "urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778",
    "@type": [
      "http://www.w3.org/ns/dcat#Dataset"
    ],
    "http://purl.org/dc/terms/identifier": [
      {
        "@value": "c41423cc-fb59-443f-86f4-72592a4f6778"
      }
    ],
    "http://purl.org/dc/terms/modified": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#date",
        "@value": "2020-08-03"
      }
    ]
  }
]
</METADATA>Suite."""
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        d.replace_uuid("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778")
        d[self.mdk]['value'] = "2020-08-03"
        d[self.lgk]['value'] = None
        d[self.dtk]['value'] = None
        g = d.build_graph(self.vocabulary)
        self.assertEqual(rdf_utils.update_pg_description(c1, g), c2)

    def test_update_pg_description_9(self):
        c1 = """Commentaire.<METADATA>N'importe quoi 1!!</METADATA>
             <METADATA>N'importe quoi 2!!</METADATA>Suite."""
        c2 = """Commentaire.<METADATA>
[
  {
    "@id": "urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778",
    "@type": [
      "http://www.w3.org/ns/dcat#Dataset"
    ],
    "http://purl.org/dc/terms/identifier": [
      {
        "@value": "c41423cc-fb59-443f-86f4-72592a4f6778"
      }
    ],
    "http://purl.org/dc/terms/modified": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#date",
        "@value": "2020-08-03"
      }
    ]
  }
]
</METADATA>Suite."""
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        d.replace_uuid("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778")
        d[self.mdk]['value'] = "2020-08-03"
        d[self.lgk]['value'] = None
        d[self.dtk]['value'] = None
        g = d.build_graph(self.vocabulary)
        self.assertEqual(rdf_utils.update_pg_description(c1, g), c2)


    def test_update_pg_description_10(self):
        c1 = None
        c2 = """

<METADATA>
[
  {
    "@id": "urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778",
    "@type": [
      "http://www.w3.org/ns/dcat#Dataset"
    ],
    "http://purl.org/dc/terms/identifier": [
      {
        "@value": "c41423cc-fb59-443f-86f4-72592a4f6778"
      }
    ],
    "http://purl.org/dc/terms/modified": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#date",
        "@value": "2020-08-03"
      }
    ]
  }
]
</METADATA>
"""
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        d.replace_uuid("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778")
        d[self.mdk]['value'] = "2020-08-03"
        d[self.lgk]['value'] = None
        d[self.dtk]['value'] = None
        g = d.build_graph(self.vocabulary)
        self.assertEqual(rdf_utils.update_pg_description(c1, g), c2)


    ### FONCTION build_vocabulary
    ### -------------------------

    # pas de vocabulaire :
    def test_build_vocabulary_1(self):
        self.assertEqual(
            rdf_utils.build_vocabulary("Thème de données (UE)", Graph()),
            []
            )

    # ensemble non renseigné :
    def test_build_vocabulary_2(self):
        self.assertEqual(
            rdf_utils.build_vocabulary("", self.vocabulary),
            []
            )

    # cas normal :
    def test_build_vocabulary_3(self):
        self.assertEqual(
            rdf_utils.build_vocabulary("Thème de données (UE)", self.vocabulary),
            ['Agriculture, pêche, sylviculture et alimentation',
            'Économie et finances', 'Éducation, culture et sport', 'Énergie',
            'Environnement', 'Gouvernement et secteur public',
            'Justice, système juridique et sécurité publique',
            'Population et société', 'Questions internationales',
            'Régions et villes', 'Santé', 'Science et technologie',
            'Transports']
            )

    # ensemble inconnu :
    def test_build_vocabulary_4(self):
        self.assertEqual(
            rdf_utils.build_vocabulary("Ensemble inconnu", self.vocabulary),
            []
            )

    # autre langue (connue et utilisée pour le nom de l'ensemble) :
    def test_build_vocabulary_5(self):
        self.assertEqual(
            rdf_utils.build_vocabulary("Data theme (EU)", self.vocabulary, language='en'),
            ['Agriculture, fisheries, forestry and food', 'Economy and finance',
            'Education, culture and sport', 'Energy', 'Environment',
            'Government and public sector', 'Health', 'International issues',
            'Justice, legal system and public safety', 'Population and society',
            'Regions and cities', 'Science and technology', 'Transport']
            )

    # autre langue (inconnue) :
    def test_build_vocabulary_6(self):
        self.assertEqual(
            rdf_utils.build_vocabulary("Data theme (EU)", self.vocabulary, language='it'),
            []
            )

    # le nom de l'ensemble n'est pas dans la langue indiquée :
    def test_build_vocabulary_6(self):
        self.assertEqual(
            rdf_utils.build_vocabulary("Data theme (EU)", self.vocabulary, language='fr'),
            []
            )


    ### F0NCTION is_valid_minipath
    ### --------------------------
        
    def test_is_valid_minipath_1(self):
        self.assertFalse(
            rdf_utils.is_valid_minipath("dct:title", Graph().namespace_manager)
            )

    def test_is_valid_minipath_2(self):
        self.assertFalse(
            rdf_utils.is_valid_minipath("", Graph().namespace_manager)
            )

    def test_is_valid_minipath_3(self):
        self.assertFalse(
            rdf_utils.is_valid_minipath("", self.nsm)
            )

    def test_is_valid_minipath_4(self):
        self.assertTrue(
            rdf_utils.is_valid_minipath("dct:title", self.nsm)
            )

    # les chemins composés ne sont pas des MINI chemins :
    def test_is_valid_minipath_5(self):
        self.assertFalse(
            rdf_utils.is_valid_minipath(
                "dcat:distribution / dct:licence / rdfs:label",
                self.nsm
                )
            )

    # sous forme d'URI brute :
    def test_is_valid_minipath_6(self):
        self.assertTrue(
            rdf_utils.is_valid_minipath(
                '<https://www.w3.org/TR/sparql11-query/>',
                self.nsm
                )
            )

unittest.main()
