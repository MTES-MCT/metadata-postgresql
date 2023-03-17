-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
--
-- PlumePg - Système de gestion des métadonnées locales
-- > Base pour les tests de sauvegarde/restauration
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
-- À exécuter sur une base vierge ou dédiée aux tests
-- de sauvegarde/restauration.
--
-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

/*

1. Exécuter le présent script sur une base vierge ou
dédiée aux tests de sauvegarde/restauration.

2. Sauvegarder cette base.

3. Vider la base avec les commandes suivantes :

DROP EXTENSION IF EXISTS plume_pg ;
DROP TABLE IF EXISTS table_test ;
DROP FUNCTION IF EXISTS plume_backup_restore_control() ;

4. Restaurer la base. Il ne doit y avoir aucune erreur.

5. Exécuter la fonction de contrôle. Elle renvoie True
si l'état de la base restaurée est conforme à ce qui
était attendu, sinon une erreur.

SELECT plume_backup_restore_control() ;


*/


------ Initialisation ------

-- suppression de tous les objets créés par une exécution
-- antérieure du présent script
DROP EXTENSION IF EXISTS plume_pg ;
DROP TABLE IF EXISTS table_test ;
DROP FUNCTION IF EXISTS plume_backup_restore_control() ;

-- création de l'extension
CREATE EXTENSION plume_pg CASCADE ;


------ Tampons de dates ------

-- activation des déclencheurs sur évènements
ALTER EVENT TRIGGER plume_stamp_table_creation ENABLE ;
ALTER EVENT TRIGGER plume_stamp_table_modification ENABLE ;
ALTER EVENT TRIGGER plume_stamp_table_drop ENABLE ;

-- et du déclencheur sur stamp_timestamp
ALTER TABLE z_plume.stamp_timestamp ENABLE TRIGGER stamp_timestamp_to_metadata ;

-- création d'une table, dont la date de création est
-- enregistrée dans z_plume.stamp_timestamp
CREATE TABLE table_test (id integer PRIMARY KEY) ;

-- ... ainsi que sa date de dernière modification
ALTER TABLE table_test ADD COLUMN txt text ;


------ Import et personnalisation d'un modèle pré-configuré ------

-- import du modèle "Classique"
SELECT * FROM z_plume.meta_import_sample_template('Classique') ;

-- ajout d'une catégorie locale
INSERT INTO z_plume.meta_categorie (label, description, datatype, is_long_text)
    VALUES ('Notes ADL', 'Note à l''usage de l''administrateur.',
        'xsd:string', True) ;

-- et référencement dans le modèle "Classique"
INSERT INTO z_plume.meta_template_categories (tpl_id, loccat_path) (
    SELECT tpl_id, path FROM z_plume.meta_categorie, z_plume.meta_template
        WHERE label = 'Notes ADL'
            AND tpl_id = (
                SELECT tpl_id 
                    FROM z_plume.meta_template 
                    WHERE tpl_label = 'Classique'
            )
    ) ;

-- modification d'une catégorie commune pour tous les modèles
UPDATE z_plume.meta_shared_categorie
    SET label = 'Titre' -- au lieu de "Libellé"
    WHERE path = 'dct:title' ;

-- modification d'une catégorie commune pour le seul modèle "Classique"
UPDATE z_plume.meta_template_categories
    SET label = 'Résumé' -- au lieu de "Description"
    WHERE tpl_id = (
            SELECT tpl_id 
                FROM z_plume.meta_template 
                WHERE tpl_label = 'Classique'
        )
        AND shrcat_path = 'dct:description' ;

-- modifcation du paramétrage du modèle
UPDATE z_plume.meta_template
    SET comment = 'Modèle pré-configuré personnalisé.'
    WHERE tpl_label = 'Classique' ;

------ Nouveau modèle ------

-- création du modèle
INSERT INTO z_plume.meta_template (tpl_label, sql_filter, priority)
    VALUES (
        'Classique bis',
        'pg_has_role(''g_urba'', ''USAGE'')
            AND NOT pg_has_role(''g_admin'', ''USAGE'')',
        50
    ) ;

-- définition d'onglets
INSERT INTO z_plume.meta_tab (tab_label, tab_num)
    VALUES ('Principal', 1), ('Secondaire', 2) ;

-- association de catégories au modèle
INSERT INTO z_plume.meta_template_categories (tpl_id, shrcat_path) (
    SELECT (
            SELECT tpl_id 
                FROM z_plume.meta_template 
                WHERE tpl_label = 'Classique bis'
        ),
        shrcat_path
        FROM z_plume.meta_template_categories
        WHERE tpl_id = (
                SELECT tpl_id 
                    FROM z_plume.meta_template 
                    WHERE tpl_label = 'Classique'
            )
    ) ;

-- paramétrage des catégories
UPDATE z_plume.meta_template_categories
    SET tab_id = (
            SELECT tab_id
                FROM z_plume.meta_tab
                WHERE tab_label = 'Secondaire'
        ),
        is_read_only = True
    WHERE tpl_id = (
            SELECT tpl_id 
                FROM z_plume.meta_template 
                WHERE tpl_label = 'Classique bis'
        ) ;

UPDATE z_plume.meta_template_categories
    SET tab_id = (
            SELECT tab_id
                FROM z_plume.meta_tab
                WHERE tab_label = 'Principal'
        ),
        is_read_only = False
    WHERE tpl_id = (
            SELECT tpl_id 
                FROM z_plume.meta_template 
                WHERE tpl_label = 'Classique bis'
        )
        AND shrcat_path IN ('adms:versionNotes', 'dct:title',
            'dct:description', 'dct:modified', 'dct:provenance',
            'dct:provenance / rdfs:label') ;


------ Fonction de contrôle ------

-- Function: plume_backup_restore_control()

CREATE OR REPLACE FUNCTION plume_backup_restore_control()
    RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
BEGIN

    ASSERT (SELECT string_agg(relid::regclass::text, ', ') = 'table_test'
        FROM z_plume.stamp_timestamp), 'échec assertion #1' ;
    
    -- à ce stade, les dates sont perdues et les déclencheurs
    -- sur évènement sont recréés dans leur état d'origine (soit
    -- inactifs, pour la plupart)
    ASSERT (SELECT evtenabled = 'O' FROM pg_event_trigger
        WHERE evtname = 'plume_stamp_new_entry'), 'échec assertion #2-a' ;
    ASSERT (SELECT bool_and(evtenabled = 'D') FROM pg_event_trigger
        WHERE evtname IN ('plume_stamp_table_creation', 'plume_stamp_table_modification',
        'plume_stamp_table_drop')), 'échec assertion #2-b' ;
    ASSERT (SELECT tgenabled = 'O' FROM pg_trigger
        WHERE tgname = 'plume_stamp_data_edit' AND tgrelid = 'table_test'::regclass),
        'échec assertion #2-c' ;
    ASSERT (SELECT tgenabled = 'D' FROM pg_trigger
        WHERE tgname = 'stamp_timestamp_to_metadata'
        AND tgrelid = 'z_plume.stamp_timestamp'::regclass), 'échec assertion #2-d' ;
    ASSERT (SELECT tgenabled = 'O' FROM pg_trigger
        WHERE tgname = 'stamp_timestamp_access_control'
        AND tgrelid = 'z_plume.stamp_timestamp'::regclass), 'échec assertion #2-e' ;
    ASSERT (SELECT modified IS NULL and created IS NULL
        FROM z_plume.stamp_timestamp WHERE relid = 'table_test'::regclass),
        'échec assertion #2-f' ;

    ASSERT (SELECT label = 'Titre'
        FROM z_plume.meta_shared_categorie WHERE path = 'dct:title'), 'échec assertion #2' ;
    
    ASSERT (SELECT string_agg(label, ', ') = 'Notes ADL'
        FROM z_plume.meta_local_categorie), 'échec assertion #3' ;
    
    ASSERT (
        SELECT label = 'Résumé'
            FROM z_plume.meta_template_categories
            WHERE shrcat_path = 'dct:description'
                AND tpl_id = (
                    SELECT tpl_id 
                        FROM z_plume.meta_template 
                        WHERE tpl_label = 'Classique'
                )
        ),
        'échec assertion #4' ;

    ASSERT (SELECT comment = 'Modèle pré-configuré personnalisé.'
        FROM z_plume.meta_template WHERE tpl_label = 'Classique'),
        'échec assertion #5' ;

    ASSERT 'Classique bis' IN (SELECT tpl_label FROM z_plume.meta_template),
        'échec assertion #6' ;

    ASSERT 'Secondaire' IN (SELECT tab_label FROM z_plume.meta_tab), 'échec assertion #7' ;
    
    ASSERT (
        SELECT tab_id = (
                SELECT tab_id
                    FROM z_plume.meta_tab
                    WHERE tab_label = 'Principal'
            ) AND is_read_only = False
            FROM z_plume.meta_template_categories
            WHERE tpl_id = (
                        SELECT tpl_id 
                            FROM z_plume.meta_template 
                            WHERE tpl_label = 'Classique bis'
                    )
                AND shrcat_path = 'adms:versionNotes'
        ),
        'échec assertion #8' ;

    RETURN True ;
    
END
$_$;

COMMENT ON FUNCTION plume_backup_restore_control() IS 'PlumePg (recette). TEST : Contrôle d''intégrité après restauration d''une base.' ;

