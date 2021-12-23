"""Mapping depuis ISO 19139 vers GeoDCAT-AP.

"""

from json import load
import xml.etree.ElementTree as etree

from plume.rdf.utils import DatasetId, abspath, forbidden_char
from plume.rdf.namespaces import DCAT, DCT, FOAF, OWL, RDF, \
    RDFS, SKOS, VCARD, XSD, PROV
from plume.rdf.rdflib import URIRef, Literal, BNode


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


class IsoToDcat:
    """Transformation d'un XML ISO 19139 en une liste de triples GeoDCAT-AP.
    
    Parameters
    ----------
    raw_xml : str
        Le résultat brut retourné par le service CSW, présumé être
        un XML conforme au standard ISO 19139.
    datasetid : plume.rdf.utils.DatasetId, optional
        L'identifiant du jeu de données. Si non fourni, un nouvel
        identifiant est généré.
    main_language : str, default 'fr'
        Langue principale de rédaction des métadonnées.
    
    Attributes
    ----------
    isoxml : xml.etree.ElementTree.Element
        La désérialisation de l'élément ``gmd:MD_Metadata``
        contenu dans le XML. Si le XML fourni en paramètre ne
        contenait pas d'élément ``gmd:MD_Metadata``, `root`
        sera initialisé avec un élément vide (cas où la
        requête sur le CSW ne renvoie pas de résultat). Idem
        si la dé-sérialisation du XML a échoué pour une raison
        ou une autre.
    triples : list
        Les triples résultant de la conversation des métadonnées
        selon GeoDCAT-AP.
    datasetid : plume.rdf.utils.DatasetId
        L'identifiant du jeu de données.
    language : str
        Langue de la fiche de métadonnées. Normalement, cette
        information est disponible dans le XML. S'il n'a pas
        été possible de l'extraire, les métadonnées seront
        présumées être dans la langue principale de rédaction
        des métadonnées (paramètre `main_language`).
    iso639_language_codes : dict
        Attribut de classe. Répertoire des codes de langues
        utilisés par les métadonnées ISO 19139. Les clés sont
        les codes sur trois caractères des métadonnées ISO, les
        valeurs sont les codes sur deux caractères utilisés
        préférentiellement pour les valeurs litériales RDF.
    
    Notes
    -----
    Le XML n'est pas validé en entrée. Les éléments non prévus ou
    mal formés ne seront simplement pas exploités.
    
    """
    
    iso639_language_codes = None
 
    def __init__(self, raw_xml, datasetid=None, main_language='fr'):
        try:
            root = etree.fromstring(raw_xml)
            self.isoxml = root.find('./gmd:MD_Metadata', ns) \
                or etree.Element(wns('gmd:MD_Metadata'))
        except:
            self.isoxml = etree.Element(wns('gmd:MD_Metadata'))
        self.triples = []
        self.datasetid = DatasetId(datasetid)
        self.language = self.metadata_language() or main_language
        for attr in dir(self):
            if attr.startswith('map_'):
                triples = getattr(self, attr, [])
                if triples:
                    for triple in triples:
                        if not triple in self.triples:
                            self.triples.append(triple)
    
    @classmethod
    def load_language_codes(cls):
        with open(abspath('iso/data/iso-639-2.json')) as src:
            cls.iso639_language_codes = load(src)
    
    def metadata_language(self):
        code = self.isoxml.findtext('./gmd:language/gmd:LanguageCode',
            namespaces=ns)
        if not code:
            code = self.isoxml.findtext('./gmd:language/gco:CharacterString',
                namespaces=ns)
        if not code or len(code) > 3:
            return
        if code in ('fre', 'fra'):
            return 'fr'
        if not IsoToDcat.iso639_language_codes:
            IsoToDcat.load_language_codes()
        alpha2 = IsoToDcat.iso639_language_codes.get(code)
        # les métadonnées ISO utilise des codes de langue
        # sur trois caractères, RDF privilégie les codes
        # sur deux caractères. iso639_language_codes établit
        # la correspondance.
        return alpha2 or code
    
    @property
    def map_title(self):
        return find_literal(self.isoxml, './gmd:identificationInfo/'
            'gmd:MD_DataIdentification/gmd:citation/'
            'gmd:CI_Citation/gmd:title/gco:CharacterString', self.datasetid,
            DCT.title, language=self.language)

    @property
    def map_description(self):
        return find_literal(self.isoxml, './gmd:identificationInfo/'
            'gmd:MD_DataIdentification/gmd:abstract/gco:CharacterString',
            self.datasetid, DCT.description, language=self.language)

    @property
    def map_organizations(self):
        l = []
        for elem in self.isoxml.findall('./gmd:identificationInfo/'
            'gmd:MD_DataIdentification/gmd:pointOfContact', ns):
            r = elem.find('./gmd:CI_ResponsibleParty/'
                'gmd:role/gmd:CI_RoleCode', namespaces=ns)
            if not r:
                continue
            role_iso = r.text or r.get('codeListValue')
            if not role_iso:
                continue
            node = BNode()
            if role_iso == 'pointOfContact':
                triples = find_literal(elem, './gmd:CI_ResponsibleParty/'
                    'gmd:organisationName/gco:CharacterString', node, VCARD.fn)
                triples += find_iri(elem, './gmd:CI_ResponsibleParty/'
                    'gmd:contactInfo/gmd:CI_Contact/gmd:address/'
                    'gmd:CI_Address/gmd:electronicMailAddress/'
                    'gco:CharacterString', node, VCARD.hasEmail)
                triples += find_iri(elem, './gmd:CI_ResponsibleParty/'
                    'gmd:contactInfo/gmd:CI_Contact/'
                    'gmd:onlineResource/gmd:CI_OnlineResource/'
                    'gmd:linkage/gmd:URL', node, VCARD.hasURL)
                triples += find_iri(elem, './gmd:CI_ResponsibleParty/'
                    'gmd:contactInfo/gmd:CI_Contact/gmd:phone/'
                    'gmd:CI_Telephone/gmd:voice/gco:CharacterString',
                    node, VCARD.hasTelephone)
                if triples:
                    triples.append((self.datasetid, DCAT.contactPoint, node))
                    triples.append((node, RDF.type, VCARD.Kind))
                    l += triples
            else:
                role_iri = 'https://inspire.ec.europa.eu/metadata-codelist/' \
                    'ResponsiblePartyRole/{}'.format(role_iso)
                #TODO
        return l

def find_literal(elem, path, subject, predicate, datatype=None, language=None):
    value = elem.findtext(path, namespaces=ns)
    if value:
        if language:
            return [(subject, predicate, Literal(value, lang=language))]
        if datatype:
            return [(subject, predicate, Literal(value, datatype=datatype))]
        return [(subject, predicate, Literal(value))]
    return []

def find_iri(elem, path, subject, predicate):
    value = elem.findtext(path, namespaces=ns)
    if not value or forbidden_char(value):
        return []
    return [(subject, predicate, URIRef(value))]
    

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




