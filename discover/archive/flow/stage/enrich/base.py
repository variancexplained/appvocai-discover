#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Discover                                                                   #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /discover/archive/flow/stage/enrich/base.py                                         #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-discover                               #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday November 22nd 2024 12:15:07 am                                               #
# Modified   : Saturday January 4th 2025 06:18:07 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Data Enrichment Stage Module"""
from discover.core.flow import DataStageDef, PhaseDef
from discover.flow.stage.base import Stage


# ------------------------------------------------------------------------------------------------ #
class DataEnrichmentStage(Stage):
    """
    Base class for data enrichment stages.

    Args:
        phase (PhaseDef): The phase of the pipeline to which this stage belongs.
        stage (DataStageDef): The specific stage identifier within the phase.
        source_config (dict): Configuration for the source dataset, including input paths and schema details.
        destination_config (dict): Configuration for the destination dataset, specifying where enriched data will be saved.
        force (bool, optional): If True, forces the stage to re-run even if outputs already exist. Defaults to False.
        **kwargs: Additional arguments to support custom functionality or configurations.
    """

    def __init__(
        self,
        phase: PhaseDef,
        stage: DataStageDef,
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
