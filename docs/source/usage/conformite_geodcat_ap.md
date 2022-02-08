# Conformité au profil GeoDCAT-AP

_Version : 2.0. Référence : https://semiceu.github.io/GeoDCAT-AP/releases/2.0.0_.

## Généralités

Les métadonnées RDF produites par Plume ont les spécificités suivantes :
- Si elles ne sont pas vides, elles contiennent un et un seul objet de classe `dcat:Dataset`.
- L'identifiant du `dcat:Dataset` (sujet de ses propriétés et rappelé en objet de la propriété `dct:identifier`) est un URN. Ex : `<urn:uuid:e0479f0f-c6f7-4127-87bc-137d34113a86> a dcat:Dataset`.
- Aucun IRI ne peut être sujet d'un triplet, hormis l'identifiant du jeu de données. Ainsi, tous les autres sujets sont des noeuds anonymes.
- Avec Plume, les propriétés sont identifiées par leur IRI. Dès lors, il n'est pas possible de distinguer des propriétés différentes rattachées à un même IRI comme le fait GeoDCAT-AP avec par exemple les propriétés des services de données (`dcat:DataService`) *service category*, *service type* et *type*, toutes trois correspondant à l'IRI `dct:type`, ou encore les propriétés *conforms to* et *reference system* des jeux de données (`dcat:Dataset`), dont l'IRI est dans les deux cas `dct:conformsTo`.

Lorsque des métadonnées externes sont importées via les fonctionnalités de Plume, elles sont retraitées pour être conformes à ces règles ou deviennent conformes de fait compte tenu des mécanismes internes de Plume.

Les propriétés prévues par GeoDCAT-AP mais non gérées par Plume, les propriétés de GeoDCAT-AP sur lesquelles des modifications ont été opérées, et les propriétés ajoutées par Plume sont listées dans la suite.

D'une manière générale, on pourra noter que, pour l'heure, Plume ne prend pas en charge toutes les propriétés visant à établir des relations entre jeux de données.

## Services de données

Les propriétés optionnelles suivantes ne sont pas prises en charge par Plume : 

| Propriété | URI | Commentaire |
| --- | --- | --- |
| *service category* | `dct:type` | Le registre INSPIRE associé à cette propriété - [Classification des services de données géographiques](https://inspire.ec.europa.eu/metadata-codelist/SpatialDataServiceCategory) - contient une longue liste de catégories de services dont l'objet n'est le plus souvent pas de mettre à diposition des données. Si cette information peut être utile pour décrire les services en général, elle semble sans grand intérêt dans le contexte de Plume, où les seuls services présentés sont ceux qui donnent accès à des distributions. |
| *spatial resolution* | `dqv:hasQualityMeasurement` | |
| *spatial resolution as text* | `rdfs:comment` | |
| *type* | `dct:type` | Il s'agirait d'une propriété à valeur fixe (`<http://inspire.ec.europa.eu/metadata-codelist/ResourceType/service>`), redondante avec l'existence même d'un service de données, ce qui présente peu d'intérêt. |

