# (c) Didier  LECLERC 2020 CMSIG MTE-MCTRCT/SG/SNUM/UNI/DRC Site de Rouen
# créé 2022

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import ( QMenu, QAction, \
                              QTreeWidget, QAbstractItemView, QTreeWidgetItemIterator, QTreeWidgetItem, QHeaderView )
from PyQt5.QtGui     import ( QIcon, QDrag )
from PyQt5.QtCore    import ( Qt, QUrl, QEventLoop, QByteArray )
from qgis.core import Qgis

from plume.bibli_plume import ( returnIcon, returnVersion, displayMess, returnObjetsMeta, saveObjetTranslation, returnAndSaveDialogParam )

import os.path
#
from plume.rdf.metagraph import metagraph_from_iso
from plume.iso import csw 
from qgis.core import QgsNetworkContentFetcher
#
from plume.config import ( LIBURLCSWDEFAUT, URLCSWDEFAUT )  

class Ui_Dialog_ImportCSW(object):
    def setupUiImportCSW(self, DialogImportCSW, Dialog):
        self.DialogImportCSW = DialogImportCSW
        self.Dialog = Dialog   #Pour remonter les variables de la boite de dialogue
        self.zMessTitle    =  QtWidgets.QApplication.translate("ImportCSW_ui", "Import metadata from a CSW service", None)
        myPath = os.path.dirname(__file__)+"\\icons\\logo\\plume.svg"

        self.DialogImportCSW.setObjectName("DialogConfirme")
        self.DialogImportCSW.setFixedSize(900,570)
        self.lScreenDialog, self.hScreenDialog = int(self.DialogImportCSW.width()), int(self.DialogImportCSW.height())
        _pathIcons = os.path.dirname(__file__) + "/icons/logo"
        iconSource          = _pathIcons + "/plume.svg"
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(iconSource), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.DialogImportCSW.setWindowIcon(icon)
        #----------
        self.labelImage = QtWidgets.QLabel(self.DialogImportCSW)
        myDefPath = myPath.replace("\\","/")
        carIcon = QtGui.QImage(myDefPath)
        self.labelImage.setPixmap(QtGui.QPixmap.fromImage(carIcon))
        self.labelImage.setGeometry(QtCore.QRect(20, 0, 100, 100))
        self.labelImage.setObjectName("labelImage")
        #----------
        self.label_2 = QtWidgets.QLabel(self.DialogImportCSW)
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
        hauteurListeUrl = 175
        #------
        self.urlCswDefautGEOIDE, self.urlCswDefautIGN, self.urlCswIdDefautGEOIDE = "", "", ""
        self.libUrlCswDefautGEOIDE, self.libUrlCswDefautIGN = "", ""
        if Dialog.urlCswDefaut.split(",")[0]   != "" : self.urlCswDefautGEOIDE   = Dialog.urlCswDefaut.split(",")[0]
        if Dialog.urlCswDefaut.split(",")[1]   != "" : self.urlCswDefautIGN      = Dialog.urlCswDefaut.split(",")[1]
        if Dialog.urlCswIdDefaut.split(",")[0] != "" : self.urlCswIdDefautGEOIDE = Dialog.urlCswIdDefaut.split(",")[0]
        if Dialog.libUrlCswDefaut.split(",")[0]   != "" : self.libUrlCswDefautGEOIDE   = Dialog.libUrlCswDefaut.split(",")[0]
        if Dialog.libUrlCswDefaut.split(",")[1]   != "" : self.libUrlCswDefautIGN      = Dialog.libUrlCswDefaut.split(",")[1]

        mDic_LH = returnAndSaveDialogParam(self, "Load")
        Dialog.urlCsw = mDic_LH["urlCsw"]             #Liste des urlcsw sauvegardées
        mListurlCsw = Dialog.urlCsw.split(",")
        self.urlCsw = Dialog.urlCsw
        Dialog.libUrlCsw = mDic_LH["liburlCsw"]             #Liste des urlcsw sauvegardées
        mListliburlCsw = Dialog.libUrlCsw.split(",")
        self.libUrlCsw = Dialog.libUrlCsw

        #------
        #group general 
        self.groupBoxGeneral = QtWidgets.QGroupBox(self.DialogImportCSW)
        self.groupBoxGeneral.setGeometry(QtCore.QRect(10,100,self.lScreenDialog - 20, self.hScreenDialog - 90))
        self.groupBoxGeneral.setObjectName("groupBoxGeneral")
        self.groupBoxGeneral.setStyleSheet("QGroupBox { border: 0px solid green}")
        #-
        self.layoutGeneral = QtWidgets.QGridLayout()
        self.layoutGeneral.setRowStretch(0, 4)
        self.layoutGeneral.setRowStretch(1, 1)
        self.layoutGeneral.setRowStretch(2, 1)
        self.layoutGeneral.setRowStretch(3, 1)
        self.groupBoxGeneral.setLayout(self.layoutGeneral)
        #------
        #Liste URL / ID 
        self.groupBoxListeUrl = QtWidgets.QGroupBox()
        self.groupBoxListeUrl.setObjectName("groupBoxListeUrl")
        self.groupBoxListeUrl.setStyleSheet("QGroupBox {   \
                              font-family:" + Dialog.policeQGroupBox  +" ; \
                              border-style: " + Dialog.lineQGroupBox  + ";    \
                              border-width:" + str(Dialog.epaiQGroupBox)  + "px ; \
                              border-color: " + Dialog.colorQGroupBoxGroupOfProperties  +"; \
                              }" \
                              "QGroupBox::title {padding-top: -7px; padding-left: 10px;}"
                              )                    
        titlegroupBoxListeUrl = QtWidgets.QApplication.translate("ImportCSW_ui", "Stored CSWs", None)
        self.groupBoxListeUrl.setTitle(titlegroupBoxListeUrl)
        #-
        self.layoutListeUrl = QtWidgets.QGridLayout()
        self.groupBoxListeUrl.setLayout(self.layoutListeUrl)
        self.layoutGeneral.addWidget(self.groupBoxListeUrl)
        #-
        #------ 
        #Liste URL / ID 
        self.groupBoxSaisie = QtWidgets.QGroupBox()
        self.groupBoxSaisie.setObjectName("groupBoxSaisie")
         #-
        self.layoutSaisie = QtWidgets.QGridLayout()
        self.layoutSaisie.setColumnStretch(0, 3)
        self.layoutSaisie.setColumnStretch(1, 6)
        self.layoutSaisie.setColumnStretch(2, 1)
        self.groupBoxSaisie.setLayout(self.layoutSaisie)
        self.layoutGeneral.addWidget(self.groupBoxSaisie)
        #-
        mLabelLibUrlText = QtWidgets.QApplication.translate("ImportCSW_ui", "CSW URL LIB", None)
        mLabelLibUrlToolTip = QtWidgets.QApplication.translate("ImportCSW_ui", "LIB URL of the CSW service.", None)
        mLabelLibUrl = QtWidgets.QLabel(self.DialogImportCSW)
        mLabelLibUrl.setStyleSheet("QLabel {  font-family:" + Dialog.policeQGroupBox  +"; background-color:" + Dialog.labelBackGround  +";}")
        mLabelLibUrl.setObjectName("mLabelLibUrl")
        mLabelLibUrl.setText(mLabelLibUrlText)
        mLabelLibUrl.setToolTip(mLabelLibUrlToolTip)
        mLabelLibUrl.setWordWrap(True)
        self.layoutSaisie.addWidget(mLabelLibUrl, 0, 0)
        #- 
        mZoneLibUrl = QtWidgets.QLineEdit(self.DialogImportCSW)
        mZoneLibUrl.setStyleSheet("QLineEdit {  font-family:" + Dialog.policeQGroupBox  +";}")
        mZoneLibUrl.setObjectName("mZoneLibUrl")
        mZoneLibUrl.setToolTip(mLabelLibUrlToolTip)
        mZoneLibUrl.setPlaceholderText("Mon libellé")
        mZoneLibUrl.setText("")
        self.layoutSaisie.addWidget(mZoneLibUrl, 0, 1)
        self.mZoneLibUrl = mZoneLibUrl
        #-
        mLabelUrlText = QtWidgets.QApplication.translate("ImportCSW_ui", "CSW URL", None)
        mLabelUrlToolTip = QtWidgets.QApplication.translate("ImportCSW_ui", "URL of the CSW service, without any parameters.", None)
        mLabelUrl = QtWidgets.QLabel(self.DialogImportCSW)
        mLabelUrl.setStyleSheet("QLabel {  font-family:" + Dialog.policeQGroupBox  +"; background-color:" + Dialog.labelBackGround  +";}")
        mLabelUrl.setObjectName("mLabelUrl")
        mLabelUrl.setText(mLabelUrlText)
        mLabelUrl.setToolTip(mLabelUrlToolTip)
        mLabelUrl.setWordWrap(True)
        self.layoutSaisie.addWidget(mLabelUrl, 1, 0)
        #- 
        mZoneUrl = QtWidgets.QLineEdit(self.DialogImportCSW)
        mZoneUrl.setStyleSheet("QLineEdit {  font-family:" + Dialog.policeQGroupBox  +";}")
        mZoneUrl.setObjectName("mZoneUrl")
        mZoneUrl.setToolTip(mLabelUrlToolTip)
        mZoneUrl.setPlaceholderText(self.urlCswDefautGEOIDE)
        mZoneUrl.setText("")
        self.layoutSaisie.addWidget(mZoneUrl, 1, 1)
        self.mZoneUrl = mZoneUrl
        #-
        mLabelUrlIdText = QtWidgets.QApplication.translate("ImportCSW_ui", "CSW ID", None)
        mLabelUrlIdToolTip = QtWidgets.QApplication.translate("ImportCSW_ui", "This identifier, not to be confused with the resource identifier, generally appears in the URL of the catalog file. This is the gmd: fileIdentifier property of XML.", None)
        mLabelUrlId = QtWidgets.QLabel(self.DialogImportCSW)
        mLabelUrlId.setStyleSheet("QLabel {  font-family:" + Dialog.policeQGroupBox  +"; background-color:" + Dialog.labelBackGround  +";}")
        mLabelUrlId.setObjectName("mLabelUrlId")
        mLabelUrlId.setText(mLabelUrlIdText)
        mLabelUrlId.setToolTip(mLabelUrlIdToolTip)
        mLabelUrlId.setWordWrap(True)
        self.layoutSaisie.addWidget(mLabelUrlId, 2, 0)
        #- 
        mZoneUrlId = QtWidgets.QLineEdit(self.DialogImportCSW)
        mZoneUrlId.setStyleSheet("QLineEdit {  font-family:" + Dialog.policeQGroupBox  +";}")
        mZoneUrlId.setObjectName("mZoneUrlId")
        mZoneUrlId.setToolTip(mLabelUrlIdToolTip)
        mZoneUrlId.setPlaceholderText(self.urlCswIdDefautGEOIDE)
        mZoneUrlId.setText("")
        self.layoutSaisie.addWidget(mZoneUrlId, 2, 1)
        self.mZoneUrlId = mZoneUrlId
        #------
        #Button Add
        self.buttonAdd = QtWidgets.QToolButton(self.DialogImportCSW)
        self.buttonAdd.setObjectName("buttonAdd")
        self.buttonAdd.setIcon(QIcon(os.path.dirname(__file__)+"\\icons\\general\\save.svg"))
        mbuttonAddToolTip = QtWidgets.QApplication.translate("ImportCSW_ui", "Add or modify a stored CSW. The URL and label will be saved in the “My CSW” section of the table above.", None)
        self.buttonAdd.setToolTip(mbuttonAddToolTip)
        self.buttonAdd.clicked.connect(lambda : self.functionAddCsw())
        self.layoutSaisie.addWidget(self.buttonAdd, 1, 2)
        #Button Add
        #------
        #------
        #Checkbox
        self.caseSave = QtWidgets.QCheckBox(self.DialogImportCSW)
        self.caseSave.setObjectName("caseSave")
        mcaseSaveToolTip = QtWidgets.QApplication.translate("ImportCSW_ui", "Save the configuration in the metadata.", None)
        self.caseSave.setToolTip(mcaseSaveToolTip)
        self.caseSave.setStyleSheet("QCheckBox {  font-family:" + Dialog.policeQGroupBox  +"; }")
        self.caseSave.setChecked(True)       
        self.layoutSaisie.addWidget(self.caseSave, 3, 1)
        mLabelcaseSaveText = QtWidgets.QApplication.translate("ImportCSW_ui", "Save the configuration in the metadata", None)
        caseSaveToolTip = QtWidgets.QApplication.translate("ImportCSW_ui", "Save the configuration in the metadata.", None)
        self.mLabelcaseSave = QtWidgets.QLabel(self.DialogImportCSW)
        self.mLabelcaseSave.setObjectName("mLabelcaseSave")
        self.mLabelcaseSave.setStyleSheet("QLabel {  font-family:" + Dialog.policeQGroupBox  +"; background-color:" + Dialog.labelBackGround  +";}")
        self.mLabelcaseSave.setText(mLabelcaseSaveText)
        self.mLabelcaseSave.setToolTip(caseSaveToolTip)
        self.mLabelcaseSave.setWordWrap(True)
        self.layoutSaisie.addWidget(self.mLabelcaseSave, 3, 0)
        #Checkbox
        #------
        #------
        #options 
        groupBoxOptions = QtWidgets.QGroupBox()
        groupBoxOptions.setObjectName("groupBoxOptions")
        groupBoxOptions.setStyleSheet("QGroupBox {   \
                              font-family:" + Dialog.policeQGroupBox  +" ; \
                              border-style: " + Dialog.lineQGroupBox  + ";    \
                              border-width:" + str(Dialog.epaiQGroupBox)  + "px ; \
                              border-color: " + Dialog.colorQGroupBoxGroupOfProperties  +"; \
                              }" \
                              "QGroupBox::title {padding-top: -5px; padding-left: 10px;}"
                              )                    
        groupBoxOptions.setTitle("Mode d'import")
        #-
        self.layoutOptions = QtWidgets.QGridLayout()
        self.layoutOptions.setColumnStretch(0, 3)
        self.layoutOptions.setColumnStretch(1, 6)
        self.layoutOptions.setColumnStretch(2, 1)
        groupBoxOptions.setLayout(self.layoutOptions)
        self.layoutGeneral.addWidget(groupBoxOptions)
        #-
        self.option1 = QtWidgets.QRadioButton(groupBoxOptions)
        self.option1.setObjectName("option1")
        self.option1.setText(QtWidgets.QApplication.translate("ImportCSW_ui", "Complete with remote metadata", None)) 
        self.option1.setStyleSheet("QRadioButton {  font-family:" + Dialog.policeQGroupBox  +";}")
        self.option1.setToolTip(QtWidgets.QApplication.translate("ImportCSW_ui", "For all metadata categories entered in the catalog record that do not have a value in the local record, the value of the remote record is added.", None))
        self.layoutOptions.addWidget(self.option1, 0, 0)
        #-
        self.option2 = QtWidgets.QRadioButton(groupBoxOptions)
        self.option2.setObjectName("option2")
        self.option2.setText(QtWidgets.QApplication.translate("ImportCSW_ui", "Update with remote metadata", None))  
        self.option2.setStyleSheet("QRadioButton {  font-family:" + Dialog.policeQGroupBox  +";}")
        self.option2.setToolTip(QtWidgets.QApplication.translate("ImportCSW_ui", "For all metadata categories entered in the catalog record, the value of the local record is replaced by that of the catalog or added if there was no value.", None))
        self.layoutOptions.addWidget(self.option2, 1, 0)
        #-
        self.option3 = QtWidgets.QRadioButton(groupBoxOptions)
        self.option3.setObjectName("option3")
        self.option3.setText(QtWidgets.QApplication.translate("ImportCSW_ui", "Replace with remote metadata", None))  
        self.option3.setStyleSheet("QRadioButton {  font-family:" + Dialog.policeQGroupBox  +";}")
        self.option3.setToolTip(QtWidgets.QApplication.translate("ImportCSW_ui", "Generates a new form from remote metadata. The difference with option 1 is that the information of the categories not filled in the catalog record but which could have existed locally will be erased.", None))
        self.layoutOptions.addWidget(self.option3, 2, 0)
        self.option1.setChecked(True)
        #options 
        #------ 

        #-
        self.groupBox_buttons = QtWidgets.QGroupBox()
        self.groupBox_buttons.setObjectName("layoutGeneral")
        self.groupBox_buttons.setStyleSheet("QGroupBox { border: 0px solid green }")
        #-
        self.layout_groupBox_buttons = QtWidgets.QGridLayout()
        self.layout_groupBox_buttons.setContentsMargins(0, 0, 0, 0)
        self.groupBox_buttons.setLayout(self.layout_groupBox_buttons)
        self.layoutGeneral.addWidget(self.groupBox_buttons)
        #-
        self.layout_groupBox_buttons.setColumnStretch(0, 3)
        self.layout_groupBox_buttons.setColumnStretch(1, 1)
        self.layout_groupBox_buttons.setColumnStretch(2, 1)
        self.layout_groupBox_buttons.setColumnStretch(3, 1)
        self.layout_groupBox_buttons.setColumnStretch(4, 3)
        #-
        self.pushButton = QtWidgets.QPushButton(self.DialogImportCSW)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(lambda : self.functionImport())
        self.layout_groupBox_buttons.addWidget(self.pushButton, 0, 1, Qt.AlignTop)
        #----------
        self.pushButtonAnnuler = QtWidgets.QPushButton(self.DialogImportCSW)
        self.pushButtonAnnuler.setObjectName("pushButtonAnnuler")
        self.pushButtonAnnuler.clicked.connect(self.DialogImportCSW.reject)
        self.layout_groupBox_buttons.addWidget(self.pushButtonAnnuler, 0, 3,  Qt.AlignTop)
        #--
        #----------
        self.DialogImportCSW.setWindowTitle(QtWidgets.QApplication.translate("plume_main", "PLUME (Metadata storage in PostGreSQL") + "  (" + str(returnVersion()) + ")")
        self.label_2.setText(QtWidgets.QApplication.translate("ImportCSW_ui", self.zMessTitle, None))
        self.pushButton.setText(QtWidgets.QApplication.translate("ImportCSW_ui", "Import", None))
        self.pushButtonAnnuler.setText(QtWidgets.QApplication.translate("ImportCSW_ui", "Cancel", None))
        
        #Lecture du tuple avec les paramétres  # Return Url and Id   
        url_csw, file_identifier = self.Dialog.metagraph.linked_record
        
        # Ajout des url par défaut temporairement
        mListurlCswTemp, mListliburlCswTemp = mListurlCsw, mListliburlCsw
        mListurlCswTemp.append(self.urlCswDefautGEOIDE)
        mListurlCswTemp.append(self.urlCswDefautIGN)
        mListliburlCswTemp.append(self.libUrlCswDefautGEOIDE)
        mListliburlCswTemp.append(self.libUrlCswDefautIGN)
        
        if url_csw != None :
           self.mZoneUrl.setText(url_csw)
           indexList = mListurlCswTemp.index(url_csw) if url_csw and url_csw in mListurlCswTemp else None
           self.mZoneLibUrl.setText(mListliburlCswTemp[indexList] if indexList != None else "")
        if file_identifier != None :
           self.mZoneUrlId.setText(file_identifier)

        #------ TREEVIEW Position importante 
        self.mTreeCSW = TREEVIEWCSW()
        self.layoutListeUrl.addWidget(self.mTreeCSW)
        #-
        self.mTreeCSW.clear()
        mListurlCswtemp = list(reversed(mListurlCsw))
        mListurlCswtemp = mListurlCsw

        self.mTreeCSW.afficheCSW(mListurlCswtemp, mListliburlCsw, self.mZoneUrl, self.mZoneLibUrl, self.mZoneUrlId)

        #------ TREEVIEW Position importante 
        
    #===============================              
    def functionAddCsw(self):
       zTitre = QtWidgets.QApplication.translate("ImportCSW_ui", "PLUME : Warning", None)
       zMess  = QtWidgets.QApplication.translate("ImportCSW_ui", "You must enter a URL of a CSW service.", None)
       if self.mZoneUrl.text() == "" or self.mZoneLibUrl.text() == "":
          displayMess(self, (2 if self.Dialog.displayMessage else 1), zTitre, zMess, Qgis.Warning, self.Dialog.durationBarInfo)
       else :   
          self.mTreeCSW.ihmsPlumeAddCSW(self.Dialog , self.mZoneUrl.text(), self.mZoneLibUrl.text())
       return

    #===============================              
    def functionImport(self):
       zTitre = QtWidgets.QApplication.translate("ImportCSW_ui", "PLUME : Warning", None)
       zMess  = QtWidgets.QApplication.translate("ImportCSW_ui", "You must enter a URL of a CSW service and a metadata record identifier.", None) 
       """
       #For test
       url_csw, file_identifier = "http://ogc.geo-ide.developpement-durable.gouv.fr","fr-120066022-jdd-1c02c1c1-cd81-4cd5-902e-acbd3d4e5527"
       #url_csw, file_identifier = "http://ogc.geo-ide.developpement-durable.gouv.fr/csw/dataset-harvestable","fr-120066022-jdd-23d6b4cd-5a3b-4e10-83ae-d8fdad9b04ab"
       #url_csw, file_identifier = "http://ogc.geo-ide.developpement-durable.gouv.fr/csw/all-dataset","fr-120066022-jdd-9618cc78-9b28-4562-8bbe-bede9bee2e9f"
       #url_csw, file_identifier = "http://ogc.geo-ide.developpement-durable.gouv.fr/csw/all-dataset","fr-120066022-jdd-a307d028-d9d2-4605-a1e5-8d31bc573bef"
       #
       raw_xml, old_metagraph = self.returnXml( url_csw, file_identifier ), self.Dialog.metagraph
       print(type(raw_xml))
       print( "DEBUT\n", raw_xml, "\nFIN")
       #For test
       #return
       """ 

       if self.mZoneUrl.text() == "" or self.mZoneUrlId.text() == "" :
          displayMess(self, (2 if self.Dialog.displayMessage else 1), zTitre, zMess, Qgis.Warning, self.Dialog.durationBarInfo)
       else :
          #options d'imports
          mOptions = "always"
          if self.option1.isChecked() :    # Compléter avec les métadonnées distantes : valeur 'always' (défaut).
             mOptions = "always"
          elif self.option2.isChecked() :  # Mettre à jour avec les métadonnées distantes : valeur 'if blank'.
             mOptions = "if blank"
          elif self.option3.isChecked() :  # Remplacer par les métadonnées distantes : valeur 'never'.
             mOptions = "never"

          #Retoune l'XML de l'appel URL + ID
          raw_xml, old_metagraph = self.returnXml( self.mZoneUrl.text(), self.mZoneUrlId.text() ), self.Dialog.metagraph                                            

          #- Cas ou le serveur CSW ne renvoie rien https://github.com/MTES-MCT/metadata-postgresql/issues/146 
          if raw_xml[0] == None : 
             zTitre = QtWidgets.QApplication.translate("ImportCSW_ui", "PLUME : Warning", None)
             zMess  = QtWidgets.QApplication.translate("ImportCSW_ui", "the server returned an error.", None) 
             displayMess(self, (2 if self.Dialog.displayMessage else 1), zTitre, zMess + '\n\nRéponse du serveur : « ' + raw_xml[2] + ' ».', Qgis.Warning, self.Dialog.durationBarInfo)
          else : 
             #NEW metagraph and OlD Metagraph
             metagraph = metagraph_from_iso(raw_xml[0], old_metagraph, mOptions)                                           
             
             #Sauvegarde l'URL et l'ID si case cochée
             if self.caseSave.isChecked() :
                metagraph.linked_record = self.mZoneUrl.text(), self.mZoneUrlId.text()

             self.Dialog.metagraph = metagraph

             #Regénère l'IHM
             saveObjetTranslation(self.Dialog.translation)
             self.Dialog.generationALaVolee(returnObjetsMeta(self.Dialog))
             
          self.close()
       return

    #===============================              
    def returnXml(self, url_csw, file_identifier) :
        resultQueryId = csw.getrecordbyid_request(url_csw, file_identifier)
        url = QUrl(resultQueryId)
        fetcher = QgsNetworkContentFetcher()
        fetcher.fetchContent(url)
        #-
        evloop = QEventLoop()
        fetcher.finished.connect(evloop.quit)
        evloop.exec_(QEventLoop.ExcludeUserInputEvents)
        fetcher.finished.disconnect(evloop.quit)
        #-
        raw_xml = [ fetcher.contentAsString() ]
        #- Cas ou le serveur CSW ne renvoie rien https://github.com/MTES-MCT/metadata-postgresql/issues/146 
        if raw_xml[0] == "" :
           ret = fetcher.reply()
           raw_xml = [ None, str(ret.error()), str(ret.errorString()) ]
        #-
        return raw_xml

#========================================================     
#========================================================     
# Class pour le tree View URL    
class TREEVIEWCSW(QTreeWidget):
    customMimeType = "text/plain"

    #===============================              
    def __init__(self, *args):
        QTreeWidget.__init__(self, *args)
        self.setColumnCount(2)
        self.setHeaderLabels(["Libellé", "URL"])
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.viewport().setAcceptDrops(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)  
        self.setSelectionMode(QAbstractItemView.SingleSelection	)  
        self.mnodeUrlUserToolTip = QtWidgets.QApplication.translate("ImportCSW_ui", "Right click to remove CSW URL", None)
        return

    #===============================              
    def startDrag(self, supportedActions):
        drag = QDrag(self)
        mimedata = self.model().mimeData(self.selectedIndexes())
        mimedata.setData(TREEVIEWCSW.customMimeType, QByteArray())
        drag.setMimeData(mimedata)
        drag.exec_(supportedActions)
        return
               
    #===============================              
    def afficheCSW(self, listeUrlCSW, listliburlCSW, _mZoneUrl, _mZoneLibUrl, _mZoneUrlId):
        self._mZoneUrl    = _mZoneUrl
        self._mZoneLibUrl = _mZoneLibUrl
        self._mZoneUrlId = _mZoneUrlId
        iconGestion = returnIcon(os.path.dirname(__file__) + "\\icons\\logo\\plume.svg")  
        #---
        self.header().setStretchLastSection(False)
        self.header().setSectionResizeMode(QHeaderView.ResizeToContents)

        # Url User
        self.mLibNodeUrlUser = "Mes CSW"
        self.insertTopLevelItems( 0, [ QTreeWidgetItem(None, [ self.mLibNodeUrlUser ] ) ] )
        self.nodeBlocsUser = self.topLevelItem( 0 )
        i = 0
        while i in range(len(listeUrlCSW)) :
           if str(listeUrlCSW[i]) not in URLCSWDEFAUT.split(",") :  
              nodeUrlUser = QTreeWidgetItem(None, [ str(listliburlCSW[i]), str(listeUrlCSW[i]) ])
              self.nodeBlocsUser.addChild( nodeUrlUser )
              nodeUrlUser.setToolTip(0, "{}".format(self.mnodeUrlUserToolTip))
              nodeUrlUser.setToolTip(1, "{}".format(self.mnodeUrlUserToolTip))
           i += 1
        # Url User
        #---
        # Url par défaut
        self.mLibNodeUrlDefaut = "CSW par défaut"
        self.insertTopLevelItems( 0, [ QTreeWidgetItem(None, [ self.mLibNodeUrlDefaut ] ) ] )
        nodeBlocs = self.topLevelItem( 0 )
        mListUrlDefaut    = URLCSWDEFAUT.split(",")
        mListLibUrlDefaut = LIBURLCSWDEFAUT.split(",")
        iListUrlDefaut = 0
        while iListUrlDefaut in range(len(mListUrlDefaut)) :
           mUrlDefaut    = mListUrlDefaut[iListUrlDefaut]
           mLibUrlDefaut = mListLibUrlDefaut[iListUrlDefaut]
           nodeUrlDefaut = QTreeWidgetItem(None, [ mLibUrlDefaut, mUrlDefaut ])
           nodeBlocs.addChild( nodeUrlDefaut )
           iListUrlDefaut += 1
        # Url par défaut

        self.itemClicked.connect( self.ihmsPlumeCSW ) 
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect( self.menuContextuelPlumeCSW)
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
    def menuContextuelPlumeCSW(self, point):
        index = self.indexAt(point)
        if not index.isValid():
           return
        #-------
        if index.data(0) != None : 
           if index.data(0) not in URLCSWDEFAUT.split(",") and index.data(0) not in LIBURLCSWDEFAUT.split(",") and index.data(0) != self.mLibNodeUrlDefaut and index.data(0) != self.mLibNodeUrlUser : 
              self.treeMenu = QMenu(self)
              menuIcon = returnIcon(os.path.dirname(__file__) + "\\icons\\general\\delete.svg")          
              treeActionCSW_delTooltip = QtWidgets.QApplication.translate("ImportCSW_ui", "Remove CSW URL", None)
              self.treeActionCSW_del = QAction(QIcon(menuIcon), treeActionCSW_delTooltip, self.treeMenu)
              self.treeMenu.addAction(self.treeActionCSW_del)
              self.treeActionCSW_del.setToolTip(treeActionCSW_delTooltip)
              self.treeActionCSW_del.triggered.connect( lambda : self.ihmsPlumeDelCSW(index) )
              #-------
              self.treeMenu.exec_(self.mapToGlobal(point))
        return
        
    #===============================              
    def ihmsPlumeCSW(self, item, column): 
        mItemClicUrlCsw = item.data(1, Qt.DisplayRole)
        mItemClicLibUrlCsw = item.data(0, Qt.DisplayRole)
        self._mZoneUrl.setText(mItemClicUrlCsw if mItemClicUrlCsw != None else "")
        self._mZoneLibUrl.setText(mItemClicLibUrlCsw if mItemClicUrlCsw != None else "")
        self._mZoneUrlId.setText("")
        return

    #===============================              
    def ihmsPlumeDelCSW(self, item): 
        current_item = self.currentItem()   #itemCourant
        self.nodeBlocsUser.removeChild(current_item) 
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
