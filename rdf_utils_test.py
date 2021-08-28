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

class TestRDFUtils(unittest.TestCase):
    
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

        # construction d'un dictionnaire de widgets à partir d'un graphe vierge
        self.widgetsdict = rdf_utils.build_dict(Graph(), self.shape, self.vocabulary)

        # récupération de quelques clés
        for k, v in self.widgetsdict.items():
            if v['path'] == 'dct:temporal':
                # clé du groupe de propriétés de la couverture temporelle
                self.tck = k
            elif v['path'] == 'dct:language':
                # clé de la langue
                self.lgk = k
            elif v['path'] == 'dct:title':
                # clé du libellé
                self.ttk = k

        # création de pseudo-widgets
        rdf_utils_debug.populate_widgets(self.widgetsdict) 
       


    ### FONCTION WidgetsDict.child
    ### -----------------------------------

    def test_wd_child_1(self):
        self.assertEqual(self.widgetsdict.child((0,))[1], (0,))

    def test_wd_child_2(self):
        self.assertEqual(self.widgetsdict.child(self.tck), (0, self.tck))


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
    
    # cas d'une clé M
    def test_replace_ancestor_5(self):
        self.assertEqual(
            rdf_utils.replace_ancestor((2, (3, (0, )), 'M'), (3, (0, )), (4, (0, ))),
            (2, (4, (0,)), 'M')
            )

    def test_replace_ancestor_7(self):
        with self.assertRaisesRegex(ValueError, r'^M\s'):
            rdf_utils.replace_ancestor((2, (1, (0,))), (1, (0,)), (3, (0, ), 'M'))
    
    
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
            '< (0,) main widget (QGroupBox) >'
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
            '< (0,) grid widget (QGridLayout) >'
            )


    ### FONCTION WidgetDict.drop
    ### ---------------------------

    # def test_wd_drop_1(self):
        # d = self.widgetsdict.copy()
        # d.drop(tck)
        # self.assertTrue(d.get(tck) is None)

    # def test_wd_drop_2(self):
        # d = self.widgetsdict.copy()
        # d.drop(tck)
        # self.assertTrue([e for e in d.keys() if is_ancestor(tck, key)] == [])


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
