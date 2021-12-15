# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import boto3
import tempfile
import os
import click
import logging

logger = logging.getLogger("job_submitter")
logger.setLevel(logging.DEBUG)
c_handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
c_handler.setFormatter(formatter)
logger.addHandler(c_handler)

OUTPUT_BUCKET = "OUTPUT_BUCKET"
INPUT_BUCKET = "INPUT_BUCKER"
CURRENT_ACCOUNT = boto3.client("sts").get_caller_identity()["Account"]

JOB_TEMPLATE = {
    "requested_cores": 0,
    "requested_memory": "10Gi",
    "init_container_image": "1234567891011.dkr.ecr.ap-southeast-1.amazonaws.com/pre-rdfox:latest",
    "publisher_container_image": "1234567891011.dkr.ecr.ap-southeast-1.amazonaws.com/post-rdfox:latest",
    "rdfox_container_image": "1234567891011.dkr.ecr.ap-southeast-1.amazonaws.com/custom-rdfox:latest",
    "rdfox_init_container_image": "oxfordsemantic/rdfox-init",
    "auto_shutdown": True,
    "parallelism": 1,
    "job_bucket": INPUT_BUCKET,
    "job_key": "",
    "output_bucket": OUTPUT_BUCKET,
}


class JobSubmitter:
    def create_jobspec(
        self,
        requested_cores: int,
        requested_memory: int,
        job_key: str,
        auto_shutdown: bool,
        input_bucket: str,
        output_bucket: str,
        account_id: str,
    ):
        template = JOB_TEMPLATE.copy()
        template["requested_cores"] = requested_cores
        template["requested_memory"] = f"{requested_memory}Gi"
        template["job_key"] = job_key
        template["auto_shutdown"] = auto_shutdown
        template["job_bucket"] = input_bucket
        template["output_bucket"] = output_bucket
        template["init_container_image"] = self.substitute_account_in_image(
            template["init_container_image"], account_id
        )
        template["publisher_container_image"] = self.substitute_account_in_image(
            template["publisher_container_image"], account_id
        )
        template["rdfox_container_image"] = self.substitute_account_in_image(
            template["rdfox_container_image"], account_id
        )
        return template

    def substitute_account_in_image(self, image, account_id):
        current_account_id = image.split(".")
        new_image_id = f"{account_id}.{'.'.join(current_account_id[1:])}"
        return new_image_id

    def deploy_jobspec(self, job_spec, bucket, key):
        _, path = tempfile.mkstemp()
        try:
            with open(path, "wb") as data:
                data.write(bytes(json.dumps(job_spec), "utf-8"))
                logger.debug(f"Spec written to {path}")
            self.upload_jobspec_to_s3(bucket=bucket, key=key, temp_path=path)
        finally:
            os.remove(path)

    def upload_jobspec_to_s3(self, bucket, key, temp_path):
        s3 = boto3.resource("s3")
        bucket = s3.Bucket(bucket)
        with open(temp_path, "rb") as data:
            logger.info(f"Uploading {temp_path} to s3://{bucket}/{key}")
            bucket.upload_fileobj(data, key)

    def submit_job(
        self,
        data_set,
        account_id,
        requested_cores,
        requested_memory,
        auto_shutdown,
        output_bucket,
        input_bucket,
    ):

        job_spec = self.create_jobspec(
            requested_cores=requested_cores,
            requested_memory=requested_memory,
            job_key=data_set,
            auto_shutdown=auto_shutdown,
            account_id=account_id,
            input_bucket=input_bucket,
            output_bucket=output_bucket,
        )
        key = self.derive_job_spec_key(
            data_set,
            requested_cores,
            requested_memory,
            auto_shutdown,
        )
        self.deploy_jobspec(job_spec=job_spec, bucket=input_bucket, key=key)

    def derive_job_spec_key(
        self, data_set, requested_cores, requested_memory, auto_shutdown
    ):
        auto_shutdown_string = "_AUTOSHUTDOWN" if auto_shutdown else "PERSIST"
        return f"{data_set}/{data_set}_{requested_cores}cores_{requested_memory}Gi{auto_shutdown_string}.rdfoxjob.json"


@click.command()
@click.option("--cores")
@click.option("--memory")
@click.option("--data-set")
@click.option("--account-id", default=CURRENT_ACCOUNT)
@click.option("--input-bucket", default=INPUT_BUCKET)
@click.option("--output-bucket", default=OUTPUT_BUCKET)
@click.option("--auto-shutdown", default=True)
def go(data_set, cores, memory, auto_shutdown, account_id, input_bucket, output_bucket):
    scheduler = JobSubmitter()
    logger.info(
        f"Requested {cores} cores {memory}Gi memory against {input_bucket}{data_set} with auto-shutdown {auto_shutdown} for {account_id} to {output_bucket}"
    )
    scheduler.submit_job(
        data_set=data_set,
        requested_cores=int(cores),
        requested_memory=int(memory),
        auto_shutdown=bool(auto_shutdown),
        account_id=account_id,
        input_bucket=input_bucket,
        output_bucket=output_bucket,
    )


if __name__ == "__main__":
    go()
