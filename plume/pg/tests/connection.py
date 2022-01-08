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

"""

class ConnectionString(str):
    """Chaîne de connexion PostgreSQL.
    
    """
    def __new__(cls):
        host = input('host (localhost): ') or 'localhost'
        port = input('port (5432): ') or '5432'
        dbname = input('dbname (metadata_dev): ') or 'metadata_dev'
        user = input('user (postgres): ') or 'postgres'
        password = None
        while not password:
            password = input('password : ')
        return super().__new__(cls,
            "host={} port={} dbname={} user={} password={}".format(
            host, port, dbname, user, password))