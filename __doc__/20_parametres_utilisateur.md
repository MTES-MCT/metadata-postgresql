# Paramètres utilisateurs

| Nom du paramètre[^1] | Type | Définition | Références |
| --- | --- | --- | --- |
| `preferedTemplate` | str | nom du modèle à utiliser à l'ouverture des fiches de métadonnées, soit toujours si `enforcePreferedTemplate` vaut `True`, soit si les conditions d'applications automatiques ne sont remplies pour aucun modèle | [1](/__doc__/08_modeles_de_formulaire.md#sélection-automatique-du-modèle) |
| `enforcePreferedTemplate` | bool | si `True`, le modèle `preferedTemplate` est appliqué à l'ouverture de toutes les fiches | [1](/__doc__/08_modeles_de_formulaire.md#sélection-automatique-du-modèle) |


[^1]: Il s'agit du nom donné au paramètre dans la présente documentation et les noms de variables des fonctions, pas nécessairement celui qui doit être utilisé dans les fichiers INI.

