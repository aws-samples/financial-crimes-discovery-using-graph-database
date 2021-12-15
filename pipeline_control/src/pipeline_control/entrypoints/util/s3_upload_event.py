# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0


class S3Uploadevent:
    def __init__(self, event):
        self._event = event

    @classmethod
    def from_json(cls, event):
        return cls(event=event)

    @property
    def bucket(self):
        return self._event["Records"][0]["s3"]["bucket"]

    @property
    def s3_object(self):
        return self._event["Records"][0]["s3"]["object"]

    @property
    def bucket_name(self):
        return self.bucket["name"]

    @property
    def object_key(self):
        return self.s3_object["key"]
