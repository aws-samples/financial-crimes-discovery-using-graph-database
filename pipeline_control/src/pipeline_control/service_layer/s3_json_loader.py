# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import os
import tempfile

import boto3


class S3JsonLoader:
    @classmethod
    def download_from_s3(
        cls,
        bucket_name: str,
        key: str,
    ):
        s3 = boto3.resource("s3")
        bucket = s3.Bucket(bucket_name)
        _, path = tempfile.mkstemp()
        try:
            with open(path, "wb") as data:
                bucket.download_fileobj(key, data)
            with open(path, "rb") as data:
                return data.read().decode("utf-8")
        finally:
            os.remove(path)

    @classmethod
    def download_and_load_json_from_s3(
        cls,
        bucket_name: str,
        key: str,
    ):
        return json.loads(cls.download_from_s3(bucket_name=bucket_name, key=key))
