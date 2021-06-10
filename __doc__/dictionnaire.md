# Mode d'emploi du dictionnaire des widgets

## Création

Le dictionnaire de paramétrage est créé par la fonction `buildDict` de `rdf_utils.py`.

Cette fonction exploite des informations issues de quatre sources :
- un **graphe RDF contenant les métadonnées** associées au jeu de données dont on souhaite éditer/visualiser les métadonnées. Issu de la dé-sérialisation du JSON-LD contenu dans le descriptif de la table ou vue PostgreSQL, il fournit principalement les valeurs à placer dans les widgets d'édition.
- un **graphe RDF contenant le vocabulaire** de toutes les ontologies dans lesquelles les catégories du graphe puisent leurs valeurs.
- un **schéma SHACL** (augmenté de propriétés sur-mesure pour le formulaire) décrivant les catégories de métadonnées communes.
- éventuellement, un dictionnaire définissant un **modèle de formulaire** choisi par l'utilisateur. Fournir un tel modèle permet :
    - d'ajouter des métadonnées locales aux catégories communes du schéma SHACL ;
    - de restreindre les catégories communes à afficher dans le formulaire ;
    - de substituer des paramètres locaux à ceux spécifiés par le schéma SHACL (par exemple remplacer le nom à afficher pour la catégorie de métadonnée ou changer le type de widget à utiliser).
    
*La structure attendue pour le modèle de formulaire est proche de celle du dictionnaire résultant de la présente fonction, si ce n'est que ses clés sont des chemins SPARQL identifiant des catégories de métadonnées et ses dictionnaires internes comprennent nettement moins de clés. De plus, certains caractéristiques ne peuvent être re-définies pour les catégories de métadonnées communes (concrètement la fonction ignorera ces informations) : il n'est pas possible de changer le type des valeurs, par exemple.*

