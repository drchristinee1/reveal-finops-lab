#!/usr/bin/env python3
"""
AWS EC2 Driver Detector

This script analyzes EC2 instances to identify compute demand drivers
that influence cloud costs through usage patterns and metrics.
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import boto3
from botocore.exceptions import ClientError, NoCredentialsError, EndpointConnectionError


class EC2DriverDetector:
    """Detects EC2 workload demand drivers based on usage patterns."""
    
    # Simplified EC2 pricing (actual prices vary by region)
    EC2_PRICING = {
        't3': {
            'nano': {'hourly': 0.0052},
            'micro': {'hourly': 0.0104},
            'small': {'hourly': 0.0208},
            'medium': {'hourly': 0.0416},
            'large': {'hourly': 0.0832},
            'xlarge': {'hourly': 0.1664},
        },
        't3a': {
            'nano': {'hourly': 0.0047},
            'micro': {'hourly': 0.0094},
            'small': {'hourly': 0.0188},
            'medium': {'hourly': 0.0376},
            'large': {'hourly': 0.0752},
            'xlarge': {'hourly': 0.1504},
        },
        'm5': {
            'large': {'hourly': 0.096},
            'xlarge': {'hourly': 0.192},
            '2xlarge': {'hourly': 0.384},
            '4xlarge': {'hourly': 0.768},
        },
        'm5a': {
            'large': {'hourly': 0.086},
            'xlarge': {'hourly': 0.172},
            '2xlarge': {'hourly': 0.344},
            '4xlarge': {'hourly': 0.688},
        },
        'c5': {
            'large': {'hourly': 0.085},
            'xlarge': {'hourly': 0.17},
            '2xlarge': {'hourly': 0.34},
            '4xlarge': {'hourly': 0.68},
        },
        'r5': {
            'large': {'hourly': 0.126},
            'xlarge': {'hourly': 0.252},
            '2xlarge': {'hourly': 0.504},
            '4xlarge': {'hourly': 1.008},
        }
    }
    
    def __init__(self, region: str = 'us-east-1', profile_name: Optional[str] = None, demo_mode: bool = False):
        """Initialize the EC2 driver detector."""
        self.region = region
        self.demo_mode = demo_mode
        self.demo_data = self._generate_demo_data()
        
        if not demo_mode:
            try:
                session = boto3.Session(profile_name=profile_name)
                self.ec2_client = session.client('ec2', region_name=region)
                self.cloudwatch_client = session.client('cloudwatch', region_name=region)
            except NoCredentialsError:
                print("Warning: AWS credentials not found. Enabling demo mode.")
                self.demo_mode = True
            except Exception as e:
                print(f"Error initializing AWS session: {e}")
                sys.exit(1)
    
    def _generate_demo_data(self) -> Dict:
        """Generate realistic sample EC2 data for demo mode."""
        return {
            'instances': [
                {
                    'InstanceId': 'i-0abc123def456ghi789',
                    'InstanceType': 'm5.large',
                    'State': {'Name': 'running', 'Code': 16},
                    'LaunchTime': datetime(2024, 1, 15, 10, 30, 0),
                    'AvailabilityZone': 'us-east-1a',
                    'VpcId': 'vpc-12345678',
                    'SubnetId': 'subnet-12345678',
                    'Tags': [
                        {'Key': 'Name', 'Value': 'web-server-prod-01'},
                        {'Key': 'Environment', 'Value': 'production'},
                        {'Key': 'Team', 'Value': 'backend'},
                        {'Key': 'Role', 'Value': 'web'}
                    ],
                    'Metrics': {
                        'CPUUtilization': 12.3,
                        'RunningHours': 720
                    },
                    'Driver': 'Overprovisioned compute'
                },
                {
                    'InstanceId': 'i-1def789abc012ghi345',
                    'InstanceType': 'c5.xlarge',
                    'State': {'Name': 'running', 'Code': 16},
                    'LaunchTime': datetime(2024, 2, 1, 14, 20, 0),
                    'AvailabilityZone': 'us-east-1b',
                    'VpcId': 'vpc-12345678',
                    'SubnetId': 'subnet-12345678',
                    'Tags': [
                        {'Key': 'Name', 'Value': 'batch-processor-01'},
                        {'Key': 'Environment', 'Value': 'production'},
                        {'Key': 'Team', 'Value': 'data'},
                        {'Key': 'Role', 'Value': 'processing'}
                    ],
                    'Metrics': {
                        'CPUUtilization': 85.7,
                        'RunningHours': 720
                    },
                    'Driver': 'Scaling pressure'
                },
                {
                    'InstanceId': 'i-2ghi345def789abc012',
                    'InstanceType': 't3.medium',
                    'State': {'Name': 'stopped', 'Code': 80},
                    'LaunchTime': datetime(2024, 1, 10, 16, 0, 0),
                    'AvailabilityZone': 'us-east-1c',
                    'VpcId': 'vpc-12345678',
                    'SubnetId': 'subnet-12345678',
                    'Tags': [
                        {'Key': 'Name', 'Value': 'dev-server-01'},
                        {'Key': 'Environment', 'Value': 'development'},
                        {'Key': 'Team', 'Value': 'devops'},
                        {'Key': 'Role', 'Value': 'testing'}
                    ],
                    'Metrics': {
                        'CPUUtilization': 0.0,
                        'RunningHours': 0
                    },
                    'Driver': 'Stopped instance'
                },
                {
                    'InstanceId': 'i-3jkl456mno789pqr012',
                    'InstanceType': 'r5.large',
                    'State': {'Name': 'running', 'Code': 16},
                    'LaunchTime': datetime(2023, 12, 20, 8, 45, 0),
                    'AvailabilityZone': 'us-east-1d',
                    'VpcId': 'vpc-12345678',
                    'SubnetId': 'subnet-12345678',
                    'Tags': [
                        {'Key': 'Name', 'Value': 'database-proxy-01'},
                        {'Key': 'Environment', 'Value': 'production'},
                        {'Key': 'Team', 'Value': 'backend'},
                        {'Key': 'Role', 'Value': 'proxy'}
                    ],
                    'Metrics': {
                        'CPUUtilization': 45.2,
                        'RunningHours': 720
                    },
                    'Driver': 'Active workload'
                }
            ]
        }
    
    def get_ec2_instances(self) -> List[Dict]:
        """
        Get all EC2 instances in the region.
        
        Returns:
            List of EC2 instance information
        """
        if self.demo_mode:
            return self.demo_data['instances']
        
        try:
            response = self.ec2_client.describe_instances()
            
            instances = []
            for reservation in response.get('Reservations', []):
                for instance in reservation.get('Instances', []):
                    instances.append(instance)
            
            return instances
        except ClientError as e:
            print(f"Error retrieving EC2 instances: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error retrieving EC2 instances: {e}")
            return []
    
    def get_instance_metrics(self, instance_id: str, days: int = 7) -> Optional[Dict]:
        """
        Get CloudWatch metrics for an EC2 instance.
        
        Args:
            instance_id: EC2 instance ID
            days: Number of days to look back for metrics
            
        Returns:
            Dictionary with metrics or None if unavailable
        """
        if self.demo_mode:
            # Return demo metrics
            for instance in self.demo_data['instances']:
                if instance['InstanceId'] == instance_id:
                    return instance['Metrics']
            return None
        
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            metrics = {}
            
            # Get CPUUtilization
            cpu_response = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[
                    {
                        'Name': 'InstanceId',
                        'Value': instance_id
                    }
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,  # 1 hour
                Statistics=['Average']
            )
            
            # Calculate averages
            cpu_data = cpu_response.get('Datapoints', [])
            avg_cpu = sum(dp['Average'] for dp in cpu_data) / len(cpu_data) if cpu_data else 0
            
            return {
                'CPUUtilization': avg_cpu,
                'RunningHours': days * 24  # Assume running for the full period
            }
            
        except ClientError as e:
            print(f"Error retrieving metrics for {instance_id}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error retrieving metrics for {instance_id}: {e}")
            return None
    
    def get_instance_pricing(self, instance_type: str) -> Dict:
        """
        Get pricing information for an EC2 instance type.
        
        Args:
            instance_type: EC2 instance type (e.g., m5.large)
            
        Returns:
            Pricing dictionary or default pricing
        """
        # Extract instance family and size
        parts = instance_type.split('.')
        if len(parts) >= 2:
            family = parts[0]  # t3, m5, c5, r5
            size = parts[1]  # nano, micro, small, large, xlarge, etc.
        else:
            # Use default pricing if not found
            return {
                'hourly': 0.1
            }
        
        # Get pricing for the family
        family_pricing = self.EC2_PRICING.get(family, {})
        pricing = family_pricing.get(size, {
            'hourly': 0.1
        })
        
        return pricing
    
    def calculate_instance_cost(self, instance: Dict, metrics: Dict) -> Dict:
        """
        Calculate estimated monthly cost for an EC2 instance.
        
        Args:
            instance: EC2 instance configuration
            metrics: CloudWatch metrics for the instance
            
        Returns:
            Cost breakdown dictionary
        """
        instance_type = instance['InstanceType']
        instance_state = instance['State']['Name']
        
        # Get pricing
        pricing = self.get_instance_pricing(instance_type)
        
        # Calculate costs
        hourly_cost = pricing['hourly']
        running_hours = metrics['RunningHours']
        
        # Monthly cost (730 hours in a month)
        if instance_state == 'running':
            monthly_cost = hourly_cost * 730
        else:
            monthly_cost = 0  # Stopped instances incur no compute cost
        
        return {
            'hourly_cost': hourly_cost,
            'running_hours': running_hours,
            'monthly_cost': monthly_cost,
            'instance_state': instance_state,
            'pricing': pricing
        }
    
    def identify_demand_driver(self, instance: Dict, metrics: Dict, cost_analysis: Dict) -> str:
        """
        Identify the likely demand driver based on instance characteristics and usage patterns.
        
        Args:
            instance: EC2 instance configuration
            metrics: CloudWatch metrics for the instance
            cost_analysis: Cost analysis for the instance
            
        Returns:
            Identified demand driver
        """
        instance_id = instance['InstanceId']
        instance_type = instance['InstanceType']
        instance_state = instance['State']['Name']
        cpu_utilization = metrics['CPUUtilization']
        
        # Get tags for analysis
        tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
        name = tags.get('Name', '').lower()
        role = tags.get('Role', '').lower()
        environment = tags.get('Environment', '').lower()
        team = tags.get('Team', '').lower()
        
        # Analyze patterns to identify drivers
        if instance_state == 'stopped':
            return 'Stopped instance'
        elif 'web' in name or 'web' in role:
            return 'Web server workload'
        elif 'batch' in name or 'batch' in role or 'processing' in role:
            return 'Batch processing'
        elif 'database' in name or 'db' in name or 'proxy' in role:
            return 'Database proxy workload'
        elif 'cache' in name or 'redis' in name or 'cache' in role:
            return 'Cache workload'
        elif 'dev' in environment or 'test' in environment:
            return 'Development/testing'
        elif 'staging' in environment:
            return 'Staging environment'
        elif cpu_utilization > 80:
            return 'Scaling pressure'
        elif cpu_utilization < 20 and instance_state == 'running':
            return 'Overprovisioned compute'
        elif cpu_utilization > 60:
            return 'Active workload'
        elif cpu_utilization > 40:
            return 'Moderate workload'
        elif instance_type.startswith('c5'):
            return 'Compute-intensive workload'
        elif instance_type.startswith('r5'):
            return 'Memory-intensive workload'
        elif instance_type.startswith('t3'):
            return 'General purpose workload'
        else:
            return 'Unknown workload'
    
    def calculate_optimization_signals(self, instance: Dict, metrics: Dict, cost_analysis: Dict) -> List[str]:
        """
        Calculate optimization signals for an instance.
        
        Args:
            instance: EC2 instance configuration
            metrics: CloudWatch metrics for the instance
            cost_analysis: Cost analysis for the instance
            
        Returns:
            List of optimization signals
        """
        signals = []
        instance_state = instance['State']['Name']
        cpu_utilization = metrics['CPUUtilization']
        instance_type = instance['InstanceType']
        
        # Get tags for analysis
        tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
        environment = tags.get('Environment', '').lower()
        
        if instance_state == 'stopped':
            if 'production' not in environment:
                signals.append("Consider terminating unused development instance")
            else:
                signals.append("Stopped production instance - investigate reason")
        elif cpu_utilization < 20:
            signals.append("Consider downsizing or scheduling shutdown")
            signals.append("Low utilization suggests overprovisioning")
        elif cpu_utilization > 80:
            signals.append("High CPU utilization - consider scaling up")
            signals.append("Performance bottleneck detected")
        elif cpu_utilization > 60:
            signals.append("Monitor for scaling opportunities")
        
        # Instance type specific signals
        if instance_type.startswith('t3') and cpu_utilization > 70:
            signals.append("Burstable instance limit reached - consider larger instance")
        
        # Environment specific signals
        if 'development' in environment and instance_state == 'running':
            signals.append("Consider scheduling development instance shutdown")
        
        return signals
    
    def analyze_ec2_drivers(self) -> Dict:
        """
        Analyze all EC2 instances to identify demand drivers.
        
        Returns:
            Analysis results with driver information
        """
        print("Analyzing EC2 instances for demand drivers...")
        
        if self.demo_mode:
            print("Running in DEMO MODE with sample data")
        
        instances = self.get_ec2_instances()
        driver_analysis = []
        
        for instance in instances:
            instance_id = instance['InstanceId']
            
            # Get metrics
            metrics = self.get_instance_metrics(instance_id)
            
            if not metrics:
                print(f"Warning: No metrics available for {instance_id}")
                continue
            
            # Calculate costs
            cost_analysis = self.calculate_instance_cost(instance, metrics)
            
            # Identify demand driver
            driver = self.identify_demand_driver(instance, metrics, cost_analysis)
            
            # Calculate optimization signals
            optimization_signals = self.calculate_optimization_signals(instance, metrics, cost_analysis)
            
            analysis = {
                'instance_id': instance_id,
                'instance_type': instance['InstanceType'],
                'instance_state': instance['State']['Name'],
                'instance_state_code': instance['State']['Code'],
                'launch_time': instance['LaunchTime'],
                'availability_zone': instance['AvailabilityZone'],
                'vpc_id': instance['VpcId'],
                'subnet_id': instance['SubnetId'],
                'tags': instance.get('Tags', []),
                'metrics': metrics,
                'cost_analysis': cost_analysis,
                'demand_driver': driver,
                'optimization_signals': optimization_signals,
                'usage_patterns': {
                    'cpu_utilization': metrics['CPUUtilization'],
                    'running_hours': metrics['RunningHours'],
                    'instance_family': instance['InstanceType'].split('.')[0],
                    'instance_size': instance['InstanceType'].split('.')[1] if '.' in instance['InstanceType'] else 'unknown'
                }
            }
            
            driver_analysis.append(analysis)
        
        # Calculate summary
        total_instances = len(driver_analysis)
        running_instances = len([a for a in driver_analysis if a['instance_state'] == 'running'])
        stopped_instances = len([a for a in driver_analysis if a['instance_state'] == 'stopped'])
        total_monthly_cost = sum(analysis['cost_analysis']['monthly_cost'] for analysis in driver_analysis)
        
        # Group by demand drivers
        driver_groups = {}
        for analysis in driver_analysis:
            driver = analysis['demand_driver']
            if driver not in driver_groups:
                driver_groups[driver] = {
                    'instances': [],
                    'total_monthly_cost': 0,
                    'avg_cpu_utilization': 0,
                    'running_count': 0,
                    'stopped_count': 0
                }
            driver_groups[driver]['instances'].append(analysis['instance_id'])
            driver_groups[driver]['total_monthly_cost'] += analysis['cost_analysis']['monthly_cost']
            driver_groups[driver]['avg_cpu_utilization'] += analysis['usage_patterns']['cpu_utilization']
            if analysis['instance_state'] == 'running':
                driver_groups[driver]['running_count'] += 1
            else:
                driver_groups[driver]['stopped_count'] += 1
        
        # Calculate averages for driver groups
        for driver in driver_groups:
            group = driver_groups[driver]
            instance_count = len(group['instances'])
            group['avg_cpu_utilization'] = group['avg_cpu_utilization'] / instance_count if instance_count > 0 else 0
        
        results = {
            'scan_time': datetime.now().isoformat(),
            'region': self.region,
            'demo_mode': self.demo_mode,
            'analysis_period_days': 7,
            'ec2_pricing': self.EC2_PRICING,
            'driver_analysis': driver_analysis,
            'driver_groups': driver_groups,
            'summary': {
                'total_instances_analyzed': total_instances,
                'running_instances': running_instances,
                'stopped_instances': stopped_instances,
                'total_monthly_cost': total_monthly_cost,
                'unique_demand_drivers': len(driver_groups),
                'average_cost_per_instance': total_monthly_cost / total_instances if total_instances > 0 else 0
            }
        }
        
        return results
    
    def print_summary(self, results: Dict):
        """Print a readable summary of the analysis."""
        summary = results['summary']
        driver_groups = results['driver_groups']
        driver_analysis = results['driver_analysis']
        
        print(f"\nEC2 Driver Analysis")
        print(f"====================")
        print(f"Region: {results['region']}")
        print(f"Scan Time: {results['scan_time']}")
        print(f"Analysis Period: {results['analysis_period_days']} days")
        if results['demo_mode']:
            print(f"Mode: DEMO (using sample data)")
        
        print(f"\n--- Summary ---")
        print(f"Total Instances Analyzed: {summary['total_instances_analyzed']}")
        print(f"Running Instances: {summary['running_instances']}")
        print(f"Stopped Instances: {summary['stopped_instances']}")
        print(f"Total Monthly Cost: ${summary['total_monthly_cost']:.2f}")
        print(f"Unique Demand Drivers: {summary['unique_demand_drivers']}")
        print(f"Average Cost per Instance: ${summary['average_cost_per_instance']:.2f}")
        
        print(f"\n--- Demand Drivers ---")
        # Sort drivers by total cost (descending)
        sorted_drivers = sorted(driver_groups.items(), key=lambda x: x[1]['total_monthly_cost'], reverse=True)
        
        for driver, data in sorted_drivers:
            print(f"\n{driver}:")
            print(f"  Instances: {', '.join(data['instances'])}")
            print(f"  Monthly Cost: ${data['total_monthly_cost']:.2f}")
            print(f"  Running: {data['running_count']}, Stopped: {data['stopped_count']}")
            print(f"  Avg CPU Utilization: {data['avg_cpu_utilization']:.1f}%")
        
        print(f"\n--- Instance Details ---")
        # Sort instances by cost (descending)
        sorted_instances = sorted(driver_analysis, key=lambda x: x['cost_analysis']['monthly_cost'], reverse=True)
        
        for i, analysis in enumerate(sorted_instances, 1):
            print(f"\n{i}. {analysis['instance_id']}")
            print(f"   Type: {analysis['instance_type']}")
            print(f"   State: {analysis['instance_state']}")
            print(f"   CPU Utilization: {analysis['usage_patterns']['cpu_utilization']:.1f}%")
            print(f"   Running Hours: {analysis['usage_patterns']['running_hours']:.0f}")
            print(f"   Estimated Monthly Cost: ${analysis['cost_analysis']['monthly_cost']:.2f}")
            print(f"   Driver: {analysis['demand_driver']}")
            
            if analysis['optimization_signals']:
                print(f"   Optimization Signals:")
                for signal in analysis['optimization_signals']:
                    print(f"     • {signal}")
    
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
    """Main function to run the EC2 driver detector."""
    parser = argparse.ArgumentParser(
        description='Analyze EC2 instances to identify compute demand drivers',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ec2_driver_detector.py
  python ec2_driver_detector.py --region us-west-2 --output ec2_report.json
  python ec2_driver_detector.py --demo --output demo_ec2.json
  python ec2_driver_detector.py --profile my-aws-profile --region eu-west-1
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
    
    print("EC2 Driver Detector")
    print(f"Region: {args.region}")
    
    # Initialize detector
    detector = EC2DriverDetector(
        region=args.region,
        profile_name=args.profile,
        demo_mode=args.demo
    )
    
    # Analyze EC2 instances
    results = detector.analyze_ec2_drivers()
    
    # Print summary
    detector.print_summary(results)
    
    # Export to JSON if output file specified
    if args.output:
        detector.export_to_json(results, args.output)
    
    # Exit with appropriate code
    total_instances = results['summary']['total_instances_analyzed']
    
    if total_instances > 0:
        print(f"\nAnalyzed {total_instances} EC2 instances with total estimated cost of ${results['summary']['total_monthly_cost']:.2f}/month")
        sys.exit(0)  # Success for analysis
    else:
        print("\nNo EC2 instances found in the specified region")
        sys.exit(0)  # Still success, just no data


if __name__ == '__main__':
    main()
