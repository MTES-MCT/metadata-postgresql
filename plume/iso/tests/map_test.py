
import unittest

from plume.rdf.utils import (
    abspath, data_from_file, DatasetId, owlthing_from_email,
    owlthing_from_tel
)
from plume.iso.map import (
    find_iri, find_literal, parse_xml, ISO_NS, normalize_crs,
    IsoToDcat
)
from plume.rdf.namespaces import DCT, FOAF, DCAT, PLUME
from plume.rdf.rdflib import Literal, URIRef

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
                    sorted(itd.map_epsg),
                    sorted(samples[sample])
                )

if __name__ == '__main__':
    unittest.main()

