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
-- objets créés par le script : néant.
--
-- objets modifiés par le script :
-- - Table: z_plume.meta_shared_categorie
--
-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

-- Table: z_plume.meta_shared_categorie

UPDATE z_plume.meta_shared_categorie
    SET sources = sources || ARRAY[
        'http://registre.data.developpement-durable.gouv.fr/ecospheres/themes-ecospheres'
    ]
    WHERE sources IS NOT NULL AND path = 'dcat:theme' ;

UPDATE z_plume.meta_shared_categorie
    SET description = 'Classification thématique du jeu de données.'
    WHERE path = 'dcat:theme' ;

UPDATE z_plume.meta_shared_categorie
    SET is_node = False,
        sources = ARRAY[
            'http://registre.data.developpement-durable.gouv.fr/plume/EuAdministrativeTerritoryUnitFrance',
            'http://registre.data.developpement-durable.gouv.fr/plume/InseeIndividualTerritory',
            'http://publications.europa.eu/resource/authority/atu'
        ],
        special = 'url'
    WHERE path = 'dct:spatial' ;

UPDATE z_plume.meta_shared_categorie
    SET sources = ARRAY['http://registre.data.developpement-durable.gouv.fr/plume/OgcEpsgFrance']
        || sources
        || ARRAY['http://registre.data.developpement-durable.gouv.fr/plume/IgnCrs']
    WHERE sources IS NOT NULL AND path in (
        'dct:conformsTo',
        'dcat:distribution / dcat:accessService / dct:conformsTo',
        'dcat:distribution / dct:conformsTo'
    ) ;

UPDATE z_plume.meta_shared_categorie
    SET sources = sources
        || ARRAY['http://registre.data.developpement-durable.gouv.fr/plume/IanaMediaType']
    WHERE sources IS NOT NULL AND path in (
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
