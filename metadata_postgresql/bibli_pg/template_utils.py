"""
Fonctions pour l'import et la préparation du modèle de formulaire (template).

"""

import re
from rdflib import Graph
from rdflib.util import from_n3


def search_template(schema_name, table_name, metagraph,
    templates):
    """Recherche le modèle de formulaire à utiliser.
    
    ARGUMENTS
    ---------
    - schema_name (str) : nom du schéma de la table ;
    - table_name (str) : nom de la table ou vue ;
    - metagraph (rdflib.graph.Graph) : le graphe de métadonnées
    extrait du commentaire de la table grâce à la fonction 
    rdf_utils.metagraph_from_pg_description() ;
    - templates (list) : la liste de tous les modèles disponibles
    avec leurs conditions d'usage (tuples). Concrètement il est 
    obtenu ainsi :
    >>> cur.execute(query_list_templates())
    >>> templates = cur.fetchall()
    
    RESULTAT
    --------
    Le nom de l'un des modèles de la liste (str) ou None si
    aucun de convient. Dans ce cas, on utilisera le modèle
    préféré (preferedTemplate) désigné dans les paramètres
    de configuration de l'utilisateur ou, à défaut, aucun
    modèle.
    
    Quand plusieurs modèles convienne, celui qui a la plus
    grande valeur de "priority" est retenu. Si le niveau
    de priorité est le même, le modèle avec le plus petit
    identifiant (= le premier traité) sera conservé.
    """
    r = None
    p = 0
    # p servira pour la comparaison du niveau de priorité
    
    for t in templates:
    
        if t[7] <= p:
            continue
        
        # table_prefix
        for e in t[2]:
            s = re.escape(e)
            if re.search('^' + s, table_name):
                r = t[1]
                p = t[7]
                break
        
        # table_suffix
        for e in t[3]:
            s = re.escape(e)
            if re.search(s + '$', table_name):
                r = t[1]
                p = t[7]
                break
        
        # schema_prefix
        for e in t[4]:
            s = re.escape(e)
            if re.search('^' + s, schema_name):
                r = t[1]
                p = t[7]
                break
        
        # schema_suffix
        for e in t[5]:
            s = re.escape(e)
            if re.search(s + '$', schema_name):
                r = t[1]
                p = t[7]
                break
        
        # conditions
        if isinstance(t[6], dict):
            for e in t[6].values():
            
                if isinstance(e, dict) and len(e) > 0:
                    b = True
                    
                    for k, v in e.items():
                        q_gr = metagraph.query(
                                """
                                SELECT
                                    ?value
                                WHERE
                                     { ?u a dcat:Dataset ;
                                          ?path ?value. }
                                """,
                                initBindings = {
                                    'path': from_n3(k, nsm=metagraph.namespace_manager)
                                    }
                                )
                         
                        if len(q_gr) < 1 \
                            or not any([str(o['value']).lower() == str(v).lower() for o in q_gr]):
                            # comparaison avec conversion, qui ne tient
                            # pas compte du type ni de la langue ni de la casse
                            b = False
                            
                    if b:
                        r = t[1]
                        p = t[7]
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
    >>> tpl_label = search_template(schema_name, table_name, metagraph, templates)
    Si n'est pas None :
    >>> cur.execute(query_get_categories(), (tpl_label,))
    >>> categories = cur.fetchall()
    
    RESULTAT
    --------
    Le modèle de formulaire (template) qui sera à donner en argument à la
    fonction rdf_utils.build_dict().
    """
    d = {}
    
    for c in categories:
        d.update({
                c[1] : {
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
                    'read only' : c[12]
                    }
            })
  
    return d
    
