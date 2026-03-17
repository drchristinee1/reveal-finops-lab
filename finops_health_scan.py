#!/usr/bin/env python3
"""
FinOps Health Scan

This script orchestrates the existing cost anomaly detector and idle resource detector
to provide a comprehensive FinOps health assessment for AWS accounts.
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class FinOpsHealthScanner:
    """Orchestrates FinOps tools to provide comprehensive health assessment."""
    
    def __init__(self, region: str = 'us-east-1', profile_name: Optional[str] = None, demo_mode: bool = False):
        """Initialize the FinOps health scanner."""
        self.region = region
        self.profile_name = profile_name
        self.demo_mode = demo_mode
        self.temp_dir = tempfile.mkdtemp(prefix='finops_health_')
        
    def _run_script(self, script_name: str, args: List[str]) -> Tuple[bool, Optional[Dict]]:
        """
        Run a Python script and capture its JSON output.
        
        Args:
            script_name: Name of the script to run
            args: Command line arguments for the script
            
        Returns:
            Tuple of (success, data) where success is bool and data is parsed JSON or None
        """
        try:
            # Build command
            cmd = [sys.executable, script_name] + args
            
            # Add profile argument if specified
            if self.profile_name:
                cmd.extend(['--profile', self.profile_name])
            
            # Add demo mode if enabled
            if self.demo_mode and script_name == 'idle_detector.py':
                cmd.append('--demo')
            
            # For cost_anomaly.py, we need different demo handling
            if self.demo_mode and script_name == 'cost_anomaly.py':
                # In demo mode, we'll create mock data since cost_anomaly.py doesn't have demo mode
                return self._create_mock_cost_anomaly_data()
            
            # Run the script and capture output
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                print(f"Error running {script_name}: {result.stderr}")
                return False, None
            
            # Try to parse JSON from stdout or create mock data for demo mode
            if self.demo_mode:
                return self._create_mock_data_for_script(script_name)
            
            # For non-demo mode, try to find JSON in output
            try:
                # Look for JSON in the output (scripts might print text before JSON)
                lines = result.stdout.strip().split('\n')
                json_data = None
                
                for line in lines:
                    line = line.strip()
                    if line.startswith('{') and line.endswith('}'):
                        json_data = json.loads(line)
                        break
                
                if json_data:
                    return True, json_data
                else:
                    # If no JSON found, create a summary from the text output
                    return self._parse_text_output_to_json(script_name, result.stdout)
                    
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON from {script_name}: {e}")
                return self._parse_text_output_to_json(script_name, result.stdout)
                
        except subprocess.TimeoutExpired:
            print(f"Timeout running {script_name}")
            return False, None
        except Exception as e:
            print(f"Unexpected error running {script_name}: {e}")
            return False, None
    
    def _create_mock_cost_anomaly_data(self) -> Tuple[bool, Optional[Dict]]:
        """Create mock cost anomaly data for demo mode."""
        mock_data = {
            'scan_time': datetime.now().isoformat(),
            'lookback_days': 30,
            'threshold_percent': 25.0,
            'demo_mode': True,
            'cost_summary': {
                'period': '2024-02-15 to 2024-03-15',
                'average_daily_cost': 125.50,
                'maximum_daily_cost': 245.80,
                'minimum_daily_cost': 45.20,
                'total_period_cost': 3765.00
            },
            'anomalies': [
                {
                    'date': '2024-03-10',
                    'cost': 245.80,
                    'historical_avg': 118.25,
                    'percent_change': 107.89,
                    'anomaly_type': 'INCREASE',
                    'top_services': [
                        {'service': 'Amazon EC2', 'cost': 180.50},
                        {'service': 'Amazon RDS', 'cost': 45.30},
                        {'service': 'Amazon S3', 'cost': 12.80}
                    ]
                }
            ],
            'summary': {
                'total_anomalies': 1,
                'increase_anomalies': 1,
                'decrease_anomalies': 0
            }
        }
        return True, mock_data
    
    def _create_mock_data_for_script(self, script_name: str) -> Tuple[bool, Optional[Dict]]:
        """Create mock data for scripts in demo mode."""
        if script_name == 'idle_detector.py':
            mock_data = {
                'scan_time': datetime.now().isoformat(),
                'region': self.region,
                'demo_mode': True,
                'unattached_volumes': [
                    {
                        'VolumeId': 'vol-1234567890abcdef0',
                        'Size': 100,
                        'VolumeType': 'gp3',
                        'AvailabilityZone': 'us-east-1a',
                        'State': 'available',
                        'CreateTime': '2024-01-15T10:30:00Z',
                        'MonthlyCost': 8.00
                    }
                ],
                'unused_elastic_ips': [
                    {
                        'AllocationId': 'eipalloc-1234567890abcdef0',
                        'PublicIp': '203.0.113.1',
                        'Domain': 'vpc',
                        'AllocationTime': '2024-01-20T08:15:00Z',
                        'MonthlyCost': 3.65
                    }
                ],
                'summary': {
                    'total_unattached_volumes': 1,
                    'total_unused_elastic_ips': 1,
                    'total_monthly_savings': 11.65
                }
            }
            return True, mock_data
        
        return False, None
    
    def _parse_text_output_to_json(self, script_name: str, output: str) -> Tuple[bool, Optional[Dict]]:
        """Parse text output to create a basic JSON structure."""
        try:
            if script_name == 'cost_anomaly.py':
                # Parse cost anomaly text output
                lines = output.strip().split('\n')
                data = {
                    'scan_time': datetime.now().isoformat(),
                    'demo_mode': False,
                    'text_output': output,
                    'summary': {'total_anomalies': 0}
                }
                
                # Look for anomaly count
                for line in lines:
                    if 'Anomalies Detected' in line:
                        try:
                            count = int(line.split('===')[1].split()[0])
                            data['summary']['total_anomalies'] = count
                        except:
                            pass
                
                return True, data
            
            elif script_name == 'idle_detector.py':
                # Parse idle detector text output
                lines = output.strip().split('\n')
                data = {
                    'scan_time': datetime.now().isoformat(),
                    'region': self.region,
                    'demo_mode': False,
                    'text_output': output,
                    'summary': {
                        'total_unattached_volumes': 0,
                        'total_unused_elastic_ips': 0,
                        'total_monthly_savings': 0.0
                    }
                }
                
                # Look for resource counts
                for line in lines:
                    if 'Unattached EBS Volumes:' in line:
                        try:
                            count = int(line.split(':')[1].strip())
                            data['summary']['total_unattached_volumes'] = count
                        except:
                            pass
                    elif 'Unused Elastic IPs:' in line:
                        try:
                            count = int(line.split(':')[1].strip())
                            data['summary']['total_unused_elastic_ips'] = count
                        except:
                            pass
                    elif 'Potential Monthly Savings:' in line:
                        try:
                            savings = float(line.split('$')[1].strip())
                            data['summary']['total_monthly_savings'] = savings
                        except:
                            pass
                
                return True, data
            
        except Exception as e:
            print(f"Error parsing text output: {e}")
        
        return False, None
    
    def run_cost_anomaly_scan(self, lookback_days: int = 30, threshold: float = 25.0) -> Optional[Dict]:
        """Run the cost anomaly detector."""
        print("Running cost anomaly analysis...")
        
        args = [
            '--lookback-days', str(lookback_days),
            '--threshold', str(threshold)
        ]
        
        success, data = self._run_script('cost_anomaly.py', args)
        
        if success and data:
            print(f"✓ Cost anomaly analysis completed")
            return data
        else:
            print("✗ Cost anomaly analysis failed")
            return None
    
    def run_idle_resource_scan(self) -> Optional[Dict]:
        """Run the idle resource detector."""
        print("Running idle resource analysis...")
        
        args = ['--region', self.region]
        
        success, data = self._run_script('idle_detector.py', args)
        
        if success and data:
            print(f"✓ Idle resource analysis completed")
            return data
        else:
            print("✗ Idle resource analysis failed")
            return None
    
    def combine_results(self, cost_anomaly_data: Optional[Dict], idle_resource_data: Optional[Dict]) -> Dict:
        """
        Combine results from both scans into a comprehensive health report.
        
        Args:
            cost_anomaly_data: Results from cost anomaly scan
            idle_resource_data: Results from idle resource scan
            
        Returns:
            Combined health report
        """
        detector_results = {
    "cost_anomaly_analysis": cost_anomaly_data or {},
    "idle_resource_analysis": idle_resource_data or {}
}

unified = UnifiedDriversDetector(detector_results)
driver_analysis = unified.aggregate_results()
        report = {
            'scan_time': datetime.now().isoformat(),
            'region': self.region,
            'demo_mode': self.demo_mode,
            'profile_used': self.profile_name,
            'health_score': self._calculate_health_score(cost_anomaly_data, idle_resource_data),
            'cost_anomaly_analysis': cost_anomaly_data or {},
            'idle_resource_analysis': idle_resource_data or {},
            'recommendations': self._generate_recommendations(cost_anomaly_data, idle_resource_data),
            'summary': self._create_summary(cost_anomaly_data, idle_resource_data)
        }
        
        return report
    
    def _calculate_health_score(self, cost_anomaly_data: Optional[Dict], idle_resource_data: Optional[Dict]) -> Dict:
        """Calculate overall FinOps health score."""
        score = 100
        issues = []
        
        # Cost anomaly scoring
        if cost_anomaly_data:
            anomalies = cost_anomaly_data.get('summary', {}).get('total_anomalies', 0)
            if anomalies > 0:
                score -= min(anomalies * 10, 50)  # Deduct up to 50 points for anomalies
                issues.append(f"{anomalies} cost anomalies detected")
        
        # Idle resource scoring
        if idle_resource_data:
            idle_volumes = idle_resource_data.get('summary', {}).get('total_unattached_volumes', 0)
            idle_ips = idle_resource_data.get('summary', {}).get('total_unused_elastic_ips', 0)
            
            if idle_volumes > 0:
                score -= min(idle_volumes * 5, 25)  # Deduct up to 25 points for idle volumes
                issues.append(f"{idle_volumes} unattached EBS volumes")
            
            if idle_ips > 0:
                score -= min(idle_ips * 5, 25)  # Deduct up to 25 points for idle IPs
                issues.append(f"{idle_ips} unused Elastic IPs")
        
        score = max(0, score)  # Ensure score doesn't go below 0
        
        return {
            'overall_score': score,
            'grade': self._get_grade(score),
            'issues_found': issues,
            'status': 'HEALTHY' if score >= 80 else 'WARNING' if score >= 60 else 'CRITICAL'
        }
    
    def _get_grade(self, score: int) -> str:
        """Get letter grade for health score."""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def _generate_recommendations(self, cost_anomaly_data: Optional[Dict], idle_resource_data: Optional[Dict]) -> List[str]:
        """Generate actionable recommendations based on scan results."""
        recommendations = []
        
        # Cost anomaly recommendations
        if cost_anomaly_data:
            anomalies = cost_anomaly_data.get('summary', {}).get('total_anomalies', 0)
            if anomalies > 0:
                recommendations.append(f"Investigate {anomalies} cost anomalies to identify unexpected spending patterns")
                recommendations.append("Set up cost alerts to monitor future anomalies")
                recommendations.append("Review service usage for anomalous days")
        
        # Idle resource recommendations
        if idle_resource_data:
            idle_volumes = idle_resource_data.get('summary', {}).get('total_unattached_volumes', 0)
            idle_ips = idle_resource_data.get('summary', {}).get('total_unused_elastic_ips', 0)
            savings = idle_resource_data.get('summary', {}).get('total_monthly_savings', 0)
            
            if idle_volumes > 0:
                recommendations.append(f"Review and cleanup {idle_volumes} unattached EBS volumes")
                recommendations.append("Create snapshots before deleting important volumes")
            
            if idle_ips > 0:
                recommendations.append(f"Release {idle_ips} unused Elastic IP addresses")
            
            if savings > 0:
                recommendations.append(f"Potential monthly savings: ${savings:.2f} from resource cleanup")
        
        # General recommendations
        if not recommendations:
            recommendations.append("Excellent FinOps health! Continue monitoring for optimization opportunities")
        else:
            recommendations.append("Schedule regular FinOps health scans (recommended: weekly)")
            recommendations.append("Consider implementing automated cleanup policies for idle resources")
        
        return recommendations
    
    def _create_summary(self, cost_anomaly_data: Optional[Dict], idle_resource_data: Optional[Dict]) -> Dict:
        """Create a summary of all findings."""
        summary = {
            'total_issues': 0,
            'potential_monthly_savings': 0.0,
            'cost_anomalies': 0,
            'idle_volumes': 0,
            'idle_elastic_ips': 0
        }
        
        if cost_anomaly_data:
            summary['cost_anomalies'] = cost_anomaly_data.get('summary', {}).get('total_anomalies', 0)
            summary['total_issues'] += summary['cost_anomalies']
        
        if idle_resource_data:
            summary['idle_volumes'] = idle_resource_data.get('summary', {}).get('total_unattached_volumes', 0)
            summary['idle_elastic_ips'] = idle_resource_data.get('summary', {}).get('total_unused_elastic_ips', 0)
            summary['potential_monthly_savings'] = idle_resource_data.get('summary', {}).get('total_monthly_savings', 0)
            summary['total_issues'] += summary['idle_volumes'] + summary['idle_elastic_ips']
        
        return summary
    
    def print_console_report(self, report: Dict):
        """Print a readable console report."""
        print("\n" + "="*60)
        print("FINOPS HEALTH SCAN REPORT")
        print("="*60)
        
        health_score = report['health_score']
        print(f"Health Score: {health_score['overall_score']}/100 ({health_score['grade']})")
        print(f"Status: {health_score['status']}")
        print(f"Region: {report['region']}")
        print(f"Scan Time: {report['scan_time']}")
        if report['demo_mode']:
            print("Mode: DEMO (using sample data)")
        
        print(f"\n--- SUMMARY ---")
        summary = report['summary']
        print(f"Total Issues Found: {summary['total_issues']}")
        print(f"Cost Anomalies: {summary['cost_anomalies']}")
        print(f"Idle EBS Volumes: {summary['idle_volumes']}")
        print(f"Unused Elastic IPs: {summary['idle_elastic_ips']}")
        print(f"Potential Monthly Savings: ${summary['potential_monthly_savings']:.2f}")
        
        if health_score['issues_found']:
            print(f"\n--- ISSUES DETECTED ---")
            for issue in health_score['issues_found']:
                print(f"• {issue}")
        
        print(f"\n--- RECOMMENDATIONS ---")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"{i}. {rec}")
        
        print("\n" + "="*60)
    
    def export_report(self, report: Dict, output_file: str):
        """Export the combined report to JSON."""
        try:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"\nComprehensive report exported to: {output_file}")
        except Exception as e:
            print(f"Error exporting report: {e}")
    
    def cleanup(self):
        """Clean up temporary files."""
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
        except:
            pass


def main():
    """Main function to run the FinOps health scan."""
    parser = argparse.ArgumentParser(
        description='Comprehensive FinOps health scan combining cost anomaly and idle resource analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python finops_health_scan.py
  python finops_health_scan.py --region us-west-2 --output health_report.json
  python finops_health_scan.py --demo --output demo_health.json
  python finops_health_scan.py --profile my-aws-profile --region eu-west-1
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
        help='Run in demo mode with sample data (ignores AWS credentials)'
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
    
    args = parser.parse_args()
    
    print("FinOps Health Scanner")
    print(f"Region: {args.region}")
    print(f"Lookback Days: {args.lookback_days}")
    print(f"Anomaly Threshold: {args.threshold}%")
    
    # Initialize scanner
    scanner = FinOpsHealthScanner(
        region=args.region,
        profile_name=args.profile,
        demo_mode=args.demo
    )
    
    try:
        # Run both scans
        cost_anomaly_data = scanner.run_cost_anomaly_scan(args.lookback_days, args.threshold)
        idle_resource_data = scanner.run_idle_resource_scan()
        
        # Combine results
        print("\nCombining results...")
        report = scanner.combine_results(cost_anomaly_data, idle_resource_data)
        
        # Print console report
        scanner.print_console_report(report)
        
        # Export report
        scanner.export_report(report, args.output)
        
        # Exit with appropriate code
        health_score = report['health_score']['overall_score']
        if health_score < 60:
            print(f"\n⚠️  CRITICAL: Health score {health_score}/100 requires immediate attention")
            sys.exit(2)
        elif health_score < 80:
            print(f"\n⚠️  WARNING: Health score {health_score}/100 needs attention")
            sys.exit(1)
        else:
            print(f"\n✅ HEALTHY: Health score {health_score}/100 - Good FinOps practices")
            sys.exit(0)
    
    except KeyboardInterrupt:
        print("\nScan interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        scanner.cleanup()


if __name__ == '__main__':
    main()
