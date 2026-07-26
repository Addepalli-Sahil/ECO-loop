# Deploy the Eco-Loop dashboard from GitHub

## Local run

```powershell
pip install -r requirements.txt
python main.py demo
python -m streamlit run streamlit_app.py
```

The dashboard is served at `http://localhost:8501`. Its entry file is
`streamlit_app.py`; it reads `results/metrics_log.json` and
`results/performance_report.json`.

## Streamlit Community Cloud

1. Create a GitHub repository and push this folder's contents.
2. In Streamlit Community Cloud, select **Create app** and choose that repo and branch.
3. Set **Main file path** to `streamlit_app.py`.
4. Deploy. Community Cloud installs `requirements.txt` automatically.

Do not claim the dashboard's demo figures are live EnergyPlus measurements.
The source banner identifies the current data type. For a validated submission,
replace the generated result JSON with EnergyPlus baseline and optimized exports.

## Full EnergyPlus validation

Install EnergyPlus separately and ensure `energyplus` is on `PATH`; also provide
an `.epw` weather file compatible with the IDF. An Ollama-compatible LLM endpoint
is optional because the agent has a conservative rules-based fallback. The current
repository includes the dashboard and demo workflow; production validation must be
performed on the target EnergyPlus installation before submitting measured savings.
