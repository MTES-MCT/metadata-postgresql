"""Recette du module template.

Les tests nécessitent une connexion PostgreSQL (paramètres à
saisir lors de l'exécution du test) pointant sur une base où 
l'extension plume_pg est installée. Il est préférable d'utiliser
un super-utilisateur.

"""

import unittest
import psycopg2
import json
from pathlib import Path

from plume.rdf.utils import data_from_file, abspath
from plume.rdf.rdflib import URIRef
from plume.rdf.namespaces import RDF, DCAT
from plume.rdf.widgetsdict import WidgetsDict
from plume.pg.template import (
    TemplateDict, search_template, LocalTemplatesCollection,
    dump_template_data, TemplateQueryBuilder
)
from plume.pg.description import PgDescription
from plume.pg.tests.connection import ConnectionString
from plume.pg.queries import (
    query_list_templates, query_get_categories,
    query_template_tabs, query_evaluate_local_templates,
    query_read_meta_categorie, query_read_meta_tab,
    query_read_meta_template, query_read_meta_template_categories
)

class TemplateTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Création de la connexion PG.
        
        """
        cls.connection_string = ConnectionString()

    def test_search_template(self):
        """Sélection automatisée du modèle à utiliser.

        Ce premier test utilise des modèles fictifs, qu'il
        crée lui-même sous forme d'objets python.
        
        """
        pg_description_1 = PgDescription(data_from_file(abspath('pg/tests/samples/pg_description_1.txt')))
        pg_description_2 = PgDescription(data_from_file(abspath('pg/tests/samples/pg_description_2.txt')))
        template1 = (
            'template 1',
            True, None, 10
            )
        template2 = (
            'template 2',
            False,
            [
                {
                    "plume:isExternal": True,
                    "dcat:keyword": "IGN"
                }
            ], 20)
        template3 = (
            'template 3',
            False,
            [
                {
                    "plume:isExternal": True,
                    "dcat:keyword": "IGN-F"
                },
                {
                    "dct:publisher / foaf:name": "Institut national de l'information géographique et forestière (IGN-F)"
                }
            ], 15)
        self.assertEqual(
            search_template(
                [template1]
                ),
            'template 1'
            )
        self.assertEqual(
            search_template(
                [template1, template2, template3]
                ),
            'template 1'
            )
        self.assertEqual(
            search_template(
                [template2, template3, template1],
                metagraph = None
                ),
            'template 1'
            )
        self.assertEqual(
            search_template(
                [template2, template3, template1],
                pg_description_2.metagraph,
                ),
            'template 1'
            )
        self.assertEqual(
            search_template(
                [template1, template2, template3],
                pg_description_1.metagraph
                ),
            'template 2'
            )
        self.assertEqual(
            search_template(
                [template1, template3],
                pg_description_1.metagraph
                ),
            'template 3'
            )
        self.assertEqual(
            search_template(
                [template3],
                pg_description_1.metagraph
                ),
            'template 3'
            )

    def test_search_template_sample_templates(self):
        """Sélection automatisée du modèle à utiliser parmi les modèles pré-configurés.

        Ce test charge les modèles pré-configurés sur
        le serveur PostgreSQL, en importe la liste, et
        les supprime.
        
        """
        pg_description_1 = PgDescription(data_from_file(abspath('pg/tests/samples/pg_description_1.txt')))
        pg_description_2 = PgDescription(data_from_file(abspath('pg/tests/samples/pg_description_2.txt')))
        conn = psycopg2.connect(TemplateTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM z_plume.meta_import_sample_template()')
                cur.execute(
                    *query_list_templates('s_schema', 'table')
                    )
                templates_a = cur.fetchall()
                cur.execute(
                    *query_list_templates('r_admin_express', 'departement_2154')
                    )
                templates_b = cur.fetchall()
                cur.execute(
                    *query_list_templates('c_amgt_urb_zon_amgt', 'l_zac_075')
                    )
                templates_c = cur.fetchall()
                cur.execute('DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg')
        conn.close()
        self.assertIsNone(
            search_template(templates_a)
            )
        self.assertEqual(
            search_template(templates_b, pg_description_1.metagraph),
            'Donnée externe'
            )
        self.assertEqual(
            search_template(templates_c, pg_description_2.metagraph),
            'Basique'
            )

    def test_templatedict_sample_templates(self):
        """Génération des modèles pré-configurés.

        Le test utilise le modèle pré-configuré
        "Classique", qui est importé puis
        supprimé de la table des modèles au cours
        de l'exécution (de même que les autres
        modèles pré-configurés).
        
        """
        conn = psycopg2.connect(TemplateTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM z_plume.meta_import_sample_template()')
                cur.execute(
                    *query_get_categories('Classique')
                    )
                categories = cur.fetchall()
                cur.execute(
                    *query_template_tabs('Classique')
                    )
                tabs = cur.fetchall()
                cur.execute('DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg')
        conn.close()
        template = TemplateDict(categories, tabs)
        self.assertEqual(len(template.shared), 41)
        self.assertEqual(template.local, {})
        d = {k: False for k in template.shared['dct:title'].keys()}
        # on vérifie que chaque caractéristique prend une valeur
        # non triviale pour au moins une propriété, sauf celles
        # dont on sait qu'elles ne sont pas utilisées par le
        # modèle "Classique"
        for prop_dict in template.shared.values():
            for k, v in prop_dict.items():
                if v and k in d:
                    del d[k]
                if not d:
                    break
        self.assertEqual(d, {'is_read_only': False, 'tab': False,
            'geo_tools': False, 'compute_params': False})

    def test_templatedict_homemade_template(self):
        """Génération d'un modèle avec onglets et catégories locales.
        
        Le test crée un modèle sur le serveur PostgreSQL,
        l'importe puis réinstalle l'extension PlumePg pour
        effacer les modifications réalisées.
        
        """
        conn = psycopg2.connect(TemplateTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO z_plume.meta_template(tpl_id, tpl_label) VALUES (100, 'Mon formulaire') ;
                    INSERT INTO z_plume.meta_tab (tab_id, tab_label, tab_num)
                        VALUES (101, 'Principal', 1), (102, 'Secondaire', 2) ;
                    INSERT INTO z_plume.meta_categorie (label, datatype, is_long_text)
                        VALUES ('Notes', 'rdf:langString', True) ;
                    INSERT INTO z_plume.meta_template_categories (tpl_id, shrcat_path, tab_id)
                        VALUES
                        (100, 'dct:description', 102),
                        (100, 'dct:modified', 102),
                        (100, 'dct:temporal / dcat:startDate', 102),
                        (100, 'dct:temporal / dcat:endDate', 102),
                        (100, 'dct:title', 101),
                        (100, 'owl:versionInfo', 101) ;
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
                cur.execute('DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg')
        conn.close()
        template = TemplateDict(categories, tabs)
        self.assertTrue('dct:temporal' in template.shared)
        # le chemin intermédiaire dct:temporal n'est pas répertorié
        # dans les catégories du modèle par meta_template_categories,
        # mais TemplateDict est censé l'ajouter automatiquement.
        self.assertEqual(len(template.shared), 7)
        self.assertEqual(template.shared['dct:title']['tab'], 'Principal')
        self.assertEqual(template.shared['dct:modified']['tab'], 'Secondaire')
        self.assertEqual(len(template.local), 1)
        for v in template.local.values():
            self.assertTrue(v['is_long_text'])
            self.assertEqual(v['label'], 'Notes')
            self.assertEqual(v['datatype'], RDF.langString)
            self.assertEqual(v['tab'], 'Secondaire')
        self.assertEqual(len(template.tabs), 2)
        self.assertTrue('Principal' in template.tabs)
        self.assertTrue('Secondaire' in template.tabs)

    def test_local_templates(self):
        """Processus de sélection du modèle avec modèles stockés en local.
        
        L'extension PlumePg est désinstallée pendant la durée
        du test.
        
        """
        templates_collection = LocalTemplatesCollection()
        self.assertEqual(len(templates_collection.labels), 4)
        self.assertTrue('Basique' in templates_collection.labels)
        pg_description_1 = PgDescription(data_from_file(abspath('pg/tests/samples/pg_description_1.txt')))
        pg_description_2 = PgDescription(data_from_file(abspath('pg/tests/samples/pg_description_2.txt')))
        conn = psycopg2.connect(TemplateTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('DROP EXTENSION plume_pg')
                cur.execute(
                    *query_evaluate_local_templates(templates_collection, 's_schema', 'table')
                    )
                templates_a = cur.fetchall()
                cur.execute(
                    *query_evaluate_local_templates(templates_collection, 'r_admin_express', 'departement_2154')
                    )
                templates_b = cur.fetchall()
                cur.execute(
                    *query_evaluate_local_templates(templates_collection, 'c_amgt_urb_zon_amgt', 'l_zac_075')
                    )
                templates_c = cur.fetchall()
                cur.execute('CREATE EXTENSION plume_pg')
        conn.close()
        self.assertIsNone(
            search_template(templates_a)
            )
        self.assertEqual(
            search_template(templates_b),
            'Donnée externe'
            )
        self.assertEqual(
            search_template(templates_a, pg_description_1.metagraph),
            'Donnée externe'
            )
        self.assertEqual(
            search_template(templates_c, pg_description_2.metagraph),
            'Basique'
            )

    def test_local_template_sources(self):
        """Récupération des sources de vocabulaires contrôlés avec les modèles stockés en local.

        """
        templates_collection = LocalTemplatesCollection()
        pg_description_1 = PgDescription(data_from_file(abspath('pg/tests/samples/pg_description_1.txt')))
        template = templates_collection['Donnée externe']
        self.assertTrue(URIRef('http://inspire.ec.europa.eu/theme') in template.shared['dcat:theme']['sources'])
        self.assertTrue(URIRef('http://publications.europa.eu/resource/authority/data-theme') in template.shared['dcat:theme']['sources'])
        widgetdict = WidgetsDict(pg_description_1.metagraph, template=template, langList=['fr', 'en'])
        k = widgetdict.root.search_from_path(DCAT.theme)
        self.assertIsNotNone(k)
        self.assertEqual(len(k.children), 2)
        c0 = k.children[0]
        c1 = k.children[1]
        self.assertTrue(URIRef('http://inspire.ec.europa.eu/theme') in c0.sources)
        self.assertTrue(URIRef('http://publications.europa.eu/resource/authority/data-theme') in c0.sources)
        self.assertEqual(c0.value_source, URIRef('http://publications.europa.eu/resource/authority/data-theme'))
        self.assertEqual(c1.value_source, URIRef('http://inspire.ec.europa.eu/theme'))
        self.assertEqual(c1.value, URIRef('http://inspire.ec.europa.eu/theme/au'))
        self.assertEqual(widgetdict[c1]['value'], 'Unités administratives')
        self.assertEqual(widgetdict[c1]['value'], 'Unités administratives')
        self.assertTrue(widgetdict[c1]['multiple sources'])

    def test_dump_template_data_all(self):
        """Export en JSON de toutes les données des modèles.

        """
        pfile = Path(abspath('pg/tests/export/template_data_temp.json'))
        conn = psycopg2.connect(TemplateTestCase.connection_string)

        with conn:
            with conn.cursor() as cur:

                # sans modèle, juste les catégories communes
                cur.execute(
                    *query_read_meta_template()
                )
                templates = cur.fetchall()
                cur.execute(
                    *query_read_meta_categorie()
                )
                categories = cur.fetchall()
                cur.execute(
                    *query_read_meta_tab()
                )
                tabs = cur.fetchall()
                cur.execute(
                    *query_read_meta_template_categories()
                )
                template_categories = cur.fetchall()

                # avec les modèles pré-configurés
                cur.execute('SELECT * FROM z_plume.meta_import_sample_template()')
                cur.execute(
                    *query_read_meta_template()
                )
                templates_2 = cur.fetchall()
                cur.execute(
                    *query_read_meta_categorie()
                )
                categories_2 = cur.fetchall()
                cur.execute(
                    *query_read_meta_tab()
                )
                tabs_2 = cur.fetchall()
                cur.execute(
                    *query_read_meta_template_categories()
                )
                template_categories_2 = cur.fetchall()

                cur.execute('DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg')

        conn.close()

        dump_template_data(
            pfile,
            templates=templates,
            categories=categories,
            tabs=tabs,
            template_categories=template_categories
        )

        raw_data = data_from_file(pfile)
        self.assertTrue(raw_data)

        data = json.loads(raw_data)
        self.assertTrue('categories' in data)
        self.assertTrue(data['categories'])
        self.assertFalse('tabs' in data)
        self.assertFalse('templates' in data)
        self.assertFalse('template_categories' in data)

        dump_template_data(
            pfile,
            templates=templates_2,
            categories=categories_2,
            tabs=tabs_2,
            template_categories=template_categories_2
        )

        raw_data = data_from_file(pfile)
        self.assertTrue(raw_data)

        data = json.loads(raw_data)
        self.assertTrue('categories' in data)
        self.assertTrue(data['categories'])
        self.assertTrue('tabs' in data)
        self.assertTrue(data['tabs'])
        self.assertTrue('templates' in data)
        self.assertTrue(data['templates'])
        self.assertTrue('template_categories' in data)
        self.assertTrue(data['template_categories'])

        pfile.unlink()

    def test_dump_template_data_inspire(self):
        """Export en JSON du modèle pré-configuré INSPIRE.

        """
        pfile = Path(abspath('pg/tests/export/template_data_temp.json'))

        conn = psycopg2.connect(TemplateTestCase.connection_string)

        with conn:
            with conn.cursor() as cur:

                cur.execute('SELECT * FROM z_plume.meta_import_sample_template()')
                cur.execute(
                    *query_read_meta_template()
                )
                templates = cur.fetchall()
                cur.execute(
                    *query_read_meta_categorie()
                )
                categories = cur.fetchall()
                cur.execute(
                    *query_read_meta_tab()
                )
                tabs = cur.fetchall()
                cur.execute(
                    *query_read_meta_template_categories()
                )
                template_categories = cur.fetchall()

                cur.execute(
                    "SELECT tpl_id FROM z_plume.meta_template WHERE tpl_label = 'INSPIRE'"
                )
                tpl_id = cur.fetchone()[0]

                cur.execute('DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg')

        conn.close()

        dump_template_data(
            pfile,
            templates=templates,
            categories=categories,
            tabs=tabs,
            template_categories=template_categories,
            tpl_id=tpl_id
        )

        raw_data = data_from_file(pfile)
        self.assertTrue(raw_data)

        data = json.loads(raw_data)
        self.assertTrue('categories' in data)
        self.assertTrue(data['categories'])
        self.assertTrue('tabs' in data)
        self.assertTrue(data['tabs'])
        self.assertTrue('templates' in data)
        self.assertEqual(len(data['templates']), 1)
        self.assertEqual(data['templates'][0]['tpl_label'], 'INSPIRE')
        self.assertTrue('template_categories' in data)
        self.assertTrue(data['template_categories'])
        self.assertTrue(
            all(
                data['template_categories'][n]['tpl_id'] == tpl_id
                for n in range(len(data['template_categories']))
            )
        )
        categories

        catpaths = [
            data['template_categories'][n]['shrcat_path'] 
            for n in range(len(data['template_categories']))
        ]
        self.assertTrue(
            all(
                data['categories'][n]['path'] in catpaths
                for n in range(len(data['categories']))
            )
        )

        pfile.unlink()

    def test_dump_template_data_two_templates(self):
        """Export en JSON des modèles pré-configurés INSPIRE et Basique.

        """
        pfile = Path(abspath('pg/tests/export/template_data_temp.json'))

        conn = psycopg2.connect(TemplateTestCase.connection_string)

        with conn:
            with conn.cursor() as cur:

                cur.execute('SELECT * FROM z_plume.meta_import_sample_template()')
                cur.execute(
                    *query_read_meta_template()
                )
                templates = cur.fetchall()
                cur.execute(
                    *query_read_meta_categorie()
                )
                categories = cur.fetchall()
                cur.execute(
                    *query_read_meta_tab()
                )
                tabs = cur.fetchall()
                cur.execute(
                    *query_read_meta_template_categories()
                )
                template_categories = cur.fetchall()

                cur.execute(
                    "SELECT tpl_id FROM z_plume.meta_template WHERE tpl_label = 'INSPIRE'"
                )
                tpl_id_inspire = cur.fetchone()[0]
                cur.execute(
                    "SELECT tpl_id FROM z_plume.meta_template WHERE tpl_label = 'Basique'"
                )
                tpl_id_basique = cur.fetchone()[0]

                cur.execute('DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg')

        conn.close()

        dump_template_data(
            pfile,
            templates=templates,
            categories=categories,
            tabs=tabs,
            template_categories=template_categories,
            tpl_id=[tpl_id_inspire, tpl_id_basique]
        )

        raw_data = data_from_file(pfile)
        self.assertTrue(raw_data)

        data = json.loads(raw_data)
        self.assertTrue('categories' in data)
        self.assertTrue(data['categories'])
        self.assertTrue('tabs' in data)
        self.assertTrue(data['tabs'])
        self.assertTrue('templates' in data)
        self.assertEqual(len(data['templates']), 2)
        self.assertTrue(data['templates'][0]['tpl_label'] in ('INSPIRE', 'Basique'))
        self.assertTrue(data['templates'][1]['tpl_label'] in ('INSPIRE', 'Basique'))
        self.assertTrue('template_categories' in data)
        self.assertTrue(data['template_categories'])
        self.assertTrue(
            all(
                data['template_categories'][n]['tpl_id'] in [tpl_id_inspire, tpl_id_basique]
                for n in range(len(data['template_categories']))
            )
        )
        categories

        catpaths = [
            data['template_categories'][n]['shrcat_path'] 
            for n in range(len(data['template_categories']))
        ]
        self.assertTrue(
            all(
                data['categories'][n]['path'] in catpaths
                for n in range(len(data['categories']))
            )
        )

        pfile.unlink()

    def test_load_template_inspire(self):
        """Test d'import du modèle INSPIRE depuis un export JSON."""
        builder = TemplateQueryBuilder(abspath('pg/tests/export/template_data_inspire.json'))
        conn = psycopg2.connect(TemplateTestCase.connection_string)

        with conn:
            with conn.cursor() as cur:

                for query in builder.queries():
                    cur.execute(*query)
                    if builder.waiting:
                        result = cur.fetchone()[0]
                        builder.feedback(result)
                
                cur.execute(
                    *query_read_meta_template()
                )
                templates = cur.fetchall()
                cur.execute(
                    *query_read_meta_categorie()
                )
                categories = cur.fetchall()
                cur.execute(
                    *query_read_meta_tab()
                )
                tabs = cur.fetchall()
                cur.execute(
                    *query_read_meta_template_categories()
                )
                template_categories = cur.fetchall()

                cur.execute('DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg')

        conn.close()

        self.assertEqual(len(templates), 1)
        self.assertTrue(categories)
        self.assertTrue(tabs)
        self.assertTrue(template_categories)

    def test_load_template_inspire_update(self):
        """Test de mise à jour du modèle INSPIRE depuis un export JSON."""
        builder = TemplateQueryBuilder(abspath('pg/tests/export/template_data_inspire.json'))
        conn = psycopg2.connect(TemplateTestCase.connection_string)

        with conn:
            with conn.cursor() as cur:

                cur.execute('SELECT * FROM z_plume.meta_import_sample_template()')
                cur.execute(
                    '''
                    UPDATE z_plume.meta_template
                        SET comment = 'Bricolage'
                        WHERE tpl_label = 'INSPIRE'
                        RETURNING tpl_id
                    '''
                )
                tpl_id_inspire = cur.fetchone()[0]
                cur.execute(
                    '''
                    INSERT INTO z_plume.meta_template_categories
                        (shrcat_path, tpl_id) VALUES ('adms:versionNotes', %s)
                    ''',
                    (tpl_id_inspire,)
                )
                cur.execute(
                    '''
                    DELETE FROM z_plume.meta_template_categories
                        WHERE shrcat_path = 'dct:title'
                            AND tpl_id = %s
                    ''',
                    (tpl_id_inspire,)
                )
                cur.execute(
                    '''
                    UPDATE z_plume.meta_categorie
                        SET label = 'Truc'
                        WHERE path = 'dct:description'
                    '''
                )
                cur.execute(
                    '''
                    SELECT count(*) FROM z_plume.meta_template
                    UNION
                    SELECT count(*) FROM z_plume.meta_template_categories
                    UNION
                    SELECT count(*) FROM z_plume.meta_tab
                    UNION
                    SELECT count(*) FROM z_plume.meta_categorie
                    '''
                )
                ref_count = cur.fetchall()

                for query in builder.queries():
                    cur.execute(*query)
                    if builder.waiting:
                        result = cur.fetchone()
                        builder.feedback(result)

                cur.execute(
                    '''
                    SELECT count(*) FROM z_plume.meta_template
                    UNION
                    SELECT count(*) FROM z_plume.meta_template_categories
                    UNION
                    SELECT count(*) FROM z_plume.meta_tab
                    UNION
                    SELECT count(*) FROM z_plume.meta_categorie
                    '''
                )
                new_count = cur.fetchall()

                cur.execute(
                    '''
                    SELECT
                        'adms:versionNotes' IN (
                            SELECT shrcat_path
                                FROM z_plume.meta_template_categories
                                WHERE tpl_id = %s
                        )
                    ''',
                    (tpl_id_inspire,)
                )
                version_note_check = cur.fetchone()[0]

                cur.execute(
                    '''
                    SELECT
                        'dct:title' IN (
                            SELECT shrcat_path
                                FROM z_plume.meta_template_categories
                                WHERE tpl_id = %s
                        )
                    ''',
                    (tpl_id_inspire,)
                )
                title_check = cur.fetchone()[0]

                cur.execute(
                    '''
                    SELECT
                        comment
                        FROM z_plume.meta_template
                        WHERE tpl_id = %s
                    ''',
                    (tpl_id_inspire,)
                )
                comment_check = cur.fetchone()[0]

                cur.execute(
                    '''
                    SELECT
                        label
                        FROM z_plume.meta_categorie
                        WHERE path = 'dct:description'
                    '''
                )
                label_check = cur.fetchone()[0]
                
                cur.execute('DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg')

        conn.close()

        self.assertEqual(label_check, 'Description')
        self.assertEqual(comment_check, 'Métadonnées obligatoires INSPIRE prises en charge par Plume.')
        self.assertTrue(title_check)
        self.assertFalse(version_note_check)
        self.assertEqual(ref_count, new_count)
    
    def test_load_template_inspire_no_update(self):
        """Test de mise à jour du modèle INSPIRE depuis un export JSON, sans mise à jour des onglets et catégories."""
        builder = TemplateQueryBuilder(
            abspath('pg/tests/export/template_data_inspire.json'),
            no_update=True
        )
        conn = psycopg2.connect(TemplateTestCase.connection_string)

        with conn:
            with conn.cursor() as cur:

                cur.execute('SELECT * FROM z_plume.meta_import_sample_template()')
                cur.execute(
                    '''
                    UPDATE z_plume.meta_tab
                        SET tab_num = 111
                        WHERE tab_label = 'Général'
                        RETURNING tab_id
                    '''
                )
                general_tab_id = cur.fetchone()[0]
                cur.execute(
                    '''
                    UPDATE z_plume.meta_categorie
                        SET label = 'Truc'
                        WHERE path = 'dct:description'
                    '''
                )
                cur.execute(
                    '''
                    SELECT count(*) FROM z_plume.meta_template
                    UNION
                    SELECT count(*) FROM z_plume.meta_template_categories
                    UNION
                    SELECT count(*) FROM z_plume.meta_tab
                    UNION
                    SELECT count(*) FROM z_plume.meta_categorie
                    '''
                )
                ref_count = cur.fetchall()

                for query in builder.queries():
                    cur.execute(*query)
                    if builder.waiting:
                        result = cur.fetchone()
                        builder.feedback(result)

                cur.execute(
                    '''
                    SELECT count(*) FROM z_plume.meta_template
                    UNION
                    SELECT count(*) FROM z_plume.meta_template_categories
                    UNION
                    SELECT count(*) FROM z_plume.meta_tab
                    UNION
                    SELECT count(*) FROM z_plume.meta_categorie
                    '''
                )
                new_count = cur.fetchall()

                cur.execute(
                    '''
                    SELECT tab_num FROM z_plume.meta_tab
                        WHERE tab_id = %s
                    ''',
                    (general_tab_id,)
                )
                tab_check = cur.fetchone()[0]

                cur.execute(
                    '''
                    SELECT
                        label
                        FROM z_plume.meta_categorie
                        WHERE path = 'dct:description'
                    '''
                )
                label_check = cur.fetchone()[0]
                
                cur.execute('DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg')

        conn.close()

        self.assertEqual(label_check, 'Truc')
        self.assertEqual(tab_check, 111)
        self.assertEqual(ref_count, new_count)

    def test_load_template_local_insert(self):
        """Chargement d'un modèle avec nouvelle catégorie locale."""
        builder = TemplateQueryBuilder(abspath('pg/tests/export/template_data_local_insert.json'))
        conn = psycopg2.connect(TemplateTestCase.connection_string)

        with conn:
            with conn.cursor() as cur:

                for query in builder.queries():
                    cur.execute(*query)
                    if builder.waiting:
                        result = cur.fetchone()[0]
                        builder.feedback(result)

                cur.execute(
                    '''
                    SELECT count(*) FROM z_plume.meta_categorie WHERE label = 'Autorisé'
                    '''
                )
                row_count = cur.fetchone()[0]
                
                cur.execute('DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg')

        conn.close()

        self.assertEqual(row_count, 1)

    def test_load_template_shared_insert(self):
        """Chargement d'un modèle avec nouvelle catégorie commune (sans effet)."""
        builder = TemplateQueryBuilder(abspath('pg/tests/export/template_data_shared_insert.json'))
        conn = psycopg2.connect(TemplateTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:

                for query in builder.queries():
                    cur.execute(*query)
                    if builder.waiting:
                        result = cur.fetchone()[0]
                        builder.feedback(result)

                cur.execute(
                    '''
                    SELECT count(*) FROM z_plume.meta_categorie WHERE label = 'Interdit'
                    '''
                )
                row_count = cur.fetchone()[0]
                
                cur.execute('DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg')

        conn.close()

        self.assertEqual(row_count, 0)

    def test_load_template_no_categorie(self):
        """Chargement d'associations modèle-catégorie avec une catégorie non explicitement définie."""
        builder = TemplateQueryBuilder(abspath('pg/tests/export/template_data_no_categorie.json'))
        conn = psycopg2.connect(TemplateTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:

                for query in builder.queries():
                    cur.execute(*query)
                    if builder.waiting:
                        result = cur.fetchone()[0]
                        builder.feedback(result)

                cur.execute(
                    '''
                    SELECT count(*) FROM z_plume.meta_template_categories
                        WHERE label = 'old 111 template'
                    '''
                )
                row_count = cur.fetchone()[0]
                
                cur.execute('DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg')

        conn.close()

        self.assertEqual(row_count, 1)
    
    def test_load_template_no_template(self):
        """Chargement d'associations modèle-catégorie avec un modèle non explicitement défini (interdit)."""
        builder = TemplateQueryBuilder(abspath('pg/tests/export/template_data_no_template.json'))
        try:
            conn = psycopg2.connect(TemplateTestCase.connection_string)
            with conn:
                with conn.cursor() as cur:

                    for query in builder.queries():
                        cur.execute(*query)
                        if builder.waiting:
                            result = cur.fetchone()[0]
                            builder.feedback(result)
                   
                    cur.execute('DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg')
            conn.close()
            self.assertTrue(False, 'An error should have occurred')
        except Exception as e:
            self.assertTrue(isinstance(e, ValueError))
            self.assertTrue('111' in str(e))

    def test_load_template_no_tab(self):
        """Chargement d'associations modèle-catégorie avec un onglet non explicitement défini (interdit)."""
        builder = TemplateQueryBuilder(abspath('pg/tests/export/template_data_no_tab.json'))
        try:
            conn = psycopg2.connect(TemplateTestCase.connection_string)
            with conn:
                with conn.cursor() as cur:

                    for query in builder.queries():
                        cur.execute(*query)
                        if builder.waiting:
                            result = cur.fetchone()[0]
                            builder.feedback(result)
                   
                    cur.execute('DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg')
            conn.close()
            self.assertTrue(False, 'An error should have occurred')
        except Exception as e:
            self.assertTrue(isinstance(e, ValueError))
            self.assertTrue('131' in str(e))

    def test_choose_template_without_priority(self):
        """Choix du modèle lorsque celui qui remplit la condition n'a pas de priorité définie."""
        conn = psycopg2.connect(TemplateTestCase.connection_string)

        with conn:
            with conn.cursor() as cur:

                cur.execute(
                    '''
                    INSERT INTO z_plume.meta_template (tpl_label, sql_filter, priority) VALUES
                        ('Bon modèle sans priorité', true, NULL),
                        ('Un autre modèle avec priorité', false, 10) ;
                    '''
                )
                cur.execute(
                    *query_list_templates('s_schema', 'table')
                    )
                templates = cur.fetchall()
                cur.execute('DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg')

        conn.close()

        self.assertEqual(
            search_template(templates),
            'Bon modèle sans priorité'
            )
        
    def test_dump_load_template_with_json_field(self):
        """Export et ré-import d'un modèle avec un attribut JSON."""
        pfile = Path(abspath('pg/tests/export/template_data_json_temp.json'))
        conn = psycopg2.connect(TemplateTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM z_plume.meta_import_sample_template()')
                cur.execute(r'''
                    UPDATE z_plume.meta_categorie
                        SET compute = ARRAY['new'],
                            compute_params = '{"pattern": "(t(?:\\s|\\w)+)[.]", "flags": "gi"}'::jsonb
                        WHERE path = 'dct:title' ;
                    ''')
                cur.execute(
                    *query_read_meta_template()
                )
                templates = cur.fetchall()
                cur.execute(
                    *query_read_meta_categorie()
                )
                categories = cur.fetchall()
                cur.execute(
                    *query_read_meta_tab()
                )
                tabs = cur.fetchall()
                cur.execute(
                    *query_read_meta_template_categories()
                )
                template_categories = cur.fetchall()

                cur.execute(
                    "SELECT tpl_id FROM z_plume.meta_template WHERE tpl_label = 'Basique'"
                )
                tpl_id = cur.fetchone()[0]
                cur.execute('DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg')
        conn.close()

        dump_template_data(
            pfile,
            templates=templates,
            categories=categories,
            tabs=tabs,
            template_categories=template_categories,
            tpl_id=tpl_id
        )
        builder = TemplateQueryBuilder(pfile)
        pfile.unlink()

        conn = psycopg2.connect(TemplateTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:

                for query in builder.queries():
                    cur.execute(*query)
                    if builder.waiting:
                        result = cur.fetchone()[0]
                        builder.feedback(result)
                
                cur.execute(r'''
                    SELECT compute_params = '{"pattern": "(t(?:\\s|\\w)+)[.]", "flags": "gi"}'::jsonb
                        FROM z_plume.meta_categorie
                        WHERE path = 'dct:title' ;
                    ''')
                res = cur.fetchone()[0]

                cur.execute('DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg')
        conn.close()
        self.assertTrue(res)

if __name__ == '__main__':
    unittest.main()

