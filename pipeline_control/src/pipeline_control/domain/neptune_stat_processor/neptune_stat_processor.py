# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from dataclasses import dataclass
from datetime import datetime


@dataclass
class NeptuneStats:
    start_time: datetime = 0
    total_records: int = 0
    total_duplicates: int = 0
    time_to_load: int = 0
    time_total: int = 0
    records_total: int = 0
    errors_parsing: int = 0
    errors_mismatch: int = 0
    errors_insert: int = 0
    status: str = "TBC"

    def __eq__(self, other):
        if not type(other) is type(self):
            return False
        if self.__dict__.items() == other.__dict__items():
            return True

    @property
    def json(self):
        return self.__dict__

    @property
    def errors_total(self):
        return self.errors_insert + self.errors_parsing + self.errors_insert


STAT_MAP = {
    "start_time": "startTime",
    "total_records": "totalRecords",
    "total_duplicates": "totalDuplicates",
    "time_total": "totalTimeSpent",
    "records_total": "totalRecords",
    "errors_parsing": "parsingErrors",
    "errors_mismatch": "datatypeMismatchErrors",
    "errors_insert": "insertErrors",
    "status": "status",
}


@dataclass
class NeptuneStatProcessor:
    def process(self, stat_dict) -> NeptuneStats:
        result_dict = {}
        overall_status = stat_dict["payload"]["overallStatus"]
        for target_key, source_key in STAT_MAP.items():
            result_dict[target_key] = overall_status[source_key]
        # TODO: see method for details
        self.adjust_failed_status_for_rdfox_log(
            result_dict=result_dict, stat_dict=stat_dict
        )
        return NeptuneStats(**result_dict)

    # TODO: Ideally we just don't even scan rdfox.log but right now we do and this causes overall failure
    def adjust_failed_status_for_rdfox_log(
        self,
        result_dict,
        stat_dict,
    ):
        # If overall failed but only failed feed is rdfox log we're good
        pass
        # payload = stat_dict["payload"]
        # overall_status = payload["overallStatus"]
        # if overall_status["status"] == "LOAD_FAILED":
        #    failed_feeds = payload["failedFeeds"]
        #    if len(failed_feeds) == 1:
        #        fullUri = failed_feeds[0]["fullUri"]
        #        failed_file = fullUri.split("/")[-1]
        #        if failed_file == "rdfox.log":
        #            result_dict["status"] = "LOAD_COMPLETE"
