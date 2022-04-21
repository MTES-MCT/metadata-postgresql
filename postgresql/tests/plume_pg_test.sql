-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
--
-- PlumePg - Système de gestion des métadonnées locales
-- > Script de recette
--
-- Copyright République Française, 2022.
-- Secrétariat général du Ministère de la transition écologique, du
-- Ministère de la cohésion des territoires et des relations avec les
-- collectivités territoriales et du Ministère de la Mer.
-- Service du numérique.
--
-- contributeurs : Leslie Lemaire (SNUM/UNI/DRC).
-- 
-- mél : drc.uni.snum.sg@developpement-durable.gouv.fr
--
-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
--
-- schéma contenant les objets : z_plume_recette
--
-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


/*

Les tests sont à exécuter par un super-utilisateur sur une base vierge
où ont simplement été installées les extensions pgcrypto et plume_pg.
L'extension asgard doit être disponible sur le serveur.


> Exécution de la recette :

SELECT * FROM z_plume_recette.execute_recette() ;


> Modèle de fonction de test :

-- Function: z_plume_recette.t000()

CREATE OR REPLACE FUNCTION z_plume_recette.t000()
    RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
DECLARE
    e_mssg text ;
    e_detl text ;
BEGIN



    RETURN True ;
    
EXCEPTION WHEN OTHERS OR ASSERT_FAILURE THEN
    GET STACKED DIAGNOSTICS e_mssg = MESSAGE_TEXT,
                            e_detl = PG_EXCEPTION_DETAIL ;
    RAISE NOTICE '%', e_mssg
        USING DETAIL = e_detl ;
        
    RETURN False ;
    
END
$_$;

COMMENT ON FUNCTION z_plume_recette.t000() IS 'PlumePg (recette). TEST : .' ;

*/


-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


-------------------------------------------
------ 0 - SCHEMA z_plume_recette ------
-------------------------------------------

-- SCHEMA: z_plume_recette

CREATE SCHEMA IF NOT EXISTS z_plume_recette ;

COMMENT ON SCHEMA z_plume_recette IS 'PlumePg. Bibliothèque de fonctions pour la recette technique.' ;


----------------------------------
------ 1 - FONCTION CHAPEAU ------
----------------------------------

-- FUNCTION: z_plume_recette.execute_recette()

CREATE OR REPLACE FUNCTION z_plume_recette.execute_recette()
    RETURNS TABLE (test text, description text)
    LANGUAGE plpgsql
    AS $_$
/* OBJET : Exécution de la recette : lance successivement toutes
           les fonctions de tests du schéma z_plume_recette.
APPEL : SELECT * FROM z_plume_recette.execute_recette() ;
ARGUMENTS : néant.
SORTIE : table des tests qui ont échoué. */
DECLARE
    l text[] ;
    test record ;
    succes boolean ;
BEGIN
    SET LOCAL client_min_messages = 'ERROR' ;
    -- empêche l'affichage des messages d'ASGARD
    
    FOR test IN (
            SELECT oid::regprocedure::text AS nom, proname::text AS ref
                FROM pg_catalog.pg_proc
                WHERE pronamespace = 'z_plume_recette'::regnamespace::oid
                    AND proname ~ '^t[0-9]+b*$'
                ORDER BY proname
            ) 
    LOOP
        EXECUTE 'SELECT ' || test.nom
            INTO succes ;
        IF NOT succes OR succes IS NULL
        THEN
            l := array_append(l, test.ref) ;
        END IF ;
    END LOOP ;
    RETURN QUERY
        SELECT
            num,
            substring(
                obj_description(('z_plume_recette.' || num || '()')::regprocedure, 'pg_proc'),
                'TEST.[:].(.*)$'
                )
            FROM unnest(l) AS t (num)
            ORDER BY num ;
END
$_$ ;

COMMENT ON FUNCTION z_plume_recette.execute_recette() IS 'PlumePg (recette). Exécution de la recette.' ;


---------------------------------------
------ 2 - BIBLIOTHÈQUE DE TESTS ------
---------------------------------------

-- Function: z_plume_recette.t001()

CREATE OR REPLACE FUNCTION z_plume_recette.t001()
    RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
DECLARE
    e_mssg text ;
    e_detl text ;
BEGIN

    DROP EXTENSION plume_pg ;
    CREATE EXTENSION plume_pg ;
    
    ASSERT EXISTS (
        SELECT * FROM pg_available_extensions
            WHERE name = 'plume_pg'
                AND installed_version IS NOT NULL
        ) ;

    RETURN True ;
    
EXCEPTION WHEN OTHERS OR ASSERT_FAILURE THEN
    GET STACKED DIAGNOSTICS e_mssg = MESSAGE_TEXT,
                            e_detl = PG_EXCEPTION_DETAIL ;
    RAISE NOTICE '%', e_mssg
        USING DETAIL = e_detl ;
        
    RETURN False ;
    
END
$_$;

COMMENT ON FUNCTION z_plume_recette.t001() IS 'PlumePg (recette). TEST : Désinstallation et ré-installation.' ;


-- Function: z_plume_recette.t002()

CREATE OR REPLACE FUNCTION z_plume_recette.t002()
    RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
DECLARE
    e_mssg text ;
    e_detl text ;
    crea bool ;
    lec text ;
    prod text ;
BEGIN

    DROP EXTENSION plume_pg ;
    
    CREATE EXTENSION asgard ;    
    CREATE EXTENSION plume_pg ;
    
    SELECT creation, producteur, lecteur
        INTO crea, prod, lec
        FROM z_asgard.gestion_schema_usr
        WHERE nom_schema = 'z_plume' ;
    
    ASSERT FOUND, 'échec assertion #1' ;
    ASSERT crea, 'échec assertion #2' ;
    ASSERT prod = 'g_admin', 'échec assertion #3' ;
    ASSERT lec = 'public', 'échec assertion #4' ;
    ASSERT has_table_privilege('g_consult', 'z_plume.meta_template_categories_full', 'SELECT') ;
    
    DROP EXTENSION plume_pg ;
    
    SELECT creation INTO crea
        FROM z_asgard.gestion_schema_usr
        WHERE nom_schema = 'z_plume' ;
        
    ASSERT FOUND, 'échec assertion #5' ;
    ASSERT NOT crea, 'échec assertion #6' ;
    
    DROP EXTENSION asgard ;
    CREATE EXTENSION plume_pg ;
    
    RETURN True ;
    
EXCEPTION WHEN OTHERS OR ASSERT_FAILURE THEN
    GET STACKED DIAGNOSTICS e_mssg = MESSAGE_TEXT,
                            e_detl = PG_EXCEPTION_DETAIL ;
    RAISE NOTICE '%', e_mssg
        USING DETAIL = e_detl ;
        
    RETURN False ;
    
END
$_$;

COMMENT ON FUNCTION z_plume_recette.t002() IS 'PlumePg (recette). TEST : Désinstallation et ré-installation avec ASGARD.' ;


-- Function: z_plume_recette.t003()

CREATE OR REPLACE FUNCTION z_plume_recette.t003()
    RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
DECLARE
    e_mssg text ;
    e_detl text ;
BEGIN

    DROP EXTENSION plume_pg ;
    CREATE EXTENSION plume_pg VERSION '0.0.1' ;
    ALTER EXTENSION plume_pg UPDATE ;

    RETURN True ;
    
EXCEPTION WHEN OTHERS OR ASSERT_FAILURE THEN
    GET STACKED DIAGNOSTICS e_mssg = MESSAGE_TEXT,
                            e_detl = PG_EXCEPTION_DETAIL ;
    RAISE NOTICE '%', e_mssg
        USING DETAIL = e_detl ;
        
    RETURN False ;
    
END
$_$;

COMMENT ON FUNCTION z_plume_recette.t003() IS 'PlumePg (recette). TEST : Installation depuis une version antérieure.' ;


-- Function: z_plume_recette.t004()

CREATE OR REPLACE FUNCTION z_plume_recette.t004()
    RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
DECLARE
    e_mssg text ;
    e_detl text ;
    p text ;
BEGIN

    INSERT INTO z_plume.meta_categorie (label)
        VALUES ('Ma catégorie') ;

    SELECT path INTO p
        FROM z_plume.meta_categorie
        WHERE label = 'Ma catégorie' ;
        
    ASSERT p ~ '^uuid[:][0-9a-z-]{36}$' ;
    
    DELETE FROM z_plume.meta_categorie ;

    RETURN True ;
    
EXCEPTION WHEN OTHERS OR ASSERT_FAILURE THEN
    GET STACKED DIAGNOSTICS e_mssg = MESSAGE_TEXT,
                            e_detl = PG_EXCEPTION_DETAIL ;
    RAISE NOTICE '%', e_mssg
        USING DETAIL = e_detl ;
        
    RETURN False ;
    
END
$_$;

COMMENT ON FUNCTION z_plume_recette.t004() IS 'PlumePg (recette). TEST : Génération des chemins des catégories locales.' ;


-- Function: z_plume_recette.t005()

CREATE OR REPLACE FUNCTION z_plume_recette.t005()
    RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
DECLARE
    e_mssg text ;
    e_detl text ;
BEGIN

    DROP EXTENSION plume_pg ;
    
    CREATE SCHEMA z_plume ;
    CREATE EXTENSION plume_pg ;
    
    DROP EXTENSION plume_pg ;
    
    ASSERT EXISTS (SELECT * FROM pg_namespace WHERE nspname = 'z_plume') ;
    -- le schéma n'est pas supposé être supprimé en même temps
    -- que l'extension lorsqu'il pré-existait.
    
    DROP SCHEMA z_plume ;
    CREATE EXTENSION plume_pg ;

    RETURN True ;
    
EXCEPTION WHEN OTHERS OR ASSERT_FAILURE THEN
    GET STACKED DIAGNOSTICS e_mssg = MESSAGE_TEXT,
                            e_detl = PG_EXCEPTION_DETAIL ;
    RAISE NOTICE '%', e_mssg
        USING DETAIL = e_detl ;
        
    RETURN False ;
    
END
$_$;

COMMENT ON FUNCTION z_plume_recette.t005() IS 'PlumePg (recette). TEST : Désinstallation et ré-installation avec schéma z_plume pré-existant.' ;


-- Function: z_plume_recette.t006()

CREATE OR REPLACE FUNCTION z_plume_recette.t006()
    RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
DECLARE
    e_mssg text ;
    e_detl text ;
BEGIN
	
	-- mime une commande INSERT produite par un
	-- script de restauration.
	-- en changeant le label
	INSERT INTO z_plume.meta_categorie (
        path, origin, label, description, special,
        is_node, datatype, is_long_text, rowspan,
        placeholder, input_mask, is_multiple, unilang,
        is_mandatory, sources, template_order
        ) VALUES
        ('dct:description', 'shared', 'résumé', 'Description du jeu de données.', NULL, false, 'rdf:langString', true, 15, NULL, NULL, true, true, true, NULL, 2) ;
		
	ASSERT (
		SELECT label = 'résumé'
			FROM z_plume.meta_categorie
			WHERE path = 'dct:description'
		) ;

	-- on remet le label initial
	UPDATE z_plume.meta_categorie
		SET label = 'Description'
		WHERE path = 'dct:description' ;

    RETURN True ;
    
EXCEPTION WHEN OTHERS OR ASSERT_FAILURE THEN
    GET STACKED DIAGNOSTICS e_mssg = MESSAGE_TEXT,
                            e_detl = PG_EXCEPTION_DETAIL ;
    RAISE NOTICE '%', e_mssg
        USING DETAIL = e_detl ;
        
    RETURN False ;
    
END
$_$;

COMMENT ON FUNCTION z_plume_recette.t006() IS 'PlumePg (recette). TEST : Restauration des modifications utilisateur dans meta_shared_categorie.' ;


-- Function: z_plume_recette.t007()

CREATE OR REPLACE FUNCTION z_plume_recette.t007()
    RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
DECLARE
    e_mssg text ;
    e_detl text ;
BEGIN

	-- sans schéma ni table :
	ASSERT (
		SELECT z_plume.meta_execute_sql_filter(
			'pg_has_role(''pg_monitor'', ''pg_read_all_stats'', ''USAGE'')',
			'schema',
			'table'
			)
		), 'échec assertion #1' ;
		
	ASSERT (
		SELECT NOT z_plume.meta_execute_sql_filter(
			'pg_has_role(''pg_read_all_stats'', ''pg_monitor'', ''USAGE'')',
			'schema',
			'table'
			)
		), 'échec assertion #2' ;

	-- avec schéma :
	ASSERT (
		SELECT z_plume.meta_execute_sql_filter(
			'$1 ~ ANY(ARRAY[''^r_'', ''^e_''])',
			'r_ign_bdtopo',
			'table'
			)
		), 'échec assertion #3' ;
		
	ASSERT (
		SELECT NOT z_plume.meta_execute_sql_filter(
			'$1 ~ ANY(ARRAY[''^r_'', ''^e_''])',
			'schema',
			'table'
			)
		), 'échec assertion #4' ;
		
	-- avec schéma et table :
	ASSERT (
		SELECT z_plume.meta_execute_sql_filter(
			'$1 ~ ANY(ARRAY[''^r_'', ''^e_'']) AND $2 ~ ''_fr$''',
			'r_ign_admin_express',
			'region_fr'
			)
		), 'échec assertion #5' ;
		
	ASSERT (
		SELECT NOT z_plume.meta_execute_sql_filter(
			'$1 ~ ANY(ARRAY[''^r_'', ''^e_'']) AND $2 ~ ''_fr$''',
			'r_ign_admin_express',
			NULL
			)
		), 'échec assertion #6' ;
		-- NB. la fonction applique un coalesce '' sur le nom 
		-- de la table.
	
	-- pas de filtre :
	ASSERT (
		SELECT z_plume.meta_execute_sql_filter(
			NULL,
			'schema',
			'table'
			) IS NULL
		), 'échec assertion #7' ;
		
	ASSERT (
		SELECT z_plume.meta_execute_sql_filter(
			'',
			'schema',
			'table'
			) IS NULL
		), 'échec assertion #8' ;
	
	-- avec un filtre invalide :
	ASSERT (
		SELECT z_plume.meta_execute_sql_filter(
			'n''importe quoi',
			'schema',
			'table'
			) IS NULL
		), 'échec assertion #9' ;


    RETURN True ;
    
EXCEPTION WHEN OTHERS OR ASSERT_FAILURE THEN
    GET STACKED DIAGNOSTICS e_mssg = MESSAGE_TEXT,
                            e_detl = PG_EXCEPTION_DETAIL ;
    RAISE NOTICE '%', e_mssg
        USING DETAIL = e_detl ;
        
    RETURN False ;
    
END
$_$;

COMMENT ON FUNCTION z_plume_recette.t007() IS 'PlumePg (recette). TEST : Exécution des filtres SQL par meta_execute_sql_filter.' ;



-- Function: z_plume_recette.t008()

CREATE OR REPLACE FUNCTION z_plume_recette.t008()
    RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
DECLARE
    res record ;
    e_mssg text ;
    e_detl text ;
BEGIN

	-- import d'un modèle
	SELECT *
        INTO res
        FROM z_plume.meta_import_sample_template('Basique') ;
        
    ASSERT res.label = 'Basique' AND res.summary = 'created',
        'échec assertion #0' ;
	
	ASSERT (
		SELECT count(*)
			FROM z_plume.meta_template_categories_full
			WHERE tpl_label = 'Basique'
		) > 0, 'échec assertion #1' ;
		
	DELETE FROM z_plume.meta_template
		WHERE tpl_label = 'Basique' ;
		
	-- import de tous les modèles
	PERFORM z_plume.meta_import_sample_template() ;
	
	ASSERT (
		SELECT count(*)
			FROM z_plume.meta_template_categories_full
			WHERE tpl_label = 'Basique'
		) > 0, 'échec assertion #2' ;
		
	ASSERT (
		SELECT count(*)
			FROM z_plume.meta_template
		) > 1, 'échec assertion #3' ;
	
	-- réinitialisation
	UPDATE z_plume.meta_template
	    SET sql_filter = 'True'
		WHERE tpl_label = 'Basique' ;
		
	SELECT *
        INTO res
        FROM z_plume.meta_import_sample_template('Basique') ;
        
    ASSERT res.label = 'Basique' AND res.summary = 'updated',
        'échec assertion #4' ;
	
	ASSERT (
		SELECT sql_filter IS NULL
			FROM z_plume.meta_template
			WHERE tpl_label = 'Basique'
		), 'échec assertion #5' ;
		
	DROP EXTENSION plume_pg ;
	CREATE EXTENSION plume_pg ;

    RETURN True ;
    
EXCEPTION WHEN OTHERS OR ASSERT_FAILURE THEN
    GET STACKED DIAGNOSTICS e_mssg = MESSAGE_TEXT,
                            e_detl = PG_EXCEPTION_DETAIL ;
    RAISE NOTICE '%', e_mssg
        USING DETAIL = e_detl ;
        
    RETURN False ;
    
END
$_$;

COMMENT ON FUNCTION z_plume_recette.t008() IS 'PlumePg (recette). TEST : Insertion des modèles pré-configurés avec meta_import_sample_template.' ;


-- Function: z_plume_recette.t009()

CREATE OR REPLACE FUNCTION z_plume_recette.t009()
    RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
DECLARE
    e_mssg text ;
    e_detl text ;
BEGIN

    UPDATE z_plume.meta_categorie
        SET geo_tools = ARRAY['show', 'point']
        WHERE path = 'dct:title' ;
    
    ASSERT FOUND, 'échec assertion #1' ;

    UPDATE z_plume.meta_categorie
        SET compute = ARRAY['auto']
        WHERE path = 'dct:title' ;
    
    ASSERT FOUND, 'échec assertion #2' ;

    DROP EXTENSION plume_pg ;
	CREATE EXTENSION plume_pg ;

    RETURN True ;
    
EXCEPTION WHEN OTHERS OR ASSERT_FAILURE THEN
    GET STACKED DIAGNOSTICS e_mssg = MESSAGE_TEXT,
                            e_detl = PG_EXCEPTION_DETAIL ;
    RAISE NOTICE '%', e_mssg
        USING DETAIL = e_detl ;
        
    RETURN False ;
    
END
$_$;

COMMENT ON FUNCTION z_plume_recette.t009() IS 'PlumePg (recette). TEST : Cast automatique du type text[] en meta_geo_tool[] et meta_compute[].' ;


-- Function: z_plume_recette.t010()

CREATE OR REPLACE FUNCTION z_plume_recette.t010()
    RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
DECLARE
    f text ;
    i int ;
    e_mssg text ;
    e_detl text ;
BEGIN

    -- expression régulière valide
    SELECT string_agg(a, '')
        INTO f
        FROM z_plume.meta_regexp_matches('A..b-/c!', '([a-z])([-])?', 'gi') AS t(a) ;

    ASSERT f = 'Ab-c', 'échec assertion #1' ;

    SELECT count(*)
        INTO i
        FROM z_plume.meta_regexp_matches('A..b-/c!', '([a-z])([-])?', 'gi') ;

    ASSERT i = 4, 'échec assertion #2' ;

    -- expression régulière invalide (parenthèses déséquilibrées)
    SELECT a
        INTO f
        FROM z_plume.meta_regexp_matches('A..b-/c!', '(([a-z])([-])?', 'gi') AS t(a) ;

    ASSERT f IS NULL, 'échec assertion #3' ;
    
    -- pas de texte
    SELECT a
        INTO f
        FROM z_plume.meta_regexp_matches(NULL, '([a-z])([-])?', 'gi') AS t(a) ;

    ASSERT f IS NULL, 'échec assertion #4' ;
    
    -- flag inconnu
    SELECT a
        INTO f
        FROM z_plume.meta_regexp_matches('', '([a-z])([-])?', 'z') AS t(a) ;

    ASSERT f IS NULL, 'échec assertion #5' ;
    
    -- pas d'expression régulière
    SELECT a
        INTO f
        FROM z_plume.meta_regexp_matches('A..b-/c!', '', 'gi') AS t(a) ;

    ASSERT f IS NULL, 'échec assertion #6' ;
    
    SELECT a
        INTO f
        FROM z_plume.meta_regexp_matches('A..b-/c!', NULL, 'gi') AS t(a) ;

    ASSERT f IS NULL, 'échec assertion #7' ;

    -- expression régulière valide sans flag
    SELECT string_agg(a, '')
        INTO f
        FROM z_plume.meta_regexp_matches('A..b-/c!', '([a-z])([-])?') AS t(a) ;

    ASSERT f = 'b-', 'échec assertion #8' ;

    RETURN True ;
    
EXCEPTION WHEN OTHERS OR ASSERT_FAILURE THEN
    GET STACKED DIAGNOSTICS e_mssg = MESSAGE_TEXT,
                            e_detl = PG_EXCEPTION_DETAIL ;
    RAISE NOTICE '%', e_mssg
        USING DETAIL = e_detl ;
        
    RETURN False ;
    
END
$_$;

COMMENT ON FUNCTION z_plume_recette.t010() IS 'PlumePg (recette). TEST : Extraction de fragments d''un texte avec meta_regexp_matches(text, text, text).' ;


-- Function: z_plume_recette.t011()

CREATE OR REPLACE FUNCTION z_plume_recette.t011()
    RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
DECLARE
	t text ;
    e_mssg text ;
    e_detl text ;
BEGIN

	CREATE TABLE z_plume.table_test () ;
	
	SELECT z_plume.meta_ante_post_description(
		'z_plume.table_test'::regclass, 'pg_class')
		INTO t ;
	
	ASSERT t IS NULL, 'échec assertion #1' ;
	
	COMMENT ON TABLE z_plume.table_test IS 'Une description.' ;
	
	SELECT z_plume.meta_ante_post_description(
		'z_plume.table_test'::regclass, 'pg_class')
		INTO t ;
	
	ASSERT t = 'Une description.', 'échec assertion #2' ;
	
	COMMENT ON TABLE z_plume.table_test IS 'Une autre description.<METADATA></METADATA>' ;
	
	SELECT z_plume.meta_ante_post_description(
		'z_plume.table_test'::regclass, 'pg_class')
		INTO t ;
	
	ASSERT t = 'Une autre description.', 'échec assertion #3' ;
	
	COMMENT ON TABLE z_plume.table_test IS 'Encore une <METADATA></METADATA>description.' ;
	
	SELECT z_plume.meta_ante_post_description(
		'z_plume.table_test'::regclass, 'pg_class')
		INTO t ;
	
	ASSERT t = 'Encore une description.', 'échec assertion #4' ;
	
	COMMENT ON TABLE z_plume.table_test IS 'Et encore une <METADATA>
		bla
		bla
		bla
		</METADATA>description.' ;
	
	SELECT z_plume.meta_ante_post_description(
		'z_plume.table_test'::regclass, 'pg_class')
		INTO t ;
	
	ASSERT t = 'Et encore une description.', 'échec assertion #5' ;
	
	DROP TABLE z_plume.table_test ;

    RETURN True ;
    
EXCEPTION WHEN OTHERS OR ASSERT_FAILURE THEN
    GET STACKED DIAGNOSTICS e_mssg = MESSAGE_TEXT,
                            e_detl = PG_EXCEPTION_DETAIL ;
    RAISE NOTICE '%', e_mssg
        USING DETAIL = e_detl ;
        
    RETURN False ;
    
END
$_$;

COMMENT ON FUNCTION z_plume_recette.t011() IS 'PlumePg (recette). TEST : Récupération d''un descriptif expurgé des métadonnées avec meta_ante_post_description(oid, text).' ;


-- Function: z_plume_recette.t012()

CREATE OR REPLACE FUNCTION z_plume_recette.t012()
    RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
DECLARE
    n int ;
    t text ;
    i1 oid ;
    i2 oid ;
    d1 timestamp with time zone ;
    d2 timestamp with time zone ;
    e_mssg text ;
    e_detl text ;
BEGIN

    CREATE TABLE z_plume_recette.test_stamp_0 () ;
    
    ------ tous event triggers inactifs ------
    
    SELECT count(*) INTO n FROM z_plume.stamp_timestamp ;
    ASSERT n = 0, 'échec assertion #1' ;
    
    CREATE TABLE z_plume_recette.test_stamp_1 (id int PRIMARY KEY) ;
    SELECT count(*) INTO n FROM z_plume.stamp_timestamp ;
    ASSERT n = 0, 'échec assertion #2' ;
    
    ALTER TABLE z_plume_recette.test_stamp_1 ADD COLUMN txt text ;
    SELECT count(*) INTO n FROM z_plume.stamp_timestamp ;
    ASSERT n = 0, 'échec assertion #3' ;

    INSERT INTO z_plume_recette.test_stamp_1 (id, txt) VALUES (4, '#4') ;
    SELECT txt INTO t FROM z_plume_recette.test_stamp_1 ;
    ASSERT t = '#4', 'échec assertion #4-a' ;
    SELECT count(*) INTO n FROM z_plume.stamp_timestamp ;
    ASSERT n = 0, 'échec assertion #4-b' ;

    DROP TABLE z_plume_recette.test_stamp_1 ;
    SELECT count(*) INTO n FROM z_plume.stamp_timestamp ;
    ASSERT n = 0, 'échec assertion #5' ;
    
    ------ avec plume_stamp_modification ------
    
    ALTER EVENT TRIGGER plume_stamp_modification ENABLE ;
    
    CREATE TABLE z_plume_recette.test_stamp_1 (id int PRIMARY KEY) ;
    SELECT count(*) INTO n FROM z_plume.stamp_timestamp ;
    ASSERT n = 0, 'échec assertion #6-a' ;
    SELECT count(*) INTO n FROM pg_trigger
        WHERE tgrelid = 'z_plume_recette.test_stamp_1'::regclass
            AND tgname = 'plume_stamp_action' ;
    ASSERT n = 0, 'échec assertion #6-b' ;

    PERFORM z_plume.stamp_create_trigger('z_plume_recette.test_stamp_1'::regclass) ;
    ALTER TABLE z_plume_recette.test_stamp_1 ADD COLUMN txt text ;
    SELECT created, modified  INTO d1, d2
        FROM z_plume.stamp_timestamp
        WHERE relid = 'z_plume_recette.test_stamp_1'::regclass ;
    ASSERT d1 IS NULL, 'échec assertion #7-a' ;
    ASSERT d2 IS NOT NULL, 'échec assertion #7-b' ;
    SELECT count(*) INTO n FROM pg_trigger
        WHERE tgrelid = 'z_plume_recette.test_stamp_1'::regclass
            AND tgname = 'plume_stamp_action' ;
    ASSERT n = 1, 'échec assertion #7-c' ;

    UPDATE z_plume.stamp_timestamp SET modified = NULL ;

    INSERT INTO z_plume_recette.test_stamp_1 (id, txt) VALUES (8, '#8') ;
    SELECT txt INTO t FROM z_plume_recette.test_stamp_1 ;
    ASSERT t = '#8', 'échec assertion #8-a' ;
    SELECT created, modified INTO d1, d2
        FROM z_plume.stamp_timestamp
        WHERE relid = 'z_plume_recette.test_stamp_1'::regclass ;
    ASSERT d1 IS NULL, 'échec assertion #8-b' ;
    ASSERT d2 IS NOT NULL, 'échec assertion #8-c' ;

    ------ avec plume_stamp_creation ------
    
    ALTER EVENT TRIGGER plume_stamp_creation ENABLE ;
    
    CREATE TABLE z_plume_recette.test_stamp_2 (id int PRIMARY KEY) ;
    SELECT created, modified  INTO d1, d2
        FROM z_plume.stamp_timestamp
        WHERE relid = 'z_plume_recette.test_stamp_2'::regclass ;
    ASSERT d1 IS NOT NULL, 'échec assertion #9-a' ;
    ASSERT d2 IS NULL, 'échec assertion #9-b' ;
    
    UPDATE z_plume.stamp_timestamp
        SET modified = NULL, created = NULL
        WHERE relid = 'z_plume_recette.test_stamp_2'::regclass ;
    
    INSERT INTO z_plume_recette.test_stamp_2 (id) VALUES (10) ;
    SELECT id INTO n FROM z_plume_recette.test_stamp_2 ;
    ASSERT n = 10, 'échec assertion #10-a' ;
    SELECT created, modified  INTO d1, d2
        FROM z_plume.stamp_timestamp
        WHERE relid = 'z_plume_recette.test_stamp_2'::regclass ;
    ASSERT d1 IS NULL, 'échec assertion #10-b' ;
    ASSERT d2 IS NOT NULL, 'échec assertion #10-c' ;
    
    UPDATE z_plume.stamp_timestamp
        SET modified = NULL
        WHERE relid = 'z_plume_recette.test_stamp_2'::regclass ;

    ALTER TABLE z_plume_recette.test_stamp_2 ADD COLUMN txt text ;
    SELECT created, modified  INTO d1, d2
        FROM z_plume.stamp_timestamp
        WHERE relid = 'z_plume_recette.test_stamp_1'::regclass ;
    ASSERT d1 IS NULL, 'échec assertion #11-a' ;
    ASSERT d2 IS NOT NULL, 'échec assertion #11-b' ;
    
    UPDATE z_plume.stamp_timestamp
        SET modified = NULL
        WHERE relid = 'z_plume_recette.test_stamp_2'::regclass ;

    UPDATE z_plume_recette.test_stamp_2 SET txt = '#12' ;
    SELECT txt INTO t FROM z_plume_recette.test_stamp_2 ;
    ASSERT t = '#12', 'échec assertion #12-a' ;
    SELECT created, modified  INTO d1, d2
        FROM z_plume.stamp_timestamp
        WHERE relid = 'z_plume_recette.test_stamp_2'::regclass ;
    ASSERT d1 IS NULL, 'échec assertion #12-b' ;
    ASSERT d2 IS NOT NULL, 'échec assertion #12-c' ;
    
    UPDATE z_plume.stamp_timestamp
        SET modified = NULL
        WHERE relid = 'z_plume_recette.test_stamp_2'::regclass ;
    
    DELETE FROM z_plume_recette.test_stamp_2 WHERE txt = '#13' ;
    SELECT count(*) INTO n FROM z_plume_recette.test_stamp_2 ;
    ASSERT n = 1, 'échec assertion #13-a' ;
    SELECT created, modified  INTO d1, d2
        FROM z_plume.stamp_timestamp
        WHERE relid = 'z_plume_recette.test_stamp_1'::regclass ;
    ASSERT d1 IS NULL, 'échec assertion #13-b' ;
    ASSERT d2 IS NOT NULL, 'échec assertion #13-c' ;

    UPDATE z_plume.stamp_timestamp
        SET modified = NULL
        WHERE relid = 'z_plume_recette.test_stamp_2'::regclass ;

    TRUNCATE z_plume_recette.test_stamp_2 ;
    SELECT count(*) INTO n FROM z_plume_recette.test_stamp_2 ;
    ASSERT n = 0, 'échec assertion #14-a' ;
    SELECT created, modified  INTO d1, d2
        FROM z_plume.stamp_timestamp
        WHERE relid = 'z_plume_recette.test_stamp_2'::regclass ;
    ASSERT d1 IS NULL, 'échec assertion #14-b' ;
    ASSERT d2 IS NOT NULL, 'échec assertion #14-c' ;

    i2 = 'z_plume_recette.test_stamp_2'::regclass::oid ;
    DROP TABLE z_plume_recette.test_stamp_2 ;
    SELECT count(*) INTO n FROM z_plume.stamp_timestamp
        WHERE relid = i2 ;
    ASSERT n = 1, 'échec assertion #15-a' ;
    SELECT count(*) INTO n FROM z_plume.stamp_timestamp
        WHERE relid = 'z_plume_recette.test_stamp_1'::regclass ;
    ASSERT n = 1, 'échec assertion #15-b' ;

    ------ avec plume_stamp_drop ------
    
    ALTER EVENT TRIGGER plume_stamp_drop ENABLE ;
    
    i1 = 'z_plume_recette.test_stamp_1'::regclass::oid ;
    DROP TABLE z_plume_recette.test_stamp_1 ;
    SELECT count(*) INTO n FROM z_plume.stamp_timestamp
        WHERE relid = i2 ;
    ASSERT n = 1, 'échec assertion #16-a' ;
    SELECT count(*) INTO n FROM z_plume.stamp_timestamp
        WHERE relid = i1 ;
    ASSERT n = 0, 'échec assertion #16-b' ;

    DROP TABLE z_plume_recette.test_stamp_0 ;
    
    TRUNCATE z_plume.stamp_timestamp ;
    ALTER EVENT TRIGGER plume_stamp_drop DISABLE ;
    ALTER EVENT TRIGGER plume_stamp_modification DISABLE ;
    ALTER EVENT TRIGGER plume_stamp_creation DISABLE ;

    RETURN True ;
    
EXCEPTION WHEN OTHERS OR ASSERT_FAILURE THEN
    GET STACKED DIAGNOSTICS e_mssg = MESSAGE_TEXT,
                            e_detl = PG_EXCEPTION_DETAIL ;
    RAISE NOTICE '%', e_mssg
        USING DETAIL = e_detl ;
        
    RETURN False ;
    
END
$_$;

COMMENT ON FUNCTION z_plume_recette.t012() IS 'PlumePg (recette). TEST : Fonctionnement général des tampons de date.' ;


-- Function: z_plume_recette.t013()

CREATE OR REPLACE FUNCTION z_plume_recette.t013()
    RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
DECLARE
    d timestamp with time zone ;
    n int ;
    i oid ;
    b boolean ;
    e_mssg text ;
    e_detl text ;
BEGIN

    CREATE SCHEMA c_librairie ;
    CREATE TABLE c_librairie.test_stamp (id int PRIMARY KEY) ;

    ALTER EVENT TRIGGER plume_stamp_creation ENABLE ;
    ALTER EVENT TRIGGER plume_stamp_modification ENABLE ;
    ALTER EVENT TRIGGER plume_stamp_drop ENABLE ;

    CREATE EXTENSION asgard ;
    CREATE ROLE g_stamp_edit ;
    
    CREATE SCHEMA c_bibliotheque ;
    PERFORM z_asgard.asgard_initialise_schema('c_librairie') ;
    UPDATE z_asgard.gestion_schema_usr
        SET editeur = 'g_stamp_edit',
            producteur = 'g_admin'
        WHERE nom_schema IN ('c_bibliotheque', 'c_librairie') ;
    
    SET ROLE g_admin ;
    CREATE TABLE c_bibliotheque.test_stamp (id int PRIMARY KEY) ;
    
    RESET ROLE ;
    SELECT created INTO d
        FROM z_plume.stamp_timestamp
        WHERE relid = 'c_bibliotheque.test_stamp'::regclass ;
    ASSERT d IS NOT NULL, 'échec assertion #1' ;
    
    SET ROLE g_admin ;
    ALTER TABLE c_bibliotheque.test_stamp ADD COLUMN txt text ;
    
    RESET ROLE ;
    SELECT modified INTO d
        FROM z_plume.stamp_timestamp
        WHERE relid = 'c_bibliotheque.test_stamp'::regclass ;
    ASSERT d IS NOT NULL, 'échec assertion #2' ;
    
    UPDATE z_plume.stamp_timestamp
        SET modified = NULL
        WHERE relid = 'c_bibliotheque.test_stamp'::regclass ;
    
    SET ROLE g_stamp_edit ;
    INSERT INTO c_bibliotheque.test_stamp (id, txt) VALUES (3, '#3') ;
    
    RESET ROLE ;
    SELECT modified INTO d
        FROM z_plume.stamp_timestamp
        WHERE relid = 'c_bibliotheque.test_stamp'::regclass ;
    ASSERT d IS NOT NULL, 'échec assertion #3-a' ;
    SELECT count(*) INTO n FROM c_bibliotheque.test_stamp ;
    ASSERT n = 1, 'échec assertion #3-b' ;
    
    SET ROLE g_stamp_edit ;
    UPDATE z_plume.stamp_timestamp SET modified = NULL ;
    GET DIAGNOSTICS n = ROW_COUNT ;
    ASSERT n = 0, 'échec assertion #4' ;  
    
    SET ROLE g_stamp_edit ;
    SELECT z_plume.stamp_create_trigger('c_librairie.test_stamp'::regclass)
        INTO b ;
    
    ASSERT NOT b, 'échec assertion #5-a' ; 
    SELECT count(*) INTO n FROM pg_trigger
        WHERE tgrelid = 'c_librairie.test_stamp'::regclass
            AND tgname = 'plume_stamp_action' ;
    ASSERT n = 0, 'échec assertion #5-b' ;
    
    SET ROLE g_admin ;
    PERFORM z_plume.stamp_create_trigger('c_librairie.test_stamp'::regclass) ;
    ALTER TABLE c_librairie.test_stamp ADD COLUMN txt text ;
    
    SELECT modified INTO d
        FROM z_plume.stamp_timestamp
        WHERE relid = 'c_librairie.test_stamp'::regclass ;
    ASSERT d IS NOT NULL, 'échec assertion #6-a' ;
    SELECT count(*) INTO n FROM pg_trigger
        WHERE tgrelid = 'c_librairie.test_stamp'::regclass
            AND tgname = 'plume_stamp_action' ;
    ASSERT n = 1, 'échec assertion #6-b' ;
    
    i = 'c_bibliotheque.test_stamp'::regclass::oid ;
    DROP TABLE c_bibliotheque.test_stamp ;
    
    SELECT count(*) INTO n
        FROM z_plume.stamp_timestamp
        WHERE relid = i ;
    ASSERT n = 0, 'échec assertion #7' ;
    
    RESET ROLE ;
    ALTER EVENT TRIGGER plume_stamp_drop DISABLE ;
    
    SET ROLE g_admin ;
    i = 'c_librairie.test_stamp'::regclass::oid ;
    DROP TABLE c_librairie.test_stamp ;
    
    SELECT count(*) INTO n
        FROM z_plume.stamp_timestamp
        WHERE relid = i ;
    ASSERT n = 1, 'échec assertion #8' ;
    
    SELECT z_plume.stamp_clean_timestamp() INTO n ;
    ASSERT n = 1, 'échec assertion #9' ;
    
    RESET ROLE ;
    DROP EXTENSION asgard ;
    DROP SCHEMA c_bibliotheque CASCADE ;
    DROP SCHEMA c_librairie CASCADE ;
    DROP ROLE g_stamp_edit ;

    TRUNCATE z_plume.stamp_timestamp ;
    ALTER EVENT TRIGGER plume_stamp_drop DISABLE ;
    ALTER EVENT TRIGGER plume_stamp_modification DISABLE ;
    ALTER EVENT TRIGGER plume_stamp_creation DISABLE ;

    RETURN True ;
    
EXCEPTION WHEN OTHERS OR ASSERT_FAILURE THEN
    GET STACKED DIAGNOSTICS e_mssg = MESSAGE_TEXT,
                            e_detl = PG_EXCEPTION_DETAIL ;
    RAISE NOTICE '%', e_mssg
        USING DETAIL = e_detl ;
        
    RETURN False ;
    
END
$_$;

COMMENT ON FUNCTION z_plume_recette.t013() IS 'PlumePg (recette). TEST : Tampons de date et privilèges.' ;

