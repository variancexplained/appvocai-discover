#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Discover                                                                   #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /discover/infra/monitor/profile.py                                                  #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-discover                               #
# ------------------------------------------------------------------------------------------------ #
# Created    : Monday September 9th 2024 07:42:03 pm                                               #
# Modified   : Saturday September 14th 2024 02:29:56 am                                            #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Profile Module"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from discover.core.data import DataClass
from discover.domain.value_objects.context import Context
from discover.domain.value_objects.lifecycle import Stage


# ------------------------------------------------------------------------------------------------ #
@dataclass
class Profile(DataClass):

    runid: str  # Unique identifier for each run.
    service_type: str  # Type of service, i.e. Pipeline or Task
    service_name: str  # Name of Pipeline or Task
    stage: Stage  # Stage of the process.
    start_time: datetime  # Task start time
    end_time: datetime  # Task end time
    runtime_seconds: float  # Total runtime of the process (in seconds)
    cpu_cores: int  # Total number of cpu cores in the machine.
    cpu_user_utilization: float  # Time spent in user space (in seconds)
    cpu_system_utilization: float  # Time spent in system space (in seconds)
    memory_usage_peak_mb: float  # Peak memory usage (in MB)
    memory_allocations: int  # Number of memory allocations during the process
    file_read_bytes: int  # Total bytes read from files during the process
    file_write_bytes: int  # Total bytes written to files during the process
    io_wait_time_seconds: (
        float  # Time spent waiting for I/O operations to complete (in seconds)
    )
    network_data_sent_bytes: int  # Total data sent over the network (in bytes)
    network_data_received_bytes: int  # Total data received over the network (in bytes)
    exceptions_raised: int = (
        0  # Number of exceptions raised during process execution (default 0)
    )

    @classmethod
    def create(cls, context: Context) -> Profile:
        return cls(
            runid=context.runid,
            service_type=context.service_type,
            service_name=context.service_name,
            stage=context.stage,
        )
