# Paramètres utilisateurs

Le tableau ci-après liste les paramètres utilisateurs définis dans les fichiers de configuration, hors paramètres d'apparence de l'interface.

| Nom du paramètre[^1] | Type | Valeur par défaut[^2] | Définition | Références |
| --- | --- | --- | --- | --- |
| `editHideUnlisted` | bool | | si `True` les catégories non référencées sont masquées en mode édition | [Génération du dictionnaire des widgets](./generation_dictionnaire_widgets.md#edithideunlisted) |
| `editOnlyCurrentLanguage` | bool | | si `True` seules les valeurs dans la langue principale sont affichées en mode édition | [Génération du dictionnaire des widgets](./generation_dictionnaire_widgets.md#editonlycurrentlanguage) |
| `enforcePreferedTemplate` | bool | | si `True`, le modèle `preferedTemplate` est appliqué à l'ouverture de toutes les fiches | [Modèles de formulaire](./modeles_de_formulaire.md#sélection-automatique-du-modèle) |
| `labelLengthLimit` | int | | nombre de caractères au-delà duquel les étiquettes des catégories sont affichées au-dessus du widget de saisie et non à côté | [Génération du dictionnaire des widgets](./generation_dictionnaire_widgets.md#labellengthlimit) |
| `language` | str | `'fr'` | langue principale de rédaction des métadonnées | [Génération du dictionnaire des widgets](./generation_dictionnaire_widgets.md#language) et [Actions générales](./actions_generales.md#langue-principale-des-métadonnées) |
| `langList` | list | `['fr', 'en']` | langues autorisées pour les traductions | [Génération du dictionnaire des widgets](./generation_dictionnaire_widgets.md#langlist) |
| `preferedTemplate` | str | | nom du modèle à utiliser à l'ouverture des fiches de métadonnées, soit toujours si `enforcePreferedTemplate` vaut `True`, soit si les conditions d'applications automatiques ne sont remplies pour aucun modèle | [Modèles de formulaire](./modeles_de_formulaire.md#sélection-automatique-du-modèle) |
| `readHideBlank` | bool | | si `True` les champs vides sont masqués en mode lecture | [Génération du dictionnaire des widgets](./generation_dictionnaire_widgets.md#reahideblank) |
| `readHideUnlisted` | bool | | si `True` les catégories non référencées sont masquées en mode lecture | [Génération du dictionnaire des widgets](./generation_dictionnaire_widgets.md#readhideunlisted) |
| `readOnlyCurrentLanguage` | bool | | si `True` seules les valeurs dans la langue principale sont affichées en mode lecture | [Génération du dictionnaire des widgets](./generation_dictionnaire_widgets.md#readonlycurrentlanguage) |
| `textEditRowSpan` | int | | nombre de lignes occupées par les widgets QTextEdit si non spécifié par ailleurs | [Génération du dictionnaire des widgets](./generation_dictionnaire_widgets.md#texteditrowspan) |
| `translation` | bool | `False` | `True` si le mode traduction est activé | [Génération du dictionnaire des widgets](./generation_dictionnaire_widgets.md#translation) et [Actions générales](./actions_generales.md#activation-du-mode-traduction) |
| `urlCsw` | list | `['http://ogc.geo-ide.developpement-durable.gouv.fr/csw/dataset-harvestable']`[^3] | Liste des URL de base de services CSW mémorisées. | [Actions générales](./actions_generales.md#import-de-métadonnées-depuis-un-service-csw) |
| `valueLengthLimit` | int | | nombre de caractères au-delà duquel les valeurs des QLineEdit sont affichées à la place dans des QTextEdit | [Génération du dictionnaire des widgets](./generation_dictionnaire_widgets.md#valuelengthlimit) |


[^1]: Il s'agit du nom donné au paramètre dans la présente documentation et les noms de variables des fonctions, pas nécessairement celui qui doit être utilisé dans les fichiers INI (même si ça simplifierait les choses).

[^2]: Valeur par défaut à renseigner dans le fichier de configuration, s'il y a lieu (à distinguer des valeurs par défaut que certaines fonctions donneront ensuite à ces paramètres). Si cette colonne ne contient aucune valeur, alors le paramètre ne doit **pas** être automatiquement ajouté au fichier de configuration `QGIS3.ini` lorsqu'il  n'est pas explicitement défini par l'utilisateur. Quand un tel paramètre n'existe pas, on considère qu'il vaut `None`. Si une valeur par défaut est fournie, le paramètre doit être automatiquement enregristré dans `QGIS3.ini` avec la valeur en question quand il n'était présent ni dans `QGIS3.ini` ni dans `global_settings.ini`.

[^3]: URL de base du service CSW de GéoIDE pour les jeux de données.
