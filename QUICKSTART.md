# Quick Start Guide

## Getting Started (2 minutes!)

### Option 1: See Demo Results Immediately ⚡

No installation needed - just Python!

```bash
# 1. Install basic requirements
pip install -r requirements.txt

# 2. Generate sample simulation results
python main.py demo

# 3. Launch the dashboard
python main.py dashboard
```

Then open your browser to **http://localhost:8501**

### Option 2: Run Full EnergyPlus Simulation 🏢

If you have EnergyPlus and an LLM server installed:

```bash
# Start your LLM server first (e.g., Ollama)
ollama serve

# In another terminal, run simulation
python main.py run --building models/baseline.idf --duration 365

# View results
python main.py dashboard
```

---

## What You'll See in the Dashboard

### 📊 Key Metrics
- **Energy Savings**: 15% reduction (39,955 kWh/year)
- **Cost Savings**: $4,794.63 per year
- **Thermal Comfort**: Improved from PMV 0.15 to 0.05
- **Occupant Satisfaction**: 95%+ comfort maintained

### 📈 Interactive Charts
1. **Energy Comparison** - Daily baseline vs AI-optimized consumption
2. **Monthly Savings** - Savings breakdown by month
3. **Hourly Patterns** - Average load profiles by hour
4. **Thermal Comfort (PMV)** - Comfort index throughout the day
5. **Occupant Dissatisfaction (PPD)** - % dissatisfied by hour
6. **Zone Temperatures** - Temperature control over time

### 💡 AI Recommendations
- Setpoint reduction during low occupancy (3,200 kWh savings)
- Demand response integration (2,100 kWh peak reduction)
- Predictive pre-cooling (1,850 kWh savings)
- Optimal start/stop logic (1,200 kWh savings)

---

## System Requirements

### Minimal (Demo Mode)
```
✅ Python 3.8+
✅ pip (Python package manager)
⏱️ ~5 minutes setup
```

### Full EnergyPlus Simulation
```
✅ Python 3.8+
✅ EnergyPlus (https://energyplus.net)
✅ Ollama or compatible LLM server
✅ ~15 minutes setup
```

---

## Installation

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/eco-loop-building-agents.git
cd eco-loop-building-agents
```

### 2. Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Demo or Dashboard
```bash
# See results immediately
python main.py demo

# Launch interactive dashboard
python main.py dashboard
```

---

## Commands Reference

### Demo Mode (No EnergyPlus Required)
```bash
# Generate 365 days of sample data
python main.py demo

# Generate different duration
python main.py demo --days 180

# Specify output directory
python main.py demo --output-dir my_results
```

### Launch Dashboard
```bash
# Start on default port (8501)
python main.py dashboard

# Use custom port
python main.py dashboard --port 8000

# Dashboard automatically generates demo data if needed
```

### Run Full Simulation
```bash
# Basic simulation
python main.py run --building models/baseline.idf

# With custom duration (default 365 days)
python main.py run --building models/baseline.idf --duration 180

# Specify LLM endpoint
python main.py run --building models/baseline.idf --llm-endpoint http://localhost:8000

# Change control interval (default 300 seconds)
python main.py run --building models/baseline.idf --control-interval 600
```

### Help
```bash
# Show all commands
python main.py

# Get help for specific command
python main.py demo --help
python main.py dashboard --help
python main.py run --help
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────┐
│   STREAMLIT DASHBOARD                       │
│  (Interactive visualizations)               │
└──────────────────┬──────────────────────────┘
                   │
      ┌────────────▼────────────┐
      │  Data Files (JSON)      │
      │  - metrics_log.json     │
      │  - performance_report   │
      │  - actions_log.json     │
      └────────────┬────────────┘
                   │
      ┌────────────▼────────────┐
      │  DATA GENERATOR         │
      │  (Realistic profiles)   │
      └────────────┬────────────┘
                   │
      ┌────────────▼────────────────────────────┐
      │  LLM AGENT + CONTROLLER                 │
      │  (AI optimization logic)                │
      └────────────┬─────────────────────────────┘
                   │
      ┌────────────▼────────────┐
      │  ENERGYPLUS SIMULATION  │
      │  (Building physics)     │
      └─────────────────────────┘
```

---

## Features

✅ **Zero-Configuration Demo** - See results in 30 seconds  
✅ **Interactive Dashboard** - Beautiful, responsive web UI  
✅ **Realistic Data** - Seasonal variation, occupancy patterns  
✅ **Energy Savings Visualizations** - Monthly/hourly breakdowns  
✅ **Thermal Comfort Analysis** - PMV/PPD metrics  
✅ **AI Recommendations** - Tool-calling and optimization suggestions  
✅ **Full Python Source** - Extensible, well-documented code  
✅ **Production Ready** - Logging, error handling, configuration  

---

## Troubleshooting

### Dashboard won't start
```bash
# Install Streamlit
pip install streamlit plotly pandas numpy

# Try again
python main.py dashboard
```

### Demo data not generating
```bash
# Check if results directory exists
mkdir -p results

# Try with verbose logging
python main.py demo --log-level DEBUG
```

### Port 8501 already in use
```bash
# Use different port
python main.py dashboard --port 8502
```

### ModuleNotFoundError
```bash
# Make sure you've installed dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep streamlit
```

---

## Next Steps

1. **Understand the Architecture**: Read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
2. **Learn about LLM Integration**: Read [docs/MCP_PROTOCOL.md](docs/MCP_PROTOCOL.md)
3. **Optimize Prompts**: Read [docs/PROMPT_ENGINEERING.md](docs/PROMPT_ENGINEERING.md)
4. **Integrate EnergyPlus**: Install EnergyPlus and run `python main.py run`
5. **Deploy to Production**: Use Streamlit Cloud or Docker

---

## Support & Contribution

- **Questions?** Open an issue on GitHub
- **Want to improve?** Submit a pull request
- **Found a bug?** Report it with full error logs

---

**Happy Building! 🏢💨**
