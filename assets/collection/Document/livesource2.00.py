#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ===== 直播源聚合处理工具 ======
# ======== 版本v2.00 =========
# ========= 优化版 ===========

# ======== 模块导入区 =========
import os
import re
import time
import json
import random
import socket
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse
import urllib.request
from urllib.error import HTTPError, URLError
import opencc

# ========= 频道分类存储变量定义 =========
# 核心频道（优先级最高）
yangshi_lines = []      # 存储央视频道数据
weishi_lines = []       # 存储卫视频道数据

# 省级地方台频道
beijing_lines = []      # 北京
shanghai_lines = []     # 上海
guangdong_lines = []    # 广东
jiangsu_lines = []      # 江苏
zhejiang_lines = []     # 浙江
shandong_lines = []     # 山东
sichuan_lines = []      # 四川
henan_lines = []        # 河南
hunan_lines = []        # 湖南
chongqing_lines = []    # 重庆
tianjin_lines = []      # 天津
hubei_lines = []        # 湖北
anhui_lines = []        # 安徽
fujian_lines = []       # 福建
liaoning_lines = []     # 辽宁
shaanxi_lines = []      # 陕西
hebei_lines = []        # 河北
jiangxi_lines = []      # 江西
guangxi_lines = []      # 广西
yunnan_lines = []       # 云南
shanxi_lines = []       # 山西
heilongjiang_lines = [] # 黑龙江
jilin_lines = []        # 吉林
guizhou_lines = []      # 贵州
gansu_lines = []        # 甘肃
neimenggu_lines = []    # 内蒙古
xinjiang_lines = []     # 新疆
hainan_lines = []       # 海南
ningxia_lines = []      # 宁夏
qinghai_lines = []      # 青海
xizang_lines = []       # 西藏

# 港澳台频道
hongkong_lines = []    # 香港
macau_lines = []       # 澳门
minnan_lines = []      # 闽南

# 其他分类频道
digital_lines = []     # 数字
movie_lines = []       # 电影
tv_drama_lines = []    # 电视剧
documentary_lines = [] # 纪录片
cartoon_lines = []     # 动画片
radio_lines = []       # 收音机
variety_lines = []     # 综艺
huya_lines = []        # 虎牙
douyu_lines = []       # 斗鱼
commentary_lines = []  # 解说
music_lines = []       # 音乐
food_lines = []        # 美食
travel_lines = []      # 旅游
health_lines = []      # 健康
finance_lines = []     # 财经
shopping_lines = []    # 购物
game_lines = []        # 游戏
news_lines = []        # 新闻
china_lines = []       # 中国
international_lines = [] # 国际
sports_lines = []      # 体育
tyss_lines = []        # 体育赛事
mgss_lines = []        # 咪咕赛事
traditional_opera_lines = [] # 戏曲频道
spring_festival_gala_lines = [] # 历届春晚
camera_lines = []      # 景区直播（直播中国）
favorite_lines = []    # 收藏频道

# 未分类频道（兜底处理）
other_lines = []
other_lines_url = [] # 为降低other文件大小，剔除重复url添加

# 体育赛事专用
filtered_tyss_lines = []

# ========= 全局变量 =========
processed_urls = set()  # 用于记录已处理的URL，全局去重
combined_blacklist = set()  # 合并的黑名单
corrections_name = {}  # 频道名称纠错字典

# 频道名称清理关键字列表
removal_list = ["_电信","电信","「LiTV」","频道","频陆","备陆","壹陆","贰陆","叁陆","肆陆","伍陆","陆陆","柒陆",
                "频晴","频粤","高清","超清","标清","斯特","粤陆","国陆","肆柒","频英","频特","频国","频壹",
                "频贰","肆贰","频测","咪咕","闽特","高特","频高","频标","汝阳","频效","国标","粤标","频推",
                "频流","粤高","频限","实时","美推","频美","（HD）","-HD","英陆","_ITV","(北美)","(HK)",
                "AKtv","「IPV4」","「IPV6」","[HD]","[BD]","[SD]","[VGA]","[超清]","4Gtv","1080","720",
                "480","HD","SD","4K","VGA","(HD)","(SD)","(4K)","(VGA)","{HD}","{SD}","{4K}","{VGA}",
                "「4gTV」","「回看」","<HD>","<SD>","<4K>","<VGA>"]

# ========= 功能函数定义区 =========

# 简繁转换函数
def traditional_to_simplified(text: str) -> str:
    converter = opencc.OpenCC('t2s')
    simplified_text = converter.convert(text)
    return simplified_text

# 获取北京时间函数
def get_beijing_time():
    """获取北京时间"""
    utc_now = datetime.now(timezone.utc)
    beijing_now = utc_now + timedelta(hours=8)
    return beijing_now

# 读取文本文件函数
def read_txt_to_array(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            lines = [line.strip() for line in lines if line.strip()]  # 跳过空行
            return lines
    except FileNotFoundError:
        print(f"❌ 文件未找到: {file_name}")
        return []
    except Exception as e:
        print(f"❌ 读取文件错误 {file_name}: {e}")
        return []

# 读取黑名单
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

# 处理带$的URL，把$之后的内容都去掉（包括$也去掉）
def clean_url(url):
    last_dollar_index = url.rfind('$')  # 安全起见找最后一个$处理
    if last_dollar_index != -1:
        return url[:last_dollar_index]
    return url

# 频道名称清理
def clean_channel_name(channel_name, removal_list):
    for item in removal_list:
        channel_name = channel_name.replace(item, "")

    # 检查并移除末尾的 'HD'
    if channel_name.endswith("HD"):
        channel_name = channel_name[:-2]  # 去掉最后两个字符 "HD"

    # 移除末尾的'台'（如果频道名称长度大于3）
    if channel_name.endswith("台") and len(channel_name) > 3:
        channel_name = channel_name[:-1]  # 去掉最后两个字符 "台"

    return channel_name

# 频道名称处理
def process_name_string(input_str):
    parts = input_str.split(',')
    processed_parts = []
    for part in parts:
        processed_part = process_part(part)
        processed_parts.append(processed_part)
    result_str = ','.join(processed_parts)
    return result_str

def process_part(part_str):
    # 处理逻辑
    if "CCTV" in part_str and "://" not in part_str:
        part_str = part_str.replace("IPV6", "")  # 先剔除IPV6字样
        part_str = part_str.replace("PLUS", "+")  # 替换PLUS
        part_str = part_str.replace("1080", "")  # 替换1080
        filtered_str = ''.join(char for char in part_str if char.isdigit() or char == 'K' or char == '+')
        if not filtered_str.strip():  # 处理特殊情况，如果发现没有找到频道数字返回原名称
            filtered_str = part_str.replace("CCTV", "")

        if len(filtered_str) > 2 and re.search(r'4K|8K', filtered_str):   # 特殊处理CCTV中部分4K和8K名称
            # 使用正则表达式替换，删除4K或8K后面的字符，并且保留4K或8K
            filtered_str = re.sub(r'(4K|8K).*', r'\1', filtered_str)
            if len(filtered_str) > 2: 
                # 给4K或8K添加括号
                filtered_str = re.sub(r'(4K|8K)', r'(\1)', filtered_str)

        return "CCTV" + filtered_str 
        
    elif "卫视" in part_str:
        # 定义正则表达式模式，匹配"卫视"后面的内容
        pattern = r'卫视「.*」'
        # 使用sub函数替换匹配的内容为空字符串
        result_str = re.sub(pattern, '卫视', part_str)
        return result_str
    
    return part_str

# 获取URL文件扩展名
def get_url_file_extension(url):
    parsed_url = urlparse(url)
    path = parsed_url.path
    extension = os.path.splitext(path)[1]
    return extension

# 将M3U格式转换为TXT格式
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
        
        # 处理后缀名为m3u，但是内容为txt的文件
        if "#genre#" not in line and "," in line and "://" in line:
            pattern = r'^[^,]+,[^\s]+://[^\s]+$'
            if bool(re.match(pattern, line)):
                txt_lines.append(line)
    
    return '\n'.join(txt_lines)

# 频道名称纠错处理
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
    except Exception as e:
        print(f"❌ 加载纠错文件错误 {filename}: {e}")
    return corrections

# 纠错频道名称
def correct_name_data(corrections, data):
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

# 按指定顺序对数据进行排序
def sort_data(order, data):
    order_dict = {name: i for i, name in enumerate(order)}
    
    def sort_key(line):
        name = line.split(',')[0]
        return order_dict.get(name, len(order))
    
    sorted_data = sorted(data, key=sort_key)
    return sorted_data

# 随机获取User-Agent
def get_random_user_agent():
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    ]
    return random.choice(USER_AGENTS)

# HTTP请求处理
def get_http_response(url, timeout=8, retries=2, backoff_factor=1.0):
    headers = {'User-Agent': get_random_user_agent()}
    
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                data = response.read()
                return data.decode('utf-8')
        except HTTPError as e:
            print(f"[HTTPError] 代码: {e.code}, URL: {url}")
            break
        except (URLError, socket.timeout) as e:
            print(f"[网络错误] {type(e).__name__}: {e}, URL: {url}, 尝试: {attempt + 1}")
            if attempt < retries - 1:
                time.sleep(backoff_factor * (2 ** attempt))
        except Exception as e:
            print(f"[异常] {type(e).__name__}: {e}, URL: {url}")
    
    return None

# 新增手工区去重复 在 get_random_url 函数后面添加这个新函数
def read_and_deduplicate_manual(file_path):
    """读取手工源文件并进行内部URL去重"""
    lines = read_txt_to_array(file_path)
    if not lines:
        return []
    
    unique_lines = []
    seen_urls = set()
    
    for line in lines:
        if "#genre#" not in line and "," in line and "://" in line:
            parts = line.split(',', 1)
            if len(parts) >= 2:
                channel_url = clean_url(parts[1].strip())
                
                # 只检查这个文件内部的URL重复
                if channel_url not in seen_urls:
                    seen_urls.add(channel_url)
                    unique_lines.append(line)
    
    return unique_lines

# ========= 频道分发核心函数 =========
def process_channel_line(line):
    """处理单行频道数据，进行分类分发"""
    # 检查是否为有效的频道行
    if "#genre#" not in line and "#EXTINF:" not in line and "," in line and "://" in line:
        parts = line.split(',', 1)
        if len(parts) < 2:
            return
        
        channel_name = parts[0].strip()
        channel_address = parts[1].strip()
        
        # 提前清理URL
        channel_address = clean_url(channel_address)
        
        # 提前黑名单检查
        if channel_address in combined_blacklist:
            print(f"🚫 黑名单过滤: {channel_name}")
            return
        
        # 全局URL去重检查
        if channel_address in processed_urls:
            print(f"🔄 URL去重: {channel_name}")
            return
        processed_urls.add(channel_address)
        
        # 清理频道名称
        original_name = channel_name
        channel_name = clean_channel_name(channel_name, removal_list)
        channel_name = traditional_to_simplified(channel_name)
        
        # 频道名称纠错
        if channel_name in corrections_name:
            corrected_name = corrections_name[channel_name]
            if corrected_name != channel_name:
                print(f"🔧 名称纠错: {channel_name} -> {corrected_name}")
                channel_name = corrected_name
        
        # 重新组合行
        line = channel_name + "," + channel_address
        
        # 根据频道名称分类
        classify_channel(channel_name, process_name_string(line.strip()), channel_address)

def classify_channel(channel_name, processed_line, channel_address):
    """分类频道，返回是否成功分类"""
    # 1. 央视
    if "CCTV" in channel_name:
        yangshi_lines.append(processed_line)
        return True
        
    # 2. 卫视
    elif channel_name in weishi_dictionary:
        weishi_lines.append(processed_line)
        return True
        
    # 3. 省级地方台（按优先级顺序）
    elif channel_name in beijing_dictionary:
        beijing_lines.append(processed_line)
        return True
    elif channel_name in shanghai_dictionary:
        shanghai_lines.append(processed_line)
        return True
    elif channel_name in guangdong_dictionary:
        guangdong_lines.append(processed_line)
        return True
    elif channel_name in jiangsu_dictionary:
        jiangsu_lines.append(processed_line)
        return True
    elif channel_name in zhejiang_dictionary:
        zhejiang_lines.append(processed_line)
        return True
    elif channel_name in shandong_dictionary:
        shandong_lines.append(processed_line)
        return True
    elif channel_name in sichuan_dictionary:
        sichuan_lines.append(processed_line)
        return True
    elif channel_name in henan_dictionary:
        henan_lines.append(processed_line)
        return True
    elif channel_name in hunan_dictionary:
        hunan_lines.append(processed_line)
        return True
    elif channel_name in chongqing_dictionary:
        chongqing_lines.append(processed_line)
        return True
    elif channel_name in tianjin_dictionary:
        tianjin_lines.append(processed_line)
        return True
    elif channel_name in hubei_dictionary:
        hubei_lines.append(processed_line)
        return True
    elif channel_name in anhui_dictionary:
        anhui_lines.append(processed_line)
        return True
    elif channel_name in fujian_dictionary:
        fujian_lines.append(processed_line)
        return True
    elif channel_name in liaoning_dictionary:
        liaoning_lines.append(processed_line)
        return True
    elif channel_name in shaanxi_dictionary:
        shaanxi_lines.append(processed_line)
        return True
    elif channel_name in hebei_dictionary:
        hebei_lines.append(processed_line)
        return True
    elif channel_name in jiangxi_dictionary:
        jiangxi_lines.append(processed_line)
        return True
    elif channel_name in guangxi_dictionary:
        guangxi_lines.append(processed_line)
        return True
    elif channel_name in yunnan_dictionary:
        yunnan_lines.append(processed_line)
        return True
    elif channel_name in shanxi_dictionary:
        shanxi_lines.append(processed_line)
        return True
    elif channel_name in heilongjiang_dictionary:
        heilongjiang_lines.append(processed_line)
        return True
    elif channel_name in jilin_dictionary:
        jilin_lines.append(processed_line)
        return True
    elif channel_name in guizhou_dictionary:
        guizhou_lines.append(processed_line)
        return True
    elif channel_name in gansu_dictionary:
        gansu_lines.append(processed_line)
        return True
    elif channel_name in neimenggu_dictionary:
        neimenggu_lines.append(processed_line)
        return True
    elif channel_name in xinjiang_dictionary:
        xinjiang_lines.append(processed_line)
        return True
    elif channel_name in hainan_dictionary:
        hainan_lines.append(processed_line)
        return True
    elif channel_name in ningxia_dictionary:
        ningxia_lines.append(processed_line)
        return True
    elif channel_name in qinghai_dictionary:
        qinghai_lines.append(processed_line)
        return True
    elif channel_name in xizang_dictionary:
        xizang_lines.append(processed_line)
        return True
        
    # 4. 港澳台地区
    elif channel_name in hongkong_dictionary:
        hongkong_lines.append(processed_line)
        return True
    elif channel_name in macau_dictionary:
        macau_lines.append(processed_line)
        return True
    elif channel_name in minnan_dictionary:
        minnan_lines.append(processed_line)
        return True
        
    # 5. 其他分类
    elif channel_name in digital_dictionary:
        digital_lines.append(processed_line)
        return True
    elif channel_name in movie_dictionary:
        movie_lines.append(processed_line)
        return True
    elif channel_name in tv_drama_dictionary:
        tv_drama_lines.append(processed_line)
        return True
    elif channel_name in documentary_dictionary:
        documentary_lines.append(processed_line)
        return True
    elif channel_name in cartoon_dictionary:
        cartoon_lines.append(processed_line)
        return True
    elif channel_name in radio_dictionary:
        radio_lines.append(processed_line)
        return True
    elif channel_name in variety_dictionary:
        variety_lines.append(processed_line)
        return True
    elif channel_name in huya_dictionary:
        huya_lines.append(processed_line)
        return True
    elif channel_name in douyu_dictionary:
        douyu_lines.append(processed_line)
        return True
    elif channel_name in commentary_dictionary:
        commentary_lines.append(processed_line)
        return True
    elif channel_name in music_dictionary:
        music_lines.append(processed_line)
        return True
    elif channel_name in food_dictionary:
        food_lines.append(processed_line)
        return True
    elif channel_name in travel_dictionary:
        travel_lines.append(processed_line)
        return True
    elif channel_name in health_dictionary:
        health_lines.append(processed_line)
        return True
    elif channel_name in finance_dictionary:
        finance_lines.append(processed_line)
        return True
    elif channel_name in shopping_dictionary:
        shopping_lines.append(processed_line)
        return True
    elif channel_name in game_dictionary:
        game_lines.append(processed_line)
        return True
    elif channel_name in news_dictionary:
        news_lines.append(processed_line)
        return True
    elif channel_name in china_dictionary:
        china_lines.append(processed_line)
        return True
    elif channel_name in international_dictionary:
        international_lines.append(processed_line)
        return True
    elif channel_name in sports_dictionary:
        sports_lines.append(processed_line)
        return True
    elif any(keyword in channel_name for keyword in tyss_dictionary):
        tyss_lines.append(processed_line)
        return True
    elif any(keyword in channel_name for keyword in mgss_dictionary):
        mgss_lines.append(processed_line)
        return True
    elif channel_name in traditional_opera_dictionary:
        traditional_opera_lines.append(processed_line)
        return True
    elif channel_name in spring_festival_gala_dictionary:
        spring_festival_gala_lines.append(processed_line)
        return True
    elif channel_name in camera_dictionary:
        camera_lines.append(processed_line)
        return True
    elif channel_name in favorite_dictionary:
        favorite_lines.append(processed_line)
        return True
    
    # 未分类
    if channel_address not in other_lines_url:
        other_lines_url.append(channel_address)
        other_lines.append(processed_line)
        return True
    
    return False

# 处理URL源
def process_url(url):
    """处理单个URL，获取并解析直播源数据"""
    try:
        print(f"📡 开始处理URL: {url}")
        other_lines.append("◆◆◆　" + url)
        
        content = get_http_response(url)
        if not content:
            print(f"❌ 获取内容失败: {url}")
            return
        
        # 检查是否为M3U格式
        is_m3u = content.startswith("#EXTM3U") or content.startswith("#EXTINF")
        if get_url_file_extension(url) in [".m3u", ".m3u8"] or is_m3u:
            content = convert_m3u_to_txt(content)
        
        lines = content.split('\n')
        processed_count = 0
        
        for line in lines:
            if ("#genre#" not in line and "," in line and "://" in line and 
                "tvbus://" not in line and "/udp/" not in line):
                
                parts = line.split(',', 1)
                if len(parts) < 2:
                    continue
                
                channel_name, channel_address = parts[0], parts[1]
                
                # 处理加速源
                if "#" not in channel_address:
                    process_channel_line(line)
                    processed_count += 1
                else:
                    url_list = channel_address.split('#')
                    for channel_url in url_list:
                        if channel_url.strip():
                            newline = f'{channel_name},{channel_url}'
                            process_channel_line(newline)
                            processed_count += 1
        
        print(f"✅ 成功处理: {processed_count} 个频道")
        other_lines.append('\n')
        
    except Exception as e:
        print(f"❌ 处理URL时发生错误 {url}: {e}")

# 体育赛事日期格式化
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

    # MM/DD 或 M/D
    text = re.sub(r'^0?(\d{1,2})/0?(\d{1,2})(.*)', format_md, text)

    # YYYY-MM-DD 或类似形式
    text = re.sub(r'^\d{4}-0?(\d{1,2})-0?(\d{1,2})(.*)', format_md, text)

    # 中文M月D日格式
    text = re.sub(r'^0?(\d{1,2})月0?(\d{1,2})日(.*)', format_md, text)

    return text

# 数据过滤函数
def filter_lines(lines, exclude_keywords):
    return [line for line in lines if not any(keyword in line for keyword in exclude_keywords)]

# 体育赛事专用排序
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

# 生成HTML播放列表
def generate_playlist_html(data_list, output_file='playlist.html'):
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

# 随机URL获取函数
def get_random_url(file_path):
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

# 生成M3U格式文件
def make_m3u(txt_file, m3u_file):
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

# ========= 主处理流程 =========
def main():
    """主函数"""
    print("=" * 60)
    print("🎬 IPTV直播源聚合处理工具 v0.03 开始运行")
    print("=" * 60)
    
    # 记录开始时间
    global timestart
    timestart = get_beijing_time()
    print(f"🕒 开始时间: {timestart.strftime('%Y%m%d %H:%M:%S')}")
    
    # 初始化输出目录
    os.makedirs('output', exist_ok=True)
    print("📂 创建输出目录: output")
    
    # 加载黑名单
    print("🚫 加载黑名单...")
    blacklist_auto = read_blacklist_from_txt('assets/livesource/blacklist/blacklist_auto.txt')
    blacklist_manual = read_blacklist_from_txt('assets/livesource/blacklist/blacklist_manual.txt')
    combined_blacklist.update(blacklist_auto.union(blacklist_manual))
    print(f"✅ 黑名单加载完成: 自动 {len(blacklist_auto)} 条, 手动 {len(blacklist_manual)} 条, 总计 {len(combined_blacklist)} 条")
    
    # 加载频道字典
    print("📋 加载频道字典...")
    
    # 全局字典变量（与v0.02保持一致）
    global yangshi_dictionary, weishi_dictionary, beijing_dictionary, shanghai_dictionary, guangdong_dictionary
    global jiangsu_dictionary, zhejiang_dictionary, shandong_dictionary, sichuan_dictionary, henan_dictionary
    global hunan_dictionary, chongqing_dictionary, tianjin_dictionary, hubei_dictionary, anhui_dictionary
    global fujian_dictionary, liaoning_dictionary, shaanxi_dictionary, hebei_dictionary, jiangxi_dictionary
    global guangxi_dictionary, yunnan_dictionary, shanxi_dictionary, heilongjiang_dictionary, jilin_dictionary
    global guizhou_dictionary, gansu_dictionary, neimenggu_dictionary, xinjiang_dictionary, hainan_dictionary
    global ningxia_dictionary, qinghai_dictionary, xizang_dictionary, hongkong_dictionary, macau_dictionary
    global minnan_dictionary, digital_dictionary, movie_dictionary, tv_drama_dictionary, documentary_dictionary
    global cartoon_dictionary, radio_dictionary, variety_dictionary, huya_dictionary, douyu_dictionary
    global commentary_dictionary, music_dictionary, food_dictionary, travel_dictionary, health_dictionary
    global finance_dictionary, shopping_dictionary, game_dictionary, news_dictionary, china_dictionary
    global international_dictionary, sports_dictionary, tyss_dictionary, mgss_dictionary, traditional_opera_dictionary
    global spring_festival_gala_dictionary, camera_dictionary, favorite_dictionary, corrections_name
    
    # 读取核心频道字典
    yangshi_dictionary = read_txt_to_array('assets/livesource/主频道/CCTV.txt')
    weishi_dictionary = read_txt_to_array('assets/livesource/主频道/卫视.txt')
    
    # 读取省级地方台字典
    beijing_dictionary = read_txt_to_array('assets/livesource/地方台/北京.txt')
    shanghai_dictionary = read_txt_to_array('assets/livesource/地方台/上海.txt')
    guangdong_dictionary = read_txt_to_array('assets/livesource/地方台/广东.txt')
    jiangsu_dictionary = read_txt_to_array('assets/livesource/地方台/江苏.txt')
    zhejiang_dictionary = read_txt_to_array('assets/livesource/地方台/浙江.txt')
    shandong_dictionary = read_txt_to_array('assets/livesource/地方台/山东.txt')
    sichuan_dictionary = read_txt_to_array('assets/livesource/地方台/四川.txt')
    henan_dictionary = read_txt_to_array('assets/livesource/地方台/河南.txt')
    hunan_dictionary = read_txt_to_array('assets/livesource/地方台/湖南.txt')
    chongqing_dictionary = read_txt_to_array('assets/livesource/地方台/重庆.txt')
    tianjin_dictionary = read_txt_to_array('assets/livesource/地方台/天津.txt')
    hubei_dictionary = read_txt_to_array('assets/livesource/地方台/湖北.txt')
    anhui_dictionary = read_txt_to_array('assets/livesource/地方台/安徽.txt')
    fujian_dictionary = read_txt_to_array('assets/livesource/地方台/福建.txt')
    liaoning_dictionary = read_txt_to_array('assets/livesource/地方台/辽宁.txt')
    shaanxi_dictionary = read_txt_to_array('assets/livesource/地方台/陕西.txt')
    hebei_dictionary = read_txt_to_array('assets/livesource/地方台/河北.txt')
    jiangxi_dictionary = read_txt_to_array('assets/livesource/地方台/江西.txt')
    guangxi_dictionary = read_txt_to_array('assets/livesource/地方台/广西.txt')
    yunnan_dictionary = read_txt_to_array('assets/livesource/地方台/云南.txt')
    shanxi_dictionary = read_txt_to_array('assets/livesource/地方台/山西.txt')
    heilongjiang_dictionary = read_txt_to_array('assets/livesource/地方台/黑龙江.txt')
    jilin_dictionary = read_txt_to_array('assets/livesource/地方台/吉林.txt')
    guizhou_dictionary = read_txt_to_array('assets/livesource/地方台/贵州.txt')
    gansu_dictionary = read_txt_to_array('assets/livesource/地方台/甘肃.txt')
    neimenggu_dictionary = read_txt_to_array('assets/livesource/地方台/内蒙.txt')
    xinjiang_dictionary = read_txt_to_array('assets/livesource/地方台/新疆.txt')
    hainan_dictionary = read_txt_to_array('assets/livesource/地方台/海南.txt')
    ningxia_dictionary = read_txt_to_array('assets/livesource/地方台/宁夏.txt')
    qinghai_dictionary = read_txt_to_array('assets/livesource/地方台/青海.txt')
    xizang_dictionary = read_txt_to_array('assets/livesource/地方台/西藏.txt')
    
    # 读取港澳台地区字典
    hongkong_dictionary = read_txt_to_array('assets/livesource/地方台/香港.txt')
    macau_dictionary = read_txt_to_array('assets/livesource/地方台/澳门.txt')
    minnan_dictionary = read_txt_to_array('assets/livesource/地方台/闽南.txt')
    
    # 读取其他分类字典
    digital_dictionary = read_txt_to_array('assets/livesource/主频道/数字.txt')
    movie_dictionary = read_txt_to_array('assets/livesource/主频道/电影.txt')
    tv_drama_dictionary = read_txt_to_array('assets/livesource/主频道/电视剧.txt')
    documentary_dictionary = read_txt_to_array('assets/livesource/主频道/纪录片.txt')
    cartoon_dictionary = read_txt_to_array('assets/livesource/主频道/动画片.txt')
    radio_dictionary = read_txt_to_array('assets/livesource/主频道/收音机.txt')
    variety_dictionary = read_txt_to_array('assets/livesource/主频道/综艺.txt')
    huya_dictionary = read_txt_to_array('assets/livesource/主频道/虎牙.txt')
    douyu_dictionary = read_txt_to_array('assets/livesource/主频道/斗鱼.txt')
    commentary_dictionary = read_txt_to_array('assets/livesource/主频道/解说.txt')
    music_dictionary = read_txt_to_array('assets/livesource/主频道/音乐.txt')
    food_dictionary = read_txt_to_array('assets/livesource/主频道/美食.txt')
    travel_dictionary = read_txt_to_array('assets/livesource/主频道/旅游.txt')
    health_dictionary = read_txt_to_array('assets/livesource/主频道/健康.txt')
    finance_dictionary = read_txt_to_array('assets/livesource/主频道/财经.txt')
    shopping_dictionary = read_txt_to_array('assets/livesource/主频道/购物.txt')
    game_dictionary = read_txt_to_array('assets/livesource/主频道/游戏.txt')
    news_dictionary = read_txt_to_array('assets/livesource/主频道/新闻.txt')
    china_dictionary = read_txt_to_array('assets/livesource/主频道/中国.txt')
    international_dictionary = read_txt_to_array('assets/livesource/主频道/国际.txt')
    sports_dictionary = read_txt_to_array('assets/livesource/主频道/体育.txt')
    tyss_dictionary = read_txt_to_array('assets/livesource/主频道/体育赛事.txt')
    mgss_dictionary = read_txt_to_array('assets/livesource/主频道/咪咕赛事.txt')
    traditional_opera_dictionary = read_txt_to_array('assets/livesource/主频道/戏曲.txt')
    spring_festival_gala_dictionary = read_txt_to_array('assets/livesource/主频道/春晚.txt')
    camera_dictionary = read_txt_to_array('assets/livesource/主频道/直播中国.txt')
    favorite_dictionary = read_txt_to_array('assets/livesource/主频道/收藏频道.txt')
    
    # 加载纠错字典
    corrections_name = load_corrections_name('assets/livesource/corrections_name.txt')
    print(f"✅ 字典加载完成: 央视 {len(yangshi_dictionary)} 条, 卫视 {len(weishi_dictionary)} 条")
    
    # 1. 处理URL源
    print("📡 步骤1: 处理URL源")
    urls = read_txt_to_array('assets/livesource/urls-daily.txt')
    print(f"📋 发现 {len(urls)} 个数据源")
    
    for url in urls:
        if url.startswith("http"):
            # 处理日期变量
            beijing_time = get_beijing_time()
            
            if "{MMdd}" in url:
                current_date_str = beijing_time.strftime("%m%d")
                url = url.replace("{MMdd}", current_date_str)
                print(f"🔄 日期替换: {current_date_str}")
            
            if "{MMdd-1}" in url:
                yesterday_date_str = (beijing_time - timedelta(days=1)).strftime("%m%d")
                url = url.replace("{MMdd-1}", yesterday_date_str)
                print(f"🔄 日期替换: {yesterday_date_str}")
            
            process_url(url)
    
    print(f"✅ URL处理完成，共处理 {len(urls)} 个数据源")
    
    # 2. 处理白名单
    print("📋 步骤2: 添加白名单...")
    whitelist_auto_lines = read_txt_to_array('assets/livesource/blacklist/whitelist_auto.txt')
    whitelist_count = 0
    whitelist_rejected_count = 0
    whitelist_error_count = 0
    
    for whitelist_line in whitelist_auto_lines:
        if "#genre#" not in whitelist_line and "," in whitelist_line and "://" in whitelist_line:
            whitelist_parts = whitelist_line.split(",")
            try:
                response_time = float(whitelist_parts[0].replace("ms", ""))
            except ValueError:
                print(f"❌ 白名单响应时间转换失败: {whitelist_line}")
                response_time = 60000
                whitelist_error_count += 1
            
            if len(whitelist_parts) >= 3:
                channel_name = whitelist_parts[1].strip()
                
                if response_time < 2000:
                    print(f"  ✅ 白名单: {channel_name} ({response_time}ms)")
                    process_channel_line(",".join(whitelist_parts[1:]))
                    whitelist_count += 1
                else:
                    print(f"  ⚠️  白名单跳过(响应慢): {channel_name} ({response_time}ms)")
                    whitelist_rejected_count += 1
            else:
                print(f"  ❌ 白名单格式错误: {whitelist_line}")
                whitelist_error_count += 1
    
    print(f"✅ 白名单处理完成: 添加 {whitelist_count} 个，跳过 {whitelist_rejected_count} 个慢速源，{whitelist_error_count} 个格式错误")
    
    # 3. 处理AKTV源
    print("📡 步骤3: 获取AKTV源...")
    aktv_url = "https://raw.githubusercontent.com/xiaoran67/update/refs/heads/main/assets/livesource/%E6%89%8B%E5%B7%A5%E5%8C%BA/channels.txt"
    
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
        process_channel_line(line)
    
    # 4. 处理手工区数据
    print("🔧 步骤4: 处理手工区数据（带去重）")

    zhejiang_manual = read_and_deduplicate_manual('assets/livesource/手工区/浙江频道.txt')
    zhejiang_lines.extend(zhejiang_manual)
    print(f"   浙江频道: 添加 {len(zhejiang_manual)} 个手工源（已去重）")

    guangdong_manual = read_and_deduplicate_manual('assets/livesource/手工区/广东频道.txt')
    guangdong_lines.extend(guangdong_manual)
    print(f"   广东频道: 添加 {len(guangdong_manual)} 个手工源（已去重）")

    hubei_manual = read_and_deduplicate_manual('assets/livesource/手工区/湖北频道.txt')
    hubei_lines.extend(hubei_manual)
    print(f"   湖北频道: 添加 {len(hubei_manual)} 个手工源（已去重）")

    shanghai_manual = read_and_deduplicate_manual('assets/livesource/手工区/上海频道.txt')
    shanghai_lines.extend(shanghai_manual)
    print(f"   上海频道: 添加 {len(shanghai_manual)} 个手工源（已去重）")

    jiangsu_manual = read_and_deduplicate_manual('assets/livesource/手工区/江苏频道.txt')
    jiangsu_lines.extend(jiangsu_manual)
    print(f"   江苏频道: 添加 {len(jiangsu_manual)} 个手工源（已去重）")

    # 5. 处理体育赛事
    print("🏆 步骤5: 处理体育赛事")
    
    # 日期格式化
    normalized_tyss_lines = [normalize_date_to_md(s) for s in tyss_lines]
    
    # 过滤关键词
    keywords_to_exclude_tiyu_txt = ["玉玉软件", "榴芒电视", "公众号", "麻豆", "「回看」"]
    keywords_to_exclude_tiyu = ["玉玉软件", "榴芒电视", "公众号", "咪视通", "麻豆", "「回看」"]
    
    # 应用过滤和排序
    normalized_tyss_lines = filter_lines(normalized_tyss_lines, keywords_to_exclude_tiyu_txt)
    normalized_tyss_lines = custom_tyss_sort(set(normalized_tyss_lines))
    filtered_tyss_lines = filter_lines(normalized_tyss_lines, keywords_to_exclude_tiyu)
    
    print(f"✅ 体育赛事处理完成: 原始 {len(tyss_lines)} 条, 过滤后 {len(filtered_tyss_lines)} 条")
    
    # 生成HTML页面
    generate_playlist_html(filtered_tyss_lines, 'output/tiyu.html')
    
    # 保存TXT文件
    with open('output/tiyu.txt', 'w', encoding='utf-8') as f:
        for line in filtered_tyss_lines:
            f.write(line + '\n')
    print("✅ 体育赛事文本已保存: output/tiyu.txt")
    
    # 6. 生成今日推荐和版本信息
    print("🕒 步骤6: 生成今日推荐和版本信息")
    
    # 获取北京时间
    beijing_time = get_beijing_time()
    formatted_time = beijing_time.strftime("%Y%m%d %H:%M:%S")
    
    # 生成今日推荐
    MTV1 = "💯推荐," + (get_random_url('assets/livesource/手工区/今日推荐.txt') or "")
    MTV2 = "🤫低调," + (get_random_url('assets/livesource/手工区/今日推荐.txt') or "")
    MTV3 = "🟢使用," + (get_random_url('assets/livesource/手工区/今日推荐.txt') or "")
    MTV4 = "⚠️禁止," + (get_random_url('assets/livesource/手工区/今日推荐.txt') or "")
    MTV5 = "🚫贩卖," + (get_random_url('assets/livesource/手工区/今日推荐.txt') or "")
    
    # 生成版本信息
    version = formatted_time + "," + (get_random_url('assets/livesource/手工区/今日推台.txt') or "")
    about = "👨潇然," + (get_random_url('assets/livesource/手工区/今日推台.txt') or "")
    
    # 7. 生成播放列表文件
    print("📄 步骤7: 生成播放列表文件")

    # 完整版播放列表（v0.02风格）
    all_lines = ["🌐央视频道,#genre#"] + sort_data(yangshi_dictionary, correct_name_data(corrections_name, yangshi_lines)) + ['\n'] + \
            ["📡卫视频道,#genre#"] + sort_data(weishi_dictionary, correct_name_data(corrections_name, weishi_lines)) + ['\n'] + \
            ["🏛️北京频道,#genre#"] + sort_data(beijing_dictionary, correct_name_data(corrections_name, beijing_lines)) + ['\n'] + \
            ["🏙️上海频道,#genre#"] + sort_data(shanghai_dictionary, correct_name_data(corrections_name, shanghai_lines)) + ['\n'] + \
            ["🐯广东频道,#genre#"] + sort_data(guangdong_dictionary, correct_name_data(corrections_name, guangdong_lines)) + ['\n'] + \
            ["🎐江苏频道,#genre#"] + sort_data(jiangsu_dictionary, correct_name_data(corrections_name, jiangsu_lines)) + ['\n'] + \
            ["🧵浙江频道,#genre#"] + sort_data(zhejiang_dictionary, correct_name_data(corrections_name, zhejiang_lines)) + ['\n'] + \
            ["⛰️山东频道,#genre#"] + sort_data(shandong_dictionary, correct_name_data(corrections_name, shandong_lines)) + ['\n'] + \
            ["🐼四川频道,#genre#"] + sort_data(sichuan_dictionary, correct_name_data(corrections_name, sichuan_lines)) + ['\n'] + \
            ["🐘河南频道,#genre#"] + sort_data(henan_dictionary, correct_name_data(corrections_name, henan_lines)) + ['\n'] + \
            ["🌶️湖南频道,#genre#"] + sort_data(hunan_dictionary, correct_name_data(corrections_name, hunan_lines)) + ['\n'] + \
            ["🏞️重庆频道,#genre#"] + sort_data(chongqing_dictionary, correct_name_data(corrections_name, chongqing_lines)) + ['\n'] + \
            ["🚢天津频道,#genre#"] + sort_data(tianjin_dictionary, correct_name_data(corrections_name, tianjin_lines)) + ['\n'] + \
            ["🏯湖北频道,#genre#"] + sort_data(hubei_dictionary, correct_name_data(corrections_name, hubei_lines)) + ['\n'] + \
            ["🌾安徽频道,#genre#"] + sort_data(anhui_dictionary, correct_name_data(corrections_name, anhui_lines)) + ['\n'] + \
            ["🌊福建频道,#genre#"] + sort_data(fujian_dictionary, correct_name_data(corrections_name, fujian_lines)) + ['\n'] + \
            ["⛰️辽宁频道,#genre#"] + sort_data(liaoning_dictionary, correct_name_data(corrections_name, liaoning_lines)) + ['\n'] + \
            ["🔥陕西频道,#genre#"] + sort_data(shaanxi_dictionary, correct_name_data(corrections_name, shaanxi_lines)) + ['\n'] + \
            ["⛩️河北频道,#genre#"] + sort_data(hebei_dictionary, correct_name_data(corrections_name, hebei_lines)) + ['\n'] + \
            ["🔥江西频道,#genre#"] + sort_data(jiangxi_dictionary, correct_name_data(corrections_name, jiangxi_lines)) + ['\n'] + \
            ["💃广西频道,#genre#"] + sort_data(guangxi_dictionary, correct_name_data(corrections_name, guangxi_lines)) + ['\n'] + \
            ["☁️云南频道,#genre#"] + sort_data(yunnan_dictionary, correct_name_data(corrections_name, yunnan_lines)) + ['\n'] + \
            ["🏮山西频道,#genre#"] + sort_data(shanxi_dictionary, correct_name_data(corrections_name, shanxi_lines)) + ['\n'] + \
            ["🐻黑·龙·江,#genre#"] + sort_data(heilongjiang_dictionary, correct_name_data(corrections_name, heilongjiang_lines)) + ['\n'] + \
            ["🎎吉林频道,#genre#"] + sort_data(jilin_dictionary, correct_name_data(corrections_name, jilin_lines)) + ['\n'] + \
            ["⛰️贵州频道,#genre#"] + sort_data(guizhou_dictionary, correct_name_data(corrections_name, guizhou_lines)) + ['\n'] + \
            ["🐫甘肃频道,#genre#"] + sort_data(gansu_dictionary, correct_name_data(corrections_name, gansu_lines)) + ['\n'] + \
            ["🐮内·蒙·古,#genre#"] + sort_data(neimenggu_dictionary, correct_name_data(corrections_name, neimenggu_lines)) + ['\n'] + \
            ["🍇新疆频道,#genre#"] + sort_data(xinjiang_dictionary, correct_name_data(corrections_name, xinjiang_lines)) + ['\n'] + \
            ["🏝️海南频道,#genre#"] + sort_data(hainan_dictionary, correct_name_data(corrections_name, hainan_lines)) + ['\n'] + \
            ["🕌宁夏频道,#genre#"] + sort_data(ningxia_dictionary, correct_name_data(corrections_name, ningxia_lines)) + ['\n'] + \
            ["🐑青海频道,#genre#"] + sort_data(qinghai_dictionary, correct_name_data(corrections_name, qinghai_lines)) + ['\n'] + \
            ["🐐西藏频道,#genre#"] + sort_data(xizang_dictionary, correct_name_data(corrections_name, xizang_lines)) + ['\n'] + \
            ["🏆️体育赛事,#genre#"] + filtered_tyss_lines + ['\n'] + \
            ["🏈咪咕赛事,#genre#"] + sorted(set(mgss_lines)) + ['\n'] + \
            ["🇭🇰香港频道,#genre#"] + sort_data(hongkong_dictionary, correct_name_data(corrections_name, hongkong_lines)) + ['\n'] + \
            ["🇲🇴澳门频道,#genre#"] + sort_data(macau_dictionary, correct_name_data(corrections_name, macau_lines)) + ['\n'] + \
            ["🇨🇳闽南频道,#genre#"] + sort_data(minnan_dictionary, correct_name_data(corrections_name, minnan_lines)) + ['\n'] + \
            ["🔢数字频道,#genre#"] + sort_data(digital_dictionary, correct_name_data(corrections_name, digital_lines)) + ['\n'] + \
            ["🎬电影频道,#genre#"] + sort_data(movie_dictionary, correct_name_data(corrections_name, movie_lines)) + ['\n'] + \
            ["📺电·视·剧,#genre#"] + sort_data(tv_drama_dictionary, correct_name_data(corrections_name, tv_drama_lines)) + ['\n'] + \
            ["🎥纪·录·片,#genre#"] + sort_data(documentary_dictionary, correct_name_data(corrections_name, documentary_lines)) + ['\n'] + \
            ["🐱动·画·片,#genre#"] + sort_data(cartoon_dictionary, correct_name_data(corrections_name, cartoon_lines)) + ['\n'] + \
            ["📻收·音·机,#genre#"] + sort_data(radio_dictionary, correct_name_data(corrections_name, radio_lines)) + ['\n'] + \
            ["🎭综艺频道,#genre#"] + sorted(set(correct_name_data(corrections_name, variety_lines))) + ['\n'] + \
            ["🐯虎牙直播,#genre#"] + sort_data(huya_dictionary, correct_name_data(corrections_name, huya_lines)) + ['\n'] + \
            ["🐠斗鱼直播,#genre#"] + sort_data(douyu_dictionary, correct_name_data(corrections_name, douyu_lines)) + ['\n'] + \
            ["🎤解说频道,#genre#"] + sorted(set(commentary_lines)) + ['\n'] + \
            ["🎵音乐频道,#genre#"] + sorted(set(music_lines)) + ['\n'] + \
            ["🍜美食频道,#genre#"] + sort_data(food_dictionary, correct_name_data(corrections_name, food_lines)) + ['\n'] + \
            ["✈️旅游频道,#genre#"] + sort_data(travel_dictionary, correct_name_data(corrections_name, travel_lines)) + ['\n'] + \
            ["🏥健康频道,#genre#"] + sort_data(health_dictionary, correct_name_data(corrections_name, health_lines)) + ['\n'] + \
            ["💰财经频道,#genre#"] + sort_data(finance_dictionary, correct_name_data(corrections_name, finance_lines)) + ['\n'] + \
            ["🛍️购物频道,#genre#"] + sort_data(shopping_dictionary, correct_name_data(corrections_name, shopping_lines)) + ['\n'] + \
            ["🎮游戏频道,#genre#"] + sorted(set(game_lines)) + ['\n'] + \
            ["📰新闻频道,#genre#"] + sort_data(news_dictionary, correct_name_data(corrections_name, news_lines)) + ['\n'] + \
            ["🇨🇳中国综合,#genre#"] + sort_data(china_dictionary, correct_name_data(corrections_name, china_lines)) + ['\n'] + \
            ["🌐国际频道,#genre#"] + sort_data(international_dictionary, correct_name_data(corrections_name, international_lines)) + ['\n'] + \
            ["⚽体育频道,#genre#"] + sort_data(sports_dictionary, correct_name_data(corrections_name, sports_lines)) + ['\n'] + \
            ["🎭戏曲频道,#genre#"] + sort_data(traditional_opera_dictionary, correct_name_data(corrections_name, traditional_opera_lines)) + ['\n'] + \
            ["🧨春晚频道,#genre#"] + sort_data(spring_festival_gala_dictionary, correct_name_data(corrections_name, spring_festival_gala_lines)) + ['\n'] + \
            ["🏞️景区直播,#genre#"] + sort_data(camera_dictionary, correct_name_data(corrections_name, camera_lines)) + ['\n'] + \
            ["⭐收藏频道,#genre#"] + sort_data(favorite_dictionary, correct_name_data(corrections_name, favorite_lines)) + ['\n'] + \
            ["📦其他频道,#genre#"] + sorted(set(other_lines)) + ['\n'] + \
            ["🕒更新时间,#genre#"] + [version] + [about] + [MTV1] + [MTV2] + [MTV3] + [MTV4] + [MTV5] + ['\n']
    
    # 精简版播放列表
    all_lines_simple = ["🌐央视频道,#genre#"] + sort_data(yangshi_dictionary, correct_name_data(corrections_name, yangshi_lines)) + ['\n'] + \
            ["📡卫视频道,#genre#"] + sort_data(weishi_dictionary, correct_name_data(corrections_name, weishi_lines)) + ['\n'] + \
            ["🕒更新时间,#genre#"] + [version] + [about] + [MTV1] + [MTV2] + [MTV3] + [MTV4] + [MTV5] + ['\n']
    
    # 定制版播放列表
    all_lines_custom = ["🌐央视频道,#genre#"] + sort_data(yangshi_dictionary, correct_name_data(corrections_name, yangshi_lines)) + ['\n'] + \
            ["📡卫视频道,#genre#"] + sort_data(weishi_dictionary, correct_name_data(corrections_name, weishi_lines)) + ['\n'] + \
            ["🏆️体育赛事,#genre#"] + filtered_tyss_lines + ['\n'] + \
            ["🏈咪咕赛事,#genre#"] + sorted(set(mgss_lines)) + ['\n'] + \
            ["🇭🇰香港频道,#genre#"] + sort_data(hongkong_dictionary, correct_name_data(corrections_name, hongkong_lines)) + ['\n'] + \
            ["🇲🇴澳门频道,#genre#"] + sort_data(macau_dictionary, correct_name_data(corrections_name, macau_lines)) + ['\n'] + \
            ["🇨🇳闽南频道,#genre#"] + sort_data(minnan_dictionary, correct_name_data(corrections_name, minnan_lines)) + ['\n'] + \
            ["🔢数字频道,#genre#"] + sort_data(digital_dictionary, correct_name_data(corrections_name, digital_lines)) + ['\n'] + \
            ["🎬电影频道,#genre#"] + sort_data(movie_dictionary, correct_name_data(corrections_name, movie_lines)) + ['\n'] + \
            ["📺电·视·剧,#genre#"] + sort_data(tv_drama_dictionary, correct_name_data(corrections_name, tv_drama_lines)) + ['\n'] + \
            ["🎥纪·录·片,#genre#"] + sort_data(documentary_dictionary, correct_name_data(corrections_name, documentary_lines)) + ['\n'] + \
            ["🐱动·画·片,#genre#"] + sort_data(cartoon_dictionary, correct_name_data(corrections_name, cartoon_lines)) + ['\n'] + \
            ["📻收·音·机,#genre#"] + sort_data(radio_dictionary, correct_name_data(corrections_name, radio_lines)) + ['\n'] + \
            ["🎭综艺频道,#genre#"] + sorted(set(correct_name_data(corrections_name, variety_lines))) + ['\n'] + \
            ["🐯虎牙直播,#genre#"] + sort_data(huya_dictionary, correct_name_data(corrections_name, huya_lines)) + ['\n'] + \
            ["🐠斗鱼直播,#genre#"] + sort_data(douyu_dictionary, correct_name_data(corrections_name, douyu_lines)) + ['\n'] + \
            ["🎤解说频道,#genre#"] + sorted(set(commentary_lines)) + ['\n'] + \
            ["🎵音乐频道,#genre#"] + sorted(set(music_lines)) + ['\n'] + \
            ["🍜美食频道,#genre#"] + sort_data(food_dictionary, correct_name_data(corrections_name, food_lines)) + ['\n'] + \
            ["✈️旅游频道,#genre#"] + sort_data(travel_dictionary, correct_name_data(corrections_name, travel_lines)) + ['\n'] + \
            ["🏥健康频道,#genre#"] + sort_data(health_dictionary, correct_name_data(corrections_name, health_lines)) + ['\n'] + \
            ["💰财经频道,#genre#"] + sort_data(finance_dictionary, correct_name_data(corrections_name, finance_lines)) + ['\n'] + \
            ["🛍️购物频道,#genre#"] + sort_data(shopping_dictionary, correct_name_data(corrections_name, shopping_lines)) + ['\n'] + \
            ["🎮游戏频道,#genre#"] + sorted(set(game_lines)) + ['\n'] + \
            ["📰新闻频道,#genre#"] + sort_data(news_dictionary, correct_name_data(corrections_name, news_lines)) + ['\n'] + \
            ["🇨🇳中国综合,#genre#"] + sort_data(china_dictionary, correct_name_data(corrections_name, china_lines)) + ['\n'] + \
            ["🌐国际频道,#genre#"] + sort_data(international_dictionary, correct_name_data(corrections_name, international_lines)) + ['\n'] + \
            ["🎭戏曲频道,#genre#"] + sort_data(traditional_opera_dictionary, correct_name_data(corrections_name, traditional_opera_lines)) + ['\n'] + \
            ["🧨春晚频道,#genre#"] + sort_data(spring_festival_gala_dictionary, correct_name_data(corrections_name, spring_festival_gala_lines)) + ['\n'] + \
            ["🏞️景区直播,#genre#"] + sort_data(camera_dictionary, correct_name_data(corrections_name, camera_lines)) + ['\n'] + \
            ["⭐收藏频道,#genre#"] + sort_data(favorite_dictionary, correct_name_data(corrections_name, favorite_lines)) + ['\n'] + \
            ["📦其他频道,#genre#"] + sorted(set(other_lines)) + ['\n'] + \
            ["🕒更新时间,#genre#"] + [version] + [about] + [MTV1] + [MTV2] + [MTV3] + [MTV4] + [MTV5] + ['\n']
    
    # 文件路径定义
    output_full = "output/full.txt"
    output_lite = "output/lite.txt"
    output_custom = "output/custom.txt"
    output_others = "output/others.txt"
    
    try:
        # 写入完整版
        with open(output_full, 'w', encoding='utf-8') as f:
            for line in all_lines:
                f.write(line + '\n')
        print(f"✅ 完整版播放列表已保存: {output_full}")
        
        # 写入精简版
        with open(output_lite, 'w', encoding='utf-8') as f:
            for line in all_lines_simple:
                f.write(line + '\n')
        print(f"✅ 精简版播放列表已保存: {output_lite}")
        
        # 写入定制版
        with open(output_custom, 'w', encoding='utf-8') as f:
            for line in all_lines_custom:
                f.write(line + '\n')
        print(f"✅ 定制版播放列表已保存: {output_custom}")
        
        # 写入未分类源
        with open(output_others, 'w', encoding='utf-8') as f:
            for line in other_lines:
                f.write(line + '\n')
        print(f"✅ 未分类频道列表已保存: {output_others}")
        
    except Exception as e:
        print(f"❌ 保存文件时发生错误: {e}")
    
    # 8. 生成M3U格式文件
    print("🔄 步骤8: 生成M3U格式文件")
    make_m3u(output_full, output_full.replace(".txt", ".m3u"))
    print(f"✅ 完整版M3U已生成: {output_full.replace('.txt', '.m3u')}")
    
    make_m3u(output_lite, output_lite.replace(".txt", ".m3u"))
    print(f"✅ 精简版M3U已生成: {output_lite.replace('.txt', '.m3u')}")
    
    make_m3u(output_custom, output_custom.replace(".txt", ".m3u"))
    print(f"✅ 定制版M3U已生成: {output_custom.replace('.txt', '.m3u')}")
    
    # 9. 统计信息
    print("📊 步骤9: 生成统计信息")
    
    # 执行结束时间
    timeend = get_beijing_time()
    
    # 计算时间差
    elapsed_time = timeend - timestart
    total_seconds = elapsed_time.total_seconds()
    
    # 转换为分钟和秒
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    
    timestart_str = timestart.strftime("%Y%m%d %H:%M:%S")
    timeend_str = timeend.strftime("%Y%m%d %H:%M:%S")
    
    print(f"开始时间: {timestart_str}")
    print(f"结束时间: {timeend_str}")
    print(f"执行时间: {minutes} 分 {seconds} 秒")
    
    # 计算去重率
    processed_urls_count = len(processed_urls)
    blacklist_urls_count = len(combined_blacklist)
    total_processed_urls = processed_urls_count + blacklist_urls_count
    
    print(f"📊 去重统计信息:")
    print(f"   处理的唯一URL数: {processed_urls_count}")
    print(f"   黑名单URL数: {blacklist_urls_count}")
    print(f"   总处理URL数: {total_processed_urls}")
    if total_processed_urls > 0:
        duplication_rate = (1 - processed_urls_count / total_processed_urls) * 100
        print(f"   🔄 去重率: {duplication_rate:.1f}%")
    else:
        print(f"   🔄 去重率: N/A")
    
    print(f"📋 其他统计:")
    print(f"   黑名单行数: {len(combined_blacklist)}")
    print(f"   完整版行数: {len(all_lines)}")
    print(f"   其他源行数: {len(other_lines)}")
    
    # 生成统计信息JSON
    stats_output = {
        "metadata": {
            "version": "v0.03",
            "start_time": timestart_str,
            "end_time": timeend_str,
            "duration_seconds": total_seconds,
            "duration_formatted": f"{minutes}分{seconds}秒",
        },
        "statistics": {
            "processed_urls": processed_urls_count,
            "blacklist_urls": blacklist_urls_count,
            "total_processed_urls": total_processed_urls,
            "duplicate_rate": (1 - processed_urls_count / total_processed_urls) * 100 if total_processed_urls > 0 else 0,
            "total_lines": len(all_lines),
            "other_lines": len(other_lines),
        },
        "category_counts": {
            "央视": len(yangshi_lines),
            "卫视": len(weishi_lines),
            "体育赛事": len(filtered_tyss_lines),
            "其他": len(other_lines),
        }
    }
    
    try:
        with open('output/statistics.json', 'w', encoding='utf-8') as f:
            json.dump(stats_output, f, ensure_ascii=False, indent=2)
        print("✅ 统计信息已保存到: output/statistics.json")
    except Exception as e:
        print(f"❌ 保存统计信息错误: {e}")
    
    print("=" * 60)
    print("🎉 IPTV直播源处理完成！")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断程序")
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")

"""
IPTV直播源聚合处理工具 v2.00
基于v1.00版本的优化重构版

主要优化和整合了v1.00的以下特点：
1. ✅ 北京时间函数：get_beijing_time()
2. ✅ 全局URL去重集合：processed_urls
3. ✅ 提前URL清理和黑名单检查
4. ✅ 增强的打印输出和错误处理（带图标）
5. ✅ 频道名称纠错增强
6. ✅ 体育赛事日期格式化
7. ✅ 白名单处理增强（详细统计）
8. ✅ 保持v1.00的所有分类功能和变量命名
9. ✅ 函数式编程架构（与v0.01保持兼容）
10. ✅ 详细统计信息（v1.00风格）
11. ✅ 与v0.01/v1.00字典文件完全兼容

新增优化：
1. 🔧 手工区源内部去重功能
2. 📊 生成详细的JSON格式统计文件
3. 🎯 更清晰的函数模块化设计
4. 🛡️ 更完善的异常处理机制
5. 📝 更规范的代码注释

输出文件：
output/
  ├── full.txt         完整播放列表
  ├── full.m3u        M3U格式完整版
  ├── lite.txt        精简版（央视+卫视）
  ├── lite.m3u       M3U格式精简版
  ├── custom.txt      定制版（不含地方台）
  ├── custom.m3u     M3U格式定制版
  ├── others.txt      未分类频道
  ├── tiyu.html       体育赛事网页
  ├── tiyu.txt        体育赛事文本
  └── statistics.json  统计信息（新增）

项目目录结构：
项目目录/
├── assets/
│   └── livesource/
│       ├── 主频道/          # 核心频道分类字典
│       ├── 地方台/          # 省级地方台字典
│       ├── 手工区/          # 高质量手工源
│       ├── blacklist/       # 黑白名单管理
│       └── livesource.py        # 主程序2.00
│       └── corrections_name.txt  # 频道名称纠错
│    
└── output/                # 输出目录（自动创建）

使用说明：
1. 配置数据源：在 assets/livesource/urls-daily.txt 中添加直播源URL
2. 运行程序：python main.py
3. 查看结果：在 output/ 目录下获取生成的播放列表
4. 体育赛事：通过 tiyu.html 网页查看最新赛事直播

版本历史：
v0.00 (2025-01-01):
  - 基础版本完成，实现完整的直播源聚合处理流程

v1.00 (2025-01-01):
  - 全局URL去重机制，性能大幅提升
  - 北京时间标准化
  - 增强的错误处理和日志输出

v2.00 (2025-02-02):
  - 代码重构和模块化优化
  - 手工区源内部去重功能
  - 生成详细的JSON统计信息
  - 更完善的异常处理机制

性能对比：
v0.00: 基础版本，功能完整但性能较低
v1.00: 性能优化版，去重效率提升10倍
v2.00: 架构优化版，代码更健壮，功能更完善（当前版本）

作者：潇然
版本：v2.00
日期：2025年2月2日
"""

# === LiveSource-Collector ====
# ====== 版本v2.00 =========
# ====== 架构优化版 ========
