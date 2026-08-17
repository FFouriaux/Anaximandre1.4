# -*- coding: utf-8 -*-
"""
/***************************************************************************
Auto3dShp
								 A QGIS plugin
 Génération de couches vectorielles de Polygone, Lignes et Points en 3D shp
							 -------------------
		begin                : 2016-01
		new version          : 2026-08-17
		copyright            : 2026 F.Fouriaux
		email                : francois.fouriaux@cnrs.fr
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 3 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
from qgis.core import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.utils import *
from qgis.gui import *
from qgis.PyQt.QtWidgets import QProgressBar
from math import *
import csv

# # F. Fouriaux April 2026
# # create automaticaly 3D polygon with a csv file from topographic survey
# # engine of Anaximandre



def Auto3DShp(CSV,Shape3D):
	
	# Creation des fichiers de sortie
	# Couche shp 3D 
	crsproject=iface.mapCanvas().mapSettings().destinationCrs()           # crs du projet

	champs=QgsFields()                                                    # creation des champs du shp
	champs.append(QgsField("US",QVariant.String))
	champs.append(QgsField("Description",QVariant.String))
	champs.append(QgsField("Z",QVariant.Double))
	# fichier polygone
	fichierPolygon=Shape3D+'/Polygon.gpkg'
	writerPoly = QgsVectorFileWriter(fichierPolygon,"utf-8",champs,Qgis.WkbType.PolygonZ,crsproject)
	#fichier ligne
	fichierPolyline=Shape3D+'/Line.gpkg'
	writerLine = QgsVectorFileWriter(fichierPolyline,"utf-8",champs,Qgis.WkbType.LineStringZ,crsproject)
	#fichier point topo (ortho, coupes, plans, stations, etc.)
	fichierPointTopo=Shape3D+'/Topo.gpkg'
	writerPt = QgsVectorFileWriter(fichierPointTopo,"utf-8",champs,Qgis.WkbType.PointZ,crsproject)
	#fichiers isolats
	fichierISO=Shape3D+'/ISO.gpkg'
	writerISO = QgsVectorFileWriter(fichierISO,"utf-8",champs,Qgis.WkbType.PointZ,crsproject)
	#Fichier MNT
	fichierMNT =  Shape3D+'/PtMNT.gpkg'
	writerMNT= QgsVectorFileWriter(fichierMNT,"utf-8",champs,Qgis.WkbType.PointZ,crsproject)

	# parametres fin de ligne OS
	windows='\r\n'
	linux='\n'

	# lecture du csv
	file=open(CSV,'r')
	entete=file.readline().split(',')          # 1ere ligne en list[]en tete
	
	#ProgressBar
	#row_count=sum(1 for row in file)
	#progressMessageBar = iface.messageBar().createMessage("traitement en cours...")
	#progress = QProgressBar()
	#progress.setMaximum(row_count)
	#progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
	#progressMessageBar.layout().addWidget(progress)
	#iface.messageBar().pushWidget(progressMessageBar, Qgis.Info)

	# determination des caracteres de fin de ligne
	der=entete[len(entete)-1]
	finl=der[len(der)-2]
	if finl=='\r':
		finligne=windows
	else:
		finligne=linux
		
	line=file.readline().split(',')
	# texte de base
	WktPoly='POLYGONZ(('
	WktLine='LINESTRINGZ('
	WktPoint='PointZ('
	# parcours du fichier

	while len(line)>1:
		i=0 
		if line[6]=='p':                                                      # si geom = polygone
			US=line[4]
			Desc=line[5]
			Z=[float(line[3])]
			pt=''
			pt1='%s %s %s,' %(str(line[1]), str(line[2]), str(line[3]))         # point de fermeture
			while len(line)>1 and line[4]==US and line[5]==Desc and line[6]=='p':
				
				pt+='%s %s %s,' %(str(line[1]), str(line[2]), str(line[3]))     # liste points 3D format texte
				Z.append(float(line[3]))										 # liste des Z                                   
				line=file.readline().split(',')
                              
			
			Zmoy=sum(Z)/len(Z)
			WktF=WktPoly+pt+pt1+'))'                                                #PolygonZ format texte
			wktgeom=QgsGeometry.fromWkt(WktF)
			poly=QgsFeature()
			poly.setGeometry(wktgeom)
			poly.setAttributes([US,Desc,Zmoy])
			writerPoly.addFeature(poly)
			
		elif line[6]=='l':                                                    # si geom = ligne
			US=line[4]
			Desc=line[5]
			Z=[]
			pt=''
			while len(line)>1 and line[4]==US and line[5]==Desc and line[6]=='l':
				
				pt+='%s %s %s,' %(str(line[1]), str(line[2]), str(line[3]))     # liste points 3D format texte
				Z.append(float(line[3]))                                        # liste des Z
				line=file.readline().split(',')

				
			pt=pt.strip(',')
			Zmoy=sum(Z)/len(Z)
			WktF=WktLine+pt+')'                                                #PolylineZ format texte
			poly2=QgsFeature()
			poly2.setGeometry(QgsGeometry.fromWkt(WktF))
			poly2.setAttributes([US,Desc,Zmoy])
			writerLine.addFeature(poly2)
			
		elif line[6]=='iso':                                                    # si geom = iso
			US=line[4]
			Desc=line[5]
			Z=float(line[3])
			pt='%s %s %s' %(str(line[1]), str(line[2]), str(line[3]))

			WktF=WktPoint+pt+')'                                                #PointZ format texte
			iso=QgsFeature()
			iso.setGeometry(QgsGeometry.fromWkt(WktF))
			iso.setAttributes([US,Desc,Z])
			writerISO.addFeature(iso)
			line=file.readline().split(',')
			
		elif line[6]=='pt':                                                    # si geom = pt
			US=line[4]
			Desc=line[5]
			Z=float(line[3])
			pt='%s %s %s' %(str(line[1]), str(line[2]), str(line[3]))

			WktF=WktPoint+pt+')'                                                #PointZ format texte
			poly3=QgsFeature()
			poly3.setGeometry(QgsGeometry.fromWkt(WktF))
			poly3.setAttributes([US,Desc,Z])
			writerPt.addFeature(poly3)
			line=file.readline().split(',')

			
		elif line[6]=='pt cpe':                                                    # si geom = point de coupe
			US=line[4]
			Desc=line[5]
			Z=[]
			ligne=''
			while len(line)>1 and line[4]==US and line[6] == 'pt cpe' and line[5]==Desc:           # cree les points et la ligne de cpe
				
				ligne+='%s %s %s,' %(str(line[1]), str(line[2]), str(line[3]))
				Z.append(float(line[3]))
				Zpt=float(line[3])
				pt='%s %s %s' %(str(line[1]), str(line[2]), str(line[3]))
				WktF=WktPoint+pt+')'                                                #PointZ format texte des points de cpe
				poly3=QgsFeature()
				poly3.setGeometry(QgsGeometry.fromWkt(WktF))
				poly3.setAttributes([US,Desc,Zpt])
				writerPt.addFeature(poly3)
				line=file.readline().split(',')
				
			ligne=ligne.strip(',')
			Zmoy=sum(Z)/len(Z)
			WktF=WktLine+ligne+')'                                                #PolylineZ format texte de la coupe
			poly2=QgsFeature()
			poly2.setGeometry(QgsGeometry.fromWkt(WktF))
			poly2.setAttributes([US,Desc,Zmoy])
			writerLine.addFeature(poly2)
		
		elif line[6]=='pt mnt':
			US=line[4]
			Desc=line[5]
			Z=[]
			ligne=''
			while len(line)>1 and line[4]==US and line[6] == 'pt mnt' and line[5]==Desc:           # cree les points et l envelope englobante du mnt
				ligne+='%s %s %s,' %(str(line[1]), str(line[2]), str(line[3]))
				Z.append(float(line[3]))
				Zpt=float(line[3])
			
				pt='%s %s %s' %(str(line[1]), str(line[2]), str(line[3]))
			
				WktF=WktPoint+pt+')'                                                                            #PointZ format texte
				poly3=QgsFeature()
				poly3.setGeometry(QgsGeometry.fromWkt(WktF))
				poly3.setAttributes([US,Desc,Zpt])
				writerMNT.addFeature(poly3)
				line=file.readline().split(',')
			
				
			ligne=ligne.strip(',')
			Zmoy=sum(Z)/len(Z)
			WktF=WktLine+ligne+')'                                                #PolylineZ format texte pour creation de l envelope
			poly2=QgsFeature()
			poly2.setGeometry(QgsGeometry.fromWkt(WktF))
			chmnt=poly2.geometry().convexHull().asPolygon()
			chmntgeom=QgsGeometry.fromPolygonXY(chmnt)                                    # envelope englobante
			polyMnt=QgsFeature()                                                               # polygon du mnt
			polyMnt.setGeometry(chmntgeom)
			polyMnt.setAttributes([US,Desc,Zmoy])
			writerPoly.addFeature(polyMnt)
			
		elif line[6]=='c':                                                        # si geom = cercle avec point central + diametre
			US=line[4]
			Desc=line[5]
			Z=float(line[3])
			rayon=float(line[7])
			
			pt='%s %s %s' %(str(line[1]), str(line[2]), str(line[3]))             # Point 3D format texte

			WktF=WktPoint+pt+')'                                               #PointZ format texte
			ptcenter=QgsFeature()
			ptcenter.setGeometry(QgsGeometry.fromWkt(WktF))
			cercle=ptcenter.geometry().buffer(rayon,20).asWkt()
			listCercle=''
			l1c=cercle.split('((')
			l2c=l1c[1].split('))')
			l3c=l2c[0].split(',')
			for n in l3c:
				listCercle+= '%s %s,' %(n,str(Z))
			WktF=WktPoly+listCercle+'))'                                                #PolygonZ format texte
			wktgeom=QgsGeometry.fromWkt(WktF)
			poly=QgsFeature()
			poly.setGeometry(wktgeom)
			poly.setAttributes([US,Desc,Z])
			writerPoly.addFeature(poly)
			line=file.readline().split(',')
			
		elif line[6]=='c2pt':                                                        # si geom = cercle avec 2 points
			
			US=line[4]
			Desc=line[5]
			Z=[]
			X=[]
			Y=[]
			X.append(float(line[1]))
			Y.append(float(line[2]))
			Z.append(float(line[3]))
			line=file.readline().split(',')
			X.append(float(line[1]))
			Y.append(float(line[2]))
			Z.append(float(line[3]))
			
			xpt=sum(X)/2
			ypt=sum(Y)/2
			zpt=sum(Z)/2
			pt='%s %s %s' %(str(xpt), str(ypt), str(zpt))             # point moyen
			distX=(X[0]-X[1])*(X[0]-X[1])
			distY=(Y[0]-Y[1])*(Y[0]-Y[1])
			rayon=sqrt(distX + distY)/2
			
			WktF=WktPoint+pt+')'                                               #PointZ format texte
			ptcenter=QgsFeature()
			ptcenter.setGeometry(QgsGeometry.fromWkt(WktF))
			cercle=ptcenter.geometry().buffer(rayon,20).asWkt()
			listCercle=''
			l1c=cercle.split('((')
			l2c=l1c[1].split('))')
			l3c=l2c[0].split(',')
			for n in l3c:
				listCercle+= '%s %s,' %(n,str(zpt))
			WktF=WktPoly+listCercle+'))'                                                #PolygonZ format texte
			wktgeom=QgsGeometry.fromWkt(WktF)
			poly=QgsFeature()
			poly.setGeometry(wktgeom)
			poly.setAttributes([US,Desc,Z])
			writerPoly.addFeature(poly)
			line=file.readline().split(',')

			
		else:
			line=file.readline().split(',')

			

	del writerPoly
	del writerLine
	del writerPt
	del writerISO
	del writerMNT

	# chargement dans le Canevas
	providerstring='ogr'
	if Shape3D=='':
		providerstring='memory'
	listLayers=[]   
	layer=QgsVectorLayer(fichierPolygon,'Polygones', providerstring)
	if layer.featureCount() >0:
		listLayers.append(layer)
	layer2=QgsVectorLayer(fichierPolyline,'Lignes', providerstring)
	if layer2.featureCount() >0:
		listLayers.append(layer2)
	layer3=QgsVectorLayer(fichierISO,'ISO', providerstring)
	if layer3.featureCount() >0:
		listLayers.append(layer3)
	layer4=QgsVectorLayer(fichierPointTopo,'PtTopo', providerstring)
	if layer4.featureCount() >0:
		listLayers.append(layer4)
	layer5=QgsVectorLayer(fichierMNT,'PtMNT', providerstring)
	if layer5.featureCount() >0:
		listLayers.append(layer5)
	QgsProject.instance().addMapLayers(listLayers)
	layers =  QgsProject.instance().mapLayers()
	map_canvas_layer_list = [l for l in layers.values()]
	QgsMapCanvas().setLayers(map_canvas_layer_list)
	QgsMapCanvas().setExtent(iface.mapCanvas().extent())
	iface.messageBar().pushMessage(u'Success' , u' Dessins crees', level=Qgis.MessageLevel.Success, duration=3)
