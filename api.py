import httpx
import os
import json
import base64
from typing import Dict, List, Union, Optional

async def login_to_qbittorrent(username, password, host):
    """
    登录到qBittorrent WebUI，获取会话cookie
    
    Args:
        username: 用户名
        password: 密码
        host: qBittorrent WebUI主机地址
        
    Returns:
        成功时返回包含会话cookie的对象，失败时返回None
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
    添加种子文件到qBittorrent
    
    Args:
        query: 包含种子文件路径的查询字符串
        host: qBittorrent WebUI主机地址
        username: 用户名
        password: 密码
        
    Returns:
        添加结果的状态和消息
    """
    # 调试日志，写入文件
    with open("qbittorrent_debug.log", "a") as f:
        f.write(f"接收到的查询: {query}\n")
    
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        return "登录失败，无法获取SID"
    
    try:
        try:
            data = json.loads(query)
        except json.JSONDecodeError:
            # 如果不是有效JSON，假设是单一文件路径
            file_paths = [query.strip()]
        else:
            # JSON解析成功，判断结果类型
            if isinstance(data, list):
                file_paths = data
            elif isinstance(data, dict) and "file_paths" in data:
                file_paths = data["file_paths"]
            else:
                return "错误：JSON格式无法识别，请提供符合要求的格式"
            
        if not file_paths:
            return "错误：未提供种子文件路径"
        
        results = []
        async with httpx.AsyncClient() as client:
            for file_path in file_paths:
                if not os.path.exists(file_path):
                    results.append(f"文件不存在: {file_path}")
                    continue
                
                files = {}
                try:
                    with open(file_path, 'rb') as f:
                        file_content = f.read()
                        file_name = os.path.basename(file_path)
                        files = {'torrents': (file_name, file_content, 'application/x-bittorrent')}
                except Exception as e:
                    results.append(f"读取文件错误 {file_path}: {str(e)}")
                    continue
                
                # 显式设置HTTP请求头
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
                    results.append(f"成功添加种子文件: {file_name}")
                elif response.status_code == 415:
                    results.append(f"无效的种子文件: {file_name}")
                else:
                    results.append(f"添加种子文件失败 {file_name}: 状态码 {response.status_code}")
        
        return "\n".join(results)
    except json.JSONDecodeError:
        return "错误：查询字符串不是有效的JSON格式"
    except Exception as e:
        return f"错误：{str(e)}"

async def delete_torrent_api(hashes: str, delete_files: bool = False, host: str = '', username: str = '', password: str = '') -> str:
    """
    删除qBittorrent中的种子
    
    Args:
        hashes: 要删除的种子哈希值，多个哈希值用|分隔，或者使用'all'删除所有种子
        delete_files: 如果为True，同时删除下载的文件
        host: qBittorrent WebUI主机地址
        username: 用户名
        password: 密码
        
    Returns:
        删除操作的结果消息
    """
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        return "登录失败，无法获取SID"
    
    try:
        # 准备表单数据
        data = {
            "hashes": hashes,
            "deleteFiles": str(delete_files).lower()
        }
        
        # 设置正确的Content-Type头
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
        }
        
        async with httpx.AsyncClient() as client:
            # 使用data参数而不是json参数
            response = await client.post(
                f"{host}/api/v2/torrents/delete",
                data=data,  # 使用data而不是json
                cookies=cookies,
                headers=headers
            )
            
            if response.status_code == 200:
                if hashes == "all":
                    return "成功删除所有种子"
                else:
                    return f"成功删除指定种子: {hashes}"
            else:
                # 错误处理
                print(f"删除种子失败，HTTP状态码: {response.status_code}")
                print(f"响应体: {response.text}")
                try:
                    return f"删除种子失败，HTTP状态码: {response.status_code}, 响应体: {response.json()}"
                except:
                    return f"删除种子失败，HTTP状态码: {response.status_code}, 响应体: {response.text}"
    except Exception as e:
        return f"错误: {str(e)}"

async def pause_torrent_api(hashes: str, host: str = '', username: str = '', password: str = '') -> str:
    """
    暂停种子
    
    Args:
        hashes: 要暂停的种子哈希值，多个哈希值用|分隔，或者使用'all'暂停所有种子
        host: qBittorrent WebUI主机地址
        username: 用户名
        password: 密码
        
    Returns:
        暂停操作的结果消息
    """
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        return "登录失败，无法获取SID"
    
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
                    return "成功暂停所有种子"
                else:
                    return f"成功暂停指定种子: {hashes}"
            else:
                return f"暂停种子失败: 状态码 {response.status_code}"
    except Exception as e:
        return f"错误: {str(e)}"

async def resume_torrent_api(hashes: str, host: str = '', username: str = '', password: str = '') -> str:
    """
    恢复种子
    
    Args:
        hashes: 要恢复的种子哈希值，多个哈希值用|分隔，或者使用'all'恢复所有种子
        host: qBittorrent WebUI主机地址
        username: 用户名
        password: 密码
        
    Returns:
        恢复操作的结果消息
    """
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        return "登录失败，无法获取SID"
    
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
                    return "成功恢复所有种子"
                else:
                    return f"成功恢复指定种子: {hashes}"
            else:
                return f"恢复种子失败: 状态码 {response.status_code}"
    except Exception as e:
        return f"错误: {str(e)}" 
    
async def get_torrent_trackers_urls(hash: str, host: str = '', username: str = '', password: str = '') -> str:
    """
    获取种子跟踪器
    
    Args:
        hash: 要获取跟踪器的种子哈希值
        host: qBittorrent WebUI主机地址
        username: 用户名
        password: 密码
    
    Returns:
        包含种子跟踪器的格式化字符串
    """
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        return "登录失败，无法获取SID"
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
                return f"错误: {str(e)}"
            
            if response.status_code == 200:

                trackers = response.json()
                if not trackers:
                    return "该种子没有跟踪器"
                
                # 提取所有URL
                tracker_urls = []
                for tracker in trackers:
                    url = tracker.get('url')
                    status = tracker.get('status')
                    msg = tracker.get('msg')
                    
                    # 排除DHT, PeX, LSD等特殊跟踪器，只获取实际URL
                    if not url.startswith('** ['):
                        tracker_urls.append(f"{url}")
                
                if not tracker_urls:
                    return "该种子没有有效的跟踪器URL"
                
                return ",".join(tracker_urls)
            else:
                return f"获取种子跟踪器失败: 状态码 {response.status_code}"
    except Exception as e:
        return f"错误: {str(e)}"
    
async def set_global_download_limit_api(limit: int, host: str = '', username: str = '', password: str = '') -> str:
    """
    设置全局下载限速
    
    Args:
        limit: 限速值，单位为字节/秒
        host: qBittorrent WebUI主机地址
        username: 用户名
        password: 密码
    
    Returns:
        设置限速的结果消息
    """
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        return "登录失败，无法获取SID"
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
                return f"成功设置限速:{limit}"
            else:
                return f"设置限速失败: 状态码 {response.status_code}"
    except Exception as e:
        return f"错误: {str(e)}" 
    
async def set_global_upload_limit_api(limit: int, host: str = '', username: str = '', password: str = '') -> str:
    """
    设置全局上传限速
    
    Args:
        limit: 限速值，单位为字节/秒
        host: qBittorrent WebUI主机地址
        username: 用户名
        password: 密码

    Returns:
        设置限速的结果消息
    """
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        return "登录失败，无法获取SID"
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
                return f"成功设置限速:{limit}"
            else:
                return f"设置限速失败: 状态码 {response.status_code}"
    except Exception as e:
        return f"错误: {str(e)}" 
    
async def get_application_version_api(host: str = '', username: str = '', password: str = '') -> str:
    """
    获取qBittorrent版本
    
    Returns:
        qBittorrent版本
    """
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        return "登录失败，无法获取SID"
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
                return f"获取qBittorrent版本失败: 状态码 {response.status_code}"
    except Exception as e:
        return f"错误: {str(e)}" 
    
async def set_file_priority_api(hash: str, id: str, priority: int, host: str = '', username: str = '', password: str = '') -> str:
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
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        return "登录失败，无法获取SID"
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
                return f"成功设置文件优先级:{hash}:{id}:{priority}"
            else:
                return f"设置文件优先级失败: 状态码 {response.status_code}"
    except Exception as e:
        return f"错误: {str(e)}"

async def set_torrent_download_limit_api(hash: str, limit: int, host: str = '', username: str = '', password: str = '') -> str:
    """
    设置种子下载限速
    
    Args:
        hash: 种子哈希值
        limit: 限速值，单位为字节/秒
        host: qBittorrent WebUI主机地址
        username: 用户名
        password: 密码
    
    Returns:
        设置种子下载限速的结果消息
    """
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        return "登录失败，无法获取SID"
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
                return f"成功设置种子下载限速:{hash}:{limit}"
            else:
                return f"设置种子下载限速失败: 状态码 {response.status_code}"
    except Exception as e:
        return f"错误: {str(e)}"
    

async def set_torrent_upload_limit_api(hash: str, limit: int, host: str = '', username: str = '', password: str = '') -> str:
    """
    设置种子上传限速
    
    Args:
        hash: 种子哈希值
        limit: 限速值，单位为字节/秒
        host: qBittorrent WebUI主机地址
        username: 用户名
        password: 密码
    
    Returns:
        设置种子上传限速的结果消息
    """
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        return "登录失败，无法获取SID"
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
                return f"成功设置种子上传限速:{hash}:{limit}"
            else:
                return f"设置种子上传限速失败: 状态码 {response.status_code}"
    except Exception as e:
        return f"错误: {str(e)}" 

async def add_trackers_to_torrent_api(hash: str, trackers: List[str], host: str = '', username: str = '', password: str = '') -> str:
    """
    添加跟踪器到种子
    
    Args:
        hash: 种子哈希值
        url: 跟踪器URL
        example: hash=8c212779b4abde7c6bc608063a0d008b7e40ce32&urls=http://192.168.0.1/announce%0Audp://192.168.0.1:3333/dummyAnnounce
    Returns:
        添加跟踪器的结果消息
    """
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        return "登录失败，无法获取SID"
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
                return f"成功添加跟踪器:{hash}:{trackers}"
            else:
                return f"添加跟踪器失败: 状态码 {response.status_code}"
    except Exception as e:
        return f"错误: {str(e)}"

async def add_torrent_tags_api(hash: str, tags: List[str], host: str = '', username: str = '', password: str = '') -> str:
    """
    添加种子标签
    
    Args:
        hash: 种子哈希值
        tags: 标签列表

        example: hashes=8c212779b4abde7c6bc608063a0d008b7e40ce32|284b83c9c7935002391129fd97f43db5d7cc2ba0&tags=TagName1,TagName2
    
    Returns:
        添加种子标签的结果消息
    """
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        return "登录失败，无法获取SID"
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
                return f"成功添加种子标签:{hash}:{tags}"
            else:
                return f"添加种子标签失败: 状态码 {response.status_code}"
    except Exception as e:
        return f"错误: {str(e)}"

async def get_torrent_list_api(host: str = '', username: str = '', password: str = '') -> str:
    """
    获取种子列表
    """
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        return "登录失败，无法获取SID"
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
                return f"获取种子列表失败: 状态码 {response.status_code}"
    except Exception as e:
        return f"错误: {str(e)}"
    
    