"""Recette des modules widgetsdict et internal.

Les tests nécessitent une connexion PostgreSQL (paramètres à
saisir lors de l'exécution du test) pointant sur une base où 
l'extension plume_pg est installée. Il est préférable d'utiliser
un super-utilisateur.

"""

import unittest, psycopg2

from plume.rdf.widgetsdict import WidgetsDict
from plume.rdf.namespaces import DCAT, DCT, OWL, LOCAL, XSD, VCARD, SKOS
from plume.rdf.widgetkey import GroupOfPropertiesKey
from plume.rdf.metagraph import Metagraph
from plume.rdf.rdflib import isomorphic, Literal, URIRef
from plume.rdf.exceptions import ForbiddenOperation

from plume.pg.tests.connection import ConnectionString
from plume.pg.queries import query_get_categories, query_template_tabs
from plume.pg.template import TemplateDict

connection_string = ConnectionString()


class WidgetsDictTestCase(unittest.TestCase):
    
    def test_widgetsdict_empty_edit(self):
        """Génération d'un dictionnaire de widgets sans graphe ni modèle.

        Ce premier test vérifie essentiellement
        que toutes les informations du dictionnaire
        interne sont correctement générées, dans le
        cas simple d'un dictionnaire en mode édition.
        
        """
        widgetsdict = WidgetsDict()
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
            'multiple sources': True,
            'sources': [
                '< manuel >',
                "Restriction d'accès public INSPIRE (UE)",
                "Droits d'accès (UE)",
                "Restrictions d'accès en application du Code des relations entre le public et l'administration"
                ],
            'current source': "Restriction d'accès public INSPIRE (UE)",
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
            'multiple sources': True,
            'sources': [
                '< manuel >',
                "Restriction d'accès public INSPIRE (UE)",
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
        key = widgetsdict.root.search_from_path(DCT.conformsTo / SKOS.inScheme)
        d = {
            'main widget type': 'QComboBox',
            'label': 'Registre',
            'has label': True,
            'object': 'edit',
            }
        for k, v in d.items():
            with self.subTest(internalkey = k):
                self.assertEqual(widgetsdict[key][k], v)
        for k, v in widgetsdict[key].items():
            with self.subTest(internalkey = k):
                if not k in d and not k == 'thesaurus values':
                    self.assertFalse(v)
        self.assertTrue("Système de coordonnées (registre de codes EPSG de l'OGC)"
            in widgetsdict[key]['thesaurus values'])
        self.assertTrue('' in widgetsdict[key]['thesaurus values'])
    
    
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
        self.assertEqual(widgetsdict.mode, 'read')
        self.assertFalse(widgetsdict.edit)
        self.assertTrue(widgetsdict.root in widgetsdict)
        self.assertEqual(len(widgetsdict), 1)
        # NB: le dictionnaire ne contient que la clé racine.
        
        # --- avec graphe, sans modèle ---
        widgetsdict = WidgetsDict(mode = 'read', metagraph=metagraph)
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
        key = widgetsdict.root.search_from_path(DCT.accessRights)
        self.assertFalse(widgetsdict[key]['multiple sources'])
        self.assertIsNone(key.m_twin)
        key = widgetsdict.root.search_from_path(OWL.versionInfo)
        self.assertIsNone(key)
        self.assertTrue(isomorphic(metagraph, widgetsdict.build_metagraph()))
        
        # --- avec graphe non inclus dans le modèle ---
        widgetsdict = WidgetsDict(mode = 'read', metagraph=metagraph,
            template=template)
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
        self.assertEqual(widgetsdict[key]['value'], '2021-01-15')
        self.assertFalse(widgetsdict[key]['has minus button'])
        self.assertTrue(widgetsdict[key]['read only'])
        key = widgetsdict.root.search_from_path(OWL.versionInfo)
        self.assertIsNone(key)
        self.assertTrue(isomorphic(metagraph, widgetsdict.build_metagraph()))
        
        # --- avec un modèle vide ---
        template = TemplateDict([])
        widgetsdict = WidgetsDict(mode = 'read', metagraph=metagraph,
            template=template)
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
        self.assertTrue(isomorphic(metagraph, widgetsdict.build_metagraph()))
        
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
        for key in widgetsdict.keys():
            self.assertNotEqual(key.path, DCAT.keyword)
        key = widgetsdict.root.search_from_path(DCT.temporal)
        self.assertTrue(key in widgetsdict)
        key = widgetsdict.root.search_from_path(OWL.versionInfo)
        self.assertTrue(key in widgetsdict)
        self.assertTrue(isomorphic(metagraph, widgetsdict.build_metagraph()))
        
        # --- editHideUnlisted sans modèle ---
        widgetsdict = WidgetsDict(metagraph=metagraph, editHideUnlisted=True)
        key = widgetsdict.root.search_from_path(DCAT.keyword)
        self.assertTrue(key in widgetsdict)
        key = widgetsdict.root.search_from_path(LOCAL['218c1245-6ba7-4163-841e-476e0d5582af'])
        self.assertIsNone(key)
        self.assertTrue(isomorphic(metagraph, widgetsdict.build_metagraph()))
        
        # --- editHideUnlisted avec un modèle vide ---
        widgetsdict = WidgetsDict(metagraph=metagraph, template=TemplateDict([]),
            editHideUnlisted=True)
        self.assertEqual(len(widgetsdict), 6)
        key = widgetsdict.root.search_tab()
        self.assertEqual(widgetsdict[key]['label'], 'Autres')
        widgetsdict[key]['grid widget'] = '<Grid onglet "Autres">'
        key = widgetsdict.root.search_from_path(DCT.title)
        self.assertEqual(widgetsdict.parent_grid(key), '<Grid onglet "Autres">')
        key = widgetsdict.root.search_from_path(DCT.description)
        self.assertEqual(widgetsdict.parent_grid(key), '<Grid onglet "Autres">')
        self.assertTrue(isomorphic(metagraph, widgetsdict.build_metagraph()))
        
        # --- editOnlyCurrentLanguage ---
        widgetsdict = WidgetsDict(metagraph=metagraph, language='it',
            langList=['fr', 'it', 'en'])
        key = widgetsdict.root.search_from_path(DCT.title)
        self.assertEqual(len(key.children), 2)
        for child in key.children:
            self.assertTrue(child in widgetsdict)
        self.assertIsNone(key.button)
        key = widgetsdict.root.search_from_path(DCAT.keyword)
        self.assertEqual(len(key.children), 4)
        for child in key.children:
            self.assertTrue(child in widgetsdict)
        self.assertTrue(isomorphic(metagraph, widgetsdict.build_metagraph()))
        
        widgetsdict = WidgetsDict(metagraph=metagraph,
            editOnlyCurrentLanguage=True, language='it',
            langList=['fr', 'it', 'en'])
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
        self.assertTrue(isomorphic(metagraph, widgetsdict.build_metagraph()))
        
        widgetsdict = WidgetsDict(metagraph=metagraph,
            editOnlyCurrentLanguage=True, language='en')
        key = widgetsdict.root.search_from_path(DCT.title)
        self.assertTrue(key in widgetsdict)
        self.assertEqual(len(key.children), 2)
        self.assertTrue(key.children[1].is_ghost)
        self.assertTrue(widgetsdict[key.children[0]]['value'],
            'ADMIN EXPRESS - Metropolitan Departments')
        self.assertTrue(isomorphic(metagraph, widgetsdict.build_metagraph()))
        
        # --- readHideBlank ---
        widgetsdict = WidgetsDict(metagraph=metagraph, template=template,
            mode='read', readHideBlank=False)
        key = widgetsdict.root.search_from_path(OWL.versionInfo)
        self.assertTrue(key in widgetsdict)
        self.assertTrue(isomorphic(metagraph, widgetsdict.build_metagraph()))
        
        widgetsdict = WidgetsDict(metagraph=metagraph, mode='read',
            readHideBlank=False)
        key = widgetsdict.root.search_from_path(DCAT.distribution / DCT.license)
        self.assertTrue(key in widgetsdict)
        self.assertTrue(isomorphic(metagraph, widgetsdict.build_metagraph()))
        
        # --- readHideUnlisted ---
        widgetsdict = WidgetsDict(metagraph=metagraph, mode='read')
        self.assertTrue(widgetsdict.hideUnlisted)
        key = widgetsdict.root.search_from_path(LOCAL['218c1245-6ba7-4163-841e-476e0d5582af'])
        self.assertIsNone(key)
        
        widgetsdict = WidgetsDict(metagraph=metagraph, mode='read',
            readHideUnlisted=False)
        self.assertFalse(widgetsdict.hideUnlisted)
        key = widgetsdict.root.search_from_path(LOCAL['218c1245-6ba7-4163-841e-476e0d5582af'])
        self.assertTrue(key in widgetsdict)
        
        widgetsdict = WidgetsDict(metagraph=metagraph, template=template,
            mode='read', readHideUnlisted=False)
        self.assertFalse(widgetsdict.hideUnlisted)
        key = widgetsdict.root.search_from_path(LOCAL['218c1245-6ba7-4163-841e-476e0d5582af'])
        self.assertTrue(key in widgetsdict)
        self.assertTrue(isomorphic(metagraph, widgetsdict.build_metagraph()))
        
        widgetsdict = WidgetsDict(metagraph=metagraph, template=template,
            mode='read', readHideUnlisted=False, readHideBlank=False)
        key = widgetsdict.root.search_from_path(DCAT.distribution / DCT.license)
        self.assertIsNone(key)
        # readHideBlank permet d'afficher des champs vides, mais pas ceux
        # hors modèle, même combiné avec readHideUnlisted (sinon à quoi
        # bon utiliser un modèle ?)
        self.assertTrue(isomorphic(metagraph, widgetsdict.build_metagraph()))
        
        # --- readOnlyCurrentLanguage ---
        widgetsdict = WidgetsDict(metagraph=metagraph, mode='read')
        self.assertTrue(widgetsdict.onlyCurrentLanguage)
        key = widgetsdict.root.search_from_path(DCT.title)
        self.assertEqual(len(key.children), 2)
        self.assertTrue(key.children[0] in widgetsdict)
        self.assertTrue(key.children[1].is_ghost)
        
        widgetsdict = WidgetsDict(metagraph=metagraph, mode='read',
            readOnlyCurrentLanguage=False)
        self.assertFalse(widgetsdict.onlyCurrentLanguage)
        key = widgetsdict.root.search_from_path(DCT.title)
        self.assertEqual(len(key.children), 2)
        self.assertTrue(key.children[0] in widgetsdict)
        self.assertTrue(key.children[1] in widgetsdict)
        key = widgetsdict.root.search_from_path(DCAT.keyword)
        self.assertEqual(len(key.children), 4)
        for child in key.children:
            self.assertTrue(child in widgetsdict)
        self.assertTrue(isomorphic(metagraph, widgetsdict.build_metagraph()))
        
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
        self.assertEqual(widgetsdict.widget_placement(g.children[4], 'main widget'), (4, 0, 1, 2))
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
        self.assertEqual(widgetsdict.widget_placement(g.children[1], 'main widget'), (1, 0, 1, 2))
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

    def test_drop(self):
        """Suppression d'une clé du dictionnaire.

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

        # --- suppression d'une clé simple ---
        g = widgetsdict.root.search_from_path(DCAT.keyword)
        b = g.children[1]
        widgetsdict[g]['grid widget'] = '<QGridLayout dcat:keyword>'
        widgetsdict[b]['main widget'] = '<B QLineEdit dcat:keyword>'
        widgetsdict[b]['minus widget'] = '<B QToolButton dcat:keyword>'
        c = g.children[2]
        widgetsdict[c]['main widget'] = '<C QLineEdit dcat:keyword>'
        widgetsdict[c]['minus widget'] = '<C QToolButton dcat:keyword>'
        widgetsdict[g.button]['main widget'] = '<P QToolButton dcat:keyword>'
        self.assertEqual(len(g.children), 4)
        self.assertTrue(widgetsdict.widget_placement(b, 'main widget'),
            (1, 0, 1, 2))
        actionsdict = widgetsdict.drop(b)
        self.assertEqual(len(g.children), 3)
        self.assertFalse(b in widgetsdict)
        self.assertEqual(actionsdict['widgets to delete'],
            ['<B QLineEdit dcat:keyword>', '<B QToolButton dcat:keyword>'])
        self.assertEqual(actionsdict['widgets to move'],
            [('<QGridLayout dcat:keyword>', '<C QLineEdit dcat:keyword>', 1, 0, 1, 2),
             ('<QGridLayout dcat:keyword>', '<C QToolButton dcat:keyword>', 1, 2, 1, 1),
             ('<QGridLayout dcat:keyword>', '<P QToolButton dcat:keyword>', 3, 0, 1, 1)])
        actionsdict = widgetsdict.drop(g.children[0])
        actionsdict = widgetsdict.drop(g.children[1])
        self.assertEqual(len(g.children), 1)
        self.assertEqual(actionsdict['widgets to hide'], ['<C QToolButton dcat:keyword>'])
        self.assertEqual(actionsdict['widgets to move'],
            [('<QGridLayout dcat:keyword>', '<P QToolButton dcat:keyword>', 1, 0, 1, 1)])
        for k in actionsdict.keys():
            if not k in ('widgets to hide', 'widgets to delete', 'widgets to move'):
                self.assertFalse(actionsdict[k])

        # --- suppression d'un groupe de propriétés ---
        g = widgetsdict.root.search_from_path(DCT.temporal)
        widgetsdict.add(g.button)
        b = g.children[0]
        c = g.children[1]
        widgetsdict[g]['grid widget'] = '<QGridLayout dct:temporal>'
        widgetsdict[g.button]['main widget'] = '<P QToolButton dct:temporal>'
        widgetsdict[b]['main widget'] = '<B QGroupBox dct:temporal>'
        widgetsdict[b]['minus widget'] = '<B QToolButton dct:temporal>'
        widgetsdict[b.children[0]]['main widget'] = '<B QGroupBox dcat:startDate>'
        widgetsdict[b.children[1]]['main widget'] = '<B QGroupBox dcat:endDate>'
        widgetsdict[c]['main widget'] = '<C QGroupBox dct:temporal>'
        widgetsdict[c]['minus widget'] = '<C QToolButton dct:temporal>'
        actionsdict = widgetsdict.drop(b)
        self.assertEqual(len(g.children), 1)
        self.assertFalse(b in widgetsdict)
        self.assertFalse(b.children[0] in widgetsdict)
        self.assertFalse(b.children[1] in widgetsdict)
        self.assertTrue(widgetsdict[c]['hide minus button'])
        self.assertEqual(actionsdict['widgets to hide'], ['<C QToolButton dct:temporal>'])
        self.assertEqual(actionsdict['widgets to delete'],
            ['<B QGroupBox dct:temporal>', '<B QToolButton dct:temporal>',
             '<B QGroupBox dcat:startDate>', '<B QGroupBox dcat:endDate>'])
        self.assertEqual(actionsdict['widgets to move'],
            [('<QGridLayout dct:temporal>', '<C QGroupBox dct:temporal>', 0, 0, 1, 2),
             ('<QGridLayout dct:temporal>', '<C QToolButton dct:temporal>', 0, 2, 1, 1),
             ('<QGridLayout dct:temporal>', '<P QToolButton dct:temporal>', 1, 0, 1, 1)])
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
            [('<QGridLayout dct:accessRights>', '<C1 QGroupBox dct:accessRights>', 0, 0, 1, 2),
             ('<QGridLayout dct:accessRights>', '<C1-minus QToolButton dct:accessRights>', 0, 3, 1, 1),
             ('<QGridLayout dct:accessRights>', '<C1-source QToolButton dct:accessRights>', 0, 2, 1, 1),
             ('<QGridLayout dct:accessRights>', '<C2 QComboBox dct:accessRights>', 0, 0, 1, 2),
             ('<QGridLayout dct:accessRights>', '<C2-minus QToolButton dct:accessRights>', 0, 3, 1, 1),
             ('<QGridLayout dct:accessRights>', '<C2-source QToolButton dct:accessRights>', 0, 2, 1, 1),
             ('<QGridLayout dct:accessRights>', '<P QToolButton dct:accessRights>', 1, 0, 1, 1)])
        self.assertEqual(actionsdict['actions to delete'], ['<B1-source QAction n°1',
            '<B1-source QAction n°2', '<B2-source QAction n°1', '<B2-source QAction n°2'])
        self.assertEqual(actionsdict['menus to delete'], ['<B1-source QMenu dct:accessRights>',
            '<B2-source QMenu dct:accessRights>'])
        for k in actionsdict.keys():
            if not k in ('widgets to hide', 'widgets to delete', 'widgets to move', 'actions to delete',
                'menus to delete'):
                self.assertFalse(actionsdict[k])
        
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

        # --- Multiples thésaurus ---
        a = widgetsdict.root.search_from_path(DCAT.theme).children[0]
        widgetsdict[a]['main widget'] = '<A QComboBox dcat:theme>'
        self.assertEqual(widgetsdict[a]['current source'], 'Thème INSPIRE (UE)')
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
        
        # --- Item non référencé vers manuel ---
        widgetsdict = WidgetsDict(metagraph=metagraph, template=template)
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
            [('<QGridLayout dct:title>', '<EN QLineEdit dct:title>', 0, 0, 1, 2),
             ('<QGridLayout dct:title>', '<EN-minus QToolButton dct:title>', 0, 3, 1, 1),
             ('<QGridLayout dct:title>', '<EN-language QToolButton dct:title>', 0, 2, 1, 1),
             ('<QGridLayout dct:title>', '<IT QLineEdit dct:title>', 1, 0, 1, 2),
             ('<QGridLayout dct:title>', '<IT-minus QToolButton dct:title>', 1, 3, 1, 1),
             ('<QGridLayout dct:title>', '<IT-language QToolButton dct:title>', 1, 2, 1, 1),
             ('<QGridLayout dct:title>', '<P QToolButton dct:title>', 2, 0, 1, 1)])
        for k in actionsdict.keys():
            if not k in ('widgets to show', 'widgets to delete', 'actions to delete',
                'menus to delete', 'language menu to update', 'widgets to move'):
                self.assertFalse(actionsdict[k])       

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
            [('<QGridLayout dcat:keyword>', '<P QToolButton dcat:keyword>', 5, 0, 1, 1)])
        self.assertEqual(actionsdict['new keys'], [c])
        for k in actionsdict.keys():
            if not k in ('widgets to move', 'new keys'):
                self.assertFalse(actionsdict[k])
        
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
            [('<QGridLayout dcat:keyword>', '<P QToolButton dcat:keyword>', 4, 0, 1, 1)])
        for k in actionsdict.keys():
            if not k in ('widgets to delete', 'actions to delete',
                'menus to delete', 'widgets to move'):
                self.assertFalse(actionsdict[k])
        
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
        widgetsdict = WidgetsDict(metagraph=metagraph, template=template,
            translation=True)

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

        # --- litéral avec un type particulier ---
        c = widgetsdict.root.search_from_path(DCT.modified)
        widgetsdict.update_value(c, '2021-01-21')
        self.assertEqual(c.value, Literal('2021-01-21', datatype=XSD.date))
        self.assertEqual(widgetsdict[c]['value'], '2021-01-21')

        # --- URI basique ---
        g = widgetsdict.root.search_from_path(DCAT.landingPage)
        widgetsdict.add(g.button)
        c = g.children[1]
        widgetsdict.update_value(c, 'https://www.postgresql.org/docs/14/index.html')
        self.assertEqual(c.value, URIRef('https://www.postgresql.org/docs/14/index.html'))
        self.assertEqual(widgetsdict[c]['value'], 'https://www.postgresql.org/docs/14/index.html')

        # --- téléphone ---
        c = widgetsdict.root.search_from_path(DCAT.contactPoint / VCARD.hasTelephone)
        widgetsdict.update_value(c, '0123456789')
        self.assertEqual(c.value, URIRef('tel:+33-1-23-45-67-89'))
        self.assertEqual(widgetsdict[c]['value'], '+33-1-23-45-67-89')

        # --- mél ---
        c = widgetsdict.root.search_from_path(DCAT.contactPoint / VCARD.hasEmail)
        widgetsdict.update_value(c, 'service@developpement-durable.gouv.fr')
        self.assertEqual(c.value, URIRef('mailto:service@developpement-durable.gouv.fr'))
        self.assertEqual(widgetsdict[c]['value'], 'service@developpement-durable.gouv.fr')

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
            @prefix owl: <http://www.w3.org/2002/07/owl#> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
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
                dcat:theme <http://publications.europa.eu/resource/authority/data-theme/REGI> ;
                dct:identifier "479fd670-32c5-4ade-a26d-0268b0ce5046" ;
                owl:versionInfo "1.0" ;
                dcat:contactPoint [ a vcard:Kind ;
                    vcard:hasTelephone <tel:+33-1-23-45-67-89> ;
                    vcard:hasEmail <mailto:service@developpement-durable.gouv.fr> ] ;
                uuid:218c1245-6ba7-4163-841e-476e0d5582af "À mettre à jour !"@fr .
            """
        metagraph = Metagraph().parse(data=metadata)
        self.assertTrue(isomorphic(metagraph, widgetsdict.build_metagraph()))
        

if __name__ == '__main__':
    unittest.main()

