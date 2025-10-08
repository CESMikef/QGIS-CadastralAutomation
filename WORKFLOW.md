# Cadastral Generation Workflow

## Visual Process Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         INPUT DATA                              │
├─────────────────────────────────────────────────────────────────┤
│  Road Centerlines (OSM)          Building Points (Google/ML)    │
│  ─────────────────               ─────────────────────          │
│  EPSG:4326 (lat/lon)             EPSG:4326 (lat/lon)            │
│  672 line features               11,527 point features          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    STEP 1: REPROJECT                            │
├─────────────────────────────────────────────────────────────────┤
│  Convert to metric CRS (EPSG:32736 - UTM Zone 36S)             │
│  • Roads: 672 features → 672 features                           │
│  • Buildings: 11,527 features → 11,527 features                 │
│  ✓ Now measurements are in meters, not degrees                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    STEP 2: BUFFER ROADS                         │
├─────────────────────────────────────────────────────────────────┤
│  Create road reserves by buffering centerlines                  │
│  • Buffer distance: 10 meters                                   │
│  • Dissolve overlaps: Yes                                       │
│  • Result: 1 dissolved polygon covering all roads + setback     │
│                                                                  │
│  ─────────  →  ═══════════                                      │
│   (line)       (buffered area)                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 STEP 3: CREATE VORONOI                          │
├─────────────────────────────────────────────────────────────────┤
│  Generate Voronoi (Thiessen) polygons from building points     │
│  • Input: 11,527 building points                                │
│  • Output: 11,527 Voronoi polygons                              │
│  • Each polygon contains exactly 1 building                     │
│                                                                  │
│     •  •  •     →    ┌───┬───┬───┐                             │
│     •  •  •          │   │   │   │                             │
│     •  •  •          ├───┼───┼───┤                             │
│                      │   │   │   │                             │
│                      └───┴───┴───┘                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 STEP 4: SUBTRACT ROADS                          │
├─────────────────────────────────────────────────────────────────┤
│  Remove road reserves from Voronoi polygons                     │
│  • Voronoi polygons: 11,527                                     │
│  • After subtraction: ~11,000 (some removed entirely)           │
│  • Creates realistic setbacks from roads                        │
│                                                                  │
│  ┌───┬───┬───┐    ═══════════    ┌─┬─┬─┐                       │
│  │   │   │   │  -                 │ │ │ │                       │
│  ├───┼───┼───┤    (road buffer)   ├─┼─┼─┤                       │
│  │   │   │   │  =                 │ │ │ │                       │
│  └───┴───┴───┘                    └─┴─┴─┘                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  STEP 5: FILTER BY AREA                         │
├─────────────────────────────────────────────────────────────────┤
│  Keep only cadastrals within area constraints                   │
│  • Minimum: 250 m²                                              │
│  • Maximum: 2,000 m²                                            │
│  • Input: ~11,000 features                                      │
│  • Output: ~5,000 features (filtered)                           │
│                                                                  │
│  Removes:                                                        │
│  • Tiny fragments (< 250 m²)                                    │
│  • Unrealistic large plots (> 2,000 m²)                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      STEP 6: SAVE                               │
├─────────────────────────────────────────────────────────────────┤
│  Save to GeoPackage and add to QGIS project                    │
│  • Format: .gpkg                                                │
│  • CRS: EPSG:32736 (UTM)                                        │
│  • Features: ~5,000 cadastral polygons                          │
│  • Layer name: "Cadastrals"                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         OUTPUT                                  │
├─────────────────────────────────────────────────────────────────┤
│  ✓ Cadastral boundaries ready for use                          │
│  ✓ Respects building positions                                 │
│  ✓ Includes road setbacks                                      │
│  ✓ Realistic plot sizes                                        │
│  ✓ Ready for planning/deployment                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Concepts

### Voronoi Diagrams (Thiessen Polygons)

A Voronoi diagram partitions space based on distance to points. Each polygon contains all locations closer to its point than to any other point.

**Why use Voronoi?**
- Natural boundaries based on building positions
- Each building gets its own cadastral
- Respects spatial distribution of buildings
- Creates realistic, organic-looking plots

### Road Buffer

The buffer creates a "road reserve" - the area occupied by the road plus setback distance.

**Buffer distance = (Road width / 2) + Setback**

Example:
- Road width: 12m
- Setback: 4m
- Buffer distance: (12/2) + 4 = 10m

### CRS (Coordinate Reference System)

**Geographic CRS (EPSG:4326):**
- Units: Degrees (latitude/longitude)
- ❌ Bad for buffering: "10 degrees" ≈ 1,100 km!
- ❌ Bad for area: Results in square degrees

**Projected CRS (EPSG:32736):**
- Units: Meters
- ✓ Good for buffering: "10 meters" = 10 meters
- ✓ Good for area: Results in square meters

---

## Processing Time

| Dataset Size | Processing Time |
|--------------|-----------------|
| < 1,000 buildings | < 10 seconds |
| 1,000 - 10,000 buildings | 10-60 seconds |
| 10,000+ buildings | 1-5 minutes |

**Test case:** 11,527 buildings processed in ~30 seconds

---

## Quality Metrics

**Input Quality:**
- Road network completeness
- Building point accuracy
- Spatial overlap between roads and buildings

**Output Quality:**
- Number of cadastrals generated
- Area distribution (should match expected plot sizes)
- Visual inspection (boundaries look realistic)

**Typical Results:**
- 40-50% of input buildings result in valid cadastrals
- Remainder filtered out due to:
  - Too small (< 250 m²)
  - Too large (> 2,000 m²)
  - Completely within road reserve
  - Duplicate/clustered points

---

## Adjusting Parameters

### If cadastrals are too small:
- ✓ Decrease `ROAD_BUFFER_METERS`
- ✓ Decrease `MIN_AREA_SQM`

### If cadastrals are too large:
- ✓ Increase `ROAD_BUFFER_METERS`
- ✓ Decrease `MAX_AREA_SQM`

### If too many cadastrals filtered out:
- ✓ Widen area range (decrease MIN, increase MAX)
- ✓ Check CRS is metric (UTM)

### If roads are too wide/narrow:
- ✓ Adjust `ROAD_BUFFER_METERS`
- ✓ Typical values: 8-15m

---

## Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| 0 cadastrals generated | Wrong CRS (using degrees) | Use UTM projection |
| Roads cover everything | Buffer too large | Reduce ROAD_BUFFER_METERS |
| Tiny fragments everywhere | MIN_AREA too small | Increase MIN_AREA_SQM |
| Missing cadastrals | MAX_AREA too small | Increase MAX_AREA_SQM or set to 0 |
| Irregular shapes | Normal for Voronoi | This is expected behavior |

---

## Data Requirements

### Road Centerlines
- **Type:** Line features
- **Source:** OpenStreetMap, government data, digitized
- **Quality:** Should cover all major roads in area
- **CRS:** Any (will be reprojected)

### Building Points
- **Type:** Point features
- **Source:** Google, ML models, surveys, digitized
- **Quality:** One point per building (duplicates will cause issues)
- **CRS:** Any (will be reprojected)

### Spatial Overlap
- Roads and buildings must overlap spatially
- If no overlap, no cadastrals will be generated
- Check extents match before processing
