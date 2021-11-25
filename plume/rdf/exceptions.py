

class ForbiddenOperation(Exception):
    """Signale l'usage non approprié d'une fonction.
    
    Attributes
    ----------
    widgetkey : WidgetKey
        La clé concernée.
    message : str
        Description de l'anomalie.
    
    """
    
    def __init__(self, widgetkey=None, message=''):
        """Génère une erreur de type ForbiddenOperation.
        
        Parameters
        ----------
        widgetkey : WidgetKey, optional
            La clé concernée du dictionnaire de widgets.
        message : str, optional
            Description de l'anomalie.
        
        """
        self.widgetkey = widgetkey
        self.message = message
        
    def __str__(self):
        return "{}{}".format(
            self.message,
            " {}.".format(self.widgetkey) if self.widgetkey else ''
            )


class IntegrityBreach(Exception):
    """Signale une rupture d'intégrité du dictionnaire de widgets.
    
    Attributes
    ----------
    widgetkey : WidgetKey
        La clé concernée.
    message : str
        Description de l'anomalie.
    
    """
    
    def __init__(self, widgetkey=None, message=''):
        """Génère une erreur de type IntegrityBreach.
        
        Parameters
        ----------
        widgetkey : WidgetKey, optional
            La clé concernée du dictionnaire de widgets.
        message : str, optional
            Description de l'anomalie.
        
        """
        self.widgetkey = widgetkey
        self.message = message
        
    def __str__(self):
        return "{}{}".format(
            self.message,
            " {}.".format(self.widgetkey) if self.widgetkey else ''
            )


class MissingParameter(Exception):
    """Signale un paramètre manquant.
    
    Attributes
    ----------
    parameter : str
        Nom du paramètre.
    widgetkey : WidgetKey
        La clé concernée.
    
    """
    def __init__(self, parameter, widgetkey=None):
        """Génère une erreur de type MissingParameter.
        
        Parameters
        ----------
        parameter : str
            Nom du paramètre.
        widgetkey : WidgetKey, optional
            La clé concernée du dictionnaire de widgets.
        
        """
        self.widgetkey = widgetkey
        self.parameter = parameter
        
    def __str__(self):
        return "Paramètre '{}' manquant.{}".format(
            self.parameter,
            " {}.".format(self.widgetkey) if self.widgetkey else ''
            )
    

class UnknownParameterValue(Exception):
    """Signale une valeur non autorisée pour un paramètre.
    
    Attributes
    ----------
    parameter : str
        Nom du paramètre.
    value : str
        Valeur problématique.
    widgetkey : WidgetKey
        La clé concernée.
    
    """
    def __init__(self, parameter, value, widgetkey=None):
        """Génère une erreur de type UnknownParameterValue.
        
        Parameters
        ----------
        parameter : str
            Nom du paramètre.
        value : str
            Valeur problématique.
        widgetkey : WidgetKey, optional
            La clé concernée du dictionnaire de widgets.
        
        """
        self.widgetkey = widgetkey
        self.parameter = parameter
        self.value = value
        
    def __str__(self):
        return "Valeur '{}' non reconnue pour le paramètre '{}'.{}".format(
            self.value, self.parameter,
            " {}.".format(self.widgetkey) if self.widgetkey else ''
            )
 