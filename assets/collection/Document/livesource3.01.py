#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ===== 直播源聚合处理工具 ======
# ========= 版本v3.01 =========
# ======= 修复体育赛事版 =========

import urllib.request
from urllib.parse import urlparse
import re
import os
from datetime import datetime, timedelta, timezone
import random
import opencc
import socket
import time
import json
from typing import Dict, List, Set, Optional, Any

# ========= 常量定义 =========
class Config:
    """配置常量"""
    OUTPUT_DIR = 'output'
    ASSETS_DIR = 'assets/livesource'
    BLACKLIST_DIR = f'{ASSETS_DIR}/blacklist'
    MANUAL_DIR = f'{ASSETS_DIR}/手工区'
    REGION_DIR = f'{ASSETS_DIR}/地方台'
    MAIN_CHANNEL_DIR = f'{ASSETS_DIR}/主频道'
    
    URLS_FILE = f'{ASSETS_DIR}/urls-daily.txt'
    CORRECTIONS_FILE = f'{ASSETS_DIR}/corrections_name.txt'
    LOGO_FILE = f'{ASSETS_DIR}/logo.txt'
    
    # 输出文件
    OUTPUT_FULL = f'{OUTPUT_DIR}/full.txt'
    OUTPUT_LITE = f'{OUTPUT_DIR}/lite.txt'
    OUTPUT_CUSTOM = f'{OUTPUT_DIR}/custom.txt'
    OUTPUT_OTHERS = f'{OUTPUT_DIR}/others.txt'
    OUTPUT_TIYU_HTML = f'{OUTPUT_DIR}/tiyu.html'
    OUTPUT_TIYU_TXT = f'{OUTPUT_DIR}/tiyu.txt'
    
    # 黑名单文件
    BLACKLIST_AUTO = f'{BLACKLIST_DIR}/blacklist_auto.txt'
    BLACKLIST_MANUAL = f'{BLACKLIST_DIR}/blacklist_manual.txt'
    WHITELIST_AUTO = f'{BLACKLIST_DIR}/whitelist_auto.txt'
    
    # AKTV源
    AKTV_URL = "https://raw.githubusercontent.com/xiaoran67/update/refs/heads/main/assets/livesource/%E6%89%8B%E5%B7%A5%E5%8C%BA/channels.txt"
    AKTV_LOCAL = f'{MANUAL_DIR}/AKTV.txt'

# ========= 频道分类配置 =========
CHANNEL_CATEGORIES = {
    'core': {
        '央视': {'dict_file': f'{Config.MAIN_CHANNEL_DIR}/CCTV.txt', 'lines': []},
        '卫视': {'dict_file': f'{Config.MAIN_CHANNEL_DIR}/卫视.txt', 'lines': []},
    },
    
    'regions': {
        '北京': {'dict_file': f'{Config.REGION_DIR}/北京.txt', 'lines': []},
        '上海': {'dict_file': f'{Config.REGION_DIR}/上海.txt', 'lines': []},
        '广东': {'dict_file': f'{Config.REGION_DIR}/广东.txt', 'lines': []},
        '江苏': {'dict_file': f'{Config.REGION_DIR}/江苏.txt', 'lines': []},
        '浙江': {'dict_file': f'{Config.REGION_DIR}/浙江.txt', 'lines': []},
        '山东': {'dict_file': f'{Config.REGION_DIR}/山东.txt', 'lines': []},
        '四川': {'dict_file': f'{Config.REGION_DIR}/四川.txt', 'lines': []},
        '河南': {'dict_file': f'{Config.REGION_DIR}/河南.txt', 'lines': []},
        '湖南': {'dict_file': f'{Config.REGION_DIR}/湖南.txt', 'lines': []},
        '重庆': {'dict_file': f'{Config.REGION_DIR}/重庆.txt', 'lines': []},
        '天津': {'dict_file': f'{Config.REGION_DIR}/天津.txt', 'lines': []},
        '湖北': {'dict_file': f'{Config.REGION_DIR}/湖北.txt', 'lines': []},
        '安徽': {'dict_file': f'{Config.REGION_DIR}/安徽.txt', 'lines': []},
        '福建': {'dict_file': f'{Config.REGION_DIR}/福建.txt', 'lines': []},
        '辽宁': {'dict_file': f'{Config.REGION_DIR}/辽宁.txt', 'lines': []},
        '陕西': {'dict_file': f'{Config.REGION_DIR}/陕西.txt', 'lines': []},
        '河北': {'dict_file': f'{Config.REGION_DIR}/河北.txt', 'lines': []},
        '江西': {'dict_file': f'{Config.REGION_DIR}/江西.txt', 'lines': []},
        '广西': {'dict_file': f'{Config.REGION_DIR}/广西.txt', 'lines': []},
        '云南': {'dict_file': f'{Config.REGION_DIR}/云南.txt', 'lines': []},
        '山西': {'dict_file': f'{Config.REGION_DIR}/山西.txt', 'lines': []},
        '黑龙江': {'dict_file': f'{Config.REGION_DIR}/黑龙江.txt', 'lines': []},
        '吉林': {'dict_file': f'{Config.REGION_DIR}/吉林.txt', 'lines': []},
        '贵州': {'dict_file': f'{Config.REGION_DIR}/贵州.txt', 'lines': []},
        '甘肃': {'dict_file': f'{Config.REGION_DIR}/甘肃.txt', 'lines': []},
        '内蒙古': {'dict_file': f'{Config.REGION_DIR}/内蒙.txt', 'lines': []},
        '新疆': {'dict_file': f'{Config.REGION_DIR}/新疆.txt', 'lines': []},
        '海南': {'dict_file': f'{Config.REGION_DIR}/海南.txt', 'lines': []},
        '宁夏': {'dict_file': f'{Config.REGION_DIR}/宁夏.txt', 'lines': []},
        '青海': {'dict_file': f'{Config.REGION_DIR}/青海.txt', 'lines': []},
        '西藏': {'dict_file': f'{Config.REGION_DIR}/西藏.txt', 'lines': []},
    },
    
    'special_regions': {
        '香港': {'dict_file': f'{Config.REGION_DIR}/香港.txt', 'lines': []},
        '澳门': {'dict_file': f'{Config.REGION_DIR}/澳门.txt', 'lines': []},
        '闽南': {'dict_file': f'{Config.REGION_DIR}/闽南.txt', 'lines': []},
    },
    
    'content': {
        '数字': {'dict_file': f'{Config.MAIN_CHANNEL_DIR}/数字.txt', 'lines': []},
        '电影': {'dict_file': f'{Config.MAIN_CHANNEL_DIR}/电影.txt', 'lines': []},
        '电视剧': {'dict_file': f'{Config.MAIN_CHANNEL_DIR}/电视剧.txt', 'lines': []},
        '纪录片': {'dict_file': f'{Config.MAIN_CHANNEL_DIR}/纪录片.txt', 'lines': []},
        '动画片': {'dict_file': f'{Config.MAIN_CHANNEL_DIR}/动画片.txt', 'lines': []},
        '收音机': {'dict_file': f'{Config.MAIN_CHANNEL_DIR}/收音机.txt', 'lines': []},
        '综艺': {'dict_file': f'{Config.MAIN_CHANNEL_DIR}/综艺.txt', 'lines': []},
        '虎牙': {'dict_file': f'{Config.MAIN_CHANNEL_DIR}/虎牙.txt', 'lines': []},
        '斗鱼': {'dict_file': f'{Config.MAIN_CHANNEL_DIR}/斗鱼.txt', 'lines': []},
        '解说': {'dict_file': f'{Config.MAIN_CHANNEL_DIR}/解说.txt', 'lines': []},
        '音乐': {'dict_file': f'{Config.MAIN_CHANNEL_DIR}/音乐.txt', 'lines': []},
        '美食': {'dict_file': f'{Config.MAIN_CHANNEL_DIR}/美食.txt', 'lines': []},
        '旅游': {'dict_file': f'{Config.MAIN_CHANNEL_DIR}/旅游.txt', 'lines': []},
        '健康': {'dict_file': f'{Config.MAIN_CHANNEL_DIR}/健康.txt', 'lines': []},
        '财经': {'dict_file': f'{Config.MAIN_CHANNEL_DIR}/财经.txt', 'lines': []},
        '购物': {'dict_file': f'{Config.MAIN_CHANNEL_DIR}/购物.txt', 'lines': []},
        '游戏': {'dict_file': f'{Config.MAIN_CHANNEL_DIR}/游戏.txt', 'lines': []},
        '新闻': {'dict_file': f'{Config.MAIN_CHANNEL_DIR}/新闻.txt', 'lines': []},
        '中国': {'dict_file': f'{Config.MAIN_CHANNEL_DIR}/中国.txt', 'lines': []},
        '国际': {'dict_file': f'{Config.MAIN_CHANNEL_DIR}/国际.txt', 'lines': []},
        '体育': {'dict_file': f'{Config.MAIN_CHANNEL_DIR}/体育.txt', 'lines': []},
        '体育赛事': {'dict_file': f'{Config.MAIN_CHANNEL_DIR}/体育赛事.txt', 'lines': []},
        '咪咕赛事': {'dict_file': f'{Config.MAIN_CHANNEL_DIR}/咪咕赛事.txt', 'lines': []},
        '戏曲': {'dict_file': f'{Config.MAIN_CHANNEL_DIR}/戏曲.txt', 'lines': []},
        '春晚': {'dict_file': f'{Config.MAIN_CHANNEL_DIR}/春晚.txt', 'lines': []},
        '直播中国': {'dict_file': f'{Config.MAIN_CHANNEL_DIR}/直播中国.txt', 'lines': []},
        '收藏频道': {'dict_file': f'{Config.MAIN_CHANNEL_DIR}/收藏频道.txt', 'lines': []},
    }
}

# ========= 全局变量 =========
class GlobalState:
    """全局状态管理"""
    def __init__(self):
        self.start_time = None
        self.processed_urls: Set[str] = set()
        self.combined_blacklist: Set[str] = set()
        self.corrections_name: Dict[str, str] = {}
        self.other_lines: List[str] = []
        self.other_lines_url: Set[str] = set()
        self.logos: Dict[str, str] = {}
        self.stats: Dict[str, Any] = {
            'total_processed': 0,
            'total_unique': 0,
            'blacklisted': 0,
            'categories': {}
        }
        # 新增：体育赛事相关
        self.tyss_lines: List[str] = []  # 体育赛事原始行
        self.filtered_tyss_lines: List[str] = []  # 处理后的体育赛事行
        self.mgss_lines: List[str] = []  # 咪咕赛事行
    
    def reset(self):
        """重置状态（测试用）"""
        self.__init__()

g = GlobalState()

# ========= 工具函数 =========
class Utils:
    """工具函数集合"""
    
    @staticmethod
    def get_beijing_time() -> datetime:
        """获取北京时间"""
        utc_now = datetime.now(timezone.utc)
        return utc_now + timedelta(hours=8)
    
    @staticmethod
    def read_txt_to_array(file_path: str) -> List[str]:
        """读取文本文件到数组"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"⚠️ 文件不存在: {file_path}")
            return []
        except Exception as e:
            print(f"❌ 读取文件错误 {file_path}: {e}")
            return []
    
    @staticmethod
    def get_random_user_agent() -> str:
        """随机User-Agent"""
        agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        ]
        return random.choice(agents)
    
    @staticmethod
    def clean_url(url: str) -> str:
        """清理URL中的$符号"""
        if '$' in url:
            return url[:url.rfind('$')]
        return url
    
    @staticmethod
    def traditional_to_simplified(text: str) -> str:
        """繁体转简体"""
        converter = opencc.OpenCC('t2s')
        return converter.convert(text)

# ========= 名称处理类 =========
class NameProcessor:
    """频道名称处理器"""
    
    REMOVAL_LIST = [
        "_电信", "电信", "「LiTV」", "频道", "频陆", "备陆", "壹陆", "贰陆", "叁陆", "肆陆",
        "伍陆", "陆陆", "柒陆", "频晴", "频粤", "高清", "超清", "标清", "斯特", "粤陆",
        "国陆", "肆柒", "频英", "频特", "频国", "频壹", "频贰", "肆贰", "频测", "咪咕",
        "闽特", "高特", "频高", "频标", "汝阳", "频效", "国标", "粤标", "频推", "频流",
        "粤高", "频限", "实时", "美推", "频美", "（HD）", "-HD", "英陆", "_ITV", "(北美)",
        "(HK)", "AKtv", "「IPV4」", "「IPV6」", "[HD]", "[BD]", "[SD]", "[VGA]", "[超清]",
        "4Gtv", "1080", "720", "480", "HD", "SD", "4K", "VGA", "(HD)", "(SD)", "(4K)",
        "(VGA)", "{HD}", "{SD}", "{4K}", "{VGA}", "「4gTV」", "「回看」", "<HD>", "<SD>",
        "<4K>", "<VGA>"
    ]
    
    @classmethod
    def clean_channel_name(cls, name: str) -> str:
        """清理频道名称"""
        # 移除特定关键字
        for item in cls.REMOVAL_LIST:
            name = name.replace(item, "")
        
        # 移除末尾HD
        if name.endswith("HD"):
            name = name[:-2]
        
        # 移除末尾"台"
        if name.endswith("台") and len(name) > 3:
            name = name[:-1]
        
        return name
    
    @staticmethod
    def process_cctv_name(name: str) -> str:
        """处理CCTV名称"""
        if "CCTV" not in name or "://" in name:
            return name
        
        name = name.replace("IPV6", "").replace("PLUS", "+").replace("1080", "")
        filtered = ''.join(c for c in name if c.isdigit() or c in 'K+')
        
        if not filtered.strip():
            filtered = name.replace("CCTV", "")
        
        # 处理4K/8K
        if len(filtered) > 2 and re.search(r'4K|8K', filtered):
            filtered = re.sub(r'(4K|8K).*', r'\1', filtered)
            if len(filtered) > 2:
                filtered = re.sub(r'(4K|8K)', r'(\1)', filtered)
        
        return f"CCTV{filtered}"
    
    @staticmethod
    def process_weishi_name(name: str) -> str:
        """处理卫视名称"""
        return re.sub(r'卫视「.*」', '卫视', name)

# ========= 文件格式处理 =========
class FileProcessor:
    """文件格式处理器"""
    
    @staticmethod
    def convert_m3u_to_txt(m3u_content: str) -> str:
        """M3U转TXT"""
        lines = m3u_content.split('\n')
        txt_lines = []
        channel_name = ""
        
        for line in lines:
            if line.startswith("#EXTM3U"):
                continue
            elif line.startswith("#EXTINF"):
                channel_name = line.split(',')[-1].strip()
            elif line.startswith(("http", "rtmp", "p3p")):
                txt_lines.append(f"{channel_name},{line.strip()}")
            elif "#genre#" not in line and "," in line and "://" in line:
                pattern = r'^[^,]+,[^\s]+://[^\s]+$'
                if re.match(pattern, line):
                    txt_lines.append(line)
        
        return '\n'.join(txt_lines)
    
    @staticmethod
    def make_m3u(txt_file: str, m3u_file: str):
        """生成M3U文件"""
        try:
            output = '#EXTM3U x-tvg-url="https://live.fanmingming.cn/e.xml"\n'
            
            with open(txt_file, "r", encoding='utf-8') as f:
                content = f.read()
            
            group_name = ""
            for line in content.strip().split("\n"):
                parts = line.split(",")
                if len(parts) == 2 and "#genre#" in line:
                    group_name = parts[0]
                elif len(parts) == 2:
                    channel_name, channel_url = parts
                    logo = g.logos.get(channel_name)
                    
                    if logo:
                        output += f'#EXTINF:-1 tvg-name="{channel_name}" tvg-logo="{logo}" group-title="{group_name}",{channel_name}\n'
                    else:
                        output += f'#EXTINF:-1 group-title="{group_name}",{channel_name}\n'
                    output += f"{channel_url}\n"
            
            with open(m3u_file, "w", encoding='utf-8') as f:
                f.write(output)
            
            print(f"✅ M3U文件生成成功: {m3u_file}")
        except Exception as e:
            print(f"❌ 生成M3U错误: {e}")

# ========= HTTP处理器 =========
class HttpHandler:
    """HTTP请求处理器"""
    
    @staticmethod
    def get_http_response(url: str, timeout: int = 8, retries: int = 2) -> Optional[str]:
        """获取HTTP响应"""
        headers = {'User-Agent': Utils.get_random_user_agent()}
        
        for attempt in range(retries):
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    return resp.read().decode('utf-8')
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(1.0 * (2 ** attempt))
                else:
                    print(f"❌ HTTP请求失败 {url}: {e}")
        
        return None

# ========= 数据处理器 =========
class DataProcessor:
    """数据处理核心"""
    
    def __init__(self):
        self.channel_dicts = {}
        self._load_all_dicts()
    
    def _load_all_dicts(self):
        """加载所有字典"""
        print("📋 加载频道字典...")
        
        # 递归加载字典
        def load_dicts(category_dict):
            for name, config in category_dict.items():
                dict_file = config['dict_file']
                if os.path.exists(dict_file):
                    self.channel_dicts[name] = Utils.read_txt_to_array(dict_file)
                    print(f"  ✅ {name}: {len(self.channel_dicts[name])}条")
                else:
                    print(f"  ⚠️  字典文件不存在: {dict_file}")
                    self.channel_dicts[name] = []
        
        for category in CHANNEL_CATEGORIES.values():
            load_dicts(category)
    
    def classify_channel(self, channel_name: str, line: str, url: str) -> bool:
        """分类频道"""
        # 特殊处理：体育赛事和咪咕赛事（需要检查是否包含关键字）
        tyss_keywords = self.channel_dicts.get('体育赛事', [])
        mgss_keywords = self.channel_dicts.get('咪咕赛事', [])
        
        # 检查体育赛事
        if tyss_keywords and any(keyword in channel_name for keyword in tyss_keywords):
            g.tyss_lines.append(line)
            return True
        
        # 检查咪咕赛事
        if mgss_keywords and any(keyword in channel_name for keyword in mgss_keywords):
            g.mgss_lines.append(line)
            return True
        
        # 央视特殊处理
        if "CCTV" in channel_name:
            self._add_to_category('央视', line)
            return True
        
        # 其他分类
        for category_name, dict_data in self.channel_dicts.items():
            if channel_name in dict_data:
                self._add_to_category(category_name, line)
                return True
        
        # 未分类
        if url not in g.other_lines_url:
            g.other_lines_url.add(url)
            g.other_lines.append(line)
        
        return False
    
    def _add_to_category(self, category_name: str, line: str):
        """添加到分类"""
        for category_type in CHANNEL_CATEGORIES.values():
            if category_name in category_type:
                category_type[category_name]['lines'].append(line)
                break
    
    def sort_category_lines(self, category_name: str) -> List[str]:
        """排序分类行"""
        if category_name not in self.channel_dicts:
            return []
        
        dict_order = self.channel_dicts[category_name]
        order_dict = {name: i for i, name in enumerate(dict_order)}
        
        # 获取分类行
        lines = []
        for category_type in CHANNEL_CATEGORIES.values():
            if category_name in category_type:
                lines = category_type[category_name]['lines']
                break
        
        def sort_key(line):
            name = line.split(',')[0]
            return order_dict.get(name, len(order_dict))
        
        return sorted(set(lines), key=sort_key)

# ========= 体育赛事处理器 =========
class SportsProcessor:
    """体育赛事专用处理器"""
    
    # 过滤关键词
    EXCLUDE_KEYWORDS_TXT = ["玉玉软件", "榴芒电视", "公众号", "麻豆", "「回看」"]
    EXCLUDE_KEYWORDS = ["玉玉软件", "榴芒电视", "公众号", "咪视通", "麻豆", "「回看」"]
    
    @staticmethod
    def normalize_date_to_md(text: str) -> str:
        """将各种日期格式统一为MM-DD格式"""
        text = text.strip()
        
        def format_md(m):
            month = int(m.group(1))
            day = int(m.group(2))
            after = m.group(3) or ''
            if not after.startswith(' '):
                after = ' ' + after
            return f"{month:02d}-{day:02d}{after}"
        
        # MM/DD 或 M/D
        text = re.sub(r'^0?(\d{1,2})/0?(\d{1,2})(.*)', format_md, text)
        
        # YYYY-MM-DD 或类似形式
        text = re.sub(r'^\d{4}-0?(\d{1,2})-0?(\d{1,2})(.*)', format_md, text)
        
        # 中文M月D日格式
        text = re.sub(r'^0?(\d{1,2})月0?(\d{1,2})日(.*)', format_md, text)
        
        return text
    
    @staticmethod
    def filter_lines(lines: List[str], exclude_keywords: List[str]) -> List[str]:
        """过滤包含关键字的行"""
        return [line for line in lines if not any(keyword in line for keyword in exclude_keywords)]
    
    @staticmethod
    def custom_tyss_sort(lines: List[str]) -> List[str]:
        """体育赛事专用排序"""
        digit_prefix = []
        others = []
        
        for line in lines:
            name_part = line.split(',')[0].strip()
            if name_part and name_part[0].isdigit():
                digit_prefix.append(line)
            else:
                others.append(line)
        
        # 分别排序：数字开头倒序，其他升序
        digit_prefix_sorted = sorted(digit_prefix, reverse=True)
        others_sorted = sorted(others)
        
        return digit_prefix_sorted + others_sorted
    
    @staticmethod
    def generate_playlist_html(data_list: List[str], output_file: str):
        """生成HTML播放列表"""
        html_head = '''
        <!DOCTYPE html>
        <html lang="zh">
        <head>
            <meta charset="UTF-8">        
            <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6061710286208572"
         crossorigin="anonymous"></script>
            <!-- Setup Google Analytics -->
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
    
    def process_tyss_data(self):
        """处理体育赛事数据"""
        print("🏆 处理体育赛事数据...")
        
        if not g.tyss_lines:
            print("⚠️  没有找到体育赛事数据")
            return
        
        # 1. 日期格式化
        normalized_lines = [self.normalize_date_to_md(line) for line in g.tyss_lines]
        
        # 2. 第一次过滤（文本关键词）
        filtered_lines = self.filter_lines(normalized_lines, self.EXCLUDE_KEYWORDS_TXT)
        
        # 3. 去重和排序
        filtered_lines = self.custom_tyss_sort(set(filtered_lines))
        
        # 4. 第二次过滤（更严格的过滤）
        g.filtered_tyss_lines = self.filter_lines(filtered_lines, self.EXCLUDE_KEYWORDS)
        
        print(f"✅ 体育赛事处理完成: 原始 {len(g.tyss_lines)} 条, 过滤后 {len(g.filtered_tyss_lines)} 条")
        
        # 5. 生成HTML页面
        self.generate_playlist_html(g.filtered_tyss_lines, Config.OUTPUT_TIYU_HTML)
        
        # 6. 保存TXT文件
        with open(Config.OUTPUT_TIYU_TXT, 'w', encoding='utf-8') as f:
            for line in g.filtered_tyss_lines:
                f.write(line + '\n')
        print(f"✅ 体育赛事文本已保存: {Config.OUTPUT_TIYU_TXT}")

# ========= 主处理类 =========
class LiveSourceProcessor:
    """直播源处理主类"""
    
    def __init__(self):
        self.utils = Utils()
        self.name_processor = NameProcessor()
        self.file_processor = FileProcessor()
        self.http_handler = HttpHandler()
        self.data_processor = DataProcessor()
        self.sports_processor = SportsProcessor()
        
        # 初始化目录
        os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
    
    def run(self):
        """主运行方法"""
        print("=" * 60)
        print("🎬 IPTV直播源聚合处理工具 v0.04.1 重构版")
        print("=" * 60)
        
        g.start_time = self.utils.get_beijing_time()
        print(f"🕒 开始时间: {g.start_time.strftime('%Y%m%d %H:%M:%S')}")
        
        # 加载必要数据
        self._load_blacklist()
        self._load_corrections()
        self._load_logos()
        
        # 处理流程
        self._process_urls()
        self._process_whitelist()
        self._process_aktv()
        self._process_manual()
        
        # 处理体育赛事
        self.sports_processor.process_tyss_data()
        
        # 生成输出
        self._generate_outputs()
        self._generate_stats()
        
        print("=" * 60)
        print("🎉 处理完成！")
        print("=" * 60)
    
    def _load_blacklist(self):
        """加载黑名单"""
        print("🚫 加载黑名单...")
        
        def load_blacklist_file(file_path: str) -> Set[str]:
            urls = set()
            for line in Utils.read_txt_to_array(file_path):
                if ',' in line:
                    url = self.utils.clean_url(line.split(',')[1].strip())
                    urls.add(url)
            return urls
        
        auto = load_blacklist_file(Config.BLACKLIST_AUTO)
        manual = load_blacklist_file(Config.BLACKLIST_MANUAL)
        
        g.combined_blacklist = auto.union(manual)
        print(f"✅ 黑名单加载完成: 自动{len(auto)}条, 手动{len(manual)}条")
    
    def _load_corrections(self):
        """加载纠错字典"""
        print("🔧 加载名称纠错...")
        
        corrections = {}
        for line in Utils.read_txt_to_array(Config.CORRECTIONS_FILE):
            parts = line.strip().split(',')
            if len(parts) >= 2:
                correct_name = parts[0]
                for name in parts[1:]:
                    corrections[name] = correct_name
        
        g.corrections_name = corrections
        print(f"✅ 纠错字典加载完成: {len(corrections)}条")
    
    def _load_logos(self):
        """加载Logo"""
        for line in Utils.read_txt_to_array(Config.LOGO_FILE):
            if ',' in line:
                name, url = line.split(',', 1)
                g.logos[name.strip()] = url.strip()
    
    def _process_urls(self):
        """处理URL列表"""
        print("📡 处理URL源...")
        
        urls = Utils.read_txt_to_array(Config.URLS_FILE)
        print(f"📋 发现 {len(urls)} 个数据源")
        
        for url in urls:
            if url.startswith("http"):
                # 处理日期变量
                beijing_time = self.utils.get_beijing_time()
                
                if "{MMdd}" in url:
                    date_str = beijing_time.strftime("%m%d")
                    url = url.replace("{MMdd}", date_str)
                
                if "{MMdd-1}" in url:
                    date_str = (beijing_time - timedelta(days=1)).strftime("%m%d")
                    url = url.replace("{MMdd-1}", date_str)
                
                self._process_single_url(url)
        
        print(f"✅ URL处理完成: {len(urls)}个数据源")
    
    def _process_single_url(self, url: str):
        """处理单个URL"""
        try:
            print(f"  📡 处理: {url}")
            g.other_lines.append(f"◆◆◆　{url}")
            
            content = self.http_handler.get_http_response(url)
            if not content:
                return
            
            # 检查M3U格式
            is_m3u = content.startswith("#EXTM3U") or content.startswith("#EXTINF")
            if url.endswith((".m3u", ".m3u8")) or is_m3u:
                content = self.file_processor.convert_m3u_to_txt(content)
            
            lines = content.split('\n')
            processed = 0
            
            for line in lines:
                if self._is_valid_channel_line(line):
                    self._process_channel_line(line)
                    processed += 1
            
            print(f"    ✅ 处理: {processed}个频道")
            g.other_lines.append('')
            
        except Exception as e:
            print(f"  ❌ 处理URL错误: {e}")
    
    def _is_valid_channel_line(self, line: str) -> bool:
        """检查是否为有效的频道行"""
        return (
            "#genre#" not in line and 
            "," in line and 
            "://" in line and 
            "tvbus://" not in line and 
            "/udp/" not in line
        )
    
    def _process_channel_line(self, line: str):
        """处理单行频道数据"""
        parts = line.split(',', 1)
        if len(parts) < 2:
            return
        
        raw_name, raw_url = parts[0].strip(), parts[1].strip()
        
        # 处理多源
        if '#' in raw_url:
            urls = raw_url.split('#')
            for url in urls:
                if url.strip():
                    self._process_single_channel(raw_name, url.strip())
        else:
            self._process_single_channel(raw_name, raw_url)
    
    def _process_single_channel(self, raw_name: str, raw_url: str):
        """处理单个频道"""
        # 清理URL
        url = self.utils.clean_url(raw_url)
        
        # 黑名单检查
        if url in g.combined_blacklist:
            print(f"    🚫 黑名单过滤: {raw_name}")
            g.stats['blacklisted'] += 1
            return
        
        # 全局去重
        if url in g.processed_urls:
            print(f"    🔄 URL去重: {raw_name}")
            return
        
        g.processed_urls.add(url)
        g.stats['total_processed'] += 1
        
        # 名称处理
        name = self.name_processor.clean_channel_name(raw_name)
        name = self.utils.traditional_to_simplified(name)
        
        # 名称纠错
        if name in g.corrections_name:
            corrected = g.corrections_name[name]
            if corrected != name:
                print(f"    🔧 名称纠错: {name} -> {corrected}")
                name = corrected
        
        # CCTV和卫视特殊处理
        if "CCTV" in name:
            name = self.name_processor.process_cctv_name(name)
        elif "卫视" in name:
            name = self.name_processor.process_weishi_name(name)
        
        # 重新组合行
        processed_line = f"{name},{url}"
        
        # 分类
        self.data_processor.classify_channel(name, processed_line, url)
    
    def _process_whitelist(self):
        """处理白名单"""
        print("📋 处理白名单...")
        
        count = 0
        for line in Utils.read_txt_to_array(Config.WHITELIST_AUTO):
            if "#genre#" not in line and "," in line and "://" in line:
                parts = line.split(",")
                if len(parts) >= 3:
                    try:
                        response_time = float(parts[0].replace("ms", ""))
                        if response_time < 2000:  # 2秒内的高质量源
                            channel_line = ",".join(parts[1:])
                            self._process_channel_line(channel_line)
                            count += 1
                    except ValueError:
                        continue
        
        print(f"✅ 白名单处理完成: {count}个高质量源")
    
    def _process_aktv(self):
        """处理AKTV源"""
        print("📡 获取AKTV源...")
        
        content = self.http_handler.get_http_response(Config.AKTV_URL)
        if content:
            print("✅ AKTV网络获取成功")
            content = self.file_processor.convert_m3u_to_txt(content)
            aktv_lines = content.strip().split('\n')
        else:
            print("⚠️ AKTV网络获取失败，使用本地")
            aktv_lines = Utils.read_txt_to_array(Config.AKTV_LOCAL)
        
        print(f"  处理 {len(aktv_lines)} 行")
        for line in aktv_lines:
            self._process_channel_line(line)
    
    def _process_manual(self):
        """处理手工区"""
        print("🔧 处理手工区...")
        
        manual_files = {
            '浙江': f'{Config.MANUAL_DIR}/浙江频道.txt',
            '广东': f'{Config.MANUAL_DIR}/广东频道.txt',
            '湖北': f'{Config.MANUAL_DIR}/湖北频道.txt',
            '上海': f'{Config.MANUAL_DIR}/上海频道.txt',
            '江苏': f'{Config.MANUAL_DIR}/江苏频道.txt',
        }
        
        for region, file_path in manual_files.items():
            lines = Utils.read_txt_to_array(file_path)
            
            # 手动去重
            seen_urls = set()
            unique_lines = []
            
            for line in lines:
                if "#genre#" not in line and "," in line and "://" in line:
                    parts = line.split(',', 1)
                    if len(parts) >= 2:
                        url = self.utils.clean_url(parts[1].strip())
                        if url not in seen_urls:
                            seen_urls.add(url)
                            unique_lines.append(line)
            
            # 添加到对应分类
            if region in CHANNEL_CATEGORIES['regions']:
                CHANNEL_CATEGORIES['regions'][region]['lines'].extend(unique_lines)
            
            print(f"  ✅ {region}: {len(unique_lines)}个手工源")
    
    def _generate_outputs(self):
        """生成输出文件"""
        print("📄 生成输出文件...")
        
        # 生成今日推荐
        beijing_time = self.utils.get_beijing_time()
        formatted_time = beijing_time.strftime("%Y%m%d %H:%M:%S")
        
        def get_random_line(file_path: str) -> str:
            lines = Utils.read_txt_to_array(file_path)
            return random.choice(lines).split(',')[-1] if lines else ""
        
        # 版本信息
        version = f"{formatted_time},{get_random_line(f'{Config.MANUAL_DIR}/今日推台.txt')}"
        about = f"👨潇然,{get_random_line(f'{Config.MANUAL_DIR}/今日推台.txt')}"
        
        # 今日推荐
        mtv_templates = ["💯推荐", "🤫低调", "🟢使用", "⚠️禁止", "🚫贩卖"]
        mtv_lines = [
            f"{mtv},{get_random_line(f'{Config.MANUAL_DIR}/今日推荐.txt')}" 
            for mtv in mtv_templates
        ]
        
        # 读取sports.txt手工源
        sports_manual = Utils.read_txt_to_array(f'{Config.MANUAL_DIR}/sports.txt')
        
        # 生成完整版
        full_content = self._build_playlist_content('full', version, about, mtv_lines, sports_manual)
        self._save_file(Config.OUTPUT_FULL, full_content)
        
        # 生成精简版
        lite_content = self._build_playlist_content('lite', version, about, mtv_lines, sports_manual)
        self._save_file(Config.OUTPUT_LITE, lite_content)
        
        # 生成定制版
        custom_content = self._build_playlist_content('custom', version, about, mtv_lines, sports_manual)
        self._save_file(Config.OUTPUT_CUSTOM, custom_content)
        
        # 保存未分类源
        self._save_file(Config.OUTPUT_OTHERS, '\n'.join(g.other_lines))
        
        # 生成M3U文件
        self._generate_m3u_files()
    
    def _build_playlist_content(self, playlist_type: str, version: str, 
                               about: str, mtv_lines: list, sports_manual: list) -> str:
        """构建播放列表内容"""
        content = []
        
        # 核心频道
        if playlist_type in ['full', 'lite', 'custom']:
            content.extend(self._build_category_section('央视', '🌐央视频道,#genre#'))
            content.extend(self._build_category_section('卫视', '📡卫视频道,#genre#'))
        
        # 完整版和定制版添加其他分类
        if playlist_type in ['full', 'custom']:
            # 省级频道
            for region in CHANNEL_CATEGORIES['regions']:
                content.extend(self._build_category_section(region, f'🏛️{region}频道,#genre#'))
            
            # 体育赛事（完整版和定制版都有）
            if g.filtered_tyss_lines:
                content.append("🏆️体育赛事,#genre#")
                content.extend(g.filtered_tyss_lines)
                content.append('')
            
            # 咪咕赛事
            if g.mgss_lines:
                content.append("🏈咪咕赛事,#genre#")
                content.extend(sorted(set(g.mgss_lines)))
                content.append('')
            
            # SPORTS手工源
            if sports_manual:
                content.append("⚽️SPORTS,#genre#")
                content.extend(sports_manual)
                content.append('')
        
        # 完整版添加所有分类
        if playlist_type == 'full':
            # AKTV源
            aktv_lines = Utils.read_txt_to_array(Config.AKTV_LOCAL)
            if aktv_lines:
                content.append("🚀 FreeTV,#genre#")
                content.extend(aktv_lines)
                content.append('')
            
            # 特殊地区
            for region in CHANNEL_CATEGORIES['special_regions']:
                content.extend(self._build_category_section(region, f'🇭🇰{region}频道,#genre#'))
            
            # 内容分类
            content_categories = {
                '数字': '🔢数字频道,#genre#',
                '电影': '🎬电影频道,#genre#',
                '电视剧': '📺电·视·剧,#genre#',
                '纪录片': '🎥纪·录·片,#genre#',
                '动画片': '🐱动·画·片,#genre#',
                '收音机': '📻收·音·机,#genre#',
                '综艺': '🎭综艺频道,#genre#',
                '虎牙': '🐯虎牙直播,#genre#',
                '斗鱼': '🐠斗鱼直播,#genre#',
                '解说': '🎤解说频道,#genre#',
                '音乐': '🎵音乐频道,#genre#',
                '美食': '🍜美食频道,#genre#',
                '旅游': '✈️旅游频道,#genre#',
                '健康': '🏥健康频道,#genre#',
                '财经': '💰财经频道,#genre#',
                '购物': '🛍️购物频道,#genre#',
                '游戏': '🎮游戏频道,#genre#',
                '新闻': '📰新闻频道,#genre#',
                '中国': '🇨🇳中国综合,#genre#',
                '国际': '🌐国际频道,#genre#',
                '体育': '⚽体育频道,#genre#',
                '戏曲': '🎭戏曲频道,#genre#',
                '春晚': '🧨春晚频道,#genre#',
                '直播中国': '🏞️景区直播,#genre#',
                '收藏频道': '⭐收藏频道,#genre#',
            }
            
            for cat_name, header in content_categories.items():
                if cat_name in CHANNEL_CATEGORIES['content']:
                    content.extend(self._build_category_section(cat_name, header))
        
        # 其他频道
        if playlist_type in ['full', 'custom']:
            content.append("📦其他频道,#genre#")
            content.extend(sorted(set(g.other_lines)))
            content.append('')
        
        # 更新时间
        content.append("🕒更新时间,#genre#")
        content.append(version)
        content.append(about)
        content.extend(mtv_lines)
        content.append('')
        
        return '\n'.join(content)
    
    def _build_category_section(self, category_name: str, header: str) -> list:
        """构建分类部分"""
        section = [header]
        sorted_lines = self.data_processor.sort_category_lines(category_name)
        section.extend(sorted_lines)
        section.append('')
        return section
    
    def _save_file(self, file_path: str, content: str):
        """保存文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 文件已保存: {file_path}")
        except Exception as e:
            print(f"❌ 保存文件错误 {file_path}: {e}")
    
    def _generate_m3u_files(self):
        """生成M3U文件"""
        print("🔄 生成M3U格式...")
        
        self.file_processor.make_m3u(Config.OUTPUT_FULL, 
                                    Config.OUTPUT_FULL.replace('.txt', '.m3u'))
        self.file_processor.make_m3u(Config.OUTPUT_LITE,
                                    Config.OUTPUT_LITE.replace('.txt', '.m3u'))
        self.file_processor.make_m3u(Config.OUTPUT_CUSTOM,
                                    Config.OUTPUT_CUSTOM.replace('.txt', '.m3u'))
    
    def _generate_stats(self):
        """生成统计信息"""
        print("📊 生成统计信息...")
        
        end_time = self.utils.get_beijing_time()
        elapsed = end_time - g.start_time
        minutes = int(elapsed.total_seconds() // 60)
        seconds = int(elapsed.total_seconds() % 60)
        
        # 计算去重率
        total_unique = len(g.processed_urls)
        total_with_blacklist = total_unique + g.stats['blacklisted']
        dup_rate = 0
        if total_with_blacklist > 0:
            dup_rate = (1 - total_unique / total_with_blacklist) * 100
        
        print(f"开始时间: {g.start_time.strftime('%Y%m%d %H:%M:%S')}")
        print(f"结束时间: {end_time.strftime('%Y%m%d %H:%M:%S')}")
        print(f"执行时间: {minutes}分{seconds}秒")
        print(f"处理URL数: {g.stats['total_processed']}")
        print(f"唯一URL数: {total_unique}")
        print(f"黑名单过滤: {g.stats['blacklisted']}")
        print(f"去重率: {dup_rate:.1f}%")
        print(f"体育赛事: {len(g.filtered_tyss_lines)}条")
        print(f"咪咕赛事: {len(g.mgss_lines)}条")
        print(f"未分类源: {len(g.other_lines)}")

# ========= 主函数 =========
def main():
    """主函数"""
    processor = LiveSourceProcessor()
    processor.run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断程序")
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")

"""
IPTV直播源聚合处理工具 v3.01 重构版
基于v1.00版本的完全重构，保持完全兼容性

主要修复：
1. ✅ 修复体育赛事缺失问题
2. ✅ 添加体育赛事专用处理器
3. ✅ 恢复体育赛事日期格式化功能
4. ✅ 恢复体育赛事HTML页面生成
5. ✅ 添加咪咕赛事分类
6. ✅ 保持与v0.01 v1.00 v2.00完全相同的输出

新增功能：
1. 🏆 完整的体育赛事处理流程
2. 📅 日期格式化（MM-DD格式）
3. 🎯 关键词过滤（玉玉软件、榴芒电视等）
4. 📊 体育赛事专用排序
5. 🌐 体育赛事HTML网页生成
6. 📝 独立的体育赛事文本输出

输出文件：
output/
  ├── full.txt         完整播放列表
  ├── full.m3u        M3U格式完整版
  ├── lite.txt        精简版（央视+卫视）
  ├── lite.m3u       M3U格式精简版
  ├── custom.txt      定制版（不含地方台）
  ├── custom.m3u     M3U格式定制版
  ├── others.txt      未分类频道
  ├── tiyu.html       体育赛事网页（新增）
  └── tiyu.txt        体育赛事文本（新增）

版本历史：
v0.01 (2025-01-01): 基础版本
v1.00 (2025-02-02): 性能优化版，去重效率提升10倍
v3.00 (2025-03-03): 重构优化版（缺少体育赛事）
v3.01 (2025-03-07): 修复体育赛事版（当前版本）

作者：潇然
版本：v3.01
日期：2025年03月
"""
# === LiveSource-Collector ====
# ====== 版本v3.01 =========
# ==== 修复体育赛事版 =======