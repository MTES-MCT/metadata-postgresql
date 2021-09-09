"""
Utilitaires pour la recette de rdf_utils.
"""
from rdflib import Graph, Namespace, Literal, BNode, URIRef
from rdflib.compare import isomorphic

from metadata_postgresql.bibli_rdf import rdf_utils


def search_keys(widgetsdict, path, object):
    """Look up for WidgetsDict keys matching given object and path.
    
    ARGUMENTS
    ---------
    - widgetsdict (WidgetsDict) : dictionnaire obtenu par exécution de la
    fonction build_dict.
    - path (str) : un chemin SPARQL présumé connu (sinon la fonction
    renverra à coup sûr une liste vide).
    - object (str) : le type d'objet recherché, parmi "edit" (widget de
    saisie), "group of values" (groupe de valeurs), "group of properties"
    (groupe de propriétés), "translation group" (groupe de traduction),
    "plus button" (bouton plus) et "translation button" (bouton de traduction).
    
    RESULAT
    -------
    Une liste des clés du dictionnaire de widgets pointant sur des objets
    du type demandé pour le chemin considéré.
    """
    l = []
    
    for k, v in widgetsdict.items():
        if v['path'] == path:
            if v['object'] == object:
                l.append(k)
                
    return l
    


def check_unchanged(metagraph, shape, vocabulary, language="fr", **args):
    """Check if given graph is preserved through widget dictionnary serialization.
    
    ARGUMENTS
    ---------
    - metagraph (rdflib.Graph) : graphe RDF contenant les métadonnées associées à
    un jeu de données. Elles serviront à initialiser le formulaire de saisie.
    - shape (rdflib.Graph) : schéma SHACL augmenté décrivant les catégories
    de métadonnées communes.
    - vocabulary (rdflib.Graph) : graphe réunissant le vocabulaire de toutes
    les ontologies pertinentes.
    - [optionnel] language (str) : langue principale de rédaction des métadonnées
    (paramètre utilisateur). Français ("fr") par défaut.
    - [optionnel] args (dict) peut contenir tout autre paramètre à passer à build_dict()
    sous forme clé/valeur.
    
    RESULTAT
    --------
    Un booléen :
    - True si graph est reconstruit à l'identique (graphes isomorphes au sens de la
    fonction rdflib.compare.isomorphic) après sérialisation en WidgetDict avec
    build_dict, puis désérialisation avec build_graph ;
    - False si les deux graphes ne sont pas isomorphes.
    
    EXEMPLES
    --------
    >>> rdf_utils_debug.check_unchanged(g, g_shape, g_vocabulary)
    
    Avec un paramètre supplémentaire :
    >>> rdf_utils_debug.check_unchanged(g, g_shape, g_vocabulary,
    ...     args={"template": d_template})   
    """
    
    kw = {
        "metagraph": metagraph,
        "shape": shape,
        "vocabulary": vocabulary,
        "language": language
        }
        
    for a in args:
        kw.update({ a: args[a] })
    
    d = rdf_utils.build_dict(**kw)
    g = d.build_graph(vocabulary, language)
    
    for n, u in shape.namespace_manager.namespaces():
        g.namespace_manager.bind(n, u, override=True, replace=True)
    
    return isomorphic(metagraph, g)
    
    

def check_rows(widgetsdict):
    """Check if row keys of given widget dictionnary are consistent.

    ARGUMENTS
    ---------
    - widgetsdict (WidgetsDict) : dictionnaire obtenu par exécution de la
    fonction build_dict.
    
    RESULTAT
    --------
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
    
    EXEMPLES
    --------
    >>> rdf_utils_debug.check_rows(d)
    """   
    idx = {}
    issues = {}
    n = 0
    
    for k, c in widgetsdict.items():
    
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
            if not widgetsdict.get( (k[0], k[1]), { 'row' : None } )['row'] == c['row']:
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
                
            idx[k[1]].append(c['label row'])
            
            
        if c['row'] in idx[k[1]]:
            issues.update( { n : (k, 'already affected') } )
            n += 1
            
        for x in range(c['row span'] or 1):
            idx[k[1]].append(c['row'] + x)

    for k, l in idx.items():
        l.sort()
        if not l == list(range(len(l))):
            issues.update( { n : (k, 'gap') } )
            n += 1
            
    if issues:
        return issues
   

def populate_widgets(widgetsdict):
    """Populate a WidgetsDict with false widgets.
    
    ARGUMENTS
    ---------
    - widgetsdict (WidgetsDict) : dictionnaire obtenu par exécution de la
    fonction build_dict.
    
    RESULTAT
    --------
    Pas de valeur renvoyée.
    """
    for k, v in widgetsdict.items():
    
        widgetsdict[k]['main widget'] = '< {} main widget ({}) >'.format(k, widgetsdict[k]['main widget type'])
        
        if len(k) > 1 and widgetsdict[k[1]]['object'] in ('translation group', 'group of values'):
            widgetsdict[k]['minus widget'] = '< {} minus widget (QToolButton) >'.format(k)
        
        if widgetsdict[k]['authorized languages']:
            widgetsdict[k]['language widget'] = '< {} language widget (QToolButton) >'.format(k)
            widgetsdict[k]['language menu'] = '< {} language menu (QMenu) >'.format(k)
            widgetsdict[k]['language actions'] = ['< {} language actions (QAction) >'.format(k)]
            
        if widgetsdict[k]['label'] and widgetsdict[k]['object']=='edit':
            widgetsdict[k]['label widget'] = '< {} label widget (QLabel) >'.format(k)

        if 'group' in widgetsdict[k]['object']:
            widgetsdict[k]['grid widget'] = '< {} grid widget (QGridLayout) >'.format(k)

        if widgetsdict[k]['multiple sources']:
            widgetsdict[k]['switch source widget'] = '< {} switch source widget (QToolButton) >'.format(k)
            widgetsdict[k]['switch source menu'] = '< {} switch source menu (QMenu) >'.format(k)
            widgetsdict[k]['switch source actions'] = ['< {} switch source actions (QAction) >'.format(k)]
            



