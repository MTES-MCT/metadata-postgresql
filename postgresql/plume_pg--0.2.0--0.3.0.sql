\echo Use "ALTER EXTENSION plume_pg UPDATE TO '0.2.0'" to load this file. \quit
-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
--
-- PlumePg - Système de gestion des métadonnées locales, version 0.3.0
-- > Script de mise à jour depuis la version 0.2.0
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
-- - Function: z_plume.stamp_create_triggers(text, text[], text[])
--
-- objets modifiés par le script :
-- - Table: z_plume.meta_shared_categorie
-- - Table: z_plume.meta_categorie
-- - Table: z_plume.meta_template_categories
-- - View: z_plume.meta_template_categories_full
-- - Function: z_plume.meta_import_sample_template(text)
--
-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

/* 1 - MODELES DE FORMULAIRES 
   3 - DATES DE MODIFICATION */

-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

----------------------------------------
------ 1 - MODELES DE FORMULAIRES ------
----------------------------------------

/* 1.1 - TABLE DE CATEGORIES
   1.4 - ASSOCIATION DES CATEGORIES AUX MODELES
   1.5 - IMPORT DE MODELES PRE-CONFIGURES */


------ 1.1 - TABLE DE CATEGORIES ------

-- Table: z_plume.meta_shared_categorie

UPDATE z_plume.meta_shared_categorie
    SET sources = sources || ARRAY[
        'http://registre.data.developpement-durable.gouv.fr/ecospheres/themes-ecospheres',
        'http://inspire.ec.europa.eu/metadata-codelist/SpatialScope',
        'http://inspire.ec.europa.eu/metadata-codelist/PriorityDataset'
    ]
    WHERE sources IS NOT NULL AND path = 'dcat:theme' ;

UPDATE z_plume.meta_shared_categorie
    SET description = 'Classification thématique du jeu de données.'
    WHERE path = 'dcat:theme' ;

UPDATE z_plume.meta_shared_categorie
    SET is_node = False,
        sources = ARRAY[
            'http://registre.data.developpement-durable.gouv.fr/plume/EuAdministrativeTerritoryUnitFrance',
            'http://id.insee.fr/geo/departement',
            'http://id.insee.fr/geo/region',
            'http://registre.data.developpement-durable.gouv.fr/plume/InseeIndividualTerritory',
            'http://publications.europa.eu/resource/authority/atu',
            'http://id.insee.fr/geo/commune'
        ],
        special = 'url'
    WHERE path IN (
        'dct:spatial',
        'dcat:distribution / dcat:accessService / dct:spatial'
    ) ;

UPDATE z_plume.meta_shared_categorie
    SET sources = ARRAY['http://registre.data.developpement-durable.gouv.fr/plume/OgcEpsgFrance']
        || sources
        || ARRAY['http://registre.data.developpement-durable.gouv.fr/plume/IgnCrs']
    WHERE sources IS NOT NULL AND path IN (
        'dct:conformsTo',
        'dcat:distribution / dcat:accessService / dct:conformsTo',
        'dcat:distribution / dct:conformsTo'
    ) ;

UPDATE z_plume.meta_shared_categorie
    SET sources = sources
        || ARRAY[
            'http://registre.data.developpement-durable.gouv.fr/plume/ISO19139ClassificationCode',
            'http://registre.data.developpement-durable.gouv.fr/plume/ISO19139RestrictionCode'
        ]
    WHERE sources IS NOT NULL AND path IN (
        'dct:accessRights',
        'dcat:distribution / dcat:accessService / dct:accessRights',
        'dcat:distribution / dct:accessRights'
    ) ;

UPDATE z_plume.meta_shared_categorie
    SET template_order = 30
    WHERE template_order = 32 AND path = 'dcat:distribution / dct:accessRights' ;

UPDATE z_plume.meta_shared_categorie
    SET template_order = 32
    WHERE template_order = 30 AND path = 'dcat:distribution / dct:rights' ;

UPDATE z_plume.meta_shared_categorie
    SET sources = sources
        || ARRAY['http://registre.data.developpement-durable.gouv.fr/plume/IanaMediaType']
    WHERE sources IS NOT NULL AND path IN (
        'dcat:distribution / dct:format',
        'dcat:distribution / dcat:compressFormat',
        'dcat:distribution / dcat:packageFormat'
    ) ;

UPDATE z_plume.meta_shared_categorie
    SET compute = ARRAY['manual']
    WHERE path = 'dct:conformsTo' ;

UPDATE z_plume.meta_shared_categorie
    SET sources = sources || ARRAY['http://registre.data.developpement-durable.gouv.fr/plume/SpdxLicense']
    WHERE sources IS NOT NULL AND path = 'dcat:distribution / dct:license' ;

UPDATE z_plume.meta_shared_categorie
    SET label = 'Statut',
        description = 'Maturité de la distribution.'
    WHERE path = 'dcat:distribution / adms:status' ;

UPDATE z_plume.meta_shared_categorie
    SET sources = sources || ARRAY[
        'http://registre.data.developpement-durable.gouv.fr/plume/ISO3166CodesCollection'
    ]
    WHERE sources IS NOT NULL AND path IN (
        'dcat:distribution / dcat:accessService / dct:spatial / skos:inScheme',
        'dct:spatial / skos:inScheme'
    ) ;

UPDATE z_plume.meta_shared_categorie
    SET is_multiple = true 
    WHERE path IN (
        'dcat:spatialResolutionInMeters',
        'dcat:distribution / dcat:spatialResolutionInMeters',
        'dcat:distribution / dcat:accessService / dcat:spatialResolutionInMeters'
    ) ;

DELETE FROM z_plume.meta_shared_categorie
    WHERE path = 'dcat:distribution / cnt:characterEncoding' ;

UPDATE z_plume.meta_shared_categorie
    SET sources = sources || ARRAY[
        'http://inspire.ec.europa.eu/metadata-codelist/SpatialDataServiceType'
    ]
    WHERE sources IS NOT NULL AND path = 'dcat:distribution / dcat:accessService / dct:type' ;

UPDATE z_plume.meta_shared_categorie
    SET is_mandatory = False
    WHERE path = 'dcat:distribution / dcat:accessURL' ;

UPDATE z_plume.meta_shared_categorie
    SET is_multiple = True,
        label = 'Contraintes légales',
        description = 'Autre contrainte d''ordre juridique applicable à la distribution (propriété intellectuelle, etc.).',
        special = 'url',
        is_node = False,
        sources = ARRAY['http://registre.data.developpement-durable.gouv.fr/plume/ISO19139RestrictionCode']
    WHERE path = 'dcat:distribution / dct:rights' ;

INSERT INTO z_plume.meta_shared_categorie (
        path, origin, label, description, special,
        is_node, datatype, is_long_text, rowspan,
        placeholder, input_mask, is_multiple, unilang,
        is_mandatory, sources, geo_tools, compute,
        template_order
    ) VALUES
    ('dqv:hasQualityMeasurement', 'shared', 'Résolution spatiale', 'Spécification du niveau de détail des données.', NULL, true, NULL, false, NULL, NULL, NULL, true, false, false, NULL, NULL, NULL, 25),
    ('dqv:hasQualityMeasurement / dqv:isMeasurementOf', 'shared', 'Indicateur', 'Critère d''évaluation de la résolution.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://registre.data.developpement-durable.gouv.fr/plume/GeoDCATMetric'], NULL, NULL, 0),
    ('dqv:hasQualityMeasurement / dqv:value', 'shared', 'Valeur', 'Valeur de la résolution.', NULL, false, 'xsd:decimal', false, NULL, NULL, NULL, false, false, false, NULL, NULL, NULL, 1),
    ('dqv:hasQualityMeasurement / sdmx-attribute:unitMeasure', 'shared', 'Unité de mesure', 'Unité dans laquelle est exprimée la résolution, le cas échéant.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://publications.europa.eu/resource/authority/measurement-unit','http://qudt.org/vocab/unit'], NULL, NULL, 2),
    ('dcat:distribution / dcat:accessService / dqv:hasQualityMeasurement', 'shared', 'Résolution spatiale', 'Spécification du niveau de détail des données mises à disposition par le service.', NULL, true, NULL, false, NULL, NULL, NULL, true, false, false, NULL, NULL, NULL, 83),
    ('dcat:distribution / dcat:accessService / dqv:hasQualityMeasurement / dqv:isMeasurementOf', 'shared', 'Indicateur', 'Critère d''évaluation de la résolution.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://registre.data.developpement-durable.gouv.fr/plume/GeoDCATMetric'], NULL, NULL, 0),
    ('dcat:distribution / dcat:accessService / dqv:hasQualityMeasurement / dqv:value', 'shared', 'Valeur', 'Valeur de la résolution.', NULL, false, 'xsd:decimal', false, NULL, NULL, NULL, false, false, false, NULL, NULL, NULL, 1),
    ('dcat:distribution / dcat:accessService / dqv:hasQualityMeasurement / sdmx-attribute:unitMeasure', 'shared', 'Unité de mesure', 'Unité dans laquelle est exprimée la résolution, le cas échéant.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://publications.europa.eu/resource/authority/measurement-unit','http://qudt.org/vocab/unit'], NULL, NULL, 2),
    ('dcat:distribution / dqv:hasQualityMeasurement', 'shared', 'Résolution spatiale', 'Spécification du niveau de détail de la distribution.', NULL, true, NULL, false, NULL, NULL, NULL, true, false, false, NULL, NULL, NULL, 25),
    ('dcat:distribution / dqv:hasQualityMeasurement / dqv:isMeasurementOf', 'shared', 'Indicateur', 'Critère d''évaluation de la résolution.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://registre.data.developpement-durable.gouv.fr/plume/GeoDCATMetric'], NULL, NULL, 0),
    ('dcat:distribution / dqv:hasQualityMeasurement / dqv:value', 'shared', 'Valeur', 'Valeur de la résolution.', NULL, false, 'xsd:decimal', false, NULL, NULL, NULL, false, false, false, NULL, NULL, NULL, 1),
    ('dcat:distribution / dqv:hasQualityMeasurement / sdmx-attribute:unitMeasure', 'shared', 'Unité de mesure', 'Unité dans laquelle est exprimée la résolution, le cas échéant.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://publications.europa.eu/resource/authority/measurement-unit','http://qudt.org/vocab/unit'], NULL, NULL, 2) ;

UPDATE z_plume.meta_shared_categorie
    SET template_order = 85
    WHERE path = 'dcat:distribution / dcat:accessService / dct:temporal' ;
UPDATE z_plume.meta_shared_categorie
    SET template_order = 86
    WHERE path = 'dcat:distribution / dcat:accessService / dcat:temporalResolution' ;

DROP VIEW z_plume.meta_template_categories_full ;

-- Table: z_plume.meta_categorie

ALTER TABLE z_plume.meta_categorie
    ALTER COLUMN unilang TYPE boolean USING (unilang::boolean) ;

-- Table: z_plume.meta_template_categories

ALTER TABLE z_plume.meta_template_categories
    ALTER COLUMN unilang TYPE boolean USING (unilang::boolean) ;


------ 1.4 - ASSOCIATION DES CATEGORIES AUX MODELES ------

-- View: z_plume.meta_template_categories_full

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
                -- (nom du modèle, chemin de la catégorie, vocabulaires à utiliser
                -- s'il y a lieu de restreindre la liste)
                ('Basique', 'dct:description', NULL),
                ('Basique', 'dct:modified', NULL),
                ('Basique', 'dct:temporal', NULL),
                ('Basique', 'dct:temporal / dcat:startDate', NULL),
                ('Basique', 'dct:temporal / dcat:endDate', NULL),
                ('Basique', 'dct:title', NULL),
                ('Basique', 'owl:versionInfo', NULL),
                
                ('Classique', 'adms:versionNotes', NULL),
                ('Classique', 'dcat:contactPoint', NULL),
                ('Classique', 'dcat:contactPoint / vcard:fn', NULL),
                ('Classique', 'dcat:contactPoint / vcard:hasEmail', NULL),
                ('Classique', 'dcat:contactPoint / vcard:hasTelephone', NULL),
                ('Classique', 'dcat:contactPoint / vcard:hasURL', NULL),
                ('Classique', 'dcat:contactPoint / vcard:organization-name', NULL),
                ('Classique', 'dcat:keyword', NULL),
                ('Classique', 'dcat:landingPage', NULL),
                ('Classique', 'dcat:spatialResolutionInMeters', NULL),
                ('Classique', 'dcat:theme', NULL),
                ('Classique', 'dct:accessRights', NULL),
                ('Classique', 'dct:accessRights / rdfs:label', NULL),
                ('Classique', 'dct:accrualPeriodicity', NULL),
                ('Classique', 'dct:conformsTo', ARRAY['http://registre.data.developpement-durable.gouv.fr/plume/OgcEpsgFrance', 'http://registre.data.developpement-durable.gouv.fr/plume/IgnCrs']),
                ('Classique', 'dct:conformsTo / dct:description', NULL),
                ('Classique', 'dct:conformsTo / dct:title', NULL),
                ('Classique', 'dct:conformsTo / dct:issued', NULL),
                ('Classique', 'dct:conformsTo / foaf:page', NULL),
                ('Classique', 'dct:conformsTo / owl:versionInfo', NULL),
                ('Classique', 'dct:created', NULL),
                ('Classique', 'dct:description', NULL),
                ('Classique', 'dct:identifier', NULL),
                ('Classique', 'dct:modified', NULL),
                ('Classique', 'dct:provenance', NULL),
                ('Classique', 'dct:provenance / rdfs:label', NULL),
                ('Classique', 'dct:spatial', ARRAY['http://registre.data.developpement-durable.gouv.fr/plume/EuAdministrativeTerritoryUnitFrance', 'http://id.insee.fr/geo/departement', 'http://id.insee.fr/geo/region', 'http://registre.data.developpement-durable.gouv.fr/plume/InseeIndividualTerritory']),
                ('Classique', 'dct:spatial / dct:identifier', NULL),
                ('Classique', 'dct:spatial / skos:inScheme', NULL),
                ('Classique', 'dct:spatial / skos:prefLabel', NULL),
                ('Classique', 'dct:temporal', NULL),
                ('Classique', 'dct:temporal / dcat:startDate', NULL),
                ('Classique', 'dct:temporal / dcat:endDate', NULL),
                ('Classique', 'dct:title', NULL),
                ('Classique', 'foaf:page', NULL),
                ('Classique', 'owl:versionInfo', NULL),
                ('Classique', 'plume:isExternal', NULL),
                
                ('Donnée externe', 'adms:versionNotes', NULL),
                ('Donnée externe', 'dcat:contactPoint', NULL),
                ('Donnée externe', 'dcat:contactPoint / vcard:fn', NULL),
                ('Donnée externe', 'dcat:contactPoint / vcard:hasEmail', NULL),
                ('Donnée externe', 'dcat:contactPoint / vcard:hasTelephone', NULL),
                ('Donnée externe', 'dcat:contactPoint / vcard:hasURL', NULL),
                ('Donnée externe', 'dcat:contactPoint / vcard:organization-name', NULL),
                ('Donnée externe', 'dcat:distribution', NULL),
                ('Donnée externe', 'dcat:distribution / dcat:accessURL', NULL),
                ('Donnée externe', 'dcat:distribution / dct:issued', NULL),
                ('Donnée externe', 'dcat:distribution / dct:license', NULL),
                ('Donnée externe', 'dcat:distribution / dct:license / rdfs:label', NULL),
                ('Donnée externe', 'dcat:keyword', NULL),
                ('Donnée externe', 'dcat:landingPage', NULL),
                ('Donnée externe', 'dcat:theme', NULL),
                ('Donnée externe', 'dct:accessRights', NULL),
                ('Donnée externe', 'dct:accessRights / rdfs:label', NULL),
                ('Donnée externe', 'dct:accrualPeriodicity', NULL),
                ('Donnée externe', 'dct:description', NULL),
                ('Donnée externe', 'dct:modified', NULL),
                ('Donnée externe', 'dct:provenance', NULL),
                ('Donnée externe', 'dct:provenance / rdfs:label', NULL),
                ('Donnée externe', 'dct:publisher', NULL),
                ('Donnée externe', 'dct:publisher / foaf:name', NULL),
                ('Donnée externe', 'dct:temporal', NULL),
                ('Donnée externe', 'dct:temporal / dcat:startDate', NULL),
                ('Donnée externe', 'dct:temporal / dcat:endDate', NULL),
                ('Donnée externe', 'dct:title', NULL),
                ('Donnée externe', 'dct:spatial', ARRAY['http://registre.data.developpement-durable.gouv.fr/plume/EuAdministrativeTerritoryUnitFrance', 'http://id.insee.fr/geo/departement', 'http://id.insee.fr/geo/region', 'http://registre.data.developpement-durable.gouv.fr/plume/InseeIndividualTerritory']),
                ('Donnée externe', 'dct:spatial / dct:identifier', NULL),
                ('Donnée externe', 'dct:spatial / skos:inScheme', NULL),
                ('Donnée externe', 'dct:spatial / skos:prefLabel', NULL),
                ('Donnée externe', 'foaf:page', NULL),
                ('Donnée externe', 'owl:versionInfo', NULL),
                ('Donnée externe', 'plume:isExternal', NULL)
            ) AS t (tpl_label, shrcat_path, sources)
            WHERE t.tpl_label = tpl.tpl_label
        LOOP
        
            INSERT INTO z_plume.meta_template_categories
                (tpl_id, shrcat_path, sources) (
                    SELECT meta_template.tpl_id, tplcat.shrcat_path, tplcat.sources
                        FROM z_plume.meta_template
                        WHERE meta_template.tpl_label = tpl.tpl_label
                ) ;
        
        END LOOP ;
    
    END LOOP ;

    RETURN ;
    
END
$BODY$ ;

COMMENT ON FUNCTION z_plume.meta_import_sample_template(text) IS 'Importe l''un des modèles de formulaires pré-configurés (ou tous si l''argument n''est pas renseigné).' ;

-- Table: z_plume.meta_template_categories

UPDATE z_plume.meta_template_categories
    SET sources = ARRAY[
        'http://registre.data.developpement-durable.gouv.fr/plume/EuAdministrativeTerritoryUnitFrance',
        'http://id.insee.fr/geo/departement',
        'http://id.insee.fr/geo/region',
        'http://registre.data.developpement-durable.gouv.fr/plume/InseeIndividualTerritory'
    ]
    WHERE meta_template_categories.tpl_id IN (
        SELECT meta_template.tpl_id
            FROM z_plume.meta_template
            WHERE tpl_label IN ('Données externe', 'Classique')
        ) AND shrcat_path = 'dct:spatial' ;

UPDATE z_plume.meta_template_categories
    SET sources = ARRAY[
        'http://registre.data.developpement-durable.gouv.fr/plume/OgcEpsgFrance',
        'http://registre.data.developpement-durable.gouv.fr/plume/IgnCrs'
    ]
    WHERE meta_template_categories.tpl_id IN (
        SELECT meta_template.tpl_id
            FROM z_plume.meta_template
            WHERE tpl_label = 'Classique'
        ) AND shrcat_path = 'dct:conformsTo' ;

-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

---------------------------------------
------ 3 - DATES DE MODIFICATION ------
---------------------------------------

/* 3.3 - MAINTENANCE */

----- 3.3 - MAINTENANCE ------

-- Function: z_plume.stamp_create_triggers(text, text[], text[])

CREATE OR REPLACE FUNCTION z_plume.stamp_create_triggers(
        target_schema text DEFAULT NULL,
        schemas_include text[] DEFAULT NULL,
        schemas_exclude text[] DEFAULT NULL
    )
    RETURNS TABLE (schema_name name, table_name name, result text)
    LANGUAGE plpgsql
    AS $BODY$
/* Crée sur les tables des schémas cibles des déclencheurs qui assureront la mise à jour de leurs dates de modification.

    Concrètement, cette fonction exécute z_plume.stamp_create_trigger(oid)
    sur une sélection de schémas spécifiés par l'opérateur. Si aucun
    paramètre n'est fourni, tous les schémas sont considérés à l'exception
    des schémas système (dont le nom commence par 'pg_') et du schéma
    information_schema.

    Si le rôle qui exécute la fonction n'est pas propriétaire
    de certaines des tables de ces schémas, leurs triggers ne seront
    pas créés. La fonction n'échoue pas, mais renverra False avec
    des messages explicitant les erreurs rencontrées.

    La fonction ne considère que les tables simples.

    Parameters
    ----------
    target_schema : text, optional
        L'identifiant d'un schéma sur les tables duquel des déclencheurs
        doivent être créés.
    schemas_include : text[], optional
        Une liste d'identifiants de schémas sur les tables desquels des
        déclencheurs doivent être créés. Ce paramètre n'est pas considéré
        si target_schema est fourni.
    schemas_exclude : text[], optional
        Si spécifié, la fonction crée des déclencheurs sur tous les schémas
        hors schémas système, information_schema et les schémas qu'il liste.
        Ce paramètre n'est pas considéré si target_schema ou schemas_include est
        fourni.

    Returns
    -------
    table (schema_name : text, table_name : text, result : text)
        Une table avec trois attributs :
        
        * "schema_name" est le nom du schéma.
        * "table_name" est le nom de la table.
        * "result" est le résultat de la tentative de création du 
          déclencheur. Il peut valoir 'success' si la création a réussi,
          'failure' si elle a échoué (le détail de l'erreur sera alors 
          précisé par des messages) ou 'trigger already exists' si le 
          déclencheur existait déjà, la fonction n'ayant alors aucun effet.

    Exemples
    --------
    SELECT * FROM z_plume.stamp_create_triggers()
    SELECT * FROM z_plume.stamp_create_triggers('c_bibliotheque')
    SELECT * FROM z_plume.stamp_create_triggers(schemas_exclude := 'c_bibliotheque')
    
*/
DECLARE
    rel record ;
    res boolean ;
BEGIN

    FOR rel in (
        SELECT nspname AS schema_name, pg_class.relname, pg_class.oid
            FROM pg_catalog.pg_namespace
                LEFT JOIN pg_catalog.pg_class
                    ON pg_namespace.oid = pg_class.relnamespace
            WHERE (
                target_schema IS NOT NULL AND target_schema = nspname::text
                OR schemas_include IS NOT NULL AND nspname = ANY(schemas_include)
                OR schemas_exclude IS NOT NULL AND NOT nspname = ANY(schemas_exclude)
            )
            AND NOT nspname ~ '^pg_' AND NOT nspname = 'information_schema'
            AND relkind = 'r'
    )
    LOOP
        IF rel.oid IN (
            SELECT tgrelid FROM pg_catalog.pg_trigger
                WHERE tgname = 'plume_stamp_data_edit'
            )
        THEN
            RETURN QUERY
                SELECT rel.schema_name, rel.relname, 'trigger already exists' ;
        ELSE
            SELECT z_plume.stamp_create_trigger(rel.oid) INTO res ;
            RETURN QUERY
                SELECT rel.schema_name, rel.relname,
                    CASE WHEN res THEN 'success' ELSE 'failure' END ;
        END IF ;
    END LOOP ;

END
$BODY$ ;

COMMENT ON FUNCTION z_plume.stamp_create_triggers(text, text[], text[]) IS 'Crée sur les tables des schémas cibles des déclencheurs qui assureront la mise à jour de leurs dates de modification.' ;

