import logging
import os
import uuid
from typing import List

import requests
import typer
from instagrapi import Client
from colorama import Fore, Style, init
from rich.progress import Progress, TextColumn, BarColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn

from api_client import APIClient
from file_utils import read_already_scraped, write_already_scraped, ensure_directory_exists
import config

# Initialize colorama if colored output is enabled
if config.USE_COLORED_OUTPUT:
    init(autoreset=True)

class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        log_message = super().format(record)
        return f"{self.COLORS.get(record.levelname, '')}{log_message}{Style.RESET_ALL}"

class InstagramDownloader:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.client = Client()
        self.logger = logging.getLogger(__name__)
        self.api_client = APIClient(config.BASE_URL, config.HEADERS)

    def login(self) -> bool:
        try:
            self.client.login(self.username, self.password)
            return True
        except Exception as e:
            self.logger.error(f"Login failed: {str(e)}")
            return False

    def logout(self) -> None:
        try:
            self.client.logout()
        except Exception as e:
            self.logger.error(f"Logout failed: {str(e)}")

    def extract_post_urls(self) -> List[str]:
        urls = []
        try:
            inbox = self.client.direct_threads()
            for thread in inbox:
                messages = self.client.direct_messages(thread.id)
                for message in messages:
                    if message.item_type == "xma_media_share" and message.xma_share:
                        url = str(message.xma_share.video_url)
                        urls.append(url)
        except Exception as e:
            self.logger.error(f"Error extracting post URLs: {str(e)}")
        return urls

    def download_file(self, url: str, dest_path: str):
        response = requests.get(url, stream=True, timeout=config.API_TIMEOUT)
        total_size = int(response.headers.get("content-length", 0))
        chunk_size = config.DOWNLOAD_CHUNK_SIZE

        with open(dest_path, "wb") as file, Progress(
            TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
            BarColumn(bar_width=None, style="cyan", complete_style="bright_cyan"),
            "[progress.percentage]{task.percentage:>3.1f}%",
            DownloadColumn(),
            TransferSpeedColumn(),
            TimeRemainingColumn(),
        ) as progress:
            download_task = progress.add_task("[green]Downloading...", total=total_size, filename=os.path.basename(dest_path))
            for data in response.iter_content(chunk_size=chunk_size):
                size = file.write(data)
                progress.update(download_task, advance=size)

    def download_media(self, payload: List[dict]):
        ensure_directory_exists(config.DOWNLOAD_DIR)

        for media in payload:
            file_name = media.get("name") or media["path"].split("/")[-1]
            unique_name = f"{uuid.uuid4()}{os.path.splitext(file_name)[1]}"
            self.download_file(
                media["path"], os.path.join(config.DOWNLOAD_DIR, unique_name)
            )

    def process_url(self, url: str) -> None:
        try:
            media_hook_response = self.api_client.post_media_hook(url)
            job_id = media_hook_response.get("job_id")

            if job_id:
                payload = self.api_client.wait_for_job_completion(job_id)
                if payload:
                    self.download_media(payload)
                    write_already_scraped(config.ALREADY_SCRAPED_FILE, url)
                    self.logger.info(f"Successfully downloaded and saved: {url}")
                else:
                    self.logger.error(f"No media payload returned for: {url}")
            else:
                self.logger.error(f"No job ID returned from media hook for: {url}")
        except Exception as e:
            self.logger.error(f"Error processing URL {url}: {str(e)}")

    def run(self):
        if not self.login():
            return

        already_scraped = read_already_scraped(config.ALREADY_SCRAPED_FILE)
        urls = self.extract_post_urls()

        for url in urls:
            if url in already_scraped:
                self.logger.info(f"Skipping already downloaded post: {url}")
                continue

            self.process_url(url)

        self.logout()

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(config.LOG_LEVEL)

    console_handler = logging.StreamHandler()
    if config.USE_COLORED_OUTPUT:
        console_handler.setFormatter(ColoredFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    else:
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)

    if config.DEBUG_MODE:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode is enabled")

def main():
    setup_logging()
    if not config.INSTAGRAM_USERNAME or not config.INSTAGRAM_PASSWORD:
        logging.error("Instagram credentials not set. Please check your .env file.")
        return
    downloader = InstagramDownloader(config.INSTAGRAM_USERNAME, config.INSTAGRAM_PASSWORD)
    downloader.run()

if __name__ == "__main__":
    main()