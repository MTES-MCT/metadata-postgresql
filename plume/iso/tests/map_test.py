
import unittest

from plume.rdf.utils import (
    abspath, data_from_file, DatasetId, owlthing_from_email,
    owlthing_from_tel
)
from plume.iso.map import (
    find_iri, find_literal, parse_xml, ISO_NS, normalize_crs,
    IsoToDcat, normalize_language, find_values, normalize_decimal,
    date_or_datetime_to_literal, to_spatial_resolution_in_meters
)
from plume.rdf.namespaces import (
    DCT, FOAF, DCAT, PLUME, ADMS, SKOS, XSD, OWL, DQV,
    GEODCAT
)
from plume.rdf.rdflib import Literal, URIRef
from plume.rdf.metagraph import metagraph_from_iso
from plume.rdf.widgetsdict import WidgetsDict

class IsoMapTestCase(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Import des fichiers de test.
        
        """
        cls.IGN_BDALTI = parse_xml(
            data_from_file(abspath('rdf/tests/samples/iso_ignf_bdaltir_2_0.xml'))
        )
        cls.CSW_DATARA_FOND_AB = parse_xml(
            data_from_file(abspath('rdf/tests/samples/iso_datara_territoire_fonds_air_bois.xml'))
        )
        cls.CSW_GEOIDE_ZAC_75 = parse_xml(
            data_from_file(abspath('rdf/tests/samples/iso_geoide_zac_paris.xml'))
        )
        cls.CSW_GEOLITTORAL_SENTIER = parse_xml(
            data_from_file(abspath('rdf/tests/samples/iso_geolittoral_sentier_du_littoral.xml'))
        )
        cls.ALL = {
            'iso_datara_territoire_fonds_air_bois': cls.CSW_DATARA_FOND_AB,
            'iso_geoide_zac_paris': cls.CSW_GEOIDE_ZAC_75,
            'iso_ignf_bdaltir_2_0': cls.IGN_BDALTI,
            'iso_geolittoral_sentier_du_littoral': cls.CSW_GEOLITTORAL_SENTIER
        }
    
    def test_parse_xml(self):
        for isoxml_name, isoxml in IsoMapTestCase.ALL.items():
            with self.subTest(file=f'{isoxml_name}.xml'):
                self.assertIsNotNone(isoxml.find('gmd:identificationInfo', ISO_NS))
    
    def test_find_values(self):
        """Récupération de valeurs dans un XML."""
        self.assertListEqual(
            find_values(
                self.CSW_GEOIDE_ZAC_75, 
                './gmd:language/gmd:LanguageCode'
            ),
            [
                'fre'
            ]
        )
        self.assertListEqual(
            find_values(
                self.CSW_GEOIDE_ZAC_75, 
                './gmd:language/gmd:LanguageCode@codeList'
            ),
            [
                'http://www.loc.gov/standards/iso639-2/'
            ]
        )
        self.assertListEqual(
            find_values(
                self.CSW_GEOIDE_ZAC_75, 
                [
                    './gmd:language/gmd:LanguageCode@codeList',
                    './gmd:language/gmd:LanguageCode'
                ]
            ),
            [
                'http://www.loc.gov/standards/iso639-2/',
                'fre'
            ]
        )
        self.assertListEqual(
            find_values(
                self.CSW_GEOIDE_ZAC_75, 
                './gmd:language/nowhere'
            ),
            []
        )

    def test_find_literal_with_list_of_paths(self):
        dataset_id = DatasetId()

        ids = find_literal(
            IsoMapTestCase.IGN_BDALTI, 
            ['./gmd:falsePath', './gmd:fileIdentifier/gco:CharacterString'],
            dataset_id,
            DCT.identifier,
            multi=False
        )
        self.assertListEqual(
            ids,
            [
                (dataset_id, DCT.identifier, Literal('IGNF_BDALTIr_2-0.xml'))
            ]
        )

        ids = find_literal(
            IsoMapTestCase.IGN_BDALTI, 
            [
                './gmd:identificationInfo/gmd:MD_DataIdentification/'
                    'gmd:citation/gmd:CI_Citation/gmd:identifier/'
                    'gmd:MD_Identifier/gmd:code/gco:CharacterString',
                './gmd:fileIdentifier/gco:CharacterString'
            ],
            dataset_id,
            DCT.identifier,
            multi=True
        )
        self.assertListEqual(
            ids,
            [
                (dataset_id, DCT.identifier, Literal('IGNF_BDALTIr_2-0')),
                (dataset_id, DCT.identifier, Literal('IGNF_BDALTIr_2-0.xml'))
            ]
        )

        ids = find_literal(
            IsoMapTestCase.IGN_BDALTI, 
            [
                './gmd:identificationInfo/gmd:MD_DataIdentification/'
                    'gmd:citation/gmd:CI_Citation/gmd:identifier/'
                    'gmd:MD_Identifier/gmd:code/gco:CharacterString',
                './gmd:fileIdentifier/gco:CharacterString'
            ],
            dataset_id,
            DCT.identifier,
            multi=False
        )
        self.assertListEqual(
            ids,
            [
                (dataset_id, DCT.identifier, Literal('IGNF_BDALTIr_2-0'))
            ]
        )

    def test_find_literal_with_attribute(self):
        """Récupération de la valeur d'un attribut."""
        dataset_id = DatasetId()

        ids = find_literal(
            IsoMapTestCase.IGN_BDALTI, 
            './gmd:language/gmd:LanguageCode@codeListValue',
            dataset_id,
            DCT.language,
            multi=False
        )
        self.assertListEqual(
            ids,
            [
                (dataset_id, DCT.language, Literal('fre'))
            ]
        )

    def test_find_iri(self):
        simple_xml = parse_xml(
            """<?xml version="1.0" encoding="UTF-8"?>
            <gmd:MD_Metadata xmlns:gmd="http://www.isotc211.org/2005/gmd">
                <b>
                    <c>https://www.postgresql.org/docs/14</c>
                    <c>https://www.postgresql.org/docs/12</c>
                </b>
                <d>
                    <c>https://www.postgresql.org/docs/13</c>
                </d>
                <e>0123456789</e>
                <f>john.smith@somewhere.com</f>
                <g>http://inspire.ec.europa.eu/metadata-codelist/TopicCategory/boundaries</g>
                <h>Boundaries</h>
                <i epsg="http://www.opengis.net/def/crs/EPSG/0/3857">EPSG 2975 : RGR92 / UTM zone 40S (La Réunion)</i>
            </gmd:MD_Metadata>
            """
        )

        dataset_id = DatasetId()

        iris = find_iri(
            simple_xml,
            ['./z', './b/c', './d/c'],
            dataset_id,
            FOAF.page,
            multi=False
        )
        self.assertListEqual(
            iris,
            [
                (
                    dataset_id, FOAF.page,
                    URIRef('https://www.postgresql.org/docs/14')
                )
            ]
        )

        iris = find_iri(
            simple_xml,
            ['./z', './b/c', './d/c'],
            dataset_id,
            FOAF.page,
            multi=True
        )
        self.assertListEqual(
            iris,
            [
                (
                    dataset_id, FOAF.page,
                    URIRef('https://www.postgresql.org/docs/14')
                ),
                (
                    dataset_id, FOAF.page,
                    URIRef('https://www.postgresql.org/docs/12')
                ),
                (
                    dataset_id, FOAF.page,
                    URIRef('https://www.postgresql.org/docs/13')
                )
            ]
        )

        iris = find_iri(
            simple_xml,
            './e',
            dataset_id,
            FOAF.phone,
            transform=owlthing_from_tel
        )
        self.assertListEqual(
            iris,
            [(dataset_id, FOAF.phone, URIRef('tel:+33-1-23-45-67-89'))]
        )

        iris = find_iri(
            simple_xml,
            './f',
            dataset_id,
            FOAF.mbox,
            transform=owlthing_from_email
        )
        self.assertListEqual(
            iris,
            [(dataset_id, FOAF.mbox, URIRef('mailto:john.smith@somewhere.com'))]
        )
        
        iris = find_iri(
            simple_xml,
            './g',
            dataset_id,
            DCAT.theme,
            thesaurus=(
                URIRef('http://inspire.ec.europa.eu/metadata-codelist/TopicCategory'),
                ('fr',)
            )
        )
        self.assertListEqual(
            iris,
            [
                (
                    dataset_id,
                    DCAT.theme,
                    URIRef('http://inspire.ec.europa.eu/metadata-codelist/TopicCategory/boundaries')
                )
            ]
        )

        iris = find_iri(
            simple_xml,
            './h',
            dataset_id,
            DCAT.theme,
            thesaurus=(
                URIRef('http://inspire.ec.europa.eu/metadata-codelist/TopicCategory'),
                ('en',)
            )
        )
        self.assertListEqual(
            iris,
            [
                (
                    dataset_id,
                    DCAT.theme,
                    URIRef('http://inspire.ec.europa.eu/metadata-codelist/TopicCategory/boundaries')
                )
            ]
        )

        # avec une liste de thésaurus
        iris = find_iri(
            simple_xml,
            './h',
            dataset_id,
            DCAT.theme,
            thesaurus=[
                (
                    URIRef('http://inspire.ec.europa.eu/metadata-codelist/MaintenanceFrequency'),
                    ('fr',)
                ),
                (
                    URIRef('http://inspire.ec.europa.eu/metadata-codelist/TopicCategory'),
                    ('en',)
                )
            ]
        )
        self.assertListEqual(
            iris,
            [
                (
                    dataset_id,
                    DCAT.theme,
                    URIRef('http://inspire.ec.europa.eu/metadata-codelist/TopicCategory/boundaries')
                )
            ]
        )

        # avec un attribut
        iris = find_iri(
            simple_xml,
            './i@epsg',
            dataset_id,
            DCT.conformsTo,
            thesaurus=(
                URIRef('http://www.opengis.net/def/crs/EPSG/0'),
                ('fr', 'en')
            ),
            multi=True
        )
        self.assertListEqual(
            iris,
            [
                (
                    dataset_id,
                    DCT.conformsTo,
                    URIRef('http://www.opengis.net/def/crs/EPSG/0/3857')
                )
            ]
        )

        iris = find_iri(
            simple_xml,
            ['./i@epsg', './i'],
            dataset_id,
            DCT.conformsTo,
            thesaurus=[
                (
                    URIRef('http://www.opengis.net/def/crs/EPSG/0'),
                    ('fr', 'en')
                ),
                (
                    PLUME.OgcEpsgFrance,
                    ('fr', 'en')
                )
            ],
            multi=True
        )
        self.assertListEqual(
            iris,
            [
                (
                    dataset_id,
                    DCT.conformsTo,
                    URIRef('http://www.opengis.net/def/crs/EPSG/0/3857')
                ),
                (
                    dataset_id,
                    DCT.conformsTo,
                    URIRef('http://www.opengis.net/def/crs/EPSG/0/2975')
                )
            ]
        )

    def test_normalize_decimal(self):
        """Contrôle le fonctionnement de la fonction de normalisation des décimaux."""
        self.assertEqual(normalize_decimal('18'), '18')
        self.assertEqual(normalize_decimal('0'), '0')
        self.assertEqual(normalize_decimal('18.20'), '18.20')
        self.assertEqual(normalize_decimal('+18.20'), '+18.20')
        self.assertEqual(normalize_decimal('18,20'), '18.20')
        self.assertEqual(normalize_decimal('1,800.20'), '1800.20')
        self.assertEqual(normalize_decimal('-1 800.20'), '-1800.20')
        self.assertEqual(normalize_decimal('1 800,20'), '1800.20')
        self.assertEqual(normalize_decimal('.20'), '.20')
        self.assertIsNone(normalize_decimal(''))
        self.assertIsNone(normalize_decimal(None))

    def test_normalize_crs(self):
        """Vérifie que la fonction qui extrait un référentiel de coordonnées d'une chaîne de caractères réagit bien dans les cas de figure anticipés."""

        self.assertEqual(
            normalize_crs('2154'),
            'http://www.opengis.net/def/crs/EPSG/0/2154'
        )

        self.assertEqual(
            normalize_crs('http://www.opengis.net/def/crs/EPSG/0/2154'),
            'http://www.opengis.net/def/crs/EPSG/0/2154'
        )

        self.assertEqual(
            normalize_crs('EPSG2154'),
            'http://www.opengis.net/def/crs/EPSG/0/2154'
        )

        self.assertEqual(
            normalize_crs('EPSG:2154'),
            'http://www.opengis.net/def/crs/EPSG/0/2154'
        )

        self.assertEqual(
            normalize_crs('EPSG 2154'),
            'http://www.opengis.net/def/crs/EPSG/0/2154'
        )

        self.assertEqual(
            normalize_crs('RGF93 / Lambert-93 (EPSG:2154)'),
            'http://www.opengis.net/def/crs/EPSG/0/2154'
        )

        self.assertEqual(
            normalize_crs('xxxxxEPSG:2154.'),
            'http://www.opengis.net/def/crs/EPSG/0/2154'
        )

        self.assertEqual(
            normalize_crs('urn:ogc:def:crs:EPSG::310566307'),
            'http://www.opengis.net/def/crs/EPSG/0/310566307'
        )

        self.assertEqual(
            normalize_crs('https://registre.ign.fr/ign/IGNF/crs/IGNF/AMANU63UTM7S'),
            'https://registre.ign.fr/ign/IGNF/crs/IGNF/AMANU63UTM7S'
        )

        self.assertEqual(
            normalize_crs('IGNF:AMANU63UTM7S'),
            'https://registre.ign.fr/ign/IGNF/crs/IGNF/AMANU63UTM7S'
        )

        self.assertEqual(
            normalize_crs('IGNF:RGAF09UTM20.MART87'),
            'https://registre.ign.fr/ign/IGNF/crs/IGNF/RGAF09UTM20.MART87'
        )
    
    def test_normalize_language(self):
        """Transformation des codes de langues en potentielles URI."""

        self.assertEqual(
            normalize_language('fre'),
            'http://publications.europa.eu/resource/authority/language/FRA'
        )

        self.assertEqual(
            normalize_language('fra'),
            'http://publications.europa.eu/resource/authority/language/FRA'
        )

        self.assertEqual(
            normalize_language('FRA'),
            'http://publications.europa.eu/resource/authority/language/FRA'
        )

        self.assertEqual(
            normalize_language('fr'),
            'http://publications.europa.eu/resource/authority/language/FRA'
        )

        self.assertEqual(
            normalize_language('FR'),
            'http://publications.europa.eu/resource/authority/language/FRA'
        )

        self.assertEqual(
            normalize_language('eng'),
            'http://publications.europa.eu/resource/authority/language/ENG'
        )

        self.assertEqual(
            normalize_language('ENG'),
            'http://publications.europa.eu/resource/authority/language/ENG'
        )

        self.assertEqual(
            normalize_language('en'),
            'http://publications.europa.eu/resource/authority/language/ENG'
        )

        self.assertEqual(
            normalize_language('EN'),
            'http://publications.europa.eu/resource/authority/language/ENG'
        )

        self.assertEqual(
            normalize_language(None),
            None
        )

        self.assertEqual(
            normalize_language('quelque chose'),
            None
        )
    
    def test_date_or_datetime_to_literal(self):
        """Création d'une valeur littérale du bon type pour représenter une date."""
        self.assertEqual(
            date_or_datetime_to_literal('2022-05-16'),
            Literal('2022-05-16', datatype=XSD.date)
        )
        self.assertEqual(
            date_or_datetime_to_literal('2022-05-16T20:30:10'),
            Literal('2022-05-16T20:30:10', datatype=XSD.dateTime)
        )
        self.assertEqual(
            date_or_datetime_to_literal('2022-05-16T20:30:10.001'),
            Literal('2022-05-16T20:30:10.001', datatype=XSD.dateTime)
        )
        self.assertEqual(
            date_or_datetime_to_literal('2022-05-16Z'),
            Literal('2022-05-16Z', datatype=XSD.date)
        )
        self.assertEqual(
            date_or_datetime_to_literal('2022-05-16-01:30'),
            Literal('2022-05-16-01:30', datatype=XSD.date)
        )
        self.assertEqual(
            date_or_datetime_to_literal('2022-05-16T20:30:10+14:00'),
            Literal('2022-05-16T20:30:10+14:00', datatype=XSD.dateTime)
        )
        self.assertEqual(
            date_or_datetime_to_literal('2022-05-16XXX'),
            None
        )
        self.assertEqual(
            date_or_datetime_to_literal(''),
            None
        )
        self.assertEqual(
            date_or_datetime_to_literal(None),
            None
        )

    def test_to_spatial_resolution_in_meters(self):
        """Conversion en mètres des résolutions spatiales exprimées dans d'autres unités."""
        self.assertEqual(to_spatial_resolution_in_meters(1, 'm'), 1)
        self.assertEqual(to_spatial_resolution_in_meters(2.5, 'cm'), 0.025)
        self.assertEqual(to_spatial_resolution_in_meters('1500', 'km'), 1500000)
        self.assertEqual(to_spatial_resolution_in_meters('xxx', 'km'), None)
        self.assertEqual(to_spatial_resolution_in_meters('1500', 'xxx'), None)
        self.assertEqual(to_spatial_resolution_in_meters(None, 'km'), None)

class IsoToDcatTestCase(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Import des fichiers de test.
        
        """
        cls.IGN_BDALTI = data_from_file(abspath('rdf/tests/samples/iso_ignf_bdaltir_2_0.xml'))
        cls.CSW_DATARA_FOND_AB = data_from_file(
            abspath('rdf/tests/samples/iso_datara_territoire_fonds_air_bois.xml')
        )
        cls.CSW_GEOIDE_ZAC_75 = data_from_file(abspath('rdf/tests/samples/iso_geoide_zac_paris.xml'))
        cls.CSW_GEOIDE_CUCS_75 = data_from_file(abspath('rdf/tests/samples/iso_geoide_quartiers_cucs_paris.xml'))
        cls.CSW_GEOLITTORAL_SENTIER = data_from_file(
            abspath('rdf/tests/samples/iso_geolittoral_sentier_du_littoral.xml')
        )
        cls.ALL = {
            'iso_datara_territoire_fonds_air_bois': cls.CSW_DATARA_FOND_AB,
            'iso_geoide_zac_paris': cls.CSW_GEOIDE_ZAC_75,
            'iso_ignf_bdaltir_2_0': cls.IGN_BDALTI,
            'iso_geolittoral_sentier_du_littoral': cls.CSW_GEOLITTORAL_SENTIER
        }

    def test_map_epsg(self):
        """Récupération des référentiels de coordonnées dans les fichiers de test."""
        dataset_id = DatasetId()

        samples = {
            self.CSW_GEOIDE_ZAC_75: [
                (dataset_id, DCT.conformsTo, URIRef('http://www.opengis.net/def/crs/EPSG/0/2154'))
            ],
            self.IGN_BDALTI: [
                # les référentiels non référencés dans les vocabulaires sont mis en commentaire
                (dataset_id, DCT.conformsTo, URIRef('https://registre.ign.fr/ign/IGNF/crs/IGNF/RGF93LAMB93.IGN69')),
                (dataset_id, DCT.conformsTo, URIRef('https://registre.ign.fr/ign/IGNF/crs/IGNF/RGF93LAMB93.IGN78C')),
                (dataset_id, DCT.conformsTo, URIRef('https://registre.ign.fr/ign/IGNF/crs/IGNF/RGFG95UTM22.GUYA77')),
                (dataset_id, DCT.conformsTo, URIRef('https://registre.ign.fr/ign/IGNF/crs/IGNF/RGM04UTM38S.MAYO53')),
                (dataset_id, DCT.conformsTo, URIRef('https://registre.ign.fr/ign/IGNF/crs/IGNF/RGR92G.REUN89')),
                (dataset_id, DCT.conformsTo, URIRef('https://registre.ign.fr/ign/IGNF/crs/IGNF/RGSPM06U21.STPM50')),
                # (dataset_id, DCT.conformsTo, URIRef('https://registre.ign.fr/ign/IGNF/crs/IGNF/WGS84UTM20.GUAD88')),
                # (dataset_id, DCT.conformsTo, URIRef('https://registre.ign.fr/ign/IGNF/crs/IGNF/WGS84UTM20.GUAD88MG')),
                # (dataset_id, DCT.conformsTo, URIRef('https://registre.ign.fr/ign/IGNF/crs/IGNF/WGS84UTM20.GUAD88SB')),
                # (dataset_id, DCT.conformsTo, URIRef('https://registre.ign.fr/ign/IGNF/crs/IGNF/WGS84UTM20.GUAD88SM')),
                # (dataset_id, DCT.conformsTo, URIRef('https://registre.ign.fr/ign/IGNF/crs/IGNF/WGS84UTM20.GUAD92LD')),
                # (dataset_id, DCT.conformsTo, URIRef('https://registre.ign.fr/ign/IGNF/crs/IGNF/WGS84UTM20.MART87'))
            ],
            self.CSW_DATARA_FOND_AB: [
                (dataset_id, DCT.conformsTo, URIRef('http://www.opengis.net/def/crs/EPSG/0/2154'))
            ],
            self.CSW_GEOLITTORAL_SENTIER: [
                (dataset_id, DCT.conformsTo, URIRef('http://www.opengis.net/def/crs/EPSG/0/2154')),
                (dataset_id, DCT.conformsTo, URIRef('http://www.opengis.net/def/crs/EPSG/0/5490')),
                (dataset_id, DCT.conformsTo, URIRef('http://www.opengis.net/def/crs/EPSG/0/4467')),
                (dataset_id, DCT.conformsTo, URIRef('http://www.opengis.net/def/crs/EPSG/0/2972'))
            ]
        }
        for sample_name in self.ALL:
            with self.subTest(sample=sample_name):
                sample = self.ALL[sample_name]
                itd = IsoToDcat(sample, datasetid=dataset_id)
                self.assertListEqual(
                    sorted(itd.map_crs),
                    sorted(samples[sample])
                )

    def test_map_language(self):
        """Récupération des langues des données dans les fichiers de test."""
        dataset_id = DatasetId()

        for sample_name in self.ALL:
            with self.subTest(sample=sample_name):
                sample = self.ALL[sample_name]
                itd = IsoToDcat(sample, datasetid=dataset_id)
                self.assertListEqual(
                    itd.map_language,
                    [
                        (
                            dataset_id,
                            DCT.language,
                            URIRef('http://publications.europa.eu/resource/authority/language/FRA')
                        )
                    ]
                )

    def test_map_representation_type(self):
        """Récupération du type de représentation dans les fichiers de test."""
        dataset_id = DatasetId()

        for sample_name in self.ALL:
            with self.subTest(sample=sample_name):
                sample = self.ALL[sample_name]
                itd = IsoToDcat(sample, datasetid=dataset_id)
                if sample is self.IGN_BDALTI:
                    value = URIRef('http://inspire.ec.europa.eu/metadata-codelist/SpatialRepresentationType/grid')
                else:
                    value = URIRef('http://inspire.ec.europa.eu/metadata-codelist/SpatialRepresentationType/vector')
                self.assertListEqual(
                    itd.map_representation_type,
                    [
                        (
                            dataset_id,
                            ADMS.representationTechnique,
                            value
                        )
                    ]
                )

    def test_map_categories(self):
        """Récupération de la catégorie ISO dans les fichiers de test."""
        dataset_id = DatasetId()

        values = {
            self.IGN_BDALTI: [
                URIRef('http://inspire.ec.europa.eu/metadata-codelist/TopicCategory/elevation'),
                URIRef('http://inspire.ec.europa.eu/metadata-codelist/TopicCategory/environment'),
                URIRef('http://inspire.ec.europa.eu/metadata-codelist/TopicCategory/geoscientificInformation'),
                URIRef('http://inspire.ec.europa.eu/metadata-codelist/TopicCategory/intelligenceMilitary')
            ],
            self.CSW_DATARA_FOND_AB: [
                URIRef('http://inspire.ec.europa.eu/metadata-codelist/TopicCategory/climatologyMeteorologyAtmosphere')
            ],
            self.CSW_GEOIDE_ZAC_75 : [
                URIRef('http://inspire.ec.europa.eu/metadata-codelist/TopicCategory/planningCadastre')
            ],
            self.CSW_GEOLITTORAL_SENTIER: [
                URIRef('http://inspire.ec.europa.eu/metadata-codelist/TopicCategory/transportation')
            ]
        }

        for sample_name in self.ALL:
            with self.subTest(sample=sample_name):
                sample = self.ALL[sample_name]
                itd = IsoToDcat(sample, datasetid=dataset_id)
                
                self.assertListEqual(
                    sorted(itd.map_categories),
                    [(dataset_id, DCAT.theme, value) for value in sorted(values[sample])]
                )

    def test_map_title(self):
        """Récupération du libellé du jeu de données dans les fichiers de test."""
        dataset_id = DatasetId()
        for sample_name in self.ALL:
            with self.subTest(sample=sample_name):
                sample = self.ALL[sample_name]
                itd = IsoToDcat(sample, datasetid=dataset_id)
                self.assertTrue(itd.map_title)

    def test_map_description(self):
        """Récupération du descriptif du jeu de données dans les fichiers de test."""
        dataset_id = DatasetId()
        for sample_name in self.ALL:
            with self.subTest(sample=sample_name):
                sample = self.ALL[sample_name]
                itd = IsoToDcat(sample, datasetid=dataset_id)
                self.assertTrue(itd.map_description)

    def test_map_location_basic(self):
        """Récupération du rectangle d'emprise du jeu de données dans les fichiers de test."""
        dataset_id = DatasetId()
        for sample_name in self.ALL:
            with self.subTest(sample=sample_name):
                sample = self.ALL[sample_name]
                itd = IsoToDcat(sample, datasetid=dataset_id)
                self.assertTrue(itd.map_location)
    
    def test_map_location_ign(self):
        """Contrôle des valeurs obtenues lors de la récupération des informations de localisation dans le fichier de test IGN."""
        metagraph = metagraph_from_iso(self.IGN_BDALTI)
        dataset_id = metagraph.datasetid
        spatial_nodes = list(metagraph.objects(dataset_id, DCT.spatial))
        self.assertEqual(len(spatial_nodes), 13)
        glp_node = None
        for node in spatial_nodes:
            if (node, DCT.identifier, Literal('GLP')) in metagraph:
                glp_node = node
        self.assertIsNotNone(glp_node)
        self.assertTrue((glp_node, DCAT.bbox, None) in metagraph)
        self.assertTrue((glp_node, SKOS.prefLabel, Literal('Guadeloupe', lang='fr')) in metagraph)
        self.assertTrue(
            (
                glp_node,
                SKOS.inScheme,
                URIRef('http://registre.data.developpement-durable.gouv.fr/plume/ISO3166CodesCollection/CountryCodeAlpha3')
            ) in metagraph
        )

    def test_map_location_geoide(self):
        """Contrôle des valeurs obtenues lors de la récupération des informations de localisation dans le fichier de test GéoIDE."""
        metagraph = metagraph_from_iso(self.CSW_GEOIDE_ZAC_75)
        dataset_id = metagraph.datasetid
        spatial_objects = list(metagraph.objects(dataset_id, DCT.spatial))
        self.assertEqual(len(spatial_objects), 1)
        self.assertEqual(spatial_objects[0], URIRef('http://id.insee.fr/geo/departement/75'))

    def test_map_location_datara(self):
        """Contrôle des valeurs obtenues lors de la récupération des informations de localisation dans le fichier de test datARA."""
        metagraph = metagraph_from_iso(self.CSW_DATARA_FOND_AB)
        dataset_id = metagraph.datasetid
        spatial_nodes = list(metagraph.objects(dataset_id, DCT.spatial))
        self.assertEqual(len(spatial_nodes), 1)
        self.assertEqual(metagraph.value(spatial_nodes[0], SKOS.prefLabel), Literal('AUVERGNE-RHONE-ALPES', lang='fr'))
        self.assertTrue((spatial_nodes[0], DCAT.bbox, None) in metagraph)
    
    def test_map_location_geolittoral(self):
        """Contrôle des valeurs obtenues lors de la récupération des informations de localisation dans le fichier de test Géolittoral."""
        metagraph = metagraph_from_iso(self.CSW_GEOLITTORAL_SENTIER)
        dataset_id = metagraph.datasetid
        spatial_nodes = list(metagraph.objects(dataset_id, DCT.spatial))
        self.assertEqual(len(spatial_nodes), 5)
        self.assertTrue(all((spatial_node, DCAT.bbox, None) in metagraph for spatial_node in spatial_nodes))

    def test_map_location_complex_1(self):
        """Contrôle des valeurs obtenues lors de la récupération des informations de localisation dans un XML artificiel complexe (1)."""
        raw_xml = """<?xml version="1.0" encoding="UTF-8"?>
<gmd:MD_Metadata xmlns:gmd="http://www.isotc211.org/2005/gmd" xmlns:gco="http://www.isotc211.org/2005/gco">
   <gmd:identificationInfo>
      <gmd:MD_DataIdentification>
         <gmd:extent>
            <gmd:EX_Extent>
               <gmd:description>
                  <gco:CharacterString>France</gco:CharacterString>
               </gmd:description>
               <gmd:geographicElement>
                  <gmd:EX_GeographicBoundingBox>
                     <gmd:westBoundLongitude>
                        <gco:Decimal>-5.857279826455812</gco:Decimal>
                     </gmd:westBoundLongitude>
                     <gmd:eastBoundLongitude>
                        <gco:Decimal>10.666157673544188</gco:Decimal>
                     </gmd:eastBoundLongitude>
                     <gmd:southBoundLatitude>
                        <gco:Decimal>41.15261992754145</gco:Decimal>
                     </gmd:southBoundLatitude>
                     <gmd:northBoundLatitude>
                        <gco:Decimal>51.43245199253582</gco:Decimal>
                     </gmd:northBoundLatitude>
                  </gmd:EX_GeographicBoundingBox>
               </gmd:geographicElement>
               <gmd:geographicElement>
                  <gmd:EX_GeographicBoundingBox>
                     <gmd:westBoundLongitude>
                        <gco:Decimal>-61,949</gco:Decimal>
                     </gmd:westBoundLongitude>
                     <gmd:eastBoundLongitude>
                        <gco:Decimal>-60,915</gco:Decimal>
                     </gmd:eastBoundLongitude>
                     <gmd:southBoundLatitude>
                        <gco:Decimal>15,648</gco:Decimal>
                     </gmd:southBoundLatitude>
                     <gmd:northBoundLatitude>
                        <gco:Decimal>16,647</gco:Decimal>
                     </gmd:northBoundLatitude>
                  </gmd:EX_GeographicBoundingBox>
               </gmd:geographicElement>
            </gmd:EX_Extent>
         </gmd:extent>
      </gmd:MD_DataIdentification>
   </gmd:identificationInfo>
</gmd:MD_Metadata>
        """
        metagraph = metagraph_from_iso(raw_xml)
        dataset_id = metagraph.datasetid
        spatial_nodes = list(metagraph.objects(dataset_id, DCT.spatial))
        self.assertEqual(len(spatial_nodes), 3)
        bboxes = list(metagraph.objects(dataset_id, DCT.spatial / DCAT.bbox))
        self.assertEqual(len(bboxes), 2)
        labels = list(metagraph.objects(dataset_id, DCT.spatial / SKOS.prefLabel))
        self.assertEqual(len(labels), 1)

    def test_map_location_complex_2(self):
        """Contrôle des valeurs obtenues lors de la récupération des informations de localisation dans un XML artificiel complexe (2)."""
        raw_xml = """<?xml version="1.0" encoding="UTF-8"?>
<gmd:MD_Metadata xmlns:gmd="http://www.isotc211.org/2005/gmd" xmlns:gco="http://www.isotc211.org/2005/gco" xmlns:gmx="http://www.isotc211.org/2005/gmx" xmlns:xlink="http://www.w3.org/1999/xlink">
   <gmd:identificationInfo>
      <gmd:MD_DataIdentification>
         <gmd:extent>
            <gmd:EX_Extent>
               <gmd:description>
                  <gco:CharacterString>France</gco:CharacterString>
               </gmd:description>
               <gmd:geographicElement>
                  <gmd:EX_GeographicDescription>
                     <gmd:geographicIdentifier>
                        <gmd:MD_Identifier>
                           <gmd:code>
                              <gco:CharacterString>http://id.insee.fr/geo/departement/75</gco:CharacterString>
                           </gmd:code>
                        </gmd:MD_Identifier>
                     </gmd:geographicIdentifier>
                  </gmd:EX_GeographicDescription>
               </gmd:geographicElement>
               <gmd:geographicElement>
                  <gmd:EX_GeographicDescription>
                     <gmd:geographicIdentifier>
                        <gmd:MD_Identifier>
                           <gmd:code>
                              <gmx:Anchor xlink:href="http://id.insee.fr/geo/departement/94">94</gmx:Anchor>
                           </gmd:code>
                        </gmd:MD_Identifier>
                     </gmd:geographicIdentifier>
                  </gmd:EX_GeographicDescription>
               </gmd:geographicElement>
               <gmd:geographicElement>
                  <gmd:EX_GeographicBoundingBox>
                     <gmd:westBoundLongitude>
                        <gco:Decimal>-61.949</gco:Decimal>
                     </gmd:westBoundLongitude>
                     <gmd:eastBoundLongitude>
                        <gco:Decimal>-60.915</gco:Decimal>
                     </gmd:eastBoundLongitude>
                     <gmd:southBoundLatitude>
                        <gco:Decimal>15.648</gco:Decimal>
                     </gmd:southBoundLatitude>
                     <gmd:northBoundLatitude>
                        <gco:Decimal>16.647</gco:Decimal>
                     </gmd:northBoundLatitude>
                  </gmd:EX_GeographicBoundingBox>
               </gmd:geographicElement>
            </gmd:EX_Extent>
         </gmd:extent>
      </gmd:MD_DataIdentification>
   </gmd:identificationInfo>
</gmd:MD_Metadata>
        """
        metagraph = metagraph_from_iso(raw_xml)
        dataset_id = metagraph.datasetid
        spatial_objects = list(metagraph.objects(dataset_id, DCT.spatial))
        self.assertEqual(len(spatial_objects), 3)
        self.assertTrue(URIRef('http://id.insee.fr/geo/departement/75') in spatial_objects)
        self.assertTrue(URIRef('http://id.insee.fr/geo/departement/94') in spatial_objects)
        bboxes = list(metagraph.objects(dataset_id, DCT.spatial / DCAT.bbox))
        self.assertEqual(len(bboxes), 1)
        labels = list(metagraph.objects(dataset_id, DCT.spatial / SKOS.prefLabel))
        self.assertEqual(len(labels), 1)
        self.assertEqual(
            list(metagraph.subjects(DCT.spatial / DCAT.bbox, None)),
            list(metagraph.subjects(DCT.spatial / SKOS.prefLabel, None))
        )

    def test_metadata_language(self):
        """Récupération de la langue des métadonnées dans les fichiers de test."""
        dataset_id = DatasetId()
        for sample_name in self.ALL:
            with self.subTest(sample=sample_name):
                sample = self.ALL[sample_name]
                itd = IsoToDcat(sample, datasetid=dataset_id)
                self.assertEqual(itd.metadata_language, 'fr')

    def test_map_version(self):
        """Récupération du nom/numéro de version."""
        metagraph = metagraph_from_iso(self.CSW_GEOIDE_CUCS_75)
        dataset_id = metagraph.datasetid
        versions = list(metagraph.objects(dataset_id, OWL.versionInfo))
        self.assertListEqual(versions, [Literal('1')])

        metagraph = metagraph_from_iso(self.IGN_BDALTI)
        dataset_id = metagraph.datasetid
        versions = list(metagraph.objects(dataset_id, OWL.versionInfo))
        self.assertListEqual(versions, [Literal('Version 2.0')])

    def test_map_dates(self):
        """Récupération des dates de référence."""
        metagraph = metagraph_from_iso(self.IGN_BDALTI)
        dataset_id = metagraph.datasetid
        dates = list(metagraph.objects(dataset_id, DCT.issued))
        self.assertListEqual(dates, [Literal('2015-02-03', datatype=XSD.date)])

        metagraph = metagraph_from_iso(self.CSW_GEOIDE_ZAC_75)
        dataset_id = metagraph.datasetid
        dates = list(metagraph.objects(dataset_id, DCT.issued))
        self.assertListEqual(dates, [Literal('2017-01-11', datatype=XSD.date)])
        dates = list(metagraph.objects(dataset_id, DCT.created))
        self.assertListEqual(dates, [Literal('2011-01-01', datatype=XSD.date)])
        dates = list(metagraph.objects(dataset_id, DCT.modified))
        self.assertListEqual(dates, [Literal('2020-01-21', datatype=XSD.date)])

        metagraph = metagraph_from_iso(self.CSW_GEOLITTORAL_SENTIER)
        dataset_id = metagraph.datasetid
        dates = list(metagraph.objects(dataset_id, DCT.issued))
        self.assertListEqual(dates, [Literal('2016-08-29', datatype=XSD.date)])
        dates = list(metagraph.objects(dataset_id, DCT.created))
        self.assertListEqual(dates, [Literal('2016-08-29', datatype=XSD.date)])
        dates = list(metagraph.objects(dataset_id, DCT.modified))
        self.assertListEqual(dates, [Literal('2020-04-09', datatype=XSD.date)])

        metagraph = metagraph_from_iso(self.CSW_DATARA_FOND_AB)
        dataset_id = metagraph.datasetid
        dates = list(metagraph.objects(dataset_id, DCT.issued))
        self.assertListEqual(dates, [Literal('2020-04-16', datatype=XSD.date)])
        dates = list(metagraph.objects(dataset_id, DCT.modified))
        self.assertListEqual(dates, [Literal('2020-11-19T13:59:52', datatype=XSD.dateTime)])

    def test_map_temporal(self):
        """Récupération de l'étendue temporelle.
        
        C'est une métadonnée assez peu utilisée, elle n'est pas présente
        dans tous les jeux de données de test.

        """
        metagraph = metagraph_from_iso(self.CSW_GEOIDE_CUCS_75)
        dataset_id = metagraph.datasetid
        temporal = list(metagraph.objects(dataset_id, DCT.temporal))
        self.assertEqual(len(temporal), 1)
        self.assertEqual(metagraph.value(temporal[0], DCAT.startDate), Literal('2007-01-01', datatype=XSD.date))
        self.assertEqual(metagraph.value(temporal[0], DCAT.endDate), Literal('2014-12-31', datatype=XSD.date))
    
    def test_map_keywords(self):
        """Récupération des thèmes INSPIRE et mots clés libres dans les fichiers de test."""
        dataset_id = DatasetId()

        keywords = {
            self.IGN_BDALTI: [
                'altitude',
                'Modèle Numérique de Terrain',
                'précision altimétrique'
            ],
            self.CSW_DATARA_FOND_AB: [
                'Auvergne-Rhône-Alpes',
                'AUVERGNE-RHONE-ALPES',
                'Qualité - Pollution',
                'Spécification locale',
                'DREAL Auvergne-Rhône-Alpes',
                'Grand public'
            ],
            self.CSW_GEOIDE_ZAC_75 : [
                'Aménagement Urbanisme/Zonages Planification',
                'données ouvertes'
            ],
            self.CSW_GEOLITTORAL_SENTIER: [
                'Tronçon littoral',
                '/Activités et Usages/Loisirs',
                '/Données dérivées/Produits composites',
                '/Métropole',
                '/Outre-mer/Antilles',
                '/Outre-mer/Guyane',
                '/Outre-mer/St-Pierre-et-Miquelon'
            ]
        }

        inspire_themes = {
            self.IGN_BDALTI: [
                URIRef('http://inspire.ec.europa.eu/theme/el')
            ],
            self.CSW_DATARA_FOND_AB: [
                URIRef('http://inspire.ec.europa.eu/theme/hh')
            ],
            self.CSW_GEOIDE_ZAC_75 : [
                URIRef('http://inspire.ec.europa.eu/theme/lu')
            ],
            self.CSW_GEOLITTORAL_SENTIER: [
                URIRef('http://inspire.ec.europa.eu/theme/tn')
            ]
        }

        for sample_name in self.ALL:
            with self.subTest(sample=sample_name):
                sample = self.ALL[sample_name]
                itd = IsoToDcat(sample, datasetid=dataset_id)

                self.assertListEqual(
                    sorted(itd.map_keywords),
                    sorted(
                        [
                            (dataset_id, DCAT.theme, value)
                            for value in inspire_themes[sample]
                        ] +
                        [
                            (dataset_id, DCAT.keyword, Literal(value, lang='fr'))
                            for value in sorted(keywords[sample])
                        ]
                    )
                )

    def test_map_spatial_resolution_as_scale(self):
        """Récupération de la résolution spatiale dans le cas d'une échelle équivalente."""
        samples = {
            self.CSW_DATARA_FOND_AB: 1.0/25000,
            self.CSW_GEOIDE_ZAC_75 : 1.0/2000,
            self.CSW_GEOLITTORAL_SENTIER: 1.0/5000
        }
        for sample, value in samples.items():       
            metagraph = metagraph_from_iso(sample)
            widgetsdict = WidgetsDict(metagraph=metagraph)
            metagraph = widgetsdict.build_metagraph()
            dataset_id = metagraph.datasetid
            resolution_nodes = list(metagraph.objects(dataset_id, DQV.hasQualityMeasurement))
            self.assertEqual(len(resolution_nodes), 1)
            self.assertEqual(
                metagraph.value(resolution_nodes[0], DQV.isMeasurementOf),
                GEODCAT.spatialResolutionAsScale
            )
            self.assertEqual(
                metagraph.value(resolution_nodes[0], DQV.value).toPython(),
                value
            )

    def test_map_spatial_resolution_as_distance(self):
        """Récupération de la résolution spatiale dans le cas d'une distance."""
        metagraph = metagraph_from_iso(self.IGN_BDALTI)
        widgetsdict = WidgetsDict(metagraph=metagraph)
        metagraph = widgetsdict.build_metagraph()
        dataset_id = metagraph.datasetid
        resolution_values = list(metagraph.objects(dataset_id, DCAT.spatialResolutionInMeters))
        self.assertEqual(len(resolution_values), 3)
        expected = [
            Literal(25.0, datatype=XSD.decimal),
            Literal(75.0, datatype=XSD.decimal),
            Literal(250.0, datatype=XSD.decimal)
        ]
        self.assertListEqual(resolution_values, expected)

if __name__ == '__main__':
    unittest.main()

