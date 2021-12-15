# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0


from neptune_load.sigv4_signer.sigv4_signer import SigV4Signer
from neptune_load.bulk_loader.bulk_loader import BulkLoader
import logging
import os
import sys

logger = logging.getLogger("bulk_load")
logger.setLevel(logging.INFO)


def kill_all_active(loader: BulkLoader):
    loads = loader.get_active_loads()
    logger.info(f"Loading {loads}")
    for load in loads:
        loader._load_id = load
        try:
            loader.cancel_load()
        except Exception as e:
            logger.warn(f"Failed to cancel {load} {e}")
    loader._load_id = None
    return


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

    loads = loader.get_active_loads()

    logger.info(f"Loading {loads}")

    kill_all_active(loader)

    try:
        loader.wait_for_bulk_load_from_s3()
    except KeyboardInterrupt as ke:
        logger.info(f"Cancellation requested")
        loader.cancel_load()
        logger.info(f"Final status \n {loader.status.raw}")
        sys.exit()

    logger.info(f"Load complete")
    logger.info(f"Results {loader.status.raw}")
