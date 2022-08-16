# (c) Didier  LECLERC 2020 CMSIG MTE-MCTRCT-Mer/SG/SNUM/UNI/DRC Site de Rouen
# créé sept 2020 

import os.path
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qt import *

from . import bibli_plume
from .bibli_plume import *

class Ui_Dialog(object):
    def setupUi(self, Dialog):

        Dialog.setObjectName("Dialog")
        Dialog.resize(QtCore.QSize(QtCore.QRect(0,0,700,600).size()).expandedTo(Dialog.minimumSizeHint()))
        iconSource = bibli_plume.getThemeIcon("logo_init.png")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(iconSource), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)

        self.groupDialog = QtWidgets.QGroupBox(Dialog)
        self.groupDialog.setGeometry(QtCore.QRect(5, 5, Dialog.width()-10,  Dialog.height()-10))
        self.groupDialog.setObjectName("groupDialog")
        self.groupDialog.setStyleSheet("QGroupBox {border: 3px solid #958B62;}")
        
        self.label_2 = QtWidgets.QLabel(self.groupDialog)
        self.label_2.setGeometry(QtCore.QRect((self.groupDialog.width()/2) - 100, 5, 200, 30))
        self.label_2.setAlignment(Qt.AlignCenter)        
        font = QtGui.QFont()
        font.setPointSize(15) 
        font.setWeight(50) 
        font.setBold(True)
        self.label_2.setFont(font)
        self.label_2.setTextFormat(QtCore.Qt.RichText)
        self.label_2.setObjectName("label_2")
        self.labelImage = QtWidgets.QLabel(self.groupDialog)
        myPath = os.path.dirname(__file__)+"\\icons\\logo\\logoabout1.png"
        myDefPath = myPath.replace("\\","/");
        carIcon = QtGui.QImage(myDefPath)
        self.labelImage.setPixmap(QtGui.QPixmap.fromImage(carIcon))
        self.labelImage.setGeometry(QtCore.QRect(10, 30, 266, 70))
        self.labelImage.setObjectName("labelImage")

        self.labelImage2 = QtWidgets.QLabel(self.groupDialog)
        myPath = os.path.dirname(__file__)+"\\icons\\logo\\logoabout2.png";
        myDefPath = myPath.replace("\\","/");
        carIcon2 = QtGui.QImage(myDefPath)
        self.labelImage2.setPixmap(QtGui.QPixmap.fromImage(carIcon2))
        self.labelImage2.setGeometry(QtCore.QRect(self.groupDialog.width()/2 - 55, 40, self.groupDialog.width()/2 + 60, self.groupDialog.height() - 70))
        self.labelImage2.setObjectName("labelImage2")
        #self.labelImage2.setStyleSheet("QLabel {border: 3px solid #958B62;}")

        self.textEdit = QtWidgets.QTextBrowser(self.groupDialog)
        palette = QtGui.QPalette()

        brush = QtGui.QBrush(QtGui.QColor(0,0,0,0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active,QtGui.QPalette.Base,brush)

        brush = QtGui.QBrush(QtGui.QColor(0,0,0,0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive,QtGui.QPalette.Base,brush)

        brush = QtGui.QBrush(QtGui.QColor(255,255,255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled,QtGui.QPalette.Base,brush)
        self.textEdit.setPalette(palette)
        self.textEdit.setAutoFillBackground(True)
        self.textEdit.width = 300
        self.textEdit.height = 260
        self.textEdit.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.textEdit.setFrameShadow(QtWidgets.QFrame.Plain)
        self.textEdit.setReadOnly(True)
        self.textEdit.setObjectName("textEdit")
        self.textEdit.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        self.textEdit.setGeometry(QtCore.QRect(10, 100, 280, 360))

        self.textEditDL = QtWidgets.QLabel(self.groupDialog)
        self.textEditDL.setGeometry(QtCore.QRect(10, 450, 280, 50))
        self.textEditDL.setWordWrap(True)
        self.textEditLL = QtWidgets.QLabel(self.groupDialog)
        self.textEditLL.setGeometry(QtCore.QRect(10, 500, 280, 50))
        self.textEditLL.setWordWrap(True)


        self.pushButton = QtWidgets.QPushButton(self.groupDialog)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setGeometry(QtCore.QRect(410, self.groupDialog.height() - 35, 100, 25))
        self.pushButton.clicked.connect(Dialog.reject)

        self.retranslateUi(Dialog)

    def retranslateUi(self, Dialog):
        MonHtml = ""
        MonHtml += "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        MonHtml += "p, li { white-space: pre-wrap; }\n"
        MonHtml += "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
        MonHtml += "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'MS Shell Dlg 2\'; font-size:8pt;\"><span style=\" font-weight:600;\">"
        mVERSION = " = version 1.6"
        MonHtml1 = QtWidgets.QApplication.translate("about", "PLUME", None) + "  (" + str(bibli_plume.returnVersion()) + ")"
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
        MonHtmlDL = "<font color='#0000FF'><b><u>" + QtWidgets.QApplication.translate("about", "Didier LECLERC: integration, development of the user interface and the interface with the PostgreSQL server.", None) + "</u></b></font><br><br>"
        mLinkDL = '<a href=\"' + mLinkDL + '\">' + MonHtmlDL + '</a>'

        mLinkLL = "mailto:leslie.lemaire@developpement-durable.gouv.fr"
        MonHtmlLL = "<font color='#0000FF'><b><u>" + QtWidgets.QApplication.translate("about", "Leslie LEMAIRE: design and development of the underlying mechanics (plume.rdf, plume.pg et plume.iso.), creation of logos and icons.", None) + "</u></b></font><br><br>"
        mLinkLL = '<a href=\"' + mLinkLL + '\">' + MonHtmlLL + '</a>'
        
        MonHtml += "<b>"
        MonHtml4 = QtWidgets.QApplication.translate("about", "MTE / MCTRCT / Mer", None) 
        MonHtml += MonHtml4
        MonHtml += "</b><br><b>"
        MonHtml6 = QtWidgets.QApplication.translate("about", "digital service SG/DNUM/UNI/DRC", None) 
        MonHtml += MonHtml6
        MonHtml += "<br><br><i>"
        MonHtml7 = QtWidgets.QApplication.translate("about", "Development in 2021/2022", None) 
        MonHtml += MonHtml7
        MonHtml += "</i></p></body></html>"

        Dialog.setWindowTitle(QtWidgets.QApplication.translate("about", "PLUME (Metadata storage in PostGreSQL)", None) + "  (" + str(bibli_plume.returnVersion()) + ")")
        self.label_2.setText(QtWidgets.QApplication.translate("about", "PLUME", None))
        self.textEdit.setHtml(QtWidgets.QApplication.translate("about", MonHtml, None))
        self.textEditDL.setText(mLinkDL)
        self.textEditDL.setOpenExternalLinks(True)       
        self.textEditLL.setText(mLinkLL)
        self.textEditLL.setOpenExternalLinks(True)       
        self.pushButton.setText(QtWidgets.QApplication.translate("about", "OK", None))
