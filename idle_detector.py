#!/usr/bin/env python3
"""
AWS Idle Resource Detector

This script detects idle AWS resources including unattached EBS volumes and unused Elastic IP addresses.
Supports demo mode with sample data when AWS credentials are unavailable.
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional
import boto3
from botocore.exceptions import ClientError, NoCredentialsError, EndpointConnectionError


class IdleResourceDetector:
    """Detects idle AWS resources to help optimize costs."""
    
    def __init__(self, region: str = 'us-east-1', profile_name: Optional[str] = None, demo_mode: bool = False):
        """Initialize the idle resource detector."""
        self.region = region
        self.demo_mode = demo_mode
        self.demo_data = self._generate_demo_data()
        
        if not demo_mode:
            try:
                session = boto3.Session(profile_name=profile_name)
                self.ec2_client = session.client('ec2', region_name=region)
            except NoCredentialsError:
                print("Warning: AWS credentials not found. Enabling demo mode.")
                self.demo_mode = True
            except Exception as e:
                print(f"Error initializing AWS session: {e}")
                sys.exit(1)
    
    def _generate_demo_data(self) -> Dict:
        """Generate sample data for demo mode."""
        return {
            'unattached_volumes': [
                {
                    'VolumeId': 'vol-1234567890abcdef0',
                    'Size': 100,
                    'VolumeType': 'gp3',
                    'AvailabilityZone': 'us-east-1a',
                    'State': 'available',
                    'CreateTime': '2024-01-15T10:30:00Z',
                    'MonthlyCost': 10.00
                },
                {
                    'VolumeId': 'vol-0fedcba9876543210',
                    'Size': 50,
                    'VolumeType': 'gp2',
                    'AvailabilityZone': 'us-east-1b',
                    'State': 'available',
                    'CreateTime': '2024-02-01T14:20:00Z',
                    'MonthlyCost': 4.25
                }
            ],
            'unused_elastic_ips': [
                {
                    'AllocationId': 'eipalloc-1234567890abcdef0',
                    'PublicIp': '203.0.113.1',
                    'Domain': 'vpc',
                    'AllocationTime': '2024-01-20T08:15:00Z',
                    'MonthlyCost': 3.65
                },
                {
                    'AllocationId': 'eipalloc-0fedcba9876543210',
                    'PublicIp': '203.0.113.2',
                    'Domain': 'vpc',
                    'AllocationTime': '2024-02-10T12:45:00Z',
                    'MonthlyCost': 3.65
                }
            ]
        }
    
    def get_unattached_volumes(self) -> List[Dict]:
        """
        Get unattached EBS volumes.
        
        Returns:
            List of unattached volume information
        """
        if self.demo_mode:
            return self.demo_data['unattached_volumes']
        
        try:
            response = self.ec2_client.describe_volumes(
                Filters=[
                    {'Name': 'status', 'Values': ['available']}
                ]
            )
            
            unattached_volumes = []
            for volume in response.get('Volumes', []):
                # Calculate monthly cost (simplified pricing)
                monthly_cost = self._calculate_volume_cost(volume)
                
                unattached_volumes.append({
                    'VolumeId': volume['VolumeId'],
                    'Size': volume['Size'],
                    'VolumeType': volume['VolumeType'],
                    'AvailabilityZone': volume['AvailabilityZone'],
                    'State': volume['State'],
                    'CreateTime': volume['CreateTime'].isoformat(),
                    'MonthlyCost': monthly_cost
                })
            
            return unattached_volumes
        except ClientError as e:
            print(f"Error retrieving EBS volumes: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error retrieving EBS volumes: {e}")
            return []
    
    def _calculate_volume_cost(self, volume: Dict) -> float:
        """
        Calculate monthly cost for an EBS volume (simplified pricing).
        
        Args:
            volume: Volume information from AWS API
            
        Returns:
            Estimated monthly cost in USD
        """
        size_gb = volume['Size']
        volume_type = volume['VolumeType']
        
        # Simplified pricing (actual prices vary by region)
        pricing = {
            'gp2': 0.10,    # $0.10 per GB-month
            'gp3': 0.08,    # $0.08 per GB-month
            'io1': 0.125,   # $0.125 per GB-month (plus provisioned IOPS)
            'io2': 0.125,   # $0.125 per GB-month (plus provisioned IOPS)
            'st1': 0.045,   # $0.045 per GB-month
            'sc1': 0.025,   # $0.025 per GB-month
            'standard': 0.05  # $0.05 per GB-month (magnetic)
        }
        
        base_cost = size_gb * pricing.get(volume_type, 0.10)
        
        # Add IOPS cost for io1/io2 volumes (simplified)
        if volume_type in ['io1', 'io2'] and 'Iops' in volume:
            base_cost += volume['Iops'] * 0.005  # $0.005 per provisioned IOPS-month
        
        return round(base_cost, 2)
    
    def get_unused_elastic_ips(self) -> List[Dict]:
        """
        Get unused Elastic IP addresses.
        
        Returns:
            List of unused Elastic IP information
        """
        if self.demo_mode:
            return self.demo_data['unused_elastic_ips']
        
        try:
            response = self.ec2_client.describe_addresses()
            
            unused_ips = []
            for address in response.get('Addresses', []):
                # Check if the EIP is not associated with any resource
                if 'AssociationId' not in address:
                    unused_ips.append({
                        'AllocationId': address['AllocationId'],
                        'PublicIp': address['PublicIp'],
                        'Domain': address.get('Domain', 'standard'),
                        'AllocationTime': address.get('AllocationTime', 'Unknown').isoformat() if hasattr(address.get('AllocationTime'), 'isoformat') else 'Unknown',
                        'MonthlyCost': 3.65  # Standard EIP pricing when not attached
                    })
            
            return unused_ips
        except ClientError as e:
            print(f"Error retrieving Elastic IPs: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error retrieving Elastic IPs: {e}")
            return []
    
    def scan_resources(self) -> Dict:
        """
        Scan for all idle resources.
        
        Returns:
            Dictionary containing all idle resource findings
        """
        print("Scanning for idle AWS resources...")
        
        if self.demo_mode:
            print("Running in DEMO MODE with sample data")
        
        unattached_volumes = self.get_unattached_volumes()
        unused_elastic_ips = self.get_unused_elastic_ips()
        
        results = {
            'scan_time': datetime.now().isoformat(),
            'region': self.region,
            'demo_mode': self.demo_mode,
            'unattached_volumes': unattached_volumes,
            'unused_elastic_ips': unused_elastic_ips,
            'summary': {
                'total_unattached_volumes': len(unattached_volumes),
                'total_unused_elastic_ips': len(unused_elastic_ips),
                'total_monthly_savings': sum(v['MonthlyCost'] for v in unattached_volumes) + 
                                       sum(ip['MonthlyCost'] for ip in unused_elastic_ips)
            }
        }
        
        return results
    
    def print_summary(self, results: Dict):
        """Print a summary of the findings."""
        summary = results['summary']
        
        print(f"\n=== AWS Idle Resource Summary ===")
        print(f"Region: {results['region']}")
        print(f"Scan Time: {results['scan_time']}")
        if results['demo_mode']:
            print(f"Mode: DEMO (using sample data)")
        
        print(f"\nUnattached EBS Volumes: {summary['total_unattached_volumes']}")
        print(f"Unused Elastic IPs: {summary['total_unused_elastic_ips']}")
        print(f"Potential Monthly Savings: ${summary['total_monthly_savings']:.2f}")
        
        # Print details for unattached volumes
        if results['unattached_volumes']:
            print(f"\n--- Unattached EBS Volumes ---")
            for volume in results['unattached_volumes']:
                print(f"Volume ID: {volume['VolumeId']}")
                print(f"  Size: {volume['Size']} GB")
                print(f"  Type: {volume['VolumeType']}")
                print(f"  AZ: {volume['AvailabilityZone']}")
                print(f"  Created: {volume['CreateTime']}")
                print(f"  Monthly Cost: ${volume['MonthlyCost']:.2f}")
                print()
        
        # Print details for unused Elastic IPs
        if results['unused_elastic_ips']:
            print(f"--- Unused Elastic IP Addresses ---")
            for eip in results['unused_elastic_ips']:
                print(f"Allocation ID: {eip['AllocationId']}")
                print(f"  Public IP: {eip['PublicIp']}")
                print(f"  Domain: {eip['Domain']}")
                print(f"  Allocated: {eip['AllocationTime']}")
                print(f"  Monthly Cost: ${eip['MonthlyCost']:.2f}")
                print()
    
    def export_to_json(self, results: Dict, output_file: str):
        """
        Export results to JSON file.
        
        Args:
            results: Scan results to export
            output_file: Path to output JSON file
        """
        try:
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"Results exported to: {output_file}")
        except Exception as e:
            print(f"Error exporting results to {output_file}: {e}")


def main():
    """Main function to run the idle resource detector."""
    parser = argparse.ArgumentParser(
        description='Detect idle AWS resources to optimize costs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python idle_detector.py
  python idle_detector.py --region us-west-2 --output results.json
  python idle_detector.py --demo --output demo_results.json
  python idle_detector.py --profile my-aws-profile --region eu-west-1
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
    
    print("AWS Idle Resource Detector")
    print(f"Region: {args.region}")
    
    # Initialize detector
    detector = IdleResourceDetector(
        region=args.region,
        profile_name=args.profile,
        demo_mode=args.demo
    )
    
    # Scan for idle resources
    results = detector.scan_resources()
    
    # Print summary
    detector.print_summary(results)
    
    # Export to JSON if output file specified
    if args.output:
        detector.export_to_json(results, args.output)
    
    # Exit with appropriate code
    total_idle = (results['summary']['total_unattached_volumes'] + 
                 results['summary']['total_unused_elastic_ips'])
    
    if total_idle > 0:
        print(f"\nFound {total_idle} idle resources that could save ${results['summary']['total_monthly_savings']:.2f}/month")
        sys.exit(1)  # Non-zero exit code to indicate findings
    else:
        print("\nNo idle resources found. Well done!")
        sys.exit(0)


if __name__ == '__main__':
    main()
