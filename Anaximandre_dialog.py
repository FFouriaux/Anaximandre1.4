# -*- coding: utf-8 -*-
"""
/***************************************************************************
 AnaximandreDialog
								 A QGIS plugin
 A plugin for auto drawing 3D Shapefiles from topographical survey.  
							 -------------------
		begin                : 2017-06-16
		new version          : 2026-08-17
		git sha              : $Format:%H$
		copyright            : (C) 2026 by F.Fouriaux
		email                : francois.fouriaux@cnrs.fr
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os


from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt import uic
from qgis.PyQt.QtGui import *

from .AnaximandreDialog import*


FORM_CLASS, _ = uic.loadUiType(os.path.join(
	os.path.dirname(__file__), 'Anaximandre_dialog_base.ui'))


class AnaximandreDialog(AnaxDialg, FORM_CLASS):			
	def __init__(self):
		AnaxDialg.__init__(self)
		# Set up the user interface from Designer.
		# After setupUI you can access any designer object by doing
		# self.<objectname>, and you can use autoconnect slots - see
		# http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
		# #widgets-and-dialogs-with-auto-connect
		
		self.setupUi(self)
		self.layerList()
		self.listeCodes()
		self.pushButton.clicked.connect(self.selectDirectory)
		self.pushButton_2.clicked.connect(self.OpenCsv)
		self.cbox_FichierCsv.currentIndexChanged.connect(self.updateFieldCombos)
		#QObject.connect(self.pushButton, SIGNAL('clicked()'),self.selectDirectory)
		#QObject.connect(self.pushButton_2, SIGNAL('clicked()'),self.OpenCsv)
		#QObject.connect(self.cbox_FichierCsv, SIGNAL('currentIndexChanged(QString)'), self.updateFieldCombos)
		localLang = QSettings().value('locale/userLocale')[0:2]
		if localLang != 'fr':
			self.label_FichierCsv.setText('Csv File')
			self.label.setText('Output')
			self.label_1.setText('First line of the file')
			self.label_2.setText('Expected format')
