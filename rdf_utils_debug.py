"""Utilitaires pour la recette de rdf_utils.
"""
from rdflib import Graph, Namespace, Literal, BNode, URIRef
from rdflib.compare import isomorphic

import rdf_utils


def checkUnchanged(
    graph: Graph,
    shape: Graph,
    vocabulary: Graph,
    language: str = "fr",
    *args
    ) -> bool:
    """Check if given graph is preserved through widget dictionnary serialization.
    """
    
    d = rdf_utils.buildDict(graph, shape, vocabulary, language = language, *args)
    g = rdf_utils.buildGraph(d, vocabulary, language)
    
    for n, u in shape.namespace_manager.namespaces():
        g.namespace_manager.bind(n, u, override=True, replace=True)
    
    return isomorphic(graph, g)
    
    

def checkRows(widgetsDict: dict) -> dict:
    """Check if row keys of given widget dictionnary are consistent.

    Arguments :
    - widgetsDict est un dictionnaire obtenu par exécution de la fonction buildDict.
    
    Si un problème est détecté, la fonction renvoie un dictionnaire recensant tous
    les problèmes rencontrés. La clé est un numéro d'ordre. La valeur est un tuple
    constitué de la clé de l'enregistrement concerné et d'une chaîne de caractère
    qui donne la nature du problème :
    - 'no row' (pas de ligne spécifiée pour le widget),
    - 'already affected' (un autre widget avec le même parent a déjà reçu ce
    numéro de ligne),
    - 'gap' (les numéros de ligne du groupe de se suivent pas),
    - 'misplaced M widget' (widget M dont la ligne n'est pas la même que son jumeau
    sans M),
    - 'unknown parent' (le parent n'est pas référencé dans le dictionnaire ou 
    n'a pas encore été traité),
    - 'row on hidden object' (valeur non affichée mais avec un numéro de ligne),
    - 'label row but no label' (ligne pour l'étiquette alors qu'il n'y a pas
    d'étiquette).
    
    >>> rdf_utils_debug.checkRows(d)
    """   
    idx = {}
    issues = {}
    n = 0
    
    for k, c in widgetsDict.items():
    
        if 'group' in c['object'] and not k in idx:
            idx.update( { k : [] } )
            
        if k == (0,):
            continue
            
        if not k[1] in idx:
            issues.update( { n : (k, 'unknown parent') } )
            n += 1
            continue
            
        if c['main widget type'] is None:
            if c['row']:
                issues.update( { n : (k, 'row on hidden object') } )
            continue
                
        if c['row'] is None:
            issues.update( { n : (k, 'no row') } )
            n += 1
            continue
            
        if len(k) == 3:
            if not widgetsDict.get( (k[0], k[1]), { 'row' : None } )['row'] == c['row']:
                issues.update( { n : (k, 'misplaced M widget') } )
                n += 1
            continue
            
        if not c['label row'] is None:
        # surtout pas juste if c['label row'], car 0 ~ False
        
            if c['label'] is None:
                issues.update( { n : (k, 'label row but no label') } )
                n += 1
                
            if c['label row'] in idx[k[1]]:
                issues.update( { n : (k, 'already affected (label row)') } )
                n += 1
                
            elif ( idx[k[1]] == [] and not c['label row'] == 0 )  or (
                    not idx[k[1]] == [] and not c['label row'] == ( max(idx[k[1]]) + 1 ) ):
                issues.update( { n : (k, 'gap (label row)') } )
                n += 1
                
            idx[k[1]].append(c['label row'])
            
            
        if c['row'] in idx[k[1]]:
            issues.update( { n : (k, 'already affected') } )
            n += 1
            
        elif ( idx[k[1]] == [] and not c['row'] == 0 ) \
                or ( not idx[k[1]] == [] and not c['row'] == ( max(idx[k[1]]) + 1 ) ):
            issues.update( { n : (k, 'gap') } )
            n += 1
            
        idx[k[1]].append(c['row'])           
            
    return issues
            
        
        