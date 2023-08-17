"""Recette du module transliterations.

"""

import unittest
from plume.rdf.transliterations import (
    transliterate, transliteration,
    translit_owl_version_info, TRANSLITERATIONS
)
from plume.rdf.namespaces import DCT, XSD, RDF, DCAT
from plume.rdf.rdflib import Literal, Graph, isomorphic
from plume.rdf.metagraph import clean_metagraph, Metagraph
from plume.rdf.utils import DatasetId
from plume.pg.description import PgDescription

class TransliterationsTestCase(unittest.TestCase):

    def test_register_transliteration(self):
        """Déclaration et exécution de translitérations."""

        @transliteration
        def new_translit_1(metagraph):
            if not metagraph.datasetid:
                metagraph.add((DatasetId(), RDF.type, DCAT.Dataset))
            metagraph.add(
                (
                    metagraph.datasetid,
                    DCT.created,
                    Literal('1789-08-26', datatype=XSD.date)
                )
            )
        
        @transliteration
        def new_translit_2(metagraph):
            if not metagraph.datasetid:
                metagraph.add((DatasetId(), RDF.type, DCAT.Dataset))
            metagraph.add(
                (
                    metagraph.datasetid,
                    DCT.modified,
                    Literal('1948-12-10', datatype=XSD.date)
                )
            )
        
        # avec transliterate
        metagraph = Metagraph()
        datasetid = metagraph.datasetid
        transliterate(metagraph)
        self.assertTrue(
            (datasetid, DCT.created, Literal('1789-08-26', datatype=XSD.date))
            in metagraph
        )
        self.assertTrue(
            (datasetid, DCT.modified, Literal('1948-12-10', datatype=XSD.date))
            in metagraph
        )

        # avec PgDescription
        metagraph = PgDescription().metagraph
        datasetid = metagraph.datasetid
        self.assertTrue(
            (datasetid, DCT.created, Literal('1789-08-26', datatype=XSD.date))
            in metagraph
        )
        self.assertTrue(
            (datasetid, DCT.modified, Literal('1948-12-10', datatype=XSD.date))
            in metagraph
        )

        # avec clean_metagraph (graphe vierge)
        metagraph = clean_metagraph(Graph())
        datasetid = metagraph.datasetid
        self.assertTrue(
            (datasetid, DCT.created, Literal('1789-08-26', datatype=XSD.date))
            in metagraph
        )
        self.assertTrue(
            (datasetid, DCT.modified, Literal('1948-12-10', datatype=XSD.date))
            in metagraph
        )

        # avec clean_metagraph (graphe non vierge)
        graph = Graph()
        datasetid = DatasetId()
        graph.add((datasetid, RDF.type, DCAT.Dataset))
        graph.add((datasetid, DCT.title, Literal('Mon jeu de données', lang='fr')))
        metagraph = clean_metagraph(graph)
        datasetid = metagraph.datasetid
        self.assertTrue(
            (datasetid, DCT.created, Literal('1789-08-26', datatype=XSD.date))
            in metagraph
        )
        self.assertTrue(
            (datasetid, DCT.modified, Literal('1948-12-10', datatype=XSD.date))
            in metagraph
        )

        # nettayage
        TRANSLITERATIONS.remove(new_translit_1)
        TRANSLITERATIONS.remove(new_translit_2)
        del new_translit_1
        del new_translit_2
        metagraph = clean_metagraph(Graph())
        datasetid = metagraph.datasetid
        self.assertEqual(len(metagraph), 1)
        self.assertTrue(
            (datasetid, RDF.type, DCAT.Dataset)
            in metagraph
        )

    def test_translit_owl_version_info(self):
        """Test de la translitération de la propriété représentant la version."""
        raw_description = """
            <METADATA>
                [
                    {
                        "@id": "urn:uuid:479fd670-32c5-4ade-a26d-0268b0ce5046",
                        "@type": [
                            "http://www.w3.org/ns/dcat#Dataset"
                        ],
                        "http://www.w3.org/2002/07/owl#versionInfo": [
                            {
                                "@value": "v1"
                            }
                        ],
                        "http://purl.org/dc/terms/description": [
                            {
                                "@language": "fr",
                                "@value": "Délimitation simplifiée des départements de France métropolitaine."
                            }
                        ],
                        "http://purl.org/dc/terms/conformsTo": [
                            {
                                "@id": "_:n5918a06081624472990e92f29db84bf2b1"
                            }
                        ]
                    },
                    {
                        "@id": "_:n5918a06081624472990e92f29db84bf2b1",
                        "@type": [
                            "http://purl.org/dc/terms/Standard"
                        ],
                        "http://www.w3.org/2002/07/owl#versionInfo": [
                            {
                                "@value": "v2"
                            }
                        ]
                    }
                ]
            </METADATA>
            """
        metagraph = PgDescription(raw=raw_description).metagraph
        translit_owl_version_info(metagraph)
        metadata = """
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix owl: <http://www.w3.org/2002/07/owl#> .
            @prefix uuid: <urn:uuid:> .

            uuid:479fd670-32c5-4ade-a26d-0268b0ce5046 a dcat:Dataset ;
                dcat:version "v1" ;
                dct:conformsTo [
                    a dct:Standard ;
                    owl:versionInfo "v2"
                ] ;
                dct:description "Délimitation simplifiée des départements de France métropolitaine."@fr .
            """
        metagraph_ref = Metagraph().parse(data=metadata)
        self.assertTrue(isomorphic(metagraph, metagraph_ref))

if __name__ == '__main__':
    unittest.main()
