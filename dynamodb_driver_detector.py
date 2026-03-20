#!/usr/bin/env python3
"""
AWS DynamoDB Driver Detector

This script analyzes DynamoDB tables to identify workload demand drivers
that influence cloud costs through usage patterns and storage.
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import boto3
from botocore.exceptions import ClientError, NoCredentialsError, EndpointConnectionError


class DynamoDBDriverDetector:
    """Detects DynamoDB workload demand drivers based on usage patterns."""
    
    # Simplified DynamoDB pricing (actual prices vary by region)
    DYNAMODB_PRICING = {
        'read_cost_per_million': 0.25,
        'write_cost_per_million': 1.25,
        'storage_cost_per_gb': 0.25
    }
    
    def __init__(self, region: str = 'us-east-1', profile_name: Optional[str] = None, demo_mode: bool = False):
        """Initialize the DynamoDB driver detector."""
        self.region = region
        self.demo_mode = demo_mode
        self.demo_data = self._generate_demo_data()
        
        if not demo_mode:
            try:
                session = boto3.Session(profile_name=profile_name)
                self.dynamodb_client = session.client('dynamodb', region_name=region)
                self.cloudwatch_client = session.client('cloudwatch', region_name=region)
            except NoCredentialsError:
                print("Warning: AWS credentials not found. Enabling demo mode.")
                self.demo_mode = True
            except Exception as e:
                print(f"Error initializing AWS session: {e}")
                sys.exit(1)
    
    def _generate_demo_data(self) -> Dict:
        """Generate realistic sample DynamoDB data for demo mode."""
        return {
            'tables': [
                {
                    'TableName': 'user-sessions',
                    'TableStatus': 'ACTIVE',
                    'CreationDateTime': datetime(2024, 1, 15, 10, 30, 0),
                    'ItemCount': 1500000,
                    'TableSizeBytes': 12884901888,  # 12 GB
                    'BillingModeSummary': {
                        'BillingMode': 'PAY_PER_REQUEST'
                    },
                    'AttributeDefinitions': [
                        {'AttributeName': 'session_id', 'AttributeType': 'S'},
                        {'AttributeName': 'user_id', 'AttributeType': 'S'},
                        {'AttributeName': 'created_at', 'AttributeType': 'N'}
                    ],
                    'KeySchema': [
                        {'AttributeName': 'session_id', 'KeyType': 'HASH'},
                        {'AttributeName': 'created_at', 'KeyType': 'RANGE'}
                    ],
                    'Tags': [
                        {'Key': 'Environment', 'Value': 'production'},
                        {'Key': 'Team', 'Value': 'backend'},
                        {'Key': 'Name', 'Value': 'user-sessions'}
                    ],
                    'Reads': 8500000,  # 8.5M reads
                    'Writes': 2000000,  # 2M writes
                    'Driver': 'Session activity'
                },
                {
                    'TableName': 'order-events',
                    'TableStatus': 'ACTIVE',
                    'CreationDateTime': datetime(2024, 2, 1, 14, 20, 0),
                    'ItemCount': 850000,
                    'TableSizeBytes': 4294967296,  # 4 GB
                    'BillingModeSummary': {
                        'BillingMode': 'PAY_PER_REQUEST'
                    },
                    'AttributeDefinitions': [
                        {'AttributeName': 'event_id', 'AttributeType': 'S'},
                        {'AttributeName': 'order_id', 'AttributeType': 'S'},
                        {'AttributeName': 'timestamp', 'AttributeType': 'N'}
                    ],
                    'KeySchema': [
                        {'AttributeName': 'event_id', 'KeyType': 'HASH'},
                        {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
                    ],
                    'Tags': [
                        {'Key': 'Environment', 'Value': 'production'},
                        {'Key': 'Team', 'Value': 'events'},
                        {'Key': 'Name', 'Value': 'order-events'}
                    ],
                    'Reads': 3200000,  # 3.2M reads
                    'Writes': 4800000,  # 4.8M writes
                    'Driver': 'Order processing'
                },
                {
                    'TableName': 'product-catalog',
                    'TableStatus': 'ACTIVE',
                    'CreationDateTime': datetime(2023, 11, 20, 8, 45, 0),
                    'ItemCount': 50000,
                    'TableSizeBytes': 2147483648,  # 2 GB
                    'BillingModeSummary': {
                        'BillingMode': 'PROVISIONED'
                    },
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 100,
                        'WriteCapacityUnits': 50
                    },
                    'AttributeDefinitions': [
                        {'AttributeName': 'product_id', 'AttributeType': 'S'},
                        {'AttributeName': 'category', 'AttributeType': 'S'}
                    ],
                    'KeySchema': [
                        {'AttributeName': 'product_id', 'KeyType': 'HASH'}
                    ],
                    'Tags': [
                        {'Key': 'Environment', 'Value': 'production'},
                        {'Key': 'Team', 'Value': 'catalog'},
                        {'Key': 'Name', 'Value': 'product-catalog'}
                    ],
                    'Reads': 1500000,  # 1.5M reads
                    'Writes': 250000,  # 250K writes
                    'Driver': 'Product lookups'
                },
                {
                    'TableName': 'audit-logs',
                    'TableStatus': 'ACTIVE',
                    'CreationDateTime': datetime(2024, 1, 1, 0, 0, 0),
                    'ItemCount': 12000000,
                    'TableSizeBytes': 64424509440,  # 60 GB
                    'BillingModeSummary': {
                        'BillingMode': 'PAY_PER_REQUEST'
                    },
                    'AttributeDefinitions': [
                        {'AttributeName': 'log_id', 'AttributeType': 'S'},
                        {'AttributeName': 'timestamp', 'AttributeType': 'N'},
                        {'AttributeName': 'service', 'AttributeType': 'S'}
                    ],
                    'KeySchema': [
                        {'AttributeName': 'log_id', 'KeyType': 'HASH'},
                        {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
                    ],
                    'Tags': [
                        {'Key': 'Environment', 'Value': 'production'},
                        {'Key': 'Team', 'Value': 'compliance'},
                        {'Key': 'Name', 'Value': 'audit-logs'}
                    ],
                    'Reads': 800000,  # 800K reads
                    'Writes': 2400000,  # 2.4M writes
                    'Driver': 'Data retention'
                }
            ]
        }
    
    def get_dynamodb_tables(self) -> List[Dict]:
        """
        Get all DynamoDB tables in the region.
        
        Returns:
            List of DynamoDB table information
        """
        if self.demo_mode:
            return self.demo_data['tables']
        
        try:
            response = self.dynamodb_client.list_tables()
            
            tables = []
            for table_name in response.get('TableNames', []):
                # Get detailed table information
                table_info = self.dynamodb_client.describe_table(TableName=table_name)
                
                # Only include active tables
                if table_info['Table']['TableStatus'] == 'ACTIVE':
                    tables.append(table_info['Table'])
            
            return tables
        except ClientError as e:
            print(f"Error retrieving DynamoDB tables: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error retrieving DynamoDB tables: {e}")
            return []
    
    def get_table_metrics(self, table_name: str, days: int = 30) -> Optional[Dict]:
        """
        Get CloudWatch metrics for a DynamoDB table.
        
        Args:
            table_name: Name of the DynamoDB table
            days: Number of days to look back for metrics
            
        Returns:
            Dictionary with metrics or None if unavailable
        """
        if self.demo_mode:
            # Return demo metrics
            for table in self.demo_data['tables']:
                if table['TableName'] == table_name:
                    return {
                        'Reads': table['Reads'],
                        'Writes': table['Writes']
                    }
            return None
        
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            metrics = {}
            
            # Get ConsumedReadCapacityUnits
            reads_response = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/DynamoDB',
                MetricName='ConsumedReadCapacityUnits',
                Dimensions=[
                    {
                        'Name': 'TableName',
                        'Value': table_name
                    }
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=86400,  # 1 day
                Statistics=['Sum']
            )
            
            # Get ConsumedWriteCapacityUnits
            writes_response = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/DynamoDB',
                MetricName='ConsumedWriteCapacityUnits',
                Dimensions=[
                    {
                        'Name': 'TableName',
                        'Value': table_name
                    }
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=86400,  # 1 day
                Statistics=['Sum']
            )
            
            # Calculate totals
            reads_data = reads_response.get('Datapoints', [])
            writes_data = writes_response.get('Datapoints', [])
            
            total_reads = sum(dp['Sum'] for dp in reads_data)
            total_writes = sum(dp['Sum'] for dp in writes_data)
            
            # Convert capacity units to request counts
            # For strongly consistent reads: 1 read capacity unit = 1 read (4KB)
            # For eventually consistent reads: 1 read capacity unit = 2 reads (4KB each)
            # For writes: 1 write capacity unit = 1 write (1KB)
            # We'll use average assumptions
            
            estimated_reads = int(total_reads * 1.5)  # Assuming mix of consistent reads
            estimated_writes = int(total_writes)
            
            return {
                'Reads': estimated_reads,
                'Writes': estimated_writes
            }
            
        except ClientError as e:
            print(f"Error retrieving metrics for {table_name}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error retrieving metrics for {table_name}: {e}")
            return None
    
    def calculate_table_cost(self, table: Dict, metrics: Dict) -> Dict:
        """
        Calculate estimated monthly cost for a DynamoDB table.
        
        Args:
            table: DynamoDB table configuration
            metrics: CloudWatch metrics for the table
            
        Returns:
            Cost breakdown dictionary
        """
        reads = metrics['Reads']
        writes = metrics['Writes']
        storage_gb = table.get('TableSizeBytes', 0) / (1024 * 1024 * 1024)  # Convert bytes to GB
        
        # Calculate costs
        read_cost = (reads / 1000000) * self.DYNAMODB_PRICING['read_cost_per_million']
        write_cost = (writes / 1000000) * self.DYNAMODB_PRICING['write_cost_per_million']
        storage_cost = storage_gb * self.DYNAMODB_PRICING['storage_cost_per_gb']
        
        total_cost = read_cost + write_cost + storage_cost
        total_requests = reads + writes
        
        # Calculate cost per 1,000 requests
        cost_per_1000_requests = (total_cost / total_requests * 1000) if total_requests > 0 else 0
        
        return {
            'read_cost': read_cost,
            'write_cost': write_cost,
            'storage_cost': storage_cost,
            'total_cost': total_cost,
            'cost_per_1000_requests': cost_per_1000_requests,
            'reads': reads,
            'writes': writes,
            'storage_gb': storage_gb,
            'total_requests': total_requests
        }
    
    def identify_demand_driver(self, table: Dict, metrics: Dict, cost_analysis: Dict) -> str:
        """
        Identify the likely demand driver based on table characteristics and usage patterns.
        
        Args:
            table: DynamoDB table configuration
            metrics: CloudWatch metrics for the table
            cost_analysis: Cost analysis for the table
            
        Returns:
            Identified demand driver
        """
        table_name = table['TableName'].lower()
        item_count = table.get('ItemCount', 0)
        storage_gb = cost_analysis['storage_gb']
        reads = metrics['Reads']
        writes = metrics['Writes']
        total_requests = reads + writes
        
        # Calculate ratios
        read_ratio = reads / total_requests if total_requests > 0 else 0
        write_ratio = writes / total_requests if total_requests > 0 else 0
        reads_per_item = reads / item_count if item_count > 0 else 0
        writes_per_item = writes / item_count if item_count > 0 else 0
        
        # Analyze patterns to identify drivers
        if 'session' in table_name or 'cache' in table_name:
            return 'Session activity'
        elif 'order' in table_name or 'transaction' in table_name or 'event' in table_name:
            return 'Order processing'
        elif 'product' in table_name or 'catalog' in table_name or 'inventory' in table_name:
            return 'Product lookups'
        elif 'user' in table_name or 'profile' in table_name or 'account' in table_name:
            return 'User data'
        elif 'audit' in table_name or 'log' in table_name or 'history' in table_name:
            return 'Data retention'
        elif 'config' in table_name or 'setting' in table_name:
            return 'Configuration data'
        elif storage_gb > 50:
            return 'Data retention'
        elif read_ratio > 0.8:
            return 'API traffic'
        elif write_ratio > 0.6:
            return 'Event processing'
        elif writes_per_item > 2:
            return 'High churn data'
        elif reads_per_item > 10:
            return 'Frequent lookups'
        else:
            return 'General workload'
    
    def analyze_dynamodb_drivers(self) -> Dict:
        """
        Analyze all DynamoDB tables to identify demand drivers.
        
        Returns:
            Analysis results with driver information
        """
        print("Analyzing DynamoDB tables for demand drivers...")
        
        if self.demo_mode:
            print("Running in DEMO MODE with sample data")
        
        tables = self.get_dynamodb_tables()
        driver_analysis = []
        
        for table in tables:
            table_name = table['TableName']
            
            # Get metrics
            metrics = self.get_table_metrics(table_name)
            
            if not metrics:
                print(f"Warning: No metrics available for {table_name}")
                continue
            
            # Calculate costs
            cost_analysis = self.calculate_table_cost(table, metrics)
            
            # Identify demand driver
            driver = self.identify_demand_driver(table, metrics, cost_analysis)
            
            analysis = {
                'table_name': table_name,
                'table_status': table['TableStatus'],
                'creation_date': table.get('CreationDateTime'),
                'item_count': table.get('ItemCount', 0),
                'table_size_bytes': table.get('TableSizeBytes', 0),
                'billing_mode': table.get('BillingModeSummary', {}).get('BillingMode', 'UNKNOWN'),
                'provisioned_throughput': table.get('ProvisionedThroughput', {}),
                'tags': table.get('Tags', []),
                'metrics': metrics,
                'cost_analysis': cost_analysis,
                'demand_driver': driver,
                'usage_patterns': {
                    'read_ratio': metrics['Reads'] / (metrics['Reads'] + metrics['Writes']) if (metrics['Reads'] + metrics['Writes']) > 0 else 0,
                    'write_ratio': metrics['Writes'] / (metrics['Reads'] + metrics['Writes']) if (metrics['Reads'] + metrics['Writes']) > 0 else 0,
                    'reads_per_item': metrics['Reads'] / table.get('ItemCount', 1) if table.get('ItemCount', 0) > 0 else 0,
                    'writes_per_item': metrics['Writes'] / table.get('ItemCount', 1) if table.get('ItemCount', 0) > 0 else 0
                }
            }
            
            driver_analysis.append(analysis)
        
        # Calculate summary
        total_tables = len(driver_analysis)
        total_reads = sum(analysis['metrics']['Reads'] for analysis in driver_analysis)
        total_writes = sum(analysis['metrics']['Writes'] for analysis in driver_analysis)
        total_storage = sum(analysis['cost_analysis']['storage_gb'] for analysis in driver_analysis)
        total_cost = sum(analysis['cost_analysis']['total_cost'] for analysis in driver_analysis)
        
        # Group by demand drivers
        driver_groups = {}
        for analysis in driver_analysis:
            driver = analysis['demand_driver']
            if driver not in driver_groups:
                driver_groups[driver] = {
                    'tables': [],
                    'total_reads': 0,
                    'total_writes': 0,
                    'total_cost': 0,
                    'total_storage': 0
                }
            driver_groups[driver]['tables'].append(analysis['table_name'])
            driver_groups[driver]['total_reads'] += analysis['metrics']['Reads']
            driver_groups[driver]['total_writes'] += analysis['metrics']['Writes']
            driver_groups[driver]['total_cost'] += analysis['cost_analysis']['total_cost']
            driver_groups[driver]['total_storage'] += analysis['cost_analysis']['storage_gb']
        
        results = {
            'scan_time': datetime.now().isoformat(),
            'region': self.region,
            'demo_mode': self.demo_mode,
            'analysis_period_days': 30,
            'dynamodb_pricing': self.DYNAMODB_PRICING,
            'driver_analysis': driver_analysis,
            'driver_groups': driver_groups,
            'summary': {
                'total_tables_analyzed': total_tables,
                'total_reads': total_reads,
                'total_writes': total_writes,
                'total_storage_gb': total_storage,
                'total_estimated_monthly_cost': total_cost,
                'unique_demand_drivers': len(driver_groups),
                'average_cost_per_table': total_cost / total_tables if total_tables > 0 else 0
            }
        }
        
        return results
    
    def print_summary(self, results: Dict):
        """Print a readable summary of the analysis."""
        summary = results['summary']
        driver_groups = results['driver_groups']
        driver_analysis = results['driver_analysis']
        
        print(f"\nDynamoDB Driver Analysis")
        print(f"========================")
        print(f"Region: {results['region']}")
        print(f"Scan Time: {results['scan_time']}")
        print(f"Analysis Period: {results['analysis_period_days']} days")
        if results['demo_mode']:
            print(f"Mode: DEMO (using sample data)")
        
        print(f"\n--- Summary ---")
        print(f"Total Tables Analyzed: {summary['total_tables_analyzed']}")
        print(f"Total Reads: {summary['total_reads']:,}")
        print(f"Total Writes: {summary['total_writes']:,}")
        print(f"Total Storage: {summary['total_storage_gb']:.1f} GB")
        print(f"Estimated Monthly Cost: ${summary['total_estimated_monthly_cost']:.2f}")
        print(f"Unique Demand Drivers: {summary['unique_demand_drivers']}")
        print(f"Average Cost per Table: ${summary['average_cost_per_table']:.2f}")
        
        print(f"\n--- Demand Drivers ---")
        # Sort drivers by total cost (descending)
        sorted_drivers = sorted(driver_groups.items(), key=lambda x: x[1]['total_cost'], reverse=True)
        
        for driver, data in sorted_drivers:
            print(f"\n{driver}:")
            print(f"  Tables: {', '.join(data['tables'])}")
            print(f"  Reads: {data['total_reads']:,}")
            print(f"  Writes: {data['total_writes']:,}")
            print(f"  Storage: {data['total_storage']:.1f} GB")
            print(f"  Cost: ${data['total_cost']:.2f}")
        
        print(f"\n--- Table Details ---")
        # Sort tables by cost (descending)
        sorted_tables = sorted(driver_analysis, key=lambda x: x['cost_analysis']['total_cost'], reverse=True)
        
        for i, analysis in enumerate(sorted_tables, 1):
            print(f"\n{i}. {analysis['table_name']}")
            print(f"   Status: {analysis['table_status']}")
            print(f"   Items: {analysis['item_count']:,}")
            print(f"   Storage: {analysis['cost_analysis']['storage_gb']:.1f} GB")
            print(f"   Reads: {analysis['metrics']['Reads']:,}")
            print(f"   Writes: {analysis['metrics']['Writes']:,}")
            print(f"   Estimated Monthly Cost: ${analysis['cost_analysis']['total_cost']:.2f}")
            print(f"   Cost per 1,000 requests: ${analysis['cost_analysis']['cost_per_1000_requests']:.4f}")
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
    """Main function to run the DynamoDB driver detector."""
    parser = argparse.ArgumentParser(
        description='Analyze DynamoDB tables to identify workload demand drivers',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python dynamodb_driver_detector.py
  python dynamodb_driver_detector.py --region us-west-2 --output dynamodb_report.json
  python dynamodb_driver_detector.py --demo --output demo_dynamodb.json
  python dynamodb_driver_detector.py --profile my-aws-profile --region eu-west-1
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
    
    print("DynamoDB Driver Detector")
    print(f"Region: {args.region}")
    
    # Initialize detector
    detector = DynamoDBDriverDetector(
        region=args.region,
        profile_name=args.profile,
        demo_mode=args.demo
    )
    
    # Analyze DynamoDB tables
    results = detector.analyze_dynamodb_drivers()
    
    # Print summary
    detector.print_summary(results)
    
    # Export to JSON if output file specified
    if args.output:
        detector.export_to_json(results, args.output)
    
    # Exit with appropriate code
    total_tables = results['summary']['total_tables_analyzed']
    
    if total_tables > 0:
        print(f"\nAnalyzed {total_tables} DynamoDB tables with total estimated cost of ${results['summary']['total_estimated_monthly_cost']:.2f}/month")
        sys.exit(0)  # Success for analysis
    else:
        print("\nNo DynamoDB tables found in the specified region")
        sys.exit(0)  # Still success, just no data


if __name__ == '__main__':
    main()
