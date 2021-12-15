# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0


FROM amazonlinux:2 AS builder
RUN yum update -y && yum install -y initscripts;
ARG ARG_BUCKET_NAME
ARG ARG_DATA_PATH
ARG ARG_NUM_OF_MSG
ARG ARG_NUM_OF_FILES
ARG ARG_NUM_OF_PARTIES
ARG ARG_MAX_DAYS_BEFORE
ARG ARG_CHAIN_DAYS_RANGE
ARG ARG_THREAD_COUNT
ENV BUCKET_NAME=$ARG_BUCKET_NAME
ENV DATA_PATH=$ARG_DATA_PATH
ENV NUM_OF_MSG=$ARG_NUM_OF_MSG
ENV NUM_OF_FILES=$ARG_NUM_OF_FILES
ENV NUM_OF_PARTIES=$ARG_NUM_OF_PARTIES
ENV MAX_DAYS_BEFORE=$ARG_MAX_DAYS_BEFORE
ENV CHAIN_DAYS_RANGE=$ARG_CHAIN_DAYS_RANGE
ENV THREAD_COUNT=$ARG_THREAD_COUNT
RUN yum update -y && yum install -y python3 python3-pip awscli
FROM builder
COPY transactions_generator transactions_generator
WORKDIR /transactions_generator
RUN pip3 install -r requirements.txt
WORKDIR /
COPY start.sh start.sh
RUN chmod +x start.sh
CMD ["sh", "/start.sh"]