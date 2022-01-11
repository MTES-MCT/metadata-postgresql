"""Recette du module properties.

Les tests nécessitent une connexion PostgreSQL (paramètres à
saisir lors de l'exécution du test) pointant sur une base où 
l'extension plume_pg est installée. Il est préférable d'utiliser
un super-utilisateur.

"""

import unittest, psycopg2

from plume.rdf.rdflib import URIRef
from plume.rdf.properties import class_properties
from plume.rdf.namespaces import RDF, DCAT, PlumeNamespaceManager
from plume.pg.tests.connection import ConnectionString
from plume.pg.queries import query_get_categories, query_template_tabs
from plume.pg.template import TemplateDict

connection_string = ConnectionString()

class PlumePropertyTestCase(unittest.TestCase):

    def test_class_properties_with_template(self):
        """Génération des catégories communes de la classe dcat:Dataset, avec personnalisation par un modèle.
        
        Le test crée un modèle sur le serveur PostgreSQL,
        l'importe puis réinstalle l'extension PlumePg pour
        effacer les modifications réalisées.
        
        """
        conn = psycopg2.connect(connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO z_plume.meta_template(tpl_label) VALUES ('Mon formulaire') ;
                    INSERT INTO z_plume.meta_tab (tab, tab_num)
                        VALUES ('Principal', 1), ('Secondaire', 2) ;
                    INSERT INTO z_plume.meta_categorie (label, datatype, is_long_text)
                        VALUES ('Notes', 'rdf:langString', True) ;
                    INSERT INTO z_plume.meta_template_categories
                        (tpl_label, shrcat_path, tab, template_order)
                        VALUES
                        ('Mon formulaire', 'dct:description', 'Secondaire', 1),
                        ('Mon formulaire', 'dct:modified', 'Secondaire', 2),
                        ('Mon formulaire', 'dct:temporal / dcat:startDate', 'Secondaire', 3),
                        ('Mon formulaire', 'dct:temporal / dcat:endDate', 'Secondaire', 4),
                        ('Mon formulaire', 'dct:title', 'Principal', 1),
                        ('Mon formulaire', 'owl:versionInfo', 'Principal', 2),
                        ('Mon formulaire', 'dcat:theme', 'Secondaire', 5),
                        ('Mon formulaire', 'dct:subject', 'Secondaire', 6) ;
                    UPDATE z_plume.meta_template_categories
                        SET sources = ARRAY['http://publications.europa.eu/resource/authority/data-theme']
                        WHERE tpl_label = 'Mon formulaire' AND shrcat_path = 'dcat:theme' ;
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
                cur.execute('DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg')
        conn.close()
        template = TemplateDict(categories, tabs)
        nsm = PlumeNamespaceManager()
        properties, predicates = class_properties(rdfclass=DCAT.Dataset,
            nsm=nsm, base_path=None, template=template)
        t = 0
        for p in properties:
            if p.n3_path == 'dcat:theme':
                t += 1
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
            if p.n3_path == 'owl:versionInfo':
                t += 1
                self.assertFalse(p.prop_dict['is_multiple'])
                self.assertTrue(p.prop_dict['is_mandatory'])
                self.assertTrue(p.prop_dict['is_read_only'])
        self.assertEqual(t, 5)            

if __name__ == '__main__':
    unittest.main()

