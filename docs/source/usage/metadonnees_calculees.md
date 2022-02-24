# Métadonnées calculées

[Principe](#principe) • [Processus de calcul](#processus-de-calcul) • [Implémentation du calcul automatique](#implémentation-du-calcul-automatique) • [Implémentation du calcul à déclenchement automatique](#implémentation-du-calcul-à-déclenchement-automatique) 

Dans la suite, on considère :
- `widgetsdict` le dictionnaire contenant tous les widgets et leurs informations de paramétrage (cf. [Génération du dictionnaire des widgets](/docs/source/usage/generation_dictionnaire_widgets.md)), objet de classe [`plume.rdf.widgetsdict.WidgetsDict`](/plume/rdf/widgetsdict.py).
- `widgetkey` la clé de ce dictionnaire pour laquelle un calcul doit être réalisé, objet de classe [`plume.rdf.widgetkey.WidgetKey`](/plume/rdf/widgetkey.py).

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

La liste des extensions PostgreSQL nécessaires à l'exécution du calcul est fournie par l'attribut `dependances` de l'objet [`plume.pg.computer.ComputationMethod`](/plume/pg/computer.py) contenu dans la clé `'compute method'` du dictionnaire interne. Il peut s'agir d'une liste vide si le calcul ne requiert aucune extension.

Pour déterminer si les extensions sont bien installées sur la base source de la table ou vue considérée, on pourra utiliser la requête renvoyée par la fonction [`plume.pg.queries.query_exists_extension`](/plume/pg/queries.py).

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

### Intégration du résultat

### Modification des widgets en conséquence

## Implémentation du calcul automatique

Le calcul automatique est effectué pendant la génération des widgets (cf. [Création d'un nouveau widget](/docs/source/usage/creation_widgets.md)) lorsque la valeur de la clé `'auto compute'` du dictionnaire interne est `True`. Ceci peut se produire pour un widget de saisie, mais aussi pour un groupe de valeurs.

```python

if widgetsdict[widgetkey]['auto compute']:
    ...

```

On suivra les étapes du [processus de calcul](#processus-de-calcul) décrit précédemment avec deux points d'attention :
- Lorsque la clé correspond à un widget de saisie, le calcul doit avoir lieu **avant la saisie de la valeur dans le widget**.
- Le dictionnaire d'actions renvoyé par la méthode `plume.rdf.widgetsdict.WidgetsDict.computing_update` **ne doit pas être considéré**, car les modifications résultant du calcul concernent des clés qui seront de toute façon traitées ensuite.

## Implémentation du calcul à déclenchement manuel

