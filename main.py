import boto3
from botocore.config import Config

conf = Config(
    s3={
        'use_accelerate_endpoint':True
    }
)

s3_bucket = 'jhart-video-syd'
region = 'ap-southeast-2'
s3 = boto3.client('s3', region_name=region, config=conf)
number_of_profiles = 5
bucket_prefix = "hls/"
playlist_file = 'playlist.m3u8'
profile_file_prefix = 'bbb_sunflower_1080p_30fps_normal_'
output_filename = 's3ta.m3u8'
output_profile_prefix = 's3ta_'

def replace_url_with_s3(m3u_content, s3_bucket):
    lines = m3u_content.splitlines()
    modified_lines = []
    i = 1
    for line in lines:
        if line.endswith('.m3u8'):
            s3_url = s3.generate_presigned_url('get_object', ExpiresIn=3600, Params={'Bucket': s3_bucket, 'Key': f'{bucket_prefix}{output_profile_prefix}{str(i)}.m3u8'})
            modified_lines.append(s3_url)
            i += 1
        elif line.endswith('.ts'):
            s3_url = s3.generate_presigned_url('get_object', ExpiresIn=3600, Params={'Bucket': s3_bucket, 'Key': f'{bucket_prefix}{line}'})
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
    s3_url = s3.generate_presigned_url('get_object', ExpiresIn=3600, Params={'Bucket': s3_bucket, 'Key': bucket_prefix + output_filename})
    print(s3_url)

if __name__ == '__main__':
    main()