
import unittest
from plume.rdf.widgetkey import WidgetKey

class WidgetKeyTestCase(unittest.TestCase):
    
    def test_root_key(self):
        """Initialisation d'une clé racine.
        
        """
        rootkey = WidgetKey(kind='group of properties')
        self.assertTrue(rootkey.is_root)
        
    def test_group_of_values(self):
        """Gestion des lignes dans un groupe de valeurs.
        
        """
        rootkey = WidgetKey(kind='group of values')
        
        pluskey = WidgetKey(parent=rootkey, kind='plus button')
        self.assertTrue(pluskey in rootkey.children)
        self.assertEqual(pluskey.row, 0)
        self.assertEqual(rootkey.button, pluskey)
        
        valkey1 = WidgetKey(parent=rootkey, kind='group of properties')
        self.assertTrue(valkey1 in rootkey.children)
        self.assertEqual(valkey1.row, 0)
        self.assertEqual(pluskey.row, 1)
        self.assertFalse(pluskey.hidden_b)
        self.assertTrue(valkey1.hide_minus_button)
        
        valkey2 = WidgetKey(parent=rootkey, kind='edit', rowspan=3)
        self.assertEqual(valkey1.row, 0)
        self.assertEqual(valkey2.row, 1)
        self.assertEqual(pluskey.row, 4)
        self.assertFalse(pluskey.hidden_b)
        self.assertFalse(valkey1.hide_minus_button)
        self.assertFalse(valkey2.hide_minus_button)


    def test_translation_group(self):
        """Gestion des lignes et des langues dans un groupe de traduction.

        """
        rootkey = WidgetKey(
            kind='translation group',
            available_languages=['fr', 'en', 'it']
            )
        transkey = WidgetKey(parent=rootkey, kind='translation button')
        self.assertTrue(transkey in rootkey.children)
        self.assertEqual(transkey.row, 0)
        self.assertEqual(rootkey.button, transkey)

        valkey1 = WidgetKey(parent=rootkey, kind='edit', rowspan=3,
            widget_language='fr')
        self.assertEqual(valkey1.row, 0)
        self.assertEqual(transkey.row, 3)
        self.assertEqual(rootkey.available_languages, ['en', 'it'])
        self.assertFalse(transkey.hidden_b)
        self.assertTrue(valkey1.hide_minus_button)

        valkey2 = WidgetKey(parent=rootkey, kind='edit', rowspan=2,
            widget_language='en')
        valkey3 = WidgetKey(parent=rootkey, kind='edit', rowspan=1,
            widget_language='it')
        self.assertEqual(transkey.row, 6)
        self.assertEqual(rootkey.available_languages, [])
        self.assertTrue(transkey.hidden_b)
        self.assertFalse(valkey1.hide_minus_button)
        

    def test_delated_computation(self):
        pass
        

unittest.main()
