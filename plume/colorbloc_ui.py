# (c) Didier  LECLERC 2020 CMSIG MTE-MCTRCT/SG/SNUM/UNI/DRC Site de Rouen
# créé sept 2021

from . import bibli_plume
from .bibli_plume import *
import os.path
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qt import *
from qgis.gui import QgsDateTimeEdit

from qgis.core import  QgsSettings

class Ui_Dialog_ColorBloc(object):
    def setupUiColorBloc(self, DialogColorBloc):
        self.DialogColorBloc = DialogColorBloc
        self.zMessTitle    =  QtWidgets.QApplication.translate("colorbloc_ui", "User settings / Customization of the IHM.", None)
        myPath = os.path.dirname(__file__)+"\\icons\\logo\\plume.svg"

        self.DialogColorBloc.setObjectName("DialogConfirme")
        self.DialogColorBloc.setFixedSize(900,570)
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
                                                    width: 170px; padding: 2px;} \
                                      QTabBar::tab:selected {background: qlineargradient(x1: 0, y1: 0, x2: 0.5, y2: 0.5, stop: 0 #958B62, stop: 1 white);  font: bold;} \
                                     ")
        #--------------------------
        self.tab_widget_Perso = QWidget()
        self.tab_widget_Perso.setObjectName("tab_widget_Perso")
        labelTab_Perso = QtWidgets.QApplication.translate("colorbloc_ui", "   IHM param   ", None)
        self.tabWidget.addTab(self.tab_widget_Perso,labelTab_Perso)
        #--------------------------
        self.tab_widget_User = QWidget()
        self.tab_widget_User.setObjectName("tab_widget_User")
        labelTab_User = QtWidgets.QApplication.translate("colorbloc_ui", "  User settings  ", None)
        self.tabWidget.addTab(self.tab_widget_User,labelTab_User)
        #Zone Onglets
        #==========================              

        #========
        self.mDic_LH = bibli_plume.returnAndSaveDialogParam(self, "Load")
        self.dicListLettre      = { 0:"QTabWidget", 1:"QGroupBox",  2:"QGroupBoxGroupOfProperties",  3:"QGroupBoxGroupOfValues",  4:"QGroupBoxTranslationGroup", 5:"QLabelBackGround"}
        self.dicListLettreLabel = { 0:"Onglet", 1:"Groupe général",  2:"Groupe de propriétés",  3:"Groupe de valeurs",  4:"Groupe de traduction", 5:"Libellé"}
        #========
        self.groupBoxAll = QtWidgets.QGroupBox(self.tab_widget_Perso)
        self.groupBoxAll.setGeometry(QtCore.QRect(10,10,self.tabWidget.width() - 20, self.tabWidget.height() - 40))
        self.groupBoxAll.setObjectName("groupBoxAll")
        self.groupBoxAll.setStyleSheet("QGroupBox {   \
                                border-style: dashed; border-width:0px;       \
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
        self.labelQGroupBox = QtWidgets.QLabel(self.groupBoxAll)
        self.labelQGroupBox.setGeometry(QtCore.QRect(10, 195, 180, 30))
        self.labelQGroupBox.setAlignment(Qt.AlignRight)        
        self.labelQGroupBox.setText("Police :")        
        #-
        self.fontQGroupBox = QtWidgets.QFontComboBox(self.groupBoxAll)
        self.fontQGroupBox.setGeometry(QtCore.QRect(205, 190, 190, 20))
        self.fontQGroupBox.setObjectName("fontComboBox")         
        self.fontQGroupBox.setCurrentFont(QFont(self.policeQGroupBox))         
        self.fontQGroupBox.currentFontChanged.connect(self.functionFont)
        self.zFontQGroupBox = self.policeQGroupBox  # si ouverture sans chgt et sauve
        #--
        mDicType = {"dashed":"Tirets", "dotted":"Pointillés", "double":"Plein double", "solid":"plein"}
        self.labelTypeLine = QtWidgets.QLabel(self.groupBoxAll)
        self.labelTypeLine.setGeometry(QtCore.QRect(10, 215, 180, 30))
        self.labelTypeLine.setAlignment(Qt.AlignRight)        
        self.labelTypeLine.setText("Type de trait des cadres :")        
        #--
        self.comboTypeLine = QtWidgets.QComboBox(self.groupBoxAll)
        self.comboTypeLine.setGeometry(QtCore.QRect(205, 210, 190, 20))
        self.comboTypeLine.setObjectName("groupBoxBar")
        self.comboTypeLine.addItems([ elem for elem in mDicType.values() ])
        self.comboTypeLine.setCurrentText(mDicType[self.lineQGroupBox])         
        self.comboTypeLine.currentTextChanged.connect(lambda : self.functionLine(mDicType))
        self.zLineQGroupBox = self.lineQGroupBox  # si ouverture sans chgt et sauve
        #-
        self.labelBoxEpai = QtWidgets.QLabel(self.groupBoxAll)
        self.labelBoxEpai.setGeometry(QtCore.QRect(10, 235, 180, 30))
        self.labelBoxEpai.setAlignment(Qt.AlignRight)        
        self.labelBoxEpai.setText("Epaisseur de trait des cadres :")        
        #-
        self.spinBoxEpai = QtWidgets.QDoubleSpinBox(self.groupBoxAll)
        self.spinBoxEpai.setGeometry(QtCore.QRect(205,230 ,50, 20))
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
        self.labelWinVsDock = QtWidgets.QLabel(self.groupBoxAll)
        self.labelWinVsDock.setGeometry(QtCore.QRect(10, 255, 180, 30))
        self.labelWinVsDock.setAlignment(Qt.AlignRight)        
        self.labelWinVsDock.setText("Interface :")        
        #-
        mDicWinVsDock = {"window":"Fenêtre", "dockFalse":"Panneau ancré", "dockTrue":"Panneau flottant"}
        self.comboWinVsDock = QtWidgets.QComboBox(self.groupBoxAll)
        self.comboWinVsDock.setGeometry(QtCore.QRect(205, 250, 190, 20))
        self.comboWinVsDock.setObjectName("comboWinVsDock")
        self.comboWinVsDock.addItems([ elem for elem in mDicWinVsDock.values() ])
        self.comboWinVsDock.setCurrentText(mDicWinVsDock[self.ihm])         
        self.comboWinVsDock.currentTextChanged.connect(lambda : self.functionWinVsDock(mDicWinVsDock))
        mValueTemp = [ k for k, v in mDicWinVsDock.items() if v == self.comboWinVsDock.currentText()][0]
        self.zComboWinVsDock = mValueTemp  # si ouverture sans chgt et sauve
        #-
        self.labelToolBarDialog = QtWidgets.QLabel(self.groupBoxAll)
        self.labelToolBarDialog.setGeometry(QtCore.QRect(10, 275, 180, 30))
        self.labelToolBarDialog.setAlignment(Qt.AlignRight)        
        self.labelToolBarDialog.setText("Barre d'outil :")        
        #-
        mDicToolBarDialog = {"button":"Mode 'Bouton'", "picture":"Mode 'Image'"}
        self.comboToolBarDialog = QtWidgets.QComboBox(self.groupBoxAll)
        self.comboToolBarDialog.setGeometry(QtCore.QRect(205, 270, 190, 20))
        self.comboToolBarDialog.setObjectName("comboToolBarDialog")
        self.comboToolBarDialog.addItems([ elem for elem in mDicToolBarDialog.values() ])
        self.comboToolBarDialog.setCurrentText(mDicToolBarDialog[self.toolBarDialog])         
        self.comboToolBarDialog.currentTextChanged.connect(lambda : self.functionToolBarDialog(mDicToolBarDialog))
        mValueTemp = [ k for k, v in mDicToolBarDialog.items() if v == self.comboToolBarDialog.currentText()][0]
        self.zComboToolBarDialog = mValueTemp  # si ouverture sans chgt et sauve

        #======== wysiwyg
        self.createWYSIWYG()
        #======== wysiwyg
        #======== User Settings
        self.createUserSettings()
        #======== User Settings

        self.labelPushButton = QtWidgets.QLabel(self.DialogColorBloc)
        self.labelPushButton.setObjectName("pushButton")
        self.labelPushButton.setGeometry(QtCore.QRect(self.DialogColorBloc.width() / 2 - 250, self.DialogColorBloc.height() - 30, 500, 25))
        self.labelPushButton.setAlignment(Qt.AlignCenter)        
        self.labelPushButton.setText("<i>Les modifications seront prises en compte au prochain démarrage de Plume.</i>")        
        #--
        self.pushButton = QtWidgets.QPushButton(self.DialogColorBloc)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setGeometry(QtCore.QRect(self.DialogColorBloc.width() / 2 - 100, self.DialogColorBloc.height() - 60, 80, 25))
        self.pushButton.clicked.connect(lambda : self.functionSave())
        #----------
        self.pushButtonAnnuler = QtWidgets.QPushButton(self.DialogColorBloc)
        self.pushButtonAnnuler.setObjectName("pushButtonAnnuler")
        self.pushButtonAnnuler.setGeometry(QtCore.QRect(self.DialogColorBloc.width() / 2 + 20, self.DialogColorBloc.height() - 60, 80, 25))
        self.pushButtonAnnuler.clicked.connect(self.DialogColorBloc.reject)
        #----------
        self.DialogColorBloc.setWindowTitle(QtWidgets.QApplication.translate("plume_main", "PLUME (Metadata storage in PostGreSQL") + "  (" + str(bibli_plume.returnVersion()) + ")")
        self.label_2.setText(QtWidgets.QApplication.translate("colorbloc_ui", self.zMessTitle, None))
        self.pushButton.setText(QtWidgets.QApplication.translate("colorbloc_ui", "OK", None))
        self.pushButtonAnnuler.setText(QtWidgets.QApplication.translate("colorbloc_ui", "Cancel", None))

    #==========================         
    def createUserSettings(self):
        #======== wysiwyg
        # liste des Paramétres UTILISATEURS
        bibli_plume.listUserParam(self)
        # liste des Paramétres UTILISATEURS
        #------
        largeurLabel,  hauteurLabel   = 400, 20 
        largeurSaisie, hauteurSaisie  = 300, 20
        abscisseLabel                 = 20 
        abscisseSaisie                = abscisseLabel + largeurLabel + 10 
        ordonneeLabelSaisie           = 15
        deltaLabelSaisie              = hauteurLabel + 8
        #------
        """ 
        mLabelLanguageText    = QtWidgets.QApplication.translate("colorbloc_ui", "Language", None)
        mLabelLanguageToolTip = QtWidgets.QApplication.translate("colorbloc_ui", "LanguageToolTip", None)
        mLabelLanguage = QtWidgets.QLabel(self.tab_widget_User)
        mLabelLanguage.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        mLabelLanguage.setGeometry(QtCore.QRect(abscisseLabel, ordonneeLabelSaisie, largeurLabel,  hauteurLabel))
        mLabelLanguage.setObjectName("mLabelLanguage")
        mLabelLanguage.setText(mLabelLanguageText)
        mLabelLanguage.setToolTip(mLabelLanguageToolTip)
        mLabelLanguage.setWordWrap(True)
        #- 
        mZoneLanguage = QtWidgets.QLineEdit(self.tab_widget_User)
        #mZoneLanguage.setStyleSheet("QLineEdit {  font-family:" + self.policeQGroupBox  +"; border-style:" + self.editStyle  +" ; border-width: 0px;}")
        mZoneLanguage.setStyleSheet("QLineEdit {  font-family:" + self.policeQGroupBox  +";}")
        mZoneLanguage.setGeometry(QtCore.QRect(abscisseSaisie, ordonneeLabelSaisie, 50, hauteurSaisie))
        mZoneLanguage.setObjectName("mZoneLanguage")
        mZoneLanguage.setText(self.language)
        mZoneLanguage.setToolTip(mLabelLanguageToolTip)
        """ 
        #------ 
        #ordonneeLabelSaisie += deltaLabelSaisie
        mLabelLangListText    = QtWidgets.QApplication.translate("colorbloc_ui", "LangList", None)
        mLabelLangListToolTip = QtWidgets.QApplication.translate("colorbloc_ui", "LangListToolTip", None)
        mLabelLangList = QtWidgets.QLabel(self.tab_widget_User)
        mLabelLangList.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        mLabelLangList.setGeometry(QtCore.QRect(abscisseLabel, ordonneeLabelSaisie, largeurLabel,  hauteurLabel))
        mLabelLangList.setObjectName("mLabelLangList")
        mLabelLangList.setText(mLabelLangListText)
        mLabelLangList.setToolTip(mLabelLangListToolTip)
        mLabelLangList.setWordWrap(True)
        #- 
        mZoneLangList = QtWidgets.QLineEdit(self.tab_widget_User)
        mZoneLangList.setStyleSheet("QLineEdit {  font-family:" + self.policeQGroupBox  +";}")
        mZoneLangList.setGeometry(QtCore.QRect(abscisseSaisie, ordonneeLabelSaisie, largeurSaisie, hauteurSaisie))
        mZoneLangList.setObjectName("mZoneLangList")
        mZoneLangList.setText(",".join(self.langList))
        mZoneLangList.setToolTip(mLabelLangListToolTip)
        #------ 
        """ 
        ordonneeLabelSaisie += deltaLabelSaisie
        mLabelTranslationText    = QtWidgets.QApplication.translate("colorbloc_ui", "Translation", None)
        mLabelTranslationToolTip = QtWidgets.QApplication.translate("colorbloc_ui", "TranslationToolTip", None)
        mLabelTranslation = QtWidgets.QLabel(self.tab_widget_User)
        mLabelTranslation.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        mLabelTranslation.setGeometry(QtCore.QRect(abscisseLabel, ordonneeLabelSaisie, largeurLabel,  hauteurLabel))
        mLabelTranslation.setObjectName("mLabelTranslation")
        mLabelTranslation.setText(mLabelTranslationText)
        mLabelTranslation.setToolTip(mLabelTranslationToolTip)
        mLabelTranslation.setWordWrap(True)
        #- 
        mZoneTranslation = QtWidgets.QCheckBox(self.tab_widget_User)
        mZoneTranslation.setStyleSheet("QCheckBox {  font-family:" + self.policeQGroupBox  +";}")
        mZoneTranslation.setGeometry(QtCore.QRect(abscisseSaisie, ordonneeLabelSaisie, 18, hauteurSaisie))
        mZoneTranslation.setObjectName("mZoneTranslation")
        mZoneTranslation.setChecked(True if self.initTranslation == 'true' else False)
        mZoneTranslation.setToolTip(mLabelTranslationToolTip)
        """ 
        #------ 
        #hauteurLabel     = 40 
        #------ 
        ordonneeLabelSaisie += deltaLabelSaisie
        mLabelGeoideJSONText    = QtWidgets.QApplication.translate("colorbloc_ui", "GeoideJSON", None)
        mLabelGeoideJSONToolTip = QtWidgets.QApplication.translate("colorbloc_ui", "GeoideJSONToolTip", None)
        mLabelGeoideJSON = QtWidgets.QLabel(self.tab_widget_User)
        mLabelGeoideJSON.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        mLabelGeoideJSON.setGeometry(QtCore.QRect(abscisseLabel, ordonneeLabelSaisie, largeurLabel,  hauteurLabel))
        mLabelGeoideJSON.setObjectName("mLabelGeoideJSON")
        mLabelGeoideJSON.setText(mLabelGeoideJSONText)
        mLabelGeoideJSON.setToolTip(mLabelGeoideJSONToolTip)
        mLabelGeoideJSON.setWordWrap(True)
        #- 
        mZoneGeoideJSON = QtWidgets.QCheckBox(self.tab_widget_User)
        mZoneGeoideJSON.setStyleSheet("QCheckBox {  font-family:" + self.policeQGroupBox  +";}")
        mZoneGeoideJSON.setGeometry(QtCore.QRect(abscisseSaisie, ordonneeLabelSaisie, 18, hauteurSaisie))
        mZoneGeoideJSON.setObjectName("mZoneGeoideJSON")
        mZoneGeoideJSON.setChecked(True if self.geoideJSON else False)
        mZoneGeoideJSON.setToolTip(mLabelGeoideJSONToolTip)
        #------ 
        deltaLabelSaisie = hauteurLabel + 8
        ordonneeLabelSaisie += deltaLabelSaisie
        mLabelPreferedTemplateText    = QtWidgets.QApplication.translate("colorbloc_ui", "PreferedTemplate", None)
        mLabelPreferedTemplateToolTip = QtWidgets.QApplication.translate("colorbloc_ui", "PreferedTemplateToolTip", None)
        mLabelPreferedTemplate = QtWidgets.QLabel(self.tab_widget_User)
        mLabelPreferedTemplate.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        mLabelPreferedTemplate.setGeometry(QtCore.QRect(abscisseLabel, ordonneeLabelSaisie, largeurLabel,  hauteurLabel))
        mLabelPreferedTemplate.setObjectName("mLabelPreferedTemplate")
        mLabelPreferedTemplate.setText(mLabelPreferedTemplateText)
        mLabelPreferedTemplate.setToolTip(mLabelPreferedTemplateToolTip)
        mLabelPreferedTemplate.setWordWrap(True)
        #- 
        mZonePreferedTemplate = QtWidgets.QLineEdit(self.tab_widget_User)
        #mZonePreferedTemplate.setStyleSheet("QLineEdit {  font-family:" + self.policeQGroupBox  +"; border-style:" + self.editStyle  +" ; border-width: 0px;}")
        mZonePreferedTemplate.setStyleSheet("QLineEdit {  font-family:" + self.policeQGroupBox  +";}")
        mZonePreferedTemplate.setGeometry(QtCore.QRect(abscisseSaisie, ordonneeLabelSaisie, largeurSaisie, hauteurSaisie))
        mZonePreferedTemplate.setObjectName("mZonePreferedTemplate")
        mZonePreferedTemplate.setText(self.preferedTemplate)
        mZonePreferedTemplate.setToolTip(mLabelPreferedTemplateToolTip)
        #------ 
        ordonneeLabelSaisie += deltaLabelSaisie
        mLabelEnforcePreferedTemplateText    = QtWidgets.QApplication.translate("colorbloc_ui", "EnforcePreferedTemplate", None)
        mLabelEnforcePreferedTemplateToolTip = QtWidgets.QApplication.translate("colorbloc_ui", "EnforcePreferedTemplateToolTip", None)
        mLabelEnforcePreferedTemplate = QtWidgets.QLabel(self.tab_widget_User)
        mLabelEnforcePreferedTemplate.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        mLabelEnforcePreferedTemplate.setGeometry(QtCore.QRect(abscisseLabel, ordonneeLabelSaisie, largeurLabel,  hauteurLabel))
        mLabelEnforcePreferedTemplate.setObjectName("mLabelEnforcePreferedTemplate")
        mLabelEnforcePreferedTemplate.setText(mLabelEnforcePreferedTemplateText)
        mLabelEnforcePreferedTemplate.setToolTip(mLabelEnforcePreferedTemplateToolTip)
        mLabelEnforcePreferedTemplate.setWordWrap(True)
        #- 
        mZoneEnforcePreferedTemplate = QtWidgets.QCheckBox(self.tab_widget_User)
        mZoneEnforcePreferedTemplate.setStyleSheet("QCheckBox {  font-family:" + self.policeQGroupBox  +";}")
        mZoneEnforcePreferedTemplate.setGeometry(QtCore.QRect(abscisseSaisie, ordonneeLabelSaisie, 18, hauteurSaisie))
        mZoneEnforcePreferedTemplate.setObjectName("mZoneEnforcePreferedTemplate")
        mZoneEnforcePreferedTemplate.setTristate(True)
        mZoneEnforcePreferedTemplate.setCheckState((Qt.Checked if self.enforcePreferedTemplate else Qt.Unchecked) if self.enforcePreferedTemplate != None else Qt.PartiallyChecked)
        mZoneEnforcePreferedTemplate.setToolTip(mLabelEnforcePreferedTemplateToolTip)
        #------ 
        ordonneeLabelSaisie += deltaLabelSaisie
        mLabelReadHideBlankText    = QtWidgets.QApplication.translate("colorbloc_ui", "ReadHideBlank", None)
        mLabelReadHideBlankToolTip = QtWidgets.QApplication.translate("colorbloc_ui", "ReadHideBlankToolTip", None)
        mLabelReadHideBlank = QtWidgets.QLabel(self.tab_widget_User)
        mLabelReadHideBlank.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        mLabelReadHideBlank.setGeometry(QtCore.QRect(abscisseLabel, ordonneeLabelSaisie, largeurLabel,  hauteurLabel))
        mLabelReadHideBlank.setObjectName("mLabelReadHideBlank")
        mLabelReadHideBlank.setText(mLabelReadHideBlankText)
        mLabelReadHideBlank.setToolTip(mLabelReadHideBlankToolTip)
        mLabelReadHideBlank.setWordWrap(True)
        #- 
        mZoneReadHideBlank = QtWidgets.QCheckBox(self.tab_widget_User)
        mZoneReadHideBlank.setStyleSheet("QCheckBox {  font-family:" + self.policeQGroupBox  +";}")
        mZoneReadHideBlank.setGeometry(QtCore.QRect(abscisseSaisie, ordonneeLabelSaisie, 18, hauteurSaisie))
        mZoneReadHideBlank.setObjectName("mZoneReadHideBlank")
        mZoneReadHideBlank.setTristate(True)
        mZoneReadHideBlank.setCheckState((Qt.Checked if self.readHideBlank else Qt.Unchecked) if self.readHideBlank != None else Qt.PartiallyChecked)
        mZoneReadHideBlank.setToolTip(mLabelReadHideBlankToolTip)
        #------
        #seconde colonne 
        #largeurLabel,  hauteurLabel   = 330, 18 
        #largeurSaisie, hauteurSaisie  = 20, 20
        #abscisseLabel                 = 200 + abscisseSaisie + largeurSaisie 
        #abscisseSaisie                = abscisseLabel + largeurLabel + 10 
        #ordonneeLabelSaisie           = 15
        #deltaLabelSaisie              = hauteurLabel + 8
        #------
        ordonneeLabelSaisie += deltaLabelSaisie
        mLabelReadHideUnlistedText    = QtWidgets.QApplication.translate("colorbloc_ui", "ReadHideUnlisted", None)
        mLabelReadHideUnlistedToolTip = QtWidgets.QApplication.translate("colorbloc_ui", "ReadHideUnlistedToolTip", None)
        mLabelReadHideUnlisted = QtWidgets.QLabel(self.tab_widget_User)
        mLabelReadHideUnlisted.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        mLabelReadHideUnlisted.setGeometry(QtCore.QRect(abscisseLabel, ordonneeLabelSaisie, largeurLabel,  hauteurLabel))
        mLabelReadHideUnlisted.setObjectName("mLabelReadHideUnlisted")
        mLabelReadHideUnlisted.setText(mLabelReadHideUnlistedText)
        mLabelReadHideUnlisted.setToolTip(mLabelReadHideUnlistedToolTip)
        mLabelReadHideUnlisted.setWordWrap(True)
        #- 
        mZoneReadHideUnlisted = QtWidgets.QCheckBox(self.tab_widget_User)
        mZoneReadHideUnlisted.setStyleSheet("QCheckBox {  font-family:" + self.policeQGroupBox  +";}")
        mZoneReadHideUnlisted.setGeometry(QtCore.QRect(abscisseSaisie, ordonneeLabelSaisie, 18, hauteurSaisie))
        mZoneReadHideUnlisted.setObjectName("mZoneReadHideUnlisted")
        mZoneReadHideUnlisted.setTristate(True)
        mZoneReadHideUnlisted.setCheckState((Qt.Checked if self.readHideUnlisted else Qt.Unchecked) if self.readHideUnlisted != None else Qt.PartiallyChecked)
        mZoneReadHideUnlisted.setToolTip(mLabelReadHideUnlistedToolTip)
        #------ 
        ordonneeLabelSaisie += deltaLabelSaisie
        mLabelEditHideUnlistedText    = QtWidgets.QApplication.translate("colorbloc_ui", "EditHideUnlisted", None)
        mLabelEditHideUnlistedToolTip = QtWidgets.QApplication.translate("colorbloc_ui", "EditHideUnlistedToolTip", None)
        mLabelEditHideUnlisted = QtWidgets.QLabel(self.tab_widget_User)
        mLabelEditHideUnlisted.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        mLabelEditHideUnlisted.setGeometry(QtCore.QRect(abscisseLabel, ordonneeLabelSaisie, largeurLabel,  hauteurLabel))
        mLabelEditHideUnlisted.setObjectName("mLabelEditHideUnlisted")
        mLabelEditHideUnlisted.setText(mLabelEditHideUnlistedText)
        mLabelEditHideUnlisted.setToolTip(mLabelEditHideUnlistedToolTip)
        mLabelEditHideUnlisted.setWordWrap(True)
        #- 
        mZoneEditHideUnlisted = QtWidgets.QCheckBox(self.tab_widget_User)
        mZoneEditHideUnlisted.setStyleSheet("QCheckBox {  font-family:" + self.policeQGroupBox  +";}")
        mZoneEditHideUnlisted.setGeometry(QtCore.QRect(abscisseSaisie, ordonneeLabelSaisie, 18, hauteurSaisie))
        mZoneEditHideUnlisted.setObjectName("mZoneEditHideUnlisted")
        mZoneEditHideUnlisted.setTristate(True)
        mZoneEditHideUnlisted.setCheckState((Qt.Checked if self.editHideUnlisted else Qt.Unchecked) if self.editHideUnlisted != None else Qt.PartiallyChecked)
        mZoneEditHideUnlisted.setToolTip(mLabelEditHideUnlistedToolTip)
        #------ 
        #hauteurLabel      = 40 
        ordonneeLabelSaisie += deltaLabelSaisie
        mLabelreadOnlyCurrentLanguageText    = QtWidgets.QApplication.translate("colorbloc_ui", "ReadOnlyCurrentLanguage", None)
        mLabelreadOnlyCurrentLanguageToolTip = QtWidgets.QApplication.translate("colorbloc_ui", "ReadOnlyCurrentLanguageToolTip", None)
        mLabelreadOnlyCurrentLanguage = QtWidgets.QLabel(self.tab_widget_User)
        mLabelreadOnlyCurrentLanguage.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        mLabelreadOnlyCurrentLanguage.setGeometry(QtCore.QRect(abscisseLabel, ordonneeLabelSaisie, largeurLabel,  hauteurLabel))
        mLabelreadOnlyCurrentLanguage.setObjectName("mLabelreadOnlyCurrentLanguage")
        mLabelreadOnlyCurrentLanguage.setText(mLabelreadOnlyCurrentLanguageText)
        mLabelreadOnlyCurrentLanguage.setToolTip(mLabelreadOnlyCurrentLanguageToolTip)
        mLabelreadOnlyCurrentLanguage.setWordWrap(True)
        #- 
        mZonereadOnlyCurrentLanguage = QtWidgets.QCheckBox(self.tab_widget_User)
        mZonereadOnlyCurrentLanguage.setStyleSheet("QCheckBox {  font-family:" + self.policeQGroupBox  +";}")
        mZonereadOnlyCurrentLanguage.setGeometry(QtCore.QRect(abscisseSaisie, ordonneeLabelSaisie, 18, hauteurSaisie))
        mZonereadOnlyCurrentLanguage.setObjectName("mZonereadOnlyCurrentLanguage")
        mZonereadOnlyCurrentLanguage.setTristate(True)
        mZonereadOnlyCurrentLanguage.setCheckState((Qt.Checked if self.readOnlyCurrentLanguage else Qt.Unchecked) if self.readOnlyCurrentLanguage != None else Qt.PartiallyChecked)
        mZonereadOnlyCurrentLanguage.setToolTip(mLabelreadOnlyCurrentLanguageToolTip)
        #------ 
        #deltaLabelSaisie = hauteurLabel + 8
        ordonneeLabelSaisie += deltaLabelSaisie
        mLabelEditOnlyCurrentLanguageText    = QtWidgets.QApplication.translate("colorbloc_ui", "EditOnlyCurrentLanguage", None)
        mLabelEditOnlyCurrentLanguageToolTip = QtWidgets.QApplication.translate("colorbloc_ui", "EditOnlyCurrentLanguageToolTip", None)
        mLabelEditOnlyCurrentLanguage = QtWidgets.QLabel(self.tab_widget_User)
        mLabelEditOnlyCurrentLanguage.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        mLabelEditOnlyCurrentLanguage.setGeometry(QtCore.QRect(abscisseLabel, ordonneeLabelSaisie, largeurLabel,  hauteurLabel))
        mLabelEditOnlyCurrentLanguage.setObjectName("mLabelEditOnlyCurrentLanguage")
        mLabelEditOnlyCurrentLanguage.setText(mLabelEditOnlyCurrentLanguageText)
        mLabelEditOnlyCurrentLanguage.setToolTip(mLabelEditOnlyCurrentLanguageToolTip)
        mLabelEditOnlyCurrentLanguage.setWordWrap(True)
        #- 
        mZoneEditOnlyCurrentLanguage = QtWidgets.QCheckBox(self.tab_widget_User)
        mZoneEditOnlyCurrentLanguage.setStyleSheet("QCheckBox {  font-family:" + self.policeQGroupBox  +";}")
        mZoneEditOnlyCurrentLanguage.setGeometry(QtCore.QRect(abscisseSaisie, ordonneeLabelSaisie, 18, hauteurSaisie))
        mZoneEditOnlyCurrentLanguage.setObjectName("mZoneEditOnlyCurrentLanguage")
        mZoneEditOnlyCurrentLanguage.setTristate(True)
        mZoneEditOnlyCurrentLanguage.setCheckState((Qt.Checked if self.editOnlyCurrentLanguage else Qt.Unchecked) if self.editOnlyCurrentLanguage != None else Qt.PartiallyChecked)
        mZoneEditOnlyCurrentLanguage.setToolTip(mLabelEditOnlyCurrentLanguageToolTip)
        #------ 
        largeurSaisie = 40
        ordonneeLabelSaisie += deltaLabelSaisie
        mLabelLabelLengthLimitText    = QtWidgets.QApplication.translate("colorbloc_ui", "LabelLengthLimit", None)
        mLabelLabelLengthLimitToolTip = QtWidgets.QApplication.translate("colorbloc_ui", "LabelLengthLimitToolTip", None)
        mLabelLabelLengthLimit = QtWidgets.QLabel(self.tab_widget_User)
        mLabelLabelLengthLimit.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        mLabelLabelLengthLimit.setGeometry(QtCore.QRect(abscisseLabel, ordonneeLabelSaisie, largeurLabel,  hauteurLabel))
        mLabelLabelLengthLimit.setObjectName("mLabelLabelLengthLimit")
        mLabelLabelLengthLimit.setText(mLabelLabelLengthLimitText)
        mLabelLabelLengthLimit.setToolTip(mLabelLabelLengthLimitToolTip)
        mLabelLabelLengthLimit.setWordWrap(True)
        #- 
        mZoneLabelLengthLimit = QtWidgets.QLineEdit(self.tab_widget_User)
        #mZoneLabelLengthLimit.setStyleSheet("QLineEdit {  font-family:" + self.policeQGroupBox  +"; border-style:" + self.editStyle  +" ; border-width: 0px;}")
        mZoneLabelLengthLimit.setStyleSheet("QLineEdit {  font-family:" + self.policeQGroupBox  +";}")
        mZoneLabelLengthLimit.setGeometry(QtCore.QRect(abscisseSaisie, ordonneeLabelSaisie, largeurSaisie, hauteurSaisie))
        mZoneLabelLengthLimit.setObjectName("mZoneLabelLengthLimit")
        mZoneLabelLengthLimit.setText(str(self.labelLengthLimit))
        mZoneLabelLengthLimit.setInputMask("99999")
        mZoneLabelLengthLimit.setCursorPosition(0)
        mZoneLabelLengthLimit.setToolTip(mLabelLabelLengthLimitToolTip)
        #------ 
        ordonneeLabelSaisie += deltaLabelSaisie
        mLabelValueLengthLimitText    = QtWidgets.QApplication.translate("colorbloc_ui", "ValueLengthLimit", None)
        mLabelValueLengthLimitToolTip = QtWidgets.QApplication.translate("colorbloc_ui", "ValueLengthLimitToolTip", None)
        mLabelValueLengthLimit = QtWidgets.QLabel(self.tab_widget_User)
        mLabelValueLengthLimit.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        mLabelValueLengthLimit.setGeometry(QtCore.QRect(abscisseLabel, ordonneeLabelSaisie, largeurLabel,  hauteurLabel))
        mLabelValueLengthLimit.setObjectName("mLabelValueLengthLimit")
        mLabelValueLengthLimit.setText(mLabelValueLengthLimitText)
        mLabelValueLengthLimit.setToolTip(mLabelValueLengthLimitToolTip)
        mLabelValueLengthLimit.setWordWrap(True)
        #- 
        mZoneValueLengthLimit = QtWidgets.QLineEdit(self.tab_widget_User)
        #mZoneValueLengthLimit.setStyleSheet("QLineEdit {  font-family:" + self.policeQGroupBox  +"; border-style:" + self.editStyle  +" ; border-width: 0px;}")
        mZoneValueLengthLimit.setStyleSheet("QLineEdit {  font-family:" + self.policeQGroupBox  +";}")
        mZoneValueLengthLimit.setGeometry(QtCore.QRect(abscisseSaisie, ordonneeLabelSaisie, largeurSaisie, hauteurSaisie))
        mZoneValueLengthLimit.setObjectName("mZoneValueLengthLimit")
        mZoneValueLengthLimit.setText(str(self.valueLengthLimit))
        mZoneValueLengthLimit.setInputMask("99999")
        mZoneValueLengthLimit.setCursorPosition(0)
        mZoneValueLengthLimit.setToolTip(mLabelValueLengthLimitToolTip)
        #------ 
        ordonneeLabelSaisie += deltaLabelSaisie
        mLabelTextEditRowSpanText    = QtWidgets.QApplication.translate("colorbloc_ui", "TextEditRowSpan", None)
        mLabelTextEditRowSpanToolTip = QtWidgets.QApplication.translate("colorbloc_ui", "TextEditRowSpanToolTip", None)
        mLabelTextEditRowSpan = QtWidgets.QLabel(self.tab_widget_User)
        mLabelTextEditRowSpan.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        mLabelTextEditRowSpan.setGeometry(QtCore.QRect(abscisseLabel, ordonneeLabelSaisie, largeurLabel,  hauteurLabel))
        mLabelTextEditRowSpan.setObjectName("mLabelTextEditRowSpan")
        mLabelTextEditRowSpan.setText(mLabelTextEditRowSpanText)
        mLabelTextEditRowSpan.setToolTip(mLabelTextEditRowSpanToolTip)
        mLabelTextEditRowSpan.setWordWrap(True)
        #- 
        mZoneTextEditRowSpan = QtWidgets.QLineEdit(self.tab_widget_User)
        #mZoneTextEditRowSpan.setStyleSheet("QLineEdit {  font-family:" + self.policeQGroupBox  +"; border-style:" + self.editStyle  +" ; border-width: 0px;}")
        mZoneTextEditRowSpan.setStyleSheet("QLineEdit {  font-family:" + self.policeQGroupBox  +";}")
        mZoneTextEditRowSpan.setGeometry(QtCore.QRect(abscisseSaisie, ordonneeLabelSaisie, largeurSaisie, hauteurSaisie))
        mZoneTextEditRowSpan.setObjectName("mZoneTextEditRowSpan")
        mZoneTextEditRowSpan.setText(str(self.textEditRowSpan))
        mZoneTextEditRowSpan.setCursorPosition(0)
        mZoneTextEditRowSpan.setInputMask("99999")
        mZoneTextEditRowSpan.setToolTip(mLabelTextEditRowSpanToolTip)

        self.mZoneLangList, self.mZoneGeoideJSON, self.mZonePreferedTemplate, self.mZoneEnforcePreferedTemplate, self.mZoneReadHideBlank, self.mZoneReadHideUnlisted, self.mZoneEditHideUnlisted, self.mZonereadOnlyCurrentLanguage, self.mZoneEditOnlyCurrentLanguage, self.mZoneLabelLengthLimit, self.mZoneValueLengthLimit, self.mZoneTextEditRowSpan = \
        mZoneLangList, mZoneGeoideJSON, mZonePreferedTemplate, mZoneEnforcePreferedTemplate, mZoneReadHideBlank, mZoneReadHideUnlisted, mZoneEditHideUnlisted, mZonereadOnlyCurrentLanguage, mZoneEditOnlyCurrentLanguage, mZoneLabelLengthLimit, mZoneValueLengthLimit, mZoneTextEditRowSpan 
        return 

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
        _thesaurus = ['', 'Agriculture, pêche, sylviculture et alimentation', 'Économie et finances', 'Éducation, culture et sport', 'Énergie', 'Environnement', 'Gouvernement et secteur public', 'Justice, système juridique et sécurité publique', 'Population et société', 'Questions internationales', 'Régions et villes', 'Santé', 'Science et technologie', 'Transports']
        _thesaurus2 = ['', 'Adresses', 'Altitude', 'Bâtiments', 'Caractéristiques géographiques météorologiques', 'Caractéristiques géographiques océanographiques', 'Conditions atmosphériques', 'Dénominations géographiques', 'Géologie', 'Habitats et biotopes', 'Hydrographie', 'Installations agricoles et aquacoles', 'Installations de suivi environnemental', 'Lieux de production et sites industriels', 'Occupation des terres', 'Ortho-imagerie', 'Parcelles cadastrales', 'Référentiels de coordonnées', 'Régions biogéographiques', 'Régions maritimes', 'Répartition de la population — démographie', 'Répartition des espèces', 'Réseaux de transport', 'Ressources minérales', 'Santé et sécurité des personnes', "Services d'utilité publique et services publics", 'Sites protégés', 'Sols', "Sources d'énergie", 'Systèmes de maillage géographique', 'Unités administratives', 'Unités statistiques', 'Usage des sols', 'Zones à risque naturel', 'Zones de gestion']

        _pathIcons = os.path.dirname(__file__) + "/icons/buttons"
        _iconQComboBox             = _pathIcons + "/dropDownArrow.png"
        _iconQComboBox = _iconQComboBox.replace("\\","/")
        _iconSources               = _pathIcons + "/source_button.svg"
        _iconSourcesSelect         = _pathIcons + "/source_button.png"
        _iconSourcesVierge         = _pathIcons + "/vierge.png"
        _iconPlus                  = _pathIcons + "/plus_button.svg"
        _iconPlusTempGoValues      = _pathIcons + "/color_button_Plus_GoValues_ForVisu.svg"
        _iconPlusTempTgroup        = _pathIcons + "/color_button_Plus_Tgroup_ForVisu.svg"
        _iconMinus                 = _pathIcons + "/minus_button.svg"
        _iconMinusTempGoValues     = _pathIcons + "/color_button_Minus_GoValues_ForVisu.svg"
        _iconMinusTempTgroup       = _pathIcons + "/color_button_Minus_Tgroup_ForVisu.svg"
        _mListeIconsButtonPlusMinus = [ _iconPlusTempGoValues,  _iconPlusTempTgroup, \
                                        _iconMinusTempGoValues, _iconMinusTempTgroup ]
        #
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
        self.writeColorIconForVisu(_iconPlus, _iconMinus, _mListeIconsButtonPlusMinus) 

        #
        self.tabWidgetFalse = QTabWidget(self.groupBoxAll)
        self.tabWidgetFalse.setObjectName("tabWidget")
        # --
        x, y = (self.tabWidget.width() / 2) - 30, 5
        larg, haut =  self.tabWidget.width()/2 + 10 , (self.tabWidget.height() - 50 )
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
        #self.falseGroupBox.setTitle(self.dicListLettreLabel[1]) # "Enlève Groupe Général"
        x, y = 5, 5
        larg, haut =  self.tabWidgetFalse.width()- 15, self.tabWidgetFalse.height()-40
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
        x, y = 10, 5
        larg, haut =  self.falseGroupBox.width()- 20, self.falseGroupBox.height()/3 - 15
        self.falseGroupBoxProperties.setGeometry(QtCore.QRect(x, y, larg, haut))
        self.falseGroupBoxProperties.setTitle(self.dicListLettreLabel[2]) 
        #------ 
        #------ 
        self.mLabelEdit = QtWidgets.QLabel(self.falseGroupBoxProperties)
        self.mLabelEdit.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        self.mLabelEdit.setGeometry(QtCore.QRect(20, 25, 120, 18))
        self.mLabelEdit.setObjectName("mLabelEdit")
        self.mLabelEdit.setText("Rectangle d'emprise")
        #- 
        self.mzoneEdit = QtWidgets.QLineEdit(self.falseGroupBoxProperties)
        self.mzoneEdit.setStyleSheet("QLineEdit {  font-family:" + self.policeQGroupBox  +"; border-style:" + self.editStyle  +" ; border-width: 0px;}")
        self.mzoneEdit.setGeometry(QtCore.QRect(150, 25, 250, 20))
        self.mzoneEdit.setObjectName("mzoneEdit")
        self.mzoneEdit.setText("POLYGON((2.46962285 48.81560897,2.46962285 48.90165328,2.22396016 48.90165328,2.22396016 48.81560897,2.46962285 48.81560897))")
        self.mzoneEdit.setAlignment(Qt.AlignLeft)
        self.mzoneEdit.setCursorPosition(0)
        #------ 
        self.mLabelDate = QtWidgets.QLabel(self.falseGroupBoxProperties)
        self.mLabelDate.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.labelBackGround  +";}")
        self.mLabelDate.setGeometry(QtCore.QRect(20, 50, 120, 18))
        self.mLabelDate.setObjectName("mLabelEdit")
        self.mLabelDate.setText("Date de création")
        #- 
        self.mzoneDate = QgsDateTimeEdit(self.falseGroupBoxProperties)
        self.mzoneDate.setStyleSheet("QgsDateTimeEdit {  font-family:" + self.policeQGroupBox  +"; }")
        self.mzoneDate.setObjectName("mzoneDate")
        _displayFormat = 'dd/MM/yyyy'
        self.mzoneDate.setDisplayFormat(_displayFormat)
        self.mzoneDate.setDate(QDate.currentDate())
        self.mzoneDate.setMinimumWidth(112)
        self.mzoneDate.setMaximumWidth(112)
        self.mzoneDate.setCalendarPopup(True)
        self.mzoneDate.setGeometry(QtCore.QRect(150, 50, 150, 20))
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
        larg, haut =  self.falseGroupBox.width()- 20, self.falseGroupBox.height()/3 + 0
        self.falseBoxGroupOfValues.setGeometry(QtCore.QRect(x, y, larg, haut))
        self.falseBoxGroupOfValues.setTitle(self.dicListLettreLabel[3]) 
        #------------------------
        """ 
        self.mzoneText = QtWidgets.QTextEdit(self.falseBoxGroupOfValues)
        self.mzoneText.setStyleSheet("QTextEdit {  font-family:" + self.policeQGroupBox  +"; border-style:" + self.editStyle  +" ; border-width: 0px;}")
        self.mzoneText.setGeometry(QtCore.QRect(20, 17, 260, 23))
        self.mzoneText.setObjectName("mzoneText")
        self.mzoneText.setText("ZAC")
        """ 
        self.mzoneTextCombo = QtWidgets.QComboBox(self.falseBoxGroupOfValues)
        self.mzoneTextCombo.setStyleSheet("QComboBox {  font-family:" + self.policeQGroupBox  +"; border-style:" + self.editStyle  + " ; border-width: 0px;} \
                                        QComboBox::drop-down {border: 0px;}\
                                        QComboBox::down-arrow {image: url(" + _iconQComboBox + ");position:absolute; left : 5px;width: 12px;height: 45px;}") 
        self.mzoneTextCombo.setGeometry(QtCore.QRect(20, 17, 260, 23))
        self.mzoneTextCombo.setObjectName("mzoneTextCombo")
        self.mzoneTextCombo.addItems(_thesaurus)
        self.mzoneTextCombo.setCurrentText("Agriculture, pêche, sylviculture et alimentation") 
        self.mzoneTextCombo.setEditable(True)
        mCompleter = QCompleter(_thesaurus, self)
        mCompleter.setCaseSensitivity(Qt.CaseInsensitive)
        self.mzoneTextCombo.setCompleter(mCompleter)
        #- 
        self.mSourcesQToolButton = QtWidgets.QToolButton(self.falseBoxGroupOfValues)
        self.mSourcesQToolButton.setGeometry(QtCore.QRect(290, 17, 40, 20))
        self.mSourcesQToolButton.setObjectName("mSourcesQToolButton")
        self.mSourcesQToolButton.setIcon(QIcon(_iconSources))
        #MenuQToolButton                        
        self.SourcestQMenuG1 = QMenu()
        self.SourcestQMenuG1.setStyleSheet("QMenu {  font-family:" + self.policeQGroupBox  +"; border-style:" + self.editStyle  +" ; border-width: 0px;}")
        #------------
        for elemQMenuItem in ['Thème INSPIRE (UE)', 'Thème de données (UE)'] :
            if elemQMenuItem == 'Thème de données (UE)' : 
               _mObjetQMenuIcon = QIcon(_iconSourcesSelect)
            else :                 
               _mObjetQMenuIcon = QIcon(_iconSourcesVierge)
              
            _mObjetQMenuItem = QAction(elemQMenuItem, self.SourcestQMenuG1)
            _mObjetQMenuItem.setText(elemQMenuItem)
            _mObjetQMenuItem.setObjectName(str(elemQMenuItem))
            _mObjetQMenuItem.setIcon(_mObjetQMenuIcon)
            self.SourcestQMenuG1.addAction(_mObjetQMenuItem)
       
        self.mSourcesQToolButton.setPopupMode(self.mSourcesQToolButton.MenuButtonPopup)
        self.mSourcesQToolButton.setMenu(self.SourcestQMenuG1)
        #- 
        self.mzoneTextQToolButton = QtWidgets.QToolButton(self.falseBoxGroupOfValues)
        self.mzoneTextQToolButton.setObjectName("mzoneTextQToolButton")
        self.mzoneTextQToolButton.setText("fr")
        self.mzoneTextQToolButton.setGeometry(QtCore.QRect(340, 17, 30, 20))
        self.mObjetQMenuG1 = QMenu()
        self.mObjetQMenuG1.setStyleSheet("QMenu {  font-family:" + self.policeQGroupBox  +"; width:50px; border-style:" + self.editStyle  + "; border-width: 0px;}")
        #
        for elemQMenuItem in ['fr', 'en'] :
            _mObjetQMenuItem = QAction(elemQMenuItem, self.mObjetQMenuG1)
            _mObjetQMenuItem.setText(elemQMenuItem)
            _mObjetQMenuItem.setObjectName(str(elemQMenuItem))
            self.mObjetQMenuG1.addAction(_mObjetQMenuItem)
        self.mzoneTextQToolButton.setPopupMode(self.mzoneTextQToolButton.MenuButtonPopup)
        self.mzoneTextQToolButton.setMenu(self.mObjetQMenuG1)
        #- 
        self.mzoneTextQToolButtonMoins = QtWidgets.QToolButton(self.falseBoxGroupOfValues)
        self.mzoneTextQToolButtonMoins.setObjectName("mzoneTextQToolButtonMoins")
        # == QICON
        self.mzoneTextQToolButtonMoins.setIcon(QIcon(_iconMinusTempGoValues))
        # == QICON
        self.mzoneTextQToolButtonMoins.setGeometry(QtCore.QRect(380, 17, 20, 20))
        #------------------------ 
        """
        self.mzoneText2 = QtWidgets.QTextEdit(self.falseBoxGroupOfValues)
        self.mzoneText2.setStyleSheet("QTextEdit {  font-family:" + self.policeQGroupBox  +"; border-style:" + self.editStyle  +" ; border-width: 0px;}")
        self.mzoneText2.setGeometry(QtCore.QRect(20, 45, 260, 23))
        self.mzoneText2.setObjectName("mzoneText2")
        self.mzoneText2.setText("Zone d'aménagement concerté")
        """
        self.mzoneTextCombo2 = QtWidgets.QComboBox(self.falseBoxGroupOfValues)
        self.mzoneTextCombo2.setStyleSheet("QComboBox {  font-family:" + self.policeQGroupBox  +"; border-style:" + self.editStyle  + " ; border-width: 0px;} \
                                        QComboBox::drop-down {border: 0px;}\
                                        QComboBox::down-arrow {image: url(" + _iconQComboBox + ");position:absolute; left : 5px;width: 12px;height: 45px;}") 
        self.mzoneTextCombo2.setGeometry(QtCore.QRect(20, 45, 260, 23))
        self.mzoneTextCombo2.setObjectName("mzoneTextCombo2")
        self.mzoneTextCombo2.addItems(_thesaurus2)
        self.mzoneTextCombo2.setCurrentText("Bâtiments") 
        self.mzoneTextCombo2.setEditable(True)
        mCompleter = QCompleter(_thesaurus2, self)
        mCompleter.setCaseSensitivity(Qt.CaseInsensitive)
        self.mzoneTextCombo2.setCompleter(mCompleter)
        #- 
        self.mSourcesQToolButton2 = QtWidgets.QToolButton(self.falseBoxGroupOfValues)
        self.mSourcesQToolButton2.setGeometry(QtCore.QRect(290, 45, 40, 20))
        self.mSourcesQToolButton2.setObjectName("mSourcesQToolButton")
        self.mSourcesQToolButton2.setIcon(QIcon(_iconSources))
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
        self.mzoneTextQToolButton2 = QtWidgets.QToolButton(self.falseBoxGroupOfValues)
        self.mzoneTextQToolButton2.setObjectName("mzoneTextQToolButton")
        self.mzoneTextQToolButton2.setText("en")
        self.mzoneTextQToolButton2.setGeometry(QtCore.QRect(340, 45, 30, 20))
        self.mObjetQMenuG2 = QMenu()
        self.mObjetQMenuG2.setStyleSheet("QMenu {  font-family:" + self.policeQGroupBox  +"; width:50px; border-style:" + self.editStyle  + "; border-width: 0px;}")
        #
        for elemQMenuItem in ['fr', 'en'] :
            _mObjetQMenuItem = QAction(elemQMenuItem, self.mObjetQMenuG2)
            _mObjetQMenuItem.setText(elemQMenuItem)
            _mObjetQMenuItem.setObjectName(str(elemQMenuItem))
            self.mObjetQMenuG2.addAction(_mObjetQMenuItem)
        self.mzoneTextQToolButton2.setPopupMode(self.mzoneTextQToolButton.MenuButtonPopup)
        self.mzoneTextQToolButton2.setMenu(self.mObjetQMenuG2)
        #- 
        self.mzoneTextQToolButtonMoins2 = QtWidgets.QToolButton(self.falseBoxGroupOfValues)
        self.mzoneTextQToolButtonMoins2.setObjectName("mzoneTextQToolButtonMoins")
        # == QICON
        self.mzoneTextQToolButtonMoins2.setIcon(QIcon(_iconMinusTempGoValues))
        # == QICON
        self.mzoneTextQToolButtonMoins2.setGeometry(QtCore.QRect(380, 45, 20, 20))
        #- 
        self.mzoneTextQToolButtonPlus = QtWidgets.QToolButton(self.falseBoxGroupOfValues)
        self.mzoneTextQToolButtonPlus.setObjectName("mzoneTextQToolButtonPlus")
        # == QICON
        self.mzoneTextQToolButtonPlus.setIcon(QIcon(_iconPlusTempGoValues))
        # == QICON
        self.mzoneTextQToolButtonPlus.setGeometry(QtCore.QRect(20, 73, 20, 20))
        #------------------------ 
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
        x, y = 10, 210
        larg, haut =  self.falseGroupBox.width()- 20, self.falseGroupBox.height()/3 + 0
        self.falseBoxTranslationGroup.setGeometry(QtCore.QRect(x, y, larg, haut))
        self.falseBoxTranslationGroup.setTitle(self.dicListLettreLabel[4]) 
        #------------------------ 
        self.mzoneTextTrad = QtWidgets.QTextEdit(self.falseBoxTranslationGroup)
        self.mzoneTextTrad.setStyleSheet("QTextEdit {  font-family:" + self.policeQGroupBox  +"; border-style:" + self.editStyle  +" ; border-width: 0px;}")
        self.mzoneTextTrad.setGeometry(QtCore.QRect(20, 17, 310, 23))
        self.mzoneTextTrad.setObjectName("mzoneText")
        self.mzoneTextTrad.setText("Délimitation des zones")
        #- 
        self.mzoneTextQToolButtonTrad = QtWidgets.QToolButton(self.falseBoxTranslationGroup)
        self.mzoneTextQToolButtonTrad.setObjectName("mzoneTextQToolButton")
        self.mzoneTextQToolButtonTrad.setText("en")
        self.mzoneTextQToolButtonTrad.setGeometry(QtCore.QRect(340, 17, 30, 20))
        self.mObjetQMenuG1Trad = QMenu()
        self.mObjetQMenuG1Trad.setStyleSheet("QMenu {  font-family:" + self.policeQGroupBox  +"; width:50px; border-style:" + self.editStyle  + "; border-width: 0px;}")
        #
        for elemQMenuItem in ['fr', 'en'] :
            _mObjetQMenuItem = QAction(elemQMenuItem, self.mObjetQMenuG1Trad)
            _mObjetQMenuItem.setText(elemQMenuItem)
            _mObjetQMenuItem.setObjectName(str(elemQMenuItem))
            self.mObjetQMenuG1Trad.addAction(_mObjetQMenuItem)
        self.mzoneTextQToolButtonTrad.setPopupMode(self.mzoneTextQToolButton.MenuButtonPopup)
        self.mzoneTextQToolButtonTrad.setMenu(self.mObjetQMenuG1Trad)
        #- 
        self.mzoneTextQToolButtonMoinsTrad = QtWidgets.QToolButton(self.falseBoxTranslationGroup)
        self.mzoneTextQToolButtonMoinsTrad.setObjectName("mzoneTextQToolButtonMoins")
        # == QICON
        self.mzoneTextQToolButtonMoinsTrad.setIcon(QIcon(_iconMinusTempTgroup))
        # == QICON
        self.mzoneTextQToolButtonMoinsTrad.setGeometry(QtCore.QRect(380, 17, 20, 20))
        #------------------------ 
        self.mzoneText2Trad = QtWidgets.QTextEdit(self.falseBoxTranslationGroup)
        self.mzoneText2Trad.setStyleSheet("QTextEdit {  font-family:" + self.policeQGroupBox  +"; border-style:" + self.editStyle  +" ; border-width: 0px;}")
        self.mzoneText2Trad.setGeometry(QtCore.QRect(20, 45, 310, 23))
        self.mzoneText2Trad.setObjectName("mzoneText2")
        self.mzoneText2Trad.setText("La table est mise à jour selon l’actualité")
        #- 
        self.mzoneTextQToolButton2Trad = QtWidgets.QToolButton(self.falseBoxTranslationGroup)
        self.mzoneTextQToolButton2Trad.setObjectName("mzoneTextQToolButton")
        self.mzoneTextQToolButton2Trad.setText("fr")
        self.mzoneTextQToolButton2Trad.setGeometry(QtCore.QRect(340, 45, 30, 20))
        self.mObjetQMenuG2Trad = QMenu()
        self.mObjetQMenuG2Trad.setStyleSheet("QMenu {  font-family:" + self.policeQGroupBox  +"; width:50px; border-style:" + self.editStyle  + "; border-width: 0px;}")
        #
        for elemQMenuItem in ['fr', 'en'] :
            _mObjetQMenuItem = QAction(elemQMenuItem, self.mObjetQMenuG2Trad)
            _mObjetQMenuItem.setText(elemQMenuItem)
            _mObjetQMenuItem.setObjectName(str(elemQMenuItem))
            self.mObjetQMenuG2Trad.addAction(_mObjetQMenuItem)
        self.mzoneTextQToolButton2Trad.setPopupMode(self.mzoneTextQToolButton.MenuButtonPopup)
        self.mzoneTextQToolButton2Trad.setMenu(self.mObjetQMenuG2Trad)
        #- 
        self.mzoneTextQToolButtonMoins2Trad = QtWidgets.QToolButton(self.falseBoxTranslationGroup)
        self.mzoneTextQToolButtonMoins2Trad.setObjectName("mzoneTextQToolButtonMoins")
        # == QICON
        self.mzoneTextQToolButtonMoins2Trad.setIcon(QIcon(_iconMinusTempTgroup))
        # == QICON
        self.mzoneTextQToolButtonMoins2Trad.setGeometry(QtCore.QRect(380, 45, 20, 20))
        #- 
        self.mzoneTextQToolButtonPlusTrad = QtWidgets.QToolButton(self.falseBoxTranslationGroup)
        self.mzoneTextQToolButtonPlusTrad.setObjectName("mzoneTextQToolButtonPlus")
        # == QICON
        self.mzoneTextQToolButtonPlusTrad.setIcon(QIcon(_iconPlusTempTgroup))
        # == QICON
        self.mzoneTextQToolButtonPlusTrad.setGeometry(QtCore.QRect(20, 73, 20, 20))
        #------------------------ 
        return 
        
    #==========================         
    #==========================         
    def applyWYSIWYG(self): 
        _pathIcons = os.path.dirname(__file__) + "/icons/buttons"
        _iconQComboBox             = _pathIcons + "/dropDownArrow.png"
        _iconQComboBox = _iconQComboBox.replace("\\","/")
        _iconSources               = _pathIcons + "/source_button.svg"
        _iconSourcesSelect         = _pathIcons + "/source_button.png"
        _iconSourcesVierge         = _pathIcons + "/vierge.png"
        _iconPlus                  = _pathIcons + "/plus_button.svg"
        _iconPlusTempGoValues      = _pathIcons + "/color_button_Plus_GoValues_ForVisu.svg"
        _iconPlusTempTgroup        = _pathIcons + "/color_button_Plus_Tgroup_ForVisu.svg"
        _iconMinus                 = _pathIcons + "/minus_button.svg"
        _iconMinusTempGoValues     = _pathIcons + "/color_button_Minus_GoValues_ForVisu.svg"
        _iconMinusTempTgroup       = _pathIcons + "/color_button_Minus_Tgroup_ForVisu.svg"
        _mListeIconsButtonPlusMinus = [ _iconPlusTempGoValues,  _iconPlusTempTgroup, \
                                        _iconMinusTempGoValues, _iconMinusTempTgroup ]

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
        
        self.writeColorIconForVisu(_iconPlus, _iconMinus, _mListeIconsButtonPlusMinus) 
                      

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
        self.mLabelEdit.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.colorQLabel  +";}")
        self.mzoneEdit.setStyleSheet("QLineEdit {  font-family:" + self.policeQGroupBox  +"; border-style:" + self.editStyle  +" ; border-width: 0px;}")
        self.mLabelDate.setStyleSheet("QLabel {  font-family:" + self.policeQGroupBox  +"; background-color:" + self.colorQLabel  +";}")
        self.mzoneDate.setStyleSheet("QgsDateTimeEdit {  font-family:" + self.policeQGroupBox  +"; }")
        #--- 
        self.mzoneTextCombo.setStyleSheet("QComboBox {  font-family:" + self.policeQGroupBox  +"; border-style:" + self.editStyle  + " ; border-width: 0px;} \
                                        QComboBox::drop-down {border: 0px;}\
                                        QComboBox::down-arrow {image: url(" + _iconQComboBox + ");position:absolute; left : 5px;width: 12px;height: 45px;}") 
        self.SourcestQMenuG1.setStyleSheet("QMenu {  font-family:" + self.policeQGroupBox  +"; border-style:" + self.editStyle  +" ; border-width: 0px;}")
        self.mObjetQMenuG1.setStyleSheet("QMenu {  font-family:" + self.policeQGroupBox  +"; width:50px; border-style:" + self.editStyle  + "; border-width: 0px;}")
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
        mReset.setGeometry(QtCore.QRect(mX3, mY3, 80, 20))
        mReset.setObjectName(mResetName)
        mReset.setText("Réinitialiser")
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
    def functionSave(self):
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

           #======== User Settings
           mSettings.beginGroup("UserSettings")
           # liste des Paramétres UTILISATEURS
           mDicUserSettings = {}
           mDicUserSettings["langList"]                = self.mZoneLangList.text().split(",")
           mDicUserSettings["geoideJSON"]              = "true" if self.mZoneGeoideJSON else "false"
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
                "#958B62",
                "#958B62",
                "#5770BE",         
                "#FF8D7E",
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