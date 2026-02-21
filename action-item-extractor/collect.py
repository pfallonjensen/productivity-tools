#!/usr/bin/env python3
"""
Step 1 of two-step extraction pipeline: collect from all sources + noise filter.

Usage:
    python3 collect.py [output_dir] [--persona persona.yaml] [--config config.yaml]

Writes candidates JSON to output_dir (default: /tmp/action-item-candidates/).
If content exceeds token budget, splits into multiple batch files.

The candidates JSON is then consumed by Step 2 (Claude Code triage skill).
"""
import argparse
import logging
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from engine.extractor import Extractor


def main():
    parser = argparse.ArgumentParser(description='Collect and filter action item candidates')
    parser.add_argument(
        'output_dir',
        nargs='?',
        default='/tmp/action-item-candidates',
        help='Directory for candidates JSON output (default: /tmp/action-item-candidates)'
    )
    parser.add_argument('--persona', default='persona.yaml', help='Path to persona.yaml')
    parser.add_argument('--config', default='config.yaml', help='Path to config.yaml')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')

    args = parser.parse_args()

    # Setup logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
        datefmt='%H:%M:%S'
    )
    logger = logging.getLogger('collect')

    # Resolve config paths
    persona_path = str(Path(args.persona).resolve())
    config_path = str(Path(args.config).resolve())

    logger.info(f"Persona: {persona_path}")
    logger.info(f"Config: {config_path}")
    logger.info(f"Output: {args.output_dir}")

    try:
        extractor = Extractor(persona_path=persona_path, config_path=config_path)
        result = extractor.collect_and_filter(output_dir=args.output_dir)

        logger.info(
            f"Collected {result['raw_items']} raw -> "
            f"{result.get('after_chunking', result['raw_items'])} chunked -> "
            f"{result['after_noise_filter']} candidates -> "
            f"{result['batch_files']} batch(es)"
        )

        if result.get('output_files'):
            for f in result['output_files']:
                logger.info(f"  -> {f}")

        # Print summary to stdout for shell script consumption
        print(f"Collected {result['raw_items']} raw -> {result['after_noise_filter']} candidates -> {args.output_dir}")

    except FileNotFoundError as e:
        logger.error(f"Config file not found: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Collection failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
