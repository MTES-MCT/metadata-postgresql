"""Requêtes prêtes à être envoyées au serveur PostgreSQL.

Ce module suppose l'usage de la bibliothèque Psycopg pour la
communication avec le serveur PostgreSQL.

Selon le cas, les paramètres des requêtes doivent être passés :

* soit en argument de la fonction qui crée la requête, dans
  le cas des identifiants d'objets PostgreSQL ;
* soit, pour les valeurs litérales, dans le tuple qui constitue le
  second argument de :py:meth:`psycopg2.cursor.execute`.

La syntaxe est systématiquement détaillée dans l'en-tête
des fonctions.

References
----------
https://www.psycopg.org

"""

import re
from psycopg2 import sql
from psycopg2.extras import Json

from plume.rdf.exceptions import UnknownParameterValue
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
                    AND (
                        meta_template_categories.shrcat_path IS NOT NULL
                            AND meta_template_categories.shrcat_path ~ '^[a-z]{1,10}[:][a-z0-9-]{1,100}$'
                        OR meta_template_categories.shrcat_path IS NULL
                            AND meta_template_categories.loccat_path ~ ANY(ARRAY[
                                '^[a-z]{1,10}[:][a-z0-9-]{1,100}$',
                                '^[<][^<>"[:space:]{}|\\^`]+[:][^<>"[:space:]{}|\\^`]+[>]$'
                                ])
                        )
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

