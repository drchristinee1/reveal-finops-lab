#!/usr/bin/env python3
"""
AWS EC2 Rightsizing Detector

This script analyzes EC2 instances for rightsizing opportunities by identifying
instances with low CPU utilization and recommending smaller instance types.
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import boto3
from botocore.exceptions import ClientError, NoCredentialsError, EndpointConnectionError


class RightsizingDetector:
    """Detects EC2 rightsizing opportunities based on CPU utilization."""
    
    # Simplified pricing per hour (USD) - actual prices vary by region
    INSTANCE_PRICING = {
        # t3 family (burstable)
        't3.nano': 0.0052, 't3.micro': 0.0104, 't3.small': 0.0208,
        't3.medium': 0.0416, 't3.large': 0.0832, 't3.xlarge': 0.1664,
        't3.2xlarge': 0.3328,
        
        # t3a family (AMD burstable)
        't3a.nano': 0.0047, 't3a.micro': 0.0094, 't3a.small': 0.0188,
        't3a.medium': 0.0375, 't3a.large': 0.0750, 't3a.xlarge': 0.1500,
        't3a.2xlarge': 0.3000,
        
        # m5 family (general purpose)
        'm5.large': 0.096, 'm5.xlarge': 0.192, 'm5.2xlarge': 0.384,
        'm5.4xlarge': 0.768, 'm5.8xlarge': 1.536, 'm5.12xlarge': 2.304,
        'm5.16xlarge': 3.072, 'm5.24xlarge': 4.608,
        
        # m5a family (AMD general purpose)
        'm5a.large': 0.086, 'm5a.xlarge': 0.172, 'm5a.2xlarge': 0.344,
        'm5a.4xlarge': 0.688, 'm5a.8xlarge': 1.376, 'm5a.12xlarge': 2.064,
        'm5a.16xlarge': 2.752, 'm5a.24xlarge': 4.128,
        
        # c5 family (compute optimized)
        'c5.large': 0.085, 'c5.xlarge': 0.170, 'c5.2xlarge': 0.340,
        'c5.4xlarge': 0.680, 'c5.9xlarge': 1.530, 'c5.12xlarge': 2.040,
        'c5.18xlarge': 3.060, 'c5.24xlarge': 4.080,
        
        # c5a family (AMD compute optimized)
        'c5a.large': 0.079, 'c5a.xlarge': 0.158, 'c5a.2xlarge': 0.316,
        'c5a.4xlarge': 0.632, 'c5a.8xlarge': 1.264, 'c5a.12xlarge': 1.896,
        'c5a.16xlarge': 2.528, 'c5a.24xlarge': 3.792,
    }
    
    # Rightsizing mapping (current -> recommended)
    RIGHTSIZING_MAP = {
        # t3 family
        't3.large': ['t3.medium', 't3.small'],
        't3.xlarge': ['t3.large', 't3.medium'],
        't3.2xlarge': ['t3.xlarge', 't3.large'],
        't3.medium': ['t3.small', 't3.micro'],
        't3.small': ['t3.micro', 't3.nano'],
        
        # t3a family
        't3a.large': ['t3a.medium', 't3a.small'],
        't3a.xlarge': ['t3a.large', 't3a.medium'],
        't3a.2xlarge': ['t3a.xlarge', 't3a.large'],
        't3a.medium': ['t3a.small', 't3a.micro'],
        't3a.small': ['t3a.micro', 't3a.nano'],
        
        # m5 family
        'm5.large': ['t3.large', 't3.medium'],
        'm5.xlarge': ['m5.large', 't3.large'],
        'm5.2xlarge': ['m5.xlarge', 'm5.large'],
        'm5.4xlarge': ['m5.2xlarge', 'm5.xlarge'],
        'm5.8xlarge': ['m5.4xlarge', 'm5.2xlarge'],
        'm5.12xlarge': ['m5.8xlarge', 'm5.4xlarge'],
        'm5.16xlarge': ['m5.12xlarge', 'm5.8xlarge'],
        'm5.24xlarge': ['m5.16xlarge', 'm5.12xlarge'],
        
        # m5a family
        'm5a.large': ['t3a.large', 't3a.medium'],
        'm5a.xlarge': ['m5a.large', 't3a.large'],
        'm5a.2xlarge': ['m5a.xlarge', 'm5a.large'],
        'm5a.4xlarge': ['m5a.2xlarge', 'm5a.xlarge'],
        'm5a.8xlarge': ['m5a.4xlarge', 'm5a.2xlarge'],
        'm5a.12xlarge': ['m5a.8xlarge', 'm5a.4xlarge'],
        'm5a.16xlarge': ['m5a.12xlarge', 'm5a.8xlarge'],
        'm5a.24xlarge': ['m5a.16xlarge', 'm5a.12xlarge'],
        
        # c5 family
        'c5.large': ['t3.large', 't3.medium'],
        'c5.xlarge': ['c5.large', 'm5.large'],
        'c5.2xlarge': ['c5.xlarge', 'c5.large'],
        'c5.4xlarge': ['c5.2xlarge', 'c5.xlarge'],
        'c5.9xlarge': ['c5.4xlarge', 'c5.2xlarge'],
        'c5.12xlarge': ['c5.9xlarge', 'c5.4xlarge'],
        'c5.18xlarge': ['c5.12xlarge', 'c5.9xlarge'],
        'c5.24xlarge': ['c5.18xlarge', 'c5.12xlarge'],
        
        # c5a family
        'c5a.large': ['t3a.large', 't3a.medium'],
        'c5a.xlarge': ['c5a.large', 'm5a.large'],
        'c5a.2xlarge': ['c5a.xlarge', 'c5a.large'],
        'c5a.4xlarge': ['c5a.2xlarge', 'c5a.xlarge'],
        'c5a.8xlarge': ['c5a.4xlarge', 'c5a.2xlarge'],
        'c5a.12xlarge': ['c5a.8xlarge', 'c5a.4xlarge'],
        'c5a.16xlarge': ['c5a.12xlarge', 'c5a.8xlarge'],
        'c5a.24xlarge': ['c5a.16xlarge', 'c5a.12xlarge'],
    }
    
    def __init__(self, region: str = 'us-east-1', profile_name: Optional[str] = None, demo_mode: bool = False):
        """Initialize the rightsizing detector."""
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
        """Generate realistic sample data for demo mode."""
        return {
            'instances': [
                {
                    'InstanceId': 'i-1234567890abcdef0',
                    'InstanceType': 't3.large',
                    'State': {'Name': 'running'},
                    'LaunchTime': '2024-02-01T10:30:00Z',
                    'Tags': [
                        {'Key': 'Name', 'Value': 'web-server-1'},
                        {'Key': 'Environment', 'Value': 'production'}
                    ],
                    'AverageCPU': 5.2,
                    'CurrentHourlyCost': 0.0832
                },
                {
                    'InstanceId': 'i-0fedcba9876543210',
                    'InstanceType': 'm5.xlarge',
                    'State': {'Name': 'running'},
                    'LaunchTime': '2024-01-15T14:20:00Z',
                    'Tags': [
                        {'Key': 'Name', 'Value': 'app-server-2'},
                        {'Key': 'Environment', 'Value': 'staging'}
                    ],
                    'AverageCPU': 8.7,
                    'CurrentHourlyCost': 0.192
                },
                {
                    'InstanceId': 'i-abcdef1234567890a',
                    'InstanceType': 'c5.2xlarge',
                    'State': {'Name': 'running'},
                    'LaunchTime': '2024-02-10T08:45:00Z',
                    'Tags': [
                        {'Key': 'Name', 'Value': 'compute-worker-1'},
                        {'Key': 'Environment', 'Value': 'production'}
                    ],
                    'AverageCPU': 3.1,
                    'CurrentHourlyCost': 0.340
                },
                {
                    'InstanceId': 'i-a1b2c3d4e5f6g7h8i',
                    'InstanceType': 't3.medium',
                    'State': {'Name': 'running'},
                    'LaunchTime': '2024-02-05T12:15:00Z',
                    'Tags': [
                        {'Key': 'Name', 'Value': 'batch-processor-1'},
                        {'Key': 'Environment', 'Value': 'development'}
                    ],
                    'AverageCPU': 15.8,
                    'CurrentHourlyCost': 0.0416
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
                    if instance['State']['Name'] == 'running':
                        instances.append(instance)
            
            return instances
        except ClientError as e:
            print(f"Error retrieving EC2 instances: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error retrieving EC2 instances: {e}")
            return []
    
    def get_cpu_utilization(self, instance_id: str, days: int = 7) -> Optional[float]:
        """
        Get average CPU utilization for an instance over the specified period.
        
        Args:
            instance_id: EC2 instance ID
            days: Number of days to look back
            
        Returns:
            Average CPU utilization percentage or None if unavailable
        """
        if self.demo_mode:
            # Return demo CPU data
            for instance in self.demo_data['instances']:
                if instance['InstanceId'] == instance_id:
                    return instance['AverageCPU']
            return None
        
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            response = self.cloudwatch_client.get_metric_statistics(
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
            
            datapoints = response.get('Datapoints', [])
            if not datapoints:
                return None
            
            # Calculate average CPU utilization
            total_cpu = sum(dp['Average'] for dp in datapoints)
            avg_cpu = total_cpu / len(datapoints)
            
            return avg_cpu
            
        except ClientError as e:
            print(f"Error retrieving CPU metrics for {instance_id}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error retrieving CPU metrics for {instance_id}: {e}")
            return None
    
    def get_instance_name(self, instance: Dict) -> str:
        """Extract instance name from tags."""
        tags = instance.get('Tags', [])
        for tag in tags:
            if tag['Key'] == 'Name':
                return tag['Value']
        return instance['InstanceId']
    
    def get_hourly_cost(self, instance_type: str) -> float:
        """Get hourly cost for an instance type."""
        return self.INSTANCE_PRICING.get(instance_type, 0.0)
    
    def recommend_instance_type(self, current_type: str, cpu_utilization: float) -> List[Dict]:
        """
        Recommend smaller instance types based on current utilization.
        
        Args:
            current_type: Current instance type
            cpu_utilization: Average CPU utilization percentage
            
        Returns:
            List of recommended instance types with savings
        """
        recommendations = []
        
        # Get possible recommendations from mapping
        possible_recommendations = self.RIGHTSIZING_MAP.get(current_type, [])
        
        for rec_type in possible_recommendations:
            if rec_type in self.INSTANCE_PRICING:
                current_cost = self.get_hourly_cost(current_type)
                rec_cost = self.get_hourly_cost(rec_type)
                
                if rec_cost > 0 and rec_cost < current_cost:
                    savings_per_hour = current_cost - rec_cost
                    savings_per_month = savings_per_hour * 24 * 30  # 30 days
                    
                    recommendations.append({
                        'instance_type': rec_type,
                        'current_hourly_cost': current_cost,
                        'recommended_hourly_cost': rec_cost,
                        'savings_per_hour': savings_per_hour,
                        'savings_per_month': savings_per_month,
                        'confidence': self._calculate_confidence(cpu_utilization, current_type, rec_type)
                    })
        
        # Sort by monthly savings (descending)
        recommendations.sort(key=lambda x: x['savings_per_month'], reverse=True)
        
        return recommendations
    
    def _calculate_confidence(self, cpu_utilization: float, current_type: str, recommended_type: str) -> str:
        """Calculate confidence level for recommendation."""
        if cpu_utilization < 5:
            return 'High'
        elif cpu_utilization < 8:
            return 'Medium'
        else:
            return 'Low'
    
    def analyze_instances(self) -> Dict:
        """
        Analyze all instances for rightsizing opportunities.
        
        Returns:
            Analysis results with recommendations
        """
        print("Analyzing EC2 instances for rightsizing opportunities...")
        
        if self.demo_mode:
            print("Running in DEMO MODE with sample data")
        
        instances = self.get_ec2_instances()
        rightsizing_candidates = []
        
        for instance in instances:
            instance_id = instance['InstanceId']
            instance_type = instance['InstanceType']
            instance_name = self.get_instance_name(instance)
            
            # Get CPU utilization
            cpu_utilization = self.get_cpu_utilization(instance_id)
            
            if cpu_utilization is None:
                print(f"Warning: No CPU data available for {instance_name} ({instance_id})")
                continue
            
            # Check if it's a rightsizing candidate (CPU < 10%)
            if cpu_utilization < 10.0:
                current_cost = self.get_hourly_cost(instance_type)
                
                # Get recommendations
                recommendations = self.recommend_instance_type(instance_type, cpu_utilization)
                
                candidate = {
                    'instance_id': instance_id,
                    'instance_name': instance_name,
                    'instance_type': instance_type,
                    'state': instance['State']['Name'],
                    'launch_time': instance['LaunchTime'].isoformat() if not self.demo_mode else instance['LaunchTime'],
                    'average_cpu_utilization': cpu_utilization,
                    'current_hourly_cost': current_cost,
                    'current_monthly_cost': current_cost * 24 * 30,
                    'recommendations': recommendations,
                    'potential_monthly_savings': sum(rec['savings_per_month'] for rec in recommendations),
                    'tags': instance.get('Tags', [])
                }
                
                rightsizing_candidates.append(candidate)
        
        # Calculate summary
        total_candidates = len(rightsizing_candidates)
        total_potential_savings = sum(candidate['potential_monthly_savings'] for candidate in rightsizing_candidates)
        
        results = {
            'scan_time': datetime.now().isoformat(),
            'region': self.region,
            'demo_mode': self.demo_mode,
            'analysis_period_days': 7,
            'cpu_threshold_percent': 10.0,
            'rightsizing_candidates': rightsizing_candidates,
            'summary': {
                'total_instances_analyzed': len(instances),
                'total_rightsizing_candidates': total_candidates,
                'total_potential_monthly_savings': total_potential_savings,
                'average_cpu_utilization': sum(candidate['average_cpu_utilization'] for candidate in rightsizing_candidates) / total_candidates if total_candidates > 0 else 0
            }
        }
        
        return results
    
    def print_summary(self, results: Dict):
        """Print a readable summary of the analysis."""
        summary = results['summary']
        candidates = results['rightsizing_candidates']
        
        print(f"\n=== EC2 Rightsizing Analysis ===")
        print(f"Region: {results['region']}")
        print(f"Scan Time: {results['scan_time']}")
        print(f"Analysis Period: {results['analysis_period_days']} days")
        print(f"CPU Threshold: {results['cpu_threshold_percent']}%")
        if results['demo_mode']:
            print(f"Mode: DEMO (using sample data)")
        
        print(f"\n--- Summary ---")
        print(f"Total Instances Analyzed: {summary['total_instances_analyzed']}")
        print(f"Rightsizing Candidates: {summary['total_rightsizing_candidates']}")
        print(f"Potential Monthly Savings: ${summary['total_potential_monthly_savings']:.2f}")
        
        if candidates:
            print(f"\n--- Rightsizing Candidates ---")
            for i, candidate in enumerate(candidates, 1):
                print(f"\n{i}. {candidate['instance_name']} ({candidate['instance_id']})")
                print(f"   Type: {candidate['instance_type']}")
                print(f"   CPU Utilization: {candidate['average_cpu_utilization']:.1f}%")
                print(f"   Current Cost: ${candidate['current_monthly_cost']:.2f}/month")
                print(f"   Potential Savings: ${candidate['potential_monthly_savings']:.2f}/month")
                
                if candidate['recommendations']:
                    print(f"   Recommendations:")
                    for j, rec in enumerate(candidate['recommendations'], 1):
                        print(f"     {j}. {rec['instance_type']} - Save ${rec['savings_per_month']:.2f}/month (Confidence: {rec['confidence']})")
        
        else:
            print("\nNo rightsizing candidates found. Your instances are well-utilized!")
    
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
    """Main function to run the rightsizing detector."""
    parser = argparse.ArgumentParser(
        description='Detect EC2 rightsizing opportunities based on CPU utilization',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python rightsizing_detector.py
  python rightsizing_detector.py --region us-west-2 --output rightsizing_report.json
  python rightsizing_detector.py --demo --output demo_rightsizing.json
  python rightsizing_detector.py --profile my-aws-profile --region eu-west-1
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
    
    print("EC2 Rightsizing Detector")
    print(f"Region: {args.region}")
    
    # Initialize detector
    detector = RightsizingDetector(
        region=args.region,
        profile_name=args.profile,
        demo_mode=args.demo
    )
    
    # Analyze instances
    results = detector.analyze_instances()
    
    # Print summary
    detector.print_summary(results)
    
    # Export to JSON if output file specified
    if args.output:
        detector.export_to_json(results, args.output)
    
    # Exit with appropriate code
    total_candidates = results['summary']['total_rightsizing_candidates']
    
    if total_candidates > 0:
        print(f"\nFound {total_candidates} rightsizing opportunities with potential savings of ${results['summary']['total_potential_monthly_savings']:.2f}/month")
        sys.exit(1)  # Non-zero exit code to indicate findings
    else:
        print("\nNo rightsizing opportunities found. Great job!")
        sys.exit(0)


if __name__ == '__main__':
    main()
