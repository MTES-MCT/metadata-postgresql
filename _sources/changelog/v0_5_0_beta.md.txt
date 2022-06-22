# Version mineure 0.5.0 bêta (en cours de développement)

*Date de publication : à venir aux alentours du 1er juillet 2022.*

*Sur GitHub : à venir.*

Plume v0.5 bêta est vraisemblablement la denière version précédant le déploiement officiel de Plume (hors correctifs éventuels). Elle poursuit la mise à disposition des fonctionnalités essentielles pour la saisie et la consultation des métadonnées.

## Import de métadonnées depuis un fichier XML conforme INSPIRE

Plume v0.5 bêta propose une nouvelle fonctionnalité d'import, qui permet de lire le contenu d'un fichier XML conforme aux spécifications d'INSPIRE. Elle est accessible, tout comme les autres méthodes d'import, via le menu ![import.svg](../../../plume/icons/general/import.svg) *Importer les métadonnées* de la barre d'outils de Plume. À noter qu'elle présente les mêmes limitations que l'[import de métadonnées INSPIRE via un service CSW](../usage/actions_generales.md#import-de-métadonnées-depuis-un-service-csw-inspire), notamment en ce qui concerne les catégories de métadonnées prises en charge à ce stade.

*Réference : [issue #72](https://github.com/MTES-MCT/metadata-postgresql/issues/72).*

## Nettoyage des infobulles de l'explorateur

Parce que Plume enregistre les métadonnées des tables et vues dans leurs descriptifs PostgreSQL, ceux-ci deviennent immanquablement rapidement illisibles. S'il n'existe pas de méthode miracle pour résoudre globalement cette problématique d'ergonomie intrinsèque, Plume v0.5 bêta offre une solution pour l'une des situations où elle était particulièrement prégnante : lorsque QGIS affiche le contenu du descriptif PostgreSQL au survol d'une couche dans l'explorateur.

Sous réserve d'avoir activé au moins une fois Plume depuis l'ouverture de QGIS en cliquant sur son icône dans la barre d'outils, Plume est désormais capable d'alléger les infobulles de l'explorateur en supprimant les balises `<METADATA>` et le JSON-LD qu'elles contiennent. Cette transformation est active par défaut, mais elle peut être inhibée via le menu ![configuration.svg](../../../plume/icons/general/configuration.svg) *Personnalisation de l'interface*. Il est également possible de paramétrer Plume, toujours via le menu ![configuration.svg](../../../plume/icons/general/configuration.svg) *Personnalisation de l'interface*, pour qu'au lieu d'effacer purement et simplement les balises `<METADATA>`, il les remplace par le libellé de la table/vue extrait des métadonnées (s'il existe).

*Réference : [issue #67](https://github.com/MTES-MCT/metadata-postgresql/issues/67).*

## Correction d'anomalies et divers

En mode lecture, ou plus généralement quand Plume est paramétré pour n'afficher que les métadonnées dans la langue principale[^mainlanguage], la fiche de métadonnées présente les informations saisies dans ladite langue lorsqu'elles existent et masque alors toutes les informations dans les autres langues. Si aucune valeur n'est disponible dans langue principale pour une métadonnée traduisible, Plume affiche une valeur (et une seule) dans une autre langue, en privilégiant les langues de la liste des langues autorisées pour les traductions, considérées dans l'ordre de la liste. Ce mécanisme était affecté par une anomalie qui empêchait parfois l'affichage de la valeur dans la langue de substitution, Plume v0.5 bêta la corrige.

[^mainlanguage]: Il s'agit de la langue que l'utilisateur peut sélectionner via la barre d'outils de Plume en choisissant dans la liste des langues autorisées pour les traductions. Cette liste est elle-même un paramètre utilisateur configurable via le menu ![configuration.svg](../../../plume/icons/general/configuration.svg)  *Personnalisation de l'interface*.