#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Discover                                                                   #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /discover/infra/identity/idxgen.py                                                  #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-discover                               #
# ------------------------------------------------------------------------------------------------ #
# Created    : Wednesday September 4th 2024 09:51:14 pm                                            #
# Modified   : Saturday September 14th 2024 06:48:26 am                                            #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
# %%
# ------------------------------------------------------------------------------------------------ #
import logging
import os
import shelve
from datetime import datetime

from discover.domain.base.identity import IDXGen
from discover.infra.config.config import Config


class RunIDXGen(IDXGen):
    """
    A class that generates a sequential index value based on the current date and the owner (either an instance or a class),
    persisting it using `shelve`. The index is reset daily and separately maintained per owner.

    Attributes:
    -----------
    __directory_key : str
        A private class attribute that holds the name of the environment variable which contains
        the directory path for storing the shelve file.

    _logger : logging.Logger
        A logger instance used to log information and errors.

    _shelve_file : str
        The file path where the shelve file is stored, determined from the environment variable.

    Methods:
    --------
    get_next_id(owner) -> str
        Generates the next sequential ID in the format 'OwnerClassName-YYYYMMDD-INDEX' or
        'OwnerInstanceName-YYYYMMDD-INDEX', depending on whether the owner is a class or an instance.
    """

    def __init__(self, config_cls: type[Config] = Config) -> None:
        """
        Initializes the IDXGen instance by setting up the logger and determining the shelve file path.

        Raises:
        -------
        Exception
            If there is an issue with setting up the shelve file path, logs the error and re-raises the exception.
        """
        self._config = config_cls()
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        try:
            ops_config = self._config.get_config(section="ops")
            self._shelve_file = ops_config.idxgen.runid
            os.makedirs(os.path.dirname(self._shelve_file), exist_ok=True)
        except Exception as e:
            self._logger.error(f"Failed to set up shelve file path: {e}")
            raise

    @property
    def today(self) -> str:
        """Returns the current date as a string in YYYYMMDD format."""
        return datetime.now().strftime("%Y%m%d")

    def get_next_id(self, owner: object) -> str:
        """
        Generates the next sequential ID for the provided owner. If the owner is a class, the ID format is
        'ClassName-YYYYMMDD-INDEX'. If the owner is an instance, the format is 'InstanceName-YYYYMMDD-INDEX'.

        Parameters:
        -----------
        owner : object
            The owner object or class for which the ID is being generated.

        Returns:
        --------
        str
            The next ID in the format 'OwnerName-YYYYMMDD-INDEX', where OwnerName is either the class or instance name.
        """
        try:
            # Check if the owner is a class or an instance
            if isinstance(owner, type):
                owner_name = owner.__name__  # Class name
            else:
                owner_name = owner.__class__.__name__  # Instance's class name

            with shelve.open(self._shelve_file) as db:
                key = f"{owner_name}_last_date"
                last_date = db.get(key, None)
                if last_date == self.today:
                    last_idx = db.get(f"{owner_name}_idx", 0)
                    next_idx = int(last_idx) + 1
                else:
                    next_idx = 1
                    db[key] = self.today
                    self._logger.info(
                        f"Date changed, index reset to: {next_idx} for new date: {self.today}"
                    )

                db[f"{owner_name}_idx"] = next_idx
                return f"{owner_name}-{self.today}-{next_idx}"

        except Exception as e:
            self._logger.error(f"Failed to generate next ID: {e}")
            raise
