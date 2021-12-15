# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from neptune_load.sigv4_signer.sigv4_signer import SigV4Signer
from neptune_load.bulk_loader.bulk_loader import BulkLoader
import logging
import os
import sys

logger = logging.getLogger("bulk_load")
logger.setLevel(logging.DEBUG)

if not logger.hasHandlers():
    c_handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    c_handler.setFormatter(formatter)
    logger.addHandler(c_handler)

if __name__ == "__main__":
    # parse_input_and_query_neptune()
    host = f'{os.getenv("NEPTUNE_ENDPOINT")}:8182'
    source_bucket = os.getenv("S3_BUCKET")
    loader_role = os.getenv("NEPTUNE_LOADER_IAM_ROLE")
    region = os.getenv("SERVICE_REGION")
    file_name = os.getenv("TRIPLE_NAME")

    source_string = f"s3://{source_bucket}/{file_name}"

    signer = SigV4Signer()
    loader = BulkLoader(
        signer=signer,
        iam_role_arn=loader_role,
        region=region,
        source=source_string,
        neptune_endpoint=host,
    )

    loader.reset_database()
