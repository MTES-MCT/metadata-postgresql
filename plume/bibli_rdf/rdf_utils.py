"""Utilitary class and functions for parsing and serializing RDF metadata.

Les fonctions suivantes permettent :
- d'extraire des métadonnées en JSON-LD d'une chaîne de
caractères balisée et les désérialiser sous la forme d'un
graphe ;
- de traduire ce graphe en un dictionnaire de catégories
de métadonnées qui pourra alimenter un formulaire ;
- en retour, de reconstruire un graphe à partir d'un
dictionnaire de métadonnées ;
- de sérialiser ce graphe en JSON-LD et l'inclure dans
une chaîne de caractères balisée.

Dépendances : rdflib 6.0.0 ou supérieur.
"""

from rdflib import Graph, Namespace, Literal, BNode, URIRef
from rdflib.namespace import NamespaceManager, split_uri
from rdflib.serializer import Serializer
from rdflib.util import from_n3
from locale import strxfrm, setlocale, LC_COLLATE
from pathlib import Path
from html import escape
from json import dumps, loads
import re, uuid

from plume.bibli_rdf import __path__
#==================================================
#Gestion de la bibliothèque RDFLIB
from ..bibli_install.bibli_install import manageLibrary
try : 
  from rdflib import Graph, Namespace, Literal, BNode, URIRef
  from rdflib.namespace import NamespaceManager, split_uri
  from rdflib.serializer import Serializer
  from rdflib.util import from_n3
except :
  manageLibrary()
  from rdflib import Graph, Namespace, Literal, BNode, URIRef
  from rdflib.namespace import NamespaceManager, split_uri
  from rdflib.serializer import Serializer
  from rdflib.util import from_n3
#==================================================


class WidgetsDict(dict):
    """Classe pour les dictionnaires de widgets.
    
    ATTRIBUTS
    ---------
    Les attributs du dictionnaire de widgets rappellent le paramétrage
    utilisé à sa création.
    
    - mode (str) : 'edit' pour un dictionnaire produit pour l'édition,
    'read' pour un dictionnaire produit uniquement pour la consultation.
    Certaines méthodes ne peuvent être utilisées que sur un
    dictionnaire dont l'attribut mode vaut 'edit'.
    
    - translation (bool) : True pour un dictionnaire comportant des
    fonctionnalités de traduction, False sinon.
    Certaines méthodes ne peuvent être utilisées que sur un dictionnaire
    dont l'attribut translation vaut True.
    
    - language (str) : langue principale déclarée lors de la création du
    dictionnaire. language est nécessairement l'un des éléments de langList
    ci-après.
    
    - langList (list): liste des langues autorisées pour les traductions,
    telles que déclarées lors de la génération du dictionnaire.
    """
    
    def __init__(self, mode, translation, language, langList):
        """Création d'un dictionnaire de widgets vide.
        
        ARGUMENTS
        ---------
        - mode (str) : indique si le dictionnaire est généré pour le mode édition
        ('edit'), le mode lecture ('read').
        Le mode détermine les actions pouvant être exécutées sur le dictionnaire.
        - translation (bool) : paramètre utilisateur qui indique si les widgets de
        traduction doivent être affichés. Sa valeur contribue à déterminer les actions
        pouvant être exécutées sur le dictionnaire. translation ne peut valoir
        True que si le mode est 'edit'.
        - language (str) : langue principale de rédaction des métadonnées
        (paramètre utilisateur). Elle influe sur certaines valeurs du dictionnaire et
        la connaître est nécessaire à l'exécution de certaines actions. language soit
        impérativement être l'un des éléments de langList.
        - langList (list) : liste des langues autorisées pour les traductions. Certaines
        valeurs du dictionnaire dépendent de cette liste, et la connaître est nécessaire
        à l'exécution de certaines actions.
        
        RESULTAT
        --------
        Un dictionnaire de widgets (WidgetsDict) vide.
        """
        if mode in ('edit', 'read'):
            # 'search' n'est pas accepté pour le moment
            self.mode = mode
        else:
            raise ValueError("mode should be either 'edit' or 'read'.")
        
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


    def copy(self):
        """Renvoie une copie (non liée) du dictionnaire de widgets.
        
        Cette méthode remplace la méthode copy() de la la classe dict().
        
        ARGUMENTS
        ---------
        Néant.
        
        RESULTAT
        --------
        Une copie non liée / shallow copy du dictionnaire de widgets
        (WidgetsDict).
        """
        d = WidgetsDict(
            mode=self.mode,
            translation=self.translation,
            language=self.language,
            langList=self.langList.copy()
            )
            
        for k, v in self.items():
            d.update({k: v})
        
        return d  

    
    def count_siblings(self, key, restrict=True, visibleOnly=False):
        """Renvoie le nombre de clés de même parent que key.
        
        ARGUMENTS
        ---------
        - key (tuple) : clé du dictionnaire de widgets (WidgetsDict).
        - [optionnel] restrict (bool) : si True, les enregistrements "plus button"
        et "translation button" ne sont pas comptabilisés. True par défaut.
        - [optionnel] visibleOnly (bool) : si True, les widgets masqués
        ne sont pas comptabilisés.
        
        RESULTAT
        --------
        Un entier qui devrait au moins valoir 1 si key est bien référencée
        dans le dictionnaire (et n'est pas un bouton avec restrict actif).
        
        EXEMPLES
        --------
        >>> d.count_siblings((1, (0,)))    
        """
        if len(key) == 1:
            return 0
        
        n = 0
        
        for k in self.keys():
            if len(k) > 1 and k[1] == key[1] and ( not restrict or
                not self[k]['object'] in ('translation button', 'plus button') ) \
                and ( not visibleOnly or ( self[k]['main widget type'] and \
                not self[k]['hidden'] and not self[k]['hidden M'] ) ):
                n += 1
                
        return n


    def child(self, key, visibleOnly=True):
        """Renvoie la clé d'un enfant de la clé key (hors boutons).
        
        Cette fonction est supposée être lancée sur un groupe de valeurs
        ou groupe de traduction, où tous les enfants sont de même nature.
        
        ARGUMENTS
        ---------
        - key (tuple) : clé du dictionnaire de widgets (WidgetsDict).
        - [optionnel] visibleOnly (bool) : si True (valeur par défaut),
        les widgets masqués ne sont pas pris en compte.
        
        RESULTAT
        --------
        La clé (tuple) d'un enfant de l'enregistrement de clé key, en
        excluant les 'plus button' et 'translation button'.

        NB : le plus souvent, l'enregistrement renvoyé sera (0, key),
        mais il est possible que celui-ci ait été supprimé par
        activation de son bouton moins.
        """
        c = None
        
        for k, v in self.items():
        
            if len(k) > 1 and k[1] == key \
                and not v['object'] in ('plus button', 'translation button') \
                and (not visibleOnly or (not v['hidden'] and not v['hidden M'] \
                and v['main widget type']) \
                ):
                c = k
                break
                
        return c 


    def retrieve_subject(self, parent):
        """Renvoie la valeur attendue pour la clé "subject" d'un enfant de la clé parent.
        
        ARGUMENTS
        ---------
        - parent (tuple) : clé du dictionnaire de widgets (WidgetsDict).
        
        RESULTAT
        --------
        Un IRI (URIRef) ou noeud vide (BNode) qui pourra sera la valeur
        de la clé "node" de parent si elle existe, sinon la valeur de la
        clé "node" du premier ancêtre qui en ait une.
        """
        
        if self[parent]['node']:
            return self[parent]['node']
            
        else:
            key = parent
            while not is_root(key):
                key = key[1]
                if self[key]['node']:
                    return self[key]['node']


    def clean_copy(self, key, language=None, langList=None, novalue=False):
        """Renvoie une copie nettoyée du dictionnaire interne de la clé key.
        
        ARGUMENTS
        ---------
        - key (tuple) : clé du dictionnaire de widgets (WidgetsDict).
        - [optionnel] language (str) : langue de la nouvelle valeur.
        Par défaut, la fonction utilise l'attribut language du dictionnaire.
        La valeur de language est supposée incluse dans langList ci-après
        (pas de contrôle).
        - [optionnel] langList (list) : la liste des langues autorisées
        pour les traductions. Par défaut, la fonction utilise l'attribut
        langList du dictionnaire.
        - [optionnel] novalue (bool) : si True, la fonction n'utilise pas les
        valeurs par défaut pour peupler la copie.

        RESULTAT
        --------
        Un dictionnaire, qui pourra être utilisé comme valeur pour une autre
        clé du dictionnaire de widgets.
        
        Le contenu du dictionnaire est identique à celui de la source, si
        ce n'est que :
        - les clés supposées contenir des widgets, actions et menus sont
        vides ;
        - la clé "value" est remise à la valeur par défaut (ou vide si
        novalue) ;
        - la clé "language value" vaudra language et "authorized languages"
        vaudra langList (s'il y avait lieu de spécifier une langue) ;
        - la clé "hidden" est réinitialisée (ne vaudra jamais True sauf si
        la liste des langues autorisées ne contient qu'une langue). À noter que
        "hidden M" est par contre conservée en l'état ;
        - la clé "node", si elle n'était pas vide, reçoit un nouveau noeud vide ;
        - la clé 'hide minus button' vaudra toujours True si 'has minus button'
        vaut True.
        """

        if language is None:
            language = self.language
        if langList is None:
            langList = self.langList
        
        d = self[key].copy()
        
        if d['sources'] is not None:
            mSources = d['sources'].copy()
            if '< non répertorié >' in mSources:
                mSources.remove('< non répertorié >')
        else:
            mSources = None
        
        if d['current source'] is None:
            mCurSource = None
            mCurSourceURI = None
        if d['current source'] == '< manuel >':
            mCurSource = '< manuel >'
            mCurSourceURI = None
        elif d['default source']:
            mCurSource = d['default source']
            mCurSourceURI = d['sources URI'][d['default source']]
        else:
            mCurSource = d['current source']
            mCurSourceURI = d['current source URI']
        
        d.update({
            'main widget' : None,
            'grid widget' : None,
            'label widget' : None,
            'minus widget' : None,
            'language widget' : None,
            'switch source widget' : None,

            'switch source menu' : None,
            'switch source actions' : None,
            'language menu' : None,
            'language actions' : None,
            
            'main widget type': d['default widget type'] if d['main widget type'] \
                and d['default widget type'] else d['main widget type'],
            'value' : d['default value'] if not novalue else None,
            'language value' : language if d['language value'] else None,
            'authorized languages' : langList.copy() if d['authorized languages'] \
                is not None else None,
            'sources' : mSources,
            'multiple sources': len(mSources) > 1 if mSources \
                and self.mode == 'edit' else None,
                # réinitialisé parce qu'on a expurgé les potentiels
                # '< non répertoriés >' qui pouvaient rendre multi-sources
                # des propriétés qui n'auraient pas dû l'être
            'current source': mCurSource,
            'current source URI': mCurSourceURI,
            'hidden' : len(langList) == 1 if (
                d['object'] == 'translation button' ) else None,
            'hide minus button': True if d['has minus button'] else None,
                
            'node': BNode() if d['node'] else None
            })
        
        return d
 

    def parent_widget(self, key):
        """Renvoie le widget parent de la clé key.
        
        ARGUMENTS
        ---------
        - key (tuple) : une clé du dictionnaire de widgets.
        
        RESULTAT
        --------
        Un widget (QGroupBox) si la clé existe, que l'enregistrement a un
        parent et que le widget principal de celui-ci a été créé. Sinon None.
        """
        if len(key) > 1 and key[1] in self:
            if 'main widget' in self[key[1]]:
                return self[key[1]]['main widget']


    def parent_grid(self, key):
        """Renvoie la grille dans laquelle doit être placé le widget de la clé key.
        
        ARGUMENTS
        ---------
        - key (tuple) : une clé du dictionnaire de widgets.
        
        RESULTAT
        --------
        Un widget (QGridLayout) si la clé existe, que l'enregistrement a un
        parent et que la grille de celui-ci a été créée. Sinon None.
        """
        if len(key) > 1 and key[1] in self:
            if 'grid widget' in self[key[1]]:
                return self[key[1]]['grid widget']


    def drop(self, key):
        """Supprime du dictionnaire un enregistrement et, en cascade, tous ses descendants.
        
        Cette fonction est à utiliser suite à l'activation par l'utilisateur
        du "bouton moins" d'un groupe de valeurs ou d'un groupe de traduction.
        Par principe, il ne devrait jamais y avoir de boutoin moins lorsque le
        groupe ne contient qu'une valeur, et faire usage de la fonction dans ce
        cas produirait une erreur.
        
        ARGUMENTS
        ---------
        - key (tuple) : une clé du dictionnaire de widgets.
        
        RESULTAT
        --------
        Un dictionnaire ainsi constitué :
        {
        "widgets to delete" : [liste des widgets à détruire (QWidget)],
        "actions to delete" : [liste des actions à détruire (QAction)],
        "menus to delete" : [liste des menus à détruire (QMenu)],
        "widgets to show" : [liste des widgets masqués à afficher (QWidget)],
        "widgets to hide' : [liste de widgets à masquer (QWidget)],
        "language menu to update" : [liste de clés (tuples) pour lesquelles
        le menu des langues devra être régénéré],
        "widgets to move" : [liste de tuples - cf. ci-après]
        }
        
        Les tuples de la clé "widgets to move" sont formés comme suit :
        [0] la grille (QGridLayout) où un widget doit être déplacé.
        [1] le widget en question (QWidget).
        [2] son nouveau numéro de ligne / row (int).
        [3] son numéro de colonne / column (int).
        [4] le nombre de lignes occupées / rowSpan (int).
        [5] le nombre de colonnes occupées / columnSpan (int).
        
        NB : Les widgets à détruire ne sont plus répertoriés dans le
        dictionnaire, au contraire des widgets à masquer.
        
        La fonction réalise par ailleurs les opérations suivantes :
        - L'enregistrement visé, son double M éventuel et ses descendants
        sont supprimés du dictionnaire.
        - Les clés row des enregistrements de même parent qui étaient
        placés en dessous dans la grille sont mises à jour en conséquence.
        S'il ne reste qu'une valeur, la clé 'hide minus button' de
        l'enregistrement indiquera désormais True.
        
        EXEMPLES
        --------
        >>> d[(2,(0,))]['row']
        3       
        >>> d.drop((1,(0,)))
        >>> d[(2,(0,))]['row']
        2
        """
        if self.mode == 'read':
            raise ForbiddenOperation("You can't remove widgets in reading mode.")
        
        if len(key) < 2:
            raise ForbiddenOperation("This is the tree root, you can't cut it !")
            
        g = self[key[1]]['object']
        if not g in ('translation group', 'group of values'):
            raise ForbiddenOperation("You can't delete a record outside of a group of values or translation group.")
            
        if not self[key]['main widget type'] or self[key]['hidden'] \
            or self[key]['hidden M']:
            raise ForbiddenOperation("Widget {} is hidden, no action is allowed here.".format(key))
        
        d = {
            "widgets to delete": [],
            "actions to delete": [],
            "menus to delete": [],
            "widgets to show": [],
            "widgets to hide": [],
            "language menu to update" : [],
            "widgets to move": []
            }
        l = []
        n = self.count_siblings(key, visibleOnly=True)
        
        language = self[key]['language value']
        
        if n < 2:
            raise ForbiddenOperation("This is the last of its kind, you can't destroy it !")
        
        keym = (key[0], key[1]) if len(key) == 3 else (key[0], key[1], 'M')
        if not keym in self:
            keym = None
        
        for k in self.keys():
            
            # cas des descendants (+ l'enregistrement cible et,
            # le cas échéant, son double M)
            # NB : on ne cherche pas les descendants dans un groupe de
            # traduction puisqu'il ne peut pas y en avoir
            if (g == 'group of values' and is_ancestor(key, k)) \
                or (g == 'group of values' and keym and is_ancestor(keym, k)) \
                or (len(k) > 1 and k[0] == key[0] and k[1] == key[1]):
            
                l.append(k)
                
                for e in ('main widget', 'grid widget', 'label widget', 'minus widget',
                          'language widget', 'switch source widget'):
                    w = self[k][e]
                    if w:
                        d["widgets to delete"].append(w)
                        
                for e in ('switch source actions', 'language actions'):
                    a = self[k][e]
                    if a:
                        d["actions to delete"] += a
                        
                for e in ('switch source menu', 'language menu'):
                    m = self[k][e]
                    if m:
                        d["menus to delete"].append(m)

            # cas des frères et soeurs (pour ceux qui 
            # ne sont pas du stockage sans widget)
            elif self[k]['main widget type'] and len(k) > 1 and k[1] == key[1]:
            
                if self[k]['row'] > self[key]['row']:
                    
                    # mise à jour de la clé 'row' des petits frères
                    self[k]['row'] -= ( self[key]['row span'] or 1 )
                    
                    for e in ('main widget', 'minus widget', 'language widget', 'switch source widget'):
                        # pas de label widget, l'étiquette est sur le groupe
                        w = self[k][e]
                        if w:
                            row, column, rowSpan, columnSpan = self.widget_placement(k, e)
                            d["widgets to move"].append((
                                self.parent_grid(k),
                                w,
                                row, column, rowSpan, columnSpan
                                ))
            
            
                if self[k]['object'] in ('plus button', 'translation button'):
                    
                    # si le bouton (de traduction) était masqué et que
                    # la langue de l'enregistrement à supprimer est bien
                    # dans la liste des langues autorisées, on le "démasque"
                    if g == 'translation group' and self[k]['hidden'] and language in self.langList:
                        self[k]['hidden'] = False
                        w = self[k]['main widget']
                        if w:
                            d["widgets to show"].append(w)

                    
                elif self[k]['object'] in ('group of properties', 'translation group', 'edit') :
                    
                    if n == 2:
                        # le bouton moins doit être masqué s'il ne
                        # reste qu'une seule valeur
                        self[k]['hide minus button'] = True
                        
                        w = self[k]['minus widget']
                        if w:
                                d["widgets to hide"].append(w)
                     
                    if g == 'translation group' and language in self.langList:
                        # on ajoute language aux listes de langues
                        # disponibles des frères et soeurs
                        if not language in self[k]['authorized languages']:
                            self[k]['authorized languages'].append(language)
                            self[k]['authorized languages'].sort()
                            d["language menu to update"].append(k)
        
        for e in l:
            del self[e]
            
        return d
   

    def add(self, key):
        """Ajoute un enregistrement (vide) dans le dictionnaire de widgets.
        
        Cette fonction est à utiliser après activation d'un bouton plus
        (plus button) ou bouton de traduction (translation button) par
        l'utilisateur.
        
        ARGUMENTS
        ---------
        - key (tuple) : une clé du dictionnaire de widgets, et plus
        précisément la clé du bouton qui vient d'être activé par
        l'utilisateur.
        
        RESULTAT
        --------
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
        
        EXEMPLES
        --------
        >>> d.add((1, (0, (0,))))
        """
        if self.mode == 'read':
            raise ForbiddenOperation("You can't add widgets in reading mode.")
        
        language = self.language
        
        d = {
            "widgets to show": [],
            "widgets to hide": [],
            "widgets to move": [],
            "language menu to update" : [],
            "new keys": []
            }
        
        if len(key) < 2:
            raise ForbiddenOperation("This is the tree root, you can't add anything here !")
            
        if not self[key]['object'] in ('plus button', 'translation button'):
            raise ValueError("{} isn't a 'plus button' nor a 'translation button'.".format(key))
        
        if self[key]['hidden']:
            raise ForbiddenOperation("Don't even try to add anything with an hidden button !")
        
        c = self.child(key[1])       
        if c is None:
            raise RuntimeError("Could not find a record to copy from.")
            
        n = self[key]['next child']      
        r = self[key]['row']
        
        # dans le cas d'un groupe de traduction, on écrase
        # les paramètres mLangList et language
        if self[key]['object'] == 'translation button':
        
            mLangList = self[c]['authorized languages'].copy()
            
            if self[c]['language value'] in mLangList:
                mLangList.remove(self[c]['language value'])
                # on retire cette langue puisqu'elle est déjà utilisée
                
            if len(mLangList) == 0:
                raise RuntimeError('No more available language for translation.')
            
            # arbitrairement, on considère que la langue
            # initialement affichée pour la nouvelle
            # valeur sera la première de la liste des
            # langues disponibles
            language = mLangList[0]
            
            # cas où la langue que l'on utilise était la
            # dernière disponible - dans ce cas on masque
            # le bouton de traduction pour empêcher d'autres
            # ajouts
            if len(mLangList) == 1:
                self[key]['hidden'] = True
                w = self[key]['main widget']
                if w:
                    d["widgets to hide"].append(w)
                    
        else:
            mLangList = self.langList.copy()
        
        k1 = (n, key[1]) if len(c) == 2 else (n, key[1], 'M')
        k2 = (n, key[1], 'M') if len(c) == 2 else (n, key[1])
        cm = (c[0], c[1], 'M') if len(c) == 2 else (c[0], c[1])
        
        self.update( { k1: self.clean_copy(c, language, mLangList, novalue=True) } )
        # on utilise le paramètre novalue de clean_copy, parce que si
        # l'utilisateur ajoute une valeur dans un groupe, ce n'est pas
        # pour se retrouver avec un widget déjà rempli (le novalue=False
        # a par contre tout son sens avec les descendants d'un double M)
        self[k1]['row'] = r
        d['new keys'].append(k1)
        
        # cas d'un enregistrement avec un double M
        if cm in self and self[cm]['main widget type']:
            self.update( { k2: self.clean_copy(cm, language, mLangList, novalue=True) } )  
            self[k2]['row'] = r
            d['new keys'].append(k2)
        else:
            cm = None
    
        # mise à jour de l'indice mémorisé dans le bouton
        # pour le prochain enregistrement à ajouter
        self[key]['next child'] += 1
        
        # on décale le bouton pour qu'il apparaisse après
        # le nouvel enregistrement
        # NB. ne fonctionnerait pas si on avait des
        # QTextEdit "URI" (ou quoi que ce soit avec un row span
        # différent de la valeur par défaut) doublés par un
        # groupe M, mais ça n'aurait aucun sens.
        self[key]['row'] += ( self[k1]['row span'] or 1 )
        w = self[key]['main widget']
        if w:
            row, column, rowSpan, columnSpan = self.widget_placement(key, 'main widget')
            d["widgets to move"].append((
                self.parent_grid(key),
                w,
                row, column, rowSpan, columnSpan
                ))
        
        for k in self.copy().keys():
        # on fait l'itération sur une copie du
        # dictionnaire, parce qu'on va ajouter des clés
        # au cours de l'itération (et on aurait sinon des
        # erreurs de type "RuntimeError: dictionary changed
        # size during iteration")
        
            # cas des frères et soeurs
            if len(k) > 1 and k[1] == key[1] \
                and self[k]['object'] in ('group of properties',
                'translation group', 'edit') and \
                self[k]['main widget type']:
                
                # on vient d'ajouter un enregistrement au groupe,
                # donc il y a lieu d'ajouter des boutons moins
                # s'ils n'étaient pas déjà là
                if self[k]['hide minus button']:
                    self[k]['hide minus button'] = False
                    w = self[k]['minus widget']
                    if w and not self[k]['hidden M']:
                        d["widgets to show"].append(w)
                
                # dans le cas d'un ajout de traduction,
                # on supprime language des listes de langues
                # autorisées des frères et soeurs
                if self[key]['object'] == 'translation button' and not k in (k1, k2) :
                    if language in self[k]['authorized languages']:
                        self[k]['authorized languages'].remove(language)
                        d["language menu to update"].append(k)
        
            # cas des descendants de la clé c ou de son double M :
            # uniquement pour les boutons plus, puisque les
            # groupes de traduction sont toujours en bout de
            # chaîne
            # on exclut les enregistrements qui n'ont pas
            # vocation à alimenter des widget (pas de main
            # widget type)
            cr = c if is_ancestor(c, k) else (
                cm if ( cm and is_ancestor(cm, k) ) else None
                )
            if cr and self[key]['object'] == 'plus button' \
                and self[k]['main widget type']:
            
                if self[k[1]]['object'] == 'group of properties' \
                    or self[k]['object'] in ('plus button', 'translation button') \
                    or self[k]['row'] == 0 \
                    or self[k]['label row'] == 0:
                    # dans les groupes de propriétés, tout est dupliqué ;
                    # dans les autres groupes, on ne garde que les boutons
                    # et le groupe ou widget placé sur la première ligne
                    # de la grille
                    kr = (n, key[1]) if len(cr) == 2 else (n, key[1], 'M')
                    newkey = replace_ancestor(k, cr, kr)
                    
                    # on prend soin d'exclure les descendants de groupes
                    # de propriétés non reproduits, car ils étaient
                    # dans un groupe de valeurs, et pas son premier membre
                    if not newkey[1] in self:
                        continue
                    
                    self.update( { newkey: self.clean_copy(k) } )
                    
                    # clean_copy se charge de réinitialiser les noeuds
                    # vides objets, par contre il faut maintenant récupérer
                    # le bon sujet pour chaque triple
                    self[newkey]['subject'] = self.retrieve_subject(newkey[1])
                    
                    # les boutons plus et boutons de traduction se trouvent
                    # nécessairement sous l'unique élément du groupe.
                    if self[newkey]['object'] in ('plus button', 'translation button'):
                        self[newkey]['row'] = self[self.child(k[1], visibleOnly=False) \
                            ]['row span'] or 1
                        # NB1 : on va bien chercher child(k[1]) et pas child(newkey[1]),
                        # car on ne maîtrise pas l'ordre de création des objets d'une
                        # même génération. Le bouton peut être créé en premier.
                        # NB2 : avec visibleOnly=False, parce que le groupe peut être
                        # entièrement masqué. Tomber sur un double M n'est pas gênant
                        # puisqu'il aura les mêmes row et rowspan que son jumeau.
                    
                    d['new keys'].append(newkey)
                    
        return d


    def change_language(self, key, new_language):
        """Change la langue sélectionnée pour une clé.
        
        ARGUMENTS
        ---------
        - key (tuple) : une clé du dictionnaire de widgets, et plus
        précisément la clé pour laquelle l'utilisateur vient de
        choisir une nouvelle langue.
        - new_language (str) : la nouvelle langue.
        
        RESULTAT
        --------
        Un dictionnaire ainsi constitué :
        {
        "language menu to update" : [liste de clés (tuples) pour lesquelles
        le menu des langues devra être régénéré],
        "widgets to hide" : [liste de widgets à masquer (QWidget)]       
        }
        
        EXEMPLES
        --------
        Pour déclarer que le libellée de la donnée est en anglais :
        >>> d.change_language((0, (0, (0,))), 'en')
        """
        if self.mode == 'read':
            raise ForbiddenOperation("You can't change a widget's language in reading mode.")
        
        if not self[key]['object'] == 'edit' \
            or not self[key]['data type'] in (
                URIRef('http://www.w3.org/2001/XMLSchema#string'),
                URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#langString')
                ):
            raise ForbiddenOperation("You can't put a language tag on anything but a string !")
            
        if not self[key]['authorized languages'] \
            or not new_language in self[key]['authorized languages']:
            raise ForbiddenOperation("{} isn't an authorized language for key {}.".format(new_language, key))
        
        d = {
            "language menu to update": [],
            "widgets to hide" : []
            }
        
        # ancienne langue
        old_language = self[key]['language value']
        
        if new_language == old_language:
            return d
        
        b = old_language and old_language in self.langList
        if ( not b ) and old_language in self[key]['authorized languages']:
            self[key]['authorized languages'].remove(old_language)
            # si la langue de fait n'était pas autorisée,
            # on la supprime du menu maintenant qu'elle n'est
            # plus utilisée  
        
        # mise à jour de la langue courante pour key
        self[key]['language value'] = new_language
        d["language menu to update"].append(key)
                
        # dans le cas d'un groupe de traduction,
        # mise à jour des menus des frères et soeurs
        if len(key) > 1 and self[key[1]]['object'] == 'translation group':
            for k in self.keys():
                if len(k) > 1 and key[1] == k[1] and not key == k:
                
                    if self[k]['object'] == 'edit':
                
                        if new_language in self[k]['authorized languages']:
                            self[k]['authorized languages'].remove(new_language)
                            d["language menu to update"].append(k)
                            
                        if b and not old_language in self[k]['authorized languages']:
                            self[k]['authorized languages'].append(old_language)
                            self[k]['authorized languages'].sort()
                            if not k in d["language menu to update"]:
                                d["language menu to update"].append(k)
                                
                    elif self[k]['object'] == 'translation button' \
                        and len(self[key]['authorized languages']) == 1:
                        # s'il ne reste aucune langue non utilisée (peut
                        # arriver si l'ancienne langue n'était pas autorisée
                        # et n'a donc pas été remise en jeu), on masque
                        # le bouton de traduction
                        self[k]['hidden'] = True
                        w = self[k]['main widget']
                        if w:
                            d["widgets to hide"].append(w)
                        
        return d  

    
    def change_source(self, key, source):
        """Change le thésaurus sélectionné pour une clé.
        
        ARGUMENTS
        ---------
        - key (tuple) : une clé du dictionnaire de widgets, et plus
        précisément la clé pour laquelle l'utilisateur vient de
        choisir une nouvelle langue.
        - source (str) : nom de la nouvelle source, qui pourra être soit
        un nom de thésaurus soit "< URI >" pour un URI sans thésaurus
        associé, soit "< manuel >" pour basculer en saisie manuelle.
        
        RESULTAT
        --------
        Un dictionnaire ainsi constitué :
        {
        "concepts list to update" : [liste de clés (tuples) correspondant à des
        QComboBox dont la liste de valeurs devra être régénérée],
        "widgets to empty" : [liste de widget de saisie (QWidget) qui ne doivent
        plus afficher de valeur]
        "switch source menu to update" : [liste de clés (tuples) pour
        lesquelles le menu de gestion de la source est à actualiser],
        "widgets to hide" : [liste de widgets à masquer (QWidget)],
        "widgets to show" : [liste de widgets masqués à afficher (QWidget)] 
        }
        
        EXEMPLES
        --------
        Pour définir manuellement la licence :
        >>> d.change_source((3, (0, (11, (0,)))), "< manuel >")
        """
        
        if self.mode == 'read':
            raise ForbiddenOperation("You can't change a widget's source in reading mode.")
        
        d = {
            "concepts list to update" : [],
            "widgets to empty" : [],
            "switch source menu to update" : [],
            "widgets to hide" : [],
            "widgets to show" : []
            }
            
        khide = None
        kshow = None
        
        old_source = self[key]['current source']
        
        # la nouvelle source est identique à l'ancienne :
        if source == old_source:
            return d
        
        if not self[key]['multiple sources']:
            raise ForbiddenOperation("Key {} doesn't provide multiple sources.".format(key))
            
        if not self[key]['main widget type'] or self[key]['hidden'] \
            or self[key]['hidden M']:
            # surtout important pour le cas d'un double M qui n'a pas été
            # créé ('main widget type' valant None), et qui propose donc une
            # source "< manuel >" qui ne serait pas dans la liste de son jumeau
            raise ForbiddenOperation("Widget {} is hidden, no action is allowed here.".format(key))
            
        if not self[key]['sources'] \
            or not source in self[key]['sources']:
            raise ValueError('Unknown source "{}" for key {}.'.format(source, key))
        
        if old_source == '< non répertorié >':
            # on se hâte de faire disparaître cette option
            # du menu
            if old_source in self[key]['sources']:
                self[key]['sources'].remove(old_source)
                d["switch source menu to update"].append(key)
            
        if source == '< manuel >':
        
            mkey = (key[0], key[1], 'M')
        
            if not len(key) == 2 or not mkey in self:
                raise RuntimeError("Manuel mode doesn't seem implemented for key {} (M key not found).".format(key))
            
            self[key]['current source'] = None
            self[key]['current source URI'] = None
            self[mkey]['current source'] = source
            d["switch source menu to update"].append(mkey)
            
            self[key]['value'] = None
            w = self[key]['main widget']
            if w:
                d["widgets to empty"].append(w)
            
            self[key]['hidden M'] = True
            self[mkey]['hidden M'] = False
            
            for e in ('main widget', 'grid widget', 'label widget', 'minus widget',
                      'language widget', 'switch source widget'):
                      
                w = self[key][e]
                if w:
                    d["widgets to hide"].append(w)
                
                w = self[mkey][e]
                if w and (e != 'minus widget' or not self[mkey]['hide minus button']):
                    d["widgets to show"].append(w)

            kshow = mkey
            
            
        elif old_source == '< manuel >':
            
            ukey = (key[0], key[1])
        
            if not len(key) == 3 or not ukey in self:
                raise RuntimeError("URI mode doesn't seem implemented for key {} (no-M key not found).".format(key))
            
            self[key]['current source'] = None
            self[ukey]['current source'] = source
            if self[ukey]['sources URI']:
                self[ukey]['current source URI'] = self[ukey]['sources URI'][source]
                # provoquerait une erreur si 'source' n'était pas référencé dans
                # 'sources URI', mais ne devrait jamais arriver dès lors que
                # 'sources URI' existe (ce qui exclut de facto le cas < manuel >
                # + < URI >).
            
            d["switch source menu to update"].append(ukey)
            
            # NB : on ne supprime pas les valeurs des branches M masquées, pour
            # éviter à l'utilisateur d'avoir à les resaisir s'il change d'avis.
            # Elles ne seront évidemment pas sauvegardées par build_graph.
            
            self[key]['hidden M'] = True
            self[ukey]['hidden M'] = False
            
            for e in ('main widget', 'grid widget', 'label widget', 'minus widget',
                      'language widget', 'switch source widget'):
                      
                w = self[key][e]
                if w:
                    d["widgets to hide"].append(w)
                
                w = self[ukey][e]
                if w and (e != 'minus widget' or not self[ukey]['hide minus button']):
                    d["widgets to show"].append(w)

            khide = key
            
            if not source == '< URI >':
                d["concepts list to update"].append(ukey)
            
        else:
            # cas d'un simple changement de thésaurus
            self[key]['current source'] = source
            self[key]['current source URI'] = self[key]['sources URI'][source]
            
            if not key in d["switch source menu to update"]:
                d["switch source menu to update"].append(key)
            
            d["concepts list to update"].append(key)
            
            self[key]['value'] = None
            w = self[key]['main widget']
            if w:
                d["widgets to empty"].append(w)
        
        if kshow or khide:
            for k in self.keys():
            # le cas échéant, on boucle sur les descendants pour
            # masquer/afficher le reste de la branche M
            
                if kshow and is_ancestor(kshow, k) and not (
                    self[key]['object'] == 'translation button'
                    and self[key]['hidden']
                    ):
                    # ATTENTION ! Ne fonctionnerait pas si
                    # on commençait à avoir des branches M non
                    # affichées dans une branche M affichée...
                    # Mais ça ne peut pas arriver avec GeoDCAT
                    # dans sa forme actuelle.
                    self[k]['hidden M'] = False

                    for e in ('main widget', 'grid widget', 'label widget', 'minus widget',
                      'language widget', 'switch source widget'):                
                        w = self[k][e]
                        if w and (e != 'minus widget' or not self[k]['hide minus button']):
                            d["widgets to show"].append(w)
                            
                     
                if khide and is_ancestor(khide, k):
                    self[k]['hidden M'] = True
                    
                    for e in ('main widget', 'grid widget', 'label widget', 'minus widget',
                      'language widget', 'switch source widget'):                
                        w = self[k][e]
                        if w:
                            d["widgets to hide"].append(w)
                            # peut contenir des boutons déjà masqués du fait de 'hidden'
                            # ou 'hide minus button'.
                        

        
        return d


    def update_value(self, key, value):
        """Mise à jour de la valeur d'un widget de saisie.
        
        ARGUMENTS
        ---------
        - key (tuple) : une clé du dictionnaire de widgets, et plus
        précisément la clé pour laquelle l'utilisateur vient de
        saisir une nouvelle valeur.
        - value (str) : nouvelle valeur.
        
        RESULTAT
        --------
        Néant.
        
        Le contenu de la clé 'value' du dictionnaire interne de
        la clé key est mise à jour.
        """
        if not self[key]['object'] == 'edit':
            raise ForbiddenOperation("{} is a {}, you can't store a value here.".format(
                key, self[key]['object']))

        if ( self[key]['hidden M'] or self[key]['hidden'] ) \
            and value is not None:
            raise ForbiddenOperation("Widget {} is hidden, you can't update its value.".format(key))

        self[key]['value'] = value


    def build_graph(self, vocabulary, bypass=False):
        """Return a RDF graph build from given widgets dictionary.

        ARGUMENTS
        ---------
        - vocabulary (rdflib.graph.Graph) : graphe réunissant le vocabulaire
        de toutes les ontologies pertinentes.
        - bypass (bool) : à mettre à True pour exécuter la fonction
        sur un dictionnaire dont le mode est 'read', sinon elle renvoie
        une erreur.

        RESULTAT
        --------
        Un graphe RDF de métadonnées (rdflib.graph.Graph).
        """
        if not bypass and self.mode == 'read':
            raise ForbiddenOperation("You can't generate a graph " \
                "from a reading mode widgetsdict.")

        graph = Graph()
        mem = None
        
        l = sorted(self.keys(), key=self.order_keys)
        # liste des clés du graphe, ordonnée de telle
        # façon que :
        # - les enfants apparaissent immédiatement
        # après leur parent (ce qui est l'ordre naturel
        # du dictionnaire, mais les ajouts et suppressions
        # de clés remettent ça en cause) ;
        # - les clés qui ne servent qu'au formulaire
        # (boutons, groupes de valeurs et de traductions)
        # sont à la fin ;
        # - les widgets de saisie vides ou masqués
        # sont à la fin.
        
        for k in l:
        
            d = self[k]
        
            if d['node'] is None and \
                (d['value'] in (None, '') or d['hidden M']):
                break
                # on a atteint la partie de la liste qui ne
                # contient plus aucune information
        
            mObject = None
            
            # cas d'un nouveau noeud
            if d['node']:
            
                mem = (d['subject'], d['predicate'], d['node'], d['class'])
                # on mémorise les informations utiles, mais le noeud
                # n'est pas immédiatement créé, au cas où il n'y aurait
                # pas de métadonnées associées
                
                # ... sauf dans le cas du noeud racine, qui est porteur
                # de l'identifiant, donc créé quoi qu'il arrive
                if k == (0,):
                    graph.add((
                        mem[2],
                        URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
                        mem[3]
                        ))
                    mem = None
                    
            else:
            
                if mem and mem[2] == d['subject']:
                
                    # création effective du noeud vide à partir
                    # des informations mémorisées
                    graph.add((mem[0], mem[1], mem[2]))
                    graph.add((
                        mem[2],
                        URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
                        mem[3]
                        ))                    
                    mem = None
            
                if d['node kind'] == 'sh:Literal':
            
                    mObject = Literal( d['value'], datatype = d['data type'] ) \
                        if not d['data type'] in (
                            URIRef("http://www.w3.org/2001/XMLSchema#string"),
                            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#langString")
                            ) \
                        else Literal( d['value'], lang = d['language value'] )
                                
                else:
        
                    if d['transform'] == 'email':
                        mObject = owlthing_from_email(d['value'])
                        
                    elif d['transform'] == 'phone':
                        mObject = owlthing_from_tel(d['value']) 
                        
                    elif not d['current source URI'] in (None, '< URI >', '< non répertorié >'):
                        mObject = concept_from_value(d['value'], d['current source URI'], vocabulary,
                            self.language, strict=False)
                        
                        if mObject is None:
                            raise ValueError( "'{}' isn't referenced as a label in scheme '{}' for any language.".format(
                                d['value'], d['current source'] )
                                )
                        
                    else:
                        f = forbidden_char(d['value'])                
                        if f:
                            raise ValueError( "Character '{}' is not allowed in ressource identifiers.".format(f) )
                            
                        mObject = URIRef( d['value'] )
                
                graph.add((d['subject'], d['predicate'], mObject))

        return graph


    def replace_uuid(self, new_uuid):
        """Replace widgets dictionnary identifier by a new UUID.
        
        ARGUMENTS
        ---------
        - new_uuid (str ou URIRef) : nouvel UUID pour substitution.
        
        RESULTAT
        --------
        Pas de valeur renvoyée.
        
        EXEMPLES
        --------
        >>> d.replace_uuid("urn:uuid:c41423cc-fb59-443f-86f4-72592a4f6778")
        """
        n = URIRef(new_uuid)
        o = self[(0,)]['node']
        self[(0,)]['node'] = n

        for k, v in self.items():
            if v['subject'] == o:
                v['subject'] = n
            if v['node'] == o:
                v['node'] = n
            if v['path'] == 'dct:identifier':
                v['value'] = strip_uuid(n)

    
    def order_keys(self, key):
        """Fonction de tri des clés du dictionnaire de widgets, à l'usage de build_graph().
        
        ARGUMENTS
        ---------
        - key (tuple) : clé d'un dictionnaire de widgets (WidgetsDict).
        
        RESULTAT
        --------
        Cette fonction a vocation à être utilisée comme valeur du paramètre
        "key" de la fonction sorted().

        """
        if ( self[key]['node'] is None and self[key]['value'] in (None, '') ) \
            or self[key]['hidden M'] or self[key]['do not save']:
            return [9999]
            # tout ce qui n'est pas un groupe de propriétés ou
            # un widget de saisie non masqué contenant une
            # valeur sera mis en vrac à la fin (puisque toutes
            # les autres clés auront une valeur de tri commençant
            # par l'indice de leur racine / onglet, supposée
            # inférieure à 9999.
            
        l = re.findall(r'[0-9]+', str(key))
        l.reverse()
        return [int(x) for x in l]


    def group_kind(self, key):
        """Renvoie la nature du groupe auquel appartient l'enregistrement de clé key.
        
        ARGUMENTS
        ---------
        - key (tuple) : une clé du dictionnaire de widgets (WidgetsDict).
        
        RESULTAT
        --------
        "group of values" si l'enregistrement est un groupe de valeurs ou, s'il
        s'agit d'un widget d'édition ou d'un bouton, si son parent est un groupe
        de valeurs.
        "group of properties" si l'enregistrement est un groupe de propriétés ou,
        s'il s'agit d'un widget d'édition ou d'un bouton, si son parent est un
        groupe de propriétés.
        "translation group" si l'enregistrement est un groupe de traduction ou,
        s'il s'agit d'un widget d'édition ou d'un bouton, si son parent est un
        groupe de traduction.
        
        """
        if self[key]['object'] in (
            'group of values', 'group of properties',
            'translation group'
            ):
            return self[key]['object']
        
        obj = self[key[1]]['object']
        
        if obj in (
            'group of values', 'group of properties',
            'translation group'
            ):
            return obj
            
        raise RuntimeError("Unknown group kind for key {}.".format(key))


    def widget_placement(self, key, kind):
        """Renvoie les paramètres de placement du widget dans la grille.
        
        ARGUMENTS
        ---------
        - key (tuple) : clé du dictionnaire de widgets.
        - kind (str) : nature du widget considéré : 'main widget',
        'minus widget', 'switch source widget', 'language widget',
        'label widget'.
        
        RESULTAT
        --------
        Un tuple avec :
        [0] l'indice de la ligne (row) ;
        [1] l'indice de la colonne (column) ;
        [2] le nombre de lignes occupées (row span) ;
        [3] le nombre de colonnes occupées (column span).
        
        La fonction renvoie None si la nature de widget donnée en
        argument n'est pas une valeur reconnue.
        """
        
        if kind == 'main widget' and 'group' in self[key]['object']:
            return (self[key]['row'], 0, 1, 2)
            
        if kind == 'main widget' and 'button' in self[key]['object']:
            return (self[key]['row'], 0, 1, 1)
            
        if kind == 'main widget' and self[key]['object'] == 'edit':
            rowSpan = self[key]['row span'] or 1
            column = 1 if self[key]['label'] and self[key]['label row'] is None else 0
            columnSpan = 1 if self[key]['label'] and self[key]['label row'] is None else 2
            return (self[key]['row'], column, rowSpan, columnSpan)
            
        if kind == 'label widget':
            row = self[key]['label row'] if self[key]['label row'] is not None \
                else self[key]['row']
            columnSpan = 2 if self[key]['label row'] is not None else 1
            return (row, 0, 1, columnSpan)
            
        if kind == 'minus widget':
            column = 2 + ( 1 if self[key]['multiple sources'] else 0 ) \
                + ( 1 if self[key]['authorized languages'] else 0 )
            return (self[key]['row'], column, 1, 1)
        
        if kind in ('language widget', 'switch source widget'):
            return (self[key]['row'], 2, 1, 1)
  

class InternalDict(dict):
    """Classe pour les dictionnaires internes.
    
    ATTRIBUTS
    ---------
    Aucun.
    
    Un objet de classe InternalDict, ou "dictionnaire interne" est un dictionnaire
    comportant les clés listées ci-après. Les valeurs des dictionnaires de widgets
    (WidgetsDict) sont des dictionnaires internes.
    
    - 'object' : classification des éléments du dictionnaire. "group of values" ou
    "group of properties" ou "translation group" ou "edit" ou "plus button" ou "translation button".
    Les "translation group" et "translation button" ne peuvent exister que si l'attribut
    "translation" vaut True.

    Les clés 'X widget' ci-après ont vocation à accueillir les futurs widgets (qui ne sont pas
    créés par la fonction). Il y a toujours un widget principal, le plus souvent de type
    QGroupBox ou QXEdit, et éventuellement des widgets secondaires. Tous ont le même parent et
    seraient à afficher sur la même ligne de la grille.
    
    - 'main widget' : widget principal.
    - 'grid widget' : widget de type QGridLayout, à créer pour tous les éléments "group of values",
    "group of properties" et "translation group".
    - 'label widget' : pour certains éléments "edit" (concrètement, tous ceux dont
    la clé "label" ci-après n'est pas vide - pour les autres il y a un "group of values" qui porte
    le label), le widget QLabel associé.
    - 'minus widget' : pour les propriétés qui admettent plusieurs valeurs ou qui, de fait, en ont,
    (concrètement celles pour lesquelles la clé "has minus button" vaut True), widget QButtonTool [-]
    permettant de supprimer les widgets.
    - 'language widget' : pour certains widgets "edit" (concrètement, ceux dont 'authorized languages'
    n'est pas vide), widget pour afficher/sélectionner la langue de la métadonnée. Les 'languages
    widget' n'auront vocation à être affiché que si le mode "traduction" est actif, soit un 
    paramètre 'translation' valant True pour la fonction.
    - 'switch source widget' : certaines catégories de métadonnées peuvent prendre une valeur
    parmi plusieurs thésaurus ou permettre de choisir entre une valeur issue d'un thésaurus et
    une valeur saisie manuellement. Le bouton "switch source widget" est un QButtonTool qui permet
    de sélectionner le thésaurus à utiliser ou de basculer en mode manuel. Il doit être implémenté
    dès lors que la clé 'multiple sources' indique True. Cf. aussi 'sources' et 'current sources'.
    
    Parmi les trois derniers boutons seuls deux au maximum pourront être affichés simultanément,
    la combinaison 'language widget' et 'switch source widget' étant impossible.
    
    En complément, des clés sont prévues pour les QMenu et QAction associés à certains widgets.
    
    - 'switch source menu' : pour le QMenu associé au 'switch source widget'.
    - 'switch source actions' : liste des QAction associées au 'switch source menu'.
    - 'language menu' : pour le QMenu associé au 'language widget'.
    - 'language actions' : liste des QAction associées au 'language menu'.   

    Les clés suivantes sont, elles, remplies par la fonction, avec toutes les informations nécessaires
    au paramétrage des widgets.
    
    - 'main widget type'* : type du widget principal (QGroupBox, QLineEdit...). Si cette clé est
    vide, c'est qu'aucun widget ne doit être créé. Ce cas correspond aux catégories de métadonnées
    hors template, dont les valeurs ne seront pas affichées, mais qu'il n'est pas question d'effacer
    pour autant.
    - 'row' : placement vertical (= numéro de ligne) du widget dans la grille (QGridLayout) qui
    organise tous les widgets rattachés au groupe parent (QGroupBox). Initialement, row est
    toujours égal à l'index de la clé, mais il ne le sera plus si les boutons d'ajout/suppression
    de valeurs ont été utilisés.
    - 'row span'* : hauteur du widget, en nombre de lignes de la grille. Spécifié uniquement pour
    certains QTextEdit (valeur par défaut à prévoir).
    - 'label'* : s'il y a lieu de mettre un label (pour les "group of values" et les "edit" ou "node
    group" qui n'ont pas de "group of values" parent), label intégré au widget QGroupBox ou, pour un
    widget "edit", le label du QLabel associé.
    - 'label row' : pour les widgets QTextEdit ou lorsque le label dépasse la longueur définie par
    l'argument labelLengthLimit, il est considéré que le label sera affiché au-dessus de la zone
    de saisie. Dans ce cas 'label row' contient la valeur à donner au paramètre row. Si cette clé
    est vide alors que 'label' contient une valeur, c'est que le label doit être positionné sur
    la même ligne que le widget principal, et son paramètre row est donc fourni par l'index
    contenu dans la clé du dictionnaire externe.
    - 'help text'* : s'il y a lieu, texte explicatif sur la métadonnée. Pourrait être affiché en
    infobulle.
    - 'value' : pour un widget "edit", la valeur à afficher. Elle tient compte à la fois de ce qui
    était déjà renseigné dans la fiche de métadonnées et des éventuelles valeurs par défaut de shape
    et template. Les valeurs par défaut sont utilisées uniquement dans les groupes de propriétés
    vides.
    - 'placeholder text'* : pour un widget QLineEdit ou QTextEdit, éventuel texte à utiliser comme
    "placeholder".
    - 'input mask'* : éventuel masque de saisie.
    - 'language value' : s'il y a lieu de créer un widget secondaire pour spécifier la langue (cf.
    'language widget'), la langue à afficher dans ce widget. Elle est déduite de la valeur lorsqu'il
    y a une valeur, sinon on utilise la valeur de l'argument language de la fonction.
    - 'authorized languages' : liste des langues disponibles dans le 'language widget', s'il y a
    lieu (cf. 'language widget').
    - 'is mandatory'* : booléen indiquant si la métadonnée doit obligatoirement être renseignée.
    - 'has minus button' : booléen indiquant si un bouton de suppression du widget doit être
    créé (cf. minus widget). Sur le principe, ce sera le cas dès qu'une catégorie admet plusieurs
    valeurs ou traductions, ou qu'il y a effectivement plusieurs valeurs saisies (un bouton pour
    chaque valeur).
    - 'hide minus button' : booléen qui vaudra True si le bouton moins doit être masqué parce
    qu'il ne reste qu'un widget dans le groupe de valeurs ou groupe de traduction.
    - 'regex validator pattern' : pour un widget "edit", une éventuelle expression régulière que la
    valeur est censée vérifier. Pour usage par un QRegularExpressionValidator.
    - 'regex validator flags' : flags associés à 'regex validator pattern', le cas échéant.
    - 'type validator' : si un validateur basé sur le type (QIntValidator ou QDoubleValidator) doit
    être utilisé, le nom du validateur.
    - 'sources' : lorsque la métadonnée prend ses valeurs dans une ou plusieurs ontologies /
    thésaurus, liste des sources. La valeur 'manuel' indique qu'une saisie manuelle est possible
    (uniquement via un widget "M").
    - 'multiple sources' : booléen indiquant que la métadonnée fait appel à plusieurs ontologies
    ou autorise à la fois la saisie manuelle et l'usage d'ontologies.
    - 'current source' spécifie la source en cours d'utilisation. Pour un widget "M", vaut
    toujours "manuel" lorsque le widget est en cours d'utilisation, None sinon). Pour un widget
    non "M", il donne le nom littéral de l'ontologie ou "non répertorié" lorsque la valeur
    antérieurement saisie n'apparaît dans aucune ontologie associée à la catégorie, None si le
    widget n'est pas utilisé. La liste des termes autorisés par la source n'est pas directement
    stockée dans le dictionnaire, mais peut être obtenue via la fonction build_vocabulary.
    - 'current source URI' : IRI correspondant à 'current source'.
    - 'read only'* : booléen qui vaudra True si la métadonnée ne doit pas être modifiable par
    l'utilisateur. En mode lecture, 'read only' vaut toujours True.
    - 'hidden' : booléen. Si True, le widget principal doit être masqué. Concerne
    les boutons de traduction, lorsque toutes les langues disponibles (cf. langList) ont été
    utilisées.
    - 'hidden M' : booléen. Si True, le widget principal doit être masqué. Concerne les branches
    M/non M (qui permettent de saisir une métadonnées soit sous forme d'IRI soit sous forme d'un
    ensemble de propriétés littérales) lorsque l'autre forme est utilisée.

    La dernière série de clés ne sert qu'aux fonctions de rdf_utils : 'default value'* (valeur par
    défaut), 'node kind', 'data type'**, 'class', 'path'***, 'subject', 'predicate', 'node',
    'transform', 'default widget type', 'one per language', 'next child' (indice à utiliser si un
    enregistrement est ajouté au groupe), 'multiple values'* (la catégorie est-elle
    censée admettre plusieurs valeurs ?), 'order shape', 'order template'* (ordre des catégories, cette
    clé s'appelle simplement "order" dans le template), 'do not save', 'sources URI', 'default source'.

    * ces clés apparaissent aussi dans le dictionnaire interne de template.
    ** le dictionnaire interne de template contient également une clé 'data type', mais dont les
    valeurs sont des chaînes de catactères parmi 'string', 'boolean', 'decimal', 'integer', 'date',
    'time', 'dateTime', 'duration', 'float', 'double' (et non des objets de type URIRef).
    *** le chemin est la clé principale de template.
    """
    
    def __init__(self):
        """Génère un dictionnaire interne vierge.
        
        ARGUMENTS
        ---------
        Néant.
        
        RESULTAT
        --------
        Un dictionnaire interne (InternalDict) vide.
        """
        
        keys = [
            'object',
            # stockage des widgets :
            'main widget', 'grid widget', 'label widget', 'minus widget',
            'language widget', 'switch source widget',
            'switch source menu', 'switch source actions', 'language menu',
            'language actions',
            # paramétrage des widgets
            'main widget type', 'row', 'row span', 'label', 'label row',
            'help text', 'value', 'language value', 'placeholder text',
            'input mask', 'is mandatory', 'has minus button', 'hide minus button',
            'regex validator pattern', 'regex validator flags', 'type validator',
            'multiple sources', 'sources', 'current source', 'current source URI',
            'authorized languages', 'read only', 'hidden', 'hidden M',
            # à l'usage des fonctions de rdf_utils
            'default value', 'default source', 'multiple values', 'node kind',
            'data type', 'ontology', 'transform', 'class', 'path', 'subject',
            'predicate', 'node', 'default widget type', 'one per language',
            'next child', 'shape order', 'template order', 'do not save',
            'sources URI'
            ]
        
        self.update({ k:None for k in keys })


def build_dict(metagraph, shape, vocabulary, template=None,
    templateTabs=None, columns=None, data=None, mode='edit',
    readHideBlank=True, readHideUnlisted=True, editHideUnlisted=False,
    language="fr", translation=False, langList=['fr', 'en'],
    readOnlyCurrentLanguage=True, editOnlyCurrentLanguage=False,
    labelLengthLimit=25, valueLengthLimit=65, textEditRowSpan=6,
    preserve=False,
    mPath=None, mTargetClass=None, mParentWidget=None, mParentNode=None,
    mNSManager=None, mDict=None, mGraphEmpty=None,  mShallowTemplate=None,
    mTemplateEmpty=None, mGhost=None, mHiddenM=None,
    mTemplateTabs=None, mData=None, mPropMap=None, mPropTemplate=None,
    idx=None, rowidx=None, mVSources=None):
    """Return a dictionary with relevant informations to build a metadata update form. 

    ARGUMENTS
    ---------
    - metagraph (rdflib.graph.Graph) : un graphe de métadonnées, extrait du commentaire
    d'un objet PostgreSQL.
    - shape (rdflib.graph.Graph) : schéma SHACL augmenté décrivant les catégories
    de métadonnées communes.
    - vocabulary (rdflib.graph.Graph) : graphe réunissant le vocabulaire de toutes
    les ontologies pertinentes.
    - [optionnel] template (dict) : dictionnaire contenant les informations relatives au modèle
    de formulaire à utiliser. Fournir un template permet : d'ajouter des métadonnées
    locales aux catégories communes définies dans shape ; de restreindre les catégories
    communes à afficher ; de substituer des paramètres locaux à ceux spécifiés par shape
    (par exemple remplacer le nom à afficher pour la catégorie de métadonnée ou changer
    le type de widget à utiliser). La forme de template est proche de celle du
    dictionnaire résultant de la présente fonction (cf. plus loin) si ce n'est que ses
    clés sont des chemins SPARQL identifiant des catégories de métadonnées et ses
    dictionnaires internes ne comprennent que les clés marquées d'astéristiques. Certains
    caractéristiques ne peuvent être définies que pour les catégories de métadonnées
    locales : il n'est pas possible de changer 'data type' ni 'multiple values' pour une
    catégorie commune.
    - [optionnel] templateTabs (dict) : dictionnaire complémentaire à template, dont les
    clés sont les noms des onglets du formulaire et les valeurs les futures clés
    correspondant aux onglets dans le dictionnaire de widgets. L'ordre des clés dans le
    dictionnaire sera l'ordre des onglets.
    - [optionnel] columns (list) : liste de tuples formés de deux éléments, le premier
    (str) pour le nom du champ, le second (str) pour son descriptif.
    - [optionnel] data (dict) : un dictionnaire contenant des informations actualisées
    à partir de sources externes (par exemple déduites des données) qui devront écraser
    les valeurs présentes dans metagraph. Les clés du dictionnaire sont des chemins
    SPARQL identifiant des catégories de métadonnées, ses valeurs sont des listes
    contenant la ou les valeurs (str) à faire apparaître pour les catégories en question.
    - [optionnel] mode (str) : indique si le formulaire est ouvert pour édition ('edit',
    valeur par défaut), en lecture ('read') ou pour lancer une recherche ('search').
    Le principal effet du mode lecture est la disparition des boutons, notamment les
    "boutons plus" qui faisaient l'objet d'un enregistrement à part dans le dictionnaire.
    ATTENTION !!! le mode recherche n'est pas encore implémenté, il renvoie le même
    dictionnaire que le mode lecture.
    - [optionnel] readHideBlank (bool) : paramètre utilisateur qui indique si les champs
    vides doivent être masqués en mode lecture. True par défaut.
    - [optionnel] readHideUnlisted (bool) : paramètre utilisateur qui indique si les
    catégories hors template doivent être masquées en mode lecture. En l'absence de template,
    si readHideUnlisted vaut True, seules les métadonnées communes seront visibles. True par défaut.
    - [optionnel] editHideUnlisted (bool) : idem readHideUnlisted mais pour le mode édition.
    False par défaut.
    - [optionnel] language (str) : langue principale de rédaction des métadonnées
    (paramètre utilisateur). Français ("fr") par défaut. La valeur de language doit être
    incluse dans langList ci-après.
    - [optionnel] translation (bool) : paramètre utilisateur qui indique si les widgets de
    traduction doivent être affichés. False par défaut.
    - [optionnel] langList (list) : paramètre utilisateur spécifiant la liste des langues
    autorisées pour les traductions (str), par défaut français et anglais, soit ['fr', 'en'].
    - [optionnel] readOnlyCurrentLanguage (bool) : paramètre utilisateur qui indique si,
    en mode lecture, seules les métadonnées saisies dans la langue principale
    (paramètre language) sont affichées. True par défaut.
    À noter que si aucune traduction n'est disponible dans la langue demandée, les valeurs
    d'une langue arbitraire seront affichées. Par ailleurs, lorsque plusieurs traductions
    existent, l'unique valeur affichée apparaîtra quoi qu'il arrive dans un groupe.
    - [optionnel] editOnlyCurrentLanguage (bool) : paramètre utilisateur qui indique si,
    en mode édition et lorsque le mode traduction est inactif, seules les métadonnées
    saisies dans la langue principale (paramètre language) sont affichées. False par défaut.
    À noter que si aucune traduction n'est disponible dans la langue demandée, les valeurs
    d'une langue arbitraire seront affichées. Par ailleurs, lorsque plusieurs traductions
    existent, l'unique valeur affichée apparaîtra quoi qu'il arrive dans un groupe.
    - [optionnel] labelLengthLimit (int) : nombre de caractères au-delà duquel le label sera
    toujours affiché au-dessus du widget de saisie et non sur la même ligne. À noter que
    pour les widgets QTextEdit le label est placé au-dessus quoi qu'il arrive. 25 par défaut.
    - [optionnel] valueLengthLimit (int) : nombre de caractères au-delà duquel une valeur qui
    aurait dû être affichée dans un widget QLineEdit sera présentée à la place dans un QTextEdit.
    Indépendemment du nombre de caractères, la substitution sera aussi réalisée si la
    valeur contient un retour à la ligne. 65 par défaut.
    - [optionnel] textEditRowSpan (int) : nombre de lignes par défaut pour un widget QTextEdit
    (utilisé si non défini par shape ou template). 6 par défaut.
    - [optionnel] preserve (bool) : indique si les valeurs doivent être préservées. Inhibe
    certaines transformation réalisées en mode lecture, notamment pour présenter des
    hyperliens à l'utilisateur, ainsi que la transcription automatique de l'identifiant dans la
    propriété dct:identifier. Valeur par défaut False. preserve n'est pas un paramètre
    utilisateur, il sert pour la recette.

    Les autres arguments sont uniquement utilisés lors des appels récursifs de la fonction
    et ne doivent pas être renseignés manuellement.

    RESULTAT
    --------
    Un dictionnaire (WidgetsDict) avec autant de clés que de widgets à empiler verticalement
    (avec emboîtements). Les valeurs associées aux clés sont elles mêmes des dictionnaires,
    dit "dictionnaires internes", contenant les informations utiles à la création des widgets
    + des clés pour le stockage des futurs widgets.
    
    Les attributs mode, translation, language et langList du dictionnaire de widgets sont
    les arguments de même nom fournis à build_dict (ou leurs valeurs par défaut).

    La clé du dictionnaire externe est un tuple formé :
    [0] d'un index, qui garantit l'unicité de la clé.
    [1] de la clé du groupe parent.
    [2] dans quelques cas, la lettre M, indiquant que le widget est la version "manuelle" d'un
    widget normalement abondé par un ou plusieurs thésaurus. Celui-ci a la même clé sans "M"
    (même parent, même index, même placement dans la grille). Ces deux widgets sont
    supposés être substitués l'un à l'autre dans la grille lorque l'utilisateur active ou
    désactive le "mode manuel" (cf. 'switch source widget' ci-après)
    

    Cf. InternalDict pour la description des clés des dictionnaires internes.
    
    EXEMPLES
    --------
    >>> g.build_dict(shape, template, vocabulary)
    """

    nsm = mNSManager or shape.namespace_manager
    mDataIdentifier = None
    
    # ---------- INITIALISATION ----------
    # uniquement à la première itération de la fonction
    
    if mParentNode is None:

        for n, u in nsm.namespaces():
            metagraph.namespace_manager.bind(n, u, override=True, replace=True)

        mTargetClass = URIRef("http://www.w3.org/ns/dcat#Dataset")
        mPath = None
        mParentNode = None
        mGraphEmpty = ( len(metagraph) == 0 )
        mTemplateEmpty = ( template is None )
        
        # on travaille sur une copie du template pour pouvoir marquer les catégories
        # comme traitées au fur et à mesure de leur traitement par l'itération
        # sur les catégories communes. À l'issue de celle-ci, ne resteront donc "non
        # traitées" que les catégories locales.
        mShallowTemplate = dict()
        if template:
            for tk, tv in template.items():
                mShallowTemplate.update({ tk: tv.copy() })

        # même logique pour data, si ce n'est que les valeurs sont
        # carrément supprimées.
        mData = data.copy() if data else dict()

        # récupération de l'identifiant
        # du jeu de données dans le graphe, s'il existe
        if not mGraphEmpty:
            mParentNode = mParentNode or get_datasetid(metagraph)

        # récupération de l'identifiant dans mData, si présent
        if mData:
            ident = (mData.get("dct:identifier") or [None])[0]
            if ident:
                mDataIdentifier = URIRef("urn:uuid:" + ident)

        # si on n'a pas pu extraire d'identifiant, on en génère un nouveau
        # (et, in fine, le formulaire sera vierge)
        # NB : ici, l'identifiant du graphe prévaut sur celui de data,
        # parce qu'on veut pouvoir récupérer les métadonnées même si
        # l'identifiant a changé. Mais celui de data prévaudra partout
        # ailleurs, et remplacera in fine celui du graphe
        mParentNode = mParentNode or mDataIdentifier \
            or URIRef("urn:uuid:" + str(uuid.uuid4()))
        
        # on stocke l'identifiant dans mData, pour être présenté à
        # l'utilisateur sous dct:identifier (sauf en mode lecture
        # quand l'identifiant n'existe pas encore, car celui qui serait
        # régénéré en cas de bascule en mode édition serait différent)
        if not (mode == 'read' and mGraphEmpty and not mDataIdentifier) \
            and not preserve:
            mData.update({
                'dct:identifier': [strip_uuid(mDataIdentifier or mParentNode)]
                })
            
        # utilitaires pour la récupération des informations
        # contenues dans le schéma SHACL.
        # NB : le second élément des tuples de mPropMap
        # indique si la propriété admet plusieurs valeurs
        mPropMap = {
            "sh:path": ("property", False),
            "sh:name": ("name", False),
            "sh:description": ("descr", False),
            "sh:nodeKind": ("kind", False),
            "sh:order": ("order", False),
            "snum:widget" : ("widget", False),
            "sh:class": ("class", False),
            "snum:placeholder": ("placeholder", False),
            "snum:inputMask": ("mask", False),
            "sh:defaultValue": ("default", False),
            "snum:rowSpan": ("rowspan", False),
            "sh:minCount": ("min", False),
            "sh:maxCount": ("max", False),
            "sh:datatype": ("type", False),
            "sh:uniqueLang": ("unilang", False),
            "sh:pattern": ("pattern", False),
            "sh:flags": ("flags", False),
            "snum:transform": ("transform", False),
            "snum:ontology": ("ontologies", True)
            } 
        mPropTemplate = { v[0]: None for v in mPropMap.values() }

        # liste des onglets
        mTemplateTabs = templateTabs.copy() if templateTabs \
                        else { "Général": (0,) }
        if columns and not "Champs" in mTemplateTabs:
            # le cas échéant, on ajoute un onglet pour les
            # descriptifs des champs
            i = max([ k[0] for k in mTemplateTabs.values() ]) + 1
            mTemplateTabs.update({ "Champs": (i,) })

        # on initialise le dictionnaire avec les groupes racines,
        # qui correspondent aux onglets du formulaire :
        mDict = WidgetsDict(mode=mode, translation=translation,
            language=language, langList=langList)
        n = 0
        for label, key in mTemplateTabs.items():        
            mDict.update( { key : InternalDict() } )
            mDict[key].update( {
                'object' : 'group of properties',
                'main widget type' : 'QGroupBox',
                'label' : label or '???',
                'row' : 0,
                'node' : mDataIdentifier or mParentNode,
                'class' : URIRef('http://www.w3.org/ns/dcat#Dataset'),
                'shape order' : key[0],
                'do not save' : n > 0
                } )
            n += 1

        mParentWidget = (0,)
        
        idx = dict()
        rowidx = dict()


    # ---------- EXECUTION COURANTE ----------

    idx.update( { mParentWidget : 0 } )
    rowidx.update( { mParentWidget : 0 } )

    # on identifie la forme du schéma SHACL qui décrit la
    # classe cible :
    for s in shape.subjects(
        URIRef("http://www.w3.org/ns/shacl#targetClass"),
        mTargetClass
        ):
        mShape = s
        break

    # --- BOUCLE SUR LES CATEGORIES
    
    for mShapeProperty in shape.objects(
        mShape,
        URIRef("http://www.w3.org/ns/shacl#property")
        ):
        
        # récupération des informations relatives
        # à la catégorie dans le schéma SHACL
        p = mPropTemplate.copy()
        for a, b in shape.predicate_objects(mShapeProperty):
            if a.n3(nsm) in mPropMap:
                if mPropMap[a.n3(nsm)][1]:
                    p[mPropMap[a.n3(nsm)][0]] = (p[mPropMap[a.n3(nsm)][0]] or []) + [b]
                else:
                    p[mPropMap[a.n3(nsm)][0]] = b

        mParent = mParentWidget
        mProperty = p['property']
        mKind = p['kind'].n3(nsm)
        mNPath = ( mPath + " / " if mPath else '') + mProperty.n3(nsm)
        mSources = {}
        mDefault = None
        mDefaultBrut = None
        mDefaultSource = None
        mDefaultSourceURI = None
        mDefaultPage = None
        mLangList = None
        mNGhost = mGhost or False
        mOneLanguage = None
        values = None
        
        multilingual = p['unilang'] and (str(p['unilang']).lower() == 'true') or False
        multiple = ( p['max'] is None or int( p['max'] ) > 1 ) and not multilingual

        # cas d'une propriété dont les valeurs sont mises à
        # jour à partir d'informations disponibles côté serveur
        if mData and mNPath in mData:
            values = mData[mNPath].copy()
            del mData[mNPath]

        # sinon, on extrait la ou les valeurs éventuellement
        # renseignées dans le graphe pour cette catégorie
        # et le sujet considéré
        if not values and not mGraphEmpty: 
            values = [ o for o in metagraph.objects(mParentNode, mProperty) ]
    
        # exclusion des catégories qui ne sont pas prévues par
        # le modèle, ne sont pas considérées comme obligatoires
        # par shape et n'ont pas de valeur renseignée
        # les catégories obligatoires de shape sont affichées
        # quoi qu'il arrive en mode édition
        # les catégories sans valeurs sont éliminées indépendemment
        # du modèle en mode lecture quand readHideBlank vaut True
        if values in ( None, [], [ None ] ) and (
            ( readHideBlank and mode == 'read' ) \
            or ( not mTemplateEmpty  and not ( mNPath in template ) \
                and not ( mode == 'edit' and p['min'] and int(p['min']) > 0 ) ) \
            ):
            continue
        # s'il y a une valeur, mais que
        # read/editHideUnlisted vaut True et que la catégorie n'est
        # pas prévue par le modèle, on poursuit le traitement
        # pour ne pas perdre la valeur, mais on ne créera
        # pas de widget
        # les catégories obligatoires de shape sont affichées
        # quoi qu'il arrive
        elif ( (mode == 'edit' and editHideUnlisted) or \
            (mode == 'read' and readHideUnlisted) ) \
            and not mTemplateEmpty and not ( mNPath in template ) \
            and not ( p['min'] and int(p['min']) > 0 ):
            mNGhost = True
        
        values = values or [ None ]
        
        if not mNGhost and ( mNPath in mShallowTemplate ):
            t = mShallowTemplate[mNPath]
            mShallowTemplate[mNPath].update( { 'done' : True } )
            
            # choix du bon onglet (évidemment juste
            # pour les catégories de premier niveau)
            if is_root(mParent):
                tab = t.get('tab name', None)
                if tab and tab in mTemplateTabs:
                    mParent = mTemplateTabs[tab]
                    if not mParent in idx:
                        idx.update({ mParent: 0 })
                    if not mParent in rowidx:
                        rowidx.update({ mParent: 0 })
            
        else:
            t = dict()
            if not mNGhost and not mTemplateEmpty \
                and is_root(mParent):
                # les métadonnées hors modèle non masquées
                # de premier niveau iront dans un onglet "Autres".
                # S'il n'existe pas encore, on l'ajoute :
                if not "Autres" in mTemplateTabs:
                    i = max([ k[0] for k in mTemplateTabs.values() ]) + 1
                    mParent = (i,)
                    mTemplateTabs.update({ "Autres": mParent })
                    mDict.update( { mParent : InternalDict() } )
                    mDict[mParent].update( {
                        'object' : 'group of properties',
                        'main widget type' : 'QGroupBox',
                        'label' : "Autres",
                        'row' : 0,
                        'node' : mParentNode,
                        'class' : URIRef('http://www.w3.org/ns/dcat#Dataset'),
                        'shape order' : i,
                        'do not save' : True
                        } )
                else:
                    mParent = mTemplateTabs["Autres"]
                    
                if not mParent in idx:
                    idx.update({ mParent: 0 })
                if not mParent in rowidx:
                    rowidx.update({ mParent: 0 })


        if mNGhost:
            # cas d'une catégorie qui ne sera pas affichée à l'utilisateur, car
            # absente du template, mais pour laquelle une valeur était renseignée
            # et qu'il s'agit de ne pas perdre
        
            if len(values) > 1:               
                # si plusieurs valeurs étaient renseignées, on référence un groupe
                # de valeurs (dans certains cas un groupe de traduction aurait été plus
                # adapté, mais ça n'a pas d'importance) sans aucune autre propriété
                mWidget = ( idx[mParent], mParent )
                mDict.update( { mWidget : InternalDict() } )
                mDict[mWidget].update( {
                    'object' : 'group of values'
                    } )

                idx[mParent] += 1
                idx.update( { mWidget : 0 } )
                mParent = mWidget        
        
        else:
            # récupération de la liste des thésaurus
            if mKind in ("sh:BlankNodeOrIRI", "sh:IRI") and p['ontologies']:

                for s in p['ontologies']:
                    lt = [ o for o in vocabulary.objects(
                        s, URIRef("http://www.w3.org/2004/02/skos/core#prefLabel")
                        ) ]
                    st = pick_translation(lt, language) if lt else None
                    if st:
                        mSources.update({ s: str(st) })
                        # si t vaut None, c'est que le thésaurus n'est pas
                        # référencé dans vocabulary, dans ce cas, on l'exclut

            # traitement de la valeur par défaut :
            mDefault = t.get('default value') or None
            if mDefault:
                if mSources:
                    for s in mSources:
                        # comme on ne sait pas de quel thésaurus provient le concept
                        # on les teste tous jusqu'à trouver le bon
                        mDefaultBrut = concept_from_value(
                            mDefault, s, vocabulary, language, strict=False
                            )
                        if mDefaultBrut:
                            mDefaultSourceURI = s
                            mDefaultSource = mSources.get(mDefaultSourceURI)
                            mDefault, mDefaultPage = value_from_concept(
                                mDefaultBrut, vocabulary, language, getpage=True,
                                getschemeStr=False, getschemeIRI=False, getconceptStr=True
                                )
                            # NB : on retourne chercher mDefault, car la langue de la valeur
                            # du template n'était pas nécessairement la bonne
                            break
                    # s'il y a le moindre problème avec la valeur par défaut, on la rejette :
                    if mDefault is None or mDefaultBrut is None or mDefaultSource is None:
                        mDefault = mDefaultBrut = mDefaultSource = mDefaultPage = mDefaultSourceURI = None
                elif mKind in ("sh:BlankNodeOrIRI", "sh:IRI") and forbidden_char(mDefault) is None:
                    mDefaultBrut = URIRef(mDefault)
                    
            elif p['default']:
                mDefaultBrut = p['default']
                if mSources:
                    mDefault, mDefaultPage, mDefaultSourceURI = value_from_concept(
                        mDefaultBrut, vocabulary, language, getpage=True, getschemeIRI=True,
                        getschemeStr=False, getconceptStr=True
                        )
                    mDefaultSource = mSources.get(mDefaultSourceURI)
                    # s'il y a le moindre problème avec la valeur par défaut, on la rejette :
                    if mDefault is None or mDefaultBrut is None or mDefaultSource is None:
                        mDefault = mDefaultBrut = mDefaultSource = mDefaultPage = mDefaultSourceURI = None
                elif mKind == 'sh:Literal' and p['type'].n3(nsm) == 'rdf:langString' \
                    and (not isinstance(p['default'], Literal) \
                    or not p['default'].language == language):
                    # une valeur par défaut litérale qui n'est pas dans la langue
                    # principale de saisie n'est pas conservée
                    mDefaultBrut = None
                    
            # propriété qui admet à la fois des valeurs manuelles (noeuds vides)
            # et des IRI
            if mKind == 'sh:BlankNodeOrIRI':
                if not mSources:
                    mSources.update({ "< URI >": "< URI >" })
                mSources.update({ "< manuel >": "< manuel >" })
            
            # si seules les métadonnées dans la langue
            # principale doivent être affichées et qu'aucune valeur n'est
            # disponible dans cette langue, on prendra le parti d'afficher
            # arbitrairement les valeurs de la première langue venue
            if ( ( mode == 'read' and readOnlyCurrentLanguage ) or
                   ( mode == 'edit' and editOnlyCurrentLanguage and not translation ) ) \
                and not any([ not isinstance(v, Literal) or v.language in (None, language) \
                              for v in values ]):
                    for v in values:
                        if isinstance(v, Literal) and v.language:
                            mOneLanguage = v.language
                            break
            
            if translation and multilingual:
                mLangList = [ l for l in langList or [] if not l in [ v.language for v in values if isinstance(v, Literal) ] ]
                # à ce stade, mLangList contient toutes les langues de langList pour lesquelles
                # aucune tranduction n'est disponible. On y ajoutera ensuite la langue de la valeur
                # courante pour obtenir la liste à afficher dans son widget de sélection de langue
            
            if len(values) > 1 or ( ( ( translation and multilingual ) or multiple )
                    and not ( mode == 'read' and readHideBlank ) ):
                
                # si la catégorie admet plusieurs valeurs ou traductions,
                # on référence un widget de groupe
                mWidget = ( idx[mParent], mParent )
                mDict.update( { mWidget : InternalDict() } )
                mDict[mWidget].update( {
                    'object' : 'translation group' if ( multilingual and translation ) else 'group of values',
                    'main widget type' : 'QGroupBox',
                    'row' : rowidx[mParent],
                    'label' : t.get('label', None) or str(p['name']),
                    'help text' : t.get('help text', None) or ( str(p['descr']) if p['descr'] else None ),
                    'hidden M' : mHiddenM,
                    'path' : mNPath,
                    'shape order' : int(p['order']) if p['order'] is not None else None,
                    'template order' : int(t.get('order')) if t.get('order') is not None else None
                    } )

                idx[mParent] += 1
                rowidx[mParent] += 1
                idx.update( { mWidget : 0 } )
                rowidx.update( { mWidget : 0 } )
                mParent = mWidget
                # les widgets de saisie référencés juste après auront
                # ce widget de groupe pour parent
                
                
            mLabel = ( t.get('label', None) or str(p['name']) ) if (
                        ( mode == 'read' and len(values) <= 1 ) or not (
                        multiple or len(values) > 1 or ( multilingual and translation ) ) ) else None
                        
            mHelp = t.get('help text', None) or ( str(p['descr']) if p['descr'] else None )


        # --- BOUCLE SUR LES VALEURS
        
        for mValueBrut in values:
            
            mValue = None
            mCurSource = None
            mCurSourceURI = None
            mVSources = mSources.copy() if mSources is not None else None
            mVHiddenM = None
            mVLangList = mLangList.copy() if mLangList is not None else None
            mLanguage = ( ( mValueBrut.language if isinstance(mValueBrut, Literal) else None ) or language ) if (
                        mKind == 'sh:Literal' and p['type'].n3(nsm) == 'rdf:langString' ) else None
            mNGraphEmpty = mGraphEmpty
            mPage = None
            
            # cas d'un noeud vide :
            # on ajoute un groupe et on relance la fonction sur la classe du noeud
            if mKind in ( 'sh:BlankNode', 'sh:BlankNodeOrIRI' ) and (
                    not readHideBlank or not mode == 'read' or isinstance(mValueBrut, BNode) ):

                # cas d'une branche fantôme
                if mNGhost and isinstance(mValueBrut, BNode):
                    
                    mNode = mValueBrut
                    mWidget = ( idx[mParent], mParent )
                    mDict.update( { mWidget : InternalDict() } )
                    mDict[mWidget].update( {
                        'object' : 'group of properties',
                        'node kind' : mKind,
                        'class' : p['class'],
                        'path' : mNPath,
                        'subject' : mDataIdentifier or mParentNode,
                        'predicate' : mProperty,
                        'node' : mNode
                        } )
                    idx[mParent] += 1                    
                    idx.update( { mWidget : 0 } )

                # branche visible
                elif not mNGhost:
                
                    mNGraphEmpty = mGraphEmpty or mValueBrut is None              
                    mNode = mValueBrut if isinstance(mValueBrut, BNode) else BNode()

                    if mKind == 'sh:BlankNodeOrIRI':
                        mCurSource = "< manuel >" if isinstance(mValueBrut, BNode) else None
                    
                    # cas d'un double M quand la source "< manuel >" n'est pas sélectionnée
                    # on voudra créer les widgets, mais ils ne seront affichés que si
                    # l'utilisateur bascule sur "< manuel >".
                    mVHiddenM = mHiddenM or ( ( mCurSource is None ) if mKind == 'sh:BlankNodeOrIRI' else None )

                    mWidget = ( idx[mParent], mParent, 'M' ) if mKind == 'sh:BlankNodeOrIRI' else ( idx[mParent], mParent )
                    mDict.update( { mWidget : InternalDict() } )
                    mDict[mWidget].update( {
                        'object' : 'group of properties',
                        'main widget type' : 'QGroupBox',
                        'row' : rowidx[mParent],
                        'label' : mLabel,
                        'help text' : mHelp,
                        'has minus button' : mode == 'edit' and ( multiple or len(values) > 1 ),
                        'hide minus button': len(values) <= 1 if ( mode == 'edit' and ( multiple or len(values) > 1 ) ) \
                            else None,
                        'multiple values' : multiple,
                        'node kind' : mKind,
                        'class' : p['class'],
                        'path' : mNPath,
                        'subject' : mDataIdentifier or mParentNode,
                        'predicate' : mProperty,
                        'node' : mNode,
                        'multiple sources' : mKind == 'sh:BlankNodeOrIRI' and mode == 'edit',
                        'current source' : mCurSource,
                        'sources' : [v for v in mVSources.values()] if mode == 'edit' else None,
                        'hidden M' : mVHiddenM,
                        'shape order' : int(p['order']) if p['order'] is not None else None,
                        'template order' : int(t.get('order')) if t.get('order') is not None else None
                        } )

                    if mKind == 'sh:BlankNode' or ( mode == 'read'
                        and isinstance(mValueBrut, BNode) ):
                        # s'il n'y a pas lieu de créer un widget jumeau
                        # pour un IRI, on incrémente tout de suite les compteurs
                        idx[mParent] += 1
                        rowidx[mParent] += 1
                        
                    idx.update( { mWidget : 0 } )
                    rowidx.update( { mWidget : 0 } )

                if not mNGhost or isinstance(mValueBrut, BNode):              
                    build_dict(
                        metagraph, shape, vocabulary, template=template, templateTabs=templateTabs,
                        columns=columns, data=data, mode=mode, readHideBlank=readHideBlank,
                        readHideUnlisted=readHideUnlisted, editHideUnlisted=editHideUnlisted,
                        language=language, translation=translation, langList=langList,
                        readOnlyCurrentLanguage=readOnlyCurrentLanguage,
                        editOnlyCurrentLanguage=editOnlyCurrentLanguage,
                        labelLengthLimit=labelLengthLimit, valueLengthLimit=valueLengthLimit,
                        textEditRowSpan=textEditRowSpan, preserve=preserve,
                        mPath=mNPath, mTargetClass=p['class'],
                        mParentWidget=mWidget,  mParentNode=mNode, mNSManager=mNSManager,
                        mDict=mDict, mGraphEmpty=mNGraphEmpty,
                        mShallowTemplate=mShallowTemplate, mTemplateEmpty=mTemplateEmpty,
                        mGhost=mNGhost, mHiddenM=mVHiddenM, mTemplateTabs=mTemplateTabs,
                        mData=mData, mPropMap=mPropMap, mPropTemplate=mPropTemplate,
                        idx=idx, rowidx=rowidx, mVSources=mVSources
                        )

            # pour tout ce qui n'est pas un pur noeud vide :
            # on ajoute un widget de saisie, en l'initialisant avec
            # une représentation lisible de la valeur
            if not ( mKind == 'sh:BlankNode' \
                or ( mode == 'read' and isinstance(mValueBrut, BNode) ) ):
                      
                # cas d'une valeur appartenant à une branche fantôme
                # ou d'une traduction dans une langue qui n'est pas
                # supposée être affichée (c'est à dire toute autre
                # langue que celle qui a été demandée ou la langue
                # de substitution fournie par mOneLanguage)
                if mNGhost or ( \
                    ( ( mode == 'read' and readOnlyCurrentLanguage ) \
                        or ( mode == 'edit' and editOnlyCurrentLanguage and not translation ) ) \
                    and isinstance(mValueBrut, Literal) \
                    and not mValueBrut.language in (None, language, mOneLanguage) ):
                
                    if isinstance(mValueBrut, BNode):
                        continue   
                        
                    mDict.update( { ( idx[mParent], mParent ) : InternalDict() } )
                    mDict[ ( idx[mParent], mParent ) ].update( {
                        'object' : 'edit',                      
                        'value' : mValueBrut,                        
                        'language value' : mLanguage,                        
                        'node kind' : mKind,
                        'data type' : p['type'],
                        'class' : p['class'],
                        'path' : mNPath,
                        'subject' : mDataIdentifier or mParentNode,
                        'predicate' : mProperty                      
                        } )
                
                    idx[mParent] += 1
                    continue
                
                if isinstance(mValueBrut, BNode):
                    mValueBrut = None
                    
                if  multilingual and translation and mLanguage:
                    mVLangList = mVLangList + [ mLanguage ] if not mLanguage in mVLangList else mVLangList
                elif translation and mLanguage:
                    mVLangList = [ mLanguage ] + ( langList or [] ) if not mLanguage in ( langList or [] ) else langList.copy()
                
                # cas d'une catégorie qui tire ses valeurs d'une
                # ontologie : on récupère le label à afficher
                if mVSources:
                    if isinstance(mValueBrut, URIRef) \
                        and any(not k in ("< URI >", "< manuel >") for k in mVSources.keys()):
                        mValue, mPage, mCurSourceURI = value_from_concept(
                            mValueBrut, vocabulary, language, getpage=True, getschemeStr=False,
                            getschemeIRI=True, getconceptStr=True
                            )
                            # pourrait renvoyer une valeur dans une autre langue
                            # que language, mais on retrouvera la même dans la liste
                            # obtenue avec build_vocabulary()
                        mCurSource = mSources.get(mCurSourceURI)
                        if mValue is None or not mCurSourceURI in mVSources:
                            mCurSource = '< non répertorié >'
                            mVSources.update({mCurSource : mCurSource})

                    elif mGraphEmpty and ( mValueBrut is None ):
                        mCurSource = mDefaultSource
                        mCurSourceURI = mDefaultSourceURI
                        # dans le cas d'un graphe vide,
                        # on s'assure que la valeur par défaut, s'il y en a une,
                        # est associée à la bonne source

                    if mCurSource is None:
                        # cas où la valeur n'était pas renseignée - ou n'est pas un IRI
                        if "< URI >" in mVSources:
                            # cas où l'utilisateur a le choix entre le mode manuel
                            # et des URI en saisie libre
                            mCurSource = "< URI >"
                        elif mValueBrut:
                            mCurSource = '< non répertorié >'
                            mVSources.update({mCurSource : mCurSource})
                        else:
                            # pas de valeur, on prend la première source
                            # répertorié
                            for sk, sv in mVSources.items():
                                mCurSourceURI = sk
                                mCurSource = sv
                                break

                    elif mCurSource == "< manuel >":
                        # la saisie est faite sur le noeud vide
                        # c'est à lui de porter le nom de la source
                        # courante
                        mCurSource = None
                        mCurSourceURI = None # devrait déjà être le cas
                        
                    if mode == 'read':
                        mVSources = None

                # cas d'un numéro de téléphone. on transforme
                # l'IRI en quelque chose d'un peu plus lisible
                if mValueBrut and str(p['transform']) == 'phone':
                    mValue = tel_from_owlthing(mValueBrut)
                if mDefaultBrut and str(p['transform']) == 'phone':
                    mDefault = tel_from_owlthing(mDefaultBrut)

                # cas d'une adresse mél. on transforme
                # l'IRI en quelque chose d'un peu plus lisible
                if mValueBrut and str(p['transform']) == 'email':
                    mValue = email_from_owlthing(mValueBrut)
                if mDefaultBrut and str(p['transform']) == 'email':
                    mDefault = email_from_owlthing(mDefaultBrut)
                    
                if mDefaultBrut is not None:
                    mDefault = mDefault or str(mDefaultBrut)
                    
                if mGraphEmpty and ( mValueBrut is None ):
                    # NB : la condition sur mValueBrut est nécessaire,
                    # car on peut avoir des valeurs issues de data
                    # dans un graphe vide
                    mValueBrut = mDefaultBrut
                    mValue = mDefault
                    mPage = mDefaultPage

                if mValueBrut and mKind in ("sh:BlankNodeOrIRI", "sh:IRI") \
                    and mode == 'read' and not preserve:
                    mValue = text_with_link(mValue or str(mValueBrut), mPage or mValueBrut)
                    # en mode lecture, on modifie la valeur
                    # pour présenter un lien au lieu du texte brut
                elif mValueBrut is not None:
                    mValue = mValue or str(mValueBrut)

                mWidgetType = t.get('main widget type', None) or str(p['widget']) or "QLineEdit"
                 
                mLabelRow = None

                if mWidgetType == "QComboBox" and ( ( not mVSources ) \
                    or '< URI >' in mVSources ):
                    mWidgetType = "QLineEdit"
                    # le schéma SHACL prévoira généralement un QComboBox
                    # pour les URI, mais on est dans un cas où, pour on ne sait quelle
                    # raison, aucun thésaurus n'est disponible. Dans ce cas on affiche
                    # un QLineEdit à la place.
                    
                mDefaultWidgetType = mWidgetType
                
                if mWidgetType == "QLineEdit" and mValue and ( len(mValue) > valueLengthLimit \
                    or mValue.count("\n") > 0 ) and not mVSources:
                    mWidgetType = 'QTextEdit'
                    # on fait apparaître un QTextEdit à la place du QLineEdit quand
                    # la longueur du texte dépasse le seuil valueLengthLimit ou
                    # s'il contient des retours à la ligne, et que ce n'est pas un IRI
                    # on exclut les valeurs avec sources, car il est essentiel de maîtriser
                    # leur rowSpan, particulièrement quand il y a un jumeau M.
                    
                if mDefaultWidgetType == "QLineEdit" and mDefault and ( len(mDefault) > valueLengthLimit \
                    or mDefault.count("\n") > 0 ) and not mVSources:
                    mDefaultWidgetType = 'QTextEdit'
                    # idem avec le widget par défaut et la valeur par défaut
                
                if mLabel and ( mWidgetType == 'QTextEdit' or len(mLabel) > labelLengthLimit ):
                    mLabelRow = rowidx[mParent]
                    rowidx[mParent] += 1
                    
                if ( mode == 'read' ) and mWidgetType in ("QLineEdit", "QTextEdit",
                    "QComboBox", "QDateEdit", "QDateTimeEdit"):
                    mWidgetType = 'QLabel'
                    
                mRowSpan = ( t.get('row span', None) or ( int(p['rowspan']) if p['rowspan'] else textEditRowSpan ) ) \
                           if mWidgetType == 'QTextEdit' else None

                mDict.update( { ( idx[mParent], mParent ) : InternalDict() } )
                mDict[ ( idx[mParent], mParent ) ].update( {
                    'object' : 'edit',
                    'main widget type' : mWidgetType,
                    'row' : rowidx[mParent],
                    'row span' : mRowSpan,
                    'input mask' : ( t.get('input mask', None) or ( str(p['mask']) if p['mask'] else None ) \
                        ) if mode == 'edit' else None,
                    'label' : mLabel,
                    'label row' : mLabelRow,
                    'help text' : mHelp,
                    'value' : mValue,
                    'placeholder text' : ( t.get('placeholder text', None) or ( str(p['placeholder']) if p['placeholder'] else mCurSource ) 
                        ) if mWidgetType in ( 'QTextEdit', 'QLineEdit', 'QComboBox' ) and mode == 'edit' else None,
                    'language value' : mLanguage,
                    'is mandatory' : ( t.get('is mandatory', None) or ( int(p['min']) > 0 if p['min'] else False ) )
                        if mode == 'edit' else None,
                    'has minus button' : mode == 'edit' and ( ( multilingual and translation and mVLangList and len(mVLangList) > 1 )
                        or multiple or len(values) > 1 ),
                    'hide minus button' : len(values) <= 1 if ( mode == 'edit' and (
                        ( multilingual and translation and mVLangList and len(mVLangList) > 1 ) or multiple or len(values) > 1 ) ) \
                        else None,
                    'regex validator pattern' : str(p['pattern']) if p['pattern'] and mode == 'edit' else None,
                    'regex validator flags' : str(p['flags']) if p['flags'] and mode == 'edit' else None,
                    'default value' : mDefault,
                    'default source' : mDefaultSource,
                    'multiple values' : multiple,
                    'node kind' : mKind,
                    'data type' : p['type'],
                    'class' : p['class'],
                    'path' : mNPath,
                    'subject' : mDataIdentifier or mParentNode,
                    'predicate' : mProperty,
                    'default widget type' : mDefaultWidgetType,
                    'transform' : str(p['transform']) if p['transform'] else None,
                    'type validator' : None if mode == 'read' else (
                        'QIntValidator' if p['type'] and p['type'].n3(nsm) == "xsd:integer" else (
                        'QDoubleValidator' if p['type'] and p['type'].n3(nsm) in ("xsd:decimal", "xsd:float", "xsd:double") \
                        else None )),
                    'multiple sources' : len(mVSources) > 1 if mVSources and mode == 'edit' else False,
                    'current source' : mCurSource,
                    'current source URI': mCurSourceURI,
                    'sources' : sorted([sv for sv in mVSources.values()]) if mVSources else None,
                    'sources URI': { v: k for k, v in mSources.items() },
                    'one per language' : multilingual,
                    'authorized languages' : sorted(mVLangList) if ( mode == 'edit' and mVLangList ) else None,
                    'read only' : ( mode == 'read' ) or t.get('read only', False),
                    'hidden M' : mHiddenM or ( ( mCurSource is None ) if mKind == 'sh:BlankNodeOrIRI' else None ),
                    'shape order' : int(p['order']) if p['order'] is not None else None,
                    'template order' : int(t.get('order')) if t.get('order') is not None else None
                    } )
                
                idx[mParent] += 1
                rowidx[mParent] += ( mRowSpan or 1 )

        
        if mDict[mParent]['object'] in ('group of values', 'translation group'):
        
            if rowidx.get(mParent) == 0:
                # on vient de créer un groupe de valeurs... qui n'en contient finalement
                # aucune (cas rare où les enfants auraient été des groupes de propriétés,
                # mais toutes les propriétés en question sont hors template)
                if idx[mParent] == 0:
                    del mDict[mParent]
                else:
                    mDict[mParent]['main widget type'] = None
                rowidx[mParent[1]] -= 1
                
            elif not mNGhost and mode == 'edit' and \
                ( ( multilingual and translation and mVLangList and len(mVLangList) > 1 ) \
                or multiple ):
                
                # référencement d'un widget bouton pour ajouter une valeur
                # si la catégorie en admet plusieurs
                mDict.update( { ( idx[mParent], mParent ) : InternalDict() } )
                mDict[ ( idx[mParent], mParent ) ].update( {
                    'object' : 'translation button' if multilingual else 'plus button',
                    'main widget type' : 'QToolButton',
                    'row' : rowidx[mParent],
                    'next child' : idx[mParent] + 1,
                    'hidden M' : mHiddenM,
                    'hidden' :  len(mVLangList) == 1 if multilingual else None,
                    'path' : mNPath,
                    'help text': 'Ajouter une traduction' if multilingual \
                        else 'Ajouter un élément « {} »'.format(t.get('label', None) or str(p['name']) or '')
                    } )
                
                idx[mParent] += 1
                rowidx[mParent] += 1
            


    # ---------- METADONNEES LOCALES DEFINIES PAR LE MODELE ----------
    
    if mTargetClass == URIRef("http://www.w3.org/ns/dcat#Dataset"):

        for meta, t in mShallowTemplate.items():

            if t.get('done', False):
                # on passe les catégories déjà traitées
                continue

            if not is_valid_minipath(meta, nsm):
                # on élimine d'office les catégories locales dont
                # l'identifiant n'est pas un chemin SPARQL valide
                # à un seul élément et dont le préfixe éventuel
                # est déjà référencé
                continue
                
            mProperty = uripath_from_sparqlpath(meta, nsm, strict=False)
            if mProperty is None:
                continue
                
            mParent = mParentWidget
            
            # choix du bon onglet
            if is_root(mParent):
                # NB. Aussi longtemps que les catégories locales
                # seront toutes de premier niveau, cette condition
                # devrait toujours être vérifiée
                tab = t.get('tab name', None)
                if tab and tab in mTemplateTabs:
                    mParent = mTemplateTabs[tab]
                    if not mParent in idx:
                        idx.update({ mParent: 0 })
                    if not mParent in rowidx:
                        rowidx.update({ mParent: 0 })

            mType = uripath_from_sparqlpath(
                t.get('data type', None) or 'xsd:string',
                nsm, strict=False
                ) or URIRef('http://www.w3.org/2001/XMLSchema#string')

            # on extrait la ou les valeurs éventuellement
            # renseignées dans le graphe pour cette catégorie
            values = [ o for o in metagraph.objects(mParentNode, mProperty) ] \
                if mode == 'read' and readHideBlank else \
                ( [ o for o in metagraph.objects(mParentNode, mProperty) ] \
                or [ t.get('default value', None) if mGraphEmpty else None ] )

            multiple = t.get('multiple values', False)

            if len(values) > 1 or ( multiple and not ( mode == 'read' and readHideBlank ) ):
 
                mWidget = ( idx[mParent], mParent )
                mDict.update( { mWidget : InternalDict() } )
                mDict[mWidget].update( {
                    'object' : 'group of values',
                    'main widget type' : 'QGroupBox',
                    'row' : rowidx[mParent],
                    'label' : t.get('label', None) or "???",
                    'help text' : t.get('help text', None),
                    'path' : meta,
                    'template order' : int(t.get('order')) if t.get('order') is not None else None
                    } )

                idx[mParent] += 1
                rowidx[mParent] += 1
                idx.update( { mWidget : 0 } )
                rowidx.update( { mWidget : 0 } )
                mParent = mWidget


            for mValueBrut in values:
                
                # on considère que toutes les valeurs sont des Literal
                mValue = str(mValueBrut) if mValueBrut else None
                
                mLanguage = ( ( mValueBrut.language if mValueBrut and isinstance(mValueBrut, Literal) else None ) or language
                                 ) if mType.n3(nsm) == 'rdf:langString' else None
                                 
                mVLangList = ( [ mLanguage ] + ( langList.copy() or [] ) if not mLanguage in ( langList or [] ) \
                            else langList.copy()) if mLanguage and translation else None

                mWidgetType = t.get('main widget type', None) or "QLineEdit"
                mDefaultWidgetType = mWidgetType
                mLabel = ( t.get('label', None) or "???" ) if not ( multiple or len(values) > 1 ) else None
                mLabelRow = None

                if mWidgetType == "QLineEdit" and mValue and ( len(mValue) > valueLengthLimit \
                    or mValue.count("\n") > 0 ):
                    mWidgetType = 'QTextEdit'

                if mLabel and ( mWidgetType == 'QTextEdit' or len(mLabel) > labelLengthLimit ):
                    mLabelRow = rowidx[mParent]
                    rowidx[mParent] += 1

                if ( mode == 'read' ) and mWidgetType in ("QLineEdit", "QTextEdit",
                    "QComboBox", "QDateEdit", "QDateTimeEdit"):
                    mWidgetType = 'QLabel'

                mRowSpan = t.get('row span', textEditRowSpan) if mWidgetType == 'QTextEdit' else None

                mDict.update( { ( idx[mParent], mParent ) : InternalDict() } )
                mDict[ ( idx[mParent], mParent ) ].update( {
                    'object' : 'edit',
                    'main widget type' : mWidgetType,
                    'row' : rowidx[mParent],
                    'row span' : mRowSpan,
                    'input mask' : t.get('input mask', None) if mode == 'edit' else None,
                    'label' : mLabel,
                    'label row' : mLabelRow,
                    'help text' : t.get('help text', None),
                    'value' : mValue,
                    'placeholder text' : t.get('placeholder text', None) \
                        if mode == 'edit' and mWidgetType in ( 'QTextEdit', 'QLineEdit', 'QComboBox' ) \
                        else None,
                    'language value' : mLanguage,
                    'is mandatory' : t.get('is mandatory', None) if mode == 'edit' else None,
                    'multiple values' : multiple,
                    'has minus button' : mode == 'edit' and ( multiple or len(values) > 1 ),
                    'hide minus button': len(values) <= 1 if ( mode == 'edit' and ( multiple or len(values) > 1 ) ) else None,
                    'default value' : t.get('default value', None),
                    'node kind' : "sh:Literal",
                    'data type' : mType,
                    'subject' : mDataIdentifier or mParentNode,
                    'predicate' : mProperty,
                    'path' : meta,
                    'default widget type' : mDefaultWidgetType,
                    'type validator' : None if (mode == 'read') else (
                        'QIntValidator' if mType.n3(nsm) == "xsd:integer" else (
                        'QDoubleValidator' if mType.n3(nsm) in ("xsd:decimal", "xsd:float", "xsd:double") \
                        else None )),
                    'authorized languages' : sorted(mVLangList) if ( mode == 'edit' and mVLangList ) else None,
                    'read only' : ( mode == 'read' ) or t.get('read only', False),
                    'template order' : int(t.get('order')) if t.get('order') is not None else None
                    } )
                        
                idx[mParent] += 1
                rowidx[mParent] += ( mRowSpan or 1 )

            if multiple and mode == 'edit':

                mDict.update( { ( idx[mParent], mParent ) : InternalDict() } )
                mDict[ ( idx[mParent], mParent ) ].update( {
                    'object' : 'plus button',
                    'main widget type' : 'QToolButton',
                    'row' : rowidx[mParent],
                    'next child' : idx[mParent] + 1,
                    'path' : meta,
                    'help text' : 'Ajouter un élément « {} »'.format(t.get('label', ''))
                    } )
                
                idx[mParent] += 1
                rowidx[mParent] += 1


    # ---------- RENUMEROTATION ----------
    # le cas échéant, on réordonne les catégories en fonction
    # paramètre "order" du template (stocké dans la clé
    # 'template order'). Les métadonnées non définies
    # traitées plus loin iront naturellement à la fin.
    if template:
        
        lw = [k for k in mTemplateTabs.values()] if is_root(mParentWidget) \
            else [mParentWidget]
            
        for w in lw:
            n = 0
            l = [k for k in iter_children_keys(mDict, w)]
            l.sort(key= lambda k: (
                mDict[k]["template order"] if mDict[k]["template order"] is not None else 9999,
                mDict[k]["shape order"] if mDict[k]["shape order"] is not None else 9999
                ))
            
            for k in l:       
                if mDict[k]['row'] is not None:
            
                    # on ne traite pas les doubles M
                    # indépendemment, mais en même temps
                    # que leurs jumeaux non M
                    if len(k) == 3 and (k[0], k[1]) in mDict:
                        continue
                    elif len(k) == 2 and (k[0], k[1], 'M') in mDict:                    
                        mDict[(k[0], k[1], 'M')]['row'] = n
                        # la question du label ne se pose
                        # pas puisqu'on est sur un groupe
                    
                    if mDict[k]['label row'] is not None:
                        mDict[k]['label row'] = n
                        n += 1
                    
                    mDict[k]['row'] = n
                    n += ( mDict[k]['row span'] or 1 )


    # ---------- DESCRIPTIFS DES CHAMPS ----------
    
    if columns and mTargetClass == URIRef("http://www.w3.org/ns/dcat#Dataset"):

        # dans l'onglet "Champs"
        mParent = mTemplateTabs["Champs"]
        if not mParent in idx:
            idx.update({ mParent: 0 })
        if not mParent in rowidx:
            rowidx.update({ mParent: 0 })
        
        # pour chaque champ, on référence un widget de saisie
        # QTextEdit, dont le nom du champ sera le label.
        for colname, coldescr in columns:
        
            mWidgetType = 'QTextEdit' if mode == 'edit' else 'QLabel'

            mWidget = ( idx[mParent], mParent )
            mDict.update( { mWidget : InternalDict() } )
            mDict[ ( idx[mParent], mParent ) ].update( {
                'object' : 'edit',
                'main widget type' : mWidgetType,
                'row' : rowidx[mParent] + 1,
                'row span' : textEditRowSpan if mWidgetType == "QTextEdit" else None,
                'label' : colname,
                'help text' : 'Description du champ.',
                'label row' : rowidx[mParent],
                'value' : coldescr,
                'do not save' : True,
                'path' : 'snum:column'
                } )
            idx[mParent] += 1
            rowidx[mParent] += ( 1 + textEditRowSpan ) 
            
            

    # ---------- METADONNEES NON DEFINIES ----------
    # métadonnées présentes dans le graphe mais ni dans shape ni dans template
    
    if mTargetClass == URIRef("http://www.w3.org/ns/dcat#Dataset"):
    
        mNGhost = (mode == 'edit' and editHideUnlisted) or \
            (mode == 'read' and readHideUnlisted)

        dpv = dict()
        
        for p, v in metagraph.predicate_objects(mParentNode):
        
            if isinstance(v, BNode):
                # on élimine d'entrée de jeu tout ce qui
                # n'est pas une branche terminale
                continue
                
            if p == URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"):
                continue
                
            if not p.n3(nsm) in [ d.get('path', None) for d in mDict.values() ]:        
                dpv.update( { p : ( dpv.get(p, []) ) + [ v ] } )

        for p in dpv:

            mParent = mParentWidget
            
            if not mNGhost:
                # dès lors qu'on les affiche, les catégories non
                # référencées vont toujours dans l'onglet "Autres". 
                # s'il n'existait pas encore, on le crée :
                if not "Autres" in mTemplateTabs:
                    i = max([ k[0] for k in mTemplateTabs.values() ]) + 1
                    mParent = (i,)
                    mTemplateTabs.update({ "Autres": mParent })
                    mDict.update( { mParent : InternalDict() } )
                    mDict[mParent].update( {
                        'object' : 'group of properties',
                        'main widget type' : 'QGroupBox',
                        'label' : "Autres",
                        'row' : 0,
                        'node' : mParentNode,
                        'class' : URIRef('http://www.w3.org/ns/dcat#Dataset'),
                        'shape order' : i,
                        'do not save' : True
                        } )
                else:
                    mParent = mTemplateTabs["Autres"]
                    
                if not mParent in idx:
                    idx.update({ mParent: 0 })
                if not mParent in rowidx:
                    rowidx.update({ mParent: 0 })
            
            # cas d'un groupe de valeurs
            if len(dpv[p]) > 1:
            
                if mNGhost:
                    # si les catégories non répertoriées ne
                    # doivent pas être affichées
                    mWidget = ( idx[mParent], mParent )
                    mDict.update( { mWidget : InternalDict() } )
                    mDict[mWidget].update( {
                        'object' : 'group of values'
                        } )

                    idx[mParent] += 1
                    idx.update( { mWidget : 0 } )
                    mParent = mWidget
                
                else:
                    mWidget = ( idx[mParent], mParent )
                    mDict.update( { mWidget : InternalDict() } )
                    mDict[mWidget].update( {
                        'object' : 'group of values',
                        'main widget type' : 'QGroupBox',
                        'row' : rowidx[mParent],
                        'label' : "???",
                        'help text' : p.n3(nsm),
                        'path' : p.n3(nsm)
                        } )

                    idx[mParent] += 1
                    rowidx[mParent] += 1
                    idx.update( { mWidget : 0 } )
                    rowidx.update( { mWidget : 0 } )
                    mParent = mWidget


            for v in dpv[p]:

                mValue = str(v)
                
                mType = None
                if isinstance(v, Literal):
                    mType = URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#langString') \
                        if v.language else v.datatype
                mType = mType or URIRef("http://www.w3.org/2001/XMLSchema#string")
                # NB : pourrait ne pas être homogène pour toutes les valeurs d'une même catégorie
                
                mLanguage = v.language if mType.n3(nsm) == 'rdf:langString' else None
                            
                if mNGhost:
                    # si les catégories non répertoriées ne
                    # doivent pas être affichées
                    mDict.update( { ( idx[mParent], mParent ) : InternalDict() } )
                    mDict[ ( idx[mParent], mParent ) ].update( {
                        'object' : 'edit',                      
                        'value' : mValue,                        
                        'language value' : mLanguage,                        
                        'node kind' : "sh:Literal",
                        'data type' : mType,
                        'path' : p.n3(nsm),
                        'subject' : mDataIdentifier or mParentNode,
                        'predicate' : p                      
                        } )
                
                    idx[mParent] += 1
                    
                else:

                    mWidgetType = 'QTextEdit' if ( len(mValue) > valueLengthLimit \
                        or mValue.count("\n") > 0 ) else "QLineEdit"
                        
                    mLabelRow = None
                    if len(dpv[p]) == 1 and mWidgetType == 'QTextEdit':
                        mLabelRow = rowidx[mParent]
                        rowidx[mParent] += 1
                        
                    if mode == 'read':
                        mWidgetType = 'QLabel'
                                
                    mVLangList = ( [ mLanguage ] + ( langList.copy() or [] ) \
                        if not mLanguage in ( langList or [] ) else langList.copy() \
                        ) if mLanguage and translation else None

                    mDict.update( { ( idx[mParent], mParent ) : InternalDict() } )
                    mDict[ ( idx[mParent], mParent ) ].update( {
                        'object' : 'edit',
                        'main widget type' : mWidgetType,
                        'row' : rowidx[mParent],
                        'row span' : textEditRowSpan if mWidgetType == "QTextEdit" else None,
                        'label' : "???" if len(dpv[p]) == 1 else None,
                        'label row' : mLabelRow,
                        'help text' : p.n3(nsm),
                        'value' : mValue,
                        'language value' : mLanguage,
                        'node kind' : "sh:Literal",
                        'data type' : mType,
                        'multiple values' : False,
                        'has minus button' : ( len(dpv[p]) > 1 and mode == 'edit' ) or False,
                        'hide minus button': False if ( len(dpv[p]) > 1 and mode == 'edit' ) else None,
                        'subject' : mDataIdentifier or mParentNode,
                        'predicate' : p,
                        'path' : p.n3(nsm),
                        'default widget type' : "QLineEdit",
                        'type validator' : None if mode == 'read' else (
                            'QIntValidator' if mType.n3(nsm) == "xsd:integer" else (
                            'QDoubleValidator' if mType.n3(nsm) in ("xsd:decimal", "xsd:float", "xsd:double") \
                            else None )),
                        'authorized languages' : sorted(mVLangList) if ( mode == 'edit' and mVLangList ) else None,
                        'read only' : ( mode == 'read' )
                        } )
                            
                    idx[mParent] += 1
                    rowidx[mParent] += 1

                    # pas de bouton plus, faute de modèle indiquant si la catégorie
                    # admet des valeurs multiples


    # ------ GROUPES VIDES ------

    if not is_root(mParentWidget) and rowidx.get(mParentWidget) == 0 \
        and mDict[mParentWidget]['main widget type']:
        # cas d'un groupe de propriétés dans lequel on n'aura finalement
        # aucune propriété à afficher.
        
        if idx[mParentWidget] == 0 :
            # enregistrement sans descendant, on le supprime.
            # NB : correspond 1) au cas d'un double M dont
            # toutes les propriétés sont hors template, en mode édition,
            # et lorsque soit la valeur renseignée est une IRI, soit
            # la propriété dont le noeud vide est l'objet est, elle, dans
            # le template ; 2) au cas où une branche du template se finit
            # sur un noeud vide, en mode édition et quand aucune valeur
            # n'était renseignée sur cette branche
            del mDict[mParentWidget]
            if len(mParentWidget) == 2:
                rowidx[mParentWidget[1]] -= 1
            elif mVSources and '< manuel >' in mVSources:
                del mVSources['< manuel >']
            
        else:
            # si l'enregistrement a des descendants (cas de stockage
            # d'informations masquées en mode lecture), on se contente
            # de ne pas afficher le groupe
            mDict[mParentWidget]['main widget type'] = None
            mDict[mParentWidget]['row'] = None
            # on corrige l'index du parent (pas pour les doubles M,
            # puisque le numéro de ligne est partagé avec le jumeau,
            # mais tous devraient avoir été traités au point précédent)
            if len(mParentWidget) == 2:
                rowidx[mParentWidget[1]] -= 1
            elif mVSources and '< manuel >' in mVSources:
                del mVSources['< manuel >']
        
    elif mTargetClass == URIRef("http://www.w3.org/ns/dcat#Dataset"):
        # contrôle des onglets non utilisés
        for t in mTemplateTabs.values():
            if (not t in rowidx) or rowidx[t] == 0:
                mDict[t]['main widget type'] = None

    return mDict


def update_pg_description(description, metagraph, geoideJSON=False):
    """Return new description with metadata section updated from JSON-LD serialization of metadata graph.

    ARGUMENTS
    ---------
    - metagraph (rdflib.graph.Graph) : un graphe de métadonnées mis à
    jour suite aux actions effectuées par l'utilisateur.
    - description (str) : chaîne de caractères supposée correspondre à la
    description (ou le commentaire) d'un objet PostgreSQL.
    - geoideJSON (bool) : True si, en plus de la sérialisation JSON-LD
    standard, doit un constitué un fragment JSON contenant les
    métadonnées gérées par le processus de réplication GéoIDE. False par
    défaut.

    RESULTAT
    --------
    Une chaîne de caractère (str) correspondant à la description mise à jour
    d'après le contenu du graphe.

    Les informations comprises entre les deux balises <METADATA> et </METADATA>
    sont remplacées par un JSON-LD contenant les métadonnées de l'objet
    PostgreSQL. Si les balises n'existaient pas, elles sont ajoutées à la
    fin du texte.
    
    Si geoideJSON vaut True, les informations comprises entre les deux balises
    <GEOIDE> et </GEOIDE> sont remplacées par un JSON contenant une petite
    partie des métadonnées communes - celles qui sont prises en charge par
    le processus de réplication de GéoIDE.

    EXEMPLES
    --------
    >>> c = update_pg_description(c, metagraph)
    """

    if len(metagraph) == 0:
        return description
    
    s = metagraph.serialize(format="json-ld")
    
    if description:
        t = re.subn(
            "[<]METADATA[>].*[<][/]METADATA[>]",
            "<METADATA>\n" + s.replace('\\', r'\\') + "\n</METADATA>",
            description,
            flags=re.DOTALL
            )
        # cette expression remplace tout de la première balise <METADATA> à
        # la dernière balise </METADATA> (elle maximise la cible, au contraire
        # de la fonction metagraph_from_pg_description)

        if t[1] == 0:
            new_description = description + "\n\n<METADATA>\n" + s + "\n</METADATA>\n"
        else:
            new_description = t[0]
    else:
        new_description = "\n\n<METADATA>\n" + s + "\n</METADATA>\n"
    
    if geoideJSON:
        j = build_geoide_json(metagraph)
        if j:
            t = re.subn(
            "[<]GEOIDE[>].*[<][/]GEOIDE[>]",
            "<GEOIDE>\n" + j + "\n</GEOIDE>",
            new_description,
            flags=re.DOTALL
            )
            if t[1] == 0:
                new_description = new_description + "\n<GEOIDE>\n" + j + "\n</GEOIDE>\n"
            else:
                new_description = t[0]
    
    return new_description


def forbidden_char(anyStr):
    """Return any character from given string that is not allowed in IRIs.
    
    ARGUMENTS
    ---------
    - anyStr (str) : chaîne de caractères à tester.
    
    RESULTAT
    --------
    Si la chaîne contient au moins un caractère interdit, l'un
    de ces caractères.
    
    EXEMPLES
    --------
    >>> forbidden_char('avec des espaces')
    ' '
    """
    
    r = re.search(r'([<>"\s{}|\\^`])', anyStr)
    
    return r[1] if r else None


def is_valid_minipath(path, nsm):
    """Run basic validity test on SPARQL mono-element path.

    ARGUMENTS
    ---------
    - path (str) : un chemin SPARQL.
    - nsm (rdflib.namespace.NamespaceManager) : un
    gestionnaire d'espaces de nommage.

    RESULTAT
    --------
    La fonction renvoie False si path est visiblement composé
    de plus d'un élément.

    Elle renvoie True si path est un URI valide (pas de
    caractères interdits), soit non abrégé et écrit entre < >,
    soit abrégé avec un préfixe référencé dans le gestionnaire
    d'espaces de nommage fourni en argument.

    EXEMPLES
    --------
    >>> is_valid_minipath('<https://www.w3.org/TR/sparql11-query/>',
    ...     Graph().namespace_manager)
    True
    """

    if re.match(r'^[<][^<>"\s{}|\\^`]+[:][^<>"\s{}|\\^`]+[>]$', path):
        return True

    r = re.match('^([a-z]+)[:][a-zA-Z0-9-]+$', path)
    if r and r[1] in [ k for k,v in nsm.namespaces() ]:
        return True

    return False
    

def metagraph_from_pg_description(description, shape):
    """Get JSON-LD metadata from description and parse them into a graph.

    ARGUMENTS
    ---------
    - description (str) :chaîne de caractères supposée correspondre à la
    description (ou le commentaire) d'un objet PostgreSQL.
    - shape (rdflib.graph.Graph) : schéma SHACL augmenté décrivant les catégories
    de métadonnées communes. Il fournit ici les préfixes d'espaces de nommage
    à déclarer dans le graphe.

    RESULTAT
    --------
    Un graphe RDF de métadonnées (rdflib.graph.Graph) déduit par désérialisation du JSON-LD.

    Le JSON-LD est présumé se trouver entre deux balises <METADATA> et </METADATA>.

    Si la valeur contenue entre les balises n'est pas un JSON valide, la
    fonction échoue sur une erreur de type json.decoder.JSONDecodeError.

    S'il n'y a pas de balises ou s'il n'y a rien entre les balises, la fonction renvoie
    un graphe vierge, avec seulement un identifiant de dcat:Dataset.

    EXEMPLES
    --------
    >>> with open('shape.ttl', encoding='UTF-8') as src:
    ...    shape = Graph().parse(data=src.read(), format='turtle')
    >>> with open('exemples\\exemple_commentaire_pg.txt', encoding='UTF-8') as src:
    ...    c_source = src.read()
    >>> g_source = metagraph_from_pg_description(c_source, shape)
    """

    j = re.search("^(?:.*)[<]METADATA[>](.*?)[<][/]METADATA[>]", description, re.DOTALL)
    # s'il y a plusieurs balises <METADATA> et/ou </METADATA>, cette expression retient
    # les caractères compris entre la dernière balise <METADATA> et la première balise </METADATA>.
    # s'il devait y avoir plusieurs couples de balises, elle retiendrait le contenu du
    # dernier.

    if j is None or not j[1]:
        g = Graph()
    else:
        g = Graph().parse(data=j[1], format='json-ld')
  
    for n, u in shape.namespace_manager.namespaces():
        g.namespace_manager.bind(n, u, override=True, replace=True)

    return g


def build_vocabulary(schemeIRI, vocabulary, language="fr", value=None):
    """List all concept labels from given scheme.

    ARGUMENTS
    ---------
    - schemeIRI (URIRef) : IRI de l'ensemble dont on veut lister les concepts.
    - vocabulary (rdflib.graph.Graph) : graphe réunissant le vocabulaire de tous
    les ensembles à considérer.
    - [optionnel] language (str) : langue attendue pour les libellés des concepts.
    Français par défaut.
    - [optionnel] value (str) : un terme supposé être dans la liste. Cet argument
    ne sert que dans le cas d'un schemeIRI (qui n'est alors pas un IRI) valant
    '< non répertorié >', car la fonction renvoie alors une liste contenant 
    seulement une chaîne de caractères vides et la valeur en question.

    RESULTAT
    --------
    Liste (list) contenant les libellés (str) des termes du thésaurus, triés par
    ordre alphabétique selon la locale de l'utilisateur.
    
    La fonction rajoute systématiquement une chaîne de caractères vide en première
    position de la liste.

    EXEMPLES
    --------
    >>> rdf_utils.build_vocabulary(
    ...    URIRef("http://publications.europa.eu/resource/authority/data-theme"),
    ...    vocabulary
    ...    )
    ['', 'Agriculture, pêche, sylviculture et alimentation', 'Données provisoires',
    'Économie et finances', 'Éducation, culture et sport', 'Énergie', 'Environnement',
    'Gouvernement et secteur public', 'Justice, système juridique et sécurité publique',
    'Population et société', 'Questions internationales', 'Régions et villes', 'Santé',
    'Science et technologie', 'Transports']
    """
    if schemeIRI == '< non répertorié >':
        return ['', value] if value else ['']
    
    if not isinstance(schemeIRI, URIRef):
        raise ForbiddenOperation(
            "Can't generate a concept list from non-URIRef source '{}'.".format(schemeIRI)
            )
    
    concepts = [ c for c in vocabulary.subjects(
        URIRef("http://www.w3.org/2004/02/skos/core#inScheme"),
        schemeIRI ) ] 

    labels = []
    if concepts:
        
        for c in concepts:
            clabels = [ o for o in vocabulary.objects(
                c, URIRef("http://www.w3.org/2004/02/skos/core#prefLabel")
                ) ]
            if clabels:
                t = pick_translation(clabels, language)
                labels.append(str(t))

        if labels:
            setlocale(LC_COLLATE, "")

            labels = sorted(
                labels,
                key=lambda x: strxfrm(x)
                )
                
    labels.insert(0, '')
    return labels


def concept_from_value(conceptStr, schemeIRI, vocabulary, language='fr', strict=True):
    """Return a skos:Concept IRI matching given label.

    ARGUMENTS
    ---------
    - conceptStr (str) : chaîne de caractères présumée correspondre au libellé d'un
    concept.
    - schemeIRI (URIRef) : IRI de l'ensemble qui référence ce concept.
    Si schemeIRI n'est pas spécifié, la fonction effectuera la recherche dans tous les
    ensembles disponibles. En cas de correspondance multiple, elle renvoie arbitrairement
    un des résultats.
    - vocabulary (rdflib.graph.Graph) : graphe réunissant le vocabulaire de tous les
    ensembles à considérer.
    - [optionnel] language (str) : langue présumée de strValue. Français par défaut.
    - [optionnel] strict (bool) : si True, la fonction renverra None plutôt que
    d'aller chercher une correspondance dans une autre langue que language. True par
    défaut.

    RESULTAT
    --------
    Si schemeIRI n'est pas fourni en argument, un tuple formé comme suit :
    [0] est l'IRI du terme (rdflib.term.URIRef).
    [1] est l'IRI de l'ensemble (rdflib.term.URIRef).
    Sinon, la fonction renvoie seulement l'IRI du concept.
    
    Si strict vaut False et que schemeIRI est fourni, alors si la fonction échoue à
    trouver un label correspond dans la langue langage, elle examinera les labels du
    concept en français, puis dans toutes les langues jusqu'à en trouver un qui
    corresponde.

    EXEMPLES
    --------
    >>> rdf_utils.concept_from_value("Domaine public", URIRef('http://purl.org/adms/licencetype/1.1'), vocabulary)
    rdflib.term.URIRef('http://purl.org/adms/licencetype/PublicDomain')
        
    >>> rdf_utils.concept_from_value("Transports", None, vocabulary)
    (rdflib.term.URIRef('http://publications.europa.eu/resource/authority/data-theme/TRAN'), rdflib.term.URIRef('http://publications.europa.eu/resource/authority/data-theme'))
    """
    conceptIRI = None
    
    if schemeIRI in ('< non répertorié >', '< manuel >', '< URI >'):
        return None

    # IRI des concepts dont le label est conceptStr :
    concepts = [ s for s in vocabulary.subjects(
        URIRef("http://www.w3.org/2004/02/skos/core#prefLabel"),
        Literal(conceptStr, lang=language)
        ) ]
        
    if not concepts:   
        if not schemeIRI:
            return None, None
        if strict:
            return None
        
        # en français
        if not language == 'fr':
            concepts = [ s for s in vocabulary.subjects(
                URIRef("http://www.w3.org/2004/02/skos/core#prefLabel"),
                Literal(conceptStr, lang='fr')
                ) ]
        
        if not concepts:
            # dans les autres langues, on récupère tous les concepts
            # du thésaurus et on boucle sur leurs labels
            candidats = [ s for s in vocabulary.subjects(
                URIRef("http://www.w3.org/2004/02/skos/core#inScheme"),
                schemeIRI
                ) ]
            for c in candidats:
                candidat_labels = [ o for o in vocabulary.objects(
                    c, URIRef("http://www.w3.org/2004/02/skos/core#prefLabel")
                    ) ]
                for l in candidat_labels:
                    if str(l) == conceptStr:
                        conceptIRI = c
                        return conceptIRI
    
            return None

    if not schemeIRI:
        # choix arbitraire d'un concept dans la liste :
        conceptIRI = concepts[0]
        
        # IRI de l'ensemble dont fait partie le concept :
        schemeIRI = vocabulary.value(
            conceptIRI,
            URIRef("http://www.w3.org/2004/02/skos/core#inScheme")
            )
        
        if schemeIRI:
            # NB : cette condition est en principe inutile. Si
            # vocabulary a été correctement contrôlé, inScheme
            # sera présent sur tous les concepts
            return conceptIRI, schemeIRI
        else:
            return None, None

    for conceptIRI in concepts:
        # IRI de l'ensemble dont fait partie le concept :
        schemeIRIBis = vocabulary.value(
            conceptIRI,
            URIRef("http://www.w3.org/2004/02/skos/core#inScheme")
            )
        # ... et on le garde s'il coïncide avec schemeStr :
        if schemeIRI == schemeIRIBis:
            return conceptIRI
        
    return None


def value_from_concept(conceptIRI, vocabulary, language="fr", getpage=False,
    getschemeStr=True, getschemeIRI=False, getconceptStr=True, strict=False):
    """Return the skos:prefLabel strings matching given conceptIRI and its scheme.

    ARGUMENTS
    ---------
    - conceptIRI (rdflib.term.URIRef) : objet URIRef présumé correspondre à un
    concept d'ontologie.
    - vocabulary (rdflib.graph.Graph) : graphe réunissant le vocabulaire de tous
    les ensembles à considérer.
    - [optionnel] language (str) : langue attendue pour le libellé résultant.
    Français par défaut.
    - [optionnel] getpage (bool) : True si la fonction doit également
    récupérer l'eventuelle page web (foaf:page) associée au concept. False par défaut.
    - [optionnel] getschemeStr (bool) : True si la fonction doit récupérer le label de
    l'ensemble dont fait partie le concept. True par défaut.
    - [optionnel] getschemeIRI (bool) : True si la fonction doit récupérer l'objet
    URIRef identifiant l'ensemble dont fait partie de le concept. False par défaut.
    - [optionnel] getconceptStr (bool) : True si la fonction doit renvoyer le
    label du concept. True par défaut.
    - [optionnel] strict (bool) : si True, la fonction ne renverra pas de valeurs
    qui ne seraient pas dans la langue demandée. False par défaut.

    RESULTAT
    --------
    Un tuple contenant zéro à quatre chaînes de caractères :
    [0] est le libellé du concept (str), si getconceptStr vaut True.
    [1] est le nom de l'ensemble (str), si getschemeStr vaut True.
    [2] l'IRI (rdflib.term.URIRef) de la page web associée, si existe et si
    getpage vaut True, sinon None.
    [3] l'IRI de l'ensemble (rdflib.term.URIRef), si getschemeIRI vaut True.
    Les éléments seront toujours dans cet ordre, mais ne seront pas présents
    si le paramétrage ne les prévoyait pas.
    
    Un tuple de None si l'IRI n'est pas répertorié.
    
    Si aucune valeur n'est disponible pour la langue spécifiée et que strict
    ne vaut pas True, la fonction retournera la traduction française
    (si elle existe), ou à défaut la première traduction venue.
    Si strict vaut True, la fonction renvoie un tuple de None s'il
    n'existe pas de label pour le concept dans la langue demandée.
    
    EXEMPLES
    --------
    Dans l'exemple ci-après, il existe une traduction française et anglaise pour le terme
    recherché, mais pas de version espagnole.

    >>> u = URIRef("http://publications.europa.eu/resource/authority/data-theme/TRAN")
    
    >>> rdf_utils.value_from_concept(u, vocabulary)
    ('Transports', 'Thèmes de données (UE)')
    
    >>> rdf_utils.value_from_concept(u, vocabulary, 'en')
    ('Transport', 'Data theme (EU)')
    
    >>> rdf_utils.value_from_concept(u, vocabulary, 'es')
    ('Transports', 'Thèmes de données (UE)')
    """
    d = {}
    if getconceptStr:
        d.update({ 'conceptStr': None })
    if getschemeStr:
        d.update({ 'schemeStr': None })
    if getpage:
        d.update({ 'page': None })
    if getschemeIRI:
        d.update({ 'schemeIRI': None })
    
    if getconceptStr:
        # labels du concept dans toutes les langues :
        labels = [ o for o in vocabulary.objects(
            conceptIRI, URIRef("http://www.w3.org/2004/02/skos/core#prefLabel")
            ) ]

        if not labels:
            # concept non référencé
            return tuple([None for v in d.values()])
        
        t = pick_translation(labels, language)
        
        if strict and not t.language == language:
            return tuple([v for v in d.values()])
        
        d['conceptStr'] = str(t)
    
    if getschemeStr or getschemeIRI:
        schemeIRI = vocabulary.value(
            conceptIRI, URIRef("http://www.w3.org/2004/02/skos/core#inScheme")
            )
        
        if schemeIRI is None:
            # NB : cette condition est en principe inutile. Si
            # vocabulary a été correctement contrôlé, inScheme
            # sera présent sur tous les concepts
            return tuple([None for v in d.values()])
        
        if getschemeIRI:
            d['schemeIRI'] = schemeIRI
        
        if getschemeStr:
            # labels de l'ensemble dans toutes les langues :
            slabels = [ o for o in vocabulary.objects(
                schemeIRI, URIRef("http://www.w3.org/2004/02/skos/core#prefLabel")
                ) ]
                
            if not slabels:
                # NB : ne devrait jamais arriver. Tout ensemble
                # référencé a au moins un label
                return tuple([None for v in d.values()])
            
            d['schemeStr'] = str(pick_translation(slabels, language))
    
    if getpage:
        d['page'] = vocabulary.value(
            conceptIRI, URIRef("http://xmlns.com/foaf/0.1/page")
            )

    return tuple([v for v in d.values()])
    

def email_from_owlthing(thingIRI):
    """Return a string human-readable version of an owl:Thing IRI representing an email adress.

    ARGUMENTS
    ---------
    - thingIRI (rdflib.term.URIRef) : objet de type URIref supposé
    correspondre à une adresse mél (classe RDF owl:Thing).

    RESULTAT
    --------
    Une chaîne de caractères (str), correspondant à une forme
    plus lisible par un être humain de l'adresse mél.

    Cette fonction très basique se contente de retirer le préfixe
    "mailto:" s'il était présent.

    EXEMPLES
    --------
    >>> email_from_owlthing(URIRef("mailto:jon.snow@the-wall.we"))
    'jon.snow@the-wall.we'
    """

    # à partir de la version 3.9
    # str(thingIRI).removeprefix("mailto:") serait plus élégant
    
    return re.sub("^mailto[:]", "", str(thingIRI))


def owlthing_from_email(emailStr):
    """Return an IRI from a string representing an email adress.

    ARGUMENTS
    ---------
    - emailStr (str) : est une chaîne de caractère supposée
    correspondre à une adresse mél.

    RESULTAT
    --------
    Un objet de type URIRef (rdflib.term.URIRef) respectant grosso
    modo le schéma officiel des URI pour les adresses mél :
    mailto:<email>.
    (réf : https://datatracker.ietf.org/doc/html/rfc6068)

    La fonction ne fait aucun contrôle de validité sur l'adresse si ce
    n'est vérifier qu'elle ne contient aucun caractère interdit pour
    un IRI.

    EXEMPLES
    --------
    >>> owlthing_from_email("jon.snow@the-wall.we")
    rdflib.term.URIRef('mailto:jon.snow@the-wall.we')
    """

    emailStr = re.sub("^mailto[:]", "", emailStr)

    l = [i for i in '<> "{}|\\^`' if i in emailStr]

    if l and not l == []:          
        raise ValueError("Invalid IRI. Forbiden character '{}' in email adress '{}'.".format("".join(l), emailStr))

    if emailStr and not emailStr == "":
        return URIRef("mailto:" + emailStr)


def tel_from_owlthing(thingIRI):
    """Return a string human-readable version of an owl:Thing IRI representing a phone number.

    ARGUMENTS
    ---------
    - thingIRI (rdflib.term.URIRef) : objet de type URIref supposé
    correspondre à un numéro de téléphone (classe RDF owl:Thing).

    RESULTAT
    --------
    Une chaîne de caractères (str), correspondant à une forme
    plus lisible par un être humain du numéro de téléphone.

    Contrairement à owlthing_from_tel, cette fonction très basique
    ne standardise pas la forme du numéro de téléphone. Elle se contente
    de retirer le préfixe "tel:" s'il était présent.

    EXEMPLES
    --------
    >>> tel_from_owlthing(URIRef("tel:+33-1-23-45-67-89"))
    '+33-1-23-45-67-89'
    """
    
    return re.sub("^tel[:]", "", str(thingIRI))


def owlthing_from_tel(telStr, addPrefixFr=True):
    """Return an IRI from a string representing a phone number.

    ARGUMENTS
    ---------
    - telStr (str) : chaîne de caractère supposée correspondre à un
    numéro de téléphone.
    - addPrefixFr (bool) : True si la fonction doit tenter
    de transformer les numéros de téléphone français locaux ou présumés
    comme tels (un zéro suivi de neuf chiffres) en numéros globaux ("+33"
    suivi des neuf chiffres). True par défaut.

    RESULTAT
    --------
    Un objet de type URIRef respectant grosso modo le schéma
    officiel des URI pour les numéros de téléphone : tel:<phonenumber>.
    (réf : https://datatracker.ietf.org/doc/html/rfc3966)

    Si le numéro semble être un numéro de téléphone français valide,
    il est standardisé sous la forme <tel:+33-x-xx-xx-xx-xx>.

    EXEMPLES
    --------
    >>> owlthing_from_tel("0123456789")
    rdflib.term.URIRef('tel:+33-1-23-45-67-89')
    """

    telStr = re.sub("^tel[:]", "", telStr)
    red = re.sub(r"[.\s-]", "", telStr)
    tel = ""

    if addPrefixFr:
        a = re.match(r"0(\d{9})$", red)
        # numéro français local
        
        if a:
            red = "+33" + a[1]

    if re.match(r"[+]33\d{9}$", red):
    # numéro français global
    
        for i in range(len(red)):
            if i == 3 or i > 2 and i%2 == 0:
                tel = tel + "-" + red[i]
            else:
                tel = tel + red[i]

    else:
        tel = re.sub(r"(\d)\s(\d)", r"\1-\2", telStr).strip(" ")
        # les espaces entre les chiffres sont remplacés par des tirets,
        # ceux en début et fin de chaine sont supprimés

        l = [i for i in '<> "{}|\\^`' if i in tel]

        if l and not l == []:          
            raise ValueError("Invalid IRI. Forbiden character '{}' in phone number '{}'.".format("".join(l), telStr))

    if tel and not tel == "":
        return URIRef("tel:" + tel)


def is_root(key):
    """La clé key est-elle une clé racine ?
    
    ARGUMENTS
    ---------
    - key (tuple) : clé d'un dictionnaire de widgets (WidgetsDict).
    
    RESULTAT
    --------
    True si la clé est une clé racine, c'est-à-dire une clé sans ancêtre,
    correspondant à un onglet du formulaire.
    
    EXEMPLES
    --------
    >>> rdf_utils.is_root((1,))
    True
    
    >>> rdf_utils.is_root((0,(0,)))
    False
    """
    return len(key) == 1


def is_older(key1, key2):
    """La clé key1 est-elle plus proche de la racine que key2 ?
    
    ARGUMENTS
    ---------
    - key1 (tuple) : clé d'un dictionnaire de widgets (WidgetsDict).
    - key2 (tuple) : clé d'un dictionnaire de widgets (WidgetsDict).
    
    RESULTAT
    --------
    True si key1 est plus proche de la racine que key2.
    False si les deux clés appartiennent à la même génération,
    ou que key2 est plus proche de la racine.
    
    EXEMPLES
    --------
    >>> rdf_utils.is_older((0, (0,)), (1, (0,)))
    False
    
    >>> rdf_utils.is_older((0, (0,)), (0, (1, (0,))))
    True
    
    >>> rdf_utils.is_older((0, (1, (0,))), (0, (0,)))
    False
    """    
    return str(key1).count("(") < str(key2).count("(")


def is_ancestor(key1, key2):
    """La clé key1 est-elle un ancêtre de la clé key2 ?
    
    ARGUMENTS
    ---------
    - key1 (tuple) : clé d'un dictionnaire de widgets (WidgetsDict).
    - key2 (tuple) : clé d'un dictionnaire de widgets (WidgetsDict).
    
    RESULTAT
    --------
    True si key1 est un ancêtre direct ou indirect de key2.
    
    Une clé n'est pas sa propre ancêtre, ni celui de son
    éventuel double M.
    
    EXEMPLES
    --------
    >>> rdf_utils.is_ancestor((2, (0,)), (8, (1, (2, (0,)))))
    True
    
    >>> rdf_utils.is_ancestor((2, (0,)), (8, (1, (3, (0,)))))
    False
    
    >>> rdf_utils.is_ancestor((8, (1, (2, (0,)))), (2, (0,)))
    False
    """
    
    if len(key2) <= 1 or is_older(key2, key1):
        return False
    
    if key2[1] == key1:
        return True
    else:
        return is_ancestor(key1, key2[1])


def replace_ancestor(key, old_ancestor, new_ancestor, mKey=None):
    """Réécrit la clé key, en remplaçant un de ses ancêtres.
    
    ARGUMENTS
    ---------
    - key (tuple) : clé d'un dictionnaire de widgets (WidgetsDict).
    - old_ancestor (tuple) : clé d'un dictionnaire de widgets
    (WidgetsDict), présumée être une clé ancêtre de key.
    - new_ancestor (tuple) : clé d'un dictionnaire de widgets
    (WidgetsDict) à substituer à old_ancestor.
    
    mKey sert uniquement aux appels récursifs de la fonction.
    
    old_ancestor et new_ancestor doivent appartenir à la
    même génération.
    
    RESULTAT
    --------
    La clé (tuple) résultant de la substitution.
    
    EXEMPLES
    --------
    >>> rdf_utils.replace_ancestor((1, (2, (3, (0, )))), (3, (0, )), (4, (0, )))
    (1, (2, (4, (0,))))
    >>> rdf_utils.replace_ancestor((2, (3, (0, )), 'M'), (3, (0, )), (4, (0, )))
    (2, (4, (0,)), 'M')
    """
    if mKey is None:
        if is_older(old_ancestor, new_ancestor) or is_older(new_ancestor, old_ancestor):
            raise ValueError("Keys {} and {} don't belong to the same generation.".format(
                    old_ancestor, new_ancestor))
        if len(old_ancestor) == 3 and len(new_ancestor) == 2:
            raise ForbiddenOperation("You shouldn't replace M widget" \
                "{} by non-M widget {}.".format(old_ancestor, new_ancestor))
        if len(old_ancestor) == 2 and len(new_ancestor) == 3:
            raise ForbiddenOperation("You shouldn't replace non-M widget" \
                "{} by M widget {}.".format(old_ancestor, new_ancestor))
        mKey = key
        # mémorisation de la clé initiale, juste pour les messages d'erreur
        # on travaille sur mKey
        
    if is_root(mKey) or is_older(mKey, old_ancestor):
        raise ValueError("Key {} is not {}'s ancestor.".format(old_ancestor, key))
        
    if mKey[1] == old_ancestor:
        return (mKey[0], new_ancestor, mKey[2]) if len(mKey) == 3 else (mKey[0], new_ancestor)
    
    if len(mKey) == 3:
        return (mKey[0], replace_ancestor(key, old_ancestor, new_ancestor, mKey[1]), mKey[2])
    else:
        return (mKey[0], replace_ancestor(key, old_ancestor, new_ancestor, mKey[1]))
    

def export_metagraph(metagraph, shape, filepath, format=None):
    """Serialize metagraph into a file.
    
    ARGUMENTS
    ---------
    - metagraph (rdflib.graph.Graph) : un graphe de métadonnées.
    - shape (rdflib.graph.Graph) : schéma SHACL augmenté décrivant
    les catégories de métadonnées communes. Il fournit ici les préfixes
    d'espaces de nommage à déclarer dans le graphe.
    - filepath (str) : chemin complet du fichier cible.
    - format (str) : format d'export, parmi les valeurs autorisées
    pour le paramètre format de la fonction serialize de rdflib
    ("turtle", "json-ld", "xml", "n3", "nt", "pretty-xml", "trig").
    "trix" et "nquads" sont exclus d'office, car non adaptés pour
    un stockage sous forme de fichier.
    
    À noter que les formats "xml" et "pretty-xml" ne sont pas
    compatibles avec les métadonnées locales. Plus généralement,
    on pourra utiliser la fonction available_formats()
    pour connaître à l'avance tous les formats autorisés pour
    un graphe donné.
    
    Si aucun format n'est fourni et qu'il ne peut pas être
    déduit de l'extension du fichier cible, l'export sera fait en
    turtle.
    
    RESULTAT
    --------
    Pas de valeur renvoyée.
    
    Le fichier sera toujours encodé en UTF-8 sauf pour le format
    NTriples (encodage ASCII).
    """
    pfile = Path(filepath)

    if format and not format in export_formats():
        raise ValueError("Format '{}' is not supported.".format(format))

    for n, u in shape.namespace_manager.namespaces():
            metagraph.namespace_manager.bind(n, u, override=True, replace=True)
    
    # en l'absence de format, si le chemin comporte un
    # suffixe, on tente d'en déduire le format
    if not format and pfile.suffix:
        format = export_format_from_extension(pfile.suffix)
    if not format:
        format = 'turtle'
    
    # réciproquement, si le nom de fichier n'a pas
    # de suffixe, on en ajoute un d'après le format
    if not pfile.suffix:
        pfile = pfile.with_suffix(
            export_extension_from_format(format) or ''
            )
    
    s = metagraph.serialize(
        format=format,
        encoding='ascii' if format=='nt' else 'utf-8'
        )
    
    with open(pfile, 'wb') as dest:
        dest.write(s)


def import_formats():
    """Renvoie la liste de tous les formats disponibles pour l'import.
    
    ARGUMENTS
    ---------
    Néant.
    
    RESULTAT
    --------
    Une liste (list) de formats (str).
    """
    return [ k for k, v in rdflib_formats.items() if v['import'] ]


def export_formats():
    """Renvoie la liste de tous les formats disponibles pour l'export.
    
    ARGUMENTS
    ---------
    Néant.
    
    RESULTAT
    --------
    Une liste (list) de formats (str).
    """
    return [ k for k in rdflib_formats.keys() ]


def import_extensions_from_format(format=None):
    """Renvoie la liste des extensions associées à un format d'import.
    
    ARGUMENTS
    ---------
    - [optionnel] format (str): un format d'import présumé inclus dans
    la liste des formats reconnus par les fonctions de RDFLib
    (rdflib_formats avec import=True).
    
    RESULTAT
    --------
    La liste de toutes les extensions associées au format considéré,
    avec le point.
    
    Si format n'est pas renseigné, la fonction renvoie la liste
    de toutes les extensions reconnues pour l'import.
    
    EXEMPLES
    --------
    >>> rdf_utils.import_extensions('xml')
    ['.rdf', '.xml']
    """
    if not format:
        l = []
        for k, d in rdflib_formats.items():
            if d['import']:
                l += d['extensions']
        return l
    
    d = rdflib_formats.get(format)
    if d and d['import']:
        return d['extensions']


def export_extension_from_format(format):
    """Renvoie l'extension utilisée pour les exports dans le format considéré.
    
    ARGUMENTS
    ---------
    - format (str): un format d'export présumé inclus dans la liste
    des formats reconnus par les fonctions de RDFLib (rdflib_formats).
    
    RESULTAT
    --------
    L'extension (str) à utiliser pour le format considéré, avec le
    point.
    
    EXEMPLES
    --------
    >>> rdf_utils.export_extension('pretty-xml')
    '.rdf'
    """
    d = rdflib_formats.get(format)
    if d:
        return d['extensions'][0]


def import_format_from_extension(extension):
    """Renvoie le format d'import correspondant à l'extension.
    
    ARGUMENTS
    ---------
    - extension (str) : une extension (avec point).
    
    La fonction renvoie None si l'extension n'est pas
    reconnue.
    
    RESULTAT
    --------
    Un nom de format (str).
    """
    for k, d in rdflib_formats.items():
        if d['import'] and extension in d['extensions']:
            return k


def export_format_from_extension(extension):
    """Renvoie le format d'export correspondant à l'extension.
    
    ARGUMENTS
    ---------
    - extension (str) : une extension (avec point).
    
    La fonction renvoie None si l'extension n'est pas
    reconnue.
    
    RESULTAT
    --------
    Un nom de format (str).
    """
    for k, d in rdflib_formats.items():
        if d['export default'] and extension in d['extensions']:
            return k

   
def available_formats(metagraph, shape):
    """List valid export formats for given metagraph.
    
    ARGUMENTS
    ---------
    - metagraph (rdflib.graph.Graph) : un graphe de métadonnées.
    - shape (rdflib.graph.Graph) : schéma SHACL augmenté décrivant
    les catégories de métadonnées communes. Il fournit ici les préfixes
    d'espaces de nommage à déclarer dans le graphe.
    
    RESULTAT
    --------
    Une liste de formats (str) pouvant être utilisés pour
    sérialiser le graphe.
    """
    
    for n, u in shape.namespace_manager.namespaces():
            metagraph.namespace_manager.bind(n, u, override=True, replace=True)

    l = export_formats()

    # Une méthode plus gourmande pourrait consister à purement et simplement
    # tester toutes les sérialisations possibles et retourner celles qui
    # ne produisent pas d'erreur. À ce stade, il semble cependant que
    # la seule incompatibilité prévisible et admissible soit la
    # combinaison XML + usage d'UUID pour les métadonnées locales. C'est
    # donc uniquement ce cas qui est testé ici.

    for p in metagraph.predicates():
    
        if str(p).startswith('urn:uuid:'):
            for f in ("xml", "pretty-xml"):
                if f in l:
                    l.remove(f)            
            break
            
        # try:
            # split_uri(p)
        # except:
            # for f in ("xml", "pretty-xml"):
                # if f in l:
                    # l.remove(f)            
            # break
            
    return l
   

def metagraph_from_file(filepath, format=None):
    """Parse file content as metagraph.
    
    ARGUMENTS
    ---------
    - filepath (str) : chemin complet du fichier source,
    supposé contenir des métadonnées dans un format RDF,
    sans quoi l'import échouera.
    - format (str) : le format des métadonnées. Si non
    renseigné, RDFLib déduira le format de l'extension du fichier,
    qui devra donc être cohérente avec son contenu.
    Valeurs acceptées : "turtle", "json-ld", "xml", "n3", "nt",
    "trig".
    
    Le fichier sera présumé être encodé en UTF-8 et mieux
    vaudrait qu'il le soit.
    
    RESULTAT
    --------
    Un graphe de métadonnées (rdflib.graph.Graph).
    """
    pfile = Path(filepath)
    
    if not pfile.exists():
        raise FileNotFoundError("Can't find file {}.".format(filepath))
        
    if not pfile.is_file():
        raise TypeError("{} is not a file.".format(filepath))
    
    if format and not format in import_formats():
        raise ValueError("Format '{}' is not supported.".format(format))
    
    if not format:
    
        if not pfile.suffix in import_extensions_from_format():
            raise TypeError("Couldn't guess RDF format from file extension."\
                            "Please use format to declare it manually.")
                            
        else:
            format = import_format_from_extension(pfile.suffix)
            # NB : en théorie, la fonction parse de RDFLib est censée
            # pouvoir reconnaître le format d'après l'extension, mais à
            # ce jour elle n'identifie même pas toute la liste ci-avant.
    
    with pfile.open(encoding='UTF-8') as src:
        g = Graph().parse(data=src.read(), format=format)

    return g
    

def iter_children_keys(widgetsdict, key):
    """Generator on keys of given record children.
    
    ARGUMENTS
    ---------
    - widgetsdict (WidgetsDict) : dictionnaire obtenu par exécution de la
    fonction build_dict.
    - key (tuple) : clé d'un dictionnaire de widgets (WidgetsDict).
    
    RESULTAT
    --------
    Un générateur sur les clés des enregistrements du dictionnaire dont
    key est la clé parente, qui pourra être appelé ainsi :
    >>> for k in iter_children_keys(widgetsdict, key):
    ...     [do whatever]
    
    EXEMPLES
    --------
    >>> for k in rdf_utils.iter_children_keys(d, (0,)):
    ...     print(k)
    """
    for k in widgetsdict.keys():
        if len(k) > 1 and k[1] == key:
            yield k


def iter_siblings_keys(widgetsdict, key, include=False):
    """Generator on keys of given record siblings.
    
    ARGUMENTS
    ---------
    - widgetsdict (WidgetsDict) : dictionnaire obtenu par exécution de la
    fonction build_dict.
    - key (tuple) : clé d'un dictionnaire de widgets (WidgetsDict).
    - [optionnel] include (bool) : indique si key doit être incluse
    dans le générateur. False par défaut.
    
    RESULTAT
    --------
    Un générateur sur les enregistrements du dictionnaire de même
    parent que key, qui pourra être appelé ainsi :
    >>> for k in iter_siblings_keys(widgetsdict, key):
    ...     [do whatever]
    
    EXEMPLES
    --------
    >>> for k in rdf_utils.iter_siblings_keys(d, (0, (0,))):
    ...     print(k)
    """
    if len(key) > 1:
        for k in widgetsdict.keys():
            if len(k) > 1 and k[1] == key[1] \
                and (include or not k == key):
                yield k


def load_shape():
    """Renvoie le graphe RDF contenant le schéma SHACL des catégories communes (shape).
    
    ARGUMENTS
    ---------
    Néant.
    
    RESULTAT
    --------
    Le graphe RDF (rdflib.graph.Graph) auquel fait référence
    l'argument "shape" des fonctions du présent script.
    """
    return metagraph_from_file(__path__[0] + r'\modeles\shape.ttl')
    
    
def load_vocabulary():
    """Renvoie le graphe RDF contenant la compilation des thésaurus (vocabulary).
    
    ARGUMENTS
    ---------
    Néant.
    
    RESULTAT
    --------
    Le graphe RDF (rdflib.graph.Graph) auquel fait référence
    l'argument "vocabulary" des fonctions du présent script.
    """
    return metagraph_from_file(__path__[0] + r'\modeles\vocabulary.ttl')


def is_dataset_uri(anyIRI):
    """anyIRI est-il un identifiant de jeu de données ?
    
    ARGUMENTS
    ---------
    - anyIRI (URIRef) : un IRI quelconque.
    
    RESULTAT
    --------
    True si la forme d'anyIRI est celle d'un identifiant
    de jeu de données, False sinon.
    
    En aucun cas cette fonction ne vérifie qu'il y a bien
    dans la base PostgreSQL une table avec ledit identifiant.
    
    EXEMPLES
    --------
    >>> rdf_utils.is_dataset_uri(URIRef("urn:uuid:88b31c95-ff96-4b85-bb55-1edc65402129"))
    True
    
    """
    return re.fullmatch('^urn[:]uuid[:][a-z0-9-]{36}$', str(anyIRI)) is not None


def text_with_link(anyStr, anyIRI):
    """Génère un fragment HTML définissant un lien.
    
    ARGUMENTS
    ---------
    - anyStr (str) : la chaîne de caractères porteuse du lien.
    - anyIRI (URIRef) : un IRI quelconque correspondant à la
    cible du lien.
    
    RESULTAT
    --------
    Une chaîne de caractère (str) correspondant à un élément A,
    qui sera interprétée par les widgets comme du texte riche.
    
    EXEMPLES
    --------
    >>> rdf_utils.text_with_link(
    ...     "Documentation de PostgreSQL 10",
    ...     URIRef("https://www.postgresql.org/docs/10/index.html")
    ...     )
    '<A href="https://www.postgresql.org/docs/10/index.html">Documentation de PostgreSQL 10</A>'
    """
    return """<a href="{}">{}</a>""".format(
        escape(str(anyIRI), quote=True),
        escape(anyStr, quote=True)
        )
    

def get_datasetid(metagraph):
    """Renvoie l'identifiant du jeu de données contenu dans le graphe.
    
    ARGUMENTS
    ---------
    - metagraph (rdflib.graph.Graph) : un graphe de métadonnées.
    
    RESULTAT
    --------
    L'identifiant (URIRef) du jeu de données contenu dans le graphe.
    
    Cette fonction renvoie None si le graphe ne contient pas de jeu
    de données.
    """
    for s in metagraph.subjects(
        URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
        URIRef("http://www.w3.org/ns/dcat#Dataset")
        ):
        return s


def strip_uuid(datasetid):
    """Extrait l'UUID d'un identifiant de dataset.
    
    ARGUMENTS
    ---------
    - datasetid (rdflib.URIRef) : un identifiant de jeu de données.
    
    RESULTAT
    --------
    Une chaîne de caractères (str) correspondant à l'UUID du jeu de
    données, sans espace de nommage.
    
    Cette fonction renvoie None si l'identifiant du jeu de données n'est
    pas un UUID.
    """
    u = re.search('[:]([a-z0-9-]{36})$', str(datasetid))
    if u:
        return u[1]


def build_geoide_json(metagraph):
    """Renvoie une vue JSON basique des métadonnées, à l'usage de GéoIDE.
    
    ARGUMENTS
    ---------
    - metagraph (rdflib.graph.Graph) : un graphe de métadonnées.
    
    RESULTAT
    --------
    Une chaîne de caractères (str) correspondant au JSON à copier entre
    les balises <GEOIDE> et </GEOIDE> du descriptif PostgreSQL, à l'usage de
    GéoIDE Catalogue.
    """
    
    datasetid = get_datasetid(metagraph)
    if not datasetid:
        return None
    
    d = {}
    
    # identifiant
    e = strip_uuid(datasetid)
    if e:
        d.update({ "business_id": str(e) })
    
    # titre
    e = metagraph.value(
        datasetid,
        URIRef("http://purl.org/dc/terms/title")
        )
        # on prend le premier élément renvoyé, qui est donc
        # susceptible d'être dans n'importe quelle langue
    if e:
        d.update({ "title" : str(e) })
        
    # description
    l = []
    for e in metagraph.objects(
        datasetid,
        URIRef("http://purl.org/dc/terms/description")
        ):
        l.append(str(e))
    c = "\n\n".join(l)
    # s'il y a plusieurs traductions, elles sont concaténées.
    d.update({ "description" : c })
    
    # mots-clés
    l = []
    for e in metagraph.objects(
        datasetid,
        URIRef("http://www.w3.org/ns/dcat#keyword")
        ):
        l.append(str(e))
    if l:
        d.update({ "keywords" : l })

    # jeu original
    for e in metagraph.objects(
        datasetid,
        URIRef("http://snum.scenari-community.org/Metadata/Vocabulaire/#isExternal")
        ):
        # n'est pas supposé renvoyer plus d'un élément,
        # on prend le premier qui soit un vrai booléen,
        # quoi qu'il en soit
        s = str(e).lower()
        if s in ('true', 'false'):
            d.update({ "original" : (s == 'false') })
            break

    # version
    e = metagraph.value(
        datasetid,
        URIRef("http://www.w3.org/2002/07/owl#versionInfo")
        )
        # n'est pas supposé renvoyer plus d'un élément,
        # on ne prend que le premier quoi qu'il en soit
    if e:
        d.update({ "version" : str(e) })

    # emprises géographiques nommées
    l = []
    for p in metagraph.objects(
        datasetid,
        URIRef("http://purl.org/dc/terms/spatial")
        ):
        z = metagraph.value(
            p, URIRef("http://www.w3.org/2004/02/skos/core#inScheme")
            )
        if z:
            for e in metagraph.objects(
                p, URIRef("http://purl.org/dc/terms/identifier")
                ):
                h = '{}/{}'.format(z, e)
                if forbidden_char(h) is None:
                    l.append(h)
    if l:
        d.update({ "extent" : l })
    
    # rectangles d'emprise
    e = metagraph.value(
        datasetid,
        URIRef("http://purl.org/dc/terms/spatial") /
        URIRef("http://www.w3.org/ns/dcat#bbox")
        )
    if e and e.datatype == URIRef("http://www.opengis.net/ont/geosparql#wktLiteral") \
        and ( str(e).startswith("POLYGON") or "/CRS84> POLYGON" in str(e) \
        or "/4979> POLYGON" in str(e) ):
        # ne fournira des coordonnées en degré d'angle que si on était en
        # CRS84 / EPSG 4979 au départ (http://www.opengis.net/def/crs/OGC/1.3/CRS84),
        # c'est plus ou moins ce que vérifie la condition ci-avant
        long = re.findall(r"(?:[(]|[,])(?:\s)*([-]?[0-9]+(?:[.][0-9]+)?)\s", str(e))
        lat = re.findall(r"\s([-]?[0-9]+(?:[.][0-9]+)?)(?:\s)*(?:[)]|[,])", str(e))
        if long and lat:
            longmax = max(long)
            longmin = min(long)
            latmax = max(lat)
            latmin = min(lat)
            if longmax != longmin and latmax != latmin:
                d.update({ "geographicextent / westBoundLongitude" : longmin })
                d.update({ "geographicextent / eastBoundLongitude" : longmax })
                d.update({ "geographicextent / southBoundLatitude" : latmin })
                d.update({ "geographicextent / northBoundLatitude" : latmax })
                
    
    # date et heure de modification
    for e in metagraph.objects(
        datasetid,
        URIRef("http://purl.org/dc/terms/modified")
        ):
        # n'est pas supposé renvoyer plus d'un élément,
        # on ne prend que le premier quoi qu'il en soit
        if re.fullmatch(
            "^[0-9]{4}[-][0-9]{2}[-][0-9]{2}(T[0-9]{2}[:][0-9]{2}[:][0-9]{2}" \
            "([.][0-9]{6})?([+][0-9]{2}[:][0-9]{2}([:][0-9]{2}([.][0-9]{6})?)?)?)?$",
            str(e)
            ):
            d.update({ "lastRevisionDate" : str(e) })
            break
    
    # URL des ressources liées
    l = []
    for e in metagraph.objects(
        datasetid,
        URIRef("http://xmlns.com/foaf/0.1/page")
        ):
        l.append(str(e))
    for e in metagraph.objects(
        datasetid,
        URIRef("http://www.w3.org/ns/dcat#landingPage")
        ):
        l.append(str(e))
    d.update({ "document / path" : l })
    
    # point de contact
    p = metagraph.value(
        datasetid,
        URIRef("http://www.w3.org/ns/dcat#contactPoint")
        )
    if p:
        n = metagraph.value(
            p, URIRef("http://www.w3.org/2006/vcard/ns#fn")
            )
        m = metagraph.value(
            p, URIRef("http://www.w3.org/2006/vcard/ns#hasEmail")
            )
        if n:
            d.update({ "contact / name" : str(n) })
        if m:
            d.update({ "contact / email" : email_from_owlthing(m) })
    
    # généalogie
    l = []
    for e in metagraph.objects(
        datasetid,
        URIRef("http://purl.org/dc/terms/provenance") /
        URIRef("http://www.w3.org/2000/01/rdf-schema#label")
        ):
        l.append(str(e))
    for e in metagraph.objects(
        datasetid,
        URIRef("http://www.w3.org/ns/adms#versionNotes")
        ):
        l.append(str(e))
    c = "\n\n".join(l)
    d.update({ "lineage" : c })
    
    return dumps(d, indent=4, ensure_ascii=False)


def get_geoide_json_uuid(description):
    """Renvoie l'UUID contenu dans le JSON de GéoIDE, si présent.

    ARGUMENTS
    ---------
    - description (str) : chaîne de caractères supposée correspondre à la
    description (ou le commentaire) d'un objet PostgreSQL.

    RESULTAT
    --------
    Une chaîne de caractère (str) correspondant à un UUID.
    
    Pour que cette fonction retourne un résultat, il faut :
    - que les balises <GEOIDE> et </GEOIDE> soient présentes ;
    - que leur contenu soit un JSON dé-sérialisable ;
    - que "business_id" soit une clé de premier niveau du JSON ;
    - que sa valeur respecte la forme d'un UUID.
    """
    if not description:
        return None
    
    j = re.search("^(?:.*)[<]GEOIDE[>](.*?)[<][/]GEOIDE[>]", description, re.DOTALL)
    # s'il y a plusieurs balises <GEOIDE> et/ou </GEOIDE>, cette expression retient
    # les caractères compris entre la dernière balise <GEOIDE> et la première balise </GEOIDE>.
    # s'il devait y avoir plusieurs couples de balises, elle retiendrait le contenu du
    # dernier.
    
    if j is None or not j[1]:
        return None

    try:
        d = loads(j[1])
    except:
        return None
  
    if not isinstance(d, dict):
        return None
        
    uuid = d.get('business_id')
    
    if uuid and re.fullmatch('^[a-z0-9-]{36}$', uuid):
        return uuid

    return None


def uripath_from_sparqlpath(path, nsm, strict=True):
    """Convertit un chemin SPARQL en chemin d'URIRef.

    ARGUMENTS
    ---------
    - path (str) : un chemin SPARQL.
    - nsm (rdflib.namespace.NamespaceManager) : un
    gestionnaire d'espaces de nommage.
    - strict (bool) : si True (défaut), la fonction échoue
    sur un chemin invalide. Si False elle renvoie None.

    RESULTAT
    --------
    Si path ne contient qu'un élément, l'URIRef correspondant.
    Si path est composé de plusieurs éléments, un objet RDFLib Path.
    
    ATTENTION : à ce stade, cette fonction ne renverra un
    résultat correct que si le chemin est formé d'éléments
    préfixés (pas de "<elem>", seulement "prefix:elem").
    
    Appliquée à un chemin à un élément, uripath_from_sparqlpath
    est similaire à la fonction from_n3() de RDFLib, si ce n'est que
    son résultat est plus contrôlé.
    """
    d = { k: v for k, v in nsm.namespaces() }
    l = re.split(r"\s*[/]\s*", path)
    p = None
    
    for e in l:
        r = re.match('^([a-z]+)[:]([a-zA-Z0-9-]+)$', e)
        if r and r[1] and r[2]:
            if r[1] in d:
                p = ( p / URIRef(str(d[r[1]]) + r[2]) ) if p \
                    else URIRef(str(d[r[1]]) + r[2])
            elif strict:
                raise ValueError("Unknown namespace prefix '{}'.".format(r[1]))
        elif strict:
            raise ValueError("'{}' is not a valid prefixed SPARQL path element.".format(e))
            
    return p


def pick_translation(litList, language):
    """Renvoie l'élément de la liste correspondant à la langue désirée.
    
    ARGUMENTS
    ---------
    - litList (list) : une liste de Literal, présumés
    de type xsd:string.
    - language (str) : la langue pour laquelle on cherche
    une traduction.
    
    RESULTAT
    --------
    Un des éléments de la liste (Literal), qui peut être :
    - le premier dont la langue est language ;
    - à défaut, le dernier dont la langue est 'fr' ;
    - à défaut, le premier de la liste.
    
    ATTENTION : cette fonction ne doit en aucun cas être
    appliquée à une liste vide (provoquerait une erreur).
    """
    val = None
    
    for l in litList:
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
        val = litList[0]
        
    return val


def clean_metagraph(raw_metagraph, shape, old_metagraph=None,
    mMetagraph=None, mTriple=None, mSubject=None,
    mMemMetagraph=None, mMap=None):
    """Nettoie un graphe issu d'une source externe.
    
    ARGUMENTS
    ---------
    - raw_metagraph (rdflib.graph.Graph) : un graphe de métadonnées
    présumé issu d'un import via metagraph_from_file ou
    équivalent.
    - shape (rdflib.graph.Graph) : schéma SHACL augmenté décrivant
    les catégories de métadonnées communes.
    - [optionnel] old_metagraph (rdflib.graph.Graph) : l'ancien
    graphe de métadonnées de l'objet PostgreSQL considéré, dont on
    récupèrera l'identifiant.
    
    Les autres arguments servent uniquement aux appels récursifs
    de la fonction.
    
    RESULTAT
    --------
    Un graphe (rdflib.graph.Graph) retraité pour qu'un maximum de
    métadonnées soient reconnues lors du passage dans build_dict().
    En particulier, la fonction s'assure que tous les noeuds internes sont
    de type BNode et donne un nouvel identifiant à la fiche.
    """
    
    if mSubject is None:
    
        # ------ initialisation ------
        
        mMetagraph=Graph()
        # mMetagraph est le futur graphe nettoyé
        mMemMetagraph=Graph()
        # mMemMetagraph contient les éléments de
        # metagraph déjà traités. Il est là pour éviter
        # les boucles infinies
        
        mTriple=None
        
        # mapping de propriétés qui ont notoirement tendance à
        # être mal écrites (formes dépréciées, coquilles...)
        mMap = {
            URIRef("http://www.w3.org/2006/vcard/ns#organisation-name"): URIRef("http://www.w3.org/2006/vcard/ns#organization-name"),
            URIRef("http://schema.org/endDate"): URIRef("http://www.w3.org/ns/dcat#endDate"),
            URIRef("http://schema.org/startDate"): URIRef("http://www.w3.org/ns/dcat#startDate")
            }
        
    
        # ------ gestion de l'identifiant -------
        
        mSubject = get_datasetid(raw_metagraph)
        mNSubject = None
        
        # autant que possible, on récupère l'identifiant
        # de l'ancien graphe
        if old_metagraph:
            mNSubject = get_datasetid(old_metagraph)

        # le graphe ne contient pas de dcat:Dataset
        # on renvoie un graphe avec uniquement l'ancien
        # identifiant, ou vierge en l'absence d'identifiant
        if not mSubject :
            if mNSubject:
                mMetagraph.add( (
                    mNSubject,
                    URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
                    URIRef("http://www.w3.org/ns/dcat#Dataset")
                    ) )
            return mMetagraph
        
        # à défaut d'avoir pu récupérer l'identifiant de
        # l'ancien graphe, on en génère un nouveau
        if not mNSubject:
            mNSubject = URIRef("urn:uuid:" + str(uuid.uuid4())) 

    
    # ------ exécution courante ------
        
    l = [ (p, o) for p, o in raw_metagraph.predicate_objects(mSubject) ]
    
    # juste un IRI avec une classe, on oublie
    # l'information sur la classe
    if len(l) == 1 and \
        l[0][0] == URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"):
        l = []
        
    if l:
        t = raw_metagraph.value(
            mSubject,
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
            )
            
        # pas de classe, ou classe non décrite dans shape
        # un IRI ou Literal sera écrit tel quel,
        # sans ses descendants, un BNode est effacé
        if not t or not (
            None, URIRef("http://www.w3.org/ns/shacl#targetClass"), t
            ) in shape:
            l = []
            if isinstance(mSubject, BNode):
                mTriple = None

    # suppression des noeuds vides terminaux
    if not l and isinstance(mSubject, BNode):
        mTriple = None

    if mTriple:
    
        mNSubject = mSubject
    
        # cas d'un IRI non terminal
        # on le remplace par un noeud vide
        if l and not isinstance(mSubject, BNode):
            mNSubject = BNode()
            mTriple = (mTriple[0], mTriple[1], mNSubject)
        
        mMetagraph.add(mTriple)        
    
    for p, o in l:
    
        if not (mSubject, p, o) in mMemMetagraph:
            mMemMetagraph.add((mSubject, p, o))
            clean_metagraph(
                raw_metagraph=raw_metagraph, shape=shape,
                old_metagraph=old_metagraph, mMetagraph=mMetagraph,
                mTriple=(mNSubject, mMap.get(p, p), o), mSubject=o,
                mMemMetagraph=mMemMetagraph, mMap=mMap
                )
                
    return mMetagraph
    

def copy_metagraph(src_metagraph, old_metagraph=None):
    """Renvoie un graphe avec l'identifiant de old_metagraph et les métadonnées de src_metagraph.
    
    ARGUMENTS
    ---------
    - src_metagraph (rdflib.graph.Graph) : le graphe dont on
    souhaite copier le contenu. None est admis et aura le même
    effet qu'un graphe vide.
    - [optionnel] old_metagraph (rdflib.graph.Graph) : l'ancien
    graphe de métadonnées de l'objet PostgreSQL considéré, dont on
    récupèrera l'identifiant.
    
    RESULTAT
    --------
    Un graphe (rdflib.graph.Graph) dont l'identifiant est,
    autant que possible, l'identifiant de old_metagraph, et
    qui contient toutes les métadonnées des src_metagraph.
    
    La fonction ne réalise aucun contrôle sur src_metagraph. Si
    celui-ci n'est pas issu d'une source fiable, il est préférable
    d'utiliser la fonction clean_metagraph().
    """
    if src_metagraph is None:
        src_metagraph = Graph()
        srcId = None
    else:  
        srcId = get_datasetid(src_metagraph)
        
    oldId = get_datasetid(old_metagraph) if old_metagraph else None
    mMetagraph = Graph()
    
    # cas où le graphe à copier ne contiendrait pas
    # de descriptif de dataset, on renvoie un graphe contenant
    # uniquement l'identifiant, ou vierge à défaut d'identifiant
    if not srcId:
        if oldId:
            mMetagraph.add( (
                oldId,
                URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
                URIRef("http://www.w3.org/ns/dcat#Dataset")
                ) )
        return mMetagraph
    
    # à défaut d'avoir pu d'extraire un identifiant de l'ancien
    # graphe, on en génère un nouveau
    if not oldId:
        oldId = URIRef("urn:uuid:" + str(uuid.uuid4()))
    
    # boucle sur les triples du graphe source, on remplace
    # l'identifiant partout où il apparaît en sujet ou (même si
    # ça ne devrait pas être le cas) en objet
    for s, p, o in src_metagraph:
        mMetagraph.add( (
            oldId if s == srcId else s,
            p,
            oldId if o == srcId else o
            ) )
        
    # NB : on ne se préoccupe pas de mettre à jour dct:identifier,
    # build_dict() s'en chargera.
    return mMetagraph
    
    

class ForbiddenOperation(Exception):
    pass



# formats reconnus par les fonctions de RDFLib
# si la clé 'import' vaut False, le format n'est
# pas reconnu à l'import. si 'export default'
# vaut True, il s'agit du format d'export privilégié
# pour les extensions de la clé 'extensions'.
rdflib_formats = {
    'turtle': {
        'extensions': ['.ttl'],
        'import': True,
        'export default': True
        },
    'n3': {
        'extensions': ['.n3'],
        'import': True,
        'export default': True
        },
    'json-ld': {
        'extensions': ['.jsonld', '.json'],
        'import': True,
        'export default': True
        },
    'xml': {
        'extensions': ['.rdf', '.xml'],
        'import': True,
        'export default': False
        },
    'pretty-xml': {
        'extensions': ['.rdf', '.xml'],
        'import': False,
        'export default': True
        },
    'nt': {
        'extensions': ['.nt'],
        'import': True,
        'export default': True
        },
    'trig': {
        'extensions': ['.trig'],
        'import': True,
        'export default': True
        }
    }

