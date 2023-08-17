"""Interface minimale pour l'exécution des tests de Plume.

On pourra soit exécuter ce fichier comme un script, ce qui
lancera l'ensemble des tests, soit utiliser la fonction
:py:func:`run`.

Pour lancer tous les tests :

    >>> from admin.tests import run
    >>> run()
    ...

Pour lancer uniquement les tests de certains modules ou
packages, il faut les lister en argument. Le dernier niveau
d'arborescence suffit - ``widgetkey`` - même s'il ne serait
pas gênant de spécifier ``rdf.widgetkey`` ou ``plume.rdf.widgetkey``.

Ainsi, la commande suivante exécute les tests de tous les modules du
package :py:mod:`plume.pg`, ainsi que les tests du module
:py:mod:`plume.rdf.widgetkey` :

    >>> from admin.tests import run
    >>> run('pg', 'widgetkey')
    ...

"""

from unittest import TestLoader, TestSuite, TextTestRunner

from plume.pg.tests import (
    description_test, queries_test, template_test, computer_test
)
from plume.rdf.tests import (
    actionsbook_test, metagraph_test, properties_test, utils_test, widgetkey_test,
    widgetsdict_test, thesaurus_test, transliterations_test
)
from plume.iso.tests import map_test

TESTS = {
    queries_test: ['queries', 'pg'],
    description_test: ['description', 'pg'],
    template_test: ['template', 'pg'],
    computer_test: ['computer', 'pg'],
    actionsbook_test: ['actionsbook', 'rdf'],
    metagraph_test: ['metagraph', 'rdf'],
    properties_test: ['properties', 'rdf'],
    thesaurus_test: ['thesaurus', 'rdf'],
    utils_test: ['utils', 'rdf'],
    widgetkey_test: ['widgetkey', 'rdf'],
    widgetsdict_test: ['widgetsdict', 'rdf'],
    map_test: ['map', 'iso'],
    transliterations_test : ['transliterations', 'rdf']
    }

def run(*names):
    """Exécute les tests des modules listés en argument.
    
    Parameters
    ----------
    *names : list(str), optional
        Liste des noms des modules ou package à tester.
        En l'absence d'argument, tous les tests sont
        exécutés.
    
    """
    if not names:
        modules = list(TESTS)
    else:
        names = [n.split('.')[-1] for n in names]
        modules = [m for m, l in TESTS.items() 
            if any(k in names for k in l)]
    if not modules:
        return
    loader = TestLoader()
    suite = TestSuite()
    for m in modules:
        tests = loader.loadTestsFromModule(m)
        suite.addTests(tests)
    runner = TextTestRunner()
    runner.run(suite)

if __name__ == '__main__':
    run()
