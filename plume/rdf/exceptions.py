

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