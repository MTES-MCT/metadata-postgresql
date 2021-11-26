
import unittest
from plume.rdf.widgetkey import WidgetKey, EditKey, GroupOfPropertiesKey, \
    GroupOfValuesKey, TranslationGroupKey, TranslationButtonKey, PlusButtonKey

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
        

    def test_delated_computation(self):
        pass
        

unittest.main()
