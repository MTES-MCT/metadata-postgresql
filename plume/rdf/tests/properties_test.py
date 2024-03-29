"""Recette du module properties.

Les tests nécessitent une connexion PostgreSQL (paramètres à
saisir lors de l'exécution du test) pointant sur une base où 
l'extension plume_pg est installée. Il est préférable d'utiliser
un super-utilisateur.

"""

import unittest
import psycopg2

from plume.rdf.rdflib import URIRef, Literal, from_n3
from plume.rdf.properties import (
    class_properties, PlumeProperty, property_param_values, property_sources
)
from plume.rdf.namespaces import XSD, RDF, DCAT, LOCAL, DCT, SH, PlumeNamespaceManager
from plume.pg.tests.connection import ConnectionString
from plume.pg.queries import query_get_categories, query_template_tabs
from plume.pg.template import TemplateDict

class PlumePropertyTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Création de la connexion PG.
        
        """
        cls.connection_string = ConnectionString()

    def test_disabled_vocabularies(self):
        """Contrôle de l'effectivité de la désactivation des vocabulaires censés l'être."""
        nsm = PlumeNamespaceManager()
        properties, predicates = class_properties(
            rdfclass=DCAT.Dataset, nsm=nsm, base_path=None
        )
        for prop in properties:
            if prop.n3_path == 'dct:spatial':
                # vocabulaire désactivé
                self.assertTrue(URIRef('http://id.insee.fr/geo/commune') in prop.prop_dict['ontology'])
                self.assertTrue(URIRef('http://id.insee.fr/geo/commune') in prop.prop_dict['disabled_ontology'])
                self.assertFalse(URIRef('http://id.insee.fr/geo/commune') in prop.prop_dict['sources'])
                # vocabulaire actif
                self.assertTrue(URIRef('http://id.insee.fr/geo/region') in prop.prop_dict['ontology'])
                self.assertFalse(URIRef('http://id.insee.fr/geo/region') in prop.prop_dict['disabled_ontology'])
                self.assertTrue(URIRef('http://id.insee.fr/geo/region') in prop.prop_dict['sources'])

    def test_class_properties_with_template(self):
        """Génération des catégories communes de la classe dcat:Dataset, avec personnalisation par un modèle.
        
        Le test crée un modèle sur le serveur PostgreSQL,
        l'importe puis réinstalle l'extension PlumePg pour
        effacer les modifications réalisées.
        
        """
        conn = psycopg2.connect(PlumePropertyTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO z_plume.meta_template(tpl_id, tpl_label) VALUES (100, 'Mon formulaire') ;
                    INSERT INTO z_plume.meta_tab (tab_id, tab_label, tab_num)
                        VALUES (101, 'Principal', 1), (102, 'Secondaire', 2) ;
                    INSERT INTO z_plume.meta_categorie
                        (label, datatype, is_long_text, is_multiple)
                        VALUES ('Notes', 'rdf:langString', True, True) ;
                    INSERT INTO z_plume.meta_template_categories
                        (tpl_id, shrcat_path, tab_id, template_order)
                        VALUES
                        (100, 'dct:description', 102, 1),
                        (100, 'dct:modified', 102, 2),
                        (100, 'dct:temporal / dcat:startDate', 102, 3),
                        (100, 'dct:temporal / dcat:endDate', 102, 4),
                        (100, 'dct:title', 101, 1),
                        (100, 'owl:versionInfo', 101, 2),
                        (100, 'dct:spatial / locn:geometry', 102, 10),
                        (100, 'dcat:theme', 102, 5),
                        (100, 'dct:language', 102, 6) ;
                    INSERT INTO z_plume.meta_template_categories
                        (tpl_id, shrcat_path, tab_id, template_order, sources)
                        VALUES
                        (100, 'dct:conformsTo', 102, 7, NULL) ;
                    UPDATE z_plume.meta_template_categories
                        SET sources = ARRAY['http://publications.europa.eu/resource/authority/data-theme']
                        WHERE tpl_id = 100 AND shrcat_path = 'dcat:theme' ;
                    UPDATE z_plume.meta_template_categories
                        SET geo_tools = ARRAY['point', 'rectangle']::z_plume.meta_geo_tool[]
                        WHERE tpl_id = 100 AND shrcat_path = 'dct:spatial / locn:geometry' ;
                    UPDATE z_plume.meta_template_categories
                        SET sources = ARRAY['https://source-inconnue']
                        WHERE tpl_id = 100 AND shrcat_path = 'dct:language' ;
                    UPDATE z_plume.meta_template_categories
                        SET datatype = 'xsd:string',
                            label = 'Nom'
                        WHERE tpl_id = 100 AND shrcat_path = 'dct:title' ;
                    UPDATE z_plume.meta_template_categories
                        SET unilang = False,
                            is_mandatory = False
                        WHERE tpl_id = 100 AND shrcat_path = 'dct:description' ;
                    UPDATE z_plume.meta_template_categories
                        SET is_multiple = True,
                            is_read_only = True,
                            is_mandatory = True
                        WHERE tpl_id = 100 AND shrcat_path = 'owl:versionInfo' ;
                    UPDATE z_plume.meta_template_categories
                        SET datatype = 'xsd:dateTime'
                        WHERE tpl_id = 100 AND shrcat_path = 'dct:temporal / dcat:startDate' ;
                    UPDATE z_plume.meta_template_categories
                        SET datatype = 'xsd:string'
                        WHERE tpl_id = 100 AND shrcat_path = 'dct:temporal / dcat:endDate' ;
                    INSERT INTO z_plume.meta_template_categories (tpl_id, loccat_path, tab_id) (
                        SELECT 100, path, 102
                            FROM z_plume.meta_categorie
                            WHERE origin = 'local' AND label = 'Notes'
                        ) ;
                    """)
                cur.execute(
                    *query_get_categories('Mon formulaire')
                    )
                categories = cur.fetchall()
                cur.execute(
                    *query_template_tabs('Mon formulaire')
                    )
                tabs = cur.fetchall()
                cur.execute("""
                    SELECT path FROM z_plume.meta_categorie
                        WHERE origin = 'local' AND label = 'Notes'
                    """)
                locpath = cur.fetchone()[0]
                cur.execute('DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg')
        conn.close()
        template = TemplateDict(categories, tabs)
        nsm = PlumeNamespaceManager()
        properties, predicates = class_properties(rdfclass=DCAT.Dataset,
            nsm=nsm, base_path=None, template=template)
        t = 0
        for p in properties:
            # catégories communes, avec fusion du schéma et du modèle
            if p.n3_path == 'dcat:theme':
                t += 1
                self.assertFalse(p.unlisted)
                self.assertEqual(p.predicate, DCAT.theme)
                self.assertEqual(p.path, DCAT.theme)
                self.assertEqual(p.prop_dict['sources'],
                    [URIRef('http://publications.europa.eu/resource/authority/data-theme')]),
                self.assertEqual(p.prop_dict['order_idx'], (5,4))
            if p.n3_path == 'dct:language':
                t += 1
                self.assertEqual(p.prop_dict['sources'],
                    [URIRef('http://publications.europa.eu/resource/authority/language')])
                self.assertEqual(p.prop_dict['tab'], 'Secondaire')
            if p.n3_path == 'dct:title':
                t += 1
                self.assertEqual(p.prop_dict['datatype'], RDF.langString)
                self.assertEqual(p.prop_dict['label'], 'Nom')
            if p.n3_path == 'dct:description':
                t += 1
                self.assertTrue(p.prop_dict['unilang'])
                self.assertTrue(p.prop_dict['is_mandatory'])
                self.assertEqual(p.prop_dict['label'], 'Description')
            if p.n3_path == 'owl:versionInfo':
                t += 1
                self.assertFalse(p.prop_dict['is_multiple'])
                self.assertTrue(p.prop_dict['is_mandatory'])
                self.assertTrue(p.prop_dict['is_read_only'])
            if p.n3_path == 'dct:spatial':
                t += 1
            if p.n3_path == 'dct:conformsTo':
                t += 1
                self.assertTrue(URIRef('http://www.opengis.net/def/crs/EPSG/0') in p.prop_dict['sources'])
            # catégorie commune hors modèle
            if p.n3_path == 'dct:created':
                t += 1
                self.assertEqual(p.prop_dict['label'],
                    Literal('Date de création', lang='fr'))
                self.assertTrue(p.unlisted)
        # catégorie locale
        for n3_path in template.local.keys():
            t += 1
            p = PlumeProperty(origin='local', nsm=nsm, n3_path=n3_path,
                template=template)
            self.assertFalse(p.unlisted)
            self.assertEqual(p.n3_path, locpath)
            self.assertEqual(p.predicate, from_n3(locpath, nsm=nsm))
            self.assertEqual(p.path, from_n3(locpath, nsm=nsm))
            self.assertTrue(p.prop_dict['is_multiple'])
            self.assertEqual(p.prop_dict['datatype'], RDF.langString)
            self.assertEqual(p.prop_dict['label'], 'Notes')
            self.assertTrue(p.prop_dict['is_long_text'])
            self.assertEqual(p.prop_dict['tab'], 'Secondaire')
        self.assertEqual(t, 9)
        # catégorie non référencée
        p = PlumeProperty(origin='unknown', nsm=nsm,
            predicate=URIRef('urn:uuid:479fd670-32c5-4ade-a26d-0268b0ce5046'))
        self.assertEqual(p.prop_dict,
            {'predicate': URIRef('urn:uuid:479fd670-32c5-4ade-a26d-0268b0ce5046')})
        self.assertTrue(p.unlisted)
        self.assertEqual(p.n3_path, 'uuid:479fd670-32c5-4ade-a26d-0268b0ce5046')
        self.assertEqual(p.predicate, LOCAL['479fd670-32c5-4ade-a26d-0268b0ce5046'])
        self.assertEqual(p.path, LOCAL['479fd670-32c5-4ade-a26d-0268b0ce5046'])
        # catégories de niveau 2
        properties, predicates = class_properties(rdfclass=DCT.PeriodOfTime,
            nsm=nsm, base_path=DCT.temporal, template=template)
        t = 0
        for p in properties:
            if p.n3_path == 'dct:temporal / dcat:startDate':
                t += 1
                self.assertEqual(p.path, DCT.temporal / DCAT.startDate)
                self.assertFalse(p.unlisted)
                self.assertEqual(p.predicate, DCAT.startDate)
                self.assertEqual(p.prop_dict['label'], 'Date de début')
                self.assertEqual(p.prop_dict['datatype'], XSD.dateTime)
                # changement de type licite
            if p.n3_path == 'dct:temporal / dcat:endDate':
                t += 1
                self.assertEqual(p.prop_dict['datatype'], XSD.date)
                # changement de type illicite ignoré
        self.assertEqual(t, 2)
        properties, predicates = class_properties(rdfclass=DCT.Location,
            nsm=nsm, base_path=DCT.spatial, template=template)
        t = 0
        for p in properties:
            if p.n3_path == 'dct:spatial / locn:geometry':
                    t += 1
                    self.assertListEqual(p.prop_dict['geo_tools'],
                        ['point', 'rectangle'])
        self.assertEqual(t, 1)

    def test_property_param_values(self):
        """Récupération des valeurs d'une option de configuration d'une catagéorie commune."""
        self.assertListEqual(property_param_values('dct:title', 'sh:datatype'), [RDF.langString])
        self.assertListEqual(property_param_values(DCT.title, SH.datatype), [RDF.langString])
        self.assertListEqual(property_param_values('dct:temporal / dcat:endDate', 'sh:datatype'), [XSD.date])
        self.assertListEqual(property_param_values(DCT.temporal / DCAT.endDate, 'sh:datatype'), [XSD.date])
        self.assertEqual(property_param_values('plume:inconnu', 'sh:datatype'), [])
        self.assertEqual(property_param_values(DCT.temporal / DCAT.endDate, 'plume:inconnu'), [])

    def test_property_sources(self):
        """Récupération des sources disponibles pour une catégories communes."""
        self.assertIn('http://inspire.ec.europa.eu/theme', property_sources(DCAT.theme))
        self.assertIn('http://inspire.ec.europa.eu/theme', property_sources('dcat:theme'))
        self.assertIn('http://publications.europa.eu/resource/authority/licence', property_sources(DCAT.distribution / DCT.license))
        self.assertIn('http://publications.europa.eu/resource/authority/licence', property_sources('dcat:distribution / dct:license'))
        self.assertEqual([], property_sources('dct:title'))

if __name__ == '__main__':
    unittest.main()

