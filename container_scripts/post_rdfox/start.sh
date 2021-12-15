# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0


date
echo "Hello World! Start RDFox Publisher ";
grep -q 'The REST endpoint was successfully started' <(tail -f /output/rdfox.log);
echo "Signal found, start uploading results";
echo "Arguments:";
echo "BUCKET_NAME: $BUCKET_NAME";
echo "JOB_ID: $JOB_ID";
echo "DATA_PATH: $DATA_PATH";
ls -la /output
ls -la /output/data
echo "Recursive dir"
aws s3 cp /output/data s3://$BUCKET_NAME/$DATA_PATH/$JOB_ID/data --recursive
echo "And now the 2nd one";
aws s3 cp /output/rdfox.log s3://$BUCKET_NAME/$DATA_PATH/$JOB_ID/
echo 'Publishing data job end. Bash';
echo "Auto shutdown ${AUTO_SHUTDOWN}"
while [ $AUTO_SHUTDOWN == False ] ; do echo "Idling because no auto-shutdown please kill the job via the Kubernetes API"; sleep 10; done
date