
import unittest
from uuid import uuid4

from plume.rdf.rdflib import Literal, URIRef
from plume.rdf.utils import sort_by_language, pick_translation, \
    path_from_n3, int_from_duration, duration_from_int, str_from_duration, \
    wkt_with_srid, split_rdf_wkt, str_from_datetime, str_from_date, \
    str_from_time, datetime_from_str, date_from_str, time_from_str, \
    str_from_decimal, decimal_from_str
from plume.rdf.namespaces import PlumeNamespaceManager, DCT, XSD

nsm = PlumeNamespaceManager()

class UtilsTestCase(unittest.TestCase):

    def test_decimal_from_str(self):
        """Désérialisation en littéral RDF d'un nombre décimal sous forme de chaîne de caractères.
        
        """
        self.assertEqual(
            Literal('0.25', datatype=XSD.decimal),
            decimal_from_str('0,25')
            )
        self.assertEqual(
            Literal('-1.25', datatype=XSD.decimal),
            decimal_from_str('-1,25')
            )
        self.assertEqual(
            Literal('+100000.25', datatype=XSD.decimal),
            decimal_from_str('+100 000.25')
            )
        self.assertEqual(
            Literal('.25', datatype=XSD.decimal),
            decimal_from_str('.25')
            )
        self.assertEqual(
            Literal('25', datatype=XSD.decimal),
            decimal_from_str('25')
            )
        self.assertEqual(
            Literal('0', datatype=XSD.decimal),
            decimal_from_str('0')
            )
        self.assertIsNone(decimal_from_str(None))
        self.assertIsNone(decimal_from_str('chose'))

    def test_time_from_str(self):
        """Désérialisation en littéral RDF d'une heure sous forme de chaîne de caractères.
        
        """
        self.assertEqual(
            time_from_str('15:30:14'),
            Literal('15:30:14', datatype=XSD.time)
            )
        self.assertEqual(
            time_from_str('15:30:14.444'),
            Literal('15:30:14', datatype=XSD.time)
            )
        self.assertIsNone(time_from_str(None))
        self.assertIsNone(time_from_str('chose'))
        self.assertIsNone(time_from_str('24:30:14'))
        self.assertIsNone(time_from_str('21:70:14'))
        self.assertIsNone(time_from_str('21:10:84'))

    def test_datetime_from_str(self):
        """Désérialisation en littéral RDF d'une date avec heure sous forme de chaîne de caractères.
        
        """
        self.assertEqual(
            datetime_from_str('13/02/2022 15:30:14'),
            Literal('2022-02-13T15:30:14', datatype=XSD.dateTime)
            )
        self.assertEqual(
            datetime_from_str('13/02/2022 15:30:14.444'),
            Literal('2022-02-13T15:30:14', datatype=XSD.dateTime)
            )
        self.assertEqual(
            datetime_from_str('13/02/2022'),
            Literal('2022-02-13T00:00:00', datatype=XSD.dateTime)
            )
        self.assertEqual(
            datetime_from_str('13/02/2022 chose'),
            Literal('2022-02-13T00:00:00', datatype=XSD.dateTime)
            )
        self.assertIsNone(datetime_from_str(None))
        self.assertIsNone(datetime_from_str('chose'))

    def test_date_from_str(self):
        """Désérialisation en littéral RDF d'une date sous forme de chaîne de caractères.
        
        """
        self.assertEqual(
            date_from_str('13/02/2022'),
            Literal('2022-02-13', datatype=XSD.date)
            )
        self.assertEqual(
            date_from_str('13/02/2022 15:30:14'),
            Literal('2022-02-13', datatype=XSD.date)
            )
        self.assertIsNone(date_from_str(None))
        self.assertIsNone(date_from_str('chose'))
        self.assertIsNone(date_from_str('13/02/24'))
        self.assertIsNone(date_from_str('32/02/2022'))
        self.assertIsNone(date_from_str('10/13/2022'))

    def test_str_from_decimal(self):
        """Représentation d'un décimal RDF sous forme de chaîne de caractères.
        
        """
        self.assertEqual(
            str_from_decimal(Literal('0.25', datatype=XSD.decimal)),
            '0,25'
            )
        self.assertEqual(
            str_from_decimal(Literal('-1.25', datatype=XSD.decimal)),
            '-1,25'
            )
        self.assertEqual(
            str_from_decimal(Literal('.25', datatype=XSD.decimal)),
            '0,25'
            )
        self.assertEqual(
            str_from_decimal(Literal('25', datatype=XSD.decimal)),
            '25'
            )
        self.assertEqual(
            str_from_decimal(Literal('0', datatype=XSD.decimal)),
            '0'
            )
        self.assertIsNone(str_from_decimal(None))
        self.assertIsNone(str_from_decimal('chose'))
        self.assertIsNone(str_from_decimal(Literal('chose')))
        self.assertIsNone(str_from_decimal(Literal('chose', datatype=XSD.decimal)))

    def test_str_from_time(self):
        """Représentation d'une heure sous forme de chaîne de caractères.
        
        """
        self.assertEqual(
            str_from_time(Literal('15:30:14', datatype=XSD.time)),
            '15:30:14'
            )
        self.assertEqual(
            str_from_time(Literal('15:30:14.444', datatype=XSD.time)),
            '15:30:14'
            )
        self.assertIsNone(str_from_time(None))
        self.assertIsNone(str_from_time('chose'))
        self.assertIsNone(str_from_time(Literal('chose')))
        self.assertIsNone(str_from_time(Literal('chose', datatype=XSD.time)))

    def test_str_from_date(self):
        """Représentation d'une date sous forme de chaîne de caractères.
        
        """
        self.assertEqual(
            str_from_date(Literal('2022-02-12', datatype=XSD.date)),
            '12/02/2022'
            )
        self.assertEqual(
            str_from_date(Literal('2022-02-12T03:00:00', datatype=XSD.date)),
            '12/02/2022'
            )
        self.assertIsNone(str_from_date(None))
        self.assertIsNone(str_from_date('chose'))
        self.assertIsNone(str_from_date(Literal('chose')))
        self.assertIsNone(str_from_date(Literal('chose', datatype=XSD.date)))

    def test_str_from_datetime(self):
        """Représentation d'une date avec heure sous forme de chaîne de caractères.
        
        """
        self.assertEqual(
            str_from_datetime(Literal('2022-02-12T03:00:00', datatype=XSD.dateTime)),
            '12/02/2022 03:00:00'
            )
        self.assertIsNone(str_from_datetime(None))
        self.assertIsNone(str_from_datetime('chose'))
        self.assertIsNone(str_from_datetime(Literal('chose')))
        self.assertIsNone(str_from_datetime(Literal('chose', datatype=XSD.dateTime)))
        self.assertIsNone(str_from_datetime(Literal('2022-02-12', datatype=XSD.dateTime)))

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

