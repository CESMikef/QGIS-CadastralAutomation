"""
Dialog class for Cadastral Automation plugin
"""

from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QGroupBox, QLabel, QDoubleSpinBox, QCheckBox,
    QDialogButtonBox, QSpacerItem, QSizePolicy
)
from qgis.PyQt.QtCore import Qt
from qgis.gui import QgsMapLayerComboBox, QgsProjectionSelectionWidget, QgsFileWidget
from qgis.core import QgsMapLayerProxyModel, QgsCoordinateReferenceSystem


class CadastralAutomationDialog(QDialog):
    """Dialog for Cadastral Automation plugin"""
    
    def __init__(self, parent=None):
        """Constructor."""
        super(CadastralAutomationDialog, self).__init__(parent)
        self.setupUi()
        
        # Connect blocks mode checkbox to enable/disable point layer
        self.checkBox_blocks_mode.toggled.connect(self.on_blocks_mode_toggled)
    
    def setupUi(self):
        """Create the UI programmatically"""
        self.setWindowTitle("Cadastral Automation")
        self.resize(500, 550)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # ===== Input Layers Group =====
        group_layers = QGroupBox("Input Layers")
        form_layers = QFormLayout()
        
        self.label_centerline = QLabel("Centre Line Layer:")
        self.mMapLayerComboBox_centerline = QgsMapLayerComboBox()
        self.mMapLayerComboBox_centerline.setFilters(QgsMapLayerProxyModel.LineLayer)
        form_layers.addRow(self.label_centerline, self.mMapLayerComboBox_centerline)
        
        self.label_points = QLabel("Point Data Layer:")
        self.mMapLayerComboBox_points = QgsMapLayerComboBox()
        self.mMapLayerComboBox_points.setFilters(QgsMapLayerProxyModel.PointLayer)
        form_layers.addRow(self.label_points, self.mMapLayerComboBox_points)
        
        group_layers.setLayout(form_layers)
        main_layout.addWidget(group_layers)
        
        # ===== Processing Parameters Group =====
        group_params = QGroupBox("Processing Parameters")
        form_params = QFormLayout()
        
        # Road Buffer
        self.label_buffer = QLabel("Road Buffer (m):")
        self.label_buffer.setToolTip("Buffer distance around road centerlines (half road width + setback)")
        self.doubleSpinBox_buffer = QDoubleSpinBox()
        self.doubleSpinBox_buffer.setSuffix(" m")
        self.doubleSpinBox_buffer.setDecimals(1)
        self.doubleSpinBox_buffer.setMinimum(0.1)
        self.doubleSpinBox_buffer.setMaximum(100.0)
        self.doubleSpinBox_buffer.setValue(10.0)
        form_params.addRow(self.label_buffer, self.doubleSpinBox_buffer)
        
        # Minimum Area
        self.label_min_area = QLabel("Minimum Area (m²):")
        self.label_min_area.setToolTip("Minimum cadastral area in square meters")
        self.doubleSpinBox_min_area = QDoubleSpinBox()
        self.doubleSpinBox_min_area.setSuffix(" m²")
        self.doubleSpinBox_min_area.setDecimals(0)
        self.doubleSpinBox_min_area.setMinimum(1.0)
        self.doubleSpinBox_min_area.setMaximum(100000.0)
        self.doubleSpinBox_min_area.setValue(250.0)
        form_params.addRow(self.label_min_area, self.doubleSpinBox_min_area)
        
        # Maximum Area
        self.label_max_area = QLabel("Maximum Area (m²):")
        self.label_max_area.setToolTip("Maximum cadastral area in square meters (0 = no limit)")
        self.doubleSpinBox_max_area = QDoubleSpinBox()
        self.doubleSpinBox_max_area.setSuffix(" m²")
        self.doubleSpinBox_max_area.setDecimals(0)
        self.doubleSpinBox_max_area.setMinimum(0.0)
        self.doubleSpinBox_max_area.setMaximum(100000.0)
        self.doubleSpinBox_max_area.setValue(2000.0)
        form_params.addRow(self.label_max_area, self.doubleSpinBox_max_area)
        
        # Target CRS
        self.label_crs = QLabel("Target CRS:")
        self.label_crs.setToolTip("Coordinate Reference System for processing (must be metric)")
        self.mQgsProjectionSelectionWidget = QgsProjectionSelectionWidget()
        self.mQgsProjectionSelectionWidget.setCrs(QgsCoordinateReferenceSystem("EPSG:32736"))
        form_params.addRow(self.label_crs, self.mQgsProjectionSelectionWidget)
        
        group_params.setLayout(form_params)
        main_layout.addWidget(group_params)
        
        # ===== Processing Mode Group =====
        group_mode = QGroupBox("Processing Mode")
        layout_mode = QVBoxLayout()
        
        self.checkBox_blocks_mode = QCheckBox("Blocks Mode (outer boundaries only, no inner cadastrals)")
        self.checkBox_blocks_mode.setToolTip("When enabled, creates only the outer block boundaries without subdividing into individual cadastrals")
        layout_mode.addWidget(self.checkBox_blocks_mode)
        
        self.label_blocks_info = QLabel(
            "<i>Blocks mode creates outer boundaries by buffering roads without using point data for subdivision.</i>"
        )
        self.label_blocks_info.setWordWrap(True)
        layout_mode.addWidget(self.label_blocks_info)
        
        group_mode.setLayout(layout_mode)
        main_layout.addWidget(group_mode)
        
        # ===== Output Group =====
        group_output = QGroupBox("Output")
        form_output = QFormLayout()
        
        self.label_output = QLabel("Output File:")
        self.mQgsFileWidget_output = QgsFileWidget()
        self.mQgsFileWidget_output.setStorageMode(QgsFileWidget.SaveFile)
        self.mQgsFileWidget_output.setFilter("GeoPackage (*.gpkg);;Shapefile (*.shp);;All Files (*.*)")
        form_output.addRow(self.label_output, self.mQgsFileWidget_output)
        
        group_output.setLayout(form_output)
        main_layout.addWidget(group_output)
        
        # ===== Spacer =====
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        main_layout.addItem(spacer)
        
        # ===== Button Box =====
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)
    
    def on_blocks_mode_toggled(self, checked):
        """Enable/disable point layer selection based on blocks mode"""
        # In blocks mode, we don't need point data
        self.mMapLayerComboBox_points.setEnabled(not checked)
        self.label_points.setEnabled(not checked)
