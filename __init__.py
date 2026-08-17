# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Anaximandre
                                 A QGIS plugin
 A plugin for auto drawing 3D Shapefiles from topographical survey.  
                             -------------------
        begin                : 2017-06-16
        new version          : 2026-08-17
        copyright            : (C) 2026 by F.Fouriaux
        email                : francois.fouriaux@cnrs.fr
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load Anaximandre class from file Anaximandre.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .Anaximandre import Anaximandre
    return Anaximandre(iface)
