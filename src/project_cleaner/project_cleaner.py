"""Copyright (c) 2023 Aydin Abdi

A script for cleaning up project directories.
"""
import asyncio
import aiofiles
from pathlib import Path
import shutil
from typing import List, Set

# Usage
TMP_DIRECTORIES = [
    "_build",
    "build",
    "dist",
    "__pycache__",
    ".pytest_cache",
    "lib",
    "include",
    "htmlcov",
    "share",
    "bin",
    "output",
    "lib64",
    ".tox",
]

FILE_EXTENSIONS = [".pyc", ".egg"]


class ProjectCleaner:
    """A class for cleaning up project directories.

    Parameters:
        directories_to_remove: A set of directory names to remove.
        file_extensions_to_remove: A set of file extensions to remove.

    Examples as library:
        >>> cleaner = ProjectCleaner(TMP_DIRECTORIES, FILE_EXTENSIONS)
        >>> cleaner.clean()

    Examples as script:
        >>> python project_cleaner.py
    """

    def __init__(
        self,
        directories_to_remove: Set[str] = None,
        file_extensions_to_remove: Set[str] = None,
    ):
        """Inits ProjectCleaner with directories and file extensions to remove."""
        self.directories_to_remove = directories_to_remove or set()
        self.file_extensions_to_remove = file_extensions_to_remove or set()

    async def remove_file(self, file_path: Path):
        """Removes a file asynchronously.

        Args:
            file_path: The path of the file to remove.
        """
        if file_path.exists() and file_path.is_file():
            await aiofiles.os.remove(file_path)

    async def remove_directories(self, directory_queue: asyncio.Queue):
        """Consumer function to remove directories from queue.

        Args:
            directory_queue: asyncio Queue containing directories to remove.
        """
        while True:
            directory = await directory_queue.get()
            if directory is None:
                break
            shutil.rmtree(directory, ignore_errors=True)
            directory_queue.task_done()

    async def produce_directories(
        self, all_paths: List[Path], directory_queue: asyncio.Queue
    ):
        """Producer function to add directories to queue.

        Args:
            all_paths: A list of all paths in the root directory.
            directory_queue: asyncio Queue where directories are added.
        """
        directories = self.find_directories_to_remove(all_paths)
        for directory in directories:
            await directory_queue.put(directory)

    async def clean(self, path: str = "."):
        """Removes specified directories and files in a given directory.

        Args:
            path: The root directory to clean.
        """
        root = Path(path)
        # Create a list of all paths, this will avoid modifying the iterator during loop
        all_paths = list(root.rglob("*"))
        files = {
            p
            for p in all_paths
            if p.is_file() and p.suffix in self.file_extensions_to_remove
        }

        directory_queue = asyncio.Queue()

        # Producer and Consumer tasks
        producer_task = asyncio.create_task(
            self.produce_directories(all_paths, directory_queue)
        )
        consumer_task = asyncio.create_task(self.remove_directories(directory_queue))

        # Remove files asynchronously
        await self.remove_files_async(files)

        # Wait for the producer task to finish
        await producer_task

        # Wait for the remaining directory to be removed and then close the queue
        await directory_queue.join()
        await directory_queue.put(None)

        # Cancel the consumer task
        consumer_task.cancel()
        try:
            await consumer_task
        except asyncio.CancelledError:
            pass

    def find_directories_to_remove(self, all_paths: List[Path]) -> Set[Path]:
        """Find directories to remove based on the specified rules.

        Args:
            all_paths: A list of all paths in the root directory.

        Returns:
            A set of directory paths to remove.
        """
        directories = set()
        exclude_path = ".tox/clean"
        for p in all_paths:
            # do not remove .tox/clean directory and its subdirectories
            if exclude_path in str(p) or any(
                exclude_path in str(parent) for parent in p.parents
            ):
                continue
            if p.is_dir() and p.name in self.directories_to_remove:
                print(f"Removing directory: {p}")
                directories.add(p)

        return directories

    async def remove_files_async(self, files: Set[Path]):
        """Removes a set of files asynchronously.

        Args:
            files: A set of file paths to remove.
        """
        tasks = [self.remove_file(file) for file in files]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        cleaner = ProjectCleaner(TMP_DIRECTORIES, FILE_EXTENSIONS)
        asyncio.run(cleaner.clean())
    except Exception as e:
        print(f"Error while cleaning project: {e}")
    else:
        print("Project cleaned successfully!")
