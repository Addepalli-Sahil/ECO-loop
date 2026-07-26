# EnergyPlus validation report

## Run environment

- Engine: EnergyPlus 26.1.0
- Weather: `USA_CO_Golden-NREL.724666_TMY3.epw` bundled with EnergyPlus
- Baseline: `models/energyplus_baseline.idf`
- Optimized scenario: `models/energyplus_optimized.idf`
- Control change: heating schedule setpoint reduced from 20.0 C to 19.5 C.

Both annual EnergyPlus runs completed with exit code 0. Raw CSV and error logs
are retained locally in `.energyplus-validation/` and intentionally ignored by
Git because they are generated artifacts.

## Results

| Metric | Baseline | Optimized | Change |
| --- | ---: | ---: | ---: |
| Facility electricity | 12,192.49 kWh | 11,692.92 kWh | **-4.10%** |
| Electricity saved | — | 499.58 kWh | — |
| Estimated cost saved at $0.12/kWh | — | $59.95 | — |
| Mean zone temperature | 21.15 C | 20.81 C | -0.33 C |
| Temperature-derived PMV proxy | 0.06 | -0.07 | within +/-0.5 |
| Temperature-derived PPD proxy | 14.59% | 16.93% | below 20% |

Energy values are direct hourly EnergyPlus output. The selected EnergyPlus
example model does not emit Fanger PMV/PPD variables, so the dashboard reports
a transparent zone-temperature-derived comfort proxy. Do not describe it as an
EnergyPlus Fanger PMV result in the presentation.

## Reproduce

```powershell
& 'C:\EnergyPlusV26-1-0\energyplus.exe' --readvars `
  -w 'C:\EnergyPlusV26-1-0\WeatherData\USA_CO_Golden-NREL.724666_TMY3.epw' `
  -d .energyplus-validation\baseline-final models\energyplus_baseline.idf

& 'C:\EnergyPlusV26-1-0\energyplus.exe' --readvars `
  -w 'C:\EnergyPlusV26-1-0\WeatherData\USA_CO_Golden-NREL.724666_TMY3.epw' `
  -d .energyplus-validation\optimized-final models\energyplus_optimized.idf

python scripts\export_energyplus_results.py `
  --baseline .energyplus-validation\baseline-final\eplusout.csv `
  --optimized .energyplus-validation\optimized-final\eplusout.csv `
  --output-dir results
```
