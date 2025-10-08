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

from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsVectorFileWriter
)
from qgis import processing


# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

class Config:
    """Configuration parameters for cadastral generation"""
    
    # Input layer names (must match layers in QGIS project)
    ROAD_LAYER_NAME = 'lines'
    BUILDING_LAYER_NAME = 'Msogwaba Point Data — extracted_location'
    
    # Output file path
    OUTPUT_PATH = 'C:/Users/mfenn/OneDrive - Corelinefibre/Documents/QGIS Projects/Vuma/cadastrals.gpkg'
    
    # Processing parameters
    ROAD_BUFFER_METERS = 10.0      # Road buffer distance (half road width + setback)
    MIN_AREA_SQM = 250.0           # Minimum cadastral area (square meters)
    MAX_AREA_SQM = 2000.0          # Maximum cadastral area (square meters, 0 = no limit)
    
    # Coordinate Reference System
    # EPSG:32736 = WGS 84 / UTM Zone 36S (South Africa - Mpumalanga region)
    TARGET_CRS = 'EPSG:32736'


# ═══════════════════════════════════════════════════════════════════════════
# CORE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def get_layers(road_name, building_name):
    """
    Retrieve layers from QGIS project by name
    
    Args:
        road_name (str): Name of road centerlines layer
        building_name (str): Name of building points layer
        
    Returns:
        tuple: (road_layer, building_layer) or (None, None) if not found
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


def reproject_layer(layer, target_crs):
    """
    Reproject layer to target CRS
    
    Args:
        layer: QgsVectorLayer to reproject
        target_crs (str): Target CRS (e.g., 'EPSG:32736')
        
    Returns:
        QgsVectorLayer: Reprojected layer
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
        'BUFFER': 10,  # 10% buffer around extent
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

def generate_cadastrals(config=None):
    """
    Main function to generate cadastral boundaries
    
    Args:
        config: Configuration object (uses Config class if None)
        
    Returns:
        QgsVectorLayer: Generated cadastral layer or None if error
    """
    if config is None:
        config = Config()
    
    print("=" * 70)
    print("CADASTRAL GENERATION TOOL")
    print("=" * 70)
    
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
    print(f"\n[3/6] Buffering roads by {config.ROAD_BUFFER_METERS}m...")
    road_buffer = buffer_roads(roads_projected, config.ROAD_BUFFER_METERS)
    print(f"  ✓ Road buffer created")
    
    # Step 4: Create Voronoi polygons
    print(f"\n[4/6] Creating Voronoi polygons from buildings...")
    voronoi = create_voronoi_polygons(buildings_projected)
    print(f"  ✓ Voronoi polygons: {voronoi.featureCount()} features")
    
    # Step 5: Subtract roads from cadastrals
    print(f"\n[5/6] Subtracting road reserves...")
    cadastrals = subtract_roads(voronoi, road_buffer)
    print(f"  ✓ After subtraction: {cadastrals.featureCount()} features")
    
    # Check area distribution
    areas = [f.geometry().area() for f in cadastrals.getFeatures() 
             if f.geometry() and not f.geometry().isEmpty()]
    
    if areas:
        print(f"  ✓ Area range: {min(areas):.1f} - {max(areas):.1f} m²")
        in_range = sum(1 for a in areas if config.MIN_AREA_SQM <= a <= (config.MAX_AREA_SQM or float('inf')))
        print(f"  ✓ Features in target range: {in_range}")
    
    # Step 6: Filter by area and save
    print(f"\n[6/6] Filtering by area ({config.MIN_AREA_SQM}-{config.MAX_AREA_SQM} m²) and saving...")
    cadastrals_filtered = filter_by_area(
        cadastrals,
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
