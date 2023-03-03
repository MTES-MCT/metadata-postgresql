"""Requêtes prêtes à être envoyées au serveur PostgreSQL.

Ce module suppose l'usage de la bibliothèque Psycopg pour la
communication avec le serveur PostgreSQL.

Il génère des requêtes à exécuter avec la méthode
:py:meth:`psycopg2.cursor.execute`. Ces requêtes - objets
:py:class:`PgQueryWithArgs` - sont auto-suffisantes, dans le sens
où elles incluent tous les paramètres nécessaires.

La syntaxe pour l'usage de ces requêtes est toujours :

    >>> cur.execute(*query)

References
----------
https://www.psycopg.org

"""

import re
from psycopg2 import sql
from psycopg2.extras import Json

from plume.rdf.exceptions import UnknownParameterValue, MissingParameter
from plume.rdf.namespaces import PLUME
from plume.config import PLUME_PG_MIN_VERSION, PLUME_PG_MAX_VERSION


class PgQueryWithArgs(tuple):
    """Requête PostgreSQL prête à l'emploi.

    Prend la forme d'un tuple à un ou deux éléments. Le premier
    élément est la requête SQL, soit un objet de classe
    :py:class:`psycopg2.sql.Composed` ou :py:class:`psycopg2.sql.SQL`.
    Le second élément correspond aux paramètres de la requête, et
    peut prendre la forme d'un tuple ou d'un dictionnaire selon les
    cas. Il n'est présent que si la requête admet des paramètres.

    D'une manière générale, il n'est pas utile de contrôler la présence
    du second élément. Une requête ``query`` peut toujours être passée
    en argument de :py:meth:`psycopg2.cursor.execute` de la manière
    suivante :

        >>> cur.execute(*query)

    Attributes
    ----------
    query : psycopg2.sql.SQL or psycopg2.sql.Composed
        La requête à proprement parler.
    args : tuple or dict or None
        Les paramètres de la requête. Il s'agira d'un tuple vide
        si la requête ne prend pas de paramètre.
    expecting : {'some rows', 'one row', 'one value', 'nothing'}
        Décrit le résultat attendu, le cas échéant.
    allow_none : bool
        ``True`` s'il est admis que la requête ne renvoie aucun
        enregistrement. Si ``False``, une erreur devra être émise
        en l'absence de résultat.
    missing_mssg : str or None
        Le message d'erreur à présenter lorsque la requête ne renvoie
        pas de résultat. Vaut toujours ``None`` lorsque `allow_none`
        vaut ``True``.
    
    Parameters
    ----------
    query : psycopg2.sql.SQL or psycopg2.sql.Composed
        La requête.
    args : tuple or dict, optional
        Les paramètres de la requête.
    expecting : {'some rows', 'one row', 'one value', 'nothing'}, optional
        Décrit le résultat attendu, le cas échéant.
    allow_none : bool, default True
        ``True`` s'il est admis que la requête ne renvoie aucun
        enregistrement. Si ``False``, une erreur devra être émise
        en l'absence de résultat.
    missing_mssg : str, optional
        Le message d'erreur à présenter lorsque la requête ne renvoie
        pas de résultat. Ce paramètre est ignoré lorsque `allow_none`
        vaut ``True``.

    """

    def __new__(cls, query, args=None, **kwargs):
        if args:
            return super().__new__(cls, (query, args))
        else:
            return super().__new__(cls, (query,))

    def __init__(self, query, args=None, expecting=None,
        allow_none=True, missing_mssg=None):
        self.expecting = expecting or 'some rows'
        self.allow_none = bool(allow_none)
        self.missing_mssg = None if self.allow_none else missing_mssg or ''


def query_is_relation_owner(schema_name, table_name):
    """Requête qui vérifie que le rôle courant est membre du propriétaire d'une relation (table, etc.).
    
    À utiliser comme suit :
    
        >>> query = query_is_relation_owner('nom du schéma', 'nom de la relation')
        >>> cur.execute(*query)
        >>> res = cur.fetchone()
        >>> is_owner = res[0] if res else False
    
    Parameters
    ----------
    schema_name : str
        Nom du schéma.
    table_name : str
        Nom de la relation (table, vue...).

    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL.
    
    """
    query = sql.SQL("""
        SELECT pg_has_role(relowner, 'USAGE')
            FROM pg_catalog.pg_class
            WHERE relnamespace = quote_ident(%s)::regnamespace
                AND relname = %s
        """)
    return PgQueryWithArgs(
        query=query,
        args=(schema_name, table_name),
        expecting='one value',
        allow_none=False,
        missing_mssg="Plume n'a pas pu confirmer si le rôle de" \
            ' connexion courant est habilité à modifier le descriptif' \
            ' de la table ou vue "{}"."{}". Elle a vraisemblablement' \
            ' été supprimée entre temps.'.format(schema_name, table_name)
        )

def query_exists_extension(extension):
    """Requête qui vérifie qu'une extension est installée sur la base PostgreSQL cible.
    
    À utiliser comme suit :
    
        >>> query = query_exists_extension('nom de l'extension')
        >>> cur.execute(*query)
        >>> extension_exists = cur.fetchone()[0]
    
    Le résultat est :
    
    * ``True`` si l'extension est installée ;
    * ``False`` si elle est disponible dans le répertoire des
      extensions du serveur mais non installée ;
    * ``None`` si elle n'est pas disponible sur le serveur.
    
    Parameters
    ----------
    extension : str
        Nom de l'extension.

    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL.
    
    """
    query = sql.SQL("""
        SELECT (SELECT installed_version IS NOT NULL
            FROM pg_available_extensions
            WHERE name = %s)
        """)
    return PgQueryWithArgs(
        query=query,
        args=(extension,),
        expecting='one value',
        allow_none=False, # n'arrivera jamais
        missing_mssg="Plume n'a pas pu confirmer si l'extension'" \
            ' "{}" est installée sur la base.'.format(extension)
        )

def query_plume_pg_check(min_version=PLUME_PG_MIN_VERSION,
    max_version=PLUME_PG_MAX_VERSION):
    """Requête qui vérifie qu'une version compatible de PlumePg est installée sur la base cible.
    
    Elle s'assure aussi que l'utilisateur dispose des
    privilèges nécessaires sur les objets de PlumePg.
    
    À utiliser comme suit :
    
        >>> query = query_plume_pg_check(min_version='0.1.0')
        >>> cur.execute(*query)
        >>> result = cur.fetchone()
    
    ``result`` est un tuple constitué des éléments suivants :
    
    * ``[0]`` est un booléen. S'il vaut ``True``, tout est en ordre
      pour l'utilisation des modèles de PlumePg. Sinon, les autres
      éléments du tuple précisent le problème.
    * ``[1]`` est une liste rappelant la version minimale (incluse)
      et la version maximale (exclue) de PlumePg compatibles avec la
      version courante de Plume.
    * ``[2]`` est la version installée de PlumePg, ou ``None``
      si l'extension n'est pas installée sur la base courante.
    * ``[3]`` est la version de référence de PlumePg disponible
      sur le serveur, ou ``None`` si l'extension n'est pas
      disponible sur le serveur.
    * ``[4]`` est une liste de schémas sur lesquels l'utilisateur
      ne dispose pas du privilège ``USAGE`` requis.
    * ``[5]`` est une liste de tables et vues sur lesquelles
      l'utilisateur ne dispose pas du privilège ``SELECT`` requis.
      À noter que les droits sur les tables et vues ne sont 
      contrôlés que si l'utilisateur dispose de tous les privilèges
      nécessaires sur les schémas.
    
    Parameters
    ----------
    min_version : str, optional
        La version minimale de PlumePg compatible
        avec la version courante de Plume (incluse).
        Elle doit être de la forme ``'x.y.z'`` où
        ``x``, ``y`` et ``z`` sont des entiers.
        Par défaut, il s'agira de :py:const:`PLUME_PG_MIN_VERSION`.
        Il est possible d'indiquer ``None`` lorsqu'il
        n'y a pas de contrainte sur la version minimale.        
    max_version : str, optional
        La version maximale de PlumePg compatible
        avec la version courante de Plume (exclue).
        Elle doit être de la forme ``'x.y.z'`` où
        ``x``, ``y`` et ``z`` sont des entiers.
        Par défaut, il s'agira de :py:const:`PLUME_PG_MAX_VERSION`.
        Il est possible d'indiquer ``None``, la version
        maximale sera alors déduite du premier
        chiffre de la borne inférieure. Par exemple,
        ``'4.0.0'`` serait la borne supérieure pour la
        version de référence ``'3.1.1'``.
    
    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL
        et son tuple de paramètres.
    
    """
    if min_version:
        if not re.match(r'^\d+[.]\d+[.]\d+$', min_version):
            raise ValueError('La forme de la version' \
                " minimum '{}' est incorrecte.".format(min_version))
        l_min = [int(x) for x in min_version.split('.')]
    else:
        l_min = [0, 0, 0]
    
    if max_version:
        if not re.match(r'^\d+[.]\d+[.]\d+$', max_version):
            raise ValueError('La forme de la version' \
                " maximum '{}' est incorrecte.".format(max_version))
        l_max = [int(x) for x in max_version.split('.')]
    elif min_version:
        l_max = [l_min[0] + 1, 0, 0]
        max_version = '.'.join(str(x) for x in l_max)
    else:
        l_max = [9999, 0, 0]
        
    return PgQueryWithArgs(
        query=sql.SQL("""
            WITH ref_versions AS (
            SELECT
                %(min_version)s::text AS min_version,
                %(max_version)s::text AS max_version
            ),
            check_plumepg AS (
            SELECT
                regexp_split_to_array(installed_version, '[.]')::int[] >= %(l_min)s::int[]
                    AND regexp_split_to_array(installed_version, '[.]')::int[] < %(l_max)s::int[]
                    AS plumepg_ok,
                installed_version,
                default_version
                FROM pg_available_extensions WHERE name = 'plume_pg'
            ),
            check_schema AS (
            SELECT
                n_schema,
                CASE WHEN plumepg_ok
                    THEN has_schema_privilege(n_schema, 'USAGE') END
                    AS schema_ok
                FROM check_plumepg, unnest(ARRAY['z_plume'])
                    AS p_schemas (n_schema)
            ),
            check_relation AS (
            SELECT
                n_table,
                CASE WHEN plumepg_ok and (SELECT bool_and(schema_ok) FROM check_schema)
                    THEN has_table_privilege(n_table, 'SELECT') END
                    AS table_ok
                FROM check_plumepg, unnest(ARRAY['z_plume.meta_template',
                    'z_plume.meta_categorie', 'z_plume.meta_tab',
                    'z_plume.meta_template_categories',
                    'z_plume.meta_template_categories_full'])
                    AS p_tables (n_table)
            )
            SELECT
                coalesce(plumepg_ok AND bool_and(schema_ok) AND bool_and(table_ok), False),
                ARRAY[min_version, max_version],
                installed_version,
                default_version,
                coalesce(array_agg(DISTINCT n_schema ORDER BY n_schema)
                    FILTER (WHERE NOT schema_ok), ARRAY[]::text[]),
                coalesce(array_agg(DISTINCT n_table ORDER BY n_table)
                    FILTER (WHERE NOT table_ok), ARRAY[]::text[])
                FROM ref_versions LEFT JOIN check_plumepg ON True
                    LEFT JOIN check_relation ON True
                    LEFT JOIN check_schema ON True
                GROUP BY min_version, max_version, plumepg_ok, installed_version, default_version
            """),
        args={'min_version': min_version, 'l_min': l_min,
            'max_version': max_version, 'l_max': l_max},
        expecting='one row',
        allow_none=False,
        missing_mssg="Plume n'a pas pu confirmer si l'extension PlumePg " \
            'est disponible sur la base cible dans une version compatible.'
        )

def query_get_relation_kind(schema_name, table_name):
    """Requête qui récupère le type d'une relation PostgreSQL.
    
    À utiliser comme suit :
    
        >>> query = query_get_relation_kind('nom du schéma',
        ...     'nom de la relation')
        >>> cur.execute(*query)
        >>> relkind = cur.fetchone()[0]
    
    Parameters
    ----------
    schema_name : str
        Nom du schéma.
    table_name : str
        Nom de la relation (table, vue...).
    
    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL.
    
    """
    return PgQueryWithArgs(
        query=sql.SQL("""
            SELECT relkind FROM pg_catalog.pg_class
                WHERE pg_class.oid = '{}'::regclass
            """).format(
                sql.Identifier(schema_name, table_name)
                ),
        expecting='one value',
        allow_none=False, # impossible
        missing_mssg="Plume n'a pas pu déterminer la nature de la relation" \
            ' "{}"."{}".'.format(schema_name, table_name)
        )

def query_update_table_comment(schema_name, table_name, relation_kind='r',
    description=''):
    """Requête de mise à jour du descriptif d'une table ou vue.
    
    À utiliser comme suit :
    
        >>> query = query_update_table_comment('nom du schéma',
        ...     'nom de la relation', 'type de relation',
        ...     'Nouveau descriptif')
        >>> cur.execute(*query)
    
    Parameters
    ----------
    schema_name : str
        Nom du schéma.
    table_name : str
        Nom de la relation (table, vue...).
    relation_kind : {'r', 'v', 'm', 'f', 'p'}, optional
        Le type de relation. ``'r'`` par défaut, ce qui
        correspond à une table simple.
    description : str, optional
        Le nouveau descriptif.
    
    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL.

    Raises
    ------
    UnknownParameterValue
        Si le type de relation n'est pas l'une des
        valeurs autorisées.

    """
    d = { 'r': 'TABLE', 'v': 'VIEW', 'm': 'MATERIALIZED VIEW',
        'f': 'FOREIGN TABLE', 'p': 'TABLE' }
    
    if not relation_kind in d:
        raise UnknownParameterValue('relation_kind', relation_kind)
    
    return PgQueryWithArgs(
        query=sql.SQL(
            "COMMENT ON {} {} IS %s"
            ).format(
                sql.SQL(d[relation_kind]),
                sql.Identifier(schema_name, table_name)
                ),
        args=(description,),
        expecting='nothing'
        )

def query_get_table_comment(schema_name, table_name):
    """Requête de récupération du descriptif d'une table ou vue.
    
    À utiliser comme suit :
    
        >>> query = query_get_table_comment('nom du schéma',
        ...     'nom de la relation')
        >>> cur.execute(*query)
        >>> old_description = cur.fetchone()[0]
    
    Parameters
    ----------
    schema_name : str
        Nom du schéma.
    table_name : str
        Nom de la relation (table, vue...).
    
    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL.
    
    """
    return PgQueryWithArgs(
        query=sql.SQL(
            "SELECT obj_description('{}'::regclass, 'pg_class')"
            ).format(
                sql.Identifier(schema_name, table_name)
                ),
        expecting='one value',
        allow_none=False, # impossible
        missing_mssg="Plume n'a pas pu importer le desriptif de la relation" \
            ' "{}"."{}".'.format(schema_name, table_name)
        )

def query_list_templates(schema_name, table_name):
    """Requête d'import de la liste des modèles disponibles.
    
    À utiliser comme suit :
    
        >>> query = query_list_templates('nom du schéma', 'nom de la relation')
        >>> cur.execute(*query)
        >>> templates = cur.fetchall()
    
    Parameters
    ----------
    schema_name : str
        Nom du schéma.
    table_name : str
        Nom de la relation (table, vue...).

    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL.
    
    Notes
    -----
    La requête interroge la table ``z_plume.meta_template``
    créée par l'extension PlumePg. Au lieu d'importer 
    tel quel le contenu de son champ ``sql_filter``,
    elle l'exécute et renvoie un booléen indiquant si la
    condition qu'il spécifie est remplie.
    
    """
    return PgQueryWithArgs(
        query=sql.SQL("""
            SELECT
                tpl_label,
                z_plume.meta_execute_sql_filter(sql_filter, %s, %s) AS check_sql_filter,
                md_conditions,
                priority
                FROM z_plume.meta_template
                WHERE enabled
                ORDER BY tpl_label
            """),
        args=(schema_name, table_name),
        expecting='some rows',
        allow_none=True
        )

def query_evaluate_local_templates(templates_collection, schema_name, table_name):
    """Requête qui évalue côté serveur les conditions d'application des modèles locaux.
    
    À utiliser comme suit :
    
        >>> query = query_evaluate_local_templates()
        >>> cur.execute(*query)
        >>> templates = cur.fetchall()
    
    Parameters
    ----------
    templates_collection : plume.pg.template.LocalTemplatesCollection
        Le répertoire des modèles stockés localement,
        qui aura été instancié parce que PlumePg
        n'est pas activée sur la base de la table
        dont on affiche les métadonnées.
    schema_name : str
        Nom du schéma.
    table_name : str
        Nom de la relation (table, vue...).
    
    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL, incluant
        son dictionnaire de paramètres.
    
    Notes
    -----
    La forme du résultat des requêtes créées avec cette fonction est
    identique à celle de :py:func:`query_list_templates`, ce qui 
    permet ensuite d'appliquer dans les deux cas la fonction
    :py:func:`plume.pg.template.search_template` pour obtenir le
    nom du modèle à appliquer.
    
    """
    return PgQueryWithArgs(
        query=sql.SQL('''
            WITH meta_template (tpl_label, check_sql_filter, md_conditions, priority, comment) AS (VALUES {})
            SELECT
                tpl_label,
                check_sql_filter,
                md_conditions::jsonb,
                priority
                FROM meta_template
                ORDER BY tpl_label
            ''').format(
                sql.SQL(', ').join(
                    sql.SQL('({})').format(sql.SQL(', ').join((
                        sql.Literal(tpl_label),
                        sql.SQL(sql_filter.replace('$1', '%(schema_name)s').replace('$2', '%(table_name)s')) if sql_filter else sql.Literal(None),
                        sql.Literal(Json(md_conditions)),
                        sql.Literal(priority),
                        sql.Literal(comment)
                        ))) for tpl_label, sql_filter, md_conditions, priority, comment in templates_collection.conditions
                    )),
        args={'schema_name': schema_name, 'table_name' : table_name},
        expecting='some rows',
        allow_none=True
        )  

def query_get_categories(tpl_label):
    """Requête d'import des catégories à afficher dans un modèle donné.
    
    À utiliser comme suit :
    
        >>> query = query_get_categories('nom du modèle')
        >>> cur.execute(*query)
        >>> categories = cur.fetchall()
    
    Parameters
    ----------
    tpl_label : str
        Nom du modèle choisi.

    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL.
    
    Notes
    -----
    La requête interroge la vue ``z_plume.meta_template_categories_full``
    créée par l'extension PlumePg. Elle ne doit donc être exécutée qu'après
    contrôle de l'existence de l'extension.
    
    """
    return PgQueryWithArgs(
        query=sql.SQL("""
            SELECT 
                path,
                origin,
                label,
                description,
                special::text,
                is_node,
                datatype::text,
                is_long_text,
                rowspan,
                placeholder,
                input_mask,
                is_multiple,
                unilang,
                is_mandatory,
                sources,
                geo_tools::text[],
                compute::text[],
                template_order,
                is_read_only,
                tab,
                compute_params
                FROM z_plume.meta_template_categories_full
                WHERE tpl_label = %s
            """),
        args=(tpl_label,),
        expecting='some rows',
        allow_none=True
        )

def query_template_tabs(tpl_label):
    """Requête d'import des onglets utilisés par un modèle.
    
    À utiliser comme suit :
    
        >>> query = query_template_tabs('nom du modèle')
        >>> cur.execute(*query)
        >>> tabs = cur.fetchall()
    
    Parameters
    ----------
    tpl_label : str
        Nom du modèle choisi.

    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL.
    
    Notes
    -----
    La requête interroge les tables ``z_plume.meta_tab`` et
    ``z_plume.meta_template_categories`` créées par l'extension
    PlumePg. Elle ne doit donc être exécutée qu'après
    contrôle de l'existence de l'extension.
    
    L'ordre de la liste résultant de l'exécution de la requête
    est l'ordre dans lequel le modèle prévoit que les onglets
    soient présentés à l'utilisateur.

    """
    return PgQueryWithArgs(
        query=sql.SQL("""
            SELECT
                meta_tab.tab
                FROM z_plume.meta_tab
                    LEFT JOIN z_plume.meta_template_categories
                        ON meta_tab.tab = meta_template_categories.tab
                WHERE meta_template_categories.tpl_label = %s
                GROUP BY meta_tab.tab, meta_tab.tab_num
                ORDER BY meta_tab.tab_num NULLS LAST, meta_tab.tab
            """),
        args=(tpl_label,),
        expecting='some rows',
        allow_none=True
        )

def query_get_columns(schema_name, table_name):
    """Requête de récupération des descriptifs des champs d'une table ou vue.
    
    À utiliser comme suit :
    
        >>> query = query_get_columns('nom du schéma',
        ...     'nom de la relation')
        >>> cur.execute(*query)
        >>> columns = cur.fetchall()
    
    Parameters
    ----------
    schema_name : str
        Nom du schéma.
    table_name : str
        Nom de la relation (table, vue...).
    
    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL.

    """
    return PgQueryWithArgs(
        query=sql.SQL(
            """
            SELECT
                attname,
                col_description('{attrelid}'::regclass, attnum)
                FROM pg_catalog.pg_attribute
                WHERE attrelid = '{attrelid}'::regclass AND attnum >= 1
                    AND NOT attisdropped
                ORDER BY attnum
            """
            ).format(
                attrelid=sql.Identifier(schema_name, table_name)
                ),
        expecting='some rows',
        allow_none=True
    )

def query_update_column_comment(schema_name, table_name, column_name, description=''):
    """Requête de mise à jour du descriptif d'un champ.
    
    À utiliser comme suit :
    
        >>> query = query_update_column_comment('nom du schéma',
        ...     'nom de la relation', 'nom du champ',
        ...     'Nouveau descriptif du champ')
        >>> cur.execute(*query)
    
    Parameters
    ----------
    schema_name : str
        Nom du schéma.
    table_name : str
        Nom de la relation (table, vue...).
    column_name : str
        Nom du champ.
    description : str, optional
        Le nouveau descriptif du champ.
    
    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL.
    
    """
    return PgQueryWithArgs(
        query=sql.SQL(
        "COMMENT ON COLUMN {} IS %s"
        ).format(
            sql.Identifier(schema_name, table_name, column_name)
            ),
        args=(description,),
        expecting='nothing'
        )

def query_update_columns_comments(schema_name, table_name, widgetsdict):
    """Requête de mise à jour des descriptifs des champs d'une table.
    
    À utiliser comme suit :
    
        >>> query = query_update_columns_comments('nom du schéma',
        ...     'nom de la relation', widgetsdict)
        >>> if query:
        ...     cur.execute(*query)
    
    Parameters
    ----------
    schema_name : str
        Nom du schéma.
    table_name : str
        Nom de la relation (table, vue...).
    widgetsdict : plume.rdf.widgetsdict.WidgetsDict
        Le dictionnaire de widgets qui contient les descriptifs
        actualisés des champs.
    
    Returns
    -------
    PgQueryWithArgs or None
        Une requête prête à être envoyée au serveur PostgreSQL.
        La fonction renvoie ``None`` si elle ne trouve aucun descriptif
        de champ dans le dictionnaire de widgets.
    
    Notes
    -----    
    À noter que cette requête pourrait échouer si des champs ont été
    supprimés ou renommés entre temps.
    
    """
    updated_columns = []
    for k in widgetsdict:
        if k.path == PLUME.column:
            updated_columns.append((k.label, str(k.value or '')))   
    if updated_columns:
        return PgQueryWithArgs(
            query=sql.SQL(' ; ').join([
                sql.SQL(
                    "COMMENT ON COLUMN {} IS {}"
                    ).format(
                        sql.Identifier(schema_name, table_name, colname),
                        sql.Literal(coldescr)
                        )
                for colname, coldescr in updated_columns
                ]),
            expecting='nothing'
            )

def query_get_geom_srid(schema_name, table_name, geom_name):
    """Requête de récupération du référentiel de coordonnées d'une couche.
    
    À utiliser comme suit :
    
        >>> query = query_get_geom_srid('nom du schéma', 'nom de la relation'
        ...     'nom du champ de géométrie')
        >>> cur.execute(*query)
        >>> srid = cur.fetchone()[0]
    
    Le référentiel ainsi obtenu est de la forme ``'Autorité:Code'``.
    
    Parameters
    ----------
    schema_name : str
        Nom du schéma.
    table_name : str
        Nom de la relation (table, vue...).
    geom_name : str
        Nom du champ de géométrie à considérer.

    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL.
    
    Warnings
    --------
    Cette requête échouera si PostGIS n'est pas installé sur la
    base. Il est donc fortement recommandé de vérifier d'abord
    la présence de PostGIS avec :py:func:`query_exists_extension` :
    
        >>> query = query_exists_extension('postgis')
        >>> cur.execute(*query)
        >>> postgis_exists = cur.fetchone()[0]
    
    """
    return PgQueryWithArgs(
        query=sql.SQL("""
            SELECT
                auth_name || ':' || auth_srid
                FROM geometry_columns
                    LEFT JOIN spatial_ref_sys
                        ON geometry_columns.srid = spatial_ref_sys.srid
                WHERE f_table_schema = %s
                    AND f_table_name = %s
                    AND f_geometry_column = %s
                    AND auth_name ~ '^[A-Z]+$'
                    AND auth_srid IS NOT NULL
            """),
        args=(schema_name, table_name, geom_name),
        expecting='one value',
        allow_none=False,
        missing_mssg="Plume n'a pas pu déterminer le référentiel du " \
            'champ "{}" de la relation "{}"."{}".'.format(
            geom_name, schema_name, table_name)
        )

def query_get_srid_list(schema_name, table_name, **kwargs):
    """Requête de récupération de la liste des référentiels de coordonnées utilisés par les géométries d'une relation.
    
    À utiliser comme suit :
    
        >>> query = query_get_srid_list(schema_name='nom du schéma',
        ...     table_name='nom de la relation', **compute_params)
        >>> cur.execute(*query)
        >>> result = cur.fetchall()
    
    ``compute_params`` est le dictionnaire fourni par la clé
    `'compute parameters'` du dictionnaire interne associé à
    la clé courante du dictionnaire de widgets.
    
    La liste ainsi obtenue contient des tuples dont le premier
    élément est l'identifiant de l'autorité qui référence le
    référentiel et le second élément est le code du référentiel
    dans le registre de cette autorité.
    
    Parameters
    ----------
    schema_name : str
        Nom du schéma.
    table_name : str
        Nom de la relation (table, vue...).
    **kwargs : dict, optional
        Paramètres supplémentaires ignorés.
    
    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL, incluant
        son tuple de paramètres.
    
    Warnings
    --------
    Cette requête échouera si PostGIS n'est pas installé sur la
    base. Il est donc fortement recommandé de vérifier d'abord
    la présence de PostGIS avec :py:func:`query_exists_extension` :
    
        >>> query = query_exists_extension('postgis')
        >>> cur.execute(*query)
        >>> postgis_exists = cur.fetchone()[0]
    
    Notes
    -----
    Cette fonction est référencée par le module
    :py:mod:`plume.pg.computer`.
    
    """
    return PgQueryWithArgs(
        query=sql.SQL("""
            SELECT
                DISTINCT auth_name, auth_srid::text
                FROM geometry_columns
                    LEFT JOIN spatial_ref_sys
                        ON geometry_columns.srid = spatial_ref_sys.srid
                WHERE f_table_schema = %s
                    AND f_table_name = %s
                    AND auth_name ~ '^[A-Z]+$'
                    AND auth_srid IS NOT NULL
                ORDER BY auth_name, auth_srid
            """),
        args=(schema_name, table_name),
        expecting='some rows',
        allow_none=True)

def query_get_geom_extent(schema_name, table_name, geom_name):
    """Requête de calcul côté serveur du rectangle d'emprise d'une couche.
    
    À utiliser comme suit :
    
        >>> query = query_get_geom_extent('nom du schéma',
        ...     'nom de la relation', 'nom du champ de géométrie')
        >>> cur.execute(*query)
        >>> bbox_geom = cur.fetchone()[0]
    
    À noter que le résultat est une géométrie dont le
    système de coordonnées n'est pas explicité. Il faudra
    le récupérer via :py:func:`query_get_geom_srid`, puis
    appliquer la fonction :py:func:`plume.rdf.utils.wkt_with_srid`
    pour obtenir la représention du rectangle d'emprise
    attendue en RDF :
    
        >>> from plume.rdf.utils import wkt_with_srid
        >>> query = query_get_geom_srid('nom du schéma', 'nom de la relation'
        ...     'nom du champ de géométrie')
        >>> cur.execute(*query)
        >>> srid = cur.fetchone()[0]
        >>> bbox = wkt_with_srid(bbox_geom, srid)
    
    Parameters
    ----------
    schema_name : str
        Nom du schéma.
    table_name : str
        Nom de la relation (table, vue...).
    geom_name : str
        Nom du champ de géométrie.
    
    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL.
    
    Warnings
    --------
    Cette requête échouera si PostGIS n'est pas installé sur la
    base. Il est donc fortement recommandé de vérifier d'abord
    la présence de PostGIS avec :py:func:`query_exists_extension` :
    
        >>> query = query_exists_extension('postgis')
        >>> cur.execute(*query)
        >>> postgis_exists = cur.fetchone()[0]
    
    """
    return PgQueryWithArgs(
        query=sql.SQL("""
            SELECT
                ST_AsText(ST_Extent({geom}))
                FROM {relation}
            """).format(
                relation=sql.Identifier(schema_name, table_name),
                geom=sql.Identifier(geom_name)
                ),
        expecting='one row',
        allow_none=False, # ne devrait pas arriver
        missing_mssg="Plume n'a pas pu déterminer l'emprise des géométries du " \
            'champ "{}" de la relation "{}"."{}".'.format(
            geom_name, schema_name, table_name)
        )

def query_get_geom_centroid(schema_name, table_name, geom_name):
    """Requête de calcul côté serveur du centre du rectangle d'emprise d'une couche.
    
    À utiliser comme suit :
    
        >>> query = query_get_geom_centroid('nom du schéma',
        ...     'nom de la relation', 'nom du champ de géométrie')
        >>> cur.execute(*query)
        >>> centroid_geom = cur.fetchone()[0]
    
    À noter que le résultat est une géométrie dont le
    système de coordonnées n'est pas explicité. Il faudra
    le récupérer via :py:func:`query_get_geom_srid`, puis
    appliquer la fonction :py:func:`plume.rdf.utils.wkt_with_srid`
    pour obtenir la représention du centroïde attendue en RDF :
    
        >>> from plume.rdf.utils import wkt_with_srid
        >>> query = query_get_geom_srid('nom du schéma', 'nom de la relation'
        ...     'nom du champ de géométrie')
        >>> cur.execute(*query)
        >>> srid = cur.fetchone()[0]
        >>> centroid = wkt_with_srid(centroid_geom, srid)
    
    Parameters
    ----------
    schema_name : str
        Nom du schéma.
    table_name : str
        Nom de la relation (table, vue...).
    geom_name : str
        Nom du champ de géométrie.
    
    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL.
    
    Warnings
    --------
    Cette requête échouera si PostGIS n'est pas installé sur la
    base. Il est donc fortement recommandé de vérifier d'abord
    la présence de PostGIS avec :py:func:`query_exists_extension` :
    
        >>> query = query_exists_extension('postgis')
        >>> cur.execute(*query)
        >>> postgis_exists = cur.fetchone()[0]
    
    """
    return PgQueryWithArgs(
        query=sql.SQL("""
            SELECT
                ST_AsText(ST_Centroid(ST_Extent({geom})))
                FROM {relation}
            """).format(
                relation=sql.Identifier(schema_name, table_name),
                geom=sql.Identifier(geom_name)
                ),
        expecting='one row',
        allow_none=False, # ne devrait pas arriver
        missing_mssg="Plume n'a pas pu déterminer le centroïde des géométries du " \
            'champ "{}" de la relation "{}"."{}".'.format(
            geom_name, schema_name, table_name)
        )

def query_get_comment_fragments(schema_name, table_name, pattern=None,
    flags=None, **kwargs):
    """Requête de récupération d'une partie du descriptif PostgreSQL d'une table.
    
    À utiliser comme suit :
    
        >>> query = query_get_comment_fragments(schema_name='nom du schéma',
        ...     table_name='nom de la relation', **compute_params)
        >>> cur.execute(*query)
        >>> result = cur.fetchall()
    
    ``compute_params`` est le dictionnaire fourni par la clé
    `'compute parameters'` du dictionnaire interne associé à
    la clé courante du dictionnaire de widgets. Si spécifié par
    le modèle, il contiendra la valeur des paramètres `pattern`
    et `flags`.
    
    La liste ainsi obtenue contient des tuples d'un élément, un
    pour chaque fragment du descriptif capturé par l'expression
    régulière. Si aucune expression régulière n'a été spécifiée,
    c'est tout le descriptif hors métadonnées qui est renvoyé.
    Avec ou sans expression régulière, la requête commence en effet
    par retirer les balises ``<METADATA>`` et leur contenu.
    
    Parameters
    ----------
    schema_name : str
        Nom du schéma.
    table_name : str
        Nom de la relation (table, vue...).
    pattern : str, optional
        Une expression régulière déterminant le ou les
        fragments du descriptif PostgreSQL à renvoyer.
        Si non spécifié, la requête récupèrera tout le
        descriptif expurgé des balises ``<METADATA>`` et
        de leur contenu. Si l'expression régulière est
        invalide (d'après les critères de PostgreSQL), la
        requête ne renverra rien.
    flags : str, optional
        Paramètres associés à l'expression rationnelle.
        Si PostgreSQL ne les reconnaît pas, la requête
        ne renverra rien.
    **kwargs : dict, optional
        Paramètres supplémentaires ignorés.
    
    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL, incluant
        son tuple de paramètres.
    
    Warnings
    --------
    Cette requête échouera si PlumePg n'est pas installée sur la
    base.
    
    Notes
    -----
    Cette fonction est référencée par le module
    :py:mod:`plume.pg.computer`.
    
    """
    if not pattern:
        return PgQueryWithArgs(
            query=sql.SQL("""
                SELECT z_plume.meta_ante_post_description('{}'::regclass, 'pg_class')
                """
                ).format(
                    sql.Identifier(schema_name, table_name)
                    ),
            expecting='some rows',
            allow_none=True # n'arrivera pas, quoi qu'il en soit
            )
    return PgQueryWithArgs(
        query=sql.SQL(
            """
            SELECT z_plume.meta_regexp_matches(
                z_plume.meta_ante_post_description(
                    '{}'::regclass, 'pg_class'),
                %s, %s)
            """
            ).format(
                sql.Identifier(schema_name, table_name)
                ),
        args=(pattern, flags),
        expecting='some rows',
        allow_none=True # n'arrivera pas, quoi qu'il en soit
        )

def query_get_modification_date(schema_name, table_name, **kwargs):
    """Requête de récupération de la date de dernière modification d'une table.
    
    À utiliser comme suit :
    
        >>> query = query_get_modification_date(schema_name='nom du schéma',
        ...     table_name='nom de la table', **compute_params)
        >>> cur.execute(*query)
        >>> result = cur.fetchall()
    
    ``compute_params`` est le dictionnaire fourni par la clé
    `'compute parameters'` du dictionnaire interne associé à
    la clé courante du dictionnaire de widgets.
    
    La liste ainsi obtenue contient un unique tuple dont le seul
    élément est la date recherchée, si tant est que l'information
    soit disponible.
    
    Parameters
    ----------
    schema_name : str
        Nom du schéma.
    table_name : str
        Nom de la table. Il est possible d'appliquer cette
        fonction sur des vues ou d'autres types de relations,
        mais la requête produite ne renverra à coup sûr rien.
    **kwargs : dict, optional
        Paramètres supplémentaires ignorés.
    
    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL,
        incluant son tuple de paramètres.
    
    Warnings
    --------
    Cette requête échouera si PlumePg n'est pas installée sur la
    base. Par ailleurs, elle ne renverra de date que si le suivi
    des dates a été activé pour la table considérée.
    
    Notes
    -----
    Cette fonction est référencée par le module
    :py:mod:`plume.pg.computer`.
    
    """
    return PgQueryWithArgs(
        query=sql.SQL("""
            SELECT modified FROM z_plume.stamp_timestamp
                WHERE relid = '{}'::regclass
            """
            ).format(
                sql.Identifier(schema_name, table_name)
                ),
        expecting='one value',
        allow_none=True # quand l'enregistrement des dates
        # n'est pas actif sur la table
        )

def query_get_creation_date(schema_name, table_name, **kwargs):
    """Requête de récupération de la date de création d'une table.
    
    À utiliser comme suit :
    
        >>> query = query_get_creation_date(schema_name='nom du schéma',
        ...     table_name='nom de la table', **compute_params)
        >>> cur.execute(*query)
        >>> result = cur.fetchall()
    
    ``compute_params`` est le dictionnaire fourni par la clé
    `'compute parameters'` du dictionnaire interne associé à
    la clé courante du dictionnaire de widgets.
    
    La liste ainsi obtenue contient un unique tuple dont le seul
    élément est la date recherchée, si tant est que l'information
    soit disponible.
    
    Parameters
    ----------
    schema_name : str
        Nom du schéma.
    table_name : str
        Nom de la table. Il est possible d'appliquer cette
        fonction sur des vues ou d'autres types de relations,
        mais la requête produite ne renverra à coup sûr rien.
    **kwargs : dict, optional
        Paramètres supplémentaires ignorés.
    
    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL,
        incluant son tuple de paramètres.
    
    Warnings
    --------
    Cette requête échouera si PlumePg n'est pas installée sur la
    base. Par ailleurs, elle ne renverra de date que si le suivi
    des dates a été activé pour la table considérée.
    
    Notes
    -----
    Cette fonction est référencée par le module
    :py:mod:`plume.pg.computer`.
    
    """
    return PgQueryWithArgs(
        query=sql.SQL("""
            SELECT created FROM z_plume.stamp_timestamp
                WHERE relid = '{}'::regclass
            """
            ).format(
                sql.Identifier(schema_name, table_name)
                ),
        expecting='one value',
        allow_none=True # quand l'enregistrement des dates
        # n'est pas actif sur la table        
        )

def query_is_template_admin():
    """Requête qui vérifie que le rôle courant dispose des privilèges nécessaire pour configurer les modèles de fiches de métadonnées de PlumePg.
    
    Concrètement, elle vérifie les privilèges suivants :
    
    * ``USAGE`` sur le schéma ``z_plume``.
    * ``INSERT``, ``UPDATE``, ``DELETE`` sur la table d'association
      des catégories aux modèles, ``z_plume.meta_template_categories``.
    * ``INSERT``, ``UPDATE``, ``DELETE`` sur la table des modèles,
      ``z_plume.meta_template``.
    * ``INSERT``, ``UPDATE``, ``DELETE`` sur la table des catégories,
      ``z_plume.meta_categorie``.
    * ``INSERT``, ``UPDATE``, ``DELETE`` sur la table des onlgets,
      ``z_plume.meta_tab``.
    
    Ces privilèges ne sont pas tout à fait suffisants pour pouvoir éditer
    les modèles (il faut aussi des droits sur les séquences, les types, etc.),
    mais en disposer signifer qu'on a voulu habiliter l'utilisateur à
    les modifier. S'il lui manque des droits annexes, Plume lui fera
    savoir par un message d'erreur qui permettra à l'administrateur du
    serveur d'accorder les privilèges manquants.

    La requête suppose que l'extension PostgreSQL PlumePg est installée
    sur le serveur, sans quoi son exécution échouera.

    À utiliser comme suit :
    
        >>> query = query_is_template_admin
        >>> cur.execute(*query)
        >>> res = cur.fetchone()
        >>> is_template_admin = res[0]

    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL.
    
    """
    return PgQueryWithArgs(
        query = sql.SQL("""
            SELECT
                has_schema_privilege('z_plume', 'USAGE')
                AND has_table_privilege('z_plume.meta_template', 'INSERT')
                AND has_table_privilege('z_plume.meta_template', 'UPDATE')
                AND has_table_privilege('z_plume.meta_template', 'DELETE')
                AND has_table_privilege('z_plume.meta_template_categories', 'INSERT')
                AND has_table_privilege('z_plume.meta_template_categories', 'UPDATE')
                AND has_table_privilege('z_plume.meta_template_categories', 'DELETE')
                AND has_table_privilege('z_plume.meta_categorie', 'INSERT')
                AND has_table_privilege('z_plume.meta_categorie', 'UPDATE')
                AND has_table_privilege('z_plume.meta_categorie', 'DELETE')
                AND has_table_privilege('z_plume.meta_tab', 'INSERT')
                AND has_table_privilege('z_plume.meta_tab', 'UPDATE')
                AND has_table_privilege('z_plume.meta_tab', 'DELETE')
            """),
        expecting='one value',
        allow_none=False,
        missing_mssg="Plume n'a pas pu confirmer si le rôle courant est " \
            'habilité à gérer les modèles de fiches de métadonnées de PlumePg.'
    )

def query_read_meta_template_categories():
    """Requête qui importe le contenu de la table d'association des catégories aux modèles (meta_template_categories) de PlumePg.

    À utiliser comme suit :
    
        >>> query = query_read_meta_template_categories()
        >>> cur.execute(*query)
        >>> template_categories = cur.fetchall()

    ``template_categories`` est une liste de tuples, où chaque tuple correspond à un
    couple modèle + catégorie. Les tuples contiennent un unique élément : un dictionnaire
    dont les clés sont les noms des champs de la table d'association et les valeurs
    sont les valeurs contenues dans ces champs pour le couple modèle + catégorie
    considéré. L'ordre des clés ne respecte pas l'ordre des champs dans la
    table.

    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL.
    
    """
    return PgQueryWithArgs(
        query = sql.SQL("""
            SELECT to_json(meta_template_categories.*)
                FROM z_plume.meta_template_categories
                ORDER BY tpl_label, shrcat_path NULLS LAST, loccat_path NULLS LAST
            """),
        expecting='some rows',
        allow_none=True
    )

def query_read_meta_template():
    """Requête qui importe le contenu de la table des modèles (meta_template) de PlumePg.

    À utiliser comme suit :
    
        >>> query = query_read_meta_template()
        >>> cur.execute(*query)
        >>> templates = cur.fetchall()

    ``templates`` est une liste de tuples, où chaque tuple correspond à un
    modèle. Les tuples contiennent un unique élément : un dictionnaire
    dont les clés sont les noms des champs de la table des modèles
    et les valeurs sont les valeurs contenues dans ces champs pour le modèle
    considéré. L'ordre des clés ne respecte pas l'ordre des champs dans la
    table.

    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL.
    
    """
    return PgQueryWithArgs(
        query = sql.SQL("""
            SELECT to_json(meta_template.*)
                FROM z_plume.meta_template
                ORDER BY tpl_label
            """),
        expecting='some rows',
        allow_none=True
    )

def query_read_meta_categorie():
    """Requête qui importe le contenu de la table des catégories de métadonnées (meta_categorie) de PlumePg.

    À utiliser comme suit :
    
        >>> query = query_read_meta_categorie()
        >>> cur.execute(*query)
        >>> categories = cur.fetchall()

    ``categories`` est une liste de tuples, où chaque tuple correspond à une
    catégorie. Les tuples contiennent un unique élément : un dictionnaire
    dont les clés sont les noms des champs de la table des catégories
    et les valeurs sont les valeurs contenues dans ces champs pour la catégorie
    considéré. L'ordre des clés ne respecte pas l'ordre des champs dans la
    table.

    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL.
    
    """
    return PgQueryWithArgs(
        query = sql.SQL("""
            SELECT to_json(meta_categorie.*) 
                FROM z_plume.meta_categorie
                ORDER BY origin DESC, path
            """),
        expecting='some rows',
        allow_none=True
    )

def query_read_meta_tab():
    """Requête qui importe le contenu de la table des onglets (meta_tab) de PlumePg.

    À utiliser comme suit :
    
        >>> query = query_read_meta_tab()
        >>> cur.execute(*query)
        >>> tabs = cur.fetchall()

    ``tabs`` est une liste de tuples, où chaque tuple correspond à un
    onglet. Les tuples contiennent un unique élément : un dictionnaire
    dont les clés sont les noms des champs de la table des onglets
    et les valeurs sont les valeurs contenues dans ces champs pour l'onglet
    considéré. L'ordre des clés ne respecte pas l'ordre des champs dans la
    table.

    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL.
    
    """
    return PgQueryWithArgs(
        query = sql.SQL("""
            SELECT to_json(meta_tab.*)
                FROM z_plume.meta_tab
                ORDER BY tab
            """),
        expecting='some rows',
        allow_none=True
    )

def query_insert_or_update_any_table(schema_name, table_name, pk_name, data, columns=None):
    """Requête qui crée ou met à jour un enregistrement d'une table quelconque.

    À utiliser comme suit :
    
        >>> query = query_insert_or_update_any_table(
        ...    'nom du schéma', 'nom de la table', 'nom du champ de clé primaire',
        ...    ['valeur champ 1', 'valeur champ 2', 'valeur champ 3'],
        ...    ['nom champ 1', 'nom champ 2', 'nom champ 3']
        ...    )
        >>> cur.execute(*query)
        >>> new_data = cur.fetchone()[0]

    ``new_data`` est un dictionnaire contenant l'enregistrement
    mis à jour, tel qu'il est stocké en base.

    Parameters
    ----------
    schema_name : str
        Nom du schéma.
    table_name : str
        Nom de la table.
    pk_name : str
        Nom du champ de clé primaire. La fonction ne prend pas en
        charge les tables avec des clés primaires multi-champs.
    data : list or dict
        `data` représente un enregistrement de la table. Il peut
        s'agir de :

        * La liste des valeurs des champs, dans l'ordre de `columns`,
          qui doit alors être renseigné.
        * Un dictionnaire dont les clés sont les noms des champs.
          `columns` est ignoré dans ce cas.
    columns : list
        Liste des noms des champs de la table des onglets pour lesquels
        `data` fournit des valeurs, exactement dans le même ordre. Il est
        possible d'obtenir la liste complète avec :py:func:`query_get_columns`.

    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL.
    
    """
    if isinstance(data, list):
        if not columns:
            raise MissingParameter('columns')
        if len(data) != len(columns):
            raise ValueError("Les listes 'data' et 'columns' devraient être de même longueur")
        values = data
    elif isinstance(data, dict):
        values = [v for v in data.values()]
        columns = [k for k in data.keys()]
    else:
        raise TypeError("'data' devrait être un dictionnaire ou une liste")

    return PgQueryWithArgs(
        query = sql.SQL("""
            INSERT INTO {relation} ({columns})
                VALUES ({values})
                ON CONFLICT ({pk_name}) DO UPDATE
                    SET ({columns}) = ROW ({values})
                RETURNING to_json({relation}.*)
        """).format(
            relation=sql.Identifier(schema_name, table_name),
            columns=sql.SQL(', ').join(sql.Identifier(c) for c in columns),
            values=sql.SQL(', ').join(
                sql.Literal(v) if v is not None else sql.SQL('DEFAULT') for v in values
            ),
            # NB: forcer "DEFAULT" empêche de remplacer la valeur par défaut par NULL
            # mais ce n'est pas un problème ici, considérant que tous les champs avec
            # des valeurs par défaut ont aussi une contrainte NOT NULL.
            pk_name=sql.Identifier(pk_name)
        ),
        expecting='one row',
        allow_none=False,
        missing_mssg="Echec de la modification des données"
    )

def query_update_any_table(schema_name, table_name, pk_name, data, columns=None):
    """Requête qui met à jour un enregistrement existant d'une table quelconque.

    La requête sera sans effet si l'enregistrement n'existait pas.
    
    À utiliser comme suit :
    
        >>> query = query_update_any_table(
        ...    'nom du schéma', 'nom de la table', 'nom du champ de clé primaire',
        ...    ['valeur champ 1', 'valeur champ 2', 'valeur champ 3'],
        ...    ['nom champ 1', 'nom champ 2', 'nom champ 3']
        ...    )
        >>> cur.execute(*query)
        >>> new_data = cur.fetchone()[0]

    ``new_data`` est un dictionnaire contenant l'enregistrement
    mis à jour, tel qu'il est stocké en base.

    Parameters
    ----------
    schema_name : str
        Nom du schéma.
    table_name : str
        Nom de la table.
    pk_name : str
        Nom du champ de clé primaire. La fonction ne prend pas en
        charge les tables avec des clés primaires multi-champs.
    data : list or dict
        `data` représente un enregistrement de la table. Il peut
        s'agir de :

        * La liste des valeurs des champs, dans l'ordre de `columns`,
          qui doit alors être renseigné.
        * Un dictionnaire dont les clés sont les noms des champs.
          `columns` est ignoré dans ce cas.
    columns : list
        Liste des noms des champs de la table des onglets pour lesquels
        `data` fournit des valeurs, exactement dans le même ordre. Il est
        possible d'obtenir la liste complète avec :py:func:`query_get_columns`.

    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL.
    
    """
    if isinstance(data, list):
        if not columns:
            raise MissingParameter('columns')
        if len(data) != len(columns):
            raise ValueError("Les listes 'data' et 'columns' devraient être de même longueur")
        values = data
    elif isinstance(data, dict):
        values = [v for v in data.values()]
        columns = [k for k in data.keys()]
    else:
        raise TypeError("'data' devrait être un dictionnaire ou une liste")

    pk_index = columns.index(pk_name)
    if pk_index is not None:
        pk_value = values[pk_index]
    else:
        raise ValueError("Identifiant de l'enregistrement non spécifié")

    return PgQueryWithArgs(
        query = sql.SQL("""
            UPDATE {relation}
                SET ({columns}) = ROW ({values})
                WHERE {pk_name} = %s
                RETURNING to_json({relation}.*)
        """).format(
            relation=sql.Identifier(schema_name, table_name),
            columns=sql.SQL(', ').join(sql.Identifier(c) for c in columns),
            values=sql.SQL(', ').join(
                sql.Literal(v) if v is not None else sql.SQL('DEFAULT') for v in values
            ),
            # NB: forcer "DEFAULT" empêche de remplacer la valeur par défaut par NULL
            # mais ce n'est pas un problème ici, considérant que tous les champs avec
            # des valeurs par défaut ont aussi une contrainte NOT NULL.
            pk_name=sql.Identifier(pk_name)
        ),
        args=(pk_value,),
        expecting='one row',
        allow_none=False,
        missing_mssg="Echec de la modification des données"
    )

def query_insert_or_update_meta_tab(data, columns=None):
    """Requête qui crée ou met à jour un onglet dans la table meta_tab de PlumePg.

    À utiliser comme suit :
    
        >>> query = query_insert_or_update_meta_tab(data)
        >>> cur.execute(*query)
        >>> new_data = cur.fetchone()[0]

    ``new_data`` est un dictionnaire contenant l'enregistrement
    mis à jour, tel qu'il est stocké en base.

    Parameters
    ----------
    data : list or dict
        `data` représente un enregistrement de la table. Il peut
        s'agir de :

        * La liste des valeurs des champs, dans l'ordre de `columns`,
          qui doit alors être renseigné.
        * Un dictionnaire dont les clés sont les noms des champs.
          `columns` est ignoré dans ce cas.
    columns : list
        Liste des noms des champs de la table des onglets pour lesquels
        `data` fournit des valeurs, exactement dans le même ordre. Il est
        possible d'obtenir la liste complète avec :py:func:`query_get_columns`.

    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL.
    
    """
    return query_insert_or_update_any_table(
        'z_plume', 'meta_tab', 'tab', data, columns=columns
    )

def query_insert_or_update_meta_categorie(data, columns=None):
    """Requête qui crée ou met à jour une catégorie de métadonnées dans la table meta_categorie de PlumePg.

    À utiliser comme suit :
    
        >>> query = query_insert_or_update_meta_categorie(data)
        >>> cur.execute(*query)
        >>> new_data = cur.fetchone()[0]

    ``new_data`` est un dictionnaire contenant l'enregistrement
    mis à jour, tel qu'il est stocké en base.

    Pour la mise à jour d'une catégorie commune, il est impératif :

    * que le champ ``origin`` soit présent et prenne la valeur 
      ``'shared'`` ;
    * que l'identifiant ``path`` soit renseigné.

    Si l'une au moins de ces deux conditions n'est pas remplie, la
    catégorie de métadonnée est considérée comme locale.

    Parameters
    ----------
    data : list or dict
        `data` représente un enregistrement de la table. Il peut
        s'agir de :

        * La liste des valeurs des champs, dans l'ordre de `columns`,
          qui doit alors être renseigné.
        * Un dictionnaire dont les clés sont les noms des champs.
          `columns` est ignoré dans ce cas.
    columns : list
        Liste des noms des champs de la table des onglets pour lesquels
        `data` fournit des valeurs, exactement dans le même ordre. Il est
        possible d'obtenir la liste complète avec :py:func:`query_get_columns`.

    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL.
    
    """
    # INSERT ON CONFLICT ne fonctionne pas avec les tables partitionnées
    if isinstance(data, list):
        if not columns:
            raise MissingParameter('columns')
        path = data[columns.index('path')] if 'path' in columns else None
        origin = data[columns.index('origin')] if 'origin' in columns else None
    elif isinstance(data, dict):
        path = data.get('path')
        origin = data.get('origin')
    else:
        raise TypeError("'data' devrait être un dictionnaire ou une liste")
    if origin == 'shared':
        if not path:
            raise ValueError('Métadonnée commune non identifiée')
        return query_update_any_table(
            'z_plume', 'meta_shared_categorie', 'path', data, columns=columns
        )
        # NB: on envoie des UPDATE et pas des INSERT ON CONFLICT DO UPDATE sur
        # meta_shared_categorie, parce qu'il y a un trigger sur cette table qui
        # supprime les enregistrements existants qui sont sur le point d'être
        # réinsérés, entraînant la perte de toutes les données liées...
    elif origin in (None, 'local'):
        return query_insert_or_update_any_table(
            'z_plume', 'meta_local_categorie', 'path', data, columns=columns
        )
    else:
        raise ValueError(
            'Une métadonnée peut être commune ("shared") ou'
            f' locale ("local"), pas "{origin}"'
        )

def query_insert_or_update_meta_template(data, columns=None):
    """Requête qui crée ou met à jour un modèle de fiches de métadonnées dans la table meta_template de PlumePg.

    À utiliser comme suit :
    
        >>> query = query_insert_or_update_meta_template(data)
        >>> cur.execute(*query)
        >>> new_data = cur.fetchone()[0]

    ``new_data`` est un dictionnaire contenant l'enregistrement
    mis à jour, tel qu'il est stocké en base.

    Parameters
    ----------
    data : list or dict
        `data` représente un enregistrement de la table. Il peut
        s'agir de :

        * La liste des valeurs des champs, dans l'ordre de `columns`,
          qui doit alors être renseigné.
        * Un dictionnaire dont les clés sont les noms des champs.
          `columns` est ignoré dans ce cas.
    columns : list
        Liste des noms des champs de la table des onglets pour lesquels
        `data` fournit des valeurs, exactement dans le même ordre. Il est
        possible d'obtenir la liste complète avec :py:func:`query_get_columns`.

    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL.
    
    """
    return query_insert_or_update_any_table(
        'z_plume', 'meta_template', 'tpl_label', data, columns=columns
    )

def query_insert_or_update_meta_template_categories(data, columns=None):
    """Requête qui crée ou met à jour une association modèle-catégorie dans la table meta_template_categories de PlumePg.

    À utiliser comme suit :
    
        >>> query = query_insert_or_update_meta_template_categories(data)
        >>> cur.execute(*query)
        >>> new_data = cur.fetchone()[0]

    ``new_data`` est un dictionnaire contenant l'enregistrement
    mis à jour, tel qu'il est stocké en base.

    Parameters
    ----------
    data : list or dict
        `data` représente un enregistrement de la table. Il peut
        s'agir de :

        * La liste des valeurs des champs, dans l'ordre de `columns`,
          qui doit alors être renseigné.
        * Un dictionnaire dont les clés sont les noms des champs.
          `columns` est ignoré dans ce cas.
    columns : list
        Liste des noms des champs de la table des onglets pour lesquels
        `data` fournit des valeurs, exactement dans le même ordre. Il est
        possible d'obtenir la liste complète avec :py:func:`query_get_columns`.

    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL.
    
    """
    return query_insert_or_update_any_table(
        'z_plume', 'meta_template_categories', 'tplcat_id', data, columns=columns
    )

def query_delete_any_table(schema_name, table_name, pk_name, data, columns):
    """Requête qui supprime un enregistrement d'une table quelconque.

    À utiliser comme suit :
    
        >>> query = query_delete_any_table(
        ...    'nom du schéma', 'nom de la table', 'nom du champ de clé primaire',
        ...    ['valeur champ 1', 'valeur de la clé primaire', 'valeur champ 3'],
        ...    ['nom champ 1', 'nom du champ de clé primaire', 'nom champ 3']
        ...    )
        >>> cur.execute(*query)

    La fonction renvoie une erreur si `data` et `columns`
    ne contiennent pas de valeur pour le champ de clé primaire.
    Il ne pose aucun problème de fournir des valeurs pour d'autres
    champs, même si la fonction n'en fera rien.

    Parameters
    ----------
    schema_name : str
        Nom du schéma.
    table_name : str
        Nom de la table.
    pk_name : str
        Nom du champ de clé primaire. La fonction ne prend pas en
        charge les tables avec des clés primaires multi-champs.
    data : list or dict
        `data` représente un enregistrement de la table. Il peut
        s'agir de :

        * La liste des valeurs des champs, dans l'ordre de `columns`,
          qui doit alors être renseigné.
        * Un dictionnaire dont les clés sont les noms des champs.
          `columns` est ignoré dans ce cas.
    columns : list
        Liste des noms des champs de la table des onglets pour lesquels
        `data` fournit des valeurs, exactement dans le même ordre. Il est
        possible d'obtenir la liste complète avec :py:func:`query_get_columns`.

    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL.
    
    """
    if isinstance(data, list):
        if not columns:
            raise MissingParameter('columns')
        pk_value = data[columns.index(pk_name)] if pk_name in columns else None
    elif isinstance(data, dict):
        pk_value = data.get(pk_name)
    else:
        raise TypeError("'data' devrait être un dictionnaire ou une liste")
    if not pk_value:
        raise ValueError('Enregistrement à supprimer non identifié')
    return PgQueryWithArgs(
        query = sql.SQL("""
            DELETE FROM {relation}
                WHERE {pk_name} = {pk_value}
            """).format(
                relation=sql.Identifier(schema_name, table_name),
                pk_name=sql.Identifier(pk_name),
                pk_value=sql.Literal(pk_value)
            ),
        expecting='nothing'
    )

def query_delete_meta_tab(data, columns=None):
    """Requête qui supprime un onglet de la table meta_tab de PlumePg.

    À utiliser comme suit :
    
        >>> query = query_delete_meta_tab(data)
        >>> cur.execute(*query)

    La fonction renvoie une erreur si `data` et `columns`
    ne contiennent pas de valeur pour le champ de clé primaire, `tab`.
    Il ne pose aucun problème de fournir des valeurs pour d'autres
    champs, même si la fonction n'en fera rien.

    Parameters
    ----------
    data : list or dict
        `data` représente un enregistrement de la table. Il peut
        s'agir de :

        * La liste des valeurs des champs, dans l'ordre de `columns`,
          qui doit alors être renseigné.
        * Un dictionnaire dont les clés sont les noms des champs.
          `columns` est ignoré dans ce cas.
    columns : list
        Liste des noms des champs de la table des onglets pour lesquels
        `data` fournit des valeurs, exactement dans le même ordre. Il est
        possible d'obtenir la liste complète avec :py:func:`query_get_columns`.

    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL.
    
    """
    return query_delete_any_table(
        'z_plume', 'meta_tab', 'tab', data, columns=columns
    )

def query_delete_meta_template(data, columns=None):
    """Requête qui supprime un modèle de fiches de métadonnées de la table meta_template de PlumePg.

    À utiliser comme suit :
    
        >>> query = query_delete_meta_template(data)
        >>> cur.execute(*query)

    La fonction renvoie une erreur si `data` et `columns`
    ne contiennent pas de valeur pour le champ de clé primaire, `tpl_label`.
    Il ne pose aucun problème de fournir des valeurs pour d'autres
    champs, même si la fonction n'en fera rien.

    Parameters
    ----------
    data : list or dict
        `data` représente un enregistrement de la table. Il peut
        s'agir de :

        * La liste des valeurs des champs, dans l'ordre de `columns`,
          qui doit alors être renseigné.
        * Un dictionnaire dont les clés sont les noms des champs.
          `columns` est ignoré dans ce cas.
    columns : list
        Liste des noms des champs de la table des onglets pour lesquels
        `data` fournit des valeurs, exactement dans le même ordre. Il est
        possible d'obtenir la liste complète avec :py:func:`query_get_columns`.

    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL.
    
    """
    return query_delete_any_table(
        'z_plume', 'meta_template', 'tpl_label', data, columns=columns
    )

def query_delete_meta_template_categories(data, columns=None):
    """Requête qui supprime une association modèle-catégorie de la table meta_template_categories de PlumePg.

    À utiliser comme suit :
    
        >>> query = query_delete_meta_template_categories(data)
        >>> cur.execute(*query)

    La fonction renvoie une erreur si `data` et `columns`
    ne contiennent pas de valeur pour le champ de clé primaire, `tplcat_id`.
    Il ne pose aucun problème de fournir des valeurs pour d'autres
    champs, même si la fonction n'en fera rien.

    Parameters
    ----------
    data : list or dict
        `data` représente un enregistrement de la table. Il peut
        s'agir de :

        * La liste des valeurs des champs, dans l'ordre de `columns`,
          qui doit alors être renseigné.
        * Un dictionnaire dont les clés sont les noms des champs.
          `columns` est ignoré dans ce cas.
    columns : list
        Liste des noms des champs de la table des onglets pour lesquels
        `data` fournit des valeurs, exactement dans le même ordre. Il est
        possible d'obtenir la liste complète avec :py:func:`query_get_columns`.

    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL.
    
    """
    return query_delete_any_table(
        'z_plume', 'meta_template_categories', 'tplcat_id', data, columns=columns
    )

def query_delete_meta_categorie(data, columns=None):
    """Requête qui supprime une catégorie de la table meta_categorie de PlumePg.

    À utiliser comme suit :
    
        >>> query = query_delete_meta_categorie(data)
        >>> cur.execute(*query)

    La fonction renvoie une erreur si `data` et `columns`
    ne contiennent pas de valeur pour le champ de clé primaire, `path`.
    Il ne pose aucun problème de fournir des valeurs pour d'autres
    champs, même si la fonction n'en fera rien.

    Parameters
    ----------
    data : list or dict
        `data` représente un enregistrement de la table. Il peut
        s'agir de :

        * La liste des valeurs des champs, dans l'ordre de `columns`,
          qui doit alors être renseigné.
        * Un dictionnaire dont les clés sont les noms des champs.
          `columns` est ignoré dans ce cas.
    columns : list
        Liste des noms des champs de la table des onglets pour lesquels
        `data` fournit des valeurs, exactement dans le même ordre. Il est
        possible d'obtenir la liste complète avec :py:func:`query_get_columns`.

    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL.
    
    """
    return query_delete_any_table(
        'z_plume', 'meta_categorie', 'path', data, columns=columns
    )

def query_read_any_enum_type(schema_name, type_name):
    """Requête qui récupère les valeurs d'un type énuméré quelconque.

    À utiliser comme suit :
    
        >>> query = query_read_any_enum_type(
        ...    'nom du schéma', 'nom du type'
        ...    )
        >>> cur.execute(*query)
        >>> enum_values = cur.fetchone()[0]

    ``enum_values`` est une liste triée par ordre alphabétique.

    Parameters
    ----------
    schema_name : str
        Nom du schéma.
    type_name : str
        Nom du type énuméré.

    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL.
    
    """
    return PgQueryWithArgs(
        query = sql.SQL("""
            SELECT array_agg(enumlabel ORDER BY enumlabel)
                FROM pg_catalog.pg_enum
                WHERE enumtypid = '{enumtype}'::regtype
            """).format(
                enumtype=sql.Identifier(schema_name, type_name)
            ),
        expecting='one value',
        allow_none=False, # cas d'un type non énuméré
        missing_mssg="Plume n'a pas pu importer les valeurs du type " \
            'énuméré "{}"."{}".'.format(schema_name, type_name)
    )

def query_read_enum_meta_special():
    """Requête qui récupère les valeurs admises par le champ special des tables meta_categorie et meta_template_categories.

    À utiliser comme suit :
    
        >>> query = query_read_enum_meta_special()
        >>> cur.execute(*query)
        >>> enum_values = cur.fetchone()[0]

    ``enum_values`` est une liste triée par ordre alphabétique.

    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL.
    
    """
    return query_read_any_enum_type('z_plume', 'meta_special')

def query_read_enum_meta_datatype():
    """Requête qui récupère les valeurs admises par le champ datatype des tables meta_categorie et meta_template_categories.

    À utiliser comme suit :
    
        >>> query = query_read_enum_meta_datatype()
        >>> cur.execute(*query)
        >>> enum_values = cur.fetchone()[0]

    ``enum_values`` est une liste triée par ordre alphabétique.

    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL.
    
    """
    return query_read_any_enum_type('z_plume', 'meta_datatype')

def query_read_enum_meta_geo_tool():
    """Requête qui récupère les valeurs admises par le champ geo_tools des tables meta_categorie et meta_template_categories.

    À utiliser comme suit :
    
        >>> query = query_read_enum_meta_geo_tool()
        >>> cur.execute(*query)
        >>> enum_values = cur.fetchone()[0]

    ``enum_values`` est une liste triée par ordre alphabétique.

    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL.
    
    """
    return query_read_any_enum_type('z_plume', 'meta_geo_tool')

def query_read_enum_meta_compute():
    """Requête qui récupère les valeurs admises par le champ compute des tables meta_categorie et meta_template_categories.

    À utiliser comme suit :
    
        >>> query = query_read_enum_meta_compute()
        >>> cur.execute(*query)
        >>> enum_values = cur.fetchone()[0]

    ``enum_values`` est une liste triée par ordre alphabétique.

    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL.
    
    """
    return query_read_any_enum_type('z_plume', 'meta_compute')

def query_plume_pg_import_sample_template(templates=None):
    """Requête qui charge un ou plusieurs modèles pré-configurés sur la base courante.

    Cette fonction peut également être utilisée pour réinitialiser
    les modèles. Elle nécessite évidemment que l'extension PlumePg soit
    activée sur la base.

    À utiliser comme suit :
    
        >>> query = query_plume_pg_import_sample_template()
        >>> cur.execute(*query)

    Parameters
    ----------
    templates str or list(str) or tuple(str), optional
        Nom d'un modèle ou plusieurs modèles pré-configurés
        (sous forme de liste ou de tuple) à charger.
        Si l'argument n'est pas fourni, tous les modèles
        pré-configurés sont chargés.

    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL.

    """
    if not templates:
        return PgQueryWithArgs(
            query = sql.SQL("""
                SELECT * FROM z_plume.meta_import_sample_template()
                """),
            expecting='nothing'
        )
    if isinstance(templates, str):
        templates = [templates]
    query = sql.SQL('')
    for template in templates:
        query += sql.SQL("""
            SELECT * FROM z_plume.meta_import_sample_template({template}) ;
            """).format(
                template=sql.Literal(template)
            )
    return PgQueryWithArgs(
        query = query,
        expecting='nothing'
    )

def query_plume_pg_status():
    """Requête qui évalue l'état de l'extension PlumePg sur la base PostgreSQL cible.
    
    Concrètement, cette requête liste les actions que l'utilisateur
    est habilité à réaliser vis-à-vis de l'extension PlumePg. À noter
    qu'à date toutes les actions concernées ne peuvent être réalisées
    que par un super-utilisateur.

    À utiliser comme suit :
    
        >>> query = query_extension_status('nom de l'extension')
        >>> cur.execute(*query)
        >>> actions = cur.fetchone()[0]
    
    Le résultat est ``None`` si aucune action n'est possible,
    sinon il s'agit de la liste des actions disponibles, parmi :
    
    * ``CREATE`` - activation de l'extension sur la base.
    * ``UPDATE`` - mise à jour de l'extension.
    * ``DROP`` - désactivation de l'extension.
    * ``STAMP RECORDING ENABLE`` - activation du suivi intégral
      des dates de création et modification des tables. Cette
      action est listée dès lors que l'un au moins des
      déclencheurs sur évènement n'est pas actif. 
    * ``STAMP RECORDING DISABLE`` - désactivation du suivi intégral
      des dates. Cette action est listée dès lors que l'un au
      moins des déclencheurs sur évènement est actif.
    * ``STAMP TO METADATA ENABLE`` - activation de l'enregistrement
      automatique des dates dans les métadonnées.
    * ``STAMP TO METADATA DISABLE`` - désactivation de l'enregistrement
      automatique des dates dans les métadonnées.

    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL.
    
    See Also
    --------
    :py:func:`query_plume_pg_check`
        Pour vérifier la compatibilité des versions de Plume et PlumePg.
    
    """
    query = sql.SQL("""
        WITH superuser AS (
            SELECT rolsuper FROM pg_roles
                WHERE rolname = current_user
        ),
        actions AS (
            SELECT 'CREATE' AS act
                FROM pg_available_extensions, superuser
                WHERE name = 'plume_pg'
                    AND default_version IS NOT NULL
                    AND installed_version IS NULL
                    AND rolsuper
            UNION
            SELECT 'UPDATE' AS act
                FROM pg_available_extensions, superuser
                WHERE name = 'plume_pg'
                    AND default_version IS NOT NULL
                    AND installed_version IS NOT NULL
                    AND installed_version != default_version
                    AND rolsuper
            UNION
            SELECT 'DROP' AS act
                FROM pg_available_extensions, superuser
                WHERE name = 'plume_pg'
                    AND installed_version IS NOT NULL
                    AND rolsuper
            UNION
            SELECT 'STAMP RECORDING ENABLE' AS act
                FROM pg_event_trigger, superuser
                WHERE evtname IN (
                    'plume_stamp_table_creation',
                    'plume_stamp_table_modification',
                    'plume_stamp_table_drop'
                )
                    AND rolsuper
                HAVING count(*) = 3
                    AND bool_or(evtenabled = 'D')
            UNION
            SELECT 'STAMP RECORDING DISABLE' AS act
                FROM pg_event_trigger, superuser
                WHERE evtname IN (
                    'plume_stamp_table_creation',
                    'plume_stamp_table_modification',
                    'plume_stamp_table_drop'
                )
                    AND rolsuper
                HAVING count(*) = 3
                    AND bool_or(evtenabled = 'O')
            UNION
            SELECT 'STAMP TO METADATA ENABLE' AS act
                FROM pg_trigger, superuser
                WHERE tgname = 'stamp_timestamp_to_metadata'
                    AND tgenabled = 'D'
                    AND rolsuper
            UNION
            SELECT 'STAMP TO METADATA DISABLE' AS act
                FROM pg_trigger, superuser
                WHERE tgname = 'stamp_timestamp_to_metadata'
                    AND tgenabled = 'O'
                    AND rolsuper
        )
        SELECT array_agg(act) FROM actions
        """)
    return PgQueryWithArgs(
        query=query,
        expecting='one value',
        allow_none=False, # n'arrivera jamais
        missing_mssg="Plume n'a pas pu confirmer l'état de l'extension PlumePg."
        )

def query_plume_pg_create():
    """Requête qui active l'extension PlumePg sur la base courante.

    La requête générée par cette fonction ne peut être utilisée
    que si ``CREATE`` était listé dans le résultat renvoyé
    par la fonction :py:func:`query_plume_pg_status`.

    À utiliser comme suit :
    
        >>> query = query_plume_pg_create()
        >>> cur.execute(*query)

    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL.

    """
    return PgQueryWithArgs(
        query = sql.SQL("CREATE EXTENSION plume_pg CASCADE"),
        expecting='nothing'
    )

def query_plume_pg_update():
    """Requête qui met à jour l'extension PlumePg sur la base courante.

    La requête générée par cette fonction ne peut être utilisée
    que si ``UPDATE`` était listé dans le résultat renvoyé
    par la fonction :py:func:`query_plume_pg_status`.

    À utiliser comme suit :
    
        >>> query = query_plume_pg_update()
        >>> cur.execute(*query)

    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL.

    """
    return PgQueryWithArgs(
        query = sql.SQL("ALTER EXTENSION plume_pg UPDATE"),
        expecting='nothing'
    )

def query_plume_pg_drop():
    """Requête qui désactive l'extension PlumePg sur la base courante.

    La requête générée par cette fonction ne peut être utilisée
    que si ``DROP`` était listé dans le résultat renvoyé
    par la fonction :py:func:`query_plume_pg_status`.

    Il est nécessaire de demander confirmation de l'utilisateur
    avant de réaliser cette action, car elle entraîne la perte
    de tous les modèles et dates enregistrés.

    À utiliser comme suit :
    
        >>> query = query_plume_pg_drop()
        >>> cur.execute(*query)

    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL.

    """
    return PgQueryWithArgs(
        query = sql.SQL("DROP EXTENSION plume_pg"),
        expecting='nothing'
    )

def query_stamp_recording_enable():
    """Requête qui active le suivi complet des dates de création/modification des tables via PlumePg.

    La requête générée par cette fonction ne peut être utilisée
    que si ``STAMP RECORDING ENABLE`` était listé dans le résultat
    renvoyé par la fonction :py:func:`query_plume_pg_status`.

    À utiliser comme suit :
    
        >>> query = query_stamp_recording_enable()
        >>> cur.execute(*query)

    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL.

    """
    return PgQueryWithArgs(
        query = sql.SQL("""
            ALTER EVENT TRIGGER plume_stamp_table_creation ENABLE ;
            ALTER EVENT TRIGGER plume_stamp_table_modification ENABLE ;
            ALTER EVENT TRIGGER plume_stamp_table_drop ENABLE ;
        """),
        expecting='nothing'
    )

def query_stamp_recording_disable():
    """Requête qui désactive entièrement le suivi des dates de création/modification des tables via PlumePg.

    La requête générée par cette fonction ne peut être utilisée
    que si ``STAMP RECORDING DISABLE`` était listé dans le résultat
    renvoyé par la fonction :py:func:`query_plume_pg_status`.

    À utiliser comme suit :
    
        >>> query = query_stamp_recording_disable()
        >>> cur.execute(*query)

    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL.

    """
    return PgQueryWithArgs(
        query = sql.SQL("""
            ALTER EVENT TRIGGER plume_stamp_table_creation DISABLE ;
            ALTER EVENT TRIGGER plume_stamp_table_modification DISABLE ;
            ALTER EVENT TRIGGER plume_stamp_table_drop DISABLE ;
        """),
        expecting='nothing'
    )

def query_stamp_to_metadata_enable():
    """Requête qui active la copie automatique des dates enregistrées par le système de suivi de PlumePg dans les fiches de métadonnées.

    La requête générée par cette fonction ne peut être utilisée
    que si ``STAMP TO METADATA ENABLE`` était listé dans le résultat
    renvoyé par la fonction :py:func:`query_plume_pg_status`.

    À utiliser comme suit :
    
        >>> query = query_stamp_to_metadata_enable()
        >>> cur.execute(*query)

    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL.

    """
    return PgQueryWithArgs(
        query = sql.SQL("""
            ALTER TABLE z_plume.stamp_timestamp
                ENABLE TRIGGER stamp_timestamp_to_metadata
        """),
        expecting='nothing'
    )

def query_stamp_to_metadata_disable():
    """Requête qui désactive la copie automatique des dates enregistrées par le système de suivi de PlumePg dans les fiches de métadonnées.

    La requête générée par cette fonction ne peut être utilisée
    que si ``STAMP TO METADATA DISABLE`` était listé dans le résultat
    renvoyé par la fonction :py:func:`query_plume_pg_status`.

    À utiliser comme suit :
    
        >>> query = query_stamp_to_metadata_disable()
        >>> cur.execute(*query)

    Returns
    -------
    PgQueryWithArgs
        Une requête prête à être envoyée au serveur PostgreSQL.

    """
    return PgQueryWithArgs(
        query = sql.SQL("""
            ALTER TABLE z_plume.stamp_timestamp
                DISABLE TRIGGER stamp_timestamp_to_metadata
        """),
        expecting='nothing'
    )
