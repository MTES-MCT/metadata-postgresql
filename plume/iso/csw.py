"""Utilitaires pour le dialogue avec les services CSW des catalogues.

"""

from urllib.parse import urlencode, urljoin


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
    ...     'http://ogc.geo-ide.developpement-durable.gouv.fr/csw/harvestable-dataset', 
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

def getcapabilities_request(url_csw):
    """Crée une requête GetCapabilities pour envoi en HTTP GET.
    
    Parameters
    ----------
    url_csw : str
        L'URL de base du service CSW du catalogue, sans aucun paramètre.
    
    Returns
    -------
    str
    
    Examples
    --------
    >>> r = getcapabilities_request(
    ...     'http://ogc.geo-ide.developpement-durable.gouv.fr/csw/harvestable-dataset'
    ...     )
    >>> from urllib.request import urlopen
    >>> with urlopen(r) as src:
    ...     xml = src.read()
    
    """
    url_csw = url_csw.rstrip('?/')
    config = {
        'service' : 'CSW',
        'REQUEST': 'GetCapabilities',
        'version': '2.0.2',
        'outputFormat': 'application/xml'
        }
    data = urlencode(config)
    return '{}?{}'.format(url_csw, data)
    

