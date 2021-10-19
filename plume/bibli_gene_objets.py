# (c) Didier  LECLERC 2020 CMSIG MTE-MCTRCT/SG/SNUM/UNI/DRC Site de Rouen
# créé sept 2021

from PyQt5 import QtCore, QtGui, QtWidgets, QtSvg
from PyQt5.QtWidgets import (QAction, QMenu , QApplication, QMessageBox, QFileDialog, QTextEdit, QLineEdit,  QMainWindow, QCompleter, QDateEdit, QDateTimeEdit, QCheckBox, QWidget) 
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import *
from qgis.gui import *
from qgis.gui import QgsDateTimeEdit
import os
from . import bibli_plume
from .bibli_plume import *
from .bibli_rdf import rdf_utils
                     
#==================================================
def generationObjets(self, _keyObjet, _valueObjet) :
    _pathIcons = os.path.dirname(__file__) + "/icons/buttons"
    _iconSources          = _pathIcons + "/source_button.svg"
    _iconSourcesSelect    = _pathIcons + "/source_button.png"
    _iconSourcesVierge    = _pathIcons + "/vierge.png"
    _iconPlus                  = _pathIcons + "/plus_button.svg"
    _iconPlusTempGoProperties  = _pathIcons + "/color_button_Plus_GoProperties.svg"
    _iconPlusTempGoValues      = _pathIcons + "/color_button_Plus_GoValues.svg"
    _iconPlusTempTgroup        = _pathIcons + "/color_button_Plus_Tgroup.svg"
    _iconMinus                 = _pathIcons + "/minus_button.svg"
    _iconMinusTempGoProperties = _pathIcons + "/color_button_Minus_GoProperties.svg"
    _iconMinusTempGoValues     = _pathIcons + "/color_button_Minus_GoValues.svg"
    _iconMinusTempTgroup       = _pathIcons + "/color_button_Minus_Tgroup.svg"
    _mListeIconsButtonPlusMinus = [ _iconPlusTempGoProperties, _iconPlusTempGoValues,  _iconPlusTempTgroup, \
                                   _iconMinusTempGoProperties, _iconMinusTempGoValues, _iconMinusTempTgroup ]

    #---------------------------
    # Gestion des langues
    _language = 'fr'
    _langList = ['fr', 'en']

    #---------------------------
    #Pour Gestion et Génération à la volée des onglets 
    if (rdf_utils.is_root(_keyObjet) and _valueObjet['main widget type'] == "QGroupBox") : 
       self.mFirst = rdf_utils.is_root(_keyObjet)
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
       #-- 
       #Masqué /Visible Générale                               
       if (_valueObjet['hidden'] or _valueObjet['hidden M']) : _mObjetGroupBox.setVisible(False)

       if _valueObjet['object'] == 'group of properties' :
          _colorQGroupBox = self.colorQGroupBox if self.mFirst else self.colorQGroupBoxGroupOfProperties
          _epaiQGroupBox  = self.epaiQGroupBox #Si on souhaite gérer l'épaisseur du premier cadre 
          _epaiQGroupBox  = 0 if self.mFirst else self.epaiQGroupBox 
       elif _valueObjet['object'] == 'group of values' :
          _colorQGroupBox = self.colorQGroupBoxGroupOfValues
          _epaiQGroupBox  = self.epaiQGroupBox 
       elif _valueObjet['object'] == 'translation group' :
          _colorQGroupBox = self.colorQGroupBoxTranslationGroup
          _epaiQGroupBox  = self.epaiQGroupBox 
       else :   
          _colorQGroupBox = self.colorDefaut
          _epaiQGroupBox  = self.epaiQGroupBox 
       _mObjetGroupBox.setStyleSheet("QGroupBox {   \
                              margin-top: 6px; \
                              margin-left: 10px; \
                              font-family:" + self.policeQGroupBox  +" ; \
                              border-style: " + self.lineQGroupBox  + ";    \
                              border-width:" + str(_epaiQGroupBox)  + "px ; \
                              border-color: " + _colorQGroupBox  +";      \
                              font: bold 11px;         \
                              padding: 6px;            \
                              }")
       #--
       #_mParentEnCours.addWidget(_mObjetGroupBox, _valueObjet['row'], 0, 1, 2)
       row, column, rowSpan, columnSpan = self.mDicObjetsInstancies.widget_placement(_keyObjet, 'main widget')
       _mParentEnCours.addWidget(_mObjetGroupBox, row, column, rowSpan, columnSpan)
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
          _mObjetQSaisie.setStyleSheet("QComboBox {  font-family:" + self.policeQGroupBox  +"; border-style:" + _editStyle  +" ; border-width: 0px;}")
       _mObjetQSaisie.setObjectName(str(_keyObjet))
       #--                        
       #Masqué /Visible Générale                               
       if (_valueObjet['hidden'] or _valueObjet['hidden M']) : _mObjetQSaisie.setVisible(False)
       #--                        
       row, column, rowSpan, columnSpan = self.mDicObjetsInstancies.widget_placement(_keyObjet, 'main widget')
       _mParentEnCours.addWidget(_mObjetQSaisie, row, column, rowSpan, columnSpan)
       #--                        
       if _valueObjet['main widget type'] in ("QTextEdit") :
          _mObjetQSaisie.setMinimumSize(QtCore.QSize(100, 15 * rowSpan)) # Pour obtenir des QTexEdit suffisament haut
       else :   
          _mObjetQSaisie.setMinimumSize(QtCore.QSize(100, 23))

       if _valueObjet['main widget type'] in ("QLineEdit", "QTextEdit") :
          #Valeur                        
          _mObjetQSaisie.setText(_valueObjet['value'])
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
          if "i" in _valueObjet['regex validator flags']:
             re.setPatternOptions(QRegularExpression.CaseInsensitiveOption)
          if "s" in _valueObjet['regex validator flags']:
             re.setPatternOptions(QRegularExpression.DotMatchesEverythingOption)
          if "m" in _valueObjet['regex validator flags']:
             re.setPatternOptions(QRegularExpression.MultilineOption)
          if "x" in _valueObjet['regex validator flags']:
             re.setPatternOptions(QRegularExpression.ExtendedPatternSyntaxOption)
          _mObjetQSaisie.setValidator(QRegularExpressionValidator(re),_mObjetQSaisie)
       
       #========== 
       #QCOMBOBOX                        
       if _valueObjet['main widget type'] in ("QComboBox") :
          _thesaurus = rdf_utils.build_vocabulary(_valueObjet['current source'], self.vocabulary, language=_language)
          #print(_thesaurus)
          if _thesaurus != None : _mObjetQSaisie.addItems(_thesaurus)
          _mObjetQSaisie.setCurrentText(_valueObjet['value']) 
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
       #Masqué /Visible Générale                               
       if (_valueObjet['hidden'] or _valueObjet['hidden M']) : _mObjetQLabel.setVisible(False)
       #--                        
       row, column, rowSpan, columnSpan = self.mDicObjetsInstancies.widget_placement(_keyObjet, 'main widget')
       _mParentEnCours.addWidget(_mObjetQLabel, row, column, rowSpan, columnSpan)
       #Valeur                        
       _mObjetQLabel.setText(_valueObjet['value']) 
       #--                        
       _mObjetQLabel.setWordWrap(True)
       _mObjetQLabel.setOpenExternalLinks(True)
    # == QLABEL
    #---------------------------
    #---------------------------
    # == QDATEEDIT
    elif _valueObjet['main widget type'] == "QDateEdit" :
       #--                        
       _mObjetQDateEdit = QgsDateTimeEdit()
       #Masqué /Visible Générale                               
       if (_valueObjet['hidden'] or _valueObjet['hidden M']) : _mObjetQDateEdit.setVisible(False)
       #--                        
       _mObjetQDateEdit.setStyleSheet("QgsDateTimeEdit {  font-family:" + self.policeQGroupBox  +"; }")
       _mObjetQDateEdit.setObjectName(str(_keyObjet))
       _mObjetQDateEdit.setDisplayFormat('dd/MM/yyyy')
       _mObjetQDateEdit.setMinimumWidth(112)
       _mObjetQDateEdit.setMaximumWidth(112)
       _mObjetQDateEdit.setCalendarPopup(True)
        #--                        
       row, column, rowSpan, columnSpan = self.mDicObjetsInstancies.widget_placement(_keyObjet, 'main widget')
       _mParentEnCours.addWidget(_mObjetQDateEdit, row, column, rowSpan, columnSpan, Qt.AlignLeft)
        #Valeur 
       if valueExiste('value', _valueObjet) : 
          _valueDate = tuple(map(int, _valueObjet['value'].split('-')))                      
          _mObjetQDateEdit.setDate(QDate(_valueDate[0], _valueDate[1], _valueDate[2]))
       else :
          _mObjetQDateEdit.setDateTime(QDateTime.currentDateTime())
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
       if (_valueObjet['hidden'] or _valueObjet['hidden M']) : _mObjetQCheckBox.setVisible(False)
       #--                        
       _mObjetQCheckBox.setStyleSheet("QCheckBox {  font-family:" + self.policeQGroupBox  +"; }")
       _mObjetQCheckBox.setObjectName(str(_keyObjet))
       #--                        
       row, column, rowSpan, columnSpan = self.mDicObjetsInstancies.widget_placement(_keyObjet, 'main widget')
       _mParentEnCours.addWidget(_mObjetQCheckBox, row, column, rowSpan, columnSpan)
       _mObjetQCheckBox.setChecked(True if _valueObjet['value'] else False)       
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
       _mObjetQDateTime = QDateTimeEdit()
       #Masqué /Visible Générale                               
       if (_valueObjet['hidden'] or _valueObjet['hidden M']) : _mObjetQDateTime.setVisible(False)
       #--                        
       _mObjetQDateTime.setStyleSheet("QDateTimeEdit {  font-family:" + self.policeQGroupBox  +"; }")
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
          _mObjetQDateTime.setDate(QDate.fromString( _valueObjet['value'], _displayFormat))       
       else :
          _mObjetQDateTime.setDateTime(QDateTime.currentDateTime())
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
    # == QTOOLBUTTON   Button PLUS et Button TRADUCTION
    elif _valueObjet['main widget type'] in ("QToolButton") :
       #--
       _mObjetQToolButton = QtWidgets.QToolButton()
       _mObjetQToolButton.setObjectName(str(_keyObjet))

       # == QICON
       _mObjetQToolButton.setIcon(QIcon(changeColorIcon(self, _keyObjet, "buttonPlus", _mListeIconsButtonPlusMinus )))
       # == QICON
              
       #- Actions
       _mObjetQToolButton.clicked.connect(lambda : action_mObjetQToolButton_Plus_translation(self, _keyObjet, _valueObjet, _language, _langList))
       #--                        
       #Masqué /Visible Générale                               
       if (_valueObjet['hidden'] or _valueObjet['hidden M']) : _mObjetQToolButton.setVisible(False)
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
    # == QTOOLBUTTON   Button MOINS
    if _valueObjet['has minus button'] :
       #--
       _mObjetQToolButton = QtWidgets.QToolButton()
       _mObjetQToolButton.setObjectName(str(_keyObjet))

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
       _mObjetQToolButton.setToolTip('Supprimer l\'élément')
       #Masqué /Visible Générale                               
       if _valueObjet['hide minus button'] : _mObjetQToolButton.setVisible(False)
       if (_valueObjet['hidden'] or _valueObjet['hidden M']) : _mObjetQToolButton.setVisible(False)

       #Dict des objets instanciés
       self.mDicObjetsInstancies[_keyObjet].update({'minus widget'  : _mObjetQToolButton}) 
    # == QTOOLBUTTON   Button MOINS
    #---------------------------
    #---------------------------
    # == QTOOLBUTTON  MULTIPLE SOURCES
    if _valueObjet['multiple sources'] :
       #--
       _mObjetQToolButton = QtWidgets.QToolButton()
       _mObjetQToolButton.setObjectName(str(_keyObjet))
       _mObjetQToolButton.setIcon(QIcon(_iconSources))
       #MenuQToolButton                        
       _mObjetQMenu = QMenu()
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
           _mObjetQMenuItem.triggered.connect(lambda : action_mObjetQToolButton(self, _keyObjet, _valueObjet, _iconSources, _iconSourcesSelect, _iconSourcesVierge))
           _mListActions.append(_mObjetQMenuItem)
       
       _mObjetQToolButton.setPopupMode(_mObjetQToolButton.MenuButtonPopup)
       _mObjetQToolButton.setMenu(_mObjetQMenu)
       #--                        
       #Masqué /Visible Générale                               
       if (_valueObjet['hidden'] or _valueObjet['hidden M']) : _mObjetQToolButton.setVisible(False)
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
       #--
       _mObjetQToolButton = QtWidgets.QToolButton()
       _mObjetQToolButton.setObjectName(str(_keyObjet))
       _mObjetQToolButton.setText(_valueObjet['language value'])
       #MenuQToolButton                        
       _mObjetQMenu = QMenu()
       _mObjetQMenu.setStyleSheet("QMenu {  font-family:" + self.policeQGroupBox  +"; width:50px;}")
       #------------
       _mListActions = []
       for elemQMenuItem in _valueObjet['authorized languages'] :
           _mObjetQMenuItem = QAction(elemQMenuItem, _mObjetQMenu)
           _mObjetQMenuItem.setText(elemQMenuItem)
           _mObjetQMenuItem.setObjectName(str(elemQMenuItem))
           _mObjetQMenu.addAction(_mObjetQMenuItem)
           #- Actions
           _mObjetQMenuItem.triggered.connect(lambda : action_mObjetQToolButtonAuthorizesLanguages(self, _keyObjet, _valueObjet, _language, _langList))
           _mListActions.append(_mObjetQMenuItem)
       
       _mObjetQToolButton.setPopupMode(_mObjetQToolButton.MenuButtonPopup)
       _mObjetQToolButton.setMenu(_mObjetQMenu)
       #--                        
       #Masqué /Visible Générale                               
       if (_valueObjet['hidden'] or _valueObjet['hidden M']) : _mObjetQToolButton.setVisible(False)
       #--                        
       row, column, rowSpan, columnSpan = self.mDicObjetsInstancies.widget_placement(_keyObjet, 'language widget')
       _mParentEnCours.addWidget(_mObjetQToolButton, row, column, rowSpan, columnSpan)
       #Tooltip                        
       _mObjetQToolButton.setToolTip('Sélection de la langue de la métadonnée')
                                          
       #Dict des objets instanciés
       self.mDicObjetsInstancies[_keyObjet].update({'language widget'  : _mObjetQToolButton, 
                                                    'language menu'    : _mObjetQMenu,
                                                    'language actions' : _mListActions}) 
       #apparence_mObjetQToolButton(self, _keyObjet, _iconSources, _valueObjet['current source'])
    # == QTOOLBUTTON  AUTHORIZED LANGUAGES
    #---------------------------

    return  

#==================================================
# Traitement action sur QToolButton avec Menu AUTHORIZED LANGUAGES
def action_mObjetQToolButtonAuthorizesLanguages(self, __keyObjet, __valueObjet, _language, _langList):
    _selectItem = self.mDicObjetsInstancies[__keyObjet]['language menu'].sender()
    #maj Source 
    ret = self.mDicObjetsInstancies.change_language(__keyObjet,  _selectItem.text(), _langList )
    #---------------------------------------------
    self.mDicObjetsInstancies[__keyObjet]['language widget'].setText(__valueObjet['language value']) 
    #---------------------------------------------
    #- Masquer          
    for elem in ret['widgets to hide'] : 
        try :
           elem.setVisible(False)
        except : 
           pass   

    #---------------------------------------------
    #- Regénération du Menu 
    regenerationMenu(self, ret['language menu to update'], __valueObjet, _language, _langList)

    #maj apparence QToolButton 
    #apparence_mObjetQToolButton(self, __keyObjet, _iconSources, _selectItem.text())
    return  

#==================================================
# Traitement action sur QToolButton Moins
def action_mObjetQToolButton_Minus(self, __keyObjet, __valueObjet, _language, _langList):
    #Mise à jour du dictionnaire des widgets 
    ret = self.mDicObjetsInstancies.drop(__keyObjet, langList=_langList)

    #- Supprimer Widget        
    for elem in ret['widgets to delete'] :
        try :                                                   
           self.mDicObjetsInstancies.parent_grid(__keyObjet).removeWidget(elem)
           elem.deleteLater()
        except : 
           pass
    #- Supprimer Menu        
    for elem in ret['menus to delete'] :
        try :                                                   
           elem.deleteLater()
        except : 
           pass
    #- Supprimer Actions        
    for elem in ret['actions to delete'] :
        try :                                                   
           elem.deleteLater()
        except : 
           pass
    #- Afficher          
    for elem in ret['widgets to show'] :
        try :                                                   
           elem.setVisible(True)
        except : 
           pass
    #- Masquer          
    for elem in ret['widgets to hide'] : 
        try :
           elem.setVisible(False)
        except : 
           pass  
    #- Déplacer 
    for elem in ret['widgets to move'] :
        elem[0].removeWidget(elem[1])
        #-- 
        elem[0].addWidget(elem[1], elem[2], elem[3], elem[4], elem[5])

    #- Regénération du menu des langues          
    regenerationMenu(self, ret['language menu to update'], __valueObjet, _language, _langList)
    return  

#==================================================
# Traitement action sur QToolButton Plus et Translation
def action_mObjetQToolButton_Plus_translation(self, __keyObjet, __valueObjet, _language, _langList):
    #Mise à jour du dictionnaire des widgets 
    ret = self.mDicObjetsInstancies.add(__keyObjet, language=_language, langList=_langList)
    
    #- Nouveaux objets à créer avec les nouvelles clefs          
    for key in ret['new keys'] :
        mParent, self.mFirst = self.mDicObjetsInstancies.parent_grid(key), False
        self.mFirst = False
        value = self.mDicObjetsInstancies[key]
        if value['main widget type'] != None :
           generationObjets(self, key, value)
        else :
           pass
    #- Afficher          
    for elem in ret['widgets to show'] :
        try :                                                   
           elem.setVisible(True)
        except : 
           pass
    #- Masquer          
    for elem in ret['widgets to hide'] : 
        try :
           elem.setVisible(False)
        except : 
           pass  
    #- Déplacer 
    for elem in ret['widgets to move'] :
        elem[0].removeWidget(elem[1])
        #--
        elem[0].addWidget(elem[1], elem[2], elem[3], elem[4], elem[5])

    #---------------------------------------------
    #- Regénération du Menu 
    regenerationMenu(self, ret['language menu to update'], __valueObjet, _language, _langList)
    return

#==================================================
# Traitement action sur QToolButton avec Menu
def action_mObjetQToolButton(self, __keyObjet, __valueObjet, _iconSources, _iconSourcesSelect, _iconSourcesVierge):
    _selectItem = self.mDicObjetsInstancies[__keyObjet]['switch source menu'].sender()
    #maj Source 
    ret = self.mDicObjetsInstancies.change_source(__keyObjet, _selectItem.text() )
    #---------------------------------------------
    #- Effacer          
    for elem in ret['widgets to empty'] : 
        try :
           elem.setText("")
        except : 
           pass
    #- Afficher          
    for elem in ret['widgets to show'] : 
        try :                                                   
           elem.setVisible(True)
        except : 
           pass
    #- Masquer          
    for elem in ret['widgets to hide'] : 
        try :
           elem.setVisible(False)
        except : 
           pass   
    #- Maj QComboBox 
    for elem in ret['concepts list to update'] : 
        __valueObjet = self.mDicObjetsInstancies[elem]
        _thesaurus = rdf_utils.build_vocabulary(_valueObjet['current source'], self.vocabulary, language=_language)
        __valueObjet['main widget'].addItems(_thesaurus)

    #---------------------------------------------
    #- Regénération du Menu 
    mListeKeyQMenuUpdate = ret['switch source menu to update'] 
    
    for mKeyQMenuUpdate in mListeKeyQMenuUpdate : 
       #Nouveau __valueObjet en fonction nouvelle clef                        
       __valueObjet  = self.mDicObjetsInstancies[mKeyQMenuUpdate]     
       #MenuQToolButton                        
       for act in __valueObjet['switch source menu'].actions() :
           __valueObjet['switch source menu'].removeAction(act)
       #--    
       _mObjetQMenu = __valueObjet['switch source menu']
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
           _mObjetQMenuItem.triggered.connect(lambda : action_mObjetQToolButton(self, mKeyQMenuUpdate, __valueObjet, _iconSources, _iconSourcesSelect, _iconSourcesVierge))
           _mListActions.append(_mObjetQMenuItem)
    
       __valueObjet['switch source widget'].setPopupMode(__valueObjet['switch source widget'].MenuButtonPopup)
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
def regenerationMenu(self, _ret, __valueObjet, _language, _langList) :
    # pour infos    _ret = ret['language menu to update']
    mListeKeyQMenuUpdate = _ret
    
    for mKeyQMenuUpdate in mListeKeyQMenuUpdate : 
       #Nouveau __valueObjet en fonction nouvelle clef                        
       __valueObjet  = self.mDicObjetsInstancies[mKeyQMenuUpdate]     
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
           _mObjetQMenuItem.setObjectName(str(elemQMenuItem))
           _mObjetQMenu.addAction(_mObjetQMenuItem)
           #- Actions
           _mObjetQMenuItem.triggered.connect(lambda : action_mObjetQToolButtonAuthorizesLanguages(self, mKeyQMenuUpdate, __valueObjet, _language, _langList))
           _mListActions.append(_mObjetQMenuItem)
    
       __valueObjet['language widget'].setPopupMode(__valueObjet['language widget'].MenuButtonPopup)
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
                border-color: red;      \
                font: bold 11px;     \
                padding: 6px;        \
                }")

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
    if __valueObjet['label'] and __valueObjet['object'] == 'edit' :
       _labelBackGround  = self.labelBackGround   #Fond Qlabel
       #--                        
       __mObjetQLabelEtiquette = QtWidgets.QLabel()
       __mObjetQLabelEtiquette.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + _labelBackGround  +";}")
       __mObjetQLabelEtiquette.setObjectName("label_" + str(__keyObjet))
       #Masqué /Visible Générale                               
       if (__valueObjet['hidden'] or __valueObjet['hidden M']) : __mObjetQLabelEtiquette.setVisible(False)
       #--                        
       row, column, rowSpan, columnSpan = self.mDicObjetsInstancies.widget_placement(__keyObjet, 'label widget')
       __mParentEnCours.addWidget(__mObjetQLabelEtiquette, row, column, rowSpan, columnSpan)
       #Valeur                        
       __mObjetQLabelEtiquette.setText(__valueObjet['label']) 
       self.mDicObjetsInstancies[__keyObjet].update({'label widget' : __mObjetQLabelEtiquette})
       __mObjetQLabelEtiquette.setMaximumSize(QtCore.QSize(self.tabWidget.width(), 18))

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
