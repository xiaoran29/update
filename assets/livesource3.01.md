IPTV直播源聚合处理工具 - 完整文档

🎯 项目概述

IPTV直播源聚合处理工具是一个专业的Python自动化工具，专门用于采集、整理、分类和优化网络直播源。本工具能够从多个公开和私有数据源自动获取直播源，经过智能处理生成高质量的播放列表文件，支持多种播放器和应用场景。

🌟 核心价值

· 自动化处理：完全自动化的采集、去重、分类流程
· 高质量输出：经过多重过滤和优化的高质量直播源
· 多格式支持：同时生成TXT、M3U、HTML等多种格式
· 智能分类：63个精细分类，满足各种观看需求
· 持续维护：每日自动更新，确保源的时效性和可用性

📊 技术架构

系统架构图

```
┌─────────────────────────────────────────────────────┐
│                   数据源层 (Sources)                 │
├─────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────┐ │
│  │  公开源  │  │  私有源  │  │  AKTV源  │  │手工区│ │
│  │ (URL列表)│  │ (白名单) │  │  (GitHub)│  │(本地)│ │
│  └──────────┘  └──────────┘  └──────────┘  └─────┘ │
└─────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────┐
│                 数据处理层 (Processing)              │
├─────────────────────────────────────────────────────┤
│  ┌────────────┐  ┌────────────┐  ┌──────────────┐  │
│  │ 格式转换   │  │ 频道分类   │  │ 名称标准化   │  │
│  │ (M3U↔TXT) │  │ (63类字典) │  │ (清理/纠错)  │  │
│  └────────────┘  └────────────┘  └──────────────┘  │
│  ┌────────────┐  ┌────────────┐  ┌──────────────┐  │
│  │ URL去重    │  │ 黑名单过滤 │  │ 白名单优先   │  │
│  │ (全局集合) │  │ (失效/垃圾)│  │ (高响应源)   │  │
│  └────────────┘  └────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────┐
│                 输出生成层 (Output)                  │
├─────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────┐ │
│  │  完整版  │  │  精简版  │  │  定制版  │  │体育 │ │
│  │ (Full)   │  │ (Lite)   │  │ (Custom) │  │赛事 │ │
│  └──────────┘  └──────────┘  └──────────┘  └─────┘ │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────┐ │
│  │  M3U格式 │  │  HTML版  │  │  统计    │  │日志 │ │
│  │ (带Logo) │  │ (体育)   │  │ (JSON)   │  │文件 │ │
│  └──────────┘  └──────────┘  └──────────┘  └─────┘ │
└─────────────────────────────────────────────────────┘
```

🛠️ 完整安装指南

系统要求

硬件要求

· 最低配置：
  · CPU：双核处理器（Intel Core i3或同等性能）
  · 内存：4GB RAM
  · 存储：10GB可用空间
  · 网络：稳定宽带连接（10Mbps以上）
· 推荐配置：
  · CPU：四核处理器（Intel Core i5或更高）
  · 内存：8GB RAM
  · 存储：20GB SSD可用空间
  · 网络：高速宽带连接（50Mbps以上）

软件要求

· 操作系统：
  · Windows 10/11（64位）
  · macOS 10.14+
  · Ubuntu 18.04+/Debian 10+/CentOS 7+
· Python环境：
  · Python 3.7.0 或更高版本
  · pip 20.0 或更高版本
  · virtualenv（推荐）

详细安装步骤

第一步：克隆项目

```bash
# 使用Git克隆项目（推荐）
git clone https://github.com/xiaoran67/livesource-collector.git
cd livesource-collector

# 或者下载ZIP包
# 1. 访问GitHub项目页面
# 2. 点击 "Code" → "Download ZIP"
# 3. 解压到指定目录
```

第二步：配置Python虚拟环境

```bash
# 创建虚拟环境（Windows）
python -m venv venv
.\venv\Scripts\activate

# 创建虚拟环境（Linux/macOS）
python3 -m venv venv
source venv/bin/activate
```

第三步：安装依赖包

```bash
# 安装核心依赖
pip install opencc>=2.1.0

# 可选：安装开发依赖
pip install requests>=2.25.0
pip install beautifulsoup4>=4.9.0
pip install lxml>=4.6.0

# 验证安装
python -c "import opencc; print('OpenCC版本:', opencc.__version__)"
```

第四步：检查目录结构

确保项目目录结构完整：

```
livesource-collector/
├── assets/livesource/
│   ├── 主频道/           # 必须存在
│   ├── 地方台/           # 必须存在
│   ├── 手工区/           # 必须存在
│   ├── blacklist/        # 必须存在
│   ├── urls-daily.txt    # 必须存在
│   ├── corrections_name.txt  # 必须存在
│   └── logo.txt          # 必须存在
├── output/               # 运行后自动创建
└── livesource.py         # 主程序文件
```

第五步：首次运行测试

```bash
# 测试运行
python livesource.py --test

# 或者直接运行
python livesource.py

# 检查输出目录
ls -la output/
```

📁 目录结构详解

项目根目录

```
livesource-collector/
├── assets/               # 资源目录（核心配置）
├── output/               # 输出目录（程序生成）
├── logs/                 # 日志目录（如果启用日志）
├── tests/                # 测试目录（测试用例）
├── docs/                 # 文档目录（相关文档）
├── requirements.txt      # 依赖包列表
├── livesource.py         # 主程序文件
├── config.yaml           # 配置文件（可选）
├── README.md             # 项目说明文档
├── LICENSE               # 许可证文件
└── .gitignore           # Git忽略文件
```

assets/livesource/ 目录详解

```
assets/livesource/
├── urls-daily.txt                # 数据源URL列表（核心）
├── corrections_name.txt          # 频道名称纠错字典
├── logo.txt                      # 频道Logo映射表
│
├── blacklist/                    # 黑白名单管理
│   ├── blacklist_auto.txt        # 自动黑名单（失效源）
│   ├── blacklist_manual.txt      # 手动黑名单（垃圾源）
│   └── whitelist_auto.txt        # 白名单（高质量源）
│
├── 主频道/                        # 核心频道分类字典
│   ├── CCTV.txt                  # 央视频道列表
│   ├── 卫视.txt                   # 卫视频道列表
│   ├── 数字.txt                   # 数字频道列表
│   ├── 电影.txt                   # 电影频道列表
│   ├── 电视剧.txt                 # 电视剧频道列表
│   ├── 纪录片.txt                 # 纪录片频道列表
│   ├── 动画片.txt                 # 动画片频道列表
│   ├── 收音机.txt                 # 收音机频道列表
│   ├── 综艺.txt                   # 综艺频道列表
│   ├── 虎牙.txt                   # 虎牙直播列表
│   ├── 斗鱼.txt                   # 斗鱼直播列表
│   ├── 解说.txt                   # 解说频道列表
│   ├── 音乐.txt                   # 音乐频道列表
│   ├── 美食.txt                   # 美食频道列表
│   ├── 旅游.txt                   # 旅游频道列表
│   ├── 健康.txt                   # 健康频道列表
│   ├── 财经.txt                   # 财经频道列表
│   ├── 购物.txt                   # 购物频道列表
│   ├── 游戏.txt                   # 游戏频道列表
│   ├── 新闻.txt                   # 新闻频道列表
│   ├── 中国.txt                   # 中国综合频道列表
│   ├── 国际.txt                   # 国际频道列表
│   ├── 体育.txt                   # 体育频道列表
│   ├── 体育赛事.txt               # 体育赛事列表
│   ├── 咪咕赛事.txt               # 咪咕赛事列表
│   ├── 戏曲.txt                   # 戏曲频道列表
│   ├── 春晚.txt                   # 春晚频道列表
│   ├── 直播中国.txt               # 景区直播列表
│   └── 收藏频道.txt               # 收藏频道列表
│
├── 地方台/                        # 省级地方台字典
│   ├── 北京.txt                   # 北京频道列表
│   ├── 上海.txt                   # 上海频道列表
│   ├── 广东.txt                   # 广东频道列表
│   ├── 江苏.txt                   # 江苏频道列表
│   ├── 浙江.txt                   # 浙江频道列表
│   ├── 山东.txt                   # 山东频道列表
│   ├── 四川.txt                   # 四川频道列表
│   ├── 河南.txt                   # 河南频道列表
│   ├── 湖南.txt                   # 湖南频道列表
│   ├── 重庆.txt                   # 重庆频道列表
│   ├── 天津.txt                   # 天津频道列表
│   ├── 湖北.txt                   # 湖北频道列表
│   ├── 安徽.txt                   # 安徽频道列表
│   ├── 福建.txt                   # 福建频道列表
│   ├── 辽宁.txt                   # 辽宁频道列表
│   ├── 陕西.txt                   # 陕西频道列表
│   ├── 河北.txt                   # 河北频道列表
│   ├── 江西.txt                   # 江西频道列表
│   ├── 广西.txt                   # 广西频道列表
│   ├── 云南.txt                   # 云南频道列表
│   ├── 山西.txt                   # 山西频道列表
│   ├── 黑龙江.txt                 # 黑龙江频道列表
│   ├── 吉林.txt                   # 吉林频道列表
│   ├── 贵州.txt                   # 贵州频道列表
│   ├── 甘肃.txt                   # 甘肃频道列表
│   ├── 内蒙.txt                   # 内蒙古频道列表
│   ├── 新疆.txt                   # 新疆频道列表
│   ├── 海南.txt                   # 海南频道列表
│   ├── 宁夏.txt                   # 宁夏频道列表
│   ├── 青海.txt                   # 青海频道列表
│   ├── 西藏.txt                   # 西藏频道列表
│   ├── 香港.txt                   # 香港频道列表
│   ├── 澳门.txt                   # 澳门频道列表
│   └── 闽南.txt                   # 闽南频道列表
│
└── 手工区/                        # 高质量手工源
    ├── AKTV.txt                   # AKTV直播源
    ├── sports.txt                 # 体育赛事手工源
    ├── 今日推荐.txt               # 今日推荐频道
    ├── 今日推台.txt               # 今日推荐电视台
    ├── 浙江频道.txt              # 浙江手工源
    ├── 广东频道.txt              # 广东手工源
    ├── 湖北频道.txt              # 湖北手工源
    ├── 上海频道.txt              # 上海手工源
    └── 江苏频道.txt              # 江苏手工源
```

🔧 配置详解

urls-daily.txt 配置

```txt
# 格式：每行一个URL，支持HTTP/HTTPS协议
# 支持动态日期变量：{MMdd} 和 {MMdd-1}
# 示例：

# 公开数据源
http://example.com/live.txt
https://raw.githubusercontent.com/user/repo/main/live.m3u

# 带日期变量的源（自动替换为当前日期）
http://example.com/live_{MMdd}.txt
https://cdn.example.com/live_{MMdd-1}.m3u

# GitHub源
https://raw.githubusercontent.com/free/live/main/live.txt

# Gitee源（国内加速）
https://gitee.com/user/repo/raw/main/live.txt

# 注释以#开头，支持中英文
# 建议按来源分类，便于管理
```

corrections_name.txt 配置

```txt
# 频道名称纠错字典
# 格式：正确名称,错误名称1,错误名称2,...

# CCTV纠错
CCTV1,CCTV-1,CCTV1综合,CCTV1综合频道
CCTV2,CCTV-2,CCTV2财经,CCTV2财经频道
CCTV5,CCTV-5,CCTV5体育,CCTV5体育频道
CCTV5+,CCTV5PLUS,CCTV5+体育,CCTV5PLUS体育
CCTV4K,CCTV4K超高清,CCTV4K频道
CCTV8K,CCTV8K超高清,CCTV8K频道

# 卫视纠错
湖南卫视,湖南卫视高清,湖南卫视HD
浙江卫视,浙江卫视高清,浙江卫视HD,浙江卫视·中国蓝
江苏卫视,江苏卫视高清,江苏卫视HD
北京卫视,北京卫视高清,北京卫视HD,BTV北京

# 地方台纠错
北京科教,BTV科教,北京电视台科教频道
上海新闻,上海电视台新闻综合频道
广东珠江,广东电视台珠江频道,珠江台

# 统一格式
CCTV-1 → CCTV1
CCTV-5+ → CCTV5+
湖南卫视HD → 湖南卫视
```

logo.txt 配置

```txt
# 频道Logo映射表
# 格式：频道名称,Logo_URL

# 央视Logo
CCTV1,https://example.com/logo/cctv1.png
CCTV2,https://example.com/logo/cctv2.png
CCTV5,https://example.com/logo/cctv5.png
CCTV5+,https://example.com/logo/cctv5plus.png
CCTV4K,https://example.com/logo/cctv4k.png

# 卫视Logo
湖南卫视,https://example.com/logo/hunan.png
浙江卫视,https://example.com/logo/zhejiang.png
江苏卫视,https://example.com/logo/jiangsu.png
北京卫视,https://example.com/logo/beijing.png

# 地方台Logo
北京科教,https://example.com/logo/beijing_kejiao.png
上海新闻,https://example.com/logo/shanghai_news.png
广东珠江,https://example.com/logo/guangdong_zhujiang.png

# 建议使用稳定的Logo源
# 推荐：https://live.fanmingming.com/tv/ 的Logo
```

黑白名单配置

blacklist_auto.txt（自动黑名单）

```txt
# 自动生成的失效源列表
# 格式：响应时间(ms),频道名称,URL

3000,CCTV1,http://expired.com/cctv1.m3u8
5000,湖南卫视,rtmp://dead-server.com/live/hunan
9999,浙江卫视,http://slow-server.com/zhejiang.ts
```

blacklist_manual.txt（手动黑名单）

```txt
# 手动添加的垃圾源
# 格式：备注,URL

广告源,http://ad.com/live.m3u8
钓鱼网站,https://phishing.com/live.txt
低质量源,rtmp://low-quality.com/live
盗版源,http://pirate.com/channels.m3u
```

whitelist_auto.txt（白名单）

```txt
# 高质量源列表（响应时间<2000ms）
# 格式：响应时间(ms),频道名称,URL

150,CCTV1,https://fast-cdn.com/cctv1.m3u8
200,湖南卫视,https://cdn.example.com/hunan.m3u8
300,浙江卫视,https://server.com/zhejiang.m3u8
500,CCTV4K,https://4k-server.com/cctv4k.m3u8
```

🚀 使用指南

基本使用

1. 每日更新（推荐）

```bash
# 每日定时运行（Linux crontab）
0 3 * * * cd /path/to/livesource-collector && python livesource.py

# Windows任务计划程序
# 1. 创建批处理文件 daily_update.bat
# 2. 添加到任务计划，每日凌晨3点执行
```

2. 手动运行

```bash
# 进入项目目录
cd livesource-collector

# 激活虚拟环境（Windows）
venv\Scripts\activate

# 激活虚拟环境（Linux/macOS）
source venv/bin/activate

# 运行主程序
python livesource.py

# 或直接运行（如果已设置环境变量）
./livesource.py
```

3. 查看输出

程序运行后，在 output/ 目录生成以下文件：

```bash
# 查看生成的文件
ls -lh output/

# 文件列表：
# -rw-r--r-- 1 user  group  1.2M Mar 10 10:30 full.txt
# -rw-r--r-- 1 user  group  1.3M Mar 10 10:30 full.m3u
# -rw-r--r-- 1 user  group   50K Mar 10 10:30 lite.txt
# -rw-r--r-- 1 user  group   55K Mar 10 10:30 lite.m3u
# -rw-r--r-- 1 user  group  800K Mar 10 10:30 custom.txt
# -rw-r--r-- 1 user  group  850K Mar 10 10:30 custom.m3u
# -rw-r--r-- 1 user  group  500K Mar 10 10:30 others.txt
# -rw-r--r-- 1 user  group  100K Mar 10 10:30 tiyu.html
# -rw-r--r-- 1 user  group   80K Mar 10 10:30 tiyu.txt
# -rw-r--r-- 1 user  group   10K Mar 10 10:30 statistics.json
```

高级使用

1. 自定义运行参数

```bash
# 仅处理特定分类（需要修改代码）
python livesource.py --category=央视,卫视,体育

# 输出详细日志
python livesource.py --verbose

# 测试模式（不保存文件）
python livesource.py --test

# 指定输出目录
python livesource.py --output=/custom/output/path
```

2. 定时任务配置

Linux (crontab):

```bash
# 编辑crontab
crontab -e

# 添加以下内容（每日凌晨3点运行）
0 3 * * * cd /home/user/livesource-collector && /usr/bin/python3 livesource.py >> /home/user/livesource-collector/logs/cron.log 2>&1

# 每小时运行一次（测试用）
0 * * * * cd /home/user/livesource-collector && /usr/bin/python3 livesource.py >> /home/user/livesource-collector/logs/hourly.log 2>&1
```

Windows (任务计划程序):

1. 打开"任务计划程序"
2. 创建基本任务
3. 触发器：每日，时间：03:00
4. 操作：启动程序
5. 程序/脚本：C:\Python39\python.exe
6. 参数：C:\livesource-collector\livesource.py
7. 起始于：C:\livesource-collector

macOS (launchd):

```xml
<!-- 创建 ~/Library/LaunchAgents/com.user.livesource.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.livesource</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/Users/user/livesource-collector/livesource.py</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>3</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/Users/user/livesource-collector/logs/launchd.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/user/livesource-collector/logs/launchd-error.log</string>
</dict>
</plist>
```

3. 代理配置（如果需要）

```python
# 在代码中添加代理支持（如果需要）
import os
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:1080'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:1080'
```

播放器配置

1. VLC播放器

```xml
<!-- 添加到VLC播放列表 -->
1. 打开VLC播放器
2. 媒体 → 打开网络串流
3. 输入：file:///path/to/output/full.m3u
4. 或者直接拖放full.m3u到VLC窗口
```

2. Kodi/Plex

```xml
<!-- 添加到Kodi -->
1. 进入Kodi主界面
2. 电视 → 电视频道 → 设置
3. 客户端 → PVR IPTV Simple Client
4. 常规 → M3U播放列表URL
5. 输入：/path/to/output/full.m3u
6. 保存并启用
```

3. IPTV播放器（Android/iOS）

```
# 大多数IPTV播放器支持M3U格式
1. 将full.m3u文件传输到手机
2. 在播放器中导入本地M3U文件
3. 或者通过WebDAV/FTP访问
```

4. 网页播放器

```html
<!-- 使用hls.js播放 -->
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
</head>
<body>
    <video id="video" controls></video>
    <script>
        var video = document.getElementById('video');
        var videoSrc = 'https://example.com/live/channel.m3u8';
        
        if(Hls.isSupported()) {
            var hls = new Hls();
            hls.loadSource(videoSrc);
            hls.attachMedia(video);
        } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
            video.src = videoSrc;
        }
    </script>
</body>
</html>
```

📊 输出文件详解

1. full.txt（完整版）

```
完整版包含所有63个分类，文件结构：

🌐央视频道,#genre#
CCTV1,http://example.com/cctv1.m3u8
CCTV2,http://example.com/cctv2.m3u8
...
CCTV4K,http://example.com/cctv4k.m3u8

📡卫视频道,#genre#
湖南卫视,http://example.com/hunan.m3u8
浙江卫视,http://example.com/zhejiang.m3u8
...

🏛️北京频道,#genre#
北京卫视,http://example.com/beijing.m3u8
北京科教,http://example.com/beijing_kejiao.m3u8
...

（共63个分类，约3000-5000个频道）
```

2. lite.txt（精简版）

```
精简版仅包含核心频道，文件结构：

🌐央视频道,#genre#
CCTV1,http://example.com/cctv1.m3u8
CCTV2,http://example.com/cctv2.m3u8
...

📡卫视频道,#genre#
湖南卫视,http://example.com/hunan.m3u8
浙江卫视,http://example.com/zhejiang.m3u8
...

🕒更新时间,#genre#
20250310 10:30:30,http://example.com/version.m3u8
👨潇然,http://example.com/about.m3u8
💯推荐,http://example.com/recommend1.m3u8
🤫低调,http://example.com/recommend2.m3u8
...

（仅2个核心分类 + 更新信息，约50-100个频道）
```

3. custom.txt（定制版）

```
定制版包含完整版中除地方台外的所有分类：

🌐央视频道,#genre#
（同完整版）

📡卫视频道,#genre#
（同完整版）

🏆️体育赛事,#genre#
（体育赛事频道）

🏈咪咕赛事,#genre#
（咪咕赛事频道）

⚽️SPORTS,#genre#
（手工区体育频道）

🚀 FreeTV,#genre#
（AKTV频道）

🇭🇰香港频道,#genre#
（香港频道）

...（所有非地方台分类）

📦其他频道,#genre#
（未分类频道）

🕒更新时间,#genre#
（更新信息）
```

4. full.m3u（M3U格式）

```m3u
#EXTM3U x-tvg-url="https://live.fanmingming.cn/e.xml"
#EXTINF:-1 tvg-name="CCTV1" tvg-logo="http://example.com/logo/cctv1.png" group-title="🌐央视频道",CCTV1
http://example.com/cctv1.m3u8
#EXTINF:-1 tvg-name="CCTV2" tvg-logo="http://example.com/logo/cctv2.png" group-title="🌐央视频道",CCTV2
http://example.com/cctv2.m3u8
...
```

5. tiyu.html（体育赛事网页）

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>最新体育赛事</title>
    <style>
        /* 专业CSS样式 */
    </style>
</head>
<body>
    <h2>📋 最新体育赛事列表</h2>
    <div class="item">
        <div class="title">🕒 03-10 英超：曼城 vs 利物浦</div>
        <div class="url-wrapper">
            <div class="url">http://example.com/premier-league.m3u8</div>
            <button class="copy-btn">复制</button>
        </div>
    </div>
    <!-- 更多赛事 -->
</body>
</html>
```

6. statistics.json（统计信息）

```json
{
  "metadata": {
    "version": "v3.01",
    "start_time": "2025-03-10 10:30:00",
    "end_time": "2025-03-10 10:35:30",
    "duration_seconds": 330,
    "duration_formatted": "5分30秒"
  },
  "statistics": {
    "processed_urls": 12500,
    "blacklist_urls": 1500,
    "total_processed_urls": 14000,
    "duplicate_rate": 10.71,
    "total_lines": 4500,
    "other_lines": 800
  },
  "category_counts": {
    "央视": 25,
    "卫视": 35,
    "体育赛事": 120,
    "其他": 800,
    "北京": 15,
    "上海": 18,
    "广东": 22,
    "浙江": 20
  },
  "performance": {
    "url_processing_time": 180.5,
    "classification_time": 45.2,
    "sorting_time": 30.8,
    "file_writing_time": 73.5
  }
}
```

🔍 故障排除

常见问题

问题1：程序无法启动

```bash
# 错误：ModuleNotFoundError: No module named 'opencc'
# 解决方案：
pip install opencc

# 错误：Permission denied
# 解决方案：
chmod +x livesource.py  # Linux/macOS
# 或以管理员身份运行（Windows）
```

问题2：网络连接失败

```bash
# 错误：urllib.error.URLError
# 解决方案：
1. 检查网络连接
2. 配置代理（如果需要）
3. 调整超时时间（修改代码中的timeout参数）
4. 使用备用数据源
```

问题3：内存不足

```bash
# 错误：MemoryError
# 解决方案：
1. 增加系统内存
2. 修改代码分批处理：
   # 在process_url函数中添加分段处理
   batch_size = 1000
   for i in range(0, len(lines), batch_size):
       batch = lines[i:i+batch_size]
       process_batch(batch)
```

问题4：输出文件过大

```bash
# 输出文件超过10MB
# 解决方案：
1. 启用更严格的黑名单过滤
2. 调整去重阈值
3. 减少数据源数量
4. 启用压缩输出
```

问题5：频道分类错误

```bash
# 频道被错误分类
# 解决方案：
1. 检查corrections_name.txt纠错字典
2. 更新频道字典文件
3. 调整分类逻辑优先级
4. 查看others.txt中的未分类频道
```

调试模式

```bash
# 启用详细日志
python livesource.py --debug

# 或修改代码启用调试
import logging
logging.basicConfig(level=logging.DEBUG)

# 输出处理进度
print(f"已处理 {processed}/{total} 个频道")
```

性能优化

1. 启用缓存

```python
# 添加缓存机制
import pickle
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_channel_info(channel_name):
    # 缓存频道信息
    pass
```

2. 多线程处理

```python
# 使用多线程加速URL处理
import concurrent.futures

def process_urls_parallel(urls, max_workers=5):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_url, url): url for url in urls}
        for future in concurrent.futures.as_completed(futures):
            url = futures[future]
            try:
                future.result()
            except Exception as e:
                print(f"URL处理失败 {url}: {e}")
```

3. 内存优化

```python
# 使用生成器减少内存占用
def read_lines_generator(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            yield line.strip()

# 分批处理大文件
def process_large_file(file_path, batch_size=1000):
    lines = []
    for line in read_lines_generator(file_path):
        lines.append(line)
        if len(lines) >= batch_size:
            process_batch(lines)
            lines = []
    if lines:
        process_batch(lines)
```

📈 监控和维护

监控指标

1. 运行状态监控

```bash
# 检查程序是否在运行
ps aux | grep livesource.py

# 查看最近运行时间
stat output/full.txt

# 检查输出文件大小
du -sh output/*

# 查看日志文件
tail -f logs/livesource.log
```

2. 质量监控

```bash
# 检查频道数量变化
wc -l output/full.txt
wc -l output/full.m3u

# 检查重复率
cat output/full.txt | cut -d',' -f2 | sort | uniq -d | wc -l

# 检查失效链接
# 可以使用curl批量测试
```

3. 性能监控

```bash
# 记录运行时间
time python livesource.py

# 监控内存使用
/usr/bin/time -v python livesource.py

# 生成性能报告
python -m cProfile -o profile.stats livesource.py
```

维护任务

每日维护

1. 检查数据源：确保所有URL可用
2. 更新黑白名单：移除失效源，添加高质量源
3. 备份配置文件：备份重要配置文件
4. 清理旧文件：删除超过7天的旧输出文件

每周维护

1. 更新频道字典：添加新频道，修正错误分类
2. 优化分类逻辑：根据实际情况调整分类规则
3. 性能分析：检查处理时间，优化慢速环节
4. 安全检查：检查代码安全性，更新依赖包

每月维护

1. 架构审查：评估是否需要重构或优化
2. 功能扩展：考虑添加新功能
3. 文档更新：更新README和文档
4. 备份整个项目：完整备份到外部存储

自动化维护脚本

```bash
#!/bin/bash
# maintenance.sh - 自动维护脚本

# 1. 每日更新
echo "=== 每日更新开始 ==="
cd /path/to/livesource-collector
python livesource.py

# 2. 备份输出文件
BACKUP_DIR="/backup/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR
cp -r output/* $BACKUP_DIR/

# 3. 清理旧备份（保留最近7天）
find /backup -type d -mtime +7 -exec rm -rf {} \;

# 4. 发送通知（可选）
# curl -X POST -d "message=维护完成" https://api.example.com/notify

echo "=== 维护完成 ==="
```

🔄 版本迁移指南

从v0.01升级到v1.00

```bash
# 1. 备份原有配置
cp -r assets/ assets_backup_v0.01/

# 2. 下载新版本
git clone https://github.com/xiaoran67/livesource-collector.git v1.00
cd v1.00

# 3. 迁移配置
cp ../assets_backup_v0.01/livesource/* assets/livesource/

# 4. 测试运行
python livesource.py

# 5. 验证输出
diff output/full.txt ../old_output/full.txt
```

从v1.00升级到v2.00

```bash
# 1. 主要变化：手工区去重和JSON统计
# 2. 配置文件完全兼容，直接替换主程序即可

cp livesource_v2.00.py livesource.py
python livesource.py
```

从v2.00升级到v3.01

```bash
# 1. 新增体育赛事处理
# 2. 需要新增体育赛事相关字典文件

# 确保有体育赛事字典文件
ls assets/livesource/主频道/体育赛事.txt

# 如果缺失，从旧版本复制或创建
cp ../v2.00/assets/livesource/主频道/体育赛事.txt assets/livesource/主频道/

# 运行测试
python livesource.py --test
```

📚 开发者指南

代码结构详解

主程序架构

```python
# livesource.py 主要模块

# 1. 导入模块区
import urllib.request, re, os, datetime, random, opencc, socket, time, json

# 2. 配置常量区
class Config:
    OUTPUT_DIR = 'output'
    ASSETS_DIR = 'assets/livesource'
    # ... 其他配置

# 3. 全局状态区
class GlobalState:
    def __init__(self):
        self.processed_urls = set()
        self.combined_blacklist = set()
        # ... 其他状态

# 4. 工具函数区
class Utils:
    @staticmethod
    def get_beijing_time(): ...
    @staticmethod
    def read_txt_to_array(file_path): ...
    # ... 其他工具函数

# 5. 名称处理器
class NameProcessor:
    REMOVAL_LIST = [...]  # 清理关键字
    @classmethod
    def clean_channel_name(cls, name): ...
    # ... 其他名称处理方法

# 6. 文件处理器
class FileProcessor:
    @staticmethod
    def convert_m3u_to_txt(m3u_content): ...
    @staticmethod
    def make_m3u(txt_file, m3u_file): ...
    # ... 其他文件处理方法

# 7. HTTP处理器
class HttpHandler:
    @staticmethod
    def get_http_response(url, timeout=8, retries=2): ...
    # ... 其他HTTP方法

# 8. 数据处理器
class DataProcessor:
    def __init__(self):
        self.channel_dicts = {}
        self._load_all_dicts()
    
    def classify_channel(self, channel_name, line, url): ...
    # ... 其他数据处理方法

# 9. 体育赛事处理器
class SportsProcessor:
    @staticmethod
    def normalize_date_to_md(text): ...
    @staticmethod
    def generate_playlist_html(data_list, output_file): ...
    # ... 其他体育赛事方法

# 10. 主处理器
class LiveSourceProcessor:
    def __init__(self):
        self.utils = Utils()
        self.name_processor = NameProcessor()
        # ... 初始化所有组件
    
    def run(self):
        # 主处理流程
        self._load_blacklist()
        self._process_urls()
        self._process_whitelist()
        self._process_aktv()
        self._process_manual()
        self.sports_processor.process_tyss_data()
        self._generate_outputs()
        self._generate_stats()

# 11. 主函数
def main():
    processor = LiveSourceProcessor()
    processor.run()

if __name__ == "__main__":
    main()
```

添加新功能

示例：添加新分类

```python
# 1. 在CHANNEL_CATEGORIES中添加新分类
CHANNEL_CATEGORIES['content']['4K频道'] = {
    'dict_file': f'{Config.MAIN_CHANNEL_DIR}/4K频道.txt',
    'lines': []
}

# 2. 创建字典文件
# assets/livesource/主频道/4K频道.txt
CCTV4K
CCTV8K
湖南卫视4K
浙江卫视4K
# ... 其他4K频道

# 3. 在输出中添加新分类
# 修改_build_playlist_content方法
content_categories = {
    # ... 现有分类
    '4K频道': '📺 4K超高清,#genre#',
}
```

示例：添加新的数据源类型

```python
class CustomSourceHandler:
    """自定义数据源处理器"""
    
    @staticmethod
    def process_json_source(json_url):
        """处理JSON格式的数据源"""
        content = HttpHandler.get_http_response(json_url)
        if content:
            data = json.loads(content)
            for channel in data['channels']:
                name = channel['name']
                url = channel['url']
                # 处理频道行
                process_channel_line(f"{name},{url}")
    
    @staticmethod  
    def process_xml_source(xml_url):
        """处理XML格式的数据源"""
        # 使用xml.etree.ElementTree解析
        pass
```

性能测试

```python
# performance_test.py - 性能测试脚本
import time
import cProfile
import pstats
from io import StringIO

def run_performance_test():
    """运行性能测试"""
    print("=== 性能测试开始 ===")
    
    # 内存使用测试
    import tracemalloc
    tracemalloc.start()
    
    # 时间测试
    start_time = time.time()
    
    # 运行主程序
    from livesource import main
    main()
    
    # 记录结果
    end_time = time.time()
    snapshot = tracemalloc.take_snapshot()
    tracemalloc.stop()
    
    # 输出结果
    print(f"\n=== 性能测试结果 ===")
    print(f"总运行时间: {end_time - start_time:.2f}秒")
    
    # 内存分析
    top_stats = snapshot.statistics('lineno')
    print("\n内存使用前10名:")
    for stat in top_stats[:10]:
        print(stat)
    
    # 生成性能报告
    pr = cProfile.Profile()
    pr.enable()
    main()
    pr.disable()
    
    s = StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats(20)
    
    with open('performance_report.txt', 'w') as f:
        f.write(s.getvalue())
    
    print("性能报告已保存到: performance_report.txt")

if __name__ == "__main__":
    run_performance_test()
```

🎯 最佳实践

1. 数据源管理

```bash
# 使用多级数据源策略
# 一级源：稳定、高质量（5-10个）
# 二级源：备用源、补充源（10-20个）
# 三级源：测试源、新发现源（动态增减）

# 定期检查数据源可用性
./check_sources.sh
```

2. 频道质量评估

```python
# 质量评分系统
def evaluate_channel_quality(name, url):
    score = 100
    
    # 负分项
    if '广告' in name: score -= 50
    if '测试' in name: score -= 30
    if '备用' in name: score -= 20
    
    # 正分项
    if 'CCTV' in name: score += 10
    if '卫视' in name: score += 5
    if '高清' in name: score += 15
    if '4K' in name: score += 20
    
    # URL质量
    if 'https://' in url: score += 10
    if '.m3u8' in url: score += 5
    
    return max(0, min(100, score))
```

3. 容错处理

```python
# 增强的容错机制
def robust_process_url(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            return process_url(url)
        except Exception as e:
            if attempt == max_retries - 1:
                log_error(f"URL处理失败 {url}: {e}")
                return None
            time.sleep(2 ** attempt)  # 指数退避
```

4. 安全建议

```python
# 输入验证
def validate_input(url):
    # 检查协议
    if not url.startswith(('http://', 'https://')):
        raise ValueError("无效的URL协议")
    
    # 检查域名
    parsed = urlparse(url)
    if not parsed.netloc:
        raise ValueError("无效的URL域名")
    
    # 防止SSRF攻击
    blocked_domains = ['localhost', '127.0.0.1', '192.168.', '10.']
    for blocked in blocked_domains:
        if blocked in parsed.netloc:
            raise ValueError("禁止访问内部网络")
    
    return True
```

📞 支持与贡献

获取帮助

1. 查看文档

· 项目文档：本README.md文件
· 代码注释：详细的代码内注释
· 示例配置：参考config_examples/目录
· 常见问题：查看FAQ.md文件

2. 社区支持

· GitHub Issues：报告bug或请求功能
· Discord频道：实时交流（如果有）
· 邮件列表：订阅更新通知
· QQ群/微信群：中文用户交流

3. 故障诊断

```bash
# 诊断脚本
./diagnose.sh

# 输出诊断信息：
# - Python版本和环境
# - 依赖包状态
# - 目录权限
# - 网络连接
# - 配置文件完整性
```

贡献指南

1. 开发流程

```bash
# 1. Fork项目
git clone https://github.com/xiaoran67/livesource-collector.git
cd livesource-collector

# 2. 创建功能分支
git checkout -b feature/new-classification

# 3. 开发测试
# 编写代码
# 添加测试用例
# 更新文档

# 4. 提交代码
git add .
git commit -m "feat: 添加新的频道分类"

# 5. 推送到远程
git push origin feature/new-classification

# 6. 创建Pull Request
```

2. 代码规范

```python
# PEP 8规范
# 使用4空格缩进
# 行长度不超过79字符
# 函数和类之间空两行
# 导入分组：标准库、第三方库、本地模块

# 文档字符串规范
def process_channel_line(line: str) -> bool:
    """
    处理单行频道数据，进行分类分发。
    
    参数:
        line (str): 频道数据行，格式为"频道名称,URL"
        
    返回:
        bool: 处理是否成功
        
    异常:
        ValueError: 如果行格式无效
        
    示例:
        >>> process_channel_line("CCTV1,http://example.com/cctv1.m3u8")
        True
    """
    # 函数实现
```

3. 测试要求

```python
# 单元测试示例
import unittest
from livesource import process_channel_line

class TestChannelProcessing(unittest.TestCase):
    def test_cctv_channel(self):
        """测试CCTV频道处理"""
        result = process_channel_line("CCTV1,http://example.com/cctv1.m3u8")
        self.assertTrue(result)
        self.assertIn("CCTV1", yangshi_lines)
    
    def test_invalid_line(self):
        """测试无效行处理"""
        with self.assertRaises(ValueError):
            process_channel_line("无效的行格式")
    
    def test_blacklisted_url(self):
        """测试黑名单URL过滤"""
        # 先添加URL到黑名单
        combined_blacklist.add("http://blacklisted.com/channel.m3u8")
        
        result = process_channel_line("测试频道,http://blacklisted.com/channel.m3u8")
        self.assertFalse(result)

# 运行测试
if __name__ == '__main__':
    unittest.main()
```

📄 许可证信息

MIT许可证

```
版权所有 (c) 2025 潇然

特此免费授予任何获得本软件及相关文档文件（以下简称"软件"）副本的人，
不受限制地处理本软件，包括但不限于使用、复制、修改、合并、发布、分发、再许可和/或销售本软件的副本，
以及允许提供本软件的人这样做，但须符合以下条件：

上述版权声明和本许可声明应包含在本软件的所有副本或重要部分中。

本软件"按原样"提供，不提供任何明示或暗示的担保，包括但不限于适销性、
特定用途适用性和非侵权性的担保。在任何情况下，作者或版权持有人均不对
因本软件或本软件的使用或其他交易而引起的任何索赔、损害或其他责任负责，
无论是在合同诉讼、侵权行为还是其他方面。
```

使用限制

1. 个人使用：允许个人非商业使用
2. 商业使用：需要获得明确授权
3. 分发修改：可以分发修改版本，但必须保留原版权声明
4. 责任限制：作者不对使用本软件造成的任何损失负责

第三方组件

```
opencc (MIT License) - 简繁转换库
requests (Apache 2.0) - HTTP客户端库
beautifulsoup4 (MIT) - HTML解析库
lxml (BSD) - XML处理库
```

📈 项目路线图

短期目标 (v3.x)

· 添加Web管理界面
· 支持更多数据源格式（JSON、XML、RSS）
· 实现智能源质量评估
· 添加频道EPG信息
· 支持用户自定义分类

中期目标 (v4.x)

· 分布式数据采集
· 实时源监控和自动切换
· 机器学习优化分类
· 多语言支持
· API接口开发

长期目标 (v5.x)

· 云服务部署
· 移动端应用
· 社区贡献系统
· 商业支持版本
· 生态系统建设

🏆 致谢

贡献者

· 潇然 - 项目创始人、核心开发者
· 所有贡献者 - 感谢每一位提交PR和Issue的用户
· 数据源提供者 - 感谢公开分享直播源的社区成员

技术支持

· GitHub - 代码托管和协作平台
· Python社区 - 提供了强大的生态系统
· 开源社区 - 所有依赖的开源项目

特别感谢

感谢所有使用本项目的用户，你们的反馈和建议让这个项目变得更好！

🔗 相关链接

· 项目主页：https://github.com/xiaoran67/livesource-collector
· 问题反馈：https://github.com/xiaoran67/livesource-collector/issues
· Wiki文档：https://github.com/xiaoran67/livesource-collector/wiki
· 更新日志：https://github.com/xiaoran67/livesource-collector/releases
· 讨论区：https://github.com/xiaoran67/livesource-collector/discussions

---

最后更新：2025年3月10日
版本：v3.01
作者：潇然
联系方式：xiaoran@example.com

感谢使用IPTV直播源聚合处理工具，祝您使用愉快！ 🎉
