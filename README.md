# qBittorrent MCP Server

NOTE: This is fork of https://github.com/pickpppcc/qbittorrent-mcp.git

qBittorrent MCP is a FastMCP-based service that provides functional interfaces for interacting with the qBittorrent WebUI API.

## Features

This service provides the following functionality:

### Torrent Management

- `add_torrent`: Add torrent files to qBittorrent
- `delete_torrent`: Delete specified torrents (optionally delete files)
- `pause_torrent`: Pause torrent downloads
- `resume_torrent`: Resume torrent downloads
- `get_torrent_list`: Get list of all torrents

### Trackers & Tags

- `get_torrent_trackers`: Get tracker list for a torrent
- `add_trackers_to_torrent`: Add new trackers to a torrent
- `add_torrent_tags`: Add tags to a torrent

### Speed & Priority Control

- `set_global_download_limit`: Set global download speed limit
- `set_global_upload_limit`: Set global upload speed limit
- `set_torrent_download_limit`: Set download speed limit for specific torrent
- `set_torrent_upload_limit`: Set upload speed limit for specific torrent
- `set_file_priority`: Set download priority for specific file

### System Information

- `get_application_version`: Get qBittorrent application version

## Configuration

The service uses the following configuration parameters:

- `DEFAULT_HOST`: qBittorrent WebUI host address
- `DEFAULT_USERNAME`: qBittorrent WebUI username
- `DEFAULT_PASSWORD`: qBittorrent WebUI password

## Usage

1. Install required dependencies:

   ```
   pip install httpx mcp
   ```

2. Run the MCP service:
   ```
   python main.py
   ```

## Development

The service consists of two main files:

- `main.py`: Defines MCP service interfaces and configuration parameters
- `api.py`: Implements interaction logic with qBittorrent WebUI

```json
   "mcp_servers": [
        {
            "command": "uv",
            "args": [
                "--directory",
                "/workspace/PC-Canary/apps/qBittorrent/qbittorrent_mcp",
                "run",
                "qbittorrent.py"
            ]
        }
    ]
```
