# Version mineure 0.7.0 bêta

*Date de publication : 20 mars 2023.*

*Sur GitHub : https://github.com/MTES-MCT/metadata-postgresql/releases/tag/v0.7-beta.*

L'extension PostgreSQL PlumePG doit obligatoirement être mise à jour en parallèle en version 0.2.0.

_**Avertissement n°1 :** Plume 0.7 bêta reste une version de test, à ne pas utiliser en production, car son schéma de métadonnées communes est susceptible d'évoluer dans la prochaine version sans que la rétro-compatibilité ne soit assurée. Autrement dit, les fiches de métadonnées créées avec cette version pourraient ne pas être pleinement exploitables par les versions ultérieures de Plume._ 

_**Avertissement n°2 :** Tous les utilisateurs de l'extension PostgreSQL PlumePg doivent impérativement mettre à jour cette dernière en version 0.2.0 pour qu'elle reste reconnue par Plume._ 

## Descriptif des objets dans le panneau d'AsgardMenu

Depuis la [version 0.5.0 bêta](./v0_5_0_beta.md), Plume peut être configuré (et l'est par défaut) pour alléger les infobulles de l'explorateur de QGIS en masquant les JSON-LD contenant les métadonnées. Désormais, ce mécanisme s'applique aussi aux infobulles du mode panneau du plugin [AsgardMenu](https://snum.scenari-community.org/Asgard/Documentation/co/SEC_AsgardMenu.html). 

*Référence : [issue #113](https://github.com/MTES-MCT/metadata-postgresql/issues/113).*

## Mise en valeur des métadonnées non renseignées

L'onglet *Fiches de métadonnées* de la boîte de dialogue *Personnalisation de l'interface* ![configuration.svg](../../plume/icons/general/configuration.svg) propose maintenant une option supplémentaire *Visualisation des zones non saisies*. Lorsque l'utilisateur l'active, il peut choisir une couleur de fond (et un niveau d'opacité) pour les champs des fiches de métadonnées dans lesquels aucune valeur n'a été renseignée, afin de les rendre plus aisés à repérer.

*Référence : [issue #100](https://github.com/MTES-MCT/metadata-postgresql/issues/100).*

## Structure de données pour le stockage des modèles

Publiée en parallèle de Plume 0.2.0 bêta, la version 0.2.0 de l'extension PostgreSQL PlumePg modifie la structure de stockage pour les modèles de fiches de métadonnées afin de la rendre plus robuste. Cette évolution s'incrit dans le cadre du développement d'une interface de gestion des modèles intégrée à Plume.

Concrètement, il s'agit de remplacer des clés primaires et étrangères sémantiques que l'administrateur peut être amené à modifier pour des raisons légitimes (nom des modèles et noms des onglets), par des identifiants techniques a priori stables. L'inconvénient de ce changement est qu'il alourdit encore la création de modèles sans interface.

La préservation des modèles déjà saisis est bien évidemment assurée lors de la mise à jour.

*Référence : [issue #115](https://github.com/MTES-MCT/metadata-postgresql/issues/115).*

*Plus de détails sur les modèles de PlumePg et leur structure de données dans la [documentation technique](../usage/modeles_de_formulaire.md#gestion-dans-postgresql).*

## Corrections d'anomalies et divers

La fenêtre *À Propos* est maintenant redimensionnable. *Référence : [issue #98](https://github.com/MTES-MCT/metadata-postgresql/issues/98).*

Correction d'une anomalie qui pouvait provoquer des erreurs lors du calcul automatique de métadonnées en mode lecture. *Référence : [issue #112](https://github.com/MTES-MCT/metadata-postgresql/issues/112).*

Actualisation des bibliothèques intégrées dans Plume. Le processus de mise à jour se déclenche automatiquement lors de l'installation de la nouvelle version de Plume et peut prendre quelques minutes. *Référence : [issue #108](https://github.com/MTES-MCT/metadata-postgresql/issues/108).* *À noter que RDFLib n'est pas mise à jour, malgré la disponibilité de deux versions plus récentes que la 6.1.1 actuellement utilisée. À date Plume n'est en effet pas compatible avec les versions 6.2.0 et 6.3.0 en raison d'une régression sur ces versions. L'anomalie [a été signalée](https://github.com/RDFLib/rdflib/issues/2281) et devrait être corrigée très prochainement.*

