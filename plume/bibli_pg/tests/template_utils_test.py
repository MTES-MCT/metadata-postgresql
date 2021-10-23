"""
Recette de template_utils et pg_queries.

Les tests nécessite une connexion PostgreSQL (définie par
input) pointant sur une base où :
- l'extension metadata est installée ;
- le schéma z_metadata_recette existe et contient les fonctions
de la recette côté serveur, qui sera exécutée par l'un des tests.

Il est préférable d'utiliser un super-utilisateur (commandes de
création et suppression de table dans le schéma z_metadata,
l'extension est désinstallée et réinstallée, etc.).

"""

import re, uuid, unittest, json, psycopg2
from pathlib import Path
from rdflib import Graph, URIRef
from rdflib.compare import isomorphic

from plume.bibli_pg import template_utils, pg_queries
from plume.bibli_rdf import __path__
from plume.bibli_rdf.rdf_utils import build_dict, load_vocabulary, \
     load_shape, metagraph_from_pg_description, WidgetsDict, \
     update_pg_description
from plume.bibli_rdf.tests.rdf_utils_debug import search_keys

# connexion à utiliser pour les tests
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

        # import d'un autre exemple de fiche de métadonnée
        with Path(__path__[0] + r'\exemples\exemple_commentaire_pg_2.txt').open(encoding='UTF-8') as src:
            self.metagraph_2 = metagraph_from_pg_description(src.read(), self.shape)
            
        # fiche de métadonnées vide
        self.metagraph_empty = metagraph_from_pg_description("", self.shape)
        
        # quelques pseudo-modèles avec conditions d'emploi
        self.template1 = (
            'template 1',
            True, None, 10
            )
        self.template2 = (
            'template 2',
            False,
            {
                "ensemble de conditions 1": {
                    "snum:isExternal": True,
                    "dcat:keyword": "IGN"
                }
            }, 20)
        self.template3 = (
            'template 3',
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


    ### EXECUTION de la recette PostgreSQL
    ### ----------------------------------
    
    def test_pg_tests(self):
        conn = psycopg2.connect(connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    DROP EXTENSION METADATA ;
                    CREATE EXTENSION METADATA ;
                    SELECT * FROM z_metadata_recette.execute_recette() ;
                    """)
                errors = cur.fetchall()     
        conn.close()  
        self.assertEqual(errors, [])


    ### FONCTION query_get_relation_kind
    ### --------------------------------
    
    def test_query_get_relation_kind_1(self):
        conn = psycopg2.connect(connection_string)
        
        with conn:
            with conn.cursor() as cur:

                cur.execute(
                    pg_queries.query_get_relation_kind(
                        'z_metadata', 'meta_local_categorie'
                        )
                    )
                kind_r = cur.fetchone()
                cur.execute(
                    pg_queries.query_get_relation_kind(
                        'z_metadata', 'meta_categorie'
                        )
                    )
                kind_p = cur.fetchone()
                cur.execute(
                    pg_queries.query_get_relation_kind(
                        'z_metadata', 'meta_template_categories_full'
                        )
                    )
                kind_v = cur.fetchone()
                cur.execute("""CREATE MATERIALIZED VIEW z_metadata.m_test AS (
                    SELECT * FROM z_metadata.meta_categorie)""")
                cur.execute(
                    pg_queries.query_get_relation_kind(
                        'z_metadata', 'm_test'
                        )
                    )
                kind_m = cur.fetchone()
                cur.execute('DROP MATERIALIZED VIEW z_metadata.m_test')

                cur.execute("""
                    CREATE EXTENSION IF NOT EXISTS postgres_fdw ;

                    CREATE SERVER serveur_bidon
                        FOREIGN DATA WRAPPER postgres_fdw
                        OPTIONS (host 'localhost', port '5432', dbname 'base_bidon') ;
    
                    CREATE FOREIGN TABLE z_metadata.f_test (
                        id integer NOT NULL,
                        data text
                        )
                        SERVER serveur_bidon
                        OPTIONS (schema_name 'schema_bidon', table_name 'table_bidon') ;
                    """)
                cur.execute(
                    pg_queries.query_get_relation_kind(
                        'z_metadata', 'f_test'
                        )
                    )
                kind_f = cur.fetchone()
                cur.execute("""
                    DROP FOREIGN TABLE z_metadata.f_test ;
                    DROP SERVER serveur_bidon ;
                    """)

        conn.close()
        
        self.assertEqual(kind_r[0], 'r')
        self.assertEqual(kind_v[0], 'v')
        self.assertEqual(kind_m[0], 'm')
        self.assertEqual(kind_p[0], 'p')
        self.assertEqual(kind_f[0], 'f')


    ### FONCTION query_update_columns_comments
    ### --------------------------------------
    
    def test_query_update_columns_comments_1(self):
        conn = psycopg2.connect(connection_string)
        
        with conn:
            with conn.cursor() as cur:

                # création d'une table de test
                cur.execute('''
                    CREATE TABLE z_metadata.table_test (
                        champ1 int, "champ 2" int, "Champ3" int
                        )
                    ''')

                columns = [
                    ("champ1", "description champ 1"),
                    ("champ 2", "description champ 2"),
                    ("Champ3", "description champ 3")
                    ]                

                d = build_dict(
                    metagraph=self.metagraph_empty,
                    shape=self.shape,
                    vocabulary=self.vocabulary,
                    columns=columns
                    )
                query = pg_queries.query_update_columns_comments(
                    'z_metadata', 'table_test', d
                    )
                cur.execute(query)
                cur.execute("""
                    SELECT
                        col_description('z_metadata.table_test'::regclass, 1),
                        col_description('z_metadata.table_test'::regclass, 2),
                        col_description('z_metadata.table_test'::regclass, 3)
                    """)
                descr = cur.fetchone()
                
                cur.execute('DROP TABLE z_metadata.table_test')
                # suppression de la table de test
        
        conn.close()
        
        self.assertEqual(descr[0], 'description champ 1')
        self.assertEqual(descr[1], 'description champ 2')
        self.assertEqual(descr[2], 'description champ 3')

    def test_query_update_columns_comments_2(self):
        columns = []                
        d = build_dict(
            metagraph=self.metagraph_empty,
            shape=self.shape,
            vocabulary=self.vocabulary,
            columns=columns
            )
        query = pg_queries.query_update_columns_comments(
            'z_metadata', 'table_test', d
            )
        self.assertIsNone(query)


    ### FONCTION query_update_column_comment
    ### ------------------------------------
    
    def test_query_update_column_comment_1(self):
        conn = psycopg2.connect(connection_string)
        
        with conn:
            with conn.cursor() as cur:
            
                cur.execute('CREATE TABLE z_metadata.table_test (num int)')
                # création d'une table de test
                
                query = pg_queries.query_update_column_comment(
                    'z_metadata', 'table_test', 'num'
                    )
                cur.execute(
                    query,
                    ('Nouvelle description',)
                    )
                cur.execute(
                    "SELECT col_description('z_metadata.table_test'::regclass, 1)"
                    )
                descr = cur.fetchone()
                
                cur.execute('DROP TABLE z_metadata.table_test')
                # suppression de la table de test
        
        conn.close()
        
        self.assertEqual(descr[0], 'Nouvelle description')


    ### FONCTION query_get_columns
    ### --------------------------
    
    def test_query_get_columns_1(self):
        conn = psycopg2.connect(connection_string)  
        with conn:
            with conn.cursor() as cur:
            
                cur.execute(
                    pg_queries.query_get_columns(
                        'z_metadata',
                        'meta_categorie'
                        )
                    )
                columns = cur.fetchall()
        conn.close()
        self.assertEqual(columns[0][0], 'path')
        self.assertTrue('SPARQL' in columns[0][1])

    # cas d'une table sans champ
    def test_query_get_columns_2(self):
        conn = psycopg2.connect(connection_string)  
        with conn:
            with conn.cursor() as cur:

                cur.execute('CREATE TABLE z_metadata.table_test ()')
                # création d'une table de test
            
                cur.execute(
                    pg_queries.query_get_columns(
                        'z_metadata',
                        'table_test'
                        )
                    )
                columns = cur.fetchall()

                cur.execute('DROP TABLE z_metadata.table_test')
                # suppression de la table de test
                
        conn.close()
        self.assertEqual(columns, [])
    

    ### FONCTION query_template_tabs
    ### ----------------------------
    
    def test_query_template_tabs_1(self):
        conn = psycopg2.connect(connection_string)
        
        with conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM z_metadata.meta_import_sample_template()')
                # import des modèles pré-configurés
                cur.execute("""
                    INSERT INTO z_metadata.meta_tab (tab_name, tab_num)
                        VALUES ('O1', NULL), ('O2', 10), ('O3', 15), ('O4', 12) ;
                    UPDATE z_metadata.meta_template_categories
                        SET tab_name = 'O1'
                        WHERE shrcat_path = 'dct:title' AND tpl_label = 'Basique' ;
                    UPDATE z_metadata.meta_template_categories
                        SET tab_name = 'O2'
                        WHERE shrcat_path = 'dct:description' AND tpl_label = 'Basique' ;
                    UPDATE z_metadata.meta_template_categories
                        SET tab_name = 'O4'
                        WHERE shrcat_path = 'dct:temporal' AND tpl_label = 'Basique' ;
                    """)
        
                cur.execute(
                    pg_queries.query_template_tabs(),
                    ('Basique',)
                    )
                tabs = cur.fetchall()
                
                cur.execute('DROP EXTENSION metadata ; CREATE EXTENSION metadata')
                # suppression des modèles pré-configurés
        
        conn.close()
        
        self.assertEqual([x[0] for x in tabs], ['O2', 'O4', 'O1'])

    def test_query_template_tabs_2(self):
        conn = psycopg2.connect(connection_string)
        
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO z_metadata.meta_tab (tab_name, tab_num)
                        VALUES ('O1', NULL), ('O2', 10), ('O3', 15), ('O4', 12) ;
                    INSERT INTO z_metadata.meta_categorie
                        (path, origin, cat_label) VALUES
                        ('uuid:218c1245-6ba7-4163-841e-476e0d5582af',
                            'local', 'Local valide'),
                        ('dct:title', 'shared', 'Commun valide'),
                        ('dcat:distribution / dct:issued', 'shared', 'Commun composé')
                        ;
                    INSERT INTO z_metadata.meta_template (tpl_label)
                        VALUES ('Template test') ;
                    INSERT INTO z_metadata.meta_template_categories
                        (tab_name, shrcat_path, loccat_path, tpl_label) VALUES
                        ('O1', 'dct:title', NULL, 'Template test'),
                        ('O2', NULL, 'uuid:218c1245-6ba7-4163-841e-476e0d5582af',
                            'Template test'),
                        ('O4', 'dcat:distribution / dct:issued', NULL, 'Template test') ;
                    """)
        
                cur.execute(
                    pg_queries.query_template_tabs(),
                    ('Template test',)
                    )
                tabs = cur.fetchall()
                
                cur.execute('DROP EXTENSION metadata ; CREATE EXTENSION metadata')
                # suppression des modèles pré-configurés
        
        conn.close()
        
        self.assertEqual([x[0] for x in tabs], ['O2', 'O1'])


    ### FONCTION build_template_tabs
    ### ----------------------------
    
    def test_build_template_tabs_1(self):
        tabs = [('O2',), ('O4',), ('O1',)]
        self.assertEqual(
            template_utils.build_template_tabs(tabs),
            { 'O2': (0,), 'O4': (1,), 'O1': (2,) }
            )

    # modèle sans onglets
    def test_build_template_tabs_2(self):
        conn = psycopg2.connect(connection_string)
        
        with conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM z_metadata.meta_import_sample_template()')
                # import des modèles pré-configurés
        
                cur.execute(
                    pg_queries.query_template_tabs(),
                    ('Basique',)
                    )
                tabs = cur.fetchall()
                
                cur.execute('DROP EXTENSION metadata ; CREATE EXTENSION metadata')
        
        conn.close()
        
        self.assertIsNone(template_utils.build_template_tabs(tabs))

    def test_build_template_tabs_3(self):
        conn = psycopg2.connect(connection_string)
        
        with conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM z_metadata.meta_import_sample_template()')
                # import des modèles pré-configurés
                cur.execute("""
                    INSERT INTO z_metadata.meta_tab (tab_name, tab_num)
                        VALUES ('O1', NULL), ('O2', 10), ('O3', 15), ('O4', 12) ;
                    UPDATE z_metadata.meta_template_categories
                        SET tab_name = 'O1'
                        WHERE shrcat_path = 'dct:title' AND tpl_label = 'Basique' ;
                    UPDATE z_metadata.meta_template_categories
                        SET tab_name = 'O2'
                        WHERE shrcat_path = 'dct:description' AND tpl_label = 'Basique' ;
                    UPDATE z_metadata.meta_template_categories
                        SET tab_name = 'O4'
                        WHERE shrcat_path = 'dct:temporal' AND tpl_label = 'Basique' ;
                    """)
        
                cur.execute(
                    pg_queries.query_template_tabs(),
                    ('Basique',)
                    )
                tabs = cur.fetchall()
                
                cur.execute('DROP EXTENSION metadata ; CREATE EXTENSION metadata')
        
        conn.close()
        
        self.assertEqual(
            template_utils.build_template_tabs(tabs),
            { 'O2': (0,), 'O4': (1,), 'O1': (2,) }
            )


    ### FONCTION query_is_relation_owner
    ### --------------------------------
    
    def test_query_is_relation_owner_1(self):
        conn = psycopg2.connect(connection_string)
        
        with conn:
            with conn.cursor() as cur:
            
                cur.execute(
                    pg_queries.query_is_relation_owner(),
                    ('z_metadata', 'meta_categorie')
                    )
                res = cur.fetchone()
        
        conn.close()
        
        self.assertTrue(res[0])
    

    ### FONCTION query_exists_extension
    ### -------------------------------
    
    # l'extension metada est supposée être installée
    # sur la base de recette
    def test_query_query_exists_extension_1(self):
        conn = psycopg2.connect(connection_string)
        
        with conn:
            with conn.cursor() as cur:
            
                cur.execute(
                    pg_queries.query_exists_extension(),
                    ('metadata',)
                    )
                res = cur.fetchone()
        
        conn.close()
        
        self.assertTrue(res[0])

    
    ### FONCTION query_get_table_comment
    ### --------------------------------
    
    def test_query_get_table_comment_1(self):
        conn = psycopg2.connect(connection_string)
        
        with conn:
            with conn.cursor() as cur:
            
                cur.execute('CREATE TABLE z_metadata.table_test (num int)')
                cur.execute(
                    'COMMENT ON TABLE z_metadata.table_test IS %s',
                    ('Nouvelle description',)
                    )
                # création d'une table de test avec descriptif
                
                cur.execute(
                    pg_queries.query_get_table_comment(
                        'z_metadata', 'table_test'
                        )
                    )
                descr = cur.fetchone()
                
                cur.execute('DROP TABLE z_metadata.table_test')
                # suppression de la table de test
        
        conn.close()
        
        self.assertEqual(descr[0], 'Nouvelle description')
  

    ### FONCTION query_update_table_comment
    ### -----------------------------------
    
    def test_query_update_table_comment_1(self):
        conn = psycopg2.connect(connection_string)
        
        with conn:
            with conn.cursor() as cur:
            
                cur.execute('CREATE TABLE z_metadata.table_test (num int)')
                # création d'une table de test
                
                query = pg_queries.query_update_table_comment(
                    'z_metadata', 'table_test'
                    )
                cur.execute(
                    query,
                    ('Nouvelle description',)
                    )
                cur.execute(
                    "SELECT obj_description('z_metadata.table_test'::regclass, 'pg_class')"
                    )
                descr = cur.fetchone()
                
                cur.execute('DROP TABLE z_metadata.table_test')
                # suppression de la table de test
        
        conn.close()
        
        self.assertEqual(descr[0], 'Nouvelle description')

    # prise en charge de tous les types de relations pertinents
    def test_query_update_table_comment_2(self):
        conn = psycopg2.connect(connection_string)
        
        with conn:
            with conn.cursor() as cur:

                cur.execute("""
                    CREATE TABLE z_metadata.r_test (num int) ;
                    
                    CREATE VIEW z_metadata.v_test AS (
                        SELECT * FROM z_metadata.meta_categorie
                        ) ;
                        
                    CREATE MATERIALIZED VIEW z_metadata.m_test AS (
                        SELECT * FROM z_metadata.meta_categorie
                        ) ;

                    CREATE TABLE z_metadata.p_test (id int, cle text)
                        PARTITION BY LIST (cle) ;
                        
                    CREATE EXTENSION IF NOT EXISTS postgres_fdw ;

                    CREATE SERVER serveur_bidon
                        FOREIGN DATA WRAPPER postgres_fdw
                        OPTIONS (host 'localhost', port '5432', dbname 'base_bidon') ;
    
                    CREATE FOREIGN TABLE z_metadata.f_test (
                        id integer NOT NULL,
                        data text
                        )
                        SERVER serveur_bidon
                        OPTIONS (schema_name 'schema_bidon', table_name 'table_bidon') ;
                    """)
                res = {'r_test': None, 'v_test': None, 'm_test': None,
                       'p_test': None, 'f_test': None}
                for k in res.keys():
                    cur.execute(
                        pg_queries.query_get_relation_kind(
                            'z_metadata', k
                            )
                        )
                    kind = cur.fetchone()[0]
                    query = pg_queries.query_update_table_comment(
                        'z_metadata', k, relation_kind=kind
                        )
                    cur.execute(
                        query,
                        ('Nouvelle description',)
                        )
                    cur.execute(
                        pg_queries.query_get_table_comment(
                            'z_metadata', k
                            )
                        )
                    res[k] = cur.fetchone()[0]
                
                cur.execute("""
                    DROP TABLE z_metadata.r_test ;
                    DROP VIEW z_metadata.v_test ;
                    DROP MATERIALIZED VIEW z_metadata.m_test ;
                    DROP TABLE z_metadata.p_test ;
                    DROP FOREIGN TABLE z_metadata.f_test ;
                    DROP SERVER serveur_bidon ;
                    """)

        conn.close()

        for k, v in res.items():
            with self.subTest(objet=k):
                self.assertEqual(v, 'Nouvelle description')


    ### FONCTION query_list_templates
    ### -----------------------------
    
    def test_query_list_templates_1(self):
        conn = psycopg2.connect(connection_string)
        
        with conn:
            with conn.cursor() as cur:
            
                cur.execute('SELECT * FROM z_metadata.meta_import_sample_template()')
                # import des modèles pré-configurés
                
                cur.execute(
                    pg_queries.query_list_templates(),
                    ('r_schema', 'table')
                    )
                templates = cur.fetchall()
                
                cur.execute('DELETE FROM z_metadata.meta_template')
                # suppression des modèles pré-configurés
        
        conn.close()
        
        self.assertEqual(len(templates), 3)


    ### FONCTION query_get_categories
    ### -----------------------------
    
    def test_query_get_categories_1(self):
        conn = psycopg2.connect(connection_string)
        
        with conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM z_metadata.meta_import_sample_template()')
                # import des modèles pré-configurés
        
                cur.execute(
                    pg_queries.query_get_categories(),
                    ('Basique',)
                    )
                categories = cur.fetchall()
                
                cur.execute('DELETE FROM z_metadata.meta_template')
                # suppression des modèles pré-configurés
        
        conn.close()
        
        self.assertTrue(len(categories) > 2)
    

    ### FONCTION search_template
    ### ------------------------

    # graphe vide, sélection sur les préfixes et suffixes
    def test_search_template_1(self):
        self.assertEqual(
            template_utils.search_template(
                self.metagraph_empty,
                [self.template1]
                ),
            'template 1'
            )
        self.assertEqual(
            template_utils.search_template(
                self.metagraph_empty,
                [self.template1, self.template2, self.template3]
                ),
            'template 1'
            )
        self.assertEqual(
            template_utils.search_template(
                self.metagraph_empty,
                [self.template2, self.template3, self.template1]
                ),
            'template 1'
            )
        self.assertEqual(
            template_utils.search_template(
                self.metagraph,
                [self.template1, self.template2, self.template3]
                ),
            'template 2'
            )
        self.assertEqual(
            template_utils.search_template(
                self.metagraph,
                [self.template1, self.template3]
                ),
            'template 3'
            )
        self.assertEqual(
            template_utils.search_template(
                self.metagraph,
                [self.template3]
                ),
            'template 3'
            )


    ### FONCTION build_template
    ### -----------------------
    
    def test_build_template_1(self):
        categories = [
            ('shared', 'dct:title', 'libellé', 'QLineEdit', None, None, None,
                None, None, True, True, 0, True, False, 'rdf:langString', None),
            ('shared', 'dct:description', 'description', 'QTextEdit', 99, None,
                None, None, None, False, False, 50, False, False, 'rdf:langString', None),
            ('shared', 'dct:modified', 'dernière modification', 'QLineEdit', None,
                None, '2021-09-01', None, None, False, False, 90, False, False,
                'xsd:string', None),
            ('local', 'uuid:218c1245-6ba7-4163-841e-476e0d5582af', 'code ADL',
                None, 30, 'code maison', None, '230-FG', '000-XX', True, False, 8,
                False, False, None, None),
            ('local', 'uuid:218c1245-6ba7-4163-841e-476e0d5582ag', 'ma date',
                'QDateEdit', None, None, None, None, None, None, None, None, None,
                False, 'xsd:date', None)
            ]
        template = template_utils.build_template(categories)
        d = build_dict(Graph(), self.shape, self.vocabulary, template)
        self.assertEqual(len(d), 10)
        # racine + title + description + modified + groupe de valeur
        # pour code ADL + code ADL + bouton plus de code ADL + ma date
        # + identifiant + onglet "Autres" pour l'identifiant = 10
        
        ttk = search_keys(d, 'dct:title', 'edit')[0]
        self.assertIsNotNone(ttk)
        dsk = search_keys(d, 'dct:description', 'edit')[0]
        self.assertIsNotNone(dsk)
        mdk = search_keys(d, 'dct:modified', 'edit')[0]
        self.assertIsNotNone(mdk)
        lck = search_keys(
             d,
             'uuid:218c1245-6ba7-4163-841e-476e0d5582af',
             'edit'
             )[0]
        self.assertIsNotNone(lck)
        lck_g = search_keys(
             d,
             'uuid:218c1245-6ba7-4163-841e-476e0d5582af',
             'group of values'
             )[0]
        self.assertIsNotNone(lck_g)
        lck_b = search_keys(
             d,
             'uuid:218c1245-6ba7-4163-841e-476e0d5582af',
             'plus button'
             )[0]
        self.assertIsNotNone(lck_b)
        lck2 = search_keys(
             d,
             'uuid:218c1245-6ba7-4163-841e-476e0d5582ag',
             'edit'
             )[0]
        self.assertIsNotNone(lck2)
        
        self.assertEqual(d[ttk]['row'], 0)
        self.assertEqual(d[lck_g]['row'], 1)
        self.assertEqual(d[dsk]['label row'], 2)
        self.assertEqual(d[dsk]['row'], 3)
        self.assertEqual(d[mdk]['row'], 102)
        # 3 + un row span de 99 -> 102
        self.assertEqual(d[lck2]['row'], 103)
        
        self.assertTrue(d[ttk]['read only'])
        self.assertFalse(d[ttk]['multiple values'])
        # ne peut pas être redéfinie pour des métadonnées communes
        self.assertEqual(d[dsk]['row span'], 99)
        self.assertTrue(d[dsk]['is mandatory'])
        # vérifie que build_dict ne permet pas de rendre optionnelles les
        # rares catégories communes obligatoires
        self.assertEqual(d[mdk]['main widget type'], 'QLineEdit')
        self.assertTrue(d[mdk]['default value'] == d[mdk]['value'] == '2021-09-01')
        # vérifie aussi que la valeur par défaut est bien reprise par build_dict
        # dans le cas d'un formulaire vide
        self.assertEqual(
            d[mdk]['data type'],
            URIRef('http://www.w3.org/2001/XMLSchema#date')
            )
        # vérifie que les modification sur data type sont ignorées
        # pour les catégories communes
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
        self.assertEqual(
            d[lck]['data type'],
            URIRef('http://www.w3.org/2001/XMLSchema#string')
            )
        # vérifie que string est appliqué si aucun type n'est
        # spécifié
        self.assertEqual(
            d[lck2]['data type'],
            URIRef('http://www.w3.org/2001/XMLSchema#date')
            )
        self.assertEqual(d[lck2]['main widget type'], 'QDateEdit')

    # ajout automatique des ancêtres manquants
    def test_build_template_2(self):
        categories = [
            ('shared', 'dcat:distribution /dct:license/ rdfs:label',
                None, None, None, None, None, None, None, None, None,
                None, None, False, None, None)
            ]
        template = template_utils.build_template(categories)
        self.assertTrue('dcat:distribution' in template)
        self.assertTrue('dcat:distribution / dct:license' in template)
        self.assertTrue('dcat:distribution / dct:license / rdfs:label' in template)
        self.assertEqual(len(template), 3)

    # suppression automatique des branches présumées vides
    def test_build_template_3(self):
        categories = [
            ('shared', 'dcat:distribution /dct:license',
                None, None, None, None, None, None, None, None,
                None, None, None, True, None, None)
            ]
        template = template_utils.build_template(categories)
        self.assertFalse('dcat:distribution' in template)
        self.assertFalse('dcat:distribution / dct:license' in template)
        self.assertEqual(len(template), 0)


    ### DIVERS
    ### ------

    # encodage des retours à la ligne
    def test_divers_1(self):
        d = build_dict(self.metagraph_2, self.shape, self.vocabulary)
        k = search_keys(d, 'dct:description', 'edit')
        d.update_value(k[0], """La table L_ZAC_S_075 recense les zones d’aménagement concerté de la Ville de Paris depuis 2004. La table est mise à jour selon l’actualité. Y sont consignées :
- les ZAC en cours ;
- les ZAC projetées, à court ou moyen terme par la collectivité, dont le dossier de création n’a pas encore été approuvé mais sur lesquelles une procédure de concertation a été lancée ;
- les anciennes ZAC, supprimées depuis 2004.""")
        new_metagraph = d.build_graph(self.vocabulary)
        new_pg_description = update_pg_description(""""
            Description +
            <METADATA> Truc à remplacer
            </METADATA>
            """, new_metagraph)
        
        conn = psycopg2.connect(connection_string)
        
        with conn:
            with conn.cursor() as cur:
            
                cur.execute('CREATE TABLE z_metadata.table_test (num int)')
                # création d'une table de test
                
                query = pg_queries.query_update_table_comment(
                    'z_metadata', 'table_test'
                    )
                cur.execute(
                    query,
                    (new_pg_description,)
                    )
                cur.execute(
                    pg_queries.query_get_table_comment(
                        'z_metadata', 'table_test'
                        )
                    )
                descr = cur.fetchone()
                
                cur.execute('DROP TABLE z_metadata.table_test')
                # suppression de la table de test
        
        conn.close()

        gt = metagraph_from_pg_description(descr[0], self.shape)
        
        self.assertTrue(isomorphic(new_metagraph, gt))


unittest.main()

