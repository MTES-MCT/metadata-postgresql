
import unittest
from uuid import uuid4
from rdflib import URIRef, Literal, RDFS, DC, FOAF

from plume.rdf.widgetkey import WidgetKey, ValueKey, GroupOfPropertiesKey, \
    GroupOfValuesKey, TranslationGroupKey, TranslationButtonKey, \
    PlusButtonKey, RootKey
from plume.rdf.actionsbook import ActionsBook

class WidgetKeyTestCase(unittest.TestCase):

    def test_lang_attributes(self):
        """Gestion des propriétés de classe, `langlist` et `main_language`.
        
        """
        r = RootKey()  
        r.langlist = ['fr', 'en']
        r.main_language = 'it'
        self.assertEqual(r.langlist, ['it', 'en', 'fr'])
        r.langlist = ['de', 'en']
        self.assertEqual(r.main_language, 'de')

    def test_search_path(self):
        """Recherche dans un arbre de clés à partir du chemin.
        
        """
        r = RootKey()
        g = GroupOfPropertiesKey(parent=r,
            rdftype=URIRef('http://purl.org/dc/terms/RightsStatement'),
            predicate=URIRef('http://purl.org/dc/terms/accessRights'))
        m = ValueKey(parent=r, m_twin=g, is_hidden_m=False)
        t = TranslationGroupKey(parent=g, predicate=RDFS.label)
        b = TranslationButtonKey(parent=t)
        w1 = ValueKey(parent=t)
        w2 = ValueKey(parent=t)
        self.assertEqual(r.search_from_path(URIRef('http://purl.org/dc/terms/' \
            'accessRights') / RDFS.label), t)
        self.assertEqual(r.search_from_path(URIRef('http://purl.org/dc/terms/' \
            'accessRights')), m)
        m.switch_twin()
        self.assertEqual(r.search_from_path(URIRef('http://purl.org/dc/terms/' \
            'accessRights')), g)
    
    def test_root_key(self):
        """Initialisation d'une clé racine.
        
        """
        rootkey = RootKey(datasetid=URIRef(uuid4().urn))
        self.assertEqual(rootkey.rdftype, \
            URIRef('http://www.w3.org/ns/dcat#Dataset'))
        
    def test_group_of_values(self):
        """Gestion des lignes dans un groupe de valeurs.
        
        """
        rootkey = RootKey()
        groupkey = GroupOfValuesKey(parent=rootkey, predicate=DC.title,
            rdftype=RDFS.label)
        
        pluskey = PlusButtonKey(parent=groupkey)
        self.assertFalse(pluskey in groupkey.children)
        #self.assertEqual(pluskey.row, 0)
        self.assertEqual(groupkey.button, pluskey)
        
        valkey1 = GroupOfPropertiesKey(parent=groupkey,
            predicate=DC.description)
        self.assertTrue(valkey1 in groupkey.children)
        self.assertEqual(valkey1.row, 0)
        self.assertEqual(pluskey.row, 1)
        self.assertFalse(pluskey.is_hidden_b)
        self.assertTrue(valkey1.is_single_child)
        self.assertEqual(valkey1.predicate, DC.title)
        
        valkey2 = ValueKey(parent=groupkey, rowspan=3)
        self.assertEqual(valkey1.row, 0)
        self.assertEqual(valkey2.row, 1)
        self.assertEqual(pluskey.row, 4)
        self.assertFalse(pluskey.is_hidden_b)
        self.assertFalse(valkey1.is_single_child)
        self.assertFalse(valkey2.is_single_child)
        self.assertEqual(valkey2.predicate, DC.title)

        valkey1.kill()
        self.assertFalse(valkey1 in groupkey.children)
        self.assertTrue(valkey2.is_single_child)
        self.assertEqual(valkey2.row, 0)
        self.assertEqual(pluskey.row, 3)


    def test_translation_group(self):
        """Gestion des lignes et des langues dans un groupe de traduction.

        """
        rootkey = RootKey()
        WidgetKey.langlist = ['fr', 'en', 'it']
        groupkey = TranslationGroupKey(parent=rootkey,
            predicate=DC.title)
        transkey = TranslationButtonKey(parent=groupkey)
        self.assertFalse(transkey in groupkey.children)
        self.assertEqual(transkey.row, 0)
        self.assertEqual(groupkey.button, transkey)

        valkey1 = ValueKey(parent=groupkey, rowspan=3,
            value_language='fr', predicate=RDFS.label)
        self.assertEqual(valkey1.row, 0)
        self.assertEqual(transkey.row, 3)
        self.assertEqual(groupkey.available_languages, ['en', 'it'])
        self.assertEqual(valkey1.predicate, DC.title)
        self.assertFalse(transkey.is_hidden_b)
        self.assertTrue(valkey1.is_single_child)

        valkey2 = ValueKey(parent=groupkey, rowspan=2,
            value_language='en')
        valkey3 = ValueKey(parent=groupkey, rowspan=1,
            value_language='it')
        self.assertEqual(transkey.row, 6)
        self.assertEqual(groupkey.available_languages, [])
        self.assertTrue(transkey.is_hidden_b)
        self.assertFalse(valkey1.is_single_child)
        self.assertEqual(valkey2.predicate, DC.title)

        valkey2.kill()
        self.assertFalse(valkey2 in groupkey.children)
        self.assertEqual(groupkey.available_languages, ['en'])
        self.assertFalse(transkey.is_hidden_b)
        self.assertEqual(transkey.row, 4)
        self.assertEqual(valkey3.row, 3)

        valkey4 = ValueKey(parent=groupkey, rowspan=2, value_language='de')
        self.assertTrue(valkey4 in groupkey.children)
        self.assertEqual(groupkey.available_languages, ['en'])
        self.assertFalse(transkey.is_hidden_b)
        valkey4.kill()

        valkey3.change_language('en')
        self.assertEqual(groupkey.available_languages, ['it'])
        self.assertFalse(transkey.is_hidden_b)

        valkey4 = ValueKey(parent=groupkey, rowspan=2, value_language='de')
        valkey4.change_language('it')
        self.assertEqual(groupkey.available_languages, [])
        self.assertTrue(transkey.is_hidden_b)

    
    def test_ghost(self):
        """Gestion des branches fantômes.
        
        """
        rootkey = RootKey()
        groupkey = GroupOfValuesKey(parent=rootkey, is_ghost=True,
            predicate=DC.title, rdftype=FOAF.Agent)
        pluskey = PlusButtonKey(parent=groupkey)
        self.assertIsNone(pluskey)
        editkey = ValueKey(parent=rootkey, rowspan=2,
            predicate=DC.title)
        
        self.assertIsNone(groupkey.row)
        self.assertEqual(editkey.row, 0)
        
        valkey1 = GroupOfPropertiesKey(parent=groupkey)
        self.assertTrue(valkey1 in groupkey.children)
        self.assertIsNone(valkey1.row)
        self.assertTrue(valkey1.is_ghost)
        self.assertFalse(valkey1.is_single_child)
        self.assertFalse(valkey1.has_minus_button)
        self.assertEqual(valkey1.predicate, DC.title)

        valkey2 = ValueKey(parent=groupkey, is_ghost=False)
        self.assertIsNone(valkey2)
        valkey2 = ValueKey(parent=groupkey, is_ghost=False,
            value=Literal('Mon fantôme à sauvegarder.',
            lang='fr'))
        self.assertTrue(valkey2.is_ghost)
        self.assertEqual(valkey2.predicate, DC.title)

        groupkey.kill()
        self.assertFalse(groupkey in rootkey.children)
        self.assertEqual(editkey.row, 0)


    def test_hidden_m(self):
        """Gestion des jumelles.
        
        """
        rootkey = RootKey(datasetid=URIRef(uuid4().urn))
        groupkey = GroupOfValuesKey(parent=rootkey, predicate=DC.title,
            rdftype=FOAF.Agent)
        buttonkey = PlusButtonKey(parent=groupkey)
        valkey1 = GroupOfPropertiesKey(parent=groupkey, is_hidden_m=True)
        valkey2 = ValueKey(parent=groupkey, rowspan=1, m_twin=valkey1)
        valkey3 = ValueKey(parent=groupkey, rowspan=3)

        self.assertTrue(valkey1 in groupkey.children)
        self.assertTrue(valkey2 in groupkey.children)
        self.assertEqual(valkey1.m_twin, valkey2)
        self.assertEqual(valkey2.m_twin, valkey1)
        self.assertEqual(valkey1.row, 0)
        self.assertEqual(valkey2.row, 0)
        self.assertEqual(valkey3.row, 1)
        self.assertEqual(buttonkey.row, 4)
        self.assertFalse(valkey1.is_single_child)

        self.assertTrue(valkey1.is_hidden_m)
        self.assertFalse(valkey2.is_hidden_m)
        valkey2.switch_twin()
        self.assertTrue(valkey2.is_hidden_m)
        self.assertFalse(valkey1.is_hidden_m)
        
        valkey3.kill()
        self.assertTrue(valkey1.is_single_child)
        self.assertTrue(valkey2.is_single_child)
        self.assertEqual(valkey1.row, 0)
        self.assertEqual(valkey2.row, 0)
        self.assertEqual(buttonkey.row, 1)
        
        valkey3 = ValueKey(parent=groupkey, rowspan=3)
        valkey1.kill()
        self.assertTrue(not valkey1 in groupkey.children)
        self.assertTrue(not valkey2 in groupkey.children)
        self.assertEqual(valkey3.row, 0)
        self.assertTrue(valkey3.is_single_child)
        
        
    def test_delated_computation(self):
        """Calcul a posteriori des lignes et filles uniques.
        
        """
        rootkey = RootKey()
        WidgetKey.langlist = ['fr', 'en', 'it']
        WidgetKey.no_computation = True
        groupkey1 = GroupOfValuesKey(parent=rootkey, predicate=DC.title,
            rdftype=FOAF.Agent)
        buttonkey1 = PlusButtonKey(parent=groupkey1)
        valkey1a = GroupOfPropertiesKey(parent=groupkey1)
        valkey1b = ValueKey(parent=groupkey1, rowspan=1, m_twin=valkey1a,
            is_hidden_m=True)
        valkey1c = ValueKey(parent=groupkey1, rowspan=3)
        groupkey2 = TranslationGroupKey(parent=rootkey, predicate=DC.title)
        buttonkey2 = TranslationButtonKey(parent=groupkey2)
        valkey2 = ValueKey(parent=groupkey2, rowspan=2, value_language='en')
        WidgetKey.no_computation = False
        
        self.assertIsNone(valkey1a.row)
        self.assertIsNone(valkey1b.row)
        self.assertIsNone(valkey1c.row)
        self.assertIsNone(buttonkey1.row)
        self.assertFalse(valkey1a.is_single_child)
        self.assertFalse(valkey1b.is_single_child)
        self.assertFalse(valkey1c.is_single_child)

        self.assertIsNone(valkey2.row)
        self.assertIsNone(buttonkey2.row)
        self.assertFalse(valkey2.is_single_child)
        
        groupkey1.compute_rows()
        self.assertEqual(valkey1a.row, 0)
        self.assertIsNone(valkey1b.row)
        self.assertEqual(valkey1c.row, 1)
        self.assertEqual(buttonkey1.row, 4)
        groupkey1.compute_single_children()
        self.assertFalse(valkey1a.is_single_child)
        self.assertFalse(valkey1b.is_single_child)
        self.assertFalse(valkey1c.is_single_child)

        groupkey2.compute_rows()
        self.assertEqual(valkey2.row, 0)
        self.assertEqual(buttonkey2.row, 2)
        groupkey2.compute_single_children()
        self.assertTrue(valkey2.is_single_child)

    def test_actionsbook(self):
        rootkey = RootKey()
        WidgetKey.langlist=['fr', 'en', 'it']
        groupkey1 = GroupOfValuesKey(parent=rootkey, predicate=DC.title,
            rdftype=FOAF.Agent)
        buttonkey1 = PlusButtonKey(parent=groupkey1)
        valkey1a = GroupOfPropertiesKey(parent=groupkey1)
        valkey1b = ValueKey(parent=groupkey1, rowspan=1, m_twin=valkey1a,
            is_hidden_m=True)
        valkey1c = ValueKey(parent=groupkey1, rowspan=3)
        groupkey2 = TranslationGroupKey(parent=rootkey, predicate=DC.title)
        buttonkey2 = TranslationButtonKey(parent=groupkey2)
        valkey2a = ValueKey(parent=groupkey2, rowspan=2,
            value_language='en')

        WidgetKey.clear_actionsbook()
        valkey1d = ValueKey(parent=groupkey1, rowspan=1)
        actionsbook = WidgetKey.unload_actionsbook()
        self.assertEqual(actionsbook.create, [valkey1d])
        self.assertEqual(actionsbook.drop, [])
        self.assertEqual(actionsbook.move, [buttonkey1])
        self.assertEqual(actionsbook.show_minus_button, [])
        self.assertEqual(actionsbook.hide_minus_button, [])
        self.assertEqual(actionsbook.show, [])
        self.assertEqual(actionsbook.hide, [])
        self.assertEqual(actionsbook.languages, [])

        actionsbook = valkey1a.switch_twin()
        self.assertEqual(actionsbook.create, [])
        self.assertEqual(actionsbook.drop, [])
        self.assertEqual(actionsbook.move, [valkey1b])
        self.assertEqual(actionsbook.show_minus_button, [])
        self.assertEqual(actionsbook.hide_minus_button, [])
        self.assertEqual(actionsbook.show, [valkey1b])
        self.assertEqual(actionsbook.hide, [valkey1a])
        self.assertEqual(actionsbook.languages, [])

        valkey2b = ValueKey(parent=groupkey2, rowspan=2, value_language='fr')
        actionsbook = WidgetKey.unload_actionsbook()
        self.assertEqual(actionsbook.create, [valkey2b])
        self.assertEqual(actionsbook.drop, [])
        self.assertEqual(actionsbook.move, [buttonkey2])
        self.assertEqual(actionsbook.show_minus_button, [valkey2a])
        self.assertEqual(actionsbook.hide_minus_button, [])
        self.assertEqual(actionsbook.show, [])
        self.assertEqual(actionsbook.hide, [])
        self.assertEqual(actionsbook.languages, [valkey2a])

        valkey2c = ValueKey(parent=groupkey2, rowspan=2, value_language='it')
        actionsbook = WidgetKey.unload_actionsbook()
        self.assertEqual(actionsbook.create, [valkey2c])
        self.assertEqual(actionsbook.drop, [])
        self.assertEqual(actionsbook.move, [buttonkey2])
        self.assertEqual(actionsbook.show_minus_button, [])
        self.assertEqual(actionsbook.hide_minus_button, [])
        self.assertEqual(actionsbook.show, [])
        self.assertEqual(actionsbook.hide, [buttonkey2])
        self.assertEqual(actionsbook.languages, [valkey2a, valkey2b])

        actionsbook = valkey2a.drop()
        self.assertEqual(actionsbook.create, [])
        self.assertEqual(actionsbook.drop, [valkey2a])
        self.assertEqual(actionsbook.move, [valkey2b, valkey2c, buttonkey2])
        self.assertEqual(actionsbook.show_minus_button, [])
        self.assertEqual(actionsbook.hide_minus_button, [])
        self.assertEqual(actionsbook.show, [buttonkey2])
        self.assertEqual(actionsbook.hide, [])
        self.assertEqual(actionsbook.languages, [valkey2b, valkey2c])

        actionsbook = valkey2c.change_language('en')
        self.assertEqual(actionsbook.create, [])
        self.assertEqual(actionsbook.drop, [])
        self.assertEqual(actionsbook.move, [])
        self.assertEqual(actionsbook.show_minus_button, [])
        self.assertEqual(actionsbook.hide_minus_button, [])
        self.assertEqual(actionsbook.show, [])
        self.assertEqual(actionsbook.hide, [])
        self.assertEqual(actionsbook.languages, [valkey2b, valkey2c])

        actionsbook = valkey2b.drop()
        self.assertEqual(actionsbook.create, [])
        self.assertEqual(actionsbook.drop, [valkey2b])
        self.assertEqual(actionsbook.move, [valkey2c, buttonkey2])
        self.assertEqual(actionsbook.show_minus_button, [])
        self.assertEqual(actionsbook.hide_minus_button, [valkey2c])
        self.assertEqual(actionsbook.show, [])
        self.assertEqual(actionsbook.hide, [])
        self.assertEqual(actionsbook.languages, [valkey2c])
        
        

unittest.main()
