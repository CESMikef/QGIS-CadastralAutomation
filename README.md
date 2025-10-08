# Automated Cadastral/Erf Generation Tool for QGIS

**Version:** 1.0  
**Author:** Matthew Fenn  
**Date:** October 2025

## Overview

This tool automatically generates cadastral boundaries (erfs/plots) from:
- **Road centerlines** (from OpenStreetMap or other sources)
- **Building demand points** (from Google, machine learning models, or surveys)

The algorithm creates realistic property boundaries by:
1. Reprojecting data to a metric coordinate system
2. Buffering roads to create road reserves
3. Generating Voronoi (Thiessen) polygons from building points
4. Subtracting road reserves from the polygons
5. Filtering by area constraints

---

## Features

✅ **Automatic CRS handling** - Reprojects to UTM for accurate metric calculations  
✅ **Voronoi tessellation** - Creates natural boundaries based on building positions  
✅ **Road buffer subtraction** - Respects road reserves and setbacks  
✅ **Area filtering** - Removes unrealistic plot sizes  
✅ **Clean, modular code** - Easy to understand and modify  
✅ **Error handling** - Graceful fallbacks and informative messages

---

## Installation

### Method 1: Direct Script Execution (Recommended)

1. **Download** `cadastral_generator.py` to your computer
2. **Open QGIS** and load your road and building layers
3. **Open Python Console**: `Plugins > Python Console` (or `Ctrl+Alt+P`)
4. **Run the script**:
   ```python
   exec(open('C:/Users/mfenn/Documents/GitHub/QGIS Plugin-ErfAutomation/cadastral_generator.py').read())
   ```

### Method 2: Add to QGIS Scripts

1. Open QGIS
2. Go to `Processing > Toolbox`
3. Click the Python icon dropdown
4. Select `Add Script to Toolbox...`
5. Browse to `cadastral_generator.py`
6. The tool will appear in the Processing Toolbox

---

## Usage

### Quick Start

1. **Prepare your data:**
   - Load road centerlines layer (line features)
   - Load building points layer (point features)

2. **Edit configuration** in `cadastral_generator.py`:
   ```python
   class Config:
       ROAD_LAYER_NAME = 'lines'              # Your road layer name
       BUILDING_LAYER_NAME = 'buildings'      # Your building layer name
       OUTPUT_PATH = 'C:/output/cadastrals.gpkg'
       
       ROAD_BUFFER_METERS = 10.0    # Road setback distance
       MIN_AREA_SQM = 250.0         # Minimum plot size
       MAX_AREA_SQM = 2000.0        # Maximum plot size
       TARGET_CRS = 'EPSG:32736'    # UTM Zone 36S (South Africa)
   ```

3. **Run the script** from Python Console:
   ```python
   exec(open('path/to/cadastral_generator.py').read())
   ```

4. **Check results** - The cadastral layer will be added to your project

---

## Configuration Parameters

### Input Layers
- **`ROAD_LAYER_NAME`**: Name of your road centerlines layer in QGIS
- **`BUILDING_LAYER_NAME`**: Name of your building points layer in QGIS

### Processing Parameters

| Parameter | Description | Typical Values |
|-----------|-------------|----------------|
| `ROAD_BUFFER_METERS` | Half road width + setback distance | 8-15m (minor roads)<br>12-20m (main roads) |
| `MIN_AREA_SQM` | Minimum acceptable plot size | 250-400 m² (urban)<br>400-800 m² (suburban)<br>1000+ m² (rural) |
| `MAX_AREA_SQM` | Maximum acceptable plot size<br>(0 = no limit) | 1500-2500 m² (residential)<br>0 (no limit) |

### Coordinate Reference System

| Region | CRS | EPSG Code |
|--------|-----|-----------|
| South Africa (Mpumalanga) | WGS 84 / UTM Zone 36S | `EPSG:32736` |
| South Africa (Western Cape) | WGS 84 / UTM Zone 34S | `EPSG:32734` |
| South Africa (Eastern Cape) | WGS 84 / UTM Zone 35S | `EPSG:32735` |

**Important:** Use a projected CRS (UTM) for accurate metric calculations, not geographic CRS (lat/lon).

---

## Output

The tool creates a polygon layer with cadastral boundaries:

- **Format**: GeoPackage (.gpkg)
- **Geometry**: Polygons
- **CRS**: Same as TARGET_CRS (metric)
- **Attributes**: Standard QGIS attributes + calculated area

---

## Workflow Example

### Complete Process for a New Area

1. **Extract roads from OpenStreetMap:**
   ```python
   # In QGIS Python Console
   import processing
   
   processing.run("native:extractbyexpression", {
       'INPUT': 'map.osm',
       'EXPRESSION': '"highway" IS NOT NULL',
       'OUTPUT': 'roads.gpkg'
   })
   ```

2. **Load building points:**
   - Import CSV with coordinates
   - Or use existing point layer

3. **Check CRS compatibility:**
   ```python
   road_layer = QgsProject.instance().mapLayersByName('roads')[0]
   building_layer = QgsProject.instance().mapLayersByName('buildings')[0]
   
   print(f"Roads CRS: {road_layer.crs().authid()}")
   print(f"Buildings CRS: {building_layer.crs().authid()}")
   ```

4. **Configure and run cadastral generator:**
   - Edit `Config` class in script
   - Run script from Python Console

5. **Review and refine:**
   - Check generated cadastrals
   - Adjust parameters if needed
   - Re-run with new settings

---

## Troubleshooting

### Problem: "Layer not found"
**Solution:** Check that layer names in `Config` match exactly (case-sensitive)

### Problem: "0 cadastrals generated"
**Solutions:**
- Verify layers overlap spatially
- Check CRS is correct for your region
- Reduce minimum area threshold
- Increase maximum area or set to 0

### Problem: "Cadastrals too large/small"
**Solutions:**
- Adjust `MIN_AREA_SQM` and `MAX_AREA_SQM`
- Check that `TARGET_CRS` is a metric projection (UTM)
- Verify road buffer distance is appropriate

### Problem: "Irregular shapes"
**Solutions:**
- This is normal for Voronoi method
- Reflects actual building positions
- For more regular shapes, consider grid-based method

---

## Technical Details

### Algorithm Steps

1. **Layer Retrieval**: Get road and building layers from QGIS project
2. **CRS Reprojection**: Reproject to metric CRS (UTM) for accurate measurements
3. **Road Buffering**: Create road reserve by buffering centerlines
4. **Voronoi Generation**: Create Thiessen polygons from building points
5. **Subtraction**: Remove road reserves from Voronoi polygons
6. **Filtering**: Keep only polygons within area constraints
7. **Output**: Save as GeoPackage and add to project

### Dependencies

- **QGIS 3.x** (tested on 3.34 LTR)
- **Python 3.x** (included with QGIS)
- **PyQt5** (included with QGIS)
- **Processing plugin** (included with QGIS)

### Performance

- **Small datasets** (<1,000 buildings): < 10 seconds
- **Medium datasets** (1,000-10,000 buildings): 10-60 seconds
- **Large datasets** (>10,000 buildings): 1-5 minutes

---

## Advanced Usage

### Programmatic Usage

```python
from cadastral_generator import generate_cadastrals, Config

# Create custom configuration
config = Config()
config.ROAD_LAYER_NAME = 'my_roads'
config.BUILDING_LAYER_NAME = 'my_buildings'
config.ROAD_BUFFER_METERS = 12.0
config.MIN_AREA_SQM = 300.0

# Generate cadastrals
result = generate_cadastrals(config)

if result:
    print(f"Generated {result.featureCount()} cadastrals")
```

### Batch Processing

```python
# Process multiple areas
areas = [
    ('Area1_roads', 'Area1_buildings', 'area1_cadastrals.gpkg'),
    ('Area2_roads', 'Area2_buildings', 'area2_cadastrals.gpkg'),
]

for road_name, building_name, output_path in areas:
    config = Config()
    config.ROAD_LAYER_NAME = road_name
    config.BUILDING_LAYER_NAME = building_name
    config.OUTPUT_PATH = output_path
    
    generate_cadastrals(config)
```

---

## Future Enhancements

Potential improvements for future versions:

- [ ] Variable buffer by road classification
- [ ] Point clustering/cleaning for ML-generated data
- [ ] Grid-based method option
- [ ] Orthogonalization (90° corners)
- [ ] Street frontage calculation
- [ ] Corner lot detection
- [ ] GUI interface
- [ ] QGIS plugin packaging

---

## License

This tool is provided as-is for cadastral generation purposes. Modify and distribute freely.

---

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review QGIS logs: `View > Panels > Log Messages`
3. Verify input data quality
4. Test with smaller datasets first

---

## Version History

- **v1.0** (2025-10-08): Initial release
  - Voronoi tessellation method
  - Metric CRS reprojection
  - Area filtering
  - Clean modular code structure

---

## References

- **Voronoi Diagrams**: https://en.wikipedia.org/wiki/Voronoi_diagram
- **QGIS Processing**: https://docs.qgis.org/latest/en/docs/user_manual/processing/
- **OSM Highway Tags**: https://wiki.openstreetmap.org/wiki/Key:highway
- **UTM Coordinate System**: https://en.wikipedia.org/wiki/Universal_Transverse_Mercator_coordinate_system
