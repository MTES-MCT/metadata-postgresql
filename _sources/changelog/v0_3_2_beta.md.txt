# Version mineure 0.3.2 bêta

*Date de publication : 31 mars 2022.*
*Sur GitHub : https://github.com/MTES-MCT/metadata-postgresql/releases/tag/v0.3.2-beta.*

Plume v0.3.2 bêta est une version corrective.

Elle incorpore à Plume la bibliothèque [`typing-extensions`](https://pypi.org/project/typing-extensions/) (dépendance de [`importlib-metadata`](https://pypi.org/project/importlib-metadata/) pour les versions de python inférieures à la 3.8), dont l'absence pouvait faire échouer l'installation. Cf. [issue #45](https://github.com/MTES-MCT/metadata-postgresql/issues/45).

Elle résout également une petite anomalie sur la forme du curseur qui, après usage des fonctionnalités d'aide à la saisie des géométries, perdait sa capacité habituelle à changer d'aspect au survol d'un hyperlien. Cf. [issue #43](https://github.com/MTES-MCT/metadata-postgresql/issues/43).
