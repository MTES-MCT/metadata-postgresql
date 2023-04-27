
import unittest

from plume.rdf.utils import (
    abspath, data_from_file, DatasetId, owlthing_from_email,
    owlthing_from_tel
)
from plume.iso.map import (
    find_iri, find_literal, parse_xml, ISO_NS
)
from plume.rdf.namespaces import DCT, FOAF, DCAT
from plume.rdf.rdflib import Literal, URIRef

class IsoMapTestCase(unittest.TestCase):

    def test_find_literal_list_of_paths(self):
        """Application de la fonction find_literal à une liste de chemins."""
    
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
            'iso_ignf_bdaltir_2_0': cls.IGN_BDALTI,
            'iso_datara_territoire_fonds_air_bois': cls.CSW_DATARA_FOND_AB,
            'iso_geoide_zac_paris': cls.CSW_GEOIDE_ZAC_75,
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


if __name__ == '__main__':
    unittest.main()

