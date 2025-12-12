# ===== 直播源聚合处理工具 ======
# ========= 版本v0.03 =========
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ========= 模块导入区 =========
import os
import re
import time
import json
import logging
import random
import socket
from typing import Dict, List, Set, Tuple, Optional
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse
import urllib.request
from urllib.error import HTTPError, URLError
import opencc

# ========= 日志配置 =========
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('iptv_processor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ========= 配置类 =========
class Config:
    """配置参数类"""
    # 输入输出配置
    INPUT_FILES = [
        "IPTV直播源.txt",
        "备用直播源.txt"
    ]
    OUTPUT_DIR = "直播源分类输出"
    MERGED_FILE = "直播源.m3u"
    STATS_FILE = "处理统计.json"
    
    # 处理设置
    MAX_WORKERS = 20
    REQUEST_TIMEOUT = 5
    CACHE_DURATION = 3600
    
    # 黑名单域名和IP
    URL_BLACKLIST = [
        "example.com", "test.com", "localhost",
        "127.0.0.1", "0.0.0.0",
        "192.168.", "10.", "172.16.", "172.17.", "172.18.", "172.19.",
        "172.20.", "172.21.", "172.22.", "172.23.", "172.24.", "172.25.",
        "172.26.", "172.27.", "172.28.", "172.29.", "172.30.", "172.31."
    ]
    
    # 频道名称清理关键字
    REMOVAL_LIST = [
        "_电信", "电信", "「LiTV」", "频道", "频陆", "备陆", "壹陆", "贰陆", "叁陆", "肆陆",
        "伍陆", "陆陆", "柒陆", "频晴", "频粤", "高清", "超清", "标清", "斯特", "粤陆",
        "国陆", "肆柒", "频英", "频特", "频国", "频壹", "频贰", "肆贰", "频测", "咪咕",
        "闽特", "高特", "频高", "频标", "汝阳", "频效", "国标", "粤标", "频推", "频流",
        "粤高", "频限", "实时", "美推", "频美", "（HD）", "-HD", "英陆", "_ITV", "(北美)",
        "(HK)", "AKtv", "「IPV4」", "「IPV6」", "[HD]", "[BD]", "[SD]", "[VGA]",
        "[超清]", "4Gtv", "1080", "720", "480", "HD", "SD", "4K", "VGA", "(HD)",
        "(SD)", "(4K)", "(VGA)", "{HD}", "{SD}", "{4K}", "{VGA}", "「4gTV」",
        "「回看」", "<HD>", "<SD>", "<4K>", "<VGA>"
    ]

# ========= 初始化 =========
class IPTVProcessor:
    """IPTV直播源处理器"""
    
    def __init__(self):
        self.config = Config()
        self.stats = {
            "total_channels": 0,
            "valid_channels": 0,
            "blacklisted": 0,
            "duplicates": 0,
            "category_counts": {},
            "start_time": None,
            "end_time": None,
            "duration": None
        }
        
        # 初始化输出目录
        os.makedirs(self.config.OUTPUT_DIR, exist_ok=True)
        logger.info(f"创建输出目录: {self.config.OUTPUT_DIR}")
        
        # 全局URL去重集合
        self.processed_urls = set()
        
        # 简繁转换器
        self.converter = opencc.OpenCC('t2s')
        
        # 初始化所有频道分类列表
        self._init_channel_categories()
        
        # 加载字典和黑名单
        self._load_dictionaries()
        self._load_blacklists()
        
    def _init_channel_categories(self):
        """初始化所有频道分类列表"""
        # 核心频道
        self.yangshi_lines = []      # 央视
        self.weishi_lines = []       # 卫视
        
        # 省级地方台
        self.beijing_lines = []      # 北京
        self.shanghai_lines = []     # 上海
        self.guangdong_lines = []    # 广东
        self.jiangsu_lines = []      # 江苏
        self.zhejiang_lines = []     # 浙江
        self.shandong_lines = []     # 山东
        self.sichuan_lines = []      # 四川
        self.henan_lines = []        # 河南
        self.hunan_lines = []        # 湖南
        self.chongqing_lines = []    # 重庆
        self.tianjin_lines = []      # 天津
        self.hubei_lines = []        # 湖北
        self.anhui_lines = []        # 安徽
        self.fujian_lines = []       # 福建
        self.liaoning_lines = []     # 辽宁
        self.shaanxi_lines = []      # 陕西
        self.hebei_lines = []        # 河北
        self.jiangxi_lines = []      # 江西
        self.guangxi_lines = []      # 广西
        self.yunnan_lines = []       # 云南
        self.shanxi_lines = []       # 山西
        self.heilongjiang_lines = [] # 黑龙江
        self.jilin_lines = []        # 吉林
        self.guizhou_lines = []      # 贵州
        self.gansu_lines = []        # 甘肃
        self.neimenggu_lines = []    # 内蒙古
        self.xinjiang_lines = []     # 新疆
        self.hainan_lines = []       # 海南
        self.ningxia_lines = []      # 宁夏
        self.qinghai_lines = []      # 青海
        self.xizang_lines = []       # 西藏
        
        # 港澳台频道
        self.hongkong_lines = []     # 香港
        self.macau_lines = []        # 澳门
        self.minnan_lines = []       # 闽南
        
        # 其他分类频道
        self.digital_lines = []      # 数字付费
        self.movie_lines = []        # 电影
        self.tv_drama_lines = []     # 电视剧
        self.documentary_lines = []  # 纪录片
        self.cartoon_lines = []      # 动画片
        self.radio_lines = []        # 收音机
        self.variety_lines = []      # 综艺
        self.huya_lines = []         # 虎牙
        self.douyu_lines = []        # 斗鱼
        self.commentary_lines = []   # 解说
        self.music_lines = []        # 音乐
        self.food_lines = []         # 美食
        self.travel_lines = []       # 旅游
        self.health_lines = []       # 健康
        self.finance_lines = []      # 财经
        self.shopping_lines = []     # 购物
        self.game_lines = []         # 游戏
        self.news_lines = []         # 新闻
        self.china_lines = []        # 中国
        self.international_lines = [] # 国际
        self.sports_lines = []       # 体育
        self.tyss_lines = []         # 体育赛事
        self.mgss_lines = []         # 咪咕赛事
        self.traditional_opera_lines = [] # 戏曲
        self.spring_festival_gala_lines = [] # 春晚
        self.camera_lines = []       # 景区直播
        self.favorite_lines = []     # 收藏
        
        # 未分类
        self.other_lines = []
        
        # 体育赛事专用
        self.filtered_tyss_lines = []
        
    def _load_dictionaries(self):
        """加载所有频道分类字典"""
        logger.info("加载频道字典...")
        
        # 核心频道
        self.yangshi_dictionary = self.read_txt_to_array('assets/livesource/主频道/CCTV.txt')
        self.weishi_dictionary = self.read_txt_to_array('assets/livesource/主频道/卫视.txt')
        
        # 省级地方台
        self.beijing_dictionary = self.read_txt_to_array('assets/livesource/地方台/北京.txt')
        self.shanghai_dictionary = self.read_txt_to_array('assets/livesource/地方台/上海.txt')
        self.guangdong_dictionary = self.read_txt_to_array('assets/livesource/地方台/广东.txt')
        self.jiangsu_dictionary = self.read_txt_to_array('assets/livesource/地方台/江苏.txt')
        self.zhejiang_dictionary = self.read_txt_to_array('assets/livesource/地方台/浙江.txt')
        self.shandong_dictionary = self.read_txt_to_array('assets/livesource/地方台/山东.txt')
        self.sichuan_dictionary = self.read_txt_to_array('assets/livesource/地方台/四川.txt')
        self.henan_dictionary = self.read_txt_to_array('assets/livesource/地方台/河南.txt')
        self.hunan_dictionary = self.read_txt_to_array('assets/livesource/地方台/湖南.txt')
        self.chongqing_dictionary = self.read_txt_to_array('assets/livesource/地方台/重庆.txt')
        self.tianjin_dictionary = self.read_txt_to_array('assets/livesource/地方台/天津.txt')
        self.hubei_dictionary = self.read_txt_to_array('assets/livesource/地方台/湖北.txt')
        self.anhui_dictionary = self.read_txt_to_array('assets/livesource/地方台/安徽.txt')
        self.fujian_dictionary = self.read_txt_to_array('assets/livesource/地方台/福建.txt')
        self.liaoning_dictionary = self.read_txt_to_array('assets/livesource/地方台/辽宁.txt')
        self.shaanxi_dictionary = self.read_txt_to_array('assets/livesource/地方台/陕西.txt')
        self.hebei_dictionary = self.read_txt_to_array('assets/livesource/地方台/河北.txt')
        self.jiangxi_dictionary = self.read_txt_to_array('assets/livesource/地方台/江西.txt')
        self.guangxi_dictionary = self.read_txt_to_array('assets/livesource/地方台/广西.txt')
        self.yunnan_dictionary = self.read_txt_to_array('assets/livesource/地方台/云南.txt')
        self.shanxi_dictionary = self.read_txt_to_array('assets/livesource/地方台/山西.txt')
        self.heilongjiang_dictionary = self.read_txt_to_array('assets/livesource/地方台/黑龙江.txt')
        self.jilin_dictionary = self.read_txt_to_array('assets/livesource/地方台/吉林.txt')
        self.guizhou_dictionary = self.read_txt_to_array('assets/livesource/地方台/贵州.txt')
        self.gansu_dictionary = self.read_txt_to_array('assets/livesource/地方台/甘肃.txt')
        self.neimenggu_dictionary = self.read_txt_to_array('assets/livesource/地方台/内蒙.txt')
        self.xinjiang_dictionary = self.read_txt_to_array('assets/livesource/地方台/新疆.txt')
        self.hainan_dictionary = self.read_txt_to_array('assets/livesource/地方台/海南.txt')
        self.ningxia_dictionary = self.read_txt_to_array('assets/livesource/地方台/宁夏.txt')
        self.qinghai_dictionary = self.read_txt_to_array('assets/livesource/地方台/青海.txt')
        self.xizang_dictionary = self.read_txt_to_array('assets/livesource/地方台/西藏.txt')
        
        # 港澳台地区
        self.hongkong_dictionary = self.read_txt_to_array('assets/livesource/地方台/香港.txt')
        self.macau_dictionary = self.read_txt_to_array('assets/livesource/地方台/澳门.txt')
        self.minnan_dictionary = self.read_txt_to_array('assets/livesource/地方台/闽南.txt')
        
        # 其他分类
        self.digital_dictionary = self.read_txt_to_array('assets/livesource/主频道/数字.txt')
        self.movie_dictionary = self.read_txt_to_array('assets/livesource/主频道/电影.txt')
        self.tv_drama_dictionary = self.read_txt_to_array('assets/livesource/主频道/电视剧.txt')
        self.documentary_dictionary = self.read_txt_to_array('assets/livesource/主频道/纪录片.txt')
        self.cartoon_dictionary = self.read_txt_to_array('assets/livesource/主频道/动画片.txt')
        self.radio_dictionary = self.read_txt_to_array('assets/livesource/主频道/收音机.txt')
        self.variety_dictionary = self.read_txt_to_array('assets/livesource/主频道/综艺.txt')
        self.huya_dictionary = self.read_txt_to_array('assets/livesource/主频道/虎牙.txt')
        self.douyu_dictionary = self.read_txt_to_array('assets/livesource/主频道/斗鱼.txt')
        self.commentary_dictionary = self.read_txt_to_array('assets/livesource/主频道/解说.txt')
        self.music_dictionary = self.read_txt_to_array('assets/livesource/主频道/音乐.txt')
        self.food_dictionary = self.read_txt_to_array('assets/livesource/主频道/美食.txt')
        self.travel_dictionary = self.read_txt_to_array('assets/livesource/主频道/旅游.txt')
        self.health_dictionary = self.read_txt_to_array('assets/livesource/主频道/健康.txt')
        self.finance_dictionary = self.read_txt_to_array('assets/livesource/主频道/财经.txt')
        self.shopping_dictionary = self.read_txt_to_array('assets/livesource/主频道/购物.txt')
        self.game_dictionary = self.read_txt_to_array('assets/livesource/主频道/游戏.txt')
        self.news_dictionary = self.read_txt_to_array('assets/livesource/主频道/新闻.txt')
        self.china_dictionary = self.read_txt_to_array('assets/livesource/主频道/中国.txt')
        self.international_dictionary = self.read_txt_to_array('assets/livesource/主频道/国际.txt')
        self.sports_dictionary = self.read_txt_to_array('assets/livesource/主频道/体育.txt')
        self.tyss_dictionary = self.read_txt_to_array('assets/livesource/主频道/体育赛事.txt')
        self.mgss_dictionary = self.read_txt_to_array('assets/livesource/主频道/咪咕赛事.txt')
        self.traditional_opera_dictionary = self.read_txt_to_array('assets/livesource/主频道/戏曲.txt')
        self.spring_festival_gala_dictionary = self.read_txt_to_array('assets/livesource/主频道/春晚.txt')
        self.camera_dictionary = self.read_txt_to_array('assets/livesource/主频道/直播中国.txt')
        self.favorite_dictionary = self.read_txt_to_array('assets/livesource/主频道/收藏频道.txt')
        
        # 加载纠错字典
        self.corrections_name = self.load_corrections_name('assets/livesource/corrections_name.txt')
        
        logger.info(f"加载完成: 央视字典 {len(self.yangshi_dictionary)} 条, 卫视字典 {len(self.weishi_dictionary)} 条")
    
    def _load_blacklists(self):
        """加载黑名单"""
        logger.info("加载黑名单...")
        
        def read_blacklist(file_path):
            """读取黑名单文件"""
            blacklist = set()
            if not os.path.exists(file_path):
                logger.warning(f"黑名单文件不存在: {file_path}")
                return blacklist
                
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if ',' in line:
                        url = line.split(',')[1].strip()
                        cleaned_url = self.clean_url(url)
                        blacklist.add(cleaned_url)
            return blacklist
        
        # 加载自动和手动黑名单
        self.blacklist_auto = read_blacklist('assets/livesource/blacklist/blacklist_auto.txt')
        self.blacklist_manual = read_blacklist('assets/livesource/blacklist/blacklist_manual.txt')
        self.combined_blacklist = self.blacklist_auto.union(self.blacklist_manual)
        
        logger.info(f"黑名单加载完成: 自动 {len(self.blacklist_auto)} 条, 手动 {len(self.blacklist_manual)} 条, 总计 {len(self.combined_blacklist)} 条")
    
    def read_txt_to_array(self, file_name: str) -> List[str]:
        """读取文本文件到数组"""
        try:
            if not os.path.exists(file_name):
                logger.warning(f"文件不存在: {file_name}")
                return []
                
            with open(file_name, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
            return lines
        except Exception as e:
            logger.error(f"读取文件失败 {file_name}: {e}")
            return []
    
    def load_corrections_name(self, filename: str) -> Dict[str, str]:
        """加载频道名称纠错字典"""
        corrections = {}
        if not os.path.exists(filename):
            logger.warning(f"纠错文件不存在: {filename}")
            return corrections
            
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                parts = line.strip().split(',')
                if len(parts) >= 2:
                    correct_name = parts[0]
                    for name in parts[1:]:
                        corrections[name] = correct_name
        return corrections
    
    # ========= 核心处理函数 =========
    
    def clean_url(self, url: str) -> str:
        """清理URL，移除$符号及其后面的内容"""
        last_dollar_index = url.rfind('$')
        if last_dollar_index != -1:
            return url[:last_dollar_index]
        return url
    
    def traditional_to_simplified(self, text: str) -> str:
        """繁体中文转简体中文"""
        return self.converter.convert(text)
    
    def clean_channel_name(self, channel_name: str) -> str:
        """清理频道名称"""
        for item in self.config.REMOVAL_LIST:
            channel_name = channel_name.replace(item, "")
        
        # 移除末尾的'HD'
        if channel_name.endswith("HD"):
            channel_name = channel_name[:-2]
        
        # 移除末尾的'台'（如果频道名称长度大于3）
        if channel_name.endswith("台") and len(channel_name) > 3:
            channel_name = channel_name[:-1]
        
        return channel_name
    
    def process_name_string(self, input_str: str) -> str:
        """处理频道名称字符串，统一命名格式"""
        parts = input_str.split(',')
        processed_parts = []
        
        for part in parts:
            processed_part = self._process_part(part)
            processed_parts.append(processed_part)
        
        return ','.join(processed_parts)
    
    def _process_part(self, part_str: str) -> str:
        """处理单个频道名称部分"""
        # 处理CCTV频道名称
        if "CCTV" in part_str and "://" not in part_str:
            # 先剔除特定关键字
            part_str = part_str.replace("IPV6", "")
            part_str = part_str.replace("PLUS", "+")
            part_str = part_str.replace("1080", "")
            
            # 只保留数字、K和+号
            filtered_str = ''.join(char for char in part_str if char.isdigit() or char == 'K' or char == '+')
            
            # 处理特殊情况：如果没有找到频道数字，返回原名称（去掉CCTV）
            if not filtered_str.strip():
                filtered_str = part_str.replace("CCTV", "")
            
            # 特殊处理CCTV中的4K和8K名称
            if len(filtered_str) > 2 and re.search(r'4K|8K', filtered_str):
                # 删除4K或8K后面的字符，保留4K或8K
                filtered_str = re.sub(r'(4K|8K).*', r'\1', filtered_str)
                if len(filtered_str) > 2:
                    # 给4K或8K添加括号
                    filtered_str = re.sub(r'(4K|8K)', r'(\1)', filtered_str)
            
            return "CCTV" + filtered_str
            
        # 处理卫视频道名称
        elif "卫视" in part_str:
            # 匹配"卫视「.*」"模式，替换为"卫视"
            pattern = r'卫视「.*」'
            result_str = re.sub(pattern, '卫视', part_str)
            return result_str
        
        return part_str
    
    def get_url_file_extension(self, url: str) -> str:
        """获取URL的文件扩展名"""
        parsed_url = urlparse(url)
        path = parsed_url.path
        extension = os.path.splitext(path)[1]
        return extension
    
    def convert_m3u_to_txt(self, m3u_content: str) -> str:
        """将M3U格式转换为TXT格式"""
        lines = m3u_content.split('\n')
        txt_lines = []
        channel_name = ""
        
        for line in lines:
            # 跳过M3U头信息
            if line.startswith("#EXTM3U"):
                continue
                
            # 处理频道信息行
            if line.startswith("#EXTINF"):
                # 提取频道名称（通常在最后一个逗号后面）
                channel_name = line.split(',')[-1].strip()
                
            # 处理URL行
            elif line.startswith("http") or line.startswith("rtmp") or line.startswith("p3p"):
                txt_lines.append(f"{channel_name},{line.strip()}")
            
            # 处理格式为TXT但后缀为M3U的文件
            if "#genre#" not in line and "," in line and "://" in line:
                pattern = r'^[^,]+,[^\s]+://[^\s]+$'
                if bool(re.match(pattern, line)):
                    txt_lines.append(line)
        
        return '\n'.join(txt_lines)
    
    def check_blacklisted_url(self, url: str) -> bool:
        """检查URL是否在黑名单中"""
        # 检查完整URL
        if url in self.combined_blacklist:
            return True
        
        # 检查域名是否在黑名单中
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            
            for blacklisted_domain in self.config.URL_BLACKLIST:
                if blacklisted_domain in domain:
                    return True
        except:
            pass
        
        return False
    
    def process_channel_line(self, line: str) -> bool:
        """处理单行频道数据，返回是否成功处理"""
        # 检查是否为有效的频道行
        if "#genre#" not in line and "#EXTINF:" not in line and "," in line and "://" in line:
            # 分割频道名称和URL
            parts = line.split(',', 1)
            if len(parts) < 2:
                return False
            
            channel_name = parts[0].strip()
            channel_address = parts[1].strip()
            
            # ========== 优化1：提前清理URL ==========
            channel_address = self.clean_url(channel_address)
            
            # ========== 优化2：提前黑名单检查 ==========
            if self.check_blacklisted_url(channel_address):
                logger.debug(f"黑名单过滤: {channel_name}")
                self.stats["blacklisted"] += 1
                return False
            
            # ========== 优化3：全局URL去重 ==========
            if channel_address in self.processed_urls:
                logger.debug(f"URL去重: {channel_name}")
                self.stats["duplicates"] += 1
                return False
            
            self.processed_urls.add(channel_address)
            
            # 清理频道名称
            channel_name = self.clean_channel_name(channel_name)
            
            # 繁体转简体
            channel_name = self.traditional_to_simplified(channel_name)
            
            # 应用名称纠错
            if channel_name in self.corrections_name:
                channel_name = self.corrections_name[channel_name]
            
            # 重新组合行
            processed_line = self.process_name_string(f"{channel_name},{channel_address}")
            
            # 根据频道名称分类
            if self._classify_channel(channel_name, processed_line):
                self.stats["valid_channels"] += 1
                return True
            
            # 未分类
            self.other_lines.append(processed_line)
            return True
        
        return False
    
    def _classify_channel(self, channel_name: str, processed_line: str) -> bool:
        """分类频道，返回是否成功分类"""
        # 1. 央视（增强识别逻辑）
        if (channel_name in self.yangshi_dictionary or 
            "CCTV" in channel_name or
            channel_name.startswith("CGTN") or
            channel_name.startswith("CETV") or
            channel_name.startswith("CEC") or
            "中央" in channel_name):
            self.yangshi_lines.append(processed_line)
            return True
            
        # 2. 卫视
        elif channel_name in self.weishi_dictionary:
            self.weishi_lines.append(processed_line)
            return True
            
        # 3. 省级地方台（按优先级顺序）
        elif channel_name in self.beijing_dictionary:
            self.beijing_lines.append(processed_line)
            return True
        elif channel_name in self.shanghai_dictionary:
            self.shanghai_lines.append(processed_line)
            return True
        elif channel_name in self.guangdong_dictionary:
            self.guangdong_lines.append(processed_line)
            return True
        elif channel_name in self.jiangsu_dictionary:
            self.jiangsu_lines.append(processed_line)
            return True
        elif channel_name in self.zhejiang_dictionary:
            self.zhejiang_lines.append(processed_line)
            return True
        elif channel_name in self.shandong_dictionary:
            self.shandong_lines.append(processed_line)
            return True
        elif channel_name in self.sichuan_dictionary:
            self.sichuan_lines.append(processed_line)
            return True
        elif channel_name in self.henan_dictionary:
            self.henan_lines.append(processed_line)
            return True
        elif channel_name in self.hunan_dictionary:
            self.hunan_lines.append(processed_line)
            return True
        elif channel_name in self.chongqing_dictionary:
            self.chongqing_lines.append(processed_line)
            return True
        elif channel_name in self.tianjin_dictionary:
            self.tianjin_lines.append(processed_line)
            return True
        elif channel_name in self.hubei_dictionary:
            self.hubei_lines.append(processed_line)
            return True
        elif channel_name in self.anhui_dictionary:
            self.anhui_lines.append(processed_line)
            return True
        elif channel_name in self.fujian_dictionary:
            self.fujian_lines.append(processed_line)
            return True
        elif channel_name in self.liaoning_dictionary:
            self.liaoning_lines.append(processed_line)
            return True
        elif channel_name in self.shaanxi_dictionary:
            self.shaanxi_lines.append(processed_line)
            return True
        elif channel_name in self.hebei_dictionary:
            self.hebei_lines.append(processed_line)
            return True
        elif channel_name in self.jiangxi_dictionary:
            self.jiangxi_lines.append(processed_line)
            return True
        elif channel_name in self.guangxi_dictionary:
            self.guangxi_lines.append(processed_line)
            return True
        elif channel_name in self.yunnan_dictionary:
            self.yunnan_lines.append(processed_line)
            return True
        elif channel_name in self.shanxi_dictionary:
            self.shanxi_lines.append(processed_line)
            return True
        elif channel_name in self.heilongjiang_dictionary:
            self.heilongjiang_lines.append(processed_line)
            return True
        elif channel_name in self.jilin_dictionary:
            self.jilin_lines.append(processed_line)
            return True
        elif channel_name in self.guizhou_dictionary:
            self.guizhou_lines.append(processed_line)
            return True
        elif channel_name in self.gansu_dictionary:
            self.gansu_lines.append(processed_line)
            return True
        elif channel_name in self.neimenggu_dictionary:
            self.neimenggu_lines.append(processed_line)
            return True
        elif channel_name in self.xinjiang_dictionary:
            self.xinjiang_lines.append(processed_line)
            return True
        elif channel_name in self.hainan_dictionary:
            self.hainan_lines.append(processed_line)
            return True
        elif channel_name in self.ningxia_dictionary:
            self.ningxia_lines.append(processed_line)
            return True
        elif channel_name in self.qinghai_dictionary:
            self.qinghai_lines.append(processed_line)
            return True
        elif channel_name in self.xizang_dictionary:
            self.xizang_lines.append(processed_line)
            return True
            
        # 4. 港澳台地区
        elif channel_name in self.hongkong_dictionary:
            self.hongkong_lines.append(processed_line)
            return True
        elif channel_name in self.macau_dictionary:
            self.macau_lines.append(processed_line)
            return True
        elif channel_name in self.minnan_dictionary:
            self.minnan_lines.append(processed_line)
            return True
            
        # 5. 其他分类
        elif channel_name in self.digital_dictionary:
            self.digital_lines.append(processed_line)
            return True
        elif channel_name in self.movie_dictionary:
            self.movie_lines.append(processed_line)
            return True
        elif channel_name in self.tv_drama_dictionary:
            self.tv_drama_lines.append(processed_line)
            return True
        elif channel_name in self.documentary_dictionary:
            self.documentary_lines.append(processed_line)
            return True
        elif channel_name in self.cartoon_dictionary:
            self.cartoon_lines.append(processed_line)
            return True
        elif channel_name in self.radio_dictionary:
            self.radio_lines.append(processed_line)
            return True
        elif channel_name in self.variety_dictionary:
            self.variety_lines.append(processed_line)
            return True
        elif channel_name in self.huya_dictionary:
            self.huya_lines.append(processed_line)
            return True
        elif channel_name in self.douyu_dictionary:
            self.douyu_lines.append(processed_line)
            return True
        elif channel_name in self.commentary_dictionary:
            self.commentary_lines.append(processed_line)
            return True
        elif channel_name in self.music_dictionary:
            self.music_lines.append(processed_line)
            return True
        elif channel_name in self.food_dictionary:
            self.food_lines.append(processed_line)
            return True
        elif channel_name in self.travel_dictionary:
            self.travel_lines.append(processed_line)
            return True
        elif channel_name in self.health_dictionary:
            self.health_lines.append(processed_line)
            return True
        elif channel_name in self.finance_dictionary:
            self.finance_lines.append(processed_line)
            return True
        elif channel_name in self.shopping_dictionary:
            self.shopping_lines.append(processed_line)
            return True
        elif channel_name in self.game_dictionary:
            self.game_lines.append(processed_line)
            return True
        elif channel_name in self.news_dictionary:
            self.news_lines.append(processed_line)
            return True
        elif channel_name in self.china_dictionary:
            self.china_lines.append(processed_line)
            return True
        elif channel_name in self.international_dictionary:
            self.international_lines.append(processed_line)
            return True
        elif channel_name in self.sports_dictionary:
            self.sports_lines.append(processed_line)
            return True
        elif any(keyword in channel_name for keyword in self.tyss_dictionary):
            self.tyss_lines.append(processed_line)
            return True
        elif any(keyword in channel_name for keyword in self.mgss_dictionary):
            self.mgss_lines.append(processed_line)
            return True
        elif channel_name in self.traditional_opera_dictionary:
            self.traditional_opera_lines.append(processed_line)
            return True
        elif channel_name in self.spring_festival_gala_dictionary:
            self.spring_festival_gala_lines.append(processed_line)
            return True
        elif channel_name in self.camera_dictionary:
            self.camera_lines.append(processed_line)
            return True
        elif channel_name in self.favorite_dictionary:
            self.favorite_lines.append(processed_line)
            return True
        
        return False
    
    def get_random_user_agent(self) -> str:
        """随机获取User-Agent"""
        USER_AGENTS = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
        ]
        return random.choice(USER_AGENTS)
    
    def get_http_response(self, url: str, timeout: int = 8, retries: int = 2) -> Optional[str]:
        """获取HTTP响应，支持重试机制"""
        headers = {
            'User-Agent': self.get_random_user_agent()
        }
        
        for attempt in range(retries):
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=timeout) as response:
                    data = response.read()
                    return data.decode('utf-8')
            except HTTPError as e:
                logger.error(f"[HTTPError] Code: {e.code}, URL: {url}")
                break
            except (URLError, socket.timeout) as e:
                logger.warning(f"[网络错误] {type(e).__name__}: {e}, URL: {url}, 尝试: {attempt + 1}")
                if attempt < retries - 1:
                    time.sleep(1 * (2 ** attempt))  # 指数退避
            except Exception as e:
                logger.error(f"[异常] {type(e).__name__}: {e}, URL: {url}")
        
        return None
    
    def process_url_source(self, url: str) -> int:
        """处理单个URL源，返回处理的频道数"""
        logger.info(f"开始处理URL: {url}")
        
        try:
            # 记录处理的URL
            self.other_lines.append(f"◆◆◆　{url}")
            
            # 获取内容
            content = self.get_http_response(url)
            if not content:
                logger.warning(f"获取内容失败: {url}")
                return 0
            
            # 检查是否为M3U格式
            is_m3u = content.startswith("#EXTM3U") or content.startswith("#EXTINF")
            if self.get_url_file_extension(url) in [".m3u", ".m3u8"] or is_m3u:
                content = self.convert_m3u_to_txt(content)
            
            # 逐行处理
            lines = content.split('\n')
            processed_count = 0
            
            for line in lines:
                # 过滤无效行
                if ("#genre#" not in line and "," in line and "://" in line and 
                    "tvbus://" not in line and "/udp/" not in line):
                    
                    parts = line.split(',', 1)
                    if len(parts) < 2:
                        continue
                    
                    channel_name, channel_address = parts[0], parts[1]
                    
                    # 处理加速源（包含#号分隔的多个URL）
                    if "#" not in channel_address:
                        # 普通源
                        if self.process_channel_line(line):
                            processed_count += 1
                    else:
                        # 加速源，分割处理
                        url_list = channel_address.split('#')
                        for channel_url in url_list:
                            if channel_url.strip():
                                newline = f'{channel_name},{channel_url}'
                                if self.process_channel_line(newline):
                                    processed_count += 1
            
            logger.info(f"URL处理完成: {url}, 成功处理 {processed_count} 个频道")
            self.other_lines.append('\n')  # 添加空行分隔
            
            return processed_count
            
        except Exception as e:
            logger.error(f"处理URL时发生错误 {url}: {e}")
            return 0
    
    def correct_name_data(self, corrections: Dict[str, str], data: List[str]) -> List[str]:
        """使用纠错字典修正频道名称"""
        corrected_data = []
        for line in data:
            line = line.strip()
            if ',' not in line:
                continue
            
            name, url = line.split(',', 1)
            
            # 应用纠错
            if name in corrections and name != corrections[name]:
                name = corrections[name]
            
            corrected_data.append(f"{name},{url}")
        return corrected_data
    
    def sort_data(self, order: List[str], data: List[str]) -> List[str]:
        """按指定顺序对数据进行排序"""
        order_dict = {name: i for i, name in enumerate(order)}
        
        def sort_key(line):
            name = line.split(',')[0]
            return order_dict.get(name, len(order))
        
        return sorted(data, key=sort_key)
    
    def normalize_date_to_md(self, text: str) -> str:
        """将各种日期格式统一为MM-DD格式"""
        text = text.strip()
        
        def format_md(m):
            month = int(m.group(1))
            day = int(m.group(2))
            after = m.group(3) or ''
            if not after.startswith(' '):
                after = ' ' + after
            return f"{month:02d}-{day:02d}{after}"
        
        # MM/DD或M/D格式
        text = re.sub(r'^0?(\d{1,2})/0?(\d{1,2})(.*)', format_md, text)
        
        # YYYY-MM-DD或类似格式
        text = re.sub(r'^\d{4}-0?(\d{1,2})-0?(\d{1,2})(.*)', format_md, text)
        
        # 中文M月D日格式
        text = re.sub(r'^0?(\d{1,2})月0?(\d{1,2})日(.*)', format_md, text)
        
        return text
    
    def filter_lines(self, lines: List[str], exclude_keywords: List[str]) -> List[str]:
        """过滤包含特定关键词的行"""
        return [line for line in lines if not any(keyword in line for keyword in exclude_keywords)]
    
    def custom_tyss_sort(self, lines: List[str]) -> List[str]:
        """体育赛事专用排序：数字开头倒序排在上面，其他升序排在下面"""
        digit_prefix = []
        others = []
        
        for line in lines:
            name_part = line.split(',')[0].strip()
            if name_part and name_part[0].isdigit():
                digit_prefix.append(line)
            else:
                others.append(line)
        
        # 分别排序
        digit_prefix_sorted = sorted(digit_prefix, reverse=True)
        others_sorted = sorted(others)
        
        return digit_prefix_sorted + others_sorted
    
    def generate_playlist_html(self, data_list: List[str], output_file: str = 'playlist.html'):
        """生成HTML格式的播放列表"""
        html_head = '''
        <!DOCTYPE html>
        <html lang="zh">
        <head>
            <meta charset="UTF-8">
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
        logger.info(f"网页已生成: {output_file}")
    
    def make_m3u(self, txt_file: str, m3u_file: str):
        """将TXT格式转换为M3U格式"""
        try:
            # 读取Logo库
            channels_logos = self.read_txt_to_array('assets/livesource/logo.txt')
            
            def get_logo_by_channel_name(channel_name):
                """根据频道名称获取Logo URL"""
                for line in channels_logos:
                    if not line.strip():
                        continue
                    if ',' in line:
                        name, url = line.split(',', 1)
                        if name == channel_name:
                            return url
                return None
            
            # M3U文件头
            output_text = '#EXTM3U x-tvg-url="https://live.fanmingming.cn/e.xml"\n'
            
            with open(txt_file, "r", encoding='utf-8') as file:
                input_text = file.read()
            
            lines = input_text.strip().split("\n")
            group_name = ""
            
            for line in lines:
                parts = line.split(",")
                # 处理分组标题行
                if len(parts) == 2 and "#genre#" in line:
                    group_name = parts[0]
                # 处理频道行
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
            
            # 写入M3U文件
            with open(f"{m3u_file}", "w", encoding='utf-8') as file:
                file.write(output_text)
            
            logger.info(f"M3U文件已生成: {m3u_file}")
            
        except Exception as e:
            logger.error(f"生成M3U文件失败: {e}")
    
    def get_random_url(self, file_path: str) -> Optional[str]:
        """从文件中随机获取一个URL"""
        urls = []
        if not os.path.exists(file_path):
            logger.warning(f"文件不存在: {file_path}")
            return None
            
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                if ',' in line:
                    url = line.strip().split(',')[-1]
                    urls.append(url)
        
        return random.choice(urls) if urls else None
    
    def process(self):
        """主处理流程"""
        logger.info("=" * 60)
        logger.info("IPTV直播源聚合处理工具 v3.0 开始运行")
        logger.info("=" * 60)
        
        # 记录开始时间
        self.stats["start_time"] = datetime.now()
        
        # 1. 处理URL源
        logger.info("步骤1: 处理URL源")
        urls = self.read_txt_to_array('assets/livesource/urls-daily.txt')
        logger.info(f"发现 {len(urls)} 个数据源")
        
        total_processed = 0
        for url in urls:
            if url.startswith("http"):
                # 处理日期变量
                if "{MMdd}" in url:
                    current_date_str = datetime.now().strftime("%m%d")
                    url = url.replace("{MMdd}", current_date_str)
                
                if "{MMdd-1}" in url:
                    yesterday_date_str = (datetime.now() - timedelta(days=1)).strftime("%m%d")
                    url = url.replace("{MMdd-1}", yesterday_date_str)
                
                processed = self.process_url_source(url)
                total_processed += processed
        
        logger.info(f"URL处理完成，共处理 {total_processed} 个频道")
        
        # 2. 处理白名单
        logger.info("步骤2: 处理白名单")
        whitelist_auto_lines = self.read_txt_to_array('assets/livesource/blacklist/whitelist_auto.txt')
        whitelist_count = 0
        
        for whitelist_line in whitelist_auto_lines:
            if "#genre#" not in whitelist_line and "," in whitelist_line and "://" in whitelist_line:
                whitelist_parts = whitelist_line.split(",")
                try:
                    response_time = float(whitelist_parts[0].replace("ms", ""))
                except ValueError:
                    response_time = 60000
                
                # 只添加响应时间小于2秒的高质量源
                if response_time < 2000:
                    if self.process_channel_line(",".join(whitelist_parts[1:])):
                        whitelist_count += 1
        
        logger.info(f"添加 {whitelist_count} 个高质量白名单源")
        
        # 3. 处理AKTV源
        logger.info("步骤3: 处理AKTV源")
        aktv_url = "https://raw.githubusercontent.com/xiaoran67/update/refs/heads/main/assets/livesource/%E6%89%8B%E5%B7%A5%E5%8C%BA/channels.txt"
        
        aktv_text = self.get_http_response(aktv_url)
        if aktv_text:
            logger.info("成功获取AKTV源")
            aktv_text = self.convert_m3u_to_txt(aktv_text)
            aktv_lines = aktv_text.strip().split('\n')
        else:
            logger.warning("AKTV请求失败，从本地获取")
            aktv_lines = self.read_txt_to_array('assets/livesource/手工区/AKTV.txt')
        
        aktv_processed = 0
        for line in aktv_lines:
            if self.process_channel_line(line):
                aktv_processed += 1
        
        logger.info(f"处理AKTV数据，共 {aktv_processed} 个频道")
        
        # 4. 处理手工区数据
        logger.info("步骤4: 处理手工区数据")
        
        # 浙江频道
        zhejiang_manual = self.read_txt_to_array('assets/livesource/手工区/浙江频道.txt')
        self.zhejiang_lines.extend(zhejiang_manual)
        logger.info(f"浙江频道: 添加 {len(zhejiang_manual)} 个手工源")
        
        # 广东频道
        guangdong_manual = self.read_txt_to_array('assets/livesource/手工区/广东频道.txt')
        self.guangdong_lines.extend(guangdong_manual)
        logger.info(f"广东频道: 添加 {len(guangdong_manual)} 个手工源")
        
        # 湖北频道
        hubei_manual = self.read_txt_to_array('assets/livesource/手工区/湖北频道.txt')
        self.hubei_lines.extend(hubei_manual)
        logger.info(f"湖北频道: 添加 {len(hubei_manual)} 个手工源")
        
        # 上海频道
        shanghai_manual = self.read_txt_to_array('assets/livesource/手工区/上海频道.txt')
        self.shanghai_lines.extend(shanghai_manual)
        logger.info(f"上海频道: 添加 {len(shanghai_manual)} 个手工源")
        
        # 江苏频道
        jiangsu_manual = self.read_txt_to_array('assets/livesource/手工区/江苏频道.txt')
        self.jiangsu_lines.extend(jiangsu_manual)
        logger.info(f"江苏频道: 添加 {len(jiangsu_manual)} 个手工源")
        
        # 5. 处理体育赛事
        logger.info("步骤5: 处理体育赛事")
        
        # 日期格式化
        normalized_tyss_lines = [self.normalize_date_to_md(s) for s in self.tyss_lines]
        
        # 过滤关键词
        keywords_to_exclude_tiyu_txt = ["玉玉软件", "榴芒电视", "公众号", "麻豆", "「回看」"]
        keywords_to_exclude_tiyu = ["玉玉软件", "榴芒电视", "公众号", "咪视通", "麻豆", "「回看」"]
        
        # 应用过滤和排序
        normalized_tyss_lines = self.filter_lines(normalized_tyss_lines, keywords_to_exclude_tiyu_txt)
        normalized_tyss_lines = self.custom_tyss_sort(set(normalized_tyss_lines))
        self.filtered_tyss_lines = self.filter_lines(normalized_tyss_lines, keywords_to_exclude_tiyu)
        
        logger.info(f"体育赛事处理完成: 原始 {len(self.tyss_lines)} 条, 过滤后 {len(self.filtered_tyss_lines)} 条")
        
        # 生成HTML页面
        self.generate_playlist_html(self.filtered_tyss_lines, 'output/tiyu.html')
        
        # 保存TXT文件
        with open('output/tiyu.txt', 'w', encoding='utf-8') as f:
            for line in self.filtered_tyss_lines:
                f.write(line + '\n')
        logger.info("体育赛事文本已保存: output/tiyu.txt")
        
        # 6. 生成今日推荐和版本信息
        logger.info("步骤6: 生成今日推荐和版本信息")
        
        # 获取北京时间
        utc_time = datetime.now(timezone.utc)
        beijing_time = utc_time + timedelta(hours=8)
        formatted_time = beijing_time.strftime("%Y%m%d %H:%M:%S")
        
        # 生成今日推荐
        MTV1 = "💯推荐," + (self.get_random_url('assets/livesource/手工区/今日推荐.txt') or "")
        MTV2 = "🤫低调," + (self.get_random_url('assets/livesource/手工区/今日推荐.txt') or "")
        MTV3 = "🟢使用," + (self.get_random_url('assets/livesource/手工区/今日推荐.txt') or "")
        MTV4 = "⚠️禁止," + (self.get_random_url('assets/livesource/手工区/今日推荐.txt') or "")
        MTV5 = "🚫贩卖," + (self.get_random_url('assets/livesource/手工区/今日推荐.txt') or "")
        
        # 生成版本信息
        version = formatted_time + "," + (self.get_random_url('assets/livesource/手工区/今日推台.txt') or "")
        about = "👨潇然," + (self.get_random_url('assets/livesource/手工区/今日推台.txt') or "")
        
        # 7. 生成播放列表文件
        logger.info("步骤7: 生成播放列表文件")
        
        # 完整版播放列表
        all_lines_full = [
            "🌐央视频道,#genre#"] + self.sort_data(self.yangshi_dictionary, self.correct_name_data(self.corrections_name, self.yangshi_lines)) + ['\n'] + \
            ["📡卫视频道,#genre#"] + self.sort_data(self.weishi_dictionary, self.correct_name_data(self.corrections_name, self.weishi_lines)) + ['\n'] + \
            ["🏛️北京频道,#genre#"] + self.sort_data(self.beijing_dictionary, self.correct_name_data(self.corrections_name, self.beijing_lines)) + ['\n'] + \
            ["🏙️上海频道,#genre#"] + self.sort_data(self.shanghai_dictionary, self.correct_name_data(self.corrections_name, self.shanghai_lines)) + ['\n'] + \
            ["🐯广东频道,#genre#"] + self.sort_data(self.guangdong_dictionary, self.correct_name_data(self.corrections_name, self.guangdong_lines)) + ['\n'] + \
            ["🎐江苏频道,#genre#"] + self.sort_data(self.jiangsu_dictionary, self.correct_name_data(self.corrections_name, self.jiangsu_lines)) + ['\n'] + \
            ["🧵浙江频道,#genre#"] + self.sort_data(self.zhejiang_dictionary, self.correct_name_data(self.corrections_name, self.zhejiang_lines)) + ['\n'] + \
            ["⛰️山东频道,#genre#"] + self.sort_data(self.shandong_dictionary, self.correct_name_data(self.corrections_name, self.shandong_lines)) + ['\n'] + \
            ["🐼四川频道,#genre#"] + self.sort_data(self.sichuan_dictionary, self.correct_name_data(self.corrections_name, self.sichuan_lines)) + ['\n'] + \
            ["🐘河南频道,#genre#"] + self.sort_data(self.henan_dictionary, self.correct_name_data(self.corrections_name, self.henan_lines)) + ['\n'] + \
            ["🌶️湖南频道,#genre#"] + self.sort_data(self.hunan_dictionary, self.correct_name_data(self.corrections_name, self.hunan_lines)) + ['\n'] + \
            ["🏞️重庆频道,#genre#"] + self.sort_data(self.chongqing_dictionary, self.correct_name_data(self.corrections_name, self.chongqing_lines)) + ['\n'] + \
            ["🚢天津频道,#genre#"] + self.sort_data(self.tianjin_dictionary, self.correct_name_data(self.corrections_name, self.tianjin_lines)) + ['\n'] + \
            ["🏯湖北频道,#genre#"] + self.sort_data(self.hubei_dictionary, self.correct_name_data(self.corrections_name, self.hubei_lines)) + ['\n'] + \
            ["🌾安徽频道,#genre#"] + self.sort_data(self.anhui_dictionary, self.correct_name_data(self.corrections_name, self.anhui_lines)) + ['\n'] + \
            ["🌊福建频道,#genre#"] + self.sort_data(self.fujian_dictionary, self.correct_name_data(self.corrections_name, self.fujian_lines)) + ['\n'] + \
            ["⛰️辽宁频道,#genre#"] + self.sort_data(self.liaoning_dictionary, self.correct_name_data(self.corrections_name, self.liaoning_lines)) + ['\n'] + \
            ["🔥陕西频道,#genre#"] + self.sort_data(self.shaanxi_dictionary, self.correct_name_data(self.corrections_name, self.shaanxi_lines)) + ['\n'] + \
            ["⛩️河北频道,#genre#"] + self.sort_data(self.hebei_dictionary, self.correct_name_data(self.corrections_name, self.hebei_lines)) + ['\n'] + \
            ["🔥江西频道,#genre#"] + self.sort_data(self.jiangxi_dictionary, self.correct_name_data(self.corrections_name, self.jiangxi_lines)) + ['\n'] + \
            ["💃广西频道,#genre#"] + self.sort_data(self.guangxi_dictionary, self.correct_name_data(self.corrections_name, self.guangxi_lines)) + ['\n'] + \
            ["☁️云南频道,#genre#"] + self.sort_data(self.yunnan_dictionary, self.correct_name_data(self.corrections_name, self.yunnan_lines)) + ['\n'] + \
            ["🏮山西频道,#genre#"] + self.sort_data(self.shanxi_dictionary, self.correct_name_data(self.corrections_name, self.shanxi_lines)) + ['\n'] + \
            ["🐻黑·龙·江,#genre#"] + self.sort_data(self.heilongjiang_dictionary, self.correct_name_data(self.corrections_name, self.heilongjiang_lines)) + ['\n'] + \
            ["🎎吉林频道,#genre#"] + self.sort_data(self.jilin_dictionary, self.correct_name_data(self.corrections_name, self.jilin_lines)) + ['\n'] + \
            ["⛰️贵州频道,#genre#"] + self.sort_data(self.guizhou_dictionary, self.correct_name_data(self.corrections_name, self.guizhou_lines)) + ['\n'] + \
            ["🐫甘肃频道,#genre#"] + self.sort_data(self.gansu_dictionary, self.correct_name_data(self.corrections_name, self.gansu_lines)) + ['\n'] + \
            ["🐮内·蒙·古,#genre#"] + self.sort_data(self.neimenggu_dictionary, self.correct_name_data(self.corrections_name, self.neimenggu_lines)) + ['\n'] + \
            ["🍇新疆频道,#genre#"] + self.sort_data(self.xinjiang_dictionary, self.correct_name_data(self.corrections_name, self.xinjiang_lines)) + ['\n'] + \
            ["🏝️海南频道,#genre#"] + self.sort_data(self.hainan_dictionary, self.correct_name_data(self.corrections_name, self.hainan_lines)) + ['\n'] + \
            ["🕌宁夏频道,#genre#"] + self.sort_data(self.ningxia_dictionary, self.correct_name_data(self.corrections_name, self.ningxia_lines)) + ['\n'] + \
            ["🐑青海频道,#genre#"] + self.sort_data(self.qinghai_dictionary, self.correct_name_data(self.corrections_name, self.qinghai_lines)) + ['\n'] + \
            ["🐐西藏频道,#genre#"] + self.sort_data(self.xizang_dictionary, self.correct_name_data(self.corrections_name, self.xizang_lines)) + ['\n'] + \
            ["🇭🇰香港频道,#genre#"] + self.sort_data(self.hongkong_dictionary, self.correct_name_data(self.corrections_name, self.hongkong_lines)) + ['\n'] + \
            ["🇲🇴澳门频道,#genre#"] + self.sort_data(self.macau_dictionary, self.correct_name_data(self.corrections_name, self.macau_lines)) + ['\n'] + \
            ["🇨🇳闽南频道,#genre#"] + self.sort_data(self.minnan_dictionary, self.correct_name_data(self.corrections_name, self.minnan_lines)) + ['\n'] + \
            ["🔢数字频道,#genre#"] + self.sort_data(self.digital_dictionary, self.correct_name_data(self.corrections_name, self.digital_lines)) + ['\n'] + \
            ["🎬电影频道,#genre#"] + self.sort_data(self.movie_dictionary, self.correct_name_data(self.corrections_name, self.movie_lines)) + ['\n'] + \
            ["📺电·视·剧,#genre#"] + self.sort_data(self.tv_drama_dictionary, self.correct_name_data(self.corrections_name, self.tv_drama_lines)) + ['\n'] + \
            ["🎥纪·录·片,#genre#"] + self.sort_data(self.documentary_dictionary, self.correct_name_data(self.corrections_name, self.documentary_lines)) + ['\n'] + \
            ["🐱动·画·片,#genre#"] + self.sort_data(self.cartoon_dictionary, self.correct_name_data(self.corrections_name, self.cartoon_lines)) + ['\n'] + \
            ["📻收·音·机,#genre#"] + self.sort_data(self.radio_dictionary, self.correct_name_data(self.corrections_name, self.radio_lines)) + ['\n'] + \
            ["🎭综艺频道,#genre#"] + self.sort_data(self.variety_dictionary, self.correct_name_data(self.corrections_name, self.variety_lines)) + ['\n'] + \
            ["🐯虎牙直播,#genre#"] + self.sort_data(self.huya_dictionary, self.correct_name_data(self.corrections_name, self.huya_lines)) + ['\n'] + \
            ["🐠斗鱼直播,#genre#"] + self.sort_data(self.douyu_dictionary, self.correct_name_data(self.corrections_name, self.douyu_lines)) + ['\n'] + \
            ["🎤解说频道,#genre#"] + self.sort_data(self.commentary_dictionary, self.correct_name_data(self.corrections_name, self.commentary_lines)) + ['\n'] + \
            ["🎵音乐频道,#genre#"] + self.sort_data(self.music_dictionary, self.correct_name_data(self.corrections_name, self.music_lines)) + ['\n'] + \
            ["🍜美食频道,#genre#"] + self.sort_data(self.food_dictionary, self.correct_name_data(self.corrections_name, self.food_lines)) + ['\n'] + \
            ["✈️旅游频道,#genre#"] + self.sort_data(self.travel_dictionary, self.correct_name_data(self.corrections_name, self.travel_lines)) + ['\n'] + \
            ["🏥健康频道,#genre#"] + self.sort_data(self.health_dictionary, self.correct_name_data(self.corrections_name, self.health_lines)) + ['\n'] + \
            ["💰财经频道,#genre#"] + self.sort_data(self.finance_dictionary, self.correct_name_data(self.corrections_name, self.finance_lines)) + ['\n'] + \
            ["🛍️购物频道,#genre#"] + self.sort_data(self.shopping_dictionary, self.correct_name_data(self.corrections_name, self.shopping_lines)) + ['\n'] + \
            ["🎮游戏频道,#genre#"] + self.sort_data(self.game_dictionary, self.correct_name_data(self.corrections_name, self.game_lines)) + ['\n'] + \
            ["📰新闻频道,#genre#"] + self.sort_data(self.news_dictionary, self.correct_name_data(self.corrections_name, self.news_lines)) + ['\n'] + \
            ["🇨🇳中国综合,#genre#"] + self.sort_data(self.china_dictionary, self.correct_name_data(self.corrections_name, self.china_lines)) + ['\n'] + \
            ["🌐国际频道,#genre#"] + self.sort_data(self.international_dictionary, self.correct_name_data(self.corrections_name, self.international_lines)) + ['\n'] + \
            ["⚽体育频道,#genre#"] + self.sort_data(self.sports_dictionary, self.correct_name_data(self.corrections_name, self.sports_lines)) + ['\n'] + \
            ["🏆体育赛事,#genre#"] + self.filtered_tyss_lines + ['\n'] + \
            ["🏈咪咕赛事,#genre#"] + sorted(set(self.mgss_lines)) + ['\n'] + \
            ["🎭戏曲频道,#genre#"] + self.sort_data(self.traditional_opera_dictionary, self.correct_name_data(self.corrections_name, self.traditional_opera_lines)) + ['\n'] + \
            ["🧨春晚频道,#genre#"] + self.sort_data(self.spring_festival_gala_dictionary, self.correct_name_data(self.corrections_name, self.spring_festival_gala_lines)) + ['\n'] + \
            ["🏞️景区直播,#genre#"] + self.sort_data(self.camera_dictionary, self.correct_name_data(self.corrections_name, self.camera_lines)) + ['\n'] + \
            ["⭐收藏频道,#genre#"] + self.sort_data(self.favorite_dictionary, self.correct_name_data(self.corrections_name, self.favorite_lines)) + ['\n'] + \
            ["📦其他频道,#genre#"] + sorted(set(self.other_lines)) + ['\n'] + \
            ["🕒更新时间,#genre#"] + [version] + [about] + [MTV1] + [MTV2] + [MTV3] + [MTV4] + [MTV5] + ['\n']
        
        # 精简版播放列表
        all_lines_lite = [
            "🌐央视频道,#genre#"] + self.sort_data(self.yangshi_dictionary, self.correct_name_data(self.corrections_name, self.yangshi_lines)) + ['\n'] + \
            ["📡卫视频道,#genre#"] + self.sort_data(self.weishi_dictionary, self.correct_name_data(self.corrections_name, self.weishi_lines)) + ['\n'] + \
            ["🏠地·方·台,#genre#"] + \
            self.sort_data(self.beijing_dictionary, self.correct_name_data(self.corrections_name, self.beijing_lines)) + \
            self.sort_data(self.shanghai_dictionary, self.correct_name_data(self.corrections_name, self.shanghai_lines)) + \
            self.sort_data(self.tianjin_dictionary, self.correct_name_data(self.corrections_name, self.tianjin_lines)) + \
            self.sort_data(self.chongqing_dictionary, self.correct_name_data(self.corrections_name, self.chongqing_lines)) + \
            self.sort_data(self.guangdong_dictionary, self.correct_name_data(self.corrections_name, self.guangdong_lines)) + \
            self.sort_data(self.jiangsu_dictionary, self.correct_name_data(self.corrections_name, self.jiangsu_lines)) + \
            self.sort_data(self.zhejiang_dictionary, self.correct_name_data(self.corrections_name, self.zhejiang_lines)) + \
            self.sort_data(self.shandong_dictionary, self.correct_name_data(self.corrections_name, self.shandong_lines)) + \
            self.sort_data(self.henan_dictionary, self.correct_name_data(self.corrections_name, self.henan_lines)) + \
            self.sort_data(self.sichuan_dictionary, self.correct_name_data(self.corrections_name, self.sichuan_lines)) + \
            self.sort_data(self.hebei_dictionary, self.correct_name_data(self.corrections_name, self.hebei_lines)) + \
            self.sort_data(self.hunan_dictionary, self.correct_name_data(self.corrections_name, self.hunan_lines)) + \
            self.sort_data(self.hubei_dictionary, self.correct_name_data(self.corrections_name, self.hubei_lines)) + \
            self.sort_data(self.anhui_dictionary, self.correct_name_data(self.corrections_name, self.anhui_lines)) + \
            self.sort_data(self.fujian_dictionary, self.correct_name_data(self.corrections_name, self.fujian_lines)) + \
            self.sort_data(self.shaanxi_dictionary, self.correct_name_data(self.corrections_name, self.shaanxi_lines)) + \
            self.sort_data(self.liaoning_dictionary, self.correct_name_data(self.corrections_name, self.liaoning_lines)) + \
            self.sort_data(self.jiangxi_dictionary, self.correct_name_data(self.corrections_name, self.jiangxi_lines)) + \
            self.sort_data(self.heilongjiang_dictionary, self.correct_name_data(self.corrections_name, self.heilongjiang_lines)) + \
            self.sort_data(self.jilin_dictionary, self.correct_name_data(self.corrections_name, self.jilin_lines)) + \
            self.sort_data(self.shanxi_dictionary, self.correct_name_data(self.corrections_name, self.shanxi_lines)) + \
            self.sort_data(self.guangxi_dictionary, self.correct_name_data(self.corrections_name, self.guangxi_lines)) + \
            self.sort_data(self.yunnan_dictionary, self.correct_name_data(self.corrections_name, self.yunnan_lines)) + \
            self.sort_data(self.guizhou_dictionary, self.correct_name_data(self.corrections_name, self.guizhou_lines)) + \
            self.sort_data(self.gansu_dictionary, self.correct_name_data(self.corrections_name, self.gansu_lines)) + \
            self.sort_data(self.neimenggu_dictionary, self.correct_name_data(self.corrections_name, self.neimenggu_lines)) + \
            self.sort_data(self.xinjiang_dictionary, self.correct_name_data(self.corrections_name, self.xinjiang_lines)) + \
            self.sort_data(self.hainan_dictionary, self.correct_name_data(self.corrections_name, self.hainan_lines)) + \
            self.sort_data(self.ningxia_dictionary, self.correct_name_data(self.corrections_name, self.ningxia_lines)) + \
            self.sort_data(self.qinghai_dictionary, self.correct_name_data(self.corrections_name, self.qinghai_lines)) + \
            self.sort_data(self.xizang_dictionary, self.correct_name_data(self.corrections_name, self.xizang_lines)) + ['\n'] + \
            ["🕒更新时间,#genre#"] + [version] + [about] + [MTV1] + [MTV2] + [MTV3] + [MTV4] + [MTV5] + ['\n']
        
        # 定制版播放列表
        all_lines_custom = [
            "🌐央视频道,#genre#"] + self.sort_data(self.yangshi_dictionary, self.correct_name_data(self.corrections_name, self.yangshi_lines)) + ['\n'] + \
            ["📡卫视频道,#genre#"] + self.sort_data(self.weishi_dictionary, self.correct_name_data(self.corrections_name, self.weishi_lines)) + ['\n'] + \
            ["🕒更新时间,#genre#"] + [version] + [about] + [MTV1] + [MTV2] + [MTV3] + [MTV4] + [MTV5] + ['\n']
        
        # 保存文件
        output_full = "output/full.txt"
        output_lite = "output/lite.txt"
        output_custom = "output/custom.txt"
        output_others = "output/others.txt"
        
        try:
            # 完整版
            with open(output_full, 'w', encoding='utf-8') as f:
                for line in all_lines_full:
                    f.write(line + '\n')
            logger.info(f"完整版播放列表已保存: {output_full}")
            
            # 精简版
            with open(output_lite, 'w', encoding='utf-8') as f:
                for line in all_lines_lite:
                    f.write(line + '\n')
            logger.info(f"精简版播放列表已保存: {output_lite}")
            
            # 定制版
            with open(output_custom, 'w', encoding='utf-8') as f:
                for line in all_lines_custom:
                    f.write(line + '\n')
            logger.info(f"定制版播放列表已保存: {output_custom}")
            
            # 未分类
            with open(output_others, 'w', encoding='utf-8') as f:
                for line in self.other_lines:
                    f.write(line + '\n')
            logger.info(f"未分类频道列表已保存: {output_others}")
            
        except Exception as e:
            logger.error(f"保存文件时发生错误: {e}")
        
        # 8. 生成M3U格式文件
        logger.info("步骤8: 生成M3U格式文件")
        self.make_m3u(output_full, output_full.replace(".txt", ".m3u"))
        self.make_m3u(output_lite, output_lite.replace(".txt", ".m3u"))
        self.make_m3u(output_custom, output_custom.replace(".txt", ".m3u"))
        
        # 9. 统计信息
        logger.info("步骤9: 生成统计信息")
        self._generate_statistics()
        
        logger.info("=" * 60)
        logger.info("IPTV直播源处理完成！")
        logger.info("=" * 60)
    
    def _generate_statistics(self):
        """生成统计信息"""
        # 记录结束时间
        self.stats["end_time"] = datetime.now()
        self.stats["duration"] = self.stats["end_time"] - self.stats["start_time"]
        
        # 统计各分类数量
        self.stats["category_counts"] = {
            "央视": len(self.yangshi_lines),
            "卫视": len(self.weishi_lines),
            "北京": len(self.beijing_lines),
            "上海": len(self.shanghai_lines),
            "广东": len(self.guangdong_lines),
            "江苏": len(self.jiangsu_lines),
            "浙江": len(self.zhejiang_lines),
            "山东": len(self.shandong_lines),
            "四川": len(self.sichuan_lines),
            "河南": len(self.henan_lines),
            "湖南": len(self.hunan_lines),
            "重庆": len(self.chongqing_lines),
            "天津": len(self.tianjin_lines),
            "湖北": len(self.hubei_lines),
            "安徽": len(self.anhui_lines),
            "福建": len(self.fujian_lines),
            "辽宁": len(self.liaoning_lines),
            "陕西": len(self.shaanxi_lines),
            "河北": len(self.hebei_lines),
            "江西": len(self.jiangxi_lines),
            "广西": len(self.guangxi_lines),
            "云南": len(self.yunnan_lines),
            "山西": len(self.shanxi_lines),
            "黑龙江": len(self.heilongjiang_lines),
            "吉林": len(self.jilin_lines),
            "贵州": len(self.guizhou_lines),
            "甘肃": len(self.gansu_lines),
            "内蒙古": len(self.neimenggu_lines),
            "新疆": len(self.xinjiang_lines),
            "海南": len(self.hainan_lines),
            "宁夏": len(self.ningxia_lines),
            "青海": len(self.qinghai_lines),
            "西藏": len(self.xizang_lines),
            "香港": len(self.hongkong_lines),
            "澳门": len(self.macau_lines),
            "闽南": len(self.minnan_lines),
            "数字": len(self.digital_lines),
            "电影": len(self.movie_lines),
            "电视剧": len(self.tv_drama_lines),
            "纪录片": len(self.documentary_lines),
            "动画片": len(self.cartoon_lines),
            "收音机": len(self.radio_lines),
            "综艺": len(self.variety_lines),
            "虎牙": len(self.huya_lines),
            "斗鱼": len(self.douyu_lines),
            "解说": len(self.commentary_lines),
            "音乐": len(self.music_lines),
            "美食": len(self.food_lines),
            "旅游": len(self.travel_lines),
            "健康": len(self.health_lines),
            "财经": len(self.finance_lines),
            "购物": len(self.shopping_lines),
            "游戏": len(self.game_lines),
            "新闻": len(self.news_lines),
            "中国": len(self.china_lines),
            "国际": len(self.international_lines),
            "体育": len(self.sports_lines),
            "体育赛事": len(self.filtered_tyss_lines),
            "咪咕赛事": len(self.mgss_lines),
            "戏曲": len(self.traditional_opera_lines),
            "春晚": len(self.spring_festival_gala_lines),
            "景区直播": len(self.camera_lines),
            "收藏": len(self.favorite_lines),
            "其他": len(self.other_lines),
        }
        
        # 计算总数
        total = sum(self.stats["category_counts"].values())
        self.stats["total_channels"] = total
        
        # 计算去重率
        total_processed = len(self.processed_urls) + self.stats["blacklisted"]
        if total_processed > 0:
            duplicate_rate = (self.stats["duplicates"] / total_processed) * 100
        else:
            duplicate_rate = 0
        
        # 输出统计信息
        logger.info("=" * 60)
        logger.info("📊 处理统计信息")
        logger.info("=" * 60)
        logger.info(f"开始时间: {self.stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"结束时间: {self.stats['end_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"处理时长: {self.stats['duration']}")
        logger.info(f"总频道数: {total}")
        logger.info(f"有效频道: {self.stats['valid_channels']}")
        logger.info(f"黑名单过滤: {self.stats['blacklisted']}")
        logger.info(f"URL去重: {self.stats['duplicates']}")
        logger.info(f"去重率: {duplicate_rate:.1f}%")
        logger.info(f"处理的唯一URL: {len(self.processed_urls)}")
        logger.info("")
        
        # 分类统计
        logger.info("📈 分类统计:")
        for category, count in sorted(self.stats["category_counts"].items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                logger.info(f"  {category}: {count} 个")
        
        # 保存统计信息到JSON文件
        stats_output = {
            "metadata": {
                "version": "3.0",
                "start_time": self.stats["start_time"].strftime('%Y-%m-%d %H:%M:%S'),
                "end_time": self.stats["end_time"].strftime('%Y-%m-%d %H:%M:%S'),
                "duration_seconds": self.stats["duration"].total_seconds(),
            },
            "statistics": {
                "total_channels": total,
                "valid_channels": self.stats["valid_channels"],
                "blacklisted": self.stats["blacklisted"],
                "duplicates": self.stats["duplicates"],
                "duplicate_rate": duplicate_rate,
                "unique_urls": len(self.processed_urls),
                "category_counts": self.stats["category_counts"],
            }
        }
        
        with open('处理统计.json', 'w', encoding='utf-8') as f:
            json.dump(stats_output, f, ensure_ascii=False, indent=2)
        
        logger.info("统计信息已保存到: 处理统计.json")


# ========= 主程序入口 =========
def main():
    """主函数"""
    try:
        processor = IPTVProcessor()
        processor.process()
    except KeyboardInterrupt:
        logger.info("用户中断程序")
    except Exception as e:
        logger.error(f"程序执行失败: {e}", exc_info=True)


if __name__ == "__main__":
    main()
    
# ===== LiveSource-Collector =====
# ========= 版本v0.03 =========
# ========= 脚本结束 =========

"""
IPTV直播源聚合处理工具 v0.03
基于0.00版本的全面重构版
主要改进：
1. 提前URL清理和黑名单检查，提升性能
2. 全局URL去重，避免重复处理
3. 优化的错误处理和日志系统
4. 更详细的统计信息
5. 更全面的央视识别逻辑
6. 改进的代码结构和注释
7. 完整保留0.00版本的所有分类功能
"""

"""
这个v0.03版本的主要特点：

1. 优化的架构：采用面向对象设计，代码结构更清晰
2. 提前URL清理和黑名单检查：在处理流程早期进行过滤，提升性能
3. 全局URL去重：避免重复处理相同URL
4. 增强的日志系统：详细记录处理过程，便于调试
5. 详细的统计信息：包括各类频道的数量和去重率等
6. 全面的央视识别逻辑：支持CCTV、CGTN、CETV、CEC等多种央视标识
7. 完整保留0.00版本分类：包含所有省级地方台、港澳台和其他专业频道
8. 多版本输出：生成完整版、精简版和定制版播放列表
9. M3U格式支持：自动生成M3U格式文件
10. HTML页面生成：为体育赛事生成美观的HTML播放列表

所有代码都完整保留了0.00版本的所有功能。
"""