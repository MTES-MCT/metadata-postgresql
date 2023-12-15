
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


#===============================              
def returnXml(url_csw, file_identifier) :
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
        
#fr-120066022-jdd-b68be6c4-ef98-40df-88b0-d2a0979c5ff4

url  = "fr-120066022-jdd-b68be6c4-ef98-40df-88b0-d2a0979c5ff4"
mId  = "fr-120066022-jdd-b68be6c4-ef98-40df-88b0-d2a0979c5ff4"

raw_xml, old_metagraph = returnXml( mZoneUrl.text(), mId ), self.Dialog.metagraph                                            

