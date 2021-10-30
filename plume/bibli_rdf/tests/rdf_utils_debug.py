"""Utilitaires pour la recette de rdf_utils.
"""
from rdflib import Graph, Namespace, Literal, BNode, URIRef
from rdflib.compare import isomorphic

from plume.bibli_rdf import rdf_utils


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
    - [optionnel] args (dict) peut contenir tout autre paramètre à passer à build_dict()
    sous forme clé/valeur.
    
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
    >>> rdf_utils_debug.check_unchanged(g, g_shape, g_vocabulary)
    
    Avec un paramètre supplémentaire :
    >>> rdf_utils_debug.check_unchanged(g, g_shape, g_vocabulary,
    ...     args={"template": d_template})   
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
    
    NB. Cette fonction est faite pour des dictionnaires construits pour le mode édition.
    Il n'est pas supposé y avoir de boutons plus et moins en mode lecture.
    """
    issues = {}
    n = 0
    
    for k, v in widgetsdict.items():
    
        if rdf_utils.is_root(k):
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


def check_rows(widgetsdict, populated=False, mode='edit'):
    """Check if row keys of given widget dictionnary are consistent.

    ARGUMENTS
    ---------
    - widgetsdict (WidgetsDict) : dictionnaire obtenu par exécution de la
    fonction build_dict.
    - populated (bool) : True si le dictionnaire a été peuplé de pseudo-widgets
    avec la populate_widgets(). Dans ce cas, la fonction vérifie aussi que les
    clés '... widget' sont remplies comme il le faut.
    - mode (str) : le mode pour lequel a été généré le graphe, 'read' ou 'edit'.
    
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
    



def execute_random_action(widgetsdict):
    """Exécute une action choisie au hasard sur le dictionnaire de widgets.
    
    ARGUMENTS
    ---------
    - widgetsdict (WidgetsDict) : dictionnaire obtenu par exécution de la
    fonction build_dict, nécessairement avec mode='edit', sans quoi aucune
    action ne pourra être réalisée.
    
    RESULTAT
    --------
    Un tuple avec :
    [0] résultat de l'action (list), tel que renvoyé par les méthodes add(),
    drop(), change_source() et change_language() ;
    [1] une description litérale (str) de l'action réalisée.
    """
    pass

