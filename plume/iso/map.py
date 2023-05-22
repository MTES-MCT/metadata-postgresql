"""Mapping depuis ISO 19139 vers GeoDCAT-AP.

"""

import re
from json import load
import xml.etree.ElementTree as etree

from plume.rdf.utils import (
    DatasetId, abspath, forbidden_char,
    owlthing_from_email, owlthing_from_tel, CRS_NS,
    FRA_URI, all_words_included
)
from plume.rdf.namespaces import (
    DCAT, DCT, FOAF, RDF, RDFS, VCARD, XSD, GEODCAT, PLUME,
    ADMS, GSP, SKOS, OWL, DQV
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

DATE_TYPE_CODE_MAP = {
    'creation': DCT.created,
    'revision': DCT.modified,
    'publication': DCT.issued
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
    def map_crs(self):
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
        """list of tuples: Triples contenant les dates de référence du jeu de données.
        
        Cette propriété est recalculée à chaque interrogation à partir
        du XML. Si l'information n'était pas disponible dans le XML,
        une liste vide est renvoyée.
        
        """
        l = []
        for elem in self.isoxml.findall(
            './gmd:identificationInfo/gmd:MD_DataIdentification/'
            'gmd:citation/gmd:CI_Citation/'
            'gmd:date/gmd:CI_Date',
            namespaces=ISO_NS
        ):
            code = find_value(
                elem,
                [
                    './gmd:dateType/gmd:CI_DateTypeCode@codeListValue',
                    './gmd:dateType/gmd:CI_DateTypeCode'
                ]
            )
            if not code or not code in DATE_TYPE_CODE_MAP:
                continue
            l += find_literal(
                elem, 
                [
                    './gmd:date/gco:Date',
                    './gmd:date/gco:DateTime'
                ],
                self.datasetid,
                DATE_TYPE_CODE_MAP[code],
                datatype=XSD.date
            )
            # XSD.date est renseigné pour le type, mais find_literal
            # (grâce à date_or_datetime_to_literal) fera en sorte
            # que le type soit XSD.dateTime ou XSD.date selon le format
            # effectif de la date, même s'il était mal spécifié dans le XML.
        return l
    
    @property
    def map_temporal(self):
        """list of tuples: Triples contenant l'étendue temporelle du jeu de données.
        
        Cette propriété est recalculée à chaque interrogation à partir
        du XML. Si l'information n'était pas disponible dans le XML,
        une liste vide est renvoyée.
        
        """
        l = []
        for elem in self.isoxml.findall(
            './gmd:identificationInfo/gmd:MD_DataIdentification/'
            'gmd:extent/gmd:EX_Extent/'
            'gmd:temporalElement/gmd:EX_TemporalExtent/'
            'gmd:extent/gml:TimePeriod',
            namespaces=ISO_NS
        ):
            node = BNode()
            start_date = find_literal(
                elem, './gml:beginPosition', node,
                DCAT.startDate, datatype=XSD.date
            )
            end_date = find_literal(
                elem, './gml:endPosition', node,
                DCAT.endDate, datatype=XSD.date
            )
            if start_date or end_date:
                l += start_date + end_date + [
                    (self.datasetid, DCT.temporal, node),
                    (node, RDF.type, DCT.PeriodOfTime)
                ]
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
    def map_location(self):
        """list of tuples: Triples contenant l'emprise géographique.
        
        Cette propriété est recalculée à chaque interrogation à partir
        du XML. Si l'information n'était pas disponible dans le XML,
        une liste vide est renvoyée.
        
        """
        l = []
        for elem in self.isoxml.findall(
            './gmd:identificationInfo/gmd:MD_DataIdentification/'
            'gmd:extent/gmd:EX_Extent',
            namespaces=ISO_NS
        ):

            geo_label = find_value(
                elem, './gmd:description/gco:CharacterString'
            )
            num_id = 0
            num_geo = 0
            num_iri = 0
            first_node = BNode()

            for id_elem in elem.findall(
                './gmd:geographicElement/gmd:EX_GeographicDescription/'
                'gmd:geographicIdentifier/gmd:MD_Identifier',
                namespaces=ISO_NS
            ):
                geo_iris = find_iri(
                    id_elem,
                    [
                        './gmd:code/gmx:Anchor@xlink:href',
                        './gmd:code/gmx:Anchor',
                        './gmd:code/gco:CharacterString'
                    ],
                    self.datasetid,
                    DCT.spatial,
                    thesaurus=[
                        (URIRef('http://id.insee.fr/geo/departement'), (self.language,)),
                        (URIRef('http://id.insee.fr/geo/region'), (self.language,)),
                        (URIRef('http://registre.data.developpement-durable.gouv.fr/plume/EuAdministrativeTerritoryUnitFrance'), (self.language,)),
                        (URIRef('http://registre.data.developpement-durable.gouv.fr/plume/InseeIndividualTerritory'), (self.language,)),
                        (URIRef('http://publications.europa.eu/resource/authority/atu'), (self.language,)),
                        (URIRef('http://id.insee.fr/geo/commune'), (self.language,))
                    ]
                )
                if geo_iris:
                    l += geo_iris
                    num_iri += 1
                    continue

                node = first_node if num_id == 0 else BNode()
                code = find_literal(id_elem, './gmd:code/gco:CharacterString', node, DCT.identifier, datatype=XSD.string)
                if code:
                    scheme = find_iri(
                        id_elem,
                        './gmd:authority/gmd:CI_Citation/gmd:title/gco:CharacterString',
                        node,
                        SKOS.inScheme,
                        thesaurus=[
                            (PLUME.ISO3166CodesCollection, (self.language,)),
                            (PLUME.InseeGeoIndex, (self.language,))
                        ],
                        comparator=all_words_included
                    )
                    if code and scheme:
                        l.append((self.datasetid, DCT.spatial, node))
                        l += code + scheme
                        num_id += 1

            if num_iri == 1:
                # s'il y exactement un IRI, on considère que les autres
                # informations sont redondantes avec lui, sinon on les
                # garde
                continue

            for geo_elem in elem.findall(
                './gmd:geographicElement/gmd:EX_GeographicBoundingBox',
                namespaces=ISO_NS
            ):
                west = normalize_decimal(
                    find_value(
                        geo_elem,
                        './gmd:westBoundLongitude/gco:Decimal'
                    )
                )
                east = normalize_decimal(
                    find_value(
                        geo_elem,
                        './gmd:eastBoundLongitude/gco:Decimal'
                    )
                )
                south = normalize_decimal(
                    find_value(
                        geo_elem,
                        './gmd:southBoundLatitude/gco:Decimal'
                    )
                )
                north = normalize_decimal(
                    find_value(
                        geo_elem,
                        './gmd:northBoundLatitude/gco:Decimal'
                    )
                )
                if any(c is None for c in (west, east, south, north)):
                    continue
                bbox = (
                    'POLYGON(('
                    f'{west} {north},'
                    f'{west} {south},'
                    f'{east} {south},'
                    f'{east} {north},'
                    f'{west} {north}))'
                )
                node = first_node if num_geo == 0 else BNode()
                l.append((node, DCAT.bbox, Literal(bbox, datatype=GSP.wktLiteral)))
                if num_id == 0 or num_geo > 0:
                    l.append((node, DCT.type, DCT.Location))
                    l.append((self.datasetid, DCT.spatial, node))
                num_geo += 1

            if geo_label:
                if num_id + num_geo == 0:
                    l.append((first_node, DCT.type, DCT.Location))
                    l.append((self.datasetid, DCT.spatial, first_node))
                if num_id > 1 or num_geo > 1:
                    node = BNode()
                    l.append((node, DCT.type, DCT.Location))
                    l.append((self.datasetid, DCT.spatial, node))
                else:
                    node = first_node
                l.append(
                    (node, SKOS.prefLabel, Literal(geo_label, lang=self.language))
                )
        return l

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
        triples = find_literal(
            self.isoxml,
            './gmd:dataQualityInfo/gmd:DQ_DataQuality/'
            'gmd:lineage/gmd:LI_Lineage/'
            'gmd:statement/gco:CharacterString',
            None,
            RDFS.label,
            multi=True,
            language=self.language
        )
        if triples:
            for subject in list_subjects(triples):
                triples.append((self.datasetid, DCT.provenance, subject))
        return triples

    @property
    def map_conforms_to(self):
        """list of tuples: Triples contenant les informations sur la conformité des données.
        
        Cette propriété est recalculée à chaque interrogation à partir
        du XML. Si l'information n'était pas disponible dans le XML,
        une liste vide est renvoyée.

        La fonction ne contrôle pas le champ (scope) de la conformité -
        ``dataset``, ``series``, etc - l'information est considérée 
        comme valable pour le jeu de données dans tous les cas.

        Elle vérifie le résultat du test de conformité, conservant
        l'information si ``gmd:pass`` ne vaut pas ``false``. Ce choix,
        pragmatique et contestable, tient compte du fait que peu de
        jeux de données ont un résultat de conformité explicite.

        Les explications libres sur la conformité (``gmd:explanation``)
        ne sont pas retranscrites.

        """
        l = []
        for elem in self.isoxml.findall(
            './gmd:dataQualityInfo/gmd:DQ_DataQuality/'
            'gmd:report/gmd:DQ_DomainConsistency/'
            'gmd:result/gmd:DQ_ConformanceResult',
            namespaces=ISO_NS
        ):
            result = find_value(
                elem,
                './gmd:pass/gco:Boolean'
            )
            if result and result.lower() == 'false':
                continue

            for specification_elem in elem.findall(
                './gmd:specification/gmd:CI_Citation',
                namespaces=ISO_NS
            ):
                node = BNode()
                titles = find_literal(
                    specification_elem,
                    [
                        './gmd:title/gco:CharacterString',
                        './gmd:title/gmx:Anchor@xlink:title',
                        './gmd:title/gmx:Anchor'
                    ],
                    node,
                    DCT.title,
                    language=self.language
                )
                if not titles:
                    continue
                l += titles
                l.append((self.datasetid, DCT.conformsTo, node))

                l += find_iri(
                    specification_elem,
                    './gmd:title/gmx:Anchor@xlink:href',
                    node,
                    FOAF.page
                )

                for date_elem in specification_elem.findall(
                    './gmd:date/gmd:CI_Date',
                    namespaces=ISO_NS
                ):
                    code = find_value(
                        date_elem,
                        [
                            './gmd:dateType/gmd:CI_DateTypeCode@codeListValue',
                            './gmd:dateType/gmd:CI_DateTypeCode'
                        ]
                    )
                    if not code or not code in DATE_TYPE_CODE_MAP:
                        continue
                    l += find_literal(
                        date_elem, 
                        [
                            './gmd:date/gco:Date',
                            './gmd:date/gco:DateTime'
                        ],
                        node,
                        DATE_TYPE_CODE_MAP[code],
                        datatype=XSD.date
                    )
        return l

            
    @property
    def map_version(self):
        """list of tuples: Triples contenant la version du jeu de données.
        
        Cette propriété est recalculée à chaque interrogation à partir
        du XML. Si l'information n'était pas disponible dans le XML,
        une liste vide est renvoyée.
        
        """
        return find_literal(
            self.isoxml,
            './gmd:identificationInfo/gmd:MD_DataIdentification/'
            'gmd:citation/gmd:CI_Citation/'
            'gmd:edition/gco:CharacterString',
            self.datasetid,
            OWL.versionInfo
        )

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

    @property
    def map_spatial_resolution(self):
        """list of tuples: Triples contenant la résolution spatiale.

        Cette propriété est recalculée à chaque interrogation à partir
        du XML. Si l'information n'était pas disponible dans le XML,
        une liste vide est renvoyée.

        La résolution spatiale est représentée via la propriété
        ``dcat:spatialResolutionInMeters`` si elle est fournie
        sous la forme d'une distance (qui est alors convertie
        en mètres), via ``dqv:hasQualityMeasurement`` si elle
        est fournie sous la forme d'une échelle équivalente. À noter
        que les échelles équivalentes de GeoDCAT-AP sont exprimées
        par un nombre décimal, pas par le seul dénominateur de la
        fraction.

        Les intervalles d'échelles sont aussi imparfaitement pris
        en charge par Plume que dans les XML ISO : les deux
        valeurs apparaîtront sans être explicitement décrites
        comme un intervalle.

        Les distances sans unité sont présumées être en mètres.
        
        """
        l = []
        # échelle équivalente
        denominators = find_values(
            self.isoxml,
            './gmd:identificationInfo/gmd:MD_DataIdentification/'
            'gmd:spatialResolution/gmd:MD_Resolution/'
            'gmd:equivalentScale/gmd:MD_RepresentativeFraction/'
            'gmd:denominator/gco:Integer'
        )
        for denominator in denominators:
            scale = denominator_to_float(denominator)
            if not scale:
                continue
            node = BNode()
            l += [
                (self.datasetid, DQV.hasQualityMeasurement, node),
                (node, RDF.type, DQV.QualityMeasurement),
                (node, DQV.value, Literal(scale, datatype=XSD.decimal)),
                (node, DQV.isMeasurementOf, GEODCAT.spatialResolutionAsScale)
            ]
        # distance
        for elem in self.isoxml.findall(
            './gmd:identificationInfo/gmd:MD_DataIdentification/'
            'gmd:spatialResolution/gmd:MD_Resolution/'
            'gmd:distance/gco:Distance',
            namespaces=ISO_NS
        ):
            unit = elem.get('uom') or 'm'
            value = to_spatial_resolution_in_meters(elem.text, unit)
            if value:
                lit = Literal(value, datatype=XSD.decimal)
                if not lit.ill_typed:
                    l.append((self.datasetid, DCAT.spatialResolutionInMeters, lit))
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
    elem, path, subject, predicate, multi=False, datatype=None, language=None,
    transform=None
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
    subject : plume.rdf.utils.DatasetId or rdflib.term.BNode or None
        L'identifiant du graphe ou le noeud anonyme sujet
        des triplets à renvoyer. Si la valeur de ce paramètre est 
        explicitement fixée à ``None``, la fonction générera un 
        nouveau noeud anonyme pour chaque triplet renvoyé.
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
    transform : function, optional
        Le cas échéant, une fonction de formatage à appliquer aux objets
        des triples. Elle doit prendre un unique argument, la valeur
        de l'objet, et renvoyer soit une valeur qui pourra être convertie
        en instance de `rdflib.term.Literal`, soit ``None``.
    
    Returns
    -------
    list of tuples
        Une liste de triples, ou une liste vide si le chemin cherché
        n'était pas présent dans le XML.
    
    """
    l = []
    subject_ref = subject
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
        value = sub.get(wns(attr)) if attr else sub.text
        if not subject_ref:
            subject = BNode()
        if not value:
            continue
        if transform:
            value = transform(value)
            if not value:
                continue
        if language:
            triple = (subject, predicate, Literal(value, lang=language))
            if not triple[2] in list_objects(l):
                l.append(triple)
        elif datatype and datatype != XSD.string:
            if datatype in (XSD.date, XSD.dateTime):
                lit = date_or_datetime_to_literal(value)
            else:
                lit = Literal(value, datatype=datatype)
            if lit and not lit.ill_typed:
                triple = (subject, predicate, lit)
                if not triple[2] in list_objects(l):
                    l.append(triple)
        else:
            triple = (subject, predicate, Literal(value))
            if not triple[2] in list_objects(l):
                l.append(triple)
        if not multi:
            break
    
    if isinstance(path, list) and len(path) > 1 and (multi or not l):
        triples = find_literal(
            elem, path[1:], subject_ref, predicate, multi=multi,
            datatype=datatype, language=language
        )
        for triple in triples:
            if not triple[2] in list_objects(l):
                l.append(triple)

    return l

def find_iri(
    elem, path, subject, predicate, multi=False, transform=None, thesaurus=None,
    comparator=None
):
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
    subject : plume.rdf.utils.DatasetId or rdflib.term.BNode or None
        L'identifiant du graphe ou le noeud anonyme sujet
        des triplets à renvoyer. Si la valeur de ce paramètre est 
        explicitement fixée à ``None``, la fonction générera un 
        nouveau noeud anonyme pour chaque triplet renvoyé.
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
        de l'objet, et renvoyer soit une valeur qui pourra être convertie
        en instance de `rdflib.term.URIRef`, soit ``None``.
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
    comparator : function, optional
        Pour autoriser des correspondances approximatives sur les libellés,
        ce paramètre doit indiquer la fonction à utiliser.
        Cf. :py:meth:`Thesaurus.look_up_label` pour plus de précisions.
    
    Returns
    -------
    list of tuples
        Une liste de triples, ou une liste vide si le chemin cherché
        n'était pas présent dans le XML ou pour une valeur issue de
        thésaurus non répertoriée.
    
    """
    l = []
    subject_ref = subject
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
        if not subject_ref:
            subject = BNode()
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

                # est-ce une étiquette (comparaison approchée) ?
                if comparator:
                    value_iri = Thesaurus.look_up_label(
                        s_thesaurus, value, comparator=comparator
                    )
                    if value_iri:
                        value = value_iri
                        break
            else:
                # non référencé
                continue
        triple = (subject, predicate, URIRef(value))
        if not triple[2] in list_objects(l):
            l.append(triple)
        if not multi:
            break
    
    if isinstance(path, list) and len(path) > 1 and (multi or not l):
        triples = find_iri(
            elem, path[1:], subject_ref, predicate, multi=multi,
            transform=transform, thesaurus=thesaurus
        )
        for triple in triples:
            if not triple[2] in list_objects(l):
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

_DECIMAL_REGEXP = re.compile(r'^(\+|-)?([0-9]+(\.[0-9]*)?|\.[0-9]+)$')

def normalize_decimal(decimal_str):
    """Normalise une valeur décimale.
    
    La fonction s'assure notamment de l'absence de virgule.

    Parameters
    ----------
    language_str : str
        Chaîne de caractères présumée correspondre à un nombre décimal.
    
    Returns
    -------
    str or None
        ``None`` lorsque l'argument de la fonction n'a pas la forme d'un
        nombre décimal.
    
    """
    if decimal_str in (None, ''):
        return
    if '.' in decimal_str:
        decimal_str = decimal_str.replace(',', '')
    else:
        decimal_str = decimal_str.replace(',', '.')
    decimal_str = decimal_str.replace(' ', '')
    if re.match(_DECIMAL_REGEXP, decimal_str):
        return decimal_str

_DATE_REGEXP = re.compile(
        '^-?([1-9][0-9]{3,}|0[0-9]{3})'
        '-(0[1-9]|1[0-2])'
        '-(0[1-9]|[12][0-9]|3[01])'
        r'(Z|(\+|-)((0[0-9]|1[0-3]):[0-5][0-9]|14:00))?$'
    )
_DATETIME_REGEXP = re.compile(
        '^-?([1-9][0-9]{3,}|0[0-9]{3})'
        '-(0[1-9]|1[0-2])'
        '-(0[1-9]|[12][0-9]|3[01])'
        r'T(([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\.[0-9]+)?|(24:00:00(\.0+)?))'
        r'(Z|(\+|-)((0[0-9]|1[0-3]):[0-5][0-9]|14:00))?$'
    )

def to_spatial_resolution_in_meters(value, unit):
    """Convertit en mètres une résolution spatiale potentiellement exprimée dans une autre unité.

    Parameters
    ----------
    value : str
        Chaîne de caractères correspondant à une valeur décimale,
        représentant une échelle équivalente.
    
    Returns
    -------
    float

    """
    if not isinstance(value, (float, int)):
        value = normalize_decimal(value)
        if value is None:
            return
    value = float(value)
    factor = {
        'qm': 1e-30,
        'rm': 1e-27,
        'ym': 1e-24,
        'zm': 1e-21,
        'am': 1e-18,
        'fm': 1e-15,
        'pm': 1e-12,
        'nm': 1e-9,
        'µm': 1e-6,
        'dmm': 1e-4,
        'mm': 0.001,
        'cm': 0.01,
        'dm': 0.1,
        'm': 1,
        'dam': 10,
        'hm': 100,
        'km': 1000,
        'mam': 1e4,
        'Mm': 1e6,
        'Gm': 1e9,
        'Tm': 1e12,
        'Pm': 1e15,
        'Em': 1e18,
        'Zm': 1e21,
        'Ym': 1e24,
        'Rm': 1e27,
        'Qm': 1e30
    }
    if unit in factor:
        return value * factor[unit]
    
def date_or_datetime_to_literal(date_str):
    """Renvoie la représentation RDF d'une date, avec ou sans heure, exprimée comme chaîne de caractères.
    
    Cette fonction produira une valeur littérale de type
    ``xsd:date`` si la valeur fournie en argument était une date sans
    heure, ``xsd:dateTime`` s'il s'agissait d'une date avec heure.

    Parameters
    ----------
    date_str : str
        Représentation ISO d'une date, avec ou sans heure, avec 
        ou sans fuseau horaire.
    
    Returns
    -------
    rdflib.term.Literal
        Un littéral de type ``xsd:dateTime`` ou ``xsd:date``.
    
    Examples
    --------
    >>> date_or_datetime_to_literal('2022-02-13T15:30:14')
    rdflib.term.Literal('2022-02-13T15:30:14', datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#dateTime'))
    
    """
    if not date_str:
        return
    if re.match(_DATE_REGEXP, date_str):
        return Literal(date_str, datatype=XSD.date)
    if re.match(_DATETIME_REGEXP, date_str):
        return Literal(date_str, datatype=XSD.dateTime)

def denominator_to_float(denominator):
    """Renvoie le nombre décimal correspondant à la fraction dont le dénominateur est fourni en argument.

    Parameters
    ----------
    denominator : str or int or float
        Une valeur numérique. 0 ou toute autre
        valeur invalide sera silencieusement 
        éliminée, la fonction renvoyant alors ``None``.
    
    Returns
    -------
    float
    
    """
    denominator = normalize_decimal(denominator)
    if not denominator:
        return
    return 1 / float(denominator)

def list_objects(triples):
    """Renvoie la liste des objets d'une liste de triplets.
    
    Parameters
    ----------
    triples : list(tuple)
        Une liste de triplets.
    
    Returns
    -------
    list(rdflib.term.URIRef or rdflib.term.Literal or rdflib.term.BNode)

    """
    return [triple[2] for triple in triples or []]

def list_subjects(triples):
    """Renvoie la liste des sujets d'une liste de triplets.
    
    Parameters
    ----------
    triples : list(tuple)
        Une liste de triplets.
    
    Returns
    -------
    list(rdflib.term.URIRef or rdflib.term.Literal or rdflib.term.BNode)

    """
    return [triple[0] for triple in triples or []]
