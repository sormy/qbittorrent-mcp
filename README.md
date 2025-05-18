# qBittorrent MCP 服务

qBittorrent MCP 是一个基于 FastMCP 的服务，提供了与 qBittorrent WebUI API 交互的功能接口。

## 功能列表

该服务提供了以下功能：

### 种子管理
- `add_torrent`: 添加种子文件到 qBittorrent
- `delete_torrent`: 删除指定种子（可选同时删除文件）
- `pause_torrent`: 暂停种子下载
- `resume_torrent`: 恢复种子下载
- `get_torrent_list`: 获取所有种子列表

### 跟踪器与标签
- `get_torrent_trackers`: 获取种子的跟踪器列表
- `add_trackers_to_torrent`: 向种子添加新的跟踪器
- `add_torrent_tags`: 为种子添加标签

### 速度与优先级控制
- `set_global_download_limit`: 设置全局下载速度限制
- `set_global_upload_limit`: 设置全局上传速度限制
- `set_torrent_download_limit`: 设置特定种子的下载速度限制
- `set_torrent_upload_limit`: 设置特定种子的上传速度限制
- `set_file_priority`: 设置特定文件的下载优先级

### 系统信息
- `get_application_version`: 获取qBittorrent应用程序版本

## 配置

服务使用以下配置参数：
- `DEFAULT_HOST`: qBittorrent WebUI的主机地址
- `DEFAULT_USERNAME`: qBittorrent WebUI用户名
- `DEFAULT_PASSWORD`: qBittorrent WebUI密码

## 使用方法

1. 确保已安装所需依赖：
   ```
   pip install httpx mcp
   ```

2. 运行MCP服务：
   ```
   python main.py
   ```

## 开发

服务分为两个主要文件：
- `main.py`: 定义MCP服务接口和配置参数
- `api.py`: 实现与qBittorrent WebUI的交互逻辑
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
