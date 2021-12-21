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

from psycopg2 import sql

from plume.rdf.exceptions import UnknownParameterValue
from plume.rdf.namespaces import SNUM


def query_is_relation_owner():
    """Requête qui vérifie que le rôle courant est membre du propriétaire d'une relation (table, etc.).
    
    À utiliser comme suit:
    
        >>> query = query_is_relation_owner()
        >>> cur.execute(query, ('nom du schéma', 'nom de la relation'))
        >>> res = cur.fetchone()
		>>> is_owner = res[0] if res else False
    
    Returns
    -------
    psycopg2.sql.SQL
        Une requête prête à être envoyée au serveur PostgreSQL.
    
    """
    return sql.SQL("""
        SELECT pg_has_role(relowner, 'USAGE')
            FROM pg_catalog.pg_class
            WHERE relnamespace = quote_ident(%s)::regnamespace
                AND relname = %s
        """)
    

def query_exists_extension():
    """Requête qui vérifie qu'une extension est installée sur la base PostgreSQL cible.
    
    À utiliser comme suit:
    
        >>> query = query_exists_extension()
        >>> cur.execute(query, ("nom de l'extension",))
        >>> metadata_exists = cur.fetchone()[0]
    
    Cette requête renverra :
    - ``True`` si l'extension est installée ;
    - ``False`` si elle est disponible dans le répertoire des
      extension du serveur mais non installée ;
    - ``NULL`` si elle n'est pas disponible sur le serveur.
    
    Returns
    -------
    psycopg2.sql.SQL
        Une requête prête à être envoyée au serveur PostgreSQL.
    
    """
    return sql.SQL("""
        SELECT count(*) = 1
            FROM pg_available_extensions
            WHERE name = %s
                AND installed_version IS NOT NULL
        """)


def query_get_relation_kind(schema_name, table_name):
    """Requête qui récupère le type d'une relation PostgreSQL.
    
    À utiliser comme suit:
    
        >>> query = query_get_relation_kind('nom du schéma',
        ...     'nom de la relation')
        >>> cur.execute(query)
        >>> relkind = cur.fetchone()[0]
    
    Parameters
    ----------
    schema_name : str
        Nom du schéma.
    table_name : str
        Nom de la relation (table, vue...).
    
    Returns
    -------
    psycopg2.sql.Composed
        Une requête prête à être envoyée au serveur PostgreSQL.
    
    """
    return sql.SQL("""
        SELECT relkind FROM pg_catalog.pg_class
            WHERE pg_class.oid = '{}'::regclass
        """).format(
            sql.Identifier(schema_name, table_name)
            )


def query_update_table_comment(schema_name, table_name, relation_kind='r'):
    """Requête de mise à jour du descriptif d'une table ou vue.
    
    À utiliser comme suit:
    
        >>> query = query_update_table_comment('nom du schéma',
        ...     'nom de la relation', 'type de relation')
        >>> cur.execute(query, ('Nouveau descriptif',)
    
    Parameters
    ----------
    schema_name : str
        Nom du schéma.
    table_name : str
        Nom de la relation (table, vue...).
    relation_kind : {'r', 'v', 'm', 'f', 'p'}, optional
        Le type de relation. ``'r'`` par défaut, ce qui
        correspond à une table simple.
    
    Returns
    -------
    psycopg2.sql.Composed
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
    
    return sql.SQL(
        "COMMENT ON {} {} IS %s"
        ).format(
            sql.SQL(d[relation_kind]),
            sql.Identifier(schema_name, table_name)
            )


def query_get_table_comment(schema_name, table_name):
    """Requête de récupération du descriptif d'une table ou vue.
    
    À utiliser comme suit:
    
        >>> query = query_get_table_comment('nom du schéma',
        ...     'nom de la relation')
        >>> cur.execute(query)
        >>> old_description = cur.fetchone()[0]
    
    Parameters
    ----------
    schema_name : str
        Nom du schéma.
    table_name : str
        Nom de la relation (table, vue...).
    
    Returns
    -------
    psycopg2.sql.Composed
        Une requête prête à être envoyée au serveur PostgreSQL.
    
    """
    return sql.SQL(
        "SELECT obj_description('{}'::regclass, 'pg_class')"
        ).format(
            sql.Identifier(schema_name, table_name)
            )


def query_list_templates():
    """Requête d'import de la liste des modèles disponibles.
    
    À utiliser comme suit:
    
        >>> query = query_list_templates()
        >>> cur.execute(query, ('nom du schéma', 'nom de la relation'))
        >>> templates = cur.fetchall()
    
    Returns
    -------
    psycopg2.sql.SQL
        Une requête prête à être envoyée au serveur PostgreSQL.
    
    Notes
    -----
    La requête interroge la table ``z_plume.meta_template``
    créée par l'extension PlumePg. Au lieu d'importer 
    tel quel le contenu de son champ ``sql_filter``,
    elle l'exécute et renvoie un booléen indiquant si la
    condition qu'il spécifie est remplie.
    
    """
    return sql.SQL("""
        SELECT
            tpl_label,
            z_plume.meta_execute_sql_filter(sql_filter, %s, %s) AS check_sql_filter,
            md_conditions,
            priority
            FROM z_plume.meta_template
            ORDER BY tpl_label
        """)


def query_get_categories():
    """Requête d'import des catégories à afficher dans un modèle donné.
    
    À utiliser comme suit:
    
        >>> query = query_get_categories()
        >>> cur.execute(query, ('nom du modèle',))
        >>> categories = cur.fetchall()
    
    Returns
    -------
    psycopg2.sql.SQL
        Une requête prête à être envoyée au serveur PostgreSQL.
    
    Notes
    -----
    La requête interroge la vue ``z_plume.meta_template_categories_full``
    créée par l'extension PlumePg.
    
    """
    return sql.SQL("""
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
            template_order,
            is_read_only,
            tab
            FROM z_plume.meta_template_categories_full
            WHERE tpl_label = %s
        """)


def query_template_tabs():
    """Requête d'import des onglets utilisés par un modèle.
    
    À utiliser comme suit:
    
        >>> query = query_template_tabs()
        >>> cur.execute(query, ('nom du modèle',))
        >>> tabs = cur.fetchall()
    
    Returns
    -------
    psycopg2.sql.SQL
        Une requête prête à être envoyée au serveur PostgreSQL.
    
    Notes
    -----
    La requête interroge les tables ``z_plume.meta_tab`` et
    ``z_plume.meta_template_categories`` créées par l'extension
    PlumePg.
    
    L'ordre de la liste résultant de l'exécution de la requête
    est l'ordre dans lequel le modèle prévoit que les onglets
    soient présentés à l'utilisateur.

    """
    return sql.SQL("""
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
        """)


def query_get_columns(schema_name, table_name):
    """Requête de récupération des descriptifs des champs d'une table ou vue.
    
    À utiliser comme suit:
    
        >>> query = query_get_columns('nom du schéma',
        ...     'nom de la relation')
        >>> cur.execute(query)
        >>> columns = cur.fetchall()
    
    Parameters
    ----------
    schema_name : str
        Nom du schéma.
    table_name : str
        Nom de la relation (table, vue...).
    
    Returns
    -------
    psycopg2.sql.Composed
        Une requête prête à être envoyée au serveur PostgreSQL.

    """
    return sql.SQL(
        """
        SELECT
            attname,
            col_description('{attrelid}'::regclass, attnum)
            FROM pg_catalog.pg_attribute
            WHERE attrelid = '{attrelid}'::regclass AND attnum >= 1
            ORDER BY attnum
        """
        ).format(
            attrelid=sql.Identifier(schema_name, table_name)
            )


def query_update_column_comment(schema_name, table_name, column_name):
    """Requête de mise à jour du descriptif d'un champ.
    
    À utiliser comme suit:
    
        >>> query = query_update_column_comment('nom du schéma',
        ...     'nom de la relation', 'nom du champ')
        >>> cur.execute(query, ('Nouveau descriptif du champ',)
    
    Parameters
    ----------
    schema_name : str
        Nom du schéma.
    table_name : str
        Nom de la relation (table, vue...).
    column_name : str
        Nom du champ.
    
    Returns
    -------
    psycopg2.sql.Composed
        Une requête prête à être envoyée au serveur PostgreSQL.
    
    """
    return sql.SQL(
        "COMMENT ON COLUMN {} IS %s"
        ).format(
            sql.Identifier(schema_name, table_name, column_name)
            )


def query_update_columns_comments(schema_name, table_name, widgetsdict):
    """Requête de mise à jour des descriptifs des champs d'une table.
    
    À utiliser comme suit:
    
        >>> query = query_update_columns_comments('nom du schéma',
        ...     'nom de la relation', widgetsdict)
        >>> if query:
        ...     cur.execute(query)
    
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
    psycopg2.sql.Composed
        Une requête prête à être envoyée au serveur PostgreSQL.
    
    Notes
    -----    
    À noter que cette requête pourrait échouer si des champs ont été
    supprimés ou renommés entre temps.
    
    La fonction renvoie ``None`` si elle ne trouve aucun descriptif
    de champ dans le dictionnaire de widgets.
    
    """
    updated_columns = []
    for k, v in widgetsdict.items():
        if k.path == SNUM.column:
            updated_columns.append((k.label, str(k.value or '')))   
    if updated_columns:
        return sql.SQL(' ; ').join([
            sql.SQL(
                "COMMENT ON COLUMN {} IS {}"
                ).format(
                    sql.Identifier(schema_name, table_name, colname),
                    sql.Literal(coldescr)
                    )
            for colname, coldescr in updated_columns
            ])


