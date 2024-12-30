#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Discover                                                                   #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /discover/asset/dataset/__init__.py                                                 #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-discover                               #
# ------------------------------------------------------------------------------------------------ #
# Created    : Monday September 9th 2024 04:21:25 pm                                               #
# Modified   : Sunday December 29th 2024 02:48:56 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Dataset Init Module for Dataset Shared Classes"""
from enum import Enum

# ------------------------------------------------------------------------------------------------ #
#                                     FILE FORMATS                                                 #
# ------------------------------------------------------------------------------------------------ #


class FileFormat(Enum):
    CSV = "csv"
    PARQUET = "parquet"


# ------------------------------------------------------------------------------------------------ #
#                                   DATAFRAME TYPE                                                 #
# ------------------------------------------------------------------------------------------------ #
class DFType(Enum):

    PANDAS = "pandas"
    SPARK = "spark"
