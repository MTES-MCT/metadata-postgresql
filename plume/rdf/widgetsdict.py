"""Dictionnaires de widgets.
"""

from plume.rdf.widgetkey import WidgetKey, EditKey, GroupOfPropertiesKey, \
    GroupOfValuesKey, TranslationGroupKey, TranslationButtonKey, PlusButtonKey
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
        root : GroupOfPropertiesKey
            La clé racine du dictionnaire, dont toutes les autres sont des
            descendantes.
        
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
            
        self.root = None


    def _build_dict(self, metagraph, shape, vocabulary, path, class_iri,
        parent, subject, nsm, template_is_empty, shallow_template,
        shallow_template_tabs, shallow_data, vsources):
        
        # identification de la forme du schéma SHACL qui décrit la
        # classe cible :
        shape_iri = shape.shape_iri_from_class(class_iri)
        if not shape_iri:
            raise IntegrityBreach("La class '{}' n'est pas répertoriée dans le " \
                "schéma SHACL".format(class_iri))
        
        # ------ Boucle sur les catégories ------
        for property_iri in shape.objects(
            shape_iri,
            URIRef("http://www.w3.org/ns/shacl#property")
            ):
            
            # récupération des informations relatives
            # à la catégorie dans le schéma SHACL
            p = shape.read_property(shape_iri, property_iri)

            cur_parent = parent
            predicate = p['property']
            kind = p['kind'].n3(nsm)
            new_path = ( path + " / " if path else '') + predicate.n3(nsm)
            sources = {}
            default_value = None
            default_brut = None
            default_source = None
            default_source_uri = None
            default_page = None
            is_ghost = parent.is_ghost or False
            one_language = None
            values = None
            
            multilingual = p['unilang'] and (str(p['unilang']).lower() == 'true') or False
            multiple = ( p['max'] is None or int( p['max'] ) > 1 ) and not multilingual
                        
            # ------ Récupération des valeurs ------
            # cas d'une propriété dont les valeurs sont mises à
            # jour à partir d'informations disponibles côté serveur
            if shallow_data and new_path in shallow_data:
                values = shallow_data[new_path].copy() or []
                del shallow_data[new_path]
                
            # sinon, on extrait la ou les valeurs éventuellement
            # renseignées dans le graphe pour cette catégorie
            # et le sujet considéré
            elif not metagraph.is_empty: 
                values = [ o for o in metagraph.objects(subject, predicate) ]

            # exclusion des catégories qui ne sont pas prévues par
            # le modèle, ne sont pas considérées comme obligatoires
            # par shape et n'ont pas de valeur renseignée
            # les catégories obligatoires de shape sont affichées
            # quoi qu'il arrive en mode édition
            # les catégories sans valeur sont éliminées indépendemment
            # du modèle en mode lecture quand readHideBlank vaut True
            if values in ( None, [], [ None ] ) and (
                ( self.readHideBlank and self.mode == 'read' ) \
                or ( not template_is_empty and not ( new_path in shallow_template ) \
                    and not ( self.mode == 'edit' and p['min'] and int(p['min']) > 0 ) ) \
                ):
                continue
            # s'il y a une valeur, mais que
            # read/editHideUnlisted vaut True et que la catégorie n'est
            # pas prévue par le modèle, on poursuit le traitement
            # pour ne pas perdre la valeur, mais on ne créera
            # pas de widget. Les catégories obligatoires de shape sont
            # affichées quoi qu'il arrive
            elif ( (mode == 'edit' and self.editHideUnlisted) or \
                (mode == 'read' and self.readHideUnlisted) ) \
                and not template_is_empty and not ( new_path in shallow_template ) \
                and not ( p['min'] and int(p['min']) > 0 ):
                is_ghost = True
            
            values = values or [ None ]
            
            # ------ Extraction des informations du modèle et choix de l'onglet ------
            if not is_ghost and (new_path in shallow_template):
                t = shallow_template[new_path]
                shallow_template[new_path].update({ 'done' : True })
                
                # choix du bon onglet (évidemment juste
                # pour les catégories de premier niveau)
                if cur_parent.parent.is_root:
                    tab = t.get('tab name', None)
                    if tab and tab in shallow_template_tabs:
                        cur_parent = shallow_template_tabs[tab]
            else:
                t = dict()
                if not is_ghost and cur_parent.parent.is_root and not template_is_empty:
                    # les métadonnées hors modèle non masquées
                    # de premier niveau iront dans un onglet "Autres".
                    # S'il n'existe pas encore, on l'ajoute :
                    if not "Autres" in shallow_template_tabs:
                        cur_parent = GroupOfPropertiesKey(parent=cur_parent)
                        shallow_template_tabs.update({ "Autres": cur_parent })
                        self.update({ cur_parent : InternalDict() })
                        self[cur_parent].update({
                            'object' : widget.object(),
                            'main widget type' : 'QGroupBox',
                            'label' : 'Autres',
                            'node' : subject,
                            'class' : URIRef('http://www.w3.org/ns/dcat#Dataset'),
                            'shape order' : len(shallow_template_tabs) + 1,
                            'do not save' : True
                            })
                    else:
                        cur_parent = shallow_template_tabs["Autres"]  
            
            # ------ Sources / thésaurus ------
            if not is_ghost and kind in ("sh:BlankNodeOrIRI", "sh:IRI") \
                and p['ontologies']:

                for s in p['ontologies']:
                    lt = [ o for o in vocabulary.objects(
                        s, URIRef("http://www.w3.org/2004/02/skos/core#prefLabel")
                        ) ]
                    st = pick_translation(lt, self.language) if lt else None
                    if st:
                        sources.update({ s: str(st) })
                        # si t vaut None, c'est que le thésaurus n'est pas
                        # référencé dans vocabulary, dans ce cas, on l'exclut
            
            # ------ Valeur par défaut ------
            if not is_ghost:
                default_value = t.get('default value') or None
                if default_value:
                    if sources:
                        for s in sources:
                            # comme on ne sait pas de quel thésaurus provient le concept
                            # on les teste tous jusqu'à trouver le bon
                            default_brut = concept_from_value(
                                default_value, s, vocabulary, self.language, strict=False
                                )
                            if default_brut:
                                default_source_uri = s
                                default_source = sources.get(default_source_uri)
                                default_value, default_page = value_from_concept(
                                    default_brut, vocabulary, self.language, getpage=True,
                                    getschemeStr=False, getschemeIRI=False, getconceptStr=True
                                    )
                                # NB : on retourne chercher default_value, car la langue de la valeur
                                # du template n'était pas nécessairement la bonne
                                break
                        # s'il y a le moindre problème avec la valeur par défaut, on la rejette :
                        if default_value is None or default_brut is None or default_source is None:
                            default_value = default_brut = default_source = default_page = default_source_uri = None
                    elif kind in ("sh:BlankNodeOrIRI", "sh:IRI") and forbidden_char(default_value) is None:
                        default_brut = URIRef(default_value)
                
            #### TODO
            
            # ------ Multi-valeurs ------
            if len(values) > 1 or (((self.translation and multilingual) or multiple)
                and not (self.mode == 'read' and self.readHideBlank)):
                
                if self.translation and multilingual:
                    widget = TranslationGroupKey(parent=cur_parent,
                        available_languages=self.langList)
                else:
                    widget = GroupOfValuesKey(parent=cur_parent, is_ghost=is_ghost)
                
                self.update({ widget : InternalDict() })
                if not is_ghost:
                    self[widget].update({
                        'object' : widget.object(),
                        'main widget type' : 'QGroupBox',
                        'label' : t.get('label') or str(p['name']),
                        'help text' : t.get('help text') or (str(p['descr']) if p['descr'] else None),
                        'path' : new_path,
                        'shape order' : int(p['order']) if p['order'] is not None else None,
                        'template order' : int(t.get('order')) if t.get('order') is not None else None
                        })
                        
                cur_parent = widget
                # les widgets de saisie référencés juste après auront
                # ce groupe pour parent





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
        
        if widgetkey.is_ghost:
            return
        
        if self[widgetkey]['independant label']:
            self[widgetkey]['label row'] = widgetkey.row
            self[widgetkey]['row'] = widgetkey.row + 1
        else:
            self[widgetkey]['row'] = widgetkey.row
        
        if isinstance(widgetkey, TranslationGroupKey):
            self[widgetkey]['authorized language'] = widgetkey.available_languages.copy()
            if not self[widgetkey]['language value'] in widgetkey.available_languages:
                self[widgetkey]['authorized language'].append(self[widgetkey]['language value'])
         
        self[widgetkey]['hidden M'] = widgetkey.hidden_m
        if isinstance(widgetkey, PlusButtonKey):
            self[widgetkey]['hidden'] = widgetkey.hidden_b
        
        if isinstance(widgetkey, GroupOfValuesKey):
            self[widgetkey]['hide minus button'] = widgetkey.is_single_child


    def add(self, buttonkey):
        """Ajoute un enregistrement (vide) dans le dictionnaire de widgets.
        
        Cette fonction est à utiliser après activation d'un bouton plus
        (plus button) ou bouton de traduction (translation button) par
        l'utilisateur.
        
        Parameters
        ----------
        buttonkey : PlusButtonKey
            La clé du bouton plus ou bouton de traduction actionné par
            l'utilisateur.
        
        Returns
        -------
        dict
            Un dictionnaire ainsi constitué :
            {
            "widgets to show" : [liste des widgets masqués à afficher (QWidget)],
            "widgets to hide" : [liste de widgets à masquer (QWidget)],
            "widgets to move" : [liste de tuples - cf. ci-après],
            "language menu to update" : [liste de clés (tuples) pour lesquelles
            le menu des langues devra être régénéré],
            "new keys" : [liste des nouvelles clés du dictionnaire (tuple)]
            }
            
            Pour toutes les clés listées sous "new keys", il sera nécessaire de
            générer les widgets, actions et menus, comme à la création initiale
            du dictionnaire.
            
            Les tuples de la clé "widgets to move" sont formés comme suit :
            [0] la grille (QGridLayout) où un widget doit être déplacé.
            [1] le widget en question (QWidget).
            [2] son nouveau numéro de ligne / row (int).
            [3] son numéro de colonne / column (int).
            [4] le nombre de lignes occupées / rowSpan (int).
            [5] le nombre de colonnes occupées / columnSpan (int).
        
        """
        ## TODO


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


def pick_translation(litlist, language):
    """Renvoie l'élément de la liste correspondant à la langue désirée.
    
    Parameters
    ----------
    litlist : list of Literal
        Une liste de Literal, présumés de type xsd:string.
    language : str
        La langue pour laquelle on cherche une traduction.
    
    Returns
    -------
    Literal
        Un des éléments de la liste, qui peut être :
        - le premier dont la langue est `language` ;
        - à défaut, le dernier dont la langue est 'fr' ;
        - à défaut, le premier de la liste.

    """
    if not litlist:
        raise ForbiddenOperation('La liste ne contient aucune valeur.')
    
    val = None
    
    for l in litlist:
        if l.language == language:
            val = l
            break
        elif l.language == 'fr':
            # à défaut de mieux, on gardera la traduction
            # française
            val = l
            
    if val is None:
        # s'il n'y a ni la langue demandée ni traduction
        # française, on prend la première valeur de la liste
        val = litlist[0]
        
    return val

