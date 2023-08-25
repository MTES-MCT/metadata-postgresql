"""Contrôles de cohérence.

Le code de Plume est partiellement redondant, avec notamment des
informations dupliquées dans le script d'installation de PlumePg.
Le présent module met à disposition des outils pour contrôler
la cohérence de ces éléments.

"""

import unittest
import psycopg2
import json
import re
from pathlib import Path

from plume.pg.tests.connection import ConnectionString
from plume.pg import queries
from plume.pg.template import dump_template_data
from plume.rdf.utils import abspath, data_from_file
from plume import __path__ as plume_path

from admin.plume_pg import store_sample_templates, query_from_shape

class ConsistencyTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.connection_string = ConnectionString()
        conn = psycopg2.connect(cls.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    *queries.query_plume_pg_import_sample_template()
                )

                cur.execute(
                    *queries.query_read_meta_template()
                )
                cls.plume_pg_templates = cur.fetchall()

                cur.execute(
                    *queries.query_read_meta_categorie()
                )
                cls.plume_pg_categories = cur.fetchall()

                cur.execute(
                    *queries.query_read_meta_tab()
                )
                cls.plume_pg_tabs = cur.fetchall()

                cur.execute(
                    *queries.query_read_meta_template_categories()
                )
                cls.plume_pg_template_categories = cur.fetchall()

                cur.execute('''
                    DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg
                ''')
        conn.close()
        
        cls.pfile = Path(plume_path[0]).parent / 'admin/consistency_plume_pg_data_temp.json'
        dump_template_data(
            cls.pfile,
            templates=cls.plume_pg_templates,
            categories=cls.plume_pg_categories,
            tabs=cls.plume_pg_tabs,
            template_categories=cls.plume_pg_template_categories
        )
        raw_data = data_from_file(cls.pfile)
        cls.plume_pg_data = json.loads(raw_data)
        cls.pfile.unlink()

        raw_data = data_from_file(abspath('pg/data/templates.json'))
        cls.local_templates_data = json.loads(raw_data)

    def test_sample_templates_local_copies_check(self):
        """Cohérence des modèles pré-configurés de PlumePg et de leurs copies locales."""
        store_sample_templates(ConsistencyTestCase.pfile)
        raw_data = data_from_file(ConsistencyTestCase.pfile)
        new_local_templates_data = json.loads(raw_data)
        ConsistencyTestCase.pfile.unlink()

        # les modèles qui sont dans l'un sont dans l'autre
        for tpl_label in new_local_templates_data:
            self.assertTrue(tpl_label in ConsistencyTestCase.local_templates_data, f'manquant en local : {tpl_label}')
        for tpl_label in ConsistencyTestCase.local_templates_data:
            self.assertTrue(tpl_label in new_local_templates_data, f'manquant dans PlumePg : {tpl_label}')

        for tpl_label in new_local_templates_data:
            # suppression des informations qui peuvent être différentes
            del new_local_templates_data[tpl_label]['configuration']['comment']
            del new_local_templates_data[tpl_label]['configuration']['tpl_id']
            for template_category in new_local_templates_data[tpl_label]['categories']:
                del template_category['tplcat_id']
            del ConsistencyTestCase.local_templates_data[tpl_label]['configuration']['comment']
            del ConsistencyTestCase.local_templates_data[tpl_label]['configuration']['tpl_id']
            for template_category in ConsistencyTestCase.local_templates_data[tpl_label]['categories']:
                del template_category['tplcat_id']
            # contrôle de l'identicité de la configuration des modèles
            self.assertEqual(new_local_templates_data[tpl_label], ConsistencyTestCase.local_templates_data[tpl_label])

    def test_plume_pg_categories_insert(self):
        """Cohérence de la requête INSERT qui importe les catégories communes dans PlumePg avec le schéma des catégories communes.
        
        Pour que ce test soit concluant, la requête incluse dans le
        fichier d'installation à la racine du répertoire ``postgresql``
        doit être exactement identique au résultat de la fonction
        :py:func:`admin.plume_pg.query_from_shape`.
        
        """
        insert_query = query_from_shape(do_not_print=True)
        pg_dir = Path(plume_path[0]).parent / 'postgresql'
        for file in pg_dir.iterdir():
            if file.is_file() and re.match('^plume_pg--(\d[.])+sql$', file.name):
                plume_pg_raw = data_from_file(file)
                break
        self.assertIn(insert_query, plume_pg_raw)

if __name__ == '__main__':
    unittest.main()