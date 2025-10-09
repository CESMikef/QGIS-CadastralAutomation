"""
Cadastral Automation Plugin - Main Class
Author: Matthew Fenn
"""

import os
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMessageBox, QProgressDialog
from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsVectorFileWriter,
    QgsCoordinateReferenceSystem,
    QgsMessageLog,
    Qgis
)
from qgis import processing

from .cadastral_automation_dialog import CadastralAutomationDialog


class CadastralAutomation:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        Args:
            iface: An interface instance that will be passed to this class
                which provides the hook by which you can manipulate the QGIS
                application at run time.
        """
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        
        # Declare instance attributes
        self.actions = []
        self.menu = '&Cadastral Automation'
        self.toolbar = self.iface.addToolBar('Cadastral Automation')
        self.toolbar.setObjectName('Cadastral Automation')
        
        self.dlg = None

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
        """Add a toolbar icon to the toolbar."""

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

        icon_path = os.path.join(self.plugin_dir, 'icon.png')
        if not os.path.exists(icon_path):
            icon_path = ''
            
        self.add_action(
            icon_path,
            text='Cadastral Automation',
            callback=self.run,
            parent=self.iface.mainWindow())

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                '&Cadastral Automation',
                action)
            self.iface.removeToolBarIcon(action)
        del self.toolbar

    def log_message(self, message, level=Qgis.Info):
        """Log message to QGIS message log"""
        QgsMessageLog.logMessage(message, 'Cadastral Automation', level)

    def reproject_layer(self, layer, target_crs):
        """Reproject layer to target CRS"""
        return processing.run('native:reprojectlayer', {
            'INPUT': layer,
            'TARGET_CRS': target_crs,
            'OUTPUT': 'memory:'
        })['OUTPUT']

    def buffer_roads(self, road_layer, buffer_distance):
        """Create buffered road reserve from road centerlines"""
        return processing.run('native:buffer', {
            'INPUT': road_layer,
            'DISTANCE': buffer_distance,
            'SEGMENTS': 8,
            'END_CAP_STYLE': 1,  # Flat
            'JOIN_STYLE': 0,     # Round
            'DISSOLVE': True,
            'OUTPUT': 'memory:'
        })['OUTPUT']

    def create_voronoi_polygons(self, building_layer):
        """Create Voronoi (Thiessen) polygons from building points"""
        return processing.run('qgis:voronoipolygons', {
            'INPUT': building_layer,
            'BUFFER': 30,  # 30% buffer around extent to ensure all points get polygons
            'OUTPUT': 'memory:'
        })['OUTPUT']

    def intersect_with_blocks(self, cadastral_layer, blocks_layer):
        """Intersect cadastral polygons with block boundaries to prevent cross-block polygons"""
        return processing.run('native:intersection', {
            'INPUT': cadastral_layer,
            'OVERLAY': blocks_layer,
            'INPUT_FIELDS': [],
            'OVERLAY_FIELDS': [],
            'OUTPUT': 'memory:'
        })['OUTPUT']

    def subtract_roads(self, cadastral_layer, road_buffer_layer):
        """Subtract road reserves from cadastral polygons"""
        return processing.run('native:difference', {
            'INPUT': cadastral_layer,
            'OVERLAY': road_buffer_layer,
            'OUTPUT': 'memory:'
        })['OUTPUT']

    def filter_by_area(self, layer, min_area, max_area):
        """Filter features by area constraints"""
        if max_area > 0:
            expression = f'$area >= {min_area} AND $area <= {max_area}'
        else:
            expression = f'$area >= {min_area}'
        
        return processing.run('native:extractbyexpression', {
            'INPUT': layer,
            'EXPRESSION': expression,
            'OUTPUT': 'memory:'
        })['OUTPUT']

    def create_blocks(self, road_layer, buffer_distance, target_crs):
        """
        Create blocks (outer boundaries only) by buffering roads and 
        extracting the negative space.
        
        Args:
            road_layer: Road centerlines layer
            buffer_distance: Buffer distance in meters
            target_crs: Target CRS for processing
            
        Returns:
            QgsVectorLayer: Block polygons
        """
        self.log_message("Creating blocks from road network...")
        
        # Reproject roads
        roads_projected = self.reproject_layer(road_layer, target_crs)
        
        # Buffer roads
        road_buffer = self.buffer_roads(roads_projected, buffer_distance)
        
        # Get extent of road buffer
        extent = road_buffer.extent()
        
        # Create a bounding polygon from extent with some padding
        padding = buffer_distance * 5
        extent.grow(padding)
        
        # Create extent polygon
        from qgis.core import QgsGeometry, QgsFeature, QgsFields
        extent_geom = QgsGeometry.fromRect(extent)
        
        extent_layer = QgsVectorLayer('Polygon?crs=' + target_crs.authid(), 'extent', 'memory')
        extent_provider = extent_layer.dataProvider()
        extent_feature = QgsFeature()
        extent_feature.setGeometry(extent_geom)
        extent_provider.addFeatures([extent_feature])
        extent_layer.updateExtents()
        
        # Subtract road buffer from extent to get blocks
        blocks = processing.run('native:difference', {
            'INPUT': extent_layer,
            'OVERLAY': road_buffer,
            'OUTPUT': 'memory:'
        })['OUTPUT']
        
        # Multipart to singleparts to separate individual blocks
        blocks = processing.run('native:multiparttosingleparts', {
            'INPUT': blocks,
            'OUTPUT': 'memory:'
        })['OUTPUT']
        
        return blocks

    def generate_cadastrals(self, centerline_layer, point_layer, buffer_distance, 
                          min_area, max_area, target_crs, blocks_mode=False, progress_callback=None):
        """
        Main processing function to generate cadastrals or blocks
        
        Args:
            centerline_layer: Road centerlines layer
            point_layer: Building points layer (can be None in blocks mode)
            buffer_distance: Road buffer distance in meters
            min_area: Minimum area in square meters
            max_area: Maximum area in square meters (0 = no limit)
            target_crs: Target CRS for processing
            blocks_mode: If True, create only outer boundaries (blocks)
            progress_callback: Optional callback function(step, message) for progress updates
            
        Returns:
            QgsVectorLayer: Generated cadastrals or blocks
        """
        def update_progress(step, message):
            """Helper to update progress"""
            self.log_message(message)
            if progress_callback:
                progress_callback(step, message)
        
        try:
            if blocks_mode:
                # Blocks mode - create outer boundaries only
                total_steps = 4
                update_progress(1, "Running in BLOCKS MODE - creating outer boundaries only")
                
                update_progress(2, "Buffering roads and creating blocks...")
                result = self.create_blocks(centerline_layer, buffer_distance, target_crs)
                
                # Filter by area
                if min_area > 0 or max_area > 0:
                    update_progress(3, f"Filtering by area ({min_area}-{max_area} m²)...")
                    result = self.filter_by_area(result, min_area, max_area)
                
                update_progress(4, f"Blocks created: {result.featureCount()} features")
                
            else:
                # Normal mode - create individual cadastrals
                total_steps = 9
                update_progress(1, "Running in CADASTRAL MODE - creating individual cadastrals")
                
                if not point_layer:
                    raise ValueError("Point layer is required for cadastral mode")
                
                # Reproject layers
                update_progress(2, "Reprojecting layers to target CRS...")
                roads_projected = self.reproject_layer(centerline_layer, target_crs)
                buildings_projected = self.reproject_layer(point_layer, target_crs)
                
                # Buffer roads to create blocks
                update_progress(3, f"Buffering roads by {buffer_distance}m...")
                road_buffer = self.buffer_roads(roads_projected, buffer_distance)
                
                # Create Voronoi polygons
                update_progress(4, "Creating Voronoi polygons from points...")
                voronoi = self.create_voronoi_polygons(buildings_projected)
                
                # Check if all points got polygons
                point_count = buildings_projected.featureCount()
                voronoi_count = voronoi.featureCount()
                self.log_message(f"Points: {point_count}, Voronoi polygons: {voronoi_count}")
                
                if voronoi_count < point_count:
                    self.log_message(
                        f"Warning: {point_count - voronoi_count} points did not get Voronoi polygons. "
                        "This may indicate points at dataset edges.",
                        Qgis.Warning
                    )
                
                # Subtract roads from Voronoi
                update_progress(5, "Subtracting road reserves from cadastrals...")
                cadastrals = self.subtract_roads(voronoi, road_buffer)
                
                # Create blocks (negative space of roads)
                update_progress(6, "Creating blocks from road network...")
                blocks = self.create_blocks(centerline_layer, buffer_distance, target_crs)
                self.log_message(f"Blocks created: {blocks.featureCount()} features")
                
                # Intersect with blocks to ensure cadastrals stay within their block
                update_progress(7, "Intersecting cadastrals with blocks (prevents cross-block polygons)...")
                cadastrals_blocked = self.intersect_with_blocks(cadastrals, blocks)
                self.log_message(f"After intersection with blocks: {cadastrals_blocked.featureCount()} features")
                
                # Filter by area
                update_progress(8, f"Filtering by area ({min_area}-{max_area} m²)...")
                result = self.filter_by_area(cadastrals_blocked, min_area, max_area)
                
                update_progress(9, f"Cadastrals created: {result.featureCount()} features")
            
            return result
            
        except Exception as e:
            self.log_message(f"Error during processing: {str(e)}", Qgis.Critical)
            raise

    def save_layer(self, layer, output_path, layer_name='Cadastrals'):
        """Save layer to file and add to QGIS project"""
        error = QgsVectorFileWriter.writeAsVectorFormat(
            layer,
            output_path,
            "UTF-8",
            layer.crs(),
            "GPKG"
        )
        
        if error[0] != QgsVectorFileWriter.NoError:
            self.log_message(f"Warning: Could not save to file ({error})", Qgis.Warning)
            self.log_message("Adding as temporary layer instead", Qgis.Warning)
            QgsProject.instance().addMapLayer(layer)
            return layer
        
        # Load saved layer and add to project
        saved_layer = QgsVectorLayer(output_path, layer_name, 'ogr')
        QgsProject.instance().addMapLayer(saved_layer)
        return saved_layer

    def run(self):
        """Run method that performs all the real work"""
        
        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.dlg is None:
            self.dlg = CadastralAutomationDialog()
        
        # Show the dialog
        self.dlg.show()
        result = self.dlg.exec_()
        
        # See if OK was pressed
        if result:
            # Get parameters from dialog
            centerline_layer = self.dlg.mMapLayerComboBox_centerline.currentLayer()
            point_layer = self.dlg.mMapLayerComboBox_points.currentLayer()
            buffer_distance = self.dlg.doubleSpinBox_buffer.value()
            min_area = self.dlg.doubleSpinBox_min_area.value()
            max_area = self.dlg.doubleSpinBox_max_area.value()
            target_crs_str = self.dlg.mQgsProjectionSelectionWidget.crs().authid()
            target_crs = QgsCoordinateReferenceSystem(target_crs_str)
            output_path = self.dlg.mQgsFileWidget_output.filePath()
            blocks_mode = self.dlg.checkBox_blocks_mode.isChecked()
            
            # Validate inputs
            if not centerline_layer:
                QMessageBox.warning(
                    self.dlg,
                    "Missing Input",
                    "Please select a centre line layer."
                )
                return
            
            if not blocks_mode and not point_layer:
                QMessageBox.warning(
                    self.dlg,
                    "Missing Input",
                    "Please select a point data layer or enable Blocks Mode."
                )
                return
            
            if not output_path:
                QMessageBox.warning(
                    self.dlg,
                    "Missing Output",
                    "Please specify an output file path."
                )
                return
            
            if not target_crs.isValid():
                QMessageBox.warning(
                    self.dlg,
                    "Invalid CRS",
                    "Please select a valid coordinate reference system."
                )
                return
            
            # Validate parameters
            if buffer_distance <= 0:
                QMessageBox.warning(
                    self.dlg,
                    "Invalid Parameter",
                    "Road buffer distance must be positive."
                )
                return
            
            if min_area <= 0:
                QMessageBox.warning(
                    self.dlg,
                    "Invalid Parameter",
                    "Minimum area must be positive."
                )
                return
            
            if max_area > 0 and min_area >= max_area:
                QMessageBox.warning(
                    self.dlg,
                    "Invalid Parameter",
                    "Minimum area must be less than maximum area."
                )
                return
            
            # Run processing with progress dialog
            try:
                self.log_message("=" * 70)
                self.log_message("CADASTRAL AUTOMATION - PROCESSING STARTED")
                self.log_message("=" * 70)
                
                # Create progress dialog
                total_steps = 4 if blocks_mode else 9
                progress = QProgressDialog(
                    "Initializing...", 
                    "Cancel", 
                    0, 
                    total_steps + 2,  # +2 for save and finalize
                    self.iface.mainWindow()
                )
                progress.setWindowTitle("Cadastral Automation")
                progress.setMinimumDuration(0)
                progress.setValue(0)
                progress.show()
                
                # Progress callback function
                def update_progress(step, message):
                    if progress.wasCanceled():
                        raise Exception("Processing cancelled by user")
                    progress.setValue(step)
                    progress.setLabelText(message)
                    QCoreApplication.processEvents()  # Keep UI responsive
                
                # Generate cadastrals/blocks
                result_layer = self.generate_cadastrals(
                    centerline_layer,
                    point_layer,
                    buffer_distance,
                    min_area,
                    max_area,
                    target_crs,
                    blocks_mode,
                    progress_callback=update_progress
                )
                
                # Save result
                layer_name = 'Blocks' if blocks_mode else 'Cadastrals'
                progress.setValue(total_steps + 1)
                progress.setLabelText(f"Saving to {output_path}...")
                QCoreApplication.processEvents()
                
                self.log_message(f"Saving to {output_path}...")
                saved_layer = self.save_layer(result_layer, output_path, layer_name)
                
                # Finalize
                progress.setValue(total_steps + 2)
                progress.setLabelText("Finalizing...")
                QCoreApplication.processEvents()
                
                self.log_message("=" * 70)
                self.log_message("PROCESSING COMPLETED SUCCESSFULLY")
                self.log_message("=" * 70)
                
                # Close progress dialog
                progress.close()
                
                # Show success message
                self.iface.messageBar().pushMessage(
                    "Success",
                    f"{layer_name} generated: {saved_layer.featureCount()} features created",
                    level=Qgis.Success,
                    duration=5
                )
                
                QMessageBox.information(
                    self.iface.mainWindow(),
                    "Success",
                    f"{layer_name} generated successfully!\n\n"
                    f"Features created: {saved_layer.featureCount()}\n"
                    f"Saved to: {output_path}"
                )
                
                # Zoom to layer
                self.iface.mapCanvas().setExtent(saved_layer.extent())
                self.iface.mapCanvas().refresh()
                
            except Exception as e:
                # Close progress dialog if it exists
                if 'progress' in locals():
                    progress.close()
                
                self.log_message(f"Processing failed: {str(e)}", Qgis.Critical)
                QMessageBox.critical(
                    self.iface.mainWindow(),
                    "Processing Error",
                    f"An error occurred during processing:\n\n{str(e)}"
                )
