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
   1.3 - ASSOCIATION DES CATEGORIES AUX MODELES
   1.4 - IMPORT DE MODELES PRE-CONFIGURES */


------ 1.1 - TABLE DE CATEGORIES ------

-- Type: z_metadata.meta_widget_type

CREATE TYPE z_metadata.meta_widget_type AS ENUM (
    'QLineEdit', 'QTextEdit', 'QDateEdit', 'QDateTimeEdit', 'QCheckBox', 'QComboBox'
    ) ;
    
COMMENT ON TYPE z_metadata.meta_widget_type IS 'Métadonnées. Types de widgets de saisie supportés par le plugin QGIS de gestion des métadonnées.' ;


--Table: z_metadata.meta_categorie

CREATE TABLE z_metadata.meta_categorie (
    path text NOT NULL DEFAULT format('<urn:uuid:%s>', gen_random_uuid()),
	origin text NOT NULL DEFAULT 'local',
    cat_label text NOT NULL,
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
COMMENT ON COLUMN z_metadata.meta_categorie.origin IS 'Origine de la catégorie : ''shared'' pour une catégorie commune, ''local'' pour une catégorie locale supplémentaire.' ;
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


-- Table: z_metadata.meta_shared_categorie

CREATE TABLE z_metadata.meta_shared_categorie 
    PARTITION OF z_metadata.meta_categorie (
        CONSTRAINT meta_shared_categorie_pkey PRIMARY KEY (path)
    )
    FOR VALUES IN ('shared') ;
    
COMMENT ON TABLE z_metadata.meta_shared_categorie IS 'Métadonnées. Catégories de métadonnées communes.' ;

COMMENT ON COLUMN z_metadata.meta_shared_categorie.path IS 'Chemin SPARQL de la catégorie (identifiant unique).' ;
COMMENT ON COLUMN z_metadata.meta_shared_categorie.origin IS 'Origine de la catégorie. Toujours ''shared''.' ;
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

-- la table est marquée comme table de configuration de l'extension
SELECT pg_extension_config_dump('z_metadata.meta_shared_categorie'::regclass, '') ;

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
        CONSTRAINT meta_local_categorie_path_check CHECK (path ~ '^[<]urn[:]uuid[:][0-9a-z-]{36}[>]$'),
        CONSTRAINT meta_local_categorie_widget_check CHECK (NOT widget_type = 'QComboBox')
    )
    FOR VALUES IN ('local') ;
    
COMMENT ON TABLE z_metadata.meta_local_categorie IS 'Métadonnées. Catégories de métadonnées supplémentaires (ajouts locaux).' ;

COMMENT ON COLUMN z_metadata.meta_local_categorie.path IS 'Chemin SPARQL de la catégorie (identifiant unique). CE CHAMP EST GENERE AUTOMATIQUEMENT, NE PAS MODIFIER MANUELLEMENT.' ;
COMMENT ON COLUMN z_metadata.meta_local_categorie.origin IS 'Origine de la catégorie. Toujours ''local''.' ;
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


------ 1.2 - TABLE DES MODELES ------

-- Table: z_metadata.meta_template

CREATE TABLE z_metadata.meta_template (
    tpl_id serial PRIMARY KEY,
    tpl_label text NOT NULL,
	sql_filter text,
    md_conditions jsonb,
    priority int,
    CONSTRAINT meta_template_tpl_label_uni UNIQUE (tpl_label)
    ) ;
    
COMMENT ON TABLE z_metadata.meta_template IS 'Métadonnées. Modèles de formulaires définis pour le plugin QGIS.' ;

COMMENT ON COLUMN z_metadata.meta_template.tpl_id IS 'Identifiant unique du modèle.' ;
COMMENT ON COLUMN z_metadata.meta_template.tpl_label IS 'Nom du modèle.' ;
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

-- la table et la séquence sont marquées comme tables de configuration de l'extension
SELECT pg_extension_config_dump('z_metadata.meta_template'::regclass, '') ;
SELECT pg_extension_config_dump('z_metadata.meta_template_tpl_id_seq'::regclass, '') ;


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


---- 1.3 - ASSOCIATION DES CATEGORIES AUX MODELES ------

-- Table z_metadata.meta_template_categories

CREATE TABLE z_metadata.meta_template_categories (
    tplcat_id serial PRIMARY KEY,
    tpl_id integer NOT NULL,
    shrcat_path text,
    loccat_path text,
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
    CONSTRAINT meta_template_categories_tpl_cat_uni UNIQUE (tpl_id, shrcat_path, loccat_path),
    CONSTRAINT meta_template_categories_tpl_id_fkey FOREIGN KEY (tpl_id)
        REFERENCES z_metadata.meta_template (tpl_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT meta_template_categories_shrcat_path_fkey FOREIGN KEY (shrcat_path)
        REFERENCES z_metadata.meta_shared_categorie (path)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT meta_template_categories_loccat_path_fkey FOREIGN KEY (loccat_path)
        REFERENCES z_metadata.meta_local_categorie (path)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT meta_template_categories_path_check CHECK (
        shrcat_path IS NULL OR loccat_path IS NULL
        AND shrcat_path IS NOT NULL OR loccat_path IS NOT NULL
        ),
    CONSTRAINT meta_template_categories_row_span_check CHECK (row_span BETWEEN 1 AND 99)
    ) ;

COMMENT ON TABLE z_metadata.meta_template_categories IS 'Métadonnées. Désignation des catégories utilisées par chaque modèle de formulaire.
Les autres champs permettent de personnaliser la présentation des catégories pour le modèle considéré. S''ils ne sont pas renseignés, les valeurs saisies dans meta_categorie seront utilisées. À défaut, le plugin s''appuyera sur le schéma des catégories communes (évidemment pour les catégories communes uniquement).' ;

COMMENT ON COLUMN z_metadata.meta_template_categories.tplcat_id IS 'Identifiant unique.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories.tpl_id IS 'Identifiant du modèle de formulaire.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories.shrcat_path IS 'Chemin SPARQL / identifiant de la catégorie de métadonnées (si catégorie commune).' ;
COMMENT ON COLUMN z_metadata.meta_template_categories.loccat_path IS 'Chemin SPARQL / identifiant de la catégorie de métadonnées (si catégorie supplémentaire locale).' ;
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
        coalesce(tc.shrcat_path, tc.loccat_path) AS path,
        c.origin,
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
                ON coalesce(tc.shrcat_path, tc.loccat_path) = c.path
            LEFT JOIN z_metadata.meta_template AS t
                ON tc.tpl_id = t.tpl_id
    ) ;

COMMENT ON VIEW z_metadata.meta_template_categories_full IS 'Métadonnées. Description complète des modèles de formulaire (rassemble les informations de meta_categorie et meta_template_categories).' ;

COMMENT ON COLUMN z_metadata.meta_template_categories_full.tplcat_id IS 'Identifiant unique.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories_full.tpl_id IS 'Identifiant du modèle de formulaire.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories_full.tpl_label IS 'Nom du modèle.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories_full.path IS 'Chemin SPARQL / identifiant de la catégorie.' ;
COMMENT ON COLUMN z_metadata.meta_template_categories_full.origin IS 'Origine de la catégorie : ''shared'' pour une catégorie commune, ''local'' pour une catégorie locale supplémentaire.' ;
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


------ 1.4 - IMPORT DE MODELES PRE-CONFIGURES -------

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
pour effet de le réinitialiser (par suppression / création,
donc l'identifiant numérique sera modifié).

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
			(nextval('z_metadata.meta_template_tpl_id_seq'::regclass), 'Donnée externe', '$1 ~ ANY(ARRAY[''^r_'', ''^e_''])', '{"c1": {"snum:isExternal": "True"}}'::jsonb, 10),
			(nextval('z_metadata.meta_template_tpl_id_seq'::regclass), 'Basique', NULL, NULL, 0)
	    ) AS t (tpl_id, tpl_label, sql_filter, md_conditions, priority)
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
			(tpl_id, tpl_label, sql_filter, md_conditions, priority)
			VALUES (tpl.tpl_id, tpl.tpl_label, tpl.sql_filter, tpl.md_conditions, tpl.priority) ;
		
		-- boucle sur les associations modèles-catégories :
		FOR tplcat IN SELECT * FROM (
			VALUES
				('Basique', 'dct:title', NULL),
				('Basique', 'dct:description', NULL),
				('Basique', 'dct:modified', NULL),
				('Basique', 'dct:temporal', NULL),
				('Basique', 'dct:temporal / dcat:startDate', NULL),
				('Basique', 'dct:temporal / dcat:endDate', NULL),
				('Donnée externe', 'dct:accessRights', NULL),
				('Donnée externe', 'dct:accessRights / rdfs:label', NULL),
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
				('Donnée externe', 'snum:isExternal', True),
				('Donnée externe', 'dcat:distribution', NULL),
				('Donnée externe', 'dcat:distribution / dct:accessURL', NULL),
				('Donnée externe', 'dcat:distribution / dct:issued', NULL),
				('Donnée externe', 'dcat:distribution / dct:license', NULL),
				('Donnée externe', 'dcat:distribution / dct:license / rdfs:label', NULL),
				('Donnée externe', 'dcat:keyword', NULL),
				('Donnée externe', 'dcat:landingPage', NULL),
				('Donnée externe', 'dcat:theme', NULL)	
			) AS t (tpl_label, shrcat_path, default_value)
			WHERE t.tpl_label = tpl.tpl_label
		LOOP
		
			INSERT INTO z_metadata.meta_template_categories
				(tpl_id, shrcat_path)
				VALUES (tpl.tpl_id, tplcat.shrcat_path) ;
		
		END LOOP ;
	
	END LOOP ;

	RETURN ;
	
END
$BODY$ ;

COMMENT ON FUNCTION z_metadata.meta_import_sample_template(text) IS 'Importe l''un des modèles de formulaires pré-configurés (ou tous si l''argument n''est pas renseigné).' ;

-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

