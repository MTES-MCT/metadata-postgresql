"""Descriptifs PostgreSQL.

Ce module prend en charge la désérialisation des métadonnées
contenues dans les descriptifs PostgreSQL en graphe de métadonées
(:py:class:`plume.rdf.metagraph.Metagraph()`). En retour, il
permet la mise à jour du texte du descriptif d'après un nouveau
graphe.

Si ``raw`` est le descriptif brut importé depuis PostgreSQL
(peut être ``None`` le cas échéant) :

    >>> raw = '...'
    >>> pgdescription = PgDescription(raw)
    
Les métadonnées éventuellement présentes, supposées être encodées en
JSON-LD et placée entre des balises ``<METADATA>`` et ``</METADATA>``,
sont automatiquement désérialisées dans le graphe exposé par la propriété
:py:attr:`PgDescription.metagraph` :

    >>> metagraph = pgdescription.metagraph
    >>> metagraph
    <Graph identifier=... (<class 'plume.rdf.metagraph.Metagraph'>)>

Pour mettre à jour le descriptif, il suffit de redéfinir la
propriété :py:attr:`PgDescription.metagraph` avec le nouveau graphe :

    >>> pgdescription.metagraph = metagraph

Le nouveau texte descriptif est simplement :

    >>> str(pgdescription)
    '...'

"""

import re
from plume.rdf.metagraph import Metagraph
from plume.rdf.namespaces import DCT
from plume.rdf.utils import pick_translation
from plume.rdf.transliterations import transliterate


class PgDescription:
    """Descriptif PostgreSQL.
    
    Parameters
    ----------
    raw : str, optional
        Une chaîne de caractères correspondant à un descriptif
        PostgreSQL. Peut être ``None``, qui sera alors
        automatiquement transformé en chaîne de caractères
        vide (idem si l'argument n'est pas fourni).
    do_not_parse : bool, default False
        Si ``True``, aucune tentative ne sera faite pour lire les
        éventuelles métadonnées contenues entre les balises
        ``<METADATA>``. Dans ce cas, la propriété
        :py:attr:`PgDescription.metagraph` sera toujours un graphe
        vide et il n'est pas assuré que :py:attr:`PgDescription.jsonld`
        soit un JSON-LD valide. Faire usage de ce paramètre est
        recommandé lorsqu'il n'est pas prévu d'exploiter les
        métadonnées, afin de réduire le temps de calcul.
    clean : {'never', 'first', 'always'}, optional
        Le descriptif PostgreSQL doit-il être réinitialisé ?
        La valeur ``'always'`` entraîne la réinitialisation
        systématique des propriétés :py:attr:`PgDescription.ante`
        et :py:attr:`PgDescription.post`. Avec ``'first'``,
        ces propriétés ne sont vidées que si le graphe d'origine
        était vide.
    copy_dct_title : bool, default False
        Si ``True``, :py:attr:`PgDescription.ante` est réinitialisé
        avec le libellé du jeu de donnée (extrait du graphe)
        lorsque le graphe est mis à jour.
    copy_dct_description : bool, default False
        Si ``True``, :py:attr:`PgDescription.ante` est réinitialisé
        avec la description du jeu de donnée (extraite du graphe)
        lorsque le graphe est mis à jour. Il est possible de combiner
        `copy_dct_title` et `copy_dct_description`, le libellé et
        la description sont alors écrits à la suite, séparés par un
        retour à la ligne.
    
    Attributes
    ----------
    raw : str
        Le descriptif PostgreSQL original, tel que fourni à
        l'initialisation. À défaut de descriptif, il s'agit
        d'une chaîne de caractères vide.
    
    Notes
    -----
    Si la dé-sérialisation du JSON-LD contenu dans le commentaire
    PostgreSQL échoue, il sera considéré que le descriptif ne
    contenait pas de métadonnées. À la première sauvegarde, le
    contenu des balises  ``<METADATA>`` sera écrasé. Le cas échéant, les
    commentaires qui se trouvaient avant et après seront par contre
    préservés.
    
    """
    
    def __init__(
        self, raw=None, do_not_parse=False, clean='never',
        copy_dct_title=False, copy_dct_description=False
    ):
        self.raw = raw or ''
        self.clean = clean if clean in ('always', 'first') else 'never'
        self.copy_dct_title = copy_dct_title or False
        self.copy_dct_description = copy_dct_description or False
        self._ante = ''
        self._post = ''
        self._jsonld = ''
        self._metagraph = Metagraph()

        if self.raw:
            r = re.split(r'\n{0,2}<METADATA>(.*)</METADATA>\n{0,1}', self.raw, flags=re.DOTALL)
            if len(r) != 3:
                self._ante = self.raw
            else:
                self._ante, jsonld, self._post = r
                self._jsonld = jsonld.strip('\n')
                if not do_not_parse:
                    try:
                        self._metagraph.parse(data=self._jsonld, format='json-ld')
                    except:
                        self._jsonld = ''
        
        if self.clean == 'always' or self.clean == 'first' and self.metagraph.is_empty:
            self._ante = ''
            self._post = ''
        
        transliterate(self.metagraph)
    
    def __str__(self):
        jsonld = '\n\n<METADATA>\n{}\n</METADATA>\n'.format(self._jsonld) \
            if self._jsonld else ''
        return '{}{}{}'.format(self._ante, jsonld, self._post)
    
    @property
    def jsonld(self):
        """str: Partie du descriptif correspondant à la sérialisation JSON-LD des métadonnées.
        
        Cette propriété est une chaîne de caractères vide si le descriptif
        ne contenait pas de JSON-LD, ou en cas de suppression a posteriori
        des métadonnées.
        
        """
        return self._jsonld
    
    @jsonld.setter
    def jsonld(self, value):
        self._jsonld = value

    @property
    def metagraph(self):
        """plume.rdf.metagraph.Metagraph: Graphe de métadonnées déduit du descriptif.
        
        À l'initialisation, cette propriété est automatiquement déduite
        du descriptif. Par la suite, ses modifications emportent mise
        à jour de la propriété :py:attr:`PgDescription.jsonld`, et par
        suite du descriptif.
        
        Cette propriété renvoie un graphe vide si le descriptif ne contenait pas
        de JSON-LD.
        
        """
        return self._metagraph
    
    @metagraph.setter
    def metagraph(self, value):
        self._metagraph = value
        if value and isinstance(value, Metagraph):
            self.jsonld = value.serialize(format='json-ld')
        else:
            self.jsonld = ''
        
        if self.copy_dct_title:
            titles = [
                o for o in self.metagraph.objects(self.metagraph.datasetid, DCT.title)
            ]
            if titles:
                t = pick_translation(titles, self.metagraph.langlist)
                self.ante = str(t)
            else:
                self.ante = ''
        
        if self.copy_dct_description:
            descriptions = [
                o for o in self.metagraph.objects(self.metagraph.datasetid, DCT.description)
            ]
            if descriptions:
                t = pick_translation(descriptions, self.metagraph.langlist)
                if self.copy_dct_title:
                    title = self.ante + '\n' if self.ante else ''
                    self.ante = title + str(t)
                else:
                    self.ante = str(t)
            elif not self.copy_dct_title:
                self.ante = ''
    
    @property
    def ante(self):
        """str: Le texte qui précède la sérialisation JSON-LD des métadonnées.
        
        À défaut de sérialisation JSON-LD, `ante` contient l'intégralité
        du descriptif.
        
        Cette propriété est une chaîne de caractères vide si l'objet PostgreSQL
        n'avait pas de descriptif, ou si le descriptif commence par le JSON-LD.
        
        """
        return self._ante

    @ante.setter
    def ante(self, value):
        self._ante = value or ''
    
    @property
    def post(self):
        """str: Le texte qui suit la sérialisation JSON-LD des métadonnées.
        
        Cette propriété est une chaîne de caractères vide si l'objet PostgreSQL
        n'avait pas de descriptif, ou si le descriptif finit par le JSON-LD.
        
        """
        return self._post
    
    @post.setter
    def post(self, value):
        self._post = value or ''

def truncate_metadata(text, with_title=False, langlist=('fr', 'en')):
    """Supprime les métadonnées d'un texte présumé contenir un descriptif PostgreSQL.

    Parameters
    ----------
    text : str
        Le texte à nettoyer.
    with_title : bool, default False
        Si ``True``, la fonction tentera d'extraire des métadonnées
        le libellé de la table ou vue, et le substituera aux
        métadonnées. Si ``False``, les métadonnées sont seulement
        supprimées sans que rien n'apparaisse à leur place.
    langlist : list(str) or tuple(str) or str, default ('fr', 'en')
        Priorisation des langues pour le libellé, si plusieurs
        traductions sont disponibles. N'est considéré que si
        `with_title` vaut ``True``.

    Returns
    -------
    tuple(str, str or None)
        Un tuple dont le premier élément est le texte nettoyé. Le
        second est toujours ``None`` si le texte ne contenait pas
        de métadonnées. Sinon il s'agit d'un texte qui explique
        que des métadonnées sont disponibles.

    """
    title = None
    info = None
    info_meta = 'Des métadonnées sont disponibles pour cette couche. Activez Plume pour les consulter.'
    
    if with_title:
        descr = PgDescription(raw=text)
        if descr.metagraph:
            info = info_meta
            titles = [o for o in descr.metagraph.objects(descr.metagraph.datasetid, DCT.title)]
            if titles:
                t = pick_translation(titles, langlist)
                title = str(t)
    else:
        descr = PgDescription(raw=text, do_not_parse=True)
        if descr.jsonld:
            info = info_meta
    
    ante = descr.ante.rstrip('\n')
    post = descr.post.strip('\n')
    sep = '\n\n' if title else '\n' if ante and post else ''
    ante = (ante + sep) if ante else ''
    post = (sep + post) if post else ''

    return ('{}{}{}'.format(ante, title or '', post), info)

