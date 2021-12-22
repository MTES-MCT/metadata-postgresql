
import unittest

from plume.rdf.rdflib import isomorphic
from plume.pg.description import PgDescription
from plume.rdf.utils import abspath, data_from_file
from plume.rdf.widgetsdict import WidgetsDict
from plume.rdf.namespaces import RDF, DCAT, DCT

pg_description_1 = data_from_file(abspath('pg/tests/samples/pg_description_1.txt'))
pg_description_2 = data_from_file(abspath('pg/tests/samples/pg_description_2.txt'))


class DescriptionTestCase(unittest.TestCase):
    
    def test_empty_description(self):
        """Différentes configurations d'entrée, sans métadonnées.
        
        """
        d = {
            'empty string': '',
            'None': None,
            'no JSON-LD': 'Description sans JSON-LD.'
            }
        for k in d:
            raw = d[k]
            with self.subTest(raw=k):
                pgdescr = PgDescription(raw=raw)
                self.assertIsNone(pgdescr.metagraph)
                self.assertEqual(str(pgdescr), raw or '')
                widgetsdict = WidgetsDict(metagraph=pgdescr.metagraph)
                metagraph = widgetsdict.build_metagraph()
                self.assertTrue((None, RDF.type, DCAT.Dataset) in metagraph)
                self.assertTrue((None, DCT.identifier, None) in metagraph)
                pgdescr.metagraph = metagraph
                self.assertTrue(str(pgdescr))

    def test_not_empty_description(self):
        """Différentes configurations d'entrée, avec métadonnées.
        
        """
        d = {
            'pg_description_1.txt': pg_description_1,
            'pg_description_2.txt': pg_description_2
            }
        for k in d:
            raw = d[k]
            with self.subTest(raw=k):
                pgdescr = PgDescription(raw=raw)
                self.assertEqual(raw, str(pgdescr))
                self.assertTrue(pgdescr.metagraph)
                self.assertTrue(str(pgdescr))
                widgetsdict = WidgetsDict(metagraph=pgdescr.metagraph)
                metagraph = widgetsdict.build_metagraph()
                self.assertTrue(isomorphic(metagraph, pgdescr.metagraph))
                pgdescr.metagraph = metagraph
                self.assertEqual(str(pgdescr), raw)

unittest.main()
