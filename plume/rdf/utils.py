"""Utilitaires.

"""

from pathlib import Path
from rdflib import Literal, URIRef

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

def sort_by_language(litlist, langlist):
    """Trie une liste selon les langues de ses valeurs.
    
    Parameters
    ----------
    litlist : list(rdflib.term.Literal)
        Une liste de valeurs litérales, présumées de type
        ``xsd:string``.
    langlist : list(str)
        Une liste de langues, triées par priorité décroissante.

    """
    litlist.sort(key=lambda v: langlist.index(v.language) \
        if isinstance(v, Literal) and v.language in langlist else 9999)

def pick_translation(litlist, langlist):
    """Renvoie l'élément de la liste dont la langue est la mieux adaptée.
    
    Parameters
    ----------
    litlist : list(rdflib.term.Literal)
        Une liste de valeurs litérales, présumées de type
        ``xsd:string``.
    langlist : list(str) or str
        Une langue ou une liste de langues triées par priorité
        décroissante.
    
    Returns
    -------
    rdflib.term.Literal
        Un des éléments de `litlist`, qui peut être :
        - le premier dont la langue est la première valeur
          de `langlist` ;
        - le premier dont la langue est la deuxième valeur
          de `langlist` ;
        - et ainsi de suite jusqu'à épuisement de `langlist` ;
        - à défaut, le premier élément de `litlist`.

    Notes
    -----
    Cette fonction peut ne pas renvoyer un objet de classe
    :py:class:`rdflib.term.Literal` si `litlist` ne contenait
    que des valeurs non litérales.

    """
    if not litlist:
        return
    if not isinstance(langlist, list):
        langlist = [langlist] if langlist else []
    
    val = None
    
    for language in langlist:
        for l in litlist:
            if isinstance(l, Literal) and l.language == language:
                val = l
                break
        if val:
            break
    
    if val is None:
        # à défaut, on prend la première valeur de la liste
        val = litlist[0]
        
    return val
    
def path_n3(path, nsm):
    """Renvoie la représentation N3 d'un chemin d'IRI.
    
    Parameters
    ----------
    path : URIRef or rdflib.paths.Path
        Un chemin d'IRI.
    nsm : plume.rdf.namespaces.PlumeNamespaceManager
        Un gestionnaire d'espaces de nommage.
    
    Notes
    -----
    RDFLib propose bien une méthode :py:meth:`rdflib.paths.Path.n3`
    pour transformer les chemins d'IRI... mais elle ne prend pas
    d'espace de nommage en argument à ce stade (v 6.0.1). Son
    autre défaut est d'écrire les chemins sans espaces avant et
    après les slashs.
    
    """
    if isinstance(path, URIRef):
        return path.n3(nsm)
    return ' / '.join(path_n3(c, nsm) for c in path.args)

