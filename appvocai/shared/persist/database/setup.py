#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Discover                                                                   #
# Version    : 0.1.0                                                                               #
# Python     : 3.12.3                                                                              #
# Filename   : /appvocai/shared/persist/database/setup.py                                          #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-discover                               #
# ------------------------------------------------------------------------------------------------ #
# Created    : Tuesday May 28th 2024 03:37:01 pm                                                   #
# Modified   : Monday September 9th 2024 09:41:26 am                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Database Setup Module"""
from appvocai.orchestration.base import Task
from appvocai.shared.dependency.container import AppInsightContainer
from appvocai.shared.persist.database.dba import SQLiteDBA
from dependency_injector.wiring import Provide, inject


# ------------------------------------------------------------------------------------------------ #
class CreateDatabasesTask(Task):
    @inject
    def __init__(self, dba: SQLiteDBA = Provide[AppInsightContainer.db.admin]) -> None:
        self._dba = dba()

    def execute(self) -> None:
        try:
            self._dba.create_table(tablename="profile")
        except Exception as e:
            msg = f"Exception occurred while creating dataset. \n{e} "
            self.logger.exception(msg)
            raise
        print("Database has been setup.")
