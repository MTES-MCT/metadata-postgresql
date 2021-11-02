"""Utilitaires pour la recette de rdf_utils.
"""
from rdflib import Graph, Namespace, Literal, BNode, URIRef
from rdflib.compare import isomorphic
from random import randrange
from time import gmtime, strftime
from json import load

from plume.bibli_rdf import rdf_utils
from plume import __path__


def search_keys(widgetsdict, path, object, visibleOnly=False):
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
    - visibleOnly (bool) : si True, la fonction ne renvoie que les clés non
    masquées. False par défaut.
    
    RESULTAT
    -------
    Une liste des clés du dictionnaire de widgets pointant sur des objets
    du type demandé pour le chemin considéré.
    """
    l = []
    
    for k, v in widgetsdict.items():
        if v['path'] == path and v['object'] == object and (not visibleOnly \
            or v['main widget type'] and not v['hidden'] and not v['hidden M']):
                l.append(k)
                
    return l
    

def check_unchanged(metagraph, shape, vocabulary, **args):
    """Check if given graph is preserved through widget dictionnary serialization.
    
    ARGUMENTS
    ---------
    - metagraph (rdflib.Graph) : graphe RDF contenant les métadonnées associées à
    un jeu de données. Elles serviront à initialiser le formulaire de saisie.
    - shape (rdflib.Graph) : schéma SHACL augmenté décrivant les catégories
    de métadonnées communes.
    - vocabulary (rdflib.Graph) : graphe réunissant le vocabulaire de toutes
    les ontologies pertinentes.
    - [optionnel] **args : tout autre paramètre nommé à passer à build_dict().
    
    Attention : dans les arguments de build_dict(), mode='read' devra toujours être
    accompagné de preserve=True, sans quoi le résultat sera le plus souvent négatif,
    uniquement à cause des transformation réalisées sur les valeurs en mode lecture
    (hyperliens).
    
    RESULTAT
    --------
    Un booléen :
    - True si graph est reconstruit à l'identique (graphes isomorphes au sens de la
    fonction rdflib.compare.isomorphic) après sérialisation en WidgetDict avec
    build_dict, puis désérialisation avec build_graph ;
    - False si les deux graphes ne sont pas isomorphes.
    
    EXEMPLES
    --------
    >>> rdf_utils_debug.check_unchanged(g, shape, vocabulary)
    
    Avec un paramètre supplémentaire :
    >>> rdf_utils_debug.check_unchanged(g, shape, vocabulary,
    ...     template=template)   
    """
    
    kw = {
        "metagraph": metagraph,
        "shape": shape,
        "vocabulary": vocabulary
        }
        
    for a in args:
        kw.update({ a: args[a] })
    
    d = rdf_utils.build_dict(**kw)
    g = d.build_graph(vocabulary, bypass=True)
    # avec bypass, parce que check_unchanged peut être appliqué sur
    # des dictionnaires créés avec mode='read' et preserve=True
    
    for n, u in shape.namespace_manager.namespaces():
        g.namespace_manager.bind(n, u, override=True, replace=True)
    
    return isomorphic(metagraph, g)
    

def check_buttons(widgetsdict, populated=False):
    """Vérifie la cohérence des boutons plus, moins et de traduction du dictionnaire.
    
    ARGUMENTS
    ---------
    - widgetsdict (WidgetsDict) : dictionnaire obtenu par exécution de la
    fonction build_dict.
    - populated (bool) : True si le dictionnaire a été peuplé de pseudo-widgets
    avec la populate_widgets(). Dans ce cas, la fonction vérifie aussi que les
    clés '... widget' des boutons sont remplies quand il le faut et seulement
    dans ce cas.
    
    RESULTAT
    --------    
    Si un problème est détecté, la fonction renvoie un dictionnaire recensant tous
    les problèmes rencontrés. La clé est un numéro d'ordre. La valeur est un tuple
    constitué de la clé de l'enregistrement concerné, de la nature du bouton et
    d'une chaîne de caractère qui donne la nature du problème :
    - 'should be hidden (keys)' : le bouton devrait être marqué comme masqué ;
    - 'should not be hidden (keys)' : le bouton ne devrait pas être marqué comme masqué ;
    - 'should have been created (keys)' : le bouton aurait dû être marqué comme à créer ;
    - 'should not have been created (keys)' : le bouton n'aurait pas dû être marqué comme à créer.
    
    Dans le cas d'un dictionnaire rempli de pseudo-widgets :
    - 'should be hidden (widget)' : le pseudo-widget aurait dû être masqué ;
    - 'should not be hidden (widget)' : le pseudo-widget n'aurait pas dû être masqué ;
    - 'should have been created (widget)' : le pseudo-widget aurait dû être créé ;
    - 'should not have been created (widget)' : le pseudo-widget n'aurait pas dû être créé.
    """
    issues = {}
    n = 0
    
    # en mode lecture
    # il n'est supposé y avoir aucun bouton
    if widgetsdict.mode == 'read':
        
        for k, v in widgetsdict.items():
        
            if v['object'] in ('plus button', 'translation button'):
                issues.update({ n: (k, v[object], 'should not have been created (keys)') })
                n += 1
            
            if v['has minus button']:
                issues.update({ n: (k, 'minus button', 'should not have been created (keys)') })
                n += 1
            
            if populated and v['minus widget']:
                issues.update({ n: (k, 'minus button', 'should not have been created (widget)') })
                n += 1
                
        return issues if issues else None
    
    # en mode édition
    for k, v in widgetsdict.items():
    
        if rdf_utils.is_root(k) or v['main widget type'] is None:
            
            if v['object'] in ('plus button', 'translation button'):
                issues.update({ n: (k, v[object], 'should not have been created (keys)') })
                n += 1
            
            if v['has minus button']:
                issues.update({ n: (k, 'minus button', 'should not have been created (keys)') })
                n += 1
            
            if populated and v['minus widget']:
                issues.update({ n: (k, 'minus button', 'should not have been created (widget)') })
                n += 1
                
            continue
    
        if v['object'] in ('edit', 'group of properties') \
            and widgetsdict[k[1]]['object'] in ('group of values', 'translation group'):
            # widgets de saisie et groupe de propriétés dans des groupes valeur ou de traduction
            
            if widgetsdict.count_siblings(k, visibleOnly=True) > 1:
            # plus d'un enregistrement dans le groupe, il faut nécessairement
            # un bouton moins visible
                if not v['has minus button']:
                    issues.update({ n: (k, 'minus button', 'should have been created (keys)') })
                    n += 1
                if v['hide minus button']:
                    issues.update({ n: (k, 'minus button', 'should not be hidden (keys)') })
                    n += 1
                
                if populated and not v['minus widget']:
                    issues.update({ n: (k, 'minus button', 'should have been created (widget)') })
                    n += 1
                elif populated and not v['minus widget'][1] and not v['hidden M']:
                    issues.update({ n: (k, 'minus button', 'should not be hidden (widget)') })
                    n += 1
        
            else:
            # un seul enregistrement dans le groupe, le bouton moins devrait exister
            # mais être masqué
                if not v['has minus button']:
                    issues.update({ n: (k, 'minus button', 'should have been created (keys)') })
                    n += 1
                if not v['hide minus button']:
                    issues.update({ n: (k, 'minus button', 'should be hidden (keys)') })
                    n += 1
                if populated and not v['minus widget']:
                    issues.update({ n: (k, 'minus button', 'should have been created (widget)') })
                    n += 1
                elif populated and v['minus widget'][1]:
                    issues.update({ n: (k, 'minus button', 'should be hidden (widget)') })
                    n += 1
                    
            continue
        
        else:
        # jamais de boutons moins sur les autres types d'objets
        
            if v['has minus button']:
                issues.update({ n: (k, 'minus button', 'should not have been created (keys)') })
                n += 1
            if populated and v['minus widget']:
                issues.update({ n: (k, 'minus button', 'should not have been created (widget)') })
                n += 1

  
        if v['object'] in ('plus button', 'translation button'):
        # boutons plus et boutons de traduction
        
            if v['object'] == 'plus button' and not widgetsdict[k[1]]['object'] == 'group of values':
            # un bouton plus hors d'un groupe de valeurs n'aurait pas dû exister
            
                issues.update({ n: (k, 'plus button', 'should not have been created (keys)') })
                n += 1
                
                if populated and v['main widget']:
                    issues.update({ n: (k, 'plus button', 'should not have been created (widget)') })
                    n += 1
            
            elif v['object'] == 'translation button' and not widgetsdict[k[1]]['object'] == 'translation group':
            # un bouton de tranduction hors d'un groupe de traduction
            # n'aurait pas dû exister
            
                issues.update({ n: (k, 'translation button', 'should not have been created (keys)') })
                n += 1
                
                if populated and v['main widget']:
                    issues.update({ n: (k, 'translation button', 'should not have been created (widget)') })
                    n += 1
            
            elif widgetsdict[k[1]]['object'] == 'group of values':
            # un bouton plus dans un groupe de valeurs devrait toujours être visible (s'il
            # n'est pas dans une branche masquée)
                if v['hidden']:
                    issues.update({ n: (k, 'plus button', 'should not be hidden (keys)') })
                    n += 1
                if populated and not v['main widget'][1] and not v['hidden M']:
                    issues.update({ n: (k, 'plus button', 'should not be hidden (widget)') })
                    n += 1
            
            else:
            # dans un groupe de traduction, le bouton plus est visible dès lors que les listes
            # de langues autorisées contiennent au moins deux valeurs
                c = widgetsdict[widgetsdict.child(k[1], visibleOnly=False)]['authorized languages']
                
                if len(c) > 1:
                    if v['hidden']:
                        issues.update({ n: (k, 'translation button', 'should not be hidden (keys)') })
                        n += 1
                    if populated and not v['main widget'][1] and not v['hidden M']:
                        issues.update({ n: (k, 'translation button', 'should not be hidden (widget)') })
                        n += 1
                        
                else:
                    if not v['hidden']:
                        issues.update({ n: (k, 'translation button', 'should be hidden (keys)') })
                        n += 1
                    if populated and v['main widget'][1]:
                        issues.update({ n: (k, 'translation button', 'should be hidden (widget)') })
                        n += 1
                        
            continue
   
        if v['object'] == 'group of values':
        # dans un groupe de valeur, le bouton plus devrait toujours avoir été créé
        # ... sauf s'il contient des traductions hors mode traduction
        
            c = widgetsdict.child(k, visibleOnly=False)
            
            if widgetsdict[c]['one per language']:
            
                for e in rdf_utils.iter_children_keys(widgetsdict, k):
                    if widgetsdict[e]['object'] == 'plus button':
                        issues.update({ n: (e, 'plus button', 'should not have been created (keys)') })
                        n += 1
                
                        if populated and widgetsdict[e]['main widget']:
                            issues.update({ n: (e, 'plus button', 'should not have been created (widget)') })
                            n += 1
            
            else:
        
                if not any([widgetsdict[e]['object'] == 'plus button' 
                    for e in rdf_utils.iter_children_keys(widgetsdict, k)]):
                    issues.update({ n: (k, 'plus button', 'should have been created (keys)') })
                    n += 1
                
                if populated and not any([widgetsdict[e]['object'] == 'plus button' and widgetsdict[e]['main widget']
                    for e in rdf_utils.iter_children_keys(widgetsdict, k)]):
                    issues.update({ n: (k, 'plus button', 'should have been created (widget)') })
                    n += 1
                
        elif v['object'] == 'translation group':
        # dans un groupe de traduction, le bouton de traduction devrait toujours avoir été créé
        
            if not any([widgetsdict[e]['object'] == 'translation button' 
                for e in rdf_utils.iter_children_keys(widgetsdict, k)]):
                issues.update({ n: (k, 'translation button', 'should have been created (keys)') })
                n += 1
            
            if populated and not any([widgetsdict[e]['object'] == 'translation button' and widgetsdict[e]['main widget']
                for e in rdf_utils.iter_children_keys(widgetsdict, k)]):
                issues.update({ n: (k, 'translation button', 'should have been created (widget)') })
                n += 1
                
    if issues:
        return issues
    

def check_hidden_branches(widgetsdict, populated=False):
    """Vérifie que les branches à masquer sont correctement masquées.
    
    ARGUMENTS
    ---------
    - widgetsdict (WidgetsDict) : dictionnaire obtenu par exécution de la
    fonction build_dict.
    - populated (bool) : True si le dictionnaire a été peuplé de pseudo-widgets
    avec la populate_widgets(). Dans ce cas, la fonction vérifie aussi que les
    clés '... widget' sont remplies comme il le faut.
    
    RESULTAT
    --------
    Si un problème est détecté, la fonction renvoie un dictionnaire recensant tous
    les problèmes rencontrés. La clé est un numéro d'ordre. La valeur est un tuple
    constitué de [0] la clé de l'enregistrement concerné, [1] la nature de
    l'objet concerné, [2] une chaîne de caractère qui donne la nature du problème :
    - "members of hidden branches should be hidden M" : l'enregistrement devrait
    être marqué comme masqué (cas du descendant d'une branche masquée) ;
    - "can't hide M this type of object outside of an hidden branch" : les groupes
    de valeurs, groupes de traduction et boutons ne sont pas supposés être masqués
    s'ils ne sont pas dans une branche masquée ;
    - "roots can't be hidden M" : les enregistrements racines (onglets) ne peuvent
    pas être masqués ;
    - "hidden M but no M twin" : l'enregistrement ne devrait pas
    être marqué comme masqué (cas d'un enregistrement masqué de bon type, mais
    qui n'a pas de double M) ;
    - "both M twins are hidden M" : l'enregistrement et son double M sont tous
    deux masqués (et n'appartiennent pas à une branche masquée) ;
    - "none of the M twins is hidden M" : l'enregistrement et son double M sont
    deux visibles ;
    - "widget to create in a ghost group of properties" : widget marqué comme à créer
    ('main widget type' non nul) descendant d'un group de propriétés avec un 'main
    widget type' nul ;
    - 'should have been a ghost' : groupe de propriétés avec un 'main widget type' non nul,
    mais aucun descendant avec un 'main widget type' non nul.
    
    Dans le cas d'un dictionnaire rempli de pseudo-widgets :
    - 'should be hidden (widget)' : le pseudo-widget aurait dû être masqué ;
    - 'should not be hidden (widget)' : le pseudo-widget n'aurait pas dû être masqué ;
    - "value should have been cleaned (widget)" : les valeurs renseignés dans les
    widgets de saisie des racines de branches masquées sont supposées être effacées ;
    - "should not have been created (widget)" : pseudo-widget dans une branche
    fantôme ('main widget type' nuls).
    """
    issues = {}
    n = 0
    hidden = []
    notcreated = []
    visible = []
    ghosts = []
    
    for k, v in widgetsdict.items():
        
        if v['object'] == 'group of properties' and v['main widget type'] is None:
        # groupes propriétés présumés vides, qui ne seront donc pas créés
            notcreated.append(k)
            
        if v['main widget type'] is None:
            continue
        
        if v['object'] == 'group of properties':
            ghosts.append(k)
            
        if not rdf_utils.is_root(k) and k[1] in ghosts:
            ghosts.remove(k[1])
        
        if any([rdf_utils.is_ancestor(a, k) for a in notcreated]):
        # cas du descendant d'un groupe de propriétés non créé
            if v['main widget type']:
                issues.update({ n: (k, v['object'], "widget to create in a ghost group of properties") })
                n += 1
                
            if populated:
                for e in ('main widget', 'minus widget', 'language widget',
                    'label widget', 'grid widget', 'switch source widget'):
                    if v[e]:
                        issues.update({ n: (k, e, 'should not have been created (widget)') })
                        n += 1

            continue
        
        if any([rdf_utils.is_ancestor(a, k) for a in hidden]):
        # cas du descendant d'une branche déjà identifiée
        # comme masquée
            if not v['hidden M']:
                issues.update({ n: (k, v['object'], "members of hidden branches should be hidden M") })
                n += 1
                
            if populated:
                for e in ('main widget', 'minus widget', 'language widget',
                    'label widget', 'grid widget', 'switch source widget'):
                    if v[e] and v[e][1]:
                        issues.update({ n: (k, e, 'should be hidden (widget)') })
                        n += 1

            continue

        if not v['object'] in ('group of properties', 'edit'):
        # cas d'un enregistrement qui ne peut pas être la racine d'une
        # branche masquée
            if v['hidden M']:
                issues.update({ n: (k, v['object'], "can't hide M this type of object outside of an hidden branch") })
                n += 1
            
            if populated:
                for e in ('main widget', 'minus widget', 'language widget',
                    'label widget', 'grid widget', 'switch source widget'):
                    if v[e] and not v['hidden'] \
                        and not (e == 'minus widget' and v['hide minus button']) \
                        and not v[e][1]:
                        issues.update({ n: (k, e, 'should not be hidden (widget)') })
                        n += 1
  
            continue
        
        if rdf_utils.is_root(k):
        # cas d'un enregistrement racine (onglet)
            if v['hidden M']:
                issues.update({ n: (k, v['object'], "roots can't be hidden M") })
                n += 1
                
            if populated:
                for e in ('main widget', 'minus widget', 'language widget',
                    'label widget', 'grid widget', 'switch source widget'):
                    if v[e] and not v['hidden'] \
                        and not (e == 'minus widget' and v['hide minus button']) \
                        and not v[e][1]:
                        issues.update({ n: (k, e, 'should not be hidden (widget)') })
                        n += 1
                        
            continue
            
        km = (k[0], k[1], 'M') if len(k) == 2 else (k[0], k[1])
        
        if not km in widgetsdict:
        # enregistrement sans double M
            if v['hidden M']:
                issues.update({ n: (k, v['object'], "hidden M but no M twin") })
                n += 1
                
            if populated:
                for e in ('main widget', 'minus widget', 'language widget',
                    'label widget', 'grid widget', 'switch source widget'):
                    if v[e] and not v['hidden'] \
                        and not (e == 'minus widget' and v['hide minus button']) \
                        and not v[e][1]:
                        issues.update({ n: (k, e, 'should not be hidden (widget)') })
                        n += 1
                        
            continue
            
        if km in hidden:
        # le double M est déjà identifié comme masqué
            if v['hidden M']:
                issues.update({ n: (k, v['object'], "both M twins are hidden M") })
                n += 1
                
            if populated:
                for e in ('main widget', 'minus widget', 'language widget',
                    'label widget', 'grid widget', 'switch source widget'):
                    if v[e] and not v['hidden'] \
                        and not (e == 'minus widget' and v['hide minus button']) \
                        and not v[e][1]:
                        issues.update({ n: (k, e, 'should not be hidden (widget)') })
                        n += 1
                        
            continue
            
        if km in visible:
        # le double M est déjà identifié comme non masqué
        
            if not v['hidden M']:
                issues.update({ n: (k, v['object'], "none of the M twins is hidden M") })
                n += 1
            else:
                hidden.append(k)
                
            if populated:
                for e in ('main widget', 'minus widget', 'language widget',
                    'label widget', 'grid widget', 'switch source widget'):
                    if v[e] and v[e][1]:
                        issues.update({ n: (k, e, 'should be hidden (widget)') })
                        n += 1
                
                if v[e] and v['main widget'][3] is not None:
                # NB : on pourrait restreindre le test aux widgets de saisie
                # mais les autres ne sont pas supposés contenir de valeur
                # non plus, donc autant en profiter pour tester
                    issues.update({ n: (k, v['object'], "value should have been cleaned (widget)") })
                    n += 1
                
            continue
            
        if v['hidden M']:
            hidden.append(k)

            if populated:
                for e in ('main widget', 'minus widget', 'language widget',
                    'label widget', 'grid widget', 'switch source widget'):
                    if v[e] and v[e][1]:
                        issues.update({ n: (k, e, 'should be hidden (widget)') })
                        n += 1
                
                if v[e] and v['main widget'][3] is not None:
                    issues.update({ n: (k, v['object'], "value should have been cleaned (widget)") })
                    n += 1
                    
        else:
            visible.append(k)
            if populated:
                for e in ('main widget', 'minus widget', 'language widget',
                    'label widget', 'grid widget', 'switch source widget'):
                    if v[e] and not v['hidden'] \
                        and not (e == 'minus widget' and v['hide minus button']) \
                        and not v[e][1]:
                        issues.update({ n: (k, e, 'should not be hidden (widget)') })
                        n += 1

    for g in ghosts:
        issues.update({ n: (g, 'group of properties', 'should have been a ghost') })
        n += 1

    if issues:
        return issues


def check_rows(widgetsdict, populated=False):
    """Check if row keys of given widget dictionnary are consistent.

    ARGUMENTS
    ---------
    - widgetsdict (WidgetsDict) : dictionnaire obtenu par exécution de la
    fonction build_dict.
    - populated (bool) : True si le dictionnaire a été peuplé de pseudo-widgets
    avec la populate_widgets(). Dans ce cas, la fonction vérifie aussi que les
    clés '... widget' sont remplies comme il le faut.
    
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
    - 'row on phantom object' (enregistrement sans widget, mais avec un numéro
    de ligne),
    - 'label row but no label' (ligne pour l'étiquette alors qu'il n'y a pas
    d'étiquette).
    
    Dans le cas d'un dictionnaire rempli de pseudo-widgets :
    - "x widget row doesn't match with key 'row'" : la ligne du pseudo-widget
    est différente de celle du dictionnaire (x est remplacé par le type du
    widget considéré).
    - "label widget row doesn't match with keys 'label row' or 'row'" : la
    ligne du pseudo-widget d'étiquette est différente de celle du dictionnaire.
    
    EXEMPLES
    --------
    >>> rdf_utils_debug.check_rows(d)
    """ 
    mode = widgetsdict.mode
    idx = {}
    issues = {}
    n = 0
    
    for k, c in widgetsdict.items():
    
        if 'group' in c['object'] and not k in idx:
            idx.update( { k : [] } )
            
        if rdf_utils.is_root(k):
            continue
            
        if not k[1] in idx:
            issues.update( { n : (k, 'unknown parent') } )
            n += 1
            continue
            
        if c['main widget type'] is None:
            if c['row']:
                issues.update( { n : (k, 'row on phantom object') } )
            continue
                
        if c['row'] is None:
            issues.update( { n : (k, 'no row') } )
            n += 1
            continue
            
        if len(k) == 3 and mode == 'edit':
            if not widgetsdict.get( (k[0], k[1]), {'row' : None} )['row'] == c['row']:
                issues.update( { n : (k, 'misplaced M widget') } )
                n += 1 
        else:
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
            
        if populated and c['label widget'] \
            and not c['label widget'][2] == ( c['label row'] \
                if c['label row'] is not None else c['row'] ):
            issues.update( { n : (k, "label widget row doesn't match with keys 'label row' or 'row'") } )
            n += 1
        
        for e in ('main widget', 'minus widget', 'language widget', 'switch source widget'):
            if populated and c[e] and not c[e][2] == c['row']:
                issues.update( { n : (k, "{} row doesn't match with key 'row'".format(e)) } )
                n += 1

    for k, l in idx.items():
        l.sort()
        if not l == list(range(len(l))):
            issues.update( { n : (k, 'gap') } )
            n += 1
            
    if issues:
        return issues
   

def check_languages(widgetsdict, populated=False):
    """Contrôle les widgets de gestion de la langue et clés afférentes du dictionnaire.
    
    ARGUMENTS
    ---------
    - widgetsdict (WidgetsDict) : dictionnaire obtenu par exécution de la
    fonction build_dict.
    - populated (bool) : True si le dictionnaire a été peuplé de pseudo-widgets
    avec la populate_widgets(). Dans ce cas, la fonction vérifie aussi que les
    clés '... widget' sont remplies comme il le faut.
    
    RESULTAT
    --------
    Si un problème est détecté, la fonction renvoie un dictionnaire recensant tous
    les problèmes rencontrés. La clé est un numéro d'ordre. La valeur est un tuple
    constitué de la clé de l'enregistrement concerné et d'une chaîne de caractère
    qui donne la nature du problème.
    
    Quand le mode traduction n'est pas actif :
    - "'authorized languages' should be None when translation is False".
    - "None langString value whose 'language value' isn't 'language'".
    - "langString without 'language value'" : la clé 'datatype' montre que la
    valeur est de type rdf:langString, mais 'language value' est vide.
    - "not a langString but 'language value' isn't None".
    - "there should be no translation group when translation is False".
    - "there should be no translation button when translation is False".
    
    et si le dictionnaire est peuplé de pseudo-widgets :
    - "no language widget should be created when translation is False (widget)".
    - "no language menu should be created when translation is False (widget)".
    - "no language action should be created when translation is False (widget)".
    
    Quand le mode traduction est actif :
    - "missing value for 'authorized languages'" : la clé 'datatype' montre que la
    valeur est de type rdf:langString, mais 'authorized languages' est vide.
    - "langString without 'language value'" : la clé 'datatype' montre que la
    valeur est de type rdf:langString, mais 'language value' est vide.
    - "not a langString but 'language value' isn't None".
    - "not a langString but 'authorized languages' isn't None".
    - "'language' is not in 'authorized language'".
    - "value from 'authorized language' missing from langList" (hors cas où
    la valeur excédentaire est 'language value').
    - "no translation button in translation group".
    - "not a langString in translation group".
    - "repeated language in translation group" : deux clés avec le même
    'language value' dans un groupe de traduction.
    - "authorized language that's already used".
    - "unused language from langList missing from 'authorized language'" : cas
    d'une langue de langList qui n'est utilisée par aucune valeur du groupe
    et n'apparait pourtant pas dans 'authorized language'.
    - "translation button should be hidden (key)" : cas où il ne reste plus qu'un
    language autorisé pour chaque valeur existante du groupe de traduction.
    - "translation button should not be hidden (key)".
    
    et dans le cas d'un dictionnaire peuplé de pseudo-widgets :
    - "missing language widget (widget)".
    - "missing language menu (widget)".
    - "missing language actions (widget)".
    - "language menu doesn't match with 'authorized language' (widget)".
    - "current language doesn't match with 'language value' (widget)".
    - "no language widget should be created for anything but a langString (widget)".
    - "no language menu should be created for anything but a langString (widget)".
    - "no language action should be created for anything but a langString (widget)".
    - "translation button should be hidden (widget)" : cas où il ne reste plus qu'un
    language autorisé pour chaque valeur existante du groupe de traduction.
    - "translation button should not be hidden (widget)".

    Cas particulier des branches fantômes :
    - "'authorized languages' should be None on ghost branches".
    - "there should be no translation group on ghost branches".
    - "there should be no translation button on ghost branches".

    et dans le cas d'un dictionnaire peuplé de pseudo-widgets :
    - "no language widget should be created on ghost branches (widget)".
    - "no language action should be created on ghost branches (widget)".
    - "no language menu should be created on ghost branches (widget)".
    """
    issues = {}
    n = 0
    langString = URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#langString')
    
    if not widgetsdict.translation:
    
        for k, v in widgetsdict.items():
        
            if v['authorized languages']:
                issues.update( { n : (k, "'authorized languages' should be None when translation is False") } )
                n += 1
            
            # Literal admettant une langue. Les informations relatives
            # à celle-ci sont supposées exister, même si elles ne sont
            # pas affichées.
            if v['node kind'] == 'sh:Literal' and v['data type'] == langString:
                if not v['language value']:
                    issues.update( { n : (k, "langString without 'language value'") } )
                    n += 1
                elif v['value'] is None and v['language value'] != widgetsdict.language:
                    issues.update( { n : (k, "None langString value whose 'language value' isn't 'language'") } )
                    n += 1
            # sinon, il n'est pas supposé y avoir d'informations sur la langue
            elif v['language value']:
                issues.update( { n : (k, "not a langString but 'language value' isn't None") } )
                n += 1
              
            if populated:
                if v['language widget']:
                    issues.update( { n : (k, "no language widget should be created " \
                        "when translation is False (widget)") } )
                    n += 1
                if v['language actions']:
                    issues.update( { n : (k, "no language action should be created " \
                        "when translation is False (widget)") } )
                    n += 1
                if v['language menu']:
                    issues.update( { n : (k, "no language menu should be created " \
                        "when translation is False (widget)") } )
                    n += 1
                    
            if v['object'] == 'translation group':
                issues.update( { n : (k, "there should be no translation group when translation is False") } )
                n += 1
            if v['object'] == 'translation button':
                issues.update( { n : (k, "there should be no translation button when translation is False") } )
                n += 1
    
        return issues if issues else None
    
    
    for k, v in widgetsdict.items():

        # branche fantôme
        if not v['main widget type']:

            if v['authorized languages']:
                issues.update( { n : (k, "'authorized languages' should be None on ghost branches") } )
                n += 1

            if populated:
                if v['language widget']:
                    issues.update( { n : (k, "no language widget should be created " \
                        "on ghost branches (widget)") } )
                    n += 1
                if v['language actions']:
                    issues.update( { n : (k, "no language action should be created " \
                        "on ghost branches (widget)") } )
                    n += 1
                if v['language menu']:
                    issues.update( { n : (k, "no language menu should be created " \
                        "on ghost branches (widget)") } )
                    n += 1

            if v['object'] == 'translation group':
                issues.update( { n : (k, "there should be no translation group on ghost branches") } )
                n += 1
            if v['object'] == 'translation button':
                issues.update( { n : (k, "there should be no translation button on ghost branches") } )
                n += 1
            
        # Literal admettant une langue
        elif v['node kind'] == 'sh:Literal' and v['data type'] == langString:
        
            if not v['authorized languages']:
                issues.update( { n : (k, "missing value for 'authorized languages'") } )
                n += 1    
            if not v['language value']:
                issues.update( { n : (k, "langString without 'language value'") } )
                n += 1
            if v['authorized languages'] and not v['language value'] in v['authorized languages']:
                issues.update( { n : (k, "'language' is not in 'authorized language'") } )
                n += 1
            if v['authorized languages'] and any([not l in widgetsdict.langList \
                and not l == v['language value'] for l in v['authorized languages']]):
                issues.update( { n : (k, "value from 'authorized language' missing from langList") } )
                n += 1
        
            if populated:
                if not v['language widget']:
                    issues.update( { n : (k, "missing language widget (widget)") } )
                    n += 1
                if not v['language actions']:
                    issues.update( { n : (k, "missing language actions (widget)") } )
                    n += 1
                if not v['language menu']:
                    issues.update( { n : (k, "missing language menu (widget)") } )
                    n += 1
                if v['language menu'][1] != v['authorized languages']:
                    issues.update( { n : (k, "language menu doesn't match with " \
                        "'authorized language' (widget)") } )
                    n += 1
                if v['language menu'][2] != v['language value']:
                    issues.update( { n : (k, "current language doesn't match" \
                        " with 'language value' (widget)") } )
                    n += 1
        
        # pas un Literal admettant une langue
        else:
            if v['language value']:
                issues.update( { n : (k, "not a langString but 'language value' isn't None") } )
                n += 1            
            if v['authorized languages']:
                issues.update( { n : (k, "not a langString but 'authorized languages' isn't None") } )
                n += 1
                
            if populated:
                if v['language widget']:
                    issues.update( { n : (k, "no language widget should be created " \
                        "for anything but a langString (widget)") } )
                    n += 1
                if v['language actions']:
                    issues.update( { n : (k, "no language action should be created " \
                        "for anything but a langString (widget)") } )
                    n += 1
                if v['language menu']:
                    issues.update( { n : (k, "no language menu should be created " \
                        "for anything but a langString (widget)") } )
                    n += 1
                    
            if v['object'] == 'translation group' and v['main widget type']:
                lu = [widgetsdict[ck]['language value'] \
                    for ck in rdf_utils.iter_children_keys(widgetsdict, k)]
                lu2 = []
                bh = False
                bk = None
                for ck in rdf_utils.iter_children_keys(widgetsdict, k):
                    cv = widgetsdict[ck]
                    
                    if cv['object'] == 'translation button' and cv['main widget type']:
                        bh = cv['hidden']
                        bk = ck
                    elif not cv['node kind'] == 'sh:Literal' \
                        or not cv['data type'] == langString:
                        issues.update( { n : (ck, "not a langString in translation group") } )
                        n += 1
                    else:
                        if cv['language value'] in lu2:
                            issues.update( { n : (ck, "repeated language in translation group") } )
                            n += 1
                        else:
                            lu2.append(cv['language value'])
                        if cv['authorized languages'] and any([l in lu and not l==cv['language value'] \
                            for l in cv['authorized languages']]):
                            issues.update( { n : (ck, "authorized language that's already used") } )
                            n += 1
                        if cv['authorized languages'] and any([not l in lu and \
                            not l in cv['authorized languages'] for l in widgetsdict.langList]):
                            issues.update( { n : (ck, "unused language from langList missing from " \
                                                  "'authorized language'") } )
                            n += 1
                
                if not bk:
                    issues.update( { n : (k, "no translation button in translation group") } )
                    n += 1
                else:
                    x = all([l in lu for l in widgetsdict.langList])
                    if x and not bh:
                        issues.update( { n : (k, "translation button should be hidden (key)") } )
                        n += 1
                    elif not x and bh:
                        issues.update( { n : (k, "translation button should not be hidden (key)") } )
                        n += 1
                    if populated:
                        if x and widgetsdict[bk]['main widget'][1]:
                            issues.update( { n : (k, "translation button should be hidden (widget)") } )
                            n += 1
                        if not x and not widgetsdict[bk]['main widget'][1] \
                            and not widgetsdict[bk]['hidden M']:
                            issues.update( { n : (k, "translation button should not be hidden (widget)") } )
                            n += 1
                
    if issues:
        return issues
    

def check_sources(widgetsdict, populated=False):
    """Contrôle les widgets de gestion de la source et clés afférentes du dictionnaire.
    
    ARGUMENTS
    ---------
    - widgetsdict (WidgetsDict) : dictionnaire obtenu par exécution de la
    fonction build_dict.
    - populated (bool) : True si le dictionnaire a été peuplé de pseudo-widgets
    avec la populate_widgets(). Dans ce cas, la fonction vérifie aussi que les
    clés '... widget' sont remplies comme il le faut.
    
    RESULTAT
    --------
    Si un problème est détecté, la fonction renvoie un dictionnaire recensant tous
    les problèmes rencontrés. La clé est un numéro d'ordre. La valeur est un tuple
    constitué de la clé de l'enregistrement concerné et d'une chaîne de caractère
    qui donne la nature du problème.
    
    - "'current source' isn't one of 'sources'".
    - "hidden M key, but 'current source' isn't None".
    - "not a M key, but 'current source' is '< manuel >'".
    - "M key, but 'current source' is not '< manuel >'" (hors cas où la clé
    est masquée).
    - "'< URI >' or a thesaurus should be provided beside '< manuel >'".
    - "missing 'value' for '< non répertorié >' source" : '< non répertorié >' ne
    devrait être utilisé que quand il y a une valeur non répertoriée...
    - "'multiple sources', yet less than two values in 'sources'".
    - "more than one value in 'sources', yet not 'multiple sources'" (en mode
    'edit' uniquement).
    - "'multiple sources' in 'read' mode".
    - "'default source' isn't one of 'sources'".
    - "some elements of 'sources' have no match in 'sources URI'" (exclut les mots
    clés < URI >, < manuel > et < non répertorié >).
    - "no keyword '< ... >' should appear in 'sources URI'" : cas où < URI >,
    < manuel > ou < non répertorié > se retrouverait dans 'sources URI'.
    - "'sources URI' keys should be strings".
    - "'sources URI' values should be strings".
    - "'current source URI' doesn't match 'current source' value in 'sources URI'".
    - "'default source URI' doesn't match 'default source' value in 'sources URI'".
    - "'default source URI' shouldn't be a keyword '< ... >'".
    
    Si le dictionnaire est peuplé de pseudo-widgets :
    - "no source widget should be created without 'sources' (widget)" : cas
    où un widget est référencé alors que la clé 'sources' est vide.
    - "no source menu should be created without 'sources' (widget)".
    - "no source action should be created without 'sources' (widget)".
    - "missing source widget (widget)" : cas où aucun widget n'est référencé alors
    que la clé 'sources' n'est pas vide.
    - "missing source menu (widget)".
    - "missing source actions (widget)".
    - "source menu items don't match with key 'sources' (widget)".
    - "source menu's current source doesn't match with key 'current source' (widget)".
    """
    pass


def check_everything(widgetsdict, populated=False):
    """Lance toutes les fonctions de contrôle de dictionnaire de widget.
    
    ARGUMENTS
    ---------
    - widgetsdict (WidgetsDict) : dictionnaire obtenu par exécution de la
    fonction build_dict.
    - populated (bool) : True si le dictionnaire a été peuplé de pseudo-widgets
    avec la populate_widgets(). Dans ce cas, les fonctions de contrôle vérifieront
    aussi que les clés '... widget' sont remplies comme il le faut.
    
    RESULTAT
    --------
    Si au moins une fonction de contrôle détecte des anomalies, un dictionnaire
    dont les clés sont les noms des fonctions de contrôle qui ont renvoyé
    un résultat et les valeurs les résultats en question.
    """
    d = {}
    
    res = check_buttons(widgetsdict, populated=populated)
    if res:
        d.update({ "check_buttons": res })
    
    res = check_rows(widgetsdict, populated=populated)
    if res:
        d.update({ "check_rows": res })
   
    res = check_hidden_branches(widgetsdict, populated=populated)
    if res:
        d.update({ "check_hidden_branches": res })
    
    res = check_languages(widgetsdict, populated=populated)
    if res:
        d.update({ "check_languages": res })
    
    res = check_sources(widgetsdict, populated=populated)
    if res:
        d.update({ "check_sources": res })
    
    if d:
        return d


def populate_widgets(widgetsdict):
    """Populate a WidgetsDict with false widgets.
    
    ARGUMENTS
    ---------
    - widgetsdict (WidgetsDict) : dictionnaire obtenu par exécution de la
    fonction build_dict.
    
    RESULTAT
    --------
    Pas de valeur renvoyée.
    
    Les widgets sont représentés par des listes :
    [0] est une chaîne de caractères identifiant le widget ;
    [1] est un booléen indiquant si le widget est visible ;
    [2] est le numéro de la ligne du widget dans la grille (None pour les
    QGridLayout) ;
    [3] est la valeur affichée dans le widget, le cas échéant.
    
    Les clés actions contiennent des listes de chaînes de caractères, qui
    ne contiennent en fait qu'un identifiant représentant toutes les
    actions.
    
    Les menus sont des listes :
    [0] est une chaîne de caractères identifiant le menu ;
    [1] est la liste des items du menu ;
    [2] est le nom de l'item actuellement sélectionné.
    """
    for k in widgetsdict.keys(): 
        populate_widgets_key(widgetsdict, k)
 

def populate_widgets_key(widgetsdict, key):
    """Populate one key of a WidgetsDict with false widgets.
    
    ARGUMENTS
    ---------
    - widgetsdict (WidgetsDict) : dictionnaire obtenu par exécution de la
    fonction build_dict.
    - key (tuple) : la clé de widgetsdict pour laquelle on veut générer
    les widgets.
    
    RESULTAT
    --------
    Pas de valeur renvoyée.
    
    Cf. populate_widgets() pour les modalités de génération des pseudo-widgets.
    """
    v = widgetsdict[key]
    
    # for e in ('main widget', 'minus widget', 'language widget', 'language menu',
        # 'language actions', 'label widget', 'grid widget', 'switch source widget',
        # 'switch source menu', 'switch source actions'):
        # if v[e] is not None:
            # raise ValueError('Widget should not exist already : key {}, {}.'.format(key, e))
    
    v['main widget'] = [
        '< {} main widget ({}) >'.format(key, v['main widget type']),
        ( not v['hidden'] and not v['hidden M'] ) or False,
        v['row'],
        v['value']
        ]
    
    if v['has minus button']:
        v['minus widget'] = [
            '< {} minus widget (QToolButton) >'.format(key),
            ( not v['hidden'] and not v['hidden M'] and not v['hide minus button'] ) or False,
            v['row'],
            None
            ]
    
    if v['authorized languages']:
        v['language widget'] = [
            '< {} language widget (QToolButton) >'.format(key),
            ( not v['hidden'] and not v['hidden M'] ) or False,
            v['row'],
            None
            ]
        v['language menu'] = [
            '< {} language menu (QMenu) >'.format(key),
            v['authorized languages'],
            v['language value']
            ]
        v['language actions'] = ['< {} language actions (QAction) >'.format(key)]
        
    if v['label'] and v['object']=='edit':
        v['label widget'] = [
            '< {} label widget (QLabel) >'.format(key),
            ( not v['hidden'] and not v['hidden M'] ) or False,
            v['label row'] if v['label row'] is not None else v['row'],
            None
            ]

    if 'group' in v['object']:
        v['grid widget'] = [
            '< {} grid widget (QGridLayout) >'.format(key),
            ( not v['hidden'] and not v['hidden M'] ) or False,
            None,
            None
            ]

    if v['multiple sources']:
        v['switch source widget'] = [
            '< {} switch source widget (QToolButton) >'.format(key),
            ( not v['hidden'] and not v['hidden M'] ) or False,
            v['row'],
            None
            ]
        v['switch source menu'] = [
            '< {} switch source menu (QMenu) >'.format(key),
            v['sources'],
            v['current source']
            ]
        v['switch source actions'] = ['< {} switch source actions (QAction) >'.format(key)]   


def execute_pseudo_actions(widgetsdict, actions):
    """Exécution de pseudo-actions sur un dictionnaire de widgets.
    
    ARGUMENTS
    ---------
    - widgetsdict (WidgetsDict) : dictionnaire obtenu par exécution de la
    fonction build_dict. Il doit avoir été préalablement peuplé par
    populate_widgets().
    - actions (dict) : un dictionnaire d'actions, tels ceux renvoyés
    par les méthodes add(), drop(), etc.
    
    RESULTAT
    --------
    Pas de valeur renvoyée, la fonction agit sur les clés
    'actions', 'menu' et 'widget' des dictionnaires internes
    de widgetsdict.
    """
    for a, l in actions.items():
    
        if a == "concepts list to update":
            pass
    
        elif a == "widgets to show":
            for w in l:
                w[1] = True
                
        elif a == "widgets to hide":
            for w in l:
                w[1] = False
                
        elif a == "widgets to move":
            for t in l:
                t[1][2] = t[2]
                
        elif a == "language menu to update":
            for k in l:
                widgetsdict[k]['language menu'][1] = widgetsdict[k]['authorized languages']
                widgetsdict[k]['language menu'][2] = widgetsdict[k]['language value']
                
        elif a == "switch source menu to update":
            for k in l:
                widgetsdict[k]['switch source menu'][1] = widgetsdict[k]['sources']
                widgetsdict[k]['switch source menu'][2] = widgetsdict[k]['current source']

        elif a == "new keys":
            for k in l:
                populate_widgets_key(widgetsdict, k)
                
        elif a == "widgets to delete":
            # on ne peut pas pseudo-supprimer ces pseudo-widgets, car les clés correspondantes
            # ont déjà disparu du dictionnaire. Mais on peut au moins vérifier que
            # les clés citées ne sont plus là.
            for w in l:
                for k, v in widgetsdict.items():
                    for e in ('main widget', 'minus widget', 'language widget', 'label widget',
                        'grid widget', 'switch source widget'):
                        if v[e] == w:
                            raise RuntimeError("This key should have been droped : {}.".format(k))
        
        elif a == "actions to delete":
            # on ne peut pas pseudo-supprimer ces pseudo-actions, car les clés correspondantes
            # ont déjà disparu du dictionnaire. Mais on peut au moins vérifier que
            # les clés citées ne sont plus là.
            for w in l:
                for k, v in widgetsdict.items():
                    for e in ('language actions', 'switch source actions'):
                        if v[e] == w:
                            raise RuntimeError("This key should have been droped : {}.".format(k))
        
        elif a == "menus to delete":
            # on ne peut pas pseudo-supprimer ces pseudo-actions, car les clés correspondantes
            # ont déjà disparu du dictionnaire. Mais on peut au moins vérifier que
            # les clés citées ne sont plus là.
            for w in l:
                for k, v in widgetsdict.items():
                    for e in ('language menu', 'switch source menu'):
                        if v[e] == w:
                            raise RuntimeError("This key should have been droped : {}.".format(k))

        elif a == "widgets to empty":
            for w in l:
                w[3] = None

        else:
            raise ValueError('Unknow action : "{}".'.format(a))


def write_pseudo_widget(widgetsdict, key, value):
    """Mime la saisie par l'utilisateur d'une valeur dans un pseudo-widget de saisie.
    
    ARGUMENTS
    ---------
    - widgetsdict (WidgetsDict) : dictionnaire obtenu par exécution de la
    fonction build_dict.
    - key (tuple) : la clé de widgetsdict pour laquelle on saisir une valeur.
    Si elle ne pointe pas sur un widget de saisie, la fonction renverra une
    erreur.
    - value (str) : la valeur à saisir.
    
    RESULTAT
    --------
    Pas de valeur renvoyée.
    """
    if not widgetsdict[key]['object'] == 'edit':
        raise rdf_utils.ForbiddenOperation("This widget isn't meant for writing ({}).".format(
            widgetsdict[key]['object']))
    
    if not widgetsdict[key]['main widget']:
        raise RuntimeError("Couldn't find any widget to write in.")
    
    widgetsdict[key]['main widget'][3] = value
    

def copy_metagraph(metagraph):
    """Renvoie une copie non liée du graphe.
    
    ARGUMENTS
    ---------
    - metagraph (rdflib.graph.Graph) : un graphe RDF.
    
    RESULTAT
    --------
    Une copie non liée / shallow copy de metagraph (rdflib.graph.Graph).
    """
    g = Graph()
    for triple in metagraph:
        g.add(triple)
    
    g.namespace_manager = metagraph.namespace_manager
    
    return g


def random_widgetsdict(**args):
    """Génère un dictionnaire de widgets avec un paramétrage aléatoire.
    
    ARGUMENTS
    ---------
    - [optionnel] **args : un paramètre (nommé) imposé pour build_dict().
    
    RESULTAT
    --------
    Un tuple dont le premier élément est le dictionnaire de widgets
    (WidgetsDict) et le second la retranscription de la commande lancée (str).
    
    EXEMPLES
    --------
    Pour que le dictionnaire soit nécessairement en mode édition avec
    traduction activée :
    >>> random_widgetsdict(mode='edit', translation=True)
    """
    d = {
        'metagraph': args['metagraph'] if 'metagraph' in args \
            else [1, 2, 3, 4][randrange(4)],
            
        'shape': args.get('shape') or rdf_utils.load_shape(),
        
        'vocabulary': args.get('vocabulary') \
            or rdf_utils.load_vocabulary(),
            
        'template': args['template'] if 'template' in args else [
            None, {}, 'template_basique', 'template_classique',
            'template_donnee_externe', 'build-in template'
            ][randrange(6)],
        
        'templateTabs': None,
        # 'templateTabs' est implémenté ensuite, car dépend de template
        
        'columns': args['columns'] if 'columns' in args else [
            None,
            [],
            [
                ("champ 1", "description champ 1"),
                ("champ 2", "description champ 2"),
                ("champ 3", "description champ 3")
                ]
            ][randrange(3)],
            
        'data': args['data'] if 'data' in args else [
            None,
            {},
            {
                'dct:modified' : ['2021-08-31'],
                'snum:relevanceScore' : [100]
                }
            ][randrange(3)],
            
        'mode': args.get('mode') or ['edit', 'read'][randrange(2)],
        
        'readHideBlank': args['readHideBlank'] \
            if 'readHideBlank' in args \
            else [True, False][randrange(2)],
            
        'readHideUnlisted': args['readHideUnlisted'] \
            if 'readHideUnlisted' in args \
            else [True, False][randrange(2)],
            
        'editHideUnlisted': args['editHideUnlisted'] \
            if 'editHideUnlisted' in args \
            else [True, False][randrange(2)],
        
        'language': None,
        # 'language' est implémenté ensuite, car dépend de langList
        
        'translation': None,
        # 'translation' est implémenté ensuite, car dépend de mode
        
        'langList': args.get('langList') or [
            ['fr', 'en'],
            ['fr', 'en', 'it', 'de'],
            ['en', 'it', 'de'],
            ['fr']
            ][randrange(4)],
            
        'readOnlyCurrentLanguage': args['readOnlyCurrentLanguage'] \
            if 'readOnlyCurrentLanguage' in args \
            else [True, False][randrange(2)],
            
        'editOnlyCurrentLanguage': args['editOnlyCurrentLanguage'] \
            if 'editOnlyCurrentLanguage' in args \
            else [True, False][randrange(2)]
            
        # les paramètres 'labelLengthLimit', 'valueLengthLimit'
        # et 'textEditRowSpan' ne sont pas considérés, car
        # leur influence sur la structure du dictionnaire est
        # négligeable
        }

    d['language'] = args.get('language') \
        or d['langList'][randrange(len(d['langList']))]
        # si le paramètre est fourni, il pourrait ne pas
        # être dans langList. On laisse build_dict
        # générer l'erreur.
        
    d['translation'] = args['translation'] \
        if 'translation' in args else \
        ( False if d['mode'] != 'edit' \
        else [True, False][randrange(2)] )
        # si le paramètre est fourni, il pourrait ne pas
        # être cohérent avec le mode. On laisse build_dict
        # générer l'erreur.
        
    # on pré-génère la transcription maintenant, tant que metagraph
    # et template sont encore numérotés.
    lit = "build_dict(\n    metagraph = {{}}," \
        "\n    shape = shape,\n    vocabulary = vocabulary," \
        "\n    template = {{}}," \
        "\n    templateTabs = {{}},\n    {}\n    )".format(
        ",\n    ".join([
            "{} = {}".format(k, repr(v).replace('{', '{{').replace('}', '}}')) \
                for k, v in d.items() if not k in ('shape', 'vocabulary',
                'metagraph', 'template', 'templateTabs') 
            ])
        )

    if d['metagraph'] == 1:
        d['metagraph'] = Graph()
        litMetagraph = 'Graph()'
    elif d['metagraph'] == 2:
        d['metagraph'] = rdf_utils.metagraph_from_file(
            __path__[0] + r'\bibli_rdf\exemples\exemple_dataset_1.ttl'
            )
        litMetagraph = 'exemple_dataset_1.ttl'
    elif d['metagraph'] == 3:
        d['metagraph'] = rdf_utils.metagraph_from_file(
            __path__[0] + r'\bibli_rdf\exemples\exemple_dataset_2.ttl'
            )
        litMetagraph = 'exemple_dataset_2.ttl'
    elif d['metagraph'] == 4:
        raw_metagraph = rdf_utils.metagraph_from_file(
            __path__[0] + r'\bibli_rdf\tests\samples\dcat_eurostat_bilan_nutritif_brut_terre_agricole.jsonld'
            )
        d['metagraph'] = rdf_utils.clean_metagraph(raw_metagraph, d['shape'])
        litMetagraph = 'dcat_eurostat_bilan_nutritif_brut_terre_agricole.jsonld'
    else:
        litMetagraph = repr(d['metagraph'])

    # les templates 3, 4 et 5 sont les trois modèles pré-définis
    # de l'extension PG metadata, exportés en JSON dans
    # plume\bibli_pg\admin\export grâce à la fonction
    # export_sample_templates de template_admin.
    if d['template'] in ('template_basique', 'template_classique',
        'template_donnee_externe'):
        with open(r'{}\bibli_pg\admin\export\{}.json'.format(
            __path__[0], d['template']
            ), encoding='utf-8') as src:
            tpl_json = load(src)
            litTemplate = '{}.json [template]'.format(d['template'])
            litTemplateTabs = '{}.json [templateTabs]'.format(d['template'])
            d['template'] = tpl_json['template']
            d['templateTabs'] = tpl_json['templateTabs']
            
    # le template 6 est un modèle sur-mesure plus vicieux
    elif d['template'] == 'build-in template':
        litTemplate = 'build-in template [template]'
        litTemplateTabs = 'build-in template [templateTabs]'
        d['templateTabs'] = {
            "Onglet n°1": (0,),
            "Onglet n°2": (1,),
            "Onglet n°3": (2,)
            }
        d['template'] = {
            "dct:title": {
                "order": 1
                },
            "dcat:contactPoint": {
                "tab name": "Onglet n°3"
                },
            "dcat:contactPoint / vcard:fn": {
                "default value": "Pôle SIG"
                },
            "dcat:contactPoint / vcard:hasEmail": {
                "default value": "sig-contact@developpement-durable.gouv.fr",
                "read only": True,
                "tab name": "Onglet n°4"
                },
            "dcat:keyword": {
                "tab name": "Onglet n°4"
                },
            "uuid:218c1245-6ba7-4163-841e-476e0d5582af" : {
                "label": "notes ADL",
                "data type": "xsd:string",
                "main widget type": "QTextEdit",
                "order": 3
                },
            'dcat:distribution': {},
            'dcat:distribution / dct:license': {
                'default value': "Licence Ouverte version 2.0"
                },
            'dcat:distribution / dct:license / rdfs:label': {
                'default value': "Valeur par défaut..."
                },
            'dcat:theme': {
                'default value' : "Gouvernement et secteur public"
                },
            'dct:accessRights': {}
            }

    else:
        litTemplate = repr(d['template'])
        litTemplateTabs = repr(d['templateTabs'])

    lit = lit.format(litMetagraph, litTemplate, \
        litTemplateTabs)
    widgetsdict = rdf_utils.build_dict(**d)
    
    return widgetsdict, lit


def random_action(widgetsdict):
    """Exécute une action aléatoire sur le dictionnaire de widgets.
    
    ARGUMENTS
    ---------
    - widgetsdict (WidgetsDict) : dictionnaire obtenu par exécution de la
    fonction build_dict, nécessairement avec mode='edit', sans quoi aucune
    action ne pourra être réalisée.
    
    RESULTAT
    --------
    Un tuple avec :
    [0] résultat de l'action (list), tel que renvoyé par les méthodes add(),
    drop(), change_source() et change_language(). Dans le cas d'update_value,
    il s'agit d'un tuple dont le premier élément est la clé du dictionnaire
    mise à jour, le second la valeur saisie.
    [1] le nom de la méthode utilisée, parmi 'add', 'drop', 'change_language',
    'change_source', 'update_value'.
    [2] une chaîne de caractères correspondant à la commande lancée.
    """
    if widgetsdict.mode == 'read':
        raise rdf_utils.ForbiddenOperation("What are you trying to do in 'read' mode ?!")
    
    method = None
    key = None
    methods = ['add', 'drop', 'change_language', 
        'change_source', 'update_value']
    keys = [ k for k, v in widgetsdict.items() if v['main widget type'] \
        and not v['hidden'] and not v['hidden M'] ]
    
    while method is None:
        m = methods.copy()
        key = keys[randrange(len(keys))]
        v = widgetsdict[key]
        if not v['object'] == 'edit':
            m.remove('update_value')
        if not v['has minus button'] or v['hide minus button']:
            m.remove('drop')
        if not v['object'] in ('plus button', 'translation button'):
            m.remove('add')
        if not v['multiple sources']:
            m.remove('change_source')
        if not v['authorized languages']:
            m.remove('change_language')
        if m:
            method = m[randrange(len(m))]
    
    if method == 'add':
        lit = 'add({})'.format(key)
        res = widgetsdict.add(key)
        
    elif method == 'drop':
        lit = 'drop({})'.format(key)
        res = widgetsdict.drop(key)
        
    elif method == 'change_language':
        languages = widgetsdict[key]['authorized languages']
        lang = languages[randrange(len(languages))]
        lit = "change_language({}, '{}')".format(key, lang)
        res = widgetsdict.change_language(key, lang)
        
    elif method == 'change_source':
        sources = widgetsdict[key]['sources']
        src = sources[randrange(len(sources))]
        lit = "change_source({}, '{}')".format(key, src)
        res = widgetsdict.change_source(key, src)
    
    elif method == 'update_value':
        dval = {
            URIRef('http://www.w3.org/2001/XMLSchema#string'): "valeur textuelle",
            URIRef('http://www.w3.org/2001/XMLSchema#integer'): 1,
            URIRef('http://www.w3.org/2001/XMLSchema#decimal'): 0.5,
            URIRef('http://www.w3.org/2001/XMLSchema#float'): 0.5,
            URIRef('http://www.w3.org/2001/XMLSchema#double'): 0.5,
            URIRef('http://www.w3.org/2001/XMLSchema#boolean'): False,
            URIRef('http://www.w3.org/2001/XMLSchema#date'): "2021-10-31",
            URIRef('http://www.w3.org/2001/XMLSchema#time'): "00:00:00",
            URIRef('http://www.w3.org/2001/XMLSchema#dateTime'): "2021-10-31T00:00:00",
            URIRef('http://www.w3.org/2001/XMLSchema#duration'): "valeur textuelle",
            URIRef('http://www.opengis.net/ont/geosparql#wktLiteral'): "valeur textuelle",
            URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#langString'): "valeur textuelle"
            }
        val = dval[widgetsdict[key]['data type'] \
            or URIRef('http://www.w3.org/2001/XMLSchema#string')]
        lit = "update_value({}, '{}')".format(key, val)
        widgetsdict.update_value(key, val)
        res = (key, val)
        
    return res, method, lit


def random_wd_test_suite(nTargets=20, nActions=200, log=True,
    verbose=True, populated=True):
    """Recette aléatoire de build_dict() et des méthodes d'actions de la classe WidgetsDict.
    
    ARGUMENTS
    ---------
    - nTargets (int) : nombre de dictionnaires de widgets à créer
    successivement. 20 par défaut.
    - nActions (int) : nombre d'actions à effectuer par dictionnaire.
    200 par défaut.
    - log (bool) : les actions réalisées doivent-elles être retranscrites
    dans un fichier de log ? True par défaut.
    - verbose (bool) : les actions réalisées doivent-elles être imprimées
    dans la console ? True par défaut.
    - populated (bool) : True si les dictionnaires doivent êtres peuplés
    de pseudo-widgets avec la populate_widgets(). Dans ce cas, la recette
    vérifie aussi que les clés '... widget' sont remplies comme il le faut.
    True par défaut.
    
    RESULTAT
    --------
    Rien si la recette s'est déroulé sans qu'aucun problème ne soit détecté.
    À chaque itération, la fonction génère un dictionnaire de widgets en
    mode édition avec un paramétrage semi-aléatoire grâce à
    random_widgetsdict(), puis lance random_action() pour simuler des actions
    de l'utilisateur sur ce dictionnaire. Si ce dernier est peuplé de pseudo-
    widgets, la fonction utilise execute_random_actions() pour répercuter
    ces actions sur eux. Après chaque action, check_everything() est exécuté
    pour détecter des anomalies éventuelles.
    
    Si check_everything() renvoie un résultat non nul, random_wd_tests_suite()
    s'arrête et renvoie ce résultat. Si une action produit une erreur,
    random_wd_tests_suite() s'arrête et renvoie l'erreur.
    
    Les logs sont écrits dans le fichier
    /__log__/random_wd_tests_suite_log_[timestamp].txt. Ils contiennent toutes
    les commandes exécutées successivement et, le cas échéant, les anomalies ou
    l'erreur qui ont conclu la recette.
    """
    ending = None
    logfile = r'{}\bibli_rdf\tests\__log__\random_wd_tests_suite_log_{}.txt'.format(
        __path__[0], strftime("%Y%m%d%H%M%S", gmtime())
        )
    shape = rdf_utils.load_shape()
    vocabulary = rdf_utils.load_vocabulary()
    
    while nTargets > 0:
    
        nTargets -= 1
        d = None
        lit = None
    
        # génération d'un dictionnaire de widgets
        try:
            d, lit = random_widgetsdict(shape=shape,
                vocabulary=vocabulary, mode='edit')
                # on force le mode édition pour pouvoir exécuter des actions
                # shape et vocabulary sont passés en arguments pour
                # éviter à random_widgetsdict de les générer à chaque itération
        except Exception as err:
            ending = "!ERROR! Widgetsdict generation failure :\n{}".format(err)
            break
    
        if log:
            # retranscription de la commande de génération
            # du dictionnaire
            with open(logfile, 'a') as dest:
                dest.write("\n{}\n".format(lit))
        if verbose:
            print("\n{}".format(lit))
        
        # premier contrôle
        try:
            if populated:
                populate_widgets(d)
            anom = check_everything(d, populated=populated)
        except Exception as err:
            ending = "!ERROR! Control failure :\n{}".format(err)
            break
        
        if anom:
            ending = "!ANOMALY! Something wrong was detected :\n{}".format(anom)
            break
        
        # actions
        mNAction = nActions
        while mNAction > 0:
        
            mNAction -= 1
            res = None
            method = None
            lit = None
            
            # exécution de l'action
            try:
                res, method, lit = random_action(d)
            except Exception as err:
                ending = "!ERROR! Action failure :\n{}".format(err)
                break
                
            if log:
                # retranscription de la commande d'action
                with open(logfile, 'a') as dest:
                    dest.write("{}\n".format(lit))
            if verbose:
                print("{}".format(lit))
        
            # contrôle
            try:
                if populated:
                    if method == 'update_value':
                        write_pseudo_widget(d, res[0], res[1])
                    else:
                        execute_pseudo_actions(d, res)
                anom = check_everything(d, populated=populated)
            except Exception as err:
                ending = "!ERROR! Control failure :\n{}".format(err)
                break
            
            if anom:
                ending = "!ANOMALY! Something wrong was detected :\n{}".format(anom)
                break
          
    if ending:
        if log:
            with open(logfile, 'a') as dest:
                dest.write("{}\n".format(ending))
        if verbose:
            print("{}".format(ending))
    
    return ending
    
