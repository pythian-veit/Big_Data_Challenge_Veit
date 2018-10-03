# Big_Data_Challenge_Veit

The working data pipeline consists of the following components:
1) An app engine application that uses App Engine Cron Service to relay a cron message to Cloud Pub/Sub for the json_to_avro_convert topic every hour
2) A simple utility that runs on Compute Engine and monitors the above Pub/Sub topic.  When it detects a new message it runs the below
3) A python script (create_cluster_and_submit_job.py) that launches a Dataproc cluster, installs a needed python library (apache.avro) on the Dataproc cluster, runs a conversion script as a pyspark job (below), and tears down the Dataproc cluster
4) The aforementioned json_to_avro.py script converts json files located in the bdc_incoming bucket according to the .avsc file located in the bdc_schemas bucket.
    Successful conversions are placed in a unique directory in the bdc_processed bucket, and failures are placed in bdc_failed (all buckets are Regional class).
    This script is leveraging the Databricks library spark-avro.

I am attaching a gzip that contains:
1) All scripts and app engine files
2) Sample logs and screenshots
    In the example logs, sf_account.json, sf_account2.json, sf_account3.json are exactly the same source file duplicated. 
    The conversion of sf_account3.json fails and is gracefully handled by the script because there is no corresponding .avsc for this file.  
    example.json and twitter.json are two smaller examples I included to show the script could handle different schemas.
3) Converted avro files (Data folder)
