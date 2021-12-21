\echo Use "CREATE EXTENSION plume_pg" to load this file. \quit
-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
--
-- PlumePg - Système de gestion des métadonnées locales
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
-- schéma contenant les objets : z_plume
--
-- objets créés par le script :
-- - Schema: z_plume
-- - Type: z_plume.meta_special
-- - Type: z_plume.meta_datatype
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
            UPDATE z_asgard.gestion_schema_usr
                SET producteur = 'g_admin',
                    lecteur = 'g_consult'
                WHERE nom_schema = 'z_plume' ;
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
	'xsd:string', 'xsd:integer', 'xsd:decimal', 'xsd:float', 'xsd:double',
    'xsd:boolean', 'xsd:date', 'xsd:time', 'xsd:dateTime', 'xsd:duration',
    'gsp:wktLiteral', 'rdf:langString'
	) ;
	
COMMENT ON TYPE z_plume.meta_datatype IS 'Types de valeurs supportés par Plume.' ;


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
COMMENT ON COLUMN z_plume.meta_shared_categorie.template_order IS 'Ordre d''apparence de la catégorie dans le formulaire. Les plus petits numéros sont affichés en premier.' ;

-- la table est marquée comme table de configuration de l'extension
SELECT pg_extension_config_dump('z_plume.meta_shared_categorie'::regclass, '') ;

-- extraction du schéma SHACL
INSERT INTO z_plume.meta_categorie (
        path, origin, label, description, special,
        is_node, datatype, is_long_text, rowspan,
        placeholder, input_mask, is_multiple, unilang,
        is_mandatory, sources, template_order
    ) VALUES
    ('dct:title', 'shared', 'Libellé', 'Libellé explicite du jeu de données.', NULL, false, 'rdf:langString', false, NULL, NULL, NULL, true, true, true, NULL, 0),
    ('owl:versionInfo', 'shared', 'Version', 'Numéro de version ou millésime du jeu de données.', NULL, false, 'xsd:string', false, NULL, NULL, NULL, false, false, false, NULL, 1),
    ('dct:description', 'shared', 'Description', 'Description du jeu de données.', NULL, false, 'rdf:langString', true, 15, NULL, NULL, true, true, true, NULL, 2),
    ('snum:isExternal', 'shared', 'Donnée externe', 'S''agit-il de la reproduction d''un jeu de données produit par un tiers ?', NULL, false, 'xsd:boolean', false, NULL, NULL, NULL, false, false, false, NULL, 3),
    ('dcat:theme', 'shared', 'Thème', NULL, 'url', false, NULL, false, NULL, NULL, NULL, true, false, false, ARRAY['http://publications.europa.eu/resource/authority/data-theme','https://inspire.ec.europa.eu/theme'], 4),
    ('dct:subject', 'shared', 'Catégorie ISO 19115', NULL, 'url', false, NULL, false, NULL, NULL, NULL, true, false, false, NULL, 5),
    ('dcat:keyword', 'shared', 'Mots-clé libres', NULL, NULL, false, 'rdf:langString', false, NULL, NULL, NULL, true, false, false, NULL, 6),
    ('dct:spatial', 'shared', 'Couverture géographique', NULL, NULL, true, NULL, false, NULL, NULL, NULL, true, false, false, NULL, 9),
    ('dct:spatial / skos:inScheme', 'shared', 'Index géographique', 'Type de lieu, index de référence pour l''identifiant (commune, département...).', 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://snum.scenari-community.org/Metadata/Vocabulaire/#InseeGeoIndex'], 0),
    ('dct:spatial / dct:identifier', 'shared', 'Code géographique', 'Code du département, code INSEE de la commune, etc.', NULL, false, 'xsd:string', false, NULL, NULL, NULL, true, false, false, NULL, 1),
    ('dct:spatial / skos:prefLabel', 'shared', 'Libellé', NULL, NULL, false, 'rdf:langString', false, NULL, NULL, NULL, true, true, false, NULL, 2),
    ('dct:spatial / dcat:bbox', 'shared', 'Rectangle d''emprise', 'Rectangle d''emprise (BBox), au format textuel WKT.', NULL, false, 'gsp:wktLiteral', false, NULL, NULL, NULL, false, false, false, NULL, 3),
    ('dct:spatial / dcat:centroid', 'shared', 'Centroïde', 'Localisant du centre géographique des données, au format textuel WKT.', NULL, false, 'gsp:wktLiteral', false, NULL, NULL, NULL, false, false, false, NULL, 4),
    ('dct:spatial / locn:geometry', 'shared', 'Géométrie', 'Emprise géométrique, au format textuel WKT.', NULL, false, 'gsp:wktLiteral', false, NULL, NULL, NULL, false, false, false, NULL, 5),
    ('dct:temporal', 'shared', 'Couverture temporelle', NULL, NULL, true, NULL, false, NULL, NULL, NULL, true, false, false, NULL, 10),
    ('dct:temporal / dcat:startDate', 'shared', 'Date de début', NULL, NULL, false, 'xsd:date', false, NULL, NULL, '0000-00-00', false, false, false, NULL, 0),
    ('dct:temporal / dcat:endDate', 'shared', 'Date de fin', NULL, NULL, false, 'xsd:date', false, NULL, NULL, '0000-00-00', false, false, false, NULL, 1),
    ('dct:created', 'shared', 'Date de création', NULL, NULL, false, 'xsd:date', false, NULL, NULL, '0000-00-00', false, false, false, NULL, 11),
    ('dct:modified', 'shared', 'Date de dernière modification', NULL, NULL, false, 'xsd:date', false, NULL, NULL, '0000-00-00', false, false, false, NULL, 12),
    ('dct:issued', 'shared', 'Date de publication', NULL, NULL, false, 'xsd:date', false, NULL, NULL, '0000-00-00', false, false, false, NULL, 13),
    ('dct:accrualPeriodicity', 'shared', 'Fréquence de mise à jour', NULL, 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://publications.europa.eu/resource/authority/frequency'], 14),
    ('dct:provenance', 'shared', 'Généalogie', NULL, NULL, true, NULL, false, NULL, NULL, NULL, true, false, false, NULL, 20),
    ('dct:provenance / rdfs:label', 'shared', 'Texte', NULL, NULL, false, 'rdf:langString', true, 20, NULL, NULL, true, true, false, NULL, 0),
    ('adms:versionNotes', 'shared', 'Note de version', 'Différences entre la version courante des données et les versions antérieures.', NULL, false, 'rdf:langString', true, NULL, NULL, NULL, true, true, false, NULL, 21),
    ('dct:conformsTo', 'shared', 'Conforme à', 'Standard, schéma, référentiel...', NULL, true, NULL, false, NULL, NULL, NULL, true, false, false, NULL, 22),
    ('dct:conformsTo / skos:inScheme', 'shared', 'Registre', NULL, 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://snum.scenari-community.org/Metadata/Vocabulaire/#StandardsRegister'], 0),
    ('dct:conformsTo / dct:identifier', 'shared', 'Identifiant', 'Identifiant du standard, s''il y a lieu. Pour un système de coordonnées géographiques, il s''agit du code EPSG.', NULL, false, 'xsd:string', false, NULL, NULL, NULL, true, false, false, NULL, 1),
    ('dct:conformsTo / dct:title', 'shared', 'Libellé', 'Libellé explicite du standard.', NULL, false, 'rdf:langString', false, NULL, NULL, NULL, true, true, false, NULL, 2),
    ('dct:conformsTo / owl:versionInfo', 'shared', 'Version', 'Numéro ou code de la version du standard à laquelle se conforment les données.', NULL, false, 'xsd:string', false, NULL, NULL, NULL, false, false, false, NULL, 3),
    ('dct:conformsTo / dct:description', 'shared', 'Description', 'Description sommaire de l''objet du standard.', NULL, false, 'rdf:langString', true, NULL, NULL, NULL, true, true, false, NULL, 4),
    ('dct:conformsTo / dct:issued', 'shared', 'Date de publication', 'Date de publication du standard.', NULL, false, 'xsd:date', false, NULL, NULL, '0000-00-00', false, false, false, NULL, 5),
    ('dct:conformsTo / dct:modified', 'shared', 'Date de modification', 'Date de la dernière modification du standard.', NULL, false, 'xsd:date', false, NULL, NULL, '0000-00-00', false, false, false, NULL, 6),
    ('dct:conformsTo / dct:created', 'shared', 'Date de création', 'Date de création du standard.', NULL, false, 'xsd:date', false, NULL, NULL, '0000-00-00', false, false, false, NULL, 7),
    ('dct:conformsTo / foaf:page', 'shared', 'Page internet', 'Chemin d''accès au standard ou URL d''une page contenant des informations sur le standard.', 'url', false, NULL, false, NULL, NULL, NULL, true, false, false, NULL, 8),
    ('dct:conformsTo / dct:type', 'shared', 'Type de standard', NULL, 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, 9),
    ('dcat:spatialResolutionInMeters', 'shared', 'Résolution spatiale en mètres', 'Plus petite distance significative dans le contexte du jeu de données, exprimée en mètres.', NULL, false, 'xsd:decimal', false, NULL, NULL, NULL, false, false, false, NULL, 24),
    ('rdfs:comment', 'shared', 'Commentaire sur la résolution spatiale', NULL, NULL, false, 'rdf:langString', true, NULL, NULL, NULL, true, false, false, NULL, 25),
    ('dcat:temporalResolution', 'shared', 'Résolution temporelle', NULL, NULL, false, 'xsd:duration', false, NULL, NULL, NULL, true, false, false, NULL, 26),
    ('dct:accessRights', 'shared', 'Conditions d''accès', NULL, 'url', false, NULL, false, NULL, NULL, NULL, true, false, false, ARRAY['http://inspire.ec.europa.eu/metadata-codelist/LimitationsOnPublicAccess','http://publications.europa.eu/resource/authority/access-right','http://snum.scenari-community.org/Metadata/Vocabulaire/#CrpaAccessLimitations'], 30),
    ('dct:accessRights / rdfs:label', 'shared', 'Mention', NULL, NULL, false, 'rdf:langString', true, 4, NULL, NULL, true, true, false, NULL, 1),
    ('dcat:contactPoint', 'shared', 'Point de contact', NULL, NULL, true, NULL, false, NULL, NULL, NULL, true, false, false, NULL, 40),
    ('dcat:contactPoint / vcard:fn', 'shared', 'Nom', NULL, NULL, false, 'xsd:string', false, NULL, NULL, NULL, false, false, false, NULL, 1),
    ('dcat:contactPoint / vcard:hasEmail', 'shared', 'Courriel', NULL, 'email', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, 2),
    ('dcat:contactPoint / vcard:hasTelephone', 'shared', 'Téléphone', NULL, 'phone', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, 3),
    ('dcat:contactPoint / vcard:hasURL', 'shared', 'Site internet', NULL, 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, 4),
    ('dcat:contactPoint / vcard:organization-name', 'shared', 'Organisme', 'Le cas échéant, organisation dont le point de contact fait partie.', NULL, false, 'xsd:string', false, NULL, NULL, NULL, false, false, false, NULL, 5),
    ('dct:publisher', 'shared', 'Éditeur', 'Organisme ou personne qui assure la publication des données.', NULL, true, NULL, false, NULL, NULL, NULL, false, false, false, NULL, 41),
    ('dct:publisher / foaf:name', 'shared', 'Nom', NULL, NULL, false, 'xsd:string', false, NULL, NULL, NULL, false, false, false, NULL, 0),
    ('dct:publisher / dct:type', 'shared', 'Type', NULL, 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://purl.org/adms/publishertype/1.0'], 1),
    ('dct:publisher / foaf:mbox', 'shared', 'Courriel', NULL, 'email', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, 2),
    ('dct:publisher / foaf:phone', 'shared', 'Téléphone', NULL, 'phone', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, 3),
    ('dct:publisher / foaf:workplaceHomepage', 'shared', 'Site internet', NULL, 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, 4),
    ('dct:creator', 'shared', 'Auteur', 'Principal responsable de la production des données.', NULL, true, NULL, false, NULL, NULL, NULL, false, false, false, NULL, 42),
    ('dct:creator / foaf:name', 'shared', 'Nom', NULL, NULL, false, 'xsd:string', false, NULL, NULL, NULL, false, false, false, NULL, 0),
    ('dct:creator / dct:type', 'shared', 'Type', NULL, 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://purl.org/adms/publishertype/1.0'], 1),
    ('dct:creator / foaf:mbox', 'shared', 'Courriel', NULL, 'email', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, 2),
    ('dct:creator / foaf:phone', 'shared', 'Téléphone', NULL, 'phone', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, 3),
    ('dct:creator / foaf:workplaceHomepage', 'shared', 'Site internet', NULL, 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, 4),
    ('dct:rightsHolder', 'shared', 'Détenteur de droits', 'Organisme ou personne qui détient des droits sur les données.', NULL, true, NULL, false, NULL, NULL, NULL, true, false, false, NULL, 43),
    ('dct:rightsHolder / foaf:name', 'shared', 'Nom', NULL, NULL, false, 'xsd:string', false, NULL, NULL, NULL, false, false, false, NULL, 0),
    ('dct:rightsHolder / dct:type', 'shared', 'Type', NULL, 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://purl.org/adms/publishertype/1.0'], 1),
    ('dct:rightsHolder / foaf:mbox', 'shared', 'Courriel', NULL, 'email', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, 2),
    ('dct:rightsHolder / foaf:phone', 'shared', 'Téléphone', NULL, 'phone', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, 3),
    ('dct:rightsHolder / foaf:workplaceHomepage', 'shared', 'Site internet', NULL, 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, 4),
    ('geodcat:custodian', 'shared', 'Gestionnaire', 'Organisme ou personne qui assume la maintenance des données.', NULL, true, NULL, false, NULL, NULL, NULL, true, false, false, NULL, 44),
    ('geodcat:custodian / foaf:name', 'shared', 'Nom', NULL, NULL, false, 'xsd:string', false, NULL, NULL, NULL, false, false, false, NULL, 0),
    ('geodcat:custodian / dct:type', 'shared', 'Type', NULL, 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://purl.org/adms/publishertype/1.0'], 1),
    ('geodcat:custodian / foaf:mbox', 'shared', 'Courriel', NULL, 'email', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, 2),
    ('geodcat:custodian / foaf:phone', 'shared', 'Téléphone', NULL, 'phone', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, 3),
    ('geodcat:custodian / foaf:workplaceHomepage', 'shared', 'Site internet', NULL, 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, 4),
    ('geodcat:distributor', 'shared', 'Distributeur', 'Organisme ou personne qui assure la distribution des données.', NULL, true, NULL, false, NULL, NULL, NULL, true, false, false, NULL, 45),
    ('geodcat:distributor / foaf:name', 'shared', 'Nom', NULL, NULL, false, 'xsd:string', false, NULL, NULL, NULL, false, false, false, NULL, 0),
    ('geodcat:distributor / dct:type', 'shared', 'Type', NULL, 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://purl.org/adms/publishertype/1.0'], 1),
    ('geodcat:distributor / foaf:mbox', 'shared', 'Courriel', NULL, 'email', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, 2),
    ('geodcat:distributor / foaf:phone', 'shared', 'Téléphone', NULL, 'phone', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, 3),
    ('geodcat:distributor / foaf:workplaceHomepage', 'shared', 'Site internet', NULL, 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, 4),
    ('geodcat:originator', 'shared', 'Commanditaire', 'Organisme ou personne qui est à l''origine de la création des données.', NULL, true, NULL, false, NULL, NULL, NULL, true, false, false, NULL, 46),
    ('geodcat:originator / foaf:name', 'shared', 'Nom', NULL, NULL, false, 'xsd:string', false, NULL, NULL, NULL, false, false, false, NULL, 0),
    ('geodcat:originator / dct:type', 'shared', 'Type', NULL, 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://purl.org/adms/publishertype/1.0'], 1),
    ('geodcat:originator / foaf:mbox', 'shared', 'Courriel', NULL, 'email', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, 2),
    ('geodcat:originator / foaf:phone', 'shared', 'Téléphone', NULL, 'phone', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, 3),
    ('geodcat:originator / foaf:workplaceHomepage', 'shared', 'Site internet', NULL, 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, 4),
    ('geodcat:principalInvestigator', 'shared', 'Maître d''œuvre', 'Organisme ou personne chargée du recueil des informations.', NULL, true, NULL, false, NULL, NULL, NULL, true, false, false, NULL, 47),
    ('geodcat:principalInvestigator / foaf:name', 'shared', 'Nom', NULL, NULL, false, 'xsd:string', false, NULL, NULL, NULL, false, false, false, NULL, 0),
    ('geodcat:principalInvestigator / dct:type', 'shared', 'Type', NULL, 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://purl.org/adms/publishertype/1.0'], 1),
    ('geodcat:principalInvestigator / foaf:mbox', 'shared', 'Courriel', NULL, 'email', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, 2),
    ('geodcat:principalInvestigator / foaf:phone', 'shared', 'Téléphone', NULL, 'phone', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, 3),
    ('geodcat:principalInvestigator / foaf:workplaceHomepage', 'shared', 'Site internet', NULL, 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, 4),
    ('geodcat:processor', 'shared', 'Intégrateur', 'Organisation ou personne qui a retraité les données.', NULL, true, NULL, false, NULL, NULL, NULL, true, false, false, NULL, 48),
    ('geodcat:processor / foaf:name', 'shared', 'Nom', NULL, NULL, false, 'xsd:string', false, NULL, NULL, NULL, false, false, false, NULL, 0),
    ('geodcat:processor / dct:type', 'shared', 'Type', NULL, 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://purl.org/adms/publishertype/1.0'], 1),
    ('geodcat:processor / foaf:mbox', 'shared', 'Courriel', NULL, 'email', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, 2),
    ('geodcat:processor / foaf:phone', 'shared', 'Téléphone', NULL, 'phone', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, 3),
    ('geodcat:processor / foaf:workplaceHomepage', 'shared', 'Site internet', NULL, 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, 4),
    ('geodcat:resourceProvider', 'shared', 'Fournisseur de la ressource', 'Organisme ou personne qui diffuse les données, soit directement soit par l''intermédiaire d''un distributeur.', NULL, true, NULL, false, NULL, NULL, NULL, true, false, false, NULL, 49),
    ('geodcat:resourceProvider / foaf:name', 'shared', 'Nom', NULL, NULL, false, 'xsd:string', false, NULL, NULL, NULL, false, false, false, NULL, 0),
    ('geodcat:resourceProvider / dct:type', 'shared', 'Type', NULL, 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://purl.org/adms/publishertype/1.0'], 1),
    ('geodcat:resourceProvider / foaf:mbox', 'shared', 'Courriel', NULL, 'email', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, 2),
    ('geodcat:resourceProvider / foaf:phone', 'shared', 'Téléphone', NULL, 'phone', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, 3),
    ('geodcat:resourceProvider / foaf:workplaceHomepage', 'shared', 'Site internet', NULL, 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, 4),
    ('geodcat:user', 'shared', 'Utilisateur', 'Organisme ou personne qui utilise les données.', NULL, true, NULL, false, NULL, NULL, NULL, true, false, false, NULL, 50),
    ('geodcat:user / foaf:name', 'shared', 'Nom', NULL, NULL, false, 'xsd:string', false, NULL, NULL, NULL, false, false, false, NULL, 0),
    ('geodcat:user / dct:type', 'shared', 'Type', NULL, 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://purl.org/adms/publishertype/1.0'], 1),
    ('geodcat:user / foaf:mbox', 'shared', 'Courriel', NULL, 'email', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, 2),
    ('geodcat:user / foaf:phone', 'shared', 'Téléphone', NULL, 'phone', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, 3),
    ('geodcat:user / foaf:workplaceHomepage', 'shared', 'Site internet', NULL, 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, 4),
    ('prov:qualifiedAttribution', 'shared', 'Partie prenante', 'Entité ou personne intervenant dans le processus de création, de diffusion ou de maintenance de la donnée.', NULL, true, NULL, false, NULL, NULL, NULL, true, false, false, NULL, 51),
    ('prov:qualifiedAttribution / prov:agent', 'shared', 'Entité', NULL, NULL, true, NULL, false, NULL, NULL, NULL, true, false, false, NULL, 0),
    ('prov:qualifiedAttribution / prov:agent / foaf:name', 'shared', 'Nom', NULL, NULL, false, 'xsd:string', false, NULL, NULL, NULL, false, false, false, NULL, 0),
    ('prov:qualifiedAttribution / prov:agent / dct:type', 'shared', 'Type', NULL, 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://purl.org/adms/publishertype/1.0'], 1),
    ('prov:qualifiedAttribution / prov:agent / foaf:mbox', 'shared', 'Courriel', NULL, 'email', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, 2),
    ('prov:qualifiedAttribution / prov:agent / foaf:phone', 'shared', 'Téléphone', NULL, 'phone', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, 3),
    ('prov:qualifiedAttribution / prov:agent / foaf:workplaceHomepage', 'shared', 'Site internet', NULL, 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, 4),
    ('prov:qualifiedAttribution / dcat:hadRole', 'shared', 'Rôle', NULL, 'url', false, NULL, false, NULL, NULL, NULL, true, false, false, NULL, 1),
    ('dcat:distribution', 'shared', 'Distribution', NULL, NULL, true, NULL, false, NULL, NULL, NULL, true, false, false, NULL, 59),
    ('dcat:distribution / dcat:accessURL', 'shared', 'URL d''accès', NULL, 'url', false, NULL, false, NULL, NULL, NULL, true, false, false, NULL, 1),
    ('dcat:distribution / dct:issued', 'shared', 'Date de publication', NULL, NULL, false, 'xsd:date', false, NULL, NULL, '0000-00-00', false, false, false, NULL, 2),
    ('dcat:distribution / dct:rights', 'shared', 'Propriété intellectuelle', NULL, NULL, true, NULL, false, NULL, NULL, NULL, false, false, false, NULL, 3),
    ('dcat:distribution / dct:rights / rdfs:label', 'shared', 'Mention', NULL, NULL, false, 'rdf:langString', true, 4, NULL, NULL, true, true, false, NULL, 1),
    ('dcat:distribution / dct:license', 'shared', 'Licence', NULL, 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, ARRAY['http://snum.scenari-community.org/Metadata/Vocabulaire/#CrpaAuthorizedLicense'], 4),
    ('dcat:distribution / dct:license / dct:type', 'shared', 'Type', NULL, 'url', false, NULL, false, NULL, NULL, NULL, true, false, false, ARRAY['http://purl.org/adms/licencetype/1.1'], 1),
    ('dcat:distribution / dct:license / rdfs:label', 'shared', 'Termes', NULL, NULL, false, 'rdf:langString', true, NULL, NULL, NULL, true, true, false, NULL, 2),
    ('dcat:landingPage', 'shared', 'Page internet', 'URL de la fiche de métadonnées sur internet.', 'url', false, NULL, false, NULL, NULL, NULL, true, false, false, NULL, 60),
    ('foaf:page', 'shared', 'Ressource associée', 'Chemin d''une page internet ou d''un document en rapport avec les données.', 'url', false, NULL, false, NULL, NULL, NULL, true, false, false, NULL, 61),
    ('dct:language', 'shared', 'Langue des données', NULL, 'url', false, NULL, false, NULL, NULL, NULL, true, false, false, ARRAY['http://publications.europa.eu/resource/authority/language'], 80),
    ('snum:relevanceScore', 'shared', 'Score', 'plus le score est élevé plus la donnée est mise en avant dans les résultats de recherche.', NULL, false, 'xsd:integer', false, NULL, NULL, NULL, false, false, false, NULL, 81),
    ('dct:type', 'shared', 'Type de jeu de données', NULL, 'url', false, NULL, false, NULL, NULL, NULL, false, false, false, NULL, 82),
    ('dct:identifier', 'shared', 'Identifiant interne', NULL, NULL, false, 'xsd:string', false, NULL, NULL, NULL, false, false, false, NULL, 83),
    ('adms:identifier', 'shared', 'Autre identifiant', NULL, 'url', false, NULL, false, NULL, NULL, NULL, true, false, false, NULL, 84) ;


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
        "snum:isExternal": True,
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
				'[{"snum:isExternal": true}]'::jsonb,
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
                ('Donnée externe', 'dct:spatial', NULL),
                ('Donnée externe', 'dct:spatial / dct:identifier', NULL),
                ('Donnée externe', 'dct:spatial / skos:inScheme', NULL),
                ('Donnée externe', 'dct:spatial / skos:prefLabel', NULL),
                ('Donnée externe', 'dct:subject', NULL),
                ('Donnée externe', 'foaf:page', NULL),
                ('Donnée externe', 'owl:versionInfo', NULL),
                ('Donnée externe', 'snum:isExternal', True)
			) AS t (tpl_label, shrcat_path, unilang)
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

