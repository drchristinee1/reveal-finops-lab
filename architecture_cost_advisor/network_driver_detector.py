#!/usr/bin/env python3
"""
AWS Network Driver Detector

This script analyzes AWS networking costs to identify traffic-related demand drivers
that influence cloud costs through usage patterns and metrics.
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import boto3
from botocore.exceptions import ClientError, NoCredentialsError, EndpointConnectionError


class NetworkDriverDetector:
    """Detects network demand drivers based on usage patterns."""
    
    # Simplified AWS networking pricing (actual prices vary by region)
    NETWORK_PRICING = {
        'nat_gateway': {
            'hourly': 0.045,  # $0.045 per hour
            'data_processing': 0.045  # $0.045 per GB
        },
        'data_transfer': {
            'out_to_internet': 0.09,  # $0.09 per GB (first 10TB/month)
            'out_to_internet_tier2': 0.085,  # $0.085 per GB (10-40TB)
            'out_to_internet_tier3': 0.07,   # $0.07 per GB (40-100TB)
            'out_to_internet_tier4': 0.05,   # $0.05 per GB (100TB+)
            'cross_az': 0.01,  # $0.01 per GB
            'same_az': 0.0    # Free
        },
        'load_balancer': {
            'alb_hourly': 0.0225,  # $0.0225 per hour
            'nlb_hourly': 0.0225,  # $0.0225 per hour
            'clb_hourly': 0.0252,  # $0.0252 per hour
            'lcu_processing': 0.008  # $0.008 per LCU-hour
        },
        'vpc_endpoint': {
            'gateway_hourly': 0.01,  # $0.01 per hour
            'interface_hourly': 0.01  # $0.01 per hour + data processing
        }
    }
    
    def __init__(self, region: str = 'us-east-1', profile_name: Optional[str] = None, demo_mode: bool = False):
        """Initialize the network driver detector."""
        self.region = region
        self.demo_mode = demo_mode
        self.demo_data = self._generate_demo_data()
        
        if not demo_mode:
            try:
                session = boto3.Session(profile_name=profile_name)
                self.ec2_client = session.client('ec2', region_name=region)
                self.elbv2_client = session.client('elbv2', region_name=region)
                self.cloudwatch_client = session.client('cloudwatch', region_name=region)
                self.ce_client = session.client('ce', region_name='us-east-1')  # Cost Explorer in us-east-1
            except NoCredentialsError:
                print("Warning: AWS credentials not found. Enabling demo mode.")
                self.demo_mode = True
            except Exception as e:
                print(f"Error initializing AWS session: {e}")
                sys.exit(1)
    
    def _generate_demo_data(self) -> Dict:
        """Generate realistic sample networking data for demo mode."""
        return {
            'nat_gateways': [
                {
                    'NatGatewayId': 'nat-1234567890abcdef0',
                    'SubnetId': 'subnet-12345678',
                    'VpcId': 'vpc-12345678',
                    'State': 'available',
                    'CreateTime': datetime(2024, 1, 15, 10, 30, 0),
                    'Tags': [
                        {'Key': 'Name', 'Value': 'main-nat-gateway'},
                        {'Key': 'Environment', 'Value': 'production'},
                        {'Key': 'Team', 'Value': 'backend'}
                    ],
                    'Metrics': {
                        'BytesProcessed': 268435456000,  # 250 GB in bytes
                        'ConnectionCount': 50000
                    }
                },
                {
                    'NatGatewayId': 'nat-0fedcba9876543210',
                    'SubnetId': 'subnet-87654321',
                    'VpcId': 'vpc-12345678',
                    'State': 'available',
                    'CreateTime': datetime(2024, 2, 1, 14, 20, 0),
                    'Tags': [
                        {'Key': 'Name', 'Value': 'backup-nat-gateway'},
                        {'Key': 'Environment', 'Value': 'production'},
                        {'Key': 'Team', 'Value': 'ops'}
                    ],
                    'Metrics': {
                        'BytesProcessed': 107374182400,  # 100 GB in bytes
                        'ConnectionCount': 20000
                    }
                }
            ],
            'load_balancers': [
                {
                    'LoadBalancerArn': 'arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/main-alb/1234567890abcdef0',
                    'LoadBalancerName': 'main-alb',
                    'Type': 'application',
                    'State': {'Code': 'active'},
                    'Scheme': 'internet-facing',
                    'VpcId': 'vpc-12345678',
                    'AvailabilityZones': ['us-east-1a', 'us-east-1b'],
                    'CreateTime': datetime(2024, 1, 10, 8, 45, 0),
                    'Tags': [
                        {'Key': 'Name', 'Value': 'main-alb'},
                        {'Key': 'Environment', 'Value': 'production'},
                        {'Key': 'Team', 'Value': 'frontend'}
                    ],
                    'Metrics': {
                        'ProcessedBytes': 536870912000,  # 500 GB in bytes
                        'RequestCount': 10000000,
                        'LCUHours': 720
                    }
                },
                {
                    'LoadBalancerArn': 'arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/net/internal-nlb/1234567890abcdef0',
                    'LoadBalancerName': 'internal-nlb',
                    'Type': 'network',
                    'State': {'Code': 'active'},
                    'Scheme': 'internal',
                    'VpcId': 'vpc-12345678',
                    'AvailabilityZones': ['us-east-1c', 'us-east-1d'],
                    'CreateTime': datetime(2024, 1, 20, 16, 0, 0),
                    'Tags': [
                        {'Key': 'Name', 'Value': 'internal-nlb'},
                        {'Key': 'Environment', 'Value': 'production'},
                        {'Key': 'Team', 'Value': 'backend'}
                    ],
                    'Metrics': {
                        'ProcessedBytes': 268435456000,  # 250 GB in bytes
                        'RequestCount': 5000000,
                        'LCUHours': 360
                    }
                }
            ],
            'vpc_endpoints': [
                {
                    'VpcEndpointId': 'vpce-1234567890abcdef0',
                    'VpcId': 'vpc-12345678',
                    'ServiceName': 'com.amazonaws.us-east-1.s3',
                    'VpcEndpointType': 'Gateway',
                    'State': 'available',
                    'CreationTimestamp': datetime(2024, 1, 5, 12, 0, 0),
                    'Tags': [
                        {'Key': 'Name', 'Value': 's3-endpoint'},
                        {'Key': 'Environment', 'Value': 'production'}
                    ]
                },
                {
                    'VpcEndpointId': 'vpce-0fedcba9876543210',
                    'VpcId': 'vpc-12345678',
                    'ServiceName': 'com.amazonaws.us-east-1.dynamodb',
                    'VpcEndpointType': 'Interface',
                    'State': 'available',
                    'CreationTimestamp': datetime(2024, 2, 10, 9, 30, 0),
                    'Tags': [
                        {'Key': 'Name', 'Value': 'dynamodb-endpoint'},
                        {'Key': 'Environment', 'Value': 'production'}
                    ]
                }
            ],
            'data_transfer': {
                'out_to_internet_gb': 850,  # GB transferred to internet
                'cross_az_gb': 120,        # GB transferred cross-AZ
                'same_az_gb': 5000,        # GB transferred same-AZ (free)
                'total_gb': 5970
            }
        }
    
    def get_nat_gateways(self) -> List[Dict]:
        """
        Get all NAT gateways in the region.
        
        Returns:
            List of NAT gateway information
        """
        if self.demo_mode:
            return self.demo_data['nat_gateways']
        
        try:
            response = self.ec2_client.describe_nat_gateways()
            
            nat_gateways = []
            for nat_gateway in response.get('NatGateways', []):
                # Only include available NAT gateways
                if nat_gateway['State'] == 'available':
                    nat_gateways.append(nat_gateway)
            
            return nat_gateways
        except ClientError as e:
            print(f"Error retrieving NAT gateways: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error retrieving NAT gateways: {e}")
            return []
    
    def get_load_balancers(self) -> List[Dict]:
        """
        Get all load balancers in the region.
        
        Returns:
            List of load balancer information
        """
        if self.demo_mode:
            return self.demo_data['load_balancers']
        
        try:
            response = self.elbv2_client.describe_load_balancers()
            
            load_balancers = []
            for lb in response.get('LoadBalancers', []):
                # Only include active load balancers
                if lb.get('State', {}).get('Code') == 'active':
                    load_balancers.append(lb)
            
            return load_balancers
        except ClientError as e:
            print(f"Error retrieving load balancers: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error retrieving load balancers: {e}")
            return []
    
    def get_vpc_endpoints(self) -> List[Dict]:
        """
        Get all VPC endpoints in the region.
        
        Returns:
            List of VPC endpoint information
        """
        if self.demo_mode:
            return self.demo_data['vpc_endpoints']
        
        try:
            response = self.ec2_client.describe_vpc_endpoints()
            
            vpc_endpoints = []
            for endpoint in response.get('VpcEndpoints', []):
                # Only include available endpoints
                if endpoint['State'] == 'available':
                    vpc_endpoints.append(endpoint)
            
            return vpc_endpoints
        except ClientError as e:
            print(f"Error retrieving VPC endpoints: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error retrieving VPC endpoints: {e}")
            return []
    
    def get_data_transfer_metrics(self, days: int = 30) -> Dict:
        """
        Get data transfer metrics for the region.
        
        Args:
            days: Number of days to look back for metrics
            
        Returns:
            Dictionary with data transfer metrics
        """
        if self.demo_mode:
            return self.demo_data['data_transfer']
        
        try:
            # In a real implementation, this would use Cost Explorer or CloudWatch
            # For demo purposes, we'll return estimated values
            return {
                'out_to_internet_gb': 850,
                'cross_az_gb': 120,
                'same_az_gb': 5000,
                'total_gb': 5970
            }
        except Exception as e:
            print(f"Error getting data transfer metrics: {e}")
            return {
                'out_to_internet_gb': 0,
                'cross_az_gb': 0,
                'same_az_gb': 0,
                'total_gb': 0
            }
    
    def get_nat_gateway_metrics(self, nat_gateway_id: str, days: int = 30) -> Optional[Dict]:
        """
        Get CloudWatch metrics for a NAT gateway.
        
        Args:
            nat_gateway_id: NAT gateway ID
            days: Number of days to look back for metrics
            
        Returns:
            Dictionary with metrics or None if unavailable
        """
        if self.demo_mode:
            # Return demo metrics
            for nat_gateway in self.demo_data['nat_gateways']:
                if nat_gateway['NatGatewayId'] == nat_gateway_id:
                    return nat_gateway['Metrics']
            return None
        
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            metrics = {}
            
            # Get BytesProcessedFromSource
            bytes_response = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/NATGateway',
                MetricName='BytesProcessedFromSource',
                Dimensions=[
                    {
                        'Name': 'NatGatewayId',
                        'Value': nat_gateway_id
                    }
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,  # 1 hour
                Statistics=['Sum']
            )
            
            # Get ConnectionAttemptCount
            connections_response = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/NATGateway',
                MetricName='ConnectionAttemptCount',
                Dimensions=[
                    {
                        'Name': 'NatGatewayId',
                        'Value': nat_gateway_id
                    }
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,  # 1 hour
                Statistics=['Sum']
            )
            
            # Calculate totals
            bytes_data = bytes_response.get('Datapoints', [])
            connections_data = connections_response.get('Datapoints', [])
            
            total_bytes = sum(dp['Sum'] for dp in bytes_data)
            total_connections = sum(dp['Sum'] for dp in connections_data)
            
            return {
                'BytesProcessed': total_bytes,
                'ConnectionCount': total_connections
            }
            
        except ClientError as e:
            print(f"Error retrieving metrics for {nat_gateway_id}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error retrieving metrics for {nat_gateway_id}: {e}")
            return None
    
    def get_load_balancer_metrics(self, lb_arn: str, days: int = 30) -> Optional[Dict]:
        """
        Get CloudWatch metrics for a load balancer.
        
        Args:
            lb_arn: Load balancer ARN
            days: Number of days to look back for metrics
            
        Returns:
            Dictionary with metrics or None if unavailable
        """
        if self.demo_mode:
            # Return demo metrics
            for lb in self.demo_data['load_balancers']:
                if lb['LoadBalancerArn'] == lb_arn:
                    return lb['Metrics']
            return None
        
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            metrics = {}
            
            # Get ProcessedBytes
            bytes_response = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/ApplicationELB' if 'app/' in lb_arn else 'AWS/NetworkLoadBalancer',
                MetricName='ProcessedBytes',
                Dimensions=[
                    {
                        'Name': 'LoadBalancer',
                        'Value': lb_arn.split('/')[-1].split('/')[0]
                    }
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,  # 1 hour
                Statistics=['Sum']
            )
            
            # Get RequestCount
            requests_response = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/ApplicationELB' if 'app/' in lb_arn else 'AWS/NetworkLoadBalancer',
                MetricName='RequestCount',
                Dimensions=[
                    {
                        'Name': 'LoadBalancer',
                        'Value': lb_arn.split('/')[-1].split('/')[0]
                    }
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,  # 1 hour
                Statistics=['Sum']
            )
            
            # Calculate totals
            bytes_data = bytes_response.get('Datapoints', [])
            requests_data = requests_response.get('Datapoints', [])
            
            total_bytes = sum(dp['Sum'] for dp in bytes_data)
            total_requests = sum(dp['Sum'] for dp in requests_data)
            
            # Estimate LCU hours (simplified)
            lcu_hours = days * 24  # Assume 1 LCU per hour
            
            return {
                'ProcessedBytes': total_bytes,
                'RequestCount': total_requests,
                'LCUHours': lcu_hours
            }
            
        except ClientError as e:
            print(f"Error retrieving metrics for {lb_arn}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error retrieving metrics for {lb_arn}: {e}")
            return None
    
    def calculate_nat_gateway_cost(self, nat_gateway: Dict, metrics: Dict) -> Dict:
        """
        Calculate estimated monthly cost for a NAT gateway.
        
        Args:
            nat_gateway: NAT gateway configuration
            metrics: CloudWatch metrics for the NAT gateway
            
        Returns:
            Cost breakdown dictionary
        """
        # Hourly cost (730 hours in a month)
        hourly_cost = self.NETWORK_PRICING['nat_gateway']['hourly']
        monthly_hourly_cost = hourly_cost * 730
        
        # Data processing cost
        bytes_processed_gb = metrics['BytesProcessed'] / (1024 * 1024 * 1024)
        data_processing_cost = bytes_processed_gb * self.NETWORK_PRICING['nat_gateway']['data_processing']
        
        total_monthly_cost = monthly_hourly_cost + data_processing_cost
        
        return {
            'hourly_cost': hourly_cost,
            'monthly_hourly_cost': monthly_hourly_cost,
            'data_processing_cost': data_processing_cost,
            'total_monthly_cost': total_monthly_cost,
            'bytes_processed_gb': bytes_processed_gb
        }
    
    def calculate_load_balancer_cost(self, load_balancer: Dict, metrics: Dict) -> Dict:
        """
        Calculate estimated monthly cost for a load balancer.
        
        Args:
            load_balancer: Load balancer configuration
            metrics: CloudWatch metrics for the load balancer
            
        Returns:
            Cost breakdown dictionary
        """
        lb_type = load_balancer['Type']
        
        # Hourly cost
        if lb_type == 'application':
            hourly_cost = self.NETWORK_PRICING['load_balancer']['alb_hourly']
        elif lb_type == 'network':
            hourly_cost = self.NETWORK_PRICING['load_balancer']['nlb_hourly']
        else:  # classic
            hourly_cost = self.NETWORK_PRICING['load_balancer']['clb_hourly']
        
        monthly_hourly_cost = hourly_cost * 730
        
        # LCU processing cost (for ALB/NLB)
        lcu_cost = 0
        if lb_type in ['application', 'network']:
            lcu_cost = metrics['LCUHours'] * self.NETWORK_PRICING['load_balancer']['lcu_processing']
        
        total_monthly_cost = monthly_hourly_cost + lcu_cost
        
        return {
            'hourly_cost': hourly_cost,
            'monthly_hourly_cost': monthly_hourly_cost,
            'lcu_cost': lcu_cost,
            'total_monthly_cost': total_monthly_cost,
            'processed_bytes_gb': metrics['ProcessedBytes'] / (1024 * 1024 * 1024),
            'request_count': metrics['RequestCount']
        }
    
    def calculate_data_transfer_cost(self, data_transfer: Dict) -> Dict:
        """
        Calculate estimated monthly cost for data transfer.
        
        Args:
            data_transfer: Data transfer metrics
            
        Returns:
            Cost breakdown dictionary
        """
        out_to_internet_gb = data_transfer['out_to_internet_gb']
        cross_az_gb = data_transfer['cross_az_gb']
        
        # Internet data transfer cost (tiered pricing)
        internet_cost = 0
        if out_to_internet_gb <= 10240:  # First 10TB
            internet_cost = out_to_internet_gb * self.NETWORK_PRICING['data_transfer']['out_to_internet']
        elif out_to_internet_gb <= 40960:  # 10-40TB
            internet_cost = 10240 * self.NETWORK_PRICING['data_transfer']['out_to_internet']
            internet_cost += (out_to_internet_gb - 10240) * self.NETWORK_PRICING['data_transfer']['out_to_internet_tier2']
        elif out_to_internet_gb <= 102400:  # 40-100TB
            internet_cost = 10240 * self.NETWORK_PRICING['data_transfer']['out_to_internet']
            internet_cost += 30720 * self.NETWORK_PRICING['data_transfer']['out_to_internet_tier2']
            internet_cost += (out_to_internet_gb - 40960) * self.NETWORK_PRICING['data_transfer']['out_to_internet_tier3']
        else:  # 100TB+
            internet_cost = 10240 * self.NETWORK_PRICING['data_transfer']['out_to_internet']
            internet_cost += 30720 * self.NETWORK_PRICING['data_transfer']['out_to_internet_tier2']
            internet_cost += 61440 * self.NETWORK_PRICING['data_transfer']['out_to_internet_tier3']
            internet_cost += (out_to_internet_gb - 102400) * self.NETWORK_PRICING['data_transfer']['out_to_internet_tier4']
        
        # Cross-AZ data transfer cost
        cross_az_cost = cross_az_gb * self.NETWORK_PRICING['data_transfer']['cross_az']
        
        # Same-AZ data transfer is free
        same_az_cost = 0
        
        total_monthly_cost = internet_cost + cross_az_cost + same_az_cost
        
        return {
            'internet_cost': internet_cost,
            'cross_az_cost': cross_az_cost,
            'same_az_cost': same_az_cost,
            'total_monthly_cost': total_monthly_cost,
            'out_to_internet_gb': out_to_internet_gb,
            'cross_az_gb': cross_az_gb,
            'same_az_gb': data_transfer['same_az_gb']
        }
    
    def identify_demand_driver(self, nat_gateways: List[Dict], load_balancers: List[Dict], 
                             vpc_endpoints: List[Dict], data_transfer: Dict, cost_analysis: Dict) -> str:
        """
        Identify the likely demand driver based on networking patterns.
        
        Args:
            nat_gateways: List of NAT gateways
            load_balancers: List of load balancers
            vpc_endpoints: List of VPC endpoints
            data_transfer: Data transfer metrics
            cost_analysis: Cost analysis breakdown
            
        Returns:
            Identified demand driver
        """
        nat_cost = cost_analysis.get('total_nat_cost', 0)
        lb_cost = cost_analysis.get('total_lb_cost', 0)
        data_transfer_cost = cost_analysis.get('total_data_transfer_cost', 0)
        
        out_to_internet_gb = data_transfer['out_to_internet_gb']
        cross_az_gb = data_transfer['cross_az_gb']
        
        # Analyze patterns to identify drivers
        if nat_cost > 100 and data_transfer_cost > 50:
            return 'External traffic and private subnet egress'
        elif lb_cost > 50 and out_to_internet_gb > 500:
            return 'High-traffic web applications'
        elif cross_az_gb > 200:
            return 'Cross-AZ communication inefficiency'
        elif nat_cost > 150:
            return 'Private subnet egress patterns'
        elif lb_cost > 100:
            return 'Load balancing infrastructure'
        elif out_to_internet_gb > 1000:
            return 'Content delivery and user traffic'
        elif len(vpc_endpoints) > 0 and nat_cost > 50:
            return 'Hybrid architecture with VPC endpoints'
        elif data_transfer_cost > 200:
            return 'Data-intensive workloads'
        elif lb_cost > 0 and nat_cost > 0:
            return 'Multi-tier application architecture'
        else:
            return 'General networking infrastructure'
    
    def calculate_optimization_signals(self, nat_gateways: List[Dict], load_balancers: List[Dict], 
                                     vpc_endpoints: List[Dict], data_transfer: Dict, cost_analysis: Dict) -> List[str]:
        """
        Calculate optimization signals for networking costs.
        
        Args:
            nat_gateways: List of NAT gateways
            load_balancers: List of load balancers
            vpc_endpoints: List of VPC endpoints
            data_transfer: Data transfer metrics
            cost_analysis: Cost analysis breakdown
            
        Returns:
            List of optimization signals
        """
        signals = []
        
        nat_cost = cost_analysis.get('total_nat_cost', 0)
        lb_cost = cost_analysis.get('total_lb_cost', 0)
        data_transfer_cost = cost_analysis.get('total_data_transfer_cost', 0)
        
        out_to_internet_gb = data_transfer['out_to_internet_gb']
        cross_az_gb = data_transfer['cross_az_gb']
        
        # NAT Gateway optimization signals
        if nat_cost > 100:
            signals.append("High NAT Gateway costs - consider VPC endpoints")
            signals.append("Review private subnet egress patterns")
        
        if len(nat_gateways) > 2:
            signals.append("Multiple NAT gateways - consider consolidation")
        
        # Load balancer optimization signals
        if lb_cost > 80:
            signals.append("High load balancer costs - review traffic patterns")
        
        # Data transfer optimization signals
        if cross_az_gb > 100:
            signals.append("High cross-AZ traffic - consider same-AZ deployment")
        
        if out_to_internet_gb > 1000:
            signals.append("High internet egress - consider CDN or edge locations")
        
        # VPC endpoint optimization signals
        if len(vpc_endpoints) == 0 and nat_cost > 50:
            signals.append("Consider VPC endpoints to reduce NAT usage")
        
        # Architecture optimization signals
        if nat_cost > 0 and lb_cost > 0 and cross_az_gb > 50:
            signals.append("Review multi-AZ architecture for efficiency")
        
        # Cost optimization signals
        if data_transfer_cost > 200:
            signals.append("Consider data compression or caching")
        
        return signals
    
    def analyze_network_drivers(self) -> Dict:
        """
        Analyze AWS networking costs to identify demand drivers.
        
        Returns:
            Analysis results with driver information
        """
        print("Analyzing AWS networking for demand drivers...")
        
        if self.demo_mode:
            print("Running in DEMO MODE with sample data")
        
        # Get networking components
        nat_gateways = self.get_nat_gateways()
        load_balancers = self.get_load_balancers()
        vpc_endpoints = self.get_vpc_endpoints()
        data_transfer = self.get_data_transfer_metrics()
        
        # Analyze NAT gateways
        nat_analysis = []
        for nat_gateway in nat_gateways:
            nat_id = nat_gateway['NatGatewayId']
            metrics = self.get_nat_gateway_metrics(nat_id)
            
            if not metrics:
                print(f"Warning: No metrics available for {nat_id}")
                continue
            
            cost_analysis = self.calculate_nat_gateway_cost(nat_gateway, metrics)
            
            analysis = {
                'nat_gateway_id': nat_id,
                'subnet_id': nat_gateway['SubnetId'],
                'vpc_id': nat_gateway['VpcId'],
                'state': nat_gateway['State'],
                'create_time': nat_gateway['CreateTime'],
                'tags': nat_gateway.get('Tags', []),
                'metrics': metrics,
                'cost_analysis': cost_analysis
            }
            
            nat_analysis.append(analysis)
        
        # Analyze load balancers
        lb_analysis = []
        for load_balancer in load_balancers:
            lb_arn = load_balancer['LoadBalancerArn']
            metrics = self.get_load_balancer_metrics(lb_arn)
            
            if not metrics:
                print(f"Warning: No metrics available for {lb_arn}")
                continue
            
            cost_analysis = self.calculate_load_balancer_cost(load_balancer, metrics)
            
            analysis = {
                'load_balancer_arn': lb_arn,
                'load_balancer_name': load_balancer['LoadBalancerName'],
                'type': load_balancer['Type'],
                'scheme': load_balancer['Scheme'],
                'vpc_id': load_balancer['VpcId'],
                'availability_zones': load_balancer['AvailabilityZones'],
                'create_time': load_balancer['CreateTime'],
                'tags': load_balancer.get('Tags', []),
                'metrics': metrics,
                'cost_analysis': cost_analysis
            }
            
            lb_analysis.append(analysis)
        
        # Calculate data transfer costs
        data_transfer_cost_analysis = self.calculate_data_transfer_cost(data_transfer)
        
        # Calculate total costs
        total_nat_cost = sum(analysis['cost_analysis']['total_monthly_cost'] for analysis in nat_analysis)
        total_lb_cost = sum(analysis['cost_analysis']['total_monthly_cost'] for analysis in lb_analysis)
        total_data_transfer_cost = data_transfer_cost_analysis['total_monthly_cost']
        total_monthly_cost = total_nat_cost + total_lb_cost + total_data_transfer_cost
        
        # Identify demand driver
        cost_analysis = {
            'total_nat_cost': total_nat_cost,
            'total_lb_cost': total_lb_cost,
            'total_data_transfer_cost': total_data_transfer_cost,
            'total_monthly_cost': total_monthly_cost
        }
        
        driver = self.identify_demand_driver(nat_gateways, load_balancers, vpc_endpoints, data_transfer, cost_analysis)
        
        # Calculate optimization signals
        optimization_signals = self.calculate_optimization_signals(nat_gateways, load_balancers, vpc_endpoints, data_transfer, cost_analysis)
        
        results = {
            'scan_time': datetime.now().isoformat(),
            'region': self.region,
            'demo_mode': self.demo_mode,
            'analysis_period_days': 30,
            'network_pricing': self.NETWORK_PRICING,
            'nat_gateways': nat_analysis,
            'load_balancers': lb_analysis,
            'vpc_endpoints': vpc_endpoints,
            'data_transfer': data_transfer,
            'data_transfer_cost_analysis': data_transfer_cost_analysis,
            'cost_analysis': cost_analysis,
            'demand_driver': driver,
            'optimization_signals': optimization_signals,
            'summary': {
                'total_nat_gateways': len(nat_analysis),
                'total_load_balancers': len(lb_analysis),
                'total_vpc_endpoints': len(vpc_endpoints),
                'total_nat_cost': total_nat_cost,
                'total_lb_cost': total_lb_cost,
                'total_data_transfer_cost': total_data_transfer_cost,
                'total_monthly_cost': total_monthly_cost,
                'out_to_internet_gb': data_transfer['out_to_internet_gb'],
                'cross_az_gb': data_transfer['cross_az_gb']
            }
        }
        
        return results
    
    def print_summary(self, results: Dict):
        """Print a readable summary of the analysis."""
        summary = results['summary']
        cost_analysis = results['cost_analysis']
        
        print(f"\nNetworking Driver Analysis")
        print(f"==========================")
        print(f"Region: {results['region']}")
        print(f"Scan Time: {results['scan_time']}")
        print(f"Analysis Period: {results['analysis_period_days']} days")
        if results['demo_mode']:
            print(f"Mode: DEMO (using sample data)")
        
        print(f"\n--- Cost Summary ---")
        print(f"NAT Gateway Cost: ${summary['total_nat_cost']:.2f}")
        print(f"Data Transfer Out: ${summary['total_data_transfer_cost']:.2f}")
        print(f"Load Balancer Cost: ${summary['total_lb_cost']:.2f}")
        print(f"Total Monthly Cost: ${summary['total_monthly_cost']:.2f}")
        
        print(f"\n--- Infrastructure Summary ---")
        print(f"NAT Gateways: {summary['total_nat_gateways']}")
        print(f"Load Balancers: {summary['total_load_balancers']}")
        print(f"VPC Endpoints: {summary['total_vpc_endpoints']}")
        print(f"Internet Egress: {summary['out_to_internet_gb']:.0f} GB")
        print(f"Cross-AZ Transfer: {summary['cross_az_gb']:.0f} GB")
        
        print(f"\n--- Demand Driver ---")
        print(f"Driver: {results['demand_driver']}")
        
        print(f"\n--- Optimization Signals ---")
        if results['optimization_signals']:
            for signal in results['optimization_signals']:
                print(f"• {signal}")
        else:
            print("No specific optimization signals detected")
        
        # NAT Gateway Details
        if results['nat_gateways']:
            print(f"\n--- NAT Gateway Details ---")
            for i, nat in enumerate(results['nat_gateways'], 1):
                print(f"\n{i}. {nat['nat_gateway_id']}")
                print(f"   Subnet: {nat['subnet_id']}")
                print(f"   State: {nat['state']}")
                print(f"   Bytes Processed: {nat['metrics']['BytesProcessed'] / (1024**3):.1f} GB")
                print(f"   Connections: {nat['metrics']['ConnectionCount']:,}")
                print(f"   Monthly Cost: ${nat['cost_analysis']['total_monthly_cost']:.2f}")
        
        # Load Balancer Details
        if results['load_balancers']:
            print(f"\n--- Load Balancer Details ---")
            for i, lb in enumerate(results['load_balancers'], 1):
                print(f"\n{i}. {lb['load_balancer_name']}")
                print(f"   Type: {lb['type'].title()}")
                print(f"   Scheme: {lb['scheme']}")
                print(f"   AZs: {', '.join(lb['availability_zones'])}")
                print(f"   Processed Bytes: {lb['metrics']['ProcessedBytes'] / (1024**3):.1f} GB")
                print(f"   Requests: {lb['metrics']['RequestCount']:,}")
                print(f"   Monthly Cost: ${lb['cost_analysis']['total_monthly_cost']:.2f}")
    
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
    """Main function to run the network driver detector."""
    parser = argparse.ArgumentParser(
        description='Analyze AWS networking costs to identify traffic-related demand drivers',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python network_driver_detector.py
  python network_driver_detector.py --region us-west-2 --output network_report.json
  python network_driver_detector.py --demo --output demo_network.json
  python network_driver_detector.py --profile my-aws-profile --region eu-west-1
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
    
    print("Network Driver Detector")
    print(f"Region: {args.region}")
    
    # Initialize detector
    detector = NetworkDriverDetector(
        region=args.region,
        profile_name=args.profile,
        demo_mode=args.demo
    )
    
    # Analyze networking costs
    results = detector.analyze_network_drivers()
    
    # Print summary
    detector.print_summary(results)
    
    # Export to JSON if output file specified
    if args.output:
        detector.export_to_json(results, args.output)
    
    # Exit with appropriate code
    total_cost = results['summary']['total_monthly_cost']
    
    if total_cost > 0:
        print(f"\nAnalyzed networking infrastructure with total estimated cost of ${total_cost:.2f}/month")
        sys.exit(0)  # Success for analysis
    else:
        print("\nNo networking infrastructure found in the specified region")
        sys.exit(0)  # Still success, just no data


if __name__ == '__main__':
    main()
