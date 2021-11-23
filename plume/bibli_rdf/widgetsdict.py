

class WidgetKey:
    """Clés des dictionnaires de widgets.
    
    Attributes
    ----------
    generation : int
        Génération de la clé. 0 pour une clé racine.
    is_root : bool
        True pour une clé racine, qui n'a pas de parent.
    parent : WidgetKey
        La clé parente. None pour une clé racine.
    is_m : bool
        True pour une clé de saisie manuelle.
    m_twin : WidgetKey
        Le cas échéant, la clé jumelle.
    
    """
    
    def __init__(self, parent, is_m=False, m_twin=None):
        """Crée une clé de dictionnaire de widgets.
        
        Parameters
        ----------
        parent : WidgetKey
            La clé parente. Vaudra None pour une clé racine.
        is_m : bool, optionnal
            La clé est-elle une clé de saisie manuelle ?
            False par défaut.
        m_twin : WidgetKey
            Le cas échéant, la clé jumelle.
        
        Returns
        -------
        WidgetKey

        """
        self.parent = parent
        self.is_root = parent is None
        self.is_m = is_m
        self.m_twin = m_twin
        self.generation = 0 for parent is None else parent.generation + 1
        
