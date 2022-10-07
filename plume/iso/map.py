"""Mapping depuis ISO 19139 vers GeoDCAT-AP.

"""

import re
from json import load
import xml.etree.ElementTree as etree

from plume.rdf.utils import DatasetId, abspath, forbidden_char, \
    owlthing_from_email, owlthing_from_tel
from plume.rdf.namespaces import DCAT, DCT, FOAF, RDF, \
    RDFS, SKOS, VCARD, XSD, GEODCAT
from plume.rdf.rdflib import URIRef, Literal, BNode
from plume.rdf.thesaurus import Thesaurus


ISO_NS = {
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
    """Transcripteur ISO 19139 / GeoDCAT-AP.
    
    Parameters
    ----------
    raw_xml : str
        Le résultat brut retourné par le service CSW, présumé être
        un XML conforme au standard ISO 19139.
    datasetid : plume.rdf.utils.DatasetId, optional
        L'identifiant du jeu de données. Si non fourni, un nouvel
        identifiant est généré.
    
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
        présumées être en français.
    
    Notes
    -----
    Le XML n'est pas validé en entrée. Les éléments non prévus ou
    mal formés ne seront simplement pas exploités.
    
    """
    
    iso639_language_codes = None
    """dict: Mapping des codes de langue de trois caractères en codes à deux caractères.
    
    Répertoire des codes de langues utilisés par les métadonnées
    ISO 19139. Les clés sont les codes sur trois caractères des
    métadonnées ISO, les valeurs sont les codes sur deux caractères
    utilisés préférentiellement pour les valeurs litériales RDF.
    
    Ce dictionnaire est chargé si besoin à l'initialisation d'un nouvel
    objet, grâce à la méthode :py:meth:`IsoToDcat.load_language_codes`.
    
    """
 
    def __init__(self, raw_xml, datasetid=None):
        try:
            root = etree.fromstring(raw_xml)
            if root.tag == wns('gmd:MD_Metadata'):
                self.isoxml = root
            else:
                self.isoxml = root.find('./gmd:MD_Metadata', ISO_NS) \
                    or etree.Element(wns('gmd:MD_Metadata'))
        except:
            self.isoxml = etree.Element(wns('gmd:MD_Metadata'))
        self.triples = []
        self.datasetid = DatasetId(datasetid)
        self.language = self.metadata_language or 'fr'
        for attr in dir(self):
            if attr.startswith('map_'):
                triples = getattr(self, attr, [])
                if triples:
                    for triple in triples:
                        if not triple in self.triples:
                            self.triples.append(triple)
    
    @classmethod
    def load_language_codes(cls):
        """Charge le dictionnaire des codes de langues.
        
        """
        with open(abspath('iso/data/iso-639-2.json')) as src:
            cls.iso639_language_codes = load(src)
    
    @property
    def metadata_language(self):
        """str: Langue des métadonnées.
        
        Cette propriété est recalculée à chaque interrogation à partir
        du XML.
        
        """
        code = self.isoxml.findtext('./gmd:language/gmd:LanguageCode',
            namespaces=ISO_NS)
        if not code:
            code = self.isoxml.findtext('./gmd:language/gco:CharacterString',
                namespaces=ISO_NS)
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
        """list of tuples: Triples contenant le libellé du jeu de données.
        
        Cette propriété est recalculée à chaque interrogation à partir
        du XML. Si l'information n'était pas disponible dans le XML,
        une liste vide est renvoyée.
        
        """
        return find_literal(self.isoxml, './gmd:identificationInfo/'
            'gmd:MD_DataIdentification/gmd:citation/'
            'gmd:CI_Citation/gmd:title/gco:CharacterString', self.datasetid,
            DCT.title, language=self.language)

    @property
    def map_description(self):
        """list of tuples: Triples contenant le descriptif du jeu de données.
        
        Cette propriété est recalculée à chaque interrogation à partir
        du XML. Si l'information n'était pas disponible dans le XML,
        une liste vide est renvoyée.
        
        """
        return find_literal(self.isoxml, './gmd:identificationInfo/'
            'gmd:MD_DataIdentification/gmd:abstract/gco:CharacterString',
            self.datasetid, DCT.description, language=self.language)

    @property
    def map_epsg(self):
        """list of tuples: Triples contenant le ou les référentiels de coordonnées du jeu de données.
        
        Cette propriété est recalculée à chaque interrogation à partir
        du XML. Si l'information n'était pas disponible dans le XML,
        une liste vide est renvoyée.
        
        """
        l = []
        for elem in self.isoxml.findall('./gmd:referenceSystemInfo/'
            'gmd:MD_ReferenceSystem/gmd:referenceSystemIdentifier/'
            'gmd:RS_Identifier/gmd:code', namespaces=ISO_NS):
            epsg = None
            epsg_txt = elem.findtext('./gmx:Anchor',
                namespaces=ISO_NS)
            if not epsg_txt:
                epsg_txt = elem.findtext('./gco:CharacterString',
                    namespaces=ISO_NS)
            if not epsg_txt:
                continue
            if epsg_txt.isdigit():
                epsg = epsg_txt
            else:
                r = re.search('EPSG:([0-9]*)', epsg_txt)
                if r:
                    epsg = r[1]
            node = BNode()
            l += [(self.datasetid, DCT.conformsTo, node),
                (node, SKOS.inScheme, URIRef('http://www.opengis.net/def/crs/EPSG/0'))]
            if epsg:
                l.append((node, DCT.identifier, Literal(epsg)))
            if epsg_txt != epsg:
                l.append((node, DCT.title, Literal(epsg_txt,
                    lang=self.language)))
        return l

    @property
    def map_dates(self):
        """list of tuples: Triples contenant les dates du jeu de données.
        
        Cette propriété est recalculée à chaque interrogation à partir
        du XML. Si l'information n'était pas disponible dans le XML,
        une liste vide est renvoyée.
        
        """
        l = []
        type_map = {
            'creation': DCT.created,
            'revision': DCT.modified,
            'publication': DCT.issued
            }
        for elem in self.isoxml.findall('./gmd:identificationInfo/'
            'gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/'
            'gmd:date', namespaces=ISO_NS):
            c = elem.find('./gmd:CI_Date/gmd:dateType/'
                'gmd:CI_DateTypeCode', namespaces=ISO_NS)
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
        """list of tuples: Triples contenant les mots-clés.
        
        Cette propriété est recalculée à chaque interrogation à partir
        du XML. Si l'information n'était pas disponible dans le XML,
        une liste vide est renvoyée.
        
        """
        l = []
        for elem in self.isoxml.findall('./gmd:identificationInfo/'
            'gmd:MD_DataIdentification/gmd:descriptiveKeywords',
            namespaces=ISO_NS):
            t = elem.findtext('./gmd:MD_Keywords/gmd:thesaurusName/'
                'gmd:CI_Citation/gmd:title/gco:CharacterString',
                namespaces=ISO_NS)
            for subelem in elem.findall('./gmd:MD_Keywords/gmd:keyword',
                namespaces=ISO_NS):
                keyword = subelem.findtext('./gco:CharacterString',
                    namespaces=ISO_NS)
                if t and 'INSPIRE themes' in t:
                    keyword_iri = Thesaurus.concept_iri((
                        URIRef('https://inspire.ec.europa.eu/theme'),
                        (self.language,)), keyword)
                    if keyword_iri:
                        l.append((self.datasetid, DCAT.theme, keyword_iri))
                        continue
                for k in keyword.split(','):
                    if k:
                        l.append((self.datasetid, DCAT.keyword,
                            Literal(k.strip(), lang=self.language)))
        return l

    @property
    def map_categories(self):
        """list of tuples: Triples contenant la ou les catégories ISO 19115.
        
        Cette propriété est recalculée à chaque interrogation à partir
        du XML. Si l'information n'était pas disponible dans le XML,
        une liste vide est renvoyée.
        
        """
        l = []
        for elem in self.isoxml.findall('./gmd:identificationInfo/'
            'gmd:MD_DataIdentification/gmd:topicCategory',
            namespaces=ISO_NS):
            code = elem.findtext('./gmd:MD_TopicCategoryCode',
                namespaces=ISO_NS)
            if not code:
                continue
            iri = URIRef('http://inspire.ec.europa.eu/metadata-codelist/'
                'TopicCategory/{}'.format(code))
            label = Thesaurus.concept_str((URIRef('https://inspire.ec.'
                'europa.eu/metadata-codelist/TopicCategory'),
                (self.language,)), iri)
            if not label:
                # on ne conserve que les codes qui existent dans le
                # thésaurus
                continue
            l.append((self.datasetid, DCAT.theme, iri))
        return l

    @property
    def map_provenance(self):
        """list of tuples: Triples contenant la généalogie des données.
        
        Cette propriété est recalculée à chaque interrogation à partir
        du XML. Si l'information n'était pas disponible dans le XML,
        une liste vide est renvoyée.
        
        """
        node = BNode()
        triples = find_literal(self.isoxml, './gmd:dataQualityInfo/'
            'gmd:DQ_DataQuality/gmd:lineage/gmd:LI_Lineage/'
            'gmd:statement/gco:CharacterString', node, RDFS.label,
            language=self.language)
        if triples:
            triples.append((self.datasetid, DCT.provenance, node))
        return triples

    @property
    def map_organizations(self):
        """list of tuples: Triples contenant les informations relatives aux organisations responsables.
        
        Cette propriété est recalculée à chaque interrogation à partir
        du XML. Si l'information n'était pas disponible dans le XML,
        une liste vide est renvoyée.
        
        """
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
            'gmd:MD_DataIdentification/gmd:pointOfContact', ISO_NS):
            r = elem.find('./gmd:CI_ResponsibleParty/'
                'gmd:role/gmd:CI_RoleCode', namespaces=ISO_NS)
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
    """Extrait des valeurs litérales d'un XML et les renvoie sous forme de triples.
    
    Parameters
    ----------
    elem : xml.etree.ElementTree.Element
        Un élément XML présumé contenir l'information
        recherchée.
    path : str
        Le chemin de l'information recherchée dans le XML.
    subject : plume.rdf.utils.DatasetId or rdflib.term.BNode
        L'identifiant du graphe ou le noeud anonyme sujet
        des triples à renvoyer.
    predicate : rdflib.term.URIRef
        La propriété qui sera le prédicat des triples
        renvoyés.
    multi : bool, default False
        La propriété admet-elle plusieurs valeurs ? Si ``False``,
        la fonction s'arrête dès qu'une valeur a été trouvée,
        même si le XML en contenait plusieurs.
    datatype : URIRef, optional
        Le cas échéant, l'IRI du type de données. Les types XSD.string
        et RDF.langString ne doivent pas être spécifiés.
    language : str, optional
        Le cas échéant, la langue de la valeur.
    
    Returns
    -------
    list of tuples
        Une liste de triples, ou une liste vide si le chemin cherché
        n'était pas présent dans le XML.
    
    """
    l = []
    for sub in elem.findall(path, namespaces=ISO_NS):
        value = sub.text
        if not value:
            continue
        if language:
            l.append((subject, predicate, Literal(value, lang=language)))
        elif datatype and datatype != XSD.string:
            l.append((subject, predicate, Literal(value, datatype=datatype)))
        else:
            l.append((subject, predicate, Literal(value)))
        if not multi:
            break
    return l

def find_iri(elem, path, subject, predicate, multi=False, transform=None, thesaurus=None):
    """Extrait des IRI d'un XML et les renvoie sous forme de triples.
    
    Parameters
    ----------
    elem : xml.etree.ElementTree.Element
        Un élément XML présumé contenir l'information
        recherchée.
    path : str
        Le chemin de l'information recherchée dans le XML.
    subject : plume.rdf.utils.DatasetId or rdflib.term.BNode
        L'identifiant du graphe ou le noeud anonyme sujet
        des triples à renvoyer.
    predicate : rdflib.term.URIRef
        La propriété qui sera le prédicat des triples
        renvoyés.
    multi : bool, default False
        La propriété admet-elle plusieurs valeurs ? Si ``False``,
        la fonction s'arrête dès qu'une valeur a été trouvée,
        même si le XML en contenait plusieurs.
    transform : {None, 'email', 'phone'}, optional
        Le cas échéant, la nature de la transformation à
        appliquer aux objets des triples.
    thesaurus : tuple(rdflib.term.URIRef, tuple(str))
        Source de vocabulaire contrôlée pour les objets des triples.
        Il s'agit d'un tuple dont le premier élément est l'IRI de la
        source, le second un tuple de langues pour lequel le thésaurus
        doit être généré.
    
    Returns
    -------
    list of tuples
        Une liste de triples, ou une liste vide si le chemin cherché
        n'était pas présent dans le XML.
    
    """
    l = []
    for sub in elem.findall(path, namespaces=ISO_NS):
        value = sub.text
        if not value or forbidden_char(value):
            continue
        if transform == 'email':
            value = owlthing_from_email(value)
        elif transform == 'phone':
            value = owlthing_from_tel(value)
        elif thesaurus:
            value = Thesaurus.concept_iri(thesaurus, value)
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
    if not len(l) == 2 or not l[0] in ISO_NS:
        return tag
    return '{{{}}}{}'.format(ISO_NS[l[0]], l[1])    




