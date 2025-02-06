# HLS Playlist S3 Signed URL Generator

This repository takes an HLS playlist and all child profiles and replaces the direct .ts files with S3 pre-signed URLs. This allows an HLS player to follow each presigned URL for each segment without having a public S3 bucket. 

This can be used for solutions where CloudFront is not appropriate and S3 or S3 with Transfer Acceleration (S3TA) is employed instead. 

Note: The generated URLs are only valid for as long as the credentials used to sign them. For example, if you are using an assumed role with a 1 hour session duration, the maximum validity of a presigned URL is 60 minutes. To achieve longer than this, use long-lived credentials to generate the URLs.

## Prerequisites

- Python 3.6 or higher
- AWS credentials configured
- AWS IAM permissions for S3 access

## Installation

1. Create and activate a Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Modify the `settings.ini` file in the project root

## AWS Credentials Setup

Ensure you have AWS credentials configured either through:
- AWS CLI (`aws configure`)
- Environment variables
- IAM role if running on AWS infrastructure

## Usage

Run the main script:
```bash
python main.py
```

This then generates the pre-signed playlist files and uploads them back to the S3 bucket. 

The tool will output a preview URL. This url can be copied into an HLS player e.g. https://hlsjs.video-dev.org/demo/ 

## Dependencies

- boto3: AWS SDK for Python