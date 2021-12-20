
import unittest

from rdflib.compare import isomorphic

from plume.rdf.utils import abspath
from plume.rdf.metagraph import Metagraph, metagraph_from_file, copy_metagraph, \
    get_datasetid

class MetagraphTestCase(unittest.TestCase):
    
    def test_metagraph_from_file(self):
        """Import depuis un fichier et génération d'un graphe de métadonnées propre.
        
        """
        m = metagraph_from_file(abspath('rdf/tests/samples/' \
            'dcat_eurostat_bilan_nutritif_brut_terre_agricole.rdf'))
        self.assertTrue(len(m) >= 98)

    def test_copy_metagraph(self):
        """Préservation des données lors de la copie d'un graphe de métadonnées.
        
        """
        m = metagraph_from_file(abspath('rdf/tests/samples/' \
            'dcat_eurostat_bilan_nutritif_brut_terre_agricole.ttl'))
        m_copy = copy_metagraph(m)
        self.assertEqual(len(m), len(m_copy))
        self.assertNotEqual(get_datasetid(m), get_datasetid(m_copy))
        m_clone = copy_metagraph(m, m)
        self.assertTrue(isomorphic(m, m_clone))
    
    def test_available_formats(self):
        """Formats d'exports disponibles pour le graphe.
        
        """
        m = metagraph_from_file(abspath('rdf/tests/samples/' \
            'dcat_eurostat_bilan_nutritif_brut_terre_agricole.jsonld'))
        l = m.available_formats
        self.assertTrue('turtle' in l)

    def test_export(self):
        """Préservation des données lors de la sérialisation dans un fichier.
        
        """
        m = metagraph_from_file(abspath('rdf/tests/samples/' \
            'dcat_eurostat_bilan_nutritif_brut_terre_agricole.jsonld'))
        m.export(abspath('rdf/tests/export/' \
            'dcat_eurostat_bilan_nutritif_brut_terre_agricole.ttl'))
        m_reload = metagraph_from_file(abspath('rdf/tests/export/' \
            'dcat_eurostat_bilan_nutritif_brut_terre_agricole.ttl'),
            old_metagraph=m)
        self.assertTrue(isomorphic(m, m_reload))

unittest.main()
