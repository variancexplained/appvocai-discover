#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Discover                                                                   #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /discover/flow/task/clean/dimension/unique.py                                       #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-discover                               #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday November 22nd 2024 01:08:57 am                                               #
# Modified   : Thursday December 19th 2024 01:40:50 pm                                             #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from typing import Literal, Type, Union

from discover.flow.task.clean.dimension.base import NominalAnomaly
from discover.flow.task.clean.strategy.nominal import NominalStrategyFactory


# ------------------------------------------------------------------------------------------------ #
class DetectOrRepairUniquenessTask(NominalAnomaly):
    """
    Class for detecting or repairing uniqueness anomalies in nominal data.

    This class extends the `NominalAnomaly` class and provides functionality for
    detecting and repairing uniqueness anomalies in nominal columns, ensuring that
    values in the specified column are unique or meet certain uniqueness criteria.

    Args:
        column (list[str]): A list of columns in the dataset to apply anomaly detection. The values in these columns should be unique.
        new_column (str): The name of the new column that will store the results of the uniqueness detection/repair.
        mode (str, optional): The mode of operation, either "detect" or "repair". Defaults to "detect".
        strategy_factory_cls (Type[NominalStrategyFactory], optional): The class for the strategy factory to use. Defaults to `NominalStrategyFactory`.
        detect_strategy (str, optional): The strategy to use for detecting uniqueness anomalies. Defaults to "unique".
        repair_strategy (str, optional): The strategy to use for repairing detected uniqueness anomalies. Defaults to "unique".
        threshold (Union[float, int], optional): The threshold value for anomaly detection, either as a count or proportion. Defaults to None.
        threshold_type (Literal["count", "proportion"], optional): Specifies if the threshold is based on a count or proportion. Defaults to None.
        unit (Literal["word", "character"], optional): Specifies whether to apply the threshold to words or characters. Defaults to None.

    Attributes:
        column (list[str]): The list of columns in the dataset to apply anomaly detection. The values in these columns should be unique.
        new_column (str): The name of the new column that will store the results of the uniqueness detection/repair.
        mode (str): The mode of operation, either "detect" or "repair".
        strategy_factory_cls (Type[NominalStrategyFactory]): The class for the strategy factory to use.
        detect_strategy (str): The strategy to use for detecting uniqueness anomalies.
        repair_strategy (str): The strategy to use for repairing detected uniqueness anomalies.
        threshold (Union[float, int]): The threshold value for anomaly detection, either as a count or proportion.
        threshold_type (str): Specifies if the threshold is based on a count or proportion.
        unit (str): Specifies whether to apply the threshold to words or characters.
    """

    def __init__(
        self,
        column: list[str],
        new_column: str,
        mode: str = "detect",
        strategy_factory_cls: Type[NominalStrategyFactory] = NominalStrategyFactory,
        detect_strategy: str = "unique",
        repair_strategy: str = "unique",
        threshold: Union[float, int] = None,
        threshold_type: Literal["count", "proportion"] = None,
        unit: Literal["word", "character"] = None,
        **kwargs,
    ) -> None:
        super().__init__(
            column=column,
            new_column=new_column,
            mode=mode,
            strategy_factory_cls=strategy_factory_cls,
            detect_strategy=detect_strategy,
            repair_strategy=repair_strategy,
            threshold=threshold,
            threshold_type=threshold_type,
            unit=unit,
            **kwargs,
        )
