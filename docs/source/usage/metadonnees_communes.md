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
| `dct:provenance` | Généalogie | Sources et méthodes mises en oeuvre pour produire les données. |  |
| `dct:provenance / rdfs:label` | Texte | None |  |
| `adms:versionNotes` | Note de version | Différences entre la version courante des données et les versions antérieures. |  |
| `dct:conformsTo` | Conforme à | Standard, schéma, référentiel... |  |
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
| `dcat:temporalResolution` | Résolution temporelle | Plus petite durée significative dans le contexte du jeu de données. |  |
| `dct:accessRights` | Conditions d'accès | None | [Restriction d'accès public INSPIRE (UE)](http://inspire.ec.europa.eu/metadata-codelist/LimitationsOnPublicAccess), [Droits d'accès (UE)](http://publications.europa.eu/resource/authority/access-right), [Restrictions d'accès en application du Code des relations entre le public et l'administration](http://snum.scenari-community.org/Metadata/Vocabulaire/#CrpaAccessLimitations) |
| `dct:accessRights / rdfs:label` | Mention | None |  |
| `dcat:contactPoint` | Point de contact | None |  |
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
| `dcat:distribution` | Distribution | None |  |
| `dcat:distribution / dcat:accessURL` | URL d'accès | None |  |
| `dcat:distribution / dct:issued` | Date de publication | None |  |
| `dcat:distribution / dct:rights` | Propriété intellectuelle | None |  |
| `dcat:distribution / dct:rights / rdfs:label` | Mention | None |  |
| `dcat:distribution / dct:license` | Licence | None | [Licences admises pour les informations publiques des administrations françaises](http://snum.scenari-community.org/Metadata/Vocabulaire/#CrpaAuthorizedLicense) |
| `dcat:distribution / dct:license / dct:type` | Type | None | [Types de licence (UE)](http://purl.org/adms/licencetype/1.1) |
| `dcat:distribution / dct:license / rdfs:label` | Termes | None |  |
| `dcat:landingPage` | Page internet | URL de la fiche de métadonnées sur internet. |  |
| `foaf:page` | Ressource associée | Chemin d'une page internet ou d'un document en rapport avec les données. |  |
| `dct:language` | Langue des données | None | [Langues (UE)](http://publications.europa.eu/resource/authority/language) |
| `snum:relevanceScore` | Score | plus le score est élevé plus la donnée est mise en avant dans les résultats de recherche. |  |
| `dct:type` | Type de jeu de données | None |  |
| `dct:identifier` | Identifiant interne | None |  |
| `snum:linkedRecord` | Fiche distante | Configuration d'import des métadonnées depuis une fiche de catalogue INSPIRE. |  |
| `snum:linkedRecord / snum:csw` | Service CSW | URL de base du service CSW, sans aucun paramètre. |  |
| `snum:linkedRecord / dct:identifier` | Identifiant de la fiche | Identifiant de la fiche de métadonnées (et non de la ressource). |  |

