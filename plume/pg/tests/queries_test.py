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
from datetime import datetime

from plume.pg.tests.connection import ConnectionString
from plume.pg.queries import (
    query_is_relation_owner, query_exists_extension, query_is_template_admin,
    query_get_relation_kind, query_update_table_comment, query_get_table_comment, 
    query_list_templates, query_get_categories, query_template_tabs,
    query_get_columns, query_update_column_comment, query_update_columns_comments,
    query_get_geom_extent, query_get_geom_srid, query_get_srid_list,
    query_get_geom_centroid, query_evaluate_local_templates, query_plume_pg_check,
    query_get_comment_fragments, query_get_creation_date, query_get_modification_date,
    query_insert_or_update_any_table, query_insert_or_update_meta_categorie,
    query_insert_or_update_meta_tab, query_insert_or_update_meta_template,
    query_insert_or_update_meta_template_categories, query_read_meta_categorie,
    query_read_meta_tab, query_read_meta_template, query_read_meta_template_categories,
    query_read_enum_meta_special, query_read_enum_meta_compute, query_read_enum_meta_datatype,
    query_read_enum_meta_geo_tool, query_delete_meta_categorie, query_delete_meta_tab,
    query_delete_meta_template, query_delete_meta_template_categories,
    query_plume_pg_import_sample_template, query_plume_pg_create, query_plume_pg_drop,
    query_plume_pg_update, query_plume_pg_status, query_stamp_recording_disable,
    query_stamp_recording_enable, query_stamp_to_metadata_disable, query_stamp_to_metadata_enable,
    query_update_any_table
)
from plume.pg.template import LocalTemplatesCollection, TemplateDict
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
                    CREATE EXTENSION plume_pg CASCADE ;
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
                query = query_is_relation_owner('z_plume', 'meta_categorie')
                cur.execute(*query)
                res = cur.fetchone()
        conn.close()
        self.assertTrue(res[0])

    def test_query_exists_extension(self):
        """Requête qui vérifie que l'extension PlumePg est installée sur la base.

        Il est présumé que c'est le cas sur la base
        utilisée pour la recette.
        
        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute(*query_exists_extension('plume_pg'))
                res0 = cur.fetchone()[0]
                cur.execute(*query_exists_extension('bidule'))
                res1 = cur.fetchone()[0]
                cur.execute(*query_exists_extension('asgard'))
                res2 = cur.fetchone()[0]
        conn.close()
        self.assertTrue(res0)
        self.assertIsNone(res1)
        self.assertFalse(res2)
        self.assertIsNotNone(res2)

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
                    *query_get_relation_kind(
                        'z_plume', 'meta_local_categorie'
                        )
                    )
                kind_r = cur.fetchone()
                cur.execute(
                    *query_get_relation_kind(
                        'z_plume', 'meta_categorie'
                        )
                    )
                kind_p = cur.fetchone()
                cur.execute(
                    *query_get_relation_kind(
                        'z_plume', 'meta_template_categories_full'
                        )
                    )
                kind_v = cur.fetchone()
                cur.execute("""CREATE MATERIALIZED VIEW z_plume.m_test AS (
                    SELECT * FROM z_plume.meta_categorie)""")
                cur.execute(
                    *query_get_relation_kind(
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
                    *query_get_relation_kind(
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
                    *query_get_table_comment(
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
                        *query_get_relation_kind(
                            'z_plume', k
                            )
                        )
                    kind = cur.fetchone()[0]
                    query = query_update_table_comment(
                        'z_plume', k, relation_kind=kind,
                        description='Nouvelle description'
                        )
                    cur.execute(*query)
                    cur.execute(
                        *query_get_table_comment(
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
                    *query_list_templates('r_schema', 'table')
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
                    *query_get_categories('Basique')
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
                    INSERT INTO z_plume.meta_tab (tab_id, tab_label, tab_num)
                        VALUES (101, 'O1', NULL), (102, 'O2', 10), (103, 'O3', 15), (104, 'O4', 12) ;
                    UPDATE z_plume.meta_template_categories
                        SET tab_id = 101
                        WHERE shrcat_path = 'dct:title'
                            AND meta_template_categories.tpl_id = (
                                SELECT meta_template.tpl_id
                                    FROM z_plume.meta_template
                                    WHERE tpl_label = 'Basique'
                            ) ;
                    UPDATE z_plume.meta_template_categories
                        SET tab_id = 102
                        WHERE shrcat_path = 'dct:description'
                            AND meta_template_categories.tpl_id = (
                                SELECT meta_template.tpl_id
                                    FROM z_plume.meta_template
                                    WHERE tpl_label = 'Basique'
                            ) ;
                    UPDATE z_plume.meta_template_categories
                        SET tab_id = 104
                        WHERE shrcat_path = 'dct:temporal'
                            AND meta_template_categories.tpl_id = (
                                SELECT meta_template.tpl_id
                                    FROM z_plume.meta_template
                                    WHERE tpl_label = 'Basique'
                            ) ;
                    """)
                cur.execute(
                    *query_template_tabs('Basique')
                    )
                tabs = cur.fetchall()
                cur.execute('DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg')
                # suppression des modèles pré-configurés
        conn.close()
        self.assertEqual([x[0] for x in tabs], ['O2', 'O4', 'O1'])

    def test_query_template_tabs_2(self):
        """Requête d'import des onglets associés à un modèle (cas particuliers).

        Ce second test vérifie notamment que
        la requête fonctionne avec les catégories locales
        et communes.
        
        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO z_plume.meta_tab (tab_id, tab_label, tab_num)
                        VALUES (101, 'O1', NULL), (102, 'O2', 10), (103, 'O3', 15), (104, 'O4', 12) ;
                    INSERT INTO z_plume.meta_categorie
                        (path, origin, label) VALUES
                        ('uuid:218c1245-6ba7-4163-841e-476e0d5582af',
                            'local', 'Local valide'),
                        ('dct:title', 'shared', 'Commun valide'),
                        ('dcat:distribution / dct:issued', 'shared', 'Commun composé')
                        ;
                    INSERT INTO z_plume.meta_template (tpl_id, tpl_label)
                        VALUES (99, 'Template test') ;
                    INSERT INTO z_plume.meta_template_categories
                        (tab_id, shrcat_path, loccat_path, tpl_id) VALUES
                        (101, 'dct:title', NULL, 99),
                        (102, NULL, 'uuid:218c1245-6ba7-4163-841e-476e0d5582af', 99),
                        (104, 'dcat:distribution / dct:issued', NULL, 99) ;
                    """)
                cur.execute(
                    *query_template_tabs('Template test')
                    )
                tabs = cur.fetchall()
                cur.execute(
                    *query_get_categories('Template test')
                    )
                categories = cur.fetchall()
                cur.execute('DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg')
                # suppression des modèles pré-configurés
        conn.close()
        self.assertEqual([x[0] for x in tabs], ['O2', 'O4', 'O1'])
        template = TemplateDict(categories, tabs)
        widgetsdict = WidgetsDict(template=template)
        self.assertListEqual([t.label for t in widgetsdict.root.children], ['O2', 'O1', 'Autres'])

    def test_query_get_columns(self):
        """Requête de récupération de la liste des colonnes d'une relation avec leurs descriptifs.

        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)  
        with conn:
            with conn.cursor() as cur:
            
                cur.execute(
                    *query_get_columns(
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
                    *query_get_columns(
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
                    'z_plume', 'table_test', 'num',
                    'Nouvelle description'
                    )
                cur.execute(*query)
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
                cur.execute(*query)
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
                cur.execute(*query)
                bbox_geom1 = cur.fetchone()[0]
                query = query_get_geom_extent(
                    'z_plume', 'table_test', 'GEOM 2'
                    )
                cur.execute(*query)
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
                cur.execute(*query)
                centroid_geom1 = cur.fetchone()[0]
                query = query_get_geom_centroid(
                    'z_plume', 'table_test', 'GEOM 2'
                    )
                cur.execute(*query)
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
                query = query_get_geom_srid('z_plume', 'table_test', 'geom1')
                cur.execute(*query)
                srid_geom1 = cur.fetchone()[0]
                query = query_get_geom_srid('z_plume', 'table_test', 'GEOM 2')
                cur.execute(*query)
                srid_geom2 = cur.fetchone()[0]
                query = query_get_geom_srid('z_plume', 'table_test', 'geom3')
                cur.execute(*query)
                l_srid_geom3 = cur.fetchone()
                query = query_get_geom_srid('z_plume', 'table_test', 'geom4')
                cur.execute(*query)
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
                    ''')
                query = query_get_comment_fragments('z_plume', 'table_test',
                    pattern='[a-z]+', flags='gi')
                cur.execute(*query)
                result0 = cur.fetchall()
                cur.execute('''
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
                cur.execute("""
                    COMMENT ON TABLE z_plume.table_test IS 'Ma + table + est.<METADATA>
                        ...
                        </METADATA> une table'""")
                query = query_get_comment_fragments('z_plume', 'table_test')
                cur.execute(*query)
                result7 = cur.fetchall()
                query = query_get_comment_fragments('z_plume', 'table_test',
                    pattern='^[^.]*')
                cur.execute(*query)
                result8 = cur.fetchall()
                query = query_get_comment_fragments('z_plume', 'table_test',
                    pattern='zzzz')
                cur.execute(*query)
                result9 = cur.fetchall()
                cur.execute('DROP TABLE z_plume.table_test')
                # suppression de la table de test
        conn.close()
        self.assertListEqual(result0, [])
        self.assertListEqual(result1, [('Ma',), ('table',), ('est',), ('une',), ('table',)])
        self.assertListEqual(result2, [('Ma + table + est',)])
        self.assertListEqual(result3, [])
        self.assertListEqual(result4, [])
        self.assertListEqual(result5, [('Ma + table + est',)])
        self.assertListEqual(result6, [('Ma + table + est. une table',)])
        self.assertListEqual(result7, [('Ma + table + est. une table',)])
        self.assertListEqual(result8, [('Ma + table + est',)])
        self.assertListEqual(result9, [])

    def test_query_get_creation_date(self):
        """Récupération de la date de création d'une table.
        
        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                # activation des fonctionnalités d'enregistrement
                # des dates + création d'une table de test
                cur.execute('''
                    ALTER EVENT TRIGGER plume_stamp_table_creation ENABLE ;
                    ALTER EVENT TRIGGER plume_stamp_table_modification ENABLE ;
                    ALTER EVENT TRIGGER plume_stamp_table_drop ENABLE ;
                    CREATE TABLE z_plume.table_test () ;
                    ''')
                query = query_get_creation_date('z_plume', 'table_test')
                cur.execute(*query)
                result1 = cur.fetchall()
                query = query_get_creation_date('z_plume', 'meta_template_categories_full')
                result2 = cur.fetchall()
                cur.execute('''
                    DROP TABLE z_plume.table_test ;
                    TRUNCATE z_plume.stamp_timestamp ;
                    ALTER EVENT TRIGGER plume_stamp_table_drop DISABLE ;
                    ALTER EVENT TRIGGER plume_stamp_table_modification DISABLE ;
                    ALTER EVENT TRIGGER plume_stamp_table_creation DISABLE ;
                    ''')
        conn.close()
        self.assertTrue(isinstance(result1[0][0], datetime))
        self.assertListEqual(result2, [])

    def test_query_get_modification_date(self):
        """Récupération de la date de création d'une table.
        
        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                # activation des fonctionnalités d'enregistrement
                # des dates + création d'une table de test
                cur.execute('''
                    ALTER EVENT TRIGGER plume_stamp_table_creation ENABLE ;
                    ALTER EVENT TRIGGER plume_stamp_table_modification ENABLE ;
                    ALTER EVENT TRIGGER plume_stamp_table_drop ENABLE ;
                    CREATE TABLE z_plume.table_test () ;
                    ALTER TABLE z_plume.table_test RENAME TO table_test_2 ;
                    ''')
                query = query_get_modification_date('z_plume', 'table_test_2')
                cur.execute(*query)
                result1 = cur.fetchall()
                query = query_get_modification_date('z_plume', 'meta_template_categories_full')
                result2 = cur.fetchall()
                cur.execute('''
                    DROP TABLE z_plume.table_test_2 ;
                    TRUNCATE z_plume.stamp_timestamp ;
                    ALTER EVENT TRIGGER plume_stamp_table_drop DISABLE ;
                    ALTER EVENT TRIGGER plume_stamp_table_modification DISABLE ;
                    ALTER EVENT TRIGGER plume_stamp_table_creation DISABLE ;
                    ''')
        conn.close()
        self.assertTrue(isinstance(result1[0][0], datetime))
        self.assertListEqual(result2, [])

    def test_query_is_template_admin(self):
        """Vérification de la présence de droits d'édition sur les modèles.

        La documentation de la fonction précise qu'elle ne doit être
        utilisée que si PlumePg est active sur la base.

        Ceci est un pseudo-test qui vérifie seulement l'absence de coquille
        dans le code. Il est exécuté avec un rôle de connexion super-utilisateur
        qui a nécessairement les droits nécessaires.
        
        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                query = query_is_template_admin()
                cur.execute(*query)
                result = cur.fetchone()
        conn.close()
        self.assertIsNotNone(result)
        # un super-utilisateur a tous les droits...
        self.assertTrue(result[0])

    def test_query_insert_or_update_any_table(self):
        """Contrôle de la fonction générique en charge de créer les requêtes INSERT ON CONFLICT DO UPDATE
        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('''
                    CREATE TABLE z_plume.table_test_insert_update (
                        id serial PRIMARY KEY,
                        field_1 text,
                        field_2 text
                    )
                ''')
                # INSERT avec une liste
                query = query_insert_or_update_any_table(
                    'z_plume', 'table_test_insert_update', 'id',
                    [None, 'val A-1'], ['id', 'field_1']
                )
                cur.execute(*query)
                cur.execute('''
                    SELECT count(*) FROM z_plume.table_test_insert_update
                        WHERE field_1 = 'val A-1'
                ''')
                res1 = cur.fetchone()[0]
                # INSERT avec dictionnaire
                query = query_insert_or_update_any_table(
                    'z_plume', 'table_test_insert_update', 'id',
                    {'id': 99, 'field_1': 'val B-1'}
                )
                cur.execute(*query)
                cur.execute('''
                    SELECT count(*) FROM z_plume.table_test_insert_update
                        WHERE field_1 = 'val B-1'
                ''')
                res2 = cur.fetchone()[0]
                # UPDATE
                query = query_insert_or_update_any_table(
                    'z_plume', 'table_test_insert_update', 'id',
                    {'id': 99, 'field_2': 'val B-2'}
                )
                cur.execute(*query)
                cur.execute('''
                    SELECT count(*) FROM z_plume.table_test_insert_update
                        WHERE field_1 = 'val B-1'
                ''')
                res3 = cur.fetchone()[0]
                cur.execute('''
                    SELECT count(*) FROM z_plume.table_test_insert_update
                        WHERE field_2 IS NULL
                ''')
                res4 = cur.fetchone()[0]
                cur.execute('''
                    SELECT count(*) FROM z_plume.table_test_insert_update
                        WHERE field_2 = 'val B-2' AND id = 99
                ''')
                res5 = cur.fetchone()[0]
                # nettoyage
                cur.execute('''
                    DROP TABLE z_plume.table_test_insert_update
                ''')
        conn.close()
        self.assertEqual(res1, 1)
        self.assertEqual(res2, 1)
        self.assertEqual(res3, 1)
        self.assertEqual(res4, 1)
        self.assertEqual(res5, 1)

    def test_query_read_meta_categorie(self):
        """Lecture de la table des catégories.        
        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                query = query_read_meta_categorie()
                cur.execute(*query)
                result = cur.fetchall()
        conn.close()
        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, list))
        self.assertGreater(len(result), 2)
        self.assertTrue(isinstance(result[0], tuple))
        self.assertEqual(len(result[0]), 1)
        self.assertTrue(isinstance(result[0][0], dict))
        self.assertIsNotNone(result[0][0].get('label'))

    def test_query_read_meta_tab(self):
        """Lecture de la table des onglets.        
        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('''
                    INSERT INTO z_plume.meta_tab (tab_label, tab_num)
                        VALUES ('Onglet 1', 1), ('Onglet 10', 10)
                ''')
                query = query_read_meta_tab()
                cur.execute(*query)
                result = cur.fetchall()
                cur.execute('''
                    TRUNCATE z_plume.meta_tab CASCADE
                ''')
        conn.close()
        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, list))
        self.assertEqual(len(result), 2)
        self.assertTrue(isinstance(result[0], tuple))
        self.assertEqual(len(result[0]), 1)
        self.assertTrue(isinstance(result[0][0], dict))
        self.assertTrue('tab_label' in result[0][0])
        self.assertEqual(result[0][0]['tab_label'], 'Onglet 1')
        self.assertTrue('tab_num' in result[0][0])
        self.assertEqual(result[0][0]['tab_num'], 1)
        self.assertTrue('tab_id' in result[0][0])
        self.assertIsNotNone(result[0][0]['tab_id'])

    def test_query_read_meta_template(self):
        """Lecture de la table des modèles.        
        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('''
                    INSERT INTO z_plume.meta_template (tpl_label)
                        VALUES ('Modèle 1'), ('Modèle 10')
                ''')
                query = query_read_meta_template()
                cur.execute(*query)
                result = cur.fetchall()
                cur.execute('''
                    TRUNCATE z_plume.meta_template CASCADE
                ''')
        conn.close()
        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, list))
        self.assertEqual(len(result), 2)
        self.assertTrue(isinstance(result[0], tuple))
        self.assertEqual(len(result[0]), 1)
        self.assertTrue(isinstance(result[0][0], dict))
        self.assertTrue('tpl_label' in result[0][0])
        self.assertEqual(result[0][0]['tpl_label'], 'Modèle 1')

    def test_query_read_meta_template_categories(self):
        """Lecture de la table des associations modèles-catégories.        
        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('''
                    INSERT INTO z_plume.meta_template (tpl_id, tpl_label)
                        VALUES (1, 'Modèle 1'), (10, 'Modèle 10') ;
                    INSERT INTO z_plume.meta_template_categories (tpl_id, shrcat_path)
                        VALUES (10, 'dct:title'), (10, 'dct:description')
                ''')
                query = query_read_meta_template_categories()
                cur.execute(*query)
                result = cur.fetchall()
                cur.execute('''
                    TRUNCATE z_plume.meta_template CASCADE
                ''')
        conn.close()
        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, list))
        self.assertEqual(len(result), 2)
        self.assertTrue(isinstance(result[0], tuple))
        self.assertEqual(len(result[0]), 1)
        self.assertTrue(isinstance(result[0][0], dict))
        self.assertTrue('tpl_id' in result[0][0])
        self.assertEqual(result[0][0]['tpl_id'], 10)

    def test_query_insert_or_update_meta_template_categories(self):
        """Mise à jour de la table des associations modèle-catégories.        
        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('''
                    INSERT INTO z_plume.meta_template (tpl_id, tpl_label)
                        VALUES (1, 'Modèle 1'), (10, 'Modèle 10') ;
                ''')
                query = query_insert_or_update_meta_template_categories(
                    {'tpl_id': 10, 'shrcat_path': 'dct:title'}
                )
                cur.execute(*query)
                result1 = cur.fetchone()
                query = query_insert_or_update_meta_template_categories(
                    [None, 10, 'dct:description'], ['tplcat_id', 'tpl_id', 'shrcat_path']
                )
                cur.execute(*query)
                result0 = cur.fetchone()
                query = query_read_meta_template_categories()
                cur.execute(*query)
                result = cur.fetchall()
                cur.execute('''
                    TRUNCATE z_plume.meta_template CASCADE
                ''')
        conn.close()
        self.assertIsNotNone(result1)
        self.assertIsNotNone(result1[0]['tplcat_id'])
        self.assertEqual(result1[0]['shrcat_path'], 'dct:title')
        self.assertIsNotNone(result0)
        self.assertIsNotNone(result0[0]['tplcat_id'])
        self.assertEqual(result0[0]['shrcat_path'], 'dct:description')
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][0]['tpl_id'], 10)

    def test_query_insert_or_update_meta_template(self):
        """Mise à jour de la table des modèles.        
        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                query = query_insert_or_update_meta_template(
                    {'tpl_id': 10, 'tpl_label': 'Modèle 10'}
                )
                cur.execute(*query)
                result0 = cur.fetchone()
                query = query_insert_or_update_meta_template(
                    [10, 'Modèle 10*', 'Mon commentaire...'], ['tpl_id', 'tpl_label', 'comment']
                )
                cur.execute(*query)
                result1 = cur.fetchone()
                query = query_read_meta_template()
                cur.execute(*query)
                result = cur.fetchall()
                cur.execute('''
                    TRUNCATE z_plume.meta_template CASCADE
                ''')
        conn.close()
        self.assertIsNotNone(result0)
        self.assertEqual(result0[0]['tpl_label'], 'Modèle 10')
        self.assertIsNotNone(result1)
        self.assertEqual(result1[0]['tpl_label'], 'Modèle 10*')
        self.assertEqual(result1[0]['comment'], 'Mon commentaire...')
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0]['tpl_label'], 'Modèle 10*')
        self.assertEqual(result[0][0]['comment'], 'Mon commentaire...')

    def test_query_insert_or_update_meta_tab(self):
        """Mise à jour de la table des onglets.        
        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                query = query_insert_or_update_meta_tab(
                    {'tab_label': 'Onglet 1'}
                )
                cur.execute(*query)
                result0 = cur.fetchone()
                query = query_insert_or_update_meta_tab(
                    ['Onglet 2', 100], ['tab_label', 'tab_num']
                )
                cur.execute(*query)
                result1 = cur.fetchone()
                query = query_read_meta_tab()
                cur.execute(*query)
                result = cur.fetchall()
                cur.execute('''
                    TRUNCATE z_plume.meta_tab CASCADE
                ''')
        conn.close()
        self.assertIsNotNone(result0)
        self.assertEqual(result0[0]['tab_label'], 'Onglet 1')
        self.assertIsNotNone(result1)
        self.assertEqual(result1[0]['tab_label'], 'Onglet 2')
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        self.assertTrue(result[0][0]['tab_label'], 'Onglet 1')
        self.assertIsNone(result[0][0]['tab_num'])
        self.assertTrue(result[1][0]['tab_label'], 'Onglet 2')
        self.assertTrue(result[1][0]['tab_num'], 100)

    def test_query_insert_or_update_meta_categorie(self):
        """Mise à jour de la table des catégories.        
        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                query = query_insert_or_update_meta_categorie(
                    {'path': None, 'label': 'Catégorie 1'}
                )
                cur.execute(*query)
                result0a = cur.fetchone()
                query = query_insert_or_update_meta_categorie(
                    {'path': None, 'origin': 'local', 'label': 'Catégorie 2'}
                )
                cur.execute(*query)
                result0b = cur.fetchone()
                query = query_insert_or_update_meta_categorie(
                    ['dct:title', 'shared', 'Catégorie titre', 'Nom Nom Nom'],
                    ['path', 'origin', 'label', 'description']
                )
                cur.execute(*query)
                result0c = cur.fetchone()
                cur.execute('''
                    SELECT * FROM z_plume.meta_shared_categorie
                        WHERE label = 'Catégorie titre'
                ''')
                result1 = cur.fetchall()
                cur.execute('''
                    SELECT * FROM z_plume.meta_local_categorie
                ''')
                result2 = cur.fetchall()
                query = query_insert_or_update_meta_categorie(
                    ['dct:title', 'shared', 'Nom'],
                    ['path', 'origin', 'label']
                )
                cur.execute(*query)
                result3 = cur.fetchone()
                cur.execute('''
                    DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg
                ''')
        conn.close()
        self.assertIsNotNone(result0a)
        self.assertIsNotNone(result0a[0]['path'])
        self.assertEqual(result0a[0]['label'], 'Catégorie 1')
        self.assertEqual(result0a[0]['origin'], 'local')
        self.assertIsNotNone(result0b)
        self.assertIsNotNone(result0b[0]['path'])
        self.assertEqual(result0b[0]['label'], 'Catégorie 2')
        self.assertIsNotNone(result0c)
        self.assertEqual(result0c[0]['label'], 'Catégorie titre')
        self.assertIsNotNone(result1)
        self.assertEqual(len(result1), 1)
        self.assertEqual(len(result2), 2)
        self.assertIsNotNone(result3)
        self.assertEqual(result3[0]['label'], 'Nom')
        self.assertEqual(result3[0]['description'], 'Nom Nom Nom')

    def test_query_read_enum_meta_special(self):
        """Récupération du type énuméré des champs 'special'.
        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                query = query_read_enum_meta_special()
                cur.execute(*query)
                result = cur.fetchone()
        conn.close()
        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result[0], list))
        self.assertTrue('url' in result[0])
        self.assertGreater(len(result[0]), 1)

    def test_query_read_enum_meta_datatype(self):
        """Récupération du type énuméré des champs 'datatype'.
        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                query = query_read_enum_meta_datatype()
                cur.execute(*query)
                result = cur.fetchone()
        conn.close()
        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result[0], list))
        self.assertTrue('rdf:langString' in result[0])
        self.assertGreater(len(result[0]), 1)

    def test_query_read_enum_meta_geo_tool(self):
        """Récupération du type énuméré des champs 'geo_tools'.
        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                query = query_read_enum_meta_geo_tool()
                cur.execute(*query)
                result = cur.fetchone()
        conn.close()
        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result[0], list))
        self.assertTrue('bbox' in result[0])
        self.assertGreater(len(result[0]), 1)

    def test_query_read_enum_meta_compute(self):
        """Récupération du type énuméré des champs 'compute'.
        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                query = query_read_enum_meta_compute()
                cur.execute(*query)
                result = cur.fetchone()
        conn.close()
        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result[0], list))
        self.assertTrue('auto' in result[0])
        self.assertGreater(len(result[0]), 1)

    def test_query_delete_meta_tab(self):
        """Suppression dans la table des onglets.        
        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                query = query_insert_or_update_meta_tab(
                    {'tab_id': 1, 'tab_label': 'Onglet 1', 'tab_num': 100}
                )
                cur.execute(*query)
                query = query_read_meta_tab()
                cur.execute(*query)
                result1 = cur.fetchall()
                query = query_delete_meta_tab(
                    [1, 200], ['tab_id', 'tab_num']
                )
                cur.execute(*query)
                query = query_read_meta_tab()
                cur.execute(*query)
                result2 = cur.fetchall()
                cur.execute('''
                    TRUNCATE z_plume.meta_tab CASCADE
                ''')
        conn.close()
        self.assertIsNotNone(result1)
        self.assertEqual(len(result1), 1)
        self.assertFalse(result2)

    def test_query_delete_meta_tab(self):
        """Suppression dans la table des modèles.        
        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                query = query_insert_or_update_meta_template(
                    [10, 'Modèle 10', 'Mon commentaire...'], ['tpl_id', 'tpl_label', 'comment']
                )
                cur.execute(*query)
                query = query_read_meta_template()
                cur.execute(*query)
                result1 = cur.fetchall()
                query = query_delete_meta_template(
                    {'tpl_id': 10}
                )
                cur.execute(*query)
                query = query_read_meta_template()
                cur.execute(*query)
                result2 = cur.fetchall()
                cur.execute('''
                    TRUNCATE z_plume.meta_template CASCADE
                ''')
        conn.close()
        self.assertIsNotNone(result1)
        self.assertEqual(len(result1), 1)
        self.assertFalse(result2)

    def test_query_delete_meta_template_categories(self):
        """Suppression dans la table d'association des catégories aux modèles.        
        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('''
                    INSERT INTO z_plume.meta_template (tpl_id, tpl_label)
                        VALUES (1, 'Modèle 1'), (10, 'Modèle 10') ;
                ''')
                query = query_insert_or_update_meta_template_categories(
                    {'tplcat_id': 100, 'tpl_id': 10, 'shrcat_path': 'dct:title'}
                )
                cur.execute(*query)
                query = query_read_meta_template_categories()
                cur.execute(*query)
                result1 = cur.fetchall()
                query = query_delete_meta_template_categories(
                    {'tplcat_id': 100,  'tpl_label': 'Modèle X', 'truc': 'bidule'}
                )
                cur.execute(*query)
                query = query_read_meta_template_categories()
                cur.execute(*query)
                result2 = cur.fetchall()
                cur.execute('''
                    TRUNCATE z_plume.meta_template CASCADE
                ''')
        conn.close()
        self.assertIsNotNone(result1)
        self.assertEqual(len(result1), 1)
        self.assertFalse(result2)

    def test_query_delete_meta_categorie(self):
        """Suppression dans la table des catégories.        
        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                query = query_read_meta_categorie()
                cur.execute(*query)
                result0 = cur.fetchall()
                query = query_delete_meta_categorie(
                    {'path': 'dct:description'}
                )
                cur.execute(*query)
                query = query_read_meta_categorie()
                cur.execute(*query)
                result1 = cur.fetchall()
                cur.execute('''
                    DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg
                ''')
        conn.close()
        self.assertEqual(len(result1), len(result0) - 1)

    def test_query_plume_pg_import_sample_template(self):
        """Import des modèles pré-configurés dans la base de données.
        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                query = query_read_meta_template()
                cur.execute(*query)
                result0 = cur.fetchall()
                query = query_plume_pg_import_sample_template('Basique')
                cur.execute(*query)
                query = query_read_meta_template()
                cur.execute(*query)
                result1 = cur.fetchall()
                query = query_plume_pg_import_sample_template(['Basique', 'Classique'])
                cur.execute(*query)
                query = query_read_meta_template()
                cur.execute(*query)
                result2 = cur.fetchall()
                query = query_plume_pg_import_sample_template()
                cur.execute(*query)
                query = query_read_meta_template()
                cur.execute(*query)
                result3 = cur.fetchall()
                cur.execute('''
                    DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg
                ''')
        conn.close()
        self.assertFalse(result0)
        self.assertTrue(result1)
        self.assertEqual(len(result1), 1)
        self.assertEqual(len(result2), 2)
        self.assertGreater(len(result3), 2)

    def test_query_plume_pg_create(self):
        """Activation de PlumePg via Plume.
        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('DROP EXTENSION plume_pg')
                cur.execute(*query_plume_pg_status())
                status1 = cur.fetchone()
                cur.execute(*query_plume_pg_create())
                cur.execute(*query_plume_pg_status())
                status2 = cur.fetchone()
                cur.execute(*query_exists_extension('plume_pg'))
                exists_plume_pg = cur.fetchone()
        self.assertTrue('CREATE' in status1[0])
        self.assertTrue('DROP' in status2[0])
        self.assertTrue(exists_plume_pg[0])

    def test_query_plume_pg_drop(self):
        """Désactivation de PlumePg via Plume.
        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute(*query_plume_pg_status())
                status1 = cur.fetchone()
                cur.execute(*query_plume_pg_drop())
                cur.execute(*query_plume_pg_status())
                status2 = cur.fetchone()
                cur.execute(*query_exists_extension('plume_pg'))
                exists_plume_pg = cur.fetchone()
                cur.execute(*query_plume_pg_create())
        self.assertTrue('DROP' in status1[0])
        self.assertTrue('CREATE' in status2[0])
        self.assertFalse(exists_plume_pg[0])

    def test_query_plume_pg_update(self):
        """Mise à jour de PlumePg via Plume.
        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('''
                    DROP EXTENSION plume_pg ;
                    CREATE EXTENSION plume_pg VERSION '0.1.1'
                ''')
                cur.execute(*query_plume_pg_check())
                ok_plume_pg1 = cur.fetchone()
                cur.execute(*query_plume_pg_status())
                status1 = cur.fetchone()
                cur.execute(*query_plume_pg_update())
                cur.execute(*query_plume_pg_status())
                status2 = cur.fetchone()
                cur.execute(*query_plume_pg_check())
                ok_plume_pg2 = cur.fetchone()
        self.assertFalse(ok_plume_pg1[0])
        self.assertTrue('UPDATE' in status1[0])
        self.assertFalse('UPDATE' in status2[0])
        self.assertTrue(ok_plume_pg2[0])

    def test_query_stamp_recording_enable(self):
        """Activation par Plume du suivi des dates par PlumePg.
        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute(*query_plume_pg_status())
                status1 = cur.fetchone()
                cur.execute('ALTER EVENT TRIGGER plume_stamp_table_drop ENABLE')
                cur.execute(*query_plume_pg_status())
                status2 = cur.fetchone()
                cur.execute(*query_stamp_recording_enable())
                cur.execute(*query_plume_pg_status())
                status3 = cur.fetchone()
                cur.execute('''
                    DROP EXTENSION plume_pg ;
                    CREATE EXTENSION plume_pg
                ''')
        self.assertTrue('STAMP RECORDING ENABLE' in status1[0])
        self.assertFalse('STAMP RECORDING DISABLE' in status1[0])
        self.assertTrue('STAMP RECORDING ENABLE' in status2[0])
        self.assertTrue('STAMP RECORDING DISABLE' in status2[0])
        self.assertFalse('STAMP RECORDING ENABLE' in status3[0])
        self.assertTrue('STAMP RECORDING DISABLE' in status3[0])

    def test_query_stamp_recording_disable(self):
        """Désactivation par Plume du suivi des dates par PlumePg.
        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('''
                    ALTER EVENT TRIGGER plume_stamp_table_creation ENABLE ;
                    ALTER EVENT TRIGGER plume_stamp_table_modification ENABLE ;
                    ALTER EVENT TRIGGER plume_stamp_table_drop ENABLE
                ''')
                cur.execute(*query_plume_pg_status())
                status1 = cur.fetchone()
                cur.execute('ALTER EVENT TRIGGER plume_stamp_table_drop DISABLE')
                cur.execute(*query_plume_pg_status())
                status2 = cur.fetchone()
                cur.execute(*query_stamp_recording_disable())
                cur.execute(*query_plume_pg_status())
                status3 = cur.fetchone()
                cur.execute('''
                    DROP EXTENSION plume_pg ;
                    CREATE EXTENSION plume_pg
                ''')
        self.assertFalse('STAMP RECORDING ENABLE' in status1[0])
        self.assertTrue('STAMP RECORDING DISABLE' in status1[0])
        self.assertTrue('STAMP RECORDING ENABLE' in status2[0])
        self.assertTrue('STAMP RECORDING DISABLE' in status2[0])
        self.assertTrue('STAMP RECORDING ENABLE' in status3[0])
        self.assertFalse('STAMP RECORDING DISABLE' in status3[0])

    def test_query_stamp_to_metadata_enable(self):
        """Activation par Plume de la copie automatique des dates enregistrées par PlumePg dans les fiches de métadonnées.
        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute(*query_plume_pg_status())
                status1 = cur.fetchone()
                cur.execute(*query_stamp_to_metadata_enable())
                cur.execute(*query_plume_pg_status())
                status2 = cur.fetchone()
                cur.execute('''
                    DROP EXTENSION plume_pg ;
                    CREATE EXTENSION plume_pg
                ''')
        self.assertTrue('STAMP TO METADATA ENABLE' in status1[0])
        self.assertFalse('STAMP TO METADATA DISABLE' in status1[0])
        self.assertFalse('STAMP TO METADATA ENABLE' in status2[0])
        self.assertTrue('STAMP TO METADATA DISABLE' in status2[0])

    def test_query_stamp_to_metadata_disable(self):
        """Désactivation par Plume de la copie automatique des dates enregistrées par PlumePg dans les fiches de métadonnées.
        """
        conn = psycopg2.connect(PlumePgTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('''
                    ALTER TABLE z_plume.stamp_timestamp
                        ENABLE TRIGGER stamp_timestamp_to_metadata
                ''')
                cur.execute(*query_plume_pg_status())
                status1 = cur.fetchone()
                cur.execute(*query_stamp_to_metadata_disable())
                cur.execute(*query_plume_pg_status())
                status2 = cur.fetchone()
                cur.execute('''
                    DROP EXTENSION plume_pg ;
                    CREATE EXTENSION plume_pg
                ''')
        self.assertFalse('STAMP TO METADATA ENABLE' in status1[0])
        self.assertTrue('STAMP TO METADATA DISABLE' in status1[0])
        self.assertTrue('STAMP TO METADATA ENABLE' in status2[0])
        self.assertFalse('STAMP TO METADATA DISABLE' in status2[0])

if __name__ == '__main__':
    unittest.main()

