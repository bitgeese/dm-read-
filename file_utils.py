import os
from typing import Set

def read_already_scraped(file_path: str) -> Set[str]:
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return set(file.read().splitlines())
    return set()

def write_already_scraped(file_path: str, url: str) -> None:
    with open(file_path, "a") as file:
        file.write(f"{url}\n")

def ensure_directory_exists(directory: str) -> None:
    if not os.path.exists(directory):
        os.makedirs(directory)