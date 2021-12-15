# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import inspect
import logging
from datetime import datetime
from typing import List, Tuple

import pynamodb

import app_config
from pipeline_control.adapters.job_repository.ddb_model import DDBJob
from pipeline_control.adapters.kubernetes_objects.rdfox_job import RDFoxJobConfiguration
from pipeline_control.domain.inference_stat_processor.inference_stat_processor import (
    InferenceStats,
)
from pipeline_control.domain.model import Job, JobStatus
from pipeline_control.domain.neptune_stat_processor.neptune_stat_processor import (
    NeptuneStats,
)

logger = logging.getLogger(__name__)

JOB_ID_DELIMITER = app_config.app_configuration.job_id_delimeter
RUN_ID_LENGTH = 3


def default_mapper(obj, key, value):
    return {key: value}


def job_id_for_model(obj, key, job_id):
    sk = JOB_ID_DELIMITER.join(obj.job_id.split(JOB_ID_DELIMITER)[1:])
    element = {key: job_id, "pk": obj.key, "sk": sk}
    return element


def job_configuration_from_model(obj, key, value: RDFoxJobConfiguration):
    return {key: value.json}


def job_configuration_to_model(obj, key, value):
    return {key: RDFoxJobConfiguration.from_dict(value)}


def now_if_not_then(obj, key, point_in_time):
    new_date = point_in_time
    if not point_in_time:
        new_date = datetime.now()
    return {key: new_date}


def set_created_if_not_created(obj, key, status):
    new_status = status
    if status == JobStatus.PRE_CREATE:
        new_status = JobStatus.CREATED
    return {key: repr(new_status)}


def todays_date(obj, key, status):
    today = datetime.now()
    today_date = today
    element = {key: today_date}
    return element


MAPPERS = {
    "job_configuration": {
        "to_domain_model": job_configuration_to_model,
        "to_ddb_model": job_configuration_from_model,
    },
    "key": {
        "to_domain_model": default_mapper,
        "to_ddb_model": default_mapper,
    },
    "time_to_load_neptune": {
        "to_domain_model": default_mapper,
        "to_ddb_model": default_mapper,
    },
    "job_status": {
        "to_domain_model": lambda obj, key, value: {key: JobStatus[value]},
        "to_ddb_model": set_created_if_not_created,
    },
    "job_created": {
        "to_domain_model": default_mapper,
        "to_ddb_model": now_if_not_then,
    },
    "job_updated": {
        "to_domain_model": default_mapper,
        "to_ddb_model": todays_date,
    },
    "kubernetes_name": {
        "to_domain_model": default_mapper,
        "to_ddb_model": default_mapper,
    },
    "kubernetes_worker_type": {
        "to_domain_model": default_mapper,
        "to_ddb_model": default_mapper,
    },
    "neptune_load_id": {
        "to_domain_model": default_mapper,
        "to_ddb_model": default_mapper,
    },
    "neptune_statistics_raw": {
        "to_domain_model": default_mapper,
        "to_ddb_model": default_mapper,
    },
    "neptune_statistics": {
        "to_domain_model": lambda obj, key, value: {key: NeptuneStats(**value)},
        "to_ddb_model": lambda obj, key, value: {key: value.json},
    },
    "rdfox_statistics": {
        "to_domain_model": lambda obj, key, value: {
            key: InferenceStats.from_static_properties(value)
        },
        "to_ddb_model": lambda obj, key, value: {key: value.json},
    },
    "rdfox_statistics_raw": {
        "to_domain_model": default_mapper,
        "to_ddb_model": default_mapper,
    },
    "job_id": {
        "to_domain_model": default_mapper,
        "to_ddb_model": job_id_for_model,
    },
    "neptune_writer_instance": {
        "to_domain_model": default_mapper,
        "to_ddb_model": default_mapper,
    },
}


class JobRepository:
    def get_job_by_id(self, job_id):
        return self.map_ddb_model_to_domain(self._lookup_job_by_id(job_id))

    def get_all(self) -> List[Job]:
        jobs = list(DDBJob.scan())
        jobs_as_objects = [self.map_ddb_model_to_domain(job) for job in jobs]
        return jobs_as_objects

    def get_all_by_status(self, job_status: JobStatus):
        jobs = list(DDBJob.job_status_index.query(repr(job_status)))
        jobs_as_objects = [self.map_ddb_model_to_domain(job) for job in jobs]
        return jobs_as_objects

    def _lookup_job_by_id(self, job_id):
        key, date, run = job_id.split(JOB_ID_DELIMITER)
        try:
            job = DDBJob.get(key, f"{date}{JOB_ID_DELIMITER}{run}")
            return job
        except Exception as e:
            logger.critical(e)
            raise JobNotFoundError(job_id)

    def create_table_if_not_exists(self):
        if not DDBJob.exists():
            DDBJob.create_table(
                read_capacity_units=1, write_capacity_units=1, wait=True
            )

    def delete_table(self):
        if DDBJob.exists():
            DDBJob.delete_table()

    def save(self, job: Job):
        if job.job_status == JobStatus.PRE_CREATE:
            job.job_id = self.get_new_job_id(job)
        ddbjob_model = self.map_domain_model_to_ddb(job)

        if job.job_status == JobStatus.PRE_CREATE:
            pass
        else:
            self.sync_changes_to_ddb(ddbjob_desired_state=ddbjob_model)

        ddbjob_model.save()

        self.sync_domain_from_ddb(job, ddbjob_model)
        return

    def sync_changes_to_ddb(self, ddbjob_desired_state: DDBJob):
        ddbjob_current_state = self._lookup_job_by_id(ddbjob_desired_state.job_id)
        update_actions = self.derive_required_updates(
            from_state=ddbjob_current_state, to_state=ddbjob_desired_state
        )
        if len(update_actions) > 0:
            ddbjob_current_state.update(actions=update_actions)

    def derive_required_updates(self, from_state: DDBJob, to_state: DDBJob):
        update_actions = []
        domain_attributes = inspect.getmembers(to_state)
        relevant_keys = MAPPERS.keys()
        for key, new_value in domain_attributes:
            from_state_value = getattr(from_state, key)
            if key in relevant_keys:
                if from_state_value != new_value:
                    update_actions.append(getattr(DDBJob, key).set(new_value))
        return update_actions

    def sync_domain_from_ddb(self, domain: Job, ddbjob: DDBJob):
        domain_state_based_on_ddb = self.map_ddb_model_to_domain(ddbjob)
        domain.__dict__.update(domain_state_based_on_ddb.__dict__)

    def get_new_job_id(self, job: Job) -> str:
        base = f"{job.key}{JOB_ID_DELIMITER}{datetime.now().date()}"
        run = self._get_next_run_id(job.key)
        return f"{base}{JOB_ID_DELIMITER}{run}"

    def _get_next_run_id(self, pk: str) -> str:
        existing_runs_for_day = DDBJob.query(
            hash_key=pk,
            range_key_condition=DDBJob.sk.startswith(str(datetime.now().date())),
        )
        number_of_previous_runs = len(list(existing_runs_for_day))

        return self._integer_to_run_id(number_of_previous_runs)

    def _integer_to_run_id(self, number: int) -> str:
        run_id = str(number)
        while len(run_id) < RUN_ID_LENGTH:
            run_id = f"0{run_id}"
        return run_id

    def map_domain_model_to_ddb(self, domain_model) -> DDBJob:
        spec = self.map_domain_ddb(source=domain_model, direction="to_ddb_model")
        return DDBJob(**spec)

    def map_ddb_model_to_domain(self, ddb_model) -> DDBJob:
        spec = self.map_domain_ddb(source=ddb_model, direction="to_domain_model")
        return Job(**spec)

    def map_domain_ddb(self, source, direction: str) -> dict:
        domain_attributes = inspect.getmembers(source)
        ddb_dict = {}
        for key, value in domain_attributes:
            if key in MAPPERS:
                mapping_functions = MAPPERS[key]
                mapping_function = mapping_functions[direction]
                if mapping_function:
                    element = mapping_function(source, key, value)
                    try:
                        ddb_dict.update(element)
                    except Exception as e:
                        logger.critical(e)
        return ddb_dict

    def __eq__(self, other):
        return type(self) == type(other)

    def _extract_ddb_attributes(var: Tuple[any]):
        return issubclass(var[1], pynamodb.attributes.Attribute)


class JobNotFoundError(Exception):
    def __init__(self, job_id):
        super().__init__(f"The job with id {job_id} could not be found")
