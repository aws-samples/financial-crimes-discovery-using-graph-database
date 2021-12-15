# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0


date
echo "Hello World! Start Generating Data"
echo "Arguments:"
echo "BUCKET_NAME: $BUCKET_NAME";
echo "DATA_PATH: $DATA_PATH";
echo "NUM_OF_MSG: $NUM_OF_MSG";
echo "NUM_OF_FILES: $NUM_OF_FILES";
echo "NUM_OF_PARTIES: $NUM_OF_PARTIES";
echo "MAX_DAYS_BEFORE : $MAX_DAYS_BEFORE";
echo "CHAIN_DAYS_RANGE: $CHAIN_DAYS_RANGE";
echo "THREAD_COUNT: $THREAD_COUNT";
date
aws sts get-caller-identity
cd /transactions_generator
python3 -u main.py -o /data -tc $NUM_OF_MSG -pc $NUM_OF_PARTIES -mdb $MAX_DAYS_BEFORE -cdr $CHAIN_DAYS_RANGE -fc $NUM_OF_FILES -thc $THREAD_COUNT -nrap 0.001 -sp 0.001
echo 'Generating data job end.'
date
echo 'Start S3 Copy.'
aws s3 cp /data s3://$BUCKET_NAME/$DATA_PATH --recursive
echo 'S3 Copy end.'
date