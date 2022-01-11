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
    
    Les paramètres de connexion sont à saisir dynamiquement
    à la première création d'objet. Ils sont ensuite
    conservés en mémoire et réutilisés pour les appels
    suivants à la classe.
    
    Parameters
    ----------
    replace : str, default False
        Si ``True``, les paramètres éventuellement
        mémorisés ne seront pas considérés.
        L'utilisateur sera invité à saisir de
        nouvelles valeurs.
    
    Warnings
    --------
    Non sécurisé (stockage en clair du mot de
    passe).
    
    """
    _memory = None

    def __new__(cls, replace=False):
        if not cls._memory or replace:
            host = input('host (localhost): ') or 'localhost'
            port = input('port (5432): ') or '5432'
            dbname = input('dbname (metadata_dev): ') or 'metadata_dev'
            user = input('user (postgres): ') or 'postgres'
            password = None
            while not password:
                password = input('password : ')
            cls._memory = "host={} port={} dbname={} user={} password={}".format(
                host, port, dbname, user, password)
        return super().__new__(cls, cls._memory)