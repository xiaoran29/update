#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ===== 直播源聚合处理工具 ======
# ======== 版本v3.00 =========
# ========= 重构版 ===========

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

# ========= 主处理类 =========
class LiveSourceProcessor:
    """直播源处理主类"""
    
    def __init__(self):
        self.utils = Utils()
        self.name_processor = NameProcessor()
        self.file_processor = FileProcessor()
        self.http_handler = HttpHandler()
        self.data_processor = DataProcessor()
        
        # 初始化目录
        os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
    
    def run(self):
        """主运行方法"""
        print("=" * 60)
        print("🎬 IPTV直播源聚合处理工具 v0.04 重构版")
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
        
        # 生成完整版
        full_content = self._build_playlist_content('full', version, about, mtv_lines)
        self._save_file(Config.OUTPUT_FULL, full_content)
        
        # 生成精简版
        lite_content = self._build_playlist_content('lite', version, about, mtv_lines)
        self._save_file(Config.OUTPUT_LITE, lite_content)
        
        # 生成定制版
        custom_content = self._build_playlist_content('custom', version, about, mtv_lines)
        self._save_file(Config.OUTPUT_CUSTOM, custom_content)
        
        # 保存未分类源
        self._save_file(Config.OUTPUT_OTHERS, '\n'.join(g.other_lines))
        
        # 生成M3U文件
        self._generate_m3u_files()
    
    def _build_playlist_content(self, playlist_type: str, version: str, 
                               about: str, mtv_lines: list) -> str:
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
        
        # 完整版添加所有分类
        if playlist_type == 'full':
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
IPTV直播源聚合处理工具 v3.00 重构版
基于v1.00版本的完全重构，保持完全兼容性

重构特点：
1. ✅ 面向对象设计：模块化、可维护性高
2. ✅ 配置集中管理：所有路径和常量统一管理
3. ✅ 数据驱动：频道分类配置化，易于扩展
4. ✅ 代码精简：去除重复代码，逻辑清晰
5. ✅ 性能优化：全局去重机制保持高效
6. ✅ 完全兼容：输入输出、字典文件完全兼容v0.01 v1.00 v2.00

主要改进：
1. 🏗️ 架构优化：从过程式重构为面向对象
2. 📁 配置管理：使用Config类统一管理路径
3. 🗂️ 数据驱动：频道分类通过CHANNEL_CATEGORIES配置
4. 🛠️ 工具类：提取通用功能到工具类
5. 📊 状态管理：使用GlobalState统一管理全局状态
6. 🔄 处理流程：重构为清晰的处理管道

文件结构：
项目目录/
├── assets/livesource/       # 完全兼容原有目录结构
│   ├── 主频道/
│   ├── 地方台/
│   ├── 手工区/
│   ├── blacklist/
│   ├── livesource3.py     # 主程序（v3.00）
│   └── corrections_name.txt
├── output/                  # 输出目录
└── requirements.txt         # 依赖包

输出文件（完全兼容v1.00）：
output/
  ├── full.txt              # 完整版
  ├── full.m3u             # M3U格式
  ├── lite.txt             # 精简版
  ├── lite.m3u            # M3U格式
  ├── custom.txt           # 定制版
  ├── custom.m3u          # M3U格式
  └── others.txt           # 未分类源

使用说明：
1. 确保目录结构与v1.00完全一致
2. 运行：python main.py
3. 结果在output目录查看

版本历史：
v0.00 (2025-01-01): 基础版本
v1.00 (2025-01-01): 性能优化版，去重效率提升10倍
v2.00 (2025-02-02): 架构优化版，代码更健壮，功能更完善
v3.00 (2025-03-03): 重构优化版（当前版本）

作者：潇然
版本：v3.00
日期：2025年3月3日
"""
# === LiveSource-Collector ====
# ====== 版本v3.00 =========
# ====== 重构优化版 ========