"""Utilitaires.

"""
import re
from pathlib import Path
from uuid import UUID, uuid4

from plume import __path__
from plume.rdf.rdflib import Literal, URIRef, from_n3

class DatasetId(URIRef):
    """Identifiant de jeu de données.
    
    Parameters
    ----------
    *uuids : str or UUID or rdflib.term.URIRef
        UUID ou chaînes de caractères ou IRI présumés correspondre
        à un UUID. Le premier élément qui s'avère être réellement
        un UUID est conservé. Si aucun n'est valide ou si l'argument
        n'est pas fourni, un nouvel UUID est utilisé pour créer
        l'identifiant.
    
    Attributes
    ----------
    uuid : uuid.UUID
        Représentation de l'identifiant sous forme d'UUID.
    
    Examples
    --------
    >>> DatasetId('4dc72616-7235-461f-95cf-94dfc3cfa629', 
    ...     'urn:uuid:2b4bb94a-c10b-4d99-a0e7-4ee28888e4f4')
    DatasetId('urn:uuid:4dc72616-7235-461f-95cf-94dfc3cfa629')

    >>> DatasetId('pas un UUID', 
    ...     'urn:uuid:2b4bb94a-c10b-4d99-a0e7-4ee28888e4f4')
    DatasetId('urn:uuid:2b4bb94a-c10b-4d99-a0e7-4ee28888e4f4')
    
    >>> DatasetId()
    DatasetId('urn:uuid:...')
    
    """
    def __new__(cls, *uuids):
        if uuids:
            for uuid in uuids:
                if isinstance(uuid, DatasetId):
                    return uuid
                try:
                    u = UUID(str(uuid))
                    return super().__new__(cls, u.urn)
                except:
                    continue
        return super().__new__(cls, uuid4().urn)
    
    def __init__(self, *uuids):
        self.uuid = UUID(str(self))

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

def forbidden_char(anystr):
    """Le cas échéant, renvoie le premier caractère de la chaîne qui ne soit pas autorisé dans un IRI.
    
    Parameters
    ----------
    anystr : str
        La chaîne de caractères à tester.
    
    Returns
    -------
    str
        Si la chaîne contient au moins un caractère interdit, l'un
        de ces caractères.
    
    Example
    -------
    >>> forbidden_char('avec des espaces')
    ' '
    
    """
    r = re.search(r'([<>"\s{}|\\^`])', anystr)
    return r[1] if r else None

def text_with_link(anystr, anyiri):
    """Génère un fragment HTML définissant un lien.
    
    Parameters
    ----------
    anystr : str
        La chaîne de caractères porteuse du lien.
    anyiri : rdflib.term.URIRef
        Un IRI quelconque correspondant à la cible du lien.
    
    Returns
    -------
    str
        Une chaîne de caractère correspondant à un élément A,
        qui sera interprétée par les widgets comme du texte riche.
    
    Examples
    --------
    >>> text_with_link(
    ...     "Documentation de PostgreSQL 10",
    ...     URIRef("https://www.postgresql.org/docs/10/index.html")
    ...     )
    '<A href="https://www.postgresql.org/docs/10/index.html">Documentation de PostgreSQL 10</A>'
    
    """
    return """<a href="{}">{}</a>""".format(
        escape(str(anyiri), quote=True),
        escape(anystr, quote=True)
        )
    
def email_from_owlthing(thing_iri):
    """Renvoie la transcription sous forme de chaîne de caractères d'un IRI représentant une adresse mél.

    Cette fonction très basique se contente de retirer le préfixe
    "mailto:" s'il était présent.

    Parameters
    ----------
    thing_iri : rdflib.term.URIRef
        IRI supposé correspondre à une adresse mél (classe
        RDF  ``owl:Thing``).

    Returns
    -------
    str

    Examples
    --------
    >>> email_from_owlthing(URIRef('mailto:jon.snow@the-wall.we'))
    'jon.snow@the-wall.we'
    
    """
    # à partir de Python 3.9
    # str(thingIRI).removeprefix("mailto:") serait plus élégant
    return re.sub('^mailto[:]', '', str(thing_iri))

def owlthing_from_email(email_str):
    """Construit un IRI valide à partir d'une chaîne de caractères représentant une adresse mél.

    La fonction ne fait aucun contrôle de validité sur l'adresse si ce
    n'est vérifier qu'elle ne contient aucun caractère interdit pour
    un IRI.

    Parameters
    ----------
    email_str : str
        Une chaîne de caractère supposée correspondre à une adresse mél.

    Returns
    -------
    rdflib.term.URIRef
        Un IRI respectant grosso modo le schéma officiel des URI pour
        les adresses mél : ``mailto:<email>``.

    Examples
    --------
    >>> owlthing_from_email('jon.snow@the-wall.we')
    rdflib.term.URIRef('mailto:jon.snow@the-wall.we')
    
    """
    email_str = re.sub('^mailto[:]', '', email_str)
    f = forbidden_char(email_str)
    if f:
        raise ValueError("Le caractère '{}' " \
            "de l'adresse '{}' n'est pas autorisé dans " \
            'un IRI.'.format(f, email_str))
    if email_str:
        return URIRef('mailto:' + email_str)

def tel_from_owlthing(thing_iri):
    """Renvoie la transcription sous forme de chaîne de caractères d'un IRI représentant un numéro de téléphone.

    Contrairement à :py:func:`owlthing_from_tel`, cette fonction très basique
    ne standardise pas la forme du numéro de téléphone. Elle se contente
    de retirer le préfixe ``'tel:'`` s'il était présent.

    Parameters
    ----------
    thing_iri : rdflib.term.URIRef
        IRI supposé correspondre à un numéro de téléphone (classe
        RDF ``owl:Thing``).

    Returns
    -------
    str

    Examples
    --------
    >>> tel_from_owlthing(URIRef('tel:+33-1-23-45-67-89'))
    '+33-1-23-45-67-89'
    
    """
    return re.sub('^tel[:]', '', str(thing_iri))

def owlthing_from_tel(tel_str, add_fr_prefix=True):
    """Construit un IRI valide à partir d'une chaîne de caractères représentant un numéro de téléphone.

    Si le numéro semble être un numéro de téléphone français valide,
    il est standardisé sous la forme ``<tel:+33-x-xx-xx-xx-xx>``.

    Parameters
    ----------
    tel_str : str
        Une chaîne de caractère supposée correspondre à un numéro de téléphone.
    add_fr_prefix : bool, default True
        ``True`` si la fonction doit tenter de transformer les numéros de téléphone
        français locaux ou présumés comme tels (un zéro suivi de neuf chiffres)
        en numéros globaux (``'+33'`` suivi des neuf chiffres). ``True`` par défaut.

    Returns
    -------
    rdflib.term.URIRef
        Un IRI respectant grosso modo le schéma officiel des URI pour les
        numéros de téléphone : ``tel:<phonenumber>``.

    Examples
    --------
    >>> owlthing_from_tel('0123456789')
    rdflib.term.URIRef('tel:+33-1-23-45-67-89')
    
    """
    tel_str = re.sub('^tel[:]', '', tel_str)
    red = re.sub(r'[.\s-]', '', tel_str)
    tel = ''

    if add_fr_prefix:
        a = re.match(r'0(\d{9})$', red)
        # numéro français local
        if a:
            red = '+33' + a[1]
    
    if re.match(r'[+]33\d{9}$', red):
        # numéro français global
        for i in range(len(red)):
            if i == 3 or i > 2 and i%2 == 0:
                tel = tel + "-" + red[i]
            else:
                tel = tel + red[i]
    else:
        tel = re.sub(r'(\d)\s(\d)', r'\1-\2', tel_str).strip(' ')
        # les espaces entre les chiffres sont remplacés par des tirets,
        # ceux en début et fin de chaine sont supprimés
        f = forbidden_char(tel)
        if f:
            raise ValueError("Le caractère '{}' " \
                "du numéro de téléphone '{}' n'est pas autorisé dans " \
                'un IRI.'.format(f, tel_str))
    if tel:
        return URIRef('tel:' + tel)


