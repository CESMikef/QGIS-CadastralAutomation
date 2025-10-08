# Quick Start Guide

Get up and running in 5 minutes!

## Step 1: Prepare Your Data

1. Open QGIS
2. Load your road centerlines layer (line features)
3. Load your building points layer (point features)
4. Note the exact layer names in the Layers panel

## Step 2: Configure the Script

Open `cadastral_generator.py` and edit these lines:

```python
class Config:
    ROAD_LAYER_NAME = 'lines'              # ← Change to your road layer name
    BUILDING_LAYER_NAME = 'buildings'      # ← Change to your building layer name
    OUTPUT_PATH = 'C:/output/cadastrals.gpkg'  # ← Change to your desired output path
```

## Step 3: Run the Script

1. Open QGIS Python Console: `Plugins > Python Console` (or `Ctrl+Alt+P`)
2. Run this command:

```python
exec(open('C:/Users/mfenn/Documents/GitHub/QGIS Plugin-ErfAutomation/cadastral_generator.py').read())
```

3. Wait for processing (usually 10-60 seconds)
4. Done! Check your Layers panel for the new 'Cadastrals' layer

## Step 4: Adjust Parameters (Optional)

If results aren't perfect, adjust these parameters in `Config`:

```python
ROAD_BUFFER_METERS = 10.0    # Increase if roads too narrow, decrease if too wide
MIN_AREA_SQM = 250.0         # Increase to remove small fragments
MAX_AREA_SQM = 2000.0        # Increase to keep larger plots (0 = no limit)
```

Then re-run the script.

---

## Example for Vuma Project

```python
class Config:
    ROAD_LAYER_NAME = 'lines'
    BUILDING_LAYER_NAME = 'Msogwaba Point Data — extracted_location'
    OUTPUT_PATH = 'C:/Users/mfenn/OneDrive - Corelinefibre/Documents/QGIS Projects/Vuma/cadastrals.gpkg'
    
    ROAD_BUFFER_METERS = 10.0
    MIN_AREA_SQM = 250.0
    MAX_AREA_SQM = 2000.0
    TARGET_CRS = 'EPSG:32736'  # UTM Zone 36S for Mpumalanga
```

---

## Troubleshooting

**"Layer not found"**  
→ Check layer names match exactly (case-sensitive)

**"0 cadastrals generated"**  
→ Layers don't overlap or wrong CRS - check data

**Script won't run**  
→ Make sure you're running from QGIS Python Console, not regular Python

---

That's it! See `README.md` for full documentation.
