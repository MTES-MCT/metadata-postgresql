# Version 0.4.0 bêta (*en cours de développement*)

*Date de publication : à venir.*

*Sur GitHub : à venir.*

La version 0.4 apporte notamment plusieurs petites évolutions fonctionnelles visant à fluidifier et sécuriser la navigation.

## Verrouillage de l'affichage sur la fiche courante

La version 0.4 ajoute à la barre d'outil de Plume un bouton en forme de cadenas qui permet de verrouiller l'affichage sur la fiche de métadonnées courante.

En mode lecture, ce bouton est désactivé par défaut. Quand l'utilisateur sélectionne une nouvelle couche PostgreSQL dans l'explorateur ou le panneau, les métadonnées de cette couche s'affichent dans le panneau de Plume. Lorsqu'il sélectionne une couche dont le fournisseur n'est pas un serveur PostgreSQL, Plume revient à son écran d'accueil.

Si l'utilisateur actionne le bouton de verrouillage, la fiche de métadonnées courante restera affichée dans le panneau de Plume quelles que soient les manipulations réalisées par l'utilisateur dans l'explorateur et le panneau des couches.

En mode édition, ce bouton est activé par défaut et ne peut pas être désactivé. Ceci permet d'éviter à l'utilisateur de perdre accidentellement ses modifications à cause d'un clic malencontreux sur une autre couche.

Références : [issue #36](https://github.com/MTES-MCT/metadata-postgresql/issues/36), [issue #41](https://github.com/MTES-MCT/metadata-postgresql/issues/41), [issue #47](https://github.com/MTES-MCT/metadata-postgresql/issues/47).

## Confirmation à la sortie du mode édition

Lorsque l'utilisateur quitte le mode édition sans avoir préalablement sauvegardé ses modifications, Plume lui demande maintenant une confirmation. Un paramètre utilisateur permet de supprimer cette étape.

Références : [issue #46](https://github.com/MTES-MCT/metadata-postgresql/issues/46).

## Affichage des métadonnées de la couche sélectionnée au lancement de Plume

Si l'utilisateur sélectionne une couche PostgreSQL dans l'explorateur ou le panneau des couches *puis* lance Plume, les métadonnées de cette couche sont maintenant immédiatement affichées. Auparavant, seules les couches sélectionnées après le lancement de Plume étaient prises en compte.

Références : [issue #38](https://github.com/MTES-MCT/metadata-postgresql/issues/38).

## PlumePg v0.1.0

**Une mise à jour de l'extension PostgreSQL PlumePg sera nécessaire** pour continuer à utiliser les modèles personnalisés avec la version 0.4 de Plume.

La version 0.1.0 de PlumePg complète le paramétrage du calcul automatique des métadonnées.

Les champs `compute` des tables `meta_categorie` et `meta_template_categories` admettent maintenant deux nouvelles valeurs, `empty` et `new`. Comme `auto`, ces mots-clés signalent à Plume que la métadonnée doit être calculée automatiquement à partir des informations disponibles sur le serveur PostgreSQL lors du chargement de la fiche de métadonnées. Toutefois, ils posent des conditions à cette action :
- `empty` indique que le calcul automatique doit avoir lieu si et seulement si aucune valeur n'est encore renseignée pour la métadonnée considérée.
- `new` signale que le calcul doit s'exécuter si et seulement si la fiche de métadonnées est vierge.

Les tables `meta_categorie` et `meta_template_categories`, ainsi que la vue `meta_template_categories_full` présentent maintenant un champ supplémentaire de type `jsonb` qui permet de paramétrer la méthode de calcul des métadonnées définie pour la catégorie, lorsque la méthode le prévoit.

## Amélioration de la gestion des métadonnées en lecture seule

La version 0.4 assure que les métadonnées en lecture seule[^isreadonly] en mode édition ne sont plus accompagnées d'aucun bouton permettant d'en altérer la valeur. Les groupes de valeurs en lecture seule n'ont plus de bouton plus.

La lecture seule est désormais une caractéristique héritable. Ainsi, si le modèle indique par exemple que la métadonnée `dct:temporal` est en lecture seule, `dct:temporal / dcat:startDate` le sera également même si ce n'est pas explicitement spécifié dans le modèle.

[^isreadonly]: Une catégorie peut être déclarée comme étant "en lecture seule" (non éditable) par un modèle de fiche défini avec *PlumePg*. On indiquera `True` dans le champ `is_read_only` de la table `z_plume.meta_template_categories` pour le modèle et la catégorie considérés.

Référence : [issue #48](https://github.com/MTES-MCT/metadata-postgresql/issues/48).

