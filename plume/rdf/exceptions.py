

class ForbiddenOperation(Exception):
    """Signale l'usage non approprié d'une fonction.
    
    Parameters
    ----------
    message : str, optional
        Description de l'anomalie.
    widgetkey : plume.rdf.widgetkey.WidgetKey, optional
        La clé concernée du dictionnaire de widgets.
    
    Attributes
    ----------
    widgetkey : plume.rdf.widgetkey.WidgetKey
        La clé concernée.
    message : str
        Description de l'anomalie.
    
    """
    
    def __init__(self, message='', widgetkey=None):
        self.widgetkey = widgetkey
        self.message = message
        
    def __str__(self):
        return "{}{}".format(
            self.message,
            " {}.".format(self.widgetkey) if self.widgetkey else ''
            )


class IntegrityBreach(Exception):
    """Signale une rupture d'intégrité du dictionnaire de widgets.
    
    Parameters
    ----------
    message : str, optional
        Description de l'anomalie.
    widgetkey : plume.rdf.widgetkey.WidgetKey, optional
        La clé concernée du dictionnaire de widgets.
    
    Attributes
    ----------
    widgetkey : plume.rdf.widgetkey.WidgetKey
        La clé concernée.
    message : str
        Description de l'anomalie.
    
    """
    
    def __init__(self, message='', widgetkey=None):
        self.widgetkey = widgetkey
        self.message = message
        
    def __str__(self):
        return "{}{}".format(
            self.message,
            " {}.".format(self.widgetkey) if self.widgetkey else ''
            )


class MissingParameter(Exception):
    """Signale un paramètre manquant.
    
    Parameters
    ----------
    parameter : str
        Nom du paramètre.
    widgetkey : plume.rdf.widgetkey.WidgetKey, optional
        La clé concernée du dictionnaire de widgets.
    
    Attributes
    ----------
    parameter : str
        Nom du paramètre.
    widgetkey : plume.rdf.widgetkey.WidgetKey
        La clé concernée.
    
    """
    def __init__(self, parameter, widgetkey=None):
        self.widgetkey = widgetkey
        self.parameter = parameter
        
    def __str__(self):
        return "Paramètre '{}' manquant.{}".format(
            self.parameter,
            " {}.".format(self.widgetkey) if self.widgetkey else ''
            )
   

class UnknownParameterValue(Exception):
    """Signale une valeur non autorisée pour un paramètre.
    
    Parameters
    ----------
    parameter : str
        Nom du paramètre.
    value : str
        Valeur problématique.
    widgetkey : plume.rdf.widgetkey.WidgetKey, optional
        La clé concernée du dictionnaire de widgets.
    
    Attributes
    ----------
    parameter : str
        Nom du paramètre.
    value : str
        Valeur problématique.
    widgetkey : plume.rdf.widgetkey.WidgetKey
        La clé concernée.
    
    """
    def __init__(self, parameter, value, widgetkey=None):
        self.widgetkey = widgetkey
        self.parameter = parameter
        self.value = value
        
    def __str__(self):
        return "Valeur '{}' non reconnue pour le paramètre '{}'.{}".format(
            self.value, self.parameter,
            " {}.".format(self.widgetkey) if self.widgetkey else ''
            )


class UnknownSource(Exception):
    """Signale une source de vocabulaire contrôlé inconnue.
    
    C'est-à-dire qui n'apparaît pas dans ``data/vocabulary.ttl``.
    
    Parameters
    ----------
    iri : rdflib.term.URIRef
        L'IRI de la source.
    
    Attributes
    ----------
    iri : rdflib.term.URIRef
        L'IRI de la source.
    
    """
    def __init__(self, iri):
        self.iri = iri

    def __str__(self):
        return "Source '{}' non répertoriée.".format(self.iri)
 
 