"""
直播源聚合处理脚本-克隆B版逻辑
功能：从多个来源获取直播源，进行分类、过滤、格式转换，生成播放列表
作者：基于A版逻辑克隆
版本：2025
"""

import urllib.request
from urllib.parse import urlparse
import re
import os
from datetime import datetime, timedelta, timezone
import random
import opencc
import socket
import time

# ======= 工具函数模块 =======

def traditional_to_simplified(text: str) -> str:
    """繁体转简体"""
    converter = opencc.OpenCC('t2s')
    return converter.convert(text)

def read_txt_to_array(file_name):
    """读取文本文件到数组，跳过空行"""
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            return [line.strip() for line in lines if line.strip()]
    except FileNotFoundError:
        print(f"File '{file_name}' not found.")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def read_blacklist_from_txt(file_path):
    """从黑名单文件读取URL列表"""
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    return [line.split(',')[1].strip() for line in lines if ',' in line]

# ======= 配置和初始化 =======

timestart = datetime.now()
print(f"开始时间: {datetime.now().strftime('%Y%m%d_%H_%M_%S')}")

# 读取黑名单
blacklist_auto = read_blacklist_from_txt('scripts/livesource0/blacklist/blacklist_auto.txt')
blacklist_manual = read_blacklist_from_txt('scripts/livesource0/blacklist/blacklist_manual.txt')
combined_blacklist = set(blacklist_auto + blacklist_manual)

# ======= 频道分类存储对象 =======

# 定义各分类频道的存储列表
yangshi_lines = []      # 央视
weishi_lines = []       # 卫视
beijing_lines = []      # 北京
shanghai_lines = []     # 上海
tianjin_lines = []      # 天津
chongqing_lines = []    # 重庆
guangdong_lines = []    # 广东
jiangsu_lines = []      # 江苏
zhejiang_lines = []     # 浙江
shandong_lines = []     # 山东
henan_lines = []        # 河南
sichuan_lines = []      # 四川
hebei_lines = []        # 河北
hunan_lines = []        # 湖南
hubei_lines = []        # 湖北
anhui_lines = []        # 安徽
fujian_lines = []       # 福建
shanxi1_lines = []      # 陕西
liaoning_lines = []     # 辽宁
jiangxi_lines = []      # 江西
heilongjiang_lines = [] # 黑龙江
jilin_lines = []        # 吉林
shanxi2_lines = []      # 山西
guangxi_lines = []      # 广西
yunnan_lines = []       # 云南
guizhou_lines = []      # 贵州
gansu_lines = []        # 甘肃
neimenggu_lines = []    # 内蒙古
xinjiang_lines = []     # 新疆
hainan_lines = []       # 海南
ningxia_lines = []      # 宁夏
qinghai_lines = []      # 青海
xizang_lines = []       # 西藏

news_lines = []         # 新闻
shuzi_lines = []        # 数字
dianying_lines = []     # 电影
jieshuo_lines = []      # 解说
zongyi_lines = []       # 综艺
huya_lines = []         # 虎牙
douyu_lines = []        # 斗鱼
xianggang_lines = []    # 香港
aomen_lines = []        # 澳门
china_lines = []        # 中国
guoji_lines = []        # 国际
gangaotai_lines = []    # 港澳台
dianshiju_lines = []    # 电视剧
radio_lines = []        # 收音机
donghuapian_lines = []  # 动画片
jilupian_lines = []       # 纪录片
tiyu_lines = []         # 体育
youxi_lines = []        # 游戏
xiqu_lines = []         # 戏曲
yinyue_lines = []       # 音乐
chunwan_lines = []      # 春晚
tyss_lines = []          # 体育赛事
mgss_lines = []         # 咪咕赛事
zhibozhongguo_lines = [] # 直播中国

other_lines = []        # 其他
other_lines_url = []    # 其他频道URL（用于去重）

# ======= 频道名称处理函数 =======

def process_name_string(input_str):
    """处理频道名称字符串"""
    parts = input_str.split(',')
    processed_parts = []
    for part in parts:
        processed_part = process_part(part)
        processed_parts.append(processed_part)
    result_str = ','.join(processed_parts)
    return result_str

def process_part(part_str):
    """处理单个频道名称部分"""
    # 处理CCTV频道名称
    if "CCTV" in part_str and "://" not in part_str:
        part_str = part_str.replace("IPV6", "").replace("PLUS", "+").replace("1080", "")
        filtered_str = ''.join(char for char in part_str if char.isdigit() or char == 'K' or char == '+')
        
        # 处理特殊情况：没有找到频道数字
        if not filtered_str.strip():
            filtered_str = part_str.replace("CCTV", "")

        # 处理4K/8K特殊格式
        if len(filtered_str) > 2 and re.search(r'4K|8K', filtered_str):
            filtered_str = re.sub(r'(4K|8K).*', r'\1', filtered_str)
            if len(filtered_str) > 2: 
                filtered_str = re.sub(r'(4K|8K)', r'(\1)', filtered_str)

        return "CCTV" + filtered_str 
        
    elif "卫视" in part_str:
        # 清理卫视频道名称中的附加信息
        pattern = r'卫视「.*」'
        result_str = re.sub(pattern, '卫视', part_str)
        return result_str
    
    return part_str

# ======= 文件格式处理 =======

def get_url_file_extension(url):
    """获取URL文件扩展名"""
    parsed_url = urlparse(url)
    path = parsed_url.path
    extension = os.path.splitext(path)[1]
    return extension

def convert_m3u_to_txt(m3u_content):
    """将M3U格式转换为TXT格式"""
    lines = m3u_content.split('\n')
    txt_lines = []
    channel_name = ""
    
    for line in lines:
        # 过滤M3U头信息
        if line.startswith("#EXTM3U"):
            continue
        # 处理频道信息行
        if line.startswith("#EXTINF"):
            channel_name = line.split(',')[-1].strip()
        # 处理URL行
        elif line.startswith("http") or line.startswith("rtmp") or line.startswith("p3p"):
            txt_lines.append(f"{channel_name},{line.strip()}")
        
        # 处理格式为txt但后缀为m3u的文件
        if "#genre#" not in line and "," in line and "://" in line:
            pattern = r'^[^,]+,[^\s]+://[^\s]+$'
            if bool(re.match(pattern, line)):
                txt_lines.append(line)
    
    return '\n'.join(txt_lines)

# ======= URL处理和验证 =======

def check_url_existence(data_list, url):
    """检查URL是否在列表中已存在"""
    urls = [item.split(',')[1] for item in data_list]
    return url not in urls  # 如果不存在返回True

def clean_url(url):
    """清理URL，移除$符号后的内容"""
    last_dollar_index = url.rfind('$')
    if last_dollar_index != -1:
        return url[:last_dollar_index]
    return url

# ======= 频道名称清理 =======

# 需要从频道名称中移除的字符列表
removal_list = ["_电信", "电信", "高清", "频道", "（HD）", "-HD", "英陆", "_ITV", "(北美)", "(HK)", "AKtv", "「IPV4」", "「IPV6」", "[HD]", "[BD]", "[SD]", "[VGA]",
                "频陆", "备陆", "壹陆", "贰陆", "叁陆", "肆陆", "伍陆", "陆陆", "柒陆", "频晴", "频粤", "[超清]", "高清", "超清", "标清", "斯特",
                "粤陆", "国陆", "肆柒", "频英", "频特", "频国", "频壹", "频贰", "肆贰", "频测", "咪咕", "闽特", "高特", "频高", "频标", "汝阳",
                "4Gtv", "频效", "国标", "粤标", "频推", "频流", "粤高", "频限", "实时", "美推", "频美"]

def clean_channel_name(channel_name, removal_list):
    """清理频道名称中的特定字符"""
    for item in removal_list:
        channel_name = channel_name.replace(item, "")

    # 移除末尾的'HD'和'台'
    if channel_name.endswith("HD"):
        channel_name = channel_name[:-2]
    if channel_name.endswith("台") and len(channel_name) > 3:
        channel_name = channel_name[:-1]

    return channel_name

# ======= 核心分发逻辑 =======

def process_channel_line(line):
    """处理单行频道数据并进行分类"""
    # 检查行格式是否符合要求
    if "#genre#" not in line and "#EXTINF:" not in line and "," in line and "://" in line:
        channel_name = line.split(',')[0].strip()
        channel_name = clean_channel_name(channel_name, removal_list)  # 清理名称
        channel_name = traditional_to_simplified(channel_name)  # 繁转简
        channel_address = clean_url(line.split(',')[1].strip())  # 清理URL
        line = channel_name + "," + channel_address  # 重新组织行
        
        # 检查是否在黑名单中
        if channel_address not in combined_blacklist:
            # 根据频道名称进行分类分发
            #if "CCTV" in channel_name and check_url_existence(yangshi_lines, channel_address):  # 注释这一行用下面替换
            if any(cctv_name in channel_name for cctv_name in yangshi_dictionary) and check_url_existence(yangshi_lines, channel_address):
                yangshi_lines.append(process_name_string(line.strip()))
            elif channel_name in weishi_dictionary and check_url_existence(weishi_lines, channel_address):
                weishi_lines.append(process_name_string(line.strip()))

            # 地方台分发逻辑
            elif channel_name in beijing_dictionary and check_url_existence(beijing_lines, channel_address):
                beijing_lines.append(process_name_string(line.strip()))
            elif channel_name in shanghai_dictionary and check_url_existence(shanghai_lines, channel_address):
                shanghai_lines.append(process_name_string(line.strip()))
            elif channel_name in tianjin_dictionary and check_url_existence(tianjin_lines, channel_address):
                tianjin_lines.append(process_name_string(line.strip()))
            elif channel_name in chongqing_dictionary and check_url_existence(chongqing_lines, channel_address):
                chongqing_lines.append(process_name_string(line.strip()))
            elif channel_name in guangdong_dictionary and check_url_existence(guangdong_lines, channel_address):
                guangdong_lines.append(process_name_string(line.strip()))
            elif channel_name in jiangsu_dictionary and check_url_existence(jiangsu_lines, channel_address):
                jiangsu_lines.append(process_name_string(line.strip()))
            elif channel_name in zhejiang_dictionary and check_url_existence(zhejiang_lines, channel_address):
                zhejiang_lines.append(process_name_string(line.strip()))
            elif channel_name in shandong_dictionary and check_url_existence(shandong_lines, channel_address):
                shandong_lines.append(process_name_string(line.strip()))
            elif channel_name in henan_dictionary and check_url_existence(henan_lines, channel_address):
                henan_lines.append(process_name_string(line.strip()))
            elif channel_name in sichuan_dictionary and check_url_existence(sichuan_lines, channel_address):
                sichuan_lines.append(process_name_string(line.strip()))
            elif channel_name in hebei_dictionary and check_url_existence(hebei_lines, channel_address):
                hebei_lines.append(process_name_string(line.strip()))
            elif channel_name in hunan_dictionary and check_url_existence(hunan_lines, channel_address):
                hunan_lines.append(process_name_string(line.strip()))
            elif channel_name in hubei_dictionary and check_url_existence(hubei_lines, channel_address):
                hubei_lines.append(process_name_string(line.strip()))
            elif channel_name in anhui_dictionary and check_url_existence(anhui_lines, channel_address):
                anhui_lines.append(process_name_string(line.strip()))
            elif channel_name in fujian_dictionary and check_url_existence(fujian_lines, channel_address):
                fujian_lines.append(process_name_string(line.strip()))
            elif channel_name in shanxi1_dictionary and check_url_existence(shanxi1_lines, channel_address):
                shanxi1_lines.append(process_name_string(line.strip()))
            elif channel_name in liaoning_dictionary and check_url_existence(liaoning_lines, channel_address):
                liaoning_lines.append(process_name_string(line.strip()))
            elif channel_name in jiangxi_dictionary and check_url_existence(jiangxi_lines, channel_address):
                jiangxi_lines.append(process_name_string(line.strip()))
            elif channel_name in heilongjiang_dictionary and check_url_existence(heilongjiang_lines, channel_address):
                heilongjiang_lines.append(process_name_string(line.strip()))
            elif channel_name in jilin_dictionary and check_url_existence(jilin_lines, channel_address):
                jilin_lines.append(process_name_string(line.strip()))
            elif channel_name in shanxi2_dictionary and check_url_existence(shanxi2_lines, channel_address):
                shanxi2_lines.append(process_name_string(line.strip()))
            elif channel_name in guangxi_dictionary and check_url_existence(guangxi_lines, channel_address):
                guangxi_lines.append(process_name_string(line.strip()))
            elif channel_name in yunnan_dictionary and check_url_existence(yunnan_lines, channel_address):
                yunnan_lines.append(process_name_string(line.strip()))
            elif channel_name in guizhou_dictionary and check_url_existence(guizhou_lines, channel_address):
                guizhou_lines.append(process_name_string(line.strip()))
            elif channel_name in gansu_dictionary and check_url_existence(gansu_lines, channel_address):
                gansu_lines.append(process_name_string(line.strip()))
            elif channel_name in neimenggu_dictionary and check_url_existence(neimenggu_lines, channel_address):
                neimenggu_lines.append(process_name_string(line.strip()))
            elif channel_name in xinjiang_dictionary and check_url_existence(xinjiang_lines, channel_address):
                xinjiang_lines.append(process_name_string(line.strip()))
            elif channel_name in hainan_dictionary and check_url_existence(hainan_lines, channel_address):
                hainan_lines.append(process_name_string(line.strip()))
            elif channel_name in ningxia_dictionary and check_url_existence(ningxia_lines, channel_address):
                ningxia_lines.append(process_name_string(line.strip()))
            elif channel_name in qinghai_dictionary and check_url_existence(qinghai_lines, channel_address):
                qinghai_lines.append(process_name_string(line.strip()))
            elif channel_name in xizang_dictionary and check_url_existence(xizang_lines, channel_address):
                xizang_lines.append(process_name_string(line.strip()))

            # 主频道分发逻辑
            elif channel_name in news_dictionary and check_url_existence(news_lines, channel_address):
                news_lines.append(process_name_string(line.strip()))
            elif channel_name in shuzi_dictionary and check_url_existence(shuzi_lines, channel_address):
                shuzi_lines.append(process_name_string(line.strip()))
            elif channel_name in dianying_dictionary and check_url_existence(dianying_lines, channel_address):
                dianying_lines.append(process_name_string(line.strip()))
            elif channel_name in jieshuo_dictionary and check_url_existence(jieshuo_lines, channel_address):
                jieshuo_lines.append(process_name_string(line.strip()))
            elif channel_name in zongyi_dictionary and check_url_existence(zongyi_lines, channel_address):
                zongyi_lines.append(process_name_string(line.strip()))
            elif channel_name in huya_dictionary and check_url_existence(huya_lines, channel_address):
                huya_lines.append(process_name_string(line.strip()))
            elif channel_name in douyu_dictionary and check_url_existence(douyu_lines, channel_address):
                douyu_lines.append(process_name_string(line.strip()))
            elif channel_name in xianggang_dictionary and check_url_existence(xianggang_lines, channel_address):
                xianggang_lines.append(process_name_string(line.strip()))
            elif channel_name in aomen_dictionary and check_url_existence(aomen_lines, channel_address):
                aomen_lines.append(process_name_string(line.strip()))
            elif channel_name in china_dictionary and check_url_existence(china_lines, channel_address):
                china_lines.append(process_name_string(line.strip()))
            elif channel_name in guoji_dictionary and check_url_existence(guoji_lines, channel_address):
                guoji_lines.append(process_name_string(line.strip()))
            elif channel_name in gangaotai_dictionary and check_url_existence(gangaotai_lines, channel_address):
                gangaotai_lines.append(process_name_string(line.strip()))
            elif channel_name in dianshiju_dictionary and check_url_existence(dianshiju_lines, channel_address):
                dianshiju_lines.append(process_name_string(line.strip()))
            elif channel_name in radio_dictionary and check_url_existence(radio_lines, channel_address):
                radio_lines.append(process_name_string(line.strip()))
            elif channel_name in donghuapian_dictionary and check_url_existence(donghuapian_lines, channel_address):
                donghuapian_lines.append(process_name_string(line.strip()))
            elif channel_name in jilupian_dictionary and check_url_existence(jilupian_lines, channel_address):
                jilupian_lines.append(process_name_string(line.strip()))
            elif channel_name in tiyu_dictionary and check_url_existence(tiyu_lines, channel_address):
                tiyu_lines.append(process_name_string(line.strip()))
            elif channel_name in youxi_dictionary and check_url_existence(youxi_lines, channel_address):
                youxi_lines.append(process_name_string(line.strip()))
            elif channel_name in xiqu_dictionary and check_url_existence(xiqu_lines, channel_address):
                xiqu_lines.append(process_name_string(line.strip()))
            elif channel_name in yinyue_dictionary and check_url_existence(yinyue_lines, channel_address):
                yinyue_lines.append(process_name_string(line.strip()))
            elif channel_name in chunwan_dictionary and check_url_existence(chunwan_lines, channel_address):
                chunwan_lines.append(process_name_string(line.strip()))
            elif any(tyss_dictionary in channel_name for tyss_dictionary in tyss_dictionary) and check_url_existence(tyss_lines, channel_address):  #体育赛事（2025新增）
                tyss_lines.append(process_name_string(line.strip()))
            elif any(mgss_dictionary in channel_name for mgss_dictionary in mgss_dictionary) and check_url_existence(mgss_lines, channel_address):  #咪咕赛事（2025新增）
                mgss_lines.append(process_name_string(line.strip()))
            elif channel_name in zhibozhongguo_dictionary and check_url_existence(zhibozhongguo_lines, channel_address):
                zhibozhongguo_lines.append(process_name_string(line.strip()))
            else:
                # 未分类的频道放入其他
                if channel_address not in other_lines_url:
                    other_lines_url.append(channel_address)
                    other_lines.append(line.strip())

# ======= 网络请求相关 =======

def get_random_user_agent():
    """获取随机User-Agent"""
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    ]
    return random.choice(USER_AGENTS)

def get_http_response(url, timeout=8, retries=2, backoff_factor=1.0):
    """带重试机制的HTTP请求"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                data = response.read()
                return data.decode('utf-8')
        except urllib.error.HTTPError as e:
            print(f"[HTTPError] Code: {e.code}, URL: {url}")
            break  # HTTP错误不会在重试中恢复
        except urllib.error.URLError as e:
            print(f"[URLError] Reason: {e.reason}, Attempt: {attempt + 1}")
        except socket.timeout:
            print(f"[Timeout] URL: {url}, Attempt: {attempt + 1}")
        except Exception as e:
            print(f"[Exception] {type(e).__name__}: {e}, Attempt: {attempt + 1}")
        
        # 等待一段时间后重试
        if attempt < retries - 1:
            time.sleep(backoff_factor * (2 ** attempt))
    
    return None  # 所有尝试失败后返回None

def process_url(url):
    """处理单个URL源"""
    try:
        other_lines.append("◆◆◆　" + url)  # 在other中标记处理的URL
        
        # 创建请求对象
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')

        # 打开URL并读取内容
        with urllib.request.urlopen(req) as response:
            data = response.read()
            text = data.decode('utf-8')
            text = text.strip()

            # 处理M3U格式
            is_m3u = text.startswith("#EXTM3U") or text.startswith("#EXTINF")
            if get_url_file_extension(url) == ".m3u" or get_url_file_extension(url) == ".m3u8" or is_m3u:
                text = convert_m3u_to_txt(text)

            # 逐行处理内容
            lines = text.split('\n')
            print(f"行数: {len(lines)}")
            for line in lines:
                # 过滤无效行：不包含分类标记，包含逗号和协议，排除tvbus和组播
                if "#genre#" not in line and "," in line and "://" in line and "tvbus://" not in line and "/udp/" not in line:
                    # 拆分成频道名和URL部分
                    channel_name, channel_address = line.split(',', 1)
                    # 处理加速源（包含#号的多个URL）
                    if "#" not in channel_address:
                        process_channel_line(line)  # 普通源直接处理
                    else: 
                        # 加速源按#分隔后分别处理
                        url_list = channel_address.split('#')
                        for channel_url in url_list:
                            newline = f'{channel_name},{channel_url}'
                            process_channel_line(newline)

            other_lines.append('\n')  # URL处理完成分隔符

    except Exception as e:
        print(f"处理URL时发生错误：{e}")

# ======= 数据校正和排序 =======

def load_corrections_name(filename):
    """加载频道名称校正字典"""
    corrections = {}
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():  # 跳过空行
                continue
            parts = line.strip().split(',')
            correct_name = parts[0]
            for name in parts[1:]:
                corrections[name] = correct_name
    return corrections

def correct_name_data(corrections, data):
    """校正频道名称数据"""
    corrected_data = []
    for line in data:
        line = line.strip()
        if ',' not in line:
            continue  # 行格式错误：跳过
        name, url = line.split(',', 1)
        # 如果名称需要校正且不等于正确名称
        if name in corrections and name != corrections[name]:
            name = corrections[name]
        corrected_data.append(f"{name},{url}")
    return corrected_data

def sort_data(order, data):
    """按照指定顺序排序数据"""
    # 创建顺序字典
    order_dict = {name: i for i, name in enumerate(order)}
    
    # 定义排序键函数
    def sort_key(line):
        name = line.split(',')[0]
        return order_dict.get(name, len(order))  # 不在字典中的排在最后
    
    # 按照顺序对数据进行排序
    sorted_data = sorted(data, key=sort_key)
    return sorted_data

# ======= 体育赛事专用函数 =======

def normalize_date_to_md(text):
    """将日期统一格式化为MM-DD格式"""
    text = text.strip()

    def format_md(m):
        """格式化日期匹配组"""
        month = int(m.group(1))
        day = int(m.group(2))
        after = m.group(3) or ''
        # 确保后面有空格分隔
        if not after.startswith(' '):
            after = ' ' + after
        return f"{month:02d}-{day:02d}{after}"

    # 处理各种日期格式
    text = re.sub(r'^0?(\d{1,2})/0?(\d{1,2})(.*)', format_md, text)  # MM/DD格式
    text = re.sub(r'^\d{4}-0?(\d{1,2})-0?(\d{1,2})(.*)', format_md, text)  # YYYY-MM-DD格式
    text = re.sub(r'^0?(\d{1,2})月0?(\d{1,2})日(.*)', format_md, text)  # 中文日期格式

    return text

def filter_lines(lines, exclude_keywords):
    """
    过滤掉包含任一关键字的行
    :param lines: 原始字符串数组
    :param exclude_keywords: 需要剔除的关键词列表
    :return: 过滤后的新列表
    """
    return [line for line in lines if not any(keyword in line for keyword in exclude_keywords)]

def generate_playlist_html(data_list, output_file='playlist.html'):
    """生成体育赛事HTML页面"""
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
    print(f"✅ 网页已生成：{output_file}")

def custom_tyss_sort(lines):
    """体育赛事专用排序：数字开头倒序，其他升序"""
    digit_prefix = []
    others = []

    for line in lines:
        # 拆分出名称部分用于判断是否以数字开头
        name_part = line.split(',')[0].strip()
        if name_part and name_part[0].isdigit():
            digit_prefix.append(line)
        else:
            others.append(line)

    # 分别排序：数字开头倒序，其他升序
    digit_prefix_sorted = sorted(digit_prefix, reverse=True)
    others_sorted = sorted(others)

    return digit_prefix_sorted + others_sorted

def get_random_url(file_path):
    """从文件中随机获取一个URL"""
    urls = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # 查找逗号后面的部分，即URL
            url = line.strip().split(',')[-1]
            urls.append(url)    
    # 随机返回一个URL
    return random.choice(urls) if urls else None

# ======= M3U文件生成 =======

def get_logo_by_channel_name(channel_name):
    """根据频道名称获取logo URL"""
    for line in channels_logos:
        if not line.strip():
            continue
        name, url = line.split(',')
        if name == channel_name:
            return url
    return None

def make_m3u(txt_file, m3u_file):
    """将TXT文件转换为M3U格式"""
    try:
        output_text = '#EXTM3U x-tvg-url="https://live.fanmingming.cn/e.xml"\n'

        with open(txt_file, "r", encoding='utf-8') as file:
            input_text = file.read()

        lines = input_text.strip().split("\n")
        group_name = ""
        for line in lines:
            parts = line.split(",")
            if len(parts) == 2 and "#genre#" in line:
                group_name = parts[0]  # 更新分组名称
            elif len(parts) == 2:
                channel_name = parts[0]
                channel_url = parts[1]
                logo_url = get_logo_by_channel_name(channel_name)
                if logo_url is None:  # 未找到logo
                    output_text += f"#EXTINF:-1 group-title=\"{group_name}\",{channel_name}\n"
                    output_text += f"{channel_url}\n"
                else:
                    output_text += f"#EXTINF:-1  tvg-name=\"{channel_name}\" tvg-logo=\"{logo_url}\"  group-title=\"{group_name}\",{channel_name}\n"
                    output_text += f"{channel_url}\n"

        with open(f"{m3u_file}", "w", encoding='utf-8') as file:
            file.write(output_text)

        print(f"M3U文件 '{m3u_file}' 生成成功。")
    except Exception as e:
        print(f"发生错误: {e}")

# ======= 主执行流程 =======

# 获取当前工作目录
current_directory = os.getcwd()

# 确保输出目录存在
output_dir = 'output'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"创建输出目录: {output_dir}")

# 1. 初始化字典数据
print("初始化频道字典...")
yangshi_dictionary = read_txt_to_array('scripts/livesource0/主频道/CCTV.txt')
weishi_dictionary = read_txt_to_array('scripts/livesource0/主频道/卫视.txt')

beijing_dictionary = read_txt_to_array('scripts/livesource0/地方台/北京.txt')
shanghai_dictionary = read_txt_to_array('scripts/livesource0/地方台/上海.txt')
tianjin_dictionary = read_txt_to_array('scripts/livesource0/地方台/天津.txt')
chongqing_dictionary = read_txt_to_array('scripts/livesource0/地方台/重庆.txt')
guangdong_dictionary = read_txt_to_array('scripts/livesource0/地方台/广东.txt')
jiangsu_dictionary = read_txt_to_array('scripts/livesource0/地方台/江苏.txt')
zhejiang_dictionary = read_txt_to_array('scripts/livesource0/地方台/浙江.txt')
shandong_dictionary = read_txt_to_array('scripts/livesource0/地方台/山东.txt')
henan_dictionary = read_txt_to_array('scripts/livesource0/地方台/河南.txt')
sichuan_dictionary = read_txt_to_array('scripts/livesource0/地方台/四川.txt')
hebei_dictionary = read_txt_to_array('scripts/livesource0/地方台/河北.txt')
hunan_dictionary = read_txt_to_array('scripts/livesource0/地方台/湖南.txt')
hubei_dictionary = read_txt_to_array('scripts/livesource0/地方台/湖北.txt')
anhui_dictionary = read_txt_to_array('scripts/livesource0/地方台/安徽.txt')
fujian_dictionary = read_txt_to_array('scripts/livesource0/地方台/福建.txt')
shanxi1_dictionary = read_txt_to_array('scripts/livesource0/地方台/陕西.txt')
liaoning_dictionary = read_txt_to_array('scripts/livesource0/地方台/辽宁.txt')
jiangxi_dictionary = read_txt_to_array('scripts/livesource0/地方台/江西.txt')
heilongjiang_dictionary = read_txt_to_array('scripts/livesource0/地方台/黑龙江.txt')
jilin_dictionary = read_txt_to_array('scripts/livesource0/地方台/吉林.txt')
shanxi2_dictionary = read_txt_to_array('scripts/livesource0/地方台/山西.txt')
guangxi_dictionary = read_txt_to_array('scripts/livesource0/地方台/广西.txt')
yunnan_dictionary = read_txt_to_array('scripts/livesource0/地方台/云南.txt')
guizhou_dictionary = read_txt_to_array('scripts/livesource0/地方台/贵州.txt')
gansu_dictionary = read_txt_to_array('scripts/livesource0/地方台/甘肃.txt')
neimenggu_dictionary = read_txt_to_array('scripts/livesource0/地方台/内蒙.txt')
xinjiang_dictionary = read_txt_to_array('scripts/livesource0/地方台/新疆.txt')
hainan_dictionary = read_txt_to_array('scripts/livesource0/地方台/海南.txt')
ningxia_dictionary = read_txt_to_array('scripts/livesource0/地方台/宁夏.txt')
qinghai_dictionary = read_txt_to_array('scripts/livesource0/地方台/青海.txt')
xizang_dictionary = read_txt_to_array('scripts/livesource0/地方台/西藏.txt')

news_dictionary = read_txt_to_array('scripts/livesource0/主频道/新闻.txt')
shuzi_dictionary = read_txt_to_array('scripts/livesource0/主频道/数字.txt')
dianying_dictionary = read_txt_to_array('scripts/livesource0/主频道/电影.txt')
jieshuo_dictionary = read_txt_to_array('scripts/livesource0/主频道/解说.txt')
zongyi_dictionary = read_txt_to_array('scripts/livesource0/主频道/综艺.txt')
huya_dictionary = read_txt_to_array('scripts/livesource0/主频道/虎牙.txt')
douyu_dictionary = read_txt_to_array('scripts/livesource0/主频道/斗鱼.txt')
xianggang_dictionary = read_txt_to_array('scripts/livesource0/主频道/香港.txt')
aomen_dictionary = read_txt_to_array('scripts/livesource0/主频道/澳门.txt')
china_dictionary = read_txt_to_array('scripts/livesource0/主频道/中国.txt')
guoji_dictionary = read_txt_to_array('scripts/livesource0/主频道/国际.txt')
gangaotai_dictionary = read_txt_to_array('scripts/livesource0/主频道/港澳台.txt')
dianshiju_dictionary = read_txt_to_array('scripts/livesource0/主频道/电视剧.txt')
radio_dictionary = read_txt_to_array('scripts/livesource0/主频道/收音机.txt')
donghuapian_dictionary = read_txt_to_array('scripts/livesource0/主频道/动画片.txt')
jilupian_dictionary = read_txt_to_array('scripts/livesource0/主频道/记录片.txt')
tiyu_dictionary = read_txt_to_array('scripts/livesource0/主频道/体育.txt')
youxi_dictionary = read_txt_to_array('scripts/livesource0/主频道/游戏.txt')
xiqu_dictionary = read_txt_to_array('scripts/livesource0/主频道/戏曲.txt')
yinyue_dictionary = read_txt_to_array('scripts/livesource0/主频道/音乐.txt')
chunwan_dictionary = read_txt_to_array('scripts/livesource0/主频道/春晚.txt')
tyss_dictionary = read_txt_to_array('scripts/livesource0/主频道/体育赛事.txt')
mgss_dictionary = read_txt_to_array('scripts/livesource0/主频道/咪咕赛事.txt')
zhibozhongguo_dictionary = read_txt_to_array('scripts/livesource0/主频道/直播中国.txt')

# 2. 加载名称校正
corrections_name = load_corrections_name('scripts/livesource0/corrections_name.txt')

# 3. 处理URL源
print("开始处理URL源...")
urls = read_txt_to_array('scripts/livesource0/urls-daily.txt')
for url in urls:
    if url.startswith("http"):
        # 处理日期变量
        if "{MMdd}" in url:  # 特别处理113格式
            current_date_str = datetime.now().strftime("%m%d")
            url = url.replace("{MMdd}", current_date_str)
        if "{MMdd-1}" in url:  # 特别处理113格式（前一天）
            yesterday_date_str = (datetime.now() - timedelta(days=1)).strftime("%m%d")
            url = url.replace("{MMdd-1}", yesterday_date_str)
            
        print(f"处理URL: {url}")
        process_url(url)

# 4. 处理白名单
print(f"ADD whitelist_auto.txt")
whitelist_auto_lines = read_txt_to_array('scripts/livesource0/blacklist/whitelist_auto.txt')
for whitelist_line in whitelist_auto_lines:
    if "#genre#" not in whitelist_line and "," in whitelist_line and "://" in whitelist_line:
        whitelist_parts = whitelist_line.split(",")
        try:
            response_time = float(whitelist_parts[0].replace("ms", ""))
        except ValueError:
            print(f"response_time转换失败: {whitelist_line}")
            response_time = 60000  # 单位毫秒，转换失败给个60秒
        if response_time < 2000:  # 2s以内的高响应源
            process_channel_line(",".join(whitelist_parts[1:]))

# ======= 体育赛事数据处理 =======

# 5. 处理体育赛事数据
# 将日期统一格式化为MM-DD格式
normalized_tyss_lines = [normalize_date_to_md(s) for s in tyss_lines]

# 6. 处理AKTV源
aktv_lines = []  # AKTV
aktv_url = "https://aktv.space/live.m3u"  # AKTV

aktv_text = get_http_response(aktv_url)
if aktv_text:
    print("AKTV成功获取内容")
    aktv_text = convert_m3u_to_txt(aktv_text)
    aktv_lines = aktv_text.strip().split('\n')
else:
    print("AKTV请求失败，从本地获取！")
    aktv_lines = read_txt_to_array('scripts/livesource0/手工区/AKTV.txt')

# 7. 过滤和生成体育赛事页面
# 过滤txt中体育赛事
keywords_to_exclude_tiyu_txt = ["玉玉软件", "榴芒电视","公众号","麻豆","「回看」"]
normalized_tyss_lines = filter_lines(normalized_tyss_lines, keywords_to_exclude_tiyu_txt)
normalized_tyss_lines = custom_tyss_sort(set(normalized_tyss_lines))

# 过滤tiyu页面中体育赛事
keywords_to_exclude_tiyu = ["玉玉软件", "榴芒电视","公众号","咪视通","麻豆","「回看」"]
filtered_tyss_lines = filter_lines(normalized_tyss_lines, keywords_to_exclude_tiyu)
generate_playlist_html(filtered_tyss_lines, 'output/sport.html')

# ======= 结束体育赛事数据处理 =======
# 8. 准备今日推荐和版本信息
daily_mtv = "今日推荐," + get_random_url('scripts/livesource0/手工区/今日推荐.txt')

# 获取当前的UTC时间并转换为北京时间
utc_time = datetime.now(timezone.utc)
beijing_time = utc_time + timedelta(hours=8)
formatted_time = beijing_time.strftime("%Y%m%d %H:%M:%S")

daily_mtv = "💯推荐," + get_random_url('scripts/livesource0/手工区/今日推荐.txt')
daily_mtv1 = "🤫低调," + get_random_url('scripts/livesource0/手工区/今日推荐.txt')
daily_mtv2 = "🟢使用," + get_random_url('scripts/livesource0/手工区/今日推荐.txt')
daily_mtv3 = "⚠️禁止," + get_random_url('scripts/livesource0/手工区/今日推荐.txt')
daily_mtv4 = "🚫贩卖," + get_random_url('scripts/livesource0/手工区/今日推荐.txt')

about_video1 = "https://gitee.com/xiaoran67/update/raw/master/scripts/livesource0/about1080p.mp4"
about_video2 = "https://gitlab.com/xiaoran67/update/-/raw/main/scripts/livesource0/about1080p.mp4"

version = formatted_time + "," + get_random_url('scripts/livesource0/手工区/今日推台.txt')
about = "👨潇然," + get_random_url('scripts/livesource0/手工区/今日推台.txt')

# 9. 增加手工区
print(f"处理手工区...")
# 使用您的手工区路径
hubei_lines = hubei_lines + read_txt_to_array('scripts/livesource0/手工区/湖北频道.txt')

# 10. 定义输出内容
# ======= 完整版内容定义 =======
# 完整版内容 📡 包含所有频道分类

all_lines = ["🌐央视频道,#genre#"] + sort_data(["CCTV1", "CCTV2", "CCTV3", "CCTV4", "CCTV5", "CCTV6", "CCTV7", "CCTV8", "CCTV9", "CCTV10", "CCTV11", "CCTV12", "CCTV13", "CCTV14", "CCTV15", "CCTV16", "CCTV17"], set(correct_name_data(corrections_name, yangshi_lines))) + ['\n'] + \
    ["📡卫视频道,#genre#"] + sort_data(weishi_dictionary, set(correct_name_data(corrections_name, weishi_lines))) + ['\n'] + \
    ["🏠北京频道,#genre#"] + sort_data(beijing_dictionary,set(correct_name_data(corrections_name,beijing_lines))) + ['\n'] + \
    ["🏙️上海频道,#genre#"] + sort_data(shanghai_dictionary,set(correct_name_data(corrections_name,shanghai_lines))) + ['\n'] + \
    ["🎡天津频道,#genre#"] + sort_data(tianjin_dictionary,set(correct_name_data(corrections_name,tianjin_lines))) + ['\n'] + \
    ["🏞️重庆频道,#genre#"] + sort_data(chongqing_dictionary,set(correct_name_data(corrections_name,chongqing_lines))) + ['\n'] + \
    ["🐅广东频道,#genre#"] + sort_data(guangdong_dictionary,set(correct_name_data(corrections_name,guangdong_lines))) + ['\n'] + \
    ["🎐江苏频道,#genre#"] + sort_data(jiangsu_dictionary,set(correct_name_data(corrections_name,jiangsu_lines))) + ['\n'] + \
    ["🌊浙江频道,#genre#"] + sort_data(zhejiang_dictionary,set(correct_name_data(corrections_name,zhejiang_lines))) + ['\n'] + \
    ["⛰️山东频道,#genre#"] + sort_data(shandong_dictionary,set(correct_name_data(corrections_name,shandong_lines))) + ['\n'] + \
    ["🌾河南频道,#genre#"] + sort_data(henan_dictionary,set(correct_name_data(corrections_name,henan_lines))) + ['\n'] + \
    ["🐼四川频道,#genre#"] + sort_data(sichuan_dictionary,set(correct_name_data(corrections_name,sichuan_lines))) + ['\n'] + \
    ["🌉河北频道,#genre#"] + sort_data(hebei_dictionary,set(correct_name_data(corrections_name,hebei_lines))) + ['\n'] + \
    ["🌶️湖南频道,#genre#"] + sort_data(hunan_dictionary,set(correct_name_data(corrections_name,hunan_lines))) + ['\n'] + \
    ["🏯湖北频道,#genre#"] + sort_data(hubei_dictionary,set(correct_name_data(corrections_name,hubei_lines))) + ['\n'] + \
    ["🎨安徽频道,#genre#"] + sort_data(anhui_dictionary,set(correct_name_data(corrections_name,anhui_lines))) + ['\n'] + \
    ["🍵福建频道,#genre#"] + sort_data(fujian_dictionary,set(correct_name_data(corrections_name,fujian_lines))) + ['\n'] + \
    ["🗿陕西频道,#genre#"] + sort_data(shanxi1_dictionary,set(correct_name_data(corrections_name,shanxi1_lines))) + ['\n'] + \
    ["🐯辽宁频道,#genre#"] + sort_data(liaoning_dictionary, set(correct_name_data(corrections_name, liaoning_lines))) + ['\n'] + \
    ["⛩️江西频道,#genre#"] + sort_data(jiangxi_dictionary, set(correct_name_data(corrections_name, jiangxi_lines))) + ['\n'] + \
    ["❄️黑龙江台,#genre#"] + sort_data(heilongjiang_dictionary,set(correct_name_data(corrections_name,heilongjiang_lines))) + ['\n'] + \
    ["🎎吉林频道,#genre#"] + sort_data(jilin_dictionary,set(correct_name_data(corrections_name,jilin_lines))) + ['\n'] + \
    ["🏮山西频道,#genre#"] + sort_data(shanxi2_dictionary,set(correct_name_data(corrections_name,shanxi2_lines))) + ['\n'] + \
    ["🐘广西频道,#genre#"] + sort_data(guangxi_dictionary,set(correct_name_data(corrections_name,guangxi_lines))) + ['\n'] + \
    ["☁️云南频道,#genre#"] + sort_data(yunnan_dictionary,set(correct_name_data(corrections_name,yunnan_lines))) + ['\n'] + \
    ["🍶贵州频道,#genre#"] + sort_data(guizhou_dictionary,set(correct_name_data(corrections_name,guizhou_lines))) + ['\n'] + \
    ["🐫甘肃频道,#genre#"] + sort_data(gansu_dictionary,set(correct_name_data(corrections_name,gansu_lines))) + ['\n'] + \
    ["🐎内蒙古台,#genre#"] + sort_data(neimenggu_dictionary,set(correct_name_data(corrections_name,neimenggu_lines))) + ['\n'] + \
    ["🍇新疆频道,#genre#"] + sort_data(xinjiang_dictionary,set(correct_name_data(corrections_name,xinjiang_lines))) + ['\n'] + \
    ["🌴海南频道,#genre#"] + sort_data(hainan_dictionary,set(correct_name_data(corrections_name,hainan_lines))) + ['\n'] + \
    ["🏜️宁夏频道,#genre#"] + sort_data(ningxia_dictionary,set(correct_name_data(corrections_name,ningxia_lines))) + ['\n'] + \
    ["🏔️青海频道,#genre#"] + sort_data(qinghai_dictionary,set(correct_name_data(corrections_name,qinghai_lines))) + ['\n'] + \
    ["⛰️西藏频道,#genre#"] + sort_data(xizang_dictionary,set(correct_name_data(corrections_name,xizang_lines))) + ['\n'] + \
    ["📰新闻频道,#genre#"] + sort_data(news_dictionary,set(correct_name_data(corrections_name,news_lines))) + ['\n'] + \
    ["🔢数字频道,#genre#"] + sort_data(shuzi_dictionary,set(correct_name_data(corrections_name,shuzi_lines))) + ['\n'] + \
    ["🎬电影频道,#genre#"] + sort_data(dianying_dictionary,set(correct_name_data(corrections_name,dianying_lines))) + ['\n'] + \
    ["🎙️解说频道,#genre#"] + sort_data(jieshuo_dictionary,set(correct_name_data(corrections_name,jieshuo_lines))) + ['\n'] + \
    ["🎭综艺频道,#genre#"] + sort_data(zongyi_dictionary,set(correct_name_data(corrections_name,zongyi_lines))) + ['\n'] + \
    ["🐯虎牙直播,#genre#"] + sort_data(huya_dictionary,set(correct_name_data(corrections_name,huya_lines))) + ['\n'] + \
    ["🐬斗鱼直播,#genre#"] + sort_data(douyu_dictionary,set(correct_name_data(corrections_name,douyu_lines))) + ['\n'] + \
    ["🇭🇰香港频道,#genre#"] + sort_data(xianggang_dictionary,set(correct_name_data(corrections_name,xianggang_lines))) + ['\n'] + \
    ["🇲🇴澳门频道,#genre#"] + sort_data(aomen_dictionary,set(correct_name_data(corrections_name,aomen_lines))) + ['\n'] + \
    ["🇨🇳中国频道,#genre#"] + sort_data(china_dictionary,set(correct_name_data(corrections_name,china_lines))) + ['\n'] + \
    ["🌍国际频道,#genre#"] + sort_data(guoji_dictionary,set(correct_name_data(corrections_name,guoji_lines))) + ['\n'] + \
    ["🇨🇳港·澳·台,#genre#"] + sort_data(gangaotai_dictionary,set(correct_name_data(corrections_name,gangaotai_lines))) + ['\n'] + \
    ["📺电·视·剧,#genre#"] + sort_data(dianshiju_dictionary,set(correct_name_data(corrections_name,dianshiju_lines))) + ['\n'] + \
    ["📻收·音·机,#genre#"] + sort_data(radio_dictionary,set(correct_name_data(corrections_name,radio_lines))) + ['\n'] + \
    ["🐶动·画·片,#genre#"] + sort_data(donghuapian_dictionary,set(correct_name_data(corrections_name,donghuapian_lines))) + ['\n'] + \
    ["🎞️纪·录·片,#genre#"] + sort_data(jilupian_dictionary,set(correct_name_data(corrections_name,jilupian_lines))) + ['\n'] + \
    ["🎮游戏频道,#genre#"] + sort_data(youxi_dictionary,set(correct_name_data(corrections_name,youxi_lines))) + ['\n'] + \
    ["🎭戏曲频道,#genre#"] + sort_data(xiqu_dictionary,set(correct_name_data(corrections_name,xiqu_lines))) + ['\n'] + \
    ["🎵音乐频道,#genre#"] + sort_data(yinyue_dictionary,set(correct_name_data(corrections_name,yinyue_lines))) + ['\n'] + \
    ["🎉春晚频道,#genre#"] + sort_data(chunwan_dictionary,set(correct_name_data(corrections_name,chunwan_lines))) + ['\n'] + \
    ["🏆体育赛事,#genre#"] + normalized_tyss_lines + ['\n'] + \
    ["⚽体育频道,#genre#"] + sort_data(tiyu_dictionary,set(correct_name_data(corrections_name,tiyu_lines))) + ['\n'] + \
    ["🏀咪咕赛事,#genre#"] + mgss_lines + ['\n'] + \
    ["📹直播中国,#genre#"] + sort_data(zhibozhongguo_dictionary,set(correct_name_data(corrections_name,zhibozhongguo_lines))) + ['\n'] + \
    ["❓其他频道,#genre#"] + sorted(set(correct_name_data(corrections_name,other_lines))) + ['\n'] + \
    ["🕒更新时间,#genre#"] + [version] + [about] + [daily_mtv] + [daily_mtv1] + [daily_mtv2] + [daily_mtv3] + [daily_mtv4] + read_txt_to_array('scripts/livesource0/手工区/about.txt') + ['\n']

# ======= 精简版内容定义 =======
# 精简版内容 🛰️ 包含核心频道分类
all_lines_simple = ["🌐央  视,#genre#"] + sort_data(["CCTV1", "CCTV2", "CCTV3", "CCTV4", "CCTV5", "CCTV6", "CCTV7", "CCTV8", "CCTV9", "CCTV10", "CCTV11", "CCTV12", "CCTV13", "CCTV14", "CCTV15", "CCTV16", "CCTV17"], set(correct_name_data(corrections_name, yangshi_lines))) + ['\n'] + \
    ["📡卫  视,#genre#"] + sort_data(weishi_dictionary, set(correct_name_data(corrections_name, weishi_lines))) + ['\n'] + \
    ["🏠地方台,#genre#"] + \
    sort_data(beijing_dictionary,set(correct_name_data(corrections_name,beijing_lines))) + \
    sort_data(shanghai_dictionary,set(correct_name_data(corrections_name,shanghai_lines))) + \
    sort_data(tianjin_dictionary,set(correct_name_data(corrections_name,tianjin_lines))) + \
    sort_data(chongqing_dictionary,set(correct_name_data(corrections_name,chongqing_lines))) + \
    sort_data(guangdong_dictionary,set(correct_name_data(corrections_name,guangdong_lines))) + \
    sort_data(jiangsu_dictionary,set(correct_name_data(corrections_name,jiangsu_lines))) + \
    sort_data(zhejiang_dictionary,set(correct_name_data(corrections_name,zhejiang_lines))) + \
    sort_data(shandong_dictionary,set(correct_name_data(corrections_name,shandong_lines))) + \
    sort_data(henan_dictionary,set(correct_name_data(corrections_name,henan_lines))) + \
    sort_data(sichuan_dictionary,set(correct_name_data(corrections_name,sichuan_lines))) + \
    sort_data(hebei_dictionary,set(correct_name_data(corrections_name,hebei_lines))) + \
    sort_data(hunan_dictionary,set(correct_name_data(corrections_name,hunan_lines))) + \
    sort_data(hubei_dictionary,set(correct_name_data(corrections_name,hubei_lines))) + \
    sort_data(anhui_dictionary,set(correct_name_data(corrections_name,anhui_lines))) + \
    sort_data(fujian_dictionary,set(correct_name_data(corrections_name,fujian_lines))) + \
    sort_data(shanxi1_dictionary,set(correct_name_data(corrections_name,shanxi1_lines))) + \
    sort_data(liaoning_dictionary,set(correct_name_data(corrections_name,liaoning_lines))) + \
    sort_data(jiangxi_dictionary,set(correct_name_data(corrections_name,jiangxi_lines))) + \
    sort_data(heilongjiang_dictionary,set(correct_name_data(corrections_name,heilongjiang_lines))) + \
    sort_data(jilin_dictionary,set(correct_name_data(corrections_name,jilin_lines))) + \
    sort_data(shanxi2_dictionary,set(correct_name_data(corrections_name,shanxi2_lines))) + \
    sort_data(guangxi_dictionary,set(correct_name_data(corrections_name,guangxi_lines))) + \
    sort_data(yunnan_dictionary,set(correct_name_data(corrections_name,yunnan_lines))) + \
    sort_data(guizhou_dictionary,set(correct_name_data(corrections_name,guizhou_lines))) + \
    sort_data(gansu_dictionary,set(correct_name_data(corrections_name,gansu_lines))) + \
    sort_data(neimenggu_dictionary,set(correct_name_data(corrections_name,neimenggu_lines))) + \
    sort_data(xinjiang_dictionary,set(correct_name_data(corrections_name,xinjiang_lines))) + \
    sort_data(hainan_dictionary,set(correct_name_data(corrections_name,hainan_lines))) + \
    sort_data(ningxia_dictionary,set(correct_name_data(corrections_name,ningxia_lines))) + \
    sort_data(qinghai_dictionary,set(correct_name_data(corrections_name,qinghai_lines))) + \
    sort_data(xizang_dictionary,set(correct_name_data(corrections_name,xizang_lines))) + ['\n'] + \
    ["🕒更新时间,#genre#"] + [version] + [about] + [daily_mtv] + [daily_mtv1] + [daily_mtv2] + [daily_mtv3] + [daily_mtv4] + read_txt_to_array('scripts/livesource0/手工区/about.txt') + ['\n']
            
# ======= 定制版内容定义 =======
# 定制版内容 🌐📡🛰️📺🏙️🏠🧧🏮 包含定制频道分类

all_lines_custom = ["🌐央视频道,#genre#"] + sort_data(["CCTV1", "CCTV2", "CCTV3", "CCTV4", "CCTV5", "CCTV6", "CCTV7", "CCTV8", "CCTV9", "CCTV10", "CCTV11", "CCTV12", "CCTV13", "CCTV14", "CCTV15", "CCTV16", "CCTV17"], set(correct_name_data(corrections_name, yangshi_lines))) + ['\n'] + \
    ["📡卫视频道,#genre#"] + sort_data(weishi_dictionary, set(correct_name_data(corrections_name, weishi_lines))) + ['\n'] + \
    ["🏠地·方·台,#genre#"] + \
    sort_data(beijing_dictionary,set(correct_name_data(corrections_name,beijing_lines))) + \
    sort_data(shanghai_dictionary,set(correct_name_data(corrections_name,shanghai_lines))) + \
    sort_data(tianjin_dictionary,set(correct_name_data(corrections_name,tianjin_lines))) + \
    sort_data(chongqing_dictionary,set(correct_name_data(corrections_name,chongqing_lines))) + \
    sort_data(guangdong_dictionary,set(correct_name_data(corrections_name,guangdong_lines))) + \
    sort_data(jiangsu_dictionary,set(correct_name_data(corrections_name,jiangsu_lines))) + \
    sort_data(zhejiang_dictionary,set(correct_name_data(corrections_name,zhejiang_lines))) + \
    sort_data(shandong_dictionary,set(correct_name_data(corrections_name,shandong_lines))) + \
    sort_data(henan_dictionary,set(correct_name_data(corrections_name,henan_lines))) + \
    sort_data(sichuan_dictionary,set(correct_name_data(corrections_name,sichuan_lines))) + \
    sort_data(hebei_dictionary,set(correct_name_data(corrections_name,hebei_lines))) + \
    sort_data(hunan_dictionary,set(correct_name_data(corrections_name,hunan_lines))) + \
    sort_data(hubei_dictionary,set(correct_name_data(corrections_name,hubei_lines))) + \
    sort_data(anhui_dictionary,set(correct_name_data(corrections_name,anhui_lines))) + \
    sort_data(fujian_dictionary,set(correct_name_data(corrections_name,fujian_lines))) + \
    sort_data(shanxi1_dictionary,set(correct_name_data(corrections_name,shanxi1_lines))) + \
    sort_data(liaoning_dictionary,set(correct_name_data(corrections_name,liaoning_lines))) + \
    sort_data(jiangxi_dictionary,set(correct_name_data(corrections_name,jiangxi_lines))) + \
    sort_data(heilongjiang_dictionary,set(correct_name_data(corrections_name,heilongjiang_lines))) + \
    sort_data(jilin_dictionary,set(correct_name_data(corrections_name,jilin_lines))) + \
    sort_data(shanxi2_dictionary,set(correct_name_data(corrections_name,shanxi2_lines))) + \
    sort_data(guangxi_dictionary,set(correct_name_data(corrections_name,guangxi_lines))) + \
    sort_data(yunnan_dictionary,set(correct_name_data(corrections_name,yunnan_lines))) + \
    sort_data(guizhou_dictionary,set(correct_name_data(corrections_name,guizhou_lines))) + \
    sort_data(gansu_dictionary,set(correct_name_data(corrections_name,gansu_lines))) + \
    sort_data(neimenggu_dictionary,set(correct_name_data(corrections_name,neimenggu_lines))) + \
    sort_data(xinjiang_dictionary,set(correct_name_data(corrections_name,xinjiang_lines))) + \
    sort_data(hainan_dictionary,set(correct_name_data(corrections_name,hainan_lines))) + \
    sort_data(ningxia_dictionary,set(correct_name_data(corrections_name,ningxia_lines))) + \
    sort_data(qinghai_dictionary,set(correct_name_data(corrections_name,qinghai_lines))) + \
    sort_data(xizang_dictionary,set(correct_name_data(corrections_name,xizang_lines))) + ['\n'] + \
    ["📰新闻频道,#genre#"] + sort_data(news_dictionary,set(correct_name_data(corrections_name,news_lines))) + ['\n'] + \
    ["🔢数字频道,#genre#"] + sort_data(shuzi_dictionary,set(correct_name_data(corrections_name,shuzi_lines))) + ['\n'] + \
    ["🎬电影频道,#genre#"] + sort_data(dianying_dictionary,set(correct_name_data(corrections_name,dianying_lines))) + ['\n'] + \
    ["🎙️解说频道,#genre#"] + sort_data(jieshuo_dictionary,set(correct_name_data(corrections_name,jieshuo_lines))) + ['\n'] + \
    ["🎭综艺频道,#genre#"] + sort_data(zongyi_dictionary,set(correct_name_data(corrections_name,zongyi_lines))) + ['\n'] + \
    ["🐯虎牙直播,#genre#"] + sort_data(huya_dictionary,set(correct_name_data(corrections_name,huya_lines))) + ['\n'] + \
    ["🐬斗鱼直播,#genre#"] + sort_data(douyu_dictionary,set(correct_name_data(corrections_name,douyu_lines))) + ['\n'] + \
    ["🇭🇰香港频道,#genre#"] + sort_data(xianggang_dictionary,set(correct_name_data(corrections_name,xianggang_lines))) + ['\n'] + \
    ["🇲🇴澳门频道,#genre#"] + sort_data(aomen_dictionary,set(correct_name_data(corrections_name,aomen_lines))) + ['\n'] + \
    ["🇨🇳中国频道,#genre#"] + sort_data(china_dictionary,set(correct_name_data(corrections_name,china_lines))) + ['\n'] + \
    ["🌍国际频道,#genre#"] + sort_data(guoji_dictionary,set(correct_name_data(corrections_name,guoji_lines))) + ['\n'] + \
    ["🇨🇳港·澳·台,#genre#"] + sort_data(gangaotai_dictionary,set(correct_name_data(corrections_name,gangaotai_lines))) + ['\n'] + \
    ["📺电·视·剧,#genre#"] + sort_data(dianshiju_dictionary,set(correct_name_data(corrections_name,dianshiju_lines))) + ['\n'] + \
    ["📻收·音·机,#genre#"] + sort_data(radio_dictionary,set(correct_name_data(corrections_name,radio_lines))) + ['\n'] + \
    ["🐶动·画·片,#genre#"] + sort_data(donghuapian_dictionary,set(correct_name_data(corrections_name,donghuapian_lines))) + ['\n'] + \
    ["🎞️纪·录·片,#genre#"] + sort_data(jilupian_dictionary,set(correct_name_data(corrections_name,jilupian_lines))) + ['\n'] + \
    ["🎮游戏频道,#genre#"] + sort_data(youxi_dictionary,set(correct_name_data(corrections_name,youxi_lines))) + ['\n'] + \
    ["🎭戏曲频道,#genre#"] + sort_data(xiqu_dictionary,set(correct_name_data(corrections_name,xiqu_lines))) + ['\n'] + \
    ["🎵音乐频道,#genre#"] + sort_data(yinyue_dictionary,set(correct_name_data(corrections_name,yinyue_lines))) + ['\n'] + \
    ["🎉春晚频道,#genre#"] + sort_data(chunwan_dictionary,set(correct_name_data(corrections_name,chunwan_lines))) + ['\n'] + \
    ["🏆体育赛事,#genre#"] + normalized_tyss_lines + ['\n'] + \
    ["⚽体育频道,#genre#"] + sort_data(tiyu_dictionary,set(correct_name_data(corrections_name,tiyu_lines))) + ['\n'] + \
    ["🏀咪咕赛事,#genre#"] + mgss_lines + ['\n'] + \
    ["📹直播中国,#genre#"] + sort_data(zhibozhongguo_dictionary,set(correct_name_data(corrections_name,zhibozhongguo_lines))) + ['\n'] + \
    ["❓其他频道,#genre#"] + sorted(set(correct_name_data(corrections_name,other_lines))) + ['\n'] + \
    ["🕒更新时间,#genre#"] + [version] + [about] + [daily_mtv] + [daily_mtv1] + [daily_mtv2] + [daily_mtv3] + [daily_mtv4] + read_txt_to_array('scripts/livesource0/手工区/about.txt') + ['\n']

# 手工专区类型：读取预设的静态优质源文件，手工维护
# 格式：read_txt_to_array('手工区/文件名.txt')

# 动态赛事类型：自动获取并处理的实时赛事数据  
# 格式：normalized_tyss_lines（体育赛事） / mgss_lines（咪咕赛事）

# 自动分类类型：脚本自动分类得到的地方频道数据
# 格式1：sort_data(排序字典, set(correct_name_data(校正字典, 数据))) - 按指定顺序排序
# 格式2：sorted(set(correct_name_data(校正字典, 数据))) - 按字母顺序排序

# 处理流程说明：
# - read_txt_to_array(): 从文件读取静态频道列表
# - 变量名: 使用动态处理的频道数据
# - sort_data(): 按自定义字典顺序排序
# - sorted(): 按字母顺序排序  
# - set(): 数据去重
# - correct_name_data(): 频道名称标准化校正

# 示例说明
# 手工专区
# ["香港台,#genre#"] + read_txt_to_array('专区/♪香港台.txt') + ['\n'] + \

# 动态赛事  
# ["体育赛事,#genre#"] + normalized_tyss_lines + ['\n'] + \

# 自动分类（字典排序）
# ["山东,#genre#"] + sort_data(shandong_dictionary,set(correct_name_data(corrections_name,shandong_lines))) + ['\n'] + \

# 自动分类（字母排序）
# ["☘️江苏,#genre#"] + sorted(set(correct_name_data(corrections_name,jsu_lines))) + ['\n'] + \

# 11. 保存输出文件
output_full = "output/full.txt"
output_lite = "output/lite.txt" 
output_custom = "output/custom.txt"
others_file = "output/others.txt"

try:
    # 保存完整版
    with open(output_full, 'w', encoding='utf-8') as f:
        for line in all_lines:
            f.write(line + '\n')
    print(f"完整版已保存到文件: {output_full}")

    # 保存精简版
    with open(output_lite, 'w', encoding='utf-8') as f:
        for line in all_lines_simple:
            f.write(line + '\n')
    print(f"精简版已保存到文件: {output_lite}")

    # 保存定制版
    with open(output_custom, 'w', encoding='utf-8') as f:
        for line in all_lines_custom:
            f.write(line + '\n')
    print(f"定制版已保存到文件: {output_custom}")

    # 保存其他频道
    with open(others_file, 'w', encoding='utf-8') as f:
        for line in other_lines:
            f.write(line + '\n')
    print(f"其他频道已保存到文件: {others_file}")

except Exception as e:
    print(f"保存文件时发生错误：{e}")

# 12. 生成M3U文件
channels_logos = read_txt_to_array('scripts/livesource0/logo.txt')  # 读入logo库
make_m3u(output_full, output_full.replace(".txt", ".m3u"))
make_m3u(output_lite, output_lite.replace(".txt", ".m3u"))
make_m3u(output_custom, output_custom.replace(".txt", ".m3u"))

# ======= 执行统计和日志 =======

# 执行结束时间
timeend = datetime.now()

# 计算时间差
elapsed_time = timeend - timestart
total_seconds = elapsed_time.total_seconds()

# 转换为分钟和秒
minutes = int(total_seconds // 60)
seconds = int(total_seconds % 60)

# 格式化开始和结束时间
timestart_str = timestart.strftime("%Y%m%d_%H_%M_%S")
timeend_str = timeend.strftime("%Y%m%d_%H_%M_%S")

print(f"开始时间: {timestart_str}")
print(f"结束时间: {timeend_str}")
print(f"执行时间: {minutes} 分 {seconds} 秒")

# 统计信息
combined_blacklist_hj = len(combined_blacklist)
all_lines_hj = len(all_lines)
other_lines_hj = len(other_lines)
print(f"黑名单行数: {combined_blacklist_hj} ")
print(f"完整源行数: {all_lines_hj} ")
print(f"其它源行数: {other_lines_hj} ")

print("\n=== 输出文件统计 ===")
output_files = [
    'output/full.txt', 'output/lite.txt', 'output/custom.txt', 
    'output/others.txt', 'output/full.m3u', 'output/lite.m3u', 
    'output/custom.m3u', 'output/sport.html'  # ✅ sport.html在当前目录
]
for file_path in output_files:
    if os.path.exists(file_path):
        file_size = os.path.getsize(file_path)
        print(f"✅ {file_path} - {file_size} 字节")
    else:
        print(f"❌ {file_path} - 文件未找到")
