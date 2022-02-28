# Métadonnées calculées

[Principe](#principe) • [Processus de calcul](#processus-de-calcul) • [Implémentation du calcul automatique](#implémentation-du-calcul-automatique) • [Implémentation du calcul à déclenchement manuel](#implémentation-du-calcul-à-déclenchement-manuel) 

Dans la suite, on considère :
- `widgetsdict` le dictionnaire contenant tous les widgets et leurs informations de paramétrage (cf. [Génération du dictionnaire des widgets](./generation_dictionnaire_widgets.md)), objet de classe `plume.rdf.widgetsdict.WidgetsDict`.
- `widgetkey` la clé de ce dictionnaire pour laquelle un calcul doit être réalisé, objet de classe `plume.rdf.widgetkey.WidgetKey`.

## Principe

Plume permet à l'administrateur de demander via ses modèles de formulaires à ce que certaines catégories de métadonnées puissent être mises à jour par un calcul côté serveur en plus de la saisie manuelle ordinaire. Ce calcul peut soit être exécuté automatiquement au chargement de la fiche de métadonnées (option `'auto'`), soit à la demande de l'utilisateur (option `'manual'`).

Les catégories pour lesquels le calcul est proposé sont, à ce stade :

| Chemin de la catégorie | Information calculée |
| --- | --- |
| `dct:conformsTo` | Tous les référentiels de coordonnées déclarés pour les géométries de la table ou vue. |

## Processus de calcul

Le calcul consiste en quatre opérations successives :
- vérifier que la base PostgreSQL cible dispose bien des extensions nécessaires au calcul ;
- générer la requête permettant d'obtenir les informations désirées et l'envoyer au serveur PostgreSQL ;
- intégrer le résultat dans le dictionnaire de widgets ;
- (selon les cas) répercuter les modifications sur les widgets.

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
                cur.execute(queries.query_exists_extension(), (extension,))
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

Le calcul automatique est effectué pendant la génération des widgets (cf. [Création d'un nouveau widget](./creation_widgets.md)) lorsque la valeur de la clé `'auto compute'` du dictionnaire interne est `True`. Ceci peut se produire pour un widget de saisie, mais aussi pour un groupe de valeurs.

```python

if widgetsdict[widgetkey]['auto compute']:
    ...

```

On suivra les étapes du [processus de calcul](#processus-de-calcul) décrit précédemment avec deux points d'attention :
- Lorsque la clé correspond à un widget de saisie, le calcul doit avoir lieu **avant la saisie de la valeur dans le widget**.
- Le dictionnaire renvoyé par la méthode `plume.rdf.widgetsdict.WidgetsDict.computing_update` **ne doit pas être considéré**, car les modifications résultant du calcul concernent des clés qui seront traitées ensuite.

## Implémentation du calcul à déclenchement manuel

Lorsque l'utilisateur clique sur un bouton de calcul du formulaire, toutes les étapes du [processus de calcul](#processus-de-calcul) sont à réaliser.

Cf. [Création d'un nouveau widget](./creation_widgets.md#widget-annexe--bouton-de-calcul) pour les modalités de création de ces boutons.


