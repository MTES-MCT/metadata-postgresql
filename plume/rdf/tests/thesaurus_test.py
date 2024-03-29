"""Recette du module thesaurus.

"""

import unittest

from plume.rdf.rdflib import URIRef
from plume.rdf.utils import abspath, all_words_included
from plume.rdf.metagraph import SHAPE
from plume.rdf.namespaces import PLUME, RDF, SKOS
from plume.rdf.thesaurus import (
    VOCABULARIES, VocabularyGraph, Thesaurus, source_label, source_url,
    source_examples, source_nb_values
)

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
            vocabulary = VocabularyGraph[iri]
            self.assertTrue(len(vocabulary), f'Failed to load vocabulary <{iri}>')
    
    def test_all_shape_vocabularies_are_registered(self):
        """Vérifie que tous les vocabulaires utilisés par SHAPE sont référencés dans VOCABULARIES."""
        for s, p, o in SHAPE:
            if p in (PLUME.ontology, PLUME.disabledOntology):
                self.assertTrue(
                    o in VOCABULARIES,
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
                (None, PLUME.ontology, iri) in SHAPE,
                f"Vocabulary <{iri}> isn't used"
            )
    
    def test_ecospheres_themes_schemas_pg(self):
        """Contrôle de l'association de schémas de la nomenclature thématiques aux thèmes Ecosphères."""
        themes = VocabularyGraph[URIRef('http://registre.data.developpement-durable.gouv.fr/ecospheres/themes-ecospheres')]
        pg_schemas_niv1 = []
        pg_schemas_niv2 = []
        for theme in themes.subjects(RDF.type, SKOS.Concept):
            # tous les thèmes de second niveau ont un schéma associé
            pg_schema = themes.value(theme, PLUME.pgSchema)
            self.assertIsNotNone(
                pg_schema,
                f"Le thème <{theme}> n'a pas de schéma associé"
            )
            # les schémas n'apparaissent qu'une seule fois par niveau
            if (theme, SKOS.narrower, None) in themes:
                self.assertNotIn(
                    pg_schema, pg_schemas_niv1,
                    f'Le schéma "{pg_schema}" est référencé sur plusieurs thèmes de niveau 1'
                )
                pg_schemas_niv1.append(pg_schema)
            else:
                self.assertNotIn(
                    pg_schema, pg_schemas_niv2,
                    f'Le schéma "{pg_schema}" est référencé sur plusieurs thèmes de niveau 2'
                )
                pg_schemas_niv2.append(pg_schema)
            # les schémas référencés sur des thèmes de niveau 2 le sont aussi
            # sur leur thème parent
            for parent in themes.subjects(SKOS.narrower, theme):
                self.assertTrue(
                    (parent, PLUME.pgSchema, pg_schema) in themes,
                    f'Le schéma "{pg_schema}" devrait être référencé sur le thème parent <{parent}> du thème <{theme}>'
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
        self.assertTrue(isinstance(thesaurus_1, Thesaurus))
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
            thesaurus = Thesaurus[(iri, ('fr',))]
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

        label = Thesaurus.concept_str(
            (
                URIRef('http://registre.data.developpement-durable.gouv.fr/plume/ISO3166CodesCollection'),
                ('fr',)
            ),
            URIRef('http://registre.data.developpement-durable.gouv.fr/plume/ISO3166CodesCollection/CountryCodeAlpha3')
        )
        self.assertEqual(
            label,
            'Code de pays sur trois caractères (ISO 3166-1 alpha-3)'
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

    def test_look_up_label(self):
        """Recherche approché d'un IRI par son label."""
        iri = Thesaurus.look_up_label(
            (
                PLUME.ISO3166CodesCollection,
                ('fr', 'en')
            ),
            'ISO 3166-1 alpha 3'
        )
        self.assertEqual(
            iri,
            URIRef('http://registre.data.developpement-durable.gouv.fr/plume/ISO3166CodesCollection/CountryCodeAlpha3')
        )

        iri = Thesaurus.look_up_label(
            (
                PLUME.ISO3166CodesCollection,
                ('fr', 'en')
            ),
            'ISO 3166 alpha 3',
            comparator=all_words_included
        )
        self.assertEqual(
            iri,
            URIRef('http://registre.data.developpement-durable.gouv.fr/plume/ISO3166CodesCollection/CountryCodeAlpha3')
        )

        iri = Thesaurus.look_up_label(
            (
                PLUME.ISO3166CodesCollection,
                ('fr', 'en')
            ),
            'ISO 3166 alpha 8',
            comparator=all_words_included
        )
        self.assertIsNone(iri)

    def test_source_label(self):
        """Récupération du libellé d'une source."""
        self.assertEqual(
            source_label('http://inspire.ec.europa.eu/theme', 'fr'),
            'Thème (INSPIRE)'
        )
        self.assertEqual(
            source_label('http://inspire.ec.europa.eu/theme', ('fr', 'en')),
            'Thème (INSPIRE)'
        )
        self.assertEqual(
            source_label('http://inspire.ec.europa.eu/theme', ['fr', 'en']),
            'Thème (INSPIRE)'
        )
        self.assertEqual(
            source_label(URIRef('http://inspire.ec.europa.eu/theme'), ('fr', 'en')),
            'Thème (INSPIRE)'
        )
        self.assertEqual(
            source_label('http://inspire.ec.europa.eu/theme', 'fr', linked=True),
            '<a href="http://inspire.ec.europa.eu/theme">Thème (INSPIRE)</a>'
        )
    
    def test_source_url(self):
        """Récupération de l'URL d'une source."""
        self.assertEqual(
            source_url('http://registre.data.developpement-durable.gouv.fr/plume/CrpaAuthorizedLicense'),
            'https://www.data.gouv.fr/fr/pages/legal/licences'
        )
        self.assertEqual(
            source_url(
                URIRef('http://registre.data.developpement-durable.gouv.fr/plume/CrpaAuthorizedLicense'),
                ('it', 'en', 'fr')),
            'https://www.data.gouv.fr/fr/pages/legal/licences'
        )

    def test_source_examples(self):
        """Récupération de quelques valeurs d'une source."""
        self.assertListEqual(
            source_examples(
                'http://publications.europa.eu/resource/authority/dataset-status',
                start=0,
                limit=10
            ),
            ['abandonné', 'achevé', 'en production', 'obsolète', 'retiré']
        )
        self.assertListEqual(
            source_examples(
                URIRef('http://publications.europa.eu/resource/authority/dataset-status'),
                ('fr', 'en'),
                start=0,
                limit=3
            ),
            ['abandonné', 'achevé', 'en production', '...']
        )
        self.assertListEqual(
            source_examples(
                URIRef('http://publications.europa.eu/resource/authority/dataset-status'),
                ('fr', 'en'),
                start=0,
                limit=3,
                dots=False
            ),
            ['abandonné', 'achevé', 'en production']
        )
        self.assertListEqual(
            source_examples(
                'http://publications.europa.eu/resource/authority/dataset-status',
                start=2,
                limit=10
            ),
            ['en production', 'obsolète', 'retiré']
        )

    def test_source_nb_values(self):
        """Récupération du nombre de valeurs d'une source."""
        self.assertEqual(
            source_nb_values(
                'http://publications.europa.eu/resource/authority/dataset-status',
                ['fr', 'en']
            ),
            5
        )

if __name__ == '__main__':
    unittest.main()
