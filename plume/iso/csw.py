"""Utilitaire pour le dialogue avec les services CSW des catalogues.

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

