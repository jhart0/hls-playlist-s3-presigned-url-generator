from configparser import ConfigParser
import boto3
from botocore.config import Config

s3_conf = Config(
    s3={
        'use_accelerate_endpoint':True
    }
)

config = ConfigParser()
config.read('settings.ini')

s3_bucket = config.get('VideoSource', 's3_bucket')
region = config.get('VideoSource', 'region')
number_of_profiles = config.getint('VideoSource', 'number_of_profiles')
bucket_prefix = config.get('VideoSource', 'bucket_prefix')
playlist_file = config.get('VideoSource', 'playlist_file')
profile_file_prefix = config.get('VideoSource', 'profile_file_prefix')
output_filename = config.get('VideoSource', 'output_filename')
output_profile_prefix = config.get('VideoSource', 'output_profile_prefix')
pre_signed_url_expiry = config.getint('VideoSource', 'pre_signed_url_expiry')

s3 = boto3.client('s3', region_name=region, config=s3_conf)

def replace_url_with_s3(m3u_content, s3_bucket):
    lines = m3u_content.splitlines()
    modified_lines = []
    i = 1
    for line in lines:
        if line.endswith('.m3u8'):
            s3_url = s3.generate_presigned_url('get_object', ExpiresIn=pre_signed_url_expiry, Params={'Bucket': s3_bucket, 'Key': f'{bucket_prefix}{output_profile_prefix}{str(i)}.m3u8'})
            modified_lines.append(s3_url)
            i += 1
        elif line.endswith('.ts'):
            s3_url = s3.generate_presigned_url('get_object', ExpiresIn=pre_signed_url_expiry, Params={'Bucket': s3_bucket, 'Key': f'{bucket_prefix}{line}'})
            modified_lines.append(s3_url)
        else:
            modified_lines.append(line)
    return '\n'.join(modified_lines)

def upload_to_s3(file, bucket):
    s3.upload_file(file, bucket, bucket_prefix + file)

def process_m3u_file(i, filename, s3_bucket):
    with open(filename, 'rb') as m3u_file:
        m3u_content = m3u_file.read().decode('utf-8')
        modified_content = replace_url_with_s3(m3u_content, s3_bucket)

    output_filename = f's3ta_{str(i)}.m3u8'
    with open(output_filename, 'wb') as output_file:
        output_file.write(modified_content.encode('utf-8'))

def main():
    #Local playlist files for each profile
    for i in range(1, number_of_profiles + 1):
        #Replace all .ts file references with S3 pre-signed URLs
        process_m3u_file(i, f'{profile_file_prefix}{str(i)}.m3u', s3_bucket)

    #Local Top-level playlist file
    m3u_file = open(playlist_file, 'rb')
    m3u_content = m3u_file.read().decode('utf-8')
    modified_content = replace_url_with_s3(m3u_content, s3_bucket)
    with open(output_filename, 'wb') as f:
        f.write(modified_content.encode('utf-8'))

    #Upload new playlists to S3
    for i in range(1, number_of_profiles + 1):
        upload_to_s3(f'{output_profile_prefix}{str(i)}.m3u8', s3_bucket)
    upload_to_s3(output_filename, s3_bucket)

    #Generate final presigned url for playlist
    s3_url = s3.generate_presigned_url('get_object', ExpiresIn=pre_signed_url_expiry, Params={'Bucket': s3_bucket, 'Key': bucket_prefix + output_filename})
    print(s3_url)

if __name__ == '__main__':
    main()