"""Dictionnaires de widgets.
"""
from rdflib.namespace import NamespaceManager

from plume.rdf.widgetkey import WidgetKey, ValueKey, GroupOfPropertiesKey, \
    GroupOfValuesKey, TranslationGroupKey, TranslationButtonKey, \
    PlusButtonKey, ObjectKey, RootKey, TabKey
from plume.rdf.internaldict import InternalDict
from plume.rdf.actionsbook import ActionsBook
from plume.rdf.exceptions import IntegrityBreach, MissingParameter, \
    UnknownParameterValue, ForbiddenOperation
from plume.rdf.thesaurus import Thesaurus
from plume.rdf.namespaces import PlumeNamespaceManager, SH, RDF, XSD, SNUM
from plume.rdf.properties import PlumeProperty, class_properties
from plume.rdf.metagraph import uuid_from_datasetid, datasetid_from_uuid

class WidgetsDict(dict):
    """Classe pour les dictionnaires de widgets.
    
    Les attributs du dictionnaire de widgets rappellent le paramétrage
    utilisé à sa création.
    
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
    
    Attributes
    ----------
    datasetid : URIRef
        L'identifiant du jeu de données dont le dictionnaire présente les
        métadonnées.
    root : RootKey
        La clé racine du dictionnaire, dont toutes les autres sont des
        descendantes.
    nsm : PlumeNamespaceManager
        Le gestionnaire d'espaces de nommage permettant de résoudre
        tous les préfixes du dictionnaire.
    mode : {'edit', 'read'} 
        ``'edit'`` pour un dictionnaire produit pour l'édition, ``'read'``
        pour un dictionnaire produit uniquement pour la consultation.
        Certaines méthodes ne peuvent être utilisées que sur un
        dictionnaire dont l'attribut `mode` vaut ``'edit'``.
    edit : bool
        *Propriété calculée*. True si `mode` vaut ``'edit'``.
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
    hideBlank : bool
        Les métadonnées sans valeur doivent-elles être masquées ?
    hideUnlisted : bool
        Les métadonnées hors modèle doivent-elles être masquées ?
    onlyCurrentLanguage : bool
        Les métadonnées qui ne sont pas dans la langue principale
        (`language`) doivent-elles être masquées ?
    textEditRowSpan : int
        Hauteur par défaut des widgets de saisie de texte multi-lignes,
        en nombre de ligne.
    valueLengthLimit : int
        Si la longueur d'une valeur textuelle (nombre de caractères)
        est supérieure à `valueLengthLimit`, elle est affichée sur
        plusieurs lignes.
    labelLengthLimit : int
        Si la longueur d'une étiquette (nombre de caractères) est
        supérieure à `labelLengthLimit`, elle est affichée au-dessus
        du widget de saisie.
    
    """
    
    def __init__(self, metagraph=None, template=None, templateTabs=None, data=None,
        columns=None, mode='edit', translation=False, language='fr',
        langList=['fr', 'en'], readHideBlank=True, editHideUnlisted=False,
        readHideUnlisted=True, editOnlyCurrentLanguage=False,
        readOnlyCurrentLanguage=True, labelLengthLimit=25, valueLengthLimit=65,
        textEditRowSpan=6):
        
        # ------ Paramètres utilisateur ------
        self.mode = mode if mode in ('edit', 'read') else 'edit'
        self.langList = langList if langList and isinstance(langList, list) \
            else ['fr', 'en']
        self.language = language if language in self.langList else 'fr'
        self.labelLengthLimit = labelLengthLimit if labelLengthLimit \
            and isinstance(labelLengthLimit, int) else 25
        self.valueLengthLimit = valueLengthLimit if valueLengthLimit \
            and isinstance(valueLengthLimit, int) else 65
        self.textEditRowSpan = textEditRowSpan if textEditRowSpan \
            and isinstance(textEditRowSpan, int) else 6
        self.translation = translation and self.edit
        self.hideBlank = readHideBlank and not self.edit
        self.hideUnlisted = (readHideUnlisted and not self.edit) \
            or (editHideUnlisted and self.edit)
        self.onlyCurrentLanguage = (readOnlyCurrentLanguage and not self.edit) \
            or (editHideUnlisted and self.edit and not self.translation)
        
        # ------ Racine ------
        # + gestion de l'identifiant
        self.root = None
        self.datasetid = None
        self.nsm = PlumeNamespaceManager()
        
        if data:
            ident = (data.get('dct:identifier') or [None])[0]
            if ident:
                self.datasetid = datasetid_from_uuid(ident)
        mg_datasetid = get_datasetid(metagraph) if metagraph else None
        self.root = RootKey(datasetid=mg_datasetid)
        self[self.root] = InternalDict()
        if not self.datasetid:
            ident = uuid_from_datasetid(self.root.node)
            if ident:
                self.datasetid = self.root.node
            else:
                ident = uuid4()
                self.datasetid = datasetid_from_uuid(ident)
            data['dct:identifier'] = [str(ident)]
            # à ce stade, l'identifiant de la clé racine est
            # celui du graphe, qui n'est plus nécessairement
            # identique à self.datasetid. On attend cependant
            # la fin de l'initialisation pour le corriger, sans
            # quoi on ne pourra pas récupérer le contenu du graphe.
            
        self.root.langlist = self.langList
        self.root.main_language = self.language
        self.root.max_rowspan = 30 if self.edit else 1
        
        # ------ Onglets ------
        if templateTabs:
            for label, order_idx in templateTabs:
                tabkey = TabKey(parent=self.root, label=label,
                    order_idx=order_idx)
                self[tabkey] = InternalDict()
        else:
            tabkey = TabKey(parent=self.root, label='Général', order_idx=(0,))
            self[tabkey] = InternalDict()
        # dans tous les cas, on ajoute un onglet "Autres"
        # pour les catégories hors modèle
        tabkey = TabKey(parent=self.root, label='Autres', order_idx=(9999,))
        self[tabkey] = InternalDict()
        
        # ------ Colonnes de la table ------
        if columns:
            tabkey = TabKey(parent=self.root, label='Champs', order_idx=(9998,))
            self[tabkey] = InternalDict()
            for label, value in columns:
                valkey = ValKey(parent=tabkey, label=label, value=value,
                    is_long_text=True, description='Description du champ',
                    rowspan=textEditRowSpan, predicate=SNUM.column,
                    do_not_save=True)
                self[valkey] = InternalDict()
        
        # ------ Construction récursive ------
        self._build_dict(parent=self.root, metagraph=metagraph, template=template, data=data)
        
        # ------ Nettoyage des groupes vides ------
        actionsbook = self.root.clean()
        for key in actionsbook.drop:
            del self[key]
        
        # ------- Mise à jour de l'identifiant ------
        # dans l'hypothèse où celui de data et celui de metagraph
        # auraient été différents
        self.root.node = self.datasetid
        
        # ------ Calcul des dictionnaires internes ------
        for widgetkey in self.keys():
            self.internalize_widgetkey(widgetkey)

    def _build_dict(self, parent, metagraph=None, template=None, data=None):
        # ------ Constitution de la liste des catégories ------
        # catégories communes de la classe :
        properties, n3_paths, predicates = class_properties(rdfclass=parent.rdfclass,
            nsm=self.nsm, base_path=parent.path, template=template)
        if isinstance(parent, RooKey):
            # catégories locales:
            for n3_path in template.keys():
                if not n3_path in n3_paths:
                    p = PlumeProperty(origin='local', nsm=self.nsm,
                        n3_path=n3_path, template=template)
                    properties.append(p)
                    predicates.append(p.predicate)
            # catégories non référencées
            if metagraph:
                for predicate, o in metagraph.predicate_objects(parent.node):
                    if not predicate in predicates:
                        properties.append(PlumeProperty(origin='unknown',
                            nsm=self.nsm, predicate=predicate))   
        
        # ------ Boucle sur les catégories ------
        for prop in properties:
            prop_dict = prop.prop_dict
            prop_dict['parent'] = parent
            kind = prop_dict.get('kind', SH.Literal)
            multilingual = bool(prop_dict.get('unilang')) and self.translation
            multiple = bool(prop_dict.get('is_multiple')) and self.edit \
                and not bool(prop_dict.get('unilang'))
            
            # ------ Récupération des valeurs ------
            # cas d'une propriété dont les valeurs sont mises à
            # jour à partir d'informations disponibles côté serveur
            if data and prop.n3_path in data:
                values = data[prop.n3_path].copy() or [None]
            # sinon, on extrait la ou les valeurs éventuellement
            # renseignées dans le graphe pour cette catégorie
            # et le sujet considéré
            elif metagraph:
                values = [o for o in metagraph.objects(parent.node,
                    prop.predicate)] or [None]
            else:
                values = [None]

            # ------ Exclusion ------
            # exclusion des catégories qui ne sont pas prévues par
            # le modèle, ne sont pas considérées comme obligatoires
            # par shape et n'ont pas de valeur renseignée.
            # Les catégories obligatoires de shape sont affichées
            # quoi qu'il arrive en mode édition.
            # Les catégories sans valeur sont éliminées indépendamment
            # du modèle quand hideBlank vaut True.
            if values == [None] and (self.hideBlank or prop.unlisted) \
                and not (self.edit and prop_dict.get('is_mandatory')):
                continue
            # ------ Fantômisation ------
            # s'il y a une valeur, mais que hideUnlisted vaut True
            # (ce qui ne peut arriver qu'en mode lecture)
            # et que la catégorie n'est pas prévue par le modèle, on
            # poursuit le traitement pour ne pas perdre la valeur, mais
            # on ne créera pas de widget.
            # Les catégories obligatoires de shape sont affichées quoi
            # qu'il arrive.
            elif prop.unlisted and self.hideUnlisted and \
                not prop_dict.get('is_mandatory'):
                prop_dict['is_ghost'] = True

            # ------ Choix de l'onglet ------
            # pour les catégories de premier niveau
            if isinstance(parent, RootKey):
                if prop.unlisted:
                    # les métadonnées hors modèle iront dans
                    # l'onglet "Autres".
                    prop_dict['parent'] = parent.search_tab('Autres')
                else:
                    prop_dict['parent'] = parent.search_tab(t.get('tab'))
                    # NB : renvoie le premier onglet si l'argument est None

            # ------ Affichage mono-langue ------
            # si seules les métadonnées dans la langue principale
            # doivent être affichées, on trie la liste pour qu'elles soient
            # en tête. Dans tous les cas, la première valeur sera
            # affichées, les autres seront des fantômes si elles
            # ne sont pas dans la bonne langue.
            if prop_dict.get('datatype') == RDF.langString \
                and self.onlyCurrentLanguage:
                sort_by_language(values, self.language)

            # ------ Multi-valeurs ------
            # création d'un groupe de valeurs ou de traduction
            # rassemblant les valeurs actuelles et futures
            if len(values) > 1 or ((multilingual or multiple) and not self.hideBlank):
                if multilingual and not prop_dict.get('is_ghost'):
                    groupkey = TranslationGroupKey(**prop_dict)
                else:
                    groupkey = GroupOfValuesKey(**prop_dict)
                self[groupkey] = InternalDict()
                # les widgets référencés ensuite auront ce groupe pour parent
                prop_dict['parent'] = groupkey
            
            # ------ Boucle sur les valeurs ------
            for value in values:
                val_dict = prop_dict.copy()
            
                # ------ Affichage mono-langue (suite) ------
                if val_dict.get('datatype') == RDF.langString \
                    and self.onlyCurrentLanguage:
                    if value and parent.has_real_children and \
                        (not isinstance(value, Literal) or \
                        value.language != self.language):
                        val_dict['is_ghost'] = True
                
                # ------ Cas d'un noeud anonyme -------
                if kind in (SH.BlankNode, SH.BlankNodeOrIRI) \
                    and (isinstance(value, BNode) or (not self.hideBlank \
                    and not val_dict.get('is_ghost'))):
                    nodekey = GroupOfPropertiesKey(**val_dict)
                    # NB: on ne conserve pas les noeuds anonymes, il est plus
                    # simple d'en générer de nouveaux à l'initialisation de la clé.
                    self[nodekey] = InternalDict()
                    self._build_dict(metagraph=metagraph, parent=nodekey,
                        template=template, data=data)
                    if kind == SH.BlankNodeOrIRI:
                        val_dict['m_twin'] = nodekey
                        val_dict['is_hidden_m'] = not isinstance(value, BNode)
                    
                # ------ Cas d'une valeur litéral ou d'un IRI ------
                if kind in (SH.BlankNodeOrIRI, SH.Literal, SH.IRI) \
                    and (isinstance(value, (Literal, URIRef)) or \
                    (not self.hideBlank and not val_dict.get('is_ghost'))):
                    
                    # adaptation de is_long_text à la valeur
                    if value and kind == SH.Literal \
                        and len(str(value)) > self.valueLengthLimit:
                        val_dict['is_long_text'] = True
                
                    # rowspan selon is_long_text
                    if val_dict.get('is_long_text') and not 'rowspan' in val_dict:
                        val_dict['rowspan'] = self.textEditRowSpan
                
                    # étiquette séparée
                    if val_dict.get('label') and (val_dict.get('is_long_text') or \
                        len(str(val_dict['label'])) > self.labelLengthLimit):
                        val_dict['independant_label'] = True
                
                    # source de la valeur
                    if val_dict.get('sources'):
                        val_dict['value_source'] = Thesaurus.concept_source(value)
                
                    val_dict['value'] = value
                    # value_language est déduit de value à l'initialisation
                    # de la clé, le cas échéant
                    valkey = ValueKey(**val_dict)
                    self[valkey] = InternalDict()
                
            # ------ Bouton ------
            if multilingual or multiple:
                buttonkey = TranslationButtonKey(**prop_dict) if multilingual \
                    else PlusButtonKey(**prop_dict)
                if buttonkey:
                    # buttonkey peut être None s'il s'avère que le groupe
                    # est un fantôme
                    self[buttonkey] = InternalDict()

    @property
    def edit(self):
        """bool: Le dictionnaire est-il généré pour l'édition ?
        
        """
        returns (mode == 'edit')

    def parent_grid(self, widgetkey):
        """Renvoie la grille dans laquelle doit être placé le widget de la clé widgetkey.
        
        Parameters
        ----------
        widgetkey : WidgetKey
            Une clé du dictionnaire de widgets.
        
        Returns
        -------
        QGridLayout
            Si la clé existe, que l'enregistrement a un parent et que la grille de
            celui-ci a été créée, ladite grille. Sinon None.
        
        """
        if widgetkey.parent:
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
        
        if not widgetkey:
            return
   
        internaldict = self[widgetkey]
        
        internaldict['main widget type'] = self.widget_type(widgetkey)
        internaldict['row'] = widgetkey.row
        internaldict['row span'] = widgetkey.row_span
        internaldict['hidden'] = widgetkey.is_hidden_b
        internaldict['hidden M'] = widgetkey.is_hidden_m
        
        if isinstance(widgetkey, (GroupKey, ObjectKey)):
            internaldict['label'] = widgetkey.label
            internaldict['help text'] = widgetkey.description
        
        if isinstance(widgetkey, ValueKey):
            internaldict['label row'] = widgetkey.label_row \
                if widgetkey.independant_label else None
            internaldict['language value'] = widgetkey.value_language
            internaldict['authorized languages'] = widgetkey.available_languages.copy() \
                if widgetkey.available_languages else None
            if not widgetkey.value_language in widgetkey.available_languages:
                internaldict['authorized languages'].insert(0, widgetkey.value_language)
            internaldict['placeholder text'] = widgetkey.placeholder
            internaldict['input mask'] = widgetkey.input_mask
            internaldict['is mandatory'] = widgetkey.is_mandatory
            internaldict['regex validator pattern'] = widgetkey.regex_validator
            internaldict['regex validator flags'] = widgetkey.regex_validator_flags
            internaldict['type validator'] = self.type_validator(widgetkey)
            internaldict['read only'] = widgetkey.read_only
            internaldict['value'] = self.str_value(widgetkey)
            if widgetkey.sources:
                internaldict['sources'] = [Thesaurus.label(s, widgetkey.main_language) \
                    for s in widgetkey.sources]
                if widgetkey.value_source:
                    internaldict['current source'] = Thesaurus.label(
                        (widgetkey.value_source, widgetkey.main_language))
                    internaldict['thesaurus values'] = Thesaurus.values(
                        (widgetkey.value_source, widgetkey.main_language))
                if not internaldict['current source']:
                    internaldict['current source'] = '< non référencé >'
                    internaldict['sources'].insert(0, '< non référencé >')
        
        if isinstance(widgetkey, ObjectKey):
            internaldict['has minus button'] = widgetkey.has_minus_button
            internaldict['hide minus button'] = widgetkey.has_minus_button \
                and widgetkey.is_single_child
            if widgetkey.m_twin:
                internaldict['sources'] = internaldict['sources'] or ['< URI >']
                internaldict['sources'].insert(0, '< manuel >')
                if isinstance(widgetkey, ValueKey): 
                    if not internaldict['current source']:
                        internaldict['current source'] = '< URI >'
                else:
                    internaldict['current source'] = '< manuel >'

    def dictisize_actionsbook(self, widgetkey, actionsbook):
        """Traduit un carnet d'actions en dictionnaire.
        
        Parameters
        ----------
        widgetkey : WidgetKey
            Une clé du dictionnaire de widgets.
        actionsbook : ActionsBook
            Le carnet d'actions à traduire.
        
        Returns
        -------
        dict
        
        """
        
        ## TODO

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

    def widget_type(self, widgetkey):
        """Renvoie le type de widget adapté pour une clé.
        
        Parameters
        ----------
        widgetkey : WidgetKey
            Une clé de dictionnaire de widgets.
        
        """
        if not widgetkey:
            return
        if isinstance(widgetkey, GroupKey):
            return 'QGroupBox'
        if isinstance(widgetkey, PlusButtonKey):
            return 'QToolButton'
        if widgetkey.datatype.n3(self.nsm) == 'xsd:boolean':
            return 'QCheckBox'
        if widgetkey.is_read_only:
            return 'QLabel'
        if not widgetkey.datatype:
            if value_source:
                return 'QComboBox'
            else:
                return 'QLineEdit'
        if widgetkey.datatype.n3(self.nsm) in ('rdf:langString', 'xsd:string'):
            if widgetkey.is_long_text:
                return 'QTextEdit'
            return 'QLineEdit'
        d = {
            'xsd:date': 'QDateEdit',
            'xsd:dateTime': 'QDateTimeEdit',
            'xsd:time': 'QTimeEdit',
            'gsp:wktLiteral': 'QTextEdit'
            }
        return d.get(widgetkey.datatype.n3(self.nsm), 'QLineEdit')
    
    def type_validator(self, widgetkey):
        """S'il y a lieu, renvoie le validateur adapté pour une clé.
        
        Parameters
        ----------
        widgetkey : WidgetKey
            Une clé de dictionnaire de widgets.
        
        """
        if not widgetkey:
            return
        d = {
            'xsd:integer': 'QIntValidator',
            'xsd:decimal': 'QDoubleValidator',
            'xsd:float': 'QDoubleValidator',
            'xsd:double': 'QDoubleValidator'
            }
        return d.get(widgetkey.datatype.n3(self.nsm))
    
    def register_value(self, widgetkey, value):
        """Prépare et enregistre une valeur dans une clé-valeur du dictionnaire de widgets.
        
        Parameters
        ----------
        widgetkey : ValueKey
            Une clé de dictionnaire de widgets.
        value : str
            La valeur, exprimée sous la forme d'une chaîne de caractères.
        
        """
        if widgetkey.is_read_only or not isinstance(widgetkey, ValueKey):
            return
        if not value:
            widgetkey.value = None
            return
        if widgetkey.transform == 'email':
            value = owlthing_from_email(value)
        if widgetkey.transform == 'phone':
            value = owlthing_from_tel(value)
        if widgetkey.value_language:
            widgetkey.value = Literal(value, lang=self.value_language)
            return 
        if widgetkey.datatype:
            widgetkey.value = Literal(value, datatype=self.datatype)
            return 
        if widgetkey.value_source:
            res = Thesaurus.concept_iri((widgetkey.value_source, \
                widgetkey.main_language), value)
            if res:
                widgetkey.value = res
                return
        f = forbidden_char(value)
        if f:
            raise ForbiddenOperation(widgetkey, "Le caractère '{}' " \
                "n'est pas autorisé dans un IRI.".format(f))
        widgetkey.value = URIRef(value)
    
    def str_value(self, widgetkey):
        """Renvoie la valeur d'une clé-valeur du dictionnaire de widgets sous forme d'une chaîne de caractères.
        
        Si la clé est en lecture seule, la fonction renvoie, s'il y a lieu,
        un fragment HTML avec un hyperlien.
        
        Parameters
        ----------
        widgetkey : ValueKey
            Une clé de dictionnaire de widgets.
        
        Returns
        -------
        str
        
        """
        value = widgetkey.value
        if not value:
            return
        str_value = None
        if widgetkey.transform == 'email':
            str_value = email_from_owlthing(value)
        elif widgetkey.transform == 'phone':
            str_value = tel_from_owlthing(value)
        elif widgetkey.value_source:
            str_value = Thesaurus.concept_str((widgetkey.value_source, \
                widgetkey.main_language), value)
        else:
            str_value = str(value)
        if widgetkey.is_read_only:
            if widgetkey.value_source:
                str_value = text_with_link(
                    str_value,
                    Thesaurus.concept_link((widgetkey.value_source, \
                        widgetkey.main_language), value) or value
                    )
            elif isinstance(value, URIRef):
                str_value = text_with_link(str_value, value)
        return str_value

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
    anyiri : URIRef
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
    thing_iri : URIRef
        Objet de type URIref supposé correspondre à une adresse
        mél (classe RDF owl:Thing).

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
    URIRef
        Un objet de type URIRef (rdflib.term.URIRef) respectant grosso
        modo le schéma officiel des URI pour les adresses mél :
        mailto:<email>.

    Examples
    --------
    >>> owlthing_from_email('jon.snow@the-wall.we')
    rdflib.term.URIRef('mailto:jon.snow@the-wall.we')
    
    """
    email_str = re.sub('^mailto[:]', '', email_str)
    f = forbidden_char(email_str)
    if f:
        raise ValueError(widgetkey, "Le caractère '{}' " \
            "de l'adresse '{}' n'est pas autorisé dans " \
            'un IRI.'.format(f, email_str))
    if email_str:
        return URIRef('mailto:' + email_str)

def tel_from_owlthing(thing_iri):
    """Renvoie la transcription sous forme de chaîne de caractères d'un IRI représentant un numéro de téléphone.

    Contrairement à owlthing_from_tel, cette fonction très basique
    ne standardise pas la forme du numéro de téléphone. Elle se contente
    de retirer le préfixe "tel:" s'il était présent.

    Parameters
    ----------
    thing_iri : URIRef
        Objet de type URIref supposé correspondre à un numéro
        de téléphone (classe RDF owl:Thing).

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
    il est standardisé sous la forme <tel:+33-x-xx-xx-xx-xx>.

    Parameters
    ----------
    tel_str : str
        Une chaîne de caractère supposée correspondre à un numéro de téléphone.
    add_fr_prefix : bool, default True
        True si la fonction doit tenter de transformer les numéros de téléphone
        français locaux ou présumés comme tels (un zéro suivi de neuf chiffres)
        en numéros globaux ("+33" suivi des neuf chiffres). True par défaut.

    Returns
    -------
    URIRef
        Un objet de type URIRef (rdflib.term.URIRef) respectant grosso
        modo le schéma officiel des URI pour les numéros de téléphone :
        tel:<phonenumber>.

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
            raise ValueError(widgetkey, "Le caractère '{}' " \
                "du numéro de téléphone '{}' n'est pas autorisé dans " \
                'un IRI.'.format(f, tel_str))
    if tel:
        return URIRef('tel:' + tel)

def sort_by_language(litlist, language):
    """Trie une liste pour que les valeurs dans la langue demandée arrivent en tête.
    
    Parameters
    ----------
    litlist : list of rdflib.term.Literal
        Une liste de valeurs litérales, présumées de type
        ``xsd:string``.
    language : str
        La langue à privilégier pour les traductions.
    
    Notes
    -----
    Les valeurs de la langue désirée sont placées en premier,
    puis les traductions françaises, puis les autres éléments.
    
    La liste est triée sur place, la fonction ne renvoie
    donc rien.

    """
    litlist.sort(key=lambda v: \
        0 if isinstance(v, Literal) and v.language == language else \
        1 if isinstance(v, Literal) and v.language == 'fr' else \
        2)
