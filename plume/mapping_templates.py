"""Configuration.
Fichier de mapping nécessaire pour la gestion des modèles, catégories, onglets et modèles/Catégories
Permet en fonction du nom de la table et du nom de l'attribut, d'obtenir le libellé, l'infobulle, le type pour l'interface  
"""

"""
enum pour spécial, datatype, geo_tools, compute et plus si affinités
"""
dicEnum = \
      {
       "special"   : { 
                       "email" : {"enum_label" : "Courriel",  "enum_help" : "saisie d'une adresse electronique"},
                       "phone" : {"enum_label" : "Téléphone", "enum_help" : "saisie d'un numéro de téléphone"},
                       "url"   : {"enum_label" : "Url",       "enum_help" : "saisie d'une url"}
                     },
       "datatype"   : { 
                       "gsp:wktLiteral" : {"enum_label" : "Géométrie",             "enum_help" : ""},
                       "rdf:langString" : {"enum_label" : "Texte traduisible",     "enum_help" : ""},
                       "xsd:boolean"    : {"enum_label" : "Booléen",               "enum_help" : ""},            
                       "xsd:date"       : {"enum_label" : "Date",                  "enum_help" : ""},
                       "xsd:dateTime"   : {"enum_label" : "Date / Heure",          "enum_help" : ""},
                       "xsd:decimal"    : {"enum_label" : "Décimal",               "enum_help" : ""},
                       "xsd:duration"   : {"enum_label" : "Durée",                 "enum_help" : ""},
                       "xsd:integer"    : {"enum_label" : "Entier",                "enum_help" : ""},
                       "xsd:string"     : {"enum_label" : "Texte non traduisible", "enum_help" : ""},
                       "xsd:time"       : {"enum_label" : "Heure",                 "enum_help" : ""}
                     },
       "geo_tools"   : { 
                       "bbox"       : {"enum_label" : "Calcul du rectangle d'emprise",        "enum_help" : "Calcule le rectangle d’emprise à partir des données. Le calcul est réalisé côté serveur, via les fonctionnalités de PostGIS."},
                       "centroid"   : {"enum_label" : "Calcul d'un centroide",                "enum_help" : "Calcule le centre du rectangle d’emprise à partir des données. Le calcul est réalisé côté serveur, via les fonctionnalités de PostGIS."},
                       "circle"     : {"enum_label" : "Tracé manuel d'un cercle",             "enum_help" : "Permet à l’utilisateur de tracer un cercle dans le canevas et mémorise la géométrie dans les métadonnées."},
                       "linestring" : {"enum_label" : "Tracé manuel d'une ligne",             "enum_help" : "Permet à l’utilisateur de tracer une ligne dans le canevas et mémorise la géométrie dans les métadonnées."},
                       "point"      : {"enum_label" : "Tracé manuel d'un point",              "enum_help" : "Permet à l’utilisateur de cliquer sur un point dans le canevas et mémorise la géométrie dans les métadonnées."},
                       "polygon"    : {"enum_label" : "Tracé manuel d'un polygone",           "enum_help" : "Permet à l’utilisateur de tracer un polygone dans le canevas et mémorise la géométrie dans les métadonnées."},
                       "rectangle"  : {"enum_label" : "Tracé manuel d'un rectangle",          "enum_help" : "Permet à l’utilisateur de tracer un rectangle dans le canevas et mémorise la géométrie dans les métadonnées."},
                       "show"       : {"enum_label" : "Visualisation de la géométrie saisie", "enum_help" : "Visualisation dans le canevas de la géométrie renseignée dans les métadonnées."}
                     },
       "compute"   : { 
                       "auto"       : {"enum_label" : "Automatique",  "enum_help" : "Le calcul est effectué systématiquement à l’ouverture de la fiche de métadonnées ou lorsqu’elle est re-générée par une réinitialisation, un import, une copie… \nIl n’est pas exécuté lorsque le formulaire est reconstruit après une sauvegarde."},
                       "empty"      : {"enum_label" : "Vide",         "enum_help" : "Le calcul est effectué dans les mêmes conditions que pour 'auto', avec une condition supplémentaire : \nle widget ou le groupe de widgets ne doit contenir aucune valeur."},
                       "manual"     : {"enum_label" : "Manuel",       "enum_help" : "Un bouton de calcul <img width='20' src='plume/icons/buttons/compute_button.svg' /> apparaîtra à droite du champ de saisie de la métadonnées dans le formulaire. \nCliquer sur ce bouton importe les informations désirées du serveur. Pour les catégories admettant plusieurs valeurs, le bouton porte sur l’ensemble du groupe."},
                       "new"        : {"enum_label" : "Nouvelle",     "enum_help" : "Le calcul n’est effectué que si la fiche de métadonnées est entièrement vide, soit dans le cas d’une table dont le descriptif ne contenait par encore de métadonnées, \ndans le cas d’une réinitialisation ou encore dans le cas de l’import d’une fiche vide."}
                     }
      }

load_mapping_read_meta_template_categories  =  \
      {"tpl_id"         : {"label" : "Identifiant",                       "enum" : "",                   "tooltip" : "", "property" : [ "visible", "disabled"],  "type" : "QLineEdit", "dicListItems" : "",                  "id" : "", "format" : "integer",         "assistantTranslate" : ["false", ""],     "help" : ""},
       "tplcat_id"      : {"label" : "Identifiant de la catégorie",       "enum" : "",                   "tooltip" : "", "property" : [ "visible", "disabled"],  "type" : "QLineEdit", "dicListItems" : "",                  "id" : "", "format" : "text",            "assistantTranslate" : ["false", ""],     "help" : ""},
       "shrcat_path"    : {"label" : "Nom de la catégorie commune",       "enum" : "",                   "tooltip" : "", "property" : [ "visible", "disabled"],  "type" : "QLineEdit", "dicListItems" : "",                  "id" : "", "format" : "text",            "assistantTranslate" : ["false", ""],     "help" : ""},
       "loccat_path"    : {"label" : "Nom de la catégorie locale",        "enum" : "",                   "tooltip" : "", "property" : [ "visible", "disabled"],  "type" : "QLineEdit", "dicListItems" : "",                  "id" : "", "format" : "text",            "assistantTranslate" : ["false", ""],     "help" : ""},         
       "label"          : {"label" : "libellé de la catégorie",           "enum" : "",                   "tooltip" : "", "property" : [ "visible", "enabled" ],  "type" : "QLineEdit", "dicListItems" : "",                  "id" : "", "format" : "text",            "assistantTranslate" : ["false", ""],     "help" : "Libellé de la catégorie."},              
       "description"    : {"label" : "Description",                       "enum" : "",                   "tooltip" : "", "property" : [ "visible", "enabled" ],  "type" : "QLineEdit", "dicListItems" : "",                  "id" : "", "format" : "text",            "assistantTranslate" : ["false", ""],     "help" : "Description de la catégorie. Elle sera affichée sous la forme d’un texte d’aide dans le formulaire."},         
       "special"       :  {"label" : "Mise en forme",                     "enum" : "",                   "tooltip" : "", "property" : [ "visible", "enabled" ],  "type" : "QComboBox", "dicListItems" : dicEnum["special"],  "id" : "", "format" : "text",            "assistantTranslate" : ["false", ""],     "help" : "Le cas échéant, mise en forme spécifique à appliquer au champ. Valeurs autorisées (type énuméré `z_plume.meta_datatype`) : `'url'`, `'email'`, et `'phone'`.\n\nPour les catégories communes, les modifications apportées à ce champ ne seront pas prises en compte."},          
       "datatype"       : {"label" : "Type de valeur",                    "enum" : "",                   "tooltip" : "", "property" : [ "visible", "enabled" ],  "type" : "QComboBox", "dicListItems" : dicEnum["datatype"], "id" : "", "format" : "text",            "assistantTranslate" : ["false", ""],     "help" : "Type de valeur attendu pour la catégorie, parmi (type énuméré `z_plume.meta_data_type`) : `'xsd:string'`, `'xsd:integer'`, `'xsd:decimal'`, `'xsd:boolean'`, `'xsd:date'`, `'xsd:time'`, `'xsd:dateTime'`, `'xsd:duration'`, `'rdf:langString'` (chaîne de caractères avec une langue associée) et `'gsp:wktLiteral'` (géométrie au format textuel WKT). Cette information détermine notamment la nature des widgets utilisés par Plume pour afficher et éditer les valeurs, ainsi que les validateurs appliqués. \n\nPour les catégories communes, les modifications apportées sur ce champ ne seront pas prises en compte sauf s'il s'agit d'utiliser des dates avec heures (`'xsd:dateTime'`) à la place des dates simples (`'xsd:date'`) ou réciproquement. Si, pour une catégorie locale, aucune valeur n'est renseignée pour ce champ (ni dans `meta_categorie` ni dans `meta_template_categories`), le plugin considérera que la catégorie prend des valeurs de type `'xsd:string'`."},         
       "is_long_text"   : {"label" : "Texte sur plusieurs lignes",        "enum" : "",                   "tooltip" : "", "property" : [ "visible", "enabled" ],  "type" : "QCheckBox", "dicListItems" : "",                  "id" : "", "format" : "Tristate(True)",  "assistantTranslate" : ["false", ""],     "help" : "True pour une catégorie appelant un texte de plusieurs lignes.\n\nCette information ne sera prise en compte que si le type de valeur (datatype) est 'xsd:string' ou 'rdf:langString'. Pour le type 'gsp:wktLiteral', elle vaut implicitement toujours True. Pour les autres types, notamment 'xsd:string' et 'rdf:langString', elle vaut implicitement toujours False (si tant est qu’elle ait encore un objet)."},         
       "rowspan"        : {"label" : "Nombre de lignes",                  "enum" : "",                   "tooltip" : "", "property" : [ "visible", "enabled" ],  "type" : "QLineEdit", "dicListItems" : "",                  "id" : "", "format" : "integer",         "assistantTranslate" : ["false", ""],     "help" : "Nombre de lignes occupées par le widget de saisie, s'il y a lieu de modifier le comportement par défaut de Plume.\n\nLa valeur ne sera considérée que si `is_long_text` vaut `True`."},          
       "placeholder"    : {"label" : "Valeur fictive pré-affichée",       "enum" : "",                   "tooltip" : "", "property" : [ "visible", "enabled" ],  "type" : "QLineEdit", "dicListItems" : "",                  "id" : "", "format" : "text",            "assistantTranslate" : ["false", ""],     "help" : "Valeur fictive pré-affichée en tant qu’exemple dans le widget de saisie, s’il y a lieu."},         
       "input_mask"     : {"label" : "Masque de saisie",                  "enum" : "",                   "tooltip" : "", "property" : [ "visible", "enabled" ],  "type" : "QLineEdit", "dicListItems" : "",                  "id" : "", "format" : "text",            "assistantTranslate" : ["false", ""],     "help" : "Masque de saisie, s’il y a lieu. La syntaxe est décrite dans la documentation de l’API Qt for python.\n\nLa valeur sera ignorée si le widget utilisé pour la catégorie ne prend pas en charge ce mécanisme."},         
       "is_multiple"    : {"label" : "Plusieurs valeurs",                 "enum" : "",                   "tooltip" : "", "property" : [ "visible", "enabled" ],  "type" : "QCheckBox", "dicListItems" : "",                  "id" : "", "format" : "Tristate(True)",  "assistantTranslate" : ["false", ""],     "help" : "True si la catégorie admet plusieurs valeurs.\n\nPour les catégories communes, les modifications apportées sur ce champ ne seront pas prises en compte."},         
       "unilang"        : {"label" : "Plusieurs langues",                 "enum" : "",                   "tooltip" : "", "property" : [ "visible", "enabled" ],  "type" : "QCheckBox", "dicListItems" : "",                  "id" : "", "format" : "Tristate(True)",  "assistantTranslate" : ["false", ""],     "help" : "`True` si la catégorie n'admet plusieurs valeurs que si elles sont dans des langues différentes (par exemple un jeu de données n'a en principe qu'un seul titre, mais il peut être traduit).\n\nPour les catégories communes, les modifications apportées sur ce champ ne seront pas prises en compte. `is_multiple` est ignoré quand `unilang` vaut `True`. Cette information n'est considérée que si `datatype` vaut `'rdf:langString'`."},          
       "is_mandatory"   : {"label" : "Obligatoire",                       "enum" : "",                   "tooltip" : "", "property" : [ "visible", "enabled" ],  "type" : "QCheckBox", "dicListItems" : "",                  "id" : "", "format" : "Tristate(True)",  "assistantTranslate" : ["false", ""],     "help" : "`True` si une valeur doit obligatoirement être saisie pour cette catégorie. \n\n Modifier cette valeur permet de rendre obligatoire une catégorie commune optionnelle, mais pas l''inverse."},         
       "sources"        : {"label" : "Liste des sources",                 "enum" : "sources",            "tooltip" : "", "property" : [ "visible", "enabled" ],  "type" : "QLineEdit", "dicListItems" : "",                  "id" : "", "format" : "list",            "assistantTranslate" : ["true", "list"],  "help" : "Pour une catégorie prenant ses valeurs dans un ou plusieurs thésaurus, liste des sources admises. \n\n Cette information n'est considérée que pour les catégories communes. Il n'est pas possible d'ajouter des sources ni de les retirer toutes - Plume reviendrait alors à la liste initiale -, mais ce champ permet de restreindre la liste à un ou plusieurs thésaurus jugés les mieux adaptés."},          
       "geo_tools"      : {"label" : "Géométrie : Liste des aides à la saisie",       
                                                                          "enum" : dicEnum["geo_tools"], "tooltip" : "", "property" : [ "visible", "enabled" ],  "type" : "QLineEdit", "dicListItems" : "",                  "id" : "", "format" : "list",            "assistantTranslate" : ["true", "list"],  "help" : "Pour une catégorie prenant pour valeurs des géométries, liste des fonctionnalités d'aide à la saisie à proposer, parmi `'show'` (visualisation de la géométrie saisie), `'point'` (tracé manuel d'une géométrie ponctuelle), `'linestring'` (tracé manuel d'une géométrie linéaire), `'rectangle'`  (tracé manuel d'un rectangle), `'polygon'` (tracé manuel d'un polygone), `'circle'` (tracé manuel d'un cercle), `'bbox'` (calcul du rectangle d'emprise de la couche courante), `'centroid'` (calcul du centre du rectangle d'emprise de la couche courante). \n\n Cette information ne sera considérée que si le type (`datatype`) est `'gsp:wktLiteral'`. Pour retirer toutes les fonctionnalités proposées par défaut pour une catégorie commune, on saisira une liste vide, soit `ARRAY[]::z_plume.meta_geo_tool[]`."},         
       "compute"        : {"label" : "Liste des modes de calcul",         "enum" : dicEnum["compute"],   "tooltip" : "", "property" : [ "visible", "enabled" ],  "type" : "QLineEdit", "dicListItems" : "",                  "id" : "", "format" : "list",            "assistantTranslate" : ["true", "list"],  "help" : "Liste des fonctionnalités de calcul à proposer, parmis, `'auto'` (déclenchement automatique lorsque la fiche de métadonnées est générée), `'manuel'` (déclenchement à la demande, lorsque l'utilisateur clique sur le bouton qui apparaîtra alors à côté du champ de saisie dans le formulaire). \n\n Cette information ne sera considérée que si une méthode de calcul est effectivement disponible pour la catégorie. Pour retirer toutes les fonctionnalités proposées par défaut pour une catégorie commune, on saisira une liste vide, soit `ARRAY[]::z_plume.meta_compute[]`."},              
       "template_order" : {"label" : "Ordre d'apparence",                 "enum" : "",                   "tooltip" : "", "property" : [ "visible", "enabled" ],  "type" : "QLineEdit", "dicListItems" : "",                  "id" : "", "format" : "integer",         "assistantTranslate" : ["false", ""],     "help" : "Ordre d'apparence de la catégorie dans le formulaire. Les plus petits numéros sont affichés en premier, il n'est pas nécessaire que les numéros se suivent. Dans le cas des catégories communes, qui ont une structure arborescente, il s'agit de l'ordre parmi les catégories de même niveau dans la branche."},         
       "is_read_only"   : {"label" : "Lecture seule",                     "enum" : "",                   "tooltip" : "", "property" : [ "visible", "enabled" ],  "type" : "QCheckBox", "dicListItems" : "",                  "id" : "", "format" : "Tristate(True)",  "assistantTranslate" : ["false", ""],     "help" : "True si la catégorie est en lecture seule."},         
       "tab_id"         : {"label" : "Identifiant de l'onglet",           "enum" : "",                   "tooltip" : "", "property" : [ "visible", "enabled" ],  "type" : "QComboBox", "dicListItems" : "tabs",              "id" : "", "format" : "text",            "assistantTranslate" : ["false", ""],     "help" : "Nom de l'onglet."},                                  
       "compute_params" : {"label" : "Paramètres des méthodes de calcul", "enum" : "compute_params",     "tooltip" : "", "property" : [ "visible", "enabled" ],  "type" : "QLineEdit", "dicListItems" : "",                  "id" : "", "format" : "jsonb",           "assistantTranslate" : ["true", "list"],  "help" : "Paramètres optionnels attendus par la méthode de calcul, si opportun. À spécifier sous la forme d'un dictionnaire JSON dont les clés correspondent aux noms des paramètres et les valeurs sont les valeurs des paramètres. Cf. [Métadonnées calculées](./metadonnees_calculees.md) pour plus de détails. \n\n Cette information ne sera considérée que si une méthode de calcul est effectivement disponible pour la catégorie et qu''elle admet un ou plusieurs paramètres."}       
      } 

load_mapping_read_meta_templates  =  \
      {"tpl_id"         : {"label" : "Identifiant",                 "enum" : "", "tooltip" : "", "property" : [ "visible", "disabled" ],  "type" : "QLineEdit", "dicListItems" : "",  "id" : "",   "format" : "integer",        "assistantTranslate" : ["false", ""], "help" : ""},
       "tpl_label"      : {"label" : "Libellé",                     "enum" : "", "tooltip" : "", "property" : [ "visible", "enabled" ],   "type" : "QLineEdit", "dicListItems" : "",  "id" : "OK", "format" : "text",           "assistantTranslate" : ["false", ""], "help" : "Libellé du modèle."},
       "sql_filter"     : {"label" : "Filtre SQL",                  "enum" : "", "tooltip" : "", "property" : [ "visible", "enabled" ],   "type" : "QLineEdit", "dicListItems" : "",  "id" : "",   "format" : "text",           "assistantTranslate" : ["false", ""], "help" : "Les champs `sql_filter` et `md_conditions` servent à définir des conditions selon lesquelles le modèle sera appliqué automatiquement à la fiche de métadonnées considérée. Les remplir est bien évidemment optionnel.\n\n \
                                                                                                                                                                                                                                     - `sql_filter` est un filtre SQL, qui peut se référer au nom du schéma avec `$1` et/ou de la table / vue avec `$2`. Il est évalué côté serveur au moment de l'import des modèles par le plugin, par la fonction `z_plume.meta_execute_sql_filter(text, text, text)`.\n\n \
                                                                                                                                                                                                                                     Par exemple, le filtre suivant appliquera le modèle aux tables des schémas des blocs 'données référentielles' (préfixe `'r_'`) et 'données externes' (préfixe `'e_'`) de la nomenclature nationale :\n\n \
                                                                                                                                                                                                                                     '$1 ~ ANY(ARRAY[''^r_'', ''^e_'']'"},
       "md_conditions"  : {"label" : "Conditions au format JSON",   "enum" : "md_conditions",
                                                                                 "tooltip" : "", "property" : [ "visible", "enabled" ],   "type" : "QLineEdit", "dicListItems" : "",   "id" : "",   "format" : "jsonb",         "assistantTranslate" : ["true", "list"], "help" : "Condition à remplir pour que ce modèle soit appliqué par défaut à une fiche de métadonnées, sous la forme d''un filtre SQL.\n\nOn pourra utiliser $1 pour représenter le nom du schéma et $2 le nom de la table.\n\n\
                                                                                                                                                                                                                                     Par exemple :\n\n\
                                                                                                                                                                                                                                     - ''$1 ~ ANY(ARRAY[''''^r_'''', ''''^e_'''']'' appliquera le modèle aux tables des schémas des blocs 'données référentielles' (préfixe ''r_'') et 'données externes' (préfixe ''e_'') de la nomenclature nationale ;\n\n\
                                                                                                                                                                                                                                     - ''pg_has_role(''''g_admin'''', ''''USAGE'''')'' appliquera le modèle pour toutes les fiches de métadonnées dès lors que l''utilisateur est membre du rôle g_admin."},              
       "priority"       : {"label" : "Priorité",                    "enum" : "", "tooltip" : "", "property" : [ "visible", "enabled" ],   "type" : "QLineEdit", "dicListItems" : "", "id" : "",   "format" : "integer",         "assistantTranslate" : ["false", ""], "help" : "Niveau de priorité du modèle. Si un jeu de données remplit les conditions de plusieurs modèles, celui dont la priorité est la plus élevée sera retenu comme modèle par défaut."},         
       "comment"        : {"label" : "Commentaire",                 "enum" : "", "tooltip" : "", "property" : [ "visible", "enabled" ],   "type" : "QLineEdit", "dicListItems" : "", "id" : "",   "format" : "text",            "assistantTranslate" : ["false", ""], "help" : "Commentaire libre."},          
       "enabled"        : {"label" : "Actif",                       "enum" : "", "tooltip" : "", "property" : [ "visible", "enabled" ],   "type" : "QCheckBox", "dicListItems" : "", "id" : "",   "format" : "Tristate(False)", "assistantTranslate" : ["false", ""], "help" : "Booléen indiquant si le modèle est actif. Les modèles désactivés n''apparaîtront pas dans la liste de modèles du plugin QGIS, même si leurs conditions d''application automatique sont remplies."}         
      }
       
load_mapping_read_meta_categories  =  \
      {"path"           : {"label" : "identifiant",                 "enum" : "",                   "tooltip" : "", "property" : [ "visible", "disabled" ], "type" : "QLineEdit", "dicListItems" : "",                  "id" : "",   "format" : "text",            "assistantTranslate" : ["false", ""],    "help" : ""},
       "origin"         : {"label" : "Commune / Locale",            "enum" : "",                   "tooltip" : "", "property" : [ "visible", "disabled" ], "type" : "QLineEdit", "dicListItems" : "",                  "id" : "",   "format" : "text",            "assistantTranslate" : ["false", ""],    "help" : ""},
       "label"          : {"label" : "libellé",                     "enum" : "",                   "tooltip" : "", "property" : [ "visible", "enabled" ],  "type" : "QLineEdit", "dicListItems" : "",                  "id" : "OK", "format" : "text",            "assistantTranslate" : ["false", ""],    "help" : "Libellé de la catégorie."},              
       "description"    : {"label" : "Description",                 "enum" : "",                   "tooltip" : "", "property" : [ "visible", "enabled" ],  "type" : "QLineEdit", "dicListItems" : "",                  "id" : "",   "format" : "text",            "assistantTranslate" : ["false", ""],    "help" : "Description de la catégorie. Elle sera affichée sous la forme d’un texte d’aide dans le formulaire."},         
       "special"       :  {"label" : "Mise en forme",               "enum" : "",                   "tooltip" : "", "property" : [ "visible", "enabled" ],  "type" : "QComboBox", "dicListItems" : dicEnum["special"],  "id" : "",   "format" : "text",            "assistantTranslate" : ["false", ""],    "help" : "Le cas échéant, mise en forme spécifique à appliquer au champ. Valeurs autorisées (type énuméré `z_plume.meta_datatype`) : `'url'`, `'email'`, et `'phone'`.\n\nPour les catégories communes, les modifications apportées à ce champ ne seront pas prises en compte."},          
       "datatype"       : {"label" : "Type de valeur",              "enum" : "",                   "tooltip" : "", "property" : [ "visible", "enabled" ],  "type" : "QComboBox", "dicListItems" : dicEnum["datatype"], "id" : "",   "format" : "text",            "assistantTranslate" : ["false", ""],    "help" : "Type de valeur attendu pour la catégorie, parmi (type énuméré `z_plume.meta_data_type`) : `'xsd:string'`, `'xsd:integer'`, `'xsd:decimal'`, `'xsd:boolean'`, `'xsd:date'`, `'xsd:time'`, `'xsd:dateTime'`, `'xsd:duration'`, `'rdf:langString'` (chaîne de caractères avec une langue associée) et `'gsp:wktLiteral'` (géométrie au format textuel WKT). Cette information détermine notamment la nature des widgets utilisés par Plume pour afficher et éditer les valeurs, ainsi que les validateurs appliqués. \n\nPour les catégories communes, les modifications apportées sur ce champ ne seront pas prises en compte sauf s'il s'agit d'utiliser des dates avec heures (`'xsd:dateTime'`) à la place des dates simples (`'xsd:date'`) ou réciproquement. Si, pour une catégorie locale, aucune valeur n'est renseignée pour ce champ (ni dans `meta_categorie` ni dans `meta_template_categories`), le plugin considérera que la catégorie prend des valeurs de type `'xsd:string'`."},         
       "is_node"        : {"label" : "Noeud",                       "enum" : "",                   "tooltip" : "", "property" : [ "visible", "disabled" ], "type" : "QCheckBox", "dicListItems" : "",                  "id" : "",   "format" : "Tristate(False)", "assistantTranslate" : ["false", ""],    "help" : "True si la catégorie est le nom d''un groupe qui contiendra lui-même d''autres catégories et non une catégorie à laquelle sera directement associée une valeur. Par exemple, is_node vaut True pour la catégorie correspondant au point de contact (dcat:contactPoint) et False pour le nom du point de contact (dcat:contactPoint / vcard:fn). CE CHAMP EST GENERE AUTOMATIQUEMENT, NE PAS MODIFIER MANUELLEMENT."},              
       "is_long_text"   : {"label" : "Texte sur plusieurs lignes",  "enum" : "",                   "tooltip" : "", "property" : [ "visible", "enabled" ],  "type" : "QCheckBox", "dicListItems" : "",                  "id" : "",   "format" : "Tristate(False)", "assistantTranslate" : ["false", ""],    "help" : "True pour une catégorie appelant un texte de plusieurs lignes.\n\nCette information ne sera prise en compte que si le type de valeur (datatype) est 'xsd:string' ou 'rdf:langString'. Pour le type 'gsp:wktLiteral', elle vaut implicitement toujours True. Pour les autres types, notamment 'xsd:string' et 'rdf:langString', elle vaut implicitement toujours False (si tant est qu’elle ait encore un objet)."},         
       "rowspan"        : {"label" : "Nombre de lignes",            "enum" : "",                   "tooltip" : "", "property" : [ "visible", "enabled" ],  "type" : "QLineEdit", "dicListItems" : "",                  "id" : "",   "format" : "integer",         "assistantTranslate" : ["false", ""],    "help" : "Nombre de lignes occupées par le widget de saisie, s'il y a lieu de modifier le comportement par défaut de Plume.\n\nLa valeur ne sera considérée que si `is_long_text` vaut `True`."},          
       "placeholder"    : {"label" : "Valeur fictive pré-affichée", "enum" : "",                   "tooltip" : "", "property" : [ "visible", "enabled" ],  "type" : "QLineEdit", "dicListItems" : "",                  "id" : "",   "format" : "text",            "assistantTranslate" : ["false", ""],    "help" : "Valeur fictive pré-affichée en tant qu’exemple dans le widget de saisie, s’il y a lieu."},         
       "input_mask"     : {"label" : "Masque de saisie",            "enum" : "",                   "tooltip" : "", "property" : [ "visible", "enabled" ],  "type" : "QLineEdit", "dicListItems" : "",                  "id" : "",   "format" : "text",            "assistantTranslate" : ["false", ""],    "help" : "Masque de saisie, s’il y a lieu. La syntaxe est décrite dans la documentation de l’API Qt for python.\n\nLa valeur sera ignorée si le widget utilisé pour la catégorie ne prend pas en charge ce mécanisme."},         
       "is_multiple"    : {"label" : "Plusieurs valeurs",           "enum" : "",                   "tooltip" : "", "property" : [ "visible", "enabled" ],  "type" : "QCheckBox", "dicListItems" : "",                  "id" : "",   "format" : "Tristate(False)", "assistantTranslate" : ["false", ""],    "help" : "True si la catégorie admet plusieurs valeurs.\n\nPour les catégories communes, les modifications apportées sur ce champ ne seront pas prises en compte."},         
       "unilang"        : {"label" : "Plusieurs langues",           "enum" : "",                   "tooltip" : "", "property" : [ "visible", "enabled" ],  "type" : "QCheckBox", "dicListItems" : "",                  "id" : "",   "format" : "Tristate(False)", "assistantTranslate" : ["false", ""],    "help" : "`True` si la catégorie n'admet plusieurs valeurs que si elles sont dans des langues différentes (par exemple un jeu de données n'a en principe qu'un seul titre, mais il peut être traduit).\n\nPour les catégories communes, les modifications apportées sur ce champ ne seront pas prises en compte. `is_multiple` est ignoré quand `unilang` vaut `True`. Cette information n'est considérée que si `datatype` vaut `'rdf:langString'`."},          
       "is_mandatory"   : {"label" : "Obligatoire",                 "enum" : "",                   "tooltip" : "", "property" : [ "visible", "enabled" ],  "type" : "QCheckBox", "dicListItems" : "",                  "id" : "",   "format" : "Tristate(False)", "assistantTranslate" : ["false", ""],    "help" : "`True` si une valeur doit obligatoirement être saisie pour cette catégorie. \n\n Modifier cette valeur permet de rendre obligatoire une catégorie commune optionnelle, mais pas l''inverse."},         
       "sources"        : {"label" : "Liste des sources",           "enum" : "sources",            "tooltip" : "", "property" : [ "visible", "enabled" ],  "type" : "QLineEdit", "dicListItems" : "",                  "id" : "",   "format" : "list",            "assistantTranslate" : ["true", "list"], "help" : "Pour une catégorie prenant ses valeurs dans un ou plusieurs thésaurus, liste des sources admises. \n\n Cette information n'est considérée que pour les catégories communes. Il n'est pas possible d'ajouter des sources ni de les retirer toutes - Plume reviendrait alors à la liste initiale -, mais ce champ permet de restreindre la liste à un ou plusieurs thésaurus jugés les mieux adaptés."},          
       "geo_tools"      : {"label" : "Géométrie : Liste des aides à la saisie", 
                                                                    "enum" : dicEnum["geo_tools"], "tooltip" : "", "property" : [ "visible", "enabled" ],  "type" : "QLineEdit", "dicListItems" : "",                  "id" : "",   "format" : "list",            "assistantTranslate" : ["true", "list"], "help" : "Pour une catégorie prenant pour valeurs des géométries, liste des fonctionnalités d'aide à la saisie à proposer, parmi `'show'` (visualisation de la géométrie saisie), `'point'` (tracé manuel d'une géométrie ponctuelle), `'linestring'` (tracé manuel d'une géométrie linéaire), `'rectangle'`  (tracé manuel d'un rectangle), `'polygon'` (tracé manuel d'un polygone), `'circle'` (tracé manuel d'un cercle), `'bbox'` (calcul du rectangle d'emprise de la couche courante), `'centroid'` (calcul du centre du rectangle d'emprise de la couche courante). \n\n Cette information ne sera considérée que si le type (`datatype`) est `'gsp:wktLiteral'`. Pour retirer toutes les fonctionnalités proposées par défaut pour une catégorie commune, on saisira une liste vide, soit `ARRAY[]::z_plume.meta_geo_tool[]`."},         
       "compute"        : {"label" : "Liste des modes de calcul",   "enum" : dicEnum["compute"],   "tooltip" : "", "property" : [ "visible", "enabled" ],  "type" : "QLineEdit", "dicListItems" : "",                  "id" : "",   "format" : "list",            "assistantTranslate" : ["true", "list"], "help" : "Liste des fonctionnalités de calcul à proposer, parmis, `'auto'` (déclenchement automatique lorsque la fiche de métadonnées est générée), `'manuel'` (déclenchement à la demande, lorsque l'utilisateur clique sur le bouton qui apparaîtra alors à côté du champ de saisie dans le formulaire). \n\n Cette information ne sera considérée que si une méthode de calcul est effectivement disponible pour la catégorie. Pour retirer toutes les fonctionnalités proposées par défaut pour une catégorie commune, on saisira une liste vide, soit `ARRAY[]::z_plume.meta_compute[]`."},              
       "template_order" : {"label" : "Ordre d'apparence",           "enum" : "",                   "tooltip" : "", "property" : [ "visible", "enabled" ],  "type" : "QLineEdit", "dicListItems" : "",                  "id" : "",   "format" : "integer",         "assistantTranslate" : ["false", ""],    "help" : "Ordre d'apparence de la catégorie dans le formulaire. Les plus petits numéros sont affichés en premier, il n'est pas nécessaire que les numéros se suivent. Dans le cas des catégories communes, qui ont une structure arborescente, il s'agit de l'ordre parmi les catégories de même niveau dans la branche."},         
       "compute_params" : {"label" : "Paramètres des méthodes de calcul",  
                                                                    "enum" : "compute_params",     "tooltip" : "", "property" : [ "visible", "enabled" ],  "type" : "QLineEdit", "dicListItems" : "",                  "id" : "",   "format" : "jsonb",           "assistantTranslate" : ["true", "list"], "help" : "Paramètres optionnels attendus par la méthode de calcul, si opportun. À spécifier sous la forme d'un dictionnaire JSON dont les clés correspondent aux noms des paramètres et les valeurs sont les valeurs des paramètres. Cf. [Métadonnées calculées](./metadonnees_calculees.md) pour plus de détails. \n\n Cette information ne sera considérée que si une méthode de calcul est effectivement disponible pour la catégorie et qu''elle admet un ou plusieurs paramètres."}       
      }

load_mapping_read_meta_tabs  =  \
      {"tab_id"         : {"label" : "Identifiant",   "enum" : "", "tooltip" : "",   "property" : [ "visible", "disabled" ], "type" : "QLineEdit", "dicListItems" : "", "id" : "",   "format" : "integer",         "assistantTranslate" : ["false", ""], "help" : ""},
       "tab_label"      : {"label" : "Libellé",       "enum" : "", "tooltip" : "",   "property" : [ "visible", "enabled" ],  "type" : "QLineEdit", "dicListItems" : "", "id" : "OK", "format" : "text",            "assistantTranslate" : ["false", ""], "help" : "Libellé de l'onglet."},
       "tab_num"        : {"label" : "Position",      "enum" : "", "tooltip" : "",   "property" : [ "visible", "enabled" ],  "type" : "QLineEdit", "dicListItems" : "", "id" : "",   "format" : "integer",         "assistantTranslate" : ["false", ""], "help" : "Position de l'onglet."}         
      }
      
