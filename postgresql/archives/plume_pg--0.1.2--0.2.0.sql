\echo Use "ALTER EXTENSION plume_pg UPDATE TO '0.2.0'" to load this file. \quit
-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
--
-- PlumePg - Système de gestion des métadonnées locales, version 0.2.0
-- > Script de mise à jour depuis la version 0.1.2
--
-- Copyright République Française, 2023.
-- Secrétariat général du Ministère de la Transition écologique et
-- de la Cohésion des territoires, du Ministère de la Transition
-- énergétique et du Secrétariat d'Etat à la Mer.
-- Direction du numérique.
--
-- contributeurs : Leslie Lemaire (SNUM/UNI/DRC).
-- 
-- mél : drc.uni.dnum.sg@developpement-durable.gouv.fr
--
-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
--
-- Documentation :
-- https://mtes-mct.github.io/metadata-postgresql/usage/gestion_plume_pg.html
-- https://snum.scenari-community.org/Plume/Documentation/ (en cours de rédaction)
--
-- GitHub :
-- https://github.com/MTES-MCT/metadata-postgresql
-- 
-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
--
-- Ce logiciel est un programme informatique complémentaire au système de
-- gestion de base de données PosgreSQL ("https://www.postgresql.org/"). Il
-- met en place côté serveur les objets nécessaires à la gestion des 
-- métadonnées, en complément du plugin QGIS Plume.
--
-- Ce logiciel est régi par la licence GNU Affero General Public License v3.0
-- or later. Lien SPDX : https://spdx.org/licenses/AGPL-3.0-or-later.html.
--
-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
--
-- dépendances : pgcrypto
--
-- schéma contenant les objets : z_plume
--
-- objets créés par le script : 
-- - Sequence: z_plume.meta_template_tpl_id_seq
-- - Sequence: z_plume.meta_tab_tab_id_seq
--
-- objets modifiés par le script :
-- - Table: z_plume.meta_template
-- - Table: z_plume.meta_tab
-- - Table: z_plume.meta_template_categories
-- - View: z_plume.meta_template_categories_full
-- - Function: z_plume.meta_import_sample_template(text)
--
-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

----------------------------------------
------ 1 - MODELES DE FORMULAIRES ------
----------------------------------------

/* 1.2 - TABLE DES MODELES
   1.3 - TABLE DES ONGLETS
   1.4 - ASSOCIATION DES CATEGORIES AUX MODELES
   1.5 - IMPORT DE MODELES PRE-CONFIGURES
*/

------ 1.2 - TABLE DES MODELES ------

-- Sequence: z_plume.meta_template_tpl_id_seq

CREATE SEQUENCE z_plume.meta_template_tpl_id_seq AS int ;

SELECT pg_extension_config_dump('z_plume.meta_template_tpl_id_seq'::regclass, '') ;


-- Table: z_plume.meta_template

ALTER TABLE z_plume.meta_template
    ADD COLUMN tpl_id int DEFAULT nextval('z_plume.meta_template_tpl_id_seq') ;

ALTER SEQUENCE z_plume.meta_template_tpl_id_seq OWNED BY z_plume.meta_template.tpl_id ;

COMMENT ON COLUMN z_plume.meta_template.tpl_id IS 'Identifiant unique.' ;

UPDATE z_plume.meta_template
    SET tpl_id = DEFAULT ;

ALTER TABLE z_plume.meta_template_categories
    DROP CONSTRAINT meta_template_categories_tpl_label_fkey ;

ALTER TABLE z_plume.meta_template
    DROP CONSTRAINT meta_template_pkey ;
ALTER TABLE z_plume.meta_template ADD PRIMARY KEY (tpl_id) ;

ALTER TABLE z_plume.meta_template
    ALTER COLUMN tpl_label SET NOT NULL,
    ADD CONSTRAINT meta_template_tpl_label_uni UNIQUE (tpl_label) ;


---- 1.3 - TABLE DES ONGLETS ------

-- Sequence: z_plume.meta_tab_tab_id_seq

CREATE SEQUENCE z_plume.meta_tab_tab_id_seq AS int ;

SELECT pg_extension_config_dump('z_plume.meta_tab_tab_id_seq'::regclass, '') ;


-- Table: z_plume.meta_tab

ALTER TABLE z_plume.meta_tab
    ADD COLUMN tab_id int DEFAULT nextval('z_plume.meta_tab_tab_id_seq') ;

ALTER SEQUENCE z_plume.meta_tab_tab_id_seq OWNED BY z_plume.meta_tab.tab_id ;

ALTER TABLE z_plume.meta_tab
    RENAME COLUMN tab TO tab_label ;

COMMENT ON COLUMN z_plume.meta_tab.tab_id IS 'Identifiant unique.' ;
COMMENT ON COLUMN z_plume.meta_tab.tab_label IS 'Nom de l''onglet.' ;

UPDATE z_plume.meta_tab
    SET tab_id = DEFAULT ;

ALTER TABLE z_plume.meta_template_categories
    DROP CONSTRAINT meta_template_categories_tab_fkey ;

ALTER TABLE z_plume.meta_tab
    DROP CONSTRAINT meta_tab_pkey ;
ALTER TABLE z_plume.meta_tab ADD PRIMARY KEY (tab_id) ;

ALTER TABLE z_plume.meta_tab
    ALTER COLUMN tab_label SET NOT NULL,
    ADD CONSTRAINT meta_tab_tab_label_uni UNIQUE (tab_label) ;


---- 1.4 - ASSOCIATION DES CATEGORIES AUX MODELES ------

-- Table: z_plume.meta_template_categories

ALTER TABLE z_plume.meta_template_categories
    ADD COLUMN tpl_id int ;

UPDATE z_plume.meta_template_categories
    SET tpl_id = (
        SELECT tpl_id
            FROM z_plume.meta_template
            WHERE meta_template.tpl_label = meta_template_categories.tpl_label
    ) ;

ALTER TABLE z_plume.meta_template_categories
    ALTER COLUMN tpl_id SET NOT NULL ;

ALTER TABLE z_plume.meta_template_categories
    ADD CONSTRAINT meta_template_categories_tpl_id_fkey FOREIGN KEY (tpl_id)
        REFERENCES z_plume.meta_template (tpl_id)
        ON UPDATE RESTRICT ON DELETE CASCADE ;

ALTER TABLE z_plume.meta_template_categories
    ADD COLUMN tab_id int ;

UPDATE z_plume.meta_template_categories
    SET tab_id = (
        SELECT tab_id
            FROM z_plume.meta_tab
            WHERE meta_tab.tab_label = meta_template_categories.tab
    ) ;

ALTER TABLE z_plume.meta_template_categories
    ADD CONSTRAINT meta_template_categories_tab_id_fkey FOREIGN KEY (tab_id)
        REFERENCES z_plume.meta_tab (tab_id)
        ON UPDATE CASCADE ON DELETE SET NULL ;

COMMENT ON COLUMN z_plume.meta_template_categories.tpl_id IS 'Identifiant du modèle de formulaire.' ;
COMMENT ON COLUMN z_plume.meta_template_categories.tab_id IS 'Identifiant de l''onglet du formulaire où placer la catégorie. Cette information n''est considérée que pour les catégories locales et les catégories communes de premier niveau (par exemple "dcat:distribution / dct:issued" ira nécessairement dans le même onglet que "dcat:distribution"). Pour celles-ci, si aucun onglet n''est fourni, la catégorie ira toujours dans le premier onglet cité pour le modèle dans la présente table ou, à défaut, dans un onglet "Général".' ;


-- View: z_plume.meta_template_categories_full

CREATE OR REPLACE VIEW z_plume.meta_template_categories_full AS (
    SELECT
        tc.tplcat_id,
        t.tpl_label,
        coalesce(tc.shrcat_path, tc.loccat_path) AS path,
        c.origin,
        coalesce(tc.label, c.label) AS label,
        coalesce(tc.description, c.description) AS description,
        coalesce(tc.special, c.special) AS special,
        c.is_node,
        coalesce(tc.datatype, c.datatype) AS datatype,
        coalesce(tc.is_long_text, c.is_long_text) AS is_long_text,
        coalesce(tc.rowspan, c.rowspan) AS rowspan,
        coalesce(tc.placeholder, c.placeholder) AS placeholder,
        coalesce(tc.input_mask, c.input_mask) AS input_mask,
        coalesce(tc.is_multiple, c.is_multiple) AS is_multiple,
        coalesce(tc.unilang, c.unilang) AS unilang,
        coalesce(tc.is_mandatory, c.is_mandatory) AS is_mandatory,
        coalesce(tc.sources, c.sources) AS sources,
        coalesce(tc.geo_tools, c.geo_tools) AS geo_tools,
        coalesce(tc.compute, c.compute) AS compute,
        coalesce(tc.template_order, c.template_order) AS template_order,
        tc.is_read_only,
        tb.tab_label AS tab,
        coalesce(tc.compute_params, c.compute_params) AS compute_params
        FROM z_plume.meta_template_categories AS tc
            LEFT JOIN z_plume.meta_categorie AS c
                ON coalesce(tc.shrcat_path, tc.loccat_path) = c.path
            LEFT JOIN z_plume.meta_template AS t
                ON tc.tpl_id = t.tpl_id
            LEFT JOIN z_plume.meta_tab AS tb 
                ON tc.tab_id = tb.tab_id
        WHERE t.enabled
    ) ;

ALTER TABLE z_plume.meta_template_categories
    DROP COLUMN tpl_label,
    DROP COLUMN tab ;

------ 1.5 - IMPORT DE MODELES PRE-CONFIGURES -------

-- Function: z_plume.meta_import_sample_template(text)

CREATE OR REPLACE FUNCTION z_plume.meta_import_sample_template(
        tpl_label text default NULL::text
        )
    RETURNS TABLE (label text, summary text)
    LANGUAGE plpgsql
    AS $BODY$
/* Importe l'un des modèles de formulaires pré-configurés (ou tous si l'argument n'est pas renseigné).

    Réexécuter la fonction sur un modèle déjà répertorié aura
    pour effet de le réinitialiser.
    
    Si le nom de modèle fourni en argument est inconnu, la
    fonction n'a aucun effet et renverra une table vide.

    Parameters
    ----------
    tpl_label : text, optional
        Nom du modèle à importer.

    Returns
    -------
    table (label : text, summary : text)
        La fonction renvoie une table listant les modèles
        effectivement importés.
        Le champ "label" contient le nom du modèle.
        Le champ "summary" fournit un résumé des opérations
        réalisées. À ce stade, il vaudra 'created' pour un modèle
        qui n'était pas encore répertorié et 'updated' pour un
        modèle déjà répertorié.

*/
DECLARE
    tpl record ;
    tplcat record ;
BEGIN

    -- boucle sur les modèles :
    FOR tpl IN SELECT * FROM (
        VALUES
            (
                'Donnée externe',
                '$1 ~ ANY(ARRAY[''^r_'', ''^e_''])',
                '[{"plume:isExternal": true}]'::jsonb,
                10,
                format(
                    'Modèle pré-configuré importé via z_plume.meta_import_sample_template() le %s à %s.',
                    now()::date,
                    left(now()::time::text, 8)
                    )
            ),
            (
                'Classique',
                '$1 ~ ''^c_''',
                NULL,
                5,
                format(
                    'Modèle pré-configuré importé via z_plume.meta_import_sample_template() le %s à %s.',
                    now()::date,
                    left(now()::time::text, 8)
                    )
            ),
            (
                'Basique', NULL, NULL, 0,
                format(
                    'Modèle pré-configuré importé via z_plume.meta_import_sample_template() le %s à %s.',
                    now()::date,
                    left(now()::time::text, 8)
                    )
            )
        ) AS t (tpl_label, sql_filter, md_conditions, priority, comment)
        WHERE meta_import_sample_template.tpl_label IS NULL
            OR meta_import_sample_template.tpl_label = t.tpl_label
    LOOP
    
        DELETE FROM z_plume.meta_template
            WHERE meta_template.tpl_label = tpl.tpl_label ;
            
        IF FOUND
        THEN
            RETURN QUERY SELECT tpl.tpl_label, 'updated' ;
        ELSE
            RETURN QUERY SELECT tpl.tpl_label, 'created' ;
        END IF ;
        
        INSERT INTO z_plume.meta_template
            (tpl_label, sql_filter, md_conditions, priority, comment)
            VALUES (tpl.tpl_label, tpl.sql_filter, tpl.md_conditions, tpl.priority, tpl.comment) ;
        
        -- boucle sur les associations modèles-catégories :
        FOR tplcat IN SELECT * FROM (
            VALUES
                ('Basique', 'dct:description'),
                ('Basique', 'dct:modified'),
                ('Basique', 'dct:temporal'),
                ('Basique', 'dct:temporal / dcat:startDate'),
                ('Basique', 'dct:temporal / dcat:endDate'),
                ('Basique', 'dct:title'),
                ('Basique', 'owl:versionInfo'),
                
                ('Classique', 'adms:versionNotes'),
                ('Classique', 'dcat:contactPoint'),
                ('Classique', 'dcat:contactPoint / vcard:fn'),
                ('Classique', 'dcat:contactPoint / vcard:hasEmail'),
                ('Classique', 'dcat:contactPoint / vcard:hasTelephone'),
                ('Classique', 'dcat:contactPoint / vcard:hasURL'),
                ('Classique', 'dcat:contactPoint / vcard:organization-name'),
                ('Classique', 'dcat:keyword'),
                ('Classique', 'dcat:landingPage'),
                ('Classique', 'dcat:spatialResolutionInMeters'),
                ('Classique', 'dcat:theme'),
                ('Classique', 'dct:accessRights'),
                ('Classique', 'dct:accessRights / rdfs:label'),
                ('Classique', 'dct:accrualPeriodicity'),
                ('Classique', 'dct:conformsTo'),
                ('Classique', 'dct:conformsTo / dct:description'),
                ('Classique', 'dct:conformsTo / dct:title'),
                ('Classique', 'dct:conformsTo / dct:issued'),
                ('Classique', 'dct:conformsTo / foaf:page'),
                ('Classique', 'dct:conformsTo / owl:versionInfo'),
                ('Classique', 'dct:created'),
                ('Classique', 'dct:description'),
                ('Classique', 'dct:identifier'),
                ('Classique', 'dct:modified'),
                ('Classique', 'dct:provenance'),
                ('Classique', 'dct:provenance / rdfs:label'),
                ('Classique', 'dct:spatial'),
                ('Classique', 'dct:spatial / dct:identifier'),
                ('Classique', 'dct:spatial / skos:inScheme'),
                ('Classique', 'dct:spatial / skos:prefLabel'),
                ('Classique', 'dct:temporal'),
                ('Classique', 'dct:temporal / dcat:startDate'),
                ('Classique', 'dct:temporal / dcat:endDate'),
                ('Classique', 'dct:title'),
                ('Classique', 'foaf:page'),
                ('Classique', 'owl:versionInfo'),
                ('Classique', 'plume:isExternal'),
                
                ('Donnée externe', 'adms:versionNotes'),
                ('Donnée externe', 'dcat:contactPoint'),
                ('Donnée externe', 'dcat:contactPoint / vcard:fn'),
                ('Donnée externe', 'dcat:contactPoint / vcard:hasEmail'),
                ('Donnée externe', 'dcat:contactPoint / vcard:hasTelephone'),
                ('Donnée externe', 'dcat:contactPoint / vcard:hasURL'),
                ('Donnée externe', 'dcat:contactPoint / vcard:organization-name'),
                ('Donnée externe', 'dcat:distribution'),
                ('Donnée externe', 'dcat:distribution / dcat:accessURL'),
                ('Donnée externe', 'dcat:distribution / dct:issued'),
                ('Donnée externe', 'dcat:distribution / dct:license'),
                ('Donnée externe', 'dcat:distribution / dct:license / rdfs:label'),
                ('Donnée externe', 'dcat:keyword'),
                ('Donnée externe', 'dcat:landingPage'),
                ('Donnée externe', 'dcat:theme'),
                ('Donnée externe', 'dct:accessRights'),
                ('Donnée externe', 'dct:accessRights / rdfs:label'),
                ('Donnée externe', 'dct:accrualPeriodicity'),
                ('Donnée externe', 'dct:description'),
                ('Donnée externe', 'dct:modified'),
                ('Donnée externe', 'dct:provenance'),
                ('Donnée externe', 'dct:provenance / rdfs:label'),
                ('Donnée externe', 'dct:publisher'),
                ('Donnée externe', 'dct:publisher / foaf:name'),
                ('Donnée externe', 'dct:temporal'),
                ('Donnée externe', 'dct:temporal / dcat:startDate'),
                ('Donnée externe', 'dct:temporal / dcat:endDate'),
                ('Donnée externe', 'dct:title'),
                ('Donnée externe', 'dct:spatial'),
                ('Donnée externe', 'dct:spatial / dct:identifier'),
                ('Donnée externe', 'dct:spatial / skos:inScheme'),
                ('Donnée externe', 'dct:spatial / skos:prefLabel'),
                ('Donnée externe', 'foaf:page'),
                ('Donnée externe', 'owl:versionInfo'),
                ('Donnée externe', 'plume:isExternal')
            ) AS t (tpl_label, shrcat_path)
            WHERE t.tpl_label = tpl.tpl_label
        LOOP
        
            INSERT INTO z_plume.meta_template_categories
                (tpl_id, shrcat_path) (
                    SELECT meta_template.tpl_id, tplcat.shrcat_path
                        FROM z_plume.meta_template
                        WHERE meta_template.tpl_label = tpl.tpl_label
                ) ;
        
        END LOOP ;
    
    END LOOP ;

    RETURN ;
    
END
$BODY$ ;

