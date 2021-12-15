# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0


echo "RDFOX Application starts"
date
/opt/RDFox/RDFox sandbox /data exec /scripts/rdfox_data_load.rdfox | tee -a /output/rdfox.log
echo "RDFOX Application ends"
date
