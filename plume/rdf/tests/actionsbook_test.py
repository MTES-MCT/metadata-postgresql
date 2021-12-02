
import unittest

from rdflib import URIRef, DC, RDFS

from plume.rdf.actionsbook import ActionsBook
from plume.rdf.widgetkey import RootKey, ObjectKey, GroupOfPropertiesKey, \
     TranslationGroupKey, ValueKey, WidgetKey

class ActionsBookTestCase(unittest.TestCase):

    def test_no_ghost(self):
        """Non enregistrement des clés fantômes dans les carnets d'action.

        """
        r = RootKey()
        g = ObjectKey(parent=r, is_ghost=True, predicate=DC.title)
        w = ObjectKey(parent=r, predicate=DC.description)
        a = r.unload_actionsbook()
        self.assertEqual(a.create, [r, w])

    def test_visible(self):
        """Pas de clés masquées dans les listes de clés à afficher.
        
        """
        r = RootKey()
        WidgetKey.langlist = ['fr']
        WidgetKey.main_language = 'fr'
        g = GroupOfPropertiesKey(parent=r,
            rdftype=URIRef('http://purl.org/dc/terms/RightsStatement'),
            predicate=URIRef('http://purl.org/dc/terms/accessRights'))
        m = ValueKey(parent=r, m_twin=g)
        t = TranslationGroupKey(parent=g, predicate=RDFS.label)
        w = ValueKey(parent=t)
        WidgetKey.clear_actionsbook()
        w.kill()
        a = r.unload_actionsbook()
        self.assertEqual(a.show, [])
        m.hidden_m = True
        a = r.unload_actionsbook()
        self.assertEqual(a.show, [w])
        
    
unittest.main()
