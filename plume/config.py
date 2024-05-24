"""Configuration.

"""

# à actualiser à chaque nouvelle version, d'autant que de besoin :

PLUME_VERSION = 'v1.2.1'
"""Version courante de Plume, sous forme litérale."""

PLUME_VERSION_TPL = (1, 2, 1)
"""Version courante de Plume, sous forme de tuple (version majeure, version mineure, correctif)."""

PLUME_PG_MIN_VERSION = '0.3.1'
"""Plus petite version de l'extension PlumePg compatible avec la version courante de Plume."""

PLUME_PG_MAX_VERSION = '1.0.0'
"""Plus petite version de l'extension PlumePg présumée non rétro-compatible avec la version courante de Plume."""

APP_NAME = 'Plume'
"""Nom de l'application."""

COPYRIGHT = 'République française, 2022-2024'
"""Copyright de l'application.

Cette information apparaît aussi dans les fichiers README.md et admin/debian/doc/copyright,
ainsi que dans les en-têtes des scripts de PlumePg, où elle doit être mise à jour manuellement 
à chaque modification de la présente variable.

"""

PUBLISHER = 'Direction du Numérique du ministère de la Transition écologique et de la Cohésion des territoires'
"""Editeur de l'application.

Cette information apparaît aussi dans les fichiers README.md, plume/metadata.txt et 
admin/debian/doc/copyright, ainsi que dans les en-têtes des scripts de PlumePg, où 
elle doit être mise à jour manuellement à chaque modification de la présente variable.

"""

# ===================
# = for Plugin PLUME
# - DL
# ===================
VALUEDEFAUTFILEHELP     = "html"
VALUEDEFAUTFILEHELPPDF  = "https://snum.scenari-community.org/Asgard/PDF/GuideAsgardManager"
VALUEDEFAUTFILEHELPHTML = "https://snum.scenari-community.org/Plume/Documentation"
# - 
LIBURLCSWDEFAUT         = "Géo-IDE,Géoplateforme IGN"
URLCSWDEFAUT            = "http://ogc.geo-ide.developpement-durable.gouv.fr/csw/dataset-harvestable,https://data.geopf.fr/csw"
URLCSWIDDEFAUT          = "fr-120066022-jdd-23d6b4cd-5a3b-4e10-83ae-d8fdad9b04ab,IGNF_GEOFLAr_2-2.xml"
# - pour les items des imports des modèles pré-configurés 
SAMPLE_TEMPLATES        = ['Basique', 'Classique', 'Donnée externe', 'INSPIRE']
