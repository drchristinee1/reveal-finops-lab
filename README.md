# Reveal FinOps Lab

A prototype FinOps automation framework for translating cloud cost signals into operational workflows and engineering actions.

## Key Features

- Cost anomaly detection  
- Idle resource analysis  
- Service-level cost drivers (EC2, RDS, DynamoDB, S3)  
- CLI-based health scan execution  
- Structured output for decision-making  

## Goal

Move FinOps from reporting → operational cost intelligence.

# AWS FinOps Tools

A comprehensive suite of Python scripts for AWS cost optimization and resource management, including cost anomaly detection, idle resource analysis, rightsizing recommendations, and unified health scanning.

## Quick Start

### Unified CLI (Recommended)

Use the unified `finops.py` CLI for easy access to all tools:

```bash
# Make the CLI executable
chmod +x finops.py

# Run different analyses
python finops.py anomalies --lookback-days 30 --threshold 25
python finops.py idle --region us-west-2 --output idle_report.json
python finops.py rightsizing --demo --profile production
python finops.py health --region eu-west-1 --output health_report.json
```

### Individual Scripts

Or run individual scripts directly:

```bash
python cost_anomaly.py --lookback-days 30 --threshold 25
python idle_detector.py --region us-west-2 --output idle_report.json
python rightsizing_detector.py --demo --profile production
python finops_health_scan.py --region eu-west-1 --output health_report.json
```

## Features

- **Cost Anomaly Detection**: Identify unusual spending patterns using AWS Cost Explorer
- **Idle Resource Detection**: Find unattached EBS volumes and unused Elastic IPs
- **EC2 Rightsizing**: Optimize EC2 instances based on CPU utilization
- **Comprehensive Health Scan**: Unified analysis with health scoring and recommendations
- **Demo Mode**: Test all tools with sample data without AWS credentials
- **Multi-Region Support**: Analyze resources across different AWS regions
- **JSON Export**: Detailed reports for integration and automation
- **AWS Profile Support**: Use different AWS credentials profiles

## Prerequisites

- Python 3.7 or higher
- AWS account with appropriate permissions
- Configured AWS credentials (optional - demo mode available)

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Make the unified CLI executable (optional):

```bash
chmod +x finops.py
```

## Unified CLI Usage

The `finops.py` script provides a unified interface to all FinOps tools.

### Available Commands

| Command | Description | Script |
|---------|-------------|---------|
| `anomalies` | Detect cost anomalies in AWS spending | `cost_anomaly.py` |
| `idle` | Detect idle AWS resources | `idle_detector.py` |
| `rightsizing` | Detect EC2 rightsizing opportunities | `rightsizing_detector.py` |
| `health` | Comprehensive FinOps health scan | `finops_health_scan.py` |
| `drivers lambda` | Analyze Lambda workload demand drivers | `driver_detector.py` |
| `drivers dynamodb` | Analyze DynamoDB workload demand drivers | `dynamodb_driver_detector.py` |
| `drivers rds` | Analyze RDS workload demand drivers | `rds_driver_detector.py` |
| `drivers ec2` | Analyze EC2 compute demand drivers | `ec2_driver_detector.py` |
| `drivers s3` | Analyze S3 storage demand drivers | `s3_driver_detector.py` |
| `drivers network` | Analyze network traffic demand drivers | `network_driver_detector.py` |
| `drivers all` | Run unified analysis of all demand drivers | `unified_drivers_detector.py` |

### Global Options

These options are available across multiple commands:

- `--region <region>`: AWS region to scan (default: us-east-1)
- `--profile <profile>`: AWS profile name to use
- `--demo`: Run in demo mode with sample data
- `--output <file>`: Export results to JSON file

### Command Examples

#### Cost Anomaly Analysis

```bash
# Basic anomaly detection
python finops.py anomalies

# Custom lookback period and threshold
python finops.py anomalies --lookback-days 60 --threshold 15

# Using specific AWS profile
python finops.py anomalies --profile production
```

#### Idle Resource Detection

```bash
# Scan default region
python finops.py idle

# Scan specific region and export results
python finops.py idle --region us-west-2 --output idle_report.json

# Demo mode for testing
python finops.py idle --demo --profile production
```

#### EC2 Rightsizing

```bash
# Analyze EC2 instances for rightsizing
python finops.py rightsizing

# Scan specific region with output
python finops.py rightsizing --region eu-west-1 --output rightsizing_report.json

# Demo mode testing
python finops.py rightsizing --demo
```

#### Comprehensive Health Scan

```bash
# Full health assessment
python finops.py health

# Custom health scan parameters
python finops.py health --region us-west-2 --lookback-days 60 --threshold 15

# Demo mode with custom output
python finops.py health --demo --output demo_health.json
```

#### Lambda Driver Analysis

```bash
# Analyze Lambda functions for demand drivers
python finops.py drivers lambda

# Scan specific region with output
python finops.py drivers lambda --region eu-west-1 --output driver_report.json

# Demo mode testing
python finops.py drivers lambda --demo
```

#### Unified Drivers Analysis

```bash
# Run unified analysis of all demand drivers
python finops.py drivers all

# Scan specific region with output
python finops.py drivers all --region eu-west-1 --output unified_drivers_report.json

# Demo mode testing
python finops.py drivers all --demo
```

### Help and Version

```bash
# Show main help
python finops.py --help

# Show help for specific command
python finops.py anomalies --help
python finops.py idle --help
python finops.py rightsizing --help
python finops.py health --help
python finops.py drivers --help
python finops.py drivers lambda --help
python finops.py drivers dynamodb --help
python finops.py drivers rds --help
python finops.py drivers ec2 --help
python finops.py drivers s3 --help
python finops.py drivers network --help
python finops.py drivers all --help

# Show version
python finops.py --version
```

## Individual Script Usage

### Cost Anomaly Detector

See [Cost Anomaly Detection](#cost-anomaly-detector) section for detailed usage.

### Idle Resource Detector

See [AWS Idle Resource Detector](#aws-idle-resource-detector) section for detailed usage.

### EC2 Rightsizing Detector

See [EC2 Rightsizing Detector](#ec2-rightsizing-detector) section for detailed usage.

### FinOps Health Scan

See [FinOps Health Scan](#finops-health-scan) section for detailed usage.

### Lambda Driver Detector

See [Lambda Driver Detector](#lambda-driver-detector) section for detailed usage.

### DynamoDB Driver Detector

See [DynamoDB Driver Detector](#dynamodb-driver-detector) section for detailed usage.

### RDS Driver Detector

See [RDS Driver Detector](#rds-driver-detector) section for detailed usage.

### EC2 Driver Detector

See [EC2 Driver Detector](#ec2-driver-detector) section for detailed usage.

### S3 Driver Detector

See [S3 Driver Detector](#s3-driver-detector) section for detailed usage.

### Network Driver Detector

See [Network Driver Detector](#network-driver-detector) section for detailed usage.

### Unified Drivers Detector

See [Unified Drivers Detector](#unified-drivers-detector) section for detailed usage.

## AWS Permissions

The scripts require the following AWS IAM permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ce:GetCostAndUsage",
                "ec2:DescribeVolumes",
                "ec2:DescribeAddresses",
                "ec2:DescribeInstances",
                "ec2:DescribeNatGateways",
                "ec2:DescribeLoadBalancers",
                "ec2:DescribeVpcEndpoints",
                "cloudwatch:GetMetricStatistics",
                "lambda:ListFunctions",
                "dynamodb:ListTables",
                "dynamodb:DescribeTable",
                "rds:DescribeDBInstances",
                "rds:DescribeDBClusters",
                "s3:ListAllMyBuckets",
                "s3:GetBucketLocation",
                "s3:GetBucketTagging",
                "elasticloadbalancing:DescribeLoadBalancers"
            ],
            "Resource": "*"
        }
    ]
}
```

## Demo Mode

All tools support demo mode for testing without AWS credentials:

```bash
# Test individual tools
python finops.py anomalies --demo
python finops.py idle --demo
python finops.py rightsizing --demo
python finops.py health --demo
python finops.py drivers lambda --demo
python finops.py drivers dynamodb --demo
python finops.py drivers rds --demo
python finops.py drivers ec2 --demo
python finops.py drivers s3 --demo
python finops.py drivers network --demo
python finops.py drivers all --demo

# Or run individual scripts
python cost_anomaly.py --demo
python idle_detector.py --demo
python rightsizing_detector.py --demo
python finops_health_scan.py --demo
python driver_detector.py --demo
python dynamodb_driver_detector.py --demo
python rds_driver_detector.py --demo
python ec2_driver_detector.py --demo
python s3_driver_detector.py --demo
python network_driver_detector.py --demo
python unified_drivers_detector.py --demo
```

Demo mode provides realistic sample data to:
- Test script functionality
- Validate output format
- Develop integrations
- Train team members

## Output Formats

### Console Output

All tools provide readable console output with summaries and recommendations.

### JSON Export

Most tools support JSON export for automation and integration:

```bash
# Export individual tool results
python finops.py idle --output idle_report.json
python finops.py rightsizing --output rightsizing_report.json
python finops.py health --output health_report.json
```

### Exit Codes

- **0**: Success, no issues found
- **1**: Issues detected or script failure
- **2**: Critical issues (health scan only)

Use exit codes for automation:
```bash
python finops.py health
if [ $? -eq 1 ]; then
    echo "FinOps issues detected - review recommendations"
fi
```

## Automation and Integration

### Cron Jobs

```bash
# Weekly FinOps health scan
0 9 * * 1 cd /path/to/finops-cost-anomaly && python finops.py health --output "health_$(date +\%Y\%m\%d).json"

# Daily idle resource check
0 8 * * * cd /path/to/finops-cost-anomaly && python finops.py idle --output "idle_$(date +\%Y\%m\%d).json"

# Monthly rightsizing analysis
0 6 1 * * cd /path/to/finops-cost-anomaly && python finops.py rightsizing --output "rightsizing_$(date +\%Y\%m\%d).json"
```

### GitHub Actions

```yaml
name: FinOps Health Check
on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9 AM
  workflow_dispatch:

jobs:
  finops-health:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run FinOps Health Scan
        run: python finops.py health --region ${{ env.AWS_REGION }} --output health_report.json
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          AWS_REGION: us-east-1
      - name: Upload Report
        uses: actions/upload-artifact@v2
        with:
          name: finops-health-report
          path: health_report.json
```

### Multi-Region Analysis

```bash
# Script to analyze all regions
#!/bin/bash
REGIONS=("us-east-1" "us-west-2" "eu-west-1" "ap-southeast-1")
DATE=$(date +%Y%m%d)

for region in "${REGIONS[@]}"; do
    echo "Scanning region: $region"
    python finops.py health --region $region --output "health_${region}_${DATE}.json"
done
```

## Extending the CLI

The `finops.py` CLI is designed to be easily extensible:

1. **Add New Commands**: Update the `script_mapping` dictionary
2. **Add Subcommand Parsers**: Create new `_add_*_parser` methods
3. **Update Argument Building**: Modify `build_script_args` method
4. **Create New Scripts**: Add new analysis scripts following the existing patterns

Example extension structure:
```python
# In finops.py
self.script_mapping['tags'] = 'tag_optimizer.py'

def _add_tags_parser(self, subparsers):
    # Add tags subcommand parser
    pass
```

## Cost Anomaly Detector

A Python script that detects idle AWS resources to help optimize costs by identifying unattached EBS volumes and unused Elastic IP addresses. Includes demo mode for testing without AWS credentials.

## Features

- **Unattached EBS Volume Detection**: Finds available EBS volumes not attached to any EC2 instance
- **Unused Elastic IP Detection**: Identifies Elastic IP addresses that are not associated with any resource
- **Cost Analysis**: Calculates potential monthly savings from cleaning up idle resources
- **JSON Export**: Export detailed results to JSON file for further analysis
- **Demo Mode**: Test the script with sample data when AWS credentials are unavailable
- **Multi-Region Support**: Scan specific AWS regions
- **AWS Profile Support**: Use different AWS credentials profiles
- **Comprehensive Error Handling**: Graceful handling of AWS API errors and connection issues

## Prerequisites

- Python 3.7 or higher
- AWS account with EC2 access (for production use)
- Configured AWS credentials (optional - demo mode available)

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## AWS Permissions

The script requires the following AWS IAM permissions for production use:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeVolumes",
                "ec2:DescribeAddresses"
            ],
            "Resource": "*"
        }
    ]
}
```

## Usage

### Demo Mode (No AWS Credentials Required)

Perfect for testing the script functionality:

```bash
python idle_detector.py --demo
```

### Basic Usage

Scan your default AWS region:

```bash
python idle_detector.py
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--region` | AWS region to scan | us-east-1 |
| `--output` | Output JSON file path | None |
| `--profile` | AWS profile name to use | None |
| `--demo` | Run in demo mode with sample data | False |

### Examples

1. **Scan specific region and export results:**
   ```bash
   python idle_detector.py --region us-west-2 --output results.json
   ```

2. **Use specific AWS profile:**
   ```bash
   python idle_detector.py --profile production --region eu-west-1
   ```

3. **Demo mode with JSON export:**
   ```bash
   python idle_detector.py --demo --output demo_results.json
   ```

4. **Quick scan of multiple regions:**
   ```bash
   for region in us-east-1 us-west-2 eu-west-1; do
       python idle_detector.py --region $region --output "results_$region.json"
   done
   ```

## Output

### Console Output

The script provides a summary of findings in the console:

```
AWS Idle Resource Detector
Region: us-east-1
Scanning for idle AWS resources...

=== AWS Idle Resource Summary ===
Region: us-east-1
Scan Time: 2024-03-15T10:30:00.123456

Unattached EBS Volumes: 2
Unused Elastic IPs: 1
Potential Monthly Savings: $23.90

--- Unattached EBS Volumes ---
Volume ID: vol-1234567890abcdef0
  Size: 100 GB
  Type: gp3
  AZ: us-east-1a
  Created: 2024-01-15T10:30:00Z
  Monthly Cost: $8.00

Volume ID: vol-0fedcba9876543210
  Size: 50 GB
  Type: gp2
  AZ: us-east-1b
  Created: 2024-02-01T14:20:00Z
  Monthly Cost: $5.00

--- Unused Elastic IP Addresses ---
Allocation ID: eipalloc-1234567890abcdef0
  Public IP: 203.0.113.1
  Domain: vpc
  Allocated: 2024-01-20T08:15:00Z
  Monthly Cost: $3.65
```

### JSON Export

When using the `--output` option, results are exported in JSON format:

```json
{
  "scan_time": "2024-03-15T10:30:00.123456",
  "region": "us-east-1",
  "demo_mode": false,
  "unattached_volumes": [
    {
      "VolumeId": "vol-1234567890abcdef0",
      "Size": 100,
      "VolumeType": "gp3",
      "AvailabilityZone": "us-east-1a",
      "State": "available",
      "CreateTime": "2024-01-15T10:30:00Z",
      "MonthlyCost": 8.0
    }
  ],
  "unused_elastic_ips": [
    {
      "AllocationId": "eipalloc-1234567890abcdef0",
      "PublicIp": "203.0.113.1",
      "Domain": "vpc",
      "AllocationTime": "2024-01-20T08:15:00Z",
      "MonthlyCost": 3.65
    }
  ],
  "summary": {
    "total_unattached_volumes": 1,
    "total_unused_elastic_ips": 1,
    "total_monthly_savings": 11.65
  }
}
```

## How It Works

### EBS Volume Detection
- Scans for volumes with status 'available'
- Calculates monthly cost based on volume type and size
- Excludes volumes attached to instances

### Elastic IP Detection
- Identifies EIPs without active associations
- Calculates standard EIP pricing ($3.65/month when unattached)
- Includes both VPC and standard domain EIPs

### Cost Calculations
- Uses simplified pricing models (actual costs vary by region)
- EBS pricing based on volume type and size
- Additional IOPS costs calculated for io1/io2 volumes

## Demo Mode

Demo mode provides sample data to test the script without AWS credentials:

- **2 unattached EBS volumes** with different sizes and types
- **2 unused Elastic IP addresses** in VPC domain
- **Realistic cost calculations** based on current AWS pricing

Use demo mode to:
- Test script functionality
- Validate output format
- Develop integrations
- Train team members

## Configuration Tips

### Region Selection
- **Single Region**: Focus on your primary AWS region
- **Multiple Regions**: Scan all regions where you have resources
- **Regional Pricing**: Costs vary by region, calculations use estimates

### Automation Ideas
1. **Daily Scans**: Schedule regular scans to catch new idle resources
2. **Cost Alerts**: Integrate with monitoring systems for cost alerts
3. **Cleanup Automation**: Use JSON output for automated cleanup workflows
4. **Reporting**: Aggregate results across regions for comprehensive reports

### Best Practices
1. **Test First**: Always use demo mode to test before production runs
2. **Verify Resources**: Double-check before deleting resources
3. **Snapshot Volumes**: Create EBS snapshots before volume deletion
4. **Monitor Changes**: Track resource cleanup over time

## Troubleshooting

### Common Issues

1. **"AWS credentials not found"**
   - Configure AWS credentials in ~/.aws/credentials
   - Use --demo flag to test without credentials
   - Check environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)

2. **"Error retrieving EBS volumes"**
   - Verify EC2 permissions in IAM policy
   - Check if the specified region is correct
   - Ensure AWS credentials have necessary permissions

3. **"Error exporting results"**
   - Check file path permissions
   - Ensure directory exists
   - Verify write access to output location

4. **No resources found**
   - Verify you have resources in the scanned region
   - Check if resources are actually idle
   - Try scanning multiple regions

### Debug Mode

For additional debugging, you can:
- Use `--demo` mode to verify script functionality
- Check AWS credentials with `aws sts get-caller-identity`
- Verify region with `aws ec2 describe-regions`

## Exit Codes

- **0**: No idle resources found
- **1**: Idle resources detected (or error occurred)

Use exit codes for automation and scripting:
```bash
python idle_detector.py --region us-west-2
if [ $? -eq 1 ]; then
    echo "Idle resources found - check cleanup"
fi
```

## Integration Examples

### Bash Script for Multi-Region Scan
```bash
#!/bin/bash
REGIONS=("us-east-1" "us-west-2" "eu-west-1")
OUTPUT_DIR="idle_resources_$(date +%Y%m%d)"
mkdir -p $OUTPUT_DIR

for region in "${REGIONS[@]}"; do
    echo "Scanning region: $region"
    python idle_detector.py --region $region --output "$OUTPUT_DIR/idle_$region.json"
done
```

### Python Integration
```python
import json
from idle_detector import IdleResourceDetector

detector = IdleResourceDetector(region='us-east-1', demo_mode=True)
results = detector.scan_resources()

if results['summary']['total_monthly_savings'] > 0:
    print(f"Potential savings: ${results['summary']['total_monthly_savings']:.2f}")
```

## License

This project is provided as-is for educational and operational use. Always verify resources before deletion and follow AWS best practices for resource management.

## FinOps Health Scan

The `finops_health_scan.py` script orchestrates both the cost anomaly detector and idle resource detector to provide a comprehensive FinOps health assessment for your AWS account.

### Features

- **Comprehensive Analysis**: Combines cost anomaly and idle resource detection
- **Health Scoring**: Provides an overall FinOps health score (0-100) with letter grades
- **Actionable Recommendations**: Generates specific recommendations based on findings
- **Combined Reporting**: Single JSON report with all findings and analysis
- **Demo Mode**: Test with sample data when AWS credentials unavailable

### Usage

#### Basic Health Scan

```bash
python finops_health_scan.py
```

#### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--region` | AWS region to scan | us-east-1 |
| `--output` | Output JSON file path | finops_health_report.json |
| `--profile` | AWS profile name to use | None |
| `--demo` | Run in demo mode with sample data | False |
| `--lookback-days` | Days for cost anomaly analysis | 30 |
| `--threshold` | Cost anomaly threshold percentage | 25.0 |

#### Examples

1. **Comprehensive health scan with custom output:**
   ```bash
   python finops_health_scan.py --region us-west-2 --output my_health_report.json
   ```

2. **Demo mode for testing:**
   ```bash
   python finops_health_scan.py --demo --output demo_health.json
   ```

3. **Custom analysis parameters:**
   ```bash
   python finops_health_scan.py --lookback-days 60 --threshold 15 --profile production
   ```

4. **High-sensitivity scan:**
   ```bash
   python finops_health_scan.py --lookback-days 14 --threshold 10
   ```

### Health Score Interpretation

| Score Range | Grade | Status | Action Required |
|-------------|-------|---------|-----------------|
| 90-100 | A | HEALTHY | Continue monitoring |
| 80-89 | B | HEALTHY | Minor optimizations recommended |
| 70-79 | C | WARNING | Review and address issues |
| 60-69 | D | WARNING | Immediate attention needed |
| 0-59 | F | CRITICAL | Urgent action required |

### Sample Output

```
============================================================
FINOPS HEALTH SCAN REPORT
============================================================
Health Score: 75/100 (C)
Status: WARNING
Region: us-east-1
Scan Time: 2024-03-15T10:30:00.123456

--- SUMMARY ---
Total Issues Found: 3
Cost Anomalies: 1
Idle EBS Volumes: 2
Unused Elastic IPs: 0
Potential Monthly Savings: $16.50

--- ISSUES DETECTED ---
• 1 cost anomalies detected
• 2 unattached EBS volumes

--- RECOMMENDATIONS ---
1. Investigate 1 cost anomalies to identify unexpected spending patterns
2. Set up cost alerts to monitor future anomalies
3. Review service usage for anomalous days
4. Review and cleanup 2 unattached EBS volumes
5. Create snapshots before deleting important volumes
6. Potential monthly savings: $16.50 from resource cleanup
7. Schedule regular FinOps health scans (recommended: weekly)
8. Consider implementing automated cleanup policies for idle resources

============================================================

Comprehensive report exported to: finops_health_report.json

⚠️  WARNING: Health score 75/100 needs attention
```

### JSON Report Structure

The combined JSON report includes:

```json
{
  "scan_time": "2024-03-15T10:30:00.123456",
  "region": "us-east-1",
  "demo_mode": false,
  "profile_used": null,
  "health_score": {
    "overall_score": 75,
    "grade": "C",
    "issues_found": ["1 cost anomalies detected", "2 unattached EBS volumes"],
    "status": "WARNING"
  },
  "cost_anomaly_analysis": { ... },
  "idle_resource_analysis": { ... },
  "recommendations": [ ... ],
  "summary": {
    "total_issues": 3,
    "potential_monthly_savings": 16.50,
    "cost_anomalies": 1,
    "idle_volumes": 2,
    "idle_elastic_ips": 0
  }
}
```

### Integration with CI/CD

#### GitHub Actions Example

```yaml
name: FinOps Health Check
on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9 AM
  workflow_dispatch:

jobs:
  finops-health:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run FinOps Health Scan
        run: python finops_health_scan.py --region ${{ env.AWS_REGION }} --output health_report.json
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          AWS_REGION: us-east-1
      - name: Upload Report
        uses: actions/upload-artifact@v2
        with:
          name: finops-health-report
          path: health_report.json
```

#### Cron Job Setup

```bash
# Add to crontab for weekly health scans
0 9 * * 1 cd /path/to/finops-cost-anomaly && python finops_health_scan.py --output "health_$(date +\%Y\%m\%d).json"
```

## Lambda Driver Detector

The `driver_detector.py` script analyzes Lambda functions to identify workload demand drivers that influence cloud costs through usage patterns and metrics.

### Features

- **Lambda Function Discovery**: Lists all active Lambda functions in the specified region
- **CloudWatch Metrics Analysis**: Retrieves invocation counts, duration, errors, and throttles
- **Cost Estimation**: Calculates Lambda compute costs using sample pricing models
- **Demand Driver Identification**: Analyzes patterns to identify workload drivers
- **Performance Analysis**: Calculates error rates and throttle rates
- **Demo Mode**: Test with realistic sample Lambda data when AWS credentials unavailable

### Prerequisites

The script requires the following AWS IAM permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "lambda:ListFunctions",
                "cloudwatch:GetMetricStatistics"
            ],
            "Resource": "*"
        }
    ]
}
```

### Usage

#### Demo Mode (No AWS Credentials Required)

Test the script with realistic sample data:

```bash
python driver_detector.py --demo
```

#### Basic Usage

Scan your default AWS region:

```bash
python driver_detector.py
```

#### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--region` | AWS region to scan | us-east-1 |
| `--output` | Output JSON file path | None |
| `--profile` | AWS profile name to use | None |
| `--demo` | Run in demo mode with sample data | False |

#### Examples

1. **Scan specific region and export results:**
   ```bash
   python driver_detector.py --region us-west-2 --output driver_report.json
   ```

2. **Use specific AWS profile:**
   ```bash
   python driver_detector.py --profile production --region eu-west-1
   ```

### Output

#### Console Output

The script provides a detailed analysis of Lambda drivers:

```
Lambda Driver Detector
Region: us-east-1
Analyzing Lambda functions for demand drivers...

=== Lambda Driver Analysis ===
Region: us-east-1
Scan Time: 2024-03-15T10:30:00.123456
Analysis Period: 30 days

--- Summary ---
Total Functions Analyzed: 4
Total Invocations: 5,225,000
Estimated Monthly Cost: $89.75
Unique Demand Drivers: 4

--- Demand Drivers ---

API requests:
  Functions: order-processing
  Invocations: 1,200,000
  Cost: $35.00

User uploads:
  Functions: image-thumbnailer
  Invocations: 450,000
  Cost: $28.50

--- Function Details ---

1. order-processing
   Runtime: python3.9
   Memory: 512 MB
   Invocations: 1,200,000
   Average Duration: 140 ms
   Estimated Monthly Cost: $35.00
   Cost per Invocation: $0.000029
   Driver: API requests
```

### How It Works

#### Demand Driver Identification
The script uses pattern recognition to identify drivers:

- **API Requests**: High invocation count, low duration
- **User Authentication**: Very high invocation count, very low duration
- **User Uploads**: Functions with upload/image-related names
- **Scheduled Jobs**: Functions with process/batch/job-related names
- **Data Processing**: High duration functions

## DynamoDB Driver Detector

The `dynamodb_driver_detector.py` script analyzes DynamoDB tables to identify workload demand drivers that influence cloud costs through usage patterns and storage.

### Features

- **Table Discovery**: Lists all active DynamoDB tables in the specified region
- **CloudWatch Metrics Analysis**: Retrieves read/write capacity usage over time
- **Storage Analysis**: Calculates table storage usage in GB
- **Cost Estimation**: Calculates DynamoDB costs using sample pricing models
- **Demand Driver Identification**: Analyzes patterns to identify workload drivers
- **Unit Economics**: Calculates cost per 1,000 requests and cost per table
- **Demo Mode**: Test with realistic sample DynamoDB data when AWS credentials unavailable

### Prerequisites

The script requires the following AWS IAM permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:ListTables",
                "dynamodb:DescribeTable",
                "cloudwatch:GetMetricStatistics"
            ],
            "Resource": "*"
        }
    ]
}
```

### Usage

#### Demo Mode (No AWS Credentials Required)

Test the script with realistic sample data:

```bash
python dynamodb_driver_detector.py --demo
```

#### Basic Usage

Scan your default AWS region:

```bash
python dynamodb_driver_detector.py
```

#### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--region` | AWS region to scan | us-east-1 |
| `--output` | Output JSON file path | None |
| `--profile` | AWS profile name to use | None |
| `--demo` | Run in demo mode with sample data | False |

#### Examples

1. **Scan specific region and export results:**
   ```bash
   python dynamodb_driver_detector.py --region us-west-2 --output dynamodb_report.json
   ```

2. **Use specific AWS profile:**
   ```bash
   python dynamodb_driver_detector.py --profile production --region eu-west-1
   ```

3. **Demo mode with JSON export:**
   ```bash
   python dynamodb_driver_detector.py --demo --output demo_dynamodb.json
   ```

### Output

#### Console Output

The script provides a detailed analysis of DynamoDB drivers:

```
DynamoDB Driver Detector
Region: us-east-1
Analyzing DynamoDB tables for demand drivers...

=== DynamoDB Driver Analysis ===
Region: us-east-1
Scan Time: 2024-03-15T10:30:00.123456
Analysis Period: 30 days

--- Summary ---
Total Tables Analyzed: 4
Total Reads: 14,000,000
Total Writes: 9,450,000
Total Storage: 78.0 GB
Estimated Monthly Cost: $28.95
Unique Demand Drivers: 4
Average Cost per Table: $7.24

--- Demand Drivers ---

Session activity:
  Tables: user-sessions
  Reads: 8,500,000
  Writes: 2,000,000
  Storage: 12.0 GB
  Cost: $5.20

Order processing:
  Tables: order-events
  Reads: 3,200,000
  Writes: 4,800,000
  Storage: 4.0 GB
  Cost: $8.50

--- Table Details ---

1. user-sessions
   Status: ACTIVE
   Items: 1,500,000
   Storage: 12.0 GB
   Reads: 8,500,000
   Writes: 2,000,000
   Estimated Monthly Cost: $5.20
   Cost per 1,000 requests: $0.0028
   Driver: Session activity
```

#### JSON Export

When using the `--output` option, results are exported in JSON format:

```json
{
  "scan_time": "2024-03-15T10:30:00.123456",
  "region": "us-east-1",
  "demo_mode": false,
  "analysis_period_days": 30,
  "dynamodb_pricing": {
    "read_cost_per_million": 0.25,
    "write_cost_per_million": 1.25,
    "storage_cost_per_gb": 0.25
  },
  "driver_analysis": [
    {
      "table_name": "user-sessions",
      "table_status": "ACTIVE",
      "item_count": 1500000,
      "table_size_bytes": 12884901888,
      "billing_mode": "PAY_PER_REQUEST",
      "metrics": {
        "Reads": 8500000,
        "Writes": 2000000
      },
      "cost_analysis": {
        "read_cost": 2.125,
        "write_cost": 2.5,
        "storage_cost": 3.0,
        "total_cost": 7.625,
        "cost_per_1000_requests": 0.0028,
        "storage_gb": 12.0
      },
      "demand_driver": "Session activity"
    }
  ],
  "driver_groups": {
    "Session activity": {
      "tables": ["user-sessions"],
      "total_reads": 8500000,
      "total_writes": 2000000,
      "total_cost": 7.625,
      "total_storage": 12.0
    }
  },
  "summary": {
    "total_tables_analyzed": 4,
    "total_reads": 14000000,
    "total_writes": 9450000,
    "total_storage_gb": 78.0,
    "total_estimated_monthly_cost": 28.95,
    "unique_demand_drivers": 4,
    "average_cost_per_table": 7.24
  }
}
```

### How It Works

#### DynamoDB Analysis
- Retrieves all active DynamoDB tables in the specified region
- Collects table configuration (billing mode, item count, storage size)
- Analyzes table tags and descriptions for context

#### CloudWatch Metrics
- **ConsumedReadCapacityUnits**: Total read capacity consumed over the analysis period
- **ConsumedWriteCapacityUnits**: Total write capacity consumed over the analysis period
- **Storage Analysis**: Table size in bytes converted to GB for cost calculations

#### Cost Calculations
- **Read Cost**: $0.25 per million read operations
- **Write Cost**: $1.25 per million write operations
- **Storage Cost**: $0.25 per GB per month
- **Total Cost**: Sum of read, write, and storage costs
- **Cost per 1,000 Requests**: Average cost per thousand operations

#### Demand Driver Identification
The script uses pattern recognition to identify drivers:

- **Session Activity**: Tables with session/cache-related names
- **Order Processing**: Tables with order/transaction/event-related names
- **Product Lookups**: Tables with product/catalog/inventory-related names
- **User Data**: Tables with user/profile/account-related names
- **Data Retention**: Tables with audit/log/history-related names or high storage
- **API Traffic**: Tables with high read ratios (>80% reads)
- **Event Processing**: Tables with high write ratios (>60% writes)
- **High Churn Data**: Tables with high writes per item ratios
- **Frequent Lookups**: Tables with high reads per item ratios

### Supported DynamoDB Features

- **Billing Modes**: PAY_PER_REQUEST and PROVISIONED throughput
- **Table States**: Only ACTIVE tables are analyzed
- **Storage Types**: Standard DynamoDB table storage
- **Metrics**: 30-day analysis period for cost accuracy

### Best Practices

#### Before Analysis
1. **Enable CloudWatch Metrics**: Ensure detailed monitoring is enabled
2. **Review Table Tags**: Properly tag tables for better driver identification
3. **Consider Time Period**: 30 days provides good balance for analysis
4. **Check Table State**: Only active tables are analyzed

#### Cost Optimization
1. **Review High-Cost Tables**: Focus on tables with highest monthly costs
2. **Analyze Driver Patterns**: Understand what drives DynamoDB usage
3. **Optimize Read/Write Patterns**: Consider access patterns and indexing
4. **Monitor Storage Growth**: Track storage usage over time

#### Driver Analysis
1. **Group by Driver**: Understand cost distribution across workload types
2. **Identify Growth Patterns**: Track driver changes over time
3. **Optimize High-Traffic Drivers**: Focus on most frequently accessed tables
4. **Review Access Patterns**: Address inefficient query patterns

### Troubleshooting

#### Common Issues

1. **"No metrics available"**
   - Table may be too new (less than 1 day old)
   - CloudWatch detailed monitoring might be disabled
   - Table might not have had any activity during analysis period

2. **"Error retrieving DynamoDB tables"**
   - Verify DynamoDB permissions in IAM policy
   - Check if the specified region is correct
   - Ensure AWS credentials have necessary permissions

3. **"Error retrieving metrics"**
   - Verify CloudWatch permissions in IAM policy
   - Check if CloudWatch is enabled for the region
   - Table might not have CloudWatch logging enabled

4. **No demand drivers identified**
   - Tables might not have clear naming patterns
   - Consider reviewing table descriptions and tags
   - Manual driver classification might be needed

### Exit Codes

- **0**: Analysis completed successfully
- **1**: Script execution failed

Use exit codes for automation:
```bash
python dynamodb_driver_detector.py --region us-west-2
if [ $? -eq 0 ]; then
    echo "DynamoDB driver analysis completed successfully"
fi
```

## RDS Driver Detector

The `rds_driver_detector.py` script analyzes Amazon RDS instances to identify workload demand drivers that influence database costs through usage patterns and metrics.

### Features

- **Instance Discovery**: Lists all active RDS instances in the specified region
- **CloudWatch Metrics Analysis**: Retrieves 7-day metrics for CPU, memory, connections, and IOPS
- **Cost Estimation**: Calculates RDS costs using sample pricing models
- **Demand Driver Identification**: Analyzes patterns to identify workload drivers
- **Performance Analysis**: Calculates utilization ratios and optimization signals
- **Demo Mode**: Test with realistic sample RDS data when AWS credentials unavailable

### Prerequisites

The script requires the following AWS IAM permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "rds:DescribeDBInstances",
                "rds:DescribeDBClusters",
                "cloudwatch:GetMetricStatistics"
            ],
            "Resource": "*"
        }
    ]
}
```

### Usage

#### Demo Mode (No AWS Credentials Required)

Test the script with realistic sample data:

```bash
python rds_driver_detector.py --demo
```

#### Basic Usage

Scan your default AWS region:

```bash
python rds_driver_detector.py
```

#### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--region` | AWS region to scan | us-east-1 |
| `--output` | Output JSON file path | None |
| `--profile` | AWS profile name to use | None |
| `--demo` | Run in demo mode with sample data | False |

#### Examples

1. **Scan specific region and export results:**
   ```bash
   python rds_driver_detector.py --region us-west-2 --output rds_report.json
   ```

2. **Use specific AWS profile:**
   ```bash
   python rds_driver_detector.py --profile production --region eu-west-1
   ```

3. **Demo mode with JSON export:**
   ```bash
   python rds_driver_detector.py --demo --output demo_rds.json
   ```

### Output

#### Console Output

The script provides a detailed analysis of RDS drivers:

```
RDS Driver Analysis
====================

Region: us-east-1
Scan Time: 2024-03-15T10:30:00.123456
Analysis Period: 7 days

--- Summary ---
Total Instances Analyzed: 4
Total Monthly Cost: $146.00
Total Storage: 1,850 GB
Unique Demand Drivers: 4
Average Cost per Instance: $36.50

--- Demand Drivers ---

Transaction processing:
  Instances: orders-prod-db
  Monthly Cost: $153.30
  Storage: 250 GB
  Avg CPU Utilization: 18.4%
  Avg Connections: 145

--- Instance Details ---

1. orders-prod-db
   Engine: postgres 14.9
   Instance Class: db.r5.large
   Status: available
   Storage: 250 GB (gp3)
   Multi-AZ: False
   CPU Utilization: 18.4%
   Freeable Memory: 2.1 GB
   Connections: 145
   Read IOPS: 320
   Write IOPS: 510
   Estimated Monthly Cost: $153.30
   Driver: Transaction processing
   Optimization Signals:
     • Underutilized instance - consider downsizing
```

#### JSON Export

When using the `--output` option, results are exported in JSON format:

```json
{
  "scan_time": "2024-03-15T10:30:00.123456",
  "region": "us-east-1",
  "demo_mode": false,
  "analysis_period_days": 7,
  "driver_analysis": [
    {
      "instance_id": "orders-prod-db",
      "instance_class": "db.r5.large",
      "engine": "postgres",
      "cost_analysis": {
        "total_monthly_cost": 153.30,
        "instance_monthly_cost": 153.30,
        "storage_monthly_cost": 28.75
      },
      "demand_driver": "Transaction processing"
    }
  ],
  "summary": {
    "total_instances_analyzed": 4,
    "total_monthly_cost": 146.00,
    "unique_demand_drivers": 4,
    "average_cost_per_instance": 36.50
  }
}
```

### How It Works

#### RDS Analysis
- Retrieves all active RDS instances in the specified region
- Collects instance configuration (engine, storage, multi-AZ, tags)

#### CloudWatch Metrics
- **CPUUtilization**: Average CPU utilization percentage over the analysis period
- **FreeableMemory**: Average available memory in GB
- **DatabaseConnections**: Average number of database connections
- **ReadIOPS**: Average read operations per second
- **WriteIOPS**: Average write operations per second

#### Cost Calculations
- **Instance Cost**: Based on instance class and engine type
- **Storage Cost**: Based on allocated storage and storage type
- **Total Cost**: Sum of instance and storage costs

#### Demand Driver Identification
The script uses pattern recognition to identify drivers:

- **Transaction Processing**: Instances with order/transaction-related names
- **Session Management**: Instances with session/user-related names
- **Analytics Workload**: Instances with analytics/warehouse/reporting names
- **Read-Heavy Reporting**: Instances with high read IOPS
- **Write-Intensive Transactions**: Instances with high write IOPS

### Best Practices

#### Before Analysis
1. **Enable Enhanced Monitoring**: Ensure detailed CloudWatch monitoring is enabled
2. **Review Instance Tags**: Properly tag instances for better driver identification
3. **Consider Time Period**: 7 days provides good balance for recent performance
4. **Check Instance State**: Only available instances are analyzed

#### Cost Optimization
1. **Review High-Cost Instances**: Focus on instances with highest monthly costs
2. **Analyze Driver Patterns**: Understand what drives RDS usage
3. **Optimize Instance Types**: Consider right-sizing based on actual utilization
4. **Monitor Storage Growth**: Track storage usage over time

### Troubleshooting

#### Common Issues

1. **"No metrics available"**
   - Instance may be too new (less than 1 day old)
   - CloudWatch detailed monitoring might be disabled
   - Instance might not have had any activity during analysis period

2. **"Error retrieving RDS instances"**
   - Verify RDS permissions in IAM policy
   - Check if the specified region is correct
   - Ensure AWS credentials have necessary permissions

3. **"Error retrieving metrics"**
   - Verify CloudWatch permissions in IAM policy
   - Check if CloudWatch is enabled for the region
   - Instance might not have CloudWatch logging enabled

### Exit Codes

- **0**: Analysis completed successfully
- **1**: Script execution failed

Use exit codes for automation:
```bash
python rds_driver_detector.py --region us-west-2
if [ $? -eq 0 ]; then
    echo "RDS driver analysis completed successfully"
fi
```

## S3 Driver Detector

The `s3_driver_detector.py` script analyzes Amazon S3 buckets to identify storage demand drivers that influence cloud costs through usage patterns and metrics.

### Features

- **Bucket Discovery**: Lists all S3 buckets in the specified region
- **CloudWatch Metrics Analysis**: Retrieves request metrics and storage data
- **Cost Estimation**: Calculates S3 costs using sample pricing models
- **Demand Driver Identification**: Analyzes patterns to identify workload drivers
- **Performance Analysis**: Calculates request ratios and optimization signals
- **Demo Mode**: Test with realistic sample S3 data when AWS credentials unavailable

### Prerequisites

The script requires the following AWS IAM permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListAllMyBuckets",
                "s3:GetBucketLocation",
                "s3:GetBucketTagging",
                "cloudwatch:GetMetricStatistics"
            ],
            "Resource": "*"
        }
    ]
}
```

### Usage

#### Demo Mode (No AWS Credentials Required)

Test the script with realistic sample data:

```bash
python s3_driver_detector.py --demo
```

#### Basic Usage

Scan your default AWS region:

```bash
python s3_driver_detector.py
```

#### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--region` | AWS region to scan | us-east-1 |
| `--output` | Output JSON file path | None |
| `--profile` | AWS profile name to use | None |
| `--demo` | Run in demo mode with sample data | False |

#### Examples

1. **Scan specific region and export results:**
   ```bash
   python s3_driver_detector.py --region us-west-2 --output s3_report.json
   ```

2. **Use specific AWS profile:**
   ```bash
   python s3_driver_detector.py --profile production --region eu-west-1
   ```

3. **Demo mode with JSON export:**
   ```bash
   python s3_driver_detector.py --demo --output demo_s3.json
   ```

### Output

#### Console Output

The script provides a detailed analysis of S3 drivers:

```
S3 Driver Analysis
===================

Region: us-east-1
Scan Time: 2024-03-15T10:30:00.123456
Analysis Period: 30 days

--- Summary ---
Total Buckets Analyzed: 4
Total Storage: 8.3 TB
Total Objects: 3,150,000
Total Monthly Cost: $45.00
Unique Demand Drivers: 4
Average Cost per Bucket: $11.25

--- Demand Drivers ---

Content delivery:
  Buckets: user-uploads, static-assets
  Monthly Cost: $25.00
  Storage: 1.3 TB
  Objects: 2,550,000
  GET Requests: 15,000,000
  PUT Requests: 510,000

Archival storage:
  Buckets: backup-archive
  Monthly Cost: $15.00
  Storage: 5.0 TB
  Objects: 100,000
  GET Requests: 10,000
  PUT Requests: 50,000

--- Bucket Details ---

1. user-uploads
   Storage Class: STANDARD
   Storage: 1.2 TB
   Objects: 2,500,000
   GET Requests: 5,000,000
   PUT Requests: 500,000
   Estimated Monthly Cost: $25.00
   Driver: Content delivery
   Optimization Signals:
     • High GET requests - consider caching or CDN

2. backup-archive
   Storage Class: GLACIER
   Storage: 5.0 TB
   Objects: 100,000
   GET Requests: 10,000
   PUT Requests: 50,000
   Estimated Monthly Cost: $15.00
   Driver: Archival storage
   Optimization Signals:
     • Consider lifecycle policy for backup storage
```

#### JSON Export

When using the `--output` option, results are exported in JSON format:

```json
{
  "scan_time": "2024-03-15T10:30:00.123456",
  "region": "us-east-1",
  "demo_mode": false,
  "analysis_period_days": 30,
  "s3_pricing": {
    "storage": {
      "standard": 0.023,
      "glacier": 0.004
    },
    "requests": {
      "get": 0.0004,
      "put": 0.005
    }
  },
  "driver_analysis": [
    {
      "bucket_name": "user-uploads",
      "storage_class": "STANDARD",
      "size_bytes": 1288490188800,
      "object_count": 2500000,
      "cost_analysis": {
        "storage_cost": 27.60,
        "get_cost": 2.00,
        "put_cost": 2.50,
        "total_monthly_cost": 32.10
      },
      "demand_driver": "Content delivery",
      "optimization_signals": ["High GET requests - consider caching or CDN"]
    }
  ],
  "driver_groups": {
    "Content delivery": {
      "buckets": ["user-uploads"],
      "total_monthly_cost": 32.10,
      "total_storage_gb": 1200.0,
      "total_objects": 2500000,
      "total_get_requests": 5000000,
      "total_put_requests": 500000
    }
  },
  "summary": {
    "total_buckets_analyzed": 4,
    "total_storage_gb": 8300.0,
    "total_objects": 3150000,
    "total_monthly_cost": 45.00,
    "unique_demand_drivers": 4,
    "average_cost_per_bucket": 11.25
  }
}
```

### How It Works

#### S3 Analysis
- Retrieves all S3 buckets in the specified region
- Collects bucket configuration (storage class, tags, location)
- Analyzes bucket tags and descriptions for context

#### CloudWatch Metrics
- **AllRequests**: Total request count for GET, PUT, LIST operations
- **StorageMetrics**: Storage size and object count data
- **Request Distribution**: Estimated GET vs PUT request ratios

#### Cost Calculations
- **Storage Cost**: Based on storage class and size in GB
- **GET Cost**: $0.0004 per 1,000 GET requests
- **PUT Cost**: $0.005 per 1,000 PUT requests
- **LIST Cost**: $0.005 per 1,000 LIST requests
- **Total Cost**: Sum of storage and request costs

#### Demand Driver Identification
The script uses pattern recognition to identify drivers:

- **User Uploads**: Buckets with upload-related names or tags
- **Archival Storage**: Buckets with backup/archive-related names or Glacier storage
- **CDN Content**: Buckets with static/asset-related names or high GET requests
- **Data Ingestion**: Buckets with data/lake-related names or high PUT requests
- **Log Storage**: Buckets with log-related names or tags
- **Media Content**: Buckets with media/video/image-related names
- **Cold Storage**: Glacier or Deep Archive storage classes
- **Long-term Retention**: Large storage with low access patterns
- **Content Delivery**: High GET request volumes
- **Data Ingestion**: High PUT request volumes
- **Read/Write Workloads**: Request distribution analysis

#### Optimization Signals
The script provides actionable recommendations:

- **Storage Optimization**: Lifecycle policies, storage class transitions
- **Request Optimization**: Caching strategies, CDN implementation
- **Lifecycle Management**: Automated archival and deletion policies
- **Cost Optimization**: Storage class selection based on access patterns

### Supported S3 Features

- **Storage Classes**: STANDARD, INTELLIGENT_TIERING, INFREQUENT_ACCESS, GLACIER, DEEP_ARCHIVE
- **Request Types**: GET, PUT, LIST operations
- **Metrics**: 30-day analysis period for request patterns
- **Tags**: Uses bucket tags for driver identification
- **Regions**: Analyzes buckets in specified region only

### Best Practices

#### Before Analysis
1. **Enable CloudWatch Metrics**: Ensure request metrics are enabled
2. **Review Bucket Tags**: Properly tag buckets for better driver identification
3. **Consider Time Period**: 30 days provides good balance for request analysis
4. **Check Bucket Location**: Only buckets in specified region are analyzed

#### Cost Optimization
1. **Review High-Cost Buckets**: Focus on buckets with highest monthly costs
2. **Analyze Storage Classes**: Match storage class to access patterns
3. **Implement Lifecycle Policies**: Automate storage class transitions
4. **Optimize Request Patterns**: Consider caching for high GET volumes
5. **Monitor Growth**: Track storage and request growth over time

#### Driver Analysis
1. **Group by Driver**: Understand cost distribution across workload types
2. **Identify Access Patterns**: Track request pattern changes over time
3. **Optimize High-Traffic Drivers**: Focus on most accessed buckets
4. **Review Storage Efficiency**: Address inefficient storage usage

### Troubleshooting

#### Common Issues

1. **"No metrics available"**
   - Bucket may be too new (less than 1 day old)
   - CloudWatch detailed monitoring might be disabled
   - Bucket might not have had any requests during analysis period

2. **"Error retrieving S3 buckets"**
   - Verify S3 permissions in IAM policy
   - Check if the specified region is correct
   - Ensure AWS credentials have necessary permissions

3. **"Error retrieving metrics"**
   - Verify CloudWatch permissions in IAM policy
   - Check if CloudWatch is enabled for the region
   - Bucket might not have CloudWatch logging enabled

4. **No demand drivers identified**
   - Buckets might not have clear naming patterns
   - Consider reviewing bucket descriptions and tags
   - Manual driver classification might be needed

### Exit Codes

- **0**: Analysis completed successfully
- **1**: Script execution failed

Use exit codes for automation:
```bash
python s3_driver_detector.py --region us-west-2
if [ $? -eq 0 ]; then
    echo "S3 driver analysis completed successfully"
fi
```

## EC2 Driver Detector

The `ec2_driver_detector.py` script analyzes Amazon EC2 instances to identify compute demand drivers that influence cloud costs through usage patterns and metrics.

### Features

- **Instance Discovery**: Lists all EC2 instances in the specified region
- **CloudWatch Metrics Analysis**: Retrieves 7-day CPU utilization metrics
- **Cost Estimation**: Calculates EC2 costs using sample pricing models
- **Demand Driver Identification**: Analyzes patterns to identify workload drivers
- **Performance Analysis**: Calculates utilization ratios and optimization signals
- **Demo Mode**: Test with realistic sample EC2 data when AWS credentials unavailable

### Prerequisites

The script requires the following AWS IAM permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances",
                "cloudwatch:GetMetricStatistics"
            ],
            "Resource": "*"
        }
    ]
}
```

### Usage

#### Demo Mode (No AWS Credentials Required)

Test the script with realistic sample data:

```bash
python ec2_driver_detector.py --demo
```

#### Basic Usage

Scan your default AWS region:

```bash
python ec2_driver_detector.py
```

#### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--region` | AWS region to scan | us-east-1 |
| `--output` | Output JSON file path | None |
| `--profile` | AWS profile name to use | None |
| `--demo` | Run in demo mode with sample data | False |

#### Examples

1. **Scan specific region and export results:**
   ```bash
   python ec2_driver_detector.py --region us-west-2 --output ec2_report.json
   ```

2. **Use specific AWS profile:**
   ```bash
   python ec2_driver_detector.py --profile production --region eu-west-1
   ```

3. **Demo mode with JSON export:**
   ```bash
   python ec2_driver_detector.py --demo --output demo_ec2.json
   ```

### Output

#### Console Output

The script provides a detailed analysis of EC2 drivers:

```
EC2 Driver Analysis
====================

Region: us-east-1
Scan Time: 2024-03-15T10:30:00.123456
Analysis Period: 7 days

--- Summary ---
Total Instances Analyzed: 4
Running Instances: 3
Stopped Instances: 1
Total Monthly Cost: $70.00
Unique Demand Drivers: 4
Average Cost per Instance: $17.50

--- Demand Drivers ---

Scaling pressure:
  Instances: i-1def789abc012ghi345
  Monthly Cost: $122.40
  Running: 1, Stopped: 0
  Avg CPU Utilization: 85.7%

Overprovisioned compute:
  Instances: i-0abc123def456ghi789
  Monthly Cost: $70.08
  Running: 1, Stopped: 0
  Avg CPU Utilization: 12.3%

--- Instance Details ---

1. i-1def789abc012ghi345
   Type: c5.xlarge
   State: running
   CPU Utilization: 85.7%
   Running Hours: 720
   Estimated Monthly Cost: $122.40
   Driver: Scaling pressure
   Optimization Signals:
     • High CPU utilization - consider scaling up
     • Performance bottleneck detected

2. i-0abc123def456ghi789
   Type: m5.large
   State: running
   CPU Utilization: 12.3%
   Running Hours: 720
   Estimated Monthly Cost: $70.08
   Driver: Overprovisioned compute
   Optimization Signals:
     • Consider downsizing or scheduling shutdown
     • Low utilization suggests overprovisioning
```

#### JSON Export

When using the `--output` option, results are exported in JSON format:

```json
{
  "scan_time": "2024-03-15T10:30:00.123456",
  "region": "us-east-1",
  "demo_mode": false,
  "analysis_period_days": 7,
  "driver_analysis": [
    {
      "instance_id": "i-0abc123def456ghi789",
      "instance_type": "m5.large",
      "instance_state": "running",
      "cost_analysis": {
        "monthly_cost": 70.08,
        "hourly_cost": 0.096,
        "running_hours": 720
      },
      "demand_driver": "Overprovisioned compute",
      "optimization_signals": ["Consider downsizing or scheduling shutdown"]
    }
  ],
  "driver_groups": {
    "Overprovisioned compute": {
      "instances": ["i-0abc123def456ghi789"],
      "total_monthly_cost": 70.08,
      "avg_cpu_utilization": 12.3,
      "running_count": 1,
      "stopped_count": 0
    }
  },
  "summary": {
    "total_instances_analyzed": 4,
    "running_instances": 3,
    "stopped_instances": 1,
    "total_monthly_cost": 70.00,
    "unique_demand_drivers": 4,
    "average_cost_per_instance": 17.50
  }
}
```

### How It Works

#### EC2 Analysis
- Retrieves all EC2 instances in the specified region
- Collects instance configuration (type, state, launch time, tags)
- Analyzes instance tags and descriptions for context

#### CloudWatch Metrics
- **CPUUtilization**: Average CPU utilization percentage over the analysis period
- **Running Hours**: Estimated running time based on instance state

#### Cost Calculations
- **Instance Cost**: Based on instance type and hourly pricing
- **Monthly Cost**: Calculated as hourly cost × 730 hours
- **Stopped Instances**: Incur no compute cost

#### Demand Driver Identification
The script uses pattern recognition to identify drivers:

- **Web Server Workload**: Instances with web-related tags or names
- **Batch Processing**: Instances with batch/processing-related tags
- **Database Proxy Workload**: Instances with database/proxy-related tags
- **Cache Workload**: Instances with cache/redis-related tags
- **Development/Testing**: Instances in development environments
- **Scaling Pressure**: Instances with high CPU utilization (>80%)
- **Overprovisioned Compute**: Running instances with low CPU (<20%)
- **Active Workload**: Instances with moderate to high CPU (60-80%)
- **Compute-Intensive**: C5 family instances
- **Memory-Intensive**: R5 family instances
- **General Purpose**: T3 family instances

#### Optimization Signals
The script provides actionable recommendations:

- **Low Utilization**: Consider downsizing or scheduling shutdown
- **High Utilization**: Consider scaling up or load balancing
- **Development Instances**: Consider scheduling shutdown
- **Burstable Limits**: Consider larger instances for T3 family
- **Stopped Production**: Investigate reason for stopped production instances

### Supported EC2 Features

- **Instance Families**: T3, T3a, M5, M5a, C5, R5
- **Instance States**: Running and stopped instances analyzed
- **Instance Types**: Various sizes from nano to 4xlarge
- **Metrics**: 7-day analysis period for performance accuracy
- **Tags**: Uses Name, Environment, Team, and Role tags for analysis

### Best Practices

#### Before Analysis
1. **Enable CloudWatch Monitoring**: Ensure detailed monitoring is enabled
2. **Review Instance Tags**: Properly tag instances for better driver identification
3. **Consider Time Period**: 7 days provides good balance for recent performance
4. **Check Instance State**: Both running and stopped instances are analyzed

#### Cost Optimization
1. **Review High-Cost Instances**: Focus on instances with highest monthly costs
2. **Analyze Driver Patterns**: Understand what drives EC2 usage
3. **Optimize Instance Types**: Consider right-sizing based on actual utilization
4. **Schedule Shutdown**: Implement automated shutdown for development instances
5. **Monitor Scaling**: Track instances with high CPU utilization

#### Driver Analysis
1. **Group by Driver**: Understand cost distribution across workload types
2. **Identify Performance Patterns**: Track driver changes over time
3. **Optimize High-Traffic Drivers**: Focus on most resource-intensive instances
4. **Review Instance Scheduling**: Address inefficient instance management

### Troubleshooting

#### Common Issues

1. **"No metrics available"**
   - Instance may be too new (less than 1 day old)
   - CloudWatch detailed monitoring might be disabled
   - Instance might not have had any activity during analysis period

2. **"Error retrieving EC2 instances"**
   - Verify EC2 permissions in IAM policy
   - Check if the specified region is correct
   - Ensure AWS credentials have necessary permissions

3. **"Error retrieving metrics"**
   - Verify CloudWatch permissions in IAM policy
   - Check if CloudWatch is enabled for the region
   - Instance might not have CloudWatch logging enabled

4. **No demand drivers identified**
   - Instances might not have clear naming patterns
   - Consider reviewing instance descriptions and tags
   - Manual driver classification might be needed

### Exit Codes

- **0**: Analysis completed successfully (even if some services failed)
- **1**: All service analyses failed

### Future Extensibility

The modular architecture makes it easy to add new services:

1. **Create Detector**: Follow the established pattern for new services
2. **Add to List**: Include service in `DRIVER_SERVICES` list
3. **Update Normalization**: Add normalization logic for the new service
4. **Test Integration**: Verify unified analysis includes new service

Planned future services include:
- **EKS**: Kubernetes cluster demand drivers
- **Redshift**: Data warehouse demand drivers
- **CloudWatch**: Monitoring and alerting demand drivers
- **EFS**: File system demand drivers

### Exit Codes

- **0**: Analysis completed successfully
- **1**: All service analyses failed

Use exit codes for automation:
```bash
python unified_drivers_detector.py --region us-west-2
if [ $? -eq 0 ]; then
    echo "Unified drivers analysis completed successfully"
fi
```

## Network Driver Detector

The `network_driver_detector.py` script analyzes AWS networking costs to identify traffic-related demand drivers that influence cloud costs through usage patterns and metrics.

### Features

- **Network Discovery**: Lists all NAT gateways, load balancers, and VPC endpoints in the specified region
- **CloudWatch Metrics Analysis**: Retrieves traffic metrics and usage data
- **Cost Estimation**: Calculates networking costs using sample pricing models
- **Demand Driver Identification**: Analyzes patterns to identify traffic drivers
- **Performance Analysis**: Calculates traffic ratios and optimization signals
- **Demo Mode**: Test with realistic sample networking data when AWS credentials unavailable

### Prerequisites

The script requires the following AWS IAM permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeNatGateways",
                "ec2:DescribeLoadBalancers",
                "ec2:DescribeVpcEndpoints",
                "elasticloadbalancing:DescribeLoadBalancers",
                "cloudwatch:GetMetricStatistics",
                "ce:GetCostAndUsage"
            ],
            "Resource": "*"
        }
    ]
}
```

### Usage

#### Demo Mode (No AWS Credentials Required)

Test the script with realistic sample data:

```bash
python network_driver_detector.py --demo
```

#### Basic Usage

Scan your default AWS region:

```bash
python network_driver_detector.py
```

#### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--region` | AWS region to scan | us-east-1 |
| `--output` | Output JSON file path | None |
| `--profile` | AWS profile name to use | None |
| `--demo` | Run in demo mode with sample data | False |

#### Examples

1. **Scan specific region and export results:**
   ```bash
   python network_driver_detector.py --region us-west-2 --output network_report.json
   ```

2. **Use specific AWS profile:**
   ```bash
   python network_driver_detector.py --profile production --region eu-west-1
   ```

3. **Demo mode with JSON export:**
   ```bash
   python network_driver_detector.py --demo --output demo_network.json
   ```

### Output

#### Console Output

The script provides a detailed analysis of network drivers:

```
Networking Driver Analysis
==========================

Region: us-east-1
Scan Time: 2024-03-15T10:30:00.123456
Analysis Period: 30 days

--- Cost Summary ---
NAT Gateway Cost: $120.00
Data Transfer Out: $85.00
Load Balancer Cost: $40.00
Total Monthly Cost: $245.00

--- Infrastructure Summary ---
NAT Gateways: 2
Load Balancers: 2
VPC Endpoints: 2
Internet Egress: 850 GB
Cross-AZ Transfer: 120 GB

--- Demand Driver ---
Driver: External traffic and private subnet egress

--- Optimization Signals ---
• High NAT Gateway costs - consider VPC endpoints
• Review private subnet egress patterns
• Consider VPC endpoints to reduce NAT usage
```

#### JSON Export

When using the `--output` option, results are exported in JSON format:

```json
{
  "scan_time": "2024-03-15T10:30:00.123456",
  "region": "us-east-1",
  "demo_mode": false,
  "analysis_period_days": 30,
  "network_pricing": {
    "nat_gateway": {"hourly": 0.045, "data_processing": 0.045},
    "data_transfer": {"out_to_internet": 0.09, "cross_az": 0.01},
    "load_balancer": {"alb_hourly": 0.0225, "nlb_hourly": 0.0225}
  },
  "cost_analysis": {
    "total_nat_cost": 120.00,
    "total_lb_cost": 40.00,
    "total_data_transfer_cost": 85.00,
    "total_monthly_cost": 245.00
  },
  "demand_driver": "External traffic and private subnet egress",
  "optimization_signals": [
    "High NAT Gateway costs - consider VPC endpoints",
    "Review private subnet egress patterns",
    "Consider VPC endpoints to reduce NAT usage"
  ],
  "summary": {
    "total_nat_gateways": 2,
    "total_load_balancers": 2,
    "total_vpc_endpoints": 2,
    "total_monthly_cost": 245.00,
    "out_to_internet_gb": 850,
    "cross_az_gb": 120
  }
}
```

### How It Works

#### Network Analysis
- Retrieves all NAT gateways, load balancers, and VPC endpoints in the specified region
- Collects networking configuration (types, schemes, availability zones)
- Analyzes network tags and descriptions for context

#### CloudWatch Metrics
- **NAT Gateway**: Bytes processed and connection count
- **Load Balancer**: Processed bytes, request count, and LCU hours
- **Data Transfer**: Internet egress and cross-AZ transfer volumes

#### Cost Calculations
- **NAT Gateway Cost**: Hourly cost + data processing cost
- **Data Transfer Cost**: Tiered pricing for internet egress + cross-AZ costs
- **Load Balancer Cost**: Hourly cost + LCU processing cost
- **Total Cost**: Sum of all networking components

#### Demand Driver Identification
The script uses pattern recognition to identify drivers:

- **External Traffic and Private Subnet Egress**: High NAT costs + data transfer
- **High-Traffic Web Applications**: High load balancer costs + internet egress
- **Cross-AZ Communication Inefficiency**: High cross-AZ transfer volumes
- **Private Subnet Egress Patterns**: High NAT gateway costs
- **Load Balancing Infrastructure**: High load balancer costs
- **Content Delivery and User Traffic**: High internet egress volumes
- **Hybrid Architecture**: VPC endpoints + NAT usage
- **Data-Intensive Workloads**: High data transfer costs
- **Multi-Tier Application Architecture**: Multiple networking components
- **General Networking Infrastructure**: Basic networking setup

#### Optimization Signals
The script provides actionable recommendations:

- **NAT Gateway Optimization**: VPC endpoints, egress pattern review
- **Load Balancer Optimization**: Traffic pattern analysis
- **Data Transfer Optimization**: Same-AZ deployment, CDN usage
- **VPC Endpoint Optimization**: Reduce NAT usage
- **Architecture Optimization**: Multi-AZ efficiency review

### Supported Networking Features

- **NAT Gateways**: Hourly and data processing costs
- **Load Balancers**: ALB, NLB, and CLB support with LCU calculation
- **VPC Endpoints**: Gateway and interface endpoint analysis
- **Data Transfer**: Tiered internet pricing and cross-AZ costs
- **Metrics**: 30-day analysis period for traffic patterns
- **Regions**: Analyzes networking components in specified region

### Best Practices

#### Before Analysis
1. **Enable CloudWatch Metrics**: Ensure detailed monitoring is enabled
2. **Review Network Tags**: Properly tag resources for better driver identification
3. **Consider Time Period**: 30 days provides good balance for traffic analysis
4. **Check Network Configuration**: Verify networking setup is optimal

#### Cost Optimization
1. **Review High-Cost Components**: Focus on components with highest monthly costs
2. **Analyze Traffic Patterns**: Understand what drives networking usage
3. **Implement VPC Endpoints**: Reduce NAT gateway usage where possible
4. **Optimize Data Transfer**: Use same-AZ deployments and caching
5. **Monitor Growth**: Track networking costs and traffic over time

#### Driver Analysis
1. **Group by Driver**: Understand cost distribution across traffic types
2. **Identify Traffic Patterns**: Track driver changes over time
3. **Optimize High-Traffic Drivers**: Focus on most expensive components
4. **Review Architecture**: Address inefficient networking patterns

### Troubleshooting

#### Common Issues

1. **"No metrics available"**
   - Component may be too new (less than 1 day old)
   - CloudWatch detailed monitoring might be disabled
   - Component might not have had traffic during analysis period

2. **"Error retrieving networking components"**
   - Verify networking permissions in IAM policy
   - Check if the specified region is correct
   - Ensure AWS credentials have necessary permissions

3. **"Error retrieving metrics"**
   - Verify CloudWatch permissions in IAM policy
   - Check if CloudWatch is enabled for the region
   - Component might not have CloudWatch logging enabled

4. **No demand drivers identified**
   - Components might not have clear naming patterns
   - Consider reviewing component descriptions and tags
   - Manual driver classification might be needed

### Exit Codes

- **0**: Analysis completed successfully
- **1**: Script execution failed

Use exit codes for automation:
```bash
python network_driver_detector.py --region us-west-2
if [ $? -eq 0 ]; then
    echo "Network driver analysis completed successfully"
fi
```

## EC2 Rightsizing Detector

The `rightsizing_detector.py` script analyzes EC2 instances for rightsizing opportunities by identifying instances with low CPU utilization and recommending smaller instance types.

### Features

- **CPU Utilization Analysis**: Retrieves 7-day average CPU utilization from CloudWatch
- **Rightsizing Detection**: Identifies instances with CPU utilization below 10%
- **Intelligent Recommendations**: Suggests smaller instance types for t3, m5, and c5 families
- **Cost Savings Analysis**: Calculates potential monthly savings using sample pricing
- **Confidence Scoring**: Provides confidence levels (High/Medium/Low) for recommendations
- **Demo Mode**: Test with realistic sample EC2 and CPU data when AWS credentials unavailable

### Prerequisites

The script requires the following AWS IAM permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances",
                "cloudwatch:GetMetricStatistics"
            ],
            "Resource": "*"
        }
    ]
}
```

### Usage

#### Demo Mode (No AWS Credentials Required)

Test the script with realistic sample data:

```bash
python rightsizing_detector.py --demo
```

#### Basic Usage

Scan your default AWS region:

```bash
python rightsizing_detector.py
```

#### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--region` | AWS region to scan | us-east-1 |
| `--output` | Output JSON file path | None |
| `--profile` | AWS profile name to use | None |
| `--demo` | Run in demo mode with sample data | False |

#### Examples

1. **Scan specific region and export results:**
   ```bash
   python rightsizing_detector.py --region us-west-2 --output rightsizing_report.json
   ```

2. **Use specific AWS profile:**
   ```bash
   python rightsizing_detector.py --profile production --region eu-west-1
   ```

3. **Demo mode with JSON export:**
   ```bash
   python rightsizing_detector.py --demo --output demo_rightsizing.json
   ```

4. **Multi-region analysis:**
   ```bash
   for region in us-east-1 us-west-2 eu-west-1; do
       python rightsizing_detector.py --region $region --output "rightsizing_$region.json"
   done
   ```

### Output

#### Console Output

The script provides a detailed analysis of rightsizing opportunities:

```
EC2 Rightsizing Detector
Region: us-east-1
Analyzing EC2 instances for rightsizing opportunities...

=== EC2 Rightsizing Analysis ===
Region: us-east-1
Scan Time: 2024-03-15T10:30:00.123456
Analysis Period: 7 days
CPU Threshold: 10%

--- Summary ---
Total Instances Analyzed: 4
Rightsizing Candidates: 3
Potential Monthly Savings: $156.80

--- Rightsizing Candidates ---

1. web-server-1 (i-1234567890abcdef0)
   Type: t3.large
   CPU Utilization: 5.2%
   Current Cost: $59.90/month
   Potential Savings: $29.95/month
   Recommendations:
     1. t3.medium - Save $29.95/month (Confidence: High)
     2. t3.small - Save $44.93/month (Confidence: High)

2. compute-worker-1 (i-abcdef1234567890a)
   Type: c5.2xlarge
   CPU Utilization: 3.1%
   Current Cost: $244.80/month
   Potential Savings: $122.40/month
   Recommendations:
     1. c5.xlarge - Save $122.40/month (Confidence: High)
     2. c5.large - Save $183.60/month (Confidence: High)

3. app-server-2 (i-0fedcba9876543210)
   Type: m5.xlarge
   CPU Utilization: 8.7%
   Current Cost: $138.24/month
   Potential Savings: $69.12/month
   Recommendations:
     1. m5.large - Save $69.12/month (Confidence: Medium)
     2. t3.large - Save $55.04/month (Confidence: Medium)
```

#### JSON Export

When using the `--output` option, results are exported in JSON format:

```json
{
  "scan_time": "2024-03-15T10:30:00.123456",
  "region": "us-east-1",
  "demo_mode": false,
  "analysis_period_days": 7,
  "cpu_threshold_percent": 10.0,
  "rightsizing_candidates": [
    {
      "instance_id": "i-1234567890abcdef0",
      "instance_name": "web-server-1",
      "instance_type": "t3.large",
      "state": "running",
      "launch_time": "2024-02-01T10:30:00Z",
      "average_cpu_utilization": 5.2,
      "current_hourly_cost": 0.0832,
      "current_monthly_cost": 59.904,
      "recommendations": [
        {
          "instance_type": "t3.medium",
          "current_hourly_cost": 0.0832,
          "recommended_hourly_cost": 0.0416,
          "savings_per_hour": 0.0416,
          "savings_per_month": 29.952,
          "confidence": "High"
        }
      ],
      "potential_monthly_savings": 29.952,
      "tags": [
        {"Key": "Name", "Value": "web-server-1"},
        {"Key": "Environment", "Value": "production"}
      ]
    }
  ],
  "summary": {
    "total_instances_analyzed": 4,
    "total_rightsizing_candidates": 3,
    "total_potential_monthly_savings": 156.80,
    "average_cpu_utilization": 5.67
  }
}
```

### How It Works

#### CPU Analysis
- Retrieves CloudWatch CPUUtilization metrics for the last 7 days
- Calculates hourly averages and computes overall average
- Identifies instances with average CPU below 10%

#### Recommendation Engine
The script uses a rightsizing mapping for common instance families:

- **t3/t3a family**: Burstable instances for general purpose workloads
- **m5/m5a family**: General purpose instances for balanced compute/memory
- **c5/c5a family**: Compute optimized instances for high-performance needs

#### Confidence Scoring
- **High**: CPU < 5% (strong rightsizing candidate)
- **Medium**: CPU 5-8% (good candidate)
- **Low**: CPU 8-10% (consider carefully)

#### Cost Calculations
- Uses simplified hourly pricing (actual costs vary by region)
- Calculates monthly savings based on 24/7 operation
- Accounts for different instance family pricing

### Supported Instance Types

The script supports rightsizing recommendations for these families:

| Family | Current Types | Recommended Types |
|--------|---------------|-------------------|
| t3 | nano, micro, small, medium, large, xlarge, 2xlarge | Smaller t3 instances |
| t3a | nano, micro, small, medium, large, xlarge, 2xlarge | Smaller t3a instances |
| m5 | large, xlarge, 2xlarge, 4xlarge, 8xlarge, 12xlarge, 16xlarge, 24xlarge | Smaller m5 or t3 instances |
| m5a | large, xlarge, 2xlarge, 4xlarge, 8xlarge, 12xlarge, 16xlarge, 24xlarge | Smaller m5a or t3a instances |
| c5 | large, xlarge, 2xlarge, 4xlarge, 9xlarge, 12xlarge, 18xlarge, 24xlarge | Smaller c5 instances |
| c5a | large, xlarge, 2xlarge, 4xlarge, 8xlarge, 12xlarge, 16xlarge, 24xlarge | Smaller c5a instances |

### Best Practices

#### Before Rightsizing
1. **Monitor Longer**: Consider 14-30 day analysis for production workloads
2. **Check Memory Usage**: CPU alone may not indicate true utilization
3. **Review Application Requirements**: Ensure smaller instances meet performance needs
4. **Test in Staging**: Validate performance before production changes

#### Rightsizing Process
1. **Create AMIs**: Backup instances before making changes
2. **Test Performance**: Validate smaller instances handle workloads
3. **Monitor Post-Change**: Watch performance after rightsizing
4. **Rollback Plan**: Have procedure to revert if issues occur

#### Automation Ideas
1. **Scheduled Scans**: Run weekly to catch new opportunities
2. **Integration**: Combine with other FinOps tools for comprehensive analysis
3. **Alerting**: Set up notifications for new rightsizing candidates
4. **Cost Tracking**: Monitor actual savings after rightsizing

### Troubleshooting

#### Common Issues

1. **"No CPU data available"**
   - Instance may be too new (less than 1 hour old)
   - CloudWatch metrics may be disabled
   - Instance might be in a stopped state

2. **"Error retrieving EC2 instances"**
   - Verify EC2 permissions in IAM policy
   - Check if the specified region is correct
   - Ensure AWS credentials have necessary permissions

3. **"Error retrieving CPU metrics"**
   - Verify CloudWatch permissions in IAM policy
   - Check if CloudWatch is enabled for the region
   - Instance might not have CloudWatch monitoring enabled

4. **No recommendations found**
   - Instance type may not be in the supported families
   - CPU utilization might be above the 10% threshold
   - No smaller instances available in the same family

### Exit Codes

- **0**: No rightsizing opportunities found
- **1**: Rightsizing opportunities detected

Use exit codes for automation:
```bash
python rightsizing_detector.py --region us-west-2
if [ $? -eq 1 ]; then
    echo "Rightsizing opportunities found - review recommendations"
fi
```

## Contributing

Feel free to submit issues or enhancement requests to improve the idle resource detection capabilities or add support for additional AWS services.
