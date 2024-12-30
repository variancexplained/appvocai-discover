#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Discover                                                                   #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /tests/test_assets/test_dataset/test_identity.py                                    #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-discover                               #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday December 27th 2024 08:21:27 pm                                               #
# Modified   : Monday December 30th 2024 04:23:17 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import inspect
import logging
from datetime import datetime

import pytest

from discover.asset.base.atype import AssetType
from discover.asset.dataset.builder.identity import DatasetPassportBuilder
from discover.asset.dataset.component.identity import DatasetPassport
from discover.core.flow import PhaseDef, TestStageDef

# ------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------ #
# pylint: disable=missing-class-docstring, line-too-long
# mypy: ignore-errors
# ------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)
# ------------------------------------------------------------------------------------------------ #
double_line = f"\n{100 * '='}"
single_line = f"\n{100 * '-'}"
# ------------------------------------------------------------------------------------------------ #


@pytest.mark.passport
@pytest.mark.dataset
class TestDatasetPassport:  # pragma: no cover
    # ============================================================================================ #
    def test_builder(self, caplog) -> None:
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #
        builder = DatasetPassportBuilder()
        passport = (
            builder.phase(PhaseDef.TESTING)
            .stage(TestStageDef.UNIT_TEST)
            .name("test_dataset_passport_builder")
            .build()
            .passport
        )
        assert isinstance(passport, DatasetPassport)
        assert isinstance(passport.asset_id, str)
        assert isinstance(passport.asset_type, AssetType)
        assert passport.phase == PhaseDef.TESTING
        assert passport.stage == TestStageDef.UNIT_TEST
        assert passport.name == "test_dataset_passport_builder"
        assert isinstance(passport.description, str)
        assert isinstance(passport.name, str)
        assert isinstance(passport.version, str)
        assert isinstance(passport.created, datetime)

        passport2 = (
            builder.phase(PhaseDef.TESTING)
            .stage(TestStageDef.PERFORMANCE_TEST)
            .name("test_dataset_passport_builder_source_parent")
            .source(passport)
            .parent(passport)
            .build()
            .passport
        )

        assert isinstance(passport2.source, DatasetPassport)
        assert isinstance(passport2.parent, DatasetPassport)
        logging.info(passport2)

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)

    # ============================================================================================ #
    def test_validation(self, caplog) -> None:
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #
        builder = DatasetPassportBuilder()

        with pytest.raises(AttributeError):
            _ = (
                builder.phase(PhaseDef.BOGUS)
                .stage(TestStageDef.UNIT_TEST)
                .name("test_dataset_passport_builder")
                .build()
                .passport
            )

        with pytest.raises(AttributeError):
            _ = (
                builder.phase(PhaseDef.TESTING)
                .stage(TestStageDef.BOGUS)
                .name("test_dataset_passport_builder")
                .build()
                .passport
            )
        with pytest.raises(ValueError):
            _ = builder.build().passport

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)
