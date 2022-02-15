"""Import et préparation des modèles de formulaire.

"""

import re

from plume.rdf.rdflib import URIRef, from_n3
from plume.rdf.utils import path_from_n3, forbidden_char
from plume.rdf.namespaces import RDFS, SH, PlumeNamespaceManager

nsm = PlumeNamespaceManager()

class TemplateDict:
    """Modèle de formulaire.
    
    Parameters
    ----------
    categories : list of tuples
        Liste des catégories de métadonnées prévues par le modèle
        avec leur paramétrage, résultant de l'exécution de la
        requête :py:func:`plume.pg.queries.query_get_categories`.
    tabs : list(str), optional
        Liste ordonnée des onglets du modèle, résultant de l'exécution
        de la requête :py:func:`plume.pg.queries.query_template_tabs`.
    
    Attributes
    ----------
    tabs : list(str)
        La liste ordonnée des onglets du modèle. Il s'agira d'une
        liste vide si le modèle ne spécifie pas d'onglets.
    shared : dict
        Les catégories communes utilisées par le modèle. Les clés
        du dictionnaire sont les chemins N3 des catégories, les
        valeurs sont des dictionnaires contenant les informations
        de paramétrage.
    local : dict
        Les catégories locales utilisées par le modèle. Les clés
        du dictionnaire sont les chemins N3 des catégories, les
        valeurs sont des dictionnaires contenant les informations
        de paramétrage.
    
    """
    
    def __init__(self, categories, tabs=None):
    
        self.tabs = [tab for tab, in tabs or []]
        self.shared = {}
        self.local = {}
        
        for path, origin, label, description, special, \
            is_node, datatype, is_long_text, rowspan, \
            placeholder, input_mask, is_multiple, unilang, \
            is_mandatory, sources, geo_tools, template_order, \
            is_read_only, tab in sorted(categories, reverse=True):
            
            config = {
                'label': label,
                'description': description,
                'datatype': from_n3(datatype, nsm=nsm),
                'is_long_text': is_long_text,
                'rowspan': rowspan,
                'placeholder': placeholder,
                'input_mask': input_mask,
                'is_multiple': is_multiple,
                'unilang': unilang,
                'is_mandatory': is_mandatory,
                'sources': [URIRef(s) for s in sources or []
                    if not forbidden_char(s)],
                'geo_tools': geo_tools,
                'template_order': template_order,
                'is_read_only': is_read_only,
                'tab': tab
                }
            
            if template_order is not None:
                config['order_idx'] = (template_order,)
                
            if special:
                config['kind'] = SH.IRI
                config['rdfclass'] = RDFS.Resource
                # NB: rdfs:Resource est un choix arbitraire et sans
                # incidence. L'essentiel est qu'il y ait une valeur
                # au moment de la construction de la clé.
                config['transform'] = special
                
            if origin == 'shared':
            
                # cas d'une branche vide qui n'a pas
                # de raison d'être :
                if is_node and not path in self.shared:
                    continue
                    # si le noeud avait eu un prolongement, le tri
                    # inversé sur categories fait qu'il aurait été
                    # traité avant, et le présent chemin aurait
                    # alors été pré-enregistré dans le dictionnaire
                    # (cf. opérations suivantes).
                    # NB : on distingue les noeuds vides au fait
                    # que is_node vaut True. Ce n'est pas une
                    # méthode parfaite, considérant que des
                    # modifications manuelles restent possibles.
                    # Les conséquences ne seraient pas dramatiques,
                    # cependant (juste un groupe sans rien dedans,
                    # qui sera éliminé à l'initialisation du
                    # dictionnaire de widgets).
            
                # gestion des hypothétiques ancêtres manquants :
                path_elements = re.split(r'\s*[/]\s*', path)
                
                path = ' / '.join(path_elements)
                # avec espacement propre, à toute fin utile
                
                if len(path_elements) > 1:
                    paths = [ ' / '.join(path_elements[:i + 1] ) \
                            for i in range(len(path_elements) - 1) ]
                    for p in paths:
                        # insertion des chemins des catégories
                        # ancêtres. S'ils étaient dans la table PG,
                        # le tri inversé sur categories fait qu'ils
                        # ne sont pas encore passés ; la configuration
                        # sera renseignée lorsque la boucle les
                        # atteindra.
                        if not p in self.shared:
                            self.shared[p] = {}
            
                self.shared[path] = config
            
            elif origin == 'local':
                del config['sources']
                self.local[path] = config

def search_template(templates, metagraph=None):
    """Déduit d'un graphe de métadonnées le modèle de formulaire à utiliser.
    
    Parameters
    ----------
    templates : list of tuples
        La liste de tous les modèles disponibles avec leurs
        conditions d'usage, résultant de l'exécution de la requête
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
        # dans check_sql_filter, calculé côté serveur)
        if check_sql_filter:
            r = tpl_label
            p = priority
            continue
        
        # conditions sur les métadonnées
        if metagraph and isinstance(md_conditions, list):
            datasetid = metagraph.datasetid
            for ands in md_conditions:
                if isinstance(ands, dict) and len(ands) > 0:
                    b = True
                    for path_n3, expected in ands.items():
                        path = path_from_n3(path_n3, nsm=nsm)
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

