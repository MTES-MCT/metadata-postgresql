# Version mineure 0.6.0 bêta (en cours de développement)

*Date de publication : à venir.*

*Sur GitHub : à venir.*

## Refonte de l'interface

L'interface de Plume devient plus ergonomique et plus souple. En particulier : 
- La barre d'outils de Plume et ses fiches de métadonnées présentent désormais de nouvelles icônes colorées plus aisément reconnaissables. *Référence : [issue #84](https://github.com/MTES-MCT/metadata-postgresql/issues/84).*
- Il est désormais possible d'utiliser des polices exotiques ou d'activer le grossissement sur son écran sans avoir de libellés tronqués, tant dans l'interface principale que dans la boîte de dialogue de paramétrage et la boîte de dialogue pour l'import depuis un CSW). *Référence : [issue #91](https://github.com/MTES-MCT/metadata-postgresql/issues/91).*
- La boîte de paramétrage a été réorganisée, avec un classement plus intuitif des paramètres dans les onglets. *Référence : [issue #90](https://github.com/MTES-MCT/metadata-postgresql/issues/90).*
- La barre d'outils de l'interface principale bénéficie désormais d'un placement dynamique des icônes et réagit mieux en cas de redimensionnement de la fenêtre, grossissement, etc. *Références : [issue #82](https://github.com/MTES-MCT/metadata-postgresql/issues/82), [issue #87](https://github.com/MTES-MCT/metadata-postgresql/issues/87).*
- Dans tous les menus de choix, il est désormais possible d'identifier immédiatement la valeur actuellement sélectionnée par la petite flèche positionnée devant. Ce fonctionnement existait déjà pour le menu de choix du modèle (barre d'outils) et les menus de choix de la source qui accompagnent certaines catégories de métadonnées, il est désormais étendu à tous les autres. *Référence : [issue #85](https://github.com/MTES-MCT/metadata-postgresql/issues/85).*

Afin d'assurer l'homogénéité visuelle des boutons avec menus, le bouton d'aide à la saisie des géométries qui, en mode édition, est associé aux métadonnées de type géométrique, adopte un nouveau fonctionnement :
cliquer brièvement active/désactive la visualisation de la géométrie saisie, cliquer en maintenant appuyé quelques secondes fait apparaître le menu.  *Référence : [issue #81](https://github.com/MTES-MCT/metadata-postgresql/issues/81).*

## Des libellés pour les services CSW

Plume permettait déjà de mémoriser des URL de base de services CSW pour éviter d'avoir à les resaisir à chaque import de fiche. Il est désormais possible d'ajouter un libellé à ces URL pour retrouver plus facilement à quoi elles correspondent. *Référence : [issue #95](https://github.com/MTES-MCT/metadata-postgresql/issues/95).*

## Sécurisation du changement de langue ou de modèle

L'utilisateur est désormais averti qu'il risque de perdre ses modifications non enregistrées lorsqu'il change la langue principale de saisie ou le modèle, comme il l'était déjà lors d'un retour en mode lecture ou lorsqu'il activait/désactivait le mode traduction. *Référence : [issue #88](https://github.com/MTES-MCT/metadata-postgresql/issues/88).*


## Correction d'anomalies et divers

Correction de la fonctionnalité d'import depuis un fichier de métadonnées INSPIRE ou ISO 19115/19139 pour qu'elle reconnaisse l'élément `gmd:MD_Metadata` qu'il soit à la racine ou englobé dans un élément de réponse comme `csw:GetRecordByIdResponse`. À défaut, les tentatives d'import produisaient souvent une fiche vide. Cette évolution rend aussi plus permissif l'import depuis les CSW, même s'il n'y avait pas nécessairement de besoin identifié à date (mêmes commandes de traitement pour les deux sources). *Référence : [issue #93](https://github.com/MTES-MCT/metadata-postgresql/issues/93).*

Un rôle qui n'est pas propriétaire d'une table/vue et n'a donc accès à ses métadonnées qu'en lecture peut désormais réaliser toutes les actions normalement disponibles dans ce mode : choisir la langue principale d'affichage des métadonnées, choisir le modèle de fiche de métadonnées, copier la fiche, exporter la fiche. *Référence : [issue #94](https://github.com/MTES-MCT/metadata-postgresql/issues/94).*

Correction d'une anomalie qui provoquait l'apparition de boutons moins parasites lors de l'activation ou la désactivation de la saisie manuelle. *Référence : [issue #89](https://github.com/MTES-MCT/metadata-postgresql/issues/89).*

Correction d'une anomalie qui altérait l'ordre de préférence des langues défini par l'utilisateur.

Correction d'une anomalie qui provoquait des erreurs lors de l'usage d'un modèle de fiche de métadonnées affectant explicitement un onglet à une catégorie commune dont le chemin comporte des majuscules. 

Correction d'une anomalie qui faisait qu'une fiche de métadonnées ouverte en mode édition lors de la fermeture de Plume réapparaissait comme fiche courante si Plume était rouvert avec une ressource sélectionnée autre qu'une couche PostgreSQL. *Référence : [issue #83](https://github.com/MTES-MCT/metadata-postgresql/issues/83).*

Correction d'une anomalie qui faisait que fermer Plume avec une fiche en mode édition puis rouvrir immédiatement Plume montrait à l'utilisateur l'écran d'accueil... avec tous les boutons de la barre d'outils actifs.  *Référence : [issue #83](https://github.com/MTES-MCT/metadata-postgresql/issues/83).*