import boto3
import os

glue_client = boto3.client("glue", "us-east-1")

def lambda_handler(event, context):

    # Iterate thru event object
    for record in event['Records']:

        # get object details
        request_id = record['responseElements']['x-amz-request-id']
        s3_source = str(record['s3']['bucket']['name'])
        key = str(record['s3']['object']['key'])

        glue_job_name = os.getenv("job_name")
        glue_db = os.getenv("glue_db")
        glue_table = s3_key.replace('.csv','')

        response = glue_client.start_job_run(
            JobName = glue_job_name,
            Arguments = {
                '--s3_source': s3_source,
                '--s3_key': key,
                '--glue_db': glue_db,
                '--glue_table': glue_table } )
