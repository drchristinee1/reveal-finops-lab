#!/usr/bin/env python3
"""
AWS RDS Driver Detector

This script analyzes Amazon RDS instances to identify workload demand drivers
that influence database costs through usage patterns and metrics.
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import boto3
from botocore.exceptions import ClientError, NoCredentialsError, EndpointConnectionError


class RDSDriverDetector:
    """Detects RDS workload demand drivers based on usage patterns."""
    
    # Simplified RDS pricing (actual prices vary by region and engine)
    RDS_PRICING = {
        'r5': {
            'large': {'instance_hourly': 0.21, 'storage_gb_monthly': 0.115},
            'xlarge': {'instance_hourly': 0.42, 'storage_gb_monthly': 0.115},
            '2xlarge': {'instance_hourly': 0.84, 'storage_gb_monthly': 0.115},
        },
        'r6g': {
            'large': {'instance_hourly': 0.252, 'storage_gb_monthly': 0.138},
            'xlarge': {'instance_hourly': 0.504, 'storage_gb_monthly': 0.138},
        },
        'db.t3': {
            'large': {'instance_hourly': 0.192, 'storage_gb_monthly': 0.095},
            'xlarge': {'instance_hourly': 0.384, 'storage_gb_monthly': 0.095},
        }
    }
    
    def __init__(self, region: str = 'us-east-1', profile_name: Optional[str] = None, demo_mode: bool = False):
        """Initialize the RDS driver detector."""
        self.region = region
        self.demo_mode = demo_mode
        self.demo_data = self._generate_demo_data()
        
        if not demo_mode:
            try:
                session = boto3.Session(profile_name=profile_name)
                self.rds_client = session.client('rds', region_name=region)
                self.cloudwatch_client = session.client('cloudwatch', region_name=region)
            except NoCredentialsError:
                print("Warning: AWS credentials not found. Enabling demo mode.")
                self.demo_mode = True
            except Exception as e:
                print(f"Error initializing AWS session: {e}")
                sys.exit(1)
    
    def _generate_demo_data(self) -> Dict:
        """Generate realistic sample RDS data for demo mode."""
        return {
            'instances': [
                {
                    'DBInstanceIdentifier': 'orders-prod-db',
                    'DBInstanceClass': 'db.r5.large',
                    'Engine': 'postgres',
                    'EngineVersion': '14.9',
                    'DBInstanceStatus': 'available',
                    'AllocatedStorage': 250,
                    'InstanceCreateTime': datetime(2024, 1, 15, 10, 30, 0),
                    'MultiAZ': False,
                    'AvailabilityZone': 'us-east-1a',
                    'PubliclyAccessible': False,
                    'StorageType': 'gp3',
                    'VpcId': 'vpc-12345678',
                    'DBSubnetGroup': 'default',
                    'TagList': [
                        {'Key': 'Environment', 'Value': 'production'},
                        {'Key': 'Team', 'Value': 'backend'},
                        {'Key': 'Name', 'Value': 'orders-prod-db'}
                    ],
                    'Metrics': {
                        'CPUUtilization': 18.4,
                        'FreeableMemory': 2.1,
                        'DatabaseConnections': 145,
                        'ReadIOPS': 320,
                        'WriteIOPS': 510
                    },
                    'Driver': 'Transaction processing'
                },
                {
                    'DBInstanceIdentifier': 'user-sessions-db',
                    'DBInstanceClass': 'db.r6g.large',
                    'Engine': 'mysql',
                    'EngineVersion': '8.0.35',
                    'DBInstanceStatus': 'available',
                    'AllocatedStorage': 500,
                    'InstanceCreateTime': datetime(2024, 2, 1, 14, 20, 0),
                    'MultiAZ': False,
                    'AvailabilityZone': 'us-east-1b',
                    'PubliclyAccessible': False,
                    'StorageType': 'io1',
                    'VpcId': 'vpc-12345678',
                    'DBSubnetGroup': 'default',
                    'TagList': [
                        {'Key': 'Environment', 'Value': 'production'},
                        {'Key': 'Team', 'Value': 'backend'},
                        {'Key': 'Name', 'Value': 'user-sessions-db'}
                    ],
                    'Metrics': {
                        'CPUUtilization': 12.8,
                        'FreeableMemory': 4.2,
                        'DatabaseConnections': 85,
                        'ReadIOPS': 180,
                        'WriteIOPS': 120
                    },
                    'Driver': 'Session management'
                },
                {
                    'DBInstanceIdentifier': 'analytics-warehouse',
                    'DBInstanceClass': 'db.r5.xlarge',
                    'Engine': 'postgres',
                    'EngineVersion': '14.9',
                    'DBInstanceStatus': 'available',
                    'AllocatedStorage': 1000,
                    'InstanceCreateTime': datetime(2023, 11, 20, 8, 45, 0),
                    'MultiAZ': True,
                    'AvailabilityZone': 'us-east-1c',
                    'PubliclyAccessible': False,
                    'StorageType': 'gp3',
                    'VpcId': 'vpc-12345678',
                    'DBSubnetGroup': 'default',
                    'TagList': [
                        {'Key': 'Environment', 'Value': 'production'},
                        {'Key': 'Team', 'Value': 'analytics'},
                        {'Key': 'Name', 'Value': 'analytics-warehouse'}
                    ],
                    'Metrics': {
                        'CPUUtilization': 45.2,
                        'FreeableMemory': 8.5,
                        'DatabaseConnections': 25,
                        'ReadIOPS': 850,
                        'WriteIOPS': 1200
                    },
                    'Driver': 'Analytics workload'
                },
                {
                    'DBInstanceIdentifier': 'catalog-readonly',
                    'DBInstanceClass': 'db.t3.large',
                    'Engine': 'mysql',
                    'EngineVersion': '8.0.35',
                    'DBInstanceStatus': 'available',
                    'AllocatedStorage': 100,
                    'InstanceCreateTime': datetime(2024, 1, 10, 16, 0, 0),
                    'MultiAZ': False,
                    'AvailabilityZone': 'us-east-1a',
                    'PubliclyAccessible': False,
                    'StorageType': 'gp2',
                    'VpcId': 'vpc-12345678',
                    'DBSubnetGroup': 'default',
                    'TagList': [
                        {'Key': 'Environment', 'Value': 'production'},
                        {'Key': 'Team', 'Value': 'catalog'},
                        {'Key': 'Name', 'Value': 'catalog-readonly'}
                    ],
                    'Metrics': {
                        'CPUUtilization': 8.5,
                        'FreeableMemory': 1.8,
                        'DatabaseConnections': 12,
                        'ReadIOPS': 45,
                        'WriteIOPS': 8
                    },
                    'Driver': 'Reporting queries'
                }
            ]
        }
    
    def get_rds_instances(self) -> List[Dict]:
        """
        Get all RDS instances in the region.
        
        Returns:
            List of RDS instance information
        """
        if self.demo_mode:
            return self.demo_data['instances']
        
        try:
            response = self.rds_client.describe_db_instances()
            
            instances = []
            for instance in response.get('DBInstances', []):
                # Only include available instances
                if instance['DBInstanceStatus'] == 'available':
                    instances.append(instance)
            
            return instances
        except ClientError as e:
            print(f"Error retrieving RDS instances: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error retrieving RDS instances: {e}")
            return []
    
    def get_instance_metrics(self, instance_id: str, days: int = 7) -> Optional[Dict]:
        """
        Get CloudWatch metrics for an RDS instance.
        
        Args:
            instance_id: Database instance identifier
            days: Number of days to look back for metrics
            
        Returns:
            Dictionary with metrics or None if unavailable
        """
        if self.demo_mode:
            # Return demo metrics
            for instance in self.demo_data['instances']:
                if instance['DBInstanceIdentifier'] == instance_id:
                    return instance['Metrics']
            return None
        
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            metrics = {}
            
            # Get CPUUtilization
            cpu_response = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/RDS',
                MetricName='CPUUtilization',
                Dimensions=[
                    {
                        'Name': 'DBInstanceIdentifier',
                        'Value': instance_id
                    }
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,  # 1 hour
                Statistics=['Average']
            )
            
            # Get FreeableMemory
            memory_response = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/RDS',
                MetricName='FreeableMemory',
                Dimensions=[
                    {
                        'Name': 'DBInstanceIdentifier',
                        'Value': instance_id
                    }
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,  # 1 hour
                Statistics=['Average']
            )
            
            # Get DatabaseConnections
            connections_response = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/RDS',
                MetricName='DatabaseConnections',
                Dimensions=[
                    {
                        'Name': 'DBInstanceIdentifier',
                        'Value': instance_id
                    }
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,  # 1 hour
                Statistics=['Average']
            )
            
            # Get ReadIOPS
            read_iops_response = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/RDS',
                MetricName='ReadIOPS',
                Dimensions=[
                    {
                        'Name': 'DBInstanceIdentifier',
                        'Value': instance_id
                    }
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,  # 1 hour
                Statistics=['Average']
            )
            
            # Get WriteIOPS
            write_iops_response = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/RDS',
                MetricName='WriteIOPS',
                Dimensions=[
                    {
                        'Name': 'DBInstanceIdentifier',
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
            memory_data = memory_response.get('Datapoints', [])
            connections_data = connections_response.get('Datapoints', [])
            read_iops_data = read_iops_response.get('Datapoints', [])
            write_iops_data = write_iops_response.get('Datapoints', [])
            
            avg_cpu = sum(dp['Average'] for dp in cpu_data) / len(cpu_data) if cpu_data else 0
            avg_memory = sum(dp['Average'] for dp in memory_data) / len(memory_data) if memory_data else 0
            avg_connections = sum(dp['Average'] for dp in connections_data) / len(connections_data) if connections_data else 0
            avg_read_iops = sum(dp['Average'] for dp in read_iops_data) / len(read_iops_data) if read_iops_data else 0
            avg_write_iops = sum(dp['Average'] for dp in write_iops_data) / len(write_iops_data) if write_iops_data else 0
            
            return {
                'CPUUtilization': avg_cpu,
                'FreeableMemory': avg_memory,
                'DatabaseConnections': avg_connections,
                'ReadIOPS': avg_read_iops,
                'WriteIOPS': avg_write_iops
            }
            
        except ClientError as e:
            print(f"Error retrieving metrics for {instance_id}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error retrieving metrics for {instance_id}: {e}")
            return None
    
    def get_instance_pricing(self, instance_class: str, engine: str) -> Dict:
        """
        Get pricing information for an RDS instance class.
        
        Args:
            instance_class: RDS instance class (e.g., db.r5.large)
            engine: Database engine type
            
        Returns:
            Pricing dictionary or default pricing
        """
        # Extract instance family and size
        parts = instance_class.split('.')
        if len(parts) >= 3:
            family = parts[1]  # r5, r6g, db.t3
            size = parts[2]  # large, xlarge, etc.
        else:
            # Use default pricing if not found
            return {
                'instance_hourly': 0.2,
                'storage_gb_monthly': 0.1
            }
        
        # Get pricing for the family
        family_pricing = self.RDS_PRICING.get(family, {})
        pricing = family_pricing.get(size, {
            'instance_hourly': 0.2,
            'storage_gb_monthly': 0.1
        })
        
        return pricing
    
    def calculate_instance_cost(self, instance: Dict, metrics: Dict) -> Dict:
        """
        Calculate estimated monthly cost for an RDS instance.
        
        Args:
            instance: RDS instance configuration
            metrics: CloudWatch metrics for the instance
            
        Returns:
            Cost breakdown dictionary
        """
        instance_class = instance['DBInstanceClass']
        engine = instance['Engine']
        allocated_storage = instance['AllocatedStorage']
        
        # Get pricing
        pricing = self.get_instance_pricing(instance_class, engine)
        
        # Calculate costs
        instance_hourly_cost = pricing['instance_hourly']
        storage_monthly_cost = allocated_storage * pricing['storage_gb_monthly']
        
        # Monthly instance cost (730 hours in a month)
        instance_monthly_cost = instance_hourly_cost * 730
        
        total_monthly_cost = instance_monthly_cost + storage_monthly_cost
        
        return {
            'instance_hourly_cost': instance_hourly_cost,
            'storage_monthly_cost': storage_monthly_cost,
            'total_monthly_cost': total_monthly_cost,
            'instance_monthly_cost': instance_monthly_cost,
            'allocated_storage_gb': allocated_storage,
            'pricing': pricing
        }
    
    def identify_demand_driver(self, instance: Dict, metrics: Dict, cost_analysis: Dict) -> str:
        """
        Identify the likely demand driver based on instance characteristics and usage patterns.
        
        Args:
            instance: RDS instance configuration
            metrics: CloudWatch metrics for the instance
            cost_analysis: Cost analysis for the instance
            
        Returns:
            Identified demand driver
        """
        instance_id = instance['DBInstanceIdentifier'].lower()
        engine = instance['Engine'].lower()
        instance_class = instance['DBInstanceClass'].lower()
        allocated_storage = instance['AllocatedStorage']
        multi_az = instance.get('MultiAZ', False)
        
        cpu_utilization = metrics['CPUUtilization']
        freeable_memory = metrics['FreeableMemory']
        connections = metrics['DatabaseConnections']
        read_iops = metrics['ReadIOPS']
        write_iops = metrics['WriteIOPS']
        
        # Calculate IOPS ratios
        total_iops = read_iops + write_iops
        read_ratio = read_iops / total_iops if total_iops > 0 else 0
        write_ratio = write_iops / total_iops if total_iops > 0 else 0
        
        # Analyze patterns to identify drivers
        if 'order' in instance_id or 'transaction' in instance_id:
            return 'Transaction processing'
        elif 'session' in instance_id or 'user' in instance_id:
            return 'Session management'
        elif 'analytics' in instance_id or 'warehouse' in instance_id or 'reporting' in instance_id:
            return 'Analytics workload'
        elif 'catalog' in instance_id or 'product' in instance_id:
            return 'Product catalog'
        elif 'audit' in instance_id or 'log' in instance_id:
            return 'Audit logging'
        elif 'backup' in instance_id or 'archive' in instance_id:
            return 'Backup/Archive'
        elif 'cache' in instance_id or 'redis' in instance_id:
            return 'Caching layer'
        elif allocated_storage > 500:
            return 'Data retention'
        elif read_iops > 500:
            return 'Read-heavy reporting'
        elif write_iops > 500:
            return 'Write-intensive transactions'
        elif connections > 100:
            return 'High connection traffic'
        elif cpu_utilization > 40:
            return 'CPU-intensive workload'
        elif freeable_memory < 1:
            return 'Memory pressure'
        elif multi_az:
            return 'High availability requirements'
        elif read_ratio > 0.7:
            return 'Read-heavy applications'
        elif write_ratio > 0.6:
            return 'Write-intensive applications'
        else:
            return 'General database workload'
    
    def analyze_rds_drivers(self) -> Dict:
        """
        Analyze all RDS instances to identify demand drivers.
        
        Returns:
            Analysis results with driver information
        """
        print("Analyzing RDS instances for demand drivers...")
        
        if self.demo_mode:
            print("Running in DEMO MODE with sample data")
        
        instances = self.get_rds_instances()
        driver_analysis = []
        
        for instance in instances:
            instance_id = instance['DBInstanceIdentifier']
            
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
            optimization_signals = []
            if metrics['CPUUtilization'] < 20 and metrics['DatabaseConnections'] < 10:
                optimization_signals.append("Underutilized instance - consider downsizing")
            elif metrics['CPUUtilization'] > 80:
                optimization_signals.append("High CPU utilization - consider scaling up")
            elif metrics['FreeableMemory'] < 1:
                optimization_signals.append("Memory pressure - consider increasing memory")
            
            analysis = {
                'instance_id': instance_id,
                'instance_class': instance['DBInstanceClass'],
                'engine': instance['Engine'],
                'engine_version': instance['EngineVersion'],
                'instance_status': instance['DBInstanceStatus'],
                'allocated_storage': instance['AllocatedStorage'],
                'multi_az': instance.get('MultiAZ', False),
                'availability_zone': instance['AvailabilityZone'],
                'storage_type': instance['StorageType'],
                'vpc_id': instance['VpcId'],
                'tags': instance.get('TagList', []),
                'create_time': instance['InstanceCreateTime'],
                'metrics': metrics,
                'cost_analysis': cost_analysis,
                'demand_driver': driver,
                'optimization_signals': optimization_signals,
                'usage_patterns': {
                    'cpu_utilization': metrics['CPUUtilization'],
                    'freeable_memory_gb': metrics['FreeableMemory'],
                    'avg_connections': metrics['DatabaseConnections'],
                    'avg_read_iops': metrics['ReadIOPS'],
                    'avg_write_iops': metrics['WriteIOPS'],
                    'read_ratio': metrics['ReadIOPS'] / (metrics['ReadIOPS'] + metrics['WriteIOPS']) if (metrics['ReadIOPS'] + metrics['WriteIOPS']) > 0 else 0,
                    'write_ratio': metrics['WriteIOPS'] / (metrics['ReadIOPS'] + metrics['WriteIOPS']) if (metrics['ReadIOPS'] + metrics['WriteIOPS']) > 0 else 0,
                    'allocated_storage_gb': instance['AllocatedStorage']
                }
            }
            
            driver_analysis.append(analysis)
        
        # Calculate summary
        total_instances = len(driver_analysis)
        total_monthly_cost = sum(analysis['cost_analysis']['total_monthly_cost'] for analysis in driver_analysis)
        total_storage = sum(analysis['usage_patterns']['allocated_storage_gb'] for analysis in driver_analysis)
        
        # Group by demand drivers
        driver_groups = {}
        for analysis in driver_analysis:
            driver = analysis['demand_driver']
            if driver not in driver_groups:
                driver_groups[driver] = {
                    'instances': [],
                    'total_monthly_cost': 0,
                    'total_storage': 0,
                    'avg_cpu_utilization': 0,
                    'avg_connections': 0
                }
            driver_groups[driver]['instances'].append(analysis['instance_id'])
            driver_groups[driver]['total_monthly_cost'] += analysis['cost_analysis']['total_monthly_cost']
            driver_groups[driver]['total_storage'] += analysis['usage_patterns']['allocated_storage_gb']
            driver_groups[driver]['avg_cpu_utilization'] += analysis['usage_patterns']['cpu_utilization']
            driver_groups[driver]['avg_connections'] += analysis['usage_patterns']['avg_connections']
        
        # Calculate averages for driver groups
        for driver in driver_groups:
            group = driver_groups[driver]
            instance_count = len(group['instances'])
            group['avg_cpu_utilization'] = group['avg_cpu_utilization'] / instance_count if instance_count > 0 else 0
            group['avg_connections'] = group['avg_connections'] / instance_count if instance_count > 0 else 0
        
        results = {
            'scan_time': datetime.now().isoformat(),
            'region': self.region,
            'demo_mode': self.demo_mode,
            'analysis_period_days': 7,
            'rds_pricing': self.RDS_PRICING,
            'driver_analysis': driver_analysis,
            'driver_groups': driver_groups,
            'summary': {
                'total_instances_analyzed': total_instances,
                'total_monthly_cost': total_monthly_cost,
                'total_storage_gb': total_storage,
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
        
        print(f"\nRDS Driver Analysis")
        print(f"====================")
        print(f"Region: {results['region']}")
        print(f"Scan Time: {results['scan_time']}")
        print(f"Analysis Period: {results['analysis_period_days']} days")
        if results['demo_mode']:
            print(f"Mode: DEMO (using sample data)")
        
        print(f"\n--- Summary ---")
        print(f"Total Instances Analyzed: {summary['total_instances_analyzed']}")
        print(f"Total Monthly Cost: ${summary['total_monthly_cost']:.2f}")
        print(f"Total Storage: {summary['total_storage_gb']:.0f} GB")
        print(f"Unique Demand Drivers: {summary['unique_demand_drivers']}")
        print(f"Average Cost per Instance: ${summary['average_cost_per_instance']:.2f}")
        
        print(f"\n--- Demand Drivers ---")
        # Sort drivers by total cost (descending)
        sorted_drivers = sorted(driver_groups.items(), key=lambda x: x[1]['total_monthly_cost'], reverse=True)
        
        for driver, data in sorted_drivers:
            print(f"\n{driver}:")
            print(f"  Instances: {', '.join(data['instances'])}")
            print(f"  Monthly Cost: ${data['total_monthly_cost']:.2f}")
            print(f"  Storage: {data['total_storage']:.0f} GB")
            print(f"  Avg CPU Utilization: {data['avg_cpu_utilization']:.1f}%")
            print(f"  Avg Connections: {data['avg_connections']:.0f}")
        
        print(f"\n--- Instance Details ---")
        # Sort instances by cost (descending)
        sorted_instances = sorted(driver_analysis, key=lambda x: x['cost_analysis']['total_monthly_cost'], reverse=True)
        
        for i, analysis in enumerate(sorted_instances, 1):
            print(f"\n{i}. {analysis['instance_id']}")
            print(f"   Engine: {analysis['engine']} {analysis['engine_version']}")
            print(f"   Instance Class: {analysis['instance_class']}")
            print(f"   Status: {analysis['instance_status']}")
            print(f"   Storage: {analysis['usage_patterns']['allocated_storage_gb']:.0f} GB ({analysis['storage_type']})")
            print(f"   Multi-AZ: {analysis['multi_az']}")
            print(f"   CPU Utilization: {analysis['usage_patterns']['cpu_utilization']:.1f}%")
            print(f"   Freeable Memory: {analysis['usage_patterns']['freeable_memory_gb']:.1f} GB")
            print(f"   Connections: {analysis['usage_patterns']['avg_connections']:.0f}")
            print(f"   Read IOPS: {analysis['usage_patterns']['avg_read_iops']:.0f}")
            print(f"   Write IOPS: {analysis['usage_patterns']['avg_write_iops']:.0f}")
            print(f"   Estimated Monthly Cost: ${analysis['cost_analysis']['total_monthly_cost']:.2f}")
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
    """Main function to run the RDS driver detector."""
    parser = argparse.ArgumentParser(
        description='Analyze RDS instances to identify workload demand drivers',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python rds_driver_detector.py
  python rds_driver_detector.py --region us-west-2 --output rds_report.json
  python rds_driver_detector.py --demo --output demo_rds.json
  python rds_driver_detector.py --profile my-aws-profile --region eu-west-1
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
    
    print("RDS Driver Detector")
    print(f"Region: {args.region}")
    
    # Initialize detector
    detector = RDSDriverDetector(
        region=args.region,
        profile_name=args.profile,
        demo_mode=args.demo
    )
    
    # Analyze RDS instances
    results = detector.analyze_rds_drivers()
    
    # Print summary
    detector.print_summary(results)
    
    # Export to JSON if output file specified
    if args.output:
        detector.export_to_json(results, args.output)
    
    # Exit with appropriate code
    total_instances = results['summary']['total_instances_analyzed']
    
    if total_instances > 0:
        print(f"\nAnalyzed {total_instances} RDS instances with total estimated cost of ${results['summary']['total_monthly_cost']:.2f}/month")
        sys.exit(0)  # Success for analysis
    else:
        print("\nNo RDS instances found in the specified region")
        sys.exit(0)  # Still success, just no data


if __name__ == '__main__':
    main()
