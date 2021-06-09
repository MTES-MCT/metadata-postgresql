"""
Exemples d'utilisation des fonctions du module rdf_utils.
"""

from rdflib import Graph, Namespace, Literal, BNode, URIRef
from rdflib.serializer import Serializer
from locale import strxfrm, setlocale, LC_COLLATE
import re, uuid

import rdf_utils


        
# en préalable, import du schéma SHACL qui décrit les métadonnées communes
with open('shape.ttl', encoding='UTF-8') as src:
    shape = Graph().parse(data=src.read(), format='turtle')
    
# et import de l'ensemble des vocabulaires contrôlés, stockés à ce stade
# dans un fichier ontologies.ttl
with open('ontologies.ttl', encoding='UTF-8') as src:
    vocabulary = Graph().parse(data=src.read(), format='turtle')

# génération du dictionnaire qui servirait à l'élaboration d'un
# formulaire vierge complet, comprenant toutes les catégories de métadonnées
# (sans template et avec un graphe de métadonnées vide)
#form =  rdf_utils.buildDict(Graph(), shape, vocabulary)
form =  rdf_utils.buildDict(Graph(), shape, vocabulary, translation=True)
#form =  rdf_utils.buildDict(Graph(), shape, vocabulary, translation=True, langList = ['fr'])
#form =  rdf_utils.buildDict(Graph(), shape, vocabulary, mode='read')

# visualisation du résultat détaillé :
for k, v in form.items():
        
    print("{} : ".format(k))
        
    for k1, v1 in v.items():
        if v1:
            print("    {} : {}".format(k1, v1))

    print("")

# visualisation de l'arborescence :
c = -1
for k, v in form.items():

    m = c
    c = str(k).count('(') - 1
    l = len(v['label']) if v['label'] else 0

    if v['object'] in ('edit', 'plus button'):

        if m > c:    
            print( '| ' * ( m - 1 ) + '|____'
                   + '_' * ( 62 - m * 4 )
                   + '_|' + ' |' * ( m - 1) )
        
        if m != c:
            print( '| ' * c
                   + ' ' * ( 65 - c * 4 )
                   +  ' |' * c )

    if 'group' in v['object']:

        if m > c:
            print( '| ' * ( m - 1 ) + '|____'
                   + '_' * ( 62 - m * 4 )
                   + '_|' + ' |' * ( m - 1 ) )

        if not v['object'] == 'property group':
            print( '| ' * c
                   + ' ' * ( 65 - c * 4 )
                   +  ' |' * c )

        print( '| ' * c + ' ___'
               + ( v['label'] or '' )
               + '_' * ( 60 - l - c * 4 )
               + ' ' +  ' |' * c )

    if 'edit' == v['object']:
        print( '| ' * c + ' ' + (
               ( v['label'] + ' : '  + '.' * 12 )
               if v['label'] else
               ( '.' * 12 + ' ' * 3 ) )
               + ( ( '  ' + v['language value'].upper() ) if v['authorized languages'] else ' ' * 4 )
               + ( '  °°°' if v['multiple sources'] else ' ' * 5 )
               + ( '  -' if v['has minus button'] else ' ' * 3 )
               + ' ' * ( 37 - l - c * 4 )
               + ' |' * c )

    if 'plus button' == v['object']:
        print( '| ' * c + ' ' * 5 + '+'
               + ' ' * ( 59 - l - c * 4 )
               + ' |' * c )

    if 'translation button' == v['object']:
        print( '| ' * c + ' ' * 5 + '+'
               + ' ' * ( 59 - l - c * 4 )
               + ' |' * c )





