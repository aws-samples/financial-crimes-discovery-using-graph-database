# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0


date
echo "Hello World! Start RDFox init"
echo "Arguments:"
echo "BUCKET_NAME: $BUCKET_NAME";
echo "DATA_PATH: $DATA_PATH";
echo "AUTO_SHUTDOWN : $AUTO_SHUTDOWN";
aws s3 cp s3://$BUCKET_NAME/$DATA_PATH/ data  --recursive
cd data
DATA_FILES=`ls -d -1 "$PWD/"*.nt | tr '\012' ' '`
RULES_FILES=`ls -d -1 "$PWD/"*.dlog | tr '\012' ' '`
cd /
cp write-general-output.rdfox /scripts/write-general-output.rdfox
cd scripts
mkdir /output/data
chmod 777 /output/data
echo 'Generating rdfox load init script...'
echo '\
        tstamp beginload
        prefix : <http://oxfordsemantic.tech/transactions/entities#>
        prefix prop: <http://oxfordsemantic.tech/transactions/properties#>
        prefix type: <http://oxfordsemantic.tech/transactions/classes#>
        prefix tt: <http://oxfordsemantic.tech/transactions/tupletables#>
        set output out
        dstore create transactions type par-complex-nw
        active transactions
        ' >> rdfox_data_load.rdfox
echo -e 'set dir.output "/output/"' >> rdfox_data_load.rdfox
echo -e 'set dir.queries "/data/"'  >> rdfox_data_load.rdfox
echo -e 'set dir.scripts "/scripts/"' >> rdfox_data_load.rdfox
echo -e 'begin' >> rdfox_data_load.rdfox
echo -n 'import ' >> rdfox_data_load.rdfox
echo -n $RULES_FILES >> rdfox_data_load.rdfox
echo -e '\n' >> rdfox_data_load.rdfox
echo -n 'import ' >> rdfox_data_load.rdfox
echo -n $DATA_FILES >> rdfox_data_load.rdfox
echo -e '\n' >> rdfox_data_load.rdfox
echo -e 'tstamp endload' >> rdfox_data_load.rdfox
echo -e 'echo LOADTIME-$(beginload)|$(endload)' >> rdfox_data_load.rdfox
echo -e 'tstamp begininference' >> rdfox_data_load.rdfox
echo -e '\n' >> rdfox_data_load.rdfox
echo -e 'mat' >> rdfox_data_load.rdfox
echo -e 'commit' >> rdfox_data_load.rdfox
echo -e 'tstamp endinference' >> rdfox_data_load.rdfox
echo -e 'echo INFERENCETIME-$(begininference)|$(endinference)' >> rdfox_data_load.rdfox
echo -e 'tstamp beginquery' >> rdfox_data_load.rdfox
FILES="/path/to/*"
for i in $(ls /data/*.rq | xargs -n 1 basename);
do
  echo -e "write-general-output /output/data/$i.nt /data/$i" >> rdfox_data_load.rdfox
done
echo -e 'tstamp endquery' >> rdfox_data_load.rdfox
echo -e 'echo QUERYTIME-$(beginquery)|$(endquery)' >> rdfox_data_load.rdfox
echo -e 'echo ---info---' >> rdfox_data_load.rdfox
echo -e 'info' >> rdfox_data_load.rdfox
echo -e 'echo ---endinfo---' >> rdfox_data_load.rdfox
echo -e 'tstamp endts' >> rdfox_data_load.rdfox
echo -e 'echo TOTALTIME-$(beginload)|$(endts)' >> rdfox_data_load.rdfox
echo -e 'echo running-counts' >> rdfox_data_load.rdfox
echo -e 'set output out' >> rdfox_data_load.rdfox
echo -e 'set query.answer-format text/csv' >> rdfox_data_load.rdfox
echo -e 'SELECT (COUNT(?chain) AS ?partialChainCount) WHERE { VALUES ?chainType { type:ForwardChain type:BackwardChain } . ?chain a ?chainType}' >> rdfox_data_load.rdfox
echo -e 'echo 2nd-query' >> rdfox_data_load.rdfox
echo -e 'SELECT (COUNT(?chain) AS ?fullChainCount) WHERE { ?chain a type:FullChain}' >> rdfox_data_load.rdfox
echo -e 'echo end-running-counts' >> rdfox_data_load.rdfox
echo -e '\n endpoint start' >> rdfox_data_load.rdfox
[ $AUTO_SHUTDOWN = "True" ] && echo -e 'quit' >> rdfox_data_load.rdfox || echo 'doing nothing here'
cat rdfox_data_load.rdfox
echo 'RDFox Init job end.'
date