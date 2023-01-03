# (c) Didier  LECLERC 2020 CMSIG MTE-MCTRCT-Mer/SG/SNUM/UNI/DRC Site de Rouen
# créé sept 2020 

import os.path
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qt import *

from . import bibli_plume
from .bibli_plume import *

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        self.mDic_LH = bibli_plume.returnAndSaveDialogParam(self, "Load")
        self.editStyle        = self.mDic_LH["QEdit"]              #style saisie
        self.labelBackGround  = self.mDic_LH["QLabelBackGround"] #QLabel    
        self.epaiQGroupBox    = self.mDic_LH["QGroupBoxEpaisseur"] #épaisseur QGroupBox
        self.lineQGroupBox    = self.mDic_LH["QGroupBoxLine"]    #trait QGroupBox
        self.policeQGroupBox  = self.mDic_LH["QGroupBoxPolice"]  #Police QGroupBox
        self.policeQTabWidget = self.mDic_LH["QTabWidgetPolice"] #Police QTabWidget
        #-
        #-
        self.Dialog = Dialog   #Pour remonter les variables de la boite de dialogue
        self.zMessTitle    =  QtWidgets.QApplication.translate("about", "model management", None)   #Gestion des modèles
        myPath = os.path.dirname(__file__)+"\\icons\\logo\\plume.svg"

        self.Dialog.setObjectName("DialogConfirme")
        #mLargDefaut, mHautDefaut = int(self.mDic_LH["dialogLargeurTemplate"]), int(self.mDic_LH["dialogHauteurTemplate"]) #900, 650    
        mLargDefaut, mHautDefaut = 900, 450
        self.Dialog.resize(mLargDefaut, mHautDefaut)
        self.lScreenDialog, self.hScreenDialog = int(self.Dialog.width()), int(self.Dialog.height())
        _pathIcons = os.path.dirname(__file__) + "/icons/logo"
        iconSource          = _pathIcons + "/plume.svg"
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(iconSource), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.Dialog.setWindowIcon(icon)
        #----------
        self.labelImage = QtWidgets.QLabel(self.Dialog)
        myDefPath = myPath.replace("\\","/")
        carIcon = QtGui.QImage(myDefPath)
        self.labelImage.setPixmap(QtGui.QPixmap.fromImage(carIcon))
        self.labelImage.setGeometry(QtCore.QRect(20, 0, 100, 100))
        self.labelImage.setObjectName("labelImage")
        #----------
        self.label_2 = QtWidgets.QLabel(self.Dialog)
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

        #group general 
        self.groupBoxGeneral = QtWidgets.QGroupBox(self.Dialog)
        self.groupBoxGeneral.setGeometry(QtCore.QRect(10,100,self.lScreenDialog - 20, self.hScreenDialog - 110))
        self.groupBoxGeneral.setObjectName("groupBoxGeneral")
        self.groupBoxGeneral.setStyleSheet("QGroupBox { border: 0px solid green}")
        #-
        self.layoutGeneral = QtWidgets.QGridLayout()
        self.layoutGeneral.setRowStretch(0, 8)
        self.layoutGeneral.setRowStretch(1, 1)
        self.layoutGeneral.setRowStretch(2, 1)
        self.layoutGeneral.setRowStretch(3, 1)
        #-
        self.layoutGeneral.setColumnStretch(0, 10)
        self.layoutGeneral.setColumnStretch(1, 1)
        self.layoutGeneral.setColumnStretch(2, 5)
        self.groupBoxGeneral.setLayout(self.layoutGeneral)

        #========
        self.labelImage2 = QtWidgets.QLabel()
        myPath = os.path.dirname(__file__)+"\\icons\\about\\ui_screenshot.svg";
        myDefPath = myPath.replace("\\","/");
        carIcon2 = QtGui.QImage(myDefPath)
        self.labelImage2.setPixmap(QtGui.QPixmap.fromImage(carIcon2))
        self.labelImage2.setObjectName("labelImage2")
        #========

        self.textEdit = QtWidgets.QTextBrowser()
        palette = QtGui.QPalette()
        #-
        brush = QtGui.QBrush(QtGui.QColor(0,0,0,0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active,QtGui.QPalette.Base,brush)
        #-
        brush = QtGui.QBrush(QtGui.QColor(0,0,0,0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive,QtGui.QPalette.Base,brush)
        #-
        brush = QtGui.QBrush(QtGui.QColor(255,255,255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled,QtGui.QPalette.Base,brush)
        self.textEdit.setPalette(palette)
        self.textEdit.setAutoFillBackground(True)
        self.textEdit.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.textEdit.setFrameShadow(QtWidgets.QFrame.Plain)
        self.textEdit.setReadOnly(True)
        self.textEdit.setObjectName("textEdit")
        self.textEdit.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        self.layoutGeneral.addWidget(self.textEdit, 0, 0, 4, 1)
        #========
        # Références Href
        self.groupBoxHref = QtWidgets.QGroupBox()
        self.groupBoxHref.setObjectName("groupBoxHref")
        self.groupBoxHref.setStyleSheet("QGroupBox { border: 0px solid blue;}")
        #-
        self.layoutHref = QtWidgets.QGridLayout()
        #-
        self.groupBoxHref.setLayout(self.layoutHref)
        self.layoutGeneral.addWidget(self.groupBoxHref, 0, 2)
        #=====================================
        # [ == scrolling == ]
        self.scroll_bar_Href = QtWidgets.QScrollArea() 
        self.scroll_bar_Href.setStyleSheet("QScrollArea { border: 0px solid red;}")
        self.scroll_bar_Href.setWidgetResizable(True)
        self.scroll_bar_Href.setWidget(self.groupBoxHref)
        self.layoutGeneral.addWidget(self.scroll_bar_Href, 0, 2)
        #=====================================
        self.textEditDL = QtWidgets.QLabel()
        self.textEditDL.setWordWrap(True)
        self.layoutHref.addWidget(self.textEditDL)
        #========
        self.pushButton = QtWidgets.QPushButton()
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(Dialog.reject)
        #self.layoutGeneral.addWidget(self.pushButton, 3, 1)

        self.retranslateUi(Dialog)

    def retranslateUi(self, Dialog):
        MonHtml = ""
        MonHtml += "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        MonHtml += "p, li { white-space: pre-wrap; }\n"
        MonHtml += "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
        MonHtml += "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'MS Shell Dlg 2\'; font-size:8pt;\"><span style=\" font-weight:600;\">"
        mVERSION = " = version 1.6"
        MonHtml1 = QtWidgets.QApplication.translate("about", "Plume", None) + "  (" + str(bibli_plume.returnVersion()) + ")"
        MonHtml += MonHtml1
        MonHtml += "</span>" 
        MonHtml2 = "<br><br>"
        MonHtml2 += QtWidgets.QApplication.translate("about", "Plume, for PLUgin MEtadata, is a QGIS plugin for consulting and entering metadata for PostgreSQL base layers.", None)
        MonHtml2 += "<br><br>"
        MonHtml2 += QtWidgets.QApplication.translate("about", "The metadata is stored in RDF (JSON-LD) format in the PostgreSQL descriptions of objects, the user can access by clicking on the layers in the QGIS explorer or in the layers panel. Plume supports tables, partitioned tables, foreign tables, views, and materialized views.", None)
        MonHtml += MonHtml2
        MonHtml += "<br><br>"
        MonHtml3 = QtWidgets.QApplication.translate("about", "It is based on the GeoDCAT-AP 2.0 profile of DCAT v2, which constitutes a common and exchangeable metadata base, while allowing a wide customization of the metadata categories presented to the user when it is coupled with the PostgreSQL plume_pg extension.", None) 
        MonHtml += MonHtml3
        MonHtml += "</b><br>"
        MonHtml += "</p></td></tr></table>"
        MonHtml += "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p>\n"
        MonHtml += "<p style=\"margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">"
        
        mLinkDL = "mailto:didier.leclerc@developpement-durable.gouv.fr"
        MonHtmlDL = "<font color='#0000FF'>" + QtWidgets.QApplication.translate("about", "Didier LECLERC: integration, development of the user interface and the interface with the PostgreSQL server.", None) + "</font><br><br>"
        mLinkDL = '<a href=\"' + mLinkDL + '\">' + MonHtmlDL + '</a>'

        mLinkLL = "mailto:leslie.lemaire@developpement-durable.gouv.fr"
        MonHtmlLL = "<font color='#0000FF'>" + QtWidgets.QApplication.translate("about", "Leslie LEMAIRE: design and development of the underlying mechanics (plume.rdf, plume.pg et plume.iso.), creation of logos and icons.", None) + "</font><br><br>"
        mLinkLL = '<a href=\"' + mLinkLL + '\">' + MonHtmlLL + '</a>'
        
        MonHtml += "<b>"
        MonHtml4 = QtWidgets.QApplication.translate("about", "MTECT/MTE/Mer", None) 
        MonHtml += MonHtml4
        MonHtml += "</b><br><b>"
        MonHtml6 = QtWidgets.QApplication.translate("about", "digital service SG/DNUM/UNI/DRC", None) 
        MonHtml += MonHtml6
        MonHtml += "<br><br><i>"
        MonHtml7 = QtWidgets.QApplication.translate("about", "Development in 2021/2022/2023", None) 
        MonHtml += MonHtml7
        MonHtml += "</i></p></body></html>"

        Dialog.setWindowTitle(QtWidgets.QApplication.translate("about", "PLUME (Metadata storage in PostGreSQL)", None) + "  (" + str(bibli_plume.returnVersion()) + ")")
        self.label_2.setText(QtWidgets.QApplication.translate("about", "Plume", None))
        self.textEdit.setHtml(QtWidgets.QApplication.translate("about", MonHtml, None))
        self.textEditDLLL = mLinkDL + "<br>" + mLinkLL
        self.textEditDL.setText(self.textEditDLLL)
        self.textEditDL.setOpenExternalLinks(True)       
        self.pushButton.setText(QtWidgets.QApplication.translate("about", "OK", None))

    #==========================
    def resizeEvent(self, event):
        self.groupBoxGeneral.setGeometry(QtCore.QRect(10,100,self.Dialog.width() - 20, self.Dialog.height() - 110))
        return
        