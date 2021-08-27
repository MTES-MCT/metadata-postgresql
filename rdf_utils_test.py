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
import rdf_utils, rdf_utils_debug

class TestRDFUtilsMethods(unittest.TestCase):
    
    def setUp(self):
    
        # import du schéma SHACL qui décrit les métadonnées communes
        with open(r'modeles\shape.ttl', encoding='UTF-8') as src:
            self.shape = Graph().parse(data=src.read(), format='turtle')
        
        # vocabulaire - ontologies utilisées par les métadonnées communes
        with open(r'modeles\vocabulary.ttl', encoding='UTF-8') as src:
            self.vocabulary = Graph().parse(data=src.read(), format='turtle')
            
        # import d'un exemple de modèle local de formulaire
        with open(r'exemples\exemple_dict_modele_local.json', encoding='UTF-8') as src:
            self.template = json.loads(src.read())

        # import d'un exemple de fiche de métadonnée
        with open(r'exemples\exemple_commentaire_pg.txt', encoding='UTF-8') as src:
            self.metagraph = rdf_utils.metagraph_from_pg_description(src.read(), self.shape)

        # sérialisation de l'exemple sous forme de dictionnaire de widget
        self.widgetsdict = rdf_utils.build_dict(self.metagraph, self.shape, self.vocabulary, template=self.template)
        
        # création de pseudo-widgets
        self.widgetsdict[(0,)]['main widget'] = 'widget QGroupBox racine'
        self.widgetsdict[(0,)]['grid widget'] = 'widget QGridLayout racine'
        
        # clé de l'enregistrement contenant le QGroupBox pour la couverture
        # temporelle
        for k, v in self.widgetsdict.items():
            if v['path'] == 'dct:temporal':
                tck = k[1]
                break
  
    
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
            'widget QGroupBox racine'
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
            'widget QGridLayout racine'
            )


    ### FONCTION WidgetDict.drop
    ### ---------------------------

    def test_wd_drop_1(self):
        d = self.widgetsdict.copy()
        d.drop(tck)
        self.assertTrue(d.get(tck) is None)

    def test_wd_drop_2(self):
        d = self.widgetsdict.copy()
        d.drop(tck)
        self.assertTrue([e for e in d.keys() if is_ancestor(tck, key)] == [])
   
    def test_wd_drop_3(self):
        d = self.widgetsdict.copy()


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


unittest.main()
