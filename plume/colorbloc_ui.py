# (c) Didier  LECLERC 2020 CMSIG MTE-MCTRCT/SG/SNUM/UNI/DRC Site de Rouen
# créé sept 2021

from . import bibli_plume
from .bibli_plume import *
import os.path
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qt import *

from qgis.core import  QgsSettings

class Ui_Dialog_ColorBloc(object):
    def setupUiColorBloc(self, DialogColorBloc):
        self.DialogColorBloc = DialogColorBloc
        self.zMessTitle    =  QtWidgets.QApplication.translate("colorbloc_ui", "Customization of the IHM.", None)
        myPath = os.path.dirname(__file__)+"\\icons\\logo\\plume.svg"

        self.DialogColorBloc.setObjectName("DialogConfirme")
        self.DialogColorBloc.setFixedSize(810,460)
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
        self.mDic_LH = bibli_plume.returnAndSaveDialogParam(self, "Load")
        self.dicListLettre      = { 0:"QTabWidget", 1:"QGroupBox",  2:"QGroupBoxGroupOfProperties",  3:"QGroupBoxGroupOfValues",  4:"QGroupBoxTranslationGroup", 5:"QLabelBackGround"}
        self.dicListLettreLabel = { 0:"Onglet", 1:"Groupe général",  2:"Groupe de propriétés",  3:"Groupe de valeurs",  4:"Groupe de traduction", 5:"Libellé"}
        #========
        self.groupBoxAll = QtWidgets.QGroupBox(self.DialogColorBloc)
        self.groupBoxAll.setGeometry(QtCore.QRect(10,90,self.DialogColorBloc.width() - 20, self.DialogColorBloc.height() - 150))
        self.groupBoxAll.setObjectName("groupBoxAll")
        self.groupBoxAll.setStyleSheet("QGroupBox {   \
                                border-style: dashed; border-width:2px;       \
                                border-color: #958B62;      \
                                font: bold 11px;         \
                                }")

        #---First Plan-------
        button_0, img_0, reset_0 = QtWidgets.QPushButton(self.groupBoxAll), QtWidgets.QLabel(self.groupBoxAll), QtWidgets.QPushButton(self.groupBoxAll)
        self.genereButtonAction(button_0, img_0, reset_0, "button_0", "img_0", "reset_0", 0)
        button_1, img_1, reset_1 = QtWidgets.QPushButton(self.groupBoxAll), QtWidgets.QLabel(self.groupBoxAll), QtWidgets.QPushButton(self.groupBoxAll)
        self.genereButtonAction(button_1, img_1, reset_1, "button_1", "img_1", "reset_1", 1)
        button_2, img_2, reset_2 = QtWidgets.QPushButton(self.groupBoxAll), QtWidgets.QLabel(self.groupBoxAll), QtWidgets.QPushButton(self.groupBoxAll)
        self.genereButtonAction(button_2, img_2, reset_2, "button_2", "img_2", "reset_2", 2)
        #-
        button_3, img_3, reset_3 = QtWidgets.QPushButton(self.groupBoxAll), QtWidgets.QLabel(self.groupBoxAll), QtWidgets.QPushButton(self.groupBoxAll)
        self.genereButtonAction(button_3, img_3, reset_3, "button_3", "img_3", "reset_3", 3)
        button_4, img_4, reset_4 = QtWidgets.QPushButton(self.groupBoxAll), QtWidgets.QLabel(self.groupBoxAll), QtWidgets.QPushButton(self.groupBoxAll)
        self.genereButtonAction(button_4, img_4, reset_4, "button_4", "img_4", "reset_4", 4)
        button_5, img_5, reset_5 = QtWidgets.QPushButton(self.groupBoxAll), QtWidgets.QLabel(self.groupBoxAll), QtWidgets.QPushButton(self.groupBoxAll)
        self.genereButtonAction(button_5, img_5, reset_5, "button_5", "img_5", "reset_5", 5)
        #-
        self.editStyle        = self.mDic_LH["QEdit"]              #style saisie
        self.labelBackGround  = self.mDic_LH["QLabelBackGround"] #QLabel    
        self.epaiQGroupBox    = self.mDic_LH["QGroupBoxEpaisseur"] #épaisseur QGroupBox
        self.lineQGroupBox    = self.mDic_LH["QGroupBoxLine"]    #trait QGroupBox
        self.policeQGroupBox  = self.mDic_LH["QGroupBoxPolice"]  #Police QGroupBox
        self.policeQTabWidget = self.mDic_LH["QTabWidgetPolice"] #Police QTabWidget
        self.ihm              = self.mDic_LH["ihm"]  #window/dock
        self.toolBarDialog    = self.mDic_LH["toolBarDialog"]  #toolBarDialog
        #-
        self.labelQGroupBox = QtWidgets.QLabel(self.DialogColorBloc)
        self.labelQGroupBox.setGeometry(QtCore.QRect(10, 285, 180, 30))
        self.labelQGroupBox.setAlignment(Qt.AlignRight)        
        self.labelQGroupBox.setText("Police :")        
        #-
        self.fontQGroupBox = QtWidgets.QFontComboBox(self.DialogColorBloc)
        self.fontQGroupBox.setGeometry(QtCore.QRect(205, 280, 190, 20))
        self.fontQGroupBox.setObjectName("fontComboBox")         
        self.fontQGroupBox.setCurrentFont(QFont(self.policeQGroupBox))         
        self.fontQGroupBox.currentFontChanged.connect(self.functionFont)
        self.zFontQGroupBox = self.policeQGroupBox  # si ouverture sans chgt et sauve
        #--
        mDicType = {"dashed":"Tirets", "dotted":"Pointillés", "double":"Plein double", "solid":"plein"}
        self.labelTypeLine = QtWidgets.QLabel(self.DialogColorBloc)
        self.labelTypeLine.setGeometry(QtCore.QRect(10, 305, 180, 30))
        self.labelTypeLine.setAlignment(Qt.AlignRight)        
        self.labelTypeLine.setText("Type de trait des cadres :")        
        #--
        self.comboTypeLine = QtWidgets.QComboBox(self.DialogColorBloc)
        self.comboTypeLine.setGeometry(QtCore.QRect(205, 300, 190, 20))
        self.comboTypeLine.setObjectName("groupBoxBar")
        self.comboTypeLine.addItems([ elem for elem in mDicType.values() ])
        self.comboTypeLine.setCurrentText(mDicType[self.lineQGroupBox])         
        self.comboTypeLine.currentTextChanged.connect(lambda : self.functionLine(mDicType))
        self.zLineQGroupBox = self.lineQGroupBox  # si ouverture sans chgt et sauve
        #-
        self.labelBoxEpai = QtWidgets.QLabel(self.DialogColorBloc)
        self.labelBoxEpai.setGeometry(QtCore.QRect(10, 325, 180, 30))
        self.labelBoxEpai.setAlignment(Qt.AlignRight)        
        self.labelBoxEpai.setText("Epaisseur de trait des cadres :")        
        #-
        self.spinBoxEpai = QtWidgets.QDoubleSpinBox(self.DialogColorBloc)
        self.spinBoxEpai.setGeometry(QtCore.QRect(205,320 ,50, 20))
        self.spinBoxEpai.setMaximum(5)
        self.spinBoxEpai.setMinimum(0)
        self.spinBoxEpai.setValue(1)
        self.spinBoxEpai.setSingleStep(1)
        self.spinBoxEpai.setDecimals(0)
        self.spinBoxEpai.setSuffix(" px")
        self.spinBoxEpai.setObjectName("spinBoxEpai")
        self.spinBoxEpai.setValue(float(self.epaiQGroupBox))         
        self.spinBoxEpai.valueChanged.connect(self.functionEpai)
        self.zEpaiQGroupBox = self.epaiQGroupBox  # si ouverture sans chgt et sauve
        #-
        self.zEditStyle = self.editStyle  # si ouverture sans chgt et sauve
        #-
        self.labelWinVsDock = QtWidgets.QLabel(self.DialogColorBloc)
        self.labelWinVsDock.setGeometry(QtCore.QRect(10, 345, 180, 30))
        self.labelWinVsDock.setAlignment(Qt.AlignRight)        
        self.labelWinVsDock.setText("Interface :")        
        #-
        mDicWinVsDock = {"window":"Fenêtre", "dockFalse":"Panneau ancré", "dockTrue":"Panneau flottant"}
        self.comboWinVsDock = QtWidgets.QComboBox(self.DialogColorBloc)
        self.comboWinVsDock.setGeometry(QtCore.QRect(205, 340, 190, 20))
        self.comboWinVsDock.setObjectName("comboWinVsDock")
        self.comboWinVsDock.addItems([ elem for elem in mDicWinVsDock.values() ])
        self.comboWinVsDock.setCurrentText(mDicWinVsDock[self.ihm])         
        self.comboWinVsDock.currentTextChanged.connect(lambda : self.functionWinVsDock(mDicWinVsDock))
        mValueTemp = [ k for k, v in mDicWinVsDock.items() if v == self.comboWinVsDock.currentText()][0]
        self.zComboWinVsDock = mValueTemp  # si ouverture sans chgt et sauve
        #-
        self.labelToolBarDialog = QtWidgets.QLabel(self.DialogColorBloc)
        self.labelToolBarDialog.setGeometry(QtCore.QRect(10, 365, 180, 30))
        self.labelToolBarDialog.setAlignment(Qt.AlignRight)        
        self.labelToolBarDialog.setText("Barre d'outil :")        
        #-
        mDicToolBarDialog = {"button":"Mode 'Bouton'", "picture":"Mode 'Image'"}
        self.comboToolBarDialog = QtWidgets.QComboBox(self.DialogColorBloc)
        self.comboToolBarDialog.setGeometry(QtCore.QRect(205, 360, 190, 20))
        self.comboToolBarDialog.setObjectName("comboToolBarDialog")
        self.comboToolBarDialog.addItems([ elem for elem in mDicToolBarDialog.values() ])
        self.comboToolBarDialog.setCurrentText(mDicToolBarDialog[self.toolBarDialog])         
        self.comboToolBarDialog.currentTextChanged.connect(lambda : self.functionToolBarDialog(mDicToolBarDialog))
        mValueTemp = [ k for k, v in mDicToolBarDialog.items() if v == self.comboToolBarDialog.currentText()][0]
        self.zComboToolBarDialog = mValueTemp  # si ouverture sans chgt et sauve

        #======== wysiwyg
        self.createWYSIWYG()
        #======== wysiwyg

        #========
        self.pushButton = QtWidgets.QPushButton(self.DialogColorBloc)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setGeometry(QtCore.QRect(self.DialogColorBloc.width() / 2 - 100, self.DialogColorBloc.height() - 50, 80, 25))
        self.pushButton.clicked.connect(lambda : self.functionSaveColor())
        #----------
        self.pushButtonAnnuler = QtWidgets.QPushButton(self.DialogColorBloc)
        self.pushButtonAnnuler.setObjectName("pushButtonAnnuler")
        self.pushButtonAnnuler.setGeometry(QtCore.QRect(self.DialogColorBloc.width() / 2 + 20, self.DialogColorBloc.height() - 50, 80, 25))
        self.pushButtonAnnuler.clicked.connect(self.DialogColorBloc.reject)
        #----------
        self.DialogColorBloc.setWindowTitle(QtWidgets.QApplication.translate("plume_main", "PLUME (Metadata storage in PostGreSQL") + "  (" + str(bibli_plume.returnVersion()) + ")")
        self.label_2.setText(QtWidgets.QApplication.translate("colorbloc_ui", self.zMessTitle, None))
        self.pushButton.setText(QtWidgets.QApplication.translate("colorbloc_ui", "OK", None))
        self.pushButtonAnnuler.setText(QtWidgets.QApplication.translate("colorbloc_ui", "Cancel", None))

    #==========================         
    #==========================         
    def functionFont(self):
        self.zFontQGroupBox = self.fontQGroupBox.currentFont().family()
        # --
        self.applyWYSIWYG() #Lecture et apply des variables
        # --
        return 

    #==========================         
    #==========================             
    def functionLine(self, mDicType):
        self.zLineQGroupBox = [ k for k, v in mDicType.items() if v == self.comboTypeLine.currentText()][0]
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
    def functionToolBarDialog(self, mDicWToolBarDialog):
        self.zComboToolBarDialog = [ k for k, v in mDicWToolBarDialog.items() if v == self.comboToolBarDialog.currentText()][0]
        # --
        self.applyWYSIWYG() #Lecture et apply des variables
        # --
        return 

    #==========================         
    #==========================             
    def functionEpai(self):
        self.zEpaiQGroupBox = self.spinBoxEpai.value()
        # --
        self.applyWYSIWYG() #Lecture et apply des variables
        # --
        return 

    #==========================         
    #==========================         
    def createWYSIWYG(self):
        #======== wysiwyg
        self.colorQGroupBox                   = self.mDic_LH["QGroupBox"]                  
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
        #print( [  self.policeQGroupBox, self.lineQGroupBox, self.epaiQGroupBox, self.colorQGroupBox, self.labelBackGround ] )

        #
        self.tabWidgetFalse = QTabWidget(self.DialogColorBloc)
        self.tabWidgetFalse.setObjectName("tabWidget")
        # --
        x, y = self.DialogColorBloc.width() / 2, 100
        larg, haut =  self.DialogColorBloc.width()/2 -20, (self.DialogColorBloc.height() - 170 )
        self.tabWidgetFalse.setGeometry(QtCore.QRect(x, y, larg , haut))
        self.tabWidgetFalse.setStyleSheet("QTabWidget::pane {border: 2px solid " + self.colorQTabWidget  + "; font-family:" + self.policeQGroupBox  +"; } \
                                    QTabBar::tab {border: 1px solid " + self.colorQTabWidget  + "; border-bottom-color: none; font-family:" + self.policeQGroupBox  +";\
                                                    border-top-left-radius: 6px;border-top-right-radius: 6px;\
                                                    width: 160px; padding: 2px;} \
                                      QTabBar::tab:selected {background: qlineargradient(x1: 0, y1: 0, x2: 0.5, y2: 0.5, stop: 0 " + self.colorQTabWidget  + ", stop: 1 white);  font: bold;} \
                                     ")
        #--------------------------
        self.tab_widget_Tab1 = QWidget()
        self.tab_widget_Tab1.setObjectName("tab_widget_Tab1")
        labeltab_widget_Tab1 = QtWidgets.QApplication.translate("colorbloc_ui", "  Onglet 1   ", None)
        self.tabWidgetFalse.addTab(self.tab_widget_Tab1, labeltab_widget_Tab1)
        #--------------------------
        self.tab_widget_Tab2 = QWidget()
        self.tab_widget_Tab2.setObjectName("tab_widget_Tab2")
        labeltab_widget_Tab2 = QtWidgets.QApplication.translate("colorbloc_ui", "  Onglet 2   ", None)
        self.tabWidgetFalse.addTab(self.tab_widget_Tab2, labeltab_widget_Tab2)
        #--------------------------
        self.tabWidgetFalse.setCurrentIndex(0)
       #==========================         
        self.falseGroupBox = QtWidgets.QGroupBox(self.tab_widget_Tab1)
        self.falseGroupBox.setObjectName("falseGroupBox")
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
        self.falseGroupBox.setTitle(self.dicListLettreLabel[1])
        x, y = 5, 5
        larg, haut =  self.tabWidgetFalse.width()- 15, self.tabWidgetFalse.height()-35
        self.falseGroupBox.setGeometry(QtCore.QRect(x, y, larg, haut))
        #------ 
        self.falseGroupBoxProperties = QtWidgets.QGroupBox(self.falseGroupBox)
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
        x, y = 10, 21
        larg, haut =  self.falseGroupBox.width()- 20, self.falseGroupBox.height()/3 - 15
        self.falseGroupBoxProperties.setGeometry(QtCore.QRect(x, y, larg, haut))
        self.falseGroupBoxProperties.setTitle(self.dicListLettreLabel[2]) 
        #------ 
        #------ 
        self.mLabelEdit = QtWidgets.QLabel(self.falseGroupBoxProperties)
        self.mLabelEdit.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        self.mLabelEdit.setGeometry(QtCore.QRect(20, 25, 70, 18))
        self.mLabelEdit.setObjectName("mLabelEdit")
        self.mLabelEdit.setText("Libellé")
        #- 
        self.mzoneEdit = QtWidgets.QLineEdit(self.falseGroupBoxProperties)
        self.mzoneEdit.setStyleSheet("QLineEdit {  font-family:" + self.policeQGroupBox  +"; border-style:" + self.editStyle  +" ; border-width: 0px;}")
        self.mzoneEdit.setGeometry(QtCore.QRect(100, 25, 150, 20))
        self.mzoneEdit.setObjectName("mzoneEdit")
        self.mzoneEdit.setText("Ma saisie des métadonnées")
        #------ 
        #------ 
        self.falseBoxGroupOfValues = QtWidgets.QGroupBox(self.falseGroupBox)
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
        x, y = 10, 100
        larg, haut =  self.falseGroupBox.width()- 20, self.falseGroupBox.height()/3 - 15
        self.falseBoxGroupOfValues.setGeometry(QtCore.QRect(x, y, larg, haut))
        self.falseBoxGroupOfValues.setTitle(self.dicListLettreLabel[3]) 
        #------ 
        #------ 
        self.mLabelText = QtWidgets.QLabel(self.falseBoxGroupOfValues)
        self.mLabelText.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        self.mLabelText.setGeometry(QtCore.QRect(20, 20, 70, 18))
        self.mLabelText.setObjectName("mLabelText")
        self.mLabelText.setText("Libellé")
        #- 
        self.mzoneText = QtWidgets.QTextEdit(self.falseBoxGroupOfValues)
        self.mzoneText.setStyleSheet("QTextEdit {  font-family:" + self.policeQGroupBox  +"; border-style:" + self.editStyle  +" ; border-width: 0px;}")
        self.mzoneText.setGeometry(QtCore.QRect(100, 17, 150, 40))
        self.mzoneText.setObjectName("mzoneText")
        self.mzoneText.setText("Ma saisie des métadonnées\nsur deux lignes")
        #------ 
        #------ 
        self.falseBoxTranslationGroup = QtWidgets.QGroupBox(self.falseGroupBox)
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
        x, y = 10, 180
        larg, haut =  self.falseGroupBox.width()- 20, self.falseGroupBox.height()/3 - 15
        self.falseBoxTranslationGroup.setGeometry(QtCore.QRect(x, y, larg, haut))
        self.falseBoxTranslationGroup.setTitle(self.dicListLettreLabel[4]) 
        return 
        
    #==========================         
    #==========================         
    def applyWYSIWYG(self): 
        mChild_premier = [mObj for mObj in self.groupBoxAll.children()] 
        mLettre, mColorFirst, mDicSaveColor = "", None, {}  
        for mObj in mChild_premier :
            for i in range(7) :
                if mObj.objectName() == "img_" + str(i) :
                   mLettre      = str(self.dicListLettre[i])
                   mColor       = mObj.palette().color(QPalette.Window)
                   mColorFirst  = mColor.name()
                   mDicSaveColor[mLettre] = mColorFirst                                 
                   break
        self.colorQGroupBox                   = mDicSaveColor["QGroupBox"]                  
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
                      

        self.policeQTabWidget = self.mDic_LH["QTabWidgetPolice"] #Police QTabWidget
        #--                
        self.tabWidgetFalse.setStyleSheet("QTabWidget::pane {border: 2px solid " + self.colorQTabWidget  + "; font-family:" + self.policeQGroupBox  +"; } \
                                    QTabBar::tab {border: 1px solid " + self.colorQTabWidget  + "; border-bottom-color: none; font-family:" + self.policeQGroupBox  +";\
                                                    border-top-left-radius: 6px;border-top-right-radius: 6px;\
                                                    width: 160px; padding: 2px;} \
                                      QTabBar::tab:selected {background: qlineargradient(x1: 0, y1: 0, x2: 0.5, y2: 0.5, stop: 0 " + self.colorQTabWidget  + ", stop: 1 white);  font: bold;} \
                                     ")
        #---
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
        self.mzoneEdit.setStyleSheet("QLineEdit {  font-family:" + self.policeQGroupBox  +"; border-style:" + self.editStyle  +" ; border-width: 0px;}")
        self.mzoneText.setStyleSheet("QTextEdit {  font-family:" + self.policeQGroupBox  +"; border-style:" + self.editStyle  +" ; border-width: 0px;}")

        self.mLabelEdit.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.colorQLabel  +";}")
        self.mLabelText.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.colorQLabel  +";}")

        return 

    #==========================         
    #==========================         
    def genereButtonAction(self, mButton, mImage, mReset, mButtonName, mImageName, mResetName, compt):
        for i in range(7) :
            if i <= 7:
               ii = 1
               mX1, mY1 = (ii * 10) +  0,  (i * 30) + 10 
               mX2, mY2 = (ii * 10) + 185, (i * 30) + 10
               mX3, mY3 = (ii * 10) + 230, (i * 30) + 10
               if i == compt : break
 
        #
        mButton.setGeometry(QtCore.QRect(mX1, mY1, 180, 20))
        mButton.setObjectName(mButtonName)
        #mButton.setText(self.dicListBlocs[self.dicListLettreLabel[i]]) if self.dicListLettre[i] in self.dicListBlocs else mButton.setText(self.dicListLettreLabel[i])
        mButton.setText(self.dicListLettreLabel[i])
        #
        mImage.setGeometry(QtCore.QRect(mX2, mY2, 40, 20))
        mImage.setObjectName(mImageName)
        if self.dicListLettre[i] in self.mDic_LH :
           varColor = str( self.mDic_LH[self.dicListLettre[i]] ) 
           zStyleBackground = "QLabel { background-color : "  + varColor + "; }"
           mImage.setStyleSheet(zStyleBackground)
        #
        mReset.setGeometry(QtCore.QRect(mX3, mY3, 40, 20))
        mReset.setObjectName(mResetName)
        mReset.setText("Reset")
        #
        mButton.clicked.connect(lambda : self.functionColor(mImage, i))
        mReset.clicked.connect(lambda : self.functionResetColor(mImage, i, mButtonName))
        
        #Pour masquer les boutons du GrouBox premeir cadre
        if compt == 1 :
           mImage.setVisible(False)
           mButton.setVisible(False)
           mReset.setVisible(False)
        return 

    #==========================         
    #==========================         
    def functionSaveColor(self):
        mSettings = QgsSettings()
        mTitre = QtWidgets.QApplication.translate("colorbloc_ui", "Confirmation", None)
        mLib = QtWidgets.QApplication.translate("colorbloc_ui", "You will save all your changes..", None)
        mLib1 = QtWidgets.QApplication.translate("colorbloc_ui", "Are you sure you want to continue ?", None)

        if QMessageBox.question(None, mTitre, mLib + "<br><br>" + mLib1,QMessageBox.Yes|QMessageBox.No) ==  QMessageBox.Yes :
           mChild_premier = [mObj for mObj in self.groupBoxAll.children()] 

           mLettre, mColorFirst, mDicSaveColor = "", None, {}  
           for mObj in mChild_premier :
               for i in range(7) :
                   if mObj.objectName() == "img_" + str(i) :
                      mLettre      = str(self.dicListLettre[i])
                      mColor       = mObj.palette().color(QPalette.Window)
                      mColorFirst  = mColor.name()
                      mDicSaveColor[mLettre] = mColorFirst
                      break
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
           mDicAutre["toolBarDialog"] = self.zComboToolBarDialog
           mSettings.beginGroup("Generale")
           for key, value in mDicAutre.items():
               mSettings.setValue(key, value)
       
           mSettings.endGroup()    
           zMess, zTitre = QtWidgets.QApplication.translate("colorbloc_ui", "Colors saved.", None), QtWidgets.QApplication.translate("bibli_plume", "Information !!!", None)
           #QMessageBox.information(self, zTitre, zMess) 
        return 

    #==========================         
    #==========================         
    def functionColor(self, mImage, i):
        mColor = mImage.palette().color(QPalette.Window)
        mColorInit = QColor(mColor.name())
        zMess = "%s %s" %(QtWidgets.QApplication.translate("colorbloc_ui", "Choose a color for the block : ", None), str(self.dicListLettreLabel[i]) )
        zColor = QColorDialog.getColor(mColorInit, self, zMess)
        if zColor.isValid():
           zStyleBackground = "QLabel { background-color : " + zColor.name() + " }"
           mImage.setStyleSheet(zStyleBackground)
           # --
           self.applyWYSIWYG() #Lecture et apply des variables
           # --
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
                "QLabelBackGround"
                ]
        listBlocsValue = [
                "#BADCFF",
                "#7560FF",
                "#00FF21",
                "#0026FF",
                "#958B62",
                "#BFEAE2"
                ] 
        mDicDashBoard = dict(zip(listBlocsKey, listBlocsValue))
 
        if self.dicListLettre[i] in self.mDic_LH :
           varColor = str( mDicDashBoard[self.dicListLettre[i]] )
           zStyleBackground = "QLabel { background-color : "  + varColor + "; }"
           mImage.setStyleSheet(zStyleBackground)
           # --
           self.applyWYSIWYG() #Lecture et apply des variables
           # --

        return                                                     