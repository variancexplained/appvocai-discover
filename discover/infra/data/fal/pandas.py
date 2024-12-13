#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Discover                                                                   #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /discover/infra/data/fal/centralized.py                                             #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-discover                               #
# ------------------------------------------------------------------------------------------------ #
# Created    : Sunday September 22nd 2024 05:36:35 pm                                              #
# Modified   : Thursday December 19th 2024 05:00:17 am                                             #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Module for the Centralized File System (CFS) Data Access Layer"""
import pandas as pd

from discover.infra.persistence.dal.fao.base import FilesetDAL
from discover.infra.persistence.dal.fao.exception import FileIOException
from discover.infra.persistence.dal.fao.location import FilesetLocationService


# ------------------------------------------------------------------------------------------------ #
class CentralizedFilesetDAL(FilesetDAL):
    """
    File Access Object (FAO) for interacting with a centralized file system using Pandas.

    This class handles reading and writing Parquet files using Pandas DataFrames for storage
    systems that are accessible as a centralized file system (e.g., local filesystem, NFS).

    Args:
        storage_config (dict): Persistence configuration

    Inherits from:
        FilesetDAL: Base class for file system-based data access operations.
    """

    def __init__(
        self, storage_config: dict, location_service: FilesetLocationService
    ) -> None:
        super().__init__(
            storage_config=storage_config, location_service=location_service
        )

    def _read(self, filepath: str) -> pd.DataFrame:
        """
        Reads a Parquet file from a specified filepath into a Pandas DataFrame.

        Uses `pd.read_parquet` to read the specified Parquet file. If an error occurs
        during the read operation, an exception is raised.

        Args:
            filepath (str): The path of the Parquet file to read.

        Returns:
            pd.DataFrame: The DataFrame containing the data read from the Parquet file.

        Raises:
            FileIOException: If an error occurs while reading the Parquet file.
        """
        try:
            return pd.read_parquet(path=filepath, **self._storage_config["read_kwargs"])
        except FileNotFoundError as e:
            msg = f"Exception occurred while reading a Parquet file from {filepath}.File does not exist.\n{e}"
            self._logger.error(msg)
            raise
        except Exception as e:
            msg = (
                f"Exception occurred while reading a Parquet file from {filepath}.\n{e}"
            )
            self._logger.exception(msg)
            raise FileIOException(msg, e) from e

    def _write(self, filepath: str, data: pd.DataFrame) -> None:
        """
        Writes a Pandas DataFrame to a specified filepath as a Parquet file.

        Uses `pd.DataFrame.to_parquet` to write the DataFrame to the specified file.
        If an error occurs during the write process, an exception is raised.

        Args:
            filepath (str): The path where the Parquet file will be written.
            data (pd.DataFrame): The DataFrame to write to the Parquet file.

        Raises:
            FileIOException: If an error occurs while writing the Parquet file.
        """
        try:
            data.to_parquet(path=filepath, **self._storage_config["write_kwargs"])
        except Exception as e:
            msg = f"Exception occurred while writing a Parquet file to {filepath}.\n{e}"
            self._logger.exception(msg)
            raise FileIOException(msg, e) from e
