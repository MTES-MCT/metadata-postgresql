"""Recette des modules widgetsdict et internal.

Les tests nécessitent une connexion PostgreSQL (paramètres à
saisir lors de l'exécution du test) pointant sur une base où 
l'extension plume_pg est installée. Il est préférable d'utiliser
un super-utilisateur.

"""

import unittest
import psycopg2
import re
from datetime import datetime, date

from plume.rdf.widgetsdict import WidgetsDict
from plume.rdf.namespaces import (
    DCAT, DCT, OWL, LOCAL, XSD, VCARD, FOAF, PLUME, LOCAL, RDF, RDFS
)
from plume.rdf.widgetkey import GroupOfPropertiesKey, ValueKey, GroupOfValuesKey
from plume.rdf.metagraph import Metagraph
from plume.rdf.rdflib import isomorphic, Literal, URIRef
from plume.rdf.exceptions import ForbiddenOperation, IntegrityBreach
from plume.rdf.labels import SourceLabels

from plume.pg.tests.connection import ConnectionString
from plume.pg.queries import query_get_categories, query_template_tabs, query_exists_extension
from plume.pg.template import TemplateDict, LocalTemplatesCollection
from plume.pg.computer import METHODS, ComputationMethod, default_parser

class WidgetsDictTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Création de la connexion et gestion de variables.
        
        """
        cls.grid = 6 # largeur de la grille
        cls.connection_string = ConnectionString()
    
    def test_widgetsdict_empty_edit(self):
        """Génération d'un dictionnaire de widgets sans graphe ni modèle.

        Ce premier test vérifie essentiellement
        que toutes les informations du dictionnaire
        interne sont correctement générées, dans le
        cas simple d'un dictionnaire en mode édition.
        
        """
        widgetsdict = WidgetsDict()
        self.assertIsNone(widgetsdict.check_grids())
        self.assertEqual(widgetsdict.main_language, 'fr')
        self.assertTrue(widgetsdict.edit)
        self.assertFalse(widgetsdict.translation)
        # groupe de valeurs
        key = widgetsdict.root.search_from_path(DCT.temporal)
        self.assertIsNotNone(key)
        d = {
            'label': 'Couverture temporelle',
            'main widget type': 'QGroupBox',
            'object': 'group of values',
            'help text': "Période·s décrite·s par le jeu de données. " \
                "La date de début et la date de fin peuvent être " \
                "confondues, par exemple dans le cas de l'extraction " \
                "ponctuelle d'une base mise à jour au fil de l'eau."
            }
        for k, v in d.items():
            with self.subTest(internalkey = k):
                self.assertEqual(widgetsdict[key][k], v)
        for k, v in widgetsdict[key].items():
            with self.subTest(internalkey = k):
                if not k in d:
                    self.assertFalse(v)
        # boutton plus
        button = key.button
        d = {
            'main widget type': 'QToolButton',
            'object': 'plus button',
            'help text': 'Ajouter un élément « Couverture temporelle ».'
            }
        for k, v in d.items():
            with self.subTest(internalkey = k):
                self.assertEqual(widgetsdict[button][k], v)
        for k, v in widgetsdict[button].items():
            with self.subTest(internalkey = k):
                if not k in d:
                    self.assertFalse(v)
        # groupe de propriétés
        key = key.children[0]
        d = {
            'main widget type': 'QGroupBox',
            'object': 'group of properties',
            'has minus button': True,
            'hide minus button': True,
            'help text': "Période·s décrite·s par le jeu de données. " \
                "La date de début et la date de fin peuvent être " \
                "confondues, par exemple dans le cas de l'extraction " \
                "ponctuelle d'une base mise à jour au fil de l'eau."
            }
        for k, v in d.items():
            with self.subTest(internalkey = k):
                self.assertEqual(widgetsdict[key][k], v)
        for k, v in widgetsdict[key].items():
            with self.subTest(internalkey = k):
                if not k in d:
                    self.assertFalse(v)
        # widget de saisie (date)
        key = widgetsdict.root.search_from_path(DCT.temporal / DCAT.startDate)
        self.assertIsNotNone(key)
        d = {
            'label': 'Date de début',
            'has label': True,
            'help text': 'Date de début de la période.',
            'main widget type': 'QDateEdit',
            'object': 'edit',
            'input mask': '9999-99-99',
            'regex validator pattern': '^[0-9]{4}[-][0-9]{2}[-][0-9]{2}$'
            }
        for k, v in d.items():
            with self.subTest(internalkey = k):
                self.assertEqual(widgetsdict[key][k], v)
        for k, v in widgetsdict[key].items():
            with self.subTest(internalkey = k):
                if not k in d:
                    self.assertFalse(v)
        # widget de saisie avec sources
        l = widgetsdict.root.search_from_path(DCT.accessRights).children
        for c in l:
            if isinstance(c, GroupOfPropertiesKey):
                mkey = c
            else:
                key = c
        d = {
            'main widget type': 'QComboBox',
            'object': 'edit',
            'help text': "Contraintes réglementaires limitant l'accès aux données.",
            'multiple sources': True,
            'sources': [
                '< manuel >',
                "Restriction d'accès public (INSPIRE)",
                "Droits d'accès (UE)",
                "Restrictions d'accès en application du Code des relations entre le public et l'administration",
                'Restriction de sécurité sur les données (ISO 19115/19139)',
                "Limitation d'accès ou d'usage des données (ISO 19115/19139)"
                ],
            'current source': "Restriction d'accès public (INSPIRE)",
            'has minus button': True,
            'hide minus button': True
            }
        for k, v in d.items():
            with self.subTest(internalkey = k):
                self.assertEqual(widgetsdict[key][k], v)
        for k, v in widgetsdict[key].items():
            with self.subTest(internalkey = k):
                if not k in d and not k == 'thesaurus values':
                    self.assertFalse(v)
        self.assertTrue("Accès public restreint en application de l'article 13(1)(h) de la " \
            "Directive INSPIRE (protection de l'environnement auquel ces informations ont trait)"
            in widgetsdict[key]['thesaurus values'])
        d = {
            'main widget type': 'QGroupBox',
            'object': 'group of properties',
            'help text': "Contraintes réglementaires limitant l'accès aux données.",
            'multiple sources': True,
            'sources': [
                '< manuel >',
                "Restriction d'accès public (INSPIRE)",
                "Droits d'accès (UE)",
                "Restrictions d'accès en application du Code des relations entre le public et l'administration",
                'Restriction de sécurité sur les données (ISO 19115/19139)',
                "Limitation d'accès ou d'usage des données (ISO 19115/19139)"
                ],
            'current source': '< manuel >',
            'hidden': True,
            'has minus button': True,
            'hide minus button': True
            }
        for k, v in d.items():
            with self.subTest(internalkey = k):
                self.assertEqual(widgetsdict[mkey][k], v)
        for k, v in widgetsdict[mkey].items():
            with self.subTest(internalkey = k):
                if not k in d:
                    self.assertFalse(v)
        # widget de saisie avec une seule source
        key = widgetsdict.root.search_from_path(DCT.language).children[0]
        d = {
            'main widget type': 'QComboBox',
            'help text': "Langue·s des données.",
            'has label': False,
            'has minus button': True,
            'hide minus button': True,
            'object': 'edit',
            }
        for k, v in d.items():
            with self.subTest(internalkey = k):
                self.assertEqual(widgetsdict[key][k], v)
        for k, v in widgetsdict[key].items():
            with self.subTest(internalkey = k):
                if not k in d and not k == 'thesaurus values':
                    self.assertFalse(v)
        self.assertTrue("islandais"
            in widgetsdict[key]['thesaurus values'])
        self.assertTrue('' in widgetsdict[key]['thesaurus values'])
        # widget de saisie avec unités
        key = widgetsdict.root.search_from_path(DCAT.temporalResolution)
        d = {
            'main widget type': 'QLineEdit',
            'label': 'Résolution temporelle',
            'has label': True,
            'help text': 'Plus petit pas de temps significatif dans le contexte du jeu de données.',
            'object': 'edit',
            'type validator': 'QIntValidator',
            'units': ['ans', 'mois', 'jours', 'heures', 'min.', 'sec.'],
            'current unit': 'ans'
            }
        for k, v in d.items():
            with self.subTest(internalkey = k):
                self.assertEqual(widgetsdict[key][k], v)
        for k, v in widgetsdict[key].items():
            with self.subTest(internalkey = k):
                if not k in d:
                    self.assertFalse(v)
        # widget de saisie avec aide à la saisie des géométries
        # (catégorie appartenant à un bloc masqué par défaut)
        key = widgetsdict.root.search_from_path(DCT.spatial / DCAT.bbox)
        d = {
            'main widget type': 'QTextEdit',
            'label': "Rectangle d'emprise",
            'has label': True,
            'hidden': True,
            'help text': "Rectangle d'emprise (BBox), au format textuel WKT.",
            'object': 'edit',
            'geo tools': ['show', 'bbox', 'rectangle'],
            'placeholder text': '<http://www.opengis.net/def/crs/EPSG/0/2154> ' \
                'POLYGON((646417.3289 6857521.1356, 657175.3272 6857521.1356, ' \
                '657175.3272 6867076.0360, 646417.3289 6867076.0360, ' \
                '646417.3289 6857521.1356))'
            }
        for k, v in d.items():
            with self.subTest(internalkey = k):
                self.assertEqual(widgetsdict[key][k], v)
        for k, v in widgetsdict[key].items():
            with self.subTest(internalkey = k):
                if not k in d:
                    self.assertFalse(v)
        # simple URL
        key = widgetsdict.root.search_from_path(FOAF.page).children[0]
        d = {
            'main widget type': 'QLineEdit',
            'help text': "URL d'accès à une documentation rédigée décrivant la donnée.",
            'object': 'edit',
            'regex validator pattern': r'^[^<>"\s{}|\\^`]*$',
            'has minus button': True,
            'hide minus button': True
            }
        for k, v in d.items():
            with self.subTest(internalkey = k):
                self.assertEqual(widgetsdict[key][k], v)
        for k, v in widgetsdict[key].items():
            with self.subTest(internalkey = k):
                if not k in d:
                    self.assertFalse(v) 
    
    def test_widgetsdict_empty_translation(self):
        """Génération d'un dictionnaire de widgets sans graphe ni modèle, en mode traduction.

        Ce test vérifie que toutes les informations du
        dictionnaire interne sont correctement générées,
        dans le cas d'un dictionnaire en mode traduction.

        Il fait aussi quelques contrôles sur la gestion
        des attributs :py:attr:`WidgetsDict.main_language` et
        :py:attr:`WidgetsDict.langList`.
        
        """
        widgetsdict = WidgetsDict(translation = True,
            langList = ['en', 'fr'], language = 'it')
        self.assertIsNone(widgetsdict.check_grids())
        self.assertEqual(widgetsdict.main_language, 'en')
        self.assertEqual(widgetsdict.langlist, ('en', 'fr'))
        widgetsdict = WidgetsDict(translation = True,
            langList = ['en', 'fr', 'it'], language = 'it')
        self.assertEqual(widgetsdict.main_language, 'it')
        self.assertEqual(widgetsdict.langlist, ('it', 'en', 'fr'))
        self.assertTrue(widgetsdict.edit)
        self.assertTrue(widgetsdict.translation)
        # groupe de traduction
        key = widgetsdict.root.search_from_path(DCT.title)
        self.assertIsNotNone(key)
        d = {
            'label': 'Libellé',
            'help text': 'Nom explicite du jeu de données.',
            'main widget type': 'QGroupBox',
            'object': 'translation group'
            }
        for k, v in d.items():
            with self.subTest(internalkey = k):
                self.assertEqual(widgetsdict[key][k], v)
        for k, v in widgetsdict[key].items():
            with self.subTest(internalkey = k):
                if not k in d:
                    self.assertFalse(v)
        # boutton de traduction
        button = key.button
        d = {
            'main widget type': 'QToolButton',
            'object': 'translation button',
            'help text': 'Ajouter une traduction.'
            }
        for k, v in d.items():
            with self.subTest(internalkey = k):
                self.assertEqual(widgetsdict[button][k], v)
        for k, v in widgetsdict[button].items():
            with self.subTest(internalkey = k):
                if not k in d:
                    self.assertFalse(v)
        # widget de saisie dans un groupe de traduction
        key = key.children[0]
        d = {
            'main widget type': 'QLineEdit',
            'object': 'edit',
            'help text': 'Nom explicite du jeu de données.',
            'authorized languages': ['it', 'en', 'fr'],
            'language value': 'it',
            'has minus button': True,
            'hide minus button': True,
            'is mandatory': True
            }
        for k, v in d.items():
            with self.subTest(internalkey = k):
                self.assertEqual(widgetsdict[key][k], v)
        for k, v in widgetsdict[key].items():
            with self.subTest(internalkey = k):
                if not k in d:
                    self.assertFalse(v)
        # widget de saisie avec traduction hors groupe de traduction
        key = widgetsdict.root.search_from_path(DCAT.keyword).children[0]
        d = {
            'main widget type': 'QLineEdit',
            'object': 'edit',
            'authorized languages': ['it', 'en', 'fr'],
            'language value': 'it',
            'has minus button': True,
            'hide minus button': True
            }

    def test_widgetsdict_read(self):
        """Génération d'un dictionnaire de widgets en mode lecture.

        Ce test vérifie que toutes les informations du
        dictionnaire interne sont correctement générées
        dans le cas d'un dictionnaire en mode lecture.
        Il s'assure également que les clés supposées
        être affichées le sont et que celles qui sont
        supposées être gardées en mémoire le sont
        également.

        Le test utilise le modèle pré-configuré
        "Basique", qui est importé puis supprimé de la
        table des modèles du serveur PostgreSQL au cours
        de l'exécution (de même que les autres modèles
        pré-configurés).
        
        """
        metadata = """
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix gsp: <http://www.opengis.net/ont/geosparql#> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix uuid: <urn:uuid:> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

            uuid:479fd670-32c5-4ade-a26d-0268b0ce5046 a dcat:Dataset ;
                dct:accessRights [ a dct:RightsStatement ;
                    rdfs:label "Aucune restriction d'accès ou d'usage."@fr ] ;
                dct:description "Some stuff in english."@en ;
                dct:title "ADMIN EXPRESS - Départements de métropole"@fr ;
                dcat:keyword "admin express"@fr,
                    "donnée externe"@fr,
                    "external data"@en,
                    "ign"@fr ;
                dct:temporal [ a dct:PeriodOfTime ;
                    dcat:endDate "2021-01-15"^^xsd:date ;
                    dcat:startDate "2021-01-15"^^xsd:date ] ;
                dcat:temporalResolution "PT10M"^^xsd:duration ;
                dct:spatial [ a dct:Location ;
                    dcat:bbox "<http://www.opengis.net/def/crs/EPSG/0/2154> POLYGON((646417.3289 6857521.1356, 657175.3272 6857521.1356, 657175.3272 6867076.0360, 646417.3289 6867076.0360, 646417.3289 6857521.1356))"^^gsp:wktLiteral ] ;
                dcat:theme <http://inspire.ec.europa.eu/theme/au> ;
                uuid:218c1245-6ba7-4163-841e-476e0d5582af "À mettre à jour !"@fr .
            """
        metagraph = Metagraph().parse(data=metadata)
        conn = psycopg2.connect(WidgetsDictTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM z_plume.meta_import_sample_template()')
                cur.execute(
                    *query_get_categories('Basique')
                    )
                categories = cur.fetchall()
                cur.execute(
                    *query_template_tabs('Basique')
                    )
                tabs = cur.fetchall()
                cur.execute('DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg')
        conn.close()
        template = TemplateDict(categories, tabs)
        
        # cohérence mode/translation
        widgetsdict = WidgetsDict(mode = 'read', translation = True)
        self.assertFalse(widgetsdict.translation)
        self.assertEqual(widgetsdict.mode, 'read')
        self.assertFalse(widgetsdict.edit)
        
        # --- sans graphe, sans modèle ---
        widgetsdict = WidgetsDict(mode = 'read')
        self.assertIsNone(widgetsdict.check_grids())
        self.assertEqual(widgetsdict.mode, 'read')
        self.assertFalse(widgetsdict.edit)
        self.assertTrue(widgetsdict.root in widgetsdict)
        self.assertEqual(len(widgetsdict), 1)
        # NB: le dictionnaire ne contient que la clé racine.
        
        # --- avec graphe, sans modèle ---
        widgetsdict = WidgetsDict(mode = 'read', metagraph=metagraph)
        self.assertIsNone(widgetsdict.check_grids())
        key = widgetsdict.root.search_from_path(DCT.description)
        self.assertTrue(key in widgetsdict)
        key = widgetsdict.root.search_from_path(DCAT.keyword)
        self.assertTrue(key in widgetsdict)
        self.assertIsNone(key.button)
        key = key.children[0]
        self.assertEqual(widgetsdict[key]['value'], 'admin express')
        self.assertFalse(widgetsdict[key]['has minus button'])
        key = widgetsdict.root.search_from_path(DCAT.keyword)
        key = key.children[3]
        self.assertEqual(key.value, Literal('external data', lang='en'))
        self.assertTrue(not key in widgetsdict)
        key = widgetsdict.root.search_from_path(DCAT.theme)
        self.assertFalse(widgetsdict[key]['multiple sources'])
        self.assertEqual(widgetsdict[key]['value'],
            '<a href="http://inspire.ec.europa.eu/theme/au">Unités administratives</a>')
        key = widgetsdict.root.search_from_path(DCAT.temporalResolution)
        self.assertFalse(widgetsdict[key]['units'])
        self.assertEqual(widgetsdict[key]['value'], '10 min.')
        key = widgetsdict.root.search_from_path(DCT.accessRights)
        self.assertFalse(widgetsdict[key]['multiple sources'])
        self.assertIsNone(key.m_twin)
        key = widgetsdict.root.search_from_path(OWL.versionInfo)
        self.assertIsNone(key)
        key = widgetsdict.root.search_from_path(DCT.spatial / DCAT.bbox)
        self.assertListEqual(widgetsdict[key]['geo tools'], ['show'])
        self.assertTrue(isomorphic(metagraph,
            widgetsdict.build_metagraph(preserve_metadata_date=True)))

        # --- avec graphe non inclus dans le modèle ---
        widgetsdict = WidgetsDict(mode = 'read', metagraph=metagraph,
            template=template)
        self.assertIsNone(widgetsdict.check_grids())
        with self.assertRaises(IntegrityBreach):
            key = widgetsdict.root.search_tab('Autres')
        for child in widgetsdict.root.children:
            if child.label == 'Autres':
                key = child
        self.assertIsNotNone(key)
        self.assertTrue(key.is_ghost)
        self.assertFalse(key in widgetsdict)
        self.assertTrue(key.children)
        self.assertFalse(key.has_real_children)
        key = widgetsdict.root.search_from_path(DCT.temporal)
        self.assertTrue(isinstance(key, GroupOfPropertiesKey))
        # pas de groupe de valeurs, puisqu'il n'y a qu'un objet
        key = widgetsdict.root.search_from_path(DCT.temporal / DCAT.startDate)
        self.assertEqual(widgetsdict[key]['value'], '15/01/2021')
        self.assertFalse(widgetsdict[key]['has minus button'])
        self.assertTrue(widgetsdict[key]['read only'])
        key = widgetsdict.root.search_from_path(OWL.versionInfo)
        self.assertIsNone(key)
        self.assertTrue(isomorphic(metagraph,
            widgetsdict.build_metagraph(preserve_metadata_date=True)))
        
        # --- avec un modèle vide ---
        template = TemplateDict([])
        widgetsdict = WidgetsDict(mode = 'read', metagraph=metagraph,
            template=template)
        self.assertIsNone(widgetsdict.check_grids())
        self.assertEqual(len(widgetsdict), 4)
        # racine + onglet + titre + description
        key = widgetsdict.root.search_tab()
        self.assertEqual(widgetsdict[key]['label'], 'Autres')
        widgetsdict[key]['grid widget'] = '<Grid onglet "Autres">'
        key = widgetsdict.root.search_from_path(DCT.title)
        self.assertEqual(widgetsdict.parent_grid(key), '<Grid onglet "Autres">')
        self.assertTrue(widgetsdict[key]['read only'])
        key = widgetsdict.root.search_from_path(DCT.description)
        self.assertEqual(widgetsdict.parent_grid(key), '<Grid onglet "Autres">')
        self.assertTrue(isomorphic(metagraph,
            widgetsdict.build_metagraph(preserve_metadata_date=True)))
    
    def test_widgetsdict_special_hidden_keys(self):
        """Génération d'un dictionnaire de widgets avec paramètres masquant certaines informations.

        Ce test contrôle l'effet des paramètres ``readHideBlank``,
        ``editHideUnlisted``, ``readHideUnlisted``,
        ``editOnlyCurrentLanguage`` et ``readOnlyCurrentLanguage``
        de :py:class:`plume.rdf.widgetsdict.WidgetsDict`.
        
        """
        metadata = """
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix uuid: <urn:uuid:> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

            uuid:479fd670-32c5-4ade-a26d-0268b0ce5046 a dcat:Dataset ;
                dct:accessRights [ a dct:RightsStatement ;
                    rdfs:label "Aucune restriction d'accès ou d'usage."@fr ] ;
                dct:title "ADMIN EXPRESS - Départements de métropole"@fr,
                    "ADMIN EXPRESS - Metropolitan Departments"@en;
                dcat:keyword "admin express"@fr,
                    "donnée externe"@fr,
                    "external data"@en,
                    "ign"@fr ;
                dct:temporal [ a dct:PeriodOfTime ;
                    dcat:endDate "2021-01-15"^^xsd:date ;
                    dcat:startDate "2021-01-15"^^xsd:date ] ;
                dcat:theme <http://inspire.ec.europa.eu/theme/au> ;
                dct:identifier "479fd670-32c5-4ade-a26d-0268b0ce5046" ;
                uuid:218c1245-6ba7-4163-841e-476e0d5582af "À mettre à jour !"@fr .
            """
        metagraph = Metagraph().parse(data=metadata)
        conn = psycopg2.connect(WidgetsDictTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM z_plume.meta_import_sample_template()')
                cur.execute(
                    *query_get_categories('Basique')
                    )
                categories = cur.fetchall()
                cur.execute(
                    *query_template_tabs('Basique')
                    )
                tabs = cur.fetchall()
                cur.execute('DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg')
        conn.close()
        template = TemplateDict(categories, tabs)
        
        # --- editHideUnlisted ---
        widgetsdict = WidgetsDict(metagraph=metagraph, template=template,
            editHideUnlisted=True)
        self.assertIsNone(widgetsdict.check_grids())
        for key in widgetsdict.keys():
            self.assertNotEqual(key.path, DCAT.keyword)
        key = widgetsdict.root.search_from_path(DCT.temporal)
        self.assertTrue(key in widgetsdict)
        key = widgetsdict.root.search_from_path(OWL.versionInfo)
        self.assertTrue(key in widgetsdict)
        self.assertTrue(isomorphic(metagraph,
            widgetsdict.build_metagraph(preserve_metadata_date=True)))
        
        # --- editHideUnlisted sans modèle ---
        widgetsdict = WidgetsDict(metagraph=metagraph, editHideUnlisted=True)
        self.assertIsNone(widgetsdict.check_grids())
        key = widgetsdict.root.search_from_path(DCAT.keyword)
        self.assertTrue(key in widgetsdict)
        key = widgetsdict.root.search_from_path(LOCAL['218c1245-6ba7-4163-841e-476e0d5582af'])
        self.assertIsNone(key)
        self.assertTrue(isomorphic(metagraph,
            widgetsdict.build_metagraph(preserve_metadata_date=True)))
        
        # --- editHideUnlisted avec un modèle vide ---
        widgetsdict = WidgetsDict(metagraph=metagraph, template=TemplateDict([]),
            editHideUnlisted=True)
        self.assertIsNone(widgetsdict.check_grids())
        self.assertEqual(len(widgetsdict), 6)
        key = widgetsdict.root.search_tab()
        self.assertEqual(widgetsdict[key]['label'], 'Autres')
        widgetsdict[key]['grid widget'] = '<Grid onglet "Autres">'
        key = widgetsdict.root.search_from_path(DCT.title)
        self.assertEqual(widgetsdict.parent_grid(key), '<Grid onglet "Autres">')
        key = widgetsdict.root.search_from_path(DCT.description)
        self.assertEqual(widgetsdict.parent_grid(key), '<Grid onglet "Autres">')
        self.assertTrue(isomorphic(metagraph,
            widgetsdict.build_metagraph(preserve_metadata_date=True)))
        
        # --- editOnlyCurrentLanguage ---
        widgetsdict = WidgetsDict(metagraph=metagraph, language='it',
            langList=['fr', 'it', 'en'])
        self.assertIsNone(widgetsdict.check_grids())
        key = widgetsdict.root.search_from_path(DCT.title)
        self.assertEqual(len(key.children), 2)
        for child in key.children:
            self.assertTrue(child in widgetsdict)
        self.assertIsNone(key.button)
        key = widgetsdict.root.search_from_path(DCAT.keyword)
        self.assertEqual(len(key.children), 4)
        for child in key.children:
            self.assertTrue(child in widgetsdict)
        self.assertTrue(isomorphic(metagraph,
            widgetsdict.build_metagraph(preserve_metadata_date=True)))
        
        widgetsdict = WidgetsDict(metagraph=metagraph,
            editOnlyCurrentLanguage=True, language='it',
            langList=['fr', 'it', 'en'])
        self.assertIsNone(widgetsdict.check_grids())
        self.assertTrue(widgetsdict.onlyCurrentLanguage)
        key = widgetsdict.root.search_from_path(DCAT.keyword)
        n = 0
        for child in key.children:
            if child in widgetsdict:
                n += 1
        self.assertEqual(n, 1)
        key = widgetsdict.root.search_from_path(DCT.title)
        self.assertTrue(key in widgetsdict)
        self.assertEqual(len(key.children), 2)
        self.assertTrue(key.children[1].is_ghost)
        self.assertTrue(widgetsdict[key.children[0]]['value'],
            'ADMIN EXPRESS - Départements de métropole')
        self.assertTrue(isomorphic(metagraph,
            widgetsdict.build_metagraph(preserve_metadata_date=True)))
        
        widgetsdict = WidgetsDict(metagraph=metagraph,
            editOnlyCurrentLanguage=True, language='en')
        self.assertIsNone(widgetsdict.check_grids())
        key = widgetsdict.root.search_from_path(DCT.title)
        self.assertTrue(key in widgetsdict)
        self.assertEqual(len(key.children), 2)
        self.assertTrue(key.children[1].is_ghost)
        self.assertTrue(widgetsdict[key.children[0]]['value'],
            'ADMIN EXPRESS - Metropolitan Departments')
        self.assertTrue(isomorphic(metagraph,
            widgetsdict.build_metagraph(preserve_metadata_date=True)))
        
        # --- readHideBlank ---
        widgetsdict = WidgetsDict(metagraph=metagraph, template=template,
            mode='read', readHideBlank=False)
        self.assertIsNone(widgetsdict.check_grids())
        key = widgetsdict.root.search_from_path(OWL.versionInfo)
        self.assertTrue(key in widgetsdict)
        self.assertTrue(isomorphic(metagraph,
            widgetsdict.build_metagraph(preserve_metadata_date=True)))
        
        widgetsdict = WidgetsDict(metagraph=metagraph, mode='read',
            readHideBlank=False)
        self.assertIsNone(widgetsdict.check_grids())
        key = widgetsdict.root.search_from_path(DCAT.distribution / DCT.license)
        self.assertTrue(key in widgetsdict)
        self.assertTrue(isomorphic(metagraph,
            widgetsdict.build_metagraph(preserve_metadata_date=True)))
        
        # --- readHideUnlisted ---
        widgetsdict = WidgetsDict(metagraph=metagraph, mode='read')
        self.assertIsNone(widgetsdict.check_grids())
        self.assertTrue(widgetsdict.hideUnlisted)
        key = widgetsdict.root.search_from_path(LOCAL['218c1245-6ba7-4163-841e-476e0d5582af'])
        self.assertIsNone(key)
        
        widgetsdict = WidgetsDict(metagraph=metagraph, mode='read',
            readHideUnlisted=False)
        self.assertIsNone(widgetsdict.check_grids())
        self.assertFalse(widgetsdict.hideUnlisted)
        key = widgetsdict.root.search_from_path(LOCAL['218c1245-6ba7-4163-841e-476e0d5582af'])
        self.assertTrue(key in widgetsdict)
        
        widgetsdict = WidgetsDict(metagraph=metagraph, template=template,
            mode='read', readHideUnlisted=False)
        self.assertIsNone(widgetsdict.check_grids())
        self.assertFalse(widgetsdict.hideUnlisted)
        key = widgetsdict.root.search_from_path(LOCAL['218c1245-6ba7-4163-841e-476e0d5582af'])
        self.assertTrue(key in widgetsdict)
        self.assertTrue(isomorphic(metagraph,
            widgetsdict.build_metagraph(preserve_metadata_date=True)))
        
        widgetsdict = WidgetsDict(metagraph=metagraph, template=template,
            mode='read', readHideUnlisted=False, readHideBlank=False)
        self.assertIsNone(widgetsdict.check_grids())
        key = widgetsdict.root.search_from_path(DCAT.distribution / DCT.license)
        self.assertIsNone(key)
        # readHideBlank permet d'afficher des champs vides, mais pas ceux
        # hors modèle, même combiné avec readHideUnlisted (sinon à quoi
        # bon utiliser un modèle ?)
        self.assertTrue(isomorphic(metagraph,
            widgetsdict.build_metagraph(preserve_metadata_date=True)))
        
        # --- readOnlyCurrentLanguage ---
        widgetsdict = WidgetsDict(metagraph=metagraph, mode='read')
        self.assertIsNone(widgetsdict.check_grids())
        self.assertTrue(widgetsdict.onlyCurrentLanguage)
        key = widgetsdict.root.search_from_path(DCT.title)
        self.assertEqual(len(key.children), 2)
        self.assertTrue(key.children[0] in widgetsdict)
        self.assertTrue(key.children[1].is_ghost)
        
        widgetsdict = WidgetsDict(metagraph=metagraph, mode='read',
            readOnlyCurrentLanguage=False)
        self.assertIsNone(widgetsdict.check_grids())
        self.assertFalse(widgetsdict.onlyCurrentLanguage)
        key = widgetsdict.root.search_from_path(DCT.title)
        self.assertEqual(len(key.children), 2)
        self.assertTrue(key.children[0] in widgetsdict)
        self.assertTrue(key.children[1] in widgetsdict)
        key = widgetsdict.root.search_from_path(DCAT.keyword)
        self.assertEqual(len(key.children), 4)
        for child in key.children:
            self.assertTrue(child in widgetsdict)
        self.assertTrue(isomorphic(metagraph,
            widgetsdict.build_metagraph(preserve_metadata_date=True)))
        
    def test_add(self):
        """Ajout d'une clé dans le dictionnaire.

        """
        metadata = """
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix uuid: <urn:uuid:> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

            uuid:479fd670-32c5-4ade-a26d-0268b0ce5046 a dcat:Dataset ;
                dct:accessRights [ a dct:RightsStatement ;
                    rdfs:label "Aucune restriction d'accès ou d'usage."@fr ] ;
                dct:title "ADMIN EXPRESS - Départements de métropole"@fr,
                    "ADMIN EXPRESS - Metropolitan Departments"@en;
                dcat:keyword "admin express"@fr,
                    "donnée externe"@fr,
                    "external data"@en,
                    "ign"@fr ;
                dct:temporal [ a dct:PeriodOfTime ;
                    dcat:endDate "2021-01-15"^^xsd:date ;
                    dcat:startDate "2021-01-15"^^xsd:date ] ;
                dcat:theme <http://inspire.ec.europa.eu/theme/au> ;
                dct:identifier "479fd670-32c5-4ade-a26d-0268b0ce5046" ;
                uuid:218c1245-6ba7-4163-841e-476e0d5582af "À mettre à jour !"@fr .
            """
        metagraph = Metagraph().parse(data=metadata)
        conn = psycopg2.connect(WidgetsDictTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM z_plume.meta_import_sample_template()')
                cur.execute(
                    *query_get_categories('Basique')
                    )
                categories = cur.fetchall()
                cur.execute(
                    *query_template_tabs('Basique')
                    )
                tabs = cur.fetchall()
                cur.execute('DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg')
        conn.close()
        template = TemplateDict(categories, tabs)
        widgetsdict = WidgetsDict(metagraph=metagraph, template=template)
        self.assertIsNone(widgetsdict.check_grids())

        # --- ajout d'un simple widget de saisie ---
        g = widgetsdict.root.search_from_path(DCAT.keyword)
        widgetsdict[g]['grid widget'] = '<QGridLayout dcat:keyword>'
        widgetsdict[g.button]['main widget'] = '<QToolButton dcat:keyword>'
        self.assertEqual(len(g.children), 4)
        actionsdict = widgetsdict.add(g.button)
        self.assertEqual(len(g.children), 5)
        for child in g.children:
            self.assertTrue(child in widgetsdict)
            self.assertTrue(widgetsdict[child]['has minus button'])
            self.assertFalse(widgetsdict[child]['hide minus button'])
        self.assertTrue(g.children[4] in actionsdict['new keys'])
        self.assertEqual(widgetsdict.widget_placement(g.children[4], 'main widget'),
            (4, 0, 1, WidgetsDictTestCase.grid - 1))
        self.assertEqual(widgetsdict.widget_placement(g.children[4], 'minus widget'),
            (4, WidgetsDictTestCase.grid - 1, 1, 1))
        self.assertEqual(actionsdict['widgets to move'], [('<QGridLayout dcat:keyword>',
            '<QToolButton dcat:keyword>', 5, 0, 1, 1)])

        # --- ajout d'un groupe de propriétés ---
        g = widgetsdict.root.search_from_path(DCT.temporal)
        widgetsdict[g]['grid widget'] = '<QGridLayout dct:temporal>'
        widgetsdict[g.button]['main widget'] = '<QToolButton dct:temporal>'
        self.assertEqual(len(g.children), 1)
        self.assertTrue(widgetsdict[g.children[0]]['has minus button'])
        self.assertTrue(widgetsdict[g.children[0]]['hide minus button'])
        actionsdict = widgetsdict.add(g.button)
        self.assertEqual(len(g.children), 2)
        for child in g.children:
            self.assertTrue(child in widgetsdict)
            self.assertEqual(len(child.children), 2)
            self.assertTrue(widgetsdict[child]['has minus button'])
            self.assertFalse(widgetsdict[child]['hide minus button'])
            for grandchild in child.children:
                self.assertTrue(grandchild in widgetsdict)
        self.assertEqual(len(actionsdict['new keys']), 3)
        self.assertTrue(g.children[1] in actionsdict['new keys'])
        self.assertEqual(widgetsdict.widget_placement(g.children[1], 'main widget'),
            (1, 0, 1, WidgetsDictTestCase.grid - 1))
        self.assertEqual(widgetsdict.widget_placement(g.children[1], 'minus widget'),
            (1, WidgetsDictTestCase.grid - 1, 1, 1))
        self.assertTrue(g.children[1].children[0] in actionsdict['new keys'])
        self.assertTrue(g.children[1].children[1] in actionsdict['new keys'])
        self.assertEqual(actionsdict['widgets to move'], [('<QGridLayout dct:temporal>',
            '<QToolButton dct:temporal>', 2, 0, 1, 1)])

        # --- ajout d'un couple de jumelles ---
        g = widgetsdict.root.search_from_path(DCT.accessRights)
        widgetsdict[g]['grid widget'] = '<QGridLayout dct:accessRights>'
        widgetsdict[g.button]['main widget'] = '<QToolButton dct:accessRights>'
        self.assertEqual(len(g.children), 2)
        actionsdict = widgetsdict.add(g.button)
        self.assertEqual(len(g.children), 4)
        self.assertEqual(g.children[2].m_twin, g.children[3])
        self.assertTrue(widgetsdict[g.children[3]]['hidden'])
        self.assertFalse(widgetsdict[g.children[2]]['hidden'])
        self.assertEqual(widgetsdict[g.children[2]]['object'], 'group of properties')
        
        # --- contrôle final de la cohérence du placement ---
        self.assertIsNone(widgetsdict.check_grids())

    def test_drop(self):
        """Suppression d'une clé du dictionnaire.

        """
        metadata = """
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix gsp: <http://www.opengis.net/ont/geosparql#> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix uuid: <urn:uuid:> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

            uuid:479fd670-32c5-4ade-a26d-0268b0ce5046 a dcat:Dataset ;
                dct:accessRights [ a dct:RightsStatement ;
                    rdfs:label "Aucune restriction d'accès ou d'usage."@fr ] ;
                dct:title "ADMIN EXPRESS - Départements de métropole"@fr,
                    "ADMIN EXPRESS - Metropolitan Departments"@en;
                dcat:keyword "admin express"@fr,
                    "donnée externe"@fr,
                    "external data"@en,
                    "ign"@fr ;
                dct:temporal [ a dct:PeriodOfTime ;
                    dcat:endDate "2021-01-15"^^xsd:date ;
                    dcat:startDate "2021-01-15"^^xsd:date ] ;
                dcat:theme <http://inspire.ec.europa.eu/theme/au> ;
                dct:identifier "479fd670-32c5-4ade-a26d-0268b0ce5046" ;
                dcat:temporalResolution "P1M"^^xsd:duration,
                    "PT12H"^^xsd:duration ;
                dct:spatial [ a dct:Location ;
                    dcat:bbox "<http://www.opengis.net/def/crs/EPSG/0/2154> POLYGON((646417.3289 6857521.1356, 657175.3272 6857521.1356, 657175.3272 6867076.0360, 646417.3289 6867076.0360, 646417.3289 6857521.1356))"^^gsp:wktLiteral,
                        "<http://www.opengis.net/def/crs/EPSG/0/2154> POLYGON((646416.3289 6857521.1356, 657175.3272 6857521.1356, 657175.3272 6867076.0360, 646417.3289 6867076.0360, 646417.3289 6857521.1356))"^^gsp:wktLiteral ] ;
                uuid:218c1245-6ba7-4163-841e-476e0d5582af "À mettre à jour !"@fr .
            """
        metagraph = Metagraph().parse(data=metadata)
        conn = psycopg2.connect(WidgetsDictTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM z_plume.meta_import_sample_template()')
                cur.execute(
                    *query_get_categories('Basique')
                    )
                categories = cur.fetchall()
                cur.execute(
                    *query_template_tabs('Basique')
                    )
                tabs = cur.fetchall()
                cur.execute('DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg')
        conn.close()
        template = TemplateDict(categories, tabs)
        widgetsdict = WidgetsDict(metagraph=metagraph, template=template)
        self.assertIsNone(widgetsdict.check_grids())

        # --- suppression d'une clé simple ---
        g = widgetsdict.root.search_from_path(DCAT.keyword)
        b = g.children[1]
        widgetsdict[g]['grid widget'] = '<QGridLayout dcat:keyword>'
        widgetsdict[b]['main widget'] = '<B QLineEdit dcat:keyword>'
        widgetsdict[b]['minus widget'] = '<B-minus QToolButton dcat:keyword>'
        c = g.children[2]
        widgetsdict[c]['main widget'] = '<C QLineEdit dcat:keyword>'
        widgetsdict[c]['minus widget'] = '<C-minus QToolButton dcat:keyword>'
        widgetsdict[g.button]['main widget'] = '<P QToolButton dcat:keyword>'
        self.assertEqual(len(g.children), 4)
        self.assertTrue(widgetsdict.widget_placement(b, 'main widget'),
            (1, 0, 1, WidgetsDictTestCase.grid - 1))
        actionsdict = widgetsdict.drop(b)
        self.assertEqual(len(g.children), 3)
        self.assertFalse(b in widgetsdict)
        self.assertEqual(actionsdict['widgets to delete'],
            ['<B QLineEdit dcat:keyword>', '<B-minus QToolButton dcat:keyword>'])
        self.assertEqual(actionsdict['widgets to move'],
            [('<QGridLayout dcat:keyword>', '<C QLineEdit dcat:keyword>',
                1, 0, 1, WidgetsDictTestCase.grid - 1),
             ('<QGridLayout dcat:keyword>', '<C-minus QToolButton dcat:keyword>',
                1, WidgetsDictTestCase.grid - 1, 1, 1),
             ('<QGridLayout dcat:keyword>', '<P QToolButton dcat:keyword>',
                3, 0, 1, 1)])
        actionsdict = widgetsdict.drop(g.children[0])
        actionsdict = widgetsdict.drop(g.children[1])
        self.assertEqual(len(g.children), 1)
        self.assertEqual(actionsdict['widgets to hide'], ['<C-minus QToolButton dcat:keyword>'])
        self.assertEqual(actionsdict['widgets to move'],
            [('<QGridLayout dcat:keyword>', '<P QToolButton dcat:keyword>',
                1, 0, 1, 1)])
        for k in actionsdict.keys():
            if not k in ('widgets to hide', 'widgets to delete', 'widgets to move'):
                self.assertFalse(actionsdict[k])

        # --- suppression d'une clé avec widget de sélection de l'unité ---
        # vérifie aussi la suppression de valeurs multiples non autorisées
        g = widgetsdict.root.search_from_path(DCAT.temporalResolution)
        b = g.children[0]
        c = g.children[1]
        widgetsdict[g]['grid widget'] = '<QGridLayout dcat:temporalResolution>'
        widgetsdict[b]['main widget'] = '<B QLineEdit dcat:temporalResolution>'
        widgetsdict[b]['minus widget'] = '<B-minus QToolButton dcat:temporalResolution>'
        widgetsdict[b]['unit widget'] = '<B-unit QToolButton dcat:temporalResolution>'
        widgetsdict[b]['unit menu'] = '<B-unit QMenu dcat:temporalResolution>'
        widgetsdict[b]['unit actions'] = ['<B-unit QAction n°1>', '<B-unit QAction n°2>']
        widgetsdict[c]['main widget'] = '<C QLineEdit dcat:temporalResolution>'
        widgetsdict[c]['minus widget'] = '<C-minus QToolButton dcat:temporalResolution>'
        widgetsdict[c]['unit widget'] = '<C-unit QToolButton dcat:temporalResolution>'
        widgetsdict[c]['unit menu'] = '<C-unit QMenu dcat:temporalResolution>'
        widgetsdict[c]['unit actions'] = ['<C-unit QAction n°1>', '<C-unit QAction n°2>']
        actionsdict = widgetsdict.drop(b)
        self.assertEqual(len(g.children), 1)
        self.assertFalse(b in widgetsdict)
        self.assertListEqual(actionsdict['widgets to hide'], ['<C-minus QToolButton dcat:temporalResolution>'])
        self.assertListEqual(actionsdict['widgets to delete'],
            ['<B QLineEdit dcat:temporalResolution>', '<B-minus QToolButton dcat:temporalResolution>',
             '<B-unit QToolButton dcat:temporalResolution>'])
        self.assertListEqual(actionsdict['widgets to move'],
            [('<QGridLayout dcat:temporalResolution>', '<C QLineEdit dcat:temporalResolution>',
                0, 0, 1, WidgetsDictTestCase.grid - 3),
             ('<QGridLayout dcat:temporalResolution>', '<C-minus QToolButton dcat:temporalResolution>',
                0, WidgetsDictTestCase.grid - 1, 1, 1),
             ('<QGridLayout dcat:temporalResolution>', '<C-unit QToolButton dcat:temporalResolution>',
                0, WidgetsDictTestCase.grid - 3, 1, 2)])
        self.assertListEqual(actionsdict['actions to delete'], ['<B-unit QAction n°1>', '<B-unit QAction n°2>'])
        self.assertListEqual(actionsdict['menus to delete'], ['<B-unit QMenu dcat:temporalResolution>'])
        for k in actionsdict.keys():
            if not k in ('widgets to hide', 'widgets to delete', 'widgets to move', 'actions to delete',
                'menus to delete'):
                self.assertFalse(actionsdict[k])

        # --- suppression d'une clé avec aide à la saisie des géométries ---
        g = widgetsdict.root.search_from_path(DCT.spatial / DCAT.bbox)
        b = g.children[0]
        c = g.children[1]
        widgetsdict[g]['grid widget'] = '<QGridLayout dcat:bbox>'
        widgetsdict[b]['main widget'] = '<B QLineEdit dcat:bbox>'
        widgetsdict[b]['minus widget'] = '<B-minus QToolButton dcat:bbox>'
        widgetsdict[b]['geo widget'] = '<B-geo QToolButton dcat:bbox>'
        widgetsdict[b]['geo menu'] = '<B-geo QMenu dcat:bbox>'
        widgetsdict[b]['geo actions'] = ['<B-geo QAction n°1>', '<B-geo QAction n°2>']
        widgetsdict[c]['main widget'] = '<C QLineEdit dcat:bbox>'
        widgetsdict[c]['minus widget'] = '<C-minus QToolButton dcat:bbox>'
        widgetsdict[c]['geo widget'] = '<C-geo QToolButton dcat:bbox>'
        widgetsdict[c]['geo menu'] = '<C-geo QMenu dcat:bbox>'
        widgetsdict[c]['geo actions'] = ['<C-geo QAction n°1>', '<C-geo QAction n°2>']
        actionsdict = widgetsdict.drop(b)
        self.assertEqual(len(g.children), 1)
        self.assertFalse(b in widgetsdict)
        self.assertListEqual(actionsdict['widgets to hide'], ['<C-minus QToolButton dcat:bbox>'])
        self.assertListEqual(actionsdict['widgets to delete'],
            ['<B QLineEdit dcat:bbox>', '<B-minus QToolButton dcat:bbox>',
             '<B-geo QToolButton dcat:bbox>'])
        self.assertListEqual(actionsdict['widgets to move'],
            [('<QGridLayout dcat:bbox>', '<C QLineEdit dcat:bbox>',
                0, 0, widgetsdict.textEditRowSpan, WidgetsDictTestCase.grid - 2),
             ('<QGridLayout dcat:bbox>', '<C-minus QToolButton dcat:bbox>',
                0, WidgetsDictTestCase.grid - 1, 1, 1),
             ('<QGridLayout dcat:bbox>', '<C-geo QToolButton dcat:bbox>',
                0, WidgetsDictTestCase.grid - 2, 1, 1)])
        self.assertListEqual(actionsdict['actions to delete'], ['<B-geo QAction n°1>', '<B-geo QAction n°2>'])
        self.assertListEqual(actionsdict['menus to delete'], ['<B-geo QMenu dcat:bbox>'])
        for k in actionsdict.keys():
            if not k in ('widgets to hide', 'widgets to delete', 'widgets to move', 'actions to delete',
                'menus to delete'):
                self.assertFalse(actionsdict[k])
        
        # --- suppression d'un groupe de propriétés ---
        g = widgetsdict.root.search_from_path(DCT.temporal)
        widgetsdict.add(g.button)
        b = g.children[0]
        c = g.children[1]
        widgetsdict[g]['grid widget'] = '<QGridLayout dct:temporal>'
        widgetsdict[g.button]['main widget'] = '<P QToolButton dct:temporal>'
        widgetsdict[b]['main widget'] = '<B QGroupBox dct:temporal>'
        widgetsdict[b]['minus widget'] = '<B-minus QToolButton dct:temporal>'
        widgetsdict[b.children[0]]['main widget'] = '<B QLineEdit dcat:startDate>'
        widgetsdict[b.children[1]]['main widget'] = '<B QLineEdit dcat:endDate>'
        widgetsdict[b]['grid widget'] = '<B QGridLayout dct:temporal>'
        widgetsdict[c]['main widget'] = '<C QGroupBox dct:temporal>'
        widgetsdict[c]['minus widget'] = '<C-minus QToolButton dct:temporal>'
        widgetsdict[c.children[0]]['main widget'] = '<C QLineEdit dcat:startDate>'
        widgetsdict[c.children[1]]['main widget'] = '<C QLineEdit dcat:endDate>'
        widgetsdict[c]['grid widget'] = '<C QGridLayout dct:temporal>'
        actionsdict = widgetsdict.drop(b)
        self.assertEqual(len(g.children), 1)
        self.assertFalse(b in widgetsdict)
        self.assertFalse(b.children[0] in widgetsdict)
        self.assertFalse(b.children[1] in widgetsdict)
        self.assertTrue(widgetsdict[c]['hide minus button'])
        self.assertListEqual(actionsdict['widgets to hide'], ['<C-minus QToolButton dct:temporal>'])
        self.assertListEqual(actionsdict['widgets to delete'],
            ['<B QGroupBox dct:temporal>', '<B-minus QToolButton dct:temporal>',
             '<B QLineEdit dcat:startDate>', '<B QLineEdit dcat:endDate>'])
        self.assertListEqual(actionsdict['grids to delete'], ['<B QGridLayout dct:temporal>'])
        self.assertListEqual(actionsdict['widgets to move'],
            [('<QGridLayout dct:temporal>', '<C QGroupBox dct:temporal>',
                0, 0, 1, WidgetsDictTestCase.grid - 1),
             ('<QGridLayout dct:temporal>', '<C-minus QToolButton dct:temporal>',
                0, WidgetsDictTestCase.grid - 1, 1, 1),
             ('<QGridLayout dct:temporal>', '<P QToolButton dct:temporal>',
                1, 0, 1, 1)])
        for k in actionsdict.keys():
            if not k in ('widgets to hide', 'widgets to delete', 'widgets to move',
                'grids to delete'):
                self.assertFalse(actionsdict[k])

        # --- suppression des clés jumelles ---
        g = widgetsdict.root.search_from_path(DCT.accessRights)
        widgetsdict.add(g.button)
        b1 = g.children[0]
        b2 = g.children[1]
        c1 = g.children[2]
        c2 = g.children[3]
        widgetsdict[g]['grid widget'] = '<QGridLayout dct:accessRights>'
        widgetsdict[g.button]['main widget'] = '<P QToolButton dct:accessRights>'
        widgetsdict[b1]['main widget'] = '<B1 QGroupBox dct:accessRights>'
        widgetsdict[b1]['minus widget'] = '<B1-minus QToolButton dct:accessRights>'
        widgetsdict[b1]['switch source widget'] = '<B1-source QToolButton dct:accessRights>'
        widgetsdict[b1]['switch source menu'] = '<B1-source QMenu dct:accessRights>'
        widgetsdict[b1]['switch source actions'] = ['<B1-source QAction n°1', '<B1-source QAction n°2']
        widgetsdict[b1.children[0]]['main widget'] = '<B1 QGroupBox rdfs:label>'
        widgetsdict[b2]['main widget'] = '<B2 QComboBox dct:accessRights>'
        widgetsdict[b2]['minus widget'] = '<B2-minus QToolButton dct:accessRights>'
        widgetsdict[b2]['switch source widget'] = '<B2-source QToolButton dct:accessRights>'
        widgetsdict[b2]['switch source menu'] = '<B2-source QMenu dct:accessRights>'
        widgetsdict[b2]['switch source actions'] = ['<B2-source QAction n°1', '<B2-source QAction n°2']
        widgetsdict[c1]['main widget'] = '<C1 QGroupBox dct:accessRights>'
        widgetsdict[c1]['minus widget'] = '<C1-minus QToolButton dct:accessRights>'
        widgetsdict[c1]['switch source widget'] = '<C1-source QToolButton dct:accessRights>'
        widgetsdict[c1]['switch source menu'] = '<C1-source QMenu dct:accessRights>'
        widgetsdict[c1]['switch source actions'] = ['<C1-source QAction n°1', '<C1-source QAction n°2']
        widgetsdict[c1.children[0]]['main widget'] = '<C1 QGroupBox rdfs:label>'
        widgetsdict[c2]['main widget'] = '<C2 QComboBox dct:accessRights>'
        widgetsdict[c2]['minus widget'] = '<C2-minus QToolButton dct:accessRights>'
        widgetsdict[c2]['switch source widget'] = '<C2-source QToolButton dct:accessRights>'
        widgetsdict[c2]['switch source menu'] = '<C2-source QMenu dct:accessRights>'
        widgetsdict[c2]['switch source actions'] = ['<C2-source QAction n°1', '<C2-source QAction n°2']
        actionsdict = widgetsdict.drop(b1)
        self.assertEqual(actionsdict['widgets to hide'], ['<C1-minus QToolButton dct:accessRights>'])
        self.assertEqual(actionsdict['widgets to delete'],
            ['<B1 QGroupBox dct:accessRights>', '<B1-minus QToolButton dct:accessRights>',
             '<B1-source QToolButton dct:accessRights>', '<B1 QGroupBox rdfs:label>',
             '<B2 QComboBox dct:accessRights>', '<B2-minus QToolButton dct:accessRights>',
             '<B2-source QToolButton dct:accessRights>'])
        self.assertEqual(actionsdict['widgets to move'],
            [('<QGridLayout dct:accessRights>', '<C1 QGroupBox dct:accessRights>',
                0, 0, 1, WidgetsDictTestCase.grid - 2),
             ('<QGridLayout dct:accessRights>', '<C1-minus QToolButton dct:accessRights>',
                0, WidgetsDictTestCase.grid - 1, 1, 1),
             ('<QGridLayout dct:accessRights>', '<C1-source QToolButton dct:accessRights>',
                0, WidgetsDictTestCase.grid - 2, 1, 1),
             ('<QGridLayout dct:accessRights>', '<C2 QComboBox dct:accessRights>',
                0, 0, 1, WidgetsDictTestCase.grid - 2),
             ('<QGridLayout dct:accessRights>', '<C2-minus QToolButton dct:accessRights>',
                0, WidgetsDictTestCase.grid - 1, 1, 1),
             ('<QGridLayout dct:accessRights>', '<C2-source QToolButton dct:accessRights>',
                0, WidgetsDictTestCase.grid - 2, 1, 1),
             ('<QGridLayout dct:accessRights>', '<P QToolButton dct:accessRights>',
                1, 0, 1, 1)])
        self.assertEqual(actionsdict['actions to delete'], ['<B1-source QAction n°1',
            '<B1-source QAction n°2', '<B2-source QAction n°1', '<B2-source QAction n°2'])
        self.assertEqual(actionsdict['menus to delete'], ['<B1-source QMenu dct:accessRights>',
            '<B2-source QMenu dct:accessRights>'])
        for k in actionsdict.keys():
            if not k in ('widgets to hide', 'widgets to delete', 'widgets to move', 'actions to delete',
                'menus to delete'):
                self.assertFalse(actionsdict[k])
        
        # --- contrôle final de la cohérence du placement ---
        self.assertIsNone(widgetsdict.check_grids())

    def test_change_unit(self):
        """Changement d'unité déclarée pour une clé du dictionnaire.
        
        """
        metadata = """
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix uuid: <urn:uuid:> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

            uuid:479fd670-32c5-4ade-a26d-0268b0ce5046 a dcat:Dataset ;
                dct:title "ADMIN EXPRESS - Départements de métropole"@fr ;
                dcat:temporalResolution "P1M"^^xsd:duration ;
                dct:identifier "479fd670-32c5-4ade-a26d-0268b0ce5046" .
            """
        metagraph = Metagraph().parse(data=metadata)
        widgetsdict = WidgetsDict(metagraph=metagraph)
        self.assertIsNone(widgetsdict.check_grids())
        b = widgetsdict.root.search_from_path(DCAT.temporalResolution)
        widgetsdict[b.parent]['grid widget'] = '<QGridLayout dcat:temporalResolution>'
        widgetsdict[b]['main widget'] = '<B QLineEdit dcat:temporalResolution>'
        widgetsdict[b]['minus widget'] = '<B-minus QToolButton dcat:temporalResolution>'
        widgetsdict[b]['unit widget'] = '<B-unit QToolButton dcat:temporalResolution>'
        widgetsdict[b]['unit menu'] = '<B-unit QMenu dcat:temporalResolution>'
        widgetsdict[b]['unit actions'] = ['<B-unit QAction n°1>', '<B-unit QAction n°2>']
        self.assertEqual(widgetsdict[b]['current unit'], 'mois')
        self.assertListEqual(widgetsdict[b]['units'], ['ans', 'mois', 'jours', 'heures', 'min.', 'sec.'])
        actionsdict = widgetsdict.change_unit(b, 'jours')
        self.assertListEqual(actionsdict['unit menu to update'], [b])
        self.assertEqual(widgetsdict[b]['current unit'], 'jours')
        self.assertListEqual(widgetsdict[b]['units'], ['ans', 'mois', 'jours', 'heures', 'min.', 'sec.'])
        for k in actionsdict.keys():
            if not k == 'unit menu to update':
                self.assertFalse(actionsdict[k])
        self.assertIsNone(widgetsdict.check_grids())
    
    def test_change_source(self):
        """Changement de la source courante d'une clé du dictionnaire.
        
        """
        metadata = """
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix uuid: <urn:uuid:> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

            uuid:479fd670-32c5-4ade-a26d-0268b0ce5046 a dcat:Dataset ;
                dct:accessRights [ a dct:RightsStatement ;
                    rdfs:label "Aucune restriction d'accès ou d'usage."@fr ],
                    <http://machin> ;
                dcat:theme <http://inspire.ec.europa.eu/theme/au> ;
                dct:identifier "479fd670-32c5-4ade-a26d-0268b0ce5046" .
            """
        metagraph = Metagraph().parse(data=metadata)
        conn = psycopg2.connect(WidgetsDictTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM z_plume.meta_import_sample_template()')
                cur.execute(
                    *query_get_categories('Classique')
                    )
                categories = cur.fetchall()
                cur.execute(
                    *query_template_tabs('Classique')
                    )
                tabs = cur.fetchall()
                cur.execute('DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg')
        conn.close()
        template = TemplateDict(categories, tabs)
        widgetsdict = WidgetsDict(metagraph=metagraph, template=template)
        self.assertIsNone(widgetsdict.check_grids())

        # --- Multiples thésaurus ---
        a = widgetsdict.root.search_from_path(DCAT.theme).children[0]
        widgetsdict[a]['main widget'] = '<A QComboBox dcat:theme>'
        self.assertEqual(widgetsdict[a]['current source'], 'Thème (INSPIRE)')
        actionsdict = widgetsdict.change_source(a, 'Thème de données (UE)')
        self.assertEqual(widgetsdict[a]['current source'], 'Thème de données (UE)')
        self.assertEqual(actionsdict['switch source menu to update'], [a])
        self.assertEqual(actionsdict['concepts list to update'], [a])
        self.assertEqual(actionsdict['value to update'], [a])
        self.assertTrue('Régions et villes' in widgetsdict[a]['thesaurus values'])
        for k in actionsdict.keys():
            if not k in ('switch source menu to update', 'concepts list to update',
                'value to update'):
                self.assertFalse(actionsdict[k])
        self.assertIsNone(widgetsdict.check_grids())
        
        # --- Item non référencé vers thésaurus ---
        g = widgetsdict.root.search_from_path(DCT.accessRights)
        b1 = g.children[2]
        b2 = g.children[3]
        widgetsdict[g]['grid widget'] = '<QGridLayout dct:accessRights>'
        widgetsdict[b1]['main widget'] = '<B1 QGroupBox dct:accessRights>'
        widgetsdict[b1]['minus widget'] = '<B1-minus QToolButton dct:accessRights>'
        widgetsdict[b1]['switch source widget'] = '<B1-source QToolButton dct:accessRights>'
        widgetsdict[b1]['switch source menu'] = '<B1-source QMenu dct:accessRights>'
        widgetsdict[b1]['switch source actions'] = ['<B1-source QAction n°1', '<B1-source QAction n°2']
        widgetsdict[b1.children[0]]['main widget'] = '<B1 QGroupBox rdfs:label>'
        widgetsdict[b2]['main widget'] = '<B2 QComboBox dct:accessRights>'
        widgetsdict[b2]['minus widget'] = '<B2-minus QToolButton dct:accessRights>'
        widgetsdict[b2]['switch source widget'] = '<B2-source QToolButton dct:accessRights>'
        widgetsdict[b2]['switch source menu'] = '<B2-source QMenu dct:accessRights>'
        widgetsdict[b2]['switch source actions'] = ['<B2-source QAction n°1', '<B2-source QAction n°2']
        self.assertEqual(widgetsdict[b2]['current source'], '< non référencé >')
        self.assertTrue(not '< non référencé >' in widgetsdict[b1]['sources'])
        actionsdict = widgetsdict.change_source(b2, "Droits d'accès (UE)")
        self.assertEqual(widgetsdict[b2]['current source'], "Droits d'accès (UE)")
        self.assertTrue(not '< non référencé >' in widgetsdict[b2]['sources'])
        self.assertTrue(not '< non référencé >' in widgetsdict[b1]['sources'])
        self.assertTrue(widgetsdict[b2]['thesaurus values'], 'public')
        self.assertListEqual(actionsdict['switch source menu to update'], [b2])
        self.assertIsNone(widgetsdict.check_grids())
        
        # --- Item non référencé vers manuel ---
        widgetsdict = WidgetsDict(metagraph=metagraph, template=template)
        self.assertIsNone(widgetsdict.check_grids())
        g = widgetsdict.root.search_from_path(DCT.accessRights)
        b1 = g.children[2]
        b2 = g.children[3]
        widgetsdict[g]['grid widget'] = '<QGridLayout dct:accessRights>'
        widgetsdict[b1]['main widget'] = '<B1 QGroupBox dct:accessRights>'
        widgetsdict[b1]['minus widget'] = '<B1-minus QToolButton dct:accessRights>'
        widgetsdict[b1]['switch source widget'] = '<B1-source QToolButton dct:accessRights>'
        widgetsdict[b1]['switch source menu'] = '<B1-source QMenu dct:accessRights>'
        widgetsdict[b1]['switch source actions'] = ['<B1-source QAction n°1', '<B1-source QAction n°2']
        widgetsdict[b1.children[0]]['main widget'] = '<B1 QGroupBox rdfs:label>'
        widgetsdict[b2]['main widget'] = '<B2 QComboBox dct:accessRights>'
        widgetsdict[b2]['minus widget'] = '<B2-minus QToolButton dct:accessRights>'
        widgetsdict[b2]['switch source widget'] = '<B2-source QToolButton dct:accessRights>'
        widgetsdict[b2]['switch source menu'] = '<B2-source QMenu dct:accessRights>'
        widgetsdict[b2]['switch source actions'] = ['<B2-source QAction n°1', '<B2-source QAction n°2']
        self.assertEqual(widgetsdict[b2]['current source'], '< non référencé >')
        self.assertTrue(not '< non référencé >' in widgetsdict[b1]['sources'])
        actionsdict = widgetsdict.change_source(b2, '< manuel >')
        self.assertEqual(widgetsdict[b1]['current source'], '< manuel >')
        self.assertTrue(not '< non référencé >' in widgetsdict[b1]['sources'])
        with self.assertRaises(ForbiddenOperation):
            actionsdict = widgetsdict.change_source(b1, '< non référencé >')
        # retour sur un thésaurus
        actionsdict = widgetsdict.change_source(b1, "Droits d'accès (UE)")
        self.assertTrue(not '< non référencé >' in widgetsdict[b2]['sources'])
        self.assertListEqual(actionsdict['switch source menu to update'], [b2])
        with self.assertRaises(ForbiddenOperation):
            actionsdict = widgetsdict.change_source(b2, '< non référencé >')
        self.assertIsNone(widgetsdict.check_grids())

        # --- Sortie du mode manuel ---
        g = widgetsdict.root.search_from_path(DCT.accessRights)
        b1 = g.children[0]
        b2 = g.children[1]
        widgetsdict[g]['grid widget'] = '<QGridLayout dct:accessRights>'
        widgetsdict[b1]['main widget'] = '<B1 QGroupBox dct:accessRights>'
        widgetsdict[b1]['minus widget'] = '<B1-minus QToolButton dct:accessRights>'
        widgetsdict[b1]['switch source widget'] = '<B1-source QToolButton dct:accessRights>'
        widgetsdict[b1]['switch source menu'] = '<B1-source QMenu dct:accessRights>'
        widgetsdict[b1]['switch source actions'] = ['<B1-source QAction n°1', '<B1-source QAction n°2']
        widgetsdict[b1.children[0]]['main widget'] = '<B1 QGroupBox rdfs:label>'
        widgetsdict[b2]['main widget'] = '<B2 QComboBox dct:accessRights>'
        widgetsdict[b2]['minus widget'] = '<B2-minus QToolButton dct:accessRights>'
        widgetsdict[b2]['switch source widget'] = '<B2-source QToolButton dct:accessRights>'
        widgetsdict[b2]['switch source menu'] = '<B2-source QMenu dct:accessRights>'
        widgetsdict[b2]['switch source actions'] = ['<B2-source QAction n°1', '<B2-source QAction n°2']
        self.assertEqual(widgetsdict[b1]['current source'], "< manuel >")
        self.assertFalse(widgetsdict[b1]['hidden'])
        self.assertFalse(widgetsdict[b1.children[0]]['hidden'])
        self.assertTrue(widgetsdict[b2]['hidden'])
        actionsdict = widgetsdict.change_source(b1, "Droits d'accès (UE)")
        self.assertEqual(widgetsdict[b2]['current source'], "Droits d'accès (UE)")
        self.assertTrue(widgetsdict[b2]['thesaurus values'], 'public')
        self.assertTrue(widgetsdict[b1]['hidden'])
        self.assertTrue(widgetsdict[b1.children[0]]['hidden'])
        self.assertFalse(widgetsdict[b2]['hidden'])
        self.assertEqual(actionsdict['widgets to show'], ['<B2 QComboBox dct:accessRights>',
            '<B2-minus QToolButton dct:accessRights>', '<B2-source QToolButton dct:accessRights>'])
        self.assertEqual(actionsdict['widgets to hide'], ['<B1 QGroupBox dct:accessRights>',
            '<B1-minus QToolButton dct:accessRights>', '<B1-source QToolButton dct:accessRights>',
            '<B1 QGroupBox rdfs:label>'])
        self.assertEqual(actionsdict['switch source menu to update'], [b2])
        self.assertEqual(actionsdict['concepts list to update'], [b2])
        self.assertEqual(actionsdict['value to update'], [b2])
        for k in actionsdict.keys():
            if not k in ('switch source menu to update', 'concepts list to update',
                'widgets to show', 'widgets to hide',  'value to update'):
                self.assertFalse(actionsdict[k])
        self.assertIsNone(widgetsdict.check_grids())

        # --- Entrée en mode manuel ---
        # cette fois avec une seule valeur dans le groupe, pour vérifier
        # qu'aucun bouton moins parasite n'apparaît
        widgetsdict.drop(g.children[3])
        self.assertTrue(b2.is_single_child)
        self.assertTrue(widgetsdict[b2]['hide minus button'])
        actionsdict = widgetsdict.change_source(b2, '< manuel >')
        self.assertEqual(widgetsdict[b1]['current source'], "< manuel >")
        self.assertFalse(widgetsdict[b1]['hidden'])
        self.assertFalse(widgetsdict[b1.children[0]]['hidden'])
        self.assertTrue(widgetsdict[b2]['hidden'])
        self.assertEqual(actionsdict['widgets to hide'], ['<B2 QComboBox dct:accessRights>',
            '<B2-minus QToolButton dct:accessRights>', '<B2-source QToolButton dct:accessRights>'])
        self.assertEqual(actionsdict['widgets to show'], ['<B1 QGroupBox dct:accessRights>',
            '<B1-source QToolButton dct:accessRights>', '<B1 QGroupBox rdfs:label>'])
        for k in actionsdict.keys():
            if not k in ('widgets to show', 'widgets to hide'):
                self.assertFalse(actionsdict[k])
        self.assertTrue(b1.is_single_child)
        self.assertTrue(widgetsdict[b1]['hide minus button'])
        self.assertIsNone(widgetsdict.check_grids())


    def test_twins_and_template(self):
        """Quelques contrôles sur le comportement des clés jumelles hors modèle.

        Lorsqu'aucune des catégories du groupe de propriété
        n'est dans le modèle, seul la clé-valeur est créée,
        et elle n'a alors pas de jumelle. Sauf bien sûr si le
        groupe de propriétés est nécessaire pour représenter
        la valeur stockée dans le graphe.
        
        """
        metadata = """
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix skos: <http://www.w3.org/2004/02/skos/core#> .
            @prefix uuid: <urn:uuid:> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

            uuid:479fd670-32c5-4ade-a26d-0268b0ce5046 a dcat:Dataset ;
                dct:accessRights <http://inspire.ec.europa.eu/metadata-codelist/LimitationsOnPublicAccess/noLimitations> ;
                dct:conformsTo [ a dct:Standard ;
                    skos:inScheme <http://www.opengis.net/def/crs/EPSG/0> ;
                    dct:identifier "4326" ],
                    <http://www.opengis.net/def/crs/EPSG/0/2154> ;
                dct:identifier "479fd670-32c5-4ade-a26d-0268b0ce5046" .
            """
        metagraph = Metagraph().parse(data=metadata)
        conn = psycopg2.connect(WidgetsDictTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM z_plume.meta_import_sample_template()')
                cur.execute('''
                    INSERT INTO z_plume.meta_template_categories (tpl_id, shrcat_path) (
                        SELECT tpl_id, 'dct:conformsTo' FROM z_plume.meta_template
                            WHERE tpl_label = 'Basique'
                    ) ;
                    DELETE FROM z_plume.meta_template_categories
                        WHERE tpl_id = (
                                SELECT meta_template.tpl_id FROM z_plume.meta_template
                                    WHERE tpl_label = 'Basique'
                            ) AND shrcat_path IN (
                                'dct:accessRights', 'dct:accessRights / rdfs:label'
                            ) ;
                    ''')
                cur.execute(
                    *query_get_categories('Basique')
                    )
                categories = cur.fetchall()
                cur.execute(
                    *query_template_tabs('Basique')
                    )
                tabs = cur.fetchall()
                cur.execute('DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg')
        conn.close()
        template = TemplateDict(categories, tabs)

        # --- non création du groupe de propriétés masqué hors modèle ---
        # et il n'y a même pas de clé dans l'arbre pour ce groupe
        widgetsdict = WidgetsDict(metagraph=metagraph, template=template)
        self.assertIsNone(widgetsdict.check_grids())
        g = widgetsdict.root.search_from_path(DCT.accessRights)
        self.assertEqual(len(g.children), 1)
        c = g.children[0]
        self.assertIsNone(c.m_twin)
        self.assertFalse('< manuel >' in widgetsdict[c]['sources'])

        g = widgetsdict.root.search_from_path(DCT.conformsTo)
        self.assertEqual(len(g.children), 3)
        c = g.children[0]
        self.assertTrue(c.m_twin)
        self.assertTrue("Système de référence de coordonnées EPSG (OGC)" in widgetsdict[c]['sources'])
        # NB: actif parce que dct:conformsTo a été ajoutée au modèle sans restreindre la liste
        # des vocabulaires autorisés.
        self.assertTrue("Système de référence de coordonnées EPSG utilisé sur le territoire français (OGC)" in widgetsdict[c]['sources'])
        self.assertTrue(widgetsdict[c]['multiple sources'])
        # on pourrait aussi ne pas avoir de clé-valeur jumelle dans
        # ce cas. Les deux tests précédents servent seulement à confirmer
        # ce comportement, même s'il pourrait être remis en question.
        self.assertTrue(len(c.children), 2)
        self.assertTrue(all(x in widgetsdict for x in g.children))
        self.assertTrue(all(x in widgetsdict for x in c.children))

        # --- non création du groupe de propriétés non masqué hors modèle ---
        # ce groupe est un fantôme et la clé-valeur jumelle éventuelle a été supprimée
        widgetsdict = WidgetsDict(metagraph=metagraph, template=template, mode='read')
        self.assertIsNone(widgetsdict.check_grids())
        g = widgetsdict.root.search_from_path(DCT.conformsTo)
        self.assertEqual(len(g.children), 2)
        c = g.children[0]
        self.assertTrue(c.is_ghost)
        self.assertIsNone(c.m_twin)
        self.assertFalse(c.is_hidden_m)
        self.assertFalse(c.is_main_twin)
        self.assertFalse(c in widgetsdict)
        self.assertEqual(len(c.children), 2)
        self.assertTrue(not any(x in widgetsdict for x in c.children))
        c = g.children[1]
        self.assertTrue(c in widgetsdict)
        self.assertEqual(c.row, 0)
        self.assertFalse(c.is_ghost)


    def test_translation_actions(self):
        """Changement de langue courante pour une clé.

        Ce test contrôle aussi l'effet des méthodes
        :py:meth:`plume.rdf.widgetsdict.WidgetsDict.drop` et
        :py:meth:`plume.rdf.widgetsdict.WidgetsDict.add` en
        mode traduction.
        
        """
        metadata = """
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix uuid: <urn:uuid:> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

            uuid:479fd670-32c5-4ade-a26d-0268b0ce5046 a dcat:Dataset ;
                dct:accessRights [ a dct:RightsStatement ;
                    rdfs:label "Aucune restriction d'accès ou d'usage."@fr ] ;
                dct:title "ADMIN EXPRESS - Départements de métropole"@fr ;
                dcat:keyword "admin express"@fr,
                    "donnée externe"@fr,
                    "external data"@en,
                    "ign"@fr ;
                dct:temporal [ a dct:PeriodOfTime ;
                    dcat:endDate "2021-01-15"^^xsd:date ;
                    dcat:startDate "2021-01-15"^^xsd:date ] ;
                dcat:theme <http://inspire.ec.europa.eu/theme/au> ;
                dct:identifier "479fd670-32c5-4ade-a26d-0268b0ce5046" ;
                uuid:218c1245-6ba7-4163-841e-476e0d5582af "À mettre à jour !"@fr .
            """
        metagraph = Metagraph().parse(data=metadata)
        conn = psycopg2.connect(WidgetsDictTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM z_plume.meta_import_sample_template()')
                cur.execute(
                    *query_get_categories('Basique')
                    )
                categories = cur.fetchall()
                cur.execute(
                    *query_template_tabs('Basique')
                    )
                tabs = cur.fetchall()
                cur.execute('DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg')
        conn.close()
        template = TemplateDict(categories, tabs)
        widgetsdict = WidgetsDict(metagraph=metagraph, template=template,
            translation=True, langList=['fr', 'en', 'it'])
        self.assertIsNone(widgetsdict.check_grids())

        # --- ajout d'une clé dans un groupe de traduction ---
        g = widgetsdict.root.search_from_path(DCT.title)
        widgetsdict[g]['grid widget'] = '<QGridLayout dct:title>'
        widgetsdict[g.button]['main widget'] = '<P QToolButton dct:title>'
        fr = g.children[0]
        widgetsdict[fr]['main widget'] = '<FR QLineEdit dct:title>'
        widgetsdict[fr]['minus widget'] = '<FR-minus QToolButton dct:title>'
        widgetsdict[fr]['language widget'] = '<FR-language QToolButton dct:title>'
        widgetsdict[fr]['language menu'] = '<FR-language QMenu dct:title>'
        widgetsdict[fr]['language actions'] = ['<FR-language QAction n°1', '<FR-language QAction n°2']
        self.assertEqual(widgetsdict[fr]['authorized languages'], ['fr', 'en', 'it'])
        actionsdict = widgetsdict.add(g.button)
        en = g.children[1]
        widgetsdict[en]['main widget'] = '<EN QLineEdit dct:title>'
        widgetsdict[en]['minus widget'] = '<EN-minus QToolButton dct:title>'
        widgetsdict[en]['language widget'] = '<EN-language QToolButton dct:title>'
        widgetsdict[en]['language menu'] = '<EN-language QMenu dct:title>'
        widgetsdict[en]['language actions'] = ['<EN-language QAction n°1', '<EN-language QAction n°2']
        self.assertEqual(widgetsdict[fr]['authorized languages'], ['fr', 'it'])
        self.assertEqual(widgetsdict[fr]['language value'], 'fr')
        self.assertEqual(widgetsdict[en]['authorized languages'], ['en', 'it'])
        self.assertEqual(widgetsdict[en]['language value'], 'en')
        self.assertFalse(widgetsdict[g.button]['hidden'])
        self.assertEqual(actionsdict['new keys'], [en])
        self.assertEqual(actionsdict['language menu to update'], [fr])
        self.assertEqual(actionsdict['widgets to move'], [('<QGridLayout dct:title>',
            '<P QToolButton dct:title>', 2, 0, 1, 1)])
        self.assertEqual(actionsdict['widgets to show'], ['<FR-minus QToolButton dct:title>'])
        for k in actionsdict.keys():
            if not k in ('new keys', 'language menu to update',
                'widgets to move', 'widgets to show'):
                self.assertFalse(actionsdict[k])
        actionsdict = widgetsdict.add(g.button)
        it = g.children[2]
        widgetsdict[it]['main widget'] = '<IT QLineEdit dct:title>'
        widgetsdict[it]['minus widget'] = '<IT-minus QToolButton dct:title>'
        widgetsdict[it]['language widget'] = '<IT-language QToolButton dct:title>'
        widgetsdict[it]['language menu'] = '<IT-language QMenu dct:title>'
        widgetsdict[it]['language actions'] = ['<IT-language QAction n°1', '<IT-language QAction n°2']
        self.assertEqual(widgetsdict[fr]['authorized languages'], ['fr'])
        self.assertEqual(widgetsdict[fr]['language value'], 'fr')
        self.assertEqual(widgetsdict[en]['authorized languages'], ['en'])
        self.assertEqual(widgetsdict[en]['language value'], 'en')
        self.assertEqual(widgetsdict[it]['authorized languages'], ['it'])
        self.assertEqual(widgetsdict[it]['language value'], 'it')
        self.assertTrue(widgetsdict[g.button]['hidden'])
        self.assertEqual(actionsdict['new keys'], [it])
        self.assertEqual(actionsdict['language menu to update'], [fr, en])
        self.assertEqual(actionsdict['widgets to move'], [('<QGridLayout dct:title>',
            '<P QToolButton dct:title>', 3, 0, 1, 1)])
        self.assertEqual(actionsdict['widgets to hide'], ['<P QToolButton dct:title>'])
        for k in actionsdict.keys():
            if not k in ('new keys', 'language menu to update',
                'widgets to move', 'widgets to hide'):
                self.assertFalse(actionsdict[k])
        self.assertIsNone(widgetsdict.check_grids())

        # --- suppression d'une clé dans un groupe de traduction ---
        actionsdict = widgetsdict.drop(fr)
        self.assertFalse(fr in widgetsdict)
        self.assertEqual(widgetsdict[en]['authorized languages'], ['en', 'fr'])
        self.assertEqual(widgetsdict[en]['language value'], 'en')
        self.assertEqual(widgetsdict[it]['authorized languages'], ['it', 'fr'])
        self.assertEqual(widgetsdict[it]['language value'], 'it')
        self.assertFalse(widgetsdict[g.button]['hidden'])
        self.assertEqual(actionsdict['widgets to show'], ['<P QToolButton dct:title>'])
        self.assertEqual(actionsdict['widgets to delete'], ['<FR QLineEdit dct:title>',
            '<FR-minus QToolButton dct:title>', '<FR-language QToolButton dct:title>'])
        self.assertEqual(actionsdict['actions to delete'], ['<FR-language QAction n°1',
            '<FR-language QAction n°2'])
        self.assertEqual(actionsdict['menus to delete'], ['<FR-language QMenu dct:title>'])
        self.assertEqual(actionsdict['language menu to update'], [en, it])
        self.assertEqual(actionsdict['widgets to move'],
            [('<QGridLayout dct:title>', '<EN QLineEdit dct:title>',
                0, 0, 1, WidgetsDictTestCase.grid - 2),
             ('<QGridLayout dct:title>', '<EN-minus QToolButton dct:title>',
                0, WidgetsDictTestCase.grid - 1, 1, 1),
             ('<QGridLayout dct:title>', '<EN-language QToolButton dct:title>',
                0, WidgetsDictTestCase.grid - 2, 1, 1),
             ('<QGridLayout dct:title>', '<IT QLineEdit dct:title>',
                1, 0, 1, WidgetsDictTestCase.grid - 2),
             ('<QGridLayout dct:title>', '<IT-minus QToolButton dct:title>',
                1, WidgetsDictTestCase.grid - 1, 1, 1),
             ('<QGridLayout dct:title>', '<IT-language QToolButton dct:title>',
                1, WidgetsDictTestCase.grid - 2, 1, 1),
             ('<QGridLayout dct:title>', '<P QToolButton dct:title>',
                2, 0, 1, 1)])
        for k in actionsdict.keys():
            if not k in ('widgets to show', 'widgets to delete', 'actions to delete',
                'menus to delete', 'language menu to update', 'widgets to move'):
                self.assertFalse(actionsdict[k])
        self.assertIsNone(widgetsdict.check_grids())

        # --- changement de langue dans un groupe de traduction ---
        actionsdict = widgetsdict.change_language(en, 'fr')
        self.assertEqual(widgetsdict[en]['authorized languages'], ['fr', 'en'])
        self.assertEqual(widgetsdict[en]['language value'], 'fr')
        self.assertEqual(widgetsdict[it]['authorized languages'], ['it', 'en'])
        self.assertEqual(widgetsdict[it]['language value'], 'it')
        self.assertEqual(actionsdict['language menu to update'], [en, it])
        for k in actionsdict.keys():
            if not k in ('language menu to update'):
                self.assertFalse(actionsdict[k])
        self.assertIsNone(widgetsdict.check_grids())
        
        # --- ajout d'une clé hors groupe de traduction ---
        g = widgetsdict.root.search_from_path(DCAT.keyword)
        widgetsdict[g]['grid widget'] = '<QGridLayout dcat:keyword>'
        widgetsdict[g.button]['main widget'] = '<P QToolButton dcat:keyword>'
        actionsdict = widgetsdict.add(g.button)
        c = g.children[4]
        widgetsdict[c]['main widget'] = '<C QLineEdit dcat:keyword>'
        widgetsdict[c]['minus widget'] = '<C-minus QToolButton dcat:keyword>'
        widgetsdict[c]['language widget'] = '<C-language QToolButton dcat:keyword>'
        widgetsdict[c]['language menu'] = '<C-language QMenu dcat:keyword>'
        widgetsdict[c]['language actions'] = ['<C-language QAction n°1', '<C-language QAction n°2']
        self.assertEqual(widgetsdict[c]['authorized languages'], ['fr', 'en', 'it'])
        self.assertEqual(widgetsdict[c]['language value'], 'fr')
        self.assertEqual(actionsdict['widgets to move'],
            [('<QGridLayout dcat:keyword>', '<P QToolButton dcat:keyword>',
                5, 0, 1, 1)])
        self.assertEqual(actionsdict['new keys'], [c])
        for k in actionsdict.keys():
            if not k in ('widgets to move', 'new keys'):
                self.assertFalse(actionsdict[k])
        self.assertIsNone(widgetsdict.check_grids())
        
        # --- suppression d'une clé hors groupe de traduction ---
        actionsdict = widgetsdict.drop(c)
        self.assertFalse(c in widgetsdict)
        self.assertEqual(widgetsdict[g.children[0]]['authorized languages'], ['fr', 'en', 'it'])
        self.assertEqual(actionsdict['widgets to delete'], ['<C QLineEdit dcat:keyword>',
            '<C-minus QToolButton dcat:keyword>', '<C-language QToolButton dcat:keyword>'])
        self.assertEqual(actionsdict['actions to delete'], ['<C-language QAction n°1',
            '<C-language QAction n°2'])
        self.assertEqual(actionsdict['menus to delete'], ['<C-language QMenu dcat:keyword>'])
        self.assertEqual(actionsdict['widgets to move'],
            [('<QGridLayout dcat:keyword>', '<P QToolButton dcat:keyword>',
                4, 0, 1, 1)])
        for k in actionsdict.keys():
            if not k in ('widgets to delete', 'actions to delete',
                'menus to delete', 'widgets to move'):
                self.assertFalse(actionsdict[k])
        self.assertIsNone(widgetsdict.check_grids())
        
        # --- changement de langue hors groupe de traduction ---
        c = g.children[0]
        widgetsdict[c]['main widget'] = '<C QLineEdit dcat:keyword>'
        widgetsdict[c]['minus widget'] = '<C-minus QToolButton dcat:keyword>'
        widgetsdict[c]['language widget'] = '<C-language QToolButton dcat:keyword>'
        widgetsdict[c]['language menu'] = '<C-language QMenu dcat:keyword>'
        widgetsdict[c]['language actions'] = ['<C-language QAction n°1', '<C-language QAction n°2']
        self.assertEqual(widgetsdict[c]['language value'], 'fr')
        actionsdict = widgetsdict.change_language(c, 'it')
        self.assertEqual(widgetsdict[c]['authorized languages'], ['fr', 'en', 'it'])
        self.assertEqual(widgetsdict[c]['language value'], 'it')
        self.assertEqual(actionsdict['language menu to update'], [c])
        for k in actionsdict.keys():
            if not k in ('language menu to update'):
                self.assertFalse(actionsdict[k])
        self.assertIsNone(widgetsdict.check_grids())

    def test_translation_unauthorized_language(self):
        """Contrôle du comportement en présence de langues non autorisées.
        
        """
        metadata = """
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix uuid: <urn:uuid:> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

            uuid:479fd670-32c5-4ade-a26d-0268b0ce5046 a dcat:Dataset ;
                dct:accessRights [ a dct:RightsStatement ;
                    rdfs:label "Aucune restriction d'accès ou d'usage."@fr ] ;
                dct:title "ADMIN EXPRESS - Départements de métropole"@fr,
                    "ADMIN EXPRESS - Metropolitan Departments"@en;
                dcat:keyword "admin express"@fr,
                    "donnée externe"@fr,
                    "external data"@en,
                    "ign"@fr ;
                dct:temporal [ a dct:PeriodOfTime ;
                    dcat:endDate "2021-01-15"^^xsd:date ;
                    dcat:startDate "2021-01-15"^^xsd:date ] ;
                dcat:theme <http://inspire.ec.europa.eu/theme/au> ;
                dct:identifier "479fd670-32c5-4ade-a26d-0268b0ce5046" ;
                uuid:218c1245-6ba7-4163-841e-476e0d5582af "À mettre à jour !"@fr .
            """
        metagraph = Metagraph().parse(data=metadata)
        conn = psycopg2.connect(WidgetsDictTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM z_plume.meta_import_sample_template()')
                cur.execute(
                    *query_get_categories('Basique')
                    )
                categories = cur.fetchall()
                cur.execute(
                    *query_template_tabs('Basique')
                    )
                tabs = cur.fetchall()
                cur.execute('DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg')
        conn.close()
        template = TemplateDict(categories, tabs)
        widgetsdict = WidgetsDict(metagraph=metagraph, template=template,
            translation=True, langList=['fr', 'it'])
        g = widgetsdict.root.search_from_path(DCT.title)
        self.assertEqual(widgetsdict[g.children[0]]['language value'], 'fr')
        self.assertEqual(widgetsdict[g.children[0]]['authorized languages'], ['fr', 'it'])
        self.assertEqual(widgetsdict[g.children[1]]['language value'], 'en')
        self.assertEqual(widgetsdict[g.children[1]]['authorized languages'], ['en', 'it'])
        actionsdict = widgetsdict.drop(g.children[0])
        self.assertEqual(widgetsdict[g.children[0]]['language value'], 'en')
        self.assertEqual(widgetsdict[g.children[0]]['authorized languages'], ['en', 'it', 'fr'])
        actionsdict = widgetsdict.add(g.button)
        self.assertEqual(widgetsdict[g.children[0]]['language value'], 'en')
        self.assertEqual(widgetsdict[g.children[0]]['authorized languages'], ['en', 'fr'])
        self.assertEqual(widgetsdict[g.children[1]]['language value'], 'it')
        self.assertEqual(widgetsdict[g.children[1]]['authorized languages'], ['it', 'fr'])
        actionsdict = widgetsdict.drop(g.children[0])
        self.assertEqual(widgetsdict[g.children[0]]['language value'], 'it')
        self.assertEqual(widgetsdict[g.children[0]]['authorized languages'], ['it', 'fr'])
        self.assertIsNone(widgetsdict.check_grids())
        with self.assertRaises(ForbiddenOperation):
            actionsdict = widgetsdict.change_language(g.children[0], 'en')

    def test_update_value(self):
        """Mise à jour des valeurs stockées dans les clés avec dé-sérialisation.

        Vérifie en même temps le fonctionnement de
        :py:meth:`plume.rdf.widgetsdict.WidgetsDict.str_value`
        en mode édition, puisque cette dernière est appliquée
        pour mettre à jour la clé ``value`` du dictionnaire
        interne.
        
        """
        metadata = """
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix foaf: <http://xmlns.com/foaf/0.1/> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix plume: <http://registre.data.developpement-durable.gouv.fr/plume/> .
            @prefix uuid: <urn:uuid:> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

            uuid:479fd670-32c5-4ade-a26d-0268b0ce5046 a dcat:Dataset ;
                dct:accessRights [ a dct:RightsStatement ;
                    rdfs:label "Aucune restriction d'accès ou d'usage."@fr ] ;
                dct:title "ADMIN EXPRESS - Départements de métropole"@fr,
                    "ADMIN EXPRESS - Metropolitan Departments"@en;
                dcat:keyword "admin express"@fr,
                    "donnée externe"@fr,
                    "external data"@en,
                    "ign"@fr ;
                dct:temporal [ a dct:PeriodOfTime ;
                    dcat:endDate "2021-01-15"^^xsd:date ;
                    dcat:startDate "2021-01-15"^^xsd:date ] ;
                dcat:temporalResolution "P1M"^^xsd:duration ;
                dcat:theme <http://inspire.ec.europa.eu/theme/au> ;
                dct:identifier "479fd670-32c5-4ade-a26d-0268b0ce5046" ;
                foaf:isPrimaryTopicOf [ a dcat:CatalogRecord ;
                    dct:modified "2022-02-13T15:30:15"^^xsd:dateTime ] ;
                plume:isExternal true ;
                uuid:218c1245-6ba7-4163-841e-476e0d5582af "À mettre à jour !"@fr .
            """
        metagraph = Metagraph().parse(data=metadata)
        conn = psycopg2.connect(WidgetsDictTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM z_plume.meta_import_sample_template()')
                cur.execute("SELECT tpl_id FROM z_plume.meta_template WHERE tpl_label = 'Classique'")
                tpl_id = cur.fetchone()[0]
                cur.execute(
                    """
                    INSERT INTO z_plume.meta_categorie (path, label, datatype)
                        VALUES ('uuid:ae75b755-97e7-4d56-be15-00c143b37af0', 'test heure', 'xsd:time'),
                            ('uuid:7a656b67-45a6-4b85-948b-334caca7671f', 'test entier', 'xsd:integer'),
                            ('uuid:9ade6b00-a16a-424c-af8f-9c4bfb2a92f9', 'test décimal', 'xsd:decimal') ;
                    INSERT INTO z_plume.meta_template_categories (tpl_id, loccat_path)
                        VALUES (%(tpl_id)s, 'uuid:ae75b755-97e7-4d56-be15-00c143b37af0'),
                            (%(tpl_id)s, 'uuid:7a656b67-45a6-4b85-948b-334caca7671f'),
                            (%(tpl_id)s, 'uuid:9ade6b00-a16a-424c-af8f-9c4bfb2a92f9') ;
                    """,
                    {'tpl_id': tpl_id}
                )
                cur.execute(
                    *query_get_categories('Classique')
                    )
                categories = cur.fetchall()
                cur.execute(
                    *query_template_tabs('Classique')
                    )
                tabs = cur.fetchall()
                cur.execute('DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg')
        conn.close()
        template = TemplateDict(categories, tabs)
        widgetsdict = WidgetsDict(metagraph=metagraph, template=template,
            translation=True)
        self.assertIsNone(widgetsdict.check_grids())

        # --- suppression de la valeur ---
        g = widgetsdict.root.search_from_path(DCAT.keyword)
        c = g.children[1]
        widgetsdict.update_value(c, None)
        self.assertEqual(c.value, None)
        self.assertEqual(widgetsdict[c]['value'], None)

        c = g.children[2]
        widgetsdict.update_value(c, '')
        self.assertEqual(c.value, None)
        self.assertEqual(widgetsdict[c]['value'], None)
        
        # --- litéral avec une langue ---
        g = widgetsdict.root.search_from_path(DCT.title)
        c = g.children[1]
        widgetsdict.update_value(c, 'Metropolitan Departments (Admin Express)')
        self.assertEqual(c.value, Literal('Metropolitan Departments (Admin Express)', lang='en'))
        self.assertEqual(widgetsdict[c]['value'], 'Metropolitan Departments (Admin Express)')

        # --- litéral sans langue ---
        c = widgetsdict.root.search_from_path(OWL.versionInfo)
        widgetsdict.update_value(c, '1.0')
        self.assertEqual(c.value, Literal('1.0'))
        self.assertEqual(widgetsdict[c]['value'], '1.0')

        # --- date ---
        c = widgetsdict.root.search_from_path(DCT.modified)
        widgetsdict.update_value(c, '21/01/2021 00:00:00')
        self.assertEqual(c.value, Literal('2021-01-21', datatype=XSD.date))
        self.assertEqual(widgetsdict[c]['value'], '21/01/2021')

        # --- date et heure ---
        c = widgetsdict.root.search_from_path(FOAF.isPrimaryTopicOf / DCT.modified)
        widgetsdict.update_value(c, '21/01/2021')
        self.assertEqual(c.value, Literal('2021-01-21T00:00:00', datatype=XSD.dateTime))
        self.assertEqual(widgetsdict[c]['value'], '21/01/2021 00:00:00')
        
        # --- heure ---
        c = widgetsdict.root.search_from_path(LOCAL['ae75b755-97e7-4d56-be15-00c143b37af0'])
        widgetsdict.update_value(c, '12:00:01.3333')
        self.assertEqual(c.value, Literal('12:00:01', datatype=XSD.time))
        self.assertEqual(widgetsdict[c]['value'], '12:00:01')

        # --- entier ---
        c = widgetsdict.root.search_from_path(LOCAL['7a656b67-45a6-4b85-948b-334caca7671f'])
        widgetsdict.update_value(c, 'chose')
        self.assertIsNone(c.value)
        self.assertIsNone(widgetsdict[c]['value'])
        widgetsdict.update_value(c, '999')
        self.assertEqual(c.value, Literal('999', datatype=XSD.integer))
        self.assertEqual(widgetsdict[c]['value'], '999')
        
        # --- décimal ---
        c = widgetsdict.root.search_from_path(LOCAL['9ade6b00-a16a-424c-af8f-9c4bfb2a92f9'])
        widgetsdict.update_value(c, 'chose')
        self.assertIsNone(c.value)
        self.assertIsNone(widgetsdict[c]['value'])
        widgetsdict.update_value(c, '999,99')
        self.assertEqual(c.value, Literal('999.99', datatype=XSD.decimal))
        self.assertEqual(widgetsdict[c]['value'], '999,99')

        # --- boolean ---
        c = widgetsdict.root.search_from_path(PLUME.isExternal)
        widgetsdict.update_value(c, None)
        self.assertIsNone(c.value)
        self.assertIsNone(widgetsdict[c]['value'])
        widgetsdict.update_value(c, False)
        self.assertEqual(c.value, Literal('false', datatype=XSD.boolean))
        self.assertEqual(widgetsdict[c]['value'], 'False')
        widgetsdict.update_value(c, 'True')
        self.assertEqual(c.value, Literal('true', datatype=XSD.boolean))
        self.assertEqual(widgetsdict[c]['value'], 'True')

        # --- URI basique ---
        g = widgetsdict.root.search_from_path(DCAT.landingPage)
        widgetsdict.add(g.button)
        c = g.children[1]
        widgetsdict.update_value(c, 'https://www.postgresql.org/docs/14/index.html')
        self.assertEqual(c.value, URIRef('https://www.postgresql.org/docs/14/index.html'))
        self.assertEqual(widgetsdict[c]['value'], 'https://www.postgresql.org/docs/14/index.html')

        # --- téléphone ---
        c = widgetsdict.root.search_from_path(DCAT.contactPoint / VCARD.hasTelephone).children[0]
        widgetsdict.update_value(c, '0123456789')
        self.assertEqual(c.value, URIRef('tel:+33-1-23-45-67-89'))
        self.assertEqual(widgetsdict[c]['value'], '+33-1-23-45-67-89')

        # --- mél ---
        c = widgetsdict.root.search_from_path(DCAT.contactPoint / VCARD.hasEmail).children[0]
        widgetsdict.update_value(c, 'service@developpement-durable.gouv.fr')
        self.assertEqual(c.value, URIRef('mailto:service@developpement-durable.gouv.fr'))
        self.assertEqual(widgetsdict[c]['value'], 'service@developpement-durable.gouv.fr')

        # --- durée (avec unité) ---
        c = widgetsdict.root.search_from_path(DCAT.temporalResolution)
        widgetsdict.change_unit(c, 'heures')
        widgetsdict.update_value(c, '5')
        self.assertEqual(c.value, Literal('PT5H', datatype=XSD.duration))
        self.assertEqual(widgetsdict[c]['value'], '5')

        # --- valeur de thésaurus ---
        g = widgetsdict.root.search_from_path(DCAT.theme)
        c = g.children[0]
        widgetsdict.change_source(c, 'Thème de données (UE)')
        widgetsdict.update_value(c, 'Régions et villes')
        self.assertEqual(c.value, URIRef('http://publications.europa.eu/resource/authority/data-theme/REGI'))
        self.assertEqual(widgetsdict[c]['value'], 'Régions et villes')

        metadata = """
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix foaf: <http://xmlns.com/foaf/0.1/> .
            @prefix owl: <http://www.w3.org/2002/07/owl#> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix plume: <http://registre.data.developpement-durable.gouv.fr/plume/> .
            @prefix uuid: <urn:uuid:> .
            @prefix vcard: <http://www.w3.org/2006/vcard/ns#> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

            uuid:479fd670-32c5-4ade-a26d-0268b0ce5046 a dcat:Dataset ;
                dct:accessRights [ a dct:RightsStatement ;
                    rdfs:label "Aucune restriction d'accès ou d'usage."@fr ] ;
                dct:title "ADMIN EXPRESS - Départements de métropole"@fr,
                    "Metropolitan Departments (Admin Express)"@en ;
                dcat:keyword "admin express"@fr,
                    "ign"@fr ;
                dcat:landingPage <https://www.postgresql.org/docs/14/index.html> ;
                dct:modified "2021-01-21"^^xsd:date ;
                dct:temporal [ a dct:PeriodOfTime ;
                    dcat:endDate "2021-01-15"^^xsd:date ;
                    dcat:startDate "2021-01-15"^^xsd:date ] ;
                dcat:temporalResolution "PT5H"^^xsd:duration ;
                dcat:theme <http://publications.europa.eu/resource/authority/data-theme/REGI> ;
                dct:identifier "479fd670-32c5-4ade-a26d-0268b0ce5046" ;
                owl:versionInfo "1.0" ;
                dcat:contactPoint [ a vcard:Kind ;
                    vcard:hasTelephone <tel:+33-1-23-45-67-89> ;
                    vcard:hasEmail <mailto:service@developpement-durable.gouv.fr> ] ;
                foaf:isPrimaryTopicOf [ a dcat:CatalogRecord ;
                    dct:modified "2021-01-21T00:00:00"^^xsd:dateTime ] ;
                plume:isExternal true ;
                uuid:218c1245-6ba7-4163-841e-476e0d5582af "À mettre à jour !"@fr ;
                uuid:ae75b755-97e7-4d56-be15-00c143b37af0 "12:00:01"^^xsd:time ;
                uuid:7a656b67-45a6-4b85-948b-334caca7671f "999"^^xsd:integer ;
                uuid:9ade6b00-a16a-424c-af8f-9c4bfb2a92f9 "999.99"^^xsd:decimal .
            """
        metagraph = Metagraph().parse(data=metadata)
        self.assertTrue(isomorphic(metagraph,
            widgetsdict.build_metagraph(preserve_metadata_date=True)))

    def test_local_categories(self):
        """Quelques contrôles sur la gestion des catégories locales.
        
        """
        conn = psycopg2.connect(WidgetsDictTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('''
                    INSERT INTO z_plume.meta_categorie (path, label, datatype)
                        VALUES
                            ('uuid:5cf84c0d-0f9c-42b7-831b-3f28be735ff0', 'test datatype time', 'xsd:time'),
                            ('uuid:a4178b2c-153d-4a26-b319-2c32589afbed', 'test datatype date', 'xsd:date'),
                            ('uuid:4f507de9-cc01-40f3-a0c3-45f134299110', 'test datatype dateTime', 'xsd:dateTime'),
                            ('uuid:14363668-e379-4dcb-8612-48f9c76fc778', 'test datatype duration', 'xsd:duration'),
                            ('uuid:19a3b882-ea1c-44de-a0c4-a6cbac3f9750', 'test datatype string', 'xsd:string'),
                            ('uuid:0da96c90-b2a1-4bbf-97e5-d3701aa1cb47', 'test datatype langString', 'rdf:langString'),
                            ('uuid:15bad182-883a-439e-a510-7abd6896bec7', 'test datatype integer', 'xsd:integer'),
                            ('uuid:97130125-3c03-4372-bc3e-da6d3a654a52', 'test datatype decimal', 'xsd:decimal'),
                            ('uuid:c2dc9756-8088-4f99-b6d7-d3897513406b', 'test datatype wktLiteral', 'gsp:wktLiteral'),
                            ('uuid:de2aa975-5663-4a72-b390-dd9aab1c2810', 'test datatype iri', NULL) ;
                    UPDATE z_plume.meta_categorie
                        SET geo_tools = ARRAY['show', 'rectangle', 'polygon', 'centroid', 'circle']::z_plume.meta_geo_tool[]
                        WHERE label = 'test datatype wktLiteral' ;
                    UPDATE z_plume.meta_categorie
                        SET special = 'url'
                        WHERE label = 'test datatype iri' ;
                    INSERT INTO z_plume.meta_template(tpl_id, tpl_label) VALUES (100, 'Datatype') ;
                    INSERT INTO z_plume.meta_template_categories (tpl_id, loccat_path)
                        (SELECT 100, path FROM z_plume.meta_categorie WHERE label ~ 'test.datatype') ;
                    ''')
                cur.execute(
                    *query_get_categories('Datatype')
                    )
                categories = cur.fetchall()
                cur.execute('DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg')
        conn.close()
        template = TemplateDict(categories)
        widgetsdict = WidgetsDict(template=template, translation=True)
        self.assertIsNone(widgetsdict.check_grids())
        k = widgetsdict.root.search_from_path(LOCAL['de2aa975-5663-4a72-b390-dd9aab1c2810'])
        self.assertEqual(widgetsdict[k]['regex validator pattern'],
            r'^[^<>"\s{}|\\^`]*$')
        k = widgetsdict.root.search_from_path(LOCAL['c2dc9756-8088-4f99-b6d7-d3897513406b'])
        self.assertTrue(k.is_long_text)
        self.assertEqual(widgetsdict.widget_type(k), 'QTextEdit')
        self.assertListEqual(widgetsdict[k]['geo tools'],
            ['show', 'rectangle', 'polygon', 'centroid', 'circle'])
        k = widgetsdict.root.search_from_path(LOCAL['14363668-e379-4dcb-8612-48f9c76fc778'])
        self.assertListEqual(widgetsdict[k]['units'],
            ['ans', 'mois', 'jours', 'heures', 'min.', 'sec.'])
        self.assertEqual(widgetsdict[k]['current unit'], 'ans')
        k = widgetsdict.root.search_from_path(LOCAL['0da96c90-b2a1-4bbf-97e5-d3701aa1cb47'])
        self.assertListEqual(widgetsdict[k]['authorized languages'], ['fr', 'en'])
        self.assertEqual(widgetsdict[k]['language value'], 'fr')
        k = widgetsdict.root.search_from_path(LOCAL['15bad182-883a-439e-a510-7abd6896bec7'])
        self.assertEqual(widgetsdict[k]['type validator'], 'QIntValidator')
        k = widgetsdict.root.search_from_path(LOCAL['97130125-3c03-4372-bc3e-da6d3a654a52'])
        self.assertEqual(widgetsdict[k]['type validator'], 'QDoubleValidator')
        
    def test_unknown_categories(self):
        """Gestion des catégories non référencées.
        
        """
        metadata = """
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix uuid: <urn:uuid:> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

            uuid:479fd670-32c5-4ade-a26d-0268b0ce5046 a dcat:Dataset ;
                dct:title "ADMIN EXPRESS - Départements de métropole"@fr ;
                dct:identifier "479fd670-32c5-4ade-a26d-0268b0ce5046" ;
                uuid:ae070a1a-190f-4541-8913-b5946ed46296 4.5 ;
                uuid:e22f03b3-e571-45d9-97c1-44e2737c12f2 8 ;
                uuid:6e855e63-5f6e-47eb-ab28-4db4124c172e "2022-02-15T15:27:31"^^xsd:dateTime,
                    "2022-02-14"^^xsd:date ;
                uuid:3028ca2c-73eb-4707-80ea-69210eeffb97 <https://github.com/MTES-MCT/metadata-postgresql> ;
                uuid:218c1245-6ba7-4163-841e-476e0d5582af "À mettre à jour !"@fr .
            """
        metagraph = Metagraph().parse(data=metadata)
        widgetsdict = WidgetsDict(metagraph=metagraph)
        self.assertIsNone(widgetsdict.check_grids())
        k = widgetsdict.root.search_from_path(LOCAL['ae070a1a-190f-4541-8913-b5946ed46296'])
        self.assertEqual(k.datatype, XSD.decimal)
        self.assertEqual(widgetsdict[k]['value'], '4,5')
        k = widgetsdict.root.search_from_path(LOCAL['e22f03b3-e571-45d9-97c1-44e2737c12f2'])
        self.assertEqual(k.datatype, XSD.integer)
        self.assertEqual(widgetsdict[k]['value'], '8')
        widgetsdict.update_value(k, 10)
        k = widgetsdict.root.search_from_path(
            LOCAL['6e855e63-5f6e-47eb-ab28-4db4124c172e']).children[0]
        self.assertEqual(k.datatype, XSD.dateTime)
        self.assertEqual(widgetsdict[k]['value'], '15/02/2022 15:27:31')
        k = widgetsdict.root.search_from_path(
            LOCAL['6e855e63-5f6e-47eb-ab28-4db4124c172e']).children[1]
        self.assertEqual(k.datatype, XSD.dateTime)
        self.assertEqual(widgetsdict[k]['value'], '14/02/2022 00:00:00')
        k = widgetsdict.root.search_from_path(LOCAL['3028ca2c-73eb-4707-80ea-69210eeffb97'])
        self.assertIsNone(k.datatype)
        self.assertIsNotNone(k.rdfclass)
        self.assertEqual(widgetsdict[k]['regex validator pattern'],
            r'^[^<>"\s{}|\\^`]*$')
        self.assertEqual(widgetsdict[k]['value'], 
            'https://github.com/MTES-MCT/metadata-postgresql')
        k = widgetsdict.root.search_from_path(LOCAL['218c1245-6ba7-4163-841e-476e0d5582af'])
        self.assertEqual(k.datatype, RDF.langString)
        self.assertEqual(widgetsdict[k]['language value'], 'fr')
        self.assertEqual(widgetsdict[k]['value'], 'À mettre à jour !')
        for k, v in widgetsdict.items():
            # mise à jour indifférenciée, semblable à ce qui est
            # fait lorsque l'utilisateur demande l'enregistrement
            # dans l'interface de Plume
            widgetsdict.update_value(k, v['value'])
        metadata = """
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix uuid: <urn:uuid:> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

            uuid:479fd670-32c5-4ade-a26d-0268b0ce5046 a dcat:Dataset ;
                dct:title "ADMIN EXPRESS - Départements de métropole"@fr ;
                dct:identifier "479fd670-32c5-4ade-a26d-0268b0ce5046" ;
                uuid:ae070a1a-190f-4541-8913-b5946ed46296 4.5 ;
                uuid:e22f03b3-e571-45d9-97c1-44e2737c12f2 10 ;
                uuid:6e855e63-5f6e-47eb-ab28-4db4124c172e "2022-02-15T15:27:31"^^xsd:dateTime,
                    "2022-02-14T00:00:00"^^xsd:dateTime ;
                uuid:3028ca2c-73eb-4707-80ea-69210eeffb97 <https://github.com/MTES-MCT/metadata-postgresql> ;
                uuid:218c1245-6ba7-4163-841e-476e0d5582af "À mettre à jour !"@fr .
            """
        metagraph = Metagraph().parse(data=metadata)
        self.assertTrue(isomorphic(metagraph,
            widgetsdict.build_metagraph(preserve_metadata_date=True)))
    
    def test_computing_update(self):
        """Mise à jour à partir d'informations calculées.
        
        """
        metadata = """
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix skos: <http://www.w3.org/2004/02/skos/core#> .
            @prefix uuid: <urn:uuid:> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

            uuid:479fd670-32c5-4ade-a26d-0268b0ce5046 a dcat:Dataset ;
                dct:title "ADMIN EXPRESS - Départements de métropole"@fr ;
                dct:conformsTo [ a dct:Standard ;
                    skos:inScheme <http://www.opengis.net/def/crs/EPSG/0> ;
                    dct:identifier "2154" ] ;
                dct:identifier "479fd670-32c5-4ade-a26d-0268b0ce5046" .
            """
        metagraph = Metagraph().parse(data=metadata)
        widgetsdict = WidgetsDict(metagraph=metagraph)
        c = widgetsdict.root.search_from_path(DCT.conformsTo)
        r1g = c.children[0]
        r1v = c.children[1]
        widgetsdict[c]['grid widget'] = '<QGridLayout dct:conformsTo>'
        widgetsdict[c.button]['main widget'] = '<P QToolButton dct:conformsTo>'
        widgetsdict[r1g]['main widget'] = '<r1g QGroupBox dct:conformsTo>'
        widgetsdict[r1g]['minus widget'] = '<r1g-minus QToolButton dct:conformsTo>'
        widgetsdict[r1g]['switch source widget'] = '<r1g-source QToolButton dct:conformsTo>'
        widgetsdict[r1g]['switch source menu'] = '<r1g-source QMenu dct:conformsTo>'
        widgetsdict[r1g]['switch source actions'] = ['<r1g-source QAction n°1', '<r1g-source QAction n°2']
        widgetsdict[r1v]['main widget'] = '<r1v QComboBox dct:conformsTo>'
        widgetsdict[r1v]['minus widget'] = '<r1v-minus QToolButton dct:conformsTo>'
        widgetsdict[r1v]['switch source widget'] = '<r1v-source QToolButton dct:conformsTo>'
        widgetsdict[r1v]['switch source menu'] = '<r1v-source QMenu dct:conformsTo>'
        widgetsdict[r1v]['switch source actions'] = ['<r1v-source QAction n°1', '<r1v-source QAction n°2']
        
        # --- avec une valeur invalide ---
        actionsdict = widgetsdict.computing_update(c, [('EPSG', '0000'), ('EPSG', '2154')])
        self.assertTrue(len(c.children), 4)
        self.assertTrue(o in c.children for o in (r1g, r1v))
        self.assertTrue(r1g.is_main_twin)
        r2g = c.children[2]
        r2v = c.children[3]
        self.assertTrue(isinstance(r2v, ValueKey))
        self.assertTrue(r2v.is_main_twin)
        self.assertEqual(r2v.value, URIRef('http://www.opengis.net/def/crs/EPSG/0/2154'))
        self.assertTrue(all(o in actionsdict['new keys'] for o in (r2v, r2g)))
        self.assertTrue(all(o in (r2v, r2g) or o.generation > r2v.generation for o in actionsdict['new keys']))
        self.assertListEqual(actionsdict['widgets to show'], ['<r1g-minus QToolButton dct:conformsTo>'])
        self.assertListEqual(actionsdict['widgets to move'], [('<QGridLayout dct:conformsTo>',
            '<P QToolButton dct:conformsTo>', 2, 0, 1, 1)])
        for a, l in actionsdict.items():
            with self.subTest(action = a):
                if not a in  ('new keys', 'widgets to show', 'widgets to move'):
                    self.assertFalse(l)
        
        widgetsdict[r2g]['main widget'] = '<r2g QGroupBox dct:conformsTo>'
        widgetsdict[r2g]['minus widget'] = '<r2g-minus QToolButton dct:conformsTo>'
        widgetsdict[r2g]['switch source widget'] = '<r2g-source QToolButton dct:conformsTo>'
        widgetsdict[r2g]['switch source menu'] = '<r2g-source QMenu dct:conformsTo>'
        widgetsdict[r2g]['switch source actions'] = ['<r2g-source QAction n°1', '<r2g-source QAction n°2']
        widgetsdict[r2v]['main widget'] = '<r2v QComboBox dct:conformsTo>'
        widgetsdict[r2v]['minus widget'] = '<r2v-minus QToolButton dct:conformsTo>'
        widgetsdict[r2v]['switch source widget'] = '<r2v-source QToolButton dct:conformsTo>'
        widgetsdict[r2v]['switch source menu'] = '<r2v-source QMenu dct:conformsTo>'
        widgetsdict[r2v]['switch source actions'] = ['<r2v-source QAction n°1', '<r2v-source QAction n°2']
        
        # --- plus de valeurs ---
        actionsdict = widgetsdict.computing_update(c, [('EPSG', '2154'), ('EPSG', '4326')])
        self.assertEqual(len(c.children), 6)
        self.assertTrue(o in c.children for o in (r1g, r1v, r2g, r2v))
        self.assertTrue(r1g.is_main_twin)
        self.assertTrue(r2v.is_main_twin)
        r3g = c.children[4]
        r3v = c.children[5]
        self.assertTrue(isinstance(r3v, ValueKey))
        self.assertTrue(r2v.is_main_twin)
        self.assertTrue(r3v.is_main_twin)
        self.assertEqual(r2v.value, URIRef('http://www.opengis.net/def/crs/EPSG/0/2154'))
        self.assertEqual(r3v.value, URIRef('http://www.opengis.net/def/crs/EPSG/0/4326'))
        self.assertTrue(all(o in actionsdict['new keys'] for o in (r3v, r3g)))
        self.assertTrue(all(o in (r3v, r3g) or o.generation > r3v.generation for o in actionsdict['new keys']))
        self.assertListEqual(actionsdict['value to update'], [r2v])
        self.assertListEqual(actionsdict['widgets to move'], [('<QGridLayout dct:conformsTo>',
            '<P QToolButton dct:conformsTo>', 3, 0, 1, 1)])
        for a, l in actionsdict.items():
            with self.subTest(action = a):
                if not a in  ('new keys', 'value to update', 'widgets to move'):
                    self.assertFalse(l)
        
        widgetsdict[r3g]['main widget'] = '<r3g QGroupBox dct:conformsTo>'
        widgetsdict[r3g]['minus widget'] = '<r3g-minus QToolButton dct:conformsTo>'
        widgetsdict[r3g]['switch source widget'] = '<r3g-source QToolButton dct:conformsTo>'
        widgetsdict[r3g]['switch source menu'] = '<r3g-source QMenu dct:conformsTo>'
        widgetsdict[r3g]['switch source actions'] = ['<r3g-source QAction n°1', '<r3g-source QAction n°2']
        widgetsdict[r3v]['main widget'] = '<r3v QComboBox dct:conformsTo>'
        widgetsdict[r3v]['minus widget'] = '<r3v-minus QToolButton dct:conformsTo>'
        widgetsdict[r3v]['switch source widget'] = '<r3v-source QToolButton dct:conformsTo>'
        widgetsdict[r3v]['switch source menu'] = '<r3v-source QMenu dct:conformsTo>'
        widgetsdict[r3v]['switch source actions'] = ['<r3v-source QAction n°1', '<r3v-source QAction n°2']
        
        # --- autant de valeurs ---
        actionsdict = widgetsdict.computing_update(c, [('EPSG', '2154'), ('EPSG', '2975')])
        self.assertListEqual(c.children, [r1g, r1v, r2g, r2v, r3g, r3v])
        self.assertTrue(r2v.is_main_twin)
        self.assertTrue(r3v.is_main_twin)
        self.assertEqual(r2v.value, URIRef('http://www.opengis.net/def/crs/EPSG/0/2154'))
        self.assertEqual(r3v.value, URIRef('http://www.opengis.net/def/crs/EPSG/0/2975'))
        self.assertListEqual(actionsdict['value to update'], [r2v, r3v])
        for a, l in actionsdict.items():
            with self.subTest(action = a):
                if not a in ('value to update',):
                    self.assertFalse(l)
        
        # --- moins de valeurs ---
        actionsdict = widgetsdict.computing_update(c, [('EPSG', '4326'), ('EPSG', '0000'), ('EPSG', '0000')])
        self.assertListEqual(c.children, [r1g, r1v, r2g, r2v])
        self.assertTrue(r2v.is_main_twin)
        self.assertEqual(r2v.value, URIRef('http://www.opengis.net/def/crs/EPSG/0/4326'))
        self.assertListEqual(actionsdict['value to update'], [r2v])
        self.assertListEqual(actionsdict['widgets to delete'], ['<r3v QComboBox dct:conformsTo>',
            '<r3v-minus QToolButton dct:conformsTo>', '<r3v-source QToolButton dct:conformsTo>',
            '<r3g QGroupBox dct:conformsTo>', '<r3g-minus QToolButton dct:conformsTo>',
            '<r3g-source QToolButton dct:conformsTo>'])
        self.assertListEqual(actionsdict['actions to delete'], ['<r3v-source QAction n°1',
            '<r3v-source QAction n°2', '<r3g-source QAction n°1', '<r3g-source QAction n°2'])
        self.assertListEqual(actionsdict['menus to delete'], ['<r3v-source QMenu dct:conformsTo>',
            '<r3g-source QMenu dct:conformsTo>'])
        self.assertListEqual(actionsdict['widgets to move'], [('<QGridLayout dct:conformsTo>',
            '<P QToolButton dct:conformsTo>', 2, 0, 1, 1)])
        for a, l in actionsdict.items():
            with self.subTest(action = a):
                if not a in  ('value to update', 'widgets to delete', 'actions to delete',
                    'menus to delete', 'widgets to move'):
                    self.assertFalse(l)
        
        # --- aucune valeur ---
        actionsdict = widgetsdict.computing_update(c, [])
        self.assertListEqual(c.children, [r1g, r1v])
        self.assertListEqual(actionsdict['widgets to delete'], ['<r2v QComboBox dct:conformsTo>',
            '<r2v-minus QToolButton dct:conformsTo>', '<r2v-source QToolButton dct:conformsTo>',
            '<r2g QGroupBox dct:conformsTo>', '<r2g-minus QToolButton dct:conformsTo>',
            '<r2g-source QToolButton dct:conformsTo>'])
        self.assertListEqual(actionsdict['actions to delete'], ['<r2v-source QAction n°1',
            '<r2v-source QAction n°2', '<r2g-source QAction n°1', '<r2g-source QAction n°2'])
        self.assertListEqual(actionsdict['menus to delete'], ['<r2v-source QMenu dct:conformsTo>',
            '<r2g-source QMenu dct:conformsTo>'])
        self.assertListEqual(actionsdict['widgets to move'], [('<QGridLayout dct:conformsTo>',
            '<P QToolButton dct:conformsTo>', 1, 0, 1, 1)])
        self.assertListEqual(actionsdict['widgets to hide'], ['<r1g-minus QToolButton dct:conformsTo>'])
        for a, l in actionsdict.items():
            with self.subTest(action = a):
                if not a in ('widgets to hide', 'widgets to delete', 'actions to delete',
                    'menus to delete', 'widgets to move'):
                    self.assertFalse(l)
        
        # --- que des valeurs invalides ---
        actionsdict = widgetsdict.computing_update(c, [('EPSG', '0000'), ('EPSG', '0000')])
        self.assertListEqual(c.children, [r1g, r1v])
        self.assertListEqual(actionsdict['widgets to move'], [('<QGridLayout dct:conformsTo>',
            '<P QToolButton dct:conformsTo>', 1, 0, 1, 1)])
        self.assertListEqual(actionsdict['widgets to hide'], ['<r1g-minus QToolButton dct:conformsTo>'])
        # NB: ce sont des actions inutiles (masquer un widget déjà masqué, "déplacer"
        # un widget sur place), mais le fait est que dans la succession d'actions
        # le widget a réellement été visible et a réellement bougé avant de revenir
        # à sa place. Il paraît admissible que le carnet d'actions ne sache pas dire
        # que l'état final est le même que l'état initial.
        for a, l in actionsdict.items():
            with self.subTest(action = a):
                if not a in ('widgets to hide', 'widgets to move'):
                    self.assertFalse(l)

    def test_computing_update_default_parser(self):
        """Mise à jour à partir d'informations calculées, en utilisant le parser par défaut.
        
        """
        conn = psycopg2.connect(WidgetsDictTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM z_plume.meta_import_sample_template()')
                cur.execute('''
                    UPDATE z_plume.meta_categorie
                        SET compute = ARRAY['manual', 'auto']::z_plume.meta_compute[]
                        WHERE path = 'dct:created' ;
                    ''')
                cur.execute(
                    *query_get_categories('Classique')
                    )
                categories = cur.fetchall()
                cur.execute('DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg')
        conn.close()
        template = TemplateDict(categories)
        metadata = """
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix skos: <http://www.w3.org/2004/02/skos/core#> .
            @prefix uuid: <urn:uuid:> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

            uuid:479fd670-32c5-4ade-a26d-0268b0ce5046 a dcat:Dataset ;
                dct:title "ADMIN EXPRESS - Départements de métropole"@fr ;
                dct:identifier "479fd670-32c5-4ade-a26d-0268b0ce5046" .
            """
        metagraph = Metagraph().parse(data=metadata)
        m = METHODS.get(DCT.created)
        METHODS[DCT.created] = ComputationMethod(query_builder=None,
            parser=default_parser)
        widgetsdict = WidgetsDict(metagraph=metagraph, template=template)
        c = widgetsdict.root.search_from_path(DCT.created)
        actionsdict = widgetsdict.computing_update(c, [('01/01/2020',), ('01/01/2021')])
        self.assertEqual(widgetsdict[c]['value'], '01/01/2020')
        self.assertEqual(c.value, Literal('2020-01-01', datatype=XSD.date))
        self.assertListEqual(actionsdict['value to update'], [c])
        for a, l in actionsdict.items():
            with self.subTest(action = a):
                if not a in ('value to update',):
                    self.assertFalse(l)
        if m:
            METHODS[DCT.created] = m
        else:
            del METHODS[DCT.created]

    def test_compute_conformsto(self):
        """Processus complet de calcul des métadonnées pour dct:conformsTo.
        
        """
        conn = psycopg2.connect(WidgetsDictTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM z_plume.meta_import_sample_template()')
                cur.execute('''
                    UPDATE z_plume.meta_categorie
                        SET compute = ARRAY['manual', 'auto']::z_plume.meta_compute[]
                        WHERE path = 'dct:conformsTo' ;
                    ''')
                cur.execute(
                    *query_get_categories('Classique')
                    )
                categories = cur.fetchall()
                cur.execute('DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg')
        conn.close()
        template = TemplateDict(categories)
        widgetsdict = WidgetsDict(template=template)
        c = widgetsdict.root.search_from_path(DCT.conformsTo)
        self.assertTrue(widgetsdict[c]['has compute button'])
        self.assertTrue(widgetsdict[c]['auto compute'])
        self.assertIsNotNone(widgetsdict[c]['compute method'].description)
        
        # --- dépendances ---
        dependances = widgetsdict[c]['compute method'].dependances
        if dependances:
            conn = psycopg2.connect(WidgetsDictTestCase.connection_string)
            dependances_ok = True
            with conn:
                with conn.cursor() as cur:
                    for extension in dependances:
                        cur.execute(*query_exists_extension(extension))
                        dependances_ok = dependances_ok and cur.fetchone()[0]
                        if not dependances_ok:
                            break
            conn.close()
        self.assertTrue(dependances_ok)
        self.assertEqual(dependances, ['postgis'])
        
        # --- requête ---
        conn = psycopg2.connect(WidgetsDictTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                # création d'une table de test
                cur.execute('''
                    CREATE TABLE z_plume.table_test (
                        geom1 geometry(POINT, 2154),
                        geom3 geometry(POLYGON, 37001),
                        geom4 text,
                        "GEOM 5" geometry(MULTILINESTRING, 4326),
                        geom6 geometry(POLYGON, 2154)
                        ) ;
                    ''')
                query = widgetsdict.computing_query(c, 'z_plume', 'table_test')
                cur.execute(*query)
                result = cur.fetchall()
                cur.execute('DROP TABLE z_plume.table_test')
                # suppression de la table de test
        conn.close()
        self.assertListEqual(
            result,
            [('EPSG', '2154'), ('EPSG', '4326'), ('ESRI', '37001')]
        )
        
        r1g = c.children[0]
        r1v = c.children[1]
        widgetsdict[c]['grid widget'] = '<QGridLayout dct:conformsTo>'
        widgetsdict[c.button]['main widget'] = '<P QToolButton dct:conformsTo>'
        widgetsdict[r1g]['main widget'] = '<r1g QGroupBox dct:conformsTo>'
        widgetsdict[r1g]['minus widget'] = '<r1g-minus QToolButton dct:conformsTo>'
        widgetsdict[r1g]['switch source widget'] = '<r1g-source QToolButton dct:conformsTo>'
        widgetsdict[r1g]['switch source menu'] = '<r1g-source QMenu dct:conformsTo>'
        widgetsdict[r1g]['switch source actions'] = ['<r1g-source QAction n°1', '<r1g-source QAction n°2']
        widgetsdict[r1v]['main widget'] = '<r1v QComboBox dct:conformsTo>'
        widgetsdict[r1v]['minus widget'] = '<r1v-minus QToolButton dct:conformsTo>'
        widgetsdict[r1v]['switch source widget'] = '<r1v-source QToolButton dct:conformsTo>'
        widgetsdict[r1v]['switch source menu'] = '<r1v-source QMenu dct:conformsTo>'
        widgetsdict[r1v]['switch source actions'] = ['<r1v-source QAction n°1', '<r1v-source QAction n°2']
        
        # --- intégration ---
        actionsdict = widgetsdict.computing_update(c, result)
        self.assertEqual(len(c.children), 4)
        r2g = c.children[2]
        r2v = c.children[3]
        self.assertEqual(r1v.value, URIRef('http://www.opengis.net/def/crs/EPSG/0/2154'))
        self.assertEqual(
            r1v.value_source, 
            URIRef('http://registre.data.developpement-durable.gouv.fr/plume/OgcEpsgFrance')
        )
        self.assertEqual(r2v.value, URIRef('http://www.opengis.net/def/crs/EPSG/0/4326'))
        self.assertEqual(
            r2v.value_source, 
            URIRef('http://registre.data.developpement-durable.gouv.fr/plume/OgcEpsgFrance')
        )
        self.assertTrue(all(o in actionsdict['new keys'] for o in (r2v, r2g)))
        self.assertTrue(
            all(o in (r2v, r2g) or o.generation > r2v.generation 
                for o in actionsdict['new keys'])
        )
        self.assertListEqual(actionsdict['widgets to show'], ['<r1v-minus QToolButton dct:conformsTo>'])
        self.assertListEqual(actionsdict['widgets to move'], [('<QGridLayout dct:conformsTo>',
            '<P QToolButton dct:conformsTo>', 2, 0, 1, 1)])
        self.assertListEqual(actionsdict['value to update'], [r1v])
        for a, l in actionsdict.items():
            with self.subTest(action = a):
                if not a in  (
                    'new keys', 'widgets to show', 'widgets to move', 'value to update'
                ):
                    self.assertFalse(l)
        
        metadata = """
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix foaf: <http://xmlns.com/foaf/0.1/> .
            @prefix owl: <http://www.w3.org/2002/07/owl#> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix plume: <http://registre.data.developpement-durable.gouv.fr/plume/> .
            @prefix uuid: <urn:uuid:> .
            @prefix vcard: <http://www.w3.org/2006/vcard/ns#> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

            uuid:{uuid} a dcat:Dataset ;
                dct:conformsTo <http://www.opengis.net/def/crs/EPSG/0/2154>,
                    <http://www.opengis.net/def/crs/EPSG/0/4326> ;
                dct:identifier "{uuid}" .
            """.format(uuid=widgetsdict.datasetid.uuid)
        metagraph = Metagraph().parse(data=metadata)
        self.assertTrue(isomorphic(metagraph,
            widgetsdict.build_metagraph(preserve_metadata_date=True)))
        
        # --- post-sauvegarde ---
        widgetsdict = WidgetsDict(metagraph=widgetsdict.build_metagraph(),
            template=template)
        c = widgetsdict.root.search_from_path(DCT.conformsTo)
        self.assertTrue(widgetsdict[c]['has compute button'])
        self.assertFalse(widgetsdict[c]['auto compute'])
        self.assertIsNotNone(widgetsdict[c]['compute method'])

    def test_compute_conformsto_with_manual_value(self):
        """Calcul des métadonnées pour dct:conformsTo dans le cas où la métadonnée avait une valeur manuelle.

        Le test contrôle l'alimentation automatique lorsque les propriétés
        manuelles sont dans le modèle et hors modèle, en mode lecture et 
        en mode édition.
        
        """
        metadata = """
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix foaf: <http://xmlns.com/foaf/0.1/> .
            @prefix owl: <http://www.w3.org/2002/07/owl#> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix plume: <http://registre.data.developpement-durable.gouv.fr/plume/> .
            @prefix uuid: <urn:uuid:> .
            @prefix vcard: <http://www.w3.org/2006/vcard/ns#> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
            @prefix skos: <http://www.w3.org/2004/02/skos/core#> .

            uuid:aa0e6a49-1ef0-49f7-a3cf-7a759fe000bf a dcat:Dataset ;
                dct:conformsTo [
                    a dct:Standard ;
                    dct:identifier "2154" ;
                    skos:inScheme <http://www.opengis.net/def/crs/EPSG/0>
                ] ;
                dct:identifier "aa0e6a49-1ef0-49f7-a3cf-7a759fe000bf" .
        """
        metagraph = Metagraph().parse(data=metadata)
        conn = psycopg2.connect(WidgetsDictTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute(''' 
                    INSERT INTO z_plume.meta_template (tpl_id, tpl_label) VALUES 
                        (100, 'Compute conformsTo IN'),
                        (200, 'Compute conformsTo OUT') ;
                    INSERT INTO z_plume.meta_template_categories (tpl_id, shrcat_path, compute) VALUES
                        (100, 'dct:conformsTo', ARRAY['auto']),
                        (100, 'dct:conformsTo / dct:identifier', NULL),
                        (100, 'dct:conformsTo / skos:inScheme', NULL),
                        (200, 'dct:conformsTo', ARRAY['auto'])
                ''')
                cur.execute(
                    *query_get_categories('Compute conformsTo IN')
                )
                categories_in = cur.fetchall()
                cur.execute(
                    *query_get_categories('Compute conformsTo OUT')
                )
                categories_out = cur.fetchall()
                cur.execute('DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg')
        conn.close()
        template_in = TemplateDict(categories_in)
        template_out = TemplateDict(categories_out)
        widgetsdict_in_read = WidgetsDict(metagraph=metagraph, template=template_in, mode='read')
        widgetsdict_in_edit = WidgetsDict(metagraph=metagraph, template=template_in, mode='edit')
        widgetsdict_out_read = WidgetsDict(metagraph=metagraph, template=template_out, mode='read')
        widgetsdict_out_edit = WidgetsDict(metagraph=metagraph, template=template_out, mode='edit')
        c_in_read = widgetsdict_in_read.root.search_from_path(DCT.conformsTo)
        c_in_edit = widgetsdict_in_edit.root.search_from_path(DCT.conformsTo)
        c_out_read = widgetsdict_out_read.root.search_from_path(DCT.conformsTo)
        c_out_edit = widgetsdict_out_edit.root.search_from_path(DCT.conformsTo)
        
        # --- requête ---
        conn = psycopg2.connect(WidgetsDictTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                # création d'une table de test
                cur.execute('''
                    CREATE TABLE z_plume.table_test (
                        geom1 geometry(POINT, 2154),
                        "GEOM 2" geometry(POINT, 4326)
                        ) ;
                    ''')
                query = widgetsdict_in_read.computing_query(c_in_read, 'z_plume', 'table_test')
                cur.execute(*query)
                result_in_read = cur.fetchall()
                query = widgetsdict_in_edit.computing_query(c_in_edit, 'z_plume', 'table_test')
                cur.execute(*query)
                result_in_edit = cur.fetchall()
                query = widgetsdict_out_read.computing_query(c_out_read, 'z_plume', 'table_test')
                cur.execute(*query)
                result_out_read = cur.fetchall()
                query = widgetsdict_out_edit.computing_query(c_out_edit, 'z_plume', 'table_test')
                cur.execute(*query)
                result_out_edit = cur.fetchall()
                cur.execute('DROP TABLE z_plume.table_test')
                # suppression de la table de test
        conn.close()
        self.assertListEqual(result_in_read, [('EPSG', '2154'), ('EPSG', '4326')])
        self.assertListEqual(result_in_edit, [('EPSG', '2154'), ('EPSG', '4326')])
        self.assertListEqual(result_out_read, [('EPSG', '2154'), ('EPSG', '4326')])
        self.assertListEqual(result_out_edit, [('EPSG', '2154'), ('EPSG', '4326')])
        
        # --- intégration ---
        widgetsdict_in_read.computing_update(c_in_read, result_in_read)
        widgetsdict_in_edit.computing_update(c_in_edit, result_in_edit)
        widgetsdict_out_read.computing_update(c_out_read, result_out_read)
        widgetsdict_out_edit.computing_update(c_out_edit, result_out_edit)

        # type, is_ghost, is_hidden, twin index, value
        expecting = {
            c_in_read: [
                (GroupOfPropertiesKey, False, False, None),
                (ValueKey, False, False, None, URIRef('http://www.opengis.net/def/crs/EPSG/0/2154')),
                (ValueKey, False, False, None, URIRef('http://www.opengis.net/def/crs/EPSG/0/4326'))
            ],
            c_in_edit: [
                (GroupOfPropertiesKey, False, False, 1),
                (ValueKey, False, True, 0, None),
                (GroupOfPropertiesKey, False, True, 3),
                (ValueKey, False, False, 2, URIRef('http://www.opengis.net/def/crs/EPSG/0/2154')),
                (GroupOfPropertiesKey, False, True, 5),
                (ValueKey, False, False, 4, URIRef('http://www.opengis.net/def/crs/EPSG/0/4326'))
            ],
            c_out_read: [
                (GroupOfPropertiesKey, True, True, None),
                (ValueKey, False, False, None, URIRef('http://www.opengis.net/def/crs/EPSG/0/2154')),
                (ValueKey, False, False, None, URIRef('http://www.opengis.net/def/crs/EPSG/0/4326'))
            ],
            c_out_edit: [
                (GroupOfPropertiesKey, False, False, 1),
                (ValueKey, False, True, 0, None),
                (ValueKey, False, False, None, URIRef('http://www.opengis.net/def/crs/EPSG/0/2154')),
                (ValueKey, False, False, None, URIRef('http://www.opengis.net/def/crs/EPSG/0/4326'))
            ]
        }
        tests = {
            c_in_read: 'in / read',
            c_in_edit: 'in / edit',
            c_out_read: 'out / read',
            c_out_edit: 'out / edit'
        }

        for c, exp in expecting.items():
            with self.subTest(test = tests[c]):
                self.assertTrue(isinstance(c, GroupOfValuesKey))
                self.assertEqual(len(c.children), len(exp), 'children : {}'.format(
                    ', '.join(f'{child} - hidden: {child.is_hidden} - twin: {child.m_twin}' for child in c.children))
                )
                for i in range(len(exp)):
                    with self.subTest(child_index = i):
                        self.assertTrue(isinstance(c.children[i], exp[i][0]), f'children : {c.children}')
                        self.assertEqual(c.children[i].is_ghost, exp[i][1], f'children : {c.children}')
                        self.assertEqual(c.children[i].is_hidden, exp[i][2], f'children : {c.children}')
                        if exp[i][3] is not None:
                            self.assertEqual(c.children[i].m_twin, c.children[exp[i][3]], f'children : {c.children}')
                        else:
                            self.assertIsNone(c.children[i].m_twin, f'children : {c.children}')
                        if exp[i][0] == ValueKey:
                            self.assertEqual(c.children[i].value, exp[i][4], f'children : {c.children}')
        
        for c, widgetsdict, expecting in [
            (c_in_read, widgetsdict_in_read, [(False, None)]*3),
            (c_in_edit, widgetsdict_in_edit, [(True, True)]*6),
            (c_out_read, widgetsdict_out_read, [(False, None)]*3),
            (
                c_out_edit,
                widgetsdict_out_edit,
                [
                    (True, True),
                    (True, True),
                    (True, False),
                    (True, False)
                ]
            )
        ]:
            with self.subTest(test = tests[c]):
                for i in range(len(expecting)):
                    with self.subTest(child_index = i):
                        if not c.children[i]:
                            self.assertFalse(c.children[i] in widgetsdict)
                            continue
                        self.assertEqual(
                            widgetsdict[c.children[i]]['multiple sources'],
                            expecting[i][0]
                        )
                        if expecting[i][0]:
                            self.assertEqual(
                                SourceLabels.MANUAL.trans(widgetsdict.langlist) in widgetsdict[c.children[i]]['sources'],
                                expecting[i][1]
                            )

    def test_local_template(self):
        """Génération du dictionnaire avec un modèle local et non issu de PlumePg.
        
        """
        templates_collection = LocalTemplatesCollection()
        metadata = """
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix foaf: <http://xmlns.com/foaf/0.1/> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix uuid: <urn:uuid:> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

            uuid:479fd670-32c5-4ade-a26d-0268b0ce5046 a dcat:Dataset ;
                dct:accessRights [ a dct:RightsStatement ;
                    rdfs:label "Aucune restriction d'accès ou d'usage."@fr ] ;
                dct:creator [ a foaf:Agent ;
                    foaf:name "IGN"@fr ] ;
                dct:title "ADMIN EXPRESS - Départements de métropole"@fr,
                    "ADMIN EXPRESS - Metropolitan Departments"@en;
                dcat:keyword "admin express"@fr,
                    "donnée externe"@fr,
                    "external data"@en,
                    "ign"@fr ;
                dct:temporal [ a dct:PeriodOfTime ;
                    dcat:endDate "2021-01-15"^^xsd:date ;
                    dcat:startDate "2021-01-15"^^xsd:date ] ;
                dcat:theme <http://inspire.ec.europa.eu/theme/au> ;
                dct:identifier "479fd670-32c5-4ade-a26d-0268b0ce5046" ;
                uuid:218c1245-6ba7-4163-841e-476e0d5582af "À mettre à jour !"@fr .
            """
        metagraph = Metagraph().parse(data=metadata)
        widgetsdict = WidgetsDict(metagraph=metagraph,
            template=templates_collection['Basique'])
        self.assertTrue(isomorphic(metagraph,
            widgetsdict.build_metagraph(preserve_metadata_date=True)))   

    def test_compute_description(self):
        """Processus complet de calcul des métadonnées pour dct:description.
        
        Avec le mode ``'empty'`` pour le calcul automatique,
        hors mode traduction (le calcul porte donc sur une
        clé-valeur).
        
        """
        conn = psycopg2.connect(WidgetsDictTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM z_plume.meta_import_sample_template()')
                cur.execute('''
                    UPDATE z_plume.meta_categorie
                        SET compute = ARRAY['manual', 'empty']::z_plume.meta_compute[]
                        WHERE path = 'dct:description' ;
                    ''')
                cur.execute(
                    *query_get_categories('Classique')
                    )
                categories = cur.fetchall()
                cur.execute('DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg')
        conn.close()
        template = TemplateDict(categories)
        widgetsdict = WidgetsDict(template=template)
        c = widgetsdict.root.search_from_path(DCT.description)
        self.assertTrue(widgetsdict[c]['has compute button'])
        self.assertTrue(widgetsdict[c]['auto compute'])
        self.assertIsNotNone(widgetsdict[c]['compute method'].description)

        # --- dépendances ---
        dependances = widgetsdict[c]['compute method'].dependances
        if dependances:
            conn = psycopg2.connect(WidgetsDictTestCase.connection_string)
            dependances_ok = True
            with conn:
                with conn.cursor() as cur:
                    for extension in dependances:
                        cur.execute(*query_exists_extension(extension))
                        dependances_ok = dependances_ok and cur.fetchone()[0]
                        if not dependances_ok:
                            break
            conn.close()
        self.assertTrue(dependances_ok)
        self.assertEqual(dependances, ['plume_pg'])
        
        # --- requête ---
        conn = psycopg2.connect(WidgetsDictTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                # création d'une table de test
                cur.execute('''
                    CREATE TABLE z_plume.table_test () ;
                    COMMENT ON TABLE z_plume.table_test IS 'Ceci est une description.' ;
                    ''')
                query = widgetsdict.computing_query(c, 'z_plume', 'table_test')
                cur.execute(*query)
                result = cur.fetchall()
                cur.execute('DROP TABLE z_plume.table_test')
                # suppression de la table de test
        conn.close()
        self.assertListEqual(result, [('Ceci est une description.',)])
        
        widgetsdict[c]['main widget'] = '<c QTextEdit dct:description>'
        widgetsdict[c]['compute widget'] = '<c-compute QToolButton dct:description>'
        
        # --- intégration ---
        actionsdict = widgetsdict.computing_update(c, result)
        self.assertEqual(c.value, Literal('Ceci est une description.', lang='fr'))
        self.assertEqual(actionsdict['value to update'], [c])
        for a, l in actionsdict.items():
            with self.subTest(action = a):
                if not a == 'value to update':
                    self.assertFalse(l)

        metadata = """
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix uuid: <urn:uuid:> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

            uuid:{uuid} a dcat:Dataset ;
                dct:description "Ceci est une description."@fr ;
                dct:identifier "{uuid}" .
            """.format(uuid=widgetsdict.datasetid.uuid)
        metagraph = Metagraph().parse(data=metadata)
        self.assertTrue(isomorphic(metagraph,
            widgetsdict.build_metagraph(preserve_metadata_date=True)))
        
        # --- champ non vide ---
        widgetsdict = WidgetsDict(metagraph=metagraph,
            template=template)
        d = widgetsdict.root.search_from_path(DCT.description)
        self.assertTrue(widgetsdict[d]['has compute button'])
        self.assertFalse(widgetsdict[d]['auto compute'])
        self.assertIsNotNone(widgetsdict[d]['compute method'])
        
        # --- post-sauvegarde ---
        widgetsdict.update_value(d, '')
        self.assertIsNone(d.value)
        metagraph = widgetsdict.build_metagraph()
        widgetsdict = WidgetsDict(metagraph=metagraph,
            template=template)
        c = widgetsdict.root.search_from_path(DCT.description)
        self.assertTrue(widgetsdict[c]['has compute button'])
        self.assertFalse(widgetsdict[c]['auto compute'])
        self.assertIsNotNone(widgetsdict[c]['compute method'])
        
        metagraph.fresh = True
        widgetsdict = WidgetsDict(metagraph=metagraph,
            template=template)
        c = widgetsdict.root.search_from_path(DCT.description)
        self.assertTrue(widgetsdict[c]['has compute button'])
        self.assertTrue(widgetsdict[c]['auto compute'])
        self.assertIsNotNone(widgetsdict[c]['compute method'])

    def test_compute_title(self):
        """Processus complet de calcul des métadonnées pour dct:title.
        
        Avec le mode ``'new'`` pour le calcul automatique, 
        avec une expression régulière (renvoyant plusieurs
        valeurs) + flags, en mode traduction.
        
        """
        conn = psycopg2.connect(WidgetsDictTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM z_plume.meta_import_sample_template()')
                cur.execute(r'''
                    UPDATE z_plume.meta_categorie
                        SET compute = ARRAY['new']::z_plume.meta_compute[],
                            compute_params = '{"pattern": "(t(?:\\s|\\w)+)[.]", "flags": "gi"}'::jsonb
                        WHERE path = 'dct:title' ;
                    ''')
                cur.execute(
                    *query_get_categories('Classique')
                    )
                categories = cur.fetchall()
                cur.execute('DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg')
        conn.close()
        template = TemplateDict(categories)
        widgetsdict = WidgetsDict(template=template, translation=True)
        c = widgetsdict.root.search_from_path(DCT.title)
        self.assertFalse(widgetsdict[c]['has compute button'])
        self.assertTrue(widgetsdict[c]['auto compute'])
        self.assertIsNotNone(widgetsdict[c]['compute method'].description)
        
        # --- dépendances ---
        dependances = widgetsdict[c]['compute method'].dependances
        if dependances:
            conn = psycopg2.connect(WidgetsDictTestCase.connection_string)
            dependances_ok = True
            with conn:
                with conn.cursor() as cur:
                    for extension in dependances:
                        cur.execute(*query_exists_extension(extension))
                        dependances_ok = dependances_ok and cur.fetchone()[0]
                        if not dependances_ok:
                            break
            conn.close()
        self.assertTrue(dependances_ok)
        self.assertEqual(dependances, ['plume_pg'])
        
        # --- requête ---
        conn = psycopg2.connect(WidgetsDictTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                # création d'une table de test
                cur.execute('''
                    CREATE TABLE z_plume.table_test () ;
                    COMMENT ON TABLE z_plume.table_test IS 'Titre 1. Titre 2.
                        t<METADATA> blabla </METADATA>. Titre 3.' ;
                    ''')
                query = widgetsdict.computing_query(c, 'z_plume', 'table_test')
                cur.execute(*query)
                result = cur.fetchall()
                cur.execute('DROP TABLE z_plume.table_test')
                # suppression de la table de test
        conn.close()
        self.assertListEqual(result, [('Titre 1',), ('Titre 2',), ('Titre 3',)])
        
        widgetsdict[c]['grid widget'] = '<c QGridLayout dct:description>'
        widgetsdict[c]['compute widget'] = '<c-compute QToolButton dct:description>'
        d = c.children[0]
        widgetsdict[d]['main widget'] = '<d QTextEdit dct:description>'
        widgetsdict[d]['minus widget'] = '<d-minus QToolButton dct:description>'
        widgetsdict[d]['language widget'] = '<d-language QToolButton dct:description>'
        widgetsdict[d]['language menu'] = '<d-language QMenu dct:description>'
        widgetsdict[d]['language actions'] = ['<d-language QAction n°1', '<d-language QAction n°2']
        
        # --- intégration ---
        actionsdict = widgetsdict.computing_update(c, result)
        self.assertEqual(len(c.children), 1)
        self.assertEqual(d.value, Literal('Titre 1', lang='fr'))
        self.assertEqual(actionsdict['value to update'], [d])
        for a, l in actionsdict.items():
            with self.subTest(action = a):
                if not a == 'value to update':
                    self.assertFalse(l)
        
        metadata = """
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix uuid: <urn:uuid:> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

            uuid:{uuid} a dcat:Dataset ;
                dct:title "Titre 1"@fr ;
                dct:identifier "{uuid}" .
            """.format(uuid=widgetsdict.datasetid.uuid)
        metagraph = Metagraph().parse(data=metadata)
        self.assertTrue(isomorphic(metagraph,
            widgetsdict.build_metagraph(preserve_metadata_date=True)))
        
        # --- champ non vide ---
        widgetsdict = WidgetsDict(metagraph=metagraph,
            template=template)
        d = widgetsdict.root.search_from_path(DCT.title)
        self.assertFalse(widgetsdict[d]['has compute button'])
        self.assertFalse(widgetsdict[d]['auto compute'])
        self.assertIsNone(widgetsdict[d]['compute method'])
        
        # --- post-sauvegarde ---
        widgetsdict.update_value(d, '')
        self.assertIsNone(d.value)
        metagraph = widgetsdict.build_metagraph()
        widgetsdict = WidgetsDict(metagraph=metagraph,
            template=template)
        c = widgetsdict.root.search_from_path(DCT.title)
        self.assertFalse(widgetsdict[c]['has compute button'])
        self.assertFalse(widgetsdict[c]['auto compute'])
        self.assertIsNone(widgetsdict[c]['compute method'])
        
        metagraph.fresh = True
        widgetsdict = WidgetsDict(metagraph=metagraph,
            template=template)
        c = widgetsdict.root.search_from_path(DCT.title)
        self.assertFalse(widgetsdict[c]['has compute button'])
        self.assertTrue(widgetsdict[c]['auto compute'])
        self.assertIsNotNone(widgetsdict[c]['compute method'])
        
        # --- graphe non vide ---
        # mais sans dct:title
        metadata = """
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix uuid: <urn:uuid:> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

            uuid:{uuid} a dcat:Dataset ;
                dct:description "Ceci est une description."@fr ;
                dct:identifier "{uuid}" .
            """.format(uuid=widgetsdict.datasetid.uuid)
        metagraph = Metagraph().parse(data=metadata)
        widgetsdict = WidgetsDict(metagraph=metagraph,
            template=template)
        c = widgetsdict.root.search_from_path(DCT.title)
        self.assertFalse(widgetsdict[c]['has compute button'])
        self.assertFalse(widgetsdict[c]['auto compute'])
        self.assertIsNone(widgetsdict[c]['compute method'])
    
    def test_manual_compute_title_multivalues(self):
        """Processus complet de calcul des métadonnées pour dct:title.
        
        Activation manuelle du calcul dans le cas où le mode traduction est
        inactif alors que des traductions avaient été préalablement saisies.
        
        """
        metadata = """
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix uuid: <urn:uuid:> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

            uuid:479fd670-32c5-4ade-a26d-0268b0ce5046 a dcat:Dataset ;
                dct:title "Un titre en français"@fr,
                    "An English Title" .
            """
        metagraph = Metagraph().parse(data=metadata)

        conn = psycopg2.connect(WidgetsDictTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM z_plume.meta_import_sample_template()')
                cur.execute(r'''
                    UPDATE z_plume.meta_categorie
                        SET compute = ARRAY['manual'],
                            compute_params = '{"pattern": "\\s*([^.]+)\\s*[.]", "flags": "g"}'::jsonb
                        WHERE path = 'dct:title' ;
                    ''')
                cur.execute(
                    *query_get_categories('Classique')
                    )
                categories = cur.fetchall()
                cur.execute('DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg')
        conn.close()
        template = TemplateDict(categories)
        widgetsdict = WidgetsDict(metagraph=metagraph, template=template, translation=False)
        c = widgetsdict.root.search_from_path(DCT.title)
        self.assertTrue(widgetsdict[c]['has compute button'])
        self.assertFalse(widgetsdict[c]['auto compute'])
        self.assertIsNotNone(widgetsdict[c]['compute method'].description)

        # --- dépendances ---
        dependances = widgetsdict[c]['compute method'].dependances
        if dependances:
            conn = psycopg2.connect(WidgetsDictTestCase.connection_string)
            dependances_ok = True
            with conn:
                with conn.cursor() as cur:
                    for extension in dependances:
                        cur.execute(*query_exists_extension(extension))
                        dependances_ok = dependances_ok and cur.fetchone()[0]
                        if not dependances_ok:
                            break
            conn.close()
        self.assertTrue(dependances_ok)
        self.assertEqual(dependances, ['plume_pg'])
        
        # --- requête ---
        conn = psycopg2.connect(WidgetsDictTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                # création d'une table de test
                cur.execute('''
                    CREATE TABLE z_plume.table_test () ;
                    COMMENT ON TABLE z_plume.table_test IS 'Autre titre. Blobliblu. <METADATA> blabla </METADATA> Blubliblo' ;
                    ''')
                query = widgetsdict.computing_query(c, 'z_plume', 'table_test')
                cur.execute(*query)
                result = cur.fetchall()
                cur.execute('DROP TABLE z_plume.table_test')
                # suppression de la table de test
        conn.close()
        self.assertListEqual(result, [('Autre titre',), ('Blobliblu',)])
        
        widgetsdict[c]['grid widget'] = '<c QGridLayout dct:description>'
        widgetsdict[c]['compute widget'] = '<c-compute QToolButton dct:description>'
        d = c.children[0]
        widgetsdict[d]['main widget'] = '<d QTextEdit dct:description>'
        self.assertTrue(widgetsdict[d]['has minus button'])
        widgetsdict[d]['minus widget'] = '<d-minus QToolButton dct:description>'
        self.assertFalse(widgetsdict[d]['authorized languages'])
        
        # --- intégration ---
        actionsdict = widgetsdict.computing_update(c, result)
        self.assertEqual(len(c.children), 1)
        self.assertEqual(d.value, Literal('Autre titre', lang='fr'))
        self.assertEqual(actionsdict['value to update'], [d])
        self.assertEqual(actionsdict['widgets to hide'], ['<d-minus QToolButton dct:description>'])
        for a, l in actionsdict.items():
            with self.subTest(action = a):
                if not a in ('value to update', 'widgets to hide'):
                    self.assertFalse(l)
        
        metadata = """
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix uuid: <urn:uuid:> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

            uuid:{uuid} a dcat:Dataset ;
                dct:title "Autre titre"@fr ;
                dct:identifier "{uuid}" .
            """.format(uuid=widgetsdict.datasetid.uuid)
        metagraph = Metagraph().parse(data=metadata)
        self.assertTrue(isomorphic(metagraph,
            widgetsdict.build_metagraph(preserve_metadata_date=True)))

    def test_compute_modified_created(self):
        """Processus complet de calcul des métadonnées pour dct:modified et dct:created.
        
        Le calcul est fait avec un rôle sans
        aucun privilège.
        
        """
        conn = psycopg2.connect(WidgetsDictTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('''
                    SELECT * FROM z_plume.meta_import_sample_template() ;
                    UPDATE z_plume.meta_categorie
                        SET compute = ARRAY['auto']::z_plume.meta_compute[]
                        WHERE path = 'dct:modified' ;
                    UPDATE z_plume.meta_categorie
                        SET compute = ARRAY['manual', 'new']::z_plume.meta_compute[]
                        WHERE path = 'dct:created' ;
                    ''')
                cur.execute(
                    *query_get_categories('Classique')
                    )
                categories = cur.fetchall()
                cur.execute('DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg')
        conn.close()
        template = TemplateDict(categories)
        widgetsdict = WidgetsDict(template=template)
        cc = widgetsdict.root.search_from_path(DCT.created)
        cm = widgetsdict.root.search_from_path(DCT.modified)
        self.assertTrue(widgetsdict[cc]['has compute button'])
        self.assertTrue(widgetsdict[cc]['auto compute'])
        self.assertIsNotNone(widgetsdict[cc]['compute method'].description)
        self.assertFalse(widgetsdict[cm]['has compute button'])
        self.assertTrue(widgetsdict[cm]['auto compute'])
        self.assertIsNotNone(widgetsdict[cm]['compute method'].description)
        
        # --- dépendances ---
        dependances = widgetsdict[cm]['compute method'].dependances
        if dependances:
            conn = psycopg2.connect(WidgetsDictTestCase.connection_string)
            dependances_ok = True
            with conn:
                with conn.cursor() as cur:
                    for extension in dependances:
                        cur.execute(*query_exists_extension(extension))
                        dependances_ok = dependances_ok and cur.fetchone()[0]
                        if not dependances_ok:
                            break
            conn.close()
        self.assertTrue(dependances_ok)
        self.assertEqual(dependances, ['plume_pg'])
        self.assertEqual(widgetsdict[cc]['compute method'].dependances, ['plume_pg'])
        
        # --- requête ---
        conn = psycopg2.connect(WidgetsDictTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                # création d'une table de test
                cur.execute('''
                    ALTER EVENT TRIGGER plume_stamp_table_creation ENABLE ;
                    ALTER EVENT TRIGGER plume_stamp_table_modification ENABLE ;
                    ALTER EVENT TRIGGER plume_stamp_table_drop ENABLE ;
                    CREATE TABLE z_plume.table_test_x () ;
                    ALTER TABLE z_plume.table_test_x RENAME TO table_test ;
                    CREATE ROLE g_compute_test ;
                    SET ROLE g_compute_test ;
                    ''')
                query_c = widgetsdict.computing_query(cc, 'z_plume', 'table_test')
                query_m = widgetsdict.computing_query(cm, 'z_plume', 'table_test')
                cur.execute(*query_c)
                result_c = cur.fetchall()
                cur.execute(*query_m)
                result_m = cur.fetchall()
                cur.execute('''
                    RESET ROLE ;
                    DROP TABLE z_plume.table_test ;
                    DROP ROLE g_compute_test ;
                    TRUNCATE z_plume.stamp_timestamp ;
                    ALTER EVENT TRIGGER plume_stamp_table_drop DISABLE ;
                    ALTER EVENT TRIGGER plume_stamp_table_modification DISABLE ;
                    ALTER EVENT TRIGGER plume_stamp_table_creation DISABLE ;
                    ''')
        conn.close()
        self.assertTrue(isinstance(result_c[0][0], datetime))
        self.assertTrue(isinstance(result_m[0][0], datetime))
        
        widgetsdict[cc]['main widget'] = '<cc QTextEdit dct:created>'
        widgetsdict[cc]['compute widget'] = '<cc-compute QToolButton dct:created>'
        widgetsdict[cm]['main widget'] = '<cm QTextEdit dct:modified>'
        widgetsdict[cm]['compute widget'] = '<cm-compute QToolButton dct:modified>'
        
        # --- intégration ---
        actionsdict_c = widgetsdict.computing_update(cc, result_c)
        self.assertIsNotNone(cc.value)
        self.assertTrue(isinstance(cc.value.toPython(), date))
        self.assertTrue(re.match(
            r'[0-9]{2}/[0-9]{2}/[0-9]{2}',
            widgetsdict[cc]['value']
            ))
        self.assertEqual(actionsdict_c['value to update'], [cc])
        for a, l in actionsdict_c.items():
            with self.subTest(action = a):
                if not a == 'value to update':
                    self.assertFalse(l)
        
        actionsdict_m = widgetsdict.computing_update(cm, result_m)
        self.assertIsNotNone(cm.value)
        self.assertTrue(isinstance(cm.value.toPython(), date))
        self.assertTrue(re.match(
            r'[0-9]{2}/[0-9]{2}/[0-9]{2}',
            widgetsdict[cm]['value']
            ))
        self.assertEqual(actionsdict_m['value to update'], [cm])
        for a, l in actionsdict_m.items():
            with self.subTest(action = a):
                if not a == 'value to update':
                    self.assertFalse(l)

    def test_columns(self):
        """Intégration des descriptifs des champs.
        
        """
        columns = [('Champ 1', 'Descriptif'), ('Champ 2', None)]
        widgetsdict = WidgetsDict(columns=columns)
        w = widgetsdict.root.search_from_path(PLUME.column)
        g = w.parent
        self.assertEqual(len(columns), len(g.children))
        for k in columns.copy():
            if any(k[0] == widgetsdict[c]['label'] 
                and k[1] == widgetsdict[c]['value']
                for c in g.children):
                columns.remove(k)
        self.assertFalse(columns)

    def test_modified(self):
        """Attribut traçant les modifications sur les clés.
        
        """
        metadata = """
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix uuid: <urn:uuid:> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

            uuid:479fd670-32c5-4ade-a26d-0268b0ce5046 a dcat:Dataset ;
                dct:accessRights [ a dct:RightsStatement ;
                    rdfs:label "Aucune restriction d'accès ou d'usage."@fr ] ;
                dct:title "ADMIN EXPRESS - Départements de métropole"@fr,
                    "ADMIN EXPRESS - Metropolitan Departments"@en;
                dcat:keyword "admin express"@fr,
                    "donnée externe"@fr,
                    "external data"@en,
                    "ign"@fr ;
                dct:temporal [ a dct:PeriodOfTime ;
                    dcat:endDate "2021-01-15"^^xsd:date ;
                    dcat:startDate "2021-01-15"^^xsd:date ] ;
                dcat:theme <http://inspire.ec.europa.eu/theme/au> ;
                dct:identifier "479fd670-32c5-4ade-a26d-0268b0ce5046" ;
                uuid:218c1245-6ba7-4163-841e-476e0d5582af "À mettre à jour !"@fr .
            """
        metagraph = Metagraph().parse(data=metadata)
        # add
        widgetsdict = WidgetsDict(metagraph=metagraph)
        self.assertFalse(widgetsdict.modified)
        w = widgetsdict.root.search_from_path(DCAT.keyword)
        widgetsdict.add(w.button)
        self.assertTrue(widgetsdict.modified)
        ## drop
        widgetsdict = WidgetsDict(metagraph=metagraph)
        w = widgetsdict.root.search_from_path(DCAT.keyword).children[0]
        widgetsdict.drop(w)
        self.assertTrue(widgetsdict.modified)
        # change_language
        widgetsdict = WidgetsDict(metagraph=metagraph, translation=True)
        self.assertFalse(widgetsdict.modified)
        w = widgetsdict.root.search_from_path(DCAT.keyword).children[0]
        widgetsdict.change_language(w, 'en')
        self.assertTrue(widgetsdict.modified)
        # change_source
        widgetsdict = WidgetsDict(metagraph=metagraph)
        w = widgetsdict.root.search_from_path(DCAT.theme).children[0]
        widgetsdict.change_source(w, 'Thème de données (UE)')
        self.assertTrue(widgetsdict.modified)
        # computing_update
        widgetsdict = WidgetsDict(metagraph=metagraph)
        w = widgetsdict.root.search_from_path(DCT.conformsTo)
        widgetsdict.computing_update(w, [('EPSG', '2154')])
        self.assertTrue(widgetsdict.modified)
        # change_unit
        widgetsdict = WidgetsDict(metagraph=metagraph)
        w = widgetsdict.root.search_from_path(DCAT.temporalResolution)
        widgetsdict.change_unit(w, 'min.')
        self.assertTrue(widgetsdict.modified)

    def test_is_read_only(self):
        """Catégories en lecture seule.
        
        """
        conn = psycopg2.connect(WidgetsDictTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    '''
                    SELECT * FROM z_plume.meta_import_sample_template('Donnée externe') ;
                    '''
                )
                cur.execute(
                    '''
                    SELECT tpl_id FROM z_plume.meta_template
                        WHERE tpl_label = 'Donnée externe' ;
                    '''
                )
                tpl_id = cur.fetchone()[0]
                cur.execute(
                    '''
                    INSERT INTO z_plume.meta_template_categories
                        (shrcat_path, tpl_id) VALUES
                        ('dct:spatial / dcat:bbox', %(tpl_id)s),
                        ('dct:conformsTo', %(tpl_id)s),
                        ('dcat:temporalResolution', %(tpl_id)s) ;
                    UPDATE z_plume.meta_template_categories
                        SET is_read_only = True
                        WHERE tpl_id = %(tpl_id)s
                            AND shrcat_path IN ('dcat:distribution',
                                'dcat:keyword', 'dcat:theme',
                                'dct:spatial / dcat:bbox',
                                'dcat:temporalResolution', 'dct:title',
                                'dct:conformsTo') ;
                    ''',
                    {'tpl_id': tpl_id}
                )
                cur.execute(
                    *query_get_categories('Donnée externe')
                )
                categories = cur.fetchall()
                cur.execute('DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg')
        conn.close()
        template = TemplateDict(categories)
        metadata = """
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix uuid: <urn:uuid:> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

            uuid:479fd670-32c5-4ade-a26d-0268b0ce5046 a dcat:Dataset ;
                dct:accessRights [ a dct:RightsStatement ;
                    rdfs:label "Aucune restriction d'accès ou d'usage."@fr ] ;
                dct:title "ADMIN EXPRESS - Départements de métropole"@fr,
                    "ADMIN EXPRESS - Metropolitan Departments"@en;
                dcat:keyword "admin express"@fr,
                    "donnée externe"@fr,
                    "external data"@en,
                    "ign"@fr ;
                dct:temporal [ a dct:PeriodOfTime ;
                    dcat:endDate "2021-01-15"^^xsd:date ;
                    dcat:startDate "2021-01-15"^^xsd:date ] ;
                dcat:theme <http://inspire.ec.europa.eu/theme/au> ;
                dct:identifier "479fd670-32c5-4ade-a26d-0268b0ce5046" ;
                dcat:distribution [ a dcat:Distribution ;
                    dcat:packageFormat <http://publications.europa.eu/resource/authority/file-type/ZIP> ;
                    dct:license [ a dct:LicenseDocument ;
                        rdfs:label "Licence ouverte Etalab 2.0"@fr ] ] ;
                uuid:218c1245-6ba7-4163-841e-476e0d5582af "À mettre à jour !"@fr .
            """
        metagraph = Metagraph().parse(data=metadata)
        widgetsdict = WidgetsDict(metagraph=metagraph, template=template,
            translation=True, langList=('fr', 'en', 'it'))
        widgetsdict_witness = WidgetsDict(metagraph=metagraph, translation=True,
            langList=('fr', 'en', 'it'))
        # dcat:keyword (groupe de valeurs)
        w = widgetsdict.root.search_from_path(DCAT.keyword)
        ww = widgetsdict_witness.root.search_from_path(DCAT.keyword)
        self.assertTrue(w.is_read_only)
        self.assertFalse(ww.is_read_only)
        self.assertTrue(all(widgetsdict[c]['read only'] for c in w.children))
        self.assertTrue(not any(widgetsdict_witness[c]['read only'] for c in ww.children))
        self.assertTrue(w.button)
        self.assertTrue(w.button.is_hidden_b)
        self.assertTrue(widgetsdict[w.button]['hidden'])
        self.assertTrue(ww.button)
        self.assertFalse(ww.button.is_hidden_b)
        self.assertFalse(widgetsdict_witness[ww.button]['hidden'])
        self.assertTrue(not any(widgetsdict[c]['has minus button'] for c in w.children))
        self.assertTrue(all(widgetsdict_witness[c]['has minus button'] for c in ww.children))
        # dct:conformsTo (bouton de calcul)
        w = widgetsdict.root.search_from_path(DCT.conformsTo)
        ww = widgetsdict_witness.root.search_from_path(DCT.conformsTo)
        self.assertTrue(w.is_read_only)
        self.assertFalse(ww.is_read_only)
        self.assertTrue(all(widgetsdict[c]['read only'] for c in w.children))
        self.assertTrue(not any(widgetsdict_witness[c]['read only'] for c in ww.children))
        self.assertTrue(w.button)
        self.assertTrue(w.button.is_hidden_b)
        self.assertTrue(widgetsdict[w.button]['hidden'])
        self.assertTrue(ww.button)
        self.assertFalse(ww.button.is_hidden_b)
        self.assertFalse(widgetsdict_witness[ww.button]['hidden'])
        self.assertTrue(not any(widgetsdict[c]['has minus button'] for c in w.children))
        self.assertTrue(all(widgetsdict_witness[c]['has minus button'] for c in ww.children))
        self.assertFalse(widgetsdict[w]['has compute button'])
        self.assertTrue(widgetsdict_witness[ww]['has compute button'])
        # dcat:theme (plusieurs sources)
        w = widgetsdict.root.search_from_path(DCAT.theme)
        ww = widgetsdict_witness.root.search_from_path(DCAT.theme)
        self.assertTrue(w.is_read_only)
        self.assertFalse(ww.is_read_only)
        self.assertTrue(all(widgetsdict[c]['read only'] for c in w.children))
        self.assertTrue(not any(widgetsdict_witness[c]['read only'] for c in ww.children))
        self.assertTrue(w.button)
        self.assertTrue(w.button.is_hidden_b)
        self.assertTrue(widgetsdict[w.button]['hidden'])
        self.assertTrue(ww.button)
        self.assertFalse(ww.button.is_hidden_b)
        self.assertFalse(widgetsdict_witness[ww.button]['hidden'])
        self.assertTrue(not any(widgetsdict[c]['multiple sources'] for c in w.children))
        self.assertTrue(all(widgetsdict_witness[c]['multiple sources'] for c in ww.children))
        # dct:title (groupe de traduction)
        w = widgetsdict.root.search_from_path(DCT.title)
        ww = widgetsdict_witness.root.search_from_path(DCT.title)
        self.assertTrue(w.is_read_only)
        self.assertFalse(ww.is_read_only)
        self.assertTrue(all(widgetsdict[c]['read only'] for c in w.children))
        self.assertTrue(not any(widgetsdict_witness[c]['read only'] for c in ww.children))
        self.assertTrue(w.button)
        self.assertTrue(w.button.is_hidden_b)
        self.assertTrue(widgetsdict[w.button]['hidden'])
        self.assertTrue(ww.button)
        self.assertFalse(ww.button.is_hidden_b)
        self.assertFalse(widgetsdict_witness[ww.button]['hidden'])
        self.assertTrue(not any(widgetsdict[c]['authorized languages'] for c in w.children))
        self.assertTrue(all(widgetsdict_witness[c]['authorized languages'] for c in ww.children))
        self.assertTrue(not any(widgetsdict[c]['has minus button'] for c in w.children))
        self.assertTrue(all(widgetsdict_witness[c]['has minus button'] for c in ww.children))
        # dcat:temporalResolution (bouton de changement d'unité)
        w = widgetsdict.root.search_from_path(DCAT.temporalResolution)
        ww = widgetsdict_witness.root.search_from_path(DCAT.temporalResolution)
        self.assertTrue(widgetsdict[w]['read only'])
        self.assertFalse(widgetsdict_witness[ww]['read only'])
        self.assertFalse(widgetsdict[w]['units'])
        self.assertTrue(widgetsdict_witness[ww]['units'])
        # dcat:bbox (bouton d'aide à la saisie des géométries)
        w = widgetsdict.root.search_from_path(DCT.spatial / DCAT.bbox)
        ww = widgetsdict_witness.root.search_from_path(DCT.spatial / DCAT.bbox)
        self.assertTrue(widgetsdict[w]['read only'])
        self.assertFalse(widgetsdict_witness[ww]['read only'])
        self.assertEqual(widgetsdict[w]['geo tools'], ['show'])
        self.assertTrue('bbox' in widgetsdict_witness[ww]['geo tools'])
        # dcat:distribution (héritage dans un groupe de propriétés)
        w = widgetsdict.root.search_from_path(DCAT.distribution)
        ww = widgetsdict_witness.root.search_from_path(DCAT.distribution)
        self.assertTrue(w.is_read_only)
        self.assertFalse(ww.is_read_only)
        w = widgetsdict.root.search_from_path(DCAT.distribution / DCT.issued)
        ww = widgetsdict_witness.root.search_from_path(DCAT.distribution / DCT.issued)
        self.assertTrue(widgetsdict[w]['read only'])
        self.assertFalse(widgetsdict_witness[ww]['read only'])
        w = widgetsdict.root.search_from_path(DCAT.distribution / DCAT.packageFormat)
        ww = widgetsdict_witness.root.search_from_path(DCAT.distribution / DCAT.packageFormat)
        self.assertTrue(widgetsdict[w]['read only'])
        self.assertFalse(widgetsdict_witness[ww]['read only'])
        w = widgetsdict.root.search_from_path(DCAT.distribution / DCT.license)
        ww = widgetsdict_witness.root.search_from_path(DCAT.distribution / DCT.license)
        self.assertTrue(w.is_read_only)
        self.assertFalse(ww.is_read_only)
        self.assertFalse(widgetsdict[w]['multiple sources'])
        self.assertTrue(widgetsdict_witness[ww]['multiple sources'])
        w = widgetsdict.root.search_from_path(DCAT.distribution / DCT.license / RDFS.label)
        ww = widgetsdict_witness.root.search_from_path(DCAT.distribution / DCT.license / RDFS.label)
        self.assertTrue(w.is_read_only)
        self.assertFalse(ww.is_read_only)
        self.assertTrue(all(widgetsdict[c]['read only'] for c in w.children))
        self.assertTrue(not any(widgetsdict_witness[c]['read only'] for c in ww.children))

    def test_items_to_compute(self):
        """Générateur sur les clés avec calcul automatique.
        
        """
        # --- préparation d'un modèle avec calcul auto ---
        conn = psycopg2.connect(WidgetsDictTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('''
                    INSERT INTO z_plume.meta_template (tpl_id, tpl_label) VALUES
                        (100, 'Calcul') ;
                    INSERT INTO z_plume.meta_template_categories
                        (tpl_id, shrcat_path, compute, compute_params) VALUES
                        (100, 'dct:title', ARRAY['manual', 'empty'],
                            '{"pattern": "^[^.]+"}'::jsonb),
                        (100, 'dct:description', ARRAY['manual', 'empty'], NULL),
                        (100, 'dct:conformsTo', ARRAY['manual', 'auto'], NULL),
                        (100, 'dct:created', ARRAY['manual', 'new'], NULL),
                        (100, 'dct:modified', ARRAY['manual', 'auto'], NULL) ;
                    ''')
                cur.execute(
                    *query_get_categories('Calcul')
                    )
                categories = cur.fetchall()
                cur.execute('''
                    TRUNCATE z_plume.meta_template CASCADE ;
                    ''')
        conn.close()
        template = TemplateDict(categories)
        widgetsdict = WidgetsDict(template=template)

        # --- préparation des objets ---
        conn = psycopg2.connect(WidgetsDictTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('''
                    ALTER EVENT TRIGGER plume_stamp_table_creation ENABLE ;
                    ALTER EVENT TRIGGER plume_stamp_table_modification ENABLE ;
                    ALTER EVENT TRIGGER plume_stamp_table_drop ENABLE ;
                    CREATE TABLE z_plume.test_multigeom (
                        id serial PRIMARY KEY,
                        geom_2154 geometry(multipolygon, 2154),
                        geom_4326 geometry(multipolygon, 4326)
                    ) ;
                    COMMENT ON TABLE z_plume.test_multigeom IS 'Table multi-géométries. ...' ;
                    ''')
        conn.close()

        # --- exécution du calcul ---
        for widgetkey, internaldict in widgetsdict.items_to_compute():
            query = widgetsdict.computing_query(widgetkey, 'z_plume', 'test_multigeom')
            conn = psycopg2.connect(WidgetsDictTestCase.connection_string)
            with conn:
                with conn.cursor() as cur:
                    cur.execute(*query)
                    result = cur.fetchall()
            conn.close()
            widgetsdict.computing_update(widgetkey, result)

        # --- nettoyage des objets ---
        conn = psycopg2.connect(WidgetsDictTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('''
                    DROP TABLE z_plume.test_multigeom ;
                    TRUNCATE z_plume.stamp_timestamp ;
                    ALTER EVENT TRIGGER plume_stamp_table_drop DISABLE ;
                    ALTER EVENT TRIGGER plume_stamp_table_modification DISABLE ;
                    ALTER EVENT TRIGGER plume_stamp_table_creation DISABLE ;
                    ''')
        conn.close()

        # --- contrôle du résultat ---
        a = widgetsdict.root.search_from_path(DCT.title)
        self.assertEqual(widgetsdict[a]['value'], 'Table multi-géométries')
        b = widgetsdict.root.search_from_path(DCT.conformsTo)
        self.assertEqual(len(b.children), 2)
        self.assertTrue('EPSG 2154 : RGF93 / Lambert-93 (France métropolitaine)'
            in [widgetsdict[c]['value'] for c in b.children])
        self.assertTrue('EPSG 4326 : WGS 84'
            in [widgetsdict[c]['value'] for c in b.children])

    def test_items_to_compute_read(self):
        """Générateur sur les clés avec calcul automatique, simulation en mode lecture.
        
        """
        metadata = """
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix uuid: <urn:uuid:> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

            uuid:479fd670-32c5-4ade-a26d-0268b0ce5046 a dcat:Dataset ;
                dct:accessRights [ a dct:RightsStatement ;
                    rdfs:label "Aucune restriction d'accès ou d'usage."@fr ] ;
                uuid:218c1245-6ba7-4163-841e-476e0d5582af "À mettre à jour !"@fr .
            """
        metagraph = Metagraph().parse(data=metadata)

        # --- préparation d'un modèle avec calcul auto ---
        conn = psycopg2.connect(WidgetsDictTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('''
                    INSERT INTO z_plume.meta_template (tpl_id, tpl_label) VALUES
                        (100, 'Calcul') ;
                    INSERT INTO z_plume.meta_template_categories
                        (tpl_id, shrcat_path, compute, compute_params) VALUES
                        (100, 'dct:title', ARRAY['manual', 'empty'],
                            '{"pattern": "^[^.]+"}'::jsonb),
                        (100, 'dct:description', ARRAY['manual', 'empty'], NULL),
                        (100, 'dct:conformsTo', ARRAY['manual', 'auto'], NULL),
                        (100, 'dct:created', ARRAY['manual', 'new'], NULL),
                        (100, 'dct:modified', ARRAY['manual', 'auto'], NULL) ;
                    ''')
                cur.execute(
                    *query_get_categories('Calcul')
                    )
                categories = cur.fetchall()
                cur.execute('''
                    TRUNCATE z_plume.meta_template CASCADE ;
                    ''')
        conn.close()
        template = TemplateDict(categories)
        widgetsdict = WidgetsDict(metagraph=metagraph, template=template,
            mode='read')
        self.assertIsNone(widgetsdict.root.search_from_path(DCT.created))
        # car 'new' sur une fiche non vide
        self.assertIsNotNone(widgetsdict.root.search_from_path(DCT.modified))
        self.assertIsNotNone(widgetsdict.root.search_from_path(DCT.conformsTo))
        self.assertIsNotNone(widgetsdict.root.search_from_path(DCT.title))

        # --- préparation des objets ---
        conn = psycopg2.connect(WidgetsDictTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('''
                    ALTER EVENT TRIGGER plume_stamp_table_creation ENABLE ;
                    ALTER EVENT TRIGGER plume_stamp_table_modification ENABLE ;
                    ALTER EVENT TRIGGER plume_stamp_table_drop ENABLE ;
                    CREATE TABLE z_plume.test_multigeom (
                        id serial PRIMARY KEY,
                        geom_2154 geometry(multipolygon, 2154),
                        geom_4326 geometry(multipolygon, 4326)
                    ) ;
                    COMMENT ON TABLE z_plume.test_multigeom IS 'Table multi-géométries. ...' ;
                    ''')
        conn.close()

        # --- exécution du calcul ---
        for widgetkey, internaldict in widgetsdict.items_to_compute():
            query = widgetsdict.computing_query(widgetkey, 'z_plume', 'test_multigeom')
            conn = psycopg2.connect(WidgetsDictTestCase.connection_string)
            with conn:
                with conn.cursor() as cur:
                    cur.execute(*query)
                    result = cur.fetchall()
            conn.close()
            widgetsdict.computing_update(widgetkey, result)

        # --- nettoyage des objets ---
        conn = psycopg2.connect(WidgetsDictTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('''
                    DROP TABLE z_plume.test_multigeom ;
                    TRUNCATE z_plume.stamp_timestamp ;
                    ALTER EVENT TRIGGER plume_stamp_table_drop DISABLE ;
                    ALTER EVENT TRIGGER plume_stamp_table_modification DISABLE ;
                    ALTER EVENT TRIGGER plume_stamp_table_creation DISABLE ;
                    ''')
        conn.close()

        # --- contrôle du résultat ---
        a = widgetsdict.root.search_from_path(DCT.title)
        self.assertEqual(widgetsdict[a]['value'], 'Table multi-géométries')
        b = widgetsdict.root.search_from_path(DCT.conformsTo)
        self.assertEqual(len(b.children), 2)
        self.assertTrue('<a href="http://www.opengis.net/def/crs/EPSG/0/2154">' \
            'EPSG 2154 : RGF93 / Lambert-93 (France métropolitaine)</a>'
            in [widgetsdict[c]['value'] for c in b.children])
        self.assertTrue('<a href="http://www.opengis.net/def/crs/EPSG/0/4326">' \
            'EPSG 4326 : WGS 84</a>' in [widgetsdict[c]['value'] for c in b.children])

    def test_multiple_custom_tabs(self):
        """Cas d'un modèle personnalisé avec plusieurs onglets.
        """
        conn = psycopg2.connect(WidgetsDictTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('''
                    SELECT * FROM z_plume.meta_import_sample_template('Classique') ;
                    INSERT INTO z_plume.meta_tab (tab_id, tab_label, tab_num) VALUES
                        (101, 'onglet XYZ', 1),
                        (102, 'onglet ABC', 2) ;
                    UPDATE z_plume.meta_template_categories
                        SET tab_id = 102
                        WHERE shrcat_path IN (
                            'dcat:contactPoint', 'adms:versionNotes'
                        ) AND tpl_id = (
                            SELECT meta_template.tpl_id
                                FROM z_plume.meta_template
                                WHERE tpl_label = 'Classique'
                        ) ;
                    UPDATE z_plume.meta_template_categories
                        SET tab_id = 101
                        WHERE shrcat_path = 'dct:title' AND tpl_id = (
                            SELECT meta_template.tpl_id
                                FROM z_plume.meta_template
                                WHERE tpl_label = 'Classique'
                        ) ;
                    ''')
                cur.execute(
                    *query_get_categories('Classique')
                    )
                categories = cur.fetchall()
                cur.execute(
                    *query_template_tabs('Classique')
                    )
                tabs = cur.fetchall()
                cur.execute('TRUNCATE z_plume.meta_tab CASCADE ; TRUNCATE z_plume.meta_template CASCADE')
        conn.close()
        template = TemplateDict(categories, tabs)
        widgetsdict = WidgetsDict(template=template, mode='edit')
        xyz = widgetsdict.root.search_tab('onglet XYZ')
        abc = widgetsdict.root.search_tab('onglet ABC')
        k = widgetsdict.root.search_from_path(DCT.title)
        self.assertEqual(k.parent, xyz)
        k = widgetsdict.root.search_from_path(DCT.description)
        self.assertEqual(k.parent, xyz)
        k = widgetsdict.root.search_from_path(DCAT.contactPoint)
        self.assertEqual(k.parent, abc)

    def test_langlist_order(self):
        """Respect de l'ordre des langues."""
        w = WidgetsDict(langList=('en', 'fr', 'it'), language='it')
        self.assertEqual(w.langlist, ('it', 'en', 'fr'))
        w = WidgetsDict(langList=('en', 'de', 'it'), language='it')
        self.assertEqual(w.langlist, ('it', 'en', 'de'))
        w = WidgetsDict(langList=('en', 'de', 'it'))
        self.assertEqual(w.langlist, ('en', 'de', 'it'))

    def test_value_help_text(self):
        """Contrôle la génération du texte à afficher en infobulle sur certaines valeurs."""
        metadata = """
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix uuid: <urn:uuid:> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

            uuid:479fd670-32c5-4ade-a26d-0268b0ce5046 a dcat:Dataset ;
                dcat:theme <http://inspire.ec.europa.eu/theme/au> ;
                dct:identifier "479fd670-32c5-4ade-a26d-0268b0ce5046" ;
                dcat:distribution [ a dcat:Distribution ;
                    dcat:packageFormat <http://publications.europa.eu/resource/authority/file-type/ZIP> ;
                    dct:license [ a dct:LicenseDocument ;
                        rdfs:label "Licence ouverte Etalab 2.0"@fr ] ;
                    dcat:accessURL <https://atom.geo-ide.developpement-durable.gouv.fr/atomArchive/GetResource?id=fr-120066022-orphan-5ac5fa30-1ce8-479f-9c67-f5960e69bcb5&dataType=datasetAggregate> ] .
            """
        # en mode lecture...
        metagraph = Metagraph().parse(data=metadata)
        widgetsdict = WidgetsDict(metagraph=metagraph, mode='read')
        themekey = widgetsdict.root.search_from_path(DCAT.theme)
        self.assertEqual(widgetsdict[themekey]['value help text'], 'http://inspire.ec.europa.eu/theme/au')
        witnesskey = widgetsdict.root.search_from_path(DCT.identifier)
        self.assertIsNone(widgetsdict[witnesskey]['value help text'])
        formatkey = widgetsdict.root.search_from_path(DCAT.distribution / DCAT.packageFormat)
        self.assertEqual(widgetsdict[formatkey]['value help text'], 'http://publications.europa.eu/resource/authority/file-type/ZIP')
        urlkey = widgetsdict.root.search_from_path(DCAT.distribution / DCAT.accessURL)
        self.assertEqual(
            widgetsdict[urlkey]['value help text'],
            'https://atom.geo-ide.developpement-durable.gouv.fr/atomArchive/GetResource?id=fr-120066022-orphan-5ac5fa30-1ce8-479f-9c67-f5960e69bcb5&dataType=datasetAggregate'
        )
        # ... mais pas en mode édition
        widgetsdict = WidgetsDict(metagraph=metagraph, mode='edit')
        themekey = widgetsdict.root.search_from_path(DCAT.theme)
        self.assertIsNone(widgetsdict[themekey]['value help text'])

    def test_compute_theme(self):
        """Processus complet de calcul des métadonnées pour dcat:theme.
        
        Avec le mode ``'auto'`` pour le calcul automatique.
        
        """
        metadata = """
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix uuid: <urn:uuid:> .

            uuid:479fd670-32c5-4ade-a26d-0268b0ce5046 a dcat:Dataset ;
                dct:title "Un jeu de données"@fr ;
                dcat:theme <http://registre.data.developpement-durable.gouv.fr/ecospheres/themes-ecospheres/zonages-d-amenagement>,
                    <http://publications.europa.eu/resource/authority/data-theme/ENER> .
            """
        metagraph = Metagraph().parse(data=metadata)

        conn = psycopg2.connect(WidgetsDictTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM z_plume.meta_import_sample_template()')
                cur.execute('''
                    UPDATE z_plume.meta_categorie
                        SET compute = ARRAY['manual', 'auto']
                        WHERE path = 'dcat:theme' ;
                    ''')
                cur.execute(
                    *query_get_categories('Classique')
                    )
                categories = cur.fetchall()
                cur.execute('DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg')
        conn.close()
        template = TemplateDict(categories)
        widgetsdict = WidgetsDict(metagraph=metagraph, template=template)
        g = widgetsdict.root.search_from_path(DCAT.theme)
        self.assertTrue(widgetsdict[g]['has compute button'])
        self.assertTrue(widgetsdict[g]['auto compute'])
        self.assertIsNotNone(widgetsdict[g]['compute method'].description)
        self.assertEqual(widgetsdict[g]['compute method'].dependances, [])
        self.assertEqual(len(g.children), 2)
        self.assertEqual(g.children[1].value, URIRef('http://publications.europa.eu/resource/authority/data-theme/ENER'))
        
        # --- requête ---
        conn = psycopg2.connect(WidgetsDictTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                query = widgetsdict.computing_query(g, 'c_air_clim_changement', 'un_jeu_de_donnees')
                cur.execute(*query)
                result = cur.fetchall()
        conn.close()
        self.assertListEqual(result, [('c_air_clim_changement', True, True,)])
        
        widgetsdict[g]['main widget'] = '<g QGroupBox dcat:theme>'
        widgetsdict[g]['grid widget'] = '<g QGridLayout dcat:theme>'
        widgetsdict[g]['compute widget'] = '<g-compute QToolButton dcat:theme>'
        widgetsdict[g.button]['main widget'] = '<g-plus-button QToolButton dcat:theme>'

        c0 = g.children[0]
        widgetsdict[c0]['main widget'] = '<c0 QComboBox dcat:theme>'
        widgetsdict[c0]['minus widget'] = '<c0-minus QToolButton dcat:theme>'
        widgetsdict[c0]['switch source widget'] = '<c0-source QToolButton dcat:theme>'
        widgetsdict[c0]['switch source menu'] = '<c0-source QMenu dcat:theme>'
        widgetsdict[c0]['switch source actions'] = ['<c0-source QAction n°1', '<c0-source QAction n°2']

        c1 = g.children[1]
        widgetsdict[c1]['main widget'] = '<c1 QComboBox dcat:theme>'
        widgetsdict[c1]['minus widget'] = '<c1-minus QToolButton dcat:theme>'
        widgetsdict[c1]['switch source widget'] = '<c1-source QToolButton dcat:theme>'
        widgetsdict[c1]['switch source menu'] = '<c1-source QMenu dcat:theme>'
        widgetsdict[c1]['switch source actions'] = ['<c1-source QAction n°1', '<c1-source QAction n°2']
        
        # --- intégration ---
        actionsdict = widgetsdict.computing_update(g, result)
        self.assertEqual(len(g.children), 3)
        self.assertEqual(
            sorted([child.value for child in g.children], key=lambda x: str(x)),
            [
                URIRef('http://publications.europa.eu/resource/authority/data-theme/ENER'),
                URIRef('http://registre.data.developpement-durable.gouv.fr/ecospheres/themes-ecospheres/changement-climatique'),
                URIRef('http://registre.data.developpement-durable.gouv.fr/ecospheres/themes-ecospheres/climat')
            ]
        )
        self.assertEqual(actionsdict['new keys'],  [g.children[2]])
        self.assertEqual(actionsdict['value to update'], [c0])
        self.assertListEqual(
            actionsdict['widgets to move'],
            [
                (
                    '<g QGridLayout dcat:theme>',
                    '<g-plus-button QToolButton dcat:theme>',
                    3, 0, 1, 1
                )
            ]
        )
        for a, l in actionsdict.items():
            with self.subTest(action = a):
                if not a in ('value to update', 'new keys', 'widgets to move'):
                    self.assertFalse(l)

        metadata = """
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix uuid: <urn:uuid:> .

            uuid:479fd670-32c5-4ade-a26d-0268b0ce5046 a dcat:Dataset ;
                dct:title "Un jeu de données"@fr ;
                dcat:theme <http://publications.europa.eu/resource/authority/data-theme/ENER>,
                    <http://registre.data.developpement-durable.gouv.fr/ecospheres/themes-ecospheres/climat>,
                    <http://registre.data.developpement-durable.gouv.fr/ecospheres/themes-ecospheres/changement-climatique> ;
                dct:identifier "479fd670-32c5-4ade-a26d-0268b0ce5046".
            """
        metagraph = Metagraph().parse(data=metadata)
        self.assertTrue(isomorphic(metagraph,
            widgetsdict.build_metagraph(preserve_metadata_date=True)))

    def test_compute_theme_with_params(self):
        """Processus complet de calcul des métadonnées pour dcat:theme, avec paramétrage manuel.
        
        Avec le mode ``'auto'`` pour le calcul automatique.
        Idem test précédent, si ce n'est que ``compute_params`` est
        spécifié par le modèle et qu'on part d'un graphe qui ne 
        contient pas de thème.
        
        """
        metadata = """
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix uuid: <urn:uuid:> .

            uuid:479fd670-32c5-4ade-a26d-0268b0ce5046 a dcat:Dataset ;
                dct:title "Un jeu de données"@fr .
            """
        metagraph = Metagraph().parse(data=metadata)

        conn = psycopg2.connect(WidgetsDictTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM z_plume.meta_import_sample_template()')
                cur.execute('''
                    UPDATE z_plume.meta_categorie
                        SET compute = ARRAY['manual', 'auto'],
                            compute_params = '{"level_one": false}'::jsonb
                        WHERE path = 'dcat:theme' ;
                    ''')
                cur.execute(
                    *query_get_categories('Classique')
                    )
                categories = cur.fetchall()
                cur.execute('DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg')
        conn.close()
        template = TemplateDict(categories)
        widgetsdict = WidgetsDict(metagraph=metagraph, template=template)
        g = widgetsdict.root.search_from_path(DCAT.theme)
        self.assertTrue(widgetsdict[g]['has compute button'])
        self.assertTrue(widgetsdict[g]['auto compute'])
        self.assertIsNotNone(widgetsdict[g]['compute method'].description)
        self.assertEqual(widgetsdict[g]['compute method'].dependances, [])
        self.assertEqual(len(g.children), 1)
        self.assertIsNone(g.children[0].value)
        
        # --- requête ---
        conn = psycopg2.connect(WidgetsDictTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                query = widgetsdict.computing_query(g, 'c_air_clim_changement', 'un_jeu_de_donnees')
                cur.execute(*query)
                result = cur.fetchall()
        conn.close()
        self.assertListEqual(result, [('c_air_clim_changement', False, True,)])
        
        widgetsdict[g]['main widget'] = '<g QGroupBox dcat:theme>'
        widgetsdict[g]['grid widget'] = '<g QGridLayout dcat:theme>'
        widgetsdict[g]['compute widget'] = '<g-compute QToolButton dcat:theme>'
        widgetsdict[g.button]['main widget'] = '<g-plus-button QToolButton dcat:theme>'

        c0 = g.children[0]
        widgetsdict[c0]['main widget'] = '<c0 QComboBox dcat:theme>'
        widgetsdict[c0]['minus widget'] = '<c0-minus QToolButton dcat:theme>'
        widgetsdict[c0]['switch source widget'] = '<c0-source QToolButton dcat:theme>'
        widgetsdict[c0]['switch source menu'] = '<c0-source QMenu dcat:theme>'
        widgetsdict[c0]['switch source actions'] = ['<c0-source QAction n°1', '<c0-source QAction n°2']
        
        # --- intégration ---
        actionsdict = widgetsdict.computing_update(g, result)
        self.assertEqual(len(g.children), 1)
        self.assertEqual(g.children[0].value, URIRef('http://registre.data.developpement-durable.gouv.fr/ecospheres/themes-ecospheres/changement-climatique'))
        self.assertEqual(actionsdict['value to update'], [c0])
        # la source doit également être mise à jour, car celle qui 
        # est utilisée par défaut ne correspond pas aux thèmes Ecosphères :
        self.assertEqual(actionsdict['concepts list to update'], [c0])
        self.assertEqual(actionsdict['switch source menu to update'], [c0])
        for a, l in actionsdict.items():
            with self.subTest(action = a):
                if not a in ('value to update', 'concepts list to update', 'switch source menu to update'):
                    self.assertFalse(l)

        metadata = """
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix uuid: <urn:uuid:> .

            uuid:479fd670-32c5-4ade-a26d-0268b0ce5046 a dcat:Dataset ;
                dct:title "Un jeu de données"@fr ;
                dcat:theme <http://registre.data.developpement-durable.gouv.fr/ecospheres/themes-ecospheres/changement-climatique> ;
                dct:identifier "479fd670-32c5-4ade-a26d-0268b0ce5046".
            """
        metagraph = Metagraph().parse(data=metadata)
        self.assertTrue(isomorphic(metagraph,
            widgetsdict.build_metagraph(preserve_metadata_date=True)))
        
    def test_compute_theme_no_result_edit(self):
        """Processus de calcul des métadonnées lorsqu'il n'y a pas de correspondance.
        
        Avec le mode ``'auto'`` pour le calcul automatique, pour un
        dictionnaire en mode édition + traduction.
        
        """
        conn = psycopg2.connect(WidgetsDictTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute(''' 
                    INSERT INTO z_plume.meta_template (tpl_id, tpl_label) VALUES 
                        (100, 'Some computing') ;
                    INSERT INTO z_plume.meta_template_categories (tpl_id, shrcat_path, compute) VALUES
                        (100, 'dct:conformsTo', ARRAY['auto']),
                        (100, 'dcat:theme', ARRAY['auto', 'manual']),
                        (100, 'dct:title', ARRAY['auto']) ;
                    CREATE SCHEMA IF NOT EXISTS ghost ;
                    CREATE TABLE ghost.some_ghost_table () ;
                ''')
                cur.execute(
                    *query_get_categories('Some computing')
                )
                categories = cur.fetchall()
                cur.execute('''
                    DROP EXTENSION plume_pg ;
                    CREATE EXTENSION plume_pg ;
                ''')
        conn.close()
        metagraph = Metagraph()
        template = TemplateDict(categories)
        widgetsdict = WidgetsDict(
            metagraph=metagraph, template=template, mode='edit', translation=True
        )
        gtheme = widgetsdict.root.search_from_path(DCAT.theme)
        self.assertTrue(widgetsdict[gtheme]['has compute button'])
        self.assertTrue(widgetsdict[gtheme]['auto compute'])
        self.assertEqual(len(gtheme.children), 1)
        self.assertIsNone(gtheme.children[0].value)

        gtitle = widgetsdict.root.search_from_path(DCT.title)
        self.assertFalse(widgetsdict[gtitle]['has compute button'])
        self.assertTrue(widgetsdict[gtitle]['auto compute'])
        self.assertEqual(len(gtitle.children), 1)
        self.assertIsNone(gtitle.children[0].value)

        gconforms = widgetsdict.root.search_from_path(DCT.conformsTo)
        self.assertFalse(widgetsdict[gconforms]['has compute button'])
        self.assertTrue(widgetsdict[gconforms]['auto compute'])
        self.assertEqual(len(gconforms.children), 1)
        self.assertIsNone(gconforms.children[0].value)
        
        # --- requête ---
        conn = psycopg2.connect(WidgetsDictTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                query = widgetsdict.computing_query(gtheme, 'ghost', 'some_ghost_table')
                cur.execute(*query)
                result_gtheme = cur.fetchall()
                query = widgetsdict.computing_query(gtitle, 'ghost', 'some_ghost_table')
                cur.execute(*query)
                result_gtitle = cur.fetchall()
                query = widgetsdict.computing_query(gconforms, 'ghost', 'some_ghost_table')
                cur.execute(*query)
                result_gconforms = cur.fetchall()
                cur.execute('''
                    DROP TABLE ghost.some_ghost_table ;
                    DROP SCHEMA ghost ;
                ''')
        conn.close()
        
        widgetsdict[gtheme]['main widget'] = '<gtheme QGroupBox dcat:theme>'
        widgetsdict[gtheme]['grid widget'] = '<gtheme QGridLayout dcat:theme>'
        widgetsdict[gtheme]['compute widget'] = '<gtheme-compute QToolButton dcat:theme>'
        widgetsdict[gtheme.button]['main widget'] = '<gtheme-plus-button QToolButton dcat:theme>'

        vtheme = gtheme.children[0]
        widgetsdict[vtheme]['main widget'] = '<vtheme QComboBox dcat:theme>'
        widgetsdict[vtheme]['minus widget'] = '<vtheme-minus QToolButton dcat:theme>'
        widgetsdict[vtheme]['switch source widget'] = '<vtheme-source QToolButton dcat:theme>'
        widgetsdict[vtheme]['switch source menu'] = '<vtheme-source QMenu dcat:theme>'
        widgetsdict[vtheme]['switch source actions'] = ['<vtheme-source QAction n°1', '<vtheme-source QAction n°2']

        widgetsdict[gtitle]['main widget'] = '<gtitle QGroupBox dct:title>'
        widgetsdict[gtitle]['grid widget'] = '<gtitle QGridLayout dct:title>'
        widgetsdict[gtitle]['compute widget'] = '<gtitle-compute QToolButton dct:title>'
        widgetsdict[gtitle.button]['main widget'] = '<gtitle-translation-button QToolButton dct:title>'

        vtitle = gtitle.children[0]
        widgetsdict[vtitle]['main widget'] = '<vtitle QComboBox dct:title>'
        widgetsdict[vtitle]['minus widget'] = '<vtitle-minus QToolButton dct:title>'
        widgetsdict[vtitle]['language widget'] = '<vtitle-language QToolButton dct:title>'
        widgetsdict[vtitle]['language menu'] = '<vtitle-language QMenu dct:title>'
        widgetsdict[vtitle]['language actions'] = ['<vtitle-language QAction n°1', '<vtitle-language QAction n°2']

        widgetsdict[gconforms]['main widget'] = '<gconforms QGroupBox dct:conformsTo>'
        widgetsdict[gconforms]['grid widget'] = '<gconforms QGridLayout dct:conformsTo>'
        widgetsdict[gconforms]['compute widget'] = '<gconforms-compute QToolButton dct:conformsTo>'
        widgetsdict[gconforms.button]['main widget'] = '<gconforms-plus-button QToolButton dct:conformsTo>'

        vconforms = gconforms.children[0]
        widgetsdict[vconforms]['main widget'] = '<vconforms QComboBox dct:conformsTo>'
        widgetsdict[vconforms]['minus widget'] = '<vconforms-minus QToolButtondct:conformsTo>'
        widgetsdict[vconforms]['switch source widget'] = '<vconforms-source QToolButton dct:conformsTo>'
        widgetsdict[vconforms]['switch source menu'] = '<vconforms-source QMenu dct:conformsTo>'
        widgetsdict[vconforms]['switch source actions'] = ['<vconforms-source QAction n°1', '<vconforms-source QAction n°2']
        
        # --- intégration ---
        actionsdict = widgetsdict.computing_update(gtheme, result_gtheme)
        self.assertListEqual(gtheme.children, [vtheme])
        self.assertIsNone(vtheme.value)
        self.assertTrue(widgetsdict[gtheme]['has compute button'])
        self.assertTrue(widgetsdict[vtheme]['has minus button'])
        self.assertTrue(widgetsdict[vtheme]['hide minus button'])
        self.assertTrue(widgetsdict[vtheme]['multiple sources'])
        self.assertFalse(widgetsdict[gtheme.button]['hidden'])
        self.assertListEqual(actionsdict['value to update'], [vtheme])
        # NB: la réinitialisation de la valeur même lorsqu'elle n'a pas
        # été modifiée est une précaution technique
        for a, l in actionsdict.items():
            with self.subTest(action = a):
                if a != 'value to update':
                    self.assertFalse(l)
        
        actionsdict = widgetsdict.computing_update(gtitle, result_gtitle)
        self.assertListEqual(gtitle.children, [vtitle])
        self.assertIsNone(vtitle.value)
        self.assertFalse(widgetsdict[gtitle]['has compute button'])
        self.assertTrue(widgetsdict[vtitle]['has minus button'])
        self.assertTrue(widgetsdict[vtitle]['hide minus button'])
        self.assertTrue(widgetsdict[vtitle]['authorized languages'])
        self.assertFalse(widgetsdict[gtitle.button]['hidden'])
        self.assertListEqual(actionsdict['value to update'], [vtitle])
        for a, l in actionsdict.items():
            with self.subTest(action = a):
                if a != 'value to update':
                    self.assertFalse(l)

        actionsdict = widgetsdict.computing_update(gconforms, result_gconforms)
        self.assertListEqual(gconforms.children, [vconforms])
        self.assertIsNone(vconforms.value)
        self.assertFalse(widgetsdict[gconforms]['has compute button'])
        self.assertTrue(widgetsdict[vconforms]['has minus button'])
        self.assertTrue(widgetsdict[vconforms]['hide minus button'])
        self.assertFalse(widgetsdict[gconforms.button]['hidden'])
        self.assertListEqual(actionsdict['value to update'], [vconforms])
        for a, l in actionsdict.items():
            with self.subTest(action = a):
                if a != 'value to update':
                    self.assertFalse(l)

    def test_compute_theme_no_result_read(self):
        """Processus de calcul des métadonnées lorsqu'il n'y a pas de correspondance - en mode lecture.
        
        Avec le mode ``'auto'`` pour le calcul automatique, pour un
        dictionnaire en mode lecture. Le principal enjeu est de vérifier
        que les groupes vides sont correctement supprimés.
        
        """
        conn = psycopg2.connect(WidgetsDictTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute(''' 
                    INSERT INTO z_plume.meta_template (tpl_id, tpl_label) VALUES 
                        (100, 'Some computing') ;
                    INSERT INTO z_plume.meta_template_categories (tpl_id, shrcat_path, compute, template_order) VALUES
                        (100, 'dct:conformsTo', ARRAY['auto'], 3),
                        (100, 'dcat:theme', ARRAY['auto', 'manual'], 2),
                        (100, 'dct:title', ARRAY['auto'], 1) ;
                    CREATE SCHEMA IF NOT EXISTS ghost ;
                    CREATE TABLE ghost.some_ghost_table () ;
                ''')
                cur.execute(
                    *query_get_categories('Some computing')
                )
                categories = cur.fetchall()
                cur.execute('''
                    DROP EXTENSION plume_pg ;
                    CREATE EXTENSION plume_pg ;
                ''')
        conn.close()
        metagraph = Metagraph()
        template = TemplateDict(categories)
        widgetsdict = WidgetsDict(
            metagraph=metagraph, template=template, mode='read'
        )
        gtheme = widgetsdict.root.search_from_path(DCAT.theme)
        self.assertFalse(widgetsdict[gtheme]['has compute button'])
        self.assertTrue(widgetsdict[gtheme]['auto compute'])
        self.assertEqual(len(gtheme.children), 1)
        self.assertIsNone(gtheme.children[0].value)
        self.assertTrue(gtheme.button.is_hidden)
        self.assertTrue(widgetsdict[gtheme.button]['hidden'])

        vtitle = widgetsdict.root.search_from_path(DCT.title)
        self.assertFalse(widgetsdict[vtitle]['has compute button'])
        self.assertTrue(widgetsdict[vtitle]['auto compute'])
        self.assertFalse(widgetsdict[vtitle]['has minus button'])
        self.assertIsInstance(vtitle, ValueKey)
        self.assertIsNone(vtitle.value)

        gconforms = widgetsdict.root.search_from_path(DCT.conformsTo)
        self.assertFalse(widgetsdict[gconforms]['has compute button'])
        self.assertTrue(widgetsdict[gconforms]['auto compute'])
        self.assertEqual(len(gconforms.children), 1)
        self.assertIsNone(gconforms.children[0].value)

        tab = widgetsdict.root.search_tab('Général')
        self.assertListEqual(tab.children, [vtitle, gtheme, gconforms])
        self.assertTrue(tab in widgetsdict.root.children)
        
        # --- requête ---
        conn = psycopg2.connect(WidgetsDictTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                query = widgetsdict.computing_query(gtheme, 'ghost', 'some_ghost_table')
                cur.execute(*query)
                result_gtheme = cur.fetchall()
                query = widgetsdict.computing_query(vtitle, 'ghost', 'some_ghost_table')
                cur.execute(*query)
                result_vtitle = cur.fetchall()
                query = widgetsdict.computing_query(gconforms, 'ghost', 'some_ghost_table')
                cur.execute(*query)
                result_gconforms = cur.fetchall()
                cur.execute('''
                    DROP TABLE ghost.some_ghost_table ;
                    DROP SCHEMA ghost ;
                ''')
        conn.close()
        
        widgetsdict[tab]['main widget'] = '<tab Général>'
        widgetsdict[tab]['grid widget'] = '<tab QGridLayout Général>'
        widgetsdict[gtheme]['main widget'] = '<gtheme QGroupBox dcat:theme>'
        widgetsdict[gtheme]['grid widget'] = '<gtheme QGridLayout dcat:theme>'
        vtheme = gtheme.children[0]
        widgetsdict[vtheme]['main widget'] = '<vtheme QComboBox dcat:theme>'
        widgetsdict[gtheme.button]['main widget'] = '<gtheme-plus-button QToolButton dcat:theme>'
        widgetsdict[vtitle]['main widget'] = '<vtitle QComboBox dct:title>'
        widgetsdict[gconforms]['main widget'] = '<gconforms QGroupBox dct:conformsTo>'
        widgetsdict[gconforms]['grid widget'] = '<gconforms QGridLayout dct:conformsTo>'
        vconforms = gconforms.children[0]
        widgetsdict[vconforms]['main widget'] = '<vconforms QComboBox dct:conformsTo>'
        widgetsdict[gconforms.button]['main widget'] = '<gconforms-plus-button QToolButton dct:conformsTo>'
        
        # --- intégration ---
        actionsdict = widgetsdict.computing_update(gtheme, result_gtheme)
        self.assertFalse(vtheme in widgetsdict)
        self.assertFalse(gtheme in widgetsdict)
        self.assertListEqual(tab.children, [vtitle, gconforms])
        self.assertListEqual(
            actionsdict['widgets to delete'], 
            [
                '<vtheme QComboBox dcat:theme>',
                '<gtheme QGroupBox dcat:theme>',
                '<gtheme-plus-button QToolButton dcat:theme>'
            ]
        )
        self.assertListEqual(
            actionsdict['grids to delete'], 
            ['<gtheme QGridLayout dcat:theme>']
        )
        self.assertListEqual(
            actionsdict['widgets to move'],
            [('<tab QGridLayout Général>', '<gconforms QGroupBox dct:conformsTo>', 1, 0, 1, 6)]
        )
        # NB: la réinitialisation de la valeur même lorsqu'elle n'a pas
        # été modifiée est une précaution technique
        for a, l in actionsdict.items():
            with self.subTest(action = a):
                if not a in ('widgets to delete', 'widgets to move', 'grids to delete'):
                    self.assertFalse(l)
        
        actionsdict = widgetsdict.computing_update(vtitle, result_vtitle)
        self.assertFalse(vtitle in widgetsdict)
        self.assertListEqual(tab.children, [gconforms])
        self.assertListEqual(
            actionsdict['widgets to delete'],
            ['<vtitle QComboBox dct:title>']
        )
        self.assertListEqual(
            actionsdict['widgets to move'],
            [('<tab QGridLayout Général>', '<gconforms QGroupBox dct:conformsTo>', 0, 0, 1, 6)]
        )
        for a, l in actionsdict.items():
            with self.subTest(action = a):
                if not a in ('widgets to delete', 'widgets to move'):
                    self.assertFalse(l)

        actionsdict = widgetsdict.computing_update(gconforms, result_gconforms)
        self.assertFalse(gconforms in widgetsdict)
        self.assertFalse(vconforms in widgetsdict)
        self.assertFalse(tab in widgetsdict)
        self.assertListEqual(tab.children, [])
        self.assertFalse(tab in widgetsdict.root.children)
        self.assertListEqual(
            actionsdict['widgets to delete'], 
            [
                '<vconforms QComboBox dct:conformsTo>',
                '<gconforms QGroupBox dct:conformsTo>',
                '<gconforms-plus-button QToolButton dct:conformsTo>',
                '<tab Général>'
            ]
        )
        self.assertListEqual(
            actionsdict['grids to delete'], 
            [
                '<gconforms QGridLayout dct:conformsTo>',
                '<tab QGridLayout Général>'
            ]
        )
        for a, l in actionsdict.items():
            with self.subTest(action = a):
                if not a in ('widgets to delete', 'grids to delete'):
                    self.assertFalse(l)

if __name__ == '__main__':
    unittest.main()

