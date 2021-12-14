"""Utilitaires.

"""

from pathlib import Path
from plume import __path__

def abspath(relpath):
    """Déduit un chemin absolu d'un chemin relatif au package.
    
    Parameters
    ----------
    relpath (str):
        Chemin relatif au package. Il n'est ni nécessaire ni
        judicieux d'utiliser la syntaxe Windows à base
        d'antislashs.
    
    Returns
    -------
    pathlib.Path
    
    Examples
    --------
    >>> abspath('rdf/data/vocabulary.ttl')
    WindowsPath('C:/Users/Alhyss/Documents/GitHub/metadata-postgresql/plume/rdf/data/vocabulary.ttl')
    
    """
    return Path(__path__[0]) / relpath