import sys
import boto3
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame

# Get Input Params
args = getResolvedOptions(sys.argv,
                          ['JOB_NAME',
                           's3_source_path',
                           'glue_db',
                           'glue_table'])

s3_source_path = str(args['s3_source_path'])
glue_db = str(args['glue_db'])
glue_table = str(args['glue_table'])

# Initialize Glue Context
glueContext = GlueContext(SparkContext.getOrCreate())

# Create AWS clients/resources
glue_client = boto3.client("glue", "us-east-1")
s3_resource = boto3.resource('s3')

# Get Bucket and Key values for S3 object
path_parts=s3_source_path.replace("s3://","").split("/")
bucket=path_parts.pop(0)
key="/".join(path_parts)

# Determine if S3 object exists
s3_object_exists = False
try:
    s3_resource.Object(bucket, key).load()
    s3_object_exists = True
except Exception as e:
    print("S3 object not found. error message: "+str(e))

if (s3_object_exists):
    try:
        table = glue_client.get_table(DatabaseName=glue_db, Name=glue_table)

        table_columns = table['Table']['StorageDescriptor']['Columns']
        s3_destination = str(table['Table']['StorageDescriptor']['Location'])

        # Create Dynamic Frame from S3 CSV Object
        dynamicFrame = glueContext.create_dynamic_frame_from_options(connection_type = "s3", connection_options = {"paths": [s3_source_path]}, format_options={"withHeader": True,"separator": ","}, format = "csv")

        # Convert to Spark Data Frame
        dataFrame = dynamicFrame.toDF()

        # Cast Column types from Glue Table into Spark Data Frame
        for column in table_columns:
            dataFrame = dataFrame.withColumn(column['Name'], dataFrame[column['Name']].cast(column['Type']))

        # Convert back to Glue Dynamic Frame for S3 upload
        final_dynamicFrame = DynamicFrame.fromDF(dataFrame, glueContext, "final_dynamicFrame")

        # Delete any unnecessary columns
        final_dynamicFrame = final_dynamicFrame.drop_fields(['col4', 'col5', 'col6'])

        # Send dynamic frame to S3 as parquet files. S3 location specified by the given Glue table
        glueContext.write_dynamic_frame.from_options(frame = final_dynamicFrame, connection_type = "s3", connection_options = {"path":s3_destination}, format = "parquet")

        # Successfully converted CSV file. Move CSV file to processed folder.
        s3_resource.Object(bucket, "processed/"+key).copy_from( CopySource=bucket+"/"+key)
        s3_resource.Object(bucket, key).delete()

    except Exception as e:
        print("Conversion failed. Moving object to error folder. error message: "+str(e))
        s3_resource.Object(bucket, "error/"+key).copy_from( CopySource=bucket+"/"+key)
        s3_resource.Object(bucket, key).delete()

