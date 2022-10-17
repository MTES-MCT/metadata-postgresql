# Métadonnées communes

| Chemin | Nom | Description | Thésaurus |
| --- | --- | --- | --- |
| `dct:title` | Libellé | Nom explicite du jeu de données. |  |
| `owl:versionInfo` | Version | Numéro de version ou millésime du jeu de données. |  |
| `dct:description` | Description | Description du jeu de données. |  |
| `plume:isExternal` | Donnée externe | Ce jeu de données est-il la reproduction de données produites par un tiers ? Une donnée issue d'une source externe mais ayant fait l'objet d'améliorations notables n'est plus une donnée externe. |  |
| `dcat:theme` | Thèmes | Classification thématique du jeu de données. | [Thème de données (UE)](http://publications.europa.eu/resource/authority/data-theme), [Thème (INSPIRE)](http://inspire.ec.europa.eu/theme), [Catégories thématiques ISO 19115 (INSPIRE)](http://inspire.ec.europa.eu/metadata-codelist/TopicCategory) |
| `dcat:keyword` | Mots-clés libres | Mots ou très brèves expressions représentatives du jeu de données, à l'usage des moteurs de recherche. |  |
| `dct:spatial` | Couverture géographique | Territoire·s décrit·s par le jeu de données. |  |
| `dct:spatial / skos:inScheme` | Index géographique | Type de lieu, index de référence pour l'identifiant (commune, département...). | [Index géographique de l'INSEE](http://registre.data.developpement-durable.gouv.fr/plume/InseeGeoIndex) |
| `dct:spatial / dct:identifier` | Code géographique | Code du département, code INSEE de la commune, etc. |  |
| `dct:spatial / skos:prefLabel` | Libellé | Dénomination explicite du lieu. |  |
| `dct:spatial / dcat:bbox` | Rectangle d'emprise | Rectangle d'emprise (BBox), au format textuel WKT. |  |
| `dct:spatial / dcat:centroid` | Centroïde | Localisant du centre géographique des données, au format textuel WKT. |  |
| `dct:spatial / locn:geometry` | Géométrie | Emprise géométrique, au format textuel WKT. |  |
| `dct:temporal` | Couverture temporelle | Période·s décrite·s par le jeu de données. La date de début et la date de fin peuvent être confondues, par exemple dans le cas de l'extraction ponctuelle d'une base mise à jour au fil de l'eau. |  |
| `dct:temporal / dcat:startDate` | Date de début | Date de début de la période. |  |
| `dct:temporal / dcat:endDate` | Date de fin | Date de fin de la période. |  |
| `dct:created` | Date de création | Date de création du jeu de données. Il peut par exemple s'agir de la date de création de la table PostgreSQL ou de la date de la première saisie de données dans cette table. |  |
| `dct:modified` | Date de dernière modification | Date de la dernière modification du jeu de données. Cette date est présumée tenir compte tant des modifications de fond, tels que les ajouts d'enregistrements, que des modification purement formelles (corrections de coquilles dans les données, changement de nom d'un champ, etc.). L'absence de date de dernière modification signifie que la donnée n'a jamais été modifiée depuis sa création. |  |
| `dct:issued` | Date de publication | Date à laquelle le jeu de données a été diffusé. Cette date ne devrait être renseignée que pour un jeu de données effectivement mis à disposition du public ou d'utilisateur tiers via un catalogue de données ou un site internet. Pour un jeu de données mis à jour en continu, il s'agit de la date de publication initiale. |  |
| `dct:accrualPeriodicity` | Fréquence de mise à jour | Fréquence de mise à jour des données. | [Fréquence d'actualisation (INSPIRE)](http://inspire.ec.europa.eu/metadata-codelist/MaintenanceFrequency), [Fréquences (UE)](http://publications.europa.eu/resource/authority/frequency) |
| `adms:status` | Statut | Maturité du jeu de données. | [Statut du jeu de données (UE)](http://publications.europa.eu/resource/authority/dataset-status), [État du jeu de données (ISO 19139)](http://registre.data.developpement-durable.gouv.fr/plume/ISO19139ProgressCode) |
| `dct:provenance` | Généalogie | Sources et méthodes mises en œuvre pour produire les données. |  |
| `dct:provenance / rdfs:label` | Texte | Informations sur l'origine des données : sources, méthodes de recueil ou de traitement... |  |
| `adms:versionNotes` | Note de version | Différences entre la version courante des données et les versions antérieures. |  |
| `dct:conformsTo` | Conforme à | Standard, schéma, référentiel de coordonnées, etc. auquel se conforment les données. | [Registre EPSG de l'OGC (systèmes de coordonnées)](http://www.opengis.net/def/crs/EPSG/0) |
| `dct:conformsTo / skos:inScheme` | Registre | Registre de référence auquel appartient le standard. | [Registre de standards](http://registre.data.developpement-durable.gouv.fr/plume/StandardsRegister) |
| `dct:conformsTo / dct:identifier` | Identifiant | Identifiant du standard, s'il y a lieu. Pour un système de coordonnées géographiques, il s'agit du code EPSG. |  |
| `dct:conformsTo / dct:title` | Libellé | Libellé explicite du standard. |  |
| `dct:conformsTo / owl:versionInfo` | Version | Numéro ou code de la version du standard à laquelle se conforment les données. |  |
| `dct:conformsTo / dct:description` | Description | Description sommaire de l'objet du standard. |  |
| `dct:conformsTo / dct:issued` | Date de publication | Date de publication du standard. |  |
| `dct:conformsTo / dct:modified` | Date de modification | Date de la dernière modification du standard. |  |
| `dct:conformsTo / dct:created` | Date de création | Date de création du standard. |  |
| `dct:conformsTo / foaf:page` | Page internet | Chemin d'accès au standard ou URL d'une page contenant des informations sur le standard. |  |
| `dcat:spatialResolutionInMeters` | Résolution spatiale en mètres | Plus petite distance significative dans le contexte du jeu de données, exprimée en mètres. |  |
| `dcat:temporalResolution` | Résolution temporelle | Plus petit pas de temps significatif dans le contexte du jeu de données. |  |
| `dct:accessRights` | Conditions d'accès | Contraintes réglementaires limitant l'accès aux données. | [Restriction d'accès public (INSPIRE)](http://inspire.ec.europa.eu/metadata-codelist/LimitationsOnPublicAccess), [Droits d'accès (UE)](http://publications.europa.eu/resource/authority/access-right), [Restrictions d'accès en application du Code des relations entre le public et l'administration](http://registre.data.developpement-durable.gouv.fr/plume/CrpaAccessLimitations) |
| `dct:accessRights / rdfs:label` | Mention | Description des contraintes réglementaires et des modalités pratiques pour s'y conformer. |  |
| `dcat:contactPoint` | Point de contact | Entité à contacter pour obtenir des informations sur les données. |  |
| `dcat:contactPoint / vcard:fn` | Nom | Nom du point de contact. |  |
| `dcat:contactPoint / vcard:hasEmail` | Courriel | Adresse mél. |  |
| `dcat:contactPoint / vcard:hasTelephone` | Téléphone | Numéro de téléphone. |  |
| `dcat:contactPoint / vcard:hasURL` | Site internet | Site internet. |  |
| `dcat:contactPoint / vcard:organization-name` | Appartient à | Le cas échéant, organisation dont le point de contact fait partie. |  |
| `dct:publisher` | Éditeur | Organisme ou personne qui assure la publication des données. |  |
| `dct:publisher / foaf:name` | Nom | Nom de l'organisation. |  |
| `dct:publisher / dct:type` | Type | Type d'organisation. | [Types d'entité en charge de la publication (UE)](http://purl.org/adms/publishertype/1.0) |
| `dct:publisher / foaf:mbox` | Courriel | Adresse mél. |  |
| `dct:publisher / foaf:phone` | Téléphone | Numéro de téléphone. |  |
| `dct:publisher / foaf:workplaceHomepage` | Site internet | Site internet. |  |
| `dct:creator` | Auteur | Principal responsable de la production des données. |  |
| `dct:creator / foaf:name` | Nom | Nom de l'organisation. |  |
| `dct:creator / dct:type` | Type | Type d'organisation. | [Types d'entité en charge de la publication (UE)](http://purl.org/adms/publishertype/1.0) |
| `dct:creator / foaf:mbox` | Courriel | Adresse mél. |  |
| `dct:creator / foaf:phone` | Téléphone | Numéro de téléphone. |  |
| `dct:creator / foaf:workplaceHomepage` | Site internet | Site internet. |  |
| `dct:rightsHolder` | Propriétaire | Organisme ou personne qui détient des droits sur les données. |  |
| `dct:rightsHolder / foaf:name` | Nom | Nom de l'organisation. |  |
| `dct:rightsHolder / dct:type` | Type | Type d'organisation. | [Types d'entité en charge de la publication (UE)](http://purl.org/adms/publishertype/1.0) |
| `dct:rightsHolder / foaf:mbox` | Courriel | Adresse mél. |  |
| `dct:rightsHolder / foaf:phone` | Téléphone | Numéro de téléphone. |  |
| `dct:rightsHolder / foaf:workplaceHomepage` | Site internet | Site internet. |  |
| `geodcat:custodian` | Gestionnaire | Organisme ou personne qui assume la maintenance des données. |  |
| `geodcat:custodian / foaf:name` | Nom | Nom de l'organisation. |  |
| `geodcat:custodian / dct:type` | Type | Type d'organisation. | [Types d'entité en charge de la publication (UE)](http://purl.org/adms/publishertype/1.0) |
| `geodcat:custodian / foaf:mbox` | Courriel | Adresse mél. |  |
| `geodcat:custodian / foaf:phone` | Téléphone | Numéro de téléphone. |  |
| `geodcat:custodian / foaf:workplaceHomepage` | Site internet | Site internet. |  |
| `geodcat:distributor` | Distributeur | Organisme ou personne qui assure la distribution des données. |  |
| `geodcat:distributor / foaf:name` | Nom | Nom de l'organisation. |  |
| `geodcat:distributor / dct:type` | Type | Type d'organisation. | [Types d'entité en charge de la publication (UE)](http://purl.org/adms/publishertype/1.0) |
| `geodcat:distributor / foaf:mbox` | Courriel | Adresse mél. |  |
| `geodcat:distributor / foaf:phone` | Téléphone | Numéro de téléphone. |  |
| `geodcat:distributor / foaf:workplaceHomepage` | Site internet | Site internet. |  |
| `geodcat:originator` | Commanditaire | Organisme ou personne qui est à l'origine de la création des données. |  |
| `geodcat:originator / foaf:name` | Nom | Nom de l'organisation. |  |
| `geodcat:originator / dct:type` | Type | Type d'organisation. | [Types d'entité en charge de la publication (UE)](http://purl.org/adms/publishertype/1.0) |
| `geodcat:originator / foaf:mbox` | Courriel | Adresse mél. |  |
| `geodcat:originator / foaf:phone` | Téléphone | Numéro de téléphone. |  |
| `geodcat:originator / foaf:workplaceHomepage` | Site internet | Site internet. |  |
| `geodcat:principalInvestigator` | Maître d'œuvre | Organisme ou personne chargée du recueil des informations. |  |
| `geodcat:principalInvestigator / foaf:name` | Nom | Nom de l'organisation. |  |
| `geodcat:principalInvestigator / dct:type` | Type | Type d'organisation. | [Types d'entité en charge de la publication (UE)](http://purl.org/adms/publishertype/1.0) |
| `geodcat:principalInvestigator / foaf:mbox` | Courriel | Adresse mél. |  |
| `geodcat:principalInvestigator / foaf:phone` | Téléphone | Numéro de téléphone. |  |
| `geodcat:principalInvestigator / foaf:workplaceHomepage` | Site internet | Site internet. |  |
| `geodcat:processor` | Intégrateur | Organisation ou personne qui a retraité les données. |  |
| `geodcat:processor / foaf:name` | Nom | Nom de l'organisation. |  |
| `geodcat:processor / dct:type` | Type | Type d'organisation. | [Types d'entité en charge de la publication (UE)](http://purl.org/adms/publishertype/1.0) |
| `geodcat:processor / foaf:mbox` | Courriel | Adresse mél. |  |
| `geodcat:processor / foaf:phone` | Téléphone | Numéro de téléphone. |  |
| `geodcat:processor / foaf:workplaceHomepage` | Site internet | Site internet. |  |
| `geodcat:resourceProvider` | Fournisseur de la ressource | Organisme ou personne qui diffuse les données, soit directement soit par l'intermédiaire d'un distributeur. |  |
| `geodcat:resourceProvider / foaf:name` | Nom | Nom de l'organisation. |  |
| `geodcat:resourceProvider / dct:type` | Type | Type d'organisation. | [Types d'entité en charge de la publication (UE)](http://purl.org/adms/publishertype/1.0) |
| `geodcat:resourceProvider / foaf:mbox` | Courriel | Adresse mél. |  |
| `geodcat:resourceProvider / foaf:phone` | Téléphone | Numéro de téléphone. |  |
| `geodcat:resourceProvider / foaf:workplaceHomepage` | Site internet | Site internet. |  |
| `geodcat:user` | Utilisateur | Organisme ou personne qui utilise les données. |  |
| `geodcat:user / foaf:name` | Nom | Nom de l'organisation. |  |
| `geodcat:user / dct:type` | Type | Type d'organisation. | [Types d'entité en charge de la publication (UE)](http://purl.org/adms/publishertype/1.0) |
| `geodcat:user / foaf:mbox` | Courriel | Adresse mél. |  |
| `geodcat:user / foaf:phone` | Téléphone | Numéro de téléphone. |  |
| `geodcat:user / foaf:workplaceHomepage` | Site internet | Site internet. |  |
| `dcat:distribution` | Distribution | Distribution. |  |
| `dcat:distribution / dcat:accessURL` | URL d'accès | URL de la page où est publiée cette distribution des données. |  |
| `dcat:distribution / dct:title` | Libellé | Nom de la distribution. |  |
| `dcat:distribution / dct:description` | Description | Description de la distribution. |  |
| `dcat:distribution / dcat:downloadURL` | Lien de téléchargement direct | URL de téléchargement direct du ou des fichiers de la distribution. |  |
| `dcat:distribution / dct:issued` | Date de publication | Date à laquelle la distribution a été diffusée. |  |
| `dcat:distribution / dct:modified` | Date de dernière modification | Date de la dernière modification de la distribution. |  |
| `dcat:distribution / dcatap:availability` | Disponibilité | Niveau de disponibilité prévu pour la distribution, permettant d'apprécier le temps pendant lequel elle est susceptible de rester accessible. | [Disponibilité prévue (UE)](http://publications.europa.eu/resource/authority/planned-availability) |
| `dcat:distribution / adms:status` | Statut | Maturité de la distribution. | [Statut du jeu de données (UE)](http://publications.europa.eu/resource/authority/dataset-status), [État du jeu de données (ISO 19139)](http://registre.data.developpement-durable.gouv.fr/plume/ISO19139ProgressCode) |
| `dcat:distribution / dct:type` | Type de distribution | Type de distribution. | [Type de distribution (UE)](http://publications.europa.eu/resource/authority/distribution-type) |
| `dcat:distribution / dct:format` | Format de fichier | Format de fichier ou extension. | [Type de fichier (UE)](http://publications.europa.eu/resource/authority/file-type) |
| `dcat:distribution / dct:format / rdfs:label` | Nom | Libellé du format. |  |
| `dcat:distribution / dcat:compressFormat` | Format de compression | Format du fichier contenant les données sous une forme compressée, afin de réduire leur volume. | [Type de fichier (UE)](http://publications.europa.eu/resource/authority/file-type) |
| `dcat:distribution / dcat:compressFormat / rdfs:label` | Nom | Libellé du format. |  |
| `dcat:distribution / dcat:packageFormat` | Format d'empaquatage | Format du fichier rassemblant les différents fichiers contenant les données pour permettre leur téléchargement conjoint. | [Type de fichier (UE)](http://publications.europa.eu/resource/authority/file-type) |
| `dcat:distribution / dcat:packageFormat / rdfs:label` | Nom | Libellé du format. |  |
| `dcat:distribution / dcat:accessService` | Service | Service donnant accès aux données. |  |
| `dcat:distribution / dcat:accessService / dct:title` | Libellé | Nom explicite du service de données. |  |
| `dcat:distribution / dcat:accessService / dcat:endpointURL` | URL de base | URL de base du service de données, sans aucun paramètre. |  |
| `dcat:distribution / dcat:accessService / dct:conformsTo` | Conforme à | Standard ou référentiel de coordonnées auquel se conforme le service. | [Registre EPSG de l'OGC (systèmes de coordonnées)](http://www.opengis.net/def/crs/EPSG/0), [Standards de services de données](http://registre.data.developpement-durable.gouv.fr/plume/DataServiceStandard) |
| `dcat:distribution / dcat:accessService / dct:conformsTo / skos:inScheme` | Registre | Registre de référence auquel appartient le standard. | [Registre de standards](http://registre.data.developpement-durable.gouv.fr/plume/StandardsRegister) |
| `dcat:distribution / dcat:accessService / dct:conformsTo / dct:identifier` | Identifiant | Identifiant du standard, s'il y a lieu. Pour un système de coordonnées géographiques, il s'agit du code EPSG. |  |
| `dcat:distribution / dcat:accessService / dct:conformsTo / dct:title` | Libellé | Libellé explicite du standard. |  |
| `dcat:distribution / dcat:accessService / dct:conformsTo / owl:versionInfo` | Version | Numéro ou code de la version du standard à laquelle se conforment les données. |  |
| `dcat:distribution / dcat:accessService / dct:conformsTo / dct:description` | Description | Description sommaire de l'objet du standard. |  |
| `dcat:distribution / dcat:accessService / dct:conformsTo / dct:issued` | Date de publication | Date de publication du standard. |  |
| `dcat:distribution / dcat:accessService / dct:conformsTo / dct:modified` | Date de modification | Date de la dernière modification du standard. |  |
| `dcat:distribution / dcat:accessService / dct:conformsTo / dct:created` | Date de création | Date de création du standard. |  |
| `dcat:distribution / dcat:accessService / dct:conformsTo / foaf:page` | Page internet | Chemin d'accès au standard ou URL d'une page contenant des informations sur le standard. |  |
| `dcat:distribution / dcat:accessService / dcat:endpointDescription` | URL de la description | URL de la description technique du service, par exemple le GetCapabilities d'un service WMS. |  |
| `dcat:distribution / dcat:accessService / dct:description` | Description | Description libre du service. |  |
| `dcat:distribution / dcat:accessService / dcat:keyword` | Mots-clés libres | Mots ou très brèves expressions représentatives du service. |  |
| `dcat:distribution / dcat:accessService / dct:type` | Type de service de données | Type de service de données. | [Types de services de données (UE)](http://publications.europa.eu/resource/authority/data-service-type) |
| `dcat:distribution / dcat:accessService / dct:accessRights` | Conditions d'accès | Contraintes réglementaires limitant l'accès au service. | [Restriction d'accès public (INSPIRE)](http://inspire.ec.europa.eu/metadata-codelist/LimitationsOnPublicAccess), [Droits d'accès (UE)](http://publications.europa.eu/resource/authority/access-right), [Restrictions d'accès en application du Code des relations entre le public et l'administration](http://registre.data.developpement-durable.gouv.fr/plume/CrpaAccessLimitations) |
| `dcat:distribution / dcat:accessService / dct:accessRights / rdfs:label` | Mention | Description des contraintes réglementaires et des modalités pratiques pour s'y conformer. |  |
| `dcat:distribution / dcat:accessService / dct:license` | Licence | Licence de mise à diposition des données via le service, ou conditions d'utilisation du service. | [Licences admises pour les informations publiques des administrations françaises](http://registre.data.developpement-durable.gouv.fr/plume/CrpaAuthorizedLicense), [Licences (UE)](http://publications.europa.eu/resource/authority/licence) |
| `dcat:distribution / dcat:accessService / dct:license / dct:type` | Type | Caractéristiques de la licence. | [Types de licence (UE)](http://purl.org/adms/licencetype/1.1) |
| `dcat:distribution / dcat:accessService / dct:license / rdfs:label` | Termes | Termes de la licence. |  |
| `dcat:distribution / dcat:accessService / dcat:contactPoint` | Point de contact | Entité à contacter pour obtenir des informations sur le service. |  |
| `dcat:distribution / dcat:accessService / dcat:contactPoint / vcard:fn` | Nom | Nom du point de contact. |  |
| `dcat:distribution / dcat:accessService / dcat:contactPoint / vcard:hasEmail` | Courriel | Adresse mél. |  |
| `dcat:distribution / dcat:accessService / dcat:contactPoint / vcard:hasTelephone` | Téléphone | Numéro de téléphone. |  |
| `dcat:distribution / dcat:accessService / dcat:contactPoint / vcard:hasURL` | Site internet | Site internet. |  |
| `dcat:distribution / dcat:accessService / dcat:contactPoint / vcard:organization-name` | Appartient à | Le cas échéant, organisation dont le point de contact fait partie. |  |
| `dcat:distribution / dcat:accessService / dct:publisher` | Éditeur | Organisme ou personne responsable de la mise à disposition du service. |  |
| `dcat:distribution / dcat:accessService / dct:publisher / foaf:name` | Nom | Nom de l'organisation. |  |
| `dcat:distribution / dcat:accessService / dct:publisher / dct:type` | Type | Type d'organisation. | [Types d'entité en charge de la publication (UE)](http://purl.org/adms/publishertype/1.0) |
| `dcat:distribution / dcat:accessService / dct:publisher / foaf:mbox` | Courriel | Adresse mél. |  |
| `dcat:distribution / dcat:accessService / dct:publisher / foaf:phone` | Téléphone | Numéro de téléphone. |  |
| `dcat:distribution / dcat:accessService / dct:publisher / foaf:workplaceHomepage` | Site internet | Site internet. |  |
| `dcat:distribution / dcat:accessService / dct:creator` | Auteur | Principal acteur de la création du service. |  |
| `dcat:distribution / dcat:accessService / dct:creator / foaf:name` | Nom | Nom de l'organisation. |  |
| `dcat:distribution / dcat:accessService / dct:creator / dct:type` | Type | Type d'organisation. | [Types d'entité en charge de la publication (UE)](http://purl.org/adms/publishertype/1.0) |
| `dcat:distribution / dcat:accessService / dct:creator / foaf:mbox` | Courriel | Adresse mél. |  |
| `dcat:distribution / dcat:accessService / dct:creator / foaf:phone` | Téléphone | Numéro de téléphone. |  |
| `dcat:distribution / dcat:accessService / dct:creator / foaf:workplaceHomepage` | Site internet | Site internet. |  |
| `dcat:distribution / dcat:accessService / dct:rightsHolder` | Propriétaire | Organisme ou personne qui détient des droits sur le service. |  |
| `dcat:distribution / dcat:accessService / dct:rightsHolder / foaf:name` | Nom | Nom de l'organisation. |  |
| `dcat:distribution / dcat:accessService / dct:rightsHolder / dct:type` | Type | Type d'organisation. | [Types d'entité en charge de la publication (UE)](http://purl.org/adms/publishertype/1.0) |
| `dcat:distribution / dcat:accessService / dct:rightsHolder / foaf:mbox` | Courriel | Adresse mél. |  |
| `dcat:distribution / dcat:accessService / dct:rightsHolder / foaf:phone` | Téléphone | Numéro de téléphone. |  |
| `dcat:distribution / dcat:accessService / dct:rightsHolder / foaf:workplaceHomepage` | Site internet | Site internet. |  |
| `dcat:distribution / dcat:accessService / dct:issued` | Date d'ouverture | Date d'ouverture du service. |  |
| `dcat:distribution / dcat:accessService / dct:language` | Langues | Langue·s prises en charge par le service. | [Langues (UE)](http://publications.europa.eu/resource/authority/language) |
| `dcat:distribution / dcat:accessService / dct:spatial` | Couverture géographique | Territoire couvert par le service. |  |
| `dcat:distribution / dcat:accessService / dct:spatial / skos:inScheme` | Index géographique | Type de lieu, index de référence pour l'identifiant (commune, département...). | [Index géographique de l'INSEE](http://registre.data.developpement-durable.gouv.fr/plume/InseeGeoIndex) |
| `dcat:distribution / dcat:accessService / dct:spatial / dct:identifier` | Code géographique | Code du département, code INSEE de la commune, etc. |  |
| `dcat:distribution / dcat:accessService / dct:spatial / skos:prefLabel` | Libellé | Dénomination explicite du lieu. |  |
| `dcat:distribution / dcat:accessService / dct:spatial / dcat:bbox` | Rectangle d'emprise | Rectangle d'emprise (BBox), au format textuel WKT. |  |
| `dcat:distribution / dcat:accessService / dct:spatial / dcat:centroid` | Centroïde | Localisant du centre géographique des données, au format textuel WKT. |  |
| `dcat:distribution / dcat:accessService / dct:spatial / locn:geometry` | Géométrie | Emprise géométrique, au format textuel WKT. |  |
| `dcat:distribution / dcat:accessService / dcat:spatialResolutionInMeters` | Résolution spatiale en mètres | Résolution des données mises à disposition par le service, exprimée en mètres. |  |
| `dcat:distribution / dcat:accessService / dct:temporal` | Couverture temporelle | Période pour laquelle des données sont mises à disposition par le service. |  |
| `dcat:distribution / dcat:accessService / dct:temporal / dcat:startDate` | Date de début | Date de début de la période. |  |
| `dcat:distribution / dcat:accessService / dct:temporal / dcat:endDate` | Date de fin | Date de fin de la période. |  |
| `dcat:distribution / dcat:accessService / dcat:temporalResolution` | Résolution temporelle | Résolution temporelle des données mises à disposition par le service. |  |
| `dcat:distribution / adms:representationTechnique` | Mode de représentation géographique | Type de représentation technique de l'information géographique présentée par la distribution, le cas échéant. | [Type de représentation géographique (INSPIRE)](http://inspire.ec.europa.eu/metadata-codelist/SpatialRepresentationType) |
| `dcat:distribution / foaf:page` | Documentation | Documentation ou page internet contenant des informations relative à la distribution. |  |
| `dcat:distribution / dct:conformsTo` | Conforme à | Standard, schéma, référentiel de coordonnées, etc. auquel se conforment les données de la distribution. | [Registre EPSG de l'OGC (systèmes de coordonnées)](http://www.opengis.net/def/crs/EPSG/0) |
| `dcat:distribution / dct:conformsTo / skos:inScheme` | Registre | Registre de référence auquel appartient le standard. | [Registre de standards](http://registre.data.developpement-durable.gouv.fr/plume/StandardsRegister) |
| `dcat:distribution / dct:conformsTo / dct:identifier` | Identifiant | Identifiant du standard, s'il y a lieu. Pour un système de coordonnées géographiques, il s'agit du code EPSG. |  |
| `dcat:distribution / dct:conformsTo / dct:title` | Libellé | Libellé explicite du standard. |  |
| `dcat:distribution / dct:conformsTo / owl:versionInfo` | Version | Numéro ou code de la version du standard à laquelle se conforment les données. |  |
| `dcat:distribution / dct:conformsTo / dct:description` | Description | Description sommaire de l'objet du standard. |  |
| `dcat:distribution / dct:conformsTo / dct:issued` | Date de publication | Date de publication du standard. |  |
| `dcat:distribution / dct:conformsTo / dct:modified` | Date de modification | Date de la dernière modification du standard. |  |
| `dcat:distribution / dct:conformsTo / dct:created` | Date de création | Date de création du standard. |  |
| `dcat:distribution / dct:conformsTo / foaf:page` | Page internet | Chemin d'accès au standard ou URL d'une page contenant des informations sur le standard. |  |
| `dcat:distribution / cnt:characterEncoding` | Encodage | Encodage de la distribution. |  |
| `dcat:distribution / dct:language` | Langue | Langue·s des données de la distribution. | [Langues (UE)](http://publications.europa.eu/resource/authority/language) |
| `dcat:distribution / dcat:byteSize` | Taille en bytes | Taille en bytes de la distribution. |  |
| `dcat:distribution / dcat:temporalResolution` | Résolution temporelle | Plus petit pas de temps significatif dans le contexte de la distribution. |  |
| `dcat:distribution / dcat:spatialResolutionInMeters` | Résolution spatiale en mètres | Résolution des données de la distribution, exprimée en mètres. |  |
| `dcat:distribution / dct:rights` | Propriété intellectuelle | Mention rappelant les droits de propriété intellectuelle sur les données, à faire apparaître en cas de réutilisation de cette distribution des données. |  |
| `dcat:distribution / dct:rights / rdfs:label` | Mention | Description des contraintes réglementaires et des modalités pratiques pour s'y conformer. |  |
| `dcat:distribution / dct:license` | Licence | Licence sous laquelle est publiée la distribution ou conditions d'utilisation de la distribution. | [Licences admises pour les informations publiques des administrations françaises](http://registre.data.developpement-durable.gouv.fr/plume/CrpaAuthorizedLicense), [Licences (UE)](http://publications.europa.eu/resource/authority/licence) |
| `dcat:distribution / dct:license / dct:type` | Type | Caractéristiques de la licence. | [Types de licence (UE)](http://purl.org/adms/licencetype/1.1) |
| `dcat:distribution / dct:license / rdfs:label` | Termes | Termes de la licence. |  |
| `dcat:distribution / dct:accessRights` | Conditions d'accès | Contraintes réglementaires limitant l'accès à la distribution. | [Restriction d'accès public (INSPIRE)](http://inspire.ec.europa.eu/metadata-codelist/LimitationsOnPublicAccess), [Droits d'accès (UE)](http://publications.europa.eu/resource/authority/access-right), [Restrictions d'accès en application du Code des relations entre le public et l'administration](http://registre.data.developpement-durable.gouv.fr/plume/CrpaAccessLimitations) |
| `dcat:distribution / dct:accessRights / rdfs:label` | Mention | Description des contraintes réglementaires et des modalités pratiques pour s'y conformer. |  |
| `dcat:landingPage` | Page internet | URL de la fiche de métadonnées sur internet. |  |
| `foaf:page` | Documentation | URL d'accès à une documentation rédigée décrivant la donnée. |  |
| `dct:isReferencedBy` | Cité par | URL d'une publication qui utilise ou évoque les données. |  |
| `dct:relation` | Ressource liée | URL d'accès à une ressource en rapport avec les données. |  |
| `dct:language` | Langue des données | Langue·s des données. | [Langues (UE)](http://publications.europa.eu/resource/authority/language) |
| `plume:relevanceScore` | Score | Niveau de pertinence de la donnée. Plus le score est élevé plus la donnée sera mise en avant dans les résultats de recherche. |  |
| `dct:type` | Type de jeu de données | Type de jeu de données. | [Types de jeux de données (UE)](http://publications.europa.eu/resource/authority/dataset-type) |
| `dct:identifier` | Identifiant interne | Identifiant du jeu de données, attribué automatiquement par Plume. |  |
| `plume:linkedRecord` | Fiche distante | Configuration d'import des métadonnées depuis une fiche de catalogue INSPIRE. |  |
| `plume:linkedRecord / dcat:endpointURL` | Service CSW | URL de base du service CSW, sans aucun paramètre. |  |
| `plume:linkedRecord / dct:identifier` | Identifiant de la fiche | Identifiant de la fiche de métadonnées (et non de la ressource). |  |
| `foaf:isPrimaryTopicOf` | Informations sur les métadonnées | Métadonnées des métadonnées. |  |
| `foaf:isPrimaryTopicOf / dct:modified` | Date de modification des métadonnées | Date et heure de la dernière modification des métadonnées. Cette propriété est renseignée automatiquement par Plume lors de la sauvegarde de la fiche de métadonnées. |  |

