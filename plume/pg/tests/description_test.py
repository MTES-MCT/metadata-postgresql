
import unittest

from plume.rdf.rdflib import isomorphic
from plume.pg.description import PgDescription
from plume.rdf.utils import abspath, data_from_file
from plume.rdf.widgetsdict import WidgetsDict
from plume.rdf.metagraph import Metagraph
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
                self.assertFalse(pgdescr.metagraph)
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

    def test_invalid_json_ld(self):
        """Avec un JSON-LD qui n'en est pas vraiment un.
        
        """
        new_comment ="""Avant

<METADATA>
[
  {{
    "@id": "{}",
    "@type": [
      "http://www.w3.org/ns/dcat#Dataset"
    ],
    "http://purl.org/dc/terms/identifier": [
      {{
        "@value": "{}"
      }}
    ]
  }}
]
</METADATA>
Après"""
        
        # --- pas un JSON ---
        raw = "Avant<METADATA> Ceci n'est pas un JSON-LD </METADATA>Après"
        pgdescr = PgDescription(raw)
        self.assertEqual(pgdescr.ante, 'Avant')
        self.assertEqual(pgdescr.post, 'Après')
        self.assertEqual(pgdescr.jsonld, '')
        self.assertFalse(pgdescr.metagraph)
        widgetsdict = WidgetsDict(metagraph=pgdescr.metagraph)
        metagraph = widgetsdict.build_metagraph()
        pgdescr.metagraph = metagraph
        self.assertEqual(str(pgdescr), new_comment.format(
            str(metagraph.datasetid), str(metagraph.datasetid.uuid)))
        
        # --- JSON mais pas JSON-LD ---
        raw = 'Avant<METADATA> {"key": "value"} </METADATA>Après'
        pgdescr = PgDescription(raw)
        self.assertEqual(pgdescr.ante, 'Avant')
        self.assertEqual(pgdescr.post, 'Après')
        self.assertEqual(pgdescr.jsonld, ' {"key": "value"} ')
        self.assertTrue(isinstance(pgdescr.metagraph, Metagraph))
        self.assertFalse(pgdescr.metagraph)
        widgetsdict = WidgetsDict(metagraph=pgdescr.metagraph)
        metagraph = widgetsdict.build_metagraph()
        pgdescr.metagraph = metagraph
        self.assertEqual(str(pgdescr), new_comment.format(
            str(metagraph.datasetid), str(metagraph.datasetid.uuid)))
            
        # --- balises vides ---
        raw = 'Avant<METADATA></METADATA>Après'
        pgdescr = PgDescription(raw)
        self.assertEqual(pgdescr.ante, 'Avant')
        self.assertEqual(pgdescr.post, 'Après')
        self.assertEqual(pgdescr.jsonld, '')
        self.assertFalse(pgdescr.metagraph)
        widgetsdict = WidgetsDict(metagraph=pgdescr.metagraph)
        metagraph = widgetsdict.build_metagraph()
        pgdescr.metagraph = metagraph
        self.assertEqual(str(pgdescr), new_comment.format(
            str(metagraph.datasetid), str(metagraph.datasetid.uuid)))

if __name__ == '__main__':
    unittest.main()

