#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppInsight                                                                          #
# Version    : 0.1.0                                                                               #
# Python     : 3.12.3                                                                              #
# Filename   : /appinsight/utils/format.py                                                         #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appinsight                                      #
# ------------------------------------------------------------------------------------------------ #
# Created    : Sunday June 2nd 2024 09:35:10 pm                                                    #
# Modified   : Monday June 3rd 2024 12:22:03 am                                                    #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import pandas as pd
from pandarallel import pandarallel

# ------------------------------------------------------------------------------------------------ #
pandarallel.initialize(progress_bar=False, nb_workers=8, verbose=0)


# ------------------------------------------------------------------------------------------------ #
def format_numerics(df: pd.DataFrame) -> pd.DataFrame:
    """Returns the resulting dataframe with thousands separators."""

    def show_thousands_separator(x):  # pragma: no cover
        """Formats an numbers with thousands separator."""
        try:
            if is_numeric(x):
                return f"{x:,}"
            else:
                return x
        except Exception:
            return x

    def is_numeric(x) -> bool:
        try:
            pd.to_numeric(x, errors="raise")
            return True
        except Exception:
            return False

    df = df.apply(show_thousands_separator)
    return df
