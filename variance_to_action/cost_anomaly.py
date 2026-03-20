#!/usr/bin/env python3
"""
AWS Cost Explorer Daily Cost Anomaly Detector

This script analyzes AWS daily costs using Cost Explorer and detects anomalies
by comparing daily costs against historical averages.
"""

import argparse
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import boto3
from botocore.exceptions import ClientError, NoCredentialsError


class CostAnomalyDetector:
    """Detects cost anomalies in AWS spending using Cost Explorer API."""
    
    def __init__(self, profile_name: Optional[str] = None):
        """Initialize the cost anomaly detector."""
        try:
            session = boto3.Session(profile_name=profile_name)
            self.ce_client = session.client('ce')
        except NoCredentialsError:
            print("Error: AWS credentials not found. Please configure your credentials.")
            sys.exit(1)
        except Exception as e:
            print(f"Error initializing AWS session: {e}")
            sys.exit(1)
    
    def get_daily_costs(self, lookback_days: int) -> List[Dict]:
        """
        Retrieve daily costs for the specified lookback period.
        
        Args:
            lookback_days: Number of days to look back for cost data
            
        Returns:
            List of daily cost records
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=lookback_days)
        
        try:
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity='DAILY',
                Metrics=['BlendedCost'],
                GroupBy=[
                    {
                        'Type': 'DIMENSION',
                        'Key': 'SERVICE'
                    }
                ]
            )
            
            return response.get('ResultsByTime', [])
        except ClientError as e:
            print(f"Error retrieving cost data: {e}")
            sys.exit(1)
    
    def calculate_daily_totals(self, cost_data: List[Dict]) -> List[Tuple[str, float]]:
        """
        Calculate total daily costs across all services.
        
        Args:
            cost_data: Raw cost data from Cost Explorer
            
        Returns:
            List of tuples containing (date, total_cost)
        """
        daily_totals = []
        
        for result in cost_data:
            date = result['TimePeriod']['Start']
            total_cost = 0.0
            
            for group in result.get('Groups', []):
                amount = float(group['Metrics']['BlendedCost']['Amount'])
                total_cost += amount
            
            daily_totals.append((date, total_cost))
        
        return sorted(daily_totals)
    
    def detect_anomalies(self, daily_totals: List[Tuple[str, float]], 
                        threshold_percent: float) -> List[Dict]:
        """
        Detect cost anomalies based on percentage deviation from historical average.
        
        Args:
            daily_totals: List of (date, cost) tuples
            threshold_percent: Percentage threshold for anomaly detection
            
        Returns:
            List of anomaly records
        """
        if len(daily_totals) < 2:
            print("Warning: Need at least 2 days of data for anomaly detection")
            return []
        
        anomalies = []
        
        for i, (date, current_cost) in enumerate(daily_totals):
            if i == 0:
                continue  # Skip first day as we need historical data
            
            # Calculate historical average (excluding current day)
            historical_costs = [cost for _, cost in daily_totals[:i]]
            historical_avg = sum(historical_costs) / len(historical_costs)
            
            if historical_avg == 0:
                continue  # Avoid division by zero
            
            # Calculate percentage change
            percent_change = ((current_cost - historical_avg) / historical_avg) * 100
            
            if abs(percent_change) >= threshold_percent:
                anomalies.append({
                    'date': date,
                    'cost': current_cost,
                    'historical_avg': historical_avg,
                    'percent_change': percent_change,
                    'anomaly_type': 'INCREASE' if percent_change > 0 else 'DECREASE'
                })
        
        return anomalies
    
    def get_service_breakdown(self, date: str) -> List[Dict]:
        """
        Get service-level cost breakdown for a specific date.
        
        Args:
            date: Date in YYYY-MM-DD format
            
        Returns:
            List of service cost records
        """
        try:
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': date,
                    'End': (datetime.strptime(date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
                },
                Granularity='DAILY',
                Metrics=['BlendedCost'],
                GroupBy=[
                    {
                        'Type': 'DIMENSION',
                        'Key': 'SERVICE'
                    }
                ]
            )
            
            services = []
            for result in response.get('ResultsByTime', []):
                for group in result.get('Groups', []):
                    service_name = group['Keys'][0]
                    amount = float(group['Metrics']['BlendedCost']['Amount'])
                    
                    if amount > 0:  # Only include services with costs
                        services.append({
                            'service': service_name,
                            'cost': amount
                        })
            
            return sorted(services, key=lambda x: x['cost'], reverse=True)
        except ClientError as e:
            print(f"Error retrieving service breakdown for {date}: {e}")
            return []
    
    def print_summary(self, daily_totals: List[Tuple[str, float]]):
        """Print summary statistics for the cost data."""
        if not daily_totals:
            print("No cost data available")
            return
        
        total_costs = [cost for _, cost in daily_totals]
        avg_daily_cost = sum(total_costs) / len(total_costs)
        max_cost = max(total_costs)
        min_cost = min(total_costs)
        
        print(f"\n=== Cost Summary ===")
        print(f"Period: {daily_totals[0][0]} to {daily_totals[-1][0]}")
        print(f"Average Daily Cost: ${avg_daily_cost:.2f}")
        print(f"Maximum Daily Cost: ${max_cost:.2f}")
        print(f"Minimum Daily Cost: ${min_cost:.2f}")
        print(f"Total Period Cost: ${sum(total_costs):.2f}")
    
    def print_anomalies(self, anomalies: List[Dict]):
        """Print detected anomalies with details."""
        if not anomalies:
            print("\n=== No Anomalies Detected ===")
            return
        
        print(f"\n=== {len(anomalies)} Anomalies Detected ===")
        for anomaly in anomalies:
            print(f"\nDate: {anomaly['date']}")
            print(f"Cost: ${anomaly['cost']:.2f}")
            print(f"Historical Average: ${anomaly['historical_avg']:.2f}")
            print(f"Change: {anomaly['percent_change']:+.2f}%")
            print(f"Type: {anomaly['anomaly_type']}")
            
            # Get service breakdown for anomaly date
            services = self.get_service_breakdown(anomaly['date'])
            if services:
                print("Top Services:")
                for i, service in enumerate(services[:5], 1):
                    print(f"  {i}. {service['service']}: ${service['cost']:.2f}")


def main():
    """Main function to run the cost anomaly detector."""
    parser = argparse.ArgumentParser(
        description='Detect AWS cost anomalies using Cost Explorer data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cost_anomaly.py --lookback-days 30 --threshold 25
  python cost_anomaly.py --lookback-days 14 --threshold 50 --profile my-aws-profile
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
    
    args = parser.parse_args()
    
    if args.lookback_days < 2:
        print("Error: lookback-days must be at least 2")
        sys.exit(1)
    
    if args.threshold <= 0:
        print("Error: threshold must be greater than 0")
        sys.exit(1)
    
    print(f"AWS Cost Anomaly Detector")
    print(f"Lookback Period: {args.lookback_days} days")
    print(f"Anomaly Threshold: {args.threshold}%")
    
    # Initialize detector
    detector = CostAnomalyDetector(profile_name=args.profile)
    
    # Get cost data
    print("Retrieving cost data...")
    cost_data = detector.get_daily_costs(args.lookback_days)
    
    # Calculate daily totals
    daily_totals = detector.calculate_daily_totals(cost_data)
    
    if not daily_totals:
        print("No cost data found for the specified period")
        sys.exit(1)
    
    # Print summary
    detector.print_summary(daily_totals)
    
    # Detect anomalies
    print("Detecting anomalies...")
    anomalies = detector.detect_anomalies(daily_totals, args.threshold)
    
    # Print anomalies
    detector.print_anomalies(anomalies)


if __name__ == '__main__':
    main()