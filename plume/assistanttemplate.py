# (c) Didier  LECLERC 2020 CMSIG MTE-MCTRCT/SG/SNUM/UNI/DRC Site de Rouen
# créé 2022

import os.path
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import ( QMenu, QAction, \
                              QTreeWidget, QTabWidget, QWidget, QAbstractItemView, QTreeWidgetItemIterator, QTreeWidgetItem, QHeaderView, QGridLayout, QGraphicsOpacityEffect, QMessageBox )

from PyQt5.QtCore    import ( QDate, QDateTime, QTime, QDateTime, Qt )
from PyQt5.QtGui     import ( QStandardItemModel, QStandardItem, QIcon )
#
from plume.mapping_templates import ( load_mapping_read_meta_template_categories, load_mapping_read_meta_templates, load_mapping_read_meta_tabs, load_mapping_read_meta_categories )
#
from plume.pg import queries

from qgis.core import ( QgsSettings, Qgis)
import re
import sys
import json
import traceback

class Ui_Dialog_AssistantTemplate(object):   
    def setupUiAssistantTemplate(self, DialogAssistantTemplate, DialogCreateTemplate, DialogPlume, _buttonAssistant, mattrib, modCat_Attrib, mDicEnum, mLabel, mHelp, keyAncetre_ModeleCategorie_Modele_Categorie_Onglet) :   # DialogAssistantTemplate, DialogCreateTemplate, DialogPlume
        #-
        #self.mDic_LH = returnAndSaveDialogParam(self, "Load")
        self.mDic_LH                = DialogPlume.mDic_LH
        self.editStyle              = self.mDic_LH["QEdit"]              #style saisie
        self.labelBackGround        = self.mDic_LH["QLabelBackGround"]   #QLabel    
        self.epaiQGroupBox          = self.mDic_LH["QGroupBoxEpaisseur"] #épaisseur QGroupBox
        self.lineQGroupBox          = self.mDic_LH["QGroupBoxLine"]      #trait QGroupBox
        self.policeQGroupBox        = self.mDic_LH["QGroupBoxPolice"]    #Police QGroupBox
        self.policeQTabWidget       = self.mDic_LH["QTabWidgetPolice"]   #Police QTabWidget
        self.colorTemplateInVersOut = self.mDic_LH["colorTemplateInVersOut"]  
        self.colorTemplateOutVersIn = self.mDic_LH["colorTemplateOutVersIn"]     
        self.sepLeftTemplate        = self.mDic_LH["sepLeftTemplate"]
        self.sepRightTemplate       = self.mDic_LH["sepRightTemplate"]
        self.fontCategorieInVersOut = int(self.mDic_LH["fontCategorieInVersOut"])
        #-
        #- Fichier de mapping table ihm
        self.mapping_template_categories = load_mapping_read_meta_template_categories
        self.mapping_templates           = load_mapping_read_meta_templates
        self.mapping_categories          = load_mapping_read_meta_categories
        self.mapping_tabs                = load_mapping_read_meta_tabs
        #-
        self.DialogPlume               = DialogPlume
        self.DialogCreateTemplate      = DialogCreateTemplate
        self.DialogAssistantTemplate   = DialogAssistantTemplate
        self.mattrib                   = mattrib
        self.modCat_Attrib             = modCat_Attrib
        self.mDicEnum                  = mDicEnum
        self.mLabel                    = mLabel
        self.mHelp                     = mHelp
        self.keyAncetre_ModeleCategorie_Modele_Categorie_Onglet = keyAncetre_ModeleCategorie_Modele_Categorie_Onglet
        #-
        myPath = os.path.dirname(__file__)+"\\icons\\logo\\plume.svg"
        self.DialogAssistantTemplate.setObjectName("DialogConfirme")
        #-
        mDic_LH_Dialog = self.loadDimDialog()
        mLargDefaut, mHautDefaut = int(mDic_LH_Dialog["dialogLargeurAssistantTemplate"]), int(mDic_LH_Dialog["dialogHauteurAssistantTemplate"])     
        self.DialogAssistantTemplate.resize(mLargDefaut, mHautDefaut)
        #-
        self.lScreenDialog, self.hScreenDialog = int(self.DialogAssistantTemplate.width()), int(self.DialogAssistantTemplate.height())
        _pathIcons = os.path.dirname(__file__) + "/icons/logo"
        iconSource          = _pathIcons + "/plume.svg"
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(iconSource), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.DialogAssistantTemplate.setWindowIcon(icon)
        #----------
        self.labelImage = QtWidgets.QLabel(self.DialogAssistantTemplate)
        myDefPath = myPath.replace("\\","/")
        carIcon = QtGui.QImage(myDefPath)
        self.labelImage.setPixmap(QtGui.QPixmap.fromImage(carIcon))
        self.labelImage.setGeometry(QtCore.QRect(20, 0, 100, 100))
        self.labelImage.setObjectName("labelImage")
        #----------
        self.label_2 = QtWidgets.QLabel(self.DialogAssistantTemplate)
        self.label_2.setGeometry(QtCore.QRect(100, 30, self.lScreenDialog - 100, 30))
        self.label_2.setAlignment(QtCore.Qt.AlignLeft)        
        font = QtGui.QFont()
        font.setPointSize(12) 
        font.setWeight(50) 
        font.setBold(True)
        self.label_2.setFont(font)
        self.label_2.setTextFormat(QtCore.Qt.RichText)
        self.label_2.setObjectName("label_2")                                                     
        #----------
        self.label_3 = QtWidgets.QLabel(self.DialogAssistantTemplate)
        self.label_3.setGeometry(QtCore.QRect(100, 60, self.lScreenDialog - 100, 30))
        self.label_3.setAlignment(QtCore.Qt.AlignLeft)        
        font = QtGui.QFont()
        font.setPointSize(10) 
        font.setWeight(50) 
        font.setBold(True)
        self.label_3.setFont(font)
        self.label_3.setTextFormat(QtCore.Qt.RichText)
        self.label_3.setObjectName("label_3")                                                     
        #========
        #------
        # Général
        self.groupBoxGeneral = QtWidgets.QGroupBox(self.DialogAssistantTemplate)                                                   
        deltaHauteurWidget = 100
        self.groupBoxGeneral.setGeometry(QtCore.QRect(10,100,self.lScreenDialog - 20, self.hScreenDialog - deltaHauteurWidget))
        self.groupBoxGeneral.setObjectName("groupBoxGeneral") 
        self.groupBoxGeneral.setStyleSheet("QGroupBox { border: 0px solid grey }")
        #-
        self.layoutGeneral = QtWidgets.QGridLayout()
        self.groupBoxGeneral.setLayout(self.layoutGeneral)
        #-
        self.layoutGeneral.setContentsMargins(0, 0, 0, 0)
        self.layoutGeneral.setRowStretch(0, 5)
        self.layoutGeneral.setRowStretch(1, 5)
        self.layoutGeneral.setRowStretch(2, 1)
        self.layoutGeneral.setRowStretch(3, 1)
        #------
        # Help
        self.groupBoxListeHelp = QtWidgets.QGroupBox()                                                   
        self.groupBoxListeHelp.setStyleSheet("QGroupBox { background: qlineargradient(x1: 0, y1: 0, x2: 0.5, y2: 0.5, stop: 0 #958B62, stop: 1 white); \
                                                                 border-radius: 9px; margin-top: 0.5em;}")
        self.groupBoxListeHelp.setObjectName("groupBoxListeHelp") 
        self.groupBoxListeHelp.setContentsMargins(0, 0, 0, 0)
        #-
        self.layoutListeHelp = QtWidgets.QGridLayout()
        self.groupBoxListeHelp.setLayout(self.layoutListeHelp)
        #-
        self.layoutGeneral.addWidget(self.groupBoxListeHelp,0 ,0)
        #-
        mText = "" 
        _Listkeys   = [ "typeWidget",       "textWidget", "nameWidget", "aligneWidget", "wordWrap" ]
        _ListValues = [ QtWidgets.QLabel(), mText,        "label_" ,     QtCore.Qt.AlignCenter, True ]
        dicParamLabel = dict(zip(_Listkeys, _ListValues))
        self.zoneDisplayHelpFocus = self.genereLabelWithDictAssistant( dicParamLabel )
        self.zoneDisplayHelpFocus.setTextFormat(Qt.MarkdownText)        
        self.layoutListeHelp.addWidget( self.zoneDisplayHelpFocus, 0, 0)
        self.zoneDisplayHelpFocus.setAlignment( Qt.AlignLeft | Qt.AlignVCenter )
        self.zoneDisplayHelpFocus.setText(self.mHelp)        
        #=====================================
        # [ == scrolling HELP == ]
        self.scroll_bar_ListeHelp = QtWidgets.QScrollArea() 
        self.scroll_bar_ListeHelp.setStyleSheet("QScrollArea { border: 0px solid red; margin-left: 10px; margin-right: 10px;}")
        self.scroll_bar_ListeHelp.setWidgetResizable(True)
        self.scroll_bar_ListeHelp.setWidget(self.groupBoxListeHelp)
        self.scroll_bar_ListeHelp.setContentsMargins(0, 0, 0, 0)
        self.layoutGeneral.addWidget(self.scroll_bar_ListeHelp, 0, 0)
        #------
        # TreeView
        self.groupBoxListeOutIn = QtWidgets.QGroupBox()                                                   
        self.groupBoxListeOutIn.setObjectName("groupBoxListeOutIn") 
        self.groupBoxListeOutIn.setStyleSheet("QGroupBox { border: 0px solid green }")
        #-
        self.layoutListeOutIn = QtWidgets.QGridLayout()
        self.groupBoxListeOutIn.setLayout(self.layoutListeOutIn)
        self.layoutListeOutIn.setColumnStretch(0, 6)
        self.layoutListeOutIn.setColumnStretch(1, 1)
        self.layoutListeOutIn.setColumnStretch(2, 6)
        #-
        self.layoutListeOutIn.setContentsMargins(10, 10, 10, 0)
        self.layoutGeneral.addWidget(self.groupBoxListeOutIn,1 ,0)
        #-
        titleListeOut = QtWidgets.QApplication.translate("AssistantTemplate_ui", "Available values", None)      # Valeurs disponibles
        titleListeIn  = QtWidgets.QApplication.translate("AssistantTemplate_ui", "Selected values", None)       # Valeurs sélectionnées
        #-
        self.mTreeListeIn  = TREEVIEW_PROPRIETE_IN_OUT()
        self.mTreeListeOut = TREEVIEW_PROPRIETE_IN_OUT()
        self.mTreeListeOut.setStyleSheet("QTreeWidget {background-color: '" + self.mDic_LH["opacityCatOut"] + "';}")
        #-
        opacityEffect = QGraphicsOpacityEffect()
        # coeff d'opacité
        opacityEffect.setOpacity(float(self.mDic_LH["opacityValueCatOut"]))
        self.mTreeListeOut.setGraphicsEffect(opacityEffect)
        #-
        self.layoutListeOutIn.addWidget( self.mTreeListeOut, 0 ,0)
        self.layoutListeOutIn.addWidget( self.mTreeListeIn,  0 ,2)
        # For assistant pour la saisir du jsonb
        mText = "" 
        _Listkeys   = [ "typeWidget",       "textWidget",    "nameWidget", "aligneWidget" ]
        _ListValues = [ QtWidgets.QTextEdit(), mText,        "zone_" ,     QtCore.Qt.AlignCenter ]
        dicParamZone = dict(zip(_Listkeys, _ListValues))
        self.zoneJSONB = self.genereLabelWithDictAssistant( dicParamZone )
        self.layoutListeOutIn.addWidget( self.zoneJSONB, 0, 0, 1, 3 )
        self.zoneJSONB.setVisible(False)
        
        #- Affiche
        if self.mDicEnum != None :
           if hasattr(self.DialogPlume.dicValuePropriete, "loccat_path") :
              self.mNameCategorieClicked = self.DialogPlume.dicValuePropriete[self.keyAncetre_ModeleCategorie_Modele_Categorie_Onglet]["loccat_path"] if self.DialogPlume.dicValuePropriete[self.keyAncetre_ModeleCategorie_Modele_Categorie_Onglet]["loccat_path"] != "" else self.DialogPlume.dicValuePropriete[self.keyAncetre_ModeleCategorie_Modele_Categorie_Onglet]["shrcat_path"]
           elif hasattr(self.DialogPlume.dicValuePropriete, "path") :
              self.mNameCategorieClicked = self.DialogPlume.dicValuePropriete[self.keyAncetre_ModeleCategorie_Modele_Categorie_Onglet]["path"]
           elif hasattr(self.DialogPlume.dicValuePropriete, "tpl_id") :
              self.mNameCategorieClicked = self.DialogPlume.dicValuePropriete[self.keyAncetre_ModeleCategorie_Modele_Categorie_Onglet]["tpl_id"]
           elif hasattr(self.DialogPlume.dicValuePropriete, "tab_id") :
              self.mNameCategorieClicked = self.DialogPlume.dicValuePropriete[self.keyAncetre_ModeleCategorie_Modele_Categorie_Onglet]["tab_id"]

           if isinstance( self.mDicEnum, dict ) : #  exemple dicEnum["geo_tools"]
              self.mListeProprietesDispo  = self.mDicEnum
              self.mListeProprietesSelect = self.DialogPlume.dicValuePropriete[self.keyAncetre_ModeleCategorie_Modele_Categorie_Onglet][self.mattrib] 
           elif self.mDicEnum == "sources" :      # For assistant pour lancer les requêtes pour alimenter les sources des thésaurus
              if self.DialogPlume.listeThesaurus != None :
                 # Géré dans le [ def ihmsPlume_CAT_IN_OUT(self, item, column): ]
                 self.mListeProprietesDispo = self.mDicEnum = self.DialogPlume.listeThesaurus
                 # gestion du In on ne touche à rien, ce sera fait dans le affiche_PROPRIETE_IN_OUT
                 self.mListeProprietesSelect = self.DialogPlume.dicValuePropriete[self.keyAncetre_ModeleCategorie_Modele_Categorie_Onglet][self.mattrib]
                 
           elif self.mDicEnum in ("compute_params", "md_conditions") :      # For assistant pour la saisir du jsonb
              self.mTreeListeOut.setVisible(False)
              self.mTreeListeIn.setVisible(False)
              self.zoneJSONB.setVisible(True)
              
        if self.mDicEnum not in ("compute_params", "md_conditions") :      
           self.mTreeListeOut.clear()
           self.mTreeListeIn.clear()
           self._origineHeaderLabelsIn  = [ "PRO_IN" , titleListeOut, titleListeIn ]
           self._origineHeaderLabelsOut = [ "PRO_OUT", titleListeOut, titleListeIn ]
           
           # Pour la gestion de la différence, on ne fait qu'une fois
           firstDisplay = True  
           self.mTreeListeOut.affiche_PROPRIETE_IN_OUT( self.DialogCreateTemplate, self.mTreeListeIn, self.mTreeListeOut, self.mattrib, self.mListeProprietesDispo, self.mListeProprietesSelect, action = True,   firstDisplay = True, header = self._origineHeaderLabelsOut) 
           self.mTreeListeIn.affiche_PROPRIETE_IN_OUT(  self.DialogCreateTemplate, self.mTreeListeIn, self.mTreeListeOut, self.mattrib, self.mListeProprietesDispo, self.mListeProprietesSelect, action = False , firstDisplay = True, header = self._origineHeaderLabelsIn)
        elif self.mDicEnum in ("compute_params", "md_conditions") :       # For assistant pour la saisir du jsonb    
           self.zoneJSONB.setAlignment( Qt.AlignJustify | Qt.AlignVCenter )
           # json dans la zone
           mVal, _exit = returnTranslatePostgreSQL_PythonVsJson(self.DialogPlume, self.DialogPlume.dicValuePropriete[self.keyAncetre_ModeleCategorie_Modele_Categorie_Onglet][self.mattrib], "pythonVERSjson")  # dumps
           self.zoneJSONB.setPlainText( "" if mVal in (None, "null", '""') else mVal )
        #========
        #-
        self.groupBox_buttons = QtWidgets.QGroupBox()
        self.groupBox_buttons.setObjectName("groupBox_buttons")
        self.groupBox_buttons.setStyleSheet("QGroupBox { border: 0px solid blue }")
        #-
        self.layout_groupBox_buttons = QtWidgets.QGridLayout()
        self.layout_groupBox_buttons.setContentsMargins(0, 0, 0, 0)
        self.groupBox_buttons.setLayout(self.layout_groupBox_buttons)
        self.layoutGeneral.addWidget(self.groupBox_buttons,3 ,0 )
        #-
        self.layout_groupBox_buttons.setColumnStretch(0, 3)
        self.layout_groupBox_buttons.setColumnStretch(1, 1)
        self.layout_groupBox_buttons.setColumnStretch(2, 1)
        self.layout_groupBox_buttons.setColumnStretch(3, 1)
        self.layout_groupBox_buttons.setColumnStretch(4, 3)
        #-
        #----------
        self.pushButtonAnnuler = QtWidgets.QPushButton()
        self.pushButtonAnnuler.setObjectName("pushButtonAnnuler")
        self.pushButtonAnnuler.clicked.connect(self.DialogAssistantTemplate.reject)
        self.layout_groupBox_buttons.addWidget(self.pushButtonAnnuler, 1, 1, QtCore.Qt.AlignTop)
        #--
        self.pushButtonApply = QtWidgets.QPushButton()
        self.pushButtonApply.setObjectName("pushButtonApply")
        self.pushButtonApply.clicked.connect(lambda : self.applySelected( self.mTreeListeIn, self.mattrib, self.modCat_Attrib, self.mDicEnum, self.zoneJSONB ))
        self.layout_groupBox_buttons.addWidget(self.pushButtonApply, 1, 3, QtCore.Qt.AlignTop)
        #--
        #----------
        self.DialogAssistantTemplate.setWindowTitle(QtWidgets.QApplication.translate("plume_main", "PLUME (Metadata storage in PostGreSQL") )
        self.zMessTitle    =  QtWidgets.QApplication.translate("AssistantTemplate_ui", "Properties Wizard", None)   #Assistant des propriétés
        self.label_2.setText(self.zMessTitle)
        self.label_3.setText(str(self.mLabel))
        self.pushButtonApply.setText(QtWidgets.QApplication.translate("AssistantTemplate_ui", "Apply", None))
        self.pushButtonAnnuler.setText(QtWidgets.QApplication.translate("AssistantTemplate_ui", "Cancel", None))
        # 

    #==================================================
    def applySelected(self, _mTreeListeIn, _mattrib, _modCat_Attrib, _mDicEnum, _zoneJSONB = None) :
        """
        {
           "pattern": "^[^.]+"
        }
        """
        _exit = True
        if _mDicEnum not in ("compute_params", "md_conditions") :       # For assistant pour la saisir du jsonb    
           _list = []
           iterator = QTreeWidgetItemIterator(_mTreeListeIn)
           while iterator.value() :
              _enumLabel = iterator.value().text(0)

              for keyDicEnum, valueDicEnum in _mDicEnum.items() :
                  if valueDicEnum["enum_label"] == _enumLabel : 
                     _list.append(keyDicEnum)
                     break
              iterator += 1

           #Mets à jour le QlineEdit dans l'IHM de createTemplate
           _modCat_Attrib.setText( str("" if len(_list) == 0  else _list) )  
           #Mets à jour la variable et le dictionnaire
           if len(_list) == 0  : _list = None
           self.mListeProprietesSelect                  = _list
           self.DialogPlume.dicValuePropriete[self.keyAncetre_ModeleCategorie_Modele_Categorie_Onglet][_mattrib] = _list
        elif _mDicEnum in ("compute_params", "md_conditions") :       # For assistant pour la saisir du jsonb 
           # La zone du QTextEdit   
           _zoneJSONB = _zoneJSONB.toPlainText()
           _zoneJSONB = _zoneJSONB if _zoneJSONB not in (None, "") else "null" 

           #Mets à jour la variable et le dictionnaire
           mVal, _exit = returnTranslatePostgreSQL_PythonVsJson(self.DialogPlume, _zoneJSONB, "jsonVERSpython")    # loads

           # Mets à jour le QTextEdit dans l'IHM de createTemplate si _exit = True (JSON OK)
           # et
           # Mets à jour la variable et le dictionnaire
           if _exit == True : 
              # For display json in QlineEdit  
              _zoneJSONB = json.dumps(mVal, ensure_ascii=False)  # dumps
              _modCat_Attrib.setText( str("" if _zoneJSONB.lower() == "null" else _zoneJSONB ) )
              #
              self.DialogPlume.dicValuePropriete[self.keyAncetre_ModeleCategorie_Modele_Categorie_Onglet][_mattrib] = mVal  
        if _exit == True : self.close()
        return 

    #==================================================
    def loadDimDialog(self) :
        mSettings = QgsSettings()
        mSettings.beginGroup("PLUME")
        mSettings.beginGroup("Generale")
       
        mDicAutre        = {}
        valueDefautAssistantTemplateL = 600
        valueDefautAssistantTemplateH = 400
        mDicAutre["dialogLargeurAssistantTemplate"]   = valueDefautAssistantTemplateL
        mDicAutre["dialogHauteurAssistantTemplate"]   = valueDefautAssistantTemplateH
                    
        for key, value in mDicAutre.items():
            if not mSettings.contains(key) :
               mSettings.setValue(key, value)
            else :
               mDicAutre[key] = mSettings.value(key)

        mSettings.endGroup()
        mSettings.endGroup()    
        return mDicAutre
          
    #==========================
    def resizeEvent(self, event):
        deltaHauteurWidget = 120
        self.groupBoxGeneral.setGeometry(QtCore.QRect(10,100,self.DialogAssistantTemplate.width() - 20, self.DialogAssistantTemplate.height() - deltaHauteurWidget))
        return
        
    #==========================         
    def genereLabelWithDictAssistant(self, dicParamLabel ) :
        for k, v in dicParamLabel.items() :
            if v != "" :
               if k == "typeWidget"    : _label = v
               if k == "nameWidget"    : _label.setObjectName(v)
               if k == "toolTipWidget" : _label.setToolTip(v)
               if k == "aligneWidget"  : _label.setAlignment(v)
               if k == "textWidget"    : _label.setText(v)
               if k == "styleSheet"    : _label.setStyleSheet(v)
               if k == "wordWrap"      : _label.setWordWrap(v)
        return _label

#==========================   
# Transformation d'un type str vers un type JSON et vice versa    
def returnTranslatePostgreSQL_PythonVsJson(_self, _mVal, _Sens) :
    _exit = True
    if _Sens   == "pythonVERSjson" :      # python vers jsonb
       _mVal = json.dumps(_mVal, ensure_ascii=False, indent=4)
    elif _Sens   == "jsonVERSpython" :    # jsonb vers python
       try : 
          _mVal = json.loads(_mVal)
       except :
          zTitre     = QtWidgets.QApplication.translate("assistanttemplate_ui", "PLUME : Warning", None)
          zMess      = QtWidgets.QApplication.translate("assistanttemplate_ui", "The syntax of your json is incorrect.", None) + "\n"
          pyMSG = "Erreur détectée :\n\n" + str(sys.exc_info()[1])
          zMess      = zMess + "\n" + pyMSG 
          QMessageBox.critical(_self, zTitre, zMess)
          _exit = False
    return _mVal, _exit 

#========================================================     
#========================================================     
# Class pour le tree View Catégories IN and OUT 
class TREEVIEW_PROPRIETE_IN_OUT(QTreeWidget):
    customMimeType = "text/plain"

    #===============================              
    def __init__(self, *args):
        QTreeWidget.__init__(self, *args)
        self.setHeaderLabels([""])  
        self.setColumnCount(1)
        self.setSelectionMode(QAbstractItemView.SingleSelection	)  
        self.itemDoubleClicked.connect(self.moveDoubleClicked)
        return

    #===============================              
    def design_Items(self, _item, _mDicInVersOutDesign, _label, _color) :
        if _mDicInVersOutDesign != None :
           if _label in _mDicInVersOutDesign :  #Design color 
              _item.setBackground(0, _color)
        return
        
    #===============================              
    def affiche_PROPRIETE_IN_OUT(self, DialogCreateTemplate, self_Pro_In, self_Pro_Out, mattrib = None, mDicOut = None, mDicIn = None, action = False, firstDisplay = False, header = None ) :
        _pathIcons = os.path.dirname(__file__) + "/icons/logo"
        # For logo dans tooltip 
        _pathIconsButtons         = os.path.dirname(__file__) + "/icons/buttons"
        self.menuIconHelpComputeManuel = _pathIconsButtons + "/compute_button.svg"
        #----------
        if header != None : self.setHeaderLabels([ header[2] if header[0] == "PRO_IN" else header[1] ])               
        self.DialogCreateTemplate    = DialogCreateTemplate                                                   
        #---
        self.self_Pro_In             = self_Pro_In                                                   
        self.self_Pro_Out            = self_Pro_Out  
        #---
        self.mattrib                 = mattrib
        self.mDicOut                 = mDicOut                                                     
        self.mDicIn                  = mDicIn                                                     
        #---
        self.header().setStretchLastSection(True)
        self.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        #---
        self.self_Pro_Out.header().setStretchLastSection(True)
        self.self_Pro_Out.header().setSectionResizeMode(QHeaderView.ResizeToContents)

        # ===== Transforme mDicIn (lecture retour PostgreSQL) vers le format mDicEnum (mDicOut)
        """
        exemple !
        self.mDicIn  =  ['empty', 'new', 'manual']
        self.mDicOut = {'auto':   {'enum_label': 'Automatique', 'enum_help': ''}, 
                        'empty':  {'enum_label': 'Vide',        'enum_help': ''}, 
                        'manual': {'enum_label': 'Manuel',      'enum_help': ''}, 
                        'new':    {'enum_label': 'Nouvelle',    'enum_help': ''}}        
        """
        # *   
        # Pour la gestion de la différence, on ne fait qu'une fois
        #  mListeProprietesDispo = dicEnum - mListeProprietesSelect
        if firstDisplay :  
           if self.mDicIn != None :
              if len(self.mDicIn) > 0 :
                 self.mDicInTempo  = {}
                 for elemPro in self.mDicIn :
                     if elemPro in self.mDicOut : self.mDicInTempo[elemPro] = self.mDicOut[elemPro]
                 #Substituer l'ancien mDicIn par le nouveau    
                 self.mDicIn = self.mDicInTempo
              else :
                 self.mDicIn = {}
           else :
              self.mDicIn = {}
           # *   
           if self.mDicOut != None :
              if len(self.mDicOut) > 0 :
                 self.mDicOutTempo = {} 
                 for k, v in self.mDicOut.items() :
                     if k not in self.mDicIn :self. mDicOutTempo[k] = v
                 #Substituer l'ancien mDicOut par le nouveau    
                 self.mDicOut = self.mDicOutTempo
              else :
                 self.mDicOut = {}
           else :
              self.mDicOut = {}
           # *   
        # ===== Transforme mDicIn (lecture retour PostgreSQL) vers le format mDicEnum (mDicOut)

        #Tri
        if len(self.mDicIn) > 0  :
           self.mDicIn = self.fonctionTritDictValue(self.mDicIn, "enum_label")
        if len(self.mDicOut) > 0  :
           self.mDicOut = self.fonctionTritDictValue(self.mDicOut, "enum_label")
        
        #Create Arbo
        if not action : return # Permet de ne pas repasser dans l'algo pour instancier les variables dans la création des QTreeWidgetItem
        # ======================================
        # ======================================
        #Create Arbo IN
        # Example : { 'gsp:wktLiteral': {'enum_label': 'Littérale', 'enum_help': ''}, rdf:langString" : {"enum_label" : "Langue",    "enum_help" : ""}, .... }
        rowNodeIn = 0
        for k, v in self.mDicIn.items() : 
           # Devient : ['Littérale', 'IN', 'aide', gsp:wktLiteral', 'datatype'] ou ['Langue', 'OUT', 'rdf:langString', 'aide', 'datatype']
           paramQTreeWidgetItem = [ v["enum_label"] ] + [ "IN" ] + [ k ] + [ v["enum_help"] ] + [mattrib] 
           nodeUser = QTreeWidgetItem(None, paramQTreeWidgetItem)
           nodeUser.setToolTip( 0, v["enum_help"].replace('menuIconHelpComputeManuel', self.menuIconHelpComputeManuel) )
           #self.design_Items(nodeUser, self.dicOutVersInDesign, _label, _color_In_OutVersIn) #For colorisation
           self.self_Pro_In.insertTopLevelItems( rowNodeIn, [ nodeUser ] )
           rowNodeIn += 1
        #Create Arbo IN
        # ======================================
        # ======================================
        #Create Arbo OUT
        # Example : { 'gsp:wktLiteral': {'enum_label': 'Littérale', 'enum_help': ''}, rdf:langString" : {"enum_label" : "Langue",    "enum_help" : ""}, .... }
        rowNodeOut = 0
        for k, v in self.mDicOut.items() : 
           # Devient : ['Littérale', 'OUT', 'aide', gsp:wktLiteral', 'datatype'] ou ['Langue', 'OUT', 'rdf:langString', 'aide', 'datatype']
           paramQTreeWidgetItem = [ v["enum_label"] ] + [ "OUT" ] + [ k ] + [ v["enum_help"] ] + [mattrib] 
           nodeUser = QTreeWidgetItem(None, paramQTreeWidgetItem)
           nodeUser.setToolTip( 0, v["enum_help"].replace('menuIconHelpComputeManuel', self.menuIconHelpComputeManuel) )
           #self.design_Items(nodeUser, self.dicOutVersInDesign, _label, _color_In_OutVersIn) #For colorisation
           self.self_Pro_Out.insertTopLevelItems( rowNodeOut, [ nodeUser ] )
           rowNodeOut += 1
        #Create Arbo OUT
        # ======================================
        # ======================================
        return

    #===============================              
    def moveDoubleClicked(self, item, column):
        if item == None : return 

        # _enum_label Libellé affiché de la propriété en français (colonne 0 in QtreeWidget)
        #  mOrigine   Sens (In vers Out ou vice Versa             (colonne 1 in QtreeWidget)
        # _enum       Libellé origine de l'enum                   (colonne 2 in QtreeWidget)
        # _enum_help  Libellé affiché de l'aide                   (colonne 3 in QtreeWidget)
        # _mattrib    Libellé de la propriété originelle          (colonne 4 in QtreeWidget)
        mItemClic_enum_label = item.data(0, QtCore.Qt.DisplayRole)  # _enum_label
        mItemClic_mOrigine   = item.data(1, QtCore.Qt.DisplayRole)  #  Origine In ou OUT
        mItemClic_enum       = item.data(2, QtCore.Qt.DisplayRole)  # _enum
        mItemClic_enum_help  = item.data(3, QtCore.Qt.DisplayRole)  # _help
        mItemClic_mattrib    = item.data(4, QtCore.Qt.DisplayRole)  # _mattrib
        """
        EXEMPLE
        'mItemClic_enum_label': 'Littérale'  
        'mItemClic_mOrigine':   'OUT' or 'IN'  
        'mItemClic_enum':       'gsp:wktLiteral'  
        'mItemClic_enum_help':  'Aide'  
        'mItemClic_mattrib':    'datatype'  
        """
        if mItemClic_mOrigine == "IN" :
           if mItemClic_enum in self.mDicIn :
              del self.mDicIn[mItemClic_enum] 
              self.mDicOut[mItemClic_enum] = {'enum_label': mItemClic_enum_label, 'enum_help': mItemClic_enum_help}
        elif mItemClic_mOrigine == "OUT" :   
           if mItemClic_enum in self.mDicOut :
              del self.mDicOut[mItemClic_enum] 
              self.mDicIn[mItemClic_enum] = {'enum_label': mItemClic_enum_label, 'enum_help': mItemClic_enum_help} 
        # -
        self.self_Pro_Out.clear()
        self.self_Pro_In.clear()
        
        # Pour la gestion de la différence, on ne fait qu'une fois
        #  mListeProprietesDispo = dicEnum - mListeProprietesSelect
        firstDisplay = False  
        self.self_Pro_Out.affiche_PROPRIETE_IN_OUT( self.DialogCreateTemplate, self.self_Pro_In, self.self_Pro_Out, self.mattrib, self.mDicOut, self.mDicIn, action = True,  firstDisplay = False, header = None) 
        self.self_Pro_In.affiche_PROPRIETE_IN_OUT(  self.DialogCreateTemplate, self.self_Pro_In, self.self_Pro_Out, self.mattrib, self.mDicOut, self.mDicIn, action = False, firstDisplay = False, header = None)
        return
        
    #===============================              
    def fonctionTritDictValue(self, dict, keyValue) :
        tempListDic = [v for k, v in dict.items()]
        tempListDic = sorted(tempListDic, key = self.fonctionTritDict, reverse=False)
        retDic = {}
        for elem in tempListDic :
            for k, v in dict.items() :
               if elem == v : 
                  retDic[k] = v
                  break
        return retDic
        
    #===============================              
    def fonctionTritDict(self, value):
        return value['enum_label']        
