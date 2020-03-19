import boto3
import os

region = str(os.getenv("REGION"))

glue_client = boto3.client("glue", region)

def lambda_handler(event, context):

    # Iterate thru event object
    for record in event['Records']:

        # get object details
        request_id = record['responseElements']['x-amz-request-id']
        bucket = str(record['s3']['bucket']['name'])
        key = str(record['s3']['object']['key'])
        s3_source_path = "s3://"+bucket+"/"+key


        glue_job_name = str(os.getenv("GLUE_JOB_NAME"))
        glue_db = str(os.getenv("GLUE_DB"))
        glue_table = key.replace('.csv','')

        response = glue_client.start_job_run(
            JobName = glue_job_name,
            Arguments = {
                '--s3_source_path': s3_source_path,
                '--glue_db': glue_db,
                '--glue_table': glue_table } )
