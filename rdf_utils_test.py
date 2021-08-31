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
import rdf_utils
from rdf_utils_debug import check_unchanged, populate_widgets


class TestRDFUtils(unittest.TestCase):
    
    def setUp(self):
    
        # import du schéma SHACL qui décrit les métadonnées communes
        with open(r'modeles\shape.ttl', encoding='UTF-8') as src:
            self.shape = Graph().parse(data=src.read(), format='turtle')
        self.nsm = self.shape.namespace_manager
        
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
        self.widgetsdict = rdf_utils.build_dict(
            Graph(), self.shape, self.vocabulary,
            translation=True, langList=['fr', 'en', 'it']
            )

        # récupération de quelques clés
        self.ttk = None
        self.tck = None
        for k, v in self.widgetsdict.items():
            if v['path'] == 'dct:temporal':
                # clé du groupe de propriétés de la couverture temporelle
                self.tck = k
            elif self.tck and len(k) > 1 and k[1]==self.tck[1] \
                    and v['object'] == 'plus button':
                # bouton plus pour la couverture temporelle
                self.tck_plus = k
            elif v['path'] == 'dct:language':
                # clé de la langue
                self.lgk = k
            elif v['path'] == 'dct:title':
                # clé du libellé
                self.ttk = k
            elif self.ttk and len(k) > 1 and k[1]==self.ttk[1] \
                    and v['object'] == 'translation button':
                # bouton de traduction du libellé
                self.ttk_plus = k
            elif v['path'] == 'dct:modified':
                # clé de la date de création
                self.mdk = k
            elif v['path'] == 'dcat:distribution / dct:license':
                if v['object'] == 'edit':
                    # clé de la licence (IRI)
                    self.lck = k
                else:
                    # clé de la licence (manuel)
                    self.lck_m = k
            elif v['path'] == 'dcat:distribution / dct:license / rdfs:label':
                # cle du texte de la licence
                self.lck_m_txt = k

        # création de pseudo-widgets
        populate_widgets(self.widgetsdict) 
       

    ### FONCTION build_dict
    ### ----------------------------------

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
                    '2021-08-31T17:32:00',
                    datatype='http://www.w3.org/2001/XMLSchema#dateTime'
                    )
                )
        d = rdf_utils.build_dict(
            self.metagraph, self.shape, self.vocabulary,
            data = { 'dct:modified' : ['2021-08-31T17:32:00'] }
            )
        b = False
        for k, v in d.items():
            if v['path'] == 'dct:modified':
                self.assertEqual(v['value'], '2021-08-31T17:32:00')
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
                    '2021-08-31T17:32:00',
                    datatype='http://www.w3.org/2001/XMLSchema#dateTime'
                    )
                )
    
    # informations mises à jour depuis une source externe 
    # + catégorie absente du modèle et hideUnlisted valant True :
    def test_build_dict_2(self):
        self.assertTrue(not 'dct:modified' in self.template)
        d = rdf_utils.build_dict(
            Graph(), self.shape, self.vocabulary,
            template = self.template, hideUnlisted=True,
            data = { 'dct:modified' : ['2021-08-31T17:32:00'] }
            )
        b = False
        for k, v in d.items():
            if v['path'] == 'dct:modified':
                self.assertEqual(v['value'], '2021-08-31T17:32:00')
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
                    '2021-08-31T17:32:00',
                    datatype='http://www.w3.org/2001/XMLSchema#dateTime'
                    )
                )
    
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
        self.assertEqual(c["switch source menu to update"], [])
        self.assertEqual(c["sources list to update"], [])
        
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
        self.assertEqual(c["switch source menu to update"], [])
        if d[self.lck]['current source'] == '< URI >':
            self.assertEqual(c["sources list to update"], [])
        else:
            self.assertEqual(c["sources list to update"], self.lck)
        self.assertTrue(d[self.lck_m]['hidden M'])
        self.assertTrue(d[self.lck_m_txt]['hidden M'])
        self.assertEqual(d[self.lck_m_txt]['value'], "Non vide")
        self.assertFalse(d[self.lck]['hidden M'])
        self.assertIsNone(d[self.lck]['value'])
        self.assertEqual(d[self.lck]['current source'], s)
        self.assertIsNone(d[self.lck_m]['current source'])

    # changement de thésaurus

    # ancienne source non référencée

    # source inconnue

    # une seule source

    # la source ne change pas


    ### FONCTION WidgetsDict.order_keys
    ### -------------------------------
    
    # groupe de valeurs
    def test_wd_order_keys_1(self):
        self.assertEqual(self.widgetsdict.order_keys(self.tck[1]), [1])
   
    # bouton plus
    def test_wd_order_keys_2(self):
        self.assertEqual(self.widgetsdict.order_keys(self.tck_plus), [1])
    
    # groupe de traduction
    def test_wd_order_keys_3(self):
        self.assertEqual(self.widgetsdict.order_keys(self.ttk[1]), [1])

    # bouton de traduction
    def test_wd_order_keys_4(self):
        self.assertEqual(self.widgetsdict.order_keys(self.ttk_plus), [1])
    
    # groupe de propriétés masqué
    def test_wd_order_keys_5(self):
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        d.change_source(self.lck, '< manuel >')
        d.update_value(self.lck_m_txt, "Non vide")
        d.change_source(self.lck_m, '< URI >')
        self.assertEqual(self.widgetsdict.order_keys(self.lck_m_txt), [1])
    
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
        q_id = g.query(
            """
            SELECT
                ?id
            WHERE
                { ?id a dcat:Dataset . }
            """,
            initNs = {'dcat': URIRef('http://www.w3.org/ns/dcat#')}
            )
        self.assertEqual(len(q_id), 1)

    def test_wd_replace_uuid_2(self):
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        d.replace_uuid("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778")
        g = d.build_graph(self.vocabulary)
        q_id = g.query(
            """
            SELECT
                ?id
            WHERE
                { ?id a dcat:Dataset . }
            """,
            initNs = {'dcat': URIRef('http://www.w3.org/ns/dcat#')}
            )
        for i in q_id:
            with self.subTest(uuid=i):
                self.assertEqual(
                    i['id'],
                    URIRef("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778")
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

    # à compléter !
    
    # def test_wd_drop_2(self):
        # d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        # d.drop(tck)
        # self.assertTrue([e for e in d.keys() if is_ancestor(tck, key)] == [])
        #self.assertTrue(d.get(tck) is None)


    ### FONCTION WidgetsDict.change_language
    ### ------------------------------------

    def test_wd_change_language_1(self):
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        populate_widgets(d)
        
        a = d.add(self.ttk_plus)
        populate_widgets(d)
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
        populate_widgets(d)
        c = d.change_language(self.ttk, 'fr')
        self.assertEqual(c["language menu to update"], [])
        self.assertEqual(c["widgets to hide"], [])
        
    # cas d'une langue de fait non autorisée :
    def test_wd_change_language_5(self):
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        populate_widgets(d)
        # modification manuelle de la langue
        d[self.ttk]['language value'] = 'es'
        d[self.ttk]['authorized languages'].append('es')
        d[self.ttk]['authorized languages'].sort()
        
        a1 = d.add(self.ttk_plus)
        populate_widgets(d)
        self.assertEqual(d[a1["new keys"][0]]['language value'], 'en')
        self.assertEqual(d[a1["new keys"][0]]['authorized languages'], ['en', 'fr', 'it'])
        self.assertEqual(d[self.ttk]['authorized languages'], ['es', 'fr', 'it'])
        a2 = d.add(self.ttk_plus)
        populate_widgets(d)
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
    "http://purl.org/dc/terms/modified": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#dateTime",
        "@value": "2020-08-03 00:00:00"
      }
    ]
  }
]
</METADATA>"""
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        d.replace_uuid("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778")
        d[self.mdk]['value'] = "2020-08-03 00:00:00"
        d[self.lgk]['value'] = None
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
    "http://purl.org/dc/terms/modified": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#dateTime",
        "@value": "2020-08-03 00:00:00"
      }
    ]
  }
]
</METADATA>"""
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        d.replace_uuid("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778")
        d[self.mdk]['value'] = "2020-08-03 00:00:00"
        d[self.lgk]['value'] = None
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
    "http://purl.org/dc/terms/modified": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#dateTime",
        "@value": "2020-08-03 00:00:00"
      }
    ]
  }
]
</METADATA></METADATA>"""
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        d.replace_uuid("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778")
        d[self.mdk]['value'] = "2020-08-03 00:00:00"
        d[self.lgk]['value'] = None
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
    "http://purl.org/dc/terms/modified": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#dateTime",
        "@value": "2020-08-03 00:00:00"
      }
    ]
  }
]
</METADATA></METADATA>"""
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        d.replace_uuid("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778")
        d[self.mdk]['value'] = "2020-08-03 00:00:00"
        d[self.lgk]['value'] = None
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
    "http://purl.org/dc/terms/modified": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#dateTime",
        "@value": "2020-08-03 00:00:00"
      }
    ]
  }
]
</METADATA>"""
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        d.replace_uuid("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778")
        d[self.mdk]['value'] = "2020-08-03 00:00:00"
        d[self.lgk]['value'] = None
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
    "http://purl.org/dc/terms/modified": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#dateTime",
        "@value": "2020-08-03 00:00:00"
      }
    ]
  }
]
</METADATA>
"""
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        d.replace_uuid("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778")
        d[self.mdk]['value'] = "2020-08-03 00:00:00"
        d[self.lgk]['value'] = None
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
    "http://purl.org/dc/terms/modified": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#dateTime",
        "@value": "2020-08-03 00:00:00"
      }
    ]
  }
]
</METADATA>
"""
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        d.replace_uuid("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778")
        d[self.mdk]['value'] = "2020-08-03 00:00:00"
        d[self.lgk]['value'] = None
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
    "http://purl.org/dc/terms/modified": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#dateTime",
        "@value": "2020-08-03 00:00:00"
      }
    ]
  }
]
</METADATA>"""
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        d.replace_uuid("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778")
        d[self.mdk]['value'] = "2020-08-03 00:00:00"
        d[self.lgk]['value'] = None
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
    "http://purl.org/dc/terms/modified": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#dateTime",
        "@value": "2020-08-03 00:00:00"
      }
    ]
  }
]
</METADATA>"""
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        d.replace_uuid("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778")
        d[self.mdk]['value'] = "2020-08-03 00:00:00"
        d[self.lgk]['value'] = None
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
    "http://purl.org/dc/terms/modified": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#dateTime",
        "@value": "2020-08-03 00:00:00"
      }
    ]
  }
]
</METADATA>"""
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        d.replace_uuid("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778")
        d[self.mdk]['value'] = "2020-08-03 00:00:00"
        d[self.lgk]['value'] = None
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
    "http://purl.org/dc/terms/modified": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#dateTime",
        "@value": "2020-08-03 00:00:00"
      }
    ]
  }
]
</METADATA>Suite."""
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        d.replace_uuid("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778")
        d[self.mdk]['value'] = "2020-08-03 00:00:00"
        d[self.lgk]['value'] = None
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
    "http://purl.org/dc/terms/modified": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#dateTime",
        "@value": "2020-08-03 00:00:00"
      }
    ]
  }
]
</METADATA>Suite."""
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        d.replace_uuid("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778")
        d[self.mdk]['value'] = "2020-08-03 00:00:00"
        d[self.lgk]['value'] = None
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
    "http://purl.org/dc/terms/modified": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#dateTime",
        "@value": "2020-08-03 00:00:00"
      }
    ]
  }
]
</METADATA>Suite."""
        d = rdf_utils.WidgetsDict(self.widgetsdict.copy())
        d.replace_uuid("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778")
        d[self.mdk]['value'] = "2020-08-03 00:00:00"
        d[self.lgk]['value'] = None
        g = d.build_graph(self.vocabulary)
        self.assertEqual(rdf_utils.update_pg_description(c1, g), c2)


    ### FONCTION build_vocabulary
    ### -------------------------

    # pas de vocabulaire :
    def test_build_vocabulary_1(self):
        self.assertEqual(
            rdf_utils.build_vocabulary("Thème de données (UE)", Graph()),
            None
            )

    # ensemble non renseigné :
    def test_build_vocabulary_2(self):
        self.assertEqual(
            rdf_utils.build_vocabulary("", self.vocabulary),
            None
            )

    # cas normal :
    def test_build_vocabulary_3(self):
        self.assertEqual(
            rdf_utils.build_vocabulary("Thème de données (UE)", self.vocabulary),
            ['Agriculture, pêche, sylviculture et alimentation',
            'Données provisoires', 'Économie et finances',
            'Éducation, culture et sport', 'Énergie', 'Environnement',
            'Gouvernement et secteur public',
            'Justice, système juridique et sécurité publique',
            'Population et société', 'Questions internationales',
            'Régions et villes', 'Santé', 'Science et technologie',
            'Transports']
            )

    # ensemble inconnu :
    def test_build_vocabulary_4(self):
        self.assertEqual(
            rdf_utils.build_vocabulary("Ensemble inconnu", self.vocabulary),
            None
            )

    # autre langue (connue et utilisée pour le nom de l'ensemble) :
    def test_build_vocabulary_5(self):
        self.assertEqual(
            rdf_utils.build_vocabulary("Data theme (EU)", self.vocabulary, language='en'),
            ['Agriculture, fisheries, forestry and food', 'Economy and finance',
            'Education, culture and sport', 'Energy', 'Environment',
            'Government and public sector', 'Health', 'International issues',
            'Justice, legal system and public safety', 'Population and society',
            'Provisional data', 'Regions and cities', 'Science and technology',
            'Transport']
            )

    # autre langue (inconnue) :
    def test_build_vocabulary_6(self):
        self.assertEqual(
            rdf_utils.build_vocabulary("Data theme (EU)", self.vocabulary, language='it'),
            None
            )

    # le nom de l'ensemble n'est pas dans la langue indiquée :
    def test_build_vocabulary_6(self):
        self.assertEqual(
            rdf_utils.build_vocabulary("Data theme (EU)", self.vocabulary, language='fr'),
            None
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
