# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Anaximandre
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

import os.path
import urllib

from qgis.core import QgsProject, QgsMapLayer, QgsWkbTypes
from qgis.PyQt.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QDialog
from qgis.PyQt.QtGui import QDesktopServices
from qgis.PyQt.QtCore import QUrl


# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .Anaximandre_dialog import AnaximandreDialog
# Import the engine for drawing
from .Auto3dShp import Auto3DShp



class Anaximandre:
	"""QGIS Plugin Implementation."""

	def __init__(self, iface):
		"""Constructor.

		:param iface: An interface instance that will be passed to this class
			which provides the hook by which you can manipulate the QGIS
			application at run time.
		:type iface: QgsInterface
		"""
		# Save reference to the QGIS interface
		self.iface = iface
		# initialize plugin directory
		self.plugin_dir = os.path.dirname(__file__)
		# initialize locale
		locale = QSettings().value('locale/userLocale')[0:2]
		locale_path = os.path.join(
			self.plugin_dir,
			'i18n',
			'Anaximandre_{}.qm'.format(locale))

		if os.path.exists(locale_path):
			self.translator = QTranslator()
			self.translator.load(locale_path)

			if qVersion() > '4.3.3':
				QCoreApplication.installTranslator(self.translator)


		# Declare instance attributes
		self.actions = []
		self.menu = self.tr(u'&Anaximandre')
		# TODO: We are going to let the user set this up in a future iteration
		self.toolbar = self.iface.addToolBar(u'Anaximandre')
		self.toolbar.setObjectName(u'Anaximandre')

	# noinspection PyMethodMayBeStatic
	def tr(self, message):
		"""Get the translation for a string using Qt translation API.

		We implement this ourselves since we do not inherit QObject.

		:param message: String for translation.
		:type message: str, QString

		:returns: Translated version of message.
		:rtype: QString
		"""
		# noinspection PyTypeChecker,PyArgumentList,PyCallByClass
		return QCoreApplication.translate('Anaximandre', message)


	def add_action(
		self,
		icon_path,
		text,
		callback,
		enabled_flag=True,
		add_to_menu=True,
		add_to_toolbar=True,
		status_tip=None,
		whats_this=None,
		parent=None):
		"""Add a toolbar icon to the toolbar.

		:param icon_path: Path to the icon for this action. Can be a resource
			path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
		:type icon_path: str

		:param text: Text that should be shown in menu items for this action.
		:type text: str

		:param callback: Function to be called when the action is triggered.
		:type callback: function

		:param enabled_flag: A flag indicating if the action should be enabled
			by default. Defaults to True.
		:type enabled_flag: bool

		:param add_to_menu: Flag indicating whether the action should also
			be added to the menu. Defaults to True.
		:type add_to_menu: bool

		:param add_to_toolbar: Flag indicating whether the action should also
			be added to the toolbar. Defaults to True.
		:type add_to_toolbar: bool

		:param status_tip: Optional text to show in a popup when mouse pointer
			hovers over the action.
		:type status_tip: str

		:param parent: Parent widget for the new action. Defaults None.
		:type parent: QWidget

		:param whats_this: Optional text to show in the status bar when the
			mouse pointer hovers over the action.

		:returns: The action that was created. Note that the action is also
			added to self.actions list.
		:rtype: QAction
		"""

		# Create the dialog (after translation) and keep reference
		self.dlg = AnaximandreDialog()

		icon = QIcon(icon_path)
		action = QAction(icon, text, parent)
		action.triggered.connect(callback)
		action.setEnabled(enabled_flag)

		if status_tip is not None:
			action.setStatusTip(status_tip)

		if whats_this is not None:
			action.setWhatsThis(whats_this)

		if add_to_toolbar:
			self.toolbar.addAction(action)

		if add_to_menu:
			self.iface.addPluginToVectorMenu(
				self.menu,
				action)

		self.actions.append(action)

		return action

	def initGui(self):
		"""Create the menu entries and toolbar icons inside the QGIS GUI."""

		icon_path = ":/plugins/Anaximandre/icon.png"
		self.add_action(
			icon_path,
			text=self.tr(u'Auto Drawing 3DShp'),
			callback=self.run,
			parent=self.iface.mainWindow())
			
		iconHelp= ':/plugins/Anaximandre/help.svg'
		self.add_action(
			iconHelp,
			text=self.tr(u'help'),
			callback=self.help,
			parent=self.iface.mainWindow())

	def help(self):
		if QCoreApplication.translate(u"Anaximandre", "help") == "aide":
			help_file = "file:///{}/help/build/html/fr/index.html".format(os.path.dirname(__file__))
		else:
			help_file = "file:///{}/help/build/html/en/index.html".format(os.path.dirname(__file__)) 
		QDesktopServices().openUrl(QUrl(help_file))
		
		
		
	def unload(self):
		"""Removes the plugin menu item and icon from QGIS GUI."""
		for action in self.actions:
			self.iface.removePluginVectorMenu(
				self.tr(u'&Anaximandre'),
				action)
			self.iface.removeToolBarIcon(action)
		# remove the toolbar
		del self.toolbar


	def run(self):
		"""Run method that performs all the real work"""
		
		 #update the available vectorial layers
		self.dlg.layerList()
		
		
		# show the dialog
		self.dlg.show()
		# Run the dialog event loop
		result = self.dlg.exec()
		# See if OK was pressed and get parameters
		if result:
			csvPath=''
			sortie=self.dlg.lineEdit.text()
			layers=[layer for layer in QgsProject.instance().mapLayers().values()]
			for layer in layers:
				if layer.name() == self.dlg.cbox_FichierCsv.currentText():
					a= layer.publicSource()
					if a[0:5] =='file:':
						b=str(a.split('?')[0])
						csvPath=urllib.parse.unquote(b)[7:]
						if os.name=='nt':
							csvPath=csvPath[1:]
					else:
						csvPath=a
						if os.name=='nt':
							csvPath=csvPath[1:]
						
			Auto3DShp(csvPath,sortie)
			pass
