"""Dictionnaires de widgets.
"""
from rdflib.namespace import NamespaceManager

from plume.rdf.widgetkey import WidgetKey, ValueKey, GroupOfPropertiesKey, \
    GroupOfValuesKey, TranslationGroupKey, TranslationButtonKey, PlusButtonKey, \
    ObjectKey
from plume.rdf.internaldict import InternalDict
from plume.rdf.actionsbook import ActionsBook
from plume.rdf.exceptions import IntegrityBreach, MissingParameter, ForbiddenOperation, \
    UnknownParameterValue
from plume.rdf.thesaurus import Thesaurus
    

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
    nsm : rdflib.namespace.NamespaceManager
        Le gestionnaire d'espaces de nommage permettant de résoudre
        tous les préfixes du dictionnaire. On pourra initialiser l'attribut
        avec le gestionnaire du schéma SHACL, et le compléter ensuite
        si besoin.
    
    Attributes
    ----------
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
    root : RootKey
        La clé racine du dictionnaire, dont toutes les autres sont des
        descendantes.
    nsm : rdflib.namespace.NamespaceManager
        Le gestionnaire d'espaces de nommage permettant de résoudre
        tous les préfixes du dictionnaire.
    
    """
    
    def __init__(self, nsm, mode='edit', translation=False, language='fr',
        langList=['fr', 'en'], readHideBlank=True, editHideUnlisted=False,
        readHideUnlisted=True, editOnlyCurrentLanguage=False,
        readOnlyCurrentLanguage=True, labelLengthLimit=25, valueLengthLimit=65,
        textEditRowSpan=6):
        if mode in ('edit', 'read'):
            # 'search' n'est pas accepté pour le moment
            self.mode = mode
        else:
            raise UnknownParameterValue('mode', mode)
            
        if isinstance(language, str):
            self.language = language
        else:
            raise TypeError('`language` devrait être une chaîne de caractères.')
            
        if not isinstance(langList, list):
            raise TypeError('`langList` devrait être une liste.')
        elif not language in langList:
            raise ValueError('`language` devrait être un des items de `langList`.')
        else:
            self.langList = langList
        
        if not isinstance(labelLengthLimit, int):
            raise TypeError('`labelLengthLimit` devrait être un nombre entier.')
        else:
            self.labelLengthLimit = labelLengthLimit
        if not isinstance(valueLengthLimit, int):
            raise TypeError('`valueLengthLimit` devrait être un nombre entier.')
        else:
            self.valueLengthLimit = valueLengthLimit
        if not isinstance(textEditRowSpan, int):
            raise TypeError('`textEditRowSpan` devrait être un nombre entier.')
        else:
            self.textEditRowSpan = textEditRowSpan
        
        self.nsm = nsm
        self.translation = translation and self.edit
        self.readHideBlank = readHideBlank and not self.edit
        self.readHideUnlisted = readHideUnlisted and not self.edit
        self.readOnlyCurrentLanguage = readOnlyCurrentLanguage and not self.edit
        self.editHideUnlisted = editHideUnlisted and self.edit
        self.editOnlyCurrentLanguage = editHideUnlisted and self.edit
        self.root = None

    @property
    def edit(self):
        """Le dictionnaire est-il généré pour l'édition ?
        
        Returns
        -------
        bool
        
        """
        returns (mode == 'edit')


    def _build_dict(self, metagraph, shape, vocabulary, path, class_iri,
        parent, subject, template_is_empty, shallow_template, shallow_data):
        
        # identification de la forme du schéma SHACL qui décrit la
        # classe cible :
        shape_iri = shape.shape_iri_from_class(class_iri)
        if not shape_iri:
            raise IntegrityBreach("La classe '{}' n'est pas répertoriée dans le " \
                "schéma SHACL".format(class_iri))
        
        # ------ Boucle sur les catégories ------
        for property_iri in shape.objects(
            shape_iri,
            URIRef("http://www.w3.org/ns/shacl#property")
            ):
            
            # récupération des informations relatives
            # à la catégorie dans le schéma SHACL
            kwargs = shape.read_property(shape_iri, property_iri)
            kwargs['parent'] = parent
            kwargs['is_mandatory'] = kwargs['min'] and int(kwargs['min']) > 0
            
            new_path = ( path + " / " if path else '') + kwargs['predicate'].n3(self.nsm)
            kind = kwargs['kind'].n3(self.nsm)
            one_language = None
            values = None
            
            multilingual = bool(kwargs['unilang'])
            multiple = (kwargs['max'] is None or int(kwargs['max']) > 1) and not multilingual
            
            # ------ Récupération des valeurs ------
            # cas d'une propriété dont les valeurs sont mises à
            # jour à partir d'informations disponibles côté serveur
            if shallow_data and new_path in shallow_data:
                values = shallow_data[new_path].copy() or []
                del shallow_data[new_path]
                
            # sinon, on extrait la ou les valeurs éventuellement
            # renseignées dans le graphe pour cette catégorie
            # et le sujet considéré
            values = [ o for o in metagraph.objects(subject, predicate) ]

            # exclusion des catégories qui ne sont pas prévues par
            # le modèle, ne sont pas considérées comme obligatoires
            # par shape et n'ont pas de valeur renseignée.
            # les catégories obligatoires de shape sont affichées
            # quoi qu'il arrive en mode édition
            # les catégories sans valeur sont éliminées indépendemment
            # du modèle en mode lecture quand readHideBlank vaut True
            if values in (None, [], [None]) and (self.readHideBlank \
                or (not template_is_empty and not (new_path in shallow_template) \
                    and not (self.edit and kwargs['is_mandatory'])) \
                ):
                continue
            # s'il y a une valeur, mais que
            # read/editHideUnlisted vaut True et que la catégorie n'est
            # pas prévue par le modèle, on poursuit le traitement
            # pour ne pas perdre la valeur, mais on ne créera
            # pas de widget. Les catégories obligatoires de shape sont
            # affichées quoi qu'il arrive
            elif (self.editHideUnlisted or self.readHideUnlisted) \
                and not template_is_empty and not new_path in shallow_template \
                and not kwargs['is_mandatory']:
                kwargs['is_ghost'] = True
            
            values = values or [None]
            
            # ------ Extraction des informations du modèle et choix de l'onglet ------
            t = dict()
            if new_path in shallow_template:
                t = shallow_template[new_path]
                shallow_template[new_path]['done'] = True
                # choix du bon onglet (évidemment juste
                # pour les catégories de premier niveau)
                if isinstance(parent, RootKey):
                    tabkey = parent.search_tab(t.get('tab name'))
                    # renvoie le premier onglet si le nom est None
                    kwargs['parent'] = tabkey
                kwargs['order_idx'] = (t.get('order', 9999), kwargs['shape_order'])
            elif isinstance(parent, RootKey) and not template_is_empty:
                # les métadonnées hors modèle non masquées
                # de premier niveau iront dans l'onglet "Autres".
                tabkey = parent.search_tab('Autres')
                kwargs['parent'] = tabkey
            elif isinstance(parent, RootKey):
                # en l'absence de modèle, on prend juste le
                # premier onglet
                tabkey = parent.search_tab()
                kwargs['parent'] = tabkey

            # si seules les métadonnées dans la langue
            # principale doivent être affichées et qu'aucune valeur n'est
            # disponible dans cette langue, on prendra le parti d'afficher
            # arbitrairement les valeurs de la première langue venue
            if ( (not self.edit and self.readOnlyCurrentLanguage) or
                   ( self.edit and self.editOnlyCurrentLanguage and not translation ) ) \
                and not any(not isinstance(v, Literal) or v.language in (None, language) \
                    for v in values):
                    for v in values:
                        if isinstance(v, Literal) and v.language:
                            one_language = v.language
                            break

            # ------ Multi-valeurs ------
            if len(values) > 1 or (((self.translation and multilingual) \
                or multiple) and not self.readHideBlank):
                
                if self.translation and multilingual:
                    groupkey = TranslationGroupKey(**kwargs)
                else:
                    groupkey = GroupOfValuesKey(**kwargs)
                self[groupkey] = InternalDict()
                # les widgets référencés ensuite auront ce groupe
                # pour parent
                kwargs['parent'] = groupkey
                # ajustement des attributs de la clé selon le modèle
                groupkey.update(t, exclude_none=True)



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
        if widgetkey.xsdtype.n3(self.nsm) == 'xsd:boolean':
            return 'QCheckBox'
        if widgetkey.is_read_only:
            return 'QLabel'
        if not widgetkey.xsdtype:
            if value_source:
                return 'QComboBox'
            else:
                return 'QLineEdit'
        if widgetkey.xsdtype.n3(self.nsm) in ('rdf:langString', 'xsd:string'):
            if widgetkey.is_long_text:
                return 'QTextEdit'
            return 'QLineEdit'
        d = {
            'xsd:date': 'QDateEdit',
            'xsd:dateTime': 'QDateTimeEdit',
            'xsd:time': 'QTimeEdit',
            'gsp:wktLiteral': 'QTextEdit'
            }
        return d.get(widgetkey.xsdtype.n3(self.nsm), 'QLineEdit')
    
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
        return d.get(widgetkey.xsdtype.n3(self.nsm))
    
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
        if widgetkey.xsdtype:
            widgetkey.value = Literal(value, datatype=self.xsdtype)
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

