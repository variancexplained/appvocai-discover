#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Discover                                                                   #
# Version    : 0.1.0                                                                               #
# Python     : 3.12.3                                                                              #
# Filename   : /conftest.py                                                                        #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-discover                               #
# ------------------------------------------------------------------------------------------------ #
# Created    : Thursday April 25th 2024 12:55:55 am                                                #
# Modified   : Friday January 3rd 2025 05:38:08 am                                                 #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import os
import sys
from datetime import datetime

import pytest
from dotenv import load_dotenv
from pyspark.sql import SparkSession

from discover.asset.base.atype import AssetType
from discover.asset.dataset.builder import DatasetBuilder
from discover.asset.dataset.identity import DatasetPassport
from discover.container import DiscoverContainer
from discover.core.dtypes import DFType
from discover.core.file import FileFormat
from discover.core.flow import PhaseDef, TestStageDef
from discover.infra.config.app import AppConfigReader
from discover.infra.persist.cloud.aws import S3Handler

# ------------------------------------------------------------------------------------------------ #
load_dotenv()
# ------------------------------------------------------------------------------------------------ #
collect_ignore_glob = ["discover/core/*.*"]
collect_ignore = ["discover/core/*.*"]
# ------------------------------------------------------------------------------------------------ #
# pylint: disable=redefined-outer-name, no-member
# ------------------------------------------------------------------------------------------------ #


# ------------------------------------------------------------------------------------------------ #
#                              DEPENDENCY INJECTION                                                #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="session", autouse=True)
def container():
    container = DiscoverContainer()
    container.init_resources()
    container.wire(packages=["discover.asset.dataset", "discover.flow"])
    return container


# ------------------------------------------------------------------------------------------------ #
#                                 CHECK ENVIRONMENT                                                #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="session", autouse=True)
def check_environment() -> None:
    # Get the current environment
    load_dotenv()
    current_env = os.environ.get("ENV")

    # Check if the current environment is 'test'
    if current_env != "test":
        print(
            "Tests can only be run in the 'test' environment. Current environment is: {}".format(
                current_env
            )
        )
        sys.exit(1)


# ------------------------------------------------------------------------------------------------ #
#                                         AWS                                                      #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="session")
def aws():
    return S3Handler(config_reader_cls=AppConfigReader)


# ------------------------------------------------------------------------------------------------ #
#                                        SPARK                                                     #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="session")
def spark():
    """
    Pytest fixture to create a Spark session.
    This fixture is session-scoped, meaning it will be created once per test session.
    """
    # Assuming the log4j.properties file is in the root directory
    log4j_conf_path = "file:" + os.path.abspath("log4j.properties")
    spark_session = (
        SparkSession.builder.appName("pytest-spark-session")
        .master("local[*]")
        .config(
            "spark.driver.extraJavaOptions", f"-Dlog4j.configuration={log4j_conf_path}"
        )
        .config("spark.sql.session.timeZone", "UTC")
        .config(
            "spark.executor.extraJavaOptions",
            f"-Dlog4j.configuration={log4j_conf_path}",
        )
        .getOrCreate()
    )
    spark_session.sparkContext.setLogLevel("ERROR")

    yield spark_session

    # Teardown after the test session ends
    spark_session.stop()


# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="session")
def sparklight():
    """
    Pytest fixture to create a Spark session.
    This fixture is session-scoped, meaning it will be created once per test session.
    """

    spark_session = (
        SparkSession.builder.appName("pytest-spark-session")
        .master("local[*]")
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )
    spark_session.sparkContext.setLogLevel("ERROR")

    yield spark_session

    # Teardown after the test session ends
    spark_session.stop()


# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="session")
def sparknlp():
    """
    Pytest fixture to create a Spark session.
    This fixture is session-scoped, meaning it will be created once per test session.
    """
    memory = "96g"
    parquet_block_size = 1073741824
    # Assuming the log4j.properties file is in the root directory
    log4j_conf_path = "file:" + os.path.abspath("log4j.properties")
    spark_session = (
        SparkSession.builder.appName("appvocai-discover-nlp")
        .master("local[*]")
        .config("spark.driver.memory", memory)
        .config("spark.executor.memory", memory)
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.sql.parquet.block.size", parquet_block_size)
        .config("spark.sql.execution.arrow.pyspark.enabled", "true")
        .config("spark.sql.execution.arrow.pyspark.fallback.enabled", "false")
        .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
        .config("spark.kryoserializer.buffer.max", "2000M")
        .config("spark.driver.maxResultSize", "0")
        .config(
            "spark.jars.packages",
            "com.johnsnowlabs.nlp:spark-nlp_2.12:5.3.3",
        )
        .config(
            "spark.driver.extraJavaOptions",
            f"-Dlog4j.configurationFile={log4j_conf_path}",
        )
        .config(
            "spark.executor.extraJavaOptions",
            f"-Dlog4j.configurationFile={log4j_conf_path}",
        )
        .getOrCreate()
    )
    spark_session.sparkContext.setLogLevel("ERROR")

    yield spark_session

    # Teardown after the test session ends
    spark_session.stop()


# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="session")
def spark_session_pool(container):
    return container.spark.session_pool()


# ------------------------------------------------------------------------------------------------ #
#                                       DATA                                                       #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="session")
def pandas_df(container):
    """
    Pytest fixture that reads a Parquet file into a pandas DataFrame.
    Modify this to point to the correct Parquet file.
    """
    FILEPATH = "data/working/reviews"
    iofactory = container.io.iofactory()
    reader = iofactory.get_reader(dftype=DFType.PANDAS, file_format=FileFormat.PARQUET)
    return reader.read(filepath=FILEPATH)


# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="session")
def spark_df(spark, container):
    """
    Pytest fixture that converts a pandas DataFrame to a Spark DataFrame.
    Requires the spark fixture and pandas_df_from_csv fixture.
    """
    FILEPATH = "data/working/reviews"
    iofactory = container.io.iofactory()
    reader = iofactory.get_reader(dftype=DFType.SPARK, file_format=FileFormat.PARQUET)
    return reader.read(filepath=FILEPATH, spark=spark)


# ------------------------------------------------------------------------------------------------ #
#                                      WORKSPACE                                                   #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="session")
def workspace(container):
    return container.workspace.service()


# ------------------------------------------------------------------------------------------------ #
#                                         FAO                                                      #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="session")
def fao(container):
    return container.io.fao()


# ------------------------------------------------------------------------------------------------ #
#                                         PASSPORT                                                 #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="session")
def ds_passport():
    return DatasetPassport(
        asset_id="dataset_test_dataset_v1.0",
        phase=PhaseDef.TESTING,
        stage=TestStageDef.SMOKE_TEST,
        asset_type=AssetType.DATASET,
        name="test_dataset",
        version="v1.0",
        creator="PyTest",
        created=datetime.now(),
    )


# ------------------------------------------------------------------------------------------------ #
#                                          FILEPATH                                                #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="session")
def filepath_csv(workspace, ds_passport):
    return workspace.get_filepath(
        asset_type=ds_passport.asset_type,
        asset_id=ds_passport.asset_id,
        phase=ds_passport.phase,
        file_format=FileFormat.CSV,
    )


# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="session")
def filepath_parquet(workspace, ds_passport):
    return workspace.get_filepath(
        asset_type=ds_passport.asset_type,
        asset_id=ds_passport.asset_id,
        phase=ds_passport.phase,
        file_format=FileFormat.PARQUET,
    )


# ------------------------------------------------------------------------------------------------ #
#                                     DATASETS                                                     #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="session")
def dataset_pandas_csv(ds_passport, pandas_df):
    return (
        DatasetBuilder().passport(ds_passport).from_dataframe(pandas_df).build().dataset
    )


# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="session")
def dataset_pandas_parquet(ds_passport, pandas_df):
    return (
        DatasetBuilder().passport(ds_passport).from_dataframe(pandas_df).build().dataset
    )


# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="session")
def dataset_spark_csv(ds_passport, spark_df):
    return (
        DatasetBuilder().passport(ds_passport).from_dataframe(spark_df).build().dataset
    )


# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="session")
def dataset_spark_parquet(ds_passport, spark_df):
    return (
        DatasetBuilder().passport(ds_passport).from_dataframe(spark_df).build().dataset
    )
