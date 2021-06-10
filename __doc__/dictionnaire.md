# Mode d'emploi du dictionnaire des widgets

## La fonction buildDict

Le dictionnaire de paramétrage est créé par la fonction `buildDict` de *rdf_utils.py*.

Cette fonction exploite des informations issues de quatre sources :
- un **graphe RDF contenant les métadonnées** associées au jeu de données dont on souhaite éditer/visualiser les métadonnées. Issu de la dé-sérialisation du JSON-LD contenu dans le descriptif de la table ou vue PostgreSQL, ce graphe fournit principalement les valeurs à placer dans les widgets d'édition.
- un **graphe RDF contenant le vocabulaire** de toutes les ontologies dans lesquelles les catégories du graphe puisent leurs valeurs.
- un **schéma SHACL** (augmenté de propriétés sur-mesure pour le formulaire) décrivant les catégories de métadonnées communes.
- éventuellement, un dictionnaire définissant un **modèle de formulaire** choisi par l'utilisateur.

## Les arguments de buildDict

### Le graphe RDF de métadonnées

### Le schéma SHACL

### Le modèle de formulaire

Fournir un modèle de formulaire permet :
- d'ajouter des métadonnées locales aux catégories communes du schéma SHACL ;
- de restreindre les catégories communes à afficher dans le formulaire. Concrètement, dès lors qu'un modèle est fourni, n'apparaîtront dans le formulaire que les catégories qu'il cite et/ou pour lesquelles des valeurs avaient préalablement été saisies ;
- de substituer des paramètres locaux à ceux spécifiés par le schéma SHACL (par exemple remplacer le nom à afficher pour la catégorie de métadonnée ou changer le type de widget à utiliser).
    
La structure attendue pour le modèle de formulaire est proche de celle du dictionnaire résultant de `buildDict`, si ce n'est que :
- ses clés sont des chemins SPARQL identifiant des catégories de métadonnées. Par exemple `dcat:contactPoint / vcard:hasEmail` pour l'adresse mél du point de contact ;
- ses dictionnaires internes comprennent nettement moins de clés.

Exemple :

```python
{
    "dct:title": {
    },
    "dct:description": {
        "label": "résumé",
        "row span": 15
    }    
}
```
*Le modèle ci-avant ne prévoit que deux catégories de métadonnées : le libellé et la description du jeu de données. Pour la description, elle définit un nouveau libellé, "résumé", et prévoit une hauteur de 15 lignes pour le QTextEdit.*

Le fichier *exemples/exemple_dict_modele_local.json* fournit un exemple plus complet de modèle de formulaire sérialisé en json.

Il n'est pas nécessaire que toutes les clés soient présentes pour toutes les catégories (la fonction utilise systématiquement la méthode `get` pour interroger le formulaire).

Certains caractéristiques ne peuvent être re-définies pour les catégories de métadonnées communes : il n'est pas possible de changer le type de valeur d'une métadonnée commune, par exemple, tandis que le service est libre de spécifier un type pour ses métadonnées locales. Concrètement la fonction ignorera les clés `multiple values` et `data type` lorsqu'elle traite des catégories communes.

| Clé | Description | Valeurs autorisées | Remarques |
| --- | --- | --- | --- |
| `'main widget type'` | type de widget de saisie | `'QLineEdit'` (valeur par défaut), `'QTextEdit'`, `'QDateEdit'`, `'QTimeEdit'`, `'QDateTimeEdit'`, `'QCheckBox'`  |  |
| `'row span'` | hauteur du widget, en nombre de lignes | nombre entier | uniquement pris en compte pour les widgets QTextEdit |
| `'input mask'` | masque de saisie | chaîne de caractères |  |
| `'label'` | libellé de la catégorie de métadonnée | chaîne de caractères |  |
| `'help text'` | explications sur la métadonnée | chaîne de caractères |  |
| `'placeholder text'` | faux texte à afficher dans la zone de saisie | chaîne de caractères | uniquement pour les widgets QTextEdit et QLineEdit |
| `'is mandatory'` | est-il obligatoire de saisir une valeur ? | booléen | `False` par défaut |
| `'multiple values'` | la catégorie admet-elle plusieurs valeurs ? | booléen | ignoré pour les catégories de métadonnées communes, `False` par défaut pour les catégories locales |
| `'default value'` | valeur par défaut | chaîne de caractères |  |
| `'data type'` | type de valeur | `'string'`, `'integer'`, `'decimal'`, `'float'`, `'double'`, `'boolean'`, `'date'`, `'time'`, `'dateTime'`, `'duration'` | ignoré pour les catégories de métadonnées communes |

### La compilation d'ontologies

### Les paramètres utilisateur

### Autres arguments

## Configurer les widgets à partir du dictionnaire





