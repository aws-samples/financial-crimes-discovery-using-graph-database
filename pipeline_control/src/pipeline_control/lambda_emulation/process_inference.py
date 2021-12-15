# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import pipeline_control.entrypoints.lambda_entry_points

event = {
    "Records": [
        {
            "eventVersion": "2.1",
            "eventSource": "aws:s3",
            "awsRegion": "ap-southeast-1",
            "eventTime": "2021-08-11T05:26:25.519Z",
            "eventName": "ObjectCreated:Put",
            "userIdentity": {
                "principalId": "AWS:AROA3LQRMF7H3PQEFEE4W:botocore-session-1628659584"
            },
            "requestParameters": {"sourceIPAddress": "13.213.146.78"},
            "responseElements": {
                "x-amz-request-id": "VTA3RS70TH1NAEEP",
                "x-amz-id-2": "NJUZdIsmVpCtpAxBqZHBJIaKhciRdq0vLph7kgBFW0OKHvx5w7vObYLH9Ysw82hP6+Eu4ZgUkGrpFoXOrw+GF12Md+BB5A1d",
            },
            "s3": {
                "s3SchemaVersion": "1.0",
                "configurationId": "tf-s3-lambda-2021072712483736980000000f",
                "bucket": {
                    "name": "abucket",
                    "ownerIdentity": {"principalId": "A19CXUXLPSHOAK"},
                    "arn": "arn:aws:s3:::abucket",
                },
                "object": {
                    "key": "TEST-SET/TEST-SET_2021-08-18_001/rdfox.log",
                    "size": 4472,
                    "eTag": "6677468c4fe39f33f74d3675069b8cbb",
                    "sequencer": "0061135F854EFA0350",
                },
            },
        }
    ]
}


pipeline_control.entrypoints.lambda_entry_points.handle_process_inference(event, {})
