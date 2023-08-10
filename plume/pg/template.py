"""Import et préparation des modèles de formulaire.

"""

import re
from json import load

from plume.rdf.rdflib import URIRef, from_n3
from plume.rdf.utils import path_from_n3, forbidden_char, abspath
from plume.rdf.namespaces import RDFS, SH, PlumeNamespaceManager

nsm = PlumeNamespaceManager()

class TemplateDict:
    """Modèle de formulaire.
    
    Parameters
    ----------
    categories : list(dict) or list(tuple(dict))
        Liste des catégories de métadonnées prévues par le modèle
        avec leur paramétrage, résultant de l'exécution de la
        requête :py:func:`plume.pg.queries.query_get_categories`
        ou importée d'un modèle local. Si la liste est constituée
        de tuples, leur premier élément doit être le dictionnaire
        qui décrit la catégorie, et tout autre élément ne sera pas
        considéré.
    tabs : list(str) or list(tuple(str)), optional
        Liste ordonnée des libellés des onglets du modèle, résultant de
        l'exécution de la requête :py:func:`plume.pg.queries.query_template_tabs`,
        ou importée d'un modèle local. Si la liste est constituée
        de tuples, leur premier élément doit être le libellé de l'onglet,
        et tout autre élément ne sera pas considéré.
    
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
    
        self.shared = {}
        self.local = {}

        if tabs and isinstance(tabs[0], tuple):
            self.tabs = [tab for tab, in tabs or []]
        else:
            self.tabs = tabs or []

        if categories and isinstance(categories[0], tuple):
            categories = [categorie_dict for categorie_dict, in categories]

        for config in sorted(categories, key=lambda x: x['path'], reverse=True):

            path = config['path']

            if config['datatype']:
                config['datatype'] = from_n3(config['datatype'], nsm=nsm)

            config['sources'] = [
                URIRef(s)
                for s in config['sources'] or []
                if not forbidden_char(s)
            ]      
            
            if config['template_order'] is not None:
                config['order_idx'] = (config['template_order'],)
                
            if config['special']:
                config['kind'] = SH.IRI
                config['rdfclass'] = RDFS.Resource
                # NB: rdfs:Resource est un choix arbitraire et sans
                # incidence. L'essentiel est qu'il y ait une valeur
                # au moment de la construction de la clé.
                config['transform'] = config['special']
                
            if config['origin'] == 'shared':
            
                # cas d'une branche vide qui n'a pas
                # de raison d'être :
                if config['is_node'] and not path in self.shared:
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
                    paths = [ 
                        ' / '.join(path_elements[:i + 1] )
                        for i in range(len(path_elements) - 1)
                    ]
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
            
            elif config['origin'] == 'local':
                del config['sources']
                self.local[path] = config

class LocalTemplatesCollection(dict):
    """Répertoire des modèles disponibles en local.
    
    Les modèles locaux se substitueront aux modèles importés
    du serveur PostgreSQL si l'extension PlumePg n'est
    pas installée sur la base courante.
    
    Un objet de classe :py:class:`LocalTemplatesCollection`
    est un dictionnaire dont les clés sont des noms des modèles
    et les valeurs sont les modèles en tant que tels (objets
    :py:class:TemplateDict).
    
    Attributes
    ----------
    labels : list(str)
        Liste des noms des modèles locaux.
    conditions : list(dict)
        Liste des modèles avec leur configuration, notamment leurs
        conditions d'application automatique. Concrètement, il s'agit
        des informations qu'on aurait trouvées dans la table
        ``z_plume.meta_template`` si PlumePg avait été
        active sur la base (a minima le champ ``tpl_label`` contenant
        le nom du modèle).
    
    """
    def __init__(self):
        self.labels = []
        self.conditions = []
        with open(abspath('pg/data/templates.json'), encoding='utf-8') as src:
            data = load(src)
        if data:
            for label, v in data.items():
                if not v:
                    continue
                self[label] = TemplateDict(v.get('categories', []), v.get('tabs'))
                self.labels.append(label)
                if not 'configuration' in v:
                    v['configuration'] = {}
                v['configuration']['tpl_label'] = label
                # le label utilisé comme clé prévaut sur celui qui aurait pu être
                # renseigné dans la configuration du modèle
                self.conditions.append(v['configuration'])

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

