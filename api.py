import httpx
import os
import json
import base64
from typing import Dict, List, Union, Optional

async def login_to_qbittorrent(username, password, host):
    """
    Login to qBittorrent WebUI and obtain session cookie

    Args:
        username: Username
        password: Password
        host: qBittorrent WebUI host address

    Returns:
        Returns object containing session cookie on success, None on failure
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{host}/api/v2/auth/login",
            data={"username": username, "password": password}
        )
    
        if response.status_code == 200:
            return response.cookies
        return None

async def add_torrent_api(query: str, host: str, username: str, password: str) -> str:
    """
    Add torrent file to qBittorrent

    Args:
        query: Query string containing torrent file path
        host: qBittorrent WebUI host address
        username: Username
        password: Password

    Returns:
        Status and message of add operation
    """
    # Debug logging - write to file
    with open("qbittorrent_debug.log", "a") as f:
        f.write(f"Received query: {query}\n")
    
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        return "Login failed, unable to get SID"

    try:
        try:
            data = json.loads(query)
        except json.JSONDecodeError:
            # If not valid JSON, assume it's a single file path
            file_paths = [query.strip()]
        else:
            # JSON parsing successful, determine result type
            if isinstance(data, list):
                file_paths = data
            elif isinstance(data, dict) and "file_paths" in data:
                file_paths = data["file_paths"]
            else:
                return "Error: Unrecognized JSON format, please provide required format"

        if not file_paths:
            return "Error: No torrent file path provided"
        
        results = []
        async with httpx.AsyncClient() as client:
            for file_path in file_paths:
                if not os.path.exists(file_path):
                    results.append(f"File does not exist: {file_path}")
                    continue

                files = {}
                try:
                    with open(file_path, 'rb') as f:
                        file_content = f.read()
                        file_name = os.path.basename(file_path)
                        files = {'torrents': (file_name, file_content, 'application/x-bittorrent')}
                except Exception as e:
                    results.append(f"Error reading file {file_path}: {str(e)}")
                    continue

                # Explicitly set HTTP request headers
                headers = {
                    "Accept": "*/*",
                    "Host": host.replace('http://', '').replace('https://', '')
                }

                response = await client.post(
                    f"{host}/api/v2/torrents/add",
                    files=files,
                    cookies=cookies,
                    headers=headers
                )

                if response.status_code == 200:
                    results.append(f"Successfully added torrent file: {file_name}")
                elif response.status_code == 415:
                    results.append(f"Invalid torrent file: {file_name}")
                else:
                    results.append(f"Failed to add torrent file {file_name}: status code {response.status_code}")

        return "\n".join(results)
    except json.JSONDecodeError:
        return "Error: Query string is not valid JSON format"
    except Exception as e:
        return f"Error: {str(e)}"

async def delete_torrent_api(hashes: str, delete_files: bool = False, host: str = '', username: str = '', password: str = '') -> str:
    """
    Delete torrent from qBittorrent

    Args:
        hashes: Hash values of torrents to delete, multiple hashes separated by |, or use 'all' to delete all torrents
        delete_files: If True, also delete downloaded files
        host: qBittorrent WebUI host address
        username: Username
        password: Password

    Returns:
        Result message of delete operation
    """
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        return "Login failed, unable to get SID"

    try:
        # Prepare form data
        data = {
            "hashes": hashes,
            "deleteFiles": str(delete_files).lower()
        }

        # Set correct Content-Type header
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
        }

        async with httpx.AsyncClient() as client:
            # Use data parameter instead of json parameter
            response = await client.post(
                f"{host}/api/v2/torrents/delete",
                data=data,  # Use data instead of json
                cookies=cookies,
                headers=headers
            )

            if response.status_code == 200:
                if hashes == "all":
                    return "Successfully deleted all torrents"
                else:
                    return f"Successfully deleted specified torrents: {hashes}"
            else:
                # Error handling
                print(f"Failed to delete torrent, HTTP status code: {response.status_code}")
                print(f"Response body: {response.text}")
                try:
                    return f"Failed to delete torrent, HTTP status code: {response.status_code}, response body: {response.json()}"
                except:
                    return f"Failed to delete torrent, HTTP status code: {response.status_code}, response body: {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

async def pause_torrent_api(hashes: str, host: str = '', username: str = '', password: str = '') -> str:
    """
    Pause torrent

    Args:
        hashes: Hash values of torrents to pause, multiple hashes separated by |, or use 'all' to pause all torrents
        host: qBittorrent WebUI host address
        username: Username
        password: Password

    Returns:
        Result message of pause operation
    """
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        return "Login failed, unable to get SID"
    
    try:
        params = {"hashes": hashes}
        
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
        }
        
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{host}/api/v2/torrents/stop",
                data=params,
                cookies=cookies,
                headers=headers
            )
            
            if response.status_code == 200:
                if hashes == "all":
                    return "Successfully paused all torrents"
                else:
                    return f"Successfully paused specified torrents: {hashes}"
            else:
                return f"Failed to pause torrent: status code {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

async def resume_torrent_api(hashes: str, host: str = '', username: str = '', password: str = '') -> str:
    """
    Resume torrent

    Args:
        hashes: Hash values of torrents to resume, multiple hashes separated by |, or use 'all' to resume all torrents
        host: qBittorrent WebUI host address
        username: Username
        password: Password

    Returns:
        Result message of resume operation
    """
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        return "Login failed, unable to get SID"
    
    try:
        params = {"hashes": hashes}
        
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{host}/api/v2/torrents/start",
                data=params,
                cookies=cookies,
                headers=headers
            )
            
            if response.status_code == 200:
                if hashes == "all":
                    return "Successfully resumed all torrents"
                else:
                    return f"Successfully resumed specified torrents: {hashes}"
            else:
                return f"Failed to resume torrent: status code {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

async def get_torrent_trackers_urls(hash: str, host: str = '', username: str = '', password: str = '') -> str:
    """
    Get torrent trackers

    Args:
        hash: Hash value of the torrent to get trackers for
        host: qBittorrent WebUI host address
        username: Username
        password: Password

    Returns:
        Formatted string containing torrent trackers
    """
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        return "Login failed, unable to get SID"
    try:
        params = {"hash": hash}
        
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{host}/api/v2/torrents/trackers",
                    params=params,
                    cookies=cookies,
                    headers=headers
                )
            except Exception as e:
                return f"Error: {str(e)}"

            if response.status_code == 200:

                trackers = response.json()
                if not trackers:
                    return "This torrent has no trackers"

                # Extract all URLs
                tracker_urls = []
                for tracker in trackers:
                    url = tracker.get('url')
                    status = tracker.get('status')
                    msg = tracker.get('msg')

                    # Exclude DHT, PeX, LSD and other special trackers, only get actual URLs
                    if not url.startswith('** ['):
                        tracker_urls.append(f"{url}")

                if not tracker_urls:
                    return "This torrent has no valid tracker URLs"

                return ",".join(tracker_urls)
            else:
                return f"Failed to get torrent trackers: status code {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"
    
async def set_global_download_limit_api(limit: int, host: str = '', username: str = '', password: str = '') -> str:
    """
    Set global download speed limit

    Args:
        limit: Speed limit value in bytes/second
        host: qBittorrent WebUI host address
        username: Username
        password: Password

    Returns:
        Result message of setting speed limit
    """
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        return "Login failed, unable to get SID"
    try:
        params = {"limit": limit}
        
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{host}/api/v2/transfer/setDownloadLimit",
                data=params,
                cookies=cookies,
                headers=headers
            )
            
            if response.status_code == 200:
                return f"Successfully set speed limit: {limit}"
            else:
                return f"Failed to set speed limit: status code {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}" 
    
async def set_global_upload_limit_api(limit: int, host: str = '', username: str = '', password: str = '') -> str:
    """
    Set global upload speed limit

    Args:
        limit: Speed limit value in bytes/second
        host: qBittorrent WebUI host address
        username: Username
        password: Password

    Returns:
        Result message of setting speed limit
    """
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        return "Login failed, unable to get SID"
    try:
        params = {"limit": limit}
        
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{host}/api/v2/transfer/setUploadLimit",
                data=params,
                cookies=cookies,
                headers=headers)
            if response.status_code == 200:
                return f"Successfully set speed limit: {limit}"
            else:
                return f"Failed to set speed limit: status code {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}" 
    
async def get_application_version_api(host: str = '', username: str = '', password: str = '') -> str:
    """
    Get qBittorrent version

    Returns:
        qBittorrent version
    """
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        return "Login failed, unable to get SID"
    try:
        headers = {
            "Accept": "*/*",
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{host}/api/v2/app/version",
                cookies=cookies,
                headers=headers
            )
            if response.status_code == 200:
                return response.text.strip()
            else:
                return f"Failed to get qBittorrent version: status code {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}" 
    
async def set_file_priority_api(hash: str, id: str, priority: int, host: str = '', username: str = '', password: str = '') -> str:
    """
    Set file priority

    Args:
        hash: Torrent hash value
        id: correspond to file position inside the array returned by torrent contents API, e.g. id=0 for first file, id=1 for second file, etc.
        priority:
        Value	Description
        0	Do not download
        1	Normal priority
        6	High priority
        7	Maximal priority

    Returns:
        Result message of setting file priority
        HTTP Status Code	Scenario
        400	Priority is invalid
        400	At least one file id is not a valid integer
        404	Torrent hash was not found
        409	Torrent metadata hasn't downloaded yet
        409	At least one file id was not found
        200	All other scenarios
    """
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        return "Login failed, unable to get SID"
    try:
        params = {"hash": hash, "id": id, "priority": priority}
        
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{host}/api/v2/torrents/filePrio",
                data=params,
                cookies=cookies,
                headers=headers)
            if response.status_code == 200:
                return f"Successfully set file priority: {hash}:{id}:{priority}"
            else:
                return f"Failed to set file priority: status code {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

async def set_torrent_download_limit_api(hash: str, limit: int, host: str = '', username: str = '', password: str = '') -> str:
    """
    Set torrent download speed limit

    Args:
        hash: Torrent hash value
        limit: Speed limit value in bytes/second
        host: qBittorrent WebUI host address
        username: Username
        password: Password

    Returns:
        Result message of setting torrent download speed limit
    """
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        return "Login failed, unable to get SID"
    try:
        params = {"hashes": hash, "limit": limit}
        
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{host}/api/v2/torrents/setDownloadLimit",
                data=params,
                cookies=cookies,
                headers=headers)
            if response.status_code == 200:
                return f"Successfully set torrent download speed limit: {hash}:{limit}"
            else:
                return f"Failed to set torrent download speed limit: status code {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"


async def set_torrent_upload_limit_api(hash: str, limit: int, host: str = '', username: str = '', password: str = '') -> str:
    """
    Set torrent upload speed limit

    Args:
        hash: Torrent hash value
        limit: Speed limit value in bytes/second
        host: qBittorrent WebUI host address
        username: Username
        password: Password

    Returns:
        Result message of setting torrent upload speed limit
    """
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        return "Login failed, unable to get SID"
    try:
        params = {"hashes": hash, "limit": limit}
        
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{host}/api/v2/torrents/setUploadLimit",
                data=params,
                cookies=cookies,
                headers=headers)
            if response.status_code == 200:
                return f"Successfully set torrent upload speed limit: {hash}:{limit}"
            else:
                return f"Failed to set torrent upload speed limit: status code {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

async def add_trackers_to_torrent_api(hash: str, trackers: List[str], host: str = '', username: str = '', password: str = '') -> str:
    """
    Add trackers to torrent

    Args:
        hash: Torrent hash value
        url: Tracker URL
        example: hash=8c212779b4abde7c6bc608063a0d008b7e40ce32&urls=http://192.168.0.1/announce%0Audp://192.168.0.1:3333/dummyAnnounce
    Returns:
        Result message of adding trackers
    """
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        return "Login failed, unable to get SID"
    try:
        params = {"hash": hash, "urls": trackers}
        
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{host}/api/v2/torrents/addTrackers",
                data=params,
                cookies=cookies,
                headers=headers)
            if response.status_code == 200:
                return f"Successfully added trackers: {hash}:{trackers}"
            else:
                return f"Failed to add trackers: status code {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

async def add_torrent_tags_api(hash: str, tags: List[str], host: str = '', username: str = '', password: str = '') -> str:
    """
    Add torrent tags

    Args:
        hash: Torrent hash value
        tags: Tag list

        example: hashes=8c212779b4abde7c6bc608063a0d008b7e40ce32|284b83c9c7935002391129fd97f43db5d7cc2ba0&tags=TagName1,TagName2

    Returns:
        Result message of adding torrent tags
    """
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        return "Login failed, unable to get SID"
    try:
        params = {"hashes": hash, "tags": tags}
        
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{host}/api/v2/torrents/addTags",
                data=params,
                cookies=cookies,
                headers=headers)
            if response.status_code == 200:
                return f"Successfully added torrent tags: {hash}:{tags}"
            else:
                return f"Failed to add torrent tags: status code {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

async def get_torrent_list_api(host: str = '', username: str = '', password: str = '') -> str:
    """
    Get torrent list
    """
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        return "Login failed, unable to get SID"
    try:
        headers = {
            "Accept": "*/*",
        }
        
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{host}/api/v2/torrents/info",
                cookies=cookies,
                headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                return f"Failed to get torrent list: status code {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"
    
    