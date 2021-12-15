# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import re
from dataclasses import dataclass
from datetime import datetime

""" This is what it looks like in the log
.............
INFERENCETIME-13-Jul-2021 10:28:28|13-Jul-2021 10:28:40
LOADTIME-13-Jul-2021 10:28:26|13-Jul-2021 10:28:28
TOTALTIME-13-Jul-2021 10:28:26|13-Jul-2021 10:28:40
QUERYTIME-13-Jul-2021 10:28:26|13-Jul-2021 10:28:40
.............
"""
TIMESTAMP_IDENTIFIER_REGEX = "[A-Z]+TIME"
# e.g. 13-Jul-2021
DATE_REGEX = "[0-9]{2}-[A-Z][a-z]{2}-[0-9]{4}"
# e.g. 01:01:01
TIME_REGEX = "[0-9]{2}:[0-9]{2}:[0-9]{2}"

"""This is what it looks like in the log
---info---


  ::RDFStore
---------------------------------------------------------------------
    Name                           :  transactions
    ID                             :               0     (  0    )
    Unique ID                      :  18225196492841182561
    Data store version             :               2     (  2    )
    End resource ID                :   4,294,967,295     (  4.2 G)
    Concurrent                     :  yes
    Persistent                     :  no
    Equality axiomatization mode   :  off
    Requires incremental reasoning :  yes
    Aggregate size                 :  80,273,916,922     ( 80.2 G)
    Aggregate number of entries    :     787,840,001     (787.8 M)
    Bytes per entry                :             101.891
    Aggregate number of EDB facts  :     510,506,725     (510.5 M)
    Aggregate number of IDB facts  :     787,421,291     (787.4 M)
    Dictionary size (%)            :              48.354
    Equality manager size (%)      :               0     (  0    )
    Rule index size (%)            :               0     (  0    )
    Facts size (%)                 :              51.645
---endinfo---
"""
RDFOX_TSTAMP_REGEX = f"{DATE_REGEX} {TIME_REGEX}"
TIMESTAMP_REGEX_STRING = fr"^(?P<identifier>{TIMESTAMP_IDENTIFIER_REGEX})-(?P<start_time>{RDFOX_TSTAMP_REGEX})\|(?P<end_time>{RDFOX_TSTAMP_REGEX})$"
TIMESTAMP_REGEX = re.compile(TIMESTAMP_REGEX_STRING, re.MULTILINE)

BYTES_PER_ENTRY_REGEX_STRING = r"Bytes per entry[^:]*:\s*(?P<value>[0-9,.]+)"
BYTES_PER_ENTRY_REGEX = re.compile(BYTES_PER_ENTRY_REGEX_STRING)
AGGREGATE_NUMBER_OF_REGEX_STRING = (
    r"Aggregate number of (?P<key>[a-zA-Z]*)[^:]*:\s*(?P<value>[0-9,.]+)"
)
AGGREGATE_NUMBER_OF_REGEX = re.compile(AGGREGATE_NUMBER_OF_REGEX_STRING)

# e.g. 13-Jul-2021 10:28:28
RDFOX_TSTAMP_FORMAT = "%d-%b-%Y %H:%M:%S"

"""This is what it looks like in the logs
running-counts
output = "out"
query.answer-format = "text/csv"
partialChainCount
1337
Number of returned tuples:   1
Total number of answers:     1
Total statement evaluation time: 0.001 s
2nd-query
fullChainCount
2667
Number of returned tuples:   1
Total number of answers:     1
Total statement evaluation time: 0 s
end-running-counts
"""
CHAIN_AMOUNT_REGEX = re.compile(
    "(?P<chainType>(?:partial|full)ChainCount)\n(?P<count>[0-9]+)"
)

CHAIN_MAP = {
    "partialChainCount": "partial_chains_amount",
    "fullChainCount": "full_chains_amount",
}

STAT_MAP = {
    "INFERENCETIME": "time_to_infer",
    "LOADTIME": "time_to_load",
    "TOTALTIME": "time_total",
    "QUERYTIME": "time_query",
}


@dataclass
class InferenceStats:
    time_to_infer: int = 0
    time_to_load: int = 0
    time_total: int = 0
    time_query: int = 0
    triples_input_amount: int = 0
    # _triples_input_rate: float = 0.0
    triples_avg_size: float = 0.0
    triples_total_amount: int = 0
    # triples_materialised_amount: int = 0
    # _triples_materialised_rate: float = 0.0
    memory_usage: int = 0
    partial_chains_amount: int = -1
    full_chains_amount: int = -1

    @classmethod
    def get_dynamic_properties(cls):
        return [
            "triples_materialised_amount",
            "memory_usage_gigabytes",
            "triples_materialised_rate",
            "triples_input_rate",
        ]

    def __eq__(self, other):
        if not type(other) is type(self):
            return False
        if self.__dict__.items() == other.__dict__items():
            return True

    @property
    def memory_usage_gigabytes(self):
        return float(self.memory_usage / 1000 / 1000 / 1000)

    @property
    def triples_materialised_amount(self):
        return self.triples_total_amount - self.triples_input_amount

    @property
    def triples_materialised_rate(self):
        return (
            self.triples_materialised_amount / self.time_to_infer
            if self.time_to_infer
            else 1.0
        )

    @property
    def triples_input_rate(self):
        return (
            self.triples_input_amount / self.time_to_load if self.time_to_load else 1.0
        )

    @property
    def json(self):
        members = self.__dict__
        for dynamic_property in InferenceStats.get_dynamic_properties():
            members[dynamic_property] = getattr(self, dynamic_property)

        return members

    @classmethod
    def from_static_properties(cls, static_properties):
        static_property_keys = static_properties.keys()
        for dynamic_property in InferenceStats.get_dynamic_properties():
            if dynamic_property in static_property_keys:
                del static_properties[dynamic_property]
        return cls(**static_properties)

    def __and__(self, other):
        merged_attributes = {}
        if not (type(other) == type(self)):
            raise Exception("These are not the same thing")
        for key, value in self.__dict__.items():
            other_value = getattr(other, key)
            new_value = other_value if other_value > value else value
            merged_attributes[key] = new_value
        return InferenceStats(**merged_attributes)


@dataclass
class InferenceStatProcessor:
    inference_stats: str

    def process_inference(self):
        self.inference_stats = self.inference_stats.replace("\r", "")
        time_stats_only = InferenceStats(**self.process_time_stats())
        performance_stats_only = InferenceStats(**self.process_performance_stats())
        final_stats = time_stats_only & performance_stats_only
        return final_stats

    def process_performance_stats(self):
        triples_avg_size = self.parse_average_entry_size()
        triples_input_amount, triples_materialised_amount = self.parse_aggregate_stats()
        memory_usage = triples_materialised_amount * triples_avg_size
        result = {
            "triples_avg_size": triples_avg_size,
            "triples_input_amount": triples_input_amount,
            "triples_total_amount": triples_materialised_amount,
            "memory_usage": memory_usage,
        }
        partial_chains = self.parse_chains_amount()
        result.update(partial_chains)
        return result

    def parse_average_entry_size(self):
        match = BYTES_PER_ENTRY_REGEX.findall(self.inference_stats)
        if match and (len(match) == 1):
            return float(match[0])
        raise Exception("Not found BYTES_PER_ENTRY")

    def parse_aggregate_stats(self):
        matches = dict(AGGREGATE_NUMBER_OF_REGEX.findall(self.inference_stats))
        triples_input_amount = int(matches["EDB"].replace(",", ""))
        triples_materialised_amount = int(matches["IDB"].replace(",", ""))

        return (triples_input_amount, triples_materialised_amount)

    def process_time_stats(self):
        inference_stats_dict = {}
        time_matches = TIMESTAMP_REGEX.findall(self.inference_stats)
        for match in time_matches:
            element = self.process_time_match_to_stat(match)
            inference_stats_dict.update(element)
        return inference_stats_dict

    def process_time_match_to_stat(self, match):
        key = STAT_MAP[match[0]]
        start_date = self.parse_rdfox_tstamp_to_datetime(match[1])
        end_date = self.parse_rdfox_tstamp_to_datetime(match[2])
        duration = (end_date - start_date).seconds
        elem = {key: duration}
        return elem

    def parse_rdfox_tstamp_to_datetime(self, rdfox_tstamp: str) -> datetime.time:
        return datetime.strptime(rdfox_tstamp, RDFOX_TSTAMP_FORMAT)

    def parse_chains_amount(self):
        result = {}
        chain_matches = CHAIN_AMOUNT_REGEX.findall(self.inference_stats)
        chain_map_keys = CHAIN_MAP.keys()
        for match in chain_matches:
            chain_type, amount = match
            if chain_type in chain_map_keys:
                result[CHAIN_MAP[chain_type]] = int(amount)
        return result
