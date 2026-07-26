# Eco-Loop Building Agents

An autonomous closed-loop building management system that combines EnergyPlus building simulations with open-source LLMs (Large Language Models) to continuously optimize energy consumption while maintaining occupant comfort.

## Overview

This proof-of-concept (PoC) demonstrates how AI-driven agents can transform buildings from passive energy consumers into active, self-correcting systems. By integrating:

- **EnergyPlus**: High-fidelity building energy simulation engine
- **Open-Source LLM**: AI reasoning and decision-making (Llama 3, Mistral, or Qwen)
- **Model Context Protocol (MCP)**: Standardized communication between systems
- **Closed-Loop Control**: Real-time feedback and continuous optimization

The system automatically discovers energy-saving opportunities while respecting thermal comfort constraints.

## Architecture

```
EnergyPlus Simulation
        ↓
   Metrics Stream
   (Temperature, HVAC, Load, PMV)
        ↓
   LLM Agent
   (Analysis & Reasoning)
        ↓
   Control Actions
   (Set-point Updates, Overrides)
        ↓
EnergyPlus Updates (Forward Loop)
```

## Key Features

- ✅ **Real-time Simulation Streaming**: Continuous performance metrics from EnergyPlus
- ✅ **AI-Driven Decision Making**: LLM analyzes data and recommends energy conservation measures (ECMs)
- ✅ **Autonomous Control Loop**: Automatic injection of optimized set-points back into simulation
- ✅ **Comfort Preservation**: Maintains thermal comfort metrics (PMV) within acceptable bounds
- ✅ **Quantifiable Savings**: Dashboard showing energy reduction percentages
- ✅ **Self-Correcting**: LLM can handle simulation errors and adapt strategies

## Quick Start

### Prerequisites

- Python 3.8+
- EnergyPlus (any recent version)
- Ollama or similar LLM server (for running open-source models locally)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/eco-loop-building-agents.git
cd eco-loop-building-agents

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Simulation

```bash
# Start the LLM server (using Ollama with Llama 2)
ollama serve

# In another terminal, run the closed-loop controller
python -m eco_loop.controller --building models/baseline.idf --duration 365
```

## Project Structure

```
eco-loop-building-agents/
├── src/eco_loop/
│   ├── __init__.py
│   ├── energyplus_wrapper.py      # EnergyPlus API wrapper
│   ├── llm_agent.py                # LLM orchestration & reasoning
│   ├── mcp_server.py               # MCP protocol implementation
│   ├── controller.py               # Main closed-loop controller
│   ├── metrics.py                  # Metrics collection & analysis
│   └── utils.py                    # Utility functions
├── models/
│   ├── baseline.idf                # Base building model
│   └── README.md                   # Model documentation
├── dashboard/
│   ├── app.py                      # Streamlit/Flask dashboard
│   └── requirements.txt            # Dashboard dependencies
├── docs/
│   ├── ARCHITECTURE.md             # System architecture document
│   ├── MCP_PROTOCOL.md             # MCP implementation details
│   └── PROMPT_ENGINEERING.md       # LLM prompting strategies
├── tests/
│   ├── test_energyplus.py
│   ├── test_llm_agent.py
│   └── test_controller.py
├── requirements.txt                # Python dependencies
├── setup.py                        # Package setup
└── README.md                       # This file
```

## Deliverables

- [x] **GitHub Repository**: Fully functional source code
- [ ] **Building Models**: Baseline and optimized `.idf` files
- [ ] **Savings Dashboard**: Visual comparison of baseline vs AI-optimized performance
- [ ] **Architecture Document**: Technical explanation of tool-calling & control strategies
- [ ] **PoC Video**: 3-minute demonstration of live closed-loop operation
- [ ] **Presentation Slides**: Solution overview and results

## Evaluation Criteria

1. **System Integration (30%)**: Robust, crash-free execution over extended simulation periods
2. **Energy Efficiency (25%)**: Quantifiable kWh reduction vs baseline
3. **Thermal Comfort (20%)**: Maintained comfort while saving energy
4. **Agentic Autonomy (15%)**: Creative use of LLM tool-calling and MCP protocols
5. **Documentation (10%)**: Clear architecture, visuals, and delivery quality

## Technical Highlights

### Tool-Calling Architecture

The LLM agent has access to the following tools:

- `run_simulation(duration, set_points)`: Execute EnergyPlus with specified parameters
- `get_metrics(timestamp_range)`: Retrieve building performance metrics
- `update_schedule(hvac_schedule)`: Modify HVAC operational schedules
- `analyze_comfort(zone_data)`: Evaluate thermal comfort indices (PMV/PPD)
- `optimize_ecm(current_metrics, constraints)`: Calculate energy conservation measures

### Prompt Engineering Strategy

- **System Prompt**: Defines agent role as autonomous building optimizer
- **Few-Shot Examples**: Demonstrates typical reasoning patterns
- **Constraint Embedding**: Hard limits on temperature, humidity, occupancy
- **Context Compression**: Summarizes lengthy logs to manage token usage

## Contributing

Contributions are welcome! Please feel free to submit PRs for:
- Additional building models
- New LLM backends
- Dashboard enhancements
- Documentation improvements

## License

MIT License - See LICENSE file for details

## Contact

For questions or collaboration, please open an issue on GitHub.

---

**Hackathon**: Honeywell's Autonomous Building Management Challenge  
**Challenge**: Create a live PoC that proves AI-driven buildings can achieve quantifiable energy savings while maintaining comfort.
