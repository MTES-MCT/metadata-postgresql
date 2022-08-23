# (c) Didier  LECLERC 2020 CMSIG MTE-MCTRCT/SG/SNUM/UNI/DRC Site de Rouen
# créé sept 2021

from PyQt5 import QtCore, QtGui, QtWidgets, QtSvg
from PyQt5.QtWidgets import (QAction, QMenu , QMenuBar, QApplication, QMessageBox, QFileDialog, QTextEdit, QLineEdit,  QMainWindow, QCompleter, QDateEdit, QDateTimeEdit, QCheckBox, QWidget, QStyleFactory, QStyle, QGridLayout, QSizePolicy) 
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import *
from qgis.gui import *
from qgis.gui import QgsDateTimeEdit
import os
from . import bibli_plume
from .bibli_plume import *
from .bibli_plume_tools_map import *
import psycopg2
from plume.pg import queries
from plume.rdf.utils import wkt_with_srid                  

#==================================================
def generationObjets(self, _keyObjet, _valueObjet) :
    _pathIconsUser = QgsApplication.qgisSettingsDirPath().replace("\\","/") + "plume/icons/buttons"
    _pathIcons = os.path.dirname(__file__) + "/icons/misc"
    _iconSourcesBlank          = _pathIcons + "/blank.svg"
    _pathIcons     = os.path.dirname(__file__) + "/icons/buttons"
    _iconQComboBox             = _pathIcons + "/drop_down_arrow.svg"
    _iconQComboBox    = _iconQComboBox.replace("\\","/")
    _iconSources               = _pathIcons + "/source_button.svg"
    _iconSourcesSelect         = _pathIcons + "/selected_blue.svg"
    _iconSourcesVierge         = _pathIcons + ""
    _iconPlus                  = _pathIcons + "/plus_button.svg"
    _iconComputeButton         = _pathIcons + "/compute_button.svg"
    _iconPlusTempGoProperties  = _pathIconsUser + "/color_button_Plus_GoProperties.svg"
    _iconPlusTempGoValues      = _pathIconsUser + "/color_button_Plus_GoValues.svg"
    _iconPlusTempTgroup        = _pathIconsUser + "/color_button_Plus_Tgroup.svg"
    _iconMinus                 = _pathIcons + "/minus_button.svg"
    _iconMinusTempGoProperties = _pathIconsUser + "/color_button_Minus_GoProperties.svg"
    _iconMinusTempGoValues     = _pathIconsUser + "/color_button_Minus_GoValues.svg"
    _iconMinusTempTgroup       = _pathIconsUser + "/color_button_Minus_Tgroup.svg"
    _iconSourcesGeoButton      = _pathIcons + "/geo_button.svg"
    #-
    _pathIconsgeo = os.path.dirname(__file__) + "/icons/buttons/geo"
    _iconSourcesGeo_bbox_pg       = _pathIconsgeo + "/bbox_pg.svg"
    _iconSourcesGeo_bbox_qgis     = _pathIconsgeo + "/bbox_qgis.svg"
    _iconSourcesGeo_centroid_pg   = _pathIconsgeo + "/centroid_pg.svg"
    _iconSourcesGeo_centroid_qgis = _pathIconsgeo + "/centroid_qgis.svg"
    _iconSourcesGeo_linestring    = _pathIconsgeo + "/linestring.svg"
    _iconSourcesGeo_point         = _pathIconsgeo + "/point.svg"
    _iconSourcesGeo_polygon       = _pathIconsgeo + "/polygon.svg"
    _iconSourcesGeo_rectangle     = _pathIconsgeo + "/rectangle.svg"
    _iconSourcesGeo_circle        = _pathIconsgeo + "/circle.svg"
    _iconSourcesGeo_show          = _pathIconsgeo + "/show.svg"
    _iconSourcesGeo_hide          = _pathIconsgeo + "/hide.svg"
    _dicGeoTools = {  \
                   'hide'         : {'libelle' : 'Visualisation (caché)',                    'icon' : _iconSourcesGeo_show,          'toolTip' :	'Visualisation dans le canevas de la géométrie renseignée dans les métadonnées.'}, \
                   'show'         : {'libelle' : 'Visualisation (affiché)',                  'icon' : _iconSourcesGeo_hide,          'toolTip' :	'Visualisation dans le canevas de la géométrie renseignée dans les métadonnées.'}, \
                   'point'        : {'libelle' : 'Tracé manuel : point',                     'icon' : _iconSourcesGeo_point,         'toolTip' :	'Saisie libre d\'un point dans le canevas.'},                                      \
                   'rectangle'    : {'libelle' : 'Tracé manuel : rectangle',                 'icon' : _iconSourcesGeo_rectangle,     'toolTip' :	'Saisie libre d\'un rectangle dans le canevas.'},                                  \
                   'circle'       : {'libelle' : 'Tracé manuel : cercle',                    'icon' : _iconSourcesGeo_circle,        'toolTip' :	'Saisie libre d\'un cercle dans le canevas.'},                                  \
                   'linestring'   : {'libelle' : 'Tracé manuel : ligne',                     'icon' : _iconSourcesGeo_linestring,    'toolTip' :	'Saisie libre d\'une ligne dans le canevas.\n ** Un clique gauche pour chaque création de point\n ** Un double-clique pour créer le dernier point, et valider votre géométrie de type multiligne'},                                     \
                   'polygon'      : {'libelle' : 'Tracé manuel : polygone',                  'icon' : _iconSourcesGeo_polygon,       'toolTip' :	'Saisie libre d\'un polygone dans le canevas.\n ** Un clique gauche pour chaque création de point\n ** Un double-clique pour créer le dernier point, qui fermera votre polygone avec le premier point, \net validera votre géométrie de type polygone'},                                     \
                   'bboxpg'       : {'libelle' : 'Calcul du rectangle d\'emprise (PostGIS)', 'icon' : _iconSourcesGeo_bbox_pg,       'toolTip' :	'Calcule le rectangle d\'emprise à partir des données. Le calcul est réalisé côté serveur, via les fonctionnalités de PostGIS.'},            \
                   'centroidpg'   : {'libelle' : 'Calcul du centroïde (PostGIS)',            'icon' : _iconSourcesGeo_centroid_pg,   'toolTip' :	'Calcule le centre du rectangle d\'emprise à partir des données. Le calcul est réalisé côté serveur, via les fonctionnalités de PostGIS.'},  \
                   'bboxqgis'     : {'libelle' : 'Calcul du rectangle d\'emprise (Qgis)',    'icon' : _iconSourcesGeo_bbox_qgis,     'toolTip' :	'Calcule le rectangle d\'emprise à partir des données, via les fonctionnalités de Qgis.'},                                                   \
                   'centroidqgis' : {'libelle' : 'Calcul du centroïde (Qgis)',               'icon' : _iconSourcesGeo_centroid_qgis, 'toolTip' :	'Calcule le centre du rectangle d\'emprise à partir des données, via les fonctionnalités de Qgis.'}                                          \
                   }
    self._dicGeoTools = _dicGeoTools
    #-
    _mListeIconsButtonPlusMinus = [ _iconPlusTempGoProperties, _iconPlusTempGoValues,  _iconPlusTempTgroup, \
                                   _iconMinusTempGoProperties, _iconMinusTempGoValues, _iconMinusTempTgroup ]

    #---------------------------
    # Gestion des langues
    _language = self.language
    _langList = self.langList

    #---------------------------
    #Pour Gestion et Génération à la volée des onglets 
    self.mFirst = _valueObjet['object'] == 'tab'
    #---------------------------
    # Gestion du Parent
    if self.mFirst :
       #ICI Gestion et Génération à la volée des onglets 
       _mParentEnCours = gestionOnglets(self, _keyObjet, _valueObjet)
       #- Create button color
       if self.mFirstColor : writeColorIcon(self, _iconPlus, _iconMinus, _mListeIconsButtonPlusMinus)
    else :
       _mParentEnCours = self.mDicObjetsInstancies.parent_grid(_keyObjet)

    #---------------------------
    # == QGROUPBOX
    if _valueObjet['main widget type'] == "QGroupBox" :
       #--                        
       _mObjetGroupBox = QtWidgets.QGroupBox()
       _mObjetGroupBox.setObjectName(str(_mObjetGroupBox))
       #-- 
       #Masqué /Visible Générale                               
       if (_valueObjet['hidden']) : _mObjetGroupBox.setVisible(False)
       #--                        
       _marginTopGroupBox = 10
       _marginLeftGroupBox = 10
       _epaiQGroupBox  = self.epaiQGroupBox
       _colorQGroupBox = self.colorDefaut
       if self.mFirst:
          _epaiQGroupBox  = 0
          _marginTopGroupBox = 0
          _marginLeftGroupBox = 0
       elif _valueObjet['object'] == 'group of properties' :
          _colorQGroupBox = self.colorQGroupBoxGroupOfProperties
       elif _valueObjet['object'] == 'group of values' :
          _colorQGroupBox = self.colorQGroupBoxGroupOfValues
       elif _valueObjet['object'] == 'translation group' :
          _colorQGroupBox = self.colorQGroupBoxTranslationGroup
       _mObjetGroupBox.setStyleSheet("QGroupBox {   \
                              margin-top: " + str(_marginTopGroupBox) + "px; \
                              margin-left: " + str(_marginLeftGroupBox) + "px; \
                              font-family:" + self.policeQGroupBox  +" ; \
                              border-style: " + self.lineQGroupBox  + ";    \
                              border-width:" + str(_epaiQGroupBox)  + "px ; \
                              border-color: " + _colorQGroupBox  +";      \
                              font-weight : bold;         \
                              padding-left:    6px;            \
                              padding-top:    10px;            \
                              padding-right:   6px;            \
                              padding-bottom:  6px;            \
                              }")
       #--
       row, column, rowSpan, columnSpan = self.mDicObjetsInstancies.widget_placement(_keyObjet, 'main widget')
       _mParentEnCours.addWidget(_mObjetGroupBox, row, column, rowSpan, columnSpan, Qt.AlignTop)
       #--                        
       _mObjet = QtWidgets.QGridLayout()
       _mObjet.setContentsMargins(0, 0, 0, 0)
       _mObjetGroupBox.setLayout(_mObjet)
       _mObjet.setObjectName(str(_keyObjet))
       #Title                        
       if not self.mFirst :
          if valueExiste('label', _valueObjet) :_mObjetGroupBox.setTitle(_valueObjet['label']) 
       #Tooltip                        
       if valueExiste('help text', _valueObjet) : _mObjetGroupBox.setToolTip(_valueObjet['help text'])  

       """                              
       #AJOUT 30 JANVIER 2022
       if _valueObjet['object'] in ['group of properties', 'group of values', 'translation group'] :
          _mObjetGroupBox.setContextMenuPolicy(Qt.CustomContextMenu)
          _mObjetGroupBox.customContextMenuRequested.connect(lambda  : self.menuContextuelQGroupBox(_keyObjet, _mObjetGroupBox, QPoint( 15, 15)))
       #AJOUT 30 JANVIER 2022
       """                              

       self.mFirst = False
       #Dict des objets instanciés
       self.mDicObjetsInstancies[_keyObjet].update({'main widget' : _mObjetGroupBox, 'grid widget' : _mObjet})
    # == QGROUPBOX
    #---------------------------
    #---------------------------
    # == QLINEEDIT / QTEXTEDIT / QCOMBOBOX
    elif _valueObjet['main widget type'] in ("QLineEdit", "QTextEdit", "QComboBox") :
       #--
       _editStyle = self.editStyle             #style saisie
       if _valueObjet['main widget type'] == "QLineEdit" :
          _mObjetQSaisie = QtWidgets.QLineEdit()
          _mObjetQSaisie.setStyleSheet("QLineEdit {  font-family:" + self.policeQGroupBox  +"; border-style:" + _editStyle  +" ; border-width: 0px;}")
       elif _valueObjet['main widget type'] == "QTextEdit" :
          _mObjetQSaisie = QtWidgets.QTextEdit()
          _mObjetQSaisie.setStyleSheet("QTextEdit {  font-family:" + self.policeQGroupBox  +"; border-style:" + _editStyle  +" ; border-width: 0px;}")
       elif _valueObjet['main widget type'] == "QComboBox" :
          _mObjetQSaisie = QtWidgets.QComboBox()
          _mObjetQSaisie.setStyleSheet("QComboBox {  font-family:" + self.policeQGroupBox  +"; border-style:" + _editStyle  + " ; border-width: 0px;} \
                                        QComboBox::drop-down {border: 0px;}\
                                        QComboBox::down-arrow {image: url(" + _iconQComboBox + ");position:absolute; left : 5px;width: 12px;height: 45px;}") 
       _mObjetQSaisie.setObjectName(str(_keyObjet))
       #--                        
       #Masqué /Visible Générale                               
       if (_valueObjet['hidden']) : _mObjetQSaisie.setVisible(False)
       #--                        
       row, column, rowSpan, columnSpan = self.mDicObjetsInstancies.widget_placement(_keyObjet, 'main widget') 
       _mParentEnCours.addWidget(_mObjetQSaisie, row, column, rowSpan, columnSpan, Qt.AlignTop)
       #--                        
       if _valueObjet['main widget type'] in ("QTextEdit") :
          _mObjetQSaisie.setMinimumSize(QtCore.QSize(100, 15 * rowSpan)) # Pour obtenir des QTexEdit suffisament haut
       else :             
          _mObjetQSaisie.setMinimumSize(QtCore.QSize(100, 23))

       if _valueObjet['main widget type'] in ("QLineEdit") :
          #Valeur 
          bibli_plume.updateObjetWithValue(_mObjetQSaisie, _valueObjet)  #Mets à jour la valeur de l'objet en fonction de son type                       
       elif _valueObjet['main widget type'] in ("QTextEdit") :
          #Valeur  
          _mObjetQSaisie.setAcceptRichText(True)                      
          bibli_plume.updateObjetWithValue(_mObjetQSaisie, _valueObjet)  #Mets à jour la valeur de l'objet en fonction de son type                       

       if _valueObjet['main widget type'] in ("QLineEdit", "QTextEdit") :
          #Lecture seule                        
          _mObjetQSaisie.setEnabled(False if _valueObjet['read only'] else True)
          #Masque valeur fictive                        
          if valueExiste('placeholder text', _valueObjet) : _mObjetQSaisie.setPlaceholderText(_valueObjet['placeholder text'])                                
          #Masque                         
          if valueExiste('input mask', _valueObjet)       : _mObjetQSaisie.setInputMask(_valueObjet['input mask'])
           
       #Tooltip                        
       if valueExiste('help text', _valueObjet)        : _mObjetQSaisie.setToolTip(_valueObjet['help text'])
       #Validateur                        
       if _valueObjet['type validator'] != None :
          mTypeValidator = _valueObjet['type validator']
          if mTypeValidator == 'QIntValidator':
             _mObjetQSaisie.setValidator(QIntValidator(_mObjetQSaisie))
          elif mTypeValidator == 'QDoubleValidator':
             _mObjetQSaisie.setValidator(QDoubleValidator(_mObjetQSaisie))
       #Mandatory                        
       if valueExiste('is mandatory', _valueObjet) : _mObjetQSaisie.setProperty("mandatoryField", True if _valueObjet['is mandatory'] else False)
       #QRegularExpression                        
       if _valueObjet['regex validator pattern'] != None :
          re = QRegularExpression(_valueObjet['regex validator pattern'])
          if _valueObjet['regex validator flags']:
              if "i" in _valueObjet['regex validator flags']:
                 re.setPatternOptions(QRegularExpression.CaseInsensitiveOption)
              if "s" in _valueObjet['regex validator flags']:
                 re.setPatternOptions(QRegularExpression.DotMatchesEverythingOption)
              if "m" in _valueObjet['regex validator flags']:
                 re.setPatternOptions(QRegularExpression.MultilineOption)
              if "x" in _valueObjet['regex validator flags']:
                 re.setPatternOptions(QRegularExpression.ExtendedPatternSyntaxOption)
          _mObjetQSaisie.setValidator(QRegularExpressionValidator(re, _mObjetQSaisie))
       
       #========== 
       #QCOMBOBOX 
       if _valueObjet['main widget type'] in ("QComboBox") :
          _thesaurus = _valueObjet['thesaurus values']                                                           
          if _thesaurus != None : _mObjetQSaisie.addItems(_thesaurus)
          bibli_plume.updateObjetWithValue(_mObjetQSaisie, _valueObjet)  #Mets à jour la valeur de l'objet en fonction de son type                       
          _mObjetQSaisie.setEditable(True)
          #-
          mCompleter = QCompleter(_thesaurus, self)
          mCompleter.setCaseSensitivity(Qt.CaseInsensitive)
          #mCompleter.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
          _mObjetQSaisie.setCompleter(mCompleter)
       #==========
                                          
       #Dict des objets instanciés
       self.mDicObjetsInstancies[_keyObjet].update({'main widget' : _mObjetQSaisie})
    # == QLINEEDIT / QTEXTEDIT / QCOMBOBOX
    #---------------------------
    #---------------------------
    # == QLABEL
    elif _valueObjet['main widget type'] in ("QLabel") :
       #--                        
       _editStyle = self.editStyle             #style saisie
       _mObjetQLabel = QtWidgets.QLabel()
       _mObjetQLabel.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; border-style:" + _editStyle  +" ; border-width: 0px;}")
       _mObjetQLabel.setObjectName(str(_keyObjet))
       _mObjetQLabel.setTextInteractionFlags(Qt.TextSelectableByMouse) # for select text"
       #Masqué /Visible Générale                               
       if (_valueObjet['hidden']) : _mObjetQLabel.setVisible(False)
       #--                        
       row, column, rowSpan, columnSpan = self.mDicObjetsInstancies.widget_placement(_keyObjet, 'main widget')
       _mParentEnCours.addWidget(_mObjetQLabel, row, column, rowSpan, columnSpan, Qt.AlignTop)
       #Valeur                        
       bibli_plume.updateObjetWithValue(_mObjetQLabel, _valueObjet)  #Mets à jour la valeur de l'objet en fonction de son type                       
       #Tooltip                        
       if valueExiste('help text', _valueObjet) : _mObjetQLabel.setToolTip(_valueObjet['help text'])
       #--                        
       _mObjetQLabel.setWordWrap(True)
       _mObjetQLabel.setOpenExternalLinks(True)

       """ GESTION DES ESPACES A FAIRE
       if valueExiste('help text', _valueObjet) : 
          if _valueObjet['help text'].find("Date et heure") != -1 :
             print([ _mObjetQLabel, _valueObjet ])       
       #_mObjetQLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
       GESTION DES ESPACES A FAIRE """


       #Dict des objets instanciés
       self.mDicObjetsInstancies[_keyObjet].update({'main widget' : _mObjetQLabel})
    # == QLABEL
    #---------------------------
    #---------------------------
    # == QDATEEDIT
    elif _valueObjet['main widget type'] == "QDateEdit" :
       #--                        
       _editStyle = self.editStyle             #style saisie
       _mObjetQDateEdit = QgsDateTimeEdit()
       #Masqué /Visible Générale                               
       if (_valueObjet['hidden']) : _mObjetQDateEdit.setVisible(False)
       #--
       _mObjetQDateEdit.setStyleSheet("QgsDateTimeEdit {  font-family:" + self.policeQGroupBox  +"; border-style:" + _editStyle  + " ; border-width: 0px;} \
                                       QgsDateTimeEdit::drop-down {border: 0px;}\
                                       QgsDateTimeEdit::down-arrow {image: url(" + _iconQComboBox + ");position:absolute; left : 5px;width: 12px;height: 45px;}") 
       _width  = _mObjetQDateEdit.width()
       _mObjetQDateEdit.setMinimumSize(QtCore.QSize(_width, 23))

       _mObjetQDateEdit.setObjectName(str(_keyObjet))
       _displayFormat = 'dd/MM/yyyy'
       _mObjetQDateEdit.setDisplayFormat(_displayFormat)
       _mObjetQDateEdit.setMinimumWidth(112)
       _mObjetQDateEdit.setMaximumWidth(112)
       _mObjetQDateEdit.setCalendarPopup(True)
        #--                        
       row, column, rowSpan, columnSpan = self.mDicObjetsInstancies.widget_placement(_keyObjet, 'main widget')
       _mParentEnCours.addWidget(_mObjetQDateEdit, row, column, rowSpan, columnSpan, Qt.AlignTop)
        #Valeur 
       if valueExiste('value', _valueObjet) :
           bibli_plume.updateObjetWithValue(_mObjetQDateEdit, _valueObjet)  #Mets à jour la valeur de l'objet en fonction de son type                       
       else :
           _mObjetQDateEdit.clear()
           bibli_plume.updateObjetWithValue(_mObjetQDateEdit, _valueObjet)  #Mets à jour la valeur de l'objet en fonction de son type                       
       #Lecture seule                        
       _mObjetQDateEdit.setEnabled(False if _valueObjet['read only'] else True)
       #Masque valeur fictive                        
       if valueExiste('placeholder text', _valueObjet) : _mObjetQDateEdit.setPlaceholderText(_valueObjet['placeholder text'])                                
       #Tooltip                        
       if valueExiste('help text', _valueObjet)        : _mObjetQDateEdit.setToolTip(_valueObjet['help text'])
                                          
       #Dict des objets instanciés
       self.mDicObjetsInstancies[_keyObjet].update({'main widget' : _mObjetQDateEdit})
    # == QDATEEDIT
    #---------------------------
    #---------------------------
    # == QCHECKBOX
    elif _valueObjet['main widget type'] == "QCheckBox" :
       #--                        
       _mObjetQCheckBox = QCheckBox()
       #Masqué /Visible Générale                               
       if (_valueObjet['hidden']) : _mObjetQCheckBox.setVisible(False)
       #--                        
       _mObjetQCheckBox.setStyleSheet("QCheckBox {  font-family:" + self.policeQGroupBox  +"; }")
       _mObjetQCheckBox.setObjectName(str(_keyObjet))
       #--                        
       row, column, rowSpan, columnSpan = self.mDicObjetsInstancies.widget_placement(_keyObjet, 'main widget')
       _mParentEnCours.addWidget(_mObjetQCheckBox, row, column, rowSpan, columnSpan)

       #-- Trois états                        
       _mObjetQCheckBox.setTristate(True)
       bibli_plume.updateObjetWithValue(_mObjetQCheckBox, _valueObjet)  #Mets à jour la valeur de l'objet en fonction de son type                       

       #Lecture seule                        
       _mObjetQCheckBox.setEnabled(False if _valueObjet['read only'] else True)
       #Masque valeur fictive                        
       if valueExiste('placeholder text', _valueObjet) : _mObjetQCheckBox.setPlaceholderText(_valueObjet['placeholder text'])                                
       #Tooltip                        
       if valueExiste('help text', _valueObjet)        : _mObjetQCheckBox.setToolTip(_valueObjet['help text'])
                                          
       #Dict des objets instanciés
       self.mDicObjetsInstancies[_keyObjet].update({'main widget' : _mObjetQCheckBox})
    # == QCHECKBOX
    #---------------------------
    #---------------------------
    # == QDATETIMEEDIT
    elif _valueObjet['main widget type'] == "QDateTimeEdit" :
       #--                        
       _editStyle = self.editStyle             #style saisie
       _mObjetQDateTime = QgsDateTimeEdit()
       #Masqué /Visible Générale                               
       if (_valueObjet['hidden']) : _mObjetQDateTime.setVisible(False)
       #--                        
       _mObjetQDateTime.setStyleSheet("QgsDateTimeEdit {  font-family:" + self.policeQGroupBox  +"; border-style:" + _editStyle  + " ; border-width: 0px;} \
                                       QgsDateTimeEdit::drop-down {border: 0px;}\
                                       QgsDateTimeEdit::down-arrow {image: url(" + _iconQComboBox + ");position:absolute; left : 5px;width: 12px;height: 45px;}") 
       _width  = _mObjetQDateTime.width()
       _mObjetQDateTime.setMinimumSize(QtCore.QSize(_width, 23))

       _mObjetQDateTime.setObjectName(str(_keyObjet))
       _displayFormat = 'dd/MM/yyyy hh:mm:ss'
       _mObjetQDateTime.setDisplayFormat(_displayFormat)
       _mObjetQDateTime.setMinimumWidth(130)
       _mObjetQDateTime.setMaximumWidth(130)
       #_mObjetQDateTime.setCalendarPopup(True)
       #--                        
       row, column, rowSpan, columnSpan = self.mDicObjetsInstancies.widget_placement(_keyObjet, 'main widget')
       _mParentEnCours.addWidget(_mObjetQDateTime, row, column, rowSpan, columnSpan, Qt.AlignLeft)
       #Valeur
       if valueExiste('value', _valueObjet) :  
          bibli_plume.updateObjetWithValue(_mObjetQDateTime, _valueObjet)  #Mets à jour la valeur de l'objet en fonction de son type                       
       else :
          _mObjetQDateTime.clear()
          bibli_plume.updateObjetWithValue(_mObjetQDateTime, _valueObjet)  #Mets à jour la valeur de l'objet en fonction de son type                       
       #Lecture seule                        
       _mObjetQDateTime.setEnabled(False if _valueObjet['read only'] else True)
       #Masque valeur fictive                        
       if valueExiste('placeholder text', _valueObjet) : _mObjetQDateTime.setPlaceholderText(_valueObjet['placeholder text'])                                
       #Tooltip                        
       if valueExiste('help text', _valueObjet)        : _mObjetQDateTime.setToolTip(_valueObjet['help text'])
                                          
       #Dict des objets instanciés
       self.mDicObjetsInstancies[_keyObjet].update({'main widget' : _mObjetQDateTime})
    # == QDATETIMEEDIT
    #---------------------------
    #---------------------------
    # == QTIMEEDIT
    elif _valueObjet['main widget type'] == "QTimeEdit" :
       #--                        
       _editStyle = self.editStyle             #style saisie
       _mObjetQTime = QgsDateTimeEdit()
       #Masqué /Visible Générale                               
       if (_valueObjet['hidden']) : _mObjetQTime.setVisible(False)
       #--                        
       _mObjetQTime.setStyleSheet("QgsDateTimeEdit {  font-family:" + self.policeQGroupBox  +"; border-style:" + _editStyle  + " ; border-width: 0px;} \
                                   QgsDateTimeEdit::drop-down {border: 0px;}\
                                   QgsDateTimeEdit::down-arrow {image: url(" + _iconQComboBox + ");position:absolute; left : 5px;width: 12px;height: 45px;}") 
       _width  = _mObjetQTime.width()
       _mObjetQTime.setMinimumSize(QtCore.QSize(_width, 23))

       _mObjetQTime.setObjectName(str(_keyObjet))
       _displayFormat = 'hh:mm:ss'
       _mObjetQTime.setDisplayFormat(_displayFormat)
       _mObjetQTime.setMinimumWidth(130)
       _mObjetQTime.setMaximumWidth(130)
       #--                        
       row, column, rowSpan, columnSpan = self.mDicObjetsInstancies.widget_placement(_keyObjet, 'main widget')
       _mParentEnCours.addWidget(_mObjetQTime, row, column, rowSpan, columnSpan, Qt.AlignLeft)
       #Valeur
       if valueExiste('value', _valueObjet) :  
          bibli_plume.updateObjetWithValue(_mObjetQTime, _valueObjet)  #  Mets à jour la valeur de l'objet en fonction de son type                       
       else :
          _mObjetQTime.clear()
          bibli_plume.updateObjetWithValue(_mObjetQTime, _valueObjet)  #  Mets à jour la valeur de l'objet en fonction de son type                       
       #Lecture seule                        
       _mObjetQTime.setEnabled(False if _valueObjet['read only'] else True)
       #Masque valeur fictive                        
       if valueExiste('placeholder text', _valueObjet) : _mObjetQTime.setPlaceholderText(_valueObjet['placeholder text'])                                
       #Tooltip                        
       if valueExiste('help text', _valueObjet)        : _mObjetQTime.setToolTip(_valueObjet['help text'])
                                          
       #Dict des objets instanciés
       self.mDicObjetsInstancies[_keyObjet].update({'main widget' : _mObjetQTime})
    # == QTIMEEDIT
    #---------------------------

    #---------------------------
    # == QTOOLBUTTON   Button PLUS et Button TRADUCTION et Button UNITES
    elif _valueObjet['main widget type'] in ("QToolButton") :
       #--
       _editStyle = self.editStyle             #style saisie
       _mObjetQToolButton = QtWidgets.QToolButton()
       _mObjetQToolButton.setObjectName(str(_keyObjet))
       _mObjetQToolButton.setStyleSheet("QToolButton {  font-family:" + self.policeQGroupBox  +";}")
       """
       if _valueObjet['object'] == "translation button" : 
          #_mObjetQToolButton.setStyleSheet("QToolButton { font-family:" + self.policeQGroupBox  +"; border-style:" + _editStyle  +" ; border: none;}")
          #_mObjetQToolButton.setPopupMode(_mObjetQToolButton.InstantPopup)  
          #_mObjetQToolButton.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
       elif _valueObjet['object'] == "plus button" :
          # == QICON  
          _mObjetQToolButton.setIcon(QIcon(  changeColorIcon(self, _keyObjet, "buttonPlus", _mListeIconsButtonPlusMinus)  ))
       """
       # == QICON
       _mObjetQToolButton.setIcon(QIcon(  changeColorIcon(self, _keyObjet, "buttonPlus", _mListeIconsButtonPlusMinus)  ))
       _mObjetQToolButton.setAutoRaise(True)
              
       #- Actions
       _mObjetQToolButton.clicked.connect(lambda : action_mObjetQToolButton_Plus_translation(self, _keyObjet, _valueObjet, _language, _langList))
       #--                        
       #Masqué /Visible Générale                               
       if (_valueObjet['hidden']) : _mObjetQToolButton.setVisible(False)
       #--                        
       row, column, rowSpan, columnSpan = self.mDicObjetsInstancies.widget_placement(_keyObjet, 'main widget')
       _mParentEnCours.addWidget(_mObjetQToolButton, row, column, rowSpan, columnSpan)
       #Tooltip                        
       if valueExiste('help text', _valueObjet)        : _mObjetQToolButton.setToolTip(_valueObjet['help text'])
       #Dict des objets instanciés
       self.mDicObjetsInstancies[_keyObjet].update({'main widget'  : _mObjetQToolButton}) 
    # == QTOOLBUTTON   Button PLUS et Button TRADUCTION
    #---------------------------
    else :
       pass

    #=============================================================================
    # Changement d'itération !!
    #=============================================================================

    # == QLABEL
    _mObjetQLabelEtiquette = generationLabel(self, _keyObjet, _valueObjet, _mParentEnCours)
    # == QLABEL
    #---------------------------
    #---------------------------
    # == QTOOLBUTTON   COMPUTE BUTTON  Métadonnées calculées
    if _valueObjet['has compute button'] :
       #--
       _mObjetQToolButton = QtWidgets.QToolButton()
       _mObjetQToolButton.setObjectName(str(_keyObjet))
       _mObjetQToolButton.setAutoRaise(True)

       # == QICON
       _mObjetQToolButton.setIcon(QIcon(_iconComputeButton ))
       # == QICON
              
       #- Actions
       _mObjetQToolButton.clicked.connect(lambda : action_mObjetQToolButton_ComputeButton_with_safe_pg_connection(self, _keyObjet, _valueObjet))
       #--                        
       row, column, rowSpan, columnSpan = self.mDicObjetsInstancies.widget_placement(_keyObjet, 'compute widget')
       _mParentEnCours.addWidget(_mObjetQToolButton, row, column, rowSpan, columnSpan)
       #Tooltip 
       _help_text = self.mDicObjetsInstancies[_keyObjet]['compute method'].description                       
       _mObjetQToolButton.setToolTip(_help_text)
       #Masqué /Visible Générale                               
       if (_valueObjet['hidden']) : _mObjetQToolButton.setVisible(False)

       #Dict des objets instanciés
       self.mDicObjetsInstancies[_keyObjet].update({'compute widget' : _mObjetQToolButton})
    # == QTOOLBUTTON   COMPUTE BUTTON
    #---------------------------

    #---------------------------
    # == QTOOLBUTTON   Button MOINS
    if _valueObjet['has minus button'] :
       #--
       _mObjetQToolButton = QtWidgets.QToolButton()
       _mObjetQToolButton.setObjectName(str(_keyObjet))
       _mObjetQToolButton.setAutoRaise(True)

       # == QICON
       _mObjetQToolButton.setIcon(QIcon(changeColorIcon(self, _keyObjet, "buttonMinus", _mListeIconsButtonPlusMinus )))
       # == QICON
              
       #- Actions
       _mObjetQToolButton.clicked.connect(lambda : action_mObjetQToolButton_Minus(self, _keyObjet, _valueObjet, _language, _langList))
       #--                        
       #--                        
       row, column, rowSpan, columnSpan = self.mDicObjetsInstancies.widget_placement(_keyObjet, 'minus widget')
       _mParentEnCours.addWidget(_mObjetQToolButton, row, column, rowSpan, columnSpan)
       #Tooltip                        
       _mObjetQToolButton.setToolTip(QtWidgets.QApplication.translate("bibli_gene_objet", "Delete item"))
       #Masqué /Visible Générale                               
       if _valueObjet['hide minus button'] : _mObjetQToolButton.setVisible(False)
       if (_valueObjet['hidden']) : _mObjetQToolButton.setVisible(False)

       #Dict des objets instanciés
       self.mDicObjetsInstancies[_keyObjet].update({'minus widget'  : _mObjetQToolButton}) 
    # == QTOOLBUTTON   Button MOINS
    #---------------------------

    #---------------------------
    # == QTOOLBUTTON  MULTIPLE SOURCES
    if _valueObjet['multiple sources'] :
       _editStyle = self.editStyle             #style saisie
       #--
       _mObjetQToolButton = QtWidgets.QToolButton()
       _mObjetQToolButton.setObjectName(str(_keyObjet))
       _mObjetQToolButton.setIcon(QIcon(_iconSources))
       #_mObjetQToolButton.setStyleSheet("QToolButton { font-family:" + self.policeQGroupBox  +"; border: none;}")
       _mObjetQToolButton.setAutoRaise(True)
       
       #MenuQToolButton                        
       _mObjetQMenu = QMenu()
       _mObjetQMenu.setStyleSheet("QMenu {  font-family:" + self.policeQGroupBox  +"; border-style:" + _editStyle  +" ; border-width: 0px;}")
       #------------
       _mListActions = []
       for elemQMenuItem in _valueObjet['sources'] :
           if elemQMenuItem == _valueObjet['current source'] : 
              _mObjetQMenuIcon = QIcon(_iconSourcesSelect)
           else :                 
              _mObjetQMenuIcon = QIcon(_iconSourcesVierge)
              
           _mObjetQMenuItem = QAction(elemQMenuItem, _mObjetQMenu)
           _mObjetQMenuItem.setText(elemQMenuItem)
           _mObjetQMenuItem.setObjectName(str(elemQMenuItem))
           _mObjetQMenuItem.setIcon(_mObjetQMenuIcon)
           _mObjetQMenu.addAction(_mObjetQMenuItem)
           #- Actions
           _mObjetQMenuItem.triggered.connect(lambda : action_mObjetQToolButton(self, _keyObjet, _valueObjet, _iconSources, _iconSourcesSelect, _iconSourcesVierge, _language))
           _mListActions.append(_mObjetQMenuItem)
       
       _mObjetQToolButton.setPopupMode(_mObjetQToolButton.InstantPopup)
       _mObjetQToolButton.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
       _mObjetQToolButton.setMenu(_mObjetQMenu)
       #--                        
       #Masqué /Visible Générale                               
       if (_valueObjet['hidden']) : _mObjetQToolButton.setVisible(False)
       #--                        
       row, column, rowSpan, columnSpan = self.mDicObjetsInstancies.widget_placement(_keyObjet, 'switch source widget')
       _mParentEnCours.addWidget(_mObjetQToolButton, row, column, rowSpan, columnSpan)
       #Tooltip                        
       if valueExiste('help text', _valueObjet)        : _mObjetQToolButton.setToolTip(_valueObjet['help text'])
                                          
       #Dict des objets instanciés
       self.mDicObjetsInstancies[_keyObjet].update({'switch source widget'  : _mObjetQToolButton,
                                                    'switch source menu'    : _mObjetQMenu,
                                                    'switch source actions' : _mListActions}) 
       #apparence_mObjetQToolButton(self, _keyObjet, _iconSources, _valueObjet['current source'])
    # == QTOOLBUTTON  MULTIPLE SOURCES
    #---------------------------

    #---------------------------
    # == QTOOLBUTTON  AUTHORIZED LANGUAGES
    if _valueObjet['authorized languages'] :
       _editStyle = self.editStyle             #style saisie
       #--
       _mObjetQToolButton = QtWidgets.QToolButton()
       _mObjetQToolButton.setObjectName(str(_keyObjet))
       _mObjetQToolButton.setText(_valueObjet['language value'])
       _mObjetQToolButton.setStyleSheet("QToolButton {  font-family:" + self.policeQGroupBox  +";}")
       _mObjetQToolButton.setIcon(QIcon(_iconSourcesBlank))
       h = _mObjetQToolButton.iconSize().height()
       _mObjetQToolButton.setIconSize(QSize(1, h))
       #_mObjetQToolButton.setStyleSheet("QToolButton { font-family:" + self.policeQGroupBox  +"; width:2.5em; border-style:" + _editStyle  + "; border : none;}")  
       _mObjetQToolButton.setAutoRaise(True)

       #MenuQToolButton                        
       _mObjetQMenu = QMenu()
       _mObjetQMenu.setStyleSheet("QMenu {  font-family:" + self.policeQGroupBox  +"; border-style:" + _editStyle  + "}")
       #------------
       _mListActions = []
       for elemQMenuItem in _valueObjet['authorized languages'] :
           _mObjetQMenuItem = QAction(elemQMenuItem, _mObjetQMenu)
           _mObjetQMenuItem.setText(elemQMenuItem)
           if elemQMenuItem == _valueObjet['language value'] : _mObjetQMenuItem.setIcon(QIcon(_iconSourcesSelect))
           _mObjetQMenuItem.setObjectName(str(elemQMenuItem))
           _mObjetQMenu.addAction(_mObjetQMenuItem)
           #- Actions
           _mObjetQMenuItem.triggered.connect(lambda : action_mObjetQToolButtonAuthorizesLanguages(self, _keyObjet, _valueObjet, _language, _langList, _iconSourcesSelect))
           _mListActions.append(_mObjetQMenuItem)
       
       _mObjetQToolButton.setPopupMode(_mObjetQToolButton.InstantPopup)
       _mObjetQToolButton.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
       _mObjetQToolButton.setMenu(_mObjetQMenu)
       #--                        
       #Masqué /Visible Générale                               
       if (_valueObjet['hidden']) : _mObjetQToolButton.setVisible(False)
       #--                        
       row, column, rowSpan, columnSpan = self.mDicObjetsInstancies.widget_placement(_keyObjet, 'language widget')
       _mParentEnCours.addWidget(_mObjetQToolButton, row, column, rowSpan, columnSpan)
       #Tooltip                        
       _mObjetQToolButton.setToolTip(QtWidgets.QApplication.translate("bibli_gene_objet", "Metadata language selection"))
                                          
       #Dict des objets instanciés
       self.mDicObjetsInstancies[_keyObjet].update({'language widget'  : _mObjetQToolButton, 
                                                    'language menu'    : _mObjetQMenu,
                                                    'language actions' : _mListActions}) 
       #apparence_mObjetQToolButton(self, _keyObjet, _iconSources, _valueObjet['current source'])
    # == QTOOLBUTTON  AUTHORIZED LANGUAGES
    #---------------------------

    #---------------------------
    # == QTOOLBUTTON  UNITS
    if _valueObjet['units'] :
       _editStyle = self.editStyle             #style saisie
       #--
       _mObjetQToolButton = QtWidgets.QToolButton()
       _mObjetQToolButton.setAutoRaise(True)
       _mObjetQToolButton.setObjectName(str(_keyObjet))
       _mObjetQToolButton.setText(_valueObjet['current unit'])
       _mObjetQToolButton.setStyleSheet("QToolButton {  font-family:" + self.policeQGroupBox  +";}")
       _mObjetQToolButton.setIcon(QIcon(_iconSourcesBlank))
       h = _mObjetQToolButton.iconSize().height()
       _mObjetQToolButton.setIconSize(QSize(1, h))
       #MenuQToolButton                        
       _mObjetQMenu = QMenu()
       _mObjetQMenu.setStyleSheet("QMenu {  font-family:" + self.policeQGroupBox  +"; border-style:" + _editStyle  + "; border-width: 0px;}")
       #------------
       _mListActions = []
       for elemQMenuItem in _valueObjet['units'] :
           _mObjetQMenuItem = QAction(elemQMenuItem, _mObjetQMenu)
           _mObjetQMenuItem.setText(elemQMenuItem)
           if elemQMenuItem == _valueObjet['current unit'] : _mObjetQMenuItem.setIcon(QIcon(_iconSourcesSelect))
           _mObjetQMenuItem.setObjectName(str(elemQMenuItem))
           _mObjetQMenu.addAction(_mObjetQMenuItem)
           #- Actions
           _mObjetQMenuItem.triggered.connect(lambda : action_mObjetQToolButtonUnits(self, _keyObjet, _valueObjet, _iconSourcesSelect))
           _mListActions.append(_mObjetQMenuItem)
       
       _mObjetQToolButton.setPopupMode(_mObjetQToolButton.InstantPopup)
       _mObjetQToolButton.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
       _mObjetQToolButton.setMenu(_mObjetQMenu)
       #--                        
       #Masqué /Visible Générale                               
       if (_valueObjet['hidden']) : _mObjetQToolButton.setVisible(False)
       #--                        
       row, column, rowSpan, columnSpan = self.mDicObjetsInstancies.widget_placement(_keyObjet, 'unit widget')
       _mParentEnCours.addWidget(_mObjetQToolButton, row, column, rowSpan, columnSpan)
       #Tooltip                        
       _mObjetQToolButton.setToolTip(QtWidgets.QApplication.translate("bibli_gene_objet", "Unit of measurement selection"))  
                                          
       #Dict des objets instanciés
       self.mDicObjetsInstancies[_keyObjet].update({'unit widget'  : _mObjetQToolButton, 
                                                    'unit menu'    : _mObjetQMenu,
                                                    'unit actions' : _mListActions}) 
    # == QTOOLBUTTON  UNITS
    #---------------------------

    #---------------------------
    # == QTOOLBUTTON  GEO TOOLS
    if _valueObjet['geo tools'] :
       _editStyle = self.editStyle             #style saisie
       #--
       _mObjetQToolButton = QtWidgets.QToolButton()
       _mObjetQToolButton.setObjectName(str(_keyObjet))
       self.dic_geoToolsShow[_keyObjet] = False  # Param for display BBOX ou no
       _mObjetQToolButton.setAutoRaise(True)
       _mObjetQToolButton.setCheckable(True)

       #---------------------------
       # Visualisation mode read
       if _valueObjet['geo tools'] == ['show'] :
          majVisuButton(self, self, _mObjetQToolButton, self.dic_geoToolsShow, _keyObjet, _valueObjet) 
          _mObjetQToolButton.clicked.connect(lambda : action_mObjetQToolButtonGeoToolsShow(self, _mObjetQToolButton, _keyObjet, _valueObjet))
       #---------------------------
       # Visualisation mode edit
       else :
          #MenuQToolButton                        
          _mObjetQToolButton.setPopupMode(_mObjetQToolButton.DelayedPopup)       # InstantPopup  MenuButtonPopup DelayedPopup
          _mObjetQToolButton.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
          
          _mObjetQMenu = QMenu()
          majVisuButton(self, self, _mObjetQToolButton, self.dic_geoToolsShow, _keyObjet, _valueObjet) 
          _mObjetQMenu.setStyleSheet("QMenu {  font-family:" + self.policeQGroupBox  +"; width:250px; border-style:" + _editStyle  + "; border-width: 0px;}")
          _mObjetQToolButton.clicked.connect(lambda : action_mObjetQToolButtonGeoToolsShow(self, _mObjetQToolButton, _keyObjet, _valueObjet))
          _mObjetQMenu.setToolTipsVisible(True)
          #------------
          _mListActions = []
          #Attention substitution on enlève show
          _valueObjet_geo_tools = [ elem for elem in _valueObjet['geo tools'] if elem != 'show' ] 
          for elemQMenuItem in _valueObjet_geo_tools :
              elemQMenuItemForBboxCentroid = elemQMenuItem
              #--
              if elemQMenuItem in ['bbox','centroid'] :
                 #Tjs QGIS
                 if self.layer.wkbType() != QgsWkbTypes.NoGeometry :  
                    elemQMenuItem = elemQMenuItemForBboxCentroid + "qgis"
                    _mObjetQMenuItem = QAction(elemQMenuItem, _mObjetQMenu)
                    _mObjetQMenuItem.setText(_dicGeoTools[elemQMenuItem]['libelle'])
                    _mObjetQMenuItem.setObjectName(str(elemQMenuItem))
                    _mObjetQMenuItem.setIcon(QIcon(_dicGeoTools[elemQMenuItem]['icon']))
                    _mObjetQMenu.addAction(_mObjetQMenuItem)
                    _mObjetQMenuItem.setToolTip(_dicGeoTools[elemQMenuItem]['toolTip'])
                    #- Actions
                    _mObjetQMenuItem.triggered.connect(lambda : action_mObjetQToolButtonGeoTools(self, _mObjetQToolButton, _keyObjet, _valueObjet))
                    _mListActions.append(_mObjetQMenuItem)
                    #Seulement si Postgis Installée
                    if self.postgis_exists :
                       elemQMenuItem = elemQMenuItemForBboxCentroid + "pg"  
                       _mObjetQMenuItem = QAction(elemQMenuItem, _mObjetQMenu)
                       _mObjetQMenuItem.setText(_dicGeoTools[elemQMenuItem]['libelle'])
                       _mObjetQMenuItem.setObjectName(str(elemQMenuItem))
                       _mObjetQMenuItem.setIcon(QIcon(_dicGeoTools[elemQMenuItem]['icon']))
                       _mObjetQMenu.addAction(_mObjetQMenuItem)
                       _mObjetQMenuItem.setToolTip(_dicGeoTools[elemQMenuItem]['toolTip'])
                       #- Actions
                       _mObjetQMenuItem.triggered.connect(lambda : action_mObjetQToolButtonGeoTools(self, _mObjetQToolButton, _keyObjet, _valueObjet))
                       _mListActions.append(_mObjetQMenuItem)
              #--
              else :
                 _mObjetQMenuItem = QAction(elemQMenuItem, _mObjetQMenu)
                 _mObjetQMenuItem.setText(_dicGeoTools[elemQMenuItem]['libelle'])
                 _mObjetQMenuItem.setObjectName(str(elemQMenuItem))
                 _mObjetQMenuItem.setIcon(QIcon(_dicGeoTools[elemQMenuItem]['icon']))
                 _mObjetQMenu.addAction(_mObjetQMenuItem)
                 _mObjetQMenuItem.setToolTip(_dicGeoTools[elemQMenuItem]['toolTip'])
                 #- Actions
                 _mObjetQMenuItem.triggered.connect(lambda : action_mObjetQToolButtonGeoTools(self, _mObjetQToolButton,_keyObjet, _valueObjet))
                 _mListActions.append(_mObjetQMenuItem)

          _mObjetQToolButton.setMenu(_mObjetQMenu)
          #Dict des objets instanciés
          self.mDicObjetsInstancies[_keyObjet].update({'geo widget'  : _mObjetQToolButton, 
                                                       'geo menu'    : _mObjetQMenu,
                                                       'geo actions' : _mListActions}) 
       #---------------------------
       #Masqué /Visible Générale                                           
       if (_valueObjet['hidden']) : _mObjetQToolButton.setVisible(False)
       #--                                 
       row, column, rowSpan, columnSpan = self.mDicObjetsInstancies.widget_placement(_keyObjet, 'geo widget')
       _mParentEnCours.addWidget(_mObjetQToolButton, row, column, rowSpan, columnSpan)
       
    # == QTOOLBUTTON  GEO TOOLS
    #---------------------------
    return  

#==================================================
# Traitement action sur QToolButton avec COMPUTE BUTTON
def action_mObjetQToolButton_ComputeButton_with_safe_pg_connection(self, __keyObjet, __valueObjet, beforeAfter = None) :
    # == Gestion Context ==
    with self.safe_pg_connection() :
       action_mObjetQToolButton_ComputeButton(self, __keyObjet, __valueObjet, beforeAfter)
    return
    
#==================================================
# Traitement action sur QToolButton avec COMPUTE BUTTON
def action_mObjetQToolButton_ComputeButton(self, __keyObjet, __valueObjet, beforeAfter = None):
    # existence extensions 
    dependances = self.mDicObjetsInstancies[__keyObjet]['compute method'].dependances
    _messDependances = ""
    dependances_ok = True

    if dependances:
       for extension in dependances :
          mKeySql = queries.query_exists_extension(extension)
          r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self.mConnectEnCours, mKeySql, optionRetour = "fetchone")
          dependances_ok = dependances_ok and r
          if not dependances_ok:
             _messDependances = extension
             zTitre = QtWidgets.QApplication.translate("plume_ui", "PLUME : Warning", None)
             zMess  = QtWidgets.QApplication.translate("plume_ui", "Au minimum, absence de l'extension : ", None) +  + _messDependances
             bibli_plume.displayMess(self.Dialog, (2 if self.Dialog.displayMessage else 1), zTitre, zMess, Qgis.Warning, self.Dialog.durationBarInfo)
             break

    # existence extensions
    if dependances_ok :
       mKeySql = (self.mDicObjetsInstancies.computing_query(__keyObjet, self.schema, self.table))
       result , zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self.mConnectEnCours, mKeySql, optionRetour = "fetchall")
       ret = self.mDicObjetsInstancies.computing_update(__keyObjet, result)
       if beforeAfter != "BEFORE" :
          #---------------------------------------------
          #- regénération et matérialisation en fonction de la structure du dictionnaire
          regenerationStructureMaterialisation(self, ret, __keyObjet, __valueObjet)
    return  

#==================================================
# Traitement action sur QToolButton Geo Visualisation
def action_mObjetQToolButtonGeoToolsShow(self, __mObjetQToolButton, __keyObjet, __valueObjet):
    # If suppression d'une couche active pour les métadonnées affichées
    if not bibli_plume.gestionErreurExisteLegendeInterface(self) : return
    # If suppression d'une couche active pour les métadonnées affichées

    #Supprime si l'objet existe et desactive le process QgsMapTool
    try : 
       for k, v in self.dic_objetMap.items() :
          try : 
             qgis.utils.iface.mapCanvas().unsetMapTool(self.dic_objetMap[k])
          except :
             pass        
    except :
       pass        
    #Supprime si l'objet existe et desactive le process QgsMapTool
 
    _selectItem = __mObjetQToolButton.sender()

    self.dic_geoToolsShow[__keyObjet] = False if self.dic_geoToolsShow[__keyObjet] else True  # Param for display BBOX ou no
    majVisuButton(self, self, __mObjetQToolButton, self.dic_geoToolsShow, __keyObjet, __valueObjet) 

    mCoordSaisie  = self.mDicObjetsInstancies[__keyObjet]['main widget'].text() if self.mDicObjetsInstancies[__keyObjet]['main widget type'] == "QLabel" else (self.mDicObjetsInstancies[__keyObjet]['main widget'].toPlainText() if self.mDicObjetsInstancies[__keyObjet]['main widget type'] == "QTextEdit" else self.mDicObjetsInstancies[__keyObjet]['main widget'].text())
    mCanvas       = qgis.utils.iface.mapCanvas()
    mAuthid       = mCanvas.mapSettings().destinationCrs().authid()
    
    if self.dic_geoToolsShow[__keyObjet] : 
       self.dic_objetMap[__keyObjet] = GeometryMapToolShow(self, __keyObjet, mCanvas, mAuthid, mCoordSaisie, self.dic_geoToolsShow[__keyObjet])
    else :
       #if not create rubberBand res = None
       eraseRubberBand(self, self.dic_objetMap, __keyObjet)
    
    #Rafraichissement du Canvas   
    mCanvas.redrawAllLayers()
    return  

#==================================================
# Traitement action sur QToolButton Geo Actions
def action_mObjetQToolButtonGeoTools(self, __mObjetQToolButton, __keyObjet, __valueObjet):
    # == Gestion Context ==
    with self.safe_pg_connection() :
       # If suppression d'une couche active pour les métadonnées affichées
       if not bibli_plume.gestionErreurExisteLegendeInterface(self) : return
       # If suppression d'une couche active pour les métadonnées affichées

       _selectItem = self.mDicObjetsInstancies[__keyObjet]['geo menu'].sender()
       self.dic_geoToolsShow[__keyObjet] = False  # Param for display BBOX ou no
       #-
       for k, v in self._dicGeoTools.items() :
           if _selectItem.text() == self._dicGeoTools[k]['libelle'] :
              mAction = k
              break 
       #-
       mCanvas      = qgis.utils.iface.mapCanvas()
       srid         = mCanvas.mapSettings().destinationCrs().authid()
       mObjet       = self.mDicObjetsInstancies[__keyObjet]['main widget']
       #-

       majVisuButton(self, self, __mObjetQToolButton, self.dic_geoToolsShow, __keyObjet, __valueObjet) 
       eraseRubberBand(self, self.dic_objetMap, __keyObjet)
    
       if mAction in ["rectangle", "point", "polygon", "linestring", "circle"] : 
          self.dic_objetMap[__keyObjet] = GeometryMapTool(self, mAction, __mObjetQToolButton, __keyObjet, mCanvas, srid, self.dic_geoToolsShow[__keyObjet])
          qgis.utils.iface.mapCanvas().setMapTool(self.dic_objetMap[__keyObjet])
       elif mAction in ["bboxpg",] :
          mKeySql = queries.query_get_geom_srid(self.schema, self.table, self.geom)
          srid, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self.mConnectEnCours, mKeySql, optionRetour = "fetchone")
          #-
          mKeySql = queries.query_get_geom_extent(self.schema, self.table, self.geom)
          geom_wkt, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self.mConnectEnCours, mKeySql, optionRetour = "fetchone")
          try : 
             geom_wkt = QgsGeometry.fromWkt(geom_wkt).asWkt(self.Dialog.geomPrecision)
          except :
             pass
       elif mAction in ["centroidpg",] : 
          mKeySql = queries.query_get_geom_srid(self.schema, self.table, self.geom)
          srid, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self.mConnectEnCours, mKeySql, optionRetour = "fetchone")
          #-
          mKeySql = queries.query_get_geom_centroid(self.schema, self.table, self.geom)
          geom_wkt, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self.mConnectEnCours, mKeySql, optionRetour = "fetchone")
          try : 
             geom_wkt = QgsGeometry.fromWkt(geom_wkt).asWkt(self.Dialog.geomPrecision)
          except :
             pass
       elif mAction in ["bboxqgis",] :
          srid     = self.layer.crs().authid()  # Attention Chgt de srid pour Qgis, on prend la couche active
          geom_wkt = QgsGeometry.fromRect(self.layer.extent()).asWkt(self.Dialog.geomPrecision)
       elif mAction in ["centroidqgis",] : 
          srid     = self.layer.crs().authid()  # Attention Chgt de srid pour Qgis, on prend la couche active
          geom_wkt = QgsGeometry.fromPointXY(self.layer.extent().center()).asWkt(self.Dialog.geomPrecision)
       #------
       if mAction in ["bboxpg", "centroidpg", "bboxqgis", "centroidqgis"] :
          rdf_wkt = wkt_with_srid(geom_wkt, srid)
          mObjet.setPlainText(rdf_wkt)
    return  

#==================================================
# Traitement action sur QToolButton avec Menu UNITS
def action_mObjetQToolButtonUnits(self, __keyObjet, __valueObjet, _iconSourcesSelect):
    _selectItem = self.mDicObjetsInstancies[__keyObjet]['unit menu'].sender()
    #maj Source 
    ret = self.mDicObjetsInstancies.change_unit(__keyObjet,  _selectItem.text() )
    #- regénération et matérialisation en fonction de la structure du dictionnaire
    regenerationStructureMaterialisation(self, ret, __keyObjet, __valueObjet, None, None, _iconSourcesSelect = _iconSourcesSelect)
    return  

#==================================================
# Traitement action sur QToolButton avec Menu AUTHORIZED LANGUAGES
def action_mObjetQToolButtonAuthorizesLanguages(self, __keyObjet, __valueObjet, _language, _langList, _iconSourcesSelect):
    _selectItem = self.mDicObjetsInstancies[__keyObjet]['language menu'].sender()
    #maj Source 
    ret = self.mDicObjetsInstancies.change_language(__keyObjet,  _selectItem.text() )

    #- regénération et matérialisation en fonction de la structure du dictionnaire
    regenerationStructureMaterialisation(self, ret, __keyObjet, __valueObjet, _language = _language, _langList = _langList, _iconSourcesSelect = _iconSourcesSelect)
    #maj apparence QToolButton 
    #apparence_mObjetQToolButton(self, __keyObjet, _iconSources, _selectItem.text())
    return  

#==================================================
# Traitement action sur QToolButton Moins
def action_mObjetQToolButton_Minus(self, __keyObjet, __valueObjet, _language, _langList):
    #Mise à jour du dictionnaire des widgets 
    ret = self.mDicObjetsInstancies.drop(__keyObjet)

    #- regénération et matérialisation en fonction de la structure du dictionnaire
    regenerationStructureMaterialisation(self, ret, __keyObjet, __valueObjet, _language = _language, _langList = _langList)
    return  

#==================================================
# Traitement action sur QToolButton Plus et Translation
def action_mObjetQToolButton_Plus_translation(self, __keyObjet, __valueObjet, _language, _langList):
    #Mise à jour du dictionnaire des widgets 
    ret = self.mDicObjetsInstancies.add(__keyObjet)
    
    #- regénération et matérialisation en fonction de la structure du dictionnaire
    regenerationStructureMaterialisation(self, ret, __keyObjet, __valueObjet, _language = _language, _langList = _langList)
    return

#==================================================
# Traitement action sur QToolButton avec Menu
def action_mObjetQToolButton(self, __keyObjet, __valueObjet, _iconSources, _iconSourcesSelect, _iconSourcesVierge, _language):
    _selectItem = self.mDicObjetsInstancies[__keyObjet]['switch source menu'].sender()
    #maj Source 
    ret = self.mDicObjetsInstancies.change_source(__keyObjet, _selectItem.text() )

    #- regénération et matérialisation en fonction de la structure du dictionnaire
    regenerationStructureMaterialisation(self, ret, __keyObjet, __valueObjet, _language = _language, _selectItem = _selectItem, _iconSources = _iconSources, _iconSourcesSelect = _iconSourcesSelect, _iconSourcesVierge = _iconSourcesVierge)
    return  

#==================================================
# Traitement pour la structuration des dictionnaires contenant les informations de matérialisation
# Les dictionnaires renvoyés par les méthodes d'actions de la classe plume.rdf.widgetsdict.WidgetsDict présentent une structure fixe,
# indépendante de la méthode exécutée. Ainsi, il est possible (et certainement préférable) de prévoir 
# des mécanismes de matérialisation eux-mêmes indépendants de la nature de l'action initialement effectuée par l'utilisateur.
def regenerationStructureMaterialisation(self, _ret, __keyObjet, __valueObjet, _language = None, _langList = None, _selectItem = None, _iconSources = None, _iconSourcesSelect = None, _iconSourcesVierge = None) :
    #- Nouveaux objets à créer avec les nouvelles clefs          
    for key in _ret['new keys'] :
        mParent, self.mFirst = self.mDicObjetsInstancies.parent_grid(key), False
        self.mFirst = False
        value = self.mDicObjetsInstancies[key]
        if value['main widget type'] != None :
           generationObjets(self, key, value)
        else :
           pass
    #- Afficher          
    for elem in _ret['widgets to show'] : 
        elem.setVisible(True)
    #- Masquer          
    for elem in _ret['widgets to hide'] : 
        elem.setVisible(False)
    #- Supprimer Widget        
    for elem in _ret['widgets to delete'] :
        self.mDicObjetsInstancies.parent_grid(__keyObjet).removeWidget(elem)
        elem.deleteLater()
    #- Supprimer QGridLayout        
    for elem in _ret['grids to delete'] :
        self.mDicObjetsInstancies.parent_grid(__keyObjet).removeItem(elem)
        elem.deleteLater()
    #- Supprimer Actions        
    for elem in _ret['actions to delete'] :
        elem.deleteLater()
    #- Supprimer Menu        
    for elem in _ret['menus to delete'] :
        elem.deleteLater()
    #---------------------------------------------
    #- Regénération du Menu Languages, Sources, Translation, Moins, Plus
    if _ret['language menu to update'] != "" : regenerationMenu(self, _ret['language menu to update'], _language, _langList, _iconSourcesSelect)
    #---------------------------------------------        
    #- Regénération du Menu des QToolButton 
    if  _ret['switch source menu to update'] != "" : regenerationMenuQToolButton(self, _ret['switch source menu to update'], _language, _selectItem, _iconSources, _iconSourcesSelect, _iconSourcesVierge)
    #---------------------------------------------
    #- Regénération du Menu Unit 
    if  _ret['unit menu to update'] != "" : regenerationMenuUnit(self, _ret['unit menu to update'], _iconSourcesSelect)
    #---------------------------------------------
    #- Maj QComboBox
    for elem in _ret['concepts list to update'] : 
        __valueObjet = self.mDicObjetsInstancies[elem]
        _thesaurus = __valueObjet['thesaurus values']
        __valueObjet['main widget'].clear()
        __valueObjet['main widget'].addItems(_thesaurus)
    #- Déplacer 
    for elem in _ret['widgets to move'] :
        elem[0].removeWidget(elem[1])
        #-- 
        elem[0].addWidget(elem[1], elem[2], elem[3], elem[4], elem[5])
    #- Maj de la valeur          
    for elem in _ret['value to update'] :
        __valueObjet = self.mDicObjetsInstancies[elem]
        bibli_plume.updateObjetWithValue(__valueObjet['main widget'], __valueObjet)  #Mets à jour la valeur de l'objet en fonction de son type                       
    return

#==================================================
# Traitement Regénération du menu Unités avec la clé "unit menu to update" 
# Pour le moment ne fait que mettre à jour le texte, en attente si utilisation nécessaire de la clé "unit menu to update")
def regenerationMenuUnit(self, _ret, _iconSourcesSelect) :
    mListeKeyQMenuUpdate = _ret

    for mKeyQMenuUpdate in mListeKeyQMenuUpdate :
       #Nouveau __valueObjet en fonction nouvelle clef                        
       __valueObjet  = self.mDicObjetsInstancies[mKeyQMenuUpdate]     
       __valueObjet['unit widget'].setText(__valueObjet['current unit'])  
       #MenuQToolButton                        
       _mObjetQMenu = __valueObjet['unit menu']
       #------------
       for elemQMenuItem in _mObjetQMenu.children() :
           if elemQMenuItem.text() == __valueObjet['current unit'] : 
              _mObjetQMenuIcon = QIcon(_iconSourcesSelect)
           else :                 
              _mObjetQMenuIcon = QIcon("")
           elemQMenuItem.setIcon(_mObjetQMenuIcon)
    return

#==================================================
# Traitement Regénération du menu des QToolButton 
def regenerationMenuQToolButton(self, _ret, _language, _selectItem, _iconSources, _iconSourcesSelect, _iconSourcesVierge) :
    #---------------------------------------------
    #- Regénération du Menu 
    mListeKeyQMenuUpdate = _ret 
    
    for mKeyQMenuUpdate in mListeKeyQMenuUpdate : 
       #Nouveau __valueObjet en fonction nouvelle clef                        
       __valueObjet  = self.mDicObjetsInstancies[mKeyQMenuUpdate]     
       #MenuQToolButton                        
       for act in __valueObjet['switch source menu'].actions() :
           __valueObjet['switch source menu'].removeAction(act)
       #--    
       _mObjetQMenu = __valueObjet['switch source menu']
       _mObjetQMenu.setStyleSheet("QMenu {  font-family:" + self.policeQGroupBox  +"; border-style:" + self.editStyle  + ";}")
       #------------
       _mListActions = []
       for elemQMenuItem in __valueObjet['sources'] :
           _mObjetQMenuItem = QAction(elemQMenuItem, _mObjetQMenu)
           _mObjetQMenuItem.setObjectName(str(elemQMenuItem))

           if elemQMenuItem == _selectItem.text() : 
              _mObjetQMenuIcon = QIcon(_iconSourcesSelect)
           else :                 
              _mObjetQMenuIcon = QIcon(_iconSourcesVierge)
           _mObjetQMenuItem.setText(elemQMenuItem)
           _mObjetQMenuItem.setIcon(_mObjetQMenuIcon)

           _mObjetQMenu.addAction(_mObjetQMenuItem)
           #- Actions
           _mObjetQMenuItem.triggered.connect(lambda : action_mObjetQToolButton(self, mKeyQMenuUpdate, __valueObjet, _iconSources, _iconSourcesSelect, _iconSourcesVierge, _language))
           _mListActions.append(_mObjetQMenuItem)
    
       #__valueObjet['switch source widget'].setPopupMode(__valueObjet['switch source widget'].MenuButtonPopup)
       #__valueObjet['switch source widget'].setStyleSheet("QToolButton { font-family:" + self.policeQGroupBox  +"; border-style:" + self.editStyle  +" ; border: none;}")
       __valueObjet['switch source widget'].setPopupMode(__valueObjet['switch source widget'].InstantPopup)
       __valueObjet['switch source widget'].setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
       __valueObjet['switch source widget'].setAutoRaise(True)
       __valueObjet['switch source widget'].setMenu(_mObjetQMenu)

       #Dict des objets instanciés
       __valueObjet.update({'switch source actions' : _mListActions}) 

    #maj apparence QToolButton 
    #apparence_mObjetQToolButton(self, __keyObjet, _iconSources, _selectItem.text())
    return

#==================================================
# Traitement Regénération du menu avec la clé "language menu to update" 
# contient une liste de clés du dictionnaire de widgets (et non directement des widgets),
# pour lesquelles le menu des langues doit être régénéré
def regenerationMenu(self, _ret, _language, _langList, _iconSourcesSelect) :
    # pour infos    _ret = ret['language menu to update']
    mListeKeyQMenuUpdate = _ret
    
    for mKeyQMenuUpdate in mListeKeyQMenuUpdate :
       #Nouveau __valueObjet en fonction nouvelle clef                        
       __valueObjet  = self.mDicObjetsInstancies[mKeyQMenuUpdate]     
       __valueObjet['language widget'].setText(__valueObjet['language value'])  
       #MenuQToolButton                        
       for act in __valueObjet['language menu'].actions() :
           __valueObjet['language menu'].removeAction(act)
       #--    
       _mObjetQMenu = __valueObjet['language menu']
       #------------
       _mListActions = []

       for elemQMenuItem in __valueObjet['authorized languages'] :
           _mObjetQMenuItem = QAction(elemQMenuItem, _mObjetQMenu)
           _mObjetQMenuItem.setText(elemQMenuItem)
           if elemQMenuItem == __valueObjet['language value'] : _mObjetQMenuItem.setIcon(QIcon(_iconSourcesSelect))
           _mObjetQMenuItem.setObjectName(str(elemQMenuItem))
           _mObjetQMenu.addAction(_mObjetQMenuItem)
           #- Actions
           _mObjetQMenuItem.triggered.connect(lambda : action_mObjetQToolButtonAuthorizesLanguages(self, mKeyQMenuUpdate, __valueObjet, _language, _langList, _iconSourcesSelect))
           _mListActions.append(_mObjetQMenuItem)
    
       __valueObjet['language widget'].setPopupMode(__valueObjet['language widget'].InstantPopup)
       __valueObjet['language widget'].setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
       __valueObjet['language widget'].setAutoRaise(True)
       __valueObjet['language widget'].setMenu(_mObjetQMenu)

       #Dict des objets instanciés
       __valueObjet.update({'language actions' : _mListActions}) 
    return

#==========================
def gestionOnglets(self, _key, _value):
    #--------------------------
    tab_widget_Onglet = QWidget()
    tab_widget_Onglet.setObjectName(str(_key))
    labelTabOnglet = str(_value['label'])
    self.tabWidget.addTab(tab_widget_Onglet, labelTabOnglet)
    #==========================     
    #Zone affichage Widgets
    zoneWidgetsGroupBox = QtWidgets.QGroupBox(tab_widget_Onglet)
    zoneWidgetsGroupBox.setStyleSheet("QGroupBox {   \
                font-family: Serif ;   \
                border-style: outset;    \
                border-width: 0px;       \
                border-radius: 10px;     \
                border-color: green;      \
                font-weight : bold;     \
                padding-top: 6px;        \
                }")
    #Zone affichage du modèle
    self.modeleEnCours = QtWidgets.QLabel(zoneWidgetsGroupBox)
    self.modeleEnCours.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; border-style:" + self.editStyle  +" ; border-width: 0px;}")
    self.modeleEnCours.setObjectName("modeleEnCours")
    self.modeleEnCours.setText("Mon modèle en cours qui va bien")
    self.modeleEnCours.setGeometry(QtCore.QRect(10, 0, tab_widget_Onglet.width(), 20))
    #Zone affichage du modèle
    self.modeleEnCours.setVisible(False)

    x, y = 0, 0
    larg, haut =  self.tabWidget.width()- 5, self.tabWidget.height()-5
    zoneWidgetsGroupBox.setGeometry(QtCore.QRect(x, y, larg, haut))
    #--            
    zoneWidgets = QtWidgets.QGridLayout()
    zoneWidgets.setContentsMargins(0, 0, 0, 0) 
    zoneWidgetsGroupBox.setLayout(zoneWidgets )
    zoneWidgets.setObjectName("zoneWidgets" + str(_key))
    #--            
    scroll_bar = QtWidgets.QScrollArea(tab_widget_Onglet) 
    scroll_bar.setStyleSheet("QScrollArea { border: 0px solid red;}")
    scroll_bar.setWidgetResizable(True)
    scroll_bar.setGeometry(QtCore.QRect(x, y, larg, haut))
    scroll_bar.setMinimumWidth(50)
    scroll_bar.setWidget(zoneWidgetsGroupBox)
    #--  
    #For resizeIhm 
    self.listeResizeIhm.append(zoneWidgetsGroupBox)             
    self.listeResizeIhm.append(scroll_bar)             
    return zoneWidgets

#==================================================
# write Color Button SVG
def writeColorIcon(self, __iconPlus, __iconMinus, __mListeIconsButtonPlusMinus) :
    with open(__iconPlus,'r') as myTempFile :
       _mTempFile = ""
       for elem in myTempFile.readlines() :
           _mTempFile += elem
       # -    
       mIcon = _mTempFile.format(fill=self.colorQGroupBoxGroupOfProperties)
       with open(__mListeIconsButtonPlusMinus[0],'w') as myTempFile :
            myTempFile.write(mIcon)
       # -    
       mIcon = _mTempFile.format(fill=self.colorQGroupBoxGroupOfValues)
       with open(__mListeIconsButtonPlusMinus[1],'w') as myTempFile :
            myTempFile.write(mIcon)
       # -    
       mIcon = _mTempFile.format(fill=self.colorQGroupBoxTranslationGroup)
       with open(__mListeIconsButtonPlusMinus[2],'w') as myTempFile :
            myTempFile.write(mIcon)
    with open(__iconMinus,'r') as myTempFile :
       _mTempFile = ""
       for elem in myTempFile.readlines() :
           _mTempFile += elem
       # -    
       mIcon = _mTempFile.format(fill=self.colorQGroupBoxGroupOfProperties)
       with open(__mListeIconsButtonPlusMinus[3],'w') as myTempFile :
            myTempFile.write(mIcon)
       # -    
       mIcon = _mTempFile.format(fill=self.colorQGroupBoxGroupOfValues)
       with open(__mListeIconsButtonPlusMinus[4],'w') as myTempFile :
            myTempFile.write(mIcon)
       # -    
       mIcon = _mTempFile.format(fill=self.colorQGroupBoxTranslationGroup)
       with open(__mListeIconsButtonPlusMinus[5],'w') as myTempFile :
            myTempFile.write(mIcon)
    return 

#==================================================
# Change Color Button SVG
def changeColorIcon(self, __keyObjet, _buttonPlusMinus, listIconTemp) :
    if self.mDicObjetsInstancies.group_kind(__keyObjet) == 'group of properties' :
       __iconTemp = listIconTemp[0] if _buttonPlusMinus == "buttonPlus" else listIconTemp[3]        
    elif self.mDicObjetsInstancies.group_kind(__keyObjet) == 'group of values' :          
       __iconTemp = listIconTemp[1] if _buttonPlusMinus == "buttonPlus" else listIconTemp[4]          
    elif self.mDicObjetsInstancies.group_kind(__keyObjet) == 'translation group' :          
       __iconTemp = listIconTemp[2] if _buttonPlusMinus == "buttonPlus" else listIconTemp[5]          
    #-                
    return __iconTemp

#==================================================
# Apparence action sur QToolButton
def apparence_mObjetQToolButton(self, __keyObjet, __iconSources, __Text):
    _mToolButton = self.mDicObjetsInstancies[__keyObjet]['switch source widget']
    _mToolButton.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
    _mActionDefaut = QAction()
    _mActionDefaut.setIcon(QIcon(__iconSources));
    _mActionDefaut.setText(__Text)
    _mToolButton.setDefaultAction(_mActionDefaut);
    return  
      
#==================================================
# Génération des QLabel
def generationLabel(self, __keyObjet, __valueObjet, __mParentEnCours) :
    __mObjetQLabelEtiquette = None
    # == QLABEL
    if __valueObjet['has label'] :
       _labelBackGround  = self.labelBackGround   #Fond Qlabel
       #--                        
       __mObjetQLabelEtiquette = QtWidgets.QLabel()
       __mObjetQLabelEtiquette.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + _labelBackGround  +";}")
       __mObjetQLabelEtiquette.setObjectName("label_" + str(__keyObjet))
       #Masqué /Visible Générale                               
       if (__valueObjet['hidden']) : __mObjetQLabelEtiquette.setVisible(False)
       #--                        
       row, column, rowSpan, columnSpan = self.mDicObjetsInstancies.widget_placement(__keyObjet, 'label widget')
       __mParentEnCours.addWidget(__mObjetQLabelEtiquette, row, column, rowSpan, columnSpan)
       #Valeur                        
       __mObjetQLabelEtiquette.setText(__valueObjet['label']) 
       self.mDicObjetsInstancies[__keyObjet].update({'label widget' : __mObjetQLabelEtiquette})
       __mObjetQLabelEtiquette.setMaximumSize(QtCore.QSize(self.tabWidget.width(), 18))
       #Tooltip                        
       if valueExiste('help text', __valueObjet) : __mObjetQLabelEtiquette.setToolTip(__valueObjet['help text'])
    # == QLABEL
    
    return __mObjetQLabelEtiquette

#==================================================
# Retourne si la valeur n'est pas nulle ou égale à "" : Clé et dictionnaire des widgets
def valueExiste(_var, _dict) :
    _ret = False
    if _dict[_var] == None :
       _ret = False
    elif _dict[_var] == "" :
       _ret = False
    else :
       _ret = True
    return _ret
    

#==================================================
# FIN
#==================================================
