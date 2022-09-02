"""Noms traduisibles pour les objets fixes des fiches de métadonnées."""

class TranslatedLabel(str):
    """Nom d'un objet fixe."""        

class TranslationsDict(dict):
    """Dictionnaire de traductions.
    
    Parameters
    ----------
    translations : dict
        Dictionnaire dont les clés sont les codes des
        langues et les valeurs les traductions dans
        ces langues.
    
    """

    def __init__(self, translations=None):
        self['fr'] = ''
        if translations:
            self.update({k: TranslatedLabel(v) for k, v in translations.items()})

    def trans(self, langlist=('fr', 'en')):
        """Renvoie la meilleure traduction disponible.

        Parameters
        ----------
        langlist : str or list(str) or tuple(str), default ('fr', 'en')
            Langue ou liste des langues autorisées pour les traductions,
            triées par priorité (langues à privilégier en premier).
        
        Returns
        -------
        str

        """
        if isinstance(langlist, str):
            langlist = (langlist,)
        for language in langlist:
            if language in self:
                return self[language]
        return self['fr']

class TabLabels:
    """Noms des onglets par défaut des formulaires."""

    GENERAL = TranslationsDict({
        'fr': 'Général',
        'en': 'General'
    })

    OTHERS = TranslationsDict({
        'fr': 'Autres',
        'en': 'Others'
    })

    FIELDS = TranslationsDict({
        'fr': 'Champs',
        'en': 'Fields'
    })

class SourceLabels:
    """Noms des sources spéciales de vocabulaire contrôlé."""

    UNLISTED = TranslationsDict({
        'fr': '< non référencé >',
        'en': '< unlisted >'
    })

    MANUAL = TranslationsDict({
        'fr': '< manuel >',
        'en': '< manual >'
    })

    URI = TranslationsDict({
        'fr': '< URI >',
        'en': '< URI >'
    })
