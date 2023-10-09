# (c) Didier  LECLERC 2020 CMSIG MTE-MCTRCT/SG/SNUM/UNI/DRC Site de Rouen
# créé 2022

import os.path

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import ( QMenu, QAction, QApplication, \
                              QTreeWidget, QTabWidget, QWidget, QAbstractItemView, QTreeWidgetItemIterator, QTreeWidgetItem, QHeaderView, QGridLayout, QGraphicsOpacityEffect )
from PyQt5.QtCore    import ( QDate, QDateTime, QTime, QDateTime, Qt )
from PyQt5.QtGui     import ( QStandardItemModel, QStandardItem, QIcon, QCursor )
#
from plume.bibli_plume import ( GenereButtonsWithDictWithEvent, GenereButtonsAssistant, returnAndSaveDialogParam, returnVersion, executeSql, genereLabelWithDict, returnIcon, displayMess )
#
from plume.mapping_templates import ( load_mapping_read_meta_template_categories, load_mapping_read_meta_templates, load_mapping_read_meta_tabs, load_mapping_read_meta_categories )
# for thésaurus
from plume.rdf.properties import property_sources
from plume.rdf.thesaurus  import source_label
from plume.rdf.thesaurus  import source_nb_values
from plume.rdf.thesaurus  import source_examples
#
from plume.pg import queries
from qgis.core import Qgis
import re
import json

class Ui_Dialog_CreateTemplate(object):
    def setupUiCreateTemplate(self, DialogCreateTemplate, Dialog, listLangList):
        #-
        self.mDic_LH = returnAndSaveDialogParam(self, "Load")
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
        self.dicValuePropriete      = {}  # Déclare le dictionnaire pour le récuperer avec self._selfCreateTemplate.dicValuePropriete
        self._selfCreateTemplate    = DialogCreateTemplate
        #-
        #- Fichier de mapping table ihm
        self.mapping_template_categories = load_mapping_read_meta_template_categories
        self.mapping_templates           = load_mapping_read_meta_templates
        self.mapping_categories          = load_mapping_read_meta_categories
        self.mapping_tabs                = load_mapping_read_meta_tabs
        #-
        self.DialogCreateTemplate = DialogCreateTemplate
        self.Dialog               = Dialog               #Pour remonter les variables de la boite de dialogue
        self.listLangList         = listLangList
        myPath = os.path.dirname(__file__)+"\\icons\\logo\\plume.svg"
        self.DialogCreateTemplate.setObjectName("DialogConfirme")
        mLargDefaut, mHautDefaut = int(self.mDic_LH["dialogLargeurTemplate"]), int(self.mDic_LH["dialogHauteurTemplate"]) #900, 650    
        self.DialogCreateTemplate.resize(mLargDefaut, mHautDefaut)
        self.lScreenDialog, self.hScreenDialog = int(self.DialogCreateTemplate.width()), int(self.DialogCreateTemplate.height())
        _pathIcons = os.path.dirname(__file__) + "/icons/logo"
        iconSource          = _pathIcons + "/plume.svg"
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(iconSource), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.DialogCreateTemplate.setWindowIcon(icon)
        #----------
        self.labelImage = QtWidgets.QLabel(self.DialogCreateTemplate)
        myDefPath = myPath.replace("\\","/")
        carIcon = QtGui.QImage(myDefPath)
        self.labelImage.setPixmap(QtGui.QPixmap.fromImage(carIcon))
        self.labelImage.setGeometry(QtCore.QRect(20, 0, 100, 100))
        self.labelImage.setObjectName("labelImage")
        #----------
        self.label_2 = QtWidgets.QLabel(self.DialogCreateTemplate)
        self.label_2.setGeometry(QtCore.QRect(100, 30, self.lScreenDialog - 100, 30))
        self.label_2.setAlignment(QtCore.Qt.AlignLeft)        
        font = QtGui.QFont()
        font.setPointSize(12) 
        font.setWeight(50) 
        font.setBold(True)
        self.label_2.setFont(font)
        self.label_2.setTextFormat(QtCore.Qt.RichText)
        self.label_2.setObjectName("label_2")                                                     
        #========
        #------ 
        #Zone Onglets
        self.deltaHauteurTabWidget = 120
        self.tabWidget = QTabWidget(self.DialogCreateTemplate)
        self.tabWidget.setObjectName("tabWidget")
        self.tabWidget.setGeometry(QtCore.QRect(10,100,self.lScreenDialog - 20, self.hScreenDialog - self.deltaHauteurTabWidget))
        self.tabWidget.setStyleSheet("QTabWidget::pane {border: 2px solid #958B62; } \
                                      QTabBar::tab {border: 1px solid #958B62; border-bottom-color: none;\
                                                    border-top-left-radius: 6px;border-top-right-radius: 6px;\
                                                    padding-left: 20px; padding-right: 20px;} \
                                      QTabBar::tab:selected {\
                                      background: qlineargradient(x1: 0, y1: 0, x2: 0.5, y2: 0.5, stop: 0 #958B62, stop: 1 white); } \
                                     ")
        self.flagNewModele, self.flagNewOnglet, self.flagNewCategorie = False, False, False
        self.tabWidget.tabBarClicked.connect(self.functionChangeTab)
        #--------------------------
        self.tab_widget_Association = QWidget()
        self.tab_widget_Association.setObjectName("tab_widget_Association")

        labelTab_General = QtWidgets.QApplication.translate("colorbloc_ui", "   Association Models / Categories   ", None)
        self.tabWidget.addTab(self.tab_widget_Association,labelTab_General)
        #-
        self.groupBox_tab_widget_Association = QtWidgets.QGroupBox(self.tab_widget_Association)
        self.groupBox_tab_widget_Association.setGeometry(QtCore.QRect(10,10,self.tabWidget.width() - 20, self.tabWidget.height() - 40))
        self.groupBox_tab_widget_Association.setObjectName("groupBox_tab_widget_Association")
        self.groupBox_tab_widget_Association.setStyleSheet("QGroupBox { border: 0px solid green }")
        #-
        self.layout_tab_widget_Association = QtWidgets.QGridLayout()
        self.layout_tab_widget_Association.setContentsMargins(0, 0, 0, 0)
        self.layout_tab_widget_Association.setRowStretch(0, 0.5)
        self.layout_tab_widget_Association.setRowStretch(1, 3)
        self.layout_tab_widget_Association.setRowStretch(2, 5)
        self.layout_tab_widget_Association.setRowStretch(3, 0.5)
        self.layout_tab_widget_Association.setRowStretch(4, 0.5)
        self.tab_widget_Association.setLayout(self.layout_tab_widget_Association)
        #--------------------------
        self.tab_widget_Ressource = QWidget()
        self.tab_widget_Ressource.setObjectName("tab_widget_Ressource")
        labelTab_Metadata = QtWidgets.QApplication.translate("colorbloc_ui", "  Resources  ", None)
        self.tabWidget.addTab(self.tab_widget_Ressource,labelTab_Metadata)
        #-
        self.groupBox_tab_widget_Ressource = QtWidgets.QGroupBox(self.tab_widget_Ressource)
        self.groupBox_tab_widget_Ressource.setGeometry(QtCore.QRect(10,10,self.tabWidget.width() - 20, self.tabWidget.height() - 40))
        self.groupBox_tab_widget_Ressource.setObjectName("groupBox_tab_widget_Ressource")
        self.groupBox_tab_widget_Ressource.setStyleSheet("QGroupBox { border: 0px solid grey }")
        #-
        self.layout_tab_widget_Ressource = QtWidgets.QGridLayout()
        self.layout_tab_widget_Ressource.setContentsMargins(10, 10, 10, 10)
        self.tab_widget_Ressource.setLayout(self.layout_tab_widget_Ressource)
        #Zone Onglets
        #--------------------------

        #============================================================
        #  Onglet ASSOCIATION
        #------
        #Liste modeles / catégories
        self.groupBoxListeModeleCategorie = QtWidgets.QGroupBox(self.tab_widget_Association)
        self.groupBoxListeModeleCategorie.setObjectName("groupBoxListeModeleCategorie") 
        self.groupBoxListeModeleCategorie.setStyleSheet("QGroupBox { border: 0px solid red }")
        titleListeModeleCategorie = QtWidgets.QApplication.translate("CreateTemplate_ui", "Existing models", None)                                #{Modèles existants}
        titleDiskSaveAndReinit    = QtWidgets.QApplication.translate("CreateTemplate_ui", "Choice of metadata for the selected model", None)      #{Modèles existants}
        #-
        self.layoutListeModeleCategorie = QtWidgets.QGridLayout()
        self.layoutListeModeleCategorie.setContentsMargins(10, 0, 0, 0)
        self.groupBoxListeModeleCategorie.setLayout(self.layoutListeModeleCategorie)
        self.layout_tab_widget_Association.addWidget(self.groupBoxListeModeleCategorie, 0, 0, 1, 2)
        #-
        self.layoutListeModeleCategorie.setColumnStretch(0, 1)
        self.layoutListeModeleCategorie.setColumnStretch(1, 1)
        self.layoutListeModeleCategorie.setColumnStretch(2, 1)
        self.layoutListeModeleCategorie.setColumnStretch(3, 1)
        self.layoutListeModeleCategorie.setColumnStretch(4, 1)
        self.layoutListeModeleCategorie.setColumnStretch(5, 1)

        #------ TREEVIEW   
        self.comboListeModeleCategorie = QtWidgets.QComboBox()
        self.comboListeModeleCategorie.setObjectName("comboAdresse")
        # Label
        self.labelListeModeleCategorie = QtWidgets.QLabel()
        self.labelListeModeleCategorie.setText(titleListeModeleCategorie)
        self.labelDiskSaveAndReinit = QtWidgets.QLabel()
        self.labelDiskSaveAndReinit.setText(titleDiskSaveAndReinit)                                        
        #------
        #Button Save Out vers In and Réinit
        self.buttonSaveOutVersIn = QtWidgets.QToolButton()
        self.buttonSaveOutVersIn.setObjectName("buttonSaveOutVersIn")
        self.buttonSaveOutVersIn.setIcon(QtGui.QIcon(os.path.dirname(__file__)+"\\icons\\general\\save.svg"))
        mbuttonSaveOutVersInToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Modify used or unused categories associated with the model.", None)  #Modifier les catégories utilisées ou non utilisées associés au modèle.
        self.buttonSaveOutVersIn.setToolTip(mbuttonSaveOutVersInToolTip)
        self.buttonSaveOutVersIn.clicked.connect(lambda : self.functionUpdateModeleCategorie("buttonSaveOutVersIn"))
        self.buttonSaveOutVersIn.setVisible(True)
        #-
        self.buttonReinitOutVersIn = QtWidgets.QToolButton()
        self.buttonReinitOutVersIn.setObjectName("buttonReinitOutVersIn")
        self.buttonReinitOutVersIn.setIcon(QtGui.QIcon(os.path.dirname(__file__)+"\\icons\\general\\reset.svg"))
        mbuttonReinitOutVersIn = QtWidgets.QApplication.translate("CreateTemplate_ui", "Resetting the selected model.", None)  #Réinitialisation du modèle sélectionné.
        self.buttonReinitOutVersIn.setToolTip(mbuttonReinitOutVersIn)
        self.buttonReinitOutVersIn.clicked.connect(lambda : self.functionUpdateModeleCategorie("buttonReinitOutVersIn"))  
        self.buttonReinitOutVersIn.setVisible(True)
        #Button Save Out vers In and Réinit
        #------
        self.layoutListeModeleCategorie.addWidget(self.labelListeModeleCategorie, 0 , 0, QtCore.Qt.AlignTop)
        self.layoutListeModeleCategorie.addWidget(self.comboListeModeleCategorie, 1 , 0, 1, 2)
        #-
        self.groupBoxLabelButtonSaveAndReinit = QtWidgets.QGroupBox()
        self.groupBoxLabelButtonSaveAndReinit.setObjectName("groupBoxLabelButtonSaveAndReinit") 
        self.groupBoxLabelButtonSaveAndReinit.setStyleSheet("QGroupBox { border: 0px solid blue }")
        self.layoutLabelButtonSaveAndReinit = QtWidgets.QHBoxLayout()
        self.groupBoxLabelButtonSaveAndReinit.setLayout(self.layoutLabelButtonSaveAndReinit)
        self.layoutListeModeleCategorie.addWidget(self.groupBoxLabelButtonSaveAndReinit, 1, 1, 1, 6, Qt.AlignCenter)
        self.layoutLabelButtonSaveAndReinit.setContentsMargins(0, 0, 0, 0)

        self.layoutLabelButtonSaveAndReinit.addWidget(self.labelDiskSaveAndReinit, 0, Qt.AlignLeft)
        self.layoutLabelButtonSaveAndReinit.addWidget(self.buttonSaveOutVersIn,    0, Qt.AlignLeft)
        self.layoutLabelButtonSaveAndReinit.addWidget(self.buttonReinitOutVersIn,  0, Qt.AlignLeft)
        #-
        self.comboListeModeleCategorie.clear()

        #------
        #------ DATA template_categories 
        mKeySql = queries.query_read_meta_template_categories()
        r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self.Dialog.mConnectEnCours, mKeySql, optionRetour = "fetchall")
        self.mListTemplateCategories = [row[0] for row in r]
        
        #------ DATA template 
        mKeySql = queries.query_read_meta_template()
        r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self.Dialog.mConnectEnCours, mKeySql, optionRetour = "fetchall")
        self.mListTemplates = [row[0] for row in r]

        listeAssociationCol1, listeAssociationCol2 = returnList_Id_Label( self.mListTemplates )
        self.modeleAssociationActif = listeAssociationCol1[0] #Pour la première initialisation 
        #------
        #------ DATA categories 
        mKeySql = queries.query_read_meta_categorie()
        r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self.Dialog.mConnectEnCours, mKeySql, optionRetour = "fetchall")
        self.mListCategories = [row[0] for row in r]
        #------
        #------ DATA Tab 
        mKeySql = queries.query_read_meta_tab()
        r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self.Dialog.mConnectEnCours, mKeySql, optionRetour = "fetchall")
        self.mListTabs = [row[0] for row in r]

        #Declaration avant pour argument dans afficheASSOCIATION 
        self.groupBoxAttributsModeleCategorie = QtWidgets.QGroupBox()
        self.groupBoxAttributsModeleCategorie.setObjectName("groupBoxAttributsModeleCategorie")

        self.mTreeListeCategorieIn  = TREEVIEW_CAT_IN_OUT()
        self.mTreeListeCategorieOut = TREEVIEW_CAT_IN_OUT()
        self.mTreeListeCategorieIn.setVisible(False)
        self.mTreeListeCategorieOut.setVisible(False)
        self.mTreeListeCategorieOut.setStyleSheet("QTreeWidget {background-color: '" + self.mDic_LH["opacityCatOut"] + "';}")
                 
        opacityEffect = QGraphicsOpacityEffect()
        # coeff d'opacité
        opacityEffect.setOpacity(float(self.mDic_LH["opacityValueCatOut"]))
        self.mTreeListeCategorieOut.setGraphicsEffect(opacityEffect)

        #------ DATA 
        self.modelComboListeModeleCategorie = QStandardItemModel()
        listeAssociationCol1 = list(reversed(listeAssociationCol1))
        listeAssociationCol1.insert(0,"")
        listeAssociationCol2 = list(reversed(listeAssociationCol2))
        listeAssociationCol2.insert(0,"")

        i = 0
        while i in range(len(listeAssociationCol1)) :
            modelComboListeModeleCategorie1 = QStandardItem(str(listeAssociationCol1[i]))
            modelComboListeModeleCategorie2 = QStandardItem(str(listeAssociationCol2[i]))
            self.modelComboListeModeleCategorie.appendRow([ modelComboListeModeleCategorie2, modelComboListeModeleCategorie1 ])
            i += 1
        self.comboListeModeleCategorie.setModel(self.modelComboListeModeleCategorie) 
        self.comboListeModeleCategorie.currentIndexChanged.connect(lambda : self.ihmsPlumeASSOCIATION( self ) )
        #------ DATA 

        #------
        #Liste catégories Out
        self.groupBoxListeCategorieOut = QtWidgets.QGroupBox()
        self.groupBoxListeCategorieOut.setObjectName("groupBoxListeCategorieOut")
        self.groupBoxListeCategorieOut.setStyleSheet("QGroupBox { border: 0px solid blue;}")
         #-
        self.layoutListeCategorieOut = QtWidgets.QGridLayout()
        #-
        self.groupBoxListeCategorieOut.setLayout(self.layoutListeCategorieOut)
        self.layout_tab_widget_Association.addWidget(self.groupBoxListeCategorieOut, 1, 0, 1, 1)
        #------ 
        #Liste catégories In
        self.groupBoxListeCategorieIn = QtWidgets.QGroupBox()
        self.groupBoxListeCategorieIn.setObjectName("groupBoxListeCategorieIn")
        self.groupBoxListeCategorieIn.setStyleSheet("QGroupBox { border: 0px solid yellow;}")
         #-
        self.layoutListeCategorieIn = QtWidgets.QGridLayout()
        #-
        self.groupBoxListeCategorieIn.setLayout(self.layoutListeCategorieIn)
        self.layout_tab_widget_Association.addWidget(self.groupBoxListeCategorieIn, 1, 1, 1, 1)
        #-

        #------ Déclare TREEVIEW
        _labelCategorieOut = QtWidgets.QApplication.translate("CreateTemplate_ui", "Categories not belonging", None)   #Catégories n'appartenant pas
        _labelCategorieIn  = QtWidgets.QApplication.translate("CreateTemplate_ui", "Categories belonging", None)   #Catégories appartenant
        self._origineHeaderLabelsIn  = [ "CAT_IN" , _labelCategorieOut, _labelCategorieIn ]
        self._origineHeaderLabelsOut = [ "CAT_OUT", _labelCategorieOut, _labelCategorieIn ]

         
        #------ TREEVIEW CATEGORIES OUT
        self.layoutListeCategorieOut.addWidget(self.mTreeListeCategorieOut, 1 , 0)
        #-
        self.mTreeListeCategorieOut.clear()
        
        #------ TREEVIEW CATEGORIES IN 
        self.layoutListeCategorieIn.addWidget(self.mTreeListeCategorieIn, 1 ,2)
        #-
        self.mTreeListeCategorieIn.clear()

        #Affichage de l'aide pour les attributs
        self.groupBoxdisplayHelpFocus = QtWidgets.QGroupBox()
        self.groupBoxdisplayHelpFocus.setObjectName("groupBoxdisplayHelpFocus")
        
        self.groupBoxdisplayHelpFocus.setStyleSheet("QGroupBox { background: qlineargradient(x1: 0, y1: 0, x2: 0.5, y2: 0.5, stop: 0 #958B62, stop: 1 white); \
                                                                 border-radius: 9px; margin-top: 0.5em;}")
        #-
        self.layoutDisplayHelpFocus = QtWidgets.QGridLayout()
        self.layoutDisplayHelpFocus.setObjectName("layoutDisplayHelpFocus")
        self.groupBoxdisplayHelpFocus.setLayout(self.layoutDisplayHelpFocus)
        self.layout_tab_widget_Association.addWidget(self.groupBoxdisplayHelpFocus, 2, 0, 1, 1)
        #-
        mText = "" 
        _Listkeys   = [ "typeWidget",       "textWidget", "nameWidget", "aligneWidget", "wordWrap" ]
        _ListValues = [ QtWidgets.QLabel(), mText,        "label_" ,     QtCore.Qt.AlignCenter, True ]
        dicParamLabel = dict(zip(_Listkeys, _ListValues))
        self.zoneDisplayHelpFocus = genereLabelWithDict( dicParamLabel )
        self.zoneDisplayHelpFocus.setTextFormat(Qt.MarkdownText)        
        self.layoutDisplayHelpFocus.addWidget( self.zoneDisplayHelpFocus, 0, 1)
        self.zoneDisplayHelpFocus.setAlignment( Qt.AlignJustify | Qt.AlignVCenter )
        #-
        #=====================================
        # [ == scrolling HELP == ]
        self.scroll_bar_help_AttributsModeleCategorie = QtWidgets.QScrollArea() 
        self.scroll_bar_help_AttributsModeleCategorie.setStyleSheet("QScrollArea { border: 0px solid red; margin-left: 10px; margin-right: 10px;}")
        self.scroll_bar_help_AttributsModeleCategorie.setWidgetResizable(True)
        self.scroll_bar_help_AttributsModeleCategorie.setWidget(self.groupBoxdisplayHelpFocus)
        self.scroll_bar_help_AttributsModeleCategorie.setContentsMargins(50, 0, 50, 0)
        self.layout_tab_widget_Association.addWidget(self.scroll_bar_help_AttributsModeleCategorie, 2, 0)
        #=====================================
        #=====================================
        self.groupBoxdisplayHelpFocus.setVisible(False)

        #Liste ATTRIBUTS modeles / catégories
        self.groupBoxAttributsModeleCategorie.setStyleSheet("QGroupBox { border: 0px solid green}")
        #-
        self.layoutAttributsModeleCategorie = QtWidgets.QGridLayout()
        self.layoutAttributsModeleCategorie.setContentsMargins(0, 0, 0, 0)
        self.layoutAttributsModeleCategorie.setObjectName("layoutAttributsModeleCategorie")
        self.groupBoxAttributsModeleCategorie.setLayout(self.layoutAttributsModeleCategorie)
        self.layout_tab_widget_Association.addWidget(self.groupBoxAttributsModeleCategorie, 2, 1)

        #=====================================
        # [ == scrolling Attributs == ]
        self.scroll_bar_AttributsModeleCategorie = QtWidgets.QScrollArea() 
        self.scroll_bar_AttributsModeleCategorie.setStyleSheet("QScrollArea { border: 0px solid red; margin-left: 10px; margin-right: 10px;}")
        self.scroll_bar_AttributsModeleCategorie.setWidgetResizable(True)
        self.scroll_bar_AttributsModeleCategorie.setWidget(self.groupBoxAttributsModeleCategorie)
        self.layout_tab_widget_Association.addWidget(self.scroll_bar_AttributsModeleCategorie, 2, 1)
        #=====================================
        #=====================================
        
        # [ == création des attributs == ]
        genereAttributs( self, self.mapping_template_categories, self.layoutAttributsModeleCategorie, 'initialiseAttributsModeleCategorie', self.groupBoxdisplayHelpFocus, self.zoneDisplayHelpFocus )
        afficheAttributs( self, self.groupBoxAttributsModeleCategorie, self.mapping_template_categories, False ) 
        # [ == création des attributs == ]

        #Button Add
        #-
        self.buttonSaveAttribModeleCategorie = QtWidgets.QToolButton()
        self.buttonSaveAttribModeleCategorie.setObjectName("buttonSaveAttribModeleCategorie")
        self.buttonSaveAttribModeleCategorie.setIcon(QtGui.QIcon(os.path.dirname(__file__)+"\\icons\\general\\save.svg"))
        self.buttonSaveAttribModeleCategorie.setToolTip( returnbuttonSaveAttribCategorieToolTip("catégorie", "modèle") ) 

        self.buttonSaveAttribModeleCategorie.clicked.connect(lambda : self.functionUpdateModeleCategorie("buttonSaveAttribModeleCategorie"))
        #Button Add
        #------

        #-
        self.groupBox_buttons = QtWidgets.QGroupBox()
        self.groupBox_buttons.setObjectName("groupBox_buttons")
        self.groupBox_buttons.setStyleSheet("QGroupBox { border: 0px solid blue }")
        #-
        self.layout_groupBox_buttons = QtWidgets.QGridLayout()
        self.layout_groupBox_buttons.setContentsMargins(0, 0, 0, 0)
        self.groupBox_buttons.setLayout(self.layout_groupBox_buttons)
        self.layout_tab_widget_Association.addWidget(self.groupBox_buttons,4 ,0 , 1, 2)
        #-
        self.layout_groupBox_buttons.setColumnStretch(0, 3)
        self.layout_groupBox_buttons.setColumnStretch(1, 1)
        self.layout_groupBox_buttons.setColumnStretch(2, 1)
        self.layout_groupBox_buttons.setColumnStretch(3, 1)
        self.layout_groupBox_buttons.setColumnStretch(4, 1)
        self.layout_groupBox_buttons.setColumnStretch(5, 1)
        self.layout_groupBox_buttons.setColumnStretch(6, 1)
        #-
        #----------
        self.pushButtonAnnuler = QtWidgets.QPushButton()
        self.pushButtonAnnuler.setObjectName("pushButtonAnnuler")
        self.pushButtonAnnuler.clicked.connect(self.DialogCreateTemplate.reject)
        self.layout_groupBox_buttons.addWidget(self.pushButtonAnnuler, 1, 2, QtCore.Qt.AlignTop)
        #--
        self.layout_groupBox_buttons.addWidget(self.buttonSaveAttribModeleCategorie, 1, 5, 1, 3, Qt.AlignTop)
        #----------
        self.DialogCreateTemplate.setWindowTitle(QtWidgets.QApplication.translate("plume_main", "PLUME (Metadata storage in PostGreSQL") + "  (" + str(returnVersion()) + ")")
        self.zMessTitle    =  QtWidgets.QApplication.translate("CreateTemplate_ui", "model management", None)   #Gestion des modèles
        self.label_2.setText(self.zMessTitle)
        self.pushButtonAnnuler.setText(QtWidgets.QApplication.translate("CreateTemplate_ui", "Cancel", None))
        # 
        afficheLabelAndLibelle(self, False, False, False, False)
        self.buttonSaveOutVersIn.setEnabled(False)
        self.buttonReinitOutVersIn.setEnabled(False)
        #  Onglet ASSOCIATION
        #============================================================
        
        #============================================================
        #  Onglet RESSOURCE
        #=====================================
        #--
        self.voletsRessource = QtWidgets.QToolBox()
        #====
        #====
        # Zone MODELE
        self.zoneModele       = QWidget()
        self.layoutZoneModele = QGridLayout()
        self.layoutZoneModele.setRowStretch(0, 6)
        self.layoutZoneModele.setRowStretch(1, 6)
        self.layoutZoneModele.setRowStretch(2, 1)
        self.zoneModele.setLayout(self.layoutZoneModele)
        #--
        #------ TREEVIEW   
        self.mTreeListeRessourceModele = TREEVIEWMODELE()
        self.layoutZoneModele.addWidget(self.mTreeListeRessourceModele, 0, 0)
        #-
        self.mTreeListeRessourceModele.clear()
        #------ TEMPORAIRE 
        #------
        #------ DATA template 
        mKeySql = queries.query_read_meta_template()
        r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self.Dialog.mConnectEnCours, mKeySql, optionRetour = "fetchall")
        self.mListTemplates = [row[0] for row in r]
        listeModeleCol1, listeModeleCol2 = returnList_Id_Label( self.mListTemplates )
        self.modeleActif = listeModeleCol1[0] if len(listeModeleCol1) > 0  else "" #Pour la première initialisation 

        self.voletsRessource.addItem(self.zoneModele, QtWidgets.QApplication.translate("CreateTemplate_ui", "List of models"))
        #====
        #=====================================
         #Liste ATTRIBUTS modeles
        self.groupBoxHelpAttributsModele = QtWidgets.QGroupBox()
        self.groupBoxHelpAttributsModele.setObjectName("groupBoxHelpAttributsModele")
        self.groupBoxHelpAttributsModele.setStyleSheet("QGroupBox { border: 0px solid blue;}")
        self.groupBoxHelpAttributsModele.setContentsMargins(0, 0, 0, 0)
        #-
        self.layoutHelpAttributsModele = QtWidgets.QGridLayout()
        self.layoutHelpAttributsModele.setObjectName("layoutHelpAttributsModele")
        self.layoutHelpAttributsModele.setColumnStretch(0, 1)
        self.layoutHelpAttributsModele.setColumnStretch(1, 1)
        #-
        self.groupBoxHelpAttributsModele.setLayout(self.layoutHelpAttributsModele)
        self.layoutZoneModele.addWidget(self.groupBoxHelpAttributsModele, 1, 0)
        #=====================================
        # [ == scrolling HELP et Attributs == ]
        self.scroll_bar_help_AttributsModele = QtWidgets.QScrollArea() 
        self.scroll_bar_help_AttributsModele.setStyleSheet("QScrollArea { border: 0px solid red;}")
        self.scroll_bar_help_AttributsModele.setWidgetResizable(True)
        self.scroll_bar_help_AttributsModele.setWidget(self.groupBoxHelpAttributsModele)
        self.layoutZoneModele.addWidget(self.scroll_bar_help_AttributsModele, 1, 0)
        #=====================================
        #=====================================

        #=====================================
        self.groupBoxAttributsModele = QtWidgets.QGroupBox()
        self.groupBoxAttributsModele.setObjectName("groupBoxAttributsModele")
        self.groupBoxAttributsModele.setStyleSheet("QGroupBox { border: 0px solid yellow;}")
        self.groupBoxAttributsModele.setContentsMargins(0, 0, 0, 0)
        #-
        self.layoutAttributsModele = QtWidgets.QGridLayout()
        self.layoutAttributsModele.setObjectName("layoutAttributsModele")
        #-
        self.layoutAttributsModele.setColumnStretch(0, 1)
        self.layoutAttributsModele.setColumnStretch(1, 4)
        self.groupBoxAttributsModele.setLayout(self.layoutAttributsModele)
        self.layoutHelpAttributsModele.addWidget(self.groupBoxAttributsModele, 0, 1)
        #=====================================
        # [ == scrolling Attributs == ]
        self.scroll_bar_AttributsModele = QtWidgets.QScrollArea() 
        self.scroll_bar_AttributsModele.setStyleSheet("QScrollArea { border: 0px solid red;}")
        self.scroll_bar_AttributsModele.setWidgetResizable(True)
        self.scroll_bar_AttributsModele.setWidget(self.groupBoxAttributsModele)
        self.layoutHelpAttributsModele.addWidget(self.scroll_bar_AttributsModele, 0, 1)
        #Affichage de l'aide pour les attributs
        self.groupBoxdisplayHelpFocusAttributsModele = QtWidgets.QGroupBox()
        self.groupBoxdisplayHelpFocusAttributsModele.setObjectName("groupBoxdisplayHelpFocusAttributsModele")
        self.groupBoxdisplayHelpFocusAttributsModele.setContentsMargins(0, 0, 0, 0)
        self.groupBoxdisplayHelpFocusAttributsModele.setStyleSheet("QGroupBox { background: qlineargradient(x1: 0, y1: 0, x2: 0.5, y2: 0.5, stop: 0 #958B62, stop: 1 white); \
                                                                 border-radius: 9px; margin-top: 0.5em;}")
        #-
        self.layoutDisplayHelpFocusAttributsModele = QtWidgets.QGridLayout()
        self.layoutDisplayHelpFocusAttributsModele.setObjectName("layoutDisplayHelpFocusAttributsModele")
        self.groupBoxdisplayHelpFocusAttributsModele.setLayout(self.layoutDisplayHelpFocusAttributsModele)
        self.layoutHelpAttributsModele.addWidget(self.groupBoxdisplayHelpFocusAttributsModele, 0, 0)
        #-
        mText = "" 
        _Listkeys   = [ "typeWidget",       "textWidget", "nameWidget", "aligneWidget", "wordWrap" ]
        _ListValues = [ QtWidgets.QLabel(), mText,        "label_" ,     QtCore.Qt.AlignCenter, True ]
        dicParamLabel = dict(zip(_Listkeys, _ListValues))
        self.zoneDisplayHelpFocusAttributsModele = genereLabelWithDict( dicParamLabel )
        self.zoneDisplayHelpFocusAttributsModele.setTextFormat(Qt.MarkdownText)        
        self.layoutDisplayHelpFocusAttributsModele.addWidget( self.zoneDisplayHelpFocusAttributsModele, 0, 0)
        self.zoneDisplayHelpFocusAttributsModele.setAlignment( Qt.AlignJustify | Qt.AlignVCenter )
        #-
        #=====================================
        # [ == scrolling HELP == ]
        self.scroll_bar_help_displayHelpFocusAttributsModele = QtWidgets.QScrollArea() 
        self.scroll_bar_help_displayHelpFocusAttributsModele.setStyleSheet("QScrollArea { border: 0px solid red;}")
        self.scroll_bar_help_displayHelpFocusAttributsModele.setWidgetResizable(True)
        self.scroll_bar_help_displayHelpFocusAttributsModele.setWidget(self.groupBoxdisplayHelpFocusAttributsModele)
        self.layoutHelpAttributsModele.addWidget(self.scroll_bar_help_displayHelpFocusAttributsModele, 0, 0)
        #=====================================
        #=====================================
        self.groupBoxdisplayHelpFocusAttributsModele.setVisible(False)

        #=====================================
        # [ == création des attributs == ]
        genereAttributs( self, self.mapping_templates, self.layoutAttributsModele, 'initialiseAttributsModele', self.groupBoxdisplayHelpFocusAttributsModele, self.zoneDisplayHelpFocusAttributsModele )
        afficheAttributs( self, self.groupBoxAttributsModele, self.mapping_templates, False ) 
        # [ == création des attributs == ]
        #------
        self.mTreeListeRessourceModele.afficheMODELE(self, listeModeleCol1, listeModeleCol2)
        self.layoutAttributsModele.setRowStretch(self.layoutAttributsModele.rowCount(), 1) #Permet de pousser vers le haut les attributs
        #------
        #Button Add
        self.groupBoxAttributsModeleButton = QtWidgets.QGroupBox()
        self.groupBoxAttributsModeleButton.setObjectName("groupBoxAttributsModeleButton")
        self.groupBoxAttributsModeleButton.setStyleSheet("QGroupBox { border: 0px solid yellow;}")
        self.groupBoxAttributsModeleButton.setContentsMargins(0, 0, 0, 0)
        #-
        self.layoutAttributsModeleButton = QtWidgets.QGridLayout()
        self.layoutAttributsModeleButton.setObjectName("layoutAttributsModeleButton")
        self.layoutAttributsModeleButton.setContentsMargins(0, 0, 0, 0)
        self.groupBoxAttributsModeleButton.setLayout(self.layoutAttributsModeleButton)
        #-
        self.layoutAttributsModeleButton.setColumnStretch(0, 4)
        self.layoutAttributsModeleButton.setColumnStretch(1, 1)
        self.layoutAttributsModeleButton.setColumnStretch(2, 3)
        self.layoutZoneModele.addWidget(self.groupBoxAttributsModeleButton, 2, 0)
        #------
        self.buttonAddModele = QtWidgets.QToolButton()
        self.buttonAddModele.setObjectName("buttonAddModele")
        self.buttonAddModele.setIcon(QtGui.QIcon(os.path.dirname(__file__)+"\\icons\\general\\save.svg"))
        mbuttonAddToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Modify a model as well as these attributes.", None)
        self.buttonAddModele.setToolTip(mbuttonAddToolTip)
        self.buttonAddModele.clicked.connect(lambda : self.functionUpdateModele())
        self.layoutAttributsModeleButton.addWidget(self.buttonAddModele, 0, 2, Qt.AlignCenter)
        self.buttonAddModele.setVisible(False)
        #Button Add
        #------

        #====
        #====
        # Zone CATEGORIES
        self.zoneCategorie       = QWidget()
        self.layoutZoneCategorie = QtWidgets.QGridLayout()
        self.layoutZoneCategorie.setRowStretch(0, 6)
        self.layoutZoneCategorie.setRowStretch(1, 6)
        self.layoutZoneCategorie.setRowStretch(2, 1)
        self.zoneCategorie.setLayout(self.layoutZoneCategorie)
        #Liste Categories
        #------ TREEVIEW CATEGORIES
        self.mTreeListeRessourceCategorie = TREEVIEWCATEGORIE()
        self.layoutZoneCategorie.addWidget(self.mTreeListeRessourceCategorie)
        #-
        self.mTreeListeRessourceCategorie.clear()

        mKeySql = queries.query_read_meta_categorie()
        r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self.Dialog.mConnectEnCours, mKeySql, optionRetour = "fetchall")
        self.mListCategories = [row[0] for row in r]

        if len(self.mListCategories)  > 0 : 
           self.listeRessourceCategorie = returnListRessourceCategorie( self, self.mListCategories )
           self.categorieActif = self.listeRessourceCategorie[0] if len(self.listeRessourceCategorie) > 0  else "" #Pour la première initialisation 
        else :   
           self.listeRessourceCategorie = []
           self.categorieActif = ""

        self.voletsRessource.addItem(self.zoneCategorie, QtWidgets.QApplication.translate("CreateTemplate_ui", "List of Categories"))
        #====

        #=====================================
         #Liste ATTRIBUTS catégories
        self.groupBoxHelpAttributsCategories = QtWidgets.QGroupBox()
        self.groupBoxHelpAttributsCategories.setObjectName("groupBoxHelpAttributsCategories")
        self.groupBoxHelpAttributsCategories.setStyleSheet("QGroupBox { border: 0px solid blue;}")
        #-
        self.layoutHelpAttributsCategorie = QtWidgets.QGridLayout()
        self.layoutHelpAttributsCategorie.setObjectName("layoutAttributsCategories")
        self.layoutHelpAttributsCategorie.setColumnStretch(0, 1)
        self.layoutHelpAttributsCategorie.setColumnStretch(1, 1)
        self.groupBoxHelpAttributsCategories.setLayout(self.layoutHelpAttributsCategorie)
        self.layoutZoneCategorie.addWidget(self.groupBoxHelpAttributsCategories, 1, 0)
        #=====================================
        self.groupBoxAttributsCategorie = QtWidgets.QGroupBox()
        self.groupBoxAttributsCategorie.setObjectName("groupBoxAttributsCategorie")
        self.groupBoxAttributsCategorie.setStyleSheet("QGroupBox { border: 0px solid yellow;}")
        #-
        self.layoutAttributsCategorie = QtWidgets.QGridLayout()
        self.layoutAttributsCategorie.setObjectName("layoutAttributsCategorie")
        #-
        self.layoutAttributsCategorie.setColumnStretch(0, 1)
        self.layoutAttributsCategorie.setColumnStretch(1, 4)
        self.groupBoxAttributsCategorie.setLayout(self.layoutAttributsCategorie)
        self.layoutHelpAttributsCategorie.addWidget(self.groupBoxAttributsCategorie, 0, 1)
        #=====================================
        # [ == scrolling Attributs == ]
        self.scroll_bar_AttributsCategorie = QtWidgets.QScrollArea() 
        self.scroll_bar_AttributsCategorie.setStyleSheet("QScrollArea { border: 0px solid red;}")
        self.scroll_bar_AttributsCategorie.setWidgetResizable(True)
        self.scroll_bar_AttributsCategorie.setWidget(self.groupBoxAttributsCategorie)
        self.layoutHelpAttributsCategorie.addWidget(self.scroll_bar_AttributsCategorie, 0, 1)
        #Affichage de l'aide pour les attributs
        self.groupBoxdisplayHelpFocusAttributsCategorie = QtWidgets.QGroupBox()
        self.groupBoxdisplayHelpFocusAttributsCategorie.setObjectName("groupBoxdisplayHelpFocusAttributsCategorie")
        
        self.groupBoxdisplayHelpFocusAttributsCategorie.setStyleSheet("QGroupBox { background: qlineargradient(x1: 0, y1: 0, x2: 0.5, y2: 0.5, stop: 0 #958B62, stop: 1 white); \
                                                                 border-radius: 9px; margin-top: 0.5em;}")
        #-
        self.layoutDisplayHelpFocusAttributsCategorie = QtWidgets.QGridLayout()
        self.layoutDisplayHelpFocusAttributsCategorie.setObjectName("layoutDisplayHelpFocusAttributsCategorie")
        self.groupBoxdisplayHelpFocusAttributsCategorie.setLayout(self.layoutDisplayHelpFocusAttributsCategorie)
        self.layoutHelpAttributsCategorie.addWidget(self.groupBoxdisplayHelpFocusAttributsCategorie, 0, 0)
        #-
        mText = "" 
        _Listkeys   = [ "typeWidget",       "textWidget", "nameWidget", "aligneWidget", "wordWrap" ]
        _ListValues = [ QtWidgets.QLabel(), mText,        "label_" ,     QtCore.Qt.AlignCenter, True ]
        dicParamLabel = dict(zip(_Listkeys, _ListValues))
        self.zoneDisplayHelpFocusAttributsCategorie = genereLabelWithDict( dicParamLabel )
        self.zoneDisplayHelpFocusAttributsCategorie.setTextFormat(Qt.MarkdownText)        
        self.layoutDisplayHelpFocusAttributsCategorie.addWidget( self.zoneDisplayHelpFocusAttributsCategorie, 0, 0)
        self.zoneDisplayHelpFocusAttributsCategorie.setAlignment( Qt.AlignJustify | Qt.AlignVCenter )
        #-
        #=====================================
        # [ == scrolling HELP == ]
        self.scroll_bar_help_displayHelpFocusAttributsCategorie = QtWidgets.QScrollArea() 
        self.scroll_bar_help_displayHelpFocusAttributsCategorie.setStyleSheet("QScrollArea { border: 0px solid red;}")
        self.scroll_bar_help_displayHelpFocusAttributsCategorie.setWidgetResizable(True)
        self.scroll_bar_help_displayHelpFocusAttributsCategorie.setWidget(self.groupBoxdisplayHelpFocusAttributsCategorie)
        self.layoutHelpAttributsCategorie.addWidget(self.scroll_bar_help_displayHelpFocusAttributsCategorie, 0, 0)
        #=====================================
        #=====================================
        self.groupBoxdisplayHelpFocusAttributsCategorie.setVisible(False)
      
        #=====================================
        # [ == création des attributs == ]
        genereAttributs( self, self.mapping_categories, self.layoutAttributsCategorie, 'initialiseAttributsCategorie', self.groupBoxdisplayHelpFocusAttributsCategorie, self.zoneDisplayHelpFocusAttributsCategorie )
        afficheAttributs( self, self.groupBoxAttributsCategorie, self.mapping_categories, False ) 
        # [ == création des attributs == ]
        #------
        self.mTreeListeRessourceCategorie.afficheCATEGORIE(self, self.listeRessourceCategorie)
        
        self.layoutAttributsCategorie.setRowStretch(self.layoutAttributsCategorie.rowCount(), 1) #Permet de pousser vers le haut les attributs
        
        #------
        #Button Add
        self.groupBoxAttributsCategorieButton = QtWidgets.QGroupBox()
        self.groupBoxAttributsCategorieButton.setObjectName("groupBoxAttributsCategorieButton")
        self.groupBoxAttributsCategorieButton.setStyleSheet("QGroupBox { border: 0px solid yellow;}")
        self.groupBoxAttributsCategorieButton.setContentsMargins(0, 0, 0, 0)
        #-
        self.layoutAttributsCategorieButton = QtWidgets.QGridLayout()
        self.layoutAttributsCategorieButton.setObjectName("layoutAttributsCategorieButton")
        self.layoutAttributsCategorieButton.setContentsMargins(0, 0, 0, 0)
        self.groupBoxAttributsCategorieButton.setLayout(self.layoutAttributsCategorieButton)
        #-
        self.layoutAttributsCategorieButton.setColumnStretch(0, 4)
        self.layoutAttributsCategorieButton.setColumnStretch(1, 1)
        self.layoutAttributsCategorieButton.setColumnStretch(2, 3)
        self.layoutZoneCategorie.addWidget(self.groupBoxAttributsCategorieButton, 2, 0)
        #------
        self.buttonAddCategorie = QtWidgets.QToolButton()
        self.buttonAddCategorie.setObjectName("buttonAddCategorie")
        self.buttonAddCategorie.setIcon(QtGui.QIcon(os.path.dirname(__file__)+"\\icons\\general\\save.svg"))
        mbuttonAddToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Modify a category as well as these attributes.", None)
        self.buttonAddCategorie.setToolTip(mbuttonAddToolTip)
        self.buttonAddCategorie.clicked.connect(lambda : self.functionUpdateCategorie())
        self.layoutAttributsCategorieButton.addWidget(self.buttonAddCategorie, 0, 2, Qt.AlignCenter)
        self.buttonAddCategorie.setVisible(False)
        #Button Add
        #------

        #====
        #====
        # Zone ONGLETS
        self.zoneOnglet       = QWidget()
        self.layoutZoneOnglet = QtWidgets.QGridLayout()  
        self.layoutZoneOnglet.setRowStretch(0, 6)
        self.layoutZoneOnglet.setRowStretch(1, 6)
        self.layoutZoneOnglet.setRowStretch(2, 1)
        self.zoneOnglet.setLayout(self.layoutZoneOnglet)
        #Liste Onglets
        #------ Déclare TREEVIEW
        self.mTreeListeRessourceOnglet = TREEVIEWONGLET()
        #-
        #------ TREEVIEW ONGLETS
        self.layoutZoneOnglet.addWidget(self.mTreeListeRessourceOnglet)
        #-
        self.mTreeListeRessourceOnglet.clear()

        if len(self.mListTabs)  > 0 : 
           listeOngletCol1, listeOngletCol2 = returnList_Id_Label( self.mListTabs )
           self.ongleteActif = listeOngletCol1[0] if len(listeOngletCol1) > 0  else "" #Pour la première initialisation 
        else :   
           listeOngletCol1, listeOngletCol2 = [], []
           self.ongleteActif = ""

        self.voletsRessource.addItem(self.zoneOnglet, QtWidgets.QApplication.translate("CreateTemplate_ui", "List of Onglets"))

        #=====================================
         #Liste ATTRIBUTS Onglets
        self.groupBoxHelpAttributsOnglets = QtWidgets.QGroupBox()
        self.groupBoxHelpAttributsOnglets.setObjectName("groupBoxHelpAttributsOnglets")
        self.groupBoxHelpAttributsOnglets.setStyleSheet("QGroupBox { border: 0px solid blue;}")
        #-
        self.layoutHelpAttributsOnglet = QtWidgets.QGridLayout()
        self.layoutHelpAttributsOnglet.setObjectName("layoutAttributsOnglets")
        self.layoutHelpAttributsOnglet.setColumnStretch(0, 1)
        self.layoutHelpAttributsOnglet.setColumnStretch(1, 1)
        self.groupBoxHelpAttributsOnglets.setLayout(self.layoutHelpAttributsOnglet)
        self.layoutZoneOnglet.addWidget(self.groupBoxHelpAttributsOnglets, 1, 0)
        #=====================================
        self.groupBoxAttributsOnglet = QtWidgets.QGroupBox()
        self.groupBoxAttributsOnglet.setObjectName("groupBoxAttributsOnglet")
        self.groupBoxAttributsOnglet.setStyleSheet("QGroupBox { border: 0px solid yellow;}")
        #-
        self.layoutAttributsOnglet = QtWidgets.QGridLayout()
        self.layoutAttributsOnglet.setObjectName("layoutAttributsOnglet")
        #-
        self.layoutAttributsOnglet.setColumnStretch(0, 1)
        self.layoutAttributsOnglet.setColumnStretch(1, 4)
        self.groupBoxAttributsOnglet.setLayout(self.layoutAttributsOnglet)
        self.layoutHelpAttributsOnglet.addWidget(self.groupBoxAttributsOnglet, 0, 1)
        #=====================================
        # [ == scrolling Attributs == ]
        self.scroll_bar_AttributsOnglet = QtWidgets.QScrollArea() 
        self.scroll_bar_AttributsOnglet.setStyleSheet("QScrollArea { border: 0px solid red;}")
        self.scroll_bar_AttributsOnglet.setWidgetResizable(True)
        self.scroll_bar_AttributsOnglet.setWidget(self.groupBoxAttributsOnglet)
        self.layoutHelpAttributsOnglet.addWidget(self.scroll_bar_AttributsOnglet, 0, 1)
        #Affichage de l'aide pour les attributs
        self.groupBoxdisplayHelpFocusAttributsOnglet = QtWidgets.QGroupBox()
        self.groupBoxdisplayHelpFocusAttributsOnglet.setObjectName("groupBoxdisplayHelpFocusAttributsOnglet")
        
        self.groupBoxdisplayHelpFocusAttributsOnglet.setStyleSheet("QGroupBox { background: qlineargradient(x1: 0, y1: 0, x2: 0.5, y2: 0.5, stop: 0 #958B62, stop: 1 white); \
                                                                 border-radius: 9px; margin-top: 0.5em;}")
        #-
        self.layoutDisplayHelpFocusAttributsOnglet = QtWidgets.QGridLayout()
        self.layoutDisplayHelpFocusAttributsOnglet.setObjectName("layoutDisplayHelpFocusAttributsOnglet")
        self.groupBoxdisplayHelpFocusAttributsOnglet.setLayout(self.layoutDisplayHelpFocusAttributsOnglet)
        self.layoutHelpAttributsOnglet.addWidget(self.groupBoxdisplayHelpFocusAttributsOnglet, 0, 0)
        #-
        mText = "" 
        _Listkeys   = [ "typeWidget",       "textWidget", "nameWidget", "aligneWidget", "wordWrap" ]
        _ListValues = [ QtWidgets.QLabel(), mText,        "label_" ,     QtCore.Qt.AlignCenter, True ]
        dicParamLabel = dict(zip(_Listkeys, _ListValues))
        self.zoneDisplayHelpFocusAttributsOnglet = genereLabelWithDict( dicParamLabel )
        self.zoneDisplayHelpFocusAttributsOnglet.setTextFormat(Qt.MarkdownText)        
        self.layoutDisplayHelpFocusAttributsOnglet.addWidget( self.zoneDisplayHelpFocusAttributsOnglet, 0, 0)
        self.zoneDisplayHelpFocusAttributsOnglet.setAlignment( Qt.AlignJustify | Qt.AlignVCenter )
        #-
        #=====================================
        # [ == scrolling HELP == ]
        self.scroll_bar_help_displayHelpFocusAttributsOnglet = QtWidgets.QScrollArea() 
        self.scroll_bar_help_displayHelpFocusAttributsOnglet.setStyleSheet("QScrollArea { border: 0px solid red;}")
        self.scroll_bar_help_displayHelpFocusAttributsOnglet.setWidgetResizable(True)
        self.scroll_bar_help_displayHelpFocusAttributsOnglet.setWidget(self.groupBoxdisplayHelpFocusAttributsOnglet)
        self.layoutHelpAttributsOnglet.addWidget(self.scroll_bar_help_displayHelpFocusAttributsOnglet, 0, 0)
        #=====================================
        #=====================================
        self.groupBoxdisplayHelpFocusAttributsOnglet.setVisible(False)

        #=====================================
        # [ == création des attributs == ]
        genereAttributs( self, self.mapping_tabs, self.layoutAttributsOnglet, 'initialiseAttributsOnglet', self.groupBoxdisplayHelpFocusAttributsOnglet, self.zoneDisplayHelpFocusAttributsOnglet )
        afficheAttributs( self, self.groupBoxAttributsOnglet, self.mapping_tabs, False ) 
        # [ == création des attributs == ]

        self.mTreeListeRessourceOnglet.afficheONGLET(self, listeOngletCol1, listeOngletCol2)
        #=====================================
        
        self.layoutAttributsOnglet.setRowStretch(self.layoutAttributsOnglet.rowCount(), 1) #Permet de pousser vers le haut les attributs
        
        #------
        #Button Add
        self.groupBoxAttributsOngletButton = QtWidgets.QGroupBox()
        self.groupBoxAttributsOngletButton.setObjectName("groupBoxAttributsOngletButton")
        self.groupBoxAttributsOngletButton.setStyleSheet("QGroupBox { border: 0px solid yellow;}")
        self.groupBoxAttributsOngletButton.setContentsMargins(0, 0, 0, 0)
        #-
        self.layoutAttributsOngletButton = QtWidgets.QGridLayout()
        self.layoutAttributsOngletButton.setObjectName("layoutAttributsOngletButton")
        self.layoutAttributsOngletButton.setContentsMargins(0, 0, 0, 0)
        self.groupBoxAttributsOngletButton.setLayout(self.layoutAttributsOngletButton)
        #-
        self.layoutAttributsOngletButton.setColumnStretch(0, 4)
        self.layoutAttributsOngletButton.setColumnStretch(1, 1)
        self.layoutAttributsOngletButton.setColumnStretch(2, 3)
        self.layoutZoneOnglet.addWidget(self.groupBoxAttributsOngletButton, 2, 0)
        #------
        self.buttonAddOnglet = QtWidgets.QToolButton()
        self.buttonAddOnglet.setObjectName("buttonAddOnglet")
        self.buttonAddOnglet.setIcon(QtGui.QIcon(os.path.dirname(__file__)+"\\icons\\general\\save.svg"))
        mbuttonAddToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Modify a tab as well as these attributes.", None)
        self.buttonAddOnglet.setToolTip(mbuttonAddToolTip)
        self.buttonAddOnglet.clicked.connect(lambda : self.functionUpdateOnglet())
        self.layoutAttributsOngletButton.addWidget(self.buttonAddOnglet, 0, 2, Qt.AlignCenter)
        self.buttonAddOnglet.setVisible(False)
        #Button Add
        #------

        #====
        #====
        self.layout_tab_widget_Ressource.addWidget(self.voletsRessource) 
        #====
        #====

        #  Onglet RESSOURCE
        #============================================================

    #===============================              
    def ihmsPlumeASSOCIATION(self, _selfCreateTemplate ) : 
        QApplication.setOverrideCursor( QCursor( Qt.WaitCursor ) )

        self._selfCreateTemplate    = _selfCreateTemplate
        if self.comboListeModeleCategorie.currentIndex() == -1 : return
        mItemClicLibelleAssociation = self.modelComboListeModeleCategorie.item(self.comboListeModeleCategorie.currentIndex(),0).text()    
        mItemClicAssociation        = self.modelComboListeModeleCategorie.item(self.comboListeModeleCategorie.currentIndex(),1).text()
        
        self.groupBoxdisplayHelpFocus.setVisible(False)
        self.zoneDisplayHelpFocus.setText("")
        
        if mItemClicLibelleAssociation == "" : 
           self.mTreeListeCategorieIn.clear()
           self.mTreeListeCategorieOut.clear()
           self.mTreeListeCategorieIn.setVisible(False)
           self.mTreeListeCategorieOut.setVisible(False)
           afficheAttributs( self, self.groupBoxAttributsModeleCategorie, self.mapping_template_categories, False )
           # 
           afficheLabelAndLibelle(self, False, False, False, False)
           return

        self.mTreeListeCategorieIn.setVisible(True)
        self.mTreeListeCategorieOut.setVisible(True)
        self.modeleAssociationActif = mItemClicAssociation
        
        #=== Nécessaire pour récupérer les valeurs initiales et/ ou sauvegardées == Cat Utilisées et Non Utilisées==              
        with self._selfCreateTemplate.Dialog.safe_pg_connection("continue") :
           #------ DATA template_categories 
           mKeySql = queries.query_read_meta_template_categories()
           r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self._selfCreateTemplate.Dialog.mConnectEnCours, mKeySql, optionRetour = "fetchall")
           self.mListTemplateCategories = [row[0] for row in r]
        self.dicInVersOutDesign = {} # Pour la gestion des double clic et la regénération des données en entrée de l'algo
        self.dicOutVersInDesign = {} # Pour la gestion des double clic et la regénération des données en entrée de l'algo
        #=== Nécessaire pour récupérer les valeurs initiales et/ ou sauvegardées
        
        self.listCategorieOut, self.listCategorieIn = ventileCatInCatOut(self, mItemClicAssociation, self.mListTemplateCategories, self.mListCategories)

        self.mTreeListeCategorieIn.clear()
        self.mTreeListeCategorieOut.clear()
        self.mTreeListeCategorieIn.affiche_CAT_IN_OUT(  self, mItemClicAssociation, self.mTreeListeCategorieIn, self.mTreeListeCategorieOut, action = True, header = self._origineHeaderLabelsIn)
        self.mTreeListeCategorieOut.affiche_CAT_IN_OUT( self, mItemClicAssociation, self.mTreeListeCategorieIn, self.mTreeListeCategorieOut,                header = self._origineHeaderLabelsOut) # Uniquement pour instancier OneShot
        #Efface les attributs
        afficheAttributs( self, self.groupBoxAttributsModeleCategorie, self.mapping_template_categories, False )
        # 
        afficheLabelAndLibelle(self, True, True, True, False)
        self.buttonSaveOutVersIn.setEnabled(False)
        self.buttonReinitOutVersIn.setEnabled(False)

        QApplication.setOverrideCursor( QCursor( Qt.ArrowCursor ) )
        return
    
    #===============================              
    def functionChangeTab(self, mIndex):
       if mIndex != -1 :
          if mIndex == 0 :
             # Gestion des flags pour maj si new modele, catégorie, onglet
             _cont = False  
             if (self.flagNewModele or self.flagNewCategorie or self.flagNewOnglet) : _cont = True
             self.flagNewModele, self.flagNewOnglet, self.flagNewCategorie = False, False, False
             if not _cont : return  
             # Gestion des flags pour maj si new modele, catégorie, onglet

             with self.Dialog.safe_pg_connection("continue") :
                #------ DATA template 
                self.comboListeModeleCategorie.clear()
                mKeySql = queries.query_read_meta_template()
                r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self.Dialog.mConnectEnCours, mKeySql, optionRetour = "fetchall")
                self.mListTemplates = [row[0] for row in r]
             with self.Dialog.safe_pg_connection("continue") :
                #------ DATA categories 
                mKeySql = queries.query_read_meta_categorie()
                r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self.Dialog.mConnectEnCours, mKeySql, optionRetour = "fetchall")
                self.mListCategories = [row[0] for row in r]
         
                listeAssociationCol1, listeAssociationCol2 = returnList_Id_Label( self.mListTemplates )
                self.modeleAssociationActif = listeAssociationCol1[0] if len(listeAssociationCol1) > 0 else "" #Pour la première initialisation 
             with self.Dialog.safe_pg_connection("continue") :
                #------ DATA Tab 
                mKeySql = queries.query_read_meta_tab()
                r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self.Dialog.mConnectEnCours, mKeySql, optionRetour = "fetchall")
                self.mListTabs = [row[0] for row in r]

             #------ DATA 
             self.modelComboListeModeleCategorie = QStandardItemModel()
             listeAssociationCol1 = list(reversed(listeAssociationCol1))
             listeAssociationCol1.insert(0,"")
             listeAssociationCol2 = list(reversed(listeAssociationCol2))
             listeAssociationCol2.insert(0,"")

             i = 0
             while i in range(len(listeAssociationCol1)) :
                 modelComboListeModeleCategorie1 = QStandardItem(str(listeAssociationCol1[i]))
                 modelComboListeModeleCategorie2 = QStandardItem(str(listeAssociationCol2[i]))
                 self.modelComboListeModeleCategorie.appendRow([ modelComboListeModeleCategorie2, modelComboListeModeleCategorie1 ])
                 i += 1
             self.comboListeModeleCategorie.setModel(self.modelComboListeModeleCategorie) 
             self.comboListeModeleCategorie.currentIndexChanged.connect(lambda : self.ihmsPlumeASSOCIATION( self ) )
             #------ DATA 

             if hasattr(self, "mSaveItemCurrent") : self.comboListeModeleCategorie.setCurrentIndex(self.mSaveItemCurrent)
          elif mIndex == 1 :
             self.mSaveItemCurrent = self.comboListeModeleCategorie.currentIndex()
             self._selfCreateTemplate    = self
       return

    #===============================              
    def functionUpdateModeleCategorie(self, mActionButton):    # mActionButton = buttonSaveOutVersIn buttonReinitOutVersIn buttonSaveAttribModeleCategorie
       with self.Dialog.safe_pg_connection("continue") :
          self.flagNewModele = True
          # Si les attributs sont visibles, je gère la sauvegarde par rapport à la catégorie sélectionnée                     ['empty', 'manual']     {"empty", "manual"}
          # if ifAttributsVisible( self, self.groupBoxAttributsModeleCategorie, self.mapping_template_categories ) :           {"pattern": "^(?:[[][^]]+[]])?\\n*\\s*(.+)$"}

          if mActionButton == "buttonSaveAttribModeleCategorie" :  
             dicForQuerieForAddModeleCategorie = returnListObjKeyValue(self, self.groupBoxAttributsModeleCategorie, self.mapping_template_categories, 'initialiseAttributsModeleCategorie', self.mListTabs)
             mKeySql = queries.query_insert_or_update_meta_template_categories(dicForQuerieForAddModeleCategorie)
             r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self.Dialog.mConnectEnCours, mKeySql, optionRetour = "fetchone")
             self._selfCreateTemplate.Dialog.mConnectEnCours.commit()
             #- Réinit
             mKeySql = queries.query_read_meta_template_categories()
             r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self.Dialog.mConnectEnCours, mKeySql, optionRetour = "fetchall")
             self._selfCreateTemplate.mListTemplateCategories = [row[0] for row in r]
             #Réinstancier les variables dans les deux treeview 
             self._selfCreateTemplate.mTreeListeCategorieIn.mListTemplateCategories = self._selfCreateTemplate.mListTemplateCategories
             self._selfCreateTemplate.mTreeListeCategorieOut.mListTemplateCategories = self._selfCreateTemplate.mListTemplateCategories

          # je gère le passage des In en Out et Vice Versa
          elif mActionButton == "buttonSaveOutVersIn" :  
             _dicInVersOutDesign = self._selfCreateTemplate.mTreeListeCategorieIn.dicInVersOutDesign
             _dicOutVersInDesign = self._selfCreateTemplate.mTreeListeCategorieIn.dicOutVersInDesign

             if len(_dicInVersOutDesign) != 0 : 
                # Delete
                listDelete = returnListObjKeyValueEnFonctionDesCatInCatOut(self, self.mListTemplateCategories, self.mapping_template_categories, _dicInVersOutDesign, "CAT_IN" )
                for elemDelete in listDelete :
                    mKeySql = queries.query_delete_meta_template_categories(elemDelete)
                    r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self.Dialog.mConnectEnCours, mKeySql, optionRetour = None)

             if len(_dicOutVersInDesign) != 0 : 
                # Insert Or Update
                listAppend = returnListObjKeyValueEnFonctionDesCatInCatOut(self, self.mListTemplateCategories, self.mapping_template_categories, _dicOutVersInDesign, "CAT_OUT" )
                for elemAppend in listAppend :
                    mKeySql = queries.query_insert_or_update_meta_template_categories(elemAppend)
                    r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self.Dialog.mConnectEnCours, mKeySql, optionRetour = "fetchone")

             # Save       
             self._selfCreateTemplate.Dialog.mConnectEnCours.commit()
             # Réintialise les treeviews CatIn et CatOUT avec les nouvelles valeurs et sans la colorisation des backGrounds       
             self.ihmsPlumeASSOCIATION( self )

          # je gère le passage des In en Out et Vice Versa
          elif mActionButton == "buttonReinitOutVersIn" :  
             self.ihmsPlumeASSOCIATION( self )
       return

    #===============================              
    def functionUpdateModele(self):
       zTitre = QtWidgets.QApplication.translate("CreateTemplate_ui", "PLUME : Warning", None)
       zMess  = QtWidgets.QApplication.translate("CreateTemplate_ui", "You must enter a label.", None)
       
       mTestExisteModele = returnListObjAttributsId(self, self.groupBoxAttributsModele, self.mapping_templates)[0]
       if mTestExisteModele.text() == "" :
          displayMess(self, (2 if self.Dialog.displayMessage else 1), zTitre, zMess, Qgis.Warning, self.Dialog.durationBarInfo)
       else :   
          self.flagNewModele = True
          self.mTreeListeRessourceModele.ihmsPlumeUpdateModele(self.Dialog, mTestExisteModele.text())
       return

    #===============================              
    def functionUpdateOnglet(self):
       zTitre = QtWidgets.QApplication.translate("CreateTemplate_ui", "PLUME : Warning", None)
       zMess  = QtWidgets.QApplication.translate("CreateTemplate_ui", "You must enter a label.", None)
       mTestExisteOnglet = returnListObjAttributsId(self, self.groupBoxAttributsOnglet, self.mapping_tabs)[0]
       if mTestExisteOnglet.text() == "" :
          displayMess(self, (2 if self.Dialog.displayMessage else 1), zTitre, zMess, Qgis.Warning, self.Dialog.durationBarInfo)
       else :   
          self.flagNewOnglet = True
          self.mTreeListeRessourceOnglet.ihmsPlumeUpdateOnglet(self.Dialog, mTestExisteOnglet.text())
       return

    #===============================              
    def functionUpdateCategorie(self):
       zTitre = QtWidgets.QApplication.translate("CreateTemplate_ui", "PLUME : Warning", None)
       zMess  = QtWidgets.QApplication.translate("CreateTemplate_ui", "You must enter a label.", None)
       mTestExisteCategorie = returnListObjAttributsId(self, self.groupBoxAttributsCategorie, self.mapping_categories)[0]
       if mTestExisteCategorie.text() == "" :
          displayMess(self, (2 if self.Dialog.displayMessage else 1), zTitre, zMess, Qgis.Warning, self.Dialog.durationBarInfo)
       else :   
          self.flagNewCategorie = True
          self.mTreeListeRessourceCategorie.ihmsPlumeUpdateCategorie(self.Dialog, mTestExisteCategorie.text())
       return


    #==========================
    def resizeEvent(self, event):
        self.tabWidget.setGeometry(QtCore.QRect(10,100,self.width() - 20, self.height() - self.deltaHauteurTabWidget))
        self.groupBox_tab_widget_Association.setGeometry(QtCore.QRect(10,10,self.tabWidget.width() - 20, self.tabWidget.height() - 40))
        self.groupBox_tab_widget_Ressource.setGeometry(QtCore.QRect(10,10,self.tabWidget.width() - 20, self.tabWidget.height() - 40))
        return

#==========================         
#==========================         
def returnListChildren(self, _labelClick, _listCategorie, _origine) : 
    _dicTempoAppendReturn, _dicTempoDeletedReturn = [], []
    i = 0
    while i < len(_listCategorie) : 
       _lib_label     =  _listCategorie[i]["_label"]
       if _labelClick == _lib_label[0 : len(_labelClick)] : 
          _dicTempoDelete = dict(zip( [                  "_displayLibelle",                    "_label",                    "_libelle",                    "_clickAsso",                    "mOrigine",                                        "mNoeud", "_local"], \
                                      [_listCategorie[i]["_displayLibelle"], _listCategorie[i]["_label"], _listCategorie[i]["_libelle"], _listCategorie[i]["_clickAsso"], _listCategorie[i]["mOrigine"],                     _listCategorie[i]["mNoeud"], _listCategorie[i]["_local"] ]))
          _dicTempoAppend = dict(zip( [                  "_displayLibelle",                    "_label",                    "_libelle",                    "_clickAsso",                    "mOrigine",                                        "mNoeud", "_local"], \
                                      [_listCategorie[i]["_displayLibelle"], _listCategorie[i]["_label"], _listCategorie[i]["_libelle"], _listCategorie[i]["_clickAsso"], ("CAT_OUT" if _origine == "CAT_IN" else "CAT_IN"), _listCategorie[i]["mNoeud"], _listCategorie[i]["_local"] ]))
          _dicTempoAppendReturn.append(_dicTempoAppend)
          _dicTempoDeletedReturn.append(_dicTempoDelete)
       i += 1
    return _dicTempoAppendReturn, _dicTempoDeletedReturn

#==========================         
#==========================         
def returnbuttonSaveAttribCategorieToolTip( mbuttonSaveAttribCategorieToolTip, mbuttonSaveAttribModeleToolTip ) : 
    mbuttonSaveAttribModeleCategorieToolTip1 = QtWidgets.QApplication.translate("CreateTemplate_ui", "Save metadata configuration", None)  
    mbuttonSaveAttribModeleCategorieToolTip2 = QtWidgets.QApplication.translate("CreateTemplate_ui", "for the model", None)
    _sep1AttribModeleToolTip, _sep2AttribModeleToolTip = "{", "}"
    return mbuttonSaveAttribModeleCategorieToolTip1 + " " + _sep1AttribModeleToolTip + mbuttonSaveAttribCategorieToolTip + _sep2AttribModeleToolTip + " " + mbuttonSaveAttribModeleCategorieToolTip2 \
                                                    + " " + _sep1AttribModeleToolTip + mbuttonSaveAttribModeleToolTip    + _sep2AttribModeleToolTip + "."

#==========================         
def afficheLabelAndLibelle(_selfCreateTemplate, etat_labelDiskSaveAndReinit, etat_buttonSaveOutVersIn, etat_buttonReinitOutVersIn, etat_buttonSaveAttribModeleCategorie) :
    _selfCreateTemplate.labelDiskSaveAndReinit.setVisible(etat_labelDiskSaveAndReinit)
    _selfCreateTemplate.buttonSaveOutVersIn.setVisible(etat_buttonSaveOutVersIn)
    _selfCreateTemplate.buttonReinitOutVersIn.setVisible(etat_buttonReinitOutVersIn)
    _selfCreateTemplate.buttonSaveAttribModeleCategorie.setVisible(etat_buttonSaveAttribModeleCategorie)
    return 

#==========================         
#==========================         
def returnListRessourceCategorie(self, mListCategories) : 
    _listCategorieIn = []
    i = 0
    while i < len(self.mListCategories) : 
       _lib_Categories     = self.mListCategories[i]["path"] 
       _libelle_Categories = self.mListCategories[i]["label"]    #deuxième colonne dans les treeview pour le In 
       _noeud              = "True" if self.mListCategories[i]["is_node"] else "False"  # si c'est un noeud pour être utilisé dans le double click, In vers Out 
       path_elements       = re.split(r'\s*[/]\s*', _lib_Categories) #pour découper le chemin, 
       paths               = [ ' / '.join(path_elements[:ii + 1] ) for ii in range(len(path_elements) - 1) ]  #Chemin des parents
       
       if self.mListCategories[i]["origin"] == "local" :
          _displayLibelle = str(_libelle_Categories) + self.sepLeftTemplate + str(path_elements[ -1 ])    + self.sepRightTemplate # For Affichage LIBELLE PLUS Dernier ELEMENT du chemin (paths)
       else :
          _displayLibelle = str(path_elements[ -1 ])    + self.sepLeftTemplate + str(_libelle_Categories) + self.sepRightTemplate # For Affichage LIBELLE PLUS Dernier ELEMENT du chemin (paths)

       _dicTempo = dict(zip( ["_displayLibelle", "_label", "_libelle", "_clickAsso", "mOrigine", "mNoeud"], [_displayLibelle, _lib_Categories, _libelle_Categories, "", '', _noeud] ))
       _listCategorieIn.append(_dicTempo)
       i += 1
    
    return _listCategorieIn

#==========================         
#==========================         
def ventileCatInCatOut(self, _mItemClicAssociation, mListTemplateCategories, mListCategories) : 
    _listCategorieOut, _listCategorieIn = [], []

    i = 0
    while i < len(self.mListCategories) : 
       _lib_Categories     = self.mListCategories[i]["path"] 
       _libelle_Categories = self.mListCategories[i]["label"]    #deuxième colonne dans les treeview pour le In 
       _noeud              = "True" if self.mListCategories[i]["is_node"] else "False"  # si c'est un noeud pour être utilisé dans le double click, In vers Out 
       path_elements       = re.split(r'\s*[/]\s*', _lib_Categories) #pour découper le chemin, 
       paths               = [ ' / '.join(path_elements[:ii + 1] ) for ii in range(len(path_elements) - 1) ]  #Chemin des parents

       j = 0
       mConditionInOut = False

       while j < len(self.mListTemplateCategories) : 
          _lib_Template_Categories = mListTemplateCategories[j]["shrcat_path"] if mListTemplateCategories[j]["shrcat_path"] != None else mListTemplateCategories[j]["loccat_path"]
          
          # _libelle (_label)  Nom du libellé de la catégorie + Nom de la catégorie (colonne 1 in QtreeWidget)
          # _label      Nom de la catégorie                                         (colonne 2 in QtreeWidget)
          # _libelle    Nom du libellé de la catégorie                              (colonne 3 in QtreeWidget) 
          # _clickAsso  Nom du modèle cliqué
          # mOrigine    Sens (In vers Out ou vice Versa
          # mNoeud      Est-ce un Noeud
          _returnAttribCategorie = returnAttribCategoriesEnFonctionLibelleTemplateCategorie(self, _lib_Categories, self.mListCategories)[0]
          _lib_Categories_in     = _returnAttribCategorie["path"]
          _libelle_Categories_in = _returnAttribCategorie["label"]

          if _returnAttribCategorie["origin"] == "local" :
             _displayLibelle = str(_libelle_Categories_in) + self.sepLeftTemplate + str(path_elements[ -1 ])    + self.sepRightTemplate # For Affichage LIBELLE PLUS Dernier ELEMENT du chemin (paths)
          else :
             _displayLibelle = str(path_elements[ -1 ])    + self.sepLeftTemplate + str(_libelle_Categories_in) + self.sepRightTemplate # For Affichage LIBELLE PLUS Dernier ELEMENT du chemin (paths)
          
          mConditionInOut = _lib_Categories == _lib_Template_Categories and str(mListTemplateCategories[j]["tpl_id"]) == _mItemClicAssociation
          
          _dicTempo = dict(zip( ["_displayLibelle", "_label", "_libelle", "_clickAsso", "mOrigine", "mNoeud", "_local"], [_displayLibelle, _lib_Categories_in, _libelle_Categories_in, _mItemClicAssociation, 'CAT_IN' if mConditionInOut else 'CAT_OUT', _noeud, _returnAttribCategorie["origin"]] ))

          # Ventilation Cat IN / Cat Out 
          if mConditionInOut :
             _listCategorieIn.append(_dicTempo)
             break
          j += 1
       if not mConditionInOut : _listCategorieOut.append(_dicTempo)
       i += 1
    
    return _listCategorieOut, _listCategorieIn

#==========================         
#===============================              
def returnAttribCategoriesEnFonctionLibelleTemplateCategorie(self, libTemplateCategories, dicCategories) :
    _returnLibelleTemplateCategorie = []
    _returnLibelleTemplateCategorie = [ elemDic for elemDic in dicCategories if elemDic["path"] == libTemplateCategories ]  
    return _returnLibelleTemplateCategorie

#==========================         
#==========================         
def returnListObjAttributsId(self,  _groupBoxAttributs, mapping ) :
  _group = _groupBoxAttributs.children() 
  _returnListObjAttributs = []
  for mObj in _group :
      _zone = mObj.objectName()[5:]
      if (_zone in mapping and mapping[_zone]["id"] == "OK") :
         _returnListObjAttributs.append(mObj)
  return _returnListObjAttributs

#==========================         
def returnListObjKeyValue(self,  _groupBoxAttributs, mapping, keyAncetre_ModeleCategorie_Modele_Categorie_Onglet, _mListTabs = None ) :
  _group = _groupBoxAttributs.children() 
  _returnListObjKeyValue = {}
  for mObj in _group :
      _zone = mObj.objectName()[5:]
      _value = ""
      if (_zone in mapping) :
         _type      = mapping[_zone]["type"]                                     

         _format    = mapping[_zone]["format"]
         _qcombobox = mapping[_zone]["dicListItems"] 
         __Val   = _zone
   
         if _type in ("QLineEdit",) :
           __Val = mObj.text() if mObj.text() != "" else None 
           if _format in ("list", )  :  __Val = self._selfCreateTemplate.dicValuePropriete[keyAncetre_ModeleCategorie_Modele_Categorie_Onglet][_zone]
           
         elif _type in ("QTextEdit",) :
               __Val = mObj.toPlainText() if mObj.toPlainText() != "" else None 
         elif _type in ("QComboBox",) :
               __Val = mObj.currentText() if (mObj.currentText() != "" and mObj.currentText() != "Aucun") else None
               #Gestion de l'ID 
               if __Val != None :
                  if _qcombobox == "tabs" :
                     __Val = [ elem["tab_id"] for elem in _mListTabs if str(elem["tab_label"]) == __Val ][0]
                  elif isinstance( _qcombobox, dict ) : #  """ EXEMPLE {  "email" : {"enum_label" : "Courriel",  "enum_help" : "saisie d'une adresse electronique"}, etc .... }
                     dicListItems = _qcombobox
                     __Val = [ k for k, v in dicListItems.items() if str(v["enum_label"]) == __Val ][0]
               #Gestion de l'ID 
         elif _type in ("QDateEdit",) :
               __Val = mObj.date().toString("dd/MM/yyyy") if mObj.date().toString("dd/MM/yyyy") != "" else None 
         elif _type in ("QDateTimeEdit",) :
               __Val = mObj.dateTime().toString("dd/MM/yyyy hh:mm:ss") if mObj.dateTime().toString("dd/MM/yyyy hh:mm:ss") != "" else None 
         elif _type in ("QTimeEdit",) :
               __Val = mObj.time().toString("hh:mm:ss") if mObj.time().toString("hh:mm:ss") != "" else None 
         elif _type in ("QCheckBox",) :
               __Val = ("true" if mObj.checkState() == QtCore.Qt.Checked else "false") if  mObj.checkState() != QtCore.Qt.PartiallyChecked else None 

         _returnListObjKeyValue[_zone] = __Val

  return _returnListObjKeyValue

#==========================         
#==========================         
def returnListObjKeyValueEnFonctionDesCatInCatOut(self, _mListTemplateCategories, _mapping, _dicInVersOut_OR_dicOutVersIn, _mOrigine ) :

    if _mOrigine == "CAT_IN" :
       _returnListObjKeyValue = []
       # Boucle for TemplateCategories
       for elemDic_TemplateCategories in _mListTemplateCategories :
           # Boucle for _dicInVersOut_OR_dicOutVersIn
           for key_dicInVersOut_OR_dicOutVersIn, value_dicInVersOut_OR_dicOutVersIn in _dicInVersOut_OR_dicOutVersIn.items() :
              if value_dicInVersOut_OR_dicOutVersIn[1] == "shared" : # If cat commune 
                 _cond1 = elemDic_TemplateCategories["shrcat_path"]  == key_dicInVersOut_OR_dicOutVersIn
              elif value_dicInVersOut_OR_dicOutVersIn[1] == "local" :# If cat locale
                 _cond1 = elemDic_TemplateCategories["loccat_path"]  == key_dicInVersOut_OR_dicOutVersIn
              _cond2 = elemDic_TemplateCategories["tpl_id"]       == int(value_dicInVersOut_OR_dicOutVersIn[0])

              if _cond1 and _cond2 :
                 _req = { "tplcat_id" : elemDic_TemplateCategories["tplcat_id"] }  # je prends tplcat_id pour les delete
                 _returnListObjKeyValue.append(_req)

    elif _mOrigine == "CAT_OUT" :
       _returnListObjKeyValue = []
       # Boucle for _dicInVersOut_OR_dicOutVersIn
       for key_dicInVersOut_OR_dicOutVersIn, value_dicInVersOut_OR_dicOutVersIn in _dicInVersOut_OR_dicOutVersIn.items() :
           if value_dicInVersOut_OR_dicOutVersIn[1] == "shared" : # If cat commune 
              _req = { "shrcat_path" : key_dicInVersOut_OR_dicOutVersIn, "tpl_id" : int(value_dicInVersOut_OR_dicOutVersIn[0]) } 
           elif value_dicInVersOut_OR_dicOutVersIn[1] == "local" :# If cat locale
              _req = { "loccat_path" : key_dicInVersOut_OR_dicOutVersIn, "tpl_id" : int(value_dicInVersOut_OR_dicOutVersIn[0]) } 
           _returnListObjKeyValue.append(_req)
          
    return _returnListObjKeyValue

#==========================         
#==========================         
def genereAttributs(self,  mapping, zoneLayout, _keyAncetre_ModeleCategorie_Modele_Categorie_Onglet, _groupBoxdisplayHelpFocus, _zoneDisplayHelpFocus ) :
  # [ == création des attibuts == ]
  _row, _col = 0, 0
  _pathIcons         = os.path.dirname(__file__) + "/icons/general"
  _iconSourcesSelect = _pathIcons + "/read.svg"
  

  for keyNameAttrib, dicLabelTooltip in mapping.items() :
      okCreateZone = False
      mattrib = keyNameAttrib
      # Libellé            "loccat_path"    : {"label" : "libelle loccat_path",     "tooltip" : "tooltip loccat_path",    "type" : "QLineEdit"},         
      mTextToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", mapping[mattrib]["tooltip"])
      _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "toolTipWidget", "aligneWidget", "styleSheet", "wordWrap" ]
      _ListValues = [ QtWidgets.QLabel(), mapping[mattrib]["label"], "label_" + mattrib , mTextToolTip, QtCore.Qt.AlignRight, "QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}", True ]
      dicParamLabel = dict(zip(_Listkeys, _ListValues))
      _modCat_Lib_Attrib = genereLabelWithDict( dicParamLabel )
      # widget
      if dicLabelTooltip["type"]   == "QLineEdit" :
         okCreateZone = True
         _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "toolTipWidget", "aligneWidget", "styleSheet" ]
         _ListValues = [ QtWidgets.QLineEdit(), "", "zone_" + mattrib, mTextToolTip, QtCore.Qt.AlignRight, "QLineEdit {  font-family:" + self.policeQGroupBox  +";}" ]
      elif dicLabelTooltip["type"] == "QCheckBox" :
         okCreateZone = True           
         _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "toolTipWidget", "aligneWidget", "styleSheet", "checked", "tristate" ]
         _ListValues = [ QtWidgets.QCheckBox(), "", "zone_" + mattrib, mTextToolTip, QtCore.Qt.AlignRight, "QCheckBox {  font-family:" + self.policeQGroupBox  +";}", False, True if mapping[mattrib]["format"] == "Tristate(True)" else False ]
      elif dicLabelTooltip["type"] == "QComboBox" :
         okCreateZone = True
         _Listkeys   = [ "typeWidget", "nameWidget", "toolTipWidget", "aligneWidget", "styleSheet" ]
         _ListValues = [ QtWidgets.QComboBox(), "zone_" + mattrib, mTextToolTip, QtCore.Qt.AlignRight, "QComboBox {  font-family:" + self.policeQGroupBox  +";}" ]

      if okCreateZone :
         dicParamButton = dict(zip(_Listkeys, _ListValues))
         _modCat_Attrib = GenereButtonsWithDictWithEvent( self, dicParamButton, mapping, _groupBoxdisplayHelpFocus, _zoneDisplayHelpFocus )._button
         
         if dicLabelTooltip["format"]   == "integer" :
            _modCat_Attrib.setValidator(QtGui.QIntValidator(_modCat_Attrib))

         if zoneLayout.objectName()   in ["layoutAttributsModeleCategorie", ] : 
            colonneLib, colonneAttrib, colonneAssistant = _col + 2, _col + 3, _col + 4        
         elif zoneLayout.objectName() in [ "layoutAttributsModele", "layoutAttributsCategorie", "layoutAttributsOnglet"] : 
            colonneLib, colonneAttrib, colonneAssistant = _col, _col + 1, _col + 2
                    
         zoneLayout.addWidget(_modCat_Lib_Attrib, _row, colonneLib,    QtCore.Qt.AlignTop)
         zoneLayout.addWidget(_modCat_Attrib    , _row, colonneAttrib, QtCore.Qt.AlignTop)

         if dicLabelTooltip["assistantTranslate"][0] == "true" :
            # lecture du fichier mapping_templates
            mDicEnum = dicLabelTooltip["enum"] if dicLabelTooltip["assistantTranslate"][1] == "list" else None
            _Listkeys   = [ "typeWidget", "nameWidget", "_modCat_Attrib", "iconWidget", "toolTipWidget" ]
            _ListValues = [ QtWidgets.QToolButton(), "assistant_" + mattrib, _modCat_Attrib, _iconSourcesSelect, QtWidgets.QApplication.translate("CreateTemplate_ui", "Assistant", None)  ]
            dicParamButton = dict(zip(_Listkeys, _ListValues))             # ci-dessous Nom de l'attrib,  objet attrib
            _mObjetAssistant = GenereButtonsAssistant( self, dicParamButton,            mattrib,          _modCat_Attrib, mDicEnum, mapping[mattrib]["label"], mapping[mattrib]["help"], _keyAncetre_ModeleCategorie_Modele_Categorie_Onglet )._buttonAssistant 
            zoneLayout.addWidget(_mObjetAssistant, _row, colonneAssistant, QtCore.Qt.AlignTop)
      _row += 1
  return 

#==========================         
#==========================  
# Recherche d'un dictionnaire dans la liste des dictionnaires sur l'id _label  
# Retourne l'index de l'élément recherché   
# param1 : __dicTempoDeleteChildrenKey = _dicTempoAppendChildren[iElem]["_label"]  
def returnIndexInListeCategorie( __dicTempoDeleteChildrenKey, _mListCategories ) :
    i = 0
    while i < len(_mListCategories) :
       if __dicTempoDeleteChildrenKey == _mListCategories[i]["_label"] :
          return i
       i += 1

#==========================         
#==========================         
def ifAttributsVisible(self,  _groupBoxAttributs, _mapping ) :
  _group = _groupBoxAttributs.children() 
  for mObj in _group :
      if (mObj.objectName()[5:] in _mapping) or (mObj.objectName()[6:] in _mapping) :
         return (True if mObj.isVisible() else False)

#==========================         
#==========================         
def afficheAttributs(self,  _groupBoxAttributs, _mapping, display ) :
  _group = _groupBoxAttributs.children() 
  for mObj in _group :
      if (mObj.objectName()[5:] in _mapping) or (mObj.objectName()[6:] in _mapping) or (mObj.objectName()[10:] in _mapping) :
         mObj.setVisible(display)
      if display == True and mObj.objectName()[5:] in _mapping : 
         mObj.setEnabled(False if "disabled"  in _mapping[mObj.objectName()[5:]]["property"] else True)  
         mObj.setVisible(False if "novisible" in _mapping[mObj.objectName()[5:]]["property"] else True)
      if display == True and mObj.objectName()[6:] in _mapping : 
         mObj.setVisible(False if "novisible" in _mapping[mObj.objectName()[6:]]["property"] else True)
  return

#==========================         
#==========================         
def initialiseAttributsModeleCategorie(self,  _mItemClic_CAT_IN_OUT, _mItemClicAssociation, _groupBoxAttributsModeleCategorie, _mapping_template_categories, _mListTemplateCategories, _mListTabs, display ) :
    _group = _groupBoxAttributsModeleCategorie.children() 

    # Select for association et catégorie
    _mapping_template_categories_id_association_id_categorie = []
    i = 0
    while i < len(_mListTemplateCategories) :
       if _mItemClicAssociation == str(_mListTemplateCategories[i]["tpl_id"]) :
           if _mItemClic_CAT_IN_OUT == (_mListTemplateCategories[i]["shrcat_path"] if _mListTemplateCategories[i]["shrcat_path"] != None else _mListTemplateCategories[i]["loccat_path"]) : 
              _mapping_template_categories_id_association_id_categorie = _mListTemplateCategories[i]
              break  
       i += 1
    # Si _mapping_template_categories_id_association_id_categorie alors catégorie déplacé provenant de Out vers In
    initialiseValueOrBlank =  len(_mapping_template_categories_id_association_id_categorie)
    sharedOrLocal = "local"
    returnDicValuePropriete = {}
    # Initialisation
    listeThesaurus = None
    for mObj in _group :
        if (mObj.objectName()[5:] in _mapping_template_categories) :
           # widget
           _type  = _mapping_template_categories[ mObj.objectName()[5:] ]["type" ]
           if initialiseValueOrBlank == 0 :
              __Val = ""
           else :
              # Ne pas transformer en string sinon, returnDicValuePropriete ne prendra les bons types
              #__Val = _mapping_template_categories_id_association_id_categorie[ mObj.objectName()[5:] ] if _mapping_template_categories_id_association_id_categorie[ mObj.objectName()[5:] ] != None else "" 
              __Val = _mapping_template_categories_id_association_id_categorie[ mObj.objectName()[5:] ] 

           # Gestion for Sources, geo_tools, Compute, demandant None pour zone Vierge
           if _mapping_template_categories[ mObj.objectName()[5:] ]["format"] == "list"  :
              if (__Val == None or __Val == "") : __Val = None

           #Initialise un dictionnaire des valeurs retournées par PostgreSQL pour l'IHM de l'asssistant
           returnDicValuePropriete[mObj.objectName()[5:]] = __Val

           # ICI, on transforme en string pour les QWidgets de saisie ou d'affichage sinon en json pour le format ) "jsonb" 
           if _mapping_template_categories[ mObj.objectName()[5:] ]["format"] == "jsonb"  :
              # For display json in QlineEdit  
              __Val = "" if (__Val == None or __Val == "") else json.dumps(__Val, ensure_ascii=False) 
           else :
              __Val = str("" if __Val == None  else __Val)

           if _type in ("QLineEdit",) :
              mObj.setText(__Val if __Val != None else "")  
           elif _type in ("QTextEdit",) :
              mObj.setPlainText(__Val if __Val != None else "")  
           elif _type in ("QComboBox",) :

              if _mapping_template_categories[ mObj.objectName()[5:] ]["dicListItems" ] == ("tabs") :
                 #Alim la QcomboBox via z_plume.meta_tab
                 listItems    = sorted(set([ elem["tab_label"] for elem in _mListTabs ]), key=lambda col: col.lower())
                 mLibAucun    = "Aucun"
                 mDicLibAucun = {"tab_label" : "Aucun", "tab_id" : ""}
                 if mLibAucun in listItems  : 
                    del listItems[listItems.index(mLibAucun)]       # Pour gérer le tri avec Aucun en tête
                 if mDicLibAucun in _mListTabs  : 
                    del _mListTabs[_mListTabs.index(mDicLibAucun)]  # Pour gérer le tri avec Aucun en tête
                 if mLibAucun not in listItems :                 
                    listItems.insert( 0, "Aucun" )
                    _mListTabs.insert( 0, {"tab_label" : "Aucun", "tab_id" : ""} )
                 __valCurrent = [ elem["tab_label"] for elem in _mListTabs if str(elem["tab_id"]) == __Val ]
                 mObj.clear()
                 mObj.addItems(listItems)

              elif isinstance( _mapping_template_categories[ mObj.objectName()[5:] ]["dicListItems" ], dict ) :
                 #Alim la QcomboBox via plume.mapping_templates
                 """ EXEMPLE
                 { 
                          "email" : {"enum_label" : "Courriel",  "enum_help" : "saisie d'une adresse electronique"},
                          "phone" : {"enum_label" : "Téléphone", "enum_help" : "saisie d'un numéro de téléphone"},
                          "url"   : {"enum_label" : "Url",       "enum_help" : "saisie d'une url"}
                        }
                 """       
                 dicListItems    = _mapping_template_categories[ mObj.objectName()[5:] ]["dicListItems" ]
                 listItems    = [ v["enum_label"] for k, v in dicListItems.items() ] 
                 listItems.append("Aucun")
                 listItems = sorted(listItems)
                 __valCurrent = [ v["enum_label"] for k, v in dicListItems.items() if str(k) == __Val ] if (__Val != "" and __Val != None) else "Aucun"
                 mObj.clear()
                 mObj.addItems(listItems)

              mObj.setCurrentText( __valCurrent[0])  
           elif _type in ("QLabel",) :
              mObj.setText(__Val if __Val != None else "")  
           elif _type in ("QDateEdit",) :
              displayFormat = 'dd/MM/yyyy'
              mObj.setDate(QDate.fromString( __Val, _displayFormat)) 
           elif _type in ("QDateTimeEdit",) :
              displayFormat = 'dd/MM/yyyy hh:mm:ss'
              mObj.setDateTime(QDateTime.fromString( __Val, _displayFormat))       
           elif _type in ("QTimeEdit",) :
              _displayFormat = 'hh:mm:ss'
              mObj.setTime(QTime.fromString( __Val, _displayFormat))       
           elif _type in ("QCheckBox",) :
              # je reprends returnDicValuePropriete[mObj.objectName()[5:]] et pas __Val pour conserver le None pour le setTristate(True)
              mObj.setCheckState((QtCore.Qt.Checked if str( returnDicValuePropriete[mObj.objectName()[5:]] ).lower() == 'true' else QtCore.Qt.Unchecked) if returnDicValuePropriete[mObj.objectName()[5:]] != None else QtCore.Qt.PartiallyChecked)
              
           #=================
           # CONTROLES DE SURFACE
           if (mObj.objectName()[5:] == "shrcat_path" and __Val != "") : sharedOrLocal = "shared" 
           if mObj.objectName()[5:] == "sources":  mObj.setEnabled(True if sharedOrLocal == "shared" else False) 
           if  (    _mapping_template_categories[ mObj.objectName()[5:] ]["assistantTranslate"][0] == "true" 
               and  _mapping_template_categories[ mObj.objectName()[5:] ]["assistantTranslate"][1] == "list" ) :  mObj.setEnabled(False) 

           #-- for button assistant en fonction returnListeThesaurus
           if mObj.objectName()[5:] == "sources" :
              listeThesaurus = returnListeThesaurus(self.listLangList, _mItemClic_CAT_IN_OUT)

        #-- for button assistant en fonction returnListeThesaurus
        if mObj.objectName() == "assistant_sources" : 
           if len(listeThesaurus) == 0 : mObj.setVisible(False)
    return returnDicValuePropriete, listeThesaurus


#==========================         
               
#==========================  
# Recherche et retourne les valeurs du thésaurus en fonction de la catégorie cliquée.
# Si rien n'est retorunée alors on n'affiche pas le bouton d'assistant
# si retour, alors on envoie en poramètre les valeurs des thésaurus
def returnListeThesaurus( listLangList, _mItemClic_CAT_IN_OUT ) :
    # gestion du Out
    mListSources = property_sources(_mItemClic_CAT_IN_OUT)
    mDicTempo = {}
    for elem in mListSources : 
        label = source_label(elem, listLangList)
        examples = source_examples(elem, listLangList)
        enum_help_title =  "<b>Exemples du contenu du thésaurus :</b><br>"
        enum_help = "<table><tr><td>" + enum_help_title + "</td></tr><tr><td><ul>"
        for elem_in_examples in examples :
            enum_help += "<li>" + elem_in_examples + "</li>" 
        enum_help += "</ul></td></tr></table>"
        mDicTempo[elem] = {"enum_label" : label,  "enum_help" : enum_help}
    # gestion du Out

    return mDicTempo

#==========================         
#==========================  
def initialiseAttributsModelesCategoriesOnglets(self, _mItemClicModele, _groupBoxAttributsModele, _mapping_template, _mListTemplates, display, _blank = None ) :
    _group = _groupBoxAttributsModele.children() 
    # Select for association et catégorie
    _mapping_template_id_template = []
    i = 0
    while i < len(_mListTemplates) :
       if "tpl_id" in _mListTemplates[i] :
          if _mItemClicModele == str(_mListTemplates[i]["tpl_id"]) :
             _mapping_template_id_template = _mListTemplates[i]
             break  
       elif "tab_id" in _mListTemplates[i] :
          if _mItemClicModele == str(_mListTemplates[i]["tab_id"]) :
             _mapping_template_id_template = _mListTemplates[i]
             break  
       elif "path" in _mListTemplates[i] :
          if _mItemClicModele == str(_mListTemplates[i]["path"]) :
             _mapping_template_id_template = _mListTemplates[i]
             break  
       i += 1
    # Si _mapping_template_categories_id_association_id_categorie alors catégorie déplacé provenant de Out vers In
    # if Vierge
    initialiseValueOrBlank =  len(_mapping_template_id_template) if _blank == None else 0

    sharedOrLocal = "local"
    returnDicValuePropriete = {}
    # Initialisation
    listeThesaurus = None
    for mObj in _group :
        if (mObj.objectName()[5:] in _mapping_template) :
           # widget
           _type  = _mapping_template[ mObj.objectName()[5:] ]["type" ]
           if initialiseValueOrBlank == 0 :
              __Val = ""
           else :    
              if _blank == None :
                 __Val = _mapping_template_id_template[ mObj.objectName()[5:] ]
              else :     
                 # if Vierge
                 __Val = ""
           # Gestion for Sources, geo_tools, Compute, demandant None pour zone Vierge
           if _mapping_template[ mObj.objectName()[5:] ]["format"] == "list"  :
              if (__Val == None or __Val == "") : __Val = None
              
           #Initialise un dictionnaire des valeurs retournées par PostgreSQL pour l'IHM de l'asssistant
           returnDicValuePropriete[mObj.objectName()[5:]] = __Val

           # ICI, on transforme en string pour les QWidgets de saisie ou d'affichage sinon en json pour le format ) "jsonb" 
           if _mapping_template[ mObj.objectName()[5:] ]["format"] == "jsonb"  :
              # For display json in QlineEdit  
              __Val = "" if (__Val == None or __Val == "") else json.dumps(__Val, ensure_ascii=False) 
           else :
              __Val = str("" if __Val == None  else __Val)

           if _type in ("QLineEdit",) :
              mObj.setText(__Val if __Val != None else "")  
           elif _type in ("QTextEdit",) :
              mObj.setPlainText(__Val if __Val != None else "")  
           elif _type in ("QComboBox",) :

              if _mapping_template[ mObj.objectName()[5:] ]["dicListItems" ] == ("tabs") :
                 #Alim la QcomboBox via z_plume.meta_tab
                 listItems    = sorted(set([ elem["tab_label"] for elem in _mListTabs ]), key=lambda col: col.lower())
                 mLibAucun    = "Aucun"
                 mDicLibAucun = {"tab_label" : "Aucun", "tab_id" : ""}
                 if mLibAucun in listItems  : 
                    del listItems[listItems.index(mLibAucun)]       # Pour gérer le tri avec Aucun en tête
                 if mDicLibAucun in _mListTabs  : 
                    del _mListTabs[_mListTabs.index(mDicLibAucun)]  # Pour gérer le tri avec Aucun en tête
                 if mLibAucun not in listItems :                 
                    listItems.insert( 0, "Aucun" )
                    _mListTabs.insert( 0, {"tab_label" : "Aucun", "tab_id" : ""} )
                 __valCurrent = [ elem["tab_label"] for elem in _mListTabs if str(elem["tab_id"]) == __Val ]
                 mObj.clear()
                 mObj.addItems(listItems)

              elif isinstance( _mapping_template[ mObj.objectName()[5:] ]["dicListItems" ], dict ) :
                 #Alim la QcomboBox via plume.mapping_templates
                 """ EXEMPLE
                 { 
                          "email" : {"enum_label" : "Courriel",  "enum_help" : "saisie d'une adresse electronique"},
                          "phone" : {"enum_label" : "Téléphone", "enum_help" : "saisie d'un numéro de téléphone"},
                          "url"   : {"enum_label" : "Url",       "enum_help" : "saisie d'une url"}
                        }
                 """       
                 dicListItems    = _mapping_template[ mObj.objectName()[5:] ]["dicListItems" ]
                 listItems    = [ v["enum_label"] for k, v in dicListItems.items() ] 
                 listItems.append("Aucun")
                 listItems = sorted(listItems)
                 __valCurrent = [ v["enum_label"] for k, v in dicListItems.items() if str(k) == __Val ] if (__Val != "" and __Val != None) else "Aucun"
                 mObj.clear()
                 mObj.addItems(listItems)

              mObj.setCurrentText( __valCurrent[0])  
           elif _type in ("QLabel",) :
              mObj.setText(__Val if __Val != None else "")  
           elif _type in ("QDateEdit",) :
              _displayFormat = 'dd/MM/yyyy'
              mObj.setDate(QDate.fromString( __Val, _displayFormat)) 
           elif _type in ("QDateTimeEdit",) :
              _displayFormat = 'dd/MM/yyyy hh:mm:ss'
              mObj.setDateTime(QDateTime.fromString( __Val, _displayFormat))       
           elif _type in ("QTimeEdit",) :
              _displayFormat = 'hh:mm:ss'
              mObj.setTime(QTime.fromString( __Val, _displayFormat))       
           elif _type in ("QCheckBox",) :
              # je reprends returnDicValuePropriete[mObj.objectName()[5:]] et pas __Val pour conserver le None pour le setTristate(True)
              mObj.setCheckState((QtCore.Qt.Checked if str( returnDicValuePropriete[mObj.objectName()[5:]] ).lower() == 'true' else QtCore.Qt.Unchecked) if returnDicValuePropriete[mObj.objectName()[5:]] != None else QtCore.Qt.PartiallyChecked)

           mObj.setVisible(display)

           #=================
           # CONTROLES DE SURFACE
           if (mObj.objectName()[5:] == "shrcat_path" and __Val != "") : sharedOrLocal = "shared" 
           if mObj.objectName()[5:] == "sources":  mObj.setEnabled(True if sharedOrLocal == "shared" else False) 
           if  (    _mapping_template[ mObj.objectName()[5:] ]["assistantTranslate"][0] == "true" 
               and  _mapping_template[ mObj.objectName()[5:] ]["assistantTranslate"][1] == "list" ) :  mObj.setEnabled(False) 

           #-- for button assistant en fonction returnListeThesaurus
           if mObj.objectName()[5:] == "sources" :
              listeThesaurus = returnListeThesaurus(self.listLangList, _mItemClicModele)

        #-- for button assistant en fonction returnListeThesaurus
        if mObj.objectName() == "assistant_sources" : 
           if len(listeThesaurus) == 0 : mObj.setVisible(False)
    return returnDicValuePropriete, listeThesaurus

#==========================   
# Retoune les listes des noms et libelles et attributs associés  
#==========================         
def returnList_Id_Label( _mapping_template_categories ) :
    i = 0
    dictAssociationCol1EtCol2 = {}
    listeAssociationCol1 = []
    listeAssociationCol2 = []

    while i < len(_mapping_template_categories) : 
       for k, v in _mapping_template_categories[i].items() :
           if "tpl_id" in _mapping_template_categories[i] :
              if _mapping_template_categories[i]["tpl_id"] not in dictAssociationCol1EtCol2 :
                 dictAssociationCol1EtCol2[str(_mapping_template_categories[i]["tpl_id"])] = ( _mapping_template_categories[i]["tpl_id"], str(_mapping_template_categories[i]["tpl_label"]) )
           elif "tab_id" in _mapping_template_categories[i] :
              if _mapping_template_categories[i]["tab_id"] not in dictAssociationCol1EtCol2 :
                 dictAssociationCol1EtCol2[str(_mapping_template_categories[i]["tab_id"])] = ( _mapping_template_categories[i]["tab_id"], str(_mapping_template_categories[i]["tab_label"]) )
           elif "path" in _mapping_template_categories[i] :
              if _mapping_template_categories[i]["path"] not in dictAssociationCol1EtCol2 :
                 dictAssociationCol1EtCol2[str(_mapping_template_categories[i]["path"])]   = ( _mapping_template_categories[i]["path"], str(_mapping_template_categories[i]["label"]) )
       i += 1
    listeAssociationCol1 = [ k    for k, v in dictAssociationCol1EtCol2.items() ]
    listeAssociationCol2 = [ v[1] for k, v in dictAssociationCol1EtCol2.items() ]
    listeAssociationCol1 = list(reversed(listeAssociationCol1))
    listeAssociationCol2 = list(reversed(listeAssociationCol2))
    return listeAssociationCol1, listeAssociationCol2
  
#==========================         
#==========================         
def returnIfExisteCategorie( _mQtreeWidgetItem ) : 
    _ret = True
    if _mQtreeWidgetItem.font(0).bold()   : _ret = False 
    if _mQtreeWidgetItem.font(0).italic() : _ret = False 
    return _ret   

#==========================         
#==========================         
def defineFont( param ) : #gras = 1, italic = 2 gras italic = 3
    _font = QtGui.QFont()
    if param == 1 : 
       _font.setBold(True)
    elif param == 2 : 
       _font.setItalic(True)
    elif param == 3 : 
       _font.setBold(True)
       _font.setItalic(True)
    return _font   

#========================================================     
#========================================================     
# Class pour le tree View Catégories IN and OUT 
class TREEVIEW_CAT_IN_OUT(QTreeWidget):
    customMimeType = "text/plain"

    #===============================              
    def __init__(self, *args):
        QTreeWidget.__init__(self, *args)
        self.setHeaderLabels([""])  
        self.setColumnCount(1)
        self.setSelectionMode(QAbstractItemView.SingleSelection	)  
        self.mnodeToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Right click to delete a Model / Categories association", None)         #Click droit pour supprimer une association Modèle / Catégories

        self.itemDoubleClicked.connect(self.moveDoubleClicked)

        #- Fichier de mapping table ihm
        self.mapping_template_categories = load_mapping_read_meta_template_categories
        
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.menuContextuelPlume_CAT_IN_OUT) 
        return

    #===============================              
    def design_Items(self, _item, _mDicInVersOutDesign, _label, _color) :
        if _mDicInVersOutDesign != None :
           if _label in _mDicInVersOutDesign :  #Design color 
              _item.setBackground(0, _color)
        return

    #===============================              
    def affiche_CAT_IN_OUT(self, _selfCreateTemplate, _mItemClicAssociation, self_Cat_In, self_Cat_Out, mDicInVersOutDesign = None, mDicOutVersInDesign = None, action = False, header = None ) :
        self._selfCreateTemplate              = _selfCreateTemplate  
        _pathIcons = os.path.dirname(__file__) + "/icons/logo"
        iconSource = returnIcon(_pathIcons + "/plume.svg")  
        self.setHeaderLabels([ header[2] if header[0] == "CAT_IN" else header[1] ])  
        self.groupBoxdisplayHelpFocus         = _selfCreateTemplate.groupBoxdisplayHelpFocus  
        self.scroll_bar_help_displayHelpFocusAttributsModele = _selfCreateTemplate.scroll_bar_help_displayHelpFocusAttributsModele
      
        self.groupBoxAttributsModeleCategorie = _selfCreateTemplate.groupBoxAttributsModeleCategorie

        self.zoneDisplayHelpFocus             = _selfCreateTemplate.zoneDisplayHelpFocus
        self.mListTemplates                   = _selfCreateTemplate.mListTemplates
        self.mListTemplateCategories          = _selfCreateTemplate.mListTemplateCategories
        self.mListCategories                  = _selfCreateTemplate.mListCategories   
        self.mListTabs                        = _selfCreateTemplate.mListTabs   
        self.modeleAssociationActif           = _selfCreateTemplate.modeleAssociationActif
        self.colorTemplateInVersOut           = _selfCreateTemplate.colorTemplateInVersOut
        self.colorTemplateOutVersIn           = _selfCreateTemplate.colorTemplateOutVersIn
        self.dicInVersOutDesign               = _selfCreateTemplate.dicInVersOutDesign # Pour la gestion des double clic et la regénération des données en antrée de l'algo
        self.dicOutVersInDesign               = _selfCreateTemplate.dicOutVersInDesign # Pour la gestion des double clic et la regénération des données en antrée de l'algo
        self.sepLeftTemplate                  = _selfCreateTemplate.sepLeftTemplate
        self.sepRightTemplate                 = _selfCreateTemplate.sepRightTemplate
        self.fontCategorieInVersOut           = _selfCreateTemplate.fontCategorieInVersOut
        self.modelComboListeModeleCategorie   = _selfCreateTemplate.modelComboListeModeleCategorie
        self.comboListeModeleCategorie        = _selfCreateTemplate.comboListeModeleCategorie
        self.listLangList                     = _selfCreateTemplate.listLangList
        #---
        self.self_Cat_In                      = self_Cat_In   #self_Cat_In                                                     
        self.self_Cat_Out                     = self_Cat_Out  #self_Cat_Out 
        #---
        self.listCategorieOut                 = _selfCreateTemplate.listCategorieOut # Liste des catégories non utilisées en fonction du click                                                     
        self.listCategorieIn                  = _selfCreateTemplate.listCategorieIn  # Liste des catégories utilisées en fonction du click
        self._origineHeaderLabelsIn           = self._selfCreateTemplate._origineHeaderLabelsIn 
        self._origineHeaderLabelsOut          = self._selfCreateTemplate._origineHeaderLabelsOut 
        #---
        self.labelDiskSaveAndReinit           = self._selfCreateTemplate.labelDiskSaveAndReinit 
        self.buttonSaveOutVersIn              = self._selfCreateTemplate.buttonSaveOutVersIn 
        self.buttonReinitOutVersIn            = self._selfCreateTemplate.buttonReinitOutVersIn 
        self.buttonSaveAttribModeleCategorie  = self._selfCreateTemplate.buttonSaveAttribModeleCategorie 
        #---
        _color_Out_InVersOut = QtGui.QBrush(QtGui.QColor(self.colorTemplateInVersOut))
        _color_In_OutVersIn  = QtGui.QBrush(QtGui.QColor(self.colorTemplateOutVersIn))
        #---
        self.header().setStretchLastSection(True)
        self.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        #---
        self.self_Cat_Out.header().setStretchLastSection(True)
        self.self_Cat_Out.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        
        #Create Arbo
        dictNoeudsArboIn  , rowNodeIn  = {}, 0 
        dictNoeudsArboOut , rowNodeOut = {}, 0 

        if not action : return # Permet de ne pas repasser dans l'algo pour instancier les variables dans la création des QTreeWidgetItem
        """
        EXEMPLE
        {'_displayLibelle': 'dcat:distribution *Distribution*',               {'_displayLibelle': 'dcat:contactPoint *Point de contact*', 
         '_label'         : 'dcat:distribution',                               '_label'         : 'dcat:distribution / dcat:accessService / dcat:contactPoint', 
         '_libelle'       : 'Distribution',                                    '_libelle'       : 'Point de contact', 
         '_clickAsso'     : '23',                                              '_clickAsso'     : '23',
         'mOrigine'       : 'CAT_IN',                                          'mOrigine'       : 'CAT_IN', 
         'mNoeud'         : 'True',                                            'mNoeud'         : 'True',
         '_local'         : 'local'}                                           '_local'         : 'shared'}
        """
        # ======================================
        # ======================================
        #Create Arbo IN
        i = 0

        while i < len(self.listCategorieIn) : 
           _lib_Categories     = self.listCategorieIn[i]["_label"]                         # path origine 
           _libelle_Categories = self.listCategorieIn[i]["_libelle"]                       # deuxième colonne dans les treeview pour le In 
           _noeud              = self.listCategorieIn[i]["mNoeud"]                         # si c'est un noeud pour être utilisé dans le double click, In vers Out 
           _local              = self.listCategorieIn[i]["_local"]                         # si c'est une catgéogorie local ou shared 
           path_elements   = re.split(r'\s*[/]\s*', _lib_Categories)                                          #pour découper le chemin, 
           paths           = [ ' / '.join(path_elements[:ii + 1] ) for ii in range(len(path_elements) - 1) ]  #Chemin des parents
           _label = self.listCategorieIn[i]["_label"]  # Id Cat
           paramQTreeWidgetItem = [ self.listCategorieIn[i]["_displayLibelle"], self.listCategorieIn[i]["_label"], self.listCategorieIn[i]["_libelle"], self.listCategorieIn[i]["_clickAsso"], self.listCategorieIn[i]["mOrigine"], self.listCategorieIn[i]["mNoeud"], self.listCategorieIn[i]["_local"] ]
           nodeUser = QTreeWidgetItem(None, paramQTreeWidgetItem)
           self.design_Items(nodeUser, self.dicOutVersInDesign, _label, _color_In_OutVersIn) #For colorisation
           
           # - Recherche dans le dictionnaire si existance de l'item en balayant les ancêtres (parents) Paths
           if len(paths) == 0 :
              self.self_Cat_In.insertTopLevelItems( rowNodeIn, [ nodeUser ] )
              dictNoeudsArboIn[_label] = nodeUser
              rowNodeIn += 1
           else :
              # ======================================
              # Ajout des noeuds en fonction des ancêtres (parents) Paths
              iElem = 0
              while iElem < len(paths) : 
                 newNoeud = paths[iElem]
                 _returnAttribCategorie = returnAttribCategoriesEnFonctionLibelleTemplateCategorie(self, newNoeud, self.mListCategories)[0]
                 _lib_Categories_In     = _returnAttribCategorie["path"]
                 _libelle_Categories_In = _returnAttribCategorie["label"]
                 _local_Categories_In   = _returnAttribCategorie["origin"]
                 _noeud                 = "True" if _returnAttribCategorie["is_node"] else "False"  # si c'est un noeud pour être utilisé dans le double click, In vers Out 
                 _path_elements_In   = re.split(r'\s*[/]\s*', _lib_Categories_In) #pour découper le chemin, 

                 if _returnAttribCategorie["origin"] == "local" :
                    _In_displayLibelleNewNoeud = str(_libelle_Categories_In) + self.sepLeftTemplate + str(_path_elements_In[ -1 ]) + self.sepRightTemplate # For Affichage LIBELLE PLUS Dernier ELEMENT du chemin (paths)
                 else :
                    _In_displayLibelleNewNoeud = str(_path_elements_In[ -1 ]) + self.sepLeftTemplate + str(_libelle_Categories_In) + self.sepRightTemplate # For Affichage LIBELLE PLUS Dernier ELEMENT du chemin (paths)

                 _displayLibelleNewNoeud, _labelNewNoeud, _libelleNewNoeud, _clickAssoNewNoeud, mOrigineNewNoeud, _noeudNewNoeud, _local_CategoriesNewNoeud = _In_displayLibelleNewNoeud, _lib_Categories_In, _libelle_Categories_In, _mItemClicAssociation, 'CAT_IN', _noeud, _local_Categories_In
                 paramQTreeWidgetItem = [ _displayLibelleNewNoeud, _labelNewNoeud, _libelleNewNoeud, _clickAssoNewNoeud, mOrigineNewNoeud, _noeudNewNoeud, _local_CategoriesNewNoeud ]
                 nodeUserNewNoeud = QTreeWidgetItem(None, paramQTreeWidgetItem)
                 self.design_Items(nodeUserNewNoeud, self.dicOutVersInDesign, _labelNewNoeud, _color_In_OutVersIn) #For colorisation
                 
                 if newNoeud not in dictNoeudsArboIn : # Si l'ancêtre n'est pas dans le dictionnaire In
                    nodeUserNewNoeud.setFont(0, defineFont(self.fontCategorieInVersOut))

                    if iElem == 0 :
                       self.self_Cat_In.insertTopLevelItems( rowNodeIn, [ nodeUserNewNoeud ] )
                       self.design_Items(nodeUserNewNoeud, self.dicOutVersInDesign, _labelNewNoeud, _color_Out_InVersOut) #For colorisation
                       rowNodeIn += 1
                    else :
                       dictNoeudsArboIn[ paths[iElem - 1] ].addChild( nodeUserNewNoeud )
                       dictNoeudsArboIn[ paths[iElem - 1] ].setIcon(0, iconSource)
                       self.design_Items(nodeUserNewNoeud, self.dicOutVersInDesign, _labelNewNoeud, _color_Out_InVersOut) #For colorisation
                    dictNoeudsArboIn[ _labelNewNoeud ]  = nodeUserNewNoeud
                 iElem += 1
              # Ajout des noeuds en fonction des ancêtres (parents) Paths
              # ======================================
                 
              # Et enfin on ajoute ma catégorie   
              dictNoeudsArboIn[_labelNewNoeud].addChild( nodeUser )
              self.design_Items(nodeUserNewNoeud, self.dicOutVersInDesign, _labelNewNoeud, _color_Out_InVersOut) #For colorisation
              dictNoeudsArboIn[_labelNewNoeud].setIcon(0, iconSource)
              dictNoeudsArboIn[_label]  = nodeUser

           i += 1
        #Create Arbo IN
        # ======================================
        # ======================================
        #Create Arbo OUT
        i = 0
        while i < len(self.listCategorieOut) : 
           _lib_Categories     = self.listCategorieOut[i]["_label"]                         # path origine 
           _libelle_Categories = self.listCategorieOut[i]["_libelle"]                       # deuxième colonne dans les treeview pour le In 
           _noeud              = self.listCategorieOut[i]["mNoeud"]                         # si c'est un noeud pour être utilisé dans le double click, In vers Out 
           _local              = self.listCategorieOut[i]["_local"]                         # si c'est une catgéogorie local ou shared 
           path_elements   = re.split(r'\s*[/]\s*', _lib_Categories)                                          #pour découper le chemin, 
           paths           = [ ' / '.join(path_elements[:ii + 1] ) for ii in range(len(path_elements) - 1) ]  #Chemin des parents
           _label = self.listCategorieOut[i]["_label"]  # Id Cat
           paramQTreeWidgetItem = [ self.listCategorieOut[i]["_displayLibelle"], self.listCategorieOut[i]["_label"], self.listCategorieOut[i]["_libelle"], self.listCategorieOut[i]["_clickAsso"], self.listCategorieOut[i]["mOrigine"], self.listCategorieOut[i]["mNoeud"], self.listCategorieOut[i]["_local"] ]
           nodeUser = QTreeWidgetItem(None, paramQTreeWidgetItem)
           self.design_Items(nodeUser, self.dicInVersOutDesign, _label, _color_Out_InVersOut) #For colorisation
           
           # - Recherche dans le dictionnaire si existance de l'item en balayant les ancêtres (parents) Paths
           if len(paths) == 0 :
              self.self_Cat_Out.insertTopLevelItems( rowNodeOut, [ nodeUser ] )
              dictNoeudsArboOut[_label] = nodeUser
              rowNodeOut += 1
           else :
              # ======================================
              # Ajout des noeuds en fonction des ancêtres (parents) Paths
              iElem = 0
              while iElem < len(paths) : 
                 newNoeud = paths[iElem]
                 _returnAttribCategorie = returnAttribCategoriesEnFonctionLibelleTemplateCategorie(self, newNoeud, self.mListCategories)[0]
                 _lib_Categories_out     = _returnAttribCategorie["path"]
                 _libelle_Categories_out = _returnAttribCategorie["label"]
                 _local_Categories_out   = _returnAttribCategorie["origin"]
                 _noeud                  = "True" if _returnAttribCategorie["is_node"] else "False"  # si c'est un noeud pour être utilisé dans le double click, In vers Out 
                 _path_elements_out   = re.split(r'\s*[/]\s*', _lib_Categories_out) #pour découper le chemin, 

                 if _returnAttribCategorie["origin"] == "local" :
                    _Out_displayLibelleNewNoeud = str(_libelle_Categories_out) + self.sepLeftTemplate + str(_path_elements_out[ -1 ]) + self.sepRightTemplate # For Affichage LIBELLE PLUS Dernier ELEMENT du chemin (paths)
                 else :
                    _Out_displayLibelleNewNoeud = str(_path_elements_out[ -1 ]) + self.sepLeftTemplate + str(_libelle_Categories_out) + self.sepRightTemplate # For Affichage LIBELLE PLUS Dernier ELEMENT du chemin (paths)

                 _displayLibelleNewNoeud, _labelNewNoeud, _libelleNewNoeud, _clickAssoNewNoeud, mOrigineNewNoeud, _noeudNewNoeud, _local_CategoriesNewNoeud = _Out_displayLibelleNewNoeud, _lib_Categories_out, _libelle_Categories_out, _mItemClicAssociation, 'CAT_OUT', _noeud, _local_Categories_out
                 paramQTreeWidgetItem = [ _displayLibelleNewNoeud, _labelNewNoeud, _libelleNewNoeud, _clickAssoNewNoeud, mOrigineNewNoeud, _noeudNewNoeud, _local_CategoriesNewNoeud ]
                 nodeUserNewNoeud = QTreeWidgetItem(None, paramQTreeWidgetItem)
                 self.design_Items(nodeUserNewNoeud, self.dicInVersOutDesign, _labelNewNoeud, _color_Out_InVersOut) #For colorisation
                 
                 if newNoeud not in dictNoeudsArboOut : # Si l'ancêtre n'est pas dans le dictionnaire OUT
                    nodeUserNewNoeud.setFont(0, defineFont(self.fontCategorieInVersOut))

                    if iElem == 0 :
                       self.self_Cat_Out.insertTopLevelItems( rowNodeOut, [ nodeUserNewNoeud ] )
                       self.design_Items(nodeUserNewNoeud, self.dicInVersOutDesign, _labelNewNoeud, _color_Out_InVersOut) #For colorisation
                       rowNodeOut += 1
                    else :
                       dictNoeudsArboOut[ paths[iElem - 1] ].addChild( nodeUserNewNoeud )
                       dictNoeudsArboOut[ paths[iElem - 1] ].setIcon(0, iconSource)
                       self.design_Items(nodeUserNewNoeud, self.dicInVersOutDesign, _labelNewNoeud, _color_Out_InVersOut) #For colorisation
                    dictNoeudsArboOut[ _labelNewNoeud ]  = nodeUserNewNoeud
                 iElem += 1
              # Ajout des noeuds en fonction des ancêtres (parents) Paths
              # ======================================
                 
              # Et enfin on ajoute ma catégorie   
              dictNoeudsArboOut[_labelNewNoeud].addChild( nodeUser )
              self.design_Items(nodeUserNewNoeud, self.dicInVersOutDesign, _labelNewNoeud, _color_Out_InVersOut) #For colorisation
              dictNoeudsArboOut[_labelNewNoeud].setIcon(0, iconSource)
              dictNoeudsArboOut[_label]  = nodeUser

           i += 1
        #Create Arbo OUT
        # ======================================
        # ======================================
        self.self_Cat_In.itemClicked.connect( self.ihmsPlume_CAT_IN_OUT ) 
        self.self_Cat_Out.itemClicked.connect( self.ihmsPlume_CAT_IN_OUT ) 
        self.self_Cat_In.currentItemChanged.connect( self.ihmsPlume_CAT_IN_OUTCurrentIndexChanged )                                                      
        return

    #===============================              
    def menuContextuelPlume_CAT_IN_OUT(self, point):
        index = self.indexAt(point)
        if not index.isValid():
           return
        #-------
        if index.data(0) != None : 
           item = self.currentItem()
           if item != None :
              mItemClic_CAT_IN_OUT = item.data(1, QtCore.Qt.DisplayRole)  # id catégorie
              mItemClicAssociation = item.data(3, QtCore.Qt.DisplayRole)  # id association
              mOrigine             = item.data(4, QtCore.Qt.DisplayRole)  # Origine Cat In ou Cat OUT
              #-------
              self.groupBoxdisplayHelpFocus.setVisible(False)
              self.zoneDisplayHelpFocus.setText("")
              if mOrigine == "CAT_IN" :
                 if returnIfExisteCategorie(item) : 
                    #Affiche les attributs
                    afficheAttributs( self, self.groupBoxAttributsModeleCategorie, self.mapping_template_categories, True ) 
                    #Initialise les attributs avec valeurs
                    returnDicValuePropriete, self._selfCreateTemplate.listeThesaurus = initialiseAttributsModeleCategorie( self, mItemClic_CAT_IN_OUT, mItemClicAssociation, self.groupBoxAttributsModeleCategorie, self.mapping_template_categories, self.mListTemplateCategories, self.mListTabs, True )
                    self._selfCreateTemplate.dicValuePropriete['initialiseAttributsModeleCategorie'] = returnDicValuePropriete 

                    afficheLabelAndLibelle(self, True, True, True, True) 
                 else :   
                    #Affiche les attributs
                    afficheAttributs( self, self.groupBoxAttributsModeleCategorie, self.mapping_template_categories, False ) 
                    afficheLabelAndLibelle(self, True, True, True, False) 
                 # 
              else :   
                 #Efface les attributs
                 afficheAttributs( self, self.groupBoxAttributsModeleCategorie, self.mapping_template_categories, False ) 
                 afficheLabelAndLibelle(self, True, True, True, False) 

              self.buttonSaveOutVersIn.setEnabled(  False if (len(self.dicInVersOutDesign) == 0 and len(self.dicOutVersInDesign) == 0) else True)
              self.buttonReinitOutVersIn.setEnabled(False if (len(self.dicInVersOutDesign) == 0 and len(self.dicOutVersInDesign) == 0) else True)
              #-------
              self.treeMenu = QMenu(self)
              #-
              if returnIfExisteCategorie(item) : # Existe  
                 if item.childCount() == 0 : 
                    menuIcon = returnIcon(os.path.dirname(__file__) + ("\\icons\\buttons\\deplace_right.svg" if mOrigine == "CAT_OUT" else "\\icons\\buttons\\deplace_left.svg"))  
                    libActionAndAction = QtWidgets.QApplication.translate("CreateTemplate_ui",  "Move category", None)       
                    treeAction_addTooltip = QtWidgets.QApplication.translate("CreateTemplate_ui", libActionAndAction, None) #Déplacer la catégorie
                    self.treeAction_add = QAction(QtGui.QIcon(menuIcon), treeAction_addTooltip, self.treeMenu)
                    self.treeMenu.addAction(self.treeAction_add)
                    self.treeAction_add.setToolTip(treeAction_addTooltip)
                    self.treeAction_add.triggered.connect( lambda : self.moveCatContextuel(item, "libActionAndAction") )
                 elif item.childCount() > 0 : 
                    menuIcon = returnIcon(os.path.dirname(__file__) + ("\\icons\\buttons\\deplace_right.svg" if mOrigine == "CAT_OUT" else "\\icons\\buttons\\deplace_left.svg"))           
                    libActionAndAction1 = QtWidgets.QApplication.translate("CreateTemplate_ui",  "Move the category with its subcategories", None)       
                    treeAction_addTooltip = QtWidgets.QApplication.translate("CreateTemplate_ui", libActionAndAction1, None) # Déplacer la catégorie avec ses sous catégories 
                    self.treeAction_add = QAction(QtGui.QIcon(menuIcon), treeAction_addTooltip, self.treeMenu)
                    self.treeMenu.addAction(self.treeAction_add)
                    self.treeAction_add.setToolTip(treeAction_addTooltip)
                    self.treeAction_add.triggered.connect( lambda : self.moveCatContextuel(item, "libActionAndAction1") )
                    #-
                    menuIcon = returnIcon(os.path.dirname(__file__) + ("\\icons\\buttons\\deplace_right.svg" if mOrigine == "CAT_OUT" else "\\icons\\buttons\\deplace_left.svg"))           
                    libActionAndAction2 = QtWidgets.QApplication.translate("CreateTemplate_ui",  "Move the category without its subcategories", None)       
                    treeAction_addTooltip = QtWidgets.QApplication.translate("CreateTemplate_ui", libActionAndAction2, None) # Déplacer la catégorie sans ses sous catégories
                    self.treeAction_add = QAction(QtGui.QIcon(menuIcon), treeAction_addTooltip, self.treeMenu)
                    self.treeMenu.addAction(self.treeAction_add)
                    self.treeAction_add.setToolTip(treeAction_addTooltip)
                    self.treeAction_add.triggered.connect( lambda : self.moveCatContextuel(item, "libActionAndAction2") )
              else : # N'existe pas donc en italic ou gras ou gras italic  
                 if item.childCount() > 0 : 
                    menuIcon = returnIcon(os.path.dirname(__file__) + ("\\icons\\buttons\\deplace_right.svg" if mOrigine == "CAT_OUT" else "\\icons\\buttons\\deplace_left.svg"))           
                    libActionAndAction3 = QtWidgets.QApplication.translate("CreateTemplate_ui",  "Move subcategories", None)       
                    treeAction_addTooltip = QtWidgets.QApplication.translate("CreateTemplate_ui", libActionAndAction3, None) # Déplacer les sous catégories
                    self.treeAction_add = QAction(QtGui.QIcon(menuIcon), treeAction_addTooltip, self.treeMenu)
                    self.treeMenu.addAction(self.treeAction_add)
                    self.treeAction_add.setToolTip(treeAction_addTooltip)
                    self.treeAction_add.triggered.connect( lambda : self.moveCatContextuel(item, "libActionAndAction3") )
              #-------
              self.treeMenu.exec_(self.mapToGlobal(point))
        return
        
    #===============================              
    def ihmsPlume_CAT_IN_OUTCurrentIndexChanged(self, itemCurrent, itemPrevious):
        if itemCurrent == None : return 
        self.ihmsPlume_CAT_IN_OUT( itemCurrent, self.currentColumn() )
        return
        
    #===============================              
    def ihmsPlume_CAT_IN_OUT(self, item, column): 
        if item == None : return 
        QApplication.setOverrideCursor( QCursor( Qt.WaitCursor ) )
        
        mItemClic_CAT_IN_OUT = item.data(1, QtCore.Qt.DisplayRole)  # id catégorie
        mItemClicAssociation = item.data(3, QtCore.Qt.DisplayRole)  # id association
        mOrigine             = item.data(4, QtCore.Qt.DisplayRole)  # Origine Cat In ou Cat OUT

        self._selfCreateTemplate.groupBoxdisplayHelpFocus.setVisible(False)
        self._selfCreateTemplate.zoneDisplayHelpFocus.setText("")
        if mOrigine == "CAT_IN" :
           if returnIfExisteCategorie(item) : 
              #Affiche les attributs
              afficheAttributs( self, self.groupBoxAttributsModeleCategorie, self.mapping_template_categories, True ) 
              #Initialise les attributs avec valeurs
              returnDicValuePropriete, self._selfCreateTemplate.listeThesaurus = initialiseAttributsModeleCategorie( self, mItemClic_CAT_IN_OUT, mItemClicAssociation, self.groupBoxAttributsModeleCategorie, self.mapping_template_categories, self.mListTemplateCategories, self.mListTabs, True )
              self._selfCreateTemplate.dicValuePropriete['initialiseAttributsModeleCategorie'] = returnDicValuePropriete 
              
              afficheLabelAndLibelle(self._selfCreateTemplate, True, True, True, True)
           else :   
              #Affiche les attributs
              afficheAttributs( self, self.groupBoxAttributsModeleCategorie, self.mapping_template_categories, False ) 
              afficheLabelAndLibelle(self._selfCreateTemplate, True, True, True, False) 
           # 
        else :   
           #Efface les attributs
           afficheAttributs( self, self.groupBoxAttributsModeleCategorie, self.mapping_template_categories, False ) 
           afficheLabelAndLibelle(self._selfCreateTemplate, True, True, True, False) 
        #InfoBulle contextuelle
        self._selfCreateTemplate.buttonSaveAttribModeleCategorie.setToolTip( returnbuttonSaveAttribCategorieToolTip( mItemClic_CAT_IN_OUT, self._selfCreateTemplate.modelComboListeModeleCategorie.item(self._selfCreateTemplate.comboListeModeleCategorie.currentIndex(),0).text() ) ) 

        self._selfCreateTemplate.buttonSaveOutVersIn.setEnabled(  False if (len(self._selfCreateTemplate.dicInVersOutDesign) == 0 and len(self._selfCreateTemplate.dicOutVersInDesign) == 0) else True)
        self._selfCreateTemplate.buttonReinitOutVersIn.setEnabled(False if (len(self._selfCreateTemplate.dicInVersOutDesign) == 0 and len(self._selfCreateTemplate.dicOutVersInDesign) == 0) else True)

        QApplication.setOverrideCursor( QCursor( Qt.ArrowCursor ) )
        return

    #===============================              
    def ifExisteInCat_Out(self, _libFind) : 
        iterator = QTreeWidgetItemIterator(self.self_Cat_Out)
        _ret = False
        while iterator.value() :
           if _libFind == iterator.value().text(1) :
              _ret = True
              break
           iterator += 1
        return _ret

    #===============================              
    def fonctionTritDict(self, value):
        return value['_label']

    #===============================              
    def moveCatContextuel(self, item, libActionAndAction = None):
        if item == None : return 
        _pathIcons = os.path.dirname(__file__) + "/icons/logo"
        iconSource = returnIcon(_pathIcons + "/plume.svg")  
        _pathIcons2 = os.path.dirname(__file__) + "/icons/general"
        iconSource2 = returnIcon(_pathIcons2 + "/lock.svg")  

        # _displayLibelle Libellé affiché de la catégorie (colonne 0 in QtreeWidget)
        # _label          Nom de la catégorie             (colonne 1 in QtreeWidget)
        # _libelle        Nom du libellé de la catégorie  (colonne 2 in QtreeWidget) 
        # _clickAsso      Nom du modèle cliqué
        # mOrigine        Sens (In vers Out ou vice Versa
        # mNoeud          Est-ce un Noeud
        # local ou shared
        mItemClic_displayLibelle_CAT_IN_OUT = item.data(0, QtCore.Qt.DisplayRole)  # Libellé affiché
        mItemClic_CAT_IN_OUT         = item.data(1, QtCore.Qt.DisplayRole)  # id catégorie
        mItemClic_libelle_CAT_IN_OUT = item.data(2, QtCore.Qt.DisplayRole)  # deuxième colonne dans les treeview
        mItemClicAssociation         = item.data(3, QtCore.Qt.DisplayRole)  # id association
        mOrigine                     = item.data(4, QtCore.Qt.DisplayRole)  # Origine Cat In ou Cat OUT
        mNoeud                       = item.data(5, QtCore.Qt.DisplayRole)  # si c'est un noeud
        mlocal                       = item.data(6, QtCore.Qt.DisplayRole)  # local ou shared
        """
        EXEMPLE
        {'_displayLibelle': 'dcat:distribution *Distribution*',               {'_displayLibelle': 'dcat:contactPoint *Point de contact*', 
         '_label'         : 'dcat:distribution',                               '_label'         : 'dcat:distribution / dcat:accessService / dcat:contactPoint', 
         '_libelle'       : 'Distribution',                                    '_libelle'       : 'Point de contact', 
         '_clickAsso'     : '23',                                              '_clickAsso'     : '23',
         'mOrigine'       : 'CAT_IN',                                          'mOrigine'       : 'CAT_IN', 
         'mNoeud'         : 'True',                                            'mNoeud'         : 'True',
         '_local'         : 'local'}                                           '_local'         : 'shared'}

                    libActionAndAction = "Move category"         
                    libActionAndAction = "Move the category with its subcategories"         
                    libActionAndAction = "Move the category without its subcategories"     
                    libActionAndAction = "Move subcategories"        

        """
        _dicTempoDeleteChildren = dict(zip( ["_displayLibelle",                  "_label",              "_libelle",                  "_clickAsso",         "mOrigine", "mNoeud", "_local"], \
                              [mItemClic_displayLibelle_CAT_IN_OUT, mItemClic_CAT_IN_OUT, mItemClic_libelle_CAT_IN_OUT, mItemClicAssociation, mOrigine, mNoeud, mlocal ] ))
        _dicTempoAppendChildren = dict(zip( ["_displayLibelle",                  "_label",              "_libelle",                  "_clickAsso",         "mOrigine", "mNoeud", "_local"], \
                              [mItemClic_displayLibelle_CAT_IN_OUT, mItemClic_CAT_IN_OUT, mItemClic_libelle_CAT_IN_OUT, mItemClicAssociation, ("CAT_OUT" if mOrigine == "CAT_IN" else "CAT_IN"), mNoeud, mlocal] ))
        #if libActionAndAction in ["Move the category with its subcategories", "Move category", "Move subcategories"] :
        if libActionAndAction in ["libActionAndAction", "libActionAndAction1", "libActionAndAction3"] :

           if mOrigine == "CAT_IN" :
              # Gestion Item Click and Children 
              _dicTempoAppendChildren, _dicTempoDeleteChildren = returnListChildren(self, mItemClic_CAT_IN_OUT, self.listCategorieIn, mOrigine)
              # 
              iElem = 0
              while iElem < len(_dicTempoAppendChildren) : 
                  self.listCategorieOut.append(_dicTempoAppendChildren[iElem])
                  _index = returnIndexInListeCategorie( _dicTempoAppendChildren[iElem]["_label"], self.listCategorieIn )
                  del self.listCategorieIn[_index]

                  self.dicInVersOutDesign[_dicTempoAppendChildren[iElem]["_label"]] = (mItemClicAssociation, mlocal) 
                  if _dicTempoAppendChildren[iElem]["_label"] in self.dicOutVersInDesign : del self.dicOutVersInDesign[_dicTempoAppendChildren[iElem]["_label"]]   # Suppprimer la clé dans l'autre dictionnaire
                  iElem += 1
              # Gestion Item Click and Children 
              # -
           elif mOrigine == "CAT_OUT" :   
              # Gestion Item Click and Children 
              _dicTempoAppendChildren, _dicTempoDeleteChildren = returnListChildren(self, mItemClic_CAT_IN_OUT, self.listCategorieOut, mOrigine)
              # 
              iElem = 0
              while iElem < len(_dicTempoAppendChildren) : 
                  self.listCategorieIn.append(_dicTempoAppendChildren[iElem])
                  _index = returnIndexInListeCategorie( _dicTempoAppendChildren[iElem]["_label"], self.listCategorieOut )
                  del self.listCategorieOut[_index]

                  self.dicOutVersInDesign[_dicTempoAppendChildren[iElem]["_label"]] = (mItemClicAssociation, mlocal)
                  if _dicTempoAppendChildren[iElem]["_label"] in self.dicInVersOutDesign :  del self.dicInVersOutDesign[_dicTempoAppendChildren[iElem]["_label"]]   # Suppprimer la clé dans l'autre dictionnaire
                  iElem += 1
              # Gestion Item Click and Children 

        elif libActionAndAction == "libActionAndAction2" :

           if mOrigine == "CAT_IN" :
              self.listCategorieOut.append(_dicTempoAppendChildren)
              _index = returnIndexInListeCategorie( _dicTempoAppendChildren["_label"], self.listCategorieIn )
              del self.listCategorieIn[_index]

              self.dicInVersOutDesign[_dicTempoAppendChildren["_label"]] = (mItemClicAssociation, mlocal) 
              if _dicTempoAppendChildren["_label"] in self.dicOutVersInDesign : del self.dicOutVersInDesign[_dicTempoAppendChildren["_label"]]   # Suppprimer la clé dans l'autre dictionnaire
              # Gestion Item Click and Children 
              # -
           elif mOrigine == "CAT_OUT" :   
              self.listCategorieIn.append(_dicTempoAppendChildren)
              _index = returnIndexInListeCategorie( _dicTempoAppendChildren["_label"], self.listCategorieOut )
              del self.listCategorieOut[_index]

              self.dicOutVersInDesign[_dicTempoAppendChildren["_label"]] = (mItemClicAssociation, mlocal)
              if _dicTempoAppendChildren["_label"] in self.dicInVersOutDesign :  del self.dicInVersOutDesign[_dicTempoAppendChildren["_label"]]   # Suppprimer la clé dans l'autre dictionnaire
              # Gestion Item Click and Children 

        self.listCategorieIn  = sorted(self.listCategorieIn, key = self.fonctionTritDict, reverse=False)
        self.listCategorieOut = sorted(self.listCategorieOut, key = self.fonctionTritDict, reverse=False)
        # -
        self.self_Cat_In.clear()
        self.self_Cat_Out.clear()
        self.self_Cat_In.affiche_CAT_IN_OUT(  self, mItemClicAssociation, self.self_Cat_In, self.self_Cat_Out, action = True, header = self._origineHeaderLabelsIn)
        self.self_Cat_Out.affiche_CAT_IN_OUT( self, mItemClicAssociation, self.self_Cat_In, self.self_Cat_Out,                header = self._origineHeaderLabelsOut) # Uniquement pour instancier OneShot
        #Efface les attributs
        afficheAttributs( self._selfCreateTemplate, self._selfCreateTemplate.groupBoxAttributsModeleCategorie, self._selfCreateTemplate.mapping_template_categories, False )
        #
        afficheLabelAndLibelle(self._selfCreateTemplate, True, True, True, False) 
        self._selfCreateTemplate.buttonSaveOutVersIn.setEnabled(  False if (len(self.dicInVersOutDesign) == 0 and len(self.dicOutVersInDesign) == 0) else True)
        self._selfCreateTemplate.buttonReinitOutVersIn.setEnabled(False if (len(self.dicInVersOutDesign) == 0 and len(self.dicOutVersInDesign) == 0) else True)
        return
        
    #===============================              
    def moveDoubleClicked(self, item, column):
        if item == None : return 
        _pathIcons = os.path.dirname(__file__) + "/icons/logo"
        iconSource = returnIcon(_pathIcons + "/plume.svg")  
        _pathIcons2 = os.path.dirname(__file__) + "/icons/general"
        iconSource2 = returnIcon(_pathIcons2 + "/lock.svg")  

        # _displayLibelle Libellé affiché de la catégorie (colonne 0 in QtreeWidget)
        # _label          Nom de la catégorie             (colonne 1 in QtreeWidget)
        # _libelle        Nom du libellé de la catégorie  (colonne 2 in QtreeWidget) 
        # _clickAsso      Nom du modèle cliqué
        # mOrigine        Sens (In vers Out ou vice Versa
        # mNoeud          Est-ce un Noeud
        # local ou shared
        mItemClic_displayLibelle_CAT_IN_OUT = item.data(0, QtCore.Qt.DisplayRole)  # Libellé affiché
        mItemClic_CAT_IN_OUT         = item.data(1, QtCore.Qt.DisplayRole)  # id catégorie
        mItemClic_libelle_CAT_IN_OUT = item.data(2, QtCore.Qt.DisplayRole)  # deuxième colonne dans les treeview
        mItemClicAssociation         = item.data(3, QtCore.Qt.DisplayRole)  # id association
        mOrigine                     = item.data(4, QtCore.Qt.DisplayRole)  # Origine Cat In ou Cat OUT
        mNoeud                       = item.data(5, QtCore.Qt.DisplayRole)  # si c'est un noeud
        mlocal                       = item.data(6, QtCore.Qt.DisplayRole)  # local ou shared
        """
        EXEMPLE
        {'_displayLibelle': 'dcat:distribution *Distribution*',               {'_displayLibelle': 'dcat:contactPoint *Point de contact*', 
         '_label'         : 'dcat:distribution',                               '_label'         : 'dcat:distribution / dcat:accessService / dcat:contactPoint', 
         '_libelle'       : 'Distribution',                                    '_libelle'       : 'Point de contact', 
         '_clickAsso'     : '23',                                              '_clickAsso'     : '23',
         'mOrigine'       : 'CAT_IN',                                          'mOrigine'       : 'CAT_IN', 
         'mNoeud'         : 'True',                                            'mNoeud'         : 'True',
         '_local'         : 'local'}                                           '_local'         : 'shared'}
        """
        _dicTempoAppendChildren, _dicTempoDeleteChildren = [], []
        if mOrigine == "CAT_IN" :
           # Gestion Item Click and Children 
           _dicTempoAppendChildren, _dicTempoDeleteChildren = returnListChildren(self, mItemClic_CAT_IN_OUT, self.listCategorieIn, mOrigine)
           # 
           iElem = 0
           while iElem < len(_dicTempoAppendChildren) : 
               self.listCategorieOut.append(_dicTempoAppendChildren[iElem])
               _index = returnIndexInListeCategorie( _dicTempoAppendChildren[iElem]["_label"], self.listCategorieIn )
               del self.listCategorieIn[_index]

               self.dicInVersOutDesign[_dicTempoAppendChildren[iElem]["_label"]] = (mItemClicAssociation, mlocal) 
               if _dicTempoAppendChildren[iElem]["_label"] in self.dicOutVersInDesign : del self.dicOutVersInDesign[_dicTempoAppendChildren[iElem]["_label"]]   # Suppprimer la clé dans l'autre dictionnaire
               iElem += 1
           # Gestion Item Click and Children 
           # -
        elif mOrigine == "CAT_OUT" :   
           # Gestion Item Click and Children 
           _dicTempoAppendChildren, _dicTempoDeleteChildren = returnListChildren(self, mItemClic_CAT_IN_OUT, self.listCategorieOut, mOrigine)
           # 
           iElem = 0
           while iElem < len(_dicTempoAppendChildren) : 
               self.listCategorieIn.append(_dicTempoAppendChildren[iElem])
               _index = returnIndexInListeCategorie( _dicTempoAppendChildren[iElem]["_label"], self.listCategorieOut )
               del self.listCategorieOut[_index]

               self.dicOutVersInDesign[_dicTempoAppendChildren[iElem]["_label"]] = (mItemClicAssociation, mlocal)
               if _dicTempoAppendChildren[iElem]["_label"] in self.dicInVersOutDesign :  del self.dicInVersOutDesign[_dicTempoAppendChildren[iElem]["_label"]]   # Suppprimer la clé dans l'autre dictionnaire
               iElem += 1
           # Gestion Item Click and Children 
           # -
           
        self.listCategorieIn  = sorted(self.listCategorieIn,  key = self.fonctionTritDict, reverse=False)
        self.listCategorieOut = sorted(self.listCategorieOut, key = self.fonctionTritDict, reverse=False)
        # -
        self.self_Cat_In.clear()
        self.self_Cat_Out.clear()
        self.self_Cat_In.affiche_CAT_IN_OUT(  self, mItemClicAssociation, self.self_Cat_In, self.self_Cat_Out, action = True, header = self._origineHeaderLabelsIn)
        self.self_Cat_Out.affiche_CAT_IN_OUT( self, mItemClicAssociation, self.self_Cat_In, self.self_Cat_Out,                header = self._origineHeaderLabelsOut) # Uniquement pour instancier OneShot
        #Efface les attributs
        afficheAttributs( self._selfCreateTemplate, self._selfCreateTemplate.groupBoxAttributsModeleCategorie, self._selfCreateTemplate.mapping_template_categories, False )
        #
        afficheLabelAndLibelle(self._selfCreateTemplate, True, True, True, False) 
        self._selfCreateTemplate.buttonSaveOutVersIn.setEnabled(  False if (len(self.dicInVersOutDesign) == 0 and len(self.dicOutVersInDesign) == 0) else True)
        self._selfCreateTemplate.buttonReinitOutVersIn.setEnabled(False if (len(self.dicInVersOutDesign) == 0 and len(self.dicOutVersInDesign) == 0) else True)
        return

    #===============================              
    def returnValueItemParent(self, item, column):          
        if item == None : return None 
        mReturnValueItemParent, mItem = [], item
        while True :
           mReturnValueItemParent.append(mItem.data(1, QtCore.Qt.DisplayRole))
           mParentItem = mItem.parent()
           if mParentItem != None :
              mItem = mParentItem
           else :
              break
              
        #Supprime la dernière valeur      
        if len(mReturnValueItemParent) > 0 : del mReturnValueItemParent[0]
        _mReturnValueItemParent = list(reversed(mReturnValueItemParent))
        return _mReturnValueItemParent

    #===============================              
    def returnValueItem(self, item, column):
        if item == None : return None 
        mReturnValueItem, mItem = [], item
        while True :
           mReturnValueItem.append(mItem.data(column, QtCore.Qt.DisplayRole))
           mParentItem = mItem.parent()
           if mParentItem != None :
              mItem = mParentItem
           else :
              break
        return mReturnValueItem

#========================================================     
#========================================================     
# Class pour le tree View Ressource MODELE 
class TREEVIEWMODELE(QTreeWidget):
    customMimeType = "text/plain"

    #===============================              
    def __init__(self, *args):
        QTreeWidget.__init__(self, *args)
        self.setColumnCount(1)
        self.hideColumn (0)   # For hide ID
        self.setHeaderLabels(["Noms", "Libellés"])
        self.setSelectionMode(QAbstractItemView.SingleSelection	)  
        self.mnodeToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Right click to add / delete a model", None)         #Click droit pour supprimer un Modèle
        return

    #===============================              
    def afficheMODELE(self, _selfCreateTemplate, listeModeleCol1, listeModeleCol2):
        self.groupBoxAttributsModele                 = _selfCreateTemplate.groupBoxAttributsModele
        self.mapping_templates                       = _selfCreateTemplate.mapping_templates
        self.groupBoxdisplayHelpFocusAttributsModele = _selfCreateTemplate.groupBoxdisplayHelpFocusAttributsModele
        self.zoneDisplayHelpFocusAttributsModele     = _selfCreateTemplate.zoneDisplayHelpFocusAttributsModele
        self.listLangList                            = _selfCreateTemplate.listLangList
        

        self.mListTemplates          = _selfCreateTemplate.mListTemplates
        self._selfCreateTemplate     = _selfCreateTemplate
        #---
        self.header().setStretchLastSection(False)
        self.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        i = 0
        while i in range(len(listeModeleCol1)) :
            nodeUrlUser = QTreeWidgetItem(None, [ str(listeModeleCol1[i]), str(listeModeleCol2[i]) ])
            self.insertTopLevelItems( 0, [ nodeUrlUser ] )
            nodeUrlUser.setToolTip(0, "{}".format(self.mnodeToolTip))
            nodeUrlUser.setToolTip(1, "{}".format(self.mnodeToolTip))
            i += 1
 
        self.itemClicked.connect( self.ihmsPlumeMODELE ) 
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect( self.menuContextuelPlumeMODELE)
        self.expandAll()
        return
        
    #===============================              
    def menuContextuelPlumeMODELE(self, point):
        self._selfCreateTemplate.groupBoxdisplayHelpFocusAttributsModele.setVisible(False)
        self._selfCreateTemplate.zoneDisplayHelpFocusAttributsModele.setText("")
        index = self.indexAt(point)
        if not index.isValid():
           return
        #-------
        if index.data(0) != None : 
           self.treeMenu = QMenu(self)
           #-
           menuIcon = returnIcon(os.path.dirname(__file__) + "\\icons\\buttons\\plus_button.svg")          
           treeAction_addTooltip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Add model", None)  #Supprimer le modèle
           self.treeAction_add = QAction(QtGui.QIcon(menuIcon), treeAction_addTooltip, self.treeMenu)
           self.treeMenu.addAction(self.treeAction_add)
           self.treeAction_add.setToolTip(treeAction_addTooltip)
           self.treeAction_add.triggered.connect( self.ihmsPlumeAdd )
           #-
           menuIcon = returnIcon(os.path.dirname(__file__) + "\\icons\\general\\delete.svg")          
           treeAction_delTooltip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Remove model", None)  #Supprimer le modèle
           self.treeAction_del = QAction(QtGui.QIcon(menuIcon), treeAction_delTooltip, self.treeMenu)
           self.treeMenu.addAction(self.treeAction_del)
           self.treeAction_del.setToolTip(treeAction_delTooltip)
           self.treeAction_del.triggered.connect( self.ihmsPlumeDel )
           #-------
           self.treeMenu.exec_(self.mapToGlobal(point))
        return
        
    #===============================              
    def ihmsPlumeMODELE(self, item, column): 
        mItemClicModele = item.data(0, QtCore.Qt.DisplayRole)
        self.modeleActif = mItemClicModele
        
        #=== Nécessaire pour récupérer les valeurs initiales et/ ou sauvegardées              
        with self._selfCreateTemplate.Dialog.safe_pg_connection("continue") :
           #------ DATA template 
           mKeySql = queries.query_read_meta_template()
           r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self._selfCreateTemplate.Dialog.mConnectEnCours, mKeySql, optionRetour = "fetchall")
           self.mListTemplates = [row[0] for row in r]
           listeModeleCol1, listeModeleCol2 = returnList_Id_Label( self.mListTemplates )
           self.modeleActif = listeModeleCol1[0] #Pour la première initialisation
        #------
        self._selfCreateTemplate.buttonAddModele.setVisible(True)
        #Affiche les attributs
        afficheAttributs( self, self.groupBoxAttributsModele, self.mapping_templates, True ) 
        self._selfCreateTemplate.buttonAddModele.setVisible(True)
        #Initialise les attributs avec valeurs
        returnDicValuePropriete, self._selfCreateTemplate.listeThesaurus = initialiseAttributsModelesCategoriesOnglets( self, mItemClicModele, self.groupBoxAttributsModele, self.mapping_templates, self.mListTemplates, True )
        self._selfCreateTemplate.dicValuePropriete['initialiseAttributsModele'] = returnDicValuePropriete 

        self._selfCreateTemplate.groupBoxdisplayHelpFocusAttributsModele.setVisible(False)
        self._selfCreateTemplate.zoneDisplayHelpFocusAttributsModele.setText("")
        return

    #===============================              
    def ihmsPlumeUpdateModele(self, mDialog, mId):
        #===============================              
        dicForQuerieForAddModele = returnListObjKeyValue(self._selfCreateTemplate, self.groupBoxAttributsModele, self.mapping_templates, 'initialiseAttributsModele')

        with self._selfCreateTemplate.Dialog.safe_pg_connection("continue") :
           mKeySql = queries.query_insert_or_update_meta_template(dicForQuerieForAddModele)
           r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self._selfCreateTemplate.Dialog.mConnectEnCours, mKeySql, optionRetour = "fetchone")
           self._selfCreateTemplate.Dialog.mConnectEnCours.commit()
        with self._selfCreateTemplate.Dialog.safe_pg_connection("continue") :
           #- Réinit
           mKeySql = queries.query_read_meta_template()
           r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self._selfCreateTemplate.Dialog.mConnectEnCours, mKeySql, optionRetour = "fetchall")
           self.mListTemplates = [row[0] for row in r]
           listeModeleCol1, listeModeleCol2 = returnList_Id_Label( self.mListTemplates )
        self.clear()
        self.afficheMODELE(self._selfCreateTemplate, listeModeleCol1, listeModeleCol2)
        self._selfCreateTemplate.groupBoxdisplayHelpFocusAttributsModele.setVisible(False)
        self._selfCreateTemplate.zoneDisplayHelpFocusAttributsModele.setText("")
        return

    #===============================              
    def ihmsPlumeAdd(self):
        #===============================              
        afficheAttributs( self, self.groupBoxAttributsModele, self.mapping_templates, True ) 
        self._selfCreateTemplate.buttonAddModele.setVisible(True)
        returnDicValuePropriete, self._selfCreateTemplate.listeThesaurus = initialiseAttributsModelesCategoriesOnglets( self, "", self.groupBoxAttributsModele, self.mapping_templates, self.mListTemplates, True, "Vierge" )
        self._selfCreateTemplate.dicValuePropriete['initialiseAttributsModele'] = returnDicValuePropriete 
 
        self._selfCreateTemplate.groupBoxdisplayHelpFocusAttributsModele.setVisible(False)
        self._selfCreateTemplate.zoneDisplayHelpFocusAttributsModele.setText("")
        return
                
    #===============================              
    def ihmsPlumeDel(self): 
        current_item = self.currentItem()           #itemCourant
        self.ihmsPlumeMODELE( current_item, None )  #Affiche les attributs pour impélmenter le dicForQuerieForAddModele
        self.takeTopLevelItem(self.indexOfTopLevelItem(current_item))
        #
        dicForQuerieForAddModele = returnListObjKeyValue(self, self.groupBoxAttributsModele, self.mapping_templates, 'initialiseAttributsModele')
        with self._selfCreateTemplate.Dialog.safe_pg_connection("continue") :
           mKeySql = queries.query_delete_meta_template(dicForQuerieForAddModele)
           r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self._selfCreateTemplate.Dialog.mConnectEnCours, mKeySql, optionRetour = None)
           self._selfCreateTemplate.Dialog.mConnectEnCours.commit()
        #Efface les attributs
        afficheAttributs( self, self.groupBoxAttributsModele, self.mapping_templates, False ) 
        self._selfCreateTemplate.buttonAddModele.setVisible(False)
        self._selfCreateTemplate.flagNewModele = True
        self._selfCreateTemplate.groupBoxdisplayHelpFocusAttributsModele.setVisible(False)
        self._selfCreateTemplate.zoneDisplayHelpFocusAttributsModele.setText("")
        return

#========================================================     
#========================================================     
# Class pour le tree View Ressource CATEGORIE 
class TREEVIEWCATEGORIE(QTreeWidget):
    customMimeType = "text/plain"

    #===============================              
    def __init__(self, *args):
        QTreeWidget.__init__(self, *args)
        self.setColumnCount(1)
        self.setHeaderLabels(["Identifiant et chemin"])  
        self.setSelectionMode(QAbstractItemView.SingleSelection	)  
        self.mnodeToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Right click to add / delete a category", None)         #Click droit pour supprimer un Modèle
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.menuContextuelPlumeCATEGORIE) 
        return

    #===============================              
    def afficheCATEGORIE(self, _selfCreateTemplate, listeRessourceCategorie):
        _pathIcons = os.path.dirname(__file__) + "/icons/logo"
        iconSource = returnIcon(_pathIcons + "/plume.svg")  
        self.groupBoxAttributsCategorie           = _selfCreateTemplate.groupBoxAttributsCategorie
        self.mapping_categories                   = _selfCreateTemplate.mapping_categories
        self.mListCategories                      = _selfCreateTemplate.mListCategories   
        self._selfCreateTemplate                  = _selfCreateTemplate
        self.sepLeftTemplate                      = _selfCreateTemplate.sepLeftTemplate
        self.sepRightTemplate                     = _selfCreateTemplate.sepRightTemplate
        self.fontCategorieInVersOut               = _selfCreateTemplate.fontCategorieInVersOut
        self.groupBoxdisplayHelpFocusAttributsCategorie = _selfCreateTemplate.groupBoxdisplayHelpFocusAttributsCategorie
        self.zoneDisplayHelpFocusAttributsCategorie = _selfCreateTemplate.zoneDisplayHelpFocusAttributsCategorie
        _selfCreateTemplate.listeRessourceCategorie = listeRessourceCategorie 
        self.listeRessourceCategorie                = _selfCreateTemplate.listeRessourceCategorie
        self.listLangList                           = _selfCreateTemplate.listLangList
        #---
        self.header().setStretchLastSection(False)
        self.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        # ======================================
        # ======================================
        dictNoeudsArboIn  , rowNodeIn  = {}, 0 
        #Create Arbo 
        i = 0
        while i < len(self.listeRessourceCategorie) : 
           _lib_Categories     = self.listeRessourceCategorie[i]["_label"]                         # path origine 
           _libelle_Categories = self.listeRessourceCategorie[i]["_libelle"]                       # deuxième colonne dans les treeview pour le In 
           _noeud              = self.listeRessourceCategorie[i]["mNoeud"]                         # si c'est un noeud pour être utilisé dans le double click, In vers Out 
           path_elements       = re.split(r'\s*[/]\s*', _lib_Categories)                                          #pour découper le chemin, 
           paths               = [ ' / '.join(path_elements[:ii + 1] ) for ii in range(len(path_elements) - 1) ]  #Chemin des parents
           _label              = self.listeRessourceCategorie[i]["_label"]  # Id Cat
           paramQTreeWidgetItem = [ self.listeRessourceCategorie[i]["_displayLibelle"], self.listeRessourceCategorie[i]["_label"], self.listeRessourceCategorie[i]["_libelle"], "", "", self.listeRessourceCategorie[i]["mNoeud"] ]
           nodeUser = QTreeWidgetItem(None, paramQTreeWidgetItem)
           
           # - Recherche dans le dictionnaire si existance de l'item en balayant les ancêtres (parents) Paths
           if len(paths) == 0 :
              self.insertTopLevelItems( rowNodeIn, [ nodeUser ] )
              dictNoeudsArboIn[_label] = nodeUser
              rowNodeIn += 1
           else :
              # ======================================
              # Ajout des noeuds en fonction des ancêtres (parents) Paths
              iElem = 0
              while iElem < len(paths) : 
                 newNoeud = paths[iElem]
                 _returnAttribCategorie = returnAttribCategoriesEnFonctionLibelleTemplateCategorie(self, newNoeud, self.mListCategories)[0]
                 _lib_Categories_In     = _returnAttribCategorie["path"]
                 _libelle_Categories_In = _returnAttribCategorie["label"]
                 _noeud                  = "True" if _returnAttribCategorie["is_node"] else "False"  # si c'est un noeud pour être utilisé dans le double click, In vers Out 
                 _path_elements_In   = re.split(r'\s*[/]\s*', _lib_Categories_In) #pour découper le chemin, 

                 if _returnAttribCategorie["origin"] == "local" :
                    _In_displayLibelleNewNoeud = str(_libelle_Categories_In) + self.sepLeftTemplate + str(_path_elements_In[ -1 ]) + self.sepRightTemplate # For Affichage LIBELLE PLUS Dernier ELEMENT du chemin (paths)
                 else :
                    _In_displayLibelleNewNoeud = str(_path_elements_In[ -1 ]) + self.sepLeftTemplate + str(_libelle_Categories_In) + self.sepRightTemplate # For Affichage LIBELLE PLUS Dernier ELEMENT du chemin (paths)

                 _displayLibelleNewNoeud, _labelNewNoeud, _libelleNewNoeud, _clickAssoNewNoeud, mOrigineNewNoeud, _noeudNewNoeud = _In_displayLibelleNewNoeud, _lib_Categories_In, _libelle_Categories_In, "", "", _noeud
                 paramQTreeWidgetItem = [ _displayLibelleNewNoeud, _labelNewNoeud, _libelleNewNoeud, _clickAssoNewNoeud, mOrigineNewNoeud, _noeudNewNoeud ]
                 nodeUserNewNoeud = QTreeWidgetItem(None, paramQTreeWidgetItem)
                 
                 if newNoeud not in dictNoeudsArboIn : # Si l'ancêtre n'est pas dans le dictionnaire In
                    nodeUserNewNoeud.setFont(0, defineFont(self.fontCategorieInVersOut))

                    if iElem == 0 :
                       self.insertTopLevelItems( rowNodeIn, [ nodeUserNewNoeud ] )
                       rowNodeIn += 1
                    else :
                       dictNoeudsArboIn[ paths[iElem - 1] ].addChild( nodeUserNewNoeud )
                       dictNoeudsArboIn[ paths[iElem - 1] ].setIcon(0, iconSource)
                    dictNoeudsArboIn[ _labelNewNoeud ]  = nodeUserNewNoeud
                 iElem += 1
              # Ajout des noeuds en fonction des ancêtres (parents) Paths
              # ======================================
                 
              # Et enfin on ajoute ma catégorie   
              dictNoeudsArboIn[_labelNewNoeud].addChild( nodeUser )
              dictNoeudsArboIn[_labelNewNoeud].setIcon(0, iconSource)
              dictNoeudsArboIn[_label]  = nodeUser

           i += 1
        #Create Arbo 
        
        self.itemClicked.connect( self.ihmsPlumeCATEGORIE ) 
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect( self.menuContextuelPlumeCATEGORIE)
        self.listeRessourceCategorie              = listeRessourceCategorie
        return
        
    #===============================              
    def menuContextuelPlumeCATEGORIE(self, point):
        self._selfCreateTemplate.groupBoxdisplayHelpFocusAttributsCategorie.setVisible(False)
        self._selfCreateTemplate.zoneDisplayHelpFocusAttributsCategorie.setText("")
        index = self.indexAt(point)
        #-------
        with self._selfCreateTemplate.Dialog.safe_pg_connection("continue") :
           mKeySql = queries.query_read_meta_categorie()
           r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self._selfCreateTemplate.Dialog.mConnectEnCours, mKeySql, optionRetour = "fetchall")
           self.mListCategories = [row[0] for row in r]
        
        if len(self.mListCategories) == 0 : 
           self.treeMenu = QMenu(self)
           menuIcon = returnIcon(os.path.dirname(__file__) + "\\icons\\buttons\\plus_button.svg")          
           treeAction_addTooltip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Add category", None)  #Supprimer le modèle
           self.treeAction_add = QAction(QtGui.QIcon(menuIcon), treeAction_addTooltip, self.treeMenu)
           self.treeMenu.addAction(self.treeAction_add)
           self.treeAction_add.setToolTip(treeAction_addTooltip)
           self.treeAction_add.triggered.connect( self.ihmsPlumeAdd )
           #-------
           self.treeMenu.exec_(self.mapToGlobal(point))        
        else :   
           if index.data(0) != None : 
              self.treeMenu = QMenu(self)
              menuIcon = returnIcon(os.path.dirname(__file__) + "\\icons\\buttons\\plus_button.svg")          
              treeAction_addTooltip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Add category", None)  #Supprimer le modèle
              self.treeAction_add = QAction(QtGui.QIcon(menuIcon), treeAction_addTooltip, self.treeMenu)
              self.treeMenu.addAction(self.treeAction_add)
              self.treeAction_add.setToolTip(treeAction_addTooltip)
              self.treeAction_add.triggered.connect( self.ihmsPlumeAdd )
              
              menuIcon = returnIcon(os.path.dirname(__file__) + "\\icons\\general\\delete.svg")          
              treeAction_delTooltip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Remove category", None)  #Supprimer le modèle
              self.treeAction_del = QAction(QtGui.QIcon(menuIcon), treeAction_delTooltip, self.treeMenu)
              self.treeMenu.addAction(self.treeAction_del)
              self.treeAction_del.setToolTip(treeAction_delTooltip)
              self.treeAction_del.triggered.connect( self.ihmsPlumeDel )
              #-------
              self.treeMenu.exec_(self.mapToGlobal(point))        
        return
        
    #===============================              
    def ihmsPlumeCATEGORIE(self, item, column): 
        mItemClicCategorie = item.data(1, QtCore.Qt.DisplayRole)
        self.categorieActif = mItemClicCategorie
        
        if returnIfExisteCategorie(item) : 
           #=== Nécessaire pour récupérer les valeurs initiales et/ ou sauvegardées              
           with self._selfCreateTemplate.Dialog.safe_pg_connection("continue") :
              #------ DATA template 
              mKeySql = queries.query_read_meta_categorie()
              r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self._selfCreateTemplate.Dialog.mConnectEnCours, mKeySql, optionRetour = "fetchall")
              self.mListCategories = [row[0] for row in r]
              listeCategorieCol1, listeCategorieCol2 = returnList_Id_Label( self.mListCategories )
              self.categorieActif = listeCategorieCol1[0] #Pour la première initialisation
           #------
           self._selfCreateTemplate.buttonAddCategorie.setVisible(True)
           #Affiche les attributs
           afficheAttributs( self, self.groupBoxAttributsCategorie, self.mapping_categories, True ) 
           self._selfCreateTemplate.buttonAddCategorie.setVisible(True)
           #Initialise les attributs avec valeurs
           returnDicValuePropriete, self._selfCreateTemplate.listeThesaurus = initialiseAttributsModelesCategoriesOnglets( self, mItemClicCategorie, self.groupBoxAttributsCategorie, self.mapping_categories, self.mListCategories, True )
           self._selfCreateTemplate.dicValuePropriete['initialiseAttributsCategorie'] = returnDicValuePropriete 

        else :    
           #Affiche les attributs
           afficheAttributs( self, self.groupBoxAttributsCategorie, self.mapping_categories, False ) 
           self._selfCreateTemplate.buttonAddCategorie.setVisible(False)

        self._selfCreateTemplate.groupBoxdisplayHelpFocusAttributsCategorie.setVisible(False)
        self._selfCreateTemplate.zoneDisplayHelpFocusAttributsCategorie.setText("")
        return

    #===============================              
    def ihmsPlumeUpdateCategorie(self, mDialog, mId):
        #===============================              
        dicForQuerieForAddCategorie = returnListObjKeyValue(self, self.groupBoxAttributsCategorie, self.mapping_categories, 'initialiseAttributsCategorie')
        with self._selfCreateTemplate.Dialog.safe_pg_connection("continue") :
           mKeySql = queries.query_insert_or_update_meta_categorie(dicForQuerieForAddCategorie)
           r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self._selfCreateTemplate.Dialog.mConnectEnCours, mKeySql, optionRetour = "fetchone")
           self._selfCreateTemplate.Dialog.mConnectEnCours.commit()
        with self._selfCreateTemplate.Dialog.safe_pg_connection("continue") :
           #- Réinit
           mKeySql = queries.query_read_meta_categorie()
           r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self._selfCreateTemplate.Dialog.mConnectEnCours, mKeySql, optionRetour = "fetchall")
           self.mListCategories = [row[0] for row in r]

        if len(self.mListCategories)  > 0 : 
           listeRessourceCategorie = returnListRessourceCategorie( self, self.mListCategories )
        else :   
           listeRessourceCategorie = []
        self.clear()
        self.afficheCATEGORIE(self._selfCreateTemplate, listeRessourceCategorie)
        self._selfCreateTemplate.groupBoxdisplayHelpFocusAttributsCategorie.setVisible(False)
        self._selfCreateTemplate.zoneDisplayHelpFocusAttributsCategorie.setText("")
        return

    #===============================              
    def ihmsPlumeAdd(self):
        #===============================              
        afficheAttributs( self, self.groupBoxAttributsCategorie, self.mapping_categories, True ) 
        self._selfCreateTemplate.buttonAddCategorie.setVisible(True)
        returnDicValuePropriete, self._selfCreateTemplate.listeThesaurus = initialiseAttributsModelesCategoriesOnglets( self, "", self.groupBoxAttributsCategorie, self.mapping_categories, self.mListCategories, True, "Vierge" ) 
        self._selfCreateTemplate.dicValuePropriete['initialiseAttributsCategorie'] = returnDicValuePropriete 

        self._selfCreateTemplate.groupBoxdisplayHelpFocusAttributsCategorie.setVisible(False)
        self._selfCreateTemplate.zoneDisplayHelpFocusAttributsCategorie.setText("")
        return
                
    #===============================              
    def ihmsPlumeDel(self): 
        current_item = self.currentItem()           #itemCourant
        self.ihmsPlumeCATEGORIE( current_item, None )  #Affiche les attributs pour impélmenter le dicForQuerieForAddCategorie
        self.takeTopLevelItem(self.indexOfTopLevelItem(current_item))
        #
        dicForQuerieForAddCategorie = returnListObjKeyValue(self, self.groupBoxAttributsCategorie, self.mapping_categories, 'initialiseAttributsCategorie')
        with self._selfCreateTemplate.Dialog.safe_pg_connection("continue") :
           mKeySql = queries.query_delete_meta_categorie(dicForQuerieForAddCategorie)
           r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self._selfCreateTemplate.Dialog.mConnectEnCours, mKeySql, optionRetour = None)
           self._selfCreateTemplate.Dialog.mConnectEnCours.commit()
        #Efface les attributs
        afficheAttributs( self, self.groupBoxAttributsCategorie, self.mapping_categories, False ) 
        self._selfCreateTemplate.buttonAddCategorie.setVisible(False)
        self._selfCreateTemplate.flagNewCategorie = True
        self._selfCreateTemplate.groupBoxdisplayHelpFocusAttributsCategorie.setVisible(False)
        self._selfCreateTemplate.zoneDisplayHelpFocusAttributsCategorie.setText("")
        return

#========================================================     
#========================================================     
# Class pour le tree View Ressource ONGLET 
class TREEVIEWONGLET(QTreeWidget):
    customMimeType = "text/plain"

    #===============================              
    def __init__(self, *args):
        QTreeWidget.__init__(self, *args)
        self.setColumnCount(2)
        self.hideColumn (0)   # For hide ID
        self.setHeaderLabels(["Noms", "Libellés"])
        self.setSelectionMode(QAbstractItemView.SingleSelection	)  
        self.mnodeToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Right click to add / delete a model", None)         #Click droit pour supprimer un Modèle
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.menuContextuelPlumeONGLET) 
        return

    #===============================              
    def afficheONGLET(self, _selfCreateTemplate, listeOngletCol1, listeOngletCol2):
        self.groupBoxAttributsOnglet          = _selfCreateTemplate.groupBoxAttributsOnglet
        self.mapping_tabs                      = _selfCreateTemplate.mapping_tabs

        self.mListTabs                         = _selfCreateTemplate.mListTabs
        self._selfCreateTemplate               = _selfCreateTemplate
        self.groupBoxdisplayHelpFocusAttributsOnglet = _selfCreateTemplate.groupBoxdisplayHelpFocusAttributsOnglet
        self.zoneDisplayHelpFocusAttributsOnglet     = _selfCreateTemplate.zoneDisplayHelpFocusAttributsOnglet
        self.listLangList                            = _selfCreateTemplate.listLangList
        #---
        self.header().setStretchLastSection(False)
        self.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        i = 0
        while i in range(len(listeOngletCol1)) :
            nodeUrlUser = QTreeWidgetItem(None, [ str(listeOngletCol1[i]), str(listeOngletCol2[i]) ])
            self.insertTopLevelItems( 0, [ nodeUrlUser ] )
            nodeUrlUser.setToolTip(0, "{}".format(self.mnodeToolTip))
            nodeUrlUser.setToolTip(1, "{}".format(self.mnodeToolTip))
            i += 1
 
        self.itemClicked.connect( self.ihmsPlumeONGLET ) 
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect( self.menuContextuelPlumeONGLET)
        self.expandAll()
        return
        
    #===============================              
    def menuContextuelPlumeONGLET(self, point):
        index = self.indexAt(point)
        #-------
        with self._selfCreateTemplate.Dialog.safe_pg_connection("continue") :
           mKeySql = queries.query_read_meta_tab()
           r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self._selfCreateTemplate.Dialog.mConnectEnCours, mKeySql, optionRetour = "fetchall")
           self.mListTabs = [row[0] for row in r]
        
        if len(self.mListTabs) == 0 : 
           self.treeMenu = QMenu(self)
           menuIcon = returnIcon(os.path.dirname(__file__) + "\\icons\\buttons\\plus_button.svg")          
           treeAction_addTooltip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Add tab", None)  #Supprimer le modèle
           self.treeAction_add = QAction(QtGui.QIcon(menuIcon), treeAction_addTooltip, self.treeMenu)
           self.treeMenu.addAction(self.treeAction_add)
           self.treeAction_add.setToolTip(treeAction_addTooltip)
           self.treeAction_add.triggered.connect( self.ihmsPlumeAdd )
           #-------
           self.treeMenu.exec_(self.mapToGlobal(point))        
        else :   
           if index.data(0) != None : 
              self.treeMenu = QMenu(self)
              menuIcon = returnIcon(os.path.dirname(__file__) + "\\icons\\buttons\\plus_button.svg")          
              treeAction_addTooltip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Add tab", None)  #Supprimer le modèle
              self.treeAction_add = QAction(QtGui.QIcon(menuIcon), treeAction_addTooltip, self.treeMenu)
              self.treeMenu.addAction(self.treeAction_add)
              self.treeAction_add.setToolTip(treeAction_addTooltip)
              self.treeAction_add.triggered.connect( self.ihmsPlumeAdd )
              
              menuIcon = returnIcon(os.path.dirname(__file__) + "\\icons\\general\\delete.svg")          
              treeAction_delTooltip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Remove tab", None)  #Supprimer le modèle
              self.treeAction_del = QAction(QtGui.QIcon(menuIcon), treeAction_delTooltip, self.treeMenu)
              self.treeMenu.addAction(self.treeAction_del)
              self.treeAction_del.setToolTip(treeAction_delTooltip)
              self.treeAction_del.triggered.connect( self.ihmsPlumeDel )
              #-------
              self.treeMenu.exec_(self.mapToGlobal(point))        
        return
        
    #===============================              
    def ihmsPlumeONGLET(self, item, column): 
        mItemClicOnglet = item.data(0, QtCore.Qt.DisplayRole)
        self.ongletActif = mItemClicOnglet
        
        #=== Nécessaire pour récupérer les valeurs initiales et/ ou sauvegardées              
        with self._selfCreateTemplate.Dialog.safe_pg_connection("continue") :
           #------ DATA template 
           mKeySql = queries.query_read_meta_tab()
           r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self._selfCreateTemplate.Dialog.mConnectEnCours, mKeySql, optionRetour = "fetchall")
           self.mListTabs = [row[0] for row in r]
           listeOngletCol1, listeOngletCol2 = returnList_Id_Label( self.mListTabs )
           self.ongletActif = listeOngletCol1[0] #Pour la première initialisation
        #------
        self._selfCreateTemplate.buttonAddOnglet.setVisible(True)
        #Affiche les attributs
        afficheAttributs( self, self.groupBoxAttributsOnglet, self.mapping_tabs, True ) 
        self._selfCreateTemplate.buttonAddOnglet.setVisible(True)
        #Initialise les attributs avec valeurs
        returnDicValuePropriete, self._selfCreateTemplate.listeThesaurus = initialiseAttributsModelesCategoriesOnglets( self, mItemClicOnglet, self.groupBoxAttributsOnglet, self.mapping_tabs, self.mListTabs, True ) 
        self._selfCreateTemplate.dicValuePropriete['initialiseAttributsOnglet'] = returnDicValuePropriete 

        self._selfCreateTemplate.groupBoxdisplayHelpFocusAttributsOnglet.setVisible(False)
        self._selfCreateTemplate.zoneDisplayHelpFocusAttributsOnglet.setText("")
        return

    #===============================              
    def ihmsPlumeUpdateOnglet(self, mDialog, mId):
        #===============================              
        dicForQuerieForAddOnglet = returnListObjKeyValue(self._selfCreateTemplate, self.groupBoxAttributsOnglet, self.mapping_tabs, 'initialiseAttributsOnglet')

        with self._selfCreateTemplate.Dialog.safe_pg_connection("continue") :
           mKeySql = queries.query_insert_or_update_meta_tab(dicForQuerieForAddOnglet)
           r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self._selfCreateTemplate.Dialog.mConnectEnCours, mKeySql, optionRetour = "fetchone")
           self._selfCreateTemplate.Dialog.mConnectEnCours.commit()
        with self._selfCreateTemplate.Dialog.safe_pg_connection("continue") :
           #- Réinit
           mKeySql = queries.query_read_meta_tab()
           r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self._selfCreateTemplate.Dialog.mConnectEnCours, mKeySql, optionRetour = "fetchall")
           self.mListTabs = [row[0] for row in r]
           listeOngletCol1, listeOngletCol2 = returnList_Id_Label( self.mListTabs )
        self.clear()
        self.afficheONGLET(self._selfCreateTemplate, listeOngletCol1, listeOngletCol2)
        self._selfCreateTemplate.groupBoxdisplayHelpFocusAttributsOnglet.setVisible(False)
        self._selfCreateTemplate.zoneDisplayHelpFocusAttributsOnglet.setText("")
        return

    #===============================              
    def ihmsPlumeAdd(self):
        #===============================              
        afficheAttributs( self, self.groupBoxAttributsOnglet, self.mapping_tabs, True ) 
        self._selfCreateTemplate.buttonAddOnglet.setVisible(True)
        returnDicValuePropriete, self._selfCreateTemplate.listeThesaurus = initialiseAttributsModelesCategoriesOnglets( self, "", self.groupBoxAttributsOnglet, self.mapping_tabs, self.mListTabs, True, "Vierge" ) 
        self._selfCreateTemplate.dicValuePropriete['initialiseAttributsOnglet'] = returnDicValuePropriete 

        self._selfCreateTemplate.groupBoxdisplayHelpFocusAttributsOnglet.setVisible(False)
        self._selfCreateTemplate.zoneDisplayHelpFocusAttributsOnglet.setText("")
        return
                
    #===============================              
    def ihmsPlumeDel(self): 
        current_item = self.currentItem()           #itemCourant
        self.ihmsPlumeONGLET( current_item, None )  #Affiche les attributs pour impélmenter le dicForQuerieForAddOnglet
        self.takeTopLevelItem(self.indexOfTopLevelItem(current_item))
        #
        dicForQuerieForAddOnglet = returnListObjKeyValue(self, self.groupBoxAttributsOnglet, self.mapping_tabs, 'initialiseAttributsOnglet')
        with self._selfCreateTemplate.Dialog.safe_pg_connection("continue") :
           mKeySql = queries.query_delete_meta_tab(dicForQuerieForAddOnglet)
           r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self._selfCreateTemplate.Dialog.mConnectEnCours, mKeySql, optionRetour = None)
           self._selfCreateTemplate.Dialog.mConnectEnCours.commit()
        #Efface les attributs
        afficheAttributs( self, self.groupBoxAttributsOnglet, self.mapping_tabs, False ) 
        self._selfCreateTemplate.buttonAddOnglet.setVisible(False)
        self._selfCreateTemplate.flagNewOnglet = True
        self._selfCreateTemplate.groupBoxdisplayHelpFocusAttributsOnglet.setVisible(False)
        self._selfCreateTemplate.zoneDisplayHelpFocusAttributsOnglet.setText("")
        return

