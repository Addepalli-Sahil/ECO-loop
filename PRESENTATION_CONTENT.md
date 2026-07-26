# Eco-Loop Building Agents — presentation content

Use this content to replace the placeholders in the supplied deck, delete its
instruction slide, and export the final deck as PDF.

## Slide 1 — Title

**Eco-Loop Building Agents**  
Autonomous, comfort-aware building energy optimization  
Problem statement: Autonomous Building Management  
Theme: Smart and Sustainable Buildings  

## Slide 2 — Proposed solution

- EnergyPlus digital building model produces thermal and energy telemetry.
- A constrained AI agent evaluates occupancy, PMV/PPD and energy demand.
- The agent recommends setpoint, schedule and equipment actions through a
  controlled tool allow-list.
- Dashboard compares baseline and optimized operating profiles.
- Design goal: reduce kWh without allowing PMV outside +/-0.5 or PPD above 20%.

## Slide 3 — Technical approach

`EnergyPlus -> metrics -> agent/tool registry -> constrained actions -> EnergyPlus`

- Python: controller, EnergyPlus wrapper, data-validation utilities.
- Streamlit + Plotly: visual evidence of energy and comfort performance.
- Ollama-compatible local LLM endpoint with rules-based safe fallback.
- JSON logs retain actions, timestamps and result provenance.
- Long runtime logs are reduced to error/warning lines before agent use.

## Slide 4 — Feasibility and viability

- Works as a reproducible digital-twin demo now; dashboard is deployable from GitHub.
- Local, open-source model option limits cloud-data exposure.
- Safety guardrails reject unsafe setpoints before actuation.
- Production risks: EnergyPlus installation, model calibration and actuator mapping.
- Mitigation: test one zone first, maintain audit logs, require human approval for
  high-impact overrides.

## Slide 5 — Artifacts and results

- GitHub source: controller, agent tools, model, dashboard and CI workflow.
- Dashboard entry point: `streamlit_app.py`.
- Demo data: 365-hourly-profile comparison, deterministic and labelled as demo data.
- Latest demo output: approximately 15% modeled energy reduction while improving
  average PMV/PPD.
- Replace this slide's result figure with a screenshot from the deployed dashboard.

## Slide 6 — References

- EnergyPlus documentation: https://energyplus.net
- Streamlit documentation: https://docs.streamlit.io
- Model Context Protocol: https://modelcontextprotocol.io
- Fanger thermal-comfort PMV/PPD methodology (ISO 7730).
