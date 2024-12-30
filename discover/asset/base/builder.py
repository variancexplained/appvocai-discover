#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Discover                                                                   #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /discover/asset/base/builder.py                                                     #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-discover                               #
# ------------------------------------------------------------------------------------------------ #
# Created    : Wednesday December 18th 2024 03:01:02 pm                                            #
# Modified   : Sunday December 29th 2024 05:07:50 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Base Module for the Asset Dimension"""
from __future__ import annotations

from abc import ABC, abstractmethod

from discover.asset.base.asset import Asset


# ------------------------------------------------------------------------------------------------ #
#                                   ASSET BUILDER                                                  #
# ------------------------------------------------------------------------------------------------ #
class AssetBuilder(ABC):
    """
    Abstract base class for building assets with phases, stages, and persistence
    configurations.
    """

    @abstractmethod
    def reset(self) -> None:
        """
        Resets the builder to be ready to construct another Dataset object.
        """
        pass

    @abstractmethod
    def build(self) -> Asset:
        """
        Builds and returns the final Dataset object based on the provided configurations.

        Returns:
            Dataset: The fully constructed dataset.
        """
        pass
