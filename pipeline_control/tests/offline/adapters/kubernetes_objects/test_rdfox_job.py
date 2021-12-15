# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import logging
from typing import List
from unittest.mock import patch

import hikaru
import pytest
from hikaru.model.rel_1_18 import *
from hikaru.model.rel_1_18.v1.v1 import EnvVar
from pyexpect import expect

logger = logging.getLogger("test_job")
logger.setLevel(logging.WARN)


def make_compare_to(this):
    def closure(that):
        if str(this) == that:
            return True
        else:
            logger.warn(f"{this} is NOT {that}")
            return False

    return closure


def make_is_type(target_type):
    def closure(that):
        if that is target_type:
            return True
        else:
            logger.warn(f"{that} is NOT TYPE {target_type}")

    return closure


class TestRDFoxJob:
    def _check_args_are_strings(self, args: List[str]):
        for arg in args:
            expect(arg).contains("'")

    @pytest.fixture
    def baseline_envs(self):
        return {
            "BUCKET_NAME": make_compare_to(pytest.TEST_BUCKET_NAME),
            "DATA_PATH": make_compare_to(pytest.TEST_KEY),
            "NUMBER_OF_CORES": make_compare_to(pytest.TEST_NUMBER_OF_CORES),
            "AUTO_SHUTDOWN": make_compare_to(str(pytest.TEST_AUTO_SHUTDOWN)),
            "JOB_ID": make_compare_to(pytest.TEST_JOB_ID),
        }

    def _check_has_env(self, container_under_test, expected_envs_extra, baseline_envs):
        baseline_envs.update(expected_envs_extra)
        expected_envs = baseline_envs
        envs_under_test = container_under_test.env
        expected_envs_items = expected_envs.items()
        expect(len(expected_envs_items)).equals(len(expected_envs))
        envs_under_test_tuples = [
            (env.name, env.value) if (not env.value == None) else (env.name, type(env))
            for env in envs_under_test
        ]
        envs_under_test_dict = dict(envs_under_test_tuples)
        for key, validator in expected_envs_items:
            expect(envs_under_test_dict[key]).exists()
            value = envs_under_test_dict[key]
            expect(validator(value)).equals(True)

    def test_1_make_temp_volume(self, rdfox_job_under_test):
        test_name = "test"
        test_volume = rdfox_job_under_test._make_temp_volume(test_name)
        expect(test_volume.name).to.equal(test_name)

    def test_2_1_make_rdfox_init_container(
        self, rdfox_job_under_test, rdfox_init_container_under_test, baseline_envs
    ):
        # logger.info(hikaru.get_yaml(rdfox_init_container_under_test))
        expect(len(rdfox_init_container_under_test.volumeMounts)).to.equal(4)
        expect(rdfox_init_container_under_test.image).to.be.equal(
            rdfox_job_under_test.job_configuration.rdfox_init_container_image
        )
        self._check_has_env(
            container_under_test=rdfox_init_container_under_test,
            expected_envs_extra={
                "JOB_ID": make_compare_to(pytest.TEST_JOB_ID),
                "RDFOX_ROLE": make_compare_to("ADMIN"),
                "RDFOX_PASSWORD": make_is_type(EnvVar),
            },
            baseline_envs=baseline_envs,
        )

    def test_2_make_rdfox_container(
        self, rdfox_job_under_test, rdfox_container_under_test, baseline_envs
    ):
        # logger.info(hikaru.get_yaml(rdfox_container_under_test))
        expect(len(rdfox_container_under_test.volumeMounts)).to.equal(4)
        expect(rdfox_container_under_test.image).to.be.equal(
            rdfox_job_under_test.job_configuration.rdfox_container_image
        )
        self._check_has_env(
            container_under_test=rdfox_container_under_test,
            expected_envs_extra={
                "JOB_ID": make_compare_to(pytest.TEST_JOB_ID),
                "RDFOX_ROLE": make_compare_to("ADMIN"),
                "RDFOX_PASSWORD": make_is_type(EnvVar),
                "AUTO_SHUTDOWN": make_compare_to(
                    rdfox_job_under_test.job_configuration.auto_shutdown
                ),
            },
            baseline_envs=baseline_envs,
        )

    def test_3_make_init_container(
        self, rdfox_job_under_test, init_container_under_test, baseline_envs
    ):
        # logger.info(hikaru.get_yaml(init_container_under_test))
        expect(len(init_container_under_test.volumeMounts)).to.equal(2)
        expect(init_container_under_test.image).to.be.equal(
            rdfox_job_under_test.job_configuration.init_container_image
        )

        self._check_has_env(
            container_under_test=init_container_under_test,
            expected_envs_extra={},
            baseline_envs=baseline_envs,
        )

    def test_4_make_publisher_container(
        self, rdfox_job_under_test, publisher_container_under_test, baseline_envs
    ):
        expect(len(publisher_container_under_test.volumeMounts)).to.equal(2)
        expect(publisher_container_under_test.image).to.be.equal(
            rdfox_job_under_test.job_configuration.publisher_container_image
        )
        self._check_has_env(
            container_under_test=publisher_container_under_test,
            expected_envs_extra={
                "BUCKET_NAME": make_compare_to(pytest.TEST_RESULT_BUCKET),
                "DATA_PATH": make_compare_to(pytest.TEST_KEY),
            },
            baseline_envs=baseline_envs,
        )
        # logger.info(hikaru.get_yaml(publisher_container_under_test))

    def test_5_make_job_pod_spec(self, job_pod_spec_under_test):
        expect(len(job_pod_spec_under_test.containers)).to.be.equal(2)
        expect(len(job_pod_spec_under_test.initContainers)).to.be.equal(2)
        expect(len(job_pod_spec_under_test.volumes)).to.be.equal(5)
        expect(job_pod_spec_under_test.restartPolicy).to.equal("Never")
        # expect(job_pod_spec_under_test.metadata.)
        # logger.info(hikaru.get_yaml(job_pod_spec_under_test))

    def test_6_make_job_pod_template_spec(
        self, job_pod_template_spec_under_test, job_pod_spec_under_test
    ):
        expect(job_pod_template_spec_under_test.spec).to.equal(job_pod_spec_under_test)

    def test_7_make_job_spec(
        self,
        rdfox_job_under_test,
        job_spec_under_test,
        job_pod_template_spec_under_test,
    ):
        expect(job_spec_under_test.parallelism).to.equal(
            rdfox_job_under_test.job_configuration.parallelism
        )

        expect(job_spec_under_test.template).to.equal(job_pod_template_spec_under_test)
        # logger.info(hikaru.get_yaml(job_spec_under_test))

    def test_8_make_job(self, rdfox_job_under_test, job_under_test):
        expect(job_under_test.metadata.generateName).to.equal("rdfox")

    @patch("hikaru.model.rel_1_18.v1.v1.Job.create", autospec=True)
    def test_9_deploy(
        self,
        hikaru_patch,
        rdfox_job_under_test,
        job_under_test,
    ):
        test_name = "glumanda"
        dummyJob = hikaru.model.rel_1_18.v1.v1.Job()
        dummyMeta = hikaru.model.rel_1_18.v1.v1.ObjectMeta()
        dummyMeta.name = test_name
        dummyJob.metadata = dummyMeta

        dummyJob.merge(job_under_test, overwrite=False)

        hikaru_patch.return_value = dummyJob

        rdfox_job_under_test.deploy()

        hikaru_patch.assert_called_with(
            job_under_test, namespace=rdfox_job_under_test.namespace
        )

        kubernetes_object = rdfox_job_under_test.kubernetes_object

        expect(kubernetes_object).to.exist()
        expect(type(kubernetes_object)).to.equal(hikaru.model.rel_1_18.v1.v1.Job)
        expect(kubernetes_object.metadata.name).to.be(test_name)
