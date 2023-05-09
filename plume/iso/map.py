"""Mapping depuis ISO 19139 vers GeoDCAT-AP.

"""

import re
from json import load
import xml.etree.ElementTree as etree

from plume.rdf.utils import (
    DatasetId, abspath, forbidden_char,
    owlthing_from_email, owlthing_from_tel, CRS_NS,
    FRA_URI
)
from plume.rdf.namespaces import (
    DCAT, DCT, FOAF, RDF, RDFS, VCARD, XSD, GEODCAT, PLUME,
    ADMS, GSP
)
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

SUB_NS = {
    'http://librairies.ign.fr/geoportail/resources/IGNF.xml#': 'https://registre.ign.fr/ign/IGNF/crs/IGNF/',
    'http://registre.ign.fr/ign/IGNF/IGNF.xml#': 'https://registre.ign.fr/ign/IGNF/crs/IGNF/',
    'https://registre.ign.fr/ign/IGNF/IGNF.xml#': 'https://registre.ign.fr/ign/IGNF/crs/IGNF/',
    'http://registre.ign.fr/ign/IGNF/crs/IGNF/': 'https://registre.ign.fr/ign/IGNF/crs/IGNF/'
}
"""Substitution d'espaces de nommage.

Les clés sont les espaces de nommage à remplacer par leurs valeurs.

"""

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
    
    ISO639_LANGUAGE_CODES = None
    """dict: Mapping des codes de langue de trois caractères en codes à deux caractères.
    
    Répertoire des codes de langues utilisés par les métadonnées
    ISO 19139. Les clés sont les codes sur trois caractères des
    métadonnées ISO, les valeurs sont les codes sur deux caractères
    utilisés préférentiellement pour les valeurs litériales RDF.
    
    Ce dictionnaire est chargé si besoin à l'initialisation d'un nouvel
    objet, grâce à la méthode :py:meth:`IsoToDcat.load_language_codes`.
    
    """
 
    def __init__(self, raw_xml, datasetid=None):
        self.isoxml = parse_xml(raw_xml)
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
            cls.ISO639_LANGUAGE_CODES = load(src)
    
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
        if not code:
            return
        if code in ('fre', 'fra'):
            return 'fr'
        if not IsoToDcat.ISO639_LANGUAGE_CODES:
            IsoToDcat.load_language_codes()
        alpha2 = IsoToDcat.ISO639_LANGUAGE_CODES.get(code)
        # les métadonnées ISO utilise des codes de langue
        # sur trois caractères, RDF privilégie les codes
        # sur deux caractères. ISO639_LANGUAGE_CODES établit
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
    def map_language(self):
        """list of tuples: Triples contenant la ou les langues des données.
        
        Cette propriété est recalculée à chaque interrogation à partir
        du XML. Si l'information n'était pas disponible dans le XML,
        une liste vide est renvoyée.
        
        """
        return find_iri(
            self.isoxml,
            [
                './gmd:identificationInfo/gmd:MD_DataIdentification/'
                'gmd:language/gmd:LanguageCode@codeListValue',
                './gmd:identificationInfo/gmd:MD_DataIdentification/'
                'gmd:language/gmd:LanguageCode',
                './gmd:identificationInfo/gmd:MD_DataIdentification/'
                'gmd:language/gco:CharacterString'
            ],
            self.datasetid,
            DCT.language,
            transform=normalize_language,
            multi=True,
            thesaurus= (
                URIRef('http://publications.europa.eu/resource/authority/language'),
                (self.language,)
            )
        )
    
    @property
    def map_representation_type(self):
        """list of tuples: Triples contenant le mode de représentation géographique.
        
        Cette propriété est recalculée à chaque interrogation à partir
        du XML. Si l'information n'était pas disponible dans le XML,
        une liste vide est renvoyée.
        
        """
        return find_iri(
            self.isoxml,
            [
                './gmd:identificationInfo/gmd:MD_DataIdentification/'
                'gmd:spatialRepresentationType/'
                'gmd:MD_SpatialRepresentationTypeCode@codeListValue',
                './gmd:identificationInfo/gmd:MD_DataIdentification/'
                'gmd:spatialRepresentationType/gmd:MD_SpatialRepresentationTypeCode',
                './gmd:identificationInfo/gmd:MD_DataIdentification/'
                'gmd:spatialRepresentationType/gco:CharacterString'
            ],
            self.datasetid,
            ADMS.representationTechnique,
            thesaurus= (
                URIRef('http://inspire.ec.europa.eu/metadata-codelist/SpatialRepresentationType'),
                (self.language,)
            )
        )

    @property
    def map_epsg(self):
        """list of tuples: Triples contenant le ou les référentiels de coordonnées du jeu de données.
        
        Cette propriété est recalculée à chaque interrogation à partir
        du XML. Si l'information n'était pas disponible dans le XML,
        une liste vide est renvoyée.
        
        """
        return find_iri(
            self.isoxml,
            [
                './gmd:referenceSystemInfo/gmd:MD_ReferenceSystem/'
                'gmd:referenceSystemIdentifier/gmd:RS_Identifier/'
                'gmd:code/gmx:Anchor@xlink:href',
                './gmd:referenceSystemInfo/gmd:MD_ReferenceSystem/'
                'gmd:referenceSystemIdentifier/gmd:RS_Identifier/'
                'gmd:code/gmx:Anchor',
                './gmd:referenceSystemInfo/gmd:MD_ReferenceSystem/'
                'gmd:referenceSystemIdentifier/gmd:RS_Identifier/'
                'gmd:code/gco:CharacterString'
            ],
            self.datasetid,
            DCT.conformsTo,
            transform=normalize_crs,
            multi=True,
            thesaurus=[
                (PLUME.OgcEpsgFrance, (self.language,)),
                (URIRef('http://www.opengis.net/def/crs/EPSG/0'), (self.language,)),
                (URIRef('http://registre.data.developpement-durable.gouv.fr/plume/IgnCrs'), (self.language,))
            ]
        )

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

        vocabularies_ref = {
            URIRef('http://inspire.ec.europa.eu/theme'): ['INSPIRE themes'],
            URIRef('http://inspire.ec.europa.eu/metadata-codelist/SpatialScope'): ['INSPIRE Spatial Scope']
        }

        for elem in self.isoxml.findall('./gmd:identificationInfo/'
            'gmd:MD_DataIdentification/gmd:descriptiveKeywords/gmd:MD_Keywords',
            namespaces=ISO_NS):
            raw_vocabulary = find_value(
                elem,
                [
                    './gmd:thesaurusName/gmd:CI_Citation/'
                    'gmd:title/gmx:Anchor@xlink:href',
                    './gmd:thesaurusName/gmd:CI_Citation/'
                    'gmd:title/gmx:Anchor',
                    './gmd:thesaurusName/gmd:CI_Citation/'
                    'gmd:title/gco:CharacterString'
                ]
            )
            thesaurus = None
            if raw_vocabulary:
                for vocabulary in vocabularies_ref:
                    if (
                        raw_vocabulary == str(vocabulary) 
                        or any(x in raw_vocabulary for x in vocabularies_ref[vocabulary])
                    ):
                        thesaurus = (vocabulary, (self.language,))
                        break

            for subelem in elem.findall('.gmd:keyword',
                namespaces=ISO_NS):
                if thesaurus:
                    triples = find_iri(
                        subelem,
                        [
                            './gmx:Anchor@xlink:href',
                            './gmx:Anchor',
                            './gco:CharacterString'
                        ],
                        self.datasetid,
                        DCAT.theme,
                        thesaurus=thesaurus
                    )
                    if triples:
                        l += triples
                        continue
                keyword = subelem.findtext('./gco:CharacterString',
                    namespaces=ISO_NS)
                for k in keyword.split(','):
                    k = k.strip()
                    if k:
                        l.append((self.datasetid, DCAT.keyword,
                            Literal(k, lang=self.language)))
        return l

    @property
    def map_bbox(self):
        """list of tuples: Triples contenant l'emprise géographique.
        
        Cette propriété est recalculée à chaque interrogation à partir
        du XML. Si l'information n'était pas disponible dans le XML,
        une liste vide est renvoyée.
        
        """
        west = find_value(
            self.isoxml,
            './gmd:identificationInfo/gmd:MD_DataIdentification/'
            'gmd:extent/gmd:EX_Extent/'
            'gmd:geographicElement/gmd:EX_GeographicBoundingBox/'
            'gmd:westBoundLongitude/gco:Decimal'
        )
        east = find_value(
            self.isoxml,
            './gmd:identificationInfo/gmd:MD_DataIdentification/'
            'gmd:extent/gmd:EX_Extent/'
            'gmd:geographicElement/gmd:EX_GeographicBoundingBox/'
            'gmd:eastBoundLongitude/gco:Decimal'
        )
        south=find_value(
            self.isoxml,
            './gmd:identificationInfo/gmd:MD_DataIdentification/'
            'gmd:extent/gmd:EX_Extent/'
            'gmd:geographicElement/gmd:EX_GeographicBoundingBox/'
            'gmd:southBoundLatitude/gco:Decimal'
        )
        north=find_value(
            self.isoxml,
            './gmd:identificationInfo/gmd:MD_DataIdentification/'
            'gmd:extent/gmd:EX_Extent/'
            'gmd:geographicElement/gmd:EX_GeographicBoundingBox/'
            'gmd:northBoundLatitude/gco:Decimal'
        )
        if any(c is None for c in (west, east, south, north)):
            return []
        bbox = (
            'POLYGON(('
            f'{west} {north},'
            f'{west} {south},'
            f'{east} {south},'
            f'{east} {north},'
            f'{west} {north}))'
        )
        node = BNode()
        return [
            (self.datasetid, DCT.spatial, node),
            (node, DCT.type, DCT.Location),
            (node, DCAT.bbox, Literal(bbox, datatype=GSP.wktLiteral))
        ]

    @property
    def map_categories(self):
        """list of tuples: Triples contenant la ou les catégories ISO 19115.
        
        Cette propriété est recalculée à chaque interrogation à partir
        du XML. Si l'information n'était pas disponible dans le XML,
        une liste vide est renvoyée.
        
        """
        return find_iri(
            self.isoxml,
            [
                './gmd:identificationInfo/gmd:MD_DataIdentification/'
                'gmd:topicCategory/'
                'gmd:MD_TopicCategoryCode@codeListValue',
                './gmd:identificationInfo/gmd:MD_DataIdentification/'
                'gmd:topicCategory/gmd:MD_TopicCategoryCode',
                './gmd:identificationInfo/gmd:MD_DataIdentification/'
                'gmd:topicCategory/gco:CharacterString'
            ],
            self.datasetid,
            DCAT.theme,
            multi=True,
            thesaurus=(
                URIRef('http://inspire.ec.europa.eu/metadata-codelist/TopicCategory'),
                (self.language,)
            )
        )

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
                    transform=owlthing_from_email)
                triples += find_iri(elem, './gmd:CI_ResponsibleParty/'
                    'gmd:contactInfo/gmd:CI_Contact/'
                    'gmd:onlineResource/gmd:CI_OnlineResource/'
                    'gmd:linkage/gmd:URL', node, VCARD.hasURL)
                triples += find_iri(elem, './gmd:CI_ResponsibleParty/'
                    'gmd:contactInfo/gmd:CI_Contact/gmd:phone/'
                    'gmd:CI_Telephone/gmd:voice/gco:CharacterString',
                    node, VCARD.hasTelephone, transform=owlthing_from_tel)
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
                    transform=owlthing_from_email)
                triples += find_iri(elem, './gmd:CI_ResponsibleParty/'
                    'gmd:contactInfo/gmd:CI_Contact/'
                    'gmd:onlineResource/gmd:CI_OnlineResource/'
                    'gmd:linkage/gmd:URL', node, FOAF.workplaceHomepage)
                triples += find_iri(elem, './gmd:CI_ResponsibleParty/'
                    'gmd:contactInfo/gmd:CI_Contact/gmd:phone/'
                    'gmd:CI_Telephone/gmd:voice/gco:CharacterString',
                    node, FOAF.phone, transform=owlthing_from_tel)
                if triples:
                    triples.append((self.datasetid, predicate, node))
                    triples.append((node, RDF.type, FOAF.Agent))
                    l += triples
        return l

def find_values(
    elem, path, multi=True
):
    """Extrait des valeurs d'un XML.
    
    Parameters
    ----------
    elem : xml.etree.ElementTree.Element
        Un élément XML présumé contenir l'information
        recherchée.
    path : str or list(str)
        Le chemin de l'information recherchée dans le XML.
        Il est possible de fournir une liste de chemins, auquel
        cas la fonction s'appliquera successivement à tous les
        chemins listés. XPath n'est pas pris en charge, mais il est
        possible de viser la valeur d'un attribut en ajoutant son
        nom précédé de ``'@'`` à la fin du chemin.
    multi : bool, default True
        La propriété admet-elle plusieurs valeurs ? Si ``False``,
        la fonction s'arrête dès qu'une valeur a été trouvée,
        même si le XML en contenait plusieurs.
    
    Returns
    -------
    list
        Une liste de valeurs, ou une liste vide si le chemin cherché
        n'était pas présent dans le XML.
    
    """
    l = []
    if not path:
        return l
    
    if isinstance(path, list):
        epath = path[0]
    else:
        epath = path
    
    if '@' in epath:
        epath, attr = epath.split('@', 1)
    else:
        attr = None

    for sub in elem.findall(epath, namespaces=ISO_NS):
        value = sub.get(attr) if attr else sub.text
        if not value in (None, ''):
            l.append(value)
        if not multi:
            break
    
    if isinstance(path, list) and len(path) > 1 and (multi or not l):
        values = find_values(
            elem, path[1:], multi=multi
        )
        for value in values:
            if not value in l:
                l.append(value)

    return l

def find_value(
    elem, path
):
    """Extrait une valeur d'un XML.
    
    Parameters
    ----------
    elem : xml.etree.ElementTree.Element
        Un élément XML présumé contenir l'information
        recherchée.
    path : str or list(str)
        Le chemin de l'information recherchée dans le XML.
        Il est possible de fournir une liste de chemins, auquel
        cas la fonction s'appliquera successivement à tous les
        chemins listés. XPath n'est pas pris en charge, mais il est
        possible de viser la valeur d'un attribut en ajoutant son
        nom précédé de ``'@'`` à la fin du chemin.
    
    Returns
    -------
    str or None
        La valeur si elle existe.
    
    """
    values = find_values(elem=elem, path=path, multi=False)
    if values:
        return values[0]

def find_literal(
    elem, path, subject, predicate, multi=False, datatype=None, language=None
):
    """Extrait des valeurs litérales d'un XML et les renvoie sous forme de triples.
    
    Parameters
    ----------
    elem : xml.etree.ElementTree.Element
        Un élément XML présumé contenir l'information
        recherchée.
    path : str or list(str)
        Le chemin de l'information recherchée dans le XML.
        Il est possible de fournir une liste de chemins, auquel
        cas la fonction s'appliquera successivement à tous les
        chemins listés. XPath n'est pas pris en charge, mais il est
        possible de viser la valeur d'un attribut en ajoutant son
        nom précédé de ``'@'`` à la fin du chemin.
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
    if not path:
        return l
    
    if isinstance(path, list):
        epath = path[0]
    else:
        epath = path
    
    if '@' in epath:
        epath, attr = epath.split('@', 1)
    else:
        attr = None

    for sub in elem.findall(epath, namespaces=ISO_NS):
        value = sub.get(attr) if attr else sub.text
        if not value:
            continue
        if language:
            triple = (subject, predicate, Literal(value, lang=language))
            if not triple in l:
                l.append(triple)
        elif datatype and datatype != XSD.string:
            triple = (subject, predicate, Literal(value, datatype=datatype))
            if not triple in l:
                l.append(triple)
        else:
            triple = (subject, predicate, Literal(value))
            if not triple in l:
                l.append(triple)
        if not multi:
            break
    
    if isinstance(path, list) and len(path) > 1 and (multi or not l):
        triples = find_literal(
            elem, path[1:], subject, predicate, multi=multi,
            datatype=datatype, language=language
        )
        for triple in triples:
            if not triple in l:
                l.append(triple)

    return l

def find_iri(elem, path, subject, predicate, multi=False, transform=None, thesaurus=None):
    """Extrait des IRI d'un XML et les renvoie sous forme de triples.
    
    Parameters
    ----------
    elem : xml.etree.ElementTree.Element
        Un élément XML présumé contenir l'information
        recherchée.
    path : str or list(str)
        Le chemin de l'information recherchée dans le XML.
        Il est possible de fournir une liste de chemins, auquel
        cas la fonction s'appliquera successivement à tous les
        chemins listés. XPath n'est pas pris en charge, mais il est
        possible de viser la valeur d'un attribut en ajoutant son
        nom précédé de ``'@'`` à la fin du chemin.
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
    transform : function, optional
        Le cas échéant, une fonction de formatage à appliquer aux objets
        des triples. Elle doit prendre un unique argument, la valeur
        de l'objet, et renvoyer un URI.
    thesaurus : tuple(rdflib.term.URIRef, tuple(str))
        Source de vocabulaire contrôlée pour les objets des triples.
        Il s'agit d'un tuple dont le premier élément est l'IRI de la
        source, le second un tuple de langues pour lequel le thésaurus
        doit être généré.
        La fonction ne présume pas de la nature de la valeur recueillie
        dans le XML, elle lui cherchera une correspondance en tant qu'IRI et
        en tant qu'étiquette.
        Il est possible de fournir une liste de thésaurus. Dans ce cas,
        la fonction les parcourt tous jusqu'à trouver une correspondance.
    
    Returns
    -------
    list of tuples
        Une liste de triples, ou une liste vide si le chemin cherché
        n'était pas présent dans le XML ou pour une valeur issue de
        thésaurus non répertoriée.
    
    """
    l = []
    if not path:
        return l
    
    if isinstance(path, list):
        epath = path[0]
    else:
        epath = path
        
    if '@' in epath:
        epath, attr = epath.split('@', 1)
    else:
        attr = None
    
    if isinstance(thesaurus, list) or not thesaurus:
        l_thesaurus = thesaurus 
    else:
        l_thesaurus = [thesaurus]

    for sub in elem.findall(epath, namespaces=ISO_NS):
        value = sub.get(wns(attr)) if attr else sub.text
        if not value or (
            not thesaurus and forbidden_char(value)
        ):
            continue
        for old_ns, new_ns in SUB_NS.items():
            if value.startswith(old_ns):
                value = value.replace(old_ns, new_ns)
                break
        if transform:
            value = transform(value)
            if not value:
                continue
        if l_thesaurus:
            for s_thesaurus in l_thesaurus:

                # est-ce un IRI ?
                if not forbidden_char(value):
                    value_str = Thesaurus.concept_str(s_thesaurus, URIRef(value))
                    if value_str:
                        break
                
                # est-ce la partie identifiante d'un IRI ?
                if (
                    not any(c in value for c in ('/', '#', ':'))
                    and not forbidden_char(value)
                ):
                    value_iri = URIRef(
                        '{}/{}'.format(str(s_thesaurus[0].rstrip('/')), value)
                    )
                    value_str = Thesaurus.concept_str(s_thesaurus, value_iri)
                    if value_str:
                        value = value_iri
                        break
                
                # est-ce une étiquette ?
                value_iri = Thesaurus.concept_iri(s_thesaurus, value)
                if value_iri:
                    value = value_iri
                    break
            else:
                # non référencé
                continue
        triple = (subject, predicate, URIRef(value))
        if not triple in l:
            l.append(triple)
        if not multi:
            break
    
    if isinstance(path, list) and len(path) > 1 and (multi or not l):
        triples = find_iri(
            elem, path[1:], subject, predicate, multi=multi,
            transform=transform, thesaurus=thesaurus
        )
        for triple in triples:
            if not triple in l:
                l.append(triple)

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

def parse_xml(raw_xml):
    """Désérialise un XML contenant des métadonnées ISO 19115/19139.

    Parameters
    ----------
    raw_xml : str
        Un XML présumé contenir des métadonnées ISO 19115/19139,
        englobées ou non dans une réponse de CSW.
    
    Returns
    -------
    xml.etree.ElementTree.Element
        Si un élément ``gmd:MD_Metadata`` a été trouvé
        dans le XML, il est renvoyé. Sinon, la fonction 
        renvoie un élément ``gmd:MD_Metadata`` vide.

    """
    try:
        root = etree.fromstring(raw_xml)
        if root.tag == wns('gmd:MD_Metadata'):
            return root
        else:
            return root.find('./gmd:MD_Metadata', ISO_NS) \
                or etree.Element(wns('gmd:MD_Metadata'))
    except:
        return etree.Element(wns('gmd:MD_Metadata')) 

def normalize_crs(crs_str):
    """Recherche un code de référentiel de coordonnées dans une chaîne de caractères et le normalise.

    La fonction ne saura traiter que :

    * Les URI de codes EPSG.
    * Les valeurs numériques, qui sont alors présumées être des codes EPSG.
    * Un code inclut dans une chaîne de caractères, à condition qu'il soit précédé
      d'un code d'autorité connu. Par exemple ``'EPSG:'`` ou ``'EPSG '`` pour un
      code EPSG.

    Dans les autres cas, elle renvoie la chaîne de caractères fournie en entrée.

    La fonction produit des chaînes de caractères dont :py:func:`find_iri` se 
    chargera de faire des URI. C'est également elle qui devra vérifier que les 
    URI résultants sont effectivement référencés dans les vocabulaires de Plume,
    la présente fonction ne réalise aucun contrôle.

    Parameters
    ----------
    crs_str : str
        Chaîne de caractères présumée contenir un code de référentiel
        de coordonnées.

    Returns
    -------
    str or None
        ``None`` lorsque la fonction n'a pas renconnu de code.

    """
    if not crs_str:
        return crs_str
    if crs_str.isdigit():
        # on présume qu'il s'agit d'un code EPSG
        return CRS_NS['EPSG'] + crs_str
    if any(crs_str.startswith(ns) for ns in CRS_NS.values()):
        return crs_str
    for auth, ns in CRS_NS.items():
        r = re.search(rf'{auth}\s*:?:?\s*([a-zA-Z0-9]+(?:[.][a-zA-Z0-9]+)?)', crs_str)
        if r:
            return ns + r[1]
    return crs_str

def normalize_language(language_str):
    """Transforme un code de langue en URI.
    
    Pour l'heure, le traitement est très basique :

    * Si le code est ``'fr'``, ``'fre'`` ou ``'fra'``, la fonction
      renvoie l'URI correspondant au français dans le vocabulaire
      de la commission européenne.
    * Sinon, elle juxtapose le code à l'espace de nommage du
      vocabulaire des langues de la commission européenne.
    
    La fonction produit des chaînes de caractères dont :py:func:`find_iri` se 
    chargera de faire des URI. C'est également elle qui devra vérifier que les 
    URI résultants sont effectivement référencés dans les vocabulaires de Plume,
    la présente fonction ne réalise aucun contrôle.

    Parameters
    ----------
    language_str : str
        Chaîne de caractères présumée contenir un code de référentiel
        de coordonnées.

    Returns
    -------
    str or None
        ``None`` lorsque l'argument de la fonction n'était pas un code
        sur trois caractères ou un code sur deux caractères pouvant
        être retranscrit sur trois caractères.
    
    """
    if not language_str:
        return
    if language_str.lower() in ('fra', 'fre', 'fr'):
        return str(FRA_URI)
    if not re.match('^[a-zA-Z]{3}$', language_str):
        if re.match('^[a-zA-Z]{2}$', language_str):
            if not IsoToDcat.ISO639_LANGUAGE_CODES:
                IsoToDcat.load_language_codes()
            for alpha3, alpha2 in IsoToDcat.ISO639_LANGUAGE_CODES.items():
                if alpha2.lower() == language_str.lower():
                    language_str = alpha3
                    break
            else:
                return
        else:
            return
    return (
        'http://publications.europa.eu/resource/authority/language/'
        + language_str.upper()
    )

