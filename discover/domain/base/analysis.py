#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Discover                                                                   #
# Version    : 0.1.0                                                                               #
# Python     : 3.12.3                                                                              #
# Filename   : /discover/domain/service/base/analysis.py                                           #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-discover                               #
# ------------------------------------------------------------------------------------------------ #
# Created    : Tuesday June 4th 2024 11:21:31 pm                                                   #
# Modified   : Tuesday September 10th 2024 07:36:49 pm                                             #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Base module for the analysis package """
import logging
import shelve
from abc import ABC

from discover.shared.config.env import EnvManager


# ------------------------------------------------------------------------------------------------ #
#                                       ANALYSIS                                                   #
# ------------------------------------------------------------------------------------------------ #
class Analysis(ABC):
    """Abstract base class for analysis classes

    Args:
        repo_cls: (Type[ReviewRepo]): Repository of datasets.
    """

    def __init__(self) -> None:
        super().__init__()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def reset_cache(self):
        # Get the current environment
        env = EnvManager().get_environment()
        # Set the shelve file
        shelf_file = f"cache/{env}/cache"
        # Check if the shelve file exists
        try:
            # Open the shelve file
            with shelve.open(shelf_file) as cache:
                # Get the class name
                class_name = type(self).__name__
                # Iterate over cache keys
                keys_to_remove = [key for key in cache.keys() if class_name in key]
                # Remove keys from the cache
                for key in keys_to_remove:
                    del cache[key]
        except Exception as e:
            msg = f"Exception occurred in reset_cache.\n{e}"
            self.logger.exception(msg)
            raise RuntimeError(msg)