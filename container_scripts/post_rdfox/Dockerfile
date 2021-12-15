# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0


FROM amazonlinux:2
RUN yum update -y && yum install -y initscripts;
RUN yum install -y awscli
RUN useradd -u 1211 rdfox
COPY start.sh start.sh
RUN chmod +xr start.sh
USER rdfox
ARG ARG_BUCKET_NAME
ARG ARG_DATA_PATH
ARG ARG_JOB_ID
ENV BUCKET_NAME=$ARG_BUCKET_NAME
ENV DATA_PATH=$ARG_DATA_PATH
ENV AUTO_SHUTDOWN=$ARG_AUTO_SHUTDOWN
ENV JOB_ID=$ARG_JOB_ID
WORKDIR /
CMD ["bash", "/start.sh"]