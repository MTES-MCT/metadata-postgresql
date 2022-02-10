"""Génération automatisée de pages de la documentation.

Pour mettre à jour le fichier `metadonnees_communes.md`
de la documentation, on exécutera:

    >>> shared_metadata_as_page()

Notes
-----
Ce module réutilise largement les fonctions du module
:py:mod:`admin.plume_pg` qui retranscrivent le schéma
des métadonnées communes sous forme de table.

"""
from plume.rdf.rdflib import URIRef
from plume.rdf.utils import abspath
from plume.rdf.thesaurus import Thesaurus

from admin.plume_pg import table_from_shape

def shared_metadata_as_page():
    """Met à jour le tableau des métadonnées communes de la documentation.
    
    """
    filepath = abspath('').parents[0] / 'docs/source/usage/metadonnees_communes.md'
    categories = table_from_shape(no_cast=True)
    page = '# Métadonnées communes\n\n' \
        '| Chemin | Nom | Description | Thésaurus |\n' \
        '| --- | --- | --- | --- |\n'   
    for path, origin, label, description, *other in categories:
        sources = ['[{}]({})'.format(Thesaurus.get_label(
            (URIRef(s), ('fr', 'en'))), s) for s in other[10] or []]
        if origin == 'shared':
            page += '| `{}` | {} | {} | {} |\n'.format(
                path, label, description or '',
                ', '.join(sources) if sources else '')
    page += '\n'
    with open(filepath, 'w', encoding='utf-8') as dest:
        dest.write(page)