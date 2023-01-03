# (c) Didier  LECLERC 2020 CMSIG MTE-MCTRCT/SG/SNUM/UNI/DRC Site de Rouen
# créé 2022

from . import bibli_plume
from .bibli_plume import *
import os.path
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qt import *
#
from . import bibli_plume
from .bibli_plume import *
#

#

class Ui_Dialog_CreateTemplate(object):
    def setupUiCreateTemplate(self, DialogCreateTemplate, Dialog):
        #-
        #-
        self.mDic_LH = bibli_plume.returnAndSaveDialogParam(self, "Load")
        self.editStyle        = self.mDic_LH["QEdit"]              #style saisie
        self.labelBackGround  = self.mDic_LH["QLabelBackGround"] #QLabel    
        self.epaiQGroupBox    = self.mDic_LH["QGroupBoxEpaisseur"] #épaisseur QGroupBox
        self.lineQGroupBox    = self.mDic_LH["QGroupBoxLine"]    #trait QGroupBox
        self.policeQGroupBox  = self.mDic_LH["QGroupBoxPolice"]  #Police QGroupBox
        self.policeQTabWidget = self.mDic_LH["QTabWidgetPolice"] #Police QTabWidget
        #-
        #-
        self.DialogCreateTemplate = DialogCreateTemplate
        self.Dialog = Dialog   #Pour remonter les variables de la boite de dialogue
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
        titlegroupBoxListeModeleCategorie = QtWidgets.QApplication.translate("CreateTemplate_ui", "Existing models", None)      #{Modèles existants}
        self.groupBoxListeModeleCategorie.setTitle(titlegroupBoxListeModeleCategorie)
        #-
        self.layoutListeModeleCategorie = QtWidgets.QGridLayout()
        self.groupBoxListeModeleCategorie.setLayout(self.layoutListeModeleCategorie)
        self.layout_tab_widget_Association.addWidget(self.groupBoxListeModeleCategorie)
        #-
        #------ TREEVIEW   
        self.mTreeListeModeleCategorie = TREEVIEWASSOCIATION()
        self.layoutListeModeleCategorie.addWidget(self.mTreeListeModeleCategorie)
        #-
        self.mTreeListeModeleCategorie.clear()
        
        #------ TEMPORAIRE 
        listeAssociationCol1 = ["Données externes", "Calcul V1 (Manuel)", "Calcul V2 (Mixte)", "Calcul V3 (Automatique)"]
        listeAssociationCol1 = list(reversed(listeAssociationCol1))
        listeAssociationCol2 = ["Commentaires pour Données externes", "Commentaires pour Calcul V1 (Manuel)", "Commentaires pour Calcul V2 (Mixte)", "Commentaires pour Calcul V3 (Automatique)"]
        listeAssociationCol2 = list(reversed(listeAssociationCol2))
        #------ TEMPORAIRE 
        self.mTreeListeModeleCategorie.afficheASSOCIATION(listeAssociationCol1, listeAssociationCol2)

        #------ 
        #Liste catégories
        self.groupBoxListeCategorie = QtWidgets.QGroupBox()
        self.groupBoxListeCategorie.setObjectName("groupBoxListeCategorie")
         #-
        self.layoutListeCategorie = QtWidgets.QGridLayout()
        self.layoutListeCategorie.setColumnStretch(0, 5)
        self.layoutListeCategorie.setColumnStretch(1, 0.5)
        self.layoutListeCategorie.setColumnStretch(2, 5)
        self.groupBoxListeCategorie.setLayout(self.layoutListeCategorie)
        self.layout_tab_widget_Association.addWidget(self.groupBoxListeCategorie)
        #-

        #------ Déclare TREEVIEW
        self.labelCategorieOut = QtWidgets.QLabel()
        self.labelCategorieOut.setText(QtWidgets.QApplication.translate("CreateTemplate_ui", "Categories not belonging", None))   #Catégories n'appartenant pas
        self.labelCategorieIn = QtWidgets.QLabel()
        self.labelCategorieIn.setText(QtWidgets.QApplication.translate("CreateTemplate_ui", "Categories belonging", None))   #Catégories appartenant
         
        self.mTreeListeCategorieOut = TREEVIEW_CAT_IN_OUT()
        self.mTreeListeCategorieIn  = TREEVIEW_CAT_IN_OUT()
        
        #------ TREEVIEW CATEGORIES OUT
        self.layoutListeCategorie.addWidget(self.labelCategorieOut, 0 ,0, Qt.AlignTop)
        self.layoutListeCategorie.addWidget(self.mTreeListeCategorieOut, 1 ,0)
        #-
        self.mTreeListeCategorieOut.clear()

        #------ TEMPORAIRE 
        listeCatCol1 = ["Cat1", "Cat3", "Cat4"]
        listeCatCol1 = list(reversed(listeCatCol1))
        listeCatCol2 = ["Catégories concernant ......", "Catégories concernant ......", "Catégories concernant ......"]
        listeCatCol2 = list(reversed(listeCatCol2))
        #------ TEMPORAIRE 

        self.mTreeListeCategorieOut.affiche_CAT_IN_OUT("CAT_OUT", self.mTreeListeCategorieOut, self.mTreeListeCategorieIn, listeCatCol1, listeCatCol2)

        #------ TREEVIEW CATEGORIES IN 
        self.layoutListeCategorie.addWidget(self.labelCategorieIn, 0 ,2, Qt.AlignTop)
        self.layoutListeCategorie.addWidget(self.mTreeListeCategorieIn, 1 ,2)
        #-
        self.mTreeListeCategorieIn.clear()
        
        #------ TEMPORAIRE 
        listeCatCol1 = ["Cat2"]
        listeCatCol1 = list(reversed(listeCatCol1))
        listeCatCol2 = ["Catégories concernant ......"]
        listeCatCol2 = list(reversed(listeCatCol2))
        #------ TEMPORAIRE 

        self.mTreeListeCategorieIn.affiche_CAT_IN_OUT("CAT_IN", self.mTreeListeCategorieOut, self.mTreeListeCategorieIn, listeCatCol1, listeCatCol2)

        #Liste ATTRIBUTS modeles / catégories
        self.groupBoxAttributsModeleCategorie = QtWidgets.QGroupBox()
        self.groupBoxAttributsModeleCategorie.setObjectName("groupBoxAttributsModeleCategorie")
        self.groupBoxAttributsModeleCategorie.setStyleSheet("QGroupBox { border: 0px solid blue;}")
        #-
        self.layoutAttributsModeleCategorie = QtWidgets.QGridLayout()
        self.layoutAttributsModeleCategorie.setColumnStretch(0, 3)
        self.layoutAttributsModeleCategorie.setColumnStretch(1, 7)
        self.layoutAttributsModeleCategorie.setColumnStretch(2, 1)
        self.groupBoxAttributsModeleCategorie.setLayout(self.layoutAttributsModeleCategorie)
        self.layout_tab_widget_Association.addWidget(self.groupBoxAttributsModeleCategorie)

        #=====================================
        # [ == scrolling == ]
        self.scroll_bar_AttributsModeleCategorie = QtWidgets.QScrollArea(self.tab_widget_Association) 
        self.scroll_bar_AttributsModeleCategorie.setStyleSheet("QScrollArea { border: 0px solid red;}")
        self.scroll_bar_AttributsModeleCategorie.setWidgetResizable(True)
        self.scroll_bar_AttributsModeleCategorie.setWidget(self.groupBoxAttributsModeleCategorie)
        self.layout_tab_widget_Association.addWidget(self.scroll_bar_AttributsModeleCategorie, 2, 0)
        #=====================================

        #=====================================
        # [ == cat1 == ]
        mTextToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Catégorie 1") 
        _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "toolTipWidget", "aligneWidget", "styleSheet", "wordWrap" ]
        _ListValues = [ QtWidgets.QLabel(), "RowSpan", "modCat_Lib_Attrib1", mTextToolTip, Qt.AlignRight, "QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}", True ]
        dicParamLabel = dict(zip(_Listkeys, _ListValues))
        self.modCat_Lib_Attrib1 = genereLabelWithDict( dicParamLabel )
        #-
        mTextToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Catégorie 1") 
        _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "toolTipWidget", "aligneWidget", "styleSheet" ]
        _ListValues = [ QtWidgets.QLineEdit(), "RowSpan", "modCat_Attrib1", mTextToolTip, Qt.AlignRight, "QLineEdit {  font-family:" + self.policeQGroupBox  +";}" ]
        dicParamButton = dict(zip(_Listkeys, _ListValues))
        self.modCat_Attrib1 = genereButtonsWithDict( dicParamButton )
        self.layoutAttributsModeleCategorie.addWidget(self.modCat_Lib_Attrib1, 0, 0, Qt.AlignTop)
        self.layoutAttributsModeleCategorie.addWidget(self.modCat_Attrib1    , 0, 1, Qt.AlignTop)
        #-
        # [ == cat2 == ]
        mTextToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Catégorie 2") 
        _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "toolTipWidget", "aligneWidget", "styleSheet", "wordWrap" ]
        _ListValues = [ QtWidgets.QLabel(), "PlaceHolder", "modCat_Lib_Attrib2", mTextToolTip, Qt.AlignRight, "QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}", True ]
        dicParamLabel = dict(zip(_Listkeys, _ListValues))
        self.modCat_Lib_Attrib2 = genereLabelWithDict( dicParamLabel )
        #-
        mTextToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Catégorie 2") 
        _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "toolTipWidget", "aligneWidget", "styleSheet" ]
        _ListValues = [ QtWidgets.QLineEdit(), "Mon modèle qui va bien ........", "modCat_Attrib2", mTextToolTip, Qt.AlignRight, "QLineEdit {  font-family:" + self.policeQGroupBox  +";}" ]
        dicParamButton = dict(zip(_Listkeys, _ListValues))
        self.modCat_Attrib2 = genereButtonsWithDict( dicParamButton )
        self.layoutAttributsModeleCategorie.addWidget(self.modCat_Lib_Attrib2, 1, 0, Qt.AlignTop)
        self.layoutAttributsModeleCategorie.addWidget(self.modCat_Attrib2    , 1, 1, Qt.AlignTop)
        #-
        # [ == cat3 == ]
        mTextToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Catégorie 3") 
        _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "toolTipWidget", "aligneWidget", "styleSheet", "wordWrap" ]
        _ListValues = [ QtWidgets.QLabel(), "Lecture seule", "modCat_Lib_Attrib3", mTextToolTip, Qt.AlignRight, "QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}", True ]
        dicParamLabel = dict(zip(_Listkeys, _ListValues))
        self.modCat_Lib_Attrib3 = genereLabelWithDict( dicParamLabel )
        #-
        mTextToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Catégorie 3") 
        _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "toolTipWidget", "aligneWidget", "styleSheet", "checked" ]
        _ListValues = [ QtWidgets.QCheckBox(), "", "modCat_Attrib3", mTextToolTip, Qt.AlignRight, "QLineEdit {  font-family:" + self.policeQGroupBox  +";}", True ]
        dicParamButton = dict(zip(_Listkeys, _ListValues))
        self.modCat_Attrib3 = genereButtonsWithDict( dicParamButton )
        self.layoutAttributsModeleCategorie.addWidget(self.modCat_Lib_Attrib3, 2, 0, Qt.AlignTop)
        self.layoutAttributsModeleCategorie.addWidget(self.modCat_Attrib3    , 2, 1, Qt.AlignTop)
        #-
        # [ == cat4 == ]
        mTextToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Catégorie 4") 
        _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "toolTipWidget", "aligneWidget", "styleSheet", "wordWrap" ]
        _ListValues = [ QtWidgets.QLabel(), "Onglet", "modCat_Lib_Attrib4", mTextToolTip, Qt.AlignRight, "QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}", True ]
        dicParamLabel = dict(zip(_Listkeys, _ListValues))
        self.modCat_Lib_Attrib4 = genereLabelWithDict( dicParamLabel )
        #-
        mDicQcomboBox = ["Généralités", "Géométries", "Autres"]
        mTextToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Catégorie 4") 
        _Listkeys   = [ "typeWidget", "listItems", "currentText", "nameWidget", "toolTipWidget", "aligneWidget", "styleSheet" ]
        _ListValues = [ QtWidgets.QComboBox(), mDicQcomboBox, mDicQcomboBox[1], "modCat_Attrib4", mTextToolTip, Qt.AlignRight, "QLineEdit {  font-family:" + self.policeQGroupBox  +";}" ]
        dicParamButton = dict(zip(_Listkeys, _ListValues))
        self.modCat_Attrib4 = genereButtonsWithDict( dicParamButton )
        self.layoutAttributsModeleCategorie.addWidget(self.modCat_Lib_Attrib4, 3, 0, Qt.AlignTop)
        self.layoutAttributsModeleCategorie.addWidget(self.modCat_Attrib4    , 3, 1, Qt.AlignTop)
        #-
        # [ == cat5 == ]
        mTextToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Catégorie 5") 
        _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "toolTipWidget", "aligneWidget", "styleSheet", "wordWrap" ]
        _ListValues = [ QtWidgets.QLabel(), "libellé Etc ....", "modCat_Lib_Attrib5", mTextToolTip, Qt.AlignRight, "QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}", True ]
        dicParamLabel = dict(zip(_Listkeys, _ListValues))
        self.modCat_Lib_Attrib5 = genereLabelWithDict( dicParamLabel )
        #-
        mTextToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Catégorie 5") 
        _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "toolTipWidget", "aligneWidget", "styleSheet" ]
        _ListValues = [ QtWidgets.QLineEdit(), "Etc ....", "modCat_Attrib5", mTextToolTip, Qt.AlignRight, "QLineEdit {  font-family:" + self.policeQGroupBox  +";}" ]
        dicParamButton = dict(zip(_Listkeys, _ListValues))
        self.modCat_Attrib5 = genereButtonsWithDict( dicParamButton )
        self.layoutAttributsModeleCategorie.addWidget(self.modCat_Lib_Attrib5, 4, 0, Qt.AlignTop)
        self.layoutAttributsModeleCategorie.addWidget(self.modCat_Attrib5    , 4, 1, Qt.AlignTop)
        #-
        # [ == cat6 == ]
        mTextToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Catégorie 6") 
        _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "toolTipWidget", "aligneWidget", "styleSheet", "wordWrap" ]
        _ListValues = [ QtWidgets.QLabel(), "libellé Etc ....", "modCat_Lib_Attrib6", mTextToolTip, Qt.AlignRight, "QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}", True ]
        dicParamLabel = dict(zip(_Listkeys, _ListValues))
        self.modCat_Lib_Attrib6 = genereLabelWithDict( dicParamLabel )
        #-
        mTextToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Catégorie 6") 
        _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "toolTipWidget", "aligneWidget", "styleSheet" ]
        _ListValues = [ QtWidgets.QLineEdit(), "Etc ....", "modCat_Attrib6", mTextToolTip, Qt.AlignRight, "QLineEdit {  font-family:" + self.policeQGroupBox  +";}" ]
        dicParamButton = dict(zip(_Listkeys, _ListValues))
        self.modCat_Attrib6 = genereButtonsWithDict( dicParamButton )
        self.layoutAttributsModeleCategorie.addWidget(self.modCat_Lib_Attrib6, 5, 0, Qt.AlignTop)
        self.layoutAttributsModeleCategorie.addWidget(self.modCat_Attrib6    , 5, 1, Qt.AlignTop)
        #-
        # [ == cat7 == ]
        mTextToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Catégorie 7") 
        _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "toolTipWidget", "aligneWidget", "styleSheet", "wordWrap" ]
        _ListValues = [ QtWidgets.QLabel(), "libellé Etc ....", "modCat_Lib_Attrib7", mTextToolTip, Qt.AlignRight, "QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}", True ]
        dicParamLabel = dict(zip(_Listkeys, _ListValues))
        self.modCat_Lib_Attrib7 = genereLabelWithDict( dicParamLabel )
        #-
        mTextToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Catégorie 7") 
        _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "toolTipWidget", "aligneWidget", "styleSheet" ]
        _ListValues = [ QtWidgets.QLineEdit(), "Etc ....", "modCat_Attrib7", mTextToolTip, Qt.AlignRight, "QLineEdit {  font-family:" + self.policeQGroupBox  +";}" ]
        dicParamButton = dict(zip(_Listkeys, _ListValues))
        self.modCat_Attrib7 = genereButtonsWithDict( dicParamButton )
        self.layoutAttributsModeleCategorie.addWidget(self.modCat_Lib_Attrib7, 6, 0, Qt.AlignTop)
        self.layoutAttributsModeleCategorie.addWidget(self.modCat_Attrib7    , 6, 1, Qt.AlignTop)
        #-

        #Button Add
        #-
        self.groupBox_buttonAdd = QtWidgets.QGroupBox()
        self.groupBox_buttonAdd.setObjectName("groupBox_buttonAdd")
        self.groupBox_buttonAdd.setStyleSheet("QGroupBox { border: 0px solid green }")
        #-
        self.layout_groupBox_buttonAdd = QtWidgets.QGridLayout()
        self.layout_groupBox_buttonAdd.setContentsMargins(0, 0, 0, 0)
        self.groupBox_buttonAdd.setLayout(self.layout_groupBox_buttonAdd)
        self.layout_tab_widget_Association.addWidget(self.groupBox_buttonAdd)
        #-
        self.layout_groupBox_buttonAdd.setColumnStretch(0, 3)
        self.layout_groupBox_buttonAdd.setColumnStretch(1, 1)
        self.layout_groupBox_buttonAdd.setColumnStretch(2, 1)
        self.layout_groupBox_buttonAdd.setColumnStretch(3, 1)
        self.layout_groupBox_buttonAdd.setColumnStretch(4, 3)

        self.buttonAdd = QtWidgets.QToolButton()
        self.buttonAdd.setObjectName("buttonAdd")
        self.buttonAdd.setIcon(QIcon(os.path.dirname(__file__)+"\\icons\\general\\save.svg"))
        mbuttonAddToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Add or modify a stored CSW. The URL and label will be saved in the “My CSW” section of the table above.", None)
        self.buttonAdd.setToolTip(mbuttonAddToolTip)
        self.buttonAdd.clicked.connect(lambda : self.functionAddCsw())
        self.layout_groupBox_buttonAdd.addWidget(self.buttonAdd, 0, 2,  Qt.AlignTop)
        #Button Add
        #------

        #-
        self.groupBox_buttons = QtWidgets.QGroupBox()
        self.groupBox_buttons.setObjectName("groupBox_buttons")
        self.groupBox_buttons.setStyleSheet("QGroupBox { border: 0px solid green }")
        #-
        self.layout_groupBox_buttons = QtWidgets.QGridLayout()
        self.layout_groupBox_buttons.setContentsMargins(0, 0, 0, 0)
        self.groupBox_buttons.setLayout(self.layout_groupBox_buttons)
        self.layout_tab_widget_Association.addWidget(self.groupBox_buttons)
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
        self.layout_groupBox_buttons.addWidget(self.pushButtonAnnuler, 0, 2,  Qt.AlignTop)
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
        listeModeleCol1 = ["Données externes", "Calcul V1 (Manuel)", "Calcul V2 (Mixte)", "Calcul V3 (Automatique)"]
        listeModeleCol1 = list(reversed(listeModeleCol1))
        listeModeleCol2 = ["Commentaires pour Données externes", "Commentaires pour Calcul V1 (Manuel)", "Commentaires pour Calcul V2 (Mixte)", "Commentaires pour Calcul V3 (Automatique)"]
        listeModeleCol2 = list(reversed(listeModeleCol2))
        #------ TEMPORAIRE 
        self.mTreeListeRessourceModele.afficheMODELE(listeModeleCol1, listeModeleCol2)

        self.voletsRessource.addItem(self.zoneModele, QtWidgets.QApplication.translate("CreateTemplate_ui", "List of models"))
        #====
        #=====================================
         #Liste ATTRIBUTS modeles
        self.groupBoxAttributsModele = QtWidgets.QGroupBox()
        self.groupBoxAttributsModele.setObjectName("groupBoxAttributsModele")
        self.groupBoxAttributsModele.setStyleSheet("QGroupBox { border: 0px solid blue;}")
        #-
        self.layoutAttributsModele = QtWidgets.QGridLayout()
        #-
        self.layoutAttributsModele.setColumnStretch(0, 3)
        self.layoutAttributsModele.setColumnStretch(1, 7)
        self.layoutAttributsModele.setColumnStretch(2, 1)
        self.groupBoxAttributsModele.setLayout(self.layoutAttributsModele)
        self.layoutZoneModele.addWidget(self.groupBoxAttributsModele)

        #=====================================
        # [ == scrolling == ]
        self.scroll_bar_AttributsModele = QtWidgets.QScrollArea() 
        self.scroll_bar_AttributsModele.setStyleSheet("QScrollArea { border: 0px solid red;}")
        self.scroll_bar_AttributsModele.setWidgetResizable(True)
        self.scroll_bar_AttributsModele.setWidget(self.groupBoxAttributsModele)
        self.layoutZoneModele.addWidget(self.scroll_bar_AttributsModele, 1 , 0)
        #=====================================

        #=====================================
        # [ == attrib1 == ]
        mTextToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Attribut 1") 
        _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "toolTipWidget", "aligneWidget", "styleSheet", "wordWrap" ]
        _ListValues = [ QtWidgets.QLabel(), "Nom :", "mod_Lib_Attrib1", mTextToolTip, Qt.AlignRight, "QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}", True ]
        dicParamLabel = dict(zip(_Listkeys, _ListValues))
        self.mod_Lib_Attrib1 = genereLabelWithDict( dicParamLabel )
        #-
        mTextToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Attribut 1") 
        _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "toolTipWidget", "aligneWidget", "styleSheet" ]
        _ListValues = [ QtWidgets.QLineEdit(), "Données externes", "mod_Attrib1", mTextToolTip, Qt.AlignRight, "QLineEdit {  font-family:" + self.policeQGroupBox  +";}" ]
        dicParamButton = dict(zip(_Listkeys, _ListValues))
        self.mod_Attrib1 = genereButtonsWithDict( dicParamButton )
        self.layoutAttributsModele.addWidget(self.mod_Lib_Attrib1, 0, 0, Qt.AlignTop)
        self.layoutAttributsModele.addWidget(self.mod_Attrib1    , 0, 1, Qt.AlignTop)
        # [ == attrib2 == ]
        mTextToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Attribut 2:") 
        _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "toolTipWidget", "aligneWidget", "styleSheet", "wordWrap" ]
        _ListValues = [ QtWidgets.QLabel(), "filtre :", "mod_Lib_Attrib2", mTextToolTip, Qt.AlignRight, "QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}", True ]
        dicParamLabel = dict(zip(_Listkeys, _ListValues))
        self.mod_Lib_Attrib2 = genereLabelWithDict( dicParamLabel )
        #-
        mTextToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Attribut 2") 
        _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "toolTipWidget", "aligneWidget", "styleSheet" ]
        _ListValues = [ QtWidgets.QLineEdit(), "$1 ............", "mod_Attrib2", mTextToolTip, Qt.AlignRight, "QLineEdit {  font-family:" + self.policeQGroupBox  +";}" ]
        dicParamButton = dict(zip(_Listkeys, _ListValues))
        self.mod_Attrib2 = genereButtonsWithDict( dicParamButton )
        self.layoutAttributsModele.addWidget(self.mod_Lib_Attrib2, 1, 0, Qt.AlignTop)
        self.layoutAttributsModele.addWidget(self.mod_Attrib2    , 1, 1, Qt.AlignTop)
        # [ == attrib3 == ]
        mTextToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Attribut 3:") 
        _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "toolTipWidget", "aligneWidget", "styleSheet", "wordWrap" ]
        _ListValues = [ QtWidgets.QLabel(), "Priorité :", "mod_Lib_Attrib3", mTextToolTip, Qt.AlignRight, "QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}", True ]
        dicParamLabel = dict(zip(_Listkeys, _ListValues))
        self.mod_Lib_Attrib3 = genereLabelWithDict( dicParamLabel )
        #-
        mTextToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Attribut 3") 
        _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "toolTipWidget", "aligneWidget", "styleSheet" ]
        _ListValues = [ QtWidgets.QLineEdit(), "10", "mod_Attrib3", mTextToolTip, Qt.AlignRight, "QLineEdit {  font-family:" + self.policeQGroupBox  +";}" ]
        dicParamButton = dict(zip(_Listkeys, _ListValues))
        self.mod_Attrib3 = genereButtonsWithDict( dicParamButton )
        self.layoutAttributsModele.addWidget(self.mod_Lib_Attrib3, 2, 0, Qt.AlignTop)
        self.layoutAttributsModele.addWidget(self.mod_Attrib3    , 2, 1, Qt.AlignTop)
        # [ == attrib4 == ]
        mTextToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Attribut 4:") 
        _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "toolTipWidget", "aligneWidget", "styleSheet", "wordWrap" ]
        _ListValues = [ QtWidgets.QLabel(), "Commentaires :", "mod_Lib_Attrib4", mTextToolTip, Qt.AlignRight, "QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}", True ]
        dicParamLabel = dict(zip(_Listkeys, _ListValues))
        self.mod_Lib_Attrib4 = genereLabelWithDict( dicParamLabel )
        #-
        mTextToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Attribut 4") 
        _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "toolTipWidget", "aligneWidget", "styleSheet" ]
        _ListValues = [ QtWidgets.QLineEdit(), "Commentaires pour Données externes", "mod_Attrib4", mTextToolTip, Qt.AlignRight, "QLineEdit {  font-family:" + self.policeQGroupBox  +";}" ]
        dicParamButton = dict(zip(_Listkeys, _ListValues))
        self.mod_Attrib4 = genereButtonsWithDict( dicParamButton )
        self.layoutAttributsModele.addWidget(self.mod_Lib_Attrib4, 3, 0, Qt.AlignTop)
        self.layoutAttributsModele.addWidget(self.mod_Attrib4    , 3, 1, Qt.AlignTop)
        # [ == attrib5 == ]
        mTextToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Attribut 5") 
        _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "toolTipWidget", "aligneWidget", "styleSheet", "wordWrap" ]
        _ListValues = [ QtWidgets.QLabel(), "Actif :", "modCat_Lib_Attrib3", mTextToolTip, Qt.AlignRight, "QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}", True ]
        dicParamLabel = dict(zip(_Listkeys, _ListValues))
        self.mod_Lib_Attrib5 = genereLabelWithDict( dicParamLabel )
        #-
        mTextToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Attribut 5") 
        _Listkeys   = [ "typeWidget", "textWidget", "nameWidget", "toolTipWidget", "aligneWidget", "styleSheet", "checked" ]
        _ListValues = [ QtWidgets.QCheckBox(), "", "modCat_Attrib3", mTextToolTip, Qt.AlignRight, "QLineEdit {  font-family:" + self.policeQGroupBox  +";}", True ]
        dicParamButton = dict(zip(_Listkeys, _ListValues))
        self.mod_Attrib5 = genereButtonsWithDict( dicParamButton )
        self.layoutAttributsModele.addWidget(self.mod_Lib_Attrib5, 4, 0, Qt.AlignTop)
        self.layoutAttributsModele.addWidget(self.mod_Attrib5    , 4, 1, Qt.AlignTop)

        #------
        #Button Add
        self.buttonAddModele = QtWidgets.QToolButton()
        self.buttonAddModele.setObjectName("buttonAddModele")
        self.buttonAddModele.setIcon(QIcon(os.path.dirname(__file__)+"\\icons\\general\\save.svg"))
        mbuttonAddToolTip = QtWidgets.QApplication.translate("ImportCSW_ui", "Add or modify a stored CSW. The URL and label will be saved in the “My CSW” section of the table above.", None)
        self.buttonAddModele.setToolTip(mbuttonAddToolTip)
        self.buttonAddModele.clicked.connect(lambda : self.functionAddModele())
        self.layoutAttributsModele.addWidget(self.buttonAddModele, 0, 2)
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
        #------ TEMPORAIRE 

        self.mTreeListeRessourceCategorie.affiche_CAT_IN_OUT("CAT_OUT", self.mTreeListeRessourceCategorie, self.mTreeListeRessourceCategorie, listeCatCol1, listeCatCol2)

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
        #------ TEMPORAIRE 

        self.mTreeListeRessourceOnglet.affiche_CAT_IN_OUT("CAT_OUT", self.mTreeListeRessourceOnglet, self.mTreeListeRessourceOnglet, listeCatCol1, listeCatCol2)

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
    def functionAddModele(self):
       zTitre = QtWidgets.QApplication.translate("CreateTemplate_ui", "PLUME : Warning", None)
       zMess  = QtWidgets.QApplication.translate("CreateTemplate_ui", "You must enter a URL of a CSW service.", None)
       if self.mZoneUrl.text() == "" or self.mZoneLibUrl.text() == "":
          bibli_plume.displayMess(self, (2 if self.Dialog.displayMessage else 1), zTitre, zMess, Qgis.Warning, self.Dialog.durationBarInfo)
       else :   
          self.mTreeCSW.ihmsPlumeAddCSW(self.Dialog , self.mZoneUrl.text(), self.mZoneLibUrl.text())
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

#========================================================     
#========================================================     
# Class pour le tree View Associaltion 
class TREEVIEWASSOCIATION(QTreeWidget):
    customMimeType = "text/plain"

    #===============================              
    def __init__(self, *args):
        QTreeWidget.__init__(self, *args)
        self.setColumnCount(2)
        self.setHeaderLabels(["Noms", "Commentaires"])
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.viewport().setAcceptDrops(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)  
        self.setSelectionMode(QAbstractItemView.SingleSelection	)  
        self.mnodeToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Right click to delete a Model / Categories association", None)         #Click droit pour supprimer une association Modèle / Catégories
        return

    #===============================              
    def startDrag(self, supportedActions):
        drag = QDrag(self)
        mimedata = self.model().mimeData(self.selectedIndexes())
        mimedata.setData(TREEVIEWASSOCIATION.customMimeType, QByteArray())
        drag.setMimeData(mimedata)
        drag.exec_(supportedActions)
        return
               
    #===============================              
    def afficheASSOCIATION(self, listeAssociationCol1, listeAssociationCol2):
        #---
        self.header().setStretchLastSection(False)
        self.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        i = 0
        while i in range(len(listeAssociationCol1)) :
            nodeUrlUser = QTreeWidgetItem(None, [ str(listeAssociationCol1[i]), str(listeAssociationCol2[i]) ])
            self.insertTopLevelItems( 0, [ nodeUrlUser ] )
            nodeUrlUser.setToolTip(0, "{}".format(self.mnodeToolTip))
            i += 1
 
        self.itemClicked.connect( self.ihmsPlumeASSOCIATION ) 
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect( self.menuContextuelPlumeASSOCIATION)
        self.expandAll()
        return

    #===============================              
    def update_csw(self, url_list, label_list, new_url, new_label) :
       if not new_url and not new_label:
           return None, None
       csw_index_from_url = url_list.index(new_url) if new_url and new_url in url_list else None
       csw_index_from_label = label_list.index(new_label) if new_label and new_label in label_list else None
       if csw_index_from_url is not None and csw_index_from_label is not None:
           # le libellé et l'URL sont déjà répertoriés, et pas pour le même CSW :
           # on ne garde qu'un CSW avec lesdits libellé et URL
           if csw_index_from_url != csw_index_from_label:
               del url_list[csw_index_from_label]
               del label_list[csw_index_from_label]
               csw_index_from_url = url_list.index(new_url)
               label_list[csw_index_from_url] = new_label
           # si le libellé et l'URL étaient déjà répertoriés pour le même CSW,
           # c'est que rien n'a été modifié, donc il n'y a rien à faire
       elif csw_index_from_url is not None:
           # l'URL est déjà répertoriée, on met à jour le libellé
           label_list[csw_index_from_url] = new_label
       elif csw_index_from_label is not None:
           # le libellé est déjà répertorié, on met à jour l'URL
           url_list[csw_index_from_label] = new_url
       else:
           # URL et libellé non répertoriés = nouveau CSW
           url_list.append(new_url)
           label_list.append(new_label)
       return url_list, label_list
        
    #===============================              
    def dragEnterEvent(self, event):    #//DEPART
        self.mDepart = ""
        selectedItems = self.selectedItems()
        if len(selectedItems) < 1:
            return
        mItemWidget    = selectedItems[0].text(1)
        mItemLibWidget = selectedItems[0].text(0)
        
        if event.mimeData().hasFormat('text/plain'):
           self.mDepart    = mItemWidget
           self.mDepartLib = mItemLibWidget
           if self.mDepart not in URLCSWDEFAUT.split(",") and self.mDepart not in LIBURLCSWDEFAUT.split(",") and self.mDepart != self.mLibNodeUrlDefaut and self.mDepart != self.mLibNodeUrlUser : 
              event.accept()
           else :   
              event.ignore()
        return

    #===============================              
    def dragMoveEvent(self, event):    #//EN COURS
        index = self.indexAt(event.pos())  
        try :
           r = self.itemFromIndex(index).text(1)
           if r == "" or r == None or r == self.mDepart : 
              event.ignore()
           elif r in URLCSWDEFAUT.split(",") or r in LIBURLCSWDEFAUT.split(",") or r == self.mLibNodeUrlDefaut or r == self.mLibNodeUrlUser : 
              event.ignore()
           else :
              event.accept()
        except :
           event.ignore()
        return

    #===============================              
    def dropEvent(self, event):  #//ARRIVEE
        index = self.indexAt(event.pos())
        r    = self.itemFromIndex(index).text(1)
        try :
           event.accept()
           #----
           current_item = self.currentItem()   #itemCourant
           self.nodeBlocsUser.removeChild(current_item) 
           #----
           mIndex = 0
           while mIndex < self.nodeBlocsUser.childCount() :
              if r == self.nodeBlocsUser.child(mIndex).text(1) :
                 nodeUrlUser = QTreeWidgetItem(None, [ str(self.mDepartLib), str(self.mDepart) ])
                 self.nodeBlocsUser.insertChild(mIndex, nodeUrlUser)
                 nodeUrlUser.setToolTip(0, "{}".format(self.mnodeUrlUserToolTip))
                 nodeUrlUser.setToolTip(1, "{}".format(self.mnodeUrlUserToolTip))
                 break
              mIndex += 1
           #----
        except :
           event.ignore()
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
        return # Lancer la mise à jour des tree catégories et des attributs
        mItemClicUrlCsw = item.data(1, Qt.DisplayRole)
        mItemClicLibUrlCsw = item.data(0, Qt.DisplayRole)
        self._mZoneUrl.setText(mItemClicUrlCsw if mItemClicUrlCsw != None else "")
        self._mZoneLibUrl.setText(mItemClicLibUrlCsw if mItemClicUrlCsw != None else "")
        self._mZoneUrlId.setText("")
        return

    #===============================              
    def ihmsPlumeDel(self): 
        current_item = self.currentItem()   #itemCourant
        self.takeTopLevelItem(self.indexOfTopLevelItem(current_item))
        return

    #===============================              
    def ihmsPlumeAddCSW(self, mDialog, mCsw, mLibCsw):
        #===============================              
        iterator = QTreeWidgetItemIterator(self)
        _mListCSW = []
        _mListLibCSW = []
        while iterator.value() :
           itemValueText = iterator.value().text(1)
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

#========================================================     
#========================================================     
# Class pour le tree View Catégories OUT 
class TREEVIEW_CAT_IN_OUT(QTreeWidget):
    customMimeType = "text/plain"

    #===============================              
    def __init__(self, *args):
        QTreeWidget.__init__(self, *args)
        self.setColumnCount(2)
        self.setHeaderLabels(["Noms", "Description"])  
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.viewport().setAcceptDrops(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setDefaultDropAction(Qt.MoveAction)  
        self.setSelectionMode(QAbstractItemView.SingleSelection	)  
        self.mnodeToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Right click to delete a Model / Categories association", None)         #Click droit pour supprimer une association Modèle / Catégories
        self.itemDoubleClicked.connect(self.moveDoubleClicked)
        return

    #===============================              
    def affiche_CAT_IN_OUT(self, mOrigine, self_Cat_Out, self_Cat_In, listeCatCol1, listeCatCol2):
        self.mOrigine     = mOrigine 
        self.self_Cat_Out = self_Cat_Out 
        self.self_Cat_In  = self_Cat_In 
        #---
        self.header().setStretchLastSection(False)
        self.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.nodeBlocsUser = self.topLevelItem( 0 )
        i = 0
        while i in range(len(listeCatCol1)) :
            nodeUrlUser = QTreeWidgetItem(None, [ str(listeCatCol1[i]), str(listeCatCol2[i]) ])
            #nodeUrlUser.setFlags(nodeUrlUser.flags() & ~Qt.ItemIsDropEnabled)
            self.insertTopLevelItems( 0, [ nodeUrlUser ] )
            nodeUrlUser.setToolTip(0, "{}".format(self.mnodeToolTip))
            i += 1
        return

    #===============================              
    def moveDoubleClicked(self, item, column):
        if item == None : return None
        #Remove
        current_item = self.currentItem()   #itemCourant
        self.takeTopLevelItem(self.indexOfTopLevelItem(item))

        if self.mOrigine == "CAT_OUT" :
           #Add
           pos = self.self_Cat_In.topLevelItemCount() if self.self_Cat_In.topLevelItemCount() != None else 0 
           self.self_Cat_In.insertTopLevelItem( pos, item )
        else :   
           #Add
           pos = self.self_Cat_Out.topLevelItemCount() if self.self_Cat_Out.topLevelItemCount() != None else 0 
           self.self_Cat_Out.insertTopLevelItem( pos, item )
        return
 
    #===============================              
    def dragMoveEvent(self, event):
        current_item = self.currentItem()
        item = self.itemAt(event.pos())
        event.accept() if item == None else event.ignore()
        return

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
# Class pour le tree View Associaltion 
class TREEVIEWMODELE(QTreeWidget):
    customMimeType = "text/plain"

    #===============================              
    def __init__(self, *args):
        QTreeWidget.__init__(self, *args)
        self.setColumnCount(2)
        self.setHeaderLabels(["Noms", "Commentaires"])
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.viewport().setAcceptDrops(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)  
        self.setSelectionMode(QAbstractItemView.SingleSelection	)  
        self.mnodeToolTip = QtWidgets.QApplication.translate("CreateTemplate_ui", "Right click to delete a Model", None)         #Click droit pour supprimer un Modèle
        return

    #===============================              
    def startDrag(self, supportedActions):
        drag = QDrag(self)
        mimedata = self.model().mimeData(self.selectedIndexes())
        mimedata.setData(TREEVIEWMODELE.customMimeType, QByteArray())
        drag.setMimeData(mimedata)
        drag.exec_(supportedActions)
        return
               
    #===============================              
    def afficheMODELE(self, listeModeleCol1, listeModeleCol2):
        #---
        self.header().setStretchLastSection(False)
        self.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        i = 0
        while i in range(len(listeModeleCol1)) :
            nodeUrlUser = QTreeWidgetItem(None, [ str(listeModeleCol1[i]), str(listeModeleCol2[i]) ])
            self.insertTopLevelItems( 0, [ nodeUrlUser ] )
            nodeUrlUser.setToolTip(0, "{}".format(self.mnodeToolTip))
            i += 1
 
        self.itemClicked.connect( self.ihmsPlumeMODELE ) 
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect( self.menuContextuelPlumeMODELE)
        self.expandAll()
        return

    #===============================              
    def update_csw(self, url_list, label_list, new_url, new_label) :
       if not new_url and not new_label:
           return None, None
       csw_index_from_url = url_list.index(new_url) if new_url and new_url in url_list else None
       csw_index_from_label = label_list.index(new_label) if new_label and new_label in label_list else None
       if csw_index_from_url is not None and csw_index_from_label is not None:
           # le libellé et l'URL sont déjà répertoriés, et pas pour le même CSW :
           # on ne garde qu'un CSW avec lesdits libellé et URL
           if csw_index_from_url != csw_index_from_label:
               del url_list[csw_index_from_label]
               del label_list[csw_index_from_label]
               csw_index_from_url = url_list.index(new_url)
               label_list[csw_index_from_url] = new_label
           # si le libellé et l'URL étaient déjà répertoriés pour le même CSW,
           # c'est que rien n'a été modifié, donc il n'y a rien à faire
       elif csw_index_from_url is not None:
           # l'URL est déjà répertoriée, on met à jour le libellé
           label_list[csw_index_from_url] = new_label
       elif csw_index_from_label is not None:
           # le libellé est déjà répertorié, on met à jour l'URL
           url_list[csw_index_from_label] = new_url
       else:
           # URL et libellé non répertoriés = nouveau CSW
           url_list.append(new_url)
           label_list.append(new_label)
       return url_list, label_list
        
    #===============================              
    def dragEnterEvent(self, event):    #//DEPART
        self.mDepart = ""
        selectedItems = self.selectedItems()
        if len(selectedItems) < 1:
            return
        mItemWidget    = selectedItems[0].text(1)
        mItemLibWidget = selectedItems[0].text(0)
        
        if event.mimeData().hasFormat('text/plain'):
           self.mDepart    = mItemWidget
           self.mDepartLib = mItemLibWidget
           if self.mDepart not in URLCSWDEFAUT.split(",") and self.mDepart not in LIBURLCSWDEFAUT.split(",") and self.mDepart != self.mLibNodeUrlDefaut and self.mDepart != self.mLibNodeUrlUser : 
              event.accept()
           else :   
              event.ignore()
        return

    #===============================              
    def dragMoveEvent(self, event):    #//EN COURS
        index = self.indexAt(event.pos())  
        try :
           r = self.itemFromIndex(index).text(1)
           if r == "" or r == None or r == self.mDepart : 
              event.ignore()
           elif r in URLCSWDEFAUT.split(",") or r in LIBURLCSWDEFAUT.split(",") or r == self.mLibNodeUrlDefaut or r == self.mLibNodeUrlUser : 
              event.ignore()
           else :
              event.accept()
        except :
           event.ignore()
        return

    #===============================              
    def dropEvent(self, event):  #//ARRIVEE
        index = self.indexAt(event.pos())
        r    = self.itemFromIndex(index).text(1)
        try :
           event.accept()
           #----
           current_item = self.currentItem()   #itemCourant
           self.nodeBlocsUser.removeChild(current_item) 
           #----
           mIndex = 0
           while mIndex < self.nodeBlocsUser.childCount() :
              if r == self.nodeBlocsUser.child(mIndex).text(1) :
                 nodeUrlUser = QTreeWidgetItem(None, [ str(self.mDepartLib), str(self.mDepart) ])
                 self.nodeBlocsUser.insertChild(mIndex, nodeUrlUser)
                 nodeUrlUser.setToolTip(0, "{}".format(self.mnodeUrlUserToolTip))
                 nodeUrlUser.setToolTip(1, "{}".format(self.mnodeUrlUserToolTip))
                 break
              mIndex += 1
           #----
        except :
           event.ignore()
        return
        
    #===============================              
    def menuContextuelPlumeMODELE(self, point):
        index = self.indexAt(point)
        if not index.isValid():
           return
        #-------
        if index.data(0) != None : 
           self.treeMenu = QMenu(self)
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
        return # Lancer la mise à jour des tree catégories et des attributs
        mItemClicUrlCsw = item.data(1, Qt.DisplayRole)
        mItemClicLibUrlCsw = item.data(0, Qt.DisplayRole)
        self._mZoneUrl.setText(mItemClicUrlCsw if mItemClicUrlCsw != None else "")
        self._mZoneLibUrl.setText(mItemClicLibUrlCsw if mItemClicUrlCsw != None else "")
        self._mZoneUrlId.setText("")
        return

    #===============================              
    def ihmsPlumeDel(self): 
        current_item = self.currentItem()   #itemCourant
        self.takeTopLevelItem(self.indexOfTopLevelItem(current_item))
        return

    #===============================              
    def ihmsPlumeAddCSW(self, mDialog, mCsw, mLibCsw):
        #===============================              
        iterator = QTreeWidgetItemIterator(self)
        _mListCSW = []
        _mListLibCSW = []
        while iterator.value() :
           itemValueText = iterator.value().text(1)
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
