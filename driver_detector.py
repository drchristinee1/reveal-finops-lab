#!/usr/bin/env python3
"""
AWS Lambda Driver Detector

This script analyzes Lambda functions to identify workload demand drivers
that influence cloud costs through usage patterns and metrics.
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import boto3
from botocore.exceptions import ClientError, NoCredentialsError, EndpointConnectionError


class LambdaDriverDetector:
    """Detects Lambda workload demand drivers based on usage patterns."""
    
    # Simplified Lambda pricing (actual prices vary by region)
    # Pricing: $0.20 per 1M requests + $0.0000166667 per GB-second
    LAMBDA_PRICING = {
        'request_cost_per_million': 0.20,
        'compute_cost_per_gb_second': 0.0000166667
    }
    
    def __init__(self, region: str = 'us-east-1', profile_name: Optional[str] = None, demo_mode: bool = False):
        """Initialize the Lambda driver detector."""
        self.region = region
        self.demo_mode = demo_mode
        self.demo_data = self._generate_demo_data()
        
        if not demo_mode:
            try:
                session = boto3.Session(profile_name=profile_name)
                self.lambda_client = session.client('lambda', region_name=region)
                self.cloudwatch_client = session.client('cloudwatch', region_name=region)
            except NoCredentialsError:
                print("Warning: AWS credentials not found. Enabling demo mode.")
                self.demo_mode = True
            except Exception as e:
                print(f"Error initializing AWS session: {e}")
                sys.exit(1)
    
    def _generate_demo_data(self) -> Dict:
        """Generate realistic sample Lambda data for demo mode."""
        return {
            'functions': [
                {
                    'FunctionName': 'order-processing',
                    'FunctionArn': 'arn:aws:lambda:us-east-1:123456789012:function:order-processing',
                    'Runtime': 'python3.9',
                    'Handler': 'lambda_function.lambda_handler',
                    'CodeSize': 5024567,
                    'Description': 'Process customer orders',
                    'Timeout': 300,
                    'MemorySize': 512,
                    'LastModified': '2024-03-01T10:30:00.000+0000',
                    'State': 'Active',
                    'StateReason': None,
                    'StateReasonCode': None,
                    'PackageType': 'Zip',
                    'Architectures': ['x86_64'],
                    'Tags': [
                        {'Key': 'Environment', 'Value': 'production'},
                        {'Key': 'Team', 'Value': 'backend'},
                        {'Key': 'Name', 'Value': 'order-processing'}
                    ],
                    'Invocations': 1200000,
                    'AverageDuration': 140,  # milliseconds
                    'Errors': 2400,  # 0.2% error rate
                    'Throttles': 1200,  # 0.1% throttle rate
                    'Driver': 'API requests'
                },
                {
                    'FunctionName': 'image-thumbnailer',
                    'FunctionArn': 'arn:aws:lambda:us-east-1:123456789012:function:image-thumbnailer',
                    'Runtime': 'python3.9',
                    'Handler': 'lambda_function.generate_thumbnail',
                    'CodeSize': 8456234,
                    'Description': 'Generate image thumbnails',
                    'Timeout': 900,
                    'MemorySize': 1024,
                    'LastModified': '2024-02-15T14:20:00.000+0000',
                    'State': 'Active',
                    'StateReason': None,
                    'StateReasonCode': None,
                    'PackageType': 'Zip',
                    'Architectures': ['x86_64'],
                    'Tags': [
                        {'Key': 'Environment', 'Value': 'production'},
                        {'Key': 'Team', 'Value': 'media'},
                        {'Key': 'Name', 'Value': 'image-thumbnailer'}
                    ],
                    'Invocations': 450000,
                    'AverageDuration': 850,  # milliseconds
                    'Errors': 1350,  # 0.3% error rate
                    'Throttles': 2250,  # 0.5% throttle rate
                    'Driver': 'User uploads'
                },
                {
                    'FunctionName': 'data-processor',
                    'FunctionArn': 'arn:aws:lambda:us-east-1:123456789012:function:data-processor',
                    'Runtime': 'python3.9',
                    'Handler': 'lambda_function.process_data',
                    'CodeSize': 3456789,
                    'Description': 'Process batch data jobs',
                    'Timeout': 600,
                    'MemorySize': 256,
                    'LastModified': '2024-03-10T08:45:00.000+0000',
                    'State': 'Active',
                    'StateReason': None,
                    'StateReasonCode': None,
                    'PackageType': 'Zip',
                    'Architectures': ['x86_64'],
                    'Tags': [
                        {'Key': 'Environment', 'Value': 'production'},
                        {'Key': 'Team', 'Value': 'analytics'},
                        {'Key': 'Name', 'Value': 'data-processor'}
                    ],
                    'Invocations': 75000,
                    'AverageDuration': 2200,  # milliseconds
                    'Errors': 750,  # 1.0% error rate
                    'Throttles': 0,  # No throttling
                    'Driver': 'Scheduled jobs'
                },
                {
                    'FunctionName': 'auth-validator',
                    'FunctionArn': 'arn:aws:lambda:us-east-1:123456789012:function:auth-validator',
                    'Runtime': 'nodejs18.x',
                    'Handler': 'index.validateToken',
                    'CodeSize': 1234567,
                    'Description': 'Validate authentication tokens',
                    'Timeout': 30,
                    'MemorySize': 128,
                    'LastModified': '2024-01-20T12:15:00.000+0000',
                    'State': 'Active',
                    'StateReason': None,
                    'StateReasonCode': None,
                    'PackageType': 'Zip',
                    'Architectures': ['x86_64'],
                    'Tags': [
                        {'Key': 'Environment', 'Value': 'production'},
                        {'Key': 'Team', 'Value': 'security'},
                        {'Key': 'Name', 'Value': 'auth-validator'}
                    ],
                    'Invocations': 3500000,
                    'AverageDuration': 45,  # milliseconds
                    'Errors': 3500,  # 0.1% error rate
                    'Throttles': 35000,  # 1.0% throttle rate
                    'Driver': 'User authentication'
                }
            ]
        }
    
    def get_lambda_functions(self) -> List[Dict]:
        """
        Get all Lambda functions in the region.
        
        Returns:
            List of Lambda function information
        """
        if self.demo_mode:
            return self.demo_data['functions']
        
        try:
            response = self.lambda_client.list_functions()
            
            functions = []
            for function in response.get('Functions', []):
                # Only include active functions
                if function['State'] == 'Active':
                    functions.append(function)
            
            return functions
        except ClientError as e:
            print(f"Error retrieving Lambda functions: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error retrieving Lambda functions: {e}")
            return []
    
    def get_lambda_metrics(self, function_name: str, days: int = 30) -> Optional[Dict]:
        """
        Get CloudWatch metrics for a Lambda function.
        
        Args:
            function_name: Name of the Lambda function
            days: Number of days to look back for metrics
            
        Returns:
            Dictionary with metrics or None if unavailable
        """
        if self.demo_mode:
            # Return demo metrics
            for function in self.demo_data['functions']:
                if function['FunctionName'] == function_name:
                    return {
                        'Invocations': function['Invocations'],
                        'AverageDuration': function['AverageDuration'],
                        'Errors': function['Errors'],
                        'Throttles': function['Throttles']
                    }
            return None
        
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            metrics = {}
            
            # Get Invocations
            invocations_response = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/Lambda',
                MetricName='Invocations',
                Dimensions=[
                    {
                        'Name': 'FunctionName',
                        'Value': function_name
                    }
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=86400,  # 1 day
                Statistics=['Sum']
            )
            
            # Get Duration
            duration_response = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/Lambda',
                MetricName='Duration',
                Dimensions=[
                    {
                        'Name': 'FunctionName',
                        'Value': function_name
                    }
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=86400,  # 1 day
                Statistics=['Average']
            )
            
            # Get Errors
            errors_response = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/Lambda',
                MetricName='Errors',
                Dimensions=[
                    {
                        'Name': 'FunctionName',
                        'Value': function_name
                    }
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=86400,  # 1 day
                Statistics=['Sum']
            )
            
            # Get Throttles
            throttles_response = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/Lambda',
                MetricName='Throttles',
                Dimensions=[
                    {
                        'Name': 'FunctionName',
                        'Value': function_name
                    }
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=86400,  # 1 day
                Statistics=['Sum']
            )
            
            # Calculate totals and averages
            invocations_data = invocations_response.get('Datapoints', [])
            duration_data = duration_response.get('Datapoints', [])
            errors_data = errors_response.get('Datapoints', [])
            throttles_data = throttles_response.get('Datapoints', [])
            
            if not invocations_data or not duration_data:
                return None
            
            total_invocations = sum(dp['Sum'] for dp in invocations_data)
            total_errors = sum(dp['Sum'] for dp in errors_data) if errors_data else 0
            total_throttles = sum(dp['Sum'] for dp in throttles_data) if throttles_data else 0
            
            # Calculate average duration across all invocations
            total_duration = 0
            total_invocations_for_duration = 0
            for dp in duration_data:
                total_duration += dp['Average'] * dp['Sum'] if 'Sum' in dp else dp['Average']
                total_invocations_for_duration += dp['Sum'] if 'Sum' in dp else 1
            
            avg_duration = total_duration / total_invocations_for_duration if total_invocations_for_duration > 0 else 0
            
            return {
                'Invocations': int(total_invocations),
                'AverageDuration': avg_duration,  # milliseconds
                'Errors': int(total_errors),
                'Throttles': int(total_throttles)
            }
            
        except ClientError as e:
            print(f"Error retrieving metrics for {function_name}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error retrieving metrics for {function_name}: {e}")
            return None
    
    def calculate_lambda_cost(self, function: Dict, metrics: Dict) -> Dict:
        """
        Calculate estimated monthly cost for a Lambda function.
        
        Args:
            function: Lambda function configuration
            metrics: CloudWatch metrics for the function
            
        Returns:
            Cost breakdown dictionary
        """
        memory_size_mb = function['MemorySize']
        avg_duration_ms = metrics['AverageDuration']
        invocations = metrics['Invocations']
        
        # Convert to GB-seconds for pricing
        avg_duration_seconds = avg_duration_ms / 1000
        memory_size_gb = memory_size_mb / 1024
        gb_seconds_per_invocation = avg_duration_seconds * memory_size_gb
        
        # Calculate costs
        request_cost = (invocations / 1000000) * self.LAMBDA_PRICING['request_cost_per_million']
        compute_cost = invocations * gb_seconds_per_invocation * self.LAMBDA_PRICING['compute_cost_per_gb_second']
        total_cost = request_cost + compute_cost
        
        # Calculate cost per invocation
        cost_per_invocation = total_cost / invocations if invocations > 0 else 0
        
        return {
            'request_cost': request_cost,
            'compute_cost': compute_cost,
            'total_cost': total_cost,
            'cost_per_invocation': cost_per_invocation,
            'invocations': invocations,
            'gb_seconds_per_invocation': gb_seconds_per_invocation
        }
    
    def identify_demand_driver(self, function: Dict, metrics: Dict) -> str:
        """
        Identify the likely demand driver based on function characteristics and usage patterns.
        
        Args:
            function: Lambda function configuration
            metrics: CloudWatch metrics for the function
            
        Returns:
            Identified demand driver
        """
        function_name = function['FunctionName'].lower()
        description = function.get('Description', '').lower()
        tags = {tag['Key'].lower(): tag['Value'].lower() for tag in function.get('Tags', [])}
        
        invocations = metrics['Invocations']
        avg_duration = metrics['AverageDuration']
        error_rate = (metrics['Errors'] / invocations * 100) if invocations > 0 else 0
        throttle_rate = (metrics['Throttles'] / invocations * 100) if invocations > 0 else 0
        
        # Analyze patterns to identify drivers
        if invocations > 1000000 and avg_duration < 100:
            return 'API requests'
        elif invocations > 1000000 and avg_duration < 50:
            return 'User authentication'
        elif 'upload' in function_name or 'image' in function_name or 'thumbnail' in function_name:
            return 'User uploads'
        elif 'process' in function_name or 'batch' in function_name or 'job' in function_name:
            return 'Scheduled jobs'
        elif 'stream' in function_name or 'kinesis' in function_name or 'dynamodb' in function_name:
            return 'Event processing'
        elif 'webhook' in function_name or 'notification' in function_name:
            return 'External integrations'
        elif avg_duration > 1000:
            return 'Data processing'
        elif throttle_rate > 1:
            return 'High traffic events'
        elif error_rate > 1:
            return 'Error-prone workloads'
        else:
            return 'General workloads'
    
    def analyze_lambda_drivers(self) -> Dict:
        """
        Analyze all Lambda functions to identify demand drivers.
        
        Returns:
            Analysis results with driver information
        """
        print("Analyzing Lambda functions for demand drivers...")
        
        if self.demo_mode:
            print("Running in DEMO MODE with sample data")
        
        functions = self.get_lambda_functions()
        driver_analysis = []
        
        for function in functions:
            function_name = function['FunctionName']
            
            # Get metrics
            metrics = self.get_lambda_metrics(function_name)
            
            if not metrics:
                print(f"Warning: No metrics available for {function_name}")
                continue
            
            # Calculate costs
            cost_analysis = self.calculate_lambda_cost(function, metrics)
            
            # Identify demand driver
            driver = self.identify_demand_driver(function, metrics)
            
            analysis = {
                'function_name': function_name,
                'function_arn': function['FunctionArn'],
                'runtime': function['Runtime'],
                'memory_size': function['MemorySize'],
                'timeout': function['Timeout'],
                'description': function.get('Description', ''),
                'tags': function.get('Tags', []),
                'metrics': metrics,
                'cost_analysis': cost_analysis,
                'demand_driver': driver,
                'performance_metrics': {
                    'error_rate': (metrics['Errors'] / metrics['Invocations'] * 100) if metrics['Invocations'] > 0 else 0,
                    'throttle_rate': (metrics['Throttles'] / metrics['Invocations'] * 100) if metrics['Invocations'] > 0 else 0
                }
            }
            
            driver_analysis.append(analysis)
        
        # Calculate summary
        total_functions = len(driver_analysis)
        total_invocations = sum(analysis['metrics']['Invocations'] for analysis in driver_analysis)
        total_cost = sum(analysis['cost_analysis']['total_cost'] for analysis in driver_analysis)
        
        # Group by demand drivers
        driver_groups = {}
        for analysis in driver_analysis:
            driver = analysis['demand_driver']
            if driver not in driver_groups:
                driver_groups[driver] = {
                    'functions': [],
                    'total_invocations': 0,
                    'total_cost': 0
                }
            driver_groups[driver]['functions'].append(analysis['function_name'])
            driver_groups[driver]['total_invocations'] += analysis['metrics']['Invocations']
            driver_groups[driver]['total_cost'] += analysis['cost_analysis']['total_cost']
        
        results = {
            'scan_time': datetime.now().isoformat(),
            'region': self.region,
            'demo_mode': self.demo_mode,
            'analysis_period_days': 30,
            'lambda_pricing': self.LAMBDA_PRICING,
            'driver_analysis': driver_analysis,
            'driver_groups': driver_groups,
            'summary': {
                'total_functions_analyzed': total_functions,
                'total_invocations': total_invocations,
                'total_estimated_monthly_cost': total_cost,
                'unique_demand_drivers': len(driver_groups),
                'average_cost_per_function': total_cost / total_functions if total_functions > 0 else 0
            }
        }
        
        return results
    
    def print_summary(self, results: Dict):
        """Print a readable summary of the analysis."""
        summary = results['summary']
        driver_groups = results['driver_groups']
        driver_analysis = results['driver_analysis']
        
        print(f"\nLambda Driver Analysis")
        print(f"====================")
        print(f"Region: {results['region']}")
        print(f"Scan Time: {results['scan_time']}")
        print(f"Analysis Period: {results['analysis_period_days']} days")
        if results['demo_mode']:
            print(f"Mode: DEMO (using sample data)")
        
        print(f"\n--- Summary ---")
        print(f"Total Functions Analyzed: {summary['total_functions_analyzed']}")
        print(f"Total Invocations: {summary['total_invocations']:,}")
        print(f"Estimated Monthly Cost: ${summary['total_estimated_monthly_cost']:.2f}")
        print(f"Unique Demand Drivers: {summary['unique_demand_drivers']}")
        print(f"Average Cost per Function: ${summary['average_cost_per_function']:.2f}")
        
        print(f"\n--- Demand Drivers ---")
        # Sort drivers by total cost (descending)
        sorted_drivers = sorted(driver_groups.items(), key=lambda x: x[1]['total_cost'], reverse=True)
        
        for driver, data in sorted_drivers:
            print(f"\n{driver}:")
            print(f"  Functions: {', '.join(data['functions'])}")
            print(f"  Invocations: {data['total_invocations']:,}")
            print(f"  Cost: ${data['total_cost']:.2f}")
        
        print(f"\n--- Function Details ---")
        # Sort functions by cost (descending)
        sorted_functions = sorted(driver_analysis, key=lambda x: x['cost_analysis']['total_cost'], reverse=True)
        
        for i, analysis in enumerate(sorted_functions, 1):
            print(f"\n{i}. {analysis['function_name']}")
            print(f"   Runtime: {analysis['runtime']}")
            print(f"   Memory: {analysis['memory_size']} MB")
            print(f"   Invocations: {analysis['metrics']['Invocations']:,}")
            print(f"   Average Duration: {analysis['metrics']['AverageDuration']:.0f} ms")
            print(f"   Estimated Monthly Cost: ${analysis['cost_analysis']['total_cost']:.2f}")
            print(f"   Cost per Invocation: ${analysis['cost_analysis']['cost_per_invocation']:.6f}")
            print(f"   Error Rate: {analysis['performance_metrics']['error_rate']:.2f}%")
            print(f"   Throttle Rate: {analysis['performance_metrics']['throttle_rate']:.2f}%")
            print(f"   Driver: {analysis['demand_driver']}")
    
    def export_to_json(self, results: Dict, output_file: str):
        """
        Export results to JSON file.
        
        Args:
            results: Analysis results to export
            output_file: Path to output JSON file
        """
        try:
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"\nResults exported to: {output_file}")
        except Exception as e:
            print(f"Error exporting results to {output_file}: {e}")


def main():
    """Main function to run the Lambda driver detector."""
    parser = argparse.ArgumentParser(
        description='Analyze Lambda functions to identify workload demand drivers',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python driver_detector.py
  python driver_detector.py --region us-west-2 --output driver_report.json
  python driver_detector.py --demo --output demo_driver.json
  python driver_detector.py --profile my-aws-profile --region eu-west-1
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
        help='Output JSON file path (optional)'
    )
    
    parser.add_argument(
        '--profile',
        type=str,
        help='AWS profile name to use for authentication'
    )
    
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Run in demo mode with sample data (ignores AWS credentials)'
    )
    
    args = parser.parse_args()
    
    print("Lambda Driver Detector")
    print(f"Region: {args.region}")
    
    # Initialize detector
    detector = LambdaDriverDetector(
        region=args.region,
        profile_name=args.profile,
        demo_mode=args.demo
    )
    
    # Analyze Lambda functions
    results = detector.analyze_lambda_drivers()
    
    # Print summary
    detector.print_summary(results)
    
    # Export to JSON if output file specified
    if args.output:
        detector.export_to_json(results, args.output)
    
    # Exit with appropriate code
    total_functions = results['summary']['total_functions_analyzed']
    
    if total_functions > 0:
        print(f"\nAnalyzed {total_functions} Lambda functions with total estimated cost of ${results['summary']['total_estimated_monthly_cost']:.2f}/month")
        sys.exit(0)  # Success for analysis
    else:
        print("\nNo Lambda functions found in the specified region")
        sys.exit(0)  # Still success, just no data


if __name__ == '__main__':
    main()
