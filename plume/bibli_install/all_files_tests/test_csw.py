from urllib.parse import urlencode, urljoin
from urllib import request
from PyQt5.QtCore import QUrl
from qgis.core import QgsNetworkContentFetcher
import time

#==================================================
"""Utilitaires pour le dialogue avec les services CSW des catalogues.
"""
def getrecordbyid_request(url_csw, file_identifier):
    """Crée une requête GetRecordById pour envoi en HTTP GET.
    
    Parameters
    ----------
    url_csw : str
        L'URL de base du service CSW du catalogue, sans aucun paramètre.
    file_identifier : str
        L'identifiant de la fiche de métadonnées sur le catalogue.
        Correspond à la valeur de la balise ``gmd:fileIdentifier``
        des fiches ISO 19139.
    
    Returns
    -------
    str
    
    Examples
    --------
    >>> r = getrecordbyid_request(
    ...     'http://ogc.geo-ide.developpement-durable.gouv.fr/csw/dataset-harvestable', 
    ...     'fr-120066022-jdd-d3d794eb-76ba-450a-9f03-6eb84662f297'
    ...     )
    >>> from urllib.request import urlopen
    >>> with urlopen(r) as src:
    ...     xml = src.read()
    
    Notes
    -----
    La requête n'est pas en encodage-pourcent, car elle a vocation à être
    passée au constructeur de la classe :py:class:`PyQt5.QtCore.QUrl` qui
    s'en chargera.
    
    """
    url_csw = url_csw.rstrip('?/')
    config = {
        'service' : 'CSW',
        'REQUEST': 'GetRecordById',
        'version': '2.0.2',
        'namespace': 'xmlns:csw=http://www.opengis.net/cat/csw',
        'outputFormat': 'application/xml',
        'outputSchema': 'http://www.isotc211.org/2005/gmd',
        'ElementSetName': 'full',
        'Id': file_identifier
        }
    data = '&'.join('{}={}'.format(k, v) for k, v in config.items())
    return '{}?{}'.format(url_csw, data)

#http://ogc.geo-ide.developpement-durable.gouv.fr/csw/dataset-harvestable?service=CSW&REQUEST=GetRecordById&version=2.0.2&namespace=xmlns:csw=http://www.opengis.net/cat/csw&outputFormat=application/xml&outputSchema=http://www.isotc211.org/2005/gmd&ElementSetName=full&Id=fr-120066022-jdd-23d6b4cd-5a3b-4e10-83ae-d8fdad9b04ab
#http://ogc.geo-ide.developpement-durable.gouv.fr/csw/dataset-harvestable?service=CSW&REQUEST=GetRecordById&version=2.0.2&namespace=xmlns%3Acsw%3Dhttp%3A%2F%2Fwww.opengis.net%2Fcat%2Fcsw&outputFormat=application%2Fxml&outputSchema=http%3A%2F%2Fwww.isotc211.org%2F2005%2Fgmd&ElementSetName=full&Id=fr-120066022-jdd-23d6b4cd-5a3b-4e10-83ae-d8fdad9b04ab


import xml.etree.ElementTree as ET

#==================================================
def return_reponse_xml(reponse_xml) :

   # Analyser la réponse XML
   root = ET.fromstring(reponse_xml)
   print("root ", root)


   namespace = "{" + root.tag.split('}')[0][1:] + "}"
   print("namespace ", namespace)


   children = list(root)

   if children:
       for child in children:
           # Traitez les balises enfants ici
           print("Balise enfant:", child.tag)
   else:
       print("Aucune balise enfant trouvée dans <csw:GetRecordByIdResponse>.")

   

   print("children ", children)

#==================================================
def mainGeoideID_OK(urlCatalogue, nameCatalogue, idSet) :
    print("\n====== {} ======".format(str(nameCatalogue)))


    resultQueryId = getrecordbyid_request(urlCatalogue, idSet)
    print("DEBUT")
    print(resultQueryId)
    print("FIN")
    url = QUrl(resultQueryId)
    fetcher = QgsNetworkContentFetcher()

    fetcher.fetchContent(url)
    raw_xml = fetcher.contentAsString()
    print("raw_xml {} ".format(str(raw_xml)))
    #-
    time_1 = time.time()
    #time.sleep(240)

    evloop = QEventLoop()
    print("AVANT 1")
    fetcher.finished.connect(evloop.quit)
    print("AVANT 2")
    evloop.exec_(QEventLoop.ExcludeUserInputEvents)
    print("AVANT 3")
    fetcher.finished.disconnect(evloop.quit)
    print("AVANT 4")

    time_2 = time.time()
    print(time_2 - time_1)
    #-
    raw_xml = fetcher.contentAsString()
    print("raw_xml **{}** ".format(str(raw_xml)))
    #-
    ret = fetcher.reply()
    print("fetcher.reply() **{}** ".format(str(fetcher.reply())))

    print(ret)
    print(ret.error())
    print(ret.errorString())
    print("fetcher.reply() {} ".format(str(ret)))
    print("fetcher.reply().error() {} ".format(str(ret.error())))
    print("fetcher.reply().errorString() {} ".format(str(ret.errorString())))
    
        
    #- Cas ou le serveur CSW ne renvoie rien https://github.com/MTES-MCT/metadata-postgresql/issues/146 
    if raw_xml == "" : 
       ret = fetcher.reply()
       raw_xml = [ None, str(ret.error()), str(ret.errorString()) ]
    print(type(raw_xml))
    
    return_reponse_xml(raw_xml)
    return


#==================================================
#Test KO
"""
urlGEOIDE,       nameGEOIDE       = "https://id.insee.fr/geo/region/28",     "Catalogage GEOIDE"
mainGeoideID_OK(urlGEOIDE, nameGEOIDE, "fr-120066022-jdd-1c02c1c1-cd81-4cd5-902e-acbd3d4e5527")

#Test OK A
urlGEOIDE,       nameGEOIDE       = "http://ogc.geo-ide.developpement-durable.gouv.fr/csw/dataset-harvestable",     "Catalogage GEOIDE"
mainGeoideID_OK(urlGEOIDE, nameGEOIDE, "fr-120066022-jdd-23d6b4cd-5a3b-4e10-83ae-d8fdad9b04ab")
"""

#Test KO A cgt d'id
urlGEOIDE,       nameGEOIDE       = "http://ogc.geo-ide.developpement-durable.gouv.fr/csw/dataset-harvestable",     "Catalogage GEOIDE"
mainGeoideID_OK(urlGEOIDE, nameGEOIDE, "fr-120066022-jdd-23d6b4cd-5a3b-4e10-83ae-bad-url")
#mainGeoideID_OK(urlGEOIDE, nameGEOIDE, "fr-120066022-jdd-23d6b4cd-5a3b-4e10-83ae-d8fdad9b04ab")

#http://ogc.geo-ide.developpement-durable.gouv.fr/csw/dataset-harvestable?service=CSW&REQUEST=GetRecordById&version=2.0.2&namespace=xmlns%3Acsw%3Dhttp%3A%2F%2Fwww.opengis.net%2Fcat%2Fcsw&outputSchema=http%3A%2F%2Fwww.isotc211.org%2F2005%2Fgmd&ElementSetName=full&Id=fr-120066022-jdd-23d6b4cd-5a3b-4e10-83ae-d8fdad9b04ab

                                        
#==================================================
