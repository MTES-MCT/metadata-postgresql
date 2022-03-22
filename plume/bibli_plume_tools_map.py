# (c) Didier  LECLERC 2020 CMSIG MTE-MCTRCT/SG/SNUM/UNI/DRC Site de Rouen
# créé 2022

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QAction, QMenu , QApplication
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import *

from qgis.core import *
from qgis.gui import *
import qgis
from math import sqrt,pi,sin,cos
import shapely.wkt
from shapely.geometry import Point, Polygon
from . import bibli_plume
from .bibli_plume import *

from plume.rdf.utils import split_rdf_wkt, geomtype_from_wkt, wkt_with_srid

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
         self.rubberBand = QgsRubberBand(self.canvas, True)
         self.rubberBand.setWidth(int(self.Dialog.geomEpaisseur))
      elif self._mAction in ["circle",] : 
         self.rubberBand = QgsRubberBand(self.canvas, True)
         self.rubberBand.setWidth(int(self.Dialog.geomEpaisseur))
      elif self._mAction in ["point",] :
         self.rubberBand = QgsVertexMarker(self.canvas)
         self.rubberBand.setPenWidth(int(self.Dialog.geomEpaisseur))
         self.rubberBand.setIconType(self.Dialog.mDicTypeObj[self.Dialog.geomPoint]) 
      elif self._mAction in ["polygon", "linestring"] : 
         self.rubberBand = QgsRubberBand(self.canvas, True)
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
         QApplication.setOverrideCursor( QCursor( Qt.ArrowCursor ) )  
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
         QApplication.setOverrideCursor( QCursor( Qt.ArrowCursor ) )  
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
      return geomCircleString.asWkt(4)
      
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
      return QgsGeometry.fromPolygonXY([ pointsPolygon ]).asWkt(4)

  #-----
  def linestring(self):
      pointsPolygon = [ QgsPointXY(self.rubberBand.getPoint(0, i)) for i in range(self.rubberBand.numberOfVertices()) ]
      #==
      return QgsGeometry.fromPolylineXY(pointsPolygon).asWkt(4)

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
      return QgsGeometry.fromPolygonXY([ pointsRectangle ]).asWkt(4)

  #==================================================
  #** -----
  #** point
  #** -----
  def showPoint(self, startPoint):
      point1 = QgsPointXY(startPoint.x(), startPoint.y())
      self.rubberBand.setCenter(point1)
      return
  #-----
  def point(self): return QgsGeometry.fromPointXY(QgsPointXY(self.startPoint.x(), self.startPoint.y())).asWkt(4)
  #** -----
  #** -----
  #==================================================
  
  #-----                                                  
  def deactivate(self):
      QgsMapTool.deactivate(self)
      self.deactivated.emit()
      QApplication.setOverrideCursor( QCursor( Qt.ArrowCursor ) )  
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

      if etat :
         res = split_rdf_wkt(mCoordSaisie)
         if res :
            #-
            try : 
               geom_wkt, self.srid = res
               if geomtype_from_wkt(mCoordSaisie) == "circularstring" :
                  mPolygone = geom_wkt
               else :   
                  mPolygone = shapely.wkt.loads(geom_wkt)
            except : 
               zTitre = QtWidgets.QApplication.translate("plume_ui", "PLUME : Warning", None)
               zMess  = QtWidgets.QApplication.translate("plume_ui", "Géométrie invalide ou type non pris en charge.", None)
               bibli_plume.displayMess(self.Dialog, (2 if self.Dialog.displayMessage else 1), zTitre, zMess, Qgis.Warning, self.Dialog.durationBarInfo)
               return
            #-
            if geomtype_from_wkt(mCoordSaisie) == "polygon" :
               self.rubberBand = QgsRubberBand(self.canvas, True)
               self.rubberBand.setWidth(int(self.Dialog.geomEpaisseur))
               self.showPolygon(mPolygone)
            elif geomtype_from_wkt(mCoordSaisie) == "rectangle" :
               self.rubberBand = QgsRubberBand(self.canvas, True)
               self.rubberBand.setWidth(int(self.Dialog.geomEpaisseur))
               self.startPoint = Point(mPolygone.bounds[0], mPolygone.bounds[1]) 
               self.endPoint   = Point(mPolygone.bounds[2], mPolygone.bounds[3]) 
               self.showRect(self.startPoint, self.endPoint)
            elif geomtype_from_wkt(mCoordSaisie) == "circularstring" :
               self.rubberBand = QgsRubberBand(self.canvas, True)
               self.rubberBand.setWidth(int(self.Dialog.geomEpaisseur))
               self.showCircle(mPolygone)
            elif geomtype_from_wkt(mCoordSaisie) == "point" : 
               self.rubberBand = QgsVertexMarker(self.canvas)
               self.rubberBand.setPenWidth(int(self.Dialog.geomEpaisseur))
               self.rubberBand.setIconType(self.Dialog.mDicTypeObj[self.Dialog.geomPoint]) 
               self.showPoint(mPolygone)
            elif geomtype_from_wkt(mCoordSaisie) == "linestring" :
               self.rubberBand = QgsRubberBand(self.canvas, False)
               self.rubberBand.setWidth(int(self.Dialog.geomEpaisseur))
               self.showLine(mPolygone)
            else :
               self.rubberBand = QgsRubberBand(self.canvas, False)
               self.rubberBand.setWidth(int(self.Dialog.geomEpaisseur))
               self.showLine(mPolygone)

            self.rubberBand.setColor(QColor(self.Dialog.geomColor))
            self.rubberBand.setFillColor(QColor(255, 0, 0, 0)) #For transparent
            self.rubberBand.show()
            
            #Zoom si case cochée dans personnalisation de l'interface
            if self.Dialog.geomZoom : 
               if geomtype_from_wkt(mCoordSaisie) == "point" : 
                  point1 = QgsPointXY(mPolygone.x, mPolygone.y)
                  point1 = transformSourceCibleLayer(self.srid, self.mAuthid, point1)
                  self.canvas.setExtent(QgsGeometry.fromWkt(point1.asWkt()).boundingBox())
               else :   
                  self.canvas.setExtent(QgsGeometry.fromWkt(self.rubberBand.asGeometry().boundingBox().asWktPolygon()).boundingBox())
      return 
  #-----
  def showCircle(self, pointsCircle):
      #Instanciation d'une géom QgsCircularString
      geomCircle = QgsCircularString()
      geomCircle.fromWkt(pointsCircle)
      #Lecture de chaque points pour la transformation
      points = geomCircle.points() 
      points = [ transformSourceCibleLayer(self.srid, self.mAuthid, QgsPointXY(p)) for p in points ]
      #Instanciation d'une géom QgsCircularString pour alimenter la géométrie du rubberBand
      feature = QgsFeature()
      geomCircleString = QgsCircularString()
      geomCircleString.setPoints(QgsPoint(p) for p in points)
      feature.setGeometry(geomCircleString)
      self.rubberBand.addGeometry(feature.geometry(),None)
      return 
  #-----        
  def showPolygon(self, pointsPolygone):
      points = [ transformSourceCibleLayer(self.srid, self.mAuthid, QgsPointXY(p[0], p[1])) for p in list(pointsPolygone.exterior.coords) ]
      self.rubberBand.setToGeometry(QgsGeometry.fromPolygonXY([ points ]), None)
      return 
  #-----
  def showLine(self, pointsLine):
      points = [ transformSourceCibleLayer(self.srid, self.mAuthid, QgsPointXY(p[0], p[1])) for p in pointsLine.coords ]
      self.rubberBand.setToGeometry(QgsGeometry.fromPolylineXY(points), None)
      return 
  #-----
  def showRect(self, startPoint, endPoint):
      self.rubberBand.reset()
      if startPoint.x == endPoint.x or startPoint.y == endPoint.y:
        return

      point1 = QgsPointXY(startPoint.x, startPoint.y)
      point5 = QgsPointXY(startPoint.x, startPoint.y) #Point5 = Point1
      point1 = transformSourceCibleLayer(self.srid, self.mAuthid, point1)
      point2 = QgsPointXY(startPoint.x, endPoint.y)
      point2 = transformSourceCibleLayer(self.srid, self.mAuthid, point2)
      point3 = QgsPointXY(endPoint.x, endPoint.y)
      point3 = transformSourceCibleLayer(self.srid, self.mAuthid, point3)
      point4 = QgsPointXY(endPoint.x, startPoint.y)
      point4 = transformSourceCibleLayer(self.srid, self.mAuthid, point4)
      point5 = transformSourceCibleLayer(self.srid, self.mAuthid, point5)

      self.rubberBand.addPoint(point1, False)
      self.rubberBand.addPoint(point2, False)
      self.rubberBand.addPoint(point3, False)
      self.rubberBand.addPoint(point4, False) 
      self.rubberBand.addPoint(point1, True)    # true to update canvas
      return 
  #-----
  def showPoint(self, startPoint):
      point1 = QgsPointXY(startPoint.x, startPoint.y)
      point1 = transformSourceCibleLayer(self.srid, self.mAuthid, point1)
      self.rubberBand.setCenter(point1)
      return 

#==================================================
# Transform système de projection
def transformSourceCibleLayer(crsSource, crsCible, mGeom) : 
    transform = QgsCoordinateTransform(QgsCoordinateReferenceSystem(crsSource), QgsCoordinateReferenceSystem(crsCible), QgsProject.instance())
    newmGeom = transform.transform(mGeom)
    return newmGeom

#==================================================
# Maj text, Icon, ToolTip
def majVisuButton(self, Dialog, __mObjetQToolButton, mDic_geoToolsShow, __keyObjet, __valueObjet = None) :
    self.Dialog = Dialog
    __mObjetQToolButton.setText(self.Dialog._dicGeoTools['show' if mDic_geoToolsShow[__keyObjet] else 'hide']['libelle'])
    __mObjetQToolButton.setIcon(QIcon(self.Dialog._dicGeoTools['show' if mDic_geoToolsShow[__keyObjet] else 'hide']['icon']))
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
