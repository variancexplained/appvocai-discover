#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppInsight                                                                          #
# Version    : 0.1.0                                                                               #
# Python     : 3.12.3                                                                              #
# Filename   : /appvocai/utils/io.py                                                               #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appinsight                                      #
# ------------------------------------------------------------------------------------------------ #
# Created    : Wednesday May 29th 2024 12:55:39 am                                                 #
# Modified   : Tuesday August 27th 2024 10:54:13 pm                                                #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""IO Utility Module"""
import os

import pandas as pd
from appvocai.shared.persist.file.io import IOService
from appvocai.utils.base import Reader, Writer
from pyspark.sql import DataFrame, SparkSession


# ------------------------------------------------------------------------------------------------ #
#                                         PANDAS READER                                            #
# ------------------------------------------------------------------------------------------------ #
class FileReader(Reader):
    """Reads pandas DataFrame from file.

    Args:
        io (type[IOService]):
    """

    def __init__(self, io_cls: type[IOService] = IOService, **kwargs) -> None:
        super().__init__()
        self._io = io_cls()
        self._kwargs = kwargs

    def read(self, filepath: str) -> pd.DataFrame:
        """Reads Pandas DataFrames from various file formats."""
        try:
            return self._io.read(filepath=filepath, **self._kwargs)
        except FileNotFoundError as fe:
            msg = f"File was not found at {filepath}\n{fe}"
            self.logger.exception(msg)
            raise

        except Exception as e:
            msg = f"Exception occurred while reading from {filepath}.\n{e}"
            self.logger.exception(msg)
            raise


# ------------------------------------------------------------------------------------------------ #
#                                         PANDAS WRITER                                            #
# ------------------------------------------------------------------------------------------------ #
class FileWriter(Writer):
    """Writes a pandas DataFrame to file.

    Args:
        review_repo (ReviewRepo): Dataset Manager responsible for files in environments.
    """

    def __init__(self, io_cls: type[IOService] = IOService, **kwargs) -> None:
        super().__init__()
        self._io = io_cls()
        self._kwargs = kwargs

    def write(self, data: pd.DataFrame, filepath: str) -> pd.DataFrame:
        """Writes Pandas DataFrames in various file formats."""
        try:
            return self._io.write(data=data, filepath=filepath, **self._kwargs)
        except Exception as e:
            msg = f"Exception occurred while writing to {filepath}.\n{e}"
            self.logger.exception(msg)
            raise


# ------------------------------------------------------------------------------------------------ #
#                                        PYSPARK READER                                            #
# ------------------------------------------------------------------------------------------------ #
class PySparkReader(Reader):
    """Reads pyspark DataFrame from file.

    Args:
        spark (SparkSession): Spark session.
        partition (bool): Whether to partition the dataset.
    """

    def __init__(
        self,
        spark: SparkSession,
    ) -> None:
        super().__init__()
        self._spark = spark

    def read(
        self,
        filepath: str,
    ) -> DataFrame:
        """Reads Spark DataFrames from various file formats."""
        try:
            return self._spark.read.parquet(filepath)
        except Exception as e:
            msg = f"Exception occurred while reading {filepath}.\n{e}"
            self.logger.exception(msg)
            raise


# ------------------------------------------------------------------------------------------------ #
#                                        PYSPARK WRITER                                            #
# ------------------------------------------------------------------------------------------------ #
class PySparkWriter(Writer):
    """Writes a pyspark DataFrame to file."""

    def __init__(self) -> None:
        super().__init__()

    def write(
        self,
        data: DataFrame,
        filepath: str,
    ) -> None:
        """Writes a PySpark DataFrame to file."""
        # Ensure the directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        try:
            data.write.parquet(path=filepath, mode="overwrite")
        except Exception as e:
            msg = f"Exception occurred while writing to {filepath}.\n{e}"
            self.logger.exception(msg)
            raise
