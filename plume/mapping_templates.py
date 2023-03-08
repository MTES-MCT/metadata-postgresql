"""Configuration.
Fichier de mapping nécessaire pour la gestion des modèles, catégories, onglets et modèles/Catégories
Permet en fonction du nom de la table et du nom de l'attribut, d'obtenir le libellé, l'infobulle, le type pour l'interface  
"""

load_mapping_read_meta_template_categories  =  \
      {"tpl_id"         : {"label" : "identifiant",             "tooltip" : "tooltip identifiant",    "type" : "QLineEdit", "id" : "", "format" : "integer"},
       "shrcat_path"    : {"label" : "libelle shrcat_path",     "tooltip" : "tooltip shrcat_path",    "type" : "QLineEdit", "id" : "", "format" : "text"},
       "loccat_path"    : {"label" : "libelle loccat_path",     "tooltip" : "tooltip loccat_path",    "type" : "QLineEdit", "id" : "", "format" : "text"},         
       "label"          : {"label" : "libelle label",           "tooltip" : "tooltip label",          "type" : "QLineEdit", "id" : "", "format" : "text"},              
       "description"    : {"label" : "libelle description",     "tooltip" : "tooltip description",    "type" : "QLineEdit", "id" : "", "format" : "text"},         
       "special"        : {"label" : "libelle special",         "tooltip" : "tooltip special",        "type" : "QLineEdit", "id" : "", "format" : "text"},          
       "datatype"       : {"label" : "libelle datatype",        "tooltip" : "tooltip datatype",       "type" : "QLineEdit", "id" : "", "format" : "text"},         
       "is_long_text"   : {"label" : "libelle is_long_text",    "tooltip" : "tooltip is_long_text",   "type" : "QCheckBox", "id" : "", "format" : "boolean"},         
       "rowspan"        : {"label" : "libelle rowspan",         "tooltip" : "tooltip rowspan",        "type" : "QLineEdit", "id" : "", "format" : "integer"},          
       "placeholder"    : {"label" : "libelle placeholder",     "tooltip" : "tooltip placeholder",    "type" : "QLineEdit", "id" : "", "format" : "text"},         
       "input_mask"     : {"label" : "libelle input_mask",      "tooltip" : "tooltip input_mask",     "type" : "QLineEdit", "id" : "", "format" : "text"},         
       "is_multiple"    : {"label" : "libelle is_multiple",     "tooltip" : "tooltip is_multiple",    "type" : "QCheckBox", "id" : "", "format" : "boolean"},         
       "unilang"        : {"label" : "libelle unilang",         "tooltip" : "tooltip unilang",        "type" : "QLineEdit", "id" : "", "format" : "text"},          
       "is_mandatory"   : {"label" : "libelle is_mandatory",    "tooltip" : "tooltip is_mandatory",   "type" : "QCheckBox", "id" : "", "format" : "boolean"},         
       "sources"        : {"label" : "libelle sources",         "tooltip" : "tooltip sources",        "type" : "QLineEdit", "id" : "", "format" : "text"},          
       "geo_tools"      : {"label" : "libelle geo_tools",       "tooltip" : "tooltip geo_tools",      "type" : "QLineEdit", "id" : "", "format" : "text"},         
       "template_order" : {"label" : "libelle template_order",  "tooltip" : "tooltip template_order", "type" : "QLineEdit", "id" : "", "format" : "integer"},         
       "is_read_only"   : {"label" : "libelle is_read_only",    "tooltip" : "tooltip is_read_only",   "type" : "QChekcBox", "id" : "", "format" : "boolean"},         
       "tab_id"         : {"label" : "id tab",                  "tooltip" : "tooltip tab id",         "type" : "QLineEdit", "id" : "", "format" : "text"},                                  
       "compute_params" : {"label" : "libelle compute_params",  "tooltip" : "tooltip compute_params", "type" : "QLineEdit", "id" : "", "format" : "jsonb"}       
      } 

load_mapping_read_meta_templates  =  \
      {"tpl_id"         : {"label" : "identifiant",             "tooltip" : "tooltip identifiant",    "type" : "QLineEdit", "id" : "", "format" : "integer"},
       "tpl_label"      : {"label" : "libelle tpl_label",       "tooltip" : "tooltip tpl_label",      "type" : "QLineEdit", "id" : "OK", "format" : "text"},
       "sql_filter"     : {"label" : "libelle sql_filter",      "tooltip" : "tooltip sql_filter",     "type" : "QLineEdit", "id" : "",   "format" : "text"},         
       "md_conditions"  : {"label" : "libelle md_conditions",   "tooltip" : "tooltip md_conditions",  "type" : "QLineEdit", "id" : "",   "format" : "jsonb"},              
       "priority"       : {"label" : "libelle priority",        "tooltip" : "tooltip priority",       "type" : "QLineEdit", "id" : "",   "format" : "integer"},         
       "comment"        : {"label" : "libelle comment",         "tooltip" : "tooltip comment",        "type" : "QLineEdit", "id" : "",   "format" : "text"},          
       "enabled"        : {"label" : "libelle enabled",         "tooltip" : "tooltip enabled",        "type" : "QCheckBox", "id" : "",   "format" : "boolean"}         
      } 