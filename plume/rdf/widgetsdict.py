"""Dictionnaires de widgets.

Ce module permet de générer des dictionnaires de widgets
(:py:class:`WidgetsDict`) rassemblant et structurant
toutes les informations nécessaires à la création d'un
formulaire de consultation ou saisie des métadonnées.

Création d'un dictionnaire vierge:

    >>> widgetsdict = WidgetDict()
    
Cf. classe :py:class:`WidgetsDict` pour les informations
pouvant être fournies en argument : graphe contenant les
métadonnées de l'objet PostgreSQL, modèle de formulaire,
descriptifs des champs...

"""

from plume.rdf.rdflib import Literal, URIRef, BNode, NamespaceManager
from plume.rdf.utils import sort_by_language, DatasetId, forbidden_char, \
    owlthing_from_email, owlthing_from_tel, text_with_link, email_from_owlthing, \
    tel_from_owlthing, duration_from_int, int_from_duration, str_from_duration, \
    str_from_datetime, str_from_date, datetime_from_str, date_from_str
from plume.rdf.widgetkey import WidgetKey, ValueKey, GroupOfPropertiesKey, \
    GroupOfValuesKey, TranslationGroupKey, TranslationButtonKey, \
    PlusButtonKey, ObjectKey, RootKey, TabKey, GroupKey
from plume.rdf.internaldict import InternalDict
from plume.rdf.actionsbook import ActionsBook
from plume.rdf.exceptions import IntegrityBreach, MissingParameter, \
    UnknownParameterValue, ForbiddenOperation
from plume.rdf.thesaurus import Thesaurus
from plume.rdf.namespaces import PlumeNamespaceManager, SH, RDF, XSD, SNUM, GSP
from plume.rdf.properties import PlumeProperty, class_properties

class WidgetsDict(dict):
    """Classe pour les dictionnaires de widgets.
    
    Parameters
    ----------
    metagraph : plume.rdf.metagraph.Metagraph, optional
        Le graphe RDF contenant les métadonnées de l'objet PostgreSQL
        considéré.
    template : plume.pg.template.TemplateDict, optional
        Un dictionnaire contenant la configuration d'un modèle local
        de formulaire de consultation/saisie des métadonnées.
    data : dict, optional
        Un dictionnaire dont les clés sont des chemins N3 de catégories
        de métadonnées, et les valeurs des listes contenant la ou les
        valeurs à associer à ces catégories, à la place de celles de
        `metagraph`. `data` sert à notamment à mettre à jour certaines
        métadonnées à partir de sources externes, par exemple des
        informations calculées par des requêtes sur le serveur.
        Si `data` contient la clé ``dct:identifier``, sa valeur deviendra
        l'identifiant du jeu de données, sous réserve qu'il s'agisse d'un
        UUID valide.
    columns : list(tuple(str, str)), optional
        Une liste de tuples - un par champ de la table ou vue PostgreSQL
        (si l'objet considéré n'est pas un schéma) -, contenant les noms
        des champs et leurs descriptifs.
    mode : {'edit', 'read'}, default 'edit'
        Indique si le dictionnaire est généré pour le mode édition
        (``'edit'``), le mode lecture (``'read'``). Le mode détermine les
        actions pouvant être exécutées sur le dictionnaire par la suite.
    translation : bool, default False
        Paramètre utilisateur qui indique si les widgets de traduction
        doivent être affichés. Sa valeur contribue à déterminer les actions
        pouvant être exécutées sur le dictionnaire. `translation` sera
        silencieusement corrigé à ``False`` si `mode` n'est pas `'edit'`,
        car l'ajout de traductions n'est évidemment possible qu'en mode
        édition.
    langList : list(str) or tuple(str), default ('fr', 'en')
        Liste des langues autorisées pour les traductions. Les langues
        doivent être triées par priorité (langues à privilégier en
        premier).
    language : str, optional
        Langue principale de rédaction des métadonnées.
        Si `language` n'est pas fourni ou n'appartient pas à `langList`,
        la première langue de `langList` tiendra lieu de langue principale.
    
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
    translation : bool
        ``True`` pour un dictionnaire comportant des fonctionnalités de
        traduction, ``False`` sinon. Certaines méthodes ne peuvent être
        utilisées que sur un dictionnaire dont l'attribut `translation`
        vaut ``True``.
    langlist : tuple(str)
        Tuple des langues autorisées pour les traductions, ordonné
        de manière à ce que la langue principale éventuellement
        fournie à l'initialisation soit la première valeur (et
        préservant pour le reste l'ordre d'origine du paramètre
        `langList`).
    hideBlank : bool
        Les métadonnées sans valeur sont-elles masquées ?
    hideUnlisted : bool
        Les métadonnées avec valeur mais hors modèle sont-elles masquées ?
    onlyCurrentLanguage : bool
        Les métadonnées qui ne sont pas dans la langue principale
        (`language`) sont-elles masquées ?
    textEditRowSpan : int
        Hauteur par défaut des widgets de saisie de texte multi-lignes,
        en nombre de lignes.
    valueLengthLimit : int
        Si la longueur d'une valeur textuelle (nombre de caractères)
        est supérieure à `valueLengthLimit`, elle est affichée sur
        plusieurs lignes.
    labelLengthLimit : int
        Si la longueur d'une étiquette (nombre de caractères) est
        supérieure à `labelLengthLimit`, elle est affichée au-dessus
        du widget de saisie.
    
    Other Parameters
    ----------------
    readHideBlank : bool, default True
        Les champs vide du formulaire doivent-ils être masqués en mode
        lecture ?
    editHideUnlisted : bool, default False
        Lorsqu'un modèle (`template`) est fourni, les champs non référencés
        par celui-ci doivent-ils être masqués en mode édition même s'ils
        contiennent une valeur ? Lorsque ce paramètre vaut ``False``, les
        champs non référencés apparaissent dans l'onglet *Autres* du
        formulaire.
    readHideUnlisted : bool, default True
        Lorsqu'un modèle (`template`) est fourni, les champs non référencés
        par celui-ci doivent-ils être masqués en mode lecture même s'ils
        contiennent une valeur ? Lorsque ce paramètre vaut ``False``, les
        champs non référencés apparaissent dans l'onglet *Autres* du
        formulaire.
    editOnlyCurrentLanguage : bool, default False
        Hors mode traduction et pour les propriétés appelant des traductions
        (type ``rdf:langString``), les valeurs qui ne sont pas dans la
        langue principale (`language`) doivent-elles être masquées en mode
        édition ? S'il n'existe aucune traduction pour la langue demandée,
        une valeur dans une autre langue est affichée, avec priorisation
        des langues selon l'ordre de `langList`.
    readOnlyCurrentLanguage : bool, default True
        Pour les propriétés appelant des traductions (type ``rdf:langString``),
        les valeurs qui ne sont pas dans la langue principale (`language`)
        doivent-elles être masquées en mode lecture ? S'il n'existe aucune
        traduction pour la langue demandée, une valeur dans une autre langue
        est affichée, avec priorisation des langues selon l'ordre de `langList`.
    labelLengthLimit : int, default 25
        Si la longueur d'une étiquette (nombre de caractères) est
        supérieure à `labelLengthLimit`, elle est affichée au-dessus
        du widget de saisie.
    valueLengthLimit : int, default 65
        Si la longueur d'une valeur textuelle (nombre de caractères)
        est supérieure à `valueLengthLimit`, elle est affichée sur
        plusieurs lignes.
    textEditRowSpan : int, default 6
        Hauteur par défaut des widgets de saisie de texte multi-lignes,
        en nombre de lignes. C'est la valeur utilisée quand le modèle local
        ou le schéma des métadonnées communes ne définit pas de paramétrage
        spécifique.
    
    """
    
    def __init__(self, metagraph=None, template=None, data=None, columns=None,
        mode=None, translation=False, langList=None, language=None,
        readHideBlank=True, editHideUnlisted=False, readHideUnlisted=True,
        editOnlyCurrentLanguage=False, readOnlyCurrentLanguage=True,
        labelLengthLimit=None, valueLengthLimit=None, textEditRowSpan=None):
        
        # ------ Paramètres utilisateur ------
        self.mode = mode if mode in ('edit', 'read') else 'edit'
        self.langlist = tuple(langList) if langList \
            and isinstance(langList, (list, tuple)) else ('fr', 'en')
        if not language in self.langlist:
            language = None
        self.labelLengthLimit = labelLengthLimit if labelLengthLimit \
            and isinstance(labelLengthLimit, int) else 25
        self.valueLengthLimit = valueLengthLimit if valueLengthLimit \
            and isinstance(valueLengthLimit, int) else 65
        self.textEditRowSpan = textEditRowSpan if textEditRowSpan \
            and isinstance(textEditRowSpan, int) else 6
        self.translation = bool(translation) and self.edit
        self.hideBlank = bool(readHideBlank) and not self.edit
        self.hideUnlisted = (bool(readHideUnlisted) and not self.edit) \
            or (bool(editHideUnlisted) and self.edit)
        self.onlyCurrentLanguage = (bool(readOnlyCurrentLanguage) and not self.edit) \
            or (bool(editOnlyCurrentLanguage) and self.edit and not self.translation)
        
        # ------ Racine ------
        # + gestion de l'identifiant
        self.root = None
        self.nsm = PlumeNamespaceManager()
        data = data or {}
        
        ident = data.get('dct:identifier') if data else None
        old_uuid = ident[0] if ident else None
        old_datasetid = metagraph.datasetid if metagraph else None
        self.root = RootKey(datasetid=old_datasetid)
        self.datasetid = DatasetId(old_uuid, old_datasetid)
        if self.edit:
            data['dct:identifier'] = [str(self.datasetid.uuid)]
        # à ce stade, on a nécessairement un UUID valide dans
        # l'attribut datasetid. Par contre, l'identifiant de la
        # clé racine est identique à celui du graphe et pas
        # nécessairement à self.datasetid.
        # On attend la fin de l'initialisation pour le remettre
        # en cohérence, sans quoi on ne pourrait pas récupérer le
        # contenu du graphe.
        
        # paramètres de configuration des clés
        WidgetKey.with_source_buttons = self.edit
        WidgetKey.with_unit_buttons = self.edit
        WidgetKey.with_language_buttons = self.translation
        WidgetKey.with_geo_buttons = True
        # NB: les boutons d'aide à la saisie des géométries
        # sont autorisés en mode lecture. Le fait que la clé
        # soit en lecture seule limitera les fonctionnalités
        # disponibles à celles qui ont trait à la visualisation.
        WidgetKey.langlist = list(self.langlist)
        self.root.main_language = language
        self.langlist = tuple(WidgetKey.langlist)
        # NB: pour avoir la liste triée dans le bon ordre
        WidgetKey.max_rowspan = 30 if self.edit else 1
        
        # ------ Onglets ------
        if template and template.tabs:
            i = 1
            for label in template.tabs:
                tabkey = TabKey(parent=self.root, label=label,
                    order_idx=(i,))
                i += 1
            # s'il n'existe pas déjà, on ajoute un
            # onglet "Autres" pour les catégories hors
            # modèle
            if not 'Autres' in template.tabs:
                tabkey = TabKey(parent=self.root, label='Autres',
                    order_idx=(9999,))
        else:
            tabkey = TabKey(parent=self.root, label='Général', order_idx=(0,))
            # et on ajoute un onglet "Autres"
            # pour les catégories hors modèle
            tabkey = TabKey(parent=self.root, label='Autres', order_idx=(9999,))
        
        # ------ Colonnes de la table ------
        if columns:
            tabkey = TabKey(parent=self.root, label='Champs', order_idx=(9998,))
            for label, value in columns:
                valkey = ValueKey(parent=tabkey, label=label, value=Literal(value),
                    is_long_text=True, description='Description du champ',
                    rowspan=self.textEditRowSpan, predicate=SNUM.column,
                    do_not_save=True, independant_label=True,
                    is_read_only=not self.edit)
        
        # ------ Construction récursive ------
        self._build_tree(parent=self.root, metagraph=metagraph, \
            template=template, data=data)
        
        # ------ Nettoyage des groupes vides ------
        self.root.clean()
        
        # ------- Mise à jour de l'identifiant ------
        # dans l'hypothèse où celui de data et celui de metagraph
        # auraient été différents
        self.root.node = self.datasetid
        
        # ------ Calcul des dictionnaires internes ------
        # et référencement dans le dictionnaire
        for widgetkey in self.root.tree_keys():
            self.internalize(widgetkey)

    def _build_tree(self, parent, metagraph=None, template=None, data=None):
        # ------ Constitution de la liste des catégories ------
        # catégories communes de la classe :
        properties, predicates = class_properties(rdfclass=parent.rdfclass,
            nsm=self.nsm, base_path=parent.path, template=template)
        if isinstance(parent, RootKey):
            # catégories locales:
            if template:
                for n3_path in template.local.keys():
                    p = PlumeProperty(origin='local', nsm=self.nsm,
                        n3_path=n3_path, template=template)
                    properties.append(p)
                    predicates.append(p.predicate)
            # catégories non référencées
            # en principe il s'agit simplement de catégories locales
            # qui ne sont pas référencées par le modèle considéré
            if metagraph:
                for predicate, o in metagraph.predicate_objects(parent.node):
                    if not predicate in predicates and not predicate == RDF.type:
                        properties.append(PlumeProperty(origin='unknown',
                            nsm=self.nsm, predicate=predicate))   
        
        # ------ Boucle sur les catégories ------
        for prop in properties:
            prop_dict = prop.prop_dict
            prop_dict['parent'] = parent
            kind = prop_dict.get('kind', SH.Literal)
            multilingual = bool(prop_dict.get('unilang')) \
                and prop_dict.get('datatype') == RDF.langString \
                and self.translation
            multiple = bool(prop_dict.get('is_multiple')) and self.edit \
                and not bool(prop_dict.get('unilang'))
            
            if not self.edit:
                prop_dict['is_read_only'] = True
            
            # ------ Récupération des valeurs ------
            # cas d'une propriété dont les valeurs sont mises à
            # jour à partir d'informations disponibles côté serveur
            if data and prop.n3_path in data:
                values = data[prop.n3_path].copy() or [None]
                if values != [None]:
                    prop_dict['delayed'] = True
                    # NB: permettra la mise à jour silencieuse
                    # de propriétés non affichées
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
            # et que la catégorie n'est pas prévue par le modèle, on
            # poursuit le traitement pour ne pas perdre la valeur, mais
            # on ne créera pas de widget.
            # Les catégories obligatoires de shape sont affichées quoi
            # qu'il arrive.
            if values != [None] and prop.unlisted and self.hideUnlisted \
                and not prop_dict.get('is_mandatory'):
                prop_dict['is_ghost'] = True

            # ------ Choix de l'onglet ------
            # pour les catégories de premier niveau
            if isinstance(parent, RootKey):
                if prop.unlisted:
                    # les métadonnées hors modèle iront dans
                    # l'onglet "Autres".
                    prop_dict['parent'] = parent.search_tab('Autres')
                else:
                    tab_label = prop_dict.get('tab')
                    prop_dict['parent'] = parent.search_tab(tab_label)
                    # NB : renvoie le premier onglet si l'argument est None

            # ------ Affichage mono-langue ------
            # si seules les métadonnées dans la langue principale
            # doivent être affichées, on trie la liste pour qu'elles soient
            # en tête. Dans tous les cas, la première valeur sera
            # affichées, les autres seront des fantômes si elles
            # ne sont pas dans la bonne langue.
            if prop_dict.get('datatype') == RDF.langString \
                and self.onlyCurrentLanguage:
                sort_by_language(values, self.langlist)

            # ------ Multi-valeurs ------
            # création d'un groupe de valeurs ou de traduction
            # rassemblant les valeurs actuelles et futures
            if len(values) > 1 or multilingual or multiple:
                if not self.edit:
                    prop_dict['with_minus_buttons'] = False
                if multilingual and not prop_dict.get('is_ghost'):
                    groupkey = TranslationGroupKey(**prop_dict)
                else:
                    groupkey = GroupOfValuesKey(**prop_dict)
                # les widgets référencés ensuite auront ce groupe pour parent
                prop_dict['parent'] = groupkey
            
            # ------ Boucle sur les valeurs ------
            for value in values:
                val_dict = prop_dict.copy()
            
                # ------ Affichage mono-langue (suite) ------
                if val_dict.get('datatype') == RDF.langString \
                    and self.onlyCurrentLanguage:
                    if value and prop_dict['parent'].has_real_children and \
                        (not isinstance(value, Literal) or \
                        value.language != self.main_language):
                        val_dict['is_ghost'] = True
                
                # ------ Cas d'un noeud anonyme -------
                if kind in (SH.BlankNode, SH.BlankNodeOrIRI):
                    if isinstance(value, BNode):
                        val_dict['node'] = value
                    # NB: on doit conserver les noeuds anonymes, sans quoi
                    # il ne serait plus possible de récupérer les valeurs
                    # dans le graphe
                    nodekey = GroupOfPropertiesKey(**val_dict)
                    self._build_tree(parent=nodekey, metagraph=metagraph,
                        template=template, data=data)
                    if kind == SH.BlankNodeOrIRI:
                        val_dict['m_twin'] = nodekey
                        val_dict['is_hidden_m'] = isinstance(value, BNode)
                    
                # ------ Cas d'une valeur litéral ou d'un IRI ------
                if kind in (SH.BlankNodeOrIRI, SH.Literal, SH.IRI):
                    if isinstance(value, BNode):
                        value = None
                    
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
                
                    if isinstance(value, (URIRef, Literal)):
                        # source de la valeur
                        if val_dict.get('sources') and isinstance(value, URIRef):
                            val_dict['value_source'] = Thesaurus.concept_source(value)
                        # value_language est déduit de value à l'initialisation
                        # de la clé, le cas échéant
                        val_dict['value'] = value
                    
                    valkey = ValueKey(**val_dict)
                    
                    if value is not None and not isinstance(value, (URIRef, Literal)):
                        # cas d'une valeur issue de data, par exemple.
                        # on saisit la valeur après la création de la clé,
                        # pour pouvoir la dé-sérialiser en fonction des
                        # attributs de la clé
                        self.update_value(valkey, value, override=True)
                
            # ------ Bouton ------
            if multilingual or multiple:
                buttonkey = TranslationButtonKey(**prop_dict) if multilingual \
                    else PlusButtonKey(**prop_dict)

    @property
    def edit(self):
        """bool: Le dictionnaire est-il généré pour l'édition ?
        
        """
        return (self.mode == 'edit')

    @property
    def main_language(self):
        """str: Language principale de saisie.
        
        Raises
        ------
        IntegrityBreach
            Lorsque l'attribut :py:attr:`WidgetsDict.langlist` ne
            contient aucune valeur.
        
        """
        if self.langlist:
            return self.langlist[0]
        else:
            raise IntegrityBreach('La liste des langues autorisées est vide, ' \
                'impossible de déterminer la langue principale de saisie.')

    def parent_grid(self, widgetkey):
        """Renvoie la grille dans laquelle doit être placé le widget de la clé widgetkey.
        
        Parameters
        ----------
        widgetkey : plume.rdf.widgetkey.WidgetKey
            Une clé du dictionnaire de widgets.
        
        Returns
        -------
        QGridLayout
            Si la clé existe, que l'enregistrement a un parent et que la grille de
            celui-ci a été créée, ladite grille. Sinon None.
        
        """
        if widgetkey.parent:
            return self[widgetkey.parent].get('grid widget')

    def internalize(self, widgetkey):
        """Retranscrit les attributs d'une clé dans le dictionnaire interne associé.
        
        Si la clé n'était pas référencée dans le dictionnaire de widgets,
        cette méthode se charge de la référencer.
        
        Parameters
        ----------
        widgetkey : plume.rdf.widgetkey.WidgetKey
            Une clé du dictionnaire de widgets. Si la clé n'est pas encore
            référencée dans le dictionnaire, elle le sera.
        
        Raises
        ------
        IntegrityBreach
            En cas de tentative d'utilisation de cette méthode sur une clé
            fantôme.
        
        """
        if not widgetkey:
            raise IntegrityBreach('Les clés fantômes ne doivent pas être ' \
                'référencées dans le dictionnaire de widgets.', widgetkey=widgetkey)
        
        if widgetkey in self:
            internaldict = self[widgetkey]
        else:
            internaldict = InternalDict()
            self[widgetkey] = internaldict
   
        internaldict['object'] = widgetkey.key_object
        internaldict['main widget type'] = self.widget_type(widgetkey)
        
        if isinstance(widgetkey, RootKey):
            return
            
        if isinstance(widgetkey, (GroupKey, ObjectKey)):
            internaldict['label'] = widgetkey.label
            
        if isinstance(widgetkey, TabKey):
            return
        
        internaldict['help text'] = widgetkey.description
        internaldict['hidden'] = widgetkey.is_hidden
        internaldict['multiple sources'] = widgetkey.has_source_button
        internaldict['has label'] = widgetkey.has_label
        
        if isinstance(widgetkey, ValueKey):
            internaldict['placeholder text'] = widgetkey.placeholder
            internaldict['input mask'] = widgetkey.input_mask
            internaldict['is mandatory'] = widgetkey.is_mandatory
            internaldict['regex validator pattern'] = widgetkey.regex_validator
            internaldict['regex validator flags'] = widgetkey.regex_validator_flags
            internaldict['type validator'] = self.type_validator(widgetkey)
            internaldict['read only'] = widgetkey.is_read_only
            internaldict['value'] = self.str_value(widgetkey)
            internaldict['language value'] = widgetkey.value_language
            if widgetkey.has_language_button:
                internaldict['authorized languages'] = widgetkey.available_languages.copy()
                if not widgetkey.value_language in widgetkey.available_languages:
                    internaldict['authorized languages'].insert(0, widgetkey.value_language)
            if not widgetkey.has_source_button and widgetkey.value_source \
                and not widgetkey.is_read_only:
                # cas où il n'y a qu'une seule source, le multi-sources
                # est traité juste après
                internaldict['thesaurus values'] = Thesaurus.get_values(
                    (widgetkey.value_source, self.langlist))
            if widgetkey.has_unit_button:
                internaldict['units'] = widgetkey.units.copy()
                internaldict['current unit'] = widgetkey.value_unit
            if widgetkey.has_geo_button:
                internaldict['geo tools'] = widgetkey.geo_tools

        if isinstance(widgetkey, ObjectKey):
            internaldict['has minus button'] = widgetkey.has_minus_button
            internaldict['hide minus button'] = widgetkey.has_minus_button \
                and widgetkey.is_single_child
            if widgetkey.has_source_button:
                if widgetkey.sources:
                    internaldict['sources'] = [Thesaurus.get_label((s, self.langlist)) \
                        for s in widgetkey.sources]
                    if isinstance(widgetkey, ValueKey):
                        if widgetkey.value_source:
                            internaldict['current source'] = Thesaurus.get_label(
                                (widgetkey.value_source, self.langlist))
                            internaldict['thesaurus values'] = Thesaurus.get_values(
                                (widgetkey.value_source, self.langlist))
                        else:
                            internaldict['current source'] = '< non référencé >'
                            internaldict['sources'].insert(0, '< non référencé >')
                else:
                    internaldict['sources'] = ['< URI >']
                    if isinstance(widgetkey, ValueKey):
                        internaldict['current source'] = '< URI >'
                if widgetkey.m_twin:
                    internaldict['sources'].insert(0, '< manuel >')
                    if isinstance(widgetkey, GroupOfPropertiesKey): 
                        internaldict['current source'] = '< manuel >'


    def widget_placement(self, widgetkey, kind):
        """Renvoie les paramètres de placement du widget dans la grille.
        
        Parameters
        ----------
        widgetkey : plume.rdf.widgetkey.WidgetKey
            Une clé du dictionnaire de widgets.
        kind : {'main widget', 'minus widget', 'switch source widget', 'language widget', 'unit widget', 'geo widget', 'label widget'}
            Nature du widget considéré, soit plus prosaïquement le nom
            de la clé du dictionnaire interne qui le référence.
        
        Returns
        -------
        tuple
            Le placement dans le ``QGridLayout`` est défini par un tuple à
            quatre éléments :
            * ``[0]`` est l'indice de la ligne (paramètre ``row``) ;
            * ``[1]`` est l'indice de la colonne (paramètre ``column``) ;
            * ``[2]`` est le nombre de lignes occupées (paramètre ``rowSpan``) ;
            * ``[3]`` est le nombre de colonnes occupées (paramètre ``columnSpan``).
        
        Notes
        -----
        La fonction renvoie ``None`` pour une clé fantôme ou si la nature de widget
        donnée en argument n'est pas une valeur reconnue. Pour les clés-racines
        et les onglets, elle renvoie un tuple de zéros.
        
        """
        if not widgetkey or not widgetkey in self:
            return
        if kind == 'main widget':
            return widgetkey.placement or (0, 0, 0, 0)
        if kind == 'label widget':
            return widgetkey.label_placement
        if kind == 'language widget':
            return widgetkey.language_button_placement
        if kind == 'switch source widget':
            return widgetkey.source_button_placement
        if kind == 'unit widget':
            return widgetkey.unit_button_placement
        if kind == 'geo widget':
            return widgetkey.geo_button_placement
        if kind == 'minus widget':
            return widgetkey.minus_button_placement

    def dictisize_actionsbook(self, actionsbook=None):
        """Traduit un carnet d'actions en dictionnaire.
        
        Cette méthode assure également la mise à jour du dictionnaire
        de widgets.
        
        Parameters
        ----------
        actionsbook : plume.rdf.actionsbook.ActionsBook, optionnal
            Le carnet d'actions à traduire. Si aucune carnet n'est
            fournie, la méthode renvoie un dictionnaire dont toutes
            les clés ont pour valeur des listes vides.
        
        Returns
        -------
        dict
            Un dictionnaire avec les clés suivantes :
            
            * ``new keys`` : liste de nouvelles clés du dictionnaire de widgets
              à matérialiser (:py:class:`plume.rdf.widgetkey.WidgetKey`). Elles
              sont évidemment fournies dans le bon ordre, d'abord les clés parents
              puis les clés filles. Pour toutes ces clés, il sera nécessaire de
              générer les widgets, actions et menus, comme à la création initiale
              du dictionnaire.
            * ``widgets to show`` : liste de widgets (:py:class:`QtWidgets.QWidget`)
              à rendre visibles. Il s'agit a priori de widgets antérieurement masqués,
              mais ce n'est pas une règle absolue.
            * ``widgets to hide`` : liste de widgets (:py:class:`QtWidgets.QWidget`)
              à masquer. Il s'agit a priori de widgets antérieurement visibles, mais
              ce n'est pas une règle absolue.
            * ``widgets to delete`` : liste de widgets (:py:class:`QtWidgets.QWidget`)
              à détruire, incluant les grilles (:py:class:`QtWidgets.QGridLayout`).
            * ``actions to delete`` : liste d'actions (:py:class:`QtGui.QAction`) à
              détruire.
            * ``menus to delete`` : liste de menus (:py:class:`QtWidgets.QMenu`) à
              détruire.
            * ``language menu to update`` : liste de clés du dictionnaire de widgets
              (:py:class:`plume.rdf.widgetkey.WidgetKey`) pour lesquelles le menu
              du bouton de sélection de la langue doit être régénéré.
            * ``switch source menu to update`` : liste de clés du dictionnaire de
              widgets (:py:class:`plume.rdf.widgetkey.WidgetKey`) pour lesquelles le
              menu du bouton de sélection de la source doit être régénéré.
            * ``unit menu to update`` : liste de clés du dictionnaire de widgets
              (:py:class:`plume.rdf.widgetkey.WidgetKey`) pour lesquelles le
              menu du bouton de sélection de l'unité doit être régénéré.
            * ``concepts list to update`` : liste de clés du dictionnaire
              (:py:class:`plume.rdf.widgetkey.WidgetKey`) tel que le widget principal
              est un widget ``QComboBox`` dont la liste de termes doit être
              régénérée.
            * ``widgets to empty`` : liste de widgets (:py:class:`QtWidgets.QWidget`)
              dont le texte doit être effacé.
            * ``widgets to move`` : liste de tuples contenant les informations relatives
              à des widgets dont - parce qu'on a supprimé un widget antérieurement
              positionné au-dessus d'eux dans la grille - il faut à présent modifier
              la position.
              
              * ``[0]`` est la grille (:py:class:`QtWidgets.QGridLayout`) ;
              * ``[1]`` est le widget (:py:class:`QtWidgets.QWidget`) à déplacer ;
              * ``[2]`` est le nouveau numéro de ligne du widget dans la grille (paramètre
                ``row``) ;
              * ``[3]`` est l'indice (inchangé) de la colonne (paramètre ``column``) ;
              * ``[4]`` est le nombre (inchangé) de lignes occupées (paramètre ``rowSpan``) ;
              * ``[5]`` est le nombre (inchangé) de colonnes occupées (paramètre ``columnSpan``).
        
        """
        d = {k: [] for k in ('new keys', 'widgets to show', 'widgets to hide',
            'widgets to delete', 'actions to delete', 'menus to delete',
            'language menu to update', 'switch source menu to update',
            'unit menu to update', 'concepts list to update',
            'widgets to empty', 'widgets to move')}
        
        if not actionsbook:
            return d
        
        for widgetkey in actionsbook.create:
            self.internalize(widgetkey)
        for widgetkey in actionsbook.modified:
            self.internalize(widgetkey)
        
        d['new keys'] = actionsbook.create
        d['language menu to update'] = actionsbook.languages
        d['switch source menu to update'] = actionsbook.sources
        d['concepts list to update'] = actionsbook.thesaurus
        d['unit menu to update'] = actionsbook.units
        
        for widgetkey in actionsbook.show:
            d['widgets to show'] += self.list_widgets(widgetkey)
        
        for widgetkey in actionsbook.show_minus_button:
            w = self[widgetkey]['minus widget']
            if w:
                d['widgets to show'].append(w)
        
        for widgetkey in actionsbook.hide:
            d['widgets to hide'] += self.list_widgets(widgetkey)
        
        for widgetkey in actionsbook.hide_minus_button:
            w = self[widgetkey]['minus widget']
            if w:
                d['widgets to hide'].append(w)
        
        for widgetkey in actionsbook.drop:
            d['widgets to delete'] += self.list_widgets(widgetkey)
            w = self[widgetkey]['grid widget']
            if w:
                d['widgets to delete'].append(w)
            m = self[widgetkey]['language menu']
            if m:
                d['menus to delete'].append(m)
            m = self[widgetkey]['switch source menu']
            if m:
                d['menus to delete'].append(m)
            m = self[widgetkey]['unit menu']
            if m:
                d['menus to delete'].append(m)
            m = self[widgetkey]['geo menu']
            if m:
                d['menus to delete'].append(m)
            a = self[widgetkey]['switch source actions']
            if a:
                d['actions to delete'] += a
            a = self[widgetkey]['language actions']
            if a:
                d['actions to delete'] += a
            a = self[widgetkey]['unit actions']
            if a:
                d['actions to delete'] += a
            a = self[widgetkey]['geo actions']
            if a:
                d['actions to delete'] += a
            
            del self[widgetkey]
        
        for widgetkey in actionsbook.empty:
            w = self[widgetkey]['main widget']
            if w:
                d['widgets to empty'].append(w)
        
        for widgetkey in actionsbook.move:
            g = self.parent_grid(widgetkey)
            for w, k in self.list_widgets(widgetkey, with_kind=True):
                p = self.widget_placement(widgetkey, k)
                d['widgets to move'].append((g, w, *p))
        
        return d

    def list_widgets(self, widgetkey, with_kind=False):
        """Renvoie la liste des widgets référencés pour la clé considérée.
        
        Parameters
        ----------
        widgetkey : plume.rdf.widgetkey.WidgetKey
            Une clé du dictionnaire de widgets.
        with_kind : bool, default False
            Si ``True``, la méthode ne renvoie pas une liste de widgets, mais une
            liste de tuples dont le premier élément est le widget et le
            second une chaîne de caractères spécifiant sa nature (nom de la
            clé du dictionnaire interne où il est référencé).
            
        Returns
        -------
        list

        """
        if not widgetkey or not widgetkey in self:
            return []
        l = []        
        for k in ('main widget', 'minus widget', 'switch source widget',
            'language widget', 'unit widget', 'geo widget', 'label widget'):
            w = self[widgetkey][k]
            if w:
                if with_kind:
                    l.append((w, k))
                else:
                    l.append(w)
        return l

    def add(self, buttonkey):
        """Ajoute une clé sans valeur dans le dictionnaire de widgets.
        
        Cette méthode est à exécuter après l'activation d'un bouton plus
        ou bouton de traduction par l'utilisateur.
        
        Parameters
        ----------
        buttonkey : plume.rdf.widgetkey.PlusButtonKey
            La clé du bouton plus ou bouton de traduction actionné par
            l'utilisateur.
        
        Returns
        -------
        dict
            Cf. :py:meth:`WidgetsDict.dictisize_actionsbook` pour la
            description de ce dictionnaire, qui contient toutes
            les informations qui permettront de matérialiser l'action
            réalisée.
        
        Raises
        ------
        ForbiddenOperation
            Quand la clé est masquée ou qu'il ne s'agit pas d'un
            bouton plus.
        
        """
        if not isinstance(buttonkey, PlusButtonKey):
            raise ForbiddenOperation("Seul un bouton permet d'ajouter" \
                ' des éléments.', buttonkey)
        if buttonkey.is_hidden:
            raise ForbiddenOperation("Il n'est pas permis d'ajouter des " \
                'éléments avec un bouton invisible.', buttonkey)
        a = buttonkey.add()
        return self.dictisize_actionsbook(a)

    def drop(self, objectkey):
        """Supprime une clé du dictionnaire de widgets.
        
        Cette méthode est à exécuter après l'activation d'un bouton moins
        par l'utilisateur.
        
        Parameters
        ----------
        objectkey : plume.rdf.widgetkey.ObjectKey
            Une clé-valeur ou un groupe de propriété dont l'utilisateur
            vient d'activer le bouton moins.
        
        Returns
        -------
        dict
            Cf. :py:meth:`WidgetsDict.dictisize_actionsbook` pour la
            description de ce dictionnaire, qui contient toutes
            les informations qui permettront de matérialiser l'action
            réalisée.
        
        Raises
        ------
        ForbiddenOperation
            Quand la clé est masquée, quand la clé n'a pas de bouton
            moins.
        
        """
        if not objectkey.has_minus_button:
            raise ForbiddenOperation("Il faut un bouton moins " \
                ' pour supprimer une clé.', objectkey)
        if objectkey.is_single_child or objectkey.is_hidden:
            raise ForbiddenOperation("Il n'est pas permis de supprimer des " \
                'éléments avec un bouton moins invisible.', objectkey)
        a = objectkey.drop()
        return self.dictisize_actionsbook(a)

    def change_language(self, valuekey, new_language):
        """Change la langue déclarée pour une clé du dictionnaire de widgets.
        
        Cette méthode est à exécuter lorsque l'utilisateur clique sur
        une langue dans le menu d'un bouton de sélection de la langue.
        
        Parameters
        ----------
        valuekey : plume.rdf.widgetkey.ValueKey
            La clé-valeur dont un item du menu des langues vient d'être
            actionné par l'utilisateur.
        new_language : str
            La nouvelle langue sélectionnée par l'utilisateur.
        
        Returns
        -------
        dict
            Cf. :py:meth:`WidgetsDict.dictisize_actionsbook` pour la
            description de ce dictionnaire, qui contient toutes
            les informations qui permettront de matérialiser l'action
            réalisée.
        
        Raises
        ------
        ForbiddenOperation
            Quand la clé est masquée, quand la clé n'a pas de widget
            annexe de sélection de la langue, ou quand la langue
            n'est pas dans la liste des langues autorisées.
        
        """
        if self[valuekey]['language value'] == new_language:
            return self.dictisize_actionsbook()
        if not valuekey.has_language_button:
            raise ForbiddenOperation("Il faut un bouton de sélection " \
                "de la langue pour changer la langue d'une clé.", valuekey)
        if valuekey.is_hidden:
            raise ForbiddenOperation("Il n'est pas permis de changer " \
                "la langue d'une clé invisible.", valuekey)
        if not new_language in self[valuekey]['authorized languages']:
            raise ForbiddenOperation("La langue {} n'est pas disponible " \
                'pour les traductions.'.format(new_language), valuekey)
        a = valuekey.change_language(new_language)
        return self.dictisize_actionsbook(a)

    def change_source(self, objectkey, new_source):
        """Change la source déclarée pour une clé du dictionnaire de widgets.
        
        Cette méthode est à exécuter lorsque l'utilisateur clique sur
        une source dans le menu d'un bouton de sélection de la source.
        
        Parameters
        ----------
        objectkey : plume.rdf.widgetkey.ObjectKey
            La clé-valeur ou le groupe de propriété dont un item du menu des
            sources vient d'être actionné par l'utilisateur.
        
        Returns
        -------
        dict
            Cf. :py:meth:`WidgetsDict.dictisize_actionsbook` pour la
            description de ce dictionnaire, qui contient toutes
            les informations qui permettront de matérialiser l'action
            réalisée.
        
        Raises
        ------
        ForbiddenOperation
            Quand la clé est masquée, quand la clé n'a pas de widget
            annexe de sélection de la source, quand la source cible
            n'est pas dans la liste des sources autorisées pour la clé.
        
        """
        if self[objectkey]['current source'] == new_source:
            return self.dictisize_actionsbook()
        if not new_source in self[objectkey]['sources']:
            raise ForbiddenOperation("La source '{}' n'est pas " \
                'autorisée.', objectkey)
        if not objectkey.has_source_button:
            raise ForbiddenOperation("Il faut un bouton de sélection " \
                "de la source pour changer la source d'une clé.", objectkey)
        if objectkey.is_hidden:
            raise ForbiddenOperation("Il n'est pas permis de changer " \
                "la source d'une clé invisible.", objectkey)
        
        value_source = None
        if not new_source in ('< manuel >', '< URI >', '< non référencé >'):
            for s in objectkey.sources:
                # tous ces thésaurus ont déjà été chargé à
                # l'initialisation du dictionnaire de widgets, donc
                # cette boucle sur deux ou trois valeurs maximum
                # ne coûte pas grand chose
                if Thesaurus.get_label((s, self.langlist)) == new_source:
                    value_source = s
                    break
        
        if isinstance(objectkey, GroupOfPropertiesKey):
            # si la source n'est pas la même, c'est que ce n'est pas
            # < manuel >, et toutes les autres impliquent de basculer
            # sur la jumelle clé-valeur
            # Le cas d'une nouvelle source valant < URI > remplit
            # nécessairement cette condition
            a = objectkey.switch_twin(value_source)
        elif isinstance(objectkey, ValueKey) and new_source == '< manuel >':
            a = objectkey.switch_twin()
        else:
            a = objectkey.change_source(value_source)
        
        return self.dictisize_actionsbook(a)

    def change_unit(self, valuekey, new_unit):
        """Change l'unité déclarée pour une clé du dictionnaire de widgets.
        
        Cette méthode est à exécuter lorsque l'utilisateur clique sur
        une unité dans le menu d'un bouton de sélection d'unité.
        
        Parameters
        ----------
        valuekey : plume.rdf.widgetkey.ValueKey
            La clé-valeur dont un item du menu des unités vient d'être
            actionné par l'utilisateur.
        new_unit : str
            La nouvelle unité sélectionnée par l'utilisateur.
        
        Returns
        -------
        dict
            Cf. :py:meth:`WidgetsDict.dictisize_actionsbook` pour la
            description de ce dictionnaire, qui contient toutes
            les informations qui permettront de matérialiser l'action
            réalisée.
        
        Raises
        ------
        ForbiddenOperation
            Quand la clé est masquée, quand la clé n'a pas de widget
            annexe de sélection d'unité, ou quand l'unité
            n'est pas dans la liste des unités autorisées.
        
        """
        if self[valuekey]['current unit'] == new_unit:
            return self.dictisize_actionsbook()
        if not valuekey.has_unit_button:
            raise ForbiddenOperation("Il faut un bouton de sélection " \
                "de l'unité pour changer l'unité d'une clé.", valuekey)
        if valuekey.is_hidden:
            raise ForbiddenOperation("Il n'est pas permis de changer " \
                "l'unité d'une clé invisible.", valuekey)
        if not new_unit in self[valuekey]['units']:
            raise ForbiddenOperation("L'unité {} n'est pas " \
                'reconnue.'.format(new_unit), valuekey)
        a = valuekey.change_unit(new_unit)
        return self.dictisize_actionsbook(a)

    def widget_type(self, widgetkey):
        """Renvoie le type de widget adapté pour une clé.
        
        Parameters
        ----------
        widgetkey : plume.rdf.widgetkey.WidgetKey
            Une clé de dictionnaire de widgets.
        
        """
        if not widgetkey:
            return
        if isinstance(widgetkey, RootKey):
            return None
        if isinstance(widgetkey, GroupKey):
            return 'QGroupBox'
        if isinstance(widgetkey, PlusButtonKey):
            return 'QToolButton'
        if widgetkey.datatype == XSD.boolean:
            return 'QCheckBox'
        if widgetkey.is_read_only:
            return 'QLabel'
        if widgetkey.sources:
            return 'QComboBox'
        if widgetkey.is_long_text:
            return 'QTextEdit'
        d = {
            XSD.date: 'QDateEdit',
            XSD.dateTime: 'QDateTimeEdit',
            XSD.time: 'QTimeEdit'
            }
        return d.get(widgetkey.datatype, 'QLineEdit')
    
    def type_validator(self, widgetkey):
        """S'il y a lieu, renvoie le validateur adapté pour une clé.
        
        Parameters
        ----------
        widgetkey : plume.rdf.widgetkey.WidgetKey
            Une clé de dictionnaire de widgets.
        
        """
        if not widgetkey or widgetkey.is_read_only:
            return
        d = {
            XSD.integer: 'QIntValidator',
            XSD.decimal: 'QDoubleValidator',
            XSD.float: 'QDoubleValidator',
            XSD.double: 'QDoubleValidator',
            XSD.duration: 'QIntValidator'
            }
        return d.get(widgetkey.datatype)
    
    def update_value(self, widgetkey, value, override=False):
        """Prépare et enregistre une valeur dans une clé-valeur du dictionnaire de widgets.
        
        Parameters
        ----------
        widgetkey : plume.rdf.widgetkey.ValueKey
            Une clé-valeur de dictionnaire de widgets.
        value : str
            La valeur, exprimée sous la forme d'une chaîne de caractères.
        override : bool, default False
            Si ``True``, permet de modifier la valeur d'une clé
            en lecture seule.
        
        """
        if not isinstance(widgetkey, ValueKey) \
            or (widgetkey.is_read_only and not override):
            return
        if value in (None, ''):
            widgetkey.value = None
        else:
            if widgetkey.transform == 'email':
                value = owlthing_from_email(value)
            if widgetkey.transform == 'phone':
                value = owlthing_from_tel(value)
            if widgetkey.value_language:
                widgetkey.value = Literal(value, lang=widgetkey.value_language)
            elif widgetkey.value_unit:
                widgetkey.value = duration_from_int(value, widgetkey.value_unit)
            elif widgetkey.datatype == XSD.date:
                widgetkey.value = date_from_str(value)
            elif widgetkey.datatype == XSD.dateTime:
                widgetkey.value = datetime_from_str(value)
            elif widgetkey.datatype and widgetkey.datatype != XSD.string:
                widgetkey.value = Literal(value, datatype=widgetkey.datatype)
            elif widgetkey.datatype == XSD.string:
                widgetkey.value = Literal(value)
            elif widgetkey.value_source:
                res = Thesaurus.concept_iri((widgetkey.value_source, \
                    widgetkey.main_language), value)
                if res:
                    widgetkey.value = res
            else:
                f = forbidden_char(value)
                if f:
                    raise ForbiddenOperation("Le caractère '{}' " \
                        "n'est pas autorisé dans un IRI.".format(f), widgetkey)
                widgetkey.value = URIRef(value)
        if widgetkey in self:
            self.internalize(widgetkey)
    
    def str_value(self, widgetkey):
        """Renvoie la valeur d'une clé-valeur du dictionnaire de widgets sous forme d'une chaîne de caractères.
        
        Si la clé est en lecture seule, la fonction renvoie, s'il y a lieu,
        un fragment HTML avec un hyperlien.
        
        Parameters
        ----------
        widgetkey : plume.rdf.widgetkey.ValueKey
            Une clé-valeur de dictionnaire de widgets.
        
        Returns
        -------
        str
        
        """
        value = widgetkey.value
        if value is None:
            return
        str_value = None
        if widgetkey.transform == 'email':
            str_value = email_from_owlthing(value)
        elif widgetkey.transform == 'phone':
            str_value = tel_from_owlthing(value)
        elif widgetkey.value_source:
            str_value = Thesaurus.concept_str((widgetkey.value_source, \
                widgetkey.main_language), value)
        elif widgetkey.value_unit:
            if widgetkey.is_read_only:
                str_value = str_from_duration(value)
            else:
                str_value = str(int_from_duration(value)[0])
        elif widgetkey.datatype == XSD.date:
            str_value = str_from_date(value)
        elif widgetkey.datatype == XSD.dateTime:
            str_value = str_from_datetime(value)
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
    
    def build_metagraph(self, preserve_metadata_date=False):
        """Construit un graphe de métadonnées à partir du contenu du dictionnaire.
        
        Parameters
        ----------
        preserve_metadata_date : bool, default False
            Si ``True`` la date de dernière modification du
            graphe ne sera pas incrémentée.
        
        Returns
        -------
        plume.rdf.metagraph.Metagraph
        
        Notes
        -----
        Sauf lorsque `preserve_metadata_date` vaut ``True``, la date
        de mise à jour des métadonnées est silencieusement actualisée
        lors de la génération du nouveau graphe. Cette modification n'est
        pas répercuté sur le dictionnaire (et son arbre de clés), ni donc
        sur les widgets. Elle ne sera visible de l'utilisateur que si
        un nouveau dictionnaire est généré à partir du nouveau graphe, par
        exemple lorsqu'il quittera le mode édition.
        
        """
        if self.root:
            metagraph = self.root.build_metagraph()
            if not preserve_metadata_date:
                metagraph.update_metadata_date()
            return metagraph

    def group_kind(self, widgetkey):
        """Renvoie la nature du groupe auquel appartient la clé.
        
        Parameters
        ----------
        widgetkey : plume.rdf.widgetkey.ValueKey
            Une clé-valeur de dictionnaire de widgets.
        
        Returns
        -------
        str
            * ``'group of values'`` si la clé est un groupe
              de valeurs ou, s'il s'agit d'une clé-valeur ou
              d'un bouton, si son parent est un groupe de valeurs.
            * ``'group of properties'`` si la clé est un groupe
              de propriétés ou, s'il s'agit d'une clé-valeur ou d'un
              bouton, si son parent est un groupe de propriétés.
              Les clés-racines et les onglets sont considérés ici
              comme des groupes de propriétés.
            * ``'translation group'`` si l'enregistrement est un groupe de
              traduction ou, s'il s'agit d'une clé-valeur ou d'un bouton,
              si son parent est un groupe de traduction.
        
        Raises
        ------
        RuntimeError
            Si le type obtenu n'est pas l'un des trois susmentionnés.
        
        """
        if isinstance(widgetkey, GroupKey):
            obj = self[widgetkey]['object']
        else:
            obj = self[widgetkey.parent]['object']
        
        if obj in ('root', 'tab'):
            return 'group of properties'
        if obj in ('group of values', 'group of properties',
            'translation group'):
            return obj
            
        raise RuntimeError("Unknown group kind for key {}.".format(key))
    
    def print(self):
        """Visualisateur très sommaire du contenu du dictionnaire de widgets.
        
        Les clés sont imprimées dans la console, avec - si
        défini - leur libellé, leur valeur et leurs boutons annexes.
        Une clé ou un bouton masqué apparaît précédé d'un
        astérisque.
        
        """
        l = sorted(self.keys(), key=lambda x: x.tree_idx)
        for widgetkey in l:
            print('  ' * widgetkey.generation, end='')
            if self[widgetkey]['hidden']:
                print('*', end='')
            print('<', self[widgetkey]['object'], '/',
                self[widgetkey]['main widget type'], '>', end=' ')
            if self[widgetkey]['label']:
                print(self[widgetkey]['label'], ':', end=' ')
            if self[widgetkey]['value']:
                print(self[widgetkey]['value'], end=' ')
            if self[widgetkey]['hide minus button']:
                print('*', end='')
            if self[widgetkey]['has minus button']:
                print('[-]', end=' ')
            if self[widgetkey]['multiple sources']:
                print('[...]', end=' ')
            if self[widgetkey]['authorized languages']:
                print('[{}]'.format(self[widgetkey]['language value']), end=' ')
            print()

