# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import datetime
from enum import Enum

from pipeline_control.adapters.kubernetes_objects.rdfox_job import RDFoxJobConfiguration
from pipeline_control.domain.inference_stat_processor.inference_stat_processor import (
    InferenceStats,
)
from pipeline_control.domain.neptune_stat_processor.neptune_stat_processor import (
    NeptuneStats,
)


class JobStatus(Enum):
    PRE_CREATE = "PRE_CREATE"
    CREATED = "CREATED"
    SCHEDULED = "SCHEDULED"
    INFERENCE_COMPLETE = "INFERENCE_COMPLETE"
    SCHEDULE_FAILED = "SCHEDULE_FAILED"
    INFERENCE_FAILED = "INFERENCE_FAILED"
    NEPTUNE_LOAD_NOT_STARTED = "NEPTUNE_LOAD_NOT_STARTED"
    NEPTUNE_LOAD_IN_PROGRESS = "NEPTUNE_LOAD_IN_PROGRESS"
    NEPTUNE_LOAD_COMPLETED = "NEPTUNE_LOAD_COMPLETED"
    NEPTUNE_LOAD_CANCELLED_BY_USER = "NEPTUNE_LOAD_CANCELLED_BY_USER"
    NEPTUNE_LOAD_CANCELLED_DUE_TO_ERRORS = "NEPTUNE_LOAD_CANCELLED_DUE_TO_ERRORS"
    NEPTUNE_LOAD_UNEXPECTED_ERROR = "NEPTUNE_LOAD_UNEXPECTED_ERROR"
    NEPTUNE_LOAD_FAILED = "NEPTUNE_LOAD_FAILED"
    NEPTUNE_LOAD_S3_READ_ERROR = "NEPTUNE_LOAD_S3_READ_ERROR"
    NEPTUNE_LOAD_S3_ACCESS_DENIED_ERROR = "NEPTUNE_LOAD_S3_ACCESS_DENIED_ERROR"
    NEPTUNE_LOAD_COMMITTED_W_WRITE_CONFLICTS = (
        "NEPTUNE_LOAD_COMMITTED_W_WRITE_CONFLICTS"
    )
    NEPTUNE_LOAD_DATA_DEADLOCK = "NEPTUNE_LOAD_DATA_DEADLOCK"
    NEPTUNE_LOAD_DATA_FAILED_DUE_TO_FEED_MODIFIED_OR_DELETED = (
        "NEPTUNE_LOAD_DATA_FAILED_DUE_TO_FEED_MODIFIED_OR_DELETED"
    )
    NEPTUNE_LOAD_FAILED_BECAUSE_DEPENDENCY_NOT_SATISFIED = (
        "NEPTUNE_LOAD_FAILED_BECAUSE_DEPENDENCY_NOT_SATISFIED"
    )
    NEPTUNE_LOAD_IN_QUEUE = "NEPTUNE_LOAD_IN_QUEUE"
    NEPTUNE_LOAD_FAILED_INVALID_REQUEST = "NEPTUNE_LOAD_FAILED_INVALID_REQUEST"
    SUCCESS_NOTIFICATION_SENT = "SUCCESS_NOTIFICATION_SENT"
    ERROR_NOTIFICATION_SENT = "ERROR_NOTIFICATION_SENT"

    def __repr__(self):
        return self.name


class Job:
    def __init__(
        self,
        key: str,
        job_id: str = None,
        job_configuration: RDFoxJobConfiguration = RDFoxJobConfiguration(),
        time_to_load_neptune: int = 0,
        neptune_load_id: str = "N/A",
        job_created: datetime.datetime = None,
        job_updated: datetime.datetime = None,
        job_status: JobStatus = JobStatus.PRE_CREATE,
        neptune_statistics_raw={},
        neptune_statistics=NeptuneStats(),
        rdfox_statistics_raw="N/A",
        rdfox_statistics: InferenceStats = InferenceStats(),
        kubernetes_name: str = "N/A",
        kubernetes_worker_type: str = "N/A",
        neptune_writer_instance: str = "N/A",
    ):
        if not job_status:
            job_status = JobStatus.PRE_CREATE

        self._job_status = job_status
        self.key = key
        self.job_configuration = job_configuration
        self.rdfox_statistics = rdfox_statistics
        self.rdfox_statistics_raw = rdfox_statistics_raw
        self.job_created = job_created
        self.job_updated = job_updated
        self._job_id = job_id
        self._is_dirty = False
        self.kubernetes_name = kubernetes_name
        self.neptune_load_id = neptune_load_id
        self.neptune_statistics_raw = neptune_statistics_raw
        self.neptune_statistics = neptune_statistics
        self.neptune_writer_instance = neptune_writer_instance
        self.kubernetes_worker_type = kubernetes_worker_type

    @property
    def is_dirty(self):
        return self._is_dirty

    def mark_clean(self):
        self._is_dirty = False

    def _markdirty(self):
        self._is_dirty = True

    @is_dirty.setter
    def is_dirty(self, value: bool):
        self._is_dirty = value

    @property
    def job_id(self):
        if not self._job_id:
            raise Exception("Job id is available once Job is persisted")
        return self._job_id

    @job_id.setter
    def job_id(self, job_id):
        if self._job_id:
            raise Exception("Job ID is immutable once set")
        self._job_id = job_id
        self._markdirty()

    @property
    def job_status(self):
        return self._job_status

    @job_status.setter
    def job_status(self, status: JobStatus):
        if not type(status) == JobStatus:
            raise Exception(f"Not a valid JobStatus {type(status)}")
        self._job_status = status
        self._markdirty()
