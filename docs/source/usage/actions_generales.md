# Actions générales

Sont décrites ici les actions que l'utilisateur peut réaliser dans la partie fixe de l'interface du plugin. Pour les interactions de l'utilisateur avec les widgets du formulaire de saisie (ajout/suppression de valeurs, etc.), on se reportera à [Actions contrôlées par les widgets du formulaire](/docs/source/usage/actions_widgets.md).

Barre d'outils de plume : [Mode lecture, mode édition](#mode-lecture-mode-édition) • [Sauvegarde](#sauvegarde) • [Activation du mode traduction](#activation-du-mode-traduction) • [Choix de la trame de formulaire](#choix-de-la-trame-de-formulaire) • [Langue principale des métadonnées](#langue-principale-des-métadonnées) • [Import de métadonnées depuis un fichier](#import-de-métadonnées-depuis-un-fichier) • [Export des métadonnées dans un fichier](#export-des-métadonnées-dans-un-fichier) • [Réinitialisation](#réinitialisation) • [Copier / coller d'une fiche complète](#copier--coller-dune-fiche-complète)

Autres actions : [Sélection de la table à documenter](#sélection-de-la-table-à-documenter)

## Mode lecture, mode édition

### Effet sur le formulaire

Une fiche de métadonnées peut être ouverte :
- soit en **mode lecture**, qui permet de consulter les métadonnées mais pas de les modifier ;
- soit en **mode édition**, qui permet de modifier les métadonnées.

Du point de vue de l'utilisateur, le formulaire paraîtra très différent dans les deux modes. En mode lecture, tous les widgets de saisie sont désactivés (la [clé `'read only'`](/docs/source/usage/creation_widgets.md#paramètres-spécifiques-aux-widgets-de-saisie) du dictionnaire de widgets vaut toujours `True`). De plus, là où le mode édition affiche naturellement les champs sans valeur pour que l'utilisateur puisse les remplir, le mode lecture les masque (sauf si l'utilisateur a explicitement demandé le contraire en mettant à `False` le [paramètre utilisateur `readHideBlank`](/docs/source/usage/generation_dictionnaire_widgets.md#readhideblank) - cf. [Paramètres utilisateur](/docs/source/usage/parametres_utilisateur.md).

Concrètement, le passage d'un mode à l'autre implique simplement de [regénérer le dictionnaire de widgets](/docs/source/usage/generation_dictionnaire_widgets.md) en spécifiant le mode grâce au paramètre `mode` :
- `mode='edit'` en mode édition ;
- `mode='read'` en mode lecture.

Le formulaire de saisie/consultation peut ensuite être [recréé à partir du nouveau dictionnaire](/docs/source/usage/creation_widgets.md), selon les mêmes modalités quel que soit le mode.

### Autres effets

Certaines des actions générales décrites dans la suite ne devraient être disponibles qu'en mode édition :
- la sauvegarde des modifications ;
- l'activation ou la désactivation du mode traduction ;
- l'import de métadonnées depuis un fichier ;
- la réinitialisation de la fiche.

### Caractéristiques du bouton

**Initialement, toutes les fiches s'ouvrent en mode lecture**. L'utilisateur doit cliquer sur le bouton d'activation du mode édition pour basculer dans ce dernier.

Le bouton utilise l'icône [read.svg](/plume/icons/general/read.svg) :
![read.svg](/plume/icons/general/read.svg).

L'idéal serait que le texte d'aide s'adapte au mode courant :

| Mode actif | Condition | Infobulle |
| --- | --- | --- |
| lecture | `if mode == 'read'` | *Basculer en mode édition* |
| édition | `if mode == 'edit'` | *Quitter le mode édition* |

Le bouton devra être inactif quand l'utilisateur ne dispose pas des droits nécessaires pour éditer les métadonnées de la table ou vue considérée, soit quand son rôle de connexion n'est pas membre du rôle propriétaire de l'objet.

Pour s'en assurer, on utilisera la requête définie par la fonction [`plume.pg.queries.query_is_relation_owner`](/plume/pg/queries.py).

```python

import psycopg2
from plume.pg import queries

conn = psycopg2.connect(connection_string)

with conn:
	with conn.cursor() as cur:
	
		cur.execute(
			queries.query_is_relation_owner(),
			(schema_name, table_name)
			)
		res = cur.fetchone()
		is_owner = res[0] if res else False

conn.close()

```

*`connection_string` est la chaîne de connexion à la base de données PostgreSQL, `table_name` est le nom de la table ou vue dont on affiche les métadonnées, `schema_name` est le nom de son schéma.*


## Sauvegarde

### Effets

Le **bouton de sauvegarde** permet à l'utilisateur d'enregistrer sur le serveur PostgreSQL les métadonnées qu'il a saisies.

En arrière plan, cela suppose plusieurs opérations successives.

1. Enregistrer dans le dictionnaire de widgets les valeurs contenues dans les widgets de saisie. On utilisera pour ce faire la méthode `update_value` de la classe `plume.rdf.widgetsdict.WidgetsDict`.

Cette opération n'a de sens que pour les widgets de saisie non masqués, néanmoins la méthode `plume.rdf.widgetkey.RootKey.build_metagraph`[^appel-roootkey-build-metagraph], qui assure ensuite la reconstruction du graphe de métadonnées mis à jour, se charge d'éliminer les clés masquées. On pourra donc simplement boucler sur toutes les clés du dictionnaire dont le widget principal est supposé contenir une valeur (pas les boutons ni les groupes, donc) et exécuter :

[^appel-roootkey-build-metagraph]: Cette méthode est appelée par la méthode `build_metagraph` de `plume.rdf.widgetsdict.WidgetsDict` utilisée à l'étape suivante.

```python

widgetsdict.update_value(widgetkey, widget_value)

```
*Où `widgetkey` est une clé du dictionnaire de widgets `widgetsdict` correspondant à un widget de saisie et `widget_value` la valeur récupérée dans ce widget.*


2. Générer un graphe de métadonnées à partir du dictionnaire de widgets actualisé.

```python

new_metagraph = widgetsdict.build_metagraph()

```

3. Créer une version actualisée du descriptif PostgreSQL de l'objet.

Le descriptif, objet de classe [`plume.pg.description.PgDescription`](/docs/source/usage/generation_dictionnaire_widgets.md#metagraph--le-graphe-des-métadonnées-pré-existantes) nommé ci-après `pg_description`, est mis à jour via sa propriété `metagraph`.

```python

pg_description.metagraph = new_metagraph

```

4. Envoyer au serveur PostgreSQL une requête de mise à jour du descriptif.

On utilisera la requête définie par la fonction `query_update_table_comment` du module [plume.pg.queries](/plume/pg/queries.py). À noter que, dans la mesure où les commandes diffèrent selon le type de relation, il est nécessaire de commencer par récupérer cette information avec `query_get_relation_kind`.

La requête doit être appliquée à `str(pg_description)`, qui renvoie une représentation sous forme de chaîne de caractères de `pg_description`.

```python

import psycopg2
from plume.pg import queries

conn = psycopg2.connect(connection_string)

with conn:
    with conn.cursor() as cur:

        cur.execute(
            pg_queries.query_get_relation_kind(
                schema_name, table_name
                )
            )
        kind = cur.fetchone()
        
        query = pg_queries.query_update_table_comment(
            schema_name, table_name, relation_kind=kind[0]
            )
        cur.execute(query, (str(pg_description),))

conn.close()

```

*`connection_string` est la chaîne de connexion à la base de données PostgreSQL, `table_name` est le nom de la table ou vue dont on édite les métadonnées, `schema_name` est le nom de son schéma.*

5. Mettre à jour les descriptifs des champs.

La requête de mise à jour est directement déduite du dictionnaire de widgets par la fonction `query_update_columns_comments` du module [plume.pg.queries](/plume/pg/queries.py).

```python

import psycopg2
from plume.pg import queries

conn = psycopg2.connect(connection_string)

with conn:
	with conn.cursor() as cur:
	
        query = pg_queries.query_update_columns_comments(
            schema_name, table_name, widgetsdict
            )
        
        if query:
            cur.execute(query)

conn.close()

```

*`connection_string` est la chaîne de connexion à la base de données PostgreSQL, `table_name` est le nom de la table ou vue dont on édite les métadonnées, `schema_name` est le nom de son schéma.*

*La condition de non nullité sur `query` est nécessaire, car la fonction pourrait renvoyer `None` si le dictionnaire ne contenait aucun descriptif de champs. Ceci peut arriver :*
- *si le paramètre [`columns`](/docs/source/usage/generation_dictionnaire_widgets.md#columns--les-descriptifs-des-champs) n'a pas été fourni en argument lors de la création du dictionnaire de widgets ;*
- *ou si cette liste était vide, parce que la table n'a aucun champ.*

### Caractéristiques du bouton

Comme susmentionné, ce bouton ne doit être actif qu'en mode édition.

Il utilise l'icône [save.svg](/plume/icons/general/save.svg) :
![save.svg](/plume/icons/general/save.svg)

Texte d'aide : *Enregistrer les métadonnées*.

## Activation du mode traduction

### Effets

Lorsque le mode traduction est actif, l'utilisateur a la possibilité de définir la langue des valeurs qu'il saisit (sinon c'est le paramètre utilisateur `language` qui est systématiquement utilisé). Il pourra également saisir des traductions pour des catégories qui n'acceptent qu'une valeur par langue (par exemple le libellé de la donnée).

Concrètement, l'activation ou la désactivation du mode traduction impliquera de regénérer le dictionnaire de widgets, c'est-à-dire relancer la fonction `build_dict()` avec :
- `translation=True` si le mode traduction est actif ;
- `translation=False` s'il ne l'est pas (ou sans spécifier `translation`, `False` étant la valeur par défaut).

Cf. [Génération du dictionnaire des widgets](/docs/source/usage/generation_dictionnaire_widgets.md).

Le formulaire peut ensuite être regénéré à partir du nouveau dictionnaire, selon les mêmes modalités que le mode traduction soit actif ou non (cf. [Création d'un nouveau widget](/docs/source/usage/creation_widgets.md)).

### Caractéristiques du bouton

Ce bouton ne doit être actif qu'en mode édition.

Il utilise l'icône [translation.svg](/plume/icons/general/translation.svg) :
![translation.svg](/plume/icons/general/translation.svg)

L'idéal serait que le texte d'aide s'adapte selon que le mode traduction est actif ou non :

| Mode traduction activé | Condition | Infobulle |
| --- | --- | --- |
| non | `if not translation` | *Activer les fonctions de traduction* |
| oui | `if translation` | *Désactiver les fonctions de traduction* |

Si toutefois cela s'avère complexe à mettre en oeuvre, on se contera de *Activer les fonctions de traduction*.

### Initialisation

Ce paramètre pourra être systématiquement sauvegardé dans le fichier `QGIS3.ini`, et initialisé à l'activation du mode édition à partir de la valeur récupérée dans les fichiers de configuration (ou `False` à défaut).


## Choix de la trame de formulaire

### Effets

Le modèle de formulaire détermine les catégories de métadonnées affichées dans le formulaire et la manière dont elles sont présentées - cf [Modèles de formulaire](/docs/source/usage/modeles_de_formulaire.md).

Dès lors que des modèles sont disponibles, c'est-à-dire que `templateLabels` n'est pas `None` ou une liste vide (cf. [Modèles de formulaire](/docs/source/usage/modeles_de_formulaire.md), étape [Récupération de la liste des modèles](/docs/source/usage/modeles_de_formulaire.md#récupération-de-la-liste-des-modèles)), l'utilisateur doit avoir la possibilité de basculer à tout moment d'un modèle pré-défini à l'autre ou de ne pas appliquer de modèle du tout.

Dans ce dernier cas, on aurait :

```python

template = None
templateTabs = None

```

Sinon `template` et `templateTabs` devront être générés à partir du nom du modèle sélectionné (`tpl_label`), en suivant la méthode décrite dans [Modèles de formulaire](/docs/source/usage/modeles_de_formulaire.md#récupération-de-la-liste-des-modèles) (étape [Récupération des catégories associées au modèle retenu](/docs/source/usage/modeles_de_formulaire.md#récupération-des-catégories-associées-au-modèle-retenu) et suivantes).

Dans tous les cas, il faudra réexécuter `build_dict()` avec les nouveaux paramètres pour `template` et `templateTabs`, puis recréer le formulaire à partir du dictionnaire de widgets actualisé ainsi obtenu.

### Caractéristiques du widget

Le widget de sélection du modèle pourra être soit un QComboBox soit un QToolButton similaire aux boutons de sélection de la source du formulaire (cf. [Création d'un nouveau widget](/docs/source/usage/creation_widgets.md#widget-annexe--bouton-de-sélection-de-la-source)).

Les valeurs disponibles sont les noms de modèles listés par `templateLabels`, auxquelles ont ajoutera un item `'Aucun modèle'` (ou autre nom similaire).

Si `templateLabels` est `None` ou une liste vide, il n'y a pas lieu d'afficher le widget. `template` et `templateTabs` vaudront simplement toujours `None`.

D'autant que de besoin, le bouton utilise l'icône [template.svg](/plume/icons/general/template.svg) :
![template.svg](/plume/icons/general/template.svg)

Texte d'aide : *Choisir un modèle de formulaire*.

### Initialisation

La démarche à suivre à l'ouverture d'une fiche de métadonnées, est décrite dans [Modèles de formulaire](/docs/source/usage/modeles_de_formulaire.md#import-par-le-plugin). On commencera par récupérer les paramètres `preferedTemplate` et `enforcePreferedTemplate` dans les fichiers de configuration, si tant est qu'ils soient présents.


## Langue principale des métadonnées

### Effets

La langue principale de métadonnées correspond au paramètre utilisateur `language` que prennent en entrée de nombreuses fonctions et méthodes de [rdf_utils.py](/plume/bibli_rdf/rdf_utils.py).

Hors mode traduction, toutes les métadonnées saisies qui ne soient pas des dates, nombres, URL ou autres types qui ne sont pas supposés avoir une langue seront présumées être dans cette langue. C'est aussi dans cette langue que seront affichées les valeurs issues des thésaurus (autant que possible, car les thésaurus ne contiennent pas de traductions pour toutes les langues imaginables).

Lorsque l'utilisateur modifie la langue principale, il est nécessaire de regénérer le dictionnaire de widgets avec la nouvelle valeur de `language` (cf. [Génération du dictionnaire des widgets](/docs/source/usage/generation_dictionnaire_widgets.md)), puis le formulaire à partir du dictionnaire de widgets mis à jour (cf. [Création d'un nouveau widget](/docs/source/usage/creation_widgets.md)).

### Caractéristiques du widget

Le widget de choix de la langue principale pourra être soit un QComboBox soit un QToolButton similaire aux boutons de sélection de la langue du formulaire (cf. [Création d'un nouveau widget](/docs/source/usage/creation_widgets.md#widget-annexe--bouton-de-sélection-de-la-langue)). Dans les deux cas, les valeurs disponibles sont les langues listées par le paramètre utilisateur `langList`.

Texte d'aide : *Modifier la langue principale des métadonnées*.

### Initialisation

Le paramètre `language` pourra être systématiquement sauvegardé dans le fichier `QGIS3.ini`, et initialisé à l'activation du plugin à partir de la valeur récupérée dans les fichiers de configuration.

Un point important est que `language` doit toujours être l'une des langues listées par le paramètre utilisateur `langList`. Si ce n'est pas le cas avec les valeurs issues des fichiers de configuration, on pourra soit ajouter `language` à `langList`, soit choisir pour `language` une des valeurs effectives de `langList` (sous réserve que ce dernier soit renseigné). Et si aucun de ces paramètres n'est défini, on pourra utiliser les mêmes valeurs par défaut que celles de la fonction `build_dict()`, à savoir `'fr'` pour `language` et `['fr', 'en']` pour `langList`. 


## Import de métadonnées depuis un fichier

### Effets

Cette fonctionnalité permet de remplacer les métadonnées de la table ou vue considérée par des métadonnées importées depuis un fichier. L'import ne fonctionnera que si les métadonnées sont encodées dans un format RDF et il ne donnera un résulat concluant que si elles respectent les profils DCAT, DCAT-AP ou GeoDCAT, ou le profil GeoDCAT étendu mis en oeuvre par le plugin.

L'import est réalisé via la fonction `rdf_utils.metagraph_from_file()`, puis le résultat est nettoyé avec la fonction `rdf_utils.clean_metagraph()` :

```python

try:
    raw_metagraph = rdf_utils.metagraph_from_file(filepath, format)
    metagraph = rdf_utils.clean_metagraph(raw_metagraph, shape, old_metagraph)
except:
    # notamment si ce n'était pas du RDF 
    ...

```

*`filepath` est le chemin complet du fichier source, *format* est le format RDF des métadonnées qu'il contient. Ces deux paramètres sont à spécifier par l'utilisateur. `shape` est le schéma SHACL de catégories communes (cf. [Génération du dictionnaire des widgets](/docs/source/usage/generation_dictionnaire_widgets.md#shape--le-schéma-shacl-des-métadonnées-communes)). `old_metagraph` est l'ancien graphe de métadonnées de la table, soit le `metagraph` actuel, dont la fonction récupère l'identifiant.*

Si le format n'est pas déterminé, la fonction est généralement capable de le déduire de l'extension du fichier (sinon elle renverra une erreur). Il serait donc admissible de ne pas le demander et se contenter de :

```python

try:
    raw_metagraph = rdf_utils.metagraph_from_file(filepath)
    metagraph = rdf_utils.clean_metagraph(raw_metagraph, shape, old_metagraph)
except:
    # notamment si ce n'était pas du RDF ou
    # si le format n'a pas pu être deviné
    ...

```

Il faudra ensuite régénérer le dictionnaire de widgets avec le nouveau graphe de métadonnées `metagraph` ainsi obtenu (cf. [Génération du dictionnaire des widgets](/docs/source/usage/generation_dictionnaire_widgets.md)), puis le formulaire à partir du dictionnaire de widgets mis à jour (cf. [Création d'un nouveau widget](/docs/source/usage/creation_widgets.md)).


### Caractéristiques du bouton

Ce bouton ne doit être actif qu'en mode édition.

Il utilise l'icône [import.svg](/plume/icons/general/import.svg) :
![import.svg](/plume/icons/general/import.svg)

Une implémentation possible serait d'utiliser un QToolButton avec un menu listant les formats disponibles.

Texte d'aide : *Importer les métadonnées depuis un fichier*.

La liste des formats autorisés est obtenue ainsi :

```python

importFormats = rdf_utils.import_formats()

```

Pour avoir la liste des extensions correspondant à un format :

```python

extensions = rdf_utils.import_extensions_from_format(format)

```

Pour avoir la liste de toutes les extensions reconnues :

```python

extensions = rdf_utils.import_extensions_from_format()

```


## Export des métadonnées dans un fichier

### Effets

Cette fonctionnalité permet d'exporter une sérialisation RDF de `metagraph` dans un fichier.

Elle fait appel à la fonction `rdf_utils.export_metagraph()`.

```python

try:
    rdf_utils.export_metagraph(metagraph, shape, filepath, format)
except:
    ...

```

*`metagraph` est le graphe des métadonnées (cf. [Génération du dictionnaire des widgets](/docs/source/usage/generation_dictionnaire_widgets.md#metagraph--le-graphe-des-métadonnées-pré-existantes)), `shape` est le schéma SHACL de catégories communes (cf. [Génération du dictionnaire des widgets](/docs/source/usage/generation_dictionnaire_widgets.md#shape--le-schéma-shacl-des-métadonnées-communes)), `filepath` est le chemin complet de la destination, `format` est le format RDF d'export. Les deux derniers paramètres sont à spécifier par l'utilisateur.*

Le contrôle d'erreur n'est pas aussi essentiel ici que pour l'import, mais on préférera être prudent. Un échec à l'export ne mérite pas un plantage du plugin.

C'est bien `metagraph` qui est exporté et non le contenu (potentiellement non sauvegardé) du formulaire.

### Caractéristiques du bouton

Ce bouton utilise l'icône [export.svg](/plume/icons/general/export.svg) :
![import.svg](/plume/icons/general/export.svg)

Texte d'aide : *Exporter les métadonnées dans un fichier*.

Une implémentation possible serait d'utiliser un QToolButton avec un menu listant les formats autorisés. Ceux-ci varient selon le contenu de `metagraph`. Pour obtenir la liste, on fera appel à la fonction `rdf_utils.available_formats()` :

```python

exportFormats = rdf_utils.available_formats(metagraph, shape)

```

Pour connaître l'extension associée par défaut à un format :

```python

extension = rdf_utils.export_extension_from_format(format)

```

## Réinitialisation

### Effets

Cette fonctionnalité permet de remplacer les métadonnées de la table ou vue considérée par un graphe vide.

On utilisera la commande suivante :

```python

metagraph = rdf_utils.copy_metagraph(None, old_metagraph)

```
*`old_metagraph` est l'ancien graphe de métadonnées de la table, soit le `metagraph` actuel, dont la fonction conserve l'identifiant.*

Il faudra ensuite régénérer le dictionnaire de widgets avec le nouveau graphe de métadonnées `metagraph` ainsi obtenu (cf. [Génération du dictionnaire des widgets](/docs/source/usage/generation_dictionnaire_widgets.md)), puis le formulaire à partir du dictionnaire de widgets mis à jour (cf. [Création d'un nouveau widget](/docs/source/usage/creation_widgets.md)).

### Caractéristiques du bouton

Ce bouton ne doit être actif qu'en mode édition.

Il utilise l'icône [empty.svg](/plume/icons/general/empty.svg) :
![empty.svg](/plume/icons/general/empty.svg)

Texte d'aide : *Vider la fiche de métadonnées*.


## Copier / coller d'une fiche complète

### Effets

Cette fonctionnalité permet à l'utilisateur de copier l'ensemble des métadonnées renseignées pour une table A vers une autre table B.

Concrètement :
- l'action *Copier* (sur la table A) mémorise le `metagraph` de la table A ;
- l'action *Coller* (sur la table B) régénère le dictionnaire de widgets en utilisant le graphe de mémorisé comme argument `metagraph` de `build_dict()` (cf. [Génération du dictionnaire des widgets](/docs/source/usage/generation_dictionnaire_widgets.md)), puis re-construit le formulaire en conséquence (cf. [Création d'un nouveau widget](/docs/source/usage/creation_widgets.md)).

Plus précisément, l'argument `metagraph` à fournir à `build_dict()` pour la table B est obtenu via :

```python

metagraph = rdf_utils.copy_metagraph(src_metagraph, old_metagraph)

```
*`old_metagraph` est l'ancien graphe de métadonnées de la table B, soit son `metagraph` actuel, dont la fonction conserve l'identifiant. `src_metagraph` est le graphe mémorisé de la table A.*



### Caractéristiques des boutons

Le bouton *Copier* est actif quel que soit le mode.

Icône : ![copy_all.svg](/plume/icons/general/copy_all.svg)

Texte d'aide : *Copier la fiche de métadonnées*.

Le bouton *Coller* n'est actif qu'en mode édition et si un graphe a été préalablement mémorisé.

Icône : ![paste_all.svg](/plume/icons/general/paste_all.svg)

Texte d'aide : *Coller la fiche de métadonnées mémorisée*.


## Sélection de la table à documenter

Au contraire de toutes les actions précédemment décrites, la sélection de la table ou vue dont l'utilisateur souhaite éditer les métadonnées se fait hors de l'interface du plugin, dans le panneau explorateur, le panneau des couches ou encore le panneau d'AsgardMenu.

### Si aucun objet n'est sélectionné

... il n'y a évidemment pas de métadonnées à afficher.

En principe, cette situation ne devrait se produire qu'à l'ouverture du plugin, lorsque l'utilisateur n'a pas préalablement cliqué sur une table ou vue dans l'un des panneaux pour la sélectionner.

Dans ce cas, on lui montre une interface vide, avec uniquement la barre de menus.

Les seuls boutons actifs sont alors :
- le bouton de choix du modèle ;
- le bouton de sélection de la langue principale ;
- le bouton de configuration de l'interface ;
- le bouton d'aide.

### Quand l'utilisateur sélectionne un nouvel objet

**Définir une nouvelle table source ne doit être possible qu'en mode lecture.** Il est important que l'utilisateur ne perde pas involontairement toutes ses modifications en cours à cause d'un clic malencontreux dans l'explorateur... Il n'est bien sûr pas question d'empêcher l'utilisateur de sélectionner des objets dans les panneaux de QGIS, mais le plugin ne devra pas le prendre en compte tant que le mode édition reste actif.

Lorsqu'une nouvelle tables ou vue est sélectionnée, le plugin devra d'abord extraire les métadonnées contenues dans son descriptif PostgreSQL - cf. [metagraph : le graphe des métadonnées pré-existantes](/docs/source/usage/generation_dictionnaire_widgets.md#metagraph--le-graphe-des-métadonnées-pré-existantes). Il faudra ensuite régénérer le dictionnaire de widgets avec le nouveau graphe de métadonnées `metagraph` ainsi obtenu (cf. [Génération du dictionnaire des widgets](/docs/source/usage/generation_dictionnaire_widgets.md)), puis le formulaire à partir du dictionnaire de widgets mis à jour (cf. [Création d'un nouveau widget](/docs/source/usage/creation_widgets.md)).

