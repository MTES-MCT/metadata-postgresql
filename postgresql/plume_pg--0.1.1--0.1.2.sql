\echo Use "ALTER EXTENSION plume_pg UPDATE TO '0.1.1'" to load this file. \quit
-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
--
-- PlumePg - Système de gestion des métadonnées locales, version 0.1.2
-- > Script de mise à jour depuis la version 0.1.1
--
-- Copyright République Française, 2022.
-- Secrétariat général du Ministère de la transition écologique et
-- de la cohésion des territoires, du Ministère de la transition
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
-- objets créés par le script : néant.
-- objets modifiés par le script :
-- - Table: z_plume.meta_shared_categorie (données)
--
-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

-- Table: z_plume.meta_shared_categorie

UPDATE z_plume.meta_categorie
    SET sources = ARRAY[
        'http://publications.europa.eu/resource/authority/data-theme',
        'http://inspire.ec.europa.eu/theme',
        'http://inspire.ec.europa.eu/metadata-codelist/TopicCategory'
    ]
    WHERE path = 'dcat:theme' ;

UPDATE z_plume.meta_categorie
    SET sources = ARRAY[
        'http://inspire.ec.europa.eu/metadata-codelist/MaintenanceFrequency',
        'http://publications.europa.eu/resource/authority/frequency'
    ]
    WHERE path = 'dct:accrualPeriodicity' ;

INSERT INTO z_plume.meta_categorie (
        path, origin, label, description, special,
        is_node, datatype, is_long_text, rowspan,
        placeholder, input_mask, is_multiple, unilang,
        is_mandatory, sources, geo_tools, compute,
        template_order
    ) VALUES
    (
        'adms:status', 'shared', 'Statut', 'Maturité du jeu de données.', 'url',
        false, NULL, false, NULL,
        NULL, NULL, false, false,
        false, ARRAY[
            'http://publications.europa.eu/resource/authority/dataset-status',
            'http://registre.data.developpement-durable.gouv.fr/plume/ISO19139ProgressCode'
        ], NULL, NULL,
        15
    ) ;

UPDATE z_plume.meta_categorie
    SET sources = ARRAY[
        'http://publications.europa.eu/resource/authority/dataset-status',
        'http://registre.data.developpement-durable.gouv.fr/plume/ISO19139ProgressCode'
    ],
        label = 'Maturité de la distribution.'
    WHERE path = 'dcat:distribution / adms:status' ;




