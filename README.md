# csv-to-parquet-via-glue

## Converting CSV files into Parquet using AWS Glue Jobs

Proof of Concept to show how Lambda can trigger a glue job to perform data transformations. CSV to Parquet conversion workaround for data with line-breaks.

## About

When CSV files have line-breaks, it is difficult to perform S3 event-based csv to parquet conversions. Amazon Athena and AWS Glue Crawlers do not sufficiently handle line-breaks in data.  Use this solution to circumvent that issue.

----

## Architecture

![Stack-Resources](https://github.com/CYarros10/csv-to-parquet-via-glue/blob/master/architecture/datalake-transforms.png)

----

## Pre-requisites

1. A Glue Catalog with pre-defined database and table schemas
2. An existing S3 bucket location for table data (should be defined in the Glue Data Catalog)
3. An S3 bucket for pre-defined scripts
4. An S3 bucket for glue temporary filescd

## Before Deployment

This solution assumes there is existing scripts and data definitions in place.

1. Upload all contents in scripts folder to an existing s3 bucket. This will be the code for the lambdas/glue job.
2. Create a table in AWS Glue Data Catalog

ex.
Table Name: un_general_debates
Columns:

- session int
- year int
- country string
- text string

## Deploying Cloudformation

1. Go to [AWS Cloudformation Console](https://console.aws.amazon.com/cloudformation/) and choose **Create stack**
2. upload the cloudformation/master.yml template
3. enter parameters

### What is the Cloudformation creating?

1. A Source S3 bucket for CSV files to land in
2. A Lambda/Custom resource to add an S3 trigger to the Source S3 bucket
3. A Lambda that triggers whenever a CSV lands in Source S3 bucket - takes S3 object information and asynchronously starts a Glue Job
4. A glue job that retrieves data catalog information to transform CSV to parquet and place in table S3 location

## Viewing results

1. Go to [Amazon S3 Console](https://s3.console.aws.amazon.com/s3/). Upload a CSV file to the Source S3 Bucket. This triggers a lambda. ( there is sample data here: samples/un_general_debates.csv)
2. If the csv file correlates with an existing Glue Table, the lambda will start a glue job.
3. Go to the [AWS Glue console](https://console.aws.amazon.com/glue/) to view progess of the Glue Job
4. Finally, once the glue job successfully completes, you are ready to query the data.
5. Go to [Amazon Athena console](https://console.aws.amazon.com/athena) and perform the following query to view results:

        select * from un_general_debates order by year desc;
