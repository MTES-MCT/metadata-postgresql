# Conformité au profil GeoDCAT-AP

_Référence : [GeoDCAT-AP Version 2.0.0](https://semiceu.github.io/GeoDCAT-AP/releases/2.0.0)._

[Généralités](#généralités) • [Espace de nommage de Plume](#espace-de-nommage-de-plume) • [Types de valeurs littérales](#types-de-valeurs-littérales)

Classes : [Activité](#activité) • [Adresse (agent)](#adresse-agent) • [Adresse (entité)](#adresse-entité) • [Agent](#agent) • [Attribution](#attribution) • [Catalogue](#catalogue) • [Concept](#concept) • [Agent](#agent) • [Déclaration de droits](#déclaration-de-droits) • [Distribution](#distribution) • [Document](#document) • [Emplacement](#emplacement) • [Enregistrement du catalogue](#enregistrement-du-catalogue) • [Ensemble de concepts](#ensemble-de-concepts) • [Entité](#entité) • [Fiche de métadonnées liée](#fiche-de-métadonnées-liée) • [Fréquence](#fréquence) • [Généalogie](#généalogie) • [Identifiant](#identifiant) • [**Jeu de données**](#jeu-de-données) • [Licence](#licence) • [Mesure de qualité](#mesure-de-qualité) • [Métrique](#métrique) • [Période](#période) • [Relation](#relation) • [Ressource](#ressource) • [Service de données](#service-de-données) • [Somme de contrôle](#somme-de-contrôle) • [Standard](#standard) • [Système linguistique](#système-linguistique) • [Type de média](#type-de-média) • [Type de média ou extension](#type-de-média-ou-extension)

## Généralités

Les métadonnées RDF produites par Plume ont les spécificités suivantes :
- Si elles ne sont pas vides, elles contiennent un et un seul objet de classe [`dcat:Dataset`](#jeu-de-données).
- L'identifiant du `dcat:Dataset` (sujet de ses propriétés et rappelé en objet de la propriété `dct:identifier`) est un URN. Ex : `<urn:uuid:e0479f0f-c6f7-4127-87bc-137d34113a86> a dcat:Dataset`.
    Cet identifiant est généré par Plume lors de la première saisie de métadonnées sur l'objet PostgreSQL. Il est pérenne, sauf à ce que les métadonnées contenues dans le descriptif PostgreSQL soit détruites par une manipulation externes à Plume[^uuid-valide].
- Aucun IRI ne peut être sujet d'un triplet hormis l'identifiant du jeu de données. Ainsi, tous les autres sujets sont des noeuds anonymes.
    Concrètement, pour les propriétés pouvant admettre comme objets des IRI et telles que GeoDCAT-AP définit des propriétés explicites pour la classe de l'objet, l'utilisateur de Plume aura la possibilité de choisir entre renseigner un IRI sans aucune propriété attachée (soit en saisie libre, soit choisi dans un thésaurus), ou renseigner manuellement les propriétés attachées sans saisir d'IRI. Le sujet des propriétés sera alors un noeud anonyme. Ceci concerne par exemple la propriété `dct:license` et ses objets `dct:LicenseDocument`.
- Avec Plume, les propriétés sont identifiées par leur IRI. Dès lors, il n'est pas possible de distinguer des propriétés différentes rattachées à un même IRI comme le fait GeoDCAT-AP avec par exemple les propriétés des services de données ([`dcat:DataService`](#service-de-données)) *service category*, *service type* et *type*, toutes trois correspondant à l'IRI `dct:type`, ou encore les propriétés *conforms to* et *reference system* des jeux de données (`dcat:Dataset`), dont l'IRI est dans les deux cas `dct:conformsTo`.
- Plume ne permet pas de choisir entre plusieurs types de valeur littérale pour une propriété donnée. Dès lors, toutes les géométries sont exprimées comme `gsp:wktLiteral` (alors que GeoDCAT-AP admet aussi le type `gsp:gmlLiteral`) et toutes les dates soit comme `xsd:date` soit comme `xsd:dateTime`, alors que GeoDCAT-AP permet en principe de mélanger les deux pour une même propriété. Plus généralement, lorsque Plume reçoit une valeur qui n'est pas du type attendu, il tentera de la convertir et, en cas d'échec, l'effacera[^validation].
- De même, la classe de l'objet d'une propriété est fixe et unique avec Plume. Lorsque l'agent est une organisation, GeoDCAT-AP recommande l'usage des classes `org:Organization`, `org:OrganizationalUnit` et `org:FormalOrganization` de l'[Ontologie des organisations VOCAB-ORG](https://www.w3.org/TR/vocab-org/) au lieu de `foaf:Agent`, mais Plume en reste à [`foaf:Agent`](#agent). De même, Plume utilise la classe [`vcard:Kind`](#entité) et non ses sous-classes `vcard:Individual`, `vcard:Organization`, `vcard:Location` et `vcard:Group` pour représenter les entités. Ces sous-classes seront toutefois reconnues à l'import, et Plume leur substituera `foaf:Agent` ou `vcard:Kind` selon le cas.
- Plume tolère qu'une propriété supposée n'admettre qu'une seule valeur en ait *de facto* plusieurs. L'utilisateur les verra dans l'interface, pourra les modifier ou les supprimer, mais pas en ajouter d'autres (pas de bouton +). Elles sont sauvegardées normalement.

[^uuid-valide]: Plume vérifie aussi que l'identifiant est un UUID valide. S'il avait été corrompu (là encore nécessairement par une manipulation externe à Plume), il serait remplacé à la première sauvegarde dans l'interface de saisie de Plume.

[^validation]: Ce mécanisme de validation est mise en oeuvre par la méthode `update_value` de la classe `plume.rdf.widgetsdict.WidgetsDict` lors de la [sauvegarde des métadonnées par l'utilisateur](./actions_generales.md#sauvegarde) et non au moment de l'import depuis une source externe. L'utilisateur a ainsi la possibilité de contrôler visuellement les valeurs.

Lorsque des métadonnées externes sont importées via les fonctionnalités de Plume, elles sont retraitées pour être conformes à ces règles ou deviennent conformes de fait compte tenu des mécanismes internes de Plume.

Les propriétés prévues par GeoDCAT-AP mais non gérées par Plume, les propriétés de GeoDCAT-AP sur lesquelles des modifications ont été opérées, et les propriétés ajoutées par Plume sont listées dans la suite.

## Espace de nommage de Plume

Les propriétés et classes ajoutées par Plume utilisent l'espace de nommage `http://registre.data.developpement-durable.gouv.fr/plume/`, représenté par le préfixe `plume`.

```turtle

@prefix plume: <http://registre.data.developpement-durable.gouv.fr/plume/> .

```

## Types de valeurs littérales

Parmi les types explicitement cités par GeoDCAT-AP (pour les classes et propriétés prises en charges par Plume), seul le type `gsp:gmlLiteral` n'est pas reconnu par Plume. En cas d'import de métadonnées externes, les éventuelles valeurs de ce type seront traitées comme `xsd:string` et aucune des fonctionnalités permettant d'interagir avec les géométries ne sera disponible.

Les types suivants sont pris en charge sans limitation : `xsd:string`, `rdf:langString` (`xsd:string` avec langue), `xsd:integer`, `xsd:decimal`, `xsd:boolean`.

Les types suivants sont gérés par Plume, mais avec quelques limites :

| Type | Limites |
| --- | --- |
| `xsd:duration` | Plume tronque les durées en ne conservant que la valeur pour la plus grande unité. Par exemple `'P1DT2H'` (un jour et deux heures) deviendra `'P1D'` (1 jour). |
| `xsd:date` | Les fuseaux horaires ne sont pas pris en charge à ce stade. Si présents, Plume les retire. |
| `xsd:dateTime` | Les fuseaux horaires et les millisecondes ne sont pas pris en charge à ce stade. Si présents, Plume les retire. |
| `xsd:time` | Les fuseaux horaires et les millisecondes ne sont pas pris en charge à ce stade. Si présents, Plume les retire. |
| `gsp:wktLiteral` | Dans l'hypothèse où elle aurait été demandée pour la catégorie de métadonnées considérée, la fonctionnalité de visualisation des géométries sera désactivée si la géométrie n'est pas de type `POINT`, `LINESTRING`, `POLYGON` ou `CIRCULARSTRING`. |

D'une manière général, toute valeur d'un type non listé ci-avant sera considérée comme de type `xsd:string`.

## Classes

### Activité

_Classe `prov:Activity`._

Cette classe n'est pas prise en charge.

### Adresse (agent)

_Classe `locn:Address`._

Cette classe n'est pas prise en charge.

### Adresse (entité)

_Classe `vcard:Address`._

Cette classe n'est pas prise en charge.

### Agent

_Classe `foaf:Agent`._

Les propriétés suivantes ne sont pas prises en charge par Plume :

| Propriété | IRI | Commentaire |
| --- | --- | --- |
| *address* | `locn:address` | |
| *affiliation* | `org:memberOf` | GeoDCAT-AP prévoit que cette propriété ait des objets de classe `org:Organization` - donc pas une valeur littérale comme le `vcard:organization-name` de [`vcard:Kind`](#entité) - et sans associer explicitement de propriétés à cette classe, même si on peut supposer qu'il s'agirait des mêmes que `foaf:Agent`. |

Les propriétés suivantes sont modifiées par Plume :

| Propriété | IRI | Nature de la modification | Commentaire |
| --- | --- | --- | --- |
| *email* | `foaf:mbox` | Changement de cardinalité. Avant : `0..1`. Après : `0..n`. | |
| *phone* | `foaf:phone` | Changement de cardinalité. Avant : `0..1`. Après : `0..n`. | |

### Attribution

_Classe `prov:Attribution`._

Cette classe n'est pas prise en charge.

### Catalogue

_Classe `dcat:Catalog`._

Cette classe n'est pas prise en charge.

### Concept

_Classe `skos:Concept`._

Les propriétés de cette classe ne sont pas supposées être saisies manuellement. Elles sont récupérées par Plume dans un thésaurus (fichier [vocabulary.ttl](../../plume/rdf/data/vocabulary.ttl)). Pour chaque concept, celui-ci présente obligatoirement les propriétés *category scheme* (`skos:inScheme`) et *preferred label* (`skos:prefLabel`), avec le plus souvent une valeur en anglais et une valeur en français. Les traductions françaises ont été ajoutées systématiquement lorsque le thésaurus d'origine n'en contenait pas.

Des propriétés supplémentaires peuvent être disponibles pour certains concepts, dont une seule utilisée à ce stade par Plume : `foaf:page`. Celle-ci fournit l'URL d'une page web pertinente pour le concept. En mode lecture, la métadonnée portera un hyperlien pointant sur cette page ou, à défaut, sur l'IRI du concept.

Seul l'IRI du concept est enregistré dans les métadonnées.

### Déclaration de droits

_Classe `dct:RightsStatement`._

Cette classe est prise en charge dans les formes prévues par GeoDCAT-AP.

### Distribution

_Classe `dcat:Distribution`._

Les propriétés suivantes ne sont pas prises en charge par Plume :

| Propriété | IRI | Commentaire |
| --- | --- | --- |
| *media type* | `dcat:mediaType` | La différence avec le format (`dct:format`) est difficile à rendre intelligible dans le contexte de Plume. Pour les données mises à disposition via des services (incluant les flux Atom, etc.), on exprimera plutôt ces informations via les propriétés du service, lui-même introduit par `dcat:accessService`. Si cette propriété est présente dans des métadonnées importées, elle est mappée vers `dct:format`. |
| *checksum* | `spdx:checksum` | Pourrait être ajouté ultérieurement si finalement utile. |
| *encoding* | `cnt:characterEncoding` | |
| *has policy* | `odrl:hasPolicy` | |
| *spatial resolution as text* | `rdfs:comment` | La résolution est gérée uniquement avec `dcat:spatialResolutionInMeters` et `dqv:hasQualityMeasurement`. |

Les propriétés suivantes sont modifiées par Plume :

| Propriété | IRI | Nature de la modification | Commentaire |
| --- | --- | --- | --- |
| *access URL* | `dcat:accessURL` | Non obligatoire. | |
| *access rights* | `dct:accessRights` | Ajout d'une source de vocabulaire contrôlé et changement de cardinalité. Avant : `0..1`. Après : `0..n`. | Nécessité de pouvoir exprimer les limitations d'accès en référence à plusieurs réglementations différentes (INSPIRE, code des relations entre le public et l'administration...). Outre le [thésaurus INSPIRE](http://inspire.ec.europa.eu/metadata-codelist/LimitationsOnPublicAccess) et celui du [registre EU](https://op.europa.eu/s/vR3k), Plume propose un thésaurus maison [`CrpaAccessLimitations`](http://registre.data.developpement-durable.gouv.fr/plume/CrpaAccessLimitations) qui référence les limitations d'accès prévues par le code des relations entre le public et l'administration. |
| *compression format* | `dcat:compressFormat` | Changement de source de vocabulaire contrôlé. | Utilisation du même thésaurus du [registre européen](https://op.europa.eu/s/vNbR) que pour la propriété `dct:format` (qui a le mérite d'exister en RDF et d'avoir des libellés plus intelligibles que le registre IANA). | 
| *license* | `dct:license` | Ajout de deux sources de vocabulaire contrôlé. | Pour la version IRI de la propriété, Plume propose le thésaurus du [registre EU](https://op.europa.eu/s/vM9L) et un thésaurus maison [`CrpaAuthorizedLicense`](http://registre.data.developpement-durable.gouv.fr/plume/CrpaAuthorizedLicense) contenant les URI SPDX des licences autorisées pour la publication des données des administrations françaises. |
| *packaging format* | `dcat:packageFormat` | Changement de source de vocabulaire contrôlé. | Idem *compression format*. Utilisation du même thésaurus du [registre européen](https://op.europa.eu/s/vNbR) que pour la propriété `dct:format` (qui a le mérite d'exister en RDF et d'avoir des libellés plus intelligibles que le registre IANA). |
| *reference system* | `dct:conformsTo` | Simplification d'une source de vocabulaire contrôlé. | Le thésaurus `<http://www.opengis.net/def/crs/EPSG/0>` est limité aux projections officielles française + projection web Pseudo-Mercator (EPSG 3857). Pour les autres référentiels, il faudra passer par de la saisie manuelle. |
| *release date* | `dct:issued` | Restriction des types littéraux acceptés. Avant : `rdfs:Literal typed as xsd:date or xsd:dateTime`. Après : `rdfs:Literal typed as xsd:date`. | Il reste possible pour l'administrateur de redéfinir le type en `rdfs:Literal typed as xsd:dateTime` pour certains de ses [modèles locaux](./modeles_de_formulaires.md).  |
| *status* | `adms:status` | Changement de source de vocabulaire contrôlé. | Utilisation du thésaurus dédié du [registre européen](https://op.europa.eu/s/vR2T). La valeur *discontinued* (traduite en *abandonné*) est incluse bien que non listée par GeoDCAT-AP, car elle apporte une nuance intéressante par rapport à *deprecated* / *obsolète* (une distribution peut ne plus être maintenue sans que les données ait perdu leur valeur) et *withdrawn* / *retiré* (une distribution peut ne plus être maintenue sans qu'il y ait de volonté de la rendre inaccessible). |
| *update / modification date* | `dct:modified` | Restriction des types littéraux acceptés. Avant : `rdfs:Literal typed as xsd:date or xsd:dateTime`. Après : `rdfs:Literal typed as xsd:date`. | Il reste possible pour l'administrateur de redéfinir le type en `rdfs:Literal typed as xsd:dateTime` pour certains de ses [modèles locaux](./modeles_de_formulaires.md). |

Les propriétés suivantes sont ajoutées par Plume :

| IRI | Classe de l'objet | Cardinalité | Description |
| --- | --- | --- | --- |
| `dct:type` | `skos:Concept` | `0..1` | Type de distribution. Bizaremment non présent dans DCAT-AP et GeoDCAT-AP alors qu'il existe un [thésaurus dédié](https://op.europa.eu/s/vNbJ) dans le registre européen. |

### Document

_Classe `foaf:Document`._

Plume n'associe aucune propriété à cette classe. Il est attendu de l'utilisateur qu'il saisisse une URL, qui tiendra lieu d'IRI et sera la seule information relative au document sauvegardée dans les métadonnées.

### Emplacement

_Classe `dct:Location`._

Les propriétés suivantes sont modifiées par Plume :

| Propriété | IRI | Nature de la modification | Commentaire |
| --- | --- | --- | --- |
| *bounding box* | `dcat:bbox` | Restriction des types littéraux acceptés. Avant : `rdfs:Literal typed as gsp:wktLiteral or gsp:gmlLiteral`. Après : `rdfs:Literal typed as gsp:wktLiteral`. |  |
| *centroid* | `dcat:centroid` | Restriction des types littéraux acceptés. Avant : `rdfs:Literal typed as gsp:wktLiteral or gsp:gmlLiteral`. Après : `rdfs:Literal typed as gsp:wktLiteral`. |  |
| *gazetteer* | `skos:inScheme` | Ajout d'une source de vocabulaire contrôlé. | Thésaurus maison [`InseeGeoIndex`](http://registre.data.developpement-durable.gouv.fr/plume/InseeGeoIndex), basé sur le [registre de l'INSEE](http://id.insee.fr) qui répertorie les divisions administratives. |
| *geographic name* | `skos:prefLabel` | Changement de cardinalité. Avant : `1..n`. Après : `0..n`. | Rendre le nom obligatoire est discutable quand l'emplacement est un rectangle d'emprise ou autre géométrie calculée à partir des données (il pourrait d'ailleurs s'agir d'une coquille dans GeoDCAT-AP, considérant que les propriétés obligatoires sont usuellement listées à part). |
| *geometry* | `locn:geometry` | Restriction des types littéraux acceptés. Avant : `rdfs:Literal typed as gsp:wktLiteral or gsp:gmlLiteral`. Après : `rdfs:Literal typed as gsp:wktLiteral`. |  |

### Enregistrement du catalogue

_Classe `dcat:CatalogRecord`._

Dans le contexte de Plume, la classe `dcat:CatalogRecord` sert exclusivement à renseigner les métadonnées sur les métadonnées. Elle est introduite par la propriété `foaf:isPrimaryTopicOf` dans la description d'un `dcat:Dataset`, et le sujet du triplet `[] a dcat:CatalogRecord` est toujours un noeud anonyme.

Pour l'heure, la seule propriété de cette classe qui soit prise en charge par Plume est *update / modification date* - `dct:modified` -, que Plume renseigne automatiquement à chaque sauvegarde.

### Ensemble de concepts

_Classe `skos:ConceptScheme`._

Comme pour la classe `skos:Concept`, Plume fait appel à cette classe dans le cadre de son système de gestion des vocabulaires contrôlés. Aucun objet de cette classe n'est jamais enregistré dans les métadonnées. Ils apparaissent uniquement dans le fichier [vocabulary.ttl](../../plume/rdf/data/vocabulary.ttl), avec pour seule propriété `skos:prefLabel` (et non `dct:title` comme dans GeoDCAT-AP), qui fournit le libellé de l'ensemble, généralement en anglais et en français.

### Entité

_Classe `vcard:Kind`._

Les propriétés suivantes ne sont pas prises en charge par Plume :

| Propriété | IRI | Commentaire |
| --- | --- | --- |
| *address* | `vcard:hasAddress` | |

Les propriétés suivantes sont modifiées par Plume :

| Propriété | IRI | Nature de la modification | Commentaire |
| --- | --- | --- | --- |
| *email* | `vcard:hasEmail` | Changement de cardinalité. Avant : `0..1`. Après : `0..n`. | |
| *phone* | `vcard:hasTelephone` | Changement de cardinalité. Avant : `0..1`. Après : `0..n`. | |

### Fiche de métadonnées liée

_Classe `plume:LinkedRecord`._

Cette classe est ajoutée par Plume. Elle représente une fiche de métadonnées distante avec laquelle la fiche locale doit être régulièrement synchronisée. À ce stade ne sont prises en charge que les métadonnées ISO 19115 exposées par des services CSW. Les métadonnées n'ont pas pour objet de décrire la fiche mais seulement de mémoriser les informations nécessaires à Plume pour l'importer.

Propriétés :

| IRI | Classe de l'objet | Cardinalité | Description |
| --- | --- | --- | --- |
| `dcat:endpointURL` | [`rdfs:Resource`](#ressource) | `0..1` | URL de base du service CSW, sans aucun paramètre. |
| `dct:identifier` | `rdfs:Literal type as xsd:string` | `0..1` | Identifiant de la fiche de métadonnées. |

### Fréquence

_Classe `dct:Frequency`._

Cette classe est prise en charge selon les mêmes modalités que [`skos:Concept`](#concept).

### Généalogie

_Classe `dct:ProvenanceStatement`._

Cette classe est prise en charge dans les formes prévues par GeoDCAT-AP.

### Identifiant

_Classe `adms:Identifier`._

Cette classe n'est pas prise en charge.

### Jeu de données

_Classe `dcat:Dataset`._

Les propriétés suivantes ne sont pas prises en charge par Plume :

| Propriété | IRI | Commentaire |
| --- | --- | --- |
| *has version* | `dct:hasVersion` | Relations entre jeux de données non prises en charge par Plume v1. |
| *is version of* | `dct:isVersionOf` | Relations entre jeux de données non prises en charge par Plume v1. |
| *other identifier* | `adms:identifier` | |
| *qualified attribution* | `dcat:qualifiedAttribution` | Pour l'heure, Plume implémente uniquement la méthode de saisie des organisations responsables préconisée par DCAT, c'est-à-dire via les propriétés dédiées à chaque rôle (`dct:creator`, `dct:publisher`, etc.). |
| *qualified relation* | `dcat:qualifiedRelation` | Relations entre jeux de données non prises en charge par Plume v1. |
| *sample* | `adms:sample` | A priori inutile dans le contexte de Plume. |
| *source* | `dct:source` | Relations entre jeux de données non prises en charge par Plume v1. |
| *spatial resolution as text* | `rdfs:comment` | La résolution est gérée uniquement avec `dcat:spatialResolutionInMeters` et `dqv:hasQualityMeasurement` (ainsi que `dct:provenance` s'il est besoin d'ajouter des commentaires). |
| *was generated by* | `prov:wasGeneratedBy` | |
| *was used by* | `prov:wasUsedBy` | |
| *topic category* | `dct:subject` | À l'import, mappé vers `dcat:theme` qui - par souci de simplicité - est donc utilisé pour toutes les nomenclatures thématiques. |

Les propriétés suivantes sont modifiées par Plume :

| Propriété | IRI | Nature de la modification | Commentaire |
| --- | --- | --- | --- |
| *access rights* | `dct:accessRights` | Ajout d'une source de vocabulaire contrôlé et changement de cardinalité. Avant : `0..1`. Après : `0..n`. | Nécessité de pouvoir exprimer les limitations d'accès en référence à plusieurs réglementations différentes (INSPIRE, code des relations entre le public et l'administration...). Outre le [thésaurus INSPIRE](http://inspire.ec.europa.eu/metadata-codelist/LimitationsOnPublicAccess) et celui du [registre EU](https://op.europa.eu/s/vR3k), Plume propose un thésaurus maison [`CrpaAccessLimitations`](http://registre.data.developpement-durable.gouv.fr/plume/CrpaAccessLimitations) qui référence les limitations d'accès prévues par le code des relations entre le public et l'administration. |
| *creation date* | `dct:created` | Restriction des types littéraux acceptés. Avant : `rdfs:Literal typed as xsd:date or xsd:dateTime`. Après : `rdfs:Literal typed as xsd:date`. | Il reste possible pour l'administrateur de redéfinir le type en `rdfs:Literal typed as xsd:dateTime` pour certains de ses [modèles locaux](./modeles_de_formulaires.md). |
| *identifier* | `dct:identifier` | Verrouillé. | Avec Plume l'identifiant présenté dans `dct:identifier` est toujours l'IRI du `dcat:Dataset`. Plume s'en assure à chaque chargement de la fiche de métadonnées. |
| *reference system* | `dct:conformsTo` | Simplification d'une source de vocabulaire contrôlé. | Le thésaurus `<http://www.opengis.net/def/crs/EPSG/0>` est limité aux projections officielles française + projection web Pseudo-Mercator (EPSG 3857) et EPSG 4326. Pour les autres référentiels, il faudra passer par de la saisie manuelle. |
| *release date* | `dct:issued` | Restriction des types littéraux acceptés. Avant : `rdfs:Literal typed as xsd:date or xsd:dateTime`. Après : `rdfs:Literal typed as xsd:date`. | Il reste possible pour l'administrateur de redéfinir le type en `rdfs:Literal typed as xsd:dateTime` pour certains de ses [modèles locaux](./modeles_de_formulaires.md). |
| *type* | `dct:type` | Simplification d'une source de vocabulaire contrôlé, suppression d'une autre. | Le registre INSPIRE des types de ressources n'est pas utilisé, car seule sa valeur `'Spatial data set'` aurait un sens pour une relation PostgreSQL. Le [registre EU](https://op.europa.eu/s/vM9N) est expurgé de quelques valeurs difficiles à rendre intelligibles des utilisateurs de Plume et qui ne sont de toute façon pas susceptibles d'être utilisées pour des relations PostgreSQL. |
| *update / modification date* | `dct:modified` | Restriction des types littéraux acceptés. Avant : `rdfs:Literal typed as xsd:date or xsd:dateTime`. Après : `rdfs:Literal typed as xsd:date`. | Il reste possible pour l'administrateur de redéfinir le type en `rdfs:Literal typed as xsd:dateTime` pour certains de ses [modèles locaux](./modeles_de_formulaires.md). |

Les propriétés suivantes sont ajoutées par Plume :

| IRI | Classe de l'objet | Cardinalité | Description |
| --- | --- | --- | --- |
| `foaf:isPrimaryTopicOf` | [`dcat:CatalogRecord`](#enregistrement-du-catalogue) | `1..1` | Métadonnées sur les métadonnées. Cette propriété est gérée automatiquement par Plume. |
| `plume:isExternal` | `rdfs:Literal typed as xsd:boolean` | `0..1` | Ce jeu de données est-il la reproduction de données produites par un tiers ? Cette propriété permet de distinguer immédiatement les données externes qui, dans le contexte de Plume, pourront se voir appliquer des modèles de formulaires spécifiques. |
| `plume:relevanceScore` | `rdfs:Literal typed as xsd:integer` | `0..1` | Niveau de pertinence de la donnée. Cette propriété anticipe sur de futures fonctionnalités de recherche qui mettront davantage en évidence les jeux de données avec un score élevé dans les listes de résultats. |

### Licence

_Classe `dct:LicenseDocument`._

Cette classe est prise en charge dans les formes prévues par GeoDCAT-AP.

### Mesure de qualité

_Classe `dqv:QualityMeasurement`._

Les propriétés suivantes sont modifiées par Plume :

| Propriété | IRI | Nature de la modification | Commentaire |
| --- | --- | --- | --- |
| *unit of measure* | `sdmx-attribute:unitMeasure` | Ajout d'une source de vocabulaire contrôlé. | Plume permet l'usage du thésaurus des unités de mesure du [registre européen](https://op.europa.eu/s/yGXa), qui est plus retreint que le vocabulaire QUDT, mais a l'intérêt de proposer des traductions françaises. |

### Métrique

_Classe `dqv:Metric`._

Plume ne permet pas aux utilisateurs de modifier les instances de cette classe, qui sont gérées comme les termes d'un vobulaire contrôlé ([GeoDCATMetric](https://registre.data.developpement-durable.gouv.fr/plume/GeoDCATMetric)).

### Période

_Classe `dct:PeriodOfTime`._

Les propriétés suivantes sont modifiées par Plume :

| Propriété | IRI | Nature de la modification | Commentaire |
| --- | --- | --- | --- |
| *end date* | `dcat:endDate` | Restriction des types littéraux acceptés. Avant : `rdfs:Literal typed as xsd:date or xsd:dateTime`. Après : `rdfs:Literal typed as xsd:date`. | Il reste possible pour l'administrateur de redéfinir le type en `rdfs:Literal typed as xsd:dateTime` pour certains de ses [modèles locaux](./modeles_de_formulaires.md). |
| *start date* | `dcat:startDate` | Restriction des types littéraux acceptés. Avant : `rdfs:Literal typed as xsd:date or xsd:dateTime`. Après : `rdfs:Literal typed as xsd:date`. | Il reste possible pour l'administrateur de redéfinir le type en `rdfs:Literal typed as xsd:dateTime` pour certains de ses [modèles locaux](./modeles_de_formulaires.md). |

### Relation

_Classe `dcat:Relationship`._

Cette classe n'est pas prise en charge.

### Ressource

_Classe `rdfs:Resource`._

GeoDCAT-AP n'associe explicitement aucune propriété à cette classe. De la même façon, Plume propose à l'utilisateur de saisir des URL pour les propriétés qui ont des valeurs de ce type et traite lesdites URL comme des IRI.

### Service de données

_Classe `dcat:DataService`._

Avec Plume, des objets de classe `dcat:DataService` peuvent être saisis en objet de la propriété `dcat:accessService` des distributions. La vocation primaire de Plume n'est toutefois pas la documentation des services, et encore moins leur catalogage. Ainsi il a été fait le choix de limiter les propriétés disponibles pour décrire ces objets, en éliminant celles qui n'aideront pas l'utilisateur à comprendre sous quelles modalités le service met à disposition les données qui l'intéressent.

Les propriétés suivantes ne sont pas prises en charge par Plume :

| Propriété | IRI | Commentaire |
| --- | --- | --- |
| *serves dataset* | `dcat:servesDataset` | Le service est l'objet d'une propriété `dcat:accessService` d'un objet `dcat:Distribution`, lui-même objet de la propriété `dcat:distribution` d'un jeu de données. Avoir une propriété du service prenant en objet ce même jeu de données n'apporte rien. Quant à lister tous les jeux de données mis à disposition par le service, cela paraît inutilement fastidieux dans le contexte d'un patrimoine local. |
| *creation date* | `dct:created` | Information difficile à obtenir et sans intérêt dans le contexte de Plume. |
| *identifier* | `dct:identifier` | Plume n'ayant pas vocation à cataloguer les services, il ne leur attribue pas d'identifiant. |
| *qualified attribution* | `prov:qualifiedAttribution` | Sans grand intérêt pour les services dans le contexte de Plume. De plus, comme pour les jeux de données, on privilégie l'usage des propriétés qui définissent directement des organisations pour chaque rôle (comme recommandé par GeoDCAT-AP). |
| *service category* | `dct:type` | Le registre INSPIRE associé à cette propriété - [Classification des services de données géographiques](https://inspire.ec.europa.eu/metadata-codelist/SpatialDataServiceCategory) - contient une longue liste de catégories de services dont l'objet n'est le plus souvent pas de mettre à diposition des données. Si cette information peut être utile pour décrire les services en général, elle semble sans grand intérêt dans le contexte de Plume, où les seuls services présentés sont ceux qui donnent accès à des distributions. _NB : Il reste bien une propriété `dct:type` pour les services, mais sa [source de vocabulaire contrôlé](http://publications.europa.eu/resource/authority/data-service-type) est issue du registre UE._ |
| *service type* | `dct:type` | Le registre INSPIRE associé à cette propriété - [Type de service de données géographiques](https://inspire.ec.europa.eu/metadata-codelist/SpatialDataServiceType) - propose une catégorisation très vague, sans intérêt dans le contexte de Plume. _NB : Il reste bien une propriété `dct:type` pour les services, mais sa source de vocabulaire contrôlé est issue du [registre UE](https://op.europa.eu/s/vM9M)._ |
| *spatial resolution as text* | `rdfs:comment` | La résolution est gérée uniquement avec `dcat:spatialResolutionInMeters` et `dqv:hasQualityMeasurement`. |
| *theme / category* | `dcat:theme` | Catégorisation sans intérêt dans le contexte de Plume. |
| *topic category* | `dct:subject` | Catégorisation sans intérêt dans le contexte de Plume. |
| *update / modification date* | `dct:modified` | Information difficile à obtenir et sans intérêt dans le contexte de Plume. |
| *was used by* | `prov:wasUsedBy` | |
| *custodian* | `geodcat:custodian` | Propriété difficile à définir et de peu d'intérêt dans le contexte de Plume. |
| *distributor* | `geodcat:distributor` | Propriété difficile à définir et de peu d'intérêt dans le contexte de Plume. |
| *originator* | `geodcat:originator` | Propriété difficile à définir et de peu d'intérêt dans le contexte de Plume. |
| *principal investigator* | `geodcat:principalInvestigator` | Propriété difficile à définir et de peu d'intérêt dans le contexte de Plume. |
| *processor* | `geodcat:processor` | Propriété difficile à définir et de peu d'intérêt dans le contexte de Plume. |
| *resource provider* | `geodcat:resourceProvider` | Propriété difficile à définir et de peu d'intérêt dans le contexte de Plume. |
| *user* | `geodcat:user` | Propriété de peu d'intérêt dans le contexte de Plume. |

Les propriétés suivantes sont modifiées par Plume :

| Propriété | IRI | Nature de la modification | Commentaire |
| --- | --- | --- | --- |
| *access rights* | `dct:accessRights` | Ajout d'une source de vocabulaire contrôlé et changement de cardinalité. Avant : `0..1`. Après : `0..n`. | Nécessité de pouvoir exprimer les limitations d'accès en référence à plusieurs réglementations différentes (INSPIRE, code des relations entre le public et l'administration...). Outre le [thésaurus INSPIRE](http://inspire.ec.europa.eu/metadata-codelist/LimitationsOnPublicAccess) et celui du [registre EU](https://op.europa.eu/s/vR3k), Plume propose un thésaurus maison [`CrpaAccessLimitations`](http://registre.data.developpement-durable.gouv.fr/plume/CrpaAccessLimitations) qui référence les limitations d'accès prévues par le code des relations entre le public et l'administration. |
| *license* | `dct:license` | Ajout de deux sources de vocabulaire contrôlé. | Pour la version IRI de la propriété, Plume propose le thésaurus du [registre EU](https://op.europa.eu/s/vM9L) et un thésaurus maison [`CrpaAuthorizedLicense`](http://registre.data.developpement-durable.gouv.fr/plume/CrpaAuthorizedLicense) contenant les URI SPDX des licences autorisées pour la publication des données des administrations françaises. |
| *conforms to* | `dct:conformsTo` | Ajout d'une source de vocabulaire contrôlé. | Pour la version IRI de la propriété, Plume propose un thésaurus maison [`DataServiceStandard`](http://registre.data.developpement-durable.gouv.fr/plume/DataServiceStandard) contenant les URI des principaux standards utilisés pour les services de données géographiques. Il inclut tous les concepts du [thésaurus des protocoles du registre INSPIRE](http://inspire.ec.europa.eu/metadata-codelist/ProtocolValue) (auquel il se substitue), en ajoutant un concept supplémentaire pour le standard OGC API Feature et des propriétés [`foaf:page`](#concept) pointant sur les standards à proprement parler. Par exemple, en mode lecture, l'utilisateur sera renvoyé vers https://www.ogc.org/standards/wms au lieu de l'IRI http://www.opengis.net/def/serviceType/ogc/wms s'il clique sur le standard WMS. |
| *reference system* | `dct:conformsTo` | Simplification d'une source de vocabulaire contrôlé. | Le thésaurus `<http://www.opengis.net/def/crs/EPSG/0>` est limité aux projections officielles française + projection web Pseudo-Mercator (EPSG 3857). Pour les autres référentiels, il faudra passer par de la saisie manuelle. |
| *release date* | `dct:issued` | Restriction des types littéraux acceptés. Avant : `rdfs:Literal typed as xsd:date or xsd:dateTime`. Après : `rdfs:Literal typed as xsd:date`. | Il reste possible pour l'administrateur de redéfinir le type en `rdfs:Literal typed as xsd:dateTime` pour certains de ses [modèles locaux](./modeles_de_formulaires.md). |
| *type* | `dct:type` | Changement de source de vocabulaire contrôlé. | Avec le registre INSPIRE, il s'agirait d'une propriété à valeur fixe (`<http://inspire.ec.europa.eu/metadata-codelist/ResourceType/service>`), redondante avec l'existence même d'un service de données, ce qui présente peu d'intérêt. Plume utilise à la place le [registre EU](https://op.europa.eu/s/vM9M). |

### Somme de contrôle

_Classe `spdx:Checksum`._

Cette classe n'est pas prise en charge.

### Standard

_Classe `dct:Standard`._

Les propriétés suivantes ne sont pas prises en charge par Plume :

| Propriété | IRI | Commentaire |
| --- | --- | --- |
| *type* | `dct:type` | Il n'existe pas de vocabulaire contrôlé à ce stade et l'approche évoquée par GeoDCAT-AP (à savoir lister ces deux IRI : http://inspire.ec.europa.eu/glossary/CRS et http://inspire.ec.europa.eu/glossary/TemporalReferenceSystem) n'apporte pas grand chose - on préférera encourager l'usage de la propriété `skos:inScheme` ou, mieux, l'utilisation des thésaurus plutôt que la saisie manuelle pour les propriétés `dct:conformsTo`. |

Les propriétés suivantes sont modifiées par Plume :

| Propriété | IRI | Nature de la modification | Commentaire |
| --- | --- | --- | --- |
| *creation date* | `dct:created` | Restriction des types littéraux acceptés. Avant : `rdfs:Literal typed as xsd:date or xsd:dateTime`. Après : `rdfs:Literal typed as xsd:date`. | Il reste possible pour l'administrateur de redéfinir le type en `rdfs:Literal typed as xsd:dateTime` pour certains de ses [modèles locaux](./modeles_de_formulaires.md). |
| *reference register* | `skos:inScheme` | Ajout d'une source de vocabulaire contrôlé. | Thésaurus maison [`StandardsRegister`](http://registre.data.developpement-durable.gouv.fr/plume/StandardsRegister), qui ne référence à date que le registre EPSG de l'OGC. |
| *release date* | `dct:issued` | Restriction des types littéraux acceptés. Avant : `rdfs:Literal typed as xsd:date or xsd:dateTime`. Après : `rdfs:Literal typed as xsd:date`. | Il reste possible pour l'administrateur de redéfinir le type en `rdfs:Literal typed as xsd:dateTime` pour certains de ses [modèles locaux](./modeles_de_formulaires.md). |
| *update / modification date* | `dct:modified` | Restriction des types littéraux acceptés. Avant : `rdfs:Literal typed as xsd:date or xsd:dateTime`. Après : `rdfs:Literal typed as xsd:date`. | Il reste possible pour l'administrateur de redéfinir le type en `rdfs:Literal typed as xsd:dateTime` pour certains de ses [modèles locaux](./modeles_de_formulaires.md). |

Les propriétés suivantes sont ajoutées par Plume :

| IRI | Classe de l'objet | Cardinalité | Description |
| --- | --- | --- | --- |
| `foaf:page` | [`foaf:Document`](#document) | `0..n` | Chemin d'accès au standard ou URL d'une page contenant des informations sur le standard. Considérant que la majorité des standards de données géographiques n'ont pas d'URI à ce jour, les référencer dans un thésaurus n'est pas envisageable. Les utilisateurs devront les saisir manuellement et qu'ils puissent malgré tout renseigner une URL d'accès paraît essentiel. |

### Système linguistique

_Classe `dct:LinguisticSystem`._

Cette classe est prise en charge selon les mêmes modalités que [`skos:Concept`](#concept).

### Type de média

_Classe `dct:MediaType`._

Cette classe est prise en charge dans les formes prévues par GeoDCAT-AP.

### Type de média ou extension

_Classe `dct:MediaTypeOrExtent`._

GeoDCAT-AP n'associe aucune propriété à cette classe. Plume ajoute une propriété `rdfs:label` pour la saisie manuelle, comme le fait déjà GeoDCAT-AP pour la classe [`dct:MediaType`](#type-de-média).

Les propriétés suivantes sont ajoutées par Plume :

| IRI | Classe de l'objet | Cardinalité | Description |
| --- | --- | --- | --- |
| `rdfs:label` | `rdfs:Literal typed as rdf:langString` | `0..n` (une valeur par langue) | Libellé du format. |
