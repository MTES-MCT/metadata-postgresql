\echo Use "ALTER EXTENSION plume_pg UPDATE TO '0.3.1'" to load this file. \quit
-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
--
-- PlumePg - Système de gestion des métadonnées locales, version 0.3.1
-- > Script de mise à jour depuis la version 0.3.0
--
-- Copyright République Française, 2024.
-- Secrétariat général du Ministère de la Transition écologique et
-- de la Cohésion des territoires.
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
-- - View: z_plume.meta_categorie
-- - Function: z_plume.meta_categorie_instead_of_action()
-- - Trigger: meta_categorie_instead_of_action on z_plume.meta_categorie
--
-- objets modifiés par le script :
-- - Table: z_plume.meta_shared_categorie
-- - Table: z_plume.meta_local_categorie
--
-- objets supprimés par le script :
-- -Table: z_plume.meta_categorie
--
-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


--Table: z_plume.meta_categorie

ALTER TABLE z_plume.meta_categorie
    DETACH PARTITION z_plume.meta_shared_categorie ;

ALTER TABLE z_plume.meta_categorie
    DETACH PARTITION z_plume.meta_local_categorie ;

DROP VIEW z_plume.meta_template_categories_full ;
-- sera recréée à l'identique

DROP TABLE z_plume.meta_categorie ;

-- Table: z_plume.meta_shared_categorie

ALTER TABLE z_plume.meta_shared_categorie
    ALTER COLUMN path DROP DEFAULT,
    ALTER COLUMN origin SET DEFAULT 'shared',
    DROP CONSTRAINT meta_categorie_origin_check ;

ALTER TABLE z_plume.meta_shared_categorie
    ADD CONSTRAINT meta_categorie_origin_check CHECK (origin = 'shared') ;

-- Table: z_plume.meta_local_categorie

ALTER TABLE z_plume.meta_local_categorie
    ALTER COLUMN origin SET DEFAULT 'local',
    DROP CONSTRAINT meta_categorie_origin_check ;

ALTER TABLE z_plume.meta_local_categorie
    ADD CONSTRAINT meta_categorie_origin_check CHECK (origin = 'local') ;

-- View: z_plume.meta_categorie

CREATE VIEW z_plume.meta_categorie AS (
    SELECT * FROM z_plume.meta_shared_categorie
    UNION 
    SELECT * FROM z_plume.meta_local_categorie 
    ORDER BY path
    ) ;

GRANT SELECT ON TABLE z_plume.meta_categorie TO public ;

COMMENT ON VIEW z_plume.meta_categorie IS 'Catégories de métadonnées disponibles pour les modèles de formulaires.' ;

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
COMMENT ON COLUMN z_plume.meta_categorie.compute_params IS 'Paramètres des fonctionnalités de calcul, le cas échéant, sous une forme clé-valeur. La clé est le nom du paramètre, la valeur sa valeur. Cette information ne sera considérée que si une méthode de calcul est effectivement disponible pour la catégorie et qu''elle attend un ou plusieurs paramètres.' ;

-- Function: z_plume.meta_categorie_instead_of_action()

CREATE OR REPLACE FUNCTION z_plume.meta_categorie_instead_of_action()
    RETURNS trigger
    LANGUAGE plpgsql
    AS $BODY$
/* Fonction exécutée par le trigger meta_categorie_instead_of_action.

    Elle répercute la commande de l'utilisateur sur la table des 
    métadonnées communes ou la table des métadonnées locales, selon
    la valeur du champ "origin".

*/
BEGIN
    
    IF TG_OP = 'DELETE'
    THEN

        IF OLD.origin = 'shared'
        THEN
            DELETE FROM z_plume.meta_shared_categorie 
                WHERE meta_shared_categorie.path = OLD.path ;
        ELSE
            DELETE FROM z_plume.meta_local_categorie 
                WHERE meta_local_categorie.path = OLD.path ;
        END IF ;

        RETURN OLD ;

    END IF ;
        
    IF TG_OP = 'UPDATE'
    THEN

        IF OLD.origin = 'shared'
        THEN
            UPDATE z_plume.meta_shared_categorie 
                SET (
                    path, origin, label, description, special, is_node, datatype,
                    is_long_text, rowspan, placeholder, input_mask, is_multiple,
                    unilang, is_mandatory, sources, geo_tools, compute, template_order,
                    compute_params
                ) = (
                    NEW.path, NEW.origin, NEW.label, NEW.description, NEW.special, NEW.is_node, NEW.datatype,
                    NEW.is_long_text, NEW.rowspan, NEW.placeholder, NEW.input_mask, NEW.is_multiple,
                    NEW.unilang, NEW.is_mandatory, NEW.sources, NEW.geo_tools, NEW.compute, NEW.template_order,
                    NEW.compute_params
                )
                WHERE meta_shared_categorie.path = OLD.path ;
        ELSE
            UPDATE z_plume.meta_local_categorie 
                SET (
                    path, origin, label, description, special, is_node, datatype,
                    is_long_text, rowspan, placeholder, input_mask, is_multiple,
                    unilang, is_mandatory, sources, geo_tools, compute, template_order,
                    compute_params
                ) = (
                    NEW.path, NEW.origin, NEW.label, NEW.description, NEW.special, NEW.is_node, NEW.datatype,
                    NEW.is_long_text, NEW.rowspan, NEW.placeholder, NEW.input_mask, NEW.is_multiple,
                    NEW.unilang, NEW.is_mandatory, NEW.sources, NEW.geo_tools, NEW.compute, NEW.template_order,
                    NEW.compute_params
                )
                WHERE meta_local_categorie.path = OLD.path ;
        END IF ;

        RETURN NEW ;

    END IF ;

    IF TG_OP = 'INSERT'
    THEN

        IF NEW.origin = 'shared'
        THEN
            INSERT INTO z_plume.meta_shared_categorie 
                (
                    path, origin, label, description, special, is_node, datatype,
                    is_long_text, rowspan, placeholder, input_mask, is_multiple,
                    unilang, is_mandatory, sources, geo_tools, compute, template_order,
                    compute_params
                ) VALUES (
                    NEW.path, coalesce(NEW.origin, 'shared'), NEW.label, NEW.description, NEW.special, 
                    coalesce(NEW.is_node, False), NEW.datatype, NEW.is_long_text, NEW.rowspan, NEW.placeholder, 
                    NEW.input_mask, NEW.is_multiple, NEW.unilang, NEW.is_mandatory, NEW.sources, NEW.geo_tools, 
                    NEW.compute, NEW.template_order, NEW.compute_params
                ) ;
        ELSE
            INSERT INTO z_plume.meta_local_categorie 
                (
                    path, origin, label, description, special, is_node, datatype,
                    is_long_text, rowspan, placeholder, input_mask, is_multiple,
                    unilang, is_mandatory, sources, geo_tools, compute, template_order,
                    compute_params
                ) VALUES (
                    coalesce(NEW.path, format('uuid:%s', gen_random_uuid())), coalesce(NEW.origin, 'local'), 
                    NEW.label, NEW.description, NEW.special, coalesce(NEW.is_node, False), NEW.datatype,
                    NEW.is_long_text, NEW.rowspan, NEW.placeholder, NEW.input_mask, NEW.is_multiple,
                    NEW.unilang, NEW.is_mandatory, NEW.sources, NEW.geo_tools, NEW.compute, NEW.template_order,
                    NEW.compute_params
                ) ;
        END IF ;

        RETURN NEW ;

    END IF ;

END
$BODY$ ;

COMMENT ON FUNCTION z_plume.meta_categorie_instead_of_action() IS 'Fonction exécutée par le trigger meta_categorie_instead_of_action, qui répercute l''action sur la table des métadonnées locales ou communes, selon "origin".' ;

-- Trigger: meta_categorie_instead_of_action on z_plume.meta_categorie

CREATE TRIGGER meta_categorie_instead_of_action
    INSTEAD OF INSERT OR UPDATE OR DELETE
    ON z_plume.meta_categorie
    FOR EACH ROW
    EXECUTE PROCEDURE z_plume.meta_categorie_instead_of_action() ;
    
COMMENT ON TRIGGER meta_categorie_instead_of_action ON z_plume.meta_categorie IS 'Répercute l''action sur la table des métadonnées locales ou communes, selon "origin".' ;


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

