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
                           's3_source',
                           'glue_db',
                           'glue_table'])

s3_source = str(args['s3_source'])
glue_db = str(args['glue_db'])
glue_table = str(args['glue_table'])

# Initialize Glue Context
glueContext = GlueContext(SparkContext.getOrCreate())

# Get Glue Table information
glue_client = boto3.client("glue", "us-east-1")
table = glue_client.get_table(DatabaseName=glue_db, Name=glue_table)

table_columns = table['Table']['StorageDescriptor']['Columns']
s3_destination = str(table['Table']['StorageDescriptor']['Location'])

# Create Dynamic Frame from S3 CSV Object
dynamicFrame = glueContext.create_dynamic_frame_from_options(connection_type = "s3", connection_options = {"paths": [s3_source]}, format_options={"withHeader": True,"separator": ","}, format = "csv")

# Convert to Spark Data Frame
dataFrame = dynamicFrame.toDF()

# Cast Column types from Glue Table into Spark Data Frame
for column in table_columns:
    dataFrame = dataFrame.withColumn(column['Name'], dataFrame[column['Name']].cast(column['Type']))

# Convert back to Glue Dynamic Frame for S3 upload
final_dynamicFrame = DynamicFrame.fromDF(dataFrame, glueContext, "final_dynamicFrame")

# Delete any unnecessary columns
final_dynamicFrame = final_dynamicFrame.drop_fields(['col4', 'col5', 'col6'])

print("CYLOG: s3 destination: "+s3_destination)


# Send dynamic frame to S3 as parquet files. S3 location specified by the given Glue table
glueContext.write_dynamic_frame.from_options(frame = final_dynamicFrame, connection_type = "s3", connection_options = {"path":s3_destination}, format = "parquet")

