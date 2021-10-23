\echo Use "CREATE EXTENSION metadata" to load this file. \quit
-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
--
-- Système de gestion des métadonnées locales
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
-- Documentation :
-- https://snum.scenari-community.org/Metada/Documentation/
--
-- GitHub :
-- https://github.com/MTES-MCT/metadata-postgresql
-- 
-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
--
-- Ce logiciel est un programme informatique complémentaire au système de
-- gestion de base de données PosgreSQL ("https://www.postgresql.org/"). Il
-- met en place côté serveur les objets nécessaires à la gestion des 
-- métadonnées, en complément du plugin QGIS "metadata_postgresql".
--
-- Ce logiciel est régi par la licence CeCILL-B soumise au droit français
-- et respectant les principes de diffusion des logiciels libres. Vous
-- pouvez utiliser, modifier et/ou redistribuer ce programme sous les
-- conditions de la licence CeCILL-B telle que diffusée par le CEA, le
-- CNRS et l'INRIA sur le site "http://www.cecill.info".
-- Lien SPDX : "https://spdx.org/licenses/CECILL-B.html".
--
-- En contrepartie de l'accessibilité au code source et des droits de copie,
-- de modification et de redistribution accordés par cette licence, il n'est
-- offert aux utilisateurs qu'une garantie limitée.  Pour les mêmes raisons,
-- seule une responsabilité restreinte pèse sur l'auteur du programme,  le
-- titulaire des droits patrimoniaux et les concédants successifs.
--
-- A cet égard l'attention de l'utilisateur est attirée sur les risques
-- associés au chargement,  à l'utilisation,  à la modification et/ou au
-- développement et à la reproduction du logiciel par l'utilisateur étant 
-- donné sa spécificité de logiciel libre, qui peut le rendre complexe à 
-- manipuler et qui le réserve donc à des développeurs et des professionnels
-- avertis possédant  des  connaissances  informatiques approfondies.  Les
-- utilisateurs sont donc invités à charger  et  tester  l'adéquation  du
-- logiciel à leurs besoins dans des conditions permettant d'assurer la
-- sécurité de leurs systèmes et ou de leurs données et, plus généralement, 
-- à l'utiliser et l'exploiter dans les mêmes conditions de sécurité. 
--
-- Le fait que vous puissiez accéder à cet en-tête signifie que vous avez 
-- pris connaissance de la licence CeCILL-B, et que vous en avez accepté
-- les termes.
--
-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
--
-- dépendances : pgcrypto
--
-- schéma contenant les objets : z_metadata
--
-- objets créés par le script :
-- - Schema: z_metadata
-- - Type: z_metadata.meta_widget_type
-- - Type: z_metadata.meta_data_type
-- - Table: z_metadata.meta_categorie
-- - Table: z_metadata.meta_shared_categorie
-- - Function: z_metadata.meta_shared_categorie_before_insert()
-- - Trigger: meta_shared_categorie_before_insert
-- - Table: z_metadata.meta_local_categorie
-- - Table: z_metadata.meta_template
-- - Table: z_metadata.meta_template_categories
-- - Function: z_metadata.meta_execute_sql_filter(text, text, text)
-- - View: z_metadata.meta_template_categories_full
-- - Function: z_metadata.meta_import_sample_template(text)
--
-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


/* 0 - SCHEMA z_metadata
   1 - MODELES DE FORMULAIRES */


-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

-----------------------------------
------ 0 - SCHEMA z_metadata ------
-----------------------------------

-- Schema: z_metadata

DO
$$
BEGIN

    IF NOT EXISTS (
        SELECT * FROM pg_namespace
            WHERE nspname = 'z_metadata'
        )
    THEN
    
        CREATE SCHEMA z_metadata ;
        
        COMMENT ON SCHEMA z_metadata IS 'Utilitaires pour la gestion des métadonnées.' ;
        
        -- si l'extension asgard est présente, on déclare g_admin
        -- comme producteur et g_consult comme lecteur pour le
        -- nouveau schéma
        IF EXISTS (
            SELECT * FROM pg_available_extensions
                WHERE name = 'asgard'
                    AND installed_version IS NOT NULL
            )
        THEN
            UPDATE z_asgard.gestion_schema_usr
                SET producteur = 'g_admin',
                    lecteur = 'g_consult'
                WHERE nom_schema = 'z_metadata' ;
        END IF ;
        
    END IF ;
    
    -- si le schéma existe déjà, il ne sera pas marqué comme
    -- dépendant de l'extension et les droits ne sont pas
    -- altérés. Il pourra être nécessaire de définir des permissions
    -- supplémentaires sur les objets créés par l'extension
    
END
$$ ;


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

-- Type: z_metadata.meta_widget_type

CREATE TYPE z_metadata.meta_widget_type AS ENUM (
    'QLineEdit', 'QTextEdit', 'QDateEdit', 'QDateTimeEdit', 'QCheckBox', 'QComboBox'
    ) ;
    
COMMENT ON TYPE z_metadata.meta_widget_type IS 'Métadonnées. Types de widgets de saisie supportés par le plugin QGIS de gestion des métadonnées.' ;


-- Type: z_metadata.meta_data_type

CREATE TYPE z_metadata.meta_data_type AS ENUM (
	'xsd:string', 'xsd:integer', 'xsd:decimal', 'xsd:float', 'xsd:double',
    'xsd:boolean', 'xsd:date', 'xsd:time', 'xsd:dateTime', 'xsd:duration',
    'gsp:wktLiteral', 'rdf:langString'
	) ;
	
COMMENT ON TYPE z_metadata.meta_data_type IS 'Métadonnées. Types de valeurs supportés par le plugin QGIS de gestion des métadonnées (correspondant aux types XMLSchema utilisés par le RDF).' ;


--Table: z_metadata.meta_categorie

CREATE TABLE z_metadata.meta_categorie (
    path text NOT NULL DEFAULT format('uuid:%s', gen_random_uuid()),
	origin text NOT NULL DEFAULT 'local',
	is_node boolean NOT NULL DEFAULT False,
    cat_label text NOT NULL,
	data_type z_metadata.meta_data_type,
    widget_type z_metadata.meta_widget_type,
    row_span int,
    help_text text,
    default_value text,
    placeholder_text text,
    input_mask text,
    multiple_values boolean,
    is_mandatory boolean,
    order_key int,
    CONSTRAINT meta_categorie_origin_check CHECK (origin IN ('local', 'shared')),
    CONSTRAINT meta_categorie_row_span_check CHECK (row_span BETWEEN 1 AND 99)
    )
    PARTITION BY LIST (origin) ;

COMMENT ON TABLE z_metadata.meta_categorie IS 'Métadonnées. Catégories de métadonnées disponibles pour les modèles de formulaires.' ;

COMMENT ON COLUMN z_metadata.meta_categorie.path IS 'Chemin SPARQL de la catégorie (identifiant unique). CE CHAMP EST GENERE AUTOMATIQUEMENT, NE PAS MODIFIER MANUELLEMENT.' ;
COMMENT ON COLUMN z_metadata.meta_categorie.origin IS 'Origine de la catégorie : ''shared'' pour une catégorie commune, ''local'' pour une catégorie locale supplémentaire. CE CHAMP EST GENERE AUTOMATIQUEMENT, NE PAS MODIFIER MANUELLEMENT.' ;
COMMENT ON COLUMN z_metadata.meta_categorie.is_node IS 'True si la catégorie est le nom d''un groupe qui contiendra lui-même d''autres catégories et non une catégorie à laquelle sera directement associée une valeur. Par exemple, is_node vaut True pour la catégorie correspondant au point de contact (dcat:contactPoint) et False pour le nom du point de contact (dcat:contactPoint / vcard:fn). CE CHAMP EST GENERE AUTOMATIQUEMENT, NE PAS MODIFIER MANUELLEMENT.' ;
COMMENT ON COLUMN z_metadata.meta_categorie.cat_label IS 'Libellé de la catégorie.' ;
COMMENT ON COLUMN z_metadata.meta_categorie.data_type IS 'Type de valeur attendu pour la catégorie. Pour les catégories communes, les modifications apportées à ce champ ne seront pas prises en compte.' ;
COMMENT ON COLUMN z_metadata.meta_categorie.widget_type IS 'Type de widget de saisie à utiliser.' ;
COMMENT ON COLUMN z_metadata.meta_categorie.row_span IS 'Nombre de lignes occupées par le widget de saisie, s''il y a lieu. La valeur ne sera considérée que pour un widget QTextEdit.' ;
COMMENT ON COLUMN z_metadata.meta_categorie.help_text IS 'Description de la catégorie. Sera affiché sous la forme d''un texte d''aide dans le formulaire.' ;
COMMENT ON COLUMN z_metadata.meta_categorie.default_value IS 'Valeur par défaut, le cas échéant.' ;
COMMENT ON COLUMN z_metadata.meta_categorie.placeholder_text IS 'Valeur fictive pré-affichée en tant qu''exemple dans le widget de saisie, s''il y a lieu. La valeur ne sera considérée que pour un widget QLineEdit ou QTextEdit.' ;
COMMENT ON COLUMN z_metadata.meta_categorie.input_mask IS 'Masque de saisie, s''il y a lieu.' ;
COMMENT ON COLUMN z_metadata.meta_categorie.multiple_values IS 'True si la catégorie admet plusieurs valeurs. Pour les catégories commnes, les modifications apportées à ce champ ne seront pas prises en compte.' ;
COMMENT ON COLUMN z_metadata.meta_categorie.is_mandatory IS 'True si une valeur doit obligatoirement être saisie pour cette catégorie.' ;
COMMENT ON COLUMN z_metadata.meta_categorie.order_key IS 'Ordre d''apparence de la catégorie dans le formulaire. Les plus petits numéros sont affichés en premier.' ;


-- Table: z_metadata.meta_shared_categorie

CREATE TABLE z_metadata.meta_shared_categorie 
    PARTITION OF z_metadata.meta_categorie (
        CONSTRAINT meta_shared_categorie_pkey PRIMARY KEY (path)
    )
    FOR VALUES IN ('shared') ;
    
COMMENT ON TABLE z_metadata.meta_shared_categorie IS 'Métadonnées. Catégories de métadonnées communes.' ;

COMMENT ON COLUMN z_metadata.meta_shared_categorie.path IS 'Chemin SPARQL de la catégorie (identifiant unique). NE PAS MODIFIER MANUELLEMENT.' ;
COMMENT ON COLUMN z_metadata.meta_shared_categorie.origin IS 'Origine de la catégorie. Toujours ''shared''. NE PAS MODIFIER MANUELLEMENT.' ;
COMMENT ON COLUMN z_metadata.meta_shared_categorie.is_node IS 'True si la catégorie est le nom d''un groupe qui contiendra lui-même d''autres catégories et non une catégorie à laquelle sera directement associée une valeur. Par exemple, is_node vaut True pour la catégorie correspondant au point de contact (dcat:contactPoint) et False pour le nom du point de contact (dcat:contactPoint / vcard:fn). NE PAS MODIFIER MANUELLEMENT.' ;
COMMENT ON COLUMN z_metadata.meta_shared_categorie.cat_label IS 'Libellé de la catégorie.' ;
COMMENT ON COLUMN z_metadata.meta_shared_categorie.data_type IS 'Type de valeur attendu pour la catégorie. ATTENTION : toute modification sur ce champ sera ignorée par le plugin QGIS.' ;
COMMENT ON COLUMN z_metadata.meta_shared_categorie.widget_type IS 'Type de widget de saisie à utiliser.' ;
COMMENT ON COLUMN z_metadata.meta_shared_categorie.row_span IS 'Nombre de lignes occupées par le widget de saisie, s''il y a lieu. La valeur ne sera considérée que pour un widget QTextEdit.' ;
COMMENT ON COLUMN z_metadata.meta_shared_categorie.help_text IS 'Description de la catégorie. Sera affiché sous la forme d''un texte d''aide dans le formulaire.' ;
COMMENT ON COLUMN z_metadata.meta_shared_categorie.default_value IS 'Valeur par défaut, le cas échéant.' ;
COMMENT ON COLUMN z_metadata.meta_shared_categorie.placeholder_text IS 'Valeur fictive pré-affichée en tant qu''exemple dans le widget de saisie, s''il y a lieu. La valeur ne sera considérée que pour un widget QLineEdit ou QTextEdit.' ;
COMMENT ON COLUMN z_metadata.meta_shared_categorie.input_mask IS 'Masque de saisie, s''il y a lieu.' ;
COMMENT ON COLUMN z_metadata.meta_shared_categorie.multiple_values IS 'True si la catégorie admet plusieurs valeurs. ATTENTION : toute modification sur ce champ sera ignorée par le plugin QGIS.' ;
COMMENT ON COLUMN z_metadata.meta_shared_categorie.is_mandatory IS 'True si une valeur doit obligatoirement être saisie pour cette catégorie. ATTENTION : modifier cette valeur permet de rendre obligatoire une catégorie commune optionnelle, mais pas l''inverse.' ;
COMMENT ON COLUMN z_metadata.meta_shared_categorie.order_key IS 'Ordre d''apparence de la catégorie dans le formulaire. Les plus petits numéros sont affichés en premier.' ;

-- la table est marquée comme table de configuration de l'extension
SELECT pg_extension_config_dump('z_metadata.meta_shared_categorie'::regclass, '') ;

-- extraction du schéma SHACL
INSERT INTO z_metadata.meta_categorie (
    origin, path, is_node, cat_label, data_type, widget_type,
    row_span, help_text, default_value, placeholder_text,
    input_mask, multiple_values, is_mandatory, order_key
    ) VALUES
    ('shared', 'dct:title', false, 'Libellé', 'rdf:langString', 'QLineEdit', NULL, 'Libellé explicite du jeu de données.', NULL, NULL, NULL, true, true, 0),
    ('shared', 'owl:versionInfo', false, 'Version', 'xsd:string', 'QLineEdit', NULL, 'Numéro de version ou millésime du jeu de données.', NULL, NULL, NULL, false, false, 1),
    ('shared', 'dct:description', false, 'Description', 'rdf:langString', 'QTextEdit', 15, 'Description du jeu de données.', NULL, NULL, NULL, true, true, 2),
    ('shared', 'snum:isExternal', false, 'Donnée externe', 'xsd:boolean', 'QCheckBox', NULL, 'S''agit-il de la reproduction d''un jeu de données produit par un tiers ?', NULL, NULL, NULL, false, false, 3),
    ('shared', 'dcat:theme', false, 'Thème', NULL, 'QComboBox', NULL, NULL, NULL, NULL, NULL, true, false, 4),
    ('shared', 'dct:subject', false, 'Catégorie ISO 19115', NULL, 'QComboBox', NULL, NULL, NULL, NULL, NULL, true, false, 5),
    ('shared', 'dcat:keyword', false, 'Mots-clé libres', 'rdf:langString', 'QLineEdit', NULL, NULL, NULL, NULL, NULL, true, false, 6),
    ('shared', 'dct:spatial', true, 'Couverture géographique', NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, false, 9),
    ('shared', 'dct:spatial / skos:inScheme', false, 'Index géographique', NULL, 'QComboBox', NULL, 'Type de lieu, index de référence pour l''identifiant (commune, département...).', NULL, NULL, NULL, false, false, 0),
    ('shared', 'dct:spatial / dct:identifier', false, 'Code géographique', 'xsd:string', 'QLineEdit', NULL, 'Code du département, code INSEE de la commune, etc.', NULL, NULL, NULL, true, false, 1),
    ('shared', 'dct:spatial / skos:prefLabel', false, 'Libellé', 'rdf:langString', 'QLineEdit', NULL, NULL, NULL, NULL, NULL, true, false, 2),
    ('shared', 'dct:spatial / dcat:bbox', false, 'Rectangle d''emprise', 'gsp:wktLiteral', 'QTextEdit', NULL, 'Rectangle d''emprise (BBox), au format textuel WKT.', NULL, 'POLYGON((2.1 48.3,2.1 50.5,1.8 50.5,1.8 48.3,2.1 48.3))', NULL, false, false, 3),
    ('shared', 'dct:spatial / dcat:centroid', false, 'Centroïde', 'gsp:wktLiteral', 'QLineEdit', NULL, 'Localisant du centre géographique des données, au format textuel WKT.', NULL, 'POINT(-71.064544 42.28787)', NULL, false, false, 4),
    ('shared', 'dct:spatial / locn:geometry', false, 'Géométrie', 'gsp:wktLiteral', 'QTextEdit', NULL, 'Emprise géométrique, au format textuel WKT.', NULL, NULL, NULL, false, false, 5),
    ('shared', 'dct:temporal', true, 'Couverture temporelle', NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, false, 10),
    ('shared', 'dct:temporal / dcat:startDate', false, 'Date de début', 'xsd:date', 'QDateEdit', NULL, NULL, NULL, NULL, '0000-00-00', false, false, 0),
    ('shared', 'dct:temporal / dcat:endDate', false, 'Date de fin', 'xsd:date', 'QDateEdit', NULL, NULL, NULL, NULL, '0000-00-00', false, false, 1),
    ('shared', 'dct:created', false, 'Date de création', 'xsd:date', 'QDateEdit', NULL, NULL, NULL, NULL, '0000-00-00', false, false, 11),
    ('shared', 'dct:modified', false, 'Date de dernière modification', 'xsd:date', 'QDateEdit', NULL, NULL, NULL, NULL, '0000-00-00', false, false, 12),
    ('shared', 'dct:issued', false, 'Date de publication', 'xsd:date', 'QDateEdit', NULL, NULL, NULL, NULL, '0000-00-00', false, false, 13),
    ('shared', 'dct:accrualPeriodicity', false, 'Fréquence de mise à jour', NULL, 'QComboBox', NULL, NULL, NULL, NULL, NULL, false, false, 14),
    ('shared', 'dct:provenance', true, 'Généalogie', NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, false, 20),
    ('shared', 'dct:provenance / rdfs:label', false, 'Texte', 'rdf:langString', 'QTextEdit', 20, NULL, NULL, NULL, NULL, true, false, 0),
    ('shared', 'adms:versionNotes', false, 'Note de version', 'rdf:langString', 'QTextEdit', NULL, 'Différences entre la version courante des données et les versions antérieures.', NULL, NULL, NULL, true, false, 21),
    ('shared', 'dct:conformsTo', true, 'Conforme à', NULL, NULL, NULL, 'Standard, schéma, référentiel...', NULL, NULL, NULL, true, false, 22),
    ('shared', 'dct:conformsTo / skos:inScheme', false, 'Registre', NULL, 'QComboBox', NULL, NULL, NULL, NULL, NULL, false, false, 0),
    ('shared', 'dct:conformsTo / dct:identifier', false, 'Identifiant', 'xsd:string', 'QLineEdit', NULL, 'Identifiant du standard, s''il y a lieu. Pour un système de coordonnées géographiques, il s''agit du code EPSG.', NULL, NULL, NULL, true, false, 1),
    ('shared', 'dct:conformsTo / dct:title', false, 'Libellé', 'rdf:langString', 'QLineEdit', NULL, 'Libellé explicite du standard.', NULL, NULL, NULL, true, false, 2),
    ('shared', 'dct:conformsTo / owl:versionInfo', false, 'Version', 'xsd:string', 'QLineEdit', NULL, 'Numéro ou code de la version du standard à laquelle se conforment les données.', NULL, NULL, NULL, false, false, 3),
    ('shared', 'dct:conformsTo / dct:description', false, 'Description', 'rdf:langString', 'QTextEdit', NULL, 'Description sommaire de l''objet du standard.', NULL, NULL, NULL, true, false, 4),
    ('shared', 'dct:conformsTo / dct:issued', false, 'Date de publication', 'xsd:date', 'QDateEdit', NULL, 'Date de publication du standard.', NULL, NULL, '0000-00-00', false, false, 5),
    ('shared', 'dct:conformsTo / dct:modified', false, 'Date de modification', 'xsd:date', 'QDateEdit', NULL, 'Date de la dernière modification du standard.', NULL, NULL, '0000-00-00', false, false, 6),
    ('shared', 'dct:conformsTo / dct:created', false, 'Date de création', 'xsd:date', 'QDateEdit', NULL, 'Date de création du standard.', NULL, NULL, '0000-00-00', false, false, 7),
    ('shared', 'dct:conformsTo / foaf:page', false, 'Page internet', NULL, 'QLineEdit', NULL, 'Chemin d''accès au standard ou URL d''une page contenant des informations sur le standard.', NULL, NULL, NULL, true, false, 8),
    ('shared', 'dct:conformsTo / dct:type', false, 'Type de standard', NULL, 'QComboBox', NULL, NULL, NULL, NULL, NULL, false, false, 9),
    ('shared', 'dcat:spatialResolutionInMeters', false, 'Résolution spatiale en mètres', 'xsd:decimal', 'QLineEdit', NULL, 'Plus petite distance significative dans le contexte du jeu de données, exprimée en mètres.', NULL, NULL, NULL, false, false, 24),
    ('shared', 'rdfs:comment', false, 'Commentaire sur la résolution spatiale', 'rdf:langString', 'QTextEdit', NULL, NULL, NULL, NULL, NULL, true, false, 25),
    ('shared', 'dcat:temporalResolution', false, 'Résolution temporelle', 'xsd:duration', 'QLineEdit', NULL, NULL, NULL, NULL, NULL, true, false, 26),
    ('shared', 'dct:accessRights', false, 'Conditions d''accès', NULL, 'QComboBox', NULL, NULL, NULL, NULL, NULL, true, false, 30),
    ('shared', 'dct:accessRights / rdfs:label', false, 'Mention', 'rdf:langString', 'QTextEdit', 4, NULL, NULL, NULL, NULL, true, false, 1),
    ('shared', 'dcat:contactPoint', true, 'Point de contact', NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, false, 40),
    ('shared', 'dcat:contactPoint / vcard:fn', false, 'Nom', 'xsd:string', 'QLineEdit', NULL, NULL, NULL, NULL, NULL, false, false, 1),
    ('shared', 'dcat:contactPoint / vcard:hasEmail', false, 'Courriel', NULL, 'QLineEdit', NULL, NULL, NULL, NULL, NULL, false, false, 2),
    ('shared', 'dcat:contactPoint / vcard:hasTelephone', false, 'Téléphone', NULL, 'QLineEdit', NULL, NULL, NULL, '+33-1-23-45-67-89', NULL, false, false, 3),
    ('shared', 'dcat:contactPoint / vcard:hasURL', false, 'Site internet', NULL, 'QLineEdit', NULL, NULL, NULL, NULL, NULL, false, false, 4),
    ('shared', 'dcat:contactPoint / vcard:organization-name', false, 'Organisme', 'xsd:string', 'QLineEdit', NULL, 'Le cas échéant, organisation dont le point de contact fait partie.', NULL, NULL, NULL, false, false, 5),
    ('shared', 'dct:publisher', true, 'Éditeur', NULL, NULL, NULL, 'Organisme ou personne qui assure la publication des données.', NULL, NULL, NULL, false, false, 41),
    ('shared', 'dct:publisher / foaf:name', false, 'Nom', 'xsd:string', 'QLineEdit', NULL, NULL, NULL, NULL, NULL, false, false, 0),
    ('shared', 'dct:publisher / dct:type', false, 'Type', NULL, 'QComboBox', NULL, NULL, NULL, NULL, NULL, false, false, 1),
    ('shared', 'dct:publisher / foaf:mbox', false, 'Courriel', NULL, 'QLineEdit', NULL, NULL, NULL, NULL, NULL, false, false, 2),
    ('shared', 'dct:publisher / foaf:phone', false, 'Téléphone', NULL, 'QLineEdit', NULL, NULL, NULL, '+33-1-23-45-67-89', NULL, false, false, 3),
    ('shared', 'dct:publisher / foaf:workplaceHomepage', false, 'Site internet', NULL, 'QLineEdit', NULL, NULL, NULL, NULL, NULL, false, false, 4),
    ('shared', 'dct:creator', true, 'Auteur', NULL, NULL, NULL, 'Principal responsable de la production des données.', NULL, NULL, NULL, false, false, 42),
    ('shared', 'dct:creator / foaf:name', false, 'Nom', 'xsd:string', 'QLineEdit', NULL, NULL, NULL, NULL, NULL, false, false, 0),
    ('shared', 'dct:creator / dct:type', false, 'Type', NULL, 'QComboBox', NULL, NULL, NULL, NULL, NULL, false, false, 1),
    ('shared', 'dct:creator / foaf:mbox', false, 'Courriel', NULL, 'QLineEdit', NULL, NULL, NULL, NULL, NULL, false, false, 2),
    ('shared', 'dct:creator / foaf:phone', false, 'Téléphone', NULL, 'QLineEdit', NULL, NULL, NULL, '+33-1-23-45-67-89', NULL, false, false, 3),
    ('shared', 'dct:creator / foaf:workplaceHomepage', false, 'Site internet', NULL, 'QLineEdit', NULL, NULL, NULL, NULL, NULL, false, false, 4),
    ('shared', 'dct:rightsHolder', true, 'Détenteur de droits', NULL, NULL, NULL, 'Organisme ou personne qui détient des droits sur les données.', NULL, NULL, NULL, true, false, 43),
    ('shared', 'dct:rightsHolder / foaf:name', false, 'Nom', 'xsd:string', 'QLineEdit', NULL, NULL, NULL, NULL, NULL, false, false, 0),
    ('shared', 'dct:rightsHolder / dct:type', false, 'Type', NULL, 'QComboBox', NULL, NULL, NULL, NULL, NULL, false, false, 1),
    ('shared', 'dct:rightsHolder / foaf:mbox', false, 'Courriel', NULL, 'QLineEdit', NULL, NULL, NULL, NULL, NULL, false, false, 2),
    ('shared', 'dct:rightsHolder / foaf:phone', false, 'Téléphone', NULL, 'QLineEdit', NULL, NULL, NULL, '+33-1-23-45-67-89', NULL, false, false, 3),
    ('shared', 'dct:rightsHolder / foaf:workplaceHomepage', false, 'Site internet', NULL, 'QLineEdit', NULL, NULL, NULL, NULL, NULL, false, false, 4),
    ('shared', 'geodcat:custodian', true, 'Gestionnaire', NULL, NULL, NULL, 'Organisme ou personne qui assume la maintenance des données.', NULL, NULL, NULL, true, false, 44),
    ('shared', 'geodcat:custodian / foaf:name', false, 'Nom', 'xsd:string', 'QLineEdit', NULL, NULL, NULL, NULL, NULL, false, false, 0),
    ('shared', 'geodcat:custodian / dct:type', false, 'Type', NULL, 'QComboBox', NULL, NULL, NULL, NULL, NULL, false, false, 1),
    ('shared', 'geodcat:custodian / foaf:mbox', false, 'Courriel', NULL, 'QLineEdit', NULL, NULL, NULL, NULL, NULL, false, false, 2),
    ('shared', 'geodcat:custodian / foaf:phone', false, 'Téléphone', NULL, 'QLineEdit', NULL, NULL, NULL, '+33-1-23-45-67-89', NULL, false, false, 3),
    ('shared', 'geodcat:custodian / foaf:workplaceHomepage', false, 'Site internet', NULL, 'QLineEdit', NULL, NULL, NULL, NULL, NULL, false, false, 4),
    ('shared', 'geodcat:distributor', true, 'Distributeur', NULL, NULL, NULL, 'Organisme ou personne qui assure la distribution des données.', NULL, NULL, NULL, true, false, 45),
    ('shared', 'geodcat:distributor / foaf:name', false, 'Nom', 'xsd:string', 'QLineEdit', NULL, NULL, NULL, NULL, NULL, false, false, 0),
    ('shared', 'geodcat:distributor / dct:type', false, 'Type', NULL, 'QComboBox', NULL, NULL, NULL, NULL, NULL, false, false, 1),
    ('shared', 'geodcat:distributor / foaf:mbox', false, 'Courriel', NULL, 'QLineEdit', NULL, NULL, NULL, NULL, NULL, false, false, 2),
    ('shared', 'geodcat:distributor / foaf:phone', false, 'Téléphone', NULL, 'QLineEdit', NULL, NULL, NULL, '+33-1-23-45-67-89', NULL, false, false, 3),
    ('shared', 'geodcat:distributor / foaf:workplaceHomepage', false, 'Site internet', NULL, 'QLineEdit', NULL, NULL, NULL, NULL, NULL, false, false, 4),
    ('shared', 'geodcat:originator', true, 'Commanditaire', NULL, NULL, NULL, 'Organisme ou personne qui est à l''origine de la création des données.', NULL, NULL, NULL, true, false, 46),
    ('shared', 'geodcat:originator / foaf:name', false, 'Nom', 'xsd:string', 'QLineEdit', NULL, NULL, NULL, NULL, NULL, false, false, 0),
    ('shared', 'geodcat:originator / dct:type', false, 'Type', NULL, 'QComboBox', NULL, NULL, NULL, NULL, NULL, false, false, 1),
    ('shared', 'geodcat:originator / foaf:mbox', false, 'Courriel', NULL, 'QLineEdit', NULL, NULL, NULL, NULL, NULL, false, false, 2),
    ('shared', 'geodcat:originator / foaf:phone', false, 'Téléphone', NULL, 'QLineEdit', NULL, NULL, NULL, '+33-1-23-45-67-89', NULL, false, false, 3),
    ('shared', 'geodcat:originator / foaf:workplaceHomepage', false, 'Site internet', NULL, 'QLineEdit', NULL, NULL, NULL, NULL, NULL, false, false, 4),
    ('shared', 'geodcat:principalInvestigator', true, 'Maître d''œuvre', NULL, NULL, NULL, 'Organisme ou personne chargée du recueil des informations.', NULL, NULL, NULL, true, false, 47),
    ('shared', 'geodcat:principalInvestigator / foaf:name', false, 'Nom', 'xsd:string', 'QLineEdit', NULL, NULL, NULL, NULL, NULL, false, false, 0),
    ('shared', 'geodcat:principalInvestigator / dct:type', false, 'Type', NULL, 'QComboBox', NULL, NULL, NULL, NULL, NULL, false, false, 1),
    ('shared', 'geodcat:principalInvestigator / foaf:mbox', false, 'Courriel', NULL, 'QLineEdit', NULL, NULL, NULL, NULL, NULL, false, false, 2),
    ('shared', 'geodcat:principalInvestigator / foaf:phone', false, 'Téléphone', NULL, 'QLineEdit', NULL, NULL, NULL, '+33-1-23-45-67-89', NULL, false, false, 3),
    ('shared', 'geodcat:principalInvestigator / foaf:workplaceHomepage', false, 'Site internet', NULL, 'QLineEdit', NULL, NULL, NULL, NULL, NULL, false, false, 4),
    ('shared', 'geodcat:processor', true, 'Intégrateur', NULL, NULL, NULL, 'Organisation ou personne qui a retraité les données.', NULL, NULL, NULL, true, false, 48),
    ('shared', 'geodcat:processor / foaf:name', false, 'Nom', 'xsd:string', 'QLineEdit', NULL, NULL, NULL, NULL, NULL, false, false, 0),
    ('shared', 'geodcat:processor / dct:type', false, 'Type', NULL, 'QComboBox', NULL, NULL, NULL, NULL, NULL, false, false, 1),
    ('shared', 'geodcat:processor / foaf:mbox', false, 'Courriel', NULL, 'QLineEdit', NULL, NULL, NULL, NULL, NULL, false, false, 2),
    ('shared', 'geodcat:processor / foaf:phone', false, 'Téléphone', NULL, 'QLineEdit', NULL, NULL, NULL, '+33-1-23-45-67-89', NULL, false, false, 3),
    ('shared', 'geodcat:processor / foaf:workplaceHomepage', false, 'Site internet', NULL, 'QLineEdit', NULL, NULL, NULL, NULL, NULL, false, false, 4),
    ('shared', 'geodcat:resourceProvider', true, 'Fournisseur de la ressource', NULL, NULL, NULL, 'Organisme ou personne qui diffuse les données, soit directement soit par l''intermédiaire d''un distributeur.', NULL, NULL, NULL, true, false, 49),
    ('shared', 'geodcat:resourceProvider / foaf:name', false, 'Nom', 'xsd:string', 'QLineEdit', NULL, NULL, NULL, NULL, NULL, false, false, 0),
    ('shared', 'geodcat:resourceProvider / dct:type', false, 'Type', NULL, 'QComboBox', NULL, NULL, NULL, NULL, NULL, false, false, 1),
    ('shared', 'geodcat:resourceProvider / foaf:mbox', false, 'Courriel', NULL, 'QLineEdit', NULL, NULL, NULL, NULL, NULL, false, false, 2),
    ('shared', 'geodcat:resourceProvider / foaf:phone', false, 'Téléphone', NULL, 'QLineEdit', NULL, NULL, NULL, '+33-1-23-45-67-89', NULL, false, false, 3),
    ('shared', 'geodcat:resourceProvider / foaf:workplaceHomepage', false, 'Site internet', NULL, 'QLineEdit', NULL, NULL, NULL, NULL, NULL, false, false, 4),
    ('shared', 'geodcat:user', true, 'Utilisateur', NULL, NULL, NULL, 'Organisme ou personne qui utilise les données.', NULL, NULL, NULL, true, false, 50),
    ('shared', 'geodcat:user / foaf:name', false, 'Nom', 'xsd:string', 'QLineEdit', NULL, NULL, NULL, NULL, NULL, false, false, 0),
    ('shared', 'geodcat:user / dct:type', false, 'Type', NULL, 'QComboBox', NULL, NULL, NULL, NULL, NULL, false, false, 1),
    ('shared', 'geodcat:user / foaf:mbox', false, 'Courriel', NULL, 'QLineEdit', NULL, NULL, NULL, NULL, NULL, false, false, 2),
    ('shared', 'geodcat:user / foaf:phone', false, 'Téléphone', NULL, 'QLineEdit', NULL, NULL, NULL, '+33-1-23-45-67-89', NULL, false, false, 3),
    ('shared', 'geodcat:user / foaf:workplaceHomepage', false, 'Site internet', NULL, 'QLineEdit', NULL, NULL, NULL, NULL, NULL, false, false, 4),
    ('shared', 'prov:qualifiedAttribution', true, 'Partie prenante', NULL, NULL, NULL, 'Entité ou personne intervenant dans le processus de création, de diffusion ou de maintenance de la donnée.', NULL, NULL, NULL, true, false, 51),
    ('shared', 'prov:qualifiedAttribution / prov:agent', true, 'Entité', NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, false, 0),
    ('shared', 'prov:qualifiedAttribution / prov:agent / foaf:name', false, 'Nom', 'xsd:string', 'QLineEdit', NULL, NULL, NULL, NULL, NULL, false, false, 0),
    ('shared', 'prov:qualifiedAttribution / prov:agent / dct:type', false, 'Type', NULL, 'QComboBox', NULL, NULL, NULL, NULL, NULL, false, false, 1),
    ('shared', 'prov:qualifiedAttribution / prov:agent / foaf:mbox', false, 'Courriel', NULL, 'QLineEdit', NULL, NULL, NULL, NULL, NULL, false, false, 2),
    ('shared', 'prov:qualifiedAttribution / prov:agent / foaf:phone', false, 'Téléphone', NULL, 'QLineEdit', NULL, NULL, NULL, '+33-1-23-45-67-89', NULL, false, false, 3),
    ('shared', 'prov:qualifiedAttribution / prov:agent / foaf:workplaceHomepage', false, 'Site internet', NULL, 'QLineEdit', NULL, NULL, NULL, NULL, NULL, false, false, 4),
    ('shared', 'prov:qualifiedAttribution / dcat:hadRole', false, 'Rôle', NULL, 'QComboBox', NULL, NULL, NULL, NULL, NULL, true, false, 1),
    ('shared', 'dcat:distribution', true, 'Distribution', NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, false, 59),
    ('shared', 'dcat:distribution / dct:accessURL', false, 'URL d''accès', NULL, 'QLineEdit', NULL, NULL, NULL, NULL, NULL, true, false, 1),
    ('shared', 'dcat:distribution / dct:issued', false, 'Date de publication', 'xsd:date', 'QDateEdit', NULL, NULL, NULL, NULL, '0000-00-00', false, false, 2),
    ('shared', 'dcat:distribution / dct:rights', true, 'Propriété intellectuelle', NULL, NULL, NULL, NULL, NULL, NULL, NULL, false, false, 3),
    ('shared', 'dcat:distribution / dct:rights / rdfs:label', false, 'Mention', 'rdf:langString', 'QTextEdit', 4, NULL, NULL, NULL, NULL, true, false, 1),
    ('shared', 'dcat:distribution / dct:license', false, 'Licence', NULL, 'QComboBox', NULL, NULL, NULL, NULL, NULL, false, false, 4),
    ('shared', 'dcat:distribution / dct:license / dct:type', false, 'Type', NULL, 'QComboBox', NULL, NULL, NULL, NULL, NULL, true, false, 1),
    ('shared', 'dcat:distribution / dct:license / rdfs:label', false, 'Termes', 'rdf:langString', 'QTextEdit', NULL, NULL, NULL, NULL, NULL, true, false, 2),
    ('shared', 'dcat:landingPage', false, 'Page internet', NULL, 'QLineEdit', NULL, 'URL de la fiche de métadonnées sur internet.', NULL, NULL, NULL, true, false, 60),
    ('shared', 'foaf:page', false, 'Ressource associée', NULL, 'QLineEdit', NULL, 'Chemin d''une page internet ou d''un document en rapport avec les données.', NULL, NULL, NULL, true, false, 61),
    ('shared', 'dct:language', false, 'Langue des données', NULL, 'QComboBox', NULL, NULL, 'http://publications.europa.eu/resource/authority/language/FRA', NULL, NULL, true, false, 80),
    ('shared', 'snum:relevanceScore', false, 'Score', 'xsd:integer', 'QLineEdit', NULL, 'plus le score est élevé plus la donnée est mise en avant dans les résultats de recherche.', NULL, NULL, NULL, false, false, 81),
    ('shared', 'dct:type', false, 'Type de jeu de données', NULL, 'QComboBox', NULL, NULL, 'http://publications.europa.eu/resource/authority/dataset-type/GEOSPATIAL', NULL, NULL, false, false, 82),
    ('shared', 'dct:identifier', false, 'Identifiant interne', 'xsd:string', 'QLineEdit', NULL, NULL, NULL, NULL, NULL, false, false, 83),
    ('shared', 'adms:identifier', false, 'Autre identifiant', NULL, 'QLineEdit', NULL, NULL, NULL, NULL, NULL, true, false, 84) ;


-- Function: z_metadata.meta_shared_categorie_before_insert()

CREATE OR REPLACE FUNCTION z_metadata.meta_shared_categorie_before_insert()
	RETURNS trigger
    LANGUAGE plpgsql
    AS $BODY$
/* OBJET : Fonction exécutée par le trigger meta_shared_categorie_before_insert,
qui supprime les lignes pré-existantes (même valeur de "path") faisant l'objet
de commandes INSERT. Autrement dit, elle permet d'utiliser des commandes INSERT
pour réaliser des UPDATE.

Ne vaut que pour les catégories des métadonnées communes (les seules stockées
dans z_metadata.meta_shared_categorie).

Cette fonction est nécessaire pour que l'extension metadata puisse initialiser
la table avec les catégories partagées, et que les modifications faites par
l'administrateur sur ces enregistrements puissent ensuite être préservées en cas
de sauvegarde/restauration (table marquée comme table de configuration de
l'extension).

CIBLE : z_metadata.meta_shared_categorie.
PORTEE : FOR EACH ROW.
DECLENCHEMENT : BEFORE INSERT.*/
BEGIN
	
	DELETE FROM z_metadata.meta_shared_categorie
		WHERE meta_shared_categorie.path = NEW.path ;
		
	RETURN NEW ;

END
$BODY$ ;

COMMENT ON FUNCTION z_metadata.meta_shared_categorie_before_insert() IS 'Fonction exécutée par le trigger meta_shared_categorie_before_insert, qui supprime les lignes pré-existantes (même valeur de "path") faisant l''objet de commandes INSERT.' ;


-- Trigger: meta_shared_categorie_before_insert

CREATE TRIGGER meta_shared_categorie_before_insert
    BEFORE INSERT
    ON z_metadata.meta_shared_categorie
    FOR EACH ROW
    EXECUTE PROCEDURE z_metadata.meta_shared_categorie_before_insert() ;
	
COMMENT ON TRIGGER meta_shared_categorie_before_insert ON z_metadata.meta_shared_categorie IS 'Supprime les lignes pré-existantes (même valeur de "path") faisant l''objet de commandes INSERT.' ;


-- Table: z_metadata.meta_local_categorie

CREATE TABLE z_metadata.meta_local_categorie 
    PARTITION OF z_metadata.meta_categorie (
        CONSTRAINT meta_local_categorie_pkey PRIMARY KEY (path),
        CONSTRAINT meta_local_categorie_path_check CHECK (path ~ '^uuid[:][0-9a-z-]{36}$'),
        CONSTRAINT meta_local_categorie_widget_check CHECK (NOT widget_type = 'QComboBox'),
		CONSTRAINT meta_local_categorie_is_node_check CHECK (NOT is_node)
    )
    FOR VALUES IN ('local') ;
    
COMMENT ON TABLE z_metadata.meta_local_categorie IS 'Métadonnées. Catégories de métadonnées supplémentaires (ajouts locaux).' ;

COMMENT ON COLUMN z_metadata.meta_local_categorie.path IS 'Chemin SPARQL de la catégorie (identifiant unique). CE CHAMP EST GENERE AUTOMATIQUEMENT, NE PAS MODIFIER MANUELLEMENT.' ;
COMMENT ON COLUMN z_metadata.meta_local_categorie.origin IS 'Origine de la catégorie. Toujours ''local''. CE CHAMP EST GENERE AUTOMATIQUEMENT, NE PAS MODIFIER MANUELLEMENT.' ;
COMMENT ON COLUMN z_metadata.meta_categorie.is_node IS 'True si la catégorie est le nom d''un groupe qui contiendra lui-même d''autres catégories et non une catégorie à laquelle sera directement associée une valeur. Toujours False pour une catégorie locale. CE CHAMP EST GENERE AUTOMATIQUEMENT, NE PAS MODIFIER MANUELLEMENT.' ;
COMMENT ON COLUMN z_metadata.meta_local_categorie.cat_label IS 'Libellé de la catégorie.' ;
COMMENT ON COLUMN z_metadata.meta_local_categorie.data_type IS 'Type de valeur attendu pour la catégorie. Si ce champ n''est pas renseigné pour une catégorie locale, le plugin considérera qu''elle prend des valeurs de type ''xsd:string''.' ;
COMMENT ON COLUMN z_metadata.meta_local_categorie.widget_type IS 'Type de widget de saisie à utiliser. Si ce champ n''est pas renseigné pour une catégorie locale, le plugin utilisera des widgets QLineEdit.' ;
COMMENT ON COLUMN z_metadata.meta_local_categorie.row_span IS 'Nombre de lignes occupées par le widget de saisie, s''il y a lieu. La valeur ne sera considérée que pour un widget QTextEdit.' ;
COMMENT ON COLUMN z_metadata.meta_local_categorie.help_text IS 'Description de la catégorie. Sera affiché sous la forme d''un texte d''aide dans le formulaire.' ;
COMMENT ON COLUMN z_metadata.meta_local_categorie.default_value IS 'Valeur par défaut, le cas échéant.' ;
COMMENT ON COLUMN z_metadata.meta_local_categorie.placeholder_text IS 'Valeur fictive pré-affichée en tant qu''exemple dans le widget de saisie, s''il y a lieu. La valeur ne sera considérée que pour un widget QLineEdit ou QTextEdit.' ;
COMMENT ON COLUMN z_metadata.meta_local_categorie.input_mask IS 'Masque de saisie, s''il y a lieu.' ;
COMMENT ON COLUMN z_metadata.meta_local_categorie.multiple_values IS 'True si la catégorie admet plusieurs valeurs.' ;
COMMENT ON COLUMN z_metadata.meta_local_categorie.is_mandatory IS 'True si une valeur doit obligatoirement être saisie pour cette catégorie.' ;
COMMENT ON COLUMN z_metadata.meta_local_categorie.order_key IS 'Ordre d''apparence de la catégorie dans le formulaire. Les plus petits numéros sont affichés en premier.' ;

-- la table est marquée comme table de configuration de l'extension
SELECT pg_extension_config_dump('z_metadata.meta_local_categorie'::regclass, '') ;


------ 1.2 - TABLE DES MODELES ------

-- Table: z_metadata.meta_template

CREATE TABLE z_metadata.meta_template (
    tpl_label varchar(48) PRIMARY KEY,
	sql_filter text,
    md_conditions jsonb,
    priority int,
	comment text
    ) ;
    
COMMENT ON TABLE z_metadata.meta_template IS 'Métadonnées. Modèles de formulaires définis pour le plugin QGIS.' ;

COMMENT ON COLUMN z_metadata.meta_template.tpl_label IS 'Nom du modèle (limité à 48 caractères).' ;
COMMENT ON COLUMN z_metadata.meta_template.sql_filter IS 'Condition à remplir pour que ce modèle soit appliqué par défaut à une fiche de métadonnées, sous la forme d''un filtre SQL. On pourra utiliser $1 pour représenter le nom du schéma et $2 le nom de la table.
Par exemple :
- ''$1 ~ ANY(ARRAY[''''^r_'''', ''''^e_'''']'' appliquera le modèle aux tables des schémas des blocs "données référentielles" (préfixe ''r_'') et "données externes" (préfixe ''e_'') de la nomenclature nationale ;
- ''pg_has_role(''''g_admin'''', ''''USAGE'''')'' appliquera le modèle pour toutes les fiches de métadonnées dès lors que l''utilisateur est membre du rôle g_admin.' ;
COMMENT ON COLUMN z_metadata.meta_template.md_conditions IS 'Ensemble de conditions sur les métadonnées appelant l''usage de ce modèle.
À présenter sous une forme clé/valeur, où la clé est le chemin de la catégorie et la valeur l''une des valeur prises par la catégorie.
Dans l''exemple suivant, le modèle sera retenu pour une donnée externe avec le mot-clé "IGN" (ensemble de conditions 1) ou pour une donnée publiée par l''IGN (ensemble de conditions 2) :
{
    "ensemble de conditions 1": {
        "snum:isExternal": True,
        "dcat:keyword": "IGN"
        },
    "ensemble de conditions 2": {
        "dct:publisher / foaf:name": "Institut national de l''information géographique et forestière (IGN-F)"
        }
}
Les noms des ensembles n''ont pas d''incidence.
' ;
COMMENT ON COLUMN z_metadata.meta_template.priority IS 'Niveau de priorité du modèle.
Si un jeu de données remplit les conditions de plusieurs modèles, celui dont la priorité est la plus élevée sera retenu comme modèle par défaut.' ;
COMMENT ON COLUMN z_metadata.meta_template.comment IS 'Commentaire libre.' ;

-- la table est marquée comme table de configuration de l'extension
SELECT pg_extension_config_dump('z_metadata.meta_template'::regclass, '') ;


-- Function: z_metadata.meta_execute_sql_filter(text, text, text)

CREATE OR REPLACE FUNCTION z_metadata.meta_execute_sql_filter(
		sql_filter text, schema_name text, table_name text
		)
	RETURNS boolean
    LANGUAGE plpgsql
    AS $BODY$
/* OBJET : Détermine si un filtre SQL est vérifié.

Le filtre peut faire référence au nom du schéma avec $1
et au nom de la table avec $2.

ARGUMENTS :
- sql_filter : un filtre SQL exprimé sous la forme d'une
chaîne de caractères ;
- schema_name : le nom du schéma considéré ;
- table_name : le nom de la table ou vue considérée.

RESULTAT : True si la condition du filtre est vérifiée.
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

	EXECUTE 'SELECT ' || sql_filter
		INTO b
		USING schema_name, coalesce(table_name, '') ;
	RETURN b ;

EXCEPTION WHEN OTHERS
THEN
	RAISE NOTICE 'Filtre invalide : %', sql_filter ;
	RETURN NULL ;
END
$BODY$ ;

COMMENT ON FUNCTION z_metadata.meta_execute_sql_filter(text, text, text) IS 'Détermine si un filtre SQL est vérifié.' ;


---- 1.3 - TABLE DES ONGLETS ------

CREATE TABLE z_metadata.meta_tab (
    tab_name varchar(48) PRIMARY KEY,
    tab_num int
    ) ;
    
COMMENT ON TABLE z_metadata.meta_tab IS 'Métadonnées. Onglets des modèles.' ;

COMMENT ON COLUMN z_metadata.meta_tab.tab_name IS 'Nom de l''onglet.' ;
COMMENT ON COLUMN z_metadata.meta_tab.tab_num IS 'Numéro de l''onglet. Les onglets sont affichés du plus petit numéro au plus grand (NULL à la fin), puis par ordre alphabétique en cas d''égalité. Les numéros n''ont pas à se suivre et peuvent être répétés.' ;

-- la table est marquée comme table de configuration de l'extension
SELECT pg_extension_config_dump('z_metadata.meta_tab'::regclass, '') ;


---- 1.4 - ASSOCIATION DES CATEGORIES AUX MODELES ------

-- Table z_metadata.meta_template_categories

CREATE TABLE z_metadata.meta_template_categories (
    tplcat_id serial PRIMARY KEY,
    tpl_label varchar(48) NOT NULL,
    shrcat_path text,
    loccat_path text,
    cat_label text,
	data_type z_metadata.meta_data_type,
    widget_type z_metadata.meta_widget_type,
    row_span int,
    help_text text,
    default_value text,
    placeholder_text text,
    input_mask text,
    multiple_values boolean,
    is_mandatory boolean,
    order_key int,
    read_only boolean,
    tab_name varchar(48),
    CONSTRAINT meta_template_categories_tpl_cat_uni UNIQUE (tpl_label, shrcat_path, loccat_path),
    CONSTRAINT meta_template_categories_tpl_label_fkey FOREIGN KEY (tpl_label)
        REFERENCES z_metadata.meta_template (tpl_label)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT meta_template_categories_shrcat_path_fkey FOREIGN KEY (shrcat_path)
        REFERENCES z_metadata.meta_shared_categorie (path)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT meta_template_categories_loccat_path_fkey FOREIGN KEY (loccat_path)
        REFERENCES z_metadata.meta_local_categorie (path)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT meta_template_categories_tab_name_fkey FOREIGN KEY (tab_name)
        REFERENCES z_metadata.meta_tab (tab_name)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT meta_template_categories_path_check CHECK (
        shrcat_path IS NULL OR loccat_path IS NULL
        AND shrcat_path IS NOT NULL OR loccat_path IS NOT NULL
        ),
    CONSTRAINT meta_template_categories_row_span_check CHECK (row_span BETWEEN 1 AND 99)
    ) ;

COMMENT ON TABLE z_metadata.meta_template_categories IS 'Métadonnées. Désignation des catégories utilisées par chaque modèle de formulaire.
Les autres champs permettent de personnaliser la présentation des catégories pour le modèle considéré. S''ils ne sont pas renseignés, les valeurs saisies dans meta_categorie seront utilisées. À défaut, le plugin s''appuyera sur le schéma des catégories communes (évidemment pour les catégories communes uniquement).' ;

COMMENT ON COLUMN z_metadata.meta_template_categories.tplcat_id IS 'Identifiant unique.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories.tpl_label IS 'Nom du modèle de formulaire.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories.shrcat_path IS 'Chemin SPARQL / identifiant de la catégorie de métadonnées (si catégorie commune).' ;
COMMENT ON COLUMN z_metadata.meta_template_categories.loccat_path IS 'Chemin SPARQL / identifiant de la catégorie de métadonnées (si catégorie supplémentaire locale).' ;
COMMENT ON COLUMN z_metadata.meta_template_categories.cat_label IS 'Libellé de la catégorie de métadonnées. Si présente, cette valeur se substitue pour le modèle considéré à la valeur renseignée dans le champ éponyme de meta_categorie.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories.data_type IS 'Type de valeur attendu pour la catégorie. Si présente, cette valeur se substitue pour le modèle considéré à la valeur renseignée dans le champ éponyme de meta_categorie. ATTENTION : pour les catégories communes, les modifications apportées à ce champ ne seront pas prises en compte.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories.widget_type IS 'Type de widget de saisie à utiliser.
Si présente, cette valeur se substitue pour le modèle considéré à la valeur renseignée dans le champ éponyme de meta_categorie.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories.row_span IS 'Nombre de lignes occupées par le widget de saisie, s''il y a lieu. La valeur ne sera considérée que pour un widget QTextEdit. Si présente, cette valeur se substitue pour le modèle considéré à la valeur renseignée dans le champ éponyme de meta_categorie.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories.help_text IS 'Description de la catégorie. Sera affiché sous la forme d''un texte d''aide dans le formulaire. Si présente, cette valeur se substitue pour le modèle considéré à la valeur renseignée dans le champ éponyme de meta_categorie.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories.default_value IS 'Valeur par défaut, le cas échéant.
Si présente, cette valeur se substitue pour le modèle considéré à la valeur renseignée dans le champ éponyme de meta_categorie.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories.placeholder_text IS 'Valeur fictive pré-affichée en tant qu''exemple dans le widget de saisie, s''il y a lieu. La valeur ne sera considérée que pour un widget QLineEdit ou QTextEdit. Si présente, cette valeur se substitue pour le modèle considéré à la valeur renseignée dans le champ éponyme de meta_categorie.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories.input_mask IS 'Masque de saisie, s''il y a lieu. Si présente, cette valeur se substitue pour le modèle considéré à la valeur renseignée dans le champ éponyme de meta_categorie.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories.multiple_values IS 'True si la catégorie admet plusieurs valeurs. Si présente, cette valeur se substitue pour le modèle considéré à la valeur renseignée dans le champ éponyme de meta_categorie. ATTENTION : pour les catégories communes, les modifications apportées sur ce champ ne seront pas prises en compte.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories.is_mandatory IS 'True si une valeur doit obligatoirement être saisie pour cette catégorie. Si présente, cette valeur se substitue pour le modèle considéré à la valeur renseignée dans le champ éponyme de meta_categorie. ATTENTION : modifier cette valeur permet de rendre obligatoire une catégorie commune optionnelle, mais pas l''inverse.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories.order_key IS 'Ordre d''apparence de la catégorie dans le formulaire. Les plus petits numéros sont affichés en premier. Si présente, cette valeur se substitue pour le modèle considéré à la valeur renseignée dans le champ éponyme de meta_categorie.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories.read_only IS 'True si la catégorie est en lecture seule.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories.tab_name IS 'Nom de l''onglet du formulaire où placer la catégorie. Cette information n''est considérée que pour les catégories locales et les catégories communes de premier niveau (par exemple "dcat:distribution / dct:issued" ira nécessairement dans le même onglet que "dcat:distribution"). Pour celles-ci, si aucun onglet n''est fourni, la catégorie ira toujours dans le premier onglet cité pour le modèle dans la présente table ou, à défaut, dans un onglet "Général".' ;

-- la table et la séquence sont marquées comme tables de configuration de l'extension
SELECT pg_extension_config_dump('z_metadata.meta_template_categories'::regclass, '') ;
SELECT pg_extension_config_dump('z_metadata.meta_template_categories_tplcat_id_seq'::regclass, '') ;


-- View: z_metadata.meta_template_categories_full

CREATE VIEW z_metadata.meta_template_categories_full AS (
    SELECT
        tc.tplcat_id,
        t.tpl_label,
        coalesce(tc.shrcat_path, tc.loccat_path) AS path,
        c.origin,
		c.is_node,
        coalesce(tc.cat_label, c.cat_label) AS cat_label,
		coalesce(tc.data_type, c.data_type) AS data_type,
        coalesce(tc.widget_type, c.widget_type) AS widget_type,
        coalesce(tc.row_span, c.row_span) AS row_span,
        coalesce(tc.help_text, c.help_text) AS help_text,
        coalesce(tc.default_value, c.default_value) AS default_value,
        coalesce(tc.placeholder_text, c.placeholder_text) AS placeholder_text,
        coalesce(tc.input_mask, c.input_mask) AS input_mask,
        coalesce(tc.multiple_values, c.multiple_values) AS multiple_values,
        coalesce(tc.is_mandatory, c.is_mandatory) AS is_mandatory,
        coalesce(tc.order_key, c.order_key) AS order_key,
        tc.read_only,
        tc.tab_name
        FROM z_metadata.meta_template_categories AS tc
            LEFT JOIN z_metadata.meta_categorie AS c
                ON coalesce(tc.shrcat_path, tc.loccat_path) = c.path
            LEFT JOIN z_metadata.meta_template AS t
                ON tc.tpl_label = t.tpl_label
    ) ;

COMMENT ON VIEW z_metadata.meta_template_categories_full IS 'Métadonnées. Description complète des modèles de formulaire (rassemble les informations de meta_categorie et meta_template_categories).' ;

COMMENT ON COLUMN z_metadata.meta_template_categories_full.tplcat_id IS 'Identifiant unique.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories_full.tpl_label IS 'Nom du modèle.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories_full.path IS 'Chemin SPARQL / identifiant de la catégorie.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories_full.origin IS 'Origine de la catégorie : ''shared'' pour une catégorie commune, ''local'' pour une catégorie locale supplémentaire.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories_full.is_node IS 'True si la catégorie est le nom d''un groupe qui contiendra lui-même d''autres catégories et non une catégorie à laquelle sera directement associée une valeur. Par exemple, is_node vaut True pour la catégorie correspondant au point de contact (dcat:contactPoint) et False pour le nom du point de contact (dcat:contactPoint / vcard:fn).' ;
COMMENT ON COLUMN z_metadata.meta_template_categories_full.cat_label IS 'Libellé de la catégorie de métadonnées. Le cas échéant, cette valeur se substituera pour le modèle considéré à la valeur renseignée dans le schéma des métadonnées communes.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories_full.data_type IS 'Type de valeur attendu pour la catégorie.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories_full.widget_type IS 'Type de widget de saisie à utiliser. Le cas échéant, cette valeur se substituera pour le modèle considéré à la valeur renseignée dans le schéma des métadonnées communes.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories_full.row_span IS 'Nombre de lignes occupées par le widget de saisie, s''il y a lieu. La valeur ne sera considérée que pour un widget QTextEdit. Le cas échéant, cette valeur se substituera pour le modèle considéré à la valeur renseignée dans le schéma des métadonnées communes.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories_full.help_text IS 'Description de la catégorie. Sera affiché sous la forme d''un texte d''aide dans le formulaire. Le cas échéant, cette valeur se substituera pour le modèle considéré à la valeur renseignée dans le schéma des métadonnées communes.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories_full.default_value IS 'Valeur par défaut, le cas échéant. Le cas échéant, cette valeur se substituera pour le modèle considéré à la valeur renseignée dans le schéma des métadonnées communes.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories_full.placeholder_text IS 'Valeur fictive pré-affichée en tant qu''exemple dans le widget de saisie, s''il y a lieu. Le cas échéant, cette valeur se substituera pour le modèle considéré à la valeur renseignée dans le schéma des métadonnées communes.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories_full.input_mask IS 'Masque de saisie, s''il y a lieu. Le cas échéant, cette valeur se substituera pour le modèle considéré à la valeur renseignée dans le schéma des métadonnées communes.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories_full.multiple_values IS 'True si la catégorie admet plusieurs valeurs.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories_full.is_mandatory IS 'True si une valeur doit obligatoirement être saisie pour cette catégorie. Le cas échéant, cette valeur se substituera pour le modèle considéré à la valeur renseignée dans le schéma des métadonnées communes (uniquement s''il s''agit de rendre obligatoire une catégorie optionnelle).' ;
COMMENT ON COLUMN z_metadata.meta_template_categories_full.order_key IS 'Ordre d''apparence de la catégorie dans le formulaire. Les plus petits numéros sont affichés en premier. Le cas échéant, cette valeur se substituera pour le modèle considéré à la valeur renseignée dans le schéma des métadonnées communes.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories_full.read_only IS 'True si la catégorie est en lecture seule.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories_full.tab_name IS 'Nom de l''onglet du formulaire où placer la catégorie. Cette information n''est considérée que pour les catégories locales et les catégories communes de premier niveau (par exemple "dcat:distribution / dct:issued" ira nécessairement dans le même onglet que "dcat:distribution"). Pour celles-ci, si aucun onglet n''est fourni, la catégorie ira toujours dans le premier onglet cité pour le modèle ou, à défaut, dans un onglet "Général".' ;


------ 1.5 - IMPORT DE MODELES PRE-CONFIGURES -------

-- Function: z_metadata.meta_import_sample_template(text)

CREATE OR REPLACE FUNCTION z_metadata.meta_import_sample_template(
		tpl_label text default NULL::text
		)
	RETURNS TABLE (label text, summary text)
    LANGUAGE plpgsql
    AS $BODY$
/* OBJET : Importe l'un des modèles de formulaires pré-
configurés (ou tous si l'argument n'est pas renseigné).

Réexécuter la fonction sur un modèle déjà répertorié aura
pour effet de le réinitialiser.

ARGUMENTS :
- [optionnel] tpl_label : nom du modèle à importer.

RESULTAT :
La fonction renvoie une table listant les modèles importés.
- label : nom du modèle effectivement importé ;
- summary : résumé des opérations réalisées. À ce stade,
vaudra 'created' pour un modèle qui n'était pas encore
répertorié et 'updated' pour un modèle déjà répertorié.

Si le nom de modèle fourni en argument est inconnu, la
fonction n'a aucun effet et renverra une table vide.
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
				'{"c1": {"snum:isExternal": "True"}}'::jsonb,
				10,
				format(
					'Modèle pré-configuré importé via z_metadata.meta_import_sample_template() le %s à %s.',
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
					'Modèle pré-configuré importé via z_metadata.meta_import_sample_template() le %s à %s.',
					now()::date,
					left(now()::time::text, 8)
					)
			),
			(
				'Basique', NULL, NULL, 0,
				format(
					'Modèle pré-configuré importé via z_metadata.meta_import_sample_template() le %s à %s.',
					now()::date,
					left(now()::time::text, 8)
					)
			)
	    ) AS t (tpl_label, sql_filter, md_conditions, priority, comment)
		WHERE meta_import_sample_template.tpl_label IS NULL
			OR meta_import_sample_template.tpl_label = t.tpl_label
	LOOP
	
		DELETE FROM z_metadata.meta_template
			WHERE meta_template.tpl_label = tpl.tpl_label ;
			
		IF FOUND
		THEN
			RETURN QUERY SELECT tpl.tpl_label, 'updated' ;
		ELSE
			RETURN QUERY SELECT tpl.tpl_label, 'created' ;
		END IF ;
		
		INSERT INTO z_metadata.meta_template
			(tpl_label, sql_filter, md_conditions, priority, comment)
			VALUES (tpl.tpl_label, tpl.sql_filter, tpl.md_conditions, tpl.priority, tpl.comment) ;
		
		-- boucle sur les associations modèles-catégories :
		FOR tplcat IN SELECT * FROM (
			VALUES
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
                ('Classique', 'dct:conformsTo', NULL),
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
				('Classique', 'dct:modified', NULL),
                ('Classique', 'dct:spatial', NULL),
                ('Classique', 'dct:spatial / dct:identifier', NULL),
                ('Classique', 'dct:spatial / skos:inScheme', NULL),
                ('Classique', 'dct:spatial / skos:prefLabel', NULL),
                ('Classique', 'dct:subject', NULL),
                ('Classique', 'dct:temporal', NULL),
				('Classique', 'dct:temporal / dcat:startDate', NULL),
				('Classique', 'dct:temporal / dcat:endDate', NULL),
                ('Classique', 'dct:title', NULL),
                ('Classique', 'foaf:page', NULL),
                ('Classique', 'owl:versionInfo', NULL),
                ('Classique', 'prov:qualifiedAttribution', NULL),
                ('Classique', 'prov:qualifiedAttribution / dcat:hadRole', NULL),
                ('Classique', 'prov:qualifiedAttribution / prov:agent', NULL),
                ('Classique', 'prov:qualifiedAttribution / prov:agent / dct:type', NULL),
                ('Classique', 'prov:qualifiedAttribution / prov:agent / foaf:mbox', NULL),
                ('Classique', 'prov:qualifiedAttribution / prov:agent / foaf:name', NULL),
                ('Classique', 'prov:qualifiedAttribution / prov:agent / foaf:phone', NULL),
                ('Classique', 'prov:qualifiedAttribution / prov:agent / foaf:workplaceHomepage', NULL),
                ('Classique', 'snum:isExternal', False),
                
                ('Donnée externe', 'adms:versionNotes', NULL),
                ('Donnée externe', 'dcat:contactPoint', NULL),
                ('Donnée externe', 'dcat:contactPoint / vcard:fn', NULL),
                ('Donnée externe', 'dcat:contactPoint / vcard:hasEmail', NULL),
                ('Donnée externe', 'dcat:contactPoint / vcard:hasTelephone', NULL),
                ('Donnée externe', 'dcat:contactPoint / vcard:hasURL', NULL),
                ('Donnée externe', 'dcat:contactPoint / vcard:organization-name', NULL),
				('Donnée externe', 'dcat:distribution', NULL),
				('Donnée externe', 'dcat:distribution / dct:accessURL', NULL),
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
                ('Donnée externe', 'dct:spatial', NULL),
                ('Donnée externe', 'dct:spatial / dct:identifier', NULL),
                ('Donnée externe', 'dct:spatial / skos:inScheme', NULL),
                ('Donnée externe', 'dct:spatial / skos:prefLabel', NULL),
                ('Donnée externe', 'dct:subject', NULL),
                ('Donnée externe', 'foaf:page', NULL),
                ('Donnée externe', 'owl:versionInfo', NULL),
                ('Donnée externe', 'snum:isExternal', True)
			) AS t (tpl_label, shrcat_path, default_value)
			WHERE t.tpl_label = tpl.tpl_label
		LOOP
		
			INSERT INTO z_metadata.meta_template_categories
				(tpl_label, shrcat_path)
				VALUES (tpl.tpl_label, tplcat.shrcat_path) ;
		
		END LOOP ;
	
	END LOOP ;

	RETURN ;
	
END
$BODY$ ;

COMMENT ON FUNCTION z_metadata.meta_import_sample_template(text) IS 'Importe l''un des modèles de formulaires pré-configurés (ou tous si l''argument n''est pas renseigné).' ;

-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

