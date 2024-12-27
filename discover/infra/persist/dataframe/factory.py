#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Discover                                                                   #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /discover/infra/persist/dataframe/factory.py                                        #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-discover                               #
# ------------------------------------------------------------------------------------------------ #
# Created    : Thursday December 26th 2024 02:21:28 pm                                             #
# Modified   : Thursday December 26th 2024 08:42:19 pm                                             #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""DataFrame IO Factory Module"""
import logging

from discover.core.data_structure import DataFrameStructureEnum
from discover.core.file import FileFormat
from discover.infra.persist.dataframe.base import DataFrameReader, DataFrameWriter
from discover.infra.persist.dataframe.pandas import (
    PandasDataFrameCSVReader,
    PandasDataFrameCSVWriter,
    PandasDataFrameParquetReader,
    PandasDataFrameParquetWriter,
)
from discover.infra.persist.dataframe.spark import (
    SparkDataFrameCSVReader,
    SparkDataFrameCSVWriter,
    SparkDataFrameParquetReader,
    SparkDataFrameParquetWriter,
)
from discover.infra.persist.file.base import IOFactory


# ------------------------------------------------------------------------------------------------ #
class DataFrameIOFactory(IOFactory):
    """Factory that produces DataFrame IO objects."""

    __reader_map = {
        "pandas_csv": PandasDataFrameCSVReader,
        "pandas_parquet": PandasDataFrameParquetReader,
        "spark_csv": SparkDataFrameCSVReader,
        "spark_parquet": SparkDataFrameParquetReader,
        "sparknlp_csv": SparkDataFrameCSVReader,
        "sparknlp_parquet": SparkDataFrameParquetReader,
    }
    __writer_map = {
        "pandas_csv": PandasDataFrameCSVWriter,
        "pandas_parquet": PandasDataFrameParquetWriter,
        "spark_csv": SparkDataFrameCSVWriter,
        "spark_parquet": SparkDataFrameParquetWriter,
        "sparknlp_csv": SparkDataFrameCSVReader,
        "sparknlp_parquet": SparkDataFrameParquetReader,
    }

    @classmethod
    def get_reader(
        cls,
        dataframe_structure: DataFrameStructureEnum,
        file_format: FileFormat = FileFormat.PARQUET,
    ) -> DataFrameReader:
        """Returns a dataframe reader for the specified dataframe structure and file format."""
        key = cls._format_key(
            dataframe_structure=dataframe_structure, file_format=file_format
        )
        try:
            logging.debug(f"\n\nRequesting a {key} reader from the DataFrameIOFactory")

            return cls.__reader_map[key]
        except KeyError:
            msg = f"Unsupported dataframe structure: {dataframe_structure} and file format {file_format}. Supported datarame structures are pandas and spark. Valid file formats are csv and parquet."
            raise ValueError(msg)

    @classmethod
    def get_writer(
        cls,
        dataframe_structure: DataFrameStructureEnum,
        file_format: FileFormat = FileFormat.PARQUET,
    ) -> DataFrameWriter:
        """Returns a dataframe writer for the specified dataframe structure and file format."""
        key = cls._format_key(
            dataframe_structure=dataframe_structure, file_format=file_format
        )
        try:
            logging.debug(f"\n\nRequesting a {key} writer from the DataFrameIOFactory")
            return cls.__writer_map[key]
        except KeyError:
            msg = f"Unsupported dataframe structure: {dataframe_structure} and file format {file_format}. Supported datarame structures are pandas and spark. Valid file formats are csv and parquet."
            raise ValueError(msg)

    @classmethod
    def _format_key(
        cls,
        dataframe_structure: DataFrameStructureEnum,
        file_format: FileFormat = FileFormat.PARQUET,
    ) -> str:
        return f"{dataframe_structure.value}_{file_format.value}"