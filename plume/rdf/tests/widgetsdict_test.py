"""Recette des modules widgetsdict et internal.

Les tests nécessitent une connexion PostgreSQL (paramètres à
saisir lors de l'exécution du test) pointant sur une base où 
l'extension plume_pg est installée. Il est préférable d'utiliser
un super-utilisateur.

"""

import unittest, psycopg2

from plume.rdf.widgetsdict import WidgetsDict
from plume.rdf.namespaces import DCAT, DCT, OWL, LOCAL, XSD, VCARD, SKOS, FOAF, \
    SNUM, LOCAL, RDF
from plume.rdf.widgetkey import GroupOfPropertiesKey
from plume.rdf.metagraph import Metagraph
from plume.rdf.rdflib import isomorphic, Literal, URIRef
from plume.rdf.exceptions import ForbiddenOperation

from plume.pg.tests.connection import ConnectionString
from plume.pg.queries import query_get_categories, query_template_tabs
from plume.pg.template import TemplateDict

connection_string = ConnectionString()


class WidgetsDictTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.grid = 5 # largeur de la grille
    
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
                "Restrictions d'accès en application du Code des relations entre le public et l'administration"
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
                "Restrictions d'accès en application du Code des relations entre le public et l'administration"
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
        key = widgetsdict.root.search_from_path(DCT.subject).children[0]
        d = {
            'main widget type': 'QComboBox',
            'help text': "Classification thématique du jeu données selon la nomenclature du standard ISO 19115.",
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
        self.assertTrue("Agriculture"
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
        key = widgetsdict.root.search_from_path(DCT.spatial / DCAT.bbox)
        d = {
            'main widget type': 'QTextEdit',
            'label': "Rectangle d'emprise",
            'has label': True,
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
                dct:description "Délimitation simplifiée des départements de France métropolitaine pour représentation à petite échelle, conforme au code officiel géographique (COG) de l'INSEE au 1er janvier de l'année de référence."@fr ;
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
        conn = psycopg2.connect(connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM z_plume.meta_import_sample_template()')
                cur.execute(
                    query_get_categories(),
                    ('Basique',)
                    )
                categories = cur.fetchall()
                cur.execute(
                    query_template_tabs(),
                    ('Basique',)
                    )
                tabs = cur.fetchall()
                cur.execute('DELETE FROM z_plume.meta_template')
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
        key = widgetsdict.root.search_tab('Autres')
        self.assertIsNone(key)
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
        conn = psycopg2.connect(connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM z_plume.meta_import_sample_template()')
                cur.execute(
                    query_get_categories(),
                    ('Basique',)
                    )
                categories = cur.fetchall()
                cur.execute(
                    query_template_tabs(),
                    ('Basique',)
                    )
                tabs = cur.fetchall()
                cur.execute('DELETE FROM z_plume.meta_template')
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
        conn = psycopg2.connect(connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM z_plume.meta_import_sample_template()')
                cur.execute(
                    query_get_categories(),
                    ('Basique',)
                    )
                categories = cur.fetchall()
                cur.execute(
                    query_template_tabs(),
                    ('Basique',)
                    )
                tabs = cur.fetchall()
                cur.execute('DELETE FROM z_plume.meta_template')
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
        conn = psycopg2.connect(connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM z_plume.meta_import_sample_template()')
                cur.execute(
                    query_get_categories(),
                    ('Basique',)
                    )
                categories = cur.fetchall()
                cur.execute(
                    query_template_tabs(),
                    ('Basique',)
                    )
                tabs = cur.fetchall()
                cur.execute('DELETE FROM z_plume.meta_template')
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
        widgetsdict[b.children[0]]['main widget'] = '<B QGroupBox dcat:startDate>'
        widgetsdict[b.children[1]]['main widget'] = '<B QGroupBox dcat:endDate>'
        widgetsdict[c]['main widget'] = '<C QGroupBox dct:temporal>'
        widgetsdict[c]['minus widget'] = '<C-minus QToolButton dct:temporal>'
        actionsdict = widgetsdict.drop(b)
        self.assertEqual(len(g.children), 1)
        self.assertFalse(b in widgetsdict)
        self.assertFalse(b.children[0] in widgetsdict)
        self.assertFalse(b.children[1] in widgetsdict)
        self.assertTrue(widgetsdict[c]['hide minus button'])
        self.assertEqual(actionsdict['widgets to hide'], ['<C-minus QToolButton dct:temporal>'])
        self.assertEqual(actionsdict['widgets to delete'],
            ['<B QGroupBox dct:temporal>', '<B-minus QToolButton dct:temporal>',
             '<B QGroupBox dcat:startDate>', '<B QGroupBox dcat:endDate>'])
        self.assertEqual(actionsdict['widgets to move'],
            [('<QGridLayout dct:temporal>', '<C QGroupBox dct:temporal>',
                0, 0, 1, WidgetsDictTestCase.grid - 1),
             ('<QGridLayout dct:temporal>', '<C-minus QToolButton dct:temporal>',
                0, WidgetsDictTestCase.grid - 1, 1, 1),
             ('<QGridLayout dct:temporal>', '<P QToolButton dct:temporal>',
                1, 0, 1, 1)])
        for k in actionsdict.keys():
            if not k in ('widgets to hide', 'widgets to delete', 'widgets to move'):
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
        conn = psycopg2.connect(connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM z_plume.meta_import_sample_template()')
                cur.execute(
                    query_get_categories(),
                    ('Classique',)
                    )
                categories = cur.fetchall()
                cur.execute(
                    query_template_tabs(),
                    ('Classique',)
                    )
                tabs = cur.fetchall()
                cur.execute('DELETE FROM z_plume.meta_template')
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
        self.assertEqual(actionsdict['widgets to empty'], ['<A QComboBox dcat:theme>'])
        self.assertTrue('Régions et villes' in widgetsdict[a]['thesaurus values'])
        for k in actionsdict.keys():
            if not k in ('switch source menu to update', 'concepts list to update',
                'widgets to empty'):
                self.assertFalse(actionsdict[k])
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
        self.assertEqual(actionsdict['widgets to empty'], ['<B2 QComboBox dct:accessRights>'])
        for k in actionsdict.keys():
            if not k in ('switch source menu to update', 'concepts list to update',
                'widgets to show', 'widgets to hide', 'widgets to empty'):
                self.assertFalse(actionsdict[k])
        self.assertIsNone(widgetsdict.check_grids())

        # --- Entrée en mode manuel ---
        actionsdict = widgetsdict.change_source(b2, '< manuel >')
        self.assertEqual(widgetsdict[b1]['current source'], "< manuel >")
        self.assertFalse(widgetsdict[b1]['hidden'])
        self.assertFalse(widgetsdict[b1.children[0]]['hidden'])
        self.assertTrue(widgetsdict[b2]['hidden'])
        self.assertEqual(actionsdict['widgets to hide'], ['<B2 QComboBox dct:accessRights>',
            '<B2-minus QToolButton dct:accessRights>', '<B2-source QToolButton dct:accessRights>'])
        self.assertEqual(actionsdict['widgets to show'], ['<B1 QGroupBox dct:accessRights>',
            '<B1-minus QToolButton dct:accessRights>', '<B1-source QToolButton dct:accessRights>',
            '<B1 QGroupBox rdfs:label>'])
        for k in actionsdict.keys():
            if not k in ('widgets to show', 'widgets to hide'):
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
            @prefix uuid: <urn:uuid:> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

            uuid:479fd670-32c5-4ade-a26d-0268b0ce5046 a dcat:Dataset ;
                dct:accessRights <http://inspire.ec.europa.eu/metadata-codelist/LimitationsOnPublicAccess/noLimitations> ;
                dct:identifier "479fd670-32c5-4ade-a26d-0268b0ce5046" .
            """
        metagraph = Metagraph().parse(data=metadata)
        conn = psycopg2.connect(connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM z_plume.meta_import_sample_template()')
                cur.execute(
                    query_get_categories(),
                    ('Basique',)
                    )
                categories = cur.fetchall()
                cur.execute(
                    query_template_tabs(),
                    ('Basique',)
                    )
                tabs = cur.fetchall()
                cur.execute('DELETE FROM z_plume.meta_template')
        conn.close()
        template = TemplateDict(categories, tabs)
        widgetsdict = WidgetsDict(metagraph=metagraph, template=template)
        g = widgetsdict.root.search_from_path(DCT.accessRights)
        self.assertEqual(len(g.children), 1)
        c = g.children[0]
        self.assertIsNone(c.m_twin)
        self.assertFalse('< manuel >' in widgetsdict[c]['sources'])   
        self.assertIsNone(widgetsdict.check_grids())        

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
        conn = psycopg2.connect(connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM z_plume.meta_import_sample_template()')
                cur.execute(
                    query_get_categories(),
                    ('Basique',)
                    )
                categories = cur.fetchall()
                cur.execute(
                    query_template_tabs(),
                    ('Basique',)
                    )
                tabs = cur.fetchall()
                cur.execute('DELETE FROM z_plume.meta_template')
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
        conn = psycopg2.connect(connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM z_plume.meta_import_sample_template()')
                cur.execute(
                    query_get_categories(),
                    ('Basique',)
                    )
                categories = cur.fetchall()
                cur.execute(
                    query_template_tabs(),
                    ('Basique',)
                    )
                tabs = cur.fetchall()
                cur.execute('DELETE FROM z_plume.meta_template')
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
            @prefix snum: <http://snum.scenari-community.org/Metadata/Vocabulaire/#> .
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
                snum:isExternal true ;
                uuid:218c1245-6ba7-4163-841e-476e0d5582af "À mettre à jour !"@fr .
            """
        metagraph = Metagraph().parse(data=metadata)
        conn = psycopg2.connect(connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM z_plume.meta_import_sample_template()')
                cur.execute("""
                    INSERT INTO z_plume.meta_categorie (path, label, datatype)
                        VALUES ('uuid:ae75b755-97e7-4d56-be15-00c143b37af0', 'test heure', 'xsd:time'),
                            ('uuid:7a656b67-45a6-4b85-948b-334caca7671f', 'test entier', 'xsd:integer'),
                            ('uuid:9ade6b00-a16a-424c-af8f-9c4bfb2a92f9', 'test décimal', 'xsd:decimal') ;
                    INSERT INTO z_plume.meta_template_categories (tpl_label, loccat_path)
                        VALUES ('Classique', 'uuid:ae75b755-97e7-4d56-be15-00c143b37af0'),
                            ('Classique', 'uuid:7a656b67-45a6-4b85-948b-334caca7671f'),
                            ('Classique', 'uuid:9ade6b00-a16a-424c-af8f-9c4bfb2a92f9') ;
                    """)
                cur.execute(
                    query_get_categories(),
                    ('Classique',)
                    )
                categories = cur.fetchall()
                cur.execute(
                    query_template_tabs(),
                    ('Classique',)
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
        c = widgetsdict.root.search_from_path(SNUM.isExternal)
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
            @prefix snum: <http://snum.scenari-community.org/Metadata/Vocabulaire/#> .
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
                snum:isExternal true ;
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
        connection_string = ConnectionString()
        conn = psycopg2.connect(connection_string)
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
                        SET geo_tools = ARRAY['show', 'rectangle', 'polygon', 'centroid']::z_plume.meta_geo_tool[]
                        WHERE label = 'test datatype wktLiteral' ;
                    UPDATE z_plume.meta_categorie
                        SET special = 'url'
                        WHERE label = 'test datatype iri' ;
                    INSERT INTO z_plume.meta_template(tpl_label) VALUES ('Datatype') ;
                    INSERT INTO z_plume.meta_template_categories (tpl_label, loccat_path)
                        (SELECT 'Datatype', path FROM z_plume.meta_categorie WHERE label ~ 'test.datatype') ;
                    ''')
                cur.execute(
                    query_get_categories(),
                    ('Datatype',)
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
        self.assertListEqual(widgetsdict[k]['geo tools'],
            ['show', 'rectangle', 'polygon', 'centroid'])
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
        

if __name__ == '__main__':
    unittest.main()

