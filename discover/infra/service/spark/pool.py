#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Discover                                                                   #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /discover/infra/service/spark/pool.py                                               #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-discover                               #
# ------------------------------------------------------------------------------------------------ #
# Created    : Tuesday September 24th 2024 12:50:08 am                                             #
# Modified   : Thursday January 2nd 2025 06:46:18 am                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import atexit
import logging
import os
import time
from enum import Enum
from typing import Dict

from pyspark.sql import SparkSession

from discover.core.dstruct import NestedNamespace

# ------------------------------------------------------------------------------------------------ #
# Set up root logger to only log errors
logging.getLogger("py4j").setLevel(logging.ERROR)
logging.getLogger("pyspark").setLevel(logging.ERROR)
logging.getLogger("com.johnsnowlabs").setLevel(logging.ERROR)
logging.getLogger("org.apache.spark").setLevel(logging.ERROR)
logging.getLogger("org.apache.hadoop").setLevel(logging.ERROR)


# ------------------------------------------------------------------------------------------------ #
#                                 SPARK SESSION  TYPE                                              #
# ------------------------------------------------------------------------------------------------ #
class SparkSessionType(Enum):

    SPARK = "spark"
    SPARKNLP = "sparknlp"


# ------------------------------------------------------------------------------------------------ #
# Register shutdown hook
def shutdown(session: SparkSession):
    print("Shutting down Spark session...")
    session.stop()


# ------------------------------------------------------------------------------------------------ #
class SparkSessionPool:
    """Manages a pool of Spark and Spark NLP sessions with retry logic and configuration.

    This class provides mechanisms for creating and managing Spark and Spark NLP sessions
    with configurable settings. It ensures efficient reuse of sessions and integrates
    cleanup via shutdown handlers.

    Args:
        spark_config (Dict): Configuration for Spark, including memory allocation,
            Parquet block size, and retry attempts.

    Properties:
        spark (SparkSession): Lazily initializes and returns a Spark session.
        sparknlp (SparkSession): Lazily initializes and returns a Spark NLP session.

    Methods:
        stop: Stops any active Spark or Spark NLP sessions.
        get_spark_session: Retrieves a Spark session based on the specified type.
    """

    def __init__(self, spark_config: Dict) -> None:
        self._spark_config = NestedNamespace(spark_config)
        self._spark = None  # Spark Session
        self._sparknlp = None  # Spark NLP Session
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @property
    def spark(self) -> SparkSession:
        """Lazily initializes and returns a Spark session.

        Returns:
            SparkSession: The Spark session.
        """
        if self._spark is None:
            self._spark = self._get_or_create(nlp=False)
        return self._spark

    @property
    def sparknlp(self) -> SparkSession:
        """Lazily initializes and returns a Spark NLP session.

        Returns:
            SparkSession: The Spark NLP session.
        """
        if self._sparknlp is None:
            self._sparknlp = self._get_or_create(nlp=True)
        return self._sparknlp

    def stop(self) -> None:
        """Stops any active Spark or Spark NLP sessions."""
        if self._sparknlp is not None:
            self._sparknlp.stop()
            self._sparknlp = None
        elif self._spark is not None:
            self._spark.stop()
            self._spark = None

    def get_spark_session(
        self, spark_session_type: SparkSessionType = SparkSessionType.SPARK
    ) -> SparkSession:
        """Retrieves a Spark session based on the specified type.

        Args:
            spark_session_type (SparkSessionType): Type of Spark session to retrieve.
                Defaults to SparkSessionType.SPARK.

        Returns:
            SparkSession: The requested Spark session.
        """
        if spark_session_type == SparkSessionType.SPARK:
            return self.spark
        else:
            return self.sparknlp

    def _get_or_create(self, nlp: bool = False) -> SparkSession:
        """Creates or retrieves a Spark or Spark NLP session.

        Args:
            nlp (bool): If True, creates a Spark NLP session. Defaults to False.

        Returns:
            SparkSession: The created or retrieved Spark session.
        """
        if not nlp:
            spark_session = self._create_session(
                memory=self._spark_config.memory,
                parquet_block_size=self._spark_config.parquet_block_size,
                retries=self._spark_config.retries,
            )
        else:
            spark_session = self._create_nlp_session(
                memory=self._spark_config.memory,
                parquet_block_size=self._spark_config.parquet_block_size,
                retries=self._spark_config.retries,
            )
        atexit.register(shutdown, spark_session)
        return spark_session

    def _create_session(
        self, memory: str, parquet_block_size: int, retries: int
    ) -> SparkSession:
        """Creates a Spark session with the specified configuration.

        Args:
            memory (str): Memory allocation for the session.
            parquet_block_size (int): Parquet block size for the session.
            retries (int): Number of retry attempts for session creation.

        Returns:
            SparkSession: The created Spark session.

        Raises:
            RuntimeError: If retries are exhausted without successful session creation.
        """
        self._logger.debug("Creating a Spark session.")
        attempts = 0
        error = None
        while attempts < retries:
            try:
                log4j_conf_path = "file:" + os.path.abspath("log4j.properties")
                self._logger.debug(
                    f"Creating a Spark session. log4j Configuration: {log4j_conf_path}"
                )
                spark = (
                    SparkSession.builder.appName("appvocai-discover")
                    .master("local[*]")
                    .config("spark.sql.session.timeZone", "UTC")
                    .config("spark.driver.memory", memory)
                    .config("spark.executor.memory", memory)
                    .config("spark.sql.parquet.block.size", parquet_block_size)
                    .config("spark.sql.parquet.outputTimestampType", "TIMESTAMP_MICROS")
                    .config("spark.sql.execution.arrow.pyspark.enabled", "true")
                    .config(
                        "spark.sql.execution.arrow.pyspark.fallback.enabled", "false"
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
                spark.sparkContext.setLogLevel("ERROR")
                return spark
            except Exception as e:
                attempts += 1
                error = e
                self._logger.warning(
                    f"Error creating Spark session: {e}. Retrying {attempts} of {retries}..."
                )
                time.sleep(2**attempts)

        msg = f"Retries exhausted. Unable to create Spark session.\n{error}"
        self._logger.exception(msg)
        raise RuntimeError(msg)

    def _create_nlp_session(
        self, memory: str, parquet_block_size: int, retries: int
    ) -> SparkSession:
        """Creates a Spark NLP session with the specified configuration.

        Args:
            memory (str): Memory allocation for the session.
            parquet_block_size (int): Parquet block size for the session.
            retries (int): Number of retry attempts for session creation.

        Returns:
            SparkSession: The created Spark NLP session.

        Raises:
            RuntimeError: If retries are exhausted without successful session creation.
        """
        self._logger.debug("Creating a Spark NLP session.")
        attempts = 0
        error = None
        while attempts < retries:
            try:
                log4j_conf_path = "file:" + os.path.abspath("log4j.properties")
                self._logger.debug(
                    f"Creating a Spark NLP session. log4j Configuration: {log4j_conf_path}"
                )
                spark = (
                    SparkSession.builder.appName("appvocai-discover-nlp")
                    .master("local[*]")
                    .config("spark.sql.session.timeZone", "UTC")
                    .config("spark.driver.memory", memory)
                    .config("spark.executor.memory", memory)
                    .config("spark.sql.parquet.block.size", parquet_block_size)
                    .config("spark.sql.execution.arrow.pyspark.enabled", "true")
                    .config(
                        "spark.sql.execution.arrow.pyspark.fallback.enabled", "false"
                    )
                    .config(
                        "spark.serializer", "org.apache.spark.serializer.KryoSerializer"
                    )
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
                spark.sparkContext.setLogLevel("ERROR")
                return spark
            except Exception as e:
                attempts += 1
                error = e
                self._logger.warning(
                    f"Error creating Spark NLP session: {e}. Retrying {attempts} of {retries}..."
                )
                time.sleep(2**attempts)

        msg = f"Retries exhausted. Unable to create Spark NLP session.\n{error}"
        self._logger.exception(msg)
        raise RuntimeError(msg)
