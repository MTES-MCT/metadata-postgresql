"""
Utilitary class and functions for parsing and serializing RDF metadata.

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
import re, uuid

from metadata_postgresql.bibli_rdf import __path__


class WidgetsDict(dict):
    """Classe pour les dictionnaires de widgets.
    """
    
    def count_siblings(self, key, restrict=True):
        """Renvoie le nombre de clés de même parent que key.
        
        ARGUMENTS
        ---------
        - key (tuple) : clé du dictionnaire de widgets (WidgetsDict).
        - restrict (bool) : si True, les enregistrements "plus button"
        et "translation button" ne sont pas comptabilisés. True par défaut.
        
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
            if len(k) > 1 and k[1] == key[1] and (
                    not self[k]['object'] in ('translation button', 'plus button') \
                    or not restrict
                    ) :
                n += 1
                
        return n


    def child(self, key):
        """Renvoie la clé d'un enfant de la clé key (hors boutons).
        
        Cette fonction est supposée être lancée sur un groupe de valeurs
        ou groupe de traduction, où tous les enfants sont de même nature.
        
        ARGUMENTS
        ---------
        - key (tuple) : clé du dictionnaire de widgets (WidgetsDict).
        
        RESULTAT
        --------
        La clé (tuple) d'un enfant de l'enregistrement de clé key, en
        excluant les 'plus button' et 'translation button'.

        NB : le plus souvent, l'enregistrement renvoyé sera (0, key),
        mais il est possible que celui-ci ait été supprimé par
        activation de son bouton moins.
        """
        c = None
        
        for k in self.keys():
        
            if len(k) > 1 and k[1] == key \
                    and not self[k]['object'] in ('plus button', 'translation button'):
                    
                c = k
                break
                
        return c 


    def clean_copy(self, key, language='fr', langList=['fr', 'en']):
        """Renvoie une copie nettoyée du dictionnaire interne de la clé key.
        
        ARGUMENTS
        ---------
        - key (tuple) : clé du dictionnaire de widgets (WidgetsDict).
        - [optionnel] language (str) : langue de la nouvelle valeur.
        Français ("fr") par défaut.
        La valeur de language doit être incluse dans langList ci-après.
        - [optionnel] langList (list) : liste des langues autorisées pour
        les traductions (str). Par défaut français et anglais, soit
        ['fr', 'en'].

        RESULTAT
        --------
        Un dictionnaire, qui pourra être utilisé comme valeur pour une autre
        clé du dictionnaire de widgets.
        
        Le contenu du dictionnaire est identique à celui de la source, si
        ce n'est que :
        - les clés supposées contenir des widgets, actions et menus sont
        vides ;
        - la clé "value" est remise à la valeur par défaut ;
        - la clé "language value" vaudra language et "authorized languages"
        vaudra langList (s'il y avait lieu de spécifier une langue) ;
        - la clé "hidden" est réinitialisée (ne vaudra jamais True sauf si
        la liste des langues autorisées ne contient qu'une langue). À noter que
        "hidden M" est par contre conservée en l'état.
        """
        
        d = self[key].copy()
        
        d.update({
            'main widget' : None,
            'grid widget' : None,
            'label widget' : None,
            'minus widget' : None,
            'language widget' : None,
            'switch source widget' : None,

            'main action' : None,
            'minus action' : None,
            'switch source menu' : None,
            'switch source actions' : None,
            'language menu' : None,
            'language actions' : None,
            
            'value' : d['default value'],
            'language value' : language if d['language value'] else None,
            'authorized languages' : langList.copy() if ( d['authorized languages'] \
                                     and langList is not None ) else None,
            'sources' : d['sources'].copy() if d['sources'] is not None else None,
            'hidden' : len(langList) == 1 if ( langList is not None
                and d['object'] == 'translation button' ) else None
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


    def drop(self, key, langList=['fr', 'en']):
        """Supprime du dictionnaire un enregistrement et, en cascade, tous ses descendants.
        
        Cette fonction est à utiliser suite à l'activation par l'utilisateur
        du "bouton moins" d'un groupe de valeurs ou d'un groupe de traduction.
        Par principe, il ne devrait jamais y avoir de boutoin moins lorsque le
        groupe ne contient qu'une valeur, et faire usage de la fonction dans ce
        cas produirait une erreur.
        
        ARGUMENTS
        ---------
        - key (tuple) : une clé du dictionnaire de widgets.
        - [optionnel] langList (list) : paramètre utilisateur, liste des
        langues autorisées pour les traductions (str). Par défaut
        français et anglais, soit ['fr', 'en'].
        
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
        [2] son nouveau numéro de ligne/valeur du paramètre row (int).
        
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
        
        if len(key) < 2:
            raise ForbiddenOperation("This is the tree root, you can't cut it !")
            
        g = self[key[1]]['object']
        if not g in ('translation group', 'group of values'):
            raise ForbiddenOperation("You can't delete a record outside of a group of values or translation group.")
        
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
        n = self.count_siblings(key)
        
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
                        
                for e in ['main action', 'minus action']:
                    a = self[k][e]
                    if a:
                        d["actions to delete"].append(a)
                        
                for e in ('switch source actions', 'language actions'):
                    a = self[k][e]
                    if a:
                        d["actions to delete"] += a
                        
                for e in ('switch source menu', 'language menu'):
                    m = self[k][e]
                    if m:
                        d["menus to delete"].append(m)

            # cas des frères et soeurs
            elif len(k) > 1 and k[1] == key[1]:
            
                if self[k]['row'] > self[key]['row']:
                    
                    # mise à jour de la clé 'row' des petits frères
                    self[k]['row'] -= ( self[key]['row span'] or 1 )
                    
                    for e in ('main widget', 'minus widget', 'language widget', 'switch source widget'):
                        # pas de label widget, l'étiquette est sur le groupe
                        w = self[k][e]
                        if w:
                            d["widgets to move"].append((
                                self.parent_grid(k),
                                w,
                                self[k]['row']
                                ))
            
            
                if self[k]['object'] in ('plus button', 'translation button'):
                    
                    # si le bouton (de traduction) était masqué et que
                    # la langue de l'enregistrement à supprimer est bien
                    # dans la liste des langues autorisées, on le "démasque"
                    if g == 'translation group' and self[k]['hidden'] and language in langList:
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
                     
                    if g == 'translation group' and language in langList:
                        # on ajoute language aux listes de langues
                        # disponibles des frères et soeurs
                        if not language in self[k]['authorized languages']:
                            self[k]['authorized languages'].append(language)
                            self[k]['authorized languages'].sort()
                            d["language menu to update"].append(k)
        
        for e in l:
            del self[e]
            
        return d
   

    def add(self, key, language='fr', langList=['fr', 'en']):
        """Ajoute un enregistrement (vide) dans le dictionnaire de widgets.
        
        Cette fonction est à utiliser après activation d'un bouton plus
        (plus button) ou bouton de traduction (translation button) par
        l'utilisateur.
        
        ARGUMENTS
        ---------
        - key (tuple) : une clé du dictionnaire de widgets, et plus
        précisément la clé du bouton qui vient d'être activé par
        l'utilisateur.
        - [optionnel] language (str) : langue principale de rédaction des
        métadonnées (paramètre utilisateur). Français ("fr") par défaut.
        La valeur de language doit être incluse dans langList ci-après.
        - [optionnel] langList (list) : paramètre utilisateur, liste des
        langues autorisées pour les traductions (str). Par défaut
        français et anglais, soit ['fr', 'en'].
        
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
        [2] son nouveau numéro de ligne/valeur du paramètre row (int).
        
        EXEMPLES
        --------
        >>> d.add((1, (0, (0,))))
        """
        
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
            mLangList = langList.copy()
        
        k1 = (n, key[1]) if len(c) == 2 else (n, key[1], 'M')
        k2 = (n, key[1], 'M') if len(c) == 2 else (n, key[1])
        cm = (c[0], c[1], 'M') if len(c) == 2 else (c[0], c[1])
        
        self.update( { k1: self.clean_copy(c, language, mLangList) } )   
        self[k1]['row'] = r
        d['new keys'].append(k1)
        
        # cas d'un enregistrement avec un double M               
        if cm in self:
            self.update( { k2: self.clean_copy(cm, language, mLangList) } )   
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
            d["widgets to move"].append((
                self.parent_grid(key),
                w,
                self[key]['row']
                ))
        
        for k in self.copy().keys():
        # on fait l'itération sur une copie du
        # dictionnaire, parce qu'on va ajouter des clés
        # au cours de l'itération (et on aurait sinon des
        # erreurs de type "RuntimeError: dictionary changed
        # size during iteration")
        
            # cas des frères et soeurs
            if len(k) > 1 and k[1] == key[1] and self[k]['object'] in (
                    'group of properties', 'translation group', 'edit'):
                
                # on vient d'ajouter un enregistrement au groupe,
                # donc il y a lieu d'ajouter des boutons moins
                # s'ils n'étaient pas déjà là
                if self[k]['hide minus button']:
                    self[k]['hide minus button'] = False
                    w = self[k]['minus widget']
                    if w:
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
                and self[key]['main widget type']:
            
                if self[k[1]]['object'] == 'group of properties' \
                    or self[k]['object'] in ('plus button', 'translation button') \
                    or self[k]['row'] == 0 \
                    or self[k]['label row'] == 0:
                    # dans les groupes de propriétés, tout est dupliqué ;
                    # dans les autres groupes, on ne garde que les boutons
                    # et le groupe ou widget placé sur la première ligne
                    # de la grille
                    newkey = replace_ancestor(k, cr, (n, key[1]))
                    self.update( { newkey: self.clean_copy(k) } )
                    d['new keys'].append(newkey)
                    
        return d


    def change_language(self, key, language, langList=['fr', 'en']):
        """Change la langue sélectionnée pour une clé.
        
        ARGUMENTS
        ---------
        - key (tuple) : une clé du dictionnaire de widgets, et plus
        précisément la clé pour laquelle l'utilisateur vient de
        choisir une nouvelle langue.
        - language (str) : la nouvelle langue.
        - [optionnel] langList (list) : paramètre utilisateur, liste des
        langues autorisées pour les traductions (str). Par défaut
        français et anglais, soit ['fr', 'en'].
        
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
        
        if not self[key]['object'] == 'edit' \
            or not self[key]['data type'] == URIRef('http://www.w3.org/2001/XMLSchema#string'):
            raise ForbiddenOperation("You can't put a language tag on anything but a string !")
            
        if not self[key]['authorized languages'] \
            or not language in self[key]['authorized languages']:
            raise ForbiddenOperation("{} isn't an authorized language for key {}.".format(language, key))
        
        d = {
            "language menu to update": [],
            "widgets to hide" : []
            }
        
        # ancienne langue
        old_language = self[key]['language value']
        
        if language == old_language:
            return d
        
        b = old_language and old_language in langList
        if ( not b ) and old_language in self[key]['authorized languages']:
            self[key]['authorized languages'].remove(old_language)
            # si la langue de fait n'était pas autorisée,
            # on la supprime du menu maintenant qu'elle n'est
            # plus utilisée  
        
        # mise à jour de la langue courante pour key
        self[key]['language value'] = language
        d["language menu to update"].append(key)
                
        # dans le cas d'un groupe de traduction,
        # mise à jour des menus des frères et soeurs
        if len(key) > 1 and self[key[1]]['object'] == 'translation group':
            for k in self.keys():
                if len(k) > 1 and key[1] == k[1] and not key == k:
                
                    if self[k]['object'] == 'edit':
                
                        if language in self[k]['authorized languages']:
                            self[k]['authorized languages'].remove(language)
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
                if w:
                    d["widgets to show"].append(w)

            kshow = mkey
            
            
        elif old_source == '< manuel >':
            
            ukey = (key[0], key[1])
        
            if not len(key) == 3 or not ukey in self:
                raise RuntimeError("URI mode doesn't seem implemented for key {} (no-M key not found).".format(key))
            
            self[key]['current source'] = None
            self[ukey]['current source'] = source
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
                if w:
                    d["widgets to show"].append(w)

            khide = key
            
            if not source == '< URI >':
                d["concepts list to update"].append(ukey)
            
        else:
            # cas d'un simple changement de thésaurus
            self[key]['current source'] = source
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

        if self[key]['hidden M']:
            raise ForbiddenOperation("Widget {} is hidden, you can't update its value.".format(key))

        self[key]['value'] = value


    def build_graph(self, vocabulary, language="fr"):
        """Return a RDF graph build from given widgets dictionary.

        ARGUMENTS
        ---------
        - vocabulary (rdflib.graph.Graph) : graphe réunissant le vocabulaire de toutes
        les ontologies pertinentes.
        - [optionnel] language (str) : langue principale de rédaction des métadonnées
        (paramètre utilisateur, en l'état où il se trouve à l'issue de la saisie).
        Français ("fr") par défaut.

        RESULTAT
        --------
        Un graphe RDF de métadonnées (rdflib.graph.Graph).
        """

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
                    graph.update("""
                        INSERT
                            { ?n a ?c }
                        WHERE
                            { }
                    """,
                    initBindings = {
                        'n' : mem[2],
                        'c' : mem[3]
                        }
                    )
                    mem = None
                    
            else:
            
                if mem and mem[2] == d['subject']:
                
                    # création effective du noeud vide à partir
                    # des informations mémorisées
                    graph.update("""
                        INSERT
                            { ?s ?p ?n .
                              ?n a ?c }
                        WHERE
                            { }
                    """,
                    initBindings = {
                        's' : mem[0],
                        'p' : mem[1],
                        'n' : mem[2],
                        'c' : mem[3]
                        }
                    )
                    
                    mem = None
            
                if d['node kind'] == 'sh:Literal':
            
                    mObject = Literal( d['value'], datatype = d['data type'] ) \
                                if not d['data type'] == URIRef("http://www.w3.org/2001/XMLSchema#string") \
                                else Literal( d['value'], lang = d['language value'] )
                                
                else:
        
                    if d['transform'] == 'email':
                        mObject = owlthing_from_email(d['value'])
                        
                    elif d['transform'] == 'phone':
                        mObject = owlthing_from_tel(d['value']) 
                        
                    elif d['current source']:
                        c = concept_from_value(d['value'], d['current source'], vocabulary, language)
                        
                        if c is None:
                            raise ValueError( "'{}' isn't referenced as a label in scheme '{}' for language '{}'.".format(
                                d['value'], d['current source'], language )
                                ) 
                        else:
                            mObject = c[0]
                        
                    else:
                        f = forbidden_char(d['value'])                
                        if f:
                            raise ValueError( "Character '{}' is not allowed in ressource identifiers.".format(f) )
                            
                        mObject = URIRef( d['value'] )
                
                graph.update("""
                    INSERT
                        { ?s ?p ?o }
                    WHERE
                        { }
                """,
                initBindings = { 's' : d['subject'], 'p' : d['predicate'], 'o' : mObject }
                )  

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
            or self[key]['hidden M']:
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


def build_dict(metagraph, shape, vocabulary, template=None, templateTabs=None,
    data=None, mode='edit', readHideBlank=True, hideUnlisted=False,
    language="fr", translation=False, langList=['fr', 'en'],
    readOnlyCurrentLanguage=True, editOnlyCurrentLanguage=False,
    labelLengthLimit=25, valueLengthLimit=100, textEditRowSpan=6,
    mPath=None, mTargetClass=None, mParentWidget=None, mParentNode=None,
    mNSManager=None, mWidgetDictTemplate=None, mDict=None, mGraphEmpty=None,
    mShallowTemplate=None, mTemplateEmpty=None, mHidden=None, mHideM=None,
    mTemplateTabs=None):
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
    - [optionnel] hideUnlisted (bool) : paramètre utilisateur qui indique si les catégories
    hors template doivent être masquées. En l'absence de template, si hideUnlisted vaut True,
    seules les métadonnées communes seront visibles. False par défaut.
    - [optionnel] language (str) : langue principale de rédaction des métadonnées
    (paramètre utilisateur). Français ("fr") par défaut. La valeur de language doit être
    incluse dans langList ci-après.
    - [optionnel] translation (bool) : paramètre utilisateur qui indique si les widgets de
    traduction doivent être affichés. False par défaut.
    - [optionnel] langList (list) : paramètre utilisateur spécifiant la liste des langues
    autorisées pour les traductions (str), par défaut français et anglais, soit ['fr', 'en'].
    - [optionnel] readOnlyCurrentLanguage (bool) : paramètre utilisateur qui indique si,
    en mode lecture et lorsque le mode traduction est inactif, seules les métadonnées
    saisies dans la langue principale (paramètre language) sont affichées. True par défaut.
    À noter que si aucune traduction n'est disponible dans la langue demandée, les valeurs
    d'une langue arbitraire seront affichées. Par ailleurs, lorsque plusieurs traductions
    existe, l'unique valeur affichée apparaîtra quoi qu'il arrive dans un groupe.
    - [optionnel] editOnlyCurrentLanguage (bool) : paramètre utilisateur qui indique si,
    en mode édition et lorsque le mode traduction est inactif, seules les métadonnées
    saisies dans la langue principale (paramètre language) sont affichées. False par défaut.
    À noter que si aucune traduction n'est disponible dans la langue demandée, les valeurs
    d'une langue arbitraire seront affichées. Par ailleurs, lorsque plusieurs traductions
    existe, l'unique valeur affichée apparaîtra quoi qu'il arrive dans un groupe.
    - [optionnel] labelLengthLimit (int) : nombre de caractères au-delà duquel le label sera
    toujours affiché au-dessus du widget de saisie et non sur la même ligne. À noter que
    pour les widgets QTextEdit le label est placé au-dessus quoi qu'il arrive. 25 par défaut.
    - [optionnel] valueLengthLimit (int) : nombre de caractères au-delà duquel une valeur qui aurait
    dû être affichée dans un widget QLineEdit sera présentée à la place dans un QTextEdit.
    Indépendemment du nombre de catactères, la substitution sera aussi réalisée si la
    valeur contient un retour à la ligne. 100 par défaut.
    - [optionnel] textEditRowSpan (int) : nombre de lignes par défaut pour un widget QTextEdit
    (utilisé si non défini par shape ou template). 6 par défaut.

    Les autres arguments sont uniquement utilisés lors des appels récursifs de la fonction
    et ne doivent pas être renseignés manuellement.

    RESULTAT
    --------
    Un dictionnaire (WidgetsDict) avec autant de clés que de widgets à empiler verticalement
    (avec emboîtements). Les valeurs associées aux clés sont elles mêmes des dictionnaires,
    contenant les informations utiles à la création des widgets + des clés pour le
    stockage des futurs widgets.

    La clé du dictionnaire externe est un tuple formé :
    [0] d'un index, qui garantit l'unicité de la clé.
    [1] de la clé du groupe parent.
    [2] dans quelques cas, la lettre M, indiquant que le widget est la version "manuelle" d'un
    widget normalement abondé par un ou plusieurs thésaurus. Celui-ci a la même clé sans "M"
    (même parent, même index, même placement dans la grille). Ces deux widgets sont
    supposés être substitués l'un à l'autre dans la grille lorque l'utilisateur active ou
    désactive le "mode manuel" (cf. 'switch source widget' ci-après)
    

    Description des clés des dictionnaires internes :
    
    - 'object' : classification des éléments du dictionnaire. "group of values" ou
    "group of properties" ou "translation group" ou "edit" ou "plus button" ou "translation button".
    Les "translation group" et "translation button" ne peuvent exister que si l'argument
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
    - 'main action' : pour la QAction éventuellement associée au widget principal.
    - 'minus action' : pour la QAction associée au 'minus widget'.    

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
    clé s'appelle simplement "order" dans le template).

    * ces clés apparaissent aussi dans le dictionnaire interne de template.
    ** le dictionnaire interne de template contient également une clé 'data type', mais dont les
    valeurs sont des chaînes de catactères parmi 'string', 'boolean', 'decimal', 'integer', 'date',
    'time', 'dateTime', 'duration', 'float', 'double' (et non des objets de type URIRef).
    *** le chemin est la clé principale de template.
    
    EXEMPLES
    --------
    >>> g.build_dict(shape, template, vocabulary)
    """

    nsm = mNSManager or shape.namespace_manager
    
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
        
        # on travaille sur une copie du template pour pouvoir supprimer les catégories
        # au fur et à mesure de leur traitement par la première itération (sur les
        # catégories communes). À l'issue de celle-ci, ne resteront donc dans le
        # dictionnaire que les catégories locales.
        mShallowTemplate = template.copy() if template else dict()        

        # récupération de l'identifiant
        # du jeu de données dans le graphe, s'il existe
        if not mGraphEmpty:
        
            q_id = metagraph.query(
                """
                SELECT
                    ?id
                WHERE
                    { ?id a dcat:Dataset . }
                """
                )

            if len(q_id) > 1:
                raise ValueError("More than one dcat:Dataset object in graph.")

            for i in q_id:
                mParentNode = i['id']

        # si on n'a pas pu extraire d'identifiant, on en génère un nouveau
        # (et, in fine, le formulaire sera vierge)
        mParentNode = mParentNode or URIRef("urn:uuid:" + str(uuid.uuid4()))

        # coquille de dictionnaire pour les attributs des widgets
        mWidgetDictTemplate = {
            'object' : None,
            
            'main widget' : None,
            'grid widget' : None,
            'label widget' : None,
            'minus widget' : None,
            'language widget' : None,
            'switch source widget' : None,

            'main action' : None,
            'minus action' : None,
            'switch source menu' : None,
            'switch source actions' : None,
            'language menu' : None,
            'language actions' : None,
            
            'main widget type' : None,
            'row' : None,
            'row span' : None,              
            'label' : None,
            'label row' : None,
            'help text' : None,
            'value' : None,
            'language value': None,
            'placeholder text' : None,
            'input mask' : None,
            'is mandatory' : None,
            'has minus button' : None,
            'hide minus button': None,
            'regex validator pattern' : None,
            'regex validator flags' : None,
            'type validator' : None,
            'multiple sources': None,
            'sources' : None,
            'current source' : None,
            'authorized languages' : None,
            'read only' : None,
            'hidden' : None,
            'hidden M' : None,
            
            'default value' : None,
            'multiple values' : None,
            'node kind' : None,
            'data type' : None,
            'ontology' : None,
            'transform' : None,
            'class' : None,
            'path' : None,
            'subject' : None,
            'predicate' : None,
            'node' : None,
            'default widget type' : None,
            'one per language' : None,
            'next child' : None,
            'shape order' : None,
            'template order' : None
            }
        
        mTemplateTabs = templateTabs.copy() if templateTabs \
                        else { "Général": (0,) } 

        # on initialise le dictionnaire avec les groupes racines,
        # qui correspondent aux onglets du formulaire :
        mDict = {}
        for label, key in mTemplateTabs.items():       
            mDict.update( { key : mWidgetDictTemplate.copy() } )
            mDict[key].update( {
                'object' : 'group of properties',
                'main widget type' : 'QGroupBox',
                'label' : label or '???',
                'row' : 0,
                'node' : mParentNode,
                'class' : URIRef('http://www.w3.org/ns/dcat#Dataset'),
                'shape order' : key[0]
                } ) 

        mParentWidget = (0,)


    # ---------- EXECUTION COURANTE ----------

    idx = dict( { mParentWidget : 0 } )
    rowidx = dict( { mParentWidget : 0 } )

    # on extrait du modèle la liste des catégories de métadonnées qui
    # décrivent la classe cible, avec leurs caractéristiques
    q_tp = shape.query(
        """
        SELECT
            ?property ?name ?kind ?type
            ?class ?order ?widget ?descr
            ?default ?min ?max ?unilang
            ?pattern ?flags ?transform
            ?placeholder ?rowspan ?mask
        WHERE
            { ?u sh:targetClass ?c ;
                sh:property ?x .
              ?x sh:path ?property ;
                sh:name ?name ;
                sh:nodeKind ?kind ;
                sh:order ?order .
              OPTIONAL { ?x snum:widget ?widget } .
              OPTIONAL { ?x sh:datatype ?type } .
              OPTIONAL { ?x sh:class ?class } .
              OPTIONAL { ?x sh:description ?descr } .
              OPTIONAL { ?x snum:placeholder ?placeholder } .
              OPTIONAL { ?x snum:inputMask ?mask } .
              OPTIONAL { ?x sh:defaultValue ?default } .
              OPTIONAL { ?x sh:pattern ?pattern } .
              OPTIONAL { ?x sh:flags ?flags } .
              OPTIONAL { ?x snum:transform ?transform } .
              OPTIONAL { ?x snum:rowSpan ?rowspan } .
              OPTIONAL { ?x sh:uniqueLang ?unilang } .
              OPTIONAL { ?x sh:minCount ?min } .
              OPTIONAL { ?x sh:maxCount ?max } . }
        ORDER BY ?order
        """,
        initBindings = { 'c' : mTargetClass }
        )

    # --- BOUCLE SUR LES CATEGORIES
    
    for p in q_tp:

        mParent = mParentWidget
        mProperty = p['property']
        mKind = p['kind'].n3(nsm)
        mNPath = ( mPath + " / " if mPath else '') + mProperty.n3(nsm)
        mSources = None
        mDefaultTrad = None
        mDefaultSource = None
        mLangList = None
        mNHidden = mHidden or False
        mOneLanguage = None
        values = None

        # cas d'une propriété dont les valeurs sont mises à
        # jour à partir d'informations disponibles côté serveur
        if data and mNPath in data:
            values = data[mNPath]

        # sinon, on extrait la ou les valeurs éventuellement
        # renseignées dans le graphe pour cette catégorie
        # et le sujet considéré
        if not values and not mGraphEmpty:
        
            q_gr = metagraph.query(
                """
                SELECT
                    ?value
                WHERE
                     { ?n ?p ?value . }
                """,
                initBindings = { 'n' : mParentNode, 'p' : mProperty }
                )
                
            values = [ v['value'] for v in q_gr ]
    
        # exclusion des catégories qui ne sont pas prévues par
        # le modèle et n'ont pas de valeur renseignée
        if values in ( None, [], [ None ] ) and not mTemplateEmpty and not ( mNPath in template ):
            continue
        # s'il y a une valeur, mais que
        # hideUnlisted vaut True et que la catégorie n'est
        # pas prévue par le modèle, on poursuit le traitement
        # pour ne pas perdre la valeur, mais on ne créera
        # pas de widget
        elif hideUnlisted and not mTemplateEmpty and not ( mNPath in template ):
            mNHidden = True
        
        if not ( readHideBlank and mode == 'read' ):
            values = values or [ None ]
        
        if not mNHidden and ( mNPath in mShallowTemplate ):
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


        if mNHidden:
            # cas d'une catégorie qui ne sera pas affichée à l'utilisateur, car
            # absente du template, mais pour laquelle une valeur était renseignée
            # et qu'il s'agit de ne pas perdre
        
            if len(values) > 1:               
                # si plusieurs valeurs étaient renseignées, on référence un groupe
                # de valeurs (dans certains cas un groupe de traduction aurait été plus
                # adapté, mais ça n'a pas d'importance) sans aucune autre propriété
                mWidget = ( idx[mParent], mParent )
                mDict.update( { mWidget : mWidgetDictTemplate.copy() } )
                mDict[mWidget].update( {
                    'object' : 'group of values'
                    } )

                idx[mParent] += 1
                idx.update( { mWidget : 0 } )
                mParent = mWidget        
        
        else:
            # récupération de la liste des thésaurus
            if mKind in ("sh:BlankNodeOrIRI", "sh:IRI") :

                q_on = shape.query(
                    """
                    SELECT
                        ?ontology
                    WHERE
                        { ?u sh:targetClass ?c .
                          ?u sh:property ?x .
                          ?x sh:path ?p .
                          ?x snum:ontology ?ontology . }
                    """,
                    initBindings = { 'c' : mTargetClass, 'p' : mProperty }
                    )

                for s in q_on:
                    
                    q_vc = vocabulary.query(
                        """
                        SELECT
                            ?scheme
                        WHERE
                            {{ ?s a skos:ConceptScheme ;
                             skos:prefLabel ?scheme .
                              FILTER ( lang(?scheme) = "{}" ) }}
                        """.format(language),
                        initBindings = { 's' : s['ontology'] }
                        )

                    mSources = ( mSources or [] ) + ( [ str(l['scheme']) for l in q_vc ] if len(q_vc) == 1 else [] )
                        
                if mSources == []:
                    mSources = None

                if mSources and t.get('default value', None):
                    mDefaultSource = concept_from_value(t.get('default value', None), None, vocabulary, language)[1]
                elif mSources and p['default']:
                    mDefaultTrad, mDefaultSource = value_from_concept(p['default'], vocabulary, language)   
                    
                        
            multilingual = p['unilang'] and bool(p['unilang']) or False
            multiple = ( p['max'] is None or int( p['max'] ) > 1 ) and not multilingual
            
            # si seules les métadonnées dans la langue
            # principale doivent être affichées et qu'aucune valeur n'est
            # disponible dans cette langue, on prendra le parti d'afficher
            # arbitrairement les valeurs de la première langue venue
            if ( ( mode == 'read' and readOnlyCurrentLanguage ) or
                   ( mode == 'edit' and editOnlyCurrentLanguage ) ) \
                and not translation \
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
                mDict.update( { mWidget : mWidgetDictTemplate.copy() } )
                mDict[mWidget].update( {
                    'object' : 'translation group' if ( multilingual and translation ) else 'group of values',
                    'main widget type' : 'QGroupBox',
                    'row' : rowidx[mParent],
                    'label' : t.get('label', None) or str(p['name']),
                    'help text' : t.get('help text', None) or ( str(p['descr']) if p['descr'] else None ),
                    'hidden M' : mHideM,
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
                        
            mHelp = ( t.get('help text', None) or ( str(p['descr']) if p['descr'] else None ) ) if (
                        ( mode == 'read' and len(values) <= 1 ) or not (
                        multiple or len(values) > 1 or ( multilingual and translation ) ) ) else None


        # --- BOUCLE SUR LES VALEURS
        
        for mValueBrut in values:
            
            mValue = None
            mCurSource = None
            mVSources = mSources.copy() if mSources is not None else None
            mVHideM = None
            mVLangList = mLangList.copy() if mLangList is not None else None
            mLanguage = ( ( mValueBrut.language if isinstance(mValueBrut, Literal) else None ) or language ) if (
                        mKind == 'sh:Literal' and p['type'].n3(nsm) == 'xsd:string' ) else None
            mNGraphEmpty = mGraphEmpty
            
            # cas d'un noeud vide :
            # on ajoute un groupe et on relance la fonction sur la classe du noeud
            if mKind in ( 'sh:BlankNode', 'sh:BlankNodeOrIRI' ) and (
                    not readHideBlank or not mode == 'read' or isinstance(mValueBrut, BNode) ):

                # cas d'une branche masquée
                if mNHidden and isinstance(mValueBrut, BNode):
                    
                    mNode = mValueBrut
                    mWidget = ( idx[mParent], mParent )
                    mDict.update( { mWidget : mWidgetDictTemplate.copy() } )
                    mDict[mWidget].update( {
                        'object' : 'group of properties',
                        'node kind' : mKind,
                        'class' : p['class'],
                        'path' : mNPath,
                        'subject' : mParentNode,
                        'predicate' : mProperty,
                        'node' : mNode
                        } )
                    idx[mParent] += 1                    
                    idx.update( { mWidget : 0 } )

                # branche visible
                elif not mNHidden:
                
                    mNGraphEmpty = mGraphEmpty or mValueBrut is None              
                    mNode = mValueBrut if isinstance(mValueBrut, BNode) else BNode()

                    if mKind == 'sh:BlankNodeOrIRI':
                        mVSources = ( mVSources + [ "< manuel >" ] ) if mVSources else [ "< URI >", "< manuel >" ]
                        mCurSource = "< manuel >" if isinstance(mValueBrut, BNode) else None
                    
                    # cas d'un double M quand la source "< manuel >" n'est pas sélectionnée
                    # on voudra créer les widgets, mais ils ne seront affichés que si
                    # l'utilisateur bascule sur "< manuel >".
                    mVHideM = mHideM or ( ( mCurSource is None ) if mKind == 'sh:BlankNodeOrIRI' else None )

                    mWidget = ( idx[mParent], mParent, 'M' ) if mKind == 'sh:BlankNodeOrIRI' else ( idx[mParent], mParent )
                    mDict.update( { mWidget : mWidgetDictTemplate.copy() } )
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
                        'subject' : mParentNode,
                        'predicate' : mProperty,
                        'node' : mNode,
                        'multiple sources' : mKind == 'sh:BlankNodeOrIRI' and mode == 'edit',
                        'current source' : mCurSource,
                        'sources' : mVSources,
                        'hidden M' : mVHideM,
                        'shape order' : int(p['order']) if p['order'] is not None else None,
                        'template order' : int(t.get('order')) if t.get('order') is not None else None
                        } )

                    if mKind == 'sh:BlankNode':
                        idx[mParent] += 1
                        rowidx[mParent] += 1
                        
                    idx.update( { mWidget : 0 } )
                    rowidx.update( { mWidget : 0 } )

                if not mNHidden or isinstance(mValueBrut, BNode):              
                    build_dict(
                        metagraph, shape, vocabulary, template=template, templateTabs=templateTabs,
                        data=data, mode=mode, readHideBlank=readHideBlank, hideUnlisted=hideUnlisted,
                        language=language, translation=translation, langList=langList,
                        readOnlyCurrentLanguage=readOnlyCurrentLanguage,
                        editOnlyCurrentLanguage=editOnlyCurrentLanguage,
                        labelLengthLimit=labelLengthLimit, valueLengthLimit=valueLengthLimit,
                        textEditRowSpan=textEditRowSpan, mPath=mNPath, mTargetClass=p['class'],
                        mParentWidget=mWidget,  mParentNode=mNode, mNSManager=mNSManager,
                        mWidgetDictTemplate=mWidgetDictTemplate, mDict=mDict, mGraphEmpty=mNGraphEmpty,
                        mShallowTemplate=mShallowTemplate, mTemplateEmpty=mTemplateEmpty,
                        mHidden=mNHidden, mHideM=mVHideM, mTemplateTabs=mTemplateTabs 
                        )

            # pour tout ce qui n'est pas un pur noeud vide :
            # on ajoute un widget de saisie, en l'initialisant avec
            # une représentation lisible de la valeur
            if not mKind == 'sh:BlankNode' and (
                    not readHideBlank or not mode == 'read' or not isinstance(mValueBrut, BNode) ):
                      
                # cas d'une valeur appartenant à une branche masquée
                # ou d'une traduction dans une langue qui n'est pas
                # supposée être affichée (c'est à dire toute autre
                # langue que celle qui a été demandée ou la langue
                # de substitution fournie par mOneLanguage)
                if mNHidden or ( not translation \
                    and ( ( mode == 'read' and readOnlyCurrentLanguage ) \
                        or ( mode == 'edit' and editOnlyCurrentLanguage ) ) \
                    and isinstance(mValueBrut, Literal) \
                    and not mValueBrut.language in (None, language, mOneLanguage) ):
                
                    if isinstance(mValueBrut, BNode):
                        continue   
                        
                    mDict.update( { ( idx[mParent], mParent ) : mWidgetDictTemplate.copy() } )
                    mDict[ ( idx[mParent], mParent ) ].update( {
                        'object' : 'edit',                      
                        'value' : mValueBrut,                        
                        'language value' : mLanguage,                        
                        'node kind' : mKind,
                        'data type' : p['type'],
                        'class' : p['class'],
                        'path' : mNPath,
                        'subject' : mParentNode,
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
                if isinstance(mValueBrut, URIRef) and mVSources:             
                    mValue, mCurSource = value_from_concept(mValueBrut, vocabulary, language)                   
                    if not mCurSource in mVSources:
                        mCurSource = '< non répertorié >'
                        
                elif mVSources and mGraphEmpty and ( mValueBrut is None ):
                    mCurSource = mDefaultSource

                if mVSources and ( mCurSource is None ):
                # cas où la valeur n'était pas renseignée - ou n'est pas un IRI
                    if "< URI >" in mVSources:
                        # cas où l'utilisateur a le choix entre le mode manuel
                        # et des URI en saisie libre
                        mCurSource = "< URI >"
                    else:
                        mCurSource = '< non répertorié >' if mValueBrut else mVSources[0]

                elif mCurSource == "< manuel >":
                    mCurSource = None               
                

                # cas d'un numéro de téléphone. on transforme
                # l'IRI en quelque chose d'un peu plus lisible
                if mValueBrut and str(p['transform']) == 'phone':
                    mValue = tel_from_owlthing(mValueBrut)

                # cas d'une adresse mél. on transforme
                # l'IRI en quelque chose d'un peu plus lisible
                if mValueBrut and str(p['transform']) == 'email':
                    mValue = email_from_owlthing(mValueBrut)

                mDefault = t.get('default value', None) or mDefaultTrad or ( str(p['default']) if p['default'] else None )
                mValue = mValue or ( str(mValueBrut) if mValueBrut else ( mDefault if mGraphEmpty else None ) )

                mWidgetType = t.get('main widget type', None) or str(p['widget']) or "QLineEdit"
                mDefaultWidgetType = mWidgetType
                
                mLabelRow = None

                if mWidgetType == "QLineEdit" and mValue and ( len(mValue) > valueLengthLimit or mValue.count("\n") > 0 ):
                    mWidgetType = 'QTextEdit'
                
                if mWidgetType == "QComboBox" and ( ( not mVSources ) or '< URI >' in mVSources ):
                    mWidgetType = "QLineEdit"
                    # le schéma SHACL prévoira généralement un QComboBox
                    # pour les URI, mais on est dans un cas où, pour on ne sait quelle
                    # raison, aucun thésaurus n'est disponible. Dans ce cas on affiche
                    # un QLineEdit à la place.
                
                if mLabel and ( mWidgetType == 'QTextEdit' or len(mLabel) > labelLengthLimit ):
                    mLabelRow = rowidx[mParent]
                    rowidx[mParent] += 1
                    
                mRowSpan = ( t.get('row span', None) or ( int(p['rowspan']) if p['rowspan'] else textEditRowSpan ) ) \
                           if mWidgetType == 'QTextEdit' else None

                mDict.update( { ( idx[mParent], mParent ) : mWidgetDictTemplate.copy() } )
                mDict[ ( idx[mParent], mParent ) ].update( {
                    'object' : 'edit',
                    'main widget type' : mWidgetType,
                    'row' : rowidx[mParent],
                    'row span' : mRowSpan,
                    'input mask' : t.get('input mask', None) or ( str(p['mask']) if p['mask'] else None ),
                    'label' : mLabel,
                    'label row' : mLabelRow,
                    'help text' : mHelp,
                    'value' : mValue,
                    'placeholder text' : ( t.get('placeholder text', None) or ( str(p['placeholder']) if p['placeholder'] else mCurSource ) 
                        ) if mWidgetType in ( 'QTextEdit', 'QLineEdit', 'QComboBox' ) else None,
                    'language value' : mLanguage,
                    'is mandatory' : t.get('is mandatory', None) or ( int(p['min']) > 0 if p['min'] else False ),
                    'has minus button' : mode == 'edit' and ( ( multilingual and translation and mVLangList and len(mVLangList) > 1 )
                        or multiple or len(values) > 1 ),
                    'hide minus button' : len(values) <= 1 if ( mode == 'edit' and (
                        ( multilingual and translation and mVLangList and len(mVLangList) > 1 ) or multiple or len(values) > 1 ) ) \
                        else None,
                    'regex validator pattern' : str(p['pattern']) if p['pattern'] else None,
                    'regex validator flags' : str(p['flags']) if p['flags'] else None,
                    'default value' : mDefault,
                    'multiple values' : multiple,
                    'node kind' : mKind,
                    'data type' : p['type'],
                    'class' : p['class'],
                    'path' : mNPath,
                    'subject' : mParentNode,
                    'predicate' : mProperty,
                    'default widget type' : mDefaultWidgetType,
                    'transform' : str(p['transform']) if p['transform'] else None,
                    'type validator' : 'QIntValidator' if p['type'] and p['type'].n3(nsm) == "xsd:integer" else (
                        'QDoubleValidator' if p['type'] and p['type'].n3(nsm) in ("xsd:decimal", "xsd:float", "xsd:double") else None ),
                    'multiple sources' : len(mVSources) > 1 if mVSources and mode == 'edit' else False,
                    'current source' : mCurSource,
                    'sources' : ( mVSources or [] ) + '< non répertorié >' if mCurSource == '< non répertorié >' else mVSources,
                    'one per language' : multilingual and translation,
                    'authorized languages' : sorted(mVLangList) if ( mode == 'edit' and mVLangList ) else None,
                    'read only' : ( mode == 'read' ) or bool(t.get('read only', False)),
                    'hidden M' : mHideM or ( ( mCurSource is None ) if mKind == 'sh:BlankNodeOrIRI' else None ),
                    'shape order' : int(p['order']) if p['order'] is not None else None,
                    'template order' : int(t.get('order')) if t.get('order') is not None else None
                    } )
                
                idx[mParent] += 1
                rowidx[mParent] += ( mRowSpan or 1 )

        # référencement d'un widget bouton pour ajouter une valeur
        # si la catégorie en admet plusieurs
        if not mNHidden and mode == 'edit' and ( ( multilingual and translation and mVLangList and len(mVLangList) > 1 ) or multiple ):
        
            mDict.update( { ( idx[mParent], mParent ) : mWidgetDictTemplate.copy() } )
            mDict[ ( idx[mParent], mParent ) ].update( {
                'object' : 'translation button' if multilingual else 'plus button',
                'main widget type' : 'QToolButton',
                'row' : rowidx[mParent],
                'next child' : idx[mParent] + 1,
                'hidden M' : mHideM,
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

            mParent = mParentWidget

            mType = URIRef( "http://www.w3.org/2001/XMLSchema#" +
                    ( ( t.get('data type', None) ) or "string" ) )

            if not mType.n3(nsm) in ('xsd:string', 'xsd:integer', "xsd:decimal",
                        "xsd:float", "xsd:double", 'xsd:boolean', 'xsd:date',
                        'xsd:time', 'xsd:dateTime', 'xsd:duration'):
                mType = URIRef("http://www.w3.org/2001/XMLSchema#string")

            # on extrait la ou les valeurs éventuellement
            # renseignées dans le graphe pour cette catégorie
            q_gr = metagraph.query(
                """
                SELECT
                    ?value
                WHERE
                     {{ ?n {} ?value . }}
                """.format(meta),
                initBindings = { 'n' : mParentNode }
                )

            values = [ v['value'] for v in q_gr ] if mode == 'read' and readHideBlank else (
                        [ v['value'] for v in q_gr ] or [ t.get('default value', None) if mGraphEmpty else None ] )

            multiple = t.get('multiple values', False)

            if len(values) > 1 or ( multiple and not ( mode == 'read' and readHideBlank ) ):
 
                mWidget = ( idx[mParent], mParent )
                mDict.update( { mWidget : mWidgetDictTemplate.copy() } )
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
                                 ) if mType.n3(nsm) == 'xsd:string' else None
                                 
                mVLangList = ( [ mLanguage ] + ( langList.copy() or [] ) if not mLanguage in ( langList or [] ) \
                            else langList.copy()) if mLanguage and translation else None

                mWidgetType = t.get('main widget type', None) or "QLineEdit"
                mDefaultWidgetType = mWidgetType
                mLabel = ( t.get('label', None) or "???" ) if not ( multiple or len(values) > 1 ) else None
                mLabelRow = None

                if mWidgetType == "QLineEdit" and mValue and ( len(mValue) > valueLengthLimit or mValue.count("\n") > 0 ):
                    mWidgetType = 'QTextEdit'

                if mLabel and ( mWidgetType == 'QTextEdit' or len(mLabel) > labelLengthLimit ):
                    mLabelRow = rowidx[mParent]
                    rowidx[mParent] += 1                

                mRowSpan = t.get('row span', textEditRowSpan) if mWidgetType == 'QTextEdit' else None

                mDict.update( { ( idx[mParent], mParent ) : mWidgetDictTemplate.copy() } )
                mDict[ ( idx[mParent], mParent ) ].update( {
                    'object' : 'edit',
                    'main widget type' : mWidgetType,
                    'row' : rowidx[mParent],
                    'row span' : mRowSpan,
                    'input mask' : t.get('input mask', None),
                    'label' : mLabel,
                    'label row' : mLabelRow,
                    'help text' : t.get('help text', None) if not ( multiple or len(values) > 1 ) else None,
                    'value' : mValue,
                    'placeholder text' : t.get('placeholder text', None) if mWidgetType in ( 'QTextEdit', 'QLineEdit', 'QComboBox' ) else None,
                    'language value' : mLanguage,
                    'is mandatory' : t.get('is mandatory', None),
                    'multiple values' : multiple,
                    'has minus button' : mode == 'edit' and ( multiple or len(values) > 1 ),
                    'hide minus button': len(values) <= 1 if ( mode == 'edit' and ( multiple or len(values) > 1 ) ) else None,
                    'default value' : t.get('default value', None),
                    'node kind' : "sh:Literal",
                    'data type' : mType,
                    'subject' : mParentNode,
                    'predicate' : from_n3(meta, nsm=nsm),
                    'path' : meta,
                    'default widget type' : mDefaultWidgetType,
                    'type validator' : 'QIntValidator' if mType.n3(nsm) == "xsd:integer" else (
                        'QDoubleValidator' if mType.n3(nsm) in ("xsd:decimal", "xsd:float", "xsd:double") else None ),
                    'authorized languages' : sorted(mVLangList) if ( mode == 'edit' and mVLangList ) else None,
                    'read only' : ( mode == 'read' ) or bool(t.get('read only', False)),
                    'template order' : int(t.get('order')) if t.get('order') is not None else None
                    } )
                        
                idx[mParent] += 1
                rowidx[mParent] += ( mRowSpan or 1 )

            if multiple and mode == 'edit':

                mDict.update( { ( idx[mParent], mParent ) : mWidgetDictTemplate.copy() } )
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
    
        n = 0
        l = [k for k in iter_children_keys(mDict, mParentWidget)]
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


    # ---------- METADONNEES NON DEFINIES ----------
    # métadonnées présentes dans le graphe mais ni dans shape ni dans template
    
    if not hideUnlisted and mTargetClass == URIRef("http://www.w3.org/ns/dcat#Dataset"):
        
        q_gr = metagraph.query(
            """
            SELECT
                ?property ?value
            WHERE
                { ?n ?property ?value . 
                  FILTER ( ?property != rdf:type ) }
            """,
            initBindings = { 'n' : mParentNode }
            )
        
        dpv = dict()
        
        for p, v in q_gr:          
            if not p.n3(nsm) in [ d.get('path', None) for d in mDict.values() ]:        
                dpv.update( { p : ( dpv.get(p, []) ) + [ v ] } )

        for p in dpv:

            mParent = mParentWidget
            
            if len(dpv[p]) > 1:

                mWidget = ( idx[mParent], mParent )
                mDict.update( { mWidget : mWidgetDictTemplate.copy() } )
                mDict[mWidget].update( {
                    'object' : 'group of values',
                    'main widget type' : 'QGroupBox',
                    'row' : rowidx[mParent],
                    'label' : "???",
                    'path' : p.n3(nsm)
                    } )

                idx[mParent] += 1
                rowidx[mParent] += 1
                idx.update( { mWidget : 0 } )
                rowidx.update( { mWidget : 0 } )
                mParent = mWidget


            for v in dpv[p]:

                mValue = str(v)
                mWidgetType = 'QTextEdit' if ( len(mValue) > valueLengthLimit or mValue.count("\n") > 0 ) else "QLineEdit"
                mLabelRow = None

                if len(dpv[p]) == 1 and mWidgetType == 'QTextEdit':
                    mLabelRow = rowidx[mParent]
                    rowidx[mParent] += 1

                mType = ( v.datatype if isinstance(v, Literal) else None ) or URIRef("http://www.w3.org/2001/XMLSchema#string")
                # NB : pourrait ne pas être homogène pour toutes les valeurs d'une même catégorie
                
                mLanguage = ( ( v.language if isinstance(v, Literal) else None ) or language 
                            ) if mType.n3(nsm) == 'xsd:string' else None
                            
                mVLangList = ( [ mLanguage ] + ( langList.copy() or [] ) if not mLanguage in ( langList or [] ) else langList.copy() 
                            ) if mLanguage and translation else None

                mDict.update( { ( idx[mParent], mParent ) : mWidgetDictTemplate.copy() } )
                mDict[ ( idx[mParent], mParent ) ].update( {
                    'object' : 'edit',
                    'main widget type' : mWidgetType,
                    'row' : rowidx[mParent],
                    'row span' : textEditRowSpan if mWidgetType == "QTextEdit" else None,
                    'label' : "???" if len(dpv[p]) == 1 else None,
                    'label row' : mLabelRow,
                    'value' : mValue,
                    'language value' : mLanguage,
                    'node kind' : "sh:Literal",
                    'data type' : mType,
                    'multiple values' : False,
                    'has minus button' : ( len(dpv[p]) > 1 and mode == 'edit' ) or False,
                    'hide minus button': False if ( len(dpv[p]) > 1 and mode == 'edit' ) else None,
                    'subject' : mParentNode,
                    'predicate' : p,
                    'path' : p.n3(nsm),
                    'default widget type' : "QLineEdit",
                    'type validator' : 'QIntValidator' if mType.n3(nsm) == "xsd:integer" else (
                        'QDoubleValidator' if mType.n3(nsm) in ("xsd:decimal", "xsd:float", "xsd:double") else None ),
                    'authorized languages' : sorted(mVLangList) if ( mode == 'edit' and mVLangList ) else None,
                    'read only' : ( mode == 'read' )
                    } )
                        
                idx[mParent] += 1
                rowidx[mParent] += 1

            # pas de bouton plus, faute de modèle indiquant si la catégorie
            # admet des valeurs multiples

    return WidgetsDict(mDict)


def update_pg_description(description, metagraph):
    """Return new description with metadata section updated from JSON-LD serialization of metadata graph.

    ARGUMENTS
    ---------
    - metagraph (rdflib.graph.Graph) : un graphe de métadonnées mis à
    jour suite aux actions effectuées par l'utilisateur.
    - description (str) : chaîne de caractères supposée correspondre à la
    description (ou le commentaire) d'un objet PostgreSQL.

    RESULTAT
    --------
    Une chaîne de caractère (str) correspondant à la description mise à jour
    d'après le contenu du graphe.

    Les informations comprises entre les deux balises <METADATA> et </METADATA>
    sont remplacées. Si les balises n'existaient pas, elles sont ajoutées à la
    fin du texte.

    EXEMPLES
    --------
    >>> c = update_pg_description(c, metagraph)
    """

    if len(metagraph) == 0:
        return description
    
    s = metagraph.serialize(format="json-ld")
    # s = metagraph.serialize(format="json-ld").decode("utf-8")
    
    t = re.subn(
        "[<]METADATA[>].*[<][/]METADATA[>]",
        "<METADATA>\n" + s + "\n</METADATA>",
        description,
        flags=re.DOTALL
        )
    # cette expression remplace tout de la première balise <METADATA> à
    # la dernière balise </METADATA> (elle maximise la cible, au contraire
    # de la fonction metagraph_from_pg_description)

    if t[1] == 0:
        return description + "\n\n<METADATA>\n" + s + "\n</METADATA>\n"

    else:
        return t[0]


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

    r = re.match('^([a-z]{1,10})[:][a-z0-9-]{1,25}$', path)
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

    S'il n'y a pas de balises, s'il n'y a rien entre les balises ou si la valeur
    contenue entre les balises est un JSON et pas un JSON-LD, la fonction renvoie
    un graphe vide.

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

    if j is None:

        g = Graph()

    elif j[1]:

        g = Graph().parse(data=j[1], format='json-ld')

    else:
        g = Graph()
  
    for n, u in shape.namespace_manager.namespaces():
            g.namespace_manager.bind(n, u, override=True, replace=True)

    return g


def build_vocabulary(schemeStr, vocabulary, language="fr"):
    """List all concept labels from given scheme.

    ARGUMENTS
    ---------
    - schemeStr (str) : nom de l'ensemble dont on veut lister les concepts.
    - vocabulary (rdflib.graph.Graph) : graphe réunissant le vocabulaire de tous
    les ensembles à considérer.
    - [optionnel] language (str) : langue attendue pour les libellés des concepts.
    schemeStr doit être donné dans cette même langue. Français par défaut.

    RESULTAT
    --------
    Liste (list) contenant les libellés (str) des termes du thésaurus, triés par
    ordre alphabétique selon la locale de l'utilisateur.
    
    Renvoie une liste vide si le thésaurus n'est pas référencé ou s'il n'a aucun
    terme pour la langue considérée.

    EXEMPLES
    --------
    >>> build_vocabulary("Thème de données (UE)", vocabulary)
    ['Agriculture, pêche, sylviculture et alimentation', 'Données provisoires',
    'Économie et finances', 'Éducation, culture et sport', 'Énergie', 'Environnement',
    'Gouvernement et secteur public', 'Justice, système juridique et sécurité publique',
    'Population et société', 'Questions internationales', 'Régions et villes', 'Santé',
    'Science et technologie', 'Transports']
    """
    
    vocabulary.namespace_manager.bind(
        'skos',
        URIRef('http://www.w3.org/2004/02/skos/core#'),
        override=True, replace=True
        )
    
    q_vc = vocabulary.query(
        """
        SELECT
            ?label
        WHERE
            {{ ?c a skos:Concept ;
            skos:inScheme ?s ;
            skos:prefLabel ?label .
            ?s a skos:ConceptScheme ;
                skos:prefLabel ?l .
              FILTER ( lang(?label) = "{}" ) }}
        """.format(language),
        initBindings = { 'l' : Literal(schemeStr, lang=language) }
        )

    if len(q_vc) > 0:

        setlocale(LC_COLLATE, "")

        return sorted(
            [str(l['label']) for l in q_vc],
            key=lambda x: strxfrm(x)
            )
   
    return []


def concept_from_value(conceptStr, schemeStr, vocabulary, language='fr'):
    """Return a skos:Concept IRI matching given label.

    ARGUMENTS
    ---------
    - conceptStr (str) : chaîne de caractères présumée correspondre au libellé d'un
    concept.
    - schemeStr (str) : chaîne de caractères présumée correspondre au libellé de
    l'ensemble qui référence ce concept. Si schemeStr n'est pas spécifié, la fonction
    effectuera la recherche dans tous les ensembles disponibles. En cas de
    correspondance multiple, elle renvoie arbitrairement un des résultats.
    - vocabulary (rdflib.graph.Graph) : graphe réunissant le vocabulaire de tous les
    ensembles à considérer.
    - [optionnel] language (str) : langue présumée de strValue et schemeStr.
    Français par défaut.

    RESULTAT
    --------
    Un tuple formé comme suit :
    [0] est l'IRI du terme (rdflib.term.URIRef).
    [1] est l'IRI de l'ensemble (rdflib.term.URIRef).

    EXEMPLES
    --------
    >>> concept_from_value("Domaine public", "Types de licences (UE)", vocabulary)
    (rdflib.term.URIRef('http://purl.org/adms/licencetype/PublicDomain'), rdflib.term.URIRef('http://purl.org/adms/licencetype/1.1'))
        
    >>> concept_from_value("Transports", None, vocabulary)
    (rdflib.term.URIRef('http://publications.europa.eu/resource/authority/data-theme/TRAN'), rdflib.term.URIRef('http://publications.europa.eu/resource/authority/data-theme'))
    """

    if schemeStr:
        q_vc = vocabulary.query(
            """
            SELECT
                ?concept ?scheme
            WHERE
                { ?concept a skos:Concept ;
                   skos:inScheme ?scheme ;
                   skos:prefLabel ?c .
                   ?scheme a skos:ConceptScheme ;
                   skos:prefLabel ?s . }
            """,
            initBindings = { 'c' : Literal(conceptStr, lang=language),
                            's' : Literal(schemeStr, lang=language) }
            )
         
        for t in q_vc:
            return ( t['concept'], t['scheme'] )
            
    else:
        q_vc = vocabulary.query(
            """
            SELECT
                ?concept ?scheme
            WHERE
                { ?concept a skos:Concept ;
                   skos:inScheme ?scheme ;
                   skos:prefLabel ?c . }
            """,
            initBindings = { 'c' : Literal(conceptStr, lang=language) }
            )
         
        for t in q_vc:
            return t['concept'], t['scheme']
        
    return ( None, None )


def value_from_concept(conceptIRI, vocabulary, language="fr"):
    """Return the skos:prefLabel strings matching given conceptIRI and its scheme.

    ARGUMENTS
    ---------
    - conceptIRI (rdflib.term.URIRef) : objet URIRef présumé correspondre à un
    concept d'ontologie.
    - vocabulary (rdflib.graph.Graph) : graphe réunissant le vocabulaire de tous
    les ensembles à considérer.
    - [optionnel] language (str) : langue attendue pour le libellé résultant.
    Français par défaut.

    RESULTAT
    --------
    Un tuple contenant deux chaînes de caractères :
    [0] est le libellé du concept (str).
    [1] est le nom de l'ensemble (str).
    
    (None, None) si l'IRI n'est pas répertorié.
    
    Si aucune valeur n'est disponible pour la langue spécifiée, la fonction retournera
    la traduction française (si elle existe).
    
    EXEMPLES
    --------
    Dans l'exemple ci-après, il existe une traduction française et anglaise pour le terme
    recherché, mais pas de version espagnole.

    >>> u = URIRef("http://publications.europa.eu/resource/authority/data-theme/TRAN")
    
    >>> value_from_concept(u, vocabulary)
    ('Transports', 'Thèmes de données (UE)')
    
    >>> value_from_concept(u, vocabulary, 'en')
    ('Transport', 'Data theme (EU)')
    
    >>> value_from_concept(u, vocabulary, 'es')
    ('Transports', 'Thèmes de données (UE)')
    """
    
    q_vc = vocabulary.query(
        """
        SELECT
            ?label ?scheme
        WHERE
            {{ ?c a skos:Concept ;
               skos:inScheme ?s ;
               skos:prefLabel ?label .
               ?s a skos:ConceptScheme ;
               skos:prefLabel ?scheme .
               FILTER ((lang(?label) = "{0}") 
                  && (lang(?scheme) = "{0}")) }}
        """.format(language),
        initBindings = { 'c' : conceptIRI }
        )
    
    if len(q_vc) == 0:
        q_vc = vocabulary.query(
        """
        SELECT
            ?label ?scheme
        WHERE
            { ?c a skos:Concept ;
               skos:inScheme ?s ;
               skos:prefLabel ?label .
               ?s a skos:ConceptScheme ;
               skos:prefLabel ?scheme .
               FILTER ((lang(?label) = "fr") 
                  && (lang(?scheme) = "fr")) }
        """,
        initBindings = { 'c' : conceptIRI }
        )
    
    for t in q_vc:
        return ( str( t['label'] ), str( t['scheme'] ) )
        
    return ( None, None )
    

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


def replace_ancestor(key, old_ancestor, new_ancestor):
    """Réécrit la clé key, en remplaçant un de ses ancêtres.
    
    ARGUMENTS
    ---------
    - key (tuple) : clé d'un dictionnaire de widgets (WidgetsDict).
    - old_ancestor (tuple) : clé d'un dictionnaire de widgets
    (WidgetsDict), présumée être une clé ancêtre de key.
    - new_ancestor (tuple) : clé d'un dictionnaire de widgets
    (WidgetsDict) à substituer à old_ancestor.
    
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
    
    if not is_ancestor(old_ancestor, key):
        raise ValueError("Key {} is not {}'s ancestor.".format(old_ancestor, key))
        
    if is_older(old_ancestor, new_ancestor) or is_older(new_ancestor, old_ancestor):
        raise ValueError("Keys {} and {} don't belong to the same generation.".format(
                old_ancestor, new_ancestor))

    if len(new_ancestor) == 3:
        raise ValueError("M keys aren't allowed as ancestor.")

    t = re.sub(re.escape(str(old_ancestor)) + r"([)]*(:?[,]\s[']M['][)]+)?)$", str(new_ancestor) + '\g<1>', str(key))

    return eval(t)
    

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

    if format and not format in (
        "turtle", "json-ld", "xml", "n3", "nt", "pretty-xml", "trig"
        ):
        raise ValueError("Format '{}' is not supported.".format(format))

    for n, u in shape.namespace_manager.namespaces():
            metagraph.namespace_manager.bind(n, u, override=True, replace=True)
    
    # extensions possibles et formats correspondants :
    d = {".ttl": "turtle", ".n3": "n3", ".json": "json-ld",
         ".jsonld": "json-ld", ".xml": "pretty-xml", ".nt": "nt",
         ".rdf": "pretty-xml", ".trig": "trig"}
    dbis = {'turtle': '.ttl', 'n3': '.n3', 'json-ld': '.jsonld',
        'xml': '.rdf', "pretty-xml" : '.rdf', 'nt': '.nt',
       "trig": ".trig"}
    
    # en l'absence de format, si le chemin comporte un
    # suffixe, on tente d'en déduire le format
    if not format and pfile.suffix:
        format = d.get(pfile.suffix)
    if not format:
        format = 'turtle'
    
    # réciproquement, si le nom de fichier n'a pas
    # de suffixe, on en ajoute un d'après le format
    if not pfile.suffix:
        pfile = pfile.with_suffix(dbis.get(format, ''))
    
    s = metagraph.serialize(
        format=format,
        encoding='ascii' if format=='nt' else 'utf-8'
        )
    
    with open(pfile, 'wb') as dest:
        dest.write(s)
    
   
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

    l = ["turtle", "json-ld", "xml", "n3", "nt", "pretty-xml", "trig"]

    # Une méthode plus gourmande pourrait consister à purement et simplement
    # tester toutes les sérialisations possibles et retourner celles qui
    # ne produisent pas d'erreur. À ce stade, il semble cependant que
    # la seule incompatibilité prévisible et admissible soit la
    # combinaison XML + usage d'UUID pour les métadonnées locales. C'est
    # donc uniquement ce cas qui est testé ici.

    for p in metagraph.predicates():
    
        if str(p).startswith('urn:uuid:'):
            for f in ("xml", "pretty-xml"):
                l.remove(f)            
            break
            
        # try:
            # split_uri(p)
        # except:
            # for f in ("xml", "pretty-xml"):
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
    
    # extensions possibles et formats correspondants :
    d = {".ttl": "turtle", ".n3": "n3", ".json": "json-ld",
         ".jsonld": "json-ld", ".xml": "xml", ".nt": "nt",
         ".rdf": "xml", ".trig": "trig"}
    
    if format and not format in ("turtle", "json-ld", "xml",
        "n3", "nt", "trig"):
        raise ValueError("Format '{}' is not supported.".format(format))
    
    if not format:
    
        if not pfile.suffix in d:
            raise TypeError("Couldn't guess RDF format from file extension."\
                            "Please use format to declare it manually.")
                            
        else:
            format = d[pfile.suffix]
            # NB : en théorie, la fonction parse de RDFLib est censée
            # pouvoir reconnaître le format d'après l'extension, mais à
            # ce jour elle n'identifie même pas toute la liste ci-avant.
    
    with pfile.open(encoding='UTF-8') as src:
        g = Graph().parse(data=src.read(), format=format)

    return g
    

def iter_children_keys(widgetdict, key):
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
    >>> for k in iter_children_keys(widgetdict, key):
    ...     [do whatever]
    
    EXEMPLES
    --------
    >>> for k in rdf_utils.iter_children_keys(d, (0,)):
    ...     print(k)
    """
    for k in widgetdict.keys():
        if len(k) > 1 and k[1] == key:
            yield k


def iter_siblings_keys(widgetdict, key, include=False):
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
    >>> for k in iter_siblings_keys(widgetdict, key):
    ...     [do whatever]
    
    EXEMPLES
    --------
    >>> for k in rdf_utils.iter_siblings_keys(d, (0, (0,))):
    ...     print(k)
    """
    if len(key) > 1:
        for k in widgetdict.keys():
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


class ForbiddenOperation(Exception):
    pass

