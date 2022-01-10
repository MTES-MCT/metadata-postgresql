"""Recette du module template.

Les tests nécessite une connexion PostgreSQL (définie par
input) pointant sur une base où :
- l'extension plume_pg est installée ;
- le schéma z_plume_recette existe et contient les fonctions
de la recette côté serveur, qui sera exécutée par l'un des tests.

Il est préférable d'utiliser un super-utilisateur (commandes de
création et suppression de table dans le schéma z_plume,
l'extension est désinstallée et réinstallée, etc.).

"""

import unittest, psycopg2

from plume.rdf.utils import data_from_file, abspath
from plume.pg.template import TemplateDict, search_template
from plume.pg.description import PgDescription
from plume.pg.tests.connection import ConnectionString
from plume.pg.queries import query_list_templates, query_get_categories, \
     query_template_tabs

connection_string = ConnectionString()

class TemplateTestCase(unittest.TestCase):

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
                    "snum:isExternal": True,
                    "dcat:keyword": "IGN"
                }
            ], 20)
        template3 = (
            'template 3',
            False,
            [
                {
                    "snum:isExternal": True,
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
        """Sélection automatisée du modèle à utiliser parmi les modèles pré-configuré.

        Ce test charge les modèles pré-configurés sur
        le serveur PostgreSQL, en importe la liste, et
        les supprime.
        
        """
        pg_description_1 = PgDescription(data_from_file(abspath('pg/tests/samples/pg_description_1.txt')))
        pg_description_2 = PgDescription(data_from_file(abspath('pg/tests/samples/pg_description_2.txt')))
        conn = psycopg2.connect(connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM z_plume.meta_import_sample_template()')
                cur.execute(
                    query_list_templates(),
                    ('s_schema', 'table')
                    )
                templates_a = cur.fetchall()
                cur.execute(
                    query_list_templates(),
                    ('r_admin_express', 'departement_2154')
                    )
                templates_b = cur.fetchall()
                cur.execute(
                    query_list_templates(),
                    ('c_amgt_urb_zon_amgt', 'l_zac_075')
                    )
                templates_c = cur.fetchall()
                cur.execute('DELETE FROM z_plume.meta_template')
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
            'Classique'
            )

    def test_templatedict_sample_templates(self):
        """Génération des modèles pré-configurés.

        Le test utilise le modèle pré-configuré
        "Classique", qui est importé puis
        supprimé de la table des modèles au cours
        de l'exécution (de même que les autres
        modèles pré-configurés).
        
        """
        conn = psycopg2.connect(connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM z_plume.meta_import_sample_template()')
                cur.execute(
                    query_get_categories(),
                    ('Classique',)
                    )
                categories = cur.fetchall()
                cur.execute(
                    query_template_tabs(),
                    ('Template test',)
                    )
                tabs = cur.fetchall()
                cur.execute('DELETE FROM z_plume.meta_template')
        conn.close()
        template = TemplateDict(categories, tabs)
        self.assertEqual(len(template.shared), 38)
        self.assertEqual(template.local, {})
        d = {k: False for k in template.shared['dct:title'].keys()}
        for prop_dict in template.shared.values():
            for k, v in prop_dict.items():
                if v and k in d:
                    del d[k]
                if not d:
                    break
        self.assertEqual(d, {'is_read_only': False, 'tab': False})
                
        
        
        

unittest.main()
