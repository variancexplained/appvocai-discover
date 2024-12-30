#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Discover                                                                   #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /discover/infra/utils/file/info.py                                                  #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-discover                               #
# ------------------------------------------------------------------------------------------------ #
# Created    : Wednesday December 25th 2024 10:50:08 pm                                            #
# Modified   : Monday December 30th 2024 03:36:49 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""File / Directory Stats Module"""
import os
from datetime import datetime
from typing import Union

from pydantic.dataclasses import dataclass

from discover.core.data_structure import DataClass
from discover.infra.utils.data.format import format_size
from discover.infra.utils.date_time.format import ThirdDateFormatter

# ------------------------------------------------------------------------------------------------ #
d84mtr = ThirdDateFormatter()


# ------------------------------------------------------------------------------------------------ #
class FileTypeDetector:
    """A class to detect the file type based on magic numbers."""

    MAGIC_NUMBERS = {
        "Parquet": (b"PAR1", None),  # Footer-based detection
        "pickle": (b"\x80\x04", None),  # Pickle protocol magic bytes
        "Csv": None,  # No magic number for CSV, fallback required
        "Feather": (b"FEA1", None),  # Feather magic number
        "HDF5": (b"\x89HDF", None),  # HDF5 magic number
    }

    def get_file_type(self, filepath: str) -> str:
        """Detect the file type using magic numbers.

        Returns:
            str: The detected file type or 'Unknown' if no match is found.
        """
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"The file {filepath} does not exist.")

        try:
            with open(filepath, "rb") as file:
                header = file.read(8)  # Read enough bytes to check multiple types

                # Check footer for formats like Parquet
                file.seek(-4, os.SEEK_END)
                footer = file.read(4)

                for file_type, magic in self.MAGIC_NUMBERS.items():
                    if not magic:  # Special handling for CSV
                        continue
                    header_magic, footer_magic = magic
                    if (header_magic and header.startswith(header_magic)) or (
                        footer_magic and footer == footer_magic
                    ):
                        return file_type

                # CSV fallback: check for text-like content
                file.seek(0)
                if self._is_csv(file):
                    return "Csv"

        except Exception as e:
            raise RuntimeError(f"Error detecting file type: {e}")

        return "Unknown"

    def _is_csv(self, file) -> bool:
        """Fallback for detecting CSV files based on plain text."""
        try:
            sample = file.read(1024).decode("utf-8", errors="ignore")
            return "," in sample or "\n" in sample  # Basic CSV characteristics
        except Exception:
            return False


# ------------------------------------------------------------------------------------------------ #
class ParquetFileDetector:
    """
    Detects whether a given path is a Parquet file or a directory containing Parquet files.

    Methods:
        is_parquet(path: str) -> bool:
            Determines if the given path is a Parquet file or a directory containing Parquet files.

        is_parquet_file(filepath: str) -> bool:
            Checks if a file is a Parquet file using its magic number.

        is_parquet_directory(directory: str) -> bool:
            Recursively checks a directory and its subdirectories for Parquet files,
            quitting early once a valid file is found.

    Args:
        None
    """

    def is_parquet(self, path: str) -> bool:
        """
        Determines if the given path is a Parquet file or a directory containing Parquet files.

        Args:
            path (str): The path to a file or directory to check.

        Returns:
            bool: True if the path is a Parquet file or a directory containing Parquet files, False otherwise.
        """
        if os.path.isfile(path):
            return self.is_parquet_file(filepath=path)
        else:
            return self.is_parquet_directory(directory=path)

    def is_parquet_file(self, filepath: str) -> bool:
        """
        Checks if a file is a Parquet file using its magic number.

        Args:
            filepath (str): The path to the file to check.

        Returns:
            bool: True if the file is a valid Parquet file, False otherwise.
        """
        try:
            with open(filepath, "rb") as f:
                # Check the first 4 bytes (header)
                magic_start = f.read(4)
                # Check the last 4 bytes (footer)
                f.seek(-4, os.SEEK_END)
                magic_end = f.read(4)
                return magic_start == b"PAR1" and magic_end == b"PAR1"
        except Exception:
            return False

    def is_parquet_directory(self, directory: str) -> bool:
        """
        Recursively checks a directory and its subdirectories for Parquet files,
        quitting early once a valid file is found.

        Args:
            directory (str): The path to the directory to check.

        Returns:
            bool: True if the directory contains at least one valid Parquet file, False otherwise.
        """
        try:
            for root, _, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    if self.is_parquet_file(filepath=file_path):
                        return True  # Early quit: found a valid Parquet file
            return False  # No valid Parquet files found
        except Exception as e:
            print(f"Error while checking directory {directory}: {e}")
            return False


# ------------------------------------------------------------------------------------------------ #
@dataclass(config=dict(arbitrary_types_allowed=True))
class FileMeta(DataClass):
    """Encapsulates File level metadata."""

    filename: str
    filepath: str
    file_type: str
    isdir: bool
    file_count: int
    created: str
    accessed: str
    modified: str
    size: int


# ------------------------------------------------------------------------------------------------ #
class FileInfo:
    """Utility class for retrieving statistics and metadata about files and directories.

    This class provides methods to calculate the size, creation time, last access time,
    last modified time, and file/directory counts. It supports both files and directories,
    handling recursive operations for directories when necessary.
    """

    def get_file_info(self, filepath: str) -> FileMeta:
        ftd = FileTypeDetector()
        file_type = ftd.get_file_type(filepath)

        return FileMeta(
            filename=os.path.basename(filepath),
            filepath=filepath,
            file_type=file_type,
            isdir=self.isdir(filepath=filepath),
            file_count=self.get_count(filepath=filepath),
            created=self.file_created(filepath=filepath),
            accessed=self.file_last_accessed(filepath=filepath),
            modified=self.file_last_modified(filepath=filepath),
            size=self.get_size(path=filepath, in_bytes=True),
        )

    def isdir(self, filepath: str) -> bool:
        """Returns True if the filepath is a directory

        Args:
            filepath (str): The path to the file or directory.

        Returns:
            True if the filepath is a directory. False otherwise.
        """
        return os.path.isdir(filepath)

    def get_count(self, filepath: str) -> int:
        """Gets the count of items in the specified file or directory.

        Args:
            filepath (str): The path to the file or directory.

        Returns:
            int: 1 if the path is a file, or the total number of files and directories
            in the specified directory (recursively).

        Raises:
            ValueError: If the filepath is neither a file nor a directory.
        """
        if os.path.isfile(filepath):
            return 1
        elif os.path.isdir(filepath):
            return self._get_directory_count(directory=filepath)
        else:
            raise ValueError(f"The filepath {filepath} is not valid.")

    def file_created(self, filepath: str) -> datetime:
        """Gets the creation time of the specified file.

        Args:
            filepath (str): The path to the file.

        Returns:
            datetime: The creation time of the file in HTTP date format.
        """
        stat_info = os.stat(filepath)
        ctime = datetime.fromtimestamp(stat_info.st_ctime)
        return d84mtr.to_HTTP_format(dt=ctime)

    def file_last_accessed(self, filepath: str) -> datetime:
        """Gets the last access time of the specified file.

        Args:
            filepath (str): The path to the file.

        Returns:
            datetime: The last access time of the file in HTTP date format.
        """
        stat_info = os.stat(filepath)
        atime = datetime.fromtimestamp(stat_info.st_atime)
        return d84mtr.to_HTTP_format(dt=atime)

    def file_last_modified(self, filepath: str) -> datetime:
        """Gets the last modified time of the specified file.

        Args:
            filepath (str): The path to the file.

        Returns:
            datetime: The last modified time of the file in HTTP date format.
        """
        stat_info = os.stat(filepath)
        mtime = datetime.fromtimestamp(stat_info.st_mtime)
        return d84mtr.to_HTTP_format(dt=mtime)

    def get_size(self, path: str, in_bytes: bool = True) -> Union[int, str]:
        """Gets the size of the specified file or directory in a human-readable format.

        Args:
            path (str): The path to the file or directory.
            in_bytes (bool): Whether to return size in bytes as integer.

        Returns:
            Union[int,str]: The size of the file or directory in a formatted string (e.g., '1.23 MB')
                if in_bytes is False, otherwise an integer is returned.

        Raises:
            ValueError: If the path is neither a file nor a directory.
        """
        if os.path.isfile(path):
            size = self._get_file_size(filepath=path)
        elif os.path.isdir(path):
            size = self._get_directory_size(directory=path)
        else:
            raise ValueError(f"The path {path} is not valid.")
        if in_bytes:
            return size
        else:
            return format_size(size_in_bytes=size)

    def _get_file_size(self, filepath: str) -> int:
        """Gets the size of a file in bytes.

        Args:
            filepath (str): The path to the file.

        Returns:
            int: The size of the file in bytes.
        """
        return os.path.getsize(filepath)

    def _get_directory_size(self, directory: str) -> int:
        """Recursively calculates the total size of a directory in bytes.

        Args:
            directory (str): The path to the directory.

        Returns:
            int: The total size of the directory in bytes.
        """
        total = 0
        with os.scandir(directory) as it:
            for entry in it:
                if entry.is_file():
                    total += entry.stat().st_size
                elif entry.is_dir():
                    total += self._get_directory_size(directory=entry.path)
        return total

    def _get_directory_count(self, directory: str) -> int:
        """Recursively counts the total number of files and directories in a directory.

        Args:
            directory (str): The path to the directory.

        Returns:
            int: The total count of files and directories in the specified directory.
        """
        total = 0
        with os.scandir(directory) as it:
            for entry in it:
                if entry.is_file():
                    total += 1
                elif entry.is_dir():
                    total += self._get_directory_count(directory=entry.path)
        return total
