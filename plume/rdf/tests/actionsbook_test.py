
import unittest

from plume.rdf.rdflib import URIRef
from plume.rdf.namespaces import DCT, RDFS, DCAT
from plume.rdf.widgetkey import (
    RootKey, GroupOfPropertiesKey, TranslationGroupKey, ValueKey,
    WidgetKey, TranslationButtonKey
)

class ActionsBookTestCase(unittest.TestCase):

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

    def test_basic_operations(self):
        """Quelques opérations classiques.
        
        """
        r = RootKey()
        t = TranslationGroupKey(parent=r, predicate=RDFS.label)
        b = TranslationButtonKey(parent=t)
        w1 = ValueKey(parent=t, value_language='en')
        m = ValueKey(parent=r, predicate=DCAT.theme,
            sources=[URIRef('http://publications.europa.eu/resource/authority/data-theme'),
                URIRef('https://inspire.ec.europa.eu/theme')])
        a = WidgetKey.unload_actionsbook()
        self.assertEqual(a.create, [r, t, b, w1, m])
        a = w1.change_language('fr')
        self.assertEqual(a.languages, [w1])
        a = m.change_source(URIRef('https://inspire.ec.europa.eu/theme'))
        self.assertEqual(a.sources, [m])
        self.assertEqual(a.thesaurus, [m])
        a = b.add()
        self.assertEqual(a.show_minus_button, [w1])
        self.assertEqual(a.hide, [b])
        self.assertEqual(a.languages, [w1])
        w2 = a.create[0]
        a = w1.drop()
        self.assertEqual(a.show, [b])
        self.assertEqual(a.drop, [w1])
        self.assertEqual(a.languages, [w2])
        self.assertEqual(a.hide_minus_button, [w2])

    def test_no_ghost(self):
        """Non enregistrement des clés fantômes dans les carnets d'action.

        """
        r = RootKey()
        g = ValueKey(parent=r, is_ghost=True, predicate=DCT.title)
        w = ValueKey(parent=r, predicate=DCT.description)
        a = WidgetKey.unload_actionsbook()
        self.assertEqual(a.create, [r, w])

    def test_no_unborn(self):
        """Pas de clés non créées dans les listes autres que create.

        """
        r = RootKey()
        t = TranslationGroupKey(parent=r, predicate=RDFS.label)
        b = TranslationButtonKey(parent=t)
        w1 = ValueKey(parent=t, language_value='en')
        m = ValueKey(parent=r, predicate=DCAT.theme,
            sources=[URIRef('http://publications.europa.eu/resource/authority/data-theme'),
                URIRef('https://inspire.ec.europa.eu/theme')])
        a = WidgetKey.unload_actionsbook()
        for k in a.__dict__.keys():
            with self.subTest(key=k):
                if k == 'create':
                    self.assertEqual(getattr(a, k), [r, t, b, w1, m])
                else:
                    self.assertEqual(getattr(a, k), [])

    def test_visible(self):
        """Pas de clés masquées dans les listes de clés à afficher.
        
        """
        r = RootKey()
        g = GroupOfPropertiesKey(parent=r, rdfclass=DCT.RightsStatement,
            predicate=DCT.accessRights)
        m = ValueKey(parent=r, m_twin=g, is_hidden_m=False)
        t = TranslationGroupKey(parent=g, predicate=RDFS.label)
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
  
    
if __name__ == '__main__':
    unittest.main()

