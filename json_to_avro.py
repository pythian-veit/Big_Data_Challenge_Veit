#!/usr/bin/env python
# [START pyspark]
import pyspark
from pyspark.sql import SQLContext
from pyspark.sql import SparkSession
import json 
from subprocess import call
from os.path import join
import os.path
import avro.schema
import subprocess
import uuid




sc = pyspark.SparkContext()
spark = SparkSession(sc) 

incoming_dir = "gs://bdc_incoming"
schemas_dir = "gs://bdc_avro_schemas"
processed_dir = "gs://bdc_processed"
failed_dir = "gs://bdc_failed"




def LoadAvsc(file_path, names=None):

  file_text = open(file_path).read() 
  json_data = json.loads(file_text)
  schema = avro.schema.make_avsc_object(json_data, names) 
  return schema 



def json2avro(src_file, schemas_path, schemas_file, dest_path, dest_prefix, failed_path):
 
  # Add random hex string to path for all files, to prevent collisions
  rand_hex = str(uuid.uuid4())
  schemas_file_local = join('/tmp', rand_hex + '_' + schemas_file)
  dest_path = join(dest_path,dest_prefix+'_'+rand_hex)
  failed_path = join(failed_path,dest_prefix+'_'+rand_hex+'.json')

  try: 
 
    # Retrieve the corresponding .avsc file, safe it locally, and load it into avro_schema
    call(["hadoop","fs","-copyToLocal",join(schemas_path,schemas_file),schemas_file_local])
    file_text = open(schemas_file_local).read()

    known_schemas = avro.schema.Names()
    avro_schema = LoadAvsc(schemas_file_local, known_schemas)


    # Read the file into a dataframe with the schema from above, then write it out as avro
    df = spark.read.format("json").option("avroSchema", avro_schema).option("inferSchema", "false").load(src_file)
    df.write.format("com.databricks.spark.avro").option("avroSchema", avro_schema).save(dest_path)

  # If this process fails for any reason (missing .avsc, mismatched schema, etc) move the file from the incoming bucket to the failed bucket
  except:
    call(["hadoop","fs","-cp",src_file,failed_path])
    call(["hadoop","fs","-rm",src_file])
    print "Processing for the following file failed: %s" % src_file
    print "Failed file has been moved to: %s" % failed_path
  
  # Upon successful writing of the avro file, remove the json file from the incoming bucket
  else:
    call(["hadoop","fs","-rm",src_file])
    print "Conversion to avro for the following file succeeded: %s" % src_file
    print "Converted file is located in: %s" % dest_path



# Retrieve all json files from any part of the incoming bucket
filelist = [ line.rsplit(None,1)[-1] for line in subprocess.check_output(["hadoop","fs","-find",incoming_dir,"-name","*.json"]).split('\n') if len(line.rsplit(None,1))]

# Loop over the files and convert them to avro
for file_w_path in filelist:
  path, filename = os.path.split(file_w_path)
  filename, ext = os.path.splitext(filename)
  
  json2avro(file_w_path, schemas_dir, filename + '.avsc', processed_dir, filename, failed_dir)



# [END pyspark]