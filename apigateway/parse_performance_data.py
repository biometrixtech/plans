import json
import urllib
import boto3
import logging
import io
# import pandas
# import numpy



def lambda_handler(event, context):
    print('invoked')
    print(event, context)
    
    # logger.info('Starting unzipping for file' + urllib.unquote_plus(event['Records'][0]['s3']['object']['key']).encode('utf8'))
    
    # try:
    #     cont_write = 'fathom-otf'
    #     bucket = event['Records'][0]['s3']['bucket']['name']
    #     key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key']).encode('utf8')
    #     s3r = boto3.resource('s3')

    #     logger.info('Obtained S3 Resource')
    #     obj = s3r.Bucket(bucket).Object(key)
    #     logger.info('Obtained Key')        
    #     fileobj = obj.get()
    #     logger.info('Got Fileobj')        
    #     body = fileobj["Body"].read()
    #     logger.info('Read Content')        
    #     content = cStringIO.StringIO(body)
    #     logger.info('Converted Content')
    #     zipped = zf.ZipFile(content)
    #     names = zipped.namelist()
    #     # unzipped_content = cStringIO.StringIO()
    #     for name in names:
    #         unzipped_content = zipfiles.open(name).read()
    #         logger.info('Unzipped File')
    #         # data = pd.read_csv(unzipped_content)
    #         # f = cStringIO.StringIO()
    #         # data.to_csv(f, index = False)
    #         # f.seek(0)
    #         s3r.Bucket(cont_write).put_object(Key='unzipped/'+key+'.csv', Body=unzipped_content)
    #     logger.info('Wrote File to processed container')
    # except Exception as e:
    #     logger.info(e)
    #     logger.info('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
    #     raise e
