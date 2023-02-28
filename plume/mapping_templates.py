"""Configuration.
Fichier de mapping nécessaire pour la gestion des modèles
Permet en fonction du nom de la table et du nom de l'attribut, d'obtenir le libellé, l'infobulle pour l'interface  
"""

load_mapping_read_meta_template_categories  =  \
      {"shrcat_path"    : {"label" : "libelle shrcat_path",     "tooltip" : "tooltip shrcat_path",    "type" : "QLineEdit"},
       "loccat_path"    : {"label" : "libelle loccat_path",     "tooltip" : "tooltip loccat_path",    "type" : "QLineEdit"},         
       "label"          : {"label" : "libelle label",           "tooltip" : "tooltip label",          "type" : "QLineEdit"},              
       "description"    : {"label" : "libelle description",     "tooltip" : "tooltip description",    "type" : "QLineEdit"},         
       "special"        : {"label" : "libelle special",         "tooltip" : "tooltip special",        "type" : "QLineEdit"},          
       "datatype"       : {"label" : "libelle datatype",        "tooltip" : "tooltip datatype",       "type" : "QLineEdit"},         
       "is_long_text"   : {"label" : "libelle is_long_text",    "tooltip" : "tooltip is_long_text",   "type" : "QCheckBox"},         
       "rowspan"        : {"label" : "libelle rowspan",         "tooltip" : "tooltip rowspan",        "type" : "QLineEdit"},          
       "placeholder"    : {"label" : "libelle placeholder",     "tooltip" : "tooltip placeholder",    "type" : "QLineEdit"},         
       "input_mask"     : {"label" : "libelle input_mask",      "tooltip" : "tooltip input_mask",     "type" : "QLineEdit"},         
       "is_multiple"    : {"label" : "libelle is_multiple",     "tooltip" : "tooltip is_multiple",    "type" : "QCheckBox"},         
       "unilang"        : {"label" : "libelle unilang",         "tooltip" : "tooltip unilang",        "type" : "QLineEdit"},          
       "is_mandatory"   : {"label" : "libelle is_mandatory",    "tooltip" : "tooltip is_mandatory",   "type" : "QCheckBox"},         
       "sources"        : {"label" : "libelle sources",         "tooltip" : "tooltip sources",        "type" : "QLineEdit"},          
       "geo_tools"      : {"label" : "libelle geo_tools",       "tooltip" : "tooltip geo_tools",      "type" : "QLineEdit"},         
       "template_order" : {"label" : "libelle template_order",  "tooltip" : "tooltip template_order", "type" : "QLineEdit"},         
       "is_read_only"   : {"label" : "libelle is_read_only",    "tooltip" : "tooltip is_read_only",   "type" : "QChekcBox"},         
       "tab"            : {"label" : "libelle tab",             "tooltip" : "tooltip tab",            "type" : "QLineEdit"},                                  
       "compute_params" : {"label" : "libelle compute_params",  "tooltip" : "tooltip compute_params", "type" : "QLineEdit"}       
      } 
