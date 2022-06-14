# Version mineure 0.4.1 bêta

*Date de publication : 14 juin 2022.*

*Sur GitHub : [https://github.com/MTES-MCT/metadata-postgresql/releases/tag/v0.4.1-beta](https://github.com/MTES-MCT/metadata-postgresql/releases/tag/v0.4.1-beta).*

Plume v0.4.1 bêta est une version corrective.

Elle corrige une anomalie qui empêchait l'exécution de Plume lorsque l'extension PlumePg (toutes versions confondues) n'était pas disponible dans le répertoire des extensions du serveur PostgreSQL cible. *Réference : [issue #71](https://github.com/MTES-MCT/metadata-postgresql/issues/71).*

Elle corrige une anomalie qui prohibait la lecture des métadonnées des tables issues de serveurs PostgreSQL 9.5. *NB. Plume n'est pas officiellement compatible avec les versions de PostgreSQL antérieures à PostgreSQL 10, dans la mesure où le plugin ne fait pas l'objet de campagnes de tests systématiques avec ces versions. La compatibilité reste assurée a minima tant qu'elle n'affecte pas les fonctionnalités de l'outil. PlumePg est pour sa part absolument incompatible avec les versions antérieures à PostgreSQL 10.*

Plume v0.4.1 bêta est publiée conjointement à la version 0.1.1 de l'extension PostgreSQL PlumePg. Il s'agit là-aussi d'une version corrective, qui n'apporte absolument aucune évolution fonctionnelle et vise seulement à permettre la mise à jour depuis la version 0.0.1, laquelle s'avérait impossible sous PostgreSQL 10 et 11. Bien qu'il n'y ait aucune différence pratique, on recommandera de mettre également à jour en v0.1.1 les serveurs qui avaient pu basculer en v0.1.0. *Réference : [issue #73](https://github.com/MTES-MCT/metadata-postgresql/issues/73).*