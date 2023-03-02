# Version corrective 0.3.1 bêta

*Date de publication : 30 mars 2022.*

*Sur GitHub : [https://github.com/MTES-MCT/metadata-postgresql/releases/tag/v0.3.1-beta](https://github.com/MTES-MCT/metadata-postgresql/releases/tag/v0.3.1-beta).*

Cette version corrective améliore la gestion des dépendances. Alors que la v0.3 bêta incorporait uniquement RDFLib, seule dépendance directe de Plume, la v0.3.1 bêta inclut aussi les bibliothèques nécessaires à RDFLib, ainsi que leurs propres dépendances. Cette évolution permet l'installation du plugin QGIS depuis le réseau interne de l'Etat, ou même sans accès internet. Par ailleurs, Plume utilise désormais des installeurs au format *wheel*, plus légers et rapides.

Paquets inclus : 

| Nom du paquet | Dépendance de... | Fiche PyPi | Remarques |
| --- | --- | --- | --- |
| `rdflib` | Plume | [https://pypi.org/project/rdflib/](https://pypi.org/project/rdflib/) | Seule dépendance directe de Plume, déjà incorporée dans Plume v0.3 bêta.|
| `isodate` | `rdflib` | [https://pypi.org/project/isodate/](https://pypi.org/project/isodate/) | |
| `six` | `isodate` | [https://pypi.org/project/six/](https://pypi.org/project/six/) | |
| `pyparsing` | `rdflib` | [https://pypi.org/project/pyparsing/](https://pypi.org/project/pyparsing/) | |
| `setuptools` | `rdflib` | [https://pypi.org/project/setuptools/](https://pypi.org/project/setuptools/) | |
| `importlib-metadata` | `rdflib` | [https://pypi.org/project/importlib-metadata/](https://pypi.org/project/importlib-metadata/) | Installé uniquement pour les versions de python strictement inférieures à la 3.8.0. |
| `zipp` | `importlib-metadata` | [https://pypi.org/project/zipp/](https://pypi.org/project/zipp/) | Installé uniquement pour les versions de python strictement inférieures à la 3.8.0. |
| `wheel` | | [https://pypi.org/project/wheel/](https://pypi.org/project/wheel/) | Pour l'installation des bibliothèques. |

