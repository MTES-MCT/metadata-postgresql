"""Mapping depuis ISO 19139 vers GeoDCAT-AP.

"""

import xml.etree.ElementTree as etree

ns = {
    'csw': 'http://www.opengis.net/cat/csw/2.0.2',
    'apiso': 'http://www.opengis.net/cat/csw/apiso/1.0',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'dct': 'http://purl.org/dc/terms/',
    'gmd': 'http://www.isotc211.org/2005/gmd',
    'gml': 'http://www.opengis.net/gml',
    'ogc': 'http://www.opengis.net/ogc',
    'ows': 'http://www.opengis.net/ows',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    'gco': 'http://www.isotc211.org/2005/gco',
    'gmx': 'http://www.isotc211.org/2005/gmx',
    'xlink': 'http://www.w3.org/1999/xlink'
    }
   

class IsoXml(etree.Element):
    """XML présumé conforme ISO 19139 renvoyé par un service CSW.
    
    Plus précisément, les objets de classe `IsoXml` sont
    des éléments ``gmd:MD_Metadata``. Ils peuvent ne contenir
    aucune métadonnée, notamment si le XML fournit à l'initialisation
    ne contenait pas d'élément ``gmd:MD_Metadata`` (cas où la
    requête sur le CSW ne renvoie pas de résultat), où si la 
    dé-sérialisation du XML a échoué pour une raison ou une autre.
    
    Le XML n'est pas validé en entrée. Les éléments non prévus ou
    mal formés ne seront simplement pas exploités.
    
    Parameters
    ----------
    raw_xml : str
        Le résultat brut retourné par le CSW.
    
    """
    
    def __new__(cls, raw_xml):
        try:
            root = etree.fromstring(raw_xml)
        except:
            return etree.Element(wns('gmd:MD_Metadata'))
        isoxml = root.find('./gmd:MD_Metadata', ns) \
            or etree.Element(wns('gmd:MD_Metadata'))
            # NB: si le XML contient plusieurs éléments
            # gmd:MD_Metadata, le premier est conservé
        return isoxml


def wns(tag):
    """Explicite le tag en remplaçant le préfixe par l'URL de l'espace de nommage correspondant.
    
    La fonction n'aura pas d'effet si le tag n'est pas de la forme
    ``'prefix:objet'`` ou si le préfixe n'est pas reconnu. Le tag
    est alors retourné inchangé.
    
    Parameters
    ----------
    tag : str
        Un tag XML présumé contenir un préfixe
        d'espace de nommage.
    
    Returns
    -------
    str
    
    """
    l = tag.split(':', maxsplit=1)
    if not len(l) == 2 or not l[0] in ns:
        return tag
    return '{{{}}}{}'.format(ns[l[0]], l[1])    




