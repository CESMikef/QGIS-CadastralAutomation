# Project Summary: QGIS Cadastral/Erf Automation Tool

## Overview

This project provides an automated solution for generating cadastral boundaries (erfs/plots) from road centerlines and building points in QGIS. Developed for the Vuma project in Mpumalanga, South Africa.

## Problem Statement

**Challenge:** No existing cadastral data available for the project area. Only have:
- Road centerlines from OpenStreetMap
- Building demand points from Google/ML models

**Need:** Automatically generate realistic property boundaries (erfs) for planning and utility deployment.

## Solution

A Python script for QGIS that:
1. Takes road centerlines and building points as input
2. Reprojects to metric CRS for accurate calculations
3. Creates Voronoi polygons based on building positions
4. Subtracts road reserves with configurable setbacks
5. Filters by area to remove unrealistic plots
6. Outputs clean cadastral boundaries

## Key Features

✅ **Automatic CRS handling** - Handles lat/lon to UTM conversion  
✅ **Voronoi tessellation** - Natural boundaries based on building positions  
✅ **Configurable parameters** - Easy to adjust for different scenarios  
✅ **Clean, modular code** - Well-documented and maintainable  
✅ **Error handling** - Graceful failures with helpful messages  
✅ **Production-ready** - Successfully tested on 11,527 buildings

## Results

**Test Case: Msogwaba Area**
- Input: 672 roads, 11,527 building points
- Output: ~5,000 cadastral boundaries
- Processing time: ~30 seconds
- Area range: 250-2000 m² (configurable)

## Technical Stack

- **Platform:** QGIS 3.x
- **Language:** Python 3.x
- **Libraries:** qgis.core, qgis.processing
- **CRS:** EPSG:32736 (WGS 84 / UTM Zone 36S)
- **Output Format:** GeoPackage (.gpkg)

## File Structure

```
QGIS Plugin-ErfAutomation/
├── cadastral_generator.py    # Main script (clean, production code)
├── README.md                  # Full documentation
├── QUICK_START.md            # 5-minute getting started guide
├── LICENSE                    # MIT License
├── .gitignore                # Git ignore rules
└── PROJECT_SUMMARY.md        # This file
```

## Usage

```python
# In QGIS Python Console
exec(open('C:/path/to/cadastral_generator.py').read())
```

## Configuration

Edit the `Config` class in `cadastral_generator.py`:

```python
class Config:
    ROAD_LAYER_NAME = 'lines'
    BUILDING_LAYER_NAME = 'buildings'
    OUTPUT_PATH = 'cadastrals.gpkg'
    ROAD_BUFFER_METERS = 10.0
    MIN_AREA_SQM = 250.0
    MAX_AREA_SQM = 2000.0
    TARGET_CRS = 'EPSG:32736'
```

## Development History

1. **Initial prototype** - Basic Voronoi generation
2. **CRS fix** - Added metric projection (critical fix)
3. **Point cleaning** - Added clustering for ML-generated data
4. **Code cleanup** - Refactored into clean, modular structure
5. **Documentation** - Comprehensive docs and guides
6. **GitHub repo** - Organized professional codebase

## Future Enhancements

- [ ] GUI interface for easier parameter adjustment
- [ ] Point clustering/cleaning built-in
- [ ] Grid-based method option
- [ ] Variable road buffers by classification
- [ ] QGIS plugin packaging
- [ ] Batch processing for multiple areas

## Lessons Learned

1. **CRS matters!** - Always use metric projection (UTM) for buffering/area calculations
2. **ML data needs cleaning** - Building points from ML models have duplicates/clusters
3. **Voronoi works well** - Natural-looking boundaries that respect building positions
4. **Modular code wins** - Clean functions make debugging and enhancement easier

## Applications

- **Utility planning** - Fiber/electricity network design
- **Property development** - Initial plot layout
- **Urban planning** - Informal settlement regularization
- **Cadastral surveys** - Starting point for formal surveys

## Contact

**Author:** Matthew Fenn  
**Organization:** Corelinefibre  
**Date:** October 2025

---

## Quick Reference

**Minimum viable usage:**
```python
# 1. Load layers in QGIS
# 2. Edit Config in script
# 3. Run:
exec(open('cadastral_generator.py').read())
```

**Key parameters:**
- `ROAD_BUFFER_METERS`: 8-15m typical
- `MIN_AREA_SQM`: 250-400m² urban, 1000+ rural
- `TARGET_CRS`: Use local UTM zone

**Common CRS for South Africa:**
- Western Cape: EPSG:32734 (UTM 34S)
- Eastern Cape: EPSG:32735 (UTM 35S)
- Mpumalanga: EPSG:32736 (UTM 36S)
