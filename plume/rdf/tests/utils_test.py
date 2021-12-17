
import unittest
from rdflib import Literal

from plume.rdf.utils import sort_by_language, pick_translation

class UtilsTestCase(unittest.TestCase):

    def test_sort_by_language(self):
        """Tri d'une liste de valeurs litérales selon leur langue.
        
        """
        l1 = [Literal('My Title', lang='en'), Literal('Mon titre', lang='fr'),
                'Mon autre titre', Literal('Mein Titel', lang='de')]
        l2 = [Literal('Mon titre', lang='fr'), Literal('Mein Titel', lang='de'),
                Literal('My Title', lang='en'), 'Mon autre titre']
        langlist = ['fr', 'de']
        sort_by_language(l1, langlist)
        self.assertEqual(l1, l2) 

    def test_pick_translation(self):
        """Choix d'une traduction.
        
        """
        langlist = ['fr', 'de']
        l = [Literal('My Title', lang='en'), Literal('Mon titre', lang='fr'),
			'Mon autre titre', Literal('Mein Titel', lang='de')]
        self.assertEqual(pick_translation(l, langlist), Literal('Mon titre', lang='fr'))
        self.assertEqual(pick_translation(l, 'de'), Literal('Mein Titel', lang='de'))
        self.assertEqual(pick_translation(l, 'it'), Literal('My Title', lang='en'))

unittest.main()
