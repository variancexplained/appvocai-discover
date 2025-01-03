#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Discover                                                                   #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /discover/flow/stage/data_prep/ingest.py                                            #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-discover                               #
# ------------------------------------------------------------------------------------------------ #
# Created    : Saturday October 19th 2024 12:57:59 pm                                              #
# Modified   : Friday December 27th 2024 05:21:00 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Ingest Stage Module"""


from discover.core.flow import DataPrepStageDef, PhaseDef
from discover.flow.stage.base import DataPrepStage


# ------------------------------------------------------------------------------------------------ #
class IngestionStage(DataPrepStage):
    """
    Stage for data ingestion in the data processing pipeline.

    This class handles the ingestion of raw data from a specified source, applies
    a series of tasks to preprocess the data, and saves the processed result to
    the destination. It inherits from `DataPrepStageDef` and implements the
    logic for data loading and saving.

    Args:
        phase (PhaseDef): The phase of the data pipeline.
        stage (DataPrepStageDef): The specific stage within the data pipeline.
        source_config (dict): Configuration for the data source, including the file path.
        destination_config (dict): Configuration for the data destination.
        force (bool, optional): Whether to force execution, even if the output already
            exists. Defaults to False.
    """

    def __init__(
        self,
        phase: PhaseDef,
        stage: DataPrepStageDef,
        source_config: dict,
        destination_config: dict,
        force: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(
            phase=phase,
            stage=stage,
            source_config=source_config,
            destination_config=destination_config,
            force=force,
            **kwargs,
        )
