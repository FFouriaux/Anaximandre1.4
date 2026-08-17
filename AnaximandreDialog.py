# -*- coding: utf-8 -*-
"""
/***************************************************************************
Anaximandre
								 A QGIS plugin
 A plugin for auto drawing 3D Shapefiles from topographical survey. 
							 -------------------
		begin                : 2016-01
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

#using Unicode for all strings
from __future__ import unicode_literals

from builtins import str
import os

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtCore import QSettings
from qgis.utils import *
from qgis.core import *
from qgis.gui import *
import ntpath
import pathlib

localelang = QSettings().value('locale/userLocale')[0:2]

def selectLayer(layerName):
	layers=QgsProject.instance().mapLayers().values()
	for l in layers:
		if l.name() == layerName:
			return l

def AjoutLayer(fileName):
	if os.name=='nt':
		fileName='/'+fileName
	fileUri= pathlib.Path(fileName).as_uri()
	nom= ntpath.basename(fileName)
	iface.addVectorLayer(fileUri,nom,"delimitedtext")



class AnaxDialg(QDialog):
	def __init__(self):
		QDialog.__init__(self)
	
	# Show the structuration of the csv file needed   
	def listeCodes(self):
		if localelang =='fr':
			codif=['Num : numéro de point','X : coordonnée Est','Y : coordonnée Nord','Z: altitude','US : champ de regroupement','Desc : decription','Code : géométrie', 'Code2 : diametre(option)']
		else: 
			codif=['Num : id of the point','X : east coordinate', 'Y : north Coordinate','Z : altitude','US : grouping field','Desc : description','Code : geometry', 'Code2 : diameter (optional)']
		for n in codif:
			self.listCodes.addItem(n)
		
	 
	# list of layers 'csv' already charged in the interface   
	def layerList(self):
		layers = QgsProject.instance().mapLayers().values()
		layer_list = []
		self.cbox_FichierCsv.clear()
		for layer in layers:
			if layer.providerType()== 'delimitedtext':
				layer_list.append(layer.name())
		
		self.cbox_FichierCsv.addItems(layer_list)

	def selectedLayer(self):
	 
		if self.cbox_FichierCsv.currentText():
			return selectLayer(self.cbox_FichierCsv.currentText())


	# adopted from 'points2one Plugin'
	# Copyright (C) 2010 Pavol Kapusta
	# Copyright (C) 2010, 2013 Goyo
	# Copyright (C) Hatami 2014   

	def updateFieldCombos(self):
		self.listChp.clear()
		layer = self.selectedLayer()
		if layer is not None:            
			fields = layer.dataProvider().fields()
			for field in fields:
				name = field.name()
				self.listChp.addItem(name)

   
	def selectDirectory(self):
		self.lineEdit.setText(QFileDialog.getExistingDirectory(self))

	def OpenCsv(self):
		filtre= 'Text files (*.csv *.txt)'
		FileName= QFileDialog(filter=filtre)
		if FileName.exec():
			fileName=FileName.selectedFiles()
		AjoutLayer(fileName[0]) 
		self.layerList()

	# adopted from 'points2one Plugin'
	# Copyright (C) 2010 Pavol Kapusta
	# Copyright (C) 2010, 2013 Goyo
	def showWarning(self, engine):
		
		logMsg = '\n'.join(engine.getLogger())
		if logMsg:
			warningBox = QMessageBox(self)
			warningBox.setWindowTitle('Anaximandre')
			message = QtGui.QApplication.translate("SDialog","Output Shapefile created.", None, QtGui.QApplication.UnicodeUTF8)
			warningBox.setText(message)
			message = QtGui.QApplication.translate("SDialog","There were some issues, maybe some features could not be created.", None, QtGui.QApplication.UnicodeUTF8)
			warningBox.setInformativeText(message)
			warningBox.setDetailedText(logMsg)
			warningBox.setIcon(QMessageBox.Warning)
			warningBox.exec()        
	
	# adopted from 'points2one Plugin'
	# Copyright (C) 2010 Pavol Kapusta
	# Copyright (C) 2010, 2013 Goyo
	def addShapeToCanvas(self):
		message = str(QtGui.QApplication.translate("SDialog","Created output shapefile:", None, QtGui.QApplication.UnicodeUTF8))
		message = '\n'.join([message, str(self.getOutputFilePath())])
		message = '\n'.join([message,
			str(QtGui.QApplication.translate("SDialog","Would you like to add the new layer to your project?", None, QtGui.QApplication.UnicodeUTF8))])
		addToTOC = QMessageBox.question(self, "Anaximandre", message,
			QMessageBox.Yes, QMessageBox.No, QMessageBox.NoButton)
		if addToTOC == QMessageBox.Yes:
			Utilities.addShapeToCanvas(str(self.getOutputFilePath()))
			
	def hideDialog(self):        
		self.chkBoxFieldGroup.setCheckState(Qt.Unchecked)
		self.chkBoxSelected.setCheckState(Qt.Unchecked)
		self.outFileLine.clear()
		self.hide()
   
