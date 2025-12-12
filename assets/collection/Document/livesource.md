根据您提供的几个版本代码，我将为您整合一个优化的 v1.11 版本。这个版本将以 v1.10 的配置化频道分类为基础，整合 v2.00 和 v3.00 的所有高级功能：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ===== 直播源聚合处理工具 ======
# ======== 版本v1.11 =========
# ========= 优化完整版 ===========

# ========= 模块导入区 =========
import urllib.request
from urllib.parse import urlparse
import re  # 正则
import os
from datetime import datetime, timedelta, timezone
import random
import opencc  # 简繁转换
import socket
import time
import json

# ========= 初始化输出目录 =========
os.makedirs('output', exist_ok=True)  # 创建输出目录，如果已存在则不会报错
print("创建输出目录: output")

# ========= 频道分类配置文件 =========
CHANNEL_CONFIG = {
    # 核心频道
    "yangshi": {
        "file": "主频道/CCTV.txt",
        "lines": [],
        "match_type": "keyword",  # CCTV使用关键词匹配
        "title": "🌐央视频道"
    },
    "weishi": {
        "file": "主频道/卫视.txt",
        "lines": [],
        "match_type": "exact",
        "title": "📡卫视频道"
    },
    
    # 省级地方台
    "beijing": {
        "file": "地方台/北京.txt",
        "lines": [],
        "match_type": "exact",
        "title": "🏛️北京频道"
    },
    "shanghai": {
        "file": "地方台/上海.txt",
        "lines": [],
        "match_type": "exact",
        "title": "🏙️上海频道"
    },
    "guangdong": {
        "file": "地方台/广东.txt",
        "lines": [],
        "match_type": "exact",
        "title": "🐯广东频道"
    },
    "jiangsu": {
        "file": "地方台/江苏.txt",
        "lines": [],
        "match_type": "exact",
        "title": "🎐江苏频道"
    },
    "zhejiang": {
        "file": "地方台/浙江.txt",
        "lines": [],
        "match_type": "exact",
        "title": "🧵浙江频道"
    },
    "shandong": {
        "file": "地方台/山东.txt",
        "lines": [],
        "match_type": "exact",
        "title": "⛰️山东频道"
    },
    "sichuan": {
        "file": "地方台/四川.txt",
        "lines": [],
        "match_type": "exact",
        "title": "🐼四川频道"
    },
    "henan": {
        "file": "地方台/河南.txt",
        "lines": [],
        "match_type": "exact",
        "title": "🐘河南频道"
    },
    "hunan": {
        "file": "地方台/湖南.txt",
        "lines": [],
        "match_type": "exact",
        "title": "🌶️湖南频道"
    },
    "chongqing": {
        "file": "地方台/重庆.txt",
        "lines": [],
        "match_type": "exact",
        "title": "🌉重庆频道"
    },
    "tianjin": {
        "file": "地方台/天津.txt",
        "lines": [],
        "match_type": "exact",
        "title": "🎡天津频道"
    },
    "hubei": {
        "file": "地方台/湖北.txt",
        "lines": [],
        "match_type": "exact",
        "title": "🐉湖北频道"
    },
    "anhui": {
        "file": "地方台/安徽.txt",
        "lines": [],
        "match_type": "exact",
        "title": "🏯安徽频道"
    },
    "fujian": {
        "file": "地方台/福建.txt",
        "lines": [],
        "match_type": "exact",
        "title": "🌊福建频道"
    },
    "liaoning": {
        "file": "地方台/辽宁.txt",
        "lines": [],
        "match_type": "exact",
        "title": "🏀辽宁频道"
    },
    "shaanxi": {
        "file": "地方台/陕西.txt",
        "lines": [],
        "match_type": "exact",
        "title": "🏯陕西频道"
    },
    "hebei": {
        "file": "地方台/河北.txt",
        "lines": [],
        "match_type": "exact",
        "title": "⚓河北频道"
    },
    "jiangxi": {
        "file": "地方台/江西.txt",
        "lines": [],
        "match_type": "exact",
        "title": "⛰️江西频道"
    },
    "guangxi": {
        "file": "地方台/广西.txt",
        "lines": [],
        "match_type": "exact",
        "title": "🐘广西频道"
    },
    "yunnan": {
        "file": "地方台/云南.txt",
        "lines": [],
        "match_type": "exact",
        "title": "🌸云南频道"
    },
    "shanxi": {
        "file": "地方台/山西.txt",
        "lines": [],
        "match_type": "exact",
        "title": "⛰️山西频道"
    },
    "heilongjiang": {
        "file": "地方台/黑龙江.txt",
        "lines": [],
        "match_type": "exact",
        "title": "❄️黑龙江频道"
    },
    "jilin": {
        "file": "地方台/吉林.txt",
        "lines": [],
        "match_type": "exact",
        "title": "🌲吉林频道"
    },
    "guizhou": {
        "file": "地方台/贵州.txt",
        "lines": [],
        "match_type": "exact",
        "title": "🏞️贵州频道"
    },
    "gansu": {
        "file": "地方台/甘肃.txt",
        "lines": [],
        "match_type": "exact",
        "title": "🐫甘肃频道"
    },
    "neimenggu": {
        "file": "地方台/内蒙古.txt",
        "lines": [],
        "match_type": "exact",
        "title": "🐎内蒙古频道"
    },
    "xinjiang": {
        "file": "地方台/新疆.txt",
        "lines": [],
        "match_type": "exact",
        "title": "🍇新疆频道"
    },
    "hainan": {
        "file": "地方台/海南.txt",
        "lines": [],
        "match_type": "exact",
        "title": "🏝️海南频道"
    },
    "ningxia": {
        "file": "地方台/宁夏.txt",
        "lines": [],
        "match_type": "exact",
        "title": "🏜️宁夏频道"
    },
    "qinghai": {
        "file": "地方台/青海.txt",
        "lines": [],
        "match_type": "exact",
        "title": "🏔️青海频道"
    },
    "xizang": {
        "file": "地方台/西藏.txt",
        "lines": [],
        "match_type": "exact",
        "title": "🗻西藏频道"
    },
    
    # 港澳台
    "hongkong": {
        "file": "地方台/香港.txt",
        "lines": [],
        "match_type": "exact",
        "title": "🇭🇰香港频道"
    },
    "macau": {
        "file": "地方台/澳门.txt",
        "lines": [],
        "match_type": "exact",
        "title": "🇲🇴澳门频道"
    },
    "taiwan": {
        "file": "地方台/台湾.txt",
        "lines": [],
        "match_type": "exact",
        "title": "🇨🇳台湾频道"
    },
    
    # 其他分类
    "digital": {
        "file": "主频道/数字.txt",
        "lines": [],
        "match_type": "exact",
        "title": "🔢数字频道"
    },
    "movie": {
        "file": "主频道/电影.txt",
        "lines": [],
        "match_type": "exact",
        "title": "🎬电影频道"
    },
    "tv_drama": {
        "file": "主频道/电视剧.txt",
        "lines": [],
        "match_type": "exact",
        "title": "📺电·视·剧"
    },
    "documentary": {
        "file": "主频道/纪录片.txt",
        "lines": [],
        "match_type": "exact",
        "title": "🎥纪·录·片"
    },
    "cartoon": {
        "file": "主频道/动画片.txt",
        "lines": [],
        "match_type": "exact",
        "title": "🐱动·画·片"
    },
    "radio": {
        "file": "主频道/收音机.txt",
        "lines": [],
        "match_type": "exact",
        "title": "📻收音机"
    },
    "variety": {
        "file": "主频道/综艺.txt",
        "lines": [],
        "match_type": "exact",
        "title": "🎭综艺频道"
    },
    "huya": {
        "file": "主频道/虎牙.txt",
        "lines": [],
        "match_type": "exact",
        "title": "🐯虎牙直播"
    },
    "douyu": {
        "file": "主频道/斗鱼.txt",
        "lines": [],
        "match_type": "exact",
        "title": "🐟斗鱼直播"
    },
    "commentary": {
        "file": "主频道/解说.txt",
        "lines": [],
        "match_type": "exact",
        "title": "🗣️解说频道"
    },
    "music": {
        "file": "主频道/音乐.txt",
        "lines": [],
        "match_type": "exact",
        "title": "🎵音乐频道"
    },
    "food": {
        "file": "主频道/美食.txt",
        "lines": [],
        "match_type": "exact",
        "title": "🍜美食频道"
    },
    "travel": {
        "file": "主频道/旅游.txt",
        "lines": [],
        "match_type": "exact",
        "title": "✈️旅游频道"
    },
    "health": {
        "file": "主频道/健康.txt",
        "lines": [],
        "match_type": "exact",
        "title": "💊健康频道"
    },
    "finance": {
        "file": "主频道/财经.txt",
        "lines": [],
        "match_type": "exact",
        "title": "💰财经频道"
    },
    "shopping": {
        "file": "主频道/购物.txt",
        "lines": [],
        "match_type": "exact",
        "title": "🛒购物频道"
    },
    "game": {
        "file": "主频道/游戏.txt",
        "lines": [],
        "match_type": "exact",
        "title": "🎮游戏频道"
    },
    "news": {
        "file": "主频道/新闻.txt",
        "lines": [],
        "match_type": "exact",
        "title": "📰新闻频道"
    },
    "china": {
        "file": "主频道/中国.txt",
        "lines": [],
        "match_type": "exact",
        "title": "🇨🇳中国频道"
    },
    "international": {
        "file": "主频道/国际.txt",
        "lines": [],
        "match_type": "exact",
        "title": "🌍国际频道"
    },
    "sports": {
        "file": "主频道/体育.txt",
        "lines": [],
        "match_type": "exact",
        "title": "⚽️体育频道"
    },
    "tyss": {
        "file": "主频道/体育赛事.txt",
        "lines": [],
        "match_type": "keyword",
        "title": "🏆️体育赛事"
    },
    "mgss": {
        "file": "主频道/咪咕赛事.txt",
        "lines": [],
        "match_type": "keyword",
        "title": "🏈咪咕赛事"
    },
    "traditional_opera": {
        "file": "主频道/戏曲.txt",
        "lines": [],
        "match_type": "exact",
        "title": "🎭戏曲频道"
    },
    "spring_festival_gala": {
        "file": "主频道/春晚.txt",
        "lines": [],
        "match_type": "exact",
        "title": "🎆历届春晚"
    },
    "camera": {
        "file": "主频道/直播中国.txt",
        "lines": [],
        "match_type": "exact",
        "title": "🏞️景区直播"
    },
    "favorite": {
        "file": "主频道/收藏频道.txt",
        "lines": [],
        "match_type": "exact",
        "title": "⭐收藏频道"
    },
}

# ========= 分类显示顺序配置 =========
CATEGORY_ORDER = [
    "yangshi",      # 央视
    "weishi",       # 卫视
    
    # 省级地方台（按行政区划代码顺序）
    "beijing",      # 北京
    "tianjin",      # 天津
    "hebei",        # 河北
    "shanxi",       # 山西
    "neimenggu",    # 内蒙古
    "liaoning",     # 辽宁
    "jilin",        # 吉林
    "heilongjiang", # 黑龙江
    "shanghai",     # 上海
    "jiangsu",      # 江苏
    "zhejiang",     # 浙江
    "anhui",        # 安徽
    "fujian",       # 福建
    "jiangxi",      # 江西
    "shandong",     # 山东
    "henan",        # 河南
    "hubei",        # 湖北
    "hunan",        # 湖南
    "guangdong",    # 广东
    "guangxi",      # 广西
    "hainan",       # 海南
    "chongqing",    # 重庆
    "sichuan",      # 四川
    "guizhou",      # 贵州
    "yunnan",       # 云南
    "xizang",       # 西藏
    "shaanxi",      # 陕西
    "gansu",        # 甘肃
    "qinghai",      # 青海
    "ningxia",      # 宁夏
    "xinjiang",     # 新疆
    
    # 港澳台
    "hongkong",     # 香港
    "macau",        # 澳门
    "taiwan",       # 台湾
    
    # 其他分类
    "digital",      # 数字
    "tyss",         # 体育赛事
    "mgss",         # 咪咕赛事
    "sports",       # 体育
    "movie",        # 电影
    "tv_drama",     # 电视剧
    "documentary",  # 纪录片
    "cartoon",      # 动画片
    "news",         # 新闻
    "china",        # 中国
    "international", # 国际
    "music",        # 音乐
    "variety",      # 综艺
    "radio",        # 收音机
    "huya",         # 虎牙
    "douyu",        # 斗鱼
    "commentary",   # 解说
    "food",         # 美食
    "travel",       # 旅游
    "health",       # 健康
    "finance",      # 财经
    "shopping",     # 购物
    "game",         # 游戏
    "traditional_opera", # 戏曲
    "spring_festival_gala", # 春晚
    "camera",       # 景区直播
    "favorite",     # 收藏频道
]

# ========= 全局状态变量 =========
class GlobalState:
    def __init__(self):
        self.start_time = None
        self.processed_urls = set()
        self.combined_blacklist = set()
        self.corrections_name = {}
        self.other_lines = []
        self.other_lines_url = set()
        self.logos = {}
        self.stats = {
            'total_processed': 0,
            'total_unique': 0,
            'blacklisted': 0,
            'categories': {}
        }

g = GlobalState()

# ========= 工具函数 =========
def traditional_to_simplified(text: str) -> str:
    converter = opencc.OpenCC('t2s')
    return converter.convert(text)

def get_beijing_time():
    utc_now = datetime.now(timezone.utc)
    return utc_now + timedelta(hours=8)

def read_txt_to_array(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            lines = [line.strip() for line in lines if line.strip()]
            return lines
    except FileNotFoundError:
        print(f"❌ 文件未找到: {file_name}")
        return []
    except Exception as e:
        print(f"❌ 读取文件错误 {file_name}: {e}")
        return []

def get_random_user_agent():
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    ]
    return random.choice(USER_AGENTS)

def clean_url(url):
    last_dollar_index = url.rfind('$')
    if last_dollar_index != -1:
        return url[:last_dollar_index]
    return url

def process_name_string(input_str):
    parts = input_str.split(',')
    processed_parts = []
    for part in parts:
        processed_part = process_part(part)
        processed_parts.append(processed_part)
    result_str = ','.join(processed_parts)
    return result_str

def process_part(part_str):
    if "CCTV" in part_str and "://" not in part_str:
        part_str = part_str.replace("IPV6", "")
        part_str = part_str.replace("PLUS", "+")
        part_str = part_str.replace("1080", "")
        filtered_str = ''.join(char for char in part_str if char.isdigit() or char == 'K' or char == '+')
        if not filtered_str.strip():
            filtered_str = part_str.replace("CCTV", "")
        if len(filtered_str) > 2 and re.search(r'4K|8K', filtered_str):
            filtered_str = re.sub(r'(4K|8K).*', r'\1', filtered_str)
            if len(filtered_str) > 2: 
                filtered_str = re.sub(r'(4K|8K)', r'(\1)', filtered_str)
        return "CCTV" + filtered_str 
    elif "卫视" in part_str:
        pattern = r'卫视「.*」'
        result_str = re.sub(pattern, '卫视', part_str)
        return result_str
    return part_str

def clean_channel_name(channel_name, removal_list):
    for item in removal_list:
        channel_name = channel_name.replace(item, "")
    if channel_name.endswith("HD"):
        channel_name = channel_name[:-2]
    if channel_name.endswith("台") and len(channel_name) > 3:
        channel_name = channel_name[:-1]
    return channel_name

def convert_m3u_to_txt(m3u_content):
    lines = m3u_content.split('\n')
    txt_lines = []
    channel_name = ""
    for line in lines:
        if line.startswith("#EXTM3U"):
            continue
        if line.startswith("#EXTINF"):
            channel_name = line.split(',')[-1].strip()
        elif line.startswith("http") or line.startswith("rtmp") or line.startswith("p3p"):
            txt_lines.append(f"{channel_name},{line.strip()}")
        if "#genre#" not in line and "," in line and "://" in line:
            pattern = r'^[^,]+,[^\s]+://[^\s]+$'
            if bool(re.match(pattern, line)):
                txt_lines.append(line)
    return '\n'.join(txt_lines)

def get_http_response(url, timeout=8, retries=2, backoff_factor=1.0):
    headers = {'User-Agent': get_random_user_agent()}
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                data = response.read()
                return data.decode('utf-8')
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(backoff_factor * (2 ** attempt))
            else:
                print(f"❌ HTTP请求失败 {url}: {e}")
    return None

# ========= 字典和数据处理 =========
def load_dictionaries():
    dictionaries = {}
    for category_id, config in CHANNEL_CONFIG.items():
        file_path = os.path.join('assets/livesource', config['file'])
        if os.path.exists(file_path):
            dictionaries[category_id] = read_txt_to_array(file_path)
            print(f"✅ 加载字典: {category_id} -> {file_path} ({len(dictionaries[category_id])}条)")
        else:
            dictionaries[category_id] = []
            print(f"⚠️  字典文件不存在: {file_path}")
    return dictionaries

def load_corrections_name(filename):
    corrections = {}
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                parts = line.strip().split(',')
                if len(parts) >= 2:
                    correct_name = parts[0]
                    for name in parts[1:]:
                        corrections[name] = correct_name
    except FileNotFoundError:
        print(f"⚠️  纠错文件不存在: {filename}")
    return corrections

def correct_name_data(corrections, data):
    corrected_data = []
    for line in data:
        line = line.strip()
        if ',' not in line:
            continue
        name, url = line.split(',', 1)
        if name in corrections and name != corrections[name]:
            name = corrections[name]
        corrected_data.append(f"{name},{url}")
    return corrected_data

def sort_data(order, data):
    order_dict = {name: i for i, name in enumerate(order)}
    def sort_key(line):
        name = line.split(',')[0]
        return order_dict.get(name, len(order))
    sorted_data = sorted(data, key=sort_key)
    return sorted_data

# ========= 体育赛事处理 =========
def normalize_date_to_md(text):
    """将各种日期格式统一为MM-DD格式"""
    text = text.strip()
    
    def format_md(m):
        month = int(m.group(1))
        day = int(m.group(2))
        after = m.group(3) or ''
        if not after.startswith(' '):
            after = ' ' + after
        return f"{month:02d}-{day:02d}{after}"
    
    text = re.sub(r'^0?(\d{1,2})/0?(\d{1,2})(.*)', format_md, text)
    text = re.sub(r'^\d{4}-0?(\d{1,2})-0?(\d{1,2})(.*)', format_md, text)
    text = re.sub(r'^0?(\d{1,2})月0?(\d{1,2})日(.*)', format_md, text)
    
    return text

def filter_lines(lines, exclude_keywords):
    return [line for line in lines if not any(keyword in line for keyword in exclude_keywords)]

def custom_tyss_sort(lines):
    digit_prefix = []
    others = []
    
    for line in lines:
        name_part = line.split(',')[0].strip()
        if name_part and name_part[0].isdigit():
            digit_prefix.append(line)
        else:
            others.append(line)
    
    digit_prefix_sorted = sorted(digit_prefix, reverse=True)
    others_sorted = sorted(others)
    
    return digit_prefix_sorted + others_sorted

def generate_playlist_html(data_list, output_file='output/tiyu.html'):
    html_head = '''
    <!DOCTYPE html>
    <html lang="zh">
    <head>
        <meta charset="UTF-8">        
        <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6061710286208572"
     crossorigin="anonymous"></script>
        <script async src="https://www.googletagmanager.com/gtag/js?id=G-BS1Z4F5BDN"></script>
        <script> 
        window.dataLayer = window.dataLayer || []; 
        function gtag(){dataLayer.push(arguments);} 
        gtag('js', new Date()); 
        gtag('config', 'G-BS1Z4F5BDN'); 
        </script>
        <title>最新体育赛事</title>
        <style>
            body { font-family: sans-serif; padding: 20px; background: #f9f9f9; }
            .item { margin-bottom: 20px; padding: 12px; background: #fff; border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.06); }
            .title { font-weight: bold; font-size: 1.1em; color: #333; margin-bottom: 5px; }
            .url-wrapper { display: flex; align-items: center; gap: 10px; }
            .url {
                max-width: 80%;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                font-size: 0.9em;
                color: #555;
                background: #f0f0f0;
                padding: 6px;
                border-radius: 4px;
                flex-grow: 1;
            }
            .copy-btn {
                background-color: #007BFF;
                border: none;
                color: white;
                padding: 6px 10px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 0.8em;
            }
            .copy-btn:hover {
                background-color: #0056b3;
            }
        </style>
    </head>
    <body>
    <h2>📋 最新体育赛事列表</h2>
    '''
    
    html_body = ''
    for idx, entry in enumerate(data_list):
        if ',' not in entry:
            continue
        info, url = entry.split(',', 1)
        url_id = f"url_{idx}"
        html_body += f'''
        <div class="item">
            <div class="title">🕒 {info}</div>
            <div class="url-wrapper">
                <div class="url" id="{url_id}">{url}</div>
                <button class="copy-btn" onclick="copyToClipboard('{url_id}')">复制</button>
            </div>
        </div>
        '''
    
    html_tail = '''
    <script>
        function copyToClipboard(id) {
            const el = document.getElementById(id);
            const text = el.textContent;
            navigator.clipboard.writeText(text).then(() => {
                alert("已复制链接！");
            }).catch(err => {
                alert("复制失败: " + err);
            });
        }
    </script>
    </body>
    </html>
    '''
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_head + html_body + html_tail)
    print(f"✅ 体育赛事网页已生成：{output_file}")

def process_tyss_data():
    """处理体育赛事数据"""
    print("🏆 处理体育赛事数据...")
    
    # 从配置中获取体育赛事行
    tyss_lines = CHANNEL_CONFIG["tyss"]["lines"]
    
    if not tyss_lines:
        print("⚠️  没有找到体育赛事数据")
        return
    
    # 日期格式化
    normalized_lines = [normalize_date_to_md(s) for s in tyss_lines]
    
    # 过滤关键词
    keywords_to_exclude_tiyu_txt = ["玉玉软件", "榴芒电视", "公众号", "麻豆", "「回看」"]
    keywords_to_exclude_tiyu = ["玉玉软件", "榴芒电视", "公众号", "咪视通", "麻豆", "「回看」"]
    
    # 应用过滤和排序
    normalized_lines = filter_lines(normalized_lines, keywords_to_exclude_tiyu_txt)
    normalized_lines = custom_tyss_sort(set(normalized_lines))
    filtered_tyss_lines = filter_lines(normalized_lines, keywords_to_exclude_tiyu)
    
    print(f"✅ 体育赛事处理完成: 原始 {len(tyss_lines)} 条, 过滤后 {len(filtered_tyss_lines)} 条")
    
    # 生成HTML页面
    generate_playlist_html(filtered_tyss_lines, 'output/tiyu.html')
    
    # 保存TXT文件
    with open('output/tiyu.txt', 'w', encoding='utf-8') as f:
        for line in filtered_tyss_lines:
            f.write(line + '\n')
    print("✅ 体育赛事文本已保存: output/tiyu.txt")
    
    return filtered_tyss_lines

# ========= 频道分发核心函数 =========
def process_channel_line_config(line, dictionaries, removal_list, is_manual=False):
    """处理单行频道数据，使用配置进行分类
    is_manual: True表示手工区源，绕过黑名单检查
    """
    # 检查是否为有效的频道行
    if "#genre#" not in line and "#EXTINF:" not in line and "," in line and "://" in line:
        parts = line.split(',', 1)
        if len(parts) < 2:
            return
        
        channel_name = parts[0].strip()
        channel_address = parts[1].strip()
        
        # 清理URL
        channel_address = clean_url(channel_address)
        
        # 黑名单检查（手工区源绕过黑名单）
        if not is_manual:
            if channel_address in g.combined_blacklist:
                print(f"🚫 黑名单过滤: {channel_name}")
                g.stats['blacklisted'] += 1
                return
        
        # URL去重检查
        if channel_address in g.processed_urls:
            print(f"🔄 URL去重: {channel_name}")
            return
        
        g.processed_urls.add(channel_address)
        g.stats['total_processed'] += 1
        
        # 清理频道名称
        original_name = channel_name
        channel_name = clean_channel_name(channel_name, removal_list)
        channel_name = traditional_to_simplified(channel_name)
        
        # 频道名称纠错
        if channel_name in g.corrections_name:
            corrected_name = g.corrections_name[channel_name]
            if corrected_name != channel_name:
                print(f"🔧 名称纠错: {channel_name} -> {corrected_name}")
                channel_name = corrected_name
        
        # 重新组合行
        line = channel_name + "," + channel_address
        
        # 按配置顺序匹配分类
        matched = False
        for category_id in CATEGORY_ORDER:
            if category_id not in CHANNEL_CONFIG:
                continue
                
            config = CHANNEL_CONFIG[category_id]
            dict_list = dictionaries.get(category_id, [])
            
            if config["match_type"] == "exact":
                # 精确匹配
                if channel_name in dict_list:
                    CHANNEL_CONFIG[category_id]["lines"].append(process_name_string(line.strip()))
                    matched = True
                    break
            elif config["match_type"] == "keyword":
                # 关键词匹配（特殊处理CCTV）
                if category_id == "yangshi":
                    if "CCTV" in channel_name:
                        CHANNEL_CONFIG[category_id]["lines"].append(process_name_string(line.strip()))
                        matched = True
                        break
                else:
                    # 其他关键词匹配
                    if any(keyword in channel_name for keyword in dict_list):
                        CHANNEL_CONFIG[category_id]["lines"].append(process_name_string(line.strip()))
                        matched = True
                        break
        
        # 如果未匹配到任何分类，放入other
        if not matched:
            if channel_address not in g.other_lines_url:
                g.other_lines_url.add(channel_address)
                g.other_lines.append(line.strip())

# ========= URL处理函数 =========
def process_url_config(url, dictionaries, removal_list):
    """处理单个URL"""
    try:
        print(f"📡 处理URL: {url}")
        g.other_lines.append("◆◆◆　" + url)
        
        req = urllib.request.Request(url)
        req.add_header('User-Agent', get_random_user_agent())
        
        with urllib.request.urlopen(req) as response:
            data = response.read()
            text = data.decode('utf-8').strip()
            
            # 转换M3U格式
            if text.startswith("#EXTM3U") or text.startswith("#EXTINF"):
                text = convert_m3u_to_txt(text)
            
            # 逐行处理
            lines = text.split('\n')
            processed_count = 0
            
            for line in lines:
                if "#genre#" not in line and "," in line and "://" in line and "tvbus://" not in line and "/udp/" not in line:
                    channel_name, channel_address = line.split(',', 1)
                    
                    if "#" not in channel_address:
                        # 普通源
                        process_channel_line_config(line, dictionaries, removal_list, is_manual=False)
                        processed_count += 1
                    else:
                        # 加速源
                        url_list = channel_address.split('#')
                        for channel_url in url_list:
                            newline = f'{channel_name},{channel_url}'
                            process_channel_line_config(newline, dictionaries, removal_list, is_manual=False)
                            processed_count += 1
            
            print(f"  成功处理: {processed_count} 个频道")
            g.other_lines.append('')
            
    except Exception as e:
        print(f"❌ 处理URL时发生错误：{e}")

# ========= 白名单处理 =========
def process_whitelist(dictionaries, removal_list):
    """处理白名单高质量源"""
    print("📋 添加白名单高质量源...")
    
    whitelist_auto_lines = read_txt_to_array('assets/livesource/blacklist/whitelist_auto.txt')
    whitelist_count = 0
    whitelist_rejected_count = 0
    whitelist_error_count = 0
    
    for whitelist_line in whitelist_auto_lines:
        if "#genre#" not in whitelist_line and "," in whitelist_line and "://" in whitelist_line:
            whitelist_parts = whitelist_line.split(",")
            try:
                # 提取响应时间（毫秒）
                response_time = float(whitelist_parts[0].replace("ms", ""))
            except ValueError:
                print(f"❌ 白名单响应时间转换失败: {whitelist_line}")
                response_time = 60000
                whitelist_error_count += 1
            
            # 检查是否有频道名称部分
            if len(whitelist_parts) >= 3:
                channel_name = whitelist_parts[1].strip()
                
                # 只添加响应时间小于2秒的高质量源
                if response_time < 2000:
                    print(f"  ✅ 白名单: {channel_name} ({response_time}ms)")
                    # 手工区源绕过黑名单检查
                    process_channel_line_config(",".join(whitelist_parts[1:]), dictionaries, removal_list, is_manual=True)
                    whitelist_count += 1
                else:
                    print(f"  ⚠️  白名单跳过(响应慢): {channel_name} ({response_time}ms)")
                    whitelist_rejected_count += 1
            else:
                print(f"  ❌ 白名单格式错误: {whitelist_line}")
                whitelist_error_count += 1
    
    print(f"✅ 白名单处理完成: 添加 {whitelist_count} 个，跳过 {whitelist_rejected_count} 个慢速源，{whitelist_error_count} 个格式错误")

# ========= AKTV特殊处理 =========
def process_aktv(dictionaries, removal_list):
    """处理AKTV源"""
    print("📡 获取AKTV源...")
    
    aktv_url = "https://raw.githubusercontent.com/xiaoran67/update/refs/heads/main/assets/livesource/blacklist/whitelist_manual.txt"
    
    aktv_text = get_http_response(aktv_url)
    if aktv_text:
        print("✅ AKTV成功获取内容")
        aktv_text = convert_m3u_to_txt(aktv_text)
        aktv_lines = aktv_text.strip().split('\n')
    else:
        print("⚠️ AKTV请求失败，从本地获取！")
        aktv_lines = read_txt_to_array('assets/livesource/手工区/AKTV.txt')
    
    print(f"处理AKTV数据，共 {len(aktv_lines)} 行")
    for line in aktv_lines:
        process_channel_line_config(line, dictionaries, removal_list, is_manual=False)

# ========= 手工区处理函数 =========
def process_manual_sources(dictionaries, removal_list):
    """处理手工区高质量源（绕过黑名单检查）"""
    print("🔧 处理手工区高质量源（绕过黑名单）...")
    
    # 手工区文件列表
    manual_files = {
        '浙江': '浙江频道.txt',
        '广东': '广东频道.txt',
        '湖北': '湖北频道.txt',
        '上海': '上海频道.txt',
        '江苏': '江苏频道.txt'
    }
    
    for region, filename in manual_files.items():
        filepath = f'assets/livesource/手工区/{filename}'
        lines = read_txt_to_array(filepath)
        if not lines:
            print(f"   ⚠️  {filename}: 文件为空或不存在")
            continue
        
        # 在分类内部去重
        existing_urls = set()
        processed_count = 0
        
        for line in lines:
            if "#genre#" not in line and "," in line and "://" in line:
                parts = line.split(',', 1)
                if len(parts) < 2:
                    continue
                
                channel_name = parts[0].strip()
                channel_address = clean_url(parts[1].strip())
                
                # 只在当前分类内部去重
                if channel_address in existing_urls:
                    continue
                
                # 清理频道名称
                channel_name = clean_channel_name(channel_name, removal_list)
                channel_name = traditional_to_simplified(channel_name)
                
                # 频道名称纠错
                if channel_name in g.corrections_name:
                    corrected_name = g.corrections_name[channel_name]
                    if corrected_name != channel_name:
                        channel_name = corrected_name
                
                # 重新组合行
                processed_line = process_name_string(f"{channel_name},{channel_address}")
                
                # 添加到对应分类
                if region in dictionaries and channel_name in dictionaries[region]:
                    # 查找对应的分类ID
                    for cat_id, config in CHANNEL_CONFIG.items():
                        if cat_id == region.lower():
                            config["lines"].append(processed_line)
                            break
                
                existing_urls.add(channel_address)
                processed_count += 1
        
        print(f"   ✅ {filename}: 添加 {processed_count} 个手工源（分类内已去重）")

# ========= 生成M3U格式文件 =========
def make_m3u(txt_file, m3u_file):
    """生成M3U格式文件"""
    try:
        channels_logos = read_txt_to_array('assets/livesource/logo.txt')
        
        def get_logo_by_channel_name(channel_name):
            for line in channels_logos:
                if not line.strip():
                    continue
                if ',' in line:
                    name, url = line.split(',', 1)
                    if name == channel_name:
                        return url
            return None
        
        output_text = '#EXTM3U x-tvg-url="https://live.fanmingming.cn/e.xml"\n'
        
        with open(txt_file, "r", encoding='utf-8') as file:
            input_text = file.read()
        
        lines = input_text.strip().split("\n")
        group_name = ""
        
        for line in lines:
            parts = line.split(",")
            if len(parts) == 2 and "#genre#" in line:
                group_name = parts[0]
            elif len(parts) == 2:
                channel_name = parts[0]
                channel_url = parts[1]
                logo_url = get_logo_by_channel_name(channel_name)
                
                if logo_url is None:
                    output_text += f"#EXTINF:-1 group-title=\"{group_name}\",{channel_name}\n"
                    output_text += f"{channel_url}\n"
                else:
                    output_text += f"#EXTINF:-1 tvg-name=\"{channel_name}\" tvg-logo=\"{logo_url}\" group-title=\"{group_name}\",{channel_name}\n"
                    output_text += f"{channel_url}\n"
        
        with open(f"{m3u_file}", "w", encoding='utf-8') as file:
            file.write(output_text)
        
        print(f"✅ M3U文件 '{m3u_file}' 生成成功。")
    except Exception as e:
        print(f"❌ 生成M3U文件错误: {e}")

# ========= 今日推荐和版本信息 =========
def get_random_url(file_path):
    """随机获取URL"""
    urls = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                if ',' in line:
                    url = line.strip().split(',')[-1]
                    urls.append(url)
    except Exception as e:
        print(f"❌ 读取随机URL文件错误 {file_path}: {e}")
    return random.choice(urls) if urls else ""

# ========= 生成输出文件 =========
def generate_output_files(filtered_tyss_lines=None):
    """根据配置生成输出文件"""
    print("\n📝 生成输出文件...")
    
    # 读取sports.txt手工源
    sports_manual = read_txt_to_array('assets/livesource/手工区/sports.txt')
    
    # 生成今日推荐和版本信息
    beijing_time = get_beijing_time()
    formatted_time = beijing_time.strftime("%Y%m%d %H:%M:%S")
    
    # 今日推荐
    MTV1 = "💯推荐," + (get_random_url('assets/livesource/手工区/今日推荐.txt') or "")
    MTV2 = "🤫低调," + (get_random_url('assets/livesource/手工区/今日推荐.txt') or "")
    MTV3 = "🟢使用," + (get_random_url('assets/livesource/手工区/今日推荐.txt') or "")
    MTV4 = "⚠️禁止," + (get_random_url('assets/livesource/手工区/今日推荐.txt') or "")
    MTV5 = "🚫贩卖," + (get_random_url('assets/livesource/手工区/今日推荐.txt') or "")
    
    # 版本信息
    version = formatted_time + "," + (get_random_url('assets/livesource/手工区/今日推台.txt') or "")
    about = "👨潇然," + (get_random_url('assets/livesource/手工区/今日推台.txt') or "")
    
    # AKTV源
    aktv_lines = read_txt_to_array('assets/livesource/手工区/AKTV.txt')
    
    # 生成完整版
    all_lines = []
    for category_id in CATEGORY_ORDER:
        if category_id in CHANNEL_CONFIG:
            config = CHANNEL_CONFIG[category_id]
            lines = config["lines"]
            if lines:
                # 对每个分类的行进行排序（使用对应的字典顺序）
                dict_file = config["file"]
                dict_path = os.path.join('assets/livesource', dict_file)
                if os.path.exists(dict_path):
                    order_list = read_txt_to_array(dict_path)
                    sorted_lines = sort_data(order_list, correct_name_data(g.corrections_name, lines))
                    all_lines.append(f"{config['title']},#genre#")
                    all_lines.extend(sorted_lines)
                    all_lines.append('')
                else:
                    all_lines.append(f"{config['title']},#genre#")
                    all_lines.extend(sorted(set(correct_name_data(g.corrections_name, lines))))
                    all_lines.append('')
    
    # 添加SPORTS手工源
    if sports_manual:
        all_lines.append("⚽️SPORTS,#genre#")
        all_lines.extend(sports_manual)
        all_lines.append('')
    
    # 添加AKTV源
    if aktv_lines:
        all_lines.append("🚀 FreeTV,#genre#")
        all_lines.extend(aktv_lines)
        all_lines.append('')
    
    # 添加体育赛事（如果已处理）
    if filtered_tyss_lines:
        all_lines.append("🏆️体育赛事,#genre#")
        all_lines.extend(filtered_tyss_lines)
        all_lines.append('')
    
    # 添加其他分类
    if g.other_lines:
        all_lines.append("📦其他频道,#genre#")
        all_lines.extend(sorted(set(g.other_lines)))
        all_lines.append('')
    
    # 添加更新时间
    all_lines.append("🕒更新时间,#genre#")
    all_lines.append(version)
    all_lines.append(about)
    all_lines.append(MTV1)
    all_lines.append(MTV2)
    all_lines.append(MTV3)
    all_lines.append(MTV4)
    all_lines.append(MTV5)
    all_lines.append('')
    
    # 写入完整版文件
    output_file = "output/full.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in all_lines:
            if line:
                f.write(line + '\n')
    print(f"✅ 完整版已生成: {output_file}")
    
    # 生成精简版（只包含核心分类）
    print("✅ 生成精简版...")
    core_categories = ["yangshi", "weishi", "digital", "tyss", "mgss", "sports"]
    core_lines = []
    
    for category_id in core_categories:
        if category_id in CHANNEL_CONFIG:
            config = CHANNEL_CONFIG[category_id]
            lines = config["lines"]
            if lines:
                dict_file = config["file"]
                dict_path = os.path.join('assets/livesource', dict_file)
                if os.path.exists(dict_path):
                    order_list = read_txt_to_array(dict_path)
                    sorted_lines = sort_data(order_list, correct_name_data(g.corrections_name, lines))
                    core_lines.append(f"{config['title']},#genre#")
                    core_lines.extend(sorted_lines)
                    core_lines.append('')
    
    # 添加更新时间
    core_lines.append("🕒更新时间,#genre#")
    core_lines.append(version)
    core_lines.append(about)
    core_lines.append(MTV1)
    core_lines.append(MTV2)
    core_lines.append(MTV3)
    core_lines.append(MTV4)
    core_lines.append(MTV5)
    core_lines.append('')
    
    lite_file = "output/lite.txt"
    with open(lite_file, 'w', encoding='utf-8') as f:
        for line in core_lines:
            if line:
                f.write(line + '\n')
    print(f"✅ 精简版已生成: {lite_file}")
    
    # 生成定制版
    print("✅ 生成定制版...")
    custom_categories = ["yangshi", "weishi", "tyss", "mgss", "hongkong", "macau", "taiwan"]
    custom_lines = []
    
    for category_id in custom_categories:
        if category_id in CHANNEL_CONFIG:
            config = CHANNEL_CONFIG[category_id]
            lines = config["lines"]
            if lines:
                dict_file = config["file"]
                dict_path = os.path.join('assets/livesource', dict_file)
                if os.path.exists(dict_path):
                    order_list = read_txt_to_array(dict_path)
                    sorted_lines = sort_data(order_list, correct_name_data(g.corrections_name, lines))
                    custom_lines.append(f"{config['title']},#genre#")
                    custom_lines.extend(sorted_lines)
                    custom_lines.append('')
    
    # 添加SPORTS手工源
    if sports_manual:
        custom_lines.append("⚽️SPORTS,#genre#")
        custom_lines.extend(sports_manual)
        custom_lines.append('')
    
    # 添加更新时间
    custom_lines.append("🕒更新时间,#genre#")
    custom_lines.append(version)
    custom_lines.append(about)
    custom_lines.append(MTV1)
    custom_lines.append(MTV2)
    custom_lines.append(MTV3)
    custom_lines.append(MTV4)
    custom_lines.append(MTV5)
    custom_lines.append('')
    
    custom_file = "output/custom.txt"
    with open(custom_file, 'w', encoding='utf-8') as f:
        for line in custom_lines:
            if line:
                f.write(line + '\n')
    print(f"✅ 定制版已生成: {custom_file}")
    
    # 保存未分类源
    others_file = "output/others.txt"
    with open(others_file, 'w', encoding='utf-8') as f:
        for line in g.other_lines:
            f.write(line + '\n')
    print(f"✅ 未分类频道已生成: {others_file}")
    
    # 生成M3U文件
    make_m3u(output_file, output_file.replace(".txt", ".m3u"))
    make_m3u(lite_file, lite_file.replace(".txt", ".m3u"))
    make_m3u(custom_file, custom_file.replace(".txt", ".m3u"))

# ========= 主函数 =========
def main():
    # 执行开始时间
    g.start_time = get_beijing_time()
    print(f"开始时间: {g.start_time.strftime('%Y%m%d %H:%M:%S')}")
    
    print("=" * 60)
    print("🎬 IPTV直播源聚合处理工具 v1.11 - 优化完整版")
    print("=" * 60)
    
    # 显示配置信息
    print(f"📋 已配置 {len(CHANNEL_CONFIG)} 个分类:")
    for i, (category_id, config) in enumerate(CHANNEL_CONFIG.items()):
        print(f"  {i+1:2d}. {config['title']} ({category_id})")
    
    print(f"\n🔄 显示顺序: {len(CATEGORY_ORDER)} 个分类")
    
    # 加载字典
    print("\n📚 加载频道字典...")
    dictionaries = load_dictionaries()
    
    # 读取黑名单
    print("\n🚫 加载黑名单...")
    def read_blacklist_from_txt(file_path):
        blacklist = set()
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            for line in lines:
                if ',' in line:
                    url = line.split(',')[1].strip()
                    cleaned_url = clean_url(url)
                    blacklist.add(cleaned_url)
        except Exception as e:
            print(f"❌ 读取黑名单错误 {file_path}: {e}")
        return blacklist
    
    blacklist_auto = read_blacklist_from_txt('assets/livesource/blacklist/blacklist_auto.txt') 
    blacklist_manual = read_blacklist_from_txt('assets/livesource/blacklist/blacklist_manual.txt') 
    g.combined_blacklist = set(blacklist_auto.union(blacklist_manual))
    
    # 读取纠错文件
    print("🔧 加载纠错字典...")
    g.corrections_name = load_corrections_name('assets/livesource/corrections_name.txt')
    
    # 频道名称清理关键字列表
    removal_list = ["_电信","电信","「LiTV」","频道","频陆","备陆","壹陆","贰陆","叁陆","肆陆","伍陆","陆陆","柒陆",
                    "频晴","频粤","高清","超清","标清","斯特","粤陆","国陆","肆柒","频英","频特","频国","频壹",
                    "频贰","肆贰","频测","咪咕","闽特","高特","频高","频标","汝阳","频效","国标","粤标","频推",
                    "频流","粤高","频限","实时","美推","频美","（HD）","-HD","英陆","_ITV","(北美)","(HK)",
                    "AKtv","「IPV4」","「IPV6」","[HD]","[BD]","[SD]","[VGA]","[超清]","4Gtv","1080","720",
                    "480","HD","SD","4K","VGA","(HD)","(SD)","(4K)","(VGA)","{HD}","{SD}","{4K}","{VGA}",
                    "「4gTV」","「回看」","<HD>","<SD>","<4K>","<VGA>"]
    
    # 读取URL列表
    urls = read_txt_to_array('assets/livesource/urls-daily.txt')
    print(f"\n📡 开始处理 {len(urls)} 个数据源")
    
    # 处理每个URL
    for url in urls:
        if url.startswith("http"):
            # 处理日期占位符
            if "{MMdd}" in url:
                current_date_str = get_beijing_time().strftime("%m%d")
                url = url.replace("{MMdd}", current_date_str)
            if "{MMdd-1}" in url:
                yesterday_date_str = (get_beijing_time() - timedelta(days=1)).strftime("%m%d")
                url = url.replace("{MMdd-1}", yesterday_date_str)
            
            # 处理URL
            process_url_config(url, dictionaries, removal_list)
    
    print(f"\n✅ URL处理完成，共处理 {len(urls)} 个数据源")
    
    # 处理白名单
    process_whitelist(dictionaries, removal_list)
    
    # 处理AKTV源
    process_aktv(dictionaries, removal_list)
    
    # 处理手工区源
    process_manual_sources(dictionaries, removal_list)
    
    # 处理体育赛事
    filtered_tyss_lines = process_tyss_data()
    
    # 生成输出文件
    generate_output_files(filtered_tyss_lines)
    
    # 统计信息
    timeend = get_beijing_time()
    elapsed_time = timeend - g.start_time
    total_seconds = elapsed_time.total_seconds()
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    
    print(f"\n📊 处理统计:")
    print(f"   开始时间: {g.start_time.strftime('%Y%m%d %H:%M:%S')}")
    print(f"   结束时间: {timeend.strftime('%Y%m%d %H:%M:%S')}")
    print(f"   执行时间: {minutes}分{seconds}秒")
    
    # 显示各分类统计
    print(f"\n📈 分类统计:")
    total_channels = 0
    for category_id in CATEGORY_ORDER:
        if category_id in CHANNEL_CONFIG:
            config = CHANNEL_CONFIG[category_id]
            count = len(config["lines"])
            total_channels += count
            if count > 0:
                print(f"   {config['title']}: {count}个频道")
    
    print(f"\n📊 总计: {total_channels} 个频道")
    
    # 生成统计信息JSON
    stats_output = {
        "metadata": {
            "version": "v1.11",
            "start_time": g.start_time.strftime("%Y%m%d %H:%M:%S"),
            "end_time": timeend.strftime("%Y%m%d %H:%M:%S"),
            "duration_seconds": total_seconds,
            "duration_formatted": f"{minutes}分{seconds}秒",
        },
        "statistics": {
            "processed_urls": g.stats['total_processed'],
            "blacklist_urls": len(g.combined_blacklist),
            "total_processed_urls": g.stats['total_processed'] + len(g.combined_blacklist),
            "duplicate_rate": (1 - g.stats['total_processed'] / (g.stats['total_processed'] + len(g.combined_blacklist))) * 100 if (g.stats['total_processed'] + len(g.combined_blacklist)) > 0 else 0,
            "total_channels": total_channels,
            "other_channels": len(g.other_lines),
        },
        "category_counts": {
            "央视": len(CHANNEL_CONFIG["yangshi"]["lines"]),
            "卫视": len(CHANNEL_CONFIG["weishi"]["lines"]),
            "体育赛事": len(filtered_tyss_lines) if filtered_tyss_lines else 0,
            "其他": len(g.other_lines),
        }
    }
    
    try:
        with open('output/statistics.json', 'w', encoding='utf-8') as f:
            json.dump(stats_output, f, ensure_ascii=False, indent=2)
        print("✅ 统计信息已保存到: output/statistics.json")
    except Exception as e:
        print(f"❌ 保存统计信息错误: {e}")

# ========= 启动主函数 =========
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断程序")
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")
    
    print("\n🎉 处理完成！")
    print("💡 提示：")
    print("  1. 修改 CHANNEL_CONFIG 可以增删改分类")
    print("  2. 修改 CATEGORY_ORDER 可以调整显示顺序")
    print("  3. 重新运行脚本即可应用新配置")
```

这个 v1.11 版本整合了以下所有功能：

主要改进：

1. 保持v1.10的配置化优势

· 完全兼容原有的CHANNEL_CONFIG配置
· 保持CATEGORY_ORDER显示顺序配置
· 配置化频道分类，易于增删改

2. 整合v2.00的高级功能

· 白名单处理（绕过黑名单，只添加响应时间<2秒的高质量源）
· 手工区处理（分类内去重，绕过黑名单）
· AKTV特殊处理（网络获取+本地备份）
· 全局URL去重和黑名单检查
· 增强的HTTP请求函数（支持重试和超时）

3. 整合v3.00的完整功能

· 体育赛事日期格式化（MM/DD、YYYY-MM-DD、中文日期统一处理）
· 体育赛事关键词过滤（过滤广告和低质量源）
· 体育赛事HTML页面生成（带复制功能）
· M3U文件生成（支持台标）
· 详细的统计信息（JSON格式）
· 今日推荐和版本信息

4. 性能优化

· 全局状态管理（GlobalState类）
· 内存优化（使用set进行去重）
· 分类排序优化（使用字典顺序排序）

5. 输出文件

· output/full.txt - 完整版（所有分类）
· output/lite.txt - 精简版（核心分类）
· output/custom.txt - 定制版（精选分类）
· output/others.txt - 未分类频道
· output/tiyu.html - 体育赛事HTML页面
· output/tiyu.txt - 体育赛事文本
· output/statistics.json - 统计信息

6. 完全兼容

· 完全兼容v1.10的字典文件和配置
· 保留原有的频道处理逻辑
· 支持原有的所有字典文件结构

这个版本结合了所有版本的优点，提供了最完整的功能和最灵活的自定义能力。