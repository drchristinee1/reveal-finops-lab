#!/usr/bin/env python3
"""
FinOps Unified CLI

A command-line interface for AWS FinOps tools including cost anomaly detection,
idle resource analysis, rightsizing recommendations, and health scans.
"""

import argparse
import subprocess
import sys
from typing import List


class FinOpsCLI:
    """Unified CLI for FinOps tools."""

    def __init__(self):
        """Initialize the CLI."""
        self.script_mapping = {
            'anomalies': 'variance_to_action/cost_anomaly.py',
            'idle': 'optimization_actions/idle_detector.py',
            'rightsizing': 'optimization_actions/rightsizing_detector.py',
            'health': 'variance_to_action/finops_health_scan.py',
            'drivers': {
                'lambda': 'architecture_cost_advisor/driver_detector.py',
                'dynamodb': 'architecture_cost_advisor/dynamodb_driver_detector.py',
                'rds': 'architecture_cost_advisor/rds_driver_detector.py',
                'ec2': 'architecture_cost_advisor/ec2_driver_detector.py',
                's3': 'architecture_cost_advisor/s3_driver_detector.py',
                'network': 'architecture_cost_advisor/network_driver_detector.py',
                'all': 'variance_to_action/unified_drivers_detector.py'
            }
        }

    def run_script(self, script_name: str, args: List[str]) -> int:
        try:
            cmd = [sys.executable, script_name] + args
            result = subprocess.run(cmd, check=False)
            return result.returncode
        except Exception as e:
            print(f"Error running script '{script_name}': {e}")
            return 1

    def main(self):
        parser = argparse.ArgumentParser(
            prog='finops',
            description='AWS FinOps CLI'
        )

        parser.add_argument(
            'command',
            help='Command to run (anomalies, idle, rightsizing, health)'
        )

        args, unknown = parser.parse_known_args()

        if args.command in self.script_mapping:
            script = self.script_mapping[args.command]
            self.run_script(script, unknown)
        else:
            print(f"Unknown command: {args.command}")


if __name__ == "__main__":
    cli = FinOpsCLI()
    cli.main()
