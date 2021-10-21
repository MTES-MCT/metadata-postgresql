# Actions générales

Sont décrites ici les actions que l'utilisateur peut réaliser dans la partie fixe de l'interface du plugin. Pour les interactions de l'utilisateur avec les widgets du formulaire de saisie (ajout/suppression de valeurs, etc.), on se reportera à [Actions contrôlées par les widgets du formulaire](/__doc__/15_actions_widgets.md).

[Mode lecture, mode édition](#mode-lecture-mode-édition) • [Sauvegarde](#sauvegarde) • [Activation du mode traduction](#activation-du-mode-traduction) • [Choix de la trame de formulaire](#choix-de-la-trame-de-formulaire) • [Langue principale des métadonnées](#langue-principale-des-métadonnées) • [Import de métadonnées depuis un fichier](#import-de-métadonnées-depuis-un-fichier) • [Export des métadonnées dans un fichier](#export-des-métadonnées-dans-un-fichier) • [Réinitialisation](#réinitialisation) • [Sélection de la table à documenter](#sélection-de-la-table-à-documenter)

## Mode lecture, mode édition

### Effet sur le formulaire

Une fiche de métadonnées peut être ouverte :
- soit en **mode lecture**, qui permet de consulter les métadonnées mais pas de les modifier ;
- soit en **mode édition**, qui permet de modifier les métadonnées.

Du point de vue de l'utilisateur, le formulaire paraîtra très différent dans les deux modes. En mode lecture, tous les widgets de saisie sont désactivés (la clé `'read only'` du dictionnaire de widgets vaut toujours `True`). De plus, là où le mode édition affiche naturellement les champs sans valeur pour que l'utilisateur puisse les remplir, le mode lecture les masque (sauf si l'utilisateur a explicitement demandé le contraire en mettant à `False` le paramètre utilisateur `readHideBlank` - cf. [Paramètres utilisateur](/__doc__/20_parametres_utilisateurs.md)).

Concrètement, le passage d'un mode à l'autre implique simplement de regénérer le dictionnaire de widgets, c'est-à-dire relancer la fonction `build_dict()` en spécifiant le mode grâce au paramètre `mode` :
- `mode='edit'` en mode édition (ou rien, `'edit'` étant la valeur par défaut) ;
- `mode='read'` en mode lecture.

Cf. [Génération du dictionnaire des widgets](/__doc__/05_generation_dictionnaire_widgets.md).

Le formulaire de saisie/consultation peut ensuite être recréé à partir du nouveau dictionnaire, selon les mêmes modalités quel que soit le mode.

### Autres effets

Certaines des actions générales décrites dans la suite ne devraient être disponibles qu'en mode édition :
- la sauvegarde des modifications ;
- l'activation ou la désactivation du mode traduction ;
- l'import de métadonnées depuis un fichier ;
- la réinitialisation de la fiche.

### Caractéristiques du bouton

**Initialement, toutes les fiches s'ouvrent en mode lecture**. L'utilisateur doit cliquer sur le bouton d'activation du mode édition pour basculer dans ce dernier.

Le bouton utilise l'icône [edit.svg](/plume/icons/general/edit.svg) :
![edit.svg](/plume/icons/general/edit.svg).

L'idéal serait que le texte d'aide s'adapte au mode courant :

| Mode actif | Condition | Infobulle |
| --- | --- | --- |
| lecture | `if mode == 'read'` | *Basculer en mode édition* |
| édition | `if mode == 'edit'` | *Quitter le mode édition* |

Si toutefois cela s'avère complexe à mettre en oeuvre, on se contera de *Basculer en mode édition*.

Le bouton devra être inactif quand l'utilisateur ne dispose pas des droits nécessaires pour éditer les métadonnées de la table ou vue considérée, soit quand son rôle de connexion n'est pas membre du rôle propriétaire de l'objet.

Pour s'en assurer, on utilisera la requête définie par la fonction `query_is_relation_owner()` de [pg_queries.py](/plume/bibli_pg/pg_queries.py).

```python

import psycopg2
conn = psycopg2.connect(connection_string)

with conn:
	with conn.cursor() as cur:
	
		cur.execute(
			pg_queries.query_is_relation_owner(),
			(schema_name, table_name)
			)
		res = cur.fetchone()
		is_owner = res[0] if res else False

conn.close()

```

*`connection_string` est la chaîne de connexion à la base de données PostgreSQL, `table_name` est le nom de la table ou vue dont on affiche les métadonnées, `schema_name` est le nom de son schéma.*


## Sauvegarde

### Effets

Le **bouton de sauvegarde** permet à l'utilisateur d'enregistrer sur le serveur PostgreSQL les informations qu'il a saisies.

En arrière plan, cela suppose plusieurs opérations successives.

1. Enregistrer dans le dictionnaire de widgets les valeurs contenues dans les widgets de saisie. On utilisera pour ce faire la méthode `update_value()`.

Cette méthode ne doit être exécutée que sur des widgets de saisie non masqué, soit (les deux modes de gestion sont possibles) quand la clé `'object'` vaut `'edit'` ou lorsque `'main widget type'` est un widget de saisie. 

Soit :
- `key` la clé du widget de saisie dans le dictionnaire de widgets `widgetsdict` ;
- `widget_value` la valeur contenue dans le widget (QWidget).

Pour les widgets de saisie, on exécutera donc :

```python

if not ( widgetsdict[key]['hidden'] or widgetsdict[key]['hidden M'] ):
    widgetsdict.update_value(key, widget_value)

```

2. Générer un graphe RDF à partir du dictionnaire de widgets actualisé.

```python

new_metagraph = widgetsdict.build_graph(vocabulary, language)

```

*`vocabulary` est la compilation de thésaurus qui a servi à créer le dictionnaire de widgets. `language` est le paramètre utilisateur correspondant à la langue principale de saisie des métadonnées.*

3. Créer une version actualisée du descriptif PostgreSQL de l'objet.

Soit `old_pg_description` le descriptif/commentaire original.

```python

new_pg_description = rdf_utils.update_pg_description(old_pg_description, new_metagraph)

```

4. Envoyer au serveur PostgreSQL une requête de mise à jour du descriptif.

On utilisera la requête définie par la fonction `query_update_table_comment()` de [pg_queries.py](/plume/bibli_pg/pg_queries.py). À noter que, dans la mesure où les commandes diffèrent selon le type de relation, il est nécessaire de commencer par récupérer cette information avec `query_get_relation_kind()`.

```python

import psycopg2
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
        cur.execute(query, (new_pg_description,))

conn.close()

```

*`connection_string` est la chaîne de connexion à la base de données PostgreSQL, `table_name` est le nom de la table ou vue dont on édite les métadonnées, `schema_name` est le nom de son schéma.*

5. Mettre à jour les descriptifs des champs.

La requête de mise à jour est directement déduite du dictionnaire de widgets par la fonction `query_update_columns_comments()` de [pg_queries.py](/plume/bibli_pg/pg_queries.py).

```python

import psycopg2
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
- *si la liste des champs `columns` n'a pas été fournie en argument de `build_dict()` ;*
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

Cf. [Génération du dictionnaire des widgets](/__doc__/05_generation_dictionnaire_widgets.md).

Le formulaire peut ensuite être regénéré à partir du nouveau dictionnaire, selon les mêmes modalités que le mode traduction soit actif ou non (cf. [Création d'un nouveau widget](/__doc__/10_creation_widgets.md)).

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

Le modèle de formulaire détermine les catégories de métadonnées affichées dans le formulaire et la manière dont elles sont présentées - cf [Modèles de formulaire](/__doc__/08_modeles_de_formulaire.md).

Dès lors que des modèles sont disponibles, c'est-à-dire que `templateLabels` n'est pas `None` ou une liste vide (cf. [Modèles de formulaire](/__doc__/08_modeles_de_formulaire.md), étape [Récupération de la liste des modèles](/__doc__/08_modeles_de_formulaire.md#récupération-de-la-liste-des-modèles)), l'utilisateur doit avoir la possibilité de basculer à tout moment d'un modèle pré-défini à l'autre ou de ne pas appliquer de modèle du tout.

Dans ce dernier cas, on aurait :

```python

template = None
templateTabs = None

```

Sinon `template` et `templateTabs` devront être générés à partir du nom du modèle sélectionné (`tpl_label`), en suivant la méthode décrite dans [Modèles de formulaire](/__doc__/08_modeles_de_formulaire.md#récupération-de-la-liste-des-modèles) (étape [Récupération des catégories associées au modèle retenu](/__doc__/08_modeles_de_formulaire.md#récupération-des-catégories-associées-au-modèle-retenu) et suivantes).

Dans tous les cas, il faudra réexécuter `build_dict()` avec les nouveaux paramètres pour `template` et `templateTabs`, puis recréer le formulaire à partir du dictionnaire de widgets actualisé ainsi obtenu.

### Caractéristiques du widget

Le widget de sélection du modèle pourra être soit un QComboBox soit un QToolButton similaire aux boutons de sélection de la source du formulaire (cf. [Création d'un nouveau widget](/__doc__/10_creation_widgets.md#widget-annexe--bouton-de-sélection-de-la-source)).

Les valeurs disponibles sont les noms de modèles listés par `templateLabels`, auxquelles ont ajoutera un item `'Aucun modèle'` (ou autre nom similaire).

Si `templateLabels` est `None` ou une liste vide, il n'y a pas lieu d'afficher le widget. `template` et `templateTabs` vaudront simplement toujours `None`.

D'autant que de besoin, le bouton utilise l'icône [template.svg](/plume/icons/general/template.svg) :
![template.svg](/plume/icons/general/template.svg)

Texte d'aide : *Choisir un modèle de formulaire*.

### Initialisation

La démarche à suivre à l'ouverture d'une fiche de métadonnées, est décrite dans [Modèles de formulaire](/__doc__/08_modeles_de_formulaire.md#import-par-le-plugin). On commencera par récupérer les paramètres `preferedTemplate` et `enforcePreferedTemplate` dans les fichiers de configuration, si tant est qu'ils soient présents.


## Langue principale des métadonnées

### Effets

La langue principale de métadonnées correspond au paramètre utilisateur `language` que prennent en entrée de nombreuses fonctions et méthodes de [rdf_utils.py](/plume/bibli_rdf/rdf_utils.py).

Hors mode traduction, toutes les métadonnées saisies qui ne soient pas des dates, nombres, URL ou autres types qui ne sont pas supposés avoir une langue seront présumées être dans cette langue. C'est aussi dans cette langue que seront affichées les valeurs issues des thésaurus (autant que possible, car les thésaurus ne contiennent pas de traductions pour toutes les langues imaginables).

Lorsque l'utilisateur modifie la langue principale, il est nécessaire de regénérer le dictionnaire de widgets avec la nouvelle valeur de `language` (cf. [Génération du dictionnaire des widgets](/__doc__/05_generation_dictionnaire_widgets.md)), puis le formulaire à partir du dictionnaire de widgets mis à jour (cf. [Création d'un nouveau widget](/__doc__/10_creation_widgets.md)).

### Caractéristiques du widget

Le widget de choix de la langue principale pourra être soit un QComboBox soit un QToolButton similaire aux boutons de sélection de la langue du formulaire (cf. [Création d'un nouveau widget](/__doc__/10_creation_widgets.md#widget-annexe--bouton-de-sélection-de-la-langue)). Dans les deux cas, les valeurs disponibles sont les langues listées par le paramètre utilisateur `langList`.

Texte d'aide : *Modifier la langue principale des métadonnées*.

### Initialisation

Le paramètre `language` pourra être systématiquement sauvegardé dans le fichier `QGIS3.ini`, et initialisé à l'activation du plugin à partir de la valeur récupérée dans les fichiers de configuration.

Un point important est que `language` doit toujours être l'une des langues listées par le paramètre utilisateur `langList`. Si ce n'est pas le cas avec les valeurs issues des fichiers de configuration, on pourra soit ajouter `language` à `langList`, soit choisir pour `language` une des valeurs effectives de `langList` (sous réserve que ce dernier soit renseigné). Et si aucun de ces paramètres n'est défini, on pourra utiliser les mêmes valeurs par défaut que celles de la fonction `build_dict()`, à savoir `'fr'` pour `language` et `['fr', 'en']` pour `langList`. 


## Import de métadonnées depuis un fichier

### Effets

Cette fonctionnalité permet de remplacer les métadonnées de la table ou vue considérée par des métadonnées importées depuis un fichier. L'import ne fonctionnera que si les métadonnées sont encodées dans un format RDF et il ne donnera un résulat concluant que si elles respectent les profils DCAT, DCAT-AP ou GeoDCAT, ou le profil GeoDCAT étendu mis en oeuvre par le plugin.

L'import est réalisé via la fonction `rdf_utils.metagraph_from_file()` :

```python

try:
    metagraph = rdf_utils.metagraph_from_file(filepath, format)
except:
    # notamment si ce n'était pas du RDF 
    ...

```

*`filepath` est le chemin complet du fichier source, *format* est le format RDF des métadonnées, parmi `"turtle"`, `"json-ld"`, `"xml"`, `"n3"`, `"nt"`, `"trig"`. Ces deux paramètres sont à spécifier par l'utilisateur.*

Si le format n'est pas déterminé, la fonction est généralement capable de le déduire de l'extension du fichier (sinon elle renverra une erreur). Il serait donc admissible de ne pas le demander et se contenter de :

```python

try:
    metagraph = rdf_utils.metagraph_from_file(filepath)
except:
    # notamment si ce n'était pas du RDF ou
    # si le format n'a pas pu être deviné
    ...

```

Il faudra ensuite régénérer le dictionnaire de widgets avec le nouveau graphe de métadonnées `metagraph` ainsi obtenu (cf. [Génération du dictionnaire des widgets](/__doc__/05_generation_dictionnaire_widgets.md)), puis le formulaire à partir du dictionnaire de widgets mis à jour (cf. [Création d'un nouveau widget](/__doc__/10_creation_widgets.md)).

### Caractéristiques du bouton

Ce bouton ne doit être actif qu'en mode édition.

Il utilise l'icône [import.svg](/plume/icons/general/import.svg) :
![import.svg](/plume/icons/general/import.svg)

Une implémentation possible serait d'utiliser un QToolButton avec un menu listant les formats disponibles.

Texte d'aide : *Importer les métadonnées depuis un fichier*.

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

*`metagraph` est le graphe des métadonnées (cf. [Génération du dictionnaire des widgets](/__doc__/05_generation_dictionnaire_widgets.md#metagraph--le-graphe-des-métadonnées-pré-existantes)), `shape` est le schéma SHACL de catégories communes (cf. [Génération du dictionnaire des widgets](/__doc__/05_generation_dictionnaire_widgets.md#shape--le-schéma-shacl-des-métadonnées-communes)), `filepath` est le chemin complet de la destination, `format` est le format RDF d'export. Les deux derniers paramètres sont à spécifier par l'utilisateur.*

Le contrôle d'erreur n'est pas aussi essentiel ici que pour l'import, mais on préférera être prudent. Un échec à l'export ne mérite pas un plantage du plugin.

Les formats autorisés varient selon le contenu de `metagraph`. Pour obtenir la liste, on fera appel à la fonction `rdf_utils.available_formats()` :

```python

exportFormats = rdf_utils.available_formats(metagraph, shape)

```

C'est bien `metagraph` qui est exporté et non le contenu (potentiellement non sauvegardé) du formulaire.

### Caractéristiques du bouton

Ce bouton utilise l'icône [export.svg](/plume/icons/general/export.svg) :
![import.svg](/plume/icons/general/export.svg)

Une implémentation possible serait d'utiliser un QToolButton avec un menu listant les formats autorisés.

Texte d'aide : *Exporter les métadonnées dans un fichier*.

## Réinitialisation

### Effets

Cette fonctionnalité permet de remplacer les métadonnées de la table ou vue considérée par un graphe vide.

On utilisera la commande suivante :

```python

metagraph = rdf_utils.metagraph_from_pg_description('', shape)

```
*`shape` est le schéma SHACL de catégories communes (cf. [Génération du dictionnaire des widgets](/__doc__/05_generation_dictionnaire_widgets.md#shape--le-schéma-shacl-des-métadonnées-communes)).*

Il faudra ensuite régénérer le dictionnaire de widgets avec le nouveau graphe de métadonnées `metagraph` ainsi obtenu (cf. [Génération du dictionnaire des widgets](/__doc__/05_generation_dictionnaire_widgets.md)), puis le formulaire à partir du dictionnaire de widgets mis à jour (cf. [Création d'un nouveau widget](/__doc__/10_creation_widgets.md)).

### Caractéristiques du bouton

Ce bouton ne doit être actif qu'en mode édition.

Il utilise l'icône [empty.svg](/plume/icons/general/empty.svg) :
![empty.svg](/plume/icons/general/empty.svg)

Texte d'aide : *Vider la fiche de métadonnées*.


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

Lorsqu'une nouvelle tables ou vue est sélectionnée, le plugin devra d'abord extraire les métadonnées contenues dans son descriptif PostgreSQL - cf. [metagraph : le graphe des métadonnées pré-existantes](/__doc__/05_generation_dictionnaire_widgets.md#metagraph--le-graphe-des-métadonnées-pré-existantes). Il faudra ensuite régénérer le dictionnaire de widgets avec le nouveau graphe de métadonnées `metagraph` ainsi obtenu (cf. [Génération du dictionnaire des widgets](/__doc__/05_generation_dictionnaire_widgets.md)), puis le formulaire à partir du dictionnaire de widgets mis à jour (cf. [Création d'un nouveau widget](/__doc__/10_creation_widgets.md)).


