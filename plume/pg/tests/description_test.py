
import unittest

from plume.rdf.rdflib import isomorphic
from plume.pg.description import PgDescription, truncate_metadata
from plume.rdf.utils import abspath, data_from_file
from plume.rdf.widgetsdict import WidgetsDict
from plume.rdf.metagraph import Metagraph
from plume.rdf.namespaces import RDF, DCAT, DCT, FOAF

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
                self.assertTrue((None, FOAF.isPrimaryTopicOf, None) in metagraph)
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
                metagraph = widgetsdict.build_metagraph(preserve_metadata_date=True)
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
        metagraph = widgetsdict.build_metagraph(preserve_metadata_date=True)
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
        metagraph = widgetsdict.build_metagraph(preserve_metadata_date=True)
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
        metagraph = widgetsdict.build_metagraph(preserve_metadata_date=True)
        pgdescr.metagraph = metagraph
        self.assertEqual(str(pgdescr), new_comment.format(
            str(metagraph.datasetid), str(metagraph.datasetid.uuid)))

    def test_truncate_metadata(self):
        """Quelques tests de suppression des métadonnées dans un texte.

        """
        # avec métadonnées contenant un libellé
        text = pg_description_1 + '\ntable\ngeom MultiPolygon (srid 2154)\n'
        self.assertEqual(truncate_metadata(text), (
'''IGN Admin Express. Départements 2021-01.

table
geom MultiPolygon (srid 2154)''',
            'Des métadonnées sont disponibles pour cette couche. ' \
            'Activez Plume pour les consulter.'))
        self.assertEqual(truncate_metadata(text, with_title=True), (
'''IGN Admin Express. Départements 2021-01.

ADMIN EXPRESS - Départements de métropole

table
geom MultiPolygon (srid 2154)''',
            'Des métadonnées sont disponibles pour cette couche. ' \
            'Activez Plume pour les consulter.'))

        # sans métadonnées
        self.assertEqual(truncate_metadata('table\ngeom MultiPolygon (srid 2154)\n'),
            ('table\ngeom MultiPolygon (srid 2154)', None))
        self.assertEqual(truncate_metadata('table\ngeom MultiPolygon (srid 2154)\n',
            with_title=True), ('table\ngeom MultiPolygon (srid 2154)', None))
        self.assertEqual(truncate_metadata(''), ('', None))
        self.assertEqual(truncate_metadata('', with_title=True), ('', None))

        # avec métadonnées, mais sans libellé
        text ="""Avant

<METADATA>
[
  {
    "@id": "urn:uuid:479fd670-32c5-4ade-a26d-0268b0ce5046",
    "@type": [
      "http://www.w3.org/ns/dcat#Dataset"
    ],
    "http://purl.org/dc/terms/identifier": [
      {
        "@value": "479fd670-32c5-4ade-a26d-0268b0ce5046"
      }
    ]
  }
]
</METADATA>
Après"""
        self.assertEqual(truncate_metadata(text, with_title=True), (
'''Avant

Après''',
            'Des métadonnées sont disponibles pour cette couche. ' \
            'Activez Plume pour les consulter.'))
        self.assertEqual(truncate_metadata(text, with_title=False), (
'''Avant

Après''',
            'Des métadonnées sont disponibles pour cette couche. ' \
            'Activez Plume pour les consulter.'))

        # pas de texte avant
        text ="""<METADATA>
[
  {
    "@id": "urn:uuid:479fd670-32c5-4ade-a26d-0268b0ce5046",
    "@type": [
      "http://www.w3.org/ns/dcat#Dataset"
    ],
    "http://purl.org/dc/terms/identifier": [
      {
        "@value": "479fd670-32c5-4ade-a26d-0268b0ce5046"
      }
    ],
    "http://purl.org/dc/terms/title": [
      {
        "@language": "fr",
        "@value": "ADMIN EXPRESS - Départements de métropole"
      }
    ]
  }
]
</METADATA>

Après"""
        self.assertEqual(truncate_metadata(text, with_title=True), (
'''ADMIN EXPRESS - Départements de métropole

Après''',
            'Des métadonnées sont disponibles pour cette couche. ' \
            'Activez Plume pour les consulter.'))
        self.assertEqual(truncate_metadata(text, with_title=False), (
'''Après''',
            'Des métadonnées sont disponibles pour cette couche. ' \
            'Activez Plume pour les consulter.'))

        # pas de texte après
        text ="""Avant
<METADATA>
[
  {
    "@id": "urn:uuid:479fd670-32c5-4ade-a26d-0268b0ce5046",
    "@type": [
      "http://www.w3.org/ns/dcat#Dataset"
    ],
    "http://purl.org/dc/terms/identifier": [
      {
        "@value": "479fd670-32c5-4ade-a26d-0268b0ce5046"
      }
    ],
    "http://purl.org/dc/terms/title": [
      {
        "@language": "fr",
        "@value": "ADMIN EXPRESS - Départements de métropole"
      }
    ]
  }
]
</METADATA>"""
        self.assertEqual(truncate_metadata(text, with_title=True), (
'''Avant

ADMIN EXPRESS - Départements de métropole''',
            'Des métadonnées sont disponibles pour cette couche. ' \
            'Activez Plume pour les consulter.'))
        self.assertEqual(truncate_metadata(text, with_title=False), (
'''Avant''',
            'Des métadonnées sont disponibles pour cette couche. ' \
            'Activez Plume pour les consulter.'))

if __name__ == '__main__':
    unittest.main()

