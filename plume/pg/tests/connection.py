"""Chaînes de connexion PostgreSQL.

La classe :py:class:`ConnectionString` permet la
saisie à la volée des chaînes de connexion
utilisées par les tests.

Création d'une chaîne de connexion:

    >>> connection_string = ConnectionString()

Les paramètres sont demandés un par un. Tous ont
des valeurs par défaut (s'il n'y a pas besoin
d'en saisir une autre, il suffit d'appuyer sur
Enter), sauf le mot de passe, qui sera demandé
encore et encore jusqu'à ce qu'une valeur soit
renseignée.

Le rôle de connexion doit impérativement être
super-utilisateur. La base de données sera créée si elle
n'existe pas déjà, ou supprimée puis re-créée sinon.
Pour ce faire, la recette utilise la base de maintenance
``postgres``, qui est donc supposée exister.

"""

import psycopg2

class MetaConnection(type):

    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls.host = input('host (localhost): ') or 'localhost'
        cls.port = input('port (5432): ') or '5432'
        cls.dbname = input('dbname (plume_rec): ') or 'plume_rec'
        cls.user = input('user (postgres): ') or 'postgres'
        cls.password = None
        while not cls.password:
            cls.password = input('password : ')
        
        # (re-)création de la base de données
        conn = psycopg2.connect(cls.postgres)
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(f"""
                DROP DATABASE IF EXISTS {cls.dbname}
                """)
            cur.execute(f"""
                CREATE DATABASE {cls.dbname}
                """)
        conn.close()

        # activation des extensions nécessaires aux tests
        conn = psycopg2.connect(cls.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute(f"""
                CREATE EXTENSION postgis ;
                CREATE EXTENSION plume_pg CASCADE ;
                """)
        conn.close()
    
    @property
    def postgres(cls):
        """str : Chaîne de connexion à la base de maintenance ``postgres``."""
        return (
            f"host={cls.host} port={cls.port} dbname=postgres "
            f"user={cls.user} password={cls.password}"
        )
    
    @property
    def connection_string(cls):
        """str : Chaîne de connexion à la base cible."""
        return (
            f"host={cls.host} port={cls.port} dbname={cls.dbname} "
            f"user={cls.user} password={cls.password}"
        )

class ConnectionString(str, metaclass=MetaConnection):
    """Chaîne de connexion PostgreSQL.
    
    Les paramètres de connexion sont à saisir dynamiquement
    à l'initialisation de la classe. Ils sont ensuite
    conservés en mémoire et réutilisés pour tous les appels à 
    la classe.

    Les instances de la classe fournissent la chaîne de connexion :

        >>> ConnectionString()
        'host=localhost port=5432 dbname=plume_rec user=postgres password=xxxx'
    
    Il est possible d'accéder aux différents éléments via les attributs
    de la classe.
    
    Parameters
    ----------
    replace : str, default False
        Si ``True``, les paramètres éventuellement
        mémorisés ne seront pas considérés.
        L'utilisateur sera invité à saisir de
        nouvelles valeurs.

    Attributes
    ----------
    host : str
        Adresse du serveur.
    port : str
        Port de connexion sur le serveur.
    dbname : str
        Base de données à utiliser pour les tests. Elle
        sera créée si elle n'existe pas encore.
    user : str
        Rôle de connexion super-utilisateur à utiliser pour
        les tests.
    password : str
        Mot de passe du rôle de connexion.  

    Warnings
    --------
    Non sécurisé (stockage en clair du mot de
    passe).
    
    """
    def __new__(cls, replace=False):
        if replace:
            cls.host = input('host (localhost): ') or 'localhost'
            cls.port = input('port (5432): ') or '5432'
            cls.dbname = input('dbname (plume_rec): ') or 'plume_rec'
            cls.user = input('user (postgres): ') or 'postgres'
            cls.password = None
            while not cls.password:
                cls.password = input('password : ')
        return super().__new__(cls, cls.connection_string)
    
