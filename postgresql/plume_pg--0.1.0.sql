\echo Use "CREATE EXTENSION plume_pg" to load this file. \quit
-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
--
-- PlumePg - Système de gestion des métadonnées locales, version 0.1.0
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
-- - Schema: z_plume
-- - Type: z_plume.meta_special
-- - Type: z_plume.meta_datatype
-- - Type: z_plume.meta_geo_tool
-- - Type: z_plume.meta_compute
-- - Table: z_plume.meta_categorie
-- - Table: z_plume.meta_shared_categorie
-- - Function: z_plume.meta_shared_categorie_before_insert()
-- - Trigger: meta_shared_categorie_before_insert
-- - Table: z_plume.meta_local_categorie
-- - Table: z_plume.meta_template
-- - Table: z_plume.meta_template_categories
-- - Function: z_plume.meta_execute_sql_filter(text, text, text)
-- - View: z_plume.meta_template_categories_full
-- - Function: z_plume.meta_import_sample_template(text)
--
-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


/* 0 - SCHEMA z_plume
   1 - MODELES DE FORMULAIRES */


-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

-----------------------------------
------ 0 - SCHEMA z_plume ------
-----------------------------------

-- Schema: z_plume

DO
$$
BEGIN

    IF NOT EXISTS (
        SELECT * FROM pg_namespace
            WHERE nspname = 'z_plume'
        )
    THEN
    
        CREATE SCHEMA z_plume ;
        
        COMMENT ON SCHEMA z_plume IS 'Utilitaires pour la gestion des métadonnées.' ;
        
        -- si l'extension asgard est présente, on déclare g_admin
        -- comme producteur et g_consult comme lecteur pour le
        -- nouveau schéma
        IF EXISTS (
            SELECT * FROM pg_available_extensions
                WHERE name = 'asgard'
                    AND installed_version IS NOT NULL
            )
        THEN
            BEGIN
                UPDATE z_asgard.gestion_schema_usr
                    SET producteur = 'g_admin',
                        lecteur = 'g_consult'
                    WHERE nom_schema = 'z_plume' ;
            EXCEPTION WHEN OTHERS THEN NULL ;
            END ;
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

-- Type: z_plume.meta_special

CREATE TYPE z_plume.meta_special AS ENUM ('url', 'email', 'phone') ;
    
COMMENT ON TYPE z_plume.meta_special IS 'Valeurs admises pour les mises en forme particulières.' ;


-- Type: z_plume.meta_datatype

CREATE TYPE z_plume.meta_datatype AS ENUM (
	'xsd:string', 'xsd:integer', 'xsd:decimal', 'xsd:boolean',
    'xsd:date', 'xsd:time', 'xsd:dateTime', 'xsd:duration',
    'gsp:wktLiteral', 'rdf:langString'
	) ;
	
COMMENT ON TYPE z_plume.meta_datatype IS 'Types de valeurs supportés par Plume.' ;


-- Type: z_plume.meta_geo_tool

CREATE TYPE z_plume.meta_geo_tool AS ENUM (
	'show', 'point', 'linestring', 'rectangle', 'polygon',
    'bbox', 'centroid', 'circle'
	) ;
	
COMMENT ON TYPE z_plume.meta_geo_tool IS 'Types de fonctionnalités d''aide à la saisie des géométries supportées par Plume.' ;

CREATE CAST (text[] AS z_plume.meta_geo_tool[])
    WITH INOUT
    AS IMPLICIT ;

-- Type: z_plume.meta_compute

CREATE TYPE z_plume.meta_compute AS ENUM (
	'auto', 'empty', 'new', 'manual'
	) ;
	
COMMENT ON TYPE z_plume.meta_compute IS 'Types de fonctionnalités de calcul des métadonnées supportées par Plume.' ;

CREATE CAST (text[] AS z_plume.meta_compute[])
    WITH INOUT
    AS IMPLICIT ;

--Table: z_plume.meta_categorie

CREATE TABLE z_plume.meta_categorie (
    path text NOT NULL DEFAULT format('uuid:%s', gen_random_uuid()),
	origin text NOT NULL DEFAULT 'local',
    label text NOT NULL,
    description text,
    special z_plume.meta_special,
	is_node boolean NOT NULL DEFAULT False,
	datatype z_plume.meta_datatype,
    is_long_text boolean,
    rowspan int,
    placeholder text,
    input_mask text,
    is_multiple boolean,
    unilang text,
    is_mandatory boolean,
    sources text[],
    geo_tools z_plume.meta_geo_tool[],
    compute z_plume.meta_compute[],
    template_order int,
    CONSTRAINT meta_categorie_origin_check CHECK (origin IN ('local', 'shared')),
    CONSTRAINT meta_categorie_rowspan_check CHECK (rowspan BETWEEN 1 AND 99)
    )
    PARTITION BY LIST (origin) ;

COMMENT ON TABLE z_plume.meta_categorie IS 'Catégories de métadonnées disponibles pour les modèles de formulaires.' ;

COMMENT ON COLUMN z_plume.meta_categorie.path IS 'Chemin N3 de la catégorie (identifiant unique). CE CHAMP EST GENERE AUTOMATIQUEMENT, NE PAS MODIFIER MANUELLEMENT.' ;
COMMENT ON COLUMN z_plume.meta_categorie.origin IS 'Origine de la catégorie : ''shared'' pour une catégorie commune, ''local'' pour une catégorie locale supplémentaire. CE CHAMP EST GENERE AUTOMATIQUEMENT, NE PAS MODIFIER MANUELLEMENT.' ;
COMMENT ON COLUMN z_plume.meta_categorie.label IS 'Libellé de la catégorie.' ;
COMMENT ON COLUMN z_plume.meta_categorie.description IS 'Description de la catégorie. Sera affiché sous la forme d''un texte d''aide dans le formulaire.' ;
COMMENT ON COLUMN z_plume.meta_categorie.special IS 'Le cas échéant, mise en forme spécifique à appliquer au champ. Valeurs autorisées : ''url'', ''email'', ''phone''. Pour les catégories communes, les modifications apportées à ce champ ne seront pas prises en compte.' ;
COMMENT ON COLUMN z_plume.meta_categorie.is_node IS 'True si la catégorie est le nom d''un groupe qui contiendra lui-même d''autres catégories et non une catégorie à laquelle sera directement associée une valeur. Par exemple, is_node vaut True pour la catégorie correspondant au point de contact (dcat:contactPoint) et False pour le nom du point de contact (dcat:contactPoint / vcard:fn). CE CHAMP EST GENERE AUTOMATIQUEMENT, NE PAS MODIFIER MANUELLEMENT.' ;
COMMENT ON COLUMN z_plume.meta_categorie.datatype IS 'Type de valeur attendu pour la catégorie. Cette information détermine notamment la nature des widgets utilisés par Plume pour afficher et éditer les valeurs, ainsi que les validateurs appliqués. Pour les catégories communes, les modifications apportées à ce champ ne seront pas prises en compte.' ;
COMMENT ON COLUMN z_plume.meta_categorie.is_long_text IS 'True pour une catégorie appelant un texte de plusieurs lignes. Cette information ne sera prise en compte que si le type de valeur (datatype) est ''xsd:string'' ou ''rdf:langString''.' ;
COMMENT ON COLUMN z_plume.meta_categorie.rowspan IS 'Nombre de lignes occupées par le widget de saisie, s''il y a lieu de modifier le comportement par défaut de Plume. La valeur ne sera considérée que si is_long_text vaut True.' ;
COMMENT ON COLUMN z_plume.meta_categorie.placeholder IS 'Valeur fictive pré-affichée en tant qu''exemple dans le widget de saisie, s''il y a lieu.' ;
COMMENT ON COLUMN z_plume.meta_categorie.input_mask IS 'Masque de saisie, s''il y a lieu. La valeur sera ignorée si le widget utilisé pour la catégorie ne prend pas en charge ce mécanisme.' ;
COMMENT ON COLUMN z_plume.meta_categorie.is_multiple IS 'True si la catégorie admet plusieurs valeurs. Pour les catégories commnes, les modifications apportées à ce champ ne seront pas prises en compte.' ;
COMMENT ON COLUMN z_plume.meta_categorie.unilang IS 'True si la catégorie n''admet plusieurs valeurs que si elles sont dans des langues différentes (par exemple un jeu de données n''a en principe qu''un seul titre, mais il peut être traduit). is_multiple est ignoré quand unilang vaut True. Pour les catégories commnes, les modifications apportées à ce champ ne seront pas prises en compte.' ;
COMMENT ON COLUMN z_plume.meta_categorie.is_mandatory IS 'True si une valeur doit obligatoirement être saisie pour cette catégorie. À noter que ce champ permet de rendre obligatoire une catégorie commune optionnelle, pas l''inverse.' ;
COMMENT ON COLUMN z_plume.meta_categorie.sources IS 'Pour une catégorie prenant ses valeurs dans un ou plusieurs thésaurus, liste des sources admises. Cette information n''est considérée que pour les catégories communes. Il n''est pas possible d''ajouter des sources ni de les retirer toutes - Plume reviendrait alors à la liste initiale -, mais ce champ permet de restreindre la liste à un ou plusieurs thésaurus jugés les mieux adaptés.' ;
COMMENT ON COLUMN z_plume.meta_categorie.geo_tools IS 'Pour une catégorie prenant pour valeurs des géométries, liste des fonctionnalités d''aide à la saisie à proposer. Cette information ne sera considérée que si le type (datatype) est ''gsp:wktLiteral''. Pour retirer toutes les fonctionnalités proposées par défaut pour une catégorie commune, on saisira une liste vide.' ;
COMMENT ON COLUMN z_plume.meta_categorie.compute IS 'Liste des fonctionnalités de calcul à proposer. Cette information ne sera considérée que si une méthode de calcul est effectivement disponible pour la catégorie. Pour retirer toutes les fonctionnalités proposées par défaut pour une catégorie commune, on saisira une liste vide.' ;
COMMENT ON COLUMN z_plume.meta_categorie.template_order IS 'Ordre d''apparence de la catégorie dans le formulaire. Les plus petits numéros sont affichés en premier.' ;


-- Table: z_plume.meta_shared_categorie

CREATE TABLE z_plume.meta_shared_categorie 
    PARTITION OF z_plume.meta_categorie (
        CONSTRAINT meta_shared_categorie_pkey PRIMARY KEY (path)
    )
    FOR VALUES IN ('shared') ;
    
COMMENT ON TABLE z_plume.meta_shared_categorie IS 'Catégories de métadonnées communes.' ;

COMMENT ON COLUMN z_plume.meta_shared_categorie.path IS 'Chemin SPARQL de la catégorie (identifiant unique). CE CHAMP EST GENERE AUTOMATIQUEMENT, NE PAS MODIFIER MANUELLEMENT.' ;
COMMENT ON COLUMN z_plume.meta_shared_categorie.origin IS 'Origine de la catégorie. Toujours ''shared''. CE CHAMP EST GENERE AUTOMATIQUEMENT, NE PAS MODIFIER MANUELLEMENT.' ;
COMMENT ON COLUMN z_plume.meta_shared_categorie.label IS 'Libellé de la catégorie.' ;
COMMENT ON COLUMN z_plume.meta_shared_categorie.description IS 'Description de la catégorie. Sera affiché sous la forme d''un texte d''aide dans le formulaire.' ;
COMMENT ON COLUMN z_plume.meta_shared_categorie.special IS 'Le cas échéant, mise en forme spécifique à appliquer au champ. Valeurs autorisées : ''url'', ''email'', ''phone''. Les modifications apportées à ce champ ne seront pas prises en compte.' ;
COMMENT ON COLUMN z_plume.meta_shared_categorie.is_node IS 'True si la catégorie est le nom d''un groupe qui contiendra lui-même d''autres catégories et non une catégorie à laquelle sera directement associée une valeur. Par exemple, is_node vaut True pour la catégorie correspondant au point de contact (dcat:contactPoint) et False pour le nom du point de contact (dcat:contactPoint / vcard:fn). CE CHAMP EST GENERE AUTOMATIQUEMENT, NE PAS MODIFIER MANUELLEMENT.' ;
COMMENT ON COLUMN z_plume.meta_shared_categorie.datatype IS 'Type de valeur attendu pour la catégorie. Cette information détermine notamment la nature des widgets utilisés par Plume pour afficher et éditer les valeurs, ainsi que les validateurs appliqués. Les modifications apportées à ce champ ne seront pas prises en compte.' ;
COMMENT ON COLUMN z_plume.meta_shared_categorie.is_long_text IS 'True pour une catégorie appelant un texte de plusieurs lignes. Cette information ne sera prise en compte que si le type de valeur (datatype) est ''xsd:string'' ou ''rdf:langString''.' ;
COMMENT ON COLUMN z_plume.meta_shared_categorie.rowspan IS 'Nombre de lignes occupées par le widget de saisie, s''il y a lieu de modifier le comportement par défaut de Plume. La valeur ne sera considérée que si is_long_text vaut True.' ;
COMMENT ON COLUMN z_plume.meta_shared_categorie.placeholder IS 'Valeur fictive pré-affichée en tant qu''exemple dans le widget de saisie, s''il y a lieu.' ;
COMMENT ON COLUMN z_plume.meta_shared_categorie.input_mask IS 'Masque de saisie, s''il y a lieu. La valeur sera ignorée si le widget utilisé pour la catégorie ne prend pas en charge ce mécanisme.' ;
COMMENT ON COLUMN z_plume.meta_shared_categorie.is_multiple IS 'True si la catégorie admet plusieurs valeurs. Les modifications apportées à ce champ ne seront pas prises en compte.' ;
COMMENT ON COLUMN z_plume.meta_shared_categorie.unilang IS 'True si la catégorie n''admet plusieurs valeurs que si elles sont dans des langues différentes (par exemple un jeu de données n''a en principe qu''un seul titre, mais il peut être traduit). is_multiple est ignoré quand unilang vaut True. Les modifications apportées à ce champ ne seront pas prises en compte.' ;
COMMENT ON COLUMN z_plume.meta_shared_categorie.is_mandatory IS 'True si une valeur doit obligatoirement être saisie pour cette catégorie. À noter que ce champ permet de rendre obligatoire une catégorie commune optionnelle, pas l''inverse.' ;
COMMENT ON COLUMN z_plume.meta_shared_categorie.sources IS 'Pour une catégorie prenant ses valeurs dans un ou plusieurs thésaurus, liste des sources admises. Il n''est pas possible d''ajouter des sources ni de les retirer toutes - Plume reviendrait alors à la liste initiale -, mais ce champ permet de restreindre la liste à un ou plusieurs thésaurus jugés les mieux adaptés.' ;
COMMENT ON COLUMN z_plume.meta_shared_categorie.geo_tools IS 'Pour une catégorie prenant pour valeurs des géométries, liste des fonctionnalités d''aide à la saisie à proposer. Cette information ne sera considérée que si le type (datatype) est ''gsp:wktLiteral''. Pour retirer toutes les fonctionnalités proposées par défaut pour la catégorie commune, on saisira une liste vide.' ;
COMMENT ON COLUMN z_plume.meta_shared_categorie.compute IS 'Liste des fonctionnalités de calcul à proposer. Cette information ne sera considérée que si une méthode de calcul est effectivement disponible pour la catégorie. Pour retirer toutes les fonctionnalités proposées par défaut pour une catégorie commune, on saisira une liste vide.' ;
COMMENT ON COLUMN z_plume.meta_shared_categorie.template_order IS 'Ordre d''apparence de la catégorie dans le formulaire. Les plus petits numéros sont affichés en premier.' ;

-- la table est marquée comme table de configuration de l'extension
SELECT pg_extension_config_dump('z_plume.meta_shared_categorie'::regclass, '') ;

-- extraction du schéma SHACL
INSERT INTO z_plume.meta_categorie (
        path, origin, label, description, special,
        is_node, datatype, is_long_text, rowspan,
        placeholder, input_mask, is_multiple, unilang,
        is_mandatory, sources, geo_tools, template_order
    ) VALUES
    ('dct:title', 'shared', 'Libellé', 'Nom explicite du jeu de données.', NULL, false, 'rdf:langString', false, NULL, NULL, NULL, true, true, true, NULL, NULL, 0),
    ('owl:versionInfo', 'shared', 'Version', 'Numéro de version ou millésime du jeu de données.', NULL, false, 'xsd:string', false, NULL, NULL, NULL, false, false, false, NULL, NULL, 1),
    ('dct:description', 'shared', 'Description', 'Description du jeu de données.', NULL, false, 'rdf:langString', true, 15, NULL, NULL, true, true, true, NULL, NULL, 2),
    ('plume:isExternal', 'shared', 'Donnée externe', 'Ce jeu de données est-il la reproduction de données produites par un tiers ? Une donnée issue d''une source externe mais ayant fait l''objet d''améliorations notables n''est plus une donnée externe.', NULL, false, 'xsd:boolean', false, NULL, NULL, NULL, false, false, false, NULL, NULL, 3),
    ('dcat:theme', 'shared', 'Thèmes', 'Classification thématique du jeu de données selon la nomenclature généraliste du portail opendata européen et/ou, s''il y a lieu, la nomemclature INSPIRE.', 'url', false, NULL, false, NULL, NULL, NULL, true, false, false, ARRAY['http://publications.europa.eu/resource/authority/data-theme','https://inspire.ec.europa.eu/theme'], NULL, 4),
    ('dct:subject', 'shared', 'Catégories thématiques', 'Classification thématique du jeu données selon la nomenclature du standard ISO 19115.', 'url', false, NULL, false, NULL, NULL, NULL, true, false, false, ARRAY['https://inspire.ec.europa.eu/metadata-codelist/TopicCategory'], NULL, 5),
    ('dcat:keyword', 'shared', 'Mots-clés libres', 'Mots ou très brèves expressions représentatives du jeu de données, à l''usage des moteurs de recherche.', NULL, false, 'rdf:langString', false, NULL, NULL, NULL, true, false, false, NULL, NULL, 6),
    ('dct:spatial', 'shared', 'Couverture géographique', 'Territoire·s décrit·s par le jeu de données.', NULL, true, NULL, false, NULL, NULL, NULL, true, false, false, NULL, NULL, 9),
    ('dct:spatial / skos:inScheme', 'shared', 'Index géographique', 'Type de lieu, index de référence pour l''identifiant (commune, département...).', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://registre.data.developpement-durable.gouv.fr/plume/InseeGeoIndex'], NULL, 0),
    ('dct:spatial / dct:identifier', 'shared', 'Code géographique', 'Code du département, code INSEE de la commune, etc.', NULL, false, 'xsd:string', false, NULL, NULL, NULL, true, false, false, NULL, NULL, 1),
    ('dct:spatial / skos:prefLabel', 'shared', 'Libellé', 'Dénomination explicite du lieu.', NULL, false, 'rdf:langString', false, NULL, NULL, NULL, true, true, false, NULL, NULL, 2),
    ('dct:spatial / dcat:bbox', 'shared', 'Rectangle d''emprise', 'Rectangle d''emprise (BBox), au format textuel WKT.', NULL, false, 'gsp:wktLiteral', true, NULL, '<http://www.opengis.net/def/crs/EPSG/0/2154> POLYGON((646417.3289 6857521.1356, 657175.3272 6857521.1356, 657175.3272 6867076.0360, 646417.3289 6867076.0360, 646417.3289 6857521.1356))', NULL, false, false, false, NULL, ARRAY['show','bbox','rectangle']::z_plume.meta_geo_tool[], 3),
    ('dct:spatial / dcat:centroid', 'shared', 'Centroïde', 'Localisant du centre géographique des données, au format textuel WKT.', NULL, false, 'gsp:wktLiteral', true, NULL, '<http://www.opengis.net/def/crs/EPSG/0/2154> POINT(651796.3281 6862298.5858)', NULL, false, false, false, NULL, ARRAY['show','centroid','point']::z_plume.meta_geo_tool[], 4),
    ('dct:spatial / locn:geometry', 'shared', 'Géométrie', 'Emprise géométrique, au format textuel WKT.', NULL, false, 'gsp:wktLiteral', true, NULL, '<http://www.opengis.net/def/crs/EPSG/0/2154> POLYGON((646417.3289 6857521.1356, 657175.3272 6857521.1356, 657175.3272 6867076.0360, 646417.3289 6867076.0360, 646417.3289 6857521.1356))', NULL, false, false, false, NULL, ARRAY['show','point','linestring','polygon','circle']::z_plume.meta_geo_tool[], 5),
    ('dct:temporal', 'shared', 'Couverture temporelle', 'Période·s décrite·s par le jeu de données. La date de début et la date de fin peuvent être confondues, par exemple dans le cas de l''extraction ponctuelle d''une base mise à jour au fil de l''eau.', NULL, true, NULL, false, NULL, NULL, NULL, true, false, false, NULL, NULL, 10),
    ('dct:temporal / dcat:startDate', 'shared', 'Date de début', 'Date de début de la période.', NULL, false, 'xsd:date', false, NULL, NULL, '9999-99-99', false, false, false, NULL, NULL, 0),
    ('dct:temporal / dcat:endDate', 'shared', 'Date de fin', 'Date de fin de la période.', NULL, false, 'xsd:date', false, NULL, NULL, '9999-99-99', false, false, false, NULL, NULL, 1),
    ('dct:created', 'shared', 'Date de création', 'Date de création du jeu de données. Il peut par exemple s''agir de la date de création de la table PostgreSQL ou de la date de la première saisie de données dans cette table.', NULL, false, 'xsd:date', false, NULL, NULL, '9999-99-99', false, false, false, NULL, NULL, 11),
    ('dct:modified', 'shared', 'Date de dernière modification', 'Date de la dernière modification du jeu de données. Cette date est présumée tenir compte tant des modifications de fond, tels que les ajouts d''enregistrements, que des modification purement formelles (corrections de coquilles dans les données, changement de nom d''un champ, etc.). L''absence de date de dernière modification signifie que la donnée n''a jamais été modifiée depuis sa création.', NULL, false, 'xsd:date', false, NULL, NULL, '9999-99-99', false, false, false, NULL, NULL, 12),
    ('dct:issued', 'shared', 'Date de publication', 'Date à laquelle le jeu de données a été diffusé. Cette date ne devrait être renseignée que pour un jeu de données effectivement mis à disposition du public ou d''utilisateur tiers via un catalogue de données ou un site internet. Pour un jeu de données mis à jour en continu, il s''agit de la date de publication initiale.', NULL, false, 'xsd:date', false, NULL, NULL, '9999-99-99', false, false, false, NULL, NULL, 13),
    ('dct:accrualPeriodicity', 'shared', 'Fréquence de mise à jour', 'Fréquence de mise à jour des données.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['https://inspire.ec.europa.eu/metadata-codelist/MaintenanceFrequency','http://publications.europa.eu/resource/authority/frequency'], NULL, 14),
    ('dct:provenance', 'shared', 'Généalogie', 'Sources et méthodes mises en œuvre pour produire les données.', NULL, true, NULL, false, NULL, NULL, NULL, true, false, false, NULL, NULL, 20),
    ('dct:provenance / rdfs:label', 'shared', 'Texte', 'Informations sur l''origine des données : sources, méthodes de recueil ou de traitement...', NULL, false, 'rdf:langString', true, 20, NULL, NULL, true, true, false, NULL, NULL, 0),
    ('adms:versionNotes', 'shared', 'Note de version', 'Différences entre la version courante des données et les versions antérieures.', NULL, false, 'rdf:langString', true, NULL, NULL, NULL, true, true, false, NULL, NULL, 21),
    ('dct:conformsTo', 'shared', 'Conforme à', 'Standard, schéma, référentiel de coordonnées, etc. auquel se conforment les données.', 'url', false, NULL, false, NULL, NULL, NULL, true, false, false, ARRAY['http://www.opengis.net/def/crs/EPSG/0'], NULL, 22),
    ('dct:conformsTo / skos:inScheme', 'shared', 'Registre', 'Registre de référence auquel appartient le standard.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://registre.data.developpement-durable.gouv.fr/plume/StandardsRegister'], NULL, 0),
    ('dct:conformsTo / dct:identifier', 'shared', 'Identifiant', 'Identifiant du standard, s''il y a lieu. Pour un système de coordonnées géographiques, il s''agit du code EPSG.', NULL, false, 'xsd:string', false, NULL, NULL, NULL, true, false, false, NULL, NULL, 1),
    ('dct:conformsTo / dct:title', 'shared', 'Libellé', 'Libellé explicite du standard.', NULL, false, 'rdf:langString', false, NULL, NULL, NULL, true, true, false, NULL, NULL, 2),
    ('dct:conformsTo / owl:versionInfo', 'shared', 'Version', 'Numéro ou code de la version du standard à laquelle se conforment les données.', NULL, false, 'xsd:string', false, NULL, NULL, NULL, false, false, false, NULL, NULL, 3),
    ('dct:conformsTo / dct:description', 'shared', 'Description', 'Description sommaire de l''objet du standard.', NULL, false, 'rdf:langString', true, NULL, NULL, NULL, true, true, false, NULL, NULL, 4),
    ('dct:conformsTo / dct:issued', 'shared', 'Date de publication', 'Date de publication du standard.', NULL, false, 'xsd:date', false, NULL, NULL, '9999-99-99', false, false, false, NULL, NULL, 5),
    ('dct:conformsTo / dct:modified', 'shared', 'Date de modification', 'Date de la dernière modification du standard.', NULL, false, 'xsd:date', false, NULL, NULL, '9999-99-99', false, false, false, NULL, NULL, 6),
    ('dct:conformsTo / dct:created', 'shared', 'Date de création', 'Date de création du standard.', NULL, false, 'xsd:date', false, NULL, NULL, '9999-99-99', false, false, false, NULL, NULL, 7),
    ('dct:conformsTo / foaf:page', 'shared', 'Page internet', 'Chemin d''accès au standard ou URL d''une page contenant des informations sur le standard.', 'url', false, NULL, false, NULL, NULL, NULL, true, false, false, NULL, NULL, 8),
    ('dcat:spatialResolutionInMeters', 'shared', 'Résolution spatiale en mètres', 'Plus petite distance significative dans le contexte du jeu de données, exprimée en mètres.', NULL, false, 'xsd:decimal', false, NULL, NULL, NULL, false, false, false, NULL, NULL, 24),
    ('dcat:temporalResolution', 'shared', 'Résolution temporelle', 'Plus petit pas de temps significatif dans le contexte du jeu de données.', NULL, false, 'xsd:duration', false, NULL, NULL, NULL, false, false, false, NULL, NULL, 26),
    ('dct:accessRights', 'shared', 'Conditions d''accès', 'Contraintes réglementaires limitant l''accès aux données.', 'url', false, NULL, false, NULL, NULL, NULL, true, false, false, ARRAY['http://inspire.ec.europa.eu/metadata-codelist/LimitationsOnPublicAccess','http://publications.europa.eu/resource/authority/access-right','http://registre.data.developpement-durable.gouv.fr/plume/CrpaAccessLimitations'], NULL, 30),
    ('dct:accessRights / rdfs:label', 'shared', 'Mention', 'Description des contraintes réglementaires et des modalités pratiques pour s''y conformer.', NULL, false, 'rdf:langString', true, NULL, NULL, NULL, true, true, false, NULL, NULL, 1),
    ('dcat:contactPoint', 'shared', 'Point de contact', 'Entité à contacter pour obtenir des informations sur les données.', NULL, true, NULL, false, NULL, NULL, NULL, true, false, false, NULL, NULL, 40),
    ('dcat:contactPoint / vcard:fn', 'shared', 'Nom', 'Nom du point de contact.', NULL, false, 'xsd:string', false, NULL, NULL, NULL, false, false, true, NULL, NULL, 1),
    ('dcat:contactPoint / vcard:hasEmail', 'shared', 'Courriel', 'Adresse mél.', 'email', false, NULL, false, NULL, NULL, NULL, true, false, false, NULL, NULL, 2),
    ('dcat:contactPoint / vcard:hasTelephone', 'shared', 'Téléphone', 'Numéro de téléphone.', 'phone', false, NULL, false, NULL, '+33-1-23-45-67-89', NULL, true, false, false, NULL, NULL, 3),
    ('dcat:contactPoint / vcard:hasURL', 'shared', 'Site internet', 'Site internet.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, NULL, 4),
    ('dcat:contactPoint / vcard:organization-name', 'shared', 'Appartient à', 'Le cas échéant, organisation dont le point de contact fait partie.', NULL, false, 'xsd:string', false, NULL, NULL, NULL, false, false, false, NULL, NULL, 5),
    ('dct:publisher', 'shared', 'Éditeur', 'Organisme ou personne qui assure la publication des données.', NULL, true, NULL, false, NULL, NULL, NULL, false, false, false, NULL, NULL, 41),
    ('dct:publisher / foaf:name', 'shared', 'Nom', 'Nom de l''organisation.', NULL, false, 'rdf:langString', false, NULL, NULL, NULL, true, true, false, NULL, NULL, 0),
    ('dct:publisher / dct:type', 'shared', 'Type', 'Type d''organisation.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://purl.org/adms/publishertype/1.0'], NULL, 1),
    ('dct:publisher / foaf:mbox', 'shared', 'Courriel', 'Adresse mél.', 'email', false, NULL, false, NULL, NULL, NULL, true, false, false, NULL, NULL, 2),
    ('dct:publisher / foaf:phone', 'shared', 'Téléphone', 'Numéro de téléphone.', 'phone', false, NULL, false, NULL, '+33-1-23-45-67-89', NULL, true, false, false, NULL, NULL, 3),
    ('dct:publisher / foaf:workplaceHomepage', 'shared', 'Site internet', 'Site internet.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, NULL, 4),
    ('dct:creator', 'shared', 'Auteur', 'Principal responsable de la production des données.', NULL, true, NULL, false, NULL, NULL, NULL, false, false, false, NULL, NULL, 42),
    ('dct:creator / foaf:name', 'shared', 'Nom', 'Nom de l''organisation.', NULL, false, 'rdf:langString', false, NULL, NULL, NULL, true, true, false, NULL, NULL, 0),
    ('dct:creator / dct:type', 'shared', 'Type', 'Type d''organisation.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://purl.org/adms/publishertype/1.0'], NULL, 1),
    ('dct:creator / foaf:mbox', 'shared', 'Courriel', 'Adresse mél.', 'email', false, NULL, false, NULL, NULL, NULL, true, false, false, NULL, NULL, 2),
    ('dct:creator / foaf:phone', 'shared', 'Téléphone', 'Numéro de téléphone.', 'phone', false, NULL, false, NULL, '+33-1-23-45-67-89', NULL, true, false, false, NULL, NULL, 3),
    ('dct:creator / foaf:workplaceHomepage', 'shared', 'Site internet', 'Site internet.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, NULL, 4),
    ('dct:rightsHolder', 'shared', 'Propriétaire', 'Organisme ou personne qui détient des droits sur les données.', NULL, true, NULL, false, NULL, NULL, NULL, true, false, false, NULL, NULL, 43),
    ('dct:rightsHolder / foaf:name', 'shared', 'Nom', 'Nom de l''organisation.', NULL, false, 'rdf:langString', false, NULL, NULL, NULL, true, true, false, NULL, NULL, 0),
    ('dct:rightsHolder / dct:type', 'shared', 'Type', 'Type d''organisation.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://purl.org/adms/publishertype/1.0'], NULL, 1),
    ('dct:rightsHolder / foaf:mbox', 'shared', 'Courriel', 'Adresse mél.', 'email', false, NULL, false, NULL, NULL, NULL, true, false, false, NULL, NULL, 2),
    ('dct:rightsHolder / foaf:phone', 'shared', 'Téléphone', 'Numéro de téléphone.', 'phone', false, NULL, false, NULL, '+33-1-23-45-67-89', NULL, true, false, false, NULL, NULL, 3),
    ('dct:rightsHolder / foaf:workplaceHomepage', 'shared', 'Site internet', 'Site internet.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, NULL, 4),
    ('geodcat:custodian', 'shared', 'Gestionnaire', 'Organisme ou personne qui assume la maintenance des données.', NULL, true, NULL, false, NULL, NULL, NULL, true, false, false, NULL, NULL, 44),
    ('geodcat:custodian / foaf:name', 'shared', 'Nom', 'Nom de l''organisation.', NULL, false, 'rdf:langString', false, NULL, NULL, NULL, true, true, false, NULL, NULL, 0),
    ('geodcat:custodian / dct:type', 'shared', 'Type', 'Type d''organisation.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://purl.org/adms/publishertype/1.0'], NULL, 1),
    ('geodcat:custodian / foaf:mbox', 'shared', 'Courriel', 'Adresse mél.', 'email', false, NULL, false, NULL, NULL, NULL, true, false, false, NULL, NULL, 2),
    ('geodcat:custodian / foaf:phone', 'shared', 'Téléphone', 'Numéro de téléphone.', 'phone', false, NULL, false, NULL, '+33-1-23-45-67-89', NULL, true, false, false, NULL, NULL, 3),
    ('geodcat:custodian / foaf:workplaceHomepage', 'shared', 'Site internet', 'Site internet.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, NULL, 4),
    ('geodcat:distributor', 'shared', 'Distributeur', 'Organisme ou personne qui assure la distribution des données.', NULL, true, NULL, false, NULL, NULL, NULL, true, false, false, NULL, NULL, 45),
    ('geodcat:distributor / foaf:name', 'shared', 'Nom', 'Nom de l''organisation.', NULL, false, 'rdf:langString', false, NULL, NULL, NULL, true, true, false, NULL, NULL, 0),
    ('geodcat:distributor / dct:type', 'shared', 'Type', 'Type d''organisation.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://purl.org/adms/publishertype/1.0'], NULL, 1),
    ('geodcat:distributor / foaf:mbox', 'shared', 'Courriel', 'Adresse mél.', 'email', false, NULL, false, NULL, NULL, NULL, true, false, false, NULL, NULL, 2),
    ('geodcat:distributor / foaf:phone', 'shared', 'Téléphone', 'Numéro de téléphone.', 'phone', false, NULL, false, NULL, '+33-1-23-45-67-89', NULL, true, false, false, NULL, NULL, 3),
    ('geodcat:distributor / foaf:workplaceHomepage', 'shared', 'Site internet', 'Site internet.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, NULL, 4),
    ('geodcat:originator', 'shared', 'Commanditaire', 'Organisme ou personne qui est à l''origine de la création des données.', NULL, true, NULL, false, NULL, NULL, NULL, true, false, false, NULL, NULL, 46),
    ('geodcat:originator / foaf:name', 'shared', 'Nom', 'Nom de l''organisation.', NULL, false, 'rdf:langString', false, NULL, NULL, NULL, true, true, false, NULL, NULL, 0),
    ('geodcat:originator / dct:type', 'shared', 'Type', 'Type d''organisation.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://purl.org/adms/publishertype/1.0'], NULL, 1),
    ('geodcat:originator / foaf:mbox', 'shared', 'Courriel', 'Adresse mél.', 'email', false, NULL, false, NULL, NULL, NULL, true, false, false, NULL, NULL, 2),
    ('geodcat:originator / foaf:phone', 'shared', 'Téléphone', 'Numéro de téléphone.', 'phone', false, NULL, false, NULL, '+33-1-23-45-67-89', NULL, true, false, false, NULL, NULL, 3),
    ('geodcat:originator / foaf:workplaceHomepage', 'shared', 'Site internet', 'Site internet.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, NULL, 4),
    ('geodcat:principalInvestigator', 'shared', 'Maître d''œuvre', 'Organisme ou personne chargée du recueil des informations.', NULL, true, NULL, false, NULL, NULL, NULL, true, false, false, NULL, NULL, 47),
    ('geodcat:principalInvestigator / foaf:name', 'shared', 'Nom', 'Nom de l''organisation.', NULL, false, 'rdf:langString', false, NULL, NULL, NULL, true, true, false, NULL, NULL, 0),
    ('geodcat:principalInvestigator / dct:type', 'shared', 'Type', 'Type d''organisation.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://purl.org/adms/publishertype/1.0'], NULL, 1),
    ('geodcat:principalInvestigator / foaf:mbox', 'shared', 'Courriel', 'Adresse mél.', 'email', false, NULL, false, NULL, NULL, NULL, true, false, false, NULL, NULL, 2),
    ('geodcat:principalInvestigator / foaf:phone', 'shared', 'Téléphone', 'Numéro de téléphone.', 'phone', false, NULL, false, NULL, '+33-1-23-45-67-89', NULL, true, false, false, NULL, NULL, 3),
    ('geodcat:principalInvestigator / foaf:workplaceHomepage', 'shared', 'Site internet', 'Site internet.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, NULL, 4),
    ('geodcat:processor', 'shared', 'Intégrateur', 'Organisation ou personne qui a retraité les données.', NULL, true, NULL, false, NULL, NULL, NULL, true, false, false, NULL, NULL, 48),
    ('geodcat:processor / foaf:name', 'shared', 'Nom', 'Nom de l''organisation.', NULL, false, 'rdf:langString', false, NULL, NULL, NULL, true, true, false, NULL, NULL, 0),
    ('geodcat:processor / dct:type', 'shared', 'Type', 'Type d''organisation.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://purl.org/adms/publishertype/1.0'], NULL, 1),
    ('geodcat:processor / foaf:mbox', 'shared', 'Courriel', 'Adresse mél.', 'email', false, NULL, false, NULL, NULL, NULL, true, false, false, NULL, NULL, 2),
    ('geodcat:processor / foaf:phone', 'shared', 'Téléphone', 'Numéro de téléphone.', 'phone', false, NULL, false, NULL, '+33-1-23-45-67-89', NULL, true, false, false, NULL, NULL, 3),
    ('geodcat:processor / foaf:workplaceHomepage', 'shared', 'Site internet', 'Site internet.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, NULL, 4),
    ('geodcat:resourceProvider', 'shared', 'Fournisseur de la ressource', 'Organisme ou personne qui diffuse les données, soit directement soit par l''intermédiaire d''un distributeur.', NULL, true, NULL, false, NULL, NULL, NULL, true, false, false, NULL, NULL, 49),
    ('geodcat:resourceProvider / foaf:name', 'shared', 'Nom', 'Nom de l''organisation.', NULL, false, 'rdf:langString', false, NULL, NULL, NULL, true, true, false, NULL, NULL, 0),
    ('geodcat:resourceProvider / dct:type', 'shared', 'Type', 'Type d''organisation.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://purl.org/adms/publishertype/1.0'], NULL, 1),
    ('geodcat:resourceProvider / foaf:mbox', 'shared', 'Courriel', 'Adresse mél.', 'email', false, NULL, false, NULL, NULL, NULL, true, false, false, NULL, NULL, 2),
    ('geodcat:resourceProvider / foaf:phone', 'shared', 'Téléphone', 'Numéro de téléphone.', 'phone', false, NULL, false, NULL, '+33-1-23-45-67-89', NULL, true, false, false, NULL, NULL, 3),
    ('geodcat:resourceProvider / foaf:workplaceHomepage', 'shared', 'Site internet', 'Site internet.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, NULL, 4),
    ('geodcat:user', 'shared', 'Utilisateur', 'Organisme ou personne qui utilise les données.', NULL, true, NULL, false, NULL, NULL, NULL, true, false, false, NULL, NULL, 50),
    ('geodcat:user / foaf:name', 'shared', 'Nom', 'Nom de l''organisation.', NULL, false, 'rdf:langString', false, NULL, NULL, NULL, true, true, false, NULL, NULL, 0),
    ('geodcat:user / dct:type', 'shared', 'Type', 'Type d''organisation.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://purl.org/adms/publishertype/1.0'], NULL, 1),
    ('geodcat:user / foaf:mbox', 'shared', 'Courriel', 'Adresse mél.', 'email', false, NULL, false, NULL, NULL, NULL, true, false, false, NULL, NULL, 2),
    ('geodcat:user / foaf:phone', 'shared', 'Téléphone', 'Numéro de téléphone.', 'phone', false, NULL, false, NULL, '+33-1-23-45-67-89', NULL, true, false, false, NULL, NULL, 3),
    ('geodcat:user / foaf:workplaceHomepage', 'shared', 'Site internet', 'Site internet.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, NULL, 4),
    ('dcat:distribution', 'shared', 'Distribution', 'Distribution.', NULL, true, NULL, false, NULL, NULL, NULL, true, false, false, NULL, NULL, 59),
    ('dcat:distribution / dcat:accessURL', 'shared', 'URL d''accès', 'URL de la page où est publiée cette distribution des données.', 'url', false, NULL, false, NULL, NULL, NULL, true, false, true, NULL, NULL, 1),
    ('dcat:distribution / dct:title', 'shared', 'Libellé', 'Nom de la distribution.', NULL, false, 'rdf:langString', false, NULL, NULL, NULL, true, true, false, NULL, NULL, 2),
    ('dcat:distribution / dct:description', 'shared', 'Description', 'Description de la distribution.', NULL, false, 'rdf:langString', true, NULL, NULL, NULL, true, true, false, NULL, NULL, 3),
    ('dcat:distribution / dcat:downloadURL', 'shared', 'Lien de téléchargement direct', 'URL de téléchargement direct du ou des fichiers de la distribution.', 'url', false, NULL, false, NULL, NULL, NULL, true, false, false, NULL, NULL, 4),
    ('dcat:distribution / dct:issued', 'shared', 'Date de publication', 'Date à laquelle la distribution a été diffusée.', NULL, false, 'xsd:date', false, NULL, NULL, '9999-99-99', false, false, false, NULL, NULL, 5),
    ('dcat:distribution / dct:modified', 'shared', 'Date de dernière modification', 'Date de la dernière modification de la distribution.', NULL, false, 'xsd:date', false, NULL, NULL, '9999-99-99', false, false, false, NULL, NULL, 12),
    ('dcat:distribution / dcatap:availability', 'shared', 'Disponibilité', 'Niveau de disponibilité prévu pour la distribution, permettant d''apprécier le temps pendant lequel elle est susceptible de rester accessible.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://publications.europa.eu/resource/authority/planned-availability'], NULL, 7),
    ('dcat:distribution / adms:status', 'shared', 'Statut', 'Niveau de maturité de la distribution.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://publications.europa.eu/resource/authority/dataset-status'], NULL, 8),
    ('dcat:distribution / dct:type', 'shared', 'Type de distribution', 'Type de distribution.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://publications.europa.eu/resource/authority/distribution-type'], NULL, 10),
    ('dcat:distribution / dct:format', 'shared', 'Format de fichier', 'Format de fichier ou extension.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://publications.europa.eu/resource/authority/file-type'], NULL, 11),
    ('dcat:distribution / dct:format / rdfs:label', 'shared', 'Nom', 'Libellé du format.', NULL, false, 'rdf:langString', false, NULL, NULL, NULL, true, true, false, NULL, NULL, 0),
    ('dcat:distribution / dcat:compressFormat', 'shared', 'Format de compression', 'Format du fichier contenant les données sous une forme compressée, afin de réduire leur volume.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://publications.europa.eu/resource/authority/file-type'], NULL, 12),
    ('dcat:distribution / dcat:compressFormat / rdfs:label', 'shared', 'Nom', 'Libellé du format.', NULL, false, 'rdf:langString', false, NULL, NULL, NULL, true, true, false, NULL, NULL, 0),
    ('dcat:distribution / dcat:packageFormat', 'shared', 'Format d''empaquatage', 'Format du fichier rassemblant les différents fichiers contenant les données pour permettre leur téléchargement conjoint.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://publications.europa.eu/resource/authority/file-type'], NULL, 13),
    ('dcat:distribution / dcat:packageFormat / rdfs:label', 'shared', 'Nom', 'Libellé du format.', NULL, false, 'rdf:langString', false, NULL, NULL, NULL, true, true, false, NULL, NULL, 0),
    ('dcat:distribution / dcat:accessService', 'shared', 'Service', 'Service donnant accès aux données.', NULL, true, NULL, false, NULL, NULL, NULL, true, false, false, NULL, NULL, 14),
    ('dcat:distribution / dcat:accessService / dct:title', 'shared', 'Libellé', 'Nom explicite du service de données.', NULL, false, 'rdf:langString', false, NULL, NULL, NULL, true, true, true, NULL, NULL, 0),
    ('dcat:distribution / dcat:accessService / dcat:endpointURL', 'shared', 'URL de base', 'URL de base du service de données, sans aucun paramètre.', 'url', false, NULL, false, NULL, 'https://services.data.shom.fr/INSPIRE/wms/r', NULL, true, false, false, NULL, NULL, 1),
    ('dcat:distribution / dcat:accessService / dct:conformsTo', 'shared', 'Conforme à', 'Standard ou référentiel de coordonnées auquel se conforme le service.', 'url', false, NULL, false, NULL, NULL, NULL, true, false, false, ARRAY['http://www.opengis.net/def/crs/EPSG/0','http://registre.data.developpement-durable.gouv.fr/plume/DataServiceStandard'], NULL, 2),
    ('dcat:distribution / dcat:accessService / dct:conformsTo / skos:inScheme', 'shared', 'Registre', 'Registre de référence auquel appartient le standard.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://registre.data.developpement-durable.gouv.fr/plume/StandardsRegister'], NULL, 0),
    ('dcat:distribution / dcat:accessService / dct:conformsTo / dct:identifier', 'shared', 'Identifiant', 'Identifiant du standard, s''il y a lieu. Pour un système de coordonnées géographiques, il s''agit du code EPSG.', NULL, false, 'xsd:string', false, NULL, NULL, NULL, true, false, false, NULL, NULL, 1),
    ('dcat:distribution / dcat:accessService / dct:conformsTo / dct:title', 'shared', 'Libellé', 'Libellé explicite du standard.', NULL, false, 'rdf:langString', false, NULL, NULL, NULL, true, true, false, NULL, NULL, 2),
    ('dcat:distribution / dcat:accessService / dct:conformsTo / owl:versionInfo', 'shared', 'Version', 'Numéro ou code de la version du standard à laquelle se conforment les données.', NULL, false, 'xsd:string', false, NULL, NULL, NULL, false, false, false, NULL, NULL, 3),
    ('dcat:distribution / dcat:accessService / dct:conformsTo / dct:description', 'shared', 'Description', 'Description sommaire de l''objet du standard.', NULL, false, 'rdf:langString', true, NULL, NULL, NULL, true, true, false, NULL, NULL, 4),
    ('dcat:distribution / dcat:accessService / dct:conformsTo / dct:issued', 'shared', 'Date de publication', 'Date de publication du standard.', NULL, false, 'xsd:date', false, NULL, NULL, '9999-99-99', false, false, false, NULL, NULL, 5),
    ('dcat:distribution / dcat:accessService / dct:conformsTo / dct:modified', 'shared', 'Date de modification', 'Date de la dernière modification du standard.', NULL, false, 'xsd:date', false, NULL, NULL, '9999-99-99', false, false, false, NULL, NULL, 6),
    ('dcat:distribution / dcat:accessService / dct:conformsTo / dct:created', 'shared', 'Date de création', 'Date de création du standard.', NULL, false, 'xsd:date', false, NULL, NULL, '9999-99-99', false, false, false, NULL, NULL, 7),
    ('dcat:distribution / dcat:accessService / dct:conformsTo / foaf:page', 'shared', 'Page internet', 'Chemin d''accès au standard ou URL d''une page contenant des informations sur le standard.', 'url', false, NULL, false, NULL, NULL, NULL, true, false, false, NULL, NULL, 8),
    ('dcat:distribution / dcat:accessService / dcat:endpointDescription', 'shared', 'URL de la description', 'URL de la description technique du service, par exemple le GetCapabilities d''un service WMS.', 'url', false, NULL, false, NULL, 'https://services.data.shom.fr/INSPIRE/wms/r?service=WMS&version=1.3.0&request=GetCapabilities', NULL, true, false, false, NULL, NULL, 3),
    ('dcat:distribution / dcat:accessService / dct:description', 'shared', 'Description', 'Description libre du service.', NULL, false, 'rdf:langString', true, NULL, NULL, NULL, true, true, false, NULL, NULL, 4),
    ('dcat:distribution / dcat:accessService / dcat:keyword', 'shared', 'Mots-clés libres', 'Mots ou très brèves expressions représentatives du service.', NULL, false, 'rdf:langString', false, NULL, NULL, NULL, true, false, false, NULL, NULL, 5),
    ('dcat:distribution / dcat:accessService / dct:type', 'shared', 'Type de service de données', 'Type de service de données.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://publications.europa.eu/resource/authority/data-service-type'], NULL, 6),
    ('dcat:distribution / dcat:accessService / dct:accessRights', 'shared', 'Conditions d''accès', 'Contraintes réglementaires limitant l''accès au service.', 'url', false, NULL, false, NULL, NULL, NULL, true, false, false, ARRAY['http://inspire.ec.europa.eu/metadata-codelist/LimitationsOnPublicAccess','http://publications.europa.eu/resource/authority/access-right','http://registre.data.developpement-durable.gouv.fr/plume/CrpaAccessLimitations'], NULL, 20),
    ('dcat:distribution / dcat:accessService / dct:accessRights / rdfs:label', 'shared', 'Mention', 'Description des contraintes réglementaires et des modalités pratiques pour s''y conformer.', NULL, false, 'rdf:langString', true, NULL, NULL, NULL, true, true, false, NULL, NULL, 1),
    ('dcat:distribution / dcat:accessService / dct:license', 'shared', 'Licence', 'Licence de mise à diposition des données via le service, ou conditions d''utilisation du service.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://registre.data.developpement-durable.gouv.fr/plume/CrpaAuthorizedLicense','http://publications.europa.eu/resource/authority/licence'], NULL, 21),
    ('dcat:distribution / dcat:accessService / dct:license / dct:type', 'shared', 'Type', 'Caractéristiques de la licence.', 'url', false, NULL, false, NULL, NULL, NULL, true, false, false, ARRAY['http://purl.org/adms/licencetype/1.1'], NULL, 1),
    ('dcat:distribution / dcat:accessService / dct:license / rdfs:label', 'shared', 'Termes', 'Termes de la licence.', NULL, false, 'rdf:langString', true, NULL, NULL, NULL, true, true, false, NULL, NULL, 2),
    ('dcat:distribution / dcat:accessService / dcat:contactPoint', 'shared', 'Point de contact', 'Entité à contacter pour obtenir des informations sur le service.', NULL, true, NULL, false, NULL, NULL, NULL, true, false, false, NULL, NULL, 40),
    ('dcat:distribution / dcat:accessService / dcat:contactPoint / vcard:fn', 'shared', 'Nom', 'Nom du point de contact.', NULL, false, 'xsd:string', false, NULL, NULL, NULL, false, false, true, NULL, NULL, 1),
    ('dcat:distribution / dcat:accessService / dcat:contactPoint / vcard:hasEmail', 'shared', 'Courriel', 'Adresse mél.', 'email', false, NULL, false, NULL, NULL, NULL, true, false, false, NULL, NULL, 2),
    ('dcat:distribution / dcat:accessService / dcat:contactPoint / vcard:hasTelephone', 'shared', 'Téléphone', 'Numéro de téléphone.', 'phone', false, NULL, false, NULL, '+33-1-23-45-67-89', NULL, true, false, false, NULL, NULL, 3),
    ('dcat:distribution / dcat:accessService / dcat:contactPoint / vcard:hasURL', 'shared', 'Site internet', 'Site internet.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, NULL, 4),
    ('dcat:distribution / dcat:accessService / dcat:contactPoint / vcard:organization-name', 'shared', 'Appartient à', 'Le cas échéant, organisation dont le point de contact fait partie.', NULL, false, 'xsd:string', false, NULL, NULL, NULL, false, false, false, NULL, NULL, 5),
    ('dcat:distribution / dcat:accessService / dct:publisher', 'shared', 'Éditeur', 'Organisme ou personne responsable de la mise à disposition du service.', NULL, true, NULL, false, NULL, NULL, NULL, false, false, false, NULL, NULL, 41),
    ('dcat:distribution / dcat:accessService / dct:publisher / foaf:name', 'shared', 'Nom', 'Nom de l''organisation.', NULL, false, 'rdf:langString', false, NULL, NULL, NULL, true, true, false, NULL, NULL, 0),
    ('dcat:distribution / dcat:accessService / dct:publisher / dct:type', 'shared', 'Type', 'Type d''organisation.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://purl.org/adms/publishertype/1.0'], NULL, 1),
    ('dcat:distribution / dcat:accessService / dct:publisher / foaf:mbox', 'shared', 'Courriel', 'Adresse mél.', 'email', false, NULL, false, NULL, NULL, NULL, true, false, false, NULL, NULL, 2),
    ('dcat:distribution / dcat:accessService / dct:publisher / foaf:phone', 'shared', 'Téléphone', 'Numéro de téléphone.', 'phone', false, NULL, false, NULL, '+33-1-23-45-67-89', NULL, true, false, false, NULL, NULL, 3),
    ('dcat:distribution / dcat:accessService / dct:publisher / foaf:workplaceHomepage', 'shared', 'Site internet', 'Site internet.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, NULL, 4),
    ('dcat:distribution / dcat:accessService / dct:creator', 'shared', 'Auteur', 'Principal acteur de la création du service.', NULL, true, NULL, false, NULL, NULL, NULL, false, false, false, NULL, NULL, 42),
    ('dcat:distribution / dcat:accessService / dct:creator / foaf:name', 'shared', 'Nom', 'Nom de l''organisation.', NULL, false, 'rdf:langString', false, NULL, NULL, NULL, true, true, false, NULL, NULL, 0),
    ('dcat:distribution / dcat:accessService / dct:creator / dct:type', 'shared', 'Type', 'Type d''organisation.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://purl.org/adms/publishertype/1.0'], NULL, 1),
    ('dcat:distribution / dcat:accessService / dct:creator / foaf:mbox', 'shared', 'Courriel', 'Adresse mél.', 'email', false, NULL, false, NULL, NULL, NULL, true, false, false, NULL, NULL, 2),
    ('dcat:distribution / dcat:accessService / dct:creator / foaf:phone', 'shared', 'Téléphone', 'Numéro de téléphone.', 'phone', false, NULL, false, NULL, '+33-1-23-45-67-89', NULL, true, false, false, NULL, NULL, 3),
    ('dcat:distribution / dcat:accessService / dct:creator / foaf:workplaceHomepage', 'shared', 'Site internet', 'Site internet.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, NULL, 4),
    ('dcat:distribution / dcat:accessService / dct:rightsHolder', 'shared', 'Propriétaire', 'Organisme ou personne qui détient des droits sur le service.', NULL, true, NULL, false, NULL, NULL, NULL, true, false, false, NULL, NULL, 43),
    ('dcat:distribution / dcat:accessService / dct:rightsHolder / foaf:name', 'shared', 'Nom', 'Nom de l''organisation.', NULL, false, 'rdf:langString', false, NULL, NULL, NULL, true, true, false, NULL, NULL, 0),
    ('dcat:distribution / dcat:accessService / dct:rightsHolder / dct:type', 'shared', 'Type', 'Type d''organisation.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://purl.org/adms/publishertype/1.0'], NULL, 1),
    ('dcat:distribution / dcat:accessService / dct:rightsHolder / foaf:mbox', 'shared', 'Courriel', 'Adresse mél.', 'email', false, NULL, false, NULL, NULL, NULL, true, false, false, NULL, NULL, 2),
    ('dcat:distribution / dcat:accessService / dct:rightsHolder / foaf:phone', 'shared', 'Téléphone', 'Numéro de téléphone.', 'phone', false, NULL, false, NULL, '+33-1-23-45-67-89', NULL, true, false, false, NULL, NULL, 3),
    ('dcat:distribution / dcat:accessService / dct:rightsHolder / foaf:workplaceHomepage', 'shared', 'Site internet', 'Site internet.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, NULL, 4),
    ('dcat:distribution / dcat:accessService / dct:issued', 'shared', 'Date d''ouverture', 'Date d''ouverture du service.', NULL, false, 'xsd:date', false, NULL, NULL, '9999-99-99', false, false, false, NULL, NULL, 70),
    ('dcat:distribution / dcat:accessService / dct:language', 'shared', 'Langues', 'Langue·s prises en charge par le service.', 'url', false, NULL, false, NULL, NULL, NULL, true, false, false, ARRAY['http://publications.europa.eu/resource/authority/language'], NULL, 80),
    ('dcat:distribution / dcat:accessService / dct:spatial', 'shared', 'Couverture géographique', 'Territoire couvert par le service.', NULL, true, NULL, false, NULL, NULL, NULL, true, false, false, NULL, NULL, 81),
    ('dcat:distribution / dcat:accessService / dct:spatial / skos:inScheme', 'shared', 'Index géographique', 'Type de lieu, index de référence pour l''identifiant (commune, département...).', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://registre.data.developpement-durable.gouv.fr/plume/InseeGeoIndex'], NULL, 0),
    ('dcat:distribution / dcat:accessService / dct:spatial / dct:identifier', 'shared', 'Code géographique', 'Code du département, code INSEE de la commune, etc.', NULL, false, 'xsd:string', false, NULL, NULL, NULL, true, false, false, NULL, NULL, 1),
    ('dcat:distribution / dcat:accessService / dct:spatial / skos:prefLabel', 'shared', 'Libellé', 'Dénomination explicite du lieu.', NULL, false, 'rdf:langString', false, NULL, NULL, NULL, true, true, false, NULL, NULL, 2),
    ('dcat:distribution / dcat:accessService / dct:spatial / dcat:bbox', 'shared', 'Rectangle d''emprise', 'Rectangle d''emprise (BBox), au format textuel WKT.', NULL, false, 'gsp:wktLiteral', true, NULL, '<http://www.opengis.net/def/crs/EPSG/0/2154> POLYGON((646417.3289 6857521.1356, 657175.3272 6857521.1356, 657175.3272 6867076.0360, 646417.3289 6867076.0360, 646417.3289 6857521.1356))', NULL, false, false, false, NULL, ARRAY['show','bbox','rectangle']::z_plume.meta_geo_tool[], 3),
    ('dcat:distribution / dcat:accessService / dct:spatial / dcat:centroid', 'shared', 'Centroïde', 'Localisant du centre géographique des données, au format textuel WKT.', NULL, false, 'gsp:wktLiteral', true, NULL, '<http://www.opengis.net/def/crs/EPSG/0/2154> POINT(651796.3281 6862298.5858)', NULL, false, false, false, NULL, ARRAY['show','centroid','point']::z_plume.meta_geo_tool[], 4),
    ('dcat:distribution / dcat:accessService / dct:spatial / locn:geometry', 'shared', 'Géométrie', 'Emprise géométrique, au format textuel WKT.', NULL, false, 'gsp:wktLiteral', true, NULL, '<http://www.opengis.net/def/crs/EPSG/0/2154> POLYGON((646417.3289 6857521.1356, 657175.3272 6857521.1356, 657175.3272 6867076.0360, 646417.3289 6867076.0360, 646417.3289 6857521.1356))', NULL, false, false, false, NULL, ARRAY['show','point','linestring','polygon','circle']::z_plume.meta_geo_tool[], 5),
    ('dcat:distribution / dcat:accessService / dcat:spatialResolutionInMeters', 'shared', 'Résolution spatiale en mètres', 'Résolution des données mises à disposition par le service, exprimée en mètres.', NULL, false, 'xsd:decimal', false, NULL, NULL, NULL, false, false, false, NULL, NULL, 82),
    ('dcat:distribution / dcat:accessService / dct:temporal', 'shared', 'Couverture temporelle', 'Période pour laquelle des données sont mises à disposition par le service.', NULL, true, NULL, false, NULL, NULL, NULL, true, false, false, NULL, NULL, 83),
    ('dcat:distribution / dcat:accessService / dct:temporal / dcat:startDate', 'shared', 'Date de début', 'Date de début de la période.', NULL, false, 'xsd:date', false, NULL, NULL, '9999-99-99', false, false, false, NULL, NULL, 0),
    ('dcat:distribution / dcat:accessService / dct:temporal / dcat:endDate', 'shared', 'Date de fin', 'Date de fin de la période.', NULL, false, 'xsd:date', false, NULL, NULL, '9999-99-99', false, false, false, NULL, NULL, 1),
    ('dcat:distribution / dcat:accessService / dcat:temporalResolution', 'shared', 'Résolution temporelle', 'Résolution temporelle des données mises à disposition par le service.', NULL, false, 'xsd:duration', false, NULL, NULL, NULL, false, false, false, NULL, NULL, 84),
    ('dcat:distribution / adms:representationTechnique', 'shared', 'Mode de représentation géographique', 'Type de représentation technique de l''information géographique présentée par la distribution, le cas échéant.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://inspire.ec.europa.eu/metadata-codelist/SpatialRepresentationType'], NULL, 15),
    ('dcat:distribution / foaf:page', 'shared', 'Documentation', 'Documentation ou page internet contenant des informations relative à la distribution.', 'url', false, NULL, false, NULL, NULL, NULL, true, false, false, NULL, NULL, 16),
    ('dcat:distribution / dct:conformsTo', 'shared', 'Conforme à', 'Standard, schéma, référentiel de coordonnées, etc. auquel se conforment les données de la distribution.', 'url', false, NULL, false, NULL, NULL, NULL, true, false, false, ARRAY['http://www.opengis.net/def/crs/EPSG/0'], NULL, 17),
    ('dcat:distribution / dct:conformsTo / skos:inScheme', 'shared', 'Registre', 'Registre de référence auquel appartient le standard.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://registre.data.developpement-durable.gouv.fr/plume/StandardsRegister'], NULL, 0),
    ('dcat:distribution / dct:conformsTo / dct:identifier', 'shared', 'Identifiant', 'Identifiant du standard, s''il y a lieu. Pour un système de coordonnées géographiques, il s''agit du code EPSG.', NULL, false, 'xsd:string', false, NULL, NULL, NULL, true, false, false, NULL, NULL, 1),
    ('dcat:distribution / dct:conformsTo / dct:title', 'shared', 'Libellé', 'Libellé explicite du standard.', NULL, false, 'rdf:langString', false, NULL, NULL, NULL, true, true, false, NULL, NULL, 2),
    ('dcat:distribution / dct:conformsTo / owl:versionInfo', 'shared', 'Version', 'Numéro ou code de la version du standard à laquelle se conforment les données.', NULL, false, 'xsd:string', false, NULL, NULL, NULL, false, false, false, NULL, NULL, 3),
    ('dcat:distribution / dct:conformsTo / dct:description', 'shared', 'Description', 'Description sommaire de l''objet du standard.', NULL, false, 'rdf:langString', true, NULL, NULL, NULL, true, true, false, NULL, NULL, 4),
    ('dcat:distribution / dct:conformsTo / dct:issued', 'shared', 'Date de publication', 'Date de publication du standard.', NULL, false, 'xsd:date', false, NULL, NULL, '9999-99-99', false, false, false, NULL, NULL, 5),
    ('dcat:distribution / dct:conformsTo / dct:modified', 'shared', 'Date de modification', 'Date de la dernière modification du standard.', NULL, false, 'xsd:date', false, NULL, NULL, '9999-99-99', false, false, false, NULL, NULL, 6),
    ('dcat:distribution / dct:conformsTo / dct:created', 'shared', 'Date de création', 'Date de création du standard.', NULL, false, 'xsd:date', false, NULL, NULL, '9999-99-99', false, false, false, NULL, NULL, 7),
    ('dcat:distribution / dct:conformsTo / foaf:page', 'shared', 'Page internet', 'Chemin d''accès au standard ou URL d''une page contenant des informations sur le standard.', 'url', false, NULL, false, NULL, NULL, NULL, true, false, false, NULL, NULL, 8),
    ('dcat:distribution / cnt:characterEncoding', 'shared', 'Encodage', 'Encodage de la distribution.', NULL, false, 'xsd:string', false, NULL, 'ex : UTF-8, ISO-8859-1, US-ASCII...', NULL, false, false, false, NULL, NULL, 20),
    ('dcat:distribution / dct:language', 'shared', 'Langue', 'Langue·s des données de la distribution.', 'url', false, NULL, false, NULL, NULL, NULL, true, false, false, ARRAY['http://publications.europa.eu/resource/authority/language'], NULL, 21),
    ('dcat:distribution / dcat:byteSize', 'shared', 'Taille en bytes', 'Taille en bytes de la distribution.', NULL, false, 'xsd:decimal', false, NULL, NULL, NULL, false, false, false, NULL, NULL, 22),
    ('dcat:distribution / dcat:temporalResolution', 'shared', 'Résolution temporelle', 'Plus petit pas de temps significatif dans le contexte de la distribution.', NULL, false, 'xsd:duration', false, NULL, NULL, NULL, false, false, false, NULL, NULL, 23),
    ('dcat:distribution / dcat:spatialResolutionInMeters', 'shared', 'Résolution spatiale en mètres', 'Résolution des données de la distribution, exprimée en mètres.', NULL, false, 'xsd:decimal', false, NULL, NULL, NULL, false, false, false, NULL, NULL, 24),
    ('dcat:distribution / dct:rights', 'shared', 'Propriété intellectuelle', 'Mention rappelant les droits de propriété intellectuelle sur les données, à faire apparaître en cas de réutilisation de cette distribution des données.', NULL, true, NULL, false, NULL, NULL, NULL, false, false, false, NULL, NULL, 30),
    ('dcat:distribution / dct:rights / rdfs:label', 'shared', 'Mention', 'Description des contraintes réglementaires et des modalités pratiques pour s''y conformer.', NULL, false, 'rdf:langString', true, NULL, NULL, NULL, true, true, false, NULL, NULL, 1),
    ('dcat:distribution / dct:license', 'shared', 'Licence', 'Licence sous laquelle est publiée la distribution ou conditions d''utilisation de la distribution.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://registre.data.developpement-durable.gouv.fr/plume/CrpaAuthorizedLicense','http://publications.europa.eu/resource/authority/licence'], NULL, 31),
    ('dcat:distribution / dct:license / dct:type', 'shared', 'Type', 'Caractéristiques de la licence.', 'url', false, NULL, false, NULL, NULL, NULL, true, false, false, ARRAY['http://purl.org/adms/licencetype/1.1'], NULL, 1),
    ('dcat:distribution / dct:license / rdfs:label', 'shared', 'Termes', 'Termes de la licence.', NULL, false, 'rdf:langString', true, NULL, NULL, NULL, true, true, false, NULL, NULL, 2),
    ('dcat:distribution / dct:accessRights', 'shared', 'Conditions d''accès', 'Contraintes réglementaires limitant l''accès à la distribution.', 'url', false, NULL, false, NULL, NULL, NULL, true, false, false, ARRAY['http://inspire.ec.europa.eu/metadata-codelist/LimitationsOnPublicAccess','http://publications.europa.eu/resource/authority/access-right','http://registre.data.developpement-durable.gouv.fr/plume/CrpaAccessLimitations'], NULL, 32),
    ('dcat:distribution / dct:accessRights / rdfs:label', 'shared', 'Mention', 'Description des contraintes réglementaires et des modalités pratiques pour s''y conformer.', NULL, false, 'rdf:langString', true, NULL, NULL, NULL, true, true, false, NULL, NULL, 1),
    ('dcat:landingPage', 'shared', 'Page internet', 'URL de la fiche de métadonnées sur internet.', 'url', false, NULL, false, NULL, NULL, NULL, true, false, false, NULL, NULL, 60),
    ('foaf:page', 'shared', 'Documentation', 'URL d''accès à une documentation rédigée décrivant la donnée.', 'url', false, NULL, false, NULL, NULL, NULL, true, false, false, NULL, NULL, 61),
    ('dct:isReferencedBy', 'shared', 'Cité par', 'URL d''une publication qui utilise ou évoque les données.', 'url', false, NULL, false, NULL, NULL, NULL, true, false, false, NULL, NULL, 62),
    ('dct:relation', 'shared', 'Ressource liée', 'URL d''accès à une ressource en rapport avec les données.', 'url', false, NULL, false, NULL, NULL, NULL, true, false, false, NULL, NULL, 63),
    ('dct:language', 'shared', 'Langue des données', 'Langue·s des données.', 'url', false, NULL, false, NULL, NULL, NULL, true, false, false, ARRAY['http://publications.europa.eu/resource/authority/language'], NULL, 80),
    ('plume:relevanceScore', 'shared', 'Score', 'Niveau de pertinence de la donnée. Plus le score est élevé plus la donnée sera mise en avant dans les résultats de recherche.', NULL, false, 'xsd:integer', false, NULL, NULL, NULL, false, false, false, NULL, NULL, 81),
    ('dct:type', 'shared', 'Type de jeu de données', 'Type de jeu de données.', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://publications.europa.eu/resource/authority/dataset-type'], NULL, 82),
    ('dct:identifier', 'shared', 'Identifiant interne', 'Identifiant du jeu de données, attribué automatiquement par Plume.', NULL, false, 'xsd:string', false, NULL, NULL, NULL, false, false, false, NULL, NULL, 83),
    ('plume:linkedRecord', 'shared', 'Fiche distante', 'Configuration d''import des métadonnées depuis une fiche de catalogue INSPIRE.', NULL, true, NULL, false, NULL, NULL, NULL, false, false, false, NULL, NULL, 84),
    ('plume:linkedRecord / dcat:endpointURL', 'shared', 'Service CSW', 'URL de base du service CSW, sans aucun paramètre.', 'url', false, NULL, false, NULL, 'http://ogc.geo-ide.developpement-durable.gouv.fr/csw/dataset-harvestable', NULL, false, false, false, NULL, NULL, 0),
    ('plume:linkedRecord / dct:identifier', 'shared', 'Identifiant de la fiche', 'Identifiant de la fiche de métadonnées (et non de la ressource).', NULL, false, 'xsd:string', false, NULL, 'fr-120066022-jdd-d3d794eb-76ba-450a-9f03-6eb84662f297', NULL, false, false, false, NULL, NULL, 1),
    ('foaf:isPrimaryTopicOf', 'shared', 'Informations sur les métadonnées', 'Métadonnées des métadonnées.', NULL, true, NULL, false, NULL, NULL, NULL, false, false, false, NULL, NULL, 85),
    ('foaf:isPrimaryTopicOf / dct:modified', 'shared', 'Date de modification des métadonnées', 'Date et heure de la dernière modification des métadonnées. Cette propriété est renseignée automatiquement par Plume lors de la sauvegarde de la fiche de métadonnées.', NULL, false, 'xsd:dateTime', false, NULL, NULL, '9999-99-99T99:99:99', false, false, false, NULL, NULL, 0) ;

-- Function: z_plume.meta_shared_categorie_before_insert()

CREATE OR REPLACE FUNCTION z_plume.meta_shared_categorie_before_insert()
	RETURNS trigger
    LANGUAGE plpgsql
    AS $BODY$
/* OBJET : Fonction exécutée par le trigger meta_shared_categorie_before_insert,
qui supprime les lignes pré-existantes (même valeur de "path") faisant l'objet
de commandes INSERT. Autrement dit, elle permet d'utiliser des commandes INSERT
pour réaliser des UPDATE.

Ne vaut que pour les catégories des métadonnées communes (les seules stockées
dans z_plume.meta_shared_categorie).

Cette fonction est nécessaire pour que l'extension metadata puisse initialiser
la table avec les catégories partagées, et que les modifications faites par
l'administrateur sur ces enregistrements puissent ensuite être préservées en cas
de sauvegarde/restauration (table marquée comme table de configuration de
l'extension).

CIBLE : z_plume.meta_shared_categorie.
PORTEE : FOR EACH ROW.
DECLENCHEMENT : BEFORE INSERT.*/
BEGIN
	
	DELETE FROM z_plume.meta_shared_categorie
		WHERE meta_shared_categorie.path = NEW.path ;
		
	RETURN NEW ;

END
$BODY$ ;

COMMENT ON FUNCTION z_plume.meta_shared_categorie_before_insert() IS 'Fonction exécutée par le trigger meta_shared_categorie_before_insert, qui supprime les lignes pré-existantes (même valeur de "path") faisant l''objet de commandes INSERT.' ;


-- Trigger: meta_shared_categorie_before_insert

CREATE TRIGGER meta_shared_categorie_before_insert
    BEFORE INSERT
    ON z_plume.meta_shared_categorie
    FOR EACH ROW
    EXECUTE PROCEDURE z_plume.meta_shared_categorie_before_insert() ;
	
COMMENT ON TRIGGER meta_shared_categorie_before_insert ON z_plume.meta_shared_categorie IS 'Supprime les lignes pré-existantes (même valeur de "path") faisant l''objet de commandes INSERT.' ;


-- Table: z_plume.meta_local_categorie

CREATE TABLE z_plume.meta_local_categorie 
    PARTITION OF z_plume.meta_categorie (
        CONSTRAINT meta_local_categorie_pkey PRIMARY KEY (path),
        CONSTRAINT meta_local_categorie_path_check CHECK (path ~ '^uuid[:][0-9a-z-]{36}$'),
		CONSTRAINT meta_local_categorie_is_node_check CHECK (NOT is_node),
        CONSTRAINT meta_local_categorie_sources_check CHECK (sources IS NULL)
    )
    FOR VALUES IN ('local') ;
    
COMMENT ON TABLE z_plume.meta_local_categorie IS 'Catégories de métadonnées supplémentaires (ajouts locaux).' ;

COMMENT ON COLUMN z_plume.meta_local_categorie.path IS 'Chemin SPARQL de la catégorie (identifiant unique). CE CHAMP EST GENERE AUTOMATIQUEMENT, NE PAS MODIFIER MANUELLEMENT.' ;
COMMENT ON COLUMN z_plume.meta_local_categorie.origin IS 'Origine de la catégorie. Toujours ''local''. CE CHAMP EST GENERE AUTOMATIQUEMENT, NE PAS MODIFIER MANUELLEMENT.' ;
COMMENT ON COLUMN z_plume.meta_local_categorie.label IS 'Libellé de la catégorie.' ;
COMMENT ON COLUMN z_plume.meta_local_categorie.description IS 'Description de la catégorie. Sera affiché sous la forme d''un texte d''aide dans le formulaire.' ;
COMMENT ON COLUMN z_plume.meta_local_categorie.special IS 'Le cas échéant, mise en forme spécifique à appliquer au champ. Valeurs autorisées : ''url'', ''email'', ''phone''.' ;
COMMENT ON COLUMN z_plume.meta_local_categorie.is_node IS 'True si la catégorie est le nom d''un groupe qui contiendra lui-même d''autres catégories et non une catégorie à laquelle sera directement associée une valeur. Par exemple, is_node vaut True pour la catégorie correspondant au point de contact (dcat:contactPoint) et False pour le nom du point de contact (dcat:contactPoint / vcard:fn). CE CHAMP EST GENERE AUTOMATIQUEMENT, NE PAS MODIFIER MANUELLEMENT.' ;
COMMENT ON COLUMN z_plume.meta_local_categorie.datatype IS 'Type de valeur attendu pour la catégorie. Cette information détermine notamment la nature des widgets utilisés par Plume pour afficher et éditer les valeurs, ainsi que les validateurs appliqués.' ;
COMMENT ON COLUMN z_plume.meta_local_categorie.is_long_text IS 'True pour une catégorie appelant un texte de plusieurs lignes. Cette information ne sera prise en compte que si le type de valeur (datatype) est ''xsd:string'' ou ''rdf:langString''.' ;
COMMENT ON COLUMN z_plume.meta_local_categorie.rowspan IS 'Nombre de lignes occupées par le widget de saisie, s''il y a lieu de modifier le comportement par défaut de Plume. La valeur ne sera considérée que si is_long_text vaut True.' ;
COMMENT ON COLUMN z_plume.meta_local_categorie.placeholder IS 'Valeur fictive pré-affichée en tant qu''exemple dans le widget de saisie, s''il y a lieu.' ;
COMMENT ON COLUMN z_plume.meta_local_categorie.input_mask IS 'Masque de saisie, s''il y a lieu. La valeur sera ignorée si le widget utilisé pour la catégorie ne prend pas en charge ce mécanisme.' ;
COMMENT ON COLUMN z_plume.meta_local_categorie.is_multiple IS 'True si la catégorie admet plusieurs valeurs.' ;
COMMENT ON COLUMN z_plume.meta_local_categorie.unilang IS 'True si la catégorie n''admet plusieurs valeurs que si elles sont dans des langues différentes (par exemple un jeu de données n''a en principe qu''un seul titre, mais il peut être traduit). is_multiple est ignoré quand unilang vaut True.' ;
COMMENT ON COLUMN z_plume.meta_local_categorie.is_mandatory IS 'True si une valeur doit obligatoirement être saisie pour cette catégorie.' ;
COMMENT ON COLUMN z_plume.meta_local_categorie.sources IS 'Pour une catégorie prenant ses valeurs dans un ou plusieurs thésaurus, liste des sources admises. Cette information n''est pas considérée que pour les catégories locales.' ;
COMMENT ON COLUMN z_plume.meta_local_categorie.geo_tools IS 'Pour une catégorie prenant pour valeurs des géométries, liste des fonctionnalités d''aide à la saisie à proposer. Cette information ne sera considérée que si le type (datatype) est ''gsp:wktLiteral''.' ;
COMMENT ON COLUMN z_plume.meta_local_categorie.compute IS 'Ignoré pour les catégories locales.' ;
COMMENT ON COLUMN z_plume.meta_local_categorie.template_order IS 'Ordre d''apparence de la catégorie dans le formulaire. Les plus petits numéros sont affichés en premier.' ;

-- la table est marquée comme table de configuration de l'extension
SELECT pg_extension_config_dump('z_plume.meta_local_categorie'::regclass, '') ;


------ 1.2 - TABLE DES MODELES ------

-- Table: z_plume.meta_template

CREATE TABLE z_plume.meta_template (
    tpl_label varchar(48) PRIMARY KEY,
	sql_filter text,
    md_conditions jsonb,
    priority int,
	comment text
    ) ;
    
COMMENT ON TABLE z_plume.meta_template IS 'Modèles de formulaires définis pour le plugin QGIS.' ;

COMMENT ON COLUMN z_plume.meta_template.tpl_label IS 'Nom du modèle (limité à 48 caractères).' ;
COMMENT ON COLUMN z_plume.meta_template.sql_filter IS 'Condition à remplir pour que ce modèle soit appliqué par défaut à une fiche de métadonnées, sous la forme d''un filtre SQL. On pourra utiliser $1 pour représenter le nom du schéma et $2 le nom de la table.
Par exemple :
- ''$1 ~ ANY(ARRAY[''''^r_'''', ''''^e_'''']'' appliquera le modèle aux tables des schémas des blocs "données référentielles" (préfixe ''r_'') et "données externes" (préfixe ''e_'') de la nomenclature nationale ;
- ''pg_has_role(''''g_admin'''', ''''USAGE'''')'' appliquera le modèle pour toutes les fiches de métadonnées dès lors que l''utilisateur est membre du rôle g_admin.' ;
COMMENT ON COLUMN z_plume.meta_template.md_conditions IS 'Ensemble de conditions sur les métadonnées appelant l''usage de ce modèle. Prend la forme d''une liste de dictionnaires JSON, où chaque clé est le chemin d''une catégorie et la valeur l''une des valeur prises par la catégorie. Les éléments de la liste sont joints par l''opérateur OR, chaque item des dictionnaires par l''opérateur AND. Ainsi, dans l''exemple suivant, le modèle sera retenu pour une donnée externe avec le mot-clé "IGN" (premier ensemble de conditions) ou pour une donnée publiée par l''IGN (second ensemble de conditions) :
[
    {
        "plume:isExternal": True,
        "dcat:keyword": "IGN"
    },
    {
        "dct:publisher / foaf:name": "Institut national de l''information géographique et forestière (IGN-F)"
    }
]' ;
COMMENT ON COLUMN z_plume.meta_template.priority IS 'Niveau de priorité du modèle. Si un jeu de données remplit les conditions de plusieurs modèles, celui dont la priorité est la plus élevée sera retenu comme modèle par défaut.' ;
COMMENT ON COLUMN z_plume.meta_template.comment IS 'Commentaire libre.' ;

-- la table est marquée comme table de configuration de l'extension
SELECT pg_extension_config_dump('z_plume.meta_template'::regclass, '') ;


-- Function: z_plume.meta_execute_sql_filter(text, text, text)

CREATE OR REPLACE FUNCTION z_plume.meta_execute_sql_filter(
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

COMMENT ON FUNCTION z_plume.meta_execute_sql_filter(text, text, text) IS 'Détermine si un filtre SQL est vérifié.' ;


---- 1.3 - TABLE DES ONGLETS ------

CREATE TABLE z_plume.meta_tab (
    tab varchar(48) PRIMARY KEY,
    tab_num int
    ) ;
    
COMMENT ON TABLE z_plume.meta_tab IS 'Onglets des modèles.' ;

COMMENT ON COLUMN z_plume.meta_tab.tab IS 'Nom de l''onglet.' ;
COMMENT ON COLUMN z_plume.meta_tab.tab_num IS 'Numéro de l''onglet. Les onglets sont affichés du plus petit numéro au plus grand (NULL à la fin), puis par ordre alphabétique en cas d''égalité. Les numéros n''ont pas à se suivre et peuvent être répétés.' ;

-- la table est marquée comme table de configuration de l'extension
SELECT pg_extension_config_dump('z_plume.meta_tab'::regclass, '') ;


---- 1.4 - ASSOCIATION DES CATEGORIES AUX MODELES ------

-- Table z_plume.meta_template_categories

CREATE TABLE z_plume.meta_template_categories (
    tplcat_id serial PRIMARY KEY,
    tpl_label varchar(48) NOT NULL,
    shrcat_path text,
    loccat_path text,
    label text,
    description text,
    special z_plume.meta_special,
	datatype z_plume.meta_datatype,
    is_long_text boolean,
    rowspan int,
    placeholder text,
    input_mask text,
    is_multiple boolean,
    unilang text,
    is_mandatory boolean,
    sources text[],
    geo_tools z_plume.meta_geo_tool[],
    compute z_plume.meta_compute[],
    template_order int,
    is_read_only boolean,
    tab varchar(48),
    CONSTRAINT meta_template_categories_tpl_cat_uni UNIQUE (tpl_label, shrcat_path, loccat_path),
    CONSTRAINT meta_template_categories_tpl_label_fkey FOREIGN KEY (tpl_label)
        REFERENCES z_plume.meta_template (tpl_label)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT meta_template_categories_shrcat_path_fkey FOREIGN KEY (shrcat_path)
        REFERENCES z_plume.meta_shared_categorie (path)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT meta_template_categories_loccat_path_fkey FOREIGN KEY (loccat_path)
        REFERENCES z_plume.meta_local_categorie (path)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT meta_template_categories_tab_fkey FOREIGN KEY (tab)
        REFERENCES z_plume.meta_tab (tab)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT meta_template_categories_path_check CHECK (
        shrcat_path IS NULL OR loccat_path IS NULL
        AND shrcat_path IS NOT NULL OR loccat_path IS NOT NULL
        ),
    CONSTRAINT meta_template_categories_rowspan_check CHECK (rowspan BETWEEN 1 AND 99)
    ) ;

COMMENT ON TABLE z_plume.meta_template_categories IS 'Désignation des catégories utilisées par chaque modèle de formulaire.
Les autres champs permettent de personnaliser la présentation des catégories pour le modèle considéré. S''ils ne sont pas renseignés, les valeurs saisies dans meta_categorie seront utilisées. À défaut, le plugin s''appuyera sur le schéma des catégories communes (évidemment pour les catégories communes uniquement).' ;

COMMENT ON COLUMN z_plume.meta_template_categories.tplcat_id IS 'Identifiant unique.' ;
COMMENT ON COLUMN z_plume.meta_template_categories.tpl_label IS 'Nom du modèle de formulaire.' ;
COMMENT ON COLUMN z_plume.meta_template_categories.shrcat_path IS 'Chemin N3 / identifiant de la catégorie de métadonnées (si catégorie commune).' ;
COMMENT ON COLUMN z_plume.meta_template_categories.loccat_path IS 'Chemin N3 / identifiant de la catégorie de métadonnées (si catégorie supplémentaire locale).' ;
COMMENT ON COLUMN z_plume.meta_template_categories.label IS 'Libellé de la catégorie. Si présente, cette valeur se substitue pour le modèle considéré à la valeur renseignée dans le champ éponyme de meta_categorie.' ;
COMMENT ON COLUMN z_plume.meta_template_categories.description IS 'Description de la catégorie. Sera affiché sous la forme d''un texte d''aide dans le formulaire. Si présente, cette valeur se substitue pour le modèle considéré à la valeur renseignée dans le champ éponyme de meta_categorie.' ;
COMMENT ON COLUMN z_plume.meta_template_categories.special IS 'Le cas échéant, mise en forme spécifique à appliquer au champ. Valeurs autorisées : ''url'', ''email'', ''phone''. Si présente, cette valeur se substitue pour le modèle considéré à la valeur renseignée dans le champ éponyme de meta_categorie. Pour les catégories communes, les modifications apportées à ce champ ne seront pas prises en compte.' ;
COMMENT ON COLUMN z_plume.meta_template_categories.datatype IS 'Type de valeur attendu pour la catégorie. Cette information détermine notamment la nature des widgets utilisés par Plume pour afficher et éditer les valeurs, ainsi que les validateurs appliqués. Si présente, cette valeur se substitue pour le modèle considéré à la valeur renseignée dans le champ éponyme de meta_categorie. Pour les catégories communes, les modifications apportées à ce champ ne seront pas prises en compte.' ;
COMMENT ON COLUMN z_plume.meta_template_categories.is_long_text IS 'True pour une catégorie appelant un texte de plusieurs lignes. Si présente, cette valeur se substitue pour le modèle considéré à la valeur renseignée dans le champ éponyme de meta_categorie. Cette information ne sera prise en compte que si le type de valeur (datatype) est ''xsd:string'' ou ''rdf:langString''.' ;
COMMENT ON COLUMN z_plume.meta_template_categories.rowspan IS 'Nombre de lignes occupées par le widget de saisie, s''il y a lieu de modifier le comportement par défaut de Plume. Si présente, cette valeur se substitue pour le modèle considéré à la valeur renseignée dans le champ éponyme de meta_categorie. La valeur ne sera considérée que si is_long_text vaut True.' ;
COMMENT ON COLUMN z_plume.meta_template_categories.placeholder IS 'Valeur fictive pré-affichée en tant qu''exemple dans le widget de saisie, s''il y a lieu. Si présente, cette valeur se substitue pour le modèle considéré à la valeur renseignée dans le champ éponyme de meta_categorie.' ;
COMMENT ON COLUMN z_plume.meta_template_categories.input_mask IS 'Masque de saisie, s''il y a lieu. Si présente, cette valeur se substitue pour le modèle considéré à la valeur renseignée dans le champ éponyme de meta_categorie. La valeur sera ignorée si le widget utilisé pour la catégorie ne prend pas en charge ce mécanisme.' ;
COMMENT ON COLUMN z_plume.meta_template_categories.is_multiple IS 'True si la catégorie admet plusieurs valeurs. Si présente, cette valeur se substitue pour le modèle considéré à la valeur renseignée dans le champ éponyme de meta_categorie. Pour les catégories commnes, les modifications apportées à ce champ ne seront pas prises en compte.' ;
COMMENT ON COLUMN z_plume.meta_template_categories.unilang IS 'True si la catégorie n''admet plusieurs valeurs que si elles sont dans des langues différentes (par exemple un jeu de données n''a en principe qu''un seul titre, mais il peut être traduit). Si présente, cette valeur se substitue pour le modèle considéré à la valeur renseignée dans le champ éponyme de meta_categorie. is_multiple est ignoré quand unilang vaut True. Pour les catégories commnes, les modifications apportées à ce champ ne seront pas prises en compte.' ;
COMMENT ON COLUMN z_plume.meta_template_categories.is_mandatory IS 'True si une valeur doit obligatoirement être saisie pour cette catégorie. Si présente, cette valeur se substitue pour le modèle considéré à la valeur renseignée dans le champ éponyme de meta_categorie. À noter que ce champ permet de rendre obligatoire une catégorie commune optionnelle, pas l''inverse.' ;
COMMENT ON COLUMN z_plume.meta_template_categories.sources IS 'Pour une catégorie prenant ses valeurs dans un ou plusieurs thésaurus, liste des sources admises. Si présente, cette valeur se substitue pour le modèle considéré à la valeur renseignée dans le champ éponyme de meta_categorie. Cette information n''est considérée que pour les catégories communes. Il n''est pas possible d''ajouter des sources ni de les retirer toutes - Plume reviendrait alors à la liste initiale -, mais ce champ permet de restreindre la liste à un ou plusieurs thésaurus jugés les mieux adaptés.' ;
COMMENT ON COLUMN z_plume.meta_template_categories.geo_tools IS 'Pour une catégorie prenant pour valeurs des géométries, liste des fonctionnalités d''aide à la saisie à proposer. Cette information ne sera considérée que si le type (datatype) est ''gsp:wktLiteral''. Si présente, cette valeur se substitue pour le modèle considéré à la valeur renseignée dans le champ éponyme de meta_categorie. Pour retirer toutes les fonctionnalités proposées par défaut pour une catégorie commune, on saisira une liste vide.' ;
COMMENT ON COLUMN z_plume.meta_template_categories.compute IS 'Liste des fonctionnalités de calcul à proposer. Cette information ne sera considérée que si une méthode de calcul est effectivement disponible pour la catégorie. Si présente, cette valeur se substitue pour le modèle considéré à la valeur renseignée dans le champ éponyme de meta_categorie. Pour retirer toutes les fonctionnalités proposées par défaut pour une catégorie commune, on saisira une liste vide.' ;
COMMENT ON COLUMN z_plume.meta_template_categories.template_order IS 'Ordre d''apparence de la catégorie dans le formulaire. Les plus petits numéros sont affichés en premier. Si présente, cette valeur se substitue pour le modèle considéré à la valeur renseignée dans le champ éponyme de meta_categorie.' ;
COMMENT ON COLUMN z_plume.meta_template_categories.is_read_only IS 'True si la catégorie est en lecture seule.' ;
COMMENT ON COLUMN z_plume.meta_template_categories.tab IS 'Nom de l''onglet du formulaire où placer la catégorie. Cette information n''est considérée que pour les catégories locales et les catégories communes de premier niveau (par exemple "dcat:distribution / dct:issued" ira nécessairement dans le même onglet que "dcat:distribution"). Pour celles-ci, si aucun onglet n''est fourni, la catégorie ira toujours dans le premier onglet cité pour le modèle dans la présente table ou, à défaut, dans un onglet "Général".' ;

-- la table et la séquence sont marquées comme tables de configuration de l'extension
SELECT pg_extension_config_dump('z_plume.meta_template_categories'::regclass, '') ;
SELECT pg_extension_config_dump('z_plume.meta_template_categories_tplcat_id_seq'::regclass, '') ;


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
        tc.tab
        FROM z_plume.meta_template_categories AS tc
            LEFT JOIN z_plume.meta_categorie AS c
                ON coalesce(tc.shrcat_path, tc.loccat_path) = c.path
            LEFT JOIN z_plume.meta_template AS t
                ON tc.tpl_label = t.tpl_label
    ) ;

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


------ 1.5 - IMPORT DE MODELES PRE-CONFIGURES -------

-- Function: z_plume.meta_import_sample_template(text)

CREATE OR REPLACE FUNCTION z_plume.meta_import_sample_template(
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

