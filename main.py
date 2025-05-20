import httpx
from mcp.server import FastMCP
import base64
import os
import json
import uuid
from api import (
    login_to_qbittorrent,
    add_torrent_api,
    delete_torrent_api,
    pause_torrent_api,
    resume_torrent_api,
    get_torrent_trackers_urls,
    set_global_download_limit_api,
    set_global_upload_limit_api,
    get_application_version_api,
    set_file_priority_api,
    set_torrent_download_limit_api,
    set_torrent_upload_limit_api,
    add_trackers_to_torrent_api,
    add_torrent_tags_api,
    get_torrent_list_api
)

# 定义关键参数
DEFAULT_HOST = 'http://10.161.28.28:8080'
DEFAULT_USERNAME = 'admin'
DEFAULT_PASSWORD = 'mima123'

# 初始化 FastMCP 服务器
app = FastMCP('qbittorrent')

@app.tool()
async def add_torrent(query: str) -> str:
    """
    添加种子文件到qBittorrent
    
    Args:
        query: 包含种子文件路径的查询字符串，支持以下格式：
               1. JSON字符串: "{\"file_paths\": [\"path/to/file1.torrent\", \"path/to/file2.torrent\"]}"
               2. JSON字符串: "[\"path/to/file1.torrent\", \"path/to/file2.torrent\"]"
               3. 单一文件路径: "path/to/file.torrent"
        
    Returns:
        添加结果的状态和消息
    """
    return await add_torrent_api(query, DEFAULT_HOST, DEFAULT_USERNAME, DEFAULT_PASSWORD)

@app.tool()
async def delete_torrent(hashes: str, delete_files: bool = False) -> str:
    """
    删除qBittorrent中的种子
    
    Args:
        hashes: 要删除的种子哈希值，多个哈希值用|分隔，或者使用'all'删除所有种子
        delete_files: 如果为True，同时删除下载的文件
        
    Returns:
        删除操作的结果消息
    """
    return await delete_torrent_api(hashes, delete_files, DEFAULT_HOST, DEFAULT_USERNAME, DEFAULT_PASSWORD)

@app.tool()
async def pause_torrent(hashes: str) -> str:
    """
    暂停种子
    
    Args:
        hashes: 要暂停的种子哈希值，多个哈希值用|分隔，或者使用'all'暂停所有种子
        
    Returns:
        暂停操作的结果消息
    """
    return await pause_torrent_api(hashes, DEFAULT_HOST, DEFAULT_USERNAME, DEFAULT_PASSWORD)

@app.tool()
async def resume_torrent(hashes: str) -> str:
    """
    恢复种子
    
    Args:
        hashes: 要恢复的种子哈希值，多个哈希值用|分隔，或者使用'all'恢复所有种子
        
    Returns:
        恢复操作的结果消息
    """
    return await resume_torrent_api(hashes, DEFAULT_HOST, DEFAULT_USERNAME, DEFAULT_PASSWORD)

@app.tool()
async def get_torrent_trackers(hash: str) -> str:
    """
    获取种子跟踪器
    
    Args:
        hash: 种子哈希值
        
    Returns:
        包含跟踪器信息的字符串
    """
    return await get_torrent_trackers_urls(hash, DEFAULT_HOST, DEFAULT_USERNAME, DEFAULT_PASSWORD)

@app.tool()
async def set_global_download_limit(limit: int) -> str:
    """
    设置全局下载限速
    
    Args:
        limit: 限速值，单位为字节/秒
        
    Returns:
        设置限速的结果消息
    """ 
    return await set_global_download_limit_api(limit)

@app.tool()
async def set_global_upload_limit(limit: int) -> str:
    """
    设置全局上传限速
    
    Args:
        limit: 限速值，单位为字节/秒
        
    Returns:
        设置限速的结果消息
    """
    return await set_global_upload_limit_api(limit)

@app.tool()
async def get_application_version() -> str:
    """
    获取qBittorrent版本
    
    Returns:
        qBittorrent版本
    """
    return await get_application_version_api()

@app.tool()
async def set_file_priority(hash: str, id: str, priority: int) -> str:
    """
    设置文件优先级
    
    Args:
        hash: 种子哈希值
        id: correspond to file position inside the array returned by torrent contents API, e.g. id=0 for first file, id=1 for second file, etc.
        priority: 
        Value	Description
        0	Do not download
        1	Normal priority
        6	High priority
        7	Maximal priority
        
    Returns:
        设置文件优先级的结果消息
        HTTP Status Code	Scenario
        400	Priority is invalid
        400	At least one file id is not a valid integer
        404	Torrent hash was not found
        409	Torrent metadata hasn't downloaded yet
        409	At least one file id was not found
        200	All other scenarios
    """ 
    return await set_file_priority_api(hash, id, priority, DEFAULT_HOST, DEFAULT_USERNAME, DEFAULT_PASSWORD)

@app.tool()
async def set_torrent_download_limit(hash: str, limit: int) -> str:
    """
    设置种子下载限速
    
    Args:
        hash: 种子哈希值
        limit: 限速值，单位为字节/秒
        
    Returns:
        设置种子下载限速的结果消息
    """
    return await set_torrent_download_limit_api(hash, limit, DEFAULT_HOST, DEFAULT_USERNAME, DEFAULT_PASSWORD)

@app.tool()
async def set_torrent_upload_limit(hash: str, limit: int) -> str:
    """
    设置种子上传限速
    
    Args:
        hash: 种子哈希值
        limit: 限速值，单位为字节/秒
        
    Returns:
        设置种子上传限速的结果消息
    """ 
    return await set_torrent_upload_limit_api(hash, limit, DEFAULT_HOST, DEFAULT_USERNAME, DEFAULT_PASSWORD)

@app.tool()
async def add_trackers_to_torrent(hash: str, trackers: str) -> str:
    """
    添加跟踪器到种子    
    
    Args:
        hash: 种子哈希值
        trackers: 跟踪器URL，多个URL用%0A分隔
        
    Returns:
        添加跟踪器的结果消息 
    """
    return await add_trackers_to_torrent_api(hash, trackers, DEFAULT_HOST, DEFAULT_USERNAME, DEFAULT_PASSWORD)

@app.tool()
async def add_torrent_tags(hash: str, tags: str) -> str:
    """
    添加种子标签
    
    Args:
        hash: 种子哈希值
        tags: 标签列表，多个标签用逗号分隔
        
    Returns:
        添加种子标签的结果消息
    """
    return await add_torrent_tags_api(hash, tags, DEFAULT_HOST, DEFAULT_USERNAME, DEFAULT_PASSWORD)

@app.tool()
async def get_torrent_list() -> str:
    """
    获取种子列表
    """
    return await get_torrent_list_api(host=DEFAULT_HOST, username=DEFAULT_USERNAME, password=DEFAULT_PASSWORD)

if __name__ == "__main__":
    app.run(transport='stdio')