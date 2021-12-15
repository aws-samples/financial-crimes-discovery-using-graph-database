# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import pytest
from freezegun import freeze_time
from pyexpect import expect

from pipeline_control.domain.inference_stat_processor.inference_stat_processor import (
    InferenceStatProcessor,
    InferenceStats,
)
from pipeline_control.domain.model import Job, JobStatus


@freeze_time(pytest.TEST_FROZE_DATE)
class TestProcessInferenceHandler:
    def verify_parsed_stats(self, stats: InferenceStats):
        expect(stats.time_to_infer).to.equal(1621)
        expect(stats.time_to_load).to.equal(254)
        expect(stats.time_query).to.equal(4355)
        expect(stats.time_total).to.equal(1875)

        expect(stats.triples_avg_size).to.equal(101.891)
        expect(stats.triples_materialised_amount).to.equal(276914566)
        expect(stats.triples_materialised_rate).to.almost_equal(
            170829.467, max_delta=0.01
        )

        expect(stats.triples_input_amount).to.equal(510506725)
        expect(stats.triples_input_rate).to.almost_equal(2009868.996, max_delta=0.01)

        expect(stats.memory_usage).to.almost_equal(80231142761, max_delta=1)
        expect(stats.memory_usage_gigabytes).to.almost_equal(
            80.231142761, max_delta=0.1
        )
        expect(stats.partial_chains_amount).to.equal(1337)
        expect(stats.full_chains_amount).to.equal(2667)

    def verify_fake_stats(self, stats):
        expect(stats.time_to_infer).to.equal(0)
        expect(stats.time_to_load).to.equal(0)
        expect(stats.time_query).to.equal(0)
        expect(stats.time_total).to.equal(0)

    def test_1_parsing_inference_stats(
        self,
        g_inference_stats,
    ):
        inference_stats_string = g_inference_stats.decode("utf-8")
        inference_stat_processor = InferenceStatProcessor(inference_stats_string)
        stats = inference_stat_processor.process_inference()
        self.verify_parsed_stats(stats)
        self.verify_parsed_stats(InferenceStats.from_static_properties(stats.json))

    def test_2_handle_upload_happy_pathend_to_end(
        self,
        post_inference_handler_under_test,
        mocked_repository,
        g_post_inference_scheduled_test_job,
        g_inference_stats,
    ):
        post_inference_handler_under_test.handle()
        queried_job: Job = mocked_repository.get_job_by_id(
            g_post_inference_scheduled_test_job.job_id
        )
        expect(queried_job.job_status).to.equal(JobStatus.INFERENCE_COMPLETE)
        expect(queried_job.rdfox_statistics_raw).to.equal(
            g_inference_stats.decode("utf-8")
        )
        self.verify_fake_stats(queried_job.rdfox_statistics)
