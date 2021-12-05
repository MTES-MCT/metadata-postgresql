
import unittest

from rdflib import URIRef, DC, RDFS

from plume.rdf.actionsbook import ActionsBook
from plume.rdf.widgetkey import RootKey, ObjectKey, GroupOfPropertiesKey, \
     TranslationGroupKey, ValueKey, WidgetKey, TranslationButtonKey, \
     GroupOfValuesKey

class ActionsBookTestCase(unittest.TestCase):

    def test_no_ghost(self):
        """Non enregistrement des clés fantômes dans les carnets d'action.

        """
        r = RootKey()
        g = ObjectKey(parent=r, is_ghost=True, predicate=DC.title,
            path='dct:title')
        w = ObjectKey(parent=r, predicate=DC.description,
            path='dct:description')
        a = WidgetKey.unload_actionsbook()
        self.assertEqual(a.create, [r, w])

    def test_visible(self):
        """Pas de clés masquées dans les listes de clés à afficher.
        
        """
        r = RootKey()
        WidgetKey.langlist = ['fr', 'en']
        g = GroupOfPropertiesKey(parent=r,
            rdftype=URIRef('http://purl.org/dc/terms/RightsStatement'),
            predicate=URIRef('http://purl.org/dc/terms/accessRights'),
            path='dct:accessRights')
        m = ValueKey(parent=r, m_twin=g, is_hidden_m=False)
        t = TranslationGroupKey(parent=g, predicate=RDFS.label,
            path='dct:accessRights / rdfs:label')
        b = TranslationButtonKey(parent=t)
        self.assertFalse(b.is_hidden_b)
        w1 = ValueKey(parent=t)
        w2 = ValueKey(parent=t)
        self.assertTrue(b.is_hidden_b)
        self.assertFalse(w1.is_single_child)
        a = WidgetKey.unload_actionsbook()
        self.assertEqual(a.show_minus_button, [])
        # rien, car même si w1 n'est plus un
        # enfant unique, il appartient à
        # une branche masquée
        w2.kill()
        self.assertFalse(b.is_hidden_b)
        a = WidgetKey.unload_actionsbook()
        self.assertEqual(a.show, [])
        # rien, car même si une langue est de
        # nouveau disponible, le bouton appartient
        # à une branche masquée
        m.is_hidden_m = True
        a = WidgetKey.unload_actionsbook()
        self.assertEqual(a.show, [g, t, w1, b])
        w2 = ValueKey(parent=t)
        self.assertFalse(w1.is_single_child)
        a = WidgetKey.unload_actionsbook()
        self.assertEqual(a.show_minus_button, [w1])
        m.is_hidden_m = False
        WidgetKey.clear_actionsbook()
        m.is_hidden_m = True
        a = WidgetKey.unload_actionsbook()
        self.assertEqual(a.show, [g, t, w1, w2])
        
        
    
unittest.main()
