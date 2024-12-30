#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Discover                                                                   #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /discover/asset/dataset/base.py                                                     #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-discover                               #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday December 27th 2024 09:21:00 pm                                               #
# Modified   : Monday December 30th 2024 03:26:26 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Dataset Base Module"""

from pydantic.dataclasses import dataclass

from discover.asset.base.builder import AssetBuilder
from discover.asset.base.component import AssetComponent


# ------------------------------------------------------------------------------------------------ #
#                               DATASET COMPONENT                                                  #
# ------------------------------------------------------------------------------------------------ #
@dataclass(config=dict(arbitrary_types_allowed=True))
class DatasetComponent(AssetComponent):
    pass


# ------------------------------------------------------------------------------------------------ #
#                            DATASET COMPONENT BUILDER                                             #
# ------------------------------------------------------------------------------------------------ #
class DatasetComponentBuilder(AssetBuilder):
    pass
