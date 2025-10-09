"""
Automated Cadastral/Erf Generation Tool for QGIS
Author: Matthew Fenn
Date: 2025-10-08
Version: 1.0

Description:
    Generates cadastral boundaries (erfs) from road centerlines and building points.
    Uses Voronoi tessellation method with proper metric CRS projection.

Usage:
    Run this script from QGIS Python Console:
    exec(open('C:/path/to/cadastral_generator.py').read())
"""

import logging
from typing import Optional, Tuple
from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsVectorFileWriter
)
from qgis import processing

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

class Config:
    """Configuration parameters for cadastral generation"""
    
    # Input layer names (must match layers in QGIS project)
    ROAD_LAYER_NAME: str = 'lines'
    BUILDING_LAYER_NAME: str = 'Msogwaba Point Data — extracted_location'
    
    # Output file path
    OUTPUT_PATH: str = 'C:/Users/mfenn/OneDrive - Corelinefibre/Documents/QGIS Projects/Vuma/cadastrals.gpkg'
    
    # Processing parameters
    ROAD_BUFFER_METERS: float = 10.0      # Road buffer distance (half road width + setback)
    MIN_AREA_SQM: float = 250.0           # Minimum cadastral area (square meters)
    MAX_AREA_SQM: float = 2000.0          # Maximum cadastral area (square meters, 0 = no limit)
    
    # Coordinate Reference System
    # EPSG:32736 = WGS 84 / UTM Zone 36S (South Africa - Mpumalanga region)
    TARGET_CRS: str = 'EPSG:32736'
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration parameters"""
        if cls.ROAD_BUFFER_METERS <= 0:
            raise ValueError("ROAD_BUFFER_METERS must be positive")
        if cls.MIN_AREA_SQM <= 0:
            raise ValueError("MIN_AREA_SQM must be positive")
        if cls.MAX_AREA_SQM < 0:
            raise ValueError("MAX_AREA_SQM must be non-negative")
        if cls.MIN_AREA_SQM >= cls.MAX_AREA_SQM and cls.MAX_AREA_SQM > 0:
            raise ValueError("MIN_AREA_SQM must be less than MAX_AREA_SQM")
        return True


# ═══════════════════════════════════════════════════════════════════════════
# CORE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def get_layers(road_name: str, building_name: str) -> Tuple[Optional[QgsVectorLayer], Optional[QgsVectorLayer]]:
    """
    Retrieve layers from QGIS project by name
    
    Args:
        road_name: Name of road centerlines layer
        building_name: Name of building points layer
        
    Returns:
        Tuple of (road_layer, building_layer) or (None, None) if not found
    """
    project = QgsProject.instance()
    
    road_layers = project.mapLayersByName(road_name)
    building_layers = project.mapLayersByName(building_name)
    
    if not road_layers:
        print(f"❌ ERROR: Road layer '{road_name}' not found!")
        print(f"Available layers: {[l.name() for l in project.mapLayers().values()]}")
        return None, None
    
    if not building_layers:
        print(f"❌ ERROR: Building layer '{building_name}' not found!")
        print(f"Available layers: {[l.name() for l in project.mapLayers().values()]}")
        return None, None
    
    return road_layers[0], building_layers[0]


def reproject_layer(layer: QgsVectorLayer, target_crs: str) -> QgsVectorLayer:
    """
    Reproject layer to target CRS
    
    Args:
        layer: QgsVectorLayer to reproject
        target_crs: Target CRS (e.g., 'EPSG:32736')
        
    Returns:
        Reprojected layer
    """
    return processing.run('native:reprojectlayer', {
        'INPUT': layer,
        'TARGET_CRS': target_crs,
        'OUTPUT': 'memory:'
    })['OUTPUT']


def buffer_roads(road_layer, buffer_distance):
    """
    Create buffered road reserve from road centerlines
    
    Args:
        road_layer: QgsVectorLayer with road centerlines
        buffer_distance (float): Buffer distance in meters
        
    Returns:
        QgsVectorLayer: Buffered road reserve
    """
    return processing.run('native:buffer', {
        'INPUT': road_layer,
        'DISTANCE': buffer_distance,
        'SEGMENTS': 8,
        'END_CAP_STYLE': 1,  # Flat
        'JOIN_STYLE': 0,     # Round
        'DISSOLVE': True,
        'OUTPUT': 'memory:'
    })['OUTPUT']


def create_voronoi_polygons(building_layer):
    """
    Create Voronoi (Thiessen) polygons from building points
    
    Args:
        building_layer: QgsVectorLayer with building points
        
    Returns:
        QgsVectorLayer: Voronoi polygons
    """
    return processing.run('qgis:voronoipolygons', {
        'INPUT': building_layer,
        'BUFFER': 30,  # 30% buffer around extent to ensure all points get polygons
        'OUTPUT': 'memory:'
    })['OUTPUT']


def create_blocks(road_layer, buffer_distance, target_crs):
    """
    Create blocks (negative space of roads)
    
    Args:
        road_layer: QgsVectorLayer with road centerlines
        buffer_distance (float): Buffer distance in meters
        target_crs (str): Target CRS
        
    Returns:
        QgsVectorLayer: Block polygons
    """
    # Reproject and buffer roads
    roads_projected = reproject_layer(road_layer, target_crs)
    road_buffer = buffer_roads(roads_projected, buffer_distance)
    
    # Get extent with padding
    extent = road_buffer.extent()
    padding = buffer_distance * 5
    extent.grow(padding)
    
    # Create extent polygon
    from qgis.core import QgsGeometry, QgsFeature, QgsCoordinateReferenceSystem
    extent_geom = QgsGeometry.fromRect(extent)
    
    extent_layer = QgsVectorLayer('Polygon?crs=' + target_crs, 'extent', 'memory')
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
    
    # Multipart to singleparts
    blocks = processing.run('native:multiparttosingleparts', {
        'INPUT': blocks,
        'OUTPUT': 'memory:'
    })['OUTPUT']
    
    return blocks


def intersect_with_blocks(cadastral_layer, blocks_layer):
    """
    Intersect cadastral polygons with block boundaries to prevent cross-block polygons
    
    Args:
        cadastral_layer: QgsVectorLayer with cadastral polygons
        blocks_layer: QgsVectorLayer with block polygons
        
    Returns:
        QgsVectorLayer: Cadastrals intersected with blocks
    """
    return processing.run('native:intersection', {
        'INPUT': cadastral_layer,
        'OVERLAY': blocks_layer,
        'INPUT_FIELDS': [],
        'OVERLAY_FIELDS': [],
        'OUTPUT': 'memory:'
    })['OUTPUT']


def subtract_roads(cadastral_layer, road_buffer_layer):
    """
    Subtract road reserves from cadastral polygons
    
    Args:
        cadastral_layer: QgsVectorLayer with cadastral polygons
        road_buffer_layer: QgsVectorLayer with road buffers
        
    Returns:
        QgsVectorLayer: Cadastrals with roads subtracted
    """
    return processing.run('native:difference', {
        'INPUT': cadastral_layer,
        'OVERLAY': road_buffer_layer,
        'OUTPUT': 'memory:'
    })['OUTPUT']


def filter_by_area(layer, min_area, max_area):
    """
    Filter features by area constraints
    
    Args:
        layer: QgsVectorLayer to filter
        min_area (float): Minimum area in square meters
        max_area (float): Maximum area in square meters (0 = no limit)
        
    Returns:
        QgsVectorLayer: Filtered layer
    """
    if max_area > 0:
        expression = f'$area >= {min_area} AND $area <= {max_area}'
    else:
        expression = f'$area >= {min_area}'
    
    return processing.run('native:extractbyexpression', {
        'INPUT': layer,
        'EXPRESSION': expression,
        'OUTPUT': 'memory:'
    })['OUTPUT']


def save_layer(layer, output_path, layer_name='Cadastrals'):
    """
    Save layer to file and add to QGIS project
    
    Args:
        layer: QgsVectorLayer to save
        output_path (str): Output file path
        layer_name (str): Name for layer in QGIS
        
    Returns:
        QgsVectorLayer: Saved layer or None if error
    """
    error = QgsVectorFileWriter.writeAsVectorFormat(
        layer,
        output_path,
        "UTF-8",
        layer.crs(),
        "GPKG"
    )
    
    if error[0] != QgsVectorFileWriter.NoError:
        print(f"⚠ Warning: Could not save to file ({error})")
        print(f"→ Adding as temporary layer instead")
        QgsProject.instance().addMapLayer(layer)
        return layer
    
    # Load saved layer and add to project
    saved_layer = QgsVectorLayer(output_path, layer_name, 'ogr')
    QgsProject.instance().addMapLayer(saved_layer)
    return saved_layer


# ═══════════════════════════════════════════════════════════════════════════
# MAIN PROCESSING FUNCTION
# ═══════════════════════════════════════════════════════════════════════════

def generate_cadastrals(config: Optional[Config] = None) -> Optional[QgsVectorLayer]:
    """
    Main function to generate cadastral boundaries
    
    Args:
        config: Configuration object (uses Config class if None)
        
    Returns:
        Generated cadastral layer or None if error
    """
    import time
    
    if config is None:
        config = Config()
    
    # Validate configuration
    try:
        config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return None
    
    start_time = time.time()
    logger.info("=" * 70)
    logger.info("CADASTRAL GENERATION TOOL")
    logger.info("=" * 70)
    
    # Step 1: Get input layers
    print("\n[1/6] Loading input layers...")
    road_layer, building_layer = get_layers(
        config.ROAD_LAYER_NAME,
        config.BUILDING_LAYER_NAME
    )
    
    if not road_layer or not building_layer:
        return None
    
    print(f"  ✓ Roads: {road_layer.featureCount()} features")
    print(f"  ✓ Buildings: {building_layer.featureCount()} features")
    print(f"  ✓ Original CRS: {road_layer.crs().authid()}")
    
    # Step 2: Reproject to metric CRS
    print(f"\n[2/6] Reprojecting to {config.TARGET_CRS}...")
    roads_projected = reproject_layer(road_layer, config.TARGET_CRS)
    buildings_projected = reproject_layer(building_layer, config.TARGET_CRS)
    print(f"  ✓ Reprojected to metric CRS")
    
    # Step 3: Buffer roads
    print(f"\n[3/8] Buffering roads by {config.ROAD_BUFFER_METERS}m...")
    road_buffer = buffer_roads(roads_projected, config.ROAD_BUFFER_METERS)
    print(f"  ✓ Road buffer created")
    
    # Step 4: Create Voronoi polygons
    print(f"\n[4/8] Creating Voronoi polygons from buildings...")
    voronoi = create_voronoi_polygons(buildings_projected)
    print(f"  ✓ Voronoi polygons: {voronoi.featureCount()} features")
    
    # Check if all points got polygons
    point_count = building_layer.featureCount()
    voronoi_count = voronoi.featureCount()
    if voronoi_count < point_count:
        print(f"  ⚠ Warning: {point_count - voronoi_count} points did not get Voronoi polygons")
        print(f"    This may indicate points at dataset edges or isolated points")
    
    # Step 5: Subtract roads from Voronoi
    print(f"\n[5/8] Subtracting road reserves...")
    cadastrals = subtract_roads(voronoi, road_buffer)
    print(f"  ✓ After subtraction: {cadastrals.featureCount()} features")
    
    # Step 6: Create blocks (negative space of roads)
    print(f"\n[6/8] Creating blocks from road network...")
    blocks = create_blocks(road_layer, config.ROAD_BUFFER_METERS, config.TARGET_CRS)
    print(f"  ✓ Blocks created: {blocks.featureCount()} features")
    
    # Step 7: Intersect with blocks to ensure cadastrals stay within their block
    print(f"\n[7/8] Intersecting cadastrals with blocks (prevents cross-block polygons)...")
    cadastrals_blocked = intersect_with_blocks(cadastrals, blocks)
    print(f"  ✓ After intersection with blocks: {cadastrals_blocked.featureCount()} features")
    
    # Check area distribution
    areas = [f.geometry().area() for f in cadastrals.getFeatures() 
             if f.geometry() and not f.geometry().isEmpty()]
    
    if areas:
        print(f"  ✓ Area range: {min(areas):.1f} - {max(areas):.1f} m²")
        in_range = sum(1 for a in areas if config.MIN_AREA_SQM <= a <= (config.MAX_AREA_SQM or float('inf')))
        print(f"  ✓ Features in target range: {in_range}")
    
    # Step 8: Filter by area and save
    print(f"\n[8/8] Filtering by area ({config.MIN_AREA_SQM}-{config.MAX_AREA_SQM} m²) and saving...")
    cadastrals_filtered = filter_by_area(
        cadastrals_blocked,
        config.MIN_AREA_SQM,
        config.MAX_AREA_SQM
    )
    
    result_layer = save_layer(
        cadastrals_filtered,
        config.OUTPUT_PATH,
        'Cadastrals'
    )
    
    # Summary
    print("\n" + "=" * 70)
    print("✓ SUCCESS!")
    print("=" * 70)
    print(f"  Input buildings: {building_layer.featureCount()}")
    print(f"  Cadastrals generated: {result_layer.featureCount()}")
    print(f"  Saved to: {config.OUTPUT_PATH}")
    print("=" * 70)
    
    return result_layer


# ═══════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    # Run with default configuration
    result = generate_cadastrals()
    
    if result:
        print("\n✓ Cadastral layer added to project!")
        print("  Check your Layers panel for the new 'Cadastrals' layer")
    else:
        print("\n❌ Cadastral generation failed. Check error messages above.")
