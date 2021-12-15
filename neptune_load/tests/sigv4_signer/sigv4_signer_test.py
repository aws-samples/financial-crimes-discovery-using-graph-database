# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import requests
from neptune_load.sigv4_signer.sigv4_signer import SigV4Signer
import json
from pyexpect import expect
from unittest import mock

TEST_ACCESS_KEY_ID = "ASIA3REDACTEDQYM3YEW"
TEST_ACCESS_KEY_SECRET = "grEdACtedToPs3cretandnoonesbusinessreall"
TEST_SESSION_TOKEN = "FComple/teN0ns3nseforthemostpartxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
TEST_REGION = "ap-southeast-1"
TEST_DB_ENDPOINT = f"neptune.cluster-lollollollol.{TEST_REGION}.amazonaws.com"


class TestSigV4Signer:
    @mock.patch("requests.request", autospec=True)
    def test_signature_loader(self, mock_requests):

        # mock_requests = mock.Mock(spec=requests.request)

        neptune_signer_under_test = SigV4Signer(
            region=TEST_REGION,
            access_key_id=TEST_ACCESS_KEY_ID,
            access_key_secret=TEST_ACCESS_KEY_SECRET,
            session_token=TEST_SESSION_TOKEN,
        )

        method = "POST"
        query_type = "loader"
        load_query = {
            "source": f"s3://lalal/triples.nt",
            "format": "ntriples",
            "iamRoleArn": "who_cares",
            "region": TEST_REGION,
            "failOnError": "FALSE",
            "parallelism": "MEDIUM",
            "updateSingleCardinalityProperties": "TRUE",
            "queueRequest": "TRUE",
        }
        query_string = json.dumps(load_query)

        signed_request = neptune_signer_under_test.get_signed_request(
            host=TEST_DB_ENDPOINT,
            method=method,
            query_type=query_type,
            query=query_string,
        )

        expect(signed_request.method).to.equal("POST")
        expect(len(signed_request.params["headers"])).to.equal(4)
        signed_request.execute()

    def test_signature_sparql(self):
        neptune_signer_under_test = SigV4Signer(
            region=TEST_REGION,
            access_key_id=TEST_ACCESS_KEY_ID,
            access_key_secret=TEST_ACCESS_KEY_SECRET,
            session_token=TEST_SESSION_TOKEN,
        )

        method = "GET"
        query_type = "sparql"
        load_status_query = {
            "loadId": 666,
            "details": "true",
            "errors": "true",
            "page": "1",
        }
        query_string = json.dumps(load_status_query)

        signed_request = neptune_signer_under_test.get_signed_request(
            host=TEST_DB_ENDPOINT,
            method=method,
            query_type=query_type,
            query=query_string,
        )

        expect(signed_request.method).to.equal("GET")
        expect(len(signed_request.params["headers"])).to.equal(3)
