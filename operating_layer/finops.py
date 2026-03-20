#!/usr/bin/env python3
"""
FinOps Unified CLI

A command-line interface for AWS FinOps tools including cost anomaly detection,
idle resource analysis, rightsizing recommendations, and comprehensive health scans.
"""

import argparse
import subprocess
import sys
from typing import List, Optional


class FinOpsCLI:
    """Unified CLI for FinOps tools."""
    
    def __init__(self):
        """Initialize the CLI."""
        self.script_mapping = {
            'anomalies': 'cost_anomaly.py',
            'idle': 'idle_detector.py',
            'rightsizing': 'rightsizing_detector.py',
            'health': 'finops_health_scan.py',
            'drivers': {
                'lambda': 'driver_detector.py',
                'dynamodb': 'dynamodb_driver_detector.py',
                'rds': 'rds_driver_detector.py',
                'ec2': 'ec2_driver_detector.py',
                's3': 's3_driver_detector.py',
                'network': 'network_driver_detector.py',
                'all': 'unified_drivers_detector.py'
            }
        }
    
    def run_script(self, script_name: str, args: List[str]) -> int:
        """
        Run a FinOps script with the provided arguments.
        
        Args:
            script_name: Name of the script to run
            args: Command line arguments to pass to the script
            
        Returns:
            Exit code from the script
        """
        try:
            # Build the command
            cmd = [sys.executable, script_name] + args
            
            # Run the script
            result = subprocess.run(cmd, check=False)
            
            return result.returncode
            
        except FileNotFoundError:
            print(f"Error: Script '{script_name}' not found")
            return 1
        except Exception as e:
            print(f"Error running script '{script_name}': {e}")
            return 1
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create the main argument parser with subcommands."""
        parser = argparse.ArgumentParser(
            prog='finops',
            description='AWS FinOps tools for cost optimization and resource management',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  finops anomalies --lookback-days 30 --threshold 25
  finops idle --region us-west-2 --output idle_report.json
  finops rightsizing --demo --profile production
  finops health --region eu-west-1 --output health_report.json
  finops drivers lambda --region us-west-2 --output driver_report.json
  finops drivers dynamodb --region us-west-2 --output dynamodb_report.json
  finops drivers rds --region us-west-2 --output rds_report.json
  finops drivers ec2 --region us-west-2 --output ec2_report.json
  finops drivers s3 --region us-west-2 --output s3_report.json
  finops drivers network --region us-west-2 --output network_report.json
  
For more help on a specific command:
  finops <command> --help
  finops drivers <service> --help
            """
        )
        
        # Add global arguments
        parser.add_argument(
            '--version',
            action='version',
            version='FinOps CLI 1.0.0'
        )
        
        # Create subparsers
        subparsers = parser.add_subparsers(
            dest='command',
            help='Available commands',
            metavar='COMMAND'
        )
        
        # Anomalies subcommand
        self._add_anomalies_parser(subparsers)
        
        # Idle subcommand
        self._add_idle_parser(subparsers)
        
        # Rightsizing subcommand
        self._add_rightsizing_parser(subparsers)
        
        # Health subcommand
        self._add_health_parser(subparsers)
        
        # Drivers subcommand
        self._add_drivers_parser(subparsers)
        
        return parser
    
    def _add_anomalies_parser(self, subparsers):
        """Add anomalies subcommand parser."""
        parser = subparsers.add_parser(
            'anomalies',
            help='Detect cost anomalies in AWS spending',
            description='Detect cost anomalies using AWS Cost Explorer data',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  finops anomalies
  finops anomalies --lookback-days 14 --threshold 50
  finops anomalies --profile my-aws-profile
            """
        )
        
        parser.add_argument(
            '--lookback-days',
            type=int,
            default=30,
            help='Number of days to look back for cost analysis (default: 30)'
        )
        
        parser.add_argument(
            '--threshold',
            type=float,
            default=25.0,
            help='Anomaly threshold percentage (default: 25.0)'
        )
        
        parser.add_argument(
            '--profile',
            type=str,
            help='AWS profile name to use for authentication'
        )
    
    def _add_drivers_parser(self, subparsers):
        """Add drivers subcommand parser with nested service subcommands."""
        parser = subparsers.add_parser(
            'drivers',
            help='Analyze workload demand drivers across services',
            description='Analyze workload demand drivers that influence cloud costs across different AWS services',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  finops drivers lambda --region us-west-2 --output driver_report.json
  finops drivers dynamodb --region us-west-2 --output dynamodb_report.json
  finops drivers lambda --demo --profile production
  
For more help on a specific service:
  finops drivers <service> --help
            """
        )
        
        # Create subparsers for services
        service_subparsers = parser.add_subparsers(
            dest='service',
            help='Available services',
            metavar='SERVICE'
        )
        
        # Lambda subcommand
        self._add_drivers_lambda_parser(service_subparsers)
        
        # DynamoDB subcommand
        self._add_drivers_dynamodb_parser(service_subparsers)
        
        # RDS subcommand
        self._add_drivers_rds_parser(service_subparsers)
        
        # EC2 subcommand
        self._add_drivers_ec2_parser(service_subparsers)
        
        # S3 subcommand
        self._add_drivers_s3_parser(service_subparsers)
        
        # Network subcommand
        self._add_drivers_network_parser(service_subparsers)
        
        # All subcommand
        self._add_drivers_all_parser(service_subparsers)
        
        return parser
    
    def _add_drivers_lambda_parser(self, subparsers):
        """Add drivers lambda subcommand parser."""
        parser = subparsers.add_parser(
            'lambda',
            help='Analyze Lambda workload demand drivers',
            description='Analyze Lambda functions to identify workload demand drivers that influence cloud costs',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  finops drivers lambda
  finops drivers lambda --region us-west-2 --output driver_report.json
  finops drivers lambda --demo --profile production
            """
        )
        
        parser.add_argument(
            '--region',
            type=str,
            default='us-east-1',
            help='AWS region to scan (default: us-east-1)'
        )
        
        parser.add_argument(
            '--output',
            type=str,
            help='Output JSON file path'
        )
        
        parser.add_argument(
            '--profile',
            type=str,
            help='AWS profile name to use for authentication'
        )
        
        parser.add_argument(
            '--demo',
            action='store_true',
            help='Run in demo mode with sample data'
        )
    
    def _add_drivers_dynamodb_parser(self, subparsers):
        """Add drivers dynamodb subcommand parser."""
        parser = subparsers.add_parser(
            'dynamodb',
            help='Analyze DynamoDB workload demand drivers',
            description='Analyze DynamoDB tables to identify workload demand drivers that influence cloud costs',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  finops drivers dynamodb
  finops drivers dynamodb --region us-west-2 --output dynamodb_report.json
  finops drivers dynamodb --demo --profile production
            """
        )
        
        parser.add_argument(
            '--region',
            type=str,
            default='us-east-1',
            help='AWS region to scan (default: us-east-1)'
        )
        
        parser.add_argument(
            '--output',
            type=str,
            help='Output JSON file path'
        )
        
        parser.add_argument(
            '--profile',
            type=str,
            help='AWS profile name to use for authentication'
        )
        
        parser.add_argument(
            '--demo',
            action='store_true',
            help='Run in demo mode with sample data'
        )
    
    def _add_drivers_rds_parser(self, subparsers):
        """Add drivers rds subcommand parser."""
        parser = subparsers.add_parser(
            'rds',
            help='Analyze RDS workload demand drivers',
            description='Analyze RDS instances to identify workload demand drivers that influence cloud costs',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  finops drivers rds
  finops drivers rds --region us-west-2 --output rds_report.json
  finops drivers rds --demo --profile production
            """
        )
        
        parser.add_argument(
            '--region',
            type=str,
            default='us-east-1',
            help='AWS region to scan (default: us-east-1)'
        )
        
        parser.add_argument(
            '--output',
            type=str,
            help='Output JSON file path'
        )
        
        parser.add_argument(
            '--profile',
            type=str,
            help='AWS profile name to use for authentication'
        )
        
        parser.add_argument(
            '--demo',
            action='store_true',
            help='Run in demo mode with sample data'
        )
    
    def _add_drivers_ec2_parser(self, subparsers):
        """Add drivers ec2 subcommand parser."""
        parser = subparsers.add_parser(
            'ec2',
            help='Analyze EC2 compute demand drivers',
            description='Analyze EC2 instances to identify compute demand drivers that influence cloud costs',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  finops drivers ec2
  finops drivers ec2 --region us-west-2 --output ec2_report.json
  finops drivers ec2 --demo --profile production
            """
        )
        
        parser.add_argument(
            '--region',
            type=str,
            default='us-east-1',
            help='AWS region to scan (default: us-east-1)'
        )
        
        parser.add_argument(
            '--output',
            type=str,
            help='Output JSON file path'
        )
        
        parser.add_argument(
            '--profile',
            type=str,
            help='AWS profile name to use for authentication'
        )
        
        parser.add_argument(
            '--demo',
            action='store_true',
            help='Run in demo mode with sample data'
        )
    
    def _add_drivers_s3_parser(self, subparsers):
        """Add drivers s3 subcommand parser."""
        parser = subparsers.add_parser(
            's3',
            help='Analyze S3 storage demand drivers',
            description='Analyze S3 buckets to identify storage demand drivers that influence cloud costs',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  finops drivers s3
  finops drivers s3 --region us-west-2 --output s3_report.json
  finops drivers s3 --demo --profile production
            """
        )
        
        parser.add_argument(
            '--region',
            type=str,
            default='us-east-1',
            help='AWS region to scan (default: us-east-1)'
        )
        
        parser.add_argument(
            '--output',
            type=str,
            help='Output JSON file path'
        )
        
        parser.add_argument(
            '--profile',
            type=str,
            help='AWS profile name to use for authentication'
        )
        
        parser.add_argument(
            '--demo',
            action='store_true',
            help='Run in demo mode with sample data'
        )
    
    def _add_drivers_network_parser(self, subparsers):
        """Add drivers network subcommand parser."""
        parser = subparsers.add_parser(
            'network',
            help='Analyze network traffic demand drivers',
            description='Analyze AWS networking costs to identify traffic-related demand drivers that influence cloud costs',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  finops drivers network
  finops drivers network --region us-west-2 --output network_report.json
  finops drivers network --demo --profile production
            """
        )
        
        parser.add_argument(
            '--region',
            type=str,
            default='us-east-1',
            help='AWS region to scan (default: us-east-1)'
        )
        
        parser.add_argument(
            '--output',
            type=str,
            help='Output JSON file path'
        )
        
        parser.add_argument(
            '--profile',
            type=str,
            help='AWS profile name to use for authentication'
        )
        
        parser.add_argument(
            '--demo',
            action='store_true',
            help='Run in demo mode with sample data'
        )
    
    def _add_drivers_all_parser(self, subparsers):
        """Add drivers all subcommand parser."""
        parser = subparsers.add_parser(
            'all',
            help='Run unified analysis of all demand drivers',
            description='Run unified analysis of all AWS service demand drivers to provide comprehensive cost insights',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  finops drivers all
  finops drivers all --region us-west-2 --output unified_drivers_report.json
  finops drivers all --demo --profile production
            """
        )
        
        parser.add_argument(
            '--region',
            type=str,
            default='us-east-1',
            help='AWS region to scan (default: us-east-1)'
        )
        
        parser.add_argument(
            '--output',
            type=str,
            help='Output JSON file path'
        )
        
        parser.add_argument(
            '--profile',
            type=str,
            help='AWS profile name to use for authentication'
        )
        
        parser.add_argument(
            '--demo',
            action='store_true',
            help='Run in demo mode with sample data'
        )
    
    def _add_idle_parser(self, subparsers):
        """Add idle subcommand parser."""
        parser = subparsers.add_parser(
            'idle',
            help='Detect idle AWS resources',
            description='Detect unattached EBS volumes and unused Elastic IP addresses',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  finops idle
  finops idle --region us-west-2 --output idle_report.json
  finops idle --demo --profile production
            """
        )
        
        parser.add_argument(
            '--region',
            type=str,
            default='us-east-1',
            help='AWS region to scan (default: us-east-1)'
        )
        
        parser.add_argument(
            '--output',
            type=str,
            help='Output JSON file path'
        )
        
        parser.add_argument(
            '--profile',
            type=str,
            help='AWS profile name to use for authentication'
        )
        
        parser.add_argument(
            '--demo',
            action='store_true',
            help='Run in demo mode with sample data'
        )
    
    def _add_rightsizing_parser(self, subparsers):
        """Add rightsizing subcommand parser."""
        parser = subparsers.add_parser(
            'rightsizing',
            help='Detect EC2 rightsizing opportunities',
            description='Analyze EC2 instances for rightsizing based on CPU utilization',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  finops rightsizing
  finops rightsizing --region us-west-2 --output rightsizing_report.json
  finops rightsizing --demo --profile production
            """
        )
        
        parser.add_argument(
            '--region',
            type=str,
            default='us-east-1',
            help='AWS region to scan (default: us-east-1)'
        )
        
        parser.add_argument(
            '--output',
            type=str,
            help='Output JSON file path'
        )
        
        parser.add_argument(
            '--profile',
            type=str,
            help='AWS profile name to use for authentication'
        )
        
        parser.add_argument(
            '--demo',
            action='store_true',
            help='Run in demo mode with sample data'
        )
    
    def _add_health_parser(self, subparsers):
        """Add health subcommand parser."""
        parser = subparsers.add_parser(
            'health',
            help='Comprehensive FinOps health scan',
            description='Run comprehensive FinOps health assessment combining all analyses',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  finops health
  finops health --region us-west-2 --output health_report.json
  finops health --demo --profile production
  finops health --lookback-days 60 --threshold 15
            """
        )
        
        parser.add_argument(
            '--region',
            type=str,
            default='us-east-1',
            help='AWS region to scan (default: us-east-1)'
        )
        
        parser.add_argument(
            '--output',
            type=str,
            default='finops_health_report.json',
            help='Output JSON file path (default: finops_health_report.json)'
        )
        
        parser.add_argument(
            '--profile',
            type=str,
            help='AWS profile name to use for authentication'
        )
        
        parser.add_argument(
            '--demo',
            action='store_true',
            help='Run in demo mode with sample data'
        )
        
        parser.add_argument(
            '--lookback-days',
            type=int,
            default=30,
            help='Days to look back for cost anomaly analysis (default: 30)'
        )
        
        parser.add_argument(
            '--threshold',
            type=float,
            default=25.0,
            help='Cost anomaly threshold percentage (default: 25.0)'
        )
    
    def build_script_args(self, command: str, args: argparse.Namespace) -> List[str]:
        """
        Build arguments list for the target script based on parsed arguments.
        
        Args:
            command: The subcommand being executed
            args: Parsed arguments from argparse
            
        Returns:
            List of arguments to pass to the script
        """
        script_args = []
        
        if command == 'anomalies':
            if args.lookback_days != 30:
                script_args.extend(['--lookback-days', str(args.lookback_days)])
            if args.threshold != 25.0:
                script_args.extend(['--threshold', str(args.threshold)])
            if args.profile:
                script_args.extend(['--profile', args.profile])
        
        elif command in ['idle', 'rightsizing']:
            if args.region != 'us-east-1':
                script_args.extend(['--region', args.region])
            if args.output:
                script_args.extend(['--output', args.output])
            if args.profile:
                script_args.extend(['--profile', args.profile])
            if args.demo:
                script_args.append('--demo')
        
        elif command == 'drivers':
            if args.service == 'lambda':
                if args.region != 'us-east-1':
                    script_args.extend(['--region', args.region])
                if args.output:
                    script_args.extend(['--output', args.output])
                if args.profile:
                    script_args.extend(['--profile', args.profile])
                if args.demo:
                    script_args.append('--demo')
            elif args.service == 'dynamodb':
                if args.region != 'us-east-1':
                    script_args.extend(['--region', args.region])
                if args.output:
                    script_args.extend(['--output', args.output])
                if args.profile:
                    script_args.extend(['--profile', args.profile])
                if args.demo:
                    script_args.append('--demo')
            elif args.service == 'rds':
                if args.region != 'us-east-1':
                    script_args.extend(['--region', args.region])
                if args.output:
                    script_args.extend(['--output', args.output])
                if args.profile:
                    script_args.extend(['--profile', args.profile])
                if args.demo:
                    script_args.append('--demo')
            elif args.service == 'ec2':
                if args.region != 'us-east-1':
                    script_args.extend(['--region', args.region])
                if args.output:
                    script_args.extend(['--output', args.output])
                if args.profile:
                    script_args.extend(['--profile', args.profile])
                if args.demo:
                    script_args.append('--demo')
            elif args.service == 's3':
                if args.region != 'us-east-1':
                    script_args.extend(['--region', args.region])
                if args.output:
                    script_args.extend(['--output', args.output])
                if args.profile:
                    script_args.extend(['--profile', args.profile])
                if args.demo:
                    script_args.append('--demo')
            elif args.service == 'network':
                if args.region != 'us-east-1':
                    script_args.extend(['--region', args.region])
                if args.output:
                    script_args.extend(['--output', args.output])
                if args.profile:
                    script_args.extend(['--profile', args.profile])
                if args.demo:
                    script_args.append('--demo')
            elif args.service == 'all':
                if args.region != 'us-east-1':
                    script_args.extend(['--region', args.region])
                if args.output:
                    script_args.extend(['--output', args.output])
                if args.profile:
                    script_args.extend(['--profile', args.profile])
                if args.demo:
                    script_args.append('--demo')
        
        elif command == 'health':
            if args.region != 'us-east-1':
                script_args.extend(['--region', args.region])
            if args.output != 'finops_health_report.json':
                script_args.extend(['--output', args.output])
            if args.profile:
                script_args.extend(['--profile', args.profile])
            if args.demo:
                script_args.append('--demo')
            if args.lookback_days != 30:
                script_args.extend(['--lookback-days', str(args.lookback_days)])
            if args.threshold != 25.0:
                script_args.extend(['--threshold', str(args.threshold)])
        
        return script_args
    
    def run(self, args: Optional[List[str]] = None) -> int:
        """
        Run the CLI with the provided arguments.
        
        Args:
            args: Command line arguments (defaults to sys.argv[1:])
            
        Returns:
            Exit code
        """
        parser = self.create_parser()
        
        # Parse arguments
        parsed_args = parser.parse_args(args)
        
        # Check if a command was provided
        if not parsed_args.command:
            parser.print_help()
            return 1
        
        # Handle drivers command specially
        if parsed_args.command == 'drivers':
            if not parsed_args.service:
                parser = self.create_parser()
                subparser = parser._subparsers._group_actions[0]
                drivers_parser = subparser.choices['drivers']
                drivers_parser.print_help()
                return 1
            
            # Get the script name for the service
            script_name = self.script_mapping['drivers'].get(parsed_args.service)
            if not script_name:
                print(f"Error: Unknown drivers service '{parsed_args.service}'")
                return 1
            
            # Build arguments for the script
            script_args = self.build_script_args(parsed_args.command, parsed_args)
            
            # Run the script
            print(f"Running FinOps {parsed_args.command} {parsed_args.service} analysis...")
            exit_code = self.run_script(script_name, script_args)
            
            # Handle script failure
            if exit_code != 0:
                print(f"\n❌ {parsed_args.service.title()} driver analysis failed with exit code {exit_code}")
                print(f"   Run 'finops drivers {parsed_args.service} --help' for usage information")
                return exit_code
            
            print(f"\n✅ {parsed_args.service.title()} driver analysis completed successfully")
            return 0
        
        # Get the script name for the command
        script_name = self.script_mapping.get(parsed_args.command)
        if not script_name:
            print(f"Error: Unknown command '{parsed_args.command}'")
            return 1
        
        # Build arguments for the script
        script_args = self.build_script_args(parsed_args.command, parsed_args)
        
        # Run the script
        print(f"Running FinOps {parsed_args.command} analysis...")
        exit_code = self.run_script(script_name, script_args)
        
        # Handle script failure
        if exit_code != 0:
            print(f"\n❌ {parsed_args.command.title()} analysis failed with exit code {exit_code}")
            print(f"   Run 'finops {parsed_args.command} --help' for usage information")
            return exit_code
        
        print(f"\n✅ {parsed_args.command.title()} analysis completed successfully")
        return 0


def main():
    """Main entry point for the CLI."""
    cli = FinOpsCLI()
    exit_code = cli.run()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
