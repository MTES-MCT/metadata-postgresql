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

Le formulaire de saisie/consultation peut ensuite être recréé à partir du nouveau dictionnaire, selon les mêmes modalités quel que soit le mode.

### Autres effets

Certaines des actions générales décrites dans la suite ne devraient être disponibles qu'en mode édition :
- la sauvegarde des modifications ;
- l'activation ou la désactivation du mode traduction ;
- l'import de métadonnées depuis un fichier.

## Bouton de sauvegarde

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

Cette action sort du périmètres des fonctions de RDF Utils. On utilisera la requête définie par la fonction `query_update_table_comment()` de [pg_queries.py](/metadata_postgresql/bibli_pg/pg_queries.py).

Soit :
- `schema_name` le nom du schéma contenant la table dont on édite les métadonnées ;
- `table_name` le nom de cette dernière ;
- `cur` le nom d'un curseur ouvert sur la connexion psycopg2 au serveur PostgreSQL. 

```python

query = query_update_table_comment(schema_name, table_name)
cur.execute(query, (new_pg_description,))

```

## Activation du mode traduction

Lorsque le mode traduction est actif, l'utilisateur a la possibilité de définir la langue des valeurs qu'il saisit (sinon c'est le paramètre utilisateur `language` qui est systématiquement utilisé).

## Choix de la trame de formulaire

## Langue principale des métadonnées

## Import de métadonnées depuis un fichier

## Export des métadonnées dans un fichier

