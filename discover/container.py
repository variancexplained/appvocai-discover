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
# Modified   : Wednesday December 18th 2024 06:50:03 am                                            #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""AppVoCAI-Discover Dependency Container"""
# %%
from __future__ import annotations

import logging
import logging.config

from dependency_injector import containers, providers

from discover.infra.config.app import AppConfigReader
from discover.infra.service.spark.session import SparkSessionPool

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

    config = providers.Configuration()

    session_pool = providers.Singleton(SparkSessionPool, spark_config=config.spark)


# ------------------------------------------------------------------------------------------------ #
#                               FILE PERSISTENCE CONTAINER                                         #
# ------------------------------------------------------------------------------------------------ #
class FilePersistenceContainer(containers.DeclarativeContainer):

    from discover.infra.persistence.dal.fileset.centralized import CentralizedFilesetDAL
    from discover.infra.persistence.dal.fileset.distributed import DistributedFilesetDAL
    from discover.infra.persistence.dal.fileset.location import FilesetLocationService
    from discover.infra.persistence.repo.fileset import FilesetRepo

    config = providers.Configuration()

    spark = providers.DependenciesContainer()

    file_location_service = providers.Singleton(
        FilesetLocationService, workspace=config.workspace
    )

    # Centralized File System File Access Object
    fao_cfs = providers.Singleton(
        CentralizedFilesetDAL,
        storage_config=config.persistence.data.files.centralized,
        location_service=file_location_service,
    )

    # Distributed File System File Access Object
    fao_dfs = providers.Singleton(
        DistributedFilesetDAL,
        storage_config=config.persistence.data.files.distributed,
        location_service=file_location_service,
        session_pool=spark.session_pool,
    )

    # Fileset Repository
    fileset_repo = providers.Singleton(
        FilesetRepo,
        fao_cfs=fao_cfs,
        fao_dfs=fao_dfs,
        location_service=file_location_service,
        partitioned=config.persistence.data.files.partitioned,
    )


# ------------------------------------------------------------------------------------------------ #
#                          OBJECT PERSISTENCE CONTAINER                                            #
# ------------------------------------------------------------------------------------------------ #
class ObjectPersistenceContainer(containers.DeclarativeContainer):

    from discover.infra.persistence.dal.object.dataset import DatasetDAL
    from discover.infra.persistence.dal.object.location import DALLocationService
    from discover.infra.persistence.repo.dataset import DatasetRepo

    config = providers.Configuration()

    fileset_repo = providers.DependenciesContainer()

    dataset_location_service = providers.Singleton(
        DALLocationService,
        workspace=config.workspace,
        location=config.persistence.data.datasets.location,
    )

    # Data Access Layer
    dal = providers.Singleton(DatasetDAL, location_service=dataset_location_service)

    # Dataset Repository
    dataset_repo = providers.Singleton(
        DatasetRepo,
        dataset_dal=dal,
        fileset_repo=fileset_repo,
    )


# ------------------------------------------------------------------------------------------------ #
#                                    APPLICATION CONTAINER                                         #
# ------------------------------------------------------------------------------------------------ #
class DiscoverContainer(containers.DeclarativeContainer):

    # Provide the Config class instance dynamically
    config_reader = providers.Singleton(AppConfigReader)

    # Provide the actual config dictionary by calling get_config()
    config = providers.Factory(
        lambda: DiscoverContainer.config_reader().get_config(namespace=False),
    )

    # Configure the logs by injecting the config data
    logs = providers.Container(LoggingContainer, config=config)

    # Configure spark session pool
    spark = providers.Container(SparkContainer, config=config)

    # File Persistence Container
    file_persistence = providers.Container(
        FilePersistenceContainer, spark=spark, config=config
    )

    # Object Persistence Container
    object_persistence = providers.Container(
        ObjectPersistenceContainer,
        config=config,
        fileset_repo=file_persistence.fileset_repo,
    )


# ------------------------------------------------------------------------------------------------ #
# if __name__ == "__main__":
#     container = DiscoverContainer()
#     container.init_resources()

#     assert container.config()["workspace"] == "workspace/test"
#     logging.debug("Test Log message")
