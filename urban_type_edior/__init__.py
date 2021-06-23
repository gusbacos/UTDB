# -*- coding: utf-8 -*-
"""
/***************************************************************************
 urban_type_editor
                                 A QGIS plugin
 This plugin edit and create urban types in the SUEWS database
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2021-05-31
        copyright            : (C) 2021 by Oskar Bäcklin University of Gothenburg
        email                : oskar.backlin@gu.se
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
    """Load urban_type_editor class from file urban_type_editor.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .urban_type_edior import urban_type_editor
    return urban_type_editor(iface)