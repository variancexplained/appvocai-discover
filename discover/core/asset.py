#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Discover                                                                   #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /discover/core/asset.py                                                             #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-discover                               #
# ------------------------------------------------------------------------------------------------ #
# Created    : Monday December 23rd 2024 12:36:03 pm                                               #
# Modified   : Monday December 23rd 2024 12:47:32 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Core Asset Module"""
from __future__ import annotations

from enum import Enum
from typing import Any

# ------------------------------------------------------------------------------------------------ #


class AssetType(Enum):
    """
    Enum representing different types of assets in a machine learning workflow.

    Each asset type is associated with a string identifier (`value`) and a human-readable label (`label`).

    Attributes:
        DATASET: Represents a dataset asset.
        MODEL: Represents a model asset.
        EXPERIMENT: Represents an experiment asset.
        INFERENCE: Represents an inference asset.

    Args:
        value (str): The string identifier for the asset type.
        label (str): The human-readable label for the asset type.
    """

    DATASET = ("dataset", "Dataset")
    MODEL = ("model", "Model")
    EXPERIMENT = ("experiment", "Experiment")
    INFERENCE = ("inference", "Inference")

    def __new__(cls, value: str, label: str) -> Any:
        """
        Create a new instance of AssetType.

        Args:
            value (str): The string identifier for the asset type.
            label (str): The human-readable label for the asset type.

        Returns:
            AssetType: An instance of the AssetType enum.
        """
        obj = object.__new__(cls)
        obj._value_ = value  # Set the Enum value
        obj._label = label  # Set the custom label
        return obj

    @property
    def label(self) -> str:
        """
        Returns the human-readable label for the asset type.

        Returns:
            str: The label associated with the asset type.
        """
        return self._label
