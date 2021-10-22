# Paramètres utilisateurs

Le tableau ci-après liste les paramètres utilisateurs définis dans les fichiers de configuration et renvoie vers les passages de la documentation qui les évoquent plus en détail.

| Nom du paramètre[^1] | Type | Valeur par défaut[^2] | Définition | Références |
| --- | --- | --- | --- | --- |
| `editHideUnlisted` | bool | | si `True` les catégories non référencées sont masquées en mode édition | [Génération du dictionnaire des widgets](/__doc__/05_generation_dictionnaire_widgets.md#edithideunlisted) |
| `editOnlyCurrentLanguage` | bool | | si `True` seules les valeurs dans la langue principale sont affichées en mode édition | [Génération du dictionnaire des widgets](/__doc__/05_generation_dictionnaire_widgets.md#editonlycurrentlanguage) |
| `enforcePreferedTemplate` | bool | | si `True`, le modèle `preferedTemplate` est appliqué à l'ouverture de toutes les fiches | [Modèles de formulaire](/__doc__/08_modeles_de_formulaire.md#sélection-automatique-du-modèle) |
| `geoideJSON` | bool | `True` | si `True`, les petits JSON contenant les métadonnées destinées à GéoIDE sont créés lors de la sauvegarde | [Actions générales](/__doc__/16_actions_generales.md#sauvegarde) |
| `labelLengthLimit` | int | | nombre de caractères au-delà duquel les étiquettes des catégories sont affichées au-dessus du widget de saisie et non à côté | [Génération du dictionnaire des widgets](/__doc__/05_generation_dictionnaire_widgets.md#labellengthlimit) |
| `language` | str | `'fr'` | langue principale de rédaction des métadonnées | [Génération du dictionnaire des widgets](/__doc__/05_generation_dictionnaire_widgets.md#language) et [Actions générales](/__doc__/16_actions_generales.md#langue-principale-des-métadonnées) |
| `langList` | list | `['fr', 'en']` | langues autorisées pour les traductions | [Génération du dictionnaire des widgets](/__doc__/05_generation_dictionnaire_widgets.md#langlist) |
| `preferedTemplate` | str | | nom du modèle à utiliser à l'ouverture des fiches de métadonnées, soit toujours si `enforcePreferedTemplate` vaut `True`, soit si les conditions d'applications automatiques ne sont remplies pour aucun modèle | [Modèles de formulaire](/__doc__/08_modeles_de_formulaire.md#sélection-automatique-du-modèle) |
| `readHideBlank` | bool | | si `True` les champs vides sont masqués en mode lecture | [Génération du dictionnaire des widgets](/__doc__/05_generation_dictionnaire_widgets.md#reahideblank) |
| `readHideUnlisted` | bool | | si `True` les catégories non référencées sont masquées en mode lecture | [Génération du dictionnaire des widgets](/__doc__/05_generation_dictionnaire_widgets.md#readhideunlisted) |
| `readOnlyCurrentLanguage` | bool | | si `True` seules les valeurs dans la langue principale sont affichées en mode lecture | [Génération du dictionnaire des widgets](/__doc__/05_generation_dictionnaire_widgets.md#readonlycurrentlanguage) |
| `textEditRowSpan` | int | | nombre de lignes occupées par les widgets QTextEdit si non spécifié par ailleurs | [Génération du dictionnaire des widgets](/__doc__/05_generation_dictionnaire_widgets.md#texteditrowspan) |
| `translation` | bool | `False` | `True` si le mode traduction est activé | [Génération du dictionnaire des widgets](/__doc__/05_generation_dictionnaire_widgets.md#translation) et [Actions générales](/__doc__/16_actions_generales.md#activation-du-mode-traduction) |
| `valueLengthLimit` | int | | nombre de caractères au-delà duquel les valeurs des QLineEdit sont affichées à la place dans des QTextEdit | [Génération du dictionnaire des widgets](/__doc__/05_generation_dictionnaire_widgets.md#valuelengthlimit) |


[^1]: Il s'agit du nom donné au paramètre dans la présente documentation et les noms de variables des fonctions, pas nécessairement celui qui doit être utilisé dans les fichiers INI (même si ça simplifierait les choses).

[^2]: Si cette colonne ne contient aucune valeur, alors le paramètre ne doit **pas** être automatiquement ajouté au fichier de configuration `QGIS3.ini` lorsqu'il  n'est pas défini. Quand un tel paramètre n'existe pas, on considère qu'il vaut `None`. Si une valeur par défaut est fournie, le paramètre doit être automatiquement enregristré dans `QGIS3.ini`, avec la valeur en question, quand il n'est présent ni `QGIS3.ini` ni dans `global_settings.ini`.
