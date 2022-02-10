"""Exécution de l'ensemble des modules de test de Plume.

"""

from unittest import TestLoader, TestSuite, TextTestRunner, main

from plume.pg.tests import description_test, queries_test, \
    template_test
from plume.rdf.tests import actionsbook_test, metagraph_test, \
    properties_test, utils_test, widgetkey_test, widgetsdict_test

if __name__ == '__main__':
    loader = TestLoader()
    suite = TestSuite()
    for m in (description_test, queries_test, template_test,
        actionsbook_test, metagraph_test, properties_test,
        utils_test, widgetkey_test, widgetsdict_test):
        tests = loader.loadTestsFromModule(m)
        suite.addTests(tests)
    runner = TextTestRunner()
    runner.run(suite)
