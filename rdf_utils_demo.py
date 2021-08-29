"""
Tools for visualizing widgets dictionnaries.
"""

from rdflib import Graph, Namespace, Literal, BNode, URIRef
from rdflib.serializer import Serializer
from locale import strxfrm, setlocale, LC_COLLATE
import re, uuid
import json

import rdf_utils
import rdf_utils_debug


# schéma SHACL qui décrit les métadonnées communes
with open(r'modeles\shape.ttl', encoding='UTF-8') as src:
    g_shape = Graph().parse(data=src.read(), format='turtle')
    
# vocabulaire - ontologies utilisées par les métadonnées communes
with open(r'modeles\vocabulary.ttl', encoding='UTF-8') as src:
    g_vocabulary = Graph().parse(data=src.read(), format='turtle')
    
# exemple de modèle de formulaire
with open(r'exemples\exemple_dict_modele_local.json', encoding='UTF-8') as src:
    d_template = json.loads(src.read())

# exemple de fiche de métadonnée
with open(r'exemples\exemple_commentaire_pg.txt', encoding='UTF-8') as src:
    g = rdf_utils.metagraph_from_pg_description(src.read(), g_shape)

# constitution du dictionnaire
#d = rdf_utils.build_dict(Graph(), g_shape, g_vocabulary)
#d = rdf_utils.build_dict(g, g_shape, g_vocabulary)
#d = rdf_utils.build_dict(g, g_shape, g_vocabulary, translation=True)
d = rdf_utils.build_dict(Graph(), g_shape, g_vocabulary, translation=True)
#d = rdf_utils.build_dict(g, g_shape, g_vocabulary, translation=True, langList=['fr'])
#d = rdf_utils.build_dict(g, g_shape, g_vocabulary, mode='read')
#d = rdf_utils.build_dict(g, g_shape, g_vocabulary, template=d_template)
#d = rdf_utils.build_dict(g, g_shape, g_vocabulary, hideUnlisted=True)
#d = rdf_utils.build_dict(Graph(), g_shape, g_vocabulary, template=d_template)
#d = rdf_utils.build_dict(g, g_shape, g_vocabulary, template=d_template, hideUnlisted=True, translation=True)

rdf_utils_debug.populate_widgets(d)

g1 = d.build_graph(g_vocabulary)



def print_graph(graph):
    """Show graph with turtle serialization.
    
    ARGUMENTS
    ---------
    - graph (rdflib.Graph) : graphe RDF quelconque.
    
    EXEMPLES
    --------
    >>> print_graph(g1)
    """
    print(graph.serialize(format="turtle").decode("utf-8"))



def print_dict(widgetsDict, hideNone=True, limit=5, branch=None):
    """Show detailled contents from widgetDict.
    
    ARGUMENTS
    ---------
    - widgetsDict (WidgetsDict) : dictionnaire obtenu par exécution de la
    fonction build_dict.
    - [optionne] hideNone (bool) : True si les clés vides doivent être imprimées
    (par défaut False).
    - [optionnel] limit (int) : nombre maximal de clés à imprimer. Par défaut 5.
    - [optionnel] branch (tuple) : clé dont ne souhaite afficher qu'elle et
    ses descendants éventuels.
    
    EXEMPLES
    --------
    >>> printDict(d)
    >>> printDict(d, hideNone = False)
    >>> print_dict(d, branch=(0, (0,)))
    """
    n = limit

    print("{")

    for k, v in widgetsDict.items():

        if branch is None or k == branch or rdf_utils.is_ancestor(branch, k):
            
            print(" " * 4 + "{} : {{".format(k))
            
            l = len([ e for e, s in v.items() if s ]) if hideNone else len(v)
                
            for k1, v1 in v.items():
                if v1 is not None or not hideNone:
                    print(" " * 8 + "{!r} : {!r}{}".format(k1, v1, ',' if l > 1 else ''))
                    l -= 1           

            print(" " * 4 + "}}{}".format(',' if n > 1 else ''))

            n -= 1

            if n == 0:
                break

    print("}")


   
def pseudo_form(widgetsDict):
    """Show very basic representation of a form generated from widgetsDict.
    
    ARGUMENTS
    ---------
    - widgetsDict (WidgetsDict) : dictionnaire obtenu par exécution de la
    fonction build_dict.
    
    EXEMPLES
    --------
    >>> pseudoForm(d)
    """
    
    c = -1

    print("")
    print('  ' + str(widgetsDict[(0,)]['node']))
    
    for k, v in widgetsDict.items():

        if v['row'] is None or v['hidden']:
            continue

        m = c
        c = str(k).count('(') - 1
        l = ( len(v['label']) if v['label'] else 0 ) + ( 1 if v['read only'] else 0 )

        if v['object'] in ('edit', 'plus button'):

            if m > c:
                for i in range( m - c ):
                    print( '| ' * ( m - i - 1 ) + '|____'
                           + '_' * ( 67 - ( m - i ) * 4 )
                           + '_|' + ' |' * ( m - i - 1) )
            
            if m != c:
                print( '| ' * c
                       + ' ' * ( 70 - c * 4 )
                       +  ' |' * c )

        if 'group' in v['object']:

            if m > c:
                for i in range( m - c ):
                    print( '| ' * ( m - i - 1 ) + '|____'
                           + '_' * ( 67 - ( m - i ) * 4 )
                           + '_|' + ' |' * ( m - i - 1) )

            if not c == 0 and not v['object'] == 'property group':
                print( '| ' * c
                       + ' ' * ( 70 - c * 4 )
                       +  ' |' * c )

            print( '| ' * c + ' ___'
                   + ( v['label'] or '' )
                   + '_' * ( 55 - l - c * 4 )
                   + ( ' ••• ' if v['multiple sources'] else '_' * 5 )
                   + ( '_ - ' if v['has minus button'] else '_' * 4)
                   + '_' + ' ' +  ' |' * c )

        if 'edit' == v['object']:

            e = 0
            r = 29
            
            if v['main widget type'] == 'QCheckBox':
                o = ( '[x]' if v['value'] else '[ ]' )
                e += r - 3
            elif v['main widget type'] in ( 'QLineEdit', 'QTextEdit' ):
                o = ( v['value'].ljust(r)[:r] ) if v['value'] else '.' * r
            elif v['main widget type'] == 'QDateEdit':
                o = ( v['value'] or '0000-00-00' )
                e += r - 10
            elif v['main widget type'] == 'QDateTimeEdit':
                o = ( ( v['value'].ljust(19)[:19] ) if v['value'] else '0000-00-00T00:00:00' )
                e += r - 19
            elif v['main widget type'] == 'QComboBox':
                o = '[' + ( ( v['value'].ljust(27)[:27] ) if v['value'] else ' ' * 27 ) + ']'
            else:
                o = '???'
                e =+ r - 3

            if v['label']:
                o = v['label'] + ( '*' if v['read only'] else '' ) + ' : '  + o
            else:
                o = ( '*' if v['read only'] else '' ) + o + ' ' * 3

            

            if v['authorized languages']:
                o += '  ' + v['language value'].upper()
            else:
                e += 4

            if v['multiple sources']:
                o += '  •••'
            else:
                e += 5
                
            if v['has minus button']:
                o += '  -'
            else:
                e += 3
                
            print( '| ' * c + ' ' + o
                   + ' ' * ( 25 + e - l - c * 4 )
                   + ' |' * c )

            if v['object'] == 'QTextEdit':
                print( '| ' * c + '.' * 22
                       + ' ' * ( 48 - l - c * 4 )
                       + ' |' * c )

        if 'plus button' == v['object']:
            print( '| ' * c + ' ' * 5 + '+'
                   + ' ' * ( 64 - l - c * 4 )
                   + ' |' * c )

        if 'translation button' == v['object']:
            print( '| ' * c + ' ' * 5 + '+'
                   + ' ' * ( 64 - l - c * 4 )
                   + ' |' * c )
            

    for i in range( c ):
        print( '| ' * ( c - i - 1 ) + '|____'
               + '_' * ( 67 - ( c - i ) * 4 )
               + '_|' + ' |' * ( c - i - 1) )



