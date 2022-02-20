"""Référencement des méthodes de calcul de métadonnées côté serveur.

"""

from plume.rdf.rdflib import URIRef
from plume.rdf.utils import crs_ns
from plume.rdf.namespaces import DCT
from plume.pg.queries import query_get_srid_list

class ComputationMethod():
    """Méthode de calcul de métadonnées côté serveur.
    
    Parameters
    ----------
    query_builder : function
        Une fonction de création de requête, en principe
        rattachée au module :py:mod:`plume.pg.queries`.
        Cette fonction doit prendre pour argument le
        nom du schéma et le nom de la table et renvoyer un
        tuple dont le premier élément est la requête et, s'il
        y a lieu, le second est un tuple contenant ses paramètres.
    dependances: list(str), optional
        Liste d'extensions PostgreSQL devant être installées sur
        la base cible pour que la méthode soit valable.
    parser: function, default default_parser
        Une fonction qui servira à retraiter le résultat
        retourné par le serveur avant de le passer aux
        clés du dictionnaire de widgets. Elle doit prendre
        pour argument les éléments des tuples résultant de la
        requête et renvoyer un objet :py:class:`ComputationResult`.
    sources : list(rdflib.term.URIRef), optional
        Pour les métadonnées prenant leurs valeurs dans plusieurs
        sources de vocabulaire contrôlé, les sources
        concernées par le calcul. Concrètement, les clés-valeurs
        dont la source courante fait partie de cette liste seront
        remplacées par les valeurs calculées tandis que les autres
        seront préservées. Si ce paramètres est ``None`` ou une
        liste vide, toutes les clés (clés-valeurs et groupes de
        propriétés) seront remplacées, quelle que soit leur source.
        Cette information n'est considérée que dans un groupe de
        valeurs.
    
    Attributes
    ----------
    query_builder : function
        Fonction de création de la requête. Elle prend pour argument
        le nom du schéma et le nom de la table et renvoie un
        tuple dont le premier élément est la requête et, s'il
        y a lieu, le second est un tuple contenant ses paramètres.
    dependances: list(str)
        Liste d'extensions PostgreSQL devant être installées sur
        la base cible pour que la méthode soit valable.
    parser: function
        Fonction qui servira à retraiter le résultat retourné
        par le serveur avant de le passer aux clés du dictionnaire
        de widgets. Elle prend pour argument une valeur et en
        renvoie une autre.
    sources : list(rdflib.term.URIRef)
        Pour les métadonnées prenant leurs valeurs dans plusieurs
        sources de vocabulaire contrôlé, les sources concernées
        par le calcul.
    
    """
    
    def __init__(self, query_builder, dependances=None, parser=None, sources=None):
        self.query_builder = query_builder
        self.dependances = dependances or []
        self.sources = sources or []
        self.parser = parser or default_parser

def ComputationResult():
    """Résultat d'un calcul de métadonnées, sous une forme adaptée pour l'alimentation du dictionnaire de widgets.
    
    Parameters
    ----------
    value : str, optional
        La nouvelle valeur.
    value_iri : rdflib.term.URIRef, optional
        La nouvelle valeur sous forme d'IRI. `value_iri` est
        ignoré s'il est renseigné alors que `value` est
        présent.
    unit : str, optional
        L'unité de la valeur, s'il y a lieu.
    language : str, optional
        La langue de la valeur, s'il y a lieu.
    source : str, optional
        La source de la valeur, s'il y a lieu.
    source_iri : rdflib.term.URIRef, optional
        La source de la valeur sous forme d'IRI. `source_iri` est
        ignoré s'il est renseigné alors que `source` est
        présent.
    
    Attributes
    ----------
    value : str
        La nouvelle valeur.
    value_iri : rdflib.term.URIRef
        La nouvelle valeur sous forme d'IRI.
    unit : str
        L'unité éventuelle de la valeur.
    language : str, optional
        La langue éventuelle de la valeur.
    source : str, optional
        La source éventuelle de la valeur.
    source_iri : rdflib.term.URIRef, optional
        La source éventuelle de la valeur sous forme d'IRI.
    
    """
    
    def __init__(self, value=None, value_iri=None, unit=None, language=None,
        source=None, source_iri=None):
        self.value = value
        self.value_iri = value_iri if self.value is None else None
        self.unit = unit
        self.language = language
        self.source = source
        self.source_iri = source_iri if self.source is None else None

def default_parser(*result):
    """Fonction qui fera office de dé-sérialiseur par défaut.
    
    Parameters
    ----------
    *result : tuple
        Un enregistrement du résultat d'une requête sur le
        serveur PostgreSQL.
    
    Returns
    -------
    ComputationResult
    
    Notes
    -----
    Cette fonction basique suppose que la métadonnée considérée
    n'a ni langue, ni source, ni unité et ne touche donc pas
    à ces attributs. Elle part aussi du principe que le résultat
    ne comportait qu'un seul champ, ou du moins que la valeur à
    utiliser pour la mise à jour se trouvait dans le premier
    champ.
    
    """
    if not result:
        return ComputationResult()
    return ComputationResult(value=result[0])

def crs_parser(crs_auth, crs_code):
    """Renvoie l'URI complet d'un référentiel de coordonnées.
    
    Parameters
    ----------
    crs_auth : str
        Identifiant de l'autorité qui répertorie le
        référentiel.
    crs_code : str
        Code du référentiel dans le registre de l'autorité.
    
    Returns
    -------
    ComputationResult
    
    """
    if not crs_auth in crs_ns or not crs_code or \
        not re.match('^[a-zA-Z0-9.]+$', crs_code):
        return
    value_iri = URIRef('{}{}').format(crs_ns[crs_auth], crs_code)
    return ComputationResult(value_iri=value_iri,
        source_iri=URIRef('http://www.opengis.net/def/crs/EPSG/0'))

methods = {
    DCT.conformsTo : ComputationMethod(
        query_builder=query_get_srid_list,
        dependances=['postgis'],
        sources=[URIRef('http://www.opengis.net/def/crs/EPSG/0')],
        parser=crs_parser
        )
    }

def computation_method(path):
    """Renvoie l'éventuelle méthode de calcul définie pour la catégorie de métadonnées.
    
    Parameters
    ----------
    path : rdflib.paths.SequencePath
        Chemin de la catégorie.
    
    Returns
    -------
    ComputeMethod or None
    
    """
    return methods.get(path)

