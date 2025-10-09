# Cadastral Automation Plugin - Installation Guide

## Overview

The Cadastral Automation plugin for QGIS generates cadastral boundaries (erfs) from road centerlines and building points using Voronoi tessellation. It supports two modes:

1. **Cadastral Mode**: Creates individual property boundaries using point data
2. **Blocks Mode**: Creates outer block boundaries only (no inner subdivision)

## Features

- ✅ **Layer Selection**: Choose any line and point layers from your project
- ✅ **Adjustable Parameters**: Customize buffer distance, min/max area, and CRS
- ✅ **Blocks Mode**: Toggle to create outer boundaries without inner cadastrals
- ✅ **User-Friendly UI**: Simple dialog with all controls in one place
- ✅ **Flexible Output**: Save to GeoPackage or Shapefile

## Installation

### Method 1: Manual Installation (Recommended)

1. **Locate your QGIS plugins folder**:
   - Windows: `C:\Users\[YourUsername]\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\`
   - macOS: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`
   - Linux: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`

2. **Copy the plugin folder**:
   ```
   Copy the entire 'cadastral_automation' folder to the plugins directory
   ```

3. **Restart QGIS**

4. **Enable the plugin**:
   - Go to `Plugins` → `Manage and Install Plugins`
   - Click on `Installed`
   - Find `Cadastral Automation` and check the box to enable it

### Method 2: Create ZIP and Install via QGIS

1. **Create a ZIP file**:
   - Compress the `cadastral_automation` folder into `cadastral_automation.zip`
   - Make sure the folder structure is: `cadastral_automation.zip/cadastral_automation/[files]`

2. **Install in QGIS**:
   - Go to `Plugins` → `Manage and Install Plugins`
   - Click `Install from ZIP`
   - Select your `cadastral_automation.zip` file
   - Click `Install Plugin`

## Usage

### 1. Open the Plugin

After installation, access the plugin via:
- **Menu**: `Vector` → `Cadastral Automation`
- **Toolbar**: Click the Cadastral Automation icon

### 2. Configure Parameters

#### Input Layers
- **Centre Line Layer**: Select your road centerlines layer (must be line geometry)
- **Point Data Layer**: Select your building/point data layer (required for Cadastral Mode)

#### Processing Parameters
- **Road Buffer (m)**: Distance to buffer roads (typically half road width + setback)
  - Default: 10.0 meters
  - Range: 0.1 - 100.0 meters

- **Minimum Area (m²)**: Minimum cadastral area to keep
  - Default: 250 m²
  - Filters out small slivers and artifacts

- **Maximum Area (m²)**: Maximum cadastral area to keep
  - Default: 2000 m²
  - Set to 0 for no upper limit

- **Target CRS**: Coordinate Reference System for processing
  - Default: EPSG:32736 (WGS 84 / UTM Zone 36S)
  - **Must be a metric CRS** for accurate buffer distances

#### Processing Mode
- **Blocks Mode**: Check this to create only outer boundaries
  - When enabled, point data layer is not required
  - Creates blocks by buffering roads and extracting the negative space
  - Useful for initial planning or when individual cadastrals aren't needed

#### Output
- **Output File**: Specify where to save the result
  - Supports GeoPackage (.gpkg) and Shapefile (.shp)
  - Layer will be automatically added to your project

### 3. Run Processing

Click **OK** to start processing. 

**Progress Feedback:**
- A **progress dialog** will appear showing the current processing step
- Progress messages are logged to the QGIS message log (`View > Panels > Log Messages`)
- You can **cancel** processing at any time by clicking the Cancel button
- A **success message** will appear in the QGIS message bar when complete

## Examples

### Example 1: Individual Cadastrals

**Use Case**: Generate property boundaries for a residential area

**Settings**:
- Centre Line Layer: `road_centerlines`
- Point Data Layer: `building_points`
- Road Buffer: 10.0 m
- Min Area: 250 m²
- Max Area: 2000 m²
- Blocks Mode: ❌ Unchecked

**Result**: Individual cadastral polygons for each building

### Example 2: Blocks Only

**Use Case**: Create development blocks for initial planning

**Settings**:
- Centre Line Layer: `road_centerlines`
- Point Data Layer: (not required)
- Road Buffer: 10.0 m
- Min Area: 500 m²
- Max Area: 0 (no limit)
- Blocks Mode: ✅ Checked

**Result**: Outer block boundaries without internal subdivision

## Troubleshooting

### Plugin doesn't appear in menu

1. Check that the plugin is enabled in `Plugins` → `Manage and Install Plugins`
2. Restart QGIS
3. Check the QGIS Python console for error messages

### "No features created" error

1. Verify your input layers have features
2. Check that layers overlap spatially
3. Ensure your CRS is appropriate for your data location
4. Try adjusting the min/max area parameters

### Processing is slow

- Large datasets may take time to process
- Consider processing smaller areas at a time
- Check the QGIS message log for progress updates

### Results look incorrect

1. **Wrong CRS**: Ensure you're using a metric CRS appropriate for your region
2. **Buffer too large**: Reduce the road buffer distance
3. **Area filters too strict**: Adjust min/max area parameters
4. **Data quality**: Check your input data for errors or gaps

## Technical Details

### Processing Workflow (Cadastral Mode)

1. Reproject input layers to target CRS
2. Buffer road centerlines by specified distance
3. Create Voronoi polygons from point data
4. Subtract road buffers from Voronoi polygons
5. Filter results by area constraints
6. Save to output file

### Processing Workflow (Blocks Mode)

1. Reproject road centerlines to target CRS
2. Buffer road centerlines by specified distance
3. Create extent polygon around buffered roads
4. Subtract road buffers from extent (negative space)
5. Convert multipart to singlepart polygons
6. Filter results by area constraints
7. Save to output file

### Dependencies

- QGIS 3.0 or higher
- QGIS Processing framework (included with QGIS)
- PyQt5 (included with QGIS)

## Support

For issues, questions, or contributions:
- GitHub: https://github.com/CESMikef/QGIS-CadastralAutomation
- Issues: https://github.com/CESMikef/QGIS-CadastralAutomation/issues

## License

See LICENSE file in the repository.

## Author

Matthew Fenn - 2025
