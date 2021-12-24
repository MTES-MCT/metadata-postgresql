"""Mapping depuis ISO 19139 vers GeoDCAT-AP.

"""

from json import load
import xml.etree.ElementTree as etree

from plume.rdf.utils import DatasetId, abspath, forbidden_char, \
    owlthing_from_email, owlthing_from_tel
from plume.rdf.namespaces import DCAT, DCT, FOAF, OWL, RDF, \
    RDFS, SKOS, VCARD, XSD, GEODCAT
from plume.rdf.rdflib import URIRef, Literal, BNode
from plume.rdf.thesaurus import Thesaurus


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
    triples : list of tuples
        Liste des triples résultant de la conversation des
        métadonnées selon GeoDCAT-AP.
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
    def map_epsg(self):
        epsg = self.isoxml.findtext('./gmd:referenceSystemInfo/'
            'gmd:MD_ReferenceSystem/gmd:referenceSystemIdentifier/'
            'gmd:RS_Identifier/gmd:code/gmx:Anchor',
            namespaces=ns)
        if not epsg:
            epsg_txt = self.isoxml.findtext('./gmd:referenceSystemInfo/'
                'gmd:MD_ReferenceSystem/gmd:referenceSystemIdentifier/'
                'gmd:RS_Identifier/gmd:code/gco:CharacterString',
                namespaces=ns)
            r = re.search('EPSG:([0-9]*)', epsg_txt)
            if r:
                epsg = r[1]
        if not epsg:
            return []
        node = BNode()
        return [(self.datasetid, DCT.conformsTo, node),
            (node, SKOS.inScheme, URIRef('http://www.opengis.net/def/crs/EPSG/0')),
            (node, DCT.identifier, Literal(epsg))]

    @property
    def map_dates(self):
        l = []
        type_map = {
            'creation': DCT.created,
            'revision': DCT.issued,
            'publication': DCT.modified
            }
        for elem in self.isoxml.findall('./gmd:identificationInfo/'
            'gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/'
            'gmd:date', namespaces=ns):
            c = elem.find('./gmd:CI_Date/gmd:dateType/'
                'gmd:CI_DateTypeCode', namespaces=ns)
            if c is None:
                continue
            code = c.text or c.get('codeListValue')
            if not code or not code in type_map:
                continue
            l += find_literal(elem, './gmd:CI_Date/gmd:date/'
                'gco:Date', self.datasetid, type_map[code],
                datatype=XSD.date)
        return l

    @property
    def map_keywords(self):
        l = []
        for elem in self.isoxml.findall('./gmd:identificationInfo/'
            'gmd:MD_DataIdentification/gmd:descriptiveKeywords',
            namespaces=ns):
            t = elem.findtext('./gmd:MD_Keywords/gmd:thesaurusName/'
                'gmd:CI_Citation/gmd:title/gco:CharacterString',
                namespaces=ns)
            keyword = elem.findtext('./gmd:MD_Keywords/gmd:keyword/'
                'gco:CharacterString', namespaces=ns)
            if t and 'INSPIRE themes' in t:
                keyword_iri = Thesaurus.concept_iri((
                    URIRef('https://inspire.ec.europa.eu/theme'),
                    self.language), keyword)
                if keyword_iri:
                    l.append((self.datasetid, DCAT.theme, keyword_iri))
                    continue
            l.append((self.datasetid, DCAT.keyword,
                Literal(keyword, lang=self.language)))
        return l

    @property
    def map_access_rights(self):
        return find_iri(self.isoxml, './gmd:identificationInfo/'
            'gmd:MD_DataIdentification/gmd:resourceConstraints/'
            'gmd:MD_LegalConstraints/gmd:otherConstraints/'
            'gco:CharacterString', self.datasetid, DCT.accessRights,
            thesaurus=URIRef('http://inspire.ec.europa.eu/'
                'metadata-codelist/LimitationsOnPublicAccess'))        

    @property
    def map_organizations(self):
        l = []
        role_map = {
            'resourceProvider': GEODCAT.resourceProvider,
            'custodian': GEODCAT.custodian,
            'owner': DCT.rightsHolder,
            'user': GEODCAT.user,
            'distributor': GEODCAT.distributor,
            'originator': GEODCAT.originator,
            'principalInvestigator': GEODCAT.principalInvestigator,
            'processor': GEODCAT.processor,
            'publisher': DCT.publisher,
            'author': DCT.creator,
            'pointOfContact': DCAT.contactPoint
            }
        for elem in self.isoxml.findall('./gmd:identificationInfo/'
            'gmd:MD_DataIdentification/gmd:pointOfContact', ns):
            r = elem.find('./gmd:CI_ResponsibleParty/'
                'gmd:role/gmd:CI_RoleCode', namespaces=ns)
            if r is None:
                continue
            role = r.text or r.get('codeListValue')
            if not role or not role in role_map:
                continue
            node = BNode()
            if role == 'pointOfContact':
                triples = find_literal(elem, './gmd:CI_ResponsibleParty/'
                    'gmd:individualName/gco:CharacterString', node, VCARD.fn)
                triples += find_literal(elem, './gmd:CI_ResponsibleParty/'
                    'gmd:organisationName/gco:CharacterString', node,
                    VCARD['organization-name'] if triples else VCARD.fn)
                triples += find_iri(elem, './gmd:CI_ResponsibleParty/'
                    'gmd:contactInfo/gmd:CI_Contact/gmd:address/'
                    'gmd:CI_Address/gmd:electronicMailAddress/'
                    'gco:CharacterString', node, VCARD.hasEmail,
                    transform='email')
                triples += find_iri(elem, './gmd:CI_ResponsibleParty/'
                    'gmd:contactInfo/gmd:CI_Contact/'
                    'gmd:onlineResource/gmd:CI_OnlineResource/'
                    'gmd:linkage/gmd:URL', node, VCARD.hasURL)
                triples += find_iri(elem, './gmd:CI_ResponsibleParty/'
                    'gmd:contactInfo/gmd:CI_Contact/gmd:phone/'
                    'gmd:CI_Telephone/gmd:voice/gco:CharacterString',
                    node, VCARD.hasTelephone, transform='phone')
                if triples:
                    triples.append((self.datasetid, DCAT.contactPoint, node))
                    triples.append((node, RDF.type, VCARD.Kind))
                    l += triples
            else:
                predicate = role_map[role]
                triples = find_literal(elem, './gmd:CI_ResponsibleParty/'
                    'gmd:organisationName/gco:CharacterString', node, FOAF.name)
                triples += find_iri(elem, './gmd:CI_ResponsibleParty/'
                    'gmd:contactInfo/gmd:CI_Contact/gmd:address/'
                    'gmd:CI_Address/gmd:electronicMailAddress/'
                    'gco:CharacterString', node, FOAF.mbox,
                    transform='email')
                triples += find_iri(elem, './gmd:CI_ResponsibleParty/'
                    'gmd:contactInfo/gmd:CI_Contact/'
                    'gmd:onlineResource/gmd:CI_OnlineResource/'
                    'gmd:linkage/gmd:URL', node, FOAF.workplaceHomepage)
                triples += find_iri(elem, './gmd:CI_ResponsibleParty/'
                    'gmd:contactInfo/gmd:CI_Contact/gmd:phone/'
                    'gmd:CI_Telephone/gmd:voice/gco:CharacterString',
                    node, FOAF.phone, transform='phone')
                if triples:
                    triples.append((self.datasetid, predicate, node))
                    triples.append((node, RDF.type, FOAF.Agent))
                    l += triples
        return l

def find_literal(elem, path, subject, predicate, multi=False, datatype=None, language=None):
    l = []
    for sub in elem.findall(path, namespaces=ns):
        value = sub.text
        if not value:
            continue
        if language:
            l.append((subject, predicate, Literal(value, lang=language)))
        elif datatype:
            l.append((subject, predicate, Literal(value, datatype=datatype)))
        else:
            l.append((subject, predicate, Literal(value)))
        if not multi:
            break
    return l

def find_iri(elem, path, subject, predicate, multi=False, transform=None, thesaurus=None):
    l = []
    for sub in elem.findall(path, namespaces=ns):
        value = sub.text
        if not value or forbidden_char(value):
            continue
        if transform == 'email':
            value = owlthing_from_email(value)
        elif transform == 'phone':
            value = owlthing_from_tel(value)
        elif thesaurus:
            value = Thesaurus.concept_iri((thesaurus, self.language), value)
            if not value:
                continue
        l.append((subject, predicate, URIRef(value)))
        if not multi:
            break
    return l    

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




