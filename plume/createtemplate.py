# (c) Didier  LECLERC 2020 CMSIG MTE-MCTRCT/SG/SNUM/UNI/DRC Site de Rouen
# créé 2022

from . import bibli_plume
from .bibli_plume import *
import os.path
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qt import *
from PyQt5.QtWidgets import (QTreeWidgetItemIterator)
#
from . import bibli_plume
from .bibli_plume import *
#
from plume.mapping_templates import load_mapping_read_meta_template_categories, load_mapping_read_meta_templates
#
import re
import json

class Ui_Dialog_CreateTemplate(object):
    def setupUiCreateTemplate(self, DialogCreateTemplate, Dialog):
        #-
        self.mDic_LH = bibli_plume.returnAndSaveDialogParam(self, "Load")
        self.editStyle        = self.mDic_LH["QEdit"]              #style saisie
        self.labelBackGround  = self.mDic_LH["QLabelBackGround"] #QLabel    
        self.epaiQGroupBox    = self.mDic_LH["QGroupBoxEpaisseur"] #épaisseur QGroupBox
        self.lineQGroupBox    = self.mDic_LH["QGroupBoxLine"]    #trait QGroupBox
        self.policeQGroupBox  = self.mDic_LH["QGroupBoxPolice"]  #Police QGroupBox
        self.policeQTabWidget = self.mDic_LH["QTabWidgetPolice"] #Police QTabWidget
        self.colorTemplateInVersOut  = self.mDic_LH["colorTemplateInVersOut"]  
        self.colorTemplateOutVersIn  = self.mDic_LH["colorTemplateOutVersIn"]     
        self.sepLeftTemplate  = self.mDic_LH["sepLeftTemplate"]
        self.sepRightTemplate = self.mDic_LH["sepRightTemplate"]
        #-
        #-
        #- Fichier de mapping table ihm
        self.mapping_template_categories = load_mapping_read_meta_template_categories
        self.mapping_templates           = load_mapping_read_meta_templates
        #-
        self.DialogCreateTemplate = DialogCreateTemplate
        self.Dialog               = Dialog               #Pour remonter les variables de la boite de dialogue
        
        self.zMessTitle    =  QtWidgets.QApplication.translate("CreateTemplate_ui", "model management", None)   #Gestion des modèles
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
        self.label_2.setAlignment(Qt.AlignLeft)        
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
        self.layout_tab_widget_Association.setContentsMargins(10, 10, 10, 10)
        self.layout_tab_widget_Association.setRowStretch(0, 4)
        self.layout_tab_widget_Association.setRowStretch(1, 4)
        self.layout_tab_widget_Association.setRowStretch(2, 4)
        self.layout_tab_widget_Association.setRowStretch(3, 1)
        self.layout_tab_widget_Association.setRowStretch(4, 1.5)
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
        self.groupBox_tab_widget_Ressource.setStyleSheet("QGroupBox { border: 0px solid green }")
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
        self.groupBoxListeModeleCategorie.setStyleSheet("QGroupBox { border: px solid grey }")
        titlegroupBoxListeModeleCategorie = QtWidgets.QApplication.translate("CreateTemplate_ui", "Existing models", None)      #{Modèles existants}
        #self.groupBoxListeModeleCategorie.setTitle(titlegroupBoxListeModeleCategorie)
        #-
        self.layoutListeModeleCategorie = QtWidgets.QGridLayout()
        self.groupBoxListeModeleCategorie.setLayout(self.layoutListeModeleCategorie)
        self.layout_tab_widget_Association.addWidget(self.groupBoxListeModeleCategorie, 0, 0, 1, 3)
        #-
        #------ TREEVIEW   
        self.mTreeListeModeleCategorie = TREEVIEWASSOCIATION()

        self.labelListeModeleCategorie = QtWidgets.QLabel()
        self.labelListeModeleCategorie.setText(titlegroupBoxListeModeleCategorie)
        self.layoutListeModeleCategorie.addWidget(self.labelListeModeleCategorie, 0 ,0, Qt.AlignTop)
        self.layoutListeModeleCategorie.addWidget(self.mTreeListeModeleCategorie, 1 , 0)

        #self.layoutListeModeleCategorie.addWidget(self.mTreeListeModeleCategorie)
        #-
        self.mTreeListeModeleCategorie.clear()

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
        
        #Declaration avant pour argument dans afficheASSOCIATION 
        self.groupBoxAttributsModeleCategorie = QtWidgets.QGroupBox()
        self.groupBoxAttributsModeleCategorie.setObjectName("groupBoxAttributsModeleCategorie")

        self.mTreeListeCategorieIn  = TREEVIEW_CAT_IN_OUT()
        self.mTreeListeCategorieOut = TREEVIEW_CAT_IN_OUT()

        #------ DATA 
        self.mTreeListeModeleCategorie.afficheASSOCIATION(self, listeAssociationCol1, listeAssociationCol2)
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
        self.layout_tab_widget_Association.addWidget(self.groupBoxListeCategorieOut, 1, 0, 2, 1)
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
        self.labelCategorieOut = QtWidgets.QLabel()
        self.labelCategorieOut.setText(QtWidgets.QApplication.translate("CreateTemplate_ui", "Categories not belonging", None))   #Catégories n'appartenant pas
        self.labelCategorieIn = QtWidgets.QLabel()
        self.labelCategorieIn.setText(QtWidgets.QApplication.translate("CreateTemplate_ui", "Categories belonging", None))   #Catégories appartenant
         
        #------ TREEVIEW CATEGORIES OUT
        self.layoutListeCategorieOut.addWidget(self.labelCategorieOut, 0 ,0, Qt.AlignTop)
        self.layoutListeCategorieOut.addWidget(self.mTreeListeCategorieOut, 1 , 0)
        #-
        self.mTreeListeCategorieOut.clear()
        
        #------ TREEVIEW CATEGORIES IN 
        self.layoutListeCategorieIn.addWidget(self.labelCategorieIn, 0 ,2, Qt.AlignTop)
        self.layoutListeCategorieIn.addWidget(self.mTreeListeCategorieIn, 1 ,2)
        #-
        self.mTreeListeCategorieIn.clear()

        #Liste ATTRIBUTS modeles / catégories
        self.groupBoxAttributsModeleCategorie.setStyleSheet("QGroupBox { border: 0px solid grey;}")
        #-
        self.layoutAttributsModeleCategorie = QtWidgets.QGridLayout()
        self.layoutAttributsModeleCategorie.setObjectName("layoutAttributsModeleCategorie")
        self.groupBoxAttributsModeleCategorie.setLayout(self.layoutAttributsModeleCategorie)
        self.layout_tab_widget_Association.addWidget(self.groupBoxAttributsModeleCategorie, 2, 1)

        #=====================================
        # [ == scrolling == ]
        self.scroll_bar_AttributsModeleCategorie = QtWidgets.QScrollArea(self.tab_widget_Association) 
        self.scroll_bar_AttributsModeleCategorie.setStyleSheet("QScrollArea { border: 0px solid red;}")
        self.scroll_bar_AttributsModeleCategorie.setWidgetResizable(True)
        self.scroll_bar_AttributsModeleCategorie.setWidget(self.groupBoxAttributsModeleCategorie)
        self.layout_tab_widget_Association.addWidget(self.scroll_bar_AttributsModeleCategorie, 2, 1)
        #=====================================

        #=====================================
        
        # [ == création des attributs == ]
        genereAttributs( self, self.mapping_template_categories, self.layoutAttributsModeleCategorie )
        afficheAttributs( self, self.groupBoxAttributsModeleCategorie, self.mapping_template_categories, False ) 
        # [ == création des attributs == ]

        #Button Add
        #-
        self.groupBox_buttonAdd = QtWidgets.QGroupBox()
        self.groupBox_buttonAdd.setObjectName("groupBox_buttonAdd")
        self.groupBox_buttonAdd.setStyleSheet("QGroupBox { border: 0px solid green }")
        #-
        self.layout_groupBox_buttonAdd = QtWidgets.QGridLayout()
        self.layout_groupBox_buttonAdd.setContentsMargins(0, 0, 0, 0)
        self.groupBox_buttonAdd.setLayout(self.layout_groupBox_buttonAdd)
        self.layout_tab_widget_Association.addWidget(self.groupBox_buttonAdd, 3 ,0 , 1, 2)
        #-
        self.layout_groupBox_buttonAdd.setColumnStretch(0, 3)
        self.layout_groupBox_buttonAdd.setColumnStretch(1, 1)
        self.layout_groupBox_buttonAdd.setColumnStretch(2, 1)
        self.layout_groupBox_buttonAdd.setColumnStretch(3, 1)
        self.layout_groupBox_buttonAdd.setColumnStretch(4, 3)

        self.buttonAdd = QtWidgets.QToolButton()
        self.buttonAdd.setObjectName("buttonAdd")
        self.buttonAdd.setIcon(QIcon(os.path.dirname(__file__)+"\\icons\\general\\save.svg"))
        mbuttonAddToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Modify the attributes associated with the model, as well as the categories used or not used.", None)  
        self.buttonAdd.setToolTip(mbuttonAddToolTip)
        self.buttonAdd.clicked.connect(lambda : self.functionAddCmodele())
        self.layout_groupBox_buttonAdd.addWidget(self.buttonAdd, 1, 2)
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
        self.layout_groupBox_buttons.setColumnStretch(4, 3)
        #-
        #----------
        self.pushButtonAnnuler = QtWidgets.QPushButton()
        self.pushButtonAnnuler.setObjectName("pushButtonAnnuler")
        self.pushButtonAnnuler.clicked.connect(self.DialogCreateTemplate.reject)
        self.layout_groupBox_buttons.addWidget(self.pushButtonAnnuler, 1, 2, Qt.AlignTop)
        #--
        #----------
        self.DialogCreateTemplate.setWindowTitle(QtWidgets.QApplication.translate("plume_main", "PLUME (Metadata storage in PostGreSQL") + "  (" + str(bibli_plume.returnVersion()) + ")")
        self.label_2.setText(QtWidgets.QApplication.translate("CreateTemplate_ui", self.zMessTitle, None))
        self.pushButtonAnnuler.setText(QtWidgets.QApplication.translate("CreateTemplate_ui", "Cancel", None))
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
        self.zoneModele.setLayout(self.layoutZoneModele)
        #--
        #------ TREEVIEW   
        self.mTreeListeRessourceModele = TREEVIEWMODELE()
        self.layoutZoneModele.addWidget(self.mTreeListeRessourceModele)
        #-
        self.mTreeListeRessourceModele.clear()
        #------ TEMPORAIRE 
        #------
        #------ DATA template 
        mKeySql = queries.query_read_meta_template()
        r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self.Dialog.mConnectEnCours, mKeySql, optionRetour = "fetchall")
        self.mListTemplates = [row[0] for row in r]
        listeModeleCol1, listeModeleCol2 = returnList_Id_Label( self.mListTemplates )
        self.modeleActif = listeModeleCol1[0] #Pour la première initialisation

        self.voletsRessource.addItem(self.zoneModele, QtWidgets.QApplication.translate("CreateTemplate_ui", "List of models"))
        #====
        #=====================================
         #Liste ATTRIBUTS modeles
        self.groupBoxAttributsModele = QtWidgets.QGroupBox()
        self.groupBoxAttributsModele.setObjectName("groupBoxAttributsModele")
        self.groupBoxAttributsModele.setStyleSheet("QGroupBox { border: 0px solid blue;}")
        #-
        self.layoutAttributsModele = QtWidgets.QGridLayout()
        self.layoutAttributsModele.setObjectName("layoutAttributsModele")
        #-
        self.layoutAttributsModele.setColumnStretch(0, 3)
        self.layoutAttributsModele.setColumnStretch(1, 7)
        self.layoutAttributsModele.setColumnStretch(2, 1)
        self.groupBoxAttributsModele.setLayout(self.layoutAttributsModele)
        self.layoutZoneModele.addWidget(self.groupBoxAttributsModele)
        #------
        self.mTreeListeRessourceModele.afficheMODELE(self, listeModeleCol1, listeModeleCol2)

        #=====================================
        # [ == scrolling == ]
        self.scroll_bar_AttributsModele = QtWidgets.QScrollArea() 
        self.scroll_bar_AttributsModele.setStyleSheet("QScrollArea { border: 0px solid red;}")
        self.scroll_bar_AttributsModele.setWidgetResizable(True)
        self.scroll_bar_AttributsModele.setWidget(self.groupBoxAttributsModele)
        self.layoutZoneModele.addWidget(self.scroll_bar_AttributsModele, 1 , 0)
        #=====================================
        # [ == création des attributs == ]
        genereAttributs( self, self.mapping_templates, self.layoutAttributsModele )
        afficheAttributs( self, self.groupBoxAttributsModele, self.mapping_templates, False ) 
        # [ == création des attributs == ]

        #------
        #Button Add
        self.buttonAddModele = QtWidgets.QToolButton()
        self.buttonAddModele.setObjectName("buttonAddModele")
        self.buttonAddModele.setIcon(QIcon(os.path.dirname(__file__)+"\\icons\\general\\save.svg"))
        mbuttonAddToolTip = QtWidgets.QApplication.translate("ImportCSW_ui", "Modify a model as well as these attributes.", None)
        self.buttonAddModele.setToolTip(mbuttonAddToolTip)
        self.buttonAddModele.clicked.connect(lambda : self.functionUpdateModele())
        self.layoutAttributsModele.addWidget(self.buttonAddModele, 0, 2)
        self.buttonAddModele.setVisible(False)
        #Button Add
        #------

        #====
        #====
        # Zone CATEGORIES
        self.zoneCategorie       = QWidget()
        self.layoutZoneCategorie = QtWidgets.QGridLayout()
        self.zoneCategorie.setLayout(self.layoutZoneCategorie)
        #Liste Categories
        #------ Déclare TREEVIEW
        self.mTreeListeRessourceCategorie = TREEVIEW_CAT_IN_OUT()
        #-
        #------ TREEVIEW CATEGORIES
        self.layoutZoneCategorie.addWidget(self.mTreeListeRessourceCategorie)
        #-
        self.mTreeListeRessourceCategorie.clear()

        #------ TEMPORAIRE 
        listeCatCol1 = ["Cat1", "Cat3", "Cat4"]
        listeCatCol1 = list(reversed(listeCatCol1))
        listeCatCol2 = ["Catégories concernant ......", "Catégories concernant ......", "Catégories concernant ......"]
        listeCatCol2 = list(reversed(listeCatCol2))
        listeCatCol3 = ["click association", "click association", "click association"]
        listeCatCol3 = list(reversed(listeCatCol2))
        listeCatCol4 = [True, False, True]
        listeCatCol4 = list(reversed(listeCatCol2))
        #------ TEMPORAIRE 

        # A REPRENDRE self.mTreeListeRessourceCategorie.affiche_CAT_IN_OUT(self, "CAT_OUT", self.mTreeListeRessourceCategorie, self.mTreeListeRessourceCategorie, listeCatCol1, listeCatCol2, listeCatCol3, listeCatCol4)

        self.voletsRessource.addItem(self.zoneCategorie, QtWidgets.QApplication.translate("CreateTemplate_ui", "List of Categories"))
        #====

        #=====================================
         #Liste ATTRIBUTS catégories
        self.groupBoxAttributsCategories = QtWidgets.QGroupBox()
        self.groupBoxAttributsCategories.setObjectName("groupBoxAttributsCategories")
        self.groupBoxAttributsCategories.setStyleSheet("QGroupBox { border: 0px solid blue;}")
        #-
        self.layoutAttributsCategories = QtWidgets.QGridLayout()
        self.layoutAttributsCategories.setColumnStretch(0, 3)
        self.layoutAttributsCategories.setColumnStretch(1, 7)
        self.layoutAttributsCategories.setColumnStretch(2, 1)
        self.groupBoxAttributsCategories.setLayout(self.layoutAttributsCategories)
        self.layoutZoneCategorie.addWidget(self.groupBoxAttributsCategories)

        #=====================================
        # [ == scrolling == ]
        self.scroll_bar_AttributsCategorie = QtWidgets.QScrollArea() 
        self.scroll_bar_AttributsCategorie.setStyleSheet("QScrollArea { border: 0px solid red;}")
        self.scroll_bar_AttributsCategorie.setWidgetResizable(True)
        self.scroll_bar_AttributsCategorie.setWidget(self.groupBoxAttributsCategories)
        self.layoutZoneCategorie.addWidget(self.scroll_bar_AttributsCategorie, 1 , 0)
        #=====================================
        #=====================================
        # [ == attrib1 == ]
        mTextToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Attribut 1") 
        _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "toolTipWidget", "aligneWidget", "styleSheet", "wordWrap" ]
        _ListValues = [ QtWidgets.QLabel(), "Nom :", "cat_Lib_Attrib1", mTextToolTip, Qt.AlignRight, "QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}", True ]
        dicParamLabel = dict(zip(_Listkeys, _ListValues))
        self.cat_Lib_Attrib1 = genereLabelWithDict( dicParamLabel )
        #-
        mTextToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Attribut 1") 
        _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "toolTipWidget", "aligneWidget", "styleSheet" ]
        _ListValues = [ QtWidgets.QLineEdit(), "Cat1", "cat_Attrib1", mTextToolTip, Qt.AlignRight, "QLineEdit {  font-family:" + self.policeQGroupBox  +";}" ]
        dicParamButton = dict(zip(_Listkeys, _ListValues))
        self.cat_Attrib1 = genereButtonsWithDict( dicParamButton )
        self.layoutAttributsCategories.addWidget(self.cat_Lib_Attrib1, 0, 0, Qt.AlignTop)
        self.layoutAttributsCategories.addWidget(self.cat_Attrib1    , 0, 1, Qt.AlignTop)
        # [ == attrib2 == ]
        mTextToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Attribut 2:") 
        _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "toolTipWidget", "aligneWidget", "styleSheet", "wordWrap" ]
        _ListValues = [ QtWidgets.QLabel(), "Description :", "cat_Lib_Attrib2", mTextToolTip, Qt.AlignRight, "QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}", True ]
        dicParamLabel = dict(zip(_Listkeys, _ListValues))
        self.cat_Lib_Attrib2 = genereLabelWithDict( dicParamLabel )
        #-
        mTextToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Attribut 2") 
        _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "toolTipWidget", "aligneWidget", "styleSheet" ]
        _ListValues = [ QtWidgets.QLineEdit(), "mlkmjkl mlkj m mlkj mlkjm mlk j", "cat_Attrib2", mTextToolTip, Qt.AlignRight, "QLineEdit {  font-family:" + self.policeQGroupBox  +";}" ]
        dicParamButton = dict(zip(_Listkeys, _ListValues))
        self.cat_Attrib2 = genereButtonsWithDict( dicParamButton )
        self.layoutAttributsCategories.addWidget(self.cat_Lib_Attrib2, 1, 0, Qt.AlignTop)
        self.layoutAttributsCategories.addWidget(self.cat_Attrib2    , 1, 1, Qt.AlignTop)
        # [ == attrib3 == ]
        mTextToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Attribut 3:") 
        _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "toolTipWidget", "aligneWidget", "styleSheet", "wordWrap" ]
        _ListValues = [ QtWidgets.QLabel(), "Spécial :", "cat_Lib_Attrib3", mTextToolTip, Qt.AlignRight, "QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}", True ]
        dicParamLabel = dict(zip(_Listkeys, _ListValues))
        self.cat_Lib_Attrib3 = genereLabelWithDict( dicParamLabel )
        #-
        mTextToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Attribut 3") 
        _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "toolTipWidget", "aligneWidget", "styleSheet" ]
        _ListValues = [ QtWidgets.QLineEdit(), "Null", "cat_Attrib3", mTextToolTip, Qt.AlignRight, "QLineEdit {  font-family:" + self.policeQGroupBox  +";}" ]
        dicParamButton = dict(zip(_Listkeys, _ListValues))
        self.cat_Attrib3 = genereButtonsWithDict( dicParamButton )
        self.layoutAttributsCategories.addWidget(self.cat_Lib_Attrib3, 2, 0, Qt.AlignTop)
        self.layoutAttributsCategories.addWidget(self.cat_Attrib3    , 2, 1, Qt.AlignTop)
        # [ == attrib4 == ]
        mTextToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Attribut 4:") 
        _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "toolTipWidget", "aligneWidget", "styleSheet", "wordWrap" ]
        _ListValues = [ QtWidgets.QLabel(), "Etc :", "cat_Lib_Attrib4", mTextToolTip, Qt.AlignRight, "QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}", True ]
        dicParamLabel = dict(zip(_Listkeys, _ListValues))
        self.cat_Lib_Attrib4 = genereLabelWithDict( dicParamLabel )
        #-
        mTextToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Attribut 4") 
        _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "toolTipWidget", "aligneWidget", "styleSheet" ]
        _ListValues = [ QtWidgets.QLineEdit(), "Etc .........", "cat_Attrib4", mTextToolTip, Qt.AlignRight, "QLineEdit {  font-family:" + self.policeQGroupBox  +";}" ]
        dicParamButton = dict(zip(_Listkeys, _ListValues))
        self.cat_Attrib4 = genereButtonsWithDict( dicParamButton )
        self.layoutAttributsCategories.addWidget(self.cat_Lib_Attrib4, 3, 0, Qt.AlignTop)
        self.layoutAttributsCategories.addWidget(self.cat_Attrib4    , 3, 1, Qt.AlignTop)

        #------
        #Button Add
        self.buttonAddCategorie = QtWidgets.QToolButton()
        self.buttonAddCategorie.setObjectName("buttonAddCategorie")
        self.buttonAddCategorie.setIcon(QIcon(os.path.dirname(__file__)+"\\icons\\general\\save.svg"))
        mbuttonAddToolTip = QtWidgets.QApplication.translate("ImportCSW_ui", "Add or modify a stored CSW. The URL and label will be saved in the “My CSW” section of the table above.", None)
        self.buttonAddCategorie.setToolTip(mbuttonAddToolTip)
        self.buttonAddCategorie.clicked.connect(lambda : self.functionAddCategorie())
        self.layoutAttributsCategories.addWidget(self.buttonAddCategorie, 0, 2)
        #Button Add
        #------

        #====
        #====
        # Zone ONGLETS
        self.zoneOnglet       = QWidget()
        self.layoutZoneOnglet = QtWidgets.QGridLayout()  
        self.zoneOnglet.setLayout(self.layoutZoneOnglet)
        #Liste Onglets
        #------ Déclare TREEVIEW
        self.mTreeListeRessourceOnglet = TREEVIEW_CAT_IN_OUT()
        #-
        #------ TREEVIEW ONGLETS
        self.layoutZoneOnglet.addWidget(self.mTreeListeRessourceOnglet)
        #-
        self.mTreeListeRessourceOnglet.clear()

        #------ TEMPORAIRE 
        listeCatCol1 = ["Généralités", "Géométries", "Autres"]
        listeCatCol1 = list(reversed(listeCatCol1))
        listeCatCol2 = ["1", "3", "2"]
        listeCatCol2 = list(reversed(listeCatCol2))
        listeCatCol3 = ["click association", "click association", "click association"]
        listeCatCol3 = list(reversed(listeCatCol2))
        listeCatCol4 = [True, False, True]
        listeCatCol4 = list(reversed(listeCatCol2))
        #------ TEMPORAIRE 

        # A REPRENDRE self.mTreeListeRessourceOnglet.affiche_CAT_IN_OUT(self, "CAT_OUT", self.mTreeListeRessourceOnglet, self.mTreeListeRessourceOnglet, listeCatCol1, listeCatCol2, listeCatCol3, listeCatCol4)

        self.voletsRessource.addItem(self.zoneOnglet, QtWidgets.QApplication.translate("CreateTemplate_ui", "List of Onglets"))

        #=====================================
         #Liste ATTRIBUTS Onglets
        self.groupBoxAttributsOnglets = QtWidgets.QGroupBox()
        self.groupBoxAttributsOnglets.setObjectName("groupBoxAttributsOnglets")
        self.groupBoxAttributsOnglets.setStyleSheet("QGroupBox { border: 0px solid blue;}")
        #-
        self.layoutAttributsOnglets = QtWidgets.QGridLayout()
        self.layoutAttributsOnglets.setColumnStretch(0, 3)
        self.layoutAttributsOnglets.setColumnStretch(1, 7)
        self.layoutAttributsOnglets.setColumnStretch(2, 1)
        self.groupBoxAttributsOnglets.setLayout(self.layoutAttributsOnglets)
        self.layoutZoneOnglet.addWidget(self.groupBoxAttributsOnglets)

        #=====================================
        # [ == scrolling == ]
        self.scroll_bar_AttributsOnglet = QtWidgets.QScrollArea() 
        self.scroll_bar_AttributsOnglet.setStyleSheet("QScrollArea { border: 0px solid red;}")
        self.scroll_bar_AttributsOnglet.setWidgetResizable(True)
        self.scroll_bar_AttributsOnglet.setWidget(self.groupBoxAttributsOnglets)
        self.layoutZoneOnglet.addWidget(self.scroll_bar_AttributsOnglet, 1 , 0)
        #=====================================
        #=====================================
        # [ == attrib1 == ]
        mTextToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Attribut 1") 
        _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "toolTipWidget", "aligneWidget", "styleSheet", "wordWrap" ]
        _ListValues = [ QtWidgets.QLabel(), "Nom :", "ong_Lib_Attrib1", mTextToolTip, Qt.AlignRight, "QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}", True ]
        dicParamLabel = dict(zip(_Listkeys, _ListValues))
        self.ong_Lib_Attrib1 = genereLabelWithDict( dicParamLabel )
        #-
        mTextToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Attribut 1") 
        _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "toolTipWidget", "aligneWidget", "styleSheet" ]
        _ListValues = [ QtWidgets.QLineEdit(), "Généralités", "ong_Attrib1", mTextToolTip, Qt.AlignRight, "QLineEdit {  font-family:" + self.policeQGroupBox  +";}" ]
        dicParamButton = dict(zip(_Listkeys, _ListValues))
        self.ong_Attrib1 = genereButtonsWithDict( dicParamButton )
        self.layoutAttributsOnglets.addWidget(self.ong_Lib_Attrib1, 0, 0, Qt.AlignTop)
        self.layoutAttributsOnglets.addWidget(self.ong_Attrib1    , 0, 1, Qt.AlignTop)
        # [ == attrib2 == ]
        mTextToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Attribut 2:") 
        _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "toolTipWidget", "aligneWidget", "styleSheet", "wordWrap" ]
        _ListValues = [ QtWidgets.QLabel(), "Ordre :", "ong_Lib_Attrib2", mTextToolTip, Qt.AlignRight, "QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}", True ]
        dicParamLabel = dict(zip(_Listkeys, _ListValues))
        self.ong_Lib_Attrib2 = genereLabelWithDict( dicParamLabel )
        #-
        mTextToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Attribut 2") 
        _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "toolTipWidget", "aligneWidget", "styleSheet" ]
        _ListValues = [ QtWidgets.QLineEdit(), "1", "ong_Attrib2", mTextToolTip, Qt.AlignRight, "QLineEdit {  font-family:" + self.policeQGroupBox  +";}" ]
        dicParamButton = dict(zip(_Listkeys, _ListValues))
        self.ong_Attrib2 = genereButtonsWithDict( dicParamButton )
        self.layoutAttributsOnglets.addWidget(self.ong_Lib_Attrib2, 1, 0, Qt.AlignTop)
        self.layoutAttributsOnglets.addWidget(self.ong_Attrib2    , 1, 1, Qt.AlignTop)

        #------
        #Button Add
        self.buttonAddOnglet = QtWidgets.QToolButton()
        self.buttonAddOnglet.setObjectName("buttonAddOnglet")
        self.buttonAddOnglet.setIcon(QIcon(os.path.dirname(__file__)+"\\icons\\general\\save.svg"))
        mbuttonAddToolTip = QtWidgets.QApplication.translate("ImportCSW_ui", "Add or modify a stored CSW. The URL and label will be saved in the “My CSW” section of the table above.", None)
        self.buttonAddOnglet.setToolTip(mbuttonAddToolTip)
        self.buttonAddOnglet.clicked.connect(lambda : self.functionAddOnglet())
        self.layoutAttributsOnglets.addWidget(self.buttonAddOnglet, 0, 2)
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
    def functionChangeTab(self, mIndex):
       if mIndex != -1 :
          if mIndex == 0 :
             mSaveItemCurrent = None
             if self.mTreeListeModeleCategorie.currentItem() != None :
                mSaveItemCurrent = self.mTreeListeModeleCategorie.currentItem().data(0, Qt.DisplayRole)     #item Libelle Courant

             self.mTreeListeModeleCategorie.clear()
             mKeySql = queries.query_read_meta_template()
             r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self.Dialog.mConnectEnCours, mKeySql, optionRetour = "fetchall")
             self.mListTemplates = [row[0] for row in r]
      
             listeAssociationCol1, listeAssociationCol2 = returnList_Id_Label( self.mListTemplates )
             self.modeleAssociationActif = listeAssociationCol1[0] #Pour la première initialisation 
             #------ DATA 
             self.mTreeListeModeleCategorie.afficheASSOCIATION(self, listeAssociationCol1, listeAssociationCol2)
                
             if mSaveItemCurrent != None :
                iterator = QTreeWidgetItemIterator(self.mTreeListeModeleCategorie)
                while iterator.value() :
                   if iterator.value().text(0) == mSaveItemCurrent : 
                      self.mTreeListeModeleCategorie.setCurrentItem(iterator.value())           #itemCourant
                      break
                   iterator += 1
                #------ DATA 
       return

    #===============================              
    def functionUpdateModele(self):
       zTitre = QtWidgets.QApplication.translate("CreateTemplate_ui", "PLUME : Warning", None)
       zMess  = QtWidgets.QApplication.translate("CreateTemplate_ui", "You must enter a label.", None)
       
       mTestExisteModele = returnListObjAttributsId(self, self.groupBoxAttributsModele, self.mapping_templates)[0]
       if mTestExisteModele.text() == "" :
          bibli_plume.displayMess(self, (2 if self.Dialog.displayMessage else 1), zTitre, zMess, Qgis.Warning, self.Dialog.durationBarInfo)
       else :   
          self.mTreeListeRessourceModele.ihmsPlumeUpdateModele(self.Dialog, mTestExisteModele.text())
       return

    #===============================              
    def functionAddCategorie(self):
       zTitre = QtWidgets.QApplication.translate("CreateTemplate_ui", "PLUME : Warning", None)
       zMess  = QtWidgets.QApplication.translate("CreateTemplate_ui", "You must enter a URL of a CSW service.", None)
       if self.mZoneUrl.text() == "" or self.mZoneLibUrl.text() == "":
          bibli_plume.displayMess(self, (2 if self.Dialog.displayMessage else 1), zTitre, zMess, Qgis.Warning, self.Dialog.durationBarInfo)
       else :   
          self.mTreeCSW.ihmsPlumeAddCSW(self.Dialog , self.mZoneUrl.text(), self.mZoneLibUrl.text())
       return

    #===============================              
    def functionAddOnglet(self):
       zTitre = QtWidgets.QApplication.translate("CreateTemplate_ui", "PLUME : Warning", None)
       zMess  = QtWidgets.QApplication.translate("CreateTemplate_ui", "You must enter a URL of a CSW service.", None)
       if self.mZoneUrl.text() == "" or self.mZoneLibUrl.text() == "":
          bibli_plume.displayMess(self, (2 if self.Dialog.displayMessage else 1), zTitre, zMess, Qgis.Warning, self.Dialog.durationBarInfo)
       else :   
          self.mTreeCSW.ihmsPlumeAddCSW(self.Dialog , self.mZoneUrl.text(), self.mZoneLibUrl.text())
       return

    #===============================              
    def functionAddCsw(self):
       zTitre = QtWidgets.QApplication.translate("CreateTemplate_ui", "PLUME : Warning", None)
       zMess  = QtWidgets.QApplication.translate("CreateTemplate_ui", "You must enter a URL of a CSW service.", None)
       if self.mZoneUrl.text() == "" or self.mZoneLibUrl.text() == "":
          bibli_plume.displayMess(self, (2 if self.Dialog.displayMessage else 1), zTitre, zMess, Qgis.Warning, self.Dialog.durationBarInfo)
       else :   
          self.mTreeCSW.ihmsPlumeAddCSW(self.Dialog , self.mZoneUrl.text(), self.mZoneLibUrl.text())
       return

    #==========================
    def resizeEvent(self, event):
        self.tabWidget.setGeometry(QtCore.QRect(10,100,self.width() - 20, self.height() - self.deltaHauteurTabWidget))
        self.groupBox_tab_widget_Association.setGeometry(QtCore.QRect(10,10,self.tabWidget.width() - 20, self.tabWidget.height() - 40))
        self.groupBox_tab_widget_Ressource.setGeometry(QtCore.QRect(10,10,self.tabWidget.width() - 20, self.tabWidget.height() - 40))
        return

#==========================         
#==========================         
def update(self, name_list, new_name) :
    if not new_name :
        return None
    index_from_name = name_list.index(new_name) if new_name and new_name in name_list else None
    if index_from_name is not None :
        # le name est déjà répertorié, :
        if csw_index_from_name != csw_index_from_label:
            del name_list[csw_index_from_label]
            del label_list[csw_index_from_label]
            csw_index_from_name = name_list.index(new_name)
            label_list[csw_index_from_name] = new_label
    elif csw_index_from_name is not None:
        # le name est déjà répertorié, on met à jour le libellé
        label_list[csw_index_from_name] = new_label
    else:
        # name non répertorié = nouveau name
        name_list.append(new_name)
    return name_list
       
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
#==========================         
def returnListObjKeyValue(self,  _groupBoxAttributs, mapping ) :
  _group = _groupBoxAttributs.children() 
  _returnListObjKeyValue = {}
  for mObj in _group :
      _zone = mObj.objectName()[5:]
      _value = ""

      if (_zone in mapping) :
         _type   = mapping[_zone]["type"]
         _format = mapping[_zone]["format"]
         __Val   = _zone
   
         if _type in ("QLineEdit",) :
           __Val = mObj.text() if mObj.text() != "" else None 
           if _format in ("jsonb",) : __Val = json.dumps(__Val, ensure_ascii=False, indent=4)
         elif _type in ("QTextEdit",) :
               __Val = mObj.toPlainText() if mObj.toPlainText() != "" else None 
         elif _type in ("QComboBox",) :
               __Val = mObj.currentText() if mObj.currentText() != "" else None 
         elif _type in ("QDateEdit",) :
               __Val = mObj.date().toString("dd/MM/yyyy") if mObj.date().toString("dd/MM/yyyy") != "" else None 
         elif _type in ("QDateTimeEdit",) :
               __Val = mObj.dateTime().toString("dd/MM/yyyy hh:mm:ss") if mObj.dateTime().toString("dd/MM/yyyy hh:mm:ss") != "" else None 
         elif _type in ("QTimeEdit",) :
               __Val = mObj.time().toString("hh:mm:ss") if mObj.time().toString("hh:mm:ss") != "" else None 
         elif _type in ("QCheckBox",) :
               __Val = ("true" if mObj.checkState() == Qt.Checked else "false") if  mObj.checkState() != Qt.PartiallyChecked else None 

         _returnListObjKeyValue[_zone] = __Val

  return _returnListObjKeyValue
    
#==========================         
#==========================         
def genereAttributs(self,  mapping, zoneLayout ) :
  # [ == création des attibuts == ]
  _row, _col = 0, 0
  for keyNameAttrib, dicLabelTooltip in mapping.items() :
      okCreateZone = False
      mattrib = keyNameAttrib
      # Libellé            "loccat_path"    : {"label" : "libelle loccat_path",     "tooltip" : "tooltip loccat_path",    "type" : "QLineEdit"},         
      mTextToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", mapping[mattrib]["tooltip"])
      _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "toolTipWidget", "aligneWidget", "styleSheet", "wordWrap" ]
      _ListValues = [ QtWidgets.QLabel(), mapping[mattrib]["label"], "label_" + mattrib , mTextToolTip, Qt.AlignRight, "QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}", True ]
      dicParamLabel = dict(zip(_Listkeys, _ListValues))
      _modCat_Lib_Attrib = genereLabelWithDict( dicParamLabel )
       
      # widget
      if dicLabelTooltip["type"]   == "QLineEdit" :
         okCreateZone = True
         _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "toolTipWidget", "aligneWidget", "styleSheet" ]
         _ListValues = [ QtWidgets.QLineEdit(), "", "zone_" + mattrib, mTextToolTip, Qt.AlignRight, "QLineEdit {  font-family:" + self.policeQGroupBox  +";}" ]
      elif dicLabelTooltip["type"] == "QCheckBox" :
         okCreateZone = True           
         _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "toolTipWidget", "aligneWidget", "styleSheet", "checked" ]
         _ListValues = [ QtWidgets.QCheckBox(), "", "zone_" + mattrib, mTextToolTip, Qt.AlignRight, "QCheckBox {  font-family:" + self.policeQGroupBox  +";}", False ]
      elif dicLabelTooltip["type"] == "QComboBox" :
         okCreateZone = True
         mDicQcomboBox = ["Généralités", "Géométries", "Autres"]
         _Listkeys   = [ "typeWidget", "listItems", "currentText", "nameWidget", "toolTipWidget", "aligneWidget", "styleSheet" ]
         _ListValues = [ QtWidgets.QComboBox(), mDicQcomboBox, mDicQcomboBox[1], "zone_" + mattrib, mTextToolTip, Qt.AlignRight, "QComboBox {  font-family:" + self.policeQGroupBox  +";}" ]

      if okCreateZone :
         dicParamButton = dict(zip(_Listkeys, _ListValues))
         _modCat_Attrib = genereButtonsWithDict( dicParamButton )
         
         if dicLabelTooltip["format"]   == "integer" :
            _modCat_Attrib.setValidator(QIntValidator(_modCat_Attrib))

         if zoneLayout.objectName() == "layoutAttributsModeleCategorie" : 
            colonneLib, colonneAttrib = _col + 2, _col + 3        
         elif zoneLayout.objectName() == "layoutAttributsModele" : 
            colonneLib, colonneAttrib = _col + 0, _col + 1
                    
         zoneLayout.addWidget(_modCat_Lib_Attrib, _row, colonneLib,    Qt.AlignTop)
         zoneLayout.addWidget(_modCat_Attrib    , _row, colonneAttrib, Qt.AlignTop)
         
      _row += 1
  return 

#==========================         
#==========================         
def afficheAttributs(self,  _groupBoxAttributs, _mapping, display ) :
  _group = _groupBoxAttributs.children() 
  for mObj in _group :
      if (mObj.objectName()[5:] in _mapping) or (mObj.objectName()[6:] in _mapping) :
         mObj.setVisible(display)
  return

#==========================         
#==========================         
def initialiseAttributsModeleCategorie(self,  _mItemClic_CAT_IN_OUT, _mItemClicAssociation, _groupBoxAttributsModeleCategorie, _mapping_template_categories, _mListTemplateCategories, display ) :
    _group = _groupBoxAttributsModeleCategorie.children() 

    # Select for association et catégorie
    _mapping_template_categories_id_association_id_categorie = []
    i = 0
    while i < len(_mListTemplateCategories) :
       #$if _mItemClicAssociation == _mListTemplateCategories[i]["tpl_label"] :
       if _mItemClicAssociation == str(_mListTemplateCategories[i]["tpl_id"]) :
           if _mItemClic_CAT_IN_OUT == (_mListTemplateCategories[i]["shrcat_path"] if _mListTemplateCategories[i]["shrcat_path"] != None else _mListTemplateCategories[i]["loccat_path"]) : 
              _mapping_template_categories_id_association_id_categorie = _mListTemplateCategories[i]
              break  
       i += 1
    # Si _mapping_template_categories_id_association_id_categorie alors catégorie déplacé provenant de Out vers In
    initialiseValueOrBlank =  len(_mapping_template_categories_id_association_id_categorie)

    # Initialisation
    for mObj in _group :
        if (mObj.objectName()[5:] in _mapping_template_categories) :
           # widget
           _type  = _mapping_template_categories[ mObj.objectName()[5:] ]["type" ]
           if initialiseValueOrBlank == 0 :
              __Val = ""
           else :    
              __Val = str(_mapping_template_categories_id_association_id_categorie[ mObj.objectName()[5:] ]) if _mapping_template_categories_id_association_id_categorie[ mObj.objectName()[5:] ] != None else "" 

           if _type in ("QLineEdit",) :
              mObj.setText(__Val if __Val != None else "")  
           elif _type in ("QTextEdit",) :
              mObj.setPlainText(__Val if __Val != None else "")  
           elif _type in ("QComboBox",) :
              mObj.setCurrentText(__Val if __Val != None else "")  
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
              mObj.setCheckState((Qt.Checked if str(__Val).lower() == 'true' else Qt.Unchecked) if __Val != None else Qt.PartiallyChecked)

           mObj.setVisible(display)
    return

#==========================         
#==========================    
def initialiseAttributsModeles(self, _mItemClicModele, _groupBoxAttributsModele, _mapping_template, _mListTemplates, display, _blank = None ) :
    _group = _groupBoxAttributsModele.children() 
    # Select for association et catégorie
    _mapping_template_id_template = []
    i = 0
    while i < len(_mListTemplates) :
       #if _mItemClicModele == _mListTemplates[i]["tpl_label"] :
       if _mItemClicModele == str(_mListTemplates[i]["tpl_id"]) :
          _mapping_template_id_template = _mListTemplates[i]
          break  
       i += 1
       
    # Si _mapping_template_categories_id_association_id_categorie alors catégorie déplacé provenant de Out vers In
    # if Vierge
    initialiseValueOrBlank =  len(_mapping_template_id_template) if _blank == None else 0

    # Initialisation
    for mObj in _group :
        if (mObj.objectName()[5:] in _mapping_template) :
           # widget
           _type  = _mapping_template[ mObj.objectName()[5:] ]["type" ]
           if initialiseValueOrBlank == 0 :
              __Val = ""
           else :    
              if _blank == None :
                 __Val = str(_mapping_template_id_template[ mObj.objectName()[5:] ]) if _mapping_template_id_template[ mObj.objectName()[5:] ] != None else ""
              else :     
                 # if Vierge
                 __Val = ""

           if _type in ("QLineEdit",) :
              mObj.setText(__Val if __Val != None else "")  
           elif _type in ("QTextEdit",) :
              mObj.setPlainText(__Val if __Val != None else "")  
           elif _type in ("QComboBox",) :
              mObj.setCurrentText(__Val if __Val != None else "")  
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
              mObj.setCheckState((Qt.Checked if str(__Val).lower() == 'true' else Qt.Unchecked) if __Val != None else Qt.PartiallyChecked)

           mObj.setVisible(display)
    return

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
           #if _mapping_template_categories[i]["tpl_label"] not in dictAssociationCol1EtCol2 :
           if _mapping_template_categories[i]["tpl_id"] not in dictAssociationCol1EtCol2 :
              dictAssociationCol1EtCol2[str(_mapping_template_categories[i]["tpl_id"])] = ( _mapping_template_categories[i]["tpl_id"], str(_mapping_template_categories[i]["tpl_label"]) )
       i += 1
    listeAssociationCol1 = [ k    for k, v in dictAssociationCol1EtCol2.items() ]
    listeAssociationCol2 = [ v[1] for k, v in dictAssociationCol1EtCol2.items() ]
    listeAssociationCol1 = list(reversed(listeAssociationCol1))
    listeAssociationCol2 = list(reversed(listeAssociationCol2))
    return listeAssociationCol1, listeAssociationCol2
  
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
# Class pour le tree View Association 
class TREEVIEWASSOCIATION(QTreeWidget):
    customMimeType = "text/plain"

    #===============================              
    def __init__(self, *args):
        QTreeWidget.__init__(self, *args)
        self.setColumnCount(2)
        #self.hideColumn (0)   # For hide ID
        self.setHeaderLabels(["Id", "Noms"])
        self.setSelectionMode(QAbstractItemView.SingleSelection	)  
        self.mnodeToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Right click to delete a Model / Categories association", None)         #Click droit pour supprimer une association Modèle / Catégories

        #- Fichier de mapping table ihm
        self.mapping_template_categories = load_mapping_read_meta_template_categories
        return
               
    #===============================              
    def afficheASSOCIATION(self, _selfCreateTemplate, listeAssociationCol1, listeAssociationCol2):
        self.groupBoxAttributsModeleCategorie = _selfCreateTemplate.groupBoxAttributsModeleCategorie
        self.mListTemplates                   = _selfCreateTemplate.mListTemplates
        self.mListTemplateCategories          = _selfCreateTemplate.mListTemplateCategories
        self.mListCategories                  = _selfCreateTemplate.mListCategories    
        self.mTreeListeCategorieOut           = _selfCreateTemplate.mTreeListeCategorieOut
        self.mTreeListeCategorieIn            = _selfCreateTemplate.mTreeListeCategorieIn
        self._selfCreateTemplate              = _selfCreateTemplate
        self.colorTemplateInVersOut           = _selfCreateTemplate.colorTemplateInVersOut
        self.colorTemplateOutVersIn           = _selfCreateTemplate.colorTemplateOutVersIn
        self.sepLeftTemplate                  = _selfCreateTemplate.sepLeftTemplate
        self.sepRightTemplate                 = _selfCreateTemplate.sepRightTemplate
        #---
        self.header().setStretchLastSection(False)
        self.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        i = 0
        while i in range(len(listeAssociationCol1)) :
            nodeUrlUser = QTreeWidgetItem(None, [ listeAssociationCol1[i], str(listeAssociationCol2[i]) ])
            self.insertTopLevelItems( 0, [ nodeUrlUser ] )
            nodeUrlUser.setToolTip(0, "{}".format(self.mnodeToolTip))
            nodeUrlUser.setToolTip(1, "{}".format(self.mnodeToolTip))
            i += 1
 
        self.itemClicked.connect( self.ihmsPlumeASSOCIATION ) 
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect( self.menuContextuelPlumeASSOCIATION)
        self.expandAll()
        return

    #===============================              
    def menuContextuelPlumeASSOCIATION(self, point):
        index = self.indexAt(point)
        if not index.isValid():
           return
        #-------
        if index.data(0) != None : 
           self.treeMenu = QMenu(self)
           menuIcon = returnIcon(os.path.dirname(__file__) + "\\icons\\general\\delete.svg")          
           treeAction_delTooltip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Remove model / category association", None)  #Supprimer l'association modèle / Catégorie
           self.treeAction_del = QAction(QIcon(menuIcon), treeAction_delTooltip, self.treeMenu)
           self.treeMenu.addAction(self.treeAction_del)
           self.treeAction_del.setToolTip(treeAction_delTooltip)
           self.treeAction_del.triggered.connect( self.ihmsPlumeDel )
           #-------
           self.treeMenu.exec_(self.mapToGlobal(point))
        return
        
    #===============================              
    def ihmsPlumeASSOCIATION(self, item, column): 
        mItemClicAssociation        = item.data(0, Qt.DisplayRole)
        mItemClicLibelleAssociation = item.data(1, Qt.DisplayRole)
        self.modeleAssociationActif = mItemClicAssociation
        
        #=== Nécessaire pour récupérer les valeurs initiales et/ ou sauvegardées == Cat Utilisées et Non Utilisées==              
        #------ DATA template_categories 
        mKeySql = queries.query_read_meta_template_categories()
        r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self._selfCreateTemplate.Dialog.mConnectEnCours, mKeySql, optionRetour = "fetchall")
        self.mListTemplateCategories = [row[0] for row in r]
        self.dicInVersOutDesign = {} # Pour la gestion des double clic et la regénération des données en entrée de l'algo
        self.dicOutVersInDesign = {} # Pour la gestion des double clic et la regénération des données en entrée de l'algo
        #=== Nécessaire pour récupérer les valeurs initiales et/ ou sauvegardées
            
        self.mTreeListeCategorieIn.clear()
        self.mTreeListeCategorieOut.clear()
        self.mTreeListeCategorieIn.affiche_CAT_IN_OUT(self,  mItemClicAssociation, self.mTreeListeCategorieIn, self.mTreeListeCategorieOut, action = True)
        self.mTreeListeCategorieOut.affiche_CAT_IN_OUT(self, mItemClicAssociation, self.mTreeListeCategorieIn, self.mTreeListeCategorieOut)
        #Efface les attributs
        afficheAttributs( self, self.groupBoxAttributsModeleCategorie, self.mapping_template_categories, False ) 
        return

    #===============================              
    def ihmsPlumeDel(self): 
        current_item = self.currentItem()   #itemCourant
        self.takeTopLevelItem(self.indexOfTopLevelItem(current_item))
        return

#========================================================     
#========================================================     
# Class pour le tree View Catégories IN and OUT 
class TREEVIEW_CAT_IN_OUT(QTreeWidget):
    customMimeType = "text/plain"

    #===============================              
    def __init__(self, *args):
        QTreeWidget.__init__(self, *args)
        self.setColumnCount(5)
        self.setHeaderLabels(["Identifiant et chemin"])  
        self.setSelectionMode(QAbstractItemView.SingleSelection	)  
        self.mnodeToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Right click to delete a Model / Categories association", None)         #Click droit pour supprimer une association Modèle / Catégories

        self.itemDoubleClicked.connect(self.moveDoubleClicked)

        #- Fichier de mapping table ihm
        self.mapping_template_categories = load_mapping_read_meta_template_categories
        return

    #===============================              
    def returnLibelleCategorie(self, _mItemClicAssociation, _mListTemplateCategories) :
        # Recherche pour mettre le libelle de la table des catégories et pas celui de la table des modèleCatégories
        findLibCat = _mapping_template_categories[i]["shrcat_path"] if _mapping_template_categories[i]["shrcat_path"] != None else _mapping_template_categories[i]["loccat_path"]
        j = 0
        _label = ""
        while j < len(_mListCategories) :
           if findLibCat == _mListCategories[j]["path"]  :
              _label = _mListCategories[j]["label"]
              _node  = _mListCategories[j]["is_node"]
              break
           j += 1
        # Recherche pour mettre le libelle de la table des catégories et pas celui de la table des modèleCatégories
        return

    #===============================              
    def design_Items(self, _item, _mDicInVersOutDesign, _labelNewNoeud, _color) :
        if _mDicInVersOutDesign != None :
           if _labelNewNoeud in _mDicInVersOutDesign :  #Design color 
              _item.setBackground(0, _color)
        return

    #===============================              
    def affiche_CAT_IN_OUT(self, _selfCreateTemplate, _mItemClicAssociation, self_Cat_In, self_Cat_Out, mDicInVersOutDesign = None, mDicOutVersInDesign = None, action = False) :
        self._selfCreateTemplate              = _selfCreateTemplate  
        _pathIcons = os.path.dirname(__file__) + "/icons/logo"
        iconSource = returnIcon(_pathIcons + "/plume.svg")  
        self.groupBoxAttributsModeleCategorie = _selfCreateTemplate.groupBoxAttributsModeleCategorie
        self.mListTemplates                   = _selfCreateTemplate.mListTemplates
        self.mListTemplateCategories          = _selfCreateTemplate.mListTemplateCategories
        self.mListCategories                  = _selfCreateTemplate.mListCategories   
        self.modeleAssociationActif           = _selfCreateTemplate.modeleAssociationActif
        self.colorTemplateInVersOut           = _selfCreateTemplate.colorTemplateInVersOut
        self.colorTemplateOutVersIn           = _selfCreateTemplate.colorTemplateOutVersIn
        self.dicInVersOutDesign               = _selfCreateTemplate.dicInVersOutDesign # Pour la gestion des double clic et la regénération des données en antrée de l'algo
        self.dicOutVersInDesign               = _selfCreateTemplate.dicOutVersInDesign # Pour la gestion des double clic et la regénération des données en antrée de l'algo
        self.sepLeftTemplate                  = _selfCreateTemplate.sepLeftTemplate
        self.sepRightTemplate                 = _selfCreateTemplate.sepRightTemplate

        #---
        _color_Out_InVersOut = QBrush(QtGui.QColor(self.colorTemplateInVersOut))
        _color_In_OutVersIn  = QBrush(QtGui.QColor(self.colorTemplateOutVersIn))
        #---
        self.self_Cat_In  = _selfCreateTemplate.mTreeListeCategorieIn   #self_Cat_In                                                     
        self.self_Cat_Out = _selfCreateTemplate.mTreeListeCategorieOut  #self_Cat_Out 
        #---
        self.header().setStretchLastSection(True)
        self.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        #---
        self.self_Cat_Out.header().setStretchLastSection(True)
        self.self_Cat_Out.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        
        #Create Arbo
        dictNoeudsArboIn  , rowNodeIn  = {}, 0 
        dictNoeudsArboOut , rowNodeOut = {}, 0 

        if not action : return #Permet de ne pas repasser dans l'algo pour la création des QTreeWidgetItem
        
        i = 0
        while i < len(self.mListCategories) : 
           _lib_Categories     = self.mListCategories[i]["path"] 
           _libelle_Categories = self.mListCategories[i]["label"]    #deuxième colonne dans les treeview pour le In 
           _noeud              = "True" if self.mListCategories[i]["is_node"] else "False"  # si c'est un noeud pour être utilisé dans le double click, In vers Out 
           path_elements   = re.split(r'\s*[/]\s*', _lib_Categories) #pour découper le chemin, 
           paths           = [ ' / '.join(path_elements[:ii + 1] ) for ii in range(len(path_elements) - 1) ]  #Chemin des parents

           j = 0
           findInOut = False
           while j < len(self.mListTemplateCategories) : 
              _lib_Template_Categories = self.mListTemplateCategories[j]["shrcat_path"] if self.mListTemplateCategories[j]["shrcat_path"] != None else self.mListTemplateCategories[j]["loccat_path"]
              #-
              # Cat IN 
              #if _lib_Categories == _lib_Template_Categories and self.mListTemplateCategories[j]["tpl_label"] == _mItemClicAssociation :
              if _lib_Categories == _lib_Template_Categories and str(self.mListTemplateCategories[j]["tpl_id"]) == _mItemClicAssociation :
                 # _libelle (_label)  Nom du libellé de la catégorie + Nom de la catégorie (colonne 1 in QtreeWidget)
                 # _label      Nom de la catégorie                                         (colonne 2 in QtreeWidget)
                 # _libelle    Nom du libellé de la catégorie                              (colonne 3 in QtreeWidget) 
                 # _clickAsso  Nom du modèle cliqué
                 # mOrigine    Sens (In vers Out ou vice Versa
                 # mNoeud      Est-ce un Noeud
                 
                 _returnAttribCategorie = self.returnAttribCategoriesEnFonctionLibelleTemplateCategorie(_lib_Categories, self.mListCategories)[0]
                 _lib_Categories_in     = _returnAttribCategorie["path"]
                 _libelle_Categories_in = _returnAttribCategorie["label"]

                 if _returnAttribCategorie["origin"] == "local" :
                    _displayLibelle = str(_libelle_Categories_in) + self.sepLeftTemplate + str(path_elements[ -1 ]) + self.sepRightTemplate # For Affichage LIBELLE PLUS Dernier ELEMENT du chemin (paths)
                 else :
                    _displayLibelle = str(path_elements[ -1 ]) + self.sepLeftTemplate + str(_libelle_Categories_in) + self.sepRightTemplate # For Affichage LIBELLE PLUS Dernier ELEMENT du chemin (paths)

                 _displayLibelle, _label, _libelle, _clickAsso, mOrigine, mNoeud = _displayLibelle, _lib_Categories_in, _libelle_Categories_in, _mItemClicAssociation, 'CAT_IN', _noeud
                 nodeUser = QTreeWidgetItem(None, [ _displayLibelle, _label, _libelle, _clickAsso, mOrigine, mNoeud ])
                 self.design_Items(nodeUser, self.dicOutVersInDesign, _label, _color_In_OutVersIn) #For colorisation
                  # - Recherche dans le dictionnaire si existance de l'item en balayant les ancêtres (parents)
                 if len(paths) == 0 :
                    self.self_Cat_In.insertTopLevelItems( rowNodeIn, [ nodeUser ] )
                    dictNoeudsArboIn[_label]  = nodeUser
                    rowNodeIn += 1
                 else :
                    iElem = 0
                    while iElem < len(paths) : 
                       newNoeud = paths[iElem]
                       _returnAttribCategorie = self.returnAttribCategoriesEnFonctionLibelleTemplateCategorie(newNoeud, self.mListCategories)[0]
                       _lib_Categories_in     = _returnAttribCategorie["path"]
                       _libelle_Categories_in = _returnAttribCategorie["label"]

                       if _returnAttribCategorie["origin"] == "local" :
                          _displayLibelle = str(_libelle_Categories_in) + self.sepLeftTemplate + str(path_elements[ -1 ]) + self.sepRightTemplate # For Affichage LIBELLE PLUS Dernier ELEMENT du chemin (paths)
                       else :
                          _displayLibelle = str(path_elements[ -1 ]) + self.sepLeftTemplate + str(_libelle_Categories_in) + self.sepRightTemplate # For Affichage LIBELLE PLUS Dernier ELEMENT du chemin (paths)

                       _displayLibelleNewNoeud, _labelNewNoeud, _libelleNewNoeud, _clickAssoNewNoeud, mOrigineNewNoeud, _noeudNewNoeud = _displayLibelle, _lib_Categories_in, _libelle_Categories_in, _mItemClicAssociation, 'CAT_IN', _noeud 
                       nodeUserNewNoeud = QTreeWidgetItem(None, [ _displayLibelleNewNoeud, _labelNewNoeud, _libelleNewNoeud, _clickAssoNewNoeud, mOrigineNewNoeud, _noeudNewNoeud ])
                       self.design_Items(nodeUserNewNoeud, self.dicOutVersInDesign, _labelNewNoeud, _color_In_OutVersIn) #For colorisation

                       if newNoeud not in dictNoeudsArboIn : # Si l'ancêtre n'est pas dans le dictionnaire IN 

                          if len(paths) == 1 :
                             self.self_Cat_In.insertTopLevelItems( rowNodeIn, [ nodeUserNewNoeud ] )
                             rowNodeIn += 1
                          else :
                             dictNoeudsArboIn[ paths[iElem - 1] ].addChild( nodeUserNewNoeud )
                             dictNoeudsArboIn[ paths[iElem - 1] ].setIcon(0, iconSource)
                          dictNoeudsArboIn[ _labelNewNoeud ]  = nodeUserNewNoeud
                       iElem += 1

                    # Et enfin on ajoute ma catégorie   
                    dictNoeudsArboIn[_labelNewNoeud].addChild( nodeUser )
                    dictNoeudsArboIn[_labelNewNoeud].setIcon(0, iconSource)
                    dictNoeudsArboIn[_label]  = nodeUser

                 findInOut = True
                 break
              j += 1

           #-
           # Cat OUT 
           if not findInOut :
              _returnAttribCategorie = self.returnAttribCategoriesEnFonctionLibelleTemplateCategorie(_lib_Categories, self.mListCategories)[0]
              _lib_Categories_out     = _returnAttribCategorie["path"]
              _libelle_Categories_out = _returnAttribCategorie["label"]

              if _returnAttribCategorie["origin"] == "local" :
                 _Out_displayLibelle = str(_libelle_Categories_out) + self.sepLeftTemplate + str(path_elements[ -1 ]) + self.sepRightTemplate # For Affichage LIBELLE PLUS Dernier ELEMENT du chemin (paths)
              else :
                _Out_displayLibelle = str(path_elements[ -1 ]) + self.sepLeftTemplate + str(_libelle_Categories_out) + self.sepRightTemplate # For Affichage LIBELLE PLUS Dernier ELEMENT du chemin (paths)

              _displayLibelle,  _label, _libelle, _clickAsso, mOrigine, mNoeud = _Out_displayLibelle, _lib_Categories_out, _libelle_Categories_out, _mItemClicAssociation, 'CAT_OUT', _noeud  
              nodeUser = QTreeWidgetItem(None, [ _displayLibelle,  _label, _libelle, _clickAsso, mOrigine, mNoeud ])
              self.design_Items(nodeUser, self.dicInVersOutDesign, _label, _color_Out_InVersOut) #For colorisation
              
              # - Recherche dans le dictionnaire si existance de l'item en balayant les ancêtres (parents)
              if len(paths) == 0 :
                 self.self_Cat_Out.insertTopLevelItems( rowNodeOut, [ nodeUser ] )
                 dictNoeudsArboOut[_label] = nodeUser
                 rowNodeOut += 1
              else :
                 iElem = 0
                 while iElem < len(paths) : 
                    newNoeud = paths[iElem]
                    _returnAttribCategorie = self.returnAttribCategoriesEnFonctionLibelleTemplateCategorie(newNoeud, self.mListCategories)[0]
                    _lib_Categories_out     = _returnAttribCategorie["path"]
                    _libelle_Categories_out = _returnAttribCategorie["label"]
                    _path_elements_out   = re.split(r'\s*[/]\s*', _lib_Categories_out) #pour découper le chemin, 

                    if _returnAttribCategorie["origin"] == "local" :
                       _Out_displayLibelleNewNoeud = str(_libelle_Categories_out) + self.sepLeftTemplate + str(_path_elements_out[ -1 ]) + self.sepRightTemplate # For Affichage LIBELLE PLUS Dernier ELEMENT du chemin (paths)
                    else :
                       _Out_displayLibelleNewNoeud = str(_path_elements_out[ -1 ]) + self.sepLeftTemplate + str(_libelle_Categories_out) + self.sepRightTemplate # For Affichage LIBELLE PLUS Dernier ELEMENT du chemin (paths)

                    _displayLibelleNewNoeud, _labelNewNoeud, _libelleNewNoeud, _clickAssoNewNoeud, mOrigineNewNoeud, _noeudNewNoeud = _Out_displayLibelleNewNoeud, _lib_Categories_out, _libelle_Categories_out, _mItemClicAssociation, 'CAT_OUT', mNoeud
                    nodeUserNewNoeud = QTreeWidgetItem(None, [ _displayLibelleNewNoeud, _labelNewNoeud, _libelleNewNoeud, _clickAssoNewNoeud, mOrigineNewNoeud, _noeudNewNoeud ])
                    self.design_Items(nodeUserNewNoeud, self.dicInVersOutDesign, _labelNewNoeud, _color_Out_InVersOut) #For colorisation
                    
                    if newNoeud not in dictNoeudsArboOut : # Si l'ancêtre n'est pas dans le dictionnaire OUT

                       if len(paths) == 1 :
                          self.self_Cat_Out.insertTopLevelItems( rowNodeOut, [ nodeUserNewNoeud ] )
                          self.design_Items(nodeUserNewNoeud, self.dicInVersOutDesign, _labelNewNoeud, _color_Out_InVersOut) #For colorisation
                          rowNodeOut += 1
                       else :
                          dictNoeudsArboOut[ paths[iElem - 1] ].addChild( nodeUserNewNoeud )
                          dictNoeudsArboOut[ paths[iElem - 1] ].setIcon(0, iconSource)
                          self.design_Items(nodeUserNewNoeud, self.dicInVersOutDesign, _labelNewNoeud, _color_Out_InVersOut) #For colorisation
                       dictNoeudsArboOut[ _labelNewNoeud ]  = nodeUserNewNoeud
                    iElem += 1
                    
                 # Et enfin on ajoute ma catégorie   
                 dictNoeudsArboOut[_labelNewNoeud].addChild( nodeUser )
                 self.design_Items(nodeUserNewNoeud, self.dicInVersOutDesign, _labelNewNoeud, _color_Out_InVersOut) #For colorisation
                 dictNoeudsArboOut[_labelNewNoeud].setIcon(0, iconSource)
                 dictNoeudsArboOut[_label]  = nodeUser

           i += 1
        #Create Arbo

        self.self_Cat_In.itemClicked.connect( self.ihmsPlume_CAT_IN_OUT ) 
        self.self_Cat_Out.itemClicked.connect( self.ihmsPlume_CAT_IN_OUT ) 
        return

    #===============================              
    def ihmsPlume_CAT_IN_OUT(self, item, column): 
        mItemClic_CAT_IN_OUT = item.data(1, Qt.DisplayRole)  # id catégorie
        mItemClicAssociation = item.data(3, Qt.DisplayRole)  # id association
        mOrigine             = item.data(4, Qt.DisplayRole)  # Origine Cat In ou Cat OUT

        if mOrigine == "CAT_IN" :
           #Affiche les attributs
           afficheAttributs( self, self.groupBoxAttributsModeleCategorie, self.mapping_template_categories, True ) 
           #Initialise les attributs avec valeurs
           initialiseAttributsModeleCategorie( self, mItemClic_CAT_IN_OUT, mItemClicAssociation, self.groupBoxAttributsModeleCategorie, self.mapping_template_categories, self.mListTemplateCategories, True ) 
        else :   
           #Efface les attributs
           afficheAttributs( self, self.groupBoxAttributsModeleCategorie, self.mapping_template_categories, False ) 
        return

    #===============================              
    def moveDoubleClicked(self, item, column):
        if item == None : return 
        _pathIcons = os.path.dirname(__file__) + "/icons/logo"
        iconSource = returnIcon(_pathIcons + "/plume.svg")  
        _pathIcons2 = os.path.dirname(__file__) + "/icons/general"
        iconSource2 = returnIcon(_pathIcons2 + "/verrou.svg")  

        # _label      Nom de la catégorie             (colonne 1 in QtreeWidget)
        # _libelle    Nom du libellé de la catégorie  (colonne 2 in QtreeWidget) 
        # _clickAsso  Nom du modèle cliqué
        # mOrigine    Sens (In vers Out ou vice Versa
        # mNoeud      Est-ce un Noeud
        mItemClic_CAT_IN_OUT         = item.data(1, Qt.DisplayRole)  # id catégorie
        mItemClic_libelle_CAT_IN_OUT = item.data(2, Qt.DisplayRole)  # deuxième colonne dans les treeview
        mItemClicAssociation         = item.data(3, Qt.DisplayRole)  # id association
        mOrigine                     = item.data(4, Qt.DisplayRole)  # Origine Cat In ou Cat OUT
        mNoeud                       = True if item.data(5, Qt.DisplayRole) == "True" else False  # si c'est un noeud

        self.mListTemplateCategories  = self._selfCreateTemplate.mListTemplateCategories
        listNew = [] 

        # Eclatement for ancêtres du clic IN
        path_elements   = re.split(r'\s*[/]\s*', mItemClic_CAT_IN_OUT) #pour découper le chemin, 
        paths           = [ ' / '.join(path_elements[:ii + 1] ) for ii in range(len(path_elements) - 1) ]  #Chemin des parents

        if mOrigine == "CAT_IN" :
           # =======================
           d = list(self.mListTemplateCategories)
           listNew = [] 
           for elemDict in d :
               #if elemDict["tpl_label"] == mItemClicAssociation : #Gestion du modèle template catégories sélectionné
               if str(elemDict["tpl_id"]) == mItemClicAssociation : #Gestion du modèle template catégories sélectionné
                  _lib_Template_Categories = elemDict["shrcat_path"] if elemDict["shrcat_path"] != None else elemDict["loccat_path"]
                  _lib = _lib_Template_Categories
                  if mNoeud :
                     # Eclatement for ancêtres dans la liste des mListTemplateCategories
                     path_elements_lib_Template_Categories   = re.split(r'\s*[/]\s*', _lib_Template_Categories) #pour découper le chemin, 
                     paths_lib_Template_Categories           = [ ' / '.join(path_elements_lib_Template_Categories[:ii + 1] ) for ii in range(len(path_elements_lib_Template_Categories) - 1) ]  #Chemin des parents
                     _lib_Template_Categories = _lib_Template_Categories if len(paths_lib_Template_Categories) == 0 else paths_lib_Template_Categories[0]

                  if mItemClic_CAT_IN_OUT not in _lib_Template_Categories :
                     listNew.append(elemDict)
                  else : 
                     self.dicInVersOutDesign[_lib] = mItemClic_CAT_IN_OUT
                     if _lib in self.dicOutVersInDesign :  del self.dicOutVersInDesign[_lib]   # Suppprimer la clé dans l'autre dictionnaire 
   
               else :   
                  listNew.append(elemDict)
           # =======================

        elif mOrigine == "CAT_OUT" :
           # =======================
           # alimentation d'une liste avec les parent et les enfant du QTreeWidgetItem sélectionné
           iterator = QTreeWidgetItemIterator(self.self_Cat_Out)
           _mListOutVersInForAppend_Template_categories = []

           finParentChildren = False
           while iterator.value() :
              
              if not finParentChildren : 
                 if item.text(1) == iterator.value().text(1) :
                    __mItemClic_CAT_IN_OUT         =  iterator.value().text(1)  # id catégorie
                    __mItemClic_libelle_CAT_IN_OUT =  iterator.value().text(2)  # deuxième colonne dans les treeview
                    __mItemClicAssociation         =  iterator.value().text(3)  # id association
                    __mOrigine                     =  iterator.value().text(4)  # Origine Cat In ou Cat OUT
                    __mNoeud                       = True if  iterator.value().text(5) == "True" else False  # si c'est un noeud
                    #
                    _mListOutVersInForAppend_Template_categories.append(iterator.value())
                    _mListeParentItemParent = self.returnValueItemParent(item, column)
                    #
                    finParentChildren = True

              elif finParentChildren : 
                 if iterator.value().parent() == None :
                    break
                 #
                 if item.text(1) in iterator.value().text(1) :
                    __mItemClic_CAT_IN_OUT         =  iterator.value().text(1)  # id catégorie
                    __mItemClic_libelle_CAT_IN_OUT =  iterator.value().text(2)  # deuxième colonne dans les treeview
                    __mItemClicAssociation         =  iterator.value().text(3)  # id association
                    __mOrigine                     =  iterator.value().text(4)  # Origine Cat In ou Cat OUT
                    __mNoeud                       = True if  iterator.value().text(5) == "True" else False  # si c'est un noeud
                    _mListOutVersInForAppend_Template_categories.append(iterator.value())

              iterator += 1
           _temp = [ elem.text(1) for elem in _mListOutVersInForAppend_Template_categories ]
           
           #liste des éléments (parents et enfants) à ajouter dans le template Catégories 
           mListOutVersInForAppend_Template_categories = _mListeParentItemParent + _temp
           
           # alimentation de la liste mListTemplateCategories avec mListOutVersInForAppend_Template_categories
           listNew = [] 
           d                = list(self.mListTemplateCategories)
           dElemDictCategories = list(self.mListCategories)

           # =======================
           iInsertTemplateCategories = 0
           while iInsertTemplateCategories in range(len(d)) :
              elemDict = d[iInsertTemplateCategories]
              #if elemDict["tpl_label"] == mItemClicAssociation : #Gestion du modèle template catégories sélectionné
              if str(elemDict["tpl_id"]) == mItemClicAssociation : #Gestion du modèle template catégories sélectionné
                 _lib_Template_Categories = elemDict["shrcat_path"] if elemDict["shrcat_path"] != None else elemDict["loccat_path"]
                 _lib = _lib_Template_Categories

                 iElemDictOutVersIn = 0
                 # Boucle sur les futures insertions
                 while iElemDictOutVersIn in range(len(mListOutVersInForAppend_Template_categories)) :
                    #Create structure Template_Categories
                    elemDictAppend = {}
                    for k, v in self.mapping_template_categories.items() : 
                        elemDictAppend[k] = None        
                           
                    elemDictOutVersIn = mListOutVersInForAppend_Template_categories[iElemDictOutVersIn]

                    #Find infos for catégorie insert
                    for elemDictCategories in dElemDictCategories :
                        if elemDictOutVersIn == elemDictCategories["path"] : 
                           newAttrib = { \
                                        'tplcat_id': elemDict["tplcat_id"], \
                                        'tpl_id': int(mItemClicAssociation), \
                                        'label': elemDictCategories["label"], \
                                        'loccat_path' if elemDictCategories["origin"] == "local" else 'shrcat_path' : elemDictOutVersIn \
                                       }
                           elemDictAppend.update(newAttrib)
                           # --
                           listNew.insert(iInsertTemplateCategories + iElemDictOutVersIn, elemDictAppend)
                           self.dicOutVersInDesign[elemDictOutVersIn] = mItemClicAssociation
                           if elemDictOutVersIn in self.dicInVersOutDesign :  del self.dicInVersOutDesign[elemDictOutVersIn]   # Suppprimer la clé dans l'autre dictionnaire 
                           break
                    iElemDictOutVersIn += 1

                    if ( _lib_Template_Categories not in listNew ) : listNew.append(elemDict)       
              else :
                 listNew.append(elemDict)       
           
              iInsertTemplateCategories += 1

           # =======================
           # =======================
           # =======================
           # Create Delta mListTemplates / mListTemplateCategories
           mListTemplatesDELTA_mListTemplateCategories = []
           for elemListTemplates in self.mListTemplates : 
               findKey    = False
               #findKeyLib = elemListTemplates["tpl_label"]
               findKeyLib = elemListTemplates["tpl_id"]
               for elemListTemplateCategorie in self.mListTemplateCategories :
                  #if findKeyLib == elemListTemplateCategorie["tpl_label"] : 
                  if findKeyLib == elemListTemplateCategorie["tpl_id"] : 
                     findKey = True
                     break
               if not findKey : mListTemplatesDELTA_mListTemplateCategories.append(elemListTemplates)
           # =======================
           # =======================
           # =======================
           # Append Delta mListTemplates / mListTemplateCategories
           # Ce sont les modèles sans catégories utilisées
           # =======================
           d_TC_Delta = list(mListTemplatesDELTA_mListTemplateCategories)
           iInsertTemplate = 0
           while iInsertTemplate in range(len(d_TC_Delta)) :
              elemDict = d_TC_Delta[iInsertTemplate]
              #if elemDict["tpl_label"] == mItemClicAssociation : #Gestion du modèle template catégories sélectionné
              if str(elemDict["tpl_id"]) == mItemClicAssociation : #Gestion du modèle template catégories sélectionné
                 #_lib_Template_Categories = elemDict["tpl_label"]
                 _lib_Template_Categories = elemDict["tpl_id"]
                 _lib = _lib_Template_Categories

                 iElemDictOutVersIn = 0
                 # Boucle sur les futures insertions
                 while iElemDictOutVersIn in range(len(mListOutVersInForAppend_Template_categories)) :
                    #Create structure Template_Categories
                    elemDictAppend = {}
                    for k, v in self.mapping_template_categories.items() : 
                        elemDictAppend[k] = None        
                           
                    elemDictOutVersIn = mListOutVersInForAppend_Template_categories[iElemDictOutVersIn]

                    #Find infos for catégorie insert
                    for elemDictCategories in dElemDictCategories :
                        if elemDictOutVersIn == elemDictCategories["path"] : 
                           newAttrib = { \
                                        'tplcat_id': "", \
                                        'tpl_id': int(mItemClicAssociation), \
                                        'label': elemDictCategories["label"], \
                                        'loccat_path' if elemDictCategories["origin"] == "local" else 'shrcat_path' : elemDictOutVersIn \
                                       }
                           elemDictAppend.update(newAttrib)
                           # --
                           listNew.insert(iInsertTemplate + iElemDictOutVersIn, elemDictAppend)
                           self.dicOutVersInDesign[elemDictOutVersIn] = mItemClicAssociation
                           if elemDictOutVersIn in self.dicInVersOutDesign :  del self.dicInVersOutDesign[elemDictOutVersIn]   # Suppprimer la clé dans l'autre dictionnaire 
                           break
                    iElemDictOutVersIn += 1
              iInsertTemplate += 1
           # =======================
           # =======================
           # =======================

        self._selfCreateTemplate.mListTemplateCategories = list(listNew)  # Contenu changé 
        self.mListTemplateCategories          = self._selfCreateTemplate.mListTemplateCategories
        self.mListCategories                  = self._selfCreateTemplate.mListCategories   
        # == Cat Utilisées et Non Utilisées==
        
        print( self.dicInVersOutDesign)
        
        self._selfCreateTemplate.mTreeListeCategorieIn.clear()
        self._selfCreateTemplate.mTreeListeCategorieOut.clear()
        self._selfCreateTemplate.mTreeListeCategorieIn.affiche_CAT_IN_OUT(self._selfCreateTemplate, mItemClicAssociation, self._selfCreateTemplate.mTreeListeCategorieIn, self._selfCreateTemplate.mTreeListeCategorieOut, self.dicInVersOutDesign, self.dicOutVersInDesign, action = True)
        #Efface les attributs
        afficheAttributs( self._selfCreateTemplate, self._selfCreateTemplate.groupBoxAttributsModeleCategorie, self._selfCreateTemplate.mapping_template_categories, False ) 
        return

    #===============================              
    def returnAttribCategoriesEnFonctionLibelleTemplateCategorie(self, libTemplateCategories, dicCategories) :
        _returnLibelleTemplateCategorie = []
        _returnLibelleTemplateCategorie = [ elemDic for elemDic in dicCategories if elemDic["path"] == libTemplateCategories ]  
        return _returnLibelleTemplateCategorie

    #===============================              
    def returnValueItemParent(self, item, column):          
        if item == None : return None 
        mReturnValueItemParent, mItem = [], item
        while True :
           mReturnValueItemParent.append(mItem.data(1, Qt.DisplayRole))
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
           mReturnValueItem.append(mItem.data(column, Qt.DisplayRole))
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
        self.setColumnCount(2)
        self.setHeaderLabels(["Noms", "Commentaires"])
        self.setSelectionMode(QAbstractItemView.SingleSelection	)  
        self.mnodeToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Right click to add / delete a model", None)         #Click droit pour supprimer un Modèle
        return

    #===============================              
    def afficheMODELE(self, _selfCreateTemplate, listeModeleCol1, listeModeleCol2):
        self.groupBoxAttributsModele          = _selfCreateTemplate.groupBoxAttributsModele
        self.mapping_templates                = _selfCreateTemplate.mapping_templates

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
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect( self.menuContextuelPlumeMODELE)
        self.expandAll()
        return
        
    #===============================              
    def menuContextuelPlumeMODELE(self, point):
        index = self.indexAt(point)
        if not index.isValid():
           return
        #-------
        if index.data(0) != None : 
           self.treeMenu = QMenu(self)
           #-
           menuIcon = returnIcon(os.path.dirname(__file__) + "\\icons\\buttons\plus_button.svg")          
           treeAction_addTooltip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Add model", None)  #Supprimer le modèle
           self.treeAction_add = QAction(QIcon(menuIcon), treeAction_addTooltip, self.treeMenu)
           self.treeMenu.addAction(self.treeAction_add)
           self.treeAction_add.setToolTip(treeAction_addTooltip)
           self.treeAction_add.triggered.connect( self.ihmsPlumeAdd )
           #-
           menuIcon = returnIcon(os.path.dirname(__file__) + "\\icons\\general\\delete.svg")          
           treeAction_delTooltip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Remove model", None)  #Supprimer le modèle
           self.treeAction_del = QAction(QIcon(menuIcon), treeAction_delTooltip, self.treeMenu)
           self.treeMenu.addAction(self.treeAction_del)
           self.treeAction_del.setToolTip(treeAction_delTooltip)
           self.treeAction_del.triggered.connect( self.ihmsPlumeDel )
           #-------
           self.treeMenu.exec_(self.mapToGlobal(point))
        return
        
    #===============================              
    def ihmsPlumeMODELE(self, item, column): 
        mItemClicModele = item.data(0, Qt.DisplayRole)
        self.modeleActif = mItemClicModele
        
        #=== Nécessaire pour récupérer les valeurs initiales et/ ou sauvegardées              
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
        initialiseAttributsModeles( self, mItemClicModele, self.groupBoxAttributsModele, self.mapping_templates, self.mListTemplates, True ) 
        return

    #===============================              
    def ihmsPlumeUpdateModele(self, mDialog, mId):
        #===============================              
        dicForQuerieForAddModele = returnListObjKeyValue(self, self.groupBoxAttributsModele, self.mapping_templates)

        mKeySql = queries.query_insert_or_update_meta_template(dicForQuerieForAddModele)
        r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self._selfCreateTemplate.Dialog.mConnectEnCours, mKeySql, optionRetour = "fetchone")
        self._selfCreateTemplate.Dialog.mConnectEnCours.commit()
        #- Réinit
        mKeySql = queries.query_read_meta_template()
        r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self._selfCreateTemplate.Dialog.mConnectEnCours, mKeySql, optionRetour = "fetchall")
        self.mListTemplates = [row[0] for row in r]
        listeModeleCol1, listeModeleCol2 = returnList_Id_Label( self.mListTemplates )
        self.clear()
        self.afficheMODELE(self._selfCreateTemplate, listeModeleCol1, listeModeleCol2)
        return

    #===============================              
    def ihmsPlumeAdd(self):
        #===============================              
        afficheAttributs( self, self.groupBoxAttributsModele, self.mapping_templates, True ) 
        self._selfCreateTemplate.buttonAddModele.setVisible(True)
        initialiseAttributsModeles( self, "", self.groupBoxAttributsModele, self.mapping_templates, self.mListTemplates, True, "Vierge" ) 
        return
                
    #===============================              
    def ihmsPlumeDel(self): 
        current_item = self.currentItem()           #itemCourant
        self.ihmsPlumeMODELE( current_item, None )  #Affiche les attributs pour impélmenter le dicForQuerieForAddModele
        self.takeTopLevelItem(self.indexOfTopLevelItem(current_item))
        #
        dicForQuerieForAddModele = returnListObjKeyValue(self, self.groupBoxAttributsModele, self.mapping_templates)
        mKeySql = queries.query_delete_meta_template(dicForQuerieForAddModele)
        r, zMessError_Code, zMessError_Erreur, zMessError_Diag = executeSql(self, self._selfCreateTemplate.Dialog.mConnectEnCours, mKeySql, optionRetour = None)
        self._selfCreateTemplate.Dialog.mConnectEnCours.commit()
        #Efface les attributs
        afficheAttributs( self, self.groupBoxAttributsModele, self.mapping_templates, False ) 
        self._selfCreateTemplate.buttonAddModele.setVisible(False)
        return

    #===============================              
    def ihmsPlumeAddCSW(self, mDialog, mId):
        #===============================              
        iterator = QTreeWidgetItemIterator(self)
        _mListID = []
        while iterator.value() :
           itemValueLibText = iterator.value().text(0)
           if itemValueText != "" : 
              if itemValueText not in URLCSWDEFAUT.split(",") and itemValueText != self.mLibNodeUrlDefaut and itemValueText != self.mLibNodeUrlUser  :
                 _mListCSW.append(itemValueText)
                 _mListLibCSW.append(itemValueLibText)
           iterator += 1
        url_list   =  _mListCSW 
        label_list =  _mListLibCSW
        
        #===============================              
        self.clear()
        url_list, label_list = self.update_csw(url_list, label_list, mCsw, mLibCsw)
        self.afficheCSW(url_list, label_list, self._mZoneUrl, self._mZoneLibUrl, self._mZoneUrlId )
        return
