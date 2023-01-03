# (c) Didier  LECLERC 2020 CMSIG MTE-MCTRCT/SG/SNUM/UNI/DRC Site de Rouen
# créé sept 2021

from . import bibli_plume
from .bibli_plume import *
import os.path
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qt import *
from qgis.gui import QgsDateTimeEdit, QgsOpacityWidget

from qgis.core import  QgsSettings

class Ui_Dialog_ColorBloc(object):
        
    def setupUiColorBloc(self, DialogColorBloc, mDialog):
        self.mDialog = mDialog
        self.DialogColorBloc = DialogColorBloc
        self.zMessTitle    =  QtWidgets.QApplication.translate("colorbloc_ui", "User settings / Customization of the IHM.", None)
        myPath = os.path.dirname(__file__)+"\\icons\\logo\\plume.svg"

        self.DialogColorBloc.setObjectName("DialogConfirme")
        self.DialogColorBloc.setFixedSize(900, 620)
        _pathIcons = os.path.dirname(__file__) + "/icons/logo"
        iconSource          = _pathIcons + "/plume.svg"
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(iconSource), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.DialogColorBloc.setWindowIcon(icon)
        #----------
        self.labelImage = QtWidgets.QLabel(self.DialogColorBloc)
        myDefPath = myPath.replace("\\","/")
        carIcon = QtGui.QImage(myDefPath)
        self.labelImage.setPixmap(QtGui.QPixmap.fromImage(carIcon))
        self.labelImage.setGeometry(QtCore.QRect(20, 0, 100, 100))
        self.labelImage.setObjectName("labelImage")
        #----------
        self.label_2 = QtWidgets.QLabel(self.DialogColorBloc)
        self.label_2.setGeometry(QtCore.QRect(100, 30, 430, 30))
        self.label_2.setAlignment(Qt.AlignLeft)        
        font = QtGui.QFont()
        font.setPointSize(12) 
        font.setWeight(50) 
        font.setBold(True)
        self.label_2.setFont(font)
        self.label_2.setTextFormat(QtCore.Qt.RichText)
        self.label_2.setObjectName("label_2")                                                     
        #========
        self.lScreenDialog, self.hScreenDialog = int(self.DialogColorBloc.width()), int(self.DialogColorBloc.height())
        #==========================              
        #Zone Onglets
        self.tabWidget = QTabWidget(self.DialogColorBloc)
        self.tabWidget.setObjectName("tabWidget")
        self.tabWidget.setGeometry(QtCore.QRect(10, 90, self.lScreenDialog -20 ,self.hScreenDialog - 160))
        self.tabWidget.setStyleSheet("QTabWidget::pane {border: 2px solid #958B62; } \
                                      QTabBar::tab {border: 1px solid #958B62; border-bottom-color: none;\
                                                    border-top-left-radius: 6px;border-top-right-radius: 6px;\
                                                    padding-left: 20px; padding-right: 20px;} \
                                      QTabBar::tab:selected {\
                                      background: qlineargradient(x1: 0, y1: 0, x2: 0.5, y2: 0.5, stop: 0 #958B62, stop: 1 white); } \
                                     ")
        #--------------------------
        self.tab_widget_General = QWidget()
        self.tab_widget_General.setObjectName("tab_widget_General")
        labelTab_General = QtWidgets.QApplication.translate("colorbloc_ui", "   General   ", None)
        self.tabWidget.addTab(self.tab_widget_General,labelTab_General)
        #-
        self.groupBox_tab_widget_General = QtWidgets.QGroupBox(self.tab_widget_General)
        self.groupBox_tab_widget_General.setGeometry(QtCore.QRect(10,10,self.tabWidget.width() - 20, self.tabWidget.height() - 40))
        self.groupBox_tab_widget_General.setObjectName("groupBox_tab_widget_General")
        self.groupBox_tab_widget_General.setStyleSheet("QGroupBox { border: 0px solid green }")
        #-
        self.layout_tab_widget_General = QtWidgets.QGridLayout()
        self.layout_tab_widget_General.setContentsMargins(0, 0, 0, 0)
        self.groupBox_tab_widget_General.setLayout(self.layout_tab_widget_General)
        x, y = 10,10
        larg, haut =  self.tabWidget.width()- 20, self.tabWidget.height()-40
        #--            
        scroll_bar_General = QtWidgets.QScrollArea(self.tab_widget_General) 
        scroll_bar_General.setStyleSheet("QScrollArea { border: 0px solid red;}")
        scroll_bar_General.setWidgetResizable(True)
        scroll_bar_General.setGeometry(QtCore.QRect(x, y, larg, haut))
        scroll_bar_General.setMinimumWidth(50)
        scroll_bar_General.setWidget(self.groupBox_tab_widget_General)
        #--------------------------
        self.tab_widget_Metadata = QWidget()
        self.tab_widget_Metadata.setObjectName("tab_widget_Metadata")
        labelTab_Metadata = QtWidgets.QApplication.translate("colorbloc_ui", "  Metadata sheets  ", None)
        self.tabWidget.addTab(self.tab_widget_Metadata,labelTab_Metadata)
        #-
        self.groupBox_tab_widget_Metadata = QtWidgets.QGroupBox(self.tab_widget_Metadata)
        self.groupBox_tab_widget_Metadata.setGeometry(QtCore.QRect(10,10,self.tabWidget.width() - 20, self.tabWidget.height() - 40))
        self.groupBox_tab_widget_Metadata.setObjectName("groupBox_tab_widget_Metadata")
        self.groupBox_tab_widget_Metadata.setStyleSheet("QGroupBox { border: 0px solid green }")
        #-
        self.layout_tab_widget_Metadata = QtWidgets.QGridLayout()
        self.layout_tab_widget_Metadata.setContentsMargins(0, 0, 0, 0)
        self.groupBox_tab_widget_Metadata.setLayout(self.layout_tab_widget_Metadata)
        x, y = 10,10
        larg, haut =  self.tabWidget.width()- 20, self.tabWidget.height()-40
        #--            
        scroll_bar_Metadata = QtWidgets.QScrollArea(self.tab_widget_Metadata) 
        scroll_bar_Metadata.setStyleSheet("QScrollArea { border: 0px solid red;}")
        scroll_bar_Metadata.setWidgetResizable(True)
        scroll_bar_Metadata.setGeometry(QtCore.QRect(x, y, larg, haut))
        scroll_bar_Metadata.setMinimumWidth(50)
        scroll_bar_Metadata.setWidget(self.groupBox_tab_widget_Metadata)
        #--------------------------
        self.tab_widget_Geometries = QWidget()
        self.tab_widget_Geometries.setObjectName("tab_widget_Geometriesr")
        labelTab_Geometries = QtWidgets.QApplication.translate("colorbloc_ui", "  Geometries  ", None)
        self.tabWidget.addTab(self.tab_widget_Geometries,labelTab_Geometries)
        #-
        self.groupBox_tab_widget_Geometries = QtWidgets.QGroupBox(self.tab_widget_Geometries)
        self.groupBox_tab_widget_Geometries.setGeometry(QtCore.QRect(10,10,self.tabWidget.width() - 20, self.tabWidget.height() - 40))
        self.groupBox_tab_widget_Geometries.setObjectName("groupBox_tab_widget_Geometries")
        self.groupBox_tab_widget_Geometries.setStyleSheet("QGroupBox { border: 0px solid green }")
        #-
        self.layout_tab_widget_Geometries = QtWidgets.QGridLayout()
        self.layout_tab_widget_Geometries.setContentsMargins(0, 0, 0, 0)
        self.groupBox_tab_widget_Geometries.setLayout(self.layout_tab_widget_Geometries)
        x, y = 10,10
        larg, haut =  self.tabWidget.width()- 20, self.tabWidget.height()-40
        #--            
        scroll_bar_Geometries = QtWidgets.QScrollArea(self.tab_widget_Geometries) 
        scroll_bar_Geometries.setStyleSheet("QScrollArea { border: 0px solid red;}")
        scroll_bar_Geometries.setWidgetResizable(True)
        scroll_bar_Geometries.setGeometry(QtCore.QRect(x, y, larg, haut))
        scroll_bar_Geometries.setMinimumWidth(50)
        scroll_bar_Geometries.setWidget(self.groupBox_tab_widget_Geometries)
        #--------------------------
        self.tab_widget_Explorer = QWidget()
        self.tab_widget_Explorer.setObjectName("tab_widget_Explorer")
        labelTab_Explorer = QtWidgets.QApplication.translate("colorbloc_ui", "  Explorer  ", None)
        self.tabWidget.addTab(self.tab_widget_Explorer,labelTab_Explorer)
        #-
        self.groupBox_tab_widget_Explorer = QtWidgets.QGroupBox(self.tab_widget_Explorer)
        self.groupBox_tab_widget_Explorer.setGeometry(QtCore.QRect(10,10,self.tabWidget.width() - 20, self.tabWidget.height() - 40))
        self.groupBox_tab_widget_Explorer.setObjectName("groupBox_tab_widget_Explorer")
        self.groupBox_tab_widget_Explorer.setStyleSheet("QGroupBox { border: 0px solid green }")
        #-
        self.layout_tab_widget_Explorer = QtWidgets.QGridLayout()
        self.layout_tab_widget_Explorer.setContentsMargins(0, 0, 0, 0)
        self.groupBox_tab_widget_Explorer.setLayout(self.layout_tab_widget_Explorer)
        x, y = 10,10
        larg, haut =  self.tabWidget.width()- 20, self.tabWidget.height()-40
        #--            
        scroll_bar_Explorer = QtWidgets.QScrollArea(self.tab_widget_Explorer) 
        scroll_bar_Explorer.setStyleSheet("QScrollArea { border: 0px solid red;}")
        scroll_bar_Explorer.setWidgetResizable(True)
        scroll_bar_Explorer.setGeometry(QtCore.QRect(x, y, larg, haut))
        scroll_bar_Explorer.setMinimumWidth(50)
        scroll_bar_Explorer.setWidget(self.groupBox_tab_widget_Explorer)
        #--------------------------
        self.tab_widget_Advanced = QWidget()
        self.tab_widget_Advanced.setObjectName("tab_widget_Advanced")
        labelTab_Advanced = QtWidgets.QApplication.translate("colorbloc_ui", "  Advanced  ", None)
        self.tabWidget.addTab(self.tab_widget_Advanced,labelTab_Advanced)
        #-
        self.groupBox_tab_widget_Advanced = QtWidgets.QGroupBox(self.tab_widget_Advanced)
        self.groupBox_tab_widget_Advanced.setGeometry(QtCore.QRect(10,10,self.tabWidget.width() - 20, self.tabWidget.height() - 40))
        self.groupBox_tab_widget_Advanced.setObjectName("groupBox_tab_widget_Advanced")
        self.groupBox_tab_widget_Advanced.setStyleSheet("QGroupBox { border: 0px solid green }")
        #-
        self.layout_tab_widget_Advanced = QtWidgets.QGridLayout()
        self.layout_tab_widget_Advanced.setContentsMargins(0, 0, 0, 0)
        self.groupBox_tab_widget_Advanced.setLayout(self.layout_tab_widget_Advanced)
        x, y = 10,10
        larg, haut =  self.tabWidget.width()- 20, self.tabWidget.height()-40
        #--            
        scroll_bar_Advanced = QtWidgets.QScrollArea(self.tab_widget_Advanced) 
        scroll_bar_Advanced.setStyleSheet("QScrollArea { border: 0px solid red;}")
        scroll_bar_Advanced.setWidgetResizable(True)
        scroll_bar_Advanced.setGeometry(QtCore.QRect(x, y, larg, haut))
        scroll_bar_Advanced.setMinimumWidth(50)
        scroll_bar_Advanced.setWidget(self.groupBox_tab_widget_Advanced)
        #Zone Onglets
        #==========================              

        #========
        self.mDic_LH = bibli_plume.returnAndSaveDialogParam(self, "Load")
        self.dicListLettre      = { 0:"QTabWidget", 1:"QGroupBox",  2:"QGroupBoxGroupOfProperties",  3:"QGroupBoxGroupOfValues",  4:"QGroupBoxTranslationGroup", 5:"QLabelBackGround", 6:"geomColor", 7:"activeTooltipColorText", 8:"activeTooltipColorBackground", 9:"opacity"}
        self.dicListLettreLabel = { 0:QtWidgets.QApplication.translate("colorbloc_ui", "Tab"),\
                                    1:QtWidgets.QApplication.translate("colorbloc_ui", "General group"),\
                                    2:QtWidgets.QApplication.translate("colorbloc_ui", "Property group"),\
                                    3:QtWidgets.QApplication.translate("colorbloc_ui", "Value group"),\
                                    4:QtWidgets.QApplication.translate("colorbloc_ui", "Translation group"),\
                                    5:QtWidgets.QApplication.translate("colorbloc_ui", "Wording"),\
                                    6:QtWidgets.QApplication.translate("colorbloc_ui", "Geometry tools color"),\
                                    7:QtWidgets.QApplication.translate("colorbloc_ui", "Text color"),\
                                    8:QtWidgets.QApplication.translate("colorbloc_ui", "Background color"),\
                                    9:QtWidgets.QApplication.translate("colorbloc_ui", "Opacity")\
                                    }
        #-
        self.editStyle        = self.mDic_LH["QEdit"]              #style saisie
        self.labelBackGround  = self.mDic_LH["QLabelBackGround"] #QLabel    
        self.epaiQGroupBox    = self.mDic_LH["QGroupBoxEpaisseur"] #épaisseur QGroupBox
        self.lineQGroupBox    = self.mDic_LH["QGroupBoxLine"]    #trait QGroupBox
        self.policeQGroupBox  = self.mDic_LH["QGroupBoxPolice"]  #Police QGroupBox
        self.policeQTabWidget = self.mDic_LH["QTabWidgetPolice"] #Police QTabWidget
        self.ihm              = self.mDic_LH["ihm"]              #window/dock
        self.opacityValue     = self.mDic_LH["opacityValue"]     #valeur pour l'opacité
        self.activeZoneNonSaisie  = True   if self.mDic_LH["activeZoneNonSaisie"]     == "true" else False
        #-
        self.zEditStyle = self.editStyle  # si ouverture sans chgt et sauve
        # liste des Paramétres UTILISATEURS
        bibli_plume.listUserParam(self)
        # liste des Paramétres UTILISATEURS
        #========
        # Onglets GENERAL
        self.groupBoxGeneral = QtWidgets.QGroupBox()
        self.groupBoxGeneral.setObjectName("groupBoxGeneral")
        self.groupBoxGeneral.setStyleSheet("QGroupBox { border: 0px solid red }")
        #-
        self.layoutGeneral = QtWidgets.QGridLayout()
        self.layoutGeneral.setContentsMargins(0, 0, 0, 0)
        self.layoutGeneral.setColumnStretch(0, 2)
        self.layoutGeneral.setColumnStretch(1, 1)
        self.layoutGeneral.setColumnStretch(2, 2)
        self.groupBoxGeneral.setLayout(self.layoutGeneral)
        self.layout_tab_widget_General.addWidget(self.groupBoxGeneral, 0, 0, Qt.AlignTop)
        #-
        self.labelWinVsDock = QtWidgets.QLabel()
        self.labelWinVsDock.setText(QtWidgets.QApplication.translate("colorbloc_ui", "Interface"))
        self.labelWinVsDock.setAlignment(Qt.AlignRight)        
        self.labelWinVsDock.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        self.labelWinVsDock.setWordWrap(True)
        self.layoutGeneral.addWidget(self.labelWinVsDock, 0, 0, Qt.AlignTop)
        #-
        mDicWinVsDock = {"window":"Fenêtre", "dockFalse":"Panneau ancré", "dockTrue":"Panneau flottant"}
        self.comboWinVsDock = QtWidgets.QComboBox()
        self.comboWinVsDock.setObjectName("comboWinVsDock")
        self.comboWinVsDock.addItems([ elem for elem in mDicWinVsDock.values() ])
        self.comboWinVsDock.setCurrentText(mDicWinVsDock[self.ihm])         
        self.comboWinVsDock.currentTextChanged.connect(lambda : self.functionWinVsDock(mDicWinVsDock))
        mValueTemp = [ k for k, v in mDicWinVsDock.items() if v == self.comboWinVsDock.currentText()][0]
        self.zComboWinVsDock = mValueTemp  # si ouverture sans chgt et sauve
        self.layoutGeneral.addWidget(self.comboWinVsDock, 0, 1, Qt.AlignTop)
        #-
        self.labelQGroupBox = QtWidgets.QLabel()
        self.labelQGroupBox.setAlignment(Qt.AlignRight)        
        self.labelQGroupBox.setText(QtWidgets.QApplication.translate("colorbloc_ui", "Police :"))        
        self.labelQGroupBox.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        self.labelQGroupBox.setWordWrap(True)
        self.layoutGeneral.addWidget(self.labelQGroupBox, 1, 0, Qt.AlignTop)
        #-
        self.fontQGroupBox = QtWidgets.QFontComboBox()
        self.fontQGroupBox.setObjectName("fontComboBox")         
        self.fontQGroupBox.setCurrentFont(QFont(self.policeQGroupBox))         
        self.fontQGroupBox.currentFontChanged.connect(self.functionFont)
        self.zFontQGroupBox = self.policeQGroupBox  # si ouverture sans chgt et sauve
        self.layoutGeneral.addWidget(self.fontQGroupBox, 1, 1, Qt.AlignTop)
        #------ Affiche message box pour confirmation 
        mLabelConfirmMessageText    = QtWidgets.QApplication.translate("colorbloc_ui", "ConfirmeMessage", None)
        mLabelConfirmMessageToolTip = QtWidgets.QApplication.translate("colorbloc_ui", "ConfirmeMessageToolTip", None)
        mLabelConfirmMessage = QtWidgets.QLabel()
        mLabelConfirmMessage.setObjectName("mLabelConfirmMessage")
        mLabelConfirmMessage.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        mLabelConfirmMessage.setText(mLabelConfirmMessageText)
        mLabelConfirmMessage.setToolTip(mLabelConfirmMessageToolTip)
        mLabelConfirmMessage.setWordWrap(True)
        mLabelConfirmMessage.setAlignment(Qt.AlignRight)        
        mLabelConfirmMessage.setWordWrap(True)
        self.layoutGeneral.addWidget(mLabelConfirmMessage, 2, 0, Qt.AlignTop)
        #- 
        mZoneConfirmMessage = QtWidgets.QCheckBox()
        mZoneConfirmMessage.setStyleSheet("QCheckBox {  font-family:" + self.policeQGroupBox  +";}")
        mZoneConfirmMessage.setObjectName("mZoneConfirmMessage")
        mZoneConfirmMessage.setChecked(True if self.zoneConfirmMessage else False)
        mZoneConfirmMessage.setToolTip(mLabelConfirmMessageToolTip)
        self.layoutGeneral.addWidget(mZoneConfirmMessage, 2, 1, Qt.AlignTop)
        #- 
        self.mZoneConfirmMessage = mZoneConfirmMessage 
        # Onglets GENERAL  
        #========
        #========
        # Onglets METADATA  
        self.groupBoxMetadata = QtWidgets.QGroupBox()
        self.groupBoxMetadata.setObjectName("groupBoxMetadata")
        self.groupBoxMetadata.setStyleSheet("QGroupBox { border: 0px solid red }")
        #-
        self.layoutMetadata = QtWidgets.QGridLayout()
        self.layoutMetadata.setContentsMargins(0, 0, 0, 0)
        self.layoutMetadata.setColumnStretch(0, 1)
        self.layoutMetadata.setColumnStretch(1, 1)
        self.layoutMetadata.setColumnStretch(2, 1)
        self.groupBoxMetadata.setLayout(self.layoutMetadata)
        self.layout_tab_widget_Metadata.addWidget(self.groupBoxMetadata, 0, 0, Qt.AlignTop)
        #-
        self.groupBoxWysiwig = QtWidgets.QGroupBox()
        self.groupBoxWysiwig.setObjectName("groupBoxWysiwig")
        self.groupBoxWysiwig.setStyleSheet("QGroupBox { border: 0px solid blue }")
        #-
        self.layoutWysiwig = QtWidgets.QGridLayout()
        self.layoutWysiwig.setContentsMargins(0, 0, 0, 0)
        self.groupBoxWysiwig.setLayout(self.layoutWysiwig)
        self.layout_tab_widget_Metadata.addWidget(self.groupBoxWysiwig, 0, 1)
        #-

        layout, button_0, img_0, reset_0 = self.layoutMetadata, QtWidgets.QPushButton(), QtWidgets.QLabel(), QtWidgets.QPushButton()
        self.button_0, self.reset_0 = button_0, reset_0
        self.genereButtonActionColor(layout, button_0, img_0, reset_0, "button_0", "img_0", "reset_0", 0)
        #-
        layout, button_2, img_2, reset_2 = self.layoutMetadata, QtWidgets.QPushButton(), QtWidgets.QLabel(), QtWidgets.QPushButton()
        self.button_2, self.reset_2 = button_2, reset_2
        self.genereButtonActionColor(layout, button_2, img_2, reset_2, "button_2", "img_2", "reset_2", 2)
        #-
        layout, button_3, img_3, reset_3 = self.layoutMetadata, QtWidgets.QPushButton(), QtWidgets.QLabel(), QtWidgets.QPushButton()
        self.button_3, self.reset_3 = button_3, reset_3
        self.genereButtonActionColor(layout, button_3, img_3, reset_3, "button_3", "img_3", "reset_3", 3)
        #-
        layout, button_4, img_4, reset_4 = self.layoutMetadata, QtWidgets.QPushButton(), QtWidgets.QLabel(), QtWidgets.QPushButton()
        self.button_4, self.reset_4 = button_4, reset_4
        self.genereButtonActionColor(layout, button_4, img_4, reset_4, "button_4", "img_4", "reset_4", 4)
        #-
        layout, button_5, img_5, reset_5 = self.layoutMetadata, QtWidgets.QPushButton(), QtWidgets.QLabel(), QtWidgets.QPushButton()
        self.button_5, self.reset_5 = button_5, reset_5
        self.genereButtonActionColor(layout, button_5, img_5, reset_5, "button_5", "img_5", "reset_5", 5)
        #-
        self.labelBlank = QtWidgets.QLabel()
        self.labelBlank.setText("")         
        self.layoutMetadata.addWidget(self.labelBlank, 6, 0, Qt.AlignTop)
        #--
        mDicType = {"dashed":"Tirets", "dotted":"Pointillés", "double":"Plein double", "solid":"plein"}
        self.labelTypeLine = QtWidgets.QLabel()
        self.labelTypeLine.setAlignment(Qt.AlignRight)        
        self.labelTypeLine.setText(QtWidgets.QApplication.translate("colorbloc_ui", "Line type of frames :"))         
        self.labelTypeLine.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        self.labelTypeLine.setWordWrap(True)
        self.layoutMetadata.addWidget(self.labelTypeLine, 7, 0, Qt.AlignTop)
        #--
        self.comboTypeLine = QtWidgets.QComboBox()
        self.comboTypeLine.setObjectName("groupBoxBar")
        self.comboTypeLine.addItems([ elem for elem in mDicType.values() ])
        self.comboTypeLine.setCurrentText(mDicType[self.lineQGroupBox])         
        self.comboTypeLine.currentTextChanged.connect(lambda : self.functionLine(mDicType))
        self.layoutMetadata.addWidget(self.comboTypeLine, 7, 1, Qt.AlignTop)
        self.zLineQGroupBox = self.lineQGroupBox  # si ouverture sans chgt et sauve
        #-
        self.labelBoxEpai = QtWidgets.QLabel()
        self.labelBoxEpai.setAlignment(Qt.AlignRight)        
        self.labelBoxEpai.setText(QtWidgets.QApplication.translate("colorbloc_ui", "Frame line thickness :"))         
        self.labelBoxEpai.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        self.labelBoxEpai.setWordWrap(True)
        self.layoutMetadata.addWidget(self.labelBoxEpai, 8, 0, Qt.AlignTop)
        #-
        self.spinBoxEpai = QtWidgets.QDoubleSpinBox()
        self.spinBoxEpai.setMaximum(5)
        self.spinBoxEpai.setMinimum(0)
        self.spinBoxEpai.setValue(1)
        self.spinBoxEpai.setSingleStep(1)
        self.spinBoxEpai.setDecimals(0)
        self.spinBoxEpai.setSuffix(" px")
        self.spinBoxEpai.setObjectName("spinBoxEpai")
        self.spinBoxEpai.setValue(float(self.epaiQGroupBox))         
        self.spinBoxEpai.valueChanged.connect(self.functionEpai)
        self.layoutMetadata.addWidget(self.spinBoxEpai, 8, 1, Qt.AlignTop)
        self.zEpaiQGroupBox = self.epaiQGroupBox  # si ouverture sans chgt et sauve
        #- Début Opacité
        self.groupBoxStretch = QtWidgets.QGroupBox()
        self.groupBoxStretch.setObjectName("groupBoxStretch")
        self.groupBoxStretch.setStyleSheet("QGroupBox { border: 0px solid red }")
        self.layoutMetadata.addWidget(self.groupBoxStretch, 9, 0)

        #------ Gestion zones non saisies 
        mLabelZoneNonSaisieText    = QtWidgets.QApplication.translate("colorbloc_ui", "Visualization of non-entered zones.", None)
        mLabelZoneNonSaisieToolTip = QtWidgets.QApplication.translate("colorbloc_ui", "Use the mechanism for viewing unentered areas in edit mode.", None)
        mLabelZoneNonSaisie = QtWidgets.QLabel()
        mLabelZoneNonSaisie.setObjectName("mLabelZoneNonSaisie")
        mLabelZoneNonSaisie.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        mLabelZoneNonSaisie.setText(mLabelZoneNonSaisieText)
        mLabelZoneNonSaisie.setToolTip(mLabelZoneNonSaisieToolTip)
        mLabelZoneNonSaisie.setWordWrap(True)
        mLabelZoneNonSaisie.setAlignment(Qt.AlignRight)        
        mLabelZoneNonSaisie.setWordWrap(True)
        self.layoutMetadata.addWidget(mLabelZoneNonSaisie, 10, 0, Qt.AlignTop)
        #- 
        self.mZoneZoneNonSaisie = QtWidgets.QCheckBox()
        self.mZoneZoneNonSaisie.setStyleSheet("QCheckBox {  font-family:" + self.policeQGroupBox  +";}")
        self.mZoneZoneNonSaisie.setObjectName("mZoneZoneNonSaisie")
        self.mZoneZoneNonSaisie.setChecked(self.activeZoneNonSaisie)
        self.mZoneZoneNonSaisie.setToolTip(mLabelZoneNonSaisieToolTip)
        self.activeZoneNonSaisie = True if self.mZoneZoneNonSaisie.isChecked() else False  # si ouverture sans chgt et sauve
        self.mZoneZoneNonSaisie.toggled.connect(lambda : self.functionTooltip("activeZoneNonSaisie"))       
        self.layoutMetadata.addWidget(self.mZoneZoneNonSaisie, 10, 1, Qt.AlignTop)
        #------ Gestion zones non saisies 

        layout, button_9, img_9, reset_9 = self.layoutMetadata, QtWidgets.QPushButton(), QtWidgets.QLabel(), QtWidgets.QPushButton()
        self.button_9, self.reset_9 = button_9, reset_9
        self.genereButtonActionColor(layout, button_9, img_9, reset_9, "button_9", "img_9", "reset_9", 9)
        #.
        self.labelOpacity = QtWidgets.QLineEdit()
        self.labelOpacity.setAlignment(Qt.AlignRight)    
        self.labelOpacity.setPlaceholderText(QtWidgets.QApplication.translate("colorbloc_ui", "Zone sans valeur."))  
        self.labelOpacity.setStyleSheet("QLineEdit {  font-family:" + self.policeQGroupBox  +"; background-color:" + str( self.mDic_LH[self.dicListLettre[9]] )  +";}")
        self.labelOpacity.setAlignment(Qt.AlignLeft)        
        self.layoutMetadata.addWidget(self.labelOpacity, 13, 0, 1, 3, Qt.AlignTop)
        # création Effect opacité
        self.opacityEffect = QGraphicsOpacityEffect()
        # coeff d'opacité
        self.opacityEffect.setOpacity(float(self.mDic_LH["opacityValue"]))
        # adding opacity effect to the label
        self.labelOpacity.setGraphicsEffect(self.opacityEffect)
        #.
        self.comboOpacity = QgsOpacityWidget()
        self.comboOpacity.setObjectName("comboOpacity")         
        self.comboOpacity.setOpacity(float(self.mDic_LH["opacityValue"]))
        #Event
        self.comboOpacity.opacityChanged.connect(self.onValueChangedOpacity)
        self.layoutMetadata.addWidget(self.comboOpacity, 14, 0, 1, 3, Qt.AlignTop)
        #- Fin Opacité
        self.functionTooltip("activeZoneNonSaisie")
        #-
        # Onglets METADATA  
        #========
        #========
        # Onglets GEOMETRIES
        self.groupBoxGeometries = QtWidgets.QGroupBox()
        self.groupBoxGeometries.setObjectName("groupBoxGeometries")
        self.groupBoxGeometries.setStyleSheet("QGroupBox { border: 0px solid red }")
        #-
        self.layoutGeometries = QtWidgets.QGridLayout()
        self.layoutGeometries.setContentsMargins(0, 0, 0, 0)
        self.layoutGeometries.setColumnStretch(0, 1)
        self.layoutGeometries.setColumnStretch(1, 1)
        self.layoutGeometries.setColumnStretch(2, 1)
        self.layoutGeometries.setColumnStretch(3, 1)
        self.layoutGeometries.setColumnStretch(4, 1)
        self.layoutGeometries.setColumnStretch(5, 1)
        self.layoutGeometries.setColumnStretch(6, 1)
        self.layoutGeometries.setColumnStretch(7, 1)
        self.layoutGeometries.setColumnStretch(8, 4)
        self.groupBoxGeometries.setLayout(self.layoutGeometries)
        self.layout_tab_widget_Geometries.addWidget(self.groupBoxGeometries, 0, 0, Qt.AlignTop)
        #-
        self.geomPrecision   = self.mDic_LH["geomPrecision"]       
        self.geomEpaisseur   = self.mDic_LH["geomEpaisseur"]       
        self.geomPoint       = self.mDic_LH["geomPoint"]       
        self.geomPointEpaisseur = self.mDic_LH["geomPointEpaisseur"]       
        self.geomZoom        = True if self.mDic_LH["geomZoom"] == "true" else False
        #-
        #========
        self.labelgeomPrecision = QtWidgets.QLabel()
        self.labelgeomPrecision.setAlignment(Qt.AlignRight)        
        self.labelgeomPrecision.setText(QtWidgets.QApplication.translate("colorbloc_ui", "Coordinate accuracy. WKT :"))         
        self.labelgeomPrecision.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        self.labelgeomPrecision.setWordWrap(True)
        self.layoutGeometries.addWidget(self.labelgeomPrecision, 0, 0, 1, 4,Qt.AlignTop)
        #-
        self.spingeomPrecision = QtWidgets.QDoubleSpinBox()
        self.spingeomPrecision.setMaximum(17)
        self.spingeomPrecision.setMinimum(0)
        self.spingeomPrecision.setSingleStep(1)
        self.spingeomPrecision.setDecimals(0)
        self.spingeomPrecision.setSuffix(" déci")
        self.spingeomPrecision.setObjectName("spingeomPrecision")
        self.spingeomPrecision.setValue(int(self.geomPrecision))         
        self.spingeomPrecision.valueChanged.connect(self.functiongeomPrecision)
        self.geomPrecision = self.spingeomPrecision.value()  # si ouverture sans chgt et sauve
        self.layoutGeometries.addWidget(self.spingeomPrecision, 0, 4, Qt.AlignTop)
        #-
        self.labelgeomEpaisseur = QtWidgets.QLabel()
        self.labelgeomEpaisseur.setAlignment(Qt.AlignRight)        
        self.labelgeomEpaisseur.setText(QtWidgets.QApplication.translate("colorbloc_ui", "Geometry tool thickness :"))        
        self.labelgeomEpaisseur.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        self.labelgeomEpaisseur.setWordWrap(True)
        self.layoutGeometries.addWidget(self.labelgeomEpaisseur, 1, 0, 1, 4, Qt.AlignTop)
        #-
        self.spingeomEpaisseur = QtWidgets.QDoubleSpinBox()
        self.spingeomEpaisseur.setMaximum(10)
        self.spingeomEpaisseur.setMinimum(0)
        self.spingeomEpaisseur.setValue(1)
        self.spingeomEpaisseur.setSingleStep(1)
        self.spingeomEpaisseur.setDecimals(0)
        self.spingeomEpaisseur.setSuffix(" px")
        self.spingeomEpaisseur.setObjectName("spingeomEpaisseur")
        self.spingeomEpaisseur.setValue(int(self.geomEpaisseur))         
        self.spingeomEpaisseur.valueChanged.connect(self.functiongeomEpaisseur)
        self.geomEpaisseur = self.spingeomEpaisseur.value()  # si ouverture sans chgt et sauve
        self.layoutGeometries.addWidget(self.spingeomEpaisseur, 1, 4, Qt.AlignTop)
        #--
        mDicTypeCle      = ["ICON_CROSS", "ICON_X", "ICON_BOX", "ICON_CIRCLE", "ICON_FULL_BOX" , "ICON_DIAMOND" , "ICON_FULL_DIAMOND"]
        mDicTypeObj      = [QgsRubberBand.ICON_X, QgsRubberBand.ICON_CROSS, QgsRubberBand.ICON_BOX, QgsRubberBand.ICON_CIRCLE, QgsRubberBand.ICON_FULL_BOX, QgsRubberBand.ICON_DIAMOND, QgsRubberBand.ICON_FULL_DIAMOND]
        self.mDialog.mDicTypeObj = dict(zip(mDicTypeCle, mDicTypeObj)) # For bibli_plume_tools_map

        mDicTypeCle = [ elem.lower().capitalize() for elem in mDicTypeCle ]
        self.labelTypegeomPoint = QtWidgets.QLabel()
        self.labelTypegeomPoint.setAlignment(Qt.AlignRight)        
        self.labelTypegeomPoint.setText(QtWidgets.QApplication.translate("colorbloc_ui", "POINT geometry symbol :"))         
        self.labelTypegeomPoint.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        self.labelTypegeomPoint.setWordWrap(True)
        self.layoutGeometries.addWidget(self.labelTypegeomPoint, 2, 0, 1, 4, Qt.AlignTop)
        #--
        self.comboTypegeomPoint = QtWidgets.QComboBox()
        self.comboTypegeomPoint.setObjectName("comboTypegeomPoint")
        self.comboTypegeomPoint.addItems( mDicTypeCle )
        self.comboTypegeomPoint.currentTextChanged.connect(self.functioncomboTypegeomPoint)
        self.comboTypegeomPoint.setCurrentText(self.geomPoint.lower().capitalize())         
        self.geomPoint = self.comboTypegeomPoint.currentText().upper()  # si ouverture sans chgt et sauve
        self.layoutGeometries.addWidget(self.comboTypegeomPoint, 2, 4, Qt.AlignTop)
        #-
        self.labelgeomPointEpaisseur = QtWidgets.QLabel()
        self.labelgeomPointEpaisseur.setAlignment(Qt.AlignRight)        
        self.labelgeomPointEpaisseur.setText(QtWidgets.QApplication.translate("colorbloc_ui", "POINT geometry size :"))         
        self.labelgeomPointEpaisseur.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        self.labelgeomPointEpaisseur.setWordWrap(True)
        self.layoutGeometries.addWidget(self.labelgeomPointEpaisseur, 3, 0, 1, 4, Qt.AlignTop)
        #-
        self.spingeomPointEpaisseur = QtWidgets.QDoubleSpinBox()
        self.spingeomPointEpaisseur.setMaximum(20)
        self.spingeomPointEpaisseur.setMinimum(0)
        self.spingeomPointEpaisseur.setValue(1)
        self.spingeomPointEpaisseur.setSingleStep(1)
        self.spingeomPointEpaisseur.setDecimals(0)
        self.spingeomPointEpaisseur.setSuffix(" px")
        self.spingeomPointEpaisseur.setObjectName("spingeomPointEpaisseur")
        self.spingeomPointEpaisseur.setValue(int(self.geomPointEpaisseur))         
        self.spingeomPointEpaisseur.valueChanged.connect(self.functiongeomPointEpaisseur)
        self.geomPointEpaisseur = self.spingeomPointEpaisseur.value()  # si ouverture sans chgt et sauve
        self.layoutGeometries.addWidget(self.spingeomPointEpaisseur, 3, 4, Qt.AlignTop)
        #--
        self.labelgeomZoom = QtWidgets.QLabel()
        self.labelgeomZoom.setAlignment(Qt.AlignRight)        
        self.labelgeomZoom.setText(QtWidgets.QApplication.translate("colorbloc_ui", "Zoom on the geometric visualization :"))         
        self.labelgeomZoom.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        self.labelgeomZoom.setWordWrap(True)
        self.layoutGeometries.addWidget(self.labelgeomZoom, 4, 0, 1, 4, Qt.AlignTop)
        #--
        self.QCheckgeomZoom = QtWidgets.QCheckBox()
        self.QCheckgeomZoom.setObjectName("QCheckgeomZoom")
        self.QCheckgeomZoom.setChecked(self.geomZoom)  
        self.QCheckgeomZoom.toggled.connect(self.functiongeomZoom)       
        self.geomZoom = True if self.QCheckgeomZoom.isChecked() else False  # si ouverture sans chgt et sauve
        self.layoutGeometries.addWidget(self.QCheckgeomZoom, 4, 4, Qt.AlignTop)
        #--
        layout, button_6, img_6, reset_6 = self.layoutGeometries, QtWidgets.QPushButton(), QtWidgets.QLabel(), QtWidgets.QPushButton()
        self.genereButtonActionColor(layout, button_6, img_6, reset_6, "button_6", "img_6", "reset_6", 6)
        # Onglets GEOMETRIES
        #========
        #========
        # Onglets EXPLORER
        self.groupBoxExplorer = QtWidgets.QGroupBox()
        self.groupBoxExplorer.setObjectName("groupBoxExplorer")
        self.groupBoxExplorer.setStyleSheet("QGroupBox { border: 0px solid red }")
        #-
        self.layoutExplorer = QtWidgets.QGridLayout()
        self.layoutExplorer.setContentsMargins(0, 0, 0, 0)
        self.layoutExplorer.setColumnStretch(0, 1)
        self.layoutExplorer.setColumnStretch(1, 1)
        self.layoutExplorer.setColumnStretch(2, 1)
        self.layoutExplorer.setColumnStretch(3, 1)
        self.layoutExplorer.setColumnStretch(4, 1)
        self.layoutExplorer.setColumnStretch(5, 1)
        self.layoutExplorer.setColumnStretch(6, 1)
        self.layoutExplorer.setColumnStretch(7, 1)
        self.layoutExplorer.setColumnStretch(8, 4)
        self.groupBoxExplorer.setLayout(self.layoutExplorer)
        self.layout_tab_widget_Explorer.addWidget(self.groupBoxExplorer, 0, 0, Qt.AlignTop)
        #-  
        self.activeTooltip           = True   if self.mDic_LH["activeTooltip"]           == "true" else False
        self.activeTooltipWithtitle  = True   if self.mDic_LH["activeTooltipWithtitle"]  == "true" else False
        self.activeTooltipLogo       = True   if self.mDic_LH["activeTooltipLogo"]       == "true" else False
        self.activeTooltipCadre      = True   if self.mDic_LH["activeTooltipCadre"]      == "true" else False
        self.activeTooltipColor      = True   if self.mDic_LH["activeTooltipColor"]      == "true" else False
        self.activeTooltipColorText       = self.mDic_LH["activeTooltipColorText"] 
        self.activeTooltipColorBackground = self.mDic_LH["activeTooltipColorBackground"] 
        #--
        self.labelActivetooltip = QtWidgets.QLabel()
        self.labelActivetooltip.setAlignment(Qt.AlignRight)        
        self.labelActivetooltip.setText(QtWidgets.QApplication.translate("colorbloc_ui", "Modified tooltip :"))         
        self.labelActivetooltip.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        self.labelActivetooltip.setWordWrap(True)
        self.layoutExplorer.addWidget(self.labelActivetooltip, 0, 0, 1, 4, Qt.AlignTop)
        #--
        self.QChecklabelActivetooltip = QtWidgets.QCheckBox()
        self.QChecklabelActivetooltip.setObjectName("QChecklabelActivetooltip")
        self.QChecklabelActivetooltip.setChecked(self.activeTooltip)  
        self.QChecklabelActivetooltip.toggled.connect(lambda : self.functionTooltip("Activetooltip"))       
        self.activeTooltip = True if self.QChecklabelActivetooltip.isChecked() else False  # si ouverture sans chgt et sauve
        self.layoutExplorer.addWidget(self.QChecklabelActivetooltip, 0, 4, Qt.AlignTop)        
        #--
        self.labelActiveTooltipWithtitle = QtWidgets.QLabel()
        self.labelActiveTooltipWithtitle.setAlignment(Qt.AlignRight)        
        self.labelActiveTooltipWithtitle.setText(QtWidgets.QApplication.translate("colorbloc_ui", "Show label :"))         
        self.labelActiveTooltipWithtitle.setToolTip("Extract metadata label")        
        self.labelActiveTooltipWithtitle.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        self.labelActiveTooltipWithtitle.setWordWrap(True)
        self.layoutExplorer.addWidget(self.labelActiveTooltipWithtitle, 1, 0, 1, 4, Qt.AlignTop)
        #--
        self.QChecklabelActiveTooltipWithtitle = QtWidgets.QCheckBox()
        self.QChecklabelActiveTooltipWithtitle.setObjectName("QChecklabelActiveTooltipWithtitle")
        self.QChecklabelActiveTooltipWithtitle.setChecked(self.activeTooltipWithtitle)  
        self.QChecklabelActiveTooltipWithtitle.toggled.connect(lambda : self.functionTooltip("ActiveTooltipWithtitle"))       
        self.QChecklabelActiveTooltipWithtitle.setToolTip(QtWidgets.QApplication.translate("colorbloc_ui", "Extract metadata label :"))        
        self.activeTooltipWithtitle = True if self.QChecklabelActiveTooltipWithtitle.isChecked() else False  # si ouverture sans chgt et sauve
        self.layoutExplorer.addWidget(self.QChecklabelActiveTooltipWithtitle, 1, 4, Qt.AlignTop)
        #--
        self.labelActiveTooltipLogo = QtWidgets.QLabel()
        self.labelActiveTooltipLogo.setAlignment(Qt.AlignRight)        
        self.labelActiveTooltipLogo.setText(QtWidgets.QApplication.translate("colorbloc_ui", "Logo Plume :"))         
        self.labelActiveTooltipLogo.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        self.labelActiveTooltipLogo.setWordWrap(True)
        self.layoutExplorer.addWidget(self.labelActiveTooltipLogo, 2, 0, 1, 4, Qt.AlignTop)
        #--
        self.QChecklabelActiveTooltipLogo = QtWidgets.QCheckBox()
        self.QChecklabelActiveTooltipLogo.setObjectName("QChecklabelActiveTooltipLogo")
        self.QChecklabelActiveTooltipLogo.setChecked(self.activeTooltipLogo)  
        self.QChecklabelActiveTooltipLogo.toggled.connect(lambda : self.functionTooltip("ActiveTooltipLogo"))       
        self.activeTooltipLogo = True if self.QChecklabelActiveTooltipLogo.isChecked() else False  # si ouverture sans chgt et sauve
        self.layoutExplorer.addWidget(self.QChecklabelActiveTooltipLogo, 2, 4, Qt.AlignTop)
        #--
        self.labelActiveTooltipCadre = QtWidgets.QLabel()
        self.labelActiveTooltipCadre.setAlignment(Qt.AlignRight)        
        self.labelActiveTooltipCadre.setText(QtWidgets.QApplication.translate("colorbloc_ui", "Border :"))         
        self.labelActiveTooltipCadre.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        self.labelActiveTooltipCadre.setWordWrap(True)
        self.layoutExplorer.addWidget(self.labelActiveTooltipCadre, 3, 0, 1, 4, Qt.AlignTop)
        #--
        self.QChecklabelActiveTooltipCadre = QtWidgets.QCheckBox()
        self.QChecklabelActiveTooltipCadre.setObjectName("QChecklabelActiveTooltipCadre")
        self.QChecklabelActiveTooltipCadre.setChecked(self.activeTooltipCadre)  
        self.QChecklabelActiveTooltipCadre.toggled.connect(lambda : self.functionTooltip("ActiveTooltipCadre"))       
        self.activeTooltipCadre = True if self.QChecklabelActiveTooltipCadre.isChecked() else False  # si ouverture sans chgt et sauve
        self.layoutExplorer.addWidget(self.QChecklabelActiveTooltipCadre, 3, 4, Qt.AlignTop)
        #--
        self.labelActiveTooltipColor = QtWidgets.QLabel()
        self.labelActiveTooltipColor.setAlignment(Qt.AlignRight)        
        self.labelActiveTooltipColor.setText(QtWidgets.QApplication.translate("colorbloc_ui", "Color :"))         
        self.labelActiveTooltipColor.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        self.labelActiveTooltipColor.setWordWrap(True)
        self.layoutExplorer.addWidget(self.labelActiveTooltipColor, 5, 0, 1, 4, Qt.AlignTop)
        #--
        self.QChecklabelActiveTooltipColor = QtWidgets.QCheckBox()
        self.QChecklabelActiveTooltipColor.setObjectName("QChecklabelActiveTooltipColor")
        self.QChecklabelActiveTooltipColor.setChecked(self.activeTooltipColor)  
        self.QChecklabelActiveTooltipColor.toggled.connect(lambda : self.functionTooltip("ActiveTooltipColor"))       
        self.activeTooltipColor = True if self.QChecklabelActiveTooltipColor.isChecked() else False  # si ouverture sans chgt et sauve
        self.layoutExplorer.addWidget(self.QChecklabelActiveTooltipColor, 5, 4, Qt.AlignTop)
        #--
        layout, button_7, img_7, reset_7 = self.layoutExplorer, QtWidgets.QPushButton(), QtWidgets.QLabel(), QtWidgets.QPushButton()
        self.button_7, self.reset_7 = button_7, reset_7
        self.genereButtonActionColor(layout, button_7, img_7, reset_7, "button_7", "img_7", "reset_7", 7)
        #--
        layout, button_8, img_8, reset_8 = self.layoutExplorer, QtWidgets.QPushButton(), QtWidgets.QLabel(), QtWidgets.QPushButton()
        self.button_8, self.reset_8 = button_8, reset_8
        self.genereButtonActionColor(layout, button_8, img_8, reset_8, "button_8", "img_8", "reset_8", 8)
        self.functionTooltip("Activetooltip")
        # Onglets EXPLORER
        #========
        #========
        # Onglets ADVANCED
        self.groupBoxAdvanced = QtWidgets.QGroupBox()
        self.groupBoxAdvanced.setObjectName("groupBoxAdvanced")
        self.groupBoxAdvanced.setStyleSheet("QGroupBox { border: 0px solid red }")
        #-
        self.layoutAdvanced = QtWidgets.QGridLayout()
        self.layoutAdvanced.setContentsMargins(0, 0, 0, 0)
        self.layoutAdvanced.setColumnStretch(0, 2)
        self.layoutAdvanced.setColumnStretch(1, 1)
        self.layoutAdvanced.setColumnStretch(2, 2)
        self.groupBoxAdvanced.setLayout(self.layoutAdvanced)
        self.layout_tab_widget_Advanced.addWidget(self.groupBoxAdvanced, 0, 0, Qt.AlignTop)
        #------
        mLabelLangListText    = QtWidgets.QApplication.translate("colorbloc_ui", "LangList", None)
        mLabelLangListToolTip = QtWidgets.QApplication.translate("colorbloc_ui", "LangListToolTip", None)
        mLabelLangList = QtWidgets.QLabel()
        mLabelLangList.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        mLabelLangList.setObjectName("mLabelLangList")
        mLabelLangList.setText(mLabelLangListText)
        mLabelLangList.setToolTip(mLabelLangListToolTip)
        mLabelLangList.setWordWrap(True)
        mLabelLangList.setAlignment(Qt.AlignRight)        
        self.layoutAdvanced.addWidget(mLabelLangList, 0, 0, Qt.AlignTop)
        #- 
        mZoneLangList = QtWidgets.QLineEdit()
        mZoneLangList.setStyleSheet("QLineEdit {  font-family:" + self.policeQGroupBox  +";}")
        mZoneLangList.setObjectName("mZoneLangList")
        mZoneLangList.setText(",".join(self.langList))
        mZoneLangList.setToolTip(mLabelLangListToolTip)
        self.layoutAdvanced.addWidget(mZoneLangList, 0, 1, Qt.AlignTop)
        #------ 
        #------   A voir plus tard
        """
        mLabelGeoideJSONText    = QtWidgets.QApplication.translate("colorbloc_ui", "GeoideJSON", None)
        mLabelGeoideJSONToolTip = QtWidgets.QApplication.translate("colorbloc_ui", "GeoideJSONToolTip", None)
        mLabelGeoideJSON = QtWidgets.QLabel()
        mLabelGeoideJSON.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        mLabelGeoideJSON.setObjectName("mLabelGeoideJSON")
        mLabelGeoideJSON.setText(mLabelGeoideJSONText)
        mLabelGeoideJSON.setToolTip(mLabelGeoideJSONToolTip)
        mLabelGeoideJSON.setWordWrap(True)
        mLabelGeoideJSON.setAlignment(Qt.AlignRight)        
        self.layoutAdvanced.addWidget(mLabelGeoideJSON, 1, 0, Qt.AlignTop)
        #- 
        mZoneGeoideJSON = QtWidgets.QCheckBox()
        mZoneGeoideJSON.setStyleSheet("QCheckBox {  font-family:" + self.policeQGroupBox  +";}")
        mZoneGeoideJSON.setObjectName("mZoneGeoideJSON")
        mZoneGeoideJSON.setChecked(True if self.geoideJSON else False)
        mZoneGeoideJSON.setToolTip(mLabelGeoideJSONToolTip)
        self.layoutAdvanced.addWidget(mZoneGeoideJSON, 1, 0, Qt.AlignTop)
        mLabelGeoideJSON.setVisible(False)
        mZoneGeoideJSON.setVisible(False)
        """
        #------   A voir plus tard
        #------ 
        mLabelPreferedTemplateText    = QtWidgets.QApplication.translate("colorbloc_ui", "PreferedTemplate", None)
        mLabelPreferedTemplateToolTip = QtWidgets.QApplication.translate("colorbloc_ui", "PreferedTemplateToolTip", None)
        mLabelPreferedTemplate = QtWidgets.QLabel()
        mLabelPreferedTemplate.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        mLabelPreferedTemplate.setObjectName("mLabelPreferedTemplate")
        mLabelPreferedTemplate.setText(mLabelPreferedTemplateText)
        mLabelPreferedTemplate.setToolTip(mLabelPreferedTemplateToolTip)
        mLabelPreferedTemplate.setWordWrap(True)
        mLabelPreferedTemplate.setAlignment(Qt.AlignRight)        
        self.layoutAdvanced.addWidget(mLabelPreferedTemplate, 1, 0, Qt.AlignTop)
        #- 
        mZonePreferedTemplate = QtWidgets.QLineEdit()
        mZonePreferedTemplate.setStyleSheet("QLineEdit {  font-family:" + self.policeQGroupBox  +";}")
        mZonePreferedTemplate.setObjectName("mZonePreferedTemplate")
        mZonePreferedTemplate.setText(self.preferedTemplate)
        mZonePreferedTemplate.setToolTip(mLabelPreferedTemplateToolTip)
        self.layoutAdvanced.addWidget(mZonePreferedTemplate, 1, 1, Qt.AlignTop)
        #------ 
        mLabelEnforcePreferedTemplateText    = QtWidgets.QApplication.translate("colorbloc_ui", "EnforcePreferedTemplate", None)
        mLabelEnforcePreferedTemplateToolTip = QtWidgets.QApplication.translate("colorbloc_ui", "EnforcePreferedTemplateToolTip", None)
        mLabelEnforcePreferedTemplate = QtWidgets.QLabel()
        mLabelEnforcePreferedTemplate.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        mLabelEnforcePreferedTemplate.setObjectName("mLabelEnforcePreferedTemplate")
        mLabelEnforcePreferedTemplate.setText(mLabelEnforcePreferedTemplateText)
        mLabelEnforcePreferedTemplate.setToolTip(mLabelEnforcePreferedTemplateToolTip)
        mLabelEnforcePreferedTemplate.setWordWrap(True)
        mLabelEnforcePreferedTemplate.setAlignment(Qt.AlignRight)        
        self.layoutAdvanced.addWidget(mLabelEnforcePreferedTemplate, 2, 0, Qt.AlignTop)
        #- 
        mZoneEnforcePreferedTemplate = QtWidgets.QCheckBox()
        mZoneEnforcePreferedTemplate.setStyleSheet("QCheckBox {  font-family:" + self.policeQGroupBox  +";}")
        mZoneEnforcePreferedTemplate.setObjectName("mZoneEnforcePreferedTemplate")
        mZoneEnforcePreferedTemplate.setTristate(True)
        mZoneEnforcePreferedTemplate.setCheckState((Qt.Checked if self.enforcePreferedTemplate else Qt.Unchecked) if self.enforcePreferedTemplate != None else Qt.PartiallyChecked)
        mZoneEnforcePreferedTemplate.setToolTip(mLabelEnforcePreferedTemplateToolTip)
        self.layoutAdvanced.addWidget(mZoneEnforcePreferedTemplate, 2, 1, Qt.AlignTop)
        #------ 
        mLabelReadHideBlankText    = QtWidgets.QApplication.translate("colorbloc_ui", "ReadHideBlank", None)
        mLabelReadHideBlankToolTip = QtWidgets.QApplication.translate("colorbloc_ui", "ReadHideBlankToolTip", None)
        mLabelReadHideBlank = QtWidgets.QLabel()
        mLabelReadHideBlank.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        mLabelReadHideBlank.setObjectName("mLabelReadHideBlank")
        mLabelReadHideBlank.setText(mLabelReadHideBlankText)
        mLabelReadHideBlank.setToolTip(mLabelReadHideBlankToolTip)
        mLabelReadHideBlank.setWordWrap(True)
        mLabelReadHideBlank.setAlignment(Qt.AlignRight)        
        self.layoutAdvanced.addWidget(mLabelReadHideBlank, 3, 0, Qt.AlignTop)
        #- 
        mZoneReadHideBlank = QtWidgets.QCheckBox()
        mZoneReadHideBlank.setStyleSheet("QCheckBox {  font-family:" + self.policeQGroupBox  +";}")
        mZoneReadHideBlank.setObjectName("mZoneReadHideBlank")
        mZoneReadHideBlank.setTristate(True)
        mZoneReadHideBlank.setCheckState((Qt.Checked if self.readHideBlank else Qt.Unchecked) if self.readHideBlank != None else Qt.PartiallyChecked)
        mZoneReadHideBlank.setToolTip(mLabelReadHideBlankToolTip)
        self.layoutAdvanced.addWidget(mZoneReadHideBlank, 3, 1, Qt.AlignTop)
        #------
        mLabelReadHideUnlistedText    = QtWidgets.QApplication.translate("colorbloc_ui", "ReadHideUnlisted", None)
        mLabelReadHideUnlistedToolTip = QtWidgets.QApplication.translate("colorbloc_ui", "ReadHideUnlistedToolTip", None)
        mLabelReadHideUnlisted = QtWidgets.QLabel()
        mLabelReadHideUnlisted.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        mLabelReadHideUnlisted.setObjectName("mLabelReadHideUnlisted")
        mLabelReadHideUnlisted.setText(mLabelReadHideUnlistedText)
        mLabelReadHideUnlisted.setToolTip(mLabelReadHideUnlistedToolTip)
        mLabelReadHideUnlisted.setWordWrap(True)
        mLabelReadHideUnlisted.setAlignment(Qt.AlignRight)        
        self.layoutAdvanced.addWidget(mLabelReadHideUnlisted, 4, 0, Qt.AlignTop)
        #- 
        mZoneReadHideUnlisted = QtWidgets.QCheckBox()
        mZoneReadHideUnlisted.setStyleSheet("QCheckBox {  font-family:" + self.policeQGroupBox  +";}")
        mZoneReadHideUnlisted.setObjectName("mZoneReadHideUnlisted")
        mZoneReadHideUnlisted.setTristate(True)
        mZoneReadHideUnlisted.setCheckState((Qt.Checked if self.readHideUnlisted else Qt.Unchecked) if self.readHideUnlisted != None else Qt.PartiallyChecked)
        mZoneReadHideUnlisted.setToolTip(mLabelReadHideUnlistedToolTip)
        self.layoutAdvanced.addWidget(mZoneReadHideUnlisted, 4, 1, Qt.AlignTop)
        #------ 
        mLabelEditHideUnlistedText    = QtWidgets.QApplication.translate("colorbloc_ui", "EditHideUnlisted", None)
        mLabelEditHideUnlistedToolTip = QtWidgets.QApplication.translate("colorbloc_ui", "EditHideUnlistedToolTip", None)
        mLabelEditHideUnlisted = QtWidgets.QLabel()
        mLabelEditHideUnlisted.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        mLabelEditHideUnlisted.setObjectName("mLabelEditHideUnlisted")
        mLabelEditHideUnlisted.setText(mLabelEditHideUnlistedText)
        mLabelEditHideUnlisted.setToolTip(mLabelEditHideUnlistedToolTip)
        mLabelEditHideUnlisted.setWordWrap(True)
        mLabelEditHideUnlisted.setAlignment(Qt.AlignRight)        
        self.layoutAdvanced.addWidget(mLabelEditHideUnlisted, 5, 0, Qt.AlignTop)
        #- 
        mZoneEditHideUnlisted = QtWidgets.QCheckBox()
        mZoneEditHideUnlisted.setStyleSheet("QCheckBox {  font-family:" + self.policeQGroupBox  +";}")
        mZoneEditHideUnlisted.setObjectName("mZoneEditHideUnlisted")
        mZoneEditHideUnlisted.setTristate(True)
        mZoneEditHideUnlisted.setCheckState((Qt.Checked if self.editHideUnlisted else Qt.Unchecked) if self.editHideUnlisted != None else Qt.PartiallyChecked)
        mZoneEditHideUnlisted.setToolTip(mLabelEditHideUnlistedToolTip)
        self.layoutAdvanced.addWidget(mZoneEditHideUnlisted, 5, 1, Qt.AlignTop)
        #------ 
        mLabelreadOnlyCurrentLanguageText    = QtWidgets.QApplication.translate("colorbloc_ui", "ReadOnlyCurrentLanguage", None)
        mLabelreadOnlyCurrentLanguageToolTip = QtWidgets.QApplication.translate("colorbloc_ui", "ReadOnlyCurrentLanguageToolTip", None)
        mLabelreadOnlyCurrentLanguage = QtWidgets.QLabel()
        mLabelreadOnlyCurrentLanguage.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        mLabelreadOnlyCurrentLanguage.setObjectName("mLabelreadOnlyCurrentLanguage")
        mLabelreadOnlyCurrentLanguage.setText(mLabelreadOnlyCurrentLanguageText)
        mLabelreadOnlyCurrentLanguage.setToolTip(mLabelreadOnlyCurrentLanguageToolTip)
        mLabelreadOnlyCurrentLanguage.setWordWrap(True)
        mLabelreadOnlyCurrentLanguage.setAlignment(Qt.AlignRight)        
        self.layoutAdvanced.addWidget(mLabelreadOnlyCurrentLanguage, 6, 0, Qt.AlignTop)
        #- 
        mZonereadOnlyCurrentLanguage = QtWidgets.QCheckBox()
        mZonereadOnlyCurrentLanguage.setStyleSheet("QCheckBox {  font-family:" + self.policeQGroupBox  +";}")
        mZonereadOnlyCurrentLanguage.setObjectName("mZonereadOnlyCurrentLanguage")
        mZonereadOnlyCurrentLanguage.setTristate(True)
        mZonereadOnlyCurrentLanguage.setCheckState((Qt.Checked if self.readOnlyCurrentLanguage else Qt.Unchecked) if self.readOnlyCurrentLanguage != None else Qt.PartiallyChecked)
        mZonereadOnlyCurrentLanguage.setToolTip(mLabelreadOnlyCurrentLanguageToolTip)
        self.layoutAdvanced.addWidget(mZonereadOnlyCurrentLanguage, 6, 1, Qt.AlignTop)
        #------ 
        mLabelEditOnlyCurrentLanguageText    = QtWidgets.QApplication.translate("colorbloc_ui", "EditOnlyCurrentLanguage", None)
        mLabelEditOnlyCurrentLanguageToolTip = QtWidgets.QApplication.translate("colorbloc_ui", "EditOnlyCurrentLanguageToolTip", None)
        mLabelEditOnlyCurrentLanguage = QtWidgets.QLabel()
        mLabelEditOnlyCurrentLanguage.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        mLabelEditOnlyCurrentLanguage.setObjectName("mLabelEditOnlyCurrentLanguage")
        mLabelEditOnlyCurrentLanguage.setText(mLabelEditOnlyCurrentLanguageText)
        mLabelEditOnlyCurrentLanguage.setToolTip(mLabelEditOnlyCurrentLanguageToolTip)
        mLabelEditOnlyCurrentLanguage.setWordWrap(True)
        mLabelEditOnlyCurrentLanguage.setAlignment(Qt.AlignRight)        
        self.layoutAdvanced.addWidget(mLabelEditOnlyCurrentLanguage, 7, 0, Qt.AlignTop)
        #- 
        mZoneEditOnlyCurrentLanguage = QtWidgets.QCheckBox()
        mZoneEditOnlyCurrentLanguage.setStyleSheet("QCheckBox {  font-family:" + self.policeQGroupBox  +";}")
        mZoneEditOnlyCurrentLanguage.setObjectName("mZoneEditOnlyCurrentLanguage")
        mZoneEditOnlyCurrentLanguage.setTristate(True)
        mZoneEditOnlyCurrentLanguage.setCheckState((Qt.Checked if self.editOnlyCurrentLanguage else Qt.Unchecked) if self.editOnlyCurrentLanguage != None else Qt.PartiallyChecked)
        mZoneEditOnlyCurrentLanguage.setToolTip(mLabelEditOnlyCurrentLanguageToolTip)
        self.layoutAdvanced.addWidget(mZoneEditOnlyCurrentLanguage, 7, 1, Qt.AlignTop)
        #------ 
        mLabelLabelLengthLimitText    = QtWidgets.QApplication.translate("colorbloc_ui", "LabelLengthLimit", None)
        mLabelLabelLengthLimitToolTip = QtWidgets.QApplication.translate("colorbloc_ui", "LabelLengthLimitToolTip", None)
        mLabelLabelLengthLimit = QtWidgets.QLabel()
        mLabelLabelLengthLimit.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        mLabelLabelLengthLimit.setObjectName("mLabelLabelLengthLimit")
        mLabelLabelLengthLimit.setText(mLabelLabelLengthLimitText)
        mLabelLabelLengthLimit.setToolTip(mLabelLabelLengthLimitToolTip)
        mLabelLabelLengthLimit.setWordWrap(True)
        mLabelLabelLengthLimit.setAlignment(Qt.AlignRight)        
        self.layoutAdvanced.addWidget(mLabelLabelLengthLimit, 8, 0, Qt.AlignTop)
        #- 
        mZoneLabelLengthLimit = QtWidgets.QLineEdit()
        mZoneLabelLengthLimit.setStyleSheet("QLineEdit {  font-family:" + self.policeQGroupBox  +";}")
        mZoneLabelLengthLimit.setObjectName("mZoneLabelLengthLimit")
        mZoneLabelLengthLimit.setText(str(self.labelLengthLimit))
        mZoneLabelLengthLimit.setInputMask("99999")
        mZoneLabelLengthLimit.setCursorPosition(0)
        mZoneLabelLengthLimit.setToolTip(mLabelLabelLengthLimitToolTip)
        self.layoutAdvanced.addWidget(mZoneLabelLengthLimit, 8, 1, Qt.AlignTop)
        #------ 
        mLabelValueLengthLimitText    = QtWidgets.QApplication.translate("colorbloc_ui", "ValueLengthLimit", None)
        mLabelValueLengthLimitToolTip = QtWidgets.QApplication.translate("colorbloc_ui", "ValueLengthLimitToolTip", None)
        mLabelValueLengthLimit = QtWidgets.QLabel()
        mLabelValueLengthLimit.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        mLabelValueLengthLimit.setObjectName("mLabelValueLengthLimit")
        mLabelValueLengthLimit.setText(mLabelValueLengthLimitText)
        mLabelValueLengthLimit.setToolTip(mLabelValueLengthLimitToolTip)
        mLabelValueLengthLimit.setWordWrap(True)
        mLabelValueLengthLimit.setAlignment(Qt.AlignRight)        
        self.layoutAdvanced.addWidget(mLabelValueLengthLimit, 9, 0, Qt.AlignTop)
        #- 
        mZoneValueLengthLimit = QtWidgets.QLineEdit()
        mZoneValueLengthLimit.setStyleSheet("QLineEdit {  font-family:" + self.policeQGroupBox  +";}")
        mZoneValueLengthLimit.setObjectName("mZoneValueLengthLimit")
        mZoneValueLengthLimit.setText(str(self.valueLengthLimit))
        mZoneValueLengthLimit.setInputMask("99999")
        mZoneValueLengthLimit.setCursorPosition(0)
        mZoneValueLengthLimit.setToolTip(mLabelValueLengthLimitToolTip)
        self.layoutAdvanced.addWidget(mZoneValueLengthLimit, 9, 1, Qt.AlignTop)
        #------ 
        mLabelTextEditRowSpanText    = QtWidgets.QApplication.translate("colorbloc_ui", "TextEditRowSpan", None)
        mLabelTextEditRowSpanToolTip = QtWidgets.QApplication.translate("colorbloc_ui", "TextEditRowSpanToolTip", None)
        mLabelTextEditRowSpan = QtWidgets.QLabel()
        mLabelTextEditRowSpan.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        mLabelTextEditRowSpan.setObjectName("mLabelTextEditRowSpan")
        mLabelTextEditRowSpan.setText(mLabelTextEditRowSpanText)
        mLabelTextEditRowSpan.setToolTip(mLabelTextEditRowSpanToolTip)
        mLabelTextEditRowSpan.setWordWrap(True)
        mLabelTextEditRowSpan.setAlignment(Qt.AlignRight)        
        self.layoutAdvanced.addWidget(mLabelTextEditRowSpan, 10, 0, Qt.AlignTop)
        #- 
        mZoneTextEditRowSpan = QtWidgets.QLineEdit()
        mZoneTextEditRowSpan.setStyleSheet("QLineEdit {  font-family:" + self.policeQGroupBox  +";}")
        mZoneTextEditRowSpan.setObjectName("mZoneTextEditRowSpan")
        mZoneTextEditRowSpan.setText(str(self.textEditRowSpan))
        mZoneTextEditRowSpan.setCursorPosition(0)
        mZoneTextEditRowSpan.setInputMask("99999")
        mZoneTextEditRowSpan.setToolTip(mLabelTextEditRowSpanToolTip)
        self.layoutAdvanced.addWidget(mZoneTextEditRowSpan, 10, 1, Qt.AlignTop)

        self.mZoneLangList, self.mZonePreferedTemplate, self.mZoneEnforcePreferedTemplate, self.mZoneReadHideBlank, self.mZoneReadHideUnlisted, self.mZoneEditHideUnlisted, self.mZonereadOnlyCurrentLanguage, self.mZoneEditOnlyCurrentLanguage, self.mZoneLabelLengthLimit, self.mZoneValueLengthLimit, self.mZoneTextEditRowSpan = \
        mZoneLangList, mZonePreferedTemplate, mZoneEnforcePreferedTemplate, mZoneReadHideBlank, mZoneReadHideUnlisted, mZoneEditHideUnlisted, mZonereadOnlyCurrentLanguage, mZoneEditOnlyCurrentLanguage, mZoneLabelLengthLimit, mZoneValueLengthLimit, mZoneTextEditRowSpan 
        #------ 
        mlabelCleanPgDescriptionText    = QtWidgets.QApplication.translate("colorbloc_ui", "Clean up the PostgreSQL description", None)
        mlabelCleanPgDescriptionToolTip = QtWidgets.QApplication.translate("colorbloc_ui", "By default, Plume adds its metadata to the information present in the PostgreSQL description of the table/view, preserving the latter. When this option is activated, this non-metadata information is erased from the description when saving.", None)
        mlabelCleanPgDescription = QtWidgets.QLabel()
        mlabelCleanPgDescription.setText(mlabelCleanPgDescriptionText)
        mlabelCleanPgDescription.setAlignment(Qt.AlignRight)        
        mlabelCleanPgDescription.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        mlabelCleanPgDescription.setToolTip(mlabelCleanPgDescriptionToolTip)
        mlabelCleanPgDescription.setWordWrap(True)
        self.layoutAdvanced.addWidget(mlabelCleanPgDescription, 11, 0, Qt.AlignTop)
        #-
        mDicCleanPgDescription = {"never":"Jamais", "first":"À l'initialisation de la fiche", "always":"Toujours"}
        self.comboCleanPgDescription= QtWidgets.QComboBox()
        self.comboCleanPgDescription.setObjectName("comboCleanPgDescription")
        self.comboCleanPgDescription.addItems([ elem for elem in mDicCleanPgDescription.values() ])
        self.comboCleanPgDescription.setCurrentText(mDicCleanPgDescription[self.zComboCleanPgDescription])         
        self.comboCleanPgDescription.currentTextChanged.connect(lambda : self.functionCleanPgDescription(mDicCleanPgDescription))
        self.comboCleanPgDescription.setToolTip(mlabelCleanPgDescriptionToolTip)
        mValueTemp = [ k for k, v in mDicCleanPgDescription.items() if v == self.comboCleanPgDescription.currentText()][0]
        self.zComboCleanPgDescription = mValueTemp  # si ouverture sans chgt et sauve
        self.layoutAdvanced.addWidget(self.comboCleanPgDescription, 11, 1, Qt.AlignTop)
        #------ 
        mLabelCopyDctTitleToPgDescriptionText    = QtWidgets.QApplication.translate("colorbloc_ui", "Copy dataset label to PostgreSQL description", None)
        mLabelCopyDctTitleToPgDescriptionToolTip = QtWidgets.QApplication.translate("colorbloc_ui", "If active, the label of the dataset entered in the metadata will be copied to the beginning of the PostgreSQL description of the table/view when saving the form. Warning: this has the effect of removing any other information placed before the metadata in the PostgreSQL description.", None)
        mLabelCopyDctTitleToPgDescription = QtWidgets.QLabel()
        mLabelCopyDctTitleToPgDescription.setObjectName("mLabelCopyDctTitleToPgDescription")
        mLabelCopyDctTitleToPgDescription.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        mLabelCopyDctTitleToPgDescription.setText(mLabelCopyDctTitleToPgDescriptionText)
        mLabelCopyDctTitleToPgDescription.setToolTip(mLabelCopyDctTitleToPgDescriptionToolTip)
        mLabelCopyDctTitleToPgDescription.setWordWrap(True)
        mLabelCopyDctTitleToPgDescription.setAlignment(Qt.AlignRight)        
        self.layoutAdvanced.addWidget(mLabelCopyDctTitleToPgDescription, 12, 0, Qt.AlignTop)
        #- 
        self.mZoneCopyDctTitleToPgDescription = QtWidgets.QCheckBox()
        self.mZoneCopyDctTitleToPgDescription.setStyleSheet("QCheckBox {  font-family:" + self.policeQGroupBox  +";}")
        self.mZoneCopyDctTitleToPgDescription.setObjectName("mZoneCopyDctTitleToPgDescription")
        self.mZoneCopyDctTitleToPgDescription.setChecked(True if self.copyDctTitleToPgDescription else False)
        self.mZoneCopyDctTitleToPgDescription.setToolTip(mLabelCopyDctTitleToPgDescriptionToolTip)
        self.layoutAdvanced.addWidget(self.mZoneCopyDctTitleToPgDescription, 12, 1, Qt.AlignTop)
        #- 
        self.copyDctTitleToPgDescription = self.mZoneCopyDctTitleToPgDescription 
        #------ 
        mLabelCopyDctDescriptionToPgDescriptionText    = QtWidgets.QApplication.translate("colorbloc_ui", "Copy dataset description to PostgreSQL description", None)
        mLabelCopyDctDescriptionToPgDescriptionToolTip = QtWidgets.QApplication.translate("colorbloc_ui", "If active, the description of the dataset entered in the metadata will be copied at the beginning of the PostgreSQL description of the table/view when saving the form. Warning: this has the effect of removing any other information placed before the metadata in the PostgreSQL description.", None)
        mLabelCopyDctDescriptionToPgDescription = QtWidgets.QLabel()
        mLabelCopyDctDescriptionToPgDescription.setObjectName("mLabelCopyDctDescriptionToPgDescription")
        mLabelCopyDctDescriptionToPgDescription.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        mLabelCopyDctDescriptionToPgDescription.setText(mLabelCopyDctDescriptionToPgDescriptionText)
        mLabelCopyDctDescriptionToPgDescription.setToolTip(mLabelCopyDctDescriptionToPgDescriptionToolTip)
        mLabelCopyDctDescriptionToPgDescription.setWordWrap(True)
        mLabelCopyDctDescriptionToPgDescription.setAlignment(Qt.AlignRight)        
        self.layoutAdvanced.addWidget(mLabelCopyDctDescriptionToPgDescription, 13, 0, Qt.AlignTop)
        #- 
        self.mZoneCopyDctDescriptionToPgDescription = QtWidgets.QCheckBox()
        self.mZoneCopyDctDescriptionToPgDescription.setStyleSheet("QCheckBox {  font-family:" + self.policeQGroupBox  +";}")
        self.mZoneCopyDctDescriptionToPgDescription.setObjectName("mZoneCopyDctDescriptionToPgDescription")
        self.mZoneCopyDctDescriptionToPgDescription.setChecked(True if self.copyDctDescriptionToPgDescription else False)
        self.mZoneCopyDctDescriptionToPgDescription.setToolTip(mLabelCopyDctDescriptionToPgDescriptionToolTip)
        self.layoutAdvanced.addWidget(self.mZoneCopyDctDescriptionToPgDescription, 13, 1, Qt.AlignTop)
        #- 
        self.copyDctDescriptionToPgDescription = self.mZoneCopyDctDescriptionToPgDescription 
        # Onglets ADVANCED  
        #========

        #======== wysiwyg
        self.createWYSIWYG()
        #======== wysiwyg
        #======== User Settings
        #self.createUserSettings()
        #======== User Settings

        #-
        self.groupBox_buttons = QtWidgets.QGroupBox(self.DialogColorBloc)
        self.groupBox_buttons.setGeometry(QtCore.QRect(10,self.DialogColorBloc.height() - 60,self.DialogColorBloc.width() - 20, 60))
        self.groupBox_buttons.setObjectName("groupBox_tab_widget_General")
        self.groupBox_buttons.setStyleSheet("QGroupBox { border: 0px solid green }")
        #-
        self.layout_groupBox_buttons = QtWidgets.QGridLayout()
        self.layout_groupBox_buttons.setContentsMargins(0, 0, 0, 0)
        self.groupBox_buttons.setLayout(self.layout_groupBox_buttons)
        #-
        self.layout_groupBox_buttons.setColumnStretch(0, 3)
        self.layout_groupBox_buttons.setColumnStretch(1, 1)
        self.layout_groupBox_buttons.setColumnStretch(2, 1)
        self.layout_groupBox_buttons.setColumnStretch(3, 1)
        self.layout_groupBox_buttons.setColumnStretch(4, 3)
        #-
        self.labelPushButton = QtWidgets.QLabel()
        self.labelPushButton.setObjectName("pushButton")
        self.labelPushButton.setAlignment(Qt.AlignCenter)        
        self.labelPushButton.setText("<i>" + QtWidgets.QApplication.translate("colorbloc_ui", "The modifications will be taken into account the next time you start Plume.") + "</i>")         
        self.layout_groupBox_buttons.addWidget(self.labelPushButton, 1, 0, 1, 5, Qt.AlignTop)
        #--
        self.pushButton = QtWidgets.QPushButton(self.DialogColorBloc)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setGeometry(QtCore.QRect(self.DialogColorBloc.width() / 2 - 100, self.DialogColorBloc.height() - 60, 80, 25))
        self.pushButton.clicked.connect(lambda : self.functionSave())
        self.layout_groupBox_buttons.addWidget(self.pushButton, 0, 1, Qt.AlignTop)
        #----------
        self.pushButtonAnnuler = QtWidgets.QPushButton(self.DialogColorBloc)
        self.pushButtonAnnuler.setObjectName("pushButtonAnnuler")
        self.pushButtonAnnuler.clicked.connect(self.DialogColorBloc.reject)
        self.layout_groupBox_buttons.addWidget(self.pushButtonAnnuler, 0, 3,  Qt.AlignTop)
        #----------
        self.DialogColorBloc.setWindowTitle(QtWidgets.QApplication.translate("colorbloc_ui", "PLUME (Metadata storage in PostGreSQL") + "  (" + str(bibli_plume.returnVersion()) + ")")
        self.label_2.setText(QtWidgets.QApplication.translate("colorbloc_ui", self.zMessTitle, None))
        self.pushButton.setText(QtWidgets.QApplication.translate("colorbloc_ui", "OK", None))
        self.pushButtonAnnuler.setText(QtWidgets.QApplication.translate("colorbloc_ui", "Cancel", None))
        return 

    #==========================         
    #==========================         
    def onValueChangedOpacity(self) :
        valueOpacity = self.comboOpacity.opacity()
        # coeff d'opacité
        self.opacityEffect.setOpacity(float(valueOpacity))
        # adding opacity effect to the label
        self.labelOpacity.setGraphicsEffect(self.opacityEffect)
        return 

    #==========================         
    #==========================         
    def functionFont(self):
        self.zFontQGroupBox = self.fontQGroupBox.currentFont().family()
        # --
        self.applyWYSIWYG() #Lecture et apply des variables
        # --

    #==========================         
    #==========================             
    def functionLine(self, mDicTypeCle):
        self.zLineQGroupBox = [ k for k, v in mDicTypeCle.items() if v == self.comboTypeLine.currentText()][0]
        # --
        self.applyWYSIWYG() #Lecture et apply des variables
        # --
        return 
                                                                                                                  
    #==========================         
    #==========================             
    def functionWinVsDock(self, mDicWinVsDock):
        self.zComboWinVsDock = [ k for k, v in mDicWinVsDock.items() if v == self.comboWinVsDock.currentText()][0]
        # --
        self.applyWYSIWYG() #Lecture et apply des variables
        # --
        return 

    #==========================         
    #==========================             
    def functionCleanPgDescription(self, mDicCleanPgDescription):
        self.zComboCleanPgDescription = [ k for k, v in mDicCleanPgDescription.items() if v == self.comboCleanPgDescription.currentText()][0]
        # -- 
        self.applyWYSIWYG() #Lecture et apply des variables
        # --
        return 

    #==========================       
    def functionEpai(self):
        self.zEpaiQGroupBox = self.spinBoxEpai.value()
        # --
        self.applyWYSIWYG() #Lecture et apply des variables
        # --
        return 

    #==========================       
    # for geometry         
    def functiongeomPrecision(self):
        self.geomPrecision = self.spingeomPrecision.value()
        return 

    def functiongeomEpaisseur(self):
        self.geomEpaisseur = self.spingeomEpaisseur.value()
        return 

    def functiongeomPointEpaisseur(self):
        self.geomPointEpaisseur = self.spingeomPointEpaisseur.value()
        return 

    def functioncomboTypegeomPoint(self):
        self.geomPoint = self.comboTypegeomPoint.currentText().upper()
        return 

    def functiongeomZoom(self):
        self.geomZoom = True if self.QCheckgeomZoom.isChecked() else False
        return 
    # for geometry         
 
    #==========================       
    # for tooltip         
    def functionTooltip(self, param):
        print(param)
        if param == "Activetooltip" : 
           self.activeTooltip = True if self.QChecklabelActivetooltip.isChecked() else False
           self.QChecklabelActiveTooltipWithtitle.setEnabled(self.activeTooltip)
           self.QChecklabelActiveTooltipLogo.setEnabled(self.activeTooltip)
           self.QChecklabelActiveTooltipCadre.setEnabled(self.activeTooltip)
           self.QChecklabelActiveTooltipColor.setEnabled(self.activeTooltip)

           if self.activeTooltip :
              self.button_7.setEnabled(self.QChecklabelActiveTooltipColor.isChecked())
              self.reset_7.setEnabled(self.QChecklabelActiveTooltipColor.isChecked())
              self.button_8.setEnabled(self.QChecklabelActiveTooltipColor.isChecked())
              self.reset_8.setEnabled(self.QChecklabelActiveTooltipColor.isChecked())
           else :  
              self.button_7.setEnabled(False)
              self.reset_7.setEnabled(False)
              self.button_8.setEnabled(False)
              self.reset_8.setEnabled(False)
        elif param == "ActiveTooltipWithtitle" : 
           self.activeTooltipWithtitle = True if self.QChecklabelActiveTooltipWithtitle.isChecked() else False
        elif param == "ActiveTooltipLogo" : 
           self.activeTooltipLogo = True if self.QChecklabelActiveTooltipLogo.isChecked() else False
        elif param == "ActiveTooltipCadre" : 
           self.activeTooltipCadre = True if self.QChecklabelActiveTooltipCadre.isChecked() else False
        elif param == "ActiveTooltipColor" : 
           self.activeTooltipColor = True if self.QChecklabelActiveTooltipColor.isChecked() else False
           self.button_7.setEnabled(self.activeTooltipColor)
           self.reset_7.setEnabled(self.activeTooltipColor)
           self.button_8.setEnabled(self.activeTooltipColor)
           self.reset_8.setEnabled(self.activeTooltipColor)
        elif param == "activeZoneNonSaisie" :     
           self.activeZoneNonSaisie = True if self.mZoneZoneNonSaisie.isChecked() else False
           self.button_9.setEnabled(self.activeZoneNonSaisie)
           self.reset_9.setEnabled(self.activeZoneNonSaisie)
           self.labelOpacity.setEnabled(self.activeZoneNonSaisie)
           self.comboOpacity.setEnabled(self.activeZoneNonSaisie)
        return 
    # for tooltip         
    #==========================         

    #==========================         
    def createWYSIWYG(self):
        #======== wysiwyg
        _thesaurus = ['', 'Agriculture, pêche, sylviculture et alimentation', 'Économie et finances', 'Éducation, culture et sport', 'Énergie', 'Environnement', 'Gouvernement et secteur public', 'Justice, système juridique et sécurité publique', 'Population et société', 'Questions internationales', 'Régions et villes', 'Santé', 'Science et technologie', 'Transports']
        _thesaurus2 = ['', 'Adresses', 'Altitude', 'Bâtiments', 'Caractéristiques géographiques météorologiques', 'Caractéristiques géographiques océanographiques', 'Conditions atmosphériques', 'Dénominations géographiques', 'Géologie', 'Habitats et biotopes', 'Hydrographie', 'Installations agricoles et aquacoles', 'Installations de suivi environnemental', 'Lieux de production et sites industriels', 'Occupation des terres', 'Ortho-imagerie', 'Parcelles cadastrales', 'Référentiels de coordonnées', 'Régions biogéographiques', 'Régions maritimes', 'Répartition de la population — démographie', 'Répartition des espèces', 'Réseaux de transport', 'Ressources minérales', 'Santé et sécurité des personnes', "Services d'utilité publique et services publics", 'Sites protégés', 'Sols', "Sources d'énergie", 'Systèmes de maillage géographique', 'Unités administratives', 'Unités statistiques', 'Usage des sols', 'Zones à risque naturel', 'Zones de gestion']

        _pathIcons     = os.path.dirname(__file__) + "/icons/general"
        _iconSourcesSelectBrown    = _pathIcons + "/selected_brown.svg"
        _pathIconsUser = QgsApplication.qgisSettingsDirPath().replace("\\","/") + "plume/icons/buttons"
        _pathIcons     = os.path.dirname(__file__) + "/icons/buttons"
        _iconQComboBox             = _pathIcons + "/drop_down_arrow.svg"
        _iconQComboBox = _iconQComboBox.replace("\\","/")
        _iconSources               = _pathIcons + "/source_button.svg"
        _iconSourcesSelect         = _pathIcons + "/selected_blue.svg"
        _iconSourcesVierge         = _pathIcons + ""
        _iconPlus                  = _pathIcons + "/plus_button.svg"
        _iconPlusTempGoValues      = _pathIconsUser + "/color_button_Plus_GoValues_ForVisu.svg"
        _iconPlusTempTgroup        = _pathIconsUser + "/color_button_Plus_Tgroup_ForVisu.svg"
        _iconMinus                 = _pathIcons + "/minus_button.svg"
        _iconMinusTempGoValues     = _pathIconsUser + "/color_button_Minus_GoValues_ForVisu.svg"
        _iconMinusTempTgroup       = _pathIconsUser + "/color_button_Minus_Tgroup_ForVisu.svg"
        _mListeIconsButtonPlusMinus = [ _iconPlusTempGoValues,  _iconPlusTempTgroup, \
                                        _iconMinusTempGoValues, _iconMinusTempTgroup ]
        #
        #self.colorQGroupBox                   = self.mDic_LH["QGroupBox"]                  
        self.colorQGroupBoxGroupOfProperties  = self.mDic_LH["QGroupBoxGroupOfProperties"]  
        self.colorQGroupBoxGroupOfValues      = self.mDic_LH["QGroupBoxGroupOfValues"]      
        self.colorQGroupBoxTranslationGroup   = self.mDic_LH["QGroupBoxTranslationGroup"]   
        self.colorQTabWidget                  = self.mDic_LH["QTabWidget"]
        self.labelBackGround                  = self.mDic_LH["QLabelBackGround"] #QLabel    
        #
        self.editStyle        = self.mDic_LH["QEdit"] #QEdit   groove, ridge, inset, outset 
        self.epaiQGroupBox    = self.mDic_LH["QGroupBoxEpaisseur"] #épaisseur QGroupBox
        self.lineQGroupBox    = self.mDic_LH["QGroupBoxLine"]    #trait QGroupBox
        self.policeQGroupBox  = self.mDic_LH["QGroupBoxPolice"]  #Police QGroupBox
        self.writeColorIconForVisu(_iconPlus, _iconMinus, _mListeIconsButtonPlusMinus) 
        #
        self.tabWidgetFalse = QTabWidget()
        self.tabWidgetFalse.setObjectName("tabWidget")
        # --
        self.tabWidgetFalse.setStyleSheet("QTabWidget::pane {border: 2px solid " + self.colorQTabWidget  + "; font-family:" + self.policeQGroupBox  +"; } \
                                    QTabBar::tab {border: 1px solid " + self.colorQTabWidget  + "; border-bottom-color: none; font-family:" + self.policeQGroupBox  +";\
                                                    border-top-left-radius: 6px;border-top-right-radius: 6px;\
                                      QTabBar::tab:selected {background: qlineargradient(x1: 0, y1: 0, x2: 0.5, y2: 0.5, stop: 0 " + self.colorQTabWidget  + ", stop: 1 white);  font: bold;} \
                                     ")
        self.layoutWysiwig.addWidget(self.tabWidgetFalse, 0, 0)
        #--------------------------
        self.tab_widget_Tab1 = QWidget()
        self.tab_widget_Tab1.setObjectName("tab_widget_Tab1")
        labeltab_widget_Tab1 = QtWidgets.QApplication.translate("colorbloc_ui", "  tab 1   ", None)
        self.tabWidgetFalse.addTab(self.tab_widget_Tab1, labeltab_widget_Tab1)
        #-
        self.falseGroupBox_tab_widget_Tab1 = QtWidgets.QGroupBox(self.tab_widget_Tab1)
        self.falseGroupBox_tab_widget_Tab1.setGeometry(QtCore.QRect(10,10,self.tabWidgetFalse.width() - 240, self.tabWidgetFalse.height() - 120))
        self.falseGroupBox_tab_widget_Tab1.setObjectName("falseGroupBox_tab_widget_Tab1")
        self.falseGroupBox_tab_widget_Tab1.setStyleSheet("QGroupBox { border: 0px solid red }")
        #-
        self.layout_falseGroupBox_tab_widget_Tab1 = QtWidgets.QGridLayout()
        self.layout_falseGroupBox_tab_widget_Tab1.setContentsMargins(0, 0, 0, 0)
        self.falseGroupBox_tab_widget_Tab1.setLayout(self.layout_falseGroupBox_tab_widget_Tab1)
        #--------------------------
        self.tab_widget_Tab2 = QWidget()
        self.tab_widget_Tab2.setObjectName("tab_widget_Tab2")
        labeltab_widget_Tab2 = QtWidgets.QApplication.translate("colorbloc_ui", "  tab 2   ", None)
        self.tabWidgetFalse.addTab(self.tab_widget_Tab2, labeltab_widget_Tab2)
        #--------------------------
        self.falseGroupBox = QtWidgets.QGroupBox()
        self.falseGroupBox.setObjectName("falseGroupBox")
        self.falseGroupBox.setStyleSheet("QGroupBox { border: 0px solid yellow }")
        #-
        self.layout_falseGroupBox = QtWidgets.QGridLayout()
        self.layout_falseGroupBox.setContentsMargins(0, 0, 0, 0)
        self.falseGroupBox.setLayout(self.layout_falseGroupBox)
        self.layout_falseGroupBox_tab_widget_Tab1.addWidget(self.falseGroupBox, 0, 0,  Qt.AlignTop)
        self.tabWidgetFalse.setCurrentIndex(0)
        #==========================         
        #------ 
        self.falseGroupBoxProperties = QtWidgets.QGroupBox()
        self.falseGroupBoxProperties.setObjectName("falseGroupBoxProperties")
        self.falseGroupBoxProperties.setStyleSheet("QGroupBox#falseGroupBoxProperties {   \
                                margin-top: 6px; \
                                margin-left: 10px; \
                                font-family:" + self.policeQGroupBox  +" ; \
                                border-style: " + self.lineQGroupBox  + ";    \
                                border-width:" + str(self.epaiQGroupBox)  + "px ; \
                                border-radius: 10px;     \
                                border-color: " + self.colorQGroupBoxGroupOfProperties  +";      \
                                font: bold 11px;         \
                                padding: 6px;            \
                                }")
        self.falseGroupBoxProperties.setTitle(self.dicListLettreLabel[2]) 
        self.layout_falseGroupBox.addWidget(self.falseGroupBoxProperties, 1, 0,  Qt.AlignTop)
        #-- 
        self.layout_falseGroupBoxProperties = QtWidgets.QGridLayout()
        self.layout_falseGroupBoxProperties.setContentsMargins(0, 0, 0, 0)
        self.falseGroupBoxProperties.setLayout(self.layout_falseGroupBoxProperties)
        #-- 
        self.layout_falseGroupBoxProperties.setColumnStretch(0, 1)
        self.layout_falseGroupBoxProperties.setColumnStretch(1, 1)
        self.layout_falseGroupBoxProperties.setColumnStretch(2, 1)
        #------
        self.mLabelEdit = QtWidgets.QLabel()
        self.mLabelEdit.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        self.mLabelEdit.setObjectName("mLabelEdit")
        self.mLabelEdit.setText(QtWidgets.QApplication.translate("colorbloc_ui", "Boundary rectangle"))
        self.mLabelEdit.setAlignment(Qt.AlignRight)        
        self.mLabelEdit.setWordWrap(True)
        self.layout_falseGroupBoxProperties.addWidget(self.mLabelEdit, 0, 0,  Qt.AlignTop)
        #- 
        self.mzoneEdit = QtWidgets.QLineEdit()
        self.mzoneEdit.setStyleSheet("QLineEdit {  font-family:" + self.policeQGroupBox  +"; border-style:" + self.editStyle  +" ; border-width: 0px;}")
        self.mzoneEdit.setObjectName("mzoneEdit")
        self.mzoneEdit.setText("POLYGON((2.46962285 48.81560897,2.46962285 48.90165328,2.22396016 48.90165328,2.22396016 48.81560897,2.46962285 48.81560897))")
        self.mzoneEdit.setAlignment(Qt.AlignLeft)
        self.mzoneEdit.setCursorPosition(0)
        self.layout_falseGroupBoxProperties.addWidget(self.mzoneEdit, 0, 1, 1, 3, Qt.AlignTop)
        #------ 
        self.mLabelDate = QtWidgets.QLabel()
        self.mLabelDate.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        self.mLabelDate.setObjectName("mLabelEdit")
        self.mLabelDate.setText(QtWidgets.QApplication.translate("colorbloc_ui", "Creation date")) 
        self.mLabelDate.setAlignment(Qt.AlignRight)        
        self.mLabelDate.setWordWrap(True)
        self.layout_falseGroupBoxProperties.addWidget(self.mLabelDate, 1, 0,  Qt.AlignTop)
        #- 
        self.mzoneDate = QgsDateTimeEdit()
        self.mzoneDate.setStyleSheet("QgsDateTimeEdit {  font-family:" + self.policeQGroupBox  +"; }")
        self.mzoneDate.setObjectName("mzoneDate")
        _displayFormat = 'dd/MM/yyyy'
        self.mzoneDate.setDisplayFormat(_displayFormat)
        self.mzoneDate.setDate(QDate.currentDate())
        self.mzoneDate.setMinimumWidth(112)
        self.mzoneDate.setMaximumWidth(112)
        self.mzoneDate.setCalendarPopup(True)
        self.layout_falseGroupBoxProperties.addWidget(self.mzoneDate, 1, 1,  Qt.AlignTop)
        #------ 
        #------ 
        self.falseBoxGroupOfValues = QtWidgets.QGroupBox()
        self.falseBoxGroupOfValues.setObjectName("falseBoxGroupOfValues")
        self.falseBoxGroupOfValues.setStyleSheet("QGroupBox#falseBoxGroupOfValues {   \
                                margin-top: 6px; \
                                margin-left: 10px; \
                                font-family:" + self.policeQGroupBox  +" ; \
                                border-style: " + self.lineQGroupBox  + ";    \
                                border-width:" + str(self.epaiQGroupBox)  + "px ; \
                                border-radius: 10px;     \
                                border-color: " + self.colorQGroupBoxGroupOfValues  +";      \
                                font: bold 11px;         \
                                padding: 6px;            \
                                }")
        self.falseBoxGroupOfValues.setTitle(self.dicListLettreLabel[3]) 
        self.layout_falseGroupBox.addWidget(self.falseBoxGroupOfValues, 2, 0,  Qt.AlignTop)
        #-- 
        self.layout_falseBoxGroupOfValues = QtWidgets.QGridLayout()
        self.layout_falseBoxGroupOfValues.setContentsMargins(0, 0, 0, 0)
        self.falseBoxGroupOfValues.setLayout(self.layout_falseBoxGroupOfValues)
        #-- 
        self.layout_falseBoxGroupOfValues.setColumnStretch(0, 1)
        self.layout_falseBoxGroupOfValues.setColumnStretch(1, 1)
        self.layout_falseBoxGroupOfValues.setColumnStretch(2, 1)
        self.layout_falseBoxGroupOfValues.setColumnStretch(3, 1)
        self.layout_falseBoxGroupOfValues.setColumnStretch(4, 1)
        self.layout_falseBoxGroupOfValues.setColumnStretch(5, 1)
        self.layout_falseBoxGroupOfValues.setColumnStretch(6, 1)
        self.layout_falseBoxGroupOfValues.setColumnStretch(7, 1)
        #------------------------
        self.mzoneTextCombo = QtWidgets.QComboBox()
        self.mzoneTextCombo.setStyleSheet("QComboBox {  font-family:" + self.policeQGroupBox  +"; border-style:" + self.editStyle  + " ; border-width: 0px;} \
                                        QComboBox::drop-down {border: 0px;}\
                                        QComboBox::down-arrow {image: url(" + _iconQComboBox + ");position:absolute; left : 5px;width: 12px;height: 45px;}") 
        self.mzoneTextCombo.setObjectName("mzoneTextCombo")
        self.mzoneTextCombo.addItems(_thesaurus)
        self.mzoneTextCombo.setCurrentText("Agriculture, pêche, sylviculture et alimentation") 
        self.mzoneTextCombo.setEditable(True)
        mCompleter = QCompleter(_thesaurus, self)
        mCompleter.setCaseSensitivity(Qt.CaseInsensitive)
        self.mzoneTextCombo.setCompleter(mCompleter)
        self.layout_falseBoxGroupOfValues.addWidget(self.mzoneTextCombo, 0, 0, 1, 5, Qt.AlignTop)
        #- 
        self.mSourcesQToolButton = QtWidgets.QToolButton()
        self.mSourcesQToolButton.setObjectName("mSourcesQToolButton")
        self.mSourcesQToolButton.setIcon(QIcon(_iconSources))
        self.layout_falseBoxGroupOfValues.addWidget(self.mSourcesQToolButton, 0, 6, Qt.AlignTop)
        #MenuQToolButton                        
        self.SourcesQMenuG1 = QMenu()
        self.SourcesQMenuG1.setStyleSheet("QMenu {  font-family:" + self.policeQGroupBox  +"; border-style:" + self.editStyle  +" ; border-width: 0px;}")
        #------------
        for elemQMenuItem in ['Thème INSPIRE (UE)', 'Thème de données (UE)'] :
            if elemQMenuItem == 'Thème de données (UE)' : 
               _mObjetQMenuIcon = QIcon(_iconSourcesSelect)
            else :                 
               _mObjetQMenuIcon = QIcon("")
              
            _mObjetQMenuItem = QAction(elemQMenuItem, self.SourcesQMenuG1)
            _mObjetQMenuItem.setText(elemQMenuItem)
            _mObjetQMenuItem.setObjectName(str(elemQMenuItem))
            _mObjetQMenuItem.setIcon(_mObjetQMenuIcon)
            self.SourcesQMenuG1.addAction(_mObjetQMenuItem)
       
        self.mSourcesQToolButton.setPopupMode(self.mSourcesQToolButton.MenuButtonPopup)
        self.mSourcesQToolButton.setMenu(self.SourcesQMenuG1)
        #- 
        self.mzoneTextQToolButton = QtWidgets.QToolButton()
        self.mzoneTextQToolButton.setObjectName("mzoneTextQToolButton")
        self.mzoneTextQToolButton.setText("fr")
        self.layout_falseBoxGroupOfValues.addWidget(self.mzoneTextQToolButton, 0, 7, Qt.AlignTop)
        self.mObjetQMenuG11 = QMenu()
        self.mObjetQMenuG11.setStyleSheet("QMenu {  font-family:" + self.policeQGroupBox  +"; width:50px; border-style:" + self.editStyle  + "; border-width: 0px;}")
        #
        for elemQMenuItem in ['fr', 'en'] :
            if elemQMenuItem == 'fr' : 
               _mObjetQMenuIcon = QIcon(_iconSourcesSelectBrown)
            else :                 
               _mObjetQMenuIcon = QIcon("")

            _mObjetQMenuItem = QAction(elemQMenuItem, self.mObjetQMenuG11)
            _mObjetQMenuItem.setText(elemQMenuItem)
            _mObjetQMenuItem.setObjectName(str(elemQMenuItem))
            _mObjetQMenuItem.setIcon(_mObjetQMenuIcon)
            self.mObjetQMenuG11.addAction(_mObjetQMenuItem)
        self.mzoneTextQToolButton.setPopupMode(self.mzoneTextQToolButton.MenuButtonPopup)
        self.mzoneTextQToolButton.setMenu(self.mObjetQMenuG11)
        #- 
        self.mzoneTextQToolButtonMoins = QtWidgets.QToolButton(self.falseBoxGroupOfValues)
        self.mzoneTextQToolButtonMoins.setObjectName("mzoneTextQToolButtonMoins")
        self.layout_falseBoxGroupOfValues.addWidget(self.mzoneTextQToolButtonMoins, 0, 8, Qt.AlignTop)
        # == QICON
        self.mzoneTextQToolButtonMoins.setIcon(QIcon(_iconMinusTempGoValues))
        # == QICON
        #------------------------ 
        self.mzoneTextCombo2 = QtWidgets.QComboBox()
        self.mzoneTextCombo2.setStyleSheet("QComboBox {  font-family:" + self.policeQGroupBox  +"; border-style:" + self.editStyle  + " ; border-width: 0px;} \
                                        QComboBox::drop-down {border: 0px;}\
                                        QComboBox::down-arrow {image: url(" + _iconQComboBox + ");position:absolute; left : 5px;width: 12px;height: 45px;}") 
        self.mzoneTextCombo2.setObjectName("mzoneTextCombo2")
        self.mzoneTextCombo2.addItems(_thesaurus2)
        self.mzoneTextCombo2.setCurrentText("Bâtiments") 
        self.mzoneTextCombo2.setEditable(True)
        mCompleter = QCompleter(_thesaurus2, self)
        mCompleter.setCaseSensitivity(Qt.CaseInsensitive)
        self.mzoneTextCombo2.setCompleter(mCompleter)
        self.layout_falseBoxGroupOfValues.addWidget(self.mzoneTextCombo2, 1, 0, 1, 5, Qt.AlignTop)
        #- 
        self.mSourcesQToolButton2 = QtWidgets.QToolButton()
        self.mSourcesQToolButton2.setObjectName("mSourcesQToolButton")
        self.mSourcesQToolButton2.setIcon(QIcon(_iconSources))
        self.layout_falseBoxGroupOfValues.addWidget(self.mSourcesQToolButton2, 1, 6, Qt.AlignTop)
        #MenuQToolButton                        
        self.SourcestQMenuG2 = QMenu()
        self.SourcestQMenuG2.setStyleSheet("QMenu {  font-family:" + self.policeQGroupBox  +"; border-style:" + self.editStyle  +" ; border-width: 0px;}")
        #------------
        for elemQMenuItem in ['Thème INSPIRE (UE)', 'Thème de données (UE)'] :
            if elemQMenuItem == 'Thème INSPIRE (UE)' : 
               _mObjetQMenuIcon = QIcon(_iconSourcesSelect)
            else :                 
               _mObjetQMenuIcon = QIcon(_iconSourcesVierge)

            _mObjetQMenuItem = QAction(elemQMenuItem, self.SourcestQMenuG2)
            _mObjetQMenuItem.setText(elemQMenuItem)
            _mObjetQMenuItem.setObjectName(str(elemQMenuItem))
            _mObjetQMenuItem.setIcon(_mObjetQMenuIcon)
            self.SourcestQMenuG2.addAction(_mObjetQMenuItem)
       
        self.mSourcesQToolButton2.setPopupMode(self.mSourcesQToolButton2.MenuButtonPopup)
        self.mSourcesQToolButton2.setMenu(self.SourcestQMenuG2)
        #- 
        self.mzoneTextQToolButton2 = QtWidgets.QToolButton()
        self.mzoneTextQToolButton2.setObjectName("mzoneTextQToolButton")
        self.mzoneTextQToolButton2.setText("en")
        self.layout_falseBoxGroupOfValues.addWidget(self.mzoneTextQToolButton2, 1, 7, Qt.AlignTop)
        self.mObjetQMenuG2 = QMenu()
        self.mObjetQMenuG2.setStyleSheet("QMenu {  font-family:" + self.policeQGroupBox  +"; width:50px; border-style:" + self.editStyle  + "; border-width: 0px;}")
        #
        for elemQMenuItem in ['fr', 'en'] :
            if elemQMenuItem == 'en' : 
               _mObjetQMenuIcon = QIcon(_iconSourcesSelectBrown)
            else :                 
               _mObjetQMenuIcon = QIcon(_iconSourcesVierge)
            _mObjetQMenuItem = QAction(elemQMenuItem, self.mObjetQMenuG2)
            _mObjetQMenuItem.setText(elemQMenuItem)
            _mObjetQMenuItem.setObjectName(str(elemQMenuItem))
            _mObjetQMenuItem.setIcon(_mObjetQMenuIcon)
            self.mObjetQMenuG2.addAction(_mObjetQMenuItem)
        self.mzoneTextQToolButton2.setPopupMode(self.mzoneTextQToolButton.MenuButtonPopup)
        self.mzoneTextQToolButton2.setMenu(self.mObjetQMenuG2)
        #- 
        self.mzoneTextQToolButtonMoins2 = QtWidgets.QToolButton()
        self.mzoneTextQToolButtonMoins2.setObjectName("mzoneTextQToolButtonMoins")
        # == QICON
        self.mzoneTextQToolButtonMoins2.setIcon(QIcon(_iconMinusTempGoValues))
        # == QICON
        self.layout_falseBoxGroupOfValues.addWidget(self.mzoneTextQToolButtonMoins2, 1, 8, Qt.AlignTop)
        #- 
        self.mzoneTextQToolButtonPlus = QtWidgets.QToolButton()
        self.mzoneTextQToolButtonPlus.setObjectName("mzoneTextQToolButtonPlus")
        # == QICON
        self.mzoneTextQToolButtonPlus.setIcon(QIcon(_iconPlusTempGoValues))
        # == QICON
        self.layout_falseBoxGroupOfValues.addWidget(self.mzoneTextQToolButtonPlus, 3, 0, Qt.AlignTop)
        #------------------------ 
        #------
        self.falseBoxTranslationGroup = QtWidgets.QGroupBox()
        self.falseBoxTranslationGroup.setObjectName("falseBoxTranslationGroup")
        self.falseBoxTranslationGroup.setStyleSheet("QGroupBox#falseBoxTranslationGroup {   \
                                margin-top: 6px; \
                                margin-left: 10px; \
                                font-family:" + self.policeQGroupBox  +" ; \
                                border-style: " + self.lineQGroupBox  + ";    \
                                border-width:" + str(self.epaiQGroupBox)  + "px ; \
                                border-radius: 10px;     \
                                border-color: " + self.colorQGroupBoxTranslationGroup  +";      \
                                font: bold 11px;         \
                                padding: 6px;            \
                                }")
        self.falseBoxTranslationGroup.setTitle(self.dicListLettreLabel[4]) 
        self.layout_falseGroupBox.addWidget(self.falseBoxTranslationGroup, 3, 0, Qt.AlignTop)
        #-- 
        self.layout_falseBoxTranslationGroup = QtWidgets.QGridLayout()
        self.layout_falseBoxTranslationGroup.setContentsMargins(0, 0, 0, 0)
        self.falseBoxTranslationGroup.setLayout(self.layout_falseBoxTranslationGroup)
        #-- 
        self.layout_falseBoxTranslationGroup.setColumnStretch(0, 1)
        self.layout_falseBoxTranslationGroup.setColumnStretch(1, 1)
        self.layout_falseBoxTranslationGroup.setColumnStretch(2, 1)
        self.layout_falseBoxTranslationGroup.setColumnStretch(3, 1)
        self.layout_falseBoxTranslationGroup.setColumnStretch(4, 1)
        self.layout_falseBoxTranslationGroup.setColumnStretch(5, 1)
        self.layout_falseBoxTranslationGroup.setColumnStretch(6, 1)
        self.layout_falseBoxTranslationGroup.setColumnStretch(7, 1)
        #------------------------ 
        self.mzoneTextTrad = QtWidgets.QTextEdit()
        self.mzoneTextTrad.setStyleSheet("QTextEdit {  font-family:" + self.policeQGroupBox  +"; border-style:" + self.editStyle  +" ; border-width: 0px;}")
        self.mzoneTextTrad.setObjectName("mzoneText")
        self.mzoneTextTrad.setText("Délimitation des zones")
        self.layout_falseBoxTranslationGroup.addWidget(self.mzoneTextTrad, 0, 0, 1, 7, Qt.AlignTop)
        #- 
        self.mzoneTextQToolButtonTrad = QtWidgets.QToolButton()
        self.mzoneTextQToolButtonTrad.setObjectName("mzoneTextQToolButton")
        self.mzoneTextQToolButtonTrad.setText("en")
        self.mObjetQMenuG1Trad = QMenu()
        self.mObjetQMenuG1Trad.setStyleSheet("QMenu {  font-family:" + self.policeQGroupBox  +"; width:50px; border-style:" + self.editStyle  + "; border-width: 0px;}")
        self.layout_falseBoxTranslationGroup.addWidget(self.mzoneTextQToolButtonTrad, 0, 7, Qt.AlignTop)
        #
        for elemQMenuItem in ['fr', 'en'] :
            if elemQMenuItem == 'en' : 
               _mObjetQMenuIcon = QIcon(_iconSourcesSelectBrown)
            else :                 
               _mObjetQMenuIcon = QIcon(_iconSourcesVierge)

            _mObjetQMenuItem = QAction(elemQMenuItem, self.mObjetQMenuG1Trad)
            _mObjetQMenuItem.setText(elemQMenuItem)
            _mObjetQMenuItem.setObjectName(str(elemQMenuItem))
            _mObjetQMenuItem.setIcon(_mObjetQMenuIcon)
            self.mObjetQMenuG1Trad.addAction(_mObjetQMenuItem)
        self.mzoneTextQToolButtonTrad.setPopupMode(self.mzoneTextQToolButtonTrad.MenuButtonPopup)
        self.mzoneTextQToolButtonTrad.setMenu(self.mObjetQMenuG1Trad)
        #- 
        self.mzoneTextQToolButtonMoinsTrad = QtWidgets.QToolButton()
        self.mzoneTextQToolButtonMoinsTrad.setObjectName("mzoneTextQToolButtonMoins")
        # == QICON
        self.mzoneTextQToolButtonMoinsTrad.setIcon(QIcon(_iconMinusTempTgroup))
        # == QICON
        self.layout_falseBoxTranslationGroup.addWidget(self.mzoneTextQToolButtonMoinsTrad, 0, 8, Qt.AlignTop)
        #------------------------ 
        self.mzoneText2Trad = QtWidgets.QTextEdit()
        self.mzoneText2Trad.setStyleSheet("QTextEdit {  font-family:" + self.policeQGroupBox  +"; border-style:" + self.editStyle  +" ; border-width: 0px;}")
        self.mzoneText2Trad.setObjectName("mzoneText2")
        self.mzoneText2Trad.setText("La table est mise à jour selon l’actualité")
        self.layout_falseBoxTranslationGroup.addWidget(self.mzoneText2Trad, 1, 0, 1, 7, Qt.AlignTop)
        #- 
        self.mzoneTextQToolButton2Trad = QtWidgets.QToolButton()
        self.mzoneTextQToolButton2Trad.setObjectName("mzoneTextQToolButton")
        self.mzoneTextQToolButton2Trad.setText("fr")
        self.mObjetQMenuG2Trad = QMenu()
        self.mObjetQMenuG2Trad.setStyleSheet("QMenu {  font-family:" + self.policeQGroupBox  +"; width:50px; border-style:" + self.editStyle  + "; border-width: 0px;}")
        self.layout_falseBoxTranslationGroup.addWidget(self.mzoneTextQToolButton2Trad, 1, 7, Qt.AlignTop)
        #
        for elemQMenuItem in ['fr', 'en'] :
            if elemQMenuItem == 'fr' : 
               _mObjetQMenuIcon = QIcon(_iconSourcesSelectBrown)
            else :                 
               _mObjetQMenuIcon = QIcon(_iconSourcesVierge)

            _mObjetQMenuItem = QAction(elemQMenuItem, self.mObjetQMenuG2Trad)
            _mObjetQMenuItem.setText(elemQMenuItem)
            _mObjetQMenuItem.setObjectName(str(elemQMenuItem))
            _mObjetQMenuItem.setIcon(_mObjetQMenuIcon)
            self.mObjetQMenuG2Trad.addAction(_mObjetQMenuItem)
        self.mzoneTextQToolButton2Trad.setPopupMode(self.mzoneTextQToolButton2Trad.MenuButtonPopup)
        self.mzoneTextQToolButton2Trad.setMenu(self.mObjetQMenuG2Trad)
        #- 
        self.mzoneTextQToolButtonMoins2Trad = QtWidgets.QToolButton()
        self.mzoneTextQToolButtonMoins2Trad.setObjectName("mzoneTextQToolButtonMoins")
        # == QICON
        self.mzoneTextQToolButtonMoins2Trad.setIcon(QIcon(_iconMinusTempTgroup))
        # == QICON
        self.layout_falseBoxTranslationGroup.addWidget(self.mzoneTextQToolButtonMoins2Trad, 1, 8, Qt.AlignTop)
        #- 
        self.mzoneTextQToolButtonPlusTrad = QtWidgets.QToolButton()
        self.mzoneTextQToolButtonPlusTrad.setObjectName("mzoneTextQToolButtonPlus")
        # == QICON
        self.mzoneTextQToolButtonPlusTrad.setIcon(QIcon(_iconPlusTempTgroup))
        # == QICON
        self.layout_falseBoxTranslationGroup.addWidget(self.mzoneTextQToolButtonPlusTrad, 2, 0, Qt.AlignTop)
        #------------------------ 
        return 
        
    #==========================         
    #==========================         
    def applyWYSIWYG(self): 
        _pathIconsUser = QgsApplication.qgisSettingsDirPath().replace("\\","/") + "plume/icons/buttons"
        _pathIcons     = os.path.dirname(__file__) + "/icons/general"
        _iconSourcesSelectBrown    = _pathIcons + "/selected_brown.svg"
        _pathIcons     = os.path.dirname(__file__) + "/icons/buttons"
        _iconQComboBox             = _pathIcons + "/drop_down_arrow.svg"
        _iconQComboBox = _iconQComboBox.replace("\\","/")
        _iconSources               = _pathIcons + "/source_button.svg"
        _iconSourcesSelect         = _pathIcons + "/selected_blue.svg"
        _iconSourcesVierge         = _pathIcons + ""
        _iconPlus                  = _pathIcons + "/plus_button.svg"
        _iconPlusTempGoValues      = _pathIconsUser + "/color_button_Plus_GoValues_ForVisu.svg"
        _iconPlusTempTgroup        = _pathIconsUser + "/color_button_Plus_Tgroup_ForVisu.svg"
        _iconMinus                 = _pathIcons + "/minus_button.svg"
        _iconMinusTempGoValues     = _pathIconsUser + "/color_button_Minus_GoValues_ForVisu.svg"
        _iconMinusTempTgroup       = _pathIconsUser + "/color_button_Minus_Tgroup_ForVisu.svg"
        _mListeIconsButtonPlusMinus = [ _iconPlusTempGoValues,  _iconPlusTempTgroup, \
                                        _iconMinusTempGoValues, _iconMinusTempTgroup ]
        #METADATA
        mChild_premier = [mObj for mObj in self.groupBoxMetadata.children()] 
        mLettre, mColorFirst, mDicSaveColor = "", None, {}  
        for mObj in mChild_premier :
            for i in range(6) :
                if mObj.objectName() == "img_" + str(i) :
                   mLettre      = str(self.dicListLettre[i])
                   mColor       = mObj.palette().color(QPalette.Window)
                   mColorFirst  = mColor.name()
                   mDicSaveColor[mLettre] = mColorFirst                                 
                   break
        #self.colorQGroupBox                   = mDicSaveColor["QGroupBox"]                  
        self.colorQGroupBoxGroupOfProperties  = mDicSaveColor["QGroupBoxGroupOfProperties"]  
        self.colorQGroupBoxGroupOfValues      = mDicSaveColor["QGroupBoxGroupOfValues"]      
        self.colorQGroupBoxTranslationGroup   = mDicSaveColor["QGroupBoxTranslationGroup"]   
        self.colorQTabWidget                  = mDicSaveColor["QTabWidget"]
        self.colorQLabel                      = mDicSaveColor["QLabelBackGround"]
        #-  
        self.editStyle        = self.zEditStyle    
        self.epaiQGroupBox    = self.zEpaiQGroupBox
        self.policeQGroupBox  = self.zFontQGroupBox
        self.lineQGroupBox    = self.zLineQGroupBox  
        
        self.writeColorIconForVisu(_iconPlus, _iconMinus, _mListeIconsButtonPlusMinus) 
                      

        self.policeQTabWidget = self.mDic_LH["QTabWidgetPolice"] #Police QTabWidget
        #--                
        self.tabWidgetFalse.setStyleSheet("QTabWidget::pane {border: 2px solid " + self.colorQTabWidget  + "; font-family:" + self.policeQGroupBox  +"; } \
                                    QTabBar::tab {border: 1px solid " + self.colorQTabWidget  + "; border-bottom-color: none; font-family:" + self.policeQGroupBox  +";\
                                                    border-top-left-radius: 6px;border-top-right-radius: 6px;\
                                      QTabBar::tab:selected {background: qlineargradient(x1: 0, y1: 0, x2: 0.5, y2: 0.5, stop: 0 " + self.colorQTabWidget  + ", stop: 1 white);  font: bold;} \
                                     ")
        #---
        """
        self.falseGroupBox.setStyleSheet("QGroupBox#falseGroupBox {   \
                                margin-top: 6px; \
                                margin-left: 10px; \
                                font-family:" + self.policeQGroupBox  +" ; \
                                border-style: " + self.lineQGroupBox  + ";    \
                                border-width: 0px ; \
                                border-radius: 10px;     \
                                border-color: " + self.colorQGroupBox  +";      \
                                font: bold 11px;         \
                                padding: 6px;            \
                                }")
        """                        
        #--- 
        self.falseGroupBoxProperties.setStyleSheet("QGroupBox#falseGroupBoxProperties {   \
                                margin-top: 6px; \
                                margin-left: 10px; \
                                font-family:" + self.policeQGroupBox  +" ; \
                                border-style: " + self.lineQGroupBox  + ";    \
                                border-width:" + str(self.epaiQGroupBox)  + "px ; \
                                border-radius: 10px;     \
                                border-color: " + self.colorQGroupBoxGroupOfProperties  +";      \
                                font: bold 11px;         \
                                padding: 6px;            \
                                }")
        #--- 
        self.falseBoxGroupOfValues.setStyleSheet("QGroupBox#falseBoxGroupOfValues {   \
                                margin-top: 6px; \
                                margin-left: 10px; \
                                font-family:" + self.policeQGroupBox  +" ; \
                                border-style: " + self.lineQGroupBox  + ";    \
                                border-width:" + str(self.epaiQGroupBox)  + "px ; \
                                border-radius: 10px;     \
                                border-color: " + self.colorQGroupBoxGroupOfValues  +";      \
                                font: bold 11px;         \
                                padding: 6px;            \
                                }")
        #--- 
        self.falseBoxTranslationGroup.setStyleSheet("QGroupBox#falseBoxTranslationGroup {   \
                                margin-top: 6px; \
                                margin-left: 10px; \
                                font-family:" + self.policeQGroupBox  +" ; \
                                border-style: " + self.lineQGroupBox  + ";    \
                                border-width:" + str(self.epaiQGroupBox)  + "px ; \
                                border-radius: 10px;     \
                                border-color: " + self.colorQGroupBoxTranslationGroup  +";      \
                                font: bold 11px;         \
                                padding: 6px;            \
                                }")
        #--- 
        self.mLabelEdit.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.colorQLabel  +";}")
        self.mzoneEdit.setStyleSheet("QLineEdit {  font-family:" + self.policeQGroupBox  +"; border-style:" + self.editStyle  +" ; border-width: 0px;}")
        self.mLabelDate.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.colorQLabel  +";}")
        self.mzoneDate.setStyleSheet("QgsDateTimeEdit {  font-family:" + self.policeQGroupBox  +"; }")
        #--- 
        self.mzoneTextCombo.setStyleSheet("QComboBox {  font-family:" + self.policeQGroupBox  +"; border-style:" + self.editStyle  + " ; border-width: 0px;} \
                                        QComboBox::drop-down {border: 0px;}\
                                        QComboBox::down-arrow {image: url(" + _iconQComboBox + ");position:absolute; left : 5px;width: 12px;height: 45px;}") 
        self.SourcesQMenuG1.setStyleSheet("QMenu {  font-family:" + self.policeQGroupBox  +"; border-style:" + self.editStyle  +" ; border-width: 0px;}")
        self.mObjetQMenuG11.setStyleSheet("QMenu {  font-family:" + self.policeQGroupBox  +"; width:50px; border-style:" + self.editStyle  + "; border-width: 0px;}")
        self.mzoneTextQToolButtonMoins.setIcon(QIcon(_iconMinusTempGoValues))
        self.mzoneTextCombo2.setStyleSheet("QComboBox {  font-family:" + self.policeQGroupBox  +"; border-style:" + self.editStyle  + " ; border-width: 0px;} \
                                        QComboBox::drop-down {border: 0px;}\
                                        QComboBox::down-arrow {image: url(" + _iconQComboBox + ");position:absolute; left : 5px;width: 12px;height: 45px;}") 
        self.SourcestQMenuG2.setStyleSheet("QMenu {  font-family:" + self.policeQGroupBox  +"; border-style:" + self.editStyle  +" ; border-width: 0px;}")
        self.mObjetQMenuG2.setStyleSheet("QMenu {  font-family:" + self.policeQGroupBox  +"; width:50px; border-style:" + self.editStyle  + "; border-width: 0px;}")
        self.mzoneTextQToolButtonMoins2.setIcon(QIcon(_iconMinusTempGoValues))
        self.mzoneTextQToolButtonPlus.setIcon(QIcon(_iconPlusTempGoValues))
        #--- 
        self.mzoneTextTrad.setStyleSheet("QTextEdit {  font-family:" + self.policeQGroupBox  +"; border-style:" + self.editStyle  +" ; border-width: 0px;}")
        self.mObjetQMenuG1Trad.setStyleSheet("QMenu {  font-family:" + self.policeQGroupBox  +"; width:50px; border-style:" + self.editStyle  + "; border-width: 0px;}")
        self.mzoneTextQToolButtonMoinsTrad.setIcon(QIcon(_iconMinusTempTgroup))
        self.mzoneText2Trad.setStyleSheet("QTextEdit {  font-family:" + self.policeQGroupBox  +"; border-style:" + self.editStyle  +" ; border-width: 0px;}")
        self.mObjetQMenuG2Trad.setStyleSheet("QMenu {  font-family:" + self.policeQGroupBox  +"; width:50px; border-style:" + self.editStyle  + "; border-width: 0px;}")
        self.mzoneTextQToolButtonMoins2Trad.setIcon(QIcon(_iconMinusTempTgroup))
        self.mzoneTextQToolButtonPlusTrad.setIcon(QIcon(_iconPlusTempTgroup))
        return 

    #==================================================
    # write Color Button SVG for VISU
    def writeColorIconForVisu(self, __iconPlus, __iconMinus, __mListeIconsButtonPlusMinus) :
        with open(__iconPlus,'r') as myTempFile :
           _mTempFile = ""
           for elem in myTempFile.readlines() :
               _mTempFile += elem
           # -    
           mIcon = _mTempFile.format(fill=self.colorQGroupBoxGroupOfValues)
           with open(__mListeIconsButtonPlusMinus[0],'w') as myTempFile :
                myTempFile.write(mIcon)
           # -    
           mIcon = _mTempFile.format(fill=self.colorQGroupBoxTranslationGroup)
           with open(__mListeIconsButtonPlusMinus[1],'w') as myTempFile :
                myTempFile.write(mIcon)
        with open(__iconMinus,'r') as myTempFile :
           _mTempFile = ""
           for elem in myTempFile.readlines() :
               _mTempFile += elem
           # -    
           mIcon = _mTempFile.format(fill=self.colorQGroupBoxGroupOfValues)
           with open(__mListeIconsButtonPlusMinus[2],'w') as myTempFile :
                myTempFile.write(mIcon)
           # -    
           mIcon = _mTempFile.format(fill=self.colorQGroupBoxTranslationGroup)
           with open(__mListeIconsButtonPlusMinus[3],'w') as myTempFile :
                myTempFile.write(mIcon)
        return 


    #==========================         
    def genereButtonActionColor(self, mLayout, mButton, mImage, mReset, mButtonName, mImageName, mResetName, compt):
        i = compt
        line, col = compt, 3
        if compt in (0, 1, 2, 3, 4, 5, 6, 7, 8, 9) : 
           if compt in (0, 1, 2, 3, 4, 5, 9) :
              line, col = compt, 0
           if compt == 9 : 
              line, col = 11, 0
           if compt == 6 : 
              line, col = compt, 3
           if compt == 7 : 
              line, col = 5, 5
           if compt == 8 :  
              line, col = 6, 5
           mButton.setObjectName(mButtonName)
           mButton.setText(self.dicListLettreLabel[i])
           mLayout.addWidget(mButton, line, col, Qt.AlignTop)
           #
           mImage.setObjectName(mImageName)
           if self.dicListLettre[i] in self.mDic_LH :
              varColor = str( self.mDic_LH[self.dicListLettre[i]] ) 
              zStyleBackground = "QLabel { background-color : "  + varColor + "; }"
              mImage.setStyleSheet(zStyleBackground)
           mLayout.addWidget(mImage, line, col + 1, Qt.AlignTop)
           #
           mReset.setObjectName(mResetName)
           mReset.setText(QtWidgets.QApplication.translate("colorbloc_ui", "Reset")) 
           mLayout.addWidget(mReset, line, col + 2, Qt.AlignTop)
           #
           mButton.clicked.connect(lambda : self.functionColor(mImage, i))
           mReset.clicked.connect(lambda : self.functionResetColor(mImage, i, mButtonName))

        return 

    #==========================         
    #==========================         
    def functionSave(self):
        mSettings = QgsSettings()
        mTitre = QtWidgets.QApplication.translate("colorbloc_ui", "Confirmation", None)
        mLib = QtWidgets.QApplication.translate("colorbloc_ui", "You will save all your changes..", None)
        mLib1 = QtWidgets.QApplication.translate("colorbloc_ui", "Are you sure you want to continue ?", None)

        mChild_premier = [mObj for mObj in self.groupBoxMetadata.children()] 

        mLettre, mColorFirst, mDicSaveColor = "", None, {}
        for mObj in mChild_premier :
            for i in range(10) :
                if mObj.objectName() == "img_" + str(i) :
                   mLettre      = str(self.dicListLettre[i])
                   mColor       = mObj.palette().color(QPalette.Window)
                   mColorFirst  = mColor.name()
                   mDicSaveColor[mLettre] = mColorFirst
                   break

       #---- for Tooltip
        mChild_premier = [mObj for mObj in self.groupBoxExplorer.children()] 

        mLettre, mColorFirst = "", None
        for mObj in mChild_premier :
            for i in range(9) :
                if mObj.objectName() == "img_" + str(i) :
                   mLettre      = str(self.dicListLettre[i])
                   mColor       = mObj.palette().color(QPalette.Window)
                   mColorFirst  = mColor.name()
                   mDicSaveColor[mLettre] = mColorFirst
                   break
       #---- for Tooltip
       #======== for Geometry
        mChild_premier = [mObj for mObj in self.groupBoxGeometries.children()] 

        mLettre, mColorFirst = "", None
        for mObj in mChild_premier :
            for i in range(7) :
                if mObj.objectName() == "img_" + str(i) :
                   mLettre      = str(self.dicListLettre[i])
                   mColor       = mObj.palette().color(QPalette.Window)
                   mColorFirst  = mColor.name()
                   mDicSaveColor[mLettre] = mColorFirst
                   break
        #Ajouter si autre param
        mDicSaveColor["geomPrecision"] = self.geomPrecision
        mDicSaveColor["geomEpaisseur"] = self.geomEpaisseur
        mDicSaveColor["geomPoint"]     = self.geomPoint
        mDicSaveColor["geomPointEpaisseur"] = self.geomPointEpaisseur
        mDicSaveColor["geomZoom"]      = "true" if self.geomZoom else "false"
        mDicSaveColor["opacityValue"]  = self.comboOpacity.opacity()
        
        #======== for Geometry
        #-
        mSettings.beginGroup("PLUME")
        mSettings.beginGroup("BlocsColor")
        for key, value in mDicSaveColor.items():
            mSettings.setValue(key, value)
        mSettings.endGroup()
        #---------------
        #Ajouter si autre param
        mDicAutrePolice = {}
        mDicAutrePolice["QEdit"]              = self.zEditStyle
        mDicAutrePolice["QGroupBoxEpaisseur"] = self.zEpaiQGroupBox
        mDicAutrePolice["QGroupBoxLine"]      = self.zLineQGroupBox
        mDicAutrePolice["QGroupBoxPolice"]    = self.zFontQGroupBox
        mSettings.beginGroup("BlocsPolice")
        for key, value in mDicAutrePolice.items():
            mSettings.setValue(key, value)
    
        mSettings.endGroup()    
        #---------------
        #Ajouter si autre param
        mDicAutre = {}
        mDicAutre["ihm"]           = self.zComboWinVsDock
        mDicAutre["activeZoneNonSaisie"]     = "true" if self.activeZoneNonSaisie else "false"
        #---- for Tooltip
        mDicAutre["activeTooltip"]           = "true" if self.activeTooltip else "false"
        mDicAutre["activeTooltipWithtitle"]  = "true" if self.activeTooltipWithtitle else "false"
        mDicAutre["activeTooltipLogo"]       = "true" if self.activeTooltipLogo else "false"
        mDicAutre["activeTooltipCadre"]      = "true" if self.activeTooltipCadre else "false"
        mDicAutre["activeTooltipColor"]      = "true" if self.activeTooltipColor else "false"
        #---- for Tooltip
        mSettings.beginGroup("Generale")
        for key, value in mDicAutre.items():
            mSettings.setValue(key, value)
    
        mSettings.endGroup()    

        #======== User Settings
        mSettings.beginGroup("UserSettings")
        # liste des Paramétres UTILISATEURS
        mDicUserSettings = {}
        mDicUserSettings["langList"]                = self.mZoneLangList.text().split(",")
        #mDicUserSettings["geoideJSON"]              = "true" if self.mZoneGeoideJSON.isChecked() else "false"
        #----
        mDicUserSettings["preferedTemplate"]        = self.mZonePreferedTemplate.text().strip()
        mDicUserSettings["enforcePreferedTemplate"] = ("true" if self.mZoneEnforcePreferedTemplate.checkState() == Qt.Checked else "false") if self.mZoneEnforcePreferedTemplate.checkState() != Qt.PartiallyChecked else ""
        mDicUserSettings["readHideBlank"]           = ("true" if self.mZoneReadHideBlank.checkState() == Qt.Checked else "false")           if self.mZoneReadHideBlank.checkState() != Qt.PartiallyChecked else ""
        mDicUserSettings["readHideUnlisted"]        = ("true" if self.mZoneReadHideUnlisted.checkState() == Qt.Checked else "false")        if self.mZoneReadHideUnlisted.checkState() != Qt.PartiallyChecked else ""
        mDicUserSettings["editHideUnlisted"]        = ("true" if self.mZoneEditHideUnlisted.checkState() == Qt.Checked else "false")        if self.mZoneEditHideUnlisted.checkState() != Qt.PartiallyChecked else ""
        mDicUserSettings["readOnlyCurrentLanguage"] = ("true" if self.mZonereadOnlyCurrentLanguage.checkState() == Qt.Checked else "false") if self.mZonereadOnlyCurrentLanguage.checkState() != Qt.PartiallyChecked else ""
        mDicUserSettings["editOnlyCurrentLanguage"] = ("true" if self.mZoneEditOnlyCurrentLanguage.checkState() == Qt.Checked else "false") if self.mZoneEditOnlyCurrentLanguage.checkState() != Qt.PartiallyChecked else ""
        #----
        mDicUserSettings["labelLengthLimit"]        = "" if self.mZoneLabelLengthLimit.text().strip(",") == "" else int(self.mZoneLabelLengthLimit.text())
        mDicUserSettings["valueLengthLimit"]        = "" if self.mZoneValueLengthLimit.text().strip(",") == "" else int(self.mZoneValueLengthLimit.text())
        mDicUserSettings["textEditRowSpan"]         = "" if self.mZoneTextEditRowSpan.text().strip(",")  == "" else int(self.mZoneTextEditRowSpan.text())
        mDicUserSettings["zoneConfirmMessage"]      = "true" if self.mZoneConfirmMessage.isChecked() else "false"
        mDicUserSettings["cleanPgDescription"]                = self.zComboCleanPgDescription
        mDicUserSettings["copyDctTitleToPgDescription"]       = "true" if self.mZoneCopyDctTitleToPgDescription.isChecked()       else "false"
        mDicUserSettings["copyDctDescriptionToPgDescription"] = "true" if self.mZoneCopyDctDescriptionToPgDescription.isChecked() else "false"
        #----
        for key, value in mDicUserSettings.items():
            mSettings.setValue(key, value)
        mSettings.endGroup()    
        # liste des Paramétres UTILISATEURS

        zMess, zTitre = QtWidgets.QApplication.translate("colorbloc_ui", "Colors saved.", None), QtWidgets.QApplication.translate("bibli_plume", "Information !!!", None)
        #QMessageBox.information(self, zTitre, zMess) 
        return 

    #==========================         
    #==========================         
    def functionColor(self, mImage, i):
        mColor = mImage.palette().color(QPalette.Window)
        mColorInit = QColor(mColor.name())
        if i == 9 :
           zMess = "%s" %(QtWidgets.QApplication.translate("colorbloc_ui", "Choose a color for the untyped areas.", None) )
        else :    
           zMess = "%s %s" %(QtWidgets.QApplication.translate("colorbloc_ui", "Choose a color for the block : ", None), str(self.dicListLettreLabel[i]) )
        zColor = QColorDialog.getColor(mColorInit, self, zMess)
        if zColor.isValid():
           zStyleBackground = "QLabel { background-color : " + zColor.name() + " }"
           mImage.setStyleSheet(zStyleBackground)
           # --
           self.applyWYSIWYG() #Lecture et apply des variables
           # --
        #For opacity
        if zColor.isValid() and i == 9 :
           self.labelOpacity.setStyleSheet("QLineEdit {  font-family:" + self.policeQGroupBox  +"; background-color:" + zColor.name()  +";}")
        return 
        
    #==========================         
    #==========================         
    def functionResetColor(self, mImage, i, mButtonName):
        listBlocsKey = [
                "QGroupBox",
                "QGroupBoxGroupOfProperties",
                "QGroupBoxGroupOfValues",
                "QGroupBoxTranslationGroup",
                "QTabWidget",
                "QLabelBackGround",
                "geomColor",
                "activeTooltipColorText",
                "activeTooltipColorBackground",
                "opacity"
                ]
        listBlocsValue = [
                "#a38e63",
                "#a38e63",
                "#465f9d",         
                "#e18b76",
                "#cecece",
                "#e3e3fd",   
                "#a38e63",
                "#000000",
                "#fee9e9",
                "#ddddbe"
                ] 
        mDicDashBoard = dict(zip(listBlocsKey, listBlocsValue))
 
        if self.dicListLettre[i] in self.mDic_LH :
           varColor = str( mDicDashBoard[self.dicListLettre[i]] )
           zStyleBackground = "QLabel { background-color : "  + varColor + "; }"
           mImage.setStyleSheet(zStyleBackground)
           # --
           self.applyWYSIWYG() #Lecture et apply des variables
           # --
        #For opacity
        if i == 9 :
           varColor = str( mDicDashBoard[self.dicListLettre[i]] )
           self.labelOpacity.setStyleSheet("QLineEdit {  font-family:" + self.policeQGroupBox  +"; background-color:" + varColor  +";}")
        return                                                     
