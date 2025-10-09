# Changelog

All notable changes to the QGIS Cadastral/Erf Automation Tool will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2025-10-08

### Added
- Initial release of cadastral generation tool
- Automatic CRS reprojection to metric (UTM)
- Voronoi tessellation from building points
- Road buffer creation with configurable distance
- Area-based filtering (min/max constraints)
- Clean, modular code structure
- Comprehensive documentation (README, QUICK_START, WORKFLOW)
- Error handling and informative messages
- GeoPackage output format
- Automatic layer addition to QGIS project

### Features
- **Core Algorithm:**
  - Voronoi polygon generation
  - Road reserve subtraction
  - Area filtering
  - CRS handling

- **Configuration:**
  - Configurable road buffer distance
  - Configurable area constraints
  - Configurable target CRS
  - Easy-to-edit Config class

- **Output:**
  - GeoPackage format
  - Metric CRS (UTM)
  - Automatic project integration

### Technical Details
- Platform: QGIS 3.x
- Language: Python 3.x
- Dependencies: qgis.core, qgis.processing
- Tested on: QGIS 3.34 LTR
- Test dataset: 11,527 buildings, 672 roads
- Processing time: ~30 seconds for test dataset

### Documentation
- README.md: Full documentation
- QUICK_START.md: 5-minute getting started guide
- WORKFLOW.md: Visual process flow and technical details
- PROJECT_SUMMARY.md: Project overview and history
- LICENSE: MIT License
- .gitignore: Python and QGIS ignore rules

---

## [1.1.0] - 2025-10-09

### Added - QGIS Plugin
- **Full QGIS Plugin Implementation**
  - User-friendly dialog interface
  - Layer selection dropdowns (no hardcoded layer names)
  - Adjustable parameters in UI (buffer distance, min/max area, CRS)
  - Real-time parameter validation
  - Progress logging to QGIS message log
  
- **Blocks Mode Feature**
  - Toggle to create outer boundaries only
  - No point data required in blocks mode
  - Useful for initial planning and development blocks
  - Automatically disables point layer selector when enabled

- **Progress Feedback System**
  - Progress dialog with step-by-step updates
  - Cancellable processing (user can abort at any time)
  - Progress bar showing completion percentage
  - Detailed messages for each processing step
  - QGIS message bar notifications for success/errors
  - Responsive UI during processing

- **Plugin Infrastructure**
  - metadata.txt with plugin information
  - __init__.py for plugin loading
  - Programmatic UI creation (no .ui file dependency)
  - Icon and resources
  - Installation batch script for Windows
  - Comprehensive plugin documentation

### Changed
- Reorganized project structure with plugin folder
- Updated README with plugin installation instructions
- Enhanced documentation with plugin usage guide
- Dialog created programmatically instead of .ui file for better compatibility

### Fixed
- Resolved QgsMapLayerProxyModel enum issue by creating UI programmatically
- Improved error handling with proper dialog cleanup

### Technical Details
- Plugin compatible with QGIS 3.0+
- Uses QgsMapLayerComboBox for layer selection
- Uses QgsProjectionSelectionWidget for CRS selection
- Uses QgsFileWidget for output path selection
- Uses QProgressDialog for progress feedback
- Automatic layer filtering (lines/points)
- Progress callback system for real-time updates

### Documentation
- PLUGIN_INSTALLATION.md: Complete plugin installation guide
- install_plugin.bat: Automated Windows installation script
- Updated README.md with plugin information
- Plugin-specific README in plugin folder

---

## [Unreleased]

### Planned Features
- Point clustering/cleaning for ML-generated data
- Grid-based method option
- Orthogonalization (90° corners)
- Variable road buffers by classification
- Batch processing

### Under Consideration
- Street frontage calculation
- Corner lot detection
- Building count per cadastral
- Cadastral ID generation
- Export to multiple formats
- Integration with cadastral databases
- Plugin repository submission

---

## Version History Summary

| Version | Date | Description |
|---------|------|-------------|
| 1.1.0 | 2025-10-09 | QGIS Plugin with UI, layer selection, and blocks mode |
| 1.0.0 | 2025-10-08 | Initial release with core functionality |

---

## Development Notes

### v1.0.0 Development Process

1. **Prototype Phase**
   - Basic Voronoi generation
   - Initial testing with sample data
   - Identified CRS issues

2. **Critical Fix**
   - Added metric CRS reprojection
   - Fixed buffer distance calculations
   - Resolved "0 cadastrals" issue

3. **Code Cleanup**
   - Refactored into modular functions
   - Added comprehensive documentation
   - Improved error handling

4. **Testing**
   - Tested on Vuma project (Msogwaba area)
   - 11,527 buildings → ~5,000 cadastrals
   - Validated output quality

5. **Release Preparation**
   - Created GitHub repository structure
   - Wrote comprehensive documentation
   - Added license and changelog

### Key Decisions

- **Voronoi over Grid:** Chose Voronoi method for natural boundaries that respect building positions
- **Metric CRS:** Critical for accurate buffering and area calculations
- **Modular Design:** Separate functions for each processing step
- **Config Class:** Easy parameter adjustment without modifying code
- **GeoPackage Output:** Modern, efficient format with good QGIS support

### Lessons Learned

1. CRS matters immensely for spatial operations
2. ML-generated building data needs cleaning
3. Modular code is easier to debug and enhance
4. Good documentation is as important as good code
5. Real-world testing reveals issues not apparent in theory

---

## Migration Guide

### From Prototype Scripts

If you were using the prototype scripts (`RUN_ME.py`, `RUN_ME_FIXED.py`, etc.), migrate to v1.0.0:

**Old way:**
```python
exec(open('RUN_ME_FIXED.py').read())
```

**New way:**
```python
exec(open('cadastral_generator.py').read())
```

**Configuration changes:**
- Edit the `Config` class instead of variables at top of script
- Same parameters, just organized differently
- More maintainable and extensible

---

## Support

For issues, questions, or contributions:
- Check documentation first (README.md, WORKFLOW.md)
- Review QGIS logs for error details
- Test with smaller datasets to isolate issues
- Verify CRS is metric (UTM)

---

## Contributors

- **Matthew Fenn** - Initial development and documentation
- **Corelinefibre** - Project sponsor and testing

---

## Acknowledgments

- QGIS Development Team - For excellent GIS platform
- OpenStreetMap Contributors - For road data
- Google Building Footprints - For building data
