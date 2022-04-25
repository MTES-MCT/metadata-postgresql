\echo Use "ALTER EXTENSION plume_pg UPDATE TO '0.1.0'" to load this file. \quit
-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
--
-- PlumePg - Système de gestion des métadonnées locales, version 0.1.0
-- > Script de mise à jour depuis la version 0.0.1
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
-- Documentation :
-- https://snum.scenari-community.org/Plume/Documentation/
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
-- - Function: z_plume.meta_ante_post_description(oid, text)
-- - Function: z_plume.meta_description(oid, text)
-- - Function: z_plume.meta_regexp_matches(text, text, text)
-- - Function: z_plume.is_relowner(oid)
-- - Table: z_plume.stamp_timestamp
-- - Policy: timestamp_public_select
-- - Policy: timestamp_owner_insert
-- - Policy: timestamp_owner_update
-- - Policy: timestamp_owner_delete
-- - Function: z_plume.stamp_data_modification()
-- - Function: z_plume.stamp_create_trigger(oid)
-- - Function: z_plume.stamp_table_creation()
-- - Event trigger: plume_stamp_creation
-- - Function: z_plume.stamp_table_modification()
-- - Event trigger: plume_stamp_modification
-- - Function: z_plume.stamp_table_drop()
-- - Event trigger: plume_stamp_drop
-- - Function: z_plume.stamp_clean_timestamp()
-- - Function: z_plume.stamp_activate_recording()
--
-- objets modifiés par le script :
-- - Schema: z_plume
-- - Type: z_plume.meta_compute
-- - Table: z_plume.meta_categorie
-- - Table: z_plume.meta_shared_categorie
-- - Table: z_plume.meta_template
-- - Table: z_plume.meta_tab
-- - Function: z_plume.meta_shared_categorie_before_insert()
-- - Table: z_plume.meta_local_categorie
-- - Table: z_plume.meta_template_categories
-- - View: z_plume.meta_template_categories_full
-- - Function: z_plume.meta_import_sample_template(text)
-- - Function: z_plume.meta_execute_sql_filter(text, text, text)
--
-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


/* 0 - SCHEMA z_plume
   1 - MODELES DE FORMULAIRES
   2 - FONCTIONS UTILITAIRES
   3 - DATES DE MODIFICATION */

-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

--------------------------------
------ 0 - SCHEMA z_plume ------
--------------------------------

-- Schema: z_plume

GRANT USAGE ON SCHEMA z_plume TO public ;

-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

----------------------------------------
------ 1 - MODELES DE FORMULAIRES ------
----------------------------------------

/* 1.1 - TABLE DE CATEGORIES
   1.2 - TABLE DES MODELES
   1.3 - TABLE DES ONGLETS
   1.4 - ASSOCIATION DES CATEGORIES AUX MODELES
   1.5 - IMPORT DE MODELES PRE-CONFIGURES */


------ 1.1 - TABLE DE CATEGORIES ------

-- Type: z_plume.meta_compute

ALTER TYPE z_plume.meta_compute ADD VALUE 'empty' AFTER 'auto' ;
ALTER TYPE z_plume.meta_compute ADD VALUE 'new' AFTER 'empty' ;


--Table: z_plume.meta_categorie

ALTER TABLE z_plume.meta_categorie
    ADD COLUMN compute_params jsonb ;

GRANT SELECT ON TABLE z_plume.meta_categorie TO public ;

COMMENT ON COLUMN z_plume.meta_categorie.compute_params IS 'Paramètres des fonctionnalités de calcul, le cas échéant, sous une forme clé-valeur. La clé est le nom du paramètre, la valeur sa valeur. Cette information ne sera considérée que si une méthode de calcul est effectivement disponible pour la catégorie et qu''elle attend un ou plusieurs paramètres.' ;


-- Table: z_plume.meta_shared_categorie

GRANT SELECT ON TABLE z_plume.meta_shared_categorie TO public ;

COMMENT ON COLUMN z_plume.meta_shared_categorie.compute_params IS 'Paramètres des fonctionnalités de calcul, le cas échéant, sous une forme clé-valeur. La clé est le nom du paramètre, la valeur sa valeur. Cette information ne sera considérée que si une méthode de calcul est effectivement disponible pour la catégorie et qu''elle attend un ou plusieurs paramètres.' ;

-- Function: z_plume.meta_shared_categorie_before_insert()

CREATE OR REPLACE FUNCTION z_plume.meta_shared_categorie_before_insert()
    RETURNS trigger
    LANGUAGE plpgsql
    AS $BODY$
/* Fonction exécutée par le trigger meta_shared_categorie_before_insert.

    Elle supprime les lignes pré-existantes (même valeur de "path") faisant l'objet
    de commandes INSERT. Autrement dit, elle permet d'utiliser des commandes INSERT
    pour réaliser des UPDATE.

    Ne vaut que pour les catégories des métadonnées communes (les seules stockées
    dans z_plume.meta_shared_categorie).

    Cette fonction est nécessaire pour que l'extension PlumePg puisse initialiser
    la table avec les catégories partagées, et que les modifications faites par
    l'administrateur sur ces enregistrements puissent ensuite être préservées en cas
    de sauvegarde/restauration (table marquée comme table de configuration de
    l'extension).

*/
BEGIN
    
    DELETE FROM z_plume.meta_shared_categorie
        WHERE meta_shared_categorie.path = NEW.path ;
        
    RETURN NEW ;

END
$BODY$ ;


-- Table: z_plume.meta_local_categorie

GRANT SELECT ON TABLE z_plume.meta_local_categorie TO public ;

COMMENT ON COLUMN z_plume.meta_local_categorie.compute_params IS 'Ignoré pour les catégories locales.' ;


------ 1.2 - TABLE DES MODELES ------

-- Table: z_plume.meta_template

ALTER TABLE z_plume.meta_template
    ADD COLUMN enabled boolean NOT NULL DEFAULT True ;

GRANT SELECT ON TABLE z_plume.meta_template TO public ;

COMMENT ON COLUMN z_plume.meta_template.enabled IS 'Booléen indiquant si le modèle est actif. Les modèles désactivés n''apparaîtront pas dans la liste de modèles du plugin QGIS, même si leurs conditions d''application automatique sont remplies.' ;


---- 1.3 - TABLE DES ONGLETS ------

-- Table: z_plume.meta_tab

GRANT SELECT ON TABLE z_plume.meta_tab TO public ;


---- 1.4 - ASSOCIATION DES CATEGORIES AUX MODELES ------

-- Table: z_plume.meta_template_categories

ALTER TABLE z_plume.meta_template_categories
    ADD COLUMN compute_params jsonb ;

GRANT SELECT ON TABLE z_plume.meta_template_categories TO public ;

COMMENT ON COLUMN z_plume.meta_template_categories.compute_params IS 'Paramètres des fonctionnalités de calcul, le cas échéant, sous une forme clé-valeur. La clé est le nom du paramètre, la valeur sa valeur. Cette information ne sera considérée que si une méthode de calcul est effectivement disponible pour la catégorie et qu''elle attend un ou plusieurs paramètres. Si présente, cette valeur se substitue pour le modèle considéré à la valeur renseignée dans le champ éponyme de meta_categorie.' ;

-- View: z_plume.meta_template_categories_full

DROP VIEW z_plume.meta_template_categories_full ;
CREATE VIEW z_plume.meta_template_categories_full AS (
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
        tc.tab,
        coalesce(tc.compute_params, c.compute_params) AS compute_params
        FROM z_plume.meta_template_categories AS tc
            LEFT JOIN z_plume.meta_categorie AS c
                ON coalesce(tc.shrcat_path, tc.loccat_path) = c.path
            LEFT JOIN z_plume.meta_template AS t
                ON tc.tpl_label = t.tpl_label
        WHERE t.enabled
    ) ;

GRANT SELECT ON TABLE z_plume.meta_template_categories_full TO public ;

COMMENT ON VIEW z_plume.meta_template_categories_full IS 'Description complète des modèles de formulaire (rassemble les informations de meta_categorie et meta_template_categories).' ;

COMMENT ON COLUMN z_plume.meta_template_categories_full.tplcat_id IS 'Identifiant unique.' ;
COMMENT ON COLUMN z_plume.meta_template_categories_full.tpl_label IS 'Nom du modèle.' ;
COMMENT ON COLUMN z_plume.meta_template_categories_full.path IS 'Chemin N3 / identifiant de la catégorie.' ;
COMMENT ON COLUMN z_plume.meta_template_categories_full.origin IS 'Origine de la catégorie : ''shared'' pour une catégorie commune, ''local'' pour une catégorie locale supplémentaire.' ;
COMMENT ON COLUMN z_plume.meta_template_categories_full.label IS 'Libellé de la catégorie. Le cas échéant, cette valeur se substituera pour le modèle considéré à la valeur renseignée dans le schéma des métadonnées communes.' ;
COMMENT ON COLUMN z_plume.meta_template_categories_full.description IS 'Description de la catégorie. Sera affiché sous la forme d''un texte d''aide dans le formulaire. Le cas échéant, cette valeur se substituera pour le modèle considéré à la valeur renseignée dans le schéma des métadonnées communes.' ;
COMMENT ON COLUMN z_plume.meta_template_categories_full.special IS 'Le cas échéant, mise en forme spécifique à appliquer au champ. Valeurs autorisées : ''url'', ''email'', ''phone''. Pour les catégories communes, les modifications apportées à ce champ ne seront pas prises en compte.' ;
COMMENT ON COLUMN z_plume.meta_template_categories_full.is_node IS 'True si la catégorie est le nom d''un groupe qui contiendra lui-même d''autres catégories et non une catégorie à laquelle sera directement associée une valeur. Par exemple, is_node vaut True pour la catégorie correspondant au point de contact (dcat:contactPoint) et False pour le nom du point de contact (dcat:contactPoint / vcard:fn).' ;
COMMENT ON COLUMN z_plume.meta_template_categories_full.datatype IS 'Type de valeur attendu pour la catégorie. Cette information détermine notamment la nature des widgets utilisés par Plume pour afficher et éditer les valeurs, ainsi que les validateurs appliqués. Pour les catégories communes, les modifications apportées à ce champ ne seront pas prises en compte.' ;
COMMENT ON COLUMN z_plume.meta_template_categories_full.is_long_text IS 'True pour une catégorie appelant un texte de plusieurs lignes. Cette information ne sera prise en compte que si le type de valeur (datatype) est ''xsd:string'' ou ''rdf:langString''. Le cas échéant, cette valeur se substituera pour le modèle considéré à la valeur renseignée dans le schéma des métadonnées communes.' ;
COMMENT ON COLUMN z_plume.meta_template_categories_full.rowspan IS 'Nombre de lignes occupées par le widget de saisie, s''il y a lieu de modifier le comportement par défaut de Plume. La valeur ne sera considérée que si is_long_text vaut True. Le cas échéant, cette valeur se substituera pour le modèle considéré à la valeur renseignée dans le schéma des métadonnées communes.' ;
COMMENT ON COLUMN z_plume.meta_template_categories_full.placeholder IS 'Valeur fictive pré-affichée en tant qu''exemple dans le widget de saisie, s''il y a lieu. Le cas échéant, cette valeur se substituera pour le modèle considéré à la valeur renseignée dans le schéma des métadonnées communes.' ;
COMMENT ON COLUMN z_plume.meta_template_categories_full.input_mask IS 'Masque de saisie, s''il y a lieu. La valeur sera ignorée si le widget utilisé pour la catégorie ne prend pas en charge ce mécanisme. Le cas échéant, cette valeur se substituera pour le modèle considéré à la valeur renseignée dans le schéma des métadonnées communes.' ;
COMMENT ON COLUMN z_plume.meta_template_categories_full.is_multiple IS 'True si la catégorie admet plusieurs valeurs. Pour les catégories commnes, les modifications apportées à ce champ ne seront pas prises en compte.' ;
COMMENT ON COLUMN z_plume.meta_template_categories_full.unilang IS 'True si la catégorie n''admet plusieurs valeurs que si elles sont dans des langues différentes (par exemple un jeu de données n''a en principe qu''un seul titre, mais il peut être traduit). is_multiple est ignoré quand unilang vaut True. Pour les catégories commnes, les modifications apportées à ce champ ne seront pas prises en compte.' ;
COMMENT ON COLUMN z_plume.meta_template_categories_full.is_mandatory IS 'True si une valeur doit obligatoirement être saisie pour cette catégorie. Le cas échéant, cette valeur se substituera pour le modèle considéré à la valeur renseignée dans le schéma des métadonnées communes. À noter que ce champ permet de rendre obligatoire une catégorie commune optionnelle, pas l''inverse.' ;
COMMENT ON COLUMN z_plume.meta_template_categories_full.sources IS 'Pour une catégorie prenant ses valeurs dans un ou plusieurs thésaurus, liste des sources admises. Cette information n''est considérée que pour les catégories communes. Il n''est pas possible d''ajouter des sources ni de les retirer toutes - Plume reviendrait alors à la liste initiale -, mais ce champ permet de restreindre la liste à un ou plusieurs thésaurus jugés les mieux adaptés.' ;
COMMENT ON COLUMN z_plume.meta_template_categories_full.geo_tools IS 'Pour une catégorie prenant pour valeurs des géométries, liste des fonctionnalités d''aide à la saisie à proposer. Cette information ne sera considérée que si le type (datatype) est ''gsp:wktLiteral''. Le cas échéant, cette valeur se substituera pour le modèle considéré à la valeur renseignée dans le schéma des métadonnées communes.' ;
COMMENT ON COLUMN z_plume.meta_template_categories_full.compute IS 'Liste des fonctionnalités de calcul à proposer. Cette information ne sera considérée que si une méthode de calcul est effectivement disponible pour la catégorie. Le cas échéant, cette valeur se substituera pour le modèle considéré à la valeur renseignée dans le schéma des métadonnées communes.' ;
COMMENT ON COLUMN z_plume.meta_template_categories_full.template_order IS 'Ordre d''apparence de la catégorie dans le formulaire. Les plus petits numéros sont affichés en premier. Plume classe les catégories selon l''ordre spécifié par le présent modèle, puis selon l''ordre défini par le schéma des métadonnées communes.' ;
COMMENT ON COLUMN z_plume.meta_template_categories_full.is_read_only IS 'True si la catégorie est en lecture seule.' ;
COMMENT ON COLUMN z_plume.meta_template_categories_full.tab IS 'Nom de l''onglet du formulaire où placer la catégorie. Cette information n''est considérée que pour les catégories locales et les catégories communes de premier niveau (par exemple "dcat:distribution / dct:issued" ira nécessairement dans le même onglet que "dcat:distribution"). Pour celles-ci, si aucun onglet n''est fourni, la catégorie ira toujours dans le premier onglet cité pour le modèle ou, à défaut, dans un onglet "Général".' ;
COMMENT ON COLUMN z_plume.meta_template_categories_full.compute_params IS 'Paramètres des fonctionnalités de calcul, le cas échéant, sous une forme clé-valeur. La clé est le nom du paramètre, la valeur sa valeur. Cette information ne sera considérée que si une méthode de calcul est effectivement disponible pour la catégorie et qu''elle attend un ou plusieurs paramètres. Le cas échéant, cette valeur se substituera pour le modèle considéré à la valeur renseignée dans le schéma des métadonnées communes.' ;


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
                ('Classique', 'dct:subject'),
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
                ('Donnée externe', 'dct:subject'),
                ('Donnée externe', 'foaf:page'),
                ('Donnée externe', 'owl:versionInfo'),
                ('Donnée externe', 'plume:isExternal')
            ) AS t (tpl_label, shrcat_path)
            WHERE t.tpl_label = tpl.tpl_label
        LOOP
        
            INSERT INTO z_plume.meta_template_categories
                (tpl_label, shrcat_path)
                VALUES (tpl.tpl_label, tplcat.shrcat_path) ;
        
        END LOOP ;
    
    END LOOP ;

    RETURN ;
    
END
$BODY$ ;

COMMENT ON FUNCTION z_plume.meta_import_sample_template(text) IS 'Importe l''un des modèles de formulaires pré-configurés (ou tous si l''argument n''est pas renseigné).' ;


-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


---------------------------------------
------ 2 - FONCTIONS UTILITAIRES ------
---------------------------------------

-- Function: z_plume.meta_execute_sql_filter(text, text, text)

CREATE OR REPLACE FUNCTION z_plume.meta_execute_sql_filter(
        sql_filter text, schema_name text, table_name text
        )
    RETURNS boolean
    LANGUAGE plpgsql
    AS $BODY$
/* Détermine si un filtre SQL est vérifié.

    Le filtre peut faire référence au nom du schéma avec $1
    et au nom de la table avec $2.

    Parameters
    ----------
    sql_filter : text
        Un filtre SQL exprimé sous la forme d'une
        chaîne de caractères.
    schema_name : text
        Le nom du schéma considéré.
    table_name : text
        Le nom de la table ou vue considérée.

    Returns
    -------
    boolean
        True si la condition du filtre est vérifiée.
        Si le filtre n'est pas valide, la fonction renvoie NULL,
        avec un message d'alerte. S'il n'y a pas de filtre, la
        fonction renvoie NULL. Si le filtre est valide mais non
        vérifié, la fonction renvoie False.
    
*/
DECLARE
    b boolean ;
BEGIN

    IF nullif(sql_filter, '') IS NULL
    THEN
        RETURN NULL ;
    END IF ;

    EXECUTE format('SELECT %s', sql_filter)
        INTO b
        USING schema_name, coalesce(table_name, '') ;
    RETURN b ;

EXCEPTION WHEN OTHERS
THEN
    RAISE NOTICE 'Filtre invalide : %', sql_filter ;
    RETURN NULL ;
END
$BODY$ ;

COMMENT ON FUNCTION z_plume.meta_execute_sql_filter(text, text, text) IS 'Détermine si un filtre SQL est vérifié.' ;


-- Function: z_plume.meta_ante_post_description(oid, text)

CREATE OR REPLACE FUNCTION z_plume.meta_ante_post_description(
        object_oid oid, catalog_name text
        )
    RETURNS text
    LANGUAGE plpgsql
    AS $BODY$
/* Extrait du descriptif de l'objet ce qui précède et suit les métadonnées.

    Parameters
    ----------
    object_oid : oid
        L'identifiant de l'objet considéré.
    catalog_name : text
        Le catalogue auquel appartient l'objet.

    Returns
    -------
    text
        Le descriptif de l'objet expurgé de ses métadonnées,
        c'est-à-dire sans les éventuelles balises <METADATA>
        et </METADATA> et leur contenu. Concrètement, cette
        partie du descriptif, si elle existait, est remplacée
        par une chaîne de caractères vide.
    
    Examples
    --------
    SELECT z_plume.meta_ante_post_description(
        'schema_name.table_name'::regclass, 'pg_class') ;
    
    Notes
    -----
    L'expression régulière utilisée par cette fonction est
    identique à celle du constructeur de la classe
    plume.pg.description.PgDescription du plugin QGIS. Il est
    impératif qu'elle le reste.

*/
BEGIN

    RETURN regexp_replace(
        obj_description(object_oid, catalog_name),
        '\n{0,2}<METADATA>(.*)</METADATA>\n{0,1}',
        ''
        ) ;

END
$BODY$ ;

COMMENT ON FUNCTION z_plume.meta_ante_post_description(oid, text) IS 'Extrait du descriptif de l''objet ce qui précède et suit les métadonnées.' ;


-- Function: z_plume.meta_description(oid, text)

CREATE OR REPLACE FUNCTION z_plume.meta_description(
        object_oid oid, catalog_name text
        )
    RETURNS jsonb
    LANGUAGE plpgsql
    AS $BODY$
/* Extrait les métadonnées du descriptif de l'objet.

    Parameters
    ----------
    object_oid : oid
        L'identifiant de l'objet considéré.
    catalog_name : text
        Le catalogue auquel appartient l'objet.

    Returns
    -------
    jsonb
        Les métadonnées, soit le contenu désérialisé des
        éventuelles balises <METADATA> et </METADATA>.
        NULL en l'absence des balises ou si leur contenu
        n'était pas un JSON valide.
    
    Examples
    --------
    SELECT z_plume.meta_description(
        'schema_name.table_name'::regclass, 'pg_class') ;
    
    Notes
    -----
    L'expression régulière utilisée par cette fonction est
    identique à celle du constructeur de la classe
    plume.pg.description.PgDescription du plugin QGIS. Il est
    impératif qu'elle le reste.

*/
BEGIN

    RETURN substring(obj_description(object_oid, catalog_name),
        '\n{0,2}<METADATA>(.*)</METADATA>\n{0,1}')::jsonb ;
    
EXCEPTION WHEN OTHERS THEN RETURN NULL ;
END
$BODY$ ;

COMMENT ON FUNCTION z_plume.meta_description(oid, text) IS 'Extrait les métadonnées du descriptif de l''objet.' ;


-- Function: z_plume.meta_regexp_matches(text, text, text)

CREATE OR REPLACE FUNCTION z_plume.meta_regexp_matches(
        string text, pattern text, flags text DEFAULT NULL
        )
    RETURNS TABLE (fragment text)
    LANGUAGE plpgsql
    AS $BODY$
/* Exécute la fonction regexp_matches avec le contrôle d'erreur adéquat.

    En particulier, elle renvoie une table vide (et un
    message d'alerte) au lieu d'échouer si l'expression
    régulière n'était pas valide.

    Cette fonction a aussi pour effet notable d'éclater
    les fragments capturés sur des lignes distinctes.

    Parameters
    ----------
    string : text
        Le texte dont on souhaite capturer un ou
        plusieurs fragments.
    pattern : text
        L'expression régulière délimitant les
        fragments.
    flags : text, optional
        Paramètres associés à l'expression régulière.

    Returns
    -------
    table (fragment : text)
        Une table avec un unique champ "fragment" de type
        text et autant de lignes que de fragments de texte
        extraits.
        
*/
DECLARE
    e_mssg text ;
BEGIN

    IF nullif(pattern, '') IS NULL OR nullif(string, '') IS NULL
    THEN
        RETURN ;
    END IF ;

    RETURN QUERY
        EXECUTE 'WITH a AS (SELECT unnest(regexp_matches($1, $2, $3)) AS b)
                    SELECT * FROM a WHERE b IS NOT NULL'
        USING string, pattern, coalesce(flags, '') ;

EXCEPTION WHEN OTHERS
THEN
    GET STACKED DIAGNOSTICS e_mssg = MESSAGE_TEXT ;
    RAISE NOTICE '%', e_mssg ;
    RETURN ;
END
$BODY$ ;

COMMENT ON FUNCTION z_plume.meta_regexp_matches(text, text, text) IS 'Exécute la fonction regexp_matches avec le contrôle d''erreur adéquat' ;


-- Function: z_plume.is_relowner(oid)

CREATE OR REPLACE FUNCTION z_plume.is_relowner(relid oid)
    RETURNS boolean
    LANGUAGE plpgsql
    AS $BODY$
/* Le rôle courant est-il propriétaire de la table ?

    Parameters
    ----------
    relid : oid
        L'identifiant d'une relation. S'il s'agit d'un OID
        non référencé, la fonction renverra False.

    Returns
    -------
    boolean
        True si le rôle courant est membre du rôle propriétaire
        de la table et hérite de ses privilèges.
    
*/
DECLARE
    b boolean ;
BEGIN
        
    SELECT pg_has_role(relowner, 'USAGE')
        INTO b
        FROM pg_catalog.pg_class
        WHERE oid = relid ;
    
    IF FOUND
    THEN
        RETURN b ;
    ELSE
        RETURN False ;
    END IF ;

END
$BODY$ ;


-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


---------------------------------------
------ 3 - DATES DE MODIFICATION ------
---------------------------------------

-- Table: z_plume.stamp_timestamp

CREATE TABLE z_plume.stamp_timestamp (
    relid oid PRIMARY KEY,
    created timestamp with time zone,
    modified timestamp with time zone
    ) ;

ALTER TABLE z_plume.stamp_timestamp ENABLE ROW LEVEL SECURITY ;

CREATE POLICY timestamp_public_select ON z_plume.stamp_timestamp
    FOR SELECT USING (True) ;
CREATE POLICY timestamp_owner_insert ON z_plume.stamp_timestamp
    FOR INSERT WITH CHECK (z_plume.is_relowner(relid)) ;
CREATE POLICY timestamp_owner_update ON z_plume.stamp_timestamp
    FOR UPDATE USING (z_plume.is_relowner(relid))
    WITH CHECK (z_plume.is_relowner(relid)) ;
CREATE POLICY timestamp_owner_delete ON z_plume.stamp_timestamp
    FOR DELETE USING (z_plume.is_relowner(relid)) ;

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE z_plume.stamp_timestamp TO public ;

COMMENT ON TABLE z_plume.stamp_timestamp IS 'Suivi des dates de modification des tables.' ;

COMMENT ON COLUMN z_plume.stamp_timestamp.relid IS 'Identifiant système de la table.' ;
COMMENT ON COLUMN z_plume.stamp_timestamp.created IS 'Date de création.' ;
COMMENT ON COLUMN z_plume.stamp_timestamp.modified IS 'Date de dernière modification.' ;


-- Function: z_plume.stamp_data_modification()

CREATE OR REPLACE FUNCTION z_plume.stamp_data_modification()
    RETURNS TRIGGER
    LANGUAGE plpgsql
    SECURITY DEFINER
    AS $BODY$
/* Fonction exécutée par les déclencheurs plume_stamp qui mettent à jour la date de dernière modification des tables.

    Elle enregistre la nouvelle date de dernière modification
    de la table dans la table stamp_timestamp.
    
    Cette fonction ne provoque pas d'erreur. En cas d'échec,
    elle se contente d'un message de notification.

*/
DECLARE
    e_mssg text ;
    e_hint text ;
    e_detl text ;
BEGIN

    UPDATE z_plume.stamp_timestamp
        SET modified = now()
        WHERE relid = TG_RELID ;
    
    IF NOT FOUND
    THEN
        INSERT INTO z_plume.stamp_timestamp (relid, modified)
            VALUES (TG_RELID, now()) ;
    END IF ;
    
    RETURN NULL ;

EXCEPTION WHEN OTHERS THEN

    GET STACKED DIAGNOSTICS
        e_mssg = MESSAGE_TEXT,
        e_hint = PG_EXCEPTION_HINT,
        e_detl = PG_EXCEPTION_DETAIL ;
        
    RAISE NOTICE '%', e_mssg
        USING DETAIL = e_detl,
            HINT = e_hint ;
    
    RETURN NULL ;

END
$BODY$ ;

COMMENT ON FUNCTION z_plume.stamp_data_modification() IS 'Fonction exécutée par les déclencheurs plume_stamp qui mettent à jour la date de dernière modification des tables.' ;


-- Function: z_plume.stamp_create_trigger(oid)

CREATE OR REPLACE FUNCTION z_plume.stamp_create_trigger(tabid oid)
    RETURNS boolean
    LANGUAGE plpgsql
    AS $BODY$
/* Crée sur la table cible un déclencheur qui assurera la mise à jour de sa date de modification.

    Elle ajoute également une entrée pour la table dans
    z_plume.stamp_timestamp.

    Cette fonction doit être exécutée par un rôle membre du
    propriétaire de la table et disposant de droits d'écriture
    sur z_plume.stamp_timestamp pour donner un résultat probant.
    Néanmoins, elle ne provoque pas d'erreur. En cas d'échec,
    elle se contente d'un message de notification.

    Parameters
    ----------
    tabid : oid
        L'identifiant de la table sur laquelle le déclencheur
        doit être créé.

    Returns
    -------
    boolean
        True si la création du déclencheur a réussi.
        En cas d'échec, elle renvoie False et le détail
        de l'erreur sera précisé par un message.
    
*/
DECLARE
    e_mssg text ;
    e_hint text ;
    e_detl text ;
BEGIN
        
    EXECUTE format('
        CREATE TRIGGER plume_stamp_action
            AFTER INSERT OR DELETE OR UPDATE OR TRUNCATE
            ON %1$s
            FOR EACH STATEMENT
            EXECUTE PROCEDURE z_plume.stamp_data_modification() ;
        ALTER TRIGGER plume_stamp_action ON %1$s DEPENDS ON EXTENSION plume_pg ;
        COMMENT ON TRIGGER plume_stamp_action ON %1$s
            IS ''Mise à jour de la date de dernière modification de la table.'' ;
        ', tabid::regclass) ;
    
    INSERT INTO z_plume.stamp_timestamp (relid)
        VALUES (tabid)
        ON CONFLICT (relid) DO NOTHING ;
    
    RETURN True ;

EXCEPTION WHEN OTHERS THEN

    GET STACKED DIAGNOSTICS
        e_mssg = MESSAGE_TEXT,
        e_hint = PG_EXCEPTION_HINT,
        e_detl = PG_EXCEPTION_DETAIL ;
        
    RAISE NOTICE '%', e_mssg
        USING DETAIL = e_detl,
            HINT = e_hint ;
            
    RETURN False ;

END
$BODY$ ;

COMMENT ON FUNCTION z_plume.stamp_create_trigger(oid) IS 'Crée sur la table cible un déclencheur qui assurera la mise à jour de sa date de modification.' ;


-- Function: z_plume.stamp_table_creation()

CREATE OR REPLACE FUNCTION z_plume.stamp_table_creation()
    RETURNS event_trigger
    LANGUAGE plpgsql
    SECURITY DEFINER
    AS $BODY$
/* Fonction exécutée par le déclencheur sur évènement plume_stamp_creation, activé sur les créations de tables.

    Elle enregistre la date de création de la table dans la
    table stamp_timestamp et crée un déclencheur sur la table
    créée qui permettra de suivre ses modifications.
    
    Elle n'a pas d'effet sur les vues et plus généralement
    tous les types de relations qui ne sont pas de
    simples tables.
    
    Cette fonction ne provoque pas d'erreur. En cas d'échec,
    elle se contente d'un message de notification.

*/
DECLARE
    obj record ;
    e_mssg text ;
    e_hint text ;
    e_detl text ;
BEGIN

    FOR obj IN SELECT DISTINCT objid
        FROM pg_event_trigger_ddl_commands()
        WHERE object_type = 'table'
    LOOP
        
        PERFORM z_plume.stamp_create_trigger(obj.objid) ;
        
        UPDATE z_plume.stamp_timestamp
            SET created = now()
            WHERE relid = obj.objid ;
    
    END LOOP ;

EXCEPTION WHEN OTHERS THEN

    GET STACKED DIAGNOSTICS
        e_mssg = MESSAGE_TEXT,
        e_hint = PG_EXCEPTION_HINT,
        e_detl = PG_EXCEPTION_DETAIL ;
    
    RAISE NOTICE '%', e_mssg
        USING DETAIL = e_detl,
            HINT = e_hint ; 
END
$BODY$ ;

COMMENT ON FUNCTION z_plume.stamp_table_creation() IS 'Fonction exécutée par le déclencheur sur évènement plume_stamp_creation, activé sur les créations de tables.' ;


-- Event trigger: plume_stamp_creation

CREATE EVENT TRIGGER plume_stamp_creation ON ddl_command_end
    WHEN TAG IN ('CREATE TABLE', 'CREATE TABLE AS', 'CREATE SCHEMA', 'SELECT INTO')
    EXECUTE PROCEDURE z_plume.stamp_table_creation() ;

ALTER EVENT TRIGGER plume_stamp_creation DISABLE ;

COMMENT ON EVENT TRIGGER plume_stamp_creation IS 'Enregistrement des dates de création des tables et mise en place des déclencheurs assurant la mise à jour de la date de dernière modification des données.' ;


-- Function: z_plume.stamp_table_modification()

CREATE OR REPLACE FUNCTION z_plume.stamp_table_modification()
    RETURNS event_trigger
    LANGUAGE plpgsql
    SECURITY DEFINER
    AS $BODY$
/* Fonction exécutée par le déclencheur sur évènement plume_stamp_modification, activé par les commandes qui modifient la structure des tables.

    Elle enregistre la nouvelle date de dernière modification
    de la table dans la table stamp_timestamp.
    
    Elle n'a pas d'effet sur les vues et plus généralement
    tous les types de relations qui ne sont pas de
    simples tables.
    
    Elle n'a pas non plus d'effet si la table modifiée n'était
    pas référencée dans stamp_timestamp.
    
    Cette fonction ne provoque pas d'erreur. En cas d'échec,
    elle se contente d'un message de notification.

*/
DECLARE
    obj record ;
    e_mssg text ;
    e_hint text ;
    e_detl text ;
BEGIN

    FOR obj IN SELECT DISTINCT objid
        FROM pg_event_trigger_ddl_commands()
        WHERE object_type = 'table'
    LOOP
    
        UPDATE z_plume.stamp_timestamp
            SET modified = now()
            WHERE relid = obj.objid ;
    
    END LOOP ;

EXCEPTION WHEN OTHERS THEN

    GET STACKED DIAGNOSTICS
        e_mssg = MESSAGE_TEXT,
        e_hint = PG_EXCEPTION_HINT,
        e_detl = PG_EXCEPTION_DETAIL ;
        
    RAISE NOTICE '%', e_mssg
        USING DETAIL = e_detl,
            HINT = e_hint ;
END
$BODY$ ;

COMMENT ON FUNCTION z_plume.stamp_table_modification() IS 'Fonction exécutée par le déclencheur sur évènement plume_stamp_modification, activé par les commandes qui modifient la structure des tables.' ;


-- Event trigger: plume_stamp_rewrite

CREATE EVENT TRIGGER plume_stamp_modification ON ddl_command_end
    WHEN TAG IN ('ALTER TABLE')
    EXECUTE PROCEDURE z_plume.stamp_table_modification() ;

ALTER EVENT TRIGGER plume_stamp_modification DISABLE ;

COMMENT ON EVENT TRIGGER plume_stamp_modification IS 'Mise à jour des dates de dernière modification des tables.' ;


-- Function: z_plume.stamp_table_drop()

CREATE OR REPLACE FUNCTION z_plume.stamp_table_drop()
    RETURNS event_trigger
    LANGUAGE plpgsql
    SECURITY DEFINER
    AS $BODY$
/* Fonction exécutée par le déclencheur sur évènement plume_stamp_drop, activé par les commandes de suppression de tables.

    Elle supprime de la table stamp_timestamp Les 
    enregistrements correspondant aux tables
    supprimées, s'il y en avait.
    
    Cette fonction ne provoque pas d'erreur. En cas d'échec,
    elle se contente d'un message de notification.

*/
DECLARE
    obj record ;
    e_mssg text ;
    e_hint text ;
    e_detl text ;
BEGIN

    FOR obj IN SELECT DISTINCT objid
        FROM pg_event_trigger_dropped_objects()
        WHERE object_type = 'table'
    LOOP
    
        DELETE FROM z_plume.stamp_timestamp
            WHERE relid = obj.objid ;
    
    END LOOP ;

EXCEPTION WHEN OTHERS THEN

    GET STACKED DIAGNOSTICS
        e_mssg = MESSAGE_TEXT,
        e_hint = PG_EXCEPTION_HINT,
        e_detl = PG_EXCEPTION_DETAIL ;
        
    RAISE NOTICE '%', e_mssg
        USING DETAIL = e_detl,
            HINT = e_hint ;
END
$BODY$ ;

COMMENT ON FUNCTION z_plume.stamp_table_drop() IS 'Fonction exécutée par le déclencheur sur évènement plume_stamp_drop, activé par les commandes de suppression de tables.' ;


-- Event trigger: plume_stamp_drop

CREATE EVENT TRIGGER plume_stamp_drop ON sql_drop
    WHEN TAG IN ('DROP TABLE', 'DROP SCHEMA')
    EXECUTE PROCEDURE z_plume.stamp_table_drop() ;

ALTER EVENT TRIGGER plume_stamp_drop DISABLE ;

COMMENT ON EVENT TRIGGER plume_stamp_drop IS 'Suppression du suivi des dates de modification sur les tables supprimées.' ;


-- Function: z_plume.stamp_clean_timestamp()

CREATE OR REPLACE FUNCTION z_plume.stamp_clean_timestamp()
    RETURNS int
    LANGUAGE plpgsql
    AS $BODY$
/* Supprime les enregistrements de la table stamp_timestamp correspondant à des tables qui n'existent plus.

    Cette fonction doit être exécutée par le
    propriétaire de la table stamp_timestamp,
    sans quoi elle renverra une erreur.

    Returns
    -------
    int
        Nombre de lignes supprimées.
    
*/
DECLARE
    n int ;
BEGIN

    DELETE FROM z_plume.stamp_timestamp
        WHERE NOT relid IN (SELECT oid FROM pg_class) ;
        
    GET DIAGNOSTICS n = ROW_COUNT ;
    RETURN n ;

END
$BODY$ ;

COMMENT ON FUNCTION z_plume.stamp_clean_timestamp() IS 'Supprime les enregistrements de la table stamp_timestamp correspondant à des tables qui n''existent plus.' ;


-- Function: z_plume.stamp_record_modification_date()

CREATE OR REPLACE FUNCTION z_plume.stamp_record_modification_date()
    RETURNS TRIGGER
    LANGUAGE plpgsql
    SECURITY DEFINER
    AS $BODY$
/* Fonction exécutée par le déclencheur record_modification_date qui met à jour la date de dernière modification dans les métadonnées de la table.
    
    Cette fonction ne provoque pas d'erreur. En cas d'échec,
    elle se contente d'un message de notification. Elle
    n'aura pas d'effet si le descriptif de la table ne
    contient pas encore de fiche de métadonnées.

*/
DECLARE
    old_metadata jsonb ;
    new_metadata jsonb := '[]'::jsonb ;
    r record ;
    e_mssg text ;
    e_hint text ;
    e_detl text ;
BEGIN

    old_metadata := z_plume.meta_description(NEW.relid, 'pg_class') ;
    
    IF old_metadata IS NULL
    THEN
        RETURN NULL ;
    END IF ;
    
    -- boucle sur les éléments de premier niveau du JSON-LD
    FOR r IN (
        SELECT 
            item
            FROM jsonb_array_elements(old_metadata) AS t (item)
        )
    LOOP
    
        IF r.item @> '{"@type": ["http://www.w3.org/ns/dcat#Dataset"]}'
        THEN
            new_metadata := new_metadata || jsonb_build_array(jsonb_set(
                r.item, '{http://purl.org/dc/terms/modified}',
                jsonb_build_array(jsonb_build_object('@type',
                    'http://www.w3.org/2001/XMLSchema#dateTime',
                    '@value', NEW.modified)),
                create_if_missing := True
                )) ;
        ELSE
            new_metadata := new_metadata || jsonb_build_array(r.item) ;
        END IF ;
        
    END LOOP ;
    
    EXECUTE format(
        'COMMENT ON TABLE %s IS %L ;',
        NEW.relid::regclass,
        regexp_replace(
            obj_description(NEW.relid, 'pg_class'),
            '\n{0,2}<METADATA>(.*)</METADATA>\n{0,1}',
            format(
                '

<METADATA>
%s
</METADATA>
',
                jsonb_pretty(new_metadata)
                )
            )
        ) ;
    
    RETURN NULL ;

EXCEPTION WHEN OTHERS THEN

    GET STACKED DIAGNOSTICS
        e_mssg = MESSAGE_TEXT,
        e_hint = PG_EXCEPTION_HINT,
        e_detl = PG_EXCEPTION_DETAIL ;
        
    RAISE NOTICE '%', e_mssg
        USING DETAIL = e_detl,
            HINT = e_hint ;
    
    RETURN NULL ;

END
$BODY$ ;

COMMENT ON FUNCTION z_plume.stamp_record_modification_date() IS 'Fonction exécutée par le déclencheur record_modification_date qui enregistre la date de dernière modification dans les métadonnées de la table.' ;


-- Function: z_plume.stamp_activate_recording()

CREATE OR REPLACE FUNCTION z_plume.stamp_activate_recording()
    RETURNS boolean
    LANGUAGE plpgsql
    AS $BODY$
/* Crée ou supprime le déclencheur sur la table stamp_timestamp qui enregistre automatiquement les dates de modification dans les fiches de métadonnées.

    Si le déclencheur n'existait pas, il est créé. S'il existait,
    il est supprimé.

    Cette fonction doit être exécutée par un rôle membre du
    propriétaire de la table z_plume.stamp_timestamp.

    Returns
    -------
    boolean
        True si la création du déclencheur a réussi.
        False si la suppression du déclencheur a réussi.
        En cas d'échec, elle renvoie une erreur.
    
*/
DECLARE
    e_mssg text ;
    e_hint text ;
    e_detl text ;
BEGIN

    IF EXISTS (SELECT * FROM pg_catalog.pg_trigger
        WHERE tgrelid = 'z_plume.stamp_timestamp'::regclass
        AND tgname = 'record_modification_date')
    THEN
        DROP TRIGGER record_modification_date ON z_plume.stamp_timestamp ;
        
        RETURN False ;
    ELSE        
        CREATE TRIGGER record_modification_date
            AFTER INSERT OR UPDATE
            ON z_plume.stamp_timestamp
            FOR EACH ROW
            WHEN (NEW.modified IS NOT NULL)
            EXECUTE PROCEDURE z_plume.stamp_record_modification_date() ;
        
        COMMENT ON TRIGGER record_modification_date ON z_plume.stamp_timestamp
            IS 'Enregistre les dates de dernière modification dans les métadonnées des tables.' ;
        
        RETURN True ;
    END IF ;

END
$BODY$ ;

COMMENT ON FUNCTION z_plume.stamp_activate_recording() IS 'Crée ou supprime le déclencheur sur la table stamp_timestamp qui enregistre automatiquement les dates de modification dans les fiches de métadonnées.' ;


-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

