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
-- - Table: z_metadata.meta_categorie
-- - Table: z_metadata.meta_shared_categorie
-- - Table: z_metadata.meta_local_categorie
-- - Table: z_metadata.meta_template
-- - Table: z_metadata.meta_template_categories
-- - View: z_metadata.meta_template_categories_full
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


-- Type: z_metadata.meta_widget_type

CREATE TYPE z_metadata.meta_widget_type AS ENUM (
    'QLineEdit', 'QTextEdit', 'QDateEdit', 'QDateTimeEdit', 'QCheckBox', 'QComboBox'
    ) ;
    
COMMENT ON TYPE z_metadata.meta_widget_type IS 'Métadonnées. Types de widgets de saisie supportés par le plugin QGIS de gestion des métadonnées.' ;


--Table: z_metadata.meta_categorie

CREATE TABLE z_metadata.meta_categorie (
    cat_id serial NOT NULL,
    origin text NOT NULL DEFAULT 'local',
    path text NOT NULL DEFAULT format('<urn:uuid:%s>', gen_random_uuid()),
    cat_label text,
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

COMMENT ON COLUMN z_metadata.meta_categorie.cat_id IS 'Identifiant unique de la catégorie.' ;
COMMENT ON COLUMN z_metadata.meta_categorie.origin IS 'Origine de la catégorie : ''shared'' pour une catégorie commune, ''local'' pour une catégorie locale supplémentaire.' ;
COMMENT ON COLUMN z_metadata.meta_categorie.path IS 'Chemin SPARQL de la catégorie. CE CHAMP EST GENERE AUTOMATIQUEMENT, NE PAS MODIFIER MANUELLEMENT.' ;
COMMENT ON COLUMN z_metadata.meta_categorie.cat_label IS 'Libellé de la catégorie.' ;
COMMENT ON COLUMN z_metadata.meta_categorie.widget_type IS 'Type de widget de saisie à utiliser.' ;
COMMENT ON COLUMN z_metadata.meta_categorie.row_span IS 'Nombre de lignes occupées par le widget de saisie, s''il y a lieu. La valeur ne sera considérée que pour un widget QTextEdit.' ;
COMMENT ON COLUMN z_metadata.meta_categorie.help_text IS 'Description de la catégorie. Sera affiché sous la forme d''un texte d''aide dans le formulaire).' ;
COMMENT ON COLUMN z_metadata.meta_categorie.default_value IS 'Valeur par défaut, le cas échéant.' ;
COMMENT ON COLUMN z_metadata.meta_categorie.placeholder_text IS 'Valeur fictive pré-affichée en tant qu''exemple dans le widget de saisie, s''il y a lieu.' ;
COMMENT ON COLUMN z_metadata.meta_categorie.input_mask IS 'Masque de saisie, s''il y a lieu.' ;
COMMENT ON COLUMN z_metadata.meta_categorie.multiple_values IS 'True si la catégorie admet plusieurs valeurs.' ;
COMMENT ON COLUMN z_metadata.meta_categorie.is_mandatory IS 'True si une valeur doit obligatoirement être saisie pour cette catégorie.' ;
COMMENT ON COLUMN z_metadata.meta_categorie.order_key IS 'Ordre d''apparence de la catégorie dans le formulaire. Les plus petits numéros sont affichés en premier.' ;

-- la séquence est marquée comme "table" de configuration de l'extension
SELECT pg_extension_config_dump('z_metadata.meta_categorie_cat_id_seq'::regclass, '') ;


-- Table: z_metadata.meta_shared_categorie

CREATE TABLE z_metadata.meta_shared_categorie 
    PARTITION OF z_metadata.meta_categorie (
        CONSTRAINT meta_shared_categorie_pkey PRIMARY KEY (cat_id),
        CONSTRAINT meta_shared_categorie_path_uni UNIQUE (path)
    )
    FOR VALUES IN ('shared') ;
    
COMMENT ON TABLE z_metadata.meta_shared_categorie IS 'Métadonnées. Catégories de métadonnées communes.' ;

COMMENT ON COLUMN z_metadata.meta_shared_categorie.cat_id IS 'Identifiant unique de la catégorie.' ;
COMMENT ON COLUMN z_metadata.meta_shared_categorie.origin IS 'Origine de la catégorie. Toujours ''shared''.' ;
COMMENT ON COLUMN z_metadata.meta_shared_categorie.path IS 'Chemin SPARQL de la catégorie.' ;
COMMENT ON COLUMN z_metadata.meta_shared_categorie.cat_label IS 'Libellé de la catégorie.' ;
COMMENT ON COLUMN z_metadata.meta_shared_categorie.widget_type IS 'Type de widget de saisie à utiliser.' ;
COMMENT ON COLUMN z_metadata.meta_shared_categorie.row_span IS 'Nombre de lignes occupées par le widget de saisie, s''il y a lieu. La valeur ne sera considérée que pour un widget QTextEdit.' ;
COMMENT ON COLUMN z_metadata.meta_shared_categorie.help_text IS 'Description de la catégorie. Sera affiché sous la forme d''un texte d''aide dans le formulaire).' ;
COMMENT ON COLUMN z_metadata.meta_shared_categorie.default_value IS 'Valeur par défaut, le cas échéant.' ;
COMMENT ON COLUMN z_metadata.meta_shared_categorie.placeholder_text IS 'Valeur fictive pré-affichée en tant qu''exemple dans le widget de saisie, s''il y a lieu.' ;
COMMENT ON COLUMN z_metadata.meta_shared_categorie.input_mask IS 'Masque de saisie, s''il y a lieu.' ;
COMMENT ON COLUMN z_metadata.meta_shared_categorie.multiple_values IS 'True si la catégorie admet plusieurs valeurs. ATTENTION : toute modification sur ce champ sera ignorée par le plugin QGIS.' ;
COMMENT ON COLUMN z_metadata.meta_shared_categorie.is_mandatory IS 'True si une valeur doit obligatoirement être saisie pour cette catégorie. ATTENTION : modifier cette valeur permet de rendre obligatoire une catégorie commune optionnelle, mais pas l''inverse.' ;
COMMENT ON COLUMN z_metadata.meta_shared_categorie.order_key IS 'Ordre d''apparence de la catégorie dans le formulaire. Les plus petits numéros sont affichés en premier.' ;

-- cette table n'est pas une table de configuration de l'extension

-- extraction du schéma SHACL
INSERT INTO z_metadata.meta_categorie (
    origin, path, cat_label, widget_type, row_span,
    help_text, default_value, placeholder_text, input_mask,
    multiple_values, is_mandatory, order_key
    ) VALUES
    ('shared', 'dct:title', 'libellé', 'QLineEdit', NULL, NULL, NULL, NULL, NULL, True, True, 0),
    ('shared', 'dct:description', 'description', 'QTextEdit', 15, NULL, NULL, NULL, NULL, True, True, 1),
    ('shared', 'dct:modified', 'dernière modification', 'QDateTimeEdit', NULL, NULL, NULL, NULL, NULL, False, False, 2),
    ('shared', 'snum:isExternal', 'donnée externe', 'QCheckBox', NULL, NULL, NULL, NULL, NULL, False, False, 3),
    ('shared', 'dcat:theme', 'thème', 'QComboBox', NULL, NULL, NULL, NULL, NULL, True, False, 4),
    ('shared', 'dcat:keyword', 'mots-clé libres', 'QLineEdit', NULL, NULL, NULL, NULL, NULL, True, False, 5),
    ('shared', 'dct:temporal', 'couverture temporelle', NULL, NULL, NULL, NULL, NULL, NULL, True, False, 6),
    ('shared', 'dct:temporal / dcat:startDate', 'date de début', 'QDateEdit', NULL, NULL, NULL, NULL, '0000-00-00', False, False, 0),
    ('shared', 'dct:temporal / dcat:endDate', 'date de fin', 'QDateEdit', NULL, NULL, NULL, NULL, '0000-00-00', False, False, 1),
    ('shared', 'dct:provenance', 'généalogie', NULL, NULL, NULL, NULL, NULL, NULL, True, False, 7),
    ('shared', 'dct:provenance / rdfs:label', 'texte', 'QTextEdit', 20, NULL, NULL, NULL, NULL, True, False, 0),
    ('shared', 'dct:accessRights', 'conditions d''accès', 'QComboBox', NULL, NULL, NULL, NULL, NULL, False, False, 8),
    ('shared', 'dct:accessRights / rdfs:label', 'mention', 'QTextEdit', 4, NULL, NULL, NULL, NULL, True, False, 1),
    ('shared', 'dcat:contactPoint', 'point de contact', NULL, NULL, NULL, NULL, NULL, NULL, True, False, 10),
    ('shared', 'dcat:contactPoint / vcard:fn', 'nom', 'QLineEdit', NULL, NULL, NULL, NULL, NULL, False, False, 1),
    ('shared', 'dcat:contactPoint / vcard:hasEmail', 'mél', 'QLineEdit', NULL, NULL, NULL, NULL, NULL, False, False, 2),
    ('shared', 'dcat:contactPoint / vcard:hasTelephone', 'téléphone', 'QLineEdit', NULL, NULL, NULL, '+33-1-23-45-67-89', NULL, False, False, 3),
    ('shared', 'dcat:contactPoint / vcard:hasURL', 'site internet', 'QLineEdit', NULL, NULL, NULL, NULL, NULL, False, False, 4),
    ('shared', 'dcat:contactPoint / vcard:organization-name', 'organisme', 'QLineEdit', NULL, 'le cas échéant, organisation plus vaste dont le point de contact fait partie', NULL, NULL, NULL, False, False, 5),
    ('shared', 'dct:publisher', 'diffuseur', NULL, NULL, NULL, NULL, NULL, NULL, False, False, 11),
    ('shared', 'dct:publisher / foaf:name', 'nom', 'QLineEdit', NULL, NULL, NULL, NULL, NULL, False, False, 0),
    ('shared', 'dct:publisher / dct:type', 'type', 'QComboBox', NULL, NULL, NULL, NULL, NULL, False, False, 1),
    ('shared', 'dct:publisher / foaf:mbox', 'mél', 'QLineEdit', NULL, NULL, NULL, NULL, NULL, False, False, 2),
    ('shared', 'dct:publisher / foaf:phone', 'téléphone', 'QLineEdit', NULL, NULL, NULL, '+33-1-23-45-67-89', NULL, False, False, 3),
    ('shared', 'dct:publisher / foaf:workplaceHomepage', 'site internet', 'QLineEdit', NULL, NULL, NULL, NULL, NULL, False, False, 4),
    ('shared', 'dcat:distribution', 'distribution', NULL, NULL, NULL, NULL, NULL, NULL, True, False, 20),
    ('shared', 'dcat:distribution / dct:accessURL', 'URL d''accès', 'QLineEdit', NULL, NULL, NULL, NULL, NULL, True, False, 1),
    ('shared', 'dcat:distribution / dct:issued', 'date de publication', 'QDateEdit', NULL, NULL, NULL, NULL, '0000-00-00', False, False, 2),
    ('shared', 'dcat:distribution / dct:rights', 'propriété intellectuelle', NULL, NULL, NULL, NULL, NULL, NULL, False, False, 3),
    ('shared', 'dcat:distribution / dct:rights / rdfs:label', 'mention', 'QTextEdit', 4, NULL, NULL, NULL, NULL, True, False, 1),
    ('shared', 'dcat:distribution / dct:license', 'licence', 'QComboBox', NULL, NULL, NULL, NULL, NULL, False, False, 4),
    ('shared', 'dcat:distribution / dct:license / dct:type', 'type', 'QComboBox', NULL, NULL, NULL, NULL, NULL, True, False, 1),
    ('shared', 'dcat:distribution / dct:license / rdfs:label', 'termes', 'QTextEdit', NULL, NULL, NULL, NULL, NULL, True, False, 2),
    ('shared', 'dcat:landingPage', 'page internet', 'QLineEdit', NULL, NULL, NULL, NULL, NULL, True, False, 30),
    ('shared', 'dct:language', 'langue des données', 'QComboBox', NULL, NULL, 'http://publications.europa.eu/resource/authority/language/FRA', NULL, NULL, True, False, 40),
    ('shared', 'snum:relevanceScore', 'score', 'QLineEdit', NULL, 'plus le score est élevé plus la donnée est mise en avant dans les résultats de recherche', NULL, NULL, NULL, False, False, 50) ;



-- Table: z_metadata.meta_local_categorie

CREATE TABLE z_metadata.meta_local_categorie 
    PARTITION OF z_metadata.meta_categorie (
        CONSTRAINT meta_local_categorie_pkey PRIMARY KEY (cat_id),
        CONSTRAINT meta_local_categorie_path_uni UNIQUE (path),
        CONSTRAINT meta_local_categorie_path_check CHECK (path ~ '^[<]urn[:]uuid[:][0-9a-z-]{36}[>]$'),
        CONSTRAINT meta_local_categorie_widget_check CHECK (NOT widget_type = 'QComboBox')
    )
    FOR VALUES IN ('local') ;
    
COMMENT ON TABLE z_metadata.meta_local_categorie IS 'Métadonnées. Catégories de métadonnées supplémentaires (ajouts locaux).' ;

COMMENT ON COLUMN z_metadata.meta_local_categorie.cat_id IS 'Identifiant unique de la catégorie.' ;
COMMENT ON COLUMN z_metadata.meta_local_categorie.origin IS 'Origine de la catégorie. Toujours ''local''.' ;
COMMENT ON COLUMN z_metadata.meta_local_categorie.path IS 'Chemin SPARQL de la catégorie. CE CHAMP EST GENERE AUTOMATIQUEMENT, NE PAS MODIFIER MANUELLEMENT.' ;
COMMENT ON COLUMN z_metadata.meta_local_categorie.cat_label IS 'Libellé de la catégorie.' ;
COMMENT ON COLUMN z_metadata.meta_local_categorie.widget_type IS 'Type de widget de saisie à utiliser.' ;
COMMENT ON COLUMN z_metadata.meta_local_categorie.row_span IS 'Nombre de lignes occupées par le widget de saisie, s''il y a lieu. La valeur ne sera considérée que pour un widget QTextEdit.' ;
COMMENT ON COLUMN z_metadata.meta_local_categorie.help_text IS 'Description de la catégorie. Sera affiché sous la forme d''un texte d''aide dans le formulaire).' ;
COMMENT ON COLUMN z_metadata.meta_local_categorie.default_value IS 'Valeur par défaut, le cas échéant.' ;
COMMENT ON COLUMN z_metadata.meta_local_categorie.placeholder_text IS 'Valeur fictive pré-affichée en tant qu''exemple dans le widget de saisie, s''il y a lieu.' ;
COMMENT ON COLUMN z_metadata.meta_local_categorie.input_mask IS 'Masque de saisie, s''il y a lieu.' ;
COMMENT ON COLUMN z_metadata.meta_local_categorie.multiple_values IS 'True si la catégorie admet plusieurs valeurs.' ;
COMMENT ON COLUMN z_metadata.meta_local_categorie.is_mandatory IS 'True si une valeur doit obligatoirement être saisie pour cette catégorie.' ;
COMMENT ON COLUMN z_metadata.meta_local_categorie.order_key IS 'Ordre d''apparence de la catégorie dans le formulaire. Les plus petits numéros sont affichés en premier.' ;

-- la table est marquée comme table de configuration de l'extension
SELECT pg_extension_config_dump('z_metadata.meta_local_categorie'::regclass, '') ;


-- Table: z_metadata.meta_template

CREATE TABLE z_metadata.meta_template (
    tpl_id serial PRIMARY KEY,
    tpl_label text NOT NULL,
    schema_prefix text[],
    schema_suffix text[],
    table_prefix text[],
    table_suffix text[],
    conditions jsonb,
    priority int,
    CONSTRAINT meta_template_tpl_label_uni UNIQUE (tpl_label)
    ) ;
    
COMMENT ON TABLE z_metadata.meta_template IS 'Métadonnées. Modèles de formulaires définis pour le plugin QGIS.' ;

COMMENT ON COLUMN z_metadata.meta_template.tpl_id IS 'Identifiant unique du modèle.' ;
COMMENT ON COLUMN z_metadata.meta_template.tpl_label IS 'Nom du modèle.' ;
COMMENT ON COLUMN z_metadata.meta_template.schema_prefix IS 'Liste de préfixes. Si l''un d''eux apparaît au début du nom du schéma, le modèle sera utilisé par défaut.' ;
COMMENT ON COLUMN z_metadata.meta_template.schema_suffix IS 'Liste de suffixes. Si l''un d''eux apparaît à la fin du nom du schéma, le modèle sera utilisé par défaut.' ;
COMMENT ON COLUMN z_metadata.meta_template.table_prefix IS 'Liste de préfixes. Si l''un d''eux apparaît au début du nom de la table/vue, le modèle sera utilisé par défaut.' ;
COMMENT ON COLUMN z_metadata.meta_template.table_suffix IS 'Liste de suffixes. Si l''un d''eux apparaît à la fin du nom de la table/vue, le modèle sera utilisé par défaut.' ;
COMMENT ON COLUMN z_metadata.meta_template.conditions IS 'Ensemble de conditions sur les métadonnées appelant l''usage de ce modèle.
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

-- la table et la séquence sont marquées comme tables de configuration de l'extension
SELECT pg_extension_config_dump('z_metadata.meta_template'::regclass, '') ;
SELECT pg_extension_config_dump('z_metadata.meta_template_tpl_id_seq'::regclass, '') ;


-- Table z_metadata.meta_template_categories

CREATE TABLE z_metadata.meta_template_categories (
    tplcat_id serial PRIMARY KEY,
    tpl_id integer NOT NULL,
    shrcat_id integer,
    loccat_id integer,
    cat_label text,
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
    CONSTRAINT meta_template_categories_tpl_cat_uni UNIQUE (tpl_id, shrcat_id, loccat_id),
    CONSTRAINT meta_template_categories_tpl_id_fkey FOREIGN KEY (tpl_id)
        REFERENCES z_metadata.meta_template (tpl_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT meta_template_categories_shrcat_id_fkey FOREIGN KEY (shrcat_id)
        REFERENCES z_metadata.meta_shared_categorie (cat_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT meta_template_categories_loccat_id_fkey FOREIGN KEY (loccat_id)
        REFERENCES z_metadata.meta_local_categorie (cat_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT meta_template_categories_idcat_check CHECK (
        shrcat_id IS NULL OR loccat_id IS NULL
        AND shrcat_id IS NOT NULL OR loccat_id IS NOT NULL
        ),
    CONSTRAINT meta_template_categories_row_span_check CHECK (row_span BETWEEN 1 AND 99)
    ) ;

COMMENT ON TABLE z_metadata.meta_template_categories IS 'Métadonnées. Désignation des catégories utilisées par chaque modèle de formulaire.
Les autres champs permettent de personnaliser la présentation des catégories pour le modèle considéré. S''ils ne sont pas renseignés, les valeurs saisies dans meta_categorie seront utilisées. À défaut, le plugin s''appuyera sur le schéma des catégories communes (évidemment pour les catégories communes uniquement).' ;

COMMENT ON COLUMN z_metadata.meta_template_categories.tplcat_id IS 'Identifiant unique.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories.tpl_id IS 'Identifiant du modèle de formulaire.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories.shrcat_id IS 'Identifiant de la catégorie de métadonnées (si catégorie commune).' ;
COMMENT ON COLUMN z_metadata.meta_template_categories.loccat_id IS 'Identifiant de la catégorie de métadonnées (si catégorie supplémentaire locale).' ;
COMMENT ON COLUMN z_metadata.meta_template_categories.cat_label IS 'Libellé de la catégorie de métadonnées.
Si présente, cette valeur se substitue pour le modèle considéré à la valeur renseignée dans le champ éponyme de meta_categorie.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories.widget_type IS 'Type de widget de saisie à utiliser.
Si présente, cette valeur se substitue pour le modèle considéré à la valeur renseignée dans le champ éponyme de meta_categorie.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories.row_span IS 'Nombre de lignes occupées par le widget de saisie, s''il y a lieu. La valeur ne sera considérée que pour un widget QTextEdit.
Si présente, cette valeur se substitue pour le modèle considéré à la valeur renseignée dans le champ éponyme de meta_categorie.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories.help_text IS 'Description de la catégorie. Sera affiché sous la forme d''un texte d''aide dans le formulaire).
Si présente, cette valeur se substitue pour le modèle considéré à la valeur renseignée dans le champ éponyme de meta_categorie.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories.default_value IS 'Valeur par défaut, le cas échéant.
Si présente, cette valeur se substitue pour le modèle considéré à la valeur renseignée dans le champ éponyme de meta_categorie.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories.placeholder_text IS 'Valeur fictive pré-affichée en tant qu''exemple dans le widget de saisie, s''il y a lieu.
Si présente, cette valeur se substitue pour le modèle considéré à la valeur renseignée dans le champ éponyme de meta_categorie.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories.input_mask IS 'Masque de saisie, s''il y a lieu.
Si présente, cette valeur se substitue pour le modèle considéré à la valeur renseignée dans le champ éponyme de meta_categorie.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories.multiple_values IS 'True si la catégorie admet plusieurs valeurs.
ATTENTION : pour les catégories communes, les modifications apportées sur ce champs ne seront pas prises en compte.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories.is_mandatory IS 'True si une valeur doit obligatoirement être saisie pour cette catégorie.
ATTENTION : modifier cette valeur permet de rendre obligatoire une catégorie commune optionnelle, mais pas l''inverse.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories.order_key IS 'Ordre d''apparence de la catégorie dans le formulaire. Les plus petits numéros sont affichés en premier.
Si présente, cette valeur se substitue pour le modèle considéré à la valeur renseignée dans le champ éponyme de meta_categorie.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories.read_only IS 'True si la catégorie est en lecture seule' ;

-- la table et la séquence sont marquées comme tables de configuration de l'extension
SELECT pg_extension_config_dump('z_metadata.meta_template_categories'::regclass, '') ;
SELECT pg_extension_config_dump('z_metadata.meta_template_categories_tplcat_id_seq'::regclass, '') ;


-- View: z_metadata.meta_template_categories_full

CREATE VIEW z_metadata.meta_template_categories_full AS (
    SELECT
        tc.tplcat_id,
        tc.tpl_id,
        t.tpl_label,
        coalesce(tc.shrcat_id, tc.loccat_id) AS cat_id,
        c.origin,
        c.path,
        coalesce(tc.cat_label, c.cat_label) AS cat_label,
        coalesce(tc.widget_type, c.widget_type) AS widget_type,
        coalesce(tc.row_span, c.row_span) AS row_span,
        coalesce(tc.help_text, c.help_text) AS help_text,
        coalesce(tc.default_value, c.default_value) AS default_value,
        coalesce(tc.placeholder_text, c.placeholder_text) AS placeholder_text,
        coalesce(tc.input_mask, c.input_mask) AS input_mask,
        coalesce(tc.multiple_values, c.multiple_values) AS multiple_values,
        coalesce(tc.is_mandatory, c.is_mandatory) AS is_mandatory,
        coalesce(tc.order_key, c.order_key) AS order_key,
        tc.read_only AS read_only
        FROM z_metadata.meta_template_categories AS tc
            LEFT JOIN z_metadata.meta_categorie AS c
                ON coalesce(tc.shrcat_id, tc.loccat_id) = c.cat_id
            LEFT JOIN z_metadata.meta_template AS t
                ON tc.tpl_id = t.tpl_id
    ) ;

COMMENT ON VIEW z_metadata.meta_template_categories_full IS 'Métadonnées. Description complète des modèles de formulaire (rassemble les informations de meta_categorie et meta_template_categories).' ;

COMMENT ON COLUMN z_metadata.meta_template_categories_full.tplcat_id IS 'Identifiant unique.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories_full.tpl_id IS 'Identifiant du modèle de formulaire.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories_full.tpl_label IS 'Nom du modèle.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories_full.cat_id IS 'Identifiant unique de la catégorie.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories_full.origin IS 'Origine de la catégorie : ''shared'' pour une catégorie commune, ''local'' pour une catégorie locale supplémentaire.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories_full.path IS 'Chemin SPARQL de la catégorie.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories_full.cat_label IS 'Libellé de la catégorie de métadonnées.
Le cas échéant, cette valeur se substituera pour le modèle considéré à la valeur renseignée dans le schéma des métadonnées communes.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories_full.widget_type IS 'Type de widget de saisie à utiliser.
Le cas échéant, cette valeur se substituera pour le modèle considéré à la valeur renseignée dans le schéma des métadonnées communes.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories_full.row_span IS 'Nombre de lignes occupées par le widget de saisie, s''il y a lieu. La valeur ne sera considérée que pour un widget QTextEdit.
Le cas échéant, cette valeur se substituera pour le modèle considéré à la valeur renseignée dans le schéma des métadonnées communes.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories_full.help_text IS 'Description de la catégorie. Sera affiché sous la forme d''un texte d''aide dans le formulaire).
Le cas échéant, cette valeur se substituera pour le modèle considéré à la valeur renseignée dans le schéma des métadonnées communes.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories_full.default_value IS 'Valeur par défaut, le cas échéant.
Le cas échéant, cette valeur se substituera pour le modèle considéré à la valeur renseignée dans le schéma des métadonnées communes.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories_full.placeholder_text IS 'Valeur fictive pré-affichée en tant qu''exemple dans le widget de saisie, s''il y a lieu.
Le cas échéant, cette valeur se substituera pour le modèle considéré à la valeur renseignée dans le schéma des métadonnées communes.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories_full.input_mask IS 'Masque de saisie, s''il y a lieu.
Le cas échéant, cette valeur se substituera pour le modèle considéré à la valeur renseignée dans le schéma des métadonnées communes.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories_full.multiple_values IS 'True si la catégorie admet plusieurs valeurs.
ATTENTION : pour les catégories communes, les modifications apportées sur ce champs ne seront pas prises en compte.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories_full.is_mandatory IS 'True si une valeur doit obligatoirement être saisie pour cette catégorie.
ATTENTION : modifier cette valeur permet de rendre obligatoire une catégorie commune optionnelle, mais pas l''inverse.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories_full.order_key IS 'Ordre d''apparence de la catégorie dans le formulaire. Les plus petits numéros sont affichés en premier.
Le cas échéant, cette valeur se substituera pour le modèle considéré à la valeur renseignée dans le schéma des métadonnées communes.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories_full.read_only IS 'True si la catégorie est en lecture seule.' ;

-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

