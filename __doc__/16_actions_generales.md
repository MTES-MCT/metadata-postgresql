# Actions générales

Sont décrites ici les actions que l'utilisateur peut réaliser dans la partie fixe de l'interface du plugin. Pour les interactions de l'utilisateur avec les widgets du formulaire de saisie (ajout/suppression de valeurs, etc.), on se reportera à [Actions contrôlées par les widgets du formulaire](/__doc__/15_actions_widgets.md).

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
- l'import de métadonnées depuis un fichier.

### Caractéristiques du bouton

**Initialement, toutes les fiches s'ouvrent en mode lecture**. L'utilisateur doit cliquer sur le bouton d'activation du mode édition pour basculer dans ce dernier.

Le bouton utilise l'icône [edit.svg](/metadata_postgresql/icons/general/edit.svg) :
![edit.svg](/metadata_postgresql/icons/general/edit.svg).

Il ne devra être inactif quand l'utilisateur ne dispose pas des droits nécessaires pour éditer les métadonnées de la table ou vue considérée, soit quand son rôle de connexion n'est pas membre du rôle propriétaire de l'objet.

Pour s'en assurer, on utilisera la requête définie par la fonction `query_is_relation_owner()` de [pg_queries.py](/metadata_postgresql/bibli_pg/pg_queries.py).

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

Soit :
- `key` la clé du widget de saisie dans le dictionnaire de widgets `widgetsdict` ;
- `value` la valeur contenue dans le widget (QWidget).

On exécutera :

```python

widgetsdict.update_value(key, value)

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

On utilisera la requête définie par la fonction `query_update_table_comment()` de [pg_queries.py](/metadata_postgresql/bibli_pg/pg_queries.py).

```python

import psycopg2
conn = psycopg2.connect(connection_string)

with conn:
	with conn.cursor() as cur:
	
		query = query_update_table_comment(schema_name, table_name)
		cur.execute(query, (new_pg_description,))

conn.close()

```

*`connection_string` est la chaîne de connexion à la base de données PostgreSQL, `table_name` est le nom de la table ou vue dont on édite les métadonnées, `schema_name` est le nom de son schéma.*

### Caractéristiques du bouton

Comme susmentionné, ce bouton ne doit être actif qu'en mode édition.

Il utilise l'icône [save.svg](/metadata_postgresql/icons/general/save.svg) :
![save.svg](/metadata_postgresql/icons/general/save.svg)


## Activation du mode traduction

### Effets

Lorsque le mode traduction est actif, l'utilisateur a la possibilité de définir la langue des valeurs qu'il saisit (sinon c'est le paramètre utilisateur `language` qui est systématiquement utilisé). Il pourra également saisir des traductions pour des catégories qui n'acceptent qu'une valeur par langue (par exemple le libellé de la donnée).

Concrètement, l'activation ou la désactivation du mode traduction impliquera de regénérer le dictionnaire de widgets, c'est-à-dire relancer la fonction `build_dict()` avec :
- `translation=True` si le mode traduction est actif ;
- `translation=False` s'il ne l'est pas (ou sans spécifier `translation`, `False` étant la valeur par défaut).

Cf. [Génération du dictionnaire des widgets](/__doc__/05_generation_dictionnaire_widgets.md).

Le formulaire peut ensuite être recréé à partir du nouveau dictionnaire, selon les mêmes modalités que le mode traduction soit actif ou non.

### Caractéristiques du bouton

Ce bouton ne doit être actif qu'en mode édition.

Il utilise l'icône [translation.svg](/metadata_postgresql/icons/general/translation.svg) :
![translation.svg](/metadata_postgresql/icons/general/translation.svg)

## Choix de la trame de formulaire

## Langue principale des métadonnées

## Import de métadonnées depuis un fichier

## Export des métadonnées dans un fichier

