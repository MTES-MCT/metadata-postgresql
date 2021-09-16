"""
Recette de template_utils et pg_queries.
"""

import re, uuid, unittest, json, psycopg2
from pathlib import Path
from rdflib import Graph

from metadata_postgresql.bibli_pg import template_utils
from metadata_postgresql.bibli_rdf import __path__
from metadata_postgresql.bibli_rdf.rdf_utils import build_dict, load_vocabulary, load_shape, metagraph_from_pg_description
from metadata_postgresql.bibli_rdf.tests.rdf_utils_debug import search_keys

# connexion à utiliser pour les tests
# -> l'extension metadata doit être installée sur la base
# -> il est préférable d'utiliser un super-utilisateur (commandes de
# création et suppression de table dans le schéma z_metadata)
connection_string = "host={} port={} dbname={} user={} password={}".format(
    input('host (localhost): ') or 'localhost',
    input('port (5432): ') or '5432',
    input('dbname (metadata_dev): ') or 'metadata_dev',
    input('user (postgres): ') or 'postgres',
    input('password : ')
    )

class TestTemplateUtils(unittest.TestCase):

    def setUp(self):
        self.shape = load_shape()
        self.vocabulary = load_vocabulary()
        
        # import d'un exemple de fiche de métadonnée
        with Path(__path__[0] + r'\exemples\exemple_commentaire_pg.txt').open(encoding='UTF-8') as src:
            self.metagraph = metagraph_from_pg_description(src.read(), self.shape)
            
        # fiche de métadonnées vide
        self.metagraph_empty = metagraph_from_pg_description("", self.shape)
        
        # quelques pseudo-modèles avec conditions d'emploi
        self.template1 = (
            0, 'template 1',
            True, None, 10
            )
        self.template2 = (
            1, 'template 2',
            False,
            {
                "ensemble de conditions 1": {
                    "snum:isExternal": True,
                    "dcat:keyword": "IGN"
                }
            }, 20)
        self.template3 = (
            2, 'template 3',
            False,
            {
                "ensemble de conditions 1": {
                    "snum:isExternal": True,
                    "dcat:keyword": "IGN-F"
                },
                "ensemble de conditions 2": {
                    "dct:publisher / foaf:name": "Institut national de l'information géographique et forestière (IGN-F)"
                }
            }, 15)
        

    ### FONCTION query_update_table_comment
    ### -----------------------------------
    
    def test_query_update_table_comment_1(self):
        conn = psycopg2.connect(connection_string)
        
        with conn:
            with conn.cursor() as cur:
            
                cur.execute('CREATE TABLE z_metadata.table_test (num int)')
                # création d'une table de test
                
                query = query_update_table_comment('z_metadata', 'table_test')
                cur.execute(query, ('Nouvelle description',))
                cur.execute("SELECT obj_description('z_metadata.table_test'::regclass, 'pg_class')")
                descr = cur.fetchone()
                
                cur.execute('DROP TABLE z_metadata.table_test')
                # suppression de la table de test
        
        conn.close()
        
        self.assertEqual(descr[0], 'Nouvelle description')


    ### FONCTION query_list_templates
    ### -----------------------------
    
    def test_query_list_templates_1(self):
        conn = psycopg2.connect(connection_string)
        
        with conn:
            with conn.cursor() as cur:
            
                cur.execute('SELECT * FROM z_metadata.meta_import_sample_template()')
                # import des modèles pré-configurés
                
                cur.execute(query_list_templates(), ('r_schema', 'table'))
                templates = cur.fetchall()
                
                cur.execute('DELETE FROM z_metadata.meta_template')
                # suppression des modèles pré-configurés
        
        conn.close()
        
        self.assertEqual(len(templates), 2)


    ### FONCTION query_get_categories
    ### -----------------------------
    
    def test_query_get_categories_1(self):
        conn = psycopg2.connect(connection_string)
        
        with conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM z_metadata.meta_import_sample_template()')
                # import des modèles pré-configurés
        
                cur.execute(query_get_categories(), ('Basique',))
                categories = cur.fetchall()
                
                cur.execute('DELETE FROM z_metadata.meta_template')
                # suppression des modèles pré-configurés
        
        conn.close()
        
        self.assertTrue(len(categories) > 2)
    

    ### FONCTION build_template
    ### -----------------------

    # graphe vide, sélection sur les préfixes et suffixes
    def test_search_template_1(self):
        self.assertEqual(
            template_utils.search_template(
                'schema',
                'table',
                self.metagraph_empty,
                [self.template1]
                ),
            'template 1'
            )
        self.assertEqual(
            template_utils.search_template(
                'schema',
                'table',
                self.metagraph_empty,
                [self.template1, self.template2, self.template3]
                ),
            'template 1'
            )
        self.assertEqual(
            template_utils.search_template(
                'schema',
                'table',
                self.metagraph_empty,
                [self.template2, self.template3, self.template1]
                ),
            'template 1'
            )
        self.assertEqual(
            template_utils.search_template(
                'schema',
                'table',
                self.metagraph,
                [self.template1, self.template2, self.template3]
                ),
            'template 2'
            )
        self.assertEqual(
            template_utils.search_template(
                'schema',
                'table',
                self.metagraph,
                [self.template1, self.template3]
                ),
            'template 3'
            )
        self.assertEqual(
            template_utils.search_template(
                'schema',
                'table',
                self.metagraph,
                [self.template3]
                ),
            'template 3'
            )


    ### FONCTION build_template
    ### -----------------------
    
    def test_build_template_1(self):
        categories = [
            (0, 'dct:title', 'libellé', 'QLineEdit', None, None, None, None, None, True, True, 0, True),
            (1, 'dct:description', 'description', 'QTextEdit', 99, None, None, None, None, False, False, 50, False),
            (2, 'dct:modified', 'dernière modification', 'QDateEdit', None, None, '2021-09-01', None, None, False, False, 90, False),
            (3, '<urn:uuid:218c1245-6ba7-4163-841e-476e0d5582af>', 'code ADL', None, 30, 'code maison', None, '230-FG', '000-XX', True, False, 8, False)
            ]
        template = template_utils.build_template(categories)
        d = build_dict(Graph(), self.shape, self.vocabulary, template)
        self.assertEqual(len(d), 7)
        # racine + title + description + modified + groupe de valeur
        # pour code ADL + code ADL + bouton plus de code ADL = 7
        
        ttk = search_keys(d, 'dct:title', 'edit')[0]
        self.assertIsNotNone(ttk)
        dsk = search_keys(d, 'dct:description', 'edit')[0]
        self.assertIsNotNone(dsk)
        mdk = search_keys(d, 'dct:modified', 'edit')[0]
        self.assertIsNotNone(mdk)
        lck = search_keys(
             d,
             '<urn:uuid:218c1245-6ba7-4163-841e-476e0d5582af>',
             'edit'
             )[0]
        self.assertIsNotNone(lck)
        lck_g = search_keys(
             d,
             '<urn:uuid:218c1245-6ba7-4163-841e-476e0d5582af>',
             'group of values'
             )[0]
        self.assertIsNotNone(lck_g)
        lck_b = search_keys(
             d,
             '<urn:uuid:218c1245-6ba7-4163-841e-476e0d5582af>',
             'plus button'
             )[0]
        self.assertIsNotNone(lck_b)
        
        self.assertEqual(d[ttk]['row'], 0)
        self.assertEqual(d[lck_g]['row'], 1)
        self.assertEqual(d[dsk]['label row'], 2)
        self.assertEqual(d[dsk]['row'], 3)
        self.assertEqual(d[mdk]['row'], 102)
        # 3 + un row span de 99 -> 102
        
        self.assertTrue(d[ttk]['read only'])
        self.assertFalse(d[ttk]['multiple values'])
        # ne peut pas être redéfinie pour des métadonnées communes
        self.assertEqual(d[dsk]['row span'], 99)
        self.assertTrue(d[dsk]['is mandatory'])
        # vérifie que build_dict ne permet pas de rendre optionnelles les
        # rares catégories communes obligatoires
        self.assertEqual(d[mdk]['main widget type'], 'QDateEdit')
        self.assertTrue(d[mdk]['default value'] == d[mdk]['value'] == '2021-09-01')
        # vérifie aussi que la valeur par défaut est bien reprise par build_dict
        # dans le cas d'un formulaire vide
        self.assertEqual(d[lck]['main widget type'], 'QLineEdit')
        # vérifie que build_dict met bien des QLineEdit par défaut
        self.assertEqual(d[lck_g]['label'], 'code ADL')
        self.assertIsNone(d[lck]['row span'])
        # vérifie que build_dict ignore row_span si le widget n'est
        # pas un QTextEdit
        self.assertEqual(d[lck_g]['help text'], 'code maison')
        self.assertEqual(d[lck]['placeholder text'], '230-FG')
        self.assertEqual(d[lck]['input mask'], '000-XX')
        self.assertTrue(d[lck]['multiple values'])


unittest.main()

