# (c) Didier  LECLERC 2023 MTE-MCTRCT/SG/DNUM/UNI/DRC Site de Rouen
# créé Nov 2023

from qgis.core import QgsApplication, QgsProject

# Initialiser QGIS
qgs = QgsApplication([], False)
qgs.initQgis()

# Charger le projet
project = QgsProject.instance()
project.read('C:/Users/didier.leclerc/Desktop/[Plume] Base PG de demonstration/projet_de_demonstration_GT_POSTGIS_MODELE_Plume.qgs')

# Récupérer le layout par son nom
layout = project.layoutManager().layoutByName('aa')

# Créer un objet QgsLayoutExporter
exporter = QgsLayoutExporter(layout)

# Définir les options d'exportation, notamment pour exporter en GeoPDF
export_settings = QgsLayoutExporter.PdfExportSettings()
export_settings.dpi = 300

#Pour le géoPdf
export_settings.writeGeoPdf = True

# Spécifier le chemin de sortie du fichier GeoPDF
output_file_path = 'C:/Users/didier.leclerc/Desktop/[Plume] Base PG de demonstration/sortie_geopdf.pdf'

# Exporter le layout en GeoPDF
exporter.exportToPdf(output_file_path, export_settings)

# Fermer l'application QGIS
#qgs.exitQgis()

