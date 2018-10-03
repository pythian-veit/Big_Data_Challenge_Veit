#!/bin/bash
set -e -x

# Only run on the master node
ROLE=$(/usr/share/google/get_metadata_value attributes/dataproc-role)
if [[ "${ROLE}" == 'Master' ]]; then 
  apt-get install python-pip -y
  pip install avro
  
  # To eliminate "WARN org.apache.spark.util.Utils: Truncated the string representation of a plan since it was too large."
  sudo echo "spark.debug.maxToStringFields=1000" >> /etc/spark/conf/spark-defaults.conf
fi