-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
--
-- Système de gestion des métadonnées locales
-- > Script de recette
--
-- Copyright République Française, 2020-2021.
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
-- schéma contenant les objets : z_metadata_recette
--
-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


/*

Les tests sont à exécuter par un super-utilisateur sur une base vierge
où ont simplement été installées les extensions pgcrypto et metadata.
L'extension asgard doit être disponible sur le serveur.


> Exécution de la recette :

SELECT * FROM z_metadata_recette.execute_recette() ;


> Modèle de fonction de test :

-- Function: z_metadata_recette.t000()

CREATE OR REPLACE FUNCTION z_metadata_recette.t000()
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

COMMENT ON FUNCTION z_metadata_recette.t000() IS 'Métadonnées (recette). TEST : .' ;

*/


-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


-------------------------------------------
------ 0 - SCHEMA z_metadata_recette ------
-------------------------------------------

-- SCHEMA: z_metadata_recette

CREATE SCHEMA IF NOT EXISTS z_metadata_recette ;

COMMENT ON SCHEMA z_metadata_recette IS 'Métadonnées. Bibliothèque de fonctions pour la recette technique.' ;


----------------------------------
------ 1 - FONCTION CHAPEAU ------
----------------------------------

-- FUNCTION: z_metadata_recette.execute_recette()

CREATE OR REPLACE FUNCTION z_metadata_recette.execute_recette()
    RETURNS TABLE (test text, description text)
    LANGUAGE plpgsql
    AS $_$
/* OBJET : Exécution de la recette : lance successivement toutes
           les fonctions de tests du schéma z_metadata_recette.
APPEL : SELECT * FROM z_metadata_recette.execute_recette() ;
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
                WHERE pronamespace = 'z_metadata_recette'::regnamespace::oid
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
                obj_description(('z_metadata_recette.' || num || '()')::regprocedure, 'pg_proc'),
                'TEST.[:].(.*)$'
                )
            FROM unnest(l) AS t (num)
            ORDER BY num ;
END
$_$ ;

COMMENT ON FUNCTION z_metadata_recette.execute_recette() IS 'Métadonnées (recette). Exécution de la recette.' ;


---------------------------------------
------ 2 - BIBLIOTHÈQUE DE TESTS ------
---------------------------------------

-- Function: z_metadata_recette.t001()

CREATE OR REPLACE FUNCTION z_metadata_recette.t001()
    RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
DECLARE
   e_mssg text ;
   e_detl text ;
BEGIN

    DROP EXTENSION metadata ;
    CREATE EXTENSION metadata ;
    
    ASSERT EXISTS (
        SELECT * FROM pg_available_extensions
            WHERE name = 'metadata'
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

COMMENT ON FUNCTION z_metadata_recette.t001() IS 'Métadonnées (recette). TEST : Désinstallation et ré-installation.' ;


-- Function: z_metadata_recette.t002()

CREATE OR REPLACE FUNCTION z_metadata_recette.t002()
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

    DROP EXTENSION metadata ;
    
    CREATE EXTENSION asgard ;
    SET ROLE g_admin ;
    
    CREATE EXTENSION metadata ;
    
    SELECT creation, producteur, lecteur
        INTO crea, prod, lec
        FROM z_asgard.gestion_schema_usr
        WHERE nom_schema = 'z_metadata' ;
    
    ASSERT FOUND, 'échec assertion #1' ;
    ASSERT crea, 'échec assertion #2' ;
    ASSERT prod = 'g_admin', 'échec assertion #3' ;
    ASSERT lec = 'g_consult', 'échec assertion #4' ;
    ASSERT has_table_privilege('g_consult', 'z_metadata.meta_template_categories_full', 'SELECT') ;
    
    DROP EXTENSION metadata ;
    
    SELECT creation INTO crea
        FROM z_asgard.gestion_schema_usr
        WHERE nom_schema = 'z_metadata' ;
        
    ASSERT FOUND, 'échec assertion #5' ;
    ASSERT NOT crea, 'échec assertion #6' ;
    
    RESET ROLE ;
    DROP EXTENSION asgard ;
    CREATE EXTENSION metadata ;
    
    RETURN True ;
    
EXCEPTION WHEN OTHERS OR ASSERT_FAILURE THEN
    GET STACKED DIAGNOSTICS e_mssg = MESSAGE_TEXT,
                            e_detl = PG_EXCEPTION_DETAIL ;
    RAISE NOTICE '%', e_mssg
        USING DETAIL = e_detl ;
        
    RETURN False ;
    
END
$_$;

COMMENT ON FUNCTION z_metadata_recette.t002() IS 'Métadonnées (recette). TEST : Désinstallation et ré-installation avec ASGARD et par g_admin.' ;


-- Function: z_metadata_recette.t003()

CREATE OR REPLACE FUNCTION z_metadata_recette.t003()
    RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
DECLARE
   e_mssg text ;
   e_detl text ;
BEGIN

    DROP EXTENSION metadata ;
    CREATE EXTENSION metadata VERSION '0.0.1' ;
    ALTER EXTENSION metadata UPDATE ;

    RETURN True ;
    
EXCEPTION WHEN OTHERS OR ASSERT_FAILURE THEN
    GET STACKED DIAGNOSTICS e_mssg = MESSAGE_TEXT,
                            e_detl = PG_EXCEPTION_DETAIL ;
    RAISE NOTICE '%', e_mssg
        USING DETAIL = e_detl ;
        
    RETURN False ;
    
END
$_$;

COMMENT ON FUNCTION z_metadata_recette.t003() IS 'Métadonnées (recette). TEST : Installation depuis une version antérieure.' ;


-- Function: z_metadata_recette.t004()

CREATE OR REPLACE FUNCTION z_metadata_recette.t004()
    RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
DECLARE
   e_mssg text ;
   e_detl text ;
   p text ;
BEGIN

    INSERT INTO z_metadata.meta_categorie (cat_label)
        VALUES ('Ma catégorie') ;

    SELECT path INTO p
        FROM z_metadata.meta_categorie
        WHERE cat_label = 'Ma catégorie' ;
        
    ASSERT p ~ '^[<]urn[:]uuid[:][0-9a-z-]{36}[>]$' ;
    
    DELETE FROM z_metadata.meta_categorie ;

    RETURN True ;
    
EXCEPTION WHEN OTHERS OR ASSERT_FAILURE THEN
    GET STACKED DIAGNOSTICS e_mssg = MESSAGE_TEXT,
                            e_detl = PG_EXCEPTION_DETAIL ;
    RAISE NOTICE '%', e_mssg
        USING DETAIL = e_detl ;
        
    RETURN False ;
    
END
$_$;

COMMENT ON FUNCTION z_metadata_recette.t004() IS 'Métadonnées (recette). TEST : Génération des chemins des catégories locales.' ;


-- Function: z_metadata_recette.t005()

CREATE OR REPLACE FUNCTION z_metadata_recette.t005()
    RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
DECLARE
   e_mssg text ;
   e_detl text ;
BEGIN

    DROP EXTENSION metadata ;
    
    CREATE SCHEMA z_metadata ;
    CREATE EXTENSION metadata ;
    
    DROP EXTENSION metadata ;
    
    ASSERT EXISTS (SELECT * FROM pg_namespace WHERE nspname = 'z_metadata') ;
    -- le schéma n'est pas supposé être supprimé en même temps
    -- que l'extension lorsqu'il pré-existait.
    
    DROP SCHEMA z_metadata ;
    CREATE EXTENSION metadata ;

    RETURN True ;
    
EXCEPTION WHEN OTHERS OR ASSERT_FAILURE THEN
    GET STACKED DIAGNOSTICS e_mssg = MESSAGE_TEXT,
                            e_detl = PG_EXCEPTION_DETAIL ;
    RAISE NOTICE '%', e_mssg
        USING DETAIL = e_detl ;
        
    RETURN False ;
    
END
$_$;

COMMENT ON FUNCTION z_metadata_recette.t005() IS 'Métadonnées (recette). TEST : Désinstallation et ré-installation avec schéma z_metadata pré-existant.' ;


-- Function: z_metadata_recette.t006()

CREATE OR REPLACE FUNCTION z_metadata_recette.t006()
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
	INSERT INTO z_metadata.metada_shared_categorie (
	    origin, path, cat_label, widget_type, row_span,
		help_text, default_value, placeholder_text, input_mask,
		multiple_values, is_mandatory, order_key
		)
		VALUES ('shared', 'dct:description', 'résumé', 'QTextEdit', 15, NULL, NULL, NULL, NULL, True, True, 1)
		
	ASSERT (
		SELECT cat_label = 'résumé'
			FROM z_metadata.metada_categorie
			WHERE path = 'dct:description'
		) ;

	-- on remet le label initial
	UPDATE z_metadata.metada_categorie
		SET cat_label = 'description'
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

COMMENT ON FUNCTION z_metadata_recette.t006() IS 'Métadonnées (recette). TEST : Restauration des modifications utilisateur dans meta_shared_categorie.' ;


-- Function: z_metadata_recette.t007()

CREATE OR REPLACE FUNCTION z_metadata_recette.t007()
    RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
DECLARE
   e_mssg text ;
   e_detl text ;
BEGIN

	-- sans schéma ni table :
	ASSERT (
		SELECT z_metadata.meta_execute_sql_filter(
			'pg_has_role(''pg_monitor'', ''pg_read_all_stats'', ''USAGE'')',
			'schema',
			'table'
			)
		), 'échec assertion #1' ;
		
	ASSERT (
		SELECT NOT z_metadata.meta_execute_sql_filter(
			'pg_has_role(''pg_read_all_stats'', ''pg_monitor'', ''USAGE'')',
			'schema',
			'table'
			)
		), 'échec assertion #2' ;

	-- avec schéma :
	ASSERT (
		SELECT z_metadata.meta_execute_sql_filter(
			'$1 ~ ANY(ARRAY[''^r_'', ''^e_'']',
			'r_ign_bdtopo',
			'table'
			)
		), 'échec assertion #3' ;
		
	ASSERT (
		SELECT NOT z_metadata.meta_execute_sql_filter(
			'$1 ~ ANY(ARRAY[''^r_'', ''^e_'']',
			'schema',
			'table'
			)
		), 'échec assertion #4' ;
		
	-- avec schéma et table :
	ASSERT (
		SELECT z_metadata.meta_execute_sql_filter(
			'$1 ~ ANY(ARRAY[''^r_'', ''^e_''] AND $2 ~ ''_fr$''',
			'r_ign_admin_express',
			'region_fr'
			)
		), 'échec assertion #5' ;
		
	ASSERT (
		SELECT NOT z_metadata.meta_execute_sql_filter(
			'$1 ~ ANY(ARRAY[''^r_'', ''^e_''] AND $2 ~ ''_fr$''',
			'r_ign_admin_express',
			NULL
			)
		), 'échec assertion #6' ;
		-- NB. la fonction applique un coalesce '' sur le nom 
		-- de la table.
	
	-- pas de filtre :
	ASSERT (
		SELECT NOT z_metadata.meta_execute_sql_filter(
			NULL,
			'schema',
			'table'
			)
		), 'échec assertion #7' ;
		
	ASSERT (
		SELECT NOT z_metadata.meta_execute_sql_filter(
			'',
			'schema',
			'table'
			)
		), 'échec assertion #8' ;
	
	-- avec un filtre invalide :
	ASSERT (
		SELECT NOT z_metadata.meta_execute_sql_filter(
			'n''importe quoi',
			'schema',
			'table'
			)
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

COMMENT ON FUNCTION z_metadata_recette.t007() IS 'Métadonnées (recette). TEST : Exécution des filtres SQL par meta_execute_sql_filter.' ;



-- Function: z_metadata_recette.t008()

CREATE OR REPLACE FUNCTION z_metadata_recette.t008()
    RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
DECLARE
   e_mssg text ;
   e_detl text ;
BEGIN

	-- import d'un modèle
	SELECT meta_import_sample_template('Basique') ;
	
	ASSERT (
		SELECT count(*)
			FROM z_metadata.meta_template_categories_full
			WHERE tpl_label = 'Basique'
		) > 0, 'échec assertion #1' ;
		
	DELETE FROM z_metadata.meta_template
		WHERE tpl_label = 'Basique' ;
		
	-- import de tous les modèles
	SELECT meta_import_sample_template() ;
	
	ASSERT (
		SELECT count(*)
			FROM z_metadata.meta_template_categories_full
			WHERE tpl_label = 'Basique'
		) > 0, 'échec assertion #2' ;
		
	ASSERT (
		SELECT count(*)
			FROM z_metadata.meta_template
		) > 1, 'échec assertion #3' ;
	
	-- réinitialisation
	UPDATE z_metadata.meta_template
	    SET sql_filter = 'True'
		WHERE tpl_label = 'Basique' ;
		
	SELECT meta_import_sample_template('Basique') ;
	
	ASSERT (
		SELECT sql_filter IS NULL
			FROM z_metadata.meta_template
			WHERE tpl_label = 'Basique'
		), 'échec assertion #4' ;
		
	DROP EXTENSION metadata ;
	CREATE EXTENSION metadata ;

    RETURN True ;
    
EXCEPTION WHEN OTHERS OR ASSERT_FAILURE THEN
    GET STACKED DIAGNOSTICS e_mssg = MESSAGE_TEXT,
                            e_detl = PG_EXCEPTION_DETAIL ;
    RAISE NOTICE '%', e_mssg
        USING DETAIL = e_detl ;
        
    RETURN False ;
    
END
$_$;

COMMENT ON FUNCTION z_metadata_recette.t008() IS 'Métadonnées (recette). TEST : Insertion des modèles pré-configurés avec meta_import_sample_template.' ;

