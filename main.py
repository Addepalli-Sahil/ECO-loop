"""
Eco-Loop Building Agents - Main Entry Point

Run the autonomous closed-loop building optimization system or launch the dashboard.

Usage:
    python main.py --building path/to/model.idf --duration 365
    python main.py --building models/baseline.idf --duration 180 --llm-endpoint http://localhost:11434
    python main.py --dashboard                    # Launch the Streamlit dashboard
    python main.py --demo                         # Run with sample data (no EnergyPlus needed)
"""

import argparse
import logging
import sys
import subprocess
from pathlib import Path

from src.eco_loop.controller import ClosedLoopController
from src.eco_loop.data_generator import generate_simulation_results
from src.eco_loop.utils import setup_logging, format_performance_summary


def main():
    """Main entry point for Eco-Loop system."""
    
    parser = argparse.ArgumentParser(
        description="Eco-Loop Building Agents - Autonomous AI-driven building optimization"
    )
    
    # Sub-commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # ===== RUN COMMAND =====
    run_parser = subparsers.add_parser("run", help="Run closed-loop simulation")
    run_parser.add_argument(
        "--building",
        "-b",
        required=True,
        help="Path to EnergyPlus building model (.idf file)"
    )
    run_parser.add_argument(
        "--duration",
        "-d",
        type=int,
        default=365,
        help="Simulation duration in days (default: 365)"
    )
    run_parser.add_argument(
        "--llm-endpoint",
        default="http://localhost:11434",
        help="LLM server endpoint (default: http://localhost:11434 for Ollama)"
    )
    run_parser.add_argument(
        "--llm-model",
        default="llama2",
        help="LLM model name (default: llama2)"
    )
    run_parser.add_argument(
        "--control-interval",
        type=int,
        default=300,
        help="Control update interval in seconds (default: 300 = 5 minutes)"
    )
    run_parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)"
    )
    run_parser.add_argument(
        "--output-dir",
        default="./results",
        help="Output directory for results (default: ./results)"
    )
    
    # ===== DASHBOARD COMMAND =====
    dashboard_parser = subparsers.add_parser("dashboard", help="Launch the Streamlit dashboard")
    dashboard_parser.add_argument(
        "--port",
        type=int,
        default=8501,
        help="Port to run dashboard on (default: 8501)"
    )
    
    # ===== DEMO COMMAND =====
    demo_parser = subparsers.add_parser("demo", help="Generate sample data and show results")
    demo_parser.add_argument(
        "--days",
        type=int,
        default=365,
        help="Number of days to simulate (default: 365)"
    )
    demo_parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)"
    )
    demo_parser.add_argument(
        "--output-dir",
        default="./results",
        help="Output directory for results (default: ./results)"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = getattr(args, 'log_level', 'INFO')
    setup_logging(log_level)
    logger = logging.getLogger(__name__)
    
    # Route to appropriate command
    if args.command == "run":
        return run_simulation(args, logger)
    elif args.command == "dashboard":
        return launch_dashboard(args, logger)
    elif args.command == "demo":
        return run_demo(args, logger)
    else:
        # Default: show help
        parser.print_help()
        print("\n💡 Quick Start:")
        print("  python main.py demo              # See sample results (no setup needed)")
        print("  python main.py dashboard         # Launch interactive dashboard")
        print("  python main.py run -b models/baseline.idf  # Run actual simulation")
        return 0


def run_simulation(args, logger):
    """Run closed-loop simulation with EnergyPlus and LLM."""
    
    logger.info("=" * 70)
    logger.info("ECO-LOOP BUILDING AGENTS - Autonomous Energy Optimization")
    logger.info("=" * 70)
    logger.info(f"Building Model: {args.building}")
    logger.info(f"Simulation Duration: {args.duration} days")
    logger.info(f"LLM Endpoint: {args.llm_endpoint}")
    logger.info(f"LLM Model: {args.llm_model}")
    logger.info(f"Control Interval: {args.control_interval} seconds")
    logger.info("=" * 70)
    
    # Validate building file
    building_path = Path(args.building)
    if not building_path.exists():
        logger.error(f"Building model not found: {building_path}")
        return 1
    
    try:
        # Initialize controller
        controller = ClosedLoopController(
            idf_path=str(building_path),
            llm_endpoint=args.llm_endpoint,
            control_interval=args.control_interval,
            simulation_duration=args.duration
        )
        
        # Run closed-loop optimization
        success = controller.start()
        
        if success:
            # Generate performance report
            report = controller.get_performance_report()
            
            logger.info("\n" + "=" * 70)
            logger.info("SIMULATION COMPLETED SUCCESSFULLY")
            logger.info("=" * 70)
            
            # Display summary
            summary = format_performance_summary(report)
            logger.info("\n" + summary)
            
            # Save results
            output_path = Path(args.output_dir)
            output_path.mkdir(exist_ok=True)
            
            import json
            report_file = output_path / "performance_report.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"\nResults saved to: {report_file}")
            logger.info(f"\n💡 View results: python main.py dashboard")
            
            return 0
        else:
            logger.error("Simulation failed")
            return 1
    
    except KeyboardInterrupt:
        logger.info("\nSimulation interrupted by user")
        return 130
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


def run_demo(args, logger):
    """Run demo mode: generate sample data without EnergyPlus."""
    
    logger.info("=" * 70)
    logger.info("ECO-LOOP DEMO MODE - Generating Sample Simulation Data")
    logger.info("=" * 70)
    logger.info(f"Duration: {args.days} days")
    logger.info("=" * 70)
    
    try:
        # Generate realistic sample data
        report = generate_simulation_results(
            duration_days=args.days,
            output_dir=args.output_dir
        )
        
        logger.info("\n" + "=" * 70)
        logger.info("DEMO DATA GENERATED SUCCESSFULLY")
        logger.info("=" * 70)
        logger.info("\n📊 Results Summary:")
        logger.info(f"  Energy Saved: {report['energy_saved_kwh']:,.0f} kWh ({report['percent_savings']:.1f}%)")
        logger.info(f"  Cost Savings: ${report['cost_savings']:,.2f}")
        logger.info(f"  Comfort: PMV {report['avg_pmv_baseline']:.2f} → {report['avg_pmv_optimized']:.2f}")
        logger.info("\n💡 View dashboard: python main.py dashboard")
        
        return 0
    
    except Exception as e:
        logger.error(f"Error generating demo data: {e}", exc_info=True)
        return 1


def launch_dashboard(args, logger):
    """Launch the Streamlit dashboard."""
    
    logger.info("=" * 70)
    logger.info("Launching Eco-Loop Dashboard")
    logger.info("=" * 70)
    
    # First, check if demo data exists, if not generate it
    if not Path("results/performance_report.json").exists():
        logger.info("Generating demo data first...")
        generate_simulation_results(duration_days=365, output_dir="results")
    
    # Launch Streamlit
    dashboard_path = Path(__file__).parent / "dashboard" / "app.py"
    
    logger.info(f"Starting dashboard on http://localhost:{args.port}")
    logger.info("Press Ctrl+C to stop the server")
    
    try:
        # Use python -m streamlit instead of calling streamlit directly
        # This works even if streamlit is not in PATH
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            str(dashboard_path),
            "--server.port", str(args.port),
            "--logger.level=error"
        ])
        return 0
    except Exception as e:
        logger.error(f"Failed to start dashboard: {e}")
        logger.error("Make sure Streamlit is installed: pip install streamlit")
        return 1
    except KeyboardInterrupt:
        logger.info("\nDashboard stopped by user")
        return 0


if __name__ == "__main__":
    sys.exit(main())
