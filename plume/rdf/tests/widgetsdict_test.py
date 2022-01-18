"""Recette des modules widgetsdict et internal.

Les tests nécessitent une connexion PostgreSQL (paramètres à
saisir lors de l'exécution du test) pointant sur une base où 
l'extension plume_pg est installée. Il est préférable d'utiliser
un super-utilisateur.

"""

import unittest, psycopg2

from plume.rdf.widgetsdict import WidgetsDict
from plume.rdf.namespaces import DCAT, DCT, OWL, LOCAL
from plume.rdf.widgetkey import GroupOfPropertiesKey
from plume.rdf.metagraph import Metagraph
from plume.rdf.rdflib import isomorphic, Literal

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
            'object': 'group of values'
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
            'input mask': '0000-00-00',
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
            'help text': 'Libellé explicite du jeu de données.',
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
            'help text': 'Libellé explicite du jeu de données.',
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
        actionsdict = widgetsdict.drop(g.children[0])
        
        
        
        

if __name__ == '__main__':
    unittest.main()

