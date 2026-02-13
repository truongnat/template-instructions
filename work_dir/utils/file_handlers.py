"""
File handling utilities for SDLC Kit.

Provides common file operations with error handling and cross-platform support.
"""

import os
import shutil
from pathlib import Path
from typing import Optional, List, Union


def read_file(filepath: Union[str, Path], encoding: str = 'utf-8') -> Optional[str]:
    """
    Read file content safely.
    
    Args:
        filepath: Path to file
        encoding: File encoding (default: utf-8)
        
    Returns:
        File content as string, or None if error occurs
    """
    try:
        with open(filepath, 'r', encoding=encoding) as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None


def write_file(filepath: Union[str, Path], content: str, encoding: str = 'utf-8') -> bool:
    """
    Write content to file safely.
    
    Args:
        filepath: Path to file
        content: Content to write
        encoding: File encoding (default: utf-8)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding=encoding) as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error writing {filepath}: {e}")
        return False


def append_file(filepath: Union[str, Path], content: str, encoding: str = 'utf-8') -> bool:
    """
    Append content to file safely.
    
    Args:
        filepath: Path to file
        content: Content to append
        encoding: File encoding (default: utf-8)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'a', encoding=encoding) as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error appending to {filepath}: {e}")
        return False


def copy_file(src: Union[str, Path], dst: Union[str, Path]) -> bool:
    """
    Copy file from source to destination.
    
    Args:
        src: Source file path
        dst: Destination file path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        Path(dst).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return True
    except Exception as e:
        print(f"Error copying {src} to {dst}: {e}")
        return False


def move_file(src: Union[str, Path], dst: Union[str, Path]) -> bool:
    """
    Move file from source to destination.
    
    Args:
        src: Source file path
        dst: Destination file path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        Path(dst).parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        return True
    except Exception as e:
        print(f"Error moving {src} to {dst}: {e}")
        return False


def delete_file(filepath: Union[str, Path]) -> bool:
    """
    Delete file safely.
    
    Args:
        filepath: Path to file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        Path(filepath).unlink()
        return True
    except Exception as e:
        print(f"Error deleting {filepath}: {e}")
        return False


def list_files(directory: Union[str, Path], pattern: str = "*", recursive: bool = False) -> List[Path]:
    """
    List files in directory matching pattern.
    
    Args:
        directory: Directory to search
        pattern: Glob pattern (default: *)
        recursive: Search recursively (default: False)
        
    Returns:
        List of matching file paths
    """
    try:
        dir_path = Path(directory)
        if recursive:
            return list(dir_path.rglob(pattern))
        else:
            return list(dir_path.glob(pattern))
    except Exception as e:
        print(f"Error listing files in {directory}: {e}")
        return []


def ensure_directory(directory: Union[str, Path]) -> Path:
    """
    Ensure directory exists, create if necessary.
    
    Args:
        directory: Directory path
        
    Returns:
        Path object for the directory
    """
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path


def file_exists(filepath: Union[str, Path]) -> bool:
    """
    Check if file exists.
    
    Args:
        filepath: Path to file
        
    Returns:
        True if file exists, False otherwise
    """
    return Path(filepath).exists()


def get_file_size(filepath: Union[str, Path]) -> Optional[int]:
    """
    Get file size in bytes.
    
    Args:
        filepath: Path to file
        
    Returns:
        File size in bytes, or None if error occurs
    """
    try:
        return Path(filepath).stat().st_size
    except Exception as e:
        print(f"Error getting size of {filepath}: {e}")
        return None


__all__ = [
    'read_file',
    'write_file',
    'append_file',
    'copy_file',
    'move_file',
    'delete_file',
    'list_files',
    'ensure_directory',
    'file_exists',
    'get_file_size',
]
