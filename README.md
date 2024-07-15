# HLS Playlist S3 Signed URL Generator

This repository takes an HLS playlist and all child profiles and replaces the direct .ts files with S3 pre-signed URLs. This allows an HLS player to follow each presigned URL for each segment without having a public S3 bucket. 

This can be used for solutions where CloudFront is not appropriate and S3 or S3 with Transfer Acceleration (S3TA) is employed instead. 

Note: The generated URLs are only valid for as long as the credentials used to sign them. For example, if you are using an assumed role with a 1 hour session duration, the maximum validity of a presigned URL is 60 minutes. To achieve longer than this, use long-lived credentials to generate the URLs.

## Getting started

No additional dependencies are required beyond python 3.x and boto3:

`pip install boto3`

Update the `filenames` array in `main.py` with the list of playlist profiles that you already have downloaded locally to this directory

Update the S3 bucket and region at the top of the file. 

You can toggle transfer acceleration on and off by changing the `use_accelerate_endpoint` in the Config object. 

