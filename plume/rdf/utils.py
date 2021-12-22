"""Utilitaires.

"""
import re
from pathlib import Path

from plume import __path__
from plume.rdf.rdflib import Literal, URIRef, from_n3

def data_from_file(filepath):
    """Renvoie le contenu d'un fichier.
    
    Le fichier sera présumé être encodé en UTF-8 et mieux
    vaudrait qu'il le soit.
    
    On pourra utiliser conjointement :py:func:`abspath` pour
    l'import de données du modèle:
    
        >>> data_from_file(abspath('pg/tests/samples/pg_description_1.txt'))
    
    Parameters
    ----------
    filepath : str
        Chemin complet du fichier source.
    
    Returns
    -------
    str
    
    See Also
    --------
    plume.rdf.metagraph.graph_from_file : Import de données RDF.
    
    """
    pfile = Path(filepath)
    
    if not pfile.exists():
        raise FileNotFoundError("Can't find file {}.".format(filepath))
        
    if not pfile.is_file():
        raise TypeError("{} is not a file.".format(filepath))
    
    with pfile.open(encoding='UTF-8') as src:
        data = src.read()
    return data

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
    langlist : list(str) or tuple(str)
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
    langlist : list(str) or tuple(str) or str
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
    if not isinstance(langlist, (list, tuple)):
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

def path_from_n3(path_n3, nsm):
    """Renvoie un chemin d'IRI reconstruit à partir de sa représentation N3.
    
    Parameters
    ----------
    path_n3 : str
        Représentation N3 d'un chemin d'IRI. Les préfixes
        utilisés doivent impérativement être ceux du
        gestionnaire d'espaces de nommage, et a fortiori de
        Plume (:py:data:`plume.rdf.namespaces.namespaces`).
    nsm : plume.rdf.namespaces.PlumeNamespaceManager
        Un gestionnaire d'espaces de nommage.
    
    Returns
    -------
    URIRef or rdflib.paths.Path
        Le chemin d'IRI. ``None`` si la reconstruction a
        échoué, soit parce que `path_n3` n'était pas
        vraiment la représentation N3 d'un chemin d'IRI,
        soit parce que tous les préfixes utilisés n'ont pas
        été reconnus.
    
    """
    namespaces = nsm.namespaces()
    l = re.split(r"\s*[/]\s*", path_n3)
    path = None
    for elem in l:
        try:
            iri = from_n3(elem, nsm=nsm)
        except:
            return
        path = (path / iri) if path else iri
    return path

