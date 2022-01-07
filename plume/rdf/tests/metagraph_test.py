
import unittest

from plume.rdf.rdflib import isomorphic, URIRef, Literal
from plume.rdf.utils import abspath, data_from_file, DatasetId
from plume.rdf.metagraph import Metagraph, metagraph_from_file, copy_metagraph, \
    metagraph_from_iso
from plume.rdf.namespaces import DCT, DCAT, XSD, VCARD, GEODCAT, FOAF

class MetagraphTestCase(unittest.TestCase):
    
    def test_metagraph_from_iso_geoide(self):
        """Génération d'un graphe à partir de métadonnées ISO 19115/19139 (XML issu de GéoIDE Catalogue).
        
        """
        old_metagraph = Metagraph()
        old_metagraph.datasetid = 'a307d028-d9d2-4605-a1e5-8d31bc573bef'
        self.assertEqual(old_metagraph.datasetid,
            DatasetId(URIRef('urn:uuid:a307d028-d9d2-4605-a1e5-8d31bc573bef')))
        raw_xml = data_from_file(abspath('rdf/tests/samples/iso_geoide_zac_paris.xml'))
        metagraph = metagraph_from_iso(raw_xml, old_metagraph)
        datasetid = metagraph.datasetid
        self.assertEqual(datasetid,
            DatasetId(URIRef('urn:uuid:a307d028-d9d2-4605-a1e5-8d31bc573bef')))
        title = Literal('Délimitation des Zones d’Aménagement Concerté (ZAC) de Paris',
            lang='fr')
        self.assertTrue((datasetid, DCT.title, title) in metagraph)
        modified = Literal('2020-01-21', datatype=XSD.date)
        self.assertTrue((datasetid, DCT.modified, modified) in metagraph)
        phone = URIRef('tel:+33-1-82-52-51-84')
        self.assertTrue((datasetid, DCAT.contactPoint / VCARD.hasTelephone, phone)
            in metagraph)

    def test_metagraph_from_iso_prodige(self):
        """Génération d'un graphe à partir de métadonnées ISO 19115/19139 (XML issu de datAra).
        
        """
        raw_xml = data_from_file(abspath('rdf/tests/samples/'
            'iso_datara_territoire_fonds_air_bois.xml'))
        metagraph = metagraph_from_iso(raw_xml)
        datasetid = metagraph.datasetid
        title = Literal('Périmètres des territoires fonds air bois en Auvergne-Rhône-Alpes',
            lang='fr')
        self.assertTrue((datasetid, DCT.title, title) in metagraph)
        name = Literal('DREAL Auvergne-Rhône-Alpes')
        self.assertTrue((datasetid, GEODCAT.distributor / FOAF.name, name)
            in metagraph)
        keyword1 = Literal('Qualité - Pollution', lang='fr')
        keyword2 = Literal('Spécification locale', lang='fr')
        self.assertTrue((datasetid, DCAT.keyword, keyword1) in metagraph)
        self.assertTrue((datasetid, DCAT.keyword, keyword2) in metagraph)
        issued = Literal('2020-04-16', datatype=XSD.date)
        self.assertTrue((datasetid, DCT.issued, issued) in metagraph)
        

    def test_metagraph_from_iso_geosource(self):
        """Génération d'un graphe à partir de métadonnées ISO 19115/19139 (XML issu de GéoLittoral).
        
        """
        raw_xml = data_from_file(abspath('rdf/tests/samples/'
            'iso_geolittoral_sentier_du_littoral.xml'))
        metagraph = metagraph_from_iso(raw_xml)
        datasetid = metagraph.datasetid
        title = Literal('Sentier du Littoral français (métropole et outre-mer)',
            lang='fr')
        self.assertTrue((datasetid, DCT.title, title) in metagraph)
        issued = Literal('2016-08-29', datatype=XSD.date)
        self.assertTrue((datasetid, DCT.issued, issued) in metagraph)
        fn1 = Literal("Ministère en charge de l'environnement / DGALN")
        fn2 = Literal('CEREMA Normandie-Centre')
        self.assertTrue((datasetid, DCAT.contactPoint / VCARD.fn, fn1)
            in metagraph)
        self.assertTrue((datasetid, DCAT.contactPoint / VCARD.fn, fn2)
            in metagraph)
    
    def test_metagraph_from_file(self):
        """Import depuis un fichier et génération d'un graphe de métadonnées propre.
        
        """
        m = metagraph_from_file(abspath('rdf/tests/samples/' \
            'dcat_eurostat_bilan_nutritif_brut_terre_agricole.rdf'))
        self.assertTrue(len(m) >= 98)

    def test_copy_metagraph(self):
        """Préservation des données lors de la copie d'un graphe de métadonnées.
        
        """
        m = metagraph_from_file(abspath('rdf/tests/samples/' \
            'dcat_eurostat_bilan_nutritif_brut_terre_agricole.ttl'))
        m_copy = copy_metagraph(m)
        self.assertEqual(len(m), len(m_copy))
        self.assertNotEqual(m.datasetid, m_copy.datasetid)
        m_clone = copy_metagraph(m, m)
        self.assertTrue(isomorphic(m, m_clone))
    
    def test_available_formats(self):
        """Formats d'exports disponibles pour le graphe.
        
        """
        m = metagraph_from_file(abspath('rdf/tests/samples/' \
            'dcat_eurostat_bilan_nutritif_brut_terre_agricole.jsonld'))
        l = m.available_formats
        self.assertTrue('turtle' in l)

    def test_export(self):
        """Préservation des données lors de la sérialisation dans un fichier.
        
        """
        m = metagraph_from_file(abspath('rdf/tests/samples/' \
            'dcat_eurostat_bilan_nutritif_brut_terre_agricole.jsonld'))
        m.export(abspath('rdf/tests/export/' \
            'dcat_eurostat_bilan_nutritif_brut_terre_agricole.ttl'))
        m_reload = metagraph_from_file(abspath('rdf/tests/export/' \
            'dcat_eurostat_bilan_nutritif_brut_terre_agricole.ttl'),
            old_metagraph=m)
        self.assertTrue(isomorphic(m, m_reload))

unittest.main()
