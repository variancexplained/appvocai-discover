#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Discover                                                                   #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /discover/container.py                                                              #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-discover                               #
# ------------------------------------------------------------------------------------------------ #
# Created    : Monday September 9th 2024 04:54:25 pm                                               #
# Modified   : Tuesday September 24th 2024 02:22:47 am                                             #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""AppVoCAI-Discover Dependency Container"""
from __future__ import annotations

import logging
import logging.config  # pragma: no cover

from dependency_injector import containers, providers

from discover.infra.config.reader import ConfigReader
from discover.infra.database.sqlite import SQLiteDB, SQLiteDBA
from discover.infra.frameworks.spark.nlp import SparkSessionPoolNLP
from discover.infra.frameworks.spark.standard import SparkSessionPoolStandard
from discover.infra.identity.idgen import IDGen
from discover.infra.repo.profile import ProfileRepo

# ------------------------------------------------------------------------------------------------ #


# ------------------------------------------------------------------------------------------------ #
#                                      LOGGING CONTAINER                                           #
# ------------------------------------------------------------------------------------------------ #
class LoggingContainer(containers.DeclarativeContainer):

    config = providers.Configuration()

    main = providers.Resource(
        logging.config.dictConfig,
        config=config.logging,
    )


# ------------------------------------------------------------------------------------------------ #
#                                   SPARK CONTAINER                                                #
# ------------------------------------------------------------------------------------------------ #
class SparkContainer(containers.DeclarativeContainer):

    standard = providers.Singleton(SparkSessionPoolStandard)
    nlp = providers.Singleton(SparkSessionPoolNLP)


# ------------------------------------------------------------------------------------------------ #
#                                   IDGEN CONTAINER                                                #
# ------------------------------------------------------------------------------------------------ #
class IDGenContainer(containers.DeclarativeContainer):

    gen = providers.Singleton(IDGen)


# ------------------------------------------------------------------------------------------------ #
#                                   REPO CONTAINER                                                 #
# ------------------------------------------------------------------------------------------------ #
class RepoContainer(containers.DeclarativeContainer):

    db = providers.DependenciesContainer()

    profile = providers.Singleton(ProfileRepo, database=db.sqlite)


# ------------------------------------------------------------------------------------------------ #
#                                 DATABASE CONTAINER                                               #
# ------------------------------------------------------------------------------------------------ #
class DatabaseContainer(containers.DeclarativeContainer):

    config = providers.Configuration()

    sqlite = providers.Singleton(
        SQLiteDB,
        connection_string=config.database.sqlite.url,
        location=config.database.sqlite.filepath,
    )

    admin = providers.Singleton(SQLiteDBA, database=sqlite)


# ------------------------------------------------------------------------------------------------ #
#                                    APPLICATION CONTAINER                                         #
# ------------------------------------------------------------------------------------------------ #
class DiscoverContainer(containers.DeclarativeContainer):

    # Provide the Config class instance dynamically
    config = providers.Singleton(ConfigReader)

    # Provide the actual config dictionary by calling get_config()
    config_data = providers.Factory(
        lambda: DiscoverContainer.config().get_config(namespace=False),
    )

    # Configure the logs by injecting the config data
    logs = providers.Container(LoggingContainer, config=config_data)

    # Configure the database by injecting the config data
    db = providers.Container(DatabaseContainer, config=config_data)

    # Configure the repository by injecting the database.
    repo = providers.Container(RepoContainer, db=db)

    # Configure the spark container with configuration.
    spark = providers.Container(SparkContainer)

    # Configure the id generator container.
    id = providers.Container(IDGenContainer)
