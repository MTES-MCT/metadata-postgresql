"""
Requêtes prêtes à être envoyées au serveur PostgreSQL.

Selon le cas, les paramètres doivent être passés :
- soit en argument de la fonction qui crée la requête (cas
des identifiants d'objets PostgreSQL) ;
- soit dans le tuple qui constitue le second argument
de la fonction execute() (valeurs litérales).

La syntaxe est systématiquement détaillée dans l'en-tête
des fonctions.

Dépendances : psycopg2-binary (https://www.psycopg.org).
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

