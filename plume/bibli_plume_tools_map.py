# (c) Didier  LECLERC 2020 CMSIG MTE-MCTRCT/SG/SNUM/UNI/DRC Site de Rouen
# créé 2022

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui  import ( QIcon, QColor, QCursor )
from PyQt5.QtCore import ( Qt )

import qgis
from qgis.core import ( Qgis, QgsGeometry, QgsPointXY, QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsFeature, QgsCircle, QgsPoint, QgsCircularString, QgsProject )
from qgis.gui  import ( QgsMapTool, QgsRubberBand, QgsVertexMarker )
from math import sqrt, pi
from plume.bibli_plume import ( displayMess )

from plume.rdf.utils import split_rdf_wkt, wkt_with_srid

#==================================================
#==================================================
class GeometryMapTool(QgsMapTool ):
  def __init__(self, Dialog, _mAction, __mObjetQToolButton, __keyObjet, canvas, mAuthid, etat):
      QgsMapTool.__init__(self, canvas)
      self.canvas     = canvas
      self.mAuthid    = mAuthid
      self.etat       = etat
      self.Dialog     = Dialog
      self._mAction   = _mAction
      self.__keyObjet = __keyObjet 
      self.__mObjetQToolButton = __mObjetQToolButton
      self.iface = qgis.utils.iface 
      self.firstPolygon = True  #Début du polygon  
      
      if self._mAction in ["rectangle",] : 
         self.rubberBand = QgsRubberBand(self.canvas)
         #self.rubberBand = QgsRubberBand(self.canvas, True)
         self.rubberBand.setWidth(int(self.Dialog.geomEpaisseur))
      elif self._mAction in ["circle",] : 
         self.rubberBand = QgsRubberBand(self.canvas)
         #self.rubberBand = QgsRubberBand(self.canvas, True)
         self.rubberBand.setWidth(int(self.Dialog.geomEpaisseur))
      elif self._mAction in ["point",] :
         self.rubberBand = QgsVertexMarker(self.canvas)
         self.rubberBand.setPenWidth(int(self.Dialog.geomEpaisseur))
         self.rubberBand.setIconType(self.Dialog.mDicTypeObj[self.Dialog.geomPoint]) 
         self.rubberBand.setIconSize(int(self.Dialog.geomPointEpaisseur))
      elif self._mAction in ["polygon", "linestring"] : 
         self.rubberBand = QgsRubberBand(self.canvas)
         #self.rubberBand = QgsRubberBand(self.canvas, True)
         self.rubberBand.setWidth(int(self.Dialog.geomEpaisseur))
      self.rubberBand.setColor(QColor(self.Dialog.geomColor))
      self.etat = False

      self.reset()
      return
  #-----
  def reset(self):
      self.startPoint = self.endPoint = None
      self.isEmittingPoint = False

      if self._mAction in ["rectangle",] : 
         self.rubberBand.reset()
      elif self._mAction in ["circle",] : 
         self.rubberBand.reset()
      elif self._mAction in ["point",] :
         pass 
      elif self._mAction in ["linestring",] : 
         self.rubberBand.reset()
      elif self._mAction in ["polygon",] :
         self.rubberBand.reset()

      return
  #-----
  def canvasDoubleClickEvent(self, e):
      if self._mAction in ["polygon", "linestring"] : 
         self.Dialog.dic_geoToolsShow[self.__keyObjet] = False         # Param for display BBOX ou no
         majVisuButton(self, self.Dialog, self.__mObjetQToolButton, self.Dialog.dic_geoToolsShow, self.__keyObjet )
         #
         startPoint = self.toMapCoordinates(e.pos())
         endPoint   = startPoint
         point2 = QgsPointXY(endPoint.x(), endPoint.y())
         self.rubberBand.addPoint(point2, False) 
         
         if self._mAction in ["polygon"] : 
            point5 = self.startPolygon
            self.rubberBand.addPoint(point5, True)    # true to update canvas
         self.rubberBand.show()
         self.startPoint = self.endPoint = None
         self.isEmittingPoint = False
         self.firstPolygon = True
         #--
         if self._mAction in ["polygon"] : 
            geom_wkt = self.polygon()
         elif self._mAction in ["linestring"] : 
            geom_wkt = self.linestring()
         rdf_wkt = wkt_with_srid(geom_wkt, self.mAuthid)
         try :   #Nécessaire si l'instance d'outil unsetMapTool n'est pas supprimé
            self.Dialog.mDicObjetsInstancies[self.__keyObjet]['main widget'].setPlainText(rdf_wkt)
         except :
            pass   
         self.reset()
         QApplication.restoreOverrideCursor() 
         QApplication.restoreOverrideCursor() 
  #-----
  def canvasPressEvent(self, e):
      if self._mAction in ["polygon",] : 
         self.Dialog.dic_geoToolsShow[self.__keyObjet] = True         # Param for display BBOX ou no
      else :
         self.Dialog.dic_geoToolsShow[self.__keyObjet] = False         # Param for display BBOX ou no
         
      majVisuButton(self, self.Dialog, self.__mObjetQToolButton, self.Dialog.dic_geoToolsShow, self.__keyObjet )
       
      #Supprime si l'objet existe l'affichage du rubberBand
      if self._mAction not in ["polygon",] : 
         eraseRubberBand(self, self.Dialog.dic_objetMap, self.__keyObjet)

      QApplication.setOverrideCursor( QCursor( Qt.CrossCursor ) )
      #--
      try :
         if self._mAction not in ["polygon","linestring","circle"] :
            self.rubberBand.hide()
      except :
         pass   

      self.startPoint = self.toMapCoordinates(e.pos())
      self.endPoint = self.startPoint
      self.isEmittingPoint = True
      
      if self._mAction in ["rectangle",] : 
         self.showRect(self.startPoint, self.endPoint)
      elif self._mAction in ["circle",] :
         if not e.button() == Qt.LeftButton: return
         self.status = 1
         self.showCircle(self.rubberBand,self.startPoint,self.endPoint)
      elif self._mAction in ["point",] :
         self.showPoint(self.startPoint)
      elif self._mAction in ["linestring",] : 
         self.showPolygon(self.startPoint, self.endPoint)
      elif self._mAction in ["polygon",] : 
         self.showPolygon(self.startPoint, self.endPoint)
      return
  #-----
  def canvasReleaseEvent(self, e):
      if self._mAction not in ["polygon", "linestring"] : 
         self.isEmittingPoint = False
      
         if self._mAction in ["rectangle",] : 
            geom_wkt = self.rectangle()
         elif self._mAction in ["circle",] : 
            geom_wkt = self.circle()
         elif self._mAction in ["point",] :
            geom_wkt = self.point()
          
         rdf_wkt = wkt_with_srid(geom_wkt, self.mAuthid)
         try :   #Nécessaire si l'instance d'outil unsetMapTool n'est pas supprimé
            self.Dialog.mDicObjetsInstancies[self.__keyObjet]['main widget'].setPlainText(rdf_wkt)
         except :
            pass   
         self.reset()
         QApplication.restoreOverrideCursor() 
         QApplication.restoreOverrideCursor() 
      return
  #-----
  def canvasMoveEvent(self, e):
      if not self.isEmittingPoint:
        return

      self.endPoint = self.toMapCoordinates( e.pos() )
      
      if self._mAction in ["rectangle",] : 
         self.showRect(self.startPoint, self.endPoint)
      elif self._mAction in ["circle",] : 
         if not self.status == 1: return
         self.showCircle(self.rubberBand, self.startPoint, self.endPoint)
      elif self._mAction in ["point",] :
         self.showPoint(self.startPoint)
      elif self._mAction in ["linestring",] : 
         pass 
      elif self._mAction in ["polygon",] : 
         pass 
          
      return

  #==================================================
  #** -----
  #** Circle
  #** -----
  def showCircle(self, rubberBand, x, y) :
      rubberBand.reset()
      r = sqrt(x.sqrDist(y))
      feature = QgsFeature()
      feature.setAttributes([x, y, r])
      feature.setGeometry(QgsCircle(QgsPoint(x.x(), y.y()), r).toCircularString())
      self.rubberBand.addGeometry(feature.geometry(),None)
      self.rubberBand.show()
      return
  #-----     
  def circle(self):
      pointsCircle = [ QgsPointXY(self.rubberBand.getPoint(0, i)) for i in range(self.rubberBand.numberOfVertices()) ]
      geomCircleString = QgsCircularString()
      equi = len(pointsCircle)/4
      p1, p2, p3, p4, p5 = pointsCircle[int(equi*0)], pointsCircle[int(equi*1)], pointsCircle[int(equi*2)], pointsCircle[int(equi*3)], pointsCircle[int(equi*4) - 1]
      geomCircleString.setPoints([QgsPoint(p1), QgsPoint(p2), QgsPoint(p3), QgsPoint(p4), QgsPoint(p5)]) 
      return geomCircleString.asWkt(self.Dialog.geomPrecision)
      
  #==================================================
  #** -----
  #** polygone et linestring
  #** -----
  def showPolygon(self, startPoint, endPoint):
      if self.firstPolygon : 
         self.rubberBand.reset()
         point1 = QgsPointXY(startPoint.x(), startPoint.y())
         self.startPolygon = point1
         self.rubberBand.addPoint(point1, False)
         self.firstPolygon = False
      else :  
         point2 = QgsPointXY(endPoint.x(), endPoint.y())
         self.rubberBand.addPoint(point2, True)
      self.rubberBand.show()
      return
  #-----
  def polygon(self):
      pointsPolygon = [ QgsPointXY(self.rubberBand.getPoint(0, i)) for i in range(self.rubberBand.numberOfVertices()) ]
      #==
      return QgsGeometry.fromPolygonXY([ pointsPolygon ]).asWkt(self.Dialog.geomPrecision)

  #-----
  def linestring(self):
      pointsPolygon = [ QgsPointXY(self.rubberBand.getPoint(0, i)) for i in range(self.rubberBand.numberOfVertices()) ]
      #==
      return QgsGeometry.fromPolylineXY(pointsPolygon).asWkt(self.Dialog.geomPrecision)

  #==================================================
  #** -----
  #** rectangle
  #** -----
  def showRect(self, startPoint, endPoint):
      self.rubberBand.reset()
      if startPoint.x() == endPoint.x() or startPoint.y() == endPoint.y():
        return

      point1 = QgsPointXY(startPoint.x(), startPoint.y())
      point2 = QgsPointXY(startPoint.x(), endPoint.y())
      point3 = QgsPointXY(endPoint.x(), endPoint.y())
      point4 = QgsPointXY(endPoint.x(), startPoint.y())
      point5 = point1

      self.rubberBand.addPoint(point1, False)
      self.rubberBand.addPoint(point2, False)
      self.rubberBand.addPoint(point3, False)
      self.rubberBand.addPoint(point4, False) 
      self.rubberBand.addPoint(point5, True)    # true to update canvas
      self.rubberBand.show()
      return
  #-----
  def rectangle(self):
      if self.startPoint is None or self.endPoint is None:
        return None
      elif self.startPoint.x() == self.endPoint.x() or self.startPoint.y() == self.endPoint.y():
        return None
      #==
      pointsRectangle = [ QgsPointXY(self.rubberBand.getPoint(0, i)) for i in range(self.rubberBand.numberOfVertices()) ]
      return QgsGeometry.fromPolygonXY([ pointsRectangle ]).asWkt(self.Dialog.geomPrecision)

  #==================================================
  #** -----
  #** point
  #** -----
  def showPoint(self, startPoint):
      point1 = QgsPointXY(startPoint.x(), startPoint.y())
      self.rubberBand.setCenter(point1)
      return
  #-----
  def point(self):
      return QgsGeometry.fromPointXY(QgsPointXY(self.startPoint.x(), self.startPoint.y())).asWkt(self.Dialog.geomPrecision) if self.startPoint != None else None
  #** -----
  #** -----
  #==================================================
  
  #-----                                                  
  def deactivate(self):
      QgsMapTool.deactivate(self)
      self.deactivated.emit()
      QApplication.restoreOverrideCursor() 
      QApplication.restoreOverrideCursor() 
      return

#==================================================
#==================================================
class GeometryMapToolShow(QgsMapTool ):
  def __init__(self, Dialog, __keyObjet, canvas, mAuthid, mCoordSaisie, etat):
      QgsMapTool.__init__(self, canvas)
      self.canvas     = canvas
      self.mAuthid    = mAuthid
      self.iface      = qgis.utils.iface   
      self.__keyObjet = __keyObjet 
      self.Dialog     = Dialog

      #Supprime si l'objet existe l'affichage du rubberBand
      eraseRubberBand(self, self.Dialog.dic_objetMap, self.__keyObjet)
      if etat:
         res = split_rdf_wkt(mCoordSaisie)
         if res:
             geom_wkt, self.srid = res
             self.crs = QgsCoordinateReferenceSystem()
             try: 
                self.geom = QgsGeometry.fromWkt(geom_wkt)
                self.crs.createFromUserInput(self.srid)
             except: 
                zTitre = QtWidgets.QApplication.translate("bibli_plume_tools_map", "PLUME : Warning", None)
                zMess  = QtWidgets.QApplication.translate("bibli_plume_tools_map", "Invalid geometry or unsupported type.", None)  
                displayMess(self.Dialog, (2 if self.Dialog.displayMessage else 1), zTitre, zMess, Qgis.Warning, self.Dialog.durationBarInfo)
                return
        
             # NB. le type de géométrie du QgsRubberBand est automatiquement défini par setToGeometry
             self.rubberBand = QgsRubberBand(self.canvas)
             self.rubberBand.setToGeometry(self.geom, crs=self.crs)
        
             # configuration du QgsRubberBand :
             self.rubberBand.setWidth(int(self.Dialog.geomEpaisseur))
             self.rubberBand.setColor(QColor(self.Dialog.geomColor))
             self.rubberBand.setFillColor(QColor(255, 0, 0, 0)) # transparent
             
             # dont paramètres qui ne serviront qu'aux géométries ponctuelles :
             icon = getattr(QgsRubberBand, self.Dialog.geomPoint, QgsRubberBand.ICON_X)
             self.rubberBand.setIcon(icon)
             self.rubberBand.setIconSize(int(self.Dialog.geomPointEpaisseur))
              
             self.rubberBand.show()
             QApplication.restoreOverrideCursor() 
             QApplication.restoreOverrideCursor() 
        
             # Zoom si case cochée dans personnalisation de l'interface :
             if self.Dialog.geomZoom: 
                map_crs = QgsCoordinateReferenceSystem()
                map_crs.createFromUserInput(self.mAuthid)
                transform = QgsCoordinateTransform(self.crs, map_crs, QgsProject.instance())
                # New Dl 19/06/2023
                try: 
                   self.canvas.setExtent(transform.transformBoundingBox(self.geom.boundingBox()))
                except: 
                   zTitre = QtWidgets.QApplication.translate("bibli_plume_tools_map", "PLUME : Warning", None)
                   zMess  = QtWidgets.QApplication.translate("bibli_plume_tools_map", "Invalid geometry or unsupported type.", None)  
                   displayMess(self.Dialog, (2 if self.Dialog.displayMessage else 1), zTitre, zMess, Qgis.Warning, self.Dialog.durationBarInfo)
                   return
                # New Dl 19/06/2023
             self.canvas.redrawAllLayers()
      QApplication.setOverrideCursor( QCursor( Qt.ArrowCursor ) )
      return 

#==================================================
# Maj text, Icon, ToolTip
def majVisuButton(self, Dialog, __mObjetQToolButton, mDic_geoToolsShow, __keyObjet, __valueObjet = None) :
    self.Dialog = Dialog
    #__mObjetQToolButton.setText(self.Dialog._dicGeoTools['show' if mDic_geoToolsShow[__keyObjet] else 'hide']['libelle'])
    __mObjetQToolButton.setIcon(QIcon(self.Dialog._dicGeoTools['show' if mDic_geoToolsShow[__keyObjet] else 'hide']['icon']))
    if self.Dialog.mode == "edit" :
       __mObjetQToolButton.setToolTip(self.Dialog._dicGeoTools['show' if mDic_geoToolsShow[__keyObjet] else 'hide']['toolTip'] + "\n\nMaintenez la souris appuyée 2 à 3 secondes pour ouvrir le menu déroulant.")
    else :   
       __mObjetQToolButton.setToolTip(self.Dialog._dicGeoTools['show' if mDic_geoToolsShow[__keyObjet] else 'hide']['toolTip'])
    return

#==================================================
# Maj text, Icon, ToolTip
def eraseRubberBand(self, mDic, __keyObjet,) :
    try :
       mDic[__keyObjet].rubberBand.hide()
    except :
       pass       
    return

#==================================================
# FIN
#==================================================
