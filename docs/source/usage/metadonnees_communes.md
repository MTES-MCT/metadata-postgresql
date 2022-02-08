# Métadonnées communes

| Chemin | Nom | Description | Thésaurus |
| --- | --- | --- | --- |
| `dct:title` | Libellé | Nom explicite du jeu de données. |  |
| `owl:versionInfo` | Version | Numéro de version ou millésime du jeu de données. |  |
| `dct:description` | Description | Description du jeu de données. |  |
| `snum:isExternal` | Donnée externe | Ce jeu de données est-il la reproduction de données produites par un tiers ? Une donnée issue d'une source externe mais ayant fait l'objet d'améliorations notables n'est plus une donnée externe. |  |
| `dcat:theme` | Thèmes | Classification thématique du jeu de données selon la nomenclature généraliste du portail opendata européen et/ou, s'il y a lieu, la nomemclature INSPIRE. | [Thème de données (UE)](http://publications.europa.eu/resource/authority/data-theme), [Thème INSPIRE (UE)](https://inspire.ec.europa.eu/theme) |
| `dct:subject` | Catégories thématiques | Classification thématique du jeu données selon la nomenclature du standard ISO 19115. | [Catégories thématiques conformément à la norme EN ISO 19115](https://inspire.ec.europa.eu/metadata-codelist/TopicCategory) |
| `dcat:keyword` | Mots-clés libres | Mots ou très brèves expressions représentatives du jeu de données, à l'usage des moteurs de recherche. |  |
| `dct:spatial` | Couverture géographique | Territoire·s décrit·s par le jeu de données. |  |
| `dct:spatial / skos:inScheme` | Index géographique | Type de lieu, index de référence pour l'identifiant (commune, département...). | [Index géographique de l'INSEE](http://snum.scenari-community.org/Metadata/Vocabulaire/#InseeGeoIndex) |
| `dct:spatial / dct:identifier` | Code géographique | Code du département, code INSEE de la commune, etc. |  |
| `dct:spatial / skos:prefLabel` | Libellé | None |  |
| `dct:spatial / dcat:bbox` | Rectangle d'emprise | Rectangle d'emprise (BBox), au format textuel WKT. |  |
| `dct:spatial / dcat:centroid` | Centroïde | Localisant du centre géographique des données, au format textuel WKT. |  |
| `dct:spatial / locn:geometry` | Géométrie | Emprise géométrique, au format textuel WKT. |  |
| `dct:temporal` | Couverture temporelle | Période·s décrite·s par le jeu de données. La date de début et la date de fin peuvent être confondues, par exemple dans le cas de l'extraction ponctuelle d'une base mise à jour au fil de l'eau. |  |
| `dct:temporal / dcat:startDate` | Date de début | None |  |
| `dct:temporal / dcat:endDate` | Date de fin | None |  |
| `dct:created` | Date de création | Date de création du jeu de données. Il peut par exemple s'agir de la date de création de la table PostgreSQL ou de la date de la première saisie de données dans cette table. |  |
| `dct:modified` | Date de dernière modification | Date de la dernière modification du jeu de données. Cette date est présumée tenir compte tant des modifications de fond, tels que les ajouts d'enregistrements, que des modification purement formelles (corrections de coquilles dans les données, changement de nom d'un champ, etc.). L'absence de date de dernière modification signifie que la donnée n'a jamais été modifiée depuis sa création. |  |
| `dct:issued` | Date de publication | Date à laquelle le jeu de données a été diffusé. Cette date ne devrait être renseignée que pour un jeu de données effectivement mis à disposition du public ou d'utilisateur tiers via un catalogue de données ou un site internet. Pour un jeu de données mis à jour en continu, il s'agit de la date de publication initiale. |  |
| `dct:accrualPeriodicity` | Fréquence de mise à jour | Fréquence de mise à jour des données. | [Fréquences (UE)](http://publications.europa.eu/resource/authority/frequency) |
| `dct:provenance` | Généalogie | Sources et méthodes mises en œuvre pour produire les données. |  |
| `dct:provenance / rdfs:label` | Texte | None |  |
| `adms:versionNotes` | Note de version | Différences entre la version courante des données et les versions antérieures. |  |
| `dct:conformsTo` | Conforme à | Standard, schéma, référentiel de coordonnées, etc. auquel se conforment les données. |  |
| `dct:conformsTo / skos:inScheme` | Registre | None | [Ensemble de standards](http://snum.scenari-community.org/Metadata/Vocabulaire/#StandardsRegister) |
| `dct:conformsTo / dct:identifier` | Identifiant | Identifiant du standard, s'il y a lieu. Pour un système de coordonnées géographiques, il s'agit du code EPSG. |  |
| `dct:conformsTo / dct:title` | Libellé | Libellé explicite du standard. |  |
| `dct:conformsTo / owl:versionInfo` | Version | Numéro ou code de la version du standard à laquelle se conforment les données. |  |
| `dct:conformsTo / dct:description` | Description | Description sommaire de l'objet du standard. |  |
| `dct:conformsTo / dct:issued` | Date de publication | Date de publication du standard. |  |
| `dct:conformsTo / dct:modified` | Date de modification | Date de la dernière modification du standard. |  |
| `dct:conformsTo / dct:created` | Date de création | Date de création du standard. |  |
| `dct:conformsTo / foaf:page` | Page internet | Chemin d'accès au standard ou URL d'une page contenant des informations sur le standard. |  |
| `dct:conformsTo / dct:type` | Type de standard | None |  |
| `dcat:spatialResolutionInMeters` | Résolution spatiale en mètres | Plus petite distance significative dans le contexte du jeu de données, exprimée en mètres. |  |
| `dcat:temporalResolution` | Résolution temporelle | Plus petit pas de temps significatif dans le contexte du jeu de données. |  |
| `dct:accessRights` | Conditions d'accès | Contraintes réglementaires limitant l'accès aux données. | [Restriction d'accès public INSPIRE (UE)](http://inspire.ec.europa.eu/metadata-codelist/LimitationsOnPublicAccess), [Droits d'accès (UE)](http://publications.europa.eu/resource/authority/access-right), [Restrictions d'accès en application du Code des relations entre le public et l'administration](http://snum.scenari-community.org/Metadata/Vocabulaire/#CrpaAccessLimitations) |
| `dct:accessRights / rdfs:label` | Mention | None |  |
| `dcat:contactPoint` | Point de contact | Entité à contacter pour obtenir des informations sur les données. |  |
| `dcat:contactPoint / vcard:fn` | Nom | None |  |
| `dcat:contactPoint / vcard:hasEmail` | Courriel | None |  |
| `dcat:contactPoint / vcard:hasTelephone` | Téléphone | None |  |
| `dcat:contactPoint / vcard:hasURL` | Site internet | None |  |
| `dcat:contactPoint / vcard:organization-name` | Organisme | Le cas échéant, organisation dont le point de contact fait partie. |  |
| `dct:publisher` | Éditeur | Organisme ou personne qui assure la publication des données. |  |
| `dct:publisher / foaf:name` | Nom | None |  |
| `dct:publisher / dct:type` | Type | None | [Types d'entité en charge de la publication (UE)](http://purl.org/adms/publishertype/1.0) |
| `dct:publisher / foaf:mbox` | Courriel | None |  |
| `dct:publisher / foaf:phone` | Téléphone | None |  |
| `dct:publisher / foaf:workplaceHomepage` | Site internet | None |  |
| `dct:creator` | Auteur | Principal responsable de la production des données. |  |
| `dct:creator / foaf:name` | Nom | None |  |
| `dct:creator / dct:type` | Type | None | [Types d'entité en charge de la publication (UE)](http://purl.org/adms/publishertype/1.0) |
| `dct:creator / foaf:mbox` | Courriel | None |  |
| `dct:creator / foaf:phone` | Téléphone | None |  |
| `dct:creator / foaf:workplaceHomepage` | Site internet | None |  |
| `dct:rightsHolder` | Propriétaire | Organisme ou personne qui détient des droits sur les données. |  |
| `dct:rightsHolder / foaf:name` | Nom | None |  |
| `dct:rightsHolder / dct:type` | Type | None | [Types d'entité en charge de la publication (UE)](http://purl.org/adms/publishertype/1.0) |
| `dct:rightsHolder / foaf:mbox` | Courriel | None |  |
| `dct:rightsHolder / foaf:phone` | Téléphone | None |  |
| `dct:rightsHolder / foaf:workplaceHomepage` | Site internet | None |  |
| `geodcat:custodian` | Gestionnaire | Organisme ou personne qui assume la maintenance des données. |  |
| `geodcat:custodian / foaf:name` | Nom | None |  |
| `geodcat:custodian / dct:type` | Type | None | [Types d'entité en charge de la publication (UE)](http://purl.org/adms/publishertype/1.0) |
| `geodcat:custodian / foaf:mbox` | Courriel | None |  |
| `geodcat:custodian / foaf:phone` | Téléphone | None |  |
| `geodcat:custodian / foaf:workplaceHomepage` | Site internet | None |  |
| `geodcat:distributor` | Distributeur | Organisme ou personne qui assure la distribution des données. |  |
| `geodcat:distributor / foaf:name` | Nom | None |  |
| `geodcat:distributor / dct:type` | Type | None | [Types d'entité en charge de la publication (UE)](http://purl.org/adms/publishertype/1.0) |
| `geodcat:distributor / foaf:mbox` | Courriel | None |  |
| `geodcat:distributor / foaf:phone` | Téléphone | None |  |
| `geodcat:distributor / foaf:workplaceHomepage` | Site internet | None |  |
| `geodcat:originator` | Commanditaire | Organisme ou personne qui est à l'origine de la création des données. |  |
| `geodcat:originator / foaf:name` | Nom | None |  |
| `geodcat:originator / dct:type` | Type | None | [Types d'entité en charge de la publication (UE)](http://purl.org/adms/publishertype/1.0) |
| `geodcat:originator / foaf:mbox` | Courriel | None |  |
| `geodcat:originator / foaf:phone` | Téléphone | None |  |
| `geodcat:originator / foaf:workplaceHomepage` | Site internet | None |  |
| `geodcat:principalInvestigator` | Maître d'œuvre | Organisme ou personne chargée du recueil des informations. |  |
| `geodcat:principalInvestigator / foaf:name` | Nom | None |  |
| `geodcat:principalInvestigator / dct:type` | Type | None | [Types d'entité en charge de la publication (UE)](http://purl.org/adms/publishertype/1.0) |
| `geodcat:principalInvestigator / foaf:mbox` | Courriel | None |  |
| `geodcat:principalInvestigator / foaf:phone` | Téléphone | None |  |
| `geodcat:principalInvestigator / foaf:workplaceHomepage` | Site internet | None |  |
| `geodcat:processor` | Intégrateur | Organisation ou personne qui a retraité les données. |  |
| `geodcat:processor / foaf:name` | Nom | None |  |
| `geodcat:processor / dct:type` | Type | None | [Types d'entité en charge de la publication (UE)](http://purl.org/adms/publishertype/1.0) |
| `geodcat:processor / foaf:mbox` | Courriel | None |  |
| `geodcat:processor / foaf:phone` | Téléphone | None |  |
| `geodcat:processor / foaf:workplaceHomepage` | Site internet | None |  |
| `geodcat:resourceProvider` | Fournisseur de la ressource | Organisme ou personne qui diffuse les données, soit directement soit par l'intermédiaire d'un distributeur. |  |
| `geodcat:resourceProvider / foaf:name` | Nom | None |  |
| `geodcat:resourceProvider / dct:type` | Type | None | [Types d'entité en charge de la publication (UE)](http://purl.org/adms/publishertype/1.0) |
| `geodcat:resourceProvider / foaf:mbox` | Courriel | None |  |
| `geodcat:resourceProvider / foaf:phone` | Téléphone | None |  |
| `geodcat:resourceProvider / foaf:workplaceHomepage` | Site internet | None |  |
| `geodcat:user` | Utilisateur | Organisme ou personne qui utilise les données. |  |
| `geodcat:user / foaf:name` | Nom | None |  |
| `geodcat:user / dct:type` | Type | None | [Types d'entité en charge de la publication (UE)](http://purl.org/adms/publishertype/1.0) |
| `geodcat:user / foaf:mbox` | Courriel | None |  |
| `geodcat:user / foaf:phone` | Téléphone | None |  |
| `geodcat:user / foaf:workplaceHomepage` | Site internet | None |  |
| `dcat:distribution` | Distribution | Distribution. |  |
| `dcat:distribution / dcat:accessURL` | URL d'accès | URL de la page où est publiée cette distribution des données. |  |
| `dcat:distribution / dct:description` | Description | Description de la distribution. |  |
| `dcat:distribution / dct:issued` | Date de publication | None |  |
| `dcat:distribution / <http://data.europa.eu/r5r/availability>` | Disponibilité | Niveau de disponibilité prévu pour la distribution, permettant d'apprécier le temps pendant lequel elle est susceptible de rester accessible. | [Disponibilité prévue (UE)](http://publications.europa.eu/resource/authority/planned-availability) |
| `dcat:distribution / dct:format` | Format | Format de la distribution. | [Types de médias (IANA)](http://www.iana.org/assignments/media-types) |
| `dcat:distribution / dct:format / rdfs:label` | Nom | None |  |
| `dcat:distribution / dcat:accessService` | Service | Service donnant accès aux données. |  |
| `dcat:distribution / dcat:accessService / dct:title` | Libellé | Nom explicite du service de données. |  |
| `dcat:distribution / dcat:accessService / dcat:endpointURL` | URL de base | URL de base du service de données, sans aucun paramètre. |  |
| `dcat:distribution / dcat:accessService / dct:conformsTo` | Conforme à | Standard ou référentiel de coordonnées auquel se conforme le service. | [Standards de services de données](http://snum.scenari-community.org/Metadata/Vocabulaire/#DataServiceStandard) |
| `dcat:distribution / dcat:accessService / dct:conformsTo / skos:inScheme` | Registre | None | [Ensemble de standards](http://snum.scenari-community.org/Metadata/Vocabulaire/#StandardsRegister) |
| `dcat:distribution / dcat:accessService / dct:conformsTo / dct:identifier` | Identifiant | Identifiant du standard, s'il y a lieu. Pour un système de coordonnées géographiques, il s'agit du code EPSG. |  |
| `dcat:distribution / dcat:accessService / dct:conformsTo / dct:title` | Libellé | Libellé explicite du standard. |  |
| `dcat:distribution / dcat:accessService / dct:conformsTo / owl:versionInfo` | Version | Numéro ou code de la version du standard à laquelle se conforment les données. |  |
| `dcat:distribution / dcat:accessService / dct:conformsTo / dct:description` | Description | Description sommaire de l'objet du standard. |  |
| `dcat:distribution / dcat:accessService / dct:conformsTo / dct:issued` | Date de publication | Date de publication du standard. |  |
| `dcat:distribution / dcat:accessService / dct:conformsTo / dct:modified` | Date de modification | Date de la dernière modification du standard. |  |
| `dcat:distribution / dcat:accessService / dct:conformsTo / dct:created` | Date de création | Date de création du standard. |  |
| `dcat:distribution / dcat:accessService / dct:conformsTo / foaf:page` | Page internet | Chemin d'accès au standard ou URL d'une page contenant des informations sur le standard. |  |
| `dcat:distribution / dcat:accessService / dct:conformsTo / dct:type` | Type de standard | None |  |
| `dcat:distribution / dcat:accessService / dcat:endpointDescription` | URL de la description | URL de la description technique du service, par exemple le GetCapabilities d'un service WMS. |  |
| `dcat:distribution / dcat:accessService / dct:description` | Description | Description libre du service. |  |
| `dcat:distribution / dcat:accessService / dcat:keyword` | Mots-clés libres | Mots ou très brèves expressions représentatives du service. |  |
| `dcat:distribution / dcat:accessService / dct:accessRights` | Conditions d'accès | Contraintes réglementaires limitant l'accès au service. | [Restriction d'accès public INSPIRE (UE)](http://inspire.ec.europa.eu/metadata-codelist/LimitationsOnPublicAccess), [Droits d'accès (UE)](http://publications.europa.eu/resource/authority/access-right), [Restrictions d'accès en application du Code des relations entre le public et l'administration](http://snum.scenari-community.org/Metadata/Vocabulaire/#CrpaAccessLimitations) |
| `dcat:distribution / dcat:accessService / dct:accessRights / rdfs:label` | Mention | None |  |
| `dcat:distribution / dcat:accessService / dct:license` | Licence | Licence de mise à diposition des données via le service, ou conditions d'utilisation du service. | [Licences admises pour les informations publiques des administrations françaises](http://snum.scenari-community.org/Metadata/Vocabulaire/#CrpaAuthorizedLicense) |
| `dcat:distribution / dcat:accessService / dct:license / dct:type` | Type | None | [Types de licence (UE)](http://purl.org/adms/licencetype/1.1) |
| `dcat:distribution / dcat:accessService / dct:license / rdfs:label` | Termes | None |  |
| `dcat:distribution / dcat:accessService / dcat:contactPoint` | Point de contact | Entité à contacter pour obtenir des informations sur le service. |  |
| `dcat:distribution / dcat:accessService / dcat:contactPoint / vcard:fn` | Nom | None |  |
| `dcat:distribution / dcat:accessService / dcat:contactPoint / vcard:hasEmail` | Courriel | None |  |
| `dcat:distribution / dcat:accessService / dcat:contactPoint / vcard:hasTelephone` | Téléphone | None |  |
| `dcat:distribution / dcat:accessService / dcat:contactPoint / vcard:hasURL` | Site internet | None |  |
| `dcat:distribution / dcat:accessService / dcat:contactPoint / vcard:organization-name` | Organisme | Le cas échéant, organisation dont le point de contact fait partie. |  |
| `dcat:distribution / dcat:accessService / dct:publisher` | Éditeur | Organisme ou personne responsable de la mise à disposition du service. |  |
| `dcat:distribution / dcat:accessService / dct:publisher / foaf:name` | Nom | None |  |
| `dcat:distribution / dcat:accessService / dct:publisher / dct:type` | Type | None | [Types d'entité en charge de la publication (UE)](http://purl.org/adms/publishertype/1.0) |
| `dcat:distribution / dcat:accessService / dct:publisher / foaf:mbox` | Courriel | None |  |
| `dcat:distribution / dcat:accessService / dct:publisher / foaf:phone` | Téléphone | None |  |
| `dcat:distribution / dcat:accessService / dct:publisher / foaf:workplaceHomepage` | Site internet | None |  |
| `dcat:distribution / dcat:accessService / dct:creator` | Auteur | Principal acteur de la création du service. |  |
| `dcat:distribution / dcat:accessService / dct:creator / foaf:name` | Nom | None |  |
| `dcat:distribution / dcat:accessService / dct:creator / dct:type` | Type | None | [Types d'entité en charge de la publication (UE)](http://purl.org/adms/publishertype/1.0) |
| `dcat:distribution / dcat:accessService / dct:creator / foaf:mbox` | Courriel | None |  |
| `dcat:distribution / dcat:accessService / dct:creator / foaf:phone` | Téléphone | None |  |
| `dcat:distribution / dcat:accessService / dct:creator / foaf:workplaceHomepage` | Site internet | None |  |
| `dcat:distribution / dcat:accessService / dct:rightsHolder` | Propriétaire | Organisme ou personne qui détient des droits sur le service. |  |
| `dcat:distribution / dcat:accessService / dct:rightsHolder / foaf:name` | Nom | None |  |
| `dcat:distribution / dcat:accessService / dct:rightsHolder / dct:type` | Type | None | [Types d'entité en charge de la publication (UE)](http://purl.org/adms/publishertype/1.0) |
| `dcat:distribution / dcat:accessService / dct:rightsHolder / foaf:mbox` | Courriel | None |  |
| `dcat:distribution / dcat:accessService / dct:rightsHolder / foaf:phone` | Téléphone | None |  |
| `dcat:distribution / dcat:accessService / dct:rightsHolder / foaf:workplaceHomepage` | Site internet | None |  |
| `dcat:distribution / dcat:accessService / dct:issued` | Date d'ouverture | Date d'ouverture du service. |  |
| `dcat:distribution / dcat:accessService / dct:language` | Langues | Langue·s prises en charge par le service. | [Langues (UE)](http://publications.europa.eu/resource/authority/language) |
| `dcat:distribution / dcat:accessService / dct:spatial` | Couverture géographique | Territoire couvert par le service. |  |
| `dcat:distribution / dcat:accessService / dct:spatial / skos:inScheme` | Index géographique | Type de lieu, index de référence pour l'identifiant (commune, département...). | [Index géographique de l'INSEE](http://snum.scenari-community.org/Metadata/Vocabulaire/#InseeGeoIndex) |
| `dcat:distribution / dcat:accessService / dct:spatial / dct:identifier` | Code géographique | Code du département, code INSEE de la commune, etc. |  |
| `dcat:distribution / dcat:accessService / dct:spatial / skos:prefLabel` | Libellé | None |  |
| `dcat:distribution / dcat:accessService / dct:spatial / dcat:bbox` | Rectangle d'emprise | Rectangle d'emprise (BBox), au format textuel WKT. |  |
| `dcat:distribution / dcat:accessService / dct:spatial / dcat:centroid` | Centroïde | Localisant du centre géographique des données, au format textuel WKT. |  |
| `dcat:distribution / dcat:accessService / dct:spatial / locn:geometry` | Géométrie | Emprise géométrique, au format textuel WKT. |  |
| `dcat:distribution / dcat:accessService / dcat:spatialResolutionInMeters` | Résolution spatiale en mètres | Résolution des données mises à disposition par le service, exprimée en mètres. |  |
| `dcat:distribution / dcat:accessService / dct:temporal` | Couverture temporelle | Période pour laquelle des données sont mises à disposition par le service. |  |
| `dcat:distribution / dcat:accessService / dct:temporal / dcat:startDate` | Date de début | None |  |
| `dcat:distribution / dcat:accessService / dct:temporal / dcat:endDate` | Date de fin | None |  |
| `dcat:distribution / dcat:accessService / dcat:temporalResolution` | Résolution temporelle | Résolution temporelle des données mises à disposition par le service. |  |
| `dcat:distribution / dct:rights` | Propriété intellectuelle | Mention rappelant les droits de propriété intellectuelle sur les données, à faire apparaître en cas de réutilisation de cette distribution des données. |  |
| `dcat:distribution / dct:rights / rdfs:label` | Mention | None |  |
| `dcat:distribution / dct:license` | Licence | Licence sous laquelle est publiée la distribution ou conditions d'utilisation de la distribution. | [Licences admises pour les informations publiques des administrations françaises](http://snum.scenari-community.org/Metadata/Vocabulaire/#CrpaAuthorizedLicense) |
| `dcat:distribution / dct:license / dct:type` | Type | None | [Types de licence (UE)](http://purl.org/adms/licencetype/1.1) |
| `dcat:distribution / dct:license / rdfs:label` | Termes | None |  |
| `dcat:distribution / dct:accessRights` | Conditions d'accès | Contraintes réglementaires limitant l'accès à la distribution. | [Restriction d'accès public INSPIRE (UE)](http://inspire.ec.europa.eu/metadata-codelist/LimitationsOnPublicAccess), [Droits d'accès (UE)](http://publications.europa.eu/resource/authority/access-right), [Restrictions d'accès en application du Code des relations entre le public et l'administration](http://snum.scenari-community.org/Metadata/Vocabulaire/#CrpaAccessLimitations) |
| `dcat:distribution / dct:accessRights / rdfs:label` | Mention | None |  |
| `dcat:landingPage` | Page internet | URL de la fiche de métadonnées sur internet. |  |
| `foaf:page` | Ressource associée | Chemin d'une page internet ou d'un document en rapport avec les données. |  |
| `dct:language` | Langue des données | Langue·s des données. | [Langues (UE)](http://publications.europa.eu/resource/authority/language) |
| `snum:relevanceScore` | Score | Niveau de pertinance de la donnée. Plus le score est élevé plus la donnée sera mise en avant dans les résultats de recherche. |  |
| `dct:type` | Type de jeu de données | Type de jeu de données. |  |
| `dct:identifier` | Identifiant interne | Identifiant du jeu de données, attribué automatiquement par Plume. |  |
| `snum:linkedRecord` | Fiche distante | Configuration d'import des métadonnées depuis une fiche de catalogue INSPIRE. |  |
| `snum:linkedRecord / dcat:endpointURL` | Service CSW | URL de base du service CSW, sans aucun paramètre. |  |
| `snum:linkedRecord / dct:identifier` | Identifiant de la fiche | Identifiant de la fiche de métadonnées (et non de la ressource). |  |

