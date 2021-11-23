"""
Fonctions pour l'import et la préparation du modèle de formulaire (template).

"""

import re

try:
    from rdflib import Graph
except:
    from plume.bibli_install.bibli_install import manageLibrary
    # installe RDFLib si n'est pas déjà disponible
    manageLibrary()
    from rdflib import Graph
    
from plume.bibli_rdf.rdf_utils import uripath_from_sparqlpath, get_datasetid



def search_template(metagraph, templates):
    """Recherche le modèle de formulaire à utiliser.
    
    ARGUMENTS
    ---------
    - metagraph (rdflib.graph.Graph) : le graphe de métadonnées
    extrait du commentaire de la table grâce à la fonction 
    rdf_utils.metagraph_from_pg_description() ;
    - templates (list) : la liste de tous les modèles disponibles
    avec leurs conditions d'usage (tuples). Concrètement il est 
    obtenu ainsi :
    >>> cur.execute(query_list_templates(), (schema_name, table_name))
    >>> templates = cur.fetchall()
    
    RESULTAT
    --------
    Le nom de l'un des modèles de la liste (str) ou None si
    aucun de convient. Dans ce cas, on utilisera le modèle
    préféré (preferedTemplate) désigné dans les paramètres
    de configuration de l'utilisateur ou, à défaut, aucun
    modèle.
    
    Quand plusieurs modèles conviennent, celui qui a la plus
    grande valeur de "priority" est retenu. Si le niveau
    de priorité est le même, c'est l'ordre alphabétique qui
    déterminera quel modèle est conservé.
    """
    r = None
    p = 0
    # p servira pour la comparaison du niveau de priorité
    
    for t in templates:
    
        if t[3] is None or t[3] <= p:
            continue
        
        # filtre SQL (dont on a d'ores-et-déjà le résultat
        # dans t[1], calculé côté serveur)
        if t[1]:
            r = t[0]
            p = t[3]
        
        # conditions sur les métadonnées
        if isinstance(t[2], dict):
            u = get_datasetid(metagraph)
            
            for e in t[2].values():
            
                if isinstance(e, dict) and len(e) > 0:
                    b = True
                    
                    for k, v in e.items():
                        uri_path = uripath_from_sparqlpath(
                            k, nsm = metagraph.namespace_manager, strict = False
                            )
                        if uri_path is None:
                            b = False
                            break
                        
                        if v is None:
                            b = metagraph.value(u, uri_path) is None
                        else:
                            b = any(str(o).lower() == str(v).lower() for o in metagraph.objects(u, uri_path))
                            # comparaison avec conversion, qui ne tient
                            # pas compte du type ni de la langue ni de la casse
                            
                        if not b:
                            break
                            
                    if b:
                        r = t[0]
                        p = t[3]
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


