# -*- coding: utf-8 -*-
"""
/***************************************************************************
 urban_type_editor
                                 A QGIS plugin
 This plugin edit and create urban types in the SUEWS database
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2021-05-31
        git sha              : $Format:%H$
        copyright            : (C) 2021 by Oskar Bäcklin University of Gothenburg
        email                : oskar.backlin@gu.se
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
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QFileDialog, QAction, QMessageBox
from qgis.gui import QgsMapLayerComboBox, QgsFieldComboBox, QgsMessageBar
from qgis.core import  QgsMapLayerProxyModel, Qgis, QgsProject, QgsFieldProxyModel, QgsField
# Initialize Qt resources from file resources.py
from .resources import *
from pathlib import Path
import geopandas as gpd
import webbrowser
import pandas as pd

# Import the code for the dialog
from .urban_type_edior_dialog import urban_type_editorDialog
import os.path


class urban_type_editor(object):
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
            'urban_type_editor_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Urban Type Editor')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
    
        self.first_start = None
    
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
        return QCoreApplication.translate('urban_type_editor', message)


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

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/urban_type_edior/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u''),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True

           # Read Database
#

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Urban Type Editor'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = urban_type_editorDialog()

        # Clear 
        self.dlg.comboBoxType.clear()
        # line edits
        self.dlg.TypeLineEditName.clearValue()
        self.dlg.TypeLineEditLocation.clearValue()
        self.dlg.TypeLineEditDesc.clearValue()
        # Building
        self.dlg.comboBoxWallMtr.clear()
        self.dlg.comboBoxWallClr.clear()  
        self.dlg.textBrowserWallFrom.clear()
  
        self.dlg.comboBoxRoofMtr.clear()
        self.dlg.comboBoxRoofClr.clear()
        self.dlg.textBrowserRoofFrom.clear()

        # Paved
        self.dlg.comboBoxPavedMtr.clear()
        self.dlg.comboBoxPavedClr.clear()
        self.dlg.textBrowserPavedFrom.clear()

        # Vegetation
        self.dlg.comboBoxEvrType.clear()
        self.dlg.textBrowserEvrFrom.clear()
        self.dlg.comboBoxDecType.clear()
        self.dlg.textBrowserDecFrom.clear()
        self.dlg.comboBoxGrassType.clear()
        self.dlg.textBrowserGrassFrom.clear()

        self.dlg.comboBoxBsoilType.clear()
        self.dlg.textBrowserBsoilFrom.clear()
        self.dlg.comboBoxBsoilClr.clear()

        db_path = r'C:\Script\NGEO306\database_copy.xlsx'
        idx_col = 'ID'
        idx=-1

        Type = pd.read_excel(db_path, sheet_name= 'Lod1_Types', index_col=  idx_col)
        ref = pd.read_excel(db_path, sheet_name= 'References', index_col= idx_col)
        alb =  pd.read_excel(db_path, sheet_name= 'Lod3_Albedo', index_col= idx_col)
        em =  pd.read_excel(db_path, sheet_name= 'Lod3_Emissivity', index_col= idx_col)
        OHM =  pd.read_excel(db_path, sheet_name= 'Lod3_OHM', index_col= idx_col) # Away from Veg
        LAI =  pd.read_excel(db_path, sheet_name= 'Lod3_LAI', index_col= idx_col)
        st = pd.read_excel(db_path, sheet_name= 'Lod3_Storage', index_col = idx_col)
        cnd = pd.read_excel(db_path, sheet_name= 'Lod3_Conductance', index_col = idx_col) # Away from Veg
        veg = pd.read_excel(db_path, sheet_name= 'Lod2_Veg', index_col = idx_col)
        nonveg = pd.read_excel(db_path, sheet_name= 'Lod2_NonVeg', index_col = idx_col)
        LGP = pd.read_excel(db_path, sheet_name= 'Lod3_LGP', index_col= idx_col)
        dr = pd.read_excel(db_path, sheet_name= 'Lod3_Drainage', index_col= idx_col)

        # Add available types to combobox
        type_list = []
        for i in range(len(Type)):
            type_list.append(str(Type['Type'].iloc[i]) + ', ' + str(Type['Location'].iloc[i]))
        Type['type_location'] = type_list

        self.dlg.comboBoxType.addItems(sorted(type_list)) 
        self.dlg.comboBoxType.setCurrentIndex(-1)

        self.dlg.compButton.clicked.connect(self.check_type)
        self.dlg.genButton.clicked.connect(self.generate_type)

        # Update rest of ComboBoxes
        def type_changed(): 
            try:          
                urb_type = self.dlg.comboBoxType.currentText()
                TypeID =Type[Type['type_location'] == urb_type].index.item()
        
                for i in [self.dlg.comboBoxEvrType, self.dlg.comboBoxDecType, self.dlg.comboBoxGrassType,self.dlg.comboBoxWallMtr,
                self.dlg.comboBoxRoofMtr,self.dlg.comboBoxWallClr,self.dlg.comboBoxRoofClr]:
                    i.clear()
        
                def change_veg(cbox, surface, var, idx):
                    cbox.clear()
                    item_list = veg[var][veg['Surface'] == surface].tolist()
                    [*set(item_list)]
                    cbox.addItems([*set(item_list)])
                    try:
                        indexer = veg.loc[Type.loc[TypeID, surface],var]
                        cbox.setCurrentIndex(item_list.index(indexer))
                    except:
                        pass

                def change_nonveg(cbox, surface, var, idx):
                    cbox.clear()
                    item_list = nonveg[var][nonveg['Surface'] == surface].tolist()  
                    cbox.addItems([*set(item_list)])
                    try:
                        indexer = nonveg.loc[Type.loc[TypeID, surface],var]
                        cbox.setCurrentIndex(item_list.index(indexer))
                    except:
                        pass

                change_veg(self.dlg.comboBoxEvrType,'Evergreen Tree', 'Type' , TypeID)
                change_veg(self.dlg.comboBoxDecType,'Decidous Tree', 'Type' , TypeID)
                change_veg(self.dlg.comboBoxGrassType,'Grass', 'Type' , TypeID)
                change_nonveg(self.dlg.comboBoxWallMtr, 'Building', 'Type', TypeID)
                change_nonveg(self.dlg.comboBoxRoofMtr, 'Building', 'Type', TypeID)
                change_nonveg(self.dlg.comboBoxPavedMtr, 'Paved', 'Type', TypeID)
                change_nonveg(self.dlg.comboBoxBsoilType, 'Bare Soil', 'Type', TypeID)
            
            except:
                pass
           
        self.dlg.comboBoxType.currentIndexChanged.connect(type_changed)

        def mtr_change():
                self.dlg.comboBoxWallClr.clear()
                self.dlg.comboBoxRoofClr.clear()
                self.dlg.comboBoxPavedClr.clear()
                self.dlg.comboBoxBsoilClr.clear()

                wall_clr_list = nonveg['Color'][(nonveg['Surface'] == 'Building') & (nonveg['Type'] == self.dlg.comboBoxWallMtr.currentText())].to_list()
                roof_clr_list = nonveg['Color'][(nonveg['Surface'] == 'Building') & (nonveg['Type'] == self.dlg.comboBoxRoofMtr.currentText())].to_list()
                paved_clr_list = nonveg['Color'][(nonveg['Surface'] == 'Paved') & (nonveg['Type'] == self.dlg.comboBoxPavedMtr.currentText())].to_list()
                bsoil_clr_list = nonveg['Color'][(nonveg['Surface'] == 'Bare Soil') & (nonveg['Type'] == self.dlg.comboBoxBsoilType.currentText())].to_list()

                self.dlg.comboBoxWallClr.addItems([*(wall_clr_list)])
                self.dlg.comboBoxRoofClr.addItems([*(roof_clr_list)])
                self.dlg.comboBoxPavedClr.addItems([*(paved_clr_list)])
                self.dlg.comboBoxBsoilClr.addItems([*(bsoil_clr_list)])
        
        self.dlg.comboBoxWallMtr.currentIndexChanged.connect(mtr_change)
        self.dlg.comboBoxRoofMtr.currentIndexChanged.connect(mtr_change)
        self.dlg.comboBoxPavedMtr.currentIndexChanged.connect(mtr_change)
        self.dlg.comboBoxBsoilType.currentIndexChanged.connect(mtr_change)


        def clr_change():
            try:
                self.dlg.textBrowserWallFrom.setText(nonveg['Location'][(
                    nonveg['Surface'] == 'Building') & 
                    (nonveg['Type'] == self.dlg.comboBoxWallMtr.currentText()) & 
                    (nonveg['Color'] == self.dlg.comboBoxWallClr.currentText())].item())

                self.dlg.textBrowserRoofFrom.setText(nonveg['Location'][(
                    nonveg['Surface'] == 'Building') & 
                    (nonveg['Type'] == self.dlg.comboBoxRoofMtr.currentText()) & 
                    (nonveg['Color'] == self.dlg.comboBoxRoofClr.currentText())].item())
                    
                self.dlg.textBrowserPavedFrom.setText(nonveg['Location'][(
                    nonveg['Surface'] == 'Paved') & 
                    (nonveg['Type'] == self.dlg.comboBoxPavedMtr.currentText()) & 
                    (nonveg['Color'] == self.dlg.comboBoxPavedClr.currentText())].item())  
                
                self.dlg.textBrowserBsoilFrom.setText(nonveg['Location'][(
                    nonveg['Surface'] == 'Bare Soil') & 
                    (nonveg['Type'] == self.dlg.comboBoxBsoilType.currentText()) & 
                    (nonveg['Color'] == self.dlg.comboBoxBsoilClr.currentText())].item())
            except:
                pass
        self.dlg.comboBoxWallClr.currentIndexChanged.connect(clr_change)
        self.dlg.comboBoxRoofClr.currentIndexChanged.connect(clr_change)  
        self.dlg.comboBoxPavedClr.currentIndexChanged.connect(clr_change)  
        self.dlg.comboBoxBsoilClr.currentIndexChanged.connect(clr_change)  

        def var_change():
            urb_type = self.dlg.comboBoxType.currentText()

            def change_veg(cbox, col, var, idx):
                cbox.clear()
                item_list = veg[var][veg['Type'] == col].tolist()
                [*set(item_list)]
                cbox.addItems([*set(item_list)])
                if len(veg.loc[TypeID[col], var]) > 0:
                    indexer = veg.loc[TypeID[col], var].item()
                    cbox.setCurrentIndex(item_list.index(indexer))

            # TypeID = Type.loc[(Type['Region'] == reg) & (Type['Type'] == urb_type)]

            # self.dlg.textBrowser.setText(
            #     '<b>New Type: ' + '</b> ' +  self.dlg.newTypeLineEdit.value() + '<br><b>' +
            #     '\nNew Region: ' + '</b> ' +  self.dlg.comboBoxRegionOut.currentText() + '<br><b>' +
            #     '\n\nDescritpion ' + '</b> ' +  self.dlg.descLineEdit.value() + '<br><b>')
            #     # '\n\nMin Albedo Evergreen: ' +  '</b>' +str(alb.loc[veg.loc[veg[veg['Type'] == self.dlg.comboBoxEvrType.currentText()].index.item(), 'Alb'], 'Alb_min']) +'<br><b>' +
            #     # '\n\nMax Albedo Evergreen: ' +  '</b>' + str(alb.loc[veg.loc[veg[veg['Type'] == self.dlg.comboBoxEvrType.currentText()].index.item(), 'Alb'], 'Alb_max']) +'<br><b>' +
            #     # '\n\nMin Albedo Decidous: ' +  '</b>' + str(alb.loc[veg.loc[veg[veg['Type'] == self.dlg.comboBoxDecType.currentText()].index.item(), 'Alb'], 'Alb_min'])+'<br><b>' )
            #     # # '\n\nMax Albedo Decidous: ' +  '</b>' + str(alb.loc[veg.loc[veg[veg['Type'] == self.dlg.comboBoxDecType.currentText()].index.item(), 'Alb'], 'Alb_max']))
                
            # # print(veg[veg['Type'] == self.dlg.comboBoxDecType.currentText()].index.item())
            # # print(alb.loc[veg.loc[veg[veg['Type'] == self.dlg.comboBoxDecType.currentText()].index.item(), 'Alb'], 'Alb_min'])   
            # AlbID = nonveg['Alb'].loc[(nonveg['Material'] == self.dlg.comboBoxWallMtr.currentText() ) & (nonveg['Color'] == self.dlg.comboBoxWallClr.currentText())].item()
            # print(alb.loc[AlbID,'Alb_min'])
            
            #self.dlg.textBrowser.setText(veg.loc[(veg['Type'] == 'Evergreen Tree') & (veg['Type'] == self.dlg.comboBoxEvrType.currentText()),'Where'].item())

            try:
                if len(veg.loc[TypeID['Decidous Tree'], 'Surface']) > 0:  
                    self.dlg.textBrowserBuild.setText(  
                        '<b>Min Albedo: ' +  '</b>' +str(alb.loc[veg.loc[veg[veg['Type'] == self.dlg.comboBoxEvrType.currentText()].index.item(), 'Alb'], 'Alb_min']))
                    #'\nMax Albedo: ' +  '</b>' + str(alb.loc[veg.loc[veg[veg['Type'] == self.dlg.comboBoxEvrType.currentText()].index.item(), 'Alb'], 'Alb_max'])  
                    #str(alb.loc[nonveg['Alb'].loc[(nonveg['Material'] == self.dlg.comboBoxWallMtr.currentText()) & (nonveg['Color'] == self.dlg.comboBoxWallClr.currentText())].item(),'Alb_Min'])
            except:
                pass
            try:             
                #self.dlg.textBrowserWallFrom.setText(str(nonveg['Location'].loc[(nonveg['Type'] == self.dlg.comboBoxWallMtr.currentText())].item()))
                #self.dlg.textBrowserRoofFrom2.setText(str(nonveg['Location'].loc[(nonveg['Type'] == self.dlg.comboBoxRoofMtr.currentText())].item()))
                #self.dlg.textBrowserPavedFrom.setText(str(nonveg['Location'].loc[(nonveg['Type'] == self.dlg.comboBoxPavedMtr.currentText())].item()))
                self.dlg.textBrowserEvrFrom.setText(str(veg['Location'].loc[veg['Type'] == self.dlg.comboBoxEvrType.currentText()].item()))
                self.dlg.textBrowserDecFrom.setText(str(veg['Location'].loc[(veg['Type'] == self.dlg.comboBoxDecType.currentText())].item()))
                self.dlg.textBrowserGrassFrom.setText(str(veg['Location'].loc[(veg['Type'] == self.dlg.comboBoxGrassType.currentText())].item()))
            except:
                pass    
        self.dlg.comboBoxEvrType.currentIndexChanged.connect(var_change)
        self.dlg.comboBoxDecType.currentIndexChanged.connect(var_change)
        self.dlg.comboBoxGrassType.currentIndexChanged.connect(var_change)
        self.dlg.comboBoxWallMtr.currentIndexChanged.connect(var_change)

        def escape():
            print(' ')
        # Warnings and Messages when using check type
       

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            self.dlg.__init__()
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
        else:
            self.dlg.__init__()

    def check_type(self):
        db_path = r'C:\Script\NGEO306\database_copy.xlsx'
        idx_col = 'ID'

        Type = pd.read_excel(db_path, sheet_name= 'Lod1_Types', index_col=  idx_col)

        # Name
        if self.dlg.TypeLineEditName.value().startswith('test'):
            QMessageBox.warning(None, "Error in Name",'Please, don´t use test as type name..')
        elif self.dlg.TypeLineEditName.value().startswith('Test'):
            QMessageBox.warning(None, "Error in Name",'Please, don´t use test as type name..')
        elif self.dlg.TypeLineEditName.value() in Type['Type'].tolist():
            QMessageBox.warning(None, "Error in Name",'The suggested type name is already taken.')
        elif self.dlg.TypeLineEditName.isNull():
            QMessageBox.warning(None, "Error in Name",'Enter a name for new type')

        # Location
        elif self.dlg.TypeLineEditLocation.isNull():
            QMessageBox.warning(None, "Error in Location",'Enter a location for new type')

        # Soil
        elif self.dlg.lineEditBsoilDepth.isNull():
            QMessageBox.warning(None, "Errorin Soil Depth",'Enter Soil Depth')

        # Fix to only allow for decimals
        # elif len(self.dlg.lineEditBsoilDepth.value())>0:
            # try:
            #     float(self.dlg.lineEditBsoilDepth.value())
            #     QMessageBox.warning(None, "Error in Soil Depth",'Good Job')
            
            # except:
            #     QMessageBox.warning(None, "Error in Soil Depth",'Invalid characters in Soil Depth! \nOnly 0-9 and . are allowed')
            
        elif self.dlg.lineEditBsoilDepth.value().replace(',','b').count('.')>1 or self.dlg.lineEditBsoilDepth.value().count(',')>1:
            QMessageBox.warning(None, "Error in Soil Depth",'To many separators in Soil Depth')

        # Final - When all is Checked 
        else:
            QMessageBox.information(None, "Check Complete", 'Your type is compatible with the SUEWS-Database!\nPress Generate Type to add to Database')
            self.dlg.genButton.setEnabled(True)


    def generate_type(self):
        db_path = r'C:\Script\NGEO306\database_copy.xlsx'
        idx_col = 'ID'

        Type = pd.read_excel(db_path, sheet_name= 'Lod1_Types', index_col=  idx_col)
        ref = pd.read_excel(db_path, sheet_name= 'References', index_col= idx_col)
        alb =  pd.read_excel(db_path, sheet_name= 'Lod3_Albedo', index_col= idx_col)
        em =  pd.read_excel(db_path, sheet_name= 'Lod3_Emissivity', index_col= idx_col)
        OHM =  pd.read_excel(db_path, sheet_name= 'Lod3_OHM', index_col= idx_col) # Away from Veg
        LAI =  pd.read_excel(db_path, sheet_name= 'Lod3_LAI', index_col= idx_col)
        st = pd.read_excel(db_path, sheet_name= 'Lod3_Storage', index_col = idx_col)
        cnd = pd.read_excel(db_path, sheet_name= 'Lod3_Conductance', index_col = idx_col) # Away from Veg
        veg = pd.read_excel(db_path, sheet_name= 'Lod2_Veg', index_col = idx_col)
        nonveg = pd.read_excel(db_path, sheet_name= 'Lod2_NonVeg', index_col = idx_col)
        LGP = pd.read_excel(db_path, sheet_name= 'Lod3_LGP', index_col= idx_col)
        dr = pd.read_excel(db_path, sheet_name= 'Lod3_Drainage', index_col= idx_col)

        new_type_dict = {
            'ID' : len(Type)+1,
            'Location' : self.dlg.TypeLineEditLocation.value(),
            'Type' :  self.dlg.TypeLineEditName.value(),
            'Default' : 'N',
            'Description': self.dlg.TypeLineEditDesc.value(),
            'Period' : 'testyear',
            'Url' : '', 
            'Author' : 'SUEWS',
            'Grass' : veg.index[veg['Type'] == self.dlg.comboBoxGrassType.currentText()].item(),
            'Decidous Tree' : veg.index[veg['Type'] == self.dlg.comboBoxDecType.currentText()].item(),
            'Evergreen Tree' : veg.index[veg['Type'] == self.dlg.comboBoxEvrType.currentText()].item(),
            'Building' : 'NonVeg1',
            'Paved' : 'NonVeg2'
        }      
        print(new_type_dict)                  
        Type = Type.append(pd.DataFrame.from_dict([new_type_dict]).set_index('ID'))

        db_path =r'C:\Script\NGEO306\database_copy.xlsx'

        # with pd.ExcelWriter(db_path) as writer:  
        #     Type.to_excel(writer, sheet_name='Lod1_Types')
        #     ref.to_excel(writer, sheet_name='References')
        #     em.to_excel(writer, sheet_name='Lod3_Emissivity')
        #     OHM.to_excel(writer, sheet_name='Lod3_OHM')
        #     alb.to_excel(writer, sheet_name='Lod3_Albedo')
        #     LAI.to_excel(writer, sheet_name='Lod3_LAI')
        #     st.to_excel(writer, sheet_name='Lod3_Storage')
        #     cnd.to_excel(writer, sheet_name='Lod3_Conductance')
        #     veg.to_excel(writer, sheet_name='Lod2_Veg')
        #     nonveg.to_excel(writer, sheet_name='Lod2_NonVeg')
        #     LGP.to_excel(writer, sheet_name='Lod3_LGP')
        #     dr.to_excel(writer, sheet_name='Lod3_Drainage')
        #     # suews_veg.to_excel(writer, sheet_name='SUEWS_Veg')
        #     # suews_nonveg.to_excel(writer, sheet_name='SUEWS_NonVeg')

        QMessageBox.information(None, "Success", 'Type added to Database')
        self.run()


 