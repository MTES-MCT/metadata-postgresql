# Outils d'aide à la saisie des géométries

Pour faciliter la saisie des métadonnées prenant pour valeur des géométries, le widget de saisie - `QLineEdit` ou `QTextEdit` selon les cas - est accompagné d'un bouton annexe proposant des outils de calcul à partir des données et/ou de saisie manuelle dans le canevas principal de QGIS.

Les modalités de création de ces boutons d'aide à la saisie des géométries sont décrites dans [Création d'un nouveau widget](./creation_widgets.md#widget-annexe--bouton-daide-à-la-saisie-des-géométries). La présente page précise l'effet des différentes fonctionnalités de saisie proposées, ainsi que quand et comment les mettre en oeuvre.

[Les actions possibles](#les-actions-possibles) • [Les calculs de géométries côté serveur](#les-calculs-de-géométries-côté-serveur) • [Les calculs et tracés manuels côté QGIS](#les-calculs-et-tracés-manuels-côté-qgis) • [Alimentation du formulaire](#alimentation-du-formulaire) • [Lecture des géométries pour la visualisation](#lecture-des-géométries-pour-la-visualisation)

## Les actions possibles

La nature des actions disponibles dépend de la propriété considérée.

Une action doit :
- apparaître dans le menu du `QToolButton` si le terme qui la représente est l'une des valeurs listées par la clé `'geo tools'` du dictionnaire interne du bouton.
- être active si ses conditions d'activation sont remplies (cf. ci-après).

*NB : Un même terme peut représenter plusieurs actions, qui seront réalisées par des méthodes différentes selon la situation.*

Le terme `'show'` est un cas particulier, la fonctionnalité de visualisation correspondante étant gérée directement par le `QToolButton` et non par une action dans son menu associé. Sa mise en oeuvre est principalement traitée dans [Création d'un nouveau widget](./creation_widgets.md#avec-fonctionnalité-de-visualisation).

### Actions sans condition d'activation

Dès lors qu'elles sont listées par `'geo tools'`, les actions suivantes n'auront jamais besoin d'être désactivées.

| Libellé de l'action | Terme inclus dans `'geo tools'` | Icône | Texte d'aide | Description de l'effet |
| --- | --- | --- | --- | --- |
| *Tracé manuel : point* | `'point'` |  ![point.svg](../../plume/icons/buttons/geo/point.svg) [point.svg](../../plume/icons/buttons/geo/point.svg) | *Saisie libre d'un point dans le canevas.* | Permet à l'utilisateur de cliquer sur un point dans le canevas et mémorise la géométrie dans les métadonnées. |
| *Tracé manuel : rectangle* | `'rectangle'` |  ![rectangle.svg](../../plume/icons/buttons/geo/rectangle.svg) [rectangle.svg](../../plume/icons/buttons/geo/rectangle.svg) | *Saisie libre d'un rectangle dans le canevas.* | Permet à l'utilisateur de tracer un rectangle dans le canevas et mémorise la géométrie dans les métadonnées. |
| *Tracé manuel : ligne* | `'linestring'` |  ![linestring.svg](../../plume/icons/buttons/geo/linestring.svg) [linestring.svg](../../plume/icons/buttons/geo/linestring.svg) | *Saisie libre d'une ligne dans le canevas.*  | Permet à l'utilisateur de tracer une ligne dans le canevas et mémorise la géométrie dans les métadonnées. |
| *Tracé manuel : polygone* | `'polygon'` |  ![polygon.svg](../../plume/icons/buttons/geo/polygon.svg) [polygon.svg](../../plume/icons/buttons/geo/polygon.svg) | *Saisie libre d'un polygone dans le canevas.* | Permet à l'utilisateur de tracer un polygone dans le canevas et mémorise la géométrie dans les métadonnées. |
| *Tracé manuel : cercle* | `'circle'` |  ![circle.svg](../../plume/icons/buttons/geo/circle.svg) [circle.svg](../../plume/icons/buttons/geo/circle.svg) | *Saisie libre d'un cercle dans le canevas.* | Permet à l'utilisateur de tracer un cercle dans le canevas et mémorise la géométrie dans les métadonnées. |

### Actions à activer uniquement si l'extension PostGIS est disponible sur la base

... et si la couche sélectionnée est géométrique.

| Libellé de l'action | Terme inclus dans `'geo tools'` | Texte d'aide | Description de l'effet |
| --- | --- | --- | --- |
| *Calcul du rectangle d'emprise (PostGIS)*  | `'bbox'` |  ![bbox_pg.svg](../../plume/icons/buttons/geo/bbox_pg.svg) [bbox_pg.svg](../../plume/icons/buttons/geo/bbox_pg.svg) | *Calcule le rectangle d'emprise à partir des données. Le calcul est réalisé côté serveur, via les fonctionnalités de PostGIS.* | Calcule l'emprise de la couche par des requêtes sur le serveur PostgreSQL et mémorise la géométrie dans les métadonnées. Cf. [Les calculs de géométries côté serveur](#les-calculs-de-géométries-côté-serveur). |
| *Calcul du centroïde (PostGIS)*  | `'centroid'` |  ![centroid_pg.svg](../../plume/icons/buttons/geo/centroid_pg.svg) [centroid_pg.svg](../../plume/icons/buttons/geo/centroid_pg.svg) | *Calcule le centre du rectangle d'emprise à partir des données.  Le calcul est réalisé côté serveur, via les fonctionnalités de PostGIS.* | Calcule le centre du rectangle d'emprise par des requêtes sur le serveur PostgreSQL, et mémorise la géométrie dans les métadonnées. Cf. [Les calculs de géométries côté serveur](#les-calculs-de-géométries-côté-serveur). |

Pour déterminer si PostGIS est installée sur la base source de la table ou vue considérée, on pourra utiliser la requête renvoyée par la fonction `plume.pg.queries.query_exists_extension`.

```python

import psycopg2
from plume.pg import queries

conn = psycopg2.connect(connection_string)

with conn:
    with conn.cursor() as cur:
    
        cur.execute(*queries.query_exists_extension('postgis'))
        postgis_exists = cur.fetchone()[0]

conn.close()

```

*Si `postgis_exists` vaut `True`, l'extension PostGIS est bien installée sur la base considérée.*

### Actions à activer uniquement pour les couches chargées dans QGIS

... et si la couche sélectionnée est géométrique.

*NB : À date, Plume charge silencieusement les couches sélectionnées dans l'explorateur dont il lit les métadonées, les actions qui suivent pourront donc être activées pour toutes les couches géométriques.*

| Libellé de l'action | Terme inclus dans `'geo tools'` | Texte d'aide | Description de l'effet |
| --- | --- | --- | --- |
| *Calcul du rectangle d'emprise (QGIS)*  | `'bbox'` |  ![bbox_qgis.svg](../../plume/icons/buttons/geo/bbox_qgis.svg) [bbox_qgis.svg](../../plume/icons/buttons/geo/bbox_qgis.svg) | *Calcule le rectangle d'emprise à partir des données, via les fonctionnalités de QGIS.* | Calcule l'emprise de la couche grâce aux méthodes de QGIS (`QgsVectorLayer.extent`) et mémorise la géométrie dans les métadonnées. Cf. [Les calculs et tracé manuels côté QGIS](#les-calculs-et-tracés-manuels-côté-qgis). |
| *Calcul du centroïde (QGIS)*  | `'centroid'` |  ![centroid_qgis.svg](../../plume/icons/buttons/geo/centroid_qgis.svg) [centroid_qgis.svg](../../plume/icons/buttons/geo/centroid_qgis.svg) | *Calcule le centre du rectangle d'emprise à partir des données, via les fonctionnalités de QGIS.* | Calcule l'emprise de la couche grâce aux méthodes de QGIS (`QgsVectorLayer.extent`), puis le centre du rectangle (`QgsRectangle.centre`), et mémorise la géométrie dans les métadonnées. Cf. [Les calculs et tracé manuels côté QGIS](#les-calculs-et-tracés-manuels-côté-qgis). |

*Il n'est pas gênant de proposer à la fois le calcul dans QGIS et sous PostgreSQL. On peut supposer PostGIS plus rapide sur les très grosses tables, et QGIS a notamment l'intérêt de permettre de reprojeter une couche à la volée, si l'utilisateur ne veut pas que son rectangle d'emprise soit calculé dans le référentiel déclaré à PostGIS pour le champ de géométrie.*

## Les calculs de géométries côté serveur

Pour l'action *Calcul du rectangle d'emprise (PostGIS)*, on transmettra successivement les requêtes renvoyées par les fonctions `plume.pg.queries.query_get_geom_extent` et `plume.pg.queries.query_get_geom_srid`. La première renvoie la géométrie du rectangle d'emprise de la couche au format WKT. La seconde fournit le référentiel de coordonnées appliqué pour ladite géométrie.

```python

import psycopg2
from plume.pg import queries

conn = psycopg2.connect(connection_string)

with conn:
    with conn.cursor() as cur:
    
        query = queries.query_get_geom_srid(schema_name, table_name
            geom_name)
        cur.execute(*query)
        srid = cur.fetchone()[0]
        
        query = queries.query_get_geom_extent(schema_name,
            table_name, geom_name)
        cur.execute(*query)
        geom_wkt = cur.fetchone()[0]

conn.close()

```

*`table_name` est le nom de la table ou vue à documenter. `schema_name` est le nom de son schéma. `geom_name` est le nom du champ de géométrie de la couche sélectionnée dans le panneau des couches ou l'explorateur. C'est pour ce champ de géométrie que sera calculé l'emprise.*

Pour l'action *Calcul du centroïde (QGIS)*, le principe est le même, mais avec la fonction `query_get_geom_centroid` de `plume.pg.queries` au lieu de `query_get_geom_extent`.

Dans les deux cas, la fonction `plume.rdf.utils.wkt_with_srid` permet ensuite d'inclure le référentiel dans le WKT :

```python

from plume.rdf.utils import wkt_with_srid

rdf_wkt = wkt_with_srid(geom_wkt, srid)

```

Les valeurs résultantes seront de cette forme : `'<http://www.opengis.net/def/crs/EPSG/0/2154> POINT(651796.3281 6862298.5858)'`.

On notera que `rdf_wkt` pourrait être nul si `geom_wkt` l'était ou si le référentiel n'a pas été reconnu.

## Les calculs et tracés manuels côté QGIS

Après avoir obtenu une géométrie via les méthodes de QGIS, il faudra là encore la convertir dans le format attendu pour le type RDF `gsp:wktLiteral`.

Ceci suppose de commencer par l'encoder en WKT, avec les méthodes `QgsRectangle.asWktPolygon`, `QgsPointXY.asWkt`, etc. de QGIS.

Comme pour les géométries issues de PostGIS, on applique ensuite `plume.rdf.utils.wkt_with_srid`.

```python

from plume.rdf.utils import wkt_with_srid

rdf_wkt = wkt_with_srid(geom_wkt, srid)

```

*Où `geom_wkt` est le résultat de l'encodage de la géométrie en WKT et `srid` le référentiel de coordonnées courant de la couche (pour les fonctionnalités de calcul automatisé) ou du canevas (pour les fonctionnalités de tracé manuel).*

## Alimentation du formulaire

Contrairement à tous les autres boutons du formulaire, le bouton d'aide à la saisie des géométries n'affecte pas le dictionnaire. La géométrie obtenue sera simplement saisie dans le `QLineEdit` ou `QTextEdit`, elle sera ensuite gérée comme n'importe quelle autre valeur.

## Lecture des géométries pour la visualisation

QGIS sait construire des géométries à partir de représentations WKT, mais il ne sait pas lire les WKT incluant un référentiel qu'on trouvera en valeur des widgets. Celui-ci doit être spécifié à part.

Pour extraire la géométrie seule (toujours en WKT) d'une part, et le référentiel seul d'autre part, on exécutera `plume.rdf.utils.split_rdf_wkt` :

```python

from plume.rdf.utils import split_rdf_wkt

res = split_rdf_wkt(rdf_wkt)
if res:
    geom_wkt, srid = res
    ...

```

*Où `rdf_wkt` est la valeur saisie dans le widget principal de la clé.*

`wkt_with_srid` peut renvoyer `None` si `rdf_wkt` n'était pas exploitable, ce qui peut arriver en cas de modification manuelle. À défaut de référentiel explicitement déclaré dans `rdf_wkt`, il sera considéré que la géométrie était implicitement en `'OGC:CRS84'`.

Il est important de noter que seul un contrôle de forme superficiel est réalisé sur les référentiels, et à peu près aucun contrôle sur les géométries, dont rien n'assure a priori qu'elles soient valides. Les utiliser pour construire des objets géométriques avec les méthodes de QGIS supposera donc une solide gestion d'erreurs.


## Gestion du référentiel

Lors de la saisie d'une géométrie, le référentiel fourni en argument à `plume.rdf.utils.wkt_with_srid` doit être celui qui a effectivement été utilisé pour les coordonnées du WKT. Aucune transformation n'est nécessaire.

Lors de la visualisation, il faudra par contre projeter les coordonnées dans le référentiel courant du canevas.

| Action | Référentiel de départ | Référentiel d'arrivée |
| --- | --- | --- |
| calcul côté PostgreSQL | celui qui est renvoyé par `plume.pg.queries.query_get_geom_srid` | idem |
| calcul côté QGIS | celui de la couche | idem |
| saisie manuelle | celui du canevas | idem |
| visualisation | celui qui est renvoyé par `plume.rdf.utils.split_rdf_wkt` | celui du canevas |

## Précision des coordonnées

Par défaut, `qgis.core.QgsAbstractGeometry.asWkt` encode les WKT avec une précision de 17 décimales, et la fonction `ST_AsText` de PostGIS conserve jusqu'à 15 décimales (pourrait être variable selon les versions).

Plume permet à l'utilisateur de définir la précision adaptée à ses usages via un paramètre utilisateur. Par défaut, elle est fixée à 8 décimales, ce qui correspond à une précision de l'ordre du millimètre pour les latitudes et pour les longitudes à l'équateur en WGS 84.

