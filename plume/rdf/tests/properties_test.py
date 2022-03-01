"""Recette du module properties.

Les tests nécessitent une connexion PostgreSQL (paramètres à
saisir lors de l'exécution du test) pointant sur une base où 
l'extension plume_pg est installée. Il est préférable d'utiliser
un super-utilisateur.

"""

import unittest, psycopg2

from plume.rdf.rdflib import URIRef, Literal, from_n3
from plume.rdf.properties import class_properties, PlumeProperty
from plume.rdf.namespaces import RDF, DCAT, LOCAL, DCT, PlumeNamespaceManager
from plume.pg.tests.connection import ConnectionString
from plume.pg.queries import query_get_categories, query_template_tabs
from plume.pg.template import TemplateDict

class PlumePropertyTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Création de la connexion PG.
        
        """
        cls.connection_string = ConnectionString()

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
                    INSERT INTO z_plume.meta_template(tpl_label) VALUES ('Mon formulaire') ;
                    INSERT INTO z_plume.meta_tab (tab, tab_num)
                        VALUES ('Principal', 1), ('Secondaire', 2) ;
                    INSERT INTO z_plume.meta_categorie
                        (label, datatype, is_long_text, is_multiple)
                        VALUES ('Notes', 'rdf:langString', True, True) ;
                    INSERT INTO z_plume.meta_template_categories
                        (tpl_label, shrcat_path, tab, template_order)
                        VALUES
                        ('Mon formulaire', 'dct:description', 'Secondaire', 1),
                        ('Mon formulaire', 'dct:modified', 'Secondaire', 2),
                        ('Mon formulaire', 'dct:temporal / dcat:startDate', 'Secondaire', 3),
                        ('Mon formulaire', 'dct:temporal / dcat:endDate', 'Secondaire', 4),
                        ('Mon formulaire', 'dct:title', 'Principal', 1),
                        ('Mon formulaire', 'owl:versionInfo', 'Principal', 2),
                        ('Mon formulaire', 'dct:spatial / locn:geometry', 'Secondaire', 10),
                        ('Mon formulaire', 'dcat:theme', 'Secondaire', 5),
                        ('Mon formulaire', 'dct:subject', 'Secondaire', 6) ;
                    UPDATE z_plume.meta_template_categories
                        SET sources = ARRAY['http://publications.europa.eu/resource/authority/data-theme']
                        WHERE tpl_label = 'Mon formulaire' AND shrcat_path = 'dcat:theme' ;
                    UPDATE z_plume.meta_template_categories
                        SET geo_tools = ARRAY['point', 'rectangle']::z_plume.meta_geo_tool[]
                        WHERE tpl_label = 'Mon formulaire' AND shrcat_path = 'dct:spatial / locn:geometry' ;
                    UPDATE z_plume.meta_template_categories
                        SET sources = ARRAY['https://source-inconnue']
                        WHERE tpl_label = 'Mon formulaire' AND shrcat_path = 'dct:subject' ;
                    UPDATE z_plume.meta_template_categories
                        SET datatype = 'xsd:string',
                            label = 'Nom'
                        WHERE tpl_label = 'Mon formulaire' AND shrcat_path = 'dct:title' ;
                    UPDATE z_plume.meta_template_categories
                        SET unilang = False,
                            is_mandatory = False
                        WHERE tpl_label = 'Mon formulaire' AND shrcat_path = 'dct:description' ;
                    UPDATE z_plume.meta_template_categories
                        SET is_multiple = True,
                            is_read_only = True,
                            is_mandatory = True
                        WHERE tpl_label = 'Mon formulaire' AND shrcat_path = 'owl:versionInfo' ;
                    INSERT INTO z_plume.meta_template_categories (tpl_label, loccat_path, tab) (
                        SELECT 'Mon formulaire', path, 'Secondaire'
                            FROM z_plume.meta_categorie
                            WHERE origin = 'local' AND label = 'Notes'
                        ) ;
                    """)
                cur.execute(
                    query_get_categories(),
                    ('Mon formulaire',)
                    )
                categories = cur.fetchall()
                cur.execute(
                    query_template_tabs(),
                    ('Mon formulaire',)
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
            if p.n3_path == 'dct:subject':
                t += 1
                self.assertEqual(p.prop_dict['sources'],
                    [URIRef('https://inspire.ec.europa.eu/metadata-codelist/TopicCategory')])
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
        self.assertEqual(t, 8)
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
        self.assertEqual(t, 1)
        properties, predicates = class_properties(rdfclass=DCT.Location,
            nsm=nsm, base_path=DCT.spatial, template=template)
        t = 0
        for p in properties:
            if p.n3_path == 'dct:spatial / locn:geometry':
                    t += 1
                    self.assertListEqual(p.prop_dict['geo_tools'],
                        ['point', 'rectangle'])
        self.assertEqual(t, 1)
        

if __name__ == '__main__':
    unittest.main()

