from urllib.parse import urlencode, urljoin
from urllib import request
from PyQt5.QtCore import QUrl
from qgis.core import QgsNetworkContentFetcher

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
    data = urlencode(config)
    return '{}?{}'.format(url_csw, data)

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
    #-
    evloop = QEventLoop()
    fetcher.finished.connect(evloop.quit)
    evloop.exec_(QEventLoop.ExcludeUserInputEvents)
    fetcher.finished.disconnect(evloop.quit)
    #-
    raw_xml = fetcher.contentAsString()
    print("raw_xml {} ".format(str(raw_xml)))
    #-
    ret = fetcher.reply()
    print("fetcher.reply() {} ".format(str(ret)))



#==================================================
urlGEOIDE,       nameGEOIDE       = "http://ogc.geo-ide.developpement-durable.gouv.fr/csw/dataset-harvestable",     "Catalogage GEOIDE"
urlGEOIDE,       nameGEOIDE       = "https://wxs.ign.fr/catalogue/csw",     "Catalogage IGN"
urlGEOIDE,       nameGEOIDE       = "https://ogc.geo-ide.developpement-durable.gouv.fr/csw/all-dataset",     "Plan d'eau de la Charente"

#mainGeoideID_OK(urlGEOIDE, nameGEOIDE, "fr-120066022-jdd-23d6b4cd-5a3b-4e10-83ae-d8fdad9b04ab")
#mainGeoideID_OK(urlGEOIDE, nameGEOIDE, "IGNF_ADMIN_EXPRESS_3-1.xml")

mainGeoideID_OK(urlGEOIDE, nameGEOIDE, "fr-120066022-jdd-89a93ae4-18f8-425f-ac5c-c1cd6392ff31")
                                        
#==================================================
