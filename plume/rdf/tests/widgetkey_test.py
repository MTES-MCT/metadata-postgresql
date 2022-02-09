
import unittest
from uuid import uuid4

from plume.rdf.rdflib import URIRef, Literal
from plume.rdf.namespaces import RDFS, DCT, DCAT, FOAF, RDF, OWL, SKOS, XSD, GSP
from plume.rdf.widgetkey import WidgetKey, ValueKey, GroupOfPropertiesKey, \
    GroupOfValuesKey, TranslationGroupKey, TranslationButtonKey, \
    PlusButtonKey, RootKey, TabKey
from plume.rdf.actionsbook import ActionsBook

class WidgetKeyTestCase(unittest.TestCase):

    def test_get_all_attributes(self):
        """Vérifie que tous les attributs et propriétés peuvent être évalués sans erreur.
        
        Notes
        -----
        Ne teste pas les classes qui ne peuvent pas être appelées directement.
        
        """
        widgetkey = RootKey()
        for attr in ('actionsbook', 'attr_to_copy', 'attr_to_update', 'children', 'columnspan',
            'has_label', 'has_language_button', 'has_minus_button', 'has_source_button',
            'has_unit_button', 'independant_label', 'is_ghost', 'is_hidden', 'is_hidden_b',
            'is_hidden_m', 'is_single_child', 'key_object', 'label_placement', 'langlist',
            'language_button_placement', 'main_language', 'max_rowspan', 'minus_button_placement',
            'no_computation', 'node', 'order_idx', 'parent', 'path', 'placement', 'rdfclass',
            'row', 'rowspan', 'source_button_placement', 'unit_button_placement',
            'uuid', 'with_language_buttons', 'with_source_buttons', 'with_unit_buttons'):
            getattr(widgetkey, attr)

    def test_geo(self):
        """Clé avec bouton d'aide à la saisie des géométries.

        """
        r = RootKey()
        t = TabKey(parent=r, label='Général')
        v = ValueKey(parent=t, predicate=DCAT.bbox, datatype=GSP.wktLiteral,
            geo_tools=[Literal('bbox'), 'rectangle', Literal('chose')])
        self.assertTrue(v.has_geo_button)
        self.assertListEqual(v.geo_tools, ['bbox', 'rectangle'])
        WidgetKey.with_geo_buttons = False
        self.assertFalse(v.has_geo_button)
        WidgetKey.with_geo_buttons = True
        self.assertTrue(v.has_geo_button)
        v.is_read_only = True
        self.assertFalse(v.has_geo_button)

    def test_units(self):
        """Clé avec bouton de sélection de l'unité.

        Notes
        -----
        Ce test crée des clés ``dcat:temporalResolution``
        dans un groupe de valeurs, ce qui est discutable
        sur le fond, mais il s'agit de vérifier que les
        boutons moins sont bien placés.
        
        """
        r = RootKey()
        t = TabKey(parent=r, label='Général')
        g = GroupOfValuesKey(parent=t, predicate=DCAT.temporalResolution,
            datatype=XSD.duration)
        v1 = ValueKey(parent=g, value=Literal('PT2M', datatype=XSD.duration))
        self.assertEqual(v1.value_unit, 'min.')
        v2 = ValueKey(parent=g)
        self.assertEqual(v2.value_unit, 'ans')
        v2.value = Literal('P2M', datatype=XSD.duration)
        self.assertEqual(v2.value_unit, 'mois')
        self.assertEqual(v2.placement[1], 0)
        self.assertEqual(v2.unit_button_placement[1], 2)
        self.assertEqual(v2.minus_button_placement[1], 3)
        actionsbook = v1.change_unit('heures')
        self.assertEqual(v1.value_unit, 'heures')
        self.assertListEqual(actionsbook.units, [v1])

    def test_copy(self):
        """Copie d'une branche complexe.
        
        """
        r = RootKey()
        t = TabKey(parent=r, label='Général')
        gvs = GroupOfValuesKey(parent=t, rdfclass=DCT.Standard,
            predicate=DCT.conformsTo)
        sb = PlusButtonKey(parent=gvs)
        s1 = GroupOfPropertiesKey(parent=gvs)
        sv1 = ValueKey(parent=s1, predicate=SKOS.inScheme)
        gvi = GroupOfValuesKey(parent=s1, predicate=DCT.identifier)
        i1 = ValueKey(parent=gvi)
        i2 = ValueKey(parent=gvi)
        ib = PlusButtonKey(parent=gvi)
        self.assertListEqual(gvi.children, [i1, i2])
        sv2 = ValueKey(parent=s1, predicate=OWL.versionInfo)
        self.assertListEqual(s1.children, [sv1, gvi, sv2])
        actionsbook = gvs.button.add()
        s2 = gvs.children[1]
        self.assertEqual(len(s2.children), 3)
        self.assertEqual(s2.children[2].predicate, OWL.versionInfo)
        self.assertEqual(len(s2.children[1].children), 1)
        self.assertEqual(len(actionsbook.create), 6)
    
    def test_drop(self):
        """Suppression d'une branche.
        
        """
        r = RootKey()
        t = TabKey(parent=r, label='Général')
        gv = GroupOfValuesKey(parent=t, rdfclass=DCT.PeriodOfTime,
            predicate=DCT.temporal)
        gp1 = GroupOfPropertiesKey(parent=gv)
        v1 = ValueKey(parent=gp1, predicate=DCAT.startDate)
        v2 = ValueKey(parent=gp1, predicate=DCAT.endDate)
        actionsbook = gp1.drop()
        self.assertListEqual(actionsbook.drop, [gp1, v1, v2])

    def test_clean(self):
        """Suppression ou fantômisation a posteriori des groupes qui n'ont pas d'enfants ou que des fantômes.
        
        """
        r = RootKey()
        t = TabKey(parent=r, label='Général')
        gv = GroupOfValuesKey(parent=t, rdfclass=DCT.PeriodOfTime,
            predicate=DCT.temporal)
        gp1 = GroupOfPropertiesKey(parent=gv)
        v1 = ValueKey(parent=gp1, predicate=DCAT.startDate, is_ghost=True,
            value='2021-01-14')
        v2 = ValueKey(parent=gp1, predicate=DCAT.endDate, is_ghost=True,
            value='2021-01-17')
        gp2 = GroupOfPropertiesKey(parent=gv)
        gp3 = GroupOfPropertiesKey(parent=t, rdfclass=DCT.ProvenanceStatement,
            predicate=DCT.provenance)
        v3 = ValueKey(parent=gp3, predicate=RDFS.label)
        self.assertFalse(r.is_ghost)
        self.assertFalse(t.is_ghost)
        self.assertFalse(gv.is_ghost)
        self.assertFalse(gp1.is_ghost)
        self.assertFalse(gp3.is_ghost)
        self.assertTrue(gp1 in gv.children)
        self.assertTrue(gp2 in gv.children)
        actionsbook = r.clean()
        self.assertFalse(r.is_ghost)
        self.assertFalse(t.is_ghost)
        self.assertTrue(gv.is_ghost)
        self.assertTrue(gp1.is_ghost)
        self.assertFalse(gp3.is_ghost)
        self.assertTrue(gp1 in gv.children)
        self.assertFalse(gp2 in gv.children)
        self.assertEqual(len(actionsbook.drop), 3)
        self.assertTrue(gp1 in actionsbook.drop)
        self.assertTrue(gp2 in actionsbook.drop)
        self.assertTrue(gv in actionsbook.drop)
        v3.kill()
        actionsbook = r.clean()
        self.assertTrue(t.is_ghost)
        self.assertTrue(t in actionsbook.drop)
        self.assertTrue(gp3 in actionsbook.drop)

    def test_tree_keys(self):
        """Itérateur sur les clés non fantômes de l'arbre.
        
        """
        r = RootKey()
        g = GroupOfPropertiesKey(parent=r, rdfclass=DCT.RightsStatement,
            predicate=DCT.accessRights)
        m = ValueKey(parent=r, m_twin=g, is_hidden_m=False)
        t = TranslationGroupKey(parent=g, predicate=RDFS.label)
        b = TranslationButtonKey(parent=t)
        w1 = ValueKey(parent=t)
        w2 = ValueKey(parent=t)
        self.assertEqual([k for k in r.tree_keys()], [r, g, t, w1, w2, b, m])

    def test_update(self):
        """Mise à jour massive des attributs.

        """
        r = RootKey()
        g = GroupOfPropertiesKey(parent=r,
            rdfclass=DCT.RightsStatement, predicate=DCT.title)
        g.update(predicate=DCT.accessRights, label="Conditions d'accès")
        self.assertEqual(g.predicate, DCT.accessRights)
        self.assertEqual(g.label, "Conditions d'accès")

    def test_lang_attributes(self):
        """Gestion des propriétés de classe, `langlist` et `main_language`.
        
        """
        r = RootKey()
        r2 = RootKey()
        WidgetKey.langlist = ['fr', 'en']
        r.main_language = 'it'
        self.assertEqual(WidgetKey.langlist, ['it', 'en', 'fr'])
        WidgetKey.langlist = ['de', 'en']
        self.assertEqual(r2.main_language, 'de')

    def test_search_path(self):
        """Recherche dans un arbre de clés à partir du chemin.
        
        """
        r = RootKey()
        g = GroupOfPropertiesKey(parent=r, rdfclass=DCT.RightsStatement,
            predicate=DCT.accessRights)
        m = ValueKey(parent=r, m_twin=g, is_hidden_m=False)
        t = TranslationGroupKey(parent=g, predicate=RDFS.label)
        b = TranslationButtonKey(parent=t)
        w1 = ValueKey(parent=t)
        w2 = ValueKey(parent=t)
        self.assertEqual(r.search_from_path(DCT.accessRights / RDFS.label), t)
        self.assertEqual(r.search_from_path(DCT.accessRights), m)
        m.switch_twin()
        self.assertEqual(r.search_from_path(DCT.accessRights), g)
    
    def test_search_path_tab(self):
        """Recherche dans un arbre de clés à partir du chemin, avec onglet à la racine.
        
        """
        r = RootKey()
        o = TabKey(parent=r, label='Mon onglet')
        v = ValueKey(parent=o, predicate=DCT.title, datatype=RDF.langString)
        self.assertEqual(r.search_from_path(DCT.title), v)
    
    def test_root_key(self):
        """Initialisation d'une clé racine.
        
        """
        rootkey = RootKey(datasetid=URIRef(uuid4().urn))
        self.assertEqual(rootkey.rdfclass, DCAT.Dataset)
        
    def test_group_of_values(self):
        """Gestion des lignes dans un groupe de valeurs.
        
        """
        rootkey = RootKey()
        groupkey = GroupOfValuesKey(parent=rootkey, predicate=DCAT.keyword)
        pluskey = PlusButtonKey(parent=groupkey)
        self.assertFalse(pluskey in groupkey.children)
        #self.assertEqual(pluskey.row, 0)
        self.assertEqual(groupkey.button, pluskey)
        
        valkey1 = ValueKey(parent=groupkey)
        self.assertTrue(valkey1 in groupkey.children)
        self.assertEqual(valkey1.row, 0)
        self.assertEqual(pluskey.row, 1)
        self.assertFalse(pluskey.is_hidden_b)
        self.assertTrue(valkey1.is_single_child)
        self.assertEqual(valkey1.predicate, DCAT.keyword)
        
        valkey2 = ValueKey(parent=groupkey, rowspan=3,
            is_long_text=True)
        self.assertEqual(valkey1.row, 0)
        self.assertEqual(valkey2.row, 1)
        self.assertEqual(pluskey.row, 4)
        self.assertFalse(pluskey.is_hidden_b)
        self.assertFalse(valkey1.is_single_child)
        self.assertFalse(valkey2.is_single_child)
        self.assertEqual(valkey2.predicate, DCAT.keyword)

        valkey1.kill()
        self.assertFalse(valkey1 in groupkey.children)
        self.assertTrue(valkey2.is_single_child)
        self.assertEqual(valkey2.row, 0)
        self.assertEqual(pluskey.row, 3)


    def test_translation_group(self):
        """Gestion des lignes et des langues dans un groupe de traduction.

        """
        rootkey = RootKey()
        WidgetKey.langlist = ['fr', 'en', 'it']
        groupkey = TranslationGroupKey(parent=rootkey,
            predicate=DCT.title)
        transkey = TranslationButtonKey(parent=groupkey)
        self.assertFalse(transkey in groupkey.children)
        self.assertEqual(transkey.row, 0)
        self.assertEqual(groupkey.button, transkey)

        valkey1 = ValueKey(parent=groupkey, rowspan=3,
            is_long_text=True, value_language='fr',
            predicate=RDFS.label)
        self.assertEqual(valkey1.row, 0)
        self.assertEqual(transkey.row, 3)
        self.assertEqual(groupkey.available_languages, ['en', 'it'])
        self.assertEqual(valkey1.predicate, DCT.title)
        self.assertFalse(transkey.is_hidden_b)
        self.assertTrue(valkey1.is_single_child)

        valkey2 = ValueKey(parent=groupkey, rowspan=2,
            is_long_text=True, value_language='en')
        valkey3 = ValueKey(parent=groupkey, rowspan=8,
            value_language='it')
        self.assertEqual(transkey.row, 6)
        self.assertEqual(groupkey.available_languages, [])
        self.assertTrue(transkey.is_hidden_b)
        self.assertFalse(valkey1.is_single_child)
        self.assertEqual(valkey2.predicate, DCT.title)

        valkey2.kill()
        self.assertFalse(valkey2 in groupkey.children)
        self.assertEqual(groupkey.available_languages, ['en'])
        self.assertFalse(transkey.is_hidden_b)
        self.assertEqual(transkey.row, 4)
        self.assertEqual(valkey3.row, 3)

        valkey4 = ValueKey(parent=groupkey, rowspan=2,
            is_long_text=True, value_language='de')
        self.assertTrue(valkey4 in groupkey.children)
        self.assertEqual(groupkey.available_languages, ['en'])
        self.assertFalse(transkey.is_hidden_b)
        valkey4.kill()

        valkey3.change_language('en')
        self.assertEqual(groupkey.available_languages, ['it'])
        self.assertFalse(transkey.is_hidden_b)

        valkey4 = ValueKey(parent=groupkey, rowspan=2,
            is_long_text=True, value_language='de')
        valkey4.change_language('it')
        self.assertEqual(groupkey.available_languages, [])
        self.assertTrue(transkey.is_hidden_b)

    
    def test_ghost(self):
        """Gestion des branches fantômes.
        
        """
        rootkey = RootKey()
        groupkey = GroupOfValuesKey(parent=rootkey, is_ghost=True,
            predicate=DCT.title, rdfclass=FOAF.Agent)
        pluskey = PlusButtonKey(parent=groupkey)
        self.assertIsNone(pluskey)
        editkey = ValueKey(parent=rootkey, rowspan=2,
            predicate=DCT.title)
        
        self.assertIsNone(groupkey.row)
        self.assertEqual(editkey.row, 0)
        
        valkey1 = GroupOfPropertiesKey(parent=groupkey)
        self.assertTrue(valkey1 in groupkey.children)
        self.assertIsNone(valkey1.row)
        self.assertTrue(valkey1.is_ghost)
        self.assertFalse(valkey1.is_single_child)
        self.assertFalse(valkey1.has_minus_button)
        self.assertEqual(valkey1.predicate, DCT.title)

        valkey2 = ValueKey(parent=groupkey, is_ghost=False)
        self.assertIsNone(valkey2)
        valkey2 = ValueKey(parent=groupkey, is_ghost=False,
            value=Literal('Mon fantôme à sauvegarder.',
            lang='fr'))
        self.assertTrue(valkey2.is_ghost)
        self.assertEqual(valkey2.predicate, DCT.title)
        valkey3 = ValueKey(parent=groupkey, is_ghost=False,
            delayed=True)
        self.assertTrue(valkey3.is_ghost)

        groupkey.kill()
        self.assertFalse(groupkey in rootkey.children)
        self.assertEqual(editkey.row, 0)


    def test_hidden_m(self):
        """Gestion des jumelles.
        
        """
        rootkey = RootKey()
        groupkey = GroupOfValuesKey(parent=rootkey, predicate=DCT.title,
            rdfclass=FOAF.Agent)
        buttonkey = PlusButtonKey(parent=groupkey)
        valkey1 = GroupOfPropertiesKey(parent=groupkey, is_hidden_m=True)
        self.assertFalse(valkey1.is_hidden_m)
        valkey2 = ValueKey(parent=groupkey, m_twin=valkey1)
        valkey3 = ValueKey(parent=groupkey)

        self.assertTrue(valkey1 in groupkey.children)
        self.assertTrue(valkey2 in groupkey.children)
        self.assertEqual(valkey1.m_twin, valkey2)
        self.assertEqual(valkey2.m_twin, valkey1)
        self.assertEqual(valkey1.row, 0)
        self.assertEqual(valkey2.row, 0)
        self.assertEqual(valkey3.row, 1)
        self.assertEqual(buttonkey.row, 2)
        self.assertFalse(valkey1.is_single_child)

        self.assertTrue(valkey1.is_hidden_m)
        self.assertFalse(valkey2.is_hidden_m)
        valkey2.switch_twin()
        self.assertTrue(valkey2.is_hidden_m)
        self.assertFalse(valkey1.is_hidden_m)
        
        valkey3.kill()
        self.assertTrue(valkey1.is_single_child)
        self.assertTrue(valkey2.is_single_child)
        self.assertEqual(valkey1.row, 0)
        self.assertEqual(valkey2.row, 0)
        self.assertEqual(buttonkey.row, 1)
        
        valkey3 = ValueKey(parent=groupkey, rowspan=3)
        valkey1.kill()
        self.assertTrue(not valkey1 in groupkey.children)
        self.assertTrue(not valkey2 in groupkey.children)
        self.assertEqual(valkey3.row, 0)
        self.assertTrue(valkey3.is_single_child)
        
        
    def test_delated_computation(self):
        """Calcul a posteriori des lignes et filles uniques.
        
        """
        rootkey = RootKey()
        WidgetKey.langlist = ['fr', 'en', 'it']
        WidgetKey.no_computation = True
        groupkey1 = GroupOfValuesKey(parent=rootkey, predicate=DCT.title,
            rdfclass=FOAF.Agent)
        buttonkey1 = PlusButtonKey(parent=groupkey1)
        valkey1a = GroupOfPropertiesKey(parent=groupkey1)
        valkey1b = ValueKey(parent=groupkey1, rowspan=1, m_twin=valkey1a,
            is_hidden_m=True)
        valkey1c = ValueKey(parent=groupkey1)
        groupkey2 = TranslationGroupKey(parent=rootkey, predicate=DCT.title)
        buttonkey2 = TranslationButtonKey(parent=groupkey2)
        valkey2 = ValueKey(parent=groupkey2, rowspan=2, is_long_text=True,
            value_language='en')
        WidgetKey.no_computation = False
        
        self.assertIsNone(valkey1a.row)
        self.assertIsNone(valkey1b.row)
        self.assertIsNone(valkey1c.row)
        self.assertIsNone(buttonkey1.row)
        self.assertFalse(valkey1a.is_single_child)
        self.assertFalse(valkey1b.is_single_child)
        self.assertFalse(valkey1c.is_single_child)

        self.assertIsNone(valkey2.row)
        self.assertIsNone(buttonkey2.row)
        self.assertFalse(valkey2.is_single_child)
        
        groupkey1.compute_rows()
        self.assertEqual(valkey1a.row, 0)
        self.assertEqual(valkey1b.row, 0)
        self.assertEqual(valkey1c.row, 1)
        self.assertEqual(buttonkey1.row, 2)
        groupkey1.compute_single_children()
        self.assertFalse(valkey1a.is_single_child)
        self.assertFalse(valkey1b.is_single_child)
        self.assertFalse(valkey1c.is_single_child)

        groupkey2.compute_rows()
        self.assertEqual(valkey2.row, 0)
        self.assertEqual(buttonkey2.row, 2)
        groupkey2.compute_single_children()
        self.assertTrue(valkey2.is_single_child)

    def test_actionsbook(self):
        rootkey = RootKey()
        WidgetKey.langlist=['fr', 'en', 'it']
        groupkey1 = GroupOfValuesKey(parent=rootkey, predicate=DCT.title,
            rdfclass=FOAF.Agent)
        buttonkey1 = PlusButtonKey(parent=groupkey1)
        valkey1a = GroupOfPropertiesKey(parent=groupkey1)
        valkey1b = ValueKey(parent=groupkey1, rowspan=1, m_twin=valkey1a,
            is_hidden_m=True)
        valkey1c = ValueKey(parent=groupkey1, rowspan=3, is_long_text=True)
        groupkey2 = TranslationGroupKey(parent=rootkey, predicate=DCT.title)
        buttonkey2 = TranslationButtonKey(parent=groupkey2)
        valkey2a = ValueKey(parent=groupkey2, rowspan=2, is_long_text=True,
            value_language='en')

        WidgetKey.clear_actionsbook()
        valkey1d = ValueKey(parent=groupkey1, rowspan=1)
        actionsbook = WidgetKey.unload_actionsbook()
        self.assertEqual(actionsbook.create, [valkey1d])
        self.assertEqual(actionsbook.drop, [])
        self.assertEqual(actionsbook.move, [buttonkey1])
        self.assertEqual(actionsbook.show_minus_button, [])
        self.assertEqual(actionsbook.hide_minus_button, [])
        self.assertEqual(actionsbook.show, [])
        self.assertEqual(actionsbook.hide, [])
        self.assertEqual(actionsbook.languages, [])

        actionsbook = valkey1a.switch_twin()
        self.assertEqual(actionsbook.create, [])
        self.assertEqual(actionsbook.drop, [])
        self.assertEqual(actionsbook.move, [])
        self.assertEqual(actionsbook.show_minus_button, [])
        self.assertEqual(actionsbook.hide_minus_button, [])
        self.assertEqual(actionsbook.show, [valkey1b])
        self.assertEqual(actionsbook.hide, [valkey1a])
        self.assertEqual(actionsbook.languages, [])

        valkey2b = ValueKey(parent=groupkey2, rowspan=2, value_language='fr')
        actionsbook = WidgetKey.unload_actionsbook()
        self.assertEqual(actionsbook.create, [valkey2b])
        self.assertEqual(actionsbook.drop, [])
        self.assertEqual(actionsbook.move, [buttonkey2])
        self.assertEqual(actionsbook.show_minus_button, [valkey2a])
        self.assertEqual(actionsbook.hide_minus_button, [])
        self.assertEqual(actionsbook.show, [])
        self.assertEqual(actionsbook.hide, [])
        self.assertEqual(actionsbook.languages, [valkey2a])

        valkey2c = ValueKey(parent=groupkey2, rowspan=2, value_language='it')
        actionsbook = WidgetKey.unload_actionsbook()
        self.assertEqual(actionsbook.create, [valkey2c])
        self.assertEqual(actionsbook.drop, [])
        self.assertEqual(actionsbook.move, [buttonkey2])
        self.assertEqual(actionsbook.show_minus_button, [])
        self.assertEqual(actionsbook.hide_minus_button, [])
        self.assertEqual(actionsbook.show, [])
        self.assertEqual(actionsbook.hide, [buttonkey2])
        self.assertEqual(actionsbook.languages, [valkey2a, valkey2b])

        actionsbook = valkey2a.drop()
        self.assertEqual(actionsbook.create, [])
        self.assertEqual(actionsbook.drop, [valkey2a])
        self.assertEqual(actionsbook.move, [valkey2b, valkey2c, buttonkey2])
        self.assertEqual(actionsbook.show_minus_button, [])
        self.assertEqual(actionsbook.hide_minus_button, [])
        self.assertEqual(actionsbook.show, [buttonkey2])
        self.assertEqual(actionsbook.hide, [])
        self.assertEqual(actionsbook.languages, [valkey2b, valkey2c])

        actionsbook = valkey2c.change_language('en')
        self.assertEqual(actionsbook.create, [])
        self.assertEqual(actionsbook.drop, [])
        self.assertEqual(actionsbook.move, [])
        self.assertEqual(actionsbook.show_minus_button, [])
        self.assertEqual(actionsbook.hide_minus_button, [])
        self.assertEqual(actionsbook.show, [])
        self.assertEqual(actionsbook.hide, [])
        self.assertEqual(actionsbook.languages, [valkey2b, valkey2c])

        actionsbook = valkey2b.drop()
        self.assertEqual(actionsbook.create, [])
        self.assertEqual(actionsbook.drop, [valkey2b])
        self.assertEqual(actionsbook.move, [valkey2c, buttonkey2])
        self.assertEqual(actionsbook.show_minus_button, [])
        self.assertEqual(actionsbook.hide_minus_button, [valkey2c])
        self.assertEqual(actionsbook.show, [])
        self.assertEqual(actionsbook.hide, [])
        self.assertEqual(actionsbook.languages, [valkey2c])
 

if __name__ == '__main__':
    unittest.main()

