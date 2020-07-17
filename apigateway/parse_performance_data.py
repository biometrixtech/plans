import boto3
import io
import pandas as pd
import numpy as np
import zipfile


def lambda_handler(event, _):
    print(f"Starting unzipping for file {event['Records'][0]['s3']['object']['key']}")
    s3_key = ""
    s3_bucket = ""
    try:
        print(event)
        record = event['Records'][0]
        s3_bucket = record['s3']['bucket']['name']
        s3_key = record['s3']['object']['key']

        ids = s3_key.split('/')
        user_id = ids[-2]
        session_id = ids[-1]
        s3_resource = boto3.resource('s3')
        s3_object = s3_resource.Object(s3_bucket, s3_key)

        fileobj = s3_object.get()
        print('Got Fileobj')
        body = fileobj["Body"].read()
        print('Read Content')
        content = io.BytesIO(body)
        print('Converted Content')
        unzipped_files = zipfile.ZipFile(content)
        names = unzipped_files.namelist()
        for name in names:
            unzipped_content = unzipped_files.open(name).read()
            print(f'Unzipped File: {name}')
            s3_resource.Bucket(s3_bucket).put_object(Key=f'unzipped/{user_id}/{session_id}/{name}', Body=unzipped_content)
        print('Wrote File to processed container')
    except Exception as e:
        print(e)
        print(f'Error getting object {s3_key} from bucket {s3_bucket}. Make sure they exist and your bucket is in the same region as this function.')
        raise e
