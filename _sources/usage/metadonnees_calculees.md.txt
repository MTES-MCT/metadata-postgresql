# Métadonnées calculées

[Principe](#principe) • [Processus de calcul](#processus-de-calcul) • [Implémentation du calcul automatique](#implémentation-du-calcul-automatique) • [Implémentation du calcul à déclenchement manuel](#implémentation-du-calcul-à-déclenchement-manuel) 

## Principe

Plume permet à l'administrateur de demander via ses modèles de formulaires à ce que certaines catégories de métadonnées puissent être mises à jour par un calcul côté serveur en plus de la saisie manuelle ordinaire. Ce calcul peut soit être exécuté automatiquement au chargement de la fiche de métadonnées (options `'auto'`, `'new'` ou `'empty'`), soit à la demande de l'utilisateur (option `'manual'`).

Les catégories pour lesquelles le calcul est proposé sont, à ce stade :

| Chemin de la catégorie | Information calculée | Paramètres optionnels | Dépendances |
| --- | --- | --- | --- |
| `dct:conformsTo` | Tous les référentiels de coordonnées déclarés pour les géométries de la table ou vue. | Aucun. | L'extension PostGIS doit être active sur la base. |
| `dct:description` | Importe le contenu du descriptif PostgreSQL de l'objet[^extrait-descriptif], soit dans son intégralité, soit en utilisant une expression régulière. |  `pattern` est l'expression régulière spécifiant l'extrait du descriptif à importer[^doc-pattern]. Si l'expression renvoie plusieurs fragments, seul le premier est conservé. S'il y a lieu, `flags` contient les paramètres associés à l'expression régulière[^doc-flags]. `pattern` et `flags` correspondent précisément aux paramètres de même nom de la fonction ` regexp_matches(text, text, text)` de PostgreSQL, qui est en fait utilisée pour l'opération. | L'extension *PlumePg* doit être active sur la base. |
| `dct:title` | Idem `dct:description`. | Idem. | Idem. |
| `dct:created` | La date de création de la table si l'information est présente dans la table `z_plume.stamp.timestamp`. | Aucun. | L'extension *PlumePg* doit être active sur la base[^activation-suivi-dates]. |
| `dct:modified` | La date de dernière modification de la table si l'information est présente dans la table `z_plume.stamp.timestamp`. | Aucun. | L'extension *PlumePg* doit être active sur la base[^activation-suivi-dates]. |

[^extrait-descriptif]: Si des métadonnées ont déjà été saisies pour la table, seule la partie du descriptif qui précède la balise `<METADATA>` sera considérée.

[^doc-pattern]: Pour plus de détails, on se reportera à la documentation de PostgreSQL sur les expressions régulières. Par exemple, pour PostgreSQL 12 : https://www.postgresql.org/docs/12/functions-matching.html#FUNCTIONS-POSIX-REGEXP.

[^doc-flags]: Les valeurs acceptées sont les mêmes que pour les arguments `flags` des fonctions d'expressions régulières de PostgreSQL. Pour PostgreSQL 12 : https://www.postgresql.org/docs/12/functions-matching.html#POSIX-EMBEDDED-OPTIONS-TABLE.

[^activation-suivi-dates]: Il est également recommandé d'avoir [activé les fonctionnalités d'enregistrement des dates](#activation-de-lenregistrement-des-dates), sans quoi le calcul ne renverra jamais rien.

Les paramètres optionnels sont spécifiés via le champ `compute_params` des tables `z_plume.meta_categorie` et `z_plume.meta_template_categories`. Il s'agit d'un champ de type `jsonb`, qui attend un dictionnaire dont les clés sont les noms des paramètres et les valeurs les valeurs des paramètres.

Par exemple :

```sql

UPDATE z_plume.meta_categorie
    SET compute = ARRAY['new'],
        compute_params = '{"pattern": "^[\\w\\s]+"}'::jsonb
    WHERE path = 'dct:title' ;

```

Les trois modes de calcul automatique opèrent comme suit :
- Avec `'auto'`, le calcul est effectué systématiquement à l'ouverture de la fiche de métadonnées ou lorsqu'elle est re-générée par une réinitialisation, un import, une copie... Il n'est pas exécuté lorsque le formulaire est reconstruit après une sauvegarde.
- Avec `'empty'`, le calcul est effectué dans les mêmes conditions que pour `'auto'`, avec une condition supplémentaire : le widget ou le groupe de widgets ne doit contenir aucune valeur.
- Avec `'new'`, le calcul n'est effectué que si la fiche de métadonnées est entièrement vide[^quasi-vide], soit dans le cas d'une table dont le descriptif ne contenait par encore de métadonnées, dans le cas d'une réinitialisation ou encore dans le cas de l'import d'une fiche vide.

[^quasi-vide]: Incluant les fiches qui ne comportent que les champs mis à jour automatiquement, soit l'identifiant et/ou la date de dernière modification.

Si plusieurs de ces modes sont spécifiés simultanément, `'auto'` prévaut sur `'empty'`, qui prévaut sur `'new'`.

Avec ``'manual'``, un bouton de calcul ![compute_button.svg](../../../plume/icons/buttons/compute_button.svg) apparaîtra à droite du champ de saisie de la métadonnées dans le formulaire. Cliquer sur ce bouton importe les informations désirées du serveur. Pour les catégories admettant plusieurs valeurs, le bouton porte sur l'ensemble du groupe.

Les boutons de calcul ne sont présents qu'en mode édition, par contre le calcul automatique opère aussi bien en mode édition qu'en mode lecture. Une catégorie sur laquelle une fonctionnalité de calcul automatique est définie apparaîtra toujours dans le formulaire, même lorsque le calcul ne renvoie aucune valeur et que le paramétrage prévoit que les catégories sans valeur ne soient pas affichées (comportement par défaut en mode lecture[^hideblank]).

[^hideblank]: Cf. `readHideBlank` dans la [liste des paramètres utilisateur](./parametres_utilisateur.md).

## Processus de calcul

Le calcul consiste en quatre opérations successives :
- vérifier que la base PostgreSQL cible dispose bien des extensions nécessaires au calcul ;
- générer la requête permettant d'obtenir les informations désirées et l'envoyer au serveur PostgreSQL ;
- intégrer le résultat dans le dictionnaire de widgets ;
- (selon les cas) répercuter les modifications sur les widgets.

Dans la suite, on considère :
- `widgetsdict` le dictionnaire contenant tous les widgets et leurs informations de paramétrage (cf. [Génération du dictionnaire des widgets](./generation_dictionnaire_widgets.md)), objet de classe `plume.rdf.widgetsdict.WidgetsDict`.
- `widgetkey` la clé de ce dictionnaire pour laquelle un calcul doit être réalisé, objet de classe `plume.rdf.widgetkey.WidgetKey`.

### Contrôle des extensions disponibles

La liste des extensions PostgreSQL nécessaires à l'exécution du calcul est fournie par l'attribut `dependances` de l'objet `plume.pg.computer.ComputationMethod` contenu dans la clé `'compute method'` du dictionnaire interne. Il peut s'agir d'une liste vide si le calcul ne requiert aucune extension.

Pour déterminer si les extensions sont bien installées sur la base source de la table ou vue considérée, on pourra utiliser la requête renvoyée par la fonction `plume.pg.queries.query_exists_extension`.

```python

import psycopg2
from plume.pg import queries

dependances = widgetsdict[widgetkey]['compute method'].dependances

if dependances:
    conn = psycopg2.connect(connection_string)
    dependances_ok = True
    with conn:
        with conn.cursor() as cur:
            for extension in dependances:
                cur.execute(*queries.query_exists_extension(extension))
                dependances_ok = dependances_ok and cur.fetchone()[0]
                if not dependances_ok:
                    break
    conn.close()

```

Si `dependances_ok` vaut `True`, il est possible de passer à l'étape suivante. Sinon il faudra interrompre le processus, et vraisemblablement alerter l'utilisateur qu'une au moins des extensions requises est absente.

### Génération et exécution de la requête

La requête de calcul est construite par la méthode `computing_query` de la classe `plume.rdf.widgetsdict.WidgetsDict`. Celle-ci renvoie un tuple contenant tous les arguments à fournir à `psycopg2.cursor.execute` (contrairement à la plupart des fonctions du module `plume.pg.queries` qui ne renvoient que la requête à proprement parler).

```python

import psycopg2

conn = psycopg2.connect(connection_string)

with conn:
    with conn.cursor() as cur:
        query = widgetsdict.computing_query(widgetkey, schema_name, table_name)
        cur.execute(*query)
        result = cur.fetchall()
conn.close()

```

*`table_name` est le nom de la table ou vue à documenter. `schema_name` est le nom de son schéma.*

### Intégration du résultat

Le résultat de la requête, soit `result` dans l'exemple de code ci-avant, peut maintenant alimenter le dictionnaire de widgets et son arbre de clés. C'est l'objet de la méthode `computing_update` de la classe `plume.rdf.widgetsdict.WidgetsDict`.

```python

r = widgetsdict.computing_update(widgetkey, result)

```

### Modification des widgets en conséquence

Quand le calcul est réalisé alors que le formulaire est déjà intégralement constitué (cas du [calcul à déclenchement manuel](#implémentation-du-calcul-à-déclenchement-manuel)), les modifications effectuées par `WidgetsDict.computing_update` sur le dictionnaire et son arbre de clés doivent être répercutées sur les widgets eux-mêmes.

Pour ce faire, `WidgetsDict.computing_update` renvoie, comme toutes les méthodes d'interaction avec le formulaire, un dictionnaire contenant toutes les informations de matérialisation. Cf. [Actions contrôlées par les widgets du formulaire](./actions_widgets.md#structuration-des-dictionnaires-contenant-les-informations-de-matérialisation) pour plus de détails.

## Implémentation du calcul automatique

Le calcul automatique est la première étape de la matérialisation d'un formulaire, juste avant la [génération des widgets](./creation_widgets.md).

Il s'agit là aussi de boucler sur les clés du dictionnaire de widgets pour exécuter les calculs, mais on utilisera pour ce faire un générateur spécifique, `plume.rdf.widgetsdict.WidgetsDict.items_to_compute` au lieu de `dict.items`. Ce générateur ne considère que les clés nécessitant un calcul (la clé `'auto compute'` de leur dictionnaire interne vaut `True`) et utilise une copie du dictionnaire de widgets, afin d'autoriser l'ajout ou la suppression de clés dans le dictionnaire d'origine au cours du traitement.

```python

for widgetkey, internaldict in widgetsdict.items_to_compute():
    ...

```

*`internaldict` est le dictionnaire interne de la clé `widgetkey`, soit `widgetsdict[widgetkey]`.*

À chaque itération, on suivra toutes les étapes du [processus de calcul](#processus-de-calcul) **à l'exception de [la dernière](#modification-des-widgets-en-conséquence)**. Le dictionnaire renvoyé par la méthode `plume.rdf.widgetsdict.WidgetsDict.computing_update` est inutile ici puisque le formulaire n'a pas encore été matérialisé.

## Implémentation du calcul à déclenchement manuel

Lorsque l'utilisateur clique sur un bouton de calcul du formulaire, toutes les étapes du [processus de calcul](#processus-de-calcul) sont à réaliser.

Cf. [Création d'un nouveau widget](./creation_widgets.md#widget-annexe--bouton-de-calcul) pour les modalités de création de ces boutons.


