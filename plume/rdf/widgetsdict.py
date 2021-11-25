"""Dictionnaires de widgets.
"""

from plume.rdf.widgetkey import WidgetKey
from plume.rdf.internalkey import InternalDict
from plume.rdf.actionsbook import ActionsBook
from plume.rdf.exceptions import IntegrityBreach, MissingParameter, ForbiddenOperation, \
    UnknownParameterValue
    

class WidgetsDict(dict):
    """Classe pour les dictionnaires de widgets.
    
    Les attributs du dictionnaire de widgets rappellent le paramétrage
    utilisé à sa création.
    
    Attributes
    ----------
    mode : {'edit', 'read'} 
        'edit' pour un dictionnaire produit pour l'édition, 'read'
        pour un dictionnaire produit uniquement pour la consultation.
        Certaines méthodes ne peuvent être utilisées que sur un
        dictionnaire dont l'attribut `mode` vaut 'edit'.
    translation : bool
        True pour un dictionnaire comportant des fonctionnalités de
        traduction, False sinon. Certaines méthodes ne peuvent être
        utilisées que sur un dictionnaire dont l'attribut `translation`
        vaut True.
    language : str
        Langue principale déclarée lors de la création du dictionnaire.
        `language` est nécessairement l'un des éléments de `langList`
        ci-après.
    langList : list of str
        Liste des langues autorisées pour les traductions, telles que
        déclarées lors de la génération du dictionnaire.
    
    """
    
    def __init__(self, mode, translation, language, langList):
        """Création d'un dictionnaire de widgets vide.
        
        Parameters
        ----------
        mode : {'edit', 'read'}
            Indique si le dictionnaire est généré pour le mode édition
            ('edit'), le mode lecture ('read'). Le mode détermine les actions
            pouvant être exécutées sur le dictionnaire par la suite.
        translation : bool
            Paramètre utilisateur qui indique si les widgets de traduction
            doivent être affichés. Sa valeur contribue à déterminer les actions
            pouvant être exécutées sur le dictionnaire. `translation` ne peut valoir
            True que si le `mode` est 'edit'.
        language : str
            Langue principale de rédaction des métadonnées (paramètre utilisateur).
            Elle influe sur certaines valeurs du dictionnaire et la connaître est
            nécessaire à l'exécution de certaines actions. `language` doit
            impérativement être l'un des éléments de `langList` ci-après.
        langList : list of str
            Liste des langues autorisées pour les traductions. Certaines
            valeurs du dictionnaire dépendent de cette liste, et la connaître est
            nécessaire à l'exécution de certaines actions.
        
        Returns
        -------
        WidgetsDict
            Un dictionnaire de widgets vide.
        """
        if mode in ('edit', 'read'):
            # 'search' n'est pas accepté pour le moment
            self.mode = mode
        else:
            raise UnknownParameterValue('mode', mode)
        
        if not isinstance(translation, bool):
            raise TypeError("translation should be a boolean.")    
        elif translation and mode != 'edit':
            raise ValueError("translation can't be True in 'read' mode.")
        else:
            self.translation = translation
            
        if isinstance(language, str):
            self.language = language
        else:
            raise TypeError("language should be a string.")
            
        if not isinstance(langList, list):
            raise TypeError("langList should be a list.")
        elif not language in langList:
            raise ValueError("language should be in langList.")
        else:
            self.langList = langList


    def parent_grid(self, widgetkey):
        """Renvoie la grille dans laquelle doit être placé le widget de la clé widgetkey.
        
        Parameters
        ----------
        widgetkey : WidgetKey
            Une clé du dictionnaire de widgets.
        
        RESULTAT
        --------
        QGridLayout
            Si la clé existe, que l'enregistrement a un parent et que la grille de
            celui-ci a été créée, ladite grille. Sinon None.
        """
        if not widgetkey.is_root:
            return self[widgetkey.parent].get('grid widget')


    def internalize_widgetkey(self, widgetkey):
        """Retranscrit les attributs d'une clé dans le dictionnaire interne associé.
        
        Parameters
        ----------
        widgetkey : WidgetKey
            Une clé du dictionnaire de widgets.
        
        """
        if not widgetkey in self:
            raise KeyError("La clé '{}' n'est pas référencée.".format(widgetkey))
        
        if widgetkey.row:
            if self[widgetkey]['independant label']:
                self[widgetkey]['label row'] = widgetkey.row
                self[widgetkey]['row'] = widgetkey.row + 1
            else:
                self[widgetkey]['row'] = widgetkey.row
        
        if widgetkey.available_languages:
            self[widgetkey]['authorized language'] = widgetkey.available_languages.copy()
            if not self[widgetkey]['language value'] in widgetkey.available_languages:
                self[widgetkey]['authorized language'].append(self[widgetkey]['language value'])
         
        self[widgetkey]['hidden M'] = widgetkey.hidden_m
        self[widgetkey]['hidden'] = widgetkey.hidden_b
        self[widgetkey]['do not save'] = widgetkey.do_not_save
        
        if self[widgetkey]['has minus button']:
            self[widgetkey]['hide minus button'] = widgetkey.hide_minus_button


    def dictisize_actionsbook(self, actionsbook):
        """Traduit un carnet d'actions en dictionnaire.
        
        La fonction s'assure aussi d'éliminer les actions redondantes
        ou inutiles.
        
        Parameters
        ----------
        actionsbook : ActionsBook
            Le carnet d'actions à traduire.
        
        Returns
        -------
        dict
        
        """
        
        ## TODO

