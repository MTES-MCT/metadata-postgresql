"""
Requêtes prêtes à être envoyées au serveur PostgreSQL.

Selon le cas, les paramètres doivent être passés :
- soit en argument de la fonction qui crée la requête (cas
des identifiants d'objets PostgreSQL) ;
- soit dans le tuple qui constitue le second argument
de la fonction execute() (valeurs litérales).

La syntaxe est systématiquement détaillée dans l'en-tête
des fonctions.

Dépendances : psycopg2 (https://www.psycopg.org).
"""


from psycopg2 import sql


def query_update_table_comment(schema_name, table_name):
    """Crée une requête de mise à jour du descriptif d'une table ou vue.
    
    ARGUMENTS
    ---------
    - schema_name (str) : nom du schéma de la table ;
    - table_name (str) : nom de la table.
    
    RESULTAT
    --------
    Une requête prête à l'emploi, à utiliser comme suit :
    >>> query = query_update_table_comment(schema_name, table_name)
    >>> cur.execute(query, (new_pg_description,))
    
    Avec (arguments positionnels) :
    - new_pg_description (str) : valeur actualisée du descriptif de
    la table.
    """
    return sql.SQL(
        "COMMENT ON TABLE {} IS %s"
        ).format(
            sql.Identifier(schema_name, table_name)
        )


def query_list_templates():
    """Crée une requête d'import de la liste des modèles disponibles.
    
    ARGUMENTS
    ---------
    Néant.
    
    RESULTAT
    --------
    Une requête prête à l'emploi, à utiliser comme suit :
    >>> cur.execute(query_list_templates(), (schema_name, table_name))
    
    On notera qu'au lieu d'importer le filtre sql_filter, la
    commande l'exécute et renvoie un booléen indiquant s'il est
    vérifié.
    """
    return """
        SELECT
            tpl_label,
            z_metadata.meta_execute_sql_filter(sql_filter, %s, %s) AS check_sql_filter,
            md_conditions,
            priority
            FROM z_metadata.meta_template
            ORDER BY tpl_label
        """


def query_get_categories():
    """Crée une requête d'import des catégories à afficher dans un modèle donné.
    
    ARGUMENTS
    ---------
    Néant.
    
    RESULTAT
    --------
    Une requête prête à l'emploi, à utiliser comme suit :
    >>> cur.execute(query_get_categories(), (tpl_label,))
    
    Avec :
    - tpl_label (str) : nom du modèle à utiliser.
    """
    return """
        SELECT 
            origin,
            path,
            cat_label,
            widget_type,
            row_span,
            help_text,
            default_value,
            placeholder_text,
            input_mask,
            multiple_values,
            is_mandatory,
            order_key,
            read_only,
            is_node
            FROM z_metadata.meta_template_categories_full
            WHERE tpl_label = %s
        """

