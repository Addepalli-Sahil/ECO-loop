"""
Eco-Loop Building Agents - Main Entry Point

Run the autonomous closed-loop building optimization system.

Usage:
    python main.py --building path/to/model.idf --duration 365
    python main.py --building models/baseline.idf --duration 180 --llm-endpoint http://localhost:11434
"""

import argparse
import logging
import sys
from pathlib import Path

from src.eco_loop.controller import ClosedLoopController
from src.eco_loop.utils import setup_logging, format_performance_summary


def main():
    """Main entry point for Eco-Loop system."""
    
    parser = argparse.ArgumentParser(
        description="Eco-Loop Building Agents - Autonomous AI-driven building optimization"
    )
    
    parser.add_argument(
        "--building",
        "-b",
        required=True,
        help="Path to EnergyPlus building model (.idf file)"
    )
    
    parser.add_argument(
        "--duration",
        "-d",
        type=int,
        default=365,
        help="Simulation duration in days (default: 365)"
    )
    
    parser.add_argument(
        "--llm-endpoint",
        default="http://localhost:11434",
        help="LLM server endpoint (default: http://localhost:11434 for Ollama)"
    )
    
    parser.add_argument(
        "--llm-model",
        default="llama2",
        help="LLM model name (default: llama2)"
    )
    
    parser.add_argument(
        "--control-interval",
        type=int,
        default=300,
        help="Control update interval in seconds (default: 300 = 5 minutes)"
    )
    
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)"
    )
    
    parser.add_argument(
        "--output-dir",
        default="./results",
        help="Output directory for results (default: ./results)"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    # Validate building file
    building_path = Path(args.building)
    if not building_path.exists():
        logger.error(f"Building model not found: {building_path}")
        sys.exit(1)
    
    logger.info("=" * 70)
    logger.info("ECO-LOOP BUILDING AGENTS - Autonomous Energy Optimization")
    logger.info("=" * 70)
    logger.info(f"Building Model: {building_path}")
    logger.info(f"Simulation Duration: {args.duration} days")
    logger.info(f"LLM Endpoint: {args.llm_endpoint}")
    logger.info(f"LLM Model: {args.llm_model}")
    logger.info(f"Control Interval: {args.control_interval} seconds")
    logger.info("=" * 70)
    
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


if __name__ == "__main__":
    sys.exit(main())
