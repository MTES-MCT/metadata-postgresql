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
from . import bibli_gene_objets
from .bibli_gene_objets import *
#
from plume.rdf.metagraph import Metagraph, metagraph_from_iso
from plume.iso import csw 
from qgis.core import QgsNetworkContentFetcher
#
from qgis.core import  QgsSettings

class Ui_Dialog_ImportCSW(object):
    def setupUiImportCSW(self, DialogImportCSW, Dialog):
        self.DialogImportCSW = DialogImportCSW
        self.Dialog = Dialog   #Pour remonter les variables de la boite de dialogue
        self.zMessTitle    =  QtWidgets.QApplication.translate("ImportCSW_ui", "Import metadata from a CSW service", None)
        myPath = os.path.dirname(__file__)+"\\icons\\logo\\plume.svg"

        self.DialogImportCSW.setObjectName("DialogConfirme")
        self.DialogImportCSW.setFixedSize(900,570)
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
        self.lScreenDialog, self.hScreenDialog = int(self.DialogImportCSW.width()), int(self.DialogImportCSW.height())
        #------ 
        #--
        largeur = 150
        abscisse, ordonnee, largeur, hauteur = (self.DialogImportCSW.width() / 2) - largeur - 20 , self.DialogImportCSW.height() - 40, largeur, 25
        self.pushButton = QtWidgets.QPushButton(self.DialogImportCSW)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setGeometry(QtCore.QRect(abscisse, ordonnee, largeur, hauteur))
        self.pushButton.clicked.connect(lambda : self.functionImport())
        #----------
        abscisse, ordonnee, largeur, hauteur = (self.DialogImportCSW.width() / 2) + 20 , self.DialogImportCSW.height() - 40, largeur, 25
        self.pushButtonAnnuler = QtWidgets.QPushButton(self.DialogImportCSW)
        self.pushButtonAnnuler.setObjectName("pushButtonAnnuler")
        self.pushButtonAnnuler.setGeometry(QtCore.QRect(abscisse, ordonnee, largeur, hauteur))
        self.pushButtonAnnuler.clicked.connect(self.DialogImportCSW.reject)
        #--
        #------ 
        largeurLabel,  hauteurLabel   = 200, 20 
        abscisseLabel                 = 40 
        largeurSaisie, hauteurSaisie  = self.DialogImportCSW.width() - abscisseLabel - largeurLabel - 40 , 20
        abscisseSaisie                = abscisseLabel + largeurLabel + 10 
        ordonneeLabelSaisie           = 100
        deltaLabelSaisie              = hauteurLabel + 8
        hauteurListeUrl               = 200
        #------ 
        self.urlCswDefaut = Dialog.urlCswDefaut
        mListurlCsw = Dialog.urlCsw.split(",")
        self.urlCsw = Dialog.urlCsw
        #------
        #Liste URL / ID 
        abscisse, ordonnee, largeur, hauteur = abscisseLabel , ordonneeLabelSaisie, largeurLabel + largeurSaisie + 10, hauteurListeUrl
        groupBoxOptionsListeUrl = QtWidgets.QGroupBox(self.DialogImportCSW)
        groupBoxOptionsListeUrl.setGeometry(QtCore.QRect(abscisse, ordonnee, largeur, hauteur))
        groupBoxOptionsListeUrl.setObjectName("groupBoxOptionsListeUrl")
        groupBoxOptionsListeUrl.setStyleSheet("QGroupBox {   \
                              font-family:" + Dialog.policeQGroupBox  +" ; \
                              border-style: " + Dialog.lineQGroupBox  + ";    \
                              border-width:" + str(Dialog.epaiQGroupBox)  + "px ; \
                              border-color: " + Dialog.colorQGroupBoxGroupOfProperties  +";      \
                              }")
        self.groupBoxOptionsListeUrl = groupBoxOptionsListeUrl
        #-
        self.mTreeCSW = TREEVIEWCSW(groupBoxOptionsListeUrl)
        self.mTreeCSW.clear()
        
        mListurlCswtemp = list(reversed(mListurlCsw))
        mListurlCswtemp.append(Dialog.urlCswDefaut)
        self.mTreeCSW.afficheCSW(DialogImportCSW, mListurlCswtemp)
        #Liste URL / ID 
        #------ 

        #------ 
        ordonneeLabelSaisie = groupBoxOptionsListeUrl.y() + groupBoxOptionsListeUrl.height() + 10
        mLabelUrlText = QtWidgets.QApplication.translate("ImportCSW_ui", "CSW URL", None)
        mLabelUrlToolTip = QtWidgets.QApplication.translate("ImportCSW_ui", "URL of the CSW service, without any parameters.", None)
        mLabelUrl = QtWidgets.QLabel(self.DialogImportCSW)
        mLabelUrl.setStyleSheet("QLabel {  font-family:" + Dialog.policeQGroupBox  +"; background-color:" + Dialog.labelBackGround  +";}")
        mLabelUrl.setGeometry(QtCore.QRect(abscisseLabel, ordonneeLabelSaisie, largeurLabel,  hauteurLabel))
        mLabelUrl.setObjectName("mLabelUrl")
        mLabelUrl.setText(mLabelUrlText)
        mLabelUrl.setToolTip(mLabelUrlToolTip)
        mLabelUrl.setWordWrap(True)
        #- 
        mZoneUrl = QtWidgets.QLineEdit(self.DialogImportCSW)
        mZoneUrl.setStyleSheet("QLineEdit {  font-family:" + Dialog.policeQGroupBox  +";}")
        mZoneUrl.setGeometry(QtCore.QRect(abscisseSaisie, ordonneeLabelSaisie, largeurSaisie - 50, hauteurSaisie))
        mZoneUrl.setObjectName("mZoneUrl")
        mZoneUrl.setToolTip(mLabelUrlToolTip)
        mZoneUrl.setPlaceholderText(Dialog.urlCswDefaut)
        mZoneUrl.setText("")
        self.mZoneUrl = mZoneUrl
        #------ 
        ordonneeLabelSaisie           += deltaLabelSaisie
        mLabelUrlIdText = QtWidgets.QApplication.translate("ImportCSW_ui", "CSW ID", None)
        mLabelUrlIdToolTip = QtWidgets.QApplication.translate("ImportCSW_ui", "This identifier, not to be confused with the resource identifier, generally appears in the URL of the catalog file. This is the gmd: fileIdentifier property of XML.", None)
        mLabelUrlId = QtWidgets.QLabel(self.DialogImportCSW)
        mLabelUrlId.setStyleSheet("QLabel {  font-family:" + Dialog.policeQGroupBox  +"; background-color:" + Dialog.labelBackGround  +";}")
        mLabelUrlId.setGeometry(QtCore.QRect(abscisseLabel, ordonneeLabelSaisie, largeurLabel,  hauteurLabel))
        mLabelUrlId.setObjectName("mLabelUrlId")
        mLabelUrlId.setText(mLabelUrlIdText)
        mLabelUrlId.setToolTip(mLabelUrlIdToolTip)
        mLabelUrlId.setWordWrap(True)
        #- 
        mZoneUrlId = QtWidgets.QLineEdit(self.DialogImportCSW)
        mZoneUrlId.setStyleSheet("QLineEdit {  font-family:" + Dialog.policeQGroupBox  +";}")
        mZoneUrlId.setGeometry(QtCore.QRect(abscisseSaisie, ordonneeLabelSaisie, largeurSaisie - 50, hauteurSaisie))
        mZoneUrlId.setObjectName("mZoneUrlId")
        mZoneUrlId.setToolTip(mLabelUrlIdToolTip)
        mZoneUrlId.setPlaceholderText(Dialog.urlCswIdDefaut)
        mZoneUrlId.setText("")
        self.mZoneUrlId = mZoneUrlId
        #------
        #Button Add
        self.buttonAdd = QtWidgets.QToolButton(self.DialogImportCSW)
        self.buttonAdd.setGeometry(QtCore.QRect(abscisseSaisie + largeurSaisie - 40, mZoneUrl.y() - 3, 40, 25))
        self.buttonAdd.setObjectName("buttonAdd")
        self.buttonAdd.setIcon(QIcon(os.path.dirname(__file__)+"\\icons\\general\\save.svg"))
        self.buttonAdd.setToolTip("Ajouter la nouvelle URL saisie dans la liste.")
        self.buttonAdd.clicked.connect(lambda : self.functionAddCsw())
        #Button Add
        #------
        #------
        #Checkbox
        abscisse, ordonnee, largeur, hauteur = mZoneUrlId.x() , mLabelUrlId.y() + hauteurLabel + 5, 25, 25
        self.caseSave = QtWidgets.QCheckBox(self.DialogImportCSW)
        self.caseSave.setGeometry(QtCore.QRect(abscisse, ordonnee, largeur, hauteur))
        self.caseSave.setObjectName("caseSave")
        self.caseSave.setToolTip("Enregistrer la configuration dans les métadonnées.")
        self.caseSave.setStyleSheet("QCheckBox {  font-family:" + Dialog.policeQGroupBox  +"; }")
        self.caseSave.setChecked(True)       
        mLabelcaseSaveText = QtWidgets.QApplication.translate("ImportCSW_ui", "Save the configuration in the metadata", None)
        caseSaveToolTip = QtWidgets.QApplication.translate("ImportCSW_ui", "Save the configuration in the metadata.", None)
        abscisse, ordonnee, largeur, hauteur = mZoneUrlId.x() + 20, mLabelUrlId.y() + hauteurLabel + 4, 250, 25
        self.mLabelcaseSave = QtWidgets.QLabel(self.DialogImportCSW)
        self.mLabelcaseSave.setGeometry(QtCore.QRect(abscisse, ordonnee, largeur, hauteur))
        self.mLabelcaseSave.setObjectName("mLabelcaseSave")
        self.mLabelcaseSave.setStyleSheet("QLabel {  font-family:" + Dialog.policeQGroupBox  +"; background-color:" + Dialog.labelBackGround  +";}")
        self.mLabelcaseSave.setText(mLabelcaseSaveText)
        self.mLabelcaseSave.setToolTip(caseSaveToolTip)
        self.mLabelcaseSave.setWordWrap(True)
        #Checkbox
        #------
        #------
        #options 
        abscisse, ordonnee, largeur, hauteur = mLabelUrlId.x() , mLabelUrlId.y() + hauteurLabel + 35, largeurLabel + largeurSaisie + 10, 85
        groupBoxOptions = QtWidgets.QGroupBox(self.DialogImportCSW)
        groupBoxOptions.setGeometry(QtCore.QRect(abscisse, ordonnee, largeur, hauteur))
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
        self.option1 = QtWidgets.QRadioButton(groupBoxOptions)
        self.option1.setGeometry(QtCore.QRect(15,15,largeur - 20,23))
        self.option1.setObjectName("option1")
        self.option1.setText(QtWidgets.QApplication.translate("ImportCSW_ui", "Complete with remote metadata", None)) 
        self.option1.setStyleSheet("QRadioButton {  font-family:" + Dialog.policeQGroupBox  +";}")
        self.option1.setToolTip(QtWidgets.QApplication.translate("ImportCSW_ui", "For all metadata categories entered in the catalog record that do not have a value in the local record, the value of the remote record is added.", None))
        #-
        self.option2 = QtWidgets.QRadioButton(groupBoxOptions)
        self.option2.setGeometry(QtCore.QRect(15,35,largeur - 20,23))
        self.option2.setObjectName("option2")
        self.option2.setText(QtWidgets.QApplication.translate("ImportCSW_ui", "Update with remote metadata", None))  
        self.option2.setStyleSheet("QRadioButton {  font-family:" + Dialog.policeQGroupBox  +";}")
        self.option2.setToolTip(QtWidgets.QApplication.translate("ImportCSW_ui", "For all metadata categories entered in the catalog record, the value of the local record is replaced by that of the catalog or added if there was no value.", None))
        #-
        self.option3 = QtWidgets.QRadioButton(groupBoxOptions)
        self.option3.setGeometry(QtCore.QRect(15,55,largeur - 20,23))
        self.option3.setObjectName("option3")
        self.option3.setText(QtWidgets.QApplication.translate("ImportCSW_ui", "Replace with remote metadata", None))  
        self.option3.setStyleSheet("QRadioButton {  font-family:" + Dialog.policeQGroupBox  +";}")
        self.option3.setToolTip(QtWidgets.QApplication.translate("ImportCSW_ui", "Generates a new form from remote metadata. The difference with option 1 is that the information of the categories not filled in the catalog record but which could have existed locally will be erased.", None))
        self.option1.setChecked(True)
        #options 
        #------ 
        #----------
        self.DialogImportCSW.setWindowTitle(QtWidgets.QApplication.translate("plume_main", "PLUME (Metadata storage in PostGreSQL") + "  (" + str(bibli_plume.returnVersion()) + ")")
        self.label_2.setText(QtWidgets.QApplication.translate("ImportCSW_ui", self.zMessTitle, None))
        self.pushButton.setText(QtWidgets.QApplication.translate("ImportCSW_ui", "Import", None))
        self.pushButtonAnnuler.setText(QtWidgets.QApplication.translate("ImportCSW_ui", "Cancel", None))
        
        #Lecture du tuple avec les paramétres  # Return Url and Id   
        url_csw, file_identifier = self.Dialog.metagraph.linked_record
        
        if url_csw != None :
           self.mZoneUrl.setText(url_csw)
        if file_identifier != None :
           self.mZoneUrlId.setText(file_identifier)
        
    #===============================              
    def functionAddCsw(self):
       zTitre = QtWidgets.QApplication.translate("ImportCSW_ui", "PLUME : Warning", None)
       zMess  = QtWidgets.QApplication.translate("ImportCSW_ui", "You must enter a URL of a CSW service.", None)
       if self.mZoneUrl.text() == "" :
          bibli_plume.displayMess(self, (2 if self.Dialog.displayMessage else 1), zTitre, zMess, Qgis.Warning, self.Dialog.durationBarInfo)
       else :   
          self.mTreeCSW.ihmsPlumeAddCSW(self.Dialog , self.mZoneUrl.text())
       return

    #===============================              
    def functionImport(self):
       zTitre = QtWidgets.QApplication.translate("ImportCSW_ui", "PLUME : Warning", None)
       zMess  = QtWidgets.QApplication.translate("ImportCSW_ui", "You must enter a URL of a CSW service and a metadata record identifier.", None) 
       if self.mZoneUrl.text() == "" or self.mZoneUrlId.text() == "" :
          bibli_plume.displayMess(self, (2 if self.Dialog.displayMessage else 1), zTitre, zMess, Qgis.Warning, self.Dialog.durationBarInfo)
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

          #For test
          #url_csw, file_identifier = "http://ogc.geo-ide.developpement-durable.gouv.fr","fr-120066022-jdd-1c02c1c1-cd81-4cd5-902e-acbd3d4e5527"
          #url_csw, file_identifier = "http://ogc.geo-ide.developpement-durable.gouv.fr/csw/harvestable-dataset","fr-120066022-jdd-23d6b4cd-5a3b-4e10-83ae-d8fdad9b04ab"
          #url_csw, file_identifier = "http://ogc.geo-ide.developpement-durable.gouv.fr/csw/all-dataset","fr-120066022-jdd-9618cc78-9b28-4562-8bbe-bede9bee2e9f"
          #url_csw, file_identifier = "http://ogc.geo-ide.developpement-durable.gouv.fr/csw/all-dataset","fr-120066022-jdd-a307d028-d9d2-4605-a1e5-8d31bc573bef"
          #
          #raw_xml, old_metagraph = self.returnXml( url_csw, file_identifier ), self.Dialog.metagraph
          #For test
           
          #NEW metagraph and OlD Metagraph
          metagraph = metagraph_from_iso(raw_xml, old_metagraph, mOptions)                                           
          
          #Sauvegarde l'URL et l'ID si case cochée
          if self.caseSave.isChecked() :
             metagraph.linked_record = self.mZoneUrl.text(), self.mZoneUrlId.text()

          self.Dialog.metagraph = metagraph

          #Regénère l'IHM
          bibli_plume.saveObjetTranslation(self.Dialog.translation)
          self.Dialog.generationALaVolee(bibli_plume.returnObjetsMeta(self.Dialog))
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
        raw_xml = fetcher.contentAsString()
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
        self.setColumnCount(1)
        self.setHeaderLabels(["URL de CSW mémorisées"])
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.viewport().setAcceptDrops(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)  
        self.setSelectionMode(QAbstractItemView.SingleSelection	)  
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
    def afficheCSW(self, DialogImportCSW, listeUrlCSW):
        self.DialogImportCSW = DialogImportCSW 
        iconGestion = bibli_plume.returnIcon(os.path.dirname(__file__) + "\\icons\\logo\\logo.png")
        self.setGeometry(5, 5, self.DialogImportCSW.groupBoxOptionsListeUrl.width() - 10, self.DialogImportCSW.groupBoxOptionsListeUrl.height() - 10 )
        #---
        self.header().setStretchLastSection(False)
        self.header().setSectionResizeMode(QHeaderView.ResizeToContents)

        i = 0
        while i in range(len(listeUrlCSW)) :
           self.insertTopLevelItems( 0, [ QTreeWidgetItem(None, [ str(listeUrlCSW[i]) ] ) ] )
           root = self.topLevelItem( 0 )
           root.setIcon(0, iconGestion)
           if str(listeUrlCSW[i]) != self.DialogImportCSW.urlCswDefaut : 
              root.setToolTip(0, "{}".format("Clic droit pour supprimer l'URL CSW"))
           i += 1
        self.itemClicked.connect( self.ihmsPlumeCSW ) 
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect( self.menuContextuelPlumeCSW)
        return

    #===============================              
    def dragEnterEvent(self, event):    #//DEPART
        self.mDepart = ""
        selectedItems = self.selectedItems()
        if len(selectedItems) < 1:
            return
        mItemWidget = selectedItems[0].text(0)
        
        if event.mimeData().hasFormat('text/plain'):
           self.mDepart = mItemWidget
           event.accept()
        return

    #===============================              
    def dragMoveEvent(self, event):    #//EN COURS
        index = self.indexAt(event.pos())  

        try :
           r = self.itemFromIndex(index).text(0)
           mParentItem = self.itemFromIndex(index).parent()
           if mParentItem == None :
              event.accept()
           else :
              event.ignore()
        except :
           event.ignore()
        return

    #===============================              
    def dropEvent(self, event):  #//ARRIVEE
        index = self.indexAt(event.pos())
        r = self.itemFromIndex(index).text(0)
        try :
           #----
           mIndex = 0  
           while mIndex < self.topLevelItemCount() :
              if self.mDepart == self.topLevelItem(mIndex).text(0) :
                 self.takeTopLevelItem(mIndex)
                 break
              mIndex += 1
           #----
           mIndex = 0  
           while mIndex < self.topLevelItemCount() :
              if r == self.topLevelItem(mIndex).text(0) :
                 self.insertTopLevelItem(mIndex,  QTreeWidgetItem(None, [ str(self.mDepart) ] ) )
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
        if index.data(0) != self.DialogImportCSW.urlCswDefaut : 
           self.treeMenu = QMenu(self)
           menuIcon = returnIcon(os.path.dirname(__file__) + "\\icons\\general\\delete.svg")          
           self.treeActionCSW_del = QAction(QIcon(menuIcon), "Supprimer l'URL CSW", self.treeMenu)
           self.treeMenu.addAction(self.treeActionCSW_del)
           self.treeActionCSW_del.setToolTip("Supprimer l'URL CSW")
           self.treeActionCSW_del.triggered.connect( lambda : self.ihmsPlumeDelCSW(index) )
           #-------
           self.treeMenu.exec_(self.mapToGlobal(point))
        return
        
    #===============================              
    def ihmsPlumeCSW(self, item, column): 
        mItemClicUrlCsw = item.data(0, Qt.DisplayRole)
        self.DialogImportCSW.mZoneUrl.setText(mItemClicUrlCsw)
        return

    #===============================              
    def ihmsPlumeDelCSW(self, item): 
        mItemWidgetID  = item       #Id
        mItemWidgetLIB = mItemWidgetID.data(0)  #Lib
        #----
        mIndex = 0  
        while mIndex < self.topLevelItemCount() :
           if mItemWidgetLIB == self.topLevelItem(mIndex).text(0) :
              self.takeTopLevelItem(mIndex)
              break
           mIndex += 1
        return

    #===============================              
    def ihmsPlumeAddCSW(self, mDialog, mCsw):
        _save = True
        iterator = QTreeWidgetItemIterator(self)
        while iterator.value() :
           itemValueText = iterator.value().text(0)
           if str(mCsw) == itemValueText :
              zTitre = QtWidgets.QApplication.translate("ImportCSW_ui", "PLUME : Warning", None)
              zMess  = QtWidgets.QApplication.translate("ImportCSW_ui", "The URL already exists in the list.", None)  
              bibli_plume.displayMess(self, (2 if mDialog.displayMessage else 1), zTitre, zMess, Qgis.Warning, mDialog.durationBarInfo)
              _save = False
              break
           iterator += 1
        if _save : self.addTopLevelItems( [ QTreeWidgetItem(None, [ str(mCsw) ] ) ] )
        return
