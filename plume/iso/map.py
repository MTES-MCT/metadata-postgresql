"""Mapping depuis ISO 19139 vers GeoDCAT-AP.

"""

import xml.etree.ElementTree as ET

class IsoXML(ET.Element):
    """XML présumé ISO 19139 renvoyé par un service CSW.
    
    Parameters
    ----------
    raw_xml : str
        Le résultat brut retourné par le CSW.
    
    """
    
    def __new__(cls, raw_xml):
        try:
            xml = ET.fromstring(raw_xml)
        except:
            raise IsoParsingError('XML invalide.')
        return xml
    

class IsoParsingError(Exception):
    """Erreur lors du traitement des XML.
    
    """

