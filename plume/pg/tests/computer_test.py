
import unittest
import psycopg2

from plume.pg.computer import (
    datetime_parser, has_computation_method, ecospheres_themes_parser
)
from plume.rdf.properties import PlumeProperty
from plume.rdf.widgetsdict import WidgetsDict
from plume.rdf.namespaces import DCAT, DCT, PlumeNamespaceManager
from plume.rdf.rdflib import URIRef
from plume.pg.tests.connection import ConnectionString

class ComputerTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Création de la connexion PG.
        
        """
        cls.connection_string = ConnectionString()
    
    def test_datetime_parser(self):
        """Sérialisation textuelle des dates-heures renvoyées par PostgreSQL.
        
        """
        conn = psycopg2.connect(ComputerTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT '2022-04-20 16:46:35.487888+02'::timestamp with time zone")
                result = cur.fetchall()
        conn.close()
        cr = datetime_parser(*result[0])
        self.assertEqual(cr.str_value, '20/04/2022 16:46:35')

    def test_has_computing_method(self):
        """Détermine si une catégorie, clé ou propriété a une méthode de calcul associée.

        """
        # --- simple chemin ---
        self.assertTrue(has_computation_method(DCT.title))
        self.assertFalse(has_computation_method(DCAT.landingPage))

        # --- propriété ---
        prop = PlumeProperty(origin='unknown', nsm=PlumeNamespaceManager(),
            predicate=DCT.modified)
        self.assertTrue(has_computation_method(prop))
        prop = PlumeProperty(origin='unknown', nsm=PlumeNamespaceManager(),
            predicate=DCT.issued)
        self.assertFalse(has_computation_method(prop))

        # --- clé de dictionnaire de widgets ---
        widgetsdict = WidgetsDict()
        widgetkey = widgetsdict.root.search_from_path(DCT.conformsTo)
        self.assertTrue(has_computation_method(widgetkey))
        widgetkey = widgetsdict.root.search_from_path(DCAT.keyword)
        self.assertFalse(has_computation_method(widgetkey))

    def test_ecospheres_themes_parser(self):
        """Test de l'association des thèmes écosphères à un schéma."""
        self.assertEqual(
            sorted([r.value for r in ecospheres_themes_parser('c_tr_infra_ferroviaire', level_one=True, level_two=True)], key=lambda x: str(x)),
            [
                URIRef('http://registre.data.developpement-durable.gouv.fr/ecospheres/themes-ecospheres/infrastructure-ferree'),
                URIRef('http://registre.data.developpement-durable.gouv.fr/ecospheres/themes-ecospheres/infrastructures-de-transport')
            ]
        )
        self.assertEqual(
            sorted([r.value for r in ecospheres_themes_parser('c_tr_infra_ferroviaire')], key=lambda x: str(x)),
            [
                URIRef('http://registre.data.developpement-durable.gouv.fr/ecospheres/themes-ecospheres/infrastructure-ferree'),
                URIRef('http://registre.data.developpement-durable.gouv.fr/ecospheres/themes-ecospheres/infrastructures-de-transport')
            ]
        )
        self.assertEqual(
            [r.value for r in ecospheres_themes_parser('c_tr_infra_ferroviaire', level_one=False, level_two=True)],
            [
                URIRef('http://registre.data.developpement-durable.gouv.fr/ecospheres/themes-ecospheres/infrastructure-ferree')
            ]
        )
        self.assertEqual(
            [r.value for r in ecospheres_themes_parser('c_tr_infra_ferroviaire', level_one=True, level_two=False)],
            [
                URIRef('http://registre.data.developpement-durable.gouv.fr/ecospheres/themes-ecospheres/infrastructures-de-transport')
            ]
        )
        self.assertEqual(
            [r.source for r in ecospheres_themes_parser('c_tr_infra_ferroviaire', level_one=True, level_two=False)],
            [URIRef('http://registre.data.developpement-durable.gouv.fr/ecospheres/themes-ecospheres')]
        )
        self.assertEqual(
            [r.value for r in ecospheres_themes_parser('c_tr_infra_ferroviaire', level_one=False, level_two=False)],
            []
        )


if __name__ == '__main__':
    unittest.main()

