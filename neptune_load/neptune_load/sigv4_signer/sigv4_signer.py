# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# Amazon Neptune version 4 signing example (version v2)

# Taken from https://docs.aws.amazon.com/general/latest/gr/sigv4_signing.html
# This version makes a GET request and passes the signature
# in the Authorization header.

import sys, datetime, hashlib, hmac
import urllib
import json
import logging
import requests
from requests.models import Response
import boto3
import sys

logger = logging.getLogger(__name__)

# formatter = logging.Formatter(
#     fmt="%(asctime)s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
# )

# screen_handler = logging.StreamHandler(stream=sys.stdout)
# screen_handler.setFormatter(formatter)

# logger.addHandler(screen_handler)

# Configuration. http is required.
protocol = "https"

# The following lines enable debugging at httplib level (requests->urllib3->http.client)
# You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
#
# The only thing missing will be the response.body which is not logged.
#

# http_client.HTTPConnection.debuglevel = 1


class SigV4Signer:
    def __init__(
        self,
        region: str = None,
        access_key_id: str = None,
        access_key_secret: str = None,
        session_token: str = None,
    ):

        if not (access_key_id and access_key_secret):
            session = boto3.session.Session()
            session_credentials = session.get_credentials()
            region = session.region_name
            access_key_id = session_credentials.access_key
            access_key_secret = session_credentials.secret_key
            session_token = session_credentials.token

        if not (region and access_key_id and access_key_secret):
            raise Error("Must supply or derive region, key_id and key_secret")

        self._access_key_id = access_key_id
        self._access_key_secret = access_key_secret
        self._session_token = session_token
        self._region = region

    def normalize_query_string(self, query):
        kv = (
            list(map(str.strip, s.split("="))) for s in query.split("&") if len(s) > 0
        )

        normalized = "&".join(
            "%s=%s" % (p[0], p[1] if len(p) > 1 else "") for p in sorted(kv)
        )
        return normalized

    # Key derivation functions. See:
    # https://docs.aws.amazon.com/general/latest/gr/signature-v4-examples.html#signature-v4-examples-python
    def sign(self, key, msg):
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

    def get_signature_key(self, dateStamp, serviceName):
        kDate = self.sign(("AWS4" + self._access_key_secret).encode("utf-8"), dateStamp)
        kRegion = self.sign(kDate, self._region)
        kService = self.sign(kRegion, serviceName)
        kSigning = self.sign(kService, "aws4_request")
        return kSigning

    def validate_input(self, method, query_type):
        # Supporting GET and POST for now:
        if method != "GET" and method != "POST" and method != "DELETE":
            logger.info(
                'First parameter must be "GET" or "POST", but is "' + method + '".'
            )
            raise Exception("This shouldn't happen")

        # SPARQL UPDATE requires POST
        if method == "GET" and query_type == "sparqlupdate":
            logger.info(
                "SPARQL UPDATE is not supported in GET mode. Please choose POST."
            )
            raise Exception("This shouldn't happen")

        # Note: it looks like Gremlin POST requires the query to be encoded in a JSON
        # struct; we haven't implemented this in the python script, so let's for now
        # disable Gremlin POST requests.
        if method == "POST" and query_type == "gremlin":
            logger.info(
                "POST is currently not supported for Gremlin in this python script."
            )
            raise Exception("This shouldn't happen")

    def get_canonical_uri_and_payload(self, query_type, query):
        # Set the stack and payload depending on query_type.
        if query_type == "sparql":
            canonical_uri = "/sparql/"
            payload = {"query": query}

        elif query_type == "sparqlupdate":
            canonical_uri = "/sparql/"
            payload = {"update": query}

        elif query_type == "gremlin":
            canonical_uri = "/gremlin/"
            payload = {"gremlin": query}

        elif query_type == "loader":
            canonical_uri = "/loader/"
            payload = json.loads(query)

        elif query_type == "status":
            canonical_uri = "/status/"
            payload = {}
        elif query_type == "system":
            canonical_uri = "/system/"
            payload = json.loads(query)

        else:
            logger.info(
                'Third parameter should be from ["gremlin", "sparql", "sparqlupdate", "loader", "status", "system"] but is "'
                + query_type
                + '".'
            )
            raise Exception("This shouldn't happen")
        ## return output as tuple
        return canonical_uri, payload

    def get_signed_request(self, host, method, query_type, query):
        service = "neptune-db"
        endpoint = protocol + "://" + host

        logger.info("+++++ USER INPUT +++++")
        logger.info("host = " + host)
        logger.info("method = " + method)
        logger.info("query_type = " + query_type)
        logger.info("query = " + query)

        # validate input
        self.validate_input(method, query_type)

        # get canonical_uri and payload
        canonical_uri, payload = self.get_canonical_uri_and_payload(query_type, query)
        logger.info(payload)

        # ************* REQUEST VALUES *************

        # do the encoding => quote_via=urllib.parse.quote is used to map " " => "%20"
        request_parameters = urllib.parse.urlencode(
            payload, quote_via=urllib.parse.quote
        )
        request_parameters = request_parameters.replace("%27", "%22")
        logger.info(request_parameters)

        # ************* TASK 1: CREATE A CANONICAL REQUEST *************
        # https://docs.aws.amazon.com/general/latest/gr/sigv4-create-canonical-request.html

        # Step 1 is to define the verb (GET, POST, etc.)--already done.

        # Create a date for headers and the credential string.
        t = datetime.datetime.utcnow()
        amzdate = t.strftime("%Y%m%dT%H%M%SZ")
        datestamp = t.strftime("%Y%m%d")  # Date w/o time, used in credential scope

        # ************* TASK 1: CREATE A CANONICAL REQUEST *************
        # https://docs.aws.amazon.com/general/latest/gr/sigv4-create-canonical-request.html

        # Step 1 is to define the verb (GET, POST, etc.)--already done.
        # Step 2: is to define the canonical_uri--already done.

        # Step 3: Create the canonical query string. In this example (a GET request),
        # request parameters are in the query string. Query string values must
        # be URL-encoded (space=%20). The parameters must be sorted by name.
        # For this example, the query string is pre-formatted in the request_parameters variable.
        if method == "GET" or method == "DELETE":
            canonical_querystring = self.normalize_query_string(request_parameters)
        elif method == "POST":
            canonical_querystring = ""
        else:
            logger.info(
                'Request method is neither "GET" nor "POST", something is wrong here.'
            )
            raise Exception("This shouldn't happen")

        # Step 4: Create the canonical headers and signed headers. Header names
        # must be trimmed and lowercase, and sorted in code point order from
        # low to high. Note that there is a trailing \n.
        canonical_headers = "host:" + host + "\n" + "x-amz-date:" + amzdate + "\n"

        # Step 5: Create the list of signed headers. This lists the headers
        # in the canonical_headers list, delimited with ";" and in alpha order.
        # Note: The request can include any headers; canonical_headers and
        # signed_headers lists those that you want to be included in the
        # hash of the request. "Host" and "x-amz-date" are always required.
        signed_headers = "host;x-amz-date"

        # Step 6: Create payload hash (hash of the request body content). For GET
        # requests, the payload is an empty string ("").
        if method == "GET" or method == "DELETE":
            post_payload = ""
        elif method == "POST":
            post_payload = request_parameters
        else:
            logger.info(
                'Request method is neither "GET" nor "POST", something is wrong here.'
            )
            raise Exception("This shouldn't happen")

        payload_hash = hashlib.sha256(post_payload.encode("utf-8")).hexdigest()

        # Step 7: Combine elements to create canonical request.
        canonical_request = (
            method
            + "\n"
            + canonical_uri
            + "\n"
            + canonical_querystring
            + "\n"
            + canonical_headers
            + "\n"
            + signed_headers
            + "\n"
            + payload_hash
        )

        # ************* TASK 2: CREATE THE STRING TO SIGN*************
        # Match the algorithm to the hashing algorithm you use, either SHA-1 or
        # SHA-256 (recommended)
        algorithm = "AWS4-HMAC-SHA256"
        credential_scope = (
            datestamp + "/" + self._region + "/" + service + "/" + "aws4_request"
        )
        string_to_sign = (
            algorithm
            + "\n"
            + amzdate
            + "\n"
            + credential_scope
            + "\n"
            + hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()
        )

        # ************* TASK 3: CALCULATE THE SIGNATURE *************
        # Create the signing key using the function defined above.
        signing_key = self.get_signature_key(datestamp, service)

        # Sign the string_to_sign using the signing_key
        signature = hmac.new(
            signing_key, (string_to_sign).encode("utf-8"), hashlib.sha256
        ).hexdigest()

        # ************* TASK 4: ADD SIGNING INFORMATION TO THE REQUEST *************
        # The signing information can be either in a query string value or in
        # a header named Authorization. This code shows how to use a header.
        # Create authorization header and add to request headers
        authorization_header = (
            algorithm
            + " "
            + "Credential="
            + self._access_key_id
            + "/"
            + credential_scope
            + ", "
            + "SignedHeaders="
            + signed_headers
            + ", "
            + "Signature="
            + signature
        )

        # The request can include any headers, but MUST include "host", "x-amz-date",
        # and (for this scenario) "Authorization". "host" and "x-amz-date" must
        # be included in the canonical_headers and signed_headers, as noted
        # earlier. Order here is not significant.
        # Python note: The 'host' header is added automatically by the Python 'requests' library.
        if method == "GET" or method == "DELETE":
            headers = {"x-amz-date": amzdate, "Authorization": authorization_header}
        elif method == "POST":
            headers = {
                "content-type": "application/x-www-form-urlencoded",
                "x-amz-date": amzdate,
                "Authorization": authorization_header,
            }
        else:
            logger.info(
                'Request method is neither "GET" nor "POST", something is wrong here.'
            )
            raise Exception("This shouldn't happen")

        # https://docs.aws.amazon.com/general/latest/gr/sigv4-create-canonical-request.html
        # The process for temporary security credentials is the same as using long-term credentials and
        # for temporary security credentials should be added as parameter name is X-Amz-Security-Token.
        if self._session_token:
            headers["x-amz-security-token"] = self._session_token

        request_url = endpoint + canonical_uri
        request_config = None

        if method == "GET":
            request_config = (
                "GET",
                request_url,
                {
                    "headers": headers,
                    "verify": False,
                    "params": request_parameters,
                },
            )
        elif method == "DELETE":
            request_config = (
                "DELETE",
                request_url,
                {
                    "headers": headers,
                    "verify": False,
                    "params": request_parameters,
                },
            )
        elif method == "POST":
            request_config = (
                "POST",
                request_url,
                {"headers": headers, "verify": False, "data": request_parameters},
            )
            # r = requests.request(
            #    **post_request_config
            # )

        else:
            raise Exception(
                'Request method is neither "GET" nor "POST", something is wrong here.'
            )

        return SignedRequest(
            method=request_config[0], url=request_config[1], params=request_config[2]
        )


class SignedRequest:
    def __init__(self, method: str, url: str, params: dict):
        self._method = method
        self._url = url
        self._params = params

    @property
    def method(self):
        return self._method

    @property
    def url(self):
        return self._url

    @property
    def params(self):
        return self._params

    def validate(self):
        raise Exception("Not yet implemented")

    def execute(self) -> Response:
        return requests.request(self._method, self._url, **self._params)
