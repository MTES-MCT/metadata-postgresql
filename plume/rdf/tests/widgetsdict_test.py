
import unittest

from plume.rdf.widgetsdict import WidgetsDict
from plume.rdf.namespaces import DCAT, DCT

class WidgetsDictTestCase(unittest.TestCase):
    
    def test_widgetsdict_empty_edit(self):
        """Génération d'un dictionnaire de widgets sans graphe ni modèle.

        Ce premier test vérifie essentiellement
        que toutes les informations du dictionnaire
        interne sont correctement générées, dans le
        cas simple d'un dictionnaire en mode édition.
        
        """
        widgetsdict = WidgetsDict()
        self.assertEqual(widgetsdict.main_language, 'fr')
        self.assertTrue(widgetsdict.edit)
        self.assertFalse(widgetsdict.translation)
        key = widgetsdict.root.search_from_path(DCT.temporal / DCAT.startDate)
        self.assertIsNotNone(key)
        self.assertEqual(widgetsdict[key]['label'], 'Date de début')
        self.assertTrue(widgetsdict[key]['has label'])
        self.assertFalse(widgetsdict[key]['hidden'])
        self.assertEqual(widgetsdict[key]['main widget type'], 'QDateEdit')
        

    def test_widgetsdict_hidden_keys(self):
        """Génération d'un dictionnaire de widgets avec paramètres masquant certaines informations.

        """
	

if __name__ == '__main__':
    unittest.main()

