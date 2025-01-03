#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Discover                                                                   #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /discover/flow/dataprep/ingest/stage.py                                             #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-discover                               #
# ------------------------------------------------------------------------------------------------ #
# Created    : Wednesday January 1st 2025 05:30:48 am                                              #
# Modified   : Friday January 3rd 2025 01:23:32 am                                                 #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2025 John James                                                                 #
# ================================================================================================ #
"""Data Ingestion Stage Module"""
from typing import List

from discover.asset.dataset.dataset import Dataset
from discover.flow.base.stage import Stage
from discover.flow.base.task import Task
from discover.infra.persist.object.flowstate import FlowState
from discover.infra.persist.repo.dataset import DatasetRepo


class IngestStage(Stage):
    def __init__(
        self,
        source: Dataset,
        target: Dataset,
        tasks: List[Task],
        state: FlowState,
        repo: DatasetRepo,
    ) -> None:
        super().__init__(source=source, target=target, tasks=tasks)

    def initialize_stage(self) -> None:
        """Logic executed prior at the onset of stage execution"""
        super().initialize_stage()

    def finalize_stage(self) -> None:
        """Logic executed after stage execution"""
        super().finalize_stage()
