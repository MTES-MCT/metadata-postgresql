"""Import et préparation des modèles de formulaire.

"""

import re

from plume.rdf.utils import path_from_n3


class TemplateDict(dict):
    """Modèle de formulaire.
    
    """

class TemplateTabsList(list):
    """Liste des onglets d'un modèle.
    
    """

def search_template(templates, metagraph=None):
    """Déduit d'un graphe de métadonnées le modèle de formulaire à utiliser.
    
    Parameters
    ----------
    templates : list of tuples
        La liste de tous les modèles disponibles avec leurs conditions
        d'usage (tuples), résultant de l'exécution de la requête
        :py:func:`plume.pg.queries.query_list_templates`.
    metagraph : plume.rdf.metagraph.Metagraph, optional
        Le graphe de métadonnées issu de la dé-sérialisation des
        métadonnées d'un objet PostgreSQL. Lorsque cet argument n'est
        pas fourni, vaut ``None`` ou un graphe vide, les conditions
        d'application des modèles portant sur le graphe ne sont
        pas considérées.
    
    Returns
    -------
    str
        Le nom de l'un des modèles de la liste ou ``None`` si
        aucun de convient. Dans ce cas, on utilisera le modèle
        préféré (``preferedTemplate``) désigné dans les paramètres
        de configuration de l'utilisateur ou, à défaut, aucun
        modèle.
    
    Notes
    -----
    Quand plusieurs modèles conviennent, celui qui a la plus
    grande valeur de ``priority`` est retenu. Si le niveau
    de priorité est le même, c'est l'ordre alphabétique qui
    déterminera quel modèle est conservé (car c'est ainsi
    qu'est triée la liste renvoyée par
    :py:func:`plume.pg.queries.query_list_templates`), et
    la présente fonction considère simplement les modèles
    dans l'ordre.
    
    """
    r = None
    p = 0
    # p servira pour la comparaison du niveau de priorité
    
    for tpl_label, check_sql_filter, md_conditions, priority in templates:
    
        if r and (priority is None or priority <= p):
            continue
        
        # filtre SQL (dont on a d'ores-et-déjà le résultat
        # dans sql_filter_check, calculé côté serveur)
        if sql_filter_check:
            r = tpl_label
            p = priority
        
        # conditions sur les métadonnées
        if isinstance(md_conditions, list):
            datasetid = metagraph.datasetid
            nsm = metagraph.namespace_manager
            for ands in md_conditions:
                if isinstance(ands, dict) and len(ands) > 0:
                    b = True
                    for path_n3, expected in ands.items():
                        path = path_from_n3(path_n3, nsm)
                        if path is None:
                            b = False
                            break
                        if expected is None:
                            b = metagraph.value(datasetid, path) is None
                        else:
                            b = any(str(o).lower() == str(expected).lower() \
                                for o in metagraph.objects(datasetid, path))
                            # comparaison avec conversion, qui ne tient
                            # pas compte du type ni de la langue ni de la casse.
                            # pourrait être largement amélioré
                        if not b:
                            break 
                    if b:
                        r = tpl_label
                        p = priority
                        break
    
    return r


def build_template(categories):
    """Crée un modèle de formulaire exploitable à partir d'une liste de catégories.
    
    ARGUMENTS
    ---------
    - categories (list) : la liste de toutes les catégories
    du modèle et leur paramétrage (tuples). Concrètement elle est 
    importée du serveur PostgreSQL de cette façon :
    >>> cur.execute(query_list_templates())
    >>> templates = cur.fetchall()
    >>> tpl_label = search_template(metagraph, templates)
    Si n'est pas None :
    >>> cur.execute(query_get_categories(), (tpl_label,))
    >>> categories = cur.fetchall()
    
    RESULTAT
    --------
    Le modèle de formulaire (template) qui sera à donner en argument à la
    fonction rdf_utils.build_dict().
    """
    d = {}
    
    for c in sorted(categories, reverse=True):
        p = c[1]
    
        if c[0] == 'shared':
        
            # cas d'une branche vide qui n'a pas
            # de raison d'être :
            if not c[1] in d and c[13]:
                continue
                # si le noeud avait eu un prolongement,
                # le tri inversé sur categories fait
                # qu'il aurait été traité avant, et
                # le présent chemin aurait alors été
                # pré-enregistré dans le dictionnaire
                # (cf. opérations suivantes)
                # NB : on distingue les noeuds vides
                # au fait que is_node vaut True. Ce
                # n'est pas une méthode parfaite,
                # considérant que des modifications
                # manuelles restent possibles. Les
                # conséquences ne seraient pas
                # dramatique cependant (juste un groupe
                # sans rien dedans).       
        
            # gestion préventive des hypothétiques
            # ancêtres manquants :
            t = re.split(r'\s*[/]\s*', c[1])
            
            p = ' / '.join(t)
            # avec espacement propre, à toute fin utile
            
            if len(t) > 1:
                tbis = [ ' / '.join(t[:i + 1] ) \
                        for i in range(len(t) - 1) ]
            
                for e in tbis:
                    if not e in d:
                        d.update({ e : {} })
                        # insertion des chemins des
                        # catégories ancêtres
                        # s'ils étaient dans la table PG,
                        # le tri inversé sur categories fait
                        # qu'ils ne sont pas encore passés ;
                        # les bonnes valeurs seront renseignées
                        # par l'un des prochains update.
    
        d.update({
                p : {
                    'label' : c[2],
                    'main widget type' : c[3],
                    'row span' : c[4],
                    'help text' : c[5],
                    'default value' : c[6],
                    'placeholder text' : c[7],
                    'input mask' : c[8],
                    'multiple values' : c[9],
                    'is mandatory' : c[10],
                    'order' : c[11],
                    'read only' : c[12],
                    'data type' : c[14],
                    'tab name': c[15]
                    }
            })
  
    return d
    

def build_template_tabs(tabs):
    """Crée un dictionnaire exploitable à partir d'une liste d''onglets.
    
    ARGUMENTS
    ---------
    - tabs (list) : la liste de toutes les onglets du modèle
    et leur paramétrage (tuples). Concrètement elle est 
    importée du serveur PostgreSQL de cette façon :
    >>> cur.execute(query_list_templates())
    >>> templates = cur.fetchall()
    >>> tpl_label = search_template(metagraph, templates)
    Si n'est pas None :
    >>> cur.execute(query_template_tabs(), (tpl_label,))
    >>> tabs = cur.fetchall()
    
    RESULTAT
    --------
    La liste d'onglets (templateTabs) qui sera à donner en argument à la
    fonction rdf_utils.build_dict().
    
    La fonction renvoie None si le modèle ne définit pas d'onglets.
    """
    n = 0
    d = {}
    
    for t in tabs:
        d.update({ t[0]: (n,) })
        n += 1
    
    if n > 0:
        return d


