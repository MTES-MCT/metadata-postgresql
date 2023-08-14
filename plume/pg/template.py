"""Import et préparation des modèles de formulaire.

"""

import re
from json import load, loads, dump
from pathlib import Path

from plume.rdf.rdflib import URIRef, from_n3
from plume.rdf.utils import (
    path_from_n3, forbidden_char, abspath, data_from_file
)
from plume.rdf.namespaces import RDFS, SH, PlumeNamespaceManager
from plume.pg.queries import (
    query_insert_or_update_meta_categorie,
    query_insert_or_update_any_table,
    query_insert_or_update_meta_template_categories,
    query_delete_any_table,
    query_read_any_row
)

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

def dump_template_data(
    filepath, templates=None, categories=None, tabs=None,
    template_categories=None, tpl_id=None
    ):
    """Encode en JSON dans un fichier des données de définition des modèles.

    Cette fonction permet d'exporter en JSON les données des
    modèles stockées en base, éventuellement restreintes à un ou 
    plusieurs modèles spécifiés en argument.

    Parameters
    ----------
    filepath : str or pathlib.Path
        Chemin absolu du fichier cible.
    templates : list(tuple(dict))) or list(dict), optional
        Le contenu de la table des modèles (au moins les enregistrements
        correspondant au(x) modèle(s) à exporter, le cas échéant).
        Il peut s'agir du résultat brut renvoyé par la requête générée par 
        :py:func:`plume.pg.queries.query_read_meta_template`, ou plus
        généralement d'une liste de dictionnaires dont les clés sont
        les noms des champs de la table et les valeurs sont les valeurs
        prises par ces champs.
    categories : list(tuple(dict))) or list(dict), optional
        Le contenu de la table des catégories (au moins les enregistrements
        correspondant aux catégories utilisées par le(s) modèle(s) à
        exporter, le cas échéant).
        Il peut s'agir du résultat brut renvoyé par la requête générée par 
        :py:func:`plume.pg.queries.query_read_meta_categorie`, ou plus
        généralement d'une liste de dictionnaires dont les clés sont
        les noms des champs de la table et les valeurs sont les valeurs
        prises par ces champs.
    tabs : list(tuple(dict))) or list(dict), optional
        Le contenu de la table des onglets (au moins les enregistrements
        correspondant aux onglets utilisés par le(s) modèle(s) à
        exporter, le cas échéant).
        Il peut s'agir du résultat brut renvoyé par la requête générée par 
        :py:func:`plume.pg.queries.query_read_meta_tab`, ou plus
        généralement d'une liste de dictionnaires dont les clés sont
        les noms des champs de la table et les valeurs sont les valeurs
        prises par ces champs.
    template_categories : list(tuple(dict))) or list(dict), optional
        Le contenu de la table d'association des catégories aux modèles
        (au moins les enregistrements correspondant aux catégories utilisées
        par le(s) modèle(s) à exporter, le cas échéant).).
        Il peut s'agir du résultat brut renvoyé par la requête générée par 
        :py:func:`plume.pg.queries.query_read_meta_template_categories`,
        ou plus généralement d'une liste de dictionnaires dont les clés sont
        les noms des champs de la table et les valeurs sont les valeurs
        prises par ces champs.
    tpl_id : int or list(int), optional
        L'identifiant unique du modèle de formulaire à exporter, ou une
        liste d'identifiants. Si cet argument n'est pas fourni, toutes les
        données seront incluses.
        
    """
    pfile = Path(filepath)
    data = {}
    category_paths = []
    tab_ids = []

    if isinstance(tpl_id, int):
        tpl_id = [tpl_id]
    
    if templates:
        if isinstance(templates[0], tuple):
            templates = [elem for elem, in templates]
        if tpl_id:
            for template in templates.copy():
                if not template['tpl_id'] in tpl_id:
                    templates.remove(template)
        if templates:
            data['templates'] = templates

    if template_categories:
        if isinstance(template_categories[0], tuple):
            template_categories = [elem for elem, in template_categories]
        if tpl_id:
            for template_category in template_categories.copy():
                if not template_category['tpl_id'] in tpl_id:
                    template_categories.remove(template_category)
                else:
                    path = template_category['shrcat_path'] or template_category['loccat_path']
                    if path and not path in category_paths:
                        category_paths.append(path)
                    tab_id = template_category['tab_id']
                    if tab_id and not tab_id in tab_ids:
                        tab_ids.append(tab_id)
        if template_categories:
            data['template_categories'] = template_categories

    if categories:
        if isinstance(categories[0], tuple):
            categories = [elem for elem, in categories]
        if tpl_id: 
            for category in categories.copy():
                if not category['path'] in category_paths:
                    categories.remove(category)
        if categories:
            data['categories'] = categories
    
    if tabs:
        if isinstance(tabs[0], tuple):
            tabs = [elem for elem, in tabs]
        if tpl_id: 
            for tab in tabs.copy():
                if not tab['tab_id'] in tab_ids:
                    tabs.remove(tab)
        if tabs:
            data['tabs'] = tabs
    
    with open(pfile, 'w', encoding='utf-8') as dest:
        dump(data, dest, ensure_ascii=False, indent=4)

class TemplateQueryBuilder:
    """Constructeur des requêtes qui permettent l'import des modèles en base.
    
    La principal difficulté lors de l'import d'un modèle est le fait que
    les valeurs des clés primaires numériques des tables des modèles
    et des onglets, qui servent également de clés étrangères dans la table
    d'association des catégories aux modèles, ne sont a priori pas les mêmes
    dans la base d'origine du modèle et dans la base cible.

    La classe :py:class:`TemplateQueryBuilder` propose un processus d'intégration
    progressive des modèles qui répond à ce problème. Les enregistrements
    des différentes tables sont ajoutés ou mis à jour un par un, ce qui permet
    d'assurer la correspondance entre les anciennes et nouvelles clés.

    Le générateur :py:meth:`TemplateQueryBuilder.queries` fournit les
    requêtes, à exécuter au fur et à mesure. Après l'exécution de chaque requête,
    si et seulement si l'attribut :py:attr:`TemplateQueryBuilder.waiting` vaut
    ``True``, le résultat doit être ré-intégré avec la méthode 
    :py:meth:`TemplateQueryBuilder.feedback`:

        >>> builder = TemplateQueryBuilder(filepath)
        >>> conn = psycopg2.connect(connection_string)
        >>> with conn:
        ...     with conn.cursor() as cur:
        ...         for query in builder.queries():
        ...              cur.execute(*query)
        ...              if builder.waiting:
        ...                  result = cur.fetchone()
        ...                  builder.feedback(result)
        >>> conn.close()
    
    Le fichier source est un dictionnaire encodé en JSON, comptant au plus
    de quatre clés : ``templates``, ``categories``, ``tabs``, ``template_categories``.
    Chaque clé prend en valeur une liste de dictionnaires dont les clés sont les
    noms des champs des tables ``meta_template``, ``meta_categorie``, ``meta_tab``
    et ``meta_template_categories``.

    À noter que:

    * Les modèles et onglets sont reconnus par leur nom. Si un modèle/onglet de
      même nom qu'un modèle/onglet défini dans le fichier source existe dans
      la base cible, il sera mis à jour, sinon un nouveau modèle/onglet est ajouté.
    * Le processus échouera si les associations modèle-catégorie font référence
      à des modèles ou onglets non définies dans le fichier source, ou à des
      catégories qui ne sont définies ni en base ni dans le fichier source.
    * Il n'est pas possible d'utiliser cette méthode pour ajouter des catégories
      communes qui ne seraient pas présentes en base. Celles-ci seront ignorées si
      elles n'étaient pas utilisées pour des associations modèle-catégorie, et 
      une erreur se produira dans le cas contraire.
    * Si le fichier source contient des enregistrements de la table des modèles,
      toutes les associations modèle-catégorie correspondantes seront supprimées
      avant import des associations modèle-catégories du fichier source. La
      suppression peut être évitée en modifiant la valeur du paramètre `preserve`.

    Parameters
    ----------
    filepath : str or pathlib.Path
        Chemin absolu du fichier source. Le contenu du fichier est récupéré
        à l'initialisation, et stocké dans les attributs de la classe.
    no_update : bool, default False
        Si ``True``, les données des catégories et onglets ne sont
        pas mises à jour lorsque les enregistrements existent déjà en
        base (les enregistrements manquants sont créés dans tous les cas).
    preserve : bool, default False
        Si ``True``, les associations modèle-catégorie des modèles ne sont
        pas supprimées avant recréation. Les associations qui ne sont pas
        présentes dans le fichier source seront donc préservées.
    
    Attributes
    ----------
    templates : list(dict)
        Données décrivant des modèles, équivalant à des enregistrements
        de la table ``meta_template``.
    categories : list(dict)
        Données décrivant des catégories de métadonnées, équivalant à des
        enregistrements de la table ``meta_categorie``.
    tabs : list(dict)
        Données décrivant des onglets, équivalant à des enregistrements de
        la table ``meta_tab``.
    template_categories : list(dict)
        Données décrivant l'association d'une catégorie à un modèle, 
        équivalant à des enregistrements de la table ``meta_template_categories``.
    map_tpl_id : dict
        Correspondance entre les identifiants numériques des modèles dans les
        données sources et leurs équivalents dans la base de données cible.
        Ce dictionnaire est complété au fur et à mesure de l'exécution et
        la ré-intégration du résultat des requêtes.
    map_tab_id : dict
        Correspondance entre les identifiants numériques des onglets dans les
        données sources et leurs équivalents dans la base de données cible.
        Ce dictionnaire est complété au fur et à mesure de l'exécution et
        la ré-intégration du résultat des requêtes.
    last_type : {None, 'templates', 'categories', 'tabs', 'template_categories'}
        Nature du dernier enregistrement créé ou mis à jour en base.
        Cet attribut vaut ``None`` tant que le générateur :py:meth:`TemplateQueryBuilder.queries`
        n'a pas été lancé.
    last_id : int or None
        Identifiant numérique du dernier enregistrement créé ou mis à jour en base
        dans les données sources.
        Cet attribut vaut ``None`` tant que le générateur :py:meth:`TemplateQueryBuilder.queries`
        n'a pas été lancé, ou si le dernier enregistrement traité n'était pas un modèle
        ou un onglet.
    waiting : bool
        ``True`` si le résultat de la requête courante doit être ré-intégré
        grâce à la méthode :py:meth:`TemplateQueryBuilder.feedback`, `False`
        sinon. Cet attribut vaut également `False` pour les requêtes qui n'ont
        pas de résultat, telles les commandes de suppression, il est donc important
        de tester sa valeur avant de tenter de récupérer le résultat de la
        requête.
        
    """

    def __init__(self, filepath, no_update=False, preserve=False):

        data = data_from_file(filepath)
        data_dict = loads(data)

        self.templates = data_dict.get('templates', [])
        self.categories = data_dict.get('categories', [])
        self.tabs = data_dict.get('tabs', [])
        self.template_categories = data_dict.get('template_categories', [])

        self.map_tpl_id = {}
        self.map_tab_id = {}
        self.last_type = None
        self.last_id = None
        self.waiting = False
        self._retry_query = None
        self._retry_queries = []

        self._preserve = bool(preserve)
        self._no_update = bool(no_update)

    def feedback(self, result):
        """À utiliser pour fournir au générateur les résultats de ses requêtes.

        Concrètement, cette méthode construit des
        dictionnaires de mapping, qui permettent
        ensuite au générateur de remplacer les anciens
        identifiants numériques de modèles (ceux de la base sur
        laquelle a été réalisé l'export) et d'onglets par
        les nouveaux (ceux de la base sur laquelle est réalisé
        l'import).

        Parameters
        ----------
        result : list(tuple(dict)) or tuple(dict) or dict
            Le résultat de la dernière requête produite
            par le générateur :py:meth:`TemplateQueryBuilder.queries`.

        """
        if not self.waiting:
            return
        
        if not result:
            if self._retry_query:
                self._retry_queries.append(self._retry_query)
                self._retry_query = None
                return
                # avec l'option no_update, les requêtes
                # INSERT ... ON CONFLICT DO NOTHING
                # ne renvoient rien sur les enregistrements
                # pré-existants, ce qui ne permet donc pas de
                # récupérer les nouvelles valeurs des clés
                # primaires numériques. Dans ce cas, feedback
                # mémorise la requête query_read_any_row
                # qui permettra d'obtenir cette information
                # avant de passer à la suite.
            raise ValueError('"result" ne peut être vide')
        self._retry_query = None

        if isinstance(result, list):
            result = result[0]
        if isinstance(result, tuple):
            result = result[0]
        if not isinstance(result, dict):
            raise TypeError('"result" devrait contenir un dictionnaire')
        if self.last_type == 'tabs':
            self.map_tab_id[self.last_id] = result['tab_id']
        if self.last_type == 'templates':
            self.map_tpl_id[self.last_id] = result['tpl_id']
    
    def queries(self):
        """Générateur de requêtes.

        Yields
        ------
        PgQueryWithArgs
            Une requête prête à être envoyée au serveur PostgreSQL.
        
        """
        # modèles
        tpl_ids = []
        for data in self.templates:
            if data.get('tpl_id'):
                self.waiting = True
                self.last_type = 'templates'
                self.last_id = data['tpl_id']
                tpl_ids.append(data['tpl_id'])
                del data['tpl_id']
            yield query_insert_or_update_any_table(
                'z_plume', 'meta_template', 'tpl_label', data
            )
        
        # onglets
        for data in self.tabs:
            if data.get('tab_id'):
                self.waiting = True
                self.last_type = 'tabs'
                self.last_id = data['tab_id']
                if self._no_update:
                    self._retry_query = (
                        query_read_any_row(
                            'z_plume', 'meta_tab', 'tab_label', data
                        ),
                        'tabs',
                        data['tab_id']
                    )
                del data['tab_id']
            yield query_insert_or_update_any_table(
                'z_plume', 'meta_tab', 'tab_label', data,
                no_update=self._no_update
            )
        for query, last_type, last_id in self._retry_queries:
            self.last_type = last_type
            self.last_id = last_id
            yield query
            # cf. méthode feedboack - récupération des
            # identifiants numériques qui n'ont pas pu l'être
            # car leurs enregistrements (pré-existants) n'ont
            # pas été modifiés à cause de l'option no_update

        # catégories de métadonnées
        for data in self.categories:
            self.waiting = False
            self.last_type = 'categories'
            self.last_id = None
            yield query_insert_or_update_meta_categorie(
                data, no_update=self._no_update
            )
        
        # associations modèle-catégorie
        if not self._preserve:
            for tpl_id in tpl_ids:
                # pour tous les modèles inclus dans les données,
                # les associations modèle-catégorie sont supprimées
                # puis re-crées, afin que de ne pas conserver d'enregistrements
                # obsolètes.
                self.waiting = False
                self.last_type = 'template_categories'
                self.last_id = None
                yield query_delete_any_table(
                    'z_plume', 'meta_template_categories', 'tpl_id', {'tpl_id': tpl_id}
                )
        for data in self.template_categories:
            self.waiting = False
            self.last_type = 'template_categories'
            self.last_id = None
            if not data.get('tpl_id'):
                raise ValueError(
                    "Identifiant de modèle (tpl_id) manquant pour l'association "
                    f'modèle-catégorie "{data}"'
                )
            if not data['tpl_id'] in self.map_tpl_id:
                raise ValueError(
                        f"Le modèle {data['tpl_id']} n'est pas défini dans les données source"
                    )
            data['tpl_id'] = self.map_tpl_id[data['tpl_id']]
            if data.get('tab_id'):
                if data['tab_id'] in self.map_tab_id:
                    data['tab_id'] = self.map_tab_id[data['tab_id']]
                else:
                    raise ValueError(
                        f"L'onglet {data['tab_id']} n'est pas défini dans les données source"
                    )
            if 'tplcat_id' in data:
                del data['tplcat_id']
            yield query_insert_or_update_meta_template_categories(data)
        

