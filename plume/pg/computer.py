"""Référencement des méthodes de calcul de métadonnées côté serveur.

"""

import re
from datetime import datetime

from plume.rdf.rdflib import URIRef, Literal
from plume.rdf.utils import CRS_NS
from plume.rdf.namespaces import DCT, PLUME, DCAT, SKOS
from plume.rdf.properties import PlumeProperty
from plume.rdf.widgetkey import WidgetKey
from plume.rdf.thesaurus import VocabularyGraph
from plume.pg.queries import (
    query_get_srid_list, query_get_comment_fragments,
    query_get_creation_date, query_get_modification_date,
    query_for_theme_computing
)

class ComputationMethod():
    """Méthode de calcul de métadonnées côté serveur.
    
    Parameters
    ----------
    query_builder : function
        Une fonction de création de requête, en principe
        rattachée au module :py:mod:`plume.pg.queries`.
        Cette fonction doit accepter des paramètres arbitraires
        et renvoyer un tuple dont le premier élément est la requête et,
        s'il y a lieu, le second est un tuple contenant ses paramètres.
        Si le nom du schéma est un de ses paramètres, ce paramètre
        devra s'appeler ``schema_name``. Si le nom de la table est
        un de ses paramètres, il devra s'appeler ``table_name``.
        Seuls ces deux paramètres peuvent être obligatoires.
        Les noms des autres paramètres (optionnels, donc) sont à la
        discrétion de la fonction.
    dependances : list(str), optional
        Liste d'extensions PostgreSQL devant être installées sur
        la base cible pour que la méthode soit valable.
    parser : function, default default_parser
        Une fonction qui servira à retraiter le résultat
        retourné par le serveur avant de le passer aux
        clés du dictionnaire de widgets. Elle doit prendre
        pour argument les éléments des tuples résultant de la
        requête et renvoyer un objet :py:class:`ComputationResult`
        ou une liste de tels objets.
    sources : list(rdflib.term.URIRef), optional
        Pour les métadonnées prenant leurs valeurs dans plusieurs
        sources de vocabulaire contrôlé, les sources
        concernées par le calcul. Concrètement, les clés-valeurs
        dont la source courante fait partie de cette liste seront
        remplacées par les valeurs calculées tandis que les autres
        seront préservées. Si ce paramètre est ``None``, toutes les
        clés (clés-valeurs et groupes de propriétés) seront remplacées,
        quelle que soit leur source. Si c'est une liste vide, toutes
        les clés sont préservées. Cette information n'est considérée
        que dans un groupe de valeurs.
    description : str, optional
        Description de l'effet de la méthode de calcul. Si non
        spécifié, une description générique est renvoyée.
    
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
        de widgets. Elle prend pour argument les éléments des tuples
        résultant de la requête et renvoie un objet
        :py:class:`ComputationResult`.
    sources : list(rdflib.term.URIRef)
        Pour les métadonnées prenant leurs valeurs dans plusieurs
        sources de vocabulaire contrôlé, les sources concernées
        par le calcul.
    description : str
        Description de l'effet de la méthode de calcul.
    
    """
    
    def __init__(self, query_builder, dependances=None, parser=None,
        sources=None, description=None):
        self.query_builder = query_builder
        self.dependances = dependances or []
        self.sources = sources
        self.parser = parser or default_parser
        self.description = description or 'Calcul côté serveur'

class ComputationResult():
    """Résultat d'un calcul de métadonnées, sous une forme adaptée pour l'alimentation du dictionnaire de widgets.
    
    Parameters
    ----------
    value : rdflib.term.URIRef or rdflib.term.Literal, optional
        La nouvelle valeur sous forme d'IRI ou de littéral RDF.
        Ces valeurs ont vocation à être directement intégrées
        à l'arbre de clés du dictionnaire de widgets.
    str_value : str, optional
        La nouvelle valeur sous forme de chaîne de caractères.
        Ces valeurs seront désérialisées via 
        :py:meth:`plume.rdf.widgetsdict.WidgetsDict.prepare_value`
        avant intégration dans l'arbre de clés du dictionnaire de
        widgets. Si `value` est renseigné, `str_value` n'est pas
        pris en compte.
    unit : str, optional
        L'unité de la valeur, s'il y a lieu. Cette information ne
        sera considérée que si la valeur est fournie via 
        `str_value`.
    language : str, optional
        La langue de la valeur, s'il y a lieu. Cette information ne
        sera considérée que si la valeur est fournie via 
        `str_value`.
    source : rdflib.term.URIRef, optional
        La source de la valeur, le cas échéant. Elle sera
        déduite de `value` si non renseignée et que `value` est présent,
        et il est généralement préférable de ne pas fournir manuellement
        cette information dans ce cas, sauf à être certain que la valeur
        est bien l'un des concepts de la source considérée.
        Si seul `str_value` est disponible, il est souhaitable de
        fournir la source, sans quoi c'est la source courante du
        widget qui sera utilisée.
    
    Attributes
    ----------
    value : rdflib.term.URIRef or rdflib.term.Literal, optional
        La nouvelle valeur sous forme d'IRI ou de littéral RDF.
    str_value : str, optional
        La nouvelle valeur sous forme de chaîne de caractères.
    unit : str
        L'unité éventuelle de `str_value`.
    language : str, optional
        La langue éventuelle de `str_value`.
    source : rdflib.term.URIRef
        La source éventuelle de `value`.
    
    """
    
    def __init__(self, value=None, str_value=None, unit=None,
        language=None, source=None):
        self.value = value
        self.str_value = str_value if self.value is None else None
        self.unit = unit if self.str_value else None
        self.language = language if self.str_value else None
        self.source = source

def default_parser(*result, **kwargs):
    """Fonction qui fera office de dé-sérialiseur par défaut.
    
    Parameters
    ----------
    *result : tuple
        Un enregistrement du résultat d'une requête sur le
        serveur PostgreSQL.
    **kwargs : dict, optional
        Paramètres supplémentaires ignorés.
    
    Returns
    -------
    ComputationResult
    
    Notes
    -----
    Cette fonction basique suppose :
    
    * que la métadonnée considérée n'a ni langue, ni source,
      ni unité. Elle ne touche donc pas à ces attributs.
    * que le résultat ne comportait qu'un seul champ, ou du
      moins que la valeur à utiliser pour la mise à jour se
      trouvait dans le premier champ.
    * que les valeurs sont sérialisées de la même manière
      que pour leur présentation dans le formulaire de
      Plume. Ceci sous-entend qu'il sera possible d'obtenir
      leurs équivalents RDF en appliquant la méthode
      :py:meth:`plume.rdf.widgetsdict.WidgetsDict.prepare_value`.
    
    """
    if not result:
        return ComputationResult()
    return ComputationResult(str_value=result[0])

def datetime_parser(timestamp, **kwargs):
    """Désérialisation d'un tampon de date et heure.
    
    Parameters
    ----------
    timestamp : datetime.datetime
        Une date avec heure.
    **kwargs : dict, optional
        Paramètres supplémentaires ignorés.
    
    Returns
    -------
    ComputationResult
    
    """
    if isinstance(timestamp, datetime):
        return ComputationResult(
            str_value=timestamp.strftime('%d/%m/%Y %H:%M:%S')
            )
    return ComputationResult()

def crs_parser(crs_auth, crs_code, **kwargs):
    """Renvoie l'URI complet d'un référentiel de coordonnées.
    
    Parameters
    ----------
    crs_auth : str
        Identifiant de l'autorité qui répertorie le
        référentiel.
    crs_code : str
        Code du référentiel dans le registre de l'autorité.
    **kwargs : dict, optional
        Paramètres supplémentaires ignorés.
    
    Returns
    -------
    ComputationResult
    
    """
    if not crs_auth in CRS_NS or not crs_code or \
        not re.match('^[a-zA-Z0-9.]+$', crs_code):
        return ComputationResult()
    value = URIRef('{}{}'.format(CRS_NS[crs_auth], crs_code))
    return ComputationResult(value=value)

def ecospheres_themes_parser(
    schema_name, level_one=True, level_two=True, **kwargs
):
    """Renvoie les thèmes Ecosphères associés à un schéma de la nomenclature nationale.
    
    Parameters
    ----------
    schema_name : str
        Nom du schéma.
    level_one : bool, default True
        Si ``True``, le ou les thèmes de premier niveau
        associés au nom du schéma sont ajoutés (les plus
        génériques).
    level_two : bool, default True
        Si ``True``, le ou les thèmes de second niveau,
        associés au nom du schéma sont ajoutés (les plus
        spécifiques).
    **kwargs : dict, optional
        Paramètres supplémentaires ignorés.
    
    Returns
    -------
    list(ComputationResult)
    
    """
    themes_scheme = URIRef('http://registre.data.developpement-durable.gouv.fr/ecospheres/themes-ecospheres')
    result = []
    themes_graph = VocabularyGraph[themes_scheme]
    for theme in themes_graph.subjects(PLUME.pgSchema, Literal(schema_name)):
        if level_one and (theme, SKOS.narrower, None) in themes_graph:
            result.append(
                ComputationResult(value=theme, source=themes_scheme)
            )
        if level_two and not (theme, SKOS.narrower, None) in themes_graph:
            result.append(
                ComputationResult(value=theme, source=themes_scheme)
            )
    return result

METHODS = {
    DCT.conformsTo : ComputationMethod(
        query_builder=query_get_srid_list,
        dependances=['postgis'],
        sources=[
            PLUME.OgcEpsgFrance,
            URIRef('http://www.opengis.net/def/crs/EPSG/0'),
            PLUME.IgnCrs
        ],
        parser=crs_parser,
        description='Import des référentiels de coordonnées déclarés ' \
            'pour les champs de géométrie de la table ou vue'
        ),
    DCT.title : ComputationMethod(
        query_builder=query_get_comment_fragments,
        dependances=['plume_pg'],
        description='Extraction depuis le descriptif PostgreSQL de la table ou vue'
        ),
    DCT.description : ComputationMethod(
        query_builder=query_get_comment_fragments,
        dependances=['plume_pg'],
        description='Extraction depuis le descriptif PostgreSQL de la table ou vue'
        ),
    DCT.created : ComputationMethod(
        query_builder=query_get_creation_date,
        dependances=['plume_pg'],
        parser=datetime_parser,
        description='Import de la date de création, si enregistrée côté serveur'
        ),
    DCT.modified : ComputationMethod(
        query_builder=query_get_modification_date,
        dependances=['plume_pg'],
        parser=datetime_parser,
        description='Import de la date de dernière modification, si enregistrée côté serveur'
        ),
    DCAT.theme : ComputationMethod(
        query_builder=query_for_theme_computing,
        parser=ecospheres_themes_parser,
        sources=[
            URIRef('http://registre.data.developpement-durable.gouv.fr/ecospheres/themes-ecospheres')
        ],
        description='Thèmes de la nomenclature Ecosphères associés au nom du schéma'
        )
    }
"""Dictionnaire des méthodes de calcul associées aux catégories de métadonnées.

Les clés du dictionnaire sont les chemins (:py:class:`rdflib.paths.SequencePath`)
des catégories de métadonnées. Les valeurs sont des objets :py:class:`ComputationMethod`
décrivant la méthode de calcul disponible pour la catégorie. N'apparaissent dans
ce dictionnaire que les catégories qui ont effectivement une méthode de calcul
associée.

"""

def computation_method(path):
    """Renvoie l'éventuelle méthode de calcul définie pour la catégorie de métadonnées.
    
    Parameters
    ----------
    path : rdflib.paths.SequencePath
        Chemin de la catégorie.
    
    Returns
    -------
    ComputationMethod or None
    
    """
    return METHODS.get(path)

def has_computation_method(path):
    """Détermine si une méthode de calcul est disponible pour la catégorie de métadonnées considérée.

    Parameters
    ----------
    path : rdflib.paths.SequencePath
        Le chemin de la catégorie. Les clés de dictionnaire de
        widget (plume.rdf.widgetkey.WidgetKey) et les propriétés
        (plume.rdf.properties.PlumeProperty) sont également
        acceptées.

    Returns
    -------
    bool

    """
    if isinstance(path, (WidgetKey, PlumeProperty)):
        path = getattr(path, 'path', None)
    if path:
        return path in METHODS
    return False

