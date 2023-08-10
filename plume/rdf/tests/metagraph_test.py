
import unittest

from plume.rdf.rdflib import isomorphic, URIRef, Literal
from plume.rdf.utils import abspath, data_from_file, DatasetId
from plume.rdf.metagraph import (
    Metagraph, metagraph_from_file, copy_metagraph, metagraph_from_iso,
    clean_metagraph, metagraph_from_iso_file, graph_from_file,
    metagraph_from_rdf_data
)
from plume.rdf.namespaces import (
    DCT, DCAT, XSD, VCARD, GEODCAT, FOAF, OWL, XSD, RDF, ADMS
)
from plume.rdf.widgetsdict import WidgetsDict
from plume.pg.description import PgDescription

class MetagraphTestCase(unittest.TestCase):

    def test_fresh(self):
        """Contrôle de la mise à jour adéquate de l'attribut fresh.
        
        """
        metagraph = Metagraph()
        self.assertTrue(metagraph.fresh)
        metagraph = WidgetsDict().build_metagraph()
        self.assertFalse(metagraph.fresh)
        metagraph = copy_metagraph(metagraph, metagraph)
        self.assertTrue(metagraph.fresh)
        metagraph = clean_metagraph(metagraph, metagraph)
        self.assertTrue(metagraph.fresh)

    def test_is_empty(self):
        """Propriété servant à l'identification des graphes quasi vides.
        
        On attend notamment de cette propriété qu'elle reconnaisse comme
        vide le résultat de la désérialisation d'un dictionnaire de widgets
        vide.
        
        """
        self.assertTrue(Metagraph().is_empty)
        metagraph = WidgetsDict().build_metagraph()
        self.assertTrue(metagraph.is_empty)
        metadata = """
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix uuid: <urn:uuid:> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

            uuid:479fd670-32c5-4ade-a26d-0268b0ce5046 a dcat:Dataset ;
                dct:identifier "479fd670-32c5-4ade-a26d-0268b0ce5046" .
            """
        metagraph = Metagraph().parse(data=metadata)
        self.assertTrue(metagraph.is_empty)
        metadata = """
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix uuid: <urn:uuid:> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

            uuid:479fd670-32c5-4ade-a26d-0268b0ce5046 a dcat:Dataset ;
                dcat:theme <http://inspire.ec.europa.eu/theme/au> ;
                dct:identifier "479fd670-32c5-4ade-a26d-0268b0ce5046" .
            """
        metagraph = Metagraph().parse(data=metadata)
        self.assertFalse(metagraph.is_empty)

    def test_clean_metagraph_classmap(self):
        """Nettoyage d'un graphe avec mapping de classes et de prédicats.
        
        """
        metadata = """
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix foaf: <http://xmlns.com/foaf/0.1/> .
            @prefix org: <http://www.w3.org/ns/org#> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix uuid: <urn:uuid:> .
            @prefix vcard: <http://www.w3.org/2006/vcard/ns#> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

            uuid:479fd670-32c5-4ade-a26d-0268b0ce5046 a dcat:Dataset ;
                dct:title "ADMIN EXPRESS - Départements de métropole"@fr ;
                dct:creator [ a org:Organization ;
                    foaf:name "IGN"@fr ] ;
                dcat:pointOfContact [ a vcard:Organization ;
                    vcard:fn "Un service de l'IGN"@fr ;
                    vcard:organisation-name "Institut géographique national"@fr ] .
            """
        raw_metagraph = Metagraph().parse(data=metadata)
        metagraph = clean_metagraph(raw_metagraph, raw_metagraph)
        metadata = """
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix foaf: <http://xmlns.com/foaf/0.1/> .
            @prefix org: <http://www.w3.org/ns/org#> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix uuid: <urn:uuid:> .
            @prefix vcard: <http://www.w3.org/2006/vcard/ns#> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

            uuid:479fd670-32c5-4ade-a26d-0268b0ce5046 a dcat:Dataset ;
                dct:title "ADMIN EXPRESS - Départements de métropole"@fr ;
                dct:creator [ a foaf:Agent ;
                    foaf:name "IGN"@fr ] ;
                dcat:pointOfContact [ a vcard:Kind ;
                    vcard:fn "Un service de l'IGN"@fr ;
                    vcard:organization-name "Institut géographique national"@fr ] .
            """
        new_metagraph = Metagraph().parse(data=metadata)
        self.assertTrue(isomorphic(metagraph, new_metagraph))

    def test_update_metadata_date(self):
        """Mise à jour de la date de modification des métadonnées.
        
        """
        # --- pas de date dans le graphe d'origine ---
        metadata = """
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix uuid: <urn:uuid:> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

            uuid:479fd670-32c5-4ade-a26d-0268b0ce5046 a dcat:Dataset ;
                dct:title "ADMIN EXPRESS - Départements de métropole"@fr ;
                dcat:theme <http://inspire.ec.europa.eu/theme/au> ;
                dct:identifier "479fd670-32c5-4ade-a26d-0268b0ce5046" .
            """
        metagraph = Metagraph().parse(data=metadata)
        metagraph.update_metadata_date()
        bnode = metagraph.value(metagraph.datasetid, FOAF.isPrimaryTopicOf)
        self.assertIsNotNone(bnode)
        self.assertTrue((bnode, RDF.type, DCAT.CatalogRecord) in metagraph)
        date = metagraph.value(bnode, DCT.modified)
        self.assertTrue(isinstance(date, Literal))
        self.assertEqual(date.datatype, XSD.dateTime)
        self.assertRegex(str(date), '^[0-9]{4}[-][0-9]{2}[-][0-9]{2}T[0-9]{2}[:][0-9]{2}[:][0-9]{2}$')
        
        # --- avec date dans le graphe d'origine ---
        metadata = """
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix foaf: <http://xmlns.com/foaf/0.1/> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix uuid: <urn:uuid:> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

            uuid:479fd670-32c5-4ade-a26d-0268b0ce5046 a dcat:Dataset ;
                dct:title "ADMIN EXPRESS - Départements de métropole"@fr ;
                dcat:theme <http://inspire.ec.europa.eu/theme/au> ;
                dct:identifier "479fd670-32c5-4ade-a26d-0268b0ce5046" ;
                foaf:isPrimaryTopicOf [ a dcat:CatalogRecord ;
                    dct:modified "2022-01-01T00:00:00"^^xsd:dateTime ] .
            """
        metagraph = Metagraph().parse(data=metadata)
        metagraph.update_metadata_date()
        bnode = metagraph.value(metagraph.datasetid, FOAF.isPrimaryTopicOf)
        self.assertIsNotNone(bnode)
        self.assertTrue((bnode, RDF.type, DCAT.CatalogRecord) in metagraph)
        date = metagraph.value(bnode, DCT.modified)
        self.assertTrue(isinstance(date, Literal))
        self.assertEqual(date.datatype, XSD.dateTime)
        self.assertRegex(str(date), '^[0-9]{4}[-][0-9]{2}[-][0-9]{2}T[0-9]{2}[:][0-9]{2}[:][0-9]{2}$')
        self.assertGreater(str(date), "2022-01-01T00:00:00")

    def test_delete_branch(self):
        """Suppression d'une branche libre du graphe.

        """
        metadata = """
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix uuid: <urn:uuid:> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

            uuid:479fd670-32c5-4ade-a26d-0268b0ce5046 a dcat:Dataset ;
                dcat:distribution [ a dcat:Distribution ;
                    dct:issued "2022-01-23"^^xsd:date ;
                    dct:rights [ a dct:RightsStatement ;
                        rdfs:label "Copyright IGN" ] ] ;
                dct:title "ADMIN EXPRESS - Départements de métropole"@fr ;
                dcat:theme <http://inspire.ec.europa.eu/theme/au> ;
                dct:identifier "479fd670-32c5-4ade-a26d-0268b0ce5046" .
            """
        metagraph = Metagraph().parse(data=metadata)
        bnode = metagraph.value(metagraph.datasetid, DCAT.distribution)
        metagraph.remove((metagraph.datasetid, DCAT.distribution, bnode))
        self.assertTrue((None, DCT.issued, Literal('2022-01-23', datatype=XSD.date))
            in metagraph)
        metagraph.delete_branch(bnode)
        metadata = """
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix uuid: <urn:uuid:> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

            uuid:479fd670-32c5-4ade-a26d-0268b0ce5046 a dcat:Dataset ;
                dct:title "ADMIN EXPRESS - Départements de métropole"@fr ;
                dcat:theme <http://inspire.ec.europa.eu/theme/au> ;
                dct:identifier "479fd670-32c5-4ade-a26d-0268b0ce5046" .
            """
        metagraph_end = Metagraph().parse(data=metadata)
        self.assertTrue(isomorphic(metagraph, metagraph_end))

    def test_merge(self):
        """Fusion de deux graphes.

        """
        metadata = """
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix uuid: <urn:uuid:> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

            uuid:479fd670-32c5-4ade-a26d-0268b0ce5046 a dcat:Dataset ;
                dcat:distribution [ a dcat:Distribution ;
                    dct:issued "2022-01-22"^^xsd:date ;
                    dct:rights [ a dct:RightsStatement ;
                        rdfs:label "Copyright IGN" ] ],
                  [ a dcat:Distribution ;
                    dct:issued "2022-01-23"^^xsd:date ;
                    dct:rights [ a dct:RightsStatement ;
                        rdfs:label "Copyright IGN" ] ] ;
                dct:title "ADMIN EXPRESS - Départements de métropole"@fr ;
                dcat:theme <http://inspire.ec.europa.eu/theme/au> ;
                dct:identifier "479fd670-32c5-4ade-a26d-0268b0ce5046" .
            """
        metagraph = Metagraph().parse(data=metadata)
        metagraph_bis = copy_metagraph(metagraph, metagraph)
        metadata = """
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix uuid: <urn:uuid:> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

            uuid:1871e408-a997-4936-9051-76efeef5049c a dcat:Dataset ;
                dcat:distribution [ a dcat:Distribution ;
                    dct:issued "2022-01-24"^^xsd:date ;
                    dct:rights [ a dct:RightsStatement ;
                        rdfs:label "Copyright IGN, 2022" ] ] ;
                dct:title "ADMIN EXPRESS - Départements de métropole"@fr,
                    "ADMIN EXPRESS - Metropolitan Departments"@en ;
                dct:temporal [ a dct:PeriodOfTime ;
                    dcat:endDate "2021-01-15"^^xsd:date ;
                    dcat:startDate "2021-01-15"^^xsd:date ] ;
                dct:identifier "1871e408-a997-4936-9051-76efeef5049c" .
            """
        metagraph_alt = Metagraph().parse(data=metadata)
        metadata = """
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix uuid: <urn:uuid:> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

            uuid:479fd670-32c5-4ade-a26d-0268b0ce5046 a dcat:Dataset ;
                dcat:distribution [ a dcat:Distribution ;
                    dct:issued "2022-01-24"^^xsd:date ;
                    dct:rights [ a dct:RightsStatement ;
                        rdfs:label "Copyright IGN, 2022" ] ] ;
                dct:title "ADMIN EXPRESS - Départements de métropole"@fr,
                    "ADMIN EXPRESS - Metropolitan Departments"@en ;
                dct:temporal [ a dct:PeriodOfTime ;
                    dcat:endDate "2021-01-15"^^xsd:date ;
                    dcat:startDate "2021-01-15"^^xsd:date ] ;
                dcat:theme <http://inspire.ec.europa.eu/theme/au> ;
                dct:identifier "479fd670-32c5-4ade-a26d-0268b0ce5046" .
            """
        metagraph_end_if_exists = Metagraph().parse(data=metadata)
        metagraph.merge(metagraph_alt, replace=True)
        self.assertTrue(isomorphic(metagraph_end_if_exists, metagraph))
        metadata = """
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix uuid: <urn:uuid:> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

            uuid:479fd670-32c5-4ade-a26d-0268b0ce5046 a dcat:Dataset ;
                dcat:distribution [ a dcat:Distribution ;
                    dct:issued "2022-01-22"^^xsd:date ;
                    dct:rights [ a dct:RightsStatement ;
                        rdfs:label "Copyright IGN" ] ],
                  [ a dcat:Distribution ;
                    dct:issued "2022-01-23"^^xsd:date ;
                    dct:rights [ a dct:RightsStatement ;
                        rdfs:label "Copyright IGN" ] ] ;
                dct:title "ADMIN EXPRESS - Départements de métropole"@fr ;
                dcat:theme <http://inspire.ec.europa.eu/theme/au> ;
                dct:temporal [ a dct:PeriodOfTime ;
                    dcat:endDate "2021-01-15"^^xsd:date ;
                    dcat:startDate "2021-01-15"^^xsd:date ] ;
                dct:identifier "479fd670-32c5-4ade-a26d-0268b0ce5046" .
            """
        metagraph_end_never = Metagraph().parse(data=metadata)
        metagraph_bis.merge(metagraph_alt, replace=False)
        self.assertTrue(isomorphic(metagraph_end_never, metagraph_bis))

    def test_metagraph_from_iso_merge(self):
        """Import de métadonnées ISO 19115/19139 dans un graphe non vide.

        Ce test vérifie l'effet des différentes options d'import,
        qui priorisent plus ou moins les métadonnées ISO par
        rapport à celle du graphe d'origine.
        
        """
        metadata = """
            @prefix adms: <http://www.w3.org/ns/adms#> .
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix owl: <http://www.w3.org/2002/07/owl#> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix uuid: <urn:uuid:> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

            uuid:479fd670-32c5-4ade-a26d-0268b0ce5046 a dcat:Dataset ;
                dct:title "Zones d'aménagement concerté de Paris (75)"@fr ;
                owl:versionInfo "millésime janvier 2022" ;
                adms:versionNotes "L'excellent millésime de janvier 2022 !"@fr ;
                dct:identifier "479fd670-32c5-4ade-a26d-0268b0ce5046" .
            """
        old_metagraph = Metagraph().parse(data=metadata)
        raw_xml = data_from_file(abspath('rdf/tests/samples/iso_geoide_zac_paris.xml'))
        title = Literal('Délimitation des Zones d’Aménagement Concerté (ZAC) de Paris',
            lang='fr')
        title_bis = Literal("Zones d'aménagement concerté de Paris (75)",
            lang='fr')
        modified = Literal('2020-01-21', datatype=XSD.date)
        millesime = Literal('millésime janvier 2022')
        geoide_version = Literal('11')
        version_notes = Literal("L'excellent millésime de janvier 2022 !", lang='fr')
        # --- never ---
        metagraph = metagraph_from_iso(raw_xml, old_metagraph, preserve='never')
        datasetid = metagraph.datasetid
        self.assertTrue((datasetid, DCT.title, title) in metagraph)
        self.assertFalse((datasetid, DCT.title, title_bis) in metagraph)
        self.assertTrue((datasetid, OWL.versionInfo, geoide_version) in metagraph)
        self.assertFalse((datasetid, OWL.versionInfo, millesime) in metagraph)
        self.assertFalse((datasetid, ADMS.versionNotes, version_notes) in metagraph)
        self.assertTrue((datasetid, DCT.modified, modified) in metagraph)
        # --- if blank ---
        metagraph = metagraph_from_iso(raw_xml, old_metagraph, preserve='if blank')
        datasetid = metagraph.datasetid
        self.assertTrue((datasetid, DCT.title, title) in metagraph)
        self.assertFalse((datasetid, DCT.title, title_bis) in metagraph)
        self.assertTrue((datasetid, OWL.versionInfo, geoide_version) in metagraph)
        self.assertFalse((datasetid, OWL.versionInfo, millesime) in metagraph)
        self.assertTrue((datasetid, ADMS.versionNotes, version_notes) in metagraph)
        self.assertTrue((datasetid, DCT.modified, modified) in metagraph)
        # --- always ---
        metagraph = metagraph_from_iso(raw_xml, old_metagraph, preserve='always')
        datasetid = metagraph.datasetid
        self.assertFalse((datasetid, DCT.title, title) in metagraph)
        self.assertTrue((datasetid, DCT.title, title_bis) in metagraph)
        self.assertFalse((datasetid, OWL.versionInfo, geoide_version) in metagraph)
        self.assertTrue((datasetid, OWL.versionInfo, millesime) in metagraph)
        self.assertTrue((datasetid, ADMS.versionNotes, version_notes) in metagraph)
        self.assertTrue((datasetid, DCT.modified, modified) in metagraph)
        
    
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
        self.assertTrue((datasetid, DCT.rightsHolder / FOAF.name, fn1)
            in metagraph)
        self.assertTrue((datasetid, GEODCAT.custodian / FOAF.name, fn2)
            in metagraph)
        self.assertTrue((datasetid, DCAT.theme,
            URIRef('http://inspire.ec.europa.eu/theme/tn')) in metagraph)
    
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
        l = m.available_export_formats()
        self.assertTrue('pretty-xml' in l)
        self.assertTrue('xml' in l)
        l = m.available_export_formats(no_duplicate=True)
        self.assertTrue('pretty-xml' in l)
        self.assertFalse('xml' in l)
        l = m.available_export_formats(no_duplicate=True, format='xml')
        self.assertFalse('pretty-xml' in l)
        self.assertTrue('xml' in l)
        l = m.available_export_formats(no_duplicate=True, format='trig')
        self.assertTrue('pretty-xml' in l)
        self.assertFalse('xml' in l)

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

    def test_metagraph_from_iso_file(self):
        """Raccourci pour la création d'un graphe à partir d'un fichier de métadonnées ISO 19115/19139.
        
        """
        old_metagraph = Metagraph()
        old_metagraph.datasetid = DatasetId()
        raw_xml = data_from_file(abspath('rdf/tests/samples/'
            'iso_geolittoral_sentier_du_littoral.xml'))
        metagraph = metagraph_from_iso(raw_xml, old_metagraph=old_metagraph,
            preserve='never')
        metagraph_bis = metagraph_from_iso_file(abspath('rdf/tests/samples/'
            'iso_geolittoral_sentier_du_littoral.xml'),
            old_metagraph=old_metagraph)
        self.assertTrue(isomorphic(metagraph, metagraph_bis))

    def test_metagraph_from_iso_without_getresponsebyidresponse(self):
        """Création d'un graphe à partir d'un fichier de métadonnées ISO 19115/19139 quand la balise MD_Metadata est à la racine.
        
        """
        metagraph = metagraph_from_iso_file(
            abspath('rdf/tests/samples/iso_ignf_bdaltir_2_0.xml')
        )
        self.assertTrue((metagraph.datasetid, DCT.title, Literal('BD ALTI®', lang='fr')) in metagraph)

    def test_metagraph_rewritten(self):
        """Vérifie que l'attribut rewritten du graphe vaut True ssi le graphe est issu d'une source externe."""
        iso_filepath = abspath(
            'rdf/tests/samples/iso_geolittoral_sentier_du_littoral.xml'
        )
        dcat_filepath = abspath(
            'rdf/tests/samples/dcat_eurostat_bilan_nutritif_brut_terre_agricole.rdf'
        )

        # nouveau graphe
        old_metagraph = Metagraph()
        self.assertFalse(old_metagraph.rewritten)

        # metagraph_from_iso
        raw_xml = data_from_file(iso_filepath)
        for preserve in ('always', 'if blank', 'never'):
            with self.subTest(preserve=preserve):
                new_metagraph = metagraph_from_iso(
                    raw_xml,
                    old_metagraph=old_metagraph,
                    preserve=preserve
                )
                self.assertTrue(new_metagraph.rewritten)
        
        # metagraph_from_iso_file
        for preserve in ('always', 'if blank', 'never'):
            with self.subTest(preserve=preserve):
                new_metagraph = metagraph_from_iso_file(
                    iso_filepath,
                    old_metagraph=old_metagraph,
                    preserve=preserve
                )
                self.assertTrue(new_metagraph.rewritten)
        
        # metagraph_from_file
        new_metagraph = metagraph_from_file(
            dcat_filepath,
            old_metagraph=old_metagraph
        )
        self.assertTrue(new_metagraph.rewritten)

        # clean_metagraph
        raw_graph = graph_from_file(dcat_filepath)
        new_metagraph = clean_metagraph(
            raw_graph,
            old_metagraph=old_metagraph
        )
        self.assertTrue(new_metagraph.rewritten)

        # copy_metagraph (sans source)
        new_metagraph = copy_metagraph(
            old_metagraph=old_metagraph
        )
        self.assertTrue(new_metagraph.rewritten)

        # copy_metagraph (avec source)
        new_metagraph = copy_metagraph(
            src_metagraph = Metagraph(),
            old_metagraph=old_metagraph
        )
        self.assertTrue(new_metagraph.rewritten)

        # graphe issu d'un descriptif PostgreSQL
        pgdescr = PgDescription()
        self.assertFalse(pgdescr.metagraph.rewritten)

        # graphe construit à partir d'un dictionnaire de widgets
        widgetsdict = WidgetsDict(metagraph=new_metagraph)
        new_metagraph = widgetsdict.build_metagraph()
        self.assertFalse(new_metagraph.rewritten)

    def test_metagraph_from_rdf_data(self):
        """Génération d'un graphe à partir de données RDF."""
        data = data_from_file(abspath('rdf/tests/samples/dcat_eurostat_bilan_nutritif_brut_terre_agricole.ttl'))
        metagraph = metagraph_from_rdf_data(data, format='turtle')
        self.assertTrue((None, DCT.title, None) in metagraph)
        datasetid = DatasetId()
        old_metagraph = Metagraph()
        old_metagraph.datasetid = datasetid
        data = data_from_file(abspath('rdf/tests/samples/dcat_eurostat_bilan_nutritif_brut_terre_agricole.jsonld'))
        metagraph = metagraph_from_rdf_data(data, format='json-ld', old_metagraph=old_metagraph)
        self.assertTrue((datasetid, DCT.title, None) in metagraph)

if __name__ == '__main__':
    unittest.main()

