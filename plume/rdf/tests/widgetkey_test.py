
import unittest
from uuid import uuid4

from plume.rdf.rdflib import URIRef, Literal
from plume.rdf.namespaces import (
    RDFS, DCT, DCAT, FOAF, RDF, OWL, SKOS, XSD, GSP
)
from plume.rdf.widgetkey import (
    WidgetKey, ValueKey, GroupOfPropertiesKey, GroupOfValuesKey,
    TranslationGroupKey, TranslationButtonKey, PlusButtonKey, RootKey,
    TabKey
)

class WidgetKeyTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Réinitialisation des attributs partagés.
        
        Notes
        -----
        Précaution nécessaire quand plusieurs modules sont testés
        successivement, car chaque appel la classe 
        :py:class:`plume.rdf.widgetsdict.WidgetsDict` est susceptible
        d'affecter l'état des attributs partagés. Ce n'est pas un problème
        pour la création de nouveaux dictionnaires puisque les attributs
        sont systématiquement redéfinis, mais ça l'est quand on opère
        directement sur les clés comme c'est le cas ici.
        
        """
        WidgetKey.reinitiate_shared_attributes()

    def test_is_empty(self):
        """Méthode d'identification des clés vides.
        
        """
        r = RootKey()
        t = TabKey(parent=r, label='Général')
        g = GroupOfValuesKey(parent=t, predicate=DCT.conformsTo,
            rdfclass=DCT.Standard, sources=[
            URIRef('http://www.opengis.net/def/crs/EPSG/0'),
            URIRef('http://registre.data.developpement-durable.gouv.fr/plume/DataServiceStandard')])
        b = PlusButtonKey(parent=g)
        p1 = GroupOfPropertiesKey(parent=g)
        v1 = ValueKey(parent=g, m_twin=p1, is_hidden_m=True,
            value_source=URIRef('http://www.opengis.net/def/crs/EPSG/0'))
        p2 = GroupOfPropertiesKey(parent=g)
        v2 = ValueKey(parent=g, m_twin=p2, is_hidden_m=False,
            value_source=URIRef('http://registre.data.developpement-durable.gouv.fr/plume/DataServiceStandard'))
        # groupe vide
        self.assertTrue(g.is_empty())
        self.assertTrue(g.is_empty(sources=URIRef('http://registre.data.developpement-durable.gouv.fr/plume/DataServiceStandard')))
        # groupe avec une clé-valeur remplie
        v2.value = URIRef('http://www.opengis.net/def/serviceType/ogc/wfs')
        self.assertFalse(g.is_empty())
        self.assertFalse(g.is_empty(sources=URIRef('http://registre.data.developpement-durable.gouv.fr/plume/DataServiceStandard')))
        self.assertTrue(g.is_empty(sources=URIRef('http://www.opengis.net/def/crs/EPSG/0')))
        v2.value = None
        # groupe avec un groupe de propriétés non vide
        p1v = ValueKey(parent=p1, predicate=DCT.title)
        self.assertTrue(p1v.is_empty())
        self.assertTrue(p1.is_empty())
        self.assertTrue(g.is_empty())
        self.assertTrue(g.is_empty(sources=URIRef('http://registre.data.developpement-durable.gouv.fr/plume/DataServiceStandard')))
        p1v.value = Literal('Mon standard', lang='fr')
        self.assertFalse(p1v.is_empty())
        self.assertFalse(p1.is_empty())
        self.assertFalse(g.is_empty())
        self.assertTrue(g.is_empty(sources=URIRef('http://registre.data.developpement-durable.gouv.fr/plume/DataServiceStandard')))

    def test_shrink_expend(self):
        """Préparation d'un groupe de valeurs en vue d'un import massif.
        
        """
        r = RootKey()
        t = TabKey(parent=r, label='Général')
        g = GroupOfValuesKey(parent=t, predicate=DCT.conformsTo,
            rdfclass=DCT.Standard, sources=[
            URIRef('http://www.opengis.net/def/crs/EPSG/0'),
            URIRef('http://registre.data.developpement-durable.gouv.fr/plume/DataServiceStandard')])
        b = PlusButtonKey(parent=g)
        p1 = GroupOfPropertiesKey(parent=g)
        v1 = ValueKey(parent=g, m_twin=p1, is_hidden_m=True,
            value_source=URIRef('http://www.opengis.net/def/crs/EPSG/0'))
        p2 = GroupOfPropertiesKey(parent=g)
        v2 = ValueKey(
            parent=g, m_twin=p2, is_hidden_m=False,
            value_source=URIRef('http://registre.data.developpement-durable.gouv.fr/plume/DataServiceStandard'),
            value=URIRef('http://www.opengis.net/def/interface/ogcapi-features')
        )
        p3 = GroupOfPropertiesKey(parent=g)
        v3 = ValueKey(
            parent=g, m_twin=p3, is_hidden_m=False,
            value_source=URIRef('http://www.opengis.net/def/crs/EPSG/0'),
            value=URIRef('http://www.opengis.net/def/crs/EPSG/0/2154')
        )
        # --- en préservant tout ---
        WidgetKey.clear_actionsbook()
        l1 = g.shrink_expend(2, sources=[])
        a = WidgetKey.unload_actionsbook()
        self.assertTrue(all(k in g.children for k in (p1, v1, p2, v2, p3, v3)))
        self.assertFalse(any(k in l1 for k in (p1, v1, p2, v2, p3, v3)))
        self.assertEqual(len(l1), 2)
        self.assertEqual(len(g.children), 10)
        self.assertTrue(all(isinstance(k, ValueKey) for k in l1))
        self.assertTrue(v1.is_hidden)
        self.assertFalse(any(k.is_hidden for k in l1))
        self.assertTrue(all(k in a.create for k in l1))
        self.assertTrue(all(k.m_twin in a.create for k in l1))
        self.assertEqual(len(a.create), 4)
        self.assertFalse(a.drop)
        # --- en ne réinitialisant qu'une seule source ---
        WidgetKey.clear_actionsbook()
        l2 = g.shrink_expend(1, sources=[URIRef('http://www.opengis.net/def/crs/EPSG/0')])
        a = WidgetKey.unload_actionsbook()
        self.assertTrue(all(k in g.children for k in (p1, v1, p2, v2, p3, v3)))
        self.assertFalse(any(k in g.children for k in l1))
        self.assertFalse(any(k.m_twin in g.children for k in l1))
        self.assertTrue(v3 in l2)
        self.assertFalse(any(k in l2 for k in (p1, v1, p2, v2)))
        self.assertFalse(any(k in l2 for k in l1))
        self.assertEqual(len(l2), 1)
        self.assertEqual(len(g.children), 6)
        self.assertTrue(v1.is_hidden)
        self.assertFalse(v3.is_hidden)
        self.assertFalse(a.create)
        self.assertTrue(all(k in a.drop for k in l1))
        self.assertTrue(all(k.m_twin in a.drop for k in l1))
        self.assertEqual(len(a.drop), 4)
        # --- en réinitialisant toutes les sources ---
        WidgetKey.clear_actionsbook()
        l3 = g.shrink_expend(2)
        a = WidgetKey.unload_actionsbook()
        self.assertListEqual(g.children, [p1, v1, p2, v2])
        self.assertListEqual(l3, [v1, v2])
        self.assertFalse(any(k.is_hidden for k in l3))
        self.assertListEqual(a.drop, [v3, p3])
        self.assertFalse(a.create)
        self.assertListEqual(a.hide, [p1])

    def test_shrink_expend_read_only(self):
        """Préparation d'un groupe de valeurs en lecture seule en vue d'un import massif.
        
        """
        r = RootKey()
        t = TabKey(parent=r, label='Général')
        g = GroupOfValuesKey(parent=t, predicate=DCT.conformsTo,
            rdfclass=DCT.Standard, sources=[
            URIRef('http://www.opengis.net/def/crs/EPSG/0'),
            URIRef('http://registre.data.developpement-durable.gouv.fr/plume/DataServiceStandard')],
            is_read_only=True)
        b = PlusButtonKey(parent=g)
        self.assertTrue(b.is_hidden_b)
        p1 = GroupOfPropertiesKey(parent=g)
        v1 = ValueKey(parent=g, m_twin=p1, is_hidden_m=False,
            value_source=URIRef('http://www.opengis.net/def/crs/EPSG/0'))
        WidgetKey.clear_actionsbook()
        l = g.shrink_expend(2, sources=[URIRef('http://www.opengis.net/def/crs/EPSG/0')])
        a = WidgetKey.unload_actionsbook()
        self.assertEqual(len(l), 2)
        self.assertEqual(len(a.create), 2)
        self.assertEqual(a.create[0].m_twin, a.create[1])

    def test_shrink_expend_special_cases(self):
        """Préparation d'un groupe de valeurs en vue d'un import massif : cas particuliers.
        
        Les tests partent du principe qu'il y aura au moins une clé-valeur
        non fantôme dans le groupe susceptible d'être utilisée ou copiée.

        """
        r = RootKey()
        t = TabKey(parent=r, label='Général')
        g = GroupOfValuesKey(
            parent=t,
            predicate=DCT.conformsTo,
            rdfclass=DCT.Standard,
            sources=[
                URIRef('http://www.opengis.net/def/crs/EPSG/0')
            ]
        )
        b = PlusButtonKey(parent=g)
        v = ValueKey(parent=g, value_source=URIRef('http://www.opengis.net/def/crs/EPSG/0'))
        l = g.shrink_expend(2)
        self.assertEqual(len(l), 2)
        self.assertTrue(all(isinstance(key, ValueKey) for key in l))
        self.assertEqual(len(g.children), 2)

        r = RootKey()
        t = TabKey(parent=r, label='Général')
        g = GroupOfValuesKey(
            parent=t,
            predicate=DCT.conformsTo,
            rdfclass=DCT.Standard,
            sources=[
                URIRef('http://www.opengis.net/def/crs/EPSG/0'),
                URIRef('http://registre.data.developpement-durable.gouv.fr/plume/DataServiceStandard')
            ]
        )
        b = PlusButtonKey(parent=g)
        v = ValueKey(
            parent=g,
            value_source=URIRef('http://registre.data.developpement-durable.gouv.fr/plume/DataServiceStandard'),
            value=URIRef('http://www.opengis.net/def/interface/ogcapi-features')
        )
        l = g.shrink_expend(2, sources=[URIRef('http://www.opengis.net/def/crs/EPSG/0')])
        self.assertEqual(len(l), 2)
        self.assertTrue(all(isinstance(key, ValueKey) for key in l))
        self.assertTrue(not v in l)
        self.assertEqual(len(g.children), 3)

        r = RootKey()
        t = TabKey(parent=r, label='Général')
        g = GroupOfValuesKey(
            parent=t,
            predicate=DCT.conformsTo,
            rdfclass=DCT.Standard,
            sources=[
                URIRef('http://www.opengis.net/def/crs/EPSG/0'),
                URIRef('http://registre.data.developpement-durable.gouv.fr/plume/DataServiceStandard')
            ]
        )
        b = PlusButtonKey(parent=g)
        v = ValueKey(
            parent=g,
            value_source=URIRef('http://registre.data.developpement-durable.gouv.fr/plume/DataServiceStandard')
            # pas de valeur
        )
        l = g.shrink_expend(2, sources=[URIRef('http://www.opengis.net/def/crs/EPSG/0')])
        self.assertEqual(len(l), 2)
        self.assertTrue(all(isinstance(key, ValueKey) for key in l))
        self.assertTrue(v in l)
        self.assertEqual(len(g.children), 2)

        r = RootKey()
        t = TabKey(parent=r, label='Général')
        g = GroupOfValuesKey(
            parent=t,
            predicate=DCT.conformsTo,
            rdfclass=DCT.Standard,
            sources=[
                URIRef('http://www.opengis.net/def/crs/EPSG/0')
            ]
        )
        b = PlusButtonKey(parent=g)
        p = GroupOfPropertiesKey(parent=g)
        v = ValueKey(parent=g, value_source=URIRef('http://www.opengis.net/def/crs/EPSG/0'))
        l = g.shrink_expend(2)
        self.assertEqual(len(l), 2)
        self.assertTrue(all(isinstance(key, ValueKey) for key in l))
        self.assertEqual(len(g.children), 3)

        r = RootKey()
        t = TabKey(parent=r, label='Général')
        g = GroupOfValuesKey(
            parent=t,
            predicate=DCT.conformsTo,
            rdfclass=DCT.Standard,
            sources=[
                URIRef('http://www.opengis.net/def/crs/EPSG/0')
            ]
        )
        b = PlusButtonKey(parent=g)
        v = ValueKey(parent=g, value_source=URIRef('http://www.opengis.net/def/crs/EPSG/0'))
        p = GroupOfPropertiesKey(parent=g)
        l = g.shrink_expend(2)
        self.assertEqual(len(l), 2)
        self.assertTrue(all(isinstance(key, ValueKey) for key in l))
        self.assertEqual(len(g.children), 3)

        r = RootKey()
        t = TabKey(parent=r, label='Général')
        g = GroupOfValuesKey(
            parent=t,
            predicate=DCT.conformsTo,
            rdfclass=DCT.Standard,
            sources=[
                URIRef('http://www.opengis.net/def/crs/EPSG/0')
            ]
        )
        b = PlusButtonKey(parent=g)
        p = GroupOfPropertiesKey(parent=g)
        v = ValueKey(
            parent=g,
            value_source=URIRef('http://www.opengis.net/def/crs/EPSG/0'),
            m_twin=p,
            is_hidden_m=False
        )
        l = g.shrink_expend(2)
        self.assertEqual(len(l), 2)
        self.assertTrue(all(isinstance(key, ValueKey) for key in l))
        self.assertEqual(len(g.children), 4)
        self.assertTrue(v in l)

        r = RootKey()
        t = TabKey(parent=r, label='Général')
        g = GroupOfValuesKey(
            parent=t,
            predicate=DCT.conformsTo,
            rdfclass=DCT.Standard,
            sources=[
                URIRef('http://www.opengis.net/def/crs/EPSG/0')
            ]
        )
        b = PlusButtonKey(parent=g)
        p = GroupOfPropertiesKey(parent=g)
        v = ValueKey(
            parent=g,
            value_source=URIRef('http://www.opengis.net/def/crs/EPSG/0'),
            m_twin=p,
            is_hidden_m=True
        )
        l = g.shrink_expend(2)
        self.assertEqual(len(l), 2)
        self.assertTrue(all(isinstance(key, ValueKey) for key in l))
        self.assertEqual(len(g.children), 4)
        self.assertTrue(v in l)

        r = RootKey()
        t = TabKey(parent=r, label='Général')
        g = GroupOfValuesKey(
            parent=t,
            predicate=DCT.conformsTo,
            rdfclass=DCT.Standard,
            sources=[
                URIRef('http://www.opengis.net/def/crs/EPSG/0')
            ]
        )
        b = PlusButtonKey(parent=g)
        p = GroupOfPropertiesKey(parent=g)
        v = ValueKey(
            parent=g,
            value_source=URIRef('http://www.opengis.net/def/crs/EPSG/0'),
            m_twin=p,
            is_hidden_m=True
        )
        l = g.shrink_expend(2, sources=[URIRef('http://www.opengis.net/def/crs/EPSG/0')])
        self.assertEqual(len(l), 2)
        self.assertTrue(all(isinstance(key, ValueKey) for key in l))
        self.assertEqual(len(g.children), 6)
        self.assertFalse(v in l)

        WidgetKey.clear_actionsbook()

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
        self.assertEqual(v2.unit_button_placement[1], 3)
        self.assertEqual(v2.minus_button_placement[1], 5)
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
        actionsbook = gp1.drop(drop_single_children=True)
        self.assertListEqual(actionsbook.drop, [gp1, v1, v2])

    def test_drop_multiple_keys(self):
        """Suppression successive de plusieurs clés."""
        r = RootKey()
        t = TabKey(parent=r, label='Général')
        gv = GroupOfValuesKey(parent=t, predicate=DCAT.keyword)
        v1 = ValueKey(parent=gv, value=Literal('mot clé 1', lang='fr'))
        v2 = ValueKey(parent=gv, value=Literal('mot clé 2', lang='fr'))
        v3 = ValueKey(parent=gv, value=Literal('mot clé 3', lang='fr'))
        v4 = ValueKey(parent=gv, value=Literal('mot clé 4', lang='fr'))
        v5 = ValueKey(parent=gv, value=Literal('mot clé 5', lang='fr'))
        self.assertListEqual(gv.children, [v1, v2, v3, v4, v5])
        WidgetKey.clear_actionsbook()
        self.assertListEqual(WidgetKey.actionsbook.drop, [])
        self.assertFalse(v1.is_hidden)
        self.assertTrue(v1.has_minus_button)
        self.assertFalse(v1.is_single_child)

        actionsbook = v1.drop(append_book=True)
        self.assertListEqual(gv.children, [v2, v3, v4, v5])
        self.assertListEqual(actionsbook.drop, [v1])
        self.assertListEqual(WidgetKey.actionsbook.drop, [v1])

        actionsbook = v2.drop(append_book=True)
        self.assertListEqual(WidgetKey.actionsbook.drop, [v1, v2])
        self.assertListEqual(actionsbook.drop, [v1, v2])

        actionsbook = v3.drop()
        self.assertListEqual(WidgetKey.actionsbook.drop, [])
        self.assertListEqual(actionsbook.drop, [v3])

        actionsbook = v4.drop(append_book=True)
        self.assertListEqual(WidgetKey.actionsbook.drop, [v4])
        self.assertListEqual(actionsbook.drop, [v4])
        self.assertFalse(v5.is_hidden)
        self.assertTrue(v5.has_minus_button)
        self.assertTrue(v5.is_single_child)

        actionsbook = v5.drop(append_book=True)
        self.assertListEqual(WidgetKey.actionsbook.drop, [v4])
        self.assertListEqual(actionsbook.drop, [v4])
        actionsbook = v5.drop()
        self.assertListEqual(WidgetKey.actionsbook.drop, [])
        self.assertListEqual(actionsbook.drop, [])
        actionsbook = v5.drop(drop_single_children=True)
        self.assertListEqual(WidgetKey.actionsbook.drop, [])
        self.assertListEqual(actionsbook.drop, [v5])

        WidgetKey.clear_actionsbook()

    def test_drop_multiple_groups_of_properties(self):
        """Suppression successive de plusieurs groupes de propriétés."""
        r = RootKey()
        t = TabKey(parent=r, label='Général')
        gv = GroupOfValuesKey(parent=t, rdfclass=DCT.PeriodOfTime,
            predicate=DCT.temporal)
        gp1 = GroupOfPropertiesKey(parent=gv)
        v1 = ValueKey(parent=gp1, predicate=DCAT.startDate)
        v2 = ValueKey(parent=gp1, predicate=DCAT.endDate)
        gp2 = GroupOfPropertiesKey(parent=gv)
        v3 = ValueKey(parent=gp2, predicate=DCAT.startDate)
        v4 = ValueKey(parent=gp2, predicate=DCAT.endDate)
        gp3 = GroupOfPropertiesKey(parent=gv)
        v5 = ValueKey(parent=gp3, predicate=DCAT.startDate)
        v6 = ValueKey(parent=gp3, predicate=DCAT.endDate)
        WidgetKey.clear_actionsbook()

        actionsbook = gp1.drop(append_book=True)
        self.assertListEqual(actionsbook.drop, [gp1, v1, v2])

        actionsbook = gp2.drop(append_book=True)
        self.assertListEqual(actionsbook.drop, [gp1, v1, v2, gp2, v3, v4])

        actionsbook = gp3.drop(append_book=True)
        self.assertListEqual(actionsbook.drop, [gp1, v1, v2, gp2, v3, v4])

        self.assertListEqual(gv.children, [gp3])
        self.assertListEqual(gp3.children, [v5, v6])

        WidgetKey.clear_actionsbook()

    def test_drop_multiple_keys_with_twins(self):
        """Suppression successive de plusieurs clés, avec jumelles."""
        r = RootKey()
        t = TabKey(parent=r, label='Général')
        g = GroupOfValuesKey(
            parent=t,
            predicate=DCT.conformsTo,
            rdfclass=DCT.Standard,
            sources=[
                URIRef('http://www.opengis.net/def/crs/EPSG/0')
            ]
        )
        b = PlusButtonKey(parent=g)
        p1 = GroupOfPropertiesKey(parent=g)
        v1 = ValueKey(
            parent=g,
            value_source=URIRef('http://www.opengis.net/def/crs/EPSG/0'),
            m_twin=p1,
            is_hidden_m=True
        )
        v2 = ValueKey(
            parent=g,
            value_source=URIRef('http://www.opengis.net/def/crs/EPSG/0')
        )
        p2 = GroupOfPropertiesKey(
            parent=g,
            m_twin=v2,
            is_hidden_m=True
        )
        v3 = ValueKey(
            parent=g,
            value_source=URIRef('http://www.opengis.net/def/crs/EPSG/0')
        )
        p3 = GroupOfPropertiesKey(
            parent=g,
            m_twin=v3,
            is_hidden_m=True
        )
        self.assertTrue(v1.is_hidden)
        self.assertFalse(p1.is_hidden)
        self.assertFalse(v2.is_hidden)
        self.assertTrue(p2.is_hidden)
        self.assertFalse(v3.is_hidden)
        self.assertTrue(p3.is_hidden)
        self.assertListEqual(g.children, [p1, v1, v2, p2, v3, p3])

        WidgetKey.clear_actionsbook()

        actionsbook = v1.drop(append_book=True)
        self.assertListEqual(actionsbook.drop, [])
        self.assertListEqual(g.children, [p1, v1, v2, p2, v3, p3])

        actionsbook = p1.drop(append_book=True)
        self.assertListEqual(actionsbook.drop, [p1, v1])
        self.assertListEqual(g.children, [v2, p2, v3, p3])

        actionsbook = p2.drop(append_book=True)
        self.assertListEqual(actionsbook.drop, [p1, v1])
        self.assertListEqual(g.children, [v2, p2, v3, p3])

        actionsbook = v2.drop(append_book=True)
        self.assertListEqual(actionsbook.drop, [p1, v1, v2, p2])
        self.assertListEqual(g.children, [v3, p3])

        actionsbook = v3.drop(append_book=True)
        self.assertListEqual(actionsbook.drop, [p1, v1, v2, p2])
        self.assertListEqual(g.children, [v3, p3])

        g.is_read_only = True
        actionsbook = v3.drop(append_book=True)
        self.assertListEqual(actionsbook.drop, [p1, v1, v2, p2, v3, p3])
        self.assertListEqual(g.children, [])

        self.assertListEqual(actionsbook.move, [b])

        WidgetKey.clear_actionsbook()

    def test_drop_value_key(self):
        """Suppression d'une clé valeur."""
        r = RootKey()
        t = TabKey(parent=r, label='Général')
        vtitle = ValueKey(
            parent=t, predicate=DCT.title,
            value=Literal('Mon jeu de données', lang='fr'),
            is_read_only=False
            )
        vdescr = ValueKey(
            parent=t, predicate=DCT.description,
            value=Literal("C'est un jeu de données.", lang='fr'),
            is_read_only=True
            )

        # clé qui n'est pas en lecture seule
        actionsbook = vtitle.drop()
        self.assertListEqual(t.children, [vtitle, vdescr])
        for k, v in actionsbook.__dict__.items():
            with self.subTest(actionsbook_attribute = k):
                self.assertListEqual(v, [])

        # clé en lecture seule
        actionsbook = vdescr.drop()
        self.assertListEqual(t.children, [vtitle])
        for k, v in actionsbook.__dict__.items():
            with self.subTest(actionsbook_attribute = k):
                if k == 'drop':
                    self.assertListEqual(v, [vdescr])
                else:
                    self.assertListEqual(v, [])
    
    def test_clean_after_drop(self):
        """Nettoyage de l'arbre des clés après des suppressions."""
        r = RootKey()
        tgeneral = TabKey(parent=r, label='Général')
        vtitle = ValueKey(
            parent=tgeneral, predicate=DCT.title,
            value=Literal('Mon jeu de données', lang='fr'),
            is_read_only=True
            )
        gkeywords = GroupOfValuesKey(parent=tgeneral, predicate=DCAT.keyword, is_read_only=True)
        vkeyword1 = ValueKey(parent=gkeywords, value=Literal('mot clé 1', lang='fr'))
        vkeyword2 = ValueKey(parent=gkeywords, value=Literal('mot clé 2', lang='fr'))
        tothers = TabKey(parent=r, label='Autres')
        grights = GroupOfPropertiesKey(
            parent=tothers, rdfclass=DCT.RightsStatement,
            predicate=DCT.rights
            )
        vrigthslabel = ValueKey(parent=grights, predicate=RDFS.label, is_read_only=True)
        gaccessrights = GroupOfPropertiesKey(
            parent=tothers, rdfclass=DCT.RightsStatement,
            predicate=DCT.accessRights, is_ghost=True
            )
        vaccessrigthslabel = ValueKey(
            parent=gaccessrights, predicate=RDFS.label, value='Accès public'
        )

        WidgetKey.clear_actionsbook(allow_ghosts=True)

        actionsbook = vtitle.drop(append_book=True)
        self.assertListEqual(actionsbook.drop, [vtitle])
        self.assertListEqual(actionsbook.move, [gkeywords])
        self.assertListEqual(actionsbook.modified, [gkeywords])
        for k, v in actionsbook.__dict__.items():
            with self.subTest(actionsbook_attribute = k):
                if not k in ('drop', 'move', 'modified'):
                    self.assertListEqual(v, [])
        
        actionsbook = vkeyword1.drop(append_book=True)
        self.assertListEqual(actionsbook.drop, [vtitle, vkeyword1])
        self.assertListEqual(actionsbook.move, [gkeywords, vkeyword2])
        self.assertListEqual(actionsbook.modified, [gkeywords, vkeyword2])
        for k, v in actionsbook.__dict__.items():
            with self.subTest(actionsbook_attribute = k):
                if not k in ('drop', 'move', 'modified'):
                    self.assertListEqual(v, [])
        
        actionsbook = vkeyword2.drop(append_book=True)
        self.assertListEqual(actionsbook.drop, [vtitle, vkeyword1, vkeyword2])
        self.assertListEqual(actionsbook.move, [gkeywords])
        self.assertListEqual(actionsbook.modified, [gkeywords])
        for k, v in actionsbook.__dict__.items():
            with self.subTest(actionsbook_attribute = k):
                if not k in ('drop', 'move', 'modified'):
                    self.assertListEqual(v, [])

        actionsbook = r.clean(append_book=True)
        self.assertListEqual(actionsbook.drop, [vtitle, vkeyword1, vkeyword2, gkeywords, tgeneral])
        self.assertListEqual(actionsbook.move, [tothers])
        self.assertListEqual(actionsbook.modified, [tothers])
        for k, v in actionsbook.__dict__.items():
            with self.subTest(actionsbook_attribute = k):
                if not k in ('drop', 'move', 'modified'):
                    self.assertListEqual(v, [])
        self.assertListEqual(r.children, [tothers])

        actionsbook = vrigthslabel.drop(append_book=True)
        self.assertListEqual(actionsbook.drop, [vtitle, vkeyword1, vkeyword2, gkeywords, tgeneral, vrigthslabel])
        self.assertListEqual(actionsbook.move, [tothers])
        self.assertListEqual(actionsbook.modified, [tothers])
        for k, v in actionsbook.__dict__.items():
            with self.subTest(actionsbook_attribute = k):
                if not k in ('drop', 'move', 'modified'):
                    self.assertListEqual(v, [])

        actionsbook = r.clean(append_book=True)
        self.assertListEqual(actionsbook.drop, [vtitle, vkeyword1, vkeyword2, gkeywords, tgeneral, vrigthslabel, grights, tothers])
        for k, v in actionsbook.__dict__.items():
            with self.subTest(actionsbook_attribute = k):
                if not k in ('drop',):
                    self.assertListEqual(v, [])
        self.assertListEqual(r.children, [tothers])
        self.assertTrue(tothers.is_hidden)
        self.assertListEqual(tothers.children, [gaccessrights])
        self.assertTrue(gaccessrights.is_hidden)
        self.assertListEqual(gaccessrights.children, [vaccessrigthslabel])
        self.assertTrue(vaccessrigthslabel.is_hidden)

        WidgetKey.clear_actionsbook()

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
        self.assertEqual(WidgetKey.langlist, ['it', 'fr', 'en'])
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
        d = ValueKey(parent=r, is_ghost=True, predicate=DCT.description)
        self.assertEqual(r.search_from_path(DCT.accessRights / RDFS.label), t)
        self.assertEqual(r.search_from_path(DCT.accessRights), m)
        m.switch_twin()
        self.assertEqual(r.search_from_path(DCT.accessRights), g)
        self.assertIsNone(r.search_from_path(DCT.description))
        self.assertEqual(r.search_from_path(DCT.description, allow_ghosts=True), d)
    
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
        valkey3 = ValueKey(parent=rootkey, predicate=DCAT.temporalResolution,
            datatype=XSD.duration)

        WidgetKey.clear_actionsbook()
        valkey1d = ValueKey(parent=groupkey1, rowspan=1)
        actionsbook = WidgetKey.unload_actionsbook()
        self.assertEqual(actionsbook.create, [valkey1d])
        self.assertEqual(actionsbook.move, [buttonkey1])
        self.assertEqual(actionsbook.modified, [buttonkey1])
        for a, alist in actionsbook.__dict__.items():
            with self.subTest(actionsbook_attr = a):
                if not a in ('modified', 'create', 'move'):
                    self.assertFalse(alist)

        actionsbook = valkey1a.switch_twin()
        self.assertEqual(actionsbook.show, [valkey1b])
        self.assertEqual(actionsbook.hide, [valkey1a])
        self.assertEqual(actionsbook.modified, [valkey1a, valkey1b])
        for a, alist in actionsbook.__dict__.items():
            with self.subTest(actionsbook_attr = a):
                if not a in ('modified', 'show', 'hide'):
                    self.assertFalse(alist)

        valkey2b = ValueKey(parent=groupkey2, rowspan=2, value_language='fr')
        actionsbook = WidgetKey.unload_actionsbook()
        self.assertEqual(actionsbook.create, [valkey2b])
        self.assertEqual(actionsbook.move, [buttonkey2])
        self.assertEqual(actionsbook.show_minus_button, [valkey2a])
        self.assertEqual(actionsbook.languages, [valkey2a])
        self.assertEqual(actionsbook.modified, [valkey2a, buttonkey2])
        for a, alist in actionsbook.__dict__.items():
            with self.subTest(actionsbook_attr = a):
                if not a in ('modified', 'create', 'move',
                    'show_minus_button', 'languages'):
                    self.assertFalse(alist)

        valkey2c = ValueKey(parent=groupkey2, rowspan=2, value_language='it')
        actionsbook = WidgetKey.unload_actionsbook()
        self.assertEqual(actionsbook.create, [valkey2c])
        self.assertEqual(actionsbook.move, [buttonkey2])
        self.assertEqual(actionsbook.hide, [buttonkey2])
        self.assertEqual(actionsbook.languages, [valkey2a, valkey2b])
        self.assertEqual(actionsbook.modified, [valkey2a, valkey2b, buttonkey2])
        for a, alist in actionsbook.__dict__.items():
            with self.subTest(actionsbook_attr = a):
                if not a in ('modified', 'create', 'move',
                    'hide', 'languages'):
                    self.assertFalse(alist)

        actionsbook = valkey2a.drop()
        self.assertEqual(actionsbook.drop, [valkey2a])
        self.assertEqual(actionsbook.move, [valkey2b, valkey2c, buttonkey2])
        self.assertEqual(actionsbook.show, [buttonkey2])
        self.assertEqual(actionsbook.languages, [valkey2b, valkey2c])
        self.assertEqual(actionsbook.modified, [valkey2b, valkey2c, buttonkey2])
        for a, alist in actionsbook.__dict__.items():
            with self.subTest(actionsbook_attr = a):
                if not a in ('modified', 'drop', 'move', 'show',
                    'languages'):
                    self.assertFalse(alist)

        actionsbook = valkey2c.change_language('en')
        self.assertEqual(actionsbook.languages, [valkey2b, valkey2c])
        self.assertEqual(actionsbook.modified, [valkey2b, valkey2c])
        for a, alist in actionsbook.__dict__.items():
            with self.subTest(actionsbook_attr = a):
                if not a in ('modified', 'languages'):
                    self.assertFalse(alist)

        actionsbook = valkey2b.drop()
        self.assertEqual(actionsbook.drop, [valkey2b])
        self.assertEqual(actionsbook.move, [valkey2c, buttonkey2])
        self.assertEqual(actionsbook.hide_minus_button, [valkey2c])
        self.assertEqual(actionsbook.languages, [valkey2c])
        self.assertEqual(actionsbook.modified, [valkey2c, buttonkey2])
        for a, alist in actionsbook.__dict__.items():
            with self.subTest(actionsbook_attr = a):
                if not a in ('modified', 'drop', 'languages',
                    'hide_minus_button', 'move'):
                    self.assertFalse(alist)

        actionsbook = valkey3.change_unit('jours')
        self.assertEqual(actionsbook.units, [valkey3])
        self.assertEqual(actionsbook.modified, [valkey3])
        for a, alist in actionsbook.__dict__.items():
            with self.subTest(actionsbook_attr = a):
                if not a in ('modified', 'units'):
                    self.assertFalse(alist)
        
        valkey3.value = Literal('PT3H20M')
        actionsbook = WidgetKey.unload_actionsbook()
        self.assertEqual(actionsbook.update, [valkey3])
        self.assertEqual(actionsbook.units, [valkey3])
        self.assertEqual(actionsbook.modified, [valkey3])
        for a, alist in actionsbook.__dict__.items():
            with self.subTest(actionsbook_attr = a):
                if not a in ('modified', 'units', 'update'):
                    self.assertFalse(alist)
        

if __name__ == '__main__':
    unittest.main()

