"""Recette des modules widgetsdict et internal.

Les tests nécessitent une connexion PostgreSQL (paramètres à
saisir lors de l'exécution du test) pointant sur une base où 
l'extension plume_pg est installée. Il est préférable d'utiliser
un super-utilisateur.

"""

import unittest, psycopg2

from plume.rdf.widgetsdict import WidgetsDict
from plume.rdf.namespaces import DCAT, DCT
from plume.rdf.widgetkey import GroupOfPropertiesKey
from plume.rdf.metagraph import Metagraph

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

            uuid:479fd670-32c5-4ade-a26d-0268b0ce5046 a dcat:Dataset ;
                dct:accessRights [ a dct:RightsStatement ;
                    rdfs:label "Aucune restriction d'accès ou d'usage."@fr ] ;
                dct:description "Délimitation simplifiée des départements de France métropolitaine pour représentation à petite échelle, conforme au code officiel géographique (COG) de l'INSEE au 1er janvier de l'année de référence."@fr ;
                dct:title "ADMIN EXPRESS - Départements de métropole"@fr ;
                dcat:keyword "admin express"@fr,
                    "donnée externe"@fr,
                    "ign"@fr ;
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
        # --- avec graphe non inclus dans le modèle ---
        widgetsdict = WidgetsDict(mode = 'read', metagraph=metagraph,
            template=template)
        # groupe de valeurs
        key = widgetsdict.root.search_from_path(DCAT.keyword)
        #self.assertTrue(not key.button in widgetsdict)
        

    def test_widgetsdict_special_hidden_keys(self):
        """Génération d'un dictionnaire de widgets avec paramètres masquant certaines informations.

        """
        
	

if __name__ == '__main__':
    unittest.main()

