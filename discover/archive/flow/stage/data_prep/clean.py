#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Discover                                                                   #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /discover/archive/flow/stage/data_prep/clean.py                                     #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-discover                               #
# ------------------------------------------------------------------------------------------------ #
# Created    : Saturday October 19th 2024 12:57:59 pm                                              #
# Modified   : Thursday January 2nd 2025 06:43:37 am                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Cleaning Stage Module"""

import pandas as pd

from discover.core.dtypes import DFType
from discover.core.flow import DataPrepStageDef, PhaseDef
from discover.flow.stage.base import DataPrepStage
from discover.infra.utils.data.compare import compare_dataframes
from discover.infra.utils.data.format import show_thousands_separator

# ------------------------------------------------------------------------------------------------ #
COLUMNS = [
    "id",
    "app_id",
    "app_name",
    "category_id",
    "author",
    "rating",
    "content",
    "vote_sum",
    "vote_count",
    "date",
]


# ------------------------------------------------------------------------------------------------ #
class DataCleaningStage(DataPrepStage):
    """
    Stage for cleaning data in the data preparation pipeline.

    This class inherits from `DataPrepStageDef` and focuses on data cleaning tasks
    to ensure data quality and consistency before further processing. It sets up
    the configuration and execution logic needed for data cleaning.

    Args:
        phase (PhaseDef): The phase of the data pipeline.
        stage (DataPrepStageDef): The specific stage within the data pipeline.
        source_config (dict): Configuration for the data source.
        destination_config (dict): Configuration for the data destination.
        force (bool, optional): Whether to force execution, even if the output already
            exists. Defaults to False.
        return_dataset (bool): Whether to return resultant dataset or its asset_id
    """

    def __init__(
        self,
        phase: PhaseDef,
        stage: DataPrepStageDef,
        source_config: dict,
        destination_config: dict,
        force: bool = False,
        return_dataset: bool = True,
        **kwargs,
    ) -> None:
        super().__init__(
            phase=phase,
            stage=stage,
            source_config=source_config,
            destination_config=destination_config,
            force=force,
            return_dataset=return_dataset,
            **kwargs,
        )

    def summarize(self) -> None:
        # Reload original and clean datasets
        orig_df = self._get_data(
            asset_id=self._source_asset_id,
            dftype=DFType.PANDAS,
        )
        clean_df = self._get_data(
            asset_id=self._destination_asset_id,
            dftype=DFType.PANDAS,
        )
        comparison = compare_dataframes(
            self_df=orig_df,
            other_df=clean_df,
            cols=COLUMNS,
        )
        comparison_dict = {
            "Rows": [
                int(orig_df.shape[0]),
                int(clean_df.shape[0]),
                round(
                    (orig_df.shape[0] - clean_df.shape[0]) / orig_df.shape[0] * 100, 2
                ),
            ],
            "Rows Modified": [
                0,
                int(comparison.rows_modified),
                round(comparison.rows_modified / orig_df.shape[0] * 100, 2),
            ],
            "Size (Mb)": [
                int(comparison.self_dataset_size) / 1024 * 1024,
                int(comparison.other_dataset_size) / 1024 * 1024,
                round(
                    (comparison.self_dataset_size - comparison.other_dataset_size)
                    / comparison.self_dataset_size
                    * 100,
                    2,
                ),
            ],
        }
        summary = pd.DataFrame.from_dict(
            data=comparison_dict,
            orient="index",
            columns=["Original", "Clean", "% Change"],
        )
        return summary.apply(show_thousands_separator)
