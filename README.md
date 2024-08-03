# dm-read-dl

dm-read-dl is a Python-based tool for downloading media from Instagram direct messages.

## Features

- Login to Instagram account
- Extract post URLs from direct messages
- Download media files from extracted URLs
- Skip already downloaded posts
- Colorful console output
- Progress bar for downloads

## Installation

1. Ensure you have Python 3.12 or later installed.
2. Clone this repository:
   ```
   git clone https://github.com/bitgeese/dm-read-dl.git
   cd dm-read-dl
   ```
3. Install dependencies using Poetry:
   ```
   poetry install
   ```

## Configuration

1. Copy the `.env.example` file to `.env`:
   ```
   cp .env.example .env
   ```

2. Edit the `.env` file and fill in your specific values:
   - Set your Instagram username and password
   - Adjust the download directory path
   - Configure other settings as needed

3. Never commit your `.env` file to version control.

The `config.py` file will automatically load these environment variables using python-dotenv.

## Usage

Run the main script:

```
poetry run python main.py
```

## Project Structure

- `main.py`: Main script with Instagram downloader logic
- `config.py`: Configuration settings
- `api_client.py`: API client for interacting with external services
- `file_utils.py`: Utility functions for file operations

## Dependencies
- requests: HTTP library for making API calls
- instagrapi: Unofficial Instagram API client
- pillow: Python Imaging Library for image processing
- typer: Library for building CLI applications
- colorama: Cross-platform colored terminal text
- rich: Rich text and beautiful formatting in the terminal
- python-dotenv: Library for loading environment variables from .env files

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is for educational purposes only. Please respect Instagram's terms of service and use responsibly.

## Support

If you encounter any issues or have questions, please open an issue on the GitHub repository.