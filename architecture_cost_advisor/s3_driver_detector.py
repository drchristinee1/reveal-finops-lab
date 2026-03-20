#!/usr/bin/env python3
"""
AWS S3 Driver Detector

This script analyzes S3 buckets to identify storage demand drivers
that influence cloud costs through usage patterns and metrics.
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import boto3
from botocore.exceptions import ClientError, NoCredentialsError, EndpointConnectionError


class S3DriverDetector:
    """Detects S3 storage demand drivers based on usage patterns."""
    
    # Simplified S3 pricing (actual prices vary by region)
    S3_PRICING = {
        'storage': {
            'standard': 0.023,  # $0.023 per GB
            'intelligent_tiering': 0.023,
            'infrequent_access': 0.0125,
            'onezone_ia': 0.01,
            'glacier': 0.004,
            'glacier_deep_archive': 0.00099
        },
        'requests': {
            'get': 0.0004,  # $0.0004 per 1,000 GET requests
            'put': 0.005,   # $0.005 per 1,000 PUT requests
            'list': 0.005,  # $0.005 per 1,000 LIST requests
            'restore': 0.01  # $0.01 per GB restored
        }
    }
    
    def __init__(self, region: str = 'us-east-1', profile_name: Optional[str] = None, demo_mode: bool = False):
        """Initialize the S3 driver detector."""
        self.region = region
        self.demo_mode = demo_mode
        self.demo_data = self._generate_demo_data()
        
        if not demo_mode:
            try:
                session = boto3.Session(profile_name=profile_name)
                self.s3_client = session.client('s3', region_name=region)
                self.cloudwatch_client = session.client('cloudwatch', region_name=region)
            except NoCredentialsError:
                print("Warning: AWS credentials not found. Enabling demo mode.")
                self.demo_mode = True
            except Exception as e:
                print(f"Error initializing AWS session: {e}")
                sys.exit(1)
    
    def _generate_demo_data(self) -> Dict:
        """Generate realistic sample S3 data for demo mode."""
        return {
            'buckets': [
                {
                    'Name': 'user-uploads',
                    'CreationDate': datetime(2024, 1, 15, 10, 30, 0),
                    'Region': 'us-east-1',
                    'StorageClass': 'STANDARD',
                    'Size': 1288490188800,  # 1.2 TB in bytes
                    'ObjectCount': 2500000,
                    'Tags': [
                        {'Key': 'Environment', 'Value': 'production'},
                        {'Key': 'Team', 'Value': 'backend'},
                        {'Key': 'Purpose', 'Value': 'user-content'}
                    ],
                    'Metrics': {
                        'GETRequests': 5000000,
                        'PUTRequests': 500000,
                        'LISTRequests': 50000
                    },
                    'Driver': 'Content delivery'
                },
                {
                    'Name': 'backup-archive',
                    'CreationDate': datetime(2023, 6, 1, 14, 20, 0),
                    'Region': 'us-east-1',
                    'StorageClass': 'GLACIER',
                    'Size': 5497558138880,  # 5 TB in bytes
                    'ObjectCount': 100000,
                    'Tags': [
                        {'Key': 'Environment', 'Value': 'production'},
                        {'Key': 'Team', 'Value': 'ops'},
                        {'Key': 'Purpose', 'Value': 'backup'}
                    ],
                    'Metrics': {
                        'GETRequests': 10000,
                        'PUTRequests': 50000,
                        'LISTRequests': 1000
                    },
                    'Driver': 'Archival storage'
                },
                {
                    'Name': 'data-lake-raw',
                    'CreationDate': datetime(2024, 2, 10, 8, 45, 0),
                    'Region': 'us-east-1',
                    'StorageClass': 'INTELLIGENT_TIERING',
                    'Size': 2147483648000,  # 2 TB in bytes
                    'ObjectCount': 500000,
                    'Tags': [
                        {'Key': 'Environment', 'Value': 'production'},
                        {'Key': 'Team', 'Value': 'data'},
                        {'Key': 'Purpose', 'Value': 'analytics'}
                    ],
                    'Metrics': {
                        'GETRequests': 2000000,
                        'PUTRequests': 2000000,
                        'LISTRequests': 200000
                    },
                    'Driver': 'Data ingestion'
                },
                {
                    'Name': 'static-assets',
                    'CreationDate': datetime(2023, 12, 20, 16, 0, 0),
                    'Region': 'us-east-1',
                    'StorageClass': 'STANDARD',
                    'Size': 107374182400,  # 100 GB in bytes
                    'ObjectCount': 50000,
                    'Tags': [
                        {'Key': 'Environment', 'Value': 'production'},
                        {'Key': 'Team', 'Value': 'frontend'},
                        {'Key': 'Purpose', 'Value': 'cdn'}
                    ],
                    'Metrics': {
                        'GETRequests': 10000000,
                        'PUTRequests': 10000,
                        'LISTRequests': 10000
                    },
                    'Driver': 'CDN content'
                }
            ]
        }
    
    def get_s3_buckets(self) -> List[Dict]:
        """
        Get all S3 buckets in the region.
        
        Returns:
            List of S3 bucket information
        """
        if self.demo_mode:
            return self.demo_data['buckets']
        
        try:
            response = self.s3_client.list_buckets()
            
            buckets = []
            for bucket in response.get('Buckets', []):
                bucket_name = bucket['Name']
                
                # Get bucket location
                try:
                    location_response = self.s3_client.get_bucket_location(Bucket=bucket_name)
                    bucket_region = location_response.get('LocationConstraint') or 'us-east-1'
                    
                    # Only include buckets in the specified region
                    if bucket_region == self.region:
                        # Get additional bucket info
                        bucket_info = self._get_bucket_details(bucket_name)
                        bucket_info.update(bucket)
                        buckets.append(bucket_info)
                except ClientError as e:
                    print(f"Warning: Could not get location for bucket {bucket_name}: {e}")
                    continue
            
            return buckets
        except ClientError as e:
            print(f"Error retrieving S3 buckets: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error retrieving S3 buckets: {e}")
            return []
    
    def _get_bucket_details(self, bucket_name: str) -> Dict:
        """
        Get detailed information about a specific bucket.
        
        Args:
            bucket_name: Name of the S3 bucket
            
        Returns:
            Dictionary with bucket details
        """
        try:
            # Get bucket tags
            tags = []
            try:
                tag_response = self.s3_client.get_bucket_tagging(Bucket=bucket_name)
                tags = tag_response.get('TagSet', [])
            except ClientError:
                # Bucket might not have tags
                pass
            
            # Get bucket metrics (CloudWatch)
            metrics = self.get_bucket_metrics(bucket_name)
            
            # Get storage info (simplified - in real implementation would use CloudWatch StorageMetrics)
            storage_info = self.get_bucket_storage_info(bucket_name)
            
            return {
                'Tags': tags,
                'Metrics': metrics,
                'StorageClass': storage_info.get('StorageClass', 'STANDARD'),
                'Size': storage_info.get('Size', 0),
                'ObjectCount': storage_info.get('ObjectCount', 0)
            }
            
        except ClientError as e:
            print(f"Error getting details for bucket {bucket_name}: {e}")
            return {
                'Tags': [],
                'Metrics': {'GETRequests': 0, 'PUTRequests': 0, 'LISTRequests': 0},
                'StorageClass': 'STANDARD',
                'Size': 0,
                'ObjectCount': 0
            }
    
    def get_bucket_storage_info(self, bucket_name: str) -> Dict:
        """
        Get storage information for a bucket.
        
        Args:
            bucket_name: Name of the S3 bucket
            
        Returns:
            Dictionary with storage information
        """
        if self.demo_mode:
            # Return demo storage info
            for bucket in self.demo_data['buckets']:
                if bucket['Name'] == bucket_name:
                    return {
                        'StorageClass': bucket['StorageClass'],
                        'Size': bucket['Size'],
                        'ObjectCount': bucket['ObjectCount']
                    }
            return {'StorageClass': 'STANDARD', 'Size': 0, 'ObjectCount': 0}
        
        try:
            # In a real implementation, this would use CloudWatch StorageMetrics
            # For demo purposes, we'll return estimated values
            return {
                'StorageClass': 'STANDARD',
                'Size': 1073741824,  # 1 GB default
                'ObjectCount': 1000
            }
        except Exception as e:
            print(f"Error getting storage info for {bucket_name}: {e}")
            return {'StorageClass': 'STANDARD', 'Size': 0, 'ObjectCount': 0}
    
    def get_bucket_metrics(self, bucket_name: str, days: int = 30) -> Optional[Dict]:
        """
        Get CloudWatch metrics for an S3 bucket.
        
        Args:
            bucket_name: Name of the S3 bucket
            days: Number of days to look back for metrics
            
        Returns:
            Dictionary with metrics or None if unavailable
        """
        if self.demo_mode:
            # Return demo metrics
            for bucket in self.demo_data['buckets']:
                if bucket['Name'] == bucket_name:
                    return bucket['Metrics']
            return None
        
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            metrics = {}
            
            # Get AllRequests (includes GET, PUT, LIST, etc.)
            requests_response = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/S3',
                MetricName='AllRequests',
                Dimensions=[
                    {
                        'Name': 'BucketName',
                        'Value': bucket_name
                    }
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=86400,  # 1 day
                Statistics=['Sum']
            )
            
            # Calculate totals (simplified - in real implementation would separate by request type)
            requests_data = requests_response.get('Datapoints', [])
            total_requests = sum(dp['Sum'] for dp in requests_data)
            
            # Estimate request distribution (70% GET, 20% PUT, 10% LIST)
            estimated_get = int(total_requests * 0.7)
            estimated_put = int(total_requests * 0.2)
            estimated_list = int(total_requests * 0.1)
            
            return {
                'GETRequests': estimated_get,
                'PUTRequests': estimated_put,
                'LISTRequests': estimated_list
            }
            
        except ClientError as e:
            print(f"Error retrieving metrics for {bucket_name}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error retrieving metrics for {bucket_name}: {e}")
            return None
    
    def calculate_bucket_cost(self, bucket: Dict, metrics: Dict) -> Dict:
        """
        Calculate estimated monthly cost for an S3 bucket.
        
        Args:
            bucket: S3 bucket configuration
            metrics: CloudWatch metrics for the bucket
            
        Returns:
            Cost breakdown dictionary
        """
        storage_class = bucket['StorageClass']
        storage_size_gb = bucket['Size'] / (1024 * 1024 * 1024)  # Convert bytes to GB
        
        get_requests = metrics['GETRequests']
        put_requests = metrics['PUTRequests']
        list_requests = metrics['LISTRequests']
        
        # Calculate storage cost
        storage_cost_per_gb = self.S3_PRICING['storage'].get(storage_class.lower(), self.S3_PRICING['storage']['standard'])
        storage_cost = storage_size_gb * storage_cost_per_gb
        
        # Calculate request costs
        get_cost = (get_requests / 1000) * self.S3_PRICING['requests']['get']
        put_cost = (put_requests / 1000) * self.S3_PRICING['requests']['put']
        list_cost = (list_requests / 1000) * self.S3_PRICING['requests']['list']
        
        total_request_cost = get_cost + put_cost + list_cost
        total_monthly_cost = storage_cost + total_request_cost
        
        return {
            'storage_cost': storage_cost,
            'get_cost': get_cost,
            'put_cost': put_cost,
            'list_cost': list_cost,
            'total_request_cost': total_request_cost,
            'total_monthly_cost': total_monthly_cost,
            'storage_size_gb': storage_size_gb,
            'storage_class': storage_class
        }
    
    def identify_demand_driver(self, bucket: Dict, metrics: Dict, cost_analysis: Dict) -> str:
        """
        Identify the likely demand driver based on bucket characteristics and usage patterns.
        
        Args:
            bucket: S3 bucket configuration
            metrics: CloudWatch metrics for the bucket
            cost_analysis: Cost analysis for the bucket
            
        Returns:
            Identified demand driver
        """
        bucket_name = bucket['Name'].lower()
        storage_class = bucket['StorageClass']
        storage_size_gb = cost_analysis['storage_size_gb']
        object_count = bucket['ObjectCount']
        
        get_requests = metrics['GETRequests']
        put_requests = metrics['PUTRequests']
        total_requests = get_requests + put_requests
        
        # Calculate ratios
        get_ratio = get_requests / total_requests if total_requests > 0 else 0
        put_ratio = put_requests / total_requests if total_requests > 0 else 0
        
        # Get tags for analysis
        tags = {tag['Key']: tag['Value'] for tag in bucket.get('Tags', [])}
        purpose = tags.get('Purpose', '').lower()
        team = tags.get('Team', '').lower()
        
        # Analyze patterns to identify drivers
        if 'upload' in bucket_name or 'upload' in purpose:
            return 'User uploads'
        elif 'backup' in bucket_name or 'backup' in purpose or 'archive' in purpose:
            return 'Archival storage'
        elif 'static' in bucket_name or 'asset' in bucket_name or 'cdn' in purpose:
            return 'CDN content'
        elif 'data' in bucket_name or 'lake' in bucket_name or 'analytics' in purpose:
            return 'Data ingestion'
        elif 'log' in bucket_name or 'log' in purpose:
            return 'Log storage'
        elif 'media' in bucket_name or 'video' in bucket_name or 'image' in bucket_name:
            return 'Media content'
        elif storage_class in ['GLACIER', 'DEEP_ARCHIVE']:
            return 'Cold storage'
        elif storage_size_gb > 1000 and get_requests < 10000:
            return 'Long-term retention'
        elif get_requests > 1000000:
            return 'Content delivery'
        elif put_requests > 1000000:
            return 'Data ingestion'
        elif get_ratio > 0.8:
            return 'Read-heavy workload'
        elif put_ratio > 0.6:
            return 'Write-heavy workload'
        elif total_requests < 1000:
            return 'Infrequent access'
        else:
            return 'General storage'
    
    def calculate_optimization_signals(self, bucket: Dict, metrics: Dict, cost_analysis: Dict) -> List[str]:
        """
        Calculate optimization signals for a bucket.
        
        Args:
            bucket: S3 bucket configuration
            metrics: CloudWatch metrics for the bucket
            cost_analysis: Cost analysis for the bucket
            
        Returns:
            List of optimization signals
        """
        signals = []
        bucket_name = bucket['Name'].lower()
        storage_class = bucket['StorageClass']
        storage_size_gb = cost_analysis['storage_size_gb']
        object_count = bucket['ObjectCount']
        
        get_requests = metrics['GETRequests']
        put_requests = metrics['PUTRequests']
        total_requests = get_requests + put_requests
        
        # Calculate ratios
        get_ratio = get_requests / total_requests if total_requests > 0 else 0
        put_ratio = put_requests / total_requests if total_requests > 0 else 0
        
        # Get tags for analysis
        tags = {tag['Key']: tag['Value'] for tag in bucket.get('Tags', [])}
        purpose = tags.get('Purpose', '').lower()
        
        # Storage optimization signals
        if storage_class == 'STANDARD' and get_requests < 1000:
            signals.append("Consider moving to Infrequent Access or Glacier")
        elif storage_class == 'STANDARD' and storage_size_gb > 1000:
            signals.append("Consider Intelligent Tiering for cost optimization")
        elif storage_class == 'GLACIER' and get_requests > 10000:
            signals.append("Frequent access to Glacier storage - consider lifecycle policy")
        
        # Request optimization signals
        if get_requests > 10000000:
            signals.append("High GET requests - consider caching or CDN")
        elif put_requests > 1000000:
            signals.append("High PUT requests - consider multipart upload optimization")
        
        # Lifecycle optimization signals
        if 'backup' in purpose and storage_class == 'STANDARD':
            signals.append("Implement lifecycle policy for backup storage")
        elif 'log' in purpose and storage_size_gb > 500:
            signals.append("Consider log rotation and archival policies")
        
        # Size optimization signals
        if storage_size_gb > 10000:
            signals.append("Large bucket - consider data partitioning")
        elif object_count > 1000000 and storage_class == 'STANDARD':
            signals.append("Many objects - consider lifecycle management")
        
        # Access pattern signals
        if get_ratio > 0.9 and put_ratio < 0.1:
            signals.append("Read-only pattern - optimize for GET operations")
        elif put_ratio > 0.8:
            signals.append("Write-heavy pattern - optimize for PUT operations")
        
        return signals
    
    def analyze_s3_drivers(self) -> Dict:
        """
        Analyze all S3 buckets to identify demand drivers.
        
        Returns:
            Analysis results with driver information
        """
        print("Analyzing S3 buckets for demand drivers...")
        
        if self.demo_mode:
            print("Running in DEMO MODE with sample data")
        
        buckets = self.get_s3_buckets()
        driver_analysis = []
        
        for bucket in buckets:
            bucket_name = bucket['Name']
            
            # Get metrics
            metrics = self.get_bucket_metrics(bucket_name)
            
            if not metrics:
                print(f"Warning: No metrics available for {bucket_name}")
                continue
            
            # Calculate costs
            cost_analysis = self.calculate_bucket_cost(bucket, metrics)
            
            # Identify demand driver
            driver = self.identify_demand_driver(bucket, metrics, cost_analysis)
            
            # Calculate optimization signals
            optimization_signals = self.calculate_optimization_signals(bucket, metrics, cost_analysis)
            
            analysis = {
                'bucket_name': bucket_name,
                'creation_date': bucket['CreationDate'],
                'region': bucket.get('Region', self.region),
                'storage_class': bucket['StorageClass'],
                'size_bytes': bucket['Size'],
                'object_count': bucket['ObjectCount'],
                'tags': bucket.get('Tags', []),
                'metrics': metrics,
                'cost_analysis': cost_analysis,
                'demand_driver': driver,
                'optimization_signals': optimization_signals,
                'usage_patterns': {
                    'get_requests': metrics['GETRequests'],
                    'put_requests': metrics['PUTRequests'],
                    'list_requests': metrics['LISTRequests'],
                    'total_requests': metrics['GETRequests'] + metrics['PUTRequests'] + metrics['LISTRequests'],
                    'get_ratio': metrics['GETRequests'] / (metrics['GETRequests'] + metrics['PUTRequests']) if (metrics['GETRequests'] + metrics['PUTRequests']) > 0 else 0,
                    'put_ratio': metrics['PUTRequests'] / (metrics['GETRequests'] + metrics['PUTRequests']) if (metrics['GETRequests'] + metrics['PUTRequests']) > 0 else 0,
                    'storage_size_gb': cost_analysis['storage_size_gb'],
                    'objects_per_gb': bucket['ObjectCount'] / cost_analysis['storage_size_gb'] if cost_analysis['storage_size_gb'] > 0 else 0
                }
            }
            
            driver_analysis.append(analysis)
        
        # Calculate summary
        total_buckets = len(driver_analysis)
        total_storage_gb = sum(analysis['cost_analysis']['storage_size_gb'] for analysis in driver_analysis)
        total_objects = sum(analysis['object_count'] for analysis in driver_analysis)
        total_monthly_cost = sum(analysis['cost_analysis']['total_monthly_cost'] for analysis in driver_analysis)
        
        # Group by demand drivers
        driver_groups = {}
        for analysis in driver_analysis:
            driver = analysis['demand_driver']
            if driver not in driver_groups:
                driver_groups[driver] = {
                    'buckets': [],
                    'total_monthly_cost': 0,
                    'total_storage_gb': 0,
                    'total_objects': 0,
                    'total_get_requests': 0,
                    'total_put_requests': 0
                }
            driver_groups[driver]['buckets'].append(analysis['bucket_name'])
            driver_groups[driver]['total_monthly_cost'] += analysis['cost_analysis']['total_monthly_cost']
            driver_groups[driver]['total_storage_gb'] += analysis['cost_analysis']['storage_size_gb']
            driver_groups[driver]['total_objects'] += analysis['object_count']
            driver_groups[driver]['total_get_requests'] += analysis['usage_patterns']['get_requests']
            driver_groups[driver]['total_put_requests'] += analysis['usage_patterns']['put_requests']
        
        results = {
            'scan_time': datetime.now().isoformat(),
            'region': self.region,
            'demo_mode': self.demo_mode,
            'analysis_period_days': 30,
            's3_pricing': self.S3_PRICING,
            'driver_analysis': driver_analysis,
            'driver_groups': driver_groups,
            'summary': {
                'total_buckets_analyzed': total_buckets,
                'total_storage_gb': total_storage_gb,
                'total_objects': total_objects,
                'total_monthly_cost': total_monthly_cost,
                'unique_demand_drivers': len(driver_groups),
                'average_cost_per_bucket': total_monthly_cost / total_buckets if total_buckets > 0 else 0
            }
        }
        
        return results
    
    def print_summary(self, results: Dict):
        """Print a readable summary of the analysis."""
        summary = results['summary']
        driver_groups = results['driver_groups']
        driver_analysis = results['driver_analysis']
        
        print(f"\nS3 Driver Analysis")
        print(f"===================")
        print(f"Region: {results['region']}")
        print(f"Scan Time: {results['scan_time']}")
        print(f"Analysis Period: {results['analysis_period_days']} days")
        if results['demo_mode']:
            print(f"Mode: DEMO (using sample data)")
        
        print(f"\n--- Summary ---")
        print(f"Total Buckets Analyzed: {summary['total_buckets_analyzed']}")
        print(f"Total Storage: {summary['total_storage_gb']:.1f} GB")
        print(f"Total Objects: {summary['total_objects']:,}")
        print(f"Total Monthly Cost: ${summary['total_monthly_cost']:.2f}")
        print(f"Unique Demand Drivers: {summary['unique_demand_drivers']}")
        print(f"Average Cost per Bucket: ${summary['average_cost_per_bucket']:.2f}")
        
        print(f"\n--- Demand Drivers ---")
        # Sort drivers by total cost (descending)
        sorted_drivers = sorted(driver_groups.items(), key=lambda x: x[1]['total_monthly_cost'], reverse=True)
        
        for driver, data in sorted_drivers:
            print(f"\n{driver}:")
            print(f"  Buckets: {', '.join(data['buckets'])}")
            print(f"  Monthly Cost: ${data['total_monthly_cost']:.2f}")
            print(f"  Storage: {data['total_storage_gb']:.1f} GB")
            print(f"  Objects: {data['total_objects']:,}")
            print(f"  GET Requests: {data['total_get_requests']:,}")
            print(f"  PUT Requests: {data['total_put_requests']:,}")
        
        print(f"\n--- Bucket Details ---")
        # Sort buckets by cost (descending)
        sorted_buckets = sorted(driver_analysis, key=lambda x: x['cost_analysis']['total_monthly_cost'], reverse=True)
        
        for i, analysis in enumerate(sorted_buckets, 1):
            print(f"\n{i}. {analysis['bucket_name']}")
            print(f"   Storage Class: {analysis['storage_class']}")
            print(f"   Storage: {analysis['usage_patterns']['storage_size_gb']:.1f} GB")
            print(f"   Objects: {analysis['object_count']:,}")
            print(f"   GET Requests: {analysis['usage_patterns']['get_requests']:,}")
            print(f"   PUT Requests: {analysis['usage_patterns']['put_requests']:,}")
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
    """Main function to run the S3 driver detector."""
    parser = argparse.ArgumentParser(
        description='Analyze S3 buckets to identify storage demand drivers',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python s3_driver_detector.py
  python s3_driver_detector.py --region us-west-2 --output s3_report.json
  python s3_driver_detector.py --demo --output demo_s3.json
  python s3_driver_detector.py --profile my-aws-profile --region eu-west-1
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
    
    print("S3 Driver Detector")
    print(f"Region: {args.region}")
    
    # Initialize detector
    detector = S3DriverDetector(
        region=args.region,
        profile_name=args.profile,
        demo_mode=args.demo
    )
    
    # Analyze S3 buckets
    results = detector.analyze_s3_drivers()
    
    # Print summary
    detector.print_summary(results)
    
    # Export to JSON if output file specified
    if args.output:
        detector.export_to_json(results, args.output)
    
    # Exit with appropriate code
    total_buckets = results['summary']['total_buckets_analyzed']
    
    if total_buckets > 0:
        print(f"\nAnalyzed {total_buckets} S3 buckets with total estimated cost of ${results['summary']['total_monthly_cost']:.2f}/month")
        sys.exit(0)  # Success for analysis
    else:
        print("\nNo S3 buckets found in the specified region")
        sys.exit(0)  # Still success, just no data


if __name__ == '__main__':
    main()
