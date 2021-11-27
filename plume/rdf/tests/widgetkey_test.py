
import unittest
from plume.rdf.widgetkey import WidgetKey, EditKey, GroupOfPropertiesKey, \
    GroupOfValuesKey, TranslationGroupKey, TranslationButtonKey, PlusButtonKey
from plume.rdf.actionsbook import ActionsBook

class WidgetKeyTestCase(unittest.TestCase):
    
    def test_root_key(self):
        """Initialisation d'une clé racine.
        
        """
        rootkey = GroupOfPropertiesKey()
        self.assertTrue(rootkey.is_root)
        
    def test_group_of_values(self):
        """Gestion des lignes dans un groupe de valeurs.
        
        """
        rootkey = GroupOfPropertiesKey()
        groupkey = GroupOfValuesKey(parent=rootkey)
        
        pluskey = PlusButtonKey(parent=groupkey)
        self.assertFalse(pluskey in groupkey.children)
        self.assertEqual(pluskey.row, 0)
        self.assertEqual(groupkey.button, pluskey)
        
        valkey1 = GroupOfPropertiesKey(parent=groupkey)
        self.assertTrue(valkey1 in groupkey.children)
        self.assertEqual(valkey1.row, 0)
        self.assertEqual(pluskey.row, 1)
        self.assertFalse(pluskey.is_hidden_b)
        self.assertTrue(valkey1.is_single_child)
        
        valkey2 = EditKey(parent=groupkey, rowspan=3)
        self.assertEqual(valkey1.row, 0)
        self.assertEqual(valkey2.row, 1)
        self.assertEqual(pluskey.row, 4)
        self.assertFalse(pluskey.is_hidden_b)
        self.assertFalse(valkey1.is_single_child)
        self.assertFalse(valkey2.is_single_child)

        valkey1.kill()
        self.assertFalse(valkey1 in groupkey.children)
        self.assertTrue(valkey2.is_single_child)
        self.assertEqual(valkey2.row, 0)
        self.assertEqual(pluskey.row, 3)


    def test_translation_group(self):
        """Gestion des lignes et des langues dans un groupe de traduction.

        """
        rootkey = GroupOfPropertiesKey()
        groupkey = TranslationGroupKey(
            parent=rootkey,
            available_languages=['fr', 'en', 'it']
            )
        transkey = TranslationButtonKey(parent=groupkey)
        self.assertFalse(transkey in groupkey.children)
        self.assertEqual(transkey.row, 0)
        self.assertEqual(groupkey.button, transkey)

        valkey1 = EditKey(parent=groupkey, rowspan=3,
            widget_language='fr')
        self.assertEqual(valkey1.row, 0)
        self.assertEqual(transkey.row, 3)
        self.assertEqual(groupkey.available_languages, ['en', 'it'])
        self.assertFalse(transkey.is_hidden_b)
        self.assertTrue(valkey1.is_single_child)

        valkey2 = EditKey(parent=groupkey, rowspan=2,
            widget_language='en')
        valkey3 = EditKey(parent=groupkey, rowspan=1,
            widget_language='it')
        self.assertEqual(transkey.row, 6)
        self.assertEqual(groupkey.available_languages, [])
        self.assertTrue(transkey.is_hidden_b)
        self.assertFalse(valkey1.is_single_child)

        valkey2.kill(widget_language='en')
        self.assertFalse(valkey2 in groupkey.children)
        self.assertEqual(groupkey.available_languages, ['en'])
        self.assertFalse(transkey.is_hidden_b)
        self.assertEqual(transkey.row, 4)
        self.assertEqual(valkey3.row, 3)

        valkey4 = EditKey(parent=groupkey, rowspan=2, widget_language='de')
        self.assertTrue(valkey4 in groupkey.children)
        self.assertEqual(groupkey.available_languages, ['en'])
        self.assertFalse(transkey.is_hidden_b)
        valkey4.kill()

        groupkey.language_in('it')
        groupkey.language_out('en')
        self.assertEqual(groupkey.available_languages, ['it'])
        self.assertFalse(transkey.is_hidden_b)

    
    def test_ghost(self):
        """Gestion des branches fantômes.
        
        """
        rootkey = GroupOfPropertiesKey()
        groupkey = GroupOfValuesKey(parent=rootkey, is_ghost=True)
        editkey = EditKey(parent=rootkey, rowspan=2)
        
        self.assertIsNone(groupkey.row)
        self.assertEqual(editkey.row, 0)
        
        valkey1 = GroupOfPropertiesKey(parent=groupkey)
        self.assertTrue(valkey1 in groupkey.children)
        self.assertIsNone(valkey1.row)
        self.assertTrue(valkey1.is_ghost)
        self.assertIsNone(valkey1.is_single_child)

        valkey2 = EditKey(parent=groupkey, is_ghost=False)
        self.assertTrue(valkey2.is_ghost)

        groupkey.kill()
        self.assertFalse(groupkey in rootkey.children)
        self.assertEqual(editkey.row, 0)


    def test_hidden_m(self):
        """Gestion des jumelles.
        
        """
        rootkey = GroupOfPropertiesKey()
        groupkey = GroupOfValuesKey(parent=rootkey)
        buttonkey = PlusButtonKey(parent=groupkey)
        valkey1 = GroupOfPropertiesKey(parent=groupkey, is_hidden_m=True)
        valkey2 = EditKey(parent=groupkey, rowspan=1, m_twin=valkey1)
        valkey3 = EditKey(parent=groupkey, rowspan=3)

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
        valkey1.hide_m()
        self.assertTrue(valkey2.is_hidden_m)
        self.assertFalse(valkey1.is_hidden_m)
        
        valkey3.kill()
        self.assertTrue(valkey1.is_single_child)
        self.assertTrue(valkey2.is_single_child)
        self.assertEqual(valkey1.row, 0)
        self.assertEqual(valkey2.row, 0)
        self.assertEqual(buttonkey.row, 1)
        
        valkey3 = EditKey(parent=groupkey, rowspan=3)
        valkey1.kill()
        self.assertTrue(not valkey1 in groupkey.children)
        self.assertTrue(not valkey2 in groupkey.children)
        self.assertEqual(valkey3.row, 0)
        self.assertTrue(valkey3.is_single_child)
        
        
    def test_delated_computation(self):
        """Calcul a posteriori des lignes et filles uniques.
        
        """
        rootkey = GroupOfPropertiesKey()
        groupkey1 = GroupOfValuesKey(parent=rootkey, no_computation=True)
        buttonkey1 = PlusButtonKey(parent=groupkey1, no_computation=True)
        valkey1a = GroupOfPropertiesKey(parent=groupkey1, no_computation=True)
        valkey1b = EditKey(parent=groupkey1, no_computation=True, rowspan=1,
            m_twin=valkey1a, is_hidden_m=True)
        valkey1c = EditKey(parent=groupkey1, no_computation=True, rowspan=3)
        groupkey2 = TranslationGroupKey(
            parent=rootkey,
            available_languages=['fr', 'en', 'it']
            )
        buttonkey2 = TranslationButtonKey(parent=groupkey2, no_computation=True)
        valkey2 = EditKey(parent=groupkey2, no_computation=True, rowspan=2,
            widget_language='en')
        
        self.assertIsNone(valkey1a.row)
        self.assertIsNone(valkey1b.row)
        self.assertIsNone(valkey1c.row)
        self.assertIsNone(buttonkey1.row)
        self.assertIsNone(valkey1a.is_single_child)
        self.assertIsNone(valkey1b.is_single_child)
        self.assertIsNone(valkey1c.is_single_child)

        self.assertIsNone(valkey2.row)
        self.assertIsNone(buttonkey2.row)
        self.assertIsNone(valkey2.is_single_child)
        
        groupkey1.compute_rows()
        self.assertEqual(valkey1a.row, 0)
        self.assertEqual(valkey1b.row, 0)
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
        rootkey = GroupOfPropertiesKey()
        groupkey1 = GroupOfValuesKey(parent=rootkey)
        buttonkey1 = PlusButtonKey(parent=groupkey1)
        valkey1a = GroupOfPropertiesKey(parent=groupkey1)
        valkey1b = EditKey(parent=groupkey1, rowspan=1,
            m_twin=valkey1a, is_hidden_m=True)
        valkey1c = EditKey(parent=groupkey1, rowspan=3)
        groupkey2 = TranslationGroupKey(
            parent=rootkey,
            available_languages=['fr', 'en', 'it']
            )
        buttonkey2 = TranslationButtonKey(parent=groupkey2)
        valkey2a = EditKey(parent=groupkey2, rowspan=2,
            widget_language='en')
        
        actionsbook = ActionsBook()
        valkey1d = EditKey(parent=groupkey1, rowspan=1, actionsbook=actionsbook)
        self.assertEqual(actionsbook.create, [valkey1d])
        self.assertEqual(actionsbook.drop, [])
        self.assertEqual(actionsbook.move, [valkey1d, buttonkey1])
        self.assertEqual(actionsbook.show_minus_button, [valkey1d])
        self.assertEqual(actionsbook.hide_minus_button, [])
        self.assertEqual(actionsbook.show, [])
        self.assertEqual(actionsbook.hide, [])
        self.assertEqual(actionsbook.languages, [])

        actionsbook = ActionsBook()
        valkey1b.hide_m(actionsbook=actionsbook)
        self.assertEqual(actionsbook.create, [])
        self.assertEqual(actionsbook.drop, [])
        self.assertEqual(actionsbook.move, [])
        self.assertEqual(actionsbook.show_minus_button, [])
        self.assertEqual(actionsbook.hide_minus_button, [])
        self.assertEqual(actionsbook.show, [valkey1b])
        self.assertEqual(actionsbook.hide, [valkey1a])
        self.assertEqual(actionsbook.languages, [])

        actionsbook = ActionsBook()
        valkey2b = EditKey(parent=groupkey2, rowspan=2,
            widget_language='fr', actionsbook=actionsbook)
        self.assertEqual(actionsbook.create, [valkey2b])
        self.assertEqual(actionsbook.drop, [])
        self.assertEqual(actionsbook.move, [valkey2b, buttonkey2])
        self.assertEqual(actionsbook.show_minus_button, [valkey2a, valkey2b])
        self.assertEqual(actionsbook.hide_minus_button, [])
        self.assertEqual(actionsbook.show, [])
        self.assertEqual(actionsbook.hide, [])
        self.assertEqual(actionsbook.languages, [valkey2a, valkey2b])

        actionsbook = ActionsBook()
        valkey2c = EditKey(parent=groupkey2, rowspan=2,
            widget_language='it', actionsbook=actionsbook)
        self.assertEqual(actionsbook.create, [valkey2c])
        self.assertEqual(actionsbook.drop, [])
        self.assertEqual(actionsbook.move, [valkey2c, buttonkey2])
        self.assertEqual(actionsbook.show_minus_button, [valkey2c])
        self.assertEqual(actionsbook.hide_minus_button, [])
        self.assertEqual(actionsbook.show, [])
        self.assertEqual(actionsbook.hide, [buttonkey2])
        self.assertEqual(actionsbook.languages, [valkey2a, valkey2b, valkey2c])

        actionsbook = ActionsBook()
        valkey2a.kill(widget_language='en', actionsbook=actionsbook)
        self.assertEqual(actionsbook.create, [])
        self.assertEqual(actionsbook.drop, [valkey2a])
        self.assertEqual(actionsbook.move, [valkey2b, valkey2c, buttonkey2])
        self.assertEqual(actionsbook.show_minus_button, [])
        self.assertEqual(actionsbook.hide_minus_button, [])
        self.assertEqual(actionsbook.show, [buttonkey2])
        self.assertEqual(actionsbook.hide, [])
        self.assertEqual(actionsbook.languages, [valkey2b, valkey2c])

        actionsbook = ActionsBook()
        groupkey2.language_in('it')
        groupkey2.language_out('en', actionsbook=actionsbook)
        self.assertEqual(actionsbook.create, [])
        self.assertEqual(actionsbook.drop, [])
        self.assertEqual(actionsbook.move, [])
        self.assertEqual(actionsbook.show_minus_button, [])
        self.assertEqual(actionsbook.hide_minus_button, [])
        self.assertEqual(actionsbook.show, [])
        self.assertEqual(actionsbook.hide, [])
        self.assertEqual(actionsbook.languages, [valkey2b, valkey2c])

        actionsbook = ActionsBook()
        valkey2b.kill(widget_language='en', actionsbook=actionsbook)
        self.assertEqual(actionsbook.create, [])
        self.assertEqual(actionsbook.drop, [valkey2b])
        self.assertEqual(actionsbook.move, [valkey2c, buttonkey2])
        self.assertEqual(actionsbook.show_minus_button, [])
        self.assertEqual(actionsbook.hide_minus_button, [valkey2c])
        self.assertEqual(actionsbook.show, [])
        self.assertEqual(actionsbook.hide, [])
        self.assertEqual(actionsbook.languages, [valkey2c])
        
        

unittest.main()
