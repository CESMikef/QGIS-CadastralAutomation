# Cadastral Automation Plugin

A QGIS plugin for automated cadastral/erf generation from road centerlines and building points.

## Quick Start

1. **Install the plugin** (see [PLUGIN_INSTALLATION.md](../PLUGIN_INSTALLATION.md))
2. **Load your data** into QGIS:
   - Road centerlines (line layer)
   - Building points (point layer) - optional for Blocks Mode
3. **Open the plugin**: `Vector` → `Cadastral Automation`
4. **Configure settings**:
   - Select your layers
   - Adjust parameters
   - Choose output location
5. **Click OK** to generate cadastrals

## Features

### Layer Selection
- **Centre Line Layer**: Select any line layer from your project
- **Point Data Layer**: Select any point layer (disabled in Blocks Mode)

### Adjustable Parameters
- **Road Buffer**: Distance to buffer roads (default: 10m)
- **Min/Max Area**: Filter cadastrals by size
- **Target CRS**: Choose appropriate metric CRS for your region

### Processing Modes

#### Cadastral Mode (Default)
Creates individual property boundaries using Voronoi tessellation from point data.

**Use for**: Individual property boundaries, residential planning

#### Blocks Mode
Creates only outer boundaries without inner subdivision.

**Use for**: Initial planning, development blocks, when point data isn't available

## File Structure

```
cadastral_automation/
├── __init__.py                          # Plugin initialization
├── metadata.txt                         # Plugin metadata
├── cadastral_automation.py              # Main plugin class
├── cadastral_automation_dialog.py       # Dialog class
├── cadastral_automation_dialog.ui       # UI definition
├── icon.png                            # Plugin icon
├── resources.qrc                       # Qt resources
└── README.md                           # This file
```

## Requirements

- QGIS 3.0 or higher
- PyQt5 (included with QGIS)
- QGIS Processing framework (included with QGIS)

## Support

For detailed documentation, see:
- [Plugin Installation Guide](../PLUGIN_INSTALLATION.md)
- [Main README](../README.md)
- [GitHub Repository](https://github.com/CESMikef/QGIS-CadastralAutomation)

## License

See LICENSE file in the repository root.
