import boto3
import botocore
import configparser
import pathlib
import sys


""" Load AWS credentials """
parser = configparser.ConfigParser()
script_path = pathlib.Path(__file__).parent.resolve()
config_file = "config.conf"
parser.read(f"{script_path}/{config_file}")

BUCKET_NAME = parser.get("aws_config", "bucket_name")
AWS_REGION = parser.get("aws_config", "aws_region")
AWS_ACCESS_KEY = parser.get("aws_config", "access_key")
AWS_SECRET_KEY = parser.get("aws_config", "secret_key")

try:
    output_name = sys.argv[1]
except Exception as e:
    print(f"Command line argument not passed. Error {e}")
    sys.exit(1)

FILENAME = f"{output_name}.csv"

def main():
    s3 = s3_connect()
    check_bucket(s3)
    load_to_s3(s3)


""" Initialize connection to S3 Instance"""
def s3_connect():
    try:
        s3 = boto3.resource("s3", aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
        return s3
    except Exception as e:
        print(f"Cannot connect to s3 resource: {e}")
        sys.exit(1)

""" Check that the bucket has been instantiated """
def check_bucket(s3):
    exists = True
    try:
        s3.meta.client.head_bucket(Bucket=BUCKET_NAME)
    except botocore.exceptions.ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "404":
            exists = False
    if not exists:
        s3.create_bucket(
            Bucket=BUCKET_NAME,
            CreateBucketConfiguration={"LocationConstraint": AWS_REGION},
        )


""" Load the playlist and track data to S3 bucket"""
def load_to_s3(s3):
    s3.meta.client.upload_file(
        Filename=f"{script_path}/tmp/playlist_{FILENAME}", Bucket=BUCKET_NAME, Key=f"playlist_{output_name}"
    )
    s3.meta.client.upload_file(
        Filename=f"{script_path}/tmp/tracks_{FILENAME}", Bucket=BUCKET_NAME, Key=f"tracks_{output_name}"
    )

if __name__ == "__main__":
    main()
