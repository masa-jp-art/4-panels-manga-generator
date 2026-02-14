"""Utility functions for the application."""

import mimetypes
import os
from pathlib import Path
from typing import List


def get_files_in_directory(directory: str) -> List[str]:
    """Get list of files in a directory.

    Args:
        directory: Directory path to scan

    Returns:
        List of filenames in the directory

    Raises:
        ValueError: If directory doesn't exist
    """
    dir_path = Path(directory)

    if not dir_path.exists():
        raise ValueError(f"Directory does not exist: {directory}")

    if not dir_path.is_dir():
        raise ValueError(f"Path is not a directory: {directory}")

    files = [
        f.name
        for f in dir_path.iterdir()
        if f.is_file() and not f.name.startswith('.')
    ]

    return sorted(files)


def save_binary_file(file_path: str, data: bytes) -> None:
    """Save binary data to a file.

    Args:
        file_path: Path where to save the file
        data: Binary data to save

    Raises:
        IOError: If file cannot be written
    """
    try:
        output_path = Path(file_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'wb') as f:
            f.write(data)
    except Exception as e:
        raise IOError(f"Failed to save file {file_path}: {str(e)}")


def get_mime_type(file_path: str) -> str:
    """Get MIME type of a file.

    Args:
        file_path: Path to the file

    Returns:
        MIME type string
    """
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type or 'application/octet-stream'


def validate_api_key(api_key: str) -> None:
    """Validate API key is not empty.

    Args:
        api_key: API key to validate

    Raises:
        ValueError: If API key is invalid
    """
    if not api_key or api_key.strip() == "":
        raise ValueError("GEMINI_API_KEY is not configured")


def load_image_bytes(file_path: str) -> tuple[bytes, str]:
    """Load image file as binary data with MIME type.

    Args:
        file_path: Path to the image file

    Returns:
        Tuple of (binary data, MIME type)

    Raises:
        FileNotFoundError: If file doesn't exist
        IOError: If file cannot be read
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {file_path}")

    if not path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    try:
        with open(path, 'rb') as f:
            data = f.read()
    except Exception as e:
        raise IOError(f"Failed to read image file {file_path}: {str(e)}")

    mime_type = get_mime_type(file_path)

    return data, mime_type
