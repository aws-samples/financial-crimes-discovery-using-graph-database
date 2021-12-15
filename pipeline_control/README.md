
<!-- PROJECT SHIELDS -->
<!--
-->
[![security: bandit](https://img.shields.io/badge/security-bandit-green.svg)](https://github.com/PyCQA/bandit)

# 📜 Prequisites
* python >= 3.7
* pypoetry (optional but recommended)

# 💡 Overview
This package contains the code to orchestrate the pipeline. This code base is deployed across all three lambda functions. 

At a high level this package does the following
* Building RDFox Kubernetes Job specs and applying them
* Initiating and controlling a bulk load from S3 into Neptune
* Querying bulk load status
* Notifiying users of job completion via an SNS topic
* Reading and writing job meta-data information

# 🗞️ Install

## Install and use *Poetry*
As this is Python there is no build step as such. However, in order to keep host os python config clean we use *poetry* to manage dependencies and building of distribution archives.

if not already installed install [poetry](https://python-poetry.org/docs/#installation)

```curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python - ```

Poetry will ensure all interactions take place in the context of the virtual env and the rest of this documentation is based on it.

*Note:* You may wonder why there is no *requirements.txt* file in this repo and the reason is poetry uses *pyproject.toml* instead. Note, that if you require a *requirements.txt* file you can generate one using ```poetry export -f requirements```

*Note:* If you prefer not to use *poetry* all steps can be achieved without it, but in this case virtual environments and/or dependencies need to be managed by you.

## Install packages
Once *poetry* is installed you can install pipeline_control and its dependencies into a virtuel env

```poetry install```

*Important note*: pipeline_control relies on the *neptune_load* library, also contained in this monorepo. In order to install pipeline_control you will need to first "build" neptune_load's dist archive (see [README.md in ../neptune_load/README.md](../neptune_load/README.md)).

# Usage
The primary purpose of this package is to be used in the three AWS Lambda functions to orchestrate the Graph reasoning pipeline. 

## Configuration
The system attempts to take all its configuration from the AWS Systems Manager parameter store */parameter/pipeline_control/*  and fall back on locally configured environment variables. 

The system considers the following environment variables. Note, that are overwritten by individual job specs.

* CLUSTER_NAME: The name of the EKS cluster to schedule jobs on
* JOB_TABLE_NAME: The name of the DynamoDB Table used to meta-data
* JOBSPEC_NAME: The suffix name that identifies an uploaded file as a job (default=rdfoxjob.json)
* RDFOXLOG_NAME: The name identifying an rdfox performance log (default=rdfox.log)
* AWS_DEFAULT_REGION: The name of the AWS region (used by SDKs)
* JOB_ID_DELIMETER: The character to use to split the parts of a job_id (default="_" e.g. MYDATASET_2021-08-01_000)
* BULKLOAD_TOPIC: The name of the SNS topic to notify on job completion
* NEPTUNE_IAM_ROLE_ARN: The ARN of the role used by the Neptune cluster to perform the bulkload to S3. This has to match what has been configured on the cluster and needs to have read access to the bucket and Decrypt on the KMS key holding the data to load
* NEPTUNE_SOURCE_FORMAT: The format to use for the bulkload (default="turtle")
* NEPTUNE_UPDATE_SINGLE_CARDINALITY_PROPERTIES: As per loader documentation (default="True")
* NEPTUNE_PARALLELISM: As per loader documentation (default="True")
* NEPTUNE_QUEUE_REQUEST: As per loader documentation (default="True")
* NEPTUNE_FAIL_ON_ERROR: As per loader documentation (default="False")
* LOG_LEVEL: A valid string representation of a python *logging.loglevel* (default="info")

Refer to *app_config.py* to see how this works in more detail.

## Running debug scripts
We include some convience functions and tools that can be used to control and/or troubleshoot the system. This lets you mimic the behaviour of the Lambda function locally allowing you to use debuggers.

pipeline_control ships with a set of control scripts found under *src/lambda_emuation* these are not required for the production use in lambda but are handy to run controlled experiments from the command line. See the README.md in that directory for more information

Like the production deployment all of these scripts take their configuration from the AWS Systems Manager parameter store and fall back on locally configured environment variables.

### A note about Neptune
Some modules of this package interact with the API of an Amazon Neptune cluster. In order to run the scripts you will need to ensure TLS connectivity to that endpoint. There are two ways to achieve this 1) Run this from within a VPC that has access to the endpoint or 2) Use port forwarding via the bastion host. If using the bastion host this can be achieved using 
```ssh ec2-user@ec2-[BASTION_IP].compute.amazonaws.com -L 8182:neptune.cluster-[NEPTUNE_CLUSTER_NAME]:8182```

## scheduler

This script emulates a jobspec being uploaded to an S3 bucket. 

It will create a new job, schedule it to Kubernetes and record meta-data information.

Configuration is done within the code by updating the "S3 Event" to point at the jobspec file you want to process.

```poetry run python -m pipeline_control.lambda_emuation.scheduler```

## process_inference

The script emulates a rdfox.log performance log being uploaded to the S3. It will parse the log to derive performance metrics then attempt to initiate a bulk load against the Amazon Neptune's cluster.

Configuration is done within the code by updating the "S3 Event" to point at the jobspec file you want to process.

```poetry run python -m pipeline_control.lambda_emuation.process_inference```

## refresh_bulkload

The script emulates a time based event. It will search the state table for LOADING jobs and update their status from the loader API.

It will then search for complete jobs and send notifications.

```poetry run python -m pipeline_control.lambda_emuation.refresh_bulkload```

# Run Tests
To ensure the code will function execute *pytest* and ensure all tests are passing. It is recommended only to run the *offline* tests (see source tree) initially
```poetry run pytest tests/offline```

If all tests pass you will be ready to run control scripts

*Note:* The code was built using the Test Driven Development (TDD) methodology which means the test suite also serves as documentation for how the code works. Feel free to explore it at your leisure.

# 🏗️ Build

To build lambda deployment package we use *make*. What our Makefile does is: use poetry to generate a requirements.txt and use pip to install the dependencies into a temp dir and adds it to the root of a zip. Then it copies both the pipeline_control and the handlers to the root. The output is stored in *dist/pipeline_control.zip* it is this archive you can use to deploy to AWS Lambda

While the Makefile has many macros the only one you need to build the Lambda archive is

```make bundle.cloud```

## 📝 License

Amazon Software License 1.0

This Amazon Software License ("License") governs your use, reproduction, and
distribution of the accompanying software as specified.

