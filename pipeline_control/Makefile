# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

SHELL := /bin/bash
PY_VERSION := 3.7
export PYTHONUNBUFFERED := 1

BASE := $(shell /bin/pwd)
DIR := $(shell basename $(BASE))
POETRY := poetry

VENV_DIR := /tmp/tvenvdir
export PATH := var:$(PATH):$(VENV_DIR)/bin

PYTHON := $(shell /usr/bin/which python$(PY_VERSION))
ZIP_FILE := $(BASE)/dist/pipeline_control.zip
EXCLUSIONS_PY := -x appdirs.py -x autopep8.py -x _black_version.py -x mypy_extensions.py -x pycodestyle.py -x pyparsing.py -x six.py -x typing_extensions.py -x zipp.py -x google_auth-1.33.0-py3.9-nspkg.pth -x _ruamel_yaml.cpython-37m-x86_64-linux-gnu.so -x ruamel.yaml-0.17.10-py3.9-nspkg.pth -x distutils-precedence.pth
EXCLUSIONS := $(EXCLUSIONS_PY) -x moto/\*  -x pip/\* -x setup/\* -x __pycache__/\* -x __pycache__ -x black/\*  -x awscli/examples/\* -x \*.pyc
EXCLUSIONS_CLOUD := -x boto3/\* -x botocore/\*
LMABDA_HANDLER_DIR := "$(BASE)/src/pipeline_control/entrypoints"
LAMBDA_HANDLER := "lambda_entry_points.py"
TEST_ARGS := -o log_cli=true --log-cli-level=WARN --cov=pipeline_control --cov-report term-missing
UNIT_TEST_TARGETS := src tests/offline
LIVE_TEST_TARGETS := src tests/live_e2e
.DEFAULT_GOAL := build
.PHONY: build clean release describe deploy package bundle bundle.local
PIPELINE_FUNCTIONS := scheduler process_inference refresh_bulkload

test:
	$(POETRY) run pytest $(UNIT_TEST_TARGETS) $(TEST_ARGS)

test_continuous:
	$(POETRY) run pytest-watch $(UNIT_TEST_TARGETS) -- $(TEST_ARGS)

test_live:
	$(POETRY) run pytest $(LIVE_TEST_TARGETS) $(TEST_ARGS)

download_dependencies: pyproject.toml
	$(POETRY) export --without-hashes -f requirements.txt > requirements.txt
	$(POETRY) run python -m pip install -r requirements.txt --upgrade --platform=manylinux1_x86_64 --python-version=37 --only-binary=:all: --target=$(VENV_DIR)

bundle_dependencies: download_dependencies $(VENV_DIR)
	cd "$(VENV_DIR)" \
		&& zip -r -9 "$(ZIP_FILE)" . $(EXCLUSIONS) >> /dev/null

bundle_dependencies.cloud: download_dependencies
	cd "$(VENV_DIR)" \
		&& zip -r -9 "$(ZIP_FILE)" . $(EXCLUSIONS_CLOUD) >> /dev/null

bundle_lambda_handler: bundle_app bundle_app_config
	cd $(LMABDA_HANDLER_DIR) \
	&& zip -r -9 "$(ZIP_FILE)" $(LAMBDA_HANDLER)

bundle_app: format lint quality_checks src
	cd src \
	&& zip -r -9 $(ZIP_FILE) pipeline_control $(EXCLUSIONS)

bundle_lambda: bundle_app bundle_lambda_handler

bundle_app_config:
	zip -r -9 $(ZIP_FILE) app_config.py

bundle.cloud: bundle_lambda bundle_dependencies.cloud

publish.cloud: bundle.cloud
	aws s3 cp dist/pipeline_control.zip s3://$(LAMBDA_BUCKET)

deploy.cloud: publish.cloud
	$(foreach var,$(PIPELINE_FUNCTIONS), aws lambda update-function-code --function-name $(var) --s3-bucket $(LAMBDA_BUCKET) --s3-key pipeline_control.zip > /dev/null ;)

quality_checks:

ifndef SKIP_QUALITY_CHECKS
quality_checks: lint offline_tests security_scan
endif

lint: format
	$(POETRY) run flake8 src --max-line-length 88 --ignore=E501

format:
	$(POETRY) run isort .
	$(POETRY) run black .
	$(POETRY) run autoflake -r --in-place --remove-unused-variables .
	

security_scan:
	$(POETRY) run bandit -r src/ -n 3

offline_tests:
	$(POETRY) run pytest tests/offline

release: publish.cloud

clean:
	rm -rf "$(VENV_DIR)" "$(BASE)/var" "$(BASE)/__pycache__" "$(ZIP_FILE)"