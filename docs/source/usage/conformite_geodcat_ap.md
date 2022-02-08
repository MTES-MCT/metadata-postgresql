# Conformité au profil GeoDCAT-AP

_Version : 2.0. Référence : https://semiceu.github.io/GeoDCAT-AP/releases/2.0.0_.

## Généralités

Les métadonnées RDF produites par Plume ont les spécificités suivantes :
- Si elles ne sont pas vides, elles contiennent un et un seul objet de classe `dcat:Dataset`.
- L'identifiant du `dcat:Dataset` (sujet de ses propriétés et rappelé en objet de la propriété `dct:identifier`) est un URN. Ex : `<urn:uuid:e0479f0f-c6f7-4127-87bc-137d34113a86> a dcat:Dataset`.
    Cet identifiant est généré par Plume lors de la première saisie de métadonnées sur l'objet PostgreSQL. Il est pérenne, sauf à ce que les métadonnées contenues dans le descriptif PostgreSQL soit détruites par une manipulation externes à Plume[^uuid-valide].
- Aucun IRI ne peut être sujet d'un triplet hormis l'identifiant du jeu de données. Ainsi, tous les autres sujets sont des noeuds anonymes.
    Concrètement, pour les propriétés pouvant admettre comme objets des IRI et telles que GeoDCAT-AP définit des propriétés explicites pour la classe de l'objet, l'utilisateur de Plume aura la possibilité de choisir entre renseigner un IRI sans aucune propriété attachée (soit en saisie libre, soit choisi dans un thésaurus), ou renseigner manuellement les propriétés attachées sans saisir d'IRI. Le sujet des propriétés sera alors un noeud anonyme. Ceci concerne par exemple la propriété `dct:license` et ses objets `dct:LicenseDocument`.
- Avec Plume, les propriétés sont identifiées par leur IRI. Dès lors, il n'est pas possible de distinguer des propriétés différentes rattachées à un même IRI comme le fait GeoDCAT-AP avec par exemple les propriétés des services de données (`dcat:DataService`) *service category*, *service type* et *type*, toutes trois correspondant à l'IRI `dct:type`, ou encore les propriétés *conforms to* et *reference system* des jeux de données (`dcat:Dataset`), dont l'IRI est dans les deux cas `dct:conformsTo`.

[^uuid-valide]: Plume vérifie aussi que l'identifiant est un UUID valide. S'il avait été corrompu (là encore nécessairement par une manipulation externe à Plume), il serait remplacé à la première sauvegarde dans l'interface de saisie de Plume.

Lorsque des métadonnées externes sont importées via les fonctionnalités de Plume, elles sont retraitées pour être conformes à ces règles ou deviennent conformes de fait compte tenu des mécanismes internes de Plume.

Les propriétés prévues par GeoDCAT-AP mais non gérées par Plume, les propriétés de GeoDCAT-AP sur lesquelles des modifications ont été opérées, et les propriétés ajoutées par Plume sont listées dans la suite.

D'une manière générale, on pourra noter que, pour l'heure, Plume ne prend pas en charge toutes les propriétés visant à établir des relations entre jeux de données.

## Jeux de données

_Classe `dcat:Dataset`._

Les propriétés suivantes ne sont pas prises en charge par Plume :

| Propriété | IRI | Commentaire |
| --- | --- | --- |
| | | |

Les propriétés suivantes sont modifiées par Plume :

| Propriété | IRI | Nature de la modification | Commentaire |
| --- | --- | --- | --- |
| *access rights* | `dct:accessRights` | Changement de cardinalité. Avant : `0..1`. Après : `0..n`. | Nécessité de pouvoir exprimer les limitations d'accès en référence à plusieurs réglementations différentes (INSPIRE, code des relations entre le public et l'administration...). |

Les propriétés suivantes sont ajoutées par Plume :

| Propriété | IRI | Commentaire |
| --- | --- | --- |
| | | |

## Distributions

_Classe `dcat:Dataset`._

Les propriétés suivantes ne sont pas prises en charge par Plume :

| Propriété | IRI | Commentaire |
| --- | --- | --- |
| | | |

Les propriétés suivantes sont modifiées par Plume :

| Propriété | IRI | Nature de la modification | Commentaire |
| --- | --- | --- | --- |
| *access rights* | `dct:accessRights` | Changement de cardinalité. Avant : `0..1`. Après : `0..n`. | Nécessité de pouvoir exprimer les limitations d'accès en référence à plusieurs réglementations différentes (INSPIRE, code des relations entre le public et l'administration...). |
| *license* | `dct:license` | Ajout d'une source de vocabulaire contrôlé. | Pour la version IRI de la propriété, Plume propose un thésaurus maison contenant les URI SPDX des licences autorisées pour la publication des données des administrations françaises. |

Les propriétés suivantes sont ajoutées par Plume :

| Propriété | IRI | Commentaire |
| --- | --- | --- |
| | | |

## Services de données

_Classe `dcat:DataService`._

Avec Plume, des objets de classe `dcat:DataService` peuvent être saisis en objet de la propriété `dcat:accessService` des distributions. La vocation primaire de Plume n'est toutefois pas la documentation des services, et encore moins leur catalogage. Ainsi il a été fait le choix de limiter les propriétés disponibles pour décrire ces objets, en éliminant celles qui n'aideront pas l'utilisateur à comprendre sous quelles modalités le service met à disposition les données qui l'intéressent.

Les propriétés suivantes ne sont pas prises en charge par Plume :

| Propriété | IRI | Commentaire |
| --- | --- | --- |
| *serves dataset* | `dcat:servesDataset` | Le service est l'objet d'une propriété `dcat:accessService` d'un objet `dcat:Distribution`, lui-même objet de la propriété `dcat:distribution` d'un jeu de données. Avoir une propriété du service prenant en objet ce même jeu de données n'apporte rien. Quant à lister tous les jeux de données mis à disposition par le service, cela paraît inutilement fastidieux dans le contexte d'un patrimoine local. |
| *creation date* | `dct:created` | Information difficile à obtenir et sans intérêt dans le contexte de Plume. |
| *identifier* | `dct:identifier` | Plume n'ayant pas vocation à cataloguer les services, il ne leur attribue pas d'identifiant. |
| *qualified attribution* | `prov:qualifiedAttribution` | Sans grand intérêt pour les services dans le contexte de Plume. De plus, comme pour les jeux de données, on privilégie l'usage des propriétés qui définissent directement des organisations pour chaque rôle (comme recommandé par GeoDCAT-AP). |
| *service category* | `dct:type` | Le registre INSPIRE associé à cette propriété - [Classification des services de données géographiques](https://inspire.ec.europa.eu/metadata-codelist/SpatialDataServiceCategory) - contient une longue liste de catégories de services dont l'objet n'est le plus souvent pas de mettre à diposition des données. Si cette information peut être utile pour décrire les services en général, elle semble sans grand intérêt dans le contexte de Plume, où les seuls services présentés sont ceux qui donnent accès à des distributions. |
| *service type* | `dct:type` | Le registre INSPIRE associé à cette propriété - [Type de service de données géographiques](https://inspire.ec.europa.eu/metadata-codelist/SpatialDataServiceType) - propose une catégorisation très vague, sans intérêt dans le contexte de Plume. |
| *spatial resolution* | `dqv:hasQualityMeasurement` | |
| *spatial resolution as text* | `rdfs:comment` | |
| *theme / category* | `dcat:theme` | Catégorisation sans intérêt dans le contexte de Plume. |
| *topic category* | `dct:subject` | Catégorisation sans intérêt dans le contexte de Plume. |
| *type* | `dct:type` | Il s'agirait d'une propriété à valeur fixe (`<http://inspire.ec.europa.eu/metadata-codelist/ResourceType/service>`), redondante avec l'existence même d'un service de données, ce qui présente peu d'intérêt. |
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
| *access rights* | `dct:accessRights` | Changement de cardinalité. Avant : `0..1`. Après : `0..n`. | Nécessité de pouvoir exprimer les limitations d'accès en référence à plusieurs réglementations différentes (INSPIRE, code des relations entre le public et l'administration...). |
| *license* | `dct:license` | Ajout d'une source de vocabulaire contrôlé. | Pour la version IRI de la propriété, Plume propose un thésaurus maison contenant les URI SPDX des licences autorisées pour la publication des données des administrations françaises. |
| *conforms to* | `dct:conformsTo` | Ajout d'une source de vocabulaire contrôlé. | Pour la version IRI de la propriété, Plume propose un thésaurus maison contenant les URI des principaux standards utilisés pour les services de données géographiques. |

