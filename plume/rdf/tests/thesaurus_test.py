"""Recette du module thesaurus.

"""

import unittest

from plume.rdf.rdflib import URIRef
from plume.rdf.utils import abspath
from plume.rdf.metagraph import SHAPE
from plume.rdf.namespaces import PLUME, RDF, SKOS
from plume.rdf.thesaurus import VOCABULARIES, VocabularyGraph, Thesaurus

class VocabulariesTestCase(unittest.TestCase):

    def test_all_files_exist(self):
        """Vérifie que tous les fichiers listés par VOCABULARIES existent bel et bien."""
        for file in VOCABULARIES.values():
            filepath = abspath('rdf/data/vocabularies') / file
            self.assertTrue(filepath.exists(), f'Missing file {filepath}')
            self.assertTrue(filepath.is_file(), f"{filepath} isn't a file")
    
    def test_all_vocabularies_loadable(self):
        """Vérifie que tous les vocabulaires listés dans VOCABULARIES peuvent être chargés."""
        for iri in VOCABULARIES:
            vocabulary = VocabularyGraph[URIRef(iri)]
            self.assertTrue(len(vocabulary), f'Failed to load vocabulary <{iri}>')
    
    def test_all_shape_vocabularies_are_registered(self):
        """Vérifie que tous les vocabulaires utilisés par SHAPE sont référencés dans VOCABULARIES."""
        for s, p, o in SHAPE:
            if p == PLUME.ontology:
                self.assertTrue(
                    str(o) in VOCABULARIES,
                    f"Vocabulary <{str(o)}> isn't registered in VOCABULARIES"
                )
    
    def test_all_vocabularies_are_used(self):
        """Vérifie que tous les vocabulaires listés dans VOCABULAIRES sont utilisés dans SHAPE.
        
        Pour les exceptions légitimes, ajouter l'IRI du vocabulaire dans la liste ci-après.
        """
        exceptions = []
        for iri in VOCABULARIES:
            if iri in exceptions:
                continue
            self.assertTrue(
                (None, PLUME.ontology, URIRef(iri)) in SHAPE,
                f"Vocabulary <{iri}> isn't used"
            )

class VocabularyGraphTestCase(unittest.TestCase):

    def test_get_vocabulary(self):
        """Accès répété à un vocabulaire."""
        vocabulary_1 = VocabularyGraph[URIRef('http://purl.org/adms/licencetype/1.1')]
        self.assertTrue(len(vocabulary_1))
        self.assertTrue(isinstance(vocabulary_1, VocabularyGraph))
        self.assertTrue(
            (URIRef('http://purl.org/adms/licencetype/PublicDomain'), RDF.type, SKOS.Concept)
            in vocabulary_1
        )
        self.assertEqual(vocabulary_1.iri, URIRef('http://purl.org/adms/licencetype/1.1'))
        vocabulary_2 = VocabularyGraph[URIRef('http://purl.org/adms/licencetype/1.1')]
        self.assertTrue(vocabulary_1 is vocabulary_2)

class ThesaurusTestCase(unittest.TestCase):

    def test_get_thesaurus(self):
        """Accès répété à un thésaurus."""
        thesaurus_1 = Thesaurus[(URIRef('http://purl.org/adms/licencetype/1.1'), ('fr',))]
        self.assertEqual(thesaurus_1.label, 'Types de licence (UE)')
        self.assertEqual(thesaurus_1.iri, URIRef('http://purl.org/adms/licencetype/1.1'))
        self.assertEqual(thesaurus_1.langlist, ('fr',))
        self.assertTrue('Domaine public' in thesaurus_1.values)
        self.assertTrue(
            URIRef('http://purl.org/adms/licencetype/PublicDomain') in thesaurus_1.str_from_iri
        )
        self.assertEqual(
            thesaurus_1.str_from_iri[URIRef('http://purl.org/adms/licencetype/PublicDomain')],
            'Domaine public'
        )
        self.assertTrue(
            URIRef('http://purl.org/adms/licencetype/PublicDomain') in thesaurus_1.links_from_iri
        )
        self.assertTrue(
            'Domaine public' in thesaurus_1.iri_from_str
        )
        self.assertEqual(
            URIRef('http://purl.org/adms/licencetype/PublicDomain'),
            thesaurus_1.iri_from_str['Domaine public']
        )
        thesaurus_2 = Thesaurus[(URIRef('http://purl.org/adms/licencetype/1.1'), ('fr',))]
        self.assertTrue(thesaurus_1 is thesaurus_2)
        thesaurus_3 = Thesaurus[(URIRef('http://purl.org/adms/licencetype/1.1'), ('fr', 'en'))]
        self.assertFalse(thesaurus_1 is thesaurus_3)

    def test_all_thesaurus_in_french(self):
        """Vérifie que tous les thésaurus ont au moins une valeur lorsqu'ils sont chargés en français."""
        for iri in VOCABULARIES:
            thesaurus = Thesaurus[(URIRef(iri), ('fr',))]
            self.assertTrue(len(thesaurus.values) > 1, f'Thesaurus <{iri}> is empty')

    def test_get_values(self):
        """Récupération des valeurs d'un thésaurus."""
        values = Thesaurus.get_values(
            (
                URIRef('http://registre.data.developpement-durable.gouv.fr/plume/CrpaAuthorizedLicense'),
                ('fr', 'en')
            )
        )
        self.assertListEqual(
            values, [
                '',
                'Licence Ouverte version 2.0',
                'ODC Open Database License (ODbL) version 1.0'
            ]
        )
    
    def test_get_label(self):
        """Récupération du libellé d'un thésaurus."""
        label = Thesaurus.get_label(
            (
                URIRef('http://registre.data.developpement-durable.gouv.fr/plume/CrpaAccessLimitations'),
                ('fr', 'en')
            )
        )
        self.assertEqual(
            label,
            "Restrictions d'accès en application du Code des relations entre le public et l'administration"
        )

    def test_concept_iri(self):
        """Récupération de l'IRI correspondant à un terme de vocabulaire."""
        iri = Thesaurus.concept_iri(
            (
                URIRef('http://registre.data.developpement-durable.gouv.fr/plume/CrpaAccessLimitations'),
                ('fr', 'en')
            ),
            'Communicable au seul intéressé - atteinte à la protection de la vie privée (CRPA, L311-6 1°)'
        )
        self.assertEqual(
            iri,
            URIRef('http://registre.data.developpement-durable.gouv.fr/plume/CrpaAccessLimitations/L311-6-1-vp')
        )

    def test_concept_str(self):
        """Récupération du libellé d'un concept."""
        label = Thesaurus.concept_str(
            (
                URIRef('http://registre.data.developpement-durable.gouv.fr/plume/CrpaAccessLimitations'),
                ('fr', 'en')
            ),
            URIRef('http://registre.data.developpement-durable.gouv.fr/plume/CrpaAccessLimitations/L311-6-1-vp')
        )
        self.assertEqual(
            label,
            'Communicable au seul intéressé - atteinte à la protection de la vie privée (CRPA, L311-6 1°)'
        )
    
    def test_concept_link(self):
        """Récupération de l'URL associée à un terme de vocabulaire."""
        link = Thesaurus.concept_link(
            (
                URIRef('http://registre.data.developpement-durable.gouv.fr/plume/CrpaAccessLimitations'),
                ('fr', 'en')
            ),
            URIRef('http://registre.data.developpement-durable.gouv.fr/plume/CrpaAccessLimitations/L311-6-1-vp')
        )
        self.assertEqual(
            link,
            URIRef('https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000037269056')
        )
    
    def test_concept_source(self):
        """Récupération de l'IRI du vocabulaire auquel appartient un terme de vocabulaire."""
        scheme_iri = Thesaurus.concept_source(
            URIRef('http://registre.data.developpement-durable.gouv.fr/plume/CrpaAccessLimitations/L311-6-1-vp'),
            [
                URIRef('http://purl.org/adms/licencetype/1.1'),
                URIRef('http://registre.data.developpement-durable.gouv.fr/plume/CrpaAccessLimitations'),
                'pas un IRI'
            ]
        )
        self.assertEqual(
            scheme_iri,
            URIRef('http://registre.data.developpement-durable.gouv.fr/plume/CrpaAccessLimitations')
        )

if __name__ == '__main__':
    unittest.main()
