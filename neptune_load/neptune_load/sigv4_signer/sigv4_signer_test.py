# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from neptune_load.sigv4_signer.sigv4_signer import SignedRequest, SigV4Signer
import time


class TestSigV4Signer(SigV4Signer):
    def __init__(self, signed_request: SignedRequest, succeed=True):
        self._signed_request = signed_request
        self._success = succeed

    def get_signed_request(self, host, method, query_type, query):
        if self._success:
            return self._signed_request
        raise Exception("Something is broken")


class TestSignedRequest(SignedRequest):
    def __init__(self, response: object, delay_in_seconds=0):
        self._response = response
        self._delay_in_seconds = delay_in_seconds

    def execute(self):
        if self._delay_in_seconds:
            time.sleep(self._delay_in_seconds)
        return self._response
