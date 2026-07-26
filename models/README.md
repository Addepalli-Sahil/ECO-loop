# Building Models

This directory contains EnergyPlus building model files (`.idf` format) used for simulations.

## Files

### baseline.idf
Base building model representing a typical office/commercial building.

**Building characteristics:**
- 5-zone typical office layout
- Standard HVAC system with VAV terminals
- Baseline occupancy and lighting schedules
- Weather file: TMY3 climate data (typical year)

### Models Overview

```
Building Type: Commercial Office
Size: ~2,000 m² (5 zones)
Location: Temperate climate
Occupancy: 9 AM - 5 PM weekdays
```

## Running Simulations

```bash
# Run baseline model
python -m eco_loop.controller --building models/baseline.idf --duration 365

# Run with custom weather file
python -m eco_loop.controller --building models/baseline.idf --weather data/weather.epw
```

## Model Modification

To create modified versions:

1. **Edit IDF files** using EnergyPlus IDD reference
2. **Add ECMs** (Energy Conservation Measures) to test scenarios
3. **Run comparison** to measure impact

Example ECM: Add automated blind controls
```
New ObjectType,Blind_Control
  Enable automated exterior shades at 500 W/m2 solar intensity
  Reduces cooling load by ~15%
```

## Climate/Weather Data

Place weather files in `data/weather/`:
- Format: `.epw` (EnergyPlus Weather)
- Download from: https://energyplus.net/weather
- Used for solar radiation, temperature, humidity inputs

---

**Note**: Original IDF files are version-controlled. Generated simulation outputs are in `/results/`
