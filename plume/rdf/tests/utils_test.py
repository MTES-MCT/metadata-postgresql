
import unittest
from uuid import uuid4

from plume.rdf.rdflib import Literal, URIRef
from plume.rdf.utils import sort_by_language, pick_translation, \
    path_from_n3, int_from_duration, duration_from_int, str_from_duration, \
    wkt_with_srid, split_rdf_wkt
from plume.rdf.namespaces import PlumeNamespaceManager, DCT, XSD

nsm = PlumeNamespaceManager()

class UtilsTestCase(unittest.TestCase):

    def test_split_rfd_wkt(self):
        """Extraction du référentiel et de la géométrie d'un WKT RDF.
        
        """
        self.assertEqual(
            split_rdf_wkt('<http://www.opengis.net/def/crs/EPSG/0/2154> ' \
                'POINT(651796.32814998598769307 6862298.58582336455583572)'),
            ('POINT(651796.32814998598769307 6862298.58582336455583572)', 'EPSG:2154')
            )
        self.assertEqual(
            split_rdf_wkt('<http://www.opengis.net/def/crs/EPSG/0/2154> ' \
                '      POINT(651796.32814998598769307 6862298.58582336455583572)'),
            ('POINT(651796.32814998598769307 6862298.58582336455583572)', 'EPSG:2154')
            )
        self.assertEqual(
            split_rdf_wkt('POINT(651796.32814998598769307 6862298.58582336455583572)'),
            ('POINT(651796.32814998598769307 6862298.58582336455583572)', 'OGC:WGS84')
            )
        self.assertIsNone(
            split_rdf_wkt('<chose> POINT(651796.32814998598769307 ' \
                '6862298.58582336455583572)')
            )
        self.assertIsNone(
           split_rdf_wkt('<http://www.opengis.net/def/crs/EPSG/0/2154>     ')
           )
        self.assertIsNone(
            split_rdf_wkt('<http://www.opengis.net/def/crs/EPSG/0/21??54> ' \
                'POINT(651796.32814998598769307 6862298.58582336455583572)')
            )

    def test_wkt_with_srid(self):
        """Explicitation du référentiel dans un WKT.
        
        """
        self.assertEqual(
            wkt_with_srid('POINT(651796.32814998598769307 6862298.58582336455583572)',
                'OGC:CRS84'),
            '<http://www.opengis.net/def/crs/OGC/1.3/CRS84> ' \
            'POINT(651796.32814998598769307 6862298.58582336455583572)'
            )
        self.assertEqual(
            wkt_with_srid('POINT(651796.32814998598769307 6862298.58582336455583572)',
                'EPSG:2154'),
            '<http://www.opengis.net/def/crs/EPSG/0/2154> ' \
            'POINT(651796.32814998598769307 6862298.58582336455583572)'
            )
        self.assertEqual(
            wkt_with_srid('POINT(651796.32814998598769307 6862298.58582336455583572)',
                'IGNF:RGM04UTM38S'),
            '<https://registre.ign.fr/ign/IGNF/IGNF.xml#RGM04UTM38S> ' \
            'POINT(651796.32814998598769307 6862298.58582336455583572)'
            )
        self.assertIsNone(wkt_with_srid(None, 'IGNF:RGM04UTM38S'))
        self.assertIsNone(
            wkt_with_srid('POINT(651796.32814998598769307 6862298.58582336455583572)',
                'CHOSE:CRS84'))
        self.assertEqual(
            wkt_with_srid('POINT(651796.32814998598769307 6862298.58582336455583572)',
                None),
            'POINT(651796.32814998598769307 6862298.58582336455583572)'
            )

    def test_sort_by_language(self):
        """Tri d'une liste de valeurs litérales selon leur langue.
        
        """
        l1 = [Literal('My Title', lang='en'), Literal('Mon titre', lang='fr'),
            'Mon autre titre', Literal('Mein Titel', lang='de')]
        l2 = [Literal('Mon titre', lang='fr'), Literal('Mein Titel', lang='de'),
            Literal('My Title', lang='en'), 'Mon autre titre']
        langlist = ('fr', 'de')
        sort_by_language(l1, langlist)
        self.assertEqual(l1, l2) 

    def test_pick_translation(self):
        """Choix d'une traduction.
        
        """
        langlist = ('fr', 'de')
        l = [Literal('My Title', lang='en'), Literal('Mon titre', lang='fr'),
	    'Mon autre titre', Literal('Mein Titel', lang='de')]
        self.assertEqual(pick_translation(l, langlist), Literal('Mon titre', lang='fr'))
        self.assertEqual(pick_translation(l, 'de'), Literal('Mein Titel', lang='de'))
        self.assertEqual(pick_translation(l, 'it'), Literal('My Title', lang='en'))

    def test_path_from_n3(self):
        """Reconstruction d'un chemin d'URI à partir d'un chemin N3.

        """
        p = path_from_n3('dct:title / dct:description', nsm=nsm)
        self.assertEqual(p, DCT.title / DCT.description)
        uuid = uuid4()
        p = path_from_n3('<{}>'.format(uuid.urn), nsm=nsm)
        self.assertEqual(p, URIRef(uuid.urn))
    
    def test_int_from_duration(self):
        """Extraction de l'entier le plus significatif d'une durée.
        
        """
        self.assertEqual(
            int_from_duration(Literal('P2Y', datatype=XSD.duration)),
            (2, 'ans')
            )
        self.assertEqual(
            int_from_duration(Literal('P2YT1H', datatype=XSD.duration)),
            (2, 'ans')
            )
        self.assertEqual(
            int_from_duration(Literal('PYT1H', datatype=XSD.duration)),
            (1, 'heures')
            )
        self.assertEqual(
            int_from_duration(Literal('PT1H3M', datatype=XSD.duration)),
            (1, 'heures')
            )
        self.assertEqual(
            int_from_duration(Literal('PT3M', datatype=XSD.duration)),
            (3, 'min.')
            )
        self.assertEqual(int_from_duration(Literal('P2Y')), (None, None))
        self.assertEqual(int_from_duration('P2Y'), (None, None))
        self.assertEqual(int_from_duration(None), (None, None))

    def test_duration_from_int(self):
        """Désérialisation RDF d'une durée sous forme valeur + unité.
        
        """
        self.assertEqual(duration_from_int(2, 'ans'),
            Literal('P2Y', datatype=XSD.duration))
        self.assertEqual(duration_from_int(-2, 'ans'),
            Literal('-P2Y', datatype=XSD.duration))
        self.assertEqual(duration_from_int(3, 'min.'),
            Literal('PT3M', datatype=XSD.duration))
        self.assertEqual(duration_from_int('3', 'min.'),
            Literal('PT3M', datatype=XSD.duration))
        self.assertEqual(duration_from_int('-3', 'min.'),
            Literal('-PT3M', datatype=XSD.duration))
        self.assertIsNone(duration_from_int(3, 'chose'))
        self.assertIsNone(duration_from_int(3, None))
        self.assertIsNone(duration_from_int('chose', 'min.'))

    def test_str_from_duration(self):
        """Jolie représentation textuelle d'une durée.
        
        """
        self.assertEqual(
            str_from_duration(Literal('P2Y', datatype=XSD.duration)),
            ('2 ans')
            )
        self.assertEqual(
            str_from_duration(Literal('P1YT1H', datatype=XSD.duration)),
            ('1 an')
            )
        self.assertEqual(
            str_from_duration(Literal('PYT1H3M', datatype=XSD.duration)),
            ('1 heure')
            )
        self.assertEqual(
            str_from_duration(Literal('P1M', datatype=XSD.duration)),
            ('1 mois')
            )
        self.assertEqual(str_from_duration(Literal('P2Y')), None)

if __name__ == '__main__':
    unittest.main()

