"""Recette du module queries.

Les tests nécessitent une connexion PostgreSQL (paramètres à
saisir lors de l'exécution du test) pointant sur un serveur où
la dernière version de l'extension PlumePg est disponible. Elle
sera créée ou recréée sur la base de test, de même que les fonctions
servant à la recette côté serveur.

Il est préférable d'utiliser un super-utilisateur (commandes de
création et suppression de table dans le schéma z_plume,
l'extension est désinstallée et réinstallée, etc.).

"""

import unittest, psycopg2

from plume.pg.tests.connection import ConnectionString
from plume.pg.queries import query_is_relation_owner, query_exists_extension, \
    query_get_relation_kind, query_update_table_comment, query_get_table_comment, \
    query_list_templates, query_get_categories, query_template_tabs, \
    query_get_columns, query_update_column_comment, query_update_columns_comments, \
    query_get_geom_extent, query_get_geom_srid, query_get_srid_list,\
    query_get_geom_centroid, query_evaluate_local_templates, query_plume_pg_check, \
    query_get_comment_fragments
from plume.pg.template import LocalTemplatesCollection
from plume.rdf.widgetsdict import WidgetsDict
from plume.rdf.utils import data_from_file, abspath

class PlumePgTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Préparation de la connexion PG + recréation de l'extension et des tests sur le serveur.
        
        """
        cls.connection_string = ConnectionString()
        create_tests = data_from_file(abspath('').parents[0] /
            'postgresql/tests/plume_pg_test.sql')
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute(create_tests)
                cur.execute("""
                    DROP EXTENSION IF EXISTS plume_pg ;
                    CREATE EXTENSION plume_pg ;
                    """)  
        conn.close()
    
    def test_plume_pg_tests(self):
        """Exécution de la recette de l'extension PostgreSQL PlumePg.

        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT * FROM z_plume_recette.execute_recette() ;
                    """)
                errors = cur.fetchall()     
        conn.close()  
        self.assertEqual(errors, [])

class QueriesTestCase(unittest.TestCase):

    def test_query_is_relation_owner(self):
        """Requête qui détermine si l'utilisateur est propriétaire de l'objet PG considéré.

        Partant du principe que la présente recette
        est exécutée avec un compte super-utilisateur,
        le présent test se borne à vérifier que ce
        super-utilisateur est membre du rôle propriétaire
        d'une des tables de l'extension PlumePg, ce qui
        ne peut qu'être le cas.
        
        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    query_is_relation_owner(),
                    ('z_plume', 'meta_categorie')
                    )
                res = cur.fetchone()
        conn.close()
        self.assertTrue(res[0])

    def test_query_query_exists_extension(self):
        """Requête qui vérifie que l'extension PlumePg est installée sur la base.

        Il est présumé que c'est le cas sur la base
        utilisée pour la recette.
        
        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    query_exists_extension(),
                    ('plume_pg',)
                    )
                res = cur.fetchone()
        conn.close()
        self.assertTrue(res[0])

    def test_query_get_relation_kind(self):
        """Requête qui identifie la nature de la relation considérée.

        Le test utilise autant que possible les
        objets de l'extension PlumePg, sinon crée
        puis détruit les relations.
        
        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    query_get_relation_kind(
                        'z_plume', 'meta_local_categorie'
                        )
                    )
                kind_r = cur.fetchone()
                cur.execute(
                    query_get_relation_kind(
                        'z_plume', 'meta_categorie'
                        )
                    )
                kind_p = cur.fetchone()
                cur.execute(
                    query_get_relation_kind(
                        'z_plume', 'meta_template_categories_full'
                        )
                    )
                kind_v = cur.fetchone()
                cur.execute("""CREATE MATERIALIZED VIEW z_plume.m_test AS (
                    SELECT * FROM z_plume.meta_categorie)""")
                cur.execute(
                    query_get_relation_kind(
                        'z_plume', 'm_test'
                        )
                    )
                kind_m = cur.fetchone()
                cur.execute('DROP MATERIALIZED VIEW z_plume.m_test')
                cur.execute("""
                    CREATE EXTENSION IF NOT EXISTS postgres_fdw ;

                    CREATE SERVER serveur_bidon
                        FOREIGN DATA WRAPPER postgres_fdw
                        OPTIONS (host 'localhost', port '5432', dbname 'base_bidon') ;
    
                    CREATE FOREIGN TABLE z_plume.f_test (
                        id integer NOT NULL,
                        data text
                        )
                        SERVER serveur_bidon
                        OPTIONS (schema_name 'schema_bidon', table_name 'table_bidon') ;
                    """)
                cur.execute(
                    query_get_relation_kind(
                        'z_plume', 'f_test'
                        )
                    )
                kind_f = cur.fetchone()
                cur.execute("""
                    DROP FOREIGN TABLE z_plume.f_test ;
                    DROP SERVER serveur_bidon ;
                    """)
        conn.close()
        self.assertEqual(kind_r[0], 'r')
        self.assertEqual(kind_v[0], 'v')
        self.assertEqual(kind_m[0], 'm')
        self.assertEqual(kind_p[0], 'p')
        self.assertEqual(kind_f[0], 'f')

    def test_query_get_table_comment(self):
        """Requête de récupération du descriptif d'une relation.

        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('CREATE TABLE z_plume.table_test (num int)')
                cur.execute(
                    'COMMENT ON TABLE z_plume.table_test IS %s',
                    ('Nouvelle description',)
                    )
                # création d'une table de test avec descriptif
                cur.execute(
                    query_get_table_comment(
                        'z_plume', 'table_test'
                        )
                    )
                descr = cur.fetchone()
                cur.execute('DROP TABLE z_plume.table_test')
                # suppression de la table de test
        conn.close()
        self.assertEqual(descr[0], 'Nouvelle description')

    def test_query_update_table_comment(self):
        """Requête de mise à jour du descriptif d'une relation.

        Le test vérifie que la mise à jour s'effectue
        correctement pour tous les types de relations
        pris en charge.
        
        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE z_plume.r_test (num int) ;
                    
                    CREATE VIEW z_plume.v_test AS (
                        SELECT * FROM z_plume.meta_categorie
                        ) ;
                        
                    CREATE MATERIALIZED VIEW z_plume.m_test AS (
                        SELECT * FROM z_plume.meta_categorie
                        ) ;

                    CREATE TABLE z_plume.p_test (id int, cle text)
                        PARTITION BY LIST (cle) ;
                        
                    CREATE EXTENSION IF NOT EXISTS postgres_fdw ;

                    CREATE SERVER serveur_bidon
                        FOREIGN DATA WRAPPER postgres_fdw
                        OPTIONS (host 'localhost', port '5432', dbname 'base_bidon') ;
    
                    CREATE FOREIGN TABLE z_plume.f_test (
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
                        query_get_relation_kind(
                            'z_plume', k
                            )
                        )
                    kind = cur.fetchone()[0]
                    query = query_update_table_comment(
                        'z_plume', k, relation_kind=kind
                        )
                    cur.execute(
                        query,
                        ('Nouvelle description',)
                        )
                    cur.execute(
                        query_get_table_comment(
                            'z_plume', k
                            )
                        )
                    res[k] = cur.fetchone()[0]
                cur.execute("""
                    DROP TABLE z_plume.r_test ;
                    DROP VIEW z_plume.v_test ;
                    DROP MATERIALIZED VIEW z_plume.m_test ;
                    DROP TABLE z_plume.p_test ;
                    DROP FOREIGN TABLE z_plume.f_test ;
                    DROP SERVER serveur_bidon ;
                    """)
        conn.close()
        for k, v in res.items():
            with self.subTest(objet=k):
                self.assertEqual(v, 'Nouvelle description')

    def test_query_list_templates(self):
        """Requête qui récupère la liste des modèles disponibles.

        Concrètement, le test récupère la
        liste des modèles pré-configurés, qui
        sont importés puis supprimés de la table
        des modèles au cours de l'exécution.
        
        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM z_plume.meta_import_sample_template()')
                # import des modèles pré-configurés
                cur.execute(
                    query_list_templates(),
                    ('r_schema', 'table')
                    )
                templates = cur.fetchall()
                cur.execute('DELETE FROM z_plume.meta_template')
                # suppression des modèles pré-configurés
        conn.close()
        self.assertEqual(len(templates), 3)

    def test_query_evaluate_local_templates(self):
        """Requête qui exécute côté serveur les conditions d'application des modèles locaux.
        
        L'extension PlumePg est désinstallée pendant la durée
        du test.
        
        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        templates_collection = LocalTemplatesCollection()
        with conn:
            with conn.cursor() as cur:
                cur.execute('DROP EXTENSION plume_pg')
                cur.execute(
                    *query_evaluate_local_templates(templates_collection, 'r_schema', 'table')
                    )
                templates = cur.fetchall()
                cur.execute('CREATE EXTENSION plume_pg')
        conn.close()
        self.assertEqual(len(templates), 3)

    def test_query_get_categories(self):
        """Requête de récupération des informations associées à un modèle.

        Le test utilise le modèle pré-configuré
        "Basique", qui est importé puis
        supprimé de la table des modèles au cours
        de l'exécution (de même que les autres
        modèles pré-configurés).

        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM z_plume.meta_import_sample_template()')
                # import des modèles pré-configurés
                cur.execute(
                    query_get_categories(),
                    ('Basique',)
                    )
                categories = cur.fetchall()
                cur.execute('DELETE FROM z_plume.meta_template')
                # suppression des modèles pré-configurés
        conn.close()
        self.assertTrue(len(categories) > 2)

    def test_query_template_tabs_1(self):
        """Requête d'import des onglets associés à un modèle.

        Le test utilise le modèle pré-configuré
        "Basique", qui est importé puis
        supprimé de la table des modèles au cours
        de l'exécution (de même que les autres
        modèles pré-configurés). "Basique" n'a
        pas d'onglets, mais le test lui en ajoute
        artificiellement.

        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM z_plume.meta_import_sample_template()')
                # import des modèles pré-configurés
                cur.execute("""
                    INSERT INTO z_plume.meta_tab (tab, tab_num)
                        VALUES ('O1', NULL), ('O2', 10), ('O3', 15), ('O4', 12) ;
                    UPDATE z_plume.meta_template_categories
                        SET tab = 'O1'
                        WHERE shrcat_path = 'dct:title' AND tpl_label = 'Basique' ;
                    UPDATE z_plume.meta_template_categories
                        SET tab = 'O2'
                        WHERE shrcat_path = 'dct:description' AND tpl_label = 'Basique' ;
                    UPDATE z_plume.meta_template_categories
                        SET tab = 'O4'
                        WHERE shrcat_path = 'dct:temporal' AND tpl_label = 'Basique' ;
                    """)
                cur.execute(
                    query_template_tabs(),
                    ('Basique',)
                    )
                tabs = cur.fetchall()
                cur.execute('DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg')
                # suppression des modèles pré-configurés
        conn.close()
        self.assertEqual([x[0] for x in tabs], ['O2', 'O4', 'O1'])

    def test_query_template_tabs_2(self):
        """Requête d'import des onglets associés à un modèle (cas particuliers).

        Ce second test vérifie notamment que
        la requête n'importe pas les onglets
        des catégories qui ne sont pas de
        premier niveau, et qu'elle fonctionne
        avec les catégories locales et communes.
        
        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO z_plume.meta_tab (tab, tab_num)
                        VALUES ('O1', NULL), ('O2', 10), ('O3', 15), ('O4', 12) ;
                    INSERT INTO z_plume.meta_categorie
                        (path, origin, label) VALUES
                        ('uuid:218c1245-6ba7-4163-841e-476e0d5582af',
                            'local', 'Local valide'),
                        ('dct:title', 'shared', 'Commun valide'),
                        ('dcat:distribution / dct:issued', 'shared', 'Commun composé')
                        ;
                    INSERT INTO z_plume.meta_template (tpl_label)
                        VALUES ('Template test') ;
                    INSERT INTO z_plume.meta_template_categories
                        (tab, shrcat_path, loccat_path, tpl_label) VALUES
                        ('O1', 'dct:title', NULL, 'Template test'),
                        ('O2', NULL, 'uuid:218c1245-6ba7-4163-841e-476e0d5582af',
                            'Template test'),
                        ('O4', 'dcat:distribution / dct:issued', NULL, 'Template test') ;
                    """)
                cur.execute(
                    query_template_tabs(),
                    ('Template test',)
                    )
                tabs = cur.fetchall()
                cur.execute('DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg')
                # suppression des modèles pré-configurés
        conn.close()
        self.assertEqual([x[0] for x in tabs], ['O2', 'O1'])

    def test_query_get_columns(self):
        """Requête de récupération de la liste des colonnes d'une relation avec leurs descriptifs.

        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)  
        with conn:
            with conn.cursor() as cur:
            
                cur.execute(
                    query_get_columns(
                        'z_plume',
                        'meta_categorie'
                        )
                    )
                columns = cur.fetchall()
        conn.close()
        self.assertEqual(columns[0][0], 'path')
        self.assertTrue('chemin' in columns[0][1].lower())

    def test_query_get_columns_no_column(self):
        """Requête de récupération de la liste des colonnes... en l'absence de colonnes.

        Le test vérifie que le résultat de
        la requête est une liste vide.
        
        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)  
        with conn:
            with conn.cursor() as cur:
                cur.execute('CREATE TABLE z_plume.table_test ()')
                # création d'une table de test
                cur.execute(
                    query_get_columns(
                        'z_plume',
                        'table_test'
                        )
                    )
                columns = cur.fetchall()
                cur.execute('DROP TABLE z_plume.table_test')
                # suppression de la table de test
        conn.close()
        self.assertEqual(columns, [])

    def test_query_update_column_comment(self):
        """Requête de mise à jour du descriptif d'un (seul) champ.

        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('CREATE TABLE z_plume.table_test (num int)')
                # création d'une table de test
                query = query_update_column_comment(
                    'z_plume', 'table_test', 'num'
                    )
                cur.execute(
                    query,
                    ('Nouvelle description',)
                    )
                cur.execute(
                    "SELECT col_description('z_plume.table_test'::regclass, 1)"
                    )
                descr = cur.fetchone()
                cur.execute('DROP TABLE z_plume.table_test')
                # suppression de la table de test
        conn.close()
        self.assertEqual(descr[0], 'Nouvelle description')

    def test_query_update_columns_comments(self):
        """Requête de mise à jour des descriptifs des champs.

        """ 
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                # création d'une table de test
                cur.execute('''
                    CREATE TABLE z_plume.table_test (
                        champ1 int, "champ 2" int, "Champ3" int
                        )
                    ''')
                columns = [
                    ('champ1', 'description champ 1'),
                    ('champ 2', 'description champ 2'),
                    ('Champ3', 'description champ 3')
                    ]                
                d = WidgetsDict(columns=columns)
                query = query_update_columns_comments(
                    'z_plume', 'table_test', d
                    )
                cur.execute(query)
                cur.execute("""
                    SELECT
                        col_description('z_plume.table_test'::regclass, 1),
                        col_description('z_plume.table_test'::regclass, 2),
                        col_description('z_plume.table_test'::regclass, 3)
                    """)
                descr = cur.fetchone()
                cur.execute('DROP TABLE z_plume.table_test')
                # suppression de la table de test
        conn.close()
        self.assertEqual(descr[0], 'description champ 1')
        self.assertEqual(descr[1], 'description champ 2')
        self.assertEqual(descr[2], 'description champ 3')

    def test_query_update_columns_comments_no_columns(self):
        """Requête de mise à jour des descriptifs des champs... lorsqu'il n'y a pas de champs.

        """               
        d = WidgetsDict()
        query = query_update_columns_comments(
            'z_plume', 'table_test', d
            )
        self.assertIsNone(query)

    def test_query_get_geom_extent(self):
        """Requête de récupération du rectangle d'emprise.
        
        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                # création d'une table de test
                cur.execute('''
                    CREATE TABLE z_plume.table_test (
                        geom1 geometry(POINT, 4326),
                        "GEOM 2" geometry(POINT, 4326)
                        ) ;
                    INSERT INTO z_plume.table_test VALUES
                        (ST_SetSRID(ST_MakePoint(-70, 40), 4326), ST_SetSRID(ST_MakePoint(70, 40), 4326)),
                        (ST_SetSRID(ST_MakePoint(70, -40), 4326), ST_SetSRID(ST_MakePoint(-70, -40), 4326)) ;
                    ''')
                query = query_get_geom_extent(
                    'z_plume', 'table_test', 'geom1'
                    )
                cur.execute(query)
                bbox_geom1 = cur.fetchone()[0]
                query = query_get_geom_extent(
                    'z_plume', 'table_test', 'GEOM 2'
                    )
                cur.execute(query)
                bbox_geom2 = cur.fetchone()[0]
                cur.execute('DROP TABLE z_plume.table_test')
                # suppression de la table de test
        conn.close()
        self.assertEqual(bbox_geom1, 'POLYGON((-70 -40,-70 40,70 40,70 -40,-70 -40))')
        self.assertEqual(bbox_geom2, 'POLYGON((-70 -40,-70 40,70 40,70 -40,-70 -40))')

    def test_query_get_geom_centroid(self):
        """Requête de récupération du centre du rectangle d'emprise.
        
        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                # création d'une table de test
                cur.execute('''
                    CREATE TABLE z_plume.table_test (
                        geom1 geometry(POINT, 4326),
                        "GEOM 2" geometry(POINT, 4326)
                        ) ;
                    INSERT INTO z_plume.table_test VALUES
                        (ST_SetSRID(ST_MakePoint(-90, 40), 4326), ST_SetSRID(ST_MakePoint(70, 40), 4326)),
                        (ST_SetSRID(ST_MakePoint(70, -20), 4326), ST_SetSRID(ST_MakePoint(-90, -20), 4326)) ;
                    ''')
                query = query_get_geom_centroid(
                    'z_plume', 'table_test', 'geom1'
                    )
                cur.execute(query)
                centroid_geom1 = cur.fetchone()[0]
                query = query_get_geom_centroid(
                    'z_plume', 'table_test', 'GEOM 2'
                    )
                cur.execute(query)
                centroid_geom2 = cur.fetchone()[0]
                cur.execute('DROP TABLE z_plume.table_test')
                # suppression de la table de test
        conn.close()
        self.assertEqual(centroid_geom1, 'POINT(-10 10)')
        self.assertEqual(centroid_geom2, 'POINT(-10 10)')

    def test_query_get_geom_srid(self):
        """Requête de récupération du référentiel d'un champ de géométries donné.
        
        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                # création d'une table de test
                cur.execute('''
                    CREATE TABLE z_plume.table_test (
                        geom1 geometry(POINT, 2154),
                        "GEOM 2" geometry(POINT, 4326),
                        geom3 geometry,
                        geom4 text
                        ) ;
                    ''')
                query = query_get_geom_srid()
                cur.execute(query, 
                    ('z_plume', 'table_test', 'geom1'))
                srid_geom1 = cur.fetchone()[0]
                query = query_get_geom_srid()
                cur.execute(query,
                    ('z_plume', 'table_test', 'GEOM 2'))
                srid_geom2 = cur.fetchone()[0]
                query = query_get_geom_srid()
                cur.execute(query,
                    ('z_plume', 'table_test', 'geom3'))
                l_srid_geom3 = cur.fetchone()
                query = query_get_geom_srid()
                cur.execute(query,
                    ('z_plume', 'table_test', 'geom4'))
                l_srid_geom4 = cur.fetchone()
                cur.execute('DROP TABLE z_plume.table_test')
                # suppression de la table de test
        conn.close()
        self.assertEqual(srid_geom1, 'EPSG:2154')
        self.assertEqual(srid_geom2, 'EPSG:4326')
        self.assertFalse(l_srid_geom3)
        self.assertFalse(l_srid_geom4)
        
    def test_query_get_srid_list(self):
        """Requête de récupération de la liste des référentiels de coordonnées utilisés par une relation.
        
        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                # création d'une table de test
                cur.execute('''
                    CREATE TABLE z_plume.table_test (
                        geom1 geometry(POINT, 2154),
                        "GEOM 2" geometry(POINT, 4326),
                        geom3 geometry,
                        geom4 text,
                        geom5 geometry(POLYGON, 2154)
                        ) ;
                    ''')
                query = query_get_srid_list('z_plume', 'table_test')
                cur.execute(*query)
                srid_list = cur.fetchall()
                cur.execute('DROP TABLE z_plume.table_test')
                # suppression de la table de test
        conn.close()
        self.assertListEqual(srid_list, [('EPSG', '2154'), ('EPSG', '4326')])

    def test_query_plume_pg_check(self):
        """Contrôle de la présence de PlumePg et de l'accès aux objets.
        
        Les tests sont réalisés avec la version 0.0.1
        de PlumePg, qui doit donc être disponible sur
        le serveur.
        Il serait nécessaire de modifier cette version si
        :py:func:`plume.pg.queries.query_plume_pg_check`
        venait à contrôler les droits sur des objets qui
        n'existaient pas dans cette version.
        
        """
        # PlumePg installée, pas de spécification de version
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute("""DROP EXTENSION plume_pg ;
                    CREATE EXTENSION plume_pg VERSION '0.0.1'""")
                query = query_plume_pg_check(min_version=None,
                    max_version=None)
                cur.execute(*query)
                result = cur.fetchone()
        conn.close()
        self.assertTrue(result[0])
        self.assertListEqual(result[1], [None, None])
        self.assertIsNotNone(result[2])
        self.assertIsNotNone(result[3])
        self.assertListEqual(result[4], [])
        self.assertListEqual(result[5], [])
        # PlumePg installée, avec spécification de version min
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                query = query_plume_pg_check(min_version='0.0.1')
                cur.execute(*query)
                result = cur.fetchone()
        conn.close()
        self.assertTrue(result[0])
        self.assertListEqual(result[1], ['0.0.1', '1.0.0'])
        # PlumePg installée, avec spécification de versions min et max
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                query = query_plume_pg_check(min_version='0.0.1',
                    max_version='2.0.1')
                cur.execute(*query)
                result = cur.fetchone()
        conn.close()
        self.assertTrue(result[0])
        self.assertListEqual(result[1], ['0.0.1', '2.0.1'])
        # PlumePg installée, avec spécification de version max
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                query = query_plume_pg_check(min_version=None,
                    max_version='2.0.1')
                cur.execute(*query)
                result = cur.fetchone()
        conn.close()
        self.assertTrue(result[0])
        self.assertListEqual(result[1], [None, '2.0.1'])
        # PlumePg non installée
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                query = query_plume_pg_check()
                cur.execute('DROP EXTENSION plume_pg')
                cur.execute(*query)
                result = cur.fetchone()
                cur.execute("CREATE EXTENSION plume_pg VERSION '0.0.1'")
        conn.close()
        self.assertFalse(result[0])
        self.assertIsNone(result[2])
        self.assertIsNotNone(result[3])
        self.assertListEqual(result[4], [])
        self.assertListEqual(result[5], [])
        # Non respect borne min
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                query = query_plume_pg_check(min_version='0.3.0',
                    max_version=None)
                cur.execute(*query)
                result = cur.fetchone()
        conn.close()
        self.assertFalse(result[0])
        self.assertIsNotNone(result[2])
        self.assertIsNotNone(result[3])
        self.assertListEqual(result[4], [])
        self.assertListEqual(result[5], [])
        # Non respect borne max
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                query = query_plume_pg_check(min_version=None,
                    max_version='0.0.1')
                cur.execute(*query)
                result = cur.fetchone()
        conn.close()
        self.assertFalse(result[0])
        self.assertIsNotNone(result[2])
        self.assertIsNotNone(result[3])
        self.assertListEqual(result[4], [])
        self.assertListEqual(result[5], [])
        # Droits manquants
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                q, p  = query_plume_pg_check(min_version=None, max_version=None)
                cur.execute(psycopg2.sql.SQL('''
                    CREATE ROLE g_plumepg_test ;
                    GRANT SELECT ON ALL TABLES IN SCHEMA z_plume TO g_plumepg_test ;
                    REVOKE SELECT ON z_plume.meta_tab FROM g_plumepg_test ;
                    REVOKE SELECT ON z_plume.meta_template FROM g_plumepg_test ;
                    SET ROLE g_plumepg_test ;
                    {} ;
                    ''').format(q), p)
                result = cur.fetchone()
                cur.execute(psycopg2.sql.SQL('''
                    RESET ROLE ;
                    GRANT USAGE ON SCHEMA z_plume TO g_plumepg_test ;
                    SET ROLE g_plumepg_test ;
                    {} ;
                    ''').format(q), p)
                result2 = cur.fetchone()
                cur.execute('''
                    RESET ROLE ;
                    REVOKE SELECT ON ALL TABLES IN SCHEMA z_plume FROM g_plumepg_test ;
                    REVOKE USAGE ON SCHEMA z_plume FROM g_plumepg_test ;
                    DROP ROLE g_plumepg_test ;
                    ''')
        conn.close()
        self.assertFalse(result[0])
        self.assertFalse(result2[0])
        self.assertIsNotNone(result[2])
        self.assertIsNotNone(result2[2])
        self.assertIsNotNone(result[3])
        self.assertIsNotNone(result2[3])
        self.assertListEqual(result[4], ['z_plume'])
        self.assertListEqual(result2[4], [])
        self.assertListEqual(result[5], [])
        self.assertListEqual(result2[5], ['z_plume.meta_tab', 'z_plume.meta_template'])
        
        # PlumePg dans la version de référence,
        # bornes issues de la configuration
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute("""DROP EXTENSION plume_pg ;
                    CREATE EXTENSION plume_pg""")
                query = query_plume_pg_check()
                cur.execute(*query)
                result = cur.fetchone()
        conn.close()
        self.assertTrue(result[0])
        self.assertIsNotNone(result[1][0])
        self.assertIsNotNone(result[1][1])
        self.assertIsNotNone(result[2])
        self.assertIsNotNone(result[3])
        self.assertListEqual(result[4], [])
        self.assertListEqual(result[5], [])

    def test_query_get_comment_fragments(self):
        """Récupération d'un ou plusieurs fragments du descriptif d'une table.
        
        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                # création d'une table de test
                cur.execute('''
                    CREATE TABLE z_plume.table_test () ;
                    COMMENT ON TABLE z_plume.table_test IS 'Ma + table + est. une table'
                    ''')
                query = query_get_comment_fragments('z_plume', 'table_test',
                    pattern='[a-z]+', flags='gi')
                cur.execute(*query)
                result1 = cur.fetchall()
                query = query_get_comment_fragments('z_plume', 'table_test',
                    pattern='^[^.]*')
                cur.execute(*query)
                result2 = cur.fetchall()
                query = query_get_comment_fragments('z_plume', 'table_test',
                    pattern='[a-z+', flags='g')
                cur.execute(*query)
                result3 = cur.fetchall()
                query = query_get_comment_fragments('z_plume', 'table_test',
                    pattern='[a-z]+', flags='gz')
                cur.execute(*query)
                result4 = cur.fetchall()
                query = query_get_comment_fragments('z_plume', 'table_test',
                    pattern='^[^.]*', truc='machin')
                cur.execute(*query)
                result5 = cur.fetchall()
                query = query_get_comment_fragments('z_plume', 'table_test')
                cur.execute(*query)
                result6 = cur.fetchall()
                cur.execute('DROP TABLE z_plume.table_test')
                # suppression de la table de test
        conn.close()
        self.assertListEqual(result1, [('Ma',), ('table',), ('est',), ('une',), ('table',)])
        self.assertListEqual(result2, [('Ma + table + est',)])
        self.assertListEqual(result3, [])
        self.assertListEqual(result4, [])
        self.assertListEqual(result5, [('Ma + table + est',)])
        self.assertListEqual(result6, [('Ma + table + est. une table',)])

if __name__ == '__main__':
    unittest.main()

