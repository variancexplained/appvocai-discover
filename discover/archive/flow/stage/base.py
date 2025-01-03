#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Discover                                                                   #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /discover/archive/flow/stage/base.py                                                #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-discover                               #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday September 20th 2024 08:14:05 pm                                              #
# Modified   : Friday January 3rd 2025 01:01:17 am                                                 #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Data preparation stage base module."""
from __future__ import annotations

import logging
from abc import ABC
from typing import Type, Union

import pandas as pd
from dependency_injector.wiring import Provide, inject
from pyspark.sql import DataFrame

from discover.asset.base.atype import AssetType
from discover.container import DiscoverContainer
from discover.core.dataset import Dataset, DatasetFactory, DFType
from discover.core.file import FileFormat
from discover.core.flow import (
    DataEnrichmentStageDef,
    DataPrepStageDef,
    ModelStageDef,
    PhaseDef,
    StageDef,
)
from discover.flow.base.task import Task, TaskBuilder
from discover.infra.exception.config import (
    DatasetConfigurationException,
    PhaseConfigurationError,
    StageConfigurationException,
)
from discover.infra.service.logging.stage import stage_logger
from discover.infra.workspace.service import Workspace


# ------------------------------------------------------------------------------------------------ #
#                                         STAGE                                                    #
# ------------------------------------------------------------------------------------------------ #
class Stage(ABC):
    """Represents a data preparation stage in a pipeline.

    This stage is responsible for preparing data by applying a sequence of tasks to a source dataset
    and creating a transformed destination dataset.

    Args:
        phase (PhaseDef): The phase of the pipeline to which this stage belongs.
        stage (StageDef): The specific stage within the pipeline.
        source_config (dict): Configuration for the source dataset.
        destination_config (dict): Configuration for the destination dataset.
        dataset_factory_cls (Type[DatasetFactory], optional): Factory class for creating datasets. Defaults to DatasetFactory.
        force (bool, optional): Whether to force execution, overriding default conditions. Defaults to False.
        **kwargs: Additional keyword arguments for extended functionality.

    Attributes:
        _dataset_factory (DatasetFactory): Factory for creating datasets.
        _source_config (dict): Deserialized configuration for the source dataset.
        _destination_config (dict): Deserialized configuration for the destination dataset.
        _source_asset_id (str): Asset ID of the source dataset.
        _destination_asset_id (str): Asset ID of the destination dataset.
        _logger (logging.Logger): Logger for the stage.
    """

    _task_builder = TaskBuilder

    @inject
    def __init__(
        self,
        phase: PhaseDef,
        stage: StageDef,
        source_config: dict,
        destination_config: dict,
        dataset_factory_cls: Type[DatasetFactory] = DatasetFactory,
        workspace: Workspace = Provide[DiscoverContainer.workspace.service],
        force: bool = False,
        **kwargs,
    ) -> None:
        self._phase = phase
        self._stage = stage
        self._force = force

        self._source_config = source_config
        self._destination_config = destination_config

        self._dataset_factory = dataset_factory_cls()

        self._workspace = workspace

        # Obtain asset IDs for the source and destination datasets.
        self._source_asset_id = self._workspace.get_asset_id(**self._source_config)
        self._destination_asset_id = self._workspace.get_asset_id(
            **self._destination_config
        )

        self._tasks = []

        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @property
    def phase(self) -> PhaseDef:
        """Returns the phase of the pipeline.

        Returns:
            PhaseDef: The phase associated with this stage.
        """
        return self._phase

    @property
    def stage(self) -> StageDef:
        """Returns the specific stage within the pipeline.

        Returns:
            DataPrepStageDef: The stage associated with this instance.
        """
        return self._stage

    def add_task(self, task: Task) -> None:
        """Adds a task to the stage and assigns the stage identifier to the task.

        Args:
            task (Task): The task to be added to the stage.

        Raises:
            TypeError: If the task is not an instance of the expected Task class.
        """
        if not isinstance(task, Task):
            raise TypeError(
                f"Expected an instance or subclass of Task. Received type {type(task)}"
            )
        self._tasks.append(task)

    @stage_logger
    def run(self) -> Dataset:
        """Executes the data preparation stage.

        If the destination dataset already exists and `force` is not enabled, the existing dataset is returned.
        Otherwise, the stage processes the source dataset and generates a new destination dataset.

        Returns:
            Dataset: The resulting dataset after executing the stage.
        """
        if (
            self._workspace.dataset_repo.exists(asset_id=self._destination_asset_id)
            and not self._force
        ):
            return self._workspace.dataset_repo.get(asset_id=self._destination_asset_id)
        else:
            return self._run()

    def _run(self) -> Dataset:
        """Processes the source dataset and applies tasks to generate the destination dataset.

        Returns:
            Dataset: The newly created destination dataset.
        """
        # Obtain the source data in the specified dataframe structure
        data = self._get_data(
            asset_id=self._source_asset_id,
            dftype=self._source_config["dftype"],
        )

        # Apply tasks to the data sequentially.
        for task in self._tasks:
            data = task.run(data=data)

        # Create, persist and return the output (destination) dataset.
        return self._create_destination_dataset(data=data)

    @classmethod
    def build(
        cls,
        stage_config: dict,
        force: bool = False,
        **kwargs,
    ) -> Stage:
        """Abstract factory classmethod for constructing Stage subclasses. Subclasses will
        override this class with phase and stage specific behaviors.

        Args:
            stage_config (dict): Configuration dictionary containing stage, source, destination, and task definitions.
            force (bool, optional): Whether to force execution, overriding default conditions. Defaults to False.
            **kwargs: Additional keyword arguments for extended functionality.

        Returns:
            Stage: An instance of DataPrepStageDef.

        Raises:
            ValueError: If a required key is missing from the configuration.
            RuntimeError: If an error occurs during stage creation.
        """

        stage_config = ConfigDeserializer.deserialize_stage_config(
            stage_config=stage_config
        )

        try:
            # Instantiate the Stage object
            stage = cls(
                phase=stage_config["phase"],
                stage=stage_config["stage"],
                source_config=stage_config["source_config"],
                destination_config=stage_config["destination_config"],
                force=force,
                **kwargs,
            )

            # Construct the Stage's Task objects
            tasks = [
                cls._task_builder.build(
                    phase=stage_config["phase"],
                    stage=stage_config["stage"],
                    task_config=task_config,
                )
                for task_config in stage_config["tasks"]
            ]

            # Add Tasks to the Stage object
            for task in tasks:
                stage.add_task(task)

            return stage

        except KeyError as e:
            raise ValueError(
                f"Missing required configuration key in stage_config: {str(e)}"
            ) from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to build stage from configuration: {str(e)}"
            ) from e

    def _get_data(
        self, asset_id: str, dftype: DFType
    ) -> Union[pd.DataFrame, DataFrame]:
        # Obtain the source dataset and extract the DataFrame in the specified structure.
        dataset = self._workspace.dataset_repo.get(asset_id=asset_id)
        return dataset.as_df(dftype=dftype)

    def _create_destination_dataset(
        self, data: Union[pd.DataFrame, DataFrame]
    ) -> Dataset:

        # Delete existing destination dataset, if it exists.
        if self._workspace.dataset_repo.exists(asset_id=self._destination_asset_id):
            self._workspace.dataset_repo.remove(asset_id=self._destination_asset_id)

        # Create the new destination dataset and return it.
        return self._dataset_factory.from_df(
            phase=self._destination_config["phase"],
            stage=self._destination_config["stage"],
            name=self._destination_config["name"],
            data=data,
            dftype=self._destination_config["dftype"],
            file_format=self._destination_config["file_format"],
        )


# ------------------------------------------------------------------------------------------------ #
#                                   CONFIG DESERIALIZER                                            #
# ------------------------------------------------------------------------------------------------ #
class ConfigDeserializer:
    """Utility class for deserializing configuration objects into appropriate Enums.

    This class provides methods to deserialize configuration dictionaries and stage information,
    converting raw string values into typed Enum instances for better validation and usability.
    """

    @classmethod
    def deserialize_stage(cls, phase: str, stage: str) -> StageDef:
        """Deserializes the stage based on the provided phase value.

        Args:
            phase (str): The phase identifier, such as "dataprep", "enrich", or "model".
            stage (str): The stage identifier to be deserialized within the phase.

        Returns:
            StageDef: The deserialized stage Enum corresponding to the phase and stage.

        Raises:
            PhaseConfigurationError: If the phase value is unrecognized.
        """
        if "dataprep" in phase.strip().lower():
            return DataPrepStageDef.from_value(stage)
        elif "enrich" in phase.strip().lower():
            return DataEnrichmentStageDef.from_value(stage)
        elif "model" in phase.strip().lower():
            return ModelStageDef.from_value(stage)
        else:
            msg = f"Unrecognized phase: {phase} in deserialize_stage."
            raise PhaseConfigurationError(msg)

    @classmethod
    def deserialize_dataset_config(cls, config: dict) -> dict:
        """Deserializes a dataset configuration dictionary.

        Converts raw string values in the dataset configuration to appropriate Enums.

        Args:
            config (dict): The dataset configuration containing keys like "asset_type",
                "phase", "stage", "dftype", and "file_format".

        Returns:
            dict: The deserialized dataset configuration with Enums replacing raw string values.

        Raises:
            DatasetConfigurationException: If the configuration is malformed or an error occurs during deserialization.
        """
        config_deserialized = config.copy()

        try:
            config_deserialized["asset_type"] = AssetType.from_value(
                config["asset_type"]
            )
            config_deserialized["phase"] = PhaseDef.from_value(config["phase"])
            config_deserialized["stage"] = cls.deserialize_stage(
                phase=config["phase"], stage=config["stage"]
            )
            config_deserialized["dftype"] = DFType.from_value(value=config["dftype"])
            config_deserialized["file_format"] = FileFormat.from_value(
                value=config["file_format"]
            )
            return config_deserialized
        except KeyError as e:
            msg = f"Malformed dataset config: {config}. Unable to deserialize it."
            raise DatasetConfigurationException(msg, exc=e)
        except Exception as e:
            msg = "Unknown error occurred while deserializing dataset configuration."
            raise DatasetConfigurationException(msg, exc=e)

    @classmethod
    def deserialize_stage_config(cls, stage_config: dict) -> dict:
        """Deserializes a stage configuration dictionary.

        Converts raw string values in the stage configuration into appropriate Enums
        and recursively deserializes related dataset configurations for source and destination.

        Args:
            stage_config (dict): The stage configuration containing keys like "phase",
                "stage", "source_config", and "destination_config".

        Returns:
            dict: The deserialized stage configuration with Enums replacing raw string values
                and nested configurations deserialized.

        Raises:
            StageConfigurationException: If the stage configuration is malformed or an error occurs during deserialization.
        """
        stage_config_deserialized = stage_config.copy()

        try:
            stage_config_deserialized["phase"] = PhaseDef.from_value(
                stage_config["phase"]
            )
            stage_config_deserialized["stage"] = cls.deserialize_stage(
                phase=stage_config["phase"], stage=stage_config["stage"]
            )

            # Source Config
            stage_config_deserialized["source_config"] = cls.deserialize_dataset_config(
                config=stage_config["source_config"]
            )
            # Destination Config
            stage_config_deserialized["destination_config"] = (
                cls.deserialize_dataset_config(
                    config=stage_config["destination_config"]
                )
            )
            return stage_config_deserialized

        except KeyError as e:
            msg = f"Malformed dataset config: {stage_config}. Unable to deserialize it."
            raise StageConfigurationException(msg, exc=e)
        except Exception as e:
            msg = f"Unknown error occurred while deserializing stage configuration.\n{stage_config}"
            raise StageConfigurationException(msg, exc=e)
