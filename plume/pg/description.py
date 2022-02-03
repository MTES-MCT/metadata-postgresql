"""Descriptifs PostgreSQL.

Ce module prend en charge la désérialisation des métadonnées
contenues dans les descriptifs PostgreSQL en graphe de métadonées
(:py:class:`plume.rdf.metagraph.Metagraph()`). En retour, il
permet la mise à jour du texte du descriptif d'après un nouveau
graphe.

Si ``raw`` est le descriptif brut importé depuis PostgreSQL
(peut être ``None`` le cas échéant):

    >>> raw = '...'
    >>> pgdescription = PgDescription(raw)
    
Les métadonnées éventuellement présentes, supposées être encodées en
JSON-LD et placée entre des balises ``<METADATA>`` et ``</METADATA>``,
sont automatiquement désérialisées dans le graphe exposé par la propriété
:py:attr:`PgDescription.metagraph`:

    >>> metagraph = pgdescription.metagraph
    >>> metagraph
    <Graph identifier=... (<class 'plume.rdf.metagraph.Metagraph'>)>

Pour mettre à jour le descriptif, il suffit de redéfinir la
propriété :py:attr:`PgDescription.metagraph` avec le nouveau graphe:

    >>> pgdescription.metagraph = metagraph

Le nouveau texte descriptif est simplement:

    >>> str(pgdescription)
    '...'

"""

import re
from plume.rdf.metagraph import Metagraph


class PgDescription:
    """Descriptif PostgreSQL.
    
    Parameters
    ----------
    raw : str, optional
        Une chaîne de caractères correspondant à un descriptif
        PostgreSQL. Peut être ``None``, qui sera alors
        automatiquement transformé en chaîne de caractères
        vide (idem si l'argument n'est pas fourni).
    
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
    
    def __init__(self, raw=None):
        raw = raw or ''
        self._ante = ''
        self._post = ''
        self._jsonld = ''
        self._metagraph = Metagraph()
        if raw:
            r = re.split(r'\n{0,2}<METADATA>(.*)</METADATA>\n{0,1}', raw, flags=re.DOTALL)
            if len(r) != 3:
                self._ante = raw
            else:
                self._ante, jsonld, self._post = r
                self._jsonld = jsonld.strip('\n')
                try:
                    self._metagraph.parse(data=self._jsonld, format='json-ld')
                except:
                    self._jsonld = ''
    
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
    
    @property
    def ante(self):
        """str: Le texte qui précède la sérialisation JSON-LD des métadonnées.
        
        À défaut de sérialisation JSON-LD, `ante` contient l'intégralité
        du descriptif.
        
        Cette propriété est une chaîne de caractères vide si l'objet PostgreSQL
        n'avait pas de descriptif, ou si le descriptif commence par le JSON-LD.
        
        """
        return self._ante
    
    @property
    def post(self):
        """str: Le texte qui suit la sérialisation JSON-LD des métadonnées.
        
        Cette propriété est une chaîne de caractères vide si l'objet PostgreSQL
        n'avait pas de descriptif, ou si le descriptif finit par le JSON-LD.
        
        """
        return self._post
    
