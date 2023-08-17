"""Système de remplacement de triplets de métadonnées.

Le présent module propose une méthode souple pour gérer
les évolutions du schéma des métadonnées communes, et plus généralement
le fait que, du fait des différentes versions des standards et des marges
d'interprétation qu'ils laissent, il existe parfois plusieurs alternatives
de forme pour représenter la même information en RDF avec le vocabulaire
DCAT.

Concrètement, il contient des fonctions dites "de translitération", qui 
doivent porter le décorateur :py:func:`transliteration` et prendre pour unique
argument un graphe de métadonnées :py:class:`plume.rdf.metagraph.Metagraph`.
Ces fonctions peuvent réaliser tous types d'opérations sur le contenu du
graphe (remplacement d'une propriété ou d'une classe par une autre, modification
de la forme d'une valeur, etc.). Elles doivent être applicables à n'importe quel
graphe et ne réaliser la translitération que si les conditions s'y prêtent. Il
importe d'optimiser au maximum les traitements, car la translitération est
exécutée systématiquement au chargement d'une fiche de métadonnées.

La "translitération" des métadonnées doit être effectuée sur tout
graphe appelé à être utilisé pour générer un dictionnaire de widget, qu'il
provienne du serveur PostgreSQL ou d'une source externe. Pour ce faire, on
exécutera simplement :

    >>> transliterate(metagraph)

Pour les mappings simples applicables uniquement aux graphes issus de sources
externes, une privilégiera une déclaration dans :py:data:`plume.rdf.namespaces.PREDICATE_MAP`
ou :py:data:`plume.rdf.namespaces.CLASS_MAP`, ce qui minimise le temps de calcul.

"""

from plume.rdf.namespaces import (
    OWL, DCAT, RDF
)

TRANSLITERATIONS = []

def transliteration(translit_function):
    """Décorateur pour l'enregistrement des fonctions de translitération.
    
    Toute nouvelle fonction de translitération doit porter ce
    décorateur pour être appliquée.

    Parameters
    ----------
    translit_function : function
        Une fonction de translitération, qui prend en argument un 
        graphe de métadonnées :py:class:`plume.rdf.metagraph.Metagraph`
        et ne renvoie rien.
    
    Return
    ------
    function

    """
    TRANSLITERATIONS.append(translit_function)
    return translit_function

def transliterate(metagraph):
    """Translitération des triplets d'un graphe de métadonnées selon le schéma des métadonnées communes.
    
    Cette fonction applique au graphe l'ensemble des fonctions
    de translitération, c'est-à-dire toutes les fonctions marquées
    du décorateur :py:func:`transliteration`.

    Parameters
    ----------
    metagraph : plume.rdf.metagraph.Metagraph
        Un graphe de métadonnées.

    """
    for translit_function in TRANSLITERATIONS:
        translit_function(metagraph)

# @transliteration
def translit_owl_version_info(metagraph):
    """Translitération de la propriété owl:versionInfo en dcat:version.

    Pour les classes définies par DCAT v3, la propriété ``dcat:version``
    représente désormais le numéro de version de la ressource, au lieu
    de ``owl:versionInfo`` utilisé par DCAT-AP v2.

    Parameters
    ----------
    metagraph : plume.rdf.metagraph.Metagraph
        Un graphe de métadonnées.

    """
    for s, o in metagraph.subject_objects(OWL.versionInfo):
        rdf_type = metagraph.value(s, RDF.type)
        if rdf_type in (DCAT.Dataset, DCAT.DatasetSeries, DCAT.DataService):
            metagraph.remove((s, OWL.versionInfo, o))
            metagraph.add((s, DCAT.version, o))

